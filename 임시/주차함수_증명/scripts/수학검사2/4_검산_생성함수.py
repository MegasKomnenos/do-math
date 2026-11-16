# -*- coding: utf-8 -*-
"""4장 보조정리 e-integral (4.1), (4.3), 명제 4.6, (4.4)·(4.5)·(4.6)·(4.12)·(4.13)과
부록 D 네 항목의 재귀를 작은 k에서 정확 계산·수치로 검산한다 (수학검사2, 태그 4).
python -I scripts/수학검사2/4_검산_생성함수.py
"""
import itertools, math
from fractions import Fraction as Fr
import mpmath as mp
mp.mp.dps = 30
out = []
def P(*a):
    s = " ".join(str(x) for x in a); print(s); out.append(s)

def p(j): return (j+1)**(j-1) if j>=1 else 1
def caps(sigma):
    n=len(sigma); h=[]
    for i in range(n):
        d=i+1
        for t in range(i-1,-1,-1):
            if sigma[t]>sigma[i]: d=i-t; break
        h.append(d)
    return h

# ---------- 브루트포스: K_{n,k}(y)의 계수, A, K', K'', J_n(z) ----------
def brute(n,k):
    """returns dict: A=K(k), Kp=K'(k), Kpp=K''(k), J=J_n(k-1), and rows b_{n,l} via sigma-caps"""
    A=Kp=Kpp=J=0
    for sigma in itertools.permutations(range(1,n+1)):
        h=caps(sigma)
        Z=sum(1 for x in h if x>k); H=sum(1 for x in h if x==k)
        base=1
        for x in h:
            if x<=k: base*=x
        # K(y)=base*y^Z ; derivatives at y=k
        A+=base*k**Z
        Kp+=base*(Z*k**(Z-1) if Z>=1 else 0)
        Kpp+=base*(Z*(Z-1)*k**(Z-2) if Z>=2 else 0)
        # J_n(z)=sum H k^{H-1} z^Z prod_{h<k} h
        if H>=1:
            pr=1
            for x in h:
                if x<k: pr*=x
            J+=H*k**(H-1)*(k-1)**Z*pr
    return dict(A=A,Kp=Kp,Kpp=Kpp,J=J)

def rows_exact(nmax):
    """b_{n,l} for n<=nmax via 정리 2-6: A_{n,l} recurrence (exact ints)"""
    A={}  # A[(n,l)]
    for l in range(0,nmax+1):
        A[(0,l)]=1
        for n in range(1,nmax+1):
            s=0
            for j in range(n):
                s+=math.comb(n-1,j)*min(j+1,l+1)*A[(j,l)]*A[(n-1-j,l)]
            A[(n,l)]=s
    b={}
    for n in range(1,nmax+1):
        b[n]=[A[(n,0)]]+[A[(n,l)]-A[(n,l-1)] for l in range(1,n)]
    return A,b

P("== 0. 브루트포스 vs 재귀 (작은 n) ==")
Aex,bex = rows_exact(60)
for n in range(1,9):
    k=(n+1)//2
    br=brute(n,k)
    P(f"n={n} k={k}: A={br['A']} (A_{{n,k-1}} rec={Aex[(n,k-1)]}) e_n=K''(k)={br['Kpp']} J_n(k-1)={br['J']} d={bex[n][k]-bex[n][k-1] if k<n else None}")

# ---------- 1. 부록 D.central-gap-integer 네 재귀 (s=1, 정확 유리수) ----------
P("== 1. 정수 인증 네 재귀 vs 브루트포스 ==")
def four_rec(k, nmax):
    r=lambda i: Fr(p(i), math.factorial(i))
    a={}; d={}; z={}; jj={}
    for i in range(0,k+1):
        a[i]=r(i); d[i]=Fr(0); z[i]=Fr(0)
    for i in range(0,k): jj[i]=Fr(0)
    jj[k]=r(k-1)/k
    for n in range(k+1, nmax+1):
        rr=n-k
        a[n]=(sum(((k+i+1)*r(i)*a[n-1-i] for i in range(0,rr-1)),Fr(0))+sum((min(i+1,k)*r(i)*r(n-1-i) for i in range(rr-1,k+1)),Fr(0)))/n
        d[n]=(sum(((k+i+1)*r(i)*d[n-1-i] for i in range(0,rr-1)),Fr(0))+sum((r(i)*a[n-1-i] for i in range(0,rr)),Fr(0)))/n
        z[n]=(sum(((k+i+1)*r(i)*z[n-1-i] for i in range(0,rr-1)),Fr(0))+2*sum((r(i)*d[n-1-i] for i in range(0,rr-1)),Fr(0)))/n
        jj[n]=(sum(((k+i)*r(i)*jj[n-1-i] for i in range(0,rr)),Fr(0))+r(k-1)*r(n-k))/n
    return a,d,z,jj
