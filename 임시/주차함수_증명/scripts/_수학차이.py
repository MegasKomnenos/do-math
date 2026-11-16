# -*- coding: utf-8 -*-
"""기준 판(스냅샷)과 현재 판 사이의 수학 요소 차이를 전부 나열한다(첨삭 뒤 수학 검사용).
사용: python -I scripts/_수학차이.py <기준.md> <현재.md> [<출력.md>]
출력 절: (1) 수식 구간 — 사라진 것·새로 생긴 것(다중집합 차; 행 번호와 앞뒤 40자), (2) 숫자 토큰(산문) 차, (3) 라벨·식별자·식 번호 차,
(4) 진술 머리 차, (5) †·∎·절 머리 수, (6) 수식이나 숫자나 라벨이 든 행의 통합 diff(산문만 바뀐 행은 뺀다)."""
import difflib
import io
import re
import sys
from collections import Counter

MATH = re.compile(r"\$\$.*?\$\$|\$[^$\n]+\$", re.S)
LABEL = re.compile(r"\{\{[^}]+\}\}")
RID = re.compile(r"\br[0-9a-f]{7}\b")
EQNO = re.compile(r"\((?:\d+|[A-Z])\.\d+[a-z]?\)")
NUM = re.compile(r"(?<![\w.])\d+(?:\.\d+)?(?![\w.])")
HEAD = re.compile(r"^\*\*(정의|정리|명제|보조정리|따름정리|가정|관찰) \{\{[^}]+\}\}[^*]*\*\*", re.M)
SEC = re.compile(r"^#{2,4} .*$", re.M)


def spans_with_pos(s):
    out = []
    for m in MATH.finditer(s):
        line = s.count("\n", 0, m.start()) + 1
        a = max(0, m.start() - 40); b = min(len(s), m.end() + 40)
        ctx = s[a:b].replace("\n", "⏎")
        out.append((m.group(0), line, ctx))
    return out


def prose_only(s):
    return MATH.sub(" ", s)


def multiset_diff(a, b):
    ca, cb = Counter(a), Counter(b)
    gone = list((ca - cb).elements()); new = list((cb - ca).elements())
    return gone, new


def main():
    pa, pb = sys.argv[1], sys.argv[2]
    out = sys.argv[3] if len(sys.argv) > 3 else None
    A = io.open(pa, encoding="utf-8").read(); B = io.open(pb, encoding="utf-8").read()
    L = []
    w = L.append
    w(f"# 수학 차이: `{pa}` → `{pb}`\n")
    sa, sb = spans_with_pos(A), spans_with_pos(B)
    gone, new = multiset_diff([x[0] for x in sa], [x[0] for x in sb])
    w(f"## (1) 수식 구간: 기준 {len(sa)}개 → 현재 {len(sb)}개; 사라짐 {len(gone)}, 새로 생김 {len(new)}\n")
    cg, cn = Counter(gone), Counter(new)
    w("### 사라진 수식(기준 판의 자리)\n")
    seen = Counter()
    for sp, line, ctx in sa:
        if cg[sp] > seen[sp]:
            seen[sp] += 1; w(f"- 기준 {line}행: `{sp}`  ⟨{ctx}⟩")
    w("\n### 새로 생긴 수식(현재 판의 자리)\n")
    seen = Counter()
    for sp, line, ctx in sb:
        if cn[sp] > seen[sp]:
            seen[sp] += 1; w(f"- 현재 {line}행: `{sp}`  ⟨{ctx}⟩")
    na, nb = NUM.findall(prose_only(A)), NUM.findall(prose_only(B))
    g2, n2 = multiset_diff(na, nb)
    w(f"\n## (2) 산문의 숫자 토큰: 사라짐 {sorted(g2, key=float)} / 새로 생김 {sorted(n2, key=float)}\n")
    for name, rx in (("라벨", LABEL), ("기록 식별자", RID), ("식 번호", EQNO)):
        g, n = multiset_diff(rx.findall(A), rx.findall(B))
        w(f"## (3) {name}: 사라짐 {g} / 새로 생김 {n}\n")
    ha, hb = HEAD.findall(A), HEAD.findall(B)
    w(f"## (4) 진술 머리: 기준 {len(ha)} → 현재 {len(hb)}\n")
    heads_a = [m.group(0) for m in HEAD.finditer(A)]; heads_b = [m.group(0) for m in HEAD.finditer(B)]
    for tag, i1, i2, j1, j2 in difflib.SequenceMatcher(None, heads_a, heads_b, autojunk=False).get_opcodes():
        if tag == "equal":
            continue
        for h in heads_a[i1:i2]:
            w(f"- 기준에만: `{h[:160]}`")
        for h in heads_b[j1:j2]:
            w(f"- 현재에만: `{h[:160]}`")
    w(f"\n## (5) †: {A.count('†')}→{B.count('†')}, ∎: {A.count('∎')}→{B.count('∎')}, 절 머리: {len(SEC.findall(A))}→{len(SEC.findall(B))}\n")
    for h in SEC.findall(A):
        if h not in B:
            w(f"- 기준에만 있는 절 머리: `{h}`")
    for h in SEC.findall(B):
        if h not in A:
            w(f"- 현재에만 있는 절 머리: `{h}`")
    w("\n## (6) 수식·숫자·라벨이 든 행의 통합 diff(산문만 바뀐 행은 뺌)\n")
    la, lb = A.split("\n"), B.split("\n")
    keep = lambda l: ("$" in l) or LABEL.search(l) or NUM.search(prose_only(l)) or EQNO.search(l)
    w("```diff")
    for tag, i1, i2, j1, j2 in difflib.SequenceMatcher(None, la, lb, autojunk=False).get_opcodes():
        if tag == "equal":
            continue
        rows_a = [l for l in la[i1:i2] if keep(l)]; rows_b = [l for l in lb[j1:j2] if keep(l)]
        if not rows_a and not rows_b:
            continue
        # 수식 열이 같고 산문만 다른 짝은 뺀다
        if len(rows_a) == len(rows_b) and all(MATH.findall(x) == MATH.findall(y) and NUM.findall(prose_only(x)) == NUM.findall(prose_only(y)) and LABEL.findall(x) == LABEL.findall(y) for x, y in zip(rows_a, rows_b)):
            continue
        w(f"@@ 기준 {i1+1}-{i2} / 현재 {j1+1}-{j2} @@")
        for l in la[i1:i2]:
            if keep(l): w("- " + l[:600])
        for l in lb[j1:j2]:
            if keep(l): w("+ " + l[:600])
    w("```")
    text = "\n".join(L) + "\n"
    if out:
        io.open(out, "w", encoding="utf-8", newline="\n").write(text)
        print(f"{out}: 수식 {len(sa)}→{len(sb)} (−{len(gone)} +{len(new)}), 숫자 −{len(g2)} +{len(n2)}, 머리 {len(ha)}→{len(hb)}, {len(text)}자")
    else:
        print(text)


if __name__ == "__main__":
    main()
