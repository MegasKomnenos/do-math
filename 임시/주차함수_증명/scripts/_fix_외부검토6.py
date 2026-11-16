# -*- coding: utf-8 -*-
"""외부 피드백 여섯째 묶음(미세 오탈자, 6.50(라) 상수, 7.55 오목성 문장, D.15 상수 범위, 5.61 제외, 5.70 항등식, 부록 A v(k),
문헌 인용 둘)과 이식 C의 지적(반올림 자릿수·표의 이중 반올림), 등급 상향에 따른 11.3 서술을 반영한다. 멱등.
사용: python scripts/_fix_외부검토6.py [--dry]"""
import io
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DRY = "--dry" in sys.argv

CITE_23 = (
    "정리 {{2:old-2-3}}과 따름정리 {{2:old-2-4}}의 공식은 문제의 원 논문(Celano 외, §3)의 식 (3)·(4)와 같다. "
    "그 논문은 이 셈법을 「순열을 거쳐 세기」라 부르고, $\\ell=n-1$의 경우(보통의 주차함수)는 Konheim–Weiss에서 비롯한다고 적는다."
)
CITE_211 = (
    "정리 {{2:old-2-11}}의 첫째 식은 뿌리 숲의 갈고리 길이 공식(Knuth, *The Art of Computer Programming* 3권, §5.1.4, 연습문제 20)을 "
    "확률의 말로 옮긴 것이다. 모든 $I_v$가 $0$인 라벨링이 뿌리에서 멀어질수록 라벨이 커지는 라벨링이고, 그 확률 $\\prod_v1/t_v$가 "
    "곧 그런 라벨링의 수 $n!/\\prod_vt_v$를 $n!$로 나눈 것이기 때문이다."
)

