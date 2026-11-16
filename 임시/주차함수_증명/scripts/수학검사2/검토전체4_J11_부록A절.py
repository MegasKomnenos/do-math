import re, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
chap=['1','2','3','4','5A','5B','6','7A','7B','8','9','10']
texts={}
for c in chap:
    sec=''
    L=[]
    for line in open(f'장v2/장{c}.md',encoding='utf-8'):
        m=re.match(r'^###\s+(\d+\.\d+)',line)
        if m: sec=m.group(1)
        elif re.match(r'^## ',line): sec=c+'.0'
        L.append((sec,line))
    texts[c]=L
def strip(s): return re.sub(r'\s+','',s)
rows=[]
for line in open('장v2/부록A.md',encoding='utf-8'):
    if line.startswith('| $'):
        cells=[x.strip() for x in line.strip().strip('|').split(' | ')]
        if len(cells)<4: continue
        rows.append(cells)
print(len(rows))
for cells in rows:
    sym=cells[0]; claimed=cells[2]
    # first math token
    toks=re.findall(r'\$([^$]+)\$',sym)
    if not toks: continue
    t=toks[0].split(',')[0].strip()
    t=re.sub(r':=.*','',t).strip()
    key=strip(t)
    # search for first occurrence in the body (ordered chapters)
    found=None
    for c in chap:
        for sec,l in texts[c]:
            if key in strip(l):
                found=(c,sec); break
        if found: break
    cl=claimed.split('(')[0].split(',')[0].strip()
    ok = found and found[1].startswith(cl)
    if not ok:
        print(f'{sym[:60]:60s} | 주장 {claimed[:25]:25s} | 첫 등장 {found}')
