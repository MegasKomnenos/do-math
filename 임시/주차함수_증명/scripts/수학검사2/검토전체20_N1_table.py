# 장1 1.3절 표 (n<=10) 검산: n<=7은 전수 열거, 모든 행은 합 = (n+1)^(n-1) 확인
import itertools,sys,io
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8')
table={1:[1],2:[2,1],3:[6,7,3],4:[24,51,34,16],5:[120,421,377,253,125],
6:[720,3963,4594,3688,2546,1296],7:[5040,42253,62145,57398,46142,32359,16807],
8:[40320,505515,929856,979430,865970,702292,497442,262144],
9:[362880,6724381,15298809,18289811,17520519,15455851,12587507,8977273,4782969],
10:[3628800,98618763,275075236,371706836,385131546,359973796,318092120,259627152,186093442,100000000]}
for n,row in table.items():
    print(n,'sum ok' if sum(row)==(n+1)**(n-1) else f'SUM MISMATCH {sum(row)} vs {(n+1)**(n-1)}', 'len ok' if len(row)==n else 'LEN BAD')
def maxdisp(a):
    n=len(a); occ=[False]*(n+2); M=0
    for x in a:
        p=x
        while p<=n and occ[p]: p+=1
        if p>n: return None
        occ[p]=True; M=max(M,p-x)
    return M
for n in range(1,8):
    b=[0]*n
    for a in itertools.product(range(1,n+1),repeat=n):
        M=maxdisp(a)
        if M is not None: b[M]+=1
    print(n,b,'MATCH' if b==table[n] else 'DIFF')
# n=3 분류 검사
for a in [(1,1,2),(1,1,3),(1,3,1),(3,1,1),(1,2,2),(2,1,2),(2,2,1),(1,1,1),(1,2,1),(2,1,1),(1,2,3),(1,3,2),(2,1,3),(2,3,1),(3,1,2),(3,2,1)]:
    print(a,maxdisp(a),end='; ')
