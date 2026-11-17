# -*- coding: utf-8 -*-
# R13: 의존지도 2.1절의 주장(선언 의존 그래프 비순환, 본문 인용 그래프의 상호 인용 묶음 13개)과
#      1절 「문헌」·「첫 판 번호」 열을 장 파일·10.3절·장부 4절에서 다시 세어 맞댄다.
import re, sys, io, collections
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', newline=chr(10))
sys.setrecursionlimit(10000)
BASE = r'C:/math/임시/주차함수_증명/'
LAB = re.compile(r'\{\{(\d+:[^}]+)\}\}')
rows = {}; order = []
for ln, line in enumerate(open(BASE + '의존지도_v2.md', encoding='utf-8'), 1):
    if ln > 283: break
    if not line.startswith('| `{{'): continue
    c = [x.strip() for x in line.strip().strip('|').split(' | ')]
    lab = c[0].strip('`')[2:-2]
    rows[lab] = (ln, c); order.append(lab)
decl = {}; full = {}
for lab, (ln, c) in rows.items():
    status = c[4]; inputs = c[5]
    decl[lab] = [x for x in LAB.findall(status) if x != lab]
    full[lab] = [x for x in LAB.findall(inputs) if x != lab]
def scc(g):
    idx = {}; low = {}; st = []; on = set(); out = []; n = [0]
    def dfs(v):
        idx[v] = low[v] = n[0]; n[0] += 1; st.append(v); on.add(v)
        for w in g.get(v, []):
            if w not in idx:
                dfs(w); low[v] = min(low[v], low[w])
            elif w in on: low[v] = min(low[v], idx[w])
        if low[v] == idx[v]:
            comp = []
            while True:
                w = st.pop(); on.discard(w); comp.append(w)
                if w == v: break
            out.append(comp)
    for v in g:
        if v not in idx: dfs(v)
    return out
c1 = [c for c in scc(decl) if len(c) > 1]
print('선언 의존 그래프: 크기>=2 강결합 성분', len(c1), c1[:3])
# 선언 의존이 앞 진술만 가리키는가(뒤 진술을 가리키는 선언)
pos = {l: i for i, l in enumerate(order)}
fwd = [(l, d) for l in order for d in decl[l] if pos[d] > pos[l]]
print('뒤 진술에 의존을 선언한 머리', len(fwd))
for x in fwd: print('   ', x)
c2 = [sorted(c, key=lambda l: pos[l]) for c in scc(full) if len(c) > 1]
print('본문 인용 그래프: 묶음', len(c2), '크기', sorted(len(c) for c in c2))
# 지도 2.1절의 묶음 목록과 대조
txt = open(BASE + '의존지도_v2.md', encoding='utf-8').read().split('\n')
line = [l for l in txt if l.startswith('본문 인용 그래프의 상호 인용 묶음')][0]
groups = [set(LAB.findall(g)) for g in re.findall(r'\{(`\{\{.*?\}\}`)\}(?:;|$)', line)]
print('지도에 적힌 묶음', len(groups), sorted(len(g) for g in groups))
mine = [set(c) for c in c2]
for g in groups:
    if g not in mine: print('  지도 묶음이 계산과 다름:', sorted(g)[:6])
for g in mine:
    if g not in groups: print('  계산 묶음이 지도에 없음:', sorted(g)[:6])
# 문헌 열
lit = collections.defaultdict(list)
for l in open(BASE + '장v2/장10.md', encoding='utf-8'):
    if not l.startswith('|'): continue
    c = [x.strip() for x in l.strip().strip('|').split(' | ')]
    if len(c) == 3 and not c[0].startswith('---') and not c[0].startswith('문헌'):
        for lab in dict.fromkeys(LAB.findall(c[2])):
            lit[lab].append((c[0], c[1]))
prev_author = None
bad = 0
for lab in order:
    ln, c = rows[lab]
    cell = c[7]
    exp = lit.get(lab, [])
    if cell == '—':
        if exp and not all('Knuth' in a for a, b in exp): print('LIT 없음', ln, lab, [a[:20] for a, b in exp]); bad += 1
        continue
    # 지도 칸에 10.3의 '내용' 문자열이 그대로 들어 있는가
    for a, b in exp:
        if 'Knuth' in a and '갈고리' in b: continue
        if b not in cell:
            print('LIT 내용 다름', ln, lab, '\n   10.3:', b[:150], '\n   지도:', cell[:200]); bad += 1
    n_map = cell.count('); ') + 1
    n_exp = len([1 for a, b in exp if not ('Knuth' in a and '갈고리' in b)])
    if n_map != n_exp: print('LIT 개수', ln, lab, n_map, n_exp); bad += 1
print('문헌 열 어긋남', bad)
