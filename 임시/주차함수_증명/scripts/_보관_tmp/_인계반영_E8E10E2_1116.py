# -*- coding: utf-8 -*-
"""보충 수리 E8·E10·E2의 인계를 세션이 반영한다(장부 400행, 부록D_장8 5행, 부록D_장10 8·18·38행, ZV1 D문장 스크립트 124행). 2026-11-16."""
import io, os
ROOT = r"C:\math\임시\주차함수_증명"


def sub(rel, pairs):
    p = os.path.join(ROOT, rel)
    s = io.open(p, encoding="utf-8").read()
    for a, b in pairs:
        n = s.count(a)
        if n != 1:
            raise SystemExit(f"{rel}: {n}건 — {a[:80]}")
        s = s.replace(a, b)
    io.open(p, "w", encoding="utf-8", newline="\n").write(s)
    print("ok", rel, len(pairs))


sub(r"장부_v2.md", [
    (r"그 특정값 $70.3708$, $69.3708$, $6600^{-1/3}$",
     r"그 특정값 $0.2\cdot6600^{2/3}$($>70.3708$), $\mathfrak q_{\min}-1$, $6600^{-1/3}$"),
])
sub(r"장v2\부록D_장8.md", [
    (r"\max|\Omega'|=0.585", r"\max|\Omega'|\le0.5851"),
])
sub(r"장v2\부록D_장10.md", [
    (r"에서 $0.1324$, $0.1223$, $0.1140$, $0.1133$이며",
     r"에서 각각 $0.13237$, $0.12234$, $0.11404$, $0.11329$보다 작으며"),
    (r"확인하는 진술의 $0.1324$, $0.1223$, $0.1140$, $0.1133$은 이 구간을 넷째 자리로 반올림한 값이다",
     r"확인하는 진술의 네 상계 $0.13237$, $0.12234$, $0.11404$, $0.11329$는 이 구간의 위 끝을 다섯째 자리에서 올린 값이다"),
    (r"($\bar{\mathfrak a}=0.1880$, $\bar{\mathfrak b}=1.1190$, $\mathrm{DDL}^\natural=0.1324$, $\bar{\mathfrak d}=0.8844$, $\bar{\mathfrak e}=1.0870$은 각 구간을 넷째 자리로 반올림한 값)",
     r"($\bar{\mathfrak a}<0.18798$, $\bar{\mathfrak b}<1.11896$, $\mathrm{DDL}^\natural<0.13237$, $\bar{\mathfrak d}<0.88439$, $\bar{\mathfrak e}<1.08696$은 각 구간의 위 끝을 다섯째 자리에서 올린 상계)"),
])
sub(r"scripts\수학검사2\검토_외부피드백_1116_ZV1_D문장.py", [
    ("print('각 상자·셀의 인증 여유는 양수이고 최소 여유는 $%s$($\\\\hat x\\\\in[9.8,10]$)이다.' % m6)",
     "_v = float(str(m6).replace('$', ''))\nprint('장5A 844행은 「최소 여유도 $0.0018$보다 크다」로 적혀 있어 손대지 않는다(E2, 2026-11-16). 확인: 최솟값 %s > 0.0018 -> %s' % (m6, _v > 0.0018))\nassert _v > 0.0018, '재인증 최솟값이 0.0018 이하 — 장5A 844행을 다시 본다'"),
])
