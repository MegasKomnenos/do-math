# 검토전체8 N11: 11.3 역방향 — 입력을 인용하는 9·10장 진술/7:old-6-22 가운데 표에 적히지 않은 것.
import re, json, os
blocks = json.load(open(r"C:\math\임시\주차함수_증명\scripts\수학검사2\_N11_blocks.json", encoding="utf-8"))
root = r"C:\math\임시\주차함수_증명\장v2"
ch11 = open(os.path.join(root, "장11.md"), encoding="utf-8").read().split("\n")
tables = {}; cur = None
for ln in ch11:
    if ln.startswith("**공유 입력.**"): cur = "공유"
    elif ln.startswith("**첫째 증명의 고유 입력.**"): cur = "첫째"
    elif ln.startswith("**둘째 증명의 고유 입력.**"): cur = "둘째"
    elif ln.startswith("### 11.4"): cur = None
    if cur and ln.startswith("| ") and not ln.startswith("| 입력") and not ln.startswith("|---"):
        tables.setdefault(cur, []).append([c.strip() for c in ln.strip().strip("|").split(" | ")])
def labels(s): return re.findall(r"\{\{(\d+[A-Za-z]*:[^}]+)\}\}", s)
for name, rows in tables.items():
    for cells in rows:
        inputs = labels(cells[0])
        listed = set(labels(" ".join(cells[2:])))
        for l in inputs:
            for k, b in blocks.items():
                if k == l or k in inputs: continue
                if (b["file"] in ("장9", "장10") or k == "7:old-6-22") and "{{"+l+"}}" in b["text"] and k not in listed:
                    # 문맥 한 줄
                    idx = b["text"].find("{{"+l+"}}")
                    ctx = b["text"][max(0, idx-120): idx+80].replace("\n", " ")
                    print(f"[{name}] 입력 {l} 을 {b['file']} {b['kind']} {k}({b['sec']}) 이 인용하나 표에 없음\n      …{ctx}…")
