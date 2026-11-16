# 검토전체8 N11: 떨어진 증명 문단을 진술에 붙인 블록 지도로 두 증명의 폐포를 구하고 11.3 입력 완전성을 본다.
import re, json, os
root = r"C:\math\임시\주차함수_증명\장v2"
order = ["장1","장2","장3","장4","장5A","장5B","장6","장7A","장7B","장8","장9","장10"]
head_re = re.compile(r"^\*\*(정의|정리|명제|보조정리|따름정리)\s+\{\{([^}]+)\}\}\s*([\(\[].*?|\.)\*\*")
proof_re = re.compile(r"^\*\*(?:정의|정리|명제|보조정리|따름정리)\s+\{\{([^}]+)\}\}(?:\(.*?\))?의 증명[^*]*\*\*")
sec_re = re.compile(r"^(#{2,4})\s+(\d+(?:\.\d+)*)\.?\s")
blocks = {}
for ch in order:
    lines = open(os.path.join(root, ch+".md"), encoding="utf-8").read().split("\n")
    cur=None; sec=None
    for i, ln in enumerate(lines, 1):
        if sec_re.match(ln): sec = sec_re.match(ln).group(2); cur=None
        mh = head_re.match(ln)
        mp = proof_re.match(ln)
        if mh:
            cur = mh.group(2); blocks.setdefault(cur, dict(file=ch, sec=sec, kind=mh.group(1), head=mh.group(3), text=""))
        elif mp:
            cur = mp.group(1); blocks.setdefault(cur, dict(file=ch, sec=sec, kind="?", head="", text=""))
        if cur:
            blocks[cur]["text"] += ln + "\n"
            if ln.strip().endswith("∎"): cur=None
json.dump(blocks, open(r"C:\math\임시\주차함수_증명\scripts\수학검사2\_N11_blocks2.json","w",encoding="utf-8"), ensure_ascii=False)
def cites(l): return set(re.findall(r"\{\{(\d+[A-Za-z]*:[^}]+)\}\}", blocks[l]["text"]))-{l}
def closure(start, allow):
    seen=set(); st=[start]
    while st:
        x=st.pop()
        if x in seen or x not in blocks: continue
        seen.add(x)
        for c in cites(x):
            if c in blocks and (blocks[c]["file"] in allow or c=="7:old-6-22"): st.append(c)
    return seen
c1=closure("9:old-7-46",("장9",)); c2=closure("10:old-8-37",("장10",))
print("9장 블록 중 첫째 폐포 밖:", sorted(k for k,b in blocks.items() if b["file"]=="장9" and k not in c1))
print("10장 블록 중 둘째 폐포 밖:", sorted(k for k,b in blocks.items() if b["file"]=="장10" and k not in c2))
for l in ["9:old-7-2","9:old-7-9","9:old-7-36","9:old-7-40","9:old-7-41","10:old-8-15","10:old-8-16","10:old-8-18","10:old-8-26"]:
    print(l,"인용자:",sorted(k for k,b in blocks.items() if "{{"+l+"}}" in b["text"] and k!=l))
# 11.3 입력 완전성: 폐포 블록이 인용하는 1–8장 라벨 가운데 11.3 세 표의 '입력'/'계산 진술' 열에 없는 것
ch11 = open(os.path.join(root, "장11.md"), encoding="utf-8").read()
sec113 = ch11.split("### 11.3")[1].split("### 11.4")[0]
listed = set(re.findall(r"\{\{(\d+[A-Za-z]*:[^}]+)\}\}", sec113))
pre9 = lambda l: l.split(":")[0] in ("1","2","3","4","5","6","7","8")
for name, cl in (("첫째", c1|{"7:old-6-22"}), ("둘째", c2)):
    used = {}
    for k in cl:
        if k not in blocks: continue
        for c in cites(k):
            if pre9(c): used.setdefault(c, set()).add(k)
    miss = {c: v for c, v in used.items() if c not in listed}
    print(f"== {name} 증명 폐포가 인용하는 1–8장 라벨 {len(used)}개 중 11.3에 없는 것 {len(miss)}개:")
    for c, v in sorted(miss.items()):
        print(f"   {c} <- {sorted(v)}")
