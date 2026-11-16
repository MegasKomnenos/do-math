# -*- coding: utf-8 -*-
"""Z2 결정 D1(정리 old-4-8의 (가)(나) 분할)을 이미 끝난 작업자의 파일 두 자리에 세션이 적용한다 — Z4 인계 28행(5B 469행), Z10 인계 3절(10장 785행). 2026-11-16."""
import io, os
ROOT = r"C:\math\임시\주차함수_증명"


def sub(rel, old, new):
    p = os.path.join(ROOT, rel)
    s = io.open(p, encoding="utf-8").read()
    n = s.count(old)
    assert n == 1, (rel, old[:60], n)
    s = s.replace(old, new)
    io.open(p, "w", encoding="utf-8", newline="\n").write(s)
    print("ok", rel)


sub(r"장v2\장5B.md",
    "횡단 $\\mathsf P_X$는 정리 {{4:old-4-8}}로 $\\mathsf P_L$에서 따른다",
    "횡단 $\\mathsf P_X$는 정리 {{4:old-4-8}}(가)로 $\\mathsf P_L$에서 따른다")
sub(r"장v2\장10.md",
    "정리 {{4:old-4-8}}의 $\\mathsf P_L\\Rightarrow\\mathsf P_X$에서",
    "정리 {{4:old-4-8}}(가)의 $\\mathsf P_L\\Rightarrow\\mathsf P_X$에서")
