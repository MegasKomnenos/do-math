# -*- coding: utf-8 -*-
"""J14: 장 파일의 진술 머리를 뽑아 TSV로 둔다(라벨, 종류, 절, 이름 괄호, 지위 괄호, 파일:행).
또 장 파일에 나오는 모든 라벨 {{장:이름}}을 (파일, 행) 함께 센다.
"""
import re, sys, io, glob
from pathlib import Path
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
ROOT = Path(r'C:\math\임시\주차함수_증명')
files = sorted(glob.glob(str(ROOT/'장v2'/'*.md')))
HEAD = re.compile(r'^\*\*(정의|정리|명제|보조정리|따름정리|문제|추측|가설|관찰|주장|예|알고리즘)\s+\{\{([^}]+)\}\}(?!의 증명|\s*\(?[가-힣]*\)?의 증명)\s*(.*?)\*\*')
SEC = re.compile(r'^(#{2,4})\s+(.*)')
out = open(ROOT/'scripts'/'수학검사2'/'_J14_heads.tsv', 'w', encoding='utf-8')
labels = open(ROOT/'scripts'/'수학검사2'/'_J14_labels.tsv', 'w', encoding='utf-8')
nheads = 0
for f in files:
    name = Path(f).name
    sec = ''
    for ln, L in enumerate(Path(f).read_text(encoding='utf-8').splitlines(), 1):
        m = SEC.match(L)
        if m:
            sec = m.group(2).strip()
        for lab in re.findall(r'\{\{([^}]+)\}\}', L):
            labels.write(f'{lab}\t{name}\t{ln}\t{sec}\n')
        m = HEAD.match(L)
        if m:
            kind, lab, rest = m.group(1), m.group(2), m.group(3)
            # 이름 괄호와 지위 괄호
            nm = ''; st = ''
            mm = re.match(r'\s*\((.*?)\)\s*(\[.*\])?\s*\.?\s*$', rest)
            if mm:
                nm = mm.group(1); st = mm.group(2) or ''
            else:
                mm = re.match(r'\s*(\[.*\])\s*\.?\s*$', rest)
                if mm: st = mm.group(1)
                else: nm = rest
            out.write(f'{lab}\t{kind}\t{sec}\t{nm}\t{st}\t{name}:{ln}\n')
            nheads += 1
out.close(); labels.close()
print('heads', nheads)
