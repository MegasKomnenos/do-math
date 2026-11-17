# -*- coding: utf-8 -*-
"""점검 X1(고아와 죽은 가지) — 글자·낱말·식 번호·등록부 수의 본문 출현을 센다(색인; 판단은 원문으로).

(1) 부록 A의 기호 행마다 그 글자(들)의 본문 출현(장 파일 12 + 부록 D) — 공백·중괄호를 지운 꼴로 센다.
    「밑글자」(첨자·인수·윗첨자를 뗀 앞부분)의 출현도 함께 센다.
(2) 본문의 이름 없는 굵은 정의 문단 「**낱말.**」의 낱말이 뒤에 몇 번 나오는가.
(3) 부록 C 첫 표(이 글의 용어)의 낱말이 본문에 몇 번 나오는가.
(4) \\tag{n.m} 식 번호마다 참조 「(n.m)」의 수(태그 행 제외).
(5) 1장 등록부의 수마다 장별 출현.
읽기만 한다. 출력은 _out.txt.
"""
import re, collections, datetime
from pathlib import Path

ROOT = Path(r"C:/math/임시/주차함수_증명")
CH = ["1", "2", "3", "4", "5A", "5B", "6", "7A", "7B", "8", "10", "11"]
CH_FILES = [ROOT / "장v2" / f"장{c}.md" for c in CH]
D_FILES = sorted((ROOT / "장v2").glob("부록D_장*.md"))
BODY = CH_FILES + D_FILES
OUT = Path(__file__).with_name(Path(__file__).stem + "_out.txt")
out = []
def P(*a): out.append(" ".join(str(x) for x in a))

texts = {f.name: f.read_text(encoding="utf-8") for f in BODY}
def norm(s):
    return re.sub(r"[\s{}]", "", s)
ntexts = {k: norm(v) for k, v in texts.items()}

