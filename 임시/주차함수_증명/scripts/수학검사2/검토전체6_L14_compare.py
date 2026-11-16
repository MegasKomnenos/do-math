# -*- coding: utf-8 -*-
"""L14: 대응표·의존지도 1절·장부 4절/5절을 장 파일 색인과 맞춘다.
사용: python -I 검토전체6_L14_compare.py
"""
import re, json
from pathlib import Path

ROOT = Path(r"C:\math\임시\주차함수_증명")
IDX = json.loads((ROOT / "scripts/수학검사2/_검토전체6_L14_index.json").read_text(encoding="utf-8"))
heads = {h["label"]: h for h in IDX["heads"]}
order = [h["label"] for h in IDX["heads"]]

def rows(path, ncols_min=3):
    out = []
    for i, ln in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if ln.startswith("|") and not re.match(r"^\|\s*-+", ln):
            cells = [c.strip() for c in ln.strip().strip("|").split("|")]
            if len(cells) >= ncols_min:
                out.append((i, cells))
    return out

def norm_status(s):
    if s is None:
        return None
    return re.sub(r"\s+", " ", s.strip())

print("=== A. 대응표 vs 장 파일 ===")
mp = rows(ROOT / "대조v2/라벨_번호_대응표_1114.md")
mp_labels = {}
removed = []
for i, c in mp:
    if c[0].startswith("`{{"):
        lab = c[0].strip("`")
        if lab == "라벨":
            continue
        mp_labels[lab] = (i, c)
for lab, (i, c) in mp_labels.items():
    kind, name, cur, old, sec = c[1], c[2], c[3], c[4], c[5] if len(c) > 5 else ""
    h = heads.get(lab)
    if cur == "뺌" or "뺌" in cur:
        if h:
            print(f"  [대응표 {i}] {lab} 「뺌」인데 장 파일에 머리 있음: {h['file']}:{h['line']}")
        removed.append(lab)
        continue
    if not h:
        print(f"  [대응표 {i}] {lab} 장 파일에 머리 없음 (표: {kind} {cur})")
        continue
    if h["number"] != cur:
        print(f"  [대응표 {i}] {lab} 번호 불일치: 표 {cur} / 현행 {h['number']} ({h['file']}:{h['line']})")
    if h["kind"] != kind:
        print(f"  [대응표 {i}] {lab} 종류 불일치: 표 {kind} / 현행 {h['kind']}")
    if h["sec"] != sec:
        print(f"  [대응표 {i}] {lab} 절 불일치: 표 {sec} / 현행 {h['sec']}")
    # 이름 비교(머리 괄호)
    t = h["title"]
    if name == "—":
        if t:
            print(f"  [대응표 {i}] {lab} 표 이름 「—」인데 머리에 이름 있음: ({t})")
    else:
        if (t or "") != name:
            print(f"  [대응표 {i}] {lab} 이름 다름:\n      표: {name}\n      머리: {t}")
missing = [l for l in order if l not in mp_labels]
print("  대응표에 없는 현행 머리:", missing)
print("  대응표 행 수(라벨):", len(mp_labels), " 뺌:", len(removed), " 현행 머리:", len(order))

print("\n=== B. 의존지도 1절 vs 장 파일 ===")
dm = rows(ROOT / "의존지도_v2.md", 8)
dm_labels = {}
for i, c in dm:
    if c[0].startswith("`{{") and len(c) >= 10:
        lab = c[0].strip("`")
        dm_labels[lab] = (i, c)
