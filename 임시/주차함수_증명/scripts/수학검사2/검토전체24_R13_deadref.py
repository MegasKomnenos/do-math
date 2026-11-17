# -*- coding: utf-8 -*-
# R13: 장부 4절·의존지도 1.1절·대응표의 뺌 행 주석이 백틱으로 가리키는 라벨(`N:이름`)이 현행 머리에 있는지,
#      가리키는 부분 표지((가), (ㄱ) 등)가 그 진술에 있는지 본다.
import re, sys, io, importlib.util
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', newline=chr(10))
spec = importlib.util.spec_from_file_location('h', r'C:/math/임시/주차함수_증명/scripts/수학검사2/검토전체24_R13_heads.py')
h = importlib.util.module_from_spec(spec); spec.loader.exec_module(h)
hs = h.heads(); by = {x['label']: x for x in hs}
BASE = r'C:/math/임시/주차함수_증명/'
# 진술 본문(머리부터 다음 머리 전까지)
text = {}
FILES = ['장1','장2','장3','장4','장5A','장5B','장6','장7A','장7B','장8','장9','장10']
for f in FILES:
    L = open(BASE + '장v2/' + f + '.md', encoding='utf-8').read().split('\n')
    idx = [(x['line'], x['label']) for x in hs if x['file'] == f]
    for n, (ln, lab) in enumerate(idx):
        end = idx[n+1][0] - 1 if n + 1 < len(idx) else len(L)
        text[lab] = '\n'.join(L[ln-1:end])
def check(fn, a, b):
    for i, line in enumerate(open(BASE + fn, encoding='utf-8'), 1):
        if not (a <= i <= b): continue
        for m in re.finditer(r'`\(?(\d+:[A-Za-z0-9\-]+)\)?`((?:\([가-힣ㄱ-ㅎ]\))*)', line):
            lab, parts = m.group(1), m.group(2)
            pre = line[max(0, m.start()-1):m.start()+2]
            if '`(' in line[m.start():m.start()+2]:
                continue  # 죽은 라벨로 명시
            if lab not in by:
                print(fn, i, 'DEADREF', lab, '…' + line[max(0, m.start()-50):m.end()+20])
                continue
            for p in re.findall(r'\(([가-힣ㄱ-ㅎ])\)', parts):
                if ('(%s)' % p) not in text[lab]:
                    print(fn, i, 'NOPART', lab, p, '…' + line[max(0, m.start()-60):m.end()+10])
check('장부_v2.md', 693, 1184)
check('의존지도_v2.md', 284, 527)
check('대조v2/라벨_번호_대응표_1114.md', 1, 500)
