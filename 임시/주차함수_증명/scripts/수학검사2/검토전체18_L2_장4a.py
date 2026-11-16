# 검토전체18 L2: 4장 검산 (a) 잔차 R의 x^2,x^3 계수 소거 (b) 정리 4.5의 n<=16 중앙 틈 부호
import sys
from math import comb
out=[]
try:
    import sympy as sp
    io,xx=sp.symbols('iota x',positive=True)
    g=sp.sqrt(1-4*io); u=(1+g)/2
    C1=(1-u)/g**2; C2=-(1-u)*(2+u)/g**5; C3=sp.Rational(5,1)*(1-u)*(6+g-g**2)/(2*g**8)
    uh=lambda t: (u+xx*C1+xx**2*C2+xx**3*C3).subs(io,t)
    R=(uh(io)-1)*uh(io-xx)+io
    ser=sp.series(R,xx,0,4).removeO()
    for p in range(4):
        c=sp.simplify(sp.expand(ser.coeff(xx,p)))
        out.append(f"x^{p} coeff simplified: {c}")
except Exception as e:
    out.append(f"sympy failed: {e}")
def column(l,nmax):
    A=[0]*(nmax+1);A[0]=1
    for n in range(1,nmax+1):
        A[n]=sum(comb(n-1,j)*min(j+1,l+1)*A[j]*A[n-1-j] for j in range(n))
    return A
N=17
cols={l:column(l,N) for l in range(0,N)}
def b(n,l):
    if l<0: return 0
    if l>=n: return 0
    return cols[l][n]-(cols[l-1][n] if l>=1 else 0)
for n in range(2,18):
    k=-(-n//2)
    d=b(n,k)-b(n,k-1)
    right_nonincr=all(b(n,j)>=b(n,j+1) for j in range(k,n-1))
    out.append(f"n={n} k_n={k} d={d} sign={'+' if d>0 else '-'} right_half_nonincreasing={right_nonincr}")
open(sys.argv[1],'w',encoding='utf-8').write("\n".join(out))
