# -*- coding: utf-8 -*-
# 수리 U17 — 편집 19: 구조표_v2.md에 편집 18이 더한 2026-11-17 메모 안에서, 체크포인트 3e8c5ae0의 진술 머리에 없는(지운) 라벨은
#  장부 4절 뺌 행의 관례대로 중괄호 없이 `N:이름` 꼴로 적는다(라벨 검사기가 산 라벨로 읽지 않게). 살아 있는 라벨은 `{{N:이름}}` 그대로.
import glob, io, os, re, sys
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from 수리_U17_편집 import apply, ROOT
live = set()
HEAD = re.compile(r'^\*\*(?:정의|정리|보조정리|명제|따름정리)\s+\{\{([^}]+)\}\}')
DITEM = re.compile(r'^### D\.\{\{(D:[^}]+)\}\}')
for f in glob.glob(os.path.join(HERE, '_u17_chk', '장v2', '*.md')):
    if os.path.basename(f).startswith('부록A') or os.path.basename(f).startswith('부록B') or os.path.basename(f).startswith('부록C'):
        continue
    for l in io.open(f, encoding='utf-8'):
        m = HEAD.match(l) or DITEM.match(l)
        if m: live.add(m.group(1))
PATH = os.path.join(ROOT, '구조표_v2.md')
lines = io.open(PATH, encoding='utf-8').read().split('\n')
ops = []; changed = []
for l in lines:
    k = l.find('(2026-11-17 구조 압축')
    if k < 0: continue
    head, note = l[:k], l[k:]
    def fix(m):
        lab = m.group(1)
        if lab in live: return m.group(0)
        changed.append(lab); return '`' + lab + '`'
    note2 = re.sub(r'`\{\{([^}]+)\}\}`', fix, note)
    if note2 != note:
        prefix = l[:l.find(' |', 2) + 2] if l.startswith('| ') else l[:30]
        ops.append(('set_row', prefix, head + note2))
print('지운 라벨로 표기한 자리', len(changed), '; 줄', len(ops))
apply(PATH, ops, dry='--dry' in sys.argv)
