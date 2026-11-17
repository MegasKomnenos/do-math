# -*- coding: utf-8 -*-
"""Z4(21차 수리): 장 파일의 수식 안 맨 이탤릭 라틴 대문자(명령·로마체·산세리프·프락투어·필기체·칠판체 밖)를 센다.
읽기 전용. 사용: python -I 수리전체21_Z4_글자셈.py 파일...  [--show=C,G]"""
import io, re, sys
from collections import Counter

BS = chr(92)
show = set()
files = []
for a in sys.argv[1:]:
    if a.startswith('--show='):
        show = set(a[7:].split(','))
    else:
        files.append(a)


def math_segments(text):
    segs = []
    for m in re.finditer(r'[$][$](.+?)[$][$]|[$](.+?)[$]', text, flags=re.S):
        segs.append((m.start(), m.group(1) or m.group(2)))
    return segs


STY = '(mathrm|mathsf|mathfrak|mathcal|mathbb|mathbf|text|operatorname|mathscr)'
P1 = re.compile(re.escape(BS) + STY + r'\s*[{][^{}]*[}]')
P2 = re.compile(re.escape(BS) + STY + r'\s*[A-Za-z]')
P3 = re.compile(re.escape(BS) + r'[A-Za-z]+')


def strip(seg):
    s = P1.sub(' ', seg)
    s = P2.sub(' ', s)
    s = P3.sub(' ', s)
    return s


for f in files:
    text = io.open(f, encoding='utf-8').read()
    cnt = Counter()
    where = {}
    for pos, seg in math_segments(text):
        s = strip(seg)
        for ch in re.findall(r'[A-Z]', s):
            cnt[ch] += 1
            if ch in show:
                line = text.count('\n', 0, pos) + 1
                where.setdefault(ch, []).append((line, seg[:100].replace('\n', ' ')))
    print(f, dict(sorted(cnt.items())))
    for ch in sorted(where):
        seen = set()
        for line, seg in where[ch]:
            if (line, seg) in seen:
                continue
            seen.add((line, seg))
            print('   ', ch, line, seg)
