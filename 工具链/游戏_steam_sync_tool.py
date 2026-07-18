#!/usr/bin/env python3
"""
游戏 Steam 同步工具 v1.0
从 Steam 库拉取游戏 → 对比现有条目 → 生成新条目插入 game/index.html
用法:
  python3 工具链/游戏_steam_sync_tool.py           # 交互模式: 显示新游戏, 逐个确认
  python3 工具链/游戏_steam_sync_tool.py --check   # 验证模式
  python3 工具链/游戏_steam_sync_tool.py --dry     # 预览模式: 只显示不上传
"""

import sys, os, re, json, urllib.request, urllib.error, time, subprocess, http.client

REPO = r'C:\Users\HP\Desktop\娱乐的东西\我的个人网站'
GAME_HTML = os.path.join(REPO, 'game', 'index.html')

# ── 加载配置 ──
def load_env():
    env = {}
    env_file = os.path.join(os.path.dirname(__file__), '.env')
    with open(env_file, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                k, v = line.split('=', 1)
                env[k.strip()] = v.strip()
    return env

# ── HTTP 请求 ──
def fetch(url, retries=3):
    for i in range(retries):
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'SteamSync/1.0'})
            with urllib.request.urlopen(req, timeout=30) as resp:
                data = resp.read()
                return json.loads(data.decode('utf-8'))
        except Exception as e:
            if i == retries - 1:
                print(f"  HTTP FAIL ({url[:80]}...): {e}")
                return None
            time.sleep(2)
    return None

# ── 从 game/index.html 提取已有 appid ──
def extract_existing_appids():
    """解析 game/index.html 的 DB 数组, 提取所有已有 appid"""
    with open(GAME_HTML, 'r', encoding='utf-8') as f:
        html = f.read()

    appids = set()
    # 匹配 appid:数字
    for m in re.finditer(r'appid:\s*(\d+)', html):
        appids.add(int(m.group(1)))
    # 匹配 cv 中的 Steam CDN URL
    for m in re.finditer(r'steamcdn[^"\']*?/apps/(\d+)/', html):
        if int(m.group(1)) not in appids:
            appids.add(int(m.group(1)))
    return appids

# ── 获取 Steam 库 ──
def get_owned_games(key, steam_id):
    url = f'https://api.steampowered.com/IPlayerService/GetOwnedGames/v1/?key={key}&steamid={steam_id}&include_appinfo=true&include_played_free_games=true&format=json'
    data = fetch(url)
    if not data or 'response' not in data:
        print("FAIL: Steam API 无响应, 检查 Key 和 ID 是否正确")
        return []
    games = data['response'].get('games', [])
    return sorted(games, key=lambda g: g.get('playtime_forever', 0), reverse=True)

# ── 游戏分类过滤 ──
EXCLUDE_KEYWORDS = ['wallpaper', 'engine', 'sdk', 'benchmark', 'demo', 'prologue',
                     '3dmark', 'heaven', 'vrchat', 'tabletop', 'streaming']
EXCLUDE_APPIDS = {404790}  # Godot Engine 等工具

def is_game_worthy(game):
    """过滤不值得加入收藏站的游戏(工具/0分钟等)"""
    appid = game['appid']
    name = game.get('name', '').lower()
    playtime = game.get('playtime_forever', 0)

    if appid in EXCLUDE_APPIDS:
        return False
    # 排除工具软件
    if any(kw in name for kw in EXCLUDE_KEYWORDS):
        return False
    # 排除 0 分钟且免费的(大概率是领了没玩)
    if playtime == 0:
        return False
    return True

