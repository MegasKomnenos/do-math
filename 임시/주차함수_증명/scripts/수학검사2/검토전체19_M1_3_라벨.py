# M1: 장1·장2가 인용하는 라벨 {{장:이름}}이 해당 장 파일의 진술 머리에 같은 유형으로 존재하는지
import re, glob, os, sys
root = r"C:\math\임시\주차함수_증명\장v2"
files = {os.path.basename(f): open(f, encoding="utf-8").read() for f in glob.glob(os.path.join(root, "*.md"))}
heads = {}
for fn, txt in files.items():
    for m in re.finditer(r"\*\*(정리|명제|보조정리|따름정리|정의)\s+\{\{(\w+):([\w\-]+)\}\}", txt):
        heads.setdefault((m.group(2), m.group(3)), []).append((m.group(1), fn))
# D items
for fn, txt in files.items():
    for m in re.finditer(r"\{\{D:([\w\-]+)\}\}", txt):
        pass
dheads = set()
for fn, txt in files.items():
    if fn.startswith("부록D"):
        for m in re.finditer(r"#+\s*D\.\{\{D:([\w\-]+)\}\}|\*\*D\.\{\{D:([\w\-]+)\}\}", txt):
            dheads.add(m.group(1) or m.group(2))
for target in ["장1.md", "장2.md"]:
    txt = files[target]
    for m in re.finditer(r"(정리|명제|보조정리|따름정리|정의)?\s*(\{\{(\w+):([\w\-]+)\}\})", txt):
        typ, ch, name = m.group(1), m.group(3), m.group(4)
        if ch == "D":
            if name not in dheads: print(target, "D item missing:", name)
            continue
        key = (ch, name)
        if key not in heads: print(target, "MISSING label", ch, name, "cited as", typ); continue
        types = {t for t, _ in heads[key]}
        if typ and typ not in types: print(target, "TYPE MISMATCH", ch, name, "cited", typ, "defined", heads[key])
print("done")
