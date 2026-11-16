# -*- coding: utf-8 -*-
"""결정 K1 검산 (1) — S11 재유도, top-roots 괄호, Borel 두 나무 항등식(A7-1), P3 자료 재집계,
반감 경계 n♯_k(A6b ③), 행 문턱 산술(D2), P9 합집합 상계의 바른 범위 재평가.
python -I 로 돌린다. 출력은 결정_K1_S11_P3_out.txt.
"""
import os, json, glob, math
from fractions import Fraction
from mpmath import mp, mpf, log, exp, sqrt, loggamma as lgamma0
from mpmath import loggamma
def lgamma(x):
    return loggamma(x)

mp.dps = 50
ROOT = r"C:\math\임시\주차함수_증명"
out = []
def P(s=""):
    out.append(s)

# ---------- (1) S11: 위험률 하계 1/(2k) 의 재유도 ----------
P("== (1) S11 재유도: hz_k(N) >= 1-e^{-eps_N}, eps_N = g(N+1)-g(k), N+1 >= 2k ==")
def g(x):
    x = mpf(x); return (x-1)*log(1+1/x)
ok_all = True
for k in [8, 9, 10, 22, 50, 100, 301, 841, 2001, 3131, 6667, 10**4, 10**6]:
    k = mpf(k)
    lo_g = 1-3/(2*k)+1/(2*k**2); hi_g = 1-3/(2*k)+5/(6*k**2)
    c1 = (lo_g <= g(k) <= hi_g) and (1-3/(4*k)+1/(8*k**2) <= g(2*k) <= 1-3/(4*k)+5/(24*k**2))
    eps_lo = 3/(4*k) - 17/(24*k**2)
    c2 = g(2*k)-g(k) >= eps_lo
    hz_lo = 1-exp(-(g(2*k)-g(k)))
    claimed = (mpf(3)/4 - 11/(6*k))/k
    c3 = hz_lo >= claimed
    c4 = claimed >= 1/(2*k)
    ok_all &= c1 and c2 and c3 and (c4 or k < 8)
    P(f"  k={int(k):>8}: g 상하계 {c1}; eps>=3/(4k)-17/(24k^2) {c2}; 1-e^-eps={mp.nstr(hz_lo,10)} >= (3/4-11/(6k))/k={mp.nstr(claimed,10)} {c3}; >=1/(2k) {c4}")
P(f"  k>=8 전부 성립: {ok_all}  ((3/4-11/(6k)) >= 1/2 <=> k >= 22/3)")

# ---------- (2) top-roots 괄호에 hz >= 1/(2k) 를 넣은 값 ----------
P("\n== (2) 7:top-roots 괄호 (1/(2k))Σ_{U<=300}(rw-1) - 1 >= (1/(2k))[2.38 k^{3/2}(n+1-k)^2/(e^{sg_n} n(n+1)) - 301] - 1 ==")
def sg(n):
    n = mpf(n); return n*log(n/(n+1))+1
def bracket(k, n):
    k = mpf(k); n = mpf(n)
    return (mpf('2.38')*k**mpf(1.5)*(n+1-k)**2/(exp(sg(n))*n*(n+1)) - 301)/(2*k) - 1
def closed(k):
    k = mpf(k); return mpf('0.528')*sqrt(k) - 151/k - 1
for k in [301, 400, 500, 841, 1000, 2001, 3131, 6667, 10**4, 10**5]:
    n = 3*k+1
    b = bracket(k, n)
    # n 에 대한 단조성 점검(표본): n=3k+1 .. 100k
    mins = min(bracket(k, nn) for nn in [3*k+1, 3*k+2, 4*k, 5*k, 10*k, 30*k, 100*k, 10**7])
    P(f"  k={k:>7}: n=3k+1 괄호={mp.nstr(b,6)}; 표본 n 최소={mp.nstr(mins,6)} (n=3k+1에서 최소); 닫힌 꼴 0.528√k-151/k-1={mp.nstr(closed(k),6)}; e^(-sg_{{3k+1}})={mp.nstr(exp(-sg(n)),7)}")
