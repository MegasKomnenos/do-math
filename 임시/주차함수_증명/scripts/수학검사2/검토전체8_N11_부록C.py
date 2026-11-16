# 검토전체8 N11: 부록 C 이름표를 진술 머리와 대조하고, '쓰지 않음'이라 한 낱말을 본문에서 찾는다.
import re, json, os, glob
blocks = json.load(open(r"C:\math\임시\주차함수_증명\scripts\수학검사2\_N11_blocks.json", encoding="utf-8"))
root = r"C:\math\임시\주차함수_증명\장v2"
C = open(os.path.join(root, "부록C.md"), encoding="utf-8").read().split("\n")
sec = None
named = set()
for ln in C:
    if ln.startswith("### "): sec = ln
    if "기록이 결과에 붙인 이름" in (sec or "") and ln.startswith("| 기록"):
        cells = [c.strip() for c in ln.strip().strip("|").split(" | ")]
        recname, stmt, name = cells
        labs = re.findall(r"\{\{([^}]+)\}\}", stmt)
        mk = re.match(r"(정의|정리|명제|보조정리|따름정리)", stmt)
        if not mk: print("!! 행 형식:", cells); continue
        kind = mk.group(1)
        for l in labs:
            named.add(l)
            b = blocks.get(l)
            if not b: print("!! 라벨 없음:", l); continue
            if b["kind"] != kind: print(f"[종류 다름] C={kind} 본문={b['kind']} {l}")
            head = b["head"]
            # 머리 괄호
            m = re.match(r"\((.*?)\)\s*\[", head)
            par = m.group(1) if m else ""
            # 이 글의 이름
            hname = par.split(";")[0].strip()
            def n(s): return re.sub(r"\s+|\$", "", s)
            if n(hname) != n(name):
                print(f"[이름 다름] {l}: C이름='{name}' 머리이름='{hname}'")
            # 기록 이름: 머리의 ';' 뒤 부분과 C의 기록 이름 비교 (식별자·이름)
            rec_in_head = par.split(";")[1].strip() if ";" in par else ""
            ids_c = set(re.findall(r"r[0-9a-f]{7}", recname)); ids_h = set(re.findall(r"r[0-9a-f]{7}", rec_in_head))
            if ids_c != ids_h:
                print(f"[기록 식별자 다름] {l}: C='{recname}' 머리='{rec_in_head}'")
            else:
                # 이름 글자 대조 (느슨): 기록 이름의 핵심 토큰이 머리에 있는가
                toks = re.findall(r"[A-Za-z][A-Za-z0-9\-\.′*⁺♯♮]*|\(\d+(?:\.\d+)*\)|\d+\.\d+|[가-힣]+ [A-Z][^,·]*", recname)
                core = re.sub(r"기록 \[r[0-9a-f]{7}\]의 ", "", recname)
                if n(core) != n(rec_in_head.replace("기록 ","").split("]의 ",1)[-1]) and n(core) not in n(rec_in_head):
                    print(f"[기록 이름 글귀 다름] {l}:\n     C  ='{recname}'\n     머리='{rec_in_head}'")
# 거꾸로: 머리에 '기록 [r…]의 …' 이름이 있으나 C 이름표에 없는 진술
for l, b in blocks.items():
    m = re.match(r"\((.*?)\)\s*\[", b["head"])
    if m and "기록 [" in m.group(1) and l not in named:
        print(f"[C에 없음] {b['file']} {b['kind']} {l}: ({m.group(1)[:150]})")
