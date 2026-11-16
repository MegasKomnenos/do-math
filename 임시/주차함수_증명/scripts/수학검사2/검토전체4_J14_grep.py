# -*- coding: utf-8 -*-
"""J14 helper: python regex grep over 장v2/*.md. Patterns are read from stdin, one per line
(avoids MSYS backslash mangling; write ¥ for a backslash). Options on the command line:
  -w WIDTH  context width (default 60)   -n MAX  max printed matches per pattern (default 40)
  -f GLOB   file glob relative to project root (default 장v2/*.md)   -c  counts only
"""
import re, sys, io, glob
from pathlib import Path
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stdin = io.TextIOWrapper(sys.stdin.buffer, encoding='utf-8')
ROOT = Path(r'C:\math\임시\주차함수_증명')
args = sys.argv[1:]
width = 60; maxn = 40; fglob = '장v2/*.md'; count_only = False
i = 0
while i < len(args):
    if args[i] == '-w': width = int(args[i+1]); i += 2
    elif args[i] == '-n': maxn = int(args[i+1]); i += 2
    elif args[i] == '-f': fglob = args[i+1]; i += 2
    elif args[i] == '-c': count_only = True; i += 1
    else: i += 1
files = sorted(glob.glob(str(ROOT/fglob)))
texts = {Path(f).name: Path(f).read_text(encoding='utf-8').splitlines() for f in files}
for pat in sys.stdin.read().splitlines():
    pat = pat.rstrip('\n')
    if not pat.strip(): continue
    print(f'=== {pat}')
    rx = re.compile(pat.replace('¥', chr(92)*2))
    total = 0; counts = []
    for name, lines in texts.items():
        c = 0
        for ln, L in enumerate(lines, 1):
            for m in rx.finditer(L):
                c += 1; total += 1
                if not count_only and total <= maxn:
                    a = max(0, m.start()-width); b = min(len(L), m.end()+width)
                    print(f'{name}:{ln}: …{L[a:b]}…')
        if c: counts.append(f'{name}:{c}')
    print('## ' + '  '.join(counts) + f'  | total {total}')