# 닫힌 꼴이 양이 되는 최소 k, 20 을 넘는 최소 k
kpos = next(k for k in range(2, 10**5) if closed(k) > 0)
k20 = next(k for k in range(2, 10**6) if closed(k) > 20)
P(f"  0.528√k-151/k-1 > 0 인 최소 k = {kpos}; > 20 인 최소 k = {k20}")
P(f"  n-U >= 2k (U<=300) 가 n>=3k+1 전체에서 성립할 조건: 3k+1-300 >= 2k <=> k >= 299; U_0=300 <= k-1 <=> k >= 301")
P(f"  e^(-sg_n) >= 0.9994 인 최소 n: {next(n for n in range(2, 5000) if exp(-sg(n)) >= mpf('0.9994'))}  (n >= 3·301+1 = 904 에서 {mp.nstr(exp(-sg(904)),7)})")
P(f"  (1-k/n)^2 >= 4/9 (n >= 3k+1), 1.19·0.9994·4/9 = {mp.nstr(mpf('1.19')*mpf('0.9994')*4/9, 6)} >= 0.528")

# ---------- (3) A7-1 Borel 두 나무 항등식 (정확 유리수) ----------
P("\n== (3) A7-1: π_m(j) = Bor(j)Bor(m+1-j)/Bor(m+1), 𝒫_m(j) = (j/m)π_m(j)  (정확 유리수, m<=40 전수) ==")
def p(n):  # (n+1)^(n-1), p(0)=1
    return Fraction((n+1)**(n-1)) if n >= 1 else Fraction(1)
def borq(w):  # e^w·Bor(w) = w^{w-1}/w!  (e 인자는 항등식에서 소거)
    return Fraction(w**(w-1), math.factorial(w))
viol = 0; cnt = 0
for m in range(1, 41):
    for j in range(1, m+1):
        pi = Fraction(math.comb(m, j)) * Fraction(j**(j-1)) * p(m-j) / p(m)
        rhs = borq(j)*borq(m+1-j)/borq(m+1)
        Pm = Fraction(j*math.comb(m-1, j-1)) * p(j-1) * p(m-j) / p(m)
        cnt += 1
        if pi != rhs or Pm != Fraction(j, m)*pi:
            viol += 1
P(f"  검사 {cnt}쌍, 위반 {viol}")

