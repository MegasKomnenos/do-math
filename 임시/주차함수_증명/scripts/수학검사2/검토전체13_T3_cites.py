import re, glob, os
root = r"C:\math\임시\주차함수_증명\장v2"
text5A = open(os.path.join(root,"장5A.md"),encoding="utf-8").read().split("\n")
heads = {}
for i,l in enumerate(text5A,1):
    m = re.match(r"\*\*(정리|보조정리|명제|따름정리|정의) \{\{5:([^}]+)\}\}", l)
    if m: heads[m.group(2)] = i
files = sorted(glob.glob(os.path.join(root,"*.md")))
for lab, hl in heads.items():
    cites = []
    for f in files:
        for i,l in enumerate(open(f,encoding="utf-8").read().split("\n"),1):
            if os.path.basename(f)=="장5A.md" and i==hl: continue
            for m in re.finditer(r"\{\{5:"+re.escape(lab)+r"\}\}(\([가-힣]\))?", l):
                cites.append(f"{os.path.basename(f)}:{i}{m.group(1) or ''}")
    print(f"{lab} (head 5A:{hl}): {len(cites)} -> {' '.join(cites) if len(cites)<=14 else ' '.join(cites[:14])+' ...'}")
