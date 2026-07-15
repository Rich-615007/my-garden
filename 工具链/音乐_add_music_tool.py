#!/usr/bin/env python3
"""
音乐加歌工具 v1.0
用法: python3 add_music_tool.py <NCM_ID> [NCM_ID ...]
     python3 add_music_tool.py --batch ids.txt
     python3 add_music_tool.py --check (只验证不修改)

与追番/轻小说工具一致的工作链:
  API搜索 → 拉网易云数据 → 验证封面 → 生成条目 → 定位插入 → 四验 → 提交
"""

import sys, os, re, json, time, subprocess, shutil

PROXY = 'http://127.0.0.1:7897'
NCM_API = 'https://music.163.com/api/song/detail'
OUT = r'C:\Users\HP\Desktop\娱乐的东西\我的个人网站\music\index.html'
REPO = r'C:\Users\HP\Desktop\娱乐的东西\我的个人网站'

# ── 工具函数 ──

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

# ── 网易云API ──

def fetch_ncm_detail(ncm_id):
    """通过网易云API获取歌曲信息"""
    cmd = f"curl -s --max-time 10 -H 'Referer:https://music.163.com' 'https://music.163.com/api/song/detail?ids=%5B{ncm_id}%5D'"
    out, code = shell(cmd)
    if code != 0: return None
    try:
        song = json.loads(out)['songs'][0]
        album = song.get('album', {})
        artists = [a['name'] for a in song.get('artists', [])]
        fee = song.get('fee', 0)
        year_ms = song.get('publishTime', 0) or album.get('publishTime', 0) or 0
        return {
            'name': song.get('name', ''),
            'artists': artists,
            'album_name': album.get('name', ''),
            'album_cover': album.get('picUrl', ''),
            'duration': song.get('dt', 0) // 1000,
            'year': year_ms // 1000 if year_ms else 0,
            'fee': fee,
            'can_play': (fee == 0 or fee == 8) and song.get('status', 1) >= 0,
            'warning': 'VIP(external unplayable)' if fee == 1 else ('paid album' if fee > 1 else ''),
        }
    except: return None

# ── 验证层 (追番同款四验) ──

def validate_file():
    with open(OUT, 'r', encoding='utf-8') as f:
        html = f.read()
    results = {}

    # V1: 1:1 mapping
    ids = re.findall(r"id:'([^']+)'", html)
    cv_urls = re.findall(r"cv:'([^']+\.(?:jpg|png|jpeg|webp))'", html)
    cv_unique = set(v.split('/')[-1] for v in cv_urls)
    results['v1_1to1'] = (len(ids) == len(cv_unique), f"{len(ids)} ids vs {len(cv_unique)} unique covers")

    # V2: HTTP 200 (warning only)
    fails = []
    for u in set(cv_urls):
        out, _ = shell(f"curl -sL -o /dev/null -w '%{{http_code}}' --max-time 5 '{u}'")
        if '200' not in out:
            fails.append(u[-40:])
    v2_ok = len(fails) == 0
    if not v2_ok: print(f"    WARN V2: {len(fails)} covers not HTTP 200")
    results['v2_http'] = (v2_ok, f"{len(fails)} fails" if fails else "all pass")

    # V3: JS syntax
    issues = []
    for i, line in enumerate(html.split('\n'), 1):
        for field in ['cn', 'sp', 'album', 'lyricist', 'composer', 'arranger', 'source']:
            for m in re.finditer(rf"{field}:'([^']*)'", line):
                if "'" in m.group(1):
                    issues.append(f"line {i}: {field} has unescaped quote")
    results['v3_syntax'] = (len(issues) == 0, "; ".join(issues) if issues else "pass")

    # V4: Structure
    db_starts = html.count('const DB = [')
    source_orders = html.count('const sourceOrder')
    brace_bal = html.count('{') == html.count('}')
    results['v4_structure'] = (db_starts == 1 and source_orders == 1 and brace_bal,
                                f"DB={db_starts} srcOrder={source_orders} braces={'OK' if brace_bal else 'FAIL'}")

    # V5: ncmId accessible
    ncm_ids = re.findall(r"ncm:(\d+)", html)
    ncm_fails = 0
    for nid in set(ncm_ids):
        if not verify_url(f"https://music.163.com/song?id={nid}"):
            ncm_fails += 1
    results['v5_ncm'] = (ncm_fails == 0, f"{ncm_fails}/{len(set(ncm_ids))} ncm fail" if ncm_fails else "all pass")

    # V6: forEach variable consistency (catch groups[a] vs groups[src] bugs)
    var_issues = []
    if re.search(r'sourceOrder\.forEach\s*\(\s*src\s*=>', html):
        if re.search(r'groups\[a\]', html):
            var_issues.append('forEach uses src but groups[a] found')
    results['v6_vars'] = (len(var_issues) == 0, "; ".join(var_issues) if var_issues else "pass")

    blocking = {k: v for k, v in results.items() if k != 'v2_http'}
    all_pass = all(v[0] for v in blocking.values())
    return all_pass, results

# ── 插入层 ──

def clean_group_name(raw):
    return re.sub(r'^\d+\.?\s*', '', re.sub(r'\s*\(追加\)\s*', '', raw)).strip()

