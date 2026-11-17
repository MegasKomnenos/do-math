# -*- coding: utf-8 -*-
# 수리 V6 — 장v2/부록A.md(기호표)의 손 편집 목록. 9장 절은 한 덩어리(절 머리부터 다음 절 머리 앞까지)라 함수로 지운다.
import io, os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from 수리_U17_편집 import apply
A = os.path.join(HERE, '..', '..', '장v2', '부록A.md')


def drop_section9(dry):
    text = io.open(A, encoding='utf-8').read()
    assert '\r' not in text
    lines = text.split('\n')
    a = next(i for i, l in enumerate(lines) if l.startswith('### 9장에서 정의하는 기호'))
    b = next(i for i, l in enumerate(lines) if i > a and l.startswith('### '))
    print(f'부록 A 9장 절: 줄 {a+1}–{b}({b-a}줄) 삭제; 기호 행 {sum(1 for l in lines[a:b] if l.startswith("| $"))}')
    del lines[a:b]
    if not dry:
        io.open(A, 'w', encoding='utf-8', newline='\n').write('\n'.join(lines))


ops = [
    # 9장만 쓰던 앞 장 글자(V2·V3·V1)와 W2·W8·V6 판단
    ('del_row', '| $P_t(k)$ |'),
    ('del_row', r'| $\varrho_t, \varrho^{\mathrm H}, \varrho^{\mathrm L}, \varrho_{\min}, \varrho^{\mathrm{lb}}_t$ |'),
    ('del_row', r'| $\mathrm{dec}_N$ |'),
    ('del_row', '| $D_k$ |'),
    ('del_row', r'| $\Upsilon_k, \hat\Upsilon_k$ |'),
    ('del_row', r'| $\varphi^\flat_k$ |'),
    ('del_row', r'| $\mathsf{LRP}_2$ |'),
    ('del_row', r'| $\mathrm{lk}_{n,m}$ |'),
    ('del_row', r'| $\mathcal H_{\mathrm B}(q)$ |'),
    ('del_row', r'| $\mathsf{SRC}^+$ |'),
    ('del_row', r'| $\mathrm{lp}_k, \mathrm{lpr}_k$ |'),
    # 새 행: 기저량 $P_n(y)$(5.5; 1.2가 머리 합 행을 바꾼 것), $\Pi^{\mathrm{up}}_j$(10.4; V1·V3 인계)
    ('ins_after', r'| $\mathrm{IH}(n,y)$ |', [r'| $P_n(y)$ | 기저량 $\sum_{t=y}^{n}x_t(y)$(5.5절 Abel 재배열의 기저 — 명제 {{5:old-5-22}} 첫 항의 인자; 따름정리 {{6:cor-L}}가 아래에서 막는다) | 5.5 | $D2S_n(y)$ ([r23f10e9], [r58b4caa]) |']),
    ('ins_after', r'| $\mathrm{PM}_y(d)$ |', [r'| $\Pi^{\mathrm{up}}_j$ | 길이 $j$의 무거운 사슬 위에서 잰 생존 곱의 상계 계수 $\prod_{i=1}^{j}\frac{k+1}{k+i}$(10.4절 준비 문단; 명제 {{10:reduction-na}} 증명 (5)·명제 {{10:old-8-35}} 증명이 쓴다) | 10.4 | $\tau_h$ ([r3d0856b]; 첨자 $h\to j$) |']),
    # 뜻·기록의 글자 열
    ('sub', '| $c_m(Y)$ |', r'$c^\pm_m$ ([r5909c9e]); ', ''),
    ('sub', '| $c^{(2)}_m$ |', r'$C^\pm_s$([rae1f209], [r5909c9e])는', r'$C^\pm_s$([rae1f209])는'),
    ('sub', r'| $\pi^0_n(y)$ |', r'$P_0(N)$ ([rae1f209], [r5909c9e]; 인수 $k$ 고정); $P^{up}_0$ ([r5909c9e]); $q_F=\pi^0_F(F/2)$ ([r2fe0259]); ', r'$P_0(N)$ ([rae1f209]; 인수 $k$ 고정); '),
    ('sub', r'| $\pi^0_n(y)$ |', r'$\mathcal N(s,v+1)$ ([rc391829]); ', ''),
    ('sub', r'| $\pi_n(m)$ |', '([rae1f209], [r5909c9e], [r030ffae])', '([rae1f209], [r030ffae])'),
    ('sub', r'| $\mathcal N_\ell(t)$ |', r'$T_\ell(s)$ ([r5909c9e]); ', ''),
    ('sub', r'| $\Psi(q)$ |', r'$\Psi(b)$ ([r030ffae], [r5909c9e])', r'$\Psi(b)$ ([r030ffae])'),
    ('sub', r'| $\mathsf z_{1/2}, \mathsf z_{-1/2}, \mathsf z_{3/2}$ |', '6.6절·8장·9장이 받는다', '6.6절·8장이 받는다'),
    ('sub', r'| $\mathrm{rb}_m$ |', r'$\rho_m$ ([r5909c9e], [rae1f209])', r'$\rho_m$ ([rae1f209])'),
    ('sub', r'| $\delta_t$ |', r'; $V_{s-1}$ ([rc391829]; 첨자 한 칸)', ''),
    ('sub', r'| $\mathrm{Bor}^{*j}(m)$ |', r'$B^{(*n)}(\ell)$ ([r5909c9e]); ', ''),
    ('sub', r'| $\mathrm{PAIR}_n$ |', r'; $E_n$ ([rc391829]; 정리 1의 교차항, $/p_n$ 정규화)', ''),
    ('sub', '| $s_m(y)$ |', r'$s_N,q_N,t_N$ ([rae1f209], [r030ffae]; [r5909c9e]는 $s_m$만)', r'$s_N,q_N,t_N$ ([rae1f209], [r030ffae])'),
    ('sub', '| $s_m(y)$ |', r'$u_m(Y)$, $u_n(y)$ ([r8a9b11e], [r23f10e9], [r58b4caa], [rc391829])', r'$u_m(Y)$, $u_n(y)$ ([r8a9b11e], [r23f10e9], [r58b4caa])'),
    ('sub', r'| $x_\ast$ |', r'; $m^*$ ([rc391829])', ''),
    ('sub', '| $f$ |', '2·4·5·6·7·9장 증명 안의', '2·4·5·6·7장 증명 안의'),
    ('sub', r'| $T^{\le k}, T^{>k}$ |', r'| $T_{\le k}$, $T_{>k}$ ([r475ada3]) |', r'| $T_{\le k}$, $T_{>k}$ ([r475ada3]); $T_c(x)$ ([ra4c01fc]; 아래 첨자, 용량 $c\to k$) |'),
    ('sub', r'| $\mathsf u(k), \mathsf u^\flat(k)$ |', r'$\Upsilon_k$ 상계의 함수 $\frac3{0.35}', r'중앙 행 수준 질량 상계의 함수(따름정리 {{6:old-8-11}}(가)(나)) $\frac3{0.35}'),
    ('set_row', r'| $\mathcal R_2$ |', r'| $\mathcal R_2$ | 실질 잔여 $\{(n,k):k\ge6668,\max(2k+103,20001)\le n\le3k-1\}$ — 7장의 환원이 주 정리에 남긴 위치의 집합(그 모든 위치에서 $(\star)(n)\ge0$을 10장이 보인다) | 7.8 | — |'),
    ('sub', r'| $\Omega(\xi), \Omega_q$ |', r'$W$, $W_c$ ([r030ffae], [r5909c9e])', r'$W$, $W_c$ ([r030ffae])'),
    ('sub', r'| $\xi$ |', '$y$ ([r5909c9e]); ', ''),
    ('sub', r'| $\mathrm{Bor}_\le(q)$ |', r'$S_0(\nu)$ ([r5909c9e]); ', ''),
    ('sub', r'| $\vartheta, \vartheta_0$ |', r'(명제 {{10:old-8-35}}의 진술이 정의)(6.4의 국소 함수 $\vartheta_\xi(y)$ — 그 $\xi=0$ 값 $\vartheta_0$ 포함 — 와 다른 양)', r'(명제 {{10:old-8-35}}의 진술이 정의)'),
    ('sub', r'| $\mathrm{vm}_y(q)$ |', '수준별 공식 (6.37)', '수준별 공식 (6.35)'),
    ('sub', r'| $\mathfrak w_n(t)$ |', r'; $\tilde\pi_n(s)$ ([rc391829])', ''),
    # X4 (a): $\mathfrak c_0(N)$의 뜻 — 보조정리 `8:old-6-30`은 (가)(나)뿐이고 8.3절은 용량 이동 비 보조정리의 하계와 (나)의 큰 쪽을 이 글자로 둔다
    ('sub', r'| $\mathfrak c_0(N)$ |', r'보조정리 {{8:old-6-30}} (가)(다)의 큰 쪽', r'보조정리 {{2:capacity-shift-ratio}}의 하계와 보조정리 {{8:old-6-30}}(나)의 하계 가운데 큰 쪽'),
]

if __name__ == '__main__':
    dry = '--dry' in sys.argv
    drop_section9(dry)
    apply(A, ops, dry=dry)
