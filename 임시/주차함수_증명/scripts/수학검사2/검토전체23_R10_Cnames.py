# -*- coding: utf-8 -*-
# 부록 C 둘째 표(기록의 이름 | 이 글의 진술 | 이 글의 이름)를 진술 머리와 맞춘다.
import sys, io, os, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
base = sys.argv[1]
files = ['장1','장2','장3','장4','장5A','장5B','장6','장7A','장7B','장8','장9']
heads = {}
for fn in files:
    sec = ''
    for i, line in enumerate(open(os.path.join(base, '장v2', fn + '.md'), encoding='utf-8').read().split('\n'), 1):
        m = re.match(r'#{2,5}\s+(\d+\.\d+)', line)
        if m: sec = m.group(1)
        m = re.match(r'\*\*(정리|보조정리|명제|따름정리|정의) \{\{([0-9A-Z]+:[^}]+)\}\}', line)
        if m and not line.split('}}', 1)[1].startswith('의 증명'):
            head = line[2:line.find('**', 2)]
            # 이름 괄호: 라벨 뒤 첫 '(' 부터 표지 ' [' 앞까지
            rest = head.split('}}', 1)[1]
            k = rest.rfind(' [')
            paren = rest[:k].strip() if k >= 0 else rest.strip().rstrip('.')
            heads.setdefault(m.group(2), (fn, i, sec, m.group(1), paren, head))
txt = open(os.path.join(base, '장v2', '부록C.md'), encoding='utf-8').read()
seg = txt.split('### 기록이 결과에 붙인 이름과 이 글의 번호')[1].split('### 기록의 글자와 이 글의 글자')[0]
seen = set(); n = 0
for line in seg.split('\n'):
    if not line.startswith('| 기록 '): continue
    cells = [c.strip() for c in line.strip().strip('|').split(' | ')]
    recname, stmt, myname = cells
    m = re.match(r'(정리|보조정리|명제|따름정리|정의) \{\{([^}]+)\}\}$', stmt)
    n += 1
    if not m: print('BAD STMT', stmt); continue
    typ, lab = m.groups(); seen.add(lab)
    if lab not in heads: print('NO HEAD', lab); continue
    fn, i, sec, htyp, paren, head = heads[lab]
    probs = []
    if htyp != typ: probs.append('TYPE %s vs head %s' % (typ, htyp))
    # paren: "(이름; 기록 [r..]의 X)" 꼴
    inner = paren[1:-1] if paren.startswith('(') and paren.endswith(')') else paren
    parts = inner.split('; ', 1)
    hname = parts[0]; hrec = parts[1] if len(parts) > 1 else ''
    if hname != myname: probs.append('NAME C=[%s] head=[%s]' % (myname, hname))
    if hrec != recname: probs.append('REC C=[%s] head=[%s]' % (recname, hrec))
    if probs: print(lab, fn, 'L%d' % i, probs)
print('rows', n)
# 머리에 기록 이름이 있는데 C에 없는 것
for lab, (fn, i, sec, htyp, paren, head) in heads.items():
    if '기록 [r' in paren and lab not in seen:
        print('HEAD HAS RECNAME BUT NOT IN C:', lab, fn, 'L%d' % i, paren[:150])
