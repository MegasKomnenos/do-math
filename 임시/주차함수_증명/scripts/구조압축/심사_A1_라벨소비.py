# -*- coding: utf-8 -*-
"""2장 라벨의 저장소 내 소비처 셈 (심사 A1). 장v2/*.md, 장부_v2.md 를 읽어 {{2:...}} 라벨별 파일·행 수를 센다."""
import re, glob, os, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
root = r"C:\math\임시\주차함수_증명"
files = sorted(glob.glob(os.path.join(root, "장v2", "*.md"))) + [os.path.join(root, "장부_v2.md")]
pat = re.compile(r"\{\{(2:[^}]+)\}\}")
occ = {}
for f in files:
    name = os.path.relpath(f, root)
    with open(f, encoding="utf-8") as fh:
        for ln, line in enumerate(fh, 1):
            for m in pat.finditer(line):
                occ.setdefault(m.group(1), {}).setdefault(name, []).append(ln)
for lab in sorted(occ):
    d = occ[lab]
    tot = sum(len(v) for v in d.values())
    parts = []
    for name in sorted(d):
        short = os.path.basename(name).replace(".md", "")
        parts.append(f"{short}:{len(d[name])}")
    print(f"{lab}\t{tot}\t" + " ".join(parts))
