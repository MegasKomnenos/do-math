# -*- coding: utf-8 -*-
"""8장 8.4 묶음의 국소 글자 갱신(결정 77 반영): q'_max 삭제, q_w·q*_w·수준 k-1의 괄호 글자 추가. 멱등."""
import io
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = os.path.join(ROOT, "장부_v2.md")
s = io.open(P, encoding="utf-8").read()
old1 = "$q'_{\\max}$(줄인 창 끝), "
new1 = "$q_{\\mathrm w}$, $q^\\ast_{\\mathrm w}$(창 합의 창 끝과 착지 범위의 창 끝; $\\nu$의 세 경우로 정함 — 세션 결정 77), "
old2 = "$\\mathcal L_{\\mathrm a},\\mathcal L_{\\mathrm c},\\mathcal L_i$(세 괄호 하계; 기록 $A$, Clo, $B_i$;"
new2 = "$\\mathcal L_{\\mathrm a},\\mathcal L_{\\mathrm c},\\mathcal L_i$, 수준 $k-1$의 $\\mathcal L'_{\\mathrm a},\\mathcal L'_{\\mathrm c},\\mathcal L'_i$, $\\mathfrak h'$(세 괄호 하계와 그 수준 $k-1$ 판; 기록 $A$, Clo, $B_i$;"
changed = False
if old1 in s:
    s = s.replace(old1, new1); changed = True
if old2 in s:
    s = s.replace(old2, new2); changed = True
if changed:
    io.open(P, "w", encoding="utf-8", newline="\n").write(s)
    print("patched")
else:
    print("unchanged (already or anchors missing)", old1 in s, old2 in s)
