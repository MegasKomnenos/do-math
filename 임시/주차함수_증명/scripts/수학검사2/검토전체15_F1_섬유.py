# 정리 2:old-2-5: n<=6 모든 섬유 행 단봉, n=7 sigma=(1,2,3,5,4,6,7) 섬유 행, 비단봉 섬유 존재.
# 선호 용량 h_i 는 정의 2:old-2-2 그대로 계산. 또 따름정리 2:old-2-4 (합 = A_{n,l}) 를 n<=8 에서 직접 모사값과 대조.
import itertools
def h(sig):
    n=len(sig); out=[]
    for i in range(1,n+1):
        js=[j for j in range(1,i) if sig[j-1]>sig[i-1]]
        out.append(i-(max(js) if js else 0))
    return out
def fiber_row(sig):
    n=len(sig); hs=h(sig)
    A=[1]
    for l in range(n):
        p=1
        for x in hs: p*=min(x,l+1)
        A.append(p)
    return [A[l+1]-A[l] for l in range(n)]
def unimodal(b):
    m=max(b); p=b.index(m)
    return all(b[i]<=b[i+1] for i in range(p)) and all(b[i]>=b[i+1] for i in range(p,len(b)-1))
for n in range(1,8):
    bad=[]
    tot=[0]*n
    for sig in itertools.permutations(range(1,n+1)):
        r=fiber_row(sig)
        for l in range(n): tot[l]+=r[l]
        if not unimodal(r): bad.append((sig,r))
    print(n,"비단봉 섬유 수",len(bad),"전체 행",tot)
    if n==7:
        print(" sigma=(1,2,3,5,4,6,7):",fiber_row((1,2,3,5,4,6,7)), "h=",h((1,2,3,5,4,6,7)))
        print(" 비단봉 섬유 보기 3개:",bad[:3])
