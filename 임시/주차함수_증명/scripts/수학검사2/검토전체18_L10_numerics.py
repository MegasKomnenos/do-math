# L10 검산: 10.5–10.6절의 명시 함수 값(DDL♮, j1, j2, check-na 표, check-ga 표). 배정밀도 평가(검토용).
import math
try:
    import mpmath as mp
    HAVE_MP=True
except Exception:
    HAVE_MP=False
SQ2PI=1/math.sqrt(2*math.pi)
def simpson(f,a,b,n=20000):
    if n%2: n+=1
    h=(b-a)/n; s=f(a)+f(b)
    for i in range(1,n):
        s+= (4 if i%2 else 2)*f(a+i*h)
    return s*h/3
def integ(f,a,b):
    if HAVE_MP:
        return float(mp.quad(lambda t: f(float(t)), [a,b]))
    return simpson(f,a,b)
# ---- 명제 old-8-23 ----
def q_(r): return 1+0.7501*r/(1+r)
j2=integ(lambda r: math.sqrt((1+r)/r)*0.70836*q_(r)**3, 1e-12, 1)
j1=integ(lambda r: math.sqrt((1+r)/r)*0.70836*q_(r)**3*(2.528571-math.log(q_(r))+1.5*math.log(r)), 1e-14, 1)
print("j2=%.7f j1=%.7f (본문: 2.7171998, 0.7998716)"%(j2,j1))
def DDL(k):
    d=2*k**(2/3)
    eps=-math.log(1-math.sqrt(k+1)/(0.485917*k))
    epsp=2.26/k+0.47/(d-1)
    gam=2.6047*(2.53+0.5*math.log(k)+eps+1.5/k)/k
    t1=0.457143*SQ2PI*q_(d/k)*math.sqrt(1+d/k)*(d+1)**3.5/k**3
    t2=2*SQ2PI*k**-0.5*(1+epsp)*(j1+(0.5*math.log(k)+eps)*j2+gam)
    t3=3.9*SQ2PI/k
    return t1+t2+t3
for k in (6667,6668,8065,9551,9705):
    print("DDL♮(%d)=%.6f"%(k,DDL(k)))
print("본문: 6668<0.13237, 8065<0.12234, 9551<0.11404, 9705<0.11329")
# ---- 상수들 ----
def u_(k): return (3/0.35)*(1.35+1/k)*(0.65-1/k)**-1.5*k**-0.5
def BdT(k,nu): return (k+nu)*u_(k)*(1/(k-1)+1/k)+3*(k+1)*(k-1)**-1.5
def sup(d,y): return min(1.0,1.15*(y+d)/d**1.5)
def ec(k,nu): return 3*nu**2/((k-1)*k)+4.8*math.sqrt(nu)/k+nu**2/(2*(k-1)**2)
def ebar(k):
    xi=(math.sqrt(5*k*math.log(k))+2)/k
    return math.exp(1.5/k)*(math.exp(math.sqrt(5*math.log(k)/k)+1/k)+2.40918*k**(1.5-2.5/(1+xi)))
def cAb(r): s=math.sqrt(r); return 2*s/(1-r)+2*math.log((1+s)/(1-s))
def Stays_up(k,nub):
    tot=0
    for y in (k-1,k):
        ab=(1.15*(y+2*y**(2/3)))**(2/3)
        Flat=2*(ab-1)/(y+2-ab)
        z=0.6+1/y
        xi=(nub+4)/(k-1)
        Sub=0 if xi>=0.6 else (k-1)/k*integ(lambda r:(r-xi)*(1+r)*r**-1.5*(1-r)**-2, xi,0.6)
        Ab=1.15*(1+1/y)*(4*((1.15*y)**(2/3)-1)**-0.5+y**-0.5*(2*cAb(z)-4*z**-0.5-Sub))
        tot+=Flat+Ab
    Top=integ(lambda r: min(2,2+(nub+1)/k-r)*(1+r/3)*r**-1.5, 0.6-2.6/k, 1)
    return tot+2*16.54*k**-0.5*Top
