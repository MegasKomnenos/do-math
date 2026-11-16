# O9: numeric re-check of 9.2-9.5 constants.
from mpmath import mp, mpf, sqrt, exp, log, quad, pi, ceil, floor, e
mp.dps = 25
k = mpf(6668)
# 9.2: pi_2 bound
print("sqrt(8/(pi*6669))", sqrt(8/(pi*6669)))
# 9.3 (1): L_*(6668)
def J1(k):
    f=lambda t: (1+t+2/k)**(-mpf(3.5))*max(0,1-3*k**(-mpf(0.5))*(t-1/k)**(-mpf(1.5)))
    t0=1/k+(3/sqrt(k))**(mpf(2)/3)
    return mpf(2.5)*quad(f,[t0,0.5,1])
def J2(k):
    c=3*(k-1)*k**(-mpf(1.5))
    f=lambda t: (1+t+1/k)**(-mpf(3.5))*max(0,1-c*(t-1/k)**(-mpf(1.5)))
    t0=1/k+c**(mpf(2)/3)
    return mpf(2.5)*quad(f,[t0,0.5,(k-1)/k])
J3=(k/(2*k+1))**mpf(2.5)*(1-3/sqrt(k)); J4=(k/(2*k+1))**mpf(2.5)*(1-3/sqrt(k-1))
print("J1..J4",J1(k),J2(k),J3,J4," L*",J1(k)+J2(k)+J3+J4)
# 9.3 (2): constants
print("(2pi)^-1/2 e^-1/24 e^-1/(12*3334)", (2*pi)**-mpf(0.5)*exp(-mpf(1)/24)*exp(-1/(12*mpf(3334))))
jstar=ceil((3*k)**(mpf(2)/3)); print("j*",jstar)
print("first region lhs 4.85[...]", mpf('4.85')*(sqrt(k)*((3*k)**(mpf(2)/3)+2)**-mpf(0.5)-sqrt(2)))
print("second region 6.1224*0.95^-1.5", mpf('6.1224')*mpf('0.95')**-mpf(1.5))
print("third: 16.35*(1/0.95)^1.5/0.05 *(1+1/k)^1.5 =", mpf('16.35')*(mpf(1)/mpf('0.95'))**mpf(1.5)/mpf('0.05')*(1+1/k)**mpf(1.5), " 353.3/k vs 6.62/sqrt k:", mpf('353.3')/k, mpf('6.62')/sqrt(k))
print("third endpoint 2:", mpf('5.45')*k**-mpf(0.5)*(1+1/k)**mpf(1.5)*k/(k-jstar-1))
print("12/0.734",12/mpf('0.734'))
# (3) requirement values
dbar=mpf('6.62')/sqrt(k)
print("band req", (1+dbar/2)/(1-dbar/2))
bulk=1+mpf('1.676')*dbar/(2-dbar)+mpf('0.676')*(mpf('0.8825')/sqrt(k)+mpf('0.72')/k+mpf('41.2')*(2/(mpf('0.48')*k-102))**mpf(1.5))
print("bulk req", bulk)
print("103*(2pi)^-1/2*e^(1/(12*6670))", 103*(2*pi)**-mpf(0.5)*exp(1/(12*mpf(6670))))
print("(2/0.48)^1.5*(2pi)^-1/2", (2/mpf('0.48'))**mpf(1.5)*(2*pi)**-mpf(0.5))
# 9.4 constants
def u_(k): return 3/mpf('0.35')*(mpf('1.35')+1/k)*(mpf('0.65')-1/k)**-mpf(1.5)*k**-mpf(0.5)
def Ups(k): return (k-1)*u_(k)/(2*k+1)
def v_(k):  # need v'_k and iota_k from ch6; skip, use 0.7654 lower bound
    return mpf('0.7654')
Uk=Ups(k); print("hatUps(6668)",Uk)
mu=Uk/(mpf(1.5)*(1-mpf('1.2')/k)*(v_(k)+Uk*(k+1)/k))
print("k mu/(1-mu)", k*mu/(1-mu), " 0.1113k", mpf('0.1113')*k, " k^{1/3} mu/(1-mu)", k**(mpf(1)/3)*mu/(1-mu))
rhoH=(1-mpf(1.5)/k)*mpf('0.1535')-47/(24*k)
print("k rhoH(3k+1)",rhoH," Y(3k+1)", rhoH*v_(k)-Uk*(1-(1+1/k)*rhoH))
k2=mpf(48966); print("hatUps(48966)",Ups(k2)," (1-1/k)^103/20",(1-1/k2)**103/20)
k3=mpf(48965); print("hatUps(48965)",Ups(k3)," (1-1/k)^103/20",(1-1/k3)**103/20)
print("(i): k rhoL(0.112k)",mpf(1.5)*mpf('0.112')/mpf('1.112')," k rhoH", (1-mpf(1.5)/k)*mpf('0.307')/mpf('1.112')-47/(24*k))
print("dY/dnu const", mpf(1.5)*(1-mpf('1.2')/k)*mpf('0.7654')/mpf('1.2366'))
# 9.5 constants
print("psi-low: (2pi)^-1/2*(2.61238/12+1.46036)", (2*pi)**-mpf(0.5), mpf('1.46036')+mpf('2.61238')/12)
print("0.398942*1.67806-0.3989*1.678", mpf('0.398942')*mpf('1.67806')-mpf('0.3989')*mpf('1.678'))
print("Psi(1)=1/e",1/e," 0.3989*0.322",mpf('0.3989')*mpf('0.322'))
print("a lower bound 0.48k-1-8k^(2/3)", mpf('0.48')*k-1-8*k**(mpf(2)/3), " e^-1/(12*366)",exp(-1/(12*mpf(366))))
print("(2pi)^-1/2 e^-1/12",(2*pi)**-mpf(0.5)*exp(-mpf(1)/12))
print("2/(3*6667)",2/(3*mpf(6667)))
print("0.08*k^(2/3)-1", mpf('0.08')*k**(mpf(2)/3)-1)
print("4k^(2/3) vs 6(k-1)^(2/3)", 4*k**(mpf(2)/3), 6*(k-1)**(mpf(2)/3))
