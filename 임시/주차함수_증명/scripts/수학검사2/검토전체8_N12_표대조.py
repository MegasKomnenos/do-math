import sys,io,re,glob
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8')
base=r"C:\math\임시\주차함수_증명\장v2"
rows={}
for ln in open(base+r"\장11.md",encoding='utf-8').read().split('\n')[20:62]:
    cells=[c.strip() for c in ln.strip().strip('|').split(' | ')]
    m=re.search(r'D\.\{\{D:([^}]*)\}\}',cells[0]); rows[m.group(1)]=cells
items={}
for f in ['부록D_장2','부록D_장3','부록D_장4','부록D_장5A','부록D_장5B','부록D_장6']:
    txt=open(base+'/'+f+'.md',encoding='utf-8').read()
    for sec in re.split(r'(?m)^### ',txt)[1:]:
        m=re.match(r'D\.\{\{D:([^}]*)\}\}(.*)',sec); name=m.group(1)
        head=m.group(2)
        stmts=re.search(r'\(([^()]*(?:\([^()]*\)[^()]*)*)\)\s*$',head.strip().split('\n')[0])
        ir=re.search(r'\*\*독립 재계산\.\*\*\s*〔([^〕]*)〕\s*(.*)',sec)
        gr=re.search(r'\*\*산술 등급\.\*\*\s*(.*)',sec)
        items[name]=(stmts.group(1) if stmts else None, ir.group(1), ir.group(2).strip(), gr.group(1))
for name,(st,br,body,gr) in items.items():
    r=rows[name]
    b2=body.replace('이 문단 머리의 꺾쇠 괄호','「재계산」 열의 꺾쇠 괄호')
    if r[4]!='〔'+br+'〕': print('BRACKET DIFF',name,'\n  D :',br,'\n  11:',r[4])
    if r[5]!=b2:
        # find first difference
        i=0
        while i<min(len(r[5]),len(b2)) and r[5][i]==b2[i]: i+=1
        print('BODY DIFF',name,'\n  D :',b2[max(0,i-40):i+80],'\n  11:',r[5][max(0,i-40):i+80])
    # statements
    st_norm=re.sub(r'(보조정리|정리|명제|따름정리) ','',st or '')
    r1=re.sub(r'(보조정리|정리|명제|따름정리) ','',r[1])
    if st_norm.replace(', ',',')!=r1.replace(', ',','): print('STMT DIFF',name,'\n  D :',st,'\n  11:',r[1])
    print(name,'| 11.2 grade:',r[2],'| D grade:',gr[:90])
