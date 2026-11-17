from mpmath import mp, mpf, sqrt, exp, e, log, quad
mp.dps=20
X=(5-sqrt(7))/6
print("X*",X,"max",X*(1-X)*(3-2*X),"(10+7sqrt7)/54",(10+7*sqrt(7))/54)
print("u bound", mpf('1.0443')*mpf('1.0150')*mpf('1.01961')*mpf(4)/3, "e^(1/24+1/612)",exp(mpf(1)/24+mpf(1)/612), "tl^-1",1/(1-mpf(3)/(4*51)))
print("L/G V>=2:", mpf(1.5)/53*(mpf(4)/3)*mpf(0.5)*mpf('1.01961')*mpf('1.0150'))
print("L/G V=1:", mpf(1.5)/52*mpf('2.02')*mpf('0.51')*mpf('1.01961')*mpf('1.0150'))
print("e^{3/102}",exp(mpf(3)/102), "1.545/e",mpf('1.545')/e, "e^-2",exp(-2))
print("2e^-2+e^-1-1.03e^-2/51",2*exp(-2)+exp(-1)-mpf('1.03')*exp(-2)/51, "0.6*52/53", mpf('0.6')*52/53)
print("0.12/e",mpf('0.12')/e)
y=50
print("ratio at y=50", mpf('0.0441')*(y-1)*(y+3)**-2 / (mpf('1.2')*(y+1)/((y+2)**2*(y+3))))
print("1.03e^-1/2", mpf('1.03')*exp(-1)/2)
# I_5 closed form check
Xv=mpf('0.3')
print(quad(lambda v: v**(-mpf(1)/2)*(1-v)**(-mpf(5)/2),[0,Xv]), mpf(2)/3*Xv**mpf(0.5)*(1-Xv)**(-mpf(1.5))+mpf(4)/3*Xv**mpf(0.5)*(1-Xv)**(-mpf(0.5)))
