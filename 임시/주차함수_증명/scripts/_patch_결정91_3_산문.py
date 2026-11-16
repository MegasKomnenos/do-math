# -*- coding: utf-8 -*-
"""사용자 결정 91 (3): 블록 삭제 뒤 남는 문장의 수정(장 머리·절 도입·9.6·11.3·11.4·부록 D 항목 일부·장부·구조표). 멱등.

_patch_결정91_3_삭제.py 다음에 돌린다. 편집은 (exact) 정확 문자열 치환과 (span) 두 앵커 사이 구간 치환이다.
각 편집은 원문에 정확히 한 번 있어야 하고, 없으면 새 문자열이 이미 있는지 확인해 「이미 적용」으로 적는다.
"""
import io
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)

EDITS = [
    # ---- 장7A: 장 머리 「경로」, 7.1의 LM 정의, 7.3 도입 ----
    ("exact", "장v2/장7A.md",
     r"두 증명이 함께 받는다. 정리 {{7:S-infinity}}·{{7:moment-band}}와 따름정리 {{7:moment-window}}의 모멘트 결과는 주 정리에 쓰이지 않는 강화다.",
     r"두 증명이 함께 받는다."),
    ("exact", "장v2/장7A.md",
     r"이 충분조건을 한 범위에서 묻는 명제에 이름을 둔다. 정수 $k\ge2$에 대해",
     r"7.2절의 증가 경계에 쓸 두 양을 미리 둔다. 정수 $k\ge2$에 대해"),
    ("span", "장v2/장7A.md",
     r"$1\le\mathsf t_k\le k$다. 명제 $\mathsf{LM}$은 모든 $k\ge501$과",
     r"$b_{n,k-1}\le b_{n,k}$다. 왼쪽 절반의 환원은",
     r"$1\le\mathsf t_k\le k$다. 왼쪽 절반의 환원은"),
    ("exact", "장v2/장7A.md",
     r"곧 $n$이 $k^2$이나 $k^{5/3}$ 규모 이상인 자리를 닫는다.",
     r"곧 $n$이 $k^2$ 규모 이상인 자리를 닫는다."),
    # ---- 장7B: 7.4 도입, 오차 귀납 뒤 문단 ----
    ("exact", "장v2/장7B.md",
     r"이 띠에서 한 칸 차분 $d_{n,k}$의 부호는 두 길로 정해진다. 하나는 4.3절의 중앙 틈 증명을 $\nu$를 매개변수로 두고 그대로 옮기는 길이고, 다른 하나는 7.1절의 모멘트 판정을 결과 순열의 재귀로 직접 계산해 인증하는 길이다.",
     r"이 띠에서 한 칸 차분 $d_{n,k}$의 부호는 4.3절의 중앙 틈 증명을 $\nu$를 매개변수로 두고 그대로 옮기는 길로 정해진다. 그에 앞서 7.1절의 모멘트 판정을 결과 순열의 재귀로 직접 계산해 인증하는 길을 세우며, 이 길은 열 $501\le k\le2000$에서 왼쪽 잔여 증가를 닫는 데 쓰인다(따름정리 {{7:qstar-implies-wlflat}})."),
    ("exact", "장v2/장7B.md",
     r"같은 부록이 이 보조정리의 판정식 (7.5)를 열 $501\le k\le2000$의 모멘트 창 밖 위치 전부와 $4981\le k\le11099$의 일부 위치에서 확인한 결과를 담는다.",
     r"같은 부록이 이 보조정리의 판정식 (7.5)를 열 $501\le k\le840$의 $2k+1\le n\le\lfloor13k^2/100\rfloor$와 열 $841\le k\le2000$의 $10001\le n\le n_{\mathrm M}(k)-1$($n_{\mathrm M}(k)$는 정리 {{7:theorem-C-moment}}(나)의 문턱)에서 확인한 결과를 담는다."),
    # ---- 장9: 9.6 따름정리 old-7-44 ----
    ("exact", "장v2/장9.md",
     r"[증명됨, 정리 {{9:old-7-16}}·{{9:old-7-35}}·{{9:old-7-43}}에 의존; rae1f209, r5909c9e].**",
     r"[증명됨, 정리 {{9:old-7-16}}·{{9:old-7-35}}에 의존; rae1f209, r5909c9e].**"),
    ("exact", "장v2/장9.md",
     r"$\mathrm{BV}_n+\mathrm{PAIR}_n\ge\Theta_n$이다. 더 정확히 $\mathrm{BV}_n+\mathrm{PAIR}_n\ge\Theta_n+1.27\binom nkk^{k-2}A^\diamond_{n-k}$다.",
     r"$\mathrm{BV}_n+\mathrm{PAIR}_n\ge\Theta_n$이다."),
    ("exact", "장v2/장9.md",
     r"따름정리 {{9:old-7-17}}이 $\mathsf B^+$를 준다. 정량 여유는 정리 {{9:old-7-16}}의 $\mathrm{BV}_n\ge\Theta_n-\binom nkk^{k-2}A^\diamond_{n-k}$에 정리 {{9:old-7-43}}의 $\mathrm{PAIR}_n\ge2.27\binom nkk^{k-2}A^\diamond_{n-k}$를 더한 것이다. ∎",
     r"따름정리 {{9:old-7-17}}이 $\mathsf B^+$를 준다. ∎"),
    # ---- 장2: 장 머리 「경로」 ----
    ("exact", "장v2/장2.md",
     r"명제 {{2:old-2-41}}·{{2:old-2-42}}는 첫째 증명(9장)만,",
     r"명제 {{2:old-2-41}}은 첫째 증명(9장)만,"),
    # ---- 장11: 11.3 세 표, 11.4 Robbins 행 ----
    ("exact", "장v2/장11.md",
     r"정리 {{9:old-7-35}}·{{9:old-7-43}}, 보조정리 {{9:old-7-37}}(정리 {{8:old-6-28}})",
     r"정리 {{9:old-7-35}}, 보조정리 {{9:old-7-37}}(정리 {{8:old-6-28}})"),
    ("exact", "장v2/장11.md",
     r"보조정리 {{9:old-7-12}}·정리 {{9:old-7-43}}(정리 {{2:old-2-13}})",
     r"보조정리 {{9:old-7-12}}(정리 {{2:old-2-13}})"),
    ("exact", "장v2/장11.md",
     r"| 쌍 부등식: 정리 {{9:old-7-35}}, 정리 {{9:old-7-43}}, 보조정리 {{9:pair-one-variable}} | 보조정리 {{9:pair-one-variable}}, 정리 {{9:old-7-43}}: 방향 반올림 구간 | 따름정리 {{9:old-7-44}}(두 정리), 정리 {{9:old-7-35}}·{{9:old-7-43}}(보조정리 {{9:pair-one-variable}}) |",
     r"| 쌍 부등식: 정리 {{9:old-7-35}}, 보조정리 {{9:pair-one-variable}} | 보조정리 {{9:pair-one-variable}}: 방향 반올림 구간 | 따름정리 {{9:old-7-44}}(정리 {{9:old-7-35}}), 정리 {{9:old-7-35}}(보조정리 {{9:pair-one-variable}}) |"),
    ("exact", "장v2/장11.md",
     r"명제 {{2:old-2-41}}·{{2:old-2-42}}, 정리 {{6:old-7-21}}",
     r"명제 {{2:old-2-41}}, 정리 {{6:old-7-21}}"),
    ("exact", "장v2/장11.md",
     r"정리 {{9:old-7-43}}(명제 {{2:old-2-42}}; 그 증명이 명제 {{2:old-2-41}}을 부른다), ",
     r"명제 {{9:old-7-6}}·정리 {{9:old-7-35}}의 증명(명제 {{2:old-2-41}}), "),
    ("exact", "장v2/장11.md",
     r", 7.2절, 정리 {{7:S-infinity}}, 7.4절,",
     r", 7.2절, 7.4절,"),
    ("exact", "장v2/장11.md",
     r", 보조정리 {{9:old-7-40}}, 정리 {{9:old-7-43}}, 명제 {{10:old-8-23}}",
     r", 보조정리 {{9:old-7-40}}, 명제 {{10:old-8-23}}"),
    # ---- 부록 D.28 self-consistent-constants ----
    ("exact", "장v2/부록D_장7A.md",
     r"### D.{{D:self-consistent-constants}} 자기일관 상계의 상수: 세 층과 $k=6098$ 한 점 (정리 {{7:self-consistent-S}}, 따름정리 {{7:cor-S-prime}}, 정리 {{7:S-infinity}})",
     r"### D.{{D:self-consistent-constants}} 자기일관 상계의 상수: 세 층 (정리 {{7:self-consistent-S}}, 따름정리 {{7:cor-S-prime}})"),
    ("span", "장v2/부록D_장7A.md",
     r" (3) 정리 {{7:S-infinity}}(마)의 $k=6098$ 값.",
     r"$\sum_{j=1}^{100}j^{-3/2}\le2.41288$.",
     r""),
    ("span", "장v2/부록D_장7A.md",
     r" 정리 {{7:S-infinity}}의 양은 $\epsilon_k=1.04k^{-2/3}$",
     r"(4)는 구간 합의 위끝을 $2.41288$과 비교하는 것이다.",
     r""),
    ("span", "장v2/부록D_장7A.md",
     r" (3) $k=6098$에서 정리 {{7:S-infinity}}의 모든 양을 구간 산술로 평가하고",
     r"(`원고_자료/세션_재계산/zeta_constants/sum100_iv.py`).",
     r""),
    ("span", "장v2/부록D_장7A.md",
     r"**범위.** 세 층의 매개변수 셋; $k=6098$ 한 점; 합 하나.",
     r"$\mathfrak B^\infty(k)=0.05006$).",
     r"**범위.** 세 층의 매개변수 셋."),
    ("exact", "장v2/부록D_장7A.md",
     r"방향 반올림 구간($e^{-i}$, $k=6098$의 평가, (4)).",
     r"방향 반올림 구간($e^{-i}$)."),
    ("span", "장v2/부록D_장7A.md",
     r"세 값 모두 양수, $k=6098$에서 두 식 모두 성립,",
     r"따라서 $\le2.41288$.",
     r"세 값 모두 양수."),
    ("exact", "장v2/부록D_장7A.md",
     r"범위 부분((1)의 $\mathfrak A$·$\mathfrak B$와 (4)); 산술 정확 정수·유리수·방향 반올림 구간; 자료 기록·이 글〕",
     r"범위 부분((1)의 $\mathfrak A$·$\mathfrak B$); 산술 정확 정수·유리수·방향 반올림 구간; 자료 기록〕"),
    ("exact", "장v2/부록D_장7A.md",
     r" (4)는 이 글을 쓰며 더한 확인이고, 그 구간 계산과 출력이 자료에 있다.",
     r""),
    ("exact", "장v2/부록D_장7A.md",
     r", `records/rad00a59b22bd42a5a16cc0aa67e8841a/evidence/peer/asym_check.py`, `records/rad00a59b22bd42a5a16cc0aa67e8841a/evidence/peer/asym_check.txt`, `records/rad00a59b22bd42a5a16cc0aa67e8841a/evidence/peer/asym_bound.py`",
     r""),
    ("exact", "장v2/부록D_장7A.md",
     r"; (4)의 확인 코드와 출력은 이 글의 자료 묶음에 있다, `원고_자료/세션_재계산/zeta_constants/sum100_iv.py`, `원고_자료/세션_재계산/zeta_constants/sum100_iv_out.txt`",
     r""),
    ("exact", "장v2/부록D_장7A.md",
     r"**출처.** [rad00a59] `exposition.md` §5.5, §5.6, §5.9.",
     r"**출처.** [rad00a59] `exposition.md` §5.5, §5.6."),
    # ---- 부록 D.31 band102-integer 제목 ----
    ("exact", "장v2/부록D_장7B.md",
     r", 보조정리 {{7:hermite-nu}}, 정리 {{7:moment-band}})",
     r", 보조정리 {{7:hermite-nu}})"),
    # ---- 부록 D.32 moment-certification ----
    ("exact", "장v2/부록D_장7B.md",
     r"### D.{{D:moment-certification}} 모멘트 판정의 계산: 재귀의 구간 인증 (A1)–(A5), 열별 문턱 $n_{\mathrm M}(k)$의 정확 유리수 재계산, 중앙 띠 모멘트판의 감사 (정리 {{7:theorem-C-moment}}·{{7:moment-band}}, 따름정리 {{7:moment-window}}·{{7:qstar-implies-wlflat}})",
     r"### D.{{D:moment-certification}} 모멘트 판정의 계산: 재귀의 구간 인증 (A3)·(A5), 열별 문턱 $n_{\mathrm M}(k)$의 정확 유리수 재계산 (정리 {{7:theorem-C-moment}}, 따름정리 {{7:qstar-implies-wlflat}})"),
    ("exact", "장v2/부록D_장7B.md",
     r"(A1) $4981\le k\le9999$, $\max(2k+1,10001)\le n\le2k+40$; (A2) $10000\le k\le11099$, $2k+20\le n\le2k+40$; (A3) $501\le k\le840$",
     r"(A3) $501\le k\le840$"),
    ("span", "장v2/부록D_장7B.md",
     r" (ㄷ) 정리 {{7:moment-band}}의 넷째 단계:",
     r"$20\le\nu\le40$에서 통과한다.",
     r""),
    ("span", "장v2/부록D_장7B.md",
     r" (ㄷ) 명제 {{7:analytic-transfer}}의 식에서 $\mathcal I_k$를",
     r"호 상계에 $2$를 곱한 것.",
     r""),
    ("exact", "장v2/부록D_장7B.md",
     r" (ㄷ) 명제 {{7:analytic-transfer}}의 감사 코드에 위의 변경만 넣어 같은 $(K_1,\nu)$에서 실행한다.",
     r""),
    ("exact", "장v2/부록D_장7B.md",
     r"**범위.** (A1) $5019$열, (A2) $1100$열, (A3) $340$열, (A5) $1160$열. (ㄴ) $841\le k\le2000$의 $1160$열. (ㄷ) $K_1=10000$의 $\nu\le19$, $K_1=11100$의 $20\le\nu\le40$.",
     r"**범위.** (A3) $340$열, (A5) $1160$열. (ㄴ) $841\le k\le2000$의 $1160$열."),
    ("exact", "장v2/부록D_장7B.md",
     r"기록의 계산은 binary64 사전 오차 해석이다. (ㄴ)(ㄷ) 정확 정수·유리수.",
     r"기록의 계산은 binary64 사전 오차 해석이다. (ㄴ) 정확 정수·유리수."),
    ("exact", "장v2/부록D_장7B.md",
     r"이 글의 구간 계산: 네 범위의 $60{,}703{,}015$개 위치($7619$열; (A1) $200{,}380$, (A2) $23{,}100$, (A3) $19{,}840{,}702$, (A5) $40{,}638{,}833$개) 모두에서",
     r"이 글의 구간 계산: 두 범위의 $60{,}479{,}535$개 위치($1500$열; (A3) $19{,}840{,}702$, (A5) $40{,}638{,}833$개) 모두에서"),
    ("exact", "장v2/부록D_장7B.md",
     r"범위별 최솟값: (A1) $22.18973$($(5000,10001)$), $0.05749$($(9999,20007)$); (A2) $26.29231$($(10000,20020)$), $0.05541$($(11099,22218)$); (A3) $13.33603$",
     r"범위별 최솟값: (A3) $13.33603$"),
    ("exact", "장v2/부록D_장7B.md",
     r"기록의 여덟 열에서 양 끝을 모두 계산한 $\mathbb E^\sigma_{n,k}[\mathcal T_k]$의 구간 폭은 상대 $8.1\times10^{-8}$ 이하(가장 넓은 곳 $(11099,22218)$에서 $[26.93363518,\,26.93363734]$)로 가장 작은 상대 여유 $0.0554$보다 다섯 자리 이상 작다.",
     r"양 끝을 모두 계산한 열에서 $\mathbb E^\sigma_{n,k}[\mathcal T_k]$의 구간 폭은 상대 $8.1\times10^{-8}$ 이하로 가장 작은 상대 여유 $0.1379$보다 여섯 자리 이상 작다."),
    ("exact", "장v2/부록D_장7B.md",
     r"최대 $\mathfrak e^{(3)}$: (A1) $22.190$($(5000,10001)$), $0.0575$($(9999,20007)$), $3.9\times10^{-5}$; (A2) $26.292$($(10000,20020)$), $0.0554$($(11099,22218)$), $4.8\times10^{-5}$; (A3) $13.336$",
     r"최대 $\mathfrak e^{(3)}$: (A3) $13.336$"),
    ("exact", "장v2/부록D_장7B.md",
     r" (ㄷ) 두 감사 모두 통과하며, 호 항이 $10^{-19}$ 이하라 여유가 부록 D.{{D:band102-integer}}(ㄹ)의 $K_1=10000$·$11100$ 값과 소수 다섯째 자리까지 같다.",
     r""),
    ("exact", "장v2/부록D_장7B.md",
     r"범위 부분((ㄱ)은 전체, (ㄴ)은 1160열 전부, (ㄷ)은 없음)",
     r"범위 부분((ㄱ)은 전체, (ㄴ)은 1160열 전부)"),
    ("exact", "장v2/부록D_장7B.md",
     r"합산 순서가 다른 numpy 구현으로 일곱 열($k=5000,9999,11099,8000,4981,2000,840$)의 최솟값과 끝값이 인쇄된 자리까지 일치.",
     r"합산 순서가 다른 numpy 구현으로 두 열($k=2000,840$)의 최솟값과 끝값이 인쇄된 자리까지 일치."),
    ("exact", "장v2/부록D_장7B.md",
     r"또 소스를 같은 컴파일러로 다시 빌드해 여덟 열의 요약 행을 바이트 단위로 재현했고,",
     r"또 소스를 같은 컴파일러로 다시 빌드해 세 열($k=2000,840,1000$)의 요약 행을 바이트 단위로 재현했고,"),
    ("exact", "장v2/부록D_장7B.md",
     r"이 글을 쓰며 (ㄱ)의 네 범위 전부를 본문의 식에서 새로 쓴 끝점 구간 코드로",
     r"이 글을 쓰며 (ㄱ)의 두 범위 전부를 본문의 식에서 새로 쓴 끝점 구간 코드로"),
    ("exact", "장v2/부록D_장7B.md",
     r"같은 코드로 기록의 여덟 열($k=5000,9999,11099,8000,4981,2000,840,1000$)을 양 끝 모두 계산하면",
     r"같은 코드로 기록의 세 열($k=2000,840,1000$)을 양 끝 모두 계산하면"),
    ("exact", "장v2/부록D_장7B.md",
     r" (ㄷ)의 계산은 검토가 실행한 감사 자체다.",
     r""),
    ("exact", "장v2/부록D_장7B.md",
     r"`records/r10ff8c2…/evidence/producer/cert/`(band_A/B: (A1)+(A2); full_*: (A3); win_0..3: (A5))",
     r"`records/r10ff8c2…/evidence/producer/cert/`(full_*: (A3); win_0..3: (A5))"),
    ("exact", "장v2/부록D_장7B.md",
     r"; `records/r475ada3…/evidence/peer/repro/audit_lm.py`, `records/r475ada3…/evidence/peer/repro/audit_lm_K10000_nu1_19.txt`, `records/r475ada3…/evidence/peer/repro/audit_lm_K11100_nu20_40.txt`, `records/r475ada3…/evidence/peer/exact/peer_lm_exact.py`, `records/r475ada3…/evidence/peer/exact/peer_lm_numeric.py`",
     r""),
    ("exact", "장v2/부록D_장7B.md",
     r"**출처.** [r10ff8c2] §3.1–3.4, `evidence/producer/notes_errors.md`; [r475ada3] §6.3.",
     r"**출처.** [r10ff8c2] §3.1–3.4, `evidence/producer/notes_errors.md`."),
    # ---- 부록 D.33 column-certificates-841-2000 제목 ----
    ("exact", "장v2/부록D_장7B.md",
     r"(정리 {{7:theorem-C-moment}}(나); 따름정리 {{7:moment-window}}·{{7:qstar-implies-wlflat}}의 열 $841\le k\le2000$ 부분)",
     r"(정리 {{7:theorem-C-moment}}(나); 따름정리 {{7:qstar-implies-wlflat}}의 열 $841\le k\le2000$ 부분)"),
    # ---- 부록 D.43 pair-one-variable ----
    ("exact", "장v2/부록D_장9.md",
     r"쌍 부등식의 한 변수 확인 (보조정리 {{9:pair-one-variable}}·정리 {{9:old-7-43}})",
     r"쌍 부등식의 한 변수 확인 (보조정리 {{9:pair-one-variable}})"),
    ("exact", "장v2/부록D_장9.md",
     r"$\mathfrak F(6668,\vartheta)\ge1.149$이고, $\mathfrak F(6668,\vartheta)+\mathfrak G(6668,\vartheta)\ge2.27$이다.",
     r"$\mathfrak F(6668,\vartheta)\ge1.149$이다."),
    ("exact", "장v2/부록D_장9.md",
     r", 그리고 정리 {{9:old-7-43}}의 $\mathfrak G(k,\vartheta)$와 $\mathfrak S^{\prime\pm}(k)$. 윤곽 함수",
     r". 윤곽 함수"),
    ("exact", "장v2/부록D_장9.md",
     r" $\mathfrak F+\mathfrak G$도 같은 단조 괄호($k/(N+1)$과 $k/N$은 $\vartheta$에 감소)로 구간 하계를 구한다.",
     r""),
    ("exact", "장v2/부록D_장9.md",
     r"$\mathfrak S^{+,\mathrm{low}}/k=0.5416178$, $\mathfrak S^{\prime-}/k=0.5754977$, $\mathfrak S^{\prime+}/k=0.5754555$.",
     r"$\mathfrak S^{+,\mathrm{low}}/k=0.5416178$."),
    ("exact", "장v2/부록D_장9.md",
     r" $\mathfrak F+\mathfrak G$의 구간 하계 최솟값은 $\vartheta\in[0.5674,0.5675]$의 구간에서 $2.274021$로 $2.27$보다 $0.0040$ 크다($520$개 구간 $2.270518$, $52000$개 구간 $2.274371$).",
     r""),
    ("exact", "장v2/부록D_장9.md",
     r"$5200$개 구간의 두 최솟값이 기록의 배정밀도 값 $1.14936$, $2.2740$과 맞는다.",
     r"$5200$개 구간의 최솟값이 기록의 배정밀도 값 $1.14936$과 맞는다."),
    ("exact", "장v2/부록D_장9.md",
     r" `giant_bound.py`, `giant_bound.out`(정리 {{9:old-7-43}});",
     r""),
    ("exact", "장v2/부록D_장9.md",
     r"§3.3 조립(122–141행), §3.4 정리 P◇′(172행 부근), §7 증거 파일(367–371행).",
     r"§3.3 조립(122–141행), §7 증거 파일(367–371행)."),
    # ---- 장부_v2.md: 1.3 국소 기호 행 셋, 2절·3절·5절·7절 ----
    ("exact", "장부_v2.md",
     r"| 수준 사슬·자기일관 상계 정리 S·따름정리 S′·정리 S∞·보조정리 R의 양(7A 집필자의 최종 글자):",
     r"| 수준 사슬·자기일관 상계 정리 S·따름정리 S′·보조정리 R의 양(7A 집필자의 최종 글자):"),
    ("exact", "장부_v2.md",
     r", $\mathfrak A^\infty,\mathfrak B^\infty$(기록 $\alpha^\infty,\beta^\infty$), $\mathcal E$((S1)의 합)",
     r", $\mathcal E$((S1)의 합)"),
    ("exact", "장부_v2.md",
     r", $\mathfrak D$(기록 [rad00a59] L309 $D$; 1차 $\mathfrak d^{\mathrm S}$ — $\mathfrak d$는 씨앗 전파의 미분 횟수); 정리 S′:",
     r"; 정리 S′:"),
    ("span", "장부_v2.md",
     r"; 정리 S∞: $\epsilon_k$(기록 $\delta_k$)",
     r"$\omega,\omega'$(임시 변수; 기록 $a,c$·$x,y$); 계승 모멘트 하계",
     r"; 계승 모멘트 하계"),
    ("exact", "장부_v2.md",
     r"; $n^\natural_k$, $\mathsf{LM}^{\flat\flat}$(1.2; 7.2 끝); (1차 배정 가운데",
     r"; (1차 배정 가운데"),
    ("exact", "장부_v2.md",
     r"기록의 $a_m$은 $\mathfrak a_m$, $c_k$는 $\mathsf x_k$, $N_k=\gamma_kk^2$는 $n^\natural_k$, $p(y\to z)$는",
     r"기록의 $a_m$은 $\mathfrak a_m$, $c_k$는 $\mathsf x_k$, $p(y\to z)$는"),
    ("exact", "장부_v2.md",
     r"| 7.2 `{{7:self-consistent-S}}`, `{{7:cor-S-prime}}`, `{{7:S-infinity}}`, `{{7:lemma-R-sc}}`, `{{7:factorial-moment}}` |",
     r"| 7.2 `{{7:self-consistent-S}}`, `{{7:cor-S-prime}}`, `{{7:lemma-R-sc}}`, `{{7:factorial-moment}}` |"),
    ("exact", "장부_v2.md",
     r", $S$, $S^{(k)}$, $\tau_k=\delta_kT_k$, $K^\prime$, $R_1,R_2$, $E_t$, $\alpha(k),\beta(k)$, $\alpha^\infty,\beta^\infty$, $D$, $N_k$, $\mu$, $c_k$;",
     r", $S$, $S^{(k)}$, $\alpha(k),\beta(k)$, $\mu$, $c_k$;"),
    ("exact", "장부_v2.md",
     r"$W_j$, $\mathcal I'_k$(4.3 기록 글자 유지), $\mathrm C_1,\mathrm D_1$",
     r"$W_j$, $\mathrm C_1,\mathrm D_1$"),
    ("exact", "장부_v2.md",
     r"; $\mathcal R_{\mathrm L}$, $\mathcal R^{(>40)}_{\mathrm L}$(1.2); (1차 배정 가운데",
     r"; (1차 배정 가운데"),
    ("exact", "장부_v2.md",
     r"$L^{(k-1)}_n,U^{(k)}_n$, $\mathcal R_L,\mathcal R^{(>40)}_L$, $X(n)$, $LM_{n,k}$, $\mathcal I^\prime_k,R^\prime_{k,\lambda},c^\prime_J,W^\prime,A^\prime_\rho$; [r6b37c7e]",
     r"$L^{(k-1)}_n,U^{(k)}_n$, $X(n)$; [r6b37c7e]"),
    ("exact", "장부_v2.md",
     r"$L^{(k-1)}_n$, $\mathcal I^\prime_k$, $c^\prime_J$, $W^\prime$, $A^\prime_\rho$, $\mu_s$",
     r"$L^{(k-1)}_n$, $\mu_s$"),
    ("exact", "장부_v2.md",
     r"$\mathfrak S^-,\mathfrak S^+$, $\mathfrak S^{\pm,\mathrm{low}}$, $\mathfrak S^{\prime\pm}$(창 합·구획 합 하계·거대 나무 쪽 구획 합; 기록 $\Sigma_v,\Sigma_u,\Sigma^{low},\Sigma'$; 1차 $\mathfrak S_v,\mathfrak S_u$ 꼴)",
     r"$\mathfrak S^-,\mathfrak S^+$, $\mathfrak S^{\pm,\mathrm{low}}$(창 합·구획 합 하계; 기록 $\Sigma_v,\Sigma_u,\Sigma^{low}$; 1차 $\mathfrak S_v,\mathfrak S_u$ 꼴)"),
    ("exact", "장부_v2.md",
     r"$\mathfrak F(k,\vartheta)$, $\mathfrak G(k,\vartheta)$(쌍 부등식 비의 하계·거대 나무 몫 하계; 기록 (3.2) $F^{low}$, $L_2$; 1차 $\mathfrak f^{\mathrm{low}},\mathfrak g^{\mathrm{low}}$)",
     r"$\mathfrak F(k,\vartheta)$(쌍 부등식 비의 하계; 기록 (3.2) $F^{low}$; 1차 $\mathfrak f^{\mathrm{low}}$)"),
    ("exact", "장부_v2.md",
     r"| 쌍 부등식과 그 둘째 하계 증명의 국소 양들(9.5; 기록 [r5909c9e] §3);",
     r"| 쌍 부등식 증명의 국소 양들(9.5; 기록 [r5909c9e] §3);"),
    ("exact", "장부_v2.md",
     r"$I_i$는 $\mathfrak I_i$, $L_2$는 $\mathfrak g^{\mathrm{low}}$, $P^{up}_0$은",
     r"$I_i$는 $\mathfrak I_i$, $P^{up}_0$은"),
    ("exact", "장부_v2.md",
     r"| 9.5 `{{9:old-7-35}}`–`{{9:old-7-43}}` 증명 |",
     r"| 9.5 `{{9:old-7-35}}`–`{{9:pair-one-variable}}` 증명 |"),
    ("exact", "장부_v2.md",
     r"$F^{low}$, $G^{low}$, $\theta_a,\theta_b$",
     r"$F^{low}$, $\theta_a,\theta_b$"),
    ("exact", "장부_v2.md",
     r"$M_i$, $I_i$, $L_2$, $\rho_b,",
     r"$M_i$, $I_i$, $\rho_b,"),
    ("exact", "장부_v2.md",
     r"$n^\sharp_k$(반감 경계), $\tilde n_k$, $n^\flat_k$, $n^\natural_k$, $n^\circ_k$(값이 다른 다섯 경계;",
     r"$n^\sharp_k$(반감 경계), $\tilde n_k$, $n^\flat_k$, $n^\circ_k$(값이 다른 네 경계;"),
    ("exact", "장부_v2.md",
     r"| $N^\sharp_k$, $\tilde N_k$, $N^\flat_k$, $N_k$, $t_k$; 기록 $N^\#_k$, $\tilde N_k$, $q_k$([r39ba7c1]), $n_0$, $N_k$([r89eb039]);",
     r"| $N^\sharp_k$, $\tilde N_k$, $N^\flat_k$, $t_k$; 기록 $N^\#_k$, $\tilde N_k$, $q_k$([r39ba7c1]), $n_0$([r89eb039]);"),
    ("exact", "장부_v2.md",
     r"$\mathcal T_{n,k}$(7.1), $\mathcal R_{\mathrm L}$·$\mathcal R^{(>40)}_{\mathrm L}$(7.4), $\mathcal W^{(>40)}$(7.5)",
     r"$\mathcal T_{n,k}$(7.1), $\mathcal W^{(>40)}$(7.5)"),
    ("exact", "장부_v2.md",
     r"$\Sigma_{n,k}$, $LM_{n,k}$, $\mathcal R_L$, $\mathcal W$,",
     r"$\Sigma_{n,k}$, $\mathcal W$,"),
    ("exact", "장부_v2.md",
     r"| 왼쪽 창, 모멘트 창 | 한 걸음 판정을 묻는 위치 집합 $\mathcal W^{(>102)}$; 모멘트 인증의 위치 집합 $\mathcal W_M$ | 7.5, 7.4 | 같음 |",
     r"| 왼쪽 창 | 한 걸음 판정을 묻는 위치 집합 $\mathcal W^{(>102)}$ | 7.5 | 같음 |"),
    ("exact", "장부_v2.md",
     r"$n^\sharp_k$(반감 경계), $\tilde n_k$, $n^\flat_k$, $n^\natural_k$, $n^\circ_k$(극 영역 정리의 부호 경계는",
     r"$n^\sharp_k$(반감 경계), $\tilde n_k$, $n^\flat_k$, $n^\circ_k$(극 영역 정리의 부호 경계는"),
    ("exact", "장부_v2.md",
     r"$\mathcal W^{(>102)}, \mathcal W^{(>40)}$; $\mathcal W_M$; $\Pr^{\sigma}_{n,k}",
     r"$\mathcal W^{(>102)}, \mathcal W^{(>40)}$; $\Pr^{\sigma}_{n,k}"),
    ("exact", "장부_v2.md",
     r"$\mathcal T_k(\sigma), \mathcal T_{n,k}$; $\mathsf{LM}$; $\mathsf{LM}^{\flat\flat}$; $\mathrm{Conv}_{n,k}",
     r"$\mathcal T_k(\sigma), \mathcal T_{n,k}$; $\mathrm{Conv}_{n,k}"),
    ("exact", "장부_v2.md",
     r"$\tilde n_k$; $n^\natural_k$; $\mathsf t_k$;",
     r"$\tilde n_k$; $\mathsf t_k$;"),
    ("exact", "장부_v2.md",
     r"$\mathcal R_2$; $\mathcal R_{\mathrm L}, \mathcal R^{(>40)}_{\mathrm L}$; $\Pi^{\mathrm{up}}_h$",
     r"$\mathcal R_2$; $\Pi^{\mathrm{up}}_h$"),
    ("exact", "장부_v2.md",
     r"왼쪽 창, 모멘트 창; 전달 범위",
     r"왼쪽 창; 전달 범위"),
    ("exact", "장부_v2.md",
     r"| $n^\flat_k$, $n^\natural_k$, $n^\circ_k$ | [r7c26b8b], [r89eb039]; [rad00a59], [r89eb039]; [r89eb039] | $N^\flat_k=\min\{n\ge2k+1:\varphi_k(n)\ge0\}$; $N_k=\gamma_kk^2$(층별), $N_k$; $n_0=\lceil2k^{3/2}\rceil$ |",
     r"| $n^\flat_k$, $n^\circ_k$ | [r7c26b8b], [r89eb039]; [r89eb039] | $N^\flat_k=\min\{n\ge2k+1:\varphi_k(n)\ge0\}$; $n_0=\lceil2k^{3/2}\rceil$ |"),
    # ---- 구조표_v2.md ----
    ("exact", "구조표_v2.md",
     r"| 2.10 지수 공식과 다섯 몫 분해 | 2.40, 2.41, 2.42 | 첫 판 2.10 | 옮김 |",
     r"| 2.10 지수 공식과 다섯 몫 분해 | 2.40, 2.41; 2.42는 뺌(결정 91 (3): 쌍 부등식의 둘째 하계만이 쓰던 꼴) | 첫 판 2.10 | 옮김 |"),
    ("exact", "구조표_v2.md",
     r"`{{7:prime-decomposition}}`·`{{7:level-chain}}`·`{{7:lm-core}}`(7A의 내부 보조정리), 새 `{{7:self-consistent-S}}` 정리 S·`{{7:cor-S-prime}}`·`{{7:S-infinity}}`·`{{7:lemma-R-sc}}` [rad00a59] §2·§3·§5(약 150행; 상수는 부록 D; 전제 `{{2:ratio-e}}`, `{{7:factorial-moment}}`);",
     r"`{{7:prime-decomposition}}`·`{{7:level-chain}}`(7A의 내부 보조정리), 새 `{{7:self-consistent-S}}` 정리 S·`{{7:cor-S-prime}}`·`{{7:lemma-R-sc}}` [rad00a59] §2·§3·§5(약 150행; 상수는 부록 D; 전제 `{{2:ratio-e}}`, `{{7:factorial-moment}}`; 정리 S∞ `{{7:S-infinity}}`와 관계 1·2 `{{7:lm-core}}`는 뺌 — 결정 91 (3));"),
    ("exact", "구조표_v2.md",
     r"`{{7:theorem-C-moment}}` 정리 C §3.2(7행); (A1)–(A5)·정리 D는 부록 D |",
     r"`{{7:theorem-C-moment}}` 정리 C §3.2(7행); (A3)·(A5)·정리 D는 부록 D; [r475ada3]의 정리 LM `{{7:moment-band}}`과 [r10ff8c2]의 명제 3.1 `{{7:moment-window}}`, 부록 D의 (A1)(A2)·모멘트판 감사는 뺌(결정 91 (3)) |"),
    ("exact", "구조표_v2.md",
     r"| 9.5 쌍 부등식 | 7.35–7.43; 한 변수 확인은 부록 D |",
     r"| 9.5 쌍 부등식 | 7.35–7.42; 7.43은 뺌(결정 91 (3)); 한 변수 확인은 부록 D |"),
]


