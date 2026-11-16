# -*- coding: utf-8 -*-
"""(1) 네 파일이 인용하는 라벨이 모두 장 파일 머리에 있는가. (2) 장부 1.3 국소 기호 행의 글자가 자리 열이 가리키는 장에 실제로 있는가."""
import re, sys, io, json
from pathlib import Path
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
ROOT = Path(r"C:\math\임시\주차함수_증명")
heads = json.load(open(ROOT/"scripts"/"수학검사2"/"검토전체19_M14_heads.json", encoding="utf-8"))
hl = {h["label"]: h for h in heads}
LAB = re.compile(r"\{\{(\d+):([^}]+)\}\}")
out = []
files = {"장부": ROOT/"장부_v2.md", "구조표": ROOT/"구조표_v2.md", "의존지도": ROOT/"의존지도_v2.md", "대응표": ROOT/"대조v2"/"라벨_번호_대응표_1114.md"}
dtext = "\n".join((ROOT/"장v2"/f).read_text(encoding="utf-8") for f in ["장11.md"] + [p.name for p in (ROOT/"장v2").glob("부록D_*.md")])
dlabels = set(re.findall(r"\{\{D:[^}]+\}\}", dtext))
for name, p in files.items():
    miss = {}
    for i, l in enumerate(p.read_text(encoding="utf-8").splitlines(), 1):
        for m in LAB.finditer(l):
            lab = m.group(0)
            if m.group(1) == "D":
                if lab not in dlabels: miss.setdefault(lab, []).append(i)
            elif lab not in hl: miss.setdefault(lab, []).append(i)
    out.append("== %s: 머리 없는 라벨 인용 %d종" % (name, len(miss)))
    for lab, ls in miss.items(): out.append("   %s 행 %s" % (lab, ls[:6]))
# 부록 D labels in 11.2 vs 부록D files
d112 = set(re.findall(r"\{\{D:[^}]+\}\}", (ROOT/"장v2"/"장11.md").read_text(encoding="utf-8")))
dfiles = set()
for p in (ROOT/"장v2").glob("부록D_*.md"):
    for l in p.read_text(encoding="utf-8").splitlines():
        if l.startswith("**D.") or l.startswith("### ") or l.startswith("**{{D") or "{{D:" in l[:60]:
            dfiles |= set(re.findall(r"\{\{D:[^}]+\}\}", l))
out.append("== D 라벨: 11장 %d, 부록 D 파일(머리 근처) %d; 11장에만=%s; 부록에만=%s" % (len(d112), len(dfiles), sorted(d112-dfiles), sorted(dfiles-d112)))

# ---- 1.3 check
CH = {"1":["장1.md"],"2":["장2.md"],"3":["장3.md"],"4":["장4.md"],"5":["장5A.md","장5B.md"],"6":["장6.md"],"7":["장7A.md","장7B.md"],"8":["장8.md"],"9":["장9.md"],"10":["장10.md"],"11":["장11.md"]}
text = {ch: "\n".join((ROOT/"장v2"/f).read_text(encoding="utf-8") for f in fs) for ch, fs in CH.items()}
lines = (ROOT/"장부_v2.md").read_text(encoding="utf-8").splitlines()
in13 = False; rows = []
for i, l in enumerate(lines, 1):
    if l.startswith("### 1.3"): in13 = True; continue
    if l.startswith("## 2."): in13 = False
    if in13 and l.startswith("| $"):
        rows.append((i, [x.strip() for x in l.strip().strip("|").split("|")]))
out.append("== 1.3 행 수 %d" % len(rows))
for i, c in rows:
    glyphs = re.findall(r"\$([^$]+)\$", c[0])
    place = c[2]
    chs = set()
    for m in re.finditer(r"(?<![\d.])(\d{1,2})\.\d", place): chs.add(m.group(1))
    for m in LAB.finditer(place): chs.add(m.group(1))
    chs = {x for x in chs if x in CH}
    if not chs:
        out.append("  %d: 자리 열에서 장을 못 읽음: %r" % (i, place[:60])); continue
    missing_all = []
    for g in glyphs:
        key = re.sub(r"\([^()]*\)$", "", g.split(",")[0].split(":=")[0].split("=")[0].strip()).strip()
        if len(key) < 1: continue
        if not any(key in text[ch] for ch in chs):
            missing_all.append(key)
    if missing_all and len(missing_all) == len([g for g in glyphs]):
        out.append("  %d 장%s: 모든 글자 없음 %s" % (i, sorted(chs), missing_all[:6]))
    elif missing_all:
        out.append("  %d 장%s: 일부 글자 없음 %s" % (i, sorted(chs), missing_all[:6]))
(ROOT/"scripts"/"수학검사2"/"검토전체19_M14_labels13_out.txt").write_text("\n".join(out), encoding="utf-8")
print("\n".join(out))
