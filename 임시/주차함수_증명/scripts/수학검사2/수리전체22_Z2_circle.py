from math import sqrt
import cmath
# hand bounds
Nd=12/100+7/1e4
slo, shi = sqrt(1-Nd), sqrt(1+Nd)
glo, ghi = slo/3.01, shi/2.99
print('gamma in', glo, ghi)
u0 = (1+ghi)/2
x = 1.01*0.01/2.99**2
C1 = u0/glo**2; C2 = u0*(2+u0)/glo**5; C3 = 2.5*u0*(6+ghi+ghi**2)/glo**8
print('u0',u0,'x',x,'C1',C1,'C2',C2,'C3',C3)
uh = u0 + x*C1 + x*x*C2 + x**3*C3
print('uhat',uh, 'H<=',(3.01*uh+2+0.01)/0.01, 'with 0.7:', (3.01*0.7+2.01)*100)
# sample
mx=0; gmin=9; gmax=0; um=0
for nu in (-1,0):
    for it in range(21):
        th=it/20
        for m in range(2000):
            w=0.01*cmath.exp(2j*cmath.pi*m/2000)
            Nt=3+(nu+1-th)*w
            nm=1+(2*nu+10+2*th)*w+((nu+1)**2+2*(nu-3)*th+th*th)*w*w
            g=cmath.sqrt(nm)/Nt
            xn=(1-th*w)*w/Nt**2
            u=(1+g)/2
            c1=(1-u)/g**2; c2=-(1-u)*(2+u)/g**5; c3=5*(1-u)*(6+g-g*g)/(2*g**8)
            uh=u+xn*c1+xn**2*c2+xn**3*c3
            H=(Nt*uh-2-nu*w)/w
            mx=max(mx,abs(H)); gmin=min(gmin,abs(g)); gmax=max(gmax,abs(g)); um=max(um,abs(uh))
print('sampled max|H|',mx,'gamma',gmin,gmax,'max uhat',um)
# band hand inequalities for (다)
ok=True
for nu in range(1,601):
    H1=26+4*nu; H2=506+97*nu+5*nu*nu; H3=11016+3187*nu+239*nu**2+6*nu**3
    if not (H2+20 < 1e4*H1 and H3 < 1e4*(H2-20)): ok=False
print('band hand ineq ok', ok)
print(10**4/29999**2, 2e7/3**7, 2e7/2.9999**7, 2e7*3.07*1e4*1e16/(29999**8)*1e12)
