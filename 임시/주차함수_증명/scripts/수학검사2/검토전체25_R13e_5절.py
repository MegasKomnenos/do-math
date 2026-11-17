# -*- coding: utf-8 -*-
# 장부 5절의 둘째 열(장이 처음 정의하는 전역 기호)과 넷째 열(여유 글자)을 1.1·1.2·6절 규칙으로 다시 계산해 견준다.
import sys, io, re, importlib.util
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', newline='\n')
spec = importlib.util.spec_from_file_location('t12', 'scripts/수학검사2/검토전체25_R13e_표12.py')
t12 = importlib.util.module_from_spec(spec); spec.loader.exec_module(t12)
BS = chr(92)
g = [(ln,c) for ln,c in t12.table(49,288)]
def chap_of_sec(s):
    m = re.match(r'\s*(\d+)\.', s)
    return int(m.group(1)) if m else None
def chapters(s):
    return set(int(x) for x in re.findall(r'\d+', s.split('(')[0]))
rows12=[]
for ln,c in g:
    letter, bf, mean, defsec, used = c[0], c[1], c[2], c[3], c[4]
    base, font = bf.split('·',1)
    font = font.split('(')[0].strip() if not font.startswith('일반') else '이탤릭'
    rows12.append(dict(ln=ln, letter=letter, base=base.strip(), font=font, defch=chap_of_sec(defsec), defsec=defsec, used=chapters(used), usedraw=used))
# --- 둘째 열
sec5 = t12.table(1191,1200)
print('== 5절 둘째 열 대 1.2 정의 절의 장 ==')
for ln,c in sec5:
    ch = int(c[0])
    listed = [x.strip() for x in c[1].split(';')] if c[1].strip()!='없음' else []
    expect = [r['letter'] for r in rows12 if r['defch']==ch]
    a=set(listed); b=set(expect)
    print('장',ch,'5절',len(listed),'1.2',len(expect),'5절에만:',sorted(a-b),'1.2에만:',sorted(b-a), '순서같음' if listed==expect else '순서다름')
# --- 넷째 열
def parse_spare(cell):
    out=set()
    for part in re.split(r'\.\s+(?=[가-힣])', cell):
        for tok in re.findall(r'\$([^$]+)\$', part):
            tok=tok.strip()
            m = re.match(r'^'+re.escape(BS)+r'math(cal|frak|sf)\s+(\w)$', tok)
            if m:
                out.add(({'cal':'필기체','frak':'프락투어','sf':'산세리프'}[m.group(1)], m.group(2)))
            else:
                out.add(('이탤릭', tok))
    return out
lat_l = list('abcdefghijklmnopqrstuvwxyz'); lat_u=list('ABCDEFGHIJKLMNOPQRSTUVWXYZ')
gr = [BS+x for x in 'alpha beta gamma delta epsilon varepsilon zeta eta theta vartheta iota kappa varkappa lambda mu nu xi pi varpi rho varrho sigma varsigma tau upsilon phi varphi chi psi omega Gamma Delta Theta Lambda Xi Pi Sigma Upsilon Phi Psi Omega'.split()]
universe = set(('이탤릭',x) for x in lat_l+lat_u+gr) | set(('필기체',x) for x in lat_u) | set(('프락투어',x) for x in lat_l+lat_u) | set(('산세리프',x) for x in lat_l+lat_u)
ell = BS+'ell'
var11 = ['n','m','t','N','k',ell,'y','Y','i','j','u','v','r',BS+'nu','d','q']
reserved = ['a','b','c','e','h',BS+'delta',BS+'Delta',BS+'Sigma','l','o','O',BS+'varpi','P','Q','W','X','x','d']
print('== 5절 넷째 열 대 규칙 재계산 ==')
for ln,c in sec5:
    ch=int(c[0])
    spare = parse_spare(c[3])
    blocked = {}
    for r in rows12:
        key=(r['font'], r['base'])
        if ch in r['used'] or r['defch']==ch:
            blocked.setdefault(key,[]).append('1.2 %d행 %s (쓰이는 장)'%(r['ln'],r['letter']))
        if r['defch']==1:
            blocked.setdefault(key,[]).append('1.2 %d행 %s (1장 정의)'%(r['ln'],r['letter']))
    for x in var11: blocked.setdefault(('이탤릭',x),[]).append('1.1 변수')
    for x in reserved: blocked.setdefault(('이탤릭',x),[]).append('6절 예약')
    expect = set(k for k in universe if k not in blocked)
    extra = sorted(spare-expect); missing = sorted(expect-spare)
    print('장',ch,'여유',len(spare),'재계산',len(expect))
    for k in extra: print('   여유에 있으나 막혀야 함:',k, blocked.get(k,'(우주 밖)'))
    for k in missing: print('   여유에 없으나 막을 까닭을 못 찾음:',k)
