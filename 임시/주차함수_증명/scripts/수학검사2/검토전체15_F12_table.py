import re,sys,io
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8')
base='C:/math/임시/주차함수_증명/장v2/'
files=['부록D_장2.md','부록D_장3.md','부록D_장4.md','부록D_장5A.md','부록D_장5B.md','부록D_장6.md']
items={}
for f in files:
    txt=open(base+f,encoding='utf-8').read()
    parts=re.split(r'(?m)^### D\.\{\{D:([^}]+)\}\}',txt)
    for i in range(1,len(parts),2):
        lab=parts[i]; body=parts[i+1]
        d={'file':f}
        m=re.search(r'^### D\.\{\{D:'+re.escape(lab)+r'\}\}(.*)$',txt,re.M); d['title']=m.group(1).strip()
        for key in ['확인하는 진술','산술 등급','독립 재계산','식','알고리즘','범위','결과','자료','출처']:
            m=re.search(r'\*\*'+key+r'\.\*\*\s*(.*?)(?=\n\n\*\*|\n### |\Z)',body,re.S)
            d[key]=m.group(1).strip() if m else None
        items[lab]=d
rows={}
for line in open(base+'장11.md',encoding='utf-8'):
    if line.startswith('| 부록 D.{{D:'):
        cells=[c.strip() for c in line.strip().strip('|').split(' | ')]
        lab=re.match(r'부록 D\.\{\{D:([^}]+)\}\}',cells[0]).group(1)
        rows.setdefault(lab,[]).append(cells)
for lab,d in items.items():
    print('='*10,lab,d['file'])
    if lab not in rows: print('  !! 11.2 표에 행 없음'); continue
    for cells in rows[lab]:
        stmt,grade,loc,brk,narr=cells[1],cells[2],cells[3],cells[4],cells[5]
        g1=d['산술 등급'].split('(')[0].split('.')[0].split(';')[0].strip()
        print('  표 진술:',stmt,'| 등급:',grade,'| 곳:',loc)
        print('  D 등급 첫머리:',d['산술 등급'][:80])
        if grade not in d['산술 등급'].split('.')[0]: print('  !! 등급 불일치')
        ir=d['독립 재계산']
        m=re.match(r'(〔[^〕]*〕)\s*(.*)',ir,re.S)
        dbrk,dnarr=m.group(1),m.group(2)
        if dbrk!=brk: print('  !! 꺾쇠 불일치\n   D:',dbrk,'\n   표:',brk)
        dn=dnarr.replace('이 문단 머리의 꺾쇠 괄호','「재계산」 열의 꺾쇠 괄호')
        if re.sub(r'\s+',' ',dn)!=re.sub(r'\s+',' ',narr):
            print('  !! 서술 불일치')
            import difflib
            for op in difflib.SequenceMatcher(None,dn,narr).get_opcodes():
                if op[0]!='equal': print('    ',op[0],repr(dn[op[1]:op[2]])[:200],'->',repr(narr[op[3]:op[4]])[:200])
        # statement labels in 확인하는 진술 title
        print('  D 제목:',d['title'][:150])
