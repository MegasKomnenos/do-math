# -*- coding: utf-8 -*-
"""V4: 의존지도 1절 407행의 지위·기록 열과 부록 D 열을 장 파일 머리와 기계 대조한다. 2.1절 수치도 다시 센다. 읽기 전용."""
import io, os, re, glob
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
HEAD = re.compile(r"^\*\*(정리|명제|보조정리|따름정리|정의) \{\{(\d+:[A-Za-z][A-Za-z0-9\-]*)\}\}(?: \((.*?)\))? \[([^\]]*)\]\.\*\*")
heads = {}
for p in sorted(glob.glob(os.path.join(ROOT, "장v2", "장*.md"))):
    for l in io.open(p, encoding="utf-8").read().split("\n"):
        m = re.match(r"^\*\*(정리|명제|보조정리|따름정리|정의) \{\{(\d+:[A-Za-z][A-Za-z0-9\-]*)\}\}", l)
        if m:
            # 지위 괄호: 마지막 '[...]' 직전 '.**'
            mm = re.search(r"\[([^\[\]]*)\]\.\*\*", l)
            heads[m.group(2)] = (m.group(1), mm.group(1) if mm else None, l)
print("머리 수", len(heads))
dm = io.open(os.path.join(ROOT, "의존지도_v2.md"), encoding="utf-8").read()
sec1 = dm[dm.index("## 1. 진술별 입력 표"):dm.index("### 1.1")]
rows = [l for l in sec1.split("\n") if l.startswith("| `{{")]
print("1절 행 수", len(rows))
bad = []; labels_in_input = set(); n_input_cells = 0
for l in rows:
    c = [x.strip() for x in l.strip().strip("|").split(" | ")]
    lab = re.search(r"\{\{([^}]+)\}\}", c[0]).group(1)
    if lab not in heads:
        bad.append(("머리 없음", lab)); continue
    kind, status, hl = heads[lab]
    if status is None:
        bad.append(("지위 괄호 없음", lab)); continue
    st, _, ids = status.partition(";")
    st = st.strip(); ids = [x.strip() for x in ids.split(",") if x.strip()]
    if kind == "정의":
        if c[4] != "정의": bad.append(("정의 지위", lab, c[4]))
    elif c[4] != st:
        bad.append(("지위 불일치", lab, c[4], st))
    # 기록 열
    rec = c[6]
    rec_ids = re.findall(r"r[0-9a-f]{7}", rec)
    if sorted(set(ids)) != sorted(set(rec_ids)):
        bad.append(("기록 불일치", lab, ids, rec_ids))
    # 입력 라벨
    for x in re.findall(r"\{\{([^}]+)\}\}", c[5]):
        labels_in_input.add(x)
    # 부록 D 열: 머리의 계산 표지와 대조
    hasD = c[8] != "없음"
    comp = ("계산 증거" in st) or ("계산 보조" in st)
    if comp and not hasD: bad.append(("계산 표지 있으나 부록 D 열 없음", lab, st, c[8]))
    if hasD and not comp: bad.append(("부록 D 열 있으나 계산 표지 없음", lab, st, c[8]))
print("입력 열 라벨(중복 제외)", len(labels_in_input), "그중 머리 없는 것", [x for x in labels_in_input if x not in heads])
print("불일치", len(bad))
for b in bad: print("  ", b)
# 1절에 없는 머리
missing = [k for k in heads if k not in {re.search(r"\{\{([^}]+)\}\}", l).group(1) for l in rows}]
print("1절에 없는 머리", missing)
# 지운 라벨이 1절·비고에 남았나
REMOVED = ["5:old-5-16","5:old-5-17","5:old-5-39","5:dawson-facts","5:arc-leading","5:gauss-moments","5:old-5-40","5:old-5-41","5:old-5-23","5:old-5-24","5:old-5-25","2:old-2-23","lemma-H-interval","lemma-V-coefficients"]
for i, l in enumerate(sec1.split("\n")):
    for r in REMOVED:
        if r in l:
            print("1절 잔존:", r, "|", l[:80], "...", re.findall(r".{30}" + re.escape(r) + r".{40}", l)[:1])
