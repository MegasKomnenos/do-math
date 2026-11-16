# -*- coding: utf-8 -*-
"""외부 피드백 다섯째 묶음(기호 오타·불일치, 본문·명세 수정, 반올림) 가운데 세션이 원문으로 확인한 항목을 반영한다. 멱등.
각 치환은 기대 횟수를 적고 어긋나면 멈춘다. 줄을 한정해야 하는 치환은 LINE_EDITS로 한다."""
import io
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DRY = "--dry" in sys.argv
IV13 = "`원고_자료/세션_재계산/prop_W_thirteen/iv13.py`, `원고_자료/세션_재계산/prop_W_thirteen/iv13_out.txt`"

EDITS = [
    # ---- 3.4절 정리(봉우리의 위치) 증명 '곱의 상계': 정의되지 않은 z → t
    ("장v2/장3.md", r"\frac kz", r"\frac kt", 2),
    ("장v2/장3.md", r"\frac{k(n-t)}{zn}", r"\frac{k(n-t)}{tn}", 1),
    # ---- 글자 S의 중복: 2.12절의 길이 1 사슬 항은 정의대로 Q_{n,r,1}로 적는다
    ("장v2/장2.md", r"이다. 특히 $\mathcal S_{n,r}:=\mathcal Q_{n,r,1}$로 두면", r"이다. 특히", 1),
    ("장v2/장2.md", r"\mathcal S_{n,r}", r"\mathcal Q_{n,r,1}", 7),
    ("장부_v2.md", r"$\mathcal S_{n,r}$; ", r"", 1),
    # ---- 4.3절 보조정리(J의 보조 분해) 증명: 미분방정식의 미지함수
    ("장v2/장4.md", r"$I'=\mathcal Q_k+ye^TY$, $I(0)=0$", r"$I'=\mathcal Q_k+ye^TI$, $I(0)=0$", 1),
    # ---- 5.2절 정리(충분조건)(다) 증명: 타일 무게 곱
    ("장v2/장5A.md", r"(n)_d\prod\mathrm{ag}\prod_{\text{유색 }i}", r"(n)_d\prod_{\text{길이 }j\ge2}\mathrm{tw}_j\prod_{\text{유색 }i}", 1),
    # ---- 5.2절 보조정리(셋째 차분 비교)(마) 증명: 사슬 크기 글자와 무게 글자
    ("장v2/장5A.md", r"\frac n{S_i}", r"\frac n{\mathfrak t_i}", 4),
    ("장v2/장5A.md", r"$S_i\ge n+1-\mathfrak d_{j-1}", r"$\mathfrak t_i\ge n+1-\mathfrak d_{j-1}", 1),
    ("장v2/장5A.md", r"(라)의 $w$에 대한 $\mathrm{Fs}(\mathfrak v)$", r"(라)의 $\mathrm{ws}$에 대한 $\mathrm{Fs}(\mathfrak v)$", 1),
    ("장v2/장5A.md", r"$w$를 $\mathrm{Ren}$으로 바꾼 값", r"$\mathrm{ws}$를 $\mathrm{Ren}$으로 바꾼 값", 1),
    ("장v2/장5A.md", r"$w$를 $\mathrm{Ren}$으로 바꾸고", r"$\mathrm{ws}$를 $\mathrm{Ren}$으로 바꾸고", 1),
    # ---- 5.2절 보조정리(부호 보존 감싸기)(다): 다항식 차수 조건
    ("장v2/장5A.md", r"$-i/2$가 $0$ 이하의 정수이면 $U>-i/2$에서 $0$이며", r"$-i/2$가 $0$ 이하의 정수이면 $U>i/2$에서 $0$이며", 1),
    # ---- (마) 증명: 거짓 계수 비교 z^2 ⪯ 1
    ("장v2/장5A.md", r"계수가 음이 아닌 급수에서 $z(1+z)(1-z)^{-1}\preceq2(1-z)^{-1}$, $z^2\preceq1$이므로",
     r"계수가 음이 아닌 급수의 곱에서 $z(1+z)(1-z)^{-1}\preceq2(1-z)^{-1}$, $z^2(1-z)^{-1}\preceq(1-z)^{-1}$이므로", 1),
    # ---- 5.2절 보조정리(Cayley 비의 하계) 증명: e와 1957/720의 방향
    ("장v2/장5A.md", r"마지막 부등식은 $e<\frac{1957}{720}$과", r"마지막 부등식은 $e>\frac{1957}{720}$과", 1),
    # ---- 5.2절 보조정리(생략한 사슬 길이의 꼬리)(라) 증명: r≥598 전체의 지수 감쇠
    ("장v2/장5A.md", r"\le1.15\,r^3\,24^{-j}\le1.15\,r^3\,24^{-r}$이고, $r\ge598$에서 $\log_{10}(1.15r^3)<9$, $r\log_{10}24>825$이다. ∎",
     r"\le1.15\,r^3\,24^{-j}\le1.15\,r^3\,24^{-r}$이고, $r\mapsto r^324^{-r}$는 $r\ge1$에서 감소하며 $r=598$에서 $\log_{10}(1.15\cdot598^3)<8.4$, $598\log_{10}24>825$이므로 $r\ge598$에서 이 값은 $10^{-800}$ 미만이다. ∎", 1),
    # ---- 부록 C 글자 대응: ε_hz 행을 본문의 𝔥(k,ν)와 맞춤
    ("장부_v2.md", r"(L359; review §2.6(c) 정정: $\nu+1\to\nu$) | 사전 식 $\nu^{-1/2}$는 정정판과 일치; 출처는 [r5bbc534]가 아님",
     r"(L359) | 이 글의 $\mathfrak h(k,\nu)$ 앞 인자와 같음; 출처는 [r5bbc534]가 아님", 1),
    # ---- D.32 상수 C_h의 참값
    ("장v2/부록D_장7A.md", r"C_h:=\sqrt\pi(2/3)\Gamma(1/3)=3.1663", r"C_h:=\sqrt\pi(2/3)\Gamma(1/3)=3.1655\ldots", 1),
    # ---- 5.5절: 치환 안 된 Z → 𝔖
    ("장v2/장5B.md", r"\frac w{Z+R_j}", r"\frac w{\mathfrak S+R_j}", 1),
    ("장v2/장5B.md", r"\Bigl(\frac wZ\Bigr)^z", r"\Bigl(\frac w{\mathfrak S}\Bigr)^z", 1),
    ("장v2/장5B.md", r"\frac zZ", r"\frac z{\mathfrak S}", 4),
    ("장v2/장5B.md", r"\frac{Z}{\mathfrak i(\mathfrak i+1)}", r"\frac{\mathfrak S}{\mathfrak i(\mathfrak i+1)}", 4),
    ("장v2/장5B.md", r"\frac{1+\mathfrak r}{Z(1-\mathfrak r)^3}", r"\frac{1+\mathfrak r}{\mathfrak S(1-\mathfrak r)^3}", 1),
    # ---- 5.5.3절 사슬 전이의 합성 표기
    ("장v2/장5B.md", r"모든 합성 $(\mathrm{wt}_1,\dots,\gamma_j)$이", r"모든 합성 $(\gamma_1,\dots,\gamma_j)$이", 1),
    # ---- 5.6절 D 보정 넷째 단계: Rem_D 무게의 Gauss 인자 중복
    ("장v2/장5B.md", r"에 무게 $\upsilon^4\rho^2Q_0e^{-\eta\upsilon^2/2}e^{-\varrho^2/2}$를 곱해 $(0,\infty)\times[0,1]$ 위에서 적분한 상계이고",
     r"에 무게 $\upsilon^4\rho^2Q_0e^{-\eta\upsilon^2/2}$를 곱해 $(0,\infty)\times[0,1]$ 위에서 적분한 상계이고", 1),
    # ---- D.23 기본 적분 공식의 1/2
    ("장v2/부록D_장5B.md", r"\int_0^1\rho^{2i+1}e^{-\rho^2\upsilon^2/2}d\rho=\frac{i!}{(\upsilon^2/2)^{i+1}}\bigl(",
     r"\int_0^1\rho^{2i+1}e^{-\rho^2\upsilon^2/2}d\rho=\frac{i!}{2(\upsilon^2/2)^{i+1}}\bigl(", 1),
    # ---- D.19(무게 포락선)의 ε-항 계수와 본문의 ε-항
    ("장v2/부록D_장5B.md", r"$[0.3,1]$의 $\epsilon$-항 계수는 $\sup_{[0.3,1]}\bigl[|g_1(u)|+g_2(u)\bigr](1+u)^{-1/2}$다.",
     r"$[0.3,1]$의 $\epsilon$-항 계수는 $\sup_{[0.3,1]}|g_1(u)|(1+u)^{-1/2}$이고, $g_1$이 증가하므로 $g_1(1)/\sqrt{1.3}<5.21$로 막힌다. $\epsilon^2$-항은 $g_2(1)\epsilon^2/\sqrt{1.3}<4.8\epsilon^2$이다.", 1),
    ("장v2/장5B.md", r"$\epsilon$-항들은 $5.21\epsilon\le2.1\times10^{-4}$ 이하다.", r"$\epsilon$-항들은 $5.21\epsilon+4.8\epsilon^2\le2.1\times10^{-4}$ 이하다.", 1),
    # ---- D.18 기록 코드의 -z_{-1/2} 상수: 구간이 아니라 상계
    ("장v2/부록D_장5B.md",
     r"$-\mathsf z_{-1/2}$는 상수 구간 `[0.2078862250607212, 0.2078862250607213]`으로 둔다(이 상수 구간은 확인하는 진술의 구간 $[0.20788,0.20789]$ 안에 있다).",
     r"$-\mathsf z_{-1/2}$는 상수 $0.2078862250607$로 둔다(참값 $0.20788622497735\ldots$보다 $8\times10^{-11}$ 큰 상계이고, 쓰이는 방향은 $\mathsf z_{-1/2}\ge-0.2079$뿐이다).", 1),
    # ---- 5.5.9 조립 범위의 비: 인증된 하한으로 내림
    ("장v2/장5B.md", r"$(5.53)$의 좌변을 우변으로 나눈 비는 $1.0727$ 이상이다.", r"$(5.53)$의 좌변을 우변으로 나눈 비는 $1.0726$ 이상이다.", 1),
    ("장v2/장5B.md", r"비의 최솟값은 $\lambda\in[0.5,0.50004]$에서 $1.0727$이다.", r"비의 최솟값은 $\lambda\in[0.5,0.50004]$에서 $1.07266$으로 $1.0726$ 이상이다.", 1),
    ("장v2/부록D_장5B.md", r"좌변 하계와 우변 상계의 비가 $1.0727$ 이상이다.", r"좌변 하계와 우변 상계의 비가 $1.0726$ 이상이다.", 1),
    # ---- 5.5.6 가중 창 질량 상수: 최종 실행의 셀 수
    ("장v2/장5B.md", r"$\theta\in[0,12]$를 $3200$개 셀로 나누어", r"$\theta\in[0,12]$를 $6400$개 셀로 나누어", 1),
    # ---- 6.1절 정리 증명 (사): 변수 치환 잔재
    ("장v2/장6.md", r"\frac{3U}2\,zf(I)", r"\frac{3U}2\,I\,\mathfrak F(I)", 1),
    # ---- 6.2절 (6.12) 앞뒤: m_N → 𝔎_N
    ("장v2/장6.md", r"(1-z\,m_N)\,\mathfrak U_N", r"(1-z\,\mathfrak K_N)\,\mathfrak U_N", 1),
    ("장v2/장6.md", r"$i=N$인 항 $z\,m_N\mathfrak U_N\mathfrak U_0=z\,m_N\mathfrak U_N$만", r"$i=N$인 항 $z\,\mathfrak K_N\mathfrak U_N\mathfrak U_0=z\,\mathfrak K_N\mathfrak U_N$만", 1),
    ("장v2/장6.md", r"$N\ge k-1$이면 $m_N=k$이므로", r"$N\ge k-1$이면 $\mathfrak K_N=k$이므로", 1),
    # ---- 6.3절 보조정리(머묾 여유 보조 항) 증명: 정의되지 않은 h
    ("장v2/장6.md", r"\ge\frac32(y+1)qh(y+1+q)$이면 따라온다.", r"\ge\frac32(y+1)qV(y+1+q)$이면 따라온다.", 1),
    # ---- 6.4절: 부분나무 크기 글자
    ("장v2/장6.md", r"그 크기를 $S_i=s_{w_i}$,", r"그 크기를 $S_i=t_{w_i}$,", 1),
    # ---- 6.5절 보조정리(g의 도함수 경계): s → σ
    ("장v2/장6.md", r"s^2(\sigma+1)^2", r"\sigma^2(\sigma+1)^2", 3),
    ("장v2/장6.md", r"\frac1{s(\sigma+1)}", r"\frac1{\sigma(\sigma+1)}", 2),
    # ---- 6.5절 정리(기울임 곡률) 증명: 합의 지표 글자
    ("장v2/장6.md", r"\mathfrak Zw^{-3/2}", r"\mathfrak Z\mathfrak N^{-3/2}", 2),
    ("장v2/장6.md", r"\mathfrak Z_qw^{-3/2}", r"\mathfrak Z_q\mathfrak N^{-3/2}", 1),
    ("장v2/장6.md", r"\sum_ww^{-3/2}", r"\sum_{\mathfrak N}\mathfrak N^{-3/2}", 1),
    ("장v2/장6.md", r"\sum_ww^{-1/2}", r"\sum_{\mathfrak N}\mathfrak N^{-1/2}", 1),
    # ---- 6.2절 d=2 계산의 상수
    ("장v2/장6.md", r"=\frac{0.2707(2y+2)-0.5684}{(y+1)(y+2)}>0", r"=\frac{0.1353(2y+2)-0.5684}{(y+1)(y+2)}>0", 1),
    # ---- D.26: 열세 쌍의 구간 재계산을 등급으로
    ("장v2/장6.md", r"(핵심 근처 항의 음성; 기록 [r29c10cd]의 명제 W (가)) [비형식 증명, 계산 보조(40자리 평가, 인증 아님); r29c10cd].",
     r"(핵심 근처 항의 음성; 기록 [r29c10cd]의 명제 W (가)) [비형식 증명, 계산 보조(방향 반올림 구간); r29c10cd].", 1),
    ("장v2/부록D_장6.md", r"**산술 등급.** 40자리 평가, 인증 아님. 열세 쌍 모두에서 두 변의 차가 $49$ 이상이어서 반올림 오차는 무관하다.",
     r"**산술 등급.** 방향 반올림 구간(mpmath `iv`, 소수 $40$자리; 이 글의 재계산). 기록의 계산은 40자리 평가다.", 1),
    ("장v2/부록D_장6.md", r"이 글을 쓰며 한 독립 재계산이 구간 산술(40자리)로 열세 쌍을 재계산해 모두 $\mathsf L>\mathsf R$(차 $49.7$ 이상)이고 $d=14$에서 $\mathsf L=-24.16$임을 확인했다.",
     r"이 글을 쓰며 열세 쌍을 구간 산술(40자리)로 다시 계산해 모두 $\mathsf L>\mathsf R$(차 $49.6$ 이상)이고 $d=14$에서 $\mathsf L=-24.16$임을 확인했다(" + IV13 + ").", 1),
    # ---- 2.6절 명제(섬유는 거의 모두 단봉이 아니다)의 명시 상계: 위로 반올림
    ("장v2/장2.md", r"$n=1000$에서 $0.0657$, $n=10^4$에서 $0.0114$다.", r"$n=1000$에서 $0.0658$, $n=10^4$에서 $0.0115$다.", 1),
    ("장v2/부록D_장2.md", r"$n=1000$에서 $0.0657$, $n=10^4$에서 $0.0114$다.", r"$n=1000$에서 $0.0658$, $n=10^4$에서 $0.0115$다.", 1),
    ("장v2/부록D_장2.md", r"본문의 값은 이를 세 유효숫자로 적은 것.", r"본문의 값은 이를 위로 반올림해 세 자리로 적은 것이다.", 1),
    # ---- 7.5절 정규화 수준 질량: m=k에서 0인 쪽
    ("장v2/장7B.md", r"$m=k$에서는 $\mathrm{cl}^-_k=0$이다.", r"$m=k$에서는 $\mathrm{cl}^+_k=0$이다.", 1),
    # ---- 7.6절 보조정리 증명 끝: 𝔵 → 𝔙
    ("장v2/장7B.md", r"$\mathfrak x$는 그 뒤에서 증가하고, $\mathfrak V(\nu)=1$에서", r"$\mathfrak V$는 그 뒤에서 증가하고, $\mathfrak V(\nu)=1$에서", 1),
    # ---- 7.4절 보조정리(Hermite 계수의 ν-일반 경계) 증명: θ-단조성의 이유
    ("장v2/장7B.md", r"$\theta$에 대한 감소는 분자 $(k-\theta)$가 줄고 분모 $\mathfrak N^2$이 커지기 때문이다.",
     r"$\theta$에 대한 감소는 $\frac{d}{d\theta}\frac{k-\theta}{\mathfrak N^2}=-\frac{k+\nu+1+\theta}{\mathfrak N^3}<0$이기 때문이다($d\mathfrak N/d\theta=-1$).", 1),
    # ---- 부록 A: Stays_PM 설명의 참조 정리
    ("장부_v2.md", r"정리 `{{7:old-6-4}}`(벌크 점질량 상계)를 넣은 것", r"정리 `{{6:old-8-12}}`(벌크 점질량의 상계)를 넣은 것", 1),
    # ---- 부록 C 글자 대응: C_E의 기록 값 표기 삭제
    ("장부_v2.md", r"$C_E$(review 정정 $7.7148$)", r"$C_E$", 1),
    # ---- D.46 결과: 현재 상수의 값
    ("장v2/부록D_장10.md", r"$\mathfrak j_1=0.79985203$, $\mathfrak j_2=2.7171423$.", r"$\mathfrak j_1=0.79987169$, $\mathfrak j_2=2.7171999$.", 1),
    ("장v2/부록D_장10.md", r"(6667)=0.132371$", r"(6667)=0.132374$", 1),
    ("장v2/부록D_장10.md", r"(6668)=0.132363$", r"(6668)=0.132366$", 1),
    ("장v2/부록D_장10.md", r"(8065)=0.122328$", r"(8065)=0.122330$", 1),
    ("장v2/부록D_장10.md", r"(9551)=0.114037$", r"(9551)=0.114039$", 1),
    ("장v2/부록D_장10.md", r"(9705)=0.113282$", r"(9705)=0.113284$", 1),
    ("장v2/부록D_장10.md", r"(9949)=0.112120$", r"(9949)=0.112122$", 1),
    ("장v2/부록D_장10.md", r"(\tfrac12\log6667-1)=10.0448$", r"(\tfrac12\log6667-1)=10.0450$", 1),
    ("장v2/부록D_장10.md", r"두 적분을 다시 적분해 $\mathrm{DDL}^\natural(9705)=0.11328183$을 얻었다.", r"두 적분을 다시 적분해 $\mathrm{DDL}^\natural(9705)$를 소수 넷째 자리 $0.1133$까지 재현했다.", 1),
    ("장v2/부록D_장10.md", r"다시 계산해 $\mathrm{DDL}^\natural(9705)=0.11328183$, $\mathrm{Stays}", r"다시 계산해 $\mathrm{DDL}^\natural(9705)=0.1133$(넷째 자리까지), $\mathrm{Stays}", 1),
    # ---- D.15(임계 창 인증): 코드 상수와 참값
    ("장v2/부록D_장5A.md", r"실수축 나머지의 $\log\mathrm{et}(\frac12)\ge0.1268$은 참값 $0.126776$보다 조금 크게 적힌 오기이며 그 영향은 $e^{-1260}$ 규모다.",
     r"실수축 나머지의 $\log\mathrm{et}(\frac12)\ge0.1267$(코드는 $0.1268$; 차이는 $e^{-1260}$ 규모의 항에만 든다).", 1),
]

