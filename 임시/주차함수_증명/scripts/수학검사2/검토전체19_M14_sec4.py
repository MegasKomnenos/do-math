# -*- coding: utf-8 -*-
"""M14: 장부 4절 (이름 사전) vs 장 파일 머리; 5절 장별 배정."""
import re, sys, io, json
from pathlib import Path
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
ROOT = Path(r"C:\math\임시\주차함수_증명")
heads = json.load(open(ROOT/"scripts"/"수학검사2"/"검토전체19_M14_heads.json", encoding="utf-8"))
hl = {h["label"]: h for h in heads}
lines = (ROOT/"장부_v2.md").read_text(encoding="utf-8").splitlines()
rows = []
sec = None
for i, l in enumerate(lines, 1):
    if l.startswith("## "): sec = l[3:5].strip()
    if sec and sec.startswith("4") and l.startswith("| ") and not l.startswith("| 첫 판") and not l.startswith("|---"):
        c = [x.strip() for x in l.strip().strip("|").split("|")]
        if len(c) >= 6: rows.append((i, c))
out = ["4절 행 수: %d" % len(rows)]
seen = set(); removed = []
for i, c in rows:
    old, kind, name, recname, sec2, lab = c[:6]
    if lab.startswith("("):
        removed.append((i, old, kind, name, recname, lab)); continue
    seen.add(lab)
    h = hl.get(lab)
    if not h:
        out.append("  %d: 라벨 %s 장 파일에 없음" % (i, lab)); continue
    title = (name + ("; " + recname if recname else "")) if (name or recname) else None
    if recname and not name: title = recname
    d = []
    if kind != h["kind"]: d.append("종류 장부=%s 장=%s" % (kind, h["kind"]))
    if (title or None) != h["title"]: d.append("이름 장부=%r 장=%r" % (title, h["title"]))
    if sec2 != h["sec"]: d.append("절 장부=%s 장=%s" % (sec2, h["sec"]))
    # first-edition number consistency with label
    m = re.match(r"\{\{\d+:old-(\d+)-(\d+)\}\}", lab)
    if m:
        if old != "%s.%s" % m.groups(): d.append("첫 판 번호 %s vs 라벨 %s" % (old, lab))
    else:
        if old != "—": d.append("새 라벨인데 첫 판 번호 %s" % old)
    if d: out.append("  %d %s: %s" % (i, lab, "; ".join(d)))
out.append("== 장 파일 머리 가운데 4절에 없는 라벨")
for h in heads:
    if h["label"] not in seen: out.append("  %s %s:%d" % (h["label"], h["file"], h["line"]))
out.append("== 4절 뺌 행 %d개" % len(removed))
for r in removed: out.append("  %s" % (r,))
# 4절 뺌 라벨이 장 파일에 라벨 꼴로 남아 있는가
alltext = {p.name: p.read_text(encoding="utf-8") for p in (ROOT/"장v2").glob("*.md")}
for r in removed:
    lab = "{{" + r[5].strip("()") + "}}"
    for fn, t in alltext.items():
        if lab in t: out.append("  !! 뺌 라벨 %s 가 %s 에 남아 있음" % (lab, fn))
# duplicates in 4절
labs = [c[5] for i, c in rows]
dup = {x for x in labs if labs.count(x) > 1}
out.append("== 4절 중복 라벨: %s" % sorted(dup))
(ROOT/"scripts"/"수학검사2"/"검토전체19_M14_sec4_out.txt").write_text("\n".join(out), encoding="utf-8")
print("\n".join(out))
