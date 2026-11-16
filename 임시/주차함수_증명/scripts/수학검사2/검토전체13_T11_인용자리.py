# -*- coding: utf-8 -*-
"""T11: 11.3 표의 입력 라벨이 9장·10장·7B(7.7절)에서 인용되는 자리를 찾는다(자리 찾기용)."""
import re, os, sys, json
ROOT = r"C:\math\임시\주차함수_증명"; CH = os.path.join(ROOT, "장v2")
head_re = re.compile(r'^\*\*(정의|정리|명제|보조정리|따름정리)\s+\{\{(\w+):([\w\-]+)\}\}')
sec_re = re.compile(r'^###\s+(\d+(?:\.\d+)*)')
def segments(fname):
    out = []  # (line, kind, enclosing, sec, text)
    sec = None; enc = None; kind = '준비'
    for i, line in enumerate(open(fname, encoding='utf-8'), 1):
        m = sec_re.match(line)
        if m: sec = m.group(1); enc = None; kind = '준비'
        m = head_re.match(line)
        if m:
            enc = f"{m.group(1)} {{{{{m.group(2)}:{m.group(3)}}}}}"; kind = '진술'
        elif line.startswith('**증명') or line.startswith('**(가)의 증명') or re.match(r'^\*\*.*증명\.?\*\*', line):
            if enc: kind = '증명'
        out.append((i, kind, enc, sec, line.rstrip('\n')))
        if '∎' in line and kind == '증명':
            kind = '준비'
    return out
lines11 = open(os.path.join(CH, "장11.md"), encoding='utf-8').read().split('\n')
sec113 = '\n'.join(lines11[83:130])
labels = sorted(set(re.findall(r'\{\{(\d+:[\w\-]+)\}\}', sec113)))
targets = [l for l in labels if not l.startswith(('9:', '10:'))]
files = {'9': os.path.join(CH, '장9.md'), '10': os.path.join(CH, '장10.md'), '7B': os.path.join(CH, '장7B.md')}
segs = {k: segments(v) for k, v in files.items()}
res = {}
for lab in targets:
    pat = '{{' + lab + '}}'
    hits = []
    for k, sg in segs.items():
        for (i, kind, enc, sec, text) in sg:
            if pat in text:
                if k == '7B' and not (enc and 'old-6-22' in enc): continue
                # 맥락 60자
                j = text.find(pat)
                ctx = text[max(0, j-70):j+len(pat)+40].replace('\n', ' ')
                hits.append(f"{k}:{i} [{kind}] {enc or '-'} §{sec} …{ctx}…")
    res[lab] = hits
for lab in targets:
    print(f"\n### {lab} ({len(res[lab])})")
    for h in res[lab]: print("  ", h)
