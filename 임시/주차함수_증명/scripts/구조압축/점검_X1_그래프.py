# -*- coding: utf-8 -*-
"""점검 X1(고아와 죽은 가지) — 현행 장 파일에서 진술 머리와 인용을 전수로 뽑아 라벨 그래프를 만든다.

읽는 것: 장v2/장1·2·3·4·5A·5B·6·7A·7B·8·10·11.md, 장v2/부록D_장*.md (현행 작업 트리; 읽은 시각을 찍는다).
쓰는 것: 이 파일의 _out.txt 뿐.

진술 머리: ^**<종류> {{장:라벨}} … (종류 ∈ 정의·명제·정리·보조정리·따름정리)
부록 D 항목: ^### D.{{D:라벨}} …
블록: 머리 행부터 — 정의가 아니면 그 뒤 첫 ∎ 행까지(다음 머리·절 머리 전에 있을 때), 정의이거나 ∎가 없으면
      다음 「**」로 시작하는 행·절 머리·∎ 행 직전까지.
선: 블록 안의 인용 {{T}} → T는 S의 입력(T -> S). 블록 밖 인용은 「서술 인용」으로 따로 센다.
도달: 주 정리 1:main-theorem에서 거꾸로(입력 쪽으로) 걷는다.
"""
import re, sys, collections, datetime, os
from pathlib import Path

ROOT = Path(r"C:/math/임시/주차함수_증명")
CH = ["1", "2", "3", "4", "5A", "5B", "6", "7A", "7B", "8", "10", "11"]
CH_FILES = [ROOT / "장v2" / f"장{c}.md" for c in CH]
D_FILES = sorted((ROOT / "장v2").glob("부록D_장*.md"))
OUT = Path(__file__).with_name(Path(__file__).stem + "_out.txt")

HEAD = re.compile(r"^\*\*(정의|명제|정리|보조정리|따름정리) \{\{([0-9A-Za-z]+:[^}]+)\}\}(?!의 증명)")
PROOF = re.compile(r"^\*\*(정의|명제|정리|보조정리|따름정리) \{\{([0-9A-Za-z]+:[^}]+)\}\}의 증명\.\*\*")
PROOFSEC = re.compile(r"^#{2,4} .*mathsf W\$의 증명")  # 5B 5.5절: 정리 5:old-5-18의 증명이 절 전체
DHEAD = re.compile(r"^### D\.\{\{(D:[^}]+)\}\}")
CITE = re.compile(r"\{\{([0-9A-Za-z]+:[^}]+)\}\}")
SEC = re.compile(r"^(##+) ")

out_lines = []
def P(*a):
    s = " ".join(str(x) for x in a)
    out_lines.append(s)

now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
P(f"점검 X1 라벨 그래프 — 읽은 시각 {now}")
for f in CH_FILES + D_FILES:
    st = f.stat()
    P(f"  {f.name:16s} {st.st_size:8d}B  mtime {datetime.datetime.fromtimestamp(st.st_mtime).strftime('%H:%M:%S')}  lines {sum(1 for _ in open(f, encoding='utf-8'))}")

# ---------- 파싱 ----------
heads = {}        # label -> dict(kind, file, line, section, block_end)
dentries = {}     # D label -> dict(file, line, title, block_end)
block_cites = collections.defaultdict(list)   # S -> [(T, file, line)]
prose_cites = collections.defaultdict(list)   # T -> [(file, line, section, prev_head)]
all_cites = collections.defaultdict(list)     # T -> [(file, line, inblock_of or None)]
dup_heads = []
deferred_proofs = []
section_proof_cites = []

