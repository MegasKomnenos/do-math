# -*- coding: utf-8 -*-
"""원 논문 인용을 arXiv 첫 판(v1, 2025-07-09)으로 고정한다. v2(2026-09-19)는 제목이 바뀌고 순열을 거친 셈이 §4.1로 옮겨졌으므로
본문·11.4의 절·식 번호는 v1 기준임을 식별자에 적는다. 멱등. 사용: python scripts/_fix_arXiv판본.py [--dry]"""
import io
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DRY = "--dry" in sys.argv
EDITS = [
    ("장v2/장2.md",
     "정리 {{2:old-2-3}}과 따름정리 {{2:old-2-4}}의 공식은 문제의 원 논문(Celano 외, §3)의 식 (3)·(4)와 같다. ",
     "정리 {{2:old-2-3}}과 따름정리 {{2:old-2-4}}의 공식은 문제의 원 논문(Celano 외, arXiv 첫 판 §3)의 식 (3)·(4)와 같다. ", 1),
    ("장v2/장11.md",
     r"| Celano 외, *Statistics on ℓ-interval parking functions*, arXiv:2507.07243 (2025) | Conjecture 6.5(문제 $\mathsf P$); §3의 식 (3)·(4)(결과 순열을 거쳐 세기) | 1.3절; 정리 {{2:old-2-3}}, 따름정리 {{2:old-2-4}} |",
     r"| Celano 외, *Statistics on ℓ-interval parking functions*, arXiv:2507.07243v1 (2025년 7월 9일) | Conjecture 6.5(문제 $\mathsf P$); §3의 식 (3)·(4)(결과 순열을 거쳐 세기). 절·식 번호는 첫 판의 것이다 | 1.3절; 정리 {{2:old-2-3}}, 따름정리 {{2:old-2-4}} |", 1),
    ("장v2/장1.md",
     "이 문제는 Celano와 공저자들의 논문 *Statistics on ℓ-interval parking functions*(arXiv:2507.07243)가 Conjecture 6.5로 제시한 것이다.",
     "이 문제는 Celano와 공저자들의 논문 *Statistics on ℓ-interval parking functions*(arXiv:2507.07243; 이 글은 2025년 7월 9일의 첫 판을 인용한다)가 Conjecture 6.5로 제시한 것이다.", 1),
]


def main():
    texts = {}
    bad = 0
    for rel, old, new, expect in EDITS:
        p = os.path.join(ROOT, rel)
        s = texts.get(rel) or io.open(p, encoding="utf-8").read()
        if new in s:
            print(f"{rel}: 이미"); texts[rel] = s; continue
        n = s.count(old)
        if n != expect:
            print(f"{rel}: 횟수 {n}≠{expect} — {old[:60]!r}"); bad += 1; texts[rel] = s; continue
        texts[rel] = s.replace(old, new); print(f"{rel}: {n}곳")
    if bad:
        print("문제 있음. 쓰지 않음."); sys.exit(1)
    if DRY:
        print("(dry)"); return
    for rel, s in texts.items():
        io.open(os.path.join(ROOT, rel), "w", encoding="utf-8", newline="\n").write(s)
    print("기록함")


if __name__ == "__main__":
    main()
