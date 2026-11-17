# -*- coding: utf-8 -*-
# 장부 1.3절(국소 기호)에서 7.1·7.2·7.3 묶음의 행을 찾아 첫 두 칸과, 지정한 토큰 주변의 문맥을 출력한다(자리 찾기용).
import io, sys, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', newline='\n')
lines = io.open('장부_v2.md', encoding='utf-8').read().split('\n')
toks = sys.argv[1:]
for ln in range(288, 358):
    line = lines[ln]
    if not line.startswith('|'):
        continue
    cells = line.split(' | ')
    first = cells[0]
    if re.search(r'7\.[123]', first) or re.search(r'7A', first):
        print('=== 행', ln + 1, '첫 칸:', first[:200], '| 길이', len(line))
        if not toks:
            print('   둘째 칸:', cells[1][:3000] if len(cells) > 1 else '')
        for t in toks:
            for m in re.finditer(re.escape(t), line):
                s = max(0, m.start() - 160); e = min(len(line), m.end() + 260)
                print('   [%s] …%s…' % (t, line[s:e]))
