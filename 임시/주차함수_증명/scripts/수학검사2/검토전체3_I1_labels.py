# -*- coding: utf-8 -*-
"""장1.md가 인용한 라벨의 진술 머리를 다른 장에서 찾아 출력한다(검토 보조)."""
import re, sys, glob, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
src = sys.argv[1]
text = open(src, encoding='utf-8').read()
labels = sorted(set(re.findall(r'\{\{(\d+[AB]?|D):([^}]+)\}\}', text)))
files = {}
for f in glob.glob('장v2/*.md'):
    files[f] = open(f, encoding='utf-8').read().split('\n')
for ch, lab in labels:
    if ch == 'D':
        continue
    key = '{{%s:%s}}' % (ch, lab)
    found = False
    for f, lines in files.items():
        for i, ln in enumerate(lines):
            if re.match(r'\*\*\S+ ' + re.escape(key), ln):
                head_end = ln.find('**', 2)
                head = ln[:head_end + 2]
                body = ln[head_end + 2:head_end + 2 + int(sys.argv[2]) if len(sys.argv) > 2 else head_end + 402]
                print('%s  [%s:%d]\n  %s\n  %s\n' % (key, f, i + 1, head, body))
                found = True
    if not found:
        print('%s  NOT FOUND\n' % key)
