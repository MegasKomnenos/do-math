from mpmath import mp, mpf, sqrt, pi, log, exp
mp.dps=20
def ub(k): k=mpf(k); return mpf('1.15')/mpf('0.35')*(2+1/k)*(mpf('0.65')-1/k)**(-mpf(3)/2)*k**(-mpf(1)/2)
def DDL(k): k=mpf(k); return 14*(log(3*k)-1)/(5*sqrt(pi*k))+mpf('37.6')/(5*sqrt(pi)*k)
for k in [2001,6667]:
    a=mpf('4.6')/sqrt(k+1); b=2*ub(k); c=DDL(k)/2
    print(k, "4.6/sqrt:",a, "2u_flat:",b, "DDL/2:",c, "v=",2-a-b-c)
print("3*1.3752/sqrt(pi)", 3*mpf('1.3752')/sqrt(pi), "21/(5sqrt pi)", 21/(5*sqrt(pi)))
print("1.3778^2(1+2/2001)^2/6", mpf('1.3778')**2*(1+mpf(2)/2001)**2/6)
print("7(3-log3)+42/sqrt3", 7*(3-log(3))+42/sqrt(3))
