# 검토전체25 R9: 명제 9:old-8-33(ii)·9:old-8-35(나)·보조정리 bulk-majorants의 단조성을 k 격자 표본에서 대조(증명은 본문의 해석적 논증; 여기서는 반례가 없는지만 본다)
import io, re
src = io.open('scripts/수학검사2/검토전체25_R9_가족표.py', encoding='utf-8').read()
src = src[:src.index('print("== 벌크 k0=6668")')].replace('mp.dps = 30', 'mp.dps = 20')
exec(src)
def grid(k0, kmax, n):
    ks = sorted(set([k0+i for i in range(0, 40)]+[int(k0*(kmax/k0)**(i/n)) for i in range(n+1)]))
    return ks
def mono(name, f, ks, sign):
    v = [f(k) for k in ks]
    bad = [(ks[i], ks[i+1]) for i in range(len(ks)-1) if sign*(v[i+1]-v[i]) < 0]
    print("%-34s %s (%d점, 첫값 %s, 끝값 %s)%s" % (name, "증가" if sign > 0 else "감소", len(ks), mp.nstr(v[0], 8), mp.nstr(v[-1], 8), "" if not bad else "  반례: %s" % bad[:3]))
o1a = lambda k: 2-ec(k, mpf('1.3')*t23(k))-BdT(k, mpf('1.3')*t23(k))-DDL(k)
def o1b(k):
    xs2 = 2*t23(k)/(k-1)
    return 4-3*sup(mpf('1.3')*t23(k)+1, k+1)+(2*exp(-xs2)-1)*exp(-xs2)-BdT(k, 2*t23(k))-DDL(k)
o2 = lambda k: 4-3*sup(2*t23(k)+1, k+1)+(2*exp(mpf('-0.48'))-1)*exp(mpf('-0.48'))-BdT(k, mpf('0.48')*k)-DDL(k)
mono("o_F(1a)", o1a, grid(9705, 10**7, 40), +1)
mono("o_F(1b)", o1b, grid(9551, 10**7, 40), +1)
mono("o_F(2)", o2, grid(8065, 10**7, 40), +1)
mono("o_F(벌크)=4-ebar", lambda k: 4-ebar(k), grid(6668, 10**7, 40), +1)
mono("Stays^up(k;1.3k^(2/3))", lambda k: StaysUp(k, mpf('1.3')*t23(k)), grid(6667, 10**7, 30), -1)
mono("Stays^up(k;2k^(2/3))", lambda k: StaysUp(k, 2*t23(k)), grid(6667, 10**7, 30), -1)
mono("Stays^up(k;0.48k)", lambda k: StaysUp(k, mpf('0.48')*k), grid(6667, 10**7, 30), -1)
mono("abar+bbar+DDL+dbar", lambda k: abar(k)+bbar(k)+DDL(k)+dbar(k), grid(6667, 10**7, 40), -1)
