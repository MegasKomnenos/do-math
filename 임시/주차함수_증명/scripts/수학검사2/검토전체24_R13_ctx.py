# -*- coding: utf-8 -*-
# R13: 기호(고정 문자열 여러 철자)가 주어진 장에서 처음 나오는 자리의 앞뒤를 보인다.
import re, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', newline=chr(10))
BASE = r'C:/math/임시/주차함수_증명/장v2/'
CH = {1:['장1'],2:['장2','부록D_장2'],3:['장3','부록D_장3'],4:['장4','부록D_장4'],5:['장5A','장5B','부록D_장5A'],6:['장6'],7:['장7A','장7B','부록D_장7A','부록D_장7B'],8:['장8','부록D_장8'],9:['장9','부록D_장9'],10:['장10']}
def show(ch, pats, n=2, w=90):
    tot = 0; shown = 0
    for f in CH[ch]:
        for ln, line in enumerate(open(BASE + f + '.md', encoding='utf-8'), 1):
            for p in pats:
                st = 0
                while True:
                    j = line.find(p, st)
                    if j < 0: break
                    tot += 1
                    if shown < n:
                        print('   [%s:%d] …%s…' % (f, ln, line[max(0, j - w):j + len(p) + w].replace('\n', ' ')))
                        shown += 1
                    st = j + len(p)
    print('   => 장', ch, pats, '총', tot)
if __name__ == '__main__':
    # argv: ch  pat1 pat2 ...
    args = sys.argv[1:]
    n = 2
    if args[0].startswith('-n'):
        n = int(args[0][2:]); args = args[1:]
    show(int(args[0]), args[1:], n=n)
