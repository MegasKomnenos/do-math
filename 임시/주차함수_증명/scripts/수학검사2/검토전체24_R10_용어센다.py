# 인자로 받은 낱말이 부록 B의 기록(md·record.json) 몇 곳에 나오는지 센다.
import re, io, sys, os, glob
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', newline='\n')
R = r'C:/math/.skill-workspace/do-math/parking-unimodality-fresh-20261105-150803/knowledge/records/'
B = open(r'C:/math/임시/주차함수_증명/장v2/부록B.md', encoding='utf-8').read()
folders = re.findall(r'(?m)^[|] (r[0-9a-f]{7}) [|].*[|] `([0-9a-z]+)` [|]$', B)
corpus = {}
for rid, fo in folders:
    parts = []
    for f in glob.glob(R+fo+'/**/*', recursive=True):
        if f.endswith('.md') or f.endswith('record.json'):
            try: parts.append(open(f, encoding='utf-8').read())
            except Exception: pass
    corpus[rid] = '\n'.join(parts)
for t in sys.argv[1:]:
    hit = [rid for rid in corpus if t in corpus[rid]]
    ex = ''
    if hit:
        c = corpus[hit[0]]; j = c.find(t); ex = c[max(0, j-40):j+len(t)+40].replace('\n', ' ')
    print(f'「{t}」 기록 {len(hit)}곳 {hit[:4]} | {ex}')
