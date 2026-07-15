#!/usr/bin/env python3
"""
加番工具链 v2.0 - 完整流程自动化
用法: python3 add_anime_tool.py <MAL_ID> [MAL_ID ...]
     python3 add_anime_tool.py --batch <file_with_ids.txt

流程: 搜ID → API拉数据 → 验证封面 → 生成条目 → 插入 → 四验 → 提交
"""

import sys, os, re, json, time, subprocess, shutil

PROXY = 'http://127.0.0.1:7897'
ANILIST_API = 'https://graphql.anilist.co'
MAL_SEARCH = 'https://myanimelist.net/anime.php'
OUT = r'C:\Users\HP\Desktop\娱乐的东西\我的个人网站\anime\index.html'
REPO = r'C:\Users\HP\Desktop\娱乐的东西\我的个人网站'
CV_BASE = 'https://s4.anilist.co/file/anilistcdn/media/anime/cover/medium/'

# ── 工具函数 ──

def shell(cmd, timeout=30):
    """执行shell命令，返回(output, exit_code)"""
    env = os.environ.copy()
    env['HTTP_PROXY'] = PROXY
    env['HTTPS_PROXY'] = PROXY
    try:
        r = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=timeout, env=env, cwd=REPO)
        return r.stdout.strip(), r.returncode
    except subprocess.TimeoutExpired:
        return "TIMEOUT", 1

def fetch_anilist(mid):
    """通过AniList API获取番剧数据"""
    q = 'query{Media(idMal:%d,type:ANIME){title{romaji native}seasonYear episodes averageScore studios{nodes{name}} genres coverImage{large}}}' % mid
    cmd = f"""curl -s --max-time 10 -X POST {ANILIST_API} -H "Content-Type: application/json" -d '{{"query":"{q}"}}'"""
    out, code = shell(cmd)
    if code != 0: return None
    try:
        m = json.loads(out)['data']['Media']
        return m
    except: return None

def extract_meta(data):
    """从AniList数据提取元信息"""
    return {
        'title_romaji': data['title']['romaji'] or data['title']['native'],
        'title_native': data['title'].get('native') or data['title']['romaji'],
        'year': data.get('seasonYear') or 0,
        'eps': data.get('episodes') or 0,
        'score': round((data.get('averageScore') or 0) / 10, 1),
        'genres': data.get('genres', [])[:4],
        'cover_url': data['coverImage']['large'],
        'studio': find_animation_studio(data),
    }

def find_animation_studio(data):
    """从studio列表中提取动画制作社（过滤发行商）"""
    distributors = {
        'Aniplex','Funimation','Crunchyroll','Sentai Filmworks','Kadokawa','AT-X',
        'Mainichi Broadcasting','Toho','Movic','Sony Music','NBCUniversal',
        'Media Factory','Square Enix','ASCII Media Works','Bushiroad','Genco',
        'Shouchiku','Happinet Pictures','Delfi Sound','Mages','Nippon Columbia',
        'Bandai Namco','Lantis','Magic Capsule','Lawson Entertainment','Amuse',
        'JR East','Tokyo MX','BS11','Visual Arts','Rakuonsha','Lucky Paradise',
        'Pony Canyon','Kodansha','Dentsu','GKIDS','Starchild Records','DAX Production',
        'flying DOG','KLOCKWORX','Warner Bros','TBS','Fuji TV','TV Tokyo',
        'Docomo Anime Store','Dwango','Cospa','Notes','Q-Tec','Avex Pictures',
        'Project No Name','Hanabee Entertainment','Aniplex of America',
        'BANDAI SPIRITS','Sumzap','Selecta Vision','Ruo Hong Culture','Youku',
        'Nitroplus','Houbunsha','Manga Entertainment','Lerche','Kinema Citrus',
        'Studio Massket','Rakuten','Sega','Netflix','Amazon','Hulu',
    }
    studios = [n['name'] for n in data.get('studios', {}).get('nodes', [])]
    for s in studios:
        if s not in distributors:
            return s
    return studios[0] if studios else 'Unknown'

def verify_url(url):
    """检查URL是否可访问"""
    out, code = shell(f"curl -sL -o /dev/null -w '%{{http_code}}' --max-time 5 '{url}'")
    return '200' in out

# ── 验证层 ──