for k in (2,3,4):
    a,d,z,jj=four_rec(k,2*k)
    for n in range(k+1,2*k+1):
        if n>8: continue
        br=brute(n,k); f=math.factorial(n)
        P(f"k={k} n={n}: A rec={a[n]*f} brute={br['A']} | K' rec={d[n]*f} brute={br['Kp']} | e rec={z[n]*f} brute={br['Kpp']} | J rec={jj[n]*f} brute={br['J']}",
          "OK" if (a[n]*f==br['A'] and d[n]*f==br['Kp'] and z[n]*f==br['Kpp'] and jj[n]*f==br['J']) else "MISMATCH")
# J_k(k-1)=p_{k-1} 초기값 vs 브루트포스
for k in (2,3,4):
    P(f"J_k(k-1) brute k={k}:", brute(k,k)['J'], " p_{k-1}=", p(k-1))
# 16<=n<=60: e_n > J_n(k-1) ? and ratio at n=17 ; 2..15: d<0, right half nonincreasing
P("== 1b. 작은 행 사실 ==")
bad=[]
for n in range(2,61):
    k=(n+1)//2
    a,d,z,jj=four_rec(k,2*k)
    f=math.factorial(n); e=z[n]*f; J=jj[n]*f
    dn=bex[n][k]-bex[n][k-1]
    right_nonincr = all(bex[n][j]>=bex[n][j+1] for j in range(k,n-1))
    if n<=15:
        if not (dn<0 and right_nonincr): bad.append(n)
    else:
        if not (e>J and dn>0): bad.append(n)
    if n in (15,16,17,18,20000) or n<=4:
        P(f"n={n}: d={dn} e={e} J={J} e/J={float(Fr(e,J)) if J else None} right_nonincr={right_nonincr}")
P("2..15: d<0 & 오른쪽 비증가, 16..60: e>J & d>0 — 위반 n:", bad)
P("d_{1,1} (b_{1,1}:=0):", 0-bex[1][0])
# 확인: delta >= e - J (2-30 Xi)
P("n=16 (k=8, n=2k): J - B = Xi = C(15,7) p_7^2 ?", )
for n in (4,6,8):
    k=n//2; br=brute(n,k); dn=bex[n][k]-bex[n][k-1]
    # d = 2E - B ; B = J - Xi ; Xi = C(2k-1,k-1) p_{k-1}^2
    Xi=math.comb(2*k-1,k-1)*p(k-1)**2
    P(f"  n={n}: d={dn}, e-J={br['Kpp']-br['J']}, d>=e-J: {dn>=br['Kpp']-br['J']}, Xi={Xi}")

# ---------- 2. D.crossing-small-n 재귀 ----------
P("== 2. 미달 수 재귀 ==")
def Ac_rec(nmax, l):
    c={}
    for n in range(0,nmax+1):
        if n<=l+1: c[n]=0; continue
        s=sum(math.comb(n-1,j)*(j-l)*p(j)*p(n-1-j) for j in range(l+1,n))
        s+=sum(c[i]*math.comb(n-1,i)*p(n-1-i)*((l+1)+min(n-i,l+1)) for i in range(l+2,n))
        c[n]=s
    return c
