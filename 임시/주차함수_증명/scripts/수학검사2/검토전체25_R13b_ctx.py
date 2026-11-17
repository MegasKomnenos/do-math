# -*- coding: utf-8 -*-
"""R13b 검산 보조: 고정 문자열의 출현 자리를 행 번호와 주변 문맥으로 찍는다.
사용: python -I 검토전체25_R13b_ctx.py <파일들(쉼표)> <토큰> [앞뒤 폭=80] [최대 건수=40]
      python -I 검토전체25_R13b_ctx.py -c <파일들(쉼표)> <토큰1> <토큰2> ...   (건수만)
      python -I 검토전체25_R13b_ctx.py -l <파일> <시작행> <끝행> [행당 최대 글자]
"""
import io, sys
sys.stdout.reconfigure(encoding='utf-8')
BASE = 'C:/math/임시/주차함수_증명/'
ALIAS = {'1': '장v2/장1.md', '2': '장v2/장2.md', '3': '장v2/장3.md', '4': '장v2/장4.md',
         '5A': '장v2/장5A.md', '5B': '장v2/장5B.md', '6': '장v2/장6.md', '7A': '장v2/장7A.md',
         '7B': '장v2/장7B.md', '8': '장v2/장8.md', '9': '장v2/장9.md', '10': '장v2/장10.md',
         'A': '장v2/부록A.md', 'B': '장v2/부록B.md', 'C': '장v2/부록C.md',
         'D2': '장v2/부록D_장2.md', 'D3': '장v2/부록D_장3.md', 'D4': '장v2/부록D_장4.md',
         'D5A': '장v2/부록D_장5A.md', 'D7A': '장v2/부록D_장7A.md', 'D7B': '장v2/부록D_장7B.md',
         'D8': '장v2/부록D_장8.md', 'D9': '장v2/부록D_장9.md', 'L': '장부_v2.md'}
ALL = ['1','2','3','4','5A','5B','6','7A','7B','8','9','10','A','B','C','D2','D3','D4','D5A','D7A','D7B','D8','D9']
def files(spec):
    if spec == 'all': return ALL
    if spec == 'body': return ALL[:12]
    return spec.split(',')
def lines(f):
    return io.open(BASE + ALIAS.get(f, f), encoding='utf-8', newline='').read().split('\n')
a = sys.argv[1:]
if a[0] == '-c':
    fs = files(a[1])
    for tok in a[2:]:
        out = []
        for f in fs:
            n = sum(l.count(tok) for l in lines(f))
            if n: out.append('%s:%d' % (f, n))
        print(repr(tok), '->', ' '.join(out) if out else '0건')
elif a[0] == '-l':
    L = lines(a[1]); s, e = int(a[2]), int(a[3]); mx = int(a[4]) if len(a) > 4 else 100000
    for i in range(s - 1, min(e, len(L))):
        print(i + 1, L[i][:mx])
else:
    fs = files(a[0]); tok = a[1]; w = int(a[2]) if len(a) > 2 else 80; mx = int(a[3]) if len(a) > 3 else 40
    cnt = 0
    for f in fs:
        for i, l in enumerate(lines(f)):
            p = l.find(tok)
            while p >= 0:
                cnt += 1
                if cnt <= mx:
                    print('%s:%d: …%s…' % (f, i + 1, l[max(0, p - w):p + len(tok) + w]))
                p = l.find(tok, p + len(tok))
    print('총', cnt, '건')
