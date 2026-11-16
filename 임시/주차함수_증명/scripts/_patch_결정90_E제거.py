# -*- coding: utf-8 -*-
r"""사용자 결정 90의 (가) 안: 따름정리 {{6:cor-L}}로 5장의 열 사이 보정을 완전히 제거하는 구조 편집(줄 단위).

하는 일(모두 줄 범위의 삭제·이동이고, 새 문장은 아래 상수에 적은 것뿐이다):
  장v2/장5B.md
    1. 보조정리 {{5:old-5-29}}(기저량의 하계) 머리·진술·증명 블록 삭제.
    2. 5.5.8절 전체(`#### 5.5.8` 머리부터 `#### 5.5.9` 머리 앞까지) 삭제. 그 안의 보조정리 {{5:zeta-constants}}
       머리 줄을 꺼내어 5.5.3절 보조정리 {{5:stirling-bor}} 증명 뒤로 옮기고 도입 두 문장과 확인 문장을 새로 둔다.
    3. `#### 5.5.9` → `#### 5.5.8`, `#### 5.5.10` → `#### 5.5.9`.
  장v2/부록D_장5B.md
    4. D.{{D:column-moment-constant}} 블록과 D.{{D:mass-envelope-U2}} 블록 삭제.
  장부_v2.md
    5. 글자 사전의 네 행($\mathcal E$ 묶음, $\mathfrak e_m$, $\mathsf C_E$, $\mathrm{EB}(w)$) 삭제.
본문 문장의 수정(식 우변, 의존 목록, 상수 등)은 이 스크립트가 아니라 편집 도구로 한다.
사용: python -I scripts/_patch_결정90_E제거.py [--dry]
"""
import io
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DRY = "--dry" in sys.argv


def read_lines(path):
    with io.open(path, encoding="utf-8", newline="") as fh:
        return fh.read().splitlines(keepends=True)


def write_lines(path, lines):
    with io.open(path, "w", encoding="utf-8", newline="") as fh:
        fh.write("".join(lines))


def find_unique(lines, prefix, start=0):
    hits = [i for i in range(start, len(lines)) if lines[i].startswith(prefix)]
    assert len(hits) == 1, (prefix, hits)
    return hits[0]


# ---------------------------------------------------------------- 장5B
p5b = os.path.join(ROOT, "장v2", "장5B.md")
L = read_lines(p5b)
nl = "\n" if not L[0].endswith("\r\n") else "\r\n"

# 1. 보조정리 old-5-29 블록: 머리 줄부터 그 증명 줄(∎로 끝남)과 뒤의 빈 줄까지.
i_head = find_unique(L, "**보조정리 {{5:old-5-29}} ")
i_proof = find_unique(L, "**증명.** 보조정리 {{5:old-5-27}}의 합에서", i_head)
i_end = next(k for k in range(i_proof, i_proof + 8) if L[k].rstrip("\r\n").endswith("∎"))
assert L[i_end + 1].strip() == ""
assert L[i_end + 2].startswith("이제 명제 {{5:old-5-22}}에 보조정리 {{5:old-5-29}}를 넣으면")
removed_D = L[i_head:i_end + 2]
del L[i_head:i_end + 2]

# 2. 5.5.8절 블록과 zeta 보조정리의 이동.
i_558 = find_unique(L, "#### 5.5.8 ")
i_559 = find_unique(L, "#### 5.5.9 ")
assert i_558 < i_559
block = L[i_558:i_559]
i_zeta = [k for k in range(len(block)) if block[k].startswith("**보조정리 {{5:zeta-constants}} ")]
assert len(i_zeta) == 1
zeta_head = block[i_zeta[0]]
assert block[i_zeta[0] + 2].startswith("세 구간은 부록 D.{{D:zeta-constants}}의 계산으로 확인된다.")
del L[i_558:i_559]

intro = (
    "거듭제곱 합 $\\sum_{j\\le N}j^{\\pm1/2}$의 Euler–Maclaurin 상수와 급수 $\\sum_{j\\ge1}j^{-3/2}$의 값으로 Riemann 제타 함수의 "
    "$\\tfrac12$, $-\\tfrac12$, $\\tfrac32$에서의 값이 나타나며, 이 값들을 명명 상수 $\\mathsf z_{1/2}$, $\\mathsf z_{-1/2}$, "
    "$\\mathsf z_{3/2}$로 적는다. 세 값의 인증 구간을 여기 적어 두며, 8장과 9장이 받는다." + nl
)
confirm = "세 구간은 부록 D.{{D:zeta-constants}}의 계산으로 확인된다." + nl
i_sb_proof = find_unique(L, "**증명.** (가) Stirling 공식의 Robbins 꼴")
assert L[i_sb_proof + 1].strip() == ""
assert L[i_sb_proof + 2].startswith("**보조정리 {{5:old-5-26}} ")
L[i_sb_proof + 2:i_sb_proof + 2] = [intro, nl, zeta_head, nl, confirm, nl]

# 3. 절 번호.
i_559 = find_unique(L, "#### 5.5.9 ")
L[i_559] = L[i_559].replace("#### 5.5.9 ", "#### 5.5.8 ", 1)
i_5510 = find_unique(L, "#### 5.5.10 ")
L[i_5510] = L[i_5510].replace("#### 5.5.10 ", "#### 5.5.9 ", 1)
assert not any(ln.startswith("#### 5.5.10") for ln in L)

print(f"장5B: 보조정리 D 블록 {len(removed_D)}줄 삭제, 5.5.8절 {len(block)}줄 삭제, zeta 보조정리 이동, 절 번호 갱신 → {len(L)}줄")
if not DRY:
    write_lines(p5b, L)

# ---------------------------------------------------------------- 부록D_장5B
pD = os.path.join(ROOT, "장v2", "부록D_장5B.md")
D = read_lines(pD)
a = find_unique(D, "### D.{{D:column-moment-constant}} ")
b = find_unique(D, "### D.{{D:zeta-constants}} ")
assert a < b
n17 = b - a
del D[a:b]
a = find_unique(D, "### D.{{D:mass-envelope-U2}} ")
b = find_unique(D, "### D.{{D:band-check}} ")
assert a < b
n19 = b - a
del D[a:b]
print(f"부록D_장5B: D.17 블록 {n17}줄, D.19 블록 {n19}줄 삭제 → {len(D)}줄")
if not DRY:
    write_lines(pD, D)

# ---------------------------------------------------------------- 장부_v2
pL = os.path.join(ROOT, "장부_v2.md")
G = read_lines(pL)
for prefix in ["| $\\mathcal E, \\mathcal E^+, \\mathcal E^\\ast(y)$ |", "| $\\mathfrak e_m$ |", "| $\\mathsf C_E$ |", "| $\\mathrm{EB}(w)$ |"]:
    k = find_unique(G, prefix)
    del G[k]
print(f"장부_v2: 글자 사전 4행 삭제 → {len(G)}줄")
if not DRY:
    write_lines(pL, G)