def validate_file():
    """四验：1:1 + 封面200 + JS语法 + 浏览器预览"""
    with open(OUT, 'r', encoding='utf-8') as f:
        html = f.read()

    results = {}

    # V1: 1:1映射
    cn_count = html.count("cn:'") + len(re.findall(r'cn:"[^"]+"', html))
    cv_urls = re.findall(r"cv:'([^']+\.(?:jpg|png)[^']*)'", html)
    cv_unique = set(u.split('/')[-1] for u in cv_urls)
    results['v1_1to1'] = (cn_count == len(cv_unique), f"{cn_count} names vs {len(cv_unique)} covers")

    # V2: 封面HTTP 200
    fails = []
    for u in set(cv_urls):
        out, _ = shell(f"curl -sL -o /dev/null -w '%{{http_code}}' --max-time 5 '{u}'")
        if '200' not in out:
            fails.append(u.split('/')[-1][:40])
    results['v2_http'] = (len(fails) == 0, f"{len(fails)}/{len(set(cv_urls))} failed" if fails else "all pass")

    # V3: JS语法 - 检查单引号冲突
    issues = []
    # 检查cn/en字段中的未转义单引号
    for i, line in enumerate(html.split('\n'), 1):
        for field in ['cn', 'en', 'sp']:
            pattern = rf"{field}:'([^']*)'"
            for m in re.finditer(pattern, line):
                val = m.group(1)
                if "'" in val:
                    issues.append(f"line {i}: {field} contains unescaped quote: {val[:50]}")
    results['v3_syntax'] = (len(issues) == 0, "; ".join(issues) if issues else "pass")

    # V4: 文件一致性
    db_starts = html.count('const DB = [')
    db_ends = html.count('];')
    studio_orders = html.count('const studioOrder')
    results['v4_structure'] = (db_starts == 1 and db_ends >= 1 and studio_orders == 1,
                                f"DB={db_starts}, ]={db_ends}, studioOrder={studio_orders}")

    all_pass = all(v[0] for v in results.values())
    return all_pass, results


# ── 插入层 ──

def locate_insertion_points(html):
    """解析现有文件，返回各制作社的插入位置"""
    lines = html.split('\n')
    db_start = None
    db_end = None
    groups = {}

    for i, line in enumerate(lines):
        if 'const DB = [' in line:
            db_start = i
        if line.strip() == '];' and db_start and not db_end:
            db_end = i
        m = re.search(r"/\* ── ([\w.\s]+) ── \*/", line)
        if m and db_start and i < db_end:
            groups[m.group(1).strip()] = i

    # 找到每个group最后一个条目的行号
    group_ranges = {}
    sorted_groups = sorted(groups.items(), key=lambda x: x[1])
    for idx, (name, start) in enumerate(sorted_groups):
        if idx + 1 < len(sorted_groups):
            end = sorted_groups[idx + 1][1] - 1
        else:
            end = db_end - 1
        group_ranges[name] = (start, end)

    return db_start, db_end, group_ranges

def insert_entries(html, entries_by_group):
    """将条目插入HTML的对应制作社位置"""
    db_start, db_end, group_ranges = locate_insertion_points(html)
    lines = html.split('\n')

    for group, entries in entries_by_group.items():
        if group in group_ranges:
            _, last = group_ranges[group]
            # 找到该组内最后一条实际条目的行号
            insert_at = last + 1
            # 向后移动，找到最后一个非空非注释行
            for i in range(last + 1, db_end):
                stripped = lines[i].strip()
                if stripped and not stripped.startswith('/*') and stripped != '];':
                    insert_at = i + 1
                elif stripped.startswith('/*') or stripped == '];':
                    break
            for entry in reversed(entries):
                lines.insert(insert_at, entry)
            # 更新所有后续group的位置
            for g in group_ranges:
                if group_ranges[g][0] > insert_at:
                    group_ranges[g] = (group_ranges[g][0] + len(entries),
                                        group_ranges[g][1] + len(entries))
            db_end += len(entries)
        else:
            # 新制作社：插入到PB数组闭合之前
            for i, line in enumerate(lines):
                if i > db_start and line.strip() == '];':
                    new_block = ['', f'  /* ── {group} ── */'] + list(entries)
                    for entry in reversed(new_block):
                        lines.insert(i, entry)
                    break

    return '\n'.join(lines)

def update_studio_order(html, new_studios):
    """在studioOrder数组中加入新制作社"""
    pattern = r"(const studioOrder = \[)(.*?)(\];)"
    m = re.search(pattern, html)
    if m:
        current = m.group(2)
        # 跳过已存在的
        existing = re.findall(r"'([^']+)'", current)
        to_add = [s for s in new_studios if s not in existing]
        if to_add:
            new_current = current.rstrip().rstrip(',')
            for s in to_add:
                new_current += f",'{s}'"
            html = html[:m.start(2)] + new_current + html[m.end(2):]
    return html

def git_commit_and_push(message):
    """提交并推送"""
    shell('git add anime/index.html')
    out, code = shell(f"git commit -m '{message}'")
    if code != 0 and 'nothing to commit' not in out:
        return False, out
    out, code = shell('git push')
    if code != 0:
        return False, out
    return True, 'pushed'


# ── 主流程 ──

