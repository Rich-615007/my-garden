import json, re

OUT = r"C:\Users\HP\Desktop\娱乐的东西\我的个人网站\anime\index.html"

# Correct AniList cover URLs (from API, medium size)
covers = {
    918: 'bx918-iOaeBVUn4uK7.jpg',
    9969: 'bx9969-0GaRABYVdUcH.png',
    28977: 'bx20996-kBEGEGdeK1r7.jpg',
    34096: 'bx97889-ytqHdmus9wQi.jpg',
    5909: 'bx5909-cqlzezmvzLWa.png',
    10464: 'bx10464-BlUWhUYM8DWz.png',
    14719: 'bx14719-VT5dRzTBSZ0w.jpg',
    20899: 'bx20474-xuqem5GBlBtb.jpg',
    26055: 'bx20799-S1eyqBDlx51E.jpg',
    31933: 'bx21450-D7XFwEQjZ5GA.jpg',
    37991: 'bx102883-S9KzdMJhDswJ.png',
    48661: 'bx131942-rermlZ9lplHX.png',
    23277: 'nx20657-pMZBj6K6mLhi.jpg',
    30727: 'nx21180-6ob7MFdjttYe.jpg',
    36885: 'bx100675-Ut2Qyi9gYOKT.png',
    849: 'bx849-wQM3GqLvl62P.png',
    4382: 'bx4382-ojMWjGFfJFmN.png',
    7311: 'bx7311-9Mfc1YRHwCCW.jpg',
    14741: 'bx14741-CGXEIeUe2roA.jpg',
    18671: 'bx18671-RVIY9TGd737H.jpg',
    232: 'bx232-ERyKCNNPJJeh.png',
    33354: 'bx97881-QGpBWNtdCxrZ.png',
    42310: 'bx120377-ayZPoxiWt4Li.jpg',
    18679: 'b18679-lbkq7iYESoFW.png',
    33489: 'bx21858-huBrbIOGMYXv.jpg',
    2001: 'bx2001-XwRnjzGeFWRQ.png',
    11751: 'bx11751-CNf1IlrvzbEa.png',
    15793: 'bx15793-CNcrWE9Eqzkg.png',
    21573: 'bx20560-ghaHjE5lfnEt.png',
    32836: 'bx21672-jDZ3sy89XMMQ.png',
    32843: 'bx21673-ZXlqf3DGJph9.png',
}

with open(OUT, 'r', encoding='utf-8') as f:
    html = f.read()

old_count = 0
for mid, new_file in covers.items():
    # Find the old URL pattern: large/bxXXXXX-...jpg or large/bxXXXXX-...png
    pattern = r"s4\.anilist\.co/file/anilistcdn/media/anime/cover/large/[a-z]*\d+-\w+\.[a-z]+"
    matches = re.findall(pattern, html)
    for old_url in matches:
        if old_url in html:
            new_url = f"s4.anilist.co/file/anilistcdn/media/anime/cover/medium/{new_file}"
            html = html.replace(old_url, new_url, 1)
            old_count += 1
            break

with open(OUT, 'w', encoding='utf-8') as f:
    f.write(html)

print(f"Replaced {old_count} cover URLs")
