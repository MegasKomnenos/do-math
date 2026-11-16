# 검토전체16 E3: n<=NMAX 행 전체를 정확한 정수로 계산해 5.1절의 주장과
# 5.2.1절의 양의 원천 표현(정리 source-rep)과 Green 연결(보조정리 green-connection (다))을 수치로 대조한다.
import sys, math
from fractions import Fraction
NMAX = int(sys.argv[1]) if len(sys.argv) > 1 else 300
NSMALL = 26  # 원천 표현 대조 범위

# A[l][n] = A_{n,l}: 최대 변위 <= l 인 길이 n 주차함수의 수. 정리 2.6 재귀.
p = [ (n+1)**(n-1) if n>=1 else 1 for n in range(NMAX+2) ]
binom = [[0]*(NMAX+2) for _ in range(NMAX+2)]
for n in range(NMAX+2):
    binom[n][0]=1
    for j in range(1,n+1):
        binom[n][j]=binom[n-1][j-1]+binom[n-1][j]
A = {}  # A[(n,l)]
def getA(n,l):
    if l < 0: return 0
    if l >= n-1: return p[n]
    return A[(n,l)]
for l in range(0, NMAX):
    row = [0]*(NMAX+1)
    for m in range(0, NMAX+1):
        if l >= m-1:
            row[m] = p[m]; continue
        s = 0
        for j in range(1, m+1):
            s += binom[m-1][j-1]*min(j,l+1)*row[j-1]*row[m-j]
        row[m] = s
    for m in range(NMAX+1):
        if l < m-1:
            A[(m,l)] = row[m]
def b(n,l):
    return getA(n,l)-getA(n,l-1)

out = []
# (1) 단봉성과 가장 작은 증인
peaks = {}
for n in range(1, NMAX+1):
    row = [b(n,l) for l in range(n)]
    # first decrease
    j = next((i for i in range(n-1) if row[i] > row[i+1]), n-1)
    uni = all(row[i] >= row[i+1] for i in range(j, n-1))
    if not uni: out.append(f"NOT UNIMODAL n={n}")
    # smallest witness
    mx = max(row); peaks[n] = row.index(mx)
# (2) 첫째 조각 사슬 b_{n,0}<...<b_{n,k_n-1} 깨지는 n
broken = []
for n in range(2, NMAX+1):
    kn = -(-n//2)
    if not all(b(n,l) < b(n,l+1) for l in range(0, kn-1)):
        broken.append(n)
out.append(f"chain b_(n,0)<...<b_(n,k_n-1) broken at n in {broken}")
# (3) 셋째 조각: d_{n,k_n} sign
neg = [n for n in range(2, NMAX+1) if b(n,-(-n//2)) <= b(n,-(-n//2)-1)]
out.append(f"middle pair not strictly increasing at n in {neg}")
# (4) 넷째 조각
bad4 = []
for n in range(5, NMAX+1):
    kinds = []
    for l in range(math.ceil((n-1)/2), n-2):
        if b(n,l) <= b(n,l+1): kinds.append(0)
        else:
            ok = b(n,l) > b(n,l+1) and b(n,l+1)**2 > b(n,l)*b(n,l+2) and b(n,l)+b(n,l+2) < 2*b(n,l+1)
            kinds.append(1 if ok else 9)
    if 9 in kinds or kinds != sorted(kinds): bad4.append((n,kinds))
out.append(f"4th piece violations: {bad4[:5]} (count {len(bad4)})")
# (5) 정리 5.2 (다): 오른쪽 절반 인접 쌍 모두 엄격
ties = [(n,l) for n in range(5, NMAX+1) for l in range(math.ceil((n-1)/2), n-1) if b(n,l)==b(n,l+1)]
out.append(f"right-half ties: {ties[:10]} (count {len(ties)})")
# (6) 명제 witness-position-bound, 50<=n<=NMAX
vals = []
for n in range(50, NMAX+1):
    v = n+1-peaks[n]-0.59963*(n+1)**(2/3)-1.24847*(n+1)**(1/3)
    vals.append((v,n))
if vals:
    out.append(f"witness bound diff: min {min(vals)}, max {max(vals)}")
out.append(f"peaks n=1..20: {[peaks[n] for n in range(1,21)]}")
# n<=15 : d_{n,k_n} <0 ?  (정리 4.5 진술)
out.append("d_(n,k_n) for n=2..16: "+str([b(n,-(-n//2))-b(n,-(-n//2)-1) for n in range(2,17)]))

# (7) 원천 표현 대조: Gamma_d(y;n) 재귀, phi^{[k]}_m, K_{n,k}(y) = phi_n + y*sum phi_m Gamma_{n-m-1}(y;n)
def Gamma_list(n, dmax, y):
    g = [Fraction(1)]
    for d in range(1, dmax+1):
        s = binom[n][d]*p[d]
        t = Fraction(0)
        for j in range(0, d):
            t += binom[n-d+j][j]*p[j]*g[d-1-j]
        g.append(s + y*t)
    return g
def phi_list(k, mmax):
    ph = [1]
    for m in range(1, mmax+1):
        s = 0
        for t in range(1, min(k,m)+1):
            s += binom[m-1][t-1]*(t**(t-1))*ph[m-t]
        ph.append(s)
    return ph
def K(n,k,y):
    ph = phi_list(k, n)
    g = Gamma_list(n, n-1, y)
    return ph[n] + y*sum(ph[m]*g[n-m-1] for m in range(k, n))
errs = []
for k in range(1, 13):
    for n in range(k+1, min(2*k+1, NSMALL)+1):
        # (가): K(k)=A_{n,k-1}, K(k+1)=A_{n,k}
        if K(n,k,k) != getA(n,k-1) or K(n,k,k+1) != getA(n,k): errs.append(("Ka",n,k))
        # (다) 둘째 귀결: Gamma^+ = K(k+2) - A_{n,k+1} = p_k Gamma_{n-k-1}(k+2;n)
        gp = p[k]*Gamma_list(n, n-k-1, k+2)[n-k-1]
        if K(n,k,k+2) - getA(n,k+1) != gp: errs.append(("G+",n,k))
        # (다) 첫째 귀결 (k<=n<=2k-1): Gamma^- = K(k-1)-A_{n,k-2} = p_{k-1} Gamma_{n-k}(k-1;n)
        if n <= 2*k-1:
            gm = p[k-1]*Gamma_list(n, n-k, k-1)[n-k]
            if K(n,k,k-1) - getA(n,k-2) != gm: errs.append(("G-",n,k))
            # 2.28: d_{n,k} = 2E - B  with 2E = K(k+1)-2K(k)+K(k-1), B = Gamma^-
            d = b(n,k)-b(n,k-1)
            twoE = K(n,k,k+1)-2*K(n,k,k)+K(n,k,k-1)
            if d != twoE - gm: errs.append(("2.28",n,k))
            # S_{n,k} 원천별 전개 (다)
            if n >= k+2:
                dk1 = b(n,k+1)-b(n,k)
                S = gp*d - gm*dk1
                r = n-k
                ph = phi_list(k, n)
                def hg(dd,y): return y*Gamma_list(n, dd, y)[dd]
                def sd(dd,y): return hg(dd,y+1)-2*hg(dd,y)+hg(dd,y-1)
                S2 = sum(ph[n-dd-1]*(gp*sd(dd,k)-gm*sd(dd,k+1)) for dd in range(1, r))
                if S != S2: errs.append(("S",n,k,S,S2))
out.append(f"source-rep / green-connection mismatches: {errs[:5]} (count {len(errs)})")
print("\n".join(out))
