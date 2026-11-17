# 검토전체25 R9: 9.6절 명제 check-na 표와 check-ga 표의 닫힌 꼴 조각을 mpmath로 재계산
from mpmath import mp, mpf, sqrt, log, exp, pi, quad, floor, ceil
mp.dps = 30
mS = mpf('1.15')

def u(k): return mpf(3)/mpf('0.35')*(mpf('1.35')+mpf(1)/k)*(mpf('0.65')-mpf(1)/k)**(-1.5)*mpf(k)**(-0.5)
def BdT(k, nu): return (k+nu)*u(k)*(mpf(1)/(k-1)+mpf(1)/k)+3*(k+1)*mpf(k-1)**(-1.5)
def DDL(k): return 14*(log(3*k)-1)/(5*sqrt(pi*k))+mpf('37.6')/(5*sqrt(pi)*k)
def sup(d, y): return min(mpf(1), mS*(y+d)/mpf(d)**1.5)
def ec(k, nup): return 3*nup**2/((k-1)*k)+mpf('4.8')*sqrt(nup)/k+nup**2/(2*(k-1)**2)
def ebar(k):
    xi = (sqrt(5*k*log(k))+2)/k
    return exp(mpf(3)/(2*k))*(exp(sqrt(5*log(k)/k)+mpf(1)/k)+mpf('2.40918')*mpf(k)**(1.5-2.5/(1+xi)))
def cAb(r): return 2*sqrt(r)/(1-r)+2*log((1+sqrt(r))/(1-sqrt(r)))
def Sub(k, nub):
    xs = (nub+4)/mpf(k-1)
    if xs >= mpf('0.6'): return mpf(0)
    return mpf(k-1)/k*quad(lambda r: (r-xs)*(1+r)*r**(-1.5)*(1-r)**(-2), [xs, mpf('0.6')])
def Flat(y):
    a = (mS*(y+2*mpf(y)**(mpf(2)/3)))**(mpf(2)/3)
    return 2*(a-1)/(y+2-a)
def Ab(y, k, nub):
    z = mpf('0.6')+mpf(1)/y
    return mS*(1+mpf(1)/y)*(4*((mS*y)**(mpf(2)/3)-1)**(-0.5)+mpf(y)**(-0.5)*(2*cAb(z)-4*z**(-0.5)-Sub(k, nub)))
def Top(k, nub):
    lo = mpf('0.6')-mpf('2.6')/k
    kink = (nub+1)/mpf(k)
    f = lambda r: min(mpf(2), 2+kink-r)*(1+r/3)*r**(-1.5)
    pts = [lo, 1] if not (lo < kink < 1) else [lo, kink, 1]
    return quad(f, pts)
def StaysUp(k, nub):
    return sum(Flat(y)+Ab(y, k, nub) for y in (k-1, k))+2*mpf('16.54')*mpf(k)**(-0.5)*Top(k, nub)
def abar(k): return 3*mS*(mpf('1.48')*k+2)/(mpf('0.48')*k+1)**1.5
def bbar(k): return 2*u(k)*mpf(2*k-1)/(k-1)+3*(k+1)*mpf(k-1)**(-1.5)
def dbar(k): return mpf('72.217')/sqrt(k)

