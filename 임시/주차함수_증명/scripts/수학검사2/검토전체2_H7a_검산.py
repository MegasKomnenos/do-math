# H7a 검산: 7B 7.4-7.5의 수치 주장 몇을 독립으로 다시 센다.
from fractions import Fraction as F
from math import log, exp, ceil, sqrt
# (1) pair-check-10000: q<=q' 순서 없는 쌍 수, 최솟값 자리
k=10000
def pish(q): return F(q*(q-1),2*(k+1))
def exbar(q):
    p=pish(q); return q+(k+q)*p/(1-p)
cnt=0; best=None
for q in range(1,50):
    for qp in range(q,50):
        for j in range(0,51-q-qp):
            cnt+=1
            rhs=1-F(j,k)*(exbar(q)+exbar(qp))-(exbar(q)*(qp-1)+exbar(qp)*(q-1))/F(2*k)
            if best is None or rhs<best[0]: best=(rhs,q,qp,j)
print("count",cnt,"min",float(best[0]),best[1:])
# (2) n_X(2002)
print("2002^(4/3)=",2002**(4/3), "ceil", ceil(2002**(4/3)))
# (3) n_M ratios
print(20507/841**1.5, 73032/2000**1.5)
# (4) hermite error const
print(2e7*3.07/9**4)
# (5) polar-PD numbers
print(0.3**1.5/2, 2*exp(-5.3146*0.6996), 0.0821*exp(-3/25233), log(2/0.0820)/0.6996, 0.7*2001/2002)
# (6) C*M^1.5
for M,C in [(120,.54),(250,.593),(300,.522),(450,.548),(700,.519)]: print(M,C,C*M**1.5)
# (7) integer-strips counts
a=sum(2*k-19960 for k in range(9981,10000))+1100*40
b=sum(2*k-19898 for k in range(9950,9980))+2020*62
c=44*1000+23*1000+7*1000
print("strips",a,b,c,b+c)
# (8) (7.3)/(7.2) small check vs brute force: A_{n,k-1}, E[Z], E[H], E[Z(Z-1)] under capacity-weighted law
from itertools import permutations
def caps(sig):
    n=len(sig); h=[]
    for i in range(n):
        j=i-1
        while j>=0 and sig[j]<sig[i]: j-=1
        h.append(i-j)
    return h
def brute(n,k):
    A=0;Z=0;H=0;ZZ=0
    for sig in permutations(range(1,n+1)):
        h=caps(sig); w=1
        for x in h: w*=min(x,k)
        z=sum(1 for x in h if x>k); hh=sum(1 for x in h if x==k)
        A+=w; Z+=w*z; H+=w*hh; ZZ+=w*z*(z-1)
    return A,F(Z,A),F(H,A),F(ZZ,A)
def rec(n,k):
    a=[F(1)]; Zf=[F(0)]; ZH=[F(0)]; Zz=[F(0)]
    for m in range(1,n+1):
        s=sum(min(p,k)*a[p-1]*a[m-p] for p in range(1,m+1)); a.append(s/m)
        P=[min(p,k)*a[p-1]*a[m-p]/(m*a[m]) for p in range(1,m+1)]
        Zf.append(sum(P[p-1]*((1 if p>k else 0)+Zf[p-1]+Zf[m-p]) for p in range(1,m+1)))
        ZH.append(sum(P[p-1]*((1 if p==k else 0)+ZH[p-1]+ZH[m-p]) for p in range(1,m+1)))
        Zz.append(sum(P[p-1]*(Zz[p-1]+Zz[m-p]+2*Zf[p-1]*Zf[m-p]+2*(1 if p>k else 0)*(Zf[p-1]+Zf[m-p])) for p in range(1,m+1)))
    from math import factorial
    return a[n]*factorial(n),Zf[n],ZH[n],Zz[n]
for n,k in [(6,2),(7,3),(7,2),(8,3)]:
    print(n,k,brute(n,k)==rec(n,k), brute(n,k))
# (9) x_k identity: k*k^(k-2)/(k+1)^(k-1) == (k/(k+1))^(k-1)
print(F(5*5**3,6**4)==F(5,6)**4)