false_n=[]; true_n=[]; mism=[]
for n in range(5,61):
    k=(n+1)//2
    # need b_{n,k}, b_{n,k+1}: c at levels k-1,k,k+1 ; valid for n<=2l+4
    cs={l:Ac_rec(n,l)[n] for l in (k-1,k,k+1)}
    bk=cs[k-1]-cs[k]; bk1=cs[k]-cs[k+1]
    if (bk,bk1)!=(bex[n][k],bex[n][k+1]): mism.append(n)
    (true_n if bk<bk1 else false_n).append(n)
P("재귀 vs 전체 재귀 불일치 n:", mism)
P("b_{n,k_n}<b_{n,k_n+1} 거짓인 n (5..60):", false_n, " 참인 n 수:", len(true_n), " 최소 참 n:", min(true_n))
P("p_n = sum C(n-1,j)(j+1)p_j p_{n-1-j} 확인 n=7:", p(7), sum(math.comb(6,j)*(j+1)*p(j)*p(6-j) for j in range(7)))

# ---------- 3. D.QL-small-n ----------
P("== 3. Q_L(n), 3<=n<=15 ==")
viol=[]; cnt=0
for n in range(3,16):
    for l in range(0,n-2):
        if 2*l<=n-2 and bex[n][l]>bex[n][l+1]:
            cnt+=1
            if not bex[n][l+1]**2>bex[n][l]*bex[n][l+2]: viol.append((n,l))
P("감소 위치 수:", cnt, " 위반:", viol)
# 전체 행 1..60: 단봉, 인접 동률 없음, 감소 위치 수
dec=0; ties=0; nonuni=0
for n in range(1,61):
    b=bex[n]
    ties+=sum(1 for i in range(n-1) if b[i]==b[i+1])
    decs=[i for i in range(n-1) if b[i]>b[i+1]]
    dec+=len(decs)
    if decs:
        i0=decs[0]
        if any(b[i]<b[i+1] for i in range(i0,n-1)): nonuni+=1
P("1..60: 비단봉 행", nonuni, " 인접 동률", ties, " 감소 위치", dec)
P("로그오목 처음 깨지는 n (<=60에서):", [n for n in range(1,61) if any(bex[n][l+1]**2<bex[n][l]*bex[n][l+2] for l in range(n-2))][:3])

# ---------- 4. (4.1), (4.3), 명제 4.6 수치 검산 (Lagrange 계수 = 단위원 Cauchy 적분) ----------
P("== 4. 생성함수 식 수치 검산 ==")
mp.mp.dps = 25
def Borj(j,Z): return mp.e**(-j*Z)*(j*Z)**(j-1)/mp.factorial(j)
def Bortail(k,Z): return 1-mp.fsum(Borj(j,Z) for j in range(1,k+1))
def Vf(x): return (1-x)**2/2
def Bor(k): k=mp.mpf(k); return mp.e**(-k)*k**(k-1)/mp.factorial(k)
def lagrange_coeff(gfun, n, M=96):
    """[Y^n] g(Y)(1-Y)e^{nY} via trapezoid on |Y|=1 (entire g)"""
    s=mp.mpc(0)
    for m in range(M):
        th=2*mp.pi*m/M; Y=mp.e**(1j*th)
        s+=gfun(Y)*(1-Y)*mp.e**(n*Y)*mp.e**(-1j*n*th)
    return s/M
def Phi(k,Y,upper=None):
    up = Y if upper is None else upper
    f=lambda Z: (1-Z)**2*Bortail(k,Z)*mp.e**(k*(Vf(Z)-Vf(Y)))*(2*(Vf(Z)-Vf(Y))+k*(Vf(Z)-Vf(Y))**2)
    return mp.e**Y*mp.quad(f,[0,up])
def Kfun(k,Y):
    f=lambda Z: (1-Z)*Z**(k-1)*mp.e**(k*(1-Z)+(k-1)*Vf(Z))
    return -Bor(k)*mp.e**Y*mp.e**(-(k-1)*Vf(Y))*mp.quad(f,[Y,1])
def Dfun(k,Y): return Phi(k,Y)-Phi(k,Y,upper=1)
def Hermite(n,y):
    N=n+y+1; He=[mp.mpf(1), mp.mpf(N)]
    for j in range(2,n+1): He.append(N*He[j-1]-(j-1)*y*He[j-2])
    return He
