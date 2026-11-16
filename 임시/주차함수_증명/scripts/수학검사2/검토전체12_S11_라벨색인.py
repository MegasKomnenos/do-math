# S11: 장 파일의 진술 머리를 모아 라벨 → (종류, 절, 파일, 행, 머리) 색인을 만든다.
import re, glob, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
files = ['장1','장2','장3','장4','장5A','장5B','장6','장7A','장7B','장8','장9','장10','장11']
idx = {}
for ch in files:
    f = f'장v2/{ch}.md'
    sec = None
    for ln, line in enumerate(open(f, encoding='utf-8'), 1):
        m = re.match(r'^(#+)\s+(\d+(?:\.\d+)*)', line)
        if m:
            sec = m.group(2)
        m = re.match(r'^\*\*(정리|명제|보조정리|따름정리|정의|관찰|주석|예)\s+\{\{(\d+[AB]?):([^}]+)\}\}(.*?)\*\*', line)
        if m:
            key = f'{m.group(2)}:{m.group(3)}'
            idx[key] = (m.group(1), sec, ch, ln, m.group(4).strip())
for k, v in idx.items():
    print('\t'.join([k, v[0], str(v[1]), v[2], str(v[3]), v[4][:400]]))
