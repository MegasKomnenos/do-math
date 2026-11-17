# -*- coding: utf-8 -*-
# 진술 머리의 「…에 의존」 목록으로 주 정리(9:old-8-37)의 의존 폐포를 구하고, 폐포 안의 계산·문헌 표지를 낸다.
import re, sys, io, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
base = sys.argv[1]
root = sys.argv[2] if len(sys.argv) > 2 else '9:old-8-37'
files = ['장1','장2','장3','장4','장5A','장5B','장6','장7A','장7B','장8','장9','장10']
heads = {}
for fn in files:
    p = os.path.join(base, '장v2', fn + '.md')
    sec = ''
    for i, line in enumerate(open(p, encoding='utf-8').read().split('\n'), 1):
        m = re.match(r'#{2,5}\s+(\d+\.\d+(?:\.\d+)?)', line)
        if m: sec = m.group(1)
        m = re.match(r'\*\*(정리|보조정리|명제|따름정리|정의) \{\{([0-9A-Z]+:[^}]+)\}\}', line)
        if m and not line.split('}}', 1)[1].startswith('의 증명'):
            lab = m.group(2)
            head = line[:line.find('**', 2) + 2]
            # 표지: 마지막 [ ... ] 
            k = head.rfind(' [')
            status = head[k+2:head.rfind(']')] if k >= 0 else ''
            if lab not in heads:
                heads[lab] = (fn, i, sec, m.group(1), head, status)
dep = {}
for lab, (fn, i, sec, typ, head, status) in heads.items():
    st = status.split(';')[0]
    dep[lab] = re.findall(r'\{\{([0-9A-Z]+:[^}]+)\}\}', st)
seen = []
stack = [root]
while stack:
    x = stack.pop()
    if x in seen: continue
    seen.append(x)
    for y in dep.get(x, []):
        stack.append(y)
mode = sys.argv[3] if len(sys.argv) > 3 else 'closure'
if mode == 'closure':
    for lab in sorted(seen):
        if lab not in heads:
            print('MISSING HEAD', lab); continue
        fn, i, sec, typ, head, status = heads[lab]
        st = status.split(';')[0]
        flags = []
        for w in ['계산 증거', '계산 보조', '문헌 인용', '작성자 판단', '시작점 비명시']:
            if w in st: flags.append(w)
        print(lab, '|', fn, sec, '|', ','.join(flags), '|', re.sub(r'\{\{[^}]+\}\}', '#', st)[:200])
elif mode == 'lit':
    for lab, (fn, i, sec, typ, head, status) in heads.items():
        if '문헌 인용' in status:
            print(lab, '|', fn, 'L%d' % i, sec, '| in closure:', lab in seen, '|', head[:300])
elif mode == 'comp':
    for lab, (fn, i, sec, typ, head, status) in heads.items():
        st = status.split(';')[0]
        if '계산 증거' in st or '계산 보조' in st:
            print(lab, '|', fn, 'L%d' % i, sec, '| in closure:', lab in seen, '|', st[:160])
