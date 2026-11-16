# -*- coding: utf-8 -*-
"""11.2절 표의 각 행을 부록 D 항목과 대조한다 (N11 검토 보조)."""
import re, glob, io, sys, os
ROOT = r"C:\math\임시\주차함수_증명"
out = io.open(os.path.join(ROOT, r"대조v2\수학검사2\_N11_D표대조_out.txt"), "w", encoding="utf-8")
def P(*a):
    print(*a, file=out)

# --- 부록 D 항목 파싱
items = {}
order = []
for f in sorted(glob.glob(os.path.join(ROOT, r"장v2\부록D_장*.md"))):
    txt = io.open(f, encoding="utf-8").read()
    blocks = re.split(r"\n(?=### D\.\{\{D:)", "\n" + txt)
    for b in blocks:
        m = re.match(r"\n?### D\.\{\{D:([^}]+)\}\}\s*(.*)", b)
        if not m:
            continue
        lab = m.group(1)
        head = m.group(2).split("\n")[0]
        d = {"file": os.path.basename(f), "head": head}
        for key in ["확인하는 진술", "산술 등급", "독립 재계산", "자료", "출처", "범위", "결과"]:
            mm = re.search(r"\*\*" + key + r"\.\*\*\s*(.*)", b)
            d[key] = mm.group(1).strip() if mm else None
        items[lab] = d
        order.append(lab)

# --- 11.2 표 파싱
t11 = io.open(os.path.join(ROOT, r"장v2\장11.md"), encoding="utf-8").read().split("\n")
rows = []
for ln in t11:
    if ln.startswith("| 부록 D.{{D:"):
        cells = [c.strip() for c in ln.strip().strip("|").split(" | ")]
        rows.append(cells)
P("부록 D 항목 수:", len(order), " 11.2 행 수:", len(rows))
row_labels = [re.match(r"부록 D\.\{\{D:([^}]+)\}\}", r[0]).group(1) for r in rows]
P("순서 비교 (D 순서 vs 표 순서):")
for a, b in zip(order, row_labels):
    if a != b:
        P("  순서 다름:", a, "|", b)
P("  D에만:", set(order) - set(row_labels), " 표에만:", set(row_labels) - set(order))

LABEL = re.compile(r"(정리|명제|보조정리|따름정리|정의)\s+\{\{(\d+[AB]?):([^}]+)\}\}")
def labels_in(s):
    return LABEL.findall(s or "")

for r in rows:
    lab = re.match(r"부록 D\.\{\{D:([^}]+)\}\}", r[0]).group(1)
    d = items.get(lab)
    if not d:
        P("\n==", lab, ": 부록 D 항목 없음"); continue
    P("\n==", lab, "(", d["file"], ")")
    # 1) 확인하는 진술: 표 열 2 vs D 머리 괄호 안 라벨
    head_labels = labels_in(d["head"])
    tbl_labels = labels_in(r[1])
    if head_labels != tbl_labels:
        P("  [진술] D머리:", head_labels, "\n          표:", tbl_labels)
    # 2) 산술 등급: 표 열 3 vs D 산술 등급 줄의 첫 등급
    P("  [등급] 표:", r[2], " || D줄:", (d["산술 등급"] or "")[:160])
    # 3) 독립 재계산: 표 열 5+6 vs D 줄
    dline = d["독립 재계산"] or ""
    tline = (r[4] + " " + r[5]).strip()
    norm = lambda s: re.sub(r"\s+", " ", s.replace("「재계산」 열의 꺾쇠 괄호", "이 문단 머리의 꺾쇠 괄호")).strip()
    if norm(dline) != norm(tline):
        # 차이 위치 표시
        a, b = norm(dline), norm(tline)
        i = 0
        while i < min(len(a), len(b)) and a[i] == b[i]:
            i += 1
        P("  [재계산] 다름 @", i)
        P("     D : ...", a[max(0, i-60):i+200])
        P("     표: ...", b[max(0, i-60):i+200])
    else:
        P("  [재계산] 같음")
    P("  [놓인 곳] 표:", r[3], " 확인하는 진술 D:", (d["확인하는 진술"] or "")[:100])
out.close()
