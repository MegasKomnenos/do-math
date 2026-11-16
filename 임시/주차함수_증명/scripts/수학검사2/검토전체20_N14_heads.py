# -*- coding: utf-8 -*-
"""N14: 장 파일의 진술 머리·절·라벨 인용을 뽑아 대응표·장부 4절·의존지도 1절과 맞춘다."""
import re, sys, io, os, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
ROOT = r"C:\math\임시\주차함수_증명"
CH = ["장1","장2","장3","장4","장5A","장5B","장6","장7A","장7B","장8","장9","장10","장11"]
HEAD = re.compile(r'^\*\*(정리|보조정리|명제|정의|따름정리) \{\{([^}]+)\}\}(.*?)\*\*')
LAB = re.compile(r'\{\{(\d+:[^}]+)\}\}')
SEC = re.compile(r'^(#{3}) (\d+(?:\.\d+)*)\s')

heads = []   # dicts
deferred = []  # (file,line,label) of deferred proof heads
bodies = {}  # label -> text between head and next head (same file)
sec_of_line = {}
all_lines = {}
for ch in CH:
    p = os.path.join(ROOT, "장v2", ch + ".md")
    lines = open(p, encoding='utf-8').read().split('\n')
    all_lines[ch] = lines
    cur_sec = None
    idx = []
    for i, ln in enumerate(lines, 1):
        m = SEC.match(ln)
        if m:
            cur_sec = m.group(2)
        m = HEAD.match(ln)
        if m and m.group(3).startswith('의 증명'):
            deferred.append((ch, i, m.group(2)))
            continue
        if m:
            kind, label, rest = m.group(1), m.group(2), m.group(3)
            # name: first (...) group ; status: [...] group
            name = None; status = None; recid = None
            mn = re.match(r'\s*\((.*?)\)\s*(\[(.*?)\])?\.?$', rest)
            if mn:
                name = mn.group(1)
                if mn.group(3) is not None:
                    status = mn.group(3)
            else:
                mb = re.match(r'\s*\[(.*?)\]\.?$', rest)
                if mb:
                    status = mb.group(1)
            if status is not None and ';' in status:
                st, rec = status.rsplit(';', 1)
                status_core, recid = st.strip(), rec.strip()
            else:
                status_core, recid = (status.strip() if status else None), None
            heads.append(dict(file=ch, line=i, kind=kind, label=label, name=name,
                              status=status, status_core=status_core, recid=recid, sec=cur_sec))
            idx.append(len(heads)-1)
    # bodies
    dlines = sorted(l for (c, l, _) in deferred if c == ch)
    for j, hi in enumerate(idx):
        start = heads[hi]['line']
        end = heads[idx[j+1]]['line']-1 if j+1 < len(idx) else len(lines)
        for dl_ in dlines:
            if start < dl_ <= end:
                end = dl_-1; break
        body = '\n'.join(lines[start:end])  # lines after head line
        headline = lines[start-1]
        heads[hi]['head_labels'] = sorted(set(LAB.findall(headline)) - {heads[hi]['label']})
        heads[hi]['body_labels'] = sorted(set(LAB.findall(body)) - {heads[hi]['label']})

# deferred proofs: attach labels cited in the deferred proof block
for (ch, i, lab) in deferred:
    lines = all_lines[ch]
    end = len(lines)
    for j in range(i, len(lines)):
        if HEAD.match(lines[j]):
            end = j; break
    body = '\n'.join(lines[i-1:end])
    labs = set(LAB.findall(body)) - {lab}
    for h in heads:
        if h['label'] == lab:
            h['body_labels'] = sorted(set(h['body_labels']) | labs)
            h['deferred'] = f"{ch}.md:{i}"
# numbering per chapter
num = {}
for h in heads:
    chn = h['label'].split(':')[0]
    num[chn] = num.get(chn, 0) + 1
    h['num'] = f"{chn}.{num[chn]}"

out = os.path.join(ROOT, "scripts", "수학검사2", "_N14_heads.tsv")
with open(out, 'w', encoding='utf-8') as f:
    f.write("file\tline\tnum\tkind\tlabel\tname\tstatus_core\trecid\tsec\thead_labels\tbody_labels\n")
    for h in heads:
        f.write('\t'.join(str(h.get(k, '')) for k in ["file","line","num","kind","label","name","status_core","recid","sec"]) +
                '\t' + ' '.join(h['head_labels']) + '\t' + ' '.join(h['body_labels']) + '\n')
json.dump(heads, open(os.path.join(ROOT, "scripts", "수학검사2", "_N14_heads.json"), 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
print("heads:", len(heads))
from collections import Counter
c = Counter(h['label'] for h in heads)
dups = [k for k, v in c.items() if v > 1]
print("duplicate labels:", dups)
print("per chapter:", Counter(h['label'].split(':')[0] for h in heads))