def parse_chapter(f):
    lines = open(f, encoding="utf-8").read().split("\n")
    n = len(lines)
    # 먼저 머리·절 머리·∎ 위치
    head_at = {}
    for i, L in enumerate(lines):
        m = HEAD.match(L)
        if m:
            head_at[i] = (m.group(1), m.group(2))
    sec_at = {i for i, L in enumerate(lines) if SEC.match(L)}
    qed_at = {i for i, L in enumerate(lines) if "∎" in L}
    bold_at = {i for i, L in enumerate(lines) if L.startswith("**")}
    proof_at = {}
    for i, L in enumerate(lines):
        m = PROOF.match(L)
        if m:
            proof_at[i] = (m.group(1), m.group(2))
    head_idx = sorted(set(head_at) | set(proof_at))
    # 블록 끝 계산 — 진술 블록은 머리 행부터 첫 빈 행 직전까지(진술문만);
    # 증명 블록은 「**증명.**」(또는 「**증명 개관.**」·미룬 「**… 증명.**」) 행부터 첫 ∎ 행까지, 바로 앞 머리의 진술에 귀속.
    blank_at = {i for i, L in enumerate(lines) if L.strip() == ""}
    proof_start = {i for i, L in enumerate(lines) if L.startswith("**증명.**") or L.startswith("**증명 개관.**")}
    blocks = []  # (start, end_inclusive, label, kind)
    for j, i in enumerate(head_idx):
        is_proof = i in proof_at
        kind, lab = (proof_at[i] if is_proof else head_at[i])
        nxt = head_idx[j + 1] if j + 1 < len(head_idx) else n
        nsec = min([s for s in sec_at if s > i] + [n])
        limit = min(nxt, nsec)
        if is_proof:
            kind = "증명"
            q = [k for k in qed_at if i <= k < limit]
            end = q[0] if q else limit - 1
            blocks.append((i, end, lab, kind))
            continue
        # 진술 블록
        b = [k for k in blank_at if k > i]
        end = (b[0] - 1) if b else (limit - 1)
        end = min(end, limit - 1)
        blocks.append((i, end, lab, kind))
        # 그 머리에 딸린 증명 블록(다음 머리 전까지의 「**증명.**」 행들)
        for ps in sorted(k for k in proof_start if i < k < limit):
            if ps <= end:
                continue
            q = [k for k in qed_at if ps <= k < limit]
            pend = q[0] if q else min([k for k in blank_at if k > ps] + [limit]) - 1
            blocks.append((ps, pend, lab, "증명"))
    # 현재 절
    cur_sec = ""
    sec_of_line = {}
    for i, L in enumerate(lines):
        m = SEC.match(L)
        if m:
            cur_sec = L.strip("# ").strip()[:40]
        sec_of_line[i] = cur_sec
    # 머리 등록(증명 블록은 머리가 아니다)
    for (s, e, lab, kind) in blocks:
        if kind == "증명":
            if s in proof_at:
                deferred_proofs.append((lab, f.name, s + 1, e + 1))
            continue
        if lab in heads:
            dup_heads.append((lab, f.name, s + 1, heads[lab]["file"], heads[lab]["line"]))
        heads[lab] = dict(kind=kind, file=f.name, line=s + 1, section=sec_of_line[s], block_end=e + 1)
    # 인용 귀속
    def block_of(i):
        for (s, e, lab, kind) in blocks:
            if s <= i <= e:
                return lab
        return None
    # 절 전체가 한 정리의 증명인 절(5B 5.5): 그 절의 블록 밖 인용은 그 정리에 귀속
    proofsec_label = None
    proofsec_range = None
    for i, L in enumerate(lines):
        if PROOFSEC.match(L):
            nsec = min([s for s in sec_at if s > i and lines[s].startswith("### ")] + [n])
            first_heads = [k for k in sorted(head_at) if i < k < nsec]
            if first_heads:
                proofsec_label = head_at[first_heads[0]][1]
                proofsec_range = (i, nsec)
    prev_head = None
    for i, L in enumerate(lines):
        if i in head_at:
            prev_head = head_at[i][1]
        for m in CITE.finditer(L):
            T = m.group(1)
            S = block_of(i)
            if S is None and proofsec_range and proofsec_range[0] <= i < proofsec_range[1] and T != proofsec_label:
                S = proofsec_label
                section_proof_cites.append((S, T, f.name, i + 1))
            if S is not None and T != S:
                block_cites[S].append((T, f.name, i + 1))
            elif S is None:
                prose_cites[T].append((f.name, i + 1, sec_of_line[i], prev_head))
            all_cites[T].append((f.name, i + 1, S))

