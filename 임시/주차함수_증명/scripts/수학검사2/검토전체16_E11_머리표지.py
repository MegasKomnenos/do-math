# 11.2·11.3에 든 진술 라벨마다 본문 머리의 표지와 놓인 절을 찾아 출력한다.
import re, glob, os, sys
root = r"C:\math\임시\주차함수_증명"
heads = {}   # label -> (file, line_no, section, header text)
for f in sorted(glob.glob(os.path.join(root, "장v2", "장*.md"))):
    sec = None
    for i, line in enumerate(open(f, encoding="utf-8"), 1):
        m = re.match(r"^#{2,4}\s+(\d+(?:\.\d+)*)", line)
        if m: sec = m.group(1); continue
        m = re.match(r"^\*\*(정리|명제|보조정리|따름정리|정의)\s+\{\{(\d+[AB]?:[a-zA-Z0-9-]+)\}\}(.*?)\*\*", line)
        if m:
            lab = m.group(2).replace("5A:", "5:").replace("5B:", "5:").replace("7A:", "7:").replace("7B:", "7:")
            heads[lab] = (os.path.basename(f), i, sec, m.group(1), m.group(3).strip())
ch11 = open(os.path.join(root, "장v2", "장11.md"), encoding="utf-8").read()
want = sorted(set(re.findall(r"\{\{(\d+:[a-zA-Z0-9-]+)\}\}", ch11)))
mode = sys.argv[1] if len(sys.argv) > 1 else "all"
for lab in want:
    h = heads.get(lab)
    if not h: print("[머리 없음]", lab); continue
    f, i, sec, kind, rest = h
    if mode == "calc" and "계산" not in rest and "binary64" not in rest: continue
    print(f"{lab:28s} {kind:5s} {sec:6s} {f}:{i}  {rest[:260]}")