# check-na
k=6668
abar=3*1.15*(1.48*k+2)/(0.48*k+1)**1.5; bbar=BdT(k,k); dbar=72.217/math.sqrt(k)
print("벌크 k=6668: 4-ebar=%.5f (>2.9130?)  abar=%.5f bbar=%.5f DDL=%.5f dbar=%.5f sum=%.5f  좌변합=%.4f"%(4-ebar(k),abar,bbar,DDL(k),dbar,abar+bbar+DDL(k)+dbar, abar+bbar+DDL(k)+dbar+ebar(k)))
k=8065; th0=(2*math.exp(-0.48)-1)*math.exp(-0.48)
oF2=4-3*sup(2*k**(2/3)+1,k+1)+th0-BdT(k,0.48*k)-DDL(k)
print("가족2 k=8065: 3sup=%.5f th0=%.5f BdT=%.5f DDL=%.5f oF=%.5f Stays_up=%.5f"%(3*sup(2*k**(2/3)+1,k+1),th0,BdT(k,0.48*k),DDL(k),oF2,Stays_up(k,0.48*k)))
k=9551; xi2=2*k**(2/3)/(k-1); thb=(2*math.exp(-xi2)-1)*math.exp(-xi2)
oF1b=4-3*sup(1.3*k**(2/3)+1,k+1)+thb-BdT(k,2*k**(2/3))-DDL(k)
print("가족1b k=9551: 3sup=%.5f th=%.5f BdT=%.5f DDL=%.5f oF=%.5f Stays_up=%.5f"%(3*sup(1.3*k**(2/3)+1,k+1),thb,BdT(k,2*k**(2/3)),DDL(k),oF1b,Stays_up(k,2*k**(2/3))))
k=9705
oF1a=2-ec(k,1.3*k**(2/3))-BdT(k,1.3*k**(2/3))-DDL(k)
print("가족1a k=9705: ec=%.5f BdT=%.5f DDL=%.5f oF=%.5f Stays_up=%.5f"%(ec(k,1.3*k**(2/3)),BdT(k,1.3*k**(2/3)),DDL(k),oF1a,Stays_up(k,1.3*k**(2/3))))
# ---- check-ga ----
def logBor(m): return -m+(m-1)*math.log(m)-math.lgamma(m+1)
def Bor(m): return math.exp(logBor(m))
def s_chain(y,Q):
    # 𝔰_q(y), q=1..Q (q<=y+2), 사슬 재귀
    s=[0.0]*(Q+2); s[1]=1.0
    lb=[logBor(y+q) for q in range(0,Q+2)]
    for q in range(2,Q+1):
        acc=0.0
        for qp in range(1,q):
            P=Bor(q-qp)*math.exp(lb[qp]-lb[q])
            acc+=P*(1-(y/(y+qp))*s[qp])
        s[q]=1-acc
    return s
f1=4/(3*math.sqrt(2*math.pi))
def slow(d,y): return math.exp(-f1*((y+d-1)/y)**1.5*d**1.5/y)
cR=math.sqrt(2*math.pi)/2*math.exp(1/12)
def Qf(y,xi):
    k=y-1; q0=xi*y**(2/3)
    pref=k/(k+1)*(1-q0/(2*k))*2*SQ2PI*math.exp(-1/12)*y/(cR*q0)
    A=math.exp(-q0/y)*slow(q0,y)*(math.exp(-cR*q0/y)-math.exp(-cR*q0*math.sqrt(q0/2)/y))
    B=math.exp(-q0/(2*y))*slow(q0/2,y)*(math.exp(-cR*q0*math.sqrt(q0/2+1)/y)-math.exp(-cR*q0**1.5/y))
    return pref*(A+B)
def PrBorGe(q):  # Σ_{j>=q} Bor(j)
    return 1-sum(Bor(j) for j in range(1,q))
fam={'벌크':(6668,None),'2':(8065,0.48),'1b':(9551,2.0),'1a':(9705,1.3)}
for name,(k0,phi) in fam.items():
    y=k0+1; eps0=math.floor(2**(2/3)*(k0+1)**(2/3))
    sy=s_chain(y,eps0+2); sk=s_chain(k0,eps0+2)
    if name=='벌크':
        Rs=abar+bbar+DDL(k0)+dbar; Rsp=None
    else:
        nub=phi*k0 if name=='2' else phi*k0**(2/3)
        Su=Stays_up(k0,nub)
        if name=='1a': Rs=3+BdT(k0,1.3*k0**(2/3))+DDL(k0)+Su
        elif name=='1b': Rs=3*sup(1.3*k0**(2/3)+1,y)+BdT(k0,2*k0**(2/3))+DDL(k0)+Su
        else: Rs=3*sup(2*k0**(2/3)+1,y)+BdT(k0,0.48*k0)+DDL(k0)+Su
        Rsp=BdT(k0,nub)+DDL(k0)+Su if name in('1a','1b') else None
    cum=[0.0]*(eps0+3)
    for j in range(1,eps0+3): cum[j]=cum[j-1]+Bor(j)
    best=None; bestp=None
    for q0 in range(2,eps0+1):
        zR=0.0
        for q in range(1,q0):
            l=q0-q
            Ren_s=SQ2PI*l**-0.5*math.exp(-1/(12*l))
            Aup=math.sqrt(2*math.pi)/4*math.exp(1/(12*l))*(q0+q)*math.sqrt(l)
            zR+=Ren_s*math.exp(-(q+Aup)/y)*sy[q]
        prge=1-cum[q0-1]
        eR=k0/(k0+1)*(1-q0/(2*k0))*(max(zR,sy[q0]-prge)+Bor(q0))
        elow=4*sk[q0+1]+2*eR
        m=elow-Rs
        if best is None or m<best[0]: best=(m,q0)
        if Rsp is not None and q0>=104:
            mp_=eR+sk[q0+1]-Rsp
            if bestp is None or mp_<bestp[0]: bestp=(mp_,q0)
    xic=1.3 if name=='1a' else 2**(2/3)
    b=4*slow(xic*(k0+1)**(2/3)+1,k0)+2*Qf(y,xic)-Rs
    out="가족%s k0=%d eps0=%d R#=%.4f (a)min=%+.3f(q0=%d) (b)=%+.3f"%(name,k0,eps0,Rs,best[0],best[1],b)
    if Rsp is not None:
        bp=Qf(y,2**(2/3))+slow(2**(2/3)*(k0+1)**(2/3)+1,k0)-Rsp
        out+="  R#'=%.4f (a)'min=%+.3f(q0=%d) (b)'=%+.3f"%(Rsp,bestp[0],bestp[1],bp)
    print(out)
