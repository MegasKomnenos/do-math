# N6 검산: 장7A의 수치·부등식 재계산 (정확 유리수 + 고정밀 decimal + 작은 n 전수 검사)
from fractions import Fraction as Fr
from decimal import Decimal, getcontext
from math import factorial, log, exp, sqrt, ceil, comb
from itertools import permutations
getcontext().prec = 60
out = []
def P(*a): out.append(" ".join(str(x) for x in a))

# (a) column-lemma (가)
P("(a) 10^21*400^10 > 17^21*123^10 :", 10**21*400**10 > 17**21*123**10)
P("    (40/41)(10/17)^2.1 =", (40/41)*(10/17)**2.1, "> 0.3 ?", (40/41)*(10/17)**2.1 > 0.3)
P("    hf'(1.7) lower bound 1-2.1*(10/17)^3 =", 1-2.1*(10/17)**3)
P("    2(k+1)/(k-1) at k=41 =", 2*42/40)
P("    17^21=",17**21, "<6.95e25?",17**21<6.95e25, " 123^10=",123**10,"<7.93e20?",123**10<7.93e20, " 4^10*10^41>1.04e47?", 4**10*10**41>1.04e47)

# (b) self-consistent-S constants
def a0(m):
    return Fr(m+1)**(m-1)/factorial(m)
def g_exp(m):
    return Fr(m+2, m+1)**m
E = Decimal(1).exp()
def dec(fr): return Decimal(fr.numerator)/Decimal(fr.denominator)
ranges = [(Fr(267,100),25,501,Fr(13,100),"1"),(Fr(27,10),70,1855,Fr(2,25),"2"),(Fr(271,100),100,6098,Fr(11,200),"3")]
for L,J,k0,y,name in ranges:
    jf = max(m for m in range(0,3000) if (1+1/(m+1))**m < float(L)-1e-9 or (abs((1+1/(m+1))**m-float(L))<1e-6 and g_exp(m) < L))
    assert g_exp(jf) < L and not (g_exp(jf+1) < L)
    jstar = jf
    kR = max(2*jstar+2, ceil(L**(jstar+2)/a0(jstar+1)))
    from math import lgamma
    Ebar = Decimal(sum(exp((J+i-1)*log(J+i+1)-(J-1)*log(J+1)+lgamma(J+1)-lgamma(J+i+1)-i) for i in range(1,k0-jstar+1)))
    Le = dec(L)/E
    Einf = Le*(1-Le**k0)/(1-Le)
    RJ = max(1/(1+Ebar), 1/(1+Einf))
    RJq = Fr(int((RJ*Decimal(10**12)).to_integral_value(rounding="ROUND_CEILING")), 10**12)
    xk0 = Fr(k0, k0+1)**(k0-1)
    Xi = Fr(0); Xik = Fr(0)
    for kap in range(J):
        fall = a0(kap)*L**(-(kap+1))
        q = max(Fr(0), 1 - sum(a0(j)*L**(-(j+1)) for j in range(kap)))
        Xi += max(Fr(0), fall - RJq*q)
        Xik += max(Fr(0), a0(kap)*xk0*L**(-kap) - RJq*q)
    A0 = xk0 + Xik/(L*(1-Xi))
    B0 = RJq*(1+Xik/(1-Xi))
    xi = Fr(1,k0)
    val = (y-xi)*(y-2*xi-xi*xi) - (1+xi)**2*(A0*xi+B0*y)
    vert = (3*xi+xi*xi)/2 + (1+xi)**2*B0/2
    P(f"(b) range {name}: j*={jstar} kR={kR} RJ={RJ:.10f} Xi={float(Xi):.6f} Xi(k0)={float(Xik):.6f} A0={float(A0):.5f} B0={float(B0):.6f} corS-value={float(val):.4e} vertex={float(vert):.5f} <= y={float(y)} ? {vert<=y}  y*k0^2-2k0-1>0? {y*k0*k0-2*k0-1>0}")

