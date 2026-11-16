# H13 검산: D.M-natural-integrals 의 두 적분과 DDL^natural
import mpmath as mp
mp.mp.dps = 30
q = lambda r: 1+mp.mpf('0.7501')*r/(1+r)
c1 = mp.mpf('0.70836'); c2 = mp.mpf('2.528571')
# 치환 rho = s^2
j2 = mp.quad(lambda s: 2*mp.sqrt(1+s*s)*c1*q(s*s)**3, [0, 1])
j1 = mp.quad(lambda s: 2*mp.sqrt(1+s*s)*c1*q(s*s)**3*(c2-mp.log(q(s*s))+3*mp.log(s)), [0, mp.mpf(1)/1000, 1])
print("j2 =", mp.nstr(j2, 16), " j1 =", mp.nstr(j1, 16))
print("3sqrt2*0.16696 =", mp.nstr(3*mp.sqrt(2)*mp.mpf('0.16696'), 15), " 2.5-ln2-ln0.485917 =", mp.nstr(mp.mpf('2.5')-mp.log(2)-mp.log(mp.mpf('0.485917')), 12))
def DDL(k):
    k = mp.mpf(k); d = 2*k**(mp.mpf(2)/3)
    eps = -mp.log(1-mp.sqrt(k+1)/(mp.mpf('0.485917')*k)); epsp = mp.mpf('2.26')/k+mp.mpf('0.47')/(d-1)
    gam = mp.mpf('2.6047')*(mp.mpf('2.53')+mp.log(k)/2+eps+mp.mpf('1.5')/k)/k
    c = (2*mp.pi)**(-mp.mpf(1)/2)
    return mp.mpf('0.457143')*c*q(d/k)*mp.sqrt(1+d/k)*(d+1)**(mp.mpf(7)/2)/k**3 + 2*c/mp.sqrt(k)*(1+epsp)*(j1+(mp.log(k)/2+eps)*j2+gam) + mp.mpf('3.9')*c/k
for k in (6667, 6668, 8065, 9551, 9705, 9949):
    print("DDL(%d) = %s" % (k, mp.nstr(DDL(k), 10)))
print("감소 조건:", mp.nstr(j1+j2*(mp.log(6667)/2-1), 14))
