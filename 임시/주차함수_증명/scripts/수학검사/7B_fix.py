# -*- coding: utf-8 -*-
"""수학 검사 7B: 첨삭 뒤 수학 토큰 수정(멱등). 앵커가 파일 안에서 정확히 한 번 나타날 때만 치환한다.
실행: python -I scripts/수학검사/7B_fix.py
대상: 장v2/부록D_장7B.md — D.{{D:band102-integer}} 결과 (ㄹ)에서 수식 밖 유니코드 ν 셋을 수식으로 옮긴다.
      (같은 조각의 다른 자리는 모두 「$\nu=20$에서」, 「$\nu=96$–$100$으로」 꼴이므로 그 꼴을 따른다.)
      D.{{D:moment-certification}} 블록은 손대지 않는다. 장v2/장7B.md는 수정 없음."""
import io, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
TARGET = os.path.join(ROOT, "장v2", "부록D_장7B.md")

# (앵커, 치환) — 모두 원시 문자열
EDITS = [
    (r"(ν=59에서 $-0.0055$)",  r"($\nu=59$에서 $-0.0055$)"),
    (r"(ν=80에서 $-0.0075$)",  r"($\nu=80$에서 $-0.0075$)"),
    (r"(ν=96–100에서 $0.0244$", r"($\nu=96$–$100$에서 $0.0244$"),
]

def main():
    s = io.open(TARGET, encoding="utf-8").read()
    # 안전장치: moment-certification 블록 범위를 찾아 그 안을 건드리지 않는다.
    mc0 = s.index("### D.{{D:moment-certification}}")
    mc1 = s.index("### D.{{D:column-certificates-841-2000}}")
    changed = 0
    for old, new in EDITS:
        n_old, n_new = s.count(old), s.count(new)
        if n_old == 0 and n_new == 1:
            print(f"이미 적용됨: {old!r}")
            continue
        if n_old != 1:
            print(f"앵커 수 {n_old} != 1, 건너뜀: {old!r}"); continue
        pos = s.index(old)
        if mc0 <= pos < mc1:
            print(f"moment-certification 블록 안, 건너뜀: {old!r}"); continue
        s = s.replace(old, new, 1); changed += 1
        print(f"치환: {old!r} -> {new!r}")
    if changed:
        io.open(TARGET, "w", encoding="utf-8", newline="\n").write(s)
    print("치환 수", changed)

if __name__ == "__main__":
    main()
