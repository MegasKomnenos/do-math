# 수리 전체23 ZL — 묶음 5: 부록 A. 장부 1.2의 같은 행을 고친 것과 맞춘다(날짜·작업자 꼬리표는 옮기지 않는다 — 장부 7절 머리말).
import os
HERE = os.path.dirname(os.path.abspath(__file__))
exec(open(os.path.join(HERE, "수리전체23_ZL_apply.py"), encoding="utf-8").read())
E = [
# z (R13 장부-2, 5절 1)
(r"(명명 상수; 수치와 인증 구간은 부록 D; 2.9가 정의하고 6.6절·8장이 받는다) | 2.9 |",
 r"(명명 상수; 수치와 인증 구간은 부록 D; 2.9가 정의하고 같은 절의 보조정리 {{2:power-sum-renewal}}과 8장이 받는다) | 2.9 |"),
# X_n (R2 5절 2)
(r"과 그 극한(해싱 극한); 분포함수·생존함수는", r"과 그 극한(수렴 $X_n\Rightarrow X$가 해싱 극한); 분포함수·생존함수는"),
# Q (Z2)
(r"| 감소 뒤의 로그오목성(조건부 로그오목성)의 위치별 명제,", r"| 감소 뒤의 로그오목성의 위치별 명제,"),
# Bor_> (Z5 1)
(r"| Borel 꼬리 $\sum_{d>q}\mathrm{Bor}(d)$ | 6.1 |", r"| Borel 꼬리 $\sum_{j>q}\mathrm{Bor}(j)$ | 6.1 |"),
# w_n(t) (Z5 2)
(r"(크기 $t$ 나무를 표시하고 환경을 용량 $k$ 아래에서 센 수); 정규화 $\tilde{\mathfrak w}_n(t)=\mathfrak w_n(t)/p_n$ | 6.2 | $\varpi_n(s)$ ([rb6a2cd0], [rcb2e2d4]); $\varpi_n(N)$ ([r4868e30]; 인수 글자 $N$); $\mathcal T_n(t)$, $\tilde\pi_n(t)$ ([r33475a7]); $\varpi_t(s)$ ([raad7e6d]) |",
 r"(크기 $t$ 나무를 표시하고 환경을 용량 $k$ 아래에서 센 수) | 6.2 | $\varpi_n(s)$ ([rb6a2cd0], [rcb2e2d4]); $\varpi_n(N)$ ([r4868e30]; 인수 글자 $N$); $\mathcal T_n(t)$ ([r33475a7]; 그 기록의 정규화 $\tilde\pi_n(t)$는 이 글에 글자가 없다 — $\mathfrak w_n(t)/p_n$); $\varpi_t(s)$ ([raad7e6d]) |"),
# H_d (스스로)
(r"| 정리 {{6:old-8-22}}의 수준별 손실 합(결손 $d$의 몫;", r"| 정리 {{6:old-8-22}}의 결손별 손실 합(결손 $d$의 몫;"),
# V (Z5 5, Z9 4)
(r"에서 $\mathcal V_k(m)\ge0$); 꼬리표는 (V) | 6.5 |", r"에서 $\mathcal V_k(m)\ge0$); 6장 안에서는 (V)로도 적는다 | 6.5 |"),
# vm (Z5 4)
(r"얼린 법칙 $\Pr^{y_0}$ 아래 수준 $q$의 생존 가중 방문 질량 $\mathbb E^{y_0}[\Pi_j(y);", r"얼린 법칙 $\Pr^{y_0}$ 아래 초과 $q$에서의 생존 가중 방문 측도 $\mathbb E^{y_0}[\Pi_j(y);"),
(r"(6.5절 머리 문단의 수준별 공식 (6.35); 보조정리 {{2:h-transform}}(가)의",
 r"(6.5절 머리 문단이 정의하고 식 (6.35)이 초과마다 이 양을 무게로 더한다; 보조정리 {{2:h-transform}}(가)의"),
# P^(k)_m(j) (R10 A-가)
(r"$P_m(j)$, $P_N(J=j)$ ([r051bfe1] L68·163)", r"$P_m(j)$, $P_N(J=j)$ ([r051bfe1] L64·163)"),
# 7.7의 다섯 행 (Z7 L4; R7b 5절 6 — 기록 원문 확인)
(r"| 분할 무게 $\binom{n-1}mp_mA_{n-1-m,k-1}/A_{n,k-1}$ | 7.7 | 같음 ([r3d0856b], [re71a735]) |",
 r"| 분할 무게 $\binom{n-1}mp_mA_{n-1-m,k-1}/A_{n,k-1}$ | 7.7 | 같음 ([raad7e6d], [r317d678], [r3d0856b], [re71a735]) |"),
(r"| 문턱 단위 $w_{n-k}s_{n-k}(k+1)$ | 7.7 | $N_{thr}$ ([r3d0856b], [re71a735]) |", r"| 문턱 단위 $w_{n-k}s_{n-k}(k+1)$ | 7.7 | $N_{thr}$ ([r317d678], [r3d0856b], [re71a735]) |"),
(r"| $\mathrm{Left}_n$ | 왼쪽 항 $\sum_{m=k}^{2k}w_m\mathfrak p_m$ | 7.7 | — |",
 r"| $\mathrm{Left}_n$ | 왼쪽 자식 몫 $\sum_{m=k}^{2k}w_m\mathfrak p_m$(왼쪽 자식이 첫 층 자식인 뿌리들에서 그 자식에 붙은 선형 몫과 상속을 합친 양) | 7.7 | $\mathrm{Left}_t$ ([raad7e6d], [r317d678]) |"),
(r"| 둘째 층 한 걸음 항등식의 이차 몫; 깊은 자식 몫 | 7.7 | — |", r"| 둘째 층 한 걸음 항등식의 이차 몫; 깊은 자식 몫 | 7.7 | $\mathrm{Quad}_t$, $\mathrm{Stem}_t$ ([raad7e6d], [r317d678], [r3d0856b]) |"),
(r"의 항; 9장이 받아 쓴다) | 7.7 | — |", r"의 항; 9장이 받아 쓴다) | 7.7 | $KD^\prime_t$ ([r317d678], [r3d0856b]) |"),
# 8장 (Z8 2·4·6·7·10)
(r"| 부족량 $\Psi(q)-\mathfrak R_q$(창의 수준 질량이 극한값에서 모자라는 양; $\mathfrak D_0=0$) | 8.1 |",
 r"| 부족량 $\Psi(q)-\mathfrak R_q$($\mathfrak R_q$가 $k=\infty$의 극한값 $\Psi(q)$에서 모자라는 양; $\mathfrak D_0=0$) | 8.1 |"),
(r"| 착지 창의 수준 질량 $k\,c_{k+q}(k)$ | 8.1 |", r"| 착지 창의 수준 질량에 용량을 곱한 값 $k\,c_{k+q}(k)$ | 8.1 |"),
(r"$\mathrm{Esc}_{6600}$은 8.2절 (8.14)의 탈출 봉투 몫의 $k=6600$ 값) | 8.2 |", r"$\mathrm{Esc}_{6600}$은 8.2절 (8.14)의 탈출 하계 $\mathrm{Esc}_k$의 $k=6600$ 값) | 8.2 |"),
(r"| Jensen 봉투 지수의 $k\to\infty$ 극한 $\frac43(2\pi)^{-1/2}\xi^{3/2}$ | 8.2 |",
 r"| (8.10)의 $\mathrm{Bp}(\xi k^{2/3},k)$의 $k\to\infty$ 극한 $\frac43(2\pi)^{-1/2}\xi^{3/2}$(닫힌 꼴 봉투의 Jensen 성분 $e^{-\mathsf j_\infty}$의 지수) | 8.2 |"),
(r"의 생존과 수준 질량의 괄호 $[s_{k+q-1}(k+1)+\mathfrak R_{q-1}]$를 아래에서 막아 더한 합",
 r"의 원천에 쓰는 생존과 $\mathfrak R_{q-1}$의 괄호 $[s_{k+q-1}(k+1)+\mathfrak R_{q-1}]$를 아래에서 막아 더한 합"),
]
apply(os.path.join(HERE, "..", "..", "장v2", "부록A.md"), E)
