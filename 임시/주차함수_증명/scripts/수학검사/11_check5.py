# -*- coding: utf-8 -*-
import re, glob, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
R = "C:/math/임시/주차함수_증명/"
HEAD = re.compile(r"^\*\*(정의|정리|명제|보조정리|따름정리|문제|추측|관찰|주의|가정|표기)\s+\{\{(\d+:[^}]+)\}\}")
# map each line to (section, current statement label incl. proofs "**정리 {{x}}의 증명.**")
locs = []  # (file, lineno, section, label, line)
for f in sorted(glob.glob(R+"장v2/장*.md")) + sorted(glob.glob(R+"장v2/부록*.md")):
    lines = open(f, encoding="utf-8").read().split("\n")
    sec = None; cur = None
    for i, l in enumerate(lines, 1):
        ms = re.match(r"^###\s+(\d+\.\d+)\b", l) or re.match(r"^###\s+D\.\{\{(D:[^}]+)\}\}", l) or re.match(r"^##\s+(\d+)\.\s", l)
        if ms: sec = ms.group(1); cur = None
        m = HEAD.match(l)
        if m: cur = m.group(2)
        mp = re.match(r"^\*\*(?:정의|정리|명제|보조정리|따름정리)\s+\{\{(\d+:[^}]+)\}\}의 증명\.\*\*", l)
        if mp: cur = mp.group(1) + "(증명)"
        locs.append((f.split("/")[-1], i, sec, cur, l))
terms = {
 "Konheim": r"Konheim", "Foata/Pollak": r"Foata|Pollak", "Celano": r"Celano", "Aguilar": r"Aguilar", "지수 공식": r"지수 공식|Corollary 5\.1\.6",
 "Cayley": r"Cayley|Proposition 5\.3\.2", "Lagrange": r"Lagrange|Theorem 5\.4\.2", "Knuth TAOCP/갈고리": r"Knuth|갈고리", "Flajolet": r"Flajolet|Sedgewick",
 "Robbins": r"Robbins", "Petersson": r"Petersson", "Janson": r"Janson", "Ibragimov": r"Ibragimov", "Euler–Maclaurin": r"Euler.Maclaurin|Graham|Patashnik",
 "Cauchy/Ahlfors": r"Cauchy|Ahlfors", "FKG": r"FKG|Fortuin", "Jensen": r"Jensen", "Wallis": r"Wallis", "Corless/Lambert": r"Corless|Lambert",
 "Tanner": r"Tanner", "Grimmett": r"Grimmett", "Harris": r"Harris", "Faà/Comtet": r"Fa[àa] di Bruno|Comtet", "Apostol/Euler 합": r"Apostol|Euler 합", "Titchmarsh": r"Titchmarsh",
}
for name, pat in terms.items():
    rx = re.compile(pat)
    hits = {}
    for f, i, sec, cur, l in locs:
        if f == "장11.md": continue
        if rx.search(l):
            key = (f, sec, cur)
            hits.setdefault(key, []).append(i)
    print(f"\n### {name}")
    for (f, sec, cur), ls in hits.items():
        print(f"   {f} §{sec} {cur or '(산문)'} 행{ls[:6]}")
