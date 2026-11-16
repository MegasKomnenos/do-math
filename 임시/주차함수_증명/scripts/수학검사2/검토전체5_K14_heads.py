# -*- coding: utf-8 -*-
"""K14: 장 파일의 진술 머리·절 제목을 추출해 TSV로 낸다."""
import re, sys, os, io, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
base = r'C:\math\임시\주차함수_증명\장v2'
order = ['장1','장2','장3','장4','장5A','장5B','장6','장7A','장7B','장8','장9','장10','장11']
head_re = re.compile(r'^\*\*(정의|정리|명제|보조정리|따름정리)\s+\{\{(\d+):([^}]+)\}\}\s*(?:\(([^\n]*?)\))?\s*(?:\[([^\n]*?)\])?\s*\.?\*\*')
sec_re = re.compile(r'^(#{2,4})\s+(.*)$')
rows=[]; secs=[]
counters={}
for ch in order:
    p=os.path.join(base, ch+'.md')
    cur_sec=''
    with open(p, encoding='utf-8') as f:
        for i,line in enumerate(f,1):
            m=sec_re.match(line)
            if m:
                cur_sec=m.group(2).strip(); secs.append((ch,i,m.group(1),cur_sec)); continue
            m=head_re.match(line)
            if m:
                typ,chap,lab,name,status=m.groups()
                counters[chap]=counters.get(chap,0)+1
                num=f'{chap}.{counters[chap]}'
                rows.append(dict(file=ch,line=i,typ=typ,chap=chap,label=lab,name=(name or '').strip(),status=(status or '').strip(),num=num,sec=cur_sec,raw=line.strip()[:400]))
            elif line.startswith('**') and ('{{' in line[:60]) and re.match(r'^\*\*(정의|정리|명제|보조정리|따름정리)',line):
                rows.append(dict(file=ch,line=i,typ='??',chap='',label='',name='',status='',num='',sec=cur_sec,raw=line.strip()[:400]))
out=r'C:\math\임시\주차함수_증명\scripts\수학검사2\_K14_heads.json'
json.dump(dict(rows=rows,secs=secs),open(out,'w',encoding='utf-8'),ensure_ascii=False,indent=0)
print(len(rows),'heads;',len(secs),'section lines')
for r in rows:
    if r['typ']=='??': print('UNPARSED',r['file'],r['line'],r['raw'][:150])
print('--- sections')
for s in secs: print(s[0],s[1],s[2],s[3])