def parse_D(f):
    lines = open(f, encoding="utf-8").read().split("\n")
    n = len(lines)
    starts = [(i, DHEAD.match(L).group(1)) for i, L in enumerate(lines) if DHEAD.match(L)]
    for j, (i, lab) in enumerate(starts):
        end = starts[j + 1][0] - 1 if j + 1 < len(starts) else n - 1
        dentries[lab] = dict(file=f.name, line=i + 1, title=lines[i][:120], block_end=end + 1)
        for k in range(i, end + 1):
            for m in CITE.finditer(lines[k]):
                T = m.group(1)
                if T != lab:
                    block_cites[lab].append((T, f.name, k + 1))  # D 항목이 확인하는 진술(역방향 포인터; 도달에는 쓰지 않음)
                    all_cites[T].append((f.name, k + 1, lab))

for f in CH_FILES:
    parse_chapter(f)
for f in D_FILES:
    parse_D(f)

P("")
P(f"진술 머리 {len(heads)}개, 부록 D 항목 {len(dentries)}개")
kinds = collections.Counter(h["kind"] for h in heads.values())
P("  종류별:", dict(kinds))
bych = collections.Counter(l.split(":")[0] for l in heads)
P("  장별:", dict(sorted(bych.items(), key=lambda x: (len(x[0]), x[0]))))
if dup_heads:
    P("  !! 중복 머리:", dup_heads)
P(f"  미룬 증명 블록 {len(deferred_proofs)}: {[(l,f,a,b) for (l,f,a,b) in deferred_proofs]}")
P(f"  절 전체가 증명인 절의 블록 밖 인용(정리에 귀속) {len(section_proof_cites)}: {sorted(set((S,T) for (S,T,f,l) in section_proof_cites))}")

# 정의되지 않은 라벨 인용
undefined = sorted(T for T in all_cites if T not in heads and T not in dentries)
P("")
P(f"머리 없는 라벨 인용 {len(undefined)}개:")
for T in undefined:
    P("   ", T, "<-", [(f, l) for (f, l, S) in all_cites[T]][:6])

# ---------- 그래프 ----------
back = collections.defaultdict(set)   # S -> inputs
fwd = collections.defaultdict(set)    # T -> consumers
for S, lst in block_cites.items():
    if S.startswith("D:"):
        continue
    for (T, f, l) in lst:
        if T in heads or T in dentries:
            back[S].add(T)
            fwd[T].add(S)

MAIN = "1:main-theorem"
def reach_back(start):
    seen = set(); st = [start]
    while st:
        x = st.pop()
        if x in seen:
            continue
        seen.add(x)
        st.extend(back[x])
    return seen

R = reach_back(MAIN)
R_heads = {x for x in R if x in heads}
R_D = {x for x in R if x in dentries}
P("")
P(f"주 정리 {MAIN}에서 거꾸로(블록 안 인용으로) 도달되는 진술 {len(R_heads)}/{len(heads)}, 부록 D 항목 {len(R_D)}/{len(dentries)}")
P("  장별 도달/전체:", {c: f"{sum(1 for x in R_heads if x.split(':')[0]==c)}/{bych[c]}" for c in sorted(bych, key=lambda x:(len(x),x))})

def sortkey(lab):
    return (heads[lab]["file"], heads[lab]["line"]) if lab in heads else (dentries[lab]["file"], dentries[lab]["line"])

