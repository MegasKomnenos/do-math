import re, glob, sys, io, difflib
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
# --- appendix D items
D={}
for f in sorted(glob.glob('장v2/부록D_장*.md')):
    txt=open(f,encoding='utf-8').read()
    for p in re.split(r'\n(?=### )',txt):
        m=re.search(r'^### D\.\{\{D:([^}]+)\}\}(.*)$',p,re.M)
        if not m: continue
        lab=m.group(1); head=m.group(2)
        item={'file':f,'head':head.strip()}
        for key in ['확인하는 진술','산술 등급','독립 재계산','자료','출처']:
            mm=re.search(r'^\*\*'+key+r'\.\*\*\s*(.*)$',p,re.M)
            item[key]=mm.group(1).strip() if mm else None
        D[lab]=item
print('D items:',len(D))
# --- table rows
T={}
for line in open('장v2/장11.md',encoding='utf-8'):
    if line.startswith('| 부록 D.{{D:'):
        cells=[c.strip() for c in line.strip().strip('|').split(' | ')]
        lab=re.match(r'부록 D\.\{\{D:([^}]+)\}\}',cells[0]).group(1)
        T[lab]=cells
print('table rows:',len(T))
print('in D not in table:',sorted(set(D)-set(T)))
print('in table not in D:',sorted(set(T)-set(D)))
def norm(s):
    s=s.replace('이 문단 머리의 꺾쇠 괄호','「재계산」 열의 꺾쇠 괄호')
    return re.sub(r'\s+',' ',s).strip()
for lab in T:
    if lab not in D: continue
    cells=T[lab]; d=D[lab]
    # statements
    st_head=re.findall(r'\{\{(\d+[AB]?:[^}]+)\}\}',d['head'])
    st_tab=re.findall(r'\{\{(\d+[AB]?:[^}]+)\}\}',cells[1])
    if st_head!=st_tab: print(f'[{lab}] 진술 불일치: D머리 {st_head} / 표 {st_tab}')
    # grade
    g=d['산술 등급'] or ''
    g1=re.split(r'[(（.。;]',g)[0].strip()
    if cells[2].replace(' ','')!=g1.replace(' ',''):
        print(f'[{lab}] 등급: 표 "{cells[2]}" / D 첫 등급 "{g1}"  (D 전체: {g[:160]})')
    # recalc
    r=d['독립 재계산'] or ''
    mb=re.match(r'(〔[^〕]*〕)\s*(.*)$',r,re.S)
    if not mb: print(f'[{lab}] D 독립 재계산 줄에 꺾쇠 괄호 없음: {r[:100]}'); continue
    br,rest=mb.group(1),mb.group(2)
    if norm(br)!=norm(cells[4]): print(f'[{lab}] 꺾쇠 다름:\n   표 {cells[4]}\n   D  {br}')
    a,b=norm(cells[5]),norm(rest)
    if a!=b:
        print(f'[{lab}] 독립 재계산 서술 다름:')
        sm=difflib.SequenceMatcher(None,a,b)
        for op,i1,i2,j1,j2 in sm.get_opcodes():
            if op!='equal':
                print(f'    {op}: 표[{a[max(0,i1-25):i2+25]}] / D[{b[max(0,j1-25):j2+25]}]')
