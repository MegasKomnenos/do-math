# -*- coding: utf-8 -*-
# 수리 V6 — 장부_v2.md 4절(이름 사전)·5절·6절·7절·8절의 손 편집 목록.
#  4절의 9장 행 39와 식별자 소멸 기록 이름은 행마다 같은 꼴의 뺌 표기라 한 함수로 적용한다(행 단위; 머리 셀·라벨 셀 보존).
import io, os, re, sys
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from 수리_U17_편집 import apply
LEDGER = os.path.join(HERE, '..', '..', '장부_v2.md')
GONE_IDS = ['r5909c9e', 'rc391829', 'r2fe0259', 'r29b01e8']   # 9장 제거 물결로 본문·부록 D 인용이 사라진 기록(부록 B에서 뺌)
SPECIAL_NOTE = {
    '9:old-7-46': '(2026-11-17 구조 압축 K6·V1로 뺌 — 9장 삭제; 주 정리는 정리 `10:old-8-37`로 닫힌다)',
    '9:old-7-45': '(2026-11-17 구조 압축 K6·V1로 뺌 — 9장 삭제; $\\mathsf{LRP}_2$는 7.7절의 정리 `7:old-6-22`와 함께 소멸)',
}
NOTE = '(2026-11-17 구조 압축 K6·V1로 뺌 — 9장 삭제)'


def transform_sec4(dry):
    text = io.open(LEDGER, encoding='utf-8').read()
    assert '\r' not in text
    lines = text.split('\n')
    a = next(i for i, l in enumerate(lines) if l.startswith('## 4. '))
    b = next(i for i, l in enumerate(lines) if l.startswith('## 5. '))
    n9 = nid = 0
    for i in range(a, b):
        l = lines[i]
        if not l.startswith('| ') or l.startswith('|---'):
            continue
        cells = l.strip().strip('|').split(' | ')
        cells = [c.strip() for c in cells]
        if len(cells) != 6:
            continue
        num, kind, name, rec, sec, lab = cells
        changed = False
        m = re.fullmatch(r'\{\{(9:[^}]+)\}\}', lab)
        if m:
            key = m.group(1)
            name = name + SPECIAL_NOTE.get(key, NOTE)
            sec = '뺌'
            lab = '(' + key + ')'
            n9 += 1
            changed = True
        for rid in GONE_IDS:
            if rid in rec:
                rec = rec.replace('기록 [' + rid + ']', '옛 기록(식별자 소멸)').replace('[' + rid + ']', '옛 기록(식별자 소멸)')
                nid += 1
                changed = True
        if changed:
            lines[i] = '| ' + ' | '.join([num, kind, name, rec, sec, lab]) + ' |'
    print(f'4절: 9장 행 → 뺌 {n9}, 소멸 식별자 기록 이름 고침 {nid}')
    if not dry:
        io.open(LEDGER, 'w', encoding='utf-8', newline='\n').write('\n'.join(lines))


