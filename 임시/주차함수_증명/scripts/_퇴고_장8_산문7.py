# -*- coding: utf-8 -*-
"""장8 산문 퇴고 일곱째 묶음: 여섯째 독해(toego-jang8, 22eb86a2) 지적 3번 반영 — 수준 질량의 풀이에서 나무와 내부 숲의 혼동을 바로잡는다.
앞의 여섯 스크립트를 적용한 뒤에 돌린다. 원문 조각이 정확히 한 번 나타나지 않으면 아무것도 쓰지 않는다."""
import io
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CH = os.path.join(ROOT, "장v2", "장8.md")

E = [(
r"""둘째 층 나무의 최대 변위가 정확히 용량과 같을 확률인 수준 질량 $c_m(k)$""",
r"""둘째 층 나무의 내부 숲이 최대 변위를 정확히 용량과 같게 가질 확률인 수준 질량 $c_m(k)$""", "머리", "용어·독해3")]


def main():
    dry = "--dry" in sys.argv
    t = io.open(CH, encoding="utf-8").read()
    for i, (old, new, sec, crit) in enumerate(E, 1):
        n = t.count(old)
        if n != 1:
            print(f"[{i}] 원문 조각이 {n}번 나타남 — 아무것도 쓰지 않음")
            sys.exit(1)
        t = t.replace(old, new, 1)
    if dry:
        print(f"모든 조각 일치({len(E)}개); --dry라 쓰지 않음")
        return
    io.open(CH, "w", encoding="utf-8", newline="\n").write(t)
    print(f"적용 {len(E)}개")


if __name__ == "__main__":
    main()