# (c) t_k, n♯_k, n♭_k
def tk(k):
    j=0
    while not ((k+1)**j*k**(j+1)+(k-1)**(2*j+1) >= 2*k**(2*j+1)): j+=1
    return j
def phi(k,n):
    ms = Fr(n-k,k+1); x = Fr(k,k+1)**(k-1)
    return (1+1/k)**float(ms) + (1-1/k)**float(ms + x*n/k) - 2
for k in [2,3,5,10,41,100,501,2001]:
    t = tk(k); nsh = k+(k+1)*t
    nfl = next(n for n in range(2*k+1, nsh+1) if phi(k,n) >= 0)
    P(f"(c) k={k}: t_k={t} (1<=t<=k {1<=t<=k}) n#={nsh} n♭={nfl}  phi(2k+1)={phi(k,2*k+1):.4g}<0  phi(n#)={phi(k,nsh):.4g}>=0  n♭<=n#:{nfl<=nsh}  t_k/k={t/k:.3f}")
k=2001; nc = ceil(2*k**1.5)
P("(c) k=2001: n°=",nc," phi(n°)=",phi(k,nc)," 2k^1.5+1 =",2*k**1.5+1," 0.3476k^2=",0.3476*k*k, " e^{-1+2/2002}=",exp(-1+2/2002), " 2/sqrt(2001)=",2/sqrt(2001), " 0.75/sqrt(2001)=",0.75/sqrt(2001))
P("    0.955*0.991*0.3678=",0.955*0.991*0.3678, " exp(-0.0448)=",exp(-0.0448), " 8.344/sqrt(1e7)=",8.344/sqrt(1e7), " (1+0.91/sqrt(1e7))^3*8=",8*(1+0.91/sqrt(1e7))**3, " 0.3683*(2/sqrt(2001)+1/2001^2)=",0.3683*(2/sqrt(2001)+1/2001**2))

# (d) brute force small cases
def caps(s):
    n=len(s); h=[]
    for i in range(n):
        j=i-1
        while j>=0 and s[j]<s[i]: j-=1
        h.append(i-j)
    return h
def A_sigma(h,ell):
    r=1
    for x in h: r*=min(x,ell+1)
    return r
def Anl(n,ell):
    if n==0: return 1
    if ell<0: return 0
    return sum(A_sigma(caps(s),ell) for s in permutations(range(1,n+1)))
def conv_piece(W,k,lo,expo_fn):
    tot=Fr(0)
    for h,_ in W:
        c=1
        for x in h:
            if (lo==0 and x<=k) or (lo==-1 and x<=k-1): c*=x
        m=expo_fn(h)
        if m>=2:
            s=Fr(0)
            for i in range(m-1):
                co=comb(m-2,i)*k**(m-2-i)
                if lo==0:
                    s+=co*(Fr(1,i+1)-Fr(1,i+2))
                else:
                    s+=co*((-1)**i)*(Fr(1,i+1)-Fr(1,i+2))
            tot+=c*m*(m-1)*s
    return tot