# ---------- (4) P3 자료: G′ 인증서 1500열의 T_k 와 모멘트 인증 위치 수 ----------
P("\n== (4) P3: column_cert_iv/res_*.jsonl 재집계 ==")
rows = {}
for fn in glob.glob(os.path.join(ROOT, r"원고_자료\세션_재계산\column_cert_iv", "res_*.jsonl")):
    with open(fn, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line: continue
            d = json.loads(line); rows[d["k"]] = d
ks = sorted(rows)
P(f"  열 수 {len(ks)}, 범위 {ks[0]}..{ks[-1]}, 빠진 열 {[k for k in range(501, 2001) if k not in rows]}")
keys = sorted(rows[ks[0]].keys())
P(f"  필드: {keys}")
nvkey = "nV" if "nV" in rows[ks[0]] else None
assert nvkey, "nV 필드 없음"
T = {k: max(rows[k]["n0"], rows[k][nvkey]) for k in ks}
P(f"  ok 전부: {all(rows[k]['ok'] for k in ks)}; nV_exact 전부: {all(rows[k].get('nV_exact', True) for k in ks)}")
P(f"  T_k = max(n0, nV): 501-840 최대 {max(T[k] for k in ks if k<=840)} (k={max((k for k in ks if k<=840), key=lambda k:T[k])}); 전부 <=20000: {all(T[k]<=20000 for k in ks if k<=840)}")
P(f"  T_841={T[841]}, T_2000={T[2000]}; T_k 비감소: {all(T[ks[i]]<=T[ks[i+1]] for i in range(len(ks)-1))}; T_k>20000 첫 열: {next(k for k in ks if T[k]>20000)}")
P(f"  T_k = nV (n0<=nV) 전부: {all(rows[k]['n0']<=rows[k][nvkey] for k in ks)}")
with open(os.path.join(ROOT, r"원고_자료\세션_재계산\moment_cert_iv\nM.json"), encoding="utf-8") as f:
    nM = {int(k): v for k, v in json.load(f).items()}
diff = [nM[k]-T[k] for k in ks if k >= 841]
P(f"  n_M(k)-T_k (841-2000): [{min(diff)}, {max(diff)}], 전부 양: {all(d>0 for d in diff)}; n_M(841)={nM[841]}, n_M(2000)={nM[2000]}")
pos1 = sum((13*k*k)//100 - 2*k for k in range(501, 841))
pos2_cur = sum(nM[k]-10001 for k in range(841, 2001))
pos2_20001 = sum(T[k]-20001 for k in range(841, 2001))
pos2_10001 = sum(T[k]-10001 for k in range(841, 2001))
P(f"  모멘트 인증 위치: 첫째 범위(501-840) {pos1:,}; 둘째 범위 현행 [10001,n_M-1] {pos2_cur:,}; 합 {pos1+pos2_cur:,}")
P(f"  P3+D2 뒤 둘째 범위 [20001,T_k-1]: {pos2_20001:,} (감소 {pos1+pos2_cur-pos2_20001:,}); 시작 10001 이면 {pos2_10001:,}")
P(f"  행 10001-20000 몫 = 1160*10000 = {1160*10000:,} (=둘째 범위 현행의 {1160*10000/pos2_cur:.1%})")
P(f"  T_k <= ceil(0.836 k^1.5) 전부: {all(T[k] <= math.ceil(0.836*k**1.5) for k in ks)}")

# ---------- (5) A6b ③: 반감 경계 n♯_k = k+(k+1)t_k (정확 정수) ----------
P("\n== (5) A6b ③: n♯_k <= 20001 인 열 ==")
def t_k(k):
    j = 0
    while (k+1)**j * k**(j+1) + (k-1)**(2*j+1) < 2*k**(2*j+1):
        j += 1
    return j
ns = {k: k+(k+1)*t_k(k) for k in range(2, 700)}
P(f"  n♯_k <= 20001 인 최대 k = {max(k for k in ns if ns[k] <= 20001)}; n♯_200={ns[200]}, n♯_201={ns[201]}, n♯_202={ns[202]}; max_{{k<=120}} n♯_k = {max(ns[k] for k in range(2,121))}; n♯_500={ns[500]}, n♯_501={ns[501]}")
P(f"  n♯_k 비감소(k<=699): {all(ns[k]<=ns[k+1] for k in range(2,699))}")

# ---------- (6) 행 문턱 산술 ----------
P("\n== (6) 행 문턱 ==")
P(f"  3k+1 <= 20000 <=> k <= {(20000-1)//3};  3k >= 20001 <=> k >= {-(-20001//3)};  3k-1 >= 20001 <=> k >= {-(-20002//3)};  2k+102 >= 20001 <=> k >= {-(-(20001-102)//2)}")
P(f"  2001 <= k <= 3130 에서 20001 >= 3k+1: {all(20001 >= 3*k+1 for k in range(2001, 3131))}")

# ---------- (7) P9: 합집합 상계(바른 범위 t<=N)와 Jensen 판, k→∞ 극한 ----------
P("\n== (7) P9: 1-s_{k+q-1}(k) <= Σ_{t=k+1}^{k+q-1} θ_{k+q}(t)(t-k)/t  (θ_m(t)=Ren(m-t)Bor(t)/Bor(m)) ==")
def lbor(w):  # log Bor(w)
    w = mpf(w); return -w + (w-1)*log(w) - lgamma(w+1)
def lren(j):  # log Ren(j), Ren(0)=1
    if j == 0: return mpf(0)
    j = mpf(j); return (j-1)*log(j) - j - lgamma(j)
for k in [10000, 100000]:
    best = (0, 0); bestJ = (0, 0)
    for q in range(2, 102):
        m = k+q-1+1  # N+1 = k+q
        ub = mpf(0); bj = mpf(0)
        for t in range(k+1, k+q):
            th = exp(lren(m-t)+lbor(t)-lbor(m))
            ub += th*(t-k)/mpf(t); bj += th*log(mpf(t)/k)
        r = k*ub/mpf(q)**1.5; rJ = k*(1-exp(-bj))/mpf(q)**1.5
        if r > best[0]: best = (r, q)
        if rJ > bestJ[0]: bestJ = (rJ, q)
    P(f"  k={k}: max_q k·UB/q^1.5 = {mp.nstr(best[0],5)} (q={best[1]}); Jensen 판 max = {mp.nstr(bestJ[0],5)} (q={bestJ[1]})  (1/2 에 닿는가: {best[0] <= 0.5})")
lim = max((sum(exp(lren(i))*(q-i) for i in range(1, q))/mpf(q)**1.5, q) for q in range(2, 102))
P(f"  k→∞ 극한 Σ_{{i<q}}Ren(i)(q-i)/q^1.5 최댓값(q<=101) = {mp.nstr(lim[0],5)} (q={lim[1]})")
P("  결론: 합집합 상계(바른 범위)·Jensen 판 모두 0.55–0.57 → F4의 1/2 은 이 길로 나오지 않는다(A7의 0.837은 보조 뿌리 t=N+1 을 합에 넣은 값).")

with open(os.path.join(ROOT, r"scripts\구조압축\결정_K1_S11_P3_out.txt"), "w", encoding="utf-8", newline="\n") as f:
    f.write("\n".join(out)+"\n")
print("\n".join(out))
