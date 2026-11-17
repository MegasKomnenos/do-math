# -*- coding: utf-8 -*-
# 라벨 -> (파일, 절, 진술 머리) 찾기. 사용: heads.py <base> label1 label2 ... (라벨은 '4:old-4-5' 꼴; 없으면 전부)
import re, sys, io, glob, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
base = sys.argv[1]
want = sys.argv[2:]
files = ['장1','장2','장3','장4','장5A','장5B','장6','장7A','장7B','장8','장9','장10']
out = {}
for fn in files:
    p = os.path.join(base, '장v2', fn + '.md')
    sec = ''
    for i, line in enumerate(open(p, encoding='utf-8').read().split('\n'), 1):
        m = re.match(r'#{2,5}\s+(\d+\.\d+(?:\.\d+)?)', line)
        if m:
            sec = m.group(1)
        m = re.match(r'\*\*(정리|보조정리|명제|따름정리|정의|관찰|주의|예) \{\{([0-9A-Z]+:[^}]+)\}\}(.*?)\*\*', line)
        if m:
            lab = m.group(2)
            head = line[:line.find('**', 2) + 2]
            out.setdefault(lab, []).append((fn, i, sec, m.group(1), head))
if want:
    for w in want:
        for r in out.get(w, [('NONE', 0, '', '', '')]):
            print(w, '|', r[0], 'L%d' % r[1], '| sec', r[2], '|', r[4][:int(os.environ.get('HEADLEN', '600'))])
else:
    for lab, rs in out.items():
        for r in rs:
            print(lab, '|', r[0], 'L%d' % r[1], '| sec', r[2], '|', r[3], '|', r[4][:int(os.environ.get('HEADLEN', '200'))])
