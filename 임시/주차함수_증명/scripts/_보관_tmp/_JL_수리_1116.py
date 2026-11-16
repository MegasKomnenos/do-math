# -*- coding: utf-8 -*-
# 14차 수리 JL — 장부·부록 A·부록 C의 자리별 손 수정(Edit 도구가 CRLF를 LF로 바꾸는 문제를 피해
# 바이트 그대로 읽고, 고유한 앵커 문자열 하나를 정확히 한 번 바꾼 뒤 줄끝(세 파일 모두 LF — 파이썬 실측)을 그대로 둔다).
# 각 항목은 (파일, 옛 문자열, 새 문자열). 옛 문자열이 정확히 한 번 나타나지 않으면 아무것도 쓰지 않고 멈춘다.
import sys, io
ROOT = r"C:\math\임시\주차함수_증명"
L = ROOT + r"\장부_v2.md"
A = ROOT + r"\장v2\부록A.md"
C = ROOT + r"\장v2\부록C.md"

E = []  # (path, old, new)

# ---------- 장부_v2.md ----------
# 0절 R1′ — 부록 D의 국소 글자 되부름(H4 5절 1)
E.append((L,
 r"""국소 기호도 1.3절에 자리와 함께 등록한다.""",
 r"""국소 기호도 1.3절에 자리와 함께 등록한다. 부록 D 항목과 11.2절 표가 그 항목이 확인하는 증명의 국소 글자를 그대로 되부르는 것은 절 밖 호출로 세지 않는다(1.3 머리말; 2026-11-15 4차 J14 4절 2·사용자 결정 — 2026-11-16 14차 H4 5절 1·JL이 여기에도 적음)."""))
# 0절 R6 — 부록 A 뜻 열의 괄호(H11 4절 1)
E.append((L,
 r"""불변식 v2가 센다.""",
 r"""불변식 v2가 본문의 문장을 센다. 1.2와 부록 A의 뜻 열이 다른 장의 국소 글자와 바탕 글자가 겹침을 괄호로 알리는 것(「…와 다른 양」 꼴)은 R1′가 허용한 겹침의 안내이지 이 규칙이 세는 구별 문장이 아니다(2026-11-16 12차 S10 5절·BL, 14차 H11 4절 1·JL)."""))
# 1.1 n — 서술 범위(H11-3)
E.append((L,
 r"""; 7–10장에서는 둘째 층 행 $n=2k+\nu$ | 전 장 |""",
 r"""; 둘째 층의 행은 $n=2k+\nu$로 적는다(1.5) | 전 장 |"""))
# 1.1 i, j — 정의 절(H11-2)
E.append((L,
 r"""첫 판 1.5(3.4)의 층 번호 $r$을 $j$로 |""",
 r"""1.1에서 정의(차 $i$·자리 $i$의 지표 — 2026-11-16 14차 H11-2·JL). 첫 판 1.5(3.4)의 층 번호 $r$을 $j$로 |"""))
# 1.2 H_k — 쓰이는 장에 9(H14-3)
E.append((L,
 r"""오독으로 확인·YL) | 2.5 | 2, 5, 6, 7, 8 |""",
 r"""오독으로 확인·YL; 9장은 9.1절 보조정리 `{{9:chain-moments}}`의 증명이 $H_t(F)$를 쓴다 — 2026-11-16 14차 H14-3·JL) | 2.5 | 2, 5, 6, 7, 8, 9 |"""))
# 1.2 Φ — 2.7 국소와의 겹침 안내(H11 5절 4·J1)
E.append((L,
 r"""(7장도 씀 — 7B 집필 회수) | 4.3 | 4, 5, 7 | $\Phi$, $\Phi_{aux}$""",
 r"""(7장도 씀 — 7B 집필 회수; 2.7절 보조정리 `{{2:J-egf}}` 증명의 국소 두 변수 무게 $\Phi_\sigma(y,z)$와 다른 양 — 1.3 2.7 묶음; 2026-11-16 14차 H11 5절 4·J1·JL) | 4.3 | 4, 5, 7 | $\Phi$, $\Phi_{aux}$"""))
