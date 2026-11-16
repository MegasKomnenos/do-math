# G12 검산: 부록 D(장2~6) 항목의 작은 수치들을 독립 재계산한다.
import sys, io, math
from fractions import Fraction
from itertools import permutations, product
from math import comb, factorial
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.setrecursionlimit(10000)

# 마지막 차 재귀로 A_{n,l}, b_{n,l} (n<=N)
def rows(N):
    A = [[0]*(N+1) for _ in range(N+1)]  # A[n][l]
    for l in range(N+1):
        A[0][l] = 1
        for n in range(1, N+1):
            A[n][l] = sum(comb(n-1,j)*min(j+1,l+1)*A[j][l]*A[n-1-j][l] for j in range(n))
    b = [[A[n][l]-(A[n][l-1] if l>0 else 0) for l in range(N+1)] for n in range(N+1)]
    return A, b

A, b = rows(80)
for n in range(1, 81):
    assert sum(b[n][l] for l in range(n)) == (n+1)**(n-1)
print("n=80:", b[80][39], b[80][40], b[80][41])
print(" b39*b41-b40^2 >0:", b[80][39]*b[80][41]-b[80][40]**2 > 0)
print(" ratios:", b[80][40]/b[80][39], b[80][41]/b[80][40])
print(" separator 25928/25000:", b[80][40]*25000 < 25928*b[80][39], b[80][41]*25000 > 25928*b[80][40])
# n<=79 logconcave
bad=[(n,l) for n in range(1,80) for l in range(1,n-1) if b[n][l]**2 < b[n][l-1]*b[n][l+1]]
print(" LC violations n<=79:", bad)
bad80=[l for l in range(1,79) if b[80][l]**2 < b[80][l-1]*b[80][l+1]]
print(" LC violations n=80:", bad80)

