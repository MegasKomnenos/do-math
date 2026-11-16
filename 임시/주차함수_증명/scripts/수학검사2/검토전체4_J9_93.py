# 9.3절 수치 검산 (J9): 정리 old-7-16 증명 (2)(3)의 상수
from mpmath import mp, mpf, sqrt, exp, pi, ceil, floor
mp.dps = 25
k = mpf(6668)
print("(2) 0.3826 check:", exp(-mpf(1)/24)*exp(-mpf(1)/(12*3334))/sqrt(2*pi))
jstar = ceil((3*k)**(mpf(2)/3)); print("j* =", jstar)
print("first interval LHS 4.85[...]:", mpf('4.85')*(sqrt(k)/sqrt((3*k)**(mpf(2)/3)+2)-sqrt(2)), " 6.62*0.734=", mpf('6.62')*mpf('0.734'))
print("second: 6.1224*0.95^{-3/2} =", mpf('6.1224')*mpf('0.95')**(-mpf(3)/2))
# third interval endpoints
iota1 = mpf('0.05')*k
f = lambda i: mpf('16.35')*((k+1)/(k-i))**(mpf(3)/2)/i
print("third, iota=0.05k:", f(iota1), " 353.2/k=", mpf('353.2')/k, " 6.62/sqrt k=", mpf('6.62')/sqrt(k), " 327*0.95^-1.5*(1+1/k)^1.5=", 327*mpf('0.95')**(-1.5)*(1+1/k)**1.5)
iota2 = k-jstar-1
print("third, iota=k-j*-1:", f(iota2), " formula:", mpf('5.45')*k**(-mpf(1)/2)*(1+1/k)**(mpf(3)/2)*k/(k-jstar-1))
# (3)
d = mpf('6.62')/sqrt(k)
print("41.2 check:", 103/sqrt(2*pi)*exp(1/(12*(2*k-1))))
print("3.394 check:", exp(1/(12*(2*k-1)))/sqrt(2*pi)*(2*k/(mpf('0.48')*k**2))**(mpf(3)/2)*k**(mpf(3)/2))
print("pi0 bound: (0.26k+0.5)*3.394k^-1.5+0.676/k vs 0.8825k^-1/2+0.72/k:", (mpf('0.26')*k+mpf('0.5'))*mpf('3.394')*k**(-1.5)+mpf('0.676')/k, mpf('0.8825')/sqrt(k)+mpf('0.72')/k)
bulk = 1+(1+1/mpf('1.48'))*d/(2-d)+(1/mpf('1.48'))*(mpf('0.8825')/sqrt(k)+mpf('0.72')/k+mpf('41.2')*(2/(mpf('0.48')*k-102))**(mpf(3)/2))
band = (1+d/2)/(1-d/2)
print("bulk need:", bulk, " band need:", band)
# 9.2: pi_2 bound
print("sqrt(8/(pi*6669)) =", sqrt(8/(pi*6669)))
