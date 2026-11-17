# 부록 C 낱말 표 둘째 칸(기록의 용어)의 낱말이 부록 B의 기록 원문(md·json)에 실제로 나오는지 센다.
import re, io, sys, os, glob
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', newline='\n')
R = r'C:/math/.skill-workspace/do-math/parking-unimodality-fresh-20261105-150803/knowledge/records/'
base = r'C:/math/임시/주차함수_증명/장v2/'
B = open(base+'부록B.md', encoding='utf-8').read()
folders = re.findall(r'(?m)^[|] (r[0-9a-f]{7}) [|].*[|] `([0-9a-z]+)` [|]$', B)
corpus = {}
for rid, fo in folders:
    parts = []
    for f in glob.glob(R+fo+'/**/*', recursive=True):
        if f.endswith('.md') or f.endswith('record.json'):
            try: parts.append(open(f, encoding='utf-8').read())
            except Exception: pass
    corpus[rid] = '\n'.join(parts)
C = open(base+'부록C.md', encoding='utf-8').read().split('\n')
a = next(i for i,l in enumerate(C) if l.startswith('### 낱말'))
b = next(i for i,l in enumerate(C) if l.startswith('### 기록이 결과에'))
for i in range(a, b):
    l = C[i]
    if not l.startswith('| ') or l.startswith('| 이 글의') or l.startswith('|---'): continue
    cells = [c.strip() for c in l.strip().strip('|').split(' | ')]
    cell = cells[1]
    if cell.startswith('—'): continue
    # 괄호 풀이를 떼고 쉼표·쌍반점으로 가른다; 「…」 안 낱말도 뽑는다
    quoted = re.findall(r'「([^」]+)」', cell)
    plain = re.sub(r'\([^()]*(\([^()]*\))?[^()]*\)', '', cell)
    toks = [t.strip() for t in re.split(r'[,;]', plain) if t.strip()]
    toks = [re.sub(r'「[^」]*」.*$', '', t).strip() for t in toks]
    toks = [t for t in toks if t and not t.startswith('$') and t not in ('같음',)]
    for t in dict.fromkeys(toks + quoted):
        n = sum(1 for rid in corpus if t in corpus[rid])
        if n == 0: print(f'[C {i+1}] 이 글 「{cells[0]}」 ← 기록의 용어 「{t}」: 기록 0곳')
        elif len(sys.argv) > 1: print(f'[C {i+1}] 「{t}」: 기록 {n}곳')
