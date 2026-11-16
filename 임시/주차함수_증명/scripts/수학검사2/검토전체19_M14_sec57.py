# -*- coding: utf-8 -*-
"""장부 5절(장별 배정·여유 글자)과 7절(기록 글자 대응)의 내부 정합 검사."""
import re, sys, io
from pathlib import Path
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
ROOT = Path(r"C:\math\임시\주차함수_증명")
lines = (ROOT/"장부_v2.md").read_text(encoding="utf-8").splitlines()
out = []
# ---- 1.2 rows
rows12 = []; rows11 = []; sec = None
for i, l in enumerate(lines, 1):
    if l.startswith("### 1.1"): sec = "1.1"
    elif l.startswith("### 1.2"): sec = "1.2"
    elif l.startswith("### 1.3"): sec = "1.3"
    elif l.startswith("## "): sec = l[3:5].strip()
    if l.startswith("| $"):
        c = [x.strip() for x in l.strip().strip("|").split("|")]
        if sec == "1.2": rows12.append((i, c))
        if sec == "1.1": rows11.append((i, c))
ALL = ["1","2","3","4","5","6","7","8","9","10","11"]
def parse_ch(s):
    s = s.strip()
    if s.startswith("전 장"): return set(ALL)
    return set(re.findall(r"\b(\d{1,2})\b", s.split("(")[0]))
# ---- 5절 table
rows5 = {}
in5 = False
for i, l in enumerate(lines, 1):
    if l.startswith("## 5."): in5 = True; continue
    if l.startswith("## 6."): in5 = False
    if in5 and re.match(r"^\| \d{1,2} \|", l):
        c = [x.strip() for x in l.strip().strip("|").split("|")]
        rows5[c[0]] = c
out.append("5절 장 행: %s" % sorted(rows5, key=int))
# (a) 처음 정의하는 전역 기호 vs 1.2 정의 절
for ch in ALL:
    exp = set()
    for i, c in rows12:
        defsec = c[3]
        firsts = re.findall(r"(?<![\d.])(\d{1,2})\.\d{1,2}", defsec)
        if firsts and min(firsts, key=int) == ch: exp.add(c[0])
        elif not firsts and defsec.strip().startswith(ch): exp.add(c[0])
    listed = set(x.strip() for x in rows5[ch][1].split(";")) if rows5[ch][1] != "없음" else set()
    listed = {re.sub(r"\(.*?\)$", "", x).strip() for x in listed}
    missing = exp - listed; extra = listed - exp
    # loosen: compare by stripping $ and spaces
    norm = lambda s: re.sub(r"\s", "", s)
    missing = {m for m in missing if norm(m) not in {norm(x) for x in listed}}
    extra = {e for e in extra if norm(e) not in {norm(x) for x in exp}}
    if missing or extra:
        out.append("  장 %s: 1.2 정의절 기준인데 5절에 없음=%s ; 5절에 있는데 1.2 정의절 아님=%s" % (ch, sorted(missing)[:12], sorted(extra)[:12]))
# (b) 여유 글자 vs 사용 글자 (바탕 글자·글자체)
def base_of(latex):
    s = latex.strip()
    m = re.match(r"^\\(mathcal|mathfrak|mathsf|mathrm|mathbb)\s*\{?([A-Za-z]+)\}?", s)
    if m: return (m.group(2) if m.group(1)!="mathrm" else "RM:"+m.group(2), m.group(1))
    m = re.match(r"^(\\(?:hat|tilde|bar|widehat|widetilde)\s*)?\\?([A-Za-z]+)", s)
    if m:
        tok = m.group(2)
        if s.startswith("\\") and not m.group(1): return ("\\"+tok, "greek") if tok not in ("Pr","ell") else (("\\ell","latin") if tok=="ell" else ("Pr","Pr"))
        return (tok[0], "latin")
    return None
reserved = {("a","latin"),("b","latin"),("c","latin"),("e","latin"),("h","latin"),("\\delta","greek"),("\\Delta","greek"),("\\Sigma","greek"),("\\ell","latin"),("o","latin"),("O","latin"),("\\varpi","greek")}
ch1 = set(); var11 = set()
for i, c in rows11:
    for g in re.findall(r"\$([^$]+)\$", c[0]):
        for p in re.split(r",\s*", g):
            b = base_of(p.split(":=")[0]);
            if b: var11.add(b)
used = {ch: set() for ch in ALL}
for i, c in rows12:
    chs = parse_ch(c[4]); defs = re.findall(r"(?<![\d.])(\d{1,2})\.\d{1,2}", c[3])
    bases = set()
    for g in re.findall(r"\$([^$]+)\$", c[0]):
        for p in re.split(r",\s*(?![^{}]*\})", g):
            b = base_of(p)
            if b: bases.add(b)
    for ch in chs: used[ch] |= bases
    if defs and min(defs, key=int) == "1": ch1 |= bases
for ch in ALL:
    free = rows5[ch][3]
    freeset = set()
    for g in re.findall(r"\$([^$]+)\$", free):
        b = base_of(g)
        if b: freeset.add(b)
    bad = freeset & (used[ch] | ch1 | var11 | reserved)
    # 산세리프 여유는 명명 상수에만 — 산세리프 충돌만 따로
    if bad: out.append("  장 %s 여유 글자 가운데 충돌: %s" % (ch, sorted(bad)))
# ---- 7절 identifiers vs 부록 B
in7 = False; ids7 = set()
for i, l in enumerate(lines, 1):
    if l.startswith("## 7."): in7 = True; continue
    if l.startswith("## 8."): in7 = False
    if in7: ids7 |= set(re.findall(r"r[0-9a-f]{7}", l))
idsB = set(re.findall(r"r[0-9a-f]{7}", (ROOT/"장v2"/"부록B.md").read_text(encoding="utf-8")))
out.append("7절 식별자 %d, 부록 B %d; 7절에만=%s; B에만=%s" % (len(ids7), len(idsB), sorted(ids7-idsB), sorted(idsB-ids7)))
# 7절 header line(s)
for i, l in enumerate(lines, 1):
    if 1250 <= i <= 1262 and l.strip(): out.append("  7절 %d: %s" % (i, l[:300]))
(ROOT/"scripts"/"수학검사2"/"검토전체19_M14_sec57_out.txt").write_text("\n".join(out), encoding="utf-8")
print("\n".join(out))
