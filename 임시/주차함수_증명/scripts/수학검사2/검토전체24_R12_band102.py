# R12: D.band102-integer (가) 결과 줄 대조 (읽기 전용)
import re,glob,os,sys
B=r"C:/math/임시/주차함수_증명/원고_자료"
def parse(f):
    out={}
    for line in open(f,encoding='utf-8',errors='replace'):
        m=re.match(r'nu=\+?(-?\d+): (?:lam=([\d.]+) )?.*margin=(-?[\d.]+)',line)
        if m: out[int(m.group(1))]=(m.group(2),float(m.group(3)))
    return out
p=parse(B+'/r475ada3/audit_param_K11100_nu20_40.txt')
print('K11100', [(nu,)+p[nu] for nu in sorted(p)])
tab={12000:58,13000:79,14000:99,15000:102,20000:115,30000:132,50000:164,100000:228,200000:298,500000:435,1000000:590}
tot=0; neg=[]
for K,nm in tab.items():
    f=B+'/r6b37c7e/evidence/peer/audit_rerun/rerun_audit_K%d.txt'%K
    p=parse(f)
    if K==14000:
        p.update(parse(B+'/r6b37c7e/evidence/peer/audit_rerun/rerun_audit_K14000_nu97_100.txt'))
    nus=sorted(p)
    tot+=len(nus)
    neg+=[(K,nu,p[nu][1]) for nu in nus if p[nu][1]<0]
    lam=sorted(set(p[nu][0] for nu in nus if nu<=nm))
    print(K,nm,'range',nus[0],nus[-1],'n',len(nus),'m41',p[41][1],'mmax',p[nm][1],'next',p.get(nm+1),'lam',lam, 'minpos', min(p[nu][1] for nu in nus if nu<=nm))
print('total',tot,'neg',neg)
print(sum(nm+1-41+1 for nm in tab.values()), sum(nm+1-41+1 for nm in tab.values())+ (100-96))
