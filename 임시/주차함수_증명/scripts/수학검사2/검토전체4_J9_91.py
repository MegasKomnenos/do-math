# 9.1절 수치 검산 (J9)
from mpmath import mp, mpf, sqrt, exp, log, pi, e, binomial, factorial
mp.dps = 30
# theorem A+ constants
print("e^{-1/12}-e^{1/4}/4 =", exp(-mpf(1)/12)-exp(mpf(1)/4)/4)
print("(2/pi)^{1/2}*0.5990 =", sqrt(2/pi)*mpf('0.5990'))
print("3/(2*0.477) =", 3/(2*mpf('0.477')))
# prop-6 checks: nothing numeric
# psi-two-sided constants
print("2(2pi)^{-1/2} =", 2/sqrt(2*pi))
print("(2pi)^{-1/2}(2+2.61238/12) =", (2+mpf('2.61238')/12)/sqrt(2*pi))
# head-sum-1
k0=3132; u0=mpf(k0)**(-mpf(1)/3); print("upsilon0 =", u0)
print("k^{2/3}/(k-1) at 3132 =", mpf(k0)**(mpf(2)/3)/(k0-1))
print("c1 max (1.0684)^{1.5} e^{1/(12*3131)} =", (1+mpf('0.0684'))**mpf('1.5')*exp(mpf(1)/(12*3131)))
print("4/3 (2pi)^{-1/2} =", (mpf(4)/3)/sqrt(2*pi))
print("constants 0.11399,0.15958,0.85108:", 2/sqrt(2*pi)/7, 2/sqrt(2*pi)/5, 2/sqrt(2*pi)*mpf('3.2')/3)
print("0.8848/sqrt2 =", mpf('0.8848')/sqrt(2), " 0.7978-0.6257=", mpf('0.7978')-mpf('0.6257'))
# step 4
l0=3131; ol=1+mpf(1)/l0
xi=mpf('0.03')
ql=xi*u0*ol; print("q/l at xi=0.03:", ql)
c1=(1+ql)**mpf('1.5')*exp(ol*u0**3/12); print("c1:", c1)
uq=ol**2*(xi*u0+u0**3)**2/2; print("uq:", uq, "e^uq:", exp(uq))
br=mpf('0.11399')*xi+mpf('0.15958')*u0**2+mpf('0.85108')*sqrt(xi)*u0
print("Phi/xi^{5/2} <=", ol*c1*exp(uq)*br, " vs 0.01434; product 1.0004*1.0035*1.0001=", mpf('1.0004')*mpf('1.0035')*mpf('1.0001'))
num=c1*ol*(mpf('0.5320')*xi**mpf('1.5')*u0+mpf('0.7979')*sqrt(xi)*u0**3+c1*(mpf('0.625')*xi**2+xi*u0**2))
print("E at (0.03,u0) with denom 0.1721 sqrt(xi):", num/(mpf('0.1721')*sqrt(xi)), " true E:", num/(mpf('0.7978')*sqrt(xi)-mpf('0.8848')*u0))
print("L denom:", 1+(xi*u0+u0**3)*ol, " L lower:", mpf('0.1721')*exp(-mpf('0.0317'))/mpf('1.0024'))
print("c5 =", mpf('0.7979')*sqrt(xi)*u0**3/(mpf('0.7978')*sqrt(xi)-mpf('0.8848')*u0))
# thresholds
for p in [mpf(7)/2,mpf(5)/2,3,mpf(3)/2,2,1]:
    s=p*mpf('0.8848')*u0/((p-mpf(1)/2)*mpf('0.7978')); print("p",p,"xi threshold",s**2)
# step 6
xi=mpf(1)
ql=xi*u0*ol; c1=(1+ql)**mpf('1.5')*exp(mpf(1)/(12*l0)); uq=ol**2*(xi*u0+u0**3)**2/2
br=mpf('0.11399')+mpf('0.15958')*u0**2+mpf('0.85108')*u0
Phi=ol*c1*exp(uq)*br
print("step6: 1+1/l0",ol," q/l",ql," c1",c1," uq",uq," e^uq",exp(uq)," bracket",br," Phi",Phi)
den=mpf('0.7978')-mpf('0.8848')*u0
brn=mpf('0.5320')*u0+c1*(mpf('0.625')+u0**2)
Ebar=c1*ol*(brn/den+mpf('5.68e-4'))
Lbar=den*exp(-Ebar)/(1+(u0+u0**3)*ol)
print(" den",den," brn",brn," Ebar",Ebar," Lbar",Lbar," Rbar",Phi/Lbar)
# head-sum-2
for m in [597,598]: print(m, mpf(m)**mpf('1.5')+9*m)
n=mpf(20001); print("n^{2/3}-6n^{1/3} at 20001:", n**(mpf(2)/3)-6*n**(mpf(1)/3))
print("19404^{2/3}:", mpf(19404)**(mpf(2)/3), " 0.75*3132^{2/3}:", mpf('0.75')*mpf(3132)**(mpf(2)/3))
print("phi(7/16):", 1-mpf(3)/2*mpf(7)/16+(mpf(7)/16)**2/2-(1-mpf(7)/16)**mpf('1.5'))
print("16/3 k^{1/3} >= 39 -> k^{1/3} >=", mpf(39)*3/16)
# H*+ t=k+1
print("3/5 e^{-1} =", mpf(3)/5/e)
# region C limit
print("C limit:", mpf('0.2')/(mpf('0.7978')*sqrt(2)-mpf('0.8848')))
# centroid: pi_2(t) check small t
for t in [2,4,6]:
    print("pi2",t, 2*binomial(t,t//2)/mpf(2)**t, " sqrt(8/(pi t))", sqrt(8/(pi*t)))
# check b_{k,k-1}=k^{k-2} by brute force small k via A recursion
def A(n,l,memo={}):
    if l<0: return 0
    if n==0: return 1
    key=(n,l)
    if key in memo: return memo[key]
    s=0
    for t in range(1,n+1):
        s+=binomial(n-1,t-1)*min(t,l+1)*A(t-1,l)*A(n-t,l)
    memo[key]=s; return s
for k in range(2,8):
    print(k, A(k,k-1)-A(k,k-2), k**(k-2))
