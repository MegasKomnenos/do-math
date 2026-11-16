# -*- coding: utf-8 -*-
"""라벨의 블록(머리부터 다음 머리/절 제목 직전까지)을 출력한다. 인자: 라벨 [최대글자수] [--after: 뒤문단만]"""
import re, glob, os, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
BASE = r"C:\math\임시\주차함수_증명\장v2"
HEAD = re.compile(r'^\*\*(정리|명제|보조정리|따름정리|정의)\s+\{\{(\d+[AB]?:[^}]+)\}\}(?!의 증명)')
lab = sys.argv[1]; lim = int(sys.argv[2]) if len(sys.argv)>2 and sys.argv[2].isdigit() else 3000
only_after = '--after' in sys.argv
for f in sorted(glob.glob(os.path.join(BASE,'장*.md'))):
    lines = open(f,encoding='utf-8').read().split('\n')
    for i, ln in enumerate(lines):
        h = HEAD.match(ln)
        if h and h.group(2)==lab:
            j=i+1
            while j<len(lines) and not HEAD.match(lines[j]) and not re.match(r'#{2,4}\s', lines[j]): j+=1
            blk = lines[i:j]
            if only_after:
                txt='\n'.join(blk); k=txt.rfind('∎'); txt = txt[k+1:] if k>0 else '(∎ 없음)\n'+txt
            else: txt='\n'.join(blk)
            print(f"### {os.path.basename(f)}:{i+1}–{j}  [{lab}]")
            print(txt[:lim]); print()
