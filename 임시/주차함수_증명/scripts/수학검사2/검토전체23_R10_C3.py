# -*- coding: utf-8 -*-
# 부록 C 셋째 표 첫 열(이 글의 글자)의 $...$ 토큰이 장 파일·부록 D·부록 A에 그대로 나오는지 본다(없으면 철자 변형인지 원문으로 확인).
import sys, io, os, re, glob
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
base = sys.argv[1]
files = ['장1','장2','장3','장4','장5A','장5B','장6','장7A','장7B','장8','장9','장10'] + [os.path.basename(f)[:-3] for f in sorted(glob.glob(os.path.join(base, '장v2', '부록D_장*.md')))]
body = '\n'.join(open(os.path.join(base, '장v2', fn + '.md'), encoding='utf-8').read() for fn in files)
A = open(os.path.join(base, '장v2', '부록A.md'), encoding='utf-8').read()
def norm(s):
    BS = chr(92)
    s = s.replace('^{' + BS + 'prime}', "'").replace('^' + BS + 'prime', "'")
    s = re.sub('[' + '^' + '][{]([A-Za-z0-9' + BS + BS + ']+)[}]', lambda m: '^' + m.group(1), s)
    s = re.sub('_[{]([A-Za-z0-9])[}]', lambda m: '_' + m.group(1), s)
    return s.replace(' ', '')
nb = norm(body); nA = norm(A)
txt = open(os.path.join(base, '장v2', '부록C.md'), encoding='utf-8').read()
seg = txt.split('### 기록의 글자와 이 글의 글자')[1].split('### 영어를 함께 적은 낱말')[0]
for ln, line in enumerate(seg.split('\n')):
    if not line.startswith('| ') or line.startswith('| 이 글의') or line.startswith('|---'): continue
    cells = [c.strip() for c in line.strip().strip('|').split(' | ')]
    if len(cells) != 4: print('CELLS', len(cells), line[:70])
    for tok in re.findall(r'\$([^$]+)\$', cells[0]):
        t = norm(tok)
        inb = t in nb; inA = t in nA
        if not inb:
            print('NOT IN BODY/D%s: %s   | row: %s | rec: %s' % ('' if inA else ' (nor A)', tok, cells[0][:60], cells[1][:40]))
