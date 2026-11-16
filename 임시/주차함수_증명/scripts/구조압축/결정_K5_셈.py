# -*- coding: utf-8 -*-
"""결정 K5 검산 1 — 처분 대상 진술·부록 D 항목의 소비처 전수(정본 장 파일·장부·지도 덧씌우기; _tmp 제외)와 삭제 범위의 글자 수.
사용: python -I 결정_K5_셈.py  (출력 결정_K5_셈_out.txt)"""
import os, re, io, sys, glob
ROOT = r'C:\math\임시\주차함수_증명'
OUT = os.path.join(ROOT, 'scripts', '구조압축', '결정_K5_셈_out.txt')
chap = sorted(p for p in glob.glob(os.path.join(ROOT, '장v2', '*.md')) if '_tmp' not in p)
files = chap + [os.path.join(ROOT, '장부_v2.md'), os.path.join(ROOT, 'dependency_map', '지도_덧씌우기.json')]
texts = {p: io.open(p, encoding='utf-8').read().split('\n') for p in files}
LABELS = ['3:old-3-1','3:old-3-2','3:old-3-3','3:old-3-4','3:old-3-5','3:old-3-6','3:peak-asymptotics',
          '4:old-4-8','4:old-4-9','7:old-6-5','9:old-7-4','9:old-7-5','5:old-5-27','7:variance-formula',
          '8:envelope-code-monotone','D:logconcavity-failure-n80','D:cumulative-logconcavity','D:crossing-small-n','D:QL-small-n']
out = []
def rel(p): return os.path.relpath(p, ROOT).replace(os.sep, '/')
out.append('# 1. 라벨 소비처 전수(정본; 자기 머리 포함; _tmp 제외)')
for lab in LABELS:
    hits = []
    for p, lines in texts.items():
        for i, ln in enumerate(lines, 1):
            c = ln.count('{{' + lab + '}}')
            if c:
                hits.append(f'{rel(p)}:{i}' + (f'(x{c})' if c > 1 else ''))
    out.append(f'{lab}\t{len(hits)}\t' + ' '.join(hits))
out.append('\n# 1b. 4:old-4-8의 항목별 인용')
for tag in ['(가)', '(나)']:
    hits = []
    for p, lines in texts.items():
        for i, ln in enumerate(lines, 1):
            if '{{4:old-4-8}}' + tag in ln:
                hits.append(f'{rel(p)}:{i}')
    out.append(f'{{{{4:old-4-8}}}}{tag}\t{len(hits)}\t' + ' '.join(hits))
# 2. 글자 수
def chars(path, a, b):
    L = texts[os.path.join(ROOT, *path.split('/'))]
    seg = L[a-1:b]
    return len(seg), sum(len(x) for x in seg) + max(0, len(seg) - 1)
RANGES = [
    ('장3 전체', '장v2/장3.md', 1, 281),
    ('장3 머리 5행(3.6·4.15(나) 연결 문단)', '장v2/장3.md', 5, 5),
    ('장3 머리 13행(3.4절 소개)', '장v2/장3.md', 13, 13),
    ('장3 3.1절(15–53)', '장v2/장3.md', 15, 53),
    ('장3 3.2절(55–129)', '장v2/장3.md', 55, 129),
    ('장3 3.3절 3.4까지(131–173)', '장v2/장3.md', 131, 173),
    ('장3 3.5와 도입(175–179)', '장v2/장3.md', 175, 179),
    ('장3 3.4절 3.6까지(181–263)', '장v2/장3.md', 181, 263),
    ('장3 3.7과 증명(265–281)', '장v2/장3.md', 265, 281),
    ('장4 4.15(나) 증명 세 문단(567–571)', '장v2/장4.md', 567, 571),
    ('장4 4.16 머리·증명(573–577)', '장v2/장4.md', 573, 577),
    ('장4 4.5 증명 k≥30000 조립(543–547 첫 문장까지)', '장v2/장4.md', 543, 546),
    ('장4 4.14 머리·증명(467–539)', '장v2/장4.md', 467, 539),
    ('장7A 7.5 묶음(49–65)', '장v2/장7A.md', 49, 65),
    ('장7B 7.37 묶음(39–61)', '장v2/장7B.md', 39, 61),
    ('장8 8.17 묶음(404–422)', '장v2/장8.md', 404, 422),
    ('장9 9.15·9.16과 산문(370–404)', '장v2/장9.md', 370, 404),
    ('장5B 5.49(138–145)', '장v2/장5B.md', 138, 145),
    ('부록D_장3 전체', '장v2/부록D_장3.md', 1, 43),
    ('부록D_장3 cumulative(25–43)', '장v2/부록D_장3.md', 25, 43),
    ('부록D_장4 crossing-small-n(50–73)', '장v2/부록D_장4.md', 50, 73),
    ('부록D_장4 QL-small-n(74–92)', '장v2/부록D_장4.md', 74, 92),
    ('장11 11.2 표(19–62)', '장v2/장11.md', 19, 62),
]
out.append('\n# 2. 범위별 행 수·글자 수(줄바꿈 포함)')
for name, path, a, b in RANGES:
    n, c = chars(path, a, b)
    out.append(f'{name}\t{n}행\t{c}자')
# 3. 11.2 표 두 열의 바이트
L11 = texts[os.path.join(ROOT, '장v2', '장11.md')]
tot = 0; two = 0; rows = 0
for ln in L11[18:62]:
    if ln.startswith('| 부록 D.'):
        rows += 1
        cells = [c for c in ln.split(' | ')]
        tot += len(ln.encode('utf-8'))
        if len(cells) >= 6:
            two += len((' | '.join(cells[4:])).encode('utf-8'))
out.append(f'\n# 3. 11.2 표: 행 {rows}, 전체 {tot}B, 뒤 두 열 {two}B ({100*two/max(1,tot):.1f}%)')
# 4. 문턱 산술
out.append('\n# 4. 문턱 유도식 검산')
import math
checks = {
 '6667 = min{k: 3k>=20001}': min(k for k in range(1, 10**5) if 3*k >= 20001) == 6667,
 '6668 = min{k: 3k-1>=20001}': min(k for k in range(1, 10**5) if 3*k-1 >= 20001) == 6668,
 '10001 = 20000/2+1': 20000//2+1 == 10001,
 '25001 = ceil((50001+1)/2)': math.ceil((50001+1)/2) == 25001,
 '6666 = 6667-1': 6667-1 == 6666,
 '3132 = 3131+1': 3131+1 == 3132,
 'k>=10000, n in {2k-1,2k} -> n>=19999 (k>=30000 -> n>=59999 포함)': (2*10000-1 == 19999) and (2*30000-1 == 59999) and (59999 >= 19999),
 '4.9(가) 11/2 < 5.642': 11/2 < 5.642,
 '4.9(가) 4*sqrt2*(1-26/10000) >= 5.642': 4*math.sqrt(2)*(1-26/10000) >= 5.642,
 '3.6 수치: lambda^8+sum/31+sum/1000 < 1/2': (lambda lam: lam**8 + sum(i*lam**(i-1) for i in range(1,9))/31 + sum((i-1)*lam**(i-1) for i in range(1,9))/1000)(751/1000) < 0.5,
}
for k, v in checks.items():
    out.append(f'{k}\t{"OK" if v else "FAIL"}')
io.open(OUT, 'w', encoding='utf-8', newline='\n').write('\n'.join(out) + '\n')
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
print('\n'.join(out))