EDITS = [
    # ---- 5A: 5.22(나)
    ("장v2/장5A.md",
     r"$\mathsf o^jg^-_j\preceq\mathcal Z^{(3)}_j\preceq\mathsf o^jg^+_j$",
     r"$\mathsf o^j\mathrm{Lp}^-_j\preceq\mathcal Z^{(3)}_j\preceq\mathsf o^j\mathrm{Lp}^+_j$", 1),
    # ---- 5B: 5.72(라), 5.70
    ("장v2/장5B.md", r"\sum_{j=2}^Na^{-1/2}\le2\sqrt N-2", r"\sum_{j=2}^Nj^{-1/2}\le2\sqrt N-2", 1),
    ("장v2/장5B.md",
     r"y\mathfrak e_m((y+d)/y)^{3/2}=\frac{\mathcal N}{y(y+d)^{1/2}(y+d+1)}\le",
     r"y\mathfrak e_m((y+d)/y)^{3/2}=\frac{\mathcal N(y+d)^{1/2}}{y^{3/2}(y+d+1)}\le", 1),
    # ---- 6: 6.1(사), 6.43 치환, 6.50(라) 상수
    ("장v2/장6.md", r"\int_0^{V}I^{-1/2}(U-I)^{-5/2}dz", r"\int_0^{V}I^{-1/2}(U-I)^{-5/2}dI", 1),
    ("장v2/장6.md",
     r"$\sigma=\mathfrak A\sigma$로 바꾸면 $\int_0^qf=\mathfrak A^{-1/2}\int_0^{q/\mathfrak A}\sigma^{-3/2}\phi_{\mathcal F}=(\sqrt q/\mathfrak A)\mathcal I_{\mathcal F}(q/\mathfrak A)$다.",
     r"$\mathfrak e=\mathfrak A\sigma$로 바꾸면 $\int_0^q\mathfrak F=\mathfrak A^{-1/2}\int_0^{q/\mathfrak A}\sigma^{-3/2}\phi_{\mathcal F}(\sigma)\,d\sigma=(\sqrt q/\mathfrak A)\mathcal I_{\mathcal F}(q/\mathfrak A)$다.", 1),
    ("장v2/장6.md", r"\ge\ 0.0649\,\mathsf s_{\mathrm B}k^{-3/2}-E_3,", r"\ge\ 0.0648\,\mathsf s_{\mathrm B}k^{-3/2}-E_3,", 1),
    ("장v2/장6.md", r"둘의 차가 $0.0649$ 이상이다.", r"둘의 차가 $0.0648$ 이상이다.", 1),
    ("장v2/장6.md", r"$\mathcal U_k(m)/e\ge0.0649\,\mathsf s_{\mathrm B}k^{-3/2}-E_3$", r"$\mathcal U_k(m)/e\ge0.0648\,\mathsf s_{\mathrm B}k^{-3/2}-E_3$", 1),
    ("장v2/장6.md",
     r"$0.0649-0.0514>0$이다. 곧 $kc_{2k}(k-1)<0.0649\cdot e\cdot2^{3/2}=0.499$가 필요한 전부다.",
     r"$0.0648-0.0514>0$이다. 곧 $kc_{2k}(k-1)<0.0648\cdot e\cdot2^{3/2}=0.498$이 필요한 전부다.", 1),
    # ---- 7A: 7.22(가)·(라), Δ♯ 정의
    ("장v2/장7A.md", r"\xi^{-3/2}dx", r"\xi^{-3/2}d\xi", 4),
    ("장v2/장7A.md", r"\xi^{-5/2}dx", r"\xi^{-5/2}d\xi", 1),
    ("장v2/장7A.md", r"$e^\xi-1\le xe^\xi$", r"$e^\xi-1\le\xi e^\xi$", 1),
    ("장v2/장7A.md", r"\Delta^\sharp(x):=1-k\int_0^xE(\mathfrak f)\,d\mathfrak f", r"\Delta^\sharp(x):=1-k\int_0^x\mathrm{Ex}(\mathfrak f)\,d\mathfrak f", 1),
    # ---- 7B: 7.55 오목성
    ("장v2/장7B.md",
     r"로 오목이라 $\varepsilon$의 최댓값, 곧 $k=K_1$에서 최소이기 때문이다.",
     r"로 오목이므로 $0<\varepsilon\le K_1^{-1/2}$에서 $0$과 $\varepsilon=K_1^{-1/2}$에서의 값 가운데 작은 쪽 이상이고, 감사는 그 작은 쪽을 하계로 쓰기 때문이다.", 1),
    ("장v2/부록D_장7B.md",
     r"감사 코드가 각 $(K_1,\nu)$에서 (C1)–(C5)의 모든 상수를 정확 유리수로 평가해 최종 하계의 부호를 판정한다.",
     r"감사 코드가 각 $(K_1,\nu)$에서 (C1)–(C5)의 모든 상수를 정확 유리수로 평가해 최종 하계의 부호를 판정한다. $\mathsf b_D$ 쪽의 오목 나머지 $\varepsilon(\mathrm C_1-\mathrm D_1\varepsilon)$의 하계로는 $0$과 $\varepsilon=K_1^{-1/2}$에서의 값 가운데 작은 쪽을 쓴다.", 1),
    # ---- D.15 상수의 범위
    ("장v2/부록D_장5A.md",
     r"(하계 $0.494$, 상계 $0.438\cdot1.3$)",
     r"(코드의 하계는 $0.438$, 주 영역 $\mathrm{ag}'\le0.28$에서는 $0.49$, 상계는 $1.3$)", 1),
    # ---- 장부(부록 A) v(k)
    ("장부_v2.md",
     r"| V-핵심 상수 $0.765\ldots$와 그 성분 $\max(k+1,4000)$ |",
     r"| V-핵심의 하계 함수($k$에 증가; $\mathsf v(6667)=0.7654$)와 그 성분 $\mathsf v^\prime_k=\max(k+1,4000)$ |", 1),
    ("장부_v2.md", r"| (Q76) 상수 $\mathsf v(k)$의 값 |", r"| (Q76) 함수 $\mathsf v(k)$의 값 |", 1),
    # ---- 10장·D.46: 생략 부호 앞 자릿수(반올림이 아니라 자름), 표의 이중 반올림
    ("장v2/장10.md", r"d\rho=2.7171999\ldots,", r"d\rho=2.7171998\ldots,", 1),
    ("장v2/장10.md", r"d\rho=0.7998717\ldots,", r"d\rho=0.7998716\ldots,", 1),
    ("장v2/부록D_장10.md", r"d\rho=2.7171999\ldots,", r"d\rho=2.7171998\ldots,", 1),
    ("장v2/부록D_장10.md", r"d\rho=0.7998717\ldots", r"d\rho=0.7998716\ldots", 1),
    ("장v2/장10.md", r"$+0.236$($q_0=2$)", r"$+0.235$($q_0=2$)", 1),
    # ---- 2장 문헌 인용
    ("장v2/장2.md",
     "A_{n,\\ell}=\\sum_{\\sigma\\in\\mathfrak S_n}\\prod_{i=1}^n\\min(h_i,\\ell+1).\n$$\n\n",
     "A_{n,\\ell}=\\sum_{\\sigma\\in\\mathfrak S_n}\\prod_{i=1}^n\\min(h_i,\\ell+1).\n$$\n\n" + CITE_23 + "\n\n", 1),
    ("장v2/장2.md", "\n\n### 2.5 가장 큰 나무와 최대 나무 사슬", "\n\n" + CITE_211 + "\n\n### 2.5 가장 큰 나무와 최대 나무 사슬", 1),
    # ---- 11.4 문헌 표
    ("장v2/장11.md",
     r"| Celano 외, *Statistics on ℓ-interval parking functions*, arXiv:2507.07243 (2025) | Conjecture 6.5(문제 $\mathsf P$) | 1.3절 |",
     r"| Celano 외, *Statistics on ℓ-interval parking functions*, arXiv:2507.07243 (2025) | Conjecture 6.5(문제 $\mathsf P$); §3의 식 (3)·(4)(결과 순열을 거쳐 세기) | 1.3절; 정리 {{2:old-2-3}}, 따름정리 {{2:old-2-4}} |", 1),
    ("장v2/장11.md",
     "\n| Flajolet, Sedgewick, *Analytic Combinatorics*",
     "\n| Knuth, *The Art of Computer Programming*, vol. 3: Sorting and Searching, 2판, Addison-Wesley, 1998 | §5.1.4, 연습문제 20(뿌리 숲의 갈고리 길이 공식) | 정리 {{2:old-2-11}} |\n| Flajolet, Sedgewick, *Analytic Combinatorics*", 1),
    # ---- 11.3 산술 등급(이식 A·B·C와 D.26 상향 반영)
    ("장v2/장11.md", r"정리 {{6:theorem-U}}: 배정밀도 평가, 인증 아님", r"정리 {{6:theorem-U}}: 방향 반올림 구간", 1),
    ("장v2/장11.md", r"정리 {{6:theorem-D}}: 정확 정수·유리수, 40자리 평가, 인증 아님", r"정리 {{6:theorem-D}}: 정확 정수·유리수, 방향 반올림 구간", 1),
    ("장v2/장11.md", r"명제 {{6:v-negative}}: 40자리 평가, 인증 아님", r"명제 {{6:v-negative}}: 방향 반올림 구간", 1),
    ("장v2/장11.md", r"정리 {{9:old-7-16}}: 배정밀도 평가, 인증 아님", r"정리 {{9:old-7-16}}: 방향 반올림 구간", 1),
    ("장v2/장11.md", r"보조정리 {{9:pair-one-variable}}, 정리 {{9:old-7-43}}: 배정밀도 평가, 인증 아님", r"보조정리 {{9:pair-one-variable}}, 정리 {{9:old-7-43}}: 방향 반올림 구간", 1),
    ("장v2/장11.md", r"명제 {{10:old-8-23}}: 30자리 평가, 인증 아님", r"명제 {{10:old-8-23}}: 방향 반올림 구간", 1),
    ("장v2/장11.md", r"명제 {{10:check-na}}·{{10:check-ga}}: 배정밀도 평가, 인증 아님", r"명제 {{10:check-na}}·{{10:check-ga}}: 방향 반올림 구간", 1),
    ("장v2/장11.md",
     r"계산의 산술 등급으로 보면, 공유 입력의 계산 가운데 정리 {{6:theorem-U}}과 둘째 층 띠의 정리 {{8:old-6-28}}·{{8:old-6-29}}·{{8:old-6-33}}는 배정밀도 평가이고 명제 {{6:v-negative}}과 정리 {{6:theorem-D}}의 평가 부분은 40자리 평가여서 모두 인증 아님 등급이며, 나머지 공유 입력의 계산은 정확 정수·유리수, 방향 반올림 구간, binary64 사전 오차 해석 가운데 하나 이상의 등급이다. 첫째 증명의 고유 입력의 계산은 정확 정수·유리수 등급의 정리 {{9:head-sum-2}}과 방향 반올림 구간 등급의 정리 {{9:H-star-plus}}를 빼면 모두 배정밀도 평가이고, 둘째 증명의 고유 입력의 계산은 배정밀도 평가와 30자리 평가뿐이다. 그러므로 어느 증명도 인증 아님 등급의 계산 없이는 닫히지 않으며, 둘째 층 띠와 판정 $\mathsf V$를 받치는 인증 아님 등급의 계산에는 두 증명이 함께 기댄다.",
     r"계산의 산술 등급으로 보면, 공유 입력의 계산 가운데 둘째 층 띠의 정리 {{8:old-6-28}}·{{8:old-6-29}}·{{8:old-6-33}}만 배정밀도 평가, 곧 인증 아님 등급이고, 나머지 공유 입력의 계산은 정확 정수·유리수, 방향 반올림 구간, binary64 사전 오차 해석 가운데 하나 이상의 등급이다. 첫째 증명의 고유 입력의 계산은 띠의 닫힘(보조정리 {{9:old-7-26}}, 정리 {{9:old-7-28}}·{{9:old-7-31}}·{{9:old-7-33}})이 배정밀도 평가이고 나머지는 정확 정수·유리수나 방향 반올림 구간이며, 둘째 증명의 고유 입력의 계산은 모두 방향 반올림 구간이다. 그러므로 어느 증명도 인증 아님 등급의 계산 없이는 닫히지 않으며, 둘째 층 띠를 받치는 인증 아님 등급의 계산에는 두 증명이 함께 기댄다.", 1),
]


