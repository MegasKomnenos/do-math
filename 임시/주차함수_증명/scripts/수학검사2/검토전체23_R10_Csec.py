# -*- coding: utf-8 -*-
# 부록 C 낱말 표·영어 표의 「처음 정의된 절」을 장 파일에서의 첫 등장 절, 그리고 적힌 절 안의 등장 여부와 견준다.
import sys, io, os, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
base = sys.argv[1]
files = ['장1','장2','장3','장4','장5A','장5B','장6','장7A','장7B','장8','장9','장10']
lines = []
for fn in files:
    sec = fn.replace('장','').rstrip('AB') + '.0'
    for i, line in enumerate(open(os.path.join(base, '장v2', fn + '.md'), encoding='utf-8').read().split('\n'), 1):
        m = re.match(r'#{2,5}\s+(\d+\.\d+)(?:\.\d+)?', line)
        if m: sec = m.group(1)
        lines.append((sec, fn, i, line))
txt = open(os.path.join(base, '장v2', '부록C.md'), encoding='utf-8').read()
seg1 = txt.split('### 낱말: 이 글의 용어와 기록의 용어')[1].split('### 기록이 결과에 붙인 이름')[0]
seg2 = txt.split('### 영어를 함께 적은 낱말')[1]
def check(term, seccell, extra=''):
    secs = re.findall(r'\d+\.\d+', seccell)
    for t in [x.strip() for x in re.split(r',', re.sub(r'\([^)]*\)', '', term)) if x.strip()]:
        first = None; insec = {s: None for s in secs}
        for sec, fn, i, l in lines:
            if t in l:
                if first is None: first = (sec, fn, i)
                if sec in insec and insec[sec] is None: insec[sec] = i
        miss = [s for s, v in insec.items() if v is None]
        flag = ''
        if first is None: flag = 'NOWHERE'
        elif secs and first[0] not in secs: flag = 'EARLIER' if tuple(map(int, first[0].split('.'))) < tuple(map(int, secs[0].split('.'))) else 'LATER'
        if miss: flag += ' NOT-IN-STATED:' + ','.join(miss)
        print('%-28s stated=%-10s first=%s %s %s' % (t, seccell, first, flag, extra))
for line in seg1.split('\n'):
    if not line.startswith('| ') or line.startswith('| 이 글의') or line.startswith('|---'): continue
    cells = [c.strip() for c in line.strip().strip('|').split(' | ')]
    check(cells[0], cells[2])
print('--- 영어')
for line in seg2.split('\n'):
    if not line.startswith('| ') or line.startswith('| 이 글의') or line.startswith('|---'): continue
    cells = [c.strip() for c in line.strip().strip('|').split(' | ')]
    eng = cells[1].split('(')[0].strip()
    check(cells[0], cells[2])
    # 영어 병기 자리
    hit = [(sec, fn, i) for sec, fn, i, l in lines if eng in l]
    print('      영어 [%s] 등장: %s' % (eng, hit[:4]))
