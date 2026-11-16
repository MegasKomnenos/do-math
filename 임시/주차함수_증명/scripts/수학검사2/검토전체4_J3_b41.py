# b_{n,1}: parking functions of length n with max displacement exactly 1, vs (n-1) n!/2
from itertools import product
from math import factorial
def maxdisp(a):
    n=len(a); occ=[False]*(n+2)
    md=0
    for p in a:
        q=p
        while q<=n and occ[q]: q+=1
        if q>n: return None
        occ[q]=True; md=max(md,q-p)
    return md
for n in range(2,7):
    cnt=sum(1 for a in product(range(1,n+1),repeat=n) if maxdisp(a)==1)
    print(n, "b_{n,1}=",cnt, " (n-1)n!/2=",(n-1)*factorial(n)//2)
