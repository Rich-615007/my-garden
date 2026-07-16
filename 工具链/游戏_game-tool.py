#!/usr/bin/env python3
"""
游戏加录工具 v1.0 - 按制作公司分类
用法: python3 游戏_game-tool.py --check
      python3 游戏_game-tool.py (交互式添加)
"""
import sys, os, re, json, subprocess

REPO = r'C:\Users\HP\Desktop\娱乐的东西\我的个人网站'
OUT = os.path.join(REPO, 'game', 'index.html')

def shell(cmd, timeout=30):
    env = os.environ.copy()
    env['HTTP_PROXY'] = 'http://127.0.0.1:7897'; env['HTTPS_PROXY'] = 'http://127.0.0.1:7897'
    try:
        r = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=timeout, cwd=REPO)
        return r.stdout.strip(), r.returncode
    except: return "TIMEOUT", 1

def verify_url(url):
    out, _ = shell(f"curl -sL -o /dev/null -w '%{{http_code}}' --max-time 5 '{url}'")
    return '200' in out

def validate_file():
    with open(OUT, 'r', encoding='utf-8') as f: html = f.read()
    results = {}
    cn_count = html.count("cn:'") + len(re.findall(r'cn:"[^"]+"', html))
    cv_urls = re.findall(r"cv:'([^']+\.(?:jpg|png|jpeg|webp))'", html)
    cv_unique = set(v.split('/')[-1] for v in cv_urls)
    results['v1'] = (cn_count == len(cv_unique), f"{cn_count} cn vs {len(cv_unique)} covers")
    fails = []
    for u in set(cv_urls):
        out, _ = shell(f"curl -sL -o /dev/null -w '%{{http_code}}' --max-time 5 '{u}'")
        if '200' not in out: fails.append(u[-40:])
    results['v2_http'] = (len(fails) == 0, f"{len(fails)} fails" if fails else "all pass")
    issues = []
    for i, line in enumerate(html.split('\n'), 1):
        for field in ['cn','sp','developer','platform']:
            for m in re.finditer(rf"{field}:'([^']*)'", line):
                if "'" in m.group(1): issues.append(f"line {i}: {field} unescaped")
    results['v3'] = (len(issues) == 0, "; ".join(issues) if issues else "pass")
    db = html.count('const DB = [')
    dev_order = html.count('const devOrder')
    braces = html.count('{') == html.count('}')
    results['v4'] = (db==1 and dev_order==1 and braces, f"DB={db} devOrder={dev_order} {'OK' if braces else 'FAIL'}")
    blocking = {k:v for k,v in results.items() if k != 'v2_http'}
    all_pass = all(v[0] for v in blocking.values())
    return all_pass, results

if __name__ == '__main__':
    if '--check' in sys.argv:
        passed, results = validate_file()
        for k,(ok,detail) in results.items():
            print(f"[{'PASS' if ok else ('WARN' if k=='v2_http' else 'FAIL')}] {k}: {detail}")
        sys.exit(0 if passed else 1)
    else:
        print(__doc__)
