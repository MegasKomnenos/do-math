# Q12: 부록 D 항목(장2~장6)의 줄과 11.2절 표의 행을 맞춘다 (자리 찾기용)
import re,sys,io
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8')
files=['장v2/부록D_장2.md','장v2/부록D_장3.md','장v2/부록D_장4.md','장v2/부록D_장5A.md','장v2/부록D_장5B.md','장v2/부록D_장6.md']
items={}
for f in files:
    txt=open(f,encoding='utf-8').read()
    parts=re.split(r'^### D\.\{\{D:([^}]+)\}\}',txt,flags=re.M)
    for i in range(1,len(parts),2):
        tag=parts[i]; body=parts[i+1]
        head=body.split('\n',1)[0]
        lines={}
        for m in re.finditer(r'^\*\*([^*]+)\.\*\*\s*(.*)$',body,flags=re.M):
            lines[m.group(1)]=m.group(2).strip()
        items[tag]=(f,head,lines)
tab=open('장v2/장11.md',encoding='utf-8').read()
rows={}
for line in tab.splitlines():
    if line.startswith('| 부록 D.{{D:'):
        cells=[c.strip() for c in line.strip().strip('|').split(' | ')]
        tag=re.match(r'부록 D\.\{\{D:([^}]+)\}\}',cells[0]).group(1)
        rows[tag]=cells
for tag,(f,head,lines) in items.items():
    print('=====',tag,'(',f,')')
    if tag not in rows: print('  !! 표에 행 없음'); continue
    cells=rows[tag]
    # 확인하는 진술 열 vs 머리 괄호
    m=re.search(r'\(([^()]*(?:\([^()]*\)[^()]*)*)\)\s*$',head)
    headstmts=m.group(1) if m else head
    print('  머리:',headstmts); print('  표  :',cells[1])
    # 산술 등급
    grade=lines.get('산술 등급','')
    print('  D등급:',grade[:120]); print('  표등급:',cells[2])
    ir=lines.get('독립 재계산','')
    mb=re.match(r'〔([^〕]*)〕\s*(.*)$',ir,flags=re.S)
    if not mb: print('  !! 꺾쇠 없음'); continue
    br='〔'+mb.group(1)+'〕'; rest=mb.group(2).strip()
    print('  꺾쇠 같음:',br==cells[4])
    if br!=cells[4]: print('   D:',br); print('   표:',cells[4])
    rest2=rest.replace('이 문단 머리의 꺾쇠 괄호','「재계산」 열의 꺾쇠 괄호')
    same=(rest2==cells[5])
    print('  서술 같음:',same)
    if not same:
        import difflib
        for d in difflib.ndiff([rest2],[cells[5]]):
            if d[0] in '+-?': print('   ',d[:600])
