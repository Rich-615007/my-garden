#!/usr/bin/env python3
"""
轻小说加书工具 v1.1 - 完整工作链
用法: python3 add_ln_tool.py --batch ids.txt
     交互式: python3 add_ln_tool.py ANILIST_ID [ANILIST_ID ...]

与追番工具的区别:
  - 类型: MANGA (AniList)
  - 分组依据: publisher (出版社) 代替 studio (制作社)
  - 显示字段: author (作者) 代替 studio
  - 卷数 (volumes) 代替 集数 (episodes)
"""

import sys, os, re, json, time, subprocess, shutil

PROXY = 'http://127.0.0.1:7897'
ANILIST_API = 'https://graphql.anilist.co'
OUT = r'C:\Users\HP\Desktop\娱乐的东西\我的个人网站\lightnovel\index.html'
REPO = r'C:\Users\HP\Desktop\娱乐的东西\我的个人网站'
# 轻小说用 manga/ 路径
CV_BASE = 'https://s4.anilist.co/file/anilistcdn/media/manga/cover/medium/'

# ── 工具函数 (与追番工具共享模式) ──

def shell(cmd, timeout=30):
    env = os.environ.copy()
    env['HTTP_PROXY'] = PROXY; env['HTTPS_PROXY'] = PROXY
    try:
        r = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=timeout, env=env, cwd=REPO)
        return r.stdout.strip(), r.returncode
    except subprocess.TimeoutExpired:
        return "TIMEOUT", 1

def escape_js_string(s):
    return s.replace("\\", "\\\\").replace("'", "\\'")

def verify_url(url):
    out, code = shell(f"curl -sL -o /dev/null -w '%{{http_code}}' --max-time 5 '{url}'")
    return '200' in out

# ── AniList获取 (MANGA type) ──

def fetch_anilist(mid):
    q = ('query{Media(idMal:%d,type:MANGA){title{romaji native}format startDate{year}volumes '
         'averageScore staff{nodes{name{full}primaryOccupations}} genres coverImage{large} description}}') % mid
    cmd = f"""curl -s --max-time 10 -X POST {ANILIST_API} -H "Content-Type: application/json" -d '{{"query":"{q}"}}'"""
    out, code = shell(cmd)
    if code != 0: return None
    try:
        return json.loads(out)['data']['Media']
    except: return None

def extract_meta(data):
    """从AniList MANGA数据提取元信息"""
    staff = data.get('staff', {}).get('nodes', [])
    authors = []
    for s in staff:
        occs = str(s.get('primaryOccupations', []))
        if any(t in occs for t in ['Author', 'Writer', 'Story', 'Original Creator']):
            authors.append(s['name']['full'])
    author = authors[0] if authors else 'Unknown'

    # AniList不直接返回出版社，需要用户输入
    return {
        'title_romaji': data['title']['romaji'] or (data['title'].get('native') or ''),
        'title_native': data['title'].get('native') or data['title']['romaji'],
        'year': data.get('startDate', {}).get('year', 0) or 0,
        'volumes': data.get('volumes', 0) or 0,
        'score': round((data.get('averageScore', 0) or 0) / 10, 1),
        'genres': data.get('genres', [])[:4],
        'cover_url': data['coverImage']['large'],
        'author': author,
        'synopsis_raw': (data.get('description') or '待补完。')[:200].replace('\n', ' ').replace('<br>', ''),
    }

# ── 验证层 ──

