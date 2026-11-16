# -*- coding: utf-8 -*-
"""J14: 장부 3절 낱말 사전의 「첫 정의 절」을 장 파일의 첫 출현 절과 견준다.
자리를 찾는 용도이며 판단은 사람이 한다.
"""
import re, sys, io
from pathlib import Path
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
ROOT = Path(r'C:\math\임시\주차함수_증명')
ORDER = ['장1','장2','장3','장4','장5A','장5B','장6','장7A','장7B','장8','장9','장10','장11']
SEC = re.compile(r'^#{2,4}\s+(\d+)(?:\.(\d+))?(?:\.(\d+))?')
# 장별 (절 튜플, 행, 본문) 목록
docs = []
for f in ORDER:
    sec = (int(re.sub(r'\D','',f)),)
    for ln, L in enumerate((ROOT/'장v2'/(f+'.md')).read_text(encoding='utf-8').splitlines(), 1):
        m = SEC.match(L)
        if m:
            sec = tuple(int(x) for x in m.groups() if x)
        docs.append((sec, f, ln, L))

lines = (ROOT/'장부_v2.md').read_text(encoding='utf-8').splitlines()
rows = [L for L in lines[508:726] if L.startswith('| ')]
def parse_secs(s):
    out = []
    for m in re.finditer(r'(\d+)(?:\.(\d+))?(?:\.(\d+))?', s):
        out.append(tuple(int(x) for x in m.groups() if x))
    return out
for L in rows:
    cols = [c.strip() for c in L.strip().strip('|').split('|')]
    if len(cols) < 4: continue
    words_raw, meaning, first, old = cols[0], cols[1], cols[2], cols[3]
    if '일반어' in first or first.startswith('—'): continue
    decl = parse_secs(first)
    if not decl: continue
    dmin = min(decl)
    words = [w.strip() for w in re.split(r',\s*', words_raw)]
    for w in words:
        w2 = re.sub(r'\$[^$]*\$', '', w).strip()
        w2 = w2.replace('(오른쪽·왼쪽)', '').strip()
        if len(w2) < 2: continue
        # 첫 출현
        hit = None
        for sec, f, ln, text in docs:
            if w2 in text:
                hit = (sec, f, ln, text); break
        if hit is None:
            print(f'[없음] 「{w2}」 선언 {first}')
            continue
        sec, f, ln, text = hit
        if sec < dmin:
            i = text.find(w2)
            print(f'[앞섬] 「{w2}」 선언 {first} | 첫 출현 {f}:{ln} 절 {".".join(map(str,sec))} …{text[max(0,i-40):i+40]}…')