# 1.3 375 — source-rep 증명의 ℱ_y·mt_y 등록, 𝒱_* 등록(J3 인계 2·6)
E.append((L,
 r"""$\phi^{[k]}_m$(Green 연결 (가)·원천 표현의 양), $\mathcal R_y$, $\mathcal Q_{<k}$, $\mathcal H$(정리 `{{5:source-rep}}` 증명의 양);""",
 r"""$\phi^{[k]}_m$(Green 연결 (가)·원천 표현의 양), $\mathcal V_\ast$(보조정리 `{{5:green-connection}}` (나) 증명의 적분 표현 $e^Te^{y\mathrm{Gr}}\int_0^xe^{-y\mathrm{Gr}}\Theta$ — 같은 절의 타일 합 $\mathcal V_d$와 바탕 글자가 같으나 첨자·정의로 갈리는 증명 안의 글자; 2026-11-16 14차 J3 인계 6·JL 등록), $\mathcal F_y(x)$, $\mathrm{mt}_y(x)$(정리 `{{5:source-rep}}` 증명 (가)의 얼린 다항식 지수 생성함수 $\sum_n\mathcal K_{n,k}(y)x^n/n!$과 무게 $\prod_{t_v>k}y/t_v$를 준 뿌리 라벨 나무의 지수 생성함수, $\mathcal F_y=\exp\mathrm{mt}_y$; 옛 $\mathcal T_y$는 같은 소절 green-connection (나)의 진술 글자 $\mathcal T(x)$와 겹쳐 2026-11-16 14차 J3가 로마체로 바꿈 — 둘 다 그때까지 1.3에 등록된 적 없음), $\mathcal R_y$, $\mathcal Q_{<k}$, $\mathcal H$(같은 증명의 양);"""))
# 1.3 375 — response-kernel 증명의 mt_{𝔵′}, 𝒴 등록(J3 인계 1·6)
E.append((L,
 r"""$\mathcal J_{\mathfrak x'}(x)$, $\mathcal T_{\mathfrak x'}(x)$(보조정리 `{{5:response-kernel}}` 증명 (가)의 표시 생성함수와 그 로그 — 같은 절 green-connection (나)의 진술 글자 $\mathcal T(x)$와 바탕 글자가 같은 증명 안의 첨자 글자; 세 표시 생성함수 $\mathcal J_n(\mathfrak x,\mathfrak x',\mathfrak w)$는 보조정리 marked-riccati와 함께 2026-11-16 13차 C3로 뺌), $\mathfrak x'$(표시 변수;""",
 r"""$\mathcal J_{\mathfrak x'}(x)$, $\mathrm{mt}_{\mathfrak x'}(x)$(보조정리 `{{5:response-kernel}}` 증명 (가)의 표시 생성함수와 그 로그 — 무게와 표시 $\mathfrak x'$를 준 뿌리 라벨 나무의 지수 생성함수, $\mathcal J_{\mathfrak x'}=\exp\mathrm{mt}_{\mathfrak x'}$, 표시가 없을 때($\mathfrak x'=1$)는 $\mathrm{mt}_1$; 13차 CL 등록 때의 $\mathcal T_{\mathfrak x'}$는 같은 절 green-connection (나)의 진술 글자 $\mathcal T(x)$와 바탕 글자가 같아 2026-11-16 14차 J3가 로마체로 바꿈 — 5.2.1 source-rep 증명의 $\mathrm{mt}_y$와 같은 이름; 세 표시 생성함수 $\mathcal J_n(\mathfrak x,\mathfrak x',\mathfrak w)$는 보조정리 marked-riccati와 함께 2026-11-16 13차 C3로 뺌), $\mathcal Y=\mathcal H_t/A_{k-1}$(같은 증명 (가)가 응답 핵의 선형 방정식을 풀 때 두는 비 — 5.2.3 진술의 $\mathcal Y_j(z)$와 바탕 글자가 같으나 첨자·정의로 갈리는 증명 안의 글자; 2026-11-16 14차 J3 인계 6·JL 등록), $\mathfrak x'$(표시 변수;"""))
# 1.3 377 — ξ의 현행 꼴(H14 2.3-4)
E.append((L,
 r"""$\xi=\varsigma e^{1-\varsigma}$(기록 [ra4c01fc] L58의 생성변수; 1.2 $\xi$는 5장에서 쓰이지 않음)""",
 r"""$\xi=\mathrm{pt}'e^{1-\mathrm{pt}'}$(기록 [ra4c01fc] L58의 생성변수 $\xi=se^{1-s}$; 1차 $\varsigma e^{1-\varsigma}$ — 단위원 점의 글자가 $\mathrm{pt}'$로 바뀐 뒤의 현행 꼴로 2026-11-16 14차 H14 2.3-4·JL이 맞춤; 1.2 $\xi$는 5장에서 쓰이지 않음)"""))
