path = r"C:\Users\HP\Desktop\娱乐的东西\我的个人网站\anime\index.html"
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

# Update studio order
old_order = "['Kyoto Animation','Bones','Gonzo','AIC PLUS+','Madhouse','White Fox','A-1 Pictures','P.A. Works']"
new_order = "['Kyoto Animation','J.C.Staff','Bones','8-bit','Shaft','Gonzo','AIC PLUS+','Madhouse','White Fox','A-1 Pictures','Doga Kobo','P.A. Works']"
content = content.replace(old_order, new_order)

lines = content.split('\n')
out = []

def E(entry_text):
    """Simple wrapper to pass through entry text"""
    return entry_text

for i, line in enumerate(lines):
    out.append(line)

    # after 紫罗兰永恒花园
    if "Violet Evergarden" in line and "cn:" in line:
        out.append("  {cn:'甘城光辉游乐园',en:'Amagi Brilliant Park',y:2014,e:13,sc:7.2,fs:'Kyoto Animation',s:'Kyoto Animation',g:['喜剧','奇幻'],cv:'https://s4.anilist.co/file/anilistcdn/media/anime/cover/large/bx20602-f6CfipBF44kV.png',sp:'可儿江西也被神秘转学生千斗五十铃带到甘城光辉游乐园。公主委托他担任新经理，在三个月内吸引25万游客。而公园的演员们，全都是真正的魔法生物。'},")
        out.append("  {cn:'幸运星',en:'Lucky Star',y:2007,e:24,sc:7.5,fs:'Kyoto Animation',s:'Kyoto Animation',g:['喜剧','日常'],cv:'https://s4.anilist.co/file/anilistcdn/media/anime/cover/large/bx1887-P36Pucd4qKji.png',sp:'泉此方——热爱动漫和游戏的御宅族高中生。她和双胞胎姐妹柊镜、柊司，以及天然呆的高良美幸一起，度过普通却充满乐趣的每一天。日常系动画的鼻祖之作。'},")

    # before A-1 Pictures
    if "7. A-1 Pictures" in line:
        out.append("  {cn:'我们仍未知道那天所看见的花的名字',en:'AnoHana',y:2011,e:11,sc:8.0,fs:'A-1 Pictures',s:'A-1 Pictures',g:['剧情','恋爱','日常','超自然'],cv:'https://s4.anilist.co/file/anilistcdn/media/anime/cover/large/bx9989-hImMg6kCMm6I.jpg',sp:'仁太在某个夏天遇到了已故童年玩伴面码的幽灵。面码有个未实现的愿望。于是超和平Busters的六人再次聚在一起。'},")

    # after Angel Beats
    if "Angel Beats" in line and "cn:" in line:
        out.append("  {cn:'白箱',en:'Shirobako',y:2014,e:24,sc:8.1,fs:'P.A. Works',s:'P.A. Works',g:['喜剧','剧情','日常'],cv:'https://s4.anilist.co/file/anilistcdn/media/anime/cover/large/bx20812-KvIP1yffJEPZ.jpg',sp:'宫森葵和她的四个高中同学一起进入了动画行业。有人成为原画师，有人成为3D监督，有人追逐声优的梦想。白箱是她们的青春与梦想的见证。'},")

    # before "按 firstStudio 分组" -> new groups
    if "按 firstStudio 分组" in line:
        out.pop()
        new_entries = [
            "",
            "  /* ── J.C.Staff ── */",
            "  {cn:'魔法禁书目录',en:'Toaru Majutsu no Index',y:2008,e:24,sc:7.0,fs:'J.C.Staff',s:'J.C.Staff',g:['动作','科幻','超自然'],cv:'https://s4.anilist.co/file/anilistcdn/media/anime/cover/large/bx4654-ba44icsxDQZd.jpg',sp:'学园都市，住着230万人口的超能力城市。上条当麻拥有消除一切超能力的右手幻想杀手。他遇到了从魔法侧逃来的茵蒂克丝。'},",
            "  {cn:'魔法禁书目录 II',en:'Toaru Majutsu no Index II',y:2010,e:24,sc:7.3,fs:'J.C.Staff',s:'J.C.Staff',g:['动作','科幻','超自然'],cv:'https://s4.anilist.co/file/anilistcdn/media/anime/cover/large/bx8937-i3AW4QZxQHMy.jpg',sp:'当麻的日常继续被卷入更大的事件。罗马正教的阴谋、学园都市的暗部。'},",
            "  {cn:'魔法禁书目录 III',en:'Toaru Majutsu no Index III',y:2018,e:26,sc:6.6,fs:'J.C.Staff',s:'J.C.Staff',g:['动作','科幻','超自然'],cv:'https://s4.anilist.co/file/anilistcdn/media/anime/cover/large/bx100185-mZquZyZ8QbSS.jpg',sp:'第三次世界大战篇。当麻必须面对最艰难的选择。'},",
            "  {cn:'零之使魔',en:'Zero no Tsukaima',y:2006,e:13,sc:6.8,fs:'J.C.Staff',s:'J.C.Staff',g:['动作','冒险','喜剧','奇幻'],cv:'https://s4.anilist.co/file/anilistcdn/media/anime/cover/large/bx1195-odpKgDQ7A1fV.png',sp:'普通高中生平贺才人被召唤到异世界，成为魔法学院学生露易丝的使魔。露易丝是全校成绩最差的魔法师。'},",
            "  {cn:'零之使魔 双月的骑士',en:'Zero no Tsukaima S2',y:2007,e:12,sc:7.0,fs:'J.C.Staff',s:'J.C.Staff',g:['动作','冒险','喜剧','奇幻'],cv:'https://s4.anilist.co/file/anilistcdn/media/anime/cover/large/bx1840-AYZXdXUCpqpR.jpg',sp:'才人继续着异世界生活。新的威胁出现，两人之间的羁绊在战火中经受考验。'},",
            "  {cn:'零之使魔 三美姬的轮舞',en:'Zero no Tsukaima S3',y:2008,e:12,sc:6.9,fs:'J.C.Staff',s:'J.C.Staff',g:['动作','冒险','喜剧','奇幻'],cv:'https://s4.anilist.co/file/anilistcdn/media/anime/cover/large/bx3712-zt0ac4fjixWl.jpg',sp:'才人和露易丝面对的不只是外敌，还有内心的纠葛。'},",
            "  {cn:'零之使魔 F',en:'Zero no Tsukaima F',y:2012,e:12,sc:7.0,fs:'J.C.Staff',s:'J.C.Staff',g:['动作','冒险','喜剧','奇幻'],cv:'https://s4.anilist.co/file/anilistcdn/media/anime/cover/large/bx11319-6PwRxZiVChQo.jpg',sp:'最终季。才人和露易丝迎来了故事的终点。'},",
            "  {cn:'Little Busters!',en:'Little Busters!',y:2012,e:26,sc:7.2,fs:'J.C.Staff',s:'J.C.Staff',g:['剧情','校园','恋爱','奇幻'],cv:'https://s4.anilist.co/file/anilistcdn/media/anime/cover/large/nx13655-ZdAJjba0HrY6.jpg',sp:'失去双亲的理树，被恭介、铃、真人、谦吾带入名为Little Busters的小团体。然而这个世界的本质，远比表面复杂。'},",
            "  {cn:'Little Busters! Refrain',en:'Little Busters! Refrain',y:2013,e:13,sc:8.0,fs:'J.C.Staff',s:'J.C.Staff',g:['剧情','恋爱','奇幻'],cv:'https://s4.anilist.co/file/anilistcdn/media/anime/cover/large/bx18195-r62KJesiZQWb.png',sp:'世界的真相揭开。这是关于友情、告别与成长的终极篇章。'},",
            "",
            "  /* ── 8-bit ── */",
            "  {cn:'Rewrite',en:'Rewrite',y:2016,e:13,sc:6.2,fs:'8-bit',s:'8-bit',g:['剧情','神秘','恋爱'],cv:'https://s4.anilist.co/file/anilistcdn/media/anime/cover/large/bx21382-bBJghvjTP8Dr.jpg',sp:'天王寺瑚太朗生活在风祭市，总觉得有什么不对劲。Key社作品，关于改写命运的故事。'},",
            "  {cn:'Rewrite 2nd Season',en:'Rewrite 2nd Season',y:2017,e:11,sc:6.8,fs:'8-bit',s:'8-bit',g:['剧情','神秘','奇幻'],cv:'https://s4.anilist.co/file/anilistcdn/media/anime/cover/large/bx97665-QkYpSTjEaz57.jpg',sp:'Moon篇与Terra篇。瑚太朗逐渐接近世界的真相。'},",
            "",
            "  /* ── Shaft ── */",
            "  {cn:'魔法少女小圆',en:'Mahou Shoujo Madoka Magica',y:2011,e:12,sc:8.3,fs:'Shaft',s:'Shaft',g:['剧情','奇幻','魔法少女'],cv:'https://s4.anilist.co/file/anilistcdn/media/anime/cover/large/bx9756-QnUGwlwwnsuN.jpg',sp:'鹿目圆是普通的中学二年级学生。丘比说只要签订契约就能实现任何愿望。当真相揭开——魔法少女的命运远非童话。'},",
            "",
            "  /* ── Doga Kobo ── */",
            "  {cn:'可塑性记忆',en:'Plastic Memories',y:2015,e:13,sc:7.7,fs:'Doga Kobo',s:'Doga Kobo',g:['剧情','恋爱','科幻'],cv:'https://s4.anilist.co/file/anilistcdn/media/anime/cover/large/bx20872-j5PBzzVtrYDM.jpg',sp:'在未来，拥有感情的人形机器人Giftia普及。但它们只有约九年的寿命。水柿司与Giftia少女艾拉组成搭档。在一次次告别中，两人的感情悄然萌生。'},",
            "",
            line,
        ]
        out.extend(new_entries)

final = '\n'.join(out)
with open(path, 'w', encoding='utf-8') as f:
    f.write(final)

total = final.count("cn:'") + final.count('cn:"')
print(f"Done. Total {total} anime entries.")
