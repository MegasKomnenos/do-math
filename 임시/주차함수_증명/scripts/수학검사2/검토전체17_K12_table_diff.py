# K12: 11.2절 표의 「재계산」·「독립 재계산」 열과 부록 D 항목의 「독립 재계산」 줄을 문자열로 대조해 다른 자리만 보고 (자리 찾기용)
import re,glob,difflib
D={}
for f in ['장2','장3','장4','장5A','장5B','장6']:
    txt=open(f'장v2/부록D_{f}.md',encoding='utf-8').read()
    for m in re.finditer(r'^### D\.\{\{D:([^}]+)\}\}(.*?)(?=^### D\.|\Z)',txt,re.S|re.M):
        lab=m.group(1); body=m.group(2)
        mm=re.search(r'\*\*독립 재계산\.\*\* (〔[^〕]*〕) ?(.*?)\n',body)
        st=re.search(r'\*\*산술 등급\.\*\* (.*?)\n',body)
        D[lab]=(mm.group(1),mm.group(2).strip(),st.group(1).strip(), re.search(r'\(([^()]*(?:\([^()]*\))*[^()]*)\)\s*$',m.group(0).split('\n')[0]).group(1))
tab=open('장v2/장11.md',encoding='utf-8').read()
rows=[l for l in tab.split('\n') if l.startswith('| 부록 D.{{D:')]
for row in rows:
    cells=[c.strip() for c in row.strip().strip('|').split(' | ')]
    lab=re.search(r'D:([^}]+)',cells[0]).group(1)
    if lab not in D: continue
    br,desc,grade,head=D[lab]
    print('=== ',lab)
    print('  표 진술 열:',cells[1],' || D 머리 괄호:',head)
    print('  표 등급 열:',cells[2],' || D 등급 줄:',grade[:120])
    if cells[4]!=br: print('  재계산 괄호 다름:\n   표:',cells[4],'\n   D :',br)
    t=cells[5]
    if t!=desc:
        sm=difflib.SequenceMatcher(None,desc,t)
        for op,a1,a2,b1,b2 in sm.get_opcodes():
            if op!='equal': print(f'   {op}: D[{desc[max(0,a1-25):a2+25]!r}] vs 표[{t[max(0,b1-25):b2+25]!r}]')
