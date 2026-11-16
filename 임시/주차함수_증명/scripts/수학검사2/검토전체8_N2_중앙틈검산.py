# 검토전체8 N2: 4.3절 Gauss형 계수·Hermite 수·상수 검산 (mpmath 사용). python -I 로 실행.
import mpmath as mp
from fractions import Fraction
mp.mp.dps = 60

def hermite_ratios(n, y):
    """He_j(y,n) 를 비 upsilon_j 로 계산. 반환: (N, [upsilon_1..upsilon_n], log He_n, log He_{n-1}, He_n/He_{n-1})"""
    N = n + y + 1
    x = y / N**2
    ups = [mp.mpf(1)]
    for j in range(2, n+1):
        ups.append(1 - (j-1)*x/ups[-1])
    logHe = [mp.mpf(0)]
    for j in range(1, n+1):
        logHe.append(logHe[-1] + mp.log(N*ups[j-1]))
    return N, ups, logHe

def M_r(n, y, r, logHe, N):
    """(4.4): M_r = n!/p_n [Y^n](1-Y)^{r+1} B(Y) e^{-y/2};  [Y^m]B = He_m/m!  -> (1-Y)^{r+1} 전개"""
    s = mp.mpf(0)
    for i in range(r+2):
        m = n - i
        if m < 0: continue
        # n! * He_m/m! * C(r+1,i)(-1)^i
        s += (-1)**i * mp.binomial(r+1, i) * mp.exp(logHe[m] + mp.loggamma(n+1) - mp.loggamma(m+1))
    return s * mp.exp(-y/2) / mp.mpf(n+1)**(n-1)

def check(k, nu, theta=0):
    n = 2*k + nu; y = mp.mpf(k) - theta
    N, ups, logHe = hermite_ratios(n, y)
    vartheta = N*ups[n-1] - n
    M0 = M_r(n,y,0,logHe,N); M2 = M_r(n,y,2,logHe,N); M4 = M_r(n,y,4,logHe,N)
    # (4.9)
    rhs49 = 1 - 2*n/y + n*(n+1)/y**2 - n*(n+1)/(y**2*vartheta)
    # M4/M0 닫힌 꼴 (y=k, theta=0)
    kk = mp.mpf(k)
    if nu == 0:
        rhs4 = 1 + 16/kk + 18/kk**2 + 2/kk**3 - (4 + 38/kk + 22/kk**2 + 2/kk**3)/vartheta
        center = 4 - 26/kk + 506/kk**2
    else:
        rhs4 = 1 + 12/kk - 6/kk**2 - (4 + 26/kk - 14/kk**2)/vartheta
        center = 4 - 22/kk + 414/kk**2
    print(f"k={k} nu={nu} theta={theta}: vartheta={mp.nstr(vartheta,15)}  center={mp.nstr(center,15)}  |diff|*k^2={mp.nstr(abs(vartheta-center)*kk**2,6)}")
    print(f"   (4.9) M2/M0={mp.nstr(M2/M0,15)} rhs={mp.nstr(rhs49,15)}  k*M2/M0={mp.nstr(kk*M2/M0,10)}")
    if theta == 0:
        print(f"   M4/M0={mp.nstr(M4/M0,15)} closed={mp.nstr(rhs4,15)}  k^2*M4/M0={mp.nstr(kk**2*M4/M0,10)}")
    print(f"   M0={mp.nstr(M0,12)}  4sqrt2(1-26/k)={mp.nstr(4*mp.sqrt(2)*(1-26/kk),12)}  g_k=2-kM2/M0={mp.nstr(2-kk*M2/M0,10)}")
    # l: U = N*ups_circ(q), q = n*x
    x = y/N**2; q = n*x; upc = (1+mp.sqrt(1-4*q))/2; U = N*upc; l = U - n
    print(f"   l={mp.nstr(l,12)} in [2-2/k,2]: {2-2/kk <= l <= 2}")

for k in (50, 300):
    for nu in (0,-1):
        check(k, nu)
for k in (10000, 30000):
    for nu in (0,-1):
        check(k, nu)
        check(k, nu, theta=1)

