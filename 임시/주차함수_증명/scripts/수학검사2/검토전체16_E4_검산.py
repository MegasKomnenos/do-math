# -*- coding: utf-8 -*-
"""검토전체16 E4: 장5B(5.5절)의 식·수치 검산.

A. n<=7 전수 열거로 b_{n,l}, A_{n,l}을 얻어 5.5.1-5.5.4의 항등식·부등식을 확인.
B. 큰 매개변수에서 5.5.5-5.5.8의 상수와 포락선을 부동소수점으로 재계산.
C. 장5B가 인용한 라벨이 장 파일에 있는지 확인.
"""
import math, itertools, re, os, sys
from fractions import Fraction as Fr
from math import lgamma, log, exp, sqrt, pi, erfc, floor, ceil

ROOT = r"C:\math\임시\주차함수_증명"
out = []
def P(*a):
    s = " ".join(str(x) for x in a); out.append(s); print(s)

# ---------- A. 전수 열거 ----------
NMAX = 7
def maxdisp(pref):
    n = len(pref); occ = [False]*(n+1); md = 0
    for a in pref:
        p = a
        while occ[p]: p += 1
        occ[p] = True
        if p-a > md: md = p-a
    return md
B = {}   # B[n][l] = b_{n,l}
for n in range(1, NMAX+1):
    cnt = [0]*n
    for pref in itertools.product(range(1, n+1), repeat=n):
        occ=[False]*(n+2); md=0; ok=True
        for a in pref:
            p=a
            while p<=n and occ[p]: p+=1
            if p>n: ok=False; break
            occ[p]=True
            if p-a>md: md=p-a
        if ok: cnt[md]+=1
    B[n]=cnt
B[0]=[1]
def p_(n): return (n+1)**(n-1) if n>=1 else 1
for n in range(1,NMAX+1):
    assert sum(B[n])==p_(n), n
P("A0. 전수 열거 p_n 일치: n<=%d OK"%NMAX)
def b(n,l):
    if n==0: return 1 if l==0 else 0
    return B[n][l] if 0<=l<n else 0
def A(n,l):   # A_{n,l}=#{M<=l}; A_{n,-1}=0, A_{0,l}=1
    if l<0: return 0
    if n==0: return 1
    return sum(B[n][:min(l,n-1)+1])
def s(m,Y): return Fr(A(m,Y-1), p_(m))          # 정의 2-24
def c(m,Y): return Fr(b(m,Y), p_(m))             # 정의 2-25
def pi_(n,t): return Fr(math.comb(n,t)*t**(t-1)*p_(n-t), p_(n))
def sT(t,Y):
    if t<=Y: return Fr(1)
    return Fr(Y*A(t-1,Y-1), t**(t-1))
def x(t,y): return sT(t,y+1)-2*sT(t,y)+sT(t,y-1)
# 쪼개짐 확률 pi^0_n(y): 모든 나무 크기<=y 인 숲의 수 / p_n (지수 공식, 정확)
from functools import lru_cache
@lru_cache(None)
def forests_le(n,y):
    # f(n) = sum_{t=1..min(n,y)} C(n-1,t-1) t^{t-1} f(n-t)  (라벨 1을 품은 나무의 크기 t)
    if n==0: return 1
    return sum(math.comb(n-1,t-1)*t**(t-1)*forests_le(n-t,y) for t in range(1,min(n,y)+1))
def pi0(n,y): return Fr(forests_le(n,y), p_(n))

# A1. 정리 2-13 둘째 식 (n<=2y+1)
ok=True
for n in range(1,NMAX+1):
    for y in range(1,n+1):
        if n<=2*y+1:
            rhs=pi0(n,y)+sum(pi_(n,m)*Fr(y,m)*s(m-1,y) for m in range(y+1,n+1))
            if rhs!=s(n,y): ok=False; P("  2-13 둘째 식 불일치", n,y, s(n,y), rhs)
