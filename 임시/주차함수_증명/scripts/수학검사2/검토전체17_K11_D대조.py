import re,glob,io,sys
out=io.open(r'C:\math\임시\주차함수_증명\scripts\수학검사2\_K11_D대조_out.txt','w',encoding='utf-8')
# parse appendix D entries
entries={}
order=[]
for f in sorted(glob.glob(r'C:\math\임시\주차함수_증명\장v2\부록D_장*.md')):
    txt=io.open(f,encoding='utf-8').read()
    parts=re.split(r'\n(?=### D\.\{\{D:)',txt)
    for p in parts:
        m=re.match(r'### D\.\{\{D:([^}]+)\}\}(.*)',p)
        if not m: continue
        lab=m.group(1); head=m.group(2).strip()
        d={'file':f.replace(chr(92),'/').split('/')[-1],'head':head}
        for key in ['확인하는 진술','산술 등급','독립 재계산','범위','자료']:
            mm=re.search(r'\*\*'+key+r'\.\*\*\s*(.*)',p)
            d[key]=mm.group(1).strip() if mm else None
        entries[lab]=d; order.append(lab)
# parse 11.2 table
t=io.open(r'C:\math\임시\주차함수_증명\장v2\장11.md',encoding='utf-8').read().split('\n')
rows=[]
for i,l in enumerate(t,1):
    if l.startswith('| 부록 D.{{D:'):
        cells=[c.strip() for c in l.strip().strip('|').split(' | ')]
        rows.append((i,cells))
out.write('D entries: %d, table rows: %d\n'%(len(entries),len(rows)))
tab_labels=[re.match(r'부록 D\.\{\{D:([^}]+)\}\}',c[0]).group(1) for _,c in rows]
out.write('D not in table: %s\n'%[l for l in order if l not in tab_labels])
out.write('table not in D: %s\n'%[l for l in tab_labels if l not in entries])
out.write('order same: %s\n'%(tab_labels==[l for l in order]))
for (i,c) in rows:
    lab=re.match(r'부록 D\.\{\{D:([^}]+)\}\}',c[0]).group(1)
    e=entries.get(lab)
    out.write('\n=== row %d  %s  (%s)\n'%(i,lab,e['file'] if e else '?'))
    out.write('TBL stmt : %s\n'%c[1])
    out.write('D   head : %s\n'%(e['head'] if e else ''))
    out.write('TBL grade: %s\n'%c[2])
    out.write('D   grade: %s\n'%(e['산술 등급'] if e else ''))
    out.write('TBL loc  : %s\n'%c[3])
    out.write('TBL brk  : %s\n'%c[4])
    ir=e['독립 재계산'] if e else ''
    mb=re.match(r'(〔[^〕]*〕)\s*(.*)',ir or '')
    out.write('D   brk  : %s\n'%(mb.group(1) if mb else ir))
    rest=mb.group(2) if mb else ''
    same = rest==c[5]
    out.write('TEXT same: %s\n'%same)
    if not same:
        # show diff locations
        import difflib
        sm=difflib.SequenceMatcher(None,rest,c[5])
        for op,a1,a2,b1,b2 in sm.get_opcodes():
            if op!='equal':
                out.write('  %s D[%s] -> T[%s]\n'%(op,rest[a1:a2],c[5][b1:b2]))
out.close()
