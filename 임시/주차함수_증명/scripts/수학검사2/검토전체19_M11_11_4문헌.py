# -*- coding: utf-8 -*-
"""11.4 문헌 표: 저자 이름이 장 파일·부록 D의 어느 블록에 나오는지 나열하고, 표에 없는 저자 이름 후보를 찾는다."""
import re, os, sys, io, glob
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from 검토전체19_M11_공용 import *

bl = all_blocks()
# 부록 D 항목 블록
for f in sorted(glob.glob(os.path.join(CH, '부록D_장*.md'))):
    lines = open(f, encoding='utf-8').read().split('\n')
    cur = None
    for i, ln in enumerate(lines):
        m = re.match(r'^### D\.\{\{D:([^}]+)\}\}', ln)
        if m:
            if cur:
                cur['text'] = '\n'.join(lines[cur['start']:i]); bl.append(cur)
            cur = dict(kind='D', label='D:' + m.group(1), sec=None, start=i, file=os.path.basename(f), name=None, mark=None)
    if cur:
        cur['text'] = '\n'.join(lines[cur['start']:]); bl.append(cur)

authors = ['Konheim', 'Weiss', 'Foata', 'Riordan', 'Pollak', 'Celano', 'Aguilar', 'Stanley', 'Knuth', 'Flajolet', 'Sedgewick',
           'Tanner', 'Robbins', 'Petersson', 'Janson', 'Ibragimov', 'Ahlfors', 'Graham', 'Patashnik', 'Fortuin', 'Kasteleyn',
           'Ginibre', 'Grimmett', 'Jensen', 'Wallis', 'Corless', 'Gonnet', 'Hare', 'Jeffrey', 'Harris', 'Comtet', 'Apostol',
           'Titchmarsh', 'Heath-Brown', 'FKG']
def nm(b):
    if b['kind'] == 'D':
        return b['label']
    return (f"{b['kind']} {b['label']}" if b['label'] else f"준비({b['file']} {b['sec']} 행{b['start']+1})")
for a in authors:
    hits = []
    for b in bl:
        if b['file'] == '장11.md':
            continue
        if a in b['text']:
            n = b['text'].count(a)
            hits.append(f"{nm(b)}({b['file']} {b['sec'] or ''})x{n}")
    print('##', a, '→', '; '.join(hits) or '없음')

print()
print('=== 라틴 대문자로 시작하는 낱말 빈도(표에 없는 이름 후보 찾기; 장 파일 전체, 11장 제외)')
cnt = {}
for b in bl:
    if b['file'] == '장11.md' or b['kind'] == 'D':
        continue
    txt = re.sub(r'`[^`]*`', '', b['text'])
    txt = re.sub(r'\\[A-Za-z]+', ' ', txt)  # LaTeX 명령 제거
    for w in re.findall(r'(?<![A-Za-z\\{])[A-Z][a-zà-ÿ]{2,}(?:[–-][A-Z][a-z]+)*', txt):
        cnt[w] = cnt.get(w, 0) + 1
for w, n in sorted(cnt.items(), key=lambda x: -x[1]):
    print(w, n)