# 1.3 383 — IPF(H14 2.3-4)
E.append((L,
 r"""$\mathrm{IPF}_n(\ell)$(문헌 이름); """,
 r""""""))
E.append((L,
 r"""(1차 배정 가운데 집필자가 쓰지 않은 글자 — 기록 대응은 넷째 열: $z_0$(기록 $x_0=(2k+3)/(2ek)$), $B(k)$)""",
 r"""(1차 배정 가운데 집필자가 쓰지 않은 글자 — 기록 대응은 넷째 열: $z_0$(기록 $x_0=(2k+3)/(2ek)$), $B(k)$, $\mathrm{IPF}_n(\ell)$(문헌 이름 — 장6에 없음, 2026-11-16 14차 H14 2.3-4·JL))"""))
# 1.3 384 — P_2(y), ω^st(H14 2.3-4)
E.append((L,
 r"""$P_2(y)$; """,
 r""""""))
E.append((L,
 r"""$\omega^{\mathrm{st}}_y(a)=y/(y+a)$(기록 $\omega_c(a)$; 사슬 생존 곱의 한 인자 — 10.2의 꺾인 무게 $\omega_y(d)$와 다른 양); """,
 r""""""))
E.append((L,
 r"""(1차 배정 가운데 집필자가 쓰지 않은 글자: $\Psi(z)$, $\mathfrak q_g$)""",
 r"""(1차 배정 가운데 집필자가 쓰지 않은 글자 — 기록 대응은 넷째 열: $\Psi(z)$, $\mathfrak q_g$, $P_2(y)$(기록 $P_2(c)$), $\omega^{\mathrm{st}}_y(a)=y/(y+a)$(기록 $\omega_c(a)$; 사슬 생존 곱의 한 인자) — 뒤의 둘은 장6에 없음, 2026-11-16 14차 H14 2.3-4·JL)"""))
# 1.3 386 — β′_g, 𝔷_L, P_{d,j}, T_j, poly_d, ε_d(H14 2.3-4)
E.append((L,
 r"""$\beta^\prime_g$, """,
 r""""""))
E.append((L,
 r"""$\mathfrak L^\sharp_j(\cdot)$, $\mathfrak z_L(\cdot)$(기록 $s_J(p)$), """,
 r"""$\mathfrak L^\sharp_j(\cdot)$, """))
E.append((L,
 r"""$\mathfrak B$(6.4 국소 상수; 기록 $D$), $P_{d,j}(t)$, $T_j(t)$, $\mathrm{poly}_d$, $\epsilon_d$(기록 $\Delta_d$); (4.1) 재배열의 양 |""",
 r"""$\mathfrak B$(6.4 국소 상수; 기록 $D$); (4.1) 재배열의 양; (1차 배정 가운데 집필자가 쓰지 않은 글자 — 기록 대응은 넷째 열: $\beta^\prime_g$, $\mathfrak z_L(\cdot)$(기록 $s_J(p)$), $P_{d,j}(t)$, $T_j(t)$, $\mathrm{poly}_d$, $\epsilon_d$(기록 $\Delta_d$) — 장6에 없음, 2026-11-16 14차 H14 2.3-4·JL) |"""))
# 1.3 387 — i′·t_{i′}(H14 2.3-4; i′는 보조정리 lemma-O 증명 824행에 있음)
E.append((L,
 r"""$i'$, $t_{i'}$(Borel–Tanner 합의 지표와 나무 크기; 1차 $l$, $m_l$ — 예약 글자·1.1 변수), """,
 r"""$i'$(보조정리 `{{6:lemma-O}}` 증명의 걸음 지표 $i'\le i$ — Borel–Tanner 합의 지표; 1차 $l$ — 예약 글자), """))
E.append((L,
 r"""(1차 배정 가운데 집필자가 쓰지 않은 글자 — 기록 대응은 넷째 열: $K^0(d)$,""",
 r"""(1차 배정 가운데 집필자가 쓰지 않은 글자 — 기록 대응은 넷째 열: $t_{i'}$(Borel–Tanner 합의 나무 크기; 1차 $m_l$ — 장6에 없음, 2026-11-16 14차 H14 2.3-4·JL), $K^0(d)$,"""))
