# -*- coding: utf-8 -*-
"""D5 보조: 장 파일(장1–장10)만 대상으로, 「<종류> {{라벨}}의 증명」 인용 자리를 넓은 문맥(앞 200자·뒤 160자)과 함께 적고,
자기 증명 머리(「정리 X의 증명.」)와 머리 표지 안의 의존 선언을 뺀 뒤 셈한다."""
import re, glob, os, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
ROOT = r'C:\math\임시\주차함수_증명'
files = [os.path.join(ROOT,'장v2',f) for f in ['장1.md','장2.md','장3.md','장4.md','장5A.md','장5B.md','장6.md','장7A.md','장7B.md','장8.md','장9.md','장10.md']]
HEAD = re.compile(r'^\*\*(정리|보조정리|명제|따름정리|정의)\s+(\{\{[^}]+\}\})')
P = re.compile(r'(정리|보조정리|명제|따름정리)\s+\{\{([^}]+)\}\}((?:\([가-힣ㄱ-ㅎ0-9a-z]+\))?(?:·\([가-힣ㄱ-ㅎ]\))*)의 증명(?!됨)')
out=[]
for f in files:
    name=os.path.basename(f); lines=open(f,encoding='utf-8').read().split('\n'); cur=None
    for i,ln in enumerate(lines,1):
        m=HEAD.match(ln)
        if m: cur=m.group(2)
        for mm in P.finditer(ln):
            lab=mm.group(2); tail=ln[mm.end():mm.end()+6]
            if tail.startswith('.**'):  # 「정리 X의 증명.**」 — 증명 머리
                continue
            if cur and '{{'+lab+'}}'==cur and re.match(r'\s*(을|를)\s*(마친다|끝낸다|닫는다|완성|마무리)', ln[mm.end():]):
                continue
            s=max(0,mm.start()-200); e=min(len(ln),mm.end()+160)
            out.append((name,i,cur,lab+mm.group(3),ln[s:e]))
print('장 파일 인용 자리(증명 머리 제외):', len(out))
from collections import Counter
print('파일별:', dict(Counter(o[0] for o in out)))
print('둘러싼 진술 수:', len(set(o[2] for o in out)), '| 인용된 증명(라벨) 수:', len(set(o[3].split('(')[0] for o in out)))
print('인용 빈도 상위:', Counter(o[3].split('(')[0] for o in out).most_common(15))
print()
for n,o in enumerate(out,1):
    print(f'[{n}] {o[0]}:{o[1]} | 안 {o[2]} | 인용 {o[3]}\n    …{o[4]}…\n')
