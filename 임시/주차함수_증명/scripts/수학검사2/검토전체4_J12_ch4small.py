# J12: D.QL-small-n (3<=n<=15 exact), D.crossing-small-n (n<=400 exact via columns; A^c recurrence check), (4.14)-free rational checks
import sys
from math import comb
from fractions import Fraction as F
sys.set_int_max_str_digits(0)
N=400
P=[1]+[(n+1)**(n-1) for n in range(1,N+1)]
def column(ell,N):
    A=[1]+[0]*N
    for n in range(1,N+1):
        A[n]=sum(comb(n-1,j)*min(j+1,ell+1)*A[j]*A[n-1-j] for j in range(n))
    return A
cols={}
def A(n,l):
    if l<0: return 0
    if l>=n-1: return P[n]
    if l not in cols: cols[l]=column(l,N)
    return cols[l][n]
def b(n,l): return A(n,l)-A(n,l-1)
# QL small n
for n in range(3,16):
    row=[b(n,l) for l in range(n)]
    dec=[l for l in range(0,n-2) if 2*l<=n-2 and row[l]>row[l+1]]
    ok=all(row[l+1]**2>=row[l]*row[l+2] for l in dec)
    strict=all(row[l+1]**2>row[l]*row[l+2] for l in dec)
    uni = all(row[i]<=row[i+1] for i in range(0,max(dec+[-1])+0)) if False else None
    print("n",n,"row",row,"QL decreasing levels",dec,"QL holds",ok,"strict",strict)
# crossing: b_{n,k_n} < b_{n,k_n+1} for 5<=n<=400
bad=[]; 
for n in range(5,N+1):
    k=(n+1)//2
    if not (b(n,k)<b(n,k+1)): bad.append(n)
print("crossing false at n in", bad, " (expected 5..19)")
# A^c recurrence check for n<=2l+4, on l in a few values, n<=400
def Ac(n,l): return P[n]-A(n,l)
err=0
for l in [3,10,50,100,150,199]:
    for n in range(1,min(N,2*l+4)+1):
        s1=sum(comb(n-1,j)*(j-l)*P[j]*P[n-1-j] for j in range(l+1,n))
        s2=sum(Ac(i,l)*comb(n-1,i)*P[n-1-i]*((l+1)+min(n-i,l+1)) for i in range(l+2,n))
        if s1+s2!=Ac(n,l): err+=1
print("A^c recurrence mismatches:",err)
# rational checks (ㅅ)
lhs=F(699,100)-F(7,2)-F(6*699,100*31)-F(75,100*31)-F(13*699,2*100*961)-F(12*699,100*30000)
print("(na) value", lhs, lhs==F(495594511,240250000), float(lhs))
v=F(5642,1000)*F(16809,10000)*F(39893,100000)-F(163,10000)-F(3554,1000)
print("(da) final", float(v), v>F(213,1000))
S=2918732888; print("s=S/2^30 =", S/2**30)
print("7 D-sums", 176+2304+118+935+533+455+243, sum(F(x) for x in ['183.51','2303.07','203.57','983.74','920.70','454.86','418.83']))
# 19985 count
print("count n>=16 among n in {2k-1,2k}, 8<=k<=10000:", sum(1 for k in range(8,10001) for n in (2*k-1,2*k) if n>=16))
