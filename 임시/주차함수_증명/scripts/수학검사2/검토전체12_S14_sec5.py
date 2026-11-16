# -*- coding: utf-8 -*-
"""S14: 장부 5절 「이 장이 처음 정의하는 전역 기호」 열과 1.2의 「정의 절」·「쓰이는 장」, 여유 글자의 일관성을 센다."""
import re, sys, io, pathlib
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
ROOT = pathlib.Path(r"C:\math\임시\주차함수_증명")
lines = (ROOT/"장부_v2.md").read_text(encoding='utf-8').splitlines()
def norm(s): return re.sub(r'\s+', '', s).replace('{', '').replace('}', '')
# 1.2 행
rows12 = []
for i in range(48, 338):
    l = lines[i]
    if l.startswith('| $'):
        c = [x.strip() for x in l.strip().strip('|').split('|')]
        rows12.append((i+1, c))
# 5절 행
sec5 = {}
for i in range(1197, 1208):
    l = lines[i]
    if l.startswith('| '):
        c = [x.strip() for x in l.strip().strip('|').split('|')]
        if c[0].isdigit():
            sec5[int(c[0])] = c
print("=== 1.2 정의 절의 장과 5절 「처음 정의하는 전역 기호」의 대조")
for ln, c in rows12:
    g = norm(c[0])
    dsecs = re.findall(r'(\d+)\.\d+', c[3])
    if not dsecs: continue
    chs = sorted(set(int(d) for d in dsecs))
    for ch in chs:
        col = norm(sec5[ch][1]) if ch in sec5 else ''
        if g not in col:
            # 글자 가운데 하나라도 있으면 통과
            parts = [norm(p) for p in re.findall(r'\$([^$]+)\$', c[0])]
            if not any(p in col for p in parts):
                print(f"  L{ln} {c[0][:50]} | 정의 절 {c[3]} | 5절 {ch}장 열에 없음")
print("=== 5절 열에 있으나 1.2의 그 장 정의가 아닌 글자")
g12 = {}
for ln, c in rows12:
    for p in re.findall(r'\$([^$]+)\$', c[0]):
        g12[norm(p)] = (ln, c[3])
for ch, c in sec5.items():
    for p in re.findall(r'\$([^$]+)\$', c[1]):
        p2 = norm(p)
        if p2 not in g12:
            print(f"  {ch}장 열의 {p} — 1.2에 같은 꼴의 행 없음")
        else:
            ln, d = g12[p2]
            if str(ch) not in re.findall(r'(\d+)\.\d+', d):
                print(f"  {ch}장 열의 {p} — 1.2 L{ln} 정의 절 {d}")
print("=== 여유 글자 대 쓰이는 글자(바탕 글자·글자체) 겹침")
FONT = re.compile(r'(\\(?:mathcal|mathfrak|mathsf)[A-Za-z]|\\[A-Za-z]+|[A-Za-z])')
used = {ch: set() for ch in range(1, 12)}
for ln, c in rows12:
    chs = list(range(1, 12)) if '전 장' in c[4] else [int(x) for x in re.findall(r'\b(\d{1,2})\b', c[4].split('(')[0])]
    for p in re.findall(r'\$([^$]+)\$', c[0]):
        for it in re.split(r',(?![^{]*\})', p):
            m = FONT.match(norm(it))
            if m:
                for ch in chs: used[ch].add(m.group(1))
# 1.1 변수 글자와 1장 전역, 6절 예약 바탕 글자
var = set()
for i in range(27, 41):
    l = lines[i]
    if l.startswith('| $'):
        c = [x.strip() for x in l.strip().strip('|').split('|')]
        for p in re.findall(r'\$([^$]+)\$', c[0]):
            m = FONT.match(norm(p))
            if m: var.add(m.group(1))
reserved = {'a', 'b', 'c', 'e', 'h', '\\delta', '\\Delta', '\\Sigma', 'l', 'o', 'O', '\\varpi', 'P', 'Q', 'W', 'X'}
for ch, c in sec5.items():
    free = [norm(p) for p in re.findall(r'\$([^$]+)\$', c[3])]
    bad = [f for f in free if f in used[ch] or f in used[1] or f in var or f in reserved]
    if bad: print(f"  {ch}장 여유 글자 가운데 그 장(또는 1장)의 전역·1.1·예약과 겹침: {bad}")
