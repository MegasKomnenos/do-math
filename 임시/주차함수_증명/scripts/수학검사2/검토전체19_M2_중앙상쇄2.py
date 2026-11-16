# 순수 파이썬: int F0 (중앙 상쇄 항등식, 0이어야 함)과 int F1 (= 46 sqrt2 - 12 이어야 함)을 Simpson 으로 확인.
import math
# Dawson 표: D' = 1 - b D, D(0)=0, RK4
H=1e-4; BMAX=9.5; N=int(BMAX/H)
Dt=[0.0]*(N+1)
d=0.0
for i in range(N):
    b=i*H
    f=lambda bb,dd: 1-bb*dd
    k1=f(b,d); k2=f(b+H/2,d+H*k1/2); k3=f(b+H/2,d+H*k2/2); k4=f(b+H,d+H*k3)
    d+=H*(k1+2*k2+2*k3+k4)/6; Dt[i+1]=d
def Daw(b):
    x=b/H; i=int(x); 
    if i>=N: i=N-1
    t=x-i; return Dt[i]*(1-t)+Dt[i+1]*t
def BorldR(b): return math.exp(b*b/2)*(2-2*b*Daw(b))
ninf=2/math.sqrt(math.pi); c=1/math.sqrt(2*math.pi)
def simpson(f,a,b,m):
    h=(b-a)/m; s=f(a)+f(b)
    for i in range(1,m):
        s+= (4 if i%2 else 2)*f(a+i*h)
    return s*h/3
def Pq(z,r): mu=1-r*r; return mu*z*z+mu*mu*z**4/4
def inner0(z): return simpson(lambda r: r*r*math.exp((1-r*r)*z*z/2)*Pq(z,r)*c*BorldR(r*z),0,1,400)
def inner1(z): return simpson(lambda r: r*r*math.exp((1-r*r)*z*z/2)*Pq(z,r)*((4/3)*r*r*z*z-(2/3)*r*z**4),0,1,400)
F0=lambda z: -ninf*z**4*math.exp(-z*z)*inner0(z)
F1=lambda z: -ninf*z**4*math.exp(-z*z)*inner1(z)
I0=2*simpson(F0,0,9,900); I1=2*simpson(F1,0,9,900)
print('Dawson check D(1)=',Daw(1.0),'(ref 0.7340...? for this normalization sqrt2*dawsn(1/sqrt2)=', 'see below)')
print('int F0 =',I0,'(claimed 0); scale of |F0| integral:', 2*simpson(lambda z: abs(F0(z)),0,9,900))
print('int F1 =',I1,'claimed 46sqrt2-12 =',46*math.sqrt(2)-12)
