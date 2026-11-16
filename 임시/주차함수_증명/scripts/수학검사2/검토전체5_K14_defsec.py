# -*- coding: utf-8 -*-
"""K14: (1) 장부 1.2 「정의 절」에 그 글자가 실제로 나타나는지, (2) 3절 낱말의 첫 출현 절이 「첫 정의 절」보다 앞서지 않는지,
(3) 5절 장별 배정이 1.2 정의 절·3절 첫 정의 절과 맞는지, (4) 의존지도 2.1절의 수(라벨 378, 비순환, 강결합 15)를 센다."""
import re, sys, io, os, collections
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
B = r'C:\math\임시\주차함수_증명'
order = ['장1','장2','장3','장4','장5A','장5B','장6','장7A','장7B','장8','장9','장10','장11']
BS = chr(92)
def norm(s): return re.sub(r'[\s{}]', '', s)
lines = []  # (ch, lineno, sec, raw, norm)
for ch in order:
    sec = ''
    for i, ln in enumerate(open(os.path.join(B, '장v2', ch + '.md'), encoding='utf-8').read().split('\n'), 1):
        m = re.match(r'^(#{2,4})\s+(\d+(?:\.\d+)*)', ln)
        if m: sec = m.group(2)
        lines.append((ch, i, sec, ln, norm(ln)))
def seckey(s): return [int(x) for x in s.split('.')] if s else [0]
def in_sec(sec, target):  # target like '5.2' matches '5.2', '5.2.1'
    return sec == target or sec.startswith(target + '.')
ledger = open(os.path.join(B, '장부_v2.md'), encoding='utf-8').read().split('\n')
# ---------- (1) 1.2 정의 절
rows = []; on = False
for line in ledger:
    if line.startswith('### 1.2'): on = True
    elif line.startswith('### 1.3'): on = False
    if on and line.startswith('| $'):
        c = [x.strip() for x in line.strip().strip('|').split('|')]
        rows.append(dict(glyph=c[0], defsec=c[3], chs=c[4]))
FONTS = r'(?:mathcal|mathfrak|mathsf|mathrm|mathbb|tilde|hat|bar)'
base_re = re.compile(r'^(' + BS + BS + FONTS + BS + BS + '[A-Za-z]+|' + BS + BS + FONTS + '[A-Za-z]+|' + BS + BS + '[A-Za-z]+|[A-Za-z]+)')
dec_re = re.compile(r'^([_^])(' + BS + BS + r'[A-Za-z]+|\*?[A-Za-z0-9]+|\(|\\?[A-Za-z0-9]+)')
def keys(p):
    m = base_re.match(p)
    if not m: return []
    base = m.group(1); rest = p[len(base):]
    ks = [p]
    m2 = dec_re.match(rest)
    if m2: ks.append(base + m2.group(1) + m2.group(2))
    core = re.sub('^' + BS + BS + FONTS, '', base).lstrip(BS)
    if len(core) > 1 and core != 'ell': ks.append(base)
    return ks
print('=== (1) 1.2 정의 절에 글자가 없는 행')
for r in rows:
    secs = re.findall(r'\d+\.\d+', r['defsec'])
    ps = [norm(x) for x in re.findall(r'\$([^$]+)\$', r['glyph'])]
    ks = []
    for p in ps: ks += keys(p)
    ks = list(dict.fromkeys(ks))
    for s in secs:
        hit = any(k in n for (ch, i, sec, raw, n) in lines if in_sec(sec, s) for k in ks)
        if not hit:
            # 첫 출현 절
            first = next(((ch, i, sec) for (ch, i, sec, raw, n) in lines for k in ks if k in n), None)
            print(r['glyph'][:50].ljust(50), '| 정의 절', s, '| 열쇠', ks[:3], '| 첫 출현', first)
# ---------- (2) 3절 낱말 첫 출현
print('=== (2) 3절 낱말: 첫 정의 절보다 앞선 출현(1.4절 개관은 뺌)')
sec3 = []; on = False
for line in ledger:
    if line.startswith('## 3.'): on = True
    elif line.startswith('## 4.'): on = False
    if on and line.startswith('| ') and not line.startswith('| 낱말') and not line.startswith('|---'):
        c = [x.strip() for x in line.strip().strip('|').split('|')]
        if len(c) >= 3: sec3.append((c[0], c[1], c[2]))
def chapter_of(sec): return sec.split('.')[0]
for word, mean, first in sec3:
    if '일반어' in first or '부록' in first: continue
    secs = re.findall(r'\d+(?:\.\d+)?', first)
    if not secs: continue
    minsec = min(secs, key=seckey)
    if '.' not in minsec: minsec = minsec  # chapter-level like '8(도입)'
    ws = [w.strip() for w in re.split(r',', word) if w.strip() and not w.strip().startswith('$')]
    for w in ws:
        w0 = re.sub(r'\(.*?\)', '', w).strip()
        if len(w0) < 2: continue
        hits = [(ch, i, sec) for (ch, i, sec, raw, n) in lines if w0 in raw and sec and not sec.startswith('1.4')]
        early = [h for h in hits if seckey(h[2])[:2] < seckey(minsec)[:2] and h[2] != '']
        if early:
            e = early[0]
            print(f'{w0} | 첫 정의 절 {first} | 앞선 출현 {e[0]}:{e[1]} 절 {e[2]} | 총 앞선 출현 {len(early)}')