def validate_file():
    with open(OUT, 'r', encoding='utf-8') as f:
        html = f.read()
    results = {}
    # V1: 1:1
    cn_count = html.count("cn:'") + len(re.findall(r'cn:"[^"]+"', html))
    cv_urls = re.findall(r"cv:'([^']+\.(?:jpg|png|jpeg|webp))'", html)
    cv_unique = set(u.split('/')[-1] for u in cv_urls)
    results['v1_1to1'] = (cn_count == len(cv_unique), f"{cn_count} names vs {len(cv_unique)} covers")

    # V2: HTTP (warning only)
    fails = []
    for u in set(cv_urls):
        out, _ = shell(f"curl -sL -o /dev/null -w '%{{http_code}}' --max-time 5 '{u}'")
        if '200' not in out:
            fails.append(u.split('/')[-1][:40])
    v2_ok = len(fails) == 0
    if not v2_ok:
        print(f"    ⚠ V2: {len(fails)} covers HTTP not 200 (may be network)")
    results['v2_http'] = (v2_ok, f"{len(fails)}/{len(set(cv_urls))} failed" if fails else "all pass")

    # V3: Syntax - unescaped quotes
    issues = []
    for i, line in enumerate(html.split('\n'), 1):
        for field in ['cn', 'en', 'sp', 'author']:
            for m in re.finditer(rf"{field}:'([^']*)'", line):
                if "'" in m.group(1):
                    issues.append(f"line {i}: {field} has unescaped quote: {m.group(1)[:40]}")
    results['v3_syntax'] = (len(issues) == 0, "; ".join(issues) if issues else "pass")

    # V4: Structure
    db_starts = html.count('const DB = [')
    studio_orders = html.count('const pubOrder')
    results['v4_structure'] = (db_starts == 1 and studio_orders == 1, f"DB={db_starts}, pubOrder={studio_orders}")

    blocking = {k: v for k, v in results.items() if k != 'v2_http'}
    all_pass = all(v[0] for v in blocking.values())
    return all_pass, results

# ── 插入层 ──

def clean_group_name(raw):
    name = re.sub(r'^\d+\.?\s*', '', raw)
    name = re.sub(r'\s*\(追加\)\s*', '', name)
    return name.strip()

def locate_points(html):
    lines = html.split('\n')
    db_start = None; db_end = None; groups = {}
    for i, line in enumerate(lines):
        if 'const DB = [' in line: db_start = i
        if line.strip() == '];' and db_start and not db_end: db_end = i
        m = re.search(r"/\* ── ([\w\s\d.\(\)\[\]（）追加]+) ── \*/", line)
        if m and db_start != None and db_end != None and db_start < i < db_end:
            name = clean_group_name(m.group(1))
            if name not in groups:
                groups[name] = i
    group_ranges = {}
    sorted_groups = sorted(groups.items(), key=lambda x: x[1])
    for idx, (name, start) in enumerate(sorted_groups):
        end = sorted_groups[idx+1][1] - 1 if idx+1 < len(sorted_groups) else db_end - 1
        group_ranges[name] = (start, end)
    return db_start, db_end, group_ranges

def insert_entries(html, entries_by_pub):
    db_start, db_end, group_ranges = locate_points(html)
    lines = html.split('\n')
    for pub, entries in entries_by_pub.items():
        if pub in group_ranges:
            _, last = group_ranges[pub]
            insert_at = last + 1
            for i in range(last + 1, db_end):
                stripped = lines[i].strip()
                if stripped and not stripped.startswith('/*') and stripped != '];':
                    insert_at = i + 1
                elif stripped.startswith('/*') or stripped == '];':
                    break
            for entry in reversed(entries):
                lines.insert(insert_at, entry)
            offset = len(entries)
            for g in group_ranges:
                if group_ranges[g][0] > insert_at:
                    group_ranges[g] = (group_ranges[g][0] + offset, group_ranges[g][1] + offset)
            db_end += offset
        else:
            # New publisher
            for i, line in enumerate(lines):
                if i > db_start and line.strip() == '];':
                    new_block = ['', f'  /* ── {pub} ── */'] + list(entries)
                    for entry in reversed(new_block):
                        lines.insert(i, entry)
                    break
    return '\n'.join(lines)

def update_pub_order(html, new_pubs):
    pattern = r"(const pubOrder = \[)(.*?)(\];)"
    m = re.search(pattern, html)
    if m:
        current = m.group(2)
        existing = re.findall(r"'([^']+)'", current)
        to_add = [p for p in new_pubs if p not in existing]
        if to_add:
            new_current = current.rstrip().rstrip(',')
            for p in to_add:
                new_current += f",'{p}'"
            html = html[:m.start(2)] + new_current + html[m.end(2):]
    return html

def git_commit_push(message, backup_path=None):
    shell('git add lightnovel/index.html')
    out, code = shell(f"git commit -m '{message}'")
    if code != 0 and 'nothing to commit' not in out:
        if backup_path: shutil.copy(backup_path, OUT)
        return False, out
    out, code = shell('git push')
    if code != 0:
        if backup_path: shutil.copy(backup_path, OUT)
        return False, out
    return True, 'pushed'