bad=[]
for n in range(1,8):
    for k in range(2,n+1):
        perms=list(permutations(range(1,n+1)))
        W=[(caps(s),A_sigma(caps(s),k-1)) for s in perms]
        tot=sum(w for _,w in W)
        EZ=Fr(sum(w*sum(1 for x in h if x>k) for h,w in W),tot)
        EZZ=Fr(sum(w*sum(1 for x in h if x>k)*(sum(1 for x in h if x>k)-1) for h,w in W),tot)
        EkH=Fr(sum(w*k*sum(1 for x in h if x==k) for h,w in W),tot)
        ms=Fr(n-k,k+1)
        if EZ < ms: bad.append(("6-6",n,k))
        if n>=2*k+1 and EZZ < ms*(ms-1): bad.append(("fm",n,k))
        xk=Fr(k,k+1)**(k-1)
        if EkH > xk*n: bad.append(("6-10",n,k))
        if n==k and EkH != xk*n: bad.append(("6-10eq",n,k))
        Rs=Fr(Anl(n,k),Anl(n,k-1)); Rf=Fr(Anl(n,k-2),Anl(n,k-1))
        ok=float(Rf) > (1-1/k)*float(Rs)**(-(-2*log(1-1/k)/log(1+1/k)))  # R♭ > x♭ (R♯)^{-𝔬_k}
        if not ok: bad.append(("6-7",n,k))
        d=Anl(n,k)-2*Anl(n,k-1)+Anl(n,k-2)
        Kink=Fr(sum(w*sum(1 for x in h if x==k) for h,w in W),k)
        Conv=conv_piece(W,k,0,lambda h: sum(1 for x in h if x>k))+conv_piece(W,k,-1,lambda h: sum(1 for x in h if x>=k))
        if Conv-Kink != d: bad.append(("6-5",n,k,Conv,Kink,d))
        # 모멘트 판정: d >= T_{n,k}/k^2
        T=sum(w*(sum(1 for x in h if x>k)*(sum(1 for x in h if x>k)-1)-k*sum(1 for x in h if x==k)) for h,w in W)
        if Fr(d) < Fr(T,k*k): bad.append(("6-4",n,k))
P("(d) brute-force violations (n<=7):", bad if bad else "none")
k=3; z=1; n=2
lhs=sum(A_sigma(caps(s),k-1)*sum(1 for x in caps(s) if x==z) for s in permutations(range(1,n+1)))
P("(d) riccati counterexample LHS n![x^n]Y_1 =",lhs," (text: 4; RHS claimed 5)")
def check_611(k,N):
    a=[Fr(Anl(m,k-1),factorial(m)) for m in range(N+2)]
    a0s=[Fr(m+1)**(m-1)/factorial(m) for m in range(N+2)]
    K=[Fr(0)]*(N+3)
    for j in range(1,N+3):
        s=sum((k-m)*a0s[m-1]*K[j-m] for m in range(1,k) if j-m>=0)
        if j==k+1: s+=1
        K[j]=s/j
    res=[]
    for n in range(1,N+1):
        perms=list(permutations(range(1,n+1)))
        W=[(caps(s),A_sigma(caps(s),k-1)) for s in perms]
        EH=Fr(sum(w*sum(1 for x in h if x==k) for h,w in W),sum(w for _,w in W))
        rhs=(n+1)*a[k-1]*sum(K[j]*a[n+1-j] for j in range(k+1,n+2))/a[n]
        res.append(EH==rhs)
    return res
P("(d) old-6-11(가) k=2,n<=7:",check_611(2,7)," k=3,n<=7:",check_611(3,7))
# prime parking function counts C_{n,n}=(n-1)^(n-1) brute force
def is_pf(a):
    n=len(a); return all(sum(1 for x in a if x<=i)>=i for i in range(1,n+1))
def is_prime(a):
    n=len(a); return all(sum(1 for x in a if x<=b)!=b for b in range(1,n))
from itertools import product
for n in range(1,6):
    cnt=sum(1 for a in product(range(1,n+1),repeat=n) if is_pf(a) and is_prime(a))
    P(f"(d) C_{n},{n} brute={cnt} formula={(n-1)**(n-1)}")
# A_{n,1} vs 1/(2-e^x) and rho_2=log 2 sanity; k=1 claim b_{n,1} >= (n-1) n!/2
for n in range(2,8):
    b1=Anl(n,1)-Anl(n,0)
    P(f"(d) n={n}: b_(n,1)={b1} >= (n-1)n!/2={(n-1)*factorial(n)//2} ? {b1>=(n-1)*factorial(n)//2}")
open(r"C:\math\임시\주차함수_증명\scripts\수학검사2\검토전체20_N6_numerics_out.txt","w",encoding="utf-8").write("\n".join(out))
print("\n".join(out))
