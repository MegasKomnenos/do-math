# -*- coding: utf-8 -*-
# 수리 V6 — 장부_v2.md 1.1·1.2절의 손 편집 목록(9장 제거 물결 V1–V5와 W1–W9 인계의 반영). 수리_U17_편집.apply로 적용.
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from 수리_U17_편집 import apply
LEDGER = os.path.join(HERE, '..', '..', '장부_v2.md')

ops11 = [
    ('sub', '| $m$ |', '| 1, 2, 3, 5, 6, 7, 8, 9, 10, 11 |', '| 1, 2, 3, 5, 6, 7, 8, 10, 11 |'),
    ('sub', '| $t$ |', '| 2, 5, 6, 7, 8, 9, 10 |', '| 2, 5, 6, 7, 8, 10 |'),
    ('sub', '| $N:=n-k$ |', '| 1, 6, 7, 8, 9, 10 |', '| 1, 6, 7, 8, 10 |'),
    ('sub', '| $y$ |', '| 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11 |', '| 1, 2, 3, 4, 5, 6, 7, 8, 10, 11 |'),
    ('sub', '| $Y$ |', '| 1, 2, 5, 6, 9 |', '| 1, 2, 5, 6 |'),
    ('sub', '| $Y$ |', r'1.5 좌표표의 $c_m(Y)$ 행과 9.3절(정리 `{{9:old-7-16}}` 증명이 보조정리 `{{2:old-2-34}}`를 수준 $Y$로 쓴다)도 센다(2026-11-15 5차 K14-1·VL)', r'1.5 좌표표의 $c_m(Y)$ 행도 센다(2026-11-15 5차 K14-1·VL)'),
    ('sub', '| $u$, $v$ |', '| 2, 5, 6, 7, 8, 9 |', '| 2, 5, 6, 7, 8 |'),
    ('sub', '| $u$, $v$ |', '$v$는 여섯 장 모두', '$v$는 다섯 장 모두'),
    ('sub', '| $u$, $v$ |', '$u$는 2·6·9장뿐', '$u$는 2·6장뿐'),
    ('sub', r'| $r:=n-\ell-1$ |', '| 1, 2, 4, 5, 9, 11 |', '| 1, 2, 4, 5, 11 |'),
    ('sub', r'| $r:=n-\ell-1$ |', '2.12절의 꼬리 좌표 $r$도 센다 — 2026-11-15 5차 K1-2·K14-1·VL; 9장 머리가 $r=n-k$를 한 번 부르고 $N$으로 바꿔 적는 자리와 11.2절 표의 5장 항목도 센다 — 2026-11-15 8차 N14-1·YL)', '2.12절의 꼬리 좌표 $r$도 센다 — 2026-11-15 5차 K1-2·K14-1·VL; 11.2절 표의 5장 항목도 센다 — 2026-11-15 8차 N14-1·YL)'),
    ('sub', r'| $r:=n-\ell-1$ |', '(1.5가 한 문장으로 밝힌다); 9장은 $N$을 쓴다. ', '(1.5가 한 문장으로 밝힌다). '),
    ('sub', r'| $\nu:=n-2k$ |', '| 1, 4, 6, 7, 8, 9, 10, 11 |', '| 1, 4, 6, 7, 8, 10, 11 |'),
    ('sub', '| $d$ |', '| 1, 2, 5, 6, 7, 8, 9, 10, 11 |', '| 1, 2, 5, 6, 7, 8, 10, 11 |'),
    ('sub', '| $q$ |', '| 1, 2, 5, 6, 7, 8, 9, 10, 11 |', '| 1, 2, 5, 6, 7, 8, 10, 11 |'),
]

