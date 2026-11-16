# -*- coding: utf-8 -*-
"""수학 검사 2 · 7A: 장v2/장7A.md·장v2/부록D_장7A.md의 토큰 수정(멱등).
앵커가 파일 안에서 정확히 한 번 나타날 때만 치환한다. 실행: python -I scripts/수학검사2/7A_fix.py
입증은 대조v2/수학검사2/보고_7A.md 2절과 scripts/수학검사2/7A_검산_*.py의 출력."""
import io
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def apply(path, fixes):
    s = io.open(path, encoding="utf-8").read()
    orig = s
    for old, new in fixes:
        c_old, c_new = s.count(old), s.count(new)
        if c_old == 0 and c_new == 1:
            print("이미 적용됨:", new[:70]); continue
        if c_old != 1:
            print(f"앵커가 {c_old}번 나타남, 중단:", old[:70]); sys.exit(1)
        s = s.replace(old, new); print("치환:", old[:70], "->", new[:70])
    if s != orig:
        io.open(path, "w", encoding="utf-8", newline="").write(s); print("저장:", path)
    else:
        print("변경 없음:", path)

# ---- 장7A.md ----
FIXES_MAIN = [
    # [반올림 방향] 정리 self-consistent-S (다) 층 1의 𝔅_0: 정확값 0.09850429…(7A_검산_selfconsistent.py)이므로 상계 0.098504는 참값보다 작다 → 0.098505.
    (r"\mathbb E^{\sigma}_{n,k}[kH_k]\le1.4708\,k+0.098504\,n$이고",
     r"\mathbb E^{\sigma}_{n,k}[kH_k]\le1.4708\,k+0.098505\,n$이고"),
    # [반올림 방향] 표 층 1: 𝔑_J 참값 0.02499107…>0.024991 → 0.024992; 𝔅_0 0.098504 → 0.098505.
    (r"| 1 | $267/100$ | $25$ | $501$ | $82$ | $429$ | $0.024991$ | $0.749711$ | $0.736245$ | $1.4708$ | $0.098504$ |",
     r"| 1 | $267/100$ | $25$ | $501$ | $82$ | $429$ | $0.024992$ | $0.749711$ | $0.736245$ | $1.4708$ | $0.098505$ |"),
    # 따름정리 cor-S-prime 증명의 꼭짓점 조건에 든 같은 상수(0.098505로도 <0.0495 성립: 0.0494493).
    (r"(1+1/501)^2\cdot0.098504/2<0.0030+0.0495<0.13",
     r"(1+1/501)^2\cdot0.098505/2<0.0030+0.0495<0.13"),
]

