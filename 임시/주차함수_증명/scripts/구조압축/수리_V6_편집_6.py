# -*- coding: utf-8 -*-
# 수리 V6 — 장v2/부록B.md(인용한 기록)·장v2/부록C.md(용어 대응표)의 손 편집 목록.
#  부록 C 이름 표의 `{{9:…}}` 행 34는 같은 꼴이라 함수로 지운다(그 표 안에서만).
import io, os, re, sys
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from 수리_U17_편집 import apply
B = os.path.join(HERE, '..', '..', '장v2', '부록B.md')
C = os.path.join(HERE, '..', '..', '장v2', '부록C.md')

opsB = [('del_row', '| r5909c9e |'), ('del_row', '| r2fe0259 |'), ('del_row', '| rc391829 |'), ('del_row', '| r29b01e8 |')]


def drop_name_rows9(dry):
    text = io.open(C, encoding='utf-8').read()
    assert '\r' not in text
    lines = text.split('\n')
    a = next(i for i, l in enumerate(lines) if l.startswith('### 기록이 결과에 붙인 이름'))
    b = next(i for i, l in enumerate(lines) if i > a and l.startswith('### '))
    keep, n = [], 0
    for i, l in enumerate(lines):
        if a <= i < b and l.startswith('| ') and '{{9:' in l:
            n += 1
            continue
        keep.append(l)
    print(f'부록 C 이름 표: `{{{{9:` 행 {n} 삭제')
    if not dry:
        io.open(C, 'w', encoding='utf-8', newline='\n').write('\n'.join(keep))


