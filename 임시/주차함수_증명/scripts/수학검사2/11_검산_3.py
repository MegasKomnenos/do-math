# -*- coding: utf-8 -*-
"""수학검사2 태그 11, 검산 3: 11.4 문헌 표 25행의 「쓰인 자리」 전수 대조(읽기 전용).
행마다 문헌을 찾는 정규식을 두고, 본문(장1–10, 부록 D)에서 그 문헌 언급이 있는 자리(절, 진술 라벨, 증명, D 항목)를 모아
「쓰인 자리」 열의 각 항목(라벨·절·D 항목)이 그 집합에 있는지, 거꾸로 집합에 있으나 열에 없는 자리가 무엇인지 적는다.
"""
import re, glob, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
R = "C:/math/임시/주차함수_증명/"
HEAD = re.compile(r"^\*\*(정의|정리|명제|보조정리|따름정리|문제|추측|관찰|주의|가정|표기)\s+\{\{(\d+:[^}]+)\}\}")
PROOF = re.compile(r"^\*\*(?:정의|정리|명제|보조정리|따름정리)\s+\{\{(\d+:[^}]+)\}\}의 증명\.\*\*")
locs = []  # (file, lineno, sec, cur, kind, line)
kinds = {}
for f in sorted(glob.glob(R+"장v2/장*.md")) + sorted(glob.glob(R+"장v2/부록D_*.md")):
    fn = f.split("/")[-1]
    if fn == "장11.md": continue
    lines = open(f, encoding="utf-8").read().split("\n")
    sec = None; cur = None
    for i, l in enumerate(lines, 1):
        ms = re.match(r"^###\s+(\d+\.\d+)\b", l) or re.match(r"^###\s+D\.\{\{(D:[^}]+)\}\}", l)
        if ms: sec = ms.group(1); cur = None
        if re.match(r"^##\s+\d+\.\s", l): cur = None
        m = HEAD.match(l)
        if m: cur = m.group(2); kinds[cur] = m.group(1)
        mp = PROOF.match(l)
        if mp: cur = mp.group(1) + "(증명)"
        locs.append((fn, i, sec, cur, l))
terms = [
 (136, r"Konheim"), (137, r"Foata|Pollak"), (138, r"Celano"), (139, r"Aguilar|Theorem 3\.7"), (140, r"지수 공식|Corollary 5\.1\.6"),
 (141, r"Cayley 공식|Proposition 5\.3\.2|Cayley의 공식"), (142, r"Lagrange|Theorem 5\.4\.2"), (143, r"Knuth|갈고리"), (144, r"Flajolet|Sedgewick|§II\.5"),
 (145, r"Robbins"), (146, r"Petersson"), (147, r"Janson"), (148, r"Ibragimov"), (149, r"Euler.Maclaurin|Graham|Patashnik|§9\.5"),
 (150, r"Cauchy|Ahlfors"), (151, r"FKG|Fortuin"), (152, r"Jensen"), (153, r"Wallis"), (154, r"Corless|Lambert"),
 (155, r"Tanner"), (156, r"Grimmett|Theorem 2\.4"), (157, r"Harris"), (158, r"Fa[àa] di Bruno|Comtet"), (159, r"Apostol|Euler 합"), (160, r"Titchmarsh"),
]
ch11 = open(R+"장v2/장11.md", encoding="utf-8").read().split("\n")
def labset(s):
    out = []
    for m in re.finditer(r"(정의|정리|명제|보조정리|따름정리)\s+\{\{(\d+:[^}]+)\}\}((?:·\{\{\d+:[^}]+\}\})*)(의 증명)?", s):
        out.append((m.group(1), m.group(2), bool(m.group(4))))
        for x in re.findall(r"\{\{(\d+:[^}]+)\}\}", m.group(3)): out.append((m.group(1), x, bool(m.group(4))))
    return out
for ln, pat in terms:
    line = ch11[ln-1]
    cells = [c.strip() for c in line.strip().strip("|").split(" | ")]
    assert len(cells) == 3, (ln, line[:60])
    rx = re.compile(pat)
    hits = {}
    for fn, i, sec, cur, l in locs:
        if rx.search(l): hits.setdefault((fn, sec, cur), []).append(i)
    # 열의 항목
    claimed_labels = labset(cells[2])
    claimed_secs = re.findall(r"(?<![\d.])(\d+\.\d+)절", cells[2])
    claimed_D = re.findall(r"부록 D\.\{\{(D:[^}]+)\}\}", cells[2])
    print(f"\n### 행{ln} {cells[0][:40]} | 결과: {cells[1][:60]}")
    print("   본문 언급 자리:")
    for (fn, sec, cur), ls in sorted(hits.items(), key=lambda x: (x[0][0], x[1][0])):
        print(f"     {fn} §{sec} {cur or '(산문)'} 행{ls[:8]}")
    hit_labels = set((cur or "").replace("(증명)", "") for (fn, sec, cur) in hits if cur)
    hit_secs = set(sec for (fn, sec, cur) in hits if sec and not str(sec).startswith("D:"))
    hit_prose_secs = set(sec for (fn, sec, cur) in hits if sec and not cur and not str(sec).startswith("D:"))
    hit_D = set(sec for (fn, sec, cur) in hits if sec and str(sec).startswith("D:"))
    for k, lab, pf in claimed_labels:
        st = "OK" if lab in hit_labels else "<<< 그 진술 블록에 언급 없음"
        if lab in kinds and kinds[lab] != k: st += f" <<< 종류 {k} vs {kinds[lab]}"
        if lab not in kinds: st = "<<< 라벨 없음"
        print(f"   열 라벨 {k} {lab}{'(증명)' if pf else ''}: {st}")
    for s in claimed_secs:
        st = "OK(산문)" if s in hit_prose_secs else ("OK(진술 안에서만)" if s in hit_secs else "<<< 그 절에 언급 없음")
        print(f"   열 절 {s}: {st}")
    for d in claimed_D:
        print(f"   열 D {d}: {'OK' if d in hit_D else '<<< 그 항목에 언급 없음'}")
    missing_labels = sorted(hit_labels - set(l for k, l, p in claimed_labels))
    missing_prose = sorted(hit_prose_secs - set(claimed_secs))
    missing_D = sorted(hit_D - set(claimed_D))
    if missing_labels or missing_prose or missing_D:
        print(f"   열에 없는 본문 자리: 라벨 {missing_labels} 산문 절 {missing_prose} D {missing_D}")