# 1.3 390 — 𝔶_r, 𝒰(σ)(H14 2.3-4)
E.append((L,
 r"""$\mathfrak y_r$(기록·첫 판 $Y_r$ — 1.1 $Y$ 회피); """,
 r""""""))
E.append((L,
 r"""$\mathrm{wg}^\sharp(\mathfrak y')$(위 경로 무게; 1차 $\Psi^\sharp$ — 가중치 $\Psi$와 한 장 두 뜻이 되지 않게 로마체), $\mathcal U(\sigma)$, $\mathcal U_k(\sigma)$(용량 가중), """,
 r"""$\mathrm{wg}^\sharp(\mathfrak y')$(위 경로 무게; 1차 $\Psi^\sharp$ — 가중치 $\Psi$와 한 장 두 뜻이 되지 않게 로마체), """))
E.append((L,
 r"""2026-11-15 SM 1·T6) | 대칭 변위 가중 법칙의""",
 r"""2026-11-15 SM 1·T6); (1차 배정 가운데 집필자가 쓰지 않은 글자 — 기록 대응은 넷째 열: $\mathfrak y_r$(기록·첫 판 $Y_r$), $\mathcal U(\sigma)$, $\mathcal U_k(\sigma)$(용량 가중; 기록·첫 판 $W(\sigma)$, $W_k(\sigma)$) — 장7A에 없음, 2026-11-16 14차 H14 2.3-4·JL) | 대칭 변위 가중 법칙의"""))
# 1.3 392 — 「씨앗 전파」→「유한 전파」(H6 5절 2·JD 인계 1)
E.append((L,
 r"""| 열 인증·씨앗 전파·소인 분해의 양(7A 집필자의 최종 글자):""",
 r"""| 열 인증·유한 전파·소인 분해의 양(7A 집필자의 최종 글자):"""))
E.append((L,
 r"""씨앗 전파(유한 전파 정리와 설정; $k\le120$, $n\ge16$):""",
 r"""유한 전파(유한 전파 정리와 설정; $k\le120$, $n\ge16$; 「씨앗」은 기록 [r9e782f5]의 이름 `finite-seed-transfer`에서 온 낱말이라 부록 D 항목 제목과 함께 2026-11-16 14차 H6 5절 2·JD·JL로 걷음):"""))
# 1.3 393 — 𝔛_B→𝔛_𝔍, 𝖺_1을 7.4 묶음으로(H14 2.3-4·J7 인계 5)
E.append((L,
 r"""$\mathfrak X,\mathfrak X_i,\mathfrak X_B$(창 시작점과 문턱; 기록 $L$, $L_i$ — 전역 $L$ 회피; 1차 $\mathfrak U$는 4장 $\mathfrak U$와 겹쳐 바꿈, 세션 결정 56)""",
 r"""$\mathfrak X,\mathfrak X_i,\mathfrak X_{\mathfrak I}$(임의의 정수 문턱, 창 시작점, 마지막 창의 시작점; 기록 $L$, $L_i$ — 전역 $L$ 회피; 1차 $\mathfrak U$는 4장 $\mathfrak U$와 겹쳐 바꿈, 세션 결정 56; 2차 $\mathfrak X_B$는 창의 수 글자 $B\to\mathfrak I$를 따라 2026-11-16 14차 H14 2.3-4·JL이 맞춤)"""))
E.append((L,
 r""", $\mathsf a_1$(1.2; 기록 $C_A$), """,
 r""", """))
E.append((L,
 r""", $\mathfrak m^\sharp$(7.2와 같은 양), $\mathfrak P^{\mathrm M}_k=""",
 r""", $\mathfrak m^\sharp$(7.2와 같은 양), $\mathsf a_0,\mathsf a_1$(1.2; 기록 [rb7effe0] $C_A$; 명제 `{{7:analytic-transfer}}` 증명 (C3)이 씀 — 7A에는 없어 7.3 묶음에서 옮김, 2026-11-16 14차 H14 2.3-4·J7 인계 5·JL), $\mathfrak P^{\mathrm M}_k="""))
# 1.3 394 — 𝔱(H14 2.3-4)
E.append((L,
 r"""$\mathfrak t$(Taylor 매개변수; 양쪽 구간으로 적음), """,
 r""""""))
