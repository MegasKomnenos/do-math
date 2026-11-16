# -*- coding: utf-8 -*-
"""K14: 장부 4절(이름 사전)의 행을 장 파일 진술 머리와 대조 — 종류·이름·기록 이름·절·라벨 존재."""
import re, sys, io, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
ROOT = r'C:\math\임시\주차함수_증명'
heads = {}
for line in open(os.path.join(ROOT, '대조v2', '수학검사2', '_K17_14_heads.tsv'), encoding='utf-8'):
    f, ln, num, kind, lab, name, status, sec = line.rstrip('\n').split('\t')
    heads[lab] = dict(file=f, line=ln, num=num, kind=kind, name=name, status=status, sec=sec)
lines = open(os.path.join(ROOT, '장부_v2.md'), encoding='utf-8').read().split('\n')
s = next(i for i, l in enumerate(lines) if l.startswith('## 4.'))
e = next(i for i, l in enumerate(lines) if l.startswith('## 5.'))
out = []
n = 0
seen = set()
for l in lines[s:e]:
    m = re.match(r'^\| (.*?) \| (.*?) \| (.*?) \| (.*?) \| (.*?) \| (.*?) \|\s*$', l)
    if not m or m.group(1) in ('첫 판 번호', '---'):
        continue
    old, kind, name, rec, sec, lab = [x.strip() for x in m.groups()]
    n += 1
    labs = re.findall(r'\{\{\d+:[^}]+\}\}', lab)
    if '뺌' in lab or '뺌' in sec or '뺌' in kind:
        # 뺌 행: 라벨이 장에 없어야 한다
        for L in labs:
            if L in heads:
                out.append(('뺌 행인데 장에 머리 있음', old, L))
        continue
    if not labs:
        out.append(('라벨 없음', old, kind, name, lab)); continue
    L = labs[0]
    seen.add(L)
    if L not in heads:
        out.append(('장에 없음', old, L, kind, name)); continue
    h = heads[L]
    if h['kind'] != kind:
        out.append(('종류', L, '장부=' + kind, '현행=' + h['kind']))
    hn = h['name']
    # 머리 이름 = "이 글의 이름; 기록 [..]의 X" 꼴
    hname = hn.split(';')[0].strip()
    if name != hname:
        out.append(('이름', L, '장부=' + name, '현행=' + hname))
    hrec = hn.split(';', 1)[1].strip() if ';' in hn else ''
    if rec and rec not in hn:
        out.append(('기록 이름', L, '장부=' + rec, '현행=' + hrec))
    if not rec and hrec:
        out.append(('기록 이름 비어 있음', L, '현행=' + hrec))
    if sec != h['sec']:
        out.append(('절', L, '장부=' + sec, '현행=' + h['sec']))
for L in heads:
    if L not in seen:
        out.append(('4절에 없음', L, heads[L]['kind'], heads[L]['name']))
with open(os.path.join(ROOT, '대조v2', '수학검사2', '_K17_14_sec4_out.txt'), 'w', encoding='utf-8') as f:
    for o in out:
        f.write('\t'.join(o) + '\n')
print('rows', n, 'diffs', len(out))
