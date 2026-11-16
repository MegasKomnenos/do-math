# J12: 부록D_장6 수치 재검산 — (6.50) 열세 쌍, 기울인 Borel 합과 B_2(k), 정리 D 기저의 쌍 수와 두 끝 비
import sys
from fractions import Fraction as F
from math import comb, factorial
import mpmath as mp
mp.mp.dps=40
sys.set_int_max_str_digits(0)
e=mp.e
def eRen(m): return mp.mpf(m)**(m-1)/(e**(m-1)*mp.factorial(m-1))  # e*Ren(m) = m^{m-1}/(e^{m-1}(m-1)!)
k=3131
for d in range(1,15):
    L=(k-1)*(eRen(d+1)-mp.mpf(60)*(d+1)/(k+d))
    R=2*(1+sum(eRen(r+1)+mp.mpf(60)*(r+1)/(k+d) for r in range(1,d)))
    print("d",d,"L=%.2f R=%.2f"%(L,R), "L>R",L>R)
# tilt sums exact rational
def Bor_q_sum(k):
    s=F(0)
    for n in range(2,k+2):
        s+=F(n**(n-1),factorial(n))*F(k,k+1)**((k-1)*n)
    return s
for k in [2,3,10,20,42,43]:
    print("k",k,"sum=%.6f"%float(Bor_q_sum(k)))
mx=max(range(2,61),key=lambda k:Bor_q_sum(k)); print("max over 2..60 at k",mx,Bor_q_sum(mx))
def B2(k): return (1-1/e)+(mp.e**(mp.mpf(3)/2+mp.mpf(1)/k)-1)*2*(mp.sqrt(k+1)-1)/(mp.sqrt(2*mp.pi)*(k+1))
print("B2(42)=%.6f B2(43)=%.6f B2(2000)=%.4f"%(B2(42),B2(43),B2(2000)))
# theorem D base pair count
cnt=sum(1 for m in range(4,701) for d in range(1,200) if 8*d**3<=m*m)
print("pairs 4<=m<=700, 8d^3<=m^2:",cnt, " d_max(700)=",max(d for d in range(1,200) if 8*d**3<=700**2), " d_max(689)=",max(d for d in range(1,200) if 8*d**3<=689**2))
def Psi(d): return sum(mp.mpf(j)**j/(e**j*mp.factorial(j)) for j in range(1,d+1))
def column(ell,N):
    A=[1]+[0]*N
    for n in range(1,N+1):
        A[n]=sum(comb(n-1,j)*min(j+1,ell+1)*A[j]*A[n-1-j] for j in range(n))
    return A
def q(m,d):
    l=m-d; C=column(l,m); Cm=column(l-1,m) if l>=1 else None
    b=C[m]-(Cm[m] if Cm else 0); p=(m+1)**(m-1)
    return mp.mpf(m)*b/(mp.mpf(p)*Psi(d))
print("q(4,1)=",mp.nstr(q(4,1),12)," q(3,1)=",mp.nstr(q(3,1),10))
print("q(689,39)=",mp.nstr(q(689,39),12))