def main():
    texts = {}
    applied = skipped = 0
    for e in EDITS:
        kind, rel = e[0], e[1]
        path = os.path.join(ROOT, rel)
        if rel not in texts:
            texts[rel] = io.open(path, encoding="utf-8").read()
        s = texts[rel]
        if kind == "exact":
            old, new = e[2], e[3]
            n = s.count(old)
            if n == 0:
                if new and s.count(new) >= 1:
                    skipped += 1
                    continue
                if not new:
                    skipped += 1
                    print(f"[이미 적용?] {rel}: 삭제 대상 없음 '{old[:50]}…'")
                    continue
                raise SystemExit(f"[실패] {rel}: 없음 '{old[:60]}…'")
            if n > 1:
                raise SystemExit(f"[실패] {rel}: {n}번 '{old[:60]}…'")
            texts[rel] = s.replace(old, new)
            applied += 1
        else:
            start, end, new = e[2], e[3], e[4]
            n = s.count(start)
            if n == 0:
                skipped += 1
                print(f"[이미 적용?] {rel}: 구간 시작 없음 '{start[:50]}…'")
                continue
            if n > 1:
                raise SystemExit(f"[실패] {rel}: 구간 시작 {n}번 '{start[:50]}…'")
            a = s.index(start)
            b = s.find(end, a + len(start))
            if b < 0:
                raise SystemExit(f"[실패] {rel}: 구간 끝 없음 '{end[:50]}…'")
            if "\n" in s[a:b]:
                raise SystemExit(f"[실패] {rel}: 구간이 줄을 넘음 '{start[:40]}…'")
            texts[rel] = s[:a] + new + s[b + len(end):]
            applied += 1
    for rel, s in texts.items():
        io.open(os.path.join(ROOT, rel), "w", encoding="utf-8", newline="\n").write(s)
    print(f"적용 {applied}, 건너뜀 {skipped}, 파일 {len(texts)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
