# -*- coding: utf-8 -*-
"""부록 C 낱말 표: 「처음 정의된 절」 열과 본문에서 그 낱말이 처음 나오는 절을 대조(기계적 1차 선별)."""
import re, os
ROOT = r"C:\math\임시\주차함수_증명"
order = ["장1","장2","장3","장4","장5A","장5B","장6","장7A","장7B","장8","장9","장10","장11"]
# 절 지도
body = []  # (file, lineno, section, text)
for ch in order:
    sec = ch.replace("장","") + "(도입)"
    for i, line in enumerate(open(os.path.join(ROOT,"장v2",ch+".md"), encoding="utf-8"), 1):
        m = re.match(r"^#{2,4} (\d+(?:\.\d+)*)", line)
        if m:
            sec = m.group(1)
        body.append((ch, i, sec, line))
def first_occ(term):
    pat = re.compile(re.escape(term))
    hits = []
    for ch, i, sec, line in body:
        if pat.search(line):
            hits.append((ch, i, sec))
    return hits
rows = []
lines = open(os.path.join(ROOT,"장v2","부록C.md"), encoding="utf-8").read().split("\n")
in_tbl = False
for idx, line in enumerate(lines, 1):
    if line.startswith("### 낱말"): in_tbl = True; continue
    if line.startswith("### ") and in_tbl: break
    if in_tbl and line.startswith("| ") and not line.startswith("| 이 글의 용어") :
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) == 3:
            rows.append((idx, cells))
print("낱말 표 행 수:", len(rows))
def sec_key(s):
    return tuple(int(x) for x in s.split(".")) if s and s[0].isdigit() and "(" not in s else (999,)
for idx, (term, rec, secs) in rows:
    if secs.startswith("—"):
        continue
    listed = re.findall(r"\d+(?:\.\d+)?", secs)
    # 용어 열에서 낱말 후보 뽑기(쉼표로 나뉜 것들; 수식·괄호 제거)
    cands = [t.strip() for t in re.split(r",|·", re.sub(r"\(.*?\)", "", term)) if t.strip()]
    cands = [re.sub(r"\$.*?\$", "", c).strip() for c in cands]
    cands = [c for c in cands if c]
    out = []
    for c in cands:
        hits = first_occ(c)
        if not hits:
            out.append(f"「{c}」 본문에 없음")
            continue
        first = hits[0]
        # 첫 출현이 적힌 절 가운데 하나(장 수준이면 장 일치)인가
        ok = False
        for s in listed:
            if first[2] == s or first[2].startswith(s + ".") or (("." not in s) and first[2].split(".")[0] == s):
                ok = True
        # 적힌 절 안에 출현이 있는가
        in_listed = any(any(h[2] == s or h[2].startswith(s + ".") or (("." not in s) and h[2].split(".")[0] == s) for s in listed) for h in hits)
        if not ok:
            out.append(f"「{c}」 첫 출현 {first[0]}:{first[1]} 절 {first[2]} (적힌 절 {listed}; 적힌 절 안 출현 {'있음' if in_listed else '없음'}; 총 {len(hits)}회)")
    if out:
        print(f"{idx}행 [{term}] 절 {secs}")
        for o in out: print("   -", o)
