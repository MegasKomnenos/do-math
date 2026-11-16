# -*- coding: utf-8 -*-
"""R2 (ㄱ)(ㄷ): 장부 1.2 전역 기호의 「정의 절」과 부록 A 현재 판의 「처음 정의된 절」을, 장 파일에서 그 글자가 처음 나오는 절과 견준다(읽기 전용; 휴리스틱)."""
import io, os, re, sys, glob
ROOT = r"C:\math\임시\주차함수_증명"
ORDER = ["장1","장2","장3","장4","장5A","장5B","장6","장7A","장7B","장8","장9","장10","장11"]
def load():
    idx = []  # (chapter, lineno, section, normalized line)
    for ch in ORDER:
        sec = None
        for i, ln in enumerate(io.open(os.path.join(ROOT, "장v2", ch + ".md"), encoding="utf-8").read().split("\n"), 1):
            m = re.match(r"^### (\d+\.\d+)", ln)
            if m: sec = m.group(1)
            m2 = re.match(r"^## (\d+)\.", ln)
            if m2 and sec is None: sec = m2.group(1) + "(도입)"
            idx.append((ch, i, sec, re.sub(r"\s+", "", ln)))
    return idx
IDX = load()
def first_hit(core):
    for ch, i, sec, ln in IDX:
        if core in ln:
            return ch, i, sec
    return None
def core_of(glyph):
    m = re.search(r"\$([^$]+)\$", glyph)
    if not m: return None
    inner = m.group(1)
    inner = inner.split(",")[0]
    inner = re.sub(r"\(.*$", "", inner)      # 인수 제거
    inner = re.sub(r"[:=].*$", "", inner)    # 정의식 제거
    inner = re.sub(r"\s+", "", inner).rstrip("\\")
    return inner or None
L = io.open(os.path.join(ROOT, "장부_v2.md"), encoding="utf-8").read()
def section(text, a, bs):
    i = text.index(a); j = len(text)
    for b in bs:
        k = text.find(b, i + len(a))
        if k != -1: j = min(j, k)
    return text[i:j]
def rows(sec):
    out = []
    for ln in sec.split("\n"):
        if ln.startswith("|") and not ln.startswith("|---"):
            out.append([c.strip() for c in ln.strip().strip("|").split(" | ")])
    return out
s12 = rows(section(L, "### 1.2 전역 기호", ["### 1.3"]))
A = io.open(os.path.join(ROOT, "장v2", "부록A.md"), encoding="utf-8").read()
arows = {r[0]: r for r in rows(A) if len(r) >= 4}
out = io.StringIO()
n_mis = 0
for r in s12:
    if len(r) < 7 or r[0].startswith("글자"): continue
    glyph, sec = r[0], r[3]
    core = core_of(glyph)
    if not core: continue
    hit = first_hit(core)
    decl = re.findall(r"\d+\.\d+|부록 D", sec)
    a_sec = arows.get(glyph, [None]*4)[2] if glyph in arows else "(부록A에 없음)"
    if not hit:
        out.write(f"[없음] {glyph} | 장부 {sec} | 부록A {a_sec} | 검색 핵 {core}\n"); continue
    ch, i, hsec = hit
    ok = hsec in decl if hsec else False
    if not ok:
        n_mis += 1
        out.write(f"[어긋남?] {glyph} | 장부 {sec} | 부록A {a_sec} | 첫 출현 {ch}:{i} ({hsec}) | 핵 {core}\n")
out.write(f"\n어긋남 후보 {n_mis}\n")
sys.stdout.buffer.write(out.getvalue().encode("utf-8"))
