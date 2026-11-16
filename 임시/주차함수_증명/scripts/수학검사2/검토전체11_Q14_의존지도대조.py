# Q14: 의존지도 1절(2026-11-16 04:38 생성)을 현행 장 파일 머리와 대조한다(자리 찾기용).
import re, os
root = r"C:\math\임시\주차함수_증명"
files = ["장1.md","장2.md","장3.md","장4.md","장5A.md","장5B.md","장6.md","장7A.md","장7B.md","장8.md","장9.md","장10.md","장11.md"]
head_re = re.compile(r'^\*\*(정의|정리|명제|보조정리|따름정리)\s+\{\{(\d+):([^}]+)\}\}\s*(.*?)\*\*')
cur = {}; order = []
for f in files:
    sec = ""
    lines = open(os.path.join(root,"장v2",f), encoding="utf-8").read().splitlines()
    for i, line in enumerate(lines, 1):
        m = re.match(r'^(#{2,4})\s+(.*)', line)
        if m: sec = m.group(2).strip()
        h = head_re.match(line)
        if h:
            kind, ch, lab, rest = h.groups()
            if rest.startswith("의 증명"): continue
            key = f"{ch}:{lab}"
            r2 = rest.rstrip().rstrip('.')
            st = None; pre = r2
            if r2.endswith(']'):
                depth = 0
                for j in range(len(r2)-1, -1, -1):
                    if r2[j] == ']': depth += 1
                    elif r2[j] == '[':
                        depth -= 1
                        if depth == 0:
                            st = r2[j+1:-1]; pre = r2[:j].strip(); break
            name = pre[1:-1] if pre.startswith('(') and pre.endswith(')') else None
            secnum = re.match(r'(\d+(?:\.\d+)*)', sec).group(1) if re.match(r'\d', sec) else sec
            cur[key] = dict(file=f, line=i, kind=kind, name=name, status=st, sec=secnum, full=line)
            order.append(key)
dep = open(os.path.join(root,"의존지도_v2.md"), encoding="utf-8").read().splitlines()
seen = set(); in1 = False
for line in dep:
    if line.startswith("## 1."): in1 = True
    elif line.startswith("## 2."): in1 = False
    if not in1: continue
    m = re.match(r'^\| `\{\{(\d+:[^}]+)\}\}` \| (\S+) \| (.*?) \| (.*?) \| (.*?) \| (.*?) \| (.*?) \| (.*?) \| (.*?) \| (.*?) \|\s*$', line)
    if not m: continue
    key, sec, oldno, gist, status, inputs, rec, lit, appD, note = m.groups()
    seen.add(key)
    if key not in cur:
        print("의존지도에 있으나 장 파일 머리 없음:", key); continue
    c = cur[key]; probs = []
    if not (c["sec"] == sec or c["sec"].startswith(sec+".")): probs.append(f"절 {sec}→현행 {c['sec']}")
    cst = c["status"] or ""
    if c["kind"] != "정의":
        a = re.sub(r'\s+',' ', cst.split(";")[0].strip()); b = re.sub(r'\s+',' ', status.strip())
        if a != b: probs.append(f"지위 「{b}」→현행 「{a}」")
        cids = set(re.findall(r'r[0-9a-f]{7}', cst.split(";",1)[1])) if ";" in cst else set()
    else:
        cids = set(re.findall(r'r[0-9a-f]{7}', cst))
    dids = set(re.findall(r'r[0-9a-f]{7}', rec))
    if cids != dids: probs.append(f"기록 식별자 {sorted(dids)}→현행 {sorted(cids)}")
    hl = set(re.findall(r'\{\{(\d+:[^}]+)\}\}', c["full"])); hl.discard(key)
    dl = set(re.findall(r'\{\{(\d+:[^}]+)\}\}', inputs.split("본문 인용:")[0]))
    if hl != dl: probs.append(f"머리줄 인용 {sorted(dl)}→현행 {sorted(hl)}")
    if c["name"] and gist != c["name"]: probs.append(f"요지 「{gist}」→현행 이름 「{c['name']}」")
    if probs: print("의존지도", key, "|", "; ".join(probs))
for k in order:
    if k not in seen: print("장 파일에 있으나 의존지도 1절에 없음:", k)
print("done", len(order), len(seen))