P(f"점검 X1 글자·낱말 — 읽은 시각 {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

# ---------- (1) 부록 A ----------
A = (ROOT / "장v2" / "부록A.md").read_text(encoding="utf-8").split("\n")
sec = ""
rows = []
for L in A:
    if L.startswith("### "):
        sec = L[4:].strip()
    if L.startswith("| $") or L.startswith("| \\(") or (L.startswith("| ") and "$" in L.split("|")[1]):
        cells = [c.strip() for c in L.strip().strip("|").split("|")]
        if len(cells) >= 3:
            rows.append((sec, cells[0], cells[1][:80], cells[2]))
P("")
P(f"(1) 부록 A 기호 행 {len(rows)}개 — 본문 출현(엄격 꼴 / 밑글자 꼴). 9장 절은 V6이 지우므로 표시만.")
def glyphs_of(cell):
    gs = re.findall(r"\$([^$]+)\$", cell)
    res = []
    for g in gs:
        for part in re.split(r"\s*(?:·|,|;)\s*", g):
            part = part.strip()
            if part:
                res.append(part)
    return res
def base_of(g):
    g2 = re.sub(r"\(.*$", "", g)
    g2 = re.sub(r"(_|\^).*$", "", g2) if not g2.startswith("\\") else re.sub(r"(?<=\w)(_|\^).*$", "", g2)
    return g2
low = []
for (sec, cell, meaning, defsec) in rows:
    gs = glyphs_of(cell)
    if not gs:
        continue
    strict = collections.Counter(); base = collections.Counter()
    for g in gs:
        ng = norm(g)
        for fn, nt in ntexts.items():
            c = nt.count(ng)
            if c: strict[fn] += c
        bg = norm(base_of(g))
        if len(bg) >= 2:
            for fn, nt in ntexts.items():
                c = nt.count(bg)
                if c: base[fn] += c
    s_tot = sum(strict.values()); b_tot = sum(base.values())
    flag = ""
    if s_tot <= 1: flag = "  <<< 엄격 꼴 출현 ≤1"
    if s_tot <= 3 or flag:
        low.append((sec, cell, meaning, defsec, s_tot, dict(strict), b_tot, dict(base), flag))
for (sec, cell, meaning, defsec, s_tot, strict, b_tot, base, flag) in low:
    P(f"  [{sec[:14]}] {cell[:60]:60s} | {meaning[:50]:50s} | 절 {defsec:10s} | 엄격 {s_tot} {strict} | 밑글자 {b_tot}{flag}")

# ---------- (2) 굵은 정의 문단 ----------
P("")
P("(2) 이름 없는 굵은 정의 문단 「**낱말.**」 — 낱말의 본문 출현(정의 자리 포함)")
BOLD = re.compile(r"^\*\*([^*{]{1,40})\.\*\*")
for f in CH_FILES:
    for i, L in enumerate(f.read_text(encoding="utf-8").split("\n"), 1):
        m = BOLD.match(L)
        if not m or m.group(1) in ("증명",):
            continue
        term = m.group(1).strip()
        key = re.sub(r"\$[^$]*\$", "", term).strip()
        cnt = collections.Counter()
        if key:
            for fn, t in texts.items():
                c = t.count(key)
                if c: cnt[fn] += c
        P(f"  {f.name}:{i:<5d} 「{term}」 → 「{key}」 출현 {sum(cnt.values())} {dict(cnt)}")

# ---------- (3) 부록 C 낱말 ----------
P("")
P("(3) 부록 C 「이 글의 용어」 낱말 — 본문 출현 ≤2인 것만(같은 낱말의 변화형은 잡히지 않을 수 있다)")
C = (ROOT / "장v2" / "부록C.md").read_text(encoding="utf-8").split("\n")
inside = False
for L in C:
    if L.startswith("### "):
        inside = L.startswith("### 낱말")
        continue
    if inside and L.startswith("| ") and not L.startswith("| 이 글의") and not L.startswith("|---"):
        cells = [c.strip() for c in L.strip().strip("|").split("|")]
        words = [w.strip() for w in re.split(r"[,·;]", re.sub(r"\(.*?\)", "", cells[0])) if w.strip()]
        for w in words:
            w2 = re.sub(r"\$[^$]*\$", "", w).strip()
            if len(w2) < 2:
                continue
            cnt = collections.Counter()
            for fn, t in texts.items():
                c = t.count(w2)
                if c: cnt[fn] += c
            tot = sum(cnt.values())
            if tot <= 2:
                P(f"  「{w2}」(행: {cells[0][:40]}; 절 {cells[-1][:20]}) 출현 {tot} {dict(cnt)}")

# ---------- (4) 식 번호 ----------
P("")
P("(4) \\tag 식 번호 — 참조 0인 태그(태그 행 자체 제외; 「(n.m)」 꼴로 셈)")
tags = {}
for f in CH_FILES:
    for i, L in enumerate(f.read_text(encoding="utf-8").split("\n"), 1):
        for m in re.finditer(r"\\tag\{([0-9]+\.[0-9]+[a-z]?)\}", L):
            tags[m.group(1)] = (f.name, i)
alltext_lines = []
for f in BODY:
    for i, L in enumerate(texts[f.name].split("\n"), 1):
        alltext_lines.append((f.name, i, L))
refcount = collections.Counter()
refwhere = collections.defaultdict(list)
for (fn, i, L) in alltext_lines:
    for m in re.finditer(r"\(([0-9]+\.[0-9]+[a-z]?)\)", L):
        t = m.group(1)
        if t in tags and not (tags[t] == (fn, i)):
            refcount[t] += 1
            refwhere[t].append((fn, i))
P(f"  태그 {len(tags)}개")
def tkey(t):
    a, b = t.split(".")
    return (int(a), int(re.sub(r"[a-z]", "", b)), b)
for t in sorted(tags, key=tkey):
    if refcount[t] == 0:
        P(f"  ({t}) {tags[t][0]}:{tags[t][1]}  참조 0")
P("  참조 1인 태그:", [f"({t}) {tags[t][0]}:{tags[t][1]}<-{refwhere[t][0]}" for t in sorted(tags, key=tkey) if refcount[t] == 1])

# ---------- (5) 등록부 수 ----------
P("")
P("(5) 1장 등록부의 수 — 장별 출현(토큰 경계로 셈; 수식 안 포함)")
nums = ["6667", "6668", "25000", "25001", "10000", "10001", "2000", "2001", "140", "141", "500", "501", "840", "841", "102", "103", "0.48", "6600", "4000", "43", "50", "301", "170", "64", "20000", "20001", "50000", "50001", "16", "1.15", "1.4", "10", "597", "19880", "121"]
for nmb in nums:
    pat = re.compile(r"(?<![0-9.])" + re.escape(nmb) + r"(?![0-9])")
    cnt = {}
    for fn, t in texts.items():
        c = len(pat.findall(t))
        if c: cnt[fn] = c
    P(f"  {nmb:7s} {cnt}")

OUT.write_text("\n".join(out) + "\n", encoding="utf-8", newline="\n")
print("\n".join(out))
