# Q14: 장 파일의 진술 머리 순서로 센 번호·종류·이름·절을 대응표와 의존지도 1절과 대조한다(자리 찾기용).
import re, os
root = r"C:\math\임시\주차함수_증명"
files = ["장1.md","장2.md","장3.md","장4.md","장5A.md","장5B.md","장6.md","장7A.md","장7B.md","장8.md","장9.md","장10.md","장11.md"]
head_re = re.compile(r'^\*\*(정의|정리|명제|보조정리|따름정리)\s+\{\{(\d+):([^}]+)\}\}\s*(.*?)\*\*')
cur = {}   # label -> dict
order = []
counter = {}
for f in files:
    sec = ""
    for i, line in enumerate(open(os.path.join(root,"장v2",f), encoding="utf-8"), 1):
        m = re.match(r'^(#{2,4})\s+(.*)', line)
        if m:
            sec = m.group(2).strip()
        h = head_re.match(line)
        if h:
            kind, ch, lab, rest = h.groups()
            if rest.startswith("의 증명"):
                continue
            key = f"{ch}:{lab}"
            counter[ch] = counter.get(ch,0)+1
            num = f"{ch}.{counter[ch]}"
            # name in parentheses
            name = None; st = None
            r2 = rest.rstrip().rstrip('.')
            # status = last [...] block
            if r2.endswith(']'):
                depth=0
                for j in range(len(r2)-1, -1, -1):
                    if r2[j]==']': depth+=1
                    elif r2[j]=='[':
                        depth-=1
                        if depth==0:
                            st = r2[j+1:-1]; pre = r2[:j].strip(); break
            else:
                pre = r2.strip()
            if pre.startswith('(') and pre.endswith(')'):
                name = pre[1:-1]
            secnum = re.match(r'(\d+(?:\.\d+)*)', sec).group(1) if re.match(r'\d', sec) else sec
            cur[key] = dict(file=f, line=i, kind=kind, num=num, name=name, status=st, sec=secnum, rest=rest, full=line)
            order.append(key)
print("heads:", len(order))
# ---- 대응표
tab = open(os.path.join(root,"대조v2","라벨_번호_대응표_1114.md"), encoding="utf-8").read().splitlines()
seen = set()
for line in tab:
    m = re.match(r'^\| `\{\{(\d+:[^}]+)\}\}` \| (\S+) \| (.*?) \| (\S+) \| (\S+|사본에 없음) \| (\S+) \|', line)
    if not m: continue
    key, kind, name, num, old, sec = m.groups()
    seen.add(key)
    if key not in cur:
        print("대응표에 있으나 장 파일 머리 없음:", key); continue
    c = cur[key]
    probs = []
    if c["kind"] != kind: probs.append(f"종류 {kind}→현행 {c['kind']}")
    if c["num"] != num: probs.append(f"번호 {num}→현행 {c['num']}")
    cname = c["name"] or "—"
    if cname != name: probs.append(f"이름 「{name}」→현행 「{cname}」")
    csec = c["sec"]
    # 대응표 절은 ### 수준(5.5 등), 현행 secnum may be 5.5.1
    if not (csec == sec or csec.startswith(sec+".")): probs.append(f"절 {sec}→현행 {csec}")
    if probs: print("대응표", key, "|", "; ".join(probs))
for k in order:
    if k not in seen: print("장 파일에 있으나 대응표에 없음:", k)
# ---- 의존지도 1절
dep = open(os.path.join(root,"의존지도_v2.md"), encoding="utf-8").read().splitlines()
seen2 = set()
in1 = False
for line in dep:
    if line.startswith("## 1."): in1 = True
    elif line.startswith("## 2."): in1 = False
    if not in1: continue
    m = re.match(r'^\| `\{\{(\d+:[^}]+)\}\}` \| (\S+) \| (.*?) \| (.*?) \| (.*?) \| (.*?) \| (.*?) \| (.*?) \| (.*?) \| (.*?) \|\s*$', line)
    if not m: continue
    key, sec, oldno, gist, status, inputs, rec, lit, appD, note = m.groups()
    seen2.add(key)
    if key not in cur:
        print("의존지도에 있으나 장 파일 머리 없음:", key); continue
    c = cur[key]
    probs = []
    if not (c["sec"] == sec or c["sec"].startswith(sec+".")): probs.append(f"절 {sec}→현행 {c['sec']}")
    # status: head bracket before ';'
    cst = (c["status"] or "")
    cst_main = cst.split(";")[0].strip()
    cst_main_n = re.sub(r'\s+', ' ', cst_main)
    st_n = re.sub(r'\s+', ' ', status.strip())
    if c["kind"] == "정의":
        pass
    elif cst_main_n != st_n:
        probs.append(f"지위 「{st_n}」→현행 「{cst_main_n}」")
    # record ids
    cids = set(re.findall(r'r[0-9a-f]{7}', cst.split(";",1)[1] if ";" in cst else ""))
    if c["kind"] == "정의":
        cids = set(re.findall(r'r[0-9a-f]{7}', cst))
    dids = set(re.findall(r'r[0-9a-f]{7}', rec)) if rec != "—" else set()
    if cids != dids: probs.append(f"기록 식별자 {sorted(dids)}→현행 {sorted(cids)}")
    # head-line label citations
    hl = set(re.findall(r'\{\{(\d+:[^}]+)\}\}', c["full"]))
    hl.discard(key)
    dl_head = set(re.findall(r'`\{\{(\d+:[^}]+)\}\}`', inputs.split("본문 인용:")[0])) if inputs != "—" else set()
    if hl != dl_head: probs.append(f"머리 인용 {sorted(dl_head)}→현행 {sorted(hl)}")
    # gist vs name
    cname = c["name"]
    if cname and gist != cname: probs.append(f"요지 「{gist}」→현행 이름 「{cname}」")
    if probs: print("의존지도", key, "|", "; ".join(probs))
for k in order:
    if k not in seen2: print("장 파일에 있으나 의존지도 1절에 없음:", k)
