# -*- coding: utf-8 -*-
"""명제 polar-W의 상계 1.445가 블록 [2061,2086]의 실제 값 1.44545를 담지 못하므로 1.446으로 올리고, 그 상수를 쓰는 7B의 사슬 상수를 함께 맞춘다. 멱등."""
import io
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DRY = "--dry" in sys.argv
EDITS = [
    ("장v2/장7A.md", r"$V\sqrt k\le1.445$", r"$V\sqrt k\le1.446$", 2),
    ("장v2/장7A.md", r"\mathfrak P_k(n)\le1.445/\sqrt k", r"\mathfrak P_k(n)\le1.446/\sqrt k", 1),
    ("장v2/부록D_장7A.md", r"$V\sqrt k\le1.445$", r"$V\sqrt k\le1.446$", 2),
    ("장v2/장7B.md", r"\mathfrak P_k(n)\le1.445/\sqrt k", r"\mathfrak P_k(n)\le1.446/\sqrt k", 1),
    ("장v2/장7B.md", r"-1.445n/\sqrt k", r"-1.446n/\sqrt k", 1),
    ("장v2/장7B.md", r"-2.89k=1.11k-6.18\sqrt k>0$이다($\sqrt k>5.57$)", r"-2.892k=1.108k-6.18\sqrt k>0$이다($\sqrt k>5.58$)", 1),
    ("장v2/장7B.md", r"/(k+1)-1.445/\sqrt k\ge(4\sqrt k-3.09)/(k+1)-1.445/\sqrt k", r"/(k+1)-1.446/\sqrt k\ge(4\sqrt k-3.09)/(k+1)-1.446/\sqrt k", 1),
    ("장v2/장7B.md", r"$2.555k>3.09\sqrt k+1.445$", r"$2.554k>3.09\sqrt k+1.446$", 1),
]


def main():
    texts = {}
    bad = 0
    for rel, old, new, expect in EDITS:
        p = os.path.join(ROOT, rel)
        s = texts.get(rel)
        if s is None:
            s = io.open(p, encoding="utf-8").read()
        n = s.count(old)
        if n == 0 and new in s:
            print(f"{rel}: 이미 — {old[:40]!r}"); texts[rel] = s; continue
        if n != expect:
            print(f"{rel}: 횟수 {n}≠{expect} — {old[:60]!r}"); bad += 1; texts[rel] = s; continue
        texts[rel] = s.replace(old, new); print(f"{rel}: {n}곳 — {old[:48]!r}")
    if bad:
        print("문제 있음. 쓰지 않음."); sys.exit(1)
    if DRY:
        print("(dry)"); return
    for rel, t in texts.items():
        io.open(os.path.join(ROOT, rel), "w", encoding="utf-8", newline="\n").write(t)
    print("기록함")


if __name__ == "__main__":
    main()
