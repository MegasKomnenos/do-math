# R2 check: constants a_0, a_1 (corollary 4:gauss-coeff-numeric) and the second-piece interval of lemma 4:borel-tail-arc
import mpmath as mp
mp.mp.dps=30
# (the total-variation check lives in 검토전체23_R2_tv3.py; a direct w^{-5/2} formula is numerically unstable near w=0)
a0=mp.quad(lambda w: mp.e**(-w**3/3),[0,1,2,4,mp.inf]); a1=mp.quad(lambda w: w*mp.e**(-w**3/3),[0,1,2,4,mp.inf])
print('a0',a0,'a1',a1)
# second piece: sum_{j<=k} j Bor(j) - (2(2pi)^-1/2 sqrt k - 2/3) in [0, 2/3 (2pi)^-1/2 k^-1/2]
c=1/mp.sqrt(2*mp.pi)
s=mp.mpf(0)
bad=0
for j in range(1,20001):
    s+=mp.e**(-j+ (j-1)*mp.log(j) - mp.loggamma(j+1))*j
    d=s-(2*c*mp.sqrt(j)-mp.mpf(2)/3)
    if not (0<=d<=mp.mpf(2)/3*c/mp.sqrt(j)): bad+=1
    if j in (1,2,10,100,10000,20000): print(j, mp.nstr(d,8), mp.nstr(mp.mpf(2)/3*c/mp.sqrt(j),8))
print('bad',bad)
