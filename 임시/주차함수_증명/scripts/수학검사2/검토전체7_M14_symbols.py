# -*- coding: utf-8 -*-
"""M14: 장부 1.2 「쓰이는 장」 열과 장 파일의 실제 출현을 글리프 바탕 단위로 맞춘다(후보 목록; 판단은 손으로)."""
import re, pathlib, collections
ROOT = pathlib.Path(r"C:\math\임시\주차함수_증명")
CH = ROOT / "장v2"
files = {"장1":1,"장2":2,"장3":3,"장4":4,"장5A":5,"장5B":5,"장6":6,"장7A":7,"장7B":7,"장8":8,"장9":9,"장10":10,"장11":11}
texts = {}
for f, c in files.items():
    texts.setdefault(c, "")
    texts[c] += (CH / (f + ".md")).read_text(encoding="utf-8")
norm = {c: re.sub(r"\s+", "", t) for c, t in texts.items()}

lines = (ROOT / "장부_v2.md").read_text(encoding="utf-8").splitlines()
rows = []
in12 = False
for ln in lines:
    if ln.startswith("### 1.2"): in12 = True; continue
    if ln.startswith("### 1.3"): break
    if in12 and ln.startswith("| $"):
        cells = [c.strip() for c in ln.strip().strip("|").split("|")]
        rows.append(cells)
print("1.2 rows", len(rows))

def bases(glyph_cell):
    """글자 셀에서 검색용 바탕 토큰을 뽑는다."""
    out = set()
    for m in re.finditer(r"\$([^$]+)\$", glyph_cell):
        s = m.group(1)
        for part in re.split(r",\s*(?![^{]*\})", s):
            part = part.strip()
            mm = re.match(r"^((?:\\(?:mathrm|mathsf|mathcal|mathfrak|mathbb|operatorname)\{[^}]*\})|(?:\\(?:mathrm|mathsf|mathcal|mathfrak|mathbb|tilde|hat|bar)\s*\{?[A-Za-z]\}?)|(?:\\[A-Za-z]+)|(?:[A-Za-z]))", part)
            if not mm: continue
            b = mm.group(1)
            rest = part[len(b):]
            # 첨자·윗첨자 첫 덩어리까지 포함해 조금 더 특정한다
            mm2 = re.match(r"^((?:\^\{[^}]*\}|\^[A-Za-z0-9\\]+|_\{[^}]*\}|_[A-Za-z0-9\\]+)*)", rest)
            out.add((re.sub(r"\s+", "", b), re.sub(r"\s+", "", b + (mm2.group(1) if mm2 else ""))))
    return out

single = re.compile(r"^(\\?[A-Za-z]+|[A-Za-z])$")
report = []
for cells in rows:
    glyph, _, _, defsec, chaps = cells[:5]
    listed = set()
    if chaps.strip() == "전 장":
        listed = set(range(1, 12))
    else:
        listed = {int(x) for x in re.findall(r"\d+", chaps)}
    for base, full in bases(glyph):
        # 단일 라틴/그리스 글자(장식 없음)는 건너뛴다 — 너무 흔함
        if single.match(base) and full == base and not base.startswith("\\math"):
            continue
        key = full if full != base else base
        pat = re.escape(key)
        found = {c for c, t in norm.items() if re.search(pat, t)}
        if not found:
            report.append(("NOTFOUND", glyph[:60], key, sorted(listed)))
            continue
        extra = found - listed
        missing = listed - found
        if extra or missing:
            report.append(("DIFF", glyph[:60], key, sorted(listed), "extra", sorted(extra), "missing", sorted(missing)))
for r in report:
    print(r)
