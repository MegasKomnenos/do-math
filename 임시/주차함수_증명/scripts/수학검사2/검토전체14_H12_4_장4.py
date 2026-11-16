# H12 검산 4: 부록 D 4장 항목
import math, itertools, time
from fractions import Fraction as Fr
import mpmath as mp
t0=time.time()
def caps(sigma):
    n=len(sigma); h=[]
    for i in range(1,n+1):
        m=0
        for j in range(1,i):
            if sigma[j-1]>sigma[i-1]: m=j
        h.append(i-m)
    return h
def p(n): return (n+1)**(n-1) if n>=1 else 1
# --- brute force e_n, J_n(k-1), K'(k)
def brute(n,k):
    e=0; J=0; Kp=0; A=0
    for s in itertools.permutations(range(1,n+1)):
        h=caps(s); Z=sum(1 for x in h if x>k); H=sum(1 for x in h if x==k)
        base=1
        for x in h:
            if x<=k: base*=x
        baseJ=1
        for x in h:
            if x<k: baseJ*=x
        # K(y)=base*y^Z ; K''(k)=base*Z(Z-1)k^(Z-2); K'(k)=base*Z*k^(Z-1)
        if Z>=2: e+=base*Z*(Z-1)*k**(Z-2)
        if Z>=1: Kp+=base*Z*k**(Z-1)
        A+=base*k**Z
        if H>=1: J+=H*k**(H-1)*(k-1)**Z*baseJ
    return e,J,Kp,A
# --- polynomial recurrence for K_{n,k}(y): list of coefficients
def K_poly_all(N,k):
    # K[n] = list coeffs in y
    K=[[1]]
    def padd(a,b):
        m=max(len(a),len(b)); return [(a[i] if i<len(a) else 0)+(b[i] if i<len(b) else 0) for i in range(m)]
    def pmul(a,b):
        r=[0]*(len(a)+len(b)-1)
        for i,x in enumerate(a):
            if x:
                for j,y in enumerate(b): r[i+j]+=x*y
        return r
    def psc(a,c): return [c*x for x in a]
    for n in range(1,N+1):
        acc=[0]
        for j in range(n):
            w = [j+1] if j+1<=k else [0,1]   # weight g or y
            term=pmul(pmul(w,K[j]),K[n-1-j]); term=psc(term,math.comb(n-1,j))
            acc=padd(acc,term)
        K.append(acc)
    return K
def evalp(c,y): return sum(ci*y**i for i,ci in enumerate(c))
def d1(c): return [i*c[i] for i in range(1,len(c))]
def J_all(N,k):
    J=[0]*(N+1)
    for n in range(0,N):   # J_{n+1}
        if n+1>2*k: break
        s=0
        for i in range(0,n+1):
            if J[n-i]: s+=math.comb(n,i)*(k-1+i+1)*p(i)*J[n-i]
        if n>=k-1: s+=math.comb(n,k-1)*p(k-1)*p(n-k+1)
        J[n+1]=s
    return J
print("--- brute vs recurrence (n<=8) ---")
for n in range(2,9):
    k=(n+1)//2
    e,J,Kp,A=brute(n,k)
    K=K_poly_all(n,k); Jr=J_all(n,k)
    er=evalp(d1(d1(K[n])),k); Kpr=evalp(d1(K[n]),k); Ar=evalp(K[n],k)
    print(n,k,"e",e,er,"J",J,Jr[n],"K'",Kp,Kpr,"A",A,Ar, "OK" if (e,J,Kp,A)==(er,Jr[n],Kpr,Ar) else "<<MISMATCH")
# --- rows via last-car recurrence up to N=300 (columns 0..152)
N=300
cols={}
for l in range(0,153):
    col=[1]
    for n in range(1,N+1):
        s=0
        for j in range(n):
            s+=math.comb(n-1,j)*min(j+1,l+1)*col[j]*col[n-1-j]
        col.append(s)
    cols[l]=col
def A_(n,l):
    if l<0: return 0
    if l>=n-1: return p(n)
    return cols[l][n]
def b(n,l): return A_(n,l)-A_(n,l-1)
print("rows done",round(time.time()-t0,1))
# (ㄱ) e_n > J_n(k-1) for 16<=n<=60 and ratio
print("--- (ㄱ) small n ---")
minratio=None
for n in range(2,61):
    k=(n+1)//2
    K=K_poly_all(n,k); Jr=J_all(n,k)
    e=evalp(d1(d1(K[n])),k); J=Jr[n]
    d=b(n,k)-b(n,k-1)
    assert d>=e-J, n
    if n>=16:
        assert e>J, n
        r=Fr(e,J)
        if minratio is None or r<minratio[1]: minratio=(n,r)
    if n in (16,17,18,20,30,60): print(n,k,"e/J=%.8f"%(e/J),"d=%d e-J=%d"%(d,e-J), "e>J" if e>J else "e<=J")
    if n<16: 
        if e>J: print("  n<16 with e>J:",n)