for lab, (i, c) in dm_labels.items():
    sec, firstno, gist, status, inputs = c[1], c[2], c[3], c[4], c[5]
    h = heads.get(lab)
    if not h:
        print(f"  [의존지도 {i}] {lab} 장 파일에 머리 없음")
        continue
    if h["sec"] != sec:
        print(f"  [의존지도 {i}] {lab} 절 불일치: 표 {sec} / 현행 {h['sec']}")
    # 지위: 머리 대괄호의 ; 앞
    st = h["status"] or ""
    st_front = st.split(";")[0].strip()
    st_front = re.sub(r"\s+", " ", st_front)
    tbl = re.sub(r"\s+", " ", status.replace("`", ""))
    if h["kind"] == "정의":
        exp = "정의"
        if tbl != exp and tbl != st_front:
            print(f"  [의존지도 {i}] {lab} 정의 지위 칸: 표 「{tbl}」 / 머리 「{st_front}」")
    elif tbl != st_front:
        print(f"  [의존지도 {i}] {lab} 지위 불일치:\n      표: {tbl}\n      머리: {st_front}")
    # 요지(이름)
    t = h["title"] or ""
    if t and gist != t:
        print(f"  [의존지도 {i}] {lab} 요지≠머리 이름:\n      표: {gist}\n      머리: {t}")
    # 머리 줄 인용 라벨 vs 입력 열의 「본문 인용:」 앞
    head_labels = re.findall(r"\{\{\d+:[^}]+\}\}", h["rest"])
    head_labels = [l for l in head_labels if l != lab]
    inp_head = inputs.split("본문 인용:")[0]
    inp_labels = re.findall(r"\{\{\d+:[^}]+\}\}", inp_head)
    if sorted(set(head_labels)) != sorted(set(inp_labels)):
        print(f"  [의존지도 {i}] {lab} 머리 인용 라벨 불일치:\n      표: {sorted(set(inp_labels))}\n      머리: {sorted(set(head_labels))}")
missing = [l for l in order if l not in dm_labels]
print("  의존지도에 없는 현행 머리:", missing)
extra = [l for l in dm_labels if l not in heads]
print("  의존지도 행 수:", len(dm_labels), " 현행에 없는 라벨:", extra)

print("\n=== C. 의존지도 1.1 뺌 목록 vs 장 파일 ===")
txt = (ROOT / "의존지도_v2.md").read_text(encoding="utf-8").splitlines()
s = next(i for i, l in enumerate(txt) if l.startswith("### 1.1"))
e = next(i for i, l in enumerate(txt) if l.startswith("## 2."))
for ln in txt[s:e]:
    for lab in re.findall(r"\{\{\d+:[^}]+\}\}", ln):
        if lab in heads and ln.startswith("|"):
            cells = [c.strip() for c in ln.strip().strip("|").split("|")]
            if cells and cells[0].strip("`") == lab:
                print(f"  뺌 목록의 {lab} 가 장 파일에 있음: {heads[lab]['file']}:{heads[lab]['line']}")

print("\n=== D. 장부 4절(이름 사전) 라벨 vs 장 파일 ===")
lb = (ROOT / "장부_v2.md").read_text(encoding="utf-8").splitlines()
s4 = next(i for i, l in enumerate(lb) if l.startswith("## 4."))
e4 = next(i for i, l in enumerate(lb) if l.startswith("## 5."))
for i in range(s4, e4):
    ln = lb[i]
    if not ln.startswith("|"):
        continue
    cells = [c.strip() for c in ln.strip().strip("|").split("|")]
    for lab in re.findall(r"\{\{\d+:[^}]+\}\}", ln):
        if lab not in heads:
            print(f"  [장부 {i+1}] 라벨 {lab} 장 파일에 머리 없음 | 행: {ln[:160]}")

print("\n=== E. 장부 전체에서 인용한 라벨 가운데 장 파일에 머리 없는 것 ===")
for i, ln in enumerate(lb, 1):
    for lab in set(re.findall(r"\{\{\d+:[^}]+\}\}", ln)):
        if lab not in heads:
            print(f"  [장부 {i}] {lab}")
print("\n=== F. 구조표에서 인용한 라벨 가운데 장 파일에 머리 없는 것 ===")
for i, ln in enumerate((ROOT / "구조표_v2.md").read_text(encoding="utf-8").splitlines(), 1):
    for lab in set(re.findall(r"\{\{\d+:[^}]+\}\}", ln)):
        if lab not in heads:
            print(f"  [구조표 {i}] {lab}")
print("\n=== G. 의존지도 전체(2절 이하)에서 인용한 라벨 가운데 장 파일에 머리 없는 것 ===")
for i, ln in enumerate(txt, 1):
    if i < e:
        continue
    for lab in set(re.findall(r"\{\{\d+:[^}]+\}\}", ln)):
        if lab not in heads:
            print(f"  [의존지도 {i}] {lab}")
