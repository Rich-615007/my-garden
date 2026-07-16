/* ══════ 聊天向导 v1.0 ══════
   功能: 聊天窗口 / 页面感知 / 引导对话 / 快捷跳转 / 换角色 / 静音 / 跨页面记忆
   依赖: guide-characters.js (先加载)
   ═══════════════════════════════ */

(function() {
"use strict";

const Z = 9998;
const MSG_DELAY = 1200;    // 角色回复间隔
const IDLE_INTERVAL = 300000; // 5min空闲说话
const MAX_HISTORY = 5;     // 保留消息数

let state = {
  character: GUIDE_DEFAULT,
  collapsed: true,
  muted: false,
  history: [],
  lastTalk: 0,
  guideSeen: false,
};

/* ── state 读写 ── */
function loadState() {
  try {
    const s = JSON.parse(localStorage.getItem('guide-state') || '{}');
    state.character = s.character || GUIDE_DEFAULT;
    state.collapsed = s.collapsed !== false;
    state.muted = s.muted || false;
    state.lastTalk = s.lastTalk || 0;
    state.guideSeen = s.guideSeen || false;
  } catch(e) {}
}
function saveState() {
  const { character, collapsed, muted, lastTalk, guideSeen } = state;
  localStorage.setItem('guide-state', JSON.stringify({character,collapsed,muted,lastTalk,guideSeen}));
}

/* ── 获取角色 ── */
function charData() { return GUIDE_CHARS[state.character] || GUIDE_CHARS[GUIDE_DEFAULT]; }

/* ── 获取当前页面key ── */
function pageKey() {
  const p = window.location.pathname.toLowerCase();
  if (p.includes('/anime/'))    return '/anime/';
  if (p.includes('/music/'))    return '/music/';
  if (p.includes('/lightnovel/')) return '/lightnovel/';
  if (p.includes('/create/'))   return '/create/';
  if (p.includes('/about/'))    return '/about/';
  return '/index.html';
}

/* ── DOM ── */

let widgetEl, bodyEl, inputEl, toggleEl, charNameEl;
let quickBtns = [];

function createWidget() {
  const cd = charData();

  // 主容器
  widgetEl = document.createElement('div');
  widgetEl.id = 'guide-widget';
  widgetEl.style.cssText = `
    position:fixed; z-index:${Z}; right:12px; bottom:12px;
    width:${state.collapsed ? 'auto' : '280px'};
    max-height:${state.collapsed ? 'auto' : '420px'};
    background:rgba(255,252,246,0.96); border-radius:14px;
    box-shadow:0 4px 24px rgba(60,30,10,0.15);
    font-family:"PingFang SC","Microsoft YaHei",sans-serif;
    transition:width .25s,max-height .25s;
    overflow:hidden; font-size:13px;
  `;

  // 顶部标题栏
  const header = document.createElement('div');
  header.style.cssText = `display:flex;align-items:center;gap:8px;padding:8px 12px;cursor:pointer;user-select:none;border-bottom:1px solid rgba(180,150,120,0.15);`;
  header.onclick = toggleWidget;

  const avatar = document.createElement('img');
  avatar.id = 'guide-avatar';
  avatar.src = cd.avatar;
  avatar.style.cssText = 'width:28px;height:28px;border-radius:50%;flex-shrink:0;';

  charNameEl = document.createElement('span');
  charNameEl.id = 'guide-char-name';
  charNameEl.textContent = `${state.character} · ${cd.from}`;
  charNameEl.style.cssText = `font-weight:600;color:#5B3E2E;flex:1;font-size:12px;`;

  toggleEl = document.createElement('span');
  toggleEl.textContent = state.collapsed ? '展开' : '收起';
  toggleEl.style.cssText = 'font-size:11px;color:#A09080;';

  header.appendChild(avatar);
  header.appendChild(charNameEl);
  header.appendChild(toggleEl);
  widgetEl.appendChild(header);

  // 消息区
  bodyEl = document.createElement('div');
  bodyEl.id = 'guide-body';
  bodyEl.style.cssText = `
    padding:10px 12px; overflow-y:auto;
    max-height:260px; min-height:40px;
    display:flex; flex-direction:column; gap:6px;
    display:${state.collapsed ? 'none' : 'flex'};
  `;
  widgetEl.appendChild(bodyEl);

  // 快捷回复栏
  const quickBar = document.createElement('div');
  quickBar.id = 'guide-quick';
  quickBar.style.cssText = `
    display:${state.collapsed ? 'none' : 'flex'};
    gap:6px; padding:6px 12px; flex-wrap:wrap;
    border-top:1px solid rgba(180,150,120,0.1);
  `;
  cd.quickReplies.forEach((txt, i) => {
    const btn = document.createElement('button');
    btn.textContent = txt;
    btn.style.cssText = `
      padding:4px 10px; border-radius:14px; border:1px solid rgba(180,150,120,0.25);
      background:rgba(250,245,235,0.6); font-size:11px; cursor:pointer;
      color:#4A3728; font-family:inherit;
      transition:all .15s;
    `;
    btn.onmouseenter = () => { btn.style.background = 'rgba(200,160,100,0.2)'; };
    btn.onmouseleave = () => { btn.style.background = 'rgba(250,245,235,0.6)'; };
    btn.onclick = () => handleQuickReply(txt);
    quickBtns.push(btn);
    quickBar.appendChild(btn);
  });
  widgetEl.appendChild(quickBar);

  // 底部功能栏
  const footer = document.createElement('div');
  footer.style.cssText = `
    display:${state.collapsed ? 'none' : 'flex'};
    justify-content:space-between; padding:4px 12px 8px;
    border-top:1px solid rgba(180,150,120,0.1);
  `;

  const switchBtn = mkFooterBtn('🔄 换人', showSwitchMenu);
  const muteBtn = mkFooterBtn(state.muted ? '🔇 已静音' : '🔊', toggleMute);

  const tourBtn = mkFooterBtn('🗺 导览', () => {
    const cd2 = charData();
    cd2.guideTour.forEach((t, i) => {
      setTimeout(() => {
        addMessage(t.msg, 'char');
        if (i === cd2.guideTour.length - 1) {
          setTimeout(() => addMessage('点卡片能跳转哦~', 'char'), 800);
        }
      }, i * 1500);
    });
  });

  footer.appendChild(switchBtn);
  footer.appendChild(tourBtn);
  footer.appendChild(muteBtn);
  widgetEl.appendChild(footer);

  // 收起态预览行
  const preview = document.createElement('div');
  preview.id = 'guide-preview';
  preview.style.cssText = `
    padding:6px 14px 8px; font-size:12px; color:#8B7355;
    display:${state.collapsed ? 'block' : 'none'};
    cursor:pointer;
  `;
  preview.textContent = '💬 点击看看';
  preview.onclick = () => {
    state.collapsed = false;
    refreshWidget();
  };
  widgetEl.appendChild(preview);

  document.body.appendChild(widgetEl);
}

function mkFooterBtn(text, onClick) {
  const b = document.createElement('button');
  b.textContent = text;
  b.style.cssText = 'padding:3px 8px;border:none;background:none;font-size:11px;color:#8B7355;cursor:pointer;font-family:inherit;border-radius:8px;';
  b.onmouseenter = () => { b.style.background = 'rgba(200,160,100,0.1)'; };
  b.onmouseleave = () => { b.style.background = 'none'; };
  b.onclick = (e) => { e.stopPropagation(); onClick(); };
  return b;
}

/* ── Widget 操作 ── */

function refreshWidget() {
  if (widgetEl) widgetEl.remove();
  createWidget();
  if (!state.collapsed && state.history.length === 0) {
    greetUser();
  }
}

function toggleWidget() {
  state.collapsed = !state.collapsed;
  saveState();
  refreshWidget();
}

function toggleMute() {
  state.muted = !state.muted;
  saveState();
  refreshWidget();
}

function handleQuickReply(txt) {
  addMessage(txt, 'user');
  const cd = charData();

  // 根据快捷回复内容决定跳转
  const routes = {
    '📺 看番': ['anime/', '追番页在那边~'],
    '📺 追番': ['anime/', '145部番等着你呢~'],
    '📺 动漫': ['anime/', '哼，随汝去看。'],
    '📺': ['anime/', '。'],
    '📝 轻小说': ['lightnovel/', '轻小说区~有很多好书哦。'],
    '📝 小说': ['lightnovel/', '轻小说在这边。'],
    '📝': ['lightnovel/', '。'],
    '🎵 听歌': ['music/', '音乐区~希望你喜欢。'],
    '🎵 音乐': ['music/', '有很多动画的OST。'],
    '🎵': ['music/', '。'],
    '🎮 创作': ['create/', '创作区~看看他在做什么吧。'],
    '🎮 游戏': ['create/', '心穴在创作区。'],
    '🎮': ['create/', '。'],
  };

  setTimeout(() => {
    let replied = false;
    for (const [key, [target, reply]] of Object.entries(routes)) {
      if (txt.includes(key.replace(/[📺📝🎵🎮]/g,'').trim())) {
        addMessage(reply, 'char');
        setTimeout(() => { window.location.href = target; }, 800);
        replied = true;
        break;
      }
    }
    if (!replied) {
      const msg = cd.idleTalks[Math.floor(Math.random() * cd.idleTalks.length)];
      addMessage(msg, 'char');
    }
  }, MSG_DELAY);
}

function showSwitchMenu() {
  const menu = document.createElement('div');
  menu.style.cssText = `position:fixed;z-index:${Z+5};right:16px;bottom:60px;background:rgba(255,252,246,0.96);border-radius:8px;box-shadow:0 4px 20px rgba(0,0,0,0.15);padding:4px 0;min-width:100px;`;
  for (const name in GUIDE_CHARS) {
    const item = document.createElement('div');
    item.textContent = name;
    item.style.cssText = 'padding:6px 14px;cursor:pointer;font-size:13px;color:#4A3728;';
    item.onmouseenter = () => { item.style.background = 'rgba(200,160,100,0.1)'; };
    item.onmouseleave = () => { item.style.background = ''; };
    item.onclick = () => {
      state.character = name;
      state.history = [];
      saveState();
      refreshWidget();
      menu.remove();
    };
    menu.appendChild(item);
  }
  document.body.appendChild(menu);
  setTimeout(() => {
    const h = () => { menu.remove(); document.removeEventListener('click', h); };
    document.addEventListener('click', h);
  }, 50);
}

/* ── 消息 ── */

function addMessage(text, role) {
  if (state.collapsed) return;

  const msgEl = document.createElement('div');
  msgEl.style.cssText = `
    max-width:85%; padding:6px 10px; border-radius:10px;
    font-size:12px; line-height:1.5; word-wrap:break-word;
    animation:guide-msg-in 0.3s ease-out;
    ${role === 'char' ?
      `align-self:flex-start;background:rgba(200,160,100,0.12);color:#4A3728;` :
      `align-self:flex-end;background:rgba(180,160,140,0.2);color:#3A2A18;`}
  `;

  msgEl.textContent = text;
  bodyEl.appendChild(msgEl);
  bodyEl.scrollTop = bodyEl.scrollHeight;

  // 限制历史长度
  state.history.push({ text, role });
  if (state.history.length > MAX_HISTORY) state.history.shift();

  // 更新收起态预览
  const preview = document.getElementById('guide-preview');
  if (preview) {
    preview.textContent = `💬 ${state.character.slice(0,2)}: ${text.slice(0,20)}`;
  }

  // 注入动画 (仅一次)
  if (!document.getElementById('guide-msg-keyframes')) {
    const s = document.createElement('style');
    s.id = 'guide-msg-keyframes';
    s.textContent = '@keyframes guide-msg-in{from{opacity:0;transform:translateY(4px)}to{opacity:1;transform:translateY(0)}}';
    document.head.appendChild(s);
  }
}

/* ── 开场 / 场景 ── */

function greetUser() {
  if (state.muted) return;
  const cd = charData();

  if (!state.guideSeen) {
    // 首次访问 — 完整引导
    const allMsgs = [...cd.welcome];
    // 如果当前页面有提示，加上
    const hint = cd.pageHints[pageKey()];
    if (hint) allMsgs.push(hint);
    allMsgs.forEach((msg, i) => {
      setTimeout(() => addMessage(msg, 'char'), i * MSG_DELAY);
    });
    state.guideSeen = true;
  } else {
    // 回头客 — 根据当前页面说一句
    const hint = cd.pageHints[pageKey()];
    const msg = hint || (cd.idleTalks[Math.floor(Math.random() * cd.idleTalks.length)]);
    setTimeout(() => addMessage(msg, 'char'), 500);
  }

  state.lastTalk = Date.now();
  saveState();
}

/* ── 空闲说话 ── */

function startIdleTimer() {
  setInterval(() => {
    if (state.collapsed || state.muted) return;
    if (Date.now() - state.lastTalk > IDLE_INTERVAL) {
      const cd = charData();
      const msg = cd.idleTalks[Math.floor(Math.random() * cd.idleTalks.length)];
      addMessage(msg, 'char');
      state.lastTalk = Date.now();
      saveState();
    }
  }, 60000); // 每60秒检查
}

/* ── 初始化 ── */

function init() {
  if (typeof GUIDE_CHARS === 'undefined') {
    console.warn('guide: GUIDE_CHARS not loaded');
    return;
  }
  loadState();
  createWidget();

  if (!state.collapsed) {
    setTimeout(greetUser, 1500);
  }

  startIdleTimer();
}

if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', init);
} else {
  init();
}

})();
