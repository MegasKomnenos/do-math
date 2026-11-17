# -*- coding: utf-8 -*-
# R13: 장부 3절 낱말의 「첫 정의 절」을 장 파일에서 그 낱말이 처음 나오는 절(1장 개관·장 머리 제외)과 맞댄다.
#      처음 나오는 절이 정의 절보다 앞이면 후보(낱말이 일반어로 먼저 쓰였을 수 있으므로 원문 확인).
import re, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', newline=chr(10))
BASE = r'C:/math/임시/주차함수_증명/'
FILES = ['장1','장2','장3','장4','장5A','장5B','장6','장7A','장7B','장8','장9','장10']
sec_re = re.compile(r'^(#{2,3}) (\d+(?:\.\d+)*)\.? ')
lines = []   # (sec, file, ln, text-without-math)
for f in FILES:
    sec = None
    for ln, line in enumerate(open(BASE + '장v2/' + f + '.md', encoding='utf-8'), 1):
        m = sec_re.match(line)
        if m:
            sec = m.group(2) + ('.0' if m.group(1) == '##' else '')
        lines.append((sec, f, ln, line))
def key(s):
    return [int(x) for x in s.split('.')]
def first(word, skip_intro=True):
    for sec, f, ln, t in lines:
        if sec is None: continue
        if skip_intro and (sec.startswith('1.4') or sec.startswith('1.5') or sec.endswith('.0')): continue
        if word in t: return sec, f, ln
    return None
L = open(BASE + '장부_v2.md', encoding='utf-8').read().split(chr(10))
for i in range(452, 689):
    c = [x.strip() for x in L[i-1].strip().strip('|').split(' | ')]
    if len(c) < 4: continue
    secs = re.findall(r'\d+\.\d+', c[2])
    words = [w.strip() for w in re.split(r', ', c[0]) if w.strip()]
    for w in words:
        w0 = re.sub(r'\(.*?\)', '', w).strip()
        if '$' in w0 or len(w0) < 2: continue
        fo = first(w0)
        if fo is None:
            fo2 = first(w0, skip_intro=False)
            print(i, w0, '| 정의 절', c[2], '| 본문(개관·머리 밖)에 없음', '| 개관·머리 포함:', fo2)
            continue
        if secs:
            dmin = min(secs, key=key)
            fsec = '.'.join(fo[0].split('.')[:2])
            if key(fsec) < key(dmin) and not c[2].startswith('—') and '부록 D' not in c[2]:
                print(i, w0, '| 정의 절', c[2], '| 처음 나오는 곳', fo)
