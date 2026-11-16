# -*- coding: utf-8 -*-
"""장부 3절 낱말 사전: 낱말이 장 파일에 있는가, 첫 정의 절의 장에 있는가, 그 장보다 앞 장에 나오는가."""
import re, sys, io
from pathlib import Path
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
ROOT = Path(r"C:\math\임시\주차함수_증명")
CH = {"1":["장1.md"],"2":["장2.md"],"3":["장3.md"],"4":["장4.md"],"5":["장5A.md","장5B.md"],"6":["장6.md"],"7":["장7A.md","장7B.md"],"8":["장8.md"],"9":["장9.md"],"10":["장10.md"],"11":["장11.md"]}
text = {ch: "\n".join((ROOT/"장v2"/f).read_text(encoding="utf-8") for f in fs) for ch, fs in CH.items()}
dtext = "\n".join(p.read_text(encoding="utf-8") for p in (ROOT/"장v2").glob("부록D_*.md"))
lines = (ROOT/"장부_v2.md").read_text(encoding="utf-8").splitlines()
in3 = False; rows = []
for i, l in enumerate(lines, 1):
    if l.startswith("## 3."): in3 = True; continue
    if l.startswith("## 4."): in3 = False
    if in3 and l.startswith("| ") and not l.startswith("| 낱말") and not l.startswith("|---"):
        c = [x.strip() for x in l.strip().strip("|").split("|")]
        if len(c) >= 4: rows.append((i, c))
out = ["3절 행 수: %d" % len(rows)]
order = ["1","2","3","4","5","6","7","8","9","10","11"]
for i, c in rows:
    words = [w.strip() for w in re.split(r"[,;·]\s*", re.sub(r"\(.*?\)", "", c[0])) if w.strip()]
    words = [re.sub(r"\$.*?\$", "", w).strip() for w in words]
    words = [w for w in words if w and len(w) >= 2]
    secs = re.findall(r"(?<![\d.])(\d{1,2})\.\d{1,2}", c[2])
    chs = [s for s in secs if s in CH]
    is_general = "일반어" in c[2] or "부록 D" in c[2]
    for w in words:
        where = [ch for ch in order if w in text[ch]]
        inD = w in dtext
        if not where and not inD:
            out.append("  %d 「%s」: 장·부록 D 어디에도 없음 (첫 정의 절 %s)" % (i, w, c[2][:25])); continue
        if chs and not is_general:
            first = min(chs, key=int)
            if first not in where and not inD:
                out.append("  %d 「%s」: 첫 정의 절 장 %s 에 없음; 있는 장=%s" % (i, w, first, where))
            earlier = [ch for ch in where if int(ch) < int(first) and ch != "1"]
            if earlier:
                out.append("  %d 「%s」: 첫 정의 장 %s 보다 앞 장에 출현 %s" % (i, w, first, earlier))
(ROOT/"scripts"/"수학검사2"/"검토전체19_M14_words_out.txt").write_text("\n".join(out), encoding="utf-8")
print("\n".join(out))
