from fractions import Fraction
from math import log, exp
L=10**21*400**10; R=17**21*123**10
print("L",L, "R",R, L>R, float(L), float(R))
print("17^21*123^10 < 5.52e46:", R<5.52e46, "17^21<6.95e25:",17**21<6.95e25, "123^10<7.93e20:",123**10<7.93e20)
print("(40/41)(10/17)^2.1 =", (40/41)*(10/17)**2.1)
# o_k bound and hf' bound
k=41
ok=-2*log(1-1/k)/log(1+1/k); print("o_41",ok, 2*(k+1)/(k-1))
print("1-2.1*(10/17)**3 =",1-2.1*(10/17)**3)
# t_k and n_sharp
def tk(k):
    j=0
    while not ((k+1)**j*k**(j+1)+(k-1)**(2*j+1)>=2*k**(2*j+1)): j+=1
    return j
mx=0
for k in range(2,141):
    t=tk(k); ns=k+(k+1)*t; mx=max(mx,ns)
print("max n_sharp k<=140:",mx, "t_140",tk(140), "n_sharp_140", 140+141*tk(140))
for k in (2,3,5,10,41,121,140,141,500,2000): print(k,tk(k),k+(k+1)*tk(k))
