/* ══════ 聊天向导 · 角色定义 ══════ */
const GUIDE_CHARS = {
  "古河渚": {
    from: "CLANNAD",
    avatar: "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 40 40'%3E%3Ccircle cx='20' cy='18' r='16' fill='%23FADBD8'/%3E%3Ccircle cx='14' cy='16' r='2' fill='%235B2C2C'/%3E%3Ccircle cx='26' cy='16' r='2' fill='%235B2C2C'/%3E%3Cpath d='M16 23 Q20 27 24 23' stroke='%239B4A4A' fill='none' stroke-width='1.5'/%3E%3C/svg%3E",
    color: "#C0392B",
    welcome: [
      "欢迎来到揉碎星辰的个人花园~",
      "这里存放着他与所有美好事物的相遇记录。",
      "你想先看看什么呢？",
    ],
    pageHints: {
      "/anime/":    "这里是追番区~145部动漫按制作社分类好了，点击标题左边的小箭头可以展开或收起哦。",
      "/music/":    "音乐区~每首歌点进去可以在网易云试听。目前收藏还不多，但都是他很喜欢的歌。",
      "/lightnovel/": "轻小说分区~按出版社排列的。和追番页一样，点击出版社名可以折叠。",
      "/create/":   "创作区~他在设计一个叫「心穴」的游戏。如果你想了解，点进去看看。",
      "/about/":    "关于他的页面~如果你想了解更多，这里有一些简单的自我介绍。",
    },
    quickReplies: ["📺 看番", "📝 轻小说", "🎵 听歌", "🎮 创作"],
    idleTalks: [
      "今天想看点什么呢？",
      "需要帮忙推荐一部番吗？你随便说一个类型~",
      "如果感到疲惫的话，休息一下也是可以的哦。",
      "朋也君说过：只要找到一件喜欢的事，就能坚持下去。",
      "你看过CLANNAD吗？如果没有的话……推荐一下。",
    ],
    guideTour: [
      { msg: "想先看看追番页吗？按制作社分类很清爽的~", action:"link", target:"anime/" },
      { msg: "或者你想先了解他在设计什么游戏？「心穴」在创作区。", action:"link", target:"create/" },
    ],
  },

  "立华奏": {
    from: "Angel Beats!",
    avatar: "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 40 40'%3E%3Ccircle cx='20' cy='18' r='16' fill='%23E8DAEF'/%3E%3Ccircle cx='14' cy='17' r='2' fill='%234A235A'/%3E%3Ccircle cx='26' cy='17' r='2' fill='%234A235A'/%3E%3Cpath d='M18 22 L22 22' stroke='%237D3C98' fill='none' stroke-width='1.5'/%3E%3C/svg%3E",
    color: "#8E44AD",
    welcome: [
      "欢迎。",
      "追番。轻小说。音乐。创作。",
      "选一个。",
    ],
    pageHints: {
      "/anime/":    "145部。按制作社分类。点击可折叠。",
      "/music/":    "音乐。网易云外链。点击可试听。",
      "/lightnovel/": "轻小说。按出版社排列。",
      "/create/":   "创作。心穴。游戏设计。",
      "/about/":    "这是我。",
    },
    quickReplies: ["📺", "📝", "🎵", "🎮"],
    idleTalks: [
      "……",
      "在你身边，很安心。",
      "麻婆豆腐。",
    ],
    guideTour: [
      { msg: "看番。", action:"link", target:"anime/" },
      { msg: "轻小说。", action:"link", target:"lightnovel/" },
    ],
  },

  "忍野忍": {
    from: "物语系列",
    avatar: "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 40 40'%3E%3Ccircle cx='20' cy='18' r='16' fill='%23FDEBD0'/%3E%3Ccircle cx='14' cy='16' r='2' fill='%23935B1B'/%3E%3Ccircle cx='26' cy='16' r='2' fill='%23935B1B'/%3E%3Cpath d='M16 23 Q20 26 24 23' stroke='%23CA6F1E' fill='none' stroke-width='1.5'/%3E%3C/svg%3E",
    color: "#F39C12",
    welcome: [
      "哼，汝终于来了。",
      "吾乃Kissshot Acerolaorion Heartunder Blade。",
      "这个花园虽小，倒也整理得像模像样。",
      "汝想看什么？吾可勉为其难地带路。",
    ],
    pageHints: {
      "/anime/":    "145部动漫。按制作社分的——汝可知晓京都动画与J.C.Staff的区别？不知也无妨。",
      "/music/":    "音乐——吾最喜欢的Mister Donut主题曲不在此处，但其他尚可一听。",
      "/lightnovel/": "轻小说区。物语系列也在其中——历那小子的事迹被记录得还算完整。",
      "/create/":   "他在做游戏。吾辈也曾是铁血热血的吸血鬼，做游戏？太温和了。",
      "/about/":    "这是自我介绍。为何要了解他人？——不过既然汝想看，请便。",
    },
    quickReplies: ["📺 动漫", "📝 小说", "🎵 音乐", "🎮 游戏"],
    idleTalks: [
      "汝还是不打算去睡觉吗？",
      "一个甜甜圈……现在就想吃。",
      "历那小子最近可好？哼，吾只是随口一问。",
      "汝的手机快没电了吧。吾感觉得到。",
    ],
    guideTour: [
      { msg: "这边是追番。吾最推荐的是物语系列——还用说吗。", action:"link", target:"anime/" },
      { msg: "哼，轻小说区也有吾的故事。去看看无妨。", action:"link", target:"lightnovel/" },
    ],
  },
};

const GUIDE_DEFAULT = "古河渚";
