# 심사 A8 — E1 검산: 8장 라벨마다 어느 진술 블록(장8 안)·어느 파일(장9·10·11·부록)이 인용하는지 표로 만든다.
# 실행: python -I 심사_A8_인용표.py
import re, glob, os, sys
ROOT=r"C:/math/임시/주차함수_증명/"
ch8=open(ROOT+'장v2/장8.md',encoding='utf-8').read().split('\n')
hdr=re.compile(r'^\*\*(보조정리|정리|명제|따름정리|정의) \{\{(8:[A-Za-z0-9-]+)\}\}')
blocks=[]  # (start_line, label)
for i,l in enumerate(ch8,1):
    m=hdr.match(l)
    if m: blocks.append((i,m.group(2)))
    elif l.startswith('### '): blocks.append((i,l.strip()))
def block_of(i):
    cur='(머리)'
    for s,lab in blocks:
        if s<=i: cur=lab
        else: break
    return cur
labels=[lab for _,lab in blocks if lab.startswith('8:')]
files=sorted(glob.glob(ROOT+'장v2/*.md'))+[ROOT+'장부_v2.md']
out=[]
for lab in labels:
    tok='{{'+lab+'}}'
    internal={}
    for i,l in enumerate(ch8,1):
        if tok in l:
            b=block_of(i)
            if b==lab and hdr.match(l): continue
            internal.setdefault(b,[]).append(i)
    ext={}
    for f in files:
        if f.endswith('장8.md'): continue
        for i,l in enumerate(open(f,encoding='utf-8').read().split('\n'),1):
            if tok in l: ext.setdefault(os.path.basename(f),[]).append(i)
    out.append(f"== {lab}")
    out.append("   장8 내부 인용(블록: 행): "+'; '.join(f"{b}: {v}" for b,v in internal.items()) if internal else "   장8 내부 인용: 없음")
    out.append("   외부: "+'; '.join(f"{f}: {v}" for f,v in ext.items()) if ext else "   외부: 없음")
open(sys.argv[0].replace('.py','_out.txt'),'w',encoding='utf-8').write('\n'.join(out)); print('\n'.join(out))
