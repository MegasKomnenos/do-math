# -*- coding: utf-8 -*-
"""장v2 산문 편집의 공통 적용기. (old, new) 쌍을 받아 모든 old가 파일에 정확히 한 번 나타날 때에만 치환한다.
사용: 각 묶음 스크립트가 apply(relpath, PAIRS, dry) 를 부른다. relpath는 장v2/ 기준."""
import io, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
BASE = os.path.join(ROOT, "장v2")

def apply(relpath, pairs, dry=False):
    path = os.path.join(BASE, relpath)
    s = io.open(path, encoding="utf-8").read()
    bad = 0
    for i, (old, new) in enumerate(pairs):
        n = s.count(old)
        if n != 1:
            bad += 1
            print(f"[{i}] 앵커 {n}회: {old[:80]!r}")
        if old == new:
            bad += 1
            print(f"[{i}] old == new")
    if bad:
        print("치환하지 않음(앵커 오류", bad, ")")
        sys.exit(1)
    for old, new in pairs:
        s = s.replace(old, new, 1)
    if dry:
        print("dry:", relpath, "쌍", len(pairs), "모두 유일")
        return
    io.open(path, "w", encoding="utf-8", newline="\n").write(s)
    print("기록함:", relpath, "쌍", len(pairs))
