# -*- coding: utf-8 -*-
"""장 파일에서 절 머리와 진술 머리, 정의된 라벨을 추출한다."""
import re, sys, glob, os, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
root = r"C:\math\임시\주차함수_증명\장v2"
order = ["장1","장2","장3","장4","장5A","장5B","장6","장7A","장7B","장8","장9","장10","장11","부록A","부록B","부록C"]
hdr = re.compile(r'^\*\*(정리|보조정리|명제|따름정리|정의|관찰|주의|예|가정|추측)\s+\{\{(\d+):([^}]+)\}\}')
for name in order:
    p = os.path.join(root, name + ".md")
    with open(p, encoding='utf-8') as f:
        for i, line in enumerate(f, 1):
            if line.startswith('#'):
                print(f"{name}:{i}: {line.rstrip()[:120]}")
            m = hdr.match(line)
            if m:
                print(f"{name}:{i}: STMT {m.group(1)} {{{{{m.group(2)}:{m.group(3)}}}}} :: {line.rstrip()[:260]}")
