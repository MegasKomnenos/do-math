from math import gamma
from fractions import Fraction as Fr
from decimal import Decimal as D, getcontext
getcontext().prec=40
a0 = 3**(-2/3)*gamma(1/3); a1 = 3**(-1/3)*gamma(2/3)
print('a0',repr(a0),'a1',repr(a1))
# (나) k>=30000, omega=699/100, a0<3/2, a1<1
w=Fr(699,100)
val = w - Fr(7,2) - (4*w+Fr(1,2))*Fr(3,2)/31 - Fr(13,2)*w/961 - 12*w/30000
print('(나) exact', val, float(val), 'claimed 495594511/240250000 =', Fr(495594511,240250000), float(Fr(495594511,240250000)), 'equal?', val==Fr(495594511,240250000))
# (다) k=10000, omega=698/100 with a0<1.2879, a1<0.939, k^{-1/3}, k^{-2/3} exact floats
w=D('6.98'); k=D(10000)
k13 = D(1)/k**(D(1)/3); k23 = D(1)/k**(D(2)/3)
val2 = w - D('3.5') - (4*w+D('0.5'))*D('1.2879')*k13 - D(13)/2*w*D('0.939')*k23 - 12*w/k
print('(다) with stated bounds:', val2, 'k^-1/3', k13, 'k^-2/3', k23)
# with rational k^{-1/3} <= 1/21.54 ? check 21.54^3
print('21.54^3', 21.54**3, '21.544^3', 21.544**3, '464.1^(3/2)', 464.1**1.5, '464.15^1.5', 464.15**1.5)
