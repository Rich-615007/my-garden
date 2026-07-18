#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════════╗
║  揉碎星辰 · 个人花园 — 项目记忆文件 (四版合并最终版)     ║
║  目标: 新对话阅读本文件后可以无缝继续所有工作              ║
║  生成: 2026-07-16  |  来源: cr_v1+v2+v3+v4 合并           ║
╚══════════════════════════════════════════════════════════════╝
"""

# ═══════════════════ 第一章: 项目概览 ═══════════════════
print("""
项目名称: 揉碎星辰 · 个人花园
定位: 动漫/漫画/轻小说/音乐/游戏/创作的个人收藏展示网站
托管: GitHub Pages → https://rich-615007.github.io/my-garden/
仓库: https://github.com/Rich-615007/my-garden
本地: C:\\Users\\HP\\Desktop\\娱乐的东西\\我的个人网站
用户: Rich-615007  昵称: 揉碎星辰
代理: HTTP_PROXY=http://127.0.0.1:7897 (端口7897)
环境: Git + Python3 + curl

=== 设计主题 ===
全站花田黄昏背景 (CLANNAD AS花田): 天空渐变/三层山丘/野花/暖色半透明卡片
主页特殊: 深色Hero Banner + 海报墙浮动 + 导航卡片
导航栏: 纯文字无emoji → 追番 漫画 游戏 轻小说 音乐 创作 关于(7个)
右下角: 聊天向导(guide-widget) — 3角色(渚/奏/忍) — 关键词回复+闲话+导览
""")

# ═══════════════════ 第二章: 文件结构 ═══════════════════
print("""
个人网站/
├── index.html              # 主页(深色Hero+海报墙)
├── style.css               # 共享样式(花田背景/导航)
├── 工具链/
│   ├── 追番_add_anime_tool.py    # 追番: MAL ID→AniList→制作社
│   ├── 轻小说_add_ln_tool.py     # 轻小说: MAL ID→AniList→出版社
│   ├── 漫画_manga-tool.py        # 漫画: MAL ID→AniList→连载杂志
│   ├── 音乐_add_music_tool.py    # 音乐: 网易云ID→网易云API→作品来源
│   ├── 游戏_game-tool.py         # 游戏: 手动→制作公司
│   ├── 向导_guide-tool.py        # 聊天向导验证
│   └── 注意事项汇总/cr_master.py # ←本文件
├── js/
│   ├── guide-characters.js       # 聊天向导: 3角色台词+关键词回复
│   ├── guide-widget.js           # 聊天向导: 窗口/消息/快捷跳转/localStorage
│   ├── desk-pet.js               # (已废弃)
│   └── desk-pet-voices.js        # (已废弃)
├── anime/index.html              # 追番 145部 18社
├── manga/index.html              # 漫画 19部 8杂志
├── game/index.html               # 游戏 5款 3社(DLC折叠)
├── lightnovel/index.html         # 轻小说 14部 4出版社
├── music/index.html              # 音乐 6首 2来源(网易云播放器)
├── create/index.html             # 创作(心穴游戏)
├── about/index.html              # 关于我
└── images/                       # 图片
""")

# ═══════════════════ 第三章: 分区设计 ═══════════════════
print("""
=== 分类依据 ===
追番:    制作社(studio/fs)    ← AniList studios.nodes
轻小说:  出版社(publisher/pub) ← 手动输入
漫画:    连载杂志(magazine/mag)← 手动输入
音乐:    作品来源(source)     ← "CLANNAD"或"独立:歌手"
游戏:    制作公司(dev)        ← 手动维护

=== 通用页面结构 ===
花田背景 → 导航栏(7链接) → 分区标题 → 可折叠分组标题 → 3列网格卡片 → 点击弹窗
弹窗: 大封面 + 信息行(年份/评分/分类) + 简介 + 特定扩展(音乐播放器/DLC列表)
750px响应式 → 1列; 折叠状态 localStorage记忆
每页末尾: guide-characters.js + guide-widget.js (主页用js/,子页用../js/)

=== 数据结构速查 ===
追番:  cn,en,y,e,sc,fs,s,ch?,g,cv,sp   (e=集数,fs=首社,s=实社,ch=换社)
漫画:  id,cn,en,mag,y,v,c,sc,author,artist,st,g,cv,sp  (v=卷,c=章,st=状态)
轻小说:cn,en,y,v,sc,pub,author,g,cv,sp  (v=卷数)
音乐:  id,cn,source,album,artist,lyricist,composer,arranger,y,tn,dr,sc,cv,ncm,sp
        (source=来源,tn=曲序,dr=时长秒,ncm=网易云ID)
游戏:  id,cn,en,dev,pub,y,pf,sc,g,cv,sp,dlc?  (pf=平台,dlc=[{cn,y,pf,sc,sp}])
""")

# ═══════════════════ 第四章: 数据源 ═══════════════════
print("""
=== AniList API (追番/轻小说/漫画) ===
POST https://graphql.anilist.co  Content-Type:application/json
免费 无需Key 限流~1次/秒 sleep 3-4秒
封面CDN: s4.anilist.co → 用medium/尺寸(非large/,会404)
查询: query{Media(idMal:ID,type:ANIME/MANGA){...}}

