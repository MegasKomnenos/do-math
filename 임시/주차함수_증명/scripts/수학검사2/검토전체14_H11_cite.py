# -*- coding: utf-8 -*-
"""H11: 11.3 표의 입력 라벨마다 장9·장10·장7B(정리 7:old-6-22의 증명)에서 그 라벨을 부르는 블록을 찾는다.
블록 = 진술 머리부터 다음 머리/절 제목까지(진술+증명), 그 밖은 '절 X.Y 준비 문단(앞 진술 L 뒤)'."""
import re, glob, os, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
root = r'C:\math\임시\주차함수_증명\장v2'
def blocks(fname):
    out = []; cur = None; sec = None; last = None; buf = []
    for ln, line in enumerate(open(os.path.join(root, fname), encoding='utf-8'), 1):
        m = re.match(r'^###\s+(\d+\.\d+)', line)
        h = re.match(r'^\*\*(정리|명제|보조정리|따름정리|정의)\s+\{\{([^}]+)\}\}(.*?)\*\*', line)
        if m or (h and '의 증명' not in h.group(3)[:12]):
            if cur is not None: out.append((cur, buf))
            if m:
                sec = m.group(1); cur = f'절 {sec} 첫머리'; buf = []
            else:
                cur = f'{h.group(1)} {{{{{h.group(2)}}}}}'; last = cur; buf = []
        elif line.startswith('∎') or line.strip().endswith('∎'):
            buf.append((ln, line))
            if cur is not None: out.append((cur, buf))
            cur = f'절 {sec} 준비 문단({last} 뒤)'; buf = []
            continue
        buf.append((ln, line))
    if cur is not None: out.append((cur, buf))
    return out
T = open(os.path.join(root, '장11.md'), encoding='utf-8').read().splitlines()
inputs = []
in113 = False
for line in T:
    if line.startswith('### 11.3'): in113 = True
    if line.startswith('### 11.4'): in113 = False
    if in113 and line.startswith('| ') and not line.startswith('| 입력') and not line.startswith('|---'):
        cells = [c.strip() for c in line.strip().strip('|').split(' | ')]
        inputs.append((cells[0], re.findall(r'\{\{(\d+[AB]?:[^}]+)\}\}', cells[0])))
B9 = blocks('장9.md'); B10 = blocks('장10.md'); B7 = blocks('장7B.md')
B7 = [b for b in B7 if b[0] == '정리 {{7:old-6-22}}']
def cites(lab, B, tag):
    res = []
    for name, buf in B:
        lines = [ln for ln, l in buf if '{{'+lab+'}}' in l]
        if lines: res.append(f'{name}[{tag}:{",".join(map(str,lines[:3]))}]')
    return res
for title, labs in inputs:
    print('#####', title[:90])
    for lab in labs:
        c9 = cites(lab, B9, '9'); c10 = cites(lab, B10, '10'); c7 = cites(lab, B7, '7B')
        print(f'  {lab}:')
        print('     첫째:', '; '.join(c9 + c7) or '-')
        print('     둘째:', '; '.join(c10) or '-')
