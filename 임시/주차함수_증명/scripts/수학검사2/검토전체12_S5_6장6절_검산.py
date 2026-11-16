# S5 검산: 6.6절의 명시 상수 재계산
from mpmath import mp, mpf, sqrt, exp, log, e, pi, factorial, findroot
mp.dps = 30
c = 1/sqrt(2*pi)
def u(k):
    k = mpf(k)
    return 3/mpf('0.35')*(mpf('1.35')+1/k)*(mpf('0.65')-1/k)**(-mpf(3)/2)*k**(-mpf(1)/2)
def ups(k): k=mpf(k); return mpf(1)/2+5/(2*k)+1/(4*k*k)
gW = 2*exp(mpf('0.0031'))/e
print("gamma_W =", gW)
def dd(k): return gW*ups(k)+u(k)/(e*2**mpf('1.5'))
print("d(3131)=", dd(3131), " gW*ups=", gW*ups(3131), " u/(e 2^1.5)=", u(3131)/(e*2**mpf('1.5')))
print("d(10001)=", dd(10001), " gW*ups=", gW*ups(10001), " u/(e 2^1.5)=", u(10001)/(e*2**mpf('1.5')))
def Low(k, rho):
    k=mpf(k); rho=mpf(rho); eps=k**(-mpf(1)/3)
    br = 2*sqrt(rho)-mpf('2.218')*eps
    return c*k**(mpf(1)/3)*br/(1+rho*eps)*exp(-1/(12*(k+1)))*exp(-rho**2*(1+rho*eps)**mpf('1.5')*exp(1/(4*(k+1)))/(c*br))
print("Low(10001,1.4)=", Low(10001, mpf('1.4')))
print("Low(3131,0.75)=", Low(3131, mpf('0.75')))
def Obar(k, dk):  # dk = (d+1)/k upper
    k=mpf(k); return dd(k)*exp(1+1/(12*k))*(1+dk)**mpf('1.5')
k=mpf(10001); print("Obar(10001) far-window:", Obar(k, mpf('1.4')*k**(-mpf(1)/3)+1/k))
k=mpf(3131); print("Obar(3131) small-k:", Obar(k, mpf('0.75')*k**(-mpf(1)/3)+1/k))
# Psi(14), Fr ratio
def Ren(j): j=mpf(j); return j**j*exp(-j)/factorial(j)
Psi14 = sum(Ren(j) for j in range(1,15))
print("Psi(14)=", Psi14, " Psi(14)/(2e)=", Psi14/(2*e))
def Bor(n): n=mpf(n); return exp(-n)*n**(n-1)/factorial(n)
k=mpf(3131); n=k+15
f1 = sqrt(2*pi)*n**mpf('1.5')*Bor(n); f2=(k/n)**mpf('1.5'); f3=(k+1)/(k+14)
print("Fr factors:", f1, f2, f3, " product=", f1*f2*f3, " *Psi/(2e)=", f1*f2*f3*Psi14/(2*e))
print("0.98872*0.43946=", mpf('0.98872')*mpf('0.43946'))
print("ups*gW at 3131:", ups(3131)*gW, " 0.4345-0.3697=", mpf('0.4345')-mpf('0.3697'))
print("0.3951/(e 2^1.5)=", mpf('0.3951')/(e*2**mpf('1.5')), " 0.0648*e*2^1.5=", mpf('0.0648')*e*2**mpf('1.5'))
# h(D) max
from mpmath import diff
h = lambda D: (1-D)*(1+mpf('0.7183')*D)/(2-D)
Ds=[mpf(i)/10000 for i in range(0,10001)]
mx=max(h(D) for D in Ds); print("max h(D) on [0,1] ~", mx)
print("(1+7/3131)*0.509=", (1+mpf(7)/3131)*mpf('0.509'))
# (6.49)
k=mpf(3131); uu=k**(mpf(1)/3); print("u=k^(1/3)=", uu)
wp = lambda n: mpf('1.99')+mpf('0.59963')*(n+1)**(mpf(2)/3)+mpf('1.24847')*(n+1)**(mpf(1)/3)
lhs = mpf('0.75')*k**(mpf(2)/3); rhs = wp(k+mpf('0.75')*k**(mpf(2)/3))-1
print("(6.49) lhs,rhs,diff:", lhs, rhs, lhs-rhs)
quad = mpf('0.15037')*uu**2-mpf('1.54829')*uu-mpf('1.3314'); print("quadratic at u:", quad)
a,b,cc_= mpf('0.15037'),-mpf('1.54829'),-mpf('1.3314'); print("large root:", (-b+sqrt(b*b-4*a*cc_))/(2*a))
print("wp'(1)=", mpf(2)/3*mpf('0.59963')*2**(-mpf(1)/3)+mpf(1)/3*mpf('1.24847')*2**(-mpf(2)/3))
print("1.30212+0.39976/u+0.41616/u^2=", mpf('1.30212')+mpf('0.39976')/uu+mpf('0.41616')/uu**2)
# (6.50)
k=3131
for d in range(1,15):
    m=k+d
    L=(k-1)*(e*Ren(d+1)-mpf(60)*(d+1)/m)
    R=2*(1+sum(e*Ren(r+1)+mpf(60)*(r+1)/m for r in range(1,d)))
    print("d=%2d L=%.3f R=%.3f"%(d, float(L), float(R)))
# 2.218 constant
print("2+2.61238/12=", 2+mpf('2.61238')/12, " B=2.218*3131^(-1/3)=", mpf('2.218')*mpf(3131)**(-mpf(1)/3))
print("R(1/2) coefficients:", mpf(3)/4-2*c*sqrt(mpf(1)/2), c-2*sqrt(mpf(1)/2))
# (6.8)-related: 1.03 bound e^{3/102}; m>=701 constants
m=mpf(701); d=m**(mpf(2)/3)/2
print("d/m at 701:", d/m, " kfrak=", d**mpf('1.5')/(m-d), " es<=", mpf('0.798')*d**mpf('1.5')/(m-d), " N=", exp(-1/(12*(m-d))))
print("bracket:", exp(-1/(12*(m-d)))*(1-mpf('0.5')-mpf('0.2991'))-mpf('0.7979')*mpf('0.5')*mpf('0.3747'), " e^-1*0.0513=", exp(-1)*mpf('0.0513'))
print("RHS 0.7979*0.5*sqrt(d)/(12(m-d)) =", mpf('0.7979')*mpf('0.5')*sqrt(d)/(12*(m-d)), " 0.025 m^-2/3=", mpf('0.025')*m**(-mpf(2)/3))
print("upper: 1.1212 m^-2/3+1.3036 m^-1/3 =", mpf('1.1212')*m**(-mpf(2)/3)+mpf('1.3036')*m**(-mpf(1)/3), " 0.5/e=", mpf('0.5')/e)
print("(4/3)^1.5=", (mpf(4)/3)**mpf('1.5'), " 1.732 chord:", ((mpf(4)/3)**mpf('1.5')-1)*3)
# 6.6 (나) z bound
print("(e+3/4)/3131=", (e+mpf(3)/4)/3131, " 6.03/3131=", mpf('6.03')/3131, " 3.51/3131=", mpf('3.51')/3131)
