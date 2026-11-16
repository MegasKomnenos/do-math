import re,glob,os
root=r"C:\math\임시\주차함수_증명\장v2"
src=open(os.path.join(root,"장7A.md"),encoding="utf-8").read()
labels=set(re.findall(r"\{\{(\d+|D):([^}]+)\}\}",src))
files={f:open(f,encoding="utf-8").read() for f in glob.glob(os.path.join(root,"*.md"))}
heads={}
for f,t in files.items():
    for m in re.finditer(r"^\*\*(정리|명제|보조정리|따름정리|정의) \{\{([^}]+)\}\}|^### D\.\{\{(D:[^}]+)\}\}",t,re.M):
        lab=m.group(2) or m.group(3); heads.setdefault(lab,[]).append(os.path.basename(f))
missing=[]
for ch,lab in sorted(labels):
    key=f"{ch}:{lab}"
    if key not in heads: missing.append(key)
print("labels used:",len(labels)); print("missing heads:",missing)
# duplicates within 7A heads
h7=re.findall(r"^\*\*(?:정리|명제|보조정리|따름정리|정의) \{\{7:([^}]+)\}\}",src,re.M)
from collections import Counter
print("7A heads:",len(h7),[x for x,c in Counter(h7).items() if c>1])
# which 7 labels used in 7A are defined in 7B (forward refs)
fw=[l for l in h7]
used7=[lab for ch,lab in labels if ch=="7"]
print("7-labels used but defined in 7B:",sorted(set(l for l in used7 if l not in h7)))
# column certification counts
B=lambda k:-(-k*k//4)
d1=sum(2*B(k)-2*k for k in range(121,161)); d2=sum(2*B(k)-2*k for k in range(161,501))
r1=sum(B(k)+1 for k in range(121,161)); r2=sum(B(k)+1 for k in range(161,501))
print(d1,d2,r1,r2)