# 중앙 틈 (ㄴ): d_{n,k_n} for n<=20, right-half nonincreasing; crossing b_{k}<b_{k+1} for 5<=n<=25
print("d_{n,k_n} sign, right half nonincreasing (k_n<=j<=n-2), b_k<b_{k+1}:")
for n in range(1, 26):
    k = -(-n//2)
    d = (b[n][k] if k<=n-1 else 0) - b[n][k-1]
    rh = all(b[n][j] >= b[n][j+1] for j in range(k, n-1))
    cross = (k+1 <= n-1) and b[n][k] < b[n][k+1]
    leftstrict = all(b[n][l] < b[n][l+1] for l in range(0, k-1))
    print(f"  n={n:2d} k={k:2d} d={'<0' if d<0 else ('=0' if d==0 else '>0')} rightNonInc={rh} b_k<b_k+1={cross} leftStrict={leftstrict}")

# Q_L(n) for 3<=n<=15
for n in range(3,16):
    ok = all((not (b[n][l]>b[n][l+1])) or b[n][l+1]**2 >= b[n][l]*b[n][l+2] for l in range(0, n-2) if 2*l <= n-2)
    assert ok
print("Q_L(3..15) all ok")

# 섬유 전수 n<=7
def fibers(n):
    seen = {}
    nonuni = []
    for s in permutations(range(1,n+1)):
        h=[]
        for i in range(n):
            j = max([jj for jj in range(i) if s[jj]>s[i]], default=-1)
            h.append(i-j)
        key = tuple(sorted(h))
        if key in seen: 
            if not seen[key]: nonuni.append(s)
            continue
        Acum=[math.prod(min(hi,l+1) for hi in h) for l in range(n)]
        row=[Acum[0]]+[Acum[l]-Acum[l-1] for l in range(1,n)]
        peak=row.index(max(row))
        uni = all(row[i]<=row[i+1] for i in range(peak)) and all(row[i]>=row[i+1] for i in range(peak,n-1))
        seen[key]=uni
        if not uni: nonuni.append(s)
    return len(seen), nonuni
for n in range(1,8):
    cnt, nonuni = fibers(n)
    print(f"n={n}: distinct capacity multisets={cnt}, nonunimodal fibers={len(nonuni)}", (nonuni[0] if nonuni else ''))

# 섬유 비단봉 상계: n=17 exact rational, b=3
def bound(n, bb):
    tot1=Fraction(0); tot2=Fraction(0)
    for c in range(n//2+1, n+1):
        kap = n-c-bb+1
        if kap<0: continue
        base = Fraction(factorial(n), factorial(c))*c**(c-1)/Fraction((n+1)**(n-1))
        t1 = base*Fraction(bb*(n-c+1)**kap, (n-c+1)*factorial(kap)) if True else 0
        # (n-c+1)^{n-c-b} = (n-c+1)^{kap-1}
        t1 = base*Fraction(bb, factorial(kap))*Fraction((n-c+1))**(kap-1)
        t2 = base*Fraction(2, factorial(kap))*Fraction((n-c-bb+3))**(kap-1)
        tot1+=t1; tot2+=t2
    return 1-tot1+tot2
def allowed(n,bb):
    return all((k+1)**(i-1)*k+(k-1)**i-2*k**i<0 for i in range(3,bb+1) for k in range(n//2+1,n+1))
for bb in range(3,8):
    print(f"n=17 b={bb} allowed={allowed(17,bb)} bound={float(bound(17,bb)):.10f}")

# theorem-D-base pairs count
print("pairs 4<=m<=700, 8d^3<=m^2:", sum(1 for m in range(4,701) for d in range(1,100) if 8*d**3<=m*m))
print("d_max(700):", max(d for d in range(1,100) if 8*d**3<=700**2), " d_max(689):", max(d for d in range(1,100) if 8*d**3<=689**2))

# induction-rows floor at m=10001
print("floor(3/4 m^{2/3}) m=10001:", max(f for f in range(1,1000) if 64*f**3<=27*10001**2))

# tilt-sum B_2(42), B_2(43), exact sums
def B2(k): return (1-math.exp(-1)) + (math.exp(1.5+1/k)-1)*2*(math.sqrt(k+1)-1)/(math.sqrt(2*math.pi)*(k+1))
print("B2(42)=",B2(42)," B2(43)=",B2(43), " B2(2000)=",B2(2000))
def tiltsum(k):
    x = Fraction(k, k+1)**(k-1)
    return sum(Fraction(n**(n-1), factorial(n))*x**n for n in range(2,k+2))
for k in (2,3,10,20,42,43):
    print(f"  tiltsum({k})={float(tiltsum(k)):.6f}")

# prop-W thirteen
import mpmath as mp
mp.mp.dps=40
def eRen(r1): # e*Ren(r+1) with r+1=r1 => (r1)^{r1-1}/(e^{r1-1}(r1-1)!)
    r=r1-1
    return mp.mpf(r1)**r/(mp.e**r*mp.factorial(r))
k=3131
for d in range(1,15):
    L=(k-1)*(eRen(d+1)-mp.mpf(60)*(d+1)/(k+d))
    R=2*(1+sum(eRen(r+1)+mp.mpf(60)*(r+1)/(k+d) for r in range(1,d)))
    print(f"  d={d}: L={mp.nstr(L,6)} R={mp.nstr(R,4)}")

# zeta(3/2) coarse lower bound with N=2000
mp.mp.dps=30
N=2000
S=sum(mp.mpf(j)**mp.mpf(-1.5) for j in range(1,N))
print("zeta32 S+2N^-1/2 =", S+2*mp.mpf(N)**-0.5, " S+2(N+1)^-1/2 =", S+2*mp.mpf(N+1)**-0.5, " trapezoid lower:", S+2*mp.mpf(N)**-0.5+0.5*mp.mpf(N)**-1.5, " upper:", S+2*(mp.mpf(N)-0.5)**-0.5, " true:", mp.zeta(1.5))
print("zeta(1/2), zeta(-1/2):", mp.zeta(0.5), mp.zeta(-0.5))

# theorem-U arithmetic
c=1/mp.sqrt(2*mp.pi)
print("3c(8.133+10.301c)=", 3*c*(8.133+10.301*c), " 1.5*2.7323*0.8051*c*(17.951+23.462c)=", 1.5*2.7323*0.8051*c*(17.951+23.462*c))
print("50.62/sqrt(3130)=", 50.62/mp.sqrt(3130))
# central gap: 5.642*1.6809*0.39893-0.0163-3.554
print("5.642*1.6809*0.39893-0.0163-3.554 =", 5.642*1.6809*0.39893-0.0163-3.554)
print("S/2^30 =", 2918732888/2**30)
# D rational audit sums
print(sum([176,2304,118,935,533,455,243]), sum([183.51,2303.07,203.57,983.74,920.70,454.86,418.83]))
# counts
print("sum k_n-1 for 10001..20000:", sum(-(-n//2)-1 for n in range(10001,20001)))
print("QR positions 5..20000:", sum(n-2-(-(-(n-1)//2)) for n in range(5,20001)), " 20001..50000:", sum(n-2-(-(-(n-1)//2)) for n in range(20001,50001)))
print("sum_{r=2}^{170}(r-1)=", sum(r-1 for r in range(2,171)), " r<=40:", sum(r-1 for r in range(2,41)))
# M constants
M0=mp.quad(lambda y: mp.exp(-y-y*y/2),[0,mp.inf]); M=[M0,1-M0]
for q in range(1,5): M.append(q*M[q-1]-M[q])
Ms=lambda q: (lambda y: y**q*mp.exp(-y-y*y/2))((-1+mp.sqrt(1+4*q))/2)
print("M0..M5:", [mp.nstr(m,6) for m in M], " C1..C4:", mp.nstr(2*Ms(2)+M[3]/2+M[5]/3,6), mp.nstr(Ms(3)/2+Ms(5)/3+M[4]/2,6), mp.nstr(Ms(4)/2+M[3]/6,6), mp.nstr(Ms(3)/6,6))
M26=mp.quad(lambda y: y*y*mp.exp(-y-y*y/2),[0,6])
L=(M26-(2*Ms(2)+M[3]/2+M[5]/3)/100-(Ms(3)/2+Ms(5)/3+M[4]/2)/10**4-(Ms(4)/2+M[3]/6)/10**6-Ms(3)/6/10**8)/(M[1]+(M[0]+mp.exp(-0.5))/100+mp.mpf(1)/10**4)
print("L(10^4)=", L, " M2-M2^(6)=", M[2]-M26, " bound:", mp.exp(-6)*(6+mp.mpf(1)/6)*mp.exp(-18))
print("0.5+2*0.845204-sqrt(3pi/2)=", 0.5+2*0.845204-mp.sqrt(3*mp.pi/2))
