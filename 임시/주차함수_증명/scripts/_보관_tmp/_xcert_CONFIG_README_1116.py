# -*- coding: utf-8 -*-
"""18차 WD 인계 1–3: 재실행표 생성기의 xcert-partAB 실행 명령을 실제 실행 구성(부록D_장7A 「자료」 줄)대로, README·PARAS의 xcert 산문 한 문장, 여유 JSON 3행의 말씨. 2026-11-16 19:5x."""
import io, re
ROOT = r"C:\math\임시\주차함수_증명"
GEN = ROOT + r"\scripts\_gen_재실행표.py"
PAT = ROOT + r"\scripts\_patch_README_세션파일.py"
RD = ROOT + r"\원고_자료\README.md"
JS = ROOT + r"\scripts\_재실행표_여유.json"

def sub(path, pairs):
    s = io.open(path, encoding="utf-8").read()
    for a, b in pairs:
        n = s.count(a)
        if n != 1:
            raise SystemExit(f"{path.split(chr(92))[-1]}: {n}건 — {a[:80]}")
        s = s.replace(a, b)
    io.open(path, "w", encoding="utf-8", newline="\n").write(s)
    print("ok", path.split(chr(92))[-1])

old_cmd = '''        cmd=["python -I tables_iv.py",
             "python -I layerB.py --run --part 0 --nparts 2 --out resB_p0.jsonl",
             "python -I layerB.py --run --part 1 --nparts 2 --out resB_p1.jsonl",
             "python -I layerAint.py --run --part 0 --nparts 2 --idx 0 97 --out resAint_p0.jsonl",
             "python -I layerAint.py --run --part 1 --nparts 2 --idx 97 110 --out resAint_p1.jsonl",
             "python -I layerA1.py --run --part 0 --nparts 2 --out resA1_p0.jsonl",
             "python -I layerA1.py --run --part 1 --nparts 2 --out resA1_p1.jsonl",
             "python -I layerA2.py --run --out resA2.jsonl",
             "python -I layerA3.py --run --out resA3.json",
             "python -I summarize.py > summary.txt"],'''
new_cmd = '''        cmd=["python -I tables_iv.py",
             "python -I layerB.py --ks 501-5000 --part 0 --nparts 2 --out resB_p0.jsonl",
             "python -I layerB.py --ks 501-5000 --part 1 --nparts 2 --out resB_p1.jsonl",
             "[프로세스 1] python -I layerA1.py --run --part 0 --nparts 2 --out resA1_p0.jsonl",
             "[프로세스 1] python -I layerAint.py --run --part 1 --nparts 2 --idx 97 110 --out resAint_p1.jsonl",
             "[프로세스 1] python -I layerA1.py --run --part 1 --nparts 2 --out resA1_p1.jsonl",
             "[프로세스 1] python -I layerAint.py --run --part 0 --nparts 2 --idx 0 97 --out resAint_p0.jsonl",
             "[프로세스 2] python -I layerA1.py --run --part 3 --nparts 4 --idx 18 36 --out resA1_p3.jsonl",
             "[프로세스 2] python -I layerAint.py --run --part 3 --nparts 4 --idx 0 97 --out resAint_p3.jsonl",
             "[프로세스 2] python -I layerAint.py --run --part 2 --nparts 4 --idx 97 110 --out resAint_p2.jsonl",
             "[프로세스 2] python -I layerA1.py --run --part 2 --nparts 4 --idx 0 18 --out resA1_p2.jsonl",
             "python -I layerA2.py --run --out resA2.jsonl",
             "python -I layerA3.py",
             "python -I summarize.py > summary.txt"],'''
sub(GEN, [(old_cmd, new_cmd)])

old_txt = "범위별 실행은 `layerB.py`(범위 1 $[501,5000]$, `--part 0/1 --nparts 2`), `layerAint.py`(범위 2 $[5000,10^5]$, `--idx 0 97`·`--idx 97 110`), `layerA1.py`(범위 3), `layerA2.py`(범위 4), `layerA3.py`(범위 5)이고"
new_txt = ("범위별 코드는 `layerB.py`(범위 1 $[501,5000]$; `--ks 501-5000 --part 0/1 --nparts 2`), `layerAint.py`(범위 2 $[5000,10^5]$)·`layerA1.py`(범위 3; 두 프로세스가 `--idx`의 번호 범위를 받아 구간마다 요구 파일(`_claims/`)을 먼저 만든 쪽이 맡는 방식으로 나누어 돌렸고, "
           "명령과 조각 파일의 대응은 부록 D 항목의 「자료」 줄에 있다), `layerA2.py`(범위 4), `layerA3.py`(범위 5)이고")
sub(RD, [(old_txt, new_txt)])
# PARAS 안의 같은 문장(파이썬 문자열 리터럴 안; 백슬래시 없음)
sub(PAT, [(old_txt, new_txt)])

j = io.open(JS, encoding="utf-8").read()
a = "위 끝 $0.06573317522$ 대 진술"
if j.count(a) == 1:
    j = j.replace(a, "위 끝 $" + chr(92) + chr(92) + "le0.06573317522$ 대 진술")
    io.open(JS, "w", encoding="utf-8", newline="\n").write(j); print("ok 여유 JSON 3행")
else:
    print("여유 JSON 3행 문구", j.count(a), "건 — 손대지 않음")
