# -*- coding: utf-8 -*-
# 장 파일의 수식 안에서 변수 글자가 나오는 수를 장별로 센다(자리 찾기 전용; 판정은 원문을 읽고 한다).
# 쓰임: python -I 검토전체25_R13_letters.py [글자 ...] [--show 파일 글자]
import re, sys, io, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', newline='\n')
base = r'C:/math/임시/주차함수_증명/장v2'
files = ['장1','장2','장3','장4','장5A','장5B','장6','장7A','장7B','장8','장9','장10','부록D_장2','부록D_장3','부록D_장4','부록D_장5A','부록D_장7A','부록D_장7B','부록D_장8','부록D_장9']
BS = chr(92)
FONT = re.compile(r'\\(mathrm|mathsf|text|operatorname|mathfrak|mathcal|mathbb|mathbf|mathscr|mathtt)\s*\{[^{}]*\}')
FONT1 = re.compile(r'\\(mathrm|mathsf|mathfrak|mathcal|mathbb|mathbf|mathscr)\s*[A-Za-z]')
CMD = re.compile(r'\\[A-Za-z]+')

def maths(text):
    out = []
    for m in re.finditer(r'\$\$(.+?)\$\$|\$([^$\n]+?)\$', text, re.S):
        out.append((m.start(), m.group(1) or m.group(2)))
    return out

def strip_fonts(s):
    s = FONT.sub(' ', s)
    s = FONT1.sub(' ', s)
    return s

def count(L, s):
    s2 = strip_fonts(s)
    if L.startswith(BS):
        return len(re.findall(re.escape(L) + r'(?![A-Za-z])', s2))
    s3 = CMD.sub(' ', s2)
    return len(re.findall(r'(?<![A-Za-z])' + re.escape(L) + r'(?![A-Za-z])', s3))

args = sys.argv[1:]
if '--show' in args:
    i = args.index('--show')
    f, L = args[i + 1], args[i + 2]
    t = io.open(os.path.join(base, f + '.md'), encoding='utf-8').read()
    for pos, s in maths(t):
        if count(L, s):
            ln = t.count('\n', 0, pos) + 1
            print(ln, s.replace('\n', ' ')[:160])
    sys.exit(0)
letters = args or ['n','m','t','N','k',BS + 'ell','y','Y','i','j','u','v','r',BS + 'nu','d','q']
print('file'.ljust(12), ' '.join(x.rjust(5) for x in letters))
for f in files:
    t = io.open(os.path.join(base, f + '.md'), encoding='utf-8').read()
    ms = maths(t)
    print(f.ljust(12), ' '.join(str(sum(count(L, s) for _, s in ms)).rjust(5) for L in letters))
