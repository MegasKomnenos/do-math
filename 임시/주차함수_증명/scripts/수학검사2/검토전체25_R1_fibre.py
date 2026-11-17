# R1 검산: 비단봉 섬유가 처음 나타나는 n
import itertools, math
def caps(s):
    n=len(s); h=[]
    for i in range(n):
        z=0
        for j in range(i-1,-1,-1):
            if s[j]>s[i]: z=j+1; break
        h.append(i+1-z)
    return h
def unimodal(row):
    m=len(row)-1
    return any(all(row[i]<=row[i+1] for i in range(ls)) and all(row[i]>=row[i+1] for i in range(ls,m)) for ls in range(m+1))
for n in range(1,9):
    bad=0; ex=None; seen=set()
    for s in itertools.permutations(range(1,n+1)):
        h=tuple(sorted(caps(s)))
        if h in seen: continue
        seen.add(h)
        A=[math.prod(min(x,l+1) for x in h) for l in range(n)]
        row=[A[0]]+[A[i]-A[i-1] for i in range(1,n)]
        if not unimodal(row):
            bad+=1
            if ex is None: ex=(s,row)
    print(n,"capacity multisets:",len(seen),"non-unimodal:",bad,ex)
