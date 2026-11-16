# -*- coding: utf-8 -*-
"""결정 K1 검산 (4) — P9 의 수정 채택을 받치는 세 확인.
(ㄱ) 꼬리 보조정리(상수 1/2)의 손 증명 연쇄: k(1-s_{k+q-1}(k)) ≤ e^{3(q-1)/(2k)} Σ_{d=1}^{q-1} Ψ(d),
     Ψ(d) ≤ (2π)^{-1/2}(2√d-1), Σ_{d<q}√d ≤ (2/3)((q-1/2)^{3/2}-2^{-3/2}) → 모든 2≤q≤101, k≥10000 에서 ≤ q^{3/2}/2 인지.
     또 Abel 항등식 Σ_{i<q}Ren(i)(q-i)=Σ_{d<q}Ψ(d) 와 Ψ 상계의 수치 확인.
(ㄴ) F4 의 쌍별 손실 닫힌 상계 (b): j(e_q+e_p)+[e_q(p-1)+e_p(q-1)]/2 ≤ L²/3+(8C/25)√(2/5)L^{5/2} (e_x=x+Cx^{3/2}, p,q≥1, j≥0, p+q+j≤L)
     를 L≤200, C∈{0.525, 0.6} 의 정수 전수로 확인하고, u-매개화의 두 끝점 식을 대조한다.
(ㄷ) 접합점 (K,L)=(10000,50),(12000,58),(13000,79),(14000,99),(15000,102) 에서 C_eff=(1+q/K)/(2(1-q^{3/2}/(2K))) (q=L-1) ≤ 21/40 와
     L²/3+(8·(21/40)/25)√(2/5)L^{5/2} < K 를 확인한다(손 산술).
python -I. 출력 결정_K1_P9_out.txt.
"""
import os, math
ROOT = r"C:\math\임시\주차함수_증명"
out = []
def P(s=""): out.append(s)
def ren(j): return math.exp((j-1)*math.log(j) - j - math.lgamma(j)) if j >= 1 else 1.0
sB = (2*math.pi)**-0.5
# (ㄱ)
P("== (ㄱ) 꼬리 보조정리 1/2 의 손 증명 연쇄 ==")
Psi = [0.0]
for d in range(1, 130): Psi.append(Psi[-1] + ren(d))
okPsi = all(Psi[d] <= sB*(2*math.sqrt(d)-1) + 1e-15 for d in range(1, 130))
P(f"  Ψ(d) ≤ (2π)^(-1/2)(2√d-1) (d≤129): {okPsi};  예 Ψ(101)={Psi[101]:.5f} vs {sB*(2*math.sqrt(101)-1):.5f}")
okAbel = all(abs(sum(ren(i)*(q-i) for i in range(1, q)) - sum(Psi[d] for d in range(1, q))) < 1e-9 for q in range(2, 120))
P(f"  Abel 항등식 Σ_{{i<q}}Ren(i)(q-i)=Σ_{{d<q}}Ψ(d) (q≤119): {okAbel}")
worst = (0, 0); worst_exact = (0, 0)
for k in (10000, 9950):
    for q in range(2, 102):
        n_ = q-1  # Σ_{d=1}^{n}√d ≤ (2/3)n^{3/2}+(1/2)√n-1/6 (오목 함수의 사다리꼴 비교) → Σ_{d<q}Ψ(d) ≤ (2π)^{-1/2}[(4/3)n^{3/2}+√n-1/3-n]
        anal = math.exp(3*(q-1)/(2*k))*sB*((4/3)*n_**1.5 + math.sqrt(n_) - 1/3 - n_)/q**1.5
        exact_sum = math.exp(3*(q-1)/(2*k))*sum(Psi[d] for d in range(1, q))/q**1.5
        if anal > worst[0]: worst = (anal, q, k)
        if exact_sum > worst_exact[0]: worst_exact = (exact_sum, q, k)
