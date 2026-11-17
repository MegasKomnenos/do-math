# -*- coding: utf-8 -*-
# 7절 머리말의 계약(1.2 「기록의 글자」 열의 기록 집합 = 7절 표의 기록 집합)을 1.2 행 단위로 본다.
# 7절 토큰을 (글자체, 바탕, 위첨자, 아래첨자 항 수)로 1.2 행에 맞춘다. 맞출 행이 여럿이면 넓게(모두) 잡는다.
# 여러 글자 × 여러 기록 묶음 행은 짝을 넓게 잡으므로 (나) 후보는 원문 행을 읽어 확인한다. 「글자 없음」 칸의 토큰은 (나)에서 뺀다.
import sys, io, re, importlib.util
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', newline='\n')
spec = importlib.util.spec_from_file_location('t12','scripts/수학검사2/검토전체25_R13e_표12.py')
t12 = importlib.util.module_from_spec(spec); spec.loader.exec_module(t12)
BS=chr(92)
GREEK='alpha beta gamma delta epsilon varepsilon zeta eta theta vartheta iota kappa varkappa lambda mu nu xi pi varpi rho varrho sigma varsigma tau upsilon phi varphi chi psi omega Gamma Delta Theta Lambda Xi Pi Sigma Upsilon Phi Psi Omega ell'.split()
def grp(s,i):
    # s[i]부터 한 항(중괄호 묶음, \명령, 한 글자)을 읽어 (내용, 다음 위치)
    if i>=len(s): return '',i
    if s[i]=='{':
        d=0
        for j in range(i,len(s)):
            if s[j]=='{': d+=1
            elif s[j]=='}':
                d-=1
                if d==0: return s[i+1:j], j+1
        return s[i+1:],len(s)
    if s[i]==BS:
        m=re.match(re.escape(BS)+r'[A-Za-z]+', s[i:])
        if m:
            j=i+m.end()
            if m.group(0) in (BS+'mathrm',BS+'mathsf',BS+'mathcal',BS+'mathfrak'):
                while j<len(s) and s[j]==' ': j+=1
                inner,j2=grp(s,j); return inner,j2
            return m.group(0), j
    return s[i], i+1
def sig(tok):
    t=tok.strip()
    t=re.sub(r'^(-|e\s*'+re.escape(BS)+r',\s*|'+re.escape(BS)+r'(widehat|hat|tilde|bar)\s*)','',t)
    font=None; base=None; i=0
    m=re.match(re.escape(BS)+r'(mathrm|operatorname)\s*\{([A-Za-z0-9]+)\}', t)
    if m: font,base,i='로마체',m.group(2),m.end()
    if base is None:
        m=re.match(re.escape(BS)+r'math(cal|frak|sf|bb)\s*(?:\{([A-Za-z]+)\}|\s*([A-Za-z]))', t)
        if m: font,base,i={'cal':'필기체','frak':'프락투어','sf':'산세리프','bb':'칠판체'}[m.group(1)], m.group(2) or m.group(3), m.end()
    if base is None:
        m=re.match(re.escape(BS)+r'Pr(?![A-Za-z])', t)
        if m: font,base,i='칠판체','Pr',m.end()
    if base is None:
        m=re.match(re.escape(BS)+r'([A-Za-z]+)', t)
        if m and m.group(1) in GREEK: font,base,i='이탤릭',BS+m.group(1),m.end()
    if base is None:
        m=re.match(r'([A-Za-z])', t)
        if m: font,base,i='이탤릭',m.group(1),m.end()
    if base is None: return None
    sup=''; sub=None
    while i<len(t) and t[i] in "^_' ":
        if t[i]==' ': i+=1; continue
        if t[i]=="'": sup+="prime"; i+=1; continue
        op=t[i]; inner,i=grp(t,i+1)
        inner=inner.replace(BS+'prime','prime').replace(BS+'mathrm','').replace('{','').replace('}','').replace(' ','')
        if op=='^': sup+=inner
        else: sub=inner
    nsub = 0 if sub is None else len([x for x in re.split(r',',sub) if x!=''])
    return (font,base,sup,nsub)
def variants(cell):
    out=[]
    for tok in re.findall(r'\$([^$]+)\$', cell):
        depth=0; cur=''
        for ch in tok:
            if ch in '({[': depth+=1
            if ch in ')}]': depth-=1
            if ch==',' and depth==0: out.append(cur); cur=''
            else: cur+=ch
        out.append(cur)
    return [v.strip() for v in out if v.strip()]
def recs(cell): return set(re.findall(r'\[(r[0-9a-f]{7})\]', cell))
rows12=[(ln,c) for ln,c in t12.table(49,288)]
S12=[]  # (ln, letter, [sigs], recs)
for ln,c in rows12:
    S12.append((ln,c[0],[sig(v) for v in variants(c[0]) if sig(v)],recs(c[6]),c[6]))
def match(s):
    cand=[r for r in S12 if any(x[0]==s[0] and x[1]==s[1] for x in r[2])]
    if len(cand)<=1: return cand,'유일'
    c2=[r for r in cand if any(x[:3]==s[:3] for x in r[2])]
    if len(c2)==1: return c2,'위첨자'
    if len(c2)>1:
        c3=[r for r in c2 if any(x==s for x in r[2])]
        if len(c3)==1: return c3,'아래첨자'
        return (c3 or c2),'여럿'
    return cand,'여럿(위첨자 불일치)'
rows7=t12.table(1243,1441)
have={}   # 1.2 ln -> {record: [7절 행]}
pairs=[]
for ln,c in rows7:
    rr=recs(c[1]); nolet = '글자 없음' in c[0]
    for v in variants(c[0]):
        s=sig(v)
        if not s: continue
        cand,how=match(s)
        for r in cand:
            for x in rr: have.setdefault(r[0],{}).setdefault(x,[]).append(ln)
        pairs.append((ln,v,s,cand,how,rr,nolet))
mode=sys.argv[1] if len(sys.argv)>1 else 'a'
if mode=='a':
    for ln,letter,sigs,rs,raw in S12:
        miss=sorted(x for x in rs if x not in have.get(ln,{}))
        if miss: print('(가) 1.2 %d행 %s: 기록 %s — 7절의 그 글자 행에 없음 | 1.2 칸: %s'%(ln,letter,miss,raw[:260]))
elif mode=='b':
    seen=set()
    for ln,v,s,cand,how,rr,nolet in pairs:
        if nolet or not cand: continue
        allr=set()
        for r in cand: allr|=r[3]
        miss=sorted(rr-allr)
        if miss:
            key=(ln,v)
            if key in seen: continue
            seen.add(key)
            print('(나) 7절 %d행 $%s$ → 1.2 %s행(%s): 7절의 기록 %s 이 1.2 칸에 없음%s'%(ln,v[:36],','.join(str(r[0]) for r in cand),how,miss,' [묶음 행: 짝 확인 필요]' if len(rr)>1 and len(variants(rows7[[x[0] for x in rows7].index(ln)][1][0]))>1 else ''))
