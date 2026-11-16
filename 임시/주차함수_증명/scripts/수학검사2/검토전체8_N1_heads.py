# 장1·장2가 인용하는 다른 장의 진술 머리와 진술 본문(증명 전까지)을 뽑는다.
import re, glob, os, sys
root = r"C:\math\임시\주차함수_증명\장v2"
files = glob.glob(os.path.join(root, "장*.md"))
text = {}
for f in files:
    text[f] = open(f, encoding="utf-8").read().split("\n")
labels = sys.argv[1:]
for lab in labels:
    ch = lab.split(":")[0]
    found = False
    for f, lines in text.items():
        base = os.path.basename(f)
        if not base.startswith("장"+ch): continue
        for i, L in enumerate(lines):
            if ("{{"+lab+"}}" in L) and re.match(r"\*\*(정리|명제|보조정리|따름정리|정의|문제)", L):
                found = True
                out = [L]
                j = i+1
                while j < len(lines) and not lines[j].startswith("**증명") and j < i+25:
                    out.append(lines[j]); j += 1
                s = "\n".join(out)
                print(f"=== {lab} @ {base}:{i+1}\n{s[:2500]}\n")
    if not found:
        print(f"=== {lab} NOT FOUND as statement head")