def Mr(r,y,n,k):
    He=Hermite(n,y); pn=mp.mpf(p(n))
    s=mp.fsum(mp.binomial(r+1,i)*(-1)**i*He[n-i]/mp.factorial(n-i) for i in range(0,r+2) if n-i>=0)
    return mp.factorial(n)/pn*mp.e**(-y/2)*s
def Mr_lagrange(r,y,n,k):
    return mp.factorial(n)/mp.mpf(p(n))*lagrange_coeff(lambda Y: mp.e**Y*mp.e**(-y*(1-Y)**2/2)*(1-Y)**r, n)
for k,n in ((3,5),(3,6),(4,7),(4,8)):
    br=brute(n,k); pn=p(n); f=math.factorial(n)
    c=lagrange_coeff(lambda Y: Phi(k,Y), n)
    P(f"(4.1) k={k} n={n}: [x^n]Phi(T) = {mp.nstr(c.real,15)} (im {mp.nstr(c.imag,3)}) vs e_n/n! = {mp.nstr(mp.mpf(br['Kpp'])/f,15)}")
    # 명제 4.6
    Ik=mp.quad(lambda v: v/(1-v)*mp.e**(-v**2/2)*mp.e**(-k*(-mp.log(1-v)-v-v**2/2)), [0,1])
    M0km1=Mr(0,k-1,n,k)
    bJ=mp.factorial(n)/mp.mpf(pn)*lagrange_coeff(lambda Y: Kfun(k,Y), n).real
    rhs=Bor(k)*Ik*M0km1+bJ
    P(f"(4.6) k={k} n={n}: J_n(k-1)/p_n = {mp.nstr(mp.mpf(br['J'])/pn,15)} vs Bor I_k M0^(k-1) + b_J = {mp.nstr(rhs,15)}  [Bor I M0={mp.nstr(Bor(k)*Ik*M0km1,10)}, bJ={mp.nstr(bJ,10)}]")
    # (4.3)
    Wi=[mp.quad(lambda v: mp.e**(k*v**2/2)*v**2*Bortail(k,1-v)*(v**2/2)**j,[0,1]) for j in range(3)]
    M=[Mr(r,k,n,k) for r in (0,1,2,3,4)]
    A43=(2*Wi[1]+k*Wi[2])*M[0]-(Wi[0]+k*Wi[1])*M[2]+mp.mpf(k)/4*Wi[0]*M[4]
    Adir=mp.factorial(n)/mp.mpf(pn)*lagrange_coeff(lambda Y: Phi(k,Y,upper=1), n).real
    bD=mp.factorial(n)/mp.mpf(pn)*lagrange_coeff(lambda Y: Dfun(k,Y), n).real
    P(f"(4.3) k={k} n={n}: A_{{k,n}} direct = {mp.nstr(Adir,15)} vs formula = {mp.nstr(A43,15)}; e_n/p_n={mp.nstr(mp.mpf(br['Kpp'])/pn,12)} vs A+b_D={mp.nstr(Adir+bD,12)}")
    P(f"(4.4) M_r Hermite vs Lagrange r=0,2,4:", [mp.nstr(Mr(r,k,n,k)-Mr_lagrange(r,k,n,k),3) for r in (0,2,4)], " M0^(k-1)<=M0:", M0km1<=M[0], " M2<0:", M[2]<0, " M4:", mp.nstr(M[4],6))
    # 첫째 단계 M0 = e^{-y/2} He_{n-1} vartheta / p_n
    He=Hermite(n,k); vt=He[n]/He[n-1]-n
    P(f"  M0 = e^-k/2 He_{{n-1}} vt/p_n: {mp.nstr(mp.e**(-mp.mpf(k)/2)*He[n-1]*vt/pn,12)} vs {mp.nstr(M[0],12)}; vt={mp.nstr(vt,8)}")
    # (4.9) 수치
    r49=(vt*((n-k)**2+n)-n*(n+1))/(mp.mpf(k)**2*vt)
    P(f"  (4.9) M2/M0 = {mp.nstr(M[2]/M[0],12)} vs {mp.nstr(r49,12)}")