# ── Store API 获取游戏详情 ──
def get_game_details(appid):
    """从 Steam Store API 获取游戏详情"""
    url = f'https://store.steampowered.com/api/appdetails?appids={appid}&cc=cn'
    data = fetch(url)
    if not data or str(appid) not in data:
        return None
    info = data[str(appid)]
    if not info.get('success'):
        return None
    d = info['data']
    # 排除: 纯DLC（type=dlc 且没有独立游戏属性）
    if d.get('type') == 'dlc':
        return {'_type': 'dlc', 'appid': appid, 'name': d.get('name', '')}

    # 中文名优先(如果商店有中文)
    cn_name = ''
    en_name = d.get('name', '')
    # Steam 返回的 name 取决于地区; 尝试从 supported_languages 取中文
    if 'zh-Hans' in str(d.get('supported_languages', '')):
        cn_name = en_name  # cc=cn 在中国区能拿到中文名

    # 制作社/发行商
    devs = d.get('developers', [])
    pubs = d.get('publishers', [])
    dev = devs[0] if devs else '?'
    pub = pubs[0] if pubs else dev

    # 年份
    release = d.get('release_date', {})
    year = int(release['date'][-4:]) if release.get('date') and len(release['date']) >= 4 else 0

    # 标签/类型
    genres = [g['description'] for g in d.get('genres', [])[:3]]

    # 平台
    platforms = []
    if d.get('platforms', {}).get('windows'): platforms.append('PC')
    if d.get('platforms', {}).get('mac'): platforms.append('Mac')
    if d.get('platforms', {}).get('linux'): platforms.append('Linux')

    # 简介(简体中文优先, 截 80 字)
    desc = d.get('short_description', '')
    if len(desc) > 120:
        desc = desc[:117] + '...'

    # 评价
    score = 0
    if 'metacritic' in d and d['metacritic']:
        score = d['metacritic'].get('score', 0)
    # 转成 10 分制
    score = round(score / 10, 1) if score else 0

    # 封面
    header = d.get('header_image', '')

    return {
        '_type': 'game',
        'appid': appid,
        'cn': cn_name,
        'en': en_name,
        'dev': dev,
        'pub': pub,
        'y': year,
        'pf': '/'.join(platforms) if platforms else 'PC',
        'sc': score,
        'g': genres,
        'cv': header,
        'sp': desc,
    }

# ── 安全转义 ──
def escape_js_string(s):
    s = s.replace('\\', '\\\\')
    s = s.replace("'", "\\'")
    s = s.replace('\n', ' ')
    s = s.replace('\r', '')
    return s

# ── DLC 检查 ──
def get_dlcs(appid, all_games):
    """检查是否有对应的 DLC 在库里"""
    url = f'https://store.steampowered.com/api/appdetails?appids={appid}&cc=cn'
    data = fetch(url)
    if not data or str(appid) not in data:
        return []
    info = data[str(appid)]
    if not info.get('success'):
        return []
    dlc_list = info['data'].get('dlc', [])
    # 检查哪些 DLC 在用户库里
    owned_dlcs = []
    for dlc_appid in dlc_list:
        for g in all_games:
            if g['appid'] == dlc_appid:
                dlc_data = get_game_details(dlc_appid)
                if dlc_data and dlc_data['_type'] == 'dlc':
                    owned_dlcs.append({
                        'cn': dlc_data.get('cn', dlc_data['name']),
                        'y': dlc_data.get('y', 0),
                        'pf': dlc_data.get('pf', 'PC'),
                        'sc': dlc_data.get('sc', 0),
                    })
                break
    return owned_dlcs

# ── 生成 JS 条目 ──
next_id = 0

def gen_entry(info, existing_max_id):
    """生成单条 JS 条目字符串"""
    global next_id
    n = existing_max_id + 1 + next_id
    next_id += 1
    cn = escape_js_string(info['cn'] or info['en'])
    en = escape_js_string(info['en'])
    dev = escape_js_string(info['dev'])
    pub = escape_js_string(info['pub'])
    cv = escape_js_string(info['cv'])
    sp = escape_js_string(info.get('sp', ''))
    g_str = str(info['g']).replace("'", "\\'")
    sc = info.get('sc', 0)
    y = info.get('y', 0)
    pf = escape_js_string(info.get('pf', 'PC'))
    appid = info['appid']

    entry = f"{{id:'g{n:02d}',cn:'{cn}',en:'{en}',appid:{appid},dev:'{dev}',pub:'{pub}',y:{y},pf:'{pf}',sc:{sc},g:{g_str},cv:'{cv}',sp:'{sp}'}}"
    return entry