# 적분 상수 a_0, a_1
a0 = mp.quad(lambda w: mp.exp(-w**3/3), [0, mp.inf]); a1 = mp.quad(lambda w: w*mp.exp(-w**3/3), [0, mp.inf])
print("a0 =", mp.nstr(a0,12), " (1.287899,1.2879):", 1.287899<a0<1.2879, "  a1 =", mp.nstr(a1,12), " (0.938892,0.939):", 0.938892<a1<0.939)
# 따름정리 (나) 유리수
F=Fraction
val = F(699,100)-F(7,2)-F(6*699,100*31)-F(75,100*31)-F(13*699,200*961)-F(12*699,100*30000)
print("(나) 값:", val, "==495594511/240250000:", val==F(495594511,240250000), float(val))
# 따름정리 (다)
om = mp.mpf('6.98'); km13 = mp.mpf('0.0464159'); km23 = km13**2; a0u=mp.mpf('1.2879'); a1u=mp.mpf('0.939')
lb = om - mp.mpf(7)/2 - (4*om+mp.mpf(1)/2)*a0u*km13 - mp.mpf(13)*om/2*a1u*km23 - 12*om/10000
print("(다) 하계:", mp.nstr(lb,10), " >=1.6809:", lb>=mp.mpf('1.6809'))
# 정리 4-5 마무리 수치
print("5.642*1.6809*0.39893-0.0163-3.554 =", mp.nstr(mp.mpf('5.642')*mp.mpf('1.6809')*mp.mpf('0.39893')-mp.mpf('0.0163')-mp.mpf('3.554'),10))
print("46sqrt2-12 =", mp.nstr(46*mp.sqrt(2)-12,10), " -5000/173-0.02:", mp.nstr(46*mp.sqrt(2)-12-mp.mpf(5000)/173-mp.mpf('0.02'),8), " -54.6828:", mp.nstr(46*mp.sqrt(2)-12-mp.mpf('54.6828'),8))
print("0.4503*3*2.50663+0.16752 =", mp.nstr(mp.mpf('0.4503')*3*mp.mpf('2.50663')+mp.mpf('0.16752'),8))

# 중앙 상쇄 항등식: int F_0 = 0, int F_1 = 46sqrt2-12
ninf = 2/mp.sqrt(mp.pi)
def dawson(b): return mp.sqrt(mp.pi/2)*mp.exp(-b**2/2)*mp.erfi(b/mp.sqrt(2))
def BorldR(b): return mp.exp(b**2/2)*(2-2*b*dawson(b))
def Pq(z,r): mu=1-r*r; return mu*z*z+mu*mu*z**4/4
def F0(z):
    inner = mp.quad(lambda r: r*r*mp.exp((1-r*r)*z*z/2)*Pq(z,r)*BorldR(r*z)/mp.sqrt(2*mp.pi), [0,1])
    return -ninf*z**4*mp.exp(-z*z)*inner
def F1(z):
    inner = mp.quad(lambda r: r*r*mp.exp((1-r*r)*z*z/2)*Pq(z,r)*(mp.mpf(4)/3*r*r*z*z-mp.mpf(2)/3*r*z**4), [0,1])
    return -ninf*z**4*mp.exp(-z*z)*inner
mp.mp.dps = 25
I0 = 2*mp.quad(F0,[0,2,4,8,15]); I1 = 2*mp.quad(F1,[0,2,4,8,15])
print("int F0 =", mp.nstr(I0,8), "  int F1 =", mp.nstr(I1,10), "  46sqrt2-12 =", mp.nstr(46*mp.sqrt(2)-12,10))
# Bor^ld 적분 정의와 Dawson 표현의 일치 (베타 몇 점)
for b in (mp.mpf('0.5'), mp.mpf(2)):
    direct = 2 + mp.quad(lambda i: i**(-mp.mpf(3)/2)*(1-mp.exp(b*b*i/2)), [0,1])
    print("Bor^ld_R 직접 vs Dawson:", mp.nstr(direct,10), mp.nstr(BorldR(b),10))
