# -*- coding: utf-8 -*-
"""R1b: 전 장 진술 머리의 지위 요약(라벨 | 종류 | 지위). 읽기만. 외부 입력(계산·문헌·의존·작성자 판단)을 가진 진술 표시."""
import io, os, re, glob
ROOT = r"C:\math\임시\주차함수_증명"
HEAD = re.compile(r"^\*\*(정의|정리|명제|보조정리|따름정리) \{\{(\d+:[A-Za-z0-9\-]+)\}\}(?: \((.*?)\))?(?: \[(.*?)\])?[.．]?\*\*")
KEY = ("계산 보조", "계산 증거", "문헌 인용", "에 의존", "작성자 판단", "시작점 비명시")
for p in sorted(glob.glob(os.path.join(ROOT, "장v2", "장*.md"))):
    f = os.path.basename(p)
    for i, ln in enumerate(io.open(p, encoding="utf-8").read().split("\n"), 1):
        m = HEAD.match(ln)
        if m:
            kind, lab, name, st = m.groups()
            st = (st or "")
            status = st.rsplit(";", 1)[0] if ";" in st else st
            flag = "*" if any(k in status for k in KEY) else " "
            print(f"{flag} {{{{{lab}}}}}\t{kind}\t{status.strip()}\t{f}:{i}")
