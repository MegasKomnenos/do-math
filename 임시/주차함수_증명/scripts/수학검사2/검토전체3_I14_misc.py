# -*- coding: utf-8 -*-
"""I14: 여유 글자 재검(1장 정의 기호만), 의존지도 2.1 수치 재계산, 몇 자리 문맥."""
import re, io, sys, os, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
ROOT = r"C:/math/임시/주차함수_증명"
L = open(os.path.join(ROOT,'장부_v2.md'),encoding='utf-8').read().split('\n')
files = {'1':['장1'],'2':['장2'],'3':['장3'],'4':['장4'],'5':['장5A','장5B'],'6':['장6'],'7':['장7A','장7B'],'8':['장8'],'9':['장9'],'10':['장10'],'11':['장11']}
B = chr(92)
def family(g):
    g = g.strip().strip('$')
    m = re.match(r'^\\(mathcal|mathfrak|mathsf|mathrm|mathbb)\s*(\{[^}]*\}|[A-Za-z])', g)
    if m: return (m.group(1), m.group(2).strip('{}'))
    m = re.match(r'^\\(bar|hat|tilde)\s*(\{[^}]*\}|[A-Za-z])', g)
    if m:
        inner = m.group(2).strip('{}')
        return family(inner) if inner.startswith(B) else ('italic', inner)
    m = re.match(r'^(\\[A-Za-z]+|[A-Za-z])', g)
    if m: return ('italic', m.group(1))
    return None
rows12 = []
for i in range(49,342):
    l = L[i-1]
    if not (l.startswith('| $') or l.startswith('| (')): continue
    rows12.append((i,[c.strip() for c in l.strip().strip('|').split(' | ')]))
used = {str(c):set() for c in range(1,12)}
ch1 = set()
for i,c in rows12:
    glyphs = [g for gl in re.findall(r'\$([^$]+)\$', c[0]) for g in re.split(r',\s*(?=[\\A-Za-z(])', gl)]
    fams = {family(g) for g in glyphs if family(g)}
    chs = set(files.keys()) if '전 장' in c[4] else {x.strip() for x in c[4].split(',') if x.strip().isdigit()}
    defs = re.findall(r'\d+\.\d+', c[3])
    for s in defs: chs.add(s.split('.')[0])
    if any(s.startswith('1.') for s in defs): ch1 |= fams
    for ch in chs:
        if ch in used: used[ch] |= fams
vars11 = {('italic',x) for x in ['n','m','t','N','k','\\ell','y','Y','i','j','u','v','r','\\nu','d','q']}
print("=== 여유 글자 충돌(그 장 전역 + 1장 정의 전역 + 1.1 변수)")
for i in range(1181,1192):
    l = L[i-1]
    m = re.match(r'^\| (\d+) \| [^|]* \| [^|]* \| ([^|]*) \|', l)
    if not m: continue
    ch = m.group(1)
    free = [family(g) for g in re.findall(r'\$([^$]+)\$', m.group(2))]
    bad = [f for f in free if f in used[ch] or f in ch1 or f in vars11]
    print(f"  장{ch}: {bad if bad else '없음'}")
print("1장 정의 전역 가족:", sorted(ch1))

print("\n=== 의존지도 2.1 수치 재계산")
D = open(os.path.join(ROOT,'의존지도_v2.md'),encoding='utf-8').read().split('\n')
rows = {}
for l in D:
    m = re.match(r'^\| `\{\{(\d+:[^}]+)\}\}` \|(.*)\|\s*$', l)
    if not m: continue
    if l.count('|') < 10: continue
    cells = [c.strip() for c in m.group(2).split(' | ')]
    if len(cells) < 6: continue
    rows[m.group(1)] = cells
cited = set(); head_edges = {}; all_edges = {}
for lab, c in rows.items():
    inp = c[4]
    hp, _, bp = inp.partition('본문 인용:')
    h = set(re.findall(r'\{\{(\d+:[^}]+)\}\}', hp)); b = set(re.findall(r'\{\{(\d+:[^}]+)\}\}', bp))
    cited |= h | b
    head_edges[lab] = h; all_edges[lab] = h | b
print(" 표 행 수:", len(rows), "| 입력 열의 라벨(중복 제외):", len(cited), "| 머리 없는 인용:", sorted(cited-set(rows)))
# SCC (Tarjan) on all_edges restricted to nodes
sys.setrecursionlimit(10000)
def sccs(graph):
    index = {}; low = {}; st = []; on = set(); out = []; idx = [0]
    def strong(v):
        index[v] = low[v] = idx[0]; idx[0] += 1; st.append(v); on.add(v)
        for w in graph.get(v, ()):
            if w not in graph: continue
            if w not in index: strong(w); low[v] = min(low[v], low[w])
            elif w in on: low[v] = min(low[v], index[w])
        if low[v] == index[v]:
            comp = []
            while True:
                w = st.pop(); on.discard(w); comp.append(w)
                if w == v: break
            out.append(comp)
    for v in graph:
        if v not in index: strong(v)
    return out
hs = [c for c in sccs(head_edges) if len(c) > 1]
al = [c for c in sccs(all_edges) if len(c) > 1]
print(" 머리 선언 그래프 순환(크기>1):", len(hs), "| 본문 인용 포함 그래프 강결합 성분(크기>1):", len(al))
for comp in al: print("   ", sorted(comp))

print("\n=== 문맥")
def ctx(f, pat, n=3, w=90):
    rx = re.compile(pat)
    for i,l in enumerate(open(os.path.join(ROOT,'장v2',f+'.md'),encoding='utf-8'),1):
        m = rx.search(l)
        if m:
            s=max(0,m.start()-w); e=min(len(l),m.end()+w); print(f"  {f}:{i}: …{l[s:e]}…"); n-=1
            if n==0: break
print("-- 영차 모멘트"); ctx('장9','영차')
print("-- 7A supermultiplicative 증명 (나)");
for i,l in enumerate(open(os.path.join(ROOT,'장v2','장7A.md'),encoding='utf-8'),1):
    if i==362: print(' ', l[:1400])
print("-- 장2 164행 앞 b^T, b^circ, A^c")
for i,l in enumerate(open(os.path.join(ROOT,'장v2','장2.md'),encoding='utf-8'),1):
    if i<164 and (re.search(r'b\^\{?T', l) or (B+'circ') in l and 'b^' in l or re.search(r'A\^\{?c\}?_', l)):
        print(f"  2:{i}: {l[:220]}")
print("-- 장부 1.3 행397 mathrm w_m 등록?")
print('  ', 'mathrm w_m' in L[396].replace(' ',''), '|', [m.start() for m in re.finditer(r'mathrm w', L[396])][:3])
H = json.load(open(os.path.join(ROOT,'scripts','수학검사2','_I14_heads.json'),encoding='utf-8'))
print("-- 9장 라벨 번호/절")
for h in H:
    lab = h['label']
    if lab in ('9:old-7-46','10:old-8-37','6:old-7-13') or (lab.startswith('9:old-7-') and lab.split('-')[-1].isdigit() and int(lab.split('-')[-1])<=17):
        print('  ', lab, h['num'], h['sec'])
