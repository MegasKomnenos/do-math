# Q14: 의존지도 1절의 입력 라벨 전체(머리+본문)를 현행 장 파일의 진술 구간(머리 줄부터 다음 머리 전까지 + 미룬 증명 구간)에서 다시 모아 견준다.
import re, os
root = r"C:\math\임시\주차함수_증명"
files = ["장1.md","장2.md","장3.md","장4.md","장5A.md","장5B.md","장6.md","장7A.md","장7B.md","장8.md","장9.md","장10.md","장11.md"]
head_re = re.compile(r'^\*\*(정의|정리|명제|보조정리|따름정리)\s+\{\{(\d+):([^}]+)\}\}\s*(.*?)\*\*')
cites = {}
for f in files:
    lines = open(os.path.join(root,"장v2",f), encoding="utf-8").read().splitlines()
    cur=None
    for line in lines:
        h = head_re.match(line)
        if h:
            cur = f"{h.group(2)}:{h.group(3)}"
            cites.setdefault(cur,set())
        if cur is None: continue
        for m in re.finditer(r'\{\{(\d+:[^}]+)\}\}', line):
            if m.group(1)!=cur: cites[cur].add(m.group(1))
dep = open(os.path.join(root,"의존지도_v2.md"), encoding="utf-8").read().splitlines()
in1=False; n=0; nd=0; allin=set()
for line in dep:
    if line.startswith("## 1."): in1=True
    elif line.startswith("## 2."): in1=False
    if not in1: continue
    m = re.match(r'^\| `\{\{(\d+:[^}]+)\}\}` \| (\S+) \| (.*?) \| (.*?) \| (.*?) \| (.*?) \| (.*?) \| (.*?) \| (.*?) \| (.*?) \|\s*$', line)
    if not m: continue
    key=m.group(1); inputs=m.group(6)
    dl = set(re.findall(r'\{\{(\d+:[^}]+)\}\}', inputs)); allin |= dl
    cb = cites.get(key,set()); n+=1
    if dl!=cb:
        nd+=1; print(f"{key}: 의존지도에만={sorted(dl-cb)} 현행에만={sorted(cb-dl)}")
print("rows",n,"diff",nd,"입력 라벨 수(중복 제외)",len(allin))
