# R12 review check: D.column-certification-k500 counts and integer inequality
import math, json
def B(k): return (k*k+3)//4
d1=sum(2*B(k)-2*k for k in range(121,161)); d2=sum(2*B(k)-2*k for k in range(161,501))
b1=sum(B(k)+1 for k in range(121,161)); b2=sum(B(k)+1 for k in range(161,501))
print('direct',d1,d2,'band',b1,b2)
L=10**21*400**10; R=17**21*123**10
print(L>R, '%.6e'%L, '%.6e'%R)
print('17^21=%.4e 123^10=%.4e'%(17**21,123**10), 17*8.36**5, 1.513**5, 6.95e25*7.93e20)
# radii c
for k,rn in ((121,416066935374),(500,408049248555)):
    x=rn/2**40; print(k, x, (x*math.e-1)*k)
for km in (125,495,500):
    print(km, 0.34+0.65*math.log(km))
print('k<=141 2B<10000?', [(k,2*B(k)) for k in (140,141,142)])
print('n sharp', 140*140+2*140)
