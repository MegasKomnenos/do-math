# -*- coding: utf-8 -*-
"""수학검사2 태그 11, 검산 2: 11.3 세 표(읽기 전용).
(가) 「계산 진술과 산술 등급」 열의 (진술: 등급) 쌍을 진술 머리의 「계산 보조(…)」·「계산 증거(…)」 괄호와 대조
(나) 「쓰는 자리」 열의 라벨 실재, 종류 일치, 그리고 그 진술의 블록(진술+증명; 「X의 증명」이면 증명 블록)이 입력 라벨을
    라벨로 인용하는지 / 식 번호로 인용하는지 / 의존지도에 있는지
(다) 81행의 등급 문장과 11.2 표의 등급 열 대조
"""
import re, glob, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
R = "C:/math/임시/주차함수_증명/"
ch11txt = open(R+"장v2/장11.md", encoding="utf-8").read(); ch11 = ch11txt.split("\n")
HEAD = re.compile(r"^\*\*(정의|정리|명제|보조정리|따름정리|문제|추측|관찰|주의|가정|표기)\s+\{\{(\d+:[^}]+)\}\}(.*?)\*\*")
PROOF = re.compile(r"^\*\*(?:정의|정리|명제|보조정리|따름정리)\s+\{\{(\d+:[^}]+)\}\}의 증명\.\*\*")
blocks = {}; proofs = {}; heads = {}; kinds = {}; secof = {}; sections = {}; eqdef = {}
EQ = re.compile(r"\\tag\{(\d+\.\d+)\}")
for f in sorted(glob.glob(R+"장v2/장*.md")):
    lines = open(f, encoding="utf-8").read().split("\n")
    cur = None; sec = None; curp = None
    for i, l in enumerate(lines, 1):
        ms = re.match(r"^###\s+(\d+\.\d+)\b", l)
        if ms: sec = ms.group(1); sections.setdefault(sec, ""); cur = None; curp = None
        m = HEAD.match(l)
        if m and m.group(3).startswith("의 증명"): m = None
        if m:
            cur = m.group(2); kinds[cur] = m.group(1); heads[cur] = m.group(3); blocks.setdefault(cur, ""); secof[cur] = sec; curp = None
        mp = PROOF.match(l)
        if mp: curp = mp.group(1); proofs.setdefault(curp, ""); cur = None
        if cur: blocks[cur] += l + "\n"
        if curp: proofs[curp] += l + "\n"
        if sec: sections[sec] += l + "\n"
        for e in EQ.findall(l):
            eqdef.setdefault(e, cur or curp or ("§"+str(sec)))
# 진술 블록 안에 증명이 이어지는 경우(별도 증명 머리 없이) blocks가 이미 포함. 별도 증명이 있으면 proofs.
def fulltext(lab):
    return blocks.get(lab, "") + proofs.get(lab, "")
dep = {}
for l in open(R+"의존지도_v2.md", encoding="utf-8"):
    m = re.match(r"\| `\{\{([^}]+)\}\}` \| ([^|]*) \| [^|]* \| [^|]* \| [^|]* \| ([^|]*) \|", l)
    if m: dep[m.group(1)] = set(re.findall(r"\{\{([^}]+)\}\}", m.group(3)))
# 진술 라벨이 세운 식 번호(그 블록 안의 \tag)
eqs_of = {}
for e, owner in eqdef.items(): eqs_of.setdefault(owner, set()).add(e)
print("블록", len(blocks), "별도 증명", len(proofs), "식 번호", len(eqdef))
GR = ["정확 정수·유리수", "방향 반올림 구간", "binary64 사전 오차 해석", "인증 아님"]
def grades_in(s): return set(g for g in GR if g in s)
def labset(s):
    out = []
    for m in re.finditer(r"(정의|정리|명제|보조정리|따름정리)\s+\{\{(\d+:[^}]+)\}\}((?:·\{\{\d+:[^}]+\}\})*)", s):
        out.append((m.group(1), m.group(2)))
        for x in re.findall(r"\{\{(\d+:[^}]+)\}\}", m.group(3)): out.append((m.group(1), x))
    return out
# ---------- (가)
print("\n===== (가) 11.3 등급 열 vs 진술 머리 =====")
in113 = False; table = 0; g113 = {}
for ln, line in enumerate(ch11, 1):
    if line.startswith("### 11.3"): in113 = True
    if line.startswith("### 11.4"): in113 = False
    if not in113 or not line.startswith("| ") or line.startswith("| 입력"): continue
    cells = [c.strip() for c in line.strip().strip("|").split(" | ")]
    if cells[1] == "없음": continue
    for grp in cells[1].split("; "):
        stm, grade = grp.rsplit(": ", 1)
        for k, s in labset(stm):
            g113[s] = (ln, grade)
            h = heads.get(s, "<없음>")
            hg = set()
            for mm in re.finditer(r"계산 (?:보조|증거)\(([^)]*)\)", h): hg |= grades_in(mm.group(1))
            ok = "OK" if hg == grades_in(grade) else ("<<< 머리에 계산 표지 없음" if not hg else "<<< 다름")
            if kinds.get(s) != k: ok += f" <<< 종류 {k} vs 머리 {kinds.get(s)}"
            print(f"  행{ln} {k} {s}: 11.3 '{grade}' / 머리 '{h[:140]}' {ok}")
