# Q14: 장부 4절(이름 사전) 행을 현행 장 파일 머리와 대조한다(자리 찾기용).
import re, os
root = r"C:\math\임시\주차함수_증명"
files = ["장1.md","장2.md","장3.md","장4.md","장5A.md","장5B.md","장6.md","장7A.md","장7B.md","장8.md","장9.md","장10.md","장11.md"]
head_re = re.compile(r'^\*\*(정의|정리|명제|보조정리|따름정리)\s+\{\{(\d+):([^}]+)\}\}\s*(.*?)\*\*')
cur = {}
for f in files:
    sec = ""
    for i, line in enumerate(open(os.path.join(root,"장v2",f), encoding="utf-8").read().splitlines(), 1):
        m = re.match(r'^(#{2,4})\s+(.*)', line)
        if m: sec = m.group(2).strip()
        h = head_re.match(line)
        if h:
            kind, ch, lab, rest = h.groups()
            if rest.startswith("의 증명"): continue
            r2 = rest.rstrip().rstrip('.'); pre = r2
            if r2.endswith(']'):
                depth = 0
                for j in range(len(r2)-1, -1, -1):
                    if r2[j] == ']': depth += 1
                    elif r2[j] == '[':
                        depth -= 1
                        if depth == 0: pre = r2[:j].strip(); break
            name = pre[1:-1] if pre.startswith('(') and pre.endswith(')') else ""
            secnum = re.match(r'(\d+(?:\.\d+)*)', sec).group(1) if re.match(r'\d', sec) else sec
            cur[f"{ch}:{lab}"] = dict(kind=kind, name=name, sec=secnum, file=f, line=i)
lines = open(os.path.join(root,"장부_v2.md"), encoding="utf-8").read().splitlines()
in4 = False; seen=set(); n=0
for ln, line in enumerate(lines,1):
    if line.startswith("## 4."): in4=True
    elif line.startswith("## 5."): in4=False
    if not in4: continue
    m = re.match(r'^\| (.*?) \| (.*?) \| (.*?) \| (.*?) \| (.*?) \| (.*?) \|\s*$', line)
    if not m: continue
    old, kind, name, recname, sec, lab = m.groups()
    mm = re.search(r'\{\{(\d+:[^}]+)\}\}', lab)
    if not mm:
        print(f"L{ln} 라벨 없음: {lab[:80]}"); continue
    key = mm.group(1); n+=1; seen.add(key)
    if key not in cur:
        print(f"L{ln} {key}: 장 파일에 머리 없음 (처리: {lab[:60]} / 절 {sec})"); continue
    c = cur[key]; probs=[]
    if c["kind"] != kind: probs.append(f"종류 {kind}→현행 {c['kind']}")
    full = (name + ("; " + recname if recname else "")).strip()
    if full != c["name"]: probs.append(f"이름 「{full}」→현행 「{c['name']}」")
    if not (c["sec"]==sec or c["sec"].startswith(sec+".")): probs.append(f"절 {sec}→현행 {c['sec']}")
    if probs: print(f"L{ln} {key}: " + "; ".join(probs))
for k in cur:
    if k not in seen: print("장 파일에 있으나 4절에 없음:", k)
print("rows", n)
