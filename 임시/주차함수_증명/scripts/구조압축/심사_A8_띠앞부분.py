# 심사 A8 — E2 검산(점 평가, 인증 아님): 띠 앞부분 103<=nu<=3.6k^{2/3}에서 8.27의 LB^U(8.28)와 8.29의 LB^low(=LB^mono, 경우(iii))를
# 저장된 표 T̂(qenv_fix)와 시험 함수 Omega(wKrig 절점×안전인자, 선형 보간)로 같은 점에서 평가해 견준다.
# 물음: 8.29의 식이 앞부분에서 이미 1.05를 넘는가(그러면 8.27·D:bprime-boxes·8.10이 불필요해질 수 있다).
# 실행: python -I 심사_A8_띠앞부분.py
import math, sys, numpy as np
ROOT=r"C:/math/임시/주차함수_증명/원고_자료/r030ffae/"
C2=(2*math.pi)**-0.5; Z12=-1.4603545088095868; Zm12=-0.2078862249773545; Z32=2.6123753486854883
xT=np.load(ROOT+'qenv_fix_x.npy'); vT=np.load(ROOT+'qenv_fix_v.npy'); xK=np.load(ROOT+'xKrig.npy'); wK=np.load(ROOT+'wKrig.npy')
def gfun(x):
    e=np.where(x-1<=-0.1,0.0,np.where(x-1<0.1,(x-1+0.1)**2/0.4,x-1)); return np.minimum(1.0,0.04+0.12*e)
That=lambda x: np.interp(x,xT,vT); Omega=lambda x: (1-gfun(x))*np.interp(x,xK,wK)
M=200000
lB=np.zeros(M+1); mm=np.arange(1,M+1); lB[1:]=(mm-1)*np.log(mm)-mm-np.array([math.lgamma(x+1) for x in mm])
Bor=np.exp(lB); Bor[0]=0; Ren=np.arange(M+1)*Bor; Psi=np.cumsum(Ren); BorLE=np.cumsum(Bor)
def Blow(k,nu):
    S12=2*math.sqrt(nu)+Z12+0.5/math.sqrt(nu)-nu**-1.5/24; Sm12=2/3*nu**1.5+0.5*math.sqrt(nu)+Zm12+1/(24*math.sqrt(nu))
    return C2/(k+nu)*((nu+1)*S12-Sm12-((nu+1)*Z32-S12)/12)
def Rlow(kp,nup,qw):
    q=np.arange(1,qw+1); xi=(q-1)/kp**(2/3)
    return (1/kp)*np.sum((1-q*nup/(kp*(kp+nup)))**1.5*(kp/(kp+q))*(That(xi)+Psi[q-1]*Omega(xi)))
def Rtil(kp,nup,qm,kenv):
    q=np.arange(1,qm+1); xi=(q-1)/kp**(2/3)
    return np.sum(That(np.maximum(nup-q,0)/kenv**(2/3))/(kp+q)*(That(xi)+Psi[q-1]*Omega(xi)))
