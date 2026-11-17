from mpmath import mp, mpf, sqrt
mp.dps=20
k=mpf(2001)
u=3/mpf('0.35')*(mpf('1.35')+1/k)*(mpf('0.65')-1/k)**(-mpf(3)/2)*k**(-mpf(1)/2)
print("u(2001)=",u)
print("factors", 3/mpf('0.35'), mpf('1.35')+1/k, (mpf('0.65')-1/k)**(-mpf(3)/2), k**(-mpf(1)/2))
print("product of quoted", mpf('8.57143')*mpf('1.35050')*mpf('1.91044')*mpf('0.022356'))
ub=mpf('1.15')/mpf('0.35')*(2+1/k)*(mpf('0.65')-1/k)**(-mpf(3)/2)*k**(-mpf(1)/2)
print("u_flat(2001)=",ub, mpf('3.28572')*mpf('2.00050')*mpf('1.91044')*mpf('0.022356'))
print("9*(3/2)^1.5=",9*mpf(1.5)**mpf(1.5), "x4/3", 9*mpf(1.5)**mpf(1.5)*4/3, "16.54*4/3", mpf('16.54')*4/3)
print("(4002)^(2/3)",mpf(4002)**(mpf(2)/3), "0.65*2001-1", mpf('0.65')*2001-1)
print("(1.35*2001)", mpf('1.35')*2001)
# witness bound at n=20000
n=mpf(20000); print("witness bound", mpf('1.99')+mpf('0.59963')*(n+1)**(mpf(2)/3)+mpf('1.24847')*(n+1)**(mpf(1)/3))
