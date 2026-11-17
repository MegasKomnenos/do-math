# 부록 A의 「기록의 글자」 칸과 부록 C 셋째 표가 같은 (이 글의 글자, 기록) 쌍을 싣는지 맞대어 본다(후보 찾기 — 한 행에 글자·기록이 여럿이면 쌍을 어림으로 만든다).
import re, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', newline='\n')
root = r'C:/math/임시/주차함수_증명/장v2/'
A = open(root+'부록A.md', encoding='utf-8').read().split('\n')
C = open(root+'부록C.md', encoding='utf-8').read().split('\n')
def cells(l): return [c.strip() for c in l.strip().strip('|').split(' | ')]
def syms(cell):
    out = []
    for m in re.finditer(r'\$([^$]+)\$', cell):
        s = m.group(1)
        depth = 0; cur = ''
        for ch in s:
            if ch in '({[': depth += 1
            if ch in ')}]': depth -= 1
            if ch == ',' and depth == 0: out.append(cur.strip()); cur = ''
            else: cur += ch
        out.append(cur.strip())
    res = []
    for s in out:
        h = re.sub(r'\([^()]*\)$', '', s).strip()
        h = re.sub(r':?=.*$', '', h).strip()
        h = re.sub(r'_\{?[a-zA-Z0-9+\-,\ ]*\}?$', '', h) if False else h
        res.append(h.replace(' ', ''))
    return res
def core(h):
    # 첨자의 변수 글자를 지워 양의 머리만 남긴다: s_m → s_, \mathrm{Bor} 그대로
    h = re.sub(r'_\{[^{}]*\}', '_', h); h = re.sub(r'_[A-Za-z0-9]', '_', h)
    return h
Amap = {}
for i, l in enumerate(A):
    if not l.startswith('| $'): continue
    c = cells(l)
    recs = set(re.findall(r'r[0-9a-f]{7}', c[3]))
    for h in syms(c[0]):
        Amap.setdefault(core(h), (i+1, set(), c[0]))[1].update(recs)
a = next(i for i,l in enumerate(C) if l.startswith('### 기록의 글자와'))
b = next(i for i,l in enumerate(C) if l.startswith('### 영어를'))
miss = 0
for i in range(a, b):
    l = C[i]
    if not l.startswith('| ') or l.startswith('| 이 글의') or l.startswith('|---'): continue
    c = cells(l)
    recs = re.findall(r'r[0-9a-f]{7}', c[1])
    hs = syms(c[0])
    if len(hs) != 1: continue        # 글자 하나짜리 행만(쌍이 분명한 행)
    k = core(hs[0])
    if k not in Amap: continue
    an, arecs, a0 = Amap[k]
    lack = [r for r in recs if r not in arecs]
    if lack:
        miss += 1
        print(f'[C {i+1}] {c[0]} : 부록 A {an}행({a0})의 기록 칸에 없는 기록 {lack} | C의 글자: {c[2][:110]}')
print('후보 수', miss)
