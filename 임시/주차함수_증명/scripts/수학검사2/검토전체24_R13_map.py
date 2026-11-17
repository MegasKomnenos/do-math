# -*- coding: utf-8 -*-
# R13: 의존지도 1절의 행을 장 파일에서 독립으로 다시 만들어 맞댄다
#      (절, 요지, 지위, 머리 줄 라벨, 본문 인용 라벨, 기록 식별자, 부록 D 항목, 문헌 저자).
import re, sys, io, collections
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', newline=chr(10))
BASE = r'C:/math/임시/주차함수_증명/'
FILES = ['장1','장2','장3','장4','장5A','장5B','장6','장7A','장7B','장8','장9','장10']
KINDS = '정의|정리|보조정리|명제|따름정리'
head_re = re.compile(r'^\*\*(' + KINDS + r') \{\{(\d+:[^}]+)\}\}(.*)$')
sec_re = re.compile(r'^(#{2,3}) (\d+(?:\.\d+)*)\.? ')
LAB = re.compile(r'\{\{(\d+:[^}]+)\}\}')

def bracket_after_name(rest):
    """rest: 머리 라벨 뒤의 문자열. (이름) [지위; 기록] 을 뽑는다."""
    r = rest.lstrip(); name = None
    if r.startswith('('):
        depth = 0
        for j, c in enumerate(r):
            if c == '(': depth += 1
            elif c == ')':
                depth -= 1
                if depth == 0:
                    name = r[1:j]; r = r[j+1:].lstrip(); break
    status = None; recs = None
    if r.startswith('['):
        depth = 0
        for j, c in enumerate(r):
            if c == '[': depth += 1
            elif c == ']':
                depth -= 1
                if depth == 0:
                    inside = r[1:j]; break
        # ; 로 가르되 마지막 ; 기준
        if ';' in inside:
            k = inside.rfind(';')
            status = inside[:k].strip(); recs = inside[k+1:].strip()
        else:
            status = inside.strip(); recs = ''
    return name, status, recs

CUT = len(sys.argv) > 1 and sys.argv[1] == 'cut'
blocks = []   # (label, kind, file, line, sec, name, status, recs, headline, bodytext)
cur = None
deferred = collections.defaultdict(list)
defcur = None
for f in FILES:
    sec = None; cur = None; defcur = None
    for ln, line in enumerate(open(BASE + '장v2/' + f + '.md', encoding='utf-8'), 1):
        line = line.rstrip('\n')
        m = sec_re.match(line)
        if m and m.group(1) in ('##', '###'):
            if m.group(1) == '###': sec = m.group(2)
            if CUT: cur = None; defcur = None
        m = head_re.match(line)
        if m:
            kind, lab, rest = m.groups()
            if rest.startswith('의 증명'):
                cur = None
                defcur = [lab, f, ln, [line]]
                deferred[lab].append(defcur)
                continue
            name, status, recs = bracket_after_name(rest)
            cur = dict(label=lab, kind=kind, file=f, line=ln, sec=sec, name=name, status=status, recs=recs, head=line, body=[])
            blocks.append(cur); defcur = None
            continue
        if defcur is not None: defcur[3].append(line)
        elif cur is not None: cur['body'].append(line)

# 10.2 / 10.3 표
D_of = collections.defaultdict(list); Lit_of = collections.defaultdict(list)
for line in open(BASE + '장v2/장10.md', encoding='utf-8'):
    if not line.startswith('|'): continue
    c = [x.strip() for x in line.strip().strip('|').split(' | ')]
    if c[0].startswith('부록 D.{{'):
        d = re.search(r'\{\{(D:[^}]+)\}\}', c[0]).group(1)
        for lab in LAB.findall(c[1]): D_of[lab].append((d, c[2]))
    elif len(c) == 3 and not c[0].startswith('---') and c[0] not in ('문헌',):
        for lab in LAB.findall(c[2]): Lit_of[lab].append(c[0][:14])

# 지도 표
rows = {}
order = []
for ln, line in enumerate(open(BASE + '의존지도_v2.md', encoding='utf-8'), 1):
    if ln > 283: break
    if not line.startswith('| `{{'): continue
    c = [x.strip() for x in line.strip().strip('|').split(' | ')]
    lab = c[0].strip('`')[2:-2]
    rows[lab] = (ln, c); order.append(lab)
