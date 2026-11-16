from fractions import Fraction as F
import math
# 1. integer inequality (column-lemma)
L=10**21*400**10; R=17**21*123**10
print("int ineq", L>R, "%.6e %.6e"%(L,R))
# 2. column-cert counts
dd=0; rr=0; dd2=0; rr2=0
for k in range(121,161):
    B=-(-k*k//4); dd+= 2*B-(2*k+1)+1; rr+= 2*B-B+1
for k in range(161,501):
    B=-(-k*k//4); dd2+= 2*B-(2*k+1)+1; rr2+= 2*B-B+1
print("direct diff counts", dd, dd2, "ratio counts", rr, rr2)
# 3. cor-S-prime values with table rounded A0,B0
for (k0,y,A0,B0) in [(501,F(13,100),F('1.4708'),F('0.098505')),(1855,F(2,25),F('2.5335'),F('0.060259')),(6098,F(11,200),F('2.7354'),F('0.0422'))]:
    xi=F(1,k0)
    v=(y-xi)*(y-2*xi-xi*xi)-(1+xi)**2*(A0*xi+B0*y)
    print("corS", k0, float(v))
    vert=(3*xi+xi*xi)/2+(1+xi)**2*B0/2
    print("  vertex", float(vert), float(vert)<=y)
# 4. m1 ratio
print("m1 ratio", (3288-3136)/3136**(2/3))
# 5. pair count
un=sum((s//2)*(51-s) for s in range(2,51)); od=sum((s-1)*(51-s) for s in range(2,51))
print("pair counts", un, od)
# 6. moment first range count
c=sum((13*k*k)//100 - 2*k for k in range(501,841))
print("moment first range positions", c)
# 7. nM ratio
print(20507/841**1.5, 73032/2000**1.5)
# 8. 0.836 k^1.5 vs n_psi
for k,n in [(501,9373),(841,20025),(1000,25835),(2000,71871)]:
    print(k, math.ceil(0.836*k**1.5), n)
# 9. H-star-plus C limit
print("C limit", 0.2/(0.7978*math.sqrt(2)-0.8848))
# 10. band-boxes margins
for v,b in [(1.0097628,1.009),(1.0068936,1),(1.0136495,1),(1.0091044,1),(1.052428971,1.05)]:
    print(v,b,"%.4f%%"%((v-b)/b*100))
# 11. 0.1113*6668
print(0.1113*6668)
# 12. eps0 = floor(2^{2/3}(k0+1)^{2/3})
for k0 in [6668,8065,9551,9705]:
    print(k0, math.floor(2**(2/3)*(k0+1)**(2/3)), math.floor(2*k0**(2/3)))
# 13. 4 sqrt2 etc
print("46sqrt2-12", 46*math.sqrt(2)-12)
# 14. xc
S0=None
