# M13 item D.band102-integer: recount (ㄱ) cases and minimum, (ㅁ) comparison counts.
from fractions import Fraction as F
k=10000
def exbar(q):
    pi=F(q*(q-1),2*(k+1)); return q+(k+q)*pi/(1-pi)
cnt_unord=0; cnt_ord=0; best=None
for q in range(1,50):
    for qp in range(1,50):
        for j in range(0,51):
            if q+qp+j>50: continue
            cnt_ord+=1
            if q<=qp: cnt_unord+=1
            val=1-F(j,k)*(exbar(q)+exbar(qp))-(exbar(q)*(qp-1)+exbar(qp)*(q-1))/(2*k)
            if best is None or val<best[0]: best=(val,(q,qp,j))
print('unordered',cnt_unord,'ordered',cnt_ord,'min',float(best[0]),best[1], 'all positive', best[0]>0)
# (ㅁ) counts
r1=sum((2*k+19)-20001+1 for k in range(9991,10000) if 2*k+19>=20001)
r2=sum((2*k+40)-max(20001,2*k+1)+1 for k in range(9981,11100))
r3=sum(58-max(41,20001-2*k)+1 for k in range(9972,12000) if 58>=max(41,20001-2*k))
r4=sum(102-max(59,max(41,20001-2*k))+1 for k in range(9950,12000) if 102>=max(59,20001-2*k))
r5=1000*44; r6=1000*23; r7=1000*7
print('run1',r1,'run2',r2,'cols',11100-9981,'run3',r3,'cols',12000-9972,'run4',r4,'cols',12000-9950,'r5-7',r5,r6,r7,'sum3-7',r3+r4+r5+r6+r7,'cols3-7',2028+2050+3000)
for a,b in [(9981,10353),(10354,10726),(10727,11099)]:
    print(a,b,sum((2*k+40)-max(20001,2*k+1)+1 for k in range(a,b+1)))
# overflow
print(30102//2+1<2**14, 2*14999<2**15)
# chunk check for (나): k from 9950: 2k+41 = 19941 <20001 so n starts 20001 -> nu=20001-2k=101 for k=9950
print('k=9950 nu range', max(2*9950+41,20001)-2*9950, 'to 102')