P("A1. 정리 2-13 둘째 식 (n<=7):", "OK" if ok else "FAIL")
# A2. x_t(y)=1/t[(y+1)c_{t-1}(y)-(y-1)c_{t-1}(y-1)] (t>=y+1), x_y(y)=-1/y
ok=True
for t in range(1,NMAX+1):
    for y in range(1,t+1):
        if t>=y+1:
            if x(t,y)!=Fr(1,t)*((y+1)*c(t-1,y)-(y-1)*c(t-1,y-1)): ok=False; P("  x_t 식 불일치",t,y)
        if t==y and x(t,y)!=Fr(-1,y): ok=False; P("  x_y(y) 불일치",y,x(t,y))
P("A2. 나무 곡률 식 (5.5.1):", "OK" if ok else "FAIL")
# A3. 보조정리 5-19 열 재귀
ok=True
for n in range(3,NMAX+1):
    for y in range(1,n):
        if 2*y>=n+1 and y<=n-1:
            lhs=c(n,y)-c(n,y-1); rhs=sum(pi_(n,t)*x(t,y) for t in range(y,n+1))
            if lhs!=rhs: ok=False; P("  5-19 불일치",n,y,lhs,rhs)
P("A3. 보조정리 5-19 (열 재귀):", "OK" if ok else "FAIL")
# A4. 보조정리 5-20 비
def g(xv): return (xv-1)*log(1+1/xv)
ok=True
for n in range(3,NMAX+1):
    for t in range(math.ceil((n+1)/2), n):
        r=float(pi_(n,t+1)/pi_(n,t)); r2=exp(g(t)-g(n-t))
        if abs(r-r2)>1e-12 or r<=1: ok=False; P("  5-20",n,t,r,r2)
P("A4. 보조정리 5-20 (핵 비):", "OK" if ok else "FAIL")
# A5. 보조정리 5-27 기저 항등식
ok=True
for n in range(3,NMAX+1):
    for y in range(1,n):
        if 2*y>=n+1 and y<=n-1:
            Pn=sum(x(t,y) for t in range(y,n+1))
            rhs=Fr(-1,y)+sum(((y+1)*c(m,y)-(y-1)*c(m,y-1))/(m+1) for m in range(y,n))
            if Pn!=rhs: ok=False; P("  5-27",n,y)
            top=Fr(y*(y-1),n)*c(n-1,y-1)
            if y*Pn < -1-top: ok=False; P("  cor-L 위반",n,y,float(y*Pn),float(-1-top))
P("A5. 보조정리 5-27 항등식과 따름정리 6:cor-L (n<=7):", "OK" if ok else "FAIL")
# A6. 명제 5-22 (IH가 실제로 성립하는 자리에서)
def t0(y):
    t=y+2
    while not (y <= (t-1)-math.floor(0.75*(t-1)**(2/3))): t+=1
    return t
ok=True; cnt=0
for n in range(3,NMAX+1):
    for y in range(1,n):
        if 2*y>=n+1 and y<=n-1:
            T0=t0(y)
            if not (y+2<=T0<=n): continue
            IH=all(b(m,y)>=b(m,y-1) for m in range(T0-1,n))
            if not IH: continue
            cnt+=1
            lhs=c(n,y)-c(n,y-1)
            WIN=sum((pi_(n,t)-pi_(n,y))*max(-x(t,y),0) for t in range(y+1,T0))
            POS=sum((pi_(n,m+1)-pi_(n,T0-1))*(c(m,y)+c(m,y-1))/(m+1) for m in range(T0-1,n))
            Pn=sum(x(t,y) for t in range(y,n+1))
            rhs=pi_(n,y)*Pn-WIN+POS
            if lhs<rhs: ok=False; P("  5-22 위반",n,y,float(lhs),float(rhs))
P("A6. 명제 5-22 (검사한 자리 %d):"%cnt, "OK" if ok else "FAIL")
# A7. 정리 5-28
def zloss(m,d):
    w=m-d; return exp((d-1)/w)/(w+1)+3*d/(2*(w+1)*(m+1))
