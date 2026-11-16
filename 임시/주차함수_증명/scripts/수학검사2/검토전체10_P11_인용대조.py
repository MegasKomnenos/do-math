# -*- coding: utf-8 -*-
"""9장·10장·7.7절 진술 블록이 인용하는 라벨을 뽑아 11.3 표의 「직접 인용하는 자리」와 대조할 자료를 만든다."""
import re, glob, os, sys, io, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
BASE = r"C:\math\임시\주차함수_증명\장v2"
HEAD = re.compile(r'^\*\*(정리|명제|보조정리|따름정리|정의)\s+\{\{(\d+[AB]?:[^}]+)\}\}(?!의 증명)')
def segments(fname):
    lines = open(os.path.join(BASE,fname),encoding='utf-8').read().split('\n')
    segs = []  # (label or None, kind, section, head_line_no, lines)
    cur = None; sec=None
    for i, ln in enumerate(lines,1):
        m = re.match(r'#{2,4}\s+(\d+(?:\.\d+)*)\s', ln)
        if m: sec = m.group(1)
        h = HEAD.match(ln)
        if h or m:
            cur = dict(label=h.group(2) if h else None, kind=h.group(1) if h else None, sec=sec, line=i, text=[])
            segs.append(cur)
        if cur is None:
            cur = dict(label=None, kind=None, sec=sec, line=i, text=[]); segs.append(cur)
        cur['text'].append(ln)
    return segs
def cites(seg):
    """라벨 -> 위치 유형 집합(머리/진술, 증명, 뒤 문단)"""
    out = {}
    txt = '\n'.join(seg['text'])
    # 분할: 머리행(첫 줄), 증명 부분, 나머지
    first = seg['text'][0]
    rest = '\n'.join(seg['text'][1:])
    mp = re.search(r'\*\*증명\.?\*\*(.*?)(∎|$)', rest, flags=re.S)
    proof = mp.group(1) if mp else ''
    after = rest[mp.end():] if mp else rest
    # 머리의 표지(대괄호) 안 의존 목록과 진술 본문 구분
    mh = re.match(r'\*\*.*?\[(.*?)\]\.\*\*(.*)', first)
    head_dep = mh.group(1) if mh else ''
    stmt = (mh.group(2) if mh else first)
    for part, name in ((head_dep,'표지'),(stmt,'진술'),(proof,'증명'),(after,'뒤문단')):
        for lab in re.findall(r'\{\{(\d+[AB]?:[^}]+)\}\}', part):
            out.setdefault(lab,set()).add(name)
    return out
allsegs = {}
for f in ['장9.md','장10.md','장7B.md']:
    for s in segments(f):
        s['file']=f; allsegs.setdefault(f,[]).append(s)
# 11.3 표의 입력 라벨
ch11 = open(os.path.join(BASE,'장11.md'),encoding='utf-8').read()
i0 = ch11.index('**공유 입력.**'); i1 = ch11.index('### 11.4')
tab = ch11[i0:i1]
inputs = []
for ln in tab.split('\n'):
    if ln.startswith('| ') and not ln.startswith('| 입력') and not ln.startswith('|---'):
        c=[x.strip() for x in ln.strip().strip('|').split(' | ')]
        labs = re.findall(r'\{\{(\d+[AB]?:[^}]+)\}\}', c[0])
        inputs.append((c[0][:60], labs, c))
# 역색인: 라벨 -> 9/10장 및 7:old-6-22 블록에서의 인용
rev = {}
for f, segs in allsegs.items():
    for s in segs:
        if f=='장7B.md' and s['label']!='7:old-6-22': continue
        for lab, where in cites(s).items():
            rev.setdefault(lab, []).append((s['label'] or f"(준비문단 §{s['sec']} L{s['line']})", s['kind'], sorted(where)))
for name, labs, c in inputs:
    print(f"\n##### 행: {name}")
    for lab in labs:
        print(f"  [{lab}] 인용 자리:")
        for x in rev.get(lab, []):
            print(f"      {x[0]} ({x[1]}) {x[2]}")
    print("  표 첫째 증명 열:", c[2][:400] if len(c)>2 else '')
    if len(c)>3: print("  표 둘째 증명 열:", c[3][:400])
json.dump({k:[list(x) for x in v] for k,v in rev.items()}, open(r"C:\math\임시\주차함수_증명\scripts\수학검사2\검토전체10_P11_rev.json",'w',encoding='utf-8'), ensure_ascii=False, indent=1)
