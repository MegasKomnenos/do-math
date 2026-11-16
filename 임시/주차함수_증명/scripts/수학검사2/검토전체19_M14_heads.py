# -*- coding: utf-8 -*-
"""M14: extract statement heads from 장v2/*.md and compare with
대조v2/라벨_번호_대응표_1114.md and 의존지도_v2.md 1절."""
import re, sys, json, io
from pathlib import Path
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
ROOT = Path(r"C:\math\임시\주차함수_증명")
ORDER = ["장1","장2","장3","장4","장5A","장5B","장6","장7A","장7B","장8","장9","장10","장11"]
KINDS = "정의|정리|명제|보조정리|따름정리"
HEAD = re.compile(r"^\*\*(" + KINDS + r") \{\{(\d+):([^}]+)\}\}(.*)$")
SEC = re.compile(r"^###\s+(\d+\.\d+)\b")

heads = []
counter = {}
for ch in ORDER:
    p = ROOT / "장v2" / (ch + ".md")
    sec = None
    for i, line in enumerate(p.read_text(encoding="utf-8").splitlines(), 1):
        m = SEC.match(line)
        if m:
            sec = m.group(1)
        m = HEAD.match(line)
        if not m:
            continue
        kind, chap, name, rest = m.groups()
        label = "{{%s:%s}}" % (chap, name)
        # name in parentheses right after label, then [status]
        rest = rest.strip()
        if rest.startswith("의 증명") or rest.startswith("의 나머지") or re.match(r"^(\(.*?\) )?의 증명", rest):
            continue
        title = None
        status = None
        mm = re.match(r"^\((.*?)\)\s*(\[.*?\])?\.\*\*", rest)
        if mm:
            title = mm.group(1)
            status = mm.group(2)
        else:
            mm = re.match(r"^(\[.*?\])\.\*\*", rest)
            if mm:
                status = mm.group(1)
        counter[chap] = counter.get(chap, 0) + 1
        heads.append(dict(file=ch, line=i, kind=kind, label=label, title=title,
                          status=status, sec=sec, num="%s.%d" % (chap, counter[chap]),
                          rest=rest[:200]))

print("heads:", len(heads))
json.dump(heads, open(ROOT/"scripts"/"수학검사2"/"검토전체19_M14_heads.json","w",encoding="utf-8"), ensure_ascii=False, indent=0)

# ---- 대응표
tbl = {}
for line in (ROOT/"대조v2"/"라벨_번호_대응표_1114.md").read_text(encoding="utf-8").splitlines():
    if not line.startswith("| `{{"):
        continue
    cells = [c.strip() for c in line.strip().strip("|").split("|")]
    label = cells[0].strip("`")
    tbl[label] = cells
print("대응표 rows:", len(tbl))

# ---- 의존지도 1절
dep = {}
in1 = False
for line in (ROOT/"의존지도_v2.md").read_text(encoding="utf-8").splitlines():
    if line.startswith("## 1."):
        in1 = True; continue
    if line.startswith("### 1.1"):
        in1 = False
    if in1 and line.startswith("| `{{"):
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        dep[cells[0].strip("`")] = cells
print("의존지도 1절 rows:", len(dep))

hl = {h["label"]: h for h in heads}
out = []
out.append("== 장 파일에 있으나 대응표에 없음")
for h in heads:
    if h["label"] not in tbl: out.append("  %s %s:%d" % (h["label"], h["file"], h["line"]))
out.append("== 대응표에 있으나 장 파일에 없음(뺌 표시가 아닌 것)")
for lab, c in tbl.items():
    if lab not in hl: out.append("  %s | %s | %s" % (lab, c[1], c[3]))
out.append("== 대응표 종류/이름/현재번호/절 불일치")
for h in heads:
    c = tbl.get(h["label"])
    if not c: continue
    kind, title, num, sec = c[1], c[2], c[3], c[5]
    t = h["title"] if h["title"] is not None else "—"
    diffs = []
    if kind != h["kind"]: diffs.append("종류 표=%s 장=%s" % (kind, h["kind"]))
    if title != t: diffs.append("이름 표=%r 장=%r" % (title, t))
    if num != h["num"]: diffs.append("번호 표=%s 장=%s" % (num, h["num"]))
    if sec != h["sec"]: diffs.append("절 표=%s 장=%s" % (sec, h["sec"]))
    if diffs: out.append("  %s (%s:%d): %s" % (h["label"], h["file"], h["line"], "; ".join(diffs)))
out.append("== 장 파일에 있으나 의존지도 1절에 없음")
for h in heads:
    if h["label"] not in dep: out.append("  %s %s:%d" % (h["label"], h["file"], h["line"]))
out.append("== 의존지도 1절에 있으나 장 파일에 없음")
for lab in dep:
    if lab not in hl: out.append("  %s" % lab)
out.append("== 의존지도 절/요지/지위 불일치")
for h in heads:
    c = dep.get(h["label"])
    if not c: continue
    sec, gist, status = c[1], c[3], c[4]
    diffs = []
    if sec != h["sec"]: diffs.append("절 지도=%s 장=%s" % (sec, h["sec"]))
    if h["title"] is not None and gist != h["title"]: diffs.append("요지 지도=%r 장=%r" % (gist, h["title"]))
    st = h["status"]
    if st is None:
        st_cmp = "정의" if h["kind"] == "정의" else None
    else:
        st_cmp = st.strip("[]").split(";")[0].strip()
        if h["kind"] == "정의" and not st_cmp: st_cmp = "정의"
    if st_cmp is not None and status != st_cmp: diffs.append("지위 지도=%r 장=%r" % (status, st_cmp))
    if diffs: out.append("  %s (%s:%d): %s" % (h["label"], h["file"], h["line"], "; ".join(diffs)))
out.append("== 머리의 의존 선언 vs 의존지도 머리 입력(본문 인용 앞)")
for h in heads:
    c = dep.get(h["label"])
    if not c: continue
    st = h["status"] or ""
    declared = set(re.findall(r"\{\{\d+:[^}]+\}\}", st.split(";")[0]))
    col = c[5]
    before = col.split("본문 인용:")[0]
    mapped = set(re.findall(r"\{\{\d+:[^}]+\}\}", before))
    if declared != mapped:
        out.append("  %s (%s:%d): 머리=%s 지도=%s" % (h["label"], h["file"], h["line"], sorted(declared), sorted(mapped)))
    # declared labels exist?
    for d in declared:
        if d not in hl: out.append("  !! %s 머리가 인용한 %s 가 장 파일에 없음" % (h["label"], d))
out.append("== 머리 지위 전문(;앞) 비교 — 지도 지위 열")
for h in heads:
    c = dep.get(h["label"])
    if not c or not h["status"]: continue
    st_cmp = h["status"].strip("[]").split(";")[0].strip()
    if c[4] != st_cmp and h["kind"] != "정의":
        out.append("  %s: 지도=%r 장=%r" % (h["label"], c[4], st_cmp))
(ROOT/"scripts"/"수학검사2"/"검토전체19_M14_heads_out.txt").write_text("\n".join(out), encoding="utf-8")
print("\n".join(out[:5]))
print("... written", len(out), "lines")
