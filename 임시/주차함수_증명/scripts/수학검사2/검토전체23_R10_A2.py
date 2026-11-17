# -*- coding: utf-8 -*-
# 주어진 (핵 문자열, 절) 쌍마다 그 절 안의 첫 등장 줄 문맥을 낸다. 인자: base, 그리고 "핵@@절" 여러 개
import re, sys, io, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
base = sys.argv[1]
files = ['장1','장2','장3','장4','장5A','장5B','장6','장7A','장7B','장8','장9','장10']
lines = []
for fn in files:
    sec = fn.replace('장','').rstrip('AB') + '.0'
    for i, line in enumerate(open(os.path.join(base, '장v2', fn + '.md'), encoding='utf-8').read().split('\n'), 1):
        m = re.match(r'#{2,5}\s+(\d+\.\d+)(?:\.\d+)?', line)
        if m: sec = m.group(1)
        lines.append((sec, fn, i, line))
ctx = int(os.environ.get('CTX', '110'))
for arg in sys.argv[2:]:
    core, want = arg.split('@@')
    cores = core.split('||')
    found = False
    for sec, fn, i, l in lines:
        if want != '*' and sec != want: continue
        for c in cores:
            j = l.find(c)
            if j >= 0:
                print('[%s @ %s] %s L%d: …%s…' % (c, want, fn, i, l[max(0, j-ctx):j+len(c)+ctx]))
                found = True; break
        if found: break
    if not found:
        # 전체에서 첫 등장
        for sec, fn, i, l in lines:
            for c in cores:
                j = l.find(c)
                if j >= 0:
                    print('[%s @ %s] NOT IN SEC; first anywhere: sec %s %s L%d: …%s…' % (c, want, sec, fn, i, l[max(0, j-ctx):j+len(c)+ctx])); found = True; break
            if found: break
        if not found: print('[%s @ %s] NOWHERE' % (core, want))
