# -*- coding: utf-8 -*-
"""T11: 부록 A 「뜻」 열의 식 조각이 본문 어디에도 같은 꼴로 없는 행을 찾는다(자리 찾기용; 다시 적은 꼴은 손으로 본다)."""
import re, os, glob
ROOT = r"C:\math\임시\주차함수_증명"; CH = os.path.join(ROOT, "장v2")
body = ""
for f in glob.glob(os.path.join(CH, "장*.md")):
    if f.endswith('장11.md'): continue
    body += open(f, encoding='utf-8').read()
def norm(s): return re.sub(r'\s+', '', s).replace(r'\,', '').replace(r'\!', '').replace('\bigl','').replace('\bigr','').replace('\left','').replace('\right','')
B = norm(body)
for line in open(os.path.join(CH, '부록A.md'), encoding='utf-8'):
    if not line.startswith('| $'): continue
    c = [x.strip() for x in line.strip().strip('|').split(' | ')]
    if len(c) < 2: continue
    frags = [f for f in re.findall(r'\$([^$]+)\$', c[1]) if len(f) >= 14]
    missing = [f for f in frags if norm(f) not in B]
    if missing:
        print(f"{c[0][:40]} :: " + " ;; ".join(m[:90] for m in missing))
