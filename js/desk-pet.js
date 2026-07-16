/* ══════ 桌宠核心 v1.0 ══════
   功能: 拖拽/点击说话/双击名场面/闲话/换人/跨页面记忆
   依赖: desk-pet-voices.js (必须先加载)
   ═══════════════════════════════ */

(function() {
"use strict";

/* ── 配置 ── */
const CONFIG = {
  idleInterval: 180000,   // 空闲说话间隔 (3min)
  bubbleDuration: 4000,   // 气泡显示时间
  breathePeriod: 3,       // 浮动动画周期 (秒)
  petSize: 90,            // 桌宠尺寸 (px)
  zIndex: 9999,           // 层级
};

/* ── 角色立绘 (SVG占位, 可替换为PNG) ── */
const PET_IMAGES = {
  "古河渚": "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 90 90'%3E%3Ccircle cx='45' cy='45' r='42' fill='%23FADBD8'/%3E%3Ccircle cx='35' cy='38' r='3' fill='%235B2C2C'/%3E%3Ccircle cx='55' cy='38' r='3' fill='%235B2C2C'/%3E%3Cpath d='M40 52 Q45 58 50 52' stroke='%239B4A4A' fill='none' stroke-width='2'/%3E%3Ctext x='45' y='80' text-anchor='middle' fill='%23C0392B' font-size='8'%3ENAGISA%3C/text%3E%3C/svg%3E",
  "立华奏": "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 90 90'%3E%3Ccircle cx='45' cy='45' r='42' fill='%23E8DAEF'/%3E%3Ccircle cx='35' cy='40' r='3' fill='%234A235A'/%3E%3Ccircle cx='55' cy='40' r='3' fill='%234A235A'/%3E%3Cpath d='M42 50 L48 50' stroke='%237D3C98' fill='none' stroke-width='2'/%3E%3Ctext x='45' y='80' text-anchor='middle' fill='%238E44AD' font-size='8'%3EKANADE%3C/text%3E%3C/svg%3E",
  "忍野忍": "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 90 90'%3E%3Ccircle cx='45' cy='45' r='42' fill='%23FDEBD0'/%3E%3Ccircle cx='35' cy='38' r='3' fill='%23935B1B'/%3E%3Ccircle cx='55' cy='38' r='3' fill='%23935B1B'/%3E%3Cpath d='M42 50 Q45 55 48 50' stroke='%23CA6F1E' fill='none' stroke-width='2'/%3E%3Ctext x='45' y='80' text-anchor='middle' fill='%23F39C12' font-size='8'%3ESHINOBU%3C/text%3E%3C/svg%3E",
};

/* ── 状态 ── */
let petState = {
  x: 0, y: 0,
  character: PET_DEFAULT,
  hidden: false,
  lastTalk: 0,
};

/* ── 加载状态 ── */
function loadState() {
  try {
    const s = JSON.parse(localStorage.getItem('pet-state') || '{}');
    petState.character = s.character || PET_DEFAULT;
    petState.hidden = s.hidden || false;
    petState.x = s.x || (window.innerWidth - CONFIG.petSize - 20);
    petState.y = s.y || (window.innerHeight - CONFIG.petSize - 60);
    petState.lastTalk = s.lastTalk || 0;
  } catch(e) {}
  // Clamp to viewport
  petState.x = Math.max(0, Math.min(petState.x, window.innerWidth - CONFIG.petSize));
  petState.y = Math.max(0, Math.min(petState.y, window.innerHeight - CONFIG.petSize));
}

function saveState() {
  localStorage.setItem('pet-state', JSON.stringify(petState));
}

/* ── DOM构建 ── */

function createPet() {
  // 主容器
  const container = document.createElement('div');
  container.id = 'desk-pet';
  container.style.cssText = `
    position:fixed; z-index:${CONFIG.zIndex}; cursor:grab; user-select:none;
    width:${CONFIG.petSize}px; height:${CONFIG.petSize + 30}px;
    left:${petState.x}px; top:${petState.y}px;
    animation: pet-breathe ${CONFIG.breathePeriod}s ease-in-out infinite;
    transition: none;
  `;

  // 立绘
  const img = document.createElement('img');
  img.id = 'pet-img';
  img.src = PET_IMAGES[petState.character] || PET_IMAGES[PET_DEFAULT];
  img.alt = petState.character;
  img.title = petState.character;
  img.style.cssText = `width:${CONFIG.petSize}px; height:${CONFIG.petSize}px; border-radius:12px; pointer-events:none;`;
  img.draggable = false;

  // 名字标签
  const label = document.createElement('div');
  label.className = 'pet-label';
  label.textContent = petState.character;
  label.style.cssText = 'text-align:center; font-size:10px; color:#8B7355; margin-top:2px; pointer-events:none;';

  container.appendChild(img);
  container.appendChild(label);
  document.body.appendChild(container);

  // 呼吸动画 (只注入一次)
  if (!document.getElementById('pet-breathe-keyframes')) {
    const style = document.createElement('style');
    style.id = 'pet-breathe-keyframes';
    style.textContent = `@keyframes pet-breathe{0%,100%{transform:translateY(0)}50%{transform:translateY(-4px)}}`;
    document.head.appendChild(style);
  }

  if (petState.hidden) container.style.display = 'none';
  return container;
}

/* ── 对话气泡 ── */

function showBubble(text, isSpecial) {
  const old = document.querySelector('.pet-bubble');
  if (old) old.remove();

  const bubble = document.createElement('div');
  bubble.className = 'pet-bubble';
  const charData = PET_VOICES[petState.character];
  const color = (charData && charData.color) || '#5B3E2E';

  bubble.style.cssText = `
    position:fixed; z-index:${CONFIG.zIndex+1};
    left:${petState.x + CONFIG.petSize/2 - 100}px;
    top:${petState.y - 36}px;
    max-width:200px; min-width:60px;
    padding:8px 14px; border-radius:14px;
    background:rgba(255,252,246,0.95);
    color:#4A3728; font-size:13px; line-height:1.5;
    box-shadow:0 4px 16px rgba(0,0,0,0.12);
    pointer-events:none; word-wrap:break-word;
    animation: pet-bubble-in 0.3s ease-out;
    ${isSpecial ? `border:2px solid ${color};` : ''}
  `;
  bubble.textContent = text;

  // 防止重复注入动画定义
  if (!document.getElementById('pet-bubble-keyframes')) {
    const animStyle = document.createElement('style');
    animStyle.id = 'pet-bubble-keyframes';
    animStyle.textContent = `@keyframes pet-bubble-in{from{opacity:0;transform:translateY(6px)}to{opacity:1;transform:translateY(0)}}`;
    document.head.appendChild(animStyle);
  }
  document.body.appendChild(bubble);

  setTimeout(() => {
    if (bubble.parentNode) bubble.remove();
  }, CONFIG.bubbleDuration);
}

/* ── 台词系统 ── */

function randomLine(type) {
  const v = PET_VOICES[petState.character];
  if (!v) return '...';
  const pool = v[type] || v.idle;
  return pool[Math.floor(Math.random() * pool.length)];
}

function say(type) {
  const line = randomLine(type);
  showBubble(line, type === 'special');
  petState.lastTalk = Date.now();
  saveState();
}

/* ── 拖拽系统 ── */

function initDrag(container) {
  let dragging = false;
  let startX, startY, origX, origY;

  container.addEventListener('mousedown', (e) => {
    if (e.button !== 0) return;
    dragging = true;
    container.style.cursor = 'grabbing';
    container.style.transition = 'none';
    startX = e.clientX; startY = e.clientY;
    origX = petState.x; origY = petState.y;
    e.preventDefault();
  });

  document.addEventListener('mousemove', (e) => {
    if (!dragging) return;
    petState.x = origX + (e.clientX - startX);
    petState.y = origY + (e.clientY - startY);
    petState.x = Math.max(0, Math.min(petState.x, window.innerWidth - CONFIG.petSize));
    petState.y = Math.max(0, Math.min(petState.y, window.innerHeight - CONFIG.petSize));
    container.style.left = petState.x + 'px';
    container.style.top = petState.y + 'px';
  });

  document.addEventListener('mouseup', () => {
    if (dragging) {
      dragging = false;
      container.style.cursor = 'grab';
      saveState();
      clickTimer = null; // P1-5: 拖拽后重置双击计时器
    }
  });

  // 点击事件 (drag时不触发)
  let clickTimer = null;
  container.addEventListener('click', (e) => {
    if (dragging || (clickTimer && Date.now() - clickTimer < 300)) {
      // double click
      say('special');
      clickTimer = null;
    } else {
      clickTimer = Date.now();
      setTimeout(() => {
        if (clickTimer && Date.now() - clickTimer >= 300) {
          say('click');
        }
      }, 300);
    }
    e.stopPropagation();
  });

  // 右键菜单
  container.addEventListener('contextmenu', (e) => {
    e.preventDefault();
    showMenu(e.clientX, e.clientY);
  });
}

/* ── 右键菜单 ── */

function showMenu(mx, my) {
  const old = document.querySelector('.pet-menu');
  if (old) old.remove();

  const menu = document.createElement('div');
  menu.className = 'pet-menu';
  menu.style.cssText = `
    position:fixed; z-index:${CONFIG.zIndex+5};
    left:${mx}px; top:${my}px;
    background:rgba(255,252,246,0.96); border-radius:8px;
    box-shadow:0 4px 20px rgba(0,0,0,0.15);
    padding:4px 0; min-width:120px;
    animation:pet-menu-in 0.2s ease-out;
  `;

  // 角色选项
  for (const name in PET_VOICES) {
    const item = createMenuItem(name, () => {
      petState.character = name;
      const img = document.getElementById('pet-img');
      if (img) img.src = PET_IMAGES[name] || PET_IMAGES[PET_DEFAULT];
      const label = document.querySelector('.pet-label');
      if (label) label.textContent = name;
      saveState();
      say('idle');
    });
    menu.appendChild(item);
  }

  // 分隔线
  const sep = document.createElement('div');
  sep.style.cssText = 'border-top:1px solid rgba(180,150,120,0.2); margin:4px 0;';
  menu.appendChild(sep);

  // 隐藏/显示
  const hideItem = createMenuItem(petState.hidden ? '👁 显示桌宠' : '🙈 隐藏桌宠', () => {
    petState.hidden = !petState.hidden;
    const container = document.getElementById('desk-pet');
    if (container) container.style.display = petState.hidden ? 'none' : '';
    saveState();
    if (old) old.remove();
  });
  menu.appendChild(hideItem);

  document.body.appendChild(menu);

  // 点击空白关闭
  setTimeout(() => {
    const handler = (e) => {
      if (!menu.contains(e.target)) {
        menu.remove();
        document.removeEventListener('click', handler);
      }
    };
    document.addEventListener('click', handler);
  }, 10);
}

function createMenuItem(text, onClick) {
  const div = document.createElement('div');
  div.textContent = text;
  div.style.cssText = 'padding:6px 16px; font-size:13px; cursor:pointer; color:#4A3728; transition:background .15s;';
  div.addEventListener('mouseenter', () => div.style.background = 'rgba(200,160,100,0.1)');
  div.addEventListener('mouseleave', () => div.style.background = '');
  div.addEventListener('click', () => { onClick(); div.parentElement.remove(); });
  return div;
}

/* ── 空闲说话 ── */

function initIdleTalk() {
  setInterval(() => {
    if (petState.hidden) return;
    if (Date.now() - petState.lastTalk > CONFIG.idleInterval) {
      say('idle');
    }
  }, 30000); // 每30秒检查一次
}

/* ── 初始化 ── */

function init() {
  loadState();
  if (typeof PET_VOICES === 'undefined') {
    console.warn('desk-pet: PET_VOICES not loaded. Is desk-pet-voices.js included?');
    return;
  }
  const container = createPet();
  initDrag(container);
  initIdleTalk();

  // 初始招呼
  if (petState.lastTalk === 0) {
    setTimeout(() => say('idle'), 2000);
  }

  // 窗口大小变化时限定位置
  window.addEventListener('resize', () => {
    petState.x = Math.min(petState.x, window.innerWidth - CONFIG.petSize);
    petState.y = Math.min(petState.y, window.innerHeight - CONFIG.petSize);
    const container = document.getElementById('desk-pet');
    if (container) {
      container.style.left = petState.x + 'px';
      container.style.top = petState.y + 'px';
    }
    saveState();
  });

  console.log('Desk pet ready:', petState.character);
}

// 启动
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', init);
} else {
  init();
}

})();
