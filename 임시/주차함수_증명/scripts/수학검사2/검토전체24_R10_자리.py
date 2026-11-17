# 파일:행 과 열쇠말을 받아 그 행이 든 절, 가장 가까운 앞의 굵은 머리(진술·증명), 열쇠말 둘레의 글귀를 찍는다. 자리 찾기용.
import re, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', newline='\n')
base = r'C:/math/임시/주차함수_증명/장v2/'
W = 220
args = sys.argv[1:]
for a in args:
    f, ln, key = a.split('@')
    ln = int(ln)
    lines = open(base+f+'.md', encoding='utf-8').read().split('\n')
    sec = None; head = None; hl = None
    for i in range(ln):
        l = lines[i]
        if l.startswith('#'): sec = l; head = None
        m = re.match(r'^\*\*((정리|명제|보조정리|따름정리|정의)[^*]*?|증명[^*]*?|[^*]{0,80}의 증명[^*]*?)\*\*', l)
        if m: head = m.group(0)[:160]; hl = i+1
    l = lines[ln-1]
    print(f'--- {f}:{ln} | {sec} | 머리({hl}): {head}')
    for m in re.finditer(re.escape(key), l):
        s = max(0, m.start()-W); e = min(len(l), m.end()+W)
        print('    …' + l[s:e] + '…')
