import re,io,sys
sys.stdout.reconfigure(encoding='utf-8')
files=['장v2/부록D_장7A.md','장v2/부록D_장7B.md','장v2/부록D_장8.md','장v2/부록D_장9.md','장v2/부록D_장10.md']
items={}
for f in files:
    txt=open(f,encoding='utf-8').read()
    parts=re.split(r'^### D\.\{\{D:([^}]+)\}\}',txt,flags=re.M)
    for i in range(1,len(parts),2):
        lab=parts[i]; body=parts[i+1]
        m=re.search(r'\*\*산술 등급\.\*\*\s*(.*?)\n',body); grade=m.group(1).strip() if m else None
        m=re.search(r'\*\*독립 재계산\.\*\*\s*(.*?)\n',body); indep=m.group(1).strip() if m else None
        m=re.search(r'^\s*(.*?)\n',body); title=m.group(1).strip()
        items[lab]=(f,title,grade,indep)
rows={}
for line in open('장v2/장11.md',encoding='utf-8'):
    m=re.match(r'\| 부록 D\.\{\{D:([^}]+)\}\} \| (.*?) \| (.*?) \| (.*?) \| (.*?) \| (.*?) \|\s*$',line)
    if m: rows[m.group(1)]=m.groups()[1:]
for lab,(f,title,grade,indep) in items.items():
    print('=====',lab,f)
    if lab not in rows: print('  11.2 행 없음'); continue
    stmt,g,sec,br,txt=rows[lab]
    # title statements
    tm=re.search(r'\(([^()]*(?:\([^()]*\)[^()]*)*)\)\s*$',title)
    print('  제목 진술:',tm.group(1) if tm else title)
    print('  11.2 진술:',stmt)
    print('  D 등급   :',grade)
    print('  11.2 등급:',g, '| 쓰인 곳', sec)
    bm=re.match(r'(〔.*?〕)\s*(.*)',indep or '')
    dbr,dtxt=(bm.group(1),bm.group(2)) if bm else (None,indep)
    print('  괄호 같음:',dbr==br, '' if dbr==br else f'\n    D:{dbr}\n    T:{br}')
    print('  본문 같음:',dtxt==txt, '' if dtxt==txt else f'\n    D[:300]:{(dtxt or "")[:300]}\n    T[:300]:{txt[:300]}')
