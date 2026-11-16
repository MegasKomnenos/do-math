# 11.2 표의 행(재계산·독립 재계산 열)과 부록 D 항목의 독립 재계산 줄을 비교한다.
import re,io,sys
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8')
root='C:/math/임시/주차함수_증명/장v2/'
tab={}
for line in open(root+'장11.md',encoding='utf-8'):
    if line.startswith('| 부록 D.{{D:'):
        cells=[c.strip() for c in line.strip().strip('|').split(' | ')]
        m=re.match(r'부록 D\.\{\{D:([^}]+)\}\}',cells[0])
        tab[m.group(1)]=cells
items={}
for f in ['부록D_장2.md','부록D_장3.md','부록D_장4.md','부록D_장5A.md','부록D_장5B.md','부록D_장6.md']:
    cur=None
    for line in open(root+f,encoding='utf-8'):
        m=re.match(r'### D\.\{\{D:([^}]+)\}\} (.*)',line)
        if m: cur=m.group(1); items[cur]={'title':m.group(2),'file':f}; continue
        for key in ['확인하는 진술','산술 등급','독립 재계산','자료','출처','범위','결과','식','알고리즘']:
            if line.startswith('**'+key+'.**'):
                items[cur][key]=line[len('**'+key+'.**'):].strip()
for k,it in items.items():
    row=tab.get(k)
    print('====',k,it['file'])
    if not row: print('  11.2 표에 없음'); continue
    ind=it.get('독립 재계산','')
    m=re.match(r'〔(.*?)〕\s*(.*)',ind)
    br,txt=(m.group(1),m.group(2)) if m else ('',ind)
    print('  표 진술:',row[1]); print('  표 등급:',row[2]); print('  표 절:',row[3])
    print('  D 등급:',it.get('산술 등급','')[:150])
    print('  괄호 같음:', ('〔'+br+'〕')==row[4], '' if ('〔'+br+'〕')==row[4] else '\n    D:'+br+'\n    표:'+row[4])
    same = txt==row[5]
    print('  본문 같음:', same)
    if not same:
        # 첫 차이 위치
        i=0
        while i<min(len(txt),len(row[5])) and txt[i]==row[5][i]: i+=1
        print('    D :',txt[max(0,i-60):i+120]); print('    표:',row[5][max(0,i-60):i+120])
