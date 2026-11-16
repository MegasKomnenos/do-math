# -*- coding: utf-8 -*-
"""K14: 장부 1.2 「쓰이는 장」 대조 — 바탕 글자+첫 장식을 열쇠로 장 파일을 검색한다(거짓 양성·음성은 손으로 본다)."""
import re, sys, io, os, collections
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
B = r'C:\math\임시\주차함수_증명'
order = ['장1','장2','장3','장4','장5A','장5B','장6','장7A','장7B','장8','장9','장10','장11']
chapof = {'장1':'1','장2':'2','장3':'3','장4':'4','장5A':'5','장5B':'5','장6':'6','장7A':'7','장7B':'7','장8':'8','장9':'9','장10':'10','장11':'11'}
BS = chr(92)
def norm(s): return re.sub(r'[\s{}]', '', s)
texts = {}
for ch in order:
    L = open(os.path.join(B, '장v2', ch + '.md'), encoding='utf-8').read().split('\n')
    sec = ''; out = []
    for i, ln in enumerate(L, 1):
        m = re.match(r'^(#{2,4})\s+(\d+(?:\.\d+)*)', ln)
        if m: sec = m.group(2)
        out.append((sec, i, norm(ln)))
    texts[ch] = out
rows = []; on = False
for line in open(os.path.join(B, '장부_v2.md'), encoding='utf-8'):
    if line.startswith('### 1.2'): on = True
    elif line.startswith('### 1.3'): on = False
    if on and line.startswith('| $'):
        c = [x.strip() for x in line.strip().strip('|').split('|')]
        rows.append(dict(glyph=c[0], defsec=c[3], chs=c[4]))
FONTS = r'(?:mathcal|mathfrak|mathsf|mathrm|mathbb|tilde|hat|bar)'
base_re = re.compile(r'^(' + BS + BS + FONTS + BS + BS + '[A-Za-z]+|' + BS + BS + FONTS + '[A-Za-z]+|' + BS + BS + '[A-Za-z]+|[A-Za-z]+)')
dec_re = re.compile(r'^([_^])(' + BS + BS + r'[A-Za-z]+|\*?[A-Za-z0-9]+)')
def keyof(p):
    m = base_re.match(p)
    if not m: return None
    base = m.group(1); rest = p[len(base):]
    core = re.sub('^' + BS + BS + FONTS, '', base).lstrip(BS)
    single = len(core) <= 1 or core == 'ell'
    m2 = dec_re.match(rest)
    if single and m2: return base + m2.group(1) + m2.group(2)
    if single and not m2 and rest.startswith('('): return base + '('
    return base
for r in rows:
    ps = [norm(x) for x in re.findall(r'\$([^$]+)\$', r['glyph'])]
    ks = sorted(set(k for k in (keyof(p) for p in ps) if k))
    found = collections.OrderedDict()
    for k in ks:
        for ch in order:
            for sec, i, ln in texts[ch]:
                if k in ln:
                    found.setdefault(chapof[ch], []).append((k, ch, sec, i)); break
    claim = [x.strip() for x in r['chs'].replace('전 장', '1,2,3,4,5,6,7,8,9,10,11').split(',') if x.strip()]
    fch = sorted(found, key=int)
    if set(fch) != set(claim):
        extra = sorted(set(fch) - set(claim), key=int); missing = sorted(set(claim) - set(fch), key=int)
        print(r['glyph'][:55].ljust(55), '| 정의', r['defsec'][:12].ljust(12), '| 장부:', r['chs'].ljust(22), '| 열쇠', ks, '| 장부에 없는 장:', [(c, found[c][0][1], found[c][0][2], found[c][0][3]) for c in extra], '| 검색 못 함:', missing)
