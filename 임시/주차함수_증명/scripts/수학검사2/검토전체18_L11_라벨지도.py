# 모든 장 파일에서 진술 머리의 라벨 → (파일, 행, 절) 지도를 만들고, 장11의 라벨이 모두 정의되어 있는지, 11.2 표의 「놓인 곳」이 맞는지 본다.
import re, glob, io
root = r"C:\math\임시\주차함수_증명\장v2"
defs = {}
sec_re = re.compile(r"^###\s+(\d+\.\d+)\b")
head_re = re.compile(r"^\*\*(정리|보조정리|명제|따름정리|정의|관찰|추측|문제)\s+\{\{(\d+[AB]?|[A-Z]|D):([^}]+)\}\}")
for f in sorted(glob.glob(root + r"\장*.md")):
    cur = None
    for i, l in enumerate(open(f, encoding="utf-8"), 1):
        m = sec_re.match(l)
        if m: cur = m.group(1)
        m = head_re.match(l)
        if m:
            key = f"{m.group(2)}:{m.group(3)}"
            defs.setdefault(key, []).append((m.group(1), f.split("\\")[-1], i, cur))
ch11 = open(root + r"\장11.md", encoding="utf-8").read()
used = re.findall(r"(정리|보조정리|명제|따름정리|정의)?\s*\{\{(\d+[AB]?):([^}]+)\}\}", ch11)
out = io.StringIO()
out.write("== 장11에서 쓴 라벨 가운데 정의가 없는 것\n")
for kind, ch, lab in sorted(set(used)):
    key = f"{ch}:{lab}"
    if key not in defs:
        out.write(f"  {kind} {key}\n")
out.write("== 장11에서 쓴 라벨의 진술 종류가 정의와 다른 것\n")
for kind, ch, lab in sorted(set(used)):
    key = f"{ch}:{lab}"
    if key in defs and kind and defs[key][0][0] != kind:
        out.write(f"  장11: {kind} {key} / 정의: {defs[key]}\n")
out.write("== 중복 정의 라벨\n")
for k,v in defs.items():
    if len(v)>1: out.write(f"  {k}: {v}\n")
out.write("== 11.2 표 「놓인 곳」 대조\n")
for l in ch11.splitlines():
    if not l.startswith("| 부록 D.{{D:"): continue
    cells = [c.strip() for c in l.strip().strip("|").split(" | ")]
    labs = re.findall(r"\{\{(\d+[AB]?):([^}]+)\}\}", cells[1])
    secs = set()
    for ch, lab in labs:
        d = defs.get(f"{ch}:{lab}")
        if d: secs.add(d[0][3])
    out.write(f"  {cells[0][8:40]:34s} 표: {cells[3]:10s} 실제: {sorted(secs)}  {'' if set(cells[3].split('·'))==secs else '!!'}\n")
open(r"C:\math\임시\주차함수_증명\scripts\수학검사2\검토전체18_L11_라벨지도_out.txt","w",encoding="utf-8").write(out.getvalue())
import json
json.dump(defs, open(r"C:\math\임시\주차함수_증명\scripts\수학검사2\검토전체18_L11_라벨지도.json","w",encoding="utf-8"), ensure_ascii=False)
print(out.getvalue())
