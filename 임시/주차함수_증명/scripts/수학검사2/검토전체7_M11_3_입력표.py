# -*- coding: utf-8 -*-
"""M11: (A) 11.2 '쓰인 곳' 열 대조, (B) 11.3 입력 표의 인용 자리 대조와 인용 폐포, (C) 부록 C 이름 대조,
(D) 식별자 집합 대조, (E) 11.4 문헌 표의 '쓰인 자리' 대조 자료."""
import re, glob, os, json, sys
from collections import defaultdict
ROOT = r"C:\math\임시\주차함수_증명\장v2"
OUT = r"C:\math\임시\주차함수_증명\대조v2\수학검사2"
def rd(p): return open(p, encoding="utf-8").read()

CH_FILES = sorted(glob.glob(os.path.join(ROOT, "장*.md")))
HEAD0 = re.compile(r"^\*\*(정리|명제|보조정리|따름정리|정의) \{\{(\w+):([^}]+)\}\}\s*(.*?)\.\*\*(.*)$")
index = {}; blocks = {}  # key -> dict(text, sec, ch)
order = []
for f in CH_FILES:
    ch = os.path.basename(f)[1:-3]
    lines = rd(f).splitlines()
    sec = ""; cur = None; buf = []
    def flush():
        if cur is not None:
            blocks[cur] = dict(text="\n".join(buf), sec=cursec, ch=ch)
    cursec = ""
    for i, ln in enumerate(lines, 1):
        ms = re.match(r"^(#{2,4}) ([\d.]+[A-Z]?)\s", ln)
        if ms:
            flush(); cur = None; buf = []; sec = ms.group(2); continue
        m = HEAD0.match(ln)
        if m:
            flush()
            typ, chp, lab, mid, rest = m.groups()
            # mid = "(이름…) [표지]" 또는 "[표지]" 또는 "(이름)"
            name = None; tag = None
            mt = re.search(r"\[([^\[\]]*)\]\s*$", mid)
            if mt:
                tag = mt.group(1); mid2 = mid[:mt.start()].strip()
            else: mid2 = mid.strip()
            if mid2.startswith("(") and mid2.endswith(")"): name = mid2[1:-1]
            elif mid2: name = "?" + mid2
            key = f"{chp}:{lab}"
            index[key] = dict(type=typ, name=name, tag=tag, file=os.path.basename(f), line=i, sec=sec)
            order.append(key)
            cur = key; cursec = sec; buf = [ln]
        elif cur is not None:
            buf.append(ln)
    flush()