ops4 = [
    ('sub', '기록이 붙인 이름은 아래 표의 라벨이 놓이는', '6장(6.6절)·8장·9장이 받는다', '6장(6.6절)·8장이 받는다'),
    ('set_row', '| 2.39 | 따름정리 |', '| 2.39 | 따름정리 | 머리 합의 안쪽 층(2026-11-17 구조 압축 K6·V2로 뺌 — 소비처 소멸; 머리 합 $P_t(k)$ 문단도 함께) |  | 뺌 | (2:old-2-39) |'),
    ('set_row', '| 2.41 | 명제 |', '| 2.41 | 명제 | 쌍 항의 정수 꼴(2026-11-17 구조 압축 K6·V2로 뺌 — 소비처 소멸) | 기록 [rae1f209]의 보조정리 2 | 뺌 | (2:old-2-41) |'),
    ('set_row', '| — | 따름정리 | 무게 증분의 하계 |', '| — | 따름정리 | 무게 증분의 하계(2026-11-17 구조 압축 K6·V2로 뺌 — 소비처 소멸; 무게 증분 $\\varrho_t$·감소율 $\\mathrm{dec}_N$의 정의도 함께) |  | 뺌 | (6:increment-bounds) |'),
    ('set_row', '| — | 보조정리 | 짝 재배열 |', '| — | 보조정리 | 짝 재배열(2026-11-17 구조 압축 K6·V2로 뺌 — 따름정리 `6:cor-L`의 특수화; 소비처 소멸) | 옛 기록(식별자 소멸)의 식 (4.1) | 뺌 | (6:pair-rearrange) |'),
    ('set_row', '| — | 정리 | 평평한 핵심의 하계와 $\\Upsilon_k$의 상계 |', '| — | 정리 | 평평한 핵심의 하계와 $\\Upsilon_k$의 상계(2026-11-17 구조 압축 K6·V2로 뺌 — 소비처 소멸; $\\varphi^\\flat_k$·$\\Upsilon_k$·$D_k$의 정의 문단도 함께) | 기록 [r696d62c]의 p-lemmaD-sharp, 옛 기록(식별자 소멸)의 p-ups-bound | 뺌 | (6:D-bound) |'),
    ('set_row', '| 6.22 | 정리 |', '| 6.22 | 정리 | 주 정리와 둘째 층 한 칸 비교의 동치(2026-11-17 구조 압축 K6·V3로 뺌 — 소비처 소멸; 7.8절은 7장이 남긴 것을 $\\mathcal R_2$에서 $(\\star)(n)\\ge0$으로 적는다) |  | 뺌 | (7:old-6-22) |'),
    ('sub', '| 6.29 | 정리 |', '(2026-11-17 구조 압축 K4-2·U9로 뺌 — 정리 `8:old-6-33`의 둘째 문턱($103\\le\\nu\\le3.6k^{2/3}$에서 $1.05$))', '(2026-11-17 구조 압축 K4-2·U9로 뺌 — 정리 `8:old-6-33`의 둘째 문턱으로 흡수되었고 그 문턱도 K6·V3로 소멸)'),
    ('set_row', '| — | 명제 | 두 장부의 차 |', '| — | 명제 | 두 장부의 차(2026-11-17 구조 압축 K6·V1로 뺌 — 견줄 상대가 사라짐) |  | 뺌 | (10:regen-vs-ledger) |'),
]
ops5 = [('del_row', '| 9 |')]
ops6 = [
    ('sub', '| $\\Sigma$(기호 이름으로) |', ', 9.5의 창 합은 국소 $\\mathfrak S$ |', ' |'),
    ('sub', '| $\\theta^\\prime$ |', '(증명 국소로만 9.5절 한 변수 확인의 $\\mathfrak j$, 8.4절 보조정리 `{{8:hazard-H1}}` 증명의 $\\mathfrak z$ — 1.3의 9.5·8.4 묶음)', '(증명 국소로만 8.4절 보조정리 `{{8:hazard-H1}}` 증명의 $\\mathfrak z$ — 1.3의 8.4 묶음)'),
    ('sub', '| $\\mathrm{Src}$, $\\mathrm{Pair}$,', '$\\mathrm{Src}$, $\\mathrm{Pair}$, $\\mathrm{CF}$, $\\mathrm{FL1}$, $\\mathrm{FLlin}$, $BT$, $D2S$, $\\mathfrak t_k$, $\\mathrm{Land}$(기록), $\\mathrm{Top}_k$(기록 [r79ee9e0])', '$\\mathrm{Src}$, $\\mathrm{CF}$, $\\mathrm{FLlin}$, $BT$, $D2S$, $\\mathrm{Top}_k$(기록 [r79ee9e0])'),
    ('sub', '| $\\mathrm{Src}$, $\\mathrm{CF}$,', '글자나 뜻에서 겹치거나($\\mathfrak t_k(t)$는 같은 바탕 글자가 안팎에 놓여 읽기 어려움)', '글자나 뜻에서 겹침'),
    ('sub', '| $\\mathrm{Src}$, $\\mathrm{CF}$,', '$\\mathfrak D^{\\mathrm{src}}_q$, $\\mathrm{Pcor}_m$, $\\mathrm{DDL}^\\natural$, $\\mathrm{FL}^{(1)}_m$, $\\mathrm{inh}^{\\mathrm{lin}}_k$, $\\mathrm{Bor}^{*j}$, $P_n(y)$, $\\mathrm{flat}_k(t)$, 국소 $\\mathrm{Ld}_n$, 1.2 전역', '$\\mathfrak D^{\\mathrm{src}}_q$, $\\mathrm{DDL}^\\natural$, $\\mathrm{inh}^{\\mathrm{lin}}_k$, $\\mathrm{Bor}^{*j}$, $P_n(y)$, 1.2 전역'),
    ('sub', '| $Q_k$([r37c204b]),', '$R_j$·$a(s)$([rc391829]), ', ''),
    ('sub', '| $Q_k$([r37c204b]),', '$\\Pi_k$(짝 합; [r29b01e8]), ', ''),
]
ops7 = [
    ('sub', '전역 양의 행만 둔다(세션 결정 26·27):', '출처 목록의 86개 기록(부록 B의 목록 — 본문·부록 D가 인용하는 83개와', '출처 목록의 75개 기록(부록 B의 목록 — 본문·부록 D가 인용하는 72개와'),
    ('sub', '| $s_m(y)$ | [r13b0b8f];', '[r8a9b11e], [r23f10e9], [r58b4caa], [rc391829]; [r39ea75d]', '[r8a9b11e], [r23f10e9], [r58b4caa]; [r39ea75d]'),
    ('sub', '| $\\Pr(X\\le x)$, $f$, $x_\\ast$ |', '; [r29c10cd]; [rc391829] | $F$, $f$, $m$; $f_X$, $m$, $m_r$; $m_f$; $x_*$; $\\mathfrak m$; $m^*$ |', '; [r29c10cd] | $F$, $f$, $m$; $f_X$, $m$, $m_r$; $m_f$; $x_*$; $\\mathfrak m$ |'),
    ('ins_after', '| $\\mathfrak a^\\circ_n$ | [rb7effe0]; [r475ada3] |', ['| $T^{\\le k}, T^{>k}$ | [r475ada3]; [ra4c01fc] | $T_{\\le k}$, $T_{>k}$; $T_c(x)$ | 아래 첨자→위 첨자(2026-11-17 U1b; 5A의 아래 첨자 표기는 W4가 통일); 첨자 용량 $c\\to k$ |']),
    ('sub', '| $\\mathrm{Bor}^{*j}(m)$ | [r8a9b11e]; [r5909c9e];', '[r8a9b11e]; [r5909c9e]; [re71a735]; [r58b4caa] | $BT(z,D)$; $B^{(*n)}(\\ell)$; $BT_n(j)$; $BT_j(J)$(누적)', '[r8a9b11e]; [re71a735]; [r58b4caa] | $BT(z,D)$; $BT_n(j)$; $BT_j(J)$(누적)'),
    ('sub', '| $\\Psi(q)$ | [r5bbc534], [r9bf2dc6], [r2ec875c];', '; [r030ffae], [r5909c9e]; [r4868e30]', '; [r030ffae]; [r4868e30]'),
    ('sub', '| $\\mathrm{Bor}_\\le(q)$ | [r030ffae];', '[r030ffae]; [r5909c9e]; [r5bbc534]; [r29c10cd] | $S_0(b)$; $S_0(\\nu)$; $S_0(d)$; $\\beta(m)$', '[r030ffae]; [r5bbc534]; [r29c10cd] | $S_0(b)$; $S_0(d)$; $\\beta(m)$'),
    ('sub', '| $\\pi^0_n(y)$ | [r29c10cd];', '; [rc391829]; [r030ffae];', '; [r030ffae];'),
    ('sub', '| $\\pi^0_n(y)$ | [r29c10cd];', '$\\mathcal N(F,Y)$; $\\mathcal N(s,v+1)$; $\\pi^0_{N^\\prime}(k-1)$', '$\\mathcal N(F,Y)$; $\\pi^0_{N^\\prime}(k-1)$'),
    ('sub', '| $\\pi^0_n(y)$ | [r29c10cd];', '; [rae1f209], [r5909c9e]; [r2fe0259]; [r39ea75d] |', '; [rae1f209]; [r39ea75d] |'),
    ('sub', '| $\\pi^0_n(y)$ | [r29c10cd];', '; $P_0(N)$(인수 $k$); $q_F=\\pi^0_F(\\lfloor F/2\\rfloor)$; $f_N(y)=p_N\\pi^0_N(y)$ |', '; $P_0(N)$(인수 $k$); $f_N(y)=p_N\\pi^0_N(y)$ |'),
    ('sub', '| $\\mathrm{Bor}(N+1-r)/\\mathrm{Bor}(N+1)$($\\mathrm{tilt}$ 꼴; 글자 없음) |', '[r030ffae]; [r5bbc534]; [rc391829] | $\\rho_h$, $\\rho_j$; $\\omega_N(r)$; $R_j=\\mathrm{Bor}(F+1-j)/\\mathrm{Bor}(F+1)$', '[r030ffae]; [r5bbc534] | $\\rho_h$, $\\rho_j$; $\\omega_N(r)$'),
    ('del_row', '| $\\mathrm{dec}_N$ | [r051bfe1];'),
    ('del_row', '| $\\varphi^\\flat_k$, $\\Upsilon_k$ | [r29b01e8] |'),
    ('sub', '| $c_m(m-d)$ | [r29b01e8],', '[r29b01e8], [r2ec875c], [r23f10e9]', '[r2ec875c], [r23f10e9]'),
    ('set_row', '| $P_n(y)$ | [r29b01e8],', '| $P_n(y)$ | [r23f10e9], [r58b4caa] | $D2S_n(y)=\\sum_{t=y}^nx_t(y)$ | 글자(Q14) |'),
    ('sub', '| $\\xi$ | [re71a735] §4;', '[re71a735] §4; [r5909c9e]; [r030ffae]; [rfc69320]; [r9bf2dc6] | $x=\\delta/y^{2/3}$; $y=b/k^{2/3}$; $x_b$, $x$;', '[re71a735] §4; [r030ffae]; [rfc69320]; [r9bf2dc6] | $x=\\delta/y^{2/3}$; $x_b$, $x$;'),
    ('sub', '| $\\mathcal N_\\ell(t)$ | [r4868e30];', '[r4868e30]; [r5909c9e]; [rcb2e2d4]; [r05cf8c9] | $c_N(\\kappa)=\\min(N,\\kappa)A_{N-1,\\kappa-1}$; $T_\\ell(s)$; $\\mathcal T_\\ell(s)$; $t_s(c)$', '[r4868e30]; [rcb2e2d4]; [r05cf8c9] | $c_N(\\kappa)=\\min(N,\\kappa)A_{N-1,\\kappa-1}$; $\\mathcal T_\\ell(s)$; $t_s(c)$'),
    ('sub', '| $x_t(k)$, $\\delta_t$ | [r4868e30];', '[r4868e30]; [rcb2e2d4]; [r05cf8c9]; [rc391829] | $x_N(k)$; $\\hat\\delta_s$, $\\delta_s$; $\\delta_s$; $V_{s-1}$ | $N,s\\to t$; $V_{s-1}=\\delta_s$(첨자 한 칸)', '[r4868e30]; [rcb2e2d4]; [r05cf8c9] | $x_N(k)$; $\\hat\\delta_s$, $\\delta_s$; $\\delta_s$ | $N,s\\to t$'),
    ('sub', '| $\\mathfrak w_n(t)$, $\\tilde{\\mathfrak w}_n(t)$ | [r4868e30];', '; [r33475a7]; [rc391829] | $\\varpi_n(N)$; $\\varpi_n(s)$; $\\mathcal T_n(t)$, $\\tilde\\pi_n(t)$; $\\tilde\\pi_n(s)$ |', '; [r33475a7] | $\\varpi_n(N)$; $\\varpi_n(s)$; $\\mathcal T_n(t)$, $\\tilde\\pi_n(t)$ |'),
    ('sub', '| $c_m(Y)$(6·7장 기록) |', '[rae1f209], [r030ffae]; [r5909c9e]; [r77e234e], [rae1f209] | $\\pi_m(\\ell)$; $q_m=\\Pr_m(M=k-1)$, $q^+_m$; $r_N$, $r^\\prime_N$; $c^\\pm_m$; $f_N=f_k=c_N(k-1)$ | 글자; 인수 명시; [r2ec875c]는 $c_m(\\ell)$(같은 글자; 9장 기록 행)', '[rae1f209], [r030ffae]; [r77e234e], [rae1f209] | $\\pi_m(\\ell)$; $q_m=\\Pr_m(M=k-1)$, $q^+_m$; $r_N$, $r^\\prime_N$; $f_N=f_k=c_N(k-1)$ | 글자; 인수 명시; [r2ec875c]는 $c_m(\\ell)$(같은 글자; 아래 [r2ec875c] 행)'),
    ('sub', '| $\\mathrm{rb}_m$ | [r5909c9e], [rae1f209];', '[r5909c9e], [rae1f209]; [r5bbc534]', '[rae1f209]; [r5bbc534]'),
    ('set_row', '| $x_\\ast$ | [r29c10cd]; [rc391829] |', '| $x_\\ast$ | [r29c10cd] | $\\mathfrak m=0.5996\\ldots$ | 글자 |'),
    ('set_row', '| $Z_c(F)$, $Z_w(F)$ |', '| $Z_c(F)$, $Z_y(F)$ | [r9bf2dc6]; [r2ec875c] | $\\mathfrak h_d=\\#\\{v:s_v\\ge c+1\\}$; $Z=\\lvert\\{w:s_w\\ge v+1\\}\\rvert$ | 글자; 문턱 $c$, $v$([r2ec875c]의 문턱 $v$는 1.1 용량 변수 $y$의 자리 — 보조정리 `{{2:level-mass-jensen}}`(가)가 $Z_y(F)$로 쓴다; 꼭짓점 지표 $w\\to v$) |'),
    ('del_row', '| $\\mathrm{lp}_k$, $\\mathrm{lpr}_k$ | [rf451d83], [rb7effe0], [r89eb039]; [rf451d83] |'),
    ('set_row', '| $\\mathrm{tail}_s(y)$, $t_0(y)$, $x_t(y)$, $\\mathrm{IH}(n,y)$ |', '| $\\mathrm{tail}_s(y)$, $t_0(y)$, $x_t(y)$, $\\mathrm{IH}(n,y)$ | [r58b4caa], [r8a9b11e], [r23f10e9] | $\\mathcal T_s(y)=\\sum_{t=s+1}^nx_t(y)$, $t_0(y)$, $x_t(y)$, $H(n,y)$ | 글자(첨자 $s$는 같음); 없음(확인); 글자 |'),
    ('sub', '| $\\Omega(\\xi)$, $\\Omega_q$ | [r030ffae], [r5909c9e] |', '[r030ffae], [r5909c9e] | $W$(감소 함수 $[0,X]\\to[0,1]$), $W_c=W(x_c)$ | 없음(확인); $y$·$x_b$는 변수($\\xi$); 첨자 $c\\to q$', '[r030ffae] | $W$(감소 함수 $[0,X]\\to[0,1]$), $W_c=W(x_c)$ | 없음(확인); $x_b$는 변수($\\xi$); 첨자 $c\\to q$'),
    ('set_row', '| $\\Psi^{\\mathrm{low}}_{(\\varrho)}$, $\\mathsf c_\\Psi$ |', '| $\\Psi^{\\mathrm{low}}_{(\\varkappa)}$, $\\mathsf c_\\Psi$ | [r030ffae]; [rfc69320] | $\\Psi_{(r)}=C_2(2\\sqrt r+\\zeta(\\frac12)-\\zeta(\\frac32)/12+(2\\sqrt r)^{-1}-r^{-3/2}/24)$; $\\Psi_\\flat(r)$, $C_\\Psi=1.6780525$ | 글자(실수 인수 정밀판; 인수 글자 $r\\to\\varkappa$; 정의 절 2.9 — 보조정리 `{{2:power-sum-renewal}}`(ㄴ)); 상수는 산세리프 명명 상수 |'),
    ('del_row', '| $\\mathfrak B_N$, $\\mathfrak B^{\\mathrm{low}}(k,\\nu)$ |'),
    ('sub', '| $\\pi_n(m)$(8장 기록) |', '[r8456f59], [r5909c9e], [rae1f209] | $\\varpi_L(s)$, $\\varpi_n(s)$; $\\pi_N(m)$, $\\varpi_N(g)$, $\\varpi_N(s)$', '[r8456f59], [rae1f209] | $\\varpi_L(s)$, $\\varpi_n(s)$; $\\pi_N(m)$, $\\varpi_N(s)$'),
    ('sub', '| $\\mathrm{km}_N$ | [r8456f59]; [r030ffae] |', '글자(새 전역 글자; 로마체 이름 — 당시 9.3의 $\\mathfrak K_N$(2026-11-15 5차 1절 1항으로 뺀 글자)과 장식만으로 가르지 않기 위해; 재대조 표 3); 용량 $k\\to k+1$', '글자(새 전역 글자; 로마체 이름 — 재대조 표 3); 용량 $k\\to k+1$'),
    ('del_row', '| $\\mathrm{merge}^{\\mathrm{up}}$, $A^{(t)}_N$,'),
    ('del_row', '| $\\gamma_m$, $K_n(m)$, $\\mathcal Q_m$, $\\mathcal C_n$ |'),
    ('del_row', '| $\\mathrm{OB}_m$, $\\mathrm{FL}^{(1)}_m$,'),
    ('sub', '| $b^T_{t,k}/p_{t-1}$, $b^T_{t,k-1}/p_{t-1}$(글자 없음) |', '| [rae1f209], [r5909c9e] | $\\tilde u_s=u_s/p_{s-1}=q_{s-1}+kr_{s-1}$, $\\tilde v_s=v_s/p_{s-1}$; $C^+_s$, $C^-_s$ |', '| [rae1f209] | $\\tilde u_s=u_s/p_{s-1}=q_{s-1}+kr_{s-1}$, $\\tilde v_s=v_s/p_{s-1}$ |'),
    ('del_row', '| $\\pi_n(t_1,t_2)$, $\\pi_2(t)$ |'),
    ('del_row', '| $\\mathrm{rb}_m$, $\\mathrm{Bor}_\\le(\\nu)$, $\\mathrm{Bor}^{*n}(\\ell)$ |'),
    ('set_row', '| $c_m(\\ell)$, $\\mathrm{Bor}(n)$, $\\mathrm{Ren}(r)$, $\\Psi(d)$, $Z_w(F)$, $t_v$ |', '| $c_m(\\ell)$, $\\mathrm{Bor}(n)$, $\\mathrm{Ren}(r)$, $\\Psi(d)$, $Z_y(F)$, $t_v$ | [r2ec875c] | $c_m(\\ell)=b_{m,\\ell}/p_m$, $\\beta_n=u(n)/n$, $u(r)$, $\\Psi(d)$, $Z=\\lvert\\{w:s_w\\ge v+1\\}\\rvert$, $s_w$ | 없음(확인); 꼭짓점 지표 $w\\to v$($s_w=t_v$), 문턱 $v$는 용량 변수 $y$의 자리(보조정리 `{{2:level-mass-jensen}}`(가)); 숲 크기 $L\\to m$ |'),
    ('del_row', '| $\\mathfrak w_n(S_k)/\\mathfrak w_n(k)$(글자 없음) |'),
    ('del_row', '| $P_t(k)$, $P^+_t(k)$, $\\mathrm{flat}_k(t)$,'),
    ('set_row', '| $\\mathrm{PAIR}_n$, $\\mathrm{PAIR}_n/p_n$ |', '| $\\mathrm{PAIR}_n$ | [rb6a2cd0], [r05cf8c9] | $\\mathcal X_n$($2k+1\\le n\\le3k-1$에서 $=\\mathrm{PAIR}_n$) | 범위 명시 |'),
    ('ins_after', '| $\\mathrm{PAIR}_n$ | [rb6a2cd0], [r05cf8c9] |', ['| 교차항(정리 `{{2:tree-expansion}}`(가)의 두 합; 글자 없음) | [r2e22726]; [r05cf8c9] | 항등식 (3.1)의 두 나머지(글자 없음); $\\mathcal X_n$ | 글자 없이 풀어 적음; [r05cf8c9]의 $\\mathcal X_n$은 위 $\\mathrm{PAIR}_n$ 행 |']),
    ('del_row', '| $\\mathcal O_n$ | [r05cf8c9]; [r2e22726] |'),
    ('del_row', '| $\\mathrm{flat}_k(s+1)$, $\\pi^0_s(v+1)$,'),
    ('del_row', '| $\\mathrm{regen}_n$, $\\mathsf{FS}(n)$ |'),
    ('set_row', '| $A_{n,c-1}$, $T_{c-1}(x)$, $\\mathcal N_{c-1}(t)$,', '| $A_{n,c-1}$, $T_{c-1}(x)$, $\\mathcal N_{c-1}(t)$, $A_{c-1}(x)$, $\\mathcal B_k(x)$, $\\mathcal B_{k-1}(x)$, $\\delta_t$ | [r05cf8c9] | $\\mathcal A_n(c)$, $T_c(z)$, $t_s(c)$, $F_c=\\exp T_c$, $a$, $b$, $\\delta_s$ | 첨자 용량→수준; $s\\to t$ |'),
    ('set_row', '| $\\mathcal Y_k(n)$, $\\mathcal Y^{\\mathrm{LP}}_k(n)$,', '| $\\theta_t(k)$ | [rb6a2cd0] | $\\theta_N(k)$ | $N\\to t$ |'),
    ('set_row', '| $\\varrho_t$, $\\varrho^{\\mathrm H}$, $\\varrho^{\\mathrm L}$, $\\varrho_{\\min}$, $\\mathfrak r_N$,', '| $\\mathfrak r_N$, $\\mathrm{hz}_k(N)$, $s_N(k)$, $\\mathsf u(k)$, $g(x)$ | [rb6a2cd0] | $r_N$, $h_k(N)$, $\\mathfrak s_N$, $\\tilde g(k)$, $g(j)$ | 없음(확인) |'),
    ('set_row', '| $s_N(k)$, $s_N(k+1)$, $s_N(k-1)$ |', '| $s_N(k)$, $s_N(k+1)$, $s_N(k-1)$ | [rae1f209], [r030ffae] | $s_N=\\Pr_N(M\\le k-1)$, $q_N=\\Pr_N(M\\le k)$, $t_N=\\Pr_N(M\\le k-2)$ (L25; L42·223) | 용량 인수 명시(수준 $k-1$, $k$, $k-2$ → 용량 $k$, $k+1$, $k-1$) |'),
    ('del_row', '| $\\pi^0_F(\\lfloor F/2\\rfloor)$ |'),
    ('del_row', '| $\\Theta^\\circ_n$, $K_n(m)$, $\\gamma_m$, $\\mathcal Q_m$ |'),
    ('set_row', '| $\\mathcal H_{\\mathrm B}(q)$, $\\mathrm{Ren}(j)$, $\\mathrm{Bor}(j)$, $\\mathrm{Bor}^{*j}(m)$ |', '| $\\mathrm{Ren}(j)$, $\\mathrm{Bor}(j)$, $\\mathrm{Bor}^{*j}(m)$ | [r6a8c8b6] §6 | $c_h=h\\beta_h=\\sum_{j\\ge1}\\beta^{*j}(h)$, $\\beta_h$, $\\beta^{*j}(h)$ | 글자(첨자→인수); 글자만 다름; 글자만 다름 |'),
]
ops8 = [
    ('sub', '1. 정의 전 사용 0:', '(7.8절의 $\\mathsf B^+$·$\\mathsf{FLQ}$ — 명제 `{{9:old-7-6}}`·정리 `{{10:old-8-37}}`;', '(7.8절의 $\\mathsf Q^\\star_2$ — 정의 `{{10:old-8-1}}`·정리 `{{10:old-8-37}}`;'),
]

if __name__ == '__main__':
    dry = '--dry' in sys.argv
    transform_sec4(dry)
    apply(LEDGER, ops4, dry=dry, region=('## 4. ', '## 5. '))
    apply(LEDGER, ops5, dry=dry, region=('## 5. ', '## 6. '))
    apply(LEDGER, ops6, dry=dry, region=('## 6. ', '## 7. '))
    apply(LEDGER, ops7, dry=dry, region=('## 7. ', '## 8. '))
    apply(LEDGER, ops8, dry=dry, region=('## 8. ', None))
