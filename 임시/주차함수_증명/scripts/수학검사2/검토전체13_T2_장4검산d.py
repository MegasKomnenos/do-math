from fractions import Fraction as Fr
import mpmath as mp
mp.mp.dps=30
a0=mp.quad(lambda w: mp.e**(-w**3/3),[0,mp.inf]); a1=mp.quad(lambda w: w*mp.e**(-w**3/3),[0,mp.inf])
print("a0",a0,"a1",a1, "1.287899<a0<1.2879:",1.287899<a0<1.2879, "0.938892<a1<0.939:",0.938892<a1<0.939)
w=Fr(699,100)
val=w-Fr(7,2)-(6*w+Fr(3,4))/31-(13*w/2)/961-12*w/30000
print("(na)",val,float(val),val==Fr(495594511,240250000))
# (da): omega=6.98, k^{-1/3}<=0.0464159, a0<1.2879,a1<0.939
w=Fr(698,100); c13=Fr('0.0464159'); A0=Fr('1.2879'); A1=Fr('0.939')
val=w-Fr(7,2)-(4*w+Fr(1,2))*A0*c13-(13*w/2)*A1*c13**2-12*w/10000
print("(da)",float(val),val>=Fr('1.6809'))
# with exact k^{-1/3}=10000^{-1/3}
c=mp.mpf(10000)**(-mp.mpf(1)/3); print("k^-1/3",c, "<=0.0464159",c<=0.0464159)
val2=mp.mpf('6.98')-3.5-(4*mp.mpf('6.98')+0.5)*mp.mpf('1.2879')*c-(13*mp.mpf('6.98')/2)*mp.mpf('0.939')*c**2-12*mp.mpf('6.98')/10000
print("(da) exact c:",val2)
