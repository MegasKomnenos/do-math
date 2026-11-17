# -*- coding: utf-8 -*-
# 장부 5·6·7절(1185–1444행)이 가리키는 라벨 {{장:이름}}·{{D:이름}}과 절 번호가 살아 있는지 본다.
# 진술 라벨은 검토전체25_R13_heads.json(현행 진술 머리 272개), 부록 D 라벨은 부록D_장*.md의 항목 머리, 절 번호는 장 파일의 ###·#### 머리로 본다.
import sys, io, re, json, glob, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', newline='\n')
heads = json.load(io.open('scripts/수학검사2/검토전체25_R13_heads.json',encoding='utf-8'))
live = {(h['ch'], h['lab']): h for h in heads}
L = io.open('장부_v2.md',encoding='utf-8').read().split('\n')
a,b = (int(sys.argv[1]), int(sys.argv[2])) if len(sys.argv)>2 else (1185,1444)
dtext = '\n'.join(io.open(f,encoding='utf-8').read() for f in glob.glob('장v2/부록D_장*.md'))
dlabs = set(re.findall(r'\{\{D:([A-Za-z0-9\-]+)\}\}', dtext))
dheads = set(re.findall(r'^#+\s*D\.\{\{D:([A-Za-z0-9\-]+)\}\}', dtext, flags=re.M)) | set(re.findall(r'^\*\*D\.\{\{D:([A-Za-z0-9\-]+)\}\}', dtext, flags=re.M))
secs=set()
for f in glob.glob('장v2/장*.md'):
    for m in re.finditer(r'^#{2,5}\s+(\d+(?:\.\d+)*)[\s.]', io.open(f,encoding='utf-8').read(), flags=re.M):
        secs.add(m.group(1))
print('산 진술 라벨', len(live), '부록 D 라벨(머리)', len(dheads), '(본문 등장 포함 %d)'%len(dlabs), '절 번호', len(secs))
for i in range(a,b+1):
    s=L[i-1]
    for m in re.finditer(r'\{\{([0-9A-Za-z]+):([A-Za-z0-9\-]+)\}\}', s):
        ch,lab=m.group(1),m.group(2)
        if ch=='D':
            if lab not in dheads: print('%d행: 부록 D 라벨 {{D:%s}} — 항목 머리에 없음%s'%(i,lab,'' if lab not in dlabs else '(부록 D 글 안에는 등장)'))
        elif (ch,lab) not in live:
            print('%d행: 진술 라벨 {{%s:%s}} — 현행 머리에 없음'%(i,ch,lab))
        else:
            # 앞의 종류 낱말이 머리의 종류와 같은지
            pre = s[max(0,m.start()-12):m.start()]
            km = re.search(r'(정리|보조정리|명제|따름정리|정의|보기|관찰|주의|가설)\s*`?$', pre)
            if km and km.group(1)!=live[(ch,lab)]['kind']:
                print('%d행: {{%s:%s}} 앞의 종류 「%s」 — 머리는 「%s」'%(i,ch,lab,km.group(1),live[(ch,lab)]['kind']))
