# -*- coding: utf-8 -*-
"""K14: 본문 산문의 영어 괄호 병기를 모두 찾는다(장부 8절 규칙 8 대조)."""
import re, glob, io, sys, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
os.chdir(r'C:\math\임시\주차함수_증명\장v2')
pat = re.compile(r'\(([A-Za-z][a-zA-Z]+(?:[ \u2013-][a-zA-Z]+){0,4})[;),]')
BS = chr(92)
for f in sorted(glob.glob('장*.md')) + ['부록A.md', '부록C.md']:
    for i, ln in enumerate(open(f, encoding='utf-8'), 1):
        if ln.startswith('|') and f.startswith('장'): pass
        for m in pat.finditer(ln):
            s = m.group(1)
            if len(s) < 5 or s in ('arXiv',): continue
            pre = ln[max(0, m.start() - 30):m.start()]
            if BS in pre[-6:] or '$' in pre[-2:]: continue
            # skip inside math: count $ before
            if ln[:m.start()].count('$') % 2 == 1: continue
            print(f, i, repr(pre[-30:]), '(' + s + ')')
