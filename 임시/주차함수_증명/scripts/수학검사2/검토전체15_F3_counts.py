# F3 independent check: counts, m(n), Cayley ratio table, misc constants in 5A
from fractions import Fraction
from math import isqrt, e, pi, sqrt, log, exp, sin, cos, tan
import math

def ceil_div(a,b): return -((-a)//b)

# (1) counts in Thm 5-1 / 5-2
cnt_second = sum(ceil_div(n,2)-1 for n in range(10001,20001))
print("5-1 second piece comparisons:", cnt_second, "(claim 74,995,000)")
def qr_positions(n):  # (n-1)/2 <= l <= n-3 integer l
    lo = ceil_div(n-1,2); hi = n-3
    return max(0, hi-lo+1)
print("5-1 fourth piece positions 5..20000:", sum(qr_positions(n) for n in range(5,20001)), "(claim 99,970,002)")
print("5-2 positions 20001..50000:", sum(qr_positions(n) for n in range(20001,50001)), "(claim 524,955,000)")
def adj_pairs(n):  # ceil((n-1)/2) <= l <= n-2
    lo = ceil_div(n-1,2); hi = n-2
    return max(0,hi-lo+1)
print("D.c50 adjacent pairs 20001..50000:", sum(adj_pairs(n) for n in range(20001,50001)), "(claim 524,985,000)")
print("D.c50 adjacent pairs 5..20000:", sum(adj_pairs(n) for n in range(5,20001)), "(claim 99,989,998)")
print("rows 50..20000:", 20000-50+1, "(claim 19,951)")
print("Newton polynomials:", sum(r-1 for r in range(2,171)), "(claim 14,365)")
print("r range 171..9999 count:", 9999-171+1, "(claim 9829)")

# (2) m(n)
def mfrak(n):
    best = 170
    m = 171
    while m**3 <= (n-9*m)**2 and n-9*m >= 0:
        best = m; m += 1
    return best
print("m(20001) =", mfrak(20001), "(claim 597);  m(50001) =", mfrak(50001), "(claim 1160)")
print("m(n)>=597 for n>=20001:", all(mfrak(n)>=597 for n in (20001,20002,20100)))
# check m(n) < n^(2/3)
print("m(20001)^(3/2) =", 597**1.5, " n^(2/3)=", 20001**(2/3))

# (3) Cayley ratio table (lemma cayley-ratio): cr_k (1+5/(2k)+2/k^2) for k=1..9
vals=[]
for k in range(1,10):
    cr = Fraction(k+1,k)**(k-2)
    v = cr*(1+Fraction(5,2*k)+Fraction(2,k*k))
    vals.append(float(v))
print("cr_k*(1+5/2k+2/k^2), k=1..9:", [f"{v:.5f}" for v in vals], " all > 87/32=2.71875:", all(v>87/32 for v in vals))
print("e < 65/24+1/100 =", 65/24+0.01, "< 87/32 =", 87/32, ":", e < 65/24+0.01 < 87/32)

# (4) constants in 5-5 proof
s=100
print("sqrt(3pi/2) =", sqrt(3*pi/2), "< 2.170804:", sqrt(3*pi/2)<2.170804)
print("1/2+2*0.845204-sqrt(3pi/2) =", 0.5+2*0.845204-sqrt(3*pi/2))
br = 1/(3*s)+8/(3*s*s)+2.507/(s*s)+(1+2.1709*s)/s**3
print("bracket at s=100:", br, "< 0.0041:", br<0.0041)
print("sqrt(pi/2)=",sqrt(pi/2))

# (5) 5-11 proof constants
print("27.14^3 =", 27.14**3, "< 20001:", 27.14**3<20001, "; 27.14^2=",27.14**2)
print("(149/200)^3 =", (149/200)**3, "> (16/25)^2 =", (16/25)**2)
print("(3/4)^3 =", 0.75**3, "< (13/20)^2 =", 0.65**2)
print("(3/4)^(3/2)=",0.75**1.5, " 27/(4*27.14)=",27/(4*27.14))
r0 = math.floor(0.75*20001**(2/3)); print("r0(20001)=",r0)

# (6) 5-7 proof constant 0.28
val = (9/16)*(169/400)*(144/121)*(88/1443)*(2.5+9/1058)**3
print("tail ratio const:", val, "< 0.28:", val<0.28)
print("rq_* at S=23:", (13/20)*(1+3/529)/23, "< 1/12:", (13/20)*(1+3/529)/23 < 1/12)
# cover-edge
print("1/(1+9/sqrt(598)) =", 1/(1+9/sqrt(598)), "> 0.73")
print("(9/5)^(2/3) =", (9/5)**(2/3), "> 1.4")
print("10/2^(2/3) =", 10/2**(2/3), "> 6.29")
print("832^1.5=",832**1.5," 833^1.5=",833**1.5," 1.2*20001=",1.2*20001)
print("30001^(2/3)=",30001**(2/3))
# 5-12 rq bounds
for lab,(x,rr) in {"A":(6/5,598),"A+1":(3/2,833),"A+2":(9/5,966),"A+3":(21/10,2164),"A+4":(12/5,10000)}.items():
    print(lab, "rq<=", x/sqrt(rr), "<1/16:", x/sqrt(rr)<1/16)
print("(5/12)*sqrt(598)=", (5/12)*sqrt(598))
print("1/sqrt(598)=",1/sqrt(598))
# omitted-tail (나)
print("(12/5)(1+1/598)/sqrt(598)=", 2.4*(1+1/598)/sqrt(598), "<0.1")
print("(12/11)^1.5=",(12/11)**1.5, " 12/(110e)=",12/(110*e), " 1/24=",1/24)
print("log10(1.15*598^3)=", math.log10(1.15*598**3), " 598*log10(24)=", 598*math.log10(24))
# 5-13 constants
print("10001^(-1/3)=",10001**(-1/3), " 29*0.0015+0.00141+0.0015=",29*0.0015+0.00141+0.0015, " 0.0015/1.25^12=",0.0015/1.25**12)
print("1-cos(1)=",1-cos(1),">=0.458")
print("10*10001^(2/3)=",10*10001**(2/3),"<10001")
# et(1/2)
phi=0.5; et = e*phi*exp(-phi/tan(phi))/sin(phi); print("log et(1/2)=", log(et), "> 0.1267:", log(et)>0.1267)
# kernel-C-bound / K1 numeric check for m<=3000 using lgamma
def rb(m): return math.lgamma(m+1)-(m+0.5)*log(m)+m-0.5*log(2*pi)
ok1=ok2=True; worst=0
for m in range(1,3001):
    ratio = exp(rb(m)-rb(2*m))
    if not (1 <= ratio <= 1+1/(12*(2*m-1))): ok1=False
    lo = 1+1/(25*(2*m-1)) if m>=2 else 26/25
    if ratio < lo: ok2=False
print("kernel-C-bound first line m<=3000:", ok1, "; (K1) coefficient bound:", ok2, "; m=1 ratio 2sqrt2/e=",2*sqrt(2)/e)
# kernel-crude: Ren(m)/cb_m decreasing, first 2/e
def Ren(m): return exp(m*log(m)-m-math.lgamma(m+1))
def cb(m): return exp(math.lgamma(2*m+1)-2*math.lgamma(m+1)-m*log(4))
seq=[Ren(m)/cb(m) for m in range(1,2001)]
print("Ren/cb decreasing:", all(seq[i+1]<seq[i] for i in range(len(seq)-1)), " first=",seq[0]," 2/e=",2/e)
# laurent-coeff (나): (1-1/(6m))/sqrt(pi m) <= cb_m <= 1/sqrt(pi m)
print("cb bounds:", all((1-1/(6*m))/sqrt(pi*m) <= cb(m) <= 1/sqrt(pi*m) for m in range(1,2001)))
# kernel-sandwich (나): cb_m sqrt(m) increasing, cb_m sqrt(m+1/2) decreasing
print("cb sqrt(m) incr:", all(cb(m)*sqrt(m) < cb(m+1)*sqrt(m+1) for m in range(1,2000)), " cb sqrt(m+1/2) decr:", all(cb(m)*sqrt(m+.5) > cb(m+1)*sqrt(m+1.5) for m in range(1,2000)))
# moving-tail/nf-ratio: nf ratio bounds
def nf_ratio_log(rr): return 1+(rr-3)*log(1-1/rr)
print("nf-ratio log in [0,3/r] for r=3..2000:", all(0<=nf_ratio_log(rr)<=3/rr for rr in range(3,2001)))
# first-moment-weight: coefficient (2i+3)/(i(i+1)) decreasing, first 5/2
print("coeffs:", [(2*i+3)/(i*(i+1)) for i in range(1,6)])
# tw log-convex check
def tw(j): return Fraction(1) if j==1 else Fraction((j-1)**(j-1), math.factorial(j))
rat=[tw(j+1)/tw(j) for j in range(1,30)]
print("tw ratios nondecreasing:", all(rat[i]<=rat[i+1] for i in range(len(rat)-1)), " first two:", float(rat[0]), float(rat[1]))
