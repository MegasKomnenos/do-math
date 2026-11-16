# 검토전체6 L2: 3장·4장 유한 수치의 재계산 (마지막 차 재귀로 행을 만들어 진술과 대조)
from fractions import Fraction as Fr
from math import comb, isqrt
import mpmath as mp
N=120
p=[(n+1)**(n-1) if n>=1 else 1 for n in range(N+2)]
# A[n][l]
A=[[0]*(N+1) for _ in range(N+1)]
for l in range(N+1):
    A[0][l]=1
    for n in range(1,N+1):
        if l>=n-1: A[n][l]=p[n]; continue
        s=0
        for j in range(n):
            s+=comb(n-1,j)*min(j+1,l+1)*A[j][l]*A[n-1-j][l]
        A[n][l]=s
def b(n,l): return A[n][l]-(A[n][l-1] if l>=1 else 0)
rows={n:[b(n,l) for l in range(n)] for n in range(1,N+1)}
for n in range(1,N+1): assert sum(rows[n])==p[n]
# 1.3절 표 대조
table={1:[1],2:[2,1],3:[6,7,3],4:[24,51,34,16],5:[120,421,377,253,125],6:[720,3963,4594,3688,2546,1296],
7:[5040,42253,62145,57398,46142,32359,16807],8:[40320,505515,929856,979430,865970,702292,497442,262144],
9:[362880,6724381,15298809,18289811,17520519,15455851,12587507,8977273,4782969],
10:[3628800,98618763,275075236,371706836,385131546,359973796,318092120,259627152,186093442,100000000]}
print("1.3절 표 일치:", all(rows[n]==table[n] for n in table))
# 증인 (최댓값 첨자들)
def witnesses(r):
    m=max(r); return [i for i,v in enumerate(r) if v==m]
def unimodal(r):
    w=witnesses(r)[0]
    return all(r[i]<=r[i+1] for i in range(w)) and all(r[i]>=r[i+1] for i in range(w,len(r)-1))
