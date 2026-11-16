# -*- coding: utf-8 -*-
"""D.35(column-certificates-841-2000)의 구간 이식 적용 뒤 머리 손질: 7B의 머리 셋에 「방향 반올림 구간」을 더하고(D.34가 아직 binary64라 그 낱말은 남김),
11.3의 다섯째 고리 셀에서 명제 polar-W의 등급을 「방향 반올림 구간」으로 고친다(D.32 이식 때 빠진 셀). 멱등. --dry로 미리 보기."""
import io
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DRY = "--dry" in sys.argv

HEADS = [
    ("**정리 {{7:theorem-C-moment}}", "계산 보조(binary64 사전 오차 해석, 정확 정수·유리수)", "계산 보조(binary64 사전 오차 해석, 방향 반올림 구간, 정확 정수·유리수)"),
    ("**따름정리 {{7:moment-window}}", "계산 보조(binary64 사전 오차 해석, 정확 정수·유리수)", "계산 보조(binary64 사전 오차 해석, 방향 반올림 구간, 정확 정수·유리수)"),
    ("**따름정리 {{7:qstar-implies-wlflat}}", "계산 보조(binary64 사전 오차 해석)", "계산 보조(binary64 사전 오차 해석, 방향 반올림 구간)"),
]
CELL_OLD = "부록 D.{{D:column-certificates-841-2000}}), 명제 {{7:polar-W}}: binary64 사전 오차 해석;"
CELL_NEW = "부록 D.{{D:column-certificates-841-2000}}), 명제 {{7:polar-W}}: 방향 반올림 구간;"


def main():
    p7 = os.path.join(ROOT, "장v2", "장7B.md")
    lines = io.open(p7, encoding="utf-8").read().split("\n")
    n_done = 0
    for prefix, old, new in HEADS:
        hits = [i for i, l in enumerate(lines) if l.startswith(prefix)]
        if len(hits) != 1:
            print("머리 앵커 횟수", len(hits), prefix); sys.exit(1)
        i = hits[0]
        if new in lines[i]:
            print("이미:", prefix); continue
        if old not in lines[i]:
            print("등급 괄호 앵커 없음:", prefix, lines[i][:160]); sys.exit(1)
        lines[i] = lines[i].replace(old, new, 1); n_done += 1; print("머리 고침:", prefix)
    p11 = os.path.join(ROOT, "장v2", "장11.md")
    s11 = io.open(p11, encoding="utf-8").read()
    c = s11.count(CELL_OLD)
    if c == 1:
        s11 = s11.replace(CELL_OLD, CELL_NEW); n_done += 1; print("11.3 셀 고침(polar-W → 방향 반올림 구간)")
    elif CELL_NEW in s11:
        print("11.3 셀 이미")
    else:
        print("11.3 셀 앵커 횟수", c); sys.exit(1)
    for k, l in enumerate(s11.split("\n"), 1):
        if "polar-W" in l and "binary64" in l:
            print("남은 polar-W·binary64 공존 줄:", k, l[:200])
    if DRY:
        print("(dry)", n_done); return
    io.open(p7, "w", encoding="utf-8", newline="\n").write("\n".join(lines))
    io.open(p11, "w", encoding="utf-8", newline="\n").write(s11)
    print("기록함", n_done)


if __name__ == "__main__":
    main()