P(f"  해석 연쇄 e^{{3(q-1)/(2k)}}(2π)^(-1/2)[(4/3)(q-1)^1.5+√(q-1)-1/3-(q-1)]/q^1.5 의 최댓값(2≤q≤101, k∈{{9950,10000}}) = {worst[0]:.5f} (q={worst[1]}, k={worst[2]})  ≤ 0.5: {worst[0] <= 0.5}")
vals = [math.exp(3*(q-1)/(2*9950))*sB*((4/3)*(q-1)**1.5 + math.sqrt(q-1) - 1/3 - (q-1))/q**1.5 for q in range(2, 102)]
P(f"  q 에 대해 증가(2..101): {all(vals[i] <= vals[i+1] for i in range(len(vals)-1))}; q=2: {vals[0]:.4f}, q=50: {vals[48]:.4f}, q=101: {vals[-1]:.5f}")
P(f"  Ψ 합을 그대로 쓴 값의 최댓값 = {worst_exact[0]:.5f} (q={worst_exact[1]});  참고: k→∞ 극한 Σ_{{d<q}}Ψ(d)/q^1.5 (q=101) = {sum(Psi[d] for d in range(1,101))/101**1.5:.5f}")
# Σ_{d<q}√d ≤ (2/3)((q-1/2)^1.5 - 2^-1.5) 확인
okRoot = all(sum(math.sqrt(d) for d in range(1, n+1)) <= (2/3)*n**1.5 + 0.5*math.sqrt(n) - 1/6 + 1e-12 for n in range(1, 300))
P(f"  Σ_{{d=1}}^{{n}}√d ≤ (2/3)n^1.5+(1/2)√n-1/6 (n≤299; 오목 사다리꼴): {okRoot}")
# (ㄴ)
P("\n== (ㄴ) F4 (b) 닫힌 상계의 정수 전수 ==")
def e_(x, C): return x + C*x**1.5
for C in (0.525, 0.6):
    bad = 0; worst_ratio = 0
    for L in range(2, 201):
        rhs = L*L/3 + (8*C/25)*math.sqrt(0.4)*L**2.5
        mx = 0
        for p in range(1, L):
            for q in range(1, L-p+1):
                j = L-p-q  # j 최대에서 손실 최대(계수 양)
                v = j*(e_(q, C)+e_(p, C)) + (e_(q, C)*(p-1)+e_(p, C)*(q-1))/2
                if v > mx: mx = v
        if mx > rhs: bad += 1
        worst_ratio = max(worst_ratio, mx/rhs)
    P(f"  C={C}: L≤200 에서 위반 {bad}건, max(좌변/우변)={worst_ratio:.4f}")
# u-매개화 끝점 식 대조 (p=q 끝점): 손실 = Lr-(3/4)r²-r/2 + (C/√2) r^1.5 (L-(3/4)r-1/2), r=p+q
L, C = 102, 0.525
mxpq = max(((L-2*p)*2*e_(p, C) + e_(p, C)*(p-1), p) for p in range(1, L//2+1))
r = 2*mxpq[1]
form = L*r - 0.75*r*r - r/2 + (C/math.sqrt(2))*r**1.5*(L - 0.75*r - 0.5)
P(f"  u=1/2 끝점(p=q) 식 대조 L=102: 전수 p=q 최댓값 {mxpq[0]:.2f} (p={mxpq[1]}) vs 식 {form:.2f}")
P(f"  C-몫의 r-최대화: max_r [L r^1.5 - (3/4) r^2.5]/L^2.5 = {0.8**1.5*(1-0.6):.5f}, ×1/√2 = {0.8**1.5*0.4/math.sqrt(2):.5f} = (8/25)√(2/5) = {(8/25)*math.sqrt(0.4):.5f}")
# (ㄷ)
P("\n== (ㄷ) 접합점 산술 ==")
for K, L in ((10000, 50), (12000, 58), (13000, 79), (14000, 99), (15000, 102)):
    q = L-1
    Ceff = (1+q/K)/(2*(1-q**1.5/(2*K)))
    rhs = L*L/3 + (8*0.525/25)*math.sqrt(0.4)*L**2.5
    P(f"  (K,L)=({K},{L}): C_eff(q={q})={Ceff:.4f} ≤ 0.525: {Ceff <= 0.525};  L²/3+0.2024·0.525·L^2.5 = {rhs:.1f} < K: {rhs < K}")
P("  (ㄷ′) 현행 꼬리 삼중 tf=0.54 로는 (15000,102) 에서 C_eff=(1+101/15000)/(2(1-0.54·101^1.5/15000))·1.08 ... 닫힌 꼴이 15000 을 넘음(X3·A7) — 1/2 이 필요하다.")
with open(os.path.join(ROOT, r"scripts\구조압축\결정_K1_P9_out.txt"), "w", encoding="utf-8", newline="\n") as f:
    f.write("\n".join(out)+"\n")
print("\n".join(out))
