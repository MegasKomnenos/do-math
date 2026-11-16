# -*- coding: utf-8 -*-
"""검토전체7 M13: 부록 D 장7A·7B·8·9·10 항목의 다시 셀 수 있는 수치를 센다.
python -I 로 실행. 외부 자료는 읽지 않는다(세션_재계산 폴더는 읽기만 한다)."""
from fractions import Fraction as F
from math import ceil, floor, log, exp, sqrt, cos, pi, isqrt
import json, os, sys
from decimal import Decimal, getcontext
getcontext().prec = 60

def out(*a):
    print(*a)

# ---------- D.column-certification-k500 ----------
out("=== D.column-certification-k500")
L = 10**21 * 400**10
R = 17**21 * 123**10
out("10^21*400^10 =", L, "~%.6e" % L)
out("17^21*123^10 =", R, "~%.6e" % R, "L>R:", L > R)
def B(k): return -(-k*k // 4)
direct_a = sum(2*B(k) - (2*k+1) + 1 for k in range(121, 161))
direct_b = sum(2*B(k) - (2*k+1) + 1 for k in range(161, 501))
ratio_a = sum(2*B(k) - B(k) + 1 for k in range(121, 161))
ratio_b = sum(2*B(k) - B(k) + 1 for k in range(161, 501))
out("직접 차분 비교 수: 작성자", direct_a, "(글 386,260) 검토", direct_b, "(글 19,982,310)")
out("비 비교 수: 작성자", ratio_a, "(글 198,790) 검토", ratio_b, "(글 10,103,865)")

# ---------- D.self-consistent-constants ----------
out("=== D.self-consistent-constants")
def a_circ(m):  # (m+1)^(m-1)/m!
    from math import factorial
    if m == 0:
        return F(1)
    return F((m+1)**(m-1), factorial(m))
def jstar(Lf):
    m = 0
    while True:
        r = a_circ(m+1)/a_circ(m)
        if r >= Lf:
            return m-1
        m += 1
def kR(Lf):
    j = jstar(Lf)
    v = Lf**(j+2) / a_circ(j+1)
    return max(2*j+2, ceil(v)), j
for Lf, J, k0 in [(F(267,100),25,501),(F(27,10),70,1855),(F(271,100),100,6098)]:
    kr, j = kR(Lf)
    out("L=%s j*=%d (표 %s) k_R=%d" % (Lf, j, {F(267,100):82,F(27,10):220,F(271,100):490}[Lf], kr))
# cor-S-prime values with table (rounded-up) constants
for (k0, y, A0, B0) in [(501, F(13,100), F('1.4708'), F('0.098505')), (1855, F(2,25), F('2.5335'), F('0.060259')), (6098, F(11,200), F('2.7354'), F('0.0422'))]:
    xi = F(1, k0)
    val = (y - xi)*(y - 2*xi - xi*xi) - (1+xi)**2*(A0*xi + B0*y)
    vert = (3*xi + xi*xi)/2 + (1+xi)**2*B0/2
    out("k0=%d 세 값(표 올림값)=%.6e  꼭짓점 조건 %.6f <= y=%.4f: %s" % (k0, float(val), float(vert), float(y), vert <= y))

# ---------- D.band102-integer (ㄱ) counts ----------
out("=== D.band102-integer")
unordered = sum(1 for q in range(1, 51) for qp in range(q, 51) for j in range(0, 51) if q+qp+j <= 50)
ordered = sum(1 for q in range(1, 51) for qp in range(1, 51) for j in range(0, 51) if q+qp+j <= 50)
out("순서 없는 쌍 수", unordered, "(글 10,725); 순서쌍 수", ordered, "(글 20,825)")
# (ㄱ) minimum value check at (1,33,16), k=10000
k = 10000
def pis(q): return F(q*(q-1), 2*(k+1))
def exb(q): return q + (k+q)*pis(q)/(1-pis(q))
def rhs(q, qp, j): return 1 - F(j, k)*(exb(q)+exb(qp)) - (exb(q)*(qp-1)+exb(qp)*(q-1))/(2*k)
best = min(((rhs(q,qp,j), (q,qp,j)) for q in range(1,51) for qp in range(q,51) for j in range(0,51) if q+qp+j<=50))
out("(ㄱ) 최솟값", float(best[0]), best[1], "(글 0.04926 at (1,33,16))")
# (ㅁ) strip counts
F2cols = 11099-9981+1
F2cmp = sum(2*kk+40 - max(20001, 2*kk+1) + 1 for kk in range(9981, 11100))
out("F2 열", F2cols, "(글 1119) 비교", F2cmp, "(글 44,380)")
s58cols = 11999-9972+1
s58cmp = sum(58 - max(41, 20001-2*kk) + 1 for kk in range(9972, 12000) if 58 >= max(41, 20001-2*kk))
out("strip58 열", s58cols, "(글 2028) 비교", s58cmp, "(글 36,432)")
sA = sum(102 - max(59, max(41, 20001-2*kk)) + 1 for kk in range(9950, 12000))
sA2 = sum(102 - 59 + 1 for kk in range(9950, 12000))
out("strip102 A 열", 12000-9950, "(글 2050) 비교(59부터)", sA2, "비교(max(41,20001-2k)부터 where >59)", sA, "(글 89,738)")
out("B", 1000*44, "C", 1000*23, "D", 1000*7, "(글 44,000 23,000 7,000)")
out("strip 합계 열", s58cols+2050+3000, "(글 7078) 비교", s58cmp+sA2+44000+23000+7000, "(글 200,170)")
# (나)(다) coverage of 명제 integer-strips (나): 9950..11999, max(2k+41,20001)..2k+102
need_na = sum(2*kk+102 - max(2*kk+41, 20001) + 1 for kk in range(9950, 12000))
out("(나) 위치 수", need_na)
F1 = sum(2*kk+19 - 20001 + 1 for kk in range(9991, 10000) if 2*kk+19 >= 20001)
out("F1 위치", F1, "(글 81)")

# ---------- D.moment-certification counts ----------
out("=== D.moment-certification")
A3 = sum(13*kk*kk//100 - (2*kk+1) + 1 for kk in range(501, 841))
out("(A3) 위치 수", A3, "(글 19,840,702)")
nMpath = r"C:\math\임시\주차함수_증명\원고_자료\세션_재계산\moment_cert_iv\nM.json"
if os.path.exists(nMpath):
    with open(nMpath, encoding="utf-8") as f:
        nM = json.load(f)
    try:
        if isinstance(nM, dict):
            items = {int(a): (b if isinstance(b, int) else (b.get("nM") if isinstance(b, dict) else b)) for a, b in nM.items() if str(a).isdigit()}
        else:
            items = {int(d["k"]): int(d["nM"]) for d in nM}
        A5 = sum(items[kk]-1 - 10001 + 1 for kk in range(841, 2001))
        out("(A5) 위치 수", A5, "(글 40,638,833); nM(841)=", items.get(841), "nM(2000)=", items.get(2000))
        rat = [items[kk]/kk**1.5 for kk in range(841, 2001)]
        out("nM/k^1.5 범위 [%.5f, %.5f]" % (min(rat), max(rat)))
    except Exception as e:
        out("nM.json 구조 파악 실패:", type(nM), str(e)[:200], str(nM)[:300])
else:
    out("nM.json 없음")
out("20507/841^1.5 =", 20507/841**1.5, " 73032/2000^1.5 =", 73032/2000**1.5)

# ---------- D.m1-column-reading counts ----------
out("=== D.m1-column-reading")
tot = sum((n-3) - (-(-(n-1)//2)) + 1 for n in range(5, 20001))
out("전체 위치", tot, "(글 99,970,002)")
pairs = sum(1 for kk in range(3132, 19404) for m in range(kk + floor(0.75*kk**(2/3)), min(2*kk-1, 20000)+1))
out("(2) 쌍 수", pairs, "(글 88,933,203)")
pairs3 = sum(1 for kk in range(3132, 19404) for m in range(kk + floor(kk**(2/3)), min(2*kk-1, 20000)+1))
out("(3) 쌍 수", pairs3, "(글 86,939,621)")
out("(4) (3288-3136)/3136^(2/3) =", (3288-3136)/3136**(2/3))

# ---------- D.band-LP counts ----------
out("=== D.band-LP")
out("(나) k 수", 48965-38887+1, "(글 10079); (다)", 38886-9467+1, "(글 29420); (라)", 9466-6668+1, "(글 2799)")
out("0.1113*6668 =", 0.1113*6668)

# ---------- D.four-families ----------
out("=== D.four-families")
for k0 in (6668, 8065, 9551, 9705):
    out("k0", k0, "eps0 =", floor(2**(2/3)*(k0+1)**(2/3)))

# ---------- D.M-natural-integrals ----------
out("=== D.M-natural-integrals")
out("3*sqrt2*0.16696 =", Decimal(3)*Decimal(2).sqrt()*Decimal("0.16696"))
out("2.5-ln2-ln0.485917 =", Decimal("2.5") - Decimal(2).ln() - Decimal("0.485917").ln())
# integrals by mpmath if available
try:
    import mpmath as mp
    mp.mp.dps = 30
    q = lambda r: 1 + mp.mpf("0.7501")*r/(1+r)
    j2 = mp.quad(lambda s: 2*mp.sqrt(1+s*s)*mp.mpf("0.70836")*q(s*s)**3, [0, 1])
    j1 = mp.quad(lambda s: 2*mp.sqrt(1+s*s)*mp.mpf("0.70836")*q(s*s)**3*(mp.mpf("2.528571")-mp.log(q(s*s))+3*mp.log(s)), [0, mp.mpf("1e-8"), mp.mpf("1e-4"), mp.mpf("0.01"), 1])
    out("j2 =", j2, "(글 2.7171998...)")
    out("j1 =", j1, "(글 0.7998716...)")
    def DDL(k):
        k = mp.mpf(k)
        d = 2*k**(mp.mpf(2)/3)
        epsn = -mp.log(1 - mp.sqrt(k+1)/(mp.mpf("0.485917")*k))
        epsp = mp.mpf("2.26")/k + mp.mpf("0.47")/(d-1)
        gam = mp.mpf("2.6047")*(mp.mpf("2.53") + mp.log(k)/2 + epsn + mp.mpf("1.5")/k)/k
        c = 1/mp.sqrt(2*mp.pi)
        return mp.mpf("0.457143")*c*q(d/k)*mp.sqrt(1+d/k)*(d+1)**mp.mpf("3.5")/k**3 + 2*c/mp.sqrt(k)*(1+epsp)*(j1 + (mp.log(k)/2+epsn)*j2 + gam) + mp.mpf("3.9")*c/k
    for k0 in (6667, 6668, 8065, 9551, 9705, 9949):
        out("DDL(%d) =" % k0, mp.nstr(DDL(k0), 12))
    out("감소 조건 j1+j2(ln6667/2-1) =", j1 + j2*(mp.log(6667)/2 - 1))
    # D.AR-integrals closed forms
    out("=== D.AR-integrals")
    k = mp.mpf(6668)
    J3 = (k/(2*k+1))**mp.mpf("2.5")*(1-3/mp.sqrt(k))
    J4 = (k/(2*k+1))**mp.mpf("2.5")*(1-3/mp.sqrt(k-1))
    out("J3 =", J3, "J4 =", J4)
    f1 = lambda t: mp.mpf("2.5")*(1+t+2/k)**(-mp.mpf("3.5"))*max(0, 1-3/mp.sqrt(k)*(t-1/k)**(-mp.mpf("1.5")))
    f2 = lambda t: mp.mpf("2.5")*(1+t+1/k)**(-mp.mpf("3.5"))*max(0, 1-3*(k-1)/k**mp.mpf("1.5")*(t-1/k)**(-mp.mpf("1.5")))
    t01 = 1/k + (3/mp.sqrt(k))**(mp.mpf(2)/3)
    t02 = 1/k + (3*(k-1)/k**mp.mpf("1.5"))**(mp.mpf(2)/3)
    J1 = mp.quad(f1, [t01, 1]); J2 = mp.quad(f2, [t02, (k-1)/k])
    out("J1 =", J1, "J2 =", J2, "sum =", J1+J2+J3+J4)
    db = mp.mpf("6.62")/mp.sqrt(k)
    out("띠 요구값 (1+d/2)/(1-d/2) =", (1+db/2)/(1-db/2))
    bulk = 1 + mp.mpf("1.676")*db/(2-db) + mp.mpf("0.676")*(mp.mpf("0.8825")/mp.sqrt(k) + mp.mpf("0.72")/k + mp.mpf("41.2")*(2/(mp.mpf("0.48")*k-102))**mp.mpf("1.5"))
    out("벌크 요구값 =", bulk)
    # (2) upper function max
    def upf(qq):
        N = k+qq
        return min(1, 3*k*mp.mpf(qq)**(-mp.mpf("1.5")))/(k*(mp.mpf("0.734")*max(0,(qq+1)**(-mp.mpf("0.5")) - (mp.ceil(N/2)+1)**(-mp.mpf("0.5"))) + mp.mpf("0.98")/(N+1)))
    best = max((upf(qq), qq) for qq in range(1, 6668))
    out("상계 함수 최댓값", best[0]*mp.sqrt(k), "at q=", best[1], "(글 6.06908/sqrt k at q=6666)")
    # D.H-star-plus C limit
    out("=== D.H-star-plus-interval")
    out("(1/5)/(0.7978*sqrt2-0.8848) =", mp.mpf("0.2")/(mp.mpf("0.7978")*mp.sqrt(2)-mp.mpf("0.8848")))
    out("3132^(-1/3) =", mp.mpf(3132)**(-mp.mpf(1)/3), " 19404^(-1/3) =", mp.mpf(19404)**(-mp.mpf(1)/3))
    # D.stored-table-check seams
    out("=== D.stored-table-check")
    jinf = lambda x: mp.mpf(4)/3/mp.sqrt(2*mp.pi)*mp.mpf(x)**mp.mpf("1.5")
    out("e^{-j(2)} =", mp.exp(-jinf(2)), " e^{-j(2.1)} =", mp.exp(-jinf(mp.mpf("2.1"))))
    out("zeta(1/2), zeta(-1/2), zeta(3/2):", mp.zeta(0.5), mp.zeta(-0.5), mp.zeta(1.5))
    # D.polar-blocks: Gamma(5/3), C_h
    out("=== D.polar-blocks-488")
    out("Gamma(5/3) =", mp.gamma(mp.mpf(5)/3), " C_h = sqrt(pi)*(2/3)*Gamma(1/3) =", mp.sqrt(mp.pi)*mp.mpf(2)/3*mp.gamma(mp.mpf(1)/3))
    out("5.5/10.9^2 =", 5.5/10.9**2, " min(0.17, ..) =", min(0.17, 5.5/10.9**2))
    # D.xcert (6): Xc
    out("=== D.xcert-partAB (6)")
    pc = 1/mp.sqrt(2*mp.pi)/mp.e
    S0 = sum(mp.mpf(n-1)**(n-1)*mp.exp(-n)/mp.factorial(n) for n in range(1, 257))
    Xc = 1 - S0 - 2*pc/mp.sqrt(257) + pc*mp.mpf(257)**(-mp.mpf("1.5"))
    out("S^(0) =", S0, " Xc =", Xc, "(글 0.367943)")
    # 2002 vs 5.3146 statements
    out("k^{1/3}/3.31 at k=1e30:", mp.mpf(10)**10/mp.mpf("3.31"))
except ImportError:
    out("mpmath 없음")

# ---------- D.window-mass-env grid ----------
out("=== D.window-mass-env")
out("floor(6*1e5^(2/3)) =", floor(6*(10**5)**(2/3)), " 12927/1e5^(2/3) =", 12927/(10**5)**(2/3))
out("q/6600^(2/3) at q=2999:", 2999/6600**(2/3))

# ---------- D.bprime / band boxes ----------
out("=== D.bprime-boxes / band-boxes")
ks = [6668]
while ks[-1] < 10**12:
    ks.append(ceil(1.04*ks[-1]))
out("k 격자 점 수(6668부터 1.04배, 1e12 넘는 첫 점 포함)", len(ks), "마지막", ks[-1], "(글 480개, k_last=1001931059908)")
ks2 = [100000]
while ks2[-1] < 10**12:
    ks2.append(ceil(1.04*ks2[-1]))
out("k 격자 (1e5부터)", len(ks2), "마지막", ks2[-1], "(글 411개, 1001739455221)")
out("3.6*6668^(2/3) =", 3.6*6668**(2/3), " 0.48*6935=", 0.48*6935, " 6*6668^(2/3)=", 6*6668**(2/3))

# ---------- D.Q-fin ----------
out("=== D.Q-fin-1130")
out("n_X(y)=ceil(y^{4/3}) for y=2001:", ceil(2001**(4/3)), " 3131:", ceil(3131**(4/3)))
out("=== D.column-certificates-841-2000")
for kk in (501, 840, 841, 2000):
    out("k=%d ceil(0.836 k^1.5) = %d" % (kk, ceil(0.836*kk**1.5)))