print("min ratio 16..60 at n=",minratio[0],"=%.8f"%float(minratio[1]))
# --- four normalized recurrences (D 식) exact Fractions, compare
print("--- D 식 네 재귀 (k<=25) ---")
S=2918732888; s=Fr(S,2**30)
print("S=",S," floor(e*2^30)=",math.floor(mp.e*2**30), " s-e=",float(s-Fr(str(mp.e))) if False else float(s)-math.e)
def r_(i): return Fr(p(i), math.factorial(i)*s**i) if i>=1 else Fr(1)
for k in (3,4,5,8,12,25):
    N2=2*k
    A={i:r_(i) for i in range(0,k+1)}; dd={i:Fr(0) for i in range(0,k+1)}; z={i:Fr(0) for i in range(0,k+1)}
    jj={i:Fr(0) for i in range(0,k)}; jj[k]=r_(k-1)/(s*k)
    for n in range(k+1,N2+1):
        r=n-k
        A[n]=(sum((k+i+1)*r_(i)*A[n-1-i] for i in range(0,r-1))+sum(min(i+1,k)*r_(i)*r_(n-1-i) for i in range(r-1,k+1)))/(s*n)
        dd[n]=(sum((k+i+1)*r_(i)*dd[n-1-i] for i in range(0,r-1))+sum(r_(i)*A[n-1-i] for i in range(0,r)))/(s*n)
        z[n]=(sum((k+i+1)*r_(i)*z[n-1-i] for i in range(0,r-1))+2*sum(r_(i)*dd[n-1-i] for i in range(0,r-1)))/(s*n)
        jj[n]=(sum((k+i)*r_(i)*jj[n-1-i] for i in range(0,r))+r_(k-1)*r_(n-k))/(s*n)
    K=K_poly_all(N2,k); Jr=J_all(N2,k); ok=True
    for n in range(k+1,N2+1):
        nn=math.factorial(n)*s**n
        tA=Fr(evalp(K[n],k))/nn; td=Fr(evalp(d1(K[n]),k))/nn; tz=Fr(evalp(d1(d1(K[n])),k))/nn; tj=Fr(Jr[n])/nn
        if (A[n],dd[n],z[n],jj[n])!=(tA,td,tz,tj):
            ok=False; print("  k",k,"n",n,"MISMATCH",A[n]==tA,dd[n]==td,z[n]==tz,jj[n]==tj)
    print("k",k,"recurrences match" if ok else "recurrences MISMATCH", " init j_k ok:", jj[k]==Fr(Jr[k])/(math.factorial(k)*s**k))
# (ㄴ)
print("--- (ㄴ) ---")
neg=[n for n in range(2,61) if b(n,(n+1)//2)-b(n,(n+1)//2-1)<0]
print("d_{n,k_n}<0 for n in", neg)
for n in range(2,16):
    k=(n+1)//2
    assert all(b(n,j)>=b(n,j+1) for j in range(k,n-1)), n
print("right half nonincreasing for 2<=n<=15: True")
# Q_L
print("--- Q_L(n) 3<=n<=15 ---")
for n in range(3,16):
    ok=True
    for l in range(0,n-2):
        if 2*l<=n-2 and b(n,l)>b(n,l+1):
            if not b(n,l+1)**2>=b(n,l)*b(n,l+2): ok=False
    assert ok, n
print("Q_L holds 3..15")
# decreasing levels, strict LC after decrease, n<=300
cnt=0; viol=0; nonstrict=0
for n in range(1,154):
    for l in range(0,n-2):
        if b(n,l)>b(n,l+1):
            cnt+=1
            x=b(n,l+1)**2-b(n,l)*b(n,l+2)
            if x<0: viol+=1
            if x==0: nonstrict+=1
    # strict unimodal, no adjacent ties
    row=[b(n,l) for l in range(n)]
    assert all(row[i]!=row[i+1] for i in range(n-1)), ("tie",n)
print("n<=153: decreasing levels(l<=n-3)",cnt,"LC violations",viol,"equalities",nonstrict)
# crossing
print("--- crossing b_{n,k_n}<b_{n,k_n+1} ---")
false_n=[n for n in range(5,N+1) if not b(n,(n+1)//2)<b(n,(n+1)//2+1)]
print("false for n in", false_n)
# A^c recurrence check n<=60
def Ac(n,l): return p(n)-A_(n,l)
bad=0
for l in range(0,30):
    for n in range(l+2, min(2*l+4,60)+1):
        rhs=sum(math.comb(n-1,j)*(j-l)*p(j)*p(n-1-j) for j in range(l+1,n))
        rhs+=sum(Ac(i,l)*math.comb(n-1,i)*p(n-1-i)*((l+1)+min(n-i,l+1)) for i in range(l+2,n))
        if rhs!=Ac(n,l): bad+=1
print("A^c recurrence mismatches (l<30,n<=min(2l+4,60)):",bad)
# constants
mp.mp.dps=30
a0=mp.quad(lambda w: mp.e**(-w**3/3),[0,mp.inf]); a1=mp.quad(lambda w: w*mp.e**(-w**3/3),[0,mp.inf])
print("a0",a0,"a1",a1, " 3^(-2/3)Gamma(1/3)=",mp.mpf(3)**(-mp.mpf(2)/3)*mp.gamma(mp.mpf(1)/3))
print("tail e^{-64/3}/16=",mp.e**(-mp.mpf(64)/3)/16, " actual tail0=",mp.quad(lambda w: mp.e**(-w**3/3),[4,mp.inf]), " tail1=",mp.quad(lambda w: w*mp.e**(-w**3/3),[4,mp.inf]), " bound/4=",mp.e**(-mp.mpf(64)/3)/4)
print("sum G=1/16:",176+2304+118+935+533+455+243, " sum G=1/8:", round(183.51+2303.07+203.57+983.74+920.70+454.86+418.83,2))
print("495594511/240250000=",495594511/240250000, " assembly:",5.642*1.6809*0.39893-0.0163-3.554)
print("k^5 e^{-k/520} k=30000:", mp.mpf(30000)**5*mp.e**(-mp.mpf(30000)/520))
print("time",round(time.time()-t0,1))
