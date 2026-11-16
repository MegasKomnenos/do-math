# -*- coding: utf-8 -*-
"""M14: 장부 3절 낱말의 「첫 정의 절」과 장 본문에서 그 낱말이 처음 나타나는 절을 맞춘다(후보 목록)."""
import re, pathlib
ROOT = pathlib.Path(r"C:\math\임시\주차함수_증명")
CH = ROOT / "장v2"
order = ["장1","장2","장3","장4","장5A","장5B","장6","장7A","장7B","장8","장9","장10","장11"]
sec_re = re.compile(r"^(#{2,4})\s+([0-9]+(?:\.[0-9]+)*)\s")
docs = []
for f in order:
    cur = None
    for i, ln in enumerate((CH/(f+".md")).read_text(encoding="utf-8").splitlines(), 1):
        m = sec_re.match(ln)
        if m: cur = m.group(2)
        docs.append((f, cur, i, ln))
def key(sec):
    return [int(p) for p in sec.split(".")][:2] if sec else [0]
rows = []
in3 = False
for ln in (ROOT/"장부_v2.md").read_text(encoding="utf-8").splitlines():
    if ln.startswith("## 3."): in3 = True; continue
    if ln.startswith("## 4."): break
    if in3 and ln.startswith("| ") and not ln.startswith("| 낱말") and not ln.startswith("|---"):
        cells = [c.strip() for c in ln.strip().strip("|").split("|")]
        if len(cells) >= 3: rows.append(cells)
print("3절 rows", len(rows))
for cells in rows:
    words = [w.strip() for w in re.split(r"[,;]", cells[0]) if w.strip() and not w.strip().startswith("$")]
    secs = re.findall(r"\d+\.\d+", cells[2])
    if not secs: continue
    defk = key(secs[0])
    for w in words[:3]:
        if len(w) < 2: continue
        w0 = re.sub(r"\(.*?\)", "", w).strip()
        if not w0 or "$" in w0: continue
        first = None
        for f, sec, i, ln in docs:
            if f == "장1" and sec and key(sec) <= [1,5]: continue  # 1장 개관·1.5 미리 부름은 설계
            if w0 in ln:
                first = (f, sec, i); break
        if first and first[1] and key(first[1]) < defk:
            print(f"「{w0}」 장부 {secs[0]} / 첫 출현 {first[0]} {first[1]} L{first[2]}")