E.append((L,
 r"""(1차 배정 가운데 집필자가 쓰지 않은 글자 — 기록 대응은 넷째 열; $\mathfrak a^\circ_{k-1}$""",
 r"""(1차 배정 가운데 집필자가 쓰지 않은 글자 — 기록 대응은 넷째 열; $\mathfrak t$(Taylor 매개변수; 양쪽 구간으로 적음)는 장7B에 없어 2026-11-16 14차 H14 2.3-4·JL로 이 목록에 옮김; $\mathfrak a^\circ_{k-1}$"""))
# 1.3 399 — 「창 나무 크기」(H8 5절 1)
E.append((L,
 r"""창 나무 크기 $k+\mathfrak q$·$k+1$·""",
 r"""원천 생존을 재는 숲 크기 $k+\mathfrak q$·그 생존의 용량 $k+1$·"""))
# 1.3 400 — A^{(k-1)}_N(H14 2.3-4)
E.append((L,
 r"""| $A^{(k-1)}_N$(1.2의 $A^{(t)}_N$; 모든 뿌리 나무가 $<k$인 숲의 수), $\mathcal M(N)$,""",
 r"""| $\mathcal M(N)$,"""))
E.append((L,
 r"""$\mathcal N_\ell(t)$(기록의 $\tau_\ell(s)$) | 용량 이동 비·""",
 r"""$\mathcal N_\ell(t)$(기록의 $\tau_\ell(s)$); (1차 배정 가운데 집필자가 쓰지 않은 글자 — 기록 대응은 넷째 열: $A^{(k-1)}_N$(1.2 $A^{(t)}_N$의 꼴로 적던 「모든 뿌리 나무가 $<k$인 숲의 수」; 기록 $A^0_N$) — 장8에 없음, 2026-11-16 14차 H14 2.3-4·JL) | 용량 이동 비·"""))
# 1.3 402 — 𝔠_5→𝔠_2(J9 인계 1), 𝒪^♯·Ū(H14 2.3-4)
E.append((L,
 r"""$\mathfrak c_5$(감소 항의 최댓값; 기록 $c_5$; 1차 $\mathfrak c^\sharp_5$)""",
 r"""$\mathfrak c_2$(감소 항의 최댓값; 기록 $c_5$ — 기록의 번호를 글의 번호로 바꿈, 2026-11-16 14차 H9 4절 1·J9; 1차 $\mathfrak c^\sharp_5$)"""))
E.append((L,
 r"""$\mathcal O^\sharp$(기록 $\mathcal C$), $\bar U$, """,
 r""""""))
E.append((L,
 r"""($S_k=m_1(k)+1$은 1차 배정 — 본문에 없고 $m_1(k)$만 씀; 세션 결정 56)""",
 r"""($S_k=m_1(k)+1$은 1차 배정 — 본문에 없고 $m_1(k)$만 씀; 세션 결정 56; $\mathcal O^\sharp$(기록 $\mathcal C$)·$\bar U$도 1차 배정으로 장9에 없음 — 2026-11-16 14차 H14 2.3-4·JL)"""))
# 1.3 411 — Yc 등재(JD 인계 2)
E.append((L,
 r""",\kappa_L,\mathrm{Xc},\mathrm{xh},""",
 r""",\kappa_L,\mathrm{Xc},\mathrm{Yc},\mathrm{xh},"""))
E.append((L,
 r"""(D.{{D:xcert-partAB}} 「식」이 밝힌다)""",
 r"""(D.{{D:xcert-partAB}} 「식」이 밝힌다), $\mathrm{Yc}$(D.{{D:xcert-partAB}} (6)(b)의 [C-U] 상수 부분 $1-\mathfrak S^{(0)}-(2\pi)^{-1/2}e^{-1}e^{\eta_{257}}(2\cdot256^{-1/2}+256^{-3/2})=0.367806$; 기록 `Y0`; (6)(a)의 $\mathrm{Xc}$와 짝 — 2026-11-16 14차 H13 7A-1·JD·JL)"""))
# 2절 (Q24) — 반올림값 서술(H14-2)
E.append((L,
 r"""| (Q24) 상수 $(2\pi)^{-1/2}$ | 수 $(2\pi)^{-1/2}$를 그대로 적는다; """,
 r"""| (Q24) 상수 $(2\pi)^{-1/2}$ | 산문에서는 수 $(2\pi)^{-1/2}$를 그대로 적는다; 부등식의 한쪽을 유리수로 바꿀 때는 반올림 방향을 밝힌 값($0.39893\le(2\pi)^{-1/2}\le0.398943$ 등)을 쓴다 — 4.3·6.1·6.5·7.6·9.5절과 부록 D의 식; 보조정리 `{{9:psi-low}}`의 $\Psi^{\mathrm{lb}}(d)=0.3989(2\sqrt d-1.678)$는 그 상수 $0.3989$가 정의다(1.2 행; 2026-11-16 14차 H14-2·JL); """))
