#!/usr/bin/env python3
"""
漫画加书工具 v1.0
用法: python3 漫画_manga-tool.py --check    (验证)
     python3 漫画_manga-tool.py --batch ids.txt (批量)
     python3 漫画_manga-tool.py ANILIST_ID [ANILIST_ID ...]

分组依据: 连载杂志（magazine） — 类比动画的制作社、轻小说的出版社
其他字段: 作者(author)/作画(artist)/卷数(volumes)/状态(status)
"""

import sys, os, re, json, time, subprocess, shutil

PROXY = 'http://127.0.0.1:7897'
ANILIST_API = 'https://graphql.anilist.co'
OUT = r'C:\Users\HP\Desktop\娱乐的东西\我的个人网站\manga\index.html'
REPO = r'C:\Users\HP\Desktop\娱乐的东西\我的个人网站'
CV_BASE = 'https://s4.anilist.co/file/anilistcdn/media/manga/cover/medium/'

def shell(cmd, timeout=30):
    env = os.environ.copy()
    env['HTTP_PROXY'] = PROXY; env['HTTPS_PROXY'] = PROXY
    try:
        r = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=timeout, env=env, cwd=REPO)
        return r.stdout.strip(), r.returncode
    except: return "TIMEOUT", 1

def escape_js_string(s):
    return s.replace("\\", "\\\\").replace("'", "\\'")

def verify_url(url):
    out, _ = shell(f"curl -sL -o /dev/null -w '%{{http_code}}' --max-time 5 '{url}'")
    return '200' in out

# ── AniList获取 (MANGA type) ──

def fetch_anilist(mid):
    q = ('query{Media(idMal:%d,type:MANGA){title{romaji native}format startDate{year}volumes '
         'chapters averageScore staff{nodes{name{full}primaryOccupations}} genres coverImage{large} status description}}') % mid
    cmd = f"""curl -s --max-time 10 -X POST {ANILIST_API} -H "Content-Type: application/json" -d '{{"query":"{q}"}}'"""
    out, code = shell(cmd)
    if code != 0: return None
    try:
        return json.loads(out)['data']['Media']
    except: return None

def extract_meta(data):
    staff_list = data.get('staff', {}).get('nodes', [])
    authors = [s['name']['full'] for s in staff_list
               if any(t in str(s.get('primaryOccupations', [])) for t in ['Author','Writer','Story','Original Creator'])]
    artists = [s['name']['full'] for s in staff_list
               if any(t in str(s.get('primaryOccupations', [])) for t in ['Artist','Illustrator'])]
    author = authors[0] if authors else 'Unknown'
    artist = artists[0] if artists else author  # 作画默认同作者

    fmt = data.get('format', '')
    fmt_map = {'MANGA': '漫画', 'NOVEL': '小说', 'ONE_SHOT': '短篇'}
    format_cn = fmt_map.get(fmt, fmt)

    status_map = {'FINISHED': '已完结', 'RELEASING': '连载中', 'NOT_YET_RELEASED': '未发行', 'CANCELLED': '已腰斩', 'HIATUS': '休刊中'}
    status_cn = status_map.get(data.get('status', ''), data.get('status', ''))

    return {
        'title_romaji': data['title']['romaji'] or (data['title'].get('native') or ''),
        'title_native': data['title'].get('native') or data['title']['romaji'],
        'year': data.get('startDate', {}).get('year', 0) or 0,
        'volumes': data.get('volumes', 0) or 0,
        'chapters': data.get('chapters', 0) or 0,
        'score': round((data.get('averageScore', 0) or 0) / 10, 1),
        'genres': data.get('genres', [])[:4],
        'cover_url': data['coverImage']['large'],
        'author': author,
        'artist': artist,
        'status': status_cn,
        'synopsis_raw': (data.get('description') or '待补完。')[:200].replace('\n', ' ').replace('<br>', ''),
    }

# ── 验证层（五验） ──

def validate_file():
    with open(OUT, 'r', encoding='utf-8') as f:
        html = f.read()
    results = {}

    # V1: 1:1
    cn_count = html.count("cn:'") + len(re.findall(r'cn:"[^"]+"', html))
    cv_urls = re.findall(r"cv:'([^']+\.(?:jpg|png|jpeg|webp))'", html)
    cv_unique = set(v.split('/')[-1] for v in cv_urls)
    results['v1_1to1'] = (cn_count == len(cv_unique), f"{cn_count} cn vs {len(cv_unique)} unique covers")

    # V2: HTTP (warning)
    fails = []
    for u in set(cv_urls):
        out, _ = shell(f"curl -sL -o /dev/null -w '%{{http_code}}' --max-time 5 '{u}'")
        if '200' not in out: fails.append(u[-40:])
    v2_ok = len(fails) == 0
    if not v2_ok: print(f"    WARN V2: {len(fails)} covers not HTTP 200")
    results['v2_http'] = (v2_ok, f"{len(fails)} fails" if fails else "all pass")

    # V3: JS语法
    issues = []
    for i, line in enumerate(html.split('\n'), 1):
        for field in ['cn', 'sp', 'author', 'artist', 'magazine']:
            for m in re.finditer(rf"{field}:'([^']*)'", line):
                if "'" in m.group(1):
                    issues.append(f"line {i}: {field} has unescaped quote")
    results['v3_syntax'] = (len(issues) == 0, "; ".join(issues) if issues else "pass")

    # V4: 结构
    db_starts = html.count('const DB = [')
    mag_orders = html.count('const magOrder')
    brace_ok = html.count('{') == html.count('}')
    results['v4_structure'] = (db_starts == 1 and mag_orders == 1 and brace_ok,
                                f"DB={db_starts} magOrder={mag_orders} braces={'OK' if brace_ok else 'FAIL'}")

    blocking = {k: v for k, v in results.items() if k != 'v2_http'}
    all_pass = all(v[0] for v in blocking.values())
    return all_pass, results

