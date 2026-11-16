# -*- coding: utf-8 -*-
"""부록 C 이름 표(기록의 이름 | 이 글의 진술 | 이 글의 이름): 진술 종류·라벨·이름을 본문 진술 머리와 대조."""
import re, os, glob
ROOT = r"C:\math\임시\주차함수_증명"
heads = {}
for f in sorted(glob.glob(os.path.join(ROOT, "장v2", "장*.md"))):
    for i, line in enumerate(open(f, encoding="utf-8"), 1):
        for m in re.finditer(r"\*\*(정의|정리|보조정리|명제|따름정리|가설|관찰|추측) \{\{([^}]+)\}\}(?: \((.*?)(?:; 기록|\) \[|\)\.\*\*|\)\s*\*\*))?", line):
            kind, label, name = m.group(1), m.group(2), m.group(3)
            # 이름: 괄호 안 「; 기록」 앞까지
            full = line[m.start():]
            mm = re.match(r"\*\*\S+ \{\{[^}]+\}\} \((.*?)\)(?:\s*\[|\.\*\*|\*\*)", full)
            nm = None
            if mm:
                nm = mm.group(1)
                nm = re.split(r"; 기록 ", nm)[0]
            if label in heads:
                heads[label].append((kind, nm, os.path.basename(f), i))
            else:
                heads[label] = [(kind, nm, os.path.basename(f), i)]
rows = []
lines = open(os.path.join(ROOT, "장v2", "부록C.md"), encoding="utf-8").read().split("\n")
for idx, line in enumerate(lines, 1):
    if not line.startswith("| 기록 "):
        continue
    cells = [c.strip() for c in line.strip().strip("|").split("|")]
    if len(cells) != 3:
        print("열 수 이상", idx, line[:80]); continue
    rows.append((idx, cells))
print("이름 표 행 수:", len(rows))
bad = 0
for idx, (src, stmt, name) in rows:
    m = re.match(r"^(정의|정리|보조정리|명제|따름정리) \{\{([^}]+)\}\}$", stmt)
    if not m:
        print(f"{idx}: 진술 열 꼴 이상: {stmt}"); bad += 1; continue
    kind, label = m.groups()
    hs = heads.get(label)
    if not hs:
        print(f"{idx}: 라벨 {label} 머리 없음"); bad += 1; continue
    # 증명 머리(「…의 증명」)는 제외
    hs2 = [h for h in hs if not (h[1] or "").endswith("의 증명") or True]
    h = hs[0]
    probs = []
    if h[0] != kind:
        probs.append(f"종류: 부록 {kind} / 머리 {h[0]}")
    if h[1] != name:
        probs.append(f"이름: 부록 「{name}」 / 머리 「{h[1]}」")
    if len(hs) > 1:
        probs.append(f"머리 {len(hs)}개: {[(x[0],x[1],x[2],x[3]) for x in hs]}")
    if probs:
        bad += 1
        print(f"{idx}: {label} ({h[2]}:{h[3]})")
        for p in probs: print("   -", p)
print("문제 행:", bad)
