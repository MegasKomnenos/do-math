# -*- coding: utf-8 -*-
"""H14: 대응표의 「15:52 조립본 번호」 열을 결정 101 전 사본(전_정합1114)의 머리 순서로 다시 센다. 결정 97이 지운 둘은 되돌려 센다."""
import io, os, re
ROOT = r"C:\math\임시\주차함수_증명"
base = os.path.join(ROOT, "대조v2","수학검사2","전_정합1114")
HEAD_RE = re.compile(r"^\*\*(정의|정리|명제|보조정리|따름정리) \{\{(\d+):([A-Za-z][A-Za-z0-9\-]*)\}\}(?= \(| \[|\.\*\*|\*\*)")
CHAPTER_RE = re.compile(r"^## (\d+)\.")
files=sorted(os.listdir(base))
def key(n):
    m=re.match(r"장(\d+)([A-Z]?)\.md",n); return (int(m.group(1)),m.group(2)) if m else (99,n)
files=[f for f in files if re.match(r"장\d+[A-Z]?\.md",f)]; files.sort(key=key)
print(files)
seq=[]; chapter=0
for name in files:
    for ln in io.open(os.path.join(base,name),encoding="utf-8").read().split("\n"):
        m=CHAPTER_RE.match(ln)
        if m: chapter=int(m.group(1)); continue
        h=HEAD_RE.match(ln)
        if h: seq.append((chapter,f"{h.group(2)}:{h.group(3)}"))
# restore decision-97 deletions
out=[]
for ch,k in seq:
    out.append((ch,k))
    if k=="6:old-6-19": out.append((6,"6:V-core-identity"))
    if k=="10:old-8-4": out.append((10,"10:old-8-5"))
nums={}; cnt={}
for ch,k in out:
    cnt[ch]=cnt.get(ch,0)+1; nums[k]=f"{ch}.{cnt[ch]}"
tab=io.open(os.path.join(ROOT,"대조v2","라벨_번호_대응표_1114.md"),encoding="utf-8").read().split("\n")
probs=[]; n=0
for i,ln in enumerate(tab,1):
    if not ln.startswith("| `"): continue
    cells=[c.strip() for c in ln.strip().strip("|").split("|")]
    lab=cells[0].strip("`").strip("(){}")
    if lab.startswith("{"): lab=lab[2:-2]
    n+=1
    if lab not in nums: probs.append(f"행{i} {lab}: 1552 사본에 없음"); continue
    if cells[4]!=nums[lab]: probs.append(f"행{i} {lab}: 표 {cells[4]} / 재계산 {nums[lab]}")
missing=[k for k in nums if k not in {re.sub(r'^[`({]+|[`)}]+$','',c.split('|')[1].strip()) for c in tab if c.startswith('| `')}]
print(n,"rows;",len(probs),"problems"); [print(p) for p in probs]
print("1552 labels not in table:", [k for k in nums if not any(k in ln for ln in tab)])
