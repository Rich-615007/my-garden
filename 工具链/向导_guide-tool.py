#!/usr/bin/env python3
"""聊天向导工具链 v1.0"""
import sys, os, re, subprocess

REPO = r'C:\Users\HP\Desktop\娱乐的东西\我的个人网站'
JS_DIR = os.path.join(REPO, 'js')
CHARS_FILE = os.path.join(JS_DIR, 'guide-characters.js')
WIDGET_FILE = os.path.join(JS_DIR, 'guide-widget.js')
PAGES = ['index.html','anime/index.html','manga/index.html','novel/index.html',
         'lightnovel/index.html','music/index.html','create/index.html','about/index.html']

def shell(cmd, cwd=REPO):
    r = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30, cwd=cwd)
    return r.stdout.strip(), r.returncode

def validate():
    results = {}
    all_pass = True

    with open(CHARS_FILE, 'r', encoding='utf-8') as f:
        chars = f.read()
    with open(WIDGET_FILE, 'r', encoding='utf-8') as f:
        widget = f.read()

    # V1: 角色完整性
    char_count = chars.count('"古河渚"') + chars.count('"立华奏"') + chars.count('"忍野忍"')
    has_welcome = chars.count('welcome')  # 每个角色都有welcome数组
    has_hints = chars.count('pageHints')
    has_quick = chars.count('quickReplies')
    v1_ok = char_count >= 3 and has_welcome >= 3 and has_hints >= 3 and has_quick >= 3
    results['V1_chars'] = (v1_ok, f"chars={char_count} welcome={has_welcome} hints={has_hints}")

    # V2: JS语法
    v2_failed = False
    for name, code in [('chars', chars), ('widget', widget)]:
        braces = code.count('{') == code.count('}')
        parens = code.count('(') == code.count(')')
        if not (braces and parens):
            v2_failed = True
            results[f'V2_{name}'] = (False, f"braces={braces} parens={parens}")
    if not v2_failed:
        results['V2_syntax'] = (True, "pass")

    # V3: 页面注入
    missing = []
    for page in PAGES:
        path = os.path.join(REPO, page)
        if not os.path.exists(path): continue
        with open(path, 'r', encoding='utf-8') as f:
            html = f.read()
        if 'guide-widget.js' not in html:
            missing.append(page)
    v3_ok = len(missing) == 0
    results['V3_inject'] = (v3_ok, f"{len(PAGES)-len(missing)}/{len(PAGES)} injected" if not missing else f"missing:{missing}")

    # V4: localStorage
    state_ops = widget.count("guide-state")
    v4_ok = state_ops >= 2
    results['V4_storage'] = (v4_ok, f"state ops={state_ops}")

    # V5: 性能
    total_kb = (os.path.getsize(CHARS_FILE) + os.path.getsize(WIDGET_FILE)) / 1024
    v5_ok = total_kb < 100
    results['V5_perf'] = (v5_ok, f"{total_kb:.1f}KB")

    print(f"\n{'='*40}")
    for k, (ok, detail) in results.items():
        print(f"[{'PASS' if ok else 'FAIL'}] {k}: {detail}")
        if not ok: all_pass = False
    print(f"\nOverall: {'ALL PASS' if all_pass else 'FAILURES FOUND'}")
    return all_pass

if __name__ == '__main__':
    if '--check' in sys.argv:
        ok = validate()
        sys.exit(0 if ok else 1)
    else:
        print(__doc__)
