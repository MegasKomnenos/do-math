# -*- coding: utf-8 -*-
"""장9 산문 퇴고의 공통 적용기: (old, new) 쌍을 받아 old가 정확히 한 번 나타남을 모두 확인한 뒤에만 치환해 쓴다."""
import io
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def apply(relpath, pairs, dry=False):
    path = os.path.join(ROOT, relpath)
    s = io.open(path, encoding="utf-8").read()
    bad = 0
    for i, (old, new) in enumerate(pairs):
        n = s.count(old)
        if n != 1:
            bad += 1
            print(f"[{i}] 앵커 {n}회: {old[:70]!r}")
    if bad:
        print("치환하지 않음(앵커 오류", bad, ")")
        sys.exit(1)
    for old, new in pairs:
        s = s.replace(old, new, 1)
    if dry:
        print("dry: 쌍", len(pairs), "모두 유일")
        return
    io.open(path, "w", encoding="utf-8", newline="\n").write(s)
    print("기록함:", relpath, "쌍", len(pairs))
