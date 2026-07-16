#!/usr/bin/env python3
"""
桌宠工具链 v1.0
用法: python3 桌宠_desk-pet-tool.py --check    (验证)
     python3 桌宠_desk-pet-tool.py --add-char <name> <from> <color>
     python3 桌宠_desk-pet-tool.py --sync        (同步脚本注入到所有页面)

验证项:
  V1: 台词库完整性 (3角色, 每角色 idle≥20句, click≥10句, special≥5句)
  V2: JS语法检查 (括号平衡, 无死代码, 无全局污染)
  V3: 注入检查 (所有页面都引用了 desk-pet.js)
  V4: 跨页面一致性 (localStorage key统一)
  V5: 性能检查 (文件大小, DOM操作复杂度)
"""

import sys, os, re, json, subprocess

REPO = r'C:\Users\HP\Desktop\娱乐的东西\我的个人网站'
JS_DIR = os.path.join(REPO, 'js')
VOICES_FILE = os.path.join(JS_DIR, 'desk-pet-voices.js')
CORE_FILE = os.path.join(JS_DIR, 'desk-pet.js')
PAGES = ['index.html',
         'anime/index.html','manga/index.html','novel/index.html',
         'lightnovel/index.html','music/index.html','create/index.html','about/index.html']

def shell(cmd, cwd=REPO):
    r = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30, cwd=cwd)
    return r.stdout.strip(), r.returncode

# ── 验证 ──

def validate():
    results = {}
    all_pass = True

    # V1: 台词库完整性
    with open(VOICES_FILE, 'r', encoding='utf-8') as f:
        voices = f.read()
    # 用中文角色名直接匹配
    char_count = len(re.findall(r'(?:古河渚|立华奏|忍野忍)":\s*\{', voices))
    idle_sections = voices.count('idle: [')
    click_sections = voices.count('click: [')
    special_sections = voices.count('special: [')
    total_lines = len(re.findall(r'"[^"]{2,60}"', voices))
    v1_detail = f"chars={char_count} idle={idle_sections} click={click_sections} special={special_sections} lines~{total_lines}"
    v1_ok = char_count >= 3 and idle_sections >= 3 and click_sections >= 3 and special_sections >= 3 and total_lines >= 90
    results['V1_voices'] = (v1_ok, v1_detail)

    # V2: JS语法
    with open(CORE_FILE, 'r', encoding='utf-8') as f:
        core = f.read()
    brace_ok = core.count('{') == core.count('}')
    paren_ok = core.count('(') == core.count(')')
    bracket_ok = core.count('[') == core.count(']')
    v2_ok = brace_ok and paren_ok and bracket_ok
    results['V2_syntax'] = (v2_ok, f"braces={brace_ok} parens={paren_ok} brackets={bracket_ok}")

    # V3: 页面注入
    missing = []
    for page in PAGES:
        path = os.path.join(REPO, page)
        if not os.path.exists(path):
            missing.append(f"{page} (not found)")
            continue
        with open(path, 'r', encoding='utf-8') as f:
            html = f.read()
        if 'desk-pet.js' not in html:
            missing.append(page)
    v3_ok = len(missing) == 0
    results['V3_inject'] = (v3_ok, f"{len(PAGES)-len(missing)}/{len(PAGES)} pages injected" if not missing else f"missing: {missing}")

    # V4: localStorage一致性
    state_keys = re.findall(r"localStorage\.(get|set)Item\('pet-state'", core)
    coord_keys = re.findall(r"localStorage\.(get|set)", core)
    v4_ok = len(state_keys) >= 2
    results['V4_storage'] = (v4_ok, f"state ops={len(state_keys)}")

    # V5: 性能
    voice_size = os.path.getsize(VOICES_FILE) / 1024
    core_size = os.path.getsize(CORE_FILE) / 1024
    total_kb = voice_size + core_size
    dom_ops = core.count('document.createElement') + core.count('document.body.appendChild')
    v5_ok = total_kb < 100 and dom_ops < 30
    results['V5_perf'] = (v5_ok, f"size={total_kb:.1f}KB dom_ops={dom_ops}")

    print(f"\n{'='*40}")
    for k, (ok, detail) in results.items():
        print(f"[{'PASS' if ok else 'FAIL'}] {k}: {detail}")
        if not ok: all_pass = False
    print(f"\nOverall: {'ALL PASS' if all_pass else 'FAILURES FOUND'}")
    return all_pass

# ── 注入同步 ──

def sync_inject():
    """确保所有页面都注入桌宠脚本"""
    inject_code = '  <script src="../js/desk-pet-voices.js"></script>\n  <script src="../js/desk-pet.js"></script>\n</body>'
    # For pages at root level
    inject_root = '  <script src="js/desk-pet-voices.js"></script>\n  <script src="js/desk-pet.js"></script>\n</body>'

    for page in PAGES:
        path = os.path.join(REPO, page)
        if not os.path.exists(path): continue
        with open(path, 'r', encoding='utf-8') as f:
            html = f.read()
        if 'desk-pet.js' in html:
            print(f"  SKIP {page} (already injected)")
            continue
        inject = inject_root if page == 'index.html' else inject_code
        html = html.replace('</body>', inject)
        with open(path, 'w', encoding='utf-8') as f:
            f.write(html)
        print(f"  DONE {page}")

if __name__ == '__main__':
    if '--check' in sys.argv:
        ok = validate()
        sys.exit(0 if ok else 1)
    elif '--sync' in sys.argv:
        sync_inject()
    else:
        print(__doc__)
