# 검토전체14 H10: 10장의 명시 상수·표 값을 본문의 정의 그대로 다시 센다.
# 대상: 명제 old-8-23(DDL♮, j1, j2, 단계 상수), 명제 old-8-25 상수, 보조정리 old-8-34,
#       명제 old-8-35의 o_F, 보조정리 bulk-majorants, 명제 old-8-33의 Stays^up, 명제 check-na 표.
import mpmath as mp
mp.mp.dps = 30
from math import log, sqrt, exp, pi, floor, ceil

def q_rho(r): return 1 + 0.7501*r/(1+r)

# ---- 명제 old-8-23: j1, j2 ----
def j2_int():
    f = lambda s: 2*mp.sqrt(1+s**2)*0.70836*q_rho(s**2)**3
    return mp.quad(f, [0, 1e-6, 0.01, 1])
def j1_int():
    f = lambda s: 2*mp.sqrt(1+s**2)*0.70836*q_rho(s**2)**3*(2.528571 - mp.log(q_rho(s**2)) + 3*mp.log(s))
    return mp.quad(f, [0, 1e-6, 0.01, 1])
J2 = j2_int(); J1 = j1_int()
print("j2 =", J2, " j1 =", J1)

def DDLnat(k):
    k = mp.mpf(k)
    dn = 2*k**(mp.mpf(2)/3)
    eps = -mp.log(1 - mp.sqrt(k+1)/(0.485917*k))
    epsp = 2.26/k + 0.47/(dn-1)
    gam = 2.6047*(2.53 + 0.5*mp.log(k) + eps + 1.5/k)/k
    t1 = 0.457143*(2*mp.pi)**(-0.5)*q_rho(dn/k)*mp.sqrt(1+dn/k)*(dn+1)**3.5/k**3
    t2 = 2*(2*mp.pi)**(-0.5)*k**(-0.5)*(1+epsp)*(J1 + (0.5*mp.log(k)+eps)*J2 + gam)
    t3 = 3.9*(2*mp.pi)**(-0.5)/k
    return t1+t2+t3
for k in [6667, 6668, 8065, 9551, 9705, 9949]:
    print("DDL♮(%d) = %s" % (k, mp.nstr(DDLnat(k), 10)))
print("감소 조건 j1 + j2(log(6667)/2 - 1) =", J1 + J2*(0.5*mp.log(6667)-1))

# old-8-23 단계 상수
print("3*sqrt2*0.16696 =", 3*sqrt(2)*0.16696, " 2.5-log2-log0.485917 =", 2.5-log(2)-log(0.485917))
print("(sqrt2*0.16696)^(1/2) =", (sqrt(2)*0.16696)**0.5)
k=6667.0
print("1.00057 check: (1+1/k)(1+2/k)/(1-3/(4k)) =", (1+1/k)*(1+2/k)/(1-3/(4*k)))
print("0.16696 check: 1.00057^2 (1+2/k)^2/6 =", 1.00057**2*(1+2/k)**2/6)
print("k-bound for 0.7501: (9/8)(1+e^{3/(2k)})/3 =", (9/8)*(1+exp(3/(2*k)))/3)
dn = 2*k**(2/3); rho0 = floor(dn)/k
print("rho0 =", rho0, " q(rho0) =", q_rho(rho0), " floor(dn)^{1.5}/k =", floor(dn)**1.5/k, " 2^{1.5}(1-1/dn)^{1.5}=", 2**1.5*(1-1/dn)**1.5)
iota0 = 2.528571 - log(1.0722) + log(2**1.5*(1-1/dn)**1.5)
print("iota0 >=", iota0, "; sigma0 = e^{-iota0/1.5} =", exp(-3.4964/1.5))
s0 = exp(-3.4964/1.5); r_small = rho0*s0
print("d♮ q^3 at rho0*sigma0:", sqrt(1+r_small)*q_rho(r_small)**3, " (<=1.0288?)")
print("bracket 2*iota0-6-0.1728*sqrt(sigma0) =", 2*3.4964-6-0.1728*sqrt(s0))
print("3.9 check: 2*0.72888*1.3751^2*sqrt2 =", 2*0.72888*1.3751**2*sqrt(2))
print("2.6047 check: sqrt2*0.70836*1.37505^3 =", sqrt(2)*0.70836*1.37505**3)
print("first term const: 2^{3.5} =", 2**3.5, " 1.6*2/7 =", 1.6*2/7)

