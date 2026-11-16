import math
L=10**21*400**10; R=17**21*123**10
print("L=%.6e R=%.6e L>R=%s"%(L,R,L>R))
def B(k): return -(-k*k//4)
def cnt(ks):
    d=sum(2*B(k)-(2*k+1)+1 for k in ks); b=sum(2*B(k)-B(k)+1 for k in ks); return d,b
print("k121-160",cnt(range(121,161)))
print("k161-500",cnt(range(161,501)))
for kb in (121,125.5,495.5,500):
    print(kb, 0.34+0.65*math.log(kb))
# hf check
ok=0.4*0+40/41*(10/17)**2.1
print("40/41*(10/17)^2.1=",ok, ">0.3", ok>0.3)
print("1-2.1*(10/17)^3=",1-2.1*(10/17)**3)
print("17^4",17**4,"17^21<",17*8.36**5*1e20, 17**21, "123^10", 123**10, 1.513**5*1e20)