t23 = lambda k: mpf(k)**(mpf(2)/3)
print("== 벌크 k0=6668")
k = 6668
print(" 4-ebar", 4-ebar(k), " abar", abar(k), " bbar", bbar(k), " DDL", DDL(k), " dbar", dbar(k))
RB = abar(k)+bbar(k)+DDL(k)+dbar(k)
print(" 합", RB, " 여유", 4-ebar(k)-RB, " 좌변(합+ebar)", RB+ebar(k))
print("== 가족 2 k0=8065")
k = 8065
a = 3*sup(2*t23(k)+1, k+1); th0 = (2*exp(mpf('-0.48'))-1)*exp(mpf('-0.48'))
print(" 3sup", a, " theta0", th0, " BdT", BdT(k, mpf('0.48')*k), " DDL", DDL(k))
o2 = 4-a+th0-BdT(k, mpf('0.48')*k)-DDL(k); S2 = StaysUp(k, mpf('0.48')*k)
print(" o_F", o2, " StaysUp", S2, " 여유", o2-S2, " Rsharp", a+BdT(k, mpf('0.48')*k)+DDL(k)+S2)
print("== 가족 1b k0=9551")
k = 9551
a = 3*sup(mpf('1.3')*t23(k)+1, k+1); xs2 = 2*t23(k)/(k-1); th = (2*exp(-xs2)-1)*exp(-xs2)
o = 4-a+th-BdT(k, 2*t23(k))-DDL(k); S = StaysUp(k, 2*t23(k))
print(" 3sup", a, " theta", th, " BdT", BdT(k, 2*t23(k)), " DDL", DDL(k))
print(" o_F", o, " StaysUp", S, " 여유", o-S, " Rsharp", a+BdT(k, 2*t23(k))+DDL(k)+S, " Rsharp'", BdT(k, 2*t23(k))+DDL(k)+S)
print("== 가족 1a k0=9705")
k = 9705
nb = mpf('1.3')*t23(k)
o = 2-ec(k, nb)-BdT(k, nb)-DDL(k); S = StaysUp(k, nb)
print(" ec", ec(k, nb), " BdT", BdT(k, nb), " DDL", DDL(k))
print(" o_F", o, " StaysUp", S, " 여유", o-S, " Rsharp", 3+BdT(k, nb)+DDL(k)+S, " Rsharp'", BdT(k, nb)+DDL(k)+S)
print("== 그 밖의 상수")
print(" f1", 4/(3*sqrt(2*pi)), " cR", sqrt(2*pi)/2*exp(mpf(1)/12), " beta0 하한", sqrt(2*pi)/2*exp(mpf(1)/12)*mpf('1.04')**1.5/sqrt(2))
print(" DDL(2001,6668,8065,9551,9705)", [DDL(x) for x in (2001, 6668, 8065, 9551, 9705)])
print(" 가족 첫 열: 1a", 20001-2*9705, mpf('1.3')*t23(9705), 20001-2*9704, mpf('1.3')*t23(9704))
print("            1b", 20001-2*9551, 2*t23(9551), 20001-2*9550, 2*t23(9550))
print("            2 ", 20001-2*8065, mpf('0.48')*8065, 20001-2*8064, mpf('0.48')*8064)
print(" eps0:", [int(floor(mpf(2)**(mpf(2)/3)*mpf(k0+1)**(mpf(2)/3))) for k0 in (6668, 8065, 9551, 9705)])
print(" (2k)^(2/3) at 13334:", mpf(13334)**(mpf(2)/3), " 증인 식:", mpf('0.99')+mpf('0.59963')*mpf(13335)**(mpf(2)/3)+mpf('1.24847')*mpf(13335)**(mpf(1)/3))
print(" 0.54577 대괄호:", mpf('0.48')**(-0.5)-1+(1-sqrt(mpf('0.48')))/3, " 132.32*:", mpf('132.32')*(mpf('0.48')**(-0.5)-1+(1-sqrt(mpf('0.48')))/3))
print(" pi_two 상수:", (2*pi)**(-0.5)*exp(-1)*mpf(2)**1.5, " 1/0.41508:", 1/mpf('0.41508'))
print(" mhit(6667):", ceil(sqrt(5*6667*log(6667))), 0.09*6667)
print(" 2cAb(0.6)-4/sqrt(0.6):", 2*cAb(mpf('0.6'))-4/sqrt(mpf('0.6')), " int:", quad(lambda r: (1+r)*r**(-0.5)*(1-r)**(-2), [0, mpf('0.6')]))
print(" 0.7999:", 2/sqrt(2*pi)*sqrt(mpf(103)/mpf('102.5')), " ge(1.0216):", exp(mpf('-1.0216'))*(1+1.5*mpf('1.0216')))
