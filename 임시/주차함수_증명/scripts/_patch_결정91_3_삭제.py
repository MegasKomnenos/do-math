# -*- coding: utf-8 -*-
"""사용자 결정 91 (3): 주 정리에 쓰이지 않는 순수 강화 결과의 블록 삭제와 장부 4절 뺌 처리(멱등).

지우는 블록(라벨): 7:S-infinity(+ 도입 문단, n♮_k·LM♭♭ 정의 문단), 7:lm-core, 7:moment-band(+ 도입 문단),
7:moment-window, 7.4 「왼쪽 잔여」 문단, 9:old-7-43(+ 도입·후속 문단), 2:old-2-42(+ 도입·후속 문단).
장부_v2.md: 4절 색인 행 여섯을 「뺌」 꼴로, 1.2·7절의 지운 글만 쓰던 기호 행 여섯을 삭제.
산문 수정(장 머리·절 도입·11.3 표·부록 D 항목 일부)은 Edit 도구로 따로 한다.
"""
import io
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)


def read(path):
    return io.open(path, encoding="utf-8").read().split("\n")


def write(path, lines):
    io.open(path, "w", encoding="utf-8", newline="\n").write("\n".join(lines))


def find_one(lines, prefix):
    hits = [i for i, l in enumerate(lines) if l.startswith(prefix)]
    if len(hits) != 1:
        raise SystemExit(f"[실패] '{prefix[:40]}…' 자리 {len(hits)}개")
    return hits[0]


def delete_block(name, first_prefix, last_prefix, must_contain, next_prefix):
    """first_prefix로 시작하는 줄부터 last_prefix로 시작하는 줄까지 지운다. 그 다음 비어 있지 않은 줄은 next_prefix여야 한다."""
    path = os.path.join(ROOT, "장v2", name)
    lines = read(path)
    if not any(l.startswith(first_prefix) for l in lines):
        print(f"[이미 적용] {name}: '{first_prefix[:30]}…' 없음")
        return
    a = find_one(lines, first_prefix)
    b = find_one(lines, last_prefix)
    if b < a:
        raise SystemExit(f"[실패] {name}: 끝이 시작보다 앞")
    block = lines[a:b + 1]
    for m in must_contain:
        if not any(l.startswith(m) for l in block):
            raise SystemExit(f"[실패] {name}: 블록 안에 '{m[:30]}…' 없음")
    # 다음 비어 있지 않은 줄
    j = b + 1
    while j < len(lines) and lines[j].strip() == "":
        j += 1
    if not lines[j].startswith(next_prefix):
        raise SystemExit(f"[실패] {name}: 블록 다음 줄이 '{next_prefix}'가 아님: {lines[j][:40]}")
    # 앞 빈 줄 하나는 남기고, 블록 뒤 빈 줄은 하나로
    new = lines[:a] + lines[j - 1:]
    # a-1이 빈 줄이고 j-1도 빈 줄이면 빈 줄이 둘이 되므로 하나 줄인다
    if a >= 1 and new[a - 1].strip() == "" and new[a].strip() == "":
        del new[a]
    write(path, new)
    print(f"{name}: {a + 1}–{b + 1}행 {b - a + 1}줄 삭제")


def main():
    delete_block(
        "장7A.md",
        "정리 {{7:self-consistent-S}}의 매개변수를 $k$와 함께 움직이고",
        "**증명.** $\\mathsf{LM}^{\\flat\\flat}\\Rightarrow\\mathsf{LM}$.",
        ["**정리 {{7:S-infinity}}", "따름정리 {{7:cor-S-prime}}과 정리 {{7:S-infinity}}가 닫는 범위의", "**명제 {{7:lm-core}}"],
        "### 7.3",
    )
    delete_block(
        "장7B.md",
        "**모멘트 판정의 같은 띠.**",
        "로 두고, 그 가운데 $\\nu\\ge41$인 부분을 $\\mathcal R^{(>40)}_{\\mathrm L}$로 둔다.",
        ["**정리 {{7:moment-band}}", "**따름정리 {{7:moment-window}}", "**왼쪽 잔여.**"],
        "### 7.5",
    )
    delete_block(
        "장9.md",
        "**둘째 하계: 거대 나무를 표시한 몫.**",
        "$\\mathfrak G$는 거대 나무 자신의 수준 질량",
        ["**정리 {{9:old-7-43}}"],
        "### 9.6",
    )
    delete_block(
        "장2.md",
        "쌍 항의 이중합에서 한 나무의 크기를 고정하고",
        "이 꼴로 보면 문턱 나무 손실은 크기 $k$인 나무가",
        ["**명제 {{2:old-2-42}}"],
        "### 2.11",
    )

    # 장부_v2.md
    path = os.path.join(ROOT, "장부_v2.md")
    lines = read(path)
    changed = 0
    # 4절 색인 행 → 뺌
    for label in ["2:old-2-42", "7:S-infinity", "7:lm-core", "7:moment-band", "7:moment-window", "9:old-7-43"]:
        tag = "{{" + label + "}}"
        hits = [i for i, l in enumerate(lines) if l.startswith("| ") and l.rstrip().endswith("| " + tag + " |")]
        if not hits:
            if any(l.rstrip().endswith("| (" + label + ") |") for l in lines):
                print(f"[이미 적용] 장부 4절 {label}")
                continue
            raise SystemExit(f"[실패] 장부 4절 행 없음: {label}")
        if len(hits) > 1:
            raise SystemExit(f"[실패] 장부 4절 행 중복: {label}")
        i = hits[0]
        cells = lines[i].split(" | ")
        # | 첫 판 번호 | 종류 | 이름 | 기록 | 절 | 라벨 |
        if len(cells) != 6:
            raise SystemExit(f"[실패] 장부 4절 행의 칸 수 {len(cells)}: {lines[i][:60]}")
        cells[4] = "뺌"
        cells[5] = "(" + label + ") |"
        lines[i] = " | ".join(cells)
        changed += 1
    # 지운 글만 쓰던 기호 행 삭제(1.2 네 줄, 7절 한 줄)
    for prefix in [
        "| $n^\\natural_k$ | n·일반(이탤릭) | 자기일관 상계(정리 S)의 경계",
        "| $\\mathcal R_{\\mathrm L}, \\mathcal R^{(>40)}_{\\mathrm L}$ | R·필기체 |",
        "| $\\mathcal W_M$ | W·필기체 | 모멘트 창",
        "| $\\mathsf{LM}$ | LM·산세리프 | 왼쪽 모멘트 명제 |",
        "| $\\mathsf{LM}^{\\flat\\flat}$ | LM·산세리프 |",
        "| $\\mathcal R_{\\mathrm L}$, $\\mathcal R^{(>40)}_{\\mathrm L}$ | [r475ada3], [r89eb039];",
    ]:
        hits = [i for i, l in enumerate(lines) if l.startswith(prefix)]
        if not hits:
            print(f"[이미 적용] 장부 기호 행 '{prefix[:30]}…' 없음")
            continue
        if len(hits) > 1:
            raise SystemExit(f"[실패] 장부 기호 행 중복: {prefix[:30]}")
        del lines[hits[0]]
        changed += 1
    write(path, lines)
    print(f"장부_v2.md: {changed}곳")
    return 0


if __name__ == "__main__":
    sys.exit(main())
