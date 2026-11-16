# -*- coding: utf-8 -*-
"""11.4 문헌 표의 「쓰인 자리」를 장 파일에서 저자명 출현으로 대조한다."""
import re, io, os
ROOT = r"C:\math\임시\주차함수_증명"
OUT = os.path.join(ROOT, r"대조v2\수학검사2\_N11_문헌_out.txt")
CH = ["장1", "장2", "장3", "장4", "장5A", "장5B", "장6", "장7A", "장7B", "장8", "장9", "장10",
      "부록D_장2", "부록D_장3", "부록D_장4", "부록D_장5A", "부록D_장5B", "부록D_장6", "부록D_장7A", "부록D_장7B", "부록D_장8", "부록D_장9", "부록D_장10"]
HEAD = re.compile(r"^\*\*(정리|명제|보조정리|따름정리|정의) \{\{(\d+[AB]?):([^}]+)\}\}(.*?)\*\*")
DHEAD = re.compile(r"^### D\.\{\{D:([^}]+)\}\}")
SEC = re.compile(r"^### (\d+\.\d+)")
KEYS = ["Konheim", "Foata", "Pollak", "Celano", "Aguilar", "Stanley", "Knuth", "Flajolet", "Tanner", "Robbins", "Petersson",
        "Janson", "Ibragimov", "Ahlfors", "Graham", "Fortuin", "FKG", "Grimmett", "Jensen", "Wallis", "Corless", "Lambert",
        "Harris", "Comtet", "Faà", "Apostol", "Titchmarsh", "Euler", "Cauchy", "편각 원리", "Cayley 공식", "지수 공식", "Lagrange 역변환", "표준"]
o = io.open(OUT, "w", encoding="utf-8")
hits = {k: [] for k in KEYS}
for ch in CH:
    lines = io.open(os.path.join(ROOT, "장v2", ch + ".md"), encoding="utf-8").read().split("\n")
    sec, cur = None, None
    for i, ln in enumerate(lines):
        m = SEC.match(ln)
        if m: sec = m.group(1); cur = None
        h = HEAD.match(ln)
        if h and not h.group(4).strip().startswith("의 증명"):
            cur = h.group(1) + " " + h.group(3)
        d = DHEAD.match(ln)
        if d: cur = "D." + d.group(1)
        for k in KEYS:
            if k in ln:
                hits[k].append((ch, sec, cur, i + 1, ln[:90].replace("|", "/")))
for k in KEYS:
    print("\n=====", k, len(hits[k]), file=o)
    seen = set()
    for ch, sec, cur, i, s in hits[k]:
        key = (ch, sec, cur)
        if key in seen: continue
        seen.add(key)
        print("  ", ch, sec, cur, "@", i, file=o)
o.close()
