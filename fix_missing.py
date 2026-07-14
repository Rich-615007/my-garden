import json

OUT = r"C:\Users\HP\Desktop\娱乐的东西\我的个人网站\anime\index.html"

with open(OUT, 'r', encoding='utf-8') as f:
    html = f.read()

# New entries to add - organized by where they go
NEW_GROUPS_START = """\n
  /* ── Sunrise ── */
  {cn:'银魂',en:'Gintama',y:2006,e:201,sc:8.1,fs:'Sunrise',s:'Sunrise',g:['喜剧','动作','科幻'],cv:'https://s4.anilist.co/file/anilistcdn/media/anime/cover/large/bx918-vEB5Bk5tCXbh.jpg',sp:'江户时代末期天人入侵。坂田银时经营万事屋，与志村新八、神乐一起解决各种委托。'},
  {cn:"银魂'",en:"Gintama'",y:2011,e:51,sc:8.5,fs:'Sunrise',s:'Sunrise',g:['喜剧','动作','科幻'],cv:'https://s4.anilist.co/file/anilistcdn/media/anime/cover/large/nx9969-5W6AG7t9zrXl.jpg',sp:'第二季。长篇篇章增多，但搞笑依然是日常。'},
  {cn:'银魂°',en:'Gintama°',y:2015,e:51,sc:8.8,fs:'Sunrise',s:'Sunrise',g:['喜剧','动作','科幻'],cv:'https://s4.anilist.co/file/anilistcdn/media/anime/cover/large/bx28977-JXFPBhhqMdA9.jpg',sp:'第三季。将军篇、再见真选组篇。'},
  {cn:'银魂。',en:'Gintama.',y:2017,e:25,sc:8.5,fs:'Sunrise',s:'Sunrise',g:['喜剧','动作','科幻'],cv:'https://s4.anilist.co/file/anilistcdn/media/anime/cover/large/bx34096-8tJUXe7zWB6A.jpg',sp:'第四季。银魂进入终章。'},

  /* ── Studio DEEN ── */
  {cn:'学生会的一己之见',en:'Seitokai no Ichizon',y:2009,e:12,sc:7.3,fs:'Studio DEEN',s:'Studio DEEN',g:['喜剧','校园','恋爱'],cv:'https://s4.anilist.co/file/anilistcdn/media/anime/cover/large/bx5909-W7XJGJwftzIp.jpg',sp:'私立樱野学园学生会。唯一男性成员杉崎键的目标是建立后宫。轻松搞笑的对话剧。'},
  {cn:'学生会的一己之见 Lv.2',en:'Seitokai no Ichizon Lv.2',y:2012,e:10,sc:7.5,fs:'Studio DEEN',s:'Studio DEEN',g:['喜剧','校园','恋爱'],cv:'https://s4.anilist.co/file/anilistcdn/media/anime/cover/large/bx10464-A0yFoEYcluZ8.jpg',sp:'第二季。一如既往地闲聊。更多动画梗，更密集的笑点。'},

  /* ── David Production ── */
  {cn:'JoJo的奇妙冒险',en:'JoJo 2012',y:2012,e:26,sc:7.8,fs:'David Production',s:'David Production',g:['动作','冒险','奇幻'],cv:'https://s4.anilist.co/file/anilistcdn/media/anime/cover/large/nx14719-F2MDiDmbJffd.jpg',sp:'乔纳森为对抗Dio学习波纹气功。乔斯达家族百年宿命的开端。'},
  {cn:'JoJo 星尘斗士',en:'JoJo Stardust',y:2014,e:24,sc:8.0,fs:'David Production',s:'David Production',g:['动作','冒险','奇幻'],cv:'https://s4.anilist.co/file/anilistcdn/media/anime/cover/large/bx20899-eLxI9VwO80Jg.jpg',sp:'承太郎觉醒替身能力，踏上前往埃及的旅途。'},
  {cn:'JoJo 星尘斗士 埃及篇',en:'JoJo Egypt',y:2015,e:24,sc:8.3,fs:'David Production',s:'David Production',g:['动作','冒险','奇幻'],cv:'https://s4.anilist.co/file/anilistcdn/media/anime/cover/large/bx26055-arHve8iKCq5u.jpg',sp:'到达埃及。与Dio的替身使者逐一决战。'},
  {cn:'JoJo 不灭钻石',en:'JoJo Diamond',y:2016,e:39,sc:8.4,fs:'David Production',s:'David Production',g:['动作','冒险','奇幻'],cv:'https://s4.anilist.co/file/anilistcdn/media/anime/cover/large/bx31933-kVSnfK3YxnQH.jpg',sp:'东方仗助在杜王町。吉良吉影的日常。'},
  {cn:'JoJo 黄金之风',en:'JoJo Golden Wind',y:2018,e:39,sc:8.6,fs:'David Production',s:'David Production',g:['动作','冒险','奇幻'],cv:'https://s4.anilist.co/file/anilistcdn/media/anime/cover/large/bx37991-tsJbNi29dQFn.jpg',sp:'乔鲁诺加入黑帮，目标成为黑帮之星。'},
  {cn:'JoJo 石之海',en:'JoJo Stone Ocean',y:2021,e:38,sc:8.3,fs:'David Production',s:'David Production',g:['动作','冒险','奇幻'],cv:'https://s4.anilist.co/file/anilistcdn/media/anime/cover/large/bx48661-uohRgRQtSDRh.jpg',sp:'空条徐伦被陷害入狱。命运迎来终局。'},

  /* ── Trigger ── */
  {cn:'赛博朋克 边缘行者',en:'Edgerunners',y:2022,e:10,sc:8.6,fs:'Trigger',s:'Trigger',g:['动作','科幻','剧情'],cv:'https://s4.anilist.co/file/anilistcdn/media/anime/cover/large/bx42310-hm3GNLTYWKru.jpg',sp:'在夜之城——充满暴力的未来都市。少年大卫成为边缘行者。'},
  {cn:'斩服少女',en:'Kill la Kill',y:2013,e:24,sc:8.0,fs:'Trigger',s:'Trigger',g:['动作','喜剧','奇幻'],cv:'https://s4.anilist.co/file/anilistcdn/media/anime/cover/large/bx18679-tylQnSWE3Gq8.jpg',sp:'缠流子转学到本能字学园寻找杀父仇人。'},
  {cn:'小魔女学园',en:'Little Witch Academia',y:2017,e:25,sc:7.5,fs:'Trigger',s:'Trigger',g:['奇幻','校园','喜剧'],cv:'https://s4.anilist.co/file/anilistcdn/media/anime/cover/large/bx33489-EVMvCvQoDgzm.jpg',sp:'少女亚可憧憬魔女进入魔法学校。靠热情与不放弃的心。'},

  /* ── Gainax ── */
  {cn:'天元突破 红莲螺岩',en:'Gurren Lagann',y:2007,e:27,sc:8.4,fs:'Gainax',s:'Gainax',g:['动作','科幻','冒险'],cv:'https://s4.anilist.co/file/anilistcdn/media/anime/cover/large/nx2001-hjGzXWiy6ejx.jpg',sp:'西蒙和卡米那在地底小镇遇到少女优子。他们的命运突破天际。'},

  /* ── Satelight ── */
  {cn:'战姬绝唱 Symphogear',en:'Symphogear',y:2012,e:13,sc:7.0,fs:'Satelight',s:'Satelight',g:['动作','音乐','科幻'],cv:'https://s4.anilist.co/file/anilistcdn/media/anime/cover/large/bx11751-eGfEHSW9Mmpu.jpg',sp:'人类面对Noise的威胁。立花响以歌声与Armor战斗。'},
  {cn:'战姬绝唱 Symphogear G',en:'Symphogear G',y:2013,e:13,sc:7.4,fs:'Satelight',s:'Satelight',g:['动作','音乐','科幻'],cv:'https://s4.anilist.co/file/anilistcdn/media/anime/cover/large/bx15793-z86TYCBwYpm3.jpg',sp:'第二季。玛利亚等人登场。'},
  {cn:'战姬绝唱 Symphogear GX',en:'Symphogear GX',y:2015,e:13,sc:7.3,fs:'Satelight',s:'Satelight',g:['动作','音乐','科幻'],cv:'https://s4.anilist.co/file/anilistcdn/media/anime/cover/large/bx21573-4tLxnMvCg5st.jpg',sp:'第三季。菲尼登场。最黑暗也最燃的一季。'},
  {cn:'战姬绝唱 Symphogear AXZ',en:'Symphogear AXZ',y:2017,e:13,sc:7.5,fs:'Satelight',s:'Satelight',g:['动作','音乐','科幻'],cv:'https://s4.anilist.co/file/anilistcdn/media/anime/cover/large/bx32836-cjjzG70TG7UX.jpg',sp:'第四季。远古威胁降临。'},
  {cn:'战姬绝唱 Symphogear XV',en:'Symphogear XV',y:2019,e:13,sc:7.8,fs:'Satelight',s:'Satelight',g:['动作','音乐','科幻'],cv:'https://s4.anilist.co/file/anilistcdn/media/anime/cover/large/bx32843-jWb4tBBkQ2eA.jpg',sp:'最终季。一切真相大白。'},

  /* ── A-1 Pictures (追加) ── */
  {cn:'路人女主的养成方法',en:'Saenai Heroine',y:2015,e:13,sc:7.5,fs:'A-1 Pictures',s:'A-1 Pictures',g:['喜剧','恋爱','校园'],cv:'https://s4.anilist.co/file/anilistcdn/media/anime/cover/large/bx23277-NNmYYsbFnVdn.jpg',sp:'安艺伦也遇到理想的加藤惠。她为主角制作同人游戏。关于创作与理想的故事。'},
  {cn:'路人女主的养成方法 ♭',en:'Saenai Heroine ♭',y:2017,e:11,sc:7.8,fs:'A-1 Pictures',s:'A-1 Pictures',g:['喜剧','恋爱','校园'],cv:'https://s4.anilist.co/file/anilistcdn/media/anime/cover/large/bx30727-vnPBxBRQYnGm.jpg',sp:'第二季。创作进入瓶颈，惠也隐藏着不为人知的心事。'},
  {cn:'路人女主的养成方法 Fine',en:'Saenai Heroine Fine',y:2019,e:1,sc:8.1,fs:'A-1 Pictures',s:'A-1 Pictures',g:['喜剧','恋爱','校园'],cv:'https://s4.anilist.co/file/anilistcdn/media/anime/cover/large/bx36885-UC1fBiQYmsnL.jpg',sp:'剧场版最终章。献给所有创作者的情书。'},

  /* ── Kyoto Animation (追加) ── */
  {cn:'凉宫春日的忧郁',en:'Suzumiya Haruhi',y:2006,e:14,sc:7.8,fs:'Kyoto Animation',s:'Kyoto Animation',g:['喜剧','校园','奇幻'],cv:'https://s4.anilist.co/file/anilistcdn/media/anime/cover/large/bx849-vpQJc3DXeQCO.jpg',sp:'我对普通的人类没有兴趣！SOS团集结——神、外星人、未来人和超能力者的故事。'},
  {cn:'凉宫春日的忧郁 (2009)',en:'Suzumiya Haruhi 2009',y:2009,e:28,sc:7.8,fs:'Kyoto Animation',s:'Kyoto Animation',g:['喜剧','校园','奇幻'],cv:'https://s4.anilist.co/file/anilistcdn/media/anime/cover/large/bx4382-DGVIMlvOce42.jpg',sp:'无尽的八月——相同的时间循环了八集。'},
  {cn:'凉宫春日的消失',en:'Suzumiya Haruhi Movie',y:2010,e:1,sc:8.7,fs:'Kyoto Animation',s:'Kyoto Animation',g:['科幻','悬疑','校园'],cv:'https://s4.anilist.co/file/anilistcdn/media/anime/cover/large/bx7311-4woxLX5SnqFt.jpg',sp:'剧场版。阿虚醒来——凉宫消失，整个世界都变了。京阿尼巅峰之作。'},
  {cn:'中二病也要谈恋爱',en:'Chuunibyou',y:2012,e:12,sc:7.4,fs:'Kyoto Animation',s:'Kyoto Animation',g:['喜剧','恋爱','校园'],cv:'https://s4.anilist.co/file/anilistcdn/media/anime/cover/large/bx14741-ds2Ea2TVJBUB.jpg',sp:'前中二病少年遇到现役中二病患者小鸟游六花。'},
  {cn:'中二病也要谈恋爱！恋',en:'Chuunibyou Ren',y:2014,e:12,sc:7.1,fs:'Kyoto Animation',s:'Kyoto Animation',g:['喜剧','恋爱','校园'],cv:'https://s4.anilist.co/file/anilistcdn/media/anime/cover/large/bx18671-ac0d2H6TMRT9.jpg',sp:'第二季。七宫智音登场。混乱加倍。'},

  /* ── Madhouse (追加) ── */
  {cn:'魔卡少女樱',en:'Cardcaptor Sakura',y:1998,e:70,sc:7.9,fs:'Madhouse',s:'Madhouse',g:['奇幻','喜剧','校园'],cv:'https://s4.anilist.co/file/anilistcdn/media/anime/cover/large/bx232-2wq16a9snv4E.jpg',sp:'小学女生木之本樱在家中发现魔法书。小可委托她收集散落的库洛牌。'},
  {cn:'魔卡少女樱 透明牌篇',en:'CC Clear Card',y:2018,e:22,sc:7.6,fs:'Madhouse',s:'Madhouse',g:['奇幻','喜剧','校园'],cv:'https://s4.anilist.co/file/anilistcdn/media/anime/cover/large/bx33354-kHFYvn0LPCnx.jpg',sp:'续作。小樱升入中学，库洛牌再次变化。'},
"""

# Find the ]; that closes DB array, and insert new groups there
# The DB array closes with "];" followed by "\n\n/* ══════════ 按 firstStudio"
closing = html.find("];\n\n/* ══════════ 按 firstStudio 分组")
if closing > 0:
    html = html[:closing] + NEW_GROUPS_START + "\n" + html[closing:]
    print("New groups inserted before array closing")
else:
    print("ERROR: Could not find array closing marker!")

with open(OUT, 'w', encoding='utf-8') as f:
    f.write(html)

total = html.count("cn:'") + html.count('cn:"')
print(f"Total entries in file: {total}")