# ── 提取已有最大 ID ──
def get_max_id():
    with open(GAME_HTML, 'r', encoding='utf-8') as f:
        html = f.read()
    max_n = 0
    for m in re.finditer(r"id:'g(\d+)'", html):
        n = int(m.group(1))
        if n > max_n:
            max_n = n
    return max_n

# ── 插入条目 ──
def insert_entries(entries_by_dev):
    """按制作社插入新条目到 game/index.html"""
    with open(GAME_HTML, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    # 找到 DB 结束位置
    db_end = None
    for i, line in enumerate(lines):
        if line.strip() == '];':
            db_end = i
            break

    # 找到 devOrder 行
    dev_order_line = None
    for i, line in enumerate(lines):
        if 'const devOrder' in line:
            dev_order_line = i
            break

    if db_end is None or dev_order_line is None:
        print("FAIL: 无法定位插入点")
        return False

    # 构造新条目行
    new_entry_lines = []
    for dev, entries in entries_by_dev.items():
        new_entry_lines.append(f'  /* ── {dev} ── */\n')
        for e in entries:
            new_entry_lines.append(f'  {e},\n')

    # 在 ]; 之前插入
    for line in reversed(new_entry_lines):
        lines.insert(db_end, line)

    # 更新 devOrder
    dev_order_str = lines[dev_order_line]
    existing_devs = re.findall(r"'([^']*)'", dev_order_str)
    new_devs = [d for d in entries_by_dev.keys() if d not in existing_devs]
    if new_devs:
        combined = existing_devs + new_devs
        lines[dev_order_line] = "const devOrder = [" + ",".join(f"'{d}'" for d in combined) + "];\n"

    # 写回
    with open(GAME_HTML, 'w', encoding='utf-8') as f:
        f.writelines(lines)

    return True

# ── V6 一致性检查 ──
def check_consistency():
    with open(GAME_HTML, 'r', encoding='utf-8') as f:
        html = f.read()
    issues = []

    # 大括号平衡
    if html.count('{') != html.count('}'):
        issues.append('大括号不平衡')

    # DB 数组
    db_count = html.count("const DB = ")
    if db_count != 1:
        issues.append(f'DB 声明不是1次: {db_count}')

    # devOrder 数组
    devo_count = html.count("const devOrder = ")
    if devo_count != 1:
        issues.append(f'devOrder 声明不是1次: {devo_count}')

    # forEach 一致性检查 (devOrder.forEach 后不能有 groups 赋值/修改)
    for_each_pos = html.find('devOrder.forEach')
    if for_each_pos >= 0:
        rest = html[for_each_pos:]
        # 匹配 groups[...]= (赋值) 出现在 forEach 之后 → V6 bug
        if re.search(r'groups\[[^\]]*\]\s*=', rest):
            issues.append('groups[...]= 赋值出现在 forEach 之后 (V6 bug)')

    # 检查 devOrder 与 groups 键一致
    devs_in_order = set(re.findall(r"devOrder\s*=\s*\[([^\]]*)\]", html)[0].replace("'","").split(','))
    devs_in_db = set()
    for m in re.finditer(r"dev:'([^']*)'", html):
        devs_in_db.add(m.group(1))
    extra = devs_in_order - devs_in_db
    missing = devs_in_db - devs_in_order
    if extra:
        issues.append(f'devOrder 多余: {extra}')
    if missing:
        issues.append(f'devOrder 缺少: {missing}')

    return issues

# ═══════════════════ 主流程 ═══════════════════

def main():
    env = load_env()
    key = env.get('STEAM_API_KEY', '')
    steam_id = env.get('STEAM_ID', '')

    if '--check' in sys.argv:
        issues = check_consistency()
        if issues:
            print("FAIL:")
            for i in issues:
                print(f"  - {i}")
            sys.exit(1)
        else:
            print("PASS: 游戏页一致性检查通过")
            sys.exit(0)

    dry_run = '--dry' in sys.argv
    if dry_run:
        print("=== 预览模式: 不会修改文件 ===\n")

    print(f'Steam ID: {steam_id}')
    print('获取库游戏列表...')
    all_games = get_owned_games(key, steam_id)
    if not all_games:
        print("无法获取游戏列表。检查 Key 是否有效。")
        print("注意: 吊销后的 Key 需要重新生成。")
        sys.exit(1)

    print(f'库内游戏: {len(all_games)} 款\n')

    # 过滤
    worthy = [g for g in all_games if is_game_worthy(g)]
    print(f'可收藏(去工具/0分钟): {len(worthy)} 款')

    # 已有 appid
    existing = extract_existing_appids()
    print(f'网站已有: {len(existing)} 款 ({sorted(existing)})')

    # 新游戏(库里有但站点无)
    candidates = [g for g in worthy if g['appid'] not in existing]
    print(f'待审核: {len(candidates)} 款\n')

    if not candidates:
        print('没有新游戏需要同步。')
        return

    # 交互模式
    approved = []
    print('--- 逐个确认 ---')
    for i, g in enumerate(candidates):
        appid = g['appid']
        name = g.get('name', f'AppID {appid}')
        pt_h = g.get('playtime_forever', 0) // 60
        print(f'\n[{i+1}/{len(candidates)}] {name} (appid={appid}, {pt_h}小时)')
        if dry_run:
            print("  [预览模式 跳过]")
            continue
        ans = input('  加入收藏站? [y/n/q] ').strip().lower()
        if ans == 'y':
            print('  拉取详情...')
            info = get_game_details(appid)
            if info and info['_type'] == 'game':
                print(f'    → {info["dev"]} / {info["pub"]} / {info["y"]} / ⭐{info["sc"]}')
                print(f'    → tags: {info["g"]}')
                approved.append(info)
            elif info and info['_type'] == 'dlc':
                print(f'  → 这是 DLC, 需要手动归入正作弹窗。暂跳过。')
            else:
                print(f'  → Store API 无数据, 跳过')
            time.sleep(2)
        elif ans == 'q':
            print('退出。')
            break
        else:
            print('  跳过。')

    if not approved:
        print('\n没有确认的游戏。结束。')
        return

    # 按制作社分组
    print(f'\n确认 {len(approved)} 款, 按制作社分组:')
    by_dev = {}
    for info in approved:
        dev = info['dev']
        if dev not in by_dev:
            by_dev[dev] = []
        by_dev[dev].append(info)

    for dev, entries in by_dev.items():
        print(f'  {dev}: {len(entries)} 款')

    if dry_run:
        print('\n预览模式结束。去掉 --dry 执行写入。')
        return

    ans = input('\n确认写入 game/index.html? [y/n] ').strip().lower()
    if ans != 'y':
        print('取消。')
        return

    # 备份
    bak = GAME_HTML + '.bak'
    with open(GAME_HTML, 'r', encoding='utf-8') as src:
        with open(bak, 'w', encoding='utf-8') as dst:
            dst.write(src.read())
    print(f'备份: {bak}')

    # 生成 JS 条目
    global next_id
    next_id = 0
    max_id = get_max_id()
    entries_js = {}
    for dev, entries in by_dev.items():
        entries_js[dev] = []
        for info in entries:
            entry = gen_entry(info, max_id)
            entries_js[dev].append(entry)

    # 插入
    ok = insert_entries(entries_js)
    if not ok:
        print('插入失败, 用备份恢复!')
        return

    print('写入完成。运行一致性检查...')
    time.sleep(0.5)
    issues = check_consistency()
    if issues:
        print(f'FAIL: 发现 {len(issues)} 个问题:')
        for i in issues:
            print(f'  - {i}')
        print(f'\n请手动修复或从备份恢复: {bak}')
    else:
        print('PASS: 一致性检查通过')
        os.remove(bak)
        print('备份已清理。可以 commit+push。')

if __name__ == '__main__':
    main()
