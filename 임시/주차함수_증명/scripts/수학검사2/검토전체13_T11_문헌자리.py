# -*- coding: utf-8 -*-
"""T11: 11.4 문헌 표의 「쓰인 자리」 대조용 — 낱말이 나오는 자리와 그 자리를 품은 진술을 찾는다."""
import re, os, glob, sys
ROOT = r"C:\math\임시\주차함수_증명"; CH = os.path.join(ROOT, "장v2")
head_re = re.compile(r'^\*\*(정의|정리|명제|보조정리|따름정리)\s+\{\{(\w+):([\w\-]+)\}\}')
sec_re = re.compile(r'^###\s+(\d+(?:\.\d+)*|D\.\{\{D:[\w\-]+\}\})')
def segments(fname):
    out = []; sec = None; enc = None; kind = '준비'
    for i, line in enumerate(open(fname, encoding='utf-8'), 1):
        m = sec_re.match(line)
        if m: sec = m.group(1); enc = None; kind = '준비'
        m = head_re.match(line)
        if m: enc = f"{m.group(1)} {{{{{m.group(2)}:{m.group(3)}}}}}"; kind = '진술'
        elif re.match(r'^\*\*[^*]*증명[^*]*\*\*', line) and enc: kind = '증명'
        out.append((i, kind, enc, sec, line.rstrip('\n')))
        if '∎' in line and kind == '증명': kind = '준비'
    return out
files = sorted(glob.glob(os.path.join(CH, "장*.md"))) + sorted(glob.glob(os.path.join(CH, "부록D_*.md")))
files = [f for f in files if not f.endswith('장11.md')]
segs = {os.path.basename(f): segments(f) for f in files}
kws = sys.argv[1:]
for kw in kws:
    print(f"\n### {kw}")
    rx = re.compile(kw)
    for fn, sg in segs.items():
        for (i, kind, enc, sec, text) in sg:
            if rx.search(text):
                j = rx.search(text).start()
                ctx = text[max(0, j-60):j+70]
                print(f"  {fn}:{i} [{kind}] {enc or '-'} §{sec} …{ctx}…")