print('map rows', len(rows), 'blocks', len(blocks), 'order equal', order == [b['label'] for b in blocks])
allin = set()
for b in blocks:
    lab = b['label']
    if lab not in rows: print('NOROW', lab); continue
    ln, c = rows[lab]
    if len(c) != 10: print('CELLS', ln, lab, len(c)); continue
    _, sec, old, gist, status, inputs, recs, lit, dcol, note = c
    if sec != b['sec']: print('SEC', ln, lab, sec, b['sec'])
    if b['name'] is not None and gist != b['name']: print('GIST', ln, lab, '\n   M:', gist, '\n   H:', b['name'])
    st = '정의' if (b['kind'] == '정의' and (b['status'] is None or re.fullmatch(r'(r[0-9a-f]{7}(, )?)+', b['status'] or ''))) else b['status']
    if b['kind'] == '정의' and b['status'] is not None and not re.fullmatch(r'(r[0-9a-f]{7}(, )?)+', b['status']):
        st = b['status']
    if (st or '') != status: print('STATUS', ln, lab, '\n   M:', status, '\n   H:', st)
    # 머리 줄 라벨
    hl = []
    for x in LAB.findall(b['head']):
        if x != lab and x not in hl: hl.append(x)
    body = '\n'.join(b['body'])
    for d in deferred.get(lab, []): body += '\n' + '\n'.join(d[3])
    bl = []
    for x in LAB.findall(body):
        if x != lab and x not in hl and x not in bl: bl.append(x)
    if '본문 인용:' in inputs:
        a, bb = inputs.split('본문 인용:')
    else: a, bb = inputs, ''
    mh = LAB.findall(a); mb = LAB.findall(bb)
    allin |= set(mh) | set(mb)
    if sorted(mh) != sorted(hl): print('HEADIN', ln, lab, '\n   M:', mh, '\n   H:', hl)
    if set(mb) != set(bl):
        print('BODYIN', ln, lab, '| 지도에만:', sorted(set(mb) - set(bl)), '| 장에만:', sorted(set(bl) - set(mb)))
    # 기록 식별자
    hr = re.findall(r'r[0-9a-f]{7}', b['recs'] or (b['status'] if b['kind'] == '정의' and b['status'] else '') or '')
    mr = re.findall(r'r[0-9a-f]{7}', recs)
    if set(hr) - set(mr) or (set(mr) - set(hr) and len(hr) == 0 and False):
        print('RECS', ln, lab, '| 머리에만:', sorted(set(hr) - set(mr)), '| 지도:', recs[:120])
    if set(mr) - set(hr):
        print('RECS+', ln, lab, '| 지도에만:', sorted(set(mr) - set(hr)), '| 머리:', b['recs'])
    # 부록 D
    md = re.findall(r'\{\{(D:[^}]+)\}\}', dcol)
    hd = [d for d, g in D_of.get(lab, [])]
    if sorted(md) != sorted(hd): print('DCOL', ln, lab, '| 지도:', md, '| 10.2:', hd)
    else:
        for d, g in D_of.get(lab, []):
            if ('{{%s}}(%s)' % (d, g)) not in dcol: print('DGRADE', ln, lab, d, '| 10.2 등급:', g, '| 지도:', dcol[:200])
    # 문헌 수
    ml = 0 if lit == '—' else len([x for x in re.split(r'\); ', lit) if x.strip()])
    if (lit == '—') != (len(Lit_of.get(lab, [])) == 0): print('LIT', ln, lab, '| 지도:', lit[:80], '| 10.3:', Lit_of.get(lab))
    if b['line'] and '뒤로 미룬 증명' in note:
        mm = re.search(r'뒤로 미룬 증명 (\S+?)\.md:(\d+)', note)
        d = deferred.get(lab)
        if not d: print('DEFER?', ln, lab, note[:80])
        elif mm and (mm.group(1) != d[0][1] or int(mm.group(2)) != d[0][2]): print('DEFERLINE', ln, lab, mm.groups(), d[0][1:3])
    elif deferred.get(lab): print('DEFER-MISSING-NOTE', ln, lab)
print('distinct input labels', len(allin))
