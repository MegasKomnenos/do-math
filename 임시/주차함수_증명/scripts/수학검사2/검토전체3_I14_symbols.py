# -*- coding: utf-8 -*-
"""I14: 장부 1.2의 「쓰이는 장」 열을 장 파일의 실제 출현과 대조한다(자리 찾기용)."""
import re, sys, io, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
ROOT = r"C:/math/임시/주차함수_증명"
files = {'1':['장1'],'2':['장2'],'3':['장3'],'4':['장4'],'5':['장5A','장5B'],'6':['장6'],'7':['장7A','장7B'],'8':['장8'],'9':['장9'],'10':['장10'],'11':['장11']}
text = {c:'\n'.join(open(os.path.join(ROOT,'장v2',f+'.md'),encoding='utf-8').read() for f in fs) for c,fs in files.items()}
dtext = {}
for c,fs in files.items():
    s=''
    for f in fs:
        p=os.path.join(ROOT,'장v2','부록D_'+f+'.md')
        if os.path.exists(p): s+=open(p,encoding='utf-8').read()
    dtext[c]=s
lines = open(os.path.join(ROOT,'장부_v2.md'),encoding='utf-8').read().split('\n')
rows=[]
for i,l in enumerate(lines[48:341],49):  # 1.2 표 본문
    if not l.startswith('| $') and not l.startswith('| $('):
        continue
    cells=[c.strip() for c in l.strip().strip('|').split(' | ')]
    if len(cells)<7:
        print("CELLS?", i, len(cells), l[:80]); continue
    rows.append((i,cells))
BS = chr(92)
def stem_regex(g):
    g=g.strip().strip('$').strip()
    if g.startswith('('+BS+'mathrm G)_d'): return BS+'('+BS+BS+'mathrm G'+BS+')_d', False
    if g.startswith('('+BS+'star)'): return BS+'('+BS+BS+'star'+BS+')', False
    m=re.match(r'^(\\(?:mathcal|mathfrak|mathsf|mathrm|mathbb|bar|hat|tilde)\s*(?:\{[^}]*\}|[A-Za-z]))',g)
    if m:
        stem=m.group(1); rest=g[len(stem):]
    else:
        m=re.match(r'^(\\[A-Za-z]+|[A-Za-z])',g)
        if not m: return None, True
        stem=m.group(1); rest=g[len(stem):]
    sub=re.match(r'^(\^|_)(\\[A-Za-z]+|\{[^{}]*\}|[A-Za-z0-9])',rest)
    pat=re.escape(stem)
    manual=False
    if sub:
        pat+=re.escape(sub.group(1))+r'\{?'+re.escape(sub.group(2).strip('{}'))+r'\}?'
    else:
        if re.fullmatch(r'[A-Za-z]',stem): manual=True
        if stem.startswith(BS) and not stem.endswith('}'): pat+=r'(?![A-Za-z])'
        elif re.fullmatch(r'[A-Za-z]',stem): pat+=r'(?![A-Za-z_^])'
    return pat, manual
out=[]
for i,cells in rows:
    glyphs=[g for g in re.findall(r'\$([^$]+)\$',cells[0])]
    listed=cells[4]
    if listed.strip()=='전 장': lset=set(files.keys())
    else: lset=set(x.strip() for x in listed.split(',') if x.strip().isdigit())
    found=set(); patterns=[]; manual=False
    for gl in glyphs:
        for g in re.split(r',\s*(?=[\\A-Za-z(])',gl):
            pat,man=stem_regex(g)
            if pat is None: manual=True; continue
            manual = manual or man
            patterns.append(pat)
            for c,t in text.items():
                if re.search(pat,t): found.add(c)
    dfound={c for c,t in dtext.items() if any(re.search(p,t) for p in patterns)}
    def key(s): return sorted(s,key=int)
    if found!=lset or manual:
        out.append(f"행{i} {cells[0][:60]} | 장부: {','.join(key(lset))} | 발견: {','.join(key(found))} | 장부만: {','.join(key(lset-found))} | 발견만: {','.join(key(found-lset))} | D: {','.join(key(dfound))} | pat={patterns}{' [수동]' if manual else ''}")
print(len(rows),"rows;",len(out),"diffs")
print('\n'.join(out))
