import re, glob, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
files = ['장v2/장%s.md'%c for c in ['1','2','3','4','5A','5B','6','7A','7B','8','9','10']]
pat = re.compile(r'^\*\*(정리|명제|보조정리|따름정리|정의) \{\{([^}]+)\}\}\s*(\(.*?\))?\s*(\[[^\]]*(?:\[[^\]]*\][^\]]*)*\])?\s*\.?\*\*')
for f in files:
    sec=''
    for i,line in enumerate(open(f,encoding='utf-8'),1):
        m0=re.match(r'^###\s+(\d+\.\d+)',line)
        if m0: sec=m0.group(1)
        m=pat.match(line)
        if m:
            typ,lab,name,mark=m.groups()
            # the marker may contain nested [..]; find the last [...] before '**'
            head=line.split('**')[1]
            mk=re.findall(r'\[([^\[\]]*(?:\[[^\[\]]*\][^\[\]]*)*)\]\s*\.?$',head)
            mark=mk[-1] if mk else (mark or '')
            print(f'{f}\t{i}\t{sec}\t{typ}\t{lab}\t{mark}')
