from mpmath import mp, mpf, quad, exp, sqrt, pi
mp.dps=30
M0=quad(lambda y: exp(-y-y*y/2),[0,mp.inf]); M=[M0,1-M0]
for i in range(1,5): M.append(i*M[i-1]-M[i])
Ms=lambda i: ((-1+sqrt(1+4*i))/2)**i*exp(-((-1+sqrt(1+4*i))/2)-((-1+sqrt(1+4*i))/2)**2/2)
C1=2*Ms(2)+M[3]/2+M[5]/3; C2=Ms(3)/2+Ms(5)/3+M[4]/2; C3=Ms(4)/2+M[3]/6; C4=Ms(3)/6
print("C1..C4", [mp.nstr(x,6) for x in (C1,C2,C3,C4)])
M26=quad(lambda y: y*y*exp(-y-y*y/2),[0,6]); tail=M[2]-M26
print("M2-M2^(6) =", tail, " bound (6+1/6)e^-24 =", (6+mpf(1)/6)*exp(-24), " ok:", tail<= (6+mpf(1)/6)*exp(-24))
s=mpf(100)
L=(M26-C1/s-C2/s**2-C3/s**3-C4/s**4)/(M[1]+(M0+exp(-mpf(1)/2))/s+1/s**2)
print("L(10^4) =", L, " >=0.845204:", L>=mpf('0.845204'))
