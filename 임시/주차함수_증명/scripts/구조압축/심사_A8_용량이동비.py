# 심사 A8 — C9·S7 검산(정확 산술): 가중 재귀(G1) Z_n=sum_j C(n-1,j) w_{j+1} Z_j Z_{n-1-j}, w_t=min(t,l+1)로 A_{N,l}을 정확히 세고
#  (1) 8.24(가) s_N(k-1)/s_N(k) >= (1-1/k)^{max(N-k+1,0)} 를 N<=2k-1 밖(모든 N)까지 검사한다(C9),
#  (2) 8.7 Jensen 하계 s_N(y) >= exp(-E_N[A]/y), E_N[A]=sum_{m>y}(m-y)theta_{N+1}(m) 를 N>2y+1에서도 검사한다(S7),
#  (3) 합집합 상계 1-s_N(y) <= sum_{m>y} theta_{N+1}(m)(m-y)/m 를 모든 N에서 검사한다(S7, F4 §5).
# 실행: python -I 심사_A8_용량이동비.py
from fractions import Fraction as Fr
from math import comb, exp, log
import sys
def A_table(l, Nmax):
    w=lambda t: min(t,l+1)
    Z=[0]*(Nmax+1); Z[0]=1
    for n in range(1,Nmax+1):
        Z[n]=sum(comb(n-1,j)*w(j+1)*Z[j]*Z[n-1-j] for j in range(n))
    return Z
def p(n): return (n+1)**(n-1) if n>=1 else 1
out=[]; P=lambda *a: out.append(' '.join(str(x) for x in a))
# sanity: l+1>=n gives p_n
Z=A_table(40,12); assert all(Z[n]==p(n) for n in range(13)), "G1 recursion sanity failed"
P("sanity: w_t=min(t,41) gives Z_n=(n+1)^{n-1} for n<=12: OK")
# (1) C9
viol=0; tested=0; worst=Fr(10)
for k in range(2,9):
    Nmax=4*k+4
    Ak2=A_table(k-2,Nmax); Ak1=A_table(k-1,Nmax)
    for N in range(0,Nmax+1):
        lhs=Fr(Ak2[N],Ak1[N]); e=max(N-k+1,0); rhs=Fr(k-1,k)**e
        tested+=1
        if lhs<rhs: viol+=1; P(f"VIOLATION k={k} N={N} lhs={float(lhs):.6f} rhs={float(rhs):.6f}")
        worst=min(worst, lhs/rhs)
    # also general r<=s: A_{N,r-1}/A_{N,s-1} >= prod_{i<=N} min(i,r)/min(i,s), r=k-2, s=k (two steps)
    if k>=4:
        Ak3=A_table(k-3,Nmax)
        for N in range(0,Nmax+1):
            lhs=Fr(Ak3[N],Ak1[N]); rhs=Fr(1)
            for i in range(1,N+1): rhs*=Fr(min(i,k-2),min(i,k))
            tested+=1
            if lhs<rhs: viol+=1; P(f"VIOLATION(r=k-2,s=k) k={k} N={N}")
P(f"C9: tested {tested} (k,N) pairs, k=2..8, N<=4k+4 (N>2k-1 포함); violations={viol}; min lhs/rhs={float(worst):.6f}")
# (2)(3) S7: Jensen beyond first layer and union bound, exact theta
def theta(N,m):  # E_N[#{v: t_v=m}] = C(N,m) m^{m-1} (N+1-m)^{N-m} / p_N   (2:chain-expansion (가))
    return Fr(comb(N,m)*m**(m-1)*(N+1-m)**(N-m), p(N))
jv=0; uv=0; tested=0; minmargin=9.0
for y in range(1,8):
    Nmax=4*y+6
    Ay=A_table(y-1,Nmax)
    for N in range(y+1,Nmax+1):
        s=Fr(Ay[N],p(N))
        EA=sum((m-y)*theta(N,m) for m in range(y+1,N+1))
        jen=exp(-float(EA)/y)
        tested+=1
        if float(s)<jen-1e-15: jv+=1; P(f"JENSEN VIOLATION y={y} N={N} s={float(s):.6f} bound={jen:.6f}")
        minmargin=min(minmargin,float(s)/jen)
        ub=sum(theta(N,m)*Fr(m-y,m) for m in range(y+1,N+1))
        if 1-s>ub: uv+=1; P(f"UNION VIOLATION y={y} N={N}")
        # chain-range identity (8.10) check when N<=2y+1
        if N<=2*y+1:
            rhs=sum(theta(N,m)*Fr(m-y,m)*Fr(Ay[m-1],p(m-1)) for m in range(y+1,N+1))
            assert 1-s==rhs, f"(8.10) identity fails y={y} N={N}"
P(f"S7: Jensen s_N(y)>=exp(-E_N[A]/y) tested at {tested} (y,N), y=1..7, N up to 4y+6 (N>2y+1 포함): violations={jv}, min s/bound={minmargin:.4f}")
P(f"S7: union bound 1-s<=sum theta (m-y)/m: violations={uv}; (8.10) identity exact in chain range: OK")
open(sys.argv[0].replace('.py','_out.txt'),'w',encoding='utf-8').write('\n'.join(out)); print('\n'.join(out))
