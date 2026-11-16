# -*- coding: utf-8 -*-
"""자리표시자 `[Dn:이름]`을 JSON 지도(자리표시자 → 값)대로 채운다. 대상: 장v2/부록D_*.md, 장v2/장11.md, scripts/_gen_재실행표.py,
scripts/_재실행표_여유.json. 멱등(이미 채워진 자리는 건너뜀). 남은 자리표시자는 `_check_자리표시자.py`로 센다.
사용: python -I scripts/수학검사2/채움_자리표시자.py <지도.json> [--dry]"""
import glob
import io
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
TARGETS = sorted(glob.glob(os.path.join(ROOT, "장v2", "부록D_*.md"))) + [
    os.path.join(ROOT, "장v2", "장11.md"), os.path.join(ROOT, "scripts", "_gen_재실행표.py"), os.path.join(ROOT, "scripts", "_재실행표_여유.json")]

mp = json.load(io.open(sys.argv[1], encoding="utf-8"))
dry = "--dry" in sys.argv
total = 0
for p in TARGETS:
    s = io.open(p, encoding="utf-8").read()
    s0 = s
    for k, v in mp.items():
        c = s.count(k)
        if c:
            if p.endswith(".py") or p.endswith(".json"):
                v2 = v.replace("\\", "\\\\")            # 파이썬·JSON 문자열 리터럴 안
            else:
                v2 = v
            s = s.replace(k, v2)
            total += c
            print(os.path.relpath(p, ROOT), k, "×", c)
    if s != s0 and not dry:
        io.open(p, "w", encoding="utf-8", newline="\n").write(s)
print("채움", total, "(dry)" if dry else "")