# (4.5),(4.6) 복소점 확인
k=5
for Y in (mp.mpc(1,0.3), mp.mpc(0.6,-0.2)):
    kap=1-Y; mu=lambda r:1-r**2
    lhs=Dfun(k,Y)*(1-Y)
    rhs=-mp.e**Y*kap**4*mp.quad(lambda r: r**2*Bortail(k,1-r*kap)*mp.e**(-k*mu(r)*kap**2/2)*(-mu(r)*kap**2+mp.mpf(k)/4*mu(r)**2*kap**4),[0,1])
    lhsK=Kfun(k,Y)*(1-Y)
    rhsK=-Bor(k)*mp.e**Y*kap**3*mp.quad(lambda r: r*(1-r*kap)**(k-1)*mp.e**(k*r*kap-(k-1)*mu(r)*kap**2/2),[0,1])
    P(f"(4.5) Y={Y}: diff {mp.nstr(abs(lhs-rhs),3)} ; (4.6) diff {mp.nstr(abs(lhsK-rhsK),3)}")
# (4.12),(4.13) 피적분함수 점별 확인 (수직선)
P("== 5. (4.12)/(4.13) 피적분함수 점별 ==")
k=40
for nn in (2*k-1,2*k):
    eps=1/mp.sqrt(k); pn=mp.mpf(p(nn)); nfac=mp.factorial(nn)
    nk=nfac/pn*mp.e**(nn+1)/(2*mp.pi*mp.mpf(k)**1.5)
    Bn=Bor(k)*nfac/pn*mp.e**(nn+1)/(2*mp.pi)
    for z in (mp.mpf('0.7'), mp.mpf('1.9')):
        Y=1+1j*z*eps
        # 직접: (n!/p_n)(1/2pi i) D(Y)(1-Y) e^{nY} Y^{-n-1} dY, dY = i eps dz  -> integrand in z: (n!/p_n)(eps/2pi) D(1-Y)e^{nY}Y^{-n-1}
        direct_D = nfac/pn*eps/(2*mp.pi)*Dfun(k,Y)*(1-Y)*mp.e**(nn*Y)*Y**(-nn-1)*mp.mpf(k)**2.5
        direct_J = nfac/pn*eps/(2*mp.pi)*Kfun(k,Y)*(1-Y)*mp.e**(nn*Y)*Y**(-nn-1)*mp.mpf(k)**2.5
        Mag=(1+z**2/k)**(-(nn+1)/mp.mpf(2)); Ph=(nn+1)*(z*eps-mp.atan(z*eps))
        Pq=lambda r: (1-r**2)*z**2+(1-r**2)**2*z**4/4
        f412=-nk*z**4*Mag*mp.quad(lambda r: r**2*mp.e**((1-r**2)*z**2/2)*Pq(r)*mp.re(mp.sqrt(k)*Bortail(k,1+1j*r*z*eps)*mp.e**(1j*Ph)),[0,1])
        MagJ=Mag*mp.e**((k-1)*z**2/(2*k))
        Am=lambda r: mp.e**(-(k-1)*(r**2*z**2/(2*k)-mp.log(1+r**2*z**2/k)/2))
        PhJ=lambda r: Ph-r*z*eps-(k-1)*(r*z*eps-mp.atan(r*z*eps))
        f413=Bn*z**3*MagJ*mp.quad(lambda r: r*Am(r)*mp.sqrt(k)*mp.sin(PhJ(r)),[0,1])
        P(f"k={k} n={nn} z={z}: k^5/2 D-integrand direct Re={mp.nstr(direct_D.real,12)} (4.12)={mp.nstr(f412,12)} | J direct Re={mp.nstr(direct_J.real,12)} (4.13)={mp.nstr(f413,12)}; Am in [1-b^4/4k,1]: {all(1-(r*z)**4/(4*k)<=Am(mp.mpf(r))<=1 for r in (0.3,0.7,1))}")
    P(f"  n_k={mp.nstr(nk,10)} (n_inf={mp.nstr(2/mp.sqrt(mp.pi),10)}), Bn_k={mp.nstr(Bn,8)}")
open(r"C:\math\임시\주차함수_증명\대조v2\수학검사2\_4_검산_생성함수_출력.txt","w",encoding="utf-8").write("\n".join(out))
