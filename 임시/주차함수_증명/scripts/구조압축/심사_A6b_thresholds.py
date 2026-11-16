# A6b: 반감 경계 n^sharp_k = k+(k+1) t_k 와 평탄 문턱 n^flat_k (phi_k(n)>=0 최소 n>=2k+1) 을
# 정확 산술(t_k: 정수 비교; n^flat: Fraction/Decimal 고정밀)로 k=2..600 에서 계산하고 20001과 비교한다.
# 또 phi_k == psi_G (G = x_k) 임을 확인한다.
from fractions import Fraction
from decimal import Decimal, getcontext
getcontext().prec = 60

def t_k(k):
    j = 0
    while True:
        if (k+1)**j * k**(j+1) + (k-1)**(2*j+1) >= 2 * k**(2*j+1):
            return j
        j += 1

def xk(k):
    return Fraction(k, k+1)**(k-1)

def v_k(k, Z, H):
    # (1+1/k)^Z + (1-1/k)^(Z+H) - 2, Z,H Decimal
    a = Decimal(1) + Decimal(1)/Decimal(k)
    b = Decimal(1) - Decimal(1)/Decimal(k)
    return (Z*a.ln()).exp() + ((Z+H)*b.ln()).exp() - 2

def phi_k(k, n):
    m = Decimal(n-k)/Decimal(k+1)
    x = xk(k)
    H = Decimal(x.numerator)/Decimal(x.denominator) * Decimal(n)/Decimal(k)
    return v_k(k, m, H)

def n_flat(k):
    # phi_k convex in n, phi_k(2k+1)<0; binary search first n>=2k+1 with phi>=0
    lo, hi = 2*k+1, 2*k+1
    while phi_k(k, hi) < 0:
        hi = 2*hi
    while hi - lo > 1:
        mid = (lo+hi)//2
        if phi_k(k, mid) >= 0: hi = mid
        else: lo = mid
    return hi

out = []
ks = list(range(2, 601))
maxk_sharp = None; maxk_flat = None
rows = []
for k in ks:
    t = t_k(k); ns = k + (k+1)*t
    nf = n_flat(k)
    rows.append((k, t, ns, nf))
    if ns <= 20001: maxk_sharp = k
    if nf <= 20001: maxk_flat = k
# monotone check
sharp_vals = [r[2] for r in rows]; flat_vals = [r[3] for r in rows]
mono_sharp = all(sharp_vals[i] <= sharp_vals[i+1] for i in range(len(rows)-1))
mono_flat = all(flat_vals[i] <= flat_vals[i+1] for i in range(len(rows)-1))
out.append(f"k=2..600: n^sharp_k<=20001 인 최대 k = {maxk_sharp}; n^flat_k<=20001 인 최대 k = {maxk_flat}")
out.append(f"n^sharp_k 비감소? {mono_sharp}; n^flat_k 비감소? {mono_flat}")
for k in [2,3,5,10,20,50,100,120,121,150,200,204,205,250,272,273,300,400,500,501,600]:
    r = rows[k-2]
    out.append(f"k={k:4d}  t_k={r[1]:4d}  n^sharp={r[2]:7d}  n^flat={r[3]:7d}  n^flat/k^2={r[3]/k/k:.4f}  n^sharp/k^2={r[2]/k/k:.4f}  n^flat<=n^sharp? {r[3]<=r[2]}")
# all k<=120: n^sharp <= 20001?
out.append(f"max n^sharp_k, k<=120: {max(r[2] for r in rows if r[0]<=120)}; max n^flat_k, k<=120: {max(r[3] for r in rows if r[0]<=120)}")
out.append(f"n^flat_k <= n^sharp_k for all k<=600? {all(r[3]<=r[2] for r in rows)}")
# phi_k == psi_G with G=x_k: by definition identical; numeric spot check
k=50; n=1000
m = Decimal(n-k)/Decimal(k+1); x=xk(k); G=Decimal(x.numerator)/Decimal(x.denominator)
out.append(f"phi_50(1000) - psi_{{x_50}}(1000) = {phi_k(50,1000) - v_k(50, m, G*Decimal(n)/Decimal(k))}")
txt = "\n".join(out)
print(txt)
open("C:/math/임시/주차함수_증명/scripts/구조압축/심사_A6b_thresholds_out.txt","w",encoding="utf-8").write(txt+"\n")
