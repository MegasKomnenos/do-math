from mpmath import mp, mpf, sqrt, pi, log, exp, e, floor
mp.dps=20
k=mpf(2001); eps=k**(-mpf(1)/3)
Db=3*eps/(6-2*eps)
print("eps",eps,"Dbar",Db, "1.041k<=R?", mpf('1.041')*k, floor(3*(k-1)/2))
UB=(2*pi)**(-mpf(1)/2)*(1+Db)**mpf(1.5)*(mpf(4)/3*(3/(6-2*eps))**mpf(1.5)+sqrt(Db)*eps**mpf(1.5))
print("UBbar(2001)",UB)
sb=mpf('1.15')*sqrt(2)*(3*k-1)*k**(-mpf(1.5)); print("sbar(2001)",sb)
def ub(k): k=mpf(k); return mpf('1.15')/mpf('0.35')*(2+1/k)*(mpf('0.65')-1/k)**(-mpf(3)/2)*k**(-mpf(1)/2)
def u(k): k=mpf(k); return 3/mpf('0.35')*(mpf('1.35')+1/k)*(mpf('0.65')-1/k)**(-mpf(3)/2)*k**(-mpf(1)/2)
print("prefactor",4000/mpf(6002), "final", mpf('0.6664')*(1-mpf('0.2099')-mpf('0.1091'))-mpf('0.2808'), "1/6",mpf(1)/6)
for kk in [2001,10001]:
    print(kk,"u/(e 2^1.5)",u(kk)/(e*2**mpf(1.5)), "d=",1/e+u(kk)/(e*2**mpf(1.5)))
print("2+2.61238/12",2+mpf('2.61238')/12)
B=mpf('2.218')*eps; print("B",B, "R(1/2)", mpf(3)/4-2*B*mpf(0.5)**mpf(1.5)-2*(2*pi)**(-mpf(0.5))*sqrt(mpf(0.5))+(2*pi)**(-mpf(0.5))*B, "coeffs", 2*mpf(0.5)**1.5, 2*(2*pi)**(-0.5)*sqrt(0.5), (2*pi)**(-0.5))
print("3/sqrt2",3/sqrt(2),"2.218*4^-1/3",mpf('2.218')*4**(-mpf(1)/3))