# ── 主流程 ──

def add_ln(mal_ids, interactive=True):
    print(f"\n{'='*60}")
    print(f"轻小说加书 v1.1 - 处理 {len(mal_ids)} 部")
    print(f"{'='*60}")

    backup = OUT + '.backup'
    shutil.copy(OUT, backup)
    print(f"\n[1/6] 已备份")

    print(f"\n[2/6] 获取AniList数据...")
    entries = []
    for i, mid in enumerate(mal_ids):
        print(f"  [{i+1}/{len(mal_ids)}] ID:{mid} ", end='', flush=True)
        data = fetch_anilist(mid)
        if not data:
            print('⇒ FAIL')
            continue
        meta = extract_meta(data)
        print(f'⇒ {meta["title_romaji"][:40]} | {meta["year"]} | {meta["volumes"]}vol | sc:{meta["score"]} | {meta["author"]}')

        if interactive:
            cn_name = input("    中文名: ").strip() or meta['title_native']
            publisher = input("    出版社: ").strip()
            synopsis = input(f"    简介(≤100字, 回车用API): ").strip() or meta['synopsis_raw']
        else:
            cn_name = meta['title_native'] or meta['title_romaji']
            publisher = '待分类'
            synopsis = meta['synopsis_raw']

        synopsis = escape_js_string(synopsis[:100])
        cn_name = escape_js_string(cn_name)

        if not verify_url(meta['cover_url']):
            print(f"    ⚠ 封面HTTP异常: {meta['cover_url'][-50:]}")

        entries.append((cn_name, meta, publisher, synopsis))
        time.sleep(1)

    if not entries:
        print("没有成功获取的条目。")
        return False

    print(f"\n[3/6] 按出版社分组...")
    entries_by_pub = {}
    for cn_name, meta, pub, synopsis in entries:
        if pub not in entries_by_pub:
            entries_by_pub[pub] = []
        gs = json.dumps(meta['genres'], ensure_ascii=False)
        en_safe = escape_js_string(meta['title_romaji'])
        author_safe = escape_js_string(meta['author'])
        line = f"  {{cn:'{cn_name}',en:'{en_safe}',y:{meta['year']},v:{meta['volumes']},sc:{meta['score']},pub:'{pub}',author:'{author_safe}',g:{gs},cv:'{meta['cover_url']}',sp:'{synopsis}'}},"
        entries_by_pub[pub].append(line)
        print(f"  {pub}: {cn_name}")

    print(f"\n[4/6] 插入HTML...")
    with open(OUT, 'r', encoding='utf-8') as f:
        html = f.read()
    html = insert_entries(html, entries_by_pub)
    html = update_pub_order(html, list(entries_by_pub.keys()))
    with open(OUT, 'w', encoding='utf-8') as f:
        f.write(html)
    print(f"  已插入 {len(entries)} 条")

    print(f"\n[5/6] 四验...")
    passed, results = validate_file()
    for k, (ok, detail) in results.items():
        status = '✓' if ok else '⚠' if k == 'v2_http' else '✗'
        print(f"  {status} {k}: {detail}")
    if not passed:
        print(f"  验证失败！回退...")
        shutil.copy(backup, OUT)
        return False

    print(f"\n[6/6] 提交推送...")
    names = ','.join([e[0] for e in entries[:3]])
    msg = f"add LN: {names}{'...' if len(entries) > 3 else ''}"
    ok, detail = git_commit_push(msg, backup)
    print(f"  {'✓' if ok else '✗'} {detail}")

    if ok:
        print(f"\n完成！{len(entries)} 部轻小说已添加。")
    return ok

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(0)
    if sys.argv[1] == '--batch':
        with open(sys.argv[2], 'r') as f:
            ids = [int(x) for x in f.read().split() if x.strip().isdigit()]
        add_ln(ids, interactive=False)
    elif sys.argv[1] == '--quiet':
        ids = [int(x) for x in sys.argv[2:]]
        add_ln(ids, interactive=False)
    else:
        ids = [int(x) for x in sys.argv[1:]]
        add_ln(ids, interactive=(len(ids) <= 5))