E.append((L,
 r""", $0.3989$(반올림값은 부록 D의 식에만); 기록 $C_2$""",
 r"""; 기록 $C_2$"""))
# 2절 (Q35) — 「문턱 손실」(H14-1)
E.append((L,
 r"""$\Theta_n=\binom nkk^{k-2}A_{n-k,k-1}$ 「문턱 나무 손실」 | $\binom nkv_kA_{n-k,k-1}$,""",
 r"""$\Theta_n=\binom nkk^{k-2}A_{n-k,k-1}$ 「문턱 나무 손실」($\Theta_n$ 하나의 이름; 수식어 없는 「문턱 손실」은 $\Theta_n$의 이름으로는 쓰지 않고 가족의 통칭으로만 쓴다 — 9.2절 제목 「문턱 손실을 둘로 가르기」, 짝 없는 문턱 손실 $\Theta^\circ_n$(Q50), 정리 `{{7:old-6-16}}`의 이름 「문턱 손실의 망원 상환」; 2026-11-16 14차 H14-1·JL) | $\binom nkv_kA_{n-k,k-1}$,"""))
E.append((L,
 r""", 「유일한 순수 손실」, 「문턱 손실」(7.6의 문턱 뿌리 음 항과 겹침) | 2.10 |""",
 r""", 「유일한 순수 손실」 | 2.10 |"""))
# 3절 손실, 이득(H14-1)
E.append((L,
 r"""| 손실, 이득 | 음의 몫(문턱 나무 손실, 대각선 손실, 창의 손실); 양의 몫""",
 r"""| 손실, 이득 | 음의 몫(문턱 나무 손실, 짝 없는 문턱 손실, 대각선 손실, 창의 손실 — 수식어 없는 「문턱 손실」은 이 가족의 통칭이지 $\Theta_n$의 이름이 아니다, Q35); 양의 몫"""))
# 3절 결손(H10 5절·J1 인계 1)
E.append((L,
 r"""$d$($n+1-M$, $m-M$; 결손 좌표; 1.5절이 두 셈법 모두에 같은 글자 $d$를 쓴다고 밝힌다) | 1.5 |""",
 r"""$d$($n+1-M$, $m-M$; 생존 확률 $s_m(y)$에서는 용량 아래의 가장 높은 수준 $y-1$을 최대 변위의 자리에 둔 $m+1-y$ — 6.3절의 결손 좌표 $\mathfrak s_d(y)=s_{y+d-1}(y)$와 10장이 이렇게 센다; 1.5절이 두 셈법 모두에 같은 글자 $d$를 쓴다고 밝힌다 — 2026-11-16 14차 H10 5절·J1·JL) | 1.5 |"""))
# 3절 안쪽 패턴·내부 순서 등재(H6 5절 3·J6)
E.append((L,
 r"""| 7.2 | 블록(셋째 뜻), 조각 |""",
 "| 7.2 | 블록(셋째 뜻), 조각 |\r\n"
 r"""| 안쪽 패턴 | 조각의 마지막 자리를 뺀 자리들의 상대 순서 — 크기 하나 작은 결과 순열로 본다(정리 `{{7:old-6-6}}`·`{{7:old-6-10}}` 증명이 쓰는 낱말; 2026-11-16 14차 H6 5절 3·J6·JL 등재) | 7.2 | —(첫 판·기록에 낱말 없음; 7A 집필자의 낱말) |""" + "\n"
 r"""| 내부 순서 | 변위 부분순서 $\preceq$를 아래 닫힌 집합 $\mathcal H$와 그 여집합에 제한한 두 부분순서의 선형 확장(정리 `{{7:old-6-6}}` 증명의 한 문단이 정의하고 그 안에서만 쓴다; 2026-11-16 14차 H6 5절 3·J6·JL 등재) | 7.2 | —(첫 판·기록에 낱말 없음; 7A 집필자의 낱말) |"""))
