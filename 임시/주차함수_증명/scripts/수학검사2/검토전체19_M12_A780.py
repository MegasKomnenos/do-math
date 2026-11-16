# A_{780,575}의 자릿수와 n=780, l=575 상대 크기를 열 574,575,576으로 다시 센다.
from math import comb
N=780
CB=[[comb(m,j) for j in range(m+1)] for m in range(N)]
def col(l):
    A=[0]*(N+1); A[0]=1
    for n in range(1,N+1):
        c=CB[n-1]; s=0
        for j in range(n):
            s+=c[j]*min(j+1,l+1)*A[j]*A[n-1-j]
        A[n]=s
    return A
A={l:col(l) for l in (574,575,576)}
print("digits A_780,575:", len(str(A[575][N])), " digits A_780,574:", len(str(A[574][N])), " A_780,576:", len(str(A[576][N])))
D=A[575][N]**2-A[574][N]*A[576][N]
print("sign:", D<0, " relative:", D/ A[575][N]**2)
