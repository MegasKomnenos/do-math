import mpmath as mp
mp.mp.dps=30
# 9-1 m1-column-reading 쌍 수
def floor_pow(k,p):  # floor(p*k^(2/3)) 정확히
    v=mp.mpf(p)*mp.mpf(k)**(mp.mpf(2)/3)
    return int(mp.floor(v))
tot=0; tot2=0
for k in range(3132,19404):
    lo=k+floor_pow(k,'0.75'); hi=min(2*k-1,20000)
    tot+=max(0,hi-lo+1)
    lo2=k+floor_pow(k,'1'); tot2+=max(0,hi-lo2+1)
print("m1 pairs 0.75:",tot," pairs 1.0:",tot2)
pos=sum((n-3)-(-(-(n-1)//2))+1 for n in range(5,20001))
print("positions n=5..20000:",pos)
# 9-3 AR integrals at k=6668
k=mp.mpf(6668)
def J1():
    c=3/mp.sqrt(k)
    f=lambda t: mp.mpf(5)/2*(1+t+2/k)**(-mp.mpf(7)/2)*max(0,1-c*(t-1/k)**(-mp.mpf(3)/2))
    t0=1/k+c**(mp.mpf(2)/3)
    return mp.quad(f,[t0,0.01,0.1,1])
def J2():
    c=3*(k-1)/k**mp.mpf(1.5)
    f=lambda t: mp.mpf(5)/2*(1+t+1/k)**(-mp.mpf(7)/2)*max(0,1-c*(t-1/k)**(-mp.mpf(3)/2))
    t0=1/k+c**(mp.mpf(2)/3)
    return mp.quad(f,[t0,0.01,0.1,(k-1)/k])
j1=J1(); j2=J2(); j3=(k/(2*k+1))**mp.mpf(2.5)*(1-3/mp.sqrt(k)); j4=(k/(2*k+1))**mp.mpf(2.5)*(1-3/mp.sqrt(k-1))
print("AR:",j1,j2,j3,j4,"sum",j1+j2+j3+j4)
db=mp.mpf('6.62')/mp.sqrt(k); print("band req",(1+db/2)/(1-db/2))
bulk=1+mp.mpf('1.676')*db/(2-db)+mp.mpf('0.676')*(mp.mpf('0.8825')/mp.sqrt(k)+mp.mpf('0.72')/k+mp.mpf('41.2')*(2/(mp.mpf('0.48')*k-102))**mp.mpf(1.5))
print("bulk req",bulk)
# 10-1 M-natural integrals
q=lambda r: 1+mp.mpf('0.7501')*r/(1+r)
g=lambda s: 2*mp.sqrt(1+s*s)*mp.mpf('0.70836')*q(s*s)**3
jj2=mp.quad(g,[0,0.01,0.1,1])
jj1=mp.quad(lambda s: g(s)*(mp.mpf('2.528571')-mp.log(q(s*s))+3*mp.log(s)),[0,1e-6,0.01,0.1,1])
print("j2",jj2,"j1",jj1, "dec cond", jj1+jj2*(mp.log(6667)/2-1))
print("3*sqrt2*0.16696=",3*mp.sqrt(2)*mp.mpf('0.16696'), " 2.5-ln2-ln0.485917=",mp.mpf('2.5')-mp.log(2)-mp.log(mp.mpf('0.485917')))
def DDL(k):
    k=mp.mpf(k); d=2*k**(mp.mpf(2)/3); c=(2*mp.pi)**-0.5
    eps=-mp.log(1-mp.sqrt(k+1)/(mp.mpf('0.485917')*k)); epsp=mp.mpf('2.26')/k+mp.mpf('0.47')/(d-1)
    gam=mp.mpf('2.6047')*(mp.mpf('2.53')+mp.log(k)/2+eps+mp.mpf('1.5')/k)/k
    return mp.mpf('0.457143')*c*q(d/k)*mp.sqrt(1+d/k)*(d+1)**mp.mpf(3.5)/k**3+2*c/mp.sqrt(k)*(1+epsp)*(jj1+(mp.log(k)/2+eps)*jj2+gam)+mp.mpf('3.9')*c/k
for kk in (6667,6668,8065,9551,9705,9949): print("DDL",kk,DDL(kk))
for k0 in (6668,8065,9551,9705): print("eps0",k0,int(mp.floor(mp.mpf(2)**(mp.mpf(2)/3)*mp.mpf(k0+1)**(mp.mpf(2)/3))))