# 3절 영어 병기 — 갱신함수·임계 볼츠만 법칙·h-변환(H11-4; 8절 규칙 7·8과 맞춤)
E.append((L,
 r"""| 갱신 | Borel 갱신 집합, 갱신함수, 갱신 방문 핵, 갱신 항등식 | 2.9 |""",
 r"""| 갱신 | Borel 갱신 집합, 갱신함수(영어 병기 renewal function — 2.9에서 한 번), 갱신 방문 핵, 갱신 항등식 | 2.9 |"""))
E.append((L,
 r"""| 임계 볼츠만 법칙, Borel 분포, Borel–Tanner 분포, 이웃비 | 2.5–2.6의 법칙들과 $\mathrm{Bor}(s+1)/\mathrm{Bor}(s)$ | 2.5, 2.6 |""",
 r"""| 임계 볼츠만 법칙, Borel 분포, Borel–Tanner 분포, 이웃비 | 2.5–2.6의 법칙들(임계 볼츠만 법칙은 영어 병기 critical Boltzmann law — 2.6에서 한 번; Borel–Tanner는 이름 그대로)과 $\mathrm{Bor}(s+1)/\mathrm{Bor}(s)$ | 2.5, 2.6 |"""))
E.append((L,
 r"""(Doob의 h-변환; h-변환 함수""",
 r"""(Doob의 h-변환 — 영어 병기 h-transform, 10.5에서 한 번; h-변환 함수"""))
# 5절 7장 낱말 열(새 3절 행 둘)
E.append((L,
 r"""전달 범위; 토막; 조각; 소인 구간;""",
 r"""전달 범위; 토막; 조각; 안쪽 패턴; 내부 순서; 소인 구간;"""))
# 5절 9장 여유 라틴 대문자에서 H 제거(H14-3)
E.append((L,
 r"""라틴 대문자: $B$, $C$, $E$, $H$, $J$, $R$, $U$, $V$.""",
 r"""라틴 대문자: $B$, $C$, $E$, $J$, $R$, $U$, $V$."""))
# 8절 규칙 1 — 전방 안내 예외(H14 4절 1·H11 5절 2; J2·J7의 본문 결정)
E.append((L,
 r"""1.2의 기호 28개가 여기에 든다 — 2026-11-16 12차 S14-4), 그 밖의 장 머리 개관이 정의 절보다 앞에서 글자를 쓰면 위반으로 센다.""",
 r"""1.2의 기호 28개가 여기에 든다 — 2026-11-16 12차 S14-4), 1.4절이 먼저 부른 명제 이름을 그 뜻을 말로 밝히고 진술의 라벨을 단 전방 안내에서 되부르는 것(3장 머리의 $\mathsf P_X\Rightarrow\mathsf P_L$ — 정리 `{{4:old-4-8}}`; 7.8절의 $\mathsf B^+$·$\mathsf{FLQ}$ — 따름정리 `{{9:old-7-44}}`·정리 `{{10:old-8-37}}`)도 같은 예외다(2026-11-16 14차 H14 4절 1·H11 5절 2; J2·J7이 본문을 두기로 정해 JL이 규칙 쪽을 맞춤); 그 밖의 장 머리 개관이 정의 절보다 앞에서 글자를 쓰면 위반으로 센다."""))

# ---------- 부록A.md ----------
E.append((A,
 r"""| $n$ | 행의 크기(주차함수의 「길이」 $n$, 숲의 「크기」 $n$; 낱말은 대상마다 그렇게 쓴다); 7–10장에서는 둘째 층 행 $n=2k+\nu$ | 1.5 | — |""",
 r"""| $n$ | 행의 크기(주차함수의 「길이」 $n$, 숲의 「크기」 $n$; 낱말은 대상마다 그렇게 쓴다); 둘째 층의 행은 $n=2k+\nu$로 적는다(1.5) | 1.1 | — |"""))
E.append((A,
 r"""| $\ell=k-1$ | 수준(최대 변위의 값) | 1.5 | — |""",
 r"""| $\ell=k-1$ | 수준(최대 변위의 값) | 1.3 | — |"""))
E.append((A,
 r"""| $y$ | 용량 변수(움직일 때) | 1.5 | — |""",
 r"""| $y$ | 용량 변수(움직일 때) | 2.6 | — |"""))
E.append((A,
 r"""따름정리 `{{5:old-5-34}}`의 증명에서는 $Y\in\{y-1,y\}$) | 1.5 | — |""",
 r"""따름정리 `{{5:old-5-34}}`의 증명에서는 $Y\in\{y-1,y\}$) | 2.6 | — |"""))
