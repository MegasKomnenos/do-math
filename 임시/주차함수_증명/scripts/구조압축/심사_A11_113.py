# -*- coding: utf-8 -*-
"""11.2절·11.3절 표에서 주어진 라벨(또는 부록 D 항목)이 나오는 행을 찾는다 — 구조 주장의 여파(11장 쪽) 셈용."""
import re, os, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
ROOT = r'C:\math\임시\주차함수_증명'
lines = open(os.path.join(ROOT,'장v2','장11.md'), encoding='utf-8').read().split('\n')
rows=[]  # (section, rowkey, line no, text)
sec=None
for i,ln in enumerate(lines,1):
    if ln.startswith('### 11.2'): sec='11.2'
    elif ln.startswith('### 11.3'): sec='11.3'
    elif ln.startswith('### 11.4'): sec='11.4'
    elif ln.startswith('**공유 입력.**'): sec='11.3-공유'
    elif ln.startswith('**첫째 증명의 고유 입력.**'): sec='11.3-첫째고유'
    elif ln.startswith('**둘째 증명의 고유 입력.**'): sec='11.3-둘째고유'
    if ln.startswith('| ') and not ln.startswith('|---') and sec:
        key = ln.split(' | ')[0].strip('| ').strip()
        if key in ('입력','부록 D 항목','문헌'): continue
        rows.append((sec,key,i,ln))
labels = sys.argv[1:]
for lab in labels:
    print('=====', lab)
    for sec,key,i,ln in rows:
        if lab in ln:
            print(f'  [{sec}] 행 {i}: {key[:90]}')
