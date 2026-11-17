import mpmath as mp
mp.mp.dps=25
def M(n,c): # int_R z^{2n} e^{-c z^2/2} dz / sqrt(2 pi)
    return mp.fac2(2*n-1)*c**(-n-mp.mpf(1)/2)
# F0 ∝ z^4 e^{-z^2/2} ∫ rho^2 (mu z^2 + mu^2 z^4/4) (2 - 2 rho^2 z^2 ∫_0^1 e^{-rho^2 z^2 (1-s^2)/2} ds) d rho
def partA(r):
    mu=1-r*r
    return r*r*(mu*M(3,1)+mu*mu/4*M(4,1))*2
def partB(r,s):
    mu=1-r*r; c=1+r*r*(1-s*s)
    return r*r*2*r*r*(mu*M(4,c)+mu*mu/4*M(5,c))
A=mp.quad(partA,[0,1]); B=mp.quad(partB,[0,1],[0,1])
print("A =",A," B =",B," A-B =",A-B)
