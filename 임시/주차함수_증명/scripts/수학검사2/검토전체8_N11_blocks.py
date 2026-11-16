# 검토전체8 N11: 진술 블록 지도(라벨 -> 파일, 절, 머리, 본문)를 만들고 11.2/11.3/11.4를 대조한다.
import re, glob, os, json, sys
root = r"C:\math\임시\주차함수_증명\장v2"
order = ["장1","장2","장3","장4","장5A","장5B","장6","장7A","장7B","장8","장9","장10","장11"]
head_re = re.compile(r"^\*\*(정의|정리|명제|보조정리|따름정리)\s+\{\{([^}]+)\}\}\s*([\(\[].*?|\.)\*\*")
sec_re = re.compile(r"^(#{2,4})\s+((\d+(?:\.\d+)*)\.?\s.*)")
blocks = {}   # label -> dict
seq = []
for ch in order:
    f = os.path.join(root, ch + ".md")
    lines = open(f, encoding="utf-8").read().split("\n")
    cur_sec = None; cur = None
    for i, ln in enumerate(lines, 1):
        ms = sec_re.match(ln)
        if ms:
            cur_sec = ms.group(3)
            # 절이 바뀌면 블록 종료
            cur = None
        mh = head_re.match(ln)
        if mh:
            cur = mh.group(2)
            blocks[cur] = dict(file=ch, line=i, sec=cur_sec, kind=mh.group(1), head=mh.group(3), text=[ln])
            seq.append(cur)
            continue
        if cur is not None:
            blocks[cur]["text"].append(ln)
            if ln.strip().endswith("∎"):
                cur = None   # 증명 끝
for k, v in blocks.items():
    v["text"] = "\n".join(v["text"])
json.dump(blocks, open(r"C:\math\임시\주차함수_증명\scripts\수학검사2\_N11_blocks.json", "w", encoding="utf-8"), ensure_ascii=False)
print("blocks:", len(blocks))

# ---- 11.2 완전성과 쓰인 곳
ch11 = open(os.path.join(root, "장11.md"), encoding="utf-8").read().split("\n")
rows = [[c.strip() for c in ln.strip().strip("|").split(" | ")] for ln in ch11 if ln.startswith("| 부록 D.{{D:")]
in_table = {}
for cells in rows:
    key = re.match(r"부록 D\.\{\{D:([^}]+)\}\}", cells[0]).group(1)
    labs = re.findall(r"\{\{([^}]+)\}\}", cells[1])
    secs = cells[3]
    for l in labs:
        in_table.setdefault(l, []).append((key, secs))
        b = blocks.get(l)
        if not b:
            print("!! 11.2 표 라벨 없음:", l); continue
        # 절 번호 비교: 표의 '쓰인 곳'에 그 진술의 절이 들어 있는가
        secs_list = [s.strip() for s in re.split(r"[·,]", secs)]
        if b["sec"] not in secs_list:
            print(f"[11.2 쓰인 곳] {key}: {l} 진술은 {b['file']} {b['sec']}절, 표는 {secs}")
        # 머리에 계산 표지가 있는가
        if "계산 보조" not in b["head"] and "계산 증거" not in b["head"]:
            print(f"[11.2 머리 표지 없음] {key}: {l} 머리={b['head'][:200]}")
# 거꾸로: 계산 표지를 단 진술이 모두 표에 있는가
for l, b in blocks.items():
    if ("계산 보조" in b["head"] or "계산 증거" in b["head"]) and l not in in_table:
        print(f"[11.2 표에 없음] {b['file']} {l} 머리={b['head'][:200]}")