# 줄을 한정한 치환: (파일, 1-기반 줄 번호 확인용 부분 문자열, old, new, 기대 횟수)
LINE_EDITS = [
    ("장v2/장6.md", "(U/2+I)\\mathfrak F(I)", r"\frac{d}{dz}", r"\frac{d}{dI}", 4),
    ("장v2/장5A.md", "($\\mathfrak d'$은 남은 수열의 부분합)", r"\mathrm{dc}'_{j-1}", r"\mathfrak d'_{j-1}", 2),
    ("장v2/장5A.md", "($\\mathfrak d'$은 남은 수열의 부분합)", r"\mathrm{dc}'_{i-1}", r"\mathfrak d'_{i-1}", 1),
    ("장v2/장5A.md", "($\\mathfrak d'$은 남은 수열의 부분합)", r"\mathrm{dc}'_{i'}", r"\mathfrak d'_{i'}", 1),
]


def main():
    texts = {}
    for rel, old, new, expect in EDITS:
        p = os.path.join(ROOT, rel)
        s = texts.get(rel) or io.open(p, encoding="utf-8").read()
        n = s.count(old)
        if n == 0:
            if new and new in s:
                print(f"{rel}: 이미 반영 — {old[:40]}")
                texts[rel] = s
                continue
            print(f"{rel}: 원문 없음 — {old[:70]}")
            sys.exit(1)
        if n != expect:
            print(f"{rel}: 횟수 {n}≠{expect} — {old[:60]}")
            sys.exit(1)
        texts[rel] = s.replace(old, new)
        print(f"{rel}: {n}곳 — {old[:48]}")
    for rel, marker, old, new, expect in LINE_EDITS:
        p = os.path.join(ROOT, rel)
        s = texts.get(rel) or io.open(p, encoding="utf-8").read()
        lines = s.split("\n")
        idx = [i for i, l in enumerate(lines) if marker in l]
        if len(idx) != 1:
            print(f"{rel}: 줄 표지 {len(idx)}곳 — {marker[:40]}")
            sys.exit(1)
        n = lines[idx[0]].count(old)
        if n == 0 and new in lines[idx[0]]:
            print(f"{rel}: 이미 반영(줄 {idx[0]+1}) — {old[:40]}")
            texts[rel] = s
            continue
        if n != expect:
            print(f"{rel}: 줄 {idx[0]+1} 횟수 {n}≠{expect} — {old[:40]}")
            sys.exit(1)
        lines[idx[0]] = lines[idx[0]].replace(old, new)
        texts[rel] = "\n".join(lines)
        print(f"{rel}: 줄 {idx[0]+1} {n}곳 — {old[:40]}")
    if DRY:
        print("(dry) 쓰지 않음")
        return
    for rel, s in texts.items():
        io.open(os.path.join(ROOT, rel), "w", encoding="utf-8", newline="\n").write(s)
    print("기록함:", ", ".join(texts))


if __name__ == "__main__":
    main()
