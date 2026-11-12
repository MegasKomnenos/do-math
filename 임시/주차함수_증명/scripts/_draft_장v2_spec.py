# -*- coding: utf-8 -*-
"""둘째 판 장별 명세 JSON의 초안을 만든다.

입력: 파견/라벨_v2.md(1절 첫 판 대응, 2절 새 라벨), 구조표_v2.md, 원고.md(첫 판 조립본).
출력: 파견/명세v2/장N.json (N=1..11). 세션이 손으로 고친 뒤 _gen_장v2_파견문.py에 넣는다.

- 첫 판에서 옮기는 진술: 라벨_v2 1절의 행 번호로 원고.md의 진술 범위([머리 행, 다음 머리 또는 절 머리 전 행])를 잡아
  first_edition = {"file": "원고.md", "range": [a, b]}로 적는다.
- 새 진술: 구조표_v2의 그 라벨이 든 셀에서 [r…] 식별자와 § 토큰을 뽑아 sources 후보로 적고 "확인 요"를 붙인다.
  셀 전체를 "cell"에 남겨 세션이 보고 고친다.
"""
import io, json, os, re

ROOT = r"C:\math\임시\주차함수_증명"
LABEL = os.path.join(ROOT, "파견", "라벨_v2.md")
STRUCT = os.path.join(ROOT, "구조표_v2.md")
DRAFT = os.path.join(ROOT, "원고.md")
OUT = os.path.join(ROOT, "파견", "명세v2")
os.makedirs(OUT, exist_ok=True)

lab = io.open(LABEL, encoding="utf-8").read()
struct = io.open(STRUCT, encoding="utf-8").read()
draft_lines = io.open(DRAFT, encoding="utf-8").read().split("\n")

# 첫 판의 머리 행(진술 머리와 절 머리)
HEAD = re.compile(r"^\*\*(정의|정리|명제|보조정리|따름정리) ")
SEC = re.compile(r"^#{2,4} ")
head_lines = sorted(i for i, ln in enumerate(draft_lines, 1) if HEAD.match(ln) or SEC.match(ln))

def stmt_range(start):
    nxt = [h for h in head_lines if h > start]
    end = (nxt[0] - 1) if nxt else len(draft_lines)
    # 꼬리의 빈 줄 제거
    while end > start and not draft_lines[end - 1].strip():
        end -= 1
    return [start, end]

# 1절 표
sec1 = lab.split("## 1. 첫 판 진술의 대응", 1)[1].split("## 2.", 1)[0]
rows = []
for ln in sec1.split("\n"):
    if not ln.startswith("| ") or ln.startswith("| 첫 판 번호") or ln.startswith("|---"):
        continue
    cells = [c.strip() for c in ln.strip().strip("|").split("|")]
    if len(cells) < 5:
        continue
    num, line, kindname, sec, label = cells[:5]
    note = cells[5] if len(cells) > 5 else ""
    m = re.match(r"`(\{\{[^}]+\}\})`", label)
    label = m.group(1) if m else label
    rows.append(dict(num=num, line=int(line) if line.isdigit() else None, kindname=kindname, sec=sec, label=label, note=note))

# 2절 표(새 라벨)
sec2 = lab.split("## 2. 둘째 판의 새 진술", 1)[1].split("## 3.", 1)[0]
new_rows = []
for ln in sec2.split("\n"):
    if not ln.startswith("| ") or ln.startswith("| 장") or ln.startswith("|---"):
        continue
    cells = [c.strip() for c in ln.strip().strip("|").split("|")]
    if len(cells) < 3:
        continue
    ch, label, sec = cells[:3]
    m = re.match(r"`(\{\{[^}]+\}\})`", label)
    new_rows.append(dict(ch=int(ch), label=m.group(1) if m else label, sec=sec))

# 구조표 셀 찾기
def find_cell(label):
    for ln in struct.split("\n"):
        if label in ln and ln.startswith("|"):
            cells = [c.strip() for c in ln.strip().strip("|").split("|")]
            return cells
    return None

REC = re.compile(r"\[(r[0-9a-f]{7})\]")
SECTOK = re.compile(r"§\s*([0-9]+(?:\.[0-9]+)*(?:[–-][0-9]+(?:\.[0-9]+)*)?)")
EVID = re.compile(r"증거 `([^`]+)`")

def sources_from_cell(label, cell_text):
    """라벨이 든 셀에서 그 라벨 근처(라벨 뒤 ~ 다음 라벨 앞)의 [r…]·§·증거 파일을 뽑는다."""
    i = cell_text.find(label)
    seg = cell_text[i:]
    j = seg.find("{{", len(label))
    if j > 0:
        seg = seg[:j]
    recs = REC.findall(seg)
    secs = SECTOK.findall(seg)
    ev = EVID.findall(seg)
    out = []
    rec = recs[0] if recs else None
    for s in secs:
        out.append({"record": rec, "file": (ev[0] if ev else "exposition.md"), "sec": s, "note": "확인 요"})
    if not out and rec:
        out.append({"record": rec, "file": (ev[0] if ev else "exposition.md"), "sec": None, "note": "확인 요: 절 미상"})
    return out, seg.strip()

def kind_of(kindname):
    for k in ("보조정리", "따름정리", "정의", "정리", "명제"):
        if kindname.startswith(k):
            return k
    return ""

specs = {}
for ch in range(1, 12):
    specs[ch] = {"chapter": ch, "title": "", "scope": "", "weights": "", "sections": {}, "defines": [], "free_letters": [], "refs": [], "todo": [], "D_items": [], "notes": []}

for r in rows:
    if r["sec"] in ("뺌", "—", "") or r["label"].startswith("—"):
        continue
    m = re.match(r"\{\{(\d+):", r["label"])
    if not m:
        continue
    ch = int(m.group(1))
    kind = kind_of(r["kindname"])
    name = r["kindname"][len(kind):].strip() if kind and r["kindname"].startswith(kind) else r["kindname"]
    item = {
        "label": r["label"], "kind": kind, "name": name,
        "record_name": "", "process": "옮김", "class": "", "sources": [],
        "first_edition": {"file": "원고.md", "range": stmt_range(r["line"]) if r["line"] else None, "note": f"첫 판 {r['num']}"},
        "inputs": [], "special": r["note"],
    }
    specs[ch]["sections"].setdefault(r["sec"], []).append(item)

for nr in new_rows:
    cells = find_cell(nr["label"])
    cell_text = " | ".join(cells) if cells else ""
    srcs, seg = sources_from_cell(nr["label"], cell_text)
    item = {
        "label": nr["label"], "kind": "", "name": "", "record_name": "", "process": "전개", "class": "",
        "sources": srcs, "first_edition": None, "inputs": [], "special": "", "cell": seg,
    }
    specs[nr["ch"]]["sections"].setdefault(nr["sec"], []).append(item)

def seckey(s):
    try:
        return tuple(int(x) for x in s.split("."))
    except Exception:
        return (999,)

for ch, sp in specs.items():
    secs = []
    for sec in sorted(sp["sections"], key=seckey):
        secs.append({"sec": sec, "title": "", "items": sp["sections"][sec]})
    sp["sections"] = secs
    path = os.path.join(OUT, f"장{ch}.json")
    io.open(path, "w", encoding="utf-8", newline="\n").write(json.dumps(sp, ensure_ascii=False, indent=1))
    n_items = sum(len(s["items"]) for s in secs)
    n_new = sum(1 for s in secs for it in s["items"] if it["process"] == "전개")
    print(f"장{ch}: 절 {len(secs)}, 진술 {n_items} (새 {n_new}) -> {path}")
