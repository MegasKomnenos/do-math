# -*- coding: utf-8 -*-
"""X4 (ㄷ) 보조: 6장 안의 (6.N) 참조(N>=20)마다 참조 문맥과 그 번호의 태그가 붙은 식의 앞줄을 나란히 찍는다(V2 재부여의 뜻 대조용)."""
import io, os, re
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
BS = chr(92)
lines = io.open(os.path.join(ROOT, "장v2", "장6.md"), encoding="utf-8").read().split("\n")
TAG = re.compile(BS + BS + r"tag\{6\.(\d+)\}")
tagline = {}
for i, ln in enumerate(lines):
    m = TAG.search(ln)
    if m:
        # 식 본문: 태그 줄 자체(한 줄에 식과 태그가 같이 있으면) 또는 바로 앞줄
        body = ln.replace(m.group(0), "").strip()
        if len(body) < 8 and i > 0: body = lines[i-1].strip()
        tagline[int(m.group(1))] = (i+1, body[:150])
REF = re.compile(r"\(6\.(\d+)\)")
for i, ln in enumerate(lines):
    if BS + "tag" in ln: continue
    for m in REF.finditer(ln):
        n = int(m.group(1))
        if n < 20: continue
        ctx = ln[max(0, m.start()-110):m.end()+60]
        t = tagline.get(n, ("없음", ""))
        print(f"장6:{i+1} (6.{n}) …{ctx}…\n      → 태그 행 {t[0]}: {t[1]}")
