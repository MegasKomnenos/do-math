# 정리 2-6 마지막 차 재귀로 A_{n,l}을 구해 1.3절 표(n<=10)와 비교
import sys,io
from math import comb
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8')
table={1:[1],2:[2,1],3:[6,7,3],4:[24,51,34,16],5:[120,421,377,253,125],
6:[720,3963,4594,3688,2546,1296],7:[5040,42253,62145,57398,46142,32359,16807],
8:[40320,505515,929856,979430,865970,702292,497442,262144],
9:[362880,6724381,15298809,18289811,17520519,15455851,12587507,8977273,4782969],
10:[3628800,98618763,275075236,371706836,385131546,359973796,318092120,259627152,186093442,100000000]}
N=12
A={}
for l in range(0,N):
    A[(0,l)]=1
    for n in range(1,N+1):
        A[(n,l)]=sum(comb(n-1,j)*min(j+1,l+1)*A[(j,l)]*A[(n-1-j,l)] for j in range(n))
for n in range(1,11):
    row=[A[(n,0)]]+[A[(n,l)]-A[(n,l-1)] for l in range(1,n)]
    print(n,'MATCH' if row==table[n] else f'DIFF {row}')
# A_{n,0}=n!, A_1 = 1/(2-e^x) 계수 확인 (n<=8)
from math import factorial
from fractions import Fraction
print([A[(n,0)]==factorial(n) for n in range(1,9)])
# 1/(2-e^x) 계수: a_n = sum_{k>=1} ... 수치로 확인: c_n = n! [x^n] 1/(2-e^x) = Fubini numbers 1,1,3,13,75,541,4683
fub=[1,1,3,13,75,541,4683,47293]
print([A[(n,1)] for n in range(0,8)]==fub)
# 명제 2-7 극한 Borel 분포 합=1 확인(수치)
import math
s=sum(math.exp(-(r+1))*(r+1)**(r-1)/math.factorial(r) for r in range(0,200)); print('borel sum',s)
