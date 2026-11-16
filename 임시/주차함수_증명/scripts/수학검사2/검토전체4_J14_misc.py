# -*- coding: utf-8 -*-
"""J14: (1) 장부 7절 「이 글의 글자」가 1절(1.1–1.3)에 있는지, (2) 구조표 절 제목이 장 파일 ### 제목과 같은지,
(3) 몇 라벨의 현재 번호."""
import re, sys, io, glob
from pathlib import Path
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
ROOT = Path(r'C:\math\임시\주차함수_증명')
lines = (ROOT/'장부_v2.md').read_text(encoding='utf-8').splitlines()
sec1 = '\n'.join(lines[19:415])
def norm(s): return re.sub(r'\s+', '', s)
sec1n = norm(sec1)
print('## 7절 글자 가운데 1절에 없는 것')
for i in range(1236, 1442):
    L = lines[i]
    if not L.startswith('| '): continue
    col = L.strip().strip('|').split('|')[0]
    for g in re.findall(r'\$([^$]+)\$', col):
        gn = norm(g)
        # 바탕: 괄호 인수 떼기
        base = re.sub(r'\([^()]*\)$', '', gn)
        if gn not in sec1n and base not in sec1n:
            print(f'  {i+1}: ${g}$')
print('## 구조표 절 제목 대 장 파일 제목')
heads = {}
for f in glob.glob(str(ROOT/'장v2'/'장*.md')):
    for L in Path(f).read_text(encoding='utf-8').splitlines():
        m = re.match(r'^###\s+(\d+\.\d+)\s+(.*)', L)
        if m: heads[m.group(1)] = m.group(2).strip()
for L in (ROOT/'구조표_v2.md').read_text(encoding='utf-8').splitlines():
    m = re.match(r'^\|\s*(\d+\.\d+)\s+([^|]+?)\s*\|', L)
    if not m: continue
    num, title = m.group(1), m.group(2)
    title = re.sub(r'\(.*?\)', '', title).strip()
    h = heads.get(num)
    if h is None: print(f'  {num} 「{title}」: 장 파일에 ### {num} 없음')
    elif norm(h) != norm(title): print(f'  {num} 구조표「{title}」 장「{h}」')
print('## 번호')
import csv
for L in (ROOT/'scripts'/'수학검사2'/'_J14_heads.tsv').read_text(encoding='utf-8').splitlines():
    lab = L.split('\t')[0]
    if lab in ('9:old-7-46','10:old-8-37','6:old-6-19','7:old-6-13','5:old-5-18','4:old-4-5'):
        print('  ', L[:120])
