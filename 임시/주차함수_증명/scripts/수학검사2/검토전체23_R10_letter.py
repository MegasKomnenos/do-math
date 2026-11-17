# -*- coding: utf-8 -*-
# 수식 안에서 홀로 선 라틴 글자(앞뒤가 영문자·역슬래시가 아닌 것)의 절별 등장 수와 첫 문맥. 사용: letter.py <base> <글자> [파일,파일]
import re, sys, io, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
base = sys.argv[1]; ch = sys.argv[2]
files = sys.argv[3].split(',') if len(sys.argv) > 3 else ['장1','장2','장3','장4','장5A','장5B','장6','장7A','장7B','장8','장9']
BS = chr(92)
pat = re.compile('(?<![A-Za-z' + BS + BS + '])' + re.escape(ch) + '(?![A-Za-z])')
for fn in files:
    sec = ''; cnt = {}
    for i, line in enumerate(open(os.path.join(base, '장v2', fn + '.md'), encoding='utf-8').read().split('\n'), 1):
        m = re.match(r'#{2,5}\s+(\d+\.\d+)', line)
        if m: sec = m.group(1)
        # 수식 구간만
        for seg in re.finditer(r'\$\$.*?\$\$|\$[^$]*\$', line):
            for mm in pat.finditer(seg.group(0)):
                a = seg.start() + mm.start()
                if line[max(0,a-8):a].rstrip().endswith(('mathsf','mathfrak','mathrm','mathcal','mathbf')): continue
                cnt.setdefault(sec, []).append((i, line[max(0, a-70):a+70]))
        if line.strip() and not line.startswith('$$') and '$' not in line:
            pass
    for s, v in cnt.items():
        print(fn, s, len(v), '| L%d …%s…' % v[0])
