# -*- coding: utf-8 -*-
"""부록 A: 기호가 「처음 정의된 절」에 실제로 나타나는지(고정 문자열), 장부 1.2절 전역 기호와의 집합 비교."""
import re, os, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from 검토전체19_M11_공용 import *

chs = load_chapters()
# 절 → 텍스트
sectext = {}
for fn, lines in chs.items():
    sec = None
    for ln in lines:
        m = re.match(r'^(#+)\s+(\d+(?:\.\d+)*)', ln)
        if m:
            sec = m.group(2)
        if sec:
            sectext.setdefault(sec, []).append(ln)
sectext = {k: '\n'.join(v) for k, v in sectext.items()}
alltext = '\n'.join('\n'.join(v) for v in chs.values())

A = open(os.path.join(CH, '부록A.md'), encoding='utf-8').read().split('\n')
rows = []
for ln in A:
    if ln.startswith('| $'):
        c = [x.strip() for x in ln.strip().strip('|').split(' | ')]
        rows.append(c)
print('부록 A 행 수', len(rows))

def cores(sym):
    """기호 셀에서 검색용 고정 문자열 후보들을 뽑는다."""
    s = sym.strip('$')
    parts = [p.strip().strip('$') for p in re.split(r',\s*(?=\$)|,\s*(?=\\)|,\s*(?=[A-Za-z])', s) if p.strip()]
    out = []
    for p in parts:
        p = re.sub(r'^\(|\)$', '', p)
        p = p.split(':=')[0].split('=')[0].strip()
        # 인수 괄호 제거
        q = re.sub(r'\([^()]*\)$', '', p).strip()
        out.append(q if q else p)
    return out

def in_section(core, sec):
    # 절 번호 '1.5' 등; 소절 '5.5.6' 등은 앞 두 조각으로
    keys = [k for k in sectext if k == sec or k.startswith(sec + '.')]
    txt = '\n'.join(sectext[k] for k in keys)
    return core in txt

for c in rows:
    sym, meaning, sec, rec = c[0], c[1], c[2], c[3] if len(c) > 3 else ''
    secs = re.findall(r'\d+\.\d+', sec)
    cs = cores(sym)
    missing = []
    for core in cs:
        ok_any = any(in_section(core, s) for s in secs)
        if not ok_any:
            where = sorted({k for k, v in sectext.items() if core in v})[:6]
            missing.append((core, where, core in alltext))
    if missing:
        print('*', sym[:70], '| 절', sec, '|', missing)

print()
print('=== 장부 1.2 전역 기호 vs 부록 A')
L = open(os.path.join(ROOT, '장부_v2.md'), encoding='utf-8').read().split('\n')
in12 = False
ledger = []
for ln in L:
    if ln.startswith('### 1.2'):
        in12 = True
    elif ln.startswith('### 1.3') or ln.startswith('## 2'):
        in12 = False
    if in12 and ln.startswith('| $'):
        c = [x.strip() for x in ln.strip().strip('|').split(' | ')]
        ledger.append(c)
print('장부 1.2 행 수', len(ledger))
A_syms = {}
for c in rows:
    for core in cores(c[0]):
        A_syms[core] = c
L_syms = {}
for c in ledger:
    for core in cores(c[0]):
        L_syms[core] = c
print('-- 장부 1.2에 있으나 부록 A에 없는 기호(핵):')
for k, c in L_syms.items():
    if k not in A_syms:
        print('   ', c[0][:60], '| 정의 절', c[3] if len(c) > 3 else '')
print('-- 부록 A에 있으나 장부 1.2에 없는 기호(핵):')
for k, c in A_syms.items():
    if k not in L_syms:
        print('   ', c[0][:60], '| 절', c[2])
print('-- 정의 절이 다른 기호:')
for k, c in A_syms.items():
    if k in L_syms:
        la = re.findall(r'\d+\.\d+', c[2]); ll = re.findall(r'\d+\.\d+', L_syms[k][3] if len(L_syms[k]) > 3 else '')
        if la and ll and la[0] != ll[0]:
            print('   ', c[0][:50], '| 부록A', c[2], '| 장부', L_syms[k][3])
