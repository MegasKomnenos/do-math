# 심사 A8 — S4·S13 검산: k=6668에서 창의 수준 질량 R_q=k c_{k+q}(k)의 참값(2.13 재귀, binary64)과
# 8.23의 하계 Psi(q)Omega(xi_q)(Omega는 wKrig 절점값×안전인자의 선형 보간 근사), 10.27(i)(참 생존값 대입), 9.7 하계의 비교.
# 실행: python -I 심사_A8_창질량.py
import math, sys, numpy as np
ROOT=r"C:/math/임시/주차함수_증명/원고_자료/r030ffae/"
C2=(2*math.pi)**-0.5
def logBor(m):
    m=np.asarray(m,dtype=float); return (m-1)*np.log(m)-m-np.array([math.lgamma(x+1) for x in np.atleast_1d(m)]).reshape(m.shape)
def survival(y,Nmax):
    s=np.ones(Nmax+1); lB=np.zeros(Nmax+2); lB[1:]=logBor(np.arange(1,Nmax+2))
    for n in range(y+1,Nmax+1):
        m=np.arange(y+1,n+1); pi=np.exp(lB[m]+lB[n+1-m]-lB[n+1]); s[n]=(1-pi.sum())+np.sum(pi*(y/m)*s[m-1])
    return s
out=[]; P=lambda *a: out.append(' '.join(str(x) for x in a))
k=6668; Nmax=2*k+1
sk=survival(k,Nmax); sk1=survival(k+1,Nmax)
qmax=int(6*k**(2/3)); qs=np.arange(1,qmax+1)
R=k*(sk1[k+qs]-sk[k+qs])                   # true k c_{k+q}(k)
Bor=np.exp(logBor(np.arange(1,2*k+3))); Bor=np.concatenate([[0.0],Bor])  # Bor[j]
Ren=np.arange(0,2*k+3)*Bor; Psi=np.cumsum(Ren)   # Psi[q]=sum_{r<=q} Ren(r)
xK=np.load(ROOT+'xKrig.npy'); wK=np.load(ROOT+'wKrig.npy')
def gfun(x):
    e=lambda v: 0.0 if v<=-0.1 else ((v+0.1)**2/0.4 if v<0.1 else v)
    return min(1.0,0.04+0.12*e(x-1))
def Omega(x): return (1-gfun(x))*np.interp(x,xK,wK)
xi=qs/k**(2/3)
b823=np.array([Psi[q]*Omega(x) for q,x in zip(qs,xi)])
# 10.27(i), y=k+1, true survival values  s_q(y)=s_{y+q-1}(y)=sk1[k+q]
y=k+1
def b1027(q0):
    q=np.arange(1,q0); Rens=C2*(q0-q)**-0.5*np.exp(-1/(12*(q0-q)))
    Aup=math.sqrt(2*math.pi)/4*np.exp(1/(12*(q0-q)))*(q0+q)*np.sqrt(q0-q)
    zR=np.sum(Rens*np.exp(-(q+Aup)/y)*sk1[k+q])
    PrBorge=1-Bor[1:q0].sum()
    return k/(k+1)*(1-q0/(2*k))*(max(zR, sk1[k+q0]-PrBorge)+Bor[q0])
b1027v=np.array([b1027(int(q)) for q in qs])
def b97(q):  # 9.7 lower bound for c_m(w), m=k+q, d=q, w=k, times k
    m=k+q; d=q; w=k; g=((m+1)/(m-d+1))**1.5*math.exp(1/(12*(m-d+1)))
    return k*Psi[d]/w*math.exp(-(g*C2*(4/3*d**1.5+2*math.sqrt(d))+g*g*(5/8*d*d+d))/(w*Psi[d]))
b97v=np.array([b97(int(q)) for q in qs])
P(f"k={k}, window q<= {qmax}; true R_q = k c_{{k+q}}(k)")
P("q | xi | R_true | R/Psi | 8.23 Psi*Omega | ratio | 10.27(i) | ratio | 9.7 | ratio")
for x in [0.1,0.25,0.5,1,1.5,2,3,4,5,6]:
    q=int(round(x*k**(2/3))); q=max(1,min(q,qmax)); i=q-1
    P(f"{q:5d} | {xi[i]:5.2f} | {R[i]:.4f} | {R[i]/Psi[q]:.4f} | {b823[i]:.4f} | {b823[i]/R[i]:.3f} | {b1027v[i]:.4f} | {b1027v[i]/R[i]:.3f} | {b97v[i]:.2e} | {b97v[i]/R[i]:.3e}")
P(f"min over window of R/(Psi*Omega) = {np.min(R/b823):.4f} at q={qs[np.argmin(R/b823)]}  (D:window-mass-env rv_checks: 1.0418 at q=1)")
P(f"window sums /k: truth {R.sum()/k:.4f}; 8.23 {b823.sum()/k:.4f}; 10.27 {b1027v.sum()/k:.4f}; 9.7 {b97v.sum()/k:.4f}; 1-s_{{k+qmax}}(k)={1-sk[k+qmax]:.4f}")
P(f"pointwise: 8.23 >= 10.27 at {np.sum(b823>=b1027v)} of {qmax} q; 8.23 >= 9.7 at {np.sum(b823>=b97v)}; 10.27 >= 9.7 at {np.sum(b1027v>=b97v)}")
cross=np.where(b1027v>b823)[0]
P(f"10.27 exceeds 8.23 for q in [{qs[cross[0]] if len(cross) else None}, {qs[cross[-1]] if len(cross) else None}] (xi {xi[cross[0]] if len(cross) else 0:.2f}..{xi[cross[-1]] if len(cross) else 0:.2f})")
open(sys.argv[0].replace('.py','_out.txt'),'w',encoding='utf-8').write('\n'.join(out)); print('\n'.join(out))
