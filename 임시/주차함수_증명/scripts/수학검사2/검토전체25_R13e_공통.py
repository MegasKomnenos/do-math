# -*- coding: utf-8 -*-
# 장 파일에서 수식 조각을 (행 번호, 조각)으로 뽑는다. 여러 줄에 걸친 $$…$$ 도 한 조각으로 잡는다.
import io, re
BS = chr(92)
FILES = {1:['장1'],2:['장2','부록D_장2'],3:['장3','부록D_장3'],4:['장4','부록D_장4'],5:['장5A','장5B','부록D_장5A'],6:['장6'],
         7:['장7A','장7B','부록D_장7A','부록D_장7B'],8:['장8','부록D_장8'],9:['장9','부록D_장9'],10:['장10']}
_cache = {}
def segments(fname):
    if fname in _cache: return _cache[fname]
    txt = io.open('장v2/%s.md' % fname, encoding='utf-8').read()
    out = []
    # 먼저 $$…$$ (여러 줄 허용), 그다음 남은 글에서 $…$ (한 줄 안)
    pos = 0; rest = []
    for m in re.finditer(r'\$\$.*?\$\$', txt, flags=re.S):
        out.append((txt.count('\n', 0, m.start()) + 1, m.group(0)))
        rest.append((pos, txt[pos:m.start()])); pos = m.end()
    rest.append((pos, txt[pos:]))
    for off, chunk in rest:
        for m in re.finditer(r'\$[^$\n]*\$', chunk):
            out.append((txt.count('\n', 0, off + m.start()) + 1, m.group(0)))
    out.sort()
    _cache[fname] = out
    return out
def strip_fonts(sg):
    prev = None
    while prev != sg:
        prev = sg
        sg = re.sub(re.escape(BS) + r'(mathrm|operatorname|text|mathsf|mathcal|mathfrak|mathbb|mathbf|mathscr)\s*\{[^{}]*\}', '¤', sg)
    sg = re.sub(re.escape(BS) + r'(mathrm|mathsf|mathcal|mathfrak|mathbb|mathbf|mathscr)\s+[A-Za-z]', '¤', sg)
    return sg