json.dump(index, open(os.path.join(OUT, "_M11_index.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=0)
print("진술 수:", len(index))

def cites(key):
    t = blocks[key]["text"]
    # 머리 줄 자신의 라벨 제외
    labs = re.findall(r"\{\{(\w+:[^}]+)\}\}", t)
    return [l for l in labs if l != key and not l.startswith("D:")]

t11 = rd(os.path.join(ROOT, "장11.md"))

# ---------- (A) 11.2 쓰인 곳 ----------
print("\n##### (A) 11.2 쓰인 곳 대조")
for ln in t11.splitlines():
    if ln.startswith("| 부록 D.{{D:"):
        cells = [c.strip() for c in ln.strip().strip("|").split(" | ")]
        labs = re.findall(r"\{\{(\w+:[^}]+)\}\}", cells[1])
        secs = sorted({index[l]["sec"] for l in labs if l in index})
        claimed = cells[3]
        # 절은 소수 둘째 자리까지만 비교 (예: 5.4.2 -> 5.4)
        secs2 = sorted({".".join(s.split(".")[:2]) for s in secs})
        cl2 = sorted(re.findall(r"\d+\.\d+", claimed))
        flag = "" if secs2 == cl2 else "  <== 차이"
        print(f"{cells[0][7:40]:34s} 표:{claimed:10s} 색인:{','.join(secs)}{flag}")

# ---------- (B) 11.3 ----------
print("\n##### (B) 11.3 입력 표: 각 입력 라벨을 인용하는 9장·10장 블록(및 7:old-6-22)")
sec113 = t11.split("### 11.3")[1].split("### 11.4")[0]
rows = [ln for ln in sec113.splitlines() if ln.startswith("| ") and not ln.startswith("| 입력") and not ln.startswith("|---")]
def blocks_citing(lab, chs=("9", "10")):
    res = []
    for k in order:
        b = blocks[k]
        if b["ch"] in chs or k == "7:old-6-22":
            if lab in cites(k): res.append(k)
    return res
for ln in rows:
    cells = [c.strip() for c in ln.strip().strip("|").split(" | ")]
    inputs = re.findall(r"\{\{(\w+:[^}]+)\}\}", cells[0])
    print("\n--- 행:", cells[0][:90])
    for lab in inputs:
        print(f"   {lab}: 인용 블록 = {blocks_citing(lab)}")
    print("   표의 인용 자리:", " || ".join(cells[2:]))

# 인용 폐포: 정리 9:old-7-46 과 10:old-8-37 에서 출발
def closure(start):
    seen = set(); stack = [start]
    while stack:
        k = stack.pop()
        if k in seen or k not in blocks: continue
        seen.add(k)
        for c in cites(k):
            if c not in seen: stack.append(c)
    return seen
c1 = closure("9:old-7-46"); c2 = closure("10:old-8-37")
def pre(cs): return sorted(k for k in cs if k.split(":")[0] not in ("9", "10"))
shared = sorted(set(pre(c1)) & set(pre(c2)))
only1 = sorted(set(pre(c1)) - set(pre(c2)))
only2 = sorted(set(pre(c2)) - set(pre(c1)))
print("\n##### 인용 폐포(블록 안 라벨 인용만 추적; 식 번호·준비 문단 인용은 빠짐)")
print("첫째 증명 폐포 크기:", len(c1), " 둘째:", len(c2))
print("공유 앞장 입력:", shared)
print("첫째만:", only1)
print("둘째만:", only2)
print("9장 진술 가운데 첫째 폐포 안:", sorted(k for k in c1 if k.startswith("9:")))
print("10장 진술 가운데 둘째 폐포 안:", sorted(k for k in c2 if k.startswith("10:")))
# 표에 적힌 입력 라벨 전체
table_inputs = set()
for ln in rows:
    cells = [c.strip() for c in ln.strip().strip("|").split(" | ")]
    table_inputs |= set(re.findall(r"\{\{(\w+:[^}]+)\}\}", cells[0]))
print("표의 입력 라벨(입력 열) 수:", len(table_inputs))
print("폐포에 있으나 표 입력 열에 없는 앞장 진술:", sorted((set(pre(c1)) | set(pre(c2))) - table_inputs))
print("표 입력 열에 있으나 폐포에 없는 진술:", sorted(table_inputs - (c1 | c2)))

# ---------- (C) 부록 C 이름 대조 ----------
print("\n##### (C) 부록 C 이름/유형 대조")
tC = rd(os.path.join(ROOT, "부록C.md"))
secC2 = tC.split("### 기록이 결과에 붙인 이름")[1].split("### 기록의 글자")[0]
for ln in secC2.splitlines():
    if not ln.startswith("| 기록"): continue
    cells = [c.strip() for c in ln.strip().strip("|").split(" | ")]
    m = re.match(r"(정리|명제|보조정리|따름정리|정의) \{\{(\w+:[^}]+)\}\}", cells[1])
    if not m: print("  파싱 실패:", ln[:80]); continue
    typ, key = m.groups()
    if key not in index: print("  미정의:", key); continue
    ix = index[key]
    nm = (ix["name"] or "").split(";")[0].strip()
    issues = []
    if ix["type"] != typ: issues.append(f"유형 색인={ix['type']}")
    if nm != cells[2]: issues.append(f"이름 색인=『{nm}』 C=『{cells[2]}』")
    # 기록 이름 부분 (세미콜론 뒤)
    recpart = (ix["name"] or "").split(";", 1)[1].strip() if ix["name"] and ";" in ix["name"] else ""
    if recpart and recpart != cells[0]: issues.append(f"기록이름 머리=『{recpart}』 C=『{cells[0]}』")
    if not recpart: issues.append(f"머리에 기록 이름 없음(머리 이름=『{ix['name']}』)")
    if issues: print(f"  {key} ({ix['file']}:{ix['line']}): " + " | ".join(issues))
# 머리에 기록 이름이 있는데 부록 C에 없는 진술
Ckeys = set(re.findall(r"\{\{(\w+:[^}]+)\}\}", secC2))
print("\n  머리에 '기록 […]의' 이름이 있으나 부록 C 둘째 표에 없는 진술:")
for k, ix in index.items():
    if ix["name"] and "기록 [" in ix["name"] and k not in Ckeys:
        print("   ", k, "|", ix["name"][:120])

# ---------- (D) 식별자 ----------
print("\n##### (D) 식별자")
tB = rd(os.path.join(ROOT, "부록B.md"))
Bids = re.findall(r"^\| (r[0-9a-f]{7}) \|", tB, re.M)
allids = set()
for f in CH_FILES + glob.glob(os.path.join(ROOT, "부록[ACD]*.md")):
    allids |= set(re.findall(r"\br[0-9a-f]{7}\b", rd(f)))
print("B 행 수:", len(Bids), " 중복:", [i for i in Bids if Bids.count(i) > 1])
print("본문·부록 A/C/D에 나오나 B에 없는 식별자:", sorted(allids - set(Bids)))
print("B에 있으나 어디에도 안 나오는 식별자:", sorted(set(Bids) - allids))
# 각 식별자가 어디에 나오는지 (B 전용 확인용)
where = defaultdict(set)
for f in CH_FILES + glob.glob(os.path.join(ROOT, "부록[ACD]*.md")):
    for i in set(re.findall(r"\br[0-9a-f]{7}\b", rd(f))): where[i].add(os.path.basename(f))
for i in Bids:
    ws = sorted(where[i])
    onlyApp = all(w.startswith("부록") for w in ws)
    if onlyApp: print(f"  {i}: 본문(장)에는 없고 {ws}에만")
# 시각 순서
times = re.findall(r"^\| r[0-9a-f]{7} \| (\d\d-\d\d \d\d:\d\d) \|", tB, re.M)
print("B 시각 순 정렬 여부:", times == sorted(times))
