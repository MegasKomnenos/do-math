# -*- coding: utf-8 -*-
import re, sys, io
from pathlib import Path
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
ROOT = Path(r"C:\math\임시\주차함수_증명")
CH = {"장1.md":"1","장2.md":"2","장3.md":"3","장4.md":"4","장5A.md":"5","장5B.md":"5","장6.md":"6","장7A.md":"7","장7B.md":"7","장8.md":"8","장9.md":"9","장10.md":"10","장11.md":"11"}
lines_by = {}
for fn, ch in CH.items():
    lines_by.setdefault(ch, [])
    for i, l in enumerate((ROOT/"장v2"/fn).read_text(encoding="utf-8").splitlines(), 1):
        lines_by[ch].append((fn, i, l))
lines = (ROOT/"장부_v2.md").read_text(encoding="utf-8").splitlines()
out = []
in12 = False; rows = []
for i, l in enumerate(lines, 1):
    if l.startswith("### 1.2"): in12 = True; continue
    if l.startswith("### 1.3"): in12 = False
    if in12 and l.startswith("| $"):
        rows.append((i, [x.strip() for x in l.strip().strip("|").split("|")]))
ALL = ["1","2","3","4","5","6","7","8","9","10","11"]
def parse_ch(s):
    s = s.strip()
    if s.startswith("전 장"): return set(ALL)
    return set(re.findall(r"\b(\d{1,2})\b", s.split("(")[0]))
def keys(cell):
    g = re.findall(r"\$([^$]+)\$", cell)[0]
    parts = [p.strip() for p in re.split(r",\s*(?![^{}]*\})", g)]
    ks = []
    for p in parts:
        p2 = re.sub(r"\([^()]*\)$", "", p).strip()
        if p2: ks.append(p2)
    return g, ks
for i, c in rows:
    g, ks = keys(c[0])
    declared = parse_ch(c[4])
    found = {}
    for ch, ls in lines_by.items():
        for fn, n, l in ls:
            for k in ks:
                if k in l:
                    found.setdefault(ch, []).append((fn, n, k, l))
    fch = set(found)
    extra = fch - declared
    missing = declared - fch
    if not extra and not missing: continue
    out.append("--- %d $%s$ 선언=%s" % (i, g, sorted(declared, key=int)))
    if missing: out.append("    선언했으나 어느 글자도 없음: %s" % sorted(missing, key=int))
    for ch in sorted(extra, key=int):
        hits = found[ch]
        out.append("    선언 밖 %s (%d건): " % (ch, len(hits)))
        for fn, n, k, l in hits[:3]:
            j = l.find(k); out.append("        %s:%d [%s] …%s…" % (fn, n, k, l[max(0,j-60):j+60].replace("\n"," ")))
(ROOT/"scripts"/"수학검사2"/"검토전체19_M14_sym2_out.txt").write_text("\n".join(out), encoding="utf-8")
print(len(out), "lines")
