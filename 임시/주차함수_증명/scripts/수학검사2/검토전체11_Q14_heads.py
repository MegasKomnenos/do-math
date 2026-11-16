# Q14: 장 파일의 진술 머리와 라벨을 뽑아 둔다(자리 찾기용).
import re, glob, os, sys
root = r"C:\math\임시\주차함수_증명\장v2"
files = ["장1.md","장2.md","장3.md","장4.md","장5A.md","장5B.md","장6.md","장7A.md","장7B.md","장8.md","장9.md","장10.md","장11.md"]
head_re = re.compile(r'^\*\*(정의|정리|명제|보조정리|따름정리|관찰|주의|예|알고리즘|가정|문제|추측|약속|규약)\s+\{\{(\d+):([^}]+)\}\}\s*(.*?)\*\*')
out = []
for f in files:
    p = os.path.join(root, f)
    sec = ""
    for i, line in enumerate(open(p, encoding="utf-8"), 1):
        m = re.match(r'^(#{2,4})\s+(.*)', line)
        if m:
            sec = m.group(2).strip()
        h = head_re.match(line)
        if h:
            kind, ch, lab, rest = h.groups()
            out.append(f"{f}\t{i}\t{kind}\t{ch}:{lab}\t{sec}\t{rest[:160]}")
open(r"C:\math\임시\주차함수_증명\scripts\수학검사2\검토전체11_Q14_heads.tsv","w",encoding="utf-8").write("\n".join(out)+"\n")
print(len(out))
# labels referenced anywhere
labs = {}
for f in files + glob.glob(os.path.join(root,"부록*.md")):
    p = f if os.path.isabs(f) else os.path.join(root, f)
    txt = open(p, encoding="utf-8").read()
    for m in re.finditer(r'\{\{(\d+|D):([^}]+)\}\}', txt):
        labs.setdefault(m.group(1)+":"+m.group(2), set()).add(os.path.basename(p))
defined = set(l.split("\t")[3] for l in out)
print("referenced but not defined (non-D):", sorted(l for l in labs if not l.startswith("D:") and l not in defined))
