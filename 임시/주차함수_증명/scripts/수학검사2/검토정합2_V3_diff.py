# -*- coding: utf-8 -*-
"""V3: 전_정합1114 사본과 현재 파일의 줄 단위 diff 가운데 낱말 치환 관련 줄만 뽑는다. python -I"""
import difflib, io, os, re, sys
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OLD = os.path.join(ROOT, "대조v2", "수학검사2", "전_정합1114")
MAP = {"장부_v2.md": "장부_v2.md", "구조표_v2.md": "구조표_v2.md", "README.md": "원고_자료/README.md",
       "빠른_확인.py": "원고_자료/빠른_확인.py", "_gen_재실행표.py": "scripts/_gen_재실행표.py"}
WORDS = re.compile(r"칸|구간|구획|경계|상하계|사슬|연쇄|임계점|정류점|자르는|배치|상해|상위해|블록|크기열|걸음열|초과열|수열|증인 위치|상계|토막|묶음")
for fn in sorted(os.listdir(OLD)):
    if not (fn.endswith(".md") or fn.endswith(".py")):
        continue
    rel = MAP.get(fn, "장v2/" + fn)
    a = io.open(os.path.join(OLD, fn), encoding="utf-8").read().split("\n")
    b = io.open(os.path.join(ROOT, rel), encoding="utf-8").read().split("\n")
    sm = difflib.SequenceMatcher(None, a, b, autojunk=False)
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag == "equal":
            continue
        if tag == "replace" and (i2 - i1) == (j2 - j1):
            for k in range(i2 - i1):
                la, lb = a[i1 + k], b[j1 + k]
                # 낱말 수준 diff
                wa = re.findall(r"\S+|\s+", la); wb = re.findall(r"\S+|\s+", lb)
                s2 = difflib.SequenceMatcher(None, wa, wb, autojunk=False)
                segs = []
                for t, x1, x2, y1, y2 in s2.get_opcodes():
                    if t == "equal":
                        continue
                    segs.append(("".join(wa[x1:x2]).strip(), "".join(wb[y1:y2]).strip()))
                if any(WORDS.search(x) or WORDS.search(y) for x, y in segs):
                    print(f"## {rel}:{j1+k+1}")
                    for x, y in segs:
                        print(f"   「{x}」 → 「{y}」")
        else:
            txt = "\n".join(a[i1:i2] + b[j1:j2])
            if WORDS.search(txt):
                print(f"## {rel}:{j1+1} [{tag}] old {i2-i1} lines / new {j2-j1} lines")
                for l in a[i1:i2]:
                    print("   - " + l[:200])
                for l in b[j1:j2]:
                    print("   + " + l[:200])
