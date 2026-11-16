# -*- coding: utf-8 -*-
"""M14: check 의존지도 1절 문헌/부록D columns vs 장11.md tables; 뺌 labels absent; SCC claims."""
import re, sys, io, json
from pathlib import Path
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
ROOT = Path(r"C:\math\임시\주차함수_증명")
heads = json.load(open(ROOT/"scripts"/"수학검사2"/"검토전체19_M14_heads.json", encoding="utf-8"))
hl = {h["label"]: h for h in heads}
LAB = re.compile(r"\{\{\d+:[^}]+\}\}")
out = []

dep = {}
in1 = False
for line in (ROOT/"의존지도_v2.md").read_text(encoding="utf-8").splitlines():
    if line.startswith("## 1."): in1 = True; continue
    if line.startswith("### 1.1"): in1 = False
    if in1 and line.startswith("| `{{"):
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        dep[cells[0].strip("`")] = cells

# ---- 장11 tables
t11 = (ROOT/"장v2"/"장11.md").read_text(encoding="utf-8").splitlines()
sec = None
rows112 = []; rows114 = []
for line in t11:
    m = re.match(r"^###\s+(11\.\d)", line)
    if m: sec = m.group(1)
    if line.startswith("|") and not re.match(r"^\|\s*-", line):
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if sec == "11.2": rows112.append(cells)
        if sec == "11.4": rows114.append(cells)
out.append("11.2 rows %d (incl header), 11.4 rows %d" % (len(rows112), len(rows114)))
out.append("11.2 header: " + " | ".join(rows112[0]))
out.append("11.4 header: " + " | ".join(rows114[0]))

# 11.2: find D label, 확인하는 진술 labels, 산술 등급
d_by_label = {}
for c in rows112[1:]:
    txt = " | ".join(c)
    dl = re.findall(r"\{\{D:[^}]+\}\}", c[0])
    if not dl: continue
    dlab = dl[0]
    for L in set(LAB.findall(c[1])):
        d_by_label.setdefault(L, set()).add(dlab)
# 11.4: 문헌 rows: find labels in "쓰인 자리" column -> need to locate column index
hdr = rows114[0]
out.append("11.4 columns: %s" % hdr)
lit_by_label = {}
for c in rows114[1:]:
    txt = " | ".join(c)
    for L in set(LAB.findall(txt)):
        lit_by_label.setdefault(L, set()).add(c[0][:40])

out.append("== 부록 D 열 비교(의존지도 vs 11.2 현행)")
for lab, c in dep.items():
    col = c[8]
    mapped = set(re.findall(r"\{\{D:[^}]+\}\}", col))
    actual = d_by_label.get(lab, set())
    if mapped != actual:
        out.append("  %s: 지도=%s 11.2=%s" % (lab, sorted(mapped), sorted(actual)))
out.append("== 문헌 열 비교(의존지도가 '—'인데 11.4가 라벨을 드는 경우, 또는 반대)")
for lab, c in dep.items():
    col = c[7]
    has = col != "—"
    actual = lit_by_label.get(lab, set())
    if has and not actual: out.append("  %s: 지도 문헌=%r / 11.4에 없음" % (lab, col[:80]))
    if (not has) and actual: out.append("  %s: 지도 '—' / 11.4=%s" % (lab, sorted(actual)))
# 11.4 names present in 지도 column?
out.append("== 문헌 열의 저자명이 11.4 첫 열에 있는가")
first_col = [c[0] for c in rows114[1:]]
for lab, c in dep.items():
    col = c[7]
    if col == "—": continue
    for part in re.split(r";\s*", col):
        name = part.split("(")[0].strip()
        if not any(name.split(",")[0].split()[0] in fc for fc in first_col):
            out.append("  %s: %r not in 11.4 first col" % (lab, name))

# ---- 뺌 labels absent from 장 files
removed = []
in11 = False
for line in (ROOT/"의존지도_v2.md").read_text(encoding="utf-8").splitlines():
    if line.startswith("### 1.1"): in11 = True; continue
    if line.startswith("## 2."): in11 = False
    if in11 and line.startswith("| `{{"):
        removed.append(line.split("`")[1])
out.append("== 1.1절 뺌 라벨 %d개 가운데 장 파일(장·부록)에 나타나는 것" % len(removed))
alltext = {}
for p in sorted((ROOT/"장v2").glob("*.md")):
    alltext[p.name] = p.read_text(encoding="utf-8")
for r in removed:
    for fn, t in alltext.items():
        if r in t:
            for i, l in enumerate(t.splitlines(), 1):
                if r in l: out.append("  %s %s:%d %s" % (r, fn, i, l[:100]))
# labels cited anywhere in 장v2 that are not heads
out.append("== 장·부록 파일이 인용하는 라벨 가운데 머리가 없는 것(D: 제외)")
cited = {}
for fn, t in alltext.items():
    for i, l in enumerate(t.splitlines(), 1):
        for L in LAB.findall(l):
            if L.startswith("{{D:"): continue
            if L not in hl: cited.setdefault(L, []).append("%s:%d" % (fn, i))
for L, locs in cited.items(): out.append("  %s %s" % (L, locs[:5]))

# ---- SCC / acyclic check of head-declared graph; count unique labels in input column
import itertools
uniq = set()
G_head = {}; G_all = {}
for lab, c in dep.items():
    col = c[5]
    labs = set(LAB.findall(col))
    uniq |= labs
    before = col.split("본문 인용:")[0]
    G_head[lab] = set(LAB.findall(before)) if before.strip() not in ("—","") else set()
    G_all[lab] = labs
out.append("== 2.1절 주장 검산: 입력 열 라벨(중복 제외)=%d (지도 주장 381); 머리 없는 것=%s" % (len(uniq), sorted(uniq - set(hl))))
def tarjan(G):
    idx = {}; low = {}; st = []; on = set(); res = []; c = [0]
    sys.setrecursionlimit(10000)
    def sc(v):
        idx[v] = low[v] = c[0]; c[0] += 1; st.append(v); on.add(v)
        for w in G.get(v, ()):
            if w not in G: continue
            if w not in idx: sc(w); low[v] = min(low[v], low[w])
            elif w in on: low[v] = min(low[v], idx[w])
        if low[v] == idx[v]:
            comp = []
            while True:
                w = st.pop(); on.discard(w); comp.append(w)
                if w == v: break
            res.append(comp)
    for v in G:
        if v not in idx: sc(v)
    return res
sh = [c for c in tarjan(G_head) if len(c) > 1]
sa = [c for c in tarjan(G_all) if len(c) > 1]
out.append("머리 선언 그래프 순환 성분: %d (지도 주장 0); 본문 포함 SCC(크기2+): %d (지도 주장 17)" % (len(sh), len(sa)))
# self-loop check
self_loops = [l for l in G_all if l in G_all[l]]
out.append("자기 인용 라벨: %s" % self_loops)
(ROOT/"scripts"/"수학검사2"/"검토전체19_M14_dep11_out.txt").write_text("\n".join(out), encoding="utf-8")
print("\n".join(out))
