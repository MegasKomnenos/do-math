# K12: D.tilt-sum-small-k (정확 유리수), D.prop-W-thirteen (40자리), D.theorem-U (ㅅ) 조립 산술
from fractions import Fraction as F
from math import factorial
import mpmath as mp
mp.mp.dps=40
def tiltsum(k):
    return sum(F(n**(n-1),factorial(n))*F(k,k+1)**((k-1)*n) for n in range(2,k+2))
mx=0
for k in range(2,61):
    v=tiltsum(k); assert v<1
    if k in (2,3,10,20,42,43): print("k",k,"sum=",float(v), "exact 8/9" if v==F(8,9) else "")
    mx=max(mx,v)
print("max over 2..60 is at k=2:", mx==tiltsum(2))
# prop W thirteen
def eRen(r1): # e*Ren(r+1) = (r+1)^r/(e^r r!)
    r=r1-1; return mp.mpf(r1)**r/(mp.e**r*mp.factorial(r))
for d in range(1,15):
    L=3130*(eRen(d+1)-mp.mpf(60)*(d+1)/(3131+d))
    R=2*(1+sum(eRen(r+1)+mp.mpf(60)*(r+1)/(3131+d) for r in range(1,d)))
    print(d, mp.nstr(L,6), mp.nstr(R,5), "L>R" if L>R else "FAIL")
# theorem-U assembly
c=1/mp.sqrt(2*mp.pi); G=mp.mpf('2.7323'); m=mp.mpf('0.8051')
print("3c(8.133+10.301c)=",mp.nstr(3*c*(mp.mpf('8.133')+mp.mpf('10.301')*c),7)," 1.5*G*m*c*(17.951+23.462c)=",mp.nstr(1.5*G*m*c*(mp.mpf('17.951')+mp.mpf('23.462')*c),7))
print("with iv upper:",mp.nstr(3*c*(mp.mpf('8.13091')+mp.mpf('10.29939')*c),7), mp.nstr(1.5*G*m*c*(mp.mpf('17.94855')+mp.mpf('23.46002')*c),7))
print("32000:",mp.nstr(3*c*(mp.mpf('8.12798')+mp.mpf('10.28899')*c)+1.5*G*m*c*(mp.mpf('17.94110')+mp.mpf('23.44135')*c),7))
