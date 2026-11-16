# K12: D.band-check 첫 셀 재계산(식 그대로, mpmath 30자리 점 평가), D.theorem-D-base 전 범위 재계산(넘는 수 선형 재귀), D.tilt-sum B_2, central-gap (ㄴ) n<=60
import mpmath as mp
from math import comb, factorial
from fractions import Fraction as F
mp.mp.dps=30
# ---- band-check first cell
n=mp.mpf(50001); la=mp.mpf(1)/2; lb=la+mp.mpf(1)/24000; w0=mp.mpf('0.71216')
wid=mp.mpf('0.75')*(mp.mpf('1.1')*lb*n)**(mp.mpf(2)/3)+1
hov=mp.mpf(0); z=0
while True:
    t=1-2/mp.sqrt(mp.pi)*mp.mpf(z)**1.5/mp.sqrt(mp.floor(mp.mpf('0.3')*(1-lb)*n-1)-1)
    if t<=0: break
    hov+=(la-1/n)**z*t; z+=1
sec=1-mp.sqrt(2/mp.pi)/mp.sqrt(mp.mpf('0.3')*(1-lb)*n-1)-mp.mpf('0.3')*(1-la)*n/mp.sqrt(2*mp.pi)*((n+1)/(la*n*((1-lb)*n-wid)))**1.5*mp.e**(1/(12*(n+1)))
top=(1+1/n)**1.5/mp.sqrt(2*mp.pi)/mp.sqrt(la)*(1-lb)**-1.5/mp.sqrt(n)*mp.e**(1/(12*n))
K=la*mp.e**(-1/(12*(mp.mpf('0.4')*(1-lb)*n-6*(lb*n)**(mp.mpf(2)/3)+1))-1/(12*la*n)-1/(12*(n+1)))
c1=mp.mpf('1.5')*((2*lb-1)*n+2*wid)/(la*n*((1-lb)*n-wid)); e0=mp.mpf('1.5')*wid*((2*lb-1)*n+2*wid)/((la*n-1)*((1-lb)*n-wid))
W=mp.mpf(2)/3/mp.sqrt(2*mp.pi)*(wid+1)**1.5*c1*(1+wid/(la*n))**1.5*mp.e**(e0+1/(12*la*n))
print("band first cell: hov",mp.nstr(hov,8),"sec",mp.nstr(sec,8),"top",mp.nstr(top,8),"K",mp.nstr(K,8),"W",mp.nstr(W,8)," ratio",mp.nstr(hov*w0*K*(2*sec-top)-W,11))
# ---- B_2(k)
B2=lambda k:(1-1/mp.e)+(mp.e**(mp.mpf(3)/2+mp.mpf(1)/k)-1)*2*(mp.sqrt(k+1)-1)/(mp.sqrt(2*mp.pi)*(k+1))
print("B2(42)=",mp.nstr(B2(42),7)," B2(43)=",mp.nstr(B2(43),7))
# ---- theorem-D base via excess linear recursion
def p(m): return (m+1)**(m-1) if m>=1 else 1
P=[p(i) for i in range(800)]
def Ac_col(k,nmax):
    # returns dict n->A^c_{n,k-1} for k+1<=n<=nmax (nmax<=2k+1)
    A={}
    for n in range(k+1,nmax+1):
        s=sum(comb(n-1,i)*(n-k-i)*P[i]*P[n-1-i] for i in range(0,n-k))
        s+=sum(comb(n-1,i)*(k+i+1)*P[i]*A[n-1-i] for i in range(0,n-k-1))
        A[n]=s
    return A
# need b_{m,m-d}=A^c_{m,m-d-1}-A^c_{m,m-d}; A^c_{m,l}=A^c col with k=l+1
cols={}
def Ac(n,l):
    k=l+1
    if k not in cols: cols[k]=Ac_col(k,min(2*k+1,k+45))
    return cols[k].get(n,0) if n>=k+1 else 0
# sanity vs last-car for small n
def Acol_lastcar(l,N):
    A=[1]*(N+1)
    for n in range(1,N+1): A[n]=sum(comb(n-1,j)*min(j+1,l+1)*A[j]*A[n-1-j] for j in range(n))
    return A
ok=True
for m in range(2,31):
    for d in range(1,(m+1)//2+1):
        b1=Ac(m,m-d-1)-Ac(m,m-d)
        Al=Acol_lastcar(m-d,m); Al1=Acol_lastcar(m-d-1,m)
        if b1!=Al[m]-Al1[m]: ok=False
print("excess recursion == last-car for m<=30, 2d<=m+1:",ok)
Psi=lambda d: mp.fsum(mp.mpf(j)**j*mp.e**(-j)/mp.factorial(j) for j in range(1,d+1))
mn=(mp.mpf(10),None); mx=(mp.mpf(0),None); cnt=0
for m in range(3,701):
    for d in range(1,60):
        if 8*d**3>m*m: break
        b=Ac(m,m-d-1)-Ac(m,m-d)
        q=mp.mpf(m)*b/(mp.mpf(P[m])*Psi(d))
        if m==3: print("m=3,d=1: q=",mp.nstr(q,10)); continue
        cnt+=1
        if q<mn[0]: mn=(q,(m,d))
        if q>mx[0]: mx=(q,(m,d))
print("pairs",cnt," min q",mp.nstr(mn[0],12),mn[1]," max q",mp.nstr(mx[0],12),mx[1])
# ---- central gap (ㄴ) n<=60
neg=[]; viol=[]
for n in range(2,61):
    k=-(-n//2); A={l:Acol_lastcar(l,n)[n] for l in range(k-2,n)}
    b=lambda l: (A[l]-A[l-1]) if l-1>=k-2 else None
    d=A[k]-2*A[k-1]+A[k-2]
    if d<0:
        neg.append(n)
        if any((A[j]-A[j-1])<(A[j+1]-A[j]) for j in range(k,n-1)): viol.append(n)
print("d_{n,k_n}<0 for n in:",neg," right-half non-decreasing violations:",viol)