DEL12 = [
    # 9장 전역 글자(31)
    '| $m_1(k)$ |', '| $P^+_t(k)$ |', r'| $P^{\theta}_t(k)$ |', r'| $A^{(t)}_N, A^\diamond_N$ |', r'| $A^{\diamond,\mathrm{up}}, A^\diamond_{\mathrm{dec}}$ |',
    '| $K_n(m)$ |', r'| $\gamma_m$ |', r'| $\nu_0(k), \nu_1(k)$ |', r'| $\pi_2(t)$ |', r'| $\pi_n(t_1,t_2)$ |', r'| $\Psi^{\mathrm{lb}}(d)$ |',
    r'| $\mathcal F_k(\nu), \mathcal F^{\mathrm{LP}}_k$ |', r'| $\mathcal O_n$ |', r'| $\mathcal Q_m$ |', r'| $\mathcal Y_k(n), \mathcal Y^{\mathrm{LP}}_k(n)$ |',
    r'| $\mathfrak d_k, \bar{\mathfrak d}_k$ |', r'| $\mathfrak l_m(t)$ |', r'| $\mathfrak V_m$ |', r'| $\mathsf B^+$ |', r'| $\mathsf{FS}(n)$ |',
    r'| $\mathsf H^\ast_+$ |', r'| $\mathsf h_N$ |', r'| $\mathrm{FL}^{(1)}_m$ |', r'| $\mathrm{flat}_k(t)$ |', r'| $\mathrm{land}_m$ |',
    r'| $\mathrm{LP}_k(n)$ |', r'| $\mathrm{merge}, \mathrm{merge}^{\mathrm{up}}$ |', r'| $\mathrm{OB}_m$ |', r'| $\mathrm{Pcor}_m, \mathrm{Pcor}^{\pm}_m$ |',
    r'| $\mathrm{regen}_n$ |', r'| $(\mathrm P\Diamond)$ |',
    # 9장만 쓰던 앞 장의 글자(V2 — 6장 다섯·2장은 $P_t(k)$ 행을 기저량 행으로 바꿈), V3($\mathsf{LRP}_2$), V1($\mathrm{lk}_{n,m}$)
    '| $D_k$ |', r'| $\Upsilon_k, \hat\Upsilon_k$ |', r'| $\varphi^\flat_k$ |', r'| $\varrho_t, \varrho^{\mathrm H}, \varrho^{\mathrm L}, \varrho_{\min}, \varrho^{\mathrm{lb}}_t$ |',
    r'| $\mathrm{dec}_N$ |', r'| $\mathsf{LRP}_2$ |', r'| $\mathrm{lk}_{n,m}$ |',
    # W2($\mathcal H_{\mathrm B}$ 소멸), W8($\mathsf{SRC}^+$ 본문 0), V5·V6($\mathrm{lp}_k$ — 절 밖 호출이 부록 D뿐이라 R1′대로 1.3 7.3 묶음으로)
    r'| $\mathcal H_{\mathrm B}(q)$ |', r'| $\mathsf{SRC}^+$ |', r'| $\mathrm{lp}_k, \mathrm{lpr}_k$ |',
]
ops12 = [('del_row', p) for p in DEL12] + [
    ('set_row', '| $P_t(k)$ |', r'| $P_n(y)$ | P·일반(이탤릭) | 기저량 $\sum_{t=y}^{n}x_t(y)$(5.5절 Abel 재배열의 기저 — 명제 `{{5:old-5-22}}` 첫 항의 인자; 따름정리 `{{6:cor-L}}`가 아래에서 막는다) | 5.5 | 5, 6 | $D2S_n(y)$(5.5.2·1369) | $D2S_n(y)$ ([r23f10e9], [r58b4caa]) |'),
    ('ins_after', r'| $\Pi_j(y)$ |', [r'| $\Pi^{\mathrm{up}}_j$ | \Pi·일반(이탤릭) | 길이 $j$의 무거운 사슬 위에서 잰 생존 곱의 상계 계수 $\prod_{i=1}^{j}\frac{k+1}{k+i}$(10.4절 준비 문단이 정의; 명제 `{{10:reduction-na}}` 증명 (5)·명제 `{{10:old-8-35}}` 증명이 쓴다) | 10.4 | 10 | 같음(8.4·3418) | $\tau_h$ ([r3d0856b]; 첨자 $h$는 1.1 지표 $j$로 — 예약 글자) |']),
    ('sub', '| $c_m(Y)$ |', r'$c^\pm_m$ ([r5909c9e]); ', ''),
    ('sub', '| $c^{(2)}_m$ |', r'$C^\pm_s$([rae1f209], [r5909c9e])는', r'$C^\pm_s$([rae1f209])는'),
    ('sub', '| $f$ |', '2·4·5·6·7·9장 증명 안의', '2·4·5·6·7장 증명 안의'),
    ('sub', '| $s_m(y)$ |', r'$s_N,q_N,t_N$ ([rae1f209], [r030ffae]; [r5909c9e]는 $s_m$만)', r'$s_N,q_N,t_N$ ([rae1f209], [r030ffae])'),
    ('sub', '| $s_m(y)$ |', r'$u_m(Y)$, $u_n(y)$ ([r8a9b11e], [r23f10e9], [r58b4caa], [rc391829])', r'$u_m(Y)$, $u_n(y)$ ([r8a9b11e], [r23f10e9], [r58b4caa])'),
    ('sub', r'| $x_\ast$ |', r'; $m^*$ ([rc391829])', ''),
    ('sub', r'| $H_k(\sigma), H_k(F)$ |', r'; 9장은 9.1절 보조정리 `{{9:chain-moments}}`의 증명이 $H_t(F)$를 쓴다 — 2026-11-16 14차 H14-3·JL)', ')'),
    ('sub', r'| $S_1>S_2>\cdots$ |', ', 6.6절 $S_0:=n$, 9.1절 $S_0:=m+1$ — 2026-11-15 T4)', ', 6.6절 $S_0:=n$ — 2026-11-15 T4)'),
    ('sub', r'| $T^{\le k}, T^{>k}$ |', r'| $T_{\le k}$, $T_{>k}$ ([r475ada3]) |', r'| $T_{\le k}$, $T_{>k}$ ([r475ada3]); $T_c(x)$ ([ra4c01fc]; 아래 첨자, 용량 $c\to k$) |'),
    ('sub', r'| $Z_k(\sigma), Z_k(F)$ |', r'; 9장은 문턱을 수준 좌표 $w$로 둔 $Z_w(F)$로 쓴다 — 9.1절)', ')'),
    ('sub', r'| $\delta_t$ |', r'; $V_{s-1}$ ([rc391829]; 첨자 한 칸)', ''),
    ('sub', r'| $\Omega(\xi), \Omega_q$ |', r'$W$, $W_c$ ([r030ffae], [r5909c9e])', r'$W$, $W_c$ ([r030ffae])'),
    ('sub', r'| $\pi^0_n(y)$ |', r'$P_0(N)$ ([rae1f209], [r5909c9e]; 인수 $k$ 고정); $P^{up}_0$ ([r5909c9e]); $q_F=\pi^0_F(F/2)$ ([r2fe0259]); ', r'$P_0(N)$ ([rae1f209]; 인수 $k$ 고정); '),
    ('sub', r'| $\pi^0_n(y)$ |', r'$\mathcal N(s,v+1)$ ([rc391829]); ', ''),
    ('sub', r'| $\pi_n(m)$ |', '([rae1f209], [r5909c9e], [r030ffae])', '([rae1f209], [r030ffae])'),
    ('sub', r'| $\Psi(q)$ |', r'$\Psi(b)$ ([r030ffae], [r5909c9e])', r'$\Psi(b)$ ([r030ffae])'),
    ('sub', r'| $\xi$ |', '$y$ ([r5909c9e]); ', ''),
    ('sub', r'| $\mathcal N_\ell(t)$ |', r'$T_\ell(s)$ ([r5909c9e]); ', ''),
    ('set_row', r'| $\mathcal R_2$ |', r'| $\mathcal R_2$ | R·필기체 | 실질 잔여 $\{(n,k):k\ge6668,\max(2k+103,20001)\le n\le3k-1\}$ — 7장의 환원이 주 정리에 남긴 위치의 집합(7.8절이 정의; 그 모든 위치에서 $(\star)(n)\ge0$을 10장이 보인다) | 7.8 | 1, 7, 10 | 같음 | — |'),
    ('sub', r'| $\mathsf u(k), \mathsf u^\flat(k)$ |', r'$\Upsilon_k$ 상계의 함수 $\frac3{0.35}', r'중앙 행 수준 질량 상계의 함수(따름정리 `{{6:old-8-11}}`(가)(나)) $\frac3{0.35}'),
    ('sub', r'| $\mathsf z_{1/2}, \mathsf z_{-1/2}, \mathsf z_{3/2}$ |', '6.6절·8장·9장이 받는다', '6.6절·8장이 받는다'),
    ('sub', r'| $\mathrm{Bor}^{*j}(m)$ |', r'$B^{(*n)}(\ell)$ ([r5909c9e]); ', ''),
    ('sub', r'| $\mathrm{Bor}_\le(q)$ |', '정의 절이 6.6에서 8.1로; 9.5절의 쓰임은 U12로 소멸)', '정의 절이 6.6에서 8.1로)'),
    ('sub', r'| $\mathrm{Bor}_\le(q)$ |', r'$S_0(\nu)$ ([r5909c9e]); ', ''),
    ('sub', r'| $\mathrm{km}_N$ |', r'로마체 이름인 까닭은 당시 9.3의 핵 질량 상계 $\mathfrak K_N$(2026-11-15 5차 1절 1항으로 뺀 글자)과 장식만으로 갈리지 않게 — 재대조 표 3; 세션 결정 54)', '로마체 이름 — 재대조 표 3; 세션 결정 54)'),
    ('sub', r'| $\mathrm{PAIR}_n$ |', r'; $E_n$ ([rc391829]; 정리 1의 교차항, $/p_n$ 정규화)', ''),
    ('sub', r'| $\mathrm{rb}_m$ |', '5.2·6.6·9.1은 이 글자를 쓴다)', '5.2·6.6은 이 글자를 쓴다)'),
    ('sub', r'| $\mathrm{rb}_m$ |', r'$\rho_m$ ([r5909c9e], [rae1f209])', r'$\rho_m$ ([rae1f209])'),
    ('sub', r'| $\mathfrak w_n(t)$ |', r'; $\tilde\pi_n(s)$ ([rc391829])', ''),
    ('sub', r'| $\vartheta, \vartheta_0$ |', r'(명제 `{{10:old-8-35}}`의 진술이 정의)(6.4의 국소 함수 $\vartheta_\xi(y)$ — 그 $\xi=0$ 값 $\vartheta_0$ 포함 — 와 다른 양)', r'(명제 `{{10:old-8-35}}`의 진술이 정의)'),
    ('sub', r'| $\mathrm{vm}_y(q)$ |', '수준별 공식 (6.37)', '수준별 공식 (6.35)'),
]

if __name__ == '__main__':
    dry = '--dry' in sys.argv
    apply(LEDGER, ops11, dry=dry, region=('### 1.1', '### 1.2'))
    apply(LEDGER, ops12, dry=dry, region=('### 1.2', '### 1.3'))
