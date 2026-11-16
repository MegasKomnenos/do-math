# Q14: 의존지도 1절 「본문 인용」을 현행 장 파일에서 다시 만들어 견준다(자리 찾기용).
import re, os
root = r"C:\math\임시\주차함수_증명"
files = ["장1.md","장2.md","장3.md","장4.md","장5A.md","장5B.md","장6.md","장7A.md","장7B.md","장8.md","장9.md","장10.md","장11.md"]
head_re = re.compile(r'^\*\*(정의|정리|명제|보조정리|따름정리)\s+\{\{(\d+):([^}]+)\}\}\s*(.*?)\*\*')
body = {}  # label -> set of labels cited in body (excluding head line)
order=[]
for f in files:
    lines = open(os.path.join(root,"장v2",f), encoding="utf-8").read().splitlines()
    curlab=None
    for line in lines:
        h = head_re.match(line)
        if h:
            kind, ch, lab, rest = h.groups()
            curlab = f"{ch}:{lab}"
            if not rest.startswith("의 증명"):
                body.setdefault(curlab,set()); order.append(curlab)
                # head line citations are excluded (they belong to 머리)
                continue
            else:
                # deferred proof: following lines belong to curlab; but the head line itself may cite
                body.setdefault(curlab,set())
                for m in re.finditer(r'\{\{(\d+:[^}]+)\}\}', line):
                    if m.group(1)!=curlab: body[curlab].add(m.group(1))
                continue
        if curlab is None: continue
        if re.match(r'^#{2,4}\s', line):
            curlab=None; continue   # new section: text before next head belongs to section intro, not to statement? keep simple
        for m in re.finditer(r'\{\{(\d+:[^}]+)\}\}', line):
            if m.group(1)!=curlab: body[curlab].add(m.group(1))
dep = open(os.path.join(root,"의존지도_v2.md"), encoding="utf-8").read().splitlines()
in1=False; n=0; nd=0
for line in dep:
    if line.startswith("## 1."): in1=True
    elif line.startswith("## 2."): in1=False
    if not in1: continue
    m = re.match(r'^\| `\{\{(\d+:[^}]+)\}\}` \| (\S+) \| (.*?) \| (.*?) \| (.*?) \| (.*?) \| (.*?) \| (.*?) \| (.*?) \| (.*?) \|\s*$', line)
    if not m: continue
    key=m.group(1); inputs=m.group(6)
    dl = set(re.findall(r'\{\{(\d+:[^}]+)\}\}', inputs.split("본문 인용:")[1])) if "본문 인용:" in inputs else set()
    cb = body.get(key,set())
    n+=1
    if dl!=cb:
        nd+=1
        print(f"{key}: 의존지도에만={sorted(dl-cb)} 현행에만={sorted(cb-dl)}")
print("rows",n,"diff",nd)
