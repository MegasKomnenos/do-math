# -*- coding: utf-8 -*-
# R13: 장부 4절을 장 파일 머리·대응표·의존지도(1절 「첫 판 번호」, 1.1절)와 맞댄다.
import re, sys, io, importlib.util, collections
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', newline=chr(10))
spec = importlib.util.spec_from_file_location('h', r'C:/math/임시/주차함수_증명/scripts/수학검사2/검토전체24_R13_heads.py')
h = importlib.util.module_from_spec(spec); spec.loader.exec_module(h)
hs = h.heads(); by = {x['label']: x for x in hs}
BASE = r'C:/math/임시/주차함수_증명/'
L = open(BASE + '장부_v2.md', encoding='utf-8').read().split('\n')
live = {}; dead = {}; order = []
for i in range(693, 1185):
    line = L[i-1]
    if not line.startswith('|'): print('NONROW', i, line[:80]); continue
    c = [x.strip() for x in line.strip().strip('|').split(' | ')]
    if len(c) != 6:
        # 빈 칸(|  |)이 있어 split이 어긋날 수 있다 -> 정규식으로 다시
        c = [x.strip() for x in re.split(r'\s*\|\s*', line.strip().strip('|'))]
    if len(c) != 6: print('CELLS', i, len(c), line[:120]); continue
    old, kind, name, rec, sec, lab = c
    if lab.startswith('{{'):
        lab = lab[2:-2]
        if lab in live: print('DUP live', i, lab)
        live[lab] = (i, old, kind, name, rec, sec); order.append(lab)
    elif lab.startswith('('):
        lab = lab[1:-1]
        if lab in dead: print('DUP dead', i, lab)
        dead[lab] = (i, old, kind, name, rec, sec)
    else:
        dead['#%d' % i] = (i, old, kind, name, rec, sec)
print('장부 4절: 산 행', len(live), '죽은 행', len(dead), '(라벨 없는 행', len([k for k in dead if k.startswith('#')]), ')')
# 산 행 대 머리
for lab, (i, old, kind, name, rec, sec) in live.items():
    x = by.get(lab)
    if not x: print('LIVE-NOHEAD', i, lab); continue
    if x['kind'] != kind: print('KIND', i, lab, kind, x['kind'])
    if '.'.join(x['sec'].split('.')[:2]) != sec: print('SEC', i, lab, sec, x['sec'])
    nm = x['name'] or ''
    if '; ' in nm: n1, n2 = nm.split('; ', 1)
    else: n1, n2 = nm, ''
    if n1.startswith('기록 ['): n1, n2 = '', nm
    if n1 != name or n2 != rec:
        print('NAME', i, lab, '\n   장부:', repr(name), '|', repr(rec), '\n   머리:', repr(n1), '|', repr(n2))
for x in hs:
    if x['label'] not in live: print('HEAD-NOT-IN-4', x['label'])
print('순서(장 파일 머리 순)와 같은가:', order == [x['label'] for x in hs])
# 첫 판 번호의 겹침
cnt = collections.Counter(v[1] for v in list(live.values()) + list(dead.values()) if v[1] != '—')
print('첫 판 번호 겹침:', {k: v for k, v in cnt.items() if v > 1})
# 대응표
tdead = {}; tlive = {}
for i, line in enumerate(open(BASE + '대조v2/라벨_번호_대응표_1114.md', encoding='utf-8'), 1):
    if not line.startswith('| `'): continue
    c = [x.strip() for x in line.strip().strip('|').split(' | ')]
    lab = c[0].strip('`')
    if lab.startswith('('): tdead[lab[1:-1]] = (i, c)
    else: tlive[lab[2:-2]] = (i, c)
dl = {k for k in dead if not k.startswith('#')}
print('대응표 죽은 라벨', len(tdead), '| 장부에만:', sorted(dl - set(tdead))[:60], '| 대응표에만:', sorted(set(tdead) - dl)[:60])
# 죽은 행의 종류·이름 비교(장부 대 대응표)
n = 0
for lab in sorted(dl & set(tdead)):
    i, old, kind, name, rec, sec = dead[lab]
    j, c = tdead[lab]
    tname = c[2]
    full = name + ('; ' + rec if rec else '')
    if kind != c[1]:
        print('DEAD-KIND', lab, '장부', kind, '대응표', c[1]); n += 1
    if tname not in (full, name, '—' if not full else full) and not c[3].startswith('옮김'):
        print('DEAD-NAME', lab, '\n   장부 %d:' % i, full[:200], '\n   대응표 %d:' % j, tname[:200]); n += 1
print('죽은 행 이름·종류 어긋남', n)
# 의존지도 1절 첫 판 번호
m1 = {}; m11 = {}
for ln, line in enumerate(open(BASE + '의존지도_v2.md', encoding='utf-8'), 1):
    if line.startswith('| `{{') and ln < 284:
        c = [x.strip() for x in line.strip().strip('|').split(' | ')]
        m1[c[0].strip('`')[2:-2]] = (ln, c[2])
    elif 288 <= ln <= 527 and line.startswith('| '):
        c = [x.strip() for x in line.strip().strip('|').split(' | ')]
        m11[c[0]] = (ln, c)
for lab, (i, old, kind, name, rec, sec) in live.items():
    ln, o = m1[lab]
    exp = '새 진술' if old == '—' else '%s %s' % (kind, old)
    if o != exp: print('MAP-OLD', ln, lab, '지도:', o, '| 장부:', exp)
md = {k.strip('`')[1:-1] for k in m11 if k.startswith('`(')}
print('의존지도 1.1 행', len(m11), '라벨 있는 행', len(md), '| 지도에만:', sorted(md - dl - set(tlive))[:40], '| 장부에만:', sorted(dl - md)[:40])
# 의존지도 1.1의 옮김 행
for k, (ln, c) in m11.items():
    mm = re.match(r'^옮김\(`\{\{([^}]+)\}\}` (\d+\.\d+)절', c[2])
    if c[2].startswith('옮김'):
        if not mm: print('MAP-MOVEFMT', ln, c[2][:80]); continue
        tgt, sec = mm.groups()
        if tgt not in by: print('MAP-MOVE-NOHEAD', ln, tgt)
        elif '.'.join(by[tgt]['sec'].split('.')[:2]) != sec: print('MAP-MOVE-SEC', ln, tgt, sec, by[tgt]['sec'])
        # 대응표의 옮김과 같은가
        lab = k.strip('`')[1:-1]
        if lab in tdead:
            t = tdead[lab][1][3]
            if ('{{%s}}' % tgt) not in t: print('MOVE-TARGET-DIFF', lab, '지도:', tgt, '대응표:', t)
        if lab in dead: pass
print('지도 1.1 처리 종류:', collections.Counter(re.sub(r'\(.*', '', c[2]) for k, (ln, c) in m11.items()))
