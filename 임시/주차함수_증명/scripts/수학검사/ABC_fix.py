# -*- coding: utf-8 -*-
"""수학 검사 태그 ABC(부록 A·B·C)의 수정 스크립트. 멱등.

앵커가 파일 안에서 정확히 한 번 나타날 때만 치환한다.
2026-11-14 검사 결과 부록 A·B·C에서 고칠 토큰이 없어 치환 목록이 비어 있다.
생성기(scripts/부록_v2.py)는 건드리지 않는다. 사용: python -I scripts/수학검사/ABC_fix.py
"""
import io, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# (파일, 앵커(전), 치환(후)) — 비어 있음
FIXES = []

def apply(path, old, new):
    with io.open(path, encoding="utf-8") as f:
        s = f.read()
    if new in s and old not in s:
        return "이미 적용"
    n = s.count(old)
    if n != 1:
        return f"앵커 {n}회 — 건너뜀"
    s = s.replace(old, new)
    with io.open(path, "w", encoding="utf-8", newline="") as f:
        f.write(s)
    return "적용"

def main():
    if not FIXES:
        print("치환 목록 비어 있음 — 변경 없음")
        return
    for rel, old, new in FIXES:
        print(rel, "→", apply(os.path.join(ROOT, rel), old, new))

if __name__ == "__main__":
    main()