def LBmono(k,nu):
    n=2*k+nu; N=n-k; qmax=int(6*k**(2/3)); qfb=int((3*(k-1)/4-qmax-3)//8)
    fb=lambda lam: sum((lam*BorLE[qfb])**i for i in range(8))
    c0=max((1-1/k)**(N-k+1), 1-math.exp(7/6)*N**1.5/(4*C2*k*(2*k-1-N)))
    return BorLE[nu-1]*math.exp(-1/(12*(n+1)))*(k/n)*(math.exp(-5/(12*k))*Rlow(k,nu,qmax)*fb(k/n)+c0*math.exp(-5/(12*(k-1)))*Rlow(k-1,nu+2,qmax)*fb((k-1)/n))
def LBU(k,nu):
    n=2*k+nu; qmax=int(6*k**(2/3)); qmax1=int(6*(k-1)**(2/3))
    fbo=lambda lam: sum((lam*BorLE[300])**i for i in range(8))
    return BorLE[nu-1]*math.exp(-1/(12*(n+1)))*8*(k/n)**2.5*((k+nu+1)/(n+1))**1.5*(1+Blow(k,nu))*(math.exp(-5/(12*k))*Rtil(k,nu,qmax,k-1)*fbo(k/n)+math.exp(-5/(12*(k-1)))*Rtil(k-1,nu+2,qmax1,k-2)*fbo((k-1)/n))
out=[]; P=lambda *a: out.append(' '.join(str(x) for x in a))
P("k | nu | nu/k^(2/3) | LB^U (8.27) | LB^mono=LB^low 경우(iii) (8.29) | 비고")
for k in [6668,6935,7213,10000,20000,100000]:
    top=int(3.6*k**(2/3))
    for nu in sorted(set([103,200,400,800,top//2,top,int(k/4)-2])):
        if nu<103: continue
        note='앞 띠 끝' if nu==top else ('k/4 직전(경우(iii) 끝)' if nu==int(k/4)-2 else '')
        u=LBU(k,nu) if nu<=top else float('nan')
        P(f"{k:7d} | {nu:6d} | {nu/k**(2/3):5.2f} | {u:7.4f} | {LBmono(k,nu):7.4f} | {note}")
open(sys.argv[0].replace('.py','_out.txt'),'w',encoding='utf-8').write('\n'.join(out)); print('\n'.join(out))

# ---- 추가: 생존 1 항 LOW_k·LOW_{k-1}을 넣은 LB^low (경우 (i)(ii)) 점 평가, 기록 상자 최솟값과의 대조, 위험률 다듬기 유무 비교 ----
def LBlow(k,nu,hazard=True):
    n=2*k+nu; N=n-k; qmax=int(6*k**(2/3)); qfb=int((3*(k-1)/4-qmax-3)//8)
    if nu>=qmax+1: case='i'; qw=qmax; qws=6*k**(2/3); low=True
    elif nu-1>=k/4: case='ii'; qw=nu-1; qws=nu-1; low=True
    else: case='iii'; qw=qmax; qws=None; low=False
    fb=lambda lam: sum((lam*BorLE[qfb])**i for i in range(8))
    c0=max((1-1/k)**(N-k+1), 1-math.exp(7/6)*N**1.5/(4*C2*k*(2*k-1-N)))
    def LOW(kk,nn_k,nup,lev):  # lev 0: level k, 1: level k-1
        if not low: return 0.0
        tot=0.0
        for i in range(8):
            if lev==0:
                if nu>=qfb+2:
                    h=(k/(k+nu)-k/(2*k-1)) if hazard else 0.0
                    La=k/(n-k)-k/(2*k+2)*math.exp(-h)
                else: La=k/(n-k)-max(0.5,k/(n-qfb))
                Lc=(k/(k+qfb+1)-0.5) if (nu>=qfb+2 and qfb>=qw) else float('inf')
                Li=k/(k+qws+1)-k/(2*k+2-(i+1)*qfb)
                lam=(k/n)*BorLE[qfb]
            else:
                if nu>=qfb+2:
                    h=((k-1)/(k+nu+1)-(k-1)/(2*k-3)) if hazard else 0.0
                    La=(k-1)/(k+nu+1)-(k-1)/(2*k)*math.exp(-h)
                else: La=(k-1)/(k+nu+1)-max(0.5,(k-1)/(n-qfb))
                Lc=((k-1)/(k+qfb+1)-0.5) if (nu>=qfb+2 and qfb>=qw) else float('inf')
                Li=(k-1)/(k+qws)-(k-1)/(2*k+2-(i+1)*qfb)
                lam=((k-1)/n)*BorLE[qfb]
            tot+=lam**i*0.5*max(0.0,min(La,Lc,Li))
        return tot
    val=BorLE[nu-1]*math.exp(-1/(12*(n+1)))*(k/n)*(math.exp(-5/(12*k))*Rlow(k,nu,qw)*fb(k/n)+LOW(k,n,nu,0)+c0*(math.exp(-5/(12*(k-1)))*Rlow(k-1,nu+2,qw)*fb((k-1)/n)+LOW(k-1,n,nu+2,1)))
    return val,case
P("\n--- 기록 상자 최솟값 대조(점 평가는 상자 모서리 평가보다 조금 크다) ---")
for k,nu,ref in [(6668,2038,'MONO2 T0.3 상자 최솟값 1.0109 (nu 2038-2080, 경우(iii) 생존1항 없음)'),(6668,2080,''),(6668,3000,'LOW(위험률 없음) T0.44 상자 최솟값 1.0136 (nu 3000-3051)'),(6668,3051,''),(6668,3280,'LOWH T0.48 상자 최솟값 1.0094 (nu 3280-3328); 글의 재계산 1.0098'),(6668,3328,'')]:
    v,c=LBlow(k,nu); v0,_=LBlow(k,nu,hazard=False)
    P(f"k={k} nu={nu} case({c}): LB^low={v:.4f}  위험률 없이={v0:.4f}   {ref}")
P("\n--- 위험률 다듬기(8.28)의 기여: k=6668, nu=0.40k..0.48k ---")
for f in [0.40,0.42,0.44,0.46,0.48]:
    nu=int(f*6668); v,c=LBlow(6668,nu); v0,_=LBlow(6668,nu,hazard=False)
    P(f"nu={nu} ({f}k) case({c}): with hazard {v:.4f} | without {v0:.4f}")
P("\n--- 앞 띠(103<=nu<=3.6k^(2/3))에서 LB^low의 점 최솟값(격자 nu, 간격 ~1%) ---")
for k in [6668,6935,7213,8000,10000,20000,10**5,10**6]:
    top=int(3.6*k**(2/3)); nus=sorted(set([103]+[int(103*1.01**i) for i in range(1,400) if 103*1.01**i<top]+[top]))
    vals=[LBlow(k,nu)[0] for nu in nus]; i=int(np.argmin(vals))
    P(f"k={k}: min LB^low on front band = {vals[i]:.4f} at nu={nus[i]} (top={top});  LB^U at top = {LBU(k,top):.4f}")
open(sys.argv[0].replace('.py','_out.txt'),'w',encoding='utf-8').write('\n'.join(out)); print('\n'.join(out[-26:]))
