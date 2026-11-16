# L13 numeric spot checks for appendix D chapters 7A/7B/8/9/10
from fractions import Fraction as Fr
import math
from mpmath import mp, mpf, quad, log, sqrt, exp, iv, findroot
mp.dps = 40
out = []
def P(*a):
    s = " ".join(str(x) for x in a); out.append(s); print(s)

# 1. integer inequality 10^21*400^10 > 17^21*123^10
L = 10**21 * 400**10; R = 17**21 * 123**10
P("[col-lemma] LHS", L, "%.6e" % L); P("[col-lemma] RHS", R, "%.6e" % R, "LHS>RHS:", L > R)
# chapter bound chain: 17^21 < 6.95e25, 123^10 < 7.93e20
P("[col-lemma] 17^21=%.5e <6.95e25: %s ; 123^10=%.5e <7.93e20: %s" % (17**21, 17**21 < 6.95e25, 123**10, 123**10 < 7.93e20))

# 2. self-consistent constants: a°_m=(m+1)^{m-1}/m!, j*(L)=max{m: a°_{m+1}/a°_m < L}, k_R
def ao(m): return Fr(1) if m==0 else Fr((m+1)**(m-1), math.factorial(m))
for Lf, jexp, kexp, k0 in [(Fr(267,100),82,429,501),(Fr(27,10),220,1855,1855),(Fr(271,100),490,6098,6098)]:
    m = 0
    while ao(m+1)/ao(m) < Lf: m += 1
    jstar = m-1
    kR = max(2*jstar+2, math.ceil(Lf**(jstar+2)/ao(jstar+1)))
    P("[self-consistent] L=%s j*=%d (appendix %d) k_R=%d (appendix %d) k0>=kR: %s" % (Lf, jstar, jexp, kR, kexp, k0>=kR))

# 3. cor-S-prime values with table A0,B0 (upper-rounded)
for y, k0, A0, B0, target in [(Fr(13,100),501,Fr(14708,10000),Fr(98505,1000000),3.247e-4),(Fr(2,25),1855,Fr(25335,10000),Fr(60259,1000000),7.801e-5),(Fr(11,200),6098,Fr(27354,10000),Fr(422,10000),2.275e-4)]:
    xi = Fr(1,k0)
    v = (y-xi)*(y-2*xi-xi*xi)-(1+xi)**2*(A0*xi+B0*y)
    vert = (3*xi+xi*xi)/2+(1+xi)**2*B0/2
    P("[cor-S-prime] k0=%d value=%.6e (>%.3e: %s) vertex=%.5f <= y=%s: %s" % (k0, float(v), target, float(v)>target, float(vert), y, vert<=y))

# 4. AR integrals closed forms at k=6668
k = mpf(6668)
J3 = (k/(2*k+1))**mpf('2.5')*(1-3/sqrt(k)); J4 = (k/(2*k+1))**mpf('2.5')*(1-3/sqrt(k-1))
P("[AR] J3=%s J4=%s" % (mp.nstr(J3,10), mp.nstr(J4,10)))
dbar = mpf('6.62')/sqrt(k)
P("[AR] band req (1+d/2)/(1-d/2)=%s ; bulk req=%s" % (mp.nstr((1+dbar/2)/(1-dbar/2),8), mp.nstr(1+mpf('1.676')*dbar/(2-dbar)+mpf('0.676')*(mpf('0.8825')/sqrt(k)+mpf('0.72')/k+mpf('41.2')*(2/(mpf('0.48')*k-102))**mpf('1.5')),8)))
# AR integrals J1,J2 by quadrature (not interval; sanity)
def J1f(t): 
    v = 1-3/sqrt(k)*(t-1/k)**mpf(-1.5)
    return mpf('2.5')*(1+t+2/k)**mpf(-3.5)*(v if v>0 else 0)
def J2f(t):
    v = 1-3*(k-1)/k**mpf(1.5)*(t-1/k)**mpf(-1.5)
    return mpf('2.5')*(1+t+1/k)**mpf(-3.5)*(v if v>0 else 0)
t01 = 1/k + (3/sqrt(k))**(mpf(2)/3); t02 = 1/k + (3*(k-1)/k**mpf(1.5))**(mpf(2)/3)
J1 = quad(J1f,[t01,1]); J2 = quad(J2f,[t02,(k-1)/k])
P("[AR] J1=%s J2=%s L*=%s" % (mp.nstr(J1,8), mp.nstr(J2,8), mp.nstr(J1+J2+J3+J4,8)))

