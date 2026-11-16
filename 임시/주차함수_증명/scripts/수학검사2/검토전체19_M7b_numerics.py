from mpmath import mp, mpf, sqrt, log, exp, pi, ceil, floor
mp.dps = 30
out = []
# theorem-W (가)
out.append(("1-0.8/sqrt(301)", 1 - mpf('0.8')/sqrt(301)))
out.append(("(2pi)^-1/2", (2*pi)**-0.5))
out.append(("0.9538/0.398943", mpf('0.9538')/mpf('0.398943')))
out.append(("0.14*2.38*0.9999", mpf('0.14')*mpf('2.38')*mpf('0.9999')))
# sg_n bound at n=6263
n = 6263
sg = n*log(mpf(n)/(n+1)) + 1
out.append(("sg_6263", sg)); out.append(("exp(-sg_6263)", exp(-sg)))
out.append(("sg bound", 1/(2*(n+1)) + 1/(6*n*(n+1))))
k = 3131
out.append(("D_k(2) k=3131", mpf('0.08329')*sqrt(k) - 2 - mpf('42.14')/k))
t = mpf(k)**(mpf(1)/6)
out.append(("k^(1/6)", t))
out.append(("right end bound", mpf('0.33316')*(sqrt(k) - 2*t + 1/t) - mpf('1.0005')*mpf(k)**(mpf(1)/3) - mpf('1.0145')))
out.append(("deriv at 3131", mpf('0.33316')*(3*mpf(k)**(mpf(1)/3) - 2 - mpf(k)**(-mpf(1)/3)) - mpf('2.001')*t))
out.append(("(1+1/3131)^(4/3)", (1+mpf(1)/k)**(mpf(4)/3)))
out.append(("nPD/k exact k=3131", (ceil((k+1)**(mpf(4)/3)) + k + 1)/mpf(k)))
out.append(("1.0005k^(1/3)+1.001", mpf('1.0005')*mpf(k)**(mpf(1)/3)+mpf('1.001')))
out.append(("nPD >= 3k+2 at 3131?", ceil((k+1)**(mpf(4)/3)) + k + 1 - (3*k+2)))
# direct check D_k(n/k) over integer n at k=3131 min
def G(k, n):
    sgn = n*log(mpf(n)/(n+1)) + 1
    return mpf('0.14')/n*(mpf('2.38')*mpf(k)**1.5*(n-k+1)**2/(exp(sgn)*n*(n+1)) - 301)
k=3131; nPD = int(ceil((k+1)**(mpf(4)/3)) + k + 1)
mn = min((G(k,n), n) for n in range(2*k+1, nPD))
out.append(("min G_k(n) k=3131 over [2k+1,nPD-1]", mn))
# threshold-unit-ratio
k = 6667
j0 = floor(mpf('0.3')*k)
out.append(("j0", j0))
val = -(mpf('0.3')*k-1)*(mpf('0.3')*k)/(2*(mpf('1.3')*k+1))
out.append(("-(0.3k-1)(0.3k)/(2(1.3k+1))", val))
out.append(("1+1.5log k + val", 1 + mpf(1.5)*log(k) + val))
out.append(("exact -sum i/(k+1+i)", -sum(mpf(i)/(k+1+i) for i in range(1, int(j0)+1))))
out.append(("exact log Pi_up", -sum(log(1+mpf(i)/(k+1)) for i in range(1, int(j0)+1))))
out.append(("e^0.3", exp(mpf('0.3'))))
out.append(("(1+1/k)^j0", (1+mpf(1)/k)**j0))
out.append(("e^(3/(2k))", exp(mpf(3)/(2*k))))
out.append(("1.00023*1.34986", mpf('1.00023')*mpf('1.34986')))
out.append(("2*0.7654-1.3502", 2*mpf('0.7654')-mpf('1.3502')))
# old-6-22 bound
out.append(("1003/e", 1003/exp(1)))
out.append(("x_501", (mpf(501)/502)**500))
out.append(("x_501*1003", (mpf(501)/502)**500*1003))
# lemma explicit-bounds constants
out.append(("2/sqrt(2pi)", 2/sqrt(2*pi)))
for name, v in out:
    print(name, "=", v)
