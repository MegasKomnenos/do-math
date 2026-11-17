# -*- coding: utf-8 -*-
"""R12: 부록 D(7A,7B,8,9) 「자료」 줄의 경로가 기록 폴더와 자료 묶음에 실제로 있는지 본다(읽기 전용)."""
import re, os, glob, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
BASE = r'C:\math\임시\주차함수_증명'
REC = r'C:\math\.skill-workspace\do-math\parking-unimodality-fresh-20261105-150803\knowledge\records'
BUNDLE = os.path.join(BASE, '원고_자료')
files = ['부록D_장7A.md', '부록D_장7B.md', '부록D_장8.md', '부록D_장9.md']
for fn in files:
    txt = open(os.path.join(BASE, '장v2', fn), encoding='utf-8').read()
    print('==', fn)
    for m in re.finditer(r'`(records/(r[0-9a-f]{7})…/([^`]+))`', txt):
        rid, rel = m.group(2), m.group(3)
        dirs = glob.glob(os.path.join(REC, rid + '*'))
        if len(dirs) != 1:
            print('  REC DIR?', rid, dirs); continue
        p = os.path.join(dirs[0], rel.replace('/', os.sep))
        ok = os.path.exists(p) or bool(glob.glob(p))
        # bundle copy: <rid>/<basename> or with path
        base = os.path.basename(rel.rstrip('/'))
        b1 = os.path.join(BUNDLE, rid, base)
        b2 = os.path.join(BUNDLE, rid, rel.replace('/', os.sep))
        inb = os.path.exists(b1) or os.path.exists(b2) or bool(glob.glob(b1))
        if not ok or not inb:
            print('  record:%s bundle:%s  %s' % ('ok' if ok else 'MISSING', 'ok' if inb else 'missing', m.group(1)))
    for m in re.finditer(r'`(원고_자료/[^`]+)`', txt):
        p = os.path.join(BASE, m.group(1).replace('/', os.sep))
        if not (os.path.exists(p) or glob.glob(p)):
            print('  BUNDLE MISSING', m.group(1))