def insert_entry(html, entry_line, source_group):
    """将单条条目插入到对应source分组"""
    lines = html.split('\n')
    db_start = None; db_end = None

    for i, line in enumerate(lines):
        if 'const DB = [' in line: db_start = i
        if line.strip() == '];' and db_start is not None and db_end is None: db_end = i

    # 查找该source的注释
    target_line = None
    for i in range(db_start, db_end):
        if f'── {source_group} ──' in lines[i]:
            target_line = i
            break

    if target_line:
        # 找到该组最后一个条目
        insert_at = target_line + 1
        for i in range(target_line + 1, db_end):
            stripped = lines[i].strip()
            if stripped.startswith('/*') or stripped == '];':
                insert_at = i
                break
            insert_at = i + 1
        lines.insert(insert_at, entry_line)
    else:
        # 新分组：插入到];之前
        for i in range(db_start, db_end):
            if lines[i].strip() == '];':
                new_block = ['', f'  /* ── {source_group} ── */', entry_line]
                for entry in reversed(new_block):
                    lines.insert(i, entry)
                break

    return '\n'.join(lines)

def update_source_order(html, new_source):
    """在sourceOrder数组中追加新来源"""
    pattern = r"(const sourceOrder = \[)(.*?)(\];)"
    m = re.search(pattern, html)
    if m:
        current = m.group(2)
        existing = re.findall(r"'([^']+)'", current)
        if new_source not in existing:
            new_current = current.rstrip().rstrip(',') + f",'{new_source}'"
            html = html[:m.start(2)] + new_current + html[m.end(2):]
    return html

def git_commit_push(message, backup_path=None):
    shell('git add music/index.html')
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

def add_music(ncm_ids, interactive=True):
    print(f"\n{'='*60}")
    print(f"音乐加歌 v1.0 - {len(ncm_ids)} 首")
    print(f"{'='*60}")

    backup = OUT + '.backup'
    shutil.copy(OUT, backup)

    entries = []
    for i, nid in enumerate(ncm_ids):
        print(f"\n[{i+1}/{len(ncm_ids)}] NCM:{nid}")
        data = fetch_ncm_detail(nid)
        if not data:
            print("  FAIL: 网易云API无返回")
            continue
        print(f"  歌曲: {data['name']}")
        print(f"  歌手: {', '.join(data['artists'])}")
        print(f"  专辑: {data['album_name']}")
        if data.get('warning'):
            print(f"  !! {data['warning']} !!")

        if interactive:
            cn_name = input("  中文名(回车=原名): ").strip() or data['name']
            source = input("  来源(动漫名 或 '独立: 歌手'): ").strip()
            lyricist = input("  作词(回车=未知): ").strip() or '未知'
            composer = input("  作曲(回车=未知): ").strip() or '未知'
            arranger = input("  编曲(回车跳过): ").strip()
            sp = input("  描述(≤80字): ").strip() or data['name']
        else:
            cn_name = data['name']
            source = '待分类'
            lyricist = '未知'; composer = '未知'; arranger = ''; sp = data['name']

        safe_cn = escape_js_string(cn_name)
        safe_sp = escape_js_string(sp[:80])
        art_str = json.dumps(data['artists'], ensure_ascii=False)
        track = i + 1

        if not verify_url(data['album_cover']):
            print(f"  WARN: 封面不可访问")

        entry = f"  {{id:'ncm{nid}',cn:'{safe_cn}',source:'{source}',album:'{data['album_name']}',artist:{art_str},lyricist:'{lyricist}',composer:'{composer}',arranger:'{arranger}',y:{data['year']},tn:{track},dr:{data['duration']},sc:0,cv:'{data['album_cover']}',ncm:{nid},sp:'{safe_sp}'}},"
        entries.append((entry, source))
        time.sleep(1)

    if not entries:
        print("\n没有成功获取的条目。")
        return False

    print(f"\n插入HTML...")
    with open(OUT, 'r', encoding='utf-8') as f:
        html = f.read()

    for entry, source in entries:
        html = insert_entry(html, entry, source)
        html = update_source_order(html, source)

    with open(OUT, 'w', encoding='utf-8') as f:
        f.write(html)
    print(f"  已插入 {len(entries)} 条")

    print(f"\n验证...")
    passed, results = validate_file()
    for k, (ok, detail) in results.items():
        status = 'OK' if ok else ('WARN' if k == 'v2_http' else 'FAIL')
        print(f"  [{status}] {k}: {detail}")

    if not passed:
        print(f"\n验证失败！回退到备份...")
        shutil.copy(backup, OUT)
        return False

    names = ','.join([e[0].split("cn:'")[1].split("'")[0] for e in entries[:3]])
    msg = f"加歌: {names}{'...' if len(entries)>3 else ''}"
    ok, detail = git_commit_push(msg, backup)
    print(f"  {'OK' if ok else 'FAIL'} {detail}")

    if ok:
        print(f"\n完成！{len(entries)} 首歌已添加。")
    return ok

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
        add_music(ids, interactive=False)
    else:
        ids = [int(x) for x in sys.argv[1:]]
        add_music(ids, interactive=(len(ids) <= 5))
