# -*- coding: utf-8 -*-
# R10: dependency closure of the main-theorem proof through the "…에 의존" lists of statement heads.
import io, re, sys, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
here = os.path.dirname(os.path.abspath(__file__))
heads = {}
for line in io.open(os.path.join(here, '검토전체22_R10_heads_out.txt'), encoding='utf-8'):
    m = re.match(r'^(\S+) (\d+) (\S+) (.*)$', line.rstrip('\n'))
    if not m: continue
    h = m.group(4)
    lab = re.search(r'\{\{([^}]+)\}\}', h).group(1)
    if '의 증명' in h[:60] and lab in heads: continue
    i = h.rfind('[')
    bracket = h[i+1:] if i >= 0 else ''
    # bracket may contain nested label braces only; find the true status bracket: last '[' followed by 지위 words
    for mm in re.finditer(r'\[', h):
        seg = h[mm.start()+1:]
        if seg.startswith(('증명됨', '계산 증거', '$', '(가)', '(나)')) or '증명됨' in seg[:40] or '계산 증거' in seg[:40]:
            bracket = seg; break
    dep = []
    for m2 in re.finditer(r'((?:정리|명제|보조정리|따름정리)[^;\]]*?)에 의존', bracket):
        dep += re.findall(r'\{\{([^}]+)\}\}', m2.group(1))
    heads[lab] = dict(br=bracket, dep=dep, sec=m.group(3))
root = '9:old-8-37'
seen = set(); stack = [root]
while stack:
    x = stack.pop()
    if x in seen: continue
    seen.add(x)
    for d in heads.get(x, {}).get('dep', []): stack.append(d)
print('closure size', len(seen))
print('closure statements with 문헌 인용:', [x for x in seen if '문헌 인용' in heads.get(x, {}).get('br', '')])
print('closure statements with 계산:', sorted(x for x in seen if '계산' in heads.get(x, {}).get('br', '')))
allcomp = sorted(x for x in heads if '계산' in heads[x]['br'])
print('computation statements NOT in main closure:', [x for x in allcomp if x not in seen])
print('labels in closure without head:', [x for x in seen if x not in heads])