# ---- 부록D_장7A.md ----
FIXES_D = [
    # [글자] 따름정리 cor-S-prime의 변수는 본문 551행·장부 1.3(396행)대로 ξ:=1/k. 7.3절의 𝔷는 반지름(>1)이므로 글자 충돌.
    (r"(2) 따름정리 {{7:cor-S-prime}}의 세 값. $\mathfrak z=1/k^{\mathrm S}_0$에서 $(\mathsf y-\mathfrak z)(\mathsf y-2\mathfrak z-\mathfrak z^2)-(1+\mathfrak z)^2(\mathfrak A_0\mathfrak z+\mathfrak B_0\mathsf y)$는",
     r"(2) 따름정리 {{7:cor-S-prime}}의 세 값. $\xi=1/k^{\mathrm S}_0$에서 $(\mathsf y-\xi)(\mathsf y-2\xi-\xi^2)-(1+\xi)^2(\mathfrak A_0\xi+\mathfrak B_0\mathsf y)$는"),
    (r"꼭짓점 조건 $(3\mathfrak z+\mathfrak z^2)/2+(1+\mathfrak z)^2\mathfrak B_0/2\le\mathsf y$가 성립한다.",
     r"꼭짓점 조건 $(3\xi+\xi^2)/2+(1+\xi)^2\mathfrak B_0/2\le\mathsf y$가 성립한다."),
    (r"(2) 따름정리의 두 식을 $\mathfrak z=1/k^{\mathrm S}_0$에서 정확 유리수로 평가한다.",
     r"(2) 따름정리의 두 식을 $\xi=1/k^{\mathrm S}_0$에서 정확 유리수로 평가한다."),
    # [반올림 방향] 층 1 상수(본문 표와 같은 수정).
    (r"$\mathfrak R_{\mathcal J}\le0.024991,0.008802,0.005691$",
     r"$\mathfrak R_{\mathcal J}\le0.024992,0.008802,0.005691$"),
    (r"$\mathfrak B_0\le0.098504,0.060259,0.0422$",
     r"$\mathfrak B_0\le0.098505,0.060259,0.0422$"),
    # ---- D.polar-blocks-488 (하위 작업자 대조 + 직접 확인) ----
    # [식↔코드] (4)[A7] 𝔮_1 상계의 상수: 코드(achain3_fixed.py 178행, achain_iv.py 262행)는 1(Σ_m Bor(m)=1에서 Σ_{m<k}(k-m)Bor(m)≤k).
    (r"\mathfrak q_1\le k[(2\pi)^{-1/2}\zeta_{3/2}+(2\pi)^{-1/2}\mathfrak Y'(q_1(\mathfrak s')+2(\mathfrak s'+1)/k)]",
     r"\mathfrak q_1\le k[1+(2\pi)^{-1/2}\mathfrak Y'(q_1(\mathfrak s')+2(\mathfrak s'+1)/k)]"),
    # [식↔코드] (4)[A8] 𝔓^U_k√k: 코드(achain3_fixed.py 204행, achain_iv.py 292행)는 (𝔰+e^{tt}J_A); 𝔍_1≤e^Ξ[𝔰+e^{tt}∫e^{-𝔅-v/k}]에서 e^{tt}가 필요.
    (r"\mathfrak P^{\mathrm U}_k\sqrt k\le(2\pi)^{-1/2}\mathfrak Y_{\mathrm{hi}}k^{-1/2}e^{\Xi^{\mathrm U}}(\mathfrak s+J_A)",
     r"\mathfrak P^{\mathrm U}_k\sqrt k\le(2\pi)^{-1/2}\mathfrak Y_{\mathrm{hi}}k^{-1/2}e^{\Xi^{\mathrm U}}(\mathfrak s+e^{\mathrm{tt}}J_A)"),
    # [반올림 방향] k=10^7 한 점의 V√k: 자료 l15_check_10000000.json chain/Vsk=0.5911731>0.591 → 0.5912.
    (r"$k\theta_a=1.251$, $V\sqrt k\le0.591$", r"$k\theta_a=1.251$, $V\sqrt k\le0.5912$"),
    # [반올림 방향] 참값 오차 상계: truth_accuracy_check.json term_rel_err/tau_max=1.5265e-14>1.5e-14 → 1.6e-14.
    (r"항별 $1.5\times10^{-14}$ 이하", r"항별 $1.6\times10^{-14}$ 이하"),
    # [수치↔자료] ψ_V 하계 비교: NEW_blocks_merged.jsonl에서 min ψ_lo/((4-2V√k_1)/k_2)=0.8655, /k_1이면 0.8485<0.86.
    (r"$\psi_V$ 하계는 $(4-2V\sqrt k)/k$의 $0.86$배 이상", r"$\psi_V$ 하계는 $(4-2V\sqrt{k_1})/k_2$의 $0.86$배 이상"),
    # [첨자] 코드의 변수: sparts.py GG(c,i,j)의 c=N=k+i이고 (6)(ㄷ)의 이름은 𝒜_N.
    (r"`GG`는 $\mathcal A_{\mathfrak c}$", r"`GG`는 $\mathcal A_N$"),
    # ---- D.xcert-partAB (하위 작업자 대조 + 직접 확인) ----
    # [거짓 부등식] (5) tl_J의 닫힌 꼴: 글의 우변/참값=0.995(υ=26), 0.928(40), 0.949(60) <1. 코드(layerA2.py 53행, layerA3.py 90행)와 기록 exposition 283행의 정정판으로.
    (r"\le2e\sqrt\upsilon e^{-\upsilon}+2.83e^{-\upsilon/2}/\upsilon+2\sqrt\upsilon e^{-3\upsilon/4}$",
     r"\le2e\sqrt\upsilon e^{-\upsilon}+e^{-\upsilon/2}(2\sqrt2/\upsilon+6\sqrt2/\upsilon^2+480/\upsilon^3)+2\sqrt\upsilon e^{-3\upsilon/4}$"),
    # [항 누락] (5)[Λ 구역 B] 원자 합 상계: max_{N≥256}[Σ n pr°_n − 2c0 e^{η257}√N]=0.1119>0이라 +0.12 없이는 거짓. 코드 layerA2.py 434행(C012=0.12, EN=e^{η_{257}}), 기록 exposition 285행.
    (r"+2(2\pi)^{-1/2}e^{-1}e^{\eta}\varsigma_{\mathrm U}e^{\varsigma_{\mathrm U}\mathfrak N_1/k}\sqrt{\mathfrak N_1}/k$",
     r"+(\varsigma_{\mathrm U}/k)e^{\varsigma_{\mathrm U}\mathfrak N_1/k}\bigl(2(2\pi)^{-1/2}e^{-1}e^{\eta_{257}}\sqrt{\mathfrak N_1}+0.12\bigr)$"),
    # [반올림 방향] (5)[Far] ca_1은 Ω(ς')≥ς'+ca_1|ς'|^{3/2}의 하계 계수: 2^{3/2}/3=0.942809<0.943. 코드 layerA2.py 42·258행은 정확값.
    (r"\mathrm{ca}_1=0.943(1+(4/3)\sqrt{2\mathfrak X_1/k})^{-3/2}k^{-1/2}",
     r"\mathrm{ca}_1=(2^{3/2}/3)(1+(4/3)\sqrt{2\mathfrak X_1/k})^{-3/2}k^{-1/2}"),
    # [첨자] 몸통은 n≥257이고 코드(layerA2.py 36행, layerA3.py 59행 ETA_N=eta(N0+1))·기록 285행은 e^{η_{257}}.
    (r"(2\pi)^{-1/2}e^{-1}e^{\eta_{256}}[2\cdot256^{-1/2}", r"(2\pi)^{-1/2}e^{-1}e^{\eta_{257}}[2\cdot256^{-1/2}"),
    (r"e^{\eta_{256}}k^{j-1/2}[", r"e^{\eta_{257}}k^{j-1/2}["),
    (r"e^{\eta_{256}}\pi\sqrt\pi/20^{3/2}", r"e^{\eta_{257}}\pi\sqrt\pi/20^{3/2}"),
    # [반올림 방향] (6) 𝔰_1은 하계로 쓰임: resA3.json s1_root_enclosure=[39.08599253547307, …075], 코드는 아래 끝.
    (r"\mathfrak s\ge\mathfrak s_1:=\varsigma_{\mathrm U}(10^{30})=39.0860$", r"\mathfrak s\ge\mathfrak s_1:=\varsigma_{\mathrm U}(10^{30})=39.0859$"),
]

apply(os.path.join(ROOT, "장v2", "장7A.md"), FIXES_MAIN)
apply(os.path.join(ROOT, "장v2", "부록D_장7A.md"), FIXES_D)
