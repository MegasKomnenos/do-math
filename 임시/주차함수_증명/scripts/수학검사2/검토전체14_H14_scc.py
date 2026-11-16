# H14: 의존지도 2.1절의 수(입력 라벨 383개, 머리 그래프 비순환, 본문 그래프 강결합 성분 16개)를 다시 센다.
import re, os, sys
sys.setrecursionlimit(10000)
root = r"C:\math\임시\주차함수_증명\장v2"
files = ["장1.md","장2.md","장3.md","장4.md","장5A.md","장5B.md","장6.md","장7A.md","장7B.md","장8.md","장9.md","장10.md","장11.md"]
LABEL_RE = re.compile(r"\{\{(\d+):([A-Za-z][A-Za-z0-9\-]*)\}\}")
HEAD_RE = re.compile(r"^\*\*(정의|정리|명제|보조정리|따름정리) \{\{(\d+):([A-Za-z][A-Za-z0-9\-]*)\}\}(?= \(| \[|\.\*\*|\*\*)")
DEFER_RE = re.compile(r"^\*\*(정의|정리|명제|보조정리|따름정리) \{\{(\d+):([A-Za-z][A-Za-z0-9\-]*)\}\}의 증명\.\*\*")
stmts = {}; defers = []
for f in files:
    lines = open(os.path.join(root, f), encoding="utf-8").read().split("\n")
    marks = []
    for i, ln in enumerate(lines):
        d = DEFER_RE.match(ln)
        if d: marks.append((i, "defer", f"{d.group(2)}:{d.group(3)}")); continue
        h = HEAD_RE.match(ln)
        if h: marks.append((i, "head", f"{h.group(2)}:{h.group(3)}"))
    for j, (i, kind, key) in enumerate(marks):
        end = marks[j+1][0] if j+1 < len(marks) else len(lines)
        body = lines[i+1:end]
        if kind == "head":
            stmts[key] = dict(head=set(f"{a}:{b}" for a, b in LABEL_RE.findall(lines[i])) - {key},
                              body=set(f"{a}:{b}" for a, b in LABEL_RE.findall("\n".join(body))) - {key})
        else:
            defers.append((key, [lines[i]] + body))
for key, bl in defers:
    stmts[key]["body"].update(set(f"{a}:{b}" for a, b in LABEL_RE.findall("\n".join(bl))) - {key})
cur = set(stmts)
allinputs = set()
for k, s in stmts.items():
    allinputs |= (s["head"] | s["body"]) & cur
print("진술", len(stmts), "입력 라벨(중복 제외)", len(allinputs))
# 머리 그래프 순환
def sccs(graph):
    index = {}; low = {}; st = []; on = set(); out = []; c = [0]
    def strong(v):
        index[v] = low[v] = c[0]; c[0] += 1; st.append(v); on.add(v)
        for w in graph.get(v, ()):
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
hg = {k: [x for x in s["head"] if x in cur] for k, s in stmts.items()}
hc = [c for c in sccs(hg) if len(c) > 1]
selfloops = [k for k, s in stmts.items() if k in s["head"]]
print("머리 그래프 크기2 이상 SCC", len(hc), "자기 고리", selfloops)
bg = {k: [x for x in (s["head"] | s["body"]) if x in cur] for k, s in stmts.items()}
bc = [sorted(c) for c in sccs(bg) if len(c) > 1]
print("본문 그래프 크기2 이상 SCC", len(bc))
for c in sorted(bc, key=len): print("  ", len(c), c[:12], "..." if len(c) > 12 else "")
