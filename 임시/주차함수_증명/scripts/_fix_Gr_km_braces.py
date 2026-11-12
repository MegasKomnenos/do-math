# -*- coding: utf-8 -*-
"""세션 결정 54의 치환(_sweep_Gr_km.py)이 `…G}}` 꼴에서 닫는 중괄호 하나를 삼킨 자리를 커밋 0030d15f(치환 전)와 대조해 복구한다.
치환 전 파일에서 T^{\\mathrm G}} 또는 \\mathfrak K^{\\mathrm U}} 자리의 앞 문맥(30자)을 모으고, 현재 파일에서 같은 앞 문맥의
\\mathrm{Gr}·\\mathrm{km} 뒤에 '}'가 없으면 '}'를 넣는다.
사용: python _fix_Gr_km_braces.py [--dry]
"""
import io
import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FILES = ["장2.md", "장4.md", "장5A.md", "장5B.md", "장7B.md", "장8.md", "부록D_장7A.md"]
dry = "--dry" in sys.argv
PAIRS = [(re.compile(r"T\^\{\\mathrm\s*\{?G\}?\}\}"), "\\mathrm{Gr}"), (re.compile(r"\\mathfrak K\^\{\\mathrm\s*\{?U\}?\}\}"), "\\mathrm{km}")]
total = 0
for rel in FILES:
    p = os.path.join(ROOT, "장v2", rel)
    cur = io.open(p, encoding="utf-8").read()
    old = subprocess.run(["git", "-C", r"C:\math", "show", f"0030d15f:임시/주차함수_증명/장v2/{rel}"], capture_output=True).stdout.decode("utf-8", "replace")
    fixed = 0
    for old_re, tok in PAIRS:
        prefixes = [old[m.start()-30:m.start()] for m in old_re.finditer(old)]
        for pre in prefixes:
            # 현재 파일에서 같은 앞 문맥 + 토큰 + '}'가 아닌 다음 글자
            idx = cur.find(pre + tok)
            while idx != -1:
                end = idx + len(pre) + len(tok)
                if cur[end:end+1] != "}":
                    cur = cur[:end] + "}" + cur[end:]
                    fixed += 1
                    print(f"{rel}: 복구 …{cur[idx+len(pre)-25:end+12]!r}")
                    break
                idx = cur.find(pre + tok, idx + 1)
    print(f"== {rel}: 복구 {fixed}")
    total += fixed
    if not dry and fixed:
        io.open(p, "w", encoding="utf-8", newline="\n").write(cur)
print("총 복구", total)