# ---- old-8-25 상수 ----
c = 2*(2*pi)**-0.5
print("2/sqrt(pi) =", 2/sqrt(pi), " (1.15*6666)^{2/3} =", (1.15*6666)**(2/3))
def Ecoef(u): return c*(0.25*(1-1/778)**-1.5 + (1+u+u*u)*(1-u)**-0.5*(1+u)**-1.5)
print("E coef at u=0.9:", Ecoef(0.9), " at 0.99:", Ecoef(0.99), " at 0.9999:", Ecoef(0.9999))
print("F at u=0.99 bound:", c*3*sqrt(1-0.81), " at 0.9999:", c*(1+2*0.9999**2)*sqrt(1-0.99**2))
print("1.1284+2.82/389 =", 1.1284+2.82/389, " 6.43 check:", c*sqrt(50/0.77))

# ---- 공통 함수 ----
mS = 1.15
def u_k(k): return 3/0.35*(1.35+1/k)*(0.65-1/k)**-1.5*k**-0.5
def BdT(k, nu): return (k+nu)*u_k(k)*(1/(k-1)+1/k) + 3*(k+1)*(k-1)**-1.5
def s_up(d, y): return min(1.0, mS*(y+d)/d**1.5)
def e_c(k, nup): return 3*nup**2/((k-1)*k) + 4.8*sqrt(nup)/k + nup**2/(2*(k-1)**2)
def vartheta_T_band(theta): return (2*exp(-theta)-1)*exp(-theta)
theta0 = vartheta_T_band(0.48); print("vartheta_0 =", theta0)

# ---- 명제 old-8-35 o_F ----
def oF_1a(k): return 2 - e_c(k, 1.3*k**(2/3)) - BdT(k, 1.3*k**(2/3)) - float(DDLnat(k))
def oF_1b(k):
    xi2 = 2*k**(2/3)/(k-1)
    return 4 - 3*s_up(1.3*k**(2/3)+1, k+1) + vartheta_T_band(xi2) - BdT(k, 2*k**(2/3)) - float(DDLnat(k))
def oF_2(k): return 4 - 3*s_up(2*k**(2/3)+1, k+1) + theta0 - BdT(k, 0.48*k) - float(DDLnat(k))
def ebar(k):
    xip = (sqrt(5*k*log(k))+2)/k
    return exp(3/(2*k))*(exp(sqrt(5*log(k)/k)+1/k) + 2.40918*k**(1.5-2.5/(1+xip)))
def oF_bulk(k): return 4 - ebar(k)
print("1a 성분 k=9705: e_c=", e_c(9705,1.3*9705**(2/3)), " BdT=", BdT(9705,1.3*9705**(2/3)), " DDL=", float(DDLnat(9705)), " oF=", oF_1a(9705))
k=9551; xi2 = 2*k**(2/3)/(k-1)
print("1b 성분 k=9551: 3s_up=", 3*s_up(1.3*k**(2/3)+1,k+1), " theta term=", vartheta_T_band(xi2), " BdT=", BdT(k,2*k**(2/3)), " DDL=", float(DDLnat(k)), " oF=", oF_1b(k))
k=8065
print("2 성분 k=8065: 3s_up=", 3*s_up(2*k**(2/3)+1,k+1), " theta0=", theta0, " BdT=", BdT(k,0.48*k), " DDL=", float(DDLnat(k)), " oF=", oF_2(k))
k=6668
print("벌크 k=6668: ebar=", ebar(k), " oF=", oF_bulk(k))
# 0.41508 check
print("(2pi)^{-1/2} 2^{1.5}/e =", (2*pi)**-0.5*2**1.5/exp(1))
# m_hit < 0.09k
print("m_hit(6667)=", ceil(sqrt(5*6667*log(6667))), " 0.09k=", 0.09*6667)

# ---- bulk-majorants ----
def abar(k): return 3*mS*(1.48*k+2)/(0.48*k+1)**1.5
def bbar(k): return 2*u_k(k)*(2*k-1)/(k-1) + 3*(k+1)*(k-1)**-1.5
def dbar(k): return 72.217/sqrt(k)
r=0.48; print("bracket at 0.48:", r**-0.5 - 1 + (1-sqrt(r))/3, " 132.32*that =", 132.32*(r**-0.5 - 1 + (1-sqrt(r))/3), " 4*2*16.54*2 =", 4*16.54*2)
k=6668
print("벌크 상계: abar=", abar(k), " bbar=", bbar(k), " DDL=", float(DDLnat(k)), " dbar=", dbar(k), " sum=", abar(k)+bbar(k)+float(DDLnat(k))+dbar(k), " +ebar=", abar(k)+bbar(k)+float(DDLnat(k))+dbar(k)+ebar(k))

# ---- 명제 old-8-33 Stays^up(k; nubar) ----
def cAb(r): s=sqrt(r); return 2*s/(1-r) + 2*log((1+s)/(1-s))
def Sub(k, nubar):
    xi = (nubar+4)/(k-1)
    if xi >= 0.6: return 0.0
    f = lambda r: (r-xi)*(1+r)*r**-1.5*(1-r)**-2
    return (k-1)/k*float(mp.quad(f, [xi, 0.6]))
