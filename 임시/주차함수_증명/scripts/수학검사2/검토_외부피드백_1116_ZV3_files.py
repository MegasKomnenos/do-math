# -*- coding: utf-8 -*-
"""ZV3 탐색: 부록 D(장v2/부록D_장*.md)의 모든 줄에서 백틱 안의 파일 이름(확장자 있는 토큰)을 모아
자료 묶음 원고_자료/ 어딘가에 같은 이름의 파일이 있는지 본다. 「자료」 줄 밖(독립 재계산·알고리즘·결과 줄)에서
인용된 파일이 묶음에 없으면 그 항목의 「자료」 줄에 빠진 것이다(외부 피드백 10.2의 같은 종류).
사용: python -I scripts/수학검사2/검토_외부피드백_1116_ZV3_files.py
"""
import glob
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
BUNDLE = os.path.join(ROOT, "원고_자료")
TOK = re.compile(r"`([^`]+)`")
FNAME = re.compile(r"^[A-Za-z0-9_.\-]+\.(py|c|json|txt|out|npy|npz|tsv|csv|log|md|sh|bat|jsonl|bin|h)$")

names_in_bundle = {}
for dp, dn, fn in os.walk(BUNDLE):
    for f in fn:
        names_in_bundle.setdefault(f, []).append(os.path.relpath(os.path.join(dp, f), BUNDLE).replace("\\", "/"))

for path in sorted(glob.glob(os.path.join(ROOT, "장v2", "부록D_장*.md"))):
    cur = None
    for ln in open(path, encoding="utf-8"):
        m = re.match(r"^### D\.\{\{D:([^}]+)\}\}", ln)
        if m:
            cur = m.group(1)
            continue
        kind = "자료" if ln.startswith("**자료.**") else ("재계산" if ln.startswith("**독립 재계산.**") else "기타")
        for t in TOK.findall(ln):
            base = t.split("/")[-1].split("\\")[-1]
            if "*" in base or not FNAME.match(base):
                continue
            if base not in names_in_bundle:
                print(f"{os.path.basename(path)} | D.{cur} | {kind} | `{t}` | 묶음에 없음")