E.append((A,
 r"""| $i$, $j$ | 자리·차·항의 지표; 층 번호(1.5의 「$j$째 층」)도 $j$ | 1.5 | — |""",
 r"""| $i$, $j$ | 자리·차·항의 지표; 층 번호(1.5의 「$j$째 층」)도 $j$ | 1.1 | — |"""))
E.append((A,
 r"""| $\Phi, \Phi^{\mathrm{aux}}$ | 중앙 틈의 생성함수($e_n/n!=[x^n]\Phi(T(x))$)와 위 끝을 $1$로 바꾼 것 | 4.3 | — |""",
 r"""| $\Phi, \Phi^{\mathrm{aux}}$ | 중앙 틈의 생성함수($e_n/n!=[x^n]\Phi(T(x))$)와 위 끝을 $1$로 바꾼 것(2.7의 국소 두 변수 무게 $\Phi_\sigma(y,z)$와 다른 양) | 4.3 | — |"""))

# ---------- 부록C.md ----------
E.append((C,
 r"""| 기록 [r475ada3]의 정리 C·C′·C″, 기록 [r6b37c7e]의 정리 4.A의 감사 부분 | 명제 {{7:analytic-transfer}} | 중앙 틈 사슬의 $\nu$-이전 |""",
 r"""| 기록 [r475ada3]의 정리 C·C′·C″, 기록 [r6b37c7e]의 정리 4.A의 감사 부분 | 명제 {{7:analytic-transfer}} | 중앙 틈 연쇄의 $\nu$-이전 |"""))
E.append((C,
 r"""| 조각 | 블록(셋째 뜻), 조각 | 7.2 |""",
 "| 조각 | 블록(셋째 뜻), 조각 | 7.2 |\r\n"
 r"""| 안쪽 패턴 | —(첫 판·기록에 낱말 없음; 7A 집필자의 낱말) | 7.2 |""" + "\n"
 r"""| 내부 순서 | —(첫 판·기록에 낱말 없음; 7A 집필자의 낱말) | 7.2 |"""))

ENGLISH_TABLE = "\n".join([
 "### 영어를 함께 적은 낱말",
 "",
 "본문이 처음 정의하는 자리에서 영어를 한 번 함께 적은 낱말과 그 자리.",
 "",
 "| 이 글의 용어 | 영어 | 병기한 절 |",
 "|---|---|---|",
 "| 주차함수 | parking function | 1.1 |",
 "| 선형 탐사 | linear probing | 1.1 |",
 "| 지수 공식 | exponential formula | 2.4 |",
 "| Borel–Tanner 질량, Borel–Tanner 분포 | Borel–Tanner(이름을 그대로 쓴다) | 2.5 |",
 "| 임계 볼츠만 법칙 | critical Boltzmann law | 2.6 |",
 "| Borel 갱신함수 | renewal function | 2.9 |",
 "| 확률보행 | random walk | 2.11 |",
 "| 로그오목 | log-concave | 3.2 |",
 "| FKG 부등식 | Fortuin–Kasteleyn–Ginibre inequality | 5.2 |",
 "| h-변환 | h-transform | 10.5 |",
 ""])

def main():
    data = {}
    for p in (L, A, C):
        with open(p, "rb") as f:
            b = f.read()
        s = b.decode("utf-8")
        assert "\n" in s and "\n" not in s.replace("\n", ""), p
        data[p] = s
    # 검사: 모두 정확히 한 번
    bad = []
    for i, (p, old, new) in enumerate(E):
        c = data[p].count(old)
        if c != 1:
            bad.append((i, p, c, old[:60]))
    if bad:
        for x in bad:
            print("ANCHOR NOT UNIQUE:", x)
        sys.exit(1)
    for p, old, new in E:
        data[p] = data[p].replace(old, new, 1)
    # 부록 C 끝에 넷째 표
    s = data[C]
    if not s.endswith("\n"):
        s += "\n"
    if not s.endswith("\r\n\r\n"):
        s += "\n"
    s += ENGLISH_TABLE
    data[C] = s
    for p, s in data.items():
        assert "\n" not in s.replace("\n", ""), p
        with open(p, "wb") as f:
            f.write(s.encode("utf-8"))
        print("written", p, "lines", s.count("\n"))

if __name__ == "__main__":
    main()
