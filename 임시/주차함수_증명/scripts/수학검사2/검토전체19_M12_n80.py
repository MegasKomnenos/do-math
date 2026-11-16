# n=80 로그오목성 실패의 세 정수와 비, 분리자 교차곱을 마지막 차 재귀로 다시 센다.
from math import comb
from fractions import Fraction
N=80
def col(l):
    A=[0]*(N+1); A[0]=1
    for n in range(1,N+1):
        A[n]=sum(comb(n-1,j)*min(j+1,l+1)*A[j]*A[n-1-j] for j in range(n))
    return A
C={l:col(l) for l in range(37,43)}
b={l:C[l][N]-C[l-1][N] for l in range(38,43)}
print("digits", [len(str(b[l])) for l in (39,40,41)])
print("b39", b[39]); print("b40", b[40]); print("b41", b[41])
print("b39*b41-b40^2 >0:", b[39]*b[41]-b[40]**2>0)
print("ratios", float(Fraction(b[40],b[39])), float(Fraction(b[41],b[40])))
print("separator 25928/25000:", b[40]*25000 < 25928*b[39], 25928*b[40] < 25000*b[41])
print("increasing:", b[39]<b[40]<b[41])
