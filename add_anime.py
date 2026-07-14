# 硬编码全部番剧数据，插入HTML
import json

OUT = r"C:\Users\HP\Desktop\娱乐的东西\我的个人网站\anime\index.html"

# (cn, en, studio, group, year, eps, score, genres, cover_url, synopsis)
ALL = [
  # Sunrise - new group
  ('银魂','Gintama','Sunrise','Sunrise',2006,201,8.1,['喜剧','动作','科幻'],'https://s4.anilist.co/file/anilistcdn/media/anime/cover/large/bx918-vEB5Bk5tCXbh.jpg','江户时代末期天人入侵。坂田银时经营万事屋，与志村新八、神乐一起解决各种委托。搞笑与热血并存的日常。'),
  ("银魂'","Gintama'",'Sunrise','Sunrise',2011,51,8.5,['喜剧','动作','科幻'],'https://s4.anilist.co/file/anilistcdn/media/anime/cover/large/nx9969-5W6AG7t9zrXl.jpg','第二季。长篇篇章增多，但搞笑依然是日常。名篇连连。'),
  ('银魂°','Gintama°','Sunrise','Sunrise',2015,51,8.8,['喜剧','动作','科幻'],'https://s4.anilist.co/file/anilistcdn/media/anime/cover/large/bx28977-JXFPBhhqMdA9.jpg','第三季。将军篇、再见真选组篇——笑与泪的顶点。'),
  ('银魂。','Gintama.','Sunrise','Sunrise',2017,25,8.5,['喜剧','动作','科幻'],'https://s4.anilist.co/file/anilistcdn/media/anime/cover/large/bx34096-8tJUXe7zWB6A.jpg','第四季。银魂进入终章——最终决战即将开始。'),

  # Studio DEEN - new group
  ('学生会的一己之见','Seitokai no Ichizon','Studio DEEN','Studio DEEN',2009,12,7.3,['喜剧','校园','恋爱'],'https://s4.anilist.co/file/anilistcdn/media/anime/cover/large/bx5909-W7XJGJwftzIp.jpg','私立樱野学园学生会，全员美少女。唯一男性成员杉崎键的目标是建立后宫。一部在会议室内展开的轻松搞笑对话剧。'),
  ('学生会的一己之见 Lv.2','Seitokai no Ichizon Lv.2','Studio DEEN','Studio DEEN',2012,10,7.5,['喜剧','校园','恋爱'],'https://s4.anilist.co/file/anilistcdn/media/anime/cover/large/bx10464-A0yFoEYcluZ8.jpg','第二季。学生会一如既往地闲聊。更多的动画和游戏梗，更密集的笑点。'),

  # David Production - new group
  ('JoJo的奇妙冒险','JoJo 2012','David Production','David Production',2012,26,7.8,['动作','冒险','奇幻'],'https://s4.anilist.co/file/anilistcdn/media/anime/cover/large/nx14719-F2MDiDmbJffd.jpg','为对抗杀死Dio的父亲，乔纳森学习波纹气功。乔斯达家族百年宿命的开端。'),
  ('JoJo 星尘斗士','JoJo Stardust','David Production','David Production',2014,24,8.0,['动作','冒险','奇幻'],'https://s4.anilist.co/file/anilistcdn/media/anime/cover/large/bx20899-eLxI9VwO80Jg.jpg','第三部。承太郎觉醒替身能力，为救母亲踏上前往埃及的旅途。替身时代的开始。'),
  ('JoJo 星尘斗士 埃及篇','JoJo Egypt','David Production','David Production',2015,24,8.3,['动作','冒险','奇幻'],'https://s4.anilist.co/file/anilistcdn/media/anime/cover/large/bx26055-arHve8iKCq5u.jpg','到达埃及。与Dio的替身使者逐一决战。DIO和世界。'),
  ('JoJo 不灭钻石','JoJo Diamond','David Production','David Production',2016,39,8.4,['动作','冒险','奇幻'],'https://s4.anilist.co/file/anilistcdn/media/anime/cover/large/bx31933-kVSnfK3YxnQH.jpg','第四部。东方仗助在杜王町。吉良吉影的日常——JOJO最独特的篇章。'),
  ('JoJo 黄金之风','JoJo Golden Wind','David Production','David Production',2018,39,8.6,['动作','冒险','奇幻'],'https://s4.anilist.co/file/anilistcdn/media/anime/cover/large/bx37991-tsJbNi29dQFn.jpg','第五部。乔鲁诺加入黑帮，目标成为黑帮之星。替身战斗的巅峰。'),
  ('JoJo 石之海','JoJo Stone Ocean','David Production','David Production',2021,38,8.3,['动作','冒险','奇幻'],'https://s4.anilist.co/file/anilistcdn/media/anime/cover/large/bx48661-uohRgRQtSDRh.jpg','第六部。空条徐伦被陷害入狱。命运迎来了终局。'),

  # Trigger - new group
  ('赛博朋克 边缘行者','Edgerunners','Trigger','Trigger',2022,10,8.6,['动作','科幻','剧情'],'https://s4.anilist.co/file/anilistcdn/media/anime/cover/large/bx42310-hm3GNLTYWKru.jpg','在夜之城——充满暴力的未来都市。少年大卫成为边缘行者。没有人能活着离开夜之城。'),
  ('斩服少女','Kill la Kill','Trigger','Trigger',2013,24,8.0,['动作','喜剧','奇幻'],'https://s4.anilist.co/file/anilistcdn/media/anime/cover/large/bx18679-tylQnSWE3Gq8.jpg','缠流子转学到本能字学园寻找杀父仇人。掌权的是学生会长鬼龙院皐月。今石洋之的极致演出。'),
  ('小魔女学园','Little Witch Academia','Trigger','Trigger',2017,25,7.5,['奇幻','校园','喜剧'],'https://s4.anilist.co/file/anilistcdn/media/anime/cover/large/bx33489-EVMvCvQoDgzm.jpg','少女亚可憧憬魔女夏莉欧进入魔法学校。但连基础魔法都做不到。靠热情与不放弃的心。'),

  # Gainax - new group
  ('天元突破 红莲螺岩','Gurren Lagann','Gainax','Gainax',2007,27,8.4,['动作','科幻','冒险'],'https://s4.anilist.co/file/anilistcdn/media/anime/cover/large/nx2001-hjGzXWiy6ejx.jpg','西蒙和卡米那在地底小镇遇到少女优子。从那天起，他们的命运突破天际。钻头、羁绊、热血——这就是天元突破。'),

  # Satelight - new group
  ('战姬绝唱 Symphogear','Symphogear','Satelight','Satelight',2012,13,7.0,['动作','音乐','科幻'],'https://s4.anilist.co/file/anilistcdn/media/anime/cover/large/bx11751-eGfEHSW9Mmpu.jpg','人类面对来自Noise的威胁。立花响以歌声与Armor战斗。歌是救赎、是力量。'),
  ('战姬绝唱 Symphogear G','Symphogear G','Satelight','Satelight',2013,13,7.4,['动作','音乐','科幻'],'https://s4.anilist.co/file/anilistcdn/media/anime/cover/large/bx15793-z86TYCBwYpm3.jpg','第二季。来自Frontier的玛利亚等人登场。新的圣遗物与新的歌。'),
  ('战姬绝唱 Symphogear GX','Symphogear GX','Satelight','Satelight',2015,13,7.3,['动作','音乐','科幻'],'https://s4.anilist.co/file/anilistcdn/media/anime/cover/large/bx21573-4tLxnMvCg5st.jpg','第三季。来自传说中的菲尼登场。最黑暗也是最燃的一季。'),
  ('战姬绝唱 Symphogear AXZ','Symphogear AXZ','Satelight','Satelight',2017,13,7.5,['动作','音乐','科幻'],'https://s4.anilist.co/file/anilistcdn/media/anime/cover/large/bx32836-cjjzG70TG7UX.jpg','第四季。解除封印的远古威胁降临。响与同伴们用歌声创造奇迹。'),
  ('战姬绝唱 Symphogear XV','Symphogear XV','Satelight','Satelight',2019,13,7.8,['动作','音乐','科幻'],'https://s4.anilist.co/file/anilistcdn/media/anime/cover/large/bx32843-jWb4tBBkQ2eA.jpg','最终季。一切真相大白。战姬绝唱——响的故事迎来了终点。'),

  # A-1 Pictures (existing)
  ('路人女主的养成方法','Saenai Heroine','A-1 Pictures','A-1 Pictures',2015,13,7.5,['喜剧','恋爱','校园'],'https://s4.anilist.co/file/anilistcdn/media/anime/cover/large/bx23277-NNmYYsbFnVdn.jpg','安艺伦也在樱花坡道上遇到了理想中的女主角加藤惠。他聚集创作者们，以她为主角制作同人游戏。关于创作、理想与现实的故事。'),
  ('路人女主的养成方法 ♭','Saenai Heroine ♭','A-1 Pictures','A-1 Pictures',2017,11,7.8,['喜剧','恋爱','校园'],'https://s4.anilist.co/file/anilistcdn/media/anime/cover/large/bx30727-vnPBxBRQYnGm.jpg','第二季。社团的创作进入瓶颈，加藤惠也隐藏着不为人知的心事。'),
  ('路人女主的养成方法 Fine','Saenai Heroine Fine','A-1 Pictures','A-1 Pictures',2019,1,8.1,['喜剧','恋爱','校园'],'https://s4.anilist.co/file/anilistcdn/media/anime/cover/large/bx36885-UC1fBiQYmsnL.jpg','剧场版最终章。社团的作品终于完成——这是一部献给所有创作者的情书。'),

  # J.C.Staff (existing)
  ('绯弹的亚里亚','Aria AA','J.C.Staff','J.C.Staff',2011,12,6.7,['动作','校园','喜剧'],'https://s4.anilist.co/file/anilistcdn/media/anime/cover/large/bx10620-aq4GmD3v86CO.jpg','东京武侦高中——培养侦探与罪犯的学校。远山金次与最强武侦亚里亚搭档。速度至上的战斗物语。'),
  ('灼眼的夏娜','Shakugan no Shana','J.C.Staff','J.C.Staff',2005,24,7.2,['动作','奇幻','校园'],'https://s4.anilist.co/file/anilistcdn/media/anime/cover/large/bx355-sF9jSOInOC6v.jpg','平凡少年悠二被红世之徒袭击，拯救他的是手持太刀的少女夏娜。红世与世界战斗，以及两人间的羁绊。'),
  ('灼眼的夏娜 II','Shakugan no Shana II','J.C.Staff','J.C.Staff',2007,24,7.1,['动作','奇幻','校园'],'https://s4.anilist.co/file/anilistcdn/media/anime/cover/large/bx2787-2G3isFbZmCSh.jpg','第二季。新的敌人祭礼之蛇登场。夏娜与悠二的关系也在变化。'),
  ('灼眼的夏娜 III Final','Shakugan no Shana Final','J.C.Staff','J.C.Staff',2011,24,7.6,['动作','奇幻','校园'],'https://s4.anilist.co/file/anilistcdn/media/anime/cover/large/bx6773-hCNRXRGYWeFw.jpg','最终季。悠二做出了选择。红世、火炬、人类——所有的纠葛迎来终结。'),
  ('龙与虎','Toradora','J.C.Staff','J.C.Staff',2008,25,8.0,['喜剧','恋爱','校园'],'https://s4.anilist.co/file/anilistcdn/media/anime/cover/large/bx4224-Xj2NQFVV7iqw.jpg','慈眉善目的不良少年龙儿与掌中老虎大河。两人为了各自喜欢的人组成恋爱同盟。青春恋爱喜剧的顶点。'),

  # Kyoto Animation (existing)
  ('凉宫春日的忧郁','Suzumiya Haruhi','Kyoto Animation','Kyoto Animation',2006,14,7.8,['喜剧','校园','奇幻'],'https://s4.anilist.co/file/anilistcdn/media/anime/cover/large/bx849-vpQJc3DXeQCO.jpg','我对普通的人类没有兴趣！SOS团集结——实际上是神、外星人、未来人和超能力者的故事。'),
  ('凉宫春日的忧郁 (2009)','Suzumiya Haruhi 2009','Kyoto Animation','Kyoto Animation',2009,28,7.8,['喜剧','校园','奇幻'],'https://s4.anilist.co/file/anilistcdn/media/anime/cover/large/bx4382-DGVIMlvOce42.jpg','无尽的八月——相同的时间循环了八集，凉宫最著名的演出实验。'),
  ('凉宫春日的消失','Suzumiya Haruhi Movie','Kyoto Animation','Kyoto Animation',2010,1,8.7,['科幻','悬疑','校园'],'https://s4.anilist.co/file/anilistcdn/media/anime/cover/large/bx7311-4woxLX5SnqFt.jpg','剧场版。阿虚醒来——凉宫春日消失了，整个世界都变了。京阿尼的巅峰之作。'),
  ('中二病也要谈恋爱','Chuunibyou','Kyoto Animation','Kyoto Animation',2012,12,7.4,['喜剧','恋爱','校园'],'https://s4.anilist.co/file/anilistcdn/media/anime/cover/large/bx14741-ds2Ea2TVJBUB.jpg','前中二病少年富㭴勇太想忘记那段黑历史，却遇到了现役中二病患者小鸟游六花。'),
  ('中二病也要谈恋爱！恋','Chuunibyou Ren','Kyoto Animation','Kyoto Animation',2014,12,7.1,['喜剧','恋爱','校园'],'https://s4.anilist.co/file/anilistcdn/media/anime/cover/large/bx18671-ac0d2H6TMRT9.jpg','第二季。七宫智音登场。现役中二病、前中二病和隐藏中二病聚在一起——混乱加倍。'),

  # Madhouse (existing)
  ('魔卡少女樱','Cardcaptor Sakura','Madhouse','Madhouse',1998,70,7.9,['奇幻','喜剧','校园'],'https://s4.anilist.co/file/anilistcdn/media/anime/cover/large/bx232-2wq16a9snv4E.jpg','小学四年生木之本樱在家中书房发现魔法书。封印兽小可出现委托她收集散落的库洛牌。'),
  ('魔卡少女樱 透明牌篇','CC Clear Card','Madhouse','Madhouse',2018,22,7.6,['奇幻','喜剧','校园'],'https://s4.anilist.co/file/anilistcdn/media/anime/cover/large/bx33354-kHFYvn0LPCnx.jpg','续作。小樱升入中学，库洛牌再次发生变化。透明牌的谜团与新的邂逅。'),
]

