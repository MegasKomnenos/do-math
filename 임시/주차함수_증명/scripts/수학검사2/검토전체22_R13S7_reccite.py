# 주어진 기록 식별자가 어느 장 파일(본문·부록 D)에 몇 번 인용되는지
import io, sys, glob, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
files = ['장1','장2','장3','장4','장5A','장5B','장6','장7A','장7B','장8','장9','장10','부록D_장2','부록D_장3','부록D_장4','부록D_장5A','부록D_장7A','부록D_장7B','부록D_장8','부록D_장9']
txt = {f: open('장v2/%s.md' % f, encoding='utf-8').read() for f in files}
for r in sys.argv[1:]:
    print(r, ' '.join('%s:%d' % (f, txt[f].count(r)) for f in files if txt[f].count(r)))
