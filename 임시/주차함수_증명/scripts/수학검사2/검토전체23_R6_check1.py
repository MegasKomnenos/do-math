# 7A 검산: 7.1-7.3의 식을 작은 크기에서 정확 유리수로 다시 센다.
import sys, io, itertools, math
from fractions import Fraction as Fr
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# (1) 열 인증 (가)의 정수 부등식
L = 10**21 * 400**10; R = 17**21 * 123**10
print("10^21*400^10 > 17^21*123^10 :", L > R, "%.6e %.6e" % (L, R))
print("17^21 = %.5e (<6.95e25?)" % 17**21, 17**21 < 695*10**23, " 123^10 = %.5e (<7.93e20?)" % 123**10, 123**10 < 793*10**18)
print("8.36^5 =", 8.36**5, " 1.513^5 =", 1.513**5, " 17*40836=", 17*40836)
print("1-(21/10)(10/17)^3 =", 1-2.1*(10/17)**3)

# (2) t_k, n#_k
def tk(k):
    j = 0
    while (k+1)**j * k**(j+1) + (k-1)**(2*j+1) < 2*k**(2*j+1): j += 1
    return j
for k in (2,3,10,140,141,203,204,205,500):
    t = tk(k); print("k=%d t_k=%d n#_k=%d (k^2+2k=%d)" % (k, t, k+(k+1)*t, k*k+2*k))
print("max n# for 2<=k<=140:", max(k+(k+1)*tk(k) for k in range(2,141)))
print("largest k with n#_k<=20000:", max(k for k in range(2,400) if k+(k+1)*tk(k) <= 20000))

# (3) 순열 통계: h_i, Z_k, H_k
def caps(s):
    n = len(s); h = []
    for i in range(n):
        j = i-1
        while j >= 0 and s[j] < s[i]: j -= 1
        h.append(i-j)   # i,j 0-기준: i-(j) = (i+1)-(j+1)
    return h
def A(n, l):  # A_{n,l} by permutations
    if n == 0: return 1
    tot = 0
    for s in itertools.permutations(range(n)):
        p = 1
        for x in caps(s): p *= min(x, l+1)
        tot += p
    return tot
Acache = {}
def Af(n, l):
    if l < 0: return 1 if n == 0 else 0
    if (n,l) not in Acache: Acache[(n,l)] = A(n,l)
    return Acache[(n,l)]
# 정리 6-6 / 명제 6-7 / 정리 6-2 / 6-11 (가) 를 n<=8에서
for n in range(1, 9):
    perms = list(itertools.permutations(range(n)))
    C = [caps(s) for s in perms]
    for k in range(2, n+1):
        W = []; 
        for h in C:
            w = 1
            for x in h: w *= min(x,k)
            W.append(w)
        tot = sum(W)
        assert tot == Af(n,k-1)
        EZ = Fr(sum(w*sum(1 for x in h if x>k) for w,h in zip(W,C)), tot)
        EH = Fr(sum(w*sum(1 for x in h if x==k) for w,h in zip(W,C)), tot)
        assert EZ >= Fr(n-k, k+1), (n,k,EZ)
        Rs = Fr(Af(n,k), tot); Rf = Fr(Af(n,k-2), tot)
        ok = math.log(1-1/k)*(-2)/math.log(1+1/k)
        assert float(Rf) > (1-1/k)*float(Rs)**(-ok), (n,k)
        # 6-2 (가)
        e1 = sum(Fr(w)*Fr(k+1,k)**sum(1 for x in h if x>k) for w,h in zip(W,C))/tot
        e2 = sum(Fr(w)*Fr(k-1,k)**sum(1 for x in h if x>=k) for w,h in zip(W,C))/tot
        assert e1 == Rs and e2 == Rf
        # 6-11 (가): E[H_k] = (n+1) a_{k-1} sum_{j=k+1}^{n+1} K_j a_{n+1-j}/a_n
        a = [Fr(Af(m,k-1), math.factorial(m)) for m in range(n+1)]
        ao = [Fr((m+1)**(m-1), math.factorial(m)) if m>0 else Fr(1) for m in range(n+2)]
        K = [Fr(0)]*(n+2)
        for j in range(1, n+2):
            s = sum((k-m)*ao[m-1]*K[j-m] for m in range(1,k) if j-m >= 0)
            if j == k+1: s += 1
            K[j] = s/j
        rhs = (n+1)*a[k-1]*sum(K[j]*a[n+1-j] for j in range(k+1, n+2))/a[n]
        assert rhs == EH, (n,k,rhs,EH)
