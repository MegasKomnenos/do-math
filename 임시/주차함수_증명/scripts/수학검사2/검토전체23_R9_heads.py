# R9: print status brackets of all statements cited from 장9.md
import re, glob, io
heads = {}
for fn in sorted(glob.glob('장v2/장*.md')):
    for i, line in enumerate(io.open(fn, encoding='utf-8'), 1):
        m = re.match(r'\*\*(정리|명제|보조정리|따름정리|정의) \{\{([^}]+)\}\}(.*?)\*\*', line)
        if m:
            rest = m.group(3)
            br = re.findall(r'\[([^\[\]]*)\]\.?$', rest.strip())
            # last bracket group
            idx = rest.rfind(' [')
            heads[m.group(2)] = (m.group(1), fn, i, rest[idx:].strip() if idx >= 0 else rest.strip())
txt = io.open('장v2/장9.md', encoding='utf-8').read()
labs = sorted(set(re.findall(r'\{\{([^}]+)\}\}', txt)))
for l in labs:
    if l in heads:
        t, fn, i, br = heads[l]
        print(l, '|', t, '|', fn.split('/')[-1], i, '|', br[:330])
    else:
        print(l, '| NOT A STATEMENT HEAD')
