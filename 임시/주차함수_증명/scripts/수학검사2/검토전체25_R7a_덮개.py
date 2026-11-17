# 검토전체25 R7a: 정리 7:old-6-13 증명의 경우 나눔이 max(2k+1,20001)<=n<=2k+102 (k>=9950)를 빠짐없이 덮는지 전수
J=[(10000,50),(12000,58),(13000,79),(14000,99),(15000,102)]
rows=[(12000,58),(13000,79),(14000,99),(15000,102)]
def pair(k,nu): return any(k>=K and 1<=nu<=L for K,L in J)
def analytic(k,nu):
    if k>=10000 and 1<=nu<=19: return True
    if k>=11100 and 20<=nu<=40: return True
    return any(k>=K1 and 41<=nu<=m for K1,m in rows)
def strips(k,n):
    nu=n-2*k
    if 9981<=k<=11099 and max(20001,2*k+1)<=n<=2*k+40: return True
    if 9950<=k<=11999 and max(2*k+41,20001)<=n<=2*k+102: return True
    if 12000<=k<=12999 and 59<=nu<=102: return True
    if 13000<=k<=13999 and 80<=nu<=102: return True
    if 14000<=k<=14999 and 96<=nu<=102: return True
    return False
miss=0;tot=0;both=0;only_s=0
for k in range(2001,20001):
    for nu in range(1,103):
        n=2*k+nu
        if n<20001: continue
        tot+=1
        a=pair(k,nu) and analytic(k,nu); s=strips(k,n)
        if not(a or s): miss+=1; print('miss',k,nu)
        if s and not a: only_s+=1
print('positions',tot,'missing',miss,'strip-only',only_s)
# 행으로 읽기: n>=20001, i=1..51
bad=0
for n in range(20001,20400):
    kn=(n+1)//2
    for i in range(1,52):
        k=kn-i
        if not (k>=2001 and max(2*k+1,20001)<=n<=2*k+102): bad+=1
print('row-reading bad',bad)
