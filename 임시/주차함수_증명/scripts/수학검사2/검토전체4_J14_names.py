# -*- coding: utf-8 -*-
"""J14: 장부 4절(이름 사전) 행을 장 파일 진술 머리(_J14_heads.tsv)와 견준다.
열: 첫 판 번호 | 종류 | 이 글의 이름 | 기록의 이름 | 둘째 판 절 | 라벨
"""
import re, sys, io
from pathlib import Path
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
ROOT = Path(r'C:\math\임시\주차함수_증명')
heads = {}
for L in (ROOT/'scripts'/'수학검사2'/'_J14_heads.tsv').read_text(encoding='utf-8').splitlines():
    lab, kind, sec, nm, st, where = L.split('\t')
    heads[lab] = (kind, sec, nm, st, where)
lines = (ROOT/'장부_v2.md').read_text(encoding='utf-8').splitlines()
rows = []
for i in range(733, 1177):
    L = lines[i]
    if not L.startswith('| '): continue
    cols = [c.strip() for c in L.strip().strip('|').split('|')]
    if len(cols) < 6:
        print(f'[열 수] {i+1}: {L[:80]}'); continue
    rows.append((i+1, cols))
seen = set()
for ln, (old, kind, name, recname, sec, lab) in rows:
    m = re.match(r'\{\{([^}]+)\}\}', lab)
    if not m:
        print(f'[라벨 꼴] {ln}: {lab}'); continue
    label = m.group(1)
    if label in seen: print(f'[중복] {ln}: {label}')
    seen.add(label)
    if label not in heads:
        print(f'[머리 없음] {ln}: {label} ({kind}, {name}, {sec})'); continue
    hkind, hsec, hnm, hst, where = heads[label]
    probs = []
    if hkind != kind: probs.append(f'종류 장부={kind} 머리={hkind}')
    # 절 비교: 머리의 절 제목 앞 숫자
    hsecnum = re.match(r'(\d+(?:\.\d+)*)', hsec)
    hsecnum = hsecnum.group(1) if hsecnum else hsec
    if sec and not (hsecnum == sec or hsecnum.startswith(sec + '.') ):
        probs.append(f'절 장부={sec} 머리={hsecnum}')
    # 이름 비교: 머리 괄호의 ';' 앞부분
    hname = hnm.split(';')[0].strip()
    if name and name != hname:
        probs.append(f'이름 장부=「{name}」 머리=「{hname}」')
    # 기록 이름: 머리 괄호의 ';' 뒷부분에 들어 있어야
    hrec = ';'.join(hnm.split(';')[1:]).strip()
    if recname and recname not in hnm:
        probs.append(f'기록이름 장부=「{recname}」 머리=「{hrec}」')
    if not name and hname:
        probs.append(f'장부 이름 비었으나 머리=「{hname}」')
    if not recname and hrec:
        probs.append(f'장부 기록이름 비었으나 머리=「{hrec}」')
    if probs:
        print(f'[{ln}] {label} @ {where}: ' + ' / '.join(probs))
# 머리에는 있으나 4절에 없는 라벨
for lab, (kind, sec, nm, st, where) in heads.items():
    if lab not in seen:
        print(f'[4절 없음] {lab} ({kind}, {sec}) @ {where}')
