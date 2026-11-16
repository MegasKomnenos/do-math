# -*- coding: utf-8 -*-
"""I14: 장부 4절(첫 판 번호–라벨 대응)을 현행 장 파일의 진술 머리와 대조한다."""
import re, io, sys, os, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
ROOT = r"C:/math/임시/주차함수_증명"
L = open(os.path.join(ROOT,'장부_v2.md'),encoding='utf-8').read().split('\n')
heads = {h['label']:h for h in json.load(open(os.path.join(ROOT,'scripts','수학검사2','_I14_heads.json'),encoding='utf-8'))}
rows = []
for i in range(725,1176):
    l = L[i-1]
    m = re.match(r'^\| ([^|]*) \| ([^|]*) \| ([^|]*) \| ([^|]*) \| ([^|]*) \| ([^|]*) \|\s*$', l)
    if not m:
        if l.startswith('|') and not l.startswith('|---') and '첫 판 번호' not in l: print("PARSE?", i, l[:100])
        continue
    rows.append((i,[c.strip() for c in m.groups()]))
print("4절 행 수:", len(rows))
seen = {}
for i,(old,kind,name,recname,sec,lab) in rows:
    m = re.match(r'\{\{([^}]+)\}\}', lab)
    if not m:
        print(f"  행{i}: 라벨 없음/뺌: 첫판 {old} | {kind} | {name} | {sec} | {lab[:60]}")
        continue
    label = m.group(1)
    if label in seen: print(f"  행{i}: 라벨 중복 {label} (먼저 행{seen[label]})")
    seen[label] = i
    if label not in heads:
        print(f"  행{i}: 머리 없음 {label}"); continue
    h = heads[label]
    hname = h['name']
    # 머리 괄호: "이름; 기록 [r…]의 X" 꼴
    parts = [p.strip() for p in hname.split(';')]
    hn = parts[0]; hrec = '; '.join(parts[1:])
    if kind != h['kind']: print(f"  행{i} {label}: 종류 다름 장부 {kind} / 머리 {h['kind']}")
    if sec != h['sec']: print(f"  행{i} {label}: 절 다름 장부 {sec} / 머리 {h['sec']}")
    if name != hn: print(f"  행{i} {label}: 이름 다름\n     장부: {name}\n     머리: {hn}")
    # 기록 이름: 장부의 기록 이름 열이 머리의 '기록 [..]의 ...'과 맞는가 (느슨 비교)
    rn = re.sub(r'\s+','',recname); hr = re.sub(r'\s+','',hrec)
    if rn and rn not in hr and hr not in rn:
        print(f"  행{i} {label}: 기록 이름 다름\n     장부: {recname}\n     머리: {hrec}")
    if not rn and hr:
        print(f"  행{i} {label}: 장부 기록 이름 비었으나 머리에 있음: {hrec}")
# 4절에 없는 머리
missing = [l for l in heads if l not in seen]
print("4절에 없는 현행 머리:", missing)
# 첫 판 번호 중복
olds = {}
for i,(old,kind,name,recname,sec,lab) in rows:
    if old and old != '—':
        olds.setdefault(old,[]).append(i)
print("첫 판 번호 중복:", {k:v for k,v in olds.items() if len(v)>1})
