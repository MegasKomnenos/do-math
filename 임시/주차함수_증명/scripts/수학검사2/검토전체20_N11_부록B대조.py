# -*- coding: utf-8 -*-
"""부록 B의 행(식별자·시각·제목·폴더)을 기록 폴더와 대조하고, 장 파일이 인용한 식별자와 맞춘다."""
import re, glob, io, os, json, datetime
ROOT = r"C:\math\임시\주차함수_증명"
REC = r"C:\math\.skill-workspace\do-math\parking-unimodality-fresh-20261105-150803\knowledge\records"
out = io.open(os.path.join(ROOT, r"대조v2\수학검사2\_N11_부록B대조_out.txt"), "w", encoding="utf-8")
def P(*a): print(*a, file=out)

rows = []
for ln in io.open(os.path.join(ROOT, r"장v2\부록B.md"), encoding="utf-8"):
    if ln.startswith("| r"):
        c = [x.strip() for x in ln.strip().strip("|").split("|")]
        rows.append(c)
P("부록 B 행 수:", len(rows))
prev = None
for ident, when, title, folder in rows:
    folder = folder.strip("`")
    path = os.path.join(REC, folder)
    msgs = []
    if not folder.startswith(ident): msgs.append("식별자≠폴더 앞글자")
    if len(ident) != 8: msgs.append("식별자 길이")
    if not os.path.isdir(path):
        msgs.append("폴더 없음")
    else:
        try:
            rj = json.load(io.open(os.path.join(path, "record.json"), encoding="utf-8"))
            t = rj.get("title", "")
            if t.strip() != title.strip():
                msgs.append("제목 다름: 기록=" + t)
        except Exception as e:
            msgs.append("record.json 읽기 실패 " + str(e))
        mt = datetime.datetime.fromtimestamp(os.path.getmtime(path))
        ms = mt.strftime("%m-%d %H:%M")
        if ms != when:
            msgs.append("시각 다름: 폴더 mtime=" + ms)
        if prev and mt < prev: msgs.append("시각 순서 역전")
        prev = mt
    P(ident, when, "|", "; ".join(msgs) if msgs else "OK")

# 장 파일의 인용 식별자
cited = {}
for f in glob.glob(os.path.join(ROOT, r"장v2\*.md")):
    txt = io.open(f, encoding="utf-8").read()
    for m in re.finditer(r"r[0-9a-f]{7}\b", txt):
        cited.setdefault(m.group(0), set()).add(os.path.basename(f))
B = {r[0] for r in rows}
P("\n장v2에 나오나 부록 B에 없는 식별자:")
for k in sorted(cited):
    if k not in B: P("  ", k, sorted(cited[k]))
P("부록 B에 있으나 장v2 어디에도(부록 B 밖) 나오지 않는 식별자:")
for k in sorted(B):
    fs = cited.get(k, set()) - {"부록B.md"}
    if not fs: P("  ", k)
# 식별자가 부록B 밖 어디에 나오는지 요약
P("\n식별자별 출현 파일(부록B 제외):")
for k in sorted(B):
    P("  ", k, sorted(cited.get(k, set()) - {"부록B.md"}))
out.close()
