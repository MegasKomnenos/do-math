# T14: 장 파일에서 절 머리·진술 머리·라벨을 추출한다.
import re, sys, os, json, glob
root = r"C:\math\임시\주차함수_증명\장v2"
files = ["장1.md","장2.md","장3.md","장4.md","장5A.md","장5B.md","장6.md","장7A.md","장7B.md","장8.md","장9.md","장10.md","장11.md","부록A.md","부록B.md","부록C.md"] + sorted(os.path.basename(p) for p in glob.glob(os.path.join(root,"부록D_*.md")))
head_re = re.compile(r'^\*\*(정의|정리|보조정리|명제|따름정리|주석|관찰|문제|예|가정|규약|알고리즘|표기)\s+(\{\{[^}]+\}\})?\s*(\([^)]*(?:\([^)]*\)[^)]*)*\))?\s*(\[[^\]]*\])?[^*]*\*\*')
label_re = re.compile(r'\{\{(\d+|[0-9A-Z]+):([^}]+)\}\}')
out_heads = []
out_secs = []
cites = {}
for f in files:
    p = os.path.join(root,f)
    with open(p,encoding='utf-8') as fh:
        for ln, line in enumerate(fh,1):
            if line.startswith('#'):
                out_secs.append((f,ln,line.rstrip()))
            m = head_re.match(line)
            if m:
                out_heads.append((f,ln,m.group(1),m.group(2) or '',(m.group(3) or '')[:120],(m.group(4) or '')[:200]))
            for lm in label_re.finditer(line):
                cites.setdefault(lm.group(0),[]).append((f,ln))
with open(r"C:\math\임시\주차함수_증명\scripts\수학검사2\검토전체13_T14_secs.tsv","w",encoding='utf-8') as o:
    for s in out_secs: o.write("\t".join(map(str,s))+"\n")
with open(r"C:\math\임시\주차함수_증명\scripts\수학검사2\검토전체13_T14_heads.tsv","w",encoding='utf-8') as o:
    for s in out_heads: o.write("\t".join(map(str,s))+"\n")
with open(r"C:\math\임시\주차함수_증명\scripts\수학검사2\검토전체13_T14_labels.tsv","w",encoding='utf-8') as o:
    for k,v in sorted(cites.items()):
        o.write(f"{k}\t{len(v)}\t{v[0][0]}:{v[0][1]}\t"+" ".join(f"{a}:{b}" for a,b in v[:40])+"\n")
print(len(out_secs),len(out_heads),len(cites))
