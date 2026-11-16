import math
from fractions import Fraction
# --- theorem-W (나)
k=3131
print("D_k(2) at 3131:",0.08329*math.sqrt(k)-2-42.14/k)
print("right endpoint bound at 3131:",0.33316*(k**0.5-2*k**(1/6)+k**(-1/6))-1.0005*k**(1/3)-1.0145)
print("deriv at 3131:",0.33316*(3*k**(1/3)-2-k**(-1/3))-2.001*k**(1/6))
n=2*k+1; i_n=n*math.log(n/(n+1))+1; print("e^-i_n at 6263:",math.exp(-i_n))
# Borel sum via logs
def logbor(d): return -d+(d-1)*math.log(d)-math.lgamma(d+1)
S=sum(math.exp(logbor(d)) for d in range(1,302)); print("sum Bor(1..301):",S,"1-0.8/sqrt301:",1-0.8/math.sqrt(301))
print("0.9538/0.398943:",0.9538/0.398943)
# --- threshold-unit-ratio
k=6667; j0=math.floor(0.3*k)
val=(0.3*k-1)*(0.3*k)/(2*(1.3*k+1)); print("val 6667:",val,"1+1.5logk-val:",1+1.5*math.log(k)-val)
print("e^0.3:",math.exp(0.3),"e^{3/2k}:",math.exp(3/(2*k)),"1.00023*1.34986:",1.00023*1.34986)
# --- rw identity check
def P(n,j):
    p=lambda m: (m+1)**(m-1) if m>=1 else 1
    return Fraction(j*math.comb(n-1,j-1)*p(j-1)*p(n-j),p(n))
def g(x): return (x-1)*math.log(1+1/x)
k,nu=5,3; n=2*k+nu
rw=lambda q: Fraction(k,k+1+q)*P(n,k+1+q)/P(n,k)
print("rw(nu)=",rw(nu))
ok=all(abs(float(rw(q+1)/rw(q))-math.exp(g(k+1+q)-g(k+nu-1-q)))<1e-12 for q in range(0,k+nu-1))
print("rw ratio identity:",ok)
# --- survival s_{2k+1}(k), s_{2k+1}(k+1), bracket of (7.23) at nu=1
def Acol(l,M):
    A=[Fraction(1)]
    for m in range(1,M+1):
        s=0
        for j in range(1,m+1):
            s+=math.comb(m-1,j-1)*min(j,l+1)*A[j-1]*A[m-j]
        A.append(Fraction(s))
    return A
for k in (20,40,80,120):
    M=2*k+1
    Akm1=Acol(k-1,M); Ak=Acol(k,M); Akm2=Acol(k-2,M)
    p=lambda m:(m+1)**(m-1) if m>=1 else 1
    s=lambda A,m: A[m]/p(m)
    sn_k=float(s(Akm1,M)); sn_k1=float(s(Ak,M))
    c_k1=float(s(Akm1,k+1)-s(Akm2,k+1))  # c_{k+1}(k-1)
    br=c_k1+float(s(Ak,k+1))-sn_k-sn_k1
    print(f"k={k}: s_{{2k+1}}(k)={sn_k:.4f} s_{{2k+1}}(k+1)={sn_k1:.4f} s_{{2k-1}}(k)={float(s(Akm1,2*k-1)):.4f} bracket(nu=1)={br:.4f}")
