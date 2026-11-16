# A9 E5(a) 검산: 정리 9.10(9:head-sum-2)의 행 m<=20000 부분을 D:m1-column-reading(88,933,203쌍 판독) 대신
# 명제 5:witness-position-bound(10장 명제 10:reduction-ga (i)가 쓰는 꼴: 행 i<=20000에서
# i-k >= 0.99+0.59963(i+1)^{2/3}+1.24847(i+1)^{1/3} 이면 b_{i,k-1}<=b_{i,k})로 대체할 수 있는지 본다.
# 확인: 3132<=k<=19403, q0=floor(0.75 k^{2/3}); 모든 q in [q0, min(k-1,20000-k)]에서 q >= f(k+q).
# 또 k>=19404(k<=19999)에서 q0=floor(k^{2/3})로 같은 확인.
f=lambda i: 0.99+0.59963*(i+1)**(2/3)+1.24847*(i+1)**(1/3)
bad=[]; worst=(1e9,None)
for k in range(3132,19404):
    q0=int(0.75*k**(2/3)); qmax=min(k-1,20000-k)
    for q in range(q0,qmax+1):
        sl=q-f(k+q)
        if sl<worst[0]: worst=(sl,(k,q))
        if sl<0: bad.append((k,q)); break
print("3132<=k<=19403, q0=floor(0.75k^{2/3}): 실패 열 수 =",len(bad), bad[:5], "; 최소 여유 q-f(k+q) =",worst)
bad=[]; worst=(1e9,None)
for k in range(19404,20000):
    q0=int(k**(2/3)); qmax=min(k-1,20000-k)
    for q in range(q0,qmax+1):
        sl=q-f(k+q)
        if sl<worst[0]: worst=(sl,(k,q))
        if sl<0: bad.append((k,q)); break
print("19404<=k<=19999, q0=floor(k^{2/3}): 실패 열 수 =",len(bad),"; 최소 여유 =",worst)
for k in (3132,5000,10000,19403,19404,19999):
    q=1
    while q<f(k+q): q+=1
    print(" k=%d: 증인 상계가 주는 q* = %d, q*/k^{2/3} = %.4f"%(k,q,q/k**(2/3)))
