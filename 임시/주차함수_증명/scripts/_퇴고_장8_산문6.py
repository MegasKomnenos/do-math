# -*- coding: utf-8 -*-
"""장8 산문 퇴고 여섯째 묶음: 다섯째 독해(toego-jang8, 7cae55cd) 지적 1·2·4 반영(용어의 명확성·고유명사).
앞의 다섯 스크립트를 적용한 뒤에 돌린다. 각 원문 조각은 정확히 한 번 나타나야 하며, 하나라도 어긋나면 아무것도 쓰지 않는다."""
import io
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CH = os.path.join(ROOT, "장v2", "장8.md")

E = []  # (원문, 새 글, 절, 기준)

E.append((
"열이란 수준 하나를 고정하고 행을 따라 늘어놓은 개수들의 줄이고, 용량을 하나 고정하면 그 용량의 비교는 한 열에 놓인다.",
"열이란 수준 하나를 고정하고 행을 따라 늘어놓은 개수들의 줄이다. 용량 하나의 비교는 그 용량보다 하나 낮은 수준의 개수와 그 용량과 같은 수준의 개수를 견주는 것이고, 이 글은 그 비교를 낮은 쪽 수준의 열에 둔다.", "머리", "용어·독해1"))
E.append((
"첫 층은 크기가 용량을 넘되 용량의 두 배를 넘지 않는 나무들의 범위(나무로는 두 배에 하나를 더한 크기까지)이고,",
"첫 층은 행으로 말하면 크기가 용량을 넘되 용량의 두 배를 넘지 않는 범위이고, 나무로 말하면 크기가 용량을 넘되 용량의 두 배에 하나를 더한 값을 넘지 않는 나무들이며,", "머리", "용어·독해2"))
E.append((
r"""매 걸음 확률 $\pi^0_N(y)$ 이상으로 문턱 아래로 탈출한다.""",
r"""매 걸음, 숲에 크기가 문턱을 넘는 나무가 하나도 없을 확률 $\pi^0_N(y)$ 이상으로 문턱 아래로 탈출한다.""", "8.2", "용어·독해4"))
E.append((
r"""$y+1>N/2$이므로 $\pi_N(m)=\Pr_N(G=m)$($m\ge y+1$)이고 $\mathrm{km}_N\le""",
r"""$y+1>N/2$이므로 $\pi_N(m)=\Pr_N(G=m)$($m\ge y+1$; 오른쪽은 가장 큰 나무의 크기가 그 값일 확률)이고 $\mathrm{km}_N\le""", "8.2", "용어·독해4"))


def main():
    dry = "--dry" in sys.argv
    t = io.open(CH, encoding="utf-8").read()
    bad = 0
    for i, (old, new, sec, crit) in enumerate(E, 1):
        n = t.count(old)
        if n != 1:
            bad += 1
            print(f"[{i}] 원문 조각이 {n}번 나타남: {old[:70]!r}")
        else:
            t = t.replace(old, new, 1)
    if bad:
        print(f"어긋난 조각 {bad}개 — 아무것도 쓰지 않음")
        sys.exit(1)
    if dry:
        print(f"모든 조각 일치({len(E)}개); --dry라 쓰지 않음")
        return
    io.open(CH, "w", encoding="utf-8", newline="\n").write(t)
    print(f"적용 {len(E)}개")


if __name__ == "__main__":
    main()
