import sys,io,math
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8')
def pos(n): return n-2-math.ceil((n-1)/2)   # (n-1)/2<=l<=n-3
def pairs(n): return n-1-math.ceil((n-1)/2) # ceil((n-1)/2)<=l<=n-2
print('QR positions 5..20000', sum(pos(n) for n in range(5,20001)), 'pairs', sum(pairs(n) for n in range(5,20001)))
print('QR positions 20001..50000', sum(pos(n) for n in range(20001,50001)), 'pairs', sum(pairs(n) for n in range(20001,50001)))
print('positions 5..2000', sum(pos(n) for n in range(5,2001)))
B=lambda k: -(-k*k//4)
print('col direct 161..500', sum(2*B(k)-2*k for k in range(161,501)), 'ratio', sum(B(k)+1 for k in range(161,501)))
print('col direct 121..160', sum(2*B(k)-2*k for k in range(121,161)), 'ratio', sum(B(k)+1 for k in range(121,161)))
print('rows 50..20000',20000-49,' 901..20000',20000-900,' 50..900',900-49)
print('2B<10000 for k<=', max(k for k in range(121,501) if 2*B(k)<10000))
print('max m>=171 with m^1.5+9m<=20001:', max(m for m in range(171,3000) if m**3<=(20001-9*m)**2))
