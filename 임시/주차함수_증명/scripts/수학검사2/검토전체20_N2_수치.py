# N2 검산: 3.6 수치, 4장 상수 a0,a1, 따름정리 (다), (4.9)와 M4/M0 식의 정확 검산
from fractions import Fraction as Fr
from math import comb, gamma, pi, sqrt, exp
import mpmath as mp
out=[]
lam=Fr(751,1000)
s1=sum(i*lam**(i-1) for i in range(1,9)); s2=sum((i-1)*lam**(i-1) for i in range(1,9))
out.append("3.6: lam^8=%.6f sum1=%.5f sum2=%.5f  terms: %.5f %.5f %.5f total=%.5f"%(float(lam**8),float(s1),float(s2),float(lam**8),float(s1/31),float(s2/1000),float(lam**8+s1/31+s2/1000)))
# E_n omega_n small n
def p(m): return (m+1)**(m-1) if m>=1 else 1
for n in range(1,6):
    v=sum(Fr(comb(n,j)*j**j*p(n-j),p(n)) for j in range(1,n//2+1))
    out.append("n=%d E omega=%s <= sqrt n: %s"%(n,v,float(v)<=sqrt(n)))
# a0,a1
mp.mp.dps=30
a0=mp.quad(lambda w: mp.e**(-w**3/3),[0,mp.inf]); a1=mp.quad(lambda w: w*mp.e**(-w**3/3),[0,mp.inf])
out.append("a0=%s a1=%s"%(mp.nstr(a0,12),mp.nstr(a1,12)))
# (다): omega=6.98, k>=10000
w=mp.mpf('6.98'); k=mp.mpf(10000)
val=w-mp.mpf(7)/2-(4*w+mp.mpf(1)/2)*mp.mpf('1.2879')*k**(-mp.mpf(1)/3)-(13*w/2)*mp.mpf('0.939')*k**(-mp.mpf(2)/3)-12*w/k
out.append("(다) lower bound at k=10000 with a0<1.2879,a1<0.939: %s"%mp.nstr(val,8))
# (나)
val2=Fr(699,100)-Fr(7,2)-Fr(6*699,100*31)-Fr(75,100*31)-Fr(13*699,2*100*961)-Fr(12*699,100*30000)
out.append("(나) exact: %s = %.6f ; stated 495594511/240250000 = %.6f"%(val2,float(val2),495594511/240250000))
# 조립: 5.642*1.6809*0.39893-0.0163-3.554
out.append("assembly k>=10000: %.6f"%(5.642*1.6809*0.39893-0.0163-3.554))
out.append("assembly k>=30000: 11/2*39/100*2-7/2 = %.4f"%(5.5*0.39*2-3.5))
out.append("46sqrt2-12=%.5f ; -5000/173-0.02 -> %.4f ; (나): 46sqrt2-12-54.6828=%.5f"%(46*sqrt(2)-12,46*sqrt(2)-12-5000/173-0.02,46*sqrt(2)-12-54.6828))
# Hermite identities (4.9) and M4/M0 with exact rationals
def He_list(N,y,nmax):
    H=[Fr(1),Fr(N)]
    for j in range(2,nmax+1): H.append(N*H[j-1]-(j-1)*y*H[j-2])
    return H
def Mi(i,N,y,n):
    # n! [Y^n] (1-Y)^{i+1} B(Y) up to common factor e^{-y/2}/p_n: return sum_{m} (-1)^m C(i+1,m) n!/(n-m)! He_{n-m}
    H=He_list(N,y,n)
    s=Fr(0); f=1
    for m in range(0,i+2):
        if n-m<0: break
        s+=(-1)**m*comb(i+1,m)*f*H[n-m]
        f*= (n-m)
    return s,H
for k in (50,200):
  for nu in (0,-1):
    n=2*k+nu; y=Fr(k); N=n+y+1
    M0,H=Mi(0,N,y,n); M2,_=Mi(2,N,y,n); M4,_=Mi(4,N,y,n)
    th=H[n]/H[n-1]-n
    r2=M2/M0; f2=(th*((n-y)**2+n)-n*(n+1))/(y**2*th)
    r4=M4/M0
    kk=Fr(k)
    if nu==0: f4=1+16/kk+18/kk**2+2/kk**3-(4+38/kk+22/kk**2+2/kk**3)/th
    else: f4=1+12/kk-6/kk**2-(4+26/kk-14/kk**2)/th
    out.append("k=%d nu=%d: (4.9) exact match %s ; M4/M0 formula match %s ; theta=%.6f ; M2/M0*k=%.5f ; M4/M0*k^2=%.4f"%(k,nu,r2==f2,r4==f4,float(th),float(r2*k),float(r4*k*k)))
# M0 numeric value check for k=200 (needs e^{-y/2}/p_n): skip exactness, compute float
k=200; n=400; y=k; N=n+y+1
M0,H=Mi(0,N,Fr(y),n)
out.append("M0 approx k=200 nu=0: %s (4sqrt2=5.657)"%mp.nstr(mp.mpf(M0.numerator)/mp.mpf(M0.denominator)*mp.e**(-mp.mpf(y)/2)/mp.mpf(n+1)**(n-1),6))
open("C:/math/임시/주차함수_증명/대조v2/수학검사2/_N2_수치_out.txt","w").write("\n".join(out)+"\n")