# 등급 열의 진술은 세 표에서 한 번만 나오는가
cnt = {}
in113 = False
for ln, line in enumerate(ch11, 1):
    if line.startswith("### 11.3"): in113 = True
    if line.startswith("### 11.4"): in113 = False
    if not in113 or not line.startswith("| ") or line.startswith("| 입력"): continue
    cells = [c.strip() for c in line.strip().strip("|").split(" | ")]
    for k, s in labset(cells[1]): cnt[s] = cnt.get(s, 0) + 1
print("  등급 열에 두 번 이상 나온 진술:", [s for s, c in cnt.items() if c > 1])
# ---------- (나)
print("\n===== (나) 쓰는 자리 대조 =====")
in113 = False
pairs = 0; unresolved = []
for ln, line in enumerate(ch11, 1):
    if line.startswith("### 11.3"): in113 = True
    if line.startswith("### 11.4"): in113 = False
    if not in113 or not line.startswith("| ") or line.startswith("| 입력"): continue
    cells = [c.strip() for c in line.strip().strip("|").split(" | ")]
    inputs = [s for k, s in labset(cells[0])]
    print(f"\n--- 행{ln}: {cells[0][:80]}  입력 {inputs}")
    for ci, cell in enumerate(cells[2:], 3):
        # 각 사용 자리 항목: 쉼표로 가르되 괄호 안 쉼표는 보존
        parts = [p.strip() for p in re.split(r",\s+(?![^()]*\))", cell)]
        # 괄호가 뒤따르는 항목의 괄호는 그 앞의 괄호 없는 항목들에도 적용한다(「A, B, C(정리 X)」 = 셋 다 X)
        parsed = []
        for p in parts:
            mpar = re.match(r"^(.*?)\(([^()]*)\)\s*$", p)
            main, par = (mpar.group(1), mpar.group(2)) if mpar else (p, "")
            parsed.append([p, main, par])
        pend = []
        for e in parsed:
            if e[2]:
                for q in pend: q[2] = e[2]
                pend = []
            else: pend.append(e)
        for p, main, par in parsed:
            users = [(k, s) for k, s in labset(main) if s not in inputs]
            spec = [s for k, s in labset(par) if s in inputs]
            targets = spec if spec else inputs
            is_proof = "의 증명" in main
            for k, u in users:
                pairs += 1
                if u not in blocks:
                    print(f"   <<< 라벨 없음 {u}"); unresolved.append((ln, u, "라벨 없음")); continue
                kk = "" if kinds.get(u) == k else f" <<< 종류 {k} vs 머리 {kinds.get(u)}"
                txt = fulltext(u)
                for t in targets:
                    via_lab = ("{{"+t+"}}") in txt
                    via_eq = sorted(e for e in eqs_of.get(t, set()) if ("("+e+")") in txt)
                    via_dep = t in dep.get(u, set())
                    flag = "" if (via_lab or via_eq) else ("  (의존지도만)" if via_dep else "  <<< 인용 못 찾음")
                    if flag: unresolved.append((ln, u, t, flag.strip()))
                    print(f"   열{ci} {k} {u}{'(증명)' if is_proof else ''} ← {t}: 라벨 {via_lab} 식 {via_eq} 의존지도 {via_dep}{flag}{kk}")
            # 라벨 없는 사용 자리(절 번호·고리)
            if not users:
                print(f"   열{ci} 라벨 없는 자리: 「{p[:80]}」 → 수동 확인")
print("\n쌍 수", pairs, "/ 미해결", len(unresolved))
for x in unresolved: print("  ", x)
# ---------- (다)
print("\n===== (다) 81행 등급 문장 vs 11.2 등급 열 =====")
for ln, line in enumerate(ch11, 1):
    m = re.match(r"\| 부록 D\.\{\{(D:[^}]+)\}\} \| (.*?) \| (.*?) \|", line)
    if m and ("binary64" in m.group(3) or "인증 아님" in m.group(3)):
        print(f"  행{ln} {m.group(1)}: 등급 열 '{m.group(3)}' 진술 {re.findall(r'{{(\d+:[^}]+)}}', m.group(2))}")
print("  {{3:old-3-5}}를 입력으로 둔 진술(의존지도):", [u for u, d in dep.items() if "3:old-3-5" in d])
print("  {{3:old-3-5}}를 본문에서 인용하는 블록:", [u for u, b in blocks.items() if "{{3:old-3-5}}" in b and u != "3:old-3-5"], [u for u, b in proofs.items() if "{{3:old-3-5}}" in b])
# 11.3 등급 열 진술 vs 11.2 등급(항목 단위)
g112 = {}
for ln, line in enumerate(ch11, 1):
    m = re.match(r"\| 부록 D\.\{\{(D:[^}]+)\}\} \| (.*?) \| (.*?) \|", line)
    if m:
        for s in re.findall(r"\{\{(\d+:[^}]+)\}\}", m.group(2)): g112.setdefault(s, []).append((m.group(1), m.group(3)))
print("\n  11.3 등급 열 진술 가운데 11.2 등급과 집합이 다른 것:")
for s, (ln, g) in g113.items():
    got = g112.get(s)
    if not got: print(f"   행{ln} {s}: 11.2 표에 없음 ('{g}')"); continue
    gset = set()
    for d, gg in got: gset |= grades_in(gg)
    if gset != grades_in(g): print(f"   행{ln} {s}: 11.3 '{g}' vs 11.2 {got}")
print("  11.2 진술 중 11.3 등급 열에 없는 것:", sorted(set(g112) - set(g113)))