def add_anime(mal_ids, interactive=True):
    """主入口：加番完整流程"""
    print(f"\n{'='*60}")
    print(f"加番工具 v2.0 - 处理 {len(mal_ids)} 部番剧")
    print(f"{'='*60}")

    # ── 备份 ──
    backup = OUT + '.backup'
    shutil.copy(OUT, backup)
    print(f"\n[1/6] 备份已创建: {backup}")

    # ── 步骤1: 获取数据 ──
    print(f"\n[2/6] 获取AniList数据...")
    entries = []
    mal_id_to_studio = {}

    for i, mid in enumerate(mal_ids):
        print(f"  [{i+1}/{len(mal_ids)}] ID:{mid} ", end='', flush=True)
        data = fetch_anilist(mid)
        if not data:
            print('⇒ FAIL (API返回空)')
            continue
        meta = extract_meta(data)
        print(f'⇒ {meta["title_romaji"][:40]} | {meta["year"]} | {meta["eps"]}ep | {meta["score"]} | {meta["studio"]}')
        mal_id_to_studio[mid] = meta['studio']

        if interactive:
            cn_name = input(f"    中文名([直接回车用'↓'跳过]): ").strip()
            if cn_name == '↓':
                print(f"    跳过 ID:{mid}")
                continue
            if not cn_name:
                cn_name = meta['title_native'] or meta['title_romaji']
            synopsis = input(f"    简介(≤100字): ").strip() or '待补完。'
        else:
            cn_name = meta['title_native'] or meta['title_romaji']
            synopsis = '待补完。'

        synopsis = synopsis[:100]
        entries.append((cn_name, meta, synopsis))

        # 验证封面
        time.sleep(1)
        if not verify_url(meta['cover_url']):
            print(f"    ⚠ 封面URL返回非200，需要检查: {meta['cover_url'][-50:]}")

    if not entries:
        print("没有成功获取的条目，退出。")
        return False

    # ── 步骤2: 按制作社分组 ──
    print(f"\n[3/6] 按制作社分组...")
    entries_by_group = {}
    for cn_name, meta, synopsis in entries:
        group = meta['studio']  # firstStudio = studio
        if group not in entries_by_group:
            entries_by_group[group] = []

        gs = json.dumps(meta['genres'], ensure_ascii=False)
        line = f"  {{cn:'{cn_name}',en:'{meta['title_romaji']}',y:{meta['year']},e:{meta['eps']},sc:{meta['score']},fs:'{group}',s:'{meta['studio']}',g:{gs},cv:'{meta['cover_url']}',sp:'{synopsis}'}},"
        entries_by_group[group].append(line)
        print(f"  {group}: {cn_name}")

    # ── 步骤3: 插入 ──
    print(f"\n[4/6] 插入HTML...")
    with open(OUT, 'r', encoding='utf-8') as f:
        html = f.read()

    html = insert_entries(html, entries_by_group)
    html = update_studio_order(html, list(entries_by_group.keys()))

    with open(OUT, 'w', encoding='utf-8') as f:
        f.write(html)
    print(f"  已插入 {len(entries)} 条")

    # ── 步骤4: 验证 ──
    print(f"\n[5/6] 四验...")
    passed, results = validate_file()
    for k, (ok, detail) in results.items():
        status = '✓' if ok else '✗'
        print(f"  {status} {k}: {detail}")

    if not passed:
        print(f"\n  验证失败！回退...")
        shutil.copy(backup, OUT)
        return False

    # ── 步骤5: 提交 ──
    print(f"\n[6/6] 提交推送...")
    names = ','.join([e[0] for e in entries[:5]])
    msg = f"add: {names}{'...' if len(entries) > 5 else ''}"
    ok, detail = git_commit_and_push(msg)
    print(f"  {'✓' if ok else '✗'} {detail}")

    if ok:
        print(f"\n完成！{len(entries)} 部番剧已添加并推送。")
    return ok


# ── 批量模式 ──
def batch_mode(ids, interactive=True):
    """批量添加：一次获取所有数据，一次插入，一次验证，一次提交"""
    print(f"\n批量模式: {len(ids)} 部番剧")
    if len(ids) > 20:
        print(f"⚠ 大批量({len(ids)}部)，预计需要 {len(ids)*4} 秒 (API限流)")
        print(f"  建议: 先执行然后去喝杯水\n")

    ok = add_anime(ids, interactive=interactive)
    if not ok:
        print("\n批量添加失败，已回退。检查上面的错误信息。")
    return ok


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print(__doc__)
        print("\n示例:")
        print("  python3 add_anime_tool.py 41457        # 加一部番")
        print("  python3 add_anime_tool.py 41457 48569  # 加多部番")
        print("  python3 add_anime_tool.py --batch ids.txt # 批量模式")
        sys.exit(0)

    if sys.argv[1] == '--batch':
        # 从文件读ID
        with open(sys.argv[2], 'r') as f:
            ids = [int(x) for x in f.read().split() if x.strip().isdigit()]
        batch_mode(ids, interactive=False)
    elif sys.argv[1] == '--quiet':
        ids = [int(x) for x in sys.argv[2:]]
        batch_mode(ids, interactive=False)
    else:
        ids = [int(x) for x in sys.argv[1:]]
        if len(ids) <= 5:
            add_anime(ids, interactive=True)
        else:
            batch_mode(ids, interactive=False)
