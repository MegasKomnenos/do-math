from mpmath import mp, mpf, quad, exp, sqrt, pi, erfc
mp.dps=30
M0=quad(lambda y: exp(-y-y*y/2),[0,mp.inf]); print("M0",M0, " check e^{1/2}sqrt(pi/2)erfc(1/sqrt2)=", exp(mpf(1)/2)*sqrt(pi/2)*erfc(1/sqrt(2)))
M=[M0,1-M0]
for i in range(1,5): M.append(i*M[i-1]-M[i])
print("M0..M5", [mp.nstr(x,6) for x in M])
def Mstar(i):
    y=(-1+sqrt(1+4*i))/2; return y**i*exp(-y-y*y/2)
print("M*_2..5", [mp.nstr(Mstar(i),6) for i in range(2,6)])
print("sqrt(3pi/2)=", sqrt(3*pi/2), " 1/2+2*0.845204-sqrt(3pi/2)=", mpf(1)/2+2*mpf('0.845204')-sqrt(3*pi/2))
# Newton 계수 수: r=2..40, d=1..r-1, 차수 r+d+3 -> 계수 r+d+4 ?
print("coef count (deg r+d+3):", sum(r+d+4 for r in range(2,41) for d in range(1,r)), " (deg r+d+1):", sum(r+d+2 for r in range(2,41) for d in range(1,r)))
print("polys r<=170:", sum(r-1 for r in range(2,171)), " r<=40:", sum(r-1 for r in range(2,41)))
