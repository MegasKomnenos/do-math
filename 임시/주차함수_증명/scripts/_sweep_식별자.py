# -*- coding: utf-8 -*-
"""짧은 식별자(여섯 자리 이하)를 기록 폴더의 일곱 자리 식별자로 바꾼다(세션 결정 39와 같은 꼴).
대상: 장v2/*.md, 구조표_v2.md, 의존지도_v2.md, 장부_v2.md, 파견/명세v2/*.json, 파견/명세v2_출처목록.md, 파견/라벨_v2.md,
      scripts/명세v2_수정.py, scripts/명세v2_META.py. 멱등. 8장 명시 경계 머리의 「표준(Robbins, Euler–Maclaurin)」도 「표준」으로 고친다.
"""
import glob
import io
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SHORT = {"rba2ecf": "rba2ecf4", "ra7615a": "ra7615a0", "r9e782": "r9e782f5"}
FILES = (glob.glob(os.path.join(ROOT, "장v2", "*.md"))
         + [os.path.join(ROOT, "구조표_v2.md"), os.path.join(ROOT, "의존지도_v2.md"), os.path.join(ROOT, "장부_v2.md"),
            os.path.join(ROOT, "파견", "명세v2_출처목록.md"), os.path.join(ROOT, "파견", "라벨_v2.md"),
            os.path.join(ROOT, "scripts", "명세v2_수정.py"), os.path.join(ROOT, "scripts", "명세v2_META.py")]
         + glob.glob(os.path.join(ROOT, "파견", "명세v2", "*.json")))

total = 0
for p in FILES:
    if not os.path.exists(p):
        continue
    s = io.open(p, encoding="utf-8").read()
    t = s
    for short, full in SHORT.items():
        t = re.sub(short + r"(?![0-9a-f])", full, t)
    if os.path.basename(p) == "장8.md":
        t = t.replace("[증명됨; 표준(Robbins, Euler–Maclaurin)]", "[증명됨; 표준]")
    if t != s:
        n = sum(len(re.findall(short + r"(?![0-9a-f])", s)) for short in SHORT)
        io.open(p, "w", encoding="utf-8", newline="\n").write(t)
        total += n
        print("patched", os.path.relpath(p, ROOT), n)
print("총 치환", total)
