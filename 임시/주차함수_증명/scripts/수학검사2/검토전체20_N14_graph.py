# -*- coding: utf-8 -*-
"""N14: 의존지도 2.1의 선언(381개 라벨, 비순환, 강결합 17개)과 구조표 절 제목을 장 파일과 맞춘다."""
import re, sys, io, os, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
ROOT = r"C:\math\임시\주차함수_증명"
SD = os.path.join(ROOT, "scripts", "수학검사2")
heads = json.load(open(os.path.join(SD, "_N14_heads.json"), encoding='utf-8'))
H = {h['label']: h for h in heads}
LAB = re.compile(r'\{\{(\d+:[^}]+)\}\}')
# --- 2.1 from the map's own table
dl = open(os.path.join(ROOT, "의존지도_v2.md"), encoding='utf-8').read().split('\n')
s = dl.index("## 1. 진술별 입력 표"); e = dl.index("### 1.1 뺌·대체된 라벨")
labs_in_inputs = set()
decl = {}; full = {}
for ln in dl[s:e]:
    if not ln.startswith('| `{{'): continue
    c = [x.strip() for x in ln.strip().strip('|').split('|')]
    lab = c[0].strip('`')[2:-2]
    inputs = c[5]
    ls = set(LAB.findall(inputs)); labs_in_inputs |= ls
    if '본문 인용:' in inputs:
        d, b = inputs.split('본문 인용:')
    else:
        d, b = inputs, ''
    decl[lab] = set(LAB.findall(d)); full[lab] = set(LAB.findall(inputs))
print("지도 입력 열의 라벨 수(중복 제외):", len(labs_in_inputs), "| 모두 머리에 있음:", labs_in_inputs <= set(H))
# from chapter heads directly
decl2 = {h['label']: set(h['head_labels']) for h in heads}
full2 = {h['label']: set(h['head_labels']) | set(h['body_labels']) for h in heads}
print("장 파일 기준 입력 라벨 수:", len(set().union(*full2.values())))
# acyclicity of declared graph
def has_cycle(g):
    color = {}
    def dfs(u, stack):
        color[u] = 1
        for v in g.get(u, ()):
            if color.get(v) == 1: return stack + [u, v]
            if color.get(v) is None:
                r = dfs(v, stack + [u])
                if r: return r
        color[u] = 2
        return None
    for u in g:
        if color.get(u) is None:
            r = dfs(u, [])
            if r: return r
    return None
print("선언 그래프 순환(지도 표):", has_cycle(decl))
print("선언 그래프 순환(장 머리):", has_cycle(decl2))
# SCCs of full graph (Tarjan)
def sccs(g):
    index = {}; low = {}; st = []; on = set(); out = []; idx = [0]
    sys.setrecursionlimit(10000)
    def strong(v):
        index[v] = low[v] = idx[0]; idx[0] += 1; st.append(v); on.add(v)
        for w in g.get(v, ()):
            if w not in index:
                strong(w); low[v] = min(low[v], low[w])
            elif w in on:
                low[v] = min(low[v], index[w])
        if low[v] == index[v]:
            comp = []
            while True:
                w = st.pop(); on.discard(w); comp.append(w)
                if w == v: break
            out.append(comp)
    for v in list(g):
        if v not in index: strong(v)
    return [c for c in out if len(c) > 1]
S1 = sccs(full); S2 = sccs(full2)
print("강결합 성분(크기≥2) 수 — 지도 표:", len(S1), "| 장 파일:", len(S2))
sizes1 = sorted(len(c) for c in S1); sizes2 = sorted(len(c) for c in S2)
print("성분 크기 — 지도 표:", sizes1, "| 장 파일:", sizes2)
# compare with listed SCCs in 2.1 text
txt = '\n'.join(dl)
m = re.search(r'본문 인용 그래프의 상호 인용 묶음: (.*)', txt)
listed = [set(LAB.findall(x)) for x in m.group(1).split('}; {')] if m else []
print("2.1에 적힌 묶음 수:", len(listed), "크기:", sorted(len(x) for x in listed))
setS2 = [frozenset(c) for c in S2]
for L in listed:
    if frozenset(L) not in setS2:
        print("2.1 묶음이 장 파일 성분과 다름:", sorted(L))
for c in setS2:
    if c not in [frozenset(L) for L in listed]:
        print("장 파일 성분이 2.1에 없음:", sorted(c))

# --- 구조표 절 제목 vs 장 파일 ###
print("\n=== 구조표 절 제목 ===")
CH = ["장1","장2","장3","장4","장5A","장5B","장6","장7A","장7B","장8","장9","장10","장11"]
secs = []
for ch in CH:
    for ln in open(os.path.join(ROOT, "장v2", ch + ".md"), encoding='utf-8'):
        m = re.match(r'^(#{2,4}) (.*)', ln)
        if m: secs.append((ch, m.group(1), m.group(2).strip()))
with open(os.path.join(SD, "_N14_sections.txt"), 'w', encoding='utf-8') as f:
    for ch, lv, t in secs: f.write(f"{ch}\t{lv}\t{t}\n")
st = open(os.path.join(ROOT, "구조표_v2.md"), encoding='utf-8').read().split('\n')
rows = [ln for ln in st if re.match(r'^\| \d+\.\d+ ', ln)]
sec_titles = {t.split(' ',1)[0]: t for ch, lv, t in secs if lv == '###'}
for r in rows:
    cell = r.strip('|').split('|')[0].strip()
    num = cell.split(' ',1)[0]
    title = cell.split(' ',1)[1] if ' ' in cell else ''
    title_main = re.sub(r'\(.*$', '', title).strip()
    if num not in sec_titles:
        print("구조표 절이 장 파일에 없음:", cell[:80]); continue
    chap_title = sec_titles[num].split(' ',1)[1] if ' ' in sec_titles[num] else ''
    if title_main != chap_title:
        print(f"제목 다름 {num}: 구조표 「{title_main}」 | 장 「{chap_title}」")
print("장 파일 ### 절:", [t for ch, lv, t in secs if lv == '###' and t.split(' ')[0] not in {c.strip('|').split('|')[0].strip().split(' ')[0] for c in rows}])