opsC = [
    # 낱말 표
    ('del_row', '| 대칭점 |'), ('del_row', '| 착지 행 |'), ('del_row', '| 재생 원천 |'), ('del_row', '| 평평한 |'),
    ('del_row', '| 재생, 평평한 꼬리, 자르는 크기, 선형 최소화 |'), ('del_row', '| 평평한 핵심 |'),
    ('set_row', '| 핵심 |', '| 핵심 | 핵(둘째 뜻), core | 6.5 |'),
    ('set_row', '| 분할 무게, 문턱 단위, 생존비, 둘째 층 한 칸 비교, 실질 잔여 |', '| 분할 무게, 문턱 단위, 생존비 | 같음; 「장부」(뿌리 종류별 등식)는 「몫의 집계」 | 7.7 |'),
    ('set_row', '| 교차항 |', r'| 교차항 | —(기록 [r05cf8c9]는 글자 $\mathcal X_n$으로, 기록 [r2e22726]은 글자 없이 항등식 (3.1)의 두 나머지로 적음) | 2.10 |'),
    ('set_row', '| 구획, 거대 나무, 창×창 쌍, $k$-단조성, 한 변수 확인 |', '| 구획 | 칸 | 6.4 |'),
    ('set_row', '| 자유 비 |', '| 자유 비 | 자유 비; 성장률(10.1 자리; 기록 [r3d0856b]) | 2.6 |'),
    ('sub', '| 다섯 몫 |', '이 글의 5.4.1절·6.6절의 「다섯 조각」은', '이 글의 6.6절의 「네 조각」은'),
    # 이름 표 — 9장 밖에서 뺀 진술 셋
    ('del_row', '| 기록 [rae1f209]의 보조정리 2 |'),
    ('del_row', '| 기록 [r29b01e8]의 식 (4.1) |'),
    ('del_row', '| 기록 [r696d62c]의 p-lemmaD-sharp, 기록 [r29b01e8]의 p-ups-bound |'),
    # 글자 표(7절의 거울)
    ('sub', '| $s_m(y)$ | [r13b0b8f];', '[r8a9b11e], [r23f10e9], [r58b4caa], [rc391829]; [r39ea75d]', '[r8a9b11e], [r23f10e9], [r58b4caa]; [r39ea75d]'),
    ('sub', r'| $\Pr(X\le x)$, $f$, $x_\ast$ |', r'; [r29c10cd]; [rc391829] | $F$, $f$, $m$; $f_X$, $m$, $m_r$; $m_f$; $x_*$; $\mathfrak m$; $m^*$ |', r'; [r29c10cd] | $F$, $f$, $m$; $f_X$, $m$, $m_r$; $m_f$; $x_*$; $\mathfrak m$ |'),
    ('ins_after', r'| $\mathfrak a^\circ_n$ | [rb7effe0]; [r475ada3] |', [r'| $T^{\le k}, T^{>k}$ | [r475ada3]; [ra4c01fc] | $T_{\le k}$, $T_{>k}$; $T_c(x)$ | 아래 첨자→위 첨자; 첨자 용량 $c\to k$ |']),
    ('sub', r'| $\mathrm{Bor}^{*j}(m)$ | [r8a9b11e]; [r5909c9e];', r'[r8a9b11e]; [r5909c9e]; [re71a735]; [r58b4caa] | $BT(z,D)$; $B^{(*n)}(\ell)$; $BT_n(j)$; $BT_j(J)$(누적)', r'[r8a9b11e]; [re71a735]; [r58b4caa] | $BT(z,D)$; $BT_n(j)$; $BT_j(J)$(누적)'),
    ('sub', r'| $\Psi(q)$ | [r5bbc534], [r9bf2dc6], [r2ec875c];', '; [r030ffae], [r5909c9e]; [r4868e30]', '; [r030ffae]; [r4868e30]'),
    ('sub', r'| $\mathrm{Bor}_\le(q)$ | [r030ffae];', r'[r030ffae]; [r5909c9e]; [r5bbc534]; [r29c10cd] | $S_0(b)$; $S_0(\nu)$; $S_0(d)$; $\beta(m)$', r'[r030ffae]; [r5bbc534]; [r29c10cd] | $S_0(b)$; $S_0(d)$; $\beta(m)$'),
    ('sub', r'| $\pi^0_n(y)$ | [r29c10cd];', '; [rc391829]; [r030ffae];', '; [r030ffae];'),
    ('sub', r'| $\pi^0_n(y)$ | [r29c10cd];', r'$\mathcal N(F,Y)$; $\mathcal N(s,v+1)$; $\pi^0_{N^\prime}(k-1)$', r'$\mathcal N(F,Y)$; $\pi^0_{N^\prime}(k-1)$'),
    ('sub', r'| $\pi^0_n(y)$ | [r29c10cd];', '; [rae1f209], [r5909c9e]; [r2fe0259]; [r39ea75d] |', '; [rae1f209]; [r39ea75d] |'),
    ('sub', r'| $\pi^0_n(y)$ | [r29c10cd];', r'; $P_0(N)$(인수 $k$); $q_F=\pi^0_F(\lfloor F/2\rfloor)$; $f_N(y)=p_N\pi^0_N(y)$ |', r'; $P_0(N)$(인수 $k$); $f_N(y)=p_N\pi^0_N(y)$ |'),
    ('sub', r'| $\mathrm{Bor}(N+1-r)/\mathrm{Bor}(N+1)$($\mathrm{tilt}$ 꼴; 글자 없음) |', r'[r030ffae]; [r5bbc534]; [rc391829] | $\rho_h$, $\rho_j$; $\omega_N(r)$; $R_j=\mathrm{Bor}(F+1-j)/\mathrm{Bor}(F+1)$', r'[r030ffae]; [r5bbc534] | $\rho_h$, $\rho_j$; $\omega_N(r)$'),
    ('del_row', r'| $\mathrm{dec}_N$ | [r051bfe1];'),
    ('del_row', r'| $\varphi^\flat_k$, $\Upsilon_k$ | [r29b01e8] |'),
    ('sub', '| $c_m(m-d)$ | [r29b01e8],', '[r29b01e8], [r2ec875c], [r23f10e9]', '[r2ec875c], [r23f10e9]'),
    ('set_row', '| $P_n(y)$ | [r29b01e8],', r'| $P_n(y)$ | [r23f10e9], [r58b4caa] | $D2S_n(y)=\sum_{t=y}^nx_t(y)$ | 글자 |'),
    ('sub', r'| $\xi$ | [re71a735] §4;', r'[re71a735] §4; [r5909c9e]; [r030ffae]; [rfc69320]; [r9bf2dc6] | $x=\delta/y^{2/3}$; $y=b/k^{2/3}$; $x_b$, $x$;', r'[re71a735] §4; [r030ffae]; [rfc69320]; [r9bf2dc6] | $x=\delta/y^{2/3}$; $x_b$, $x$;'),
    ('sub', r'| $\mathcal N_\ell(t)$ | [r4868e30];', r'[r4868e30]; [r5909c9e]; [rcb2e2d4]; [r05cf8c9] | $c_N(\kappa)=\min(N,\kappa)A_{N-1,\kappa-1}$; $T_\ell(s)$; $\mathcal T_\ell(s)$; $t_s(c)$', r'[r4868e30]; [rcb2e2d4]; [r05cf8c9] | $c_N(\kappa)=\min(N,\kappa)A_{N-1,\kappa-1}$; $\mathcal T_\ell(s)$; $t_s(c)$'),
    ('set_row', r'| $x_t(k)$, $\delta_t$ | [r4868e30];', r'| $x_t(k)$, $\delta_t$ | [r4868e30]; [rcb2e2d4]; [r05cf8c9] | $x_N(k)$; $\hat\delta_s$, $\delta_s$; $\delta_s$ | $N,s\to t$ |'),
    ('sub', r'| $\mathfrak w_n(t)$, $\tilde{\mathfrak w}_n(t)$ | [r4868e30];', r'; [r33475a7]; [rc391829] | $\varpi_n(N)$; $\varpi_n(s)$; $\mathcal T_n(t)$, $\tilde\pi_n(t)$; $\tilde\pi_n(s)$ |', r'; [r33475a7] | $\varpi_n(N)$; $\varpi_n(s)$; $\mathcal T_n(t)$, $\tilde\pi_n(t)$ |'),
    ('sub', '| $c_m(Y)$(6·7장 기록) |', r'[rae1f209], [r030ffae]; [r5909c9e]; [r77e234e], [rae1f209] | $\pi_m(\ell)$; $q_m=\Pr_m(M=k-1)$, $q^+_m$; $r_N$, $r^\prime_N$; $c^\pm_m$; $f_N=f_k=c_N(k-1)$ | 글자; 인수 명시; [r2ec875c]는 $c_m(\ell)$(같은 글자; 9장 기록 행)', r'[rae1f209], [r030ffae]; [r77e234e], [rae1f209] | $\pi_m(\ell)$; $q_m=\Pr_m(M=k-1)$, $q^+_m$; $r_N$, $r^\prime_N$; $f_N=f_k=c_N(k-1)$ | 글자; 인수 명시; [r2ec875c]는 $c_m(\ell)$(같은 글자; 아래 [r2ec875c] 행)'),
    ('sub', r'| $\mathrm{rb}_m$ | [r5909c9e], [rae1f209];', '[r5909c9e], [rae1f209]; [r5bbc534]', '[rae1f209]; [r5bbc534]'),
    ('set_row', r'| $x_\ast$ | [r29c10cd]; [rc391829] |', r'| $x_\ast$ | [r29c10cd] | $\mathfrak m=0.5996\ldots$ | 글자 |'),
    ('set_row', '| $Z_c(F)$, $Z_w(F)$ |', r'| $Z_c(F)$, $Z_y(F)$ | [r9bf2dc6]; [r2ec875c] | $\mathfrak h_d=\#\{v:s_v\ge c+1\}$; $Z=\lvert\{w:s_w\ge v+1\}\rvert$ | 글자; 문턱 $c$, $v$([r2ec875c]의 문턱 $v$는 1.1 용량 변수 $y$의 자리 — 보조정리 {{2:level-mass-jensen}}(가)가 $Z_y(F)$로 쓴다; 꼭짓점 지표 $w\to v$) |'),
    ('del_row', r'| $\mathrm{lp}_k$, $\mathrm{lpr}_k$ | [rf451d83], [rb7effe0], [r89eb039]; [rf451d83] |'),
    ('set_row', r'| $\mathrm{tail}_s(y)$, $t_0(y)$, $x_t(y)$, $\mathrm{IH}(n,y)$ |', r'| $\mathrm{tail}_s(y)$, $t_0(y)$, $x_t(y)$, $\mathrm{IH}(n,y)$ | [r58b4caa], [r8a9b11e], [r23f10e9] | $\mathcal T_s(y)=\sum_{t=s+1}^nx_t(y)$, $t_0(y)$, $x_t(y)$, $H(n,y)$ | 글자(첨자 $s$는 같음); 없음; 글자 |'),
    ('set_row', r'| $\Omega(\xi)$, $\Omega_q$ | [r030ffae], [r5909c9e] |', r'| $\Omega(\xi)$, $\Omega_q$ | [r030ffae] | $W$(감소 함수 $[0,X]\to[0,1]$), $W_c=W(x_c)$ | 없음; $x_b$는 변수($\xi$); 첨자 $c\to q$ |'),
    ('set_row', r'| $\Psi^{\mathrm{low}}_{(\varrho)}$, $\mathsf c_\Psi$ |', r'| $\Psi^{\mathrm{low}}_{(\varkappa)}$, $\mathsf c_\Psi$ | [r030ffae]; [rfc69320] | $\Psi_{(r)}=C_2(2\sqrt r+\zeta(\frac12)-\zeta(\frac32)/12+(2\sqrt r)^{-1}-r^{-3/2}/24)$; $\Psi_\flat(r)$, $C_\Psi=1.6780525$ | 글자(실수 인수 정밀판; 인수 글자 $r\to\varkappa$; 정의 절 2.9 — 보조정리 {{2:power-sum-renewal}}(ㄴ)); 상수는 산세리프 명명 상수 |'),
    ('del_row', r'| $\mathfrak B_N$, $\mathfrak B^{\mathrm{low}}(k,\nu)$ |'),
    ('sub', r'| $\pi_n(m)$(8장 기록) |', r'[r8456f59], [r5909c9e], [rae1f209] | $\varpi_L(s)$, $\varpi_n(s)$; $\pi_N(m)$, $\varpi_N(g)$, $\varpi_N(s)$', r'[r8456f59], [rae1f209] | $\varpi_L(s)$, $\varpi_n(s)$; $\pi_N(m)$, $\varpi_N(s)$'),
    ('del_row', r'| $\mathrm{merge}^{\mathrm{up}}$, $A^{(t)}_N$,'),
    ('del_row', r'| $\gamma_m$, $K_n(m)$, $\mathcal Q_m$, $\mathcal C_n$ |'),
    ('del_row', r'| $\mathrm{OB}_m$, $\mathrm{FL}^{(1)}_m$,'),
    ('set_row', r'| $b^T_{t,k}/p_{t-1}$, $b^T_{t,k-1}/p_{t-1}$(글자 없음) |', r'| $b^T_{t,k}/p_{t-1}$, $b^T_{t,k-1}/p_{t-1}$(글자 없음) | [rae1f209] | $\tilde u_s=u_s/p_{s-1}=q_{s-1}+kr_{s-1}$, $\tilde v_s=v_s/p_{s-1}$ | 글자 없이 풀어 적음($u_s=b^T_{s,k}$, $v_s=b^T_{s,k-1}$); $s\to t$ |'),
    ('del_row', r'| $\pi_n(t_1,t_2)$, $\pi_2(t)$ |'),
    ('del_row', r'| $\mathrm{rb}_m$, $\mathrm{Bor}_\le(\nu)$, $\mathrm{Bor}^{*n}(\ell)$ |'),
    ('set_row', r'| $c_m(\ell)$, $\mathrm{Bor}(n)$, $\mathrm{Ren}(r)$, $\Psi(d)$, $Z_w(F)$, $t_v$ |', r'| $c_m(\ell)$, $\mathrm{Bor}(n)$, $\mathrm{Ren}(r)$, $\Psi(d)$, $Z_y(F)$, $t_v$ | [r2ec875c] | $c_m(\ell)=b_{m,\ell}/p_m$, $\beta_n=u(n)/n$, $u(r)$, $\Psi(d)$, $Z=\lvert\{w:s_w\ge v+1\}\rvert$, $s_w$ | 없음; 꼭짓점 지표 $w\to v$($s_w=t_v$), 문턱 $v$는 용량 변수 $y$의 자리(보조정리 {{2:level-mass-jensen}}(가)); 숲 크기 $L\to m$ |'),
    ('del_row', r'| $\mathfrak w_n(S_k)/\mathfrak w_n(k)$(글자 없음) |'),
    ('del_row', r'| $P_t(k)$, $P^+_t(k)$, $\mathrm{flat}_k(t)$,'),
    ('set_row', r'| $\mathrm{PAIR}_n$, $\mathrm{PAIR}_n/p_n$ |', r'| $\mathrm{PAIR}_n$ | [rb6a2cd0], [r05cf8c9] | $\mathcal X_n$($2k+1\le n\le3k-1$에서 $=\mathrm{PAIR}_n$) | 범위 명시 |'),
    ('ins_after', r'| $\mathrm{PAIR}_n$ | [rb6a2cd0], [r05cf8c9] |', [r'| 교차항(정리 {{2:tree-expansion}}(가)의 두 합; 글자 없음) | [r2e22726]; [r05cf8c9] | 항등식 (3.1)의 두 나머지(글자 없음); $\mathcal X_n$ | 글자 없이 풀어 적음; [r05cf8c9]의 $\mathcal X_n$은 위 $\mathrm{PAIR}_n$ 행 |']),
    ('del_row', r'| $\mathcal O_n$ | [r05cf8c9]; [r2e22726] |'),
    ('del_row', r'| $\mathrm{flat}_k(s+1)$, $\pi^0_s(v+1)$,'),
    ('del_row', r'| $\mathrm{regen}_n$, $\mathsf{FS}(n)$ |'),
    ('set_row', r'| $A_{n,c-1}$, $T_{c-1}(x)$, $\mathcal N_{c-1}(t)$,', r'| $A_{n,c-1}$, $T_{c-1}(x)$, $\mathcal N_{c-1}(t)$, $A_{c-1}(x)$, $\mathcal B_k(x)$, $\mathcal B_{k-1}(x)$, $\delta_t$ | [r05cf8c9] | $\mathcal A_n(c)$, $T_c(z)$, $t_s(c)$, $F_c=\exp T_c$, $a$, $b$, $\delta_s$ | 첨자 용량→수준; $s\to t$ |'),
    ('set_row', r'| $\mathcal Y_k(n)$, $\mathcal Y^{\mathrm{LP}}_k(n)$,', r'| $\theta_t(k)$ | [rb6a2cd0] | $\theta_N(k)$ | $N\to t$ |'),
    ('set_row', r'| $\varrho_t$, $\varrho^{\mathrm H}$, $\varrho^{\mathrm L}$, $\varrho_{\min}$, $\mathfrak r_N$,', r'| $\mathfrak r_N$, $\mathrm{hz}_k(N)$, $s_N(k)$, $\mathsf u(k)$, $g(x)$ | [rb6a2cd0] | $r_N$, $h_k(N)$, $\mathfrak s_N$, $\tilde g(k)$, $g(j)$ | 없음 |'),
    ('set_row', '| $s_N(k)$, $s_N(k+1)$, $s_N(k-1)$ |', r'| $s_N(k)$, $s_N(k+1)$, $s_N(k-1)$ | [rae1f209], [r030ffae] | $s_N=\Pr_N(M\le k-1)$, $q_N=\Pr_N(M\le k)$, $t_N=\Pr_N(M\le k-2)$ (L25; L42·223) | 용량 인수 명시(수준 $k-1$, $k$, $k-2$ → 용량 $k$, $k+1$, $k-1$) |'),
    ('del_row', r'| $\pi^0_F(\lfloor F/2\rfloor)$ |'),
    ('del_row', r'| $\Theta^\circ_n$, $K_n(m)$, $\gamma_m$, $\mathcal Q_m$ |'),
    ('set_row', r'| $\mathcal H_{\mathrm B}(q)$, $\mathrm{Ren}(j)$, $\mathrm{Bor}(j)$, $\mathrm{Bor}^{*j}(m)$ |', r'| $\mathrm{Ren}(j)$, $\mathrm{Bor}(j)$, $\mathrm{Bor}^{*j}(m)$ | [r6a8c8b6] §6 | $c_h=h\beta_h=\sum_{j\ge1}\beta^{*j}(h)$, $\beta_h$, $\beta^{*j}(h)$ | 글자(첨자→인수); 글자만 다름; 글자만 다름 |'),
]

if __name__ == '__main__':
    dry = '--dry' in sys.argv
    apply(B, opsB, dry=dry)
    drop_name_rows9(dry)
    apply(C, opsC, dry=dry)
