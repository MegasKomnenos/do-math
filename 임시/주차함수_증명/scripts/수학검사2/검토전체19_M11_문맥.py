# -*- coding: utf-8 -*-
"""라벨이 인용된 자리의 앞뒤 문맥을 블록 이름과 함께 찍는다. 사용: python -I 문맥.py <라벨> [파일 접두…]"""
import re, os, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from 검토전체19_M11_공용 import *

label = sys.argv[1]
files = sys.argv[2:] or ['장9.md', '장10.md', '장7B.md']
W = int(os.environ.get('W', '220'))
tag = '{{' + label + '}}'
for b in all_blocks():
    if b['file'] not in files or b['label'] == label:
        continue
    txt = b['text']
    for m in re.finditer(re.escape(tag), txt):
        s = max(0, m.start() - W); e = min(len(txt), m.end() + W)
        nm = f"{b['kind']} {b['label']}" if b['label'] else f"준비({b['file']} {b['sec']} 행{b['start']+1})"
        print(f"[{nm}] …{txt[s:e].replace(chr(10),' ')}…")
        print()
