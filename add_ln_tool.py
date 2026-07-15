#!/usr/bin/env python3
"""
轻小说加书工具 v1.0
用法: python3 add_ln_tool.py <ANILIST_ID> [ANILIST_ID ...]
     python3 add_ln_tool.py --batch ids.txt

与追番工具的区别:
  - 类型: MANGA (AniList)
  - 分组: publisher (出版社) 替代 studio (制作社)
  - 显示: author (作者) 替代 studio on cards
  - 集数 → 卷数 (volumes)
"""

import sys, os, re, json, time, subprocess, shutil

PROXY = 'http://127.0.0.1:7897'
ANILIST_API = 'https://graphql.anilist.co'
OUT = r'C:\Users\HP\Desktop\娱乐的东西\我的个人网站\lightnovel\index.html'
REPO = r'C:\Users\HP\Desktop\娱乐的东西\我的个人网站'
CV_BASE = 'https://s4.anilist.co/file/anilistcdn/media/manga/cover/medium/'

def shell(cmd, timeout=30):
    env = os.environ.copy()
    env['HTTP_PROXY'] = PROXY; env['HTTPS_PROXY'] = PROXY
    try:
        r = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=timeout, env=env, cwd=REPO)
        return r.stdout.strip(), r.returncode
    except subprocess.TimeoutExpired:
        return "TIMEOUT", 1

def fetch_anilist(mid):
    q = 'query{Media(idMal:%d,type:MANGA){title{romaji native}format startDate{year}volumes averageScore staff{nodes{name{full}primaryOccupations}} genres coverImage{large} description}}' % mid
    cmd = f"""curl -s --max-time 10 -X POST {ANILIST_API} -H "Content-Type: application/json" -d '{{"query":"{q}"}}'"""
    out, code = shell(cmd)
    if code != 0: return None
    try:
        return json.loads(out)['data']['Media']
    except: return None

def extract_meta(data):
    staff = data.get('staff', {}).get('nodes', [])
    authors = [s['name']['full'] for s in staff
               if any(t in str(s.get('primaryOccupations', []))
                      for t in ['Author', 'Writer', 'Story', 'Original Creator'])]
    author = authors[0] if authors else 'Unknown'

    return {
        'title_romaji': data['title']['romaji'] or data['title']['native'],
        'title_native': data['title'].get('native') or data['title']['romaji'],
        'year': data.get('startDate', {}).get('year', 0) or 0,
        'volumes': data.get('volumes', 0) or 0,
        'score': round((data.get('averageScore', 0) or 0) / 10, 1),
        'genres': data.get('genres', [])[:4],
        'cover_url': data['coverImage']['large'],
        'author': author,
    }

def verify_url(url):
    out, code = shell(f"curl -sL -o /dev/null -w '%{{http_code}}' --max-time 5 '{url}'")
    return '200' in out

def validate_file():
    with open(OUT, 'r', encoding='utf-8') as f:
        html = f.read()
    results = {}
    cn_count = html.count("cn:'") + len(re.findall(r'cn:"[^"]+"', html))
    cv_urls = re.findall(r"cv:'([^']+\.(?:jpg|png|jpeg|webp)[^']*)'", html)
    cv_unique = set(u.split('/')[-1] for u in cv_urls)
    results['1:1'] = (cn_count == len(cv_unique), f"{cn_count} names vs {len(cv_unique)} covers")

    fails = []
    for u in set(cv_urls):
        out, code = shell(f"curl -sL -o /dev/null -w '%{{http_code}}' --max-time 5 '{u}'")
        if '200' not in out:
            fails.append(u.split('/')[-1][:40])
    results['http'] = (len(fails) == 0, f"{len(fails)}/{len(set(cv_urls))} failed" if fails else "all pass")

    issues = []
    for i, line in enumerate(html.split('\n'), 1):
        for field in ['cn', 'en', 'sp', 'author']:
            for m in re.finditer(rf"{field}:'([^']*)'", line):
                if "'" in m.group(1):
                    issues.append(f"line {i}: {field} has unescaped quote")
    results['syntax'] = (len(issues) == 0, "; ".join(issues) if issues else "pass")

    db_starts = html.count('const DB = [')
    studio_orders = html.count('const pubOrder')
    results['structure'] = (db_starts == 1 and studio_orders == 1, f"DB={db_starts}, pubOrder={studio_orders}")

    all_pass = all(v[0] for v in results.values())
    return all_pass, results

if __name__ == '__main__':
    print("轻小说加书工具 v1.0")
    print("用法: python3 add_ln_tool.py ANILIST_ID [ANILIST_ID ...]")
    print("轻小说比追番多了: 作者字段 / 出版社分组 / 卷数替换集数")
