# -*- coding: utf-8 -*-
"""K14: 의존지도 1절의 「부록 D 계산」·「문헌」 열을 장11 11.2·11.4 표와 대조한다."""
import re,sys,io,os,collections
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
B=r'C:\math\임시\주차함수_증명'
lab_re=re.compile(r'\{\{(\d+:[^}]+)\}\}')
L=open(os.path.join(B,'장v2','장11.md'),encoding='utf-8').read().split('\n')
# 11.2
D=collections.defaultdict(set); lit=collections.defaultdict(set)
sec=''
for ln in L:
    m=re.match(r'^### (11\.\d)',ln)
    if m: sec=m.group(1)
    if ln.startswith('| 부록 D.{{D:') and sec=='11.2':
        c=[x.strip() for x in ln.strip().strip('|').split('|')]
        item=re.search(r'\{\{D:([^}]+)\}\}',c[0]).group(1)
        for lab in lab_re.findall(c[1]): D[lab].add((item,c[2]))
    if sec=='11.4' and ln.startswith('| ') and not ln.startswith('| 문헌') and not ln.startswith('|---'):
        c=[x.strip() for x in ln.strip().strip('|').split('|')]
        if len(c)>=3:
            author=re.split(r'[,，]',c[0])[0].strip().split(' ')[0]
            for lab in lab_re.findall(c[2]): lit[lab].add(author)
dep=[];on=False
for line in open(os.path.join(B,'의존지도_v2.md'),encoding='utf-8'):
    if line.startswith('## 1.'): on=True
    elif line.startswith('### 1.1'): on=False
    if on and line.startswith('| `{{'):
        c=[x.strip() for x in line.strip().strip('|').split('|')]
        dep.append(dict(lab=c[0].strip('`').strip('{}'),lit=c[7],D=c[8]))
print('--- 부록 D 열 대조')
for d in dep:
    items=set(re.findall(r'\{\{D:([^}]+)\}\}',d['D']))
    exp=set(i for i,_ in D.get(d['lab'],set()))
    if items!=exp: print(d['lab'],'| 지도:',sorted(items),'| 11.2:',sorted(exp))
    # 산술 등급 비교
    for it,grade in D.get(d['lab'],set()):
        m=re.search(re.escape('{{D:'+it+'}}')+r'\(([^)]*)\)',d['D'])
        if m and m.group(1)!=grade: print('  등급 불일치',d['lab'],it,'지도',m.group(1),'11.2',grade)
print('--- 문헌 열 대조 (지도 열에 있으나 11.4 쓰인 자리에 그 라벨이 없는 저자 / 11.4에 있으나 지도 열에 없는 저자)')
for d in dep:
    dl=d['lit']
    if dl in ('—',''): dauth=set()
    else:
        dauth=set()
        for part in re.split(r';|,\s(?=[A-Z])',dl):
            part=part.strip()
            m=re.match(r'([A-Z][A-Za-z–\-]+)',part)
            if m: dauth.add(m.group(1))
    exp=lit.get(d['lab'],set())
    if dauth!=exp: print(d['lab'],'| 지도:',sorted(dauth),'| 11.4:',sorted(exp))
