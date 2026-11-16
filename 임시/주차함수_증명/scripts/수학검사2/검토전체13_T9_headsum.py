# 9.1절 정리 head-sum-1 증명의 수치 상수와 H-star-plus 세 영역의 비를 다시 센다.
from mpmath import mp, mpf, sqrt, exp, e, pi, log, binomial, zeta
mp.dps = 30
u1 = mpf(3132)**(-mpf(1)/3); u2 = mpf(19404)**(-mpf(1)/3)
print("u1", u1, "<0.06835:", u1 < mpf('0.06835'))
print("3132^(2/3)", mpf(3132)**(mpf(2)/3), "(k-1)/6", mpf(3131)/6)
qol = mpf(3132)**(mpf(2)/3)/3131
print("q/l max", qol, "c1", (1+qol)**mpf('1.5')*exp(mpf(1)/(12*3131)))
print("4/3 (2pi)^-1/2", mpf(4)/3/sqrt(2*pi), "x1.105", mpf('0.5320')*mpf('1.105'))
print("consts", 2/sqrt(2*pi)/7, 2/sqrt(2*pi)/5, 2/sqrt(2*pi)*mpf('3.2')/3)
print("zeta3/2", zeta(mpf(3)/2), "0.8848 check", (2+zeta(mpf(3)/2)/12)/sqrt(2*pi), "0.7978", 2/sqrt(2*pi))
print("e^-1/12 - e^1/4 /4", exp(-mpf(1)/12)-exp(mpf(1)/4)/4, "x sqrt(2/pi)", (exp(-mpf(1)/12)-exp(mpf(1)/4)/4)*sqrt(2/pi), "3/(2*0.477)", 3/(2*mpf('0.477')))
print("0.8848/sqrt2", mpf('0.8848')/sqrt(2), "0.8848/0.7978", mpf('0.8848')/mpf('0.7978'))
# step 4
print("step4 q/l", mpf('0.03')*u1*mpf('1.0004'), "c1", (1+mpf('0.03')*u1*mpf('1.0004'))**mpf(1.5)*exp(mpf(1)/(12*3131)))
print("uq step4", mpf('1.0004')**2*(mpf('0.03')*u1+u1**3)**2/2)
br4 = mpf('0.11399')*mpf('0.03')+mpf('0.15958')*u1**2+mpf('0.85108')*sqrt(mpf('0.03'))*u1
print("step4 bracket", br4, "x1.0041", br4*mpf('1.0041'))
def c1f(xi,u): l1=1/(1-u**3); return (1+xi*u*l1)**mpf(1.5)*exp(l1*u**3/12)
def Ef(xi,u):
    l1=1/(1-u**3); c1=c1f(xi,u)
    return c1*l1*(mpf('0.5320')*xi**mpf(1.5)*u+mpf('0.7979')*sqrt(xi)*u**3+c1*(mpf('0.625')*xi**2+xi*u**2))/(mpf('0.7978')*sqrt(xi)-mpf('0.8848')*u)
def Phif(xi,u):
    l1=1/(1-u**3); c1=c1f(xi,u); uq=l1**2*(xi*u+u**3)**2/2
    return l1*c1*exp(uq)*(mpf('0.11399')*xi**mpf(3.5)+mpf('0.15958')*xi**mpf(2.5)*u**2+mpf('0.85108')*xi**3*u)
def Lf(xi,u):
    l1=1/(1-u**3)
    return (mpf('0.7978')*sqrt(xi)-mpf('0.8848')*u)*exp(-Ef(xi,u))/(1+(xi*u+u**3)*l1)
def Gf(xi,u): return Phif(xi,u)+u*(mpf('0.5320')*c1f(xi,u)*xi**mpf(1.5)+mpf(1)/5)
print("E(0.03,u1)", Ef(mpf('0.03'),u1), "L denom", 1+(mpf('0.03')*u1+u1**3)*mpf('1.0004'))
print("0.1721*e^-0.0317/1.0024", mpf('0.1721')*exp(-mpf('0.0317'))/mpf('1.0024'), "0.1662/0.01434", mpf('0.1662')/mpf('0.01434'))
print("0.7978 sqrt0.03", mpf('0.7978')*sqrt(mpf('0.03')), "0.8848 u1", mpf('0.8848')*u1)
for p in [mpf(7)/2, mpf(5)/2, 3, mpf(3)/2, 2, 1]:
    print(" p",p,"xi threshold",(mpf('1.11')*p*u1/(p-mpf(1)/2))**2)
