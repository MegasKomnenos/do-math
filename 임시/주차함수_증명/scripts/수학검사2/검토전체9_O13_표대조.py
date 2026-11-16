# D 항목의 〔…〕 괄호·산술 등급 첫 등급·독립 재계산 서술을 11.2 표의 행과 맞춘다(자리 찾기용).
import re,io
files=["장v2/부록D_장7A.md","장v2/부록D_장7B.md","장v2/부록D_장8.md","장v2/부록D_장9.md","장v2/부록D_장10.md"]
items={}
for f in files:
    txt=open(f,encoding='utf-8').read()
    for m in re.finditer(r'^### D\.\{\{D:([^}]+)\}\}(.*?)(?=^### D\.|\Z)',txt,re.S|re.M):
        lab=m.group(1); body=m.group(2)
        br=re.search(r'\*\*독립 재계산\.\*\*\s*(〔[^〕]*〕)\s*(.*?)\n',body,re.S)
        gr=re.search(r'\*\*산술 등급\.\*\*\s*(.*?)\n',body,re.S)
        items[lab]=dict(file=f,bracket=br.group(1) if br else None,text=br.group(2).strip() if br else None,grade=gr.group(1).strip() if gr else None,head=body.split('\n')[0])
rows={}
for line in open("장v2/장11.md",encoding='utf-8'):
    if line.startswith('| 부록 D.{{D:'):
        cells=[c.strip() for c in line.strip().strip('|').split(' | ')]
        lab=re.match(r'부록 D\.\{\{D:([^}]+)\}\}',cells[0]).group(1)
        rows[lab]=cells
for lab,it in items.items():
    r=rows.get(lab)
    if not r: print("NO ROW",lab); continue
    print("==",lab,"| 표 진술:",r[1],"| 표 등급:",r[2],"| 표 절:",r[3])
    print("   D 머리:",it['head'][:160])
    print("   D 등급:",(it['grade'] or '')[:200])
    if it['bracket']!=r[4]: print("   괄호 다름:\n     D:",it['bracket'],"\n     표:",r[4])
    t=it['text'] or ''
    t2=r[5]
    # normalize 자리 표현
    tn=t.replace('이 문단 머리의 꺾쇠 괄호','「재계산」 열의 꺾쇠 괄호')
    if tn!=t2:
        # find first difference
        i=0
        while i<min(len(tn),len(t2)) and tn[i]==t2[i]: i+=1
        print("   서술 다름 at",i,":\n     D:",tn[max(0,i-60):i+120],"\n     표:",t2[max(0,i-60):i+120])
