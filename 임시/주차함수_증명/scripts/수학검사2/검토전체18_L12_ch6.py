# L12 검산(부록 D 장6): prop-W-thirteen의 L(d),R(d); tilt-sum의 정확 유리수 합(k=2..60); theorem-D-base의 쌍 수와 q(m,d) (m<=80 정확 행); theorem-U 상수 조립.
from fractions import Fraction as Fr
from math import comb, factorial, floor
from mpmath import mp, mpf, e as E, exp, sqrt, pi
mp.dps=30
# prop-W-thirteen
k=3131
Ren=lambda r1: mpf(r1)**(r1-1)/(E**(r1-1)*factorial(r1-1))  # e*Ren(r+1) with r1=r+1
def L(d): return (k-1)*(Ren(d+1)-mpf(60)*(d+1)/(k+d))
def R(d): return 2*(1+sum(Ren(r+1)+mpf(60)*(r+1)/(k+d) for r in range(1,d)))
print("prop-W: ",[ (d, mp.nstr(L(d),6), mp.nstr(R(d),4)) for d in range(1,15)], " min L-R (d<=13):", mp.nstr(min(L(d)-R(d) for d in range(1,14)),4))
# tilt-sum exact
def S(k):
    q=Fr(k,k+1)**(k-1)
    return sum(Fr(n**(n-1),factorial(n))*q**n for n in range(2,k+2))
vals={k:S(k) for k in range(2,61)}
print("tilt-sum: all <1:",all(v<1 for v in vals.values()), " max at k=2:",vals[2], float(vals[2]), " k=3,10,20,42,43:",[round(float(vals[k]),6) for k in (3,10,20,42,43)])
# theorem-D-base counts
pairs=sum(floor(m**(2/3)/2) for m in range(4,701)); pairs2=sum(1 for m in range(4,701) for d in range(1,m) if 8*d**3<=m*m)
print("thmD pairs:",pairs,pairs2," m=700 dmax:",floor(700**(2/3)/2), " 240 check:",sum(1 for m in range(1,31) for d in range(1,m+1) if 2*d<=m+1))
N=80
A=[[1]*(N+1)]
for n in range(1,N+1):
    w=[comb(n-1,j) for j in range(n)]
    row=[sum(w[j]*min(j+1,l+1)*A[j][l]*A[n-1-j][l] for j in range(n)) for l in range(n-1)]
    row+=[(n+1)**(n-1)]*(N+1-len(row)); A.append(row)
b=lambda n,l: A[n][l]-(A[n][l-1] if l>0 else 0)
Psi=lambda d: sum(mpf(j)**j*exp(-j)/factorial(j) for j in range(1,d+1))
q=lambda m,d: m*mpf(b(m,m-d))/(mpf((m+1)**(m-1))*Psi(d))
print("thmD q(4,1)=",mp.nstr(q(4,1),12)," q(3,1)=",mp.nstr(q(3,1),10))
qs=[(q(m,d),m,d) for m in range(4,N+1) for d in range(1,m) if 8*d**3<=m*m]
print("thmD m<=80: min",mp.nstr(min(qs)[0],8),min(qs)[1:]," max",mp.nstr(max(qs)[0],8),max(qs)[1:], " all in [1/2,3/2]:",all(mpf(1)/2<=x[0]<=mpf(3)/2 for x in qs))
# theorem-U assembly
c=1/sqrt(2*pi); G=mpf('2.7323'); ms=mpf('0.8051')
print("thmU: 3c(8.133+10.301c)=",mp.nstr(3*c*(mpf('8.133')+mpf('10.301')*c),6)," 1.5 G m c(17.951+23.462c)=",mp.nstr(1.5*G*ms*c*(mpf('17.951')+mpf('23.462')*c),6), " with recomputed bounds:",mp.nstr(3*c*(mpf('8.13091')+mpf('10.29939')*c),6), mp.nstr(1.5*G*ms*c*(mpf('17.94855')+mpf('23.46002')*c),6))
