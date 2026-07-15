import re
B = "https://s4.anilist.co/file/anilistcdn/media/anime/cover/medium/"
entries = [
"\n  /* ── CoMix Wave ── */",
"  {cn:'秒速五厘米',en:'5 Centimeters per Second',y:2007,e:3,sc:7.2,fs:'CoMix Wave',s:'CoMix Wave',g:['剧情','恋爱','日常'],cv:'"+B+"bx1689-rJKhjLEjQHSy.jpg',sp:'樱花飘落的速度是秒速五厘米。贵树和明里在小学毕业后分离。多年后的擦肩而过。'},",
"\n  /* ── feel. ── */",
"  {cn:'缘之空',en:'Yosuga no Sora',y:2010,e:12,sc:5.6,fs:'feel.',s:'feel.',g:['剧情','恋爱','校园'],cv:'"+B+"bx8861-DZKseZpdtBwp.jpg',sp:'双胞胎兄妹悠和穹回到乡下小镇。每个人心中都藏着无法言说的感情。'},",
"\n  /* ── SILVER LINK. ── */",
"  {cn:'笨蛋测验召唤兽',en:'Baka to Test Shoukanjuu',y:2010,e:13,sc:7.1,fs:'SILVER LINK.',s:'SILVER LINK.',g:['喜剧','校园','恋爱'],cv:'"+B+"bx6347-DCSHLkCY7UT3.jpg',sp:'文月学园按成绩分班。F班的笨蛋们向高年级发起召唤兽战争。'},",
"  {cn:'笨蛋测验召唤兽 2',en:'Baka to Test Ni!',y:2011,e:13,sc:7.4,fs:'SILVER LINK.',s:'SILVER LINK.',g:['喜剧','校园','恋爱'],cv:'"+B+"bx8516-uAw5qWkceccn.jpg',sp:'第二季。F班的笨蛋们继续召唤兽战争。明久的恋爱之路遥遥无期。'},",
"\n  /* ── Toei Animation ── */",
"  {cn:'Girls Band Cry',en:'GIRLS BAND CRY',y:2024,e:13,sc:8.3,fs:'Toei Animation',s:'Toei Animation',g:['音乐','剧情'],cv:'"+B+"bx164212-eKh15LQxkTEx.jpg',sp:'少女仁菜离家出走到东京。愤怒挣扎梦想。她用摇滚唱出一切。'},",
"\n  /* ── SANZIGEN ── */",
"  {cn:'BanG Dream! MyGO!!!!!',en:'BanG Dream MyGO',y:2023,e:13,sc:8.2,fs:'SANZIGEN',s:'SANZIGEN',g:['音乐','剧情'],cv:'"+B+"bx163571-Atkvuzh1A1Ip.png',sp:'五个怀着心结的少女聚在一起。不是因为友情而是因为无处可去。'},",
]

with open('index.html', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Insert before ]; line that precedes the grouping comment
for i, line in enumerate(lines):
    if line.strip() == '];':
        for entry in reversed(entries):
            lines.insert(i, entry + '\n')
        break

with open('index.html', 'w', encoding='utf-8') as f:
    f.writelines(lines)

cn = sum(1 for l in lines if "cn:'" in l)
print(f"Done. cn entries: {cn}")
