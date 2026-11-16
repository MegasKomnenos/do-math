# 검토전체8 N11: 장 파일에서 진술 머리와 부록 D 항목 머리를 추출한다.
import re, glob, os, json, sys
root = r"C:\math\임시\주차함수_증명\장v2"
files = sorted(glob.glob(os.path.join(root, "*.md")))
head_re = re.compile(r"^\*\*(정의|정리|명제|보조정리|따름정리)\s+\{\{([^}]+)\}\}\s*(.*?)\*\*")
out = []
dheads = []
for f in files:
    name = os.path.basename(f)
    with open(f, encoding="utf-8") as fh:
        for i, line in enumerate(fh, 1):
            m = head_re.match(line)
            if m:
                out.append((name, i, m.group(1), m.group(2), m.group(3)[:400]))
            m2 = re.match(r"^\*\*D\.\{\{D:([^}]+)\}\}", line) or re.match(r"^###?\s*.*\{\{D:([^}]+)\}\}", line)
            if m2:
                dheads.append((name, i, m2.group(1), line.strip()[:300]))
with open(r"C:\math\임시\주차함수_증명\scripts\수학검사2\_N11_heads.tsv", "w", encoding="utf-8") as fh:
    for r in out:
        fh.write("\t".join(str(x) for x in r) + "\n")
with open(r"C:\math\임시\주차함수_증명\scripts\수학검사2\_N11_dheads.tsv", "w", encoding="utf-8") as fh:
    for r in dheads:
        fh.write("\t".join(str(x) for x in r) + "\n")
print(len(out), "heads;", len(dheads), "D heads")
