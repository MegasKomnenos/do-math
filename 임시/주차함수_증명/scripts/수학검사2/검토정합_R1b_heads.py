# -*- coding: utf-8 -*-
"""R1b: 장6·7A·7B 진술 머리 추출(라벨 | 종류 | 이름 | 지위 | 식별자 | 파일:행). 읽기만."""
import io, os, re, sys
ROOT = r"C:\math\임시\주차함수_증명"
HEAD = re.compile(r"^\*\*(정의|정리|명제|보조정리|따름정리) \{\{(\d+:[A-Za-z0-9\-]+)\}\}(?: \((.*?)\))?(?: \[(.*?)\])?[.．]?\*\*")
for f in ["장6.md", "장7A.md", "장7B.md"]:
    p = os.path.join(ROOT, "장v2", f)
    sec = ""
    for i, ln in enumerate(io.open(p, encoding="utf-8").read().split("\n"), 1):
        if ln.startswith("### "):
            sec = ln[4:].strip()
        m = HEAD.match(ln)
        if m:
            kind, lab, name, st = m.groups()
            st = st or ""
            if ";" in st:
                status, ids = st.rsplit(";", 1)
            else:
                status, ids = st, ""
            print(f"{f}:{i}\t{sec}\t{kind}\t{{{{{lab}}}}}\t{name or ''}\t{status.strip()}\t{ids.strip()}")
