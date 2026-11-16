# H14: 의존지도_v2.md 1절 표를 장 파일 현행 머리와 견준다(절·첫 판 번호·요지·지위·머리 인용 라벨·기록 식별자).
import re, os
root = r"C:\math\임시\주차함수_증명"
files = ["장1.md","장2.md","장3.md","장4.md","장5A.md","장5B.md","장6.md","장7A.md","장7B.md","장8.md","장9.md","장10.md","장11.md"]
head_re = re.compile(r"^\*\*(정리|보조정리|명제|따름정리|정의)\s+\{\{(\d+):([^}]+)\}\}(?!의)\s*(.*?)\*\*")
sec_re = re.compile(r"^(#+)\s+(\d+\.\d+)\b")
lab_re = re.compile(r"\{\{(\d+:[^}]+)\}\}")
heads = {}; order = []
cur = None
for f in files:
    lines = open(os.path.join(root, "장v2", f), encoding="utf-8").read().split("\n")
    idx = []
    for i, line in enumerate(lines):
        m = sec_re.match(line)
        if m: cur_s = m.group(2)
        if sec_re.match(line):
            lines[i] = line  # keep
    cur = None
    marks = []
    for i, line in enumerate(lines):
        m = sec_re.match(line)
        if m: cur = m.group(2); continue
        if re.match(r"^\*\*(정의|정리|명제|보조정리|따름정리) \{\{(\d+):([A-Za-z][A-Za-z0-9\-]*)\}\}의 증명\.\*\*", line):
            mm = re.match(r"^\*\*(?:정의|정리|명제|보조정리|따름정리) \{\{(\d+):([A-Za-z][A-Za-z0-9\-]*)\}\}", line)
            marks.append((i, "defer", f"{mm.group(1)}:{mm.group(2)}", cur)); continue
        m = head_re.match(line)
        if m:
            kind, ch, lab, rest = m.groups()
            rest = rest.strip(); name = None; r = rest
            if r.startswith("("):
                d = 0
                for j, c in enumerate(r):
                    if c == "(": d += 1
                    elif c == ")":
                        d -= 1
                        if d == 0: name = r[1:j].strip(); r = r[j+1:].strip(); break
            status = None; recs = None
            if r.startswith("["):
                d = 0
                for j, c in enumerate(r):
                    if c == "[": d += 1
                    elif c == "]":
                        d -= 1
                        if d == 0:
                            inner = r[1:j]
                            status, recs = (inner.rsplit(";", 1) if ";" in inner else (inner, ""))
                            break
            headlabs = [x for x in lab_re.findall(line) if x != f"{ch}:{lab}"]
            marks.append((i, "head", f"{ch}:{lab}", dict(file=f, ln=i+1, kind=kind, sec=cur, name=name, status=(status or "").strip(), recs=(recs or "").strip(), headlabs=headlabs)))
    defers = []
    for n, (i, kind, key, d) in enumerate(marks):
        end = marks[n+1][0] if n+1 < len(marks) else len(lines)
        body = lines[i+1:end]
        if kind == "head":
            d["bodyset"] = set(lab_re.findall(chr(10).join(body))) - {key}
            heads[key] = d; order.append(key)
        else:
            defers.append((key, [lines[i]] + body))
    for key, bl in defers:
        if key in heads: heads[key]["bodyset"].update(set(lab_re.findall(chr(10).join(bl))) - {key})

# 의존지도 1절 파싱
rows = []
intable = False
for ln, line in enumerate(open(os.path.join(root, "의존지도_v2.md"), encoding="utf-8"), 1):
    if line.startswith("## 1."): intable = True; continue
    if line.startswith("## 2."): break
    if intable and line.startswith("| `{{"):
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        rows.append((ln, cells))
allkeys=set(heads)
for k,d in heads.items(): d['bodylabs']=sorted((d['bodyset'] & allkeys) - set(d['headlabs']))
print("장 파일 머리", len(heads), "의존지도 1절 행", len(rows))
seen = set()
for ln, c in rows:
    lab = c[0].strip("`").strip("{}")
    seen.add(lab)
    h = heads.get(lab)
    if not h:
        print(f"[지도 {ln}] 장 파일에 없음: {lab}"); continue
    probs = []
    if c[1] != h["sec"]: probs.append(f"절 지도={c[1]} 파일={h['sec']}")
    # 첫 판 번호
    mm = re.match(r"old-(\d+)-(\d+)$", lab.split(":")[1])
    exp_old = f"{h['kind']} {mm.group(1)}.{mm.group(2)}" if mm else "새 진술"
    if c[2] != exp_old: probs.append(f"첫판 지도={c[2]!r} 기대={exp_old!r}")
    if h["name"] and re.sub(r"\s", "", c[3]) != re.sub(r"\s", "", h["name"]): probs.append(f"요지 지도={c[3]!r} 파일={h['name']!r}")
    st = h["status"] if h["kind"] != "정의" or h["status"] else "정의"
    if h["kind"] == "정의" and not h["status"]: st = "정의"
    # 지도의 지위 열은 라벨을 {{...}}로 적고 파일은 {{...}}로 같게 적음
    if re.sub(r"\s", "", c[4]) != re.sub(r"\s", "", st):
        probs.append(f"지위 지도={c[4]!r} 파일={st!r}")
    # 머리 인용 라벨
    inp = c[5]
    headpart = inp.split("본문 인용:")[0]
    jl = re.findall(r"\{\{(\d+:[^}]+)\}\}", headpart)
    if sorted(jl) != sorted(h["headlabs"]): probs.append(f"머리 인용 지도={jl} 파일={h['headlabs']}")
    bodypart = inp.split("본문 인용:")[1] if "본문 인용:" in inp else ""
    bl = sorted(set(re.findall(r"\{\{(\d+:[^}]+)\}\}", bodypart)))
    if bl != h["bodylabs"]:
        only_map = sorted(set(bl) - set(h["bodylabs"])); only_file = sorted(set(h["bodylabs"]) - set(bl))
        probs.append(f"본문 인용 차이: 지도에만={only_map} 파일에만={only_file}")
    # 기록 식별자(머리의 ; 뒤)
    recs_file = sorted(set(re.findall(r"r[0-9a-f]{7}", h["recs"])))
    recs_map = sorted(set(re.findall(r"r[0-9a-f]{7}", c[6])))
    if h["kind"] != "정의" or recs_file:
        if recs_file and set(recs_file) != set(recs_map): probs.append(f"기록 지도={recs_map} 파일={recs_file}")
    if probs:
        print(f"[지도 {ln}] {lab} ({h['file']}:{h['ln']}): " + " ; ".join(probs))
for k in order:
    if k not in seen: print("지도에 없음:", k, heads[k]["file"], heads[k]["ln"])