# Separate by group
new_groups = {'Sunrise':[],'Studio DEEN':[],'David Production':[],'Trigger':[],'Gainax':[],'Satelight':[]}
existing = {'A-1 Pictures':[],'J.C.Staff':[],'Kyoto Animation':[],'Madhouse':[]}

for (cn, en, studio, group, year, eps, score, genres, cv, sp) in ALL:
    gs = f"fs:'{group}',s:'{studio}'"
    line = f"  {{cn:'{cn}',en:'{en}',y:{year},e:{eps},sc:{score},{gs},g:{json.dumps(genres,ensure_ascii=False)},cv:'{cv}',sp:'{sp}'}},"

    if group in new_groups:
        new_groups[group].append(line)
    elif group in existing:
        existing[group].append(line)

with open(OUT, 'r', encoding='utf-8') as f:
    html = f.read()

# 1. Update studio order
html = html.replace("'Gonzo','AIC PLUS+','Madhouse','White Fox','A-1 Pictures','Doga Kobo','P.A. Works'",
                     "'Gonzo','Sunrise','Studio DEEN','David Production','Trigger','Gainax','Satelight','AIC PLUS+','Madhouse','White Fox','A-1 Pictures','Doga Kobo','P.A. Works'")

# 2. Insert new groups before DB array closing
marker = "];\n\n\n  /* ══════════ 按 firstStudio 分组"
pos = html.find(marker)
if pos > 0:
    new_text = ""
    for g, entries in new_groups.items():
        if entries:
            new_text += "\n\n  /* ── %s ── */\n" % g
            new_text += "\n".join(entries)
    if new_text:
        html = html[:pos] + new_text + html[pos:]

# 3. Insert into existing groups
for group, entries in existing.items():
    if not entries: continue
    gmarker = "/* ── %s ── */" % group
    pos = html.find(gmarker)
    if pos < 0: continue
    seg = html[pos:]
    # Find end of group - next comment or array close
    end = seg.find("\n\n  /* ── ", 30)
    if end < 0: end = seg.find("\n];")
    if end < 0: continue
    last_entry = seg.rfind("\n", 0, end)
    insert_at = pos + last_entry
    html = html[:insert_at] + "\n" + "\n".join(entries) + html[insert_at:]

with open(OUT, 'w', encoding='utf-8') as f:
    f.write(html)

total = len(ALL)
print(f"Done! {total} entries inserted into HTML")
print("New groups: Sunrise, Studio DEEN, David Production, Trigger, Gainax, Satelight")
print("Existing groups: A-1=%d, JCStaff=%d, KyoAni=%d, Madhouse=%d" % (
    len(existing['A-1 Pictures']), len(existing['J.C.Staff']),
    len(existing['Kyoto Animation']), len(existing['Madhouse'])))
