# -*- coding: utf-8 -*-
# 고정 문자열이 나오는 줄마다 (파일, 행, 절, 가장 가까운 앞 진술/증명 머리)를 낸다. 사용: where.py <base> <고정문자열> [ctx]
import re, sys, io, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
base = sys.argv[1]; needle = sys.argv[2]; ctx = int(sys.argv[3]) if len(sys.argv) > 3 else 60
files = ['장1','장2','장3','장4','장5A','장5B','장6','장7A','장7B','장8','장9','장10']
if len(sys.argv) > 4: files = sys.argv[4].split(',')
for fn in files:
    p = os.path.join(base, '장v2', fn + '.md')
    sec = ''; blk = ''
    for i, line in enumerate(open(p, encoding='utf-8').read().split('\n'), 1):
        m = re.match(r'#{2,5}\s+(\d+\.\d+(?:\.\d+)?)', line)
        if m: sec = m.group(1); blk = ''
        m = re.match(r'\*\*((정리|보조정리|명제|따름정리|정의) \{\{([0-9A-Z]+:[^}]+)\}\}(\([^)]*\))?(의 증명)?)', line)
        if m: blk = m.group(3) + ('(증명)' if m.group(5) else '')
        elif re.match(r'\*\*증명', line): blk = blk.replace('(증명)', '') + '(증명)'
        j = 0
        while True:
            j = line.find(needle, j)
            if j < 0: break
            print('%s L%d sec %s [%s] …%s…' % (fn, i, sec, blk, line[max(0, j-ctx):j+len(needle)+ctx]))
            j += len(needle)
