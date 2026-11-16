# -*- coding: utf-8 -*-
"""V1 검토: 부록 B의 기록 식별자와 본문(장·부록 A·C·D)의 [rxxxxxxx] 인용을 양방향으로 대조한다. 읽기 전용."""
import re, glob, io, os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.chdir(ROOT)
B = io.open('장v2/부록B.md', encoding='utf-8').read()
b_ids = set(re.findall(r'^\| (r[0-9a-f]{7}) \|', B, re.M))
cited = {}
for f in sorted(glob.glob('장v2/*.md')):
    if f.endswith('부록B.md'): continue
    s = io.open(f, encoding='utf-8').read()
    for m in re.finditer(r'\b(r[0-9a-f]{7})\b', s):
        cited.setdefault(m.group(1), set()).add(os.path.basename(f))
body_only = {}
for f in sorted(glob.glob('장v2/장*.md')):
    s = io.open(f, encoding='utf-8').read()
    for m in re.finditer(r'\b(r[0-9a-f]{7})\b', s):
        body_only.setdefault(m.group(1), set()).add(os.path.basename(f))
print('부록 B 식별자 수:', len(b_ids))
print('본문+부록A/C/D 인용 식별자 수:', len(cited))
print('부록 B에 있으나 어디에도 인용 없음:', sorted(b_ids - set(cited)))
print('인용되나 부록 B에 없음:', {k: sorted(v) for k, v in cited.items() if k not in b_ids})
print('부록 B에 있으나 장 파일(본문)에는 인용 없음(부록 A/C/D에만):', {k: sorted(cited[k]) for k in sorted(b_ids - set(body_only)) if k in cited})
print('rfbd91ce 부록 B:', 'rfbd91ce' in b_ids, ' 인용:', cited.get('rfbd91ce'))
print('r5f5cf73 부록 B:', 'r5f5cf73' in b_ids, ' 인용:', sorted(cited.get('r5f5cf73', [])))
