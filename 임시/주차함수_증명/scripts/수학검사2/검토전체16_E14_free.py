# -*- coding: utf-8 -*-
"""E14: 장부 1.2(쓰이는 장)·1.1·6절에서 장별 여유 글자를 다시 셈해 5절 표와 견준다."""
import re, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
ROOT = r"C:/math/임시/주차함수_증명"
lines = open(f"{ROOT}/장부_v2.md", encoding='utf-8').read().split("\n")
s = next(i for i,l in enumerate(lines) if l.startswith("### 1.2"))
e = next(i for i,l in enumerate(lines) if l.startswith("### 1.3"))
greek = {'alpha','beta','gamma','delta','epsilon','varepsilon','zeta','eta','theta','vartheta','iota','kappa','varkappa','lambda','mu','nu','xi','pi','rho','varrho','sigma','varsigma','tau','upsilon','phi','varphi','chi','psi','omega','Gamma','Delta','Theta','Lambda','Xi','Pi','Sigma','Upsilon','Phi','Psi','Omega','varpi','ell'}
used = {c:set() for c in range(1,12)}
BS = chr(92)
for l in lines[s:e]:
    if not l.startswith("| $"): continue
    cells=[c.strip() for c in l.strip().strip("|").split("|")]
    if len(cells)!=7: print("CELLS",len(cells),l[:50]); continue
    latex, basefont, meaning, defsec, chs, old, rec = cells
    parts = basefont.split('·')
    base = parts[0].lstrip(BS)
    font = parts[1] if len(parts)>1 else ''
    if font.startswith('일반'):
        f = 'greek' if base in greek else ('lower' if base.islower() else 'upper')
    elif font.startswith('필기체'): f='cal'
    elif font.startswith('프락투어'): f='frak'
    elif font.startswith('산세리프'): f='sf'
    else: f='other'
    if chs=='전 장': chset=set(range(1,12))
    else: chset=set(int(x) for x in re.findall(r'\d+', chs))
    if defsec.startswith('1.'): chset|=set(range(1,12))
    for c in chset: used[c].add((f,base))
for v in ['n','m','t','N','k','y','Y','i','j','u','v','r','d','q']:
    f='lower' if v.islower() else 'upper'
    for c in range(1,12): used[c].add((f,v))
for c in range(1,12): used[c].add(('greek','ell')); used[c].add(('greek','nu'))
for v in ['a','b','c','e','h','l','o','d','x']:
    for c in range(1,12): used[c].add(('lower',v))
for v in ['O','P','Q','W','X']:
    for c in range(1,12): used[c].add(('upper',v))
for v in ['delta','Delta','Sigma','varpi']:
    for c in range(1,12): used[c].add(('greek',v))
s5 = next(i for i,l in enumerate(lines) if l.startswith("## 5."))
e5 = next(i for i,l in enumerate(lines) if l.startswith("## 6."))
lower_all=set('abcdefghijklmnopqrstuvwxyz'); upper_all=set('ABCDEFGHIJKLMNOPQRSTUVWXYZ')
greek_all = greek - {'ell','nu','varpi','Delta','Sigma','delta'}
for l in lines[s5:e5]:
    m = re.match(r'\| (\d+) \|', l)
    if not m: continue
    c=int(m.group(1))
    cells=[x.strip() for x in l.strip().strip("|").split("|")]
    free_txt = cells[3]
    chunks = re.split(r'\. (?=라틴|그리스|필기체|프락투어|산세리프)', free_txt)
    lst={'lower':set(),'upper':set(),'greek':set(),'cal':set(),'frak':set(),'sf':set()}
    for ch in chunks:
        if ch.startswith('라틴 소문자'): lst['lower']=set(re.findall(r'\$([a-z])\$', ch))
        elif ch.startswith('라틴 대문자'): lst['upper']=set(re.findall(r'\$([A-Z])\$', ch))
        elif ch.startswith('그리스'): lst['greek']=set(re.findall(re.escape(BS)+r'([a-zA-Z]+)', ch))
        elif ch.startswith('필기체'): lst['cal']=set(re.findall(re.escape(BS)+r'mathcal ([A-Z])', ch))
        elif ch.startswith('프락투어'): lst['frak']=set(re.findall(re.escape(BS)+r'mathfrak ([a-zA-Z])', ch))
        elif ch.startswith('산세리프'): lst['sf']=set(re.findall(re.escape(BS)+r'mathsf ([a-zA-Z])', ch))
    exp={}
    exp['lower']= lower_all - {b for f,b in used[c] if f=='lower'}
    exp['upper']= upper_all - {b for f,b in used[c] if f=='upper'}
    exp['greek']= greek_all - {b for f,b in used[c] if f=='greek'}
    exp['cal']= upper_all - {b for f,b in used[c] if f=='cal'}
    exp['frak']= (lower_all|upper_all) - {b for f,b in used[c] if f=='frak'}
    exp['sf']= (lower_all|upper_all) - {b for f,b in used[c] if f=='sf'} - {'P','Q','W','X','V','B'}
    print(f"== 장 {c}")
    for f in ['lower','upper','greek','cal','frak','sf']:
        extra = sorted(lst[f]-exp[f]); missing = sorted(exp[f]-lst[f])
        if extra or missing:
            print(f"  {f}: 표에 있으나 셈으로는 여유 아님: {extra} | 셈으로는 여유인데 표에 없음: {missing}")
