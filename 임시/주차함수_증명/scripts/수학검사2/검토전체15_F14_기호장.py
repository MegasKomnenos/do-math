# -*- coding: utf-8 -*-
"""F14: 장부 1.2 「쓰이는 장」·「정의 절」 대 장 파일의 실제 출현(수식 구간 안) 셈.
자리 찾기·셈만 한다. 출력은 사람이 읽고 판정한다."""
import re, sys, io, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
ROOT = r'C:\math\임시\주차함수_증명'
CH_FILES = [('장1','1'),('장2','2'),('장3','3'),('장4','4'),('장5A','5'),('장5B','5'),('장6','6'),('장7A','7'),('장7B','7'),('장8','8'),('장9','9'),('장10','10'),('장11','11')]
def rd(p):
    with open(p, encoding='utf-8') as f:
        return f.read()
# 수식 구간 모으기(장별, 절별)
math_by_ch = {}
math_by_sec = {}   # (ch, sec) -> text
sec_re = re.compile(r'^(#{2,4}) (\d+(?:\.\d+)*)[ .]')
for fn, ch in CH_FILES:
    txt = rd(os.path.join(ROOT, '장v2', fn + '.md'))
    cur = ch + '.0'
    for line in txt.split('\n'):
        m = sec_re.match(line)
        if m:
            cur = m.group(2)
        spans = re.findall(r'\$\$(.+?)\$\$|\$(.+?)\$', line)
        s = ' '.join(a or b for a, b in spans)
        math_by_ch[ch] = math_by_ch.get(ch, '') + ' ' + s
        key = (ch, '.'.join(cur.split('.')[:2]))
        math_by_sec[key] = math_by_sec.get(key, '') + ' ' + s

jb = rd(os.path.join(ROOT, '장부_v2.md'))
s12 = jb[jb.index('### 1.2 전역 기호'):jb.index('### 1.3 국소 기호')]
rows = []
for line in s12.split('\n'):
    m = re.match(r'^\| (.*?) \| (.*?) \| (.*?) \| (.*?) \| (.*?) \| (.*?) \| (.*?) \|$', line)
    if not m or m.group(1).startswith('글자') or m.group(1).startswith('---'):
        continue
    rows.append(m.groups())

def pat_for(glyph, font):
    g = glyph.strip().strip('$')
    first = g.split(',')[0].strip().strip('$')
    pats = []
    base = font.split('·')[0]
    kind = font.split('·', 1)[1] if '·' in font else ''
    if '프락투어' in kind:
        pats.append(r'\\mathfrak\s*\{?' + re.escape(base))
    elif '필기체' in kind:
        pats.append(r'\\mathcal\s*\{?' + re.escape(base))
    elif '산세리프' in kind:
        pats.append(r'\\mathsf\s*\{?' + re.escape(base) + r'(?![A-Za-z])')
    elif '로마체' in kind:
        pats.append(r'\\mathrm\s*\{' + re.escape(base) + r'\}')
    elif '칠판체' in kind:
        pats.append(r'\\Pr' if 'Pr' in base else r'\\mathbb')
    elif '꼬리표' in kind:
        pats.append(re.escape(first))
    else:
        if base.startswith('\\'):
            pats.append(re.escape(base) + r'(?![A-Za-z])')
        else:
            # italic Latin: base followed by _ ^ ( or bare
            pats.append(r'(?<![A-Za-z\\])' + re.escape(base) + r'(?=\s*[_^(])')
    return first, pats

def pretty_first(first):
    return first

print('| 글자 | 선언 | 첫 글자 고정열 출현 장 | 느슨한(바탕 글자·글자체) 출현 장 | 정의 절 | 첫 글자 첫 출현 절 |')
for glyph, font, meaning, defsec, chs, old, rec in rows:
    first, pats = pat_for(glyph, font)
    declared = chs.strip()
    exact = []
    loose = []
    for ch in ['1','2','3','4','5','6','7','8','9','10','11']:
        t = math_by_ch.get(ch, '')
        if first and first in t:
            exact.append(ch)
        if any(re.search(p, t) for p in pats):
            loose.append(ch)
    # first occurrence section of exact string
    firstsec = ''
    for (ch, sec), t in math_by_sec.items():
        if first in t:
            if not firstsec or [int(x) for x in sec.split('.')] < [int(x) for x in firstsec.split('.')]:
                firstsec = sec
    decl_set = set(re.findall(r'\d+', declared)) if '전 장' not in declared else set(['1','2','3','4','5','6','7','8','9','10','11'])
    flag = ''
    if decl_set != set(exact) and decl_set != set(loose):
        flag = ' **'
    print(f'| {glyph} | {declared} | {",".join(exact)} | {",".join(loose)} | {defsec} | {firstsec}{flag} |')
