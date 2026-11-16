# -*- coding: utf-8 -*-
"""ZV8 6.4: 재실행표 생성기의 band-check 항목(scripts 차례·cmd·expect·time)과 여유 JSON 19행을 band_cells.py 근거로 바꾼다. 2026-11-16."""
import io, os
ROOT = r"C:\math\임시\주차함수_증명"


def sub(rel, pairs):
    p = os.path.join(ROOT, rel)
    s = io.open(p, encoding="utf-8").read()
    for a, b in pairs:
        n = s.count(a)
        if n != 1:
            raise SystemExit(f"{rel}: {n}건 — {a[:80]}")
        s = s.replace(a, b)
    io.open(p, "w", encoding="utf-8", newline="\n").write(s)
    print("ok", rel, len(pairs))


sub(r"scripts\_gen_재실행표.py", [
    ('scripts=[S + "band_check/band_iv.py", S + "band_check/band_cells.py", S + "band_check/band_read.py"],',
     'scripts=[S + "band_check/band_cells.py", S + "band_check/band_read.py", S + "band_check/band_iv.py"],'),
    ('cmd=["python -I band_iv.py 0.71216 0 4000", "python -I band_cells.py 0.71216 0 4000 band_cells_CE0.tsv",\n             "python -I band_read.py band_cells_CE0.tsv band_iv_out_CE0.txt"],',
     'cmd=["python -I band_cells.py 0.71216 0 4000 band_cells_CE0.tsv", "python -I band_read.py band_cells_CE0.tsv band_iv_out_CE0.txt",\n             "python -I band_iv.py 0.71216 0 4000"],'),
    ('expect="certified min ratio = 1.355874(첫 소구간 $[1/2,12001/24000]$); 판독 최솟값 $1.3558739652$, 문턱 $1.3558$ 미만 소구간 0개",',
     'expect="minimum ratio lower bound = 1.35587396520276(첫 소구간 $[1/2,12001/24000]$); 판독 최솟값 $1.3558739652$, 문턱 $1.3558$ 미만 소구간 0개; 기록 코드의 재실행 certified min ratio = 1.355874",'),
    ('outputs=[S + "band_check/band_iv_out_CE0.txt", S + "band_check/band_cells_CE0.tsv", S + "band_check/band_read_out_CE0.txt"],',
     'outputs=[S + "band_check/band_cells_CE0.tsv", S + "band_check/band_read_out_CE0.txt", S + "band_check/band_iv_out_CE0.txt"],'),
    ('time="`band_iv.py` 약 40초, `band_cells.py` 약 34초, `band_read.py` 약 2초(2026-11-13, 다른 계산과 코어 공유)"),',
     'time="`band_cells.py` 약 25–35초, `band_read.py` 약 2초, `band_iv.py` 약 40초(다른 계산과 코어 공유)"),'),
])
sub(r"scripts\_재실행표_여유.json", [
    ('"band-check": "최소 비 $1.355874$(첫 소구간 $[\\\\frac12,\\\\frac12+\\\\frac1{24000}]$) 대 문턱 $1.3558$(독립 판독 $1.3558740$, 여유 $7.4\\\\times10^{-5}$); $(5.53)$이 쓰는 $1$ 대비 $0.3558$",',
     '"band-check": "최소 비의 하계 $1.3558739652$(첫 소구간 $[\\\\frac12,\\\\frac12+\\\\frac1{24000}]$) 대 문턱 $1.3558$(여유 $7.4\\\\times10^{-5}$; 기록 코드의 재실행 $1.355874$와 표시 자리에서 일치); $(5.53)$이 쓰는 $1$ 대비 $0.3558$",'),
])
