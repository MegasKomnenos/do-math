# -*- coding: utf-8 -*-
"""수학 검사 2(태그 5A) 수정 스크립트. 멱등. 앵커가 파일 안에서 정확히 한 번 나타날 때만 치환한다.

python -I scripts/수학검사2/5A_fix.py
"""
import io, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
T_CH = os.path.join(ROOT, '장v2', '장5A.md')
T_AP = os.path.join(ROOT, '장v2', '부록D_장5A.md')

EDITS = [
    # [1] 장5A 5.3절 정리 {{5:old-5-11}} 증명. 27.14^2 = 736.5796 < 736.6 이므로 「n>27.14^3 → n^{2/3}>736.6」은 따르지 않는다.
    #     736.5로 내리면 따르고, 뒤의 r_0(n)>=552(0.75·736.5=552.4), 3/4-1/736.5>149/200은 그대로 선다.
    (T_CH, r"$n\ge20001>27.14^3$이므로 $n^{2/3}>736.6$이고", r"$n\ge20001>27.14^3$이므로 $n^{2/3}>736.5$이고"),
    # [2] 장5A 명제 {{5:witness-position-bound}} 증명. mode_offset.json: 50<=n<=900의 최솟값 0.889980 < 0.89.
    #     「안에 든다」 진술이므로 아래 끝은 내림(0.88).
    (T_CH, r"$50\le n\le900$에서 $[0.89,1.99]$, $901\le n\le20000$에서 $[0.85,1.88]$", r"$50\le n\le900$에서 $[0.88,1.99]$, $901\le n\le20000$에서 $[0.85,1.88]$"),
    # [3] 부록 D.exact-n20000 결과 (ㅂ). 같은 자료(최솟값 0.889980): 0.890 → 0.889.
    (T_AP, r"차는 $50\le n\le900$에서 $[0.890,1.987]$", r"차는 $50\le n\le900$에서 $[0.889,1.987]$"),
    # [4] 부록 D.c50 결과. c50_post.json 20001–50000 최솟값 0.843854 < 0.844; c20_post.json 50–900 최솟값 0.889980 < 0.890.
    (T_AP, r"$[0.844,1.849]$, $50\le n\le900$에서 $[0.890,1.987]$", r"$[0.843,1.849]$, $50\le n\le900$에서 $[0.889,1.987]$"),
    # [5][6] 부록 D.tail-T1-partAB 식 (B). 기록 코드의 kappa_q는 본문 보조정리 {{5:lemma-L}}의 𝔐^*_q(최댓값)와 같은 양.
    #     본문 글자로 통일한다(κ는 6장 κ_N의 글자).
    (T_AP, r"$\kappa_2,\dots,\kappa_5$", r"$\mathfrak M^\ast_2,\dots,\mathfrak M^\ast_5$"),
    (T_AP, r"$\kappa_q$는 유일한 임계점", r"$\mathfrak M^\ast_q$는 유일한 임계점"),
    # [7] 부록 D.critical-window-rig 알고리즘 (d). 코드 변수 kappa_rho(s), hatS(s)=ku^2 S_k/Bor(k)는 본문에 정의가 없다.
    #     v=ku s 치환을 본문 글자(보조정리 {{5:hat-normalization}}의 Wr_j, Bor^tail_k, Bor(k))로 적는다(검산 3에서 수치 일치).
    (T_AP,
     r"$\hat{\mathrm{Wr}}_j=2^{-j}\int s^{2+2j}(1-\mathrm{ku} s)^{-1}e^{-\kappa_\rho(s)}\hat S(s)ds$($v=\mathrm{ku} s$)",
     r"$\hat{\mathrm{Wr}}_j=2^{-j}\mathrm{ku}^2\int_0^{1/\mathrm{ku}}s^{2+2j}\,\mathrm{Bor}^{\mathrm{tail}}_k(1-\mathrm{ku} s)\,e^{s^2/(2\mathrm{ku})}\,ds/\mathrm{Bor}(k)$($v=\mathrm{ku} s$)"),
    # [8] 부록 D.exact-n20000 결과 (ㄴ). compare_runs.json의 독립 프로그램 최대 상대 폭 1.127e-11 > 1e-11; 기록 §: 「peer의 폭은 ≤1.13×10^{-11}」.
    (T_AP, r"구간의 상대 폭은 $10^{-11}$ 이하다", r"구간의 상대 폭은 $1.13\times10^{-11}$ 이하다"),
    # [9] 부록 D.bernstein-signs 독립 재계산 (ㄱ). k1k2_check_output.json의 K1 = 0.00049993 < 0.0005. 「이상」 진술이므로 내림.
    (T_AP, r"(최소 정규화 여유 $0.0005$ 이상)", r"(최소 정규화 여유 $0.00049$ 이상)"),
]

def main():
    files = {}
    for path, _, _ in EDITS:
        if path not in files:
            files[path] = io.open(path, encoding='utf-8').read()
    changed = {p: False for p in files}
    for i, (path, old, new) in enumerate(EDITS, 1):
        s = files[path]
        c_old, c_new = s.count(old), s.count(new)
        if c_old == 0 and c_new == 1:
            print('[%d] 이미 적용됨' % i); continue
        if c_old != 1:
            print('[%d] 앵커 수 %d (적용 안 함): %s' % (i, c_old, old[:60])); continue
        files[path] = s.replace(old, new); changed[path] = True
        print('[%d] 치환 완료: %s' % (i, os.path.basename(path)))
    for path, s in files.items():
        if changed[path]:
            io.open(path, 'w', encoding='utf-8', newline='').write(s)

if __name__ == '__main__':
    main()
