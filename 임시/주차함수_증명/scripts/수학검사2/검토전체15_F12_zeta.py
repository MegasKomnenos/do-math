from mpmath import mp, iv, mpf
iv.dps=30
def zeta32_iv(C):
    S=iv.mpf(0)
    for j in range(1,C): S+=iv.mpf(j)**iv.mpf(-1.5)
    lo=S+2*iv.mpf(C)**iv.mpf(-0.5)+iv.mpf(0.5)*iv.mpf(C)**iv.mpf(-1.5)
    hi=S+2*(iv.mpf(C)-iv.mpf(0.5))**iv.mpf(-0.5)
    return lo.a, hi.b
print("zeta32 C=2000:", zeta32_iv(2000))
mp.dps=30
S=sum(mpf(j)**mpf(-1.5) for j in range(1,2001))
print("sparse lower C=2000:", S+2*mpf(2001)**mpf(-0.5), " upper:", S+2*mpf(2000.5)**mpf(-0.5))
print("zeta(-1/2)=",mp.zeta(-0.5), " ZM12_ABS-|z|=", mpf('0.2078862250607')+mp.zeta(-0.5))