# ---------- (3) 5절
print('=== (3) 5절 장별 배정 대조')
sec5 = {}; on = False
for line in ledger:
    if line.startswith('## 5.'): on = True
    elif line.startswith('## 6.'): on = False
    if on and re.match(r'^\| \d+ \|', line):
        c = [x.strip() for x in line.strip().strip('|').split('|')]
        sec5[c[0]] = dict(glyphs=c[1], words=c[2])
# 1.2 정의 절 → 장
exp = collections.defaultdict(set)
for r in rows:
    secs = re.findall(r'\d+\.\d+', r['defsec'])
    for s in secs: exp[s.split('.')[0]].add(r['glyph'])
for ch in sorted(sec5, key=int):
    listed = set(x.strip() for x in sec5[ch]['glyphs'].split(';') if x.strip())
    listed_n = set(norm(x) for x in listed)
    exp_n = set(norm(x) for x in exp.get(ch, set()))
    miss = [x for x in exp.get(ch, set()) if norm(x) not in listed_n]
    extra = [x for x in listed if norm(x) not in exp_n]
    if miss or extra: print(f'장 {ch}: 1.2에는 있으나 5절에 없음 {miss} | 5절에만 있음 {extra}')
# 3절 낱말 → 장
expw = collections.defaultdict(set)
for word, mean, first in sec3:
    if '일반어' in first or first.strip().startswith('부록'): continue
    secs = re.findall(r'\d+(?:\.\d+)?', first)
    if not secs: continue
    minsec = min(secs, key=seckey)
    expw[minsec.split('.')[0]].add(word)
for ch in sorted(sec5, key=int):
    listed = set(x.strip() for x in sec5[ch]['words'].split(';') if x.strip())
    missing = [w for w in expw.get(ch, set()) if w not in listed]
    extra = [w for w in listed if w not in expw.get(ch, set()) and w != '없음']
    if missing or extra: print(f'장 {ch} 낱말: 3절 기준으로 빠짐 {missing} | 5절에만 {extra}')
# ---------- (4) 의존지도 2.1
print('=== (4) 의존지도 2.1 수')
dep = []; on = False
for line in open(os.path.join(B, '의존지도_v2.md'), encoding='utf-8'):
    if line.startswith('## 1.'): on = True
    elif line.startswith('### 1.1'): on = False
    if on and line.startswith('| `{{'):
        c = [x.strip() for x in line.strip().strip('|').split('|')]
        dep.append((c[0].strip('`').strip('{}'), c[5]))
lab_re = re.compile(r'\{\{(\d+:[^}]+)\}\}')
alllabs = set(l for l, _ in dep); cited = set(); head_edges = collections.defaultdict(set); full_edges = collections.defaultdict(set)
for lab, inp in dep:
    parts = inp.split('본문 인용:')
    h = set(lab_re.findall(parts[0])); b = set(lab_re.findall(parts[1])) if len(parts) > 1 else set()
    cited |= h | b; head_edges[lab] |= h; full_edges[lab] |= h | b
print('입력 열 라벨 수', len(cited), '| 장 파일 밖 라벨', sorted(cited - alllabs))
# acyclic check head graph
def has_cycle(g):
    color = {}
    def dfs(u):
        color[u] = 1
        for v in g.get(u, ()):
            if color.get(v) == 1: return True
            if color.get(v) is None and dfs(v): return True
        color[u] = 2; return False
    return any(color.get(u) is None and dfs(u) for u in list(g))
print('머리 선언 그래프 순환:', has_cycle(head_edges))
# SCC count size>=2 in full graph (Tarjan iterative)
sys.setrecursionlimit(10000)
index = {}; low = {}; onst = set(); st = []; sccs = []; idx = [0]
def sc(v):
    index[v] = low[v] = idx[0]; idx[0] += 1; st.append(v); onst.add(v)
    for w in full_edges.get(v, ()):
        if w not in index: sc(w); low[v] = min(low[v], low[w])
        elif w in onst: low[v] = min(low[v], index[w])
    if low[v] == index[v]:
        comp = []
        while True:
            w = st.pop(); onst.discard(w); comp.append(w)
            if w == v: break
        if len(comp) >= 2: sccs.append(sorted(comp))
for v in list(alllabs):
    if v not in index: sc(v)
print('강결합 성분(크기 2 이상) 수', len(sccs))
for s in sccs: print('  ', s)
