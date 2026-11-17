# 부록 C 「기록이 결과에 붙인 이름과 이 글의 번호」 표를 본문 진술 머리의 괄호(이름; 기록의 이름)에 맞댄다.
import re, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
base = 'C:/math/임시/주차함수_증명/'
idx = {}
for ln in open(base + 'scripts/수학검사2/검토전체25_R10_색인.tsv', encoding='utf-8').read().split('\n'):
    if ln:
        lab, f, i, sec, head = ln.split('\t')
        idx.setdefault(lab, []).append((f, i, sec, head))
txt = open(base + '장v2/부록C.md', encoding='utf-8').read().split('\n')
start = txt.index('### 기록이 결과에 붙인 이름과 이 글의 번호')
end = txt.index('### 기록의 글자와 이 글의 글자')
seen = set(); n = 0
for k in range(start, end):
    ln = txt[k]
    m = re.match(r'\| (.*) \| (정리|명제|보조정리|따름정리|정의) \{\{([^}]+)\}\} \| (.*) \|$', ln)
    if not m: continue
    n += 1
    recname, kind, lab, name = m.groups()
    seen.add(lab)
    if lab not in idx: print(k+1, 'LABEL NOT FOUND', lab); continue
    f, i, sec, head = idx[lab][0]
    mh = re.match(r'(정리|명제|보조정리|따름정리|정의) \{\{[^}]+\}\} \((.*)\) \[', head)
    if not mh: print(k+1, 'HEAD PARSE', lab, head[:200]); continue
    hk, inner = mh.groups()
    if ';' in inner:
        hname, hrec = inner.split(';', 1); hrec = hrec.strip()
    else:
        hname, hrec = inner, ''
    msgs = []
    if hk != kind: msgs.append(f'KIND C={kind} head={hk}')
    if hname.strip() != name.strip(): msgs.append(f'NAME\n   C: {name}\n   H: {hname}')
    if hrec != recname.strip(): msgs.append(f'RECNAME\n   C: {recname}\n   H: {hrec}')
    if msgs: print(k+1, lab, f, i, '\n  ' + '\n  '.join(msgs))
print('rows', n)
# 머리에 「기록 […]의 …」가 있는데 표에 없는 진술
for lab, v in idx.items():
    for f, i, sec, head in v:
        mh = re.match(r'(정리|명제|보조정리|따름정리|정의) \{\{[^}]+\}\} \((.*?)\) \[', head)
        if mh and '기록 [' in mh.group(2) and lab not in seen:
            print('HEAD HAS RECORD NAME BUT NOT IN C:', lab, f, i, head[:200])