def Top(k, nubar):
    f = lambda r: min(2, 2+(nubar+1)/k - r)*(1+r/3)*r**-1.5
    return float(mp.quad(f, [0.6-2.6/k, 1]))
def Flat(y):
    ab = (mS*(y+2*y**(2/3)))**(2/3)
    return 2*(ab-1)/(y+2-ab)
def Ab(y, k, nubar):
    z = 0.6+1/y
    return mS*(1+1/y)*(4*((mS*y)**(2/3)-1)**-0.5 + y**-0.5*(2*cAb(z) - 4*z**-0.5 - Sub(k, nubar)))
def Stays_up(k, nubar):
    tot = 0.0
    for y in (k-1, k):
        tot += Flat(y) + Ab(y, k, nubar)
    return tot + 2*16.54*k**-0.5*Top(k, nubar)
for (k, nubar, name) in [(8065, 0.48*8065, "2"), (9551, 2*9551**(2/3), "1b"), (9705, 1.3*9705**(2/3), "1a")]:
    print("Stays^up family", name, "k=", k, ":", Stays_up(k, nubar), " Flat(k)=", Flat(k), " Ab(k)=", Ab(k,k,nubar), " Top term=", 2*16.54*k**-0.5*Top(k,nubar))
print("2cAb(0.6)-4/sqrt0.6 =", 2*cAb(0.6)-4/sqrt(0.6), " Sub max =", float(mp.quad(lambda r:(1+r)*r**-0.5*(1-r)**-2,[0,0.6])))

# ---- check-na 표 여유 ----
print("여유 2:", oF_2(8065)-Stays_up(8065,0.48*8065))
print("여유 1b:", oF_1b(9551)-Stays_up(9551,2*9551**(2/3)))
print("여유 1a:", oF_1a(9705)-Stays_up(9705,1.3*9705**(2/3)))
print("여유 벌크:", oF_bulk(6668)-(abar(6668)+bbar(6668)+float(DDLnat(6668))+dbar(6668)))

# ---- 가족 첫 열 경계 ----
for k in [9704, 9705, 9550, 9551, 8064, 8065]:
    print(k, "20001-2k=", 20001-2*k, " 1.3k^{2/3}=", 1.3*k**(2/3), " 2k^{2/3}=", 2*k**(2/3), " 0.48k=", 0.48*k)

# ---- 10.3 표: 8065 경계, 9949 ----
print("20001/2.48 =", 20001/2.48, " k=9949: 20001-2k=", 20001-2*9949)

# ---- (가)(a) q0=2 검산 ----
def Bor(m): return float(mp.e**(-m)*mp.mpf(m)**(m-1)/mp.factorial(m))
def Pr_trans(y, q, qp): return Bor(q-qp)*Bor(y+qp)/Bor(y+q)
def s_chain(y, qmax):
    s = {1: 1.0}
    for q in range(2, qmax+1):
        tot = 1.0
        for qp in range(1, q):
            p = Pr_trans(y, q, qp)
            tot -= p*(1 - y/(y+qp)*s[qp])
        s[q] = tot
    return s
def Ren_star(j): return (2*pi)**-0.5*j**-0.5*exp(-1/(12*j))
def A_up(q0, q): return sqrt(2*pi)/4*exp(1/(12*(q0-q)))*(q0+q)*sqrt(q0-q)
def e_low_R(k0, q0):
    y = k0+1; s = s_chain(y, q0)
    zR = sum(Ren_star(q0-q)*exp(-(q+A_up(q0,q))/y)*s[q] for q in range(1, q0))
    PrBorge = 1 - sum(Bor(j) for j in range(1, q0))
    return k0/(k0+1)*(1-q0/(2*k0))*(max(zR, s[q0]-PrBorge) + Bor(q0))
def e_low(k0, q0):
    return 4*s_chain(k0, q0+1)[q0+1] + 2*e_low_R(k0, q0)
R_sharp = {6668: abar(6668)+bbar(6668)+float(DDLnat(6668))+dbar(6668),
           8065: 3*s_up(2*8065**(2/3)+1, 8066)+BdT(8065,0.48*8065)+float(DDLnat(8065))+Stays_up(8065,0.48*8065),
           9551: 3*s_up(1.3*9551**(2/3)+1, 9552)+BdT(9551,2*9551**(2/3))+float(DDLnat(9551))+Stays_up(9551,2*9551**(2/3)),
           9705: 3+BdT(9705,1.3*9705**(2/3))+float(DDLnat(9705))+Stays_up(9705,1.3*9705**(2/3))}
for k0 in [6668, 8065, 9551, 9705]:
    print("k0=%d R#=%.6f e_low(q0=2)=%.6f margin=%.6f" % (k0, R_sharp[k0], e_low(k0,2), e_low(k0,2)-R_sharp[k0]))