# ── 主流程 ──

def add_manga(mal_ids, interactive=True):
    print(f"\n{'='*60}")
    print(f"漫画加书 v1.0 - {len(mal_ids)} 部")
    print(f"{'='*60}")

    backup = OUT + '.backup'
    shutil.copy(OUT, backup)
    print(f"\n[1/6] 已备份")

    print(f"\n[2/6] 获取AniList数据...")
    entries = []
    for i, mid in enumerate(mal_ids):
        print(f"  [{i+1}/{len(mal_ids)}] ID:{mid} ", end='', flush=True)
        data = fetch_anilist(mid)
        if not data: print('=> FAIL'); continue
        meta = extract_meta(data)
        print(f"=> {meta['title_romaji'][:35]} | {meta['year']} | {meta['volumes']}卷 | sc:{meta['score']} | {meta['author']}")

        if interactive:
            cn_name = input("    中文名: ").strip() or meta['title_native']
            magazine = input("    连载杂志: ").strip()
            synopsis = input(f"    简介(<=100字,回车用API): ").strip() or meta['synopsis_raw']
        else:
            cn_name = meta['title_native'] or meta['title_romaji']
            magazine = '待分类'
            synopsis = meta['synopsis_raw']

        synopsis = escape_js_string(synopsis[:100])
        cn_name = escape_js_string(cn_name)

        if not verify_url(meta['cover_url']):
            print(f"    WARN: 封面不可访问 {meta['cover_url'][-50:]}")

        entries.append((mid, cn_name, meta, magazine, synopsis))
        time.sleep(1)

    if not entries:
        print("没有成功获取的条目。")
        return False

    print(f"\n[3/6] 按连载杂志分组...")
    entries_by_mag = {}
    for mid, cn_name, meta, mag, synopsis in entries:
        if mag not in entries_by_mag:
            entries_by_mag[mag] = []
        gs = json.dumps(meta['genres'], ensure_ascii=False)
        en_safe = escape_js_string(meta['title_romaji'])
        author_safe = escape_js_string(meta['author'])
        artist_safe = escape_js_string(meta['artist'])
        line = (
            f"  {{id:'m{mid}',cn:'{cn_name}',en:'{en_safe}',mag:'{mag}',"
            f"y:{meta['year']},v:{meta['volumes']},c:{meta['chapters']},sc:{meta['score']},"
            f"author:'{author_safe}',artist:'{artist_safe}',st:'{meta['status']}',"
            f"g:{gs},cv:'{meta['cover_url']}',sp:'{synopsis}'}},"
        )
        entries_by_mag[mag].append(line)
        print(f"  {mag}: {cn_name}")

    print(f"\n[4/6] 插入HTML...")
    with open(OUT, 'r', encoding='utf-8') as f: html = f.read()
    lines = html.split('\n')

    for mag, ent_lines in entries_by_mag.items():
        if f"/* ── {mag} ── */" in html:
            for i, line in enumerate(lines):
                if f"/* ── {mag} ── */" in line:
                    insert_at = i + 1
                    for j in range(i+1, len(lines)):
                        s = lines[j].strip()
                        if s.startswith('/* ──') or s == '];': insert_at = j; break
                        if 'cn:' in s or 'id:' in s: insert_at = j + 1
                    for entry in reversed(ent_lines):
                        lines.insert(insert_at, entry)
                    break
        else:
            for i, line in enumerate(lines):
                if line.strip() == '];' and 'const DB = [' in '\n'.join(lines[max(0,i-30):i]):
                    new_block = ['', f'  /* ── {mag} ── */'] + ent_lines
                    for entry in reversed(new_block):
                        lines.insert(i, entry)
                    break

    html = '\n'.join(lines)

    # 更新 magOrder
    for mag in entries_by_mag:
        if f"'{mag}'" not in html.split("const magOrder = [")[1].split("];")[0]:
            html = html.replace("const magOrder = [", f"const magOrder = ['{mag}',")

    with open(OUT, 'w', encoding='utf-8') as f: f.write(html)
    print(f"  已插入 {len(entries)} 条")

    print(f"\n[5/6] 验证...")
    passed, results = validate_file()
    for k, (ok, detail) in results.items():
        status = 'OK' if ok else ('WARN' if k == 'v2_http' else 'FAIL')
        print(f"  [{status}] {k}: {detail}")

    if not passed:
        print(f"\n验证失败！回退...")
        shutil.copy(backup, OUT)
        return False

    print(f"\n[6/6] 提交推送...")
    names = ','.join([e[1] for e in entries[:3]])
    msg = f"加漫画: {names}{'...' if len(entries)>3 else ''}"
    shell('git add manga/index.html')
    out, code = shell(f"git commit -m '{msg}'")
    if code != 0 and 'nothing to commit' not in out:
        print(f"  FAIL: {out}")
        return False
    out, code = shell('git push')
    print(f"  {'OK' if code==0 else 'FAIL'}")
    return code == 0

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(0)
    if sys.argv[1] == '--check':
        passed, results = validate_file()
        for k, (ok, detail) in results.items():
            print(f"[{'PASS' if ok else 'FAIL'}] {k}: {detail}")
        sys.exit(0 if passed else 1)
    elif sys.argv[1] == '--batch':
        with open(sys.argv[2], 'r') as f:
            ids = [int(x) for x in f.read().split() if x.strip().isdigit()]
        add_manga(ids, interactive=False)
    else:
        ids = [int(x) for x in sys.argv[1:]]
        add_manga(ids, interactive=(len(ids) <= 5))
