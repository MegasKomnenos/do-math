# 검토전체8 N2: 3장·4장의 유한 행 관련 진술을 정리 2-6(마지막 차 재귀)으로 다시 센다.
# python -I 로 실행. 외부 의존 없음.
from fractions import Fraction
from math import comb, isqrt

NMAX = 80
# A[n][l] = 최대 변위 <= l 인 길이 n 주차함수 수. 정리 2-6: A_{n,l} = sum_j C(n-1,j) min(j+1,l+1) A_{j,l} A_{n-1-j,l}
A = [[0]*(NMAX+1) for _ in range(NMAX+1)]
for l in range(NMAX+1):
    A[0][l] = 1
    for n in range(1, NMAX+1):
        s = 0
        for j in range(n):
            s += comb(n-1, j)*min(j+1, l+1)*A[j][l]*A[n-1-j][l]
        A[n][l] = s
def row(n):
    return [A[n][0]] + [A[n][l]-A[n][l-1] for l in range(1, n)]
p = lambda n: (n+1)**(n-1)

# 1.3절 표 대조 (n<=10)
table = {1:[1],2:[2,1],3:[6,7,3],4:[24,51,34,16],5:[120,421,377,253,125],
 6:[720,3963,4594,3688,2546,1296],7:[5040,42253,62145,57398,46142,32359,16807],
 8:[40320,505515,929856,979430,865970,702292,497442,262144],
 9:[362880,6724381,15298809,18289811,17520519,15455851,12587507,8977273,4782969],
 10:[3628800,98618763,275075236,371706836,385131546,359973796,318092120,259627152,186093442,100000000]}
print("1.3절 표 일치:", all(row(n)==table[n] for n in table), " 합=p_n:", all(sum(row(n))==p(n) for n in range(1,NMAX+1)))
# 증인 < ceil(n/2) (n<=10)
for n in range(1,11):
    b=row(n); w=[i for i,v in enumerate(b) if v==max(b)]
    assert all(x < -(-n//2) for x in w)
print("n<=10 증인 모두 ceil(n/2) 미만: 확인")

# 정리 3-4: 로그오목성 n<=79, n=80 첫 실패
def logconcave(b):
    return all(b[i]*b[i] >= b[i-1]*b[i+1] for i in range(1,len(b)-1))
first = next(n for n in range(1,NMAX+1) if not logconcave(row(n)))
b80=row(80)
bad=[i for i in range(1,79) if b80[i]**2 < b80[i-1]*b80[i+1]]
print("로그오목성 첫 실패 n =", first, " n=80 실패 수준:", bad, " 증가구간:", b80[39]<b80[40]<b80[41])

# 정리 4-5: 2<=n<=15 d_{n,k_n}<0 이고 오른쪽 절반 비증가; 16<=n<=80 d>0
ok=True
for n in range(2,NMAX+1):
    b=row(n); k=-(-n//2); d=b[k]-b[k-1]
    if n<=15:
        ok &= d<0 and all(b[j]>=b[j+1] for j in range(k,n-1))
    else:
        ok &= d>0
print("정리 4-5 유한 부분(n<=80):", ok)
# 정리 4-8: 20<=n<=80 에서 b_{n,k_n}<b_{n,k_n+1}
print("20<=n<=80 b_{k_n}<b_{k_n+1}:", all((lambda b,k: b[k]<b[k+1])(row(n), -(-n//2)) for n in range(20,NMAX+1)))
# 정리 4-9: 3<=n<=15 Q_L(n)
def QL(n):
    b=row(n)
    for l in range(0,n-2):
        if 2*l<=n-2 and b[l]>b[l+1] and not b[l+1]**2>=b[l]*b[l+2]: return False
    return True
print("3<=n<=15 Q_L(n):", all(QL(n) for n in range(3,16)))
# 정리 3-6 증인 결론이 n<=10 에서 거짓 (증인 < ceil(n/2)): 위에서 확인. 모든 n<=80 에서 단봉인지
print("n<=80 모든 행 단봉:", all((lambda b: all(b[i]<=b[i+1] for i in range(b.index(max(b)))) and all(b[i]>=b[i+1] for i in range(b.index(max(b)),len(b)-1)))(row(n)) for n in range(1,NMAX+1)))

# 정리 3-6 증명: E_n omega_n = sum_{j<=n/2} C(n,j) j^j p_{n-j}/p_n, n=1..5
for n in range(1,6):
    w = sum(Fraction(comb(n,j)*j**j*p(n-j), p(n)) for j in range(1, n//2+1))
    print(f"E_{n} omega = {w}  (<= sqrt n: {w*w <= n})")
# 정리 3-6 수치: lambda=751/1000, J=8
lam=Fraction(751,1000); J=8
val = lam**J + Fraction(1,31)*sum(i*lam**(i-1) for i in range(1,J+1)) + Fraction(1,1000)*sum((i-1)*lam**(i-1) for i in range(1,J+1))
print("s_n 상계 유리수:", val, " = 본문 값:", val==Fraction(7309649993107890414228499,15500000000000000000000000), " <0.4716:", val<Fraction(4716,10000), float(val))
# 9n^2-48n-32 at n=6
print("9n^2-48n-32 (n=6):", 9*36-48*6-32)