def main():
    texts = {}
    bad = 0
    for rel, old, new, expect in EDITS:
        p = os.path.join(ROOT, rel)
        s = texts.get(rel)
        if s is None:
            s = io.open(p, encoding="utf-8").read()
        if new in s:
            # 삽입형 편집은 new가 old를 포함하므로 먼저 본다
            print(f"{rel}: 이미 — {old[:40]!r}")
            texts[rel] = s
            continue
        n = s.count(old)
        if n == 0:
            print(f"{rel}: 원문 없음 — {old[:70]!r}")
            bad += 1
            texts[rel] = s
            continue
        if n != expect:
            print(f"{rel}: 횟수 {n}≠{expect} — {old[:60]!r}")
            bad += 1
            texts[rel] = s
            continue
        texts[rel] = s.replace(old, new)
        print(f"{rel}: {n}곳 — {old[:48]!r}")
    if bad:
        print(f"문제 {bad}건. 쓰지 않음.")
        sys.exit(1)
    if DRY:
        print("(dry) 쓰지 않음")
        return
    for rel, s in texts.items():
        io.open(os.path.join(ROOT, rel), "w", encoding="utf-8", newline="\n").write(s)
    print("기록함:", ", ".join(sorted(texts)))


if __name__ == "__main__":
    main()
