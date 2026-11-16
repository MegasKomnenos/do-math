# -*- coding: utf-8 -*-
"""장7A 산문 퇴고의 공통 적용기: (old, new) 쌍을 받아 old가 정확히 한 번 나타남을 모두 확인하고,
각 쌍의 수식 구간 열과 산문 숫자 토큰 다중집합이 같음을 확인한 뒤에만 치환해 쓴다."""
import collections
import io
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MATH_RE = re.compile(r"\$\$.*?\$\$|\$[^$\n]+\$", re.S)
NUM_RE = re.compile(r"(?<![A-Za-z\{])\d+(?:[.,]\d+)*")
LABEL_RE = re.compile(r"\{\{[0-9A-Za-z]+:[A-Za-z0-9\-]+\}\}")


def feats(t):
    maths = MATH_RE.findall(t)
    prose = MATH_RE.sub(" ", t)
    return maths, collections.Counter(NUM_RE.findall(prose)), collections.Counter(LABEL_RE.findall(t)), t.count("†"), t.count("∎"), t.count("**증명"), t.count("—")


def apply(relpath, pairs, dry=False, strict=True):
    path = os.path.join(ROOT, relpath)
    s = io.open(path, encoding="utf-8").read()
    bad = 0
    for i, (old, new) in enumerate(pairs):
        n = s.count(old)
        if n != 1:
            bad += 1
            print(f"[{i}] 앵커 {n}회: {old[:80]!r}")
            continue
        mo, no, lo, do, qo, po, dash_o = feats(old)
        mn, nn, ln, dn, qn, pn, dash_n = feats(new)
        if mo != mn:
            bad += 1
            k = next((t for t in range(min(len(mo), len(mn))) if mo[t] != mn[t]), min(len(mo), len(mn)))
            print(f"[{i}] 수식 열 다름 {len(mo)}→{len(mn)} 첫 차이 {k}: {mo[k:k+1]} → {mn[k:k+1]}")
        if no != nn:
            bad += 1
            print(f"[{i}] 숫자 토큰 다름: 사라짐 {list((no-nn).elements())} / 생김 {list((nn-no).elements())}")
        if lo != ln:
            bad += 1
            print(f"[{i}] 라벨 다름: 사라짐 {list((lo-ln).elements())} / 생김 {list((ln-lo).elements())}")
        if (do, qo, po) != (dn, qn, pn):
            bad += 1
            print(f"[{i}] †/∎/**증명 수 다름: {(do,qo,po)} → {(dn,qn,pn)}")
        if dash_n:
            print(f"[{i}] 경고: 새 글에 줄표 — {dash_n}개")
    if bad and strict:
        print("치환하지 않음(오류", bad, ")")
        sys.exit(1)
    for old, new in pairs:
        s = s.replace(old, new, 1)
    if dry:
        print("dry: 쌍", len(pairs), "모두 통과")
        return
    io.open(path, "w", encoding="utf-8", newline="\n").write(s)
    print("기록함:", relpath, "쌍", len(pairs))
