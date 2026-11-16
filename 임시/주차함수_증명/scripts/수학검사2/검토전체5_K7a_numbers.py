# K7a 검산: n_M 비, polar-PD의 수치, hermite-nu(다)의 d >= 4-(26+4nu)/k, H_3, 두 보정 상수
import math, sympy as sp
from mpmath import mp, mpf, sqrt as msqrt
print("n_M(841)/841^1.5 =",20507/841**1.5," n_M(2000)/2000^1.5 =",73032/2000**1.5)
# polar-PD
k=2001; l=math.ceil(0.3*k)
print("l",l,"(k+1-l)/(k+1)=",(k+1-l)/(k+1), "0.3^1.5/2=",0.3**1.5/2, "2e^{-5.3146*0.6996}=",2*math.exp(-5.3146*0.6996))
nx=math.ceil(2002**(4/3)); print("n_X(2002)=",nx, "0.0821e^{-3/nx}=",0.0821*math.exp(-3/nx), "varsigma needed:", math.log(2/0.0820)/0.6996)
# hermite: d lower bound check
mp.dps=50
def Hval(k,nu,th):
    k=mpf(k);nu=mpf(nu);th=mpf(th)
    N=3*k+nu+1-th; x=(k-th)/N**2; xn=(2*k+nu-1)*x
    g=msqrt(1-4*xn); up=(1+g)/2
    C1=(1-up)/g**2; C2=-(1-up)*(2+up)/g**5; C3=mpf(5)/2*(1-up)*(6+g-g**2)/g**8
    uh=up+x*C1+x**2*C2+x**3*C3
    return k*((N/k)*uh-2-nu/k)
for nu in [1,19,40,102,300,600]:
    for kk in [10000,11100,15000,10**6]:
        H=Hval(kk,nu,0); lb=4-(26+4*nu)/kk
        print("k",kk,"nu",nu,"H",float(H),"4-(26+4nu)/k",lb,"H-lb",float(H-lb), "err 9400/k^3", 9400/kk**3)
# H_3 symbolic
w,nu,th=sp.symbols('w nu theta')
Nk=3+(nu+1-th)*w; x=w*(1-th*w)/Nk**2; xn=(2+(nu-1)*w)*(1-th*w)/Nk**2
g=sp.sqrt(1-4*xn); up=(1+g)/2
C1=(1-up)/g**2; C2=-(1-up)*(2+up)/g**5; C3=sp.Rational(5,2)*(1-up)*(6+g-g**2)/g**8
H=(Nk*(up+x*C1+x**2*C2+x**3*C3)-2-nu*w)/w
ser=sp.expand(sp.series(H,w,0,4).removeO())
print("H_3 =",sp.expand(ser.coeff(w,3)))
# vertical-nu (마) constants
print("(3/2+1/20000)^1.5=",(1.5+1/20000)**1.5, "1.84*2/sqrt(pi)=",1.84*2/math.sqrt(math.pi), "2.08/sqrt(2pi)=",2.08/math.sqrt(2*math.pi))
# counts integer-strips
ca=sum(max(0,2*k+40-max(20001,2*k+1)+1) for k in range(9981,11100))
cb=sum(max(0,2*k+102-max(2*k+41,20001)+1) for k in range(9950,12000))
cc=1000*44+1000*23+1000*7
print("counts (가)",ca,"(나)+(다)",cb+cc)
# C M^1.5
for M,C in [(700,0.519),(450,0.548),(300,0.522),(250,0.593),(120,0.54)]:
    print(M,C,C*M**1.5)
# M_0 lower bound sum
print("sum first-order:", (600+4)/2, "generic: 0.5nu+2 + nu+3 + 0.75 + 10 + 6.5+nu + 1.5 =", 2+3+0.75+10+6.5+1.5)