=== 网易云API (音乐) ===
GET https://music.163.com/api/song/detail?ids=[ID]
需Referer头: https://music.163.com
Album key是"album"(非"al"), artists key是"artists"(非"ar")
copyright检查: fee=0免费可播/fee=1VIP不可播/fee=8付费
播放器外链: https://music.163.com/outchain/player?type=2&id=NID&auto=0&height=90

=== Steam封面CDN (游戏) ===
https://steamcdn-a.akamaihd.net/steam/apps/{AppID}/header.jpg
核验可用: 1245620(法环)/582010(MH世界)/1446780(MH崛起)/2246340(MH荒野)

=== MAL ID获取 ===
WebFetch myanimelist.net搜索 → 绝不凭记忆猜ID
""")

# ═══════════════════ 第五章: 验证体系 ═══════════════════
print("""
=== V1-V6 验证 ===
V1 1:1: cn数 == 唯特封面文件名 → FAIL不提交
V2 HTTP: curl验证封面200 → WARN不阻断(无代理误报)
V3 语法: 单引号内未转义引号 → FAIL
V4 结构: DB/分组数组各1次, 大括号平衡 → FAIL
V5 特定: 音乐ncmId/漫画format/向导3角色台词
V6 forEach一致性: sourceOrder.forEach(src=>) 后无 groups[a]残留

阻断: V1/V3/V4/V5/V6 FAIL→回退; V2 FAIL→仅警告
所有工具链支持 --check 模式
""")

# ═══════════════════ 第六章: SOP ═══════════════════
print("""
=== 添加内容标准流程 ===
0.备份 1.搜MAL ID 2.sleep 4s→API拉数据 3.curl验封面
4.交互输入/批量模式 5.生成JS条目 6.Python定位插入
7.同步分组数组 8.--check验证 9.PASS→commit+push 10.FAIL→回退
11.(重要修改)启动审查subagent

=== 工具链用法 ===
单部: python3 工具链/追番_add_anime_tool.py 41457
验证: python3 工具链/追番_add_anime_tool.py --check
批量: python3 工具链/追番_add_anime_tool.py --batch ids.txt

=== 新环境设置 ===
1.git clone 2.export HTTP_PROXY=http://127.0.0.1:7897
3.python3 工具链/向导_guide-tool.py --check
""")

# ═══════════════════ 第七章: 工具链对比 ═══════════════════
print("""
=== 6个工具链对照 ===
        追番      轻小说     漫画       音乐       游戏       向导
API     AniList   AniList    AniList    网易云      手动        N/A
Type    ANIME     MANGA      MANGA      song/detail N/A         N/A
分组    制作社    出版社     连载杂志   作品来源    制作公司    N/A
数组    studioOrder pubOrder magOrder  sourceOrder devOrder    N/A
卡片    年/集/社  年/卷/作者 年/卷/作者 专辑/词/曲  年/平台/社  N/A
特殊    ch(换社)  pub手输    mag手输    ncmId/tn/dr pf/dlc      3角色
""")

# ═══════════════════ 第八章: 所有错误 ═══════════════════
print("""
=== 13个关键错误 (防重犯) ===
1.封面URL猜→API实测 / 2.sed全局替换→Python逐条 / 3.插入到];外→定位边界
4.单引号注入→escape_js_string / 5.API key写错→dump raw JSON
6.groups[a]残留→V6检查 / 7.mid泄露→附元组 / 8.description未查→统一模板
9.注释正则不匹配→clean_group_name / 10.Push Protection→localStorage
11.导航缺链接→grep全检 / 12.Steam CDN→akamaihd / 13.AI接入→放弃
""")

# ═══════════════════ 第九章: 禁止事项 ═══════════════════
print("""
=== 14条禁止 ===
不用sed / 不猜ID/URL / 不拼未转义输入 / 不跳过验证 / 不写死API Key
不用行号插入 / 不跳过导航检查 / 不跳过审查 / 不用AniList large/
不接入免费AI / 不amend / 不force push(除非清Key)
不在无代理时跑V2 / 不混用r-string和三引号
""")

# ═══════════════════ 第十章: Git/网络/编码 ═══════════════════
print("""
=== Git ===
commit格式: "加番: xxx" "修复: xxx" "新增: xxx"
push时机: 每次小任务完成后立即push
force push: 仅清密钥泄露

=== 网络 ===
代理端口7897 / V2无代理会误报 / 浏览器Ctrl+Shift+R强刷 / Pages 30s延迟

=== 编码 ===
UTF-8无BOM / LF换行 / open(file,'r',encoding='utf-8')
""")

# ═══════════════════ 第十一章: 快捷命令 ═══════════════════
print("""
=== 常用命令 ===
# 全站自检
for t in 追番_add_anime_tool 漫画_manga-tool 音乐_add_music_tool 向导_guide-tool 游戏_game-tool; do
  python3 "工具链/${t}.py" --check; done

# 统计条目
grep -c "cn:'" path/index.html

# 检查导航栏
for f in anime manga game lightnovel music create about; do
  grep -c 'href="../music/"' "$f/index.html"; done

# 加番最短路径
python3 工具链/追番_add_anime_tool.py MAL_ID
""")
