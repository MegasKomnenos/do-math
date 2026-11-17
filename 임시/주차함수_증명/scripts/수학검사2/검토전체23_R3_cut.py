# R3 검산: 보조정리 cut-rep (가)(다)(라)와 그 뒤 경로 회전 문단의 상수.
import mpmath as mp
mp.mp.dps = 25
def Bor(j): return mp.e**(-j)*mp.mpf(j)**(j-1)/mp.factorial(j)
def Btail(k, Zc): return 1 - sum(mp.e**(-j*Zc)*(j*Zc)**(j-1)/mp.factorial(j) for j in range(1, k+1))
et = lambda phi: mp.e*phi*mp.e**(-phi*mp.cot(phi))/mp.sin(phi)
logetp = lambda phi: 1/phi - 2*mp.cot(phi) + phi/mp.sin(phi)**2   # (log et)' 닫힌 꼴
loget = lambda phi: 1 + mp.log(phi/mp.sin(phi)) - phi*mp.cot(phi)
# (ga): k^{k-1}/k! = (1/pi) int Im T_+ ct^{-k-1} dct, ct = et/e
for k in (1, 3, 8):
    val = mp.quad(lambda phi: phi*mp.e**(-k*(loget(phi)-1))*logetp(phi), [mp.mpf('1e-12'), 0.5, 1, 2, 3, mp.pi-mp.mpf('1e-6')])/mp.pi
    print("(ga) k=%d:" % k, mp.nstr(val, 15), mp.nstr(mp.mpf(k)**(k-1)/mp.factorial(k), 15))
for k, agp in ((6, mp.mpf('0.9')), (15, mp.mpf('0.4'))):
    ptp = mp.e**(1j*agp); xi = ptp*mp.e**(1-ptp)
    lhs = Btail(k, ptp)
    rhs = xi**(k+1)/(mp.pi*ptp)*mp.quad(lambda phi: phi*mp.e**(-k*loget(phi))*logetp(phi)/(et(phi)-xi), [mp.mpf('1e-12'), 0.5, 1, 2, 3, mp.pi-mp.mpf('1e-6')])
    ku = mp.mpf(k)**(-mp.mpf(1)/3); ah = agp/ku; s = ku**mp.mpf('1.5')
    Lh = lambda p_: k*loget(s*p_)
    lg = lambda p_: logetp(s*p_)/(s*p_)
    nu = lambda p_: p_**2*lg(p_)*mp.e**(-Lh(p_))
    qy = lambda p_: k*(et(s*p_)-1)
    Zh = (xi-1)/ku**2
    hl = mp.quad(lambda p_: nu(p_)/(ku*qy(p_)-Zh), [mp.mpf('1e-12')/s, 0.5/s, 1/s, 2/s, 3/s, (mp.pi-mp.mpf('1e-6'))/s])
    rb = mp.log(mp.factorial(k)) - (k+mp.mpf(1)/2)*mp.log(k) + k - mp.log(2*mp.pi)/2
    A_ = (1-ptp)/ku
    phv = k*(1j*agp + (1-ptp) + (1-ptp)**2/2)
    phser = sum((2**(m-1)-2)*ku**(m-3)*(1j*ah)**m/mp.factorial(m) for m in range(3, 60))
    Bt_def = ku**2*lhs*mp.e**(k*(1-ptp)**2/2)/Bor(k)
    Bt_form = mp.sqrt(2/mp.pi)*mp.e**rb*mp.e**(ku*A_)*mp.e**phser*hl
    print("k=%d: Btail=%s  cut-integral=%s | Bt def=%s formula=%s | ph diff=%s" % (k, mp.nstr(lhs, 12), mp.nstr(rhs, 12), mp.nstr(Bt_def, 12), mp.nstr(Bt_form, 12), mp.nstr(abs(phv-phser), 3)))
lm = lambda m: (2+mp.mpf(1)/m)*mp.zeta(2*m)/mp.pi**(2*m)
print("l1,l2,l3:", lm(1), lm(2)*36, lm(3)*405)
print("sum_{m>=5} 2m l_m 2^{2-2m} =", mp.nsum(lambda m: 2*m*lm(m)*mp.mpf(2)**(2-2*m), [5, mp.inf]))
print("log et(1/2) =", mp.log(et(mp.mpf(1)/2)), " sum 2m l_m 4^{1-m} =", mp.nsum(lambda m: 2*m*lm(m)*mp.mpf(4)**(1-m), [1, mp.inf]))
print("1-cos1 =", 1-mp.cos(1), " (9/5)^(2/3) =", (mp.mpf(9)/5)**(mp.mpf(2)/3), " 10/2^(2/3) =", 10/mp.mpf(2)**(mp.mpf(2)/3))
print("10001^(-1/3) =", mp.mpf(10001)**(-mp.mpf(1)/3), " 0.0015/1.25^12 =", mp.mpf('0.0015')/mp.mpf('1.25')**12)
# kernel bounds
o = 1/mp.sqrt(2)
worst_lo, worst_hi = None, None
for m in range(1, 3000):
    Ren = mp.e**(-m)*mp.mpf(m)**m/mp.factorial(m); cb = mp.binomial(2*m, m)/mp.mpf(4)**m
    q = Ren/(o*cb)
    assert 1 + mp.mpf(1)/(25*(2*m-1)) <= q <= 1 + mp.mpf(1)/(12*(2*m-1)), m
print("kernel bounds 1+1/(25(2m-1)) <= Ren/(o cb) <= 1+1/(12(2m-1)) ok for m<3000; m=1 ratio:", mp.e**-1/(o/2))
