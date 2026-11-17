# 검토전체21 R2: 중앙 상쇄 항등식 int F0 = 0, int F1 = 46sqrt2-12, J 선도 적분 3sqrt(2pi), (C3) 수치
from mpmath import mp, mpf, quad, exp, sqrt, pi, inf
mp.dps=20
ninf=2/sqrt(pi)
def Daw(b):  # e^{-b^2/2} int_0^b e^{v^2/2} dv
    return exp(-b*b/2)*quad(lambda v: exp(v*v/2),[0,b])
def BorldR(b):
    return (2-2*b*Daw(b))*exp(b*b/2)
def Pq(z,r):
    mu=1-r*r; return mu*z*z+mu*mu*z**4/4
def F0(z):
    inner=quad(lambda r: r*r*exp((1-r*r)*z*z/2)*Pq(z,r)*BorldR(r*z)/sqrt(2*pi),[0,1])
    return -ninf*z**4*exp(-z*z)*inner
def F1(z):
    inner=quad(lambda r: r*r*exp((1-r*r)*z*z/2)*Pq(z,r)*(mpf(4)/3*r*r*z*z-mpf(2)/3*r*z**4),[0,1])
    return -ninf*z**4*exp(-z*z)*inner
I0=2*quad(F0,[0,2,4,8,14])
I1=2*quad(F1,[0,2,4,8,14])
print('int F0 =',I0)
print('int F1 =',I1,' target 46sqrt2-12 =',46*sqrt(2)-12)
IJ=quad(lambda z: z**3*exp(-z*z/2)*(mpf(4)/15*z**3-z/3),[-inf,inf])
print('J leading =',IJ,' 3sqrt(2pi)=',3*sqrt(2*pi))
# (C3) at omega=6.98, k=10000 with a0<1.2879, a1<0.939
om=mpf('6.98'); k=mpf(10000)
c3=om-mpf(3.5)-(4*om+mpf(0.5))*mpf('1.2879')*k**(-mpf(1)/3)-mpf(13)/2*om*mpf('0.939')*k**(-mpf(2)/3)-12*om/k
print('(C3) bound =',c3)
print('M0 lower nu=0:',4*sqrt(2)*(1-mpf('23.75')/k),' nu=-1:',4*sqrt(2)*(1-mpf('21.25')/k))
print('assembly',mpf('5.642')*mpf('1.6809')*mpf('0.39893')-mpf('0.0163')-mpf('3.554'))
print('J bound',mpf('0.4503')*3*mpf('2.50663')+mpf('1675.2')/k+2e-20, 'sqrt2/pi*e^(1/k)=',sqrt(2)/pi*exp(1/k))
print('kD bound',(46*sqrt(2)-12-mpf('54.6828')-1e-22)*exp(1/k)-1e-19)
print('n_k/n_inf max',(mpf(1.5)+1/(2*k))**1.5*exp(1/(24*k)), 'n_k<',(mpf(1.5)+1/(2*k))**1.5*exp(1/(24*k))*ninf,'Bn<',(mpf(1.5)+1/(2*k))**1.5*exp(1/(24*k))*ninf/sqrt(2*pi))
# max of b*Daw(b)
print('max b*Daw(b) sample', max(b*Daw(mpf(b)) for b in [x/10 for x in range(0,80)]))
