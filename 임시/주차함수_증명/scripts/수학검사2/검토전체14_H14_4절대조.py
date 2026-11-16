# H14: 장부 4절(이름 사전)을 장 파일 머리와 견준다(첫 판 번호·종류·이름·기록 이름·절·라벨).
import re, os
root = r"C:\math\임시\주차함수_증명"
files = ["장1.md","장2.md","장3.md","장4.md","장5A.md","장5B.md","장6.md","장7A.md","장7B.md","장8.md","장9.md","장10.md","장11.md"]
head_re = re.compile(r"^\*\*(정리|보조정리|명제|따름정리|정의)\s+\{\{(\d+):([^}]+)\}\}(?!의)\s*(.*?)\*\*")
sec_re = re.compile(r"^(#+)\s+(\d+\.\d+)\b")
heads = {}
for f in files:
    cur = None
    for ln, line in enumerate(open(os.path.join(root, "장v2", f), encoding="utf-8"), 1):
        m = sec_re.match(line)
        if m: cur = m.group(2); continue
        m = head_re.match(line)
        if m:
            kind, ch, lab, rest = m.groups(); rest = rest.strip(); name = None
            if rest.startswith("("):
                d = 0
                for j, c in enumerate(rest):
                    if c == "(": d += 1
                    elif c == ")":
                        d -= 1
                        if d == 0: name = rest[1:j].strip(); break
            heads[f"{ch}:{lab}"] = dict(file=f, ln=ln, kind=kind, sec=cur, name=name)
lines = open(os.path.join(root, "장부_v2.md"), encoding="utf-8").read().split("\n")
start = next(i for i, l in enumerate(lines) if l.startswith("## 4. "))
end = next(i for i, l in enumerate(lines) if l.startswith("## 5. "))
rows = []
for i in range(start, end):
    l = lines[i]
    if l.startswith("| ") and not l.startswith("| 첫 판 번호") and not l.startswith("|---"):
        rows.append((i + 1, [c.strip() for c in l.strip().strip("|").split("|")]))
print("4절 행", len(rows))
seen = set(); nolabel = []
for ln, c in rows:
    if len(c) < 6:
        print(f"[장부 {ln}] 열 수 {len(c)}: {c}"); continue
    old, kind, name, recname, sec, lab = c[:6]
    m = re.search(r"\{\{(\d+:[^}]+)\}\}", lab)
    if not m:
        nolabel.append((ln, c)); continue
    key = m.group(1); seen.add(key)
    h = heads.get(key)
    if not h:
        nolabel.append((ln, c)); continue
    probs = []
    if kind != h["kind"]: probs.append(f"종류 장부={kind} 파일={h['kind']}")
    if sec != h["sec"]: probs.append(f"절 장부={sec} 파일={h['sec']}")
    mm = re.match(r"old-(\d+)-(\d+)$", key.split(":")[1])
    exp_old = f"{mm.group(1)}.{mm.group(2)}" if mm else "—"
    if old != exp_old: probs.append(f"첫판 장부={old} 기대={exp_old}")
    hn = h["name"] or ""
    # 머리 괄호: "이름; 기록 [r...]의 X" 꼴
    if ";" in hn:
        hname, hrec = [x.strip() for x in hn.split(";", 1)]
    else:
        hname, hrec = hn.strip(), ""
    if re.sub(r"\s", "", name) != re.sub(r"\s", "", hname): probs.append(f"이름 장부={name!r} 파일={hname!r}")
    if re.sub(r"\s", "", recname) != re.sub(r"\s", "", hrec): probs.append(f"기록이름 장부={recname!r} 파일={hrec!r}")
    if probs: print(f"[장부 {ln}] {key} ({h['file']}:{h['ln']}): " + " ; ".join(probs))
print("--- 라벨이 장 파일에 없거나 라벨 없는 행:", len(nolabel))
for ln, c in nolabel: print(f"  [장부 {ln}] " + " | ".join(c)[:220])
print("--- 장 파일에 있으나 4절에 없는 라벨:")
for k, h in heads.items():
    if k not in seen: print("  ", k, h["file"], h["ln"])
