from fractions import Fraction as Fr
from math import factorial
# (r) 세 재귀 검증: y=3,4, x=1
def A_exact(n, y):  # A_{n,y-1}: 최대 변위 <= y-1 인 길이 n 주차함수 수, 마지막 차 재귀 n A_n = sum_{j=0}^{n-1} min(j+1,y) A_j A_{n-1-j}
    A=[Fr(1)]
    for m in range(1,n+1):
        A.append(sum(min(j+1,y)*A[j]*A[m-1-j] for j in range(m))*Fr(1) / m * 1)
    return A
for y in (2,3,5):
    N=12
    # a°_m = (m+1)^{m-1}/m!  (여기서는 g_n 정의에 쓰는 m^{m-1}/m! 계수)
    g=[Fr(1)]
    for n in range(1,N+1):
        g.append(sum(Fr(j*j**(j-1),factorial(j))*g[n-j] for j in range(1,min(y,n)+1))/n)
    ao=lambda m: Fr((m+1)**(m-1),factorial(m)) if m>0 else Fr(1)
    h=[Fr(0)]
    for n in range(1,N+1):
        s=sum(ao(j-1)*h[n-j] for j in range(1,min(y,n)+1))
        s=y*s + (y*g[n-1] if n>=y+1 else 0)
        h.append(s/n)
    e=[Fr(1)]
    for n in range(1,N+1):
        e.append(g[n]+sum(h[j]*e[n-j] for j in range(1,n+1)))
    # 여기서 A 재귀는 A_n/n! 가 아니라 A_n 자체이므로 비교는 e_n*n! vs A_n
    A=A_exact(N,y)
    # 마지막 차 재귀의 min(j+1,y): A_{n,y-1}이면 용량 y
    ok=all(e[n]*factorial(n)==A[n] for n in range(N+1))
    print("y",y,"세 재귀 == A_{n,y-1}:",ok, [int(e[n]*factorial(n)) for n in range(6)], [int(A[n]) for n in range(6)])
# (p) 표의 올림값으로 S' 값
for (A0,B0,y,k0) in [(Fr(14708,10000),Fr(98505,1000000),Fr(13,100),501),(Fr(25335,10000),Fr(60259,1000000),Fr(2,25),1855),(Fr(27354,10000),Fr(422,10000),Fr(11,200),6098)]:
    xi=Fr(1,k0)
    v=(y-xi)*(y-2*xi-xi*xi)-(1+xi)**2*(A0*xi+B0*y)
    print("올림값 S':", "%.4e"%float(v))