print("정리 6-6, 명제 6-7, 정리 6-2(가), 정리 6-11(가): n<=8, 2<=k<=n 통과")
# y 일반의 정리 6-6 (Psi = 1{M<=k-1}, 모든 0<=y<=n) n<=7
for n in range(1,8):
    perms = list(itertools.permutations(range(n))); C=[caps(s) for s in perms]
    for k in range(1,n+2):
        W=[math.prod(min(x,k) for x in h) for h in C]; tot=sum(W)
        for y in range(0,n+1):
            EZ = Fr(sum(w*sum(1 for x in h if x>y) for w,h in zip(W,C)), tot)
            assert EZ >= Fr(n-y,y+1),(n,k,y)
print("정리 6-6 일반 y: n<=7 통과")

# (4) 소인 주차함수: C_{n,n}=(n-1)^(n-1), A_{k-1}=1/(1-C_k), C'_k = k - Q'(1-C)
def pfs(n):
    for a in itertools.product(range(1,n+1), repeat=n):
        if all(sum(1 for x in a if x<=b) >= b for b in range(1,n+1)): yield a
def maxdisp(a):
    n=len(a); occ=[False]*(n+2); M=0
    for x in a:
        p=x
        while occ[p]: p+=1
        occ[p]=True; M=max(M,p-x)
    return M
for n in range(1,7):
    cnt = {}
    for a in pfs(n):
        prime = all(sum(1 for x in a if x<=b) != b for b in range(1,n))
        if prime:
            M = maxdisp(a)
            for k in range(1,n+2):
                if M <= k-1: cnt[k] = cnt.get(k,0)+1
    assert cnt[n] == (n-1)**(n-1) if n>1 else cnt[n]==1, (n,cnt)
    Cnk = cnt
    globals().setdefault('CC',{})[n] = cnt
print("C_{n,n}=(n-1)^(n-1): n<=6 통과")
# A_{k-1} = 1/(1-C_k) 계수 비교 n<=6
for k in range(1,6):
    N=6
    c=[Fr(0)]+[Fr((CC[n].get(k,0) if k<=n+1 else CC[n][n]), math.factorial(n)) for n in range(1,N+1)]
    a=[Fr(1)]+[Fr(0)]*N
    for n in range(1,N+1):
        a[n]=sum(c[i]*a[n-i] for i in range(1,n+1))
    for n in range(0,N+1):
        assert a[n]==Fr(Af(n,k-1),math.factorial(n)),(k,n)
    # C' = k - Q'(1-C): Q'_{k-1} = sum_{m=1}^{k-1}(k-m) ao_{m-1} x^{m-1}
    ao=[Fr((m+1)**(m-1), math.factorial(m)) if m>0 else Fr(1) for m in range(N+1)]
    Qp=[(k-m)*ao[m-1] if 1<=m<=k-1 else Fr(0) for m in range(1,N+1)]  # coefficient of x^{m-1}
    omc=[Fr(1)]+[-x for x in c[1:]]
    for d in range(0,N):   # coefficient of x^d
        lhs=(d+1)*c[d+1]
        conv=sum(Qp[i]*omc[d-i] for i in range(0,d+1))
        rhs=(k if d==0 else 0)-conv
        assert lhs==rhs,(k,d,lhs,rhs)
print("A_{k-1}=1/(1-C_k), C'_k=k-Q'(1-C_k): k<=5, n<=6 통과")
# (5) b_{n,1} >= (n-1) n!/2
for n in range(4,8):
    b1 = Af(n,1)-Af(n,0); assert Af(n,0)==math.factorial(n); print("n=%d b_{n,1}=%d (n-1)n!/2=%d" % (n,b1,(n-1)*math.factorial(n)//2))