print("n<=10 가장 작은 증인:", {n:witnesses(rows[n])[0] for n in range(1,11)})
print("n<=120 모두 단봉:", all(unimodal(rows[n]) for n in range(1,N+1)), " 고원(증인 둘 이상) 있는 n:", [n for n in range(1,N+1) if len(witnesses(rows[n]))>1])
print("n<=10 증인 < ceil(n/2):", all(witnesses(rows[n])[0] < -(-n//2) for n in range(1,11)))
print("증인 >= ceil(n/2) 이 처음 성립하는 n (<=120):", [n for n in range(1,N+1) if witnesses(rows[n])[0] >= -(-n//2)][:5])
# 로그오목성 첫 실패
fails=[(n,l) for n in range(1,N+1) for l in range(1,n-1) if rows[n][l]**2 < rows[n][l-1]*rows[n][l+1]]
print("로그오목성 실패 (n<=85):", [f for f in fails if f[0]<=85])
r=rows[80]; print("b80: 39<40<41:", r[39]<r[40]<r[41], " 40^2<39*41:", r[40]**2<r[39]*r[41])
print("비:", float(Fr(r[40],r[39])), float(Fr(r[41],r[40])), " 분리자 25928/25000:", Fr(r[40],r[39])<Fr(25928,25000)<Fr(r[41],r[40]))
print("b80,39 =", r[39]); print("b80,40 =", r[40]); print("b80,41 =", r[41])
# 누적 로그오목 n<=120 성립?
cf=[(n,l) for n in range(1,N+1) for l in range(1,n-1) if A[n][l]**2 < A[n][l-1]*A[n][l+1]]
print("누적 로그오목 실패 (n<=120):", cf[:3])
# 4장: 중앙 틈 부호와 오른쪽 절반
kn=lambda n: -(-n//2)
neg=[n for n in range(2,N+1) if rows[n][kn(n)]-rows[n][kn(n)-1] < 0]
print("d_{n,k_n}<0 인 n (<=120):", neg)
print("2<=n<=15 오른쪽 절반 비증가:", all(all(rows[n][j]>=rows[n][j+1] for j in range(kn(n),n-1)) for n in range(2,16)))
cross=[n for n in range(5,N+1) if rows[n][kn(n)]<rows[n][kn(n)+1]]
print("b_{n,k_n}<b_{n,k_n+1} 거짓인 n (5..120):", [n for n in range(5,N+1) if n not in cross])
# Q_L(n), 3<=n<=15
def QL(n):
    r=rows[n]
    return all((not r[l]>r[l+1]) or r[l+1]**2>=r[l]*r[l+2] for l in range(0,n-2) if 2*l<=n-2)
print("Q_L(n) 3..15:", all(QL(n) for n in range(3,16)))
# 3.4절: E_n omega_n, n<=5
def Eomega(n):
    return sum(Fr(comb(n,j)*j**j*p[n-j],p[n]) for j in range(1,n//2+1))
print("E_n omega_n n=1..5:", [Eomega(n) for n in range(1,6)])
print("n>=6 에서 sqrt(2/pi)sqrt((n+1)(n+2)/n)<=sqrt(n) 즉 2(n+1)(n+2)<=pi n^2:", all(2*(n+1)*(n+2)<=mp.pi*n*n for n in range(6,200)), " n=5:", 2*6*7<=mp.pi*25)
# 3-6의 유리수
lam=Fr(751,1000); J=8
val=lam**J+Fr(1,31)*sum(i*lam**(i-1) for i in range(1,J+1))+Fr(1,1000)*sum((i-1)*lam**(i-1) for i in range(1,J+1))
print("3-6 유리수 일치:", val==Fr(7309649993107890414228499,15500000000000000000000000), " 값:", mp.mpf(val.numerator)/val.denominator)
print("lambda<=751/1000 for n>=1000:", all(Fr(-(-3*n//4),n)<=lam for n in range(1000,5000)))
# 4장 따름정리 수치
v=Fr(699,100)-Fr(7,2)-Fr(6*699,100)/31-Fr(3,4)/31-Fr(13*699,200)/961-Fr(12*699,100)/30000
print("(나) 유리수:", v==Fr(495594511,240250000), float(v))
a0=mp.quad(lambda w: mp.e**(-w**3/3),[0,mp.inf]); a1=mp.quad(lambda w: w*mp.e**(-w**3/3),[0,mp.inf])
print("a0,a1:", a0,a1)
w=mp.mpf('6.98'); k13=mp.mpf('0.0464159')
print("(다):", w-mp.mpf(3.5)-(4*w+0.5)*mp.mpf('1.2879')*k13-(13*w/2)*mp.mpf('0.939')*k13**2-12*w/10000)
print("10000^(-1/3)=",mp.mpf(10000)**(-mp.mpf(1)/3))
# 3.1절 Legendre, 꼬리 상수
print("Legendre:", mp.gamma(mp.mpf(1)/3)*mp.gamma(mp.mpf(5)/6), 2**(mp.mpf(1)/3)*mp.sqrt(mp.pi)*mp.gamma(mp.mpf(2)/3))
def mellin(s):
    s=mp.mpf(s)
    return (mp.mpf(3)/2)**(s/3)*mp.gamma(1+2*s/3)*mp.gamma(mp.mpf(5)/6-s/3)/mp.gamma(mp.mpf(5)/6)*mp.gamma(mp.mpf(1)/2-s/3)*mp.gamma(mp.mpf(2)/3)/(mp.gamma(mp.mpf(1)/2)*mp.gamma(mp.mpf(2)/3-s/3))
print("E X^0 =", mellin(0), " 잔차 상수 (3/2-s)E X^s at s->3/2:", (mp.mpf(3)/2-mp.mpf('1.4999999'))*mellin('1.4999999'), " 3/sqrt(2pi)=", 3/mp.sqrt(2*mp.pi))
print("(3/4)^1.5 =", mp.mpf(0.75)**1.5, 3**1.5/8)
# 3-3 모수
for rho in [-0.4999, 0, 1, 2.4999]:
    print(rho, (1+2*rho)/3, (7-2*rho)/6, (5-2*rho)/6)
