# -*- coding: utf-8 -*-
"""장부 1.2 전역 기호 '쓰이는 장' 열 vs 장 파일 실제 출현(고정 문자열)."""
import re, sys, io
from pathlib import Path
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
ROOT = Path(r"C:\math\임시\주차함수_증명")
CH = {"장1.md":"1","장2.md":"2","장3.md":"3","장4.md":"4","장5A.md":"5","장5B.md":"5","장6.md":"6","장7A.md":"7","장7B.md":"7","장8.md":"8","장9.md":"9","장10.md":"10","장11.md":"11"}
text = {}
for fn, ch in CH.items():
    text.setdefault(ch, "")
    text[ch] += (ROOT/"장v2"/fn).read_text(encoding="utf-8") + "\n"
lines = (ROOT/"장부_v2.md").read_text(encoding="utf-8").splitlines()
out = []
in12 = False
rows = []
for i, l in enumerate(lines, 1):
    if l.startswith("### 1.2"): in12 = True; continue
    if l.startswith("### 1.3"): in12 = False
    if in12 and l.startswith("| $"):
        c = [x.strip() for x in l.strip().strip("|").split("|")]
        rows.append((i, c))
out.append("1.2 rows: %d" % len(rows))
ALL = ["1","2","3","4","5","6","7","8","9","10","11"]
def parse_ch(s):
    s = s.strip()
    if s.startswith("전 장"): return set(ALL)
    return set(re.findall(r"\b(\d{1,2})\b", s.split("(")[0])) if s else set()
for i, c in rows:
    glyph_cell = c[0]
    glyphs = re.findall(r"\$([^$]+)\$", glyph_cell)
    if not glyphs: continue
    g = glyphs[0]
    stem = re.split(r"[_^(]", g, 1)[0]
    declared = parse_ch(c[4])
    found_exact = {ch for ch, t in text.items() if g in t}
    found_stem = {ch for ch, t in text.items() if stem and stem in t}
    extra = found_exact - declared
    missing = declared - found_stem if stem and len(stem) >= 2 else set()
    missing_exact = declared - found_exact
    note = []
    if extra: note.append("선언 밖 출현(정확 철자) %s" % sorted(extra, key=int))
    if missing: note.append("선언했으나 줄기 %r도 없음 %s" % (stem, sorted(missing, key=int)))
    elif missing_exact: note.append("선언했으나 정확 철자 없음 %s" % sorted(missing_exact, key=int))
    if note: out.append("  %d $%s$ [%s]: %s" % (i, g, c[4][:30], "; ".join(note)))
(ROOT/"scripts"/"수학검사2"/"검토전체19_M14_sym_out.txt").write_text("\n".join(out), encoding="utf-8")
print("\n".join(out))
