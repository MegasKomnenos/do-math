# G6 검토: 장7A의 손 계산 몇 곳을 다시 센다. python -I 로 돌린다.
from fractions import Fraction as F
from math import log, exp, sqrt, factorial, cosh
from itertools import permutations

# 1. 보조정리 column-lemma (가)의 정수 부등식
print("10^21*400^10 > 17^21*123^10 :", 10**21*400**10 > 17**21*123**10,
      f"{10**21*400**10:.3e} vs {17**21*123**10:.3e}")
print("(40/41)(10/17)^2.1 =", (40/41)*(10/17)**2.1, "> 0.3")

# 2. t_k, n#_k, ñ_k 와 1<=t_k<=k, n#_k<ñ_k
def t_k(k):
    j=0
    while not ((k+1)**j*k**(j+1)+(k-1)**(2*j+1) >= 2*k**(2*j+1)): j+=1
    return j
for k in (2,3,10,41,120,501):
    t=t_k(k); ns=k+(k+1)*t; nt=k*(2*t+1)
    assert 1<=t<=k and ns<nt
    print(f"k={k}: t_k={t}, n#={ns}, ñ={nt}, n#/k^2={ns/k**2:.3f}")

# 3. 자유 비, j*(ς), k_R(ς) (정리 self-consistent-S 표)
def a0(m): return F((m+1)**(m-1), factorial(m))
def jstar(s):
    m=0
    while (1+1/(m+2))**(m+1) < s: m+=1
    return m
for s,J,k0,jexp,kRexp in ((F(267,100),25,501,82,429),(F(27,10),70,1855,220,1855),(F(271,100),100,6098,490,6098)):
    js=jstar(float(s)); 
    import math
    kR=max(2*js+2, math.ceil(s**(js+2)/a0(js+1)))
    print(f"ς={float(s)}: j*={js} (표 {jexp}), k_R={kR} (표 {kRexp}), J<=j*: {J<=js}, k0>=k_R: {k0>=kR}")

# 4. 따름정리 cor-S-prime 의 세 값 g_S(y k^2)/k^4 (정확 유리수)
for y,k0,A0,B0 in ((F(13,100),501,F(14708,10000),F(98505,10**6)),(F(2,25),1855,F(25335,10000),F(60259,10**6)),(F(11,200),6098,F(27354,10000),F(422,10**4))):
    xi=F(1,k0)
    val=(y-xi)*(y-2*xi-xi**2)-(1+xi)**2*(A0*xi+B0*y)
    nv=((3*xi+xi**2)/2+(1+xi)**2*B0/2)
    print(f"k0={k0}: g_S/k^4={float(val):.4e} (>0: {val>0}), n_v/k^2={float(nv):.4f} <= y={float(y)}: {nv<=y}")

# 5. 명제 riccati 뒤의 반례 (k,z,n)=(3,1,2): 좌변 4, 우변 5
k,z,n=3,1,2
def caps(sig):
    h=[]
    for i,v in enumerate(sig):
        j=i-1
        while j>=0 and sig[j]<v: j-=1
        h.append(i-j)
    return h
lhs=sum(sum(1 for c in caps(s) if c==z)* (lambda h: __import__('math').prod(min(c,k) for c in h))(caps(s)) for s in permutations(range(1,n+1)))
print("riccati 반례 좌변 n!·[x^2]Y_1 =", lhs)
# 우변: A_2(x)·x + 3·Ex·j_1/Δ^2 의 x^2 계수 ×2!  (급수 전개)
import sympy as sp
x=sp.symbols('x')
Q2=2*x+x**2/2
Ex=sp.exp(-Q2); Delta=1-3*sp.integrate(Ex,(x,0,x))
A2=Ex/Delta
j1=sp.integrate(x*Ex,(x,0,x))
rhs=sp.series(A2*x+3*Ex*j1/Delta**2,x,0,3).removeO()
print("riccati 반례 우변 2!·[x^2] =", 2*rhs.coeff(x,2), "; A_{n,2} 계수 확인:", sp.series(A2,x,0,4).removeO())

# 6. 보조정리 polar-N 의 상수
e=2/sqrt(2001); print("e<=0.0448:", e, (2*(cosh(e)-1)-e*e)/e**2 <= 0.0002)
print("x_2001 <0.3683:", (2001/2002)**2000, " 2k^{3/2}+1 at 2001:", 2*2001**1.5+1, " 0.3476k^2:", 0.3476*2001**2)
# 7. polar-W † : (2*sqrt(k)+1.81)^3 <= 8.01 k^{3/2} at k=1e7, 합산
k=10**7; print("(2√k+1.81)^3/k^1.5 =", (2*sqrt(k)+1.81)**3/k**1.5, " 8.344/√k+... =", 8.344/sqrt(k)+2/k)
# 8. ρ_2 = log 2, 소인 수 (n-1)^(n-1) 과 A_1 의 첫 항들
print("C_{n,n} n=1..5:", [(n-1)**(n-1) for n in range(1,6)], " A_{n,1} (Fubini) n=0..4:", [1,1,3,13,75])
