# 정리 9:old-8-37의 머리에서 출발해 「…에 의존」 목록을 따라 내려간 폐포를 구하고, 10.2절 표의 진술이 모두 닿는지 본다.
import re, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
base = 'C:/math/임시/주차함수_증명/'
heads = {}
for ln in open(base + 'scripts/수학검사2/검토전체25_R10_색인.tsv', encoding='utf-8').read().split('\n'):
    if ln:
        lab, f, i, sec, head = ln.split('\t')
        if '[' in head and lab not in heads: heads[lab] = head
def deps(lab):
    h = heads[lab]
    br = h[h.rfind(') [')+2:] if ') [' in h else h[h.find('['):]
    pre = br.split(';')[0]
    out = []
    for seg in re.findall(r'((?:[^,]*?)에 의존)', pre):
        out += re.findall(r'\{\{([^}]+)\}\}', seg)
    return out
seen = set(); stack = ['9:old-8-37']
while stack:
    x = stack.pop()
    if x in seen: continue
    seen.add(x)
    if x not in heads: print('NO HEAD', x); continue
    for d in deps(x): stack.append(d)
comp = [l for l, h in heads.items() if ('계산 보조' in h or '계산 증거' in h)]
lit = [l for l, h in heads.items() if '문헌 인용' in h]
print('closure size', len(seen))
print('computational statements NOT in closure:', [c for c in comp if c not in seen])
print('literature-marked statements in closure:', [c for c in lit if c in seen])
t10 = open(base + '장v2/장10.md', encoding='utf-8').read()
tab = set()
for ln in t10.split('\n'):
    if ln.startswith('| 부록 D.{{'):
        tab |= set(re.findall(r'\{\{(\d[^}]+)\}\}', ln.split('|')[2]))
print('table statements not in closure:', sorted(tab - seen))
print('closure computational not in table:', sorted(set(c for c in comp if c in seen) - tab))
