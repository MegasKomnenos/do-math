# -*- coding: utf-8 -*-
"""G14: 의존지도_v2.md 1절의 행(절·지위·입력 라벨·기록 식별자·요지)을 현행 장 파일에서 다시 뽑아 대조한다. 읽기만 한다."""
import io, os, re, sys
ROOT = r"C:\math\임시\주차함수_증명"
sys.path.insert(0, os.path.join(ROOT, "scripts"))
import importlib
DD = importlib.import_module("_의존_도달")
LAB = re.compile(r"\{\{(\d+:[A-Za-z][A-Za-z0-9\-]*)\}\}")
BR = re.compile(r"\[([^\]]*)\]\.\*\*")
RID = re.compile(r"\br[0-9a-f]{7}\b")
PIPE_ESC = "\\|"


def cells(line):
    s = line.strip()
    if s.startswith("|"):
        s = s[1:]
    if s.endswith("|"):
        s = s[:-1]
    s = s.replace(PIPE_ESC, "\u0001")
    return [c.replace("\u0001", PIPE_ESC).strip() for c in s.split("|")]


def status_and_ids(head):
    m = BR.search(head)
    if not m:
        return "정의", set()
    inner = m.group(1)
    if ";" in inner:
        a, b = inner.split(";", 1)
        return a.strip(), set(RID.findall(b))
    ids = set(RID.findall(inner))
    if ids and not RID.sub("", inner).strip(" ,"):
        return "정의", ids
    return inner.strip(), set()


st = DD.parse_chapters()
order = sorted(st, key=lambda k: st[k]["order"])
cur = set(st)

txt = io.open(os.path.join(ROOT, "의존지도_v2.md"), encoding="utf-8").read()
i2 = txt.find("\n### 1.1 ")
rows = {}
for ln_no, ln in enumerate(txt[:i2].split("\n"), 1):
    if ln.startswith("| `{{"):
        c = cells(ln)
        if len(c) != 10:
            print("[칸 수 이상]", ln_no, len(c), ln[:80])
            continue
        key = c[0].strip("`{}")
        rows[key] = dict(section=c[1], first=c[2], gist=c[3], status=c[4], inputs=c[5], claims=c[6], lit=c[7], appd=c[8], note=c[9], line=ln_no)

print("표 행:", len(rows), "본문 진술:", len(cur))
for k in order:
    s = st[k]
    r = rows.get(k)
    if not r:
        print("[표에 없음]", k, s["section"])
        continue
    probs = []
    if r["section"] != s["section"]:
        probs.append("절 표 %s ≠ 본문 %s" % (r["section"], s["section"]))
    status, ids = status_and_ids(s["head"])
    if r["status"].replace("／", "|") != status:
        probs.append("지위 표 %r ≠ 본문 %r" % (r["status"], status))
    gist = s["name"].strip().replace("|", "／")
    if gist and r["gist"] != gist:
        probs.append("요지 표 %r ≠ 본문 %r" % (r["gist"], gist))
    hl = set(x for x in s["head_labels"] if x in cur)
    bl = set(x for x in s["body_labels"] if x in cur) - hl
    inp = r["inputs"]
    if "본문 인용:" in inp:
        a, b = inp.split("본문 인용:", 1)
    else:
        a, b = inp, ""
    thl = set(LAB.findall(a))
    tbl = set(LAB.findall(b))
    if thl != hl:
        probs.append("머리 인용 표에만 %s / 본문에만 %s" % (sorted(thl - hl), sorted(hl - thl)))
    if tbl != bl:
        probs.append("본문 인용 표에만 %s / 본문에만 %s" % (sorted(tbl - bl), sorted(bl - tbl)))
    tids = set(RID.findall(r["claims"]))
    if tids != ids:
        probs.append("기록 식별자 표 %s ≠ 머리 %s" % (sorted(tids), sorted(ids)))
    if s.get("defer") and "뒤로 미룬 증명" not in r["note"]:
        probs.append("뒤로 미룬 증명 %s 표 비고에 없음" % s["defer"])
    if ("계산 보조" in status or "계산 증거" in status) and r["appd"] == "없음":
        probs.append("지위에 계산 표시인데 부록 D 열 「없음」")
    if probs:
        print("[불일치] %s (표 행 %d; %s): %s" % (k, r["line"], s["section"], " | ".join(probs)))
for k in rows:
    if k not in cur:
        print("[본문에 없음]", k, rows[k]["line"])
