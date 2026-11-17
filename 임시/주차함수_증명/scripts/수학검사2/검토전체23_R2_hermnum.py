# R2 check: numeric sanity of lemma 4:gauss-contraction (na),(da) and 4:hermite-nu (na),(da),(ra) at k=10000, nu in {-1,0,1,19}
import mpmath as mp
mp.mp.dps=80
def run(k,nu,theta=0):
    y=mp.mpf(k)-theta; n=2*k+nu; N=n+y+1; x=y/N**2; q=n*x
    def v0(i): return (1+mp.sqrt(1-4*i))/2
    def vhat(i):
        g=mp.sqrt(1-4*i); w=(1+g)/2
        return w+x*(1-w)/g**2-x**2*(1-w)*(2+w)/g**5+x**3*5*(1-w)*(6+g-g**2)/(2*g**8)
    u=mp.mpf(1); logHe=mp.mpf(0); maxerr=0; minslack=mp.inf
    for j in range(2,n+1):
        xj=(j-1)*x
        u=1-xj/u
        logHe+=mp.log(u)
        if j%97==0 or j>n-5:
            maxerr=max(maxerr,abs(u-vhat(xj))/x**4)
            minslack=min(minslack,u-v0(xj))
    logHe+=n*mp.log(N)
    vt=N*u-n
    U=N*v0(q); W=N*(2*v0(q)-1)
    lb=mp.log(mp.sqrt(U/W))+n*mp.log(U)+(N-U)**2/(2*y)-mp.mpf(11)/2*x-350*n*x**2
    # M0 = e^{-y/2} He_n vt/((n+vt) p_n)
    logM0=-y/2+logHe+mp.log(vt)-mp.log(n+vt)-(n-1)*mp.log(n+1)
    H0=4;H1=-(26+4*nu)-8*theta;H2=506+97*nu+5*nu**2+(168+16*nu)*theta+12*theta**2
    H3=-(11016+3187*nu+239*nu**2+6*nu**3)-(5362+762*nu+26*nu**2)*theta-(594+36*nu)*theta**2-16*theta**3
    kk=mp.mpf(k)
    # M2/M0 at y=k
    U2=1+(2*nu+2)/kk+nu*(nu+1)/kk**2; V2=4+(4*nu+2)/kk+nu*(nu+1)/kk**2
    print('k',k,'nu',nu,'theta',theta,'| max|u-vhat|/x^4 (sampled)',mp.nstr(maxerr,6),'min(u-v0)',mp.nstr(minslack,4),
          '| logHe-lb',mp.nstr(logHe-lb,6),'| vt',mp.nstr(vt,12),'in [',mp.nstr(4-(26+4*nu)/kk,10),',4)',
          '| k^2|vt-H0-H1/k-H2/k^2|',mp.nstr(kk**2*abs(vt-H0-H1/kk-H2/kk**2),5),
          '| k^2|vt-..-H3/k^3|',mp.nstr(kk**2*abs(vt-H0-H1/kk-H2/kk**2-H3/kk**3),5),
          '| M0',mp.nstr(mp.e**logM0,10),'>=',mp.nstr(4*mp.sqrt(2)*(1-(23.75+2.5*nu)/kk),10),
          '| g_k=2-kM2/M0',mp.nstr(2-kk*(U2-V2/vt),8) if theta==0 else '')
for nu in (-1,0,1,19):
    run(10000,nu)
run(10000,0,mp.mpf(1)); run(10000,-1,mp.mpf(1)/2)
