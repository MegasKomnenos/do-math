# R12: D.window-mass-env 의 Omega 표 값과 0.744 적분 (읽기 전용; 배정밀도 어림)
import numpy as np, math
B=r"C:/math/임시/주차함수_증명/원고_자료"
x=np.load(B+'/세션_재계산/r030ffae_window/work/xKrig.npy'); w=np.load(B+'/세션_재계산/r030ffae_window/work/wKrig.npy')
print(len(x),len(w),x[:3],x[-1],w[:3])
K=1e5
print('grid check', np.max(np.abs(x-np.arange(len(x))/K**(2/3))))
def e(s):
    s=np.asarray(s); return np.where(s<=-0.1,0.0,np.where(s>=0.1,s,(s+0.1)**2/0.4))
g=np.minimum(1.0,0.04+0.12*e(x-1))
v=(1-g)*w
print('nonincreasing', np.all(np.diff(v)<=0), 'changed by cummin', np.sum(np.minimum.accumulate(v)!=v))
for t in (0,0.5,1,2,3,4,6):
    print(t, float(np.interp(t,x,v)))
d=np.diff(v)/np.diff(x)
print('max |secant slope|', np.max(np.abs(d)))
m=x<=6.0
xs=np.append(x[m],6.0); vs=np.append(v[m],np.interp(6.0,x,v))
f=vs*np.sqrt(2*xs/math.pi)
print('integral', float(np.sum((f[1:]+f[:-1])/2*np.diff(xs))))
# table T-hat
tx=np.load(B+'/r030ffae/qenv_fix_x.npy'); tv=np.load(B+'/r030ffae/qenv_fix_v.npy')
print(len(tx),len(tv),tx[:3],tx[-1], tv[:3], tv[-1])
print('coord dev', np.max(np.abs(tx-0.0005*np.arange(len(tx)))))
sl=np.diff(tv)/0.0005
print('max|T slope|', np.max(np.abs(sl)), 'TV of T-hat prime on [0,6]', np.sum(np.abs(np.diff(sl))), 'strict decreasing', np.all(np.diff(tv)<0), tv[0])
print(12927/K**(2/3), 12926/K**(2/3))
print(1.15/6**1.5)
