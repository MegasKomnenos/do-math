# -*- coding: utf-8 -*-
"""수학 검사 둘째(태그 3): 수학 토큰 수정(멱등). 앵커가 파일 안에서 정확히 한 번 나타날 때만 치환한다.
실행: python -I scripts/수학검사2/3_fix.py
대상: 장v2/부록D_장3.md — D.{{D:logconcavity-failure-n80}} 「독립 재계산」 줄.
      「모든 $0\\le\\ell\\le119$, $1\\le n\\le120$의 $A_{n,\\ell}$을 다시 계산했고, $A_{n,\\ell}$의 14,520개 값」에서
      14,520 = 121×120 은 $n=0$ 행을 포함한 수다(기록 r81e7051 evidence/peer_verify.py 9·14–20·85행:
      A=[[1]*N] 에 n=1..120 행을 붙여 len(A)*N = 121·120 = 14,520; verification.md §2 「빈 행을 포함한 A의 14,520개 항」).
      $1\\le n\\le120$ 이면 14,400개이므로 범위를 $0\\le n\\le120$ 으로 고친다.
      장v2/장3.md 는 수정 없음."""
import io, os

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
TARGET = os.path.join(ROOT, "장v2", "부록D_장3.md")

# (앵커, 치환) — 모두 원시 문자열
EDITS = [
    (r"모든 $0\le\ell\le119$, $1\le n\le120$의 $A_{n,\ell}$을 다시 계산했고, $A_{n,\ell}$의 14,520개 값",
     r"모든 $0\le\ell\le119$, $0\le n\le120$의 $A_{n,\ell}$을 다시 계산했고, $A_{n,\ell}$의 14,520개 값"),
]


def main():
    s = io.open(TARGET, encoding="utf-8").read()
    changed = 0
    for old, new in EDITS:
        n_old, n_new = s.count(old), s.count(new)
        if n_old == 0 and n_new == 1:
            print(f"이미 적용됨: {old!r}")
            continue
        if n_old != 1:
            print(f"앵커 수 {n_old} != 1, 건너뜀: {old!r}")
            continue
        s = s.replace(old, new, 1)
        changed += 1
        print(f"치환: {old!r} -> {new!r}")
    if changed:
        io.open(TARGET, "w", encoding="utf-8", newline="\n").write(s)
    print("치환 수", changed)


if __name__ == "__main__":
    main()
