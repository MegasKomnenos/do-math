# 검토전체8 N11: 부록 A 각 행의 첫 기호가 본문에서 처음 나타나는 절을 찾아 표의 절과 견준다.
import re, os
root = r"C:\math\임시\주차함수_증명\장v2"
order = ["장1","장2","장3","장4","장5A","장5B","장6","장7A","장7B","장8","장9","장10","장11"]
sec_re = re.compile(r"^(#{2,4})\s+(\d+(?:\.\d+)*)\.?\s")
lines = []
for ch in order:
    cur = None
    for i, ln in enumerate(open(os.path.join(root, ch+".md"), encoding="utf-8").read().split("\n"), 1):
        ms = sec_re.match(ln)
        if ms: cur = ms.group(2)
        lines.append((ch, i, cur, ln))
A = open(os.path.join(root, "부록A.md"), encoding="utf-8").read().split("\n")
def norm(s): return re.sub(r"\s+", "", s)
body_norm = [(ch, i, sec, norm(ln)) for ch, i, sec, ln in lines]
def secnum(s):
    try: return tuple(int(x) for x in s.split("."))
    except: return None
for ln in A:
    if not ln.startswith("| $"): continue
    cells = [c.strip() for c in ln.strip().strip("|").split(" | ")]
    syms = re.findall(r"\$([^$]+)\$", cells[0])
    listed = cells[2]
    first_listed = re.findall(r"\d+(?:\.\d+)*", listed)
    if not first_listed: continue
    target = secnum(first_listed[0])
    for sym in syms:
        key = norm(sym)
        # 변수 글자 하나짜리는 건너뜀
        if len(key) <= 2: continue
        found = None
        for ch, i, sec, t in body_norm:
            if key in t:
                found = (ch, i, sec); break
        if found is None:
            print(f"!! 본문에 없음: ${sym}$  (표: {listed})")
        else:
            fs = secnum(found[2]) if found[2] else None
            # 표의 절보다 앞 절에서 처음 나타나면 보고 (장 11, 부록 제외)
            if fs and target and fs[:2] < target[:2]:
                print(f"앞서 나타남: ${sym}$ 표={listed} 첫 출현={found[0]} {found[2]}절 {found[1]}행")
