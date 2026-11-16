# -*- coding: utf-8 -*-
"""수학 검사(태그 10) 수정 스크립트. 멱등. 앵커가 파일 안에서 정확히 한 번 나타날 때만 치환한다.

python -I scripts/수학검사/10_fix.py
"""
import io, sys, os

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
TARGET = os.path.join(ROOT, '장v2', '장10.md')

# (앵커, 치환) 목록. 원시 문자열로 적는다.
EDITS = [
    # 추가 과제 2: 10.1절 82행. 「2.6절의 성장률」 참조를 국소 정의로 바꾼다.
    # 2.6절(보조정리 {{2:old-2-26}}(나))에는 식 p_{m+1}/p_m=(m+1)e^{g(m+1)}이 있으나 「성장률」이라는 이름은 없다. 조정자 지시대로 라벨을 바로 가리키고 식은 더 넣지 않는다.
    (
        r"$e^{g(m+1)}=(1+\frac1{m+1})^m$은 2.6절의 성장률($p_{m+1}/p_m=(m+1)e^{g(m+1)}$)이고, $\mathfrak r_m=A_{m+1,k-1}/((m+1)A_{m,k-1})$은 6.2절의 제한 성장비다.",
        r"$e^{g(m+1)}=(1+\frac1{m+1})^m$은 보조정리 {{2:old-2-26}}(나)의 비 $p_{m+1}/p_m=(m+1)e^{g(m+1)}$에 나오는 인자이고, 아래에서 이것을 성장률이라 부른다. $\mathfrak r_m=A_{m+1,k-1}/((m+1)A_{m,k-1})$은 6.2절의 제한 성장비다.",
    ),
    # 과제 2의 첫 판(중간 꼴)에서 최종 꼴로 가는 전이용 항목(멱등 유지).
    (
        r"$e^{g(m+1)}=(1+\frac1{m+1})^m$은 비 $p_{m+1}/p_m=(m+1)e^{g(m+1)}$(보조정리 {{2:old-2-26}}(나))에 나오는 인자이고($g$는 2.6절의 함수), 아래에서 이것을 성장률이라 부른다. $\mathfrak r_m=A_{m+1,k-1}/((m+1)A_{m,k-1})$은 6.2절의 제한 성장비다.",
        r"$e^{g(m+1)}=(1+\frac1{m+1})^m$은 보조정리 {{2:old-2-26}}(나)의 비 $p_{m+1}/p_m=(m+1)e^{g(m+1)}$에 나오는 인자이고, 아래에서 이것을 성장률이라 부른다. $\mathfrak r_m=A_{m+1,k-1}/((m+1)A_{m,k-1})$은 6.2절의 제한 성장비다.",
    ),
    # 추가 과제 1: 88행 「순증가」 두 곳 → 「엄격히 증가한다」.
    (
        r"(b) $g$는 $x\ge1$에서 순증가한다. 곧 성장률 $e^{g(m+1)}$은 $m$에 대해 순증가한다.",
        r"(b) $g$는 $x\ge1$에서 엄격히 증가한다. 곧 성장률 $e^{g(m+1)}$은 $m$에 대해 엄격히 증가한다.",
    ),
    # 추가 과제 3: 10.7절 셋째 고리의 전제. 명제 {{7:old-6-20}}은 정리 {{6:V-all}}(판정 V)에 의존하고
    # 그 설명도 (V) 위에서 적으므로 전제 토큰은 $\mathsf V$가 맞다.
    (
        r"셋째 고리는 원천 쪽 ∧ $\mathsf V^\ast$ ∧ $\mathsf Q^\star_2$ ⇒ 열 $3131$ 이상의 $\mathsf Q^\star$다.",
        r"셋째 고리는 원천 쪽 ∧ $\mathsf V$ ∧ $\mathsf Q^\star_2$ ⇒ 열 $3131$ 이상의 $\mathsf Q^\star$다.",
    ),
]


def main():
    text = io.open(TARGET, encoding='utf-8').read()
    changed = 0
    for i, (old, new) in enumerate(EDITS, 1):
        n_old = text.count(old)
        n_new = text.count(new)
        if n_old == 0 and n_new == 1:
            print(f"[{i}] 이미 적용됨")
            continue
        if n_old != 1:
            print(f"[{i}] 앵커가 {n_old}번 나타남 — 건너뜀", file=sys.stderr)
            continue
        text = text.replace(old, new)
        changed += 1
        print(f"[{i}] 치환함")
    if changed:
        io.open(TARGET, 'w', encoding='utf-8', newline='\n').write(text)
    print(f"치환 {changed}건")


if __name__ == '__main__':
    main()
