# R12: 저장된 시험 함수 표 w_i 가 어느 원천 표로 만든 것인지 (읽기 전용; 배정밀도 재현)
import numpy as np, math
from math import lgamma
B=r"C:/math/임시/주차함수_증명/원고_자료"
w=np.load(B+'/세션_재계산/r030ffae_window/work/wKrig.npy')
x=np.load(B+'/세션_재계산/r030ffae_window/work/xKrig.npy')
tfix=np.load(B+'/r030ffae/qenv_fix_v.npy'); trig=np.load(B+'/세션_재계산/r030ffae_window/work/qenv_rig_v.npy')
tx=np.load(B+'/r030ffae/qenv_fix_x.npy')
K=100000; n=len(w)-1
m=np.arange(0,n+3,dtype=float)
with np.errstate(divide='ignore',invalid='ignore'):
    lg=np.array([lgamma(v+1) for v in m])
    LB=np.exp((m-1)*np.log(m)-m-lg); LB[0]=0.0
    U=np.exp(m*np.log(m)-m-lg); U[0]=0.0
Psi=np.cumsum(U)
def chain(tv):
    Q=np.interp(np.arange(n+1)/K**(2/3), tx, tv)
    R=np.zeros(n+1); ww=np.zeros(n+1); ww[0]=1.0
    for b in range(1,n+1):
        ms=np.arange(1,b+1); R[b]=(K/(K+b))*np.sum(LB[ms]*(Q[b-ms]+R[b-ms])); ww[b]=R[b]/Psi[b]
    return ww
for name,tv in (('qenv_rig (earlier table)',trig),('qenv_fix (T-hat)',tfix)):
    ww=chain(tv)
    d=np.abs(ww-w)
    print(name,': max |w_recomputed - w_stored| =',float(d.max()),'at i=',int(d.argmax()),'; first values',ww[1:4], 'stored',w[1:4], 'identical entries',int(np.sum(ww==w)),'of',len(w))
print('T-hat(0)=',tfix[0],' earlier table(0)=',trig[0])