# 5. band-LP (ga)
P("[band-LP] 0.1113*6668 =", 0.1113*6668)
# 6. H-star-plus limit
P("[H*+] limit = %.5f" % (0.2/(0.7978*math.sqrt(2)-0.8848)))
# 7. M-natural: constants, j1, j2, DDL, decrease condition
P("[M-nat] 3*sqrt2*0.16696 = %s ; 2.5-ln2-ln0.485917 = %s" % (mp.nstr(3*sqrt(2)*mpf('0.16696'),15), mp.nstr(mpf('2.5')-log(2)-log(mpf('0.485917')),15)))
q = lambda r: 1+mpf('0.7501')*r/(1+r)
j2 = quad(lambda s: 2*sqrt(1+s*s)*mpf('0.70836')*q(s*s)**3, [0,1])
j1 = quad(lambda s: 2*sqrt(1+s*s)*mpf('0.70836')*q(s*s)**3*(mpf('2.528571')-log(q(s*s))+3*log(s)), [0,mpf('1e-6'),mpf('0.01'),1])
P("[M-nat] j2=%s j1=%s" % (mp.nstr(j2,16), mp.nstr(j1,16)))
c2pi = 1/sqrt(2*mp.pi)
def DDL(kk):
    kk = mpf(kk); d = 2*kk**(mpf(2)/3)
    eps = -log(1-sqrt(kk+1)/(mpf('0.485917')*kk)); epsp = mpf('2.26')/kk+mpf('0.47')/(d-1)
    gam = mpf('2.6047')*(mpf('2.53')+log(kk)/2+eps+mpf('1.5')/kk)/kk
    return mpf('0.457143')*c2pi*q(d/kk)*sqrt(1+d/kk)*(d+1)**mpf(3.5)/kk**3 + 2*c2pi/sqrt(kk)*(1+epsp)*(j1+(log(kk)/2+eps)*j2+gam) + mpf('3.9')*c2pi/kk
for kk in [6667,6668,8065,9551,9705,9949]:
    P("[M-nat] DDL(%d)=%s" % (kk, mp.nstr(DDL(kk),10)))
P("[M-nat] decrease cond j1+j2(ln6667/2-1)=%s" % mp.nstr(j1+j2*(log(6667)/2-1),12))
# 8. n_X values
for kk in [501,2002,2001]:
    P("[xcert] n_X(%d)=ceil(k^{4/3})=%d" % (kk, math.ceil(Fr(kk)**1 and mpf(kk)**(mpf(4)/3))))
# 9. moment-cert first range count
cnt = sum((13*kk*kk)//100 - 2*kk for kk in range(501,841))
P("[moment] first-range positions sum_{k=501}^{840}(floor(13k^2/100)-2k) =", cnt, "(appendix 19,840,702)")
P("[moment] n_M(841)/841^1.5 =", 20507/841**1.5, " n_M(2000)/2000^1.5 =", 73032/2000**1.5)
# 10. four families eps0
for k0 in [6668,8065,9551,9705]:
    P("[four] eps0(%d)=%d" % (k0, math.floor(2**(2/3)*(k0+1)**(2/3))))
# 11. tail triples (7.12) exact-ish check with mpmath high precision (not rational, sanity)
def Bor(m): return exp(-mpf(m))*mpf(m)**(m-1)/mp.factorial(m)
for K1,M,tf in [(10**4,120,'0.54'),(2*10**4,250,'0.593'),(10**5,300,'0.522'),(10**5,450,'0.548'),(10**6,700,'0.519')]:
    K1=mpf(K1); M=mpf(M); tf=mpf(tf)
    ke = 3*(M-1)/(2*(K1+1))+(M-1)*(3*M-4)/(12*(K1+1)**2)+(M-1)**2/(2*(K1+1)*(K1+2-M))+(M-1)**4/(12*(K1+1)**2*(K1+2-M))
    eke = exp(ke); Bors=[None]+[Bor(s+1) for s in range(0,int(M))]
    minrel=None; minq=None
    for qq in range(2,int(M)+1):
        S = sum(Bors[s+1]*((qq-1-s)+tf*mpf(qq-1-s)**mpf(1.5)) for s in range(0,qq-1))
        F = tf*mpf(qq)**mpf(1.5)-eke*S
        rel = F/(tf*mpf(qq)**mpf(1.5))
        if minrel is None or rel<minrel: minrel=rel; minq=qq
    P("[tail] (K1,M,tf)=(%s,%s,%s) kebar=%s min rel margin=%s at q=%d  all>=0: %s" % (mp.nstr(K1,7),int(M),tf,mp.nstr(ke,4),mp.nstr(minrel,4),minq, minrel>=0))
# 12. polar-PD numbers
P("[polar-PD] 2e^{-5.3146*0.6996}=%s ; 0.0821e^{-3/25233}=%s ; 0.7*2001/2002=%s ; 0.3^1.5/2=%s" % (mp.nstr(2*exp(-mpf('5.3146')*mpf('0.6996')),6), mp.nstr(mpf('0.0821')*exp(-mpf(3)/25233),6), 0.7*2001/2002, 0.3**1.5/2))
open(r"C:\math\임시\주차함수_증명\scripts\수학검사2\검토전체18_L13_numeric_out.txt","w",encoding="utf-8").write("\n".join(out))
