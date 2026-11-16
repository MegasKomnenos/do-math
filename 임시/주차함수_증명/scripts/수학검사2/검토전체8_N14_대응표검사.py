# -*- coding: utf-8 -*-
"""라벨–번호 대응표를 장 파일의 현행 머리와 맞춘다: 라벨 존재, 종류, 이름, 현재 번호, 절."""
import re, sys, os, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
root = r"C:\math\임시\주차함수_증명"
order = ["장1","장2","장3","장4","장5A","장5B","장6","장7A","장7B","장8","장9","장10","장11"]
HEAD_RE = re.compile(r"^\*\*(정의|정리|명제|보조정리|따름정리) \{\{(\d+):([A-Za-z][A-Za-z0-9\-]*)\}\}(?= \(| \[|\.\*\*|\*\*)")
CH_RE = re.compile(r"^## (\d+)\.")
SEC_RE = re.compile(r"^#{3,4} (\d+\.\d+(?:\.\d+)?)")
cur = {}
chapter = None; counter = {}; sec = None
for name in order:
    with open(os.path.join(root, "장v2", name + ".md"), encoding='utf-8') as f:
        for ln_no, line in enumerate(f, 1):
            m = CH_RE.match(line)
            if m:
                chapter = int(m.group(1)); counter.setdefault(chapter, 0); sec = None
            m = SEC_RE.match(line)
            if m: sec = m.group(1)
            m = HEAD_RE.match(line)
            if m:
                counter[chapter] += 1
                kind, lab_ch, lab = m.groups()
                rest = line[m.end():]
                nm = None
                if rest.startswith(" ("):
                    depth=0
                    for idx,ch in enumerate(rest[1:],1):
                        if ch=="(": depth+=1
                        elif ch==")":
                            depth-=1
                            if depth==0:
                                nm=rest[2:idx].strip(); break
                cur[f"{lab_ch}:{lab}"] = dict(kind=kind, num=f"{chapter}.{counter[chapter]}", sec=sec, name=nm, file=name, ln=ln_no, labch=int(lab_ch), ch=chapter)
# 표 읽기
tbl = {}
with open(os.path.join(root, "대조v2", "라벨_번호_대응표_1114.md"), encoding='utf-8') as f:
    for line in f:
        m = re.match(r"^\| `\{\{(\d+):([^}]+)\}\}` \| ([^|]+) \| ([^|]*) \| ([^|]+) \| ([^|]+) \| ([^|]+) \|", line)
        if m:
            tbl[f"{m.group(1)}:{m.group(2)}"] = dict(kind=m.group(3).strip(), name=m.group(4).strip(), num=m.group(5).strip(), old=m.group(6).strip(), sec=m.group(7).strip())
        m2 = re.match(r"^\| `\((\d+):([^)]+)\)` \|", line)
        if m2:
            k = f"{m2.group(1)}:{m2.group(2)}"
            if k in cur: print("뺌으로 적혔으나 장 파일에 머리가 있음:", k, cur[k])
print("장 파일 머리 수:", len(cur), " 표의 현행 라벨 수:", len(tbl))
for k, v in cur.items():
    if v['labch'] != v['ch']: print("라벨 장 번호와 놓인 장이 다름:", k, v)
for k in cur:
    if k not in tbl: print("표에 없음:", k, cur[k]['kind'], cur[k]['num'], cur[k]['name'])
for k in tbl:
    if k not in cur: print("장 파일에 없음:", k, tbl[k])
for k in tbl:
    if k in cur:
        c, t = cur[k], tbl[k]
        if c['kind'] != t['kind']: print("종류 다름:", k, "표", t['kind'], "장", c['kind'])
        if c['num'] != t['num']: print("번호 다름:", k, "표", t['num'], "장", c['num'])
        if c['sec'] is None or not (t['sec'] == c['sec'] or c['sec'].startswith(t['sec'] + ".")): print("절 다름:", k, "표", t['sec'], "장", c['sec'])
        cn = (c['name'] or '').split(';')[0].strip()
        tn = t['name'].split(';')[0].strip()
        if tn in ('—', '') and cn: print("이름: 표는 —, 장은", repr(cn), k)
        elif tn not in ('—','') and cn != tn: print("이름 다름:", k, "| 표:", t['name'], "| 장:", c['name'])
# 순서 검사: 표의 행 순서가 장 파일 순서와 같은가
