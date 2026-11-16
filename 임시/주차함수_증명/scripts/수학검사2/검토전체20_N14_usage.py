# -*- coding: utf-8 -*-
"""N14: 장부 1.2 「쓰이는 장」·「정의 절」 열을 장 파일에서 고정 문자열로 세어 거른다(화면용 1차 걸러내기; 판정은 손으로)."""
import re, sys, io, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
ROOT = r"C:\math\임시\주차함수_증명"
SD = os.path.join(ROOT, "scripts", "수학검사2")
CH = {"1":["장1"],"2":["장2"],"3":["장3"],"4":["장4"],"5":["장5A","장5B"],"6":["장6"],"7":["장7A","장7B"],"8":["장8"],"9":["장9"],"10":["장10"],"11":["장11"]}
CMDS = ["mathcal","mathfrak","mathsf","mathrm","mathbb","mathscr","tilde","hat","bar","widetilde","overline","underline","mathbf"]
def norm(s):
    s = s.replace('\\prime', "'")
    s = re.sub(r'\s+', '', s)
    for c in CMDS:
        s = re.sub(r'\\' + c + r'([A-Za-z])', r'\\' + c + r'{\1}', s)
    s = s.replace('\\,', '').replace('\\;', '').replace('\\!', '')
    s = s.replace('\\ell', '\\ell').replace('\\dfrac','\\frac').replace('\\tfrac','\\frac')
    return s
text = {}
for k, fs in CH.items():
    text[k] = norm(''.join(open(os.path.join(ROOT, "장v2", f + ".md"), encoding='utf-8').read() for f in fs))
# section positions (### a.b) in normalized text
secpos = {}
for k, fs in CH.items():
    t = ''.join(open(os.path.join(ROOT, "장v2", f + ".md"), encoding='utf-8').read() for f in fs)
    # map section -> start offset in normalized text: normalize prefix lengths
    positions = []
    for m in re.finditer(r'^(#{3,4}) (\d+(?:\.\d+)+)', t, re.M):
        positions.append((m.group(2), len(norm(t[:m.start()]))))
    secpos[k] = positions
def section_at(k, off):
    cur = None
    for s, p in secpos[k]:
        if p <= off: cur = s
        else: break
    return cur

def split_top(s):
    out, depth, cur = [], 0, ''
    for ch in s:
        if ch in '{(': depth += 1
        if ch in '})': depth -= 1
        if ch == ',' and depth == 0:
            out.append(cur); cur = ''
        else:
            cur += ch
    out.append(cur)
    return [x.strip() for x in out if x.strip()]
def strip_args(sym):
    # remove a trailing parenthesized argument list
    sym = re.sub(r'\([^()]*\)$', '', sym)
    return sym
def core(sym):
    m = re.match(r'(\\[A-Za-z]+\{?[A-Za-z]?\}?|\\[A-Za-z]+|[A-Za-z])', sym)
    return m.group(1) if m else sym

lines = open(os.path.join(ROOT, "장부_v2.md"), encoding='utf-8').read().split('\n')
s = lines.index("### 1.2 전역 기호(라틴 소문자 / 라틴 대문자 / 그리스 / 필기체·프락투어·산세리프 / 로마체 이름·꼬리표 순)")
e = lines.index("### 1.3 국소 기호")
out = open(os.path.join(SD, "_N14_usage_out.txt"), 'w', encoding='utf-8')
for ln in lines[s:e]:
    if not ln.startswith('| $'): continue
    c = [x.strip() for x in ln.strip().strip('|').split('|')]
    symcell, defsec, used = c[0], c[3], c[4]
    syms = re.findall(r'\$(.*?)\$', symcell)
    items = []
    for g in syms: items += split_top(g)
    toks = []
    for it in items:
        a = norm(strip_args(it))
        toks.append(a)
    toks = [t for t in toks if t]
    if used == '전 장':
        used_set = set(CH)
    else:
        used_set = set(x.strip() for x in used.split(','))
    hits = {}
    first = {}
    for k in CH:
        cnt = 0; fo = None
        for t in toks:
            n = text[k].count(t)
            cnt += n
            if n:
                p = text[k].find(t)
                fo = p if fo is None else min(fo, p)
        hits[k] = cnt; first[k] = fo
    missing = [k for k in used_set if hits[k] == 0]
    extra = [k for k in CH if k not in used_set and hits[k] > 0]
    # definition section: first occurrence section in the chapter of defsec
    dchap = defsec.split('.')[0].split('(')[0].strip()
    dsec_first = None
    if dchap in CH and first.get(dchap) is not None:
        dsec_first = section_at(dchap, first[dchap])
    flag = ''
    if missing: flag += f" 적혔으나 0건: {sorted(missing, key=int)}"
    if extra: flag += f" 안 적혔으나 있음: {{{', '.join(k+':'+str(hits[k]) for k in sorted(extra, key=int))}}}"
    if dsec_first and not defsec.startswith(dsec_first.split('.')[0]+'.'+dsec_first.split('.')[1]):
        flag += f" 정의절 {defsec} vs 첫 출현 {dsec_first}"
    if flag:
        out.write(f"{symcell[:60]} | 토큰 {toks[:3]} | 쓰이는 장 {used} |{flag}\n")
out.close()
print(open(os.path.join(SD, "_N14_usage_out.txt"), encoding='utf-8').read())