c5 = mpf('0.7979')*sqrt(mpf('0.03'))*u1**3/(mpf('0.7978')*sqrt(mpf('0.03'))-mpf('0.8848')*u1)
print("c5 at 0.03", c5, "<=5.68e-4:", c5<=mpf('5.68e-4'))
# step 6
l0=1+mpf(1)/3131
print("1+1/l0", l0, "q/l", u1*l0, "c1", (1+u1*l0)**mpf(1.5)*exp(mpf(1)/(12*3131)), "bound 1.06838^1.5 e", mpf('1.06838')**mpf(1.5)*exp(mpf(1)/(12*3131)))
print("uq", l0**2*(u1+u1**3)**2/2, "1.00032^2(0.06835+0.06835^3)^2/2", mpf('1.00032')**2*(mpf('0.06835')+mpf('0.06835')**3)**2/2, exp(mpf('0.00237')))
print("bracket", mpf('0.11399')+mpf('0.15958')*u1**2+mpf('0.85108')*u1, "Phi bound prod", mpf('1.00032')*mpf('1.10434')*mpf('1.00238')*mpf('0.17292'))
print("Phi(1,u1) actual", Phif(1,u1))
print("Ebar denom", mpf('0.7978')-mpf('0.8848')*mpf('0.06835'), "num bracket", mpf('0.5320')*mpf('0.06835')+mpf('1.10434')*(mpf('0.625')+mpf('0.06835')**2))
print("Ebar", mpf('1.10434')*mpf('1.00032')*(mpf('0.73174')/mpf('0.73732')+mpf('0.000568')))
print("Lbar denom", 1+(mpf('0.06835')+mpf('0.06835')**3)*mpf('1.00032'), "Lbar", mpf('0.73732')*exp(-mpf('1.0970'))/mpf('1.0687'), "ratio", mpf('0.19148')/mpf('0.2303'))
print("R(1,u1) actual", Phif(1,u1)/Lf(1,u1))
# H-star-plus regions (grid, not interval)
import mpmath
best=0
for i in range(0,20001):
    xi = 2*u1**2*(mpf('0.75')/(2*u1**2))**(mpf(i)/20000)
    r = Gf(xi,u1)/Lf(xi,u1)
    if r>best: best=r; bx=xi
print("A max", best, "at xi", bx)
best=0
for i in range(0,4001):
    xi = mpf('0.75')+mpf('0.25')*i/4000
    r = Gf(xi,u2)/Lf(xi,u2)
    if r>best: best=r; bx=xi
print("B max", best, "at xi", bx)
best=0
for i in range(1,2001):
    u = u1*i/2000; xi=2*u**2
    r = Gf(xi,u)/Lf(xi,u)
    if r>best: best=r; bu=u
print("C max", best, "at u", bu, "limit", (mpf(1)/5)/(mpf('0.7978')*sqrt(2)-mpf('0.8848')))
# head-sum-2 (ii)
print("597", mpf(597)**mpf(1.5)+9*597, "598", mpf(598)**mpf(1.5)+9*598)
n=20001; print("m0 at 20001", mpf(n)**(mpf(2)/3)-6*mpf(n)**(mpf(1)/3))
print("19404^(2/3)", mpf(19404)**(mpf(2)/3), "3132^(2/3)*0.75", mpf('0.75')*mpf(3132)**(mpf(2)/3))
print("phi(7/16)", 1-mpf(1.5)*mpf(7)/16+mpf(0.5)*(mpf(7)/16)**2-(1-mpf(7)/16)**mpf(1.5))
print("3/5 e^-1", mpf(3)/5/e)
