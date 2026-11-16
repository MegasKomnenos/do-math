# -*- coding: utf-8 -*-
"""부록 A의 각 기호가 장 파일에서 처음 나오는 절을 찾아 「처음 정의된 절」과 견준다."""
import re, io, os
ROOT = r"C:\math\임시\주차함수_증명"
OUT = os.path.join(ROOT, r"대조v2\수학검사2\_N11_부록A절_out.txt")
CH = ["장1", "장2", "장3", "장4", "장5A", "장5B", "장6", "장7A", "장7B", "장8", "장9", "장10"]
SEC = re.compile(r"^### (\d+\.\d+)")
text = []  # (ch, sec, line, text)
for ch in CH:
    sec = None
    for i, ln in enumerate(io.open(os.path.join(ROOT, "장v2", ch + ".md"), encoding="utf-8").read().split("\n")):
        m = SEC.match(ln)
        if m: sec = m.group(1)
        text.append((ch, sec, i + 1, ln))

def first_occ(tok):
    for ch, sec, i, ln in text:
        if tok in ln:
            return (ch, sec, i)
    return None

o = io.open(OUT, "w", encoding="utf-8")
rows = []
for ln in io.open(os.path.join(ROOT, r"장v2\부록A.md"), encoding="utf-8"):
    if ln.startswith("| $"):
        c = [x.strip() for x in ln.strip().strip("|").split(" | ")]
        rows.append(c)
print("부록 A 기호 행 수:", len(rows), file=o)
for c in rows:
    syms = re.findall(r"\$([^$]+)\$", c[0])
    claimed = c[2]
    res = []
    for s in syms:
        core = s.strip()
        # 정의 꼴 '$N:=n-k$' 등은 ':=' 앞만
        core = core.split(":=")[0].split("=")[0].strip()
        occ = first_occ(core)
        res.append((core, occ))
    secs = sorted({str(occ[1]) for _, occ in res if occ})
    flag = ""
    claimed_secs = re.findall(r"\d+\.\d+", claimed)
    if res and all(occ is None for _, occ in res):
        flag = " !! 못 찾음"
    elif claimed_secs and not any(str(occ[1]) in claimed_secs for _, occ in res if occ):
        flag = " !! 절 다름"
    print(c[0][:60], "| 주장:", claimed, "| 첫 출현:", [(cr, occ) for cr, occ in res], flag, file=o)
o.close()
