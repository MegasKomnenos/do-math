# -*- coding: utf-8 -*-
"""장8 산문 퇴고 셋째 묶음: 둘째 독해(toego-jang8, 722440f9)의 지적 2·3·5번 반영. 앞의 두 스크립트를 적용한 뒤에 돌린다.
각 원문 조각은 정확히 한 번 나타나야 하며, 하나라도 어긋나면 아무것도 쓰지 않는다. 사용: python -I scripts/_퇴고_장8_산문3.py [--dry]"""
import io
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CH = os.path.join(ROOT, "장v2", "장8.md")
AP = os.path.join(ROOT, "장v2", "부록D_장8.md")

E = []  # (파일, 원문, 새 글, 절, 기준)

E.append((CH,
r"""왼쪽은 크기 $k$의 나무 하나가 수준 $k-1$에 서고(뿌리의 변위가 $k-1$일 확률 $1/k$) 그 환경, 곧 크기 $N=n-k$의 나머지 숲이 용량 $k$ 아래에서 살아남는 확률이다. 오른쪽은 크기 $m+1>2k+1$의 큰 나무 하나가 있고 그 안의 최대 변위가 수준 $k$ 또는 $k-1$에 놓일 확률이다.""",
r"""왼쪽은 크기 $k$의 나무 하나가 수준 $k-1$에 서고(뿌리의 변위가 $k-1$일 확률이 $1/k$다) 그 환경, 곧 크기 $N=n-k$의 나머지 숲이 용량 $k$ 아래에서 살아남을 확률을, 그런 나무마다 세어 더한 것이다. 오른쪽은 크기 $m+1>2k+1$의 큰 나무 하나가 있고 그 안의 최대 변위가 수준 $k$ 또는 $k-1$에 놓일 확률을, 큰 나무의 크기마다 더한 것이다.""", "머리", "용어·연결·독해2"))

E.append((CH,
r"""그래서 제값으로 세는 것은 환경이 $k$ 이상인 착지뿐이고, 그 몫만으로는 띠의 끝까지 가지 못한다.""",
r"""그래서 환경이 가벼운 착지는 제 몫을 받지 못하고, 환경이 $k$ 이상인 착지의 몫만으로는 띠의 끝까지 가지 못한다.""", "8.3", "용어·독해3"))

E.append((AP,
"증명이 검사하는 시험 함수는 이렇게 저장된 절점 값과 기울기로 고정된 함수다.",
"증명이 검사하는 시험 함수는 저장된 절점 값에 위의 기울기 규칙을 적용해 정해지는 함수 하나이고, 아래의 구간 평가는 그 함수를 감싼다.", "부록D", "용어·독해5"))


def main():
    dry = "--dry" in sys.argv
    texts = {p: io.open(p, encoding="utf-8").read() for p in {CH, AP}}
    bad = 0
    for i, (p, old, new, sec, crit) in enumerate(E, 1):
        n = texts[p].count(old)
        if n != 1:
            bad += 1
            print(f"[{i}] {os.path.basename(p)}: 원문 조각이 {n}번 나타남: {old[:70]!r}")
        else:
            texts[p] = texts[p].replace(old, new, 1)
    if bad:
        print(f"어긋난 조각 {bad}개 — 아무것도 쓰지 않음")
        sys.exit(1)
    if dry:
        print(f"모든 조각 일치({len(E)}개); --dry라 쓰지 않음")
        return
    for p, t in texts.items():
        io.open(p, "w", encoding="utf-8", newline="\n").write(t)
    print(f"적용 {len(E)}개")


if __name__ == "__main__":
    main()
