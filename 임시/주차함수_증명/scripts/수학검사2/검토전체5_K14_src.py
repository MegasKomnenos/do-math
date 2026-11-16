# -*- coding: utf-8 -*-
import re, io, sys, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
os.chdir(r'C:\math\임시\주차함수_증명\장v2')
BS = chr(92)
pat = re.compile(r'mathrm' + BS + r'{src' + BS + r'}' + BS + r'\^' + BS + r'{' + BS*2 + r'mathrm [A-Z]' + BS + r'}[_a-z0-9{}]*')
for i, ln in enumerate(open('장7B.md', encoding='utf-8'), 1):
    m = pat.search(ln)
    if m: print(i, m.group(0), '|', ln[max(0, m.start() - 70):m.start()])
print('--- 7.4 range: lines 1-375')