ok=True
for m in range(2,NMAX):
    for d in range(1,m//2+1):
        w=m-d
        if float(c(m+1,w+1)) < (1-zloss(m,d))*float(c(m,w))-1e-15: ok=False; P("  5-28 위반",m,d)
P("A7. 정리 5-28 (m<=6):", "OK" if ok else "FAIL")
# A8. 정리 6:diag-first-layer 부등식 (6.31) 작은 값
ok=True
for d in range(1,4):
    for m in range(max(2,2*d-1),NMAX):
        w=m-d
        if not ((w+2)*(m+1)*c(m+1,w+1) > w*(m+2)*c(m,w)): ok=False; P("  (6.31) 위반",m,d)
P("A8. (6.31) 작은 값:", "OK" if ok else "FAIL")
# A9. Bor, Ren, Bor^{*z}
def Bor(m): return exp(-m+(m-1)*log(m)-lgamma(m+1))
def Ren(j): return 1.0 if j==0 else j*Bor(j)
def BorT(z,D):   # Borel-Tanner
    if D<z: return 0.0
    return z/D*exp(-D+(D-z)*log(D)-lgamma(D-z+1)) if D>0 else 0.0
# A10. 보조정리 5-24 방문 확률 (사슬 재귀로 정확히)
@lru_cache(None)
def visit(t,sz):   # 크기 t 나무의 사슬이 크기 sz를 방문할 확률 (sz>t/2)
    tot=Fr(0)
    for sp in range(sz, t):   # 뿌리 지운 숲 크기 t-1의 가장 큰 나무 sp (sp>=sz>(t-1)/2 라 유일)
        pr=pi_(t-1,sp)
        tot+= pr*(1 if sp==sz else visit(sp,sz))
    return tot
ok=True
for t in range(2,NMAX+1):
    for sz in range(t//2+1,t):
        v=float(visit(t,sz)); f=Ren(t-sz)*Bor(sz)/Bor(t)
        if abs(v-f)>1e-12: ok=False; P("  5-24",t,sz,v,f)
P("A10. 보조정리 5-24 (방문 확률):", "OK" if ok else "FAIL")
# A11. 보조정리 5-25 항별 상계
ok=True
for t in range(2,NMAX+1):
    for y in range(t//2+1,t):
        lhs=max(-float(x(t,y)),0); rhs=Ren(t-y)*Bor(y)/(y*Bor(t))
        if lhs>rhs+1e-15: ok=False; P("  5-25",t,y,lhs,rhs)
P("A11. 보조정리 5-25:", "OK" if ok else "FAIL")
# A12. 정리 5-31 Lc 하계 (Y+q<=7)
def Lc(Y,q):
    tot=0.0
    for z in range(1,q+1):
        for D in range(z,q+1):
            tot+= z*BorT(z,D)*Bor(Y+q+1-D)/Bor(Y+q+1)*float(pi0(Y+q-D,Y))*exp(-(z*(q+1)-D*(z+1)/2)/Y)
    return tot/Y
ok=True
for Y in range(1,NMAX):
    for q in range(1,Y+2):
        if Y+q<=NMAX:
            lhs=float(c(Y+q,Y)); rhs=Lc(Y,q)
            if lhs<rhs-1e-13: ok=False; P("  5-31 위반",Y,q,lhs,rhs)
P("A12. 정리 5-31 (Y+q<=7):", "OK" if ok else "FAIL")
# A13. stop-lower 상계 pi^0_{Y+j}(Y)<=Pr(beta>j)
ok=True
for Y in range(1,NMAX):
    for j in range(0,NMAX-Y+1):
        lhs=float(pi0(Y+j,Y)); rhs=1-sum(Bor(i) for i in range(1,j+1))
        if lhs>rhs+1e-13: ok=False; P("  stop-lower 상계 위반",Y,j,lhs,rhs)
P("A13. stop-lower 상계 (작은 값):", "OK" if ok else "FAIL")


# ---------- A14. 정리 2-13 재귀로 n<=40 ----------
NB=40
@lru_cache(None)
def S(n,y):   # s_n(y), n<=2y+1 (첫 층), 정리 2-13 둘째 식
    if n==0: return Fr(1)
    if n<=y: return Fr(1)
    assert n<=2*y+1
    return pi0(n,y)+sum(pi_(n,m)*Fr(y,m)*S(m-1,y) for m in range(y+1,n+1))
def C(m,Y): return S(m,Y+1)-S(m,Y)      # c_m(Y), 유효 범위 m<=2Y+1
def sT2(t,Y): return Fr(1) if t<=Y else Fr(Y,t)*S(t-1,Y)
def x2(t,y): return sT2(t,y+1)-2*sT2(t,y)+sT2(t,y-1)
for n in range(1,NMAX+1):
    for y in range(max(1,-(-(n-1)//2)),n+1):
        assert S(n,y)==s(n,y),(n,y)
P("A14-0. 재귀 s_n(y)가 전수 열거와 일치 (n<=7)")
ok19=ok27=ok22=ok28=ok31=ok25=True; cnt22=0
for n in range(3,NB+1):
    for y in range((n+1+1)//2, n):
        if 2*y<n+1: continue
        lhs=C(n,y)-C(n,y-1)
        if lhs!=sum(pi_(n,t)*x2(t,y) for t in range(y,n+1)): ok19=False
        Pn=sum(x2(t,y) for t in range(y,n+1))
        if Pn!=Fr(-1,y)+sum(((y+1)*C(m,y)-(y-1)*C(m,y-1))/(m+1) for m in range(y,n)): ok27=False
        if y*Pn < -1-Fr(y*(y-1),n)*C(n-1,y-1): ok27=False; P("  cor-L 위반",n,y)
        T0=t0(y)
        if y+2<=T0<=n and all(C(m,y)>=C(m,y-1) for m in range(T0-1,n)):
            cnt22+=1
            WIN=sum((pi_(n,t)-pi_(n,y))*max(-x2(t,y),0) for t in range(y+1,T0))
            POS=sum((pi_(n,m+1)-pi_(n,T0-1))*(C(m,y)+C(m,y-1))/(m+1) for m in range(T0-1,n))
            if lhs<pi_(n,y)*Pn-WIN+POS: ok22=False; P("  5-22 위반",n,y)
        for t in range(y+1,n+1):
            if t<2*y:
                if max(-float(x2(t,y)),0)>Ren(t-y)*Bor(y)/(y*Bor(t))+1e-15: ok25=False; P("  5-25 위반",t,y)
for m in range(2,NB):
    for d in range(1,m//2+1):
        w=m-d
        if float(C(m+1,w+1))<(1-zloss(m,d))*float(C(m,w))-1e-15: ok28=False; P("  5-28 위반",m,d)
for Y in range(1,NB):
    for q in range(1,Y+2):
        if Y+q<=NB:
            if float(C(Y+q,Y))<Lc(Y,q)-1e-13: ok31=False; P("  5-31 위반",Y,q)
P("A14. n<=%d: 5-19 %s; 5-27·cor-L %s; 5-22 %s (검사 %d자리); 5-25 %s; 5-28 %s; 5-31 %s"%(NB,ok19,ok27,ok22,cnt22,ok25,ok28,ok31))

# ---------- B. 큰 매개변수 ----------
P("--- B ---")
def lpi(n,t):  # log pi_n(t) = log Bor(n+1-t)+log Bor(t)-log Bor(n+1)
    lb=lambda m: -m+(m-1)*log(m)-lgamma(m+1)
    return lb(n+1-t)+lb(t)-lb(n+1)
def pin(n,t): return exp(lpi(n,t))
# B1. t_0(y)<=n, wid 상계
ok=True
for y in [25000,25001,30000,33334,50000,100000,250000,1000000]:
    T0=t0(y); wid=T0-1-y
    if wid>0.75*(1.1*y)**(2/3)+1: ok=False; P("  wid 상계 위반",y,wid)
P("B1. wid<=0.75(1.1y)^{2/3}+1 (표본):", "OK" if ok else "FAIL", "예 y=25000:",t0(25000)-1-25000, 0.75*(1.1*25000)**(2/3)+1)
P("    h0^3=%.6e >= 1/25000=%.6e:"%(0.0342**3,1/25000), 0.0342**3>=1/25000, "; 25000^{-1/3}=%.6f"%(25000**(-1/3)))
P("    q_max(13824)=%d <= 13824/4=%d"%(floor(6*13824**(2/3)),13824//4))
# B2. 보조정리 5-30 상수
def Wsharp_positions(n, step):
    ys=[]; y=(n+1)//2 if (n+1)%2==0 else (n+2)//2
    ymax=y
    while n-ymax+1>10*ymax**(2/3): ymax+=1
    ymax-=1
    return list(range(y, ymax+1, step))+[ymax]
mx_top=0; mx_le=0; mx_gt=0; mn_br=9; mx_pn1=0
for n in [50001,50002,60000,100000,333333,1000000]:
    for y in Wsharp_positions(n, max(1,(n//2)//200)):
        top_pi=(y-1)*pin(n,y); mx_top=max(mx_top,top_pi)
        if y<=2*n/3: mx_le=max(mx_le,top_pi)
        else: mx_gt=max(mx_gt,top_pi)
        br=pin(n,n)-pin(n,t0(y)-1)-top_pi; mn_br=min(mn_br,br)
    mx_pn1=max(mx_pn1,pin(n,n-1))
P("B2. top_pi 최대 %.5f (<=0.0232), y<=2n/3 최대 %.5f (<=0.0133), y>2n/3 최대 %.5f; pi_n(n-1) 최대 %.5f (<0.1354); 괄호 최소 %.4f (>0.2)"%(mx_top,mx_le,mx_gt,mx_pn1,mn_br))
P("    e^{-1}-0.1354-0.0232=%.4f"%(exp(-1)-0.1354-0.0232), "; (2pi)^{-1/2}*sqrt2*3^{1.5}*50001^{-1/2}=%.5f"%((2*pi)**-0.5*sqrt(2)*3**1.5*50001**-0.5), "; (0.15)^{1.5}=%.5f"%(0.15**1.5), "; *(2pi)^{-1/2}=%.5f"%(0.15**1.5*(2*pi)**-0.5))
# B3. 보조정리 5-26 닫힌 꼴 vs 직접 합
ok=True
for (n,y) in [(50001,25001),(50001,30000),(100000,60000),(60000,30001),(100000,66000)]:
    T0=t0(y); wid=T0-1-y
    direct=sum((pin(n,t)-pin(n,y))*Ren(t-y)*Bor(y)/Bor(t) for t in range(y+1,T0))/y
    c1=1.5*(2*y+2*wid-n)/(y*(n-y-wid)); e0=1.5*wid*(2*y+2*wid-2-n)/((y+wid-1)*(n-y-wid+1))
    closed=pin(n,y)/y/sqrt(2*pi)*(2/3)*(wid+1)**1.5*c1*(1+wid/y)**1.5*exp(e0+1/(12*y))
    if direct>closed: ok=False
    P("  5-26 (n,y)=(%d,%d): wid=%d WIN^V=%.4e 닫힌꼴=%.4e 비=%.3f"%(n,y,wid,direct,closed,closed/direct))
P("B3. 보조정리 5-26:", "OK" if ok else "FAIL")
# B4. right-part 상수
y=33334; r=10*y**(2/3)-1
P("B4. 10*33334^{2/3}-1=%.3f (>10356?)"%r, r>10356)
chi=2064
hv=chi**-0.5*(2/sqrt(pi)*(1+1/chi)+1/sqrt(pi)); P("    hv_2064=%.5f, 1.6932*2064^{-1/2}=%.5f"%(hv,1.6932*chi**-0.5))
t=y**(1/3); eps=1.6932*(t/10+1)*(2*t*t-7.5)**-0.5; P("    eps_hov(y=33334)=%.5f (<=0.1573)"%eps)
P("    sqrt(2/pi)/sqrt(2064)=%.5f (<=0.01757)"%(sqrt(2/pi)/sqrt(2064)))
P("    0.75*1.1^{2/3}=%.5f (<=0.7993)"%(0.75*1.1**(2/3)))
P("    (2pi)^{-1/2}(1.50003/0.9199)^{1.5}=%.6f; *e^{1/(12*50002)}=%.6f (<=0.8308)"%((2*pi)**-0.5*(1.50003/0.9199)**1.5,(2*pi)**-0.5*(1.50003/0.9199)**1.5*exp(1/(12*50002))))
P("    0.24924/sqrt(10358)=%.6f (<=0.00245)"%(0.24924/sqrt(10358)))
P("    1-0.01757-0.00245=%.5f"%(1-0.01757-0.00245))
P("    (0.7993+2/33334^{2/3})^{1.5}=%.5f (<=0.7172)"%((0.7993+2/33334**(2/3))**1.5))
rp=10358; P("    (r+1)/(r-wid) at r+1=10358: %.5f (<=1.0872)"%(rp/(0.92007*rp-2)))
P("    eps_0 bound: %.5f (<=0.1305)"%(1.5*(0.07993*rp+1)/(0.92007*rp-1)))
P("    (1+wid/y)^{1.5}: %.5f (<=1.0376)"%((1+(0.7993*33334**(2/3)+1)/33334)**1.5))
W=(2*pi)**-0.5*(2/3)*0.7172*1.5*1.0872*1.0376*exp(0.1305+1/400008); P("    (r+1)/y*W bound=%.5f (<=0.3678)"%W)
P("    e^{-c4}: %.5f (>=0.9936)"%exp(-(1/156+1/(12*33334)+1/(12*50002))))
K=(1-0.1573)*0.71216*0.9936*(2*0.9799-0.0232)-0.3678; P("    0.8427*0.71216*0.9936*1.9366-0.3678=%.5f (>=0.7869)"%K)
P("    Psi_R at 2/3: %.5f"%(0.7869*2/3-1/3-2.5e-5))
# B5. scaled-integrand (마) 상수
h0=0.0342; umax=sqrt(6*h0); c3=1/sqrt(2)-umax/3
f12=c3*12**1.5-12-log(sqrt(2)*(1+6*h0)*12/c3)
P("B5. upsilon_max=%.5f c3=%.5f (>=0.556) f(12)=%.3f (>7)"%(umax,c3,f12))
def yfun(th): return max(th/2,th-h0)
def rhobar(th):
    return sqrt(2)*th**1.5*exp(-th*sqrt(yfun(th))+min(th*th*h0,umax*th**1.5)/3)*(1+min(th*h0*h0,6*h0))/(sqrt(yfun(th))-min(th*h0,umax*sqrt(th))/3)
P("    rhobar(12)=%.3e <= e^{-12}=%.3e"%(rhobar(12),exp(-12)), rhobar(12)<=exp(-12))
# B6. hover-tail 수치
def borel_tail_probs(chi,zmax):
    # Pr(R_z<=chi-1) via convolution
    N=chi; bor=[0.0]+[Bor(i) for i in range(1,N)]
    dist=[1.0]+[0.0]*(N-1); res=[]
    for z in range(1,zmax+1):
        new=[0.0]*N
        for a in range(N):
            if dist[a]==0: continue
            for i in range(1,N-a): new[a+i]+=dist[a]*bor[i]
        dist=new; res.append(sum(dist))
    return res
ok=True
for chi in [10,50,200]:
    pr=borel_tail_probs(chi,12)
    for z in range(1,13):
        lb1=max(1-2/sqrt(pi)*z**1.5*(chi-1)**-0.5,0)
        hv=chi**-0.5*(2/sqrt(pi)*(1+1/chi)+1/sqrt(pi)); lb2=1-z*hv
        if pr[z-1]<lb1-1e-12 or pr[z-1]<lb2-1e-12: ok=False; P("  hover-tail 위반",chi,z,pr[z-1],lb1,lb2)
P("B6. hover-tail 두 하계 (chi=10,50,200; z<=12):", "OK" if ok else "FAIL")
# B7. bt-tail (가), borel-gf (다), stirling-bor
ok=True
for z in [1,2,5,20]:
    for D in [z+1,z+5,z+50,z+1000]:
        W_=D-z; lub=log(z/sqrt(2*pi)/D)-0.5*log(W_)-z*z/(2*W_)+z**3/(3*W_*W_)
        lbt=log(z/D)-D+(D-z)*log(D)-lgamma(D-z+1)
        if lbt>lub+1e-12: ok=False; P("  bt-tail(가) 위반",z,D)
P("B7a. bt-tail (가):", "OK" if ok else "FAIL")
def u_of(vs):  # solve -u-log(1-u)=vs
    lo,hi=0.0,1-1e-15
    for _ in range(200):
        mid=(lo+hi)/2
        if -mid-log(1-mid)<vs: lo=mid
        else: hi=mid
    return lo
ok=True
for vs in [1e-6,1e-3,0.01,0.1,0.5,1,2,4]:
    u=u_of(vs)
    if not (sqrt(2*vs)-2*vs/3-1e-12<=u<=sqrt(2*vs)+1e-12): ok=False; P("  borel-gf(다) 위반",vs,u)
P("B7b. borel-gf (다):", "OK" if ok else "FAIL")
ok=True
for m in [1,2,3,10,100,10000]:
    if not ((2*pi)**-0.5*m**-1.5*exp(-1/(12*m))<=Bor(m)<=(2*pi)**-0.5*m**-1.5): ok=False
P("B7c. stirling-bor (가):", "OK" if ok else "FAIL")
# B8. band 첫 셀 포락선
n=50001; la=0.5; lb=0.5+1/24000
wb=0.75*(1.1*lb*n)**(2/3)+1
chi_lo=floor(0.3*(1-lb)*n-1)-1
hov=0.0; z=0
while True:
    term=(1-2/sqrt(pi)*z**1.5*chi_lo**-0.5)
    if term<=0: break
    hov+=(la-1/n)**z*term; z+=1
sec=1-sqrt(2/pi)*(0.3*(1-lb)*n-1)**-0.5-0.3*(1-la)*n*(2*pi)**-0.5*((n+1)/(la*n*((1-lb)*n-wb)))**1.5*exp(1/(12*(n+1)))
top=(2*pi)**-0.5*(1+1/n)**1.5*la**-0.5*(1-lb)**-1.5*n**-0.5*exp(1/(12*n))
Kt=la*exp(-1/(12*(0.4*(1-lb)*n-6*(lb*n)**(2/3)+1))-1/(12*la*n)-1/(12*(n+1)))
cb=1.5*((2*lb-1)*n+2*wb)/(la*n*((1-lb)*n-wb)); eb=1.5*wb*((2*lb-1)*n+2*wb)/((la*n-1)*((1-lb)*n-wb))
Wb=(2*pi)**-0.5*(2/3)*(wb+1)**1.5*cb*(1+wb/(la*n))**1.5*exp(eb+1/(12*la*n))
ratio=hov*0.71216*Kt*(2*sec-top)-Wb
P("B8. band 첫 셀: hov=%.7f sec=%.7f top=%.7f K=%.7f W=%.7f 비=%.6f (D: 1.9570106, 0.9885536, 0.0071375, 0.4999889, 0.0168736, 1.355874)"%(hov,sec,top,Kt,Wb,ratio))
# 조건 확인 (명제 band-inequality 증명)
P("    n/3 > 10(2n/3)^{2/3} at 50001: %.1f > %.1f"%(n/3,10*(2*n/3)**(2/3)), "; 0.4n/3=%.1f >= 6(2n/3)^{2/3}+1=%.1f"%(0.4*n/3,6*(2*n/3)**(2/3)+1))
P("    wid bound at y=2n/3: %.1f <= 0.7(n-y)=%.1f"%(0.75*(1.1*2*n/3)**(2/3)+1,0.7*n/3))

# ---------- C. 라벨 존재 ----------
P("--- C ---")
txt=open(os.path.join(ROOT,"장v2","장5B.md"),encoding="utf-8").read()
labels=sorted(set(re.findall(r"\{\{([^}]+)\}\}",txt)))
files=[f for f in os.listdir(os.path.join(ROOT,"장v2")) if f.endswith(".md")]
alltxt="".join(open(os.path.join(ROOT,"장v2",f),encoding="utf-8").read() for f in files)
missing=[]
for lab in labels:
    ch,name=lab.split(":",1)
    pat=re.compile(r"^(###\s*D\.\{\{"+re.escape(lab)+r"\}\}|\*\*(정리|명제|보조정리|따름정리|정의) \{\{"+re.escape(lab)+r"\}\})",re.M)
    if not pat.search(alltxt): missing.append(lab)
P("C1. 장5B가 인용한 라벨 %d개 가운데 머리를 찾지 못한 것:"%len(labels), missing if missing else "없음")
open(os.path.join(ROOT,"대조v2","수학검사2","_E4_검산_out.txt"),"w",encoding="utf-8").write("\n".join(out))
