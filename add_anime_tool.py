"""加新番工具 - 规范流程
用法: python3 add_anime_tool.py <MAL_ID_1> <MAL_ID_2> ...
例: python3 add_anime_tool.py 34537 35247 40051
"""
import urllib.request, json, time, re, sys

OUT = r"C:\Users\HP\Desktop\娱乐的东西\我的个人网站\anime\index.html"
PROXY = 'http://127.0.0.1:7897'

proxy = urllib.request.ProxyHandler({'http': PROXY, 'https': PROXY})
opener = urllib.request.build_opener(proxy)

def fetch(mid, retries=3):
    for _ in range(retries):
        time.sleep(4)
        q = 'query{Media(idMal:%d,type:ANIME){title{romaji native}seasonYear episodes averageScore studios{nodes{name}} genres coverImage{large}}}' % mid
        req = urllib.request.Request('https://graphql.anilist.co',
            data=json.dumps({'query':q}).encode(), headers={'Content-Type':'application/json'})
        try:
            with opener.open(req, timeout=10) as r:
                d = json.loads(r.read())['data']['Media']
                return d
        except: continue
    return None

def verify(url):
    import subprocess
    code = subprocess.run(
        ['curl', '-sL', '-o', '/dev/null', '-w', '%{http_code}', '--max-time', '5', url],
        env={**__import__('os').environ, 'HTTP_PROXY': PROXY, 'HTTPS_PROXY': PROXY},
        capture_output=True, text=True, timeout=10).stdout
    return code == '200'

if __name__ == '__main__':
    ids = [int(x) for x in sys.argv[1:]]
    if not ids:
        print("用法: python3 add_anime_tool.py MAL_ID_1 MAL_ID_2 ...")
        sys.exit(1)

    print(f"Fetching {len(ids)} anime...")
    for mid in ids:
        d = fetch(mid)
        if not d:
            print(f"  [FAIL] ID {mid}: API返回空")
            continue

        title = d['title']['romaji'] or d['title']['native']
        year = d.get('seasonYear', '')
        eps = d.get('episodes', 0) or 0
        score = round((d.get('averageScore', 0) or 0)/10, 1)
        cover = d['coverImage']['large']
        # Studio: take first relevant animation studio
        studios = [n['name'] for n in d.get('studios', {}).get('nodes', []) if n['name'] not in
                   ['Aniplex','Funimation','Crunchyroll','Sentai Filmworks','Kadokawa','AT-X',
                    'Mainichi Broadcasting','Toho','Movic','Sony Music','NBCUniversal',
                    'Media Factory','Square Enix','ASCII Media Works','Bushiroad',
                    'Genco','Shouchiku','Happinet Pictures','Delfi Sound','Mages',
                    'Nippon Columbia','Bandai Namco','Lantis','Magic Capsule',
                    'Lawson Entertainment','Amuse','JR East','Tokyo MX','BS11',
                    'Visual Arts','Rakuonsha','Lucky Paradise']]
        studio = studios[0] if studios else 'Unknown'
        genres = d.get('genres', [])[:4] or ['剧情']
        group = studio  # firstSeason studio

        print(f"\n  ID: {mid}")
        print(f"  标题: {d['title']['romaji']}")
        print(f"  年份: {year} | 集数: {eps} | 评分: {score}")
        print(f"  制作社: {studio}")
        print(f"  分类: {genres}")
        print(f"  封面: {cover}")
        print(f"  封面验证: {'OK' if verify(cover) else 'FAIL - 需检查'}")

        # Generate JS entry
        synopsis = input("  输入简介(中文, ≤100字): ") or "待补完。"
        cn_name = input("  中文名: ") or title

        js = f"  {{cn:'{cn_name}',en:'{title}',y:{year},e:{eps},sc:{score},fs:'{group}',s:'{studio}',g:{json.dumps(genres,ensure_ascii=False)},cv:'{cover}',sp:'{synopsis[:100]}'}},"
        print(f"\n  生成条目:\n{js}")
