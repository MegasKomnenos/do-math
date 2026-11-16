import re,io,glob,os
root=r'C:\math\임시\주차함수_증명'
order=['장1','장2','장3','장4','장5A','장5B','장6','장7A','장7B','장8','장9','장10']
chap={}
for f in order:
    sec='';L=[]
    for i,l in enumerate(io.open(root+r'\장v2\%s.md'%f,encoding='utf-8'),1):
        m=re.match(r'### (\d+\.\d+)',l)
        if m: sec=m.group(1)
        L.append((i,sec,l))
    chap[f]=L
A=io.open(root+r'\장v2\부록A.md',encoding='utf-8').read().split('\n')
out=io.open(root+r'\scripts\수학검사2\_K11_부록A절대조_out.txt','w',encoding='utf-8')
n=0
for ln,l in enumerate(A,1):
    if not l.startswith('| $'): continue
    c=[x.strip() for x in l.strip().strip('|').split(' | ')]
    if len(c)<3: continue
    sym=c[0]; sec=c[2]
    m=re.search(r'\$([^$]+)\$',sym)
    if not m: continue
    s=m.group(1)
    # key: first macro with braces or multi-letter name
    keys=re.findall(r'[\](?:mathrm|mathsf|mathcal|mathfrak|mathbb|mathscr|operatorname|text)\{[^}]+\}',s)
    if not keys:
        keys=re.findall(r'[\][A-Za-z]{3,}(?:_\{[^}]*\}|_[A-Za-z0-9])?',s)
    if not keys: continue
    key=keys[0]
    # find first occurrence in chapters
    found=None
    for f in order:
        for i,sc,line in chap[f]:
            if key in line: found=(f,i,sc); break
        if found: break
    secs=re.findall(r'\d+\.\d+',sec)
    ok = found and found[2] in secs
    if not ok:
        n+=1
        out.write('A L%d %s | key=%s | A says %s | first found %s\n'%(ln,sym[:50],key,sec[:40],found))
out.write('mismatches: %d\n'%n)
out.close()
