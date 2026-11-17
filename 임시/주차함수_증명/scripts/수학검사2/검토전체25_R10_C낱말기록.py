# 부록 C 낱말 표의 「기록의 용어」 칸에 든 낱말이 부록 B의 75개 기록(검토 폴더 제외한 md·json)에 실제로 나오는지 센다. 자리 찾기용.
import re, io, sys, os, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
base = 'C:/math/임시/주차함수_증명/장v2/'
rec = 'C:/math/.skill-workspace/do-math/parking-unimodality-fresh-20261105-150803/knowledge/records/'
ids = re.findall(r'`(r[0-9a-f]{32})`', open(base + '부록B.md', encoding='utf-8').read())
texts = {}
for d in ids:
    s = ''
    for root, ds, fs in os.walk(rec + d):
        if os.sep + 'review' in root: continue
        for f in fs:
            if f.endswith('.md') or f == 'record.json':
                try: s += open(os.path.join(root, f), encoding='utf-8').read() + '\n'
                except Exception: pass
    texts[d[:8]] = s
allrec = {}
for d in os.listdir(rec):
    if d[:8] in texts: continue
    p = rec + d + '/exposition.md'
    if os.path.exists(p):
        try: allrec[d[:8]] = open(p, encoding='utf-8').read()
        except Exception: pass
C = open(base + '부록C.md', encoding='utf-8').read().split('\n')
cs = C.index('### 낱말: 이 글의 용어와 기록의 용어'); ce = C.index('### 기록이 결과에 붙인 이름과 이 글의 번호')
terms = sys.argv[1:]
for i in range(cs, ce):
    ln = C[i]
    if not ln.startswith('| ') or ln.startswith('| 이 글의 용어') or ln.startswith('|---'): continue
    c = [x.strip() for x in ln.strip().strip('|').split(' | ')]
    own, recw = c[0], c[1]
    # 낱말 후보: 「…」 안의 것과 쉼표로 나눈 맨 앞 조각들(괄호 설명 제거)
    cands = re.findall(r'「([^」]+)」', recw)
    plain = re.sub(r'\([^()]*\)', '', recw)
    plain = re.sub(r'\([^()]*\)', '', plain)
    for part in re.split(r'[,;]\s*', plain):
        part = part.strip()
        if part and '「' not in part and len(part) <= 14 and not part.startswith('—') and '같음' not in part and '$' not in part:
            cands.append(part)
    for w in dict.fromkeys(cands):
        n = [k for k, s in texts.items() if w in s]
        if len(n) == 0:
            m = [k for k, s in allrec.items() if w in s]
            print(f'C:{i+1} [{own}] 기록의 용어 「{w}」: 75개 기록 0건; 인용하지 않은 기록 {len(m)}건 {m[:4]}')
