import re, glob, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
files = sorted(glob.glob('장v2/부록D_장*.md'))
for f in files:
    txt = open(f, encoding='utf-8').read()
    # items start with a heading or bold label containing {{D:...}}
    parts = re.split(r'\n(?=###? |\*\*D\.)', txt)
    for p in parts:
        m = re.search(r'\{\{D:([^}]+)\}\}', p)
        if not m: continue
        label = m.group(1)
        head = p.split('\n',1)[0][:200]
        print('=====', f, '|', label)
        print('HEAD:', head)
        for key in ['확인하는 진술', '산술 등급', '독립 재계산', '범위']:
            for line in p.split('\n'):
                s = line.strip()
                if s.startswith('- **'+key) or s.startswith('**'+key) or s.startswith('- '+key) or s.startswith(key):
                    print(key, '::', s[:1500])
                    break
