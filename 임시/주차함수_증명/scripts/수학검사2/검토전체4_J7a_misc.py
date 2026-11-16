# J7a: 7.4·7.5절의 흩어진 수치 재계산
import math
print("ceil(2002^(4/3)) =", math.ceil(2002**(4/3)), " exact-ish:", 2002**(4/3))
print("2 e^{-5.3146*0.6996} =", 2*math.exp(-5.3146*0.6996))
print("0.7*2001/2002 =", 0.7*2001/2002)
print("0.3^1.5/2 =", 0.3**1.5/2, " *e^{-3/25233} =", 0.3**1.5/2*math.exp(-3/25233))
print("varsigma needed: ", math.log(2/0.0820)/0.6996)
print("n_M ratios:", 20507/841**1.5, 73032/2000**1.5, " 841^1.5=",841**1.5)
print("2e7*3.07/9^4 =", 2e7*3.07/9**4)
print("N/k max (nu=600,k=1e4):", 3+601/1e4)
print("1/(9e4) =", 1/9e4)
# integer-strips counts
c1=sum(max(0, 2*k+40-max(20001,2*k+1)+1) for k in range(9981,11100)); print("(가) count", c1)
c2=sum(max(0, 2*k+102-max(2*k+41,20001)+1) for k in range(9950,12000)); c3=1000*44+1000*23+1000*7; print("(나)+(다) count", c2+c3, c2, c3)
# pi^sharp_48 at k=10000
print("pi#_48 =", 48*47/(2*10001))
# C M^{3/2}
for M,C in [(120,0.54),(250,0.593),(300,0.522),(450,0.548),(700,0.519)]:
    print(M,C,C*M**1.5)
# vertical-nu (다): normalization ratio bound at nu=600,k=1e4 and nu=k
for k,nu in [(10000,600),(10000,10000)]:
    n=2*k+nu; r=((n+1)/(2*k))**1.5*math.exp(1/(12*(n+1)))
    print(f"n_k/n_inf k={k} nu={nu}: {r:.4f}; n_k≈{r*2/math.sqrt(math.pi):.4f}; Bn_k<= {r*2/math.sqrt(math.pi)/math.sqrt(2*math.pi):.4f}")
# (1,33,16) positivity of pi^sharp<1 etc. ; also 1.12e-5
print("k^-1/3 at 1e4:", 1e4**(-1/3))
# analytic (가) differences
vals=[0.2048,0.1938,0.1827,0.1717,0.1607,0.1496,0.1386,0.1275,0.1165,0.1054,0.0944,0.0833,0.0723,0.0613,0.0502,0.0392,0.0281,0.0170,0.0060]
print("diffs:", [round(vals[i]-vals[i+1],4) for i in range(len(vals)-1)])
# heavy-block: m<=2k+1 for q<=k+2 ; pi#_q decreasing in k; check (k+q)pi#_q/(1-pi#_q) decreasing in k numerically
f=lambda k,q: (k+q)*q*(q-1)/(2*(k+1))/(1-q*(q-1)/(2*(k+1)))
print("exbar monotone check:", f(10000,30)>f(20000,30))
