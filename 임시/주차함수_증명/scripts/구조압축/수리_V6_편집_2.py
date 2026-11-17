# -*- coding: utf-8 -*-
# 수리 V6 — 장부_v2.md 1.3절(국소 기호)의 손 편집 목록.
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from 수리_U17_편집 import apply
LEDGER = os.path.join(HERE, '..', '..', '장부_v2.md')

ops = [
    # 9장 묶음 넷(9.1 / 9.3 / 9.2·9.4 / 9.5) 삭제
    ('del_row', '| 9.1 머리 합 조건의 양('),
    ('del_row', r'| $j_\ast=\lceil(3k)^{2/3}\rceil$('),
    ('del_row', '| (S)의 양: '),
    ('del_row', r'| $\mathfrak j=\nu/k$('),
    # 10.1 묶음 — 명제 regen-vs-ledger와 $\mathrm{lk}_{n,m}$ 소멸(V1)
    ('sub', r'| $\mathfrak g^{\mathrm L}_m=', r'$\mathrm{lk}_{n,m}$(1.2 — 명제 `{{10:regen-vs-ledger}}`의 진술 글자); ', ''),
    ('sub', r'| $\mathfrak g^{\mathrm L}_m=', '(장부 항등식·두 장부의 차·분할 무게·꼬리합 꼴)', '(장부 항등식·분할 무게·꼬리합 꼴)'),
    ('sub', r'| $\mathfrak g^{\mathrm L}_m=', r'`{{10:old-8-3}}`·`{{10:regen-vs-ledger}}`·`{{10:old-8-6}}`', r'`{{10:old-8-3}}`·`{{10:old-8-6}}`'),
    # 2장 일반 진술의 소비처 서술
    ('sub', r'| $\mathrm{wgt}\ge0$', '5B·8·9·10장이 인용', '5B·8·10장이 인용'),
    ('sub', r'| $\varkappa\ge1$', '— 8·9장이 인용;', '— 8장이 인용;'),
    # 5.5.7 묶음 — 9.1 셈법 서술 삭제; 결정 47로 5B 증명 국소 $\mathfrak l$ → $\mathfrak k$(W4 물음에 대한 V6 판단; 인계 「W4」)
    ('sub', '| $S_0=m+1$', r' — 정리 `{{5:old-5-33}}` 증명; 9.1절 정리 `{{9:theorem-A-plus}}` 증명의 $S_0:=m+1$과 같은 셈법; 1차·2차 $\sigma_0$', r' — 정리 `{{5:old-5-33}}` 증명; 1차·2차 $\sigma_0$'),
    ('sub', '| $S_0=m+1$', r'$\mathfrak l$(착지 크기; 기록 $s$)', r'$\mathfrak k$(착지 크기; 기록 $s$; 2차 $\mathfrak l$ — 5.4절 보조정리 `{{5:cut-rep}}`(라) 진술 글자 $\mathfrak l_m$과 (바탕 글자, 글자체)가 같아 결정 47로 바꿈, 2026-11-17 V6·W4)'),
    # 5.4 묶음 — $T_{\le k}$ 통일(W4), 5.5 묶음 — joining-width 재서술(W4)
    ('sub', r'| $j+\frac32$(포락선 지수', r', $T_{\le k}$(1.2 $T(x)$의 절단 변형; 기록 $T_c(x)$; 부록 D.exact-n20000 (ㄱ)도 씀 — 2.7 전역 $T^{\le k}$와 같은 양을 아래 첨자로 적은 것이라 통일은 5A 몫; 2026-11-17 U17 인계)', r', $T^{\le k}$(2.7 전역 — 1.2; 기록 $T_c(x)$; 부록 D.exact-n20000 (ㄱ)도 씀 — 2026-11-17 W4가 아래 첨자 $T_{\le k}$를 2.7의 글자로 통일)'),
    ('sub', r'| $\mathfrak c_1$(창 항 상계의 상수', r'$\mu$, $u$, $x$, $\xi$, $m_1$, $v$, $a$, $w$(보조정리 `{{5:joining-width}}` 증명 국소 — $\mu\ge597$은 5.2.2의 $\mathfrak m$ 값; $x$는 2.9 전역 $x_t(y)$·1장 전역 $x$의 바탕 글자, $a$는 6절 예약 글자, $\mu$는 1.2 측도 글자 — 증명 국소라 허용되나 가르기는 5B 몫, 2026-11-17 U17 인계)', r'$\xi$(더미), $m_1$, $v$, $w$(보조정리 `{{5:joining-width}}` 증명 국소 — 2026-11-17 W4의 재서술 뒤의 글자)'),
    # 6.4 묶음 둘 — `6:D-bound`·`6:pair-rearrange` 소멸(V2), 식 번호 (6.27)→(6.26), $\vartheta_\xi$→$\mathrm{tie}_\xi$(W5)
    ('sub', r'| $\mathcal N=\lfloor0.35k\rfloor$', '구간 평균 부등식 (6.27)', '구간 평균 부등식 (6.26)'),
    ('sub', r'| $\mathcal N=\lfloor0.35k\rfloor$', r'; $\mathfrak P^{\mathrm{pair}}_k$(짝 합; 기록 [r29b01e8] L146 $\Pi_k$; 2차–물결 2에는 6.5 묶음에도 있었으나 정리 U 소멸로 6.4에만 — 2026-11-17 구조 압축 U10)', ''),
    ('sub', '| 얼린 법칙과 $h$-변환의 양', r'$\mathfrak P^{\mathrm{pair}}_k$(6.4에만)', r'$\mathfrak P^{\mathrm{pair}}_k$'),
    ('sub', r'| $\mathcal N=\lfloor0.35k\rfloor$', r'`{{6:old-8-12}}`, `{{6:D-bound}}` |', r'`{{6:old-8-12}}` |'),
    ('sub', '| 첫 층의 대각선 하계 정리와 따름정리 L의 양', r', $\Pi_k$(짝 합, [r29b01e8] L146)는 6.5 묶음의 $\mathfrak P^{\mathrm{pair}}_k$', ''),
    ('sub', '| 첫 층의 대각선 하계 정리와 따름정리 L의 양', r', $\alpha_m(d)=(v+1)\rho_{m+1}(d)/(v\rho_m(d))-1$(대각선 상대 증분)은 10.2의 $\mathfrak a^{\mathrm S}_m$과 다른 국소 양', ''),
    ('sub', '| 첫 층의 대각선 하계 정리와 따름정리 L의 양', '첫 층 (Diag) 정리와 경로 이동 재배열 전개의 국소 양들(기록 [r696d62c] §1.2–2.1 L39–65, §2.6 L109, §5.2 L355–377; [r29b01e8] §4.1 L159, §4.4 L191–193)', '첫 층 (Diag) 정리 전개의 국소 양들(기록 [r696d62c] §1.2–2.1 L39–65, §2.6 L109, §5.2 L355–377)'),
    ('sub', '| 첫 층의 대각선 하계 정리와 따름정리 L의 양', '; (4.1) 재배열의 양; ', '; '),
    ('sub', '| 첫 층의 대각선 하계 정리와 따름정리 L의 양', r' | 6.4 `{{6:diag-first-layer}}`, `{{6:cor-L}}`, `{{6:pair-rearrange}}` | ', r' | 6.4 `{{6:diag-first-layer}}`, `{{6:cor-L}}` | '),
    ('sub', '| 첫 층의 대각선 하계 정리와 따름정리 L의 양', r'; [r29b01e8] $\delta_A$, $G_{AJ}$, $KA$, $KAA$(참조만), $\Pi_k$, $\alpha_m(d)$, $\varphi^\flat_k$(L35), (Diag), $\rho_m(d)$, $D2S_n(y)$ ‖ (ㄱ) 바꿔야 할 기록 글자(스크립트 셈): $Q^\natural_B$, $\delta_A$, $G_{AJ}$ |', r' ‖ (ㄱ) 바꿔야 할 기록 글자(스크립트 셈): $Q^\natural_B$ |'),
    ('sub', '| 첫 층의 대각선 하계 정리와 따름정리 L의 양', r'$\vartheta_\xi(\cdot)$', r'$\mathrm{tie}_\xi(y)$(동률 몫; 로마체 약기 — 2026-11-17 W5가 $\vartheta_\xi$에서 바꿈)'),
    # 6.5 묶음 — 식 번호(V2)
    ('sub', '| 얼린 법칙과 $h$-변환의 양', r'(6.37) 수준별 공식, (6.38) $\mathrm{Res}_d$ 식', r'(6.35) 수준별 공식, (6.36) $\mathrm{Res}_d$ 식'),
    # 7.3 묶음 — $\mathcal Y_k$ 괄호(W6), 11.3절 호출(V5), $\mathrm{lp}_k$ 국소로(V5·V6)
    ('sub', '| 7.3의 양', r'$\mathcal Y_k$(표시 생성함수; 옛 $\mathcal Y_z$의 $z=k$ 판 — 9.4 전역 $\mathcal Y_k(n)$과 바탕 글자가 같으나 7장에 그 전역이 없어 R1′ 허용)', r'$\mathcal Y_k$(표시 생성함수; 옛 $\mathcal Y_z$의 $z=k$ 판)'),
    ('sub', '| 7.3의 양', r'2차 $\varsigma_{\mathrm L},\varsigma_{\mathrm U}$ — 15차 G6; 11.3절 표도 부른다)', r'2차 $\varsigma_{\mathrm L},\varsigma_{\mathrm U}$ — 15차 G6)'),
    ('sub', '| 7.3의 양', r'$\mathrm{lp}_k$(1.2; 7.3절 준비 문단이 정의)', r'$\mathrm{lp}_k:=k\log(e\rho_k)$, $\mathrm{lpr}_k:=\mathrm{lp}_k/k$(극의 로그와 그 비율 — 7.3절 준비 문단이 정의; 2차 $\varsigma_k$·$\gamma_k$ — 6.3 전역 $\varsigma_m(\ell)$과 바탕 글자가 같아 2026-11-16 15차 F6-5·G6가 로마체 이름으로; 절 밖 호출이 부록 D.{{D:column-certificates-501-2000}}뿐이라 R1′대로 1.2 전역에서 이 묶음으로 — 2026-11-17 V6; 기록 $\sigma_k$ ([rf451d83], [rb7effe0], [r89eb039]), $\tau_k=\sigma_k/k$ ([rf451d83]))'),
    # 7.7 묶음 — `7:old-6-22`·$\mathsf{LRP}_2$ 소멸(V3), $\Pi^{\mathrm{up}}_j$는 10.4 전역(V1)
    ('sub', r'| $\mathsf r^{\mathrm{thr}}_k=', r'옛 상수 1.3502·$\Pi^{\mathrm{up}}_j$·$j_0=\lfloor0.3k\rfloor$는 소멸)', r'옛 상수 1.3502·$j_0=\lfloor0.3k\rfloor$는 소멸; $\Pi^{\mathrm{up}}_j$는 10.4절의 전역 글자로 남는다 — 1.2)'),
    ('sub', r'| $\mathsf r^{\mathrm{thr}}_k=', r'; $\mathcal R_2$, $\mathsf{LRP}_2$(1.2; 정리 `{{7:old-6-22}}` — $k\ge6668$, $\max(2k+103,20001)\le n\le3k-1$)', r'; $\mathcal R_2$(1.2; 7.8절 「남은 것」이 정의 — $k\ge6668$, $\max(2k+103,20001)\le n\le3k-1$)'),
    ('sub', r'| $\mathsf r^{\mathrm{thr}}_k=', '둘째 층의 한 걸음 항등식과 주 정리·둘째 층 한 칸 비교의 동치 증명의 국소 양들(7.7절;', '둘째 층의 한 걸음 항등식 증명의 국소 양들(7.7절;'),
    ('sub', r'| $\mathsf r^{\mathrm{thr}}_k=', r'`{{7:old-6-21}}`, `{{7:old-6-22}}` 진술과 증명, 7.7절 준비 문단 |', r'`{{7:old-6-21}}` 진술과 증명, 7.7절 준비 문단, 7.8절 |'),
    # 8.1–8.2 묶음 — $\varrho_j$ 구별 괄호(6.2 전역 $\varrho_t$ 소멸)
    ('sub', '| 8.1–8.2의 양', r'$\varrho_j$(Borel 비; 기록 $\rho_j$; 6.2 전역 $\varrho_t$(6·9·11장)와 바탕 글자가 같은 다른 양 — 8장에 그 전역이 없어 R1′로 허용, 2026-11-16 16차 E8 5절·I8·IL)', r'$\varrho_j$(Borel 비; 기록 $\rho_j$)'),
    # 8.4 묶음 — 둘째 문턱 소멸(V3)
    ('sub', '| $6600$(기록의 $k_0$; 수로)', r'중앙 창 좌표 $\zeta$는 그 정리가 정리 `{{8:old-6-33}}`의 둘째 문턱($103\le\nu\le3.6k^{2/3}$에서 $\mathrm{LB}^{\mathrm{low}}\ge1.05$)으로 흡수되며 2026-11-17 구조 압축 K4·U9로 소멸)', r'중앙 창 좌표 $\zeta$는 2026-11-17 구조 압축 K4·U9로 소멸)'),
    # 7장 부록 D 묶음 — $\mathrm{Lip}$(W9), $\mathrm{lp}_k$ 귀속
    ('sub', '| 7장 부록 D의 국소 글자', r'$\mathrm{Lip}$(원 위 도함수 상계), ', ''),
    ('sub', '| 7장 부록 D의 국소 글자', r'와 1.2 $n^{\mathrm G}_k$·$\mathfrak a^\circ_m$·$\mathrm{lp}_k$는 본문의 것을 그대로 쓴다', r'와 1.2 $n^{\mathrm G}_k$·$\mathfrak a^\circ_m$, 7.3 묶음의 $\mathrm{lp}_k$는 본문의 것을 그대로 쓴다'),
    # 4.3 묶음 — 식 번호 (4.14)→(4.12)(W3 계약 변경)
    ('sub', r'| $y\in[k-1,k]$(실수 용량', '((4.14)의 두 오차', '((4.12)의 두 오차'),
    ('sub', r'| $y\in[k-1,k]$(실수 용량', '((4.14)의 오차 다항식', '((4.12)의 오차 다항식'),
]

if __name__ == '__main__':
    dry = '--dry' in sys.argv
    apply(LEDGER, ops, dry=dry, region=('### 1.3', '## 2. '))
