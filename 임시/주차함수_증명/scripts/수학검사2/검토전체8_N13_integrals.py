# D.M-natural-integrals의 j1, j2와 D.AR-integrals의 J1..J4, 요구값을 고정밀 수치적분으로 다시 잰다(대조용).
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
try:
    import mpmath as mp
    mp.mp.dps = 30
    q = lambda r: 1+mp.mpf('0.7501')*r/(1+r)
    f2 = lambda s: 2*mp.sqrt(1+s*s)*mp.mpf('0.70836')*q(s*s)**3
    f1 = lambda s: f2(s)*(mp.mpf('2.528571')-mp.log(q(s*s))+3*mp.log(s))
    j2 = mp.quad(f2,[0,1]); j1 = mp.quad(f1,[0,mp.mpf('1e-6'),mp.mpf('0.01'),1])
    print("j2", j2, "j1", j1)
    print("decrease cond", j1 + j2*(mp.log(6667)/2-1))
    def DDL(k):
        k=mp.mpf(k); d=2*k**(mp.mpf(2)/3)
        eps=-mp.log(1-mp.sqrt(k+1)/(mp.mpf('0.485917')*k)); epsp=mp.mpf('2.26')/k+mp.mpf('0.47')/(d-1)
        gam=mp.mpf('2.6047')*(mp.mpf('2.53')+mp.log(k)/2+eps+mp.mpf('1.5')/k)/k
        c=1/mp.sqrt(2*mp.pi)
        return mp.mpf('0.457143')*c*q(d/k)*mp.sqrt(1+d/k)*(d+1)**mp.mpf('3.5')/k**3 + 2*c/mp.sqrt(k)*(1+epsp)*(j1+(mp.log(k)/2+eps)*j2+gam) + mp.mpf('3.9')*c/k
    for k in (6667,6668,8065,9551,9705,9949): print("DDL",k,DDL(k))
    # AR integrals
    k=mp.mpf(6668)
    J1 = mp.mpf(2.5)*mp.quad(lambda t: (1+t+2/k)**(-3.5)*max(0,1-3/mp.sqrt(k)*(t-1/k)**(-1.5)), [1/k, 1/k+(3/mp.sqrt(k))**(mp.mpf(2)/3), 1])
    c2 = 3*(k-1)*k**(-1.5)
    J2 = mp.mpf(2.5)*mp.quad(lambda t: (1+t+1/k)**(-3.5)*max(0,1-c2*(t-1/k)**(-1.5)), [1/k, 1/k+c2**(mp.mpf(2)/3), (k-1)/k])
    J3 = (k/(2*k+1))**2.5*(1-3/mp.sqrt(k)); J4=(k/(2*k+1))**2.5*(1-3/mp.sqrt(k-1))
    print("J1..J4", J1, J2, J3, J4, "sum", J1+J2+J3+J4)
    db = mp.mpf('6.62')/mp.sqrt(k)
    print("band req", (1+db/2)/(1-db/2), "bulk req", 1+mp.mpf('1.676')*db/(2-db)+mp.mpf('0.676')*(mp.mpf('0.8825')/mp.sqrt(k)+mp.mpf('0.72')/k+mp.mpf('41.2')*(2/(mp.mpf('0.48')*k-102))**1.5))
    # upper function max over q
    best=None
    for qq in range(1,6668):
        N=k+qq
        v = min(1, 3*k*mp.mpf(qq)**(-1.5))/(k*(mp.mpf('0.734')*max(0,(qq+1)**(-0.5)-(mp.ceil(N/2)+1)**(-0.5))+mp.mpf('0.98')/(N+1)))
        if best is None or v>best[0]: best=(v,qq)
    print("upper fn max", best[0]*mp.sqrt(k), "at q", best[1])
    # band-LP (나) Upsilon hat at 48966 and 48965
    def Ups(k):
        k=mp.mpf(k); u = 3/mp.mpf('0.35')*(mp.mpf('1.35')+1/k)*(mp.mpf('0.65')-1/k)**(-1.5)/mp.sqrt(k); return (k-1)*u/(2*k+1)
    for kk in (48965,48966): print("Ups",kk, Ups(kk), "rhs", (1-mp.mpf(1)/kk)**103/20)
    # H-star-plus C-curve limit
    print("C limit", (mp.mpf(1)/5)/(mp.mpf('0.7978')*mp.sqrt(2)-mp.mpf('0.8848')))
    # xcert A3: Xc and s1
    pc = 1/mp.sqrt(2*mp.pi)/mp.e
    S0 = sum(mp.mpf(n-1)**(n-1)*mp.exp(-n)/mp.factorial(n) for n in range(1,257))
    Xc = 1 - S0 - 2*pc/mp.sqrt(257) + pc*mp.mpf(257)**(-1.5)
    print("S0",S0,"Xc",Xc)
    k=mp.mpf(10)**30
    CL = lambda s: S0 + pc*(2/mp.sqrt(257) - 2/mp.sqrt(k) + (mp.e**s*(1/s+1.5/s**2)-3 - 2*s*mp.sqrt(257/k)*mp.e**(257*s/k))/mp.sqrt(k) - mp.mpf(257)**(-1.5)*mp.e**(257*s/k))
    s1 = mp.findroot(lambda s: CL(s)-1, 39)
    print("s1", s1, "epsU/s", pc/mp.sqrt(k)*mp.e**s1/s1, "Xc/(1+1.5/s)", Xc/(1+1.5/s1))
except ImportError as e:
    print("mpmath unavailable", e)
