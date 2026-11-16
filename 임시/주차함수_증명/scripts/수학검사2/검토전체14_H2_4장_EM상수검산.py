# H2: borel-tail-arc 증명의 † 단계 — 상수 -2/3 항등식과 T(e^{-1-U}) 전개의 수치 점검
from mpmath import mp, mpf, exp, log, sqrt, pi, zeta, lambertw, factorial, quad, inf, floor
mp.dps=30
c=1/sqrt(2*pi)
# sum_j (j Bor(j) - c j^{-1/2}) with tail via Euler-Maclaurin-ish: use exact up to J and integral tail approx of -(c/12) j^{-3/2}
J=200000
def lBor(j): return -j+(j-1)*log(j)-log(factorial(j)) if j<2000 else None
s=mpf(0)
import math
for j in range(1,J+1):
    # Bor(j) via lgamma for speed
    lb=-j+(j-1)*math.log(j)-math.lgamma(j+1)
    s+= j*mpf(math.exp(lb)) - c/sqrt(j)
# tail: j Bor(j) - c j^{-1/2} = c j^{-1/2}(e^{-rb_j}-1) ~ -c/(12) j^{-3/2} ; sum_{j>J} ~ -c/12 * 2/sqrt(J)
tail=-c/12*2/sqrt(J)
M=zeta(mpf(1)/2)
print("zeta(1/2)=",M, " M via formula -3/2 - 1/2 int:", -mpf(3)/2-quad(lambda w:(w-floor(w)-mpf(1)/2)*w**(-mpf(3)/2),[1,2,3,4,5,10,100,inf])/2)
print("c*M + sum =",c*M+s+tail," target -2/3 =",-mpf(2)/3)
# T(e^{-1-U}) expansion
for U in (mpf('1e-2'),mpf('1e-4'),mpf('1e-6')):
    x=exp(-1-U); T=-lambertw(-x)
    print("U",U," T=",T," 1-sqrt(2U)+2U/3=",1-sqrt(2*U)+2*U/3," diff/U^1.5=",(T-(1-sqrt(2*U)+2*U/3))/U**1.5)
