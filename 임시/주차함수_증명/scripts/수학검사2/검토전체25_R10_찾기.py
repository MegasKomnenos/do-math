# 고정 문자열(여러 개 가능)을 장 파일·부록에서 찾아 (파일, 행, 절, 앞뒤 문맥)을 보여 준다. 자리 찾기용.
import re, io, sys, glob
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
base = 'C:/math/임시/주차함수_증명/장v2/'
args = sys.argv[1:]
ctx = 70
scope = 'body'
while args and args[0].startswith('--'):
    a = args.pop(0)
    if a.startswith('--ctx='): ctx = int(a[6:])
    if a.startswith('--scope='): scope = a[8:]
names = ['1','2','3','4','5A','5B','6','7A','7B','8','9','10']
files = [f'장{c}.md' for c in names]
if scope in ('all', 'app'):
    app = ['부록A.md','부록B.md','부록C.md'] + sorted(__import__('os').path.basename(x) for x in glob.glob(base + '부록D_장*.md'))
    files = (files if scope == 'all' else []) + app
if scope.endswith('.md'): files = scope.split(',')
for f in files:
    sec = ''
    for i, ln in enumerate(open(base + f, encoding='utf-8').read().split('\n'), 1):
        m = re.match(r'#{2,5} (\d+(?:\.\d+)*)', ln)
        if m: sec = m.group(1)
        for a in args:
            st = 0
            while True:
                j = ln.find(a, st)
                if j < 0: break
                print(f'{f}:{i} §{sec} [{a}] …{ln[max(0,j-ctx):j+len(a)+ctx]}…')
                st = j + len(a)
