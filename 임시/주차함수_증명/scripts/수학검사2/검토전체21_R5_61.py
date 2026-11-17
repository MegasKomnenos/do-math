# 6.1절 검산: 정리 old-8-25 증명의 수치
from mpmath import mp, mpf, sqrt, pi, findroot, quad, log, exp, floor
mp.dps=30
m=mpf('1.15')
print("q_* bound:", (m*2000)**(mpf(2)/3))
# tau_1: root of (1-t)^{5/2}-1+2t
f=lambda t:(1-t)**(mpf(5)/2)-1+2*t
print("tau_1:", findroot(f, 0.28))
# Mn max
print("2/sqrt(pi):", 2/sqrt(pi))
# check Itg closed form vs numeric for a few kappa
def itg(k):
    tau_k=1-k**(mpf(2)/3)
    g=lambda t: t**(-mpf(3)/2)*min(1-k, k*((1-t)**(-mpf(3)/2)-1))
    return quad(g,[0,tau_k,1])
def Itg_cf(k):
    chi=k**(mpf(1)/3)
    return 2*(1+2*chi**2)*sqrt(1-chi**2)-2*(1-chi**3)
for k in [mpf('0.1'),mpf('0.3535'),mpf('0.7'),mpf('0.9')]:
    print("kappa",k, itg(k), Itg_cf(k))
# Mn(kappa) closed form check
def Mn(k):
    chi=k**(mpf(1)/3)
    return 2*(2*pi)**(-mpf(1)/2)*(1+2*chi**2)*sqrt(1-chi**2)
def Mn2(k):
    return 2*(2*pi)**(-mpf(1)/2)*(1-k)+(2*pi)**(-mpf(1)/2)*Itg_cf(k)
print("Mn check", Mn(mpf('0.5')), Mn2(mpf('0.5')))
# (6.7) coefficient C(chi,q) = 2(2pi)^{-1/2}[1/4 (1-1/(2q))^{-3/2} + (1+chi+chi^2)(1-chi)^{-1/2}(1+chi)^{-3/2}]
def C(chi,q):
    return 2*(2*pi)**(-mpf(1)/2)*(mpf(1)/4*(1-1/(2*q))**(-mpf(3)/2)+(1+chi+chi**2)*(1-chi)**(-mpf(1)/2)*(1+chi)**(-mpf(3)/2))
for chi in ['0.9','0.99','0.9999']:
    print("chi",chi,"C at q=175:",C(mpf(chi),175))
# Mn at chi in (0.9,0.99]: bound 2(2pi)^-1/2 *3*sqrt(1-0.81)
print("Mn bound chi>0.9:", 2*(2*pi)**(-mpf(1)/2)*3*sqrt(1-mpf('0.81')), "actual Mn at 0.9:", Mn(mpf('0.9')**3))
print("Mn at chi=0.99:", Mn(mpf('0.99')**3), "Mn at 0.9999", Mn(mpf('0.9999')**3))
# identity (1-k)(1-k^{2/3})^{-3/2} = (1+chi+chi^2)(1-chi)^{-1/2}(1+chi)^{-3/2}
k=mpf('0.6'); chi=k**(mpf(1)/3)
print("ident", (1-k)*(1-k**(mpf(2)/3))**(-mpf(3)/2), (1+chi+chi**2)*(1-chi)**(-mpf(1)/2)*(1+chi)**(-mpf(3)/2))
# direct-count case: gain(j/q) <= 1.6 j/q for j<=q/50
t=mpf(1)/50
print("gain(0.02)/0.02:", ((1-t)**(-mpf(3)/2)-1)/t)
print("1.6*0.7979/sqrt(50):", mpf('1.6')*mpf('0.7979')/sqrt(50), "1.28/sqrt50", mpf('1.28')/sqrt(50))
print("2(2pi)^-1/2 sqrt(50/0.77):", 2*(2*pi)**(-mpf(1)/2)*sqrt(50/mpf('0.77')))
print("q/50-1/2 >= 0.77 q/50 at q=175:", (175/mpf(50)-mpf(1)/2)/(175/mpf(50)))
print("final:", mpf('1.1284')+mpf('2.82')/175, mpf('1.044')+mpf('9.3')/175, mpf('0.34')+mpf('85')/175, mpf('0.182')+mpf('7.3')*mpf('0.0003'))
# derivative check of 2(2tau-1)/sqrt(tau(1-tau))
from mpmath import diff
F=lambda t: 2*(2*t-1)/sqrt(t*(1-t))
t0=mpf('0.3')
print("deriv", diff(F,t0), t0**(-mpf(3)/2)*(1-t0)**(-mpf(3)/2))
# (6.4): int_0^tau_k tau^{-3/2} gain = [2(2tau-1)+2 sqrt(1-tau)]/sqrt(tau(1-tau))
tk=mpf('0.5')
print("6.4", quad(lambda t:t**(-mpf(3)/2)*((1-t)**(-mpf(3)/2)-1),[0,tk]), (2*(2*tk-1)+2*sqrt(1-tk))/sqrt(tk*(1-tk)))
# 따름정리 old-7-13: 1.15(2k+1)<3k for k>=2000
print("1.15*(2*2000+1)=",1.15*4001, "<6000")
# Rd bound over chi<=0.9 : maximum of C over chi in [0,0.9], q>=175
print("C(0.9,175)=",C(mpf('0.9'),175))