P("")
P("=== 도달되지 않는 진술(블록 안 인용 기준) — 자리·종류·서술 인용·블록 밖 인용 ===")
unreached = sorted((x for x in heads if x not in R_heads), key=sortkey)
for x in unreached:
    h = heads[x]
    cons = sorted(fwd[x])
    pc = prose_cites.get(x, [])
    P(f"  {x:28s} {h['kind']:5s} {h['file']}:{h['line']:<5d} [{h['section'][:28]}]  블록인용(소비처 진술) {len(cons)}: {cons[:8]}  서술인용 {len(pc)}: {[(f,l) for (f,l,s,p) in pc][:8]}")

P("")
P("=== 도달되지 않는 부록 D 항목 ===")
for x in sorted((x for x in dentries if x not in R_D), key=sortkey):
    d = dentries[x]
    P(f"  {x:28s} {d['file']}:{d['line']}  인용 자리: {[(f,l,S) for (f,l,S) in all_cites.get(x, [])][:8]}")

P("")
P("=== 인용 0인 진술(블록 안·밖 모두; 자기 머리 제외) ===")
zero = sorted((x for x in heads if not fwd[x] and not prose_cites.get(x)), key=sortkey)
for x in zero:
    h = heads[x]
    P(f"  {x:28s} {h['kind']:5s} {h['file']}:{h['line']} [{h['section'][:30]}]")

P("")
P("=== 서술 인용만 있는 진술(블록 안 소비처 0, 블록 밖 인용 ≥1) ===")
for x in sorted((x for x in heads if not fwd[x] and prose_cites.get(x)), key=sortkey):
    h = heads[x]
    pc = prose_cites[x]
    P(f"  {x:28s} {h['kind']:5s} {h['file']}:{h['line']}  서술인용 {len(pc)}: {[(f,l,p) for (f,l,s,p) in pc][:10]}")

P("")
P("=== 소비처가 같은 장 안에만 있는 진술 가운데, 그 소비처들이 모두 도달 밖인 것(죽은 가지 묶음) ===")
for x in sorted(unreached, key=sortkey):
    cons = fwd[x]
    if cons and all(c not in R for c in cons):
        P(f"  {x:28s} -> 소비처 {sorted(cons)} (모두 도달 밖)")

# 도달된 진술의 장별 소비처 분포(참고: 결정 K6 3.1절과 같은 꼴)
P("")
P("=== 모든 진술의 소비처(블록 안) 장별 분포와 서술 인용 수 ===")
for x in sorted(heads, key=sortkey):
    cons = fwd[x]
    dist = collections.Counter(c.split(":")[0] for c in cons)
    mark = "" if x in R_heads else "  [도달 밖]"
    P(f"  {x:28s} {heads[x]['kind']:5s} {heads[x]['file']}:{heads[x]['line']:<5d} 소비처 {dict(sorted(dist.items()))}  서술 {len(prose_cites.get(x, []))}{mark}")

# 부록 D 항목 인용 수
P("")
P("=== 부록 D 항목별 인용 자리(장 파일 + 11장) ===")
for x in sorted(dentries, key=sortkey):
    cites = [(f, l, S) for (f, l, S) in all_cites.get(x, [])]
    P(f"  {x:28s} {dentries[x]['file']}:{dentries[x]['line']:<4d} 인용 {len(cites)}: {cites[:10]}")

# 선 목록(도달 검산용)
P("")
P("=== 선 목록(입력 -> 소비처; 블록 안 인용) ===")
for S in sorted(back, key=lambda s: sortkey(s) if (s in heads or s in dentries) else ("zzz", 0)):
    P(f"  {S:28s} <- {sorted(back[S])}")

OUT.write_text("\n".join(out_lines) + "\n", encoding="utf-8", newline="\n")
print("\n".join(out_lines[:60]))
print(f"... ({len(out_lines)} lines) -> {OUT}")
