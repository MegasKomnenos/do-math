# 9장·10장에서 지정한 앞 장 라벨이 인용되는 줄과, 그 줄을 품은 진술(마지막으로 지난 머리)을 출력한다.
import re, os, sys
root = r"C:\math\임시\주차함수_증명"
targets = sys.argv[2:]
f = sys.argv[1]
cur = "(머리말/준비 문단)"; sec = ""
for i, line in enumerate(open(os.path.join(root, "장v2", f), encoding="utf-8"), 1):
    m = re.match(r"^#{2,4}\s+(\d+(?:\.\d+)*)", line)
    if m: sec = m.group(1); cur = f"(절 {sec} 준비 문단)"; continue
    m = re.match(r"^\*\*(정리|명제|보조정리|따름정리|정의)\s+\{\{([^}]+)\}\}", line)
    if m:
        if "의 증명" in line[:len(m.group(0))+12]: cur = f"{m.group(1)} {m.group(2)} 의 증명"
        else: cur = f"{m.group(1)} {m.group(2)} 머리"
    elif line.startswith("**증명"): cur = cur.replace(" 머리", "") + " 증명"
    elif line.strip() == "" : pass
    for t in targets:
        if "{{" + t + "}}" in line:
            idx = line.index("{{" + t + "}}")
            print(f"{f}:{i:4d} [{sec}] <{cur}> {t} :: …{line[max(0,idx-120):idx+80].strip()}…")
