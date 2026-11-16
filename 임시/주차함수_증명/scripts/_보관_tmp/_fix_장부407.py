# -*- coding: utf-8 -*-
"""장부 1.3절 「9.1 머리 합 조건의 양」 행에서 $\\mathfrak p_m(\\chi)$ 항목이 두 번 등재된 것 가운데 둘째를 괄호 짝을 따라 정확히 제거한다. 멱등."""
import io

P = r"C:\math\임시\주차함수_증명\장부_v2.md"
KEY = "$\\mathfrak p_m(\\chi)$("
lines = io.open(P, encoding="utf-8").read().split("\n")
idx = next(k for k, l in enumerate(lines) if l.startswith("| 9.1 머리 합 조건의 양"))
row = lines[idx]
first = row.find(KEY)
second = row.find(KEY, first + 1)
print("등장:", first, second, "| 괄호 전:", row.count("("), row.count(")"))
if second > 0:
    # 둘째 항목의 괄호 끝 찾기
    i = second + len(KEY) - 1  # '(' 위치
    depth = 0
    j = i
    while j < len(row):
        if row[j] == "(":
            depth += 1
        elif row[j] == ")":
            depth -= 1
            if depth == 0:
                break
        j += 1
    end = j + 1
    # 앞 구분자(", " 또는 "; ") 포함해 제거
    start = second
    for sep in (", ", "; "):
        if row[start - len(sep):start] == sep:
            start -= len(sep)
            break
    removed = row[start:end]
    print("제거:", removed[:240])
    row2 = row[:start] + row[end:]
    lines[idx] = row2
    io.open(P, "w", encoding="utf-8", newline="\n").write("\n".join(lines))
    print("괄호 후:", row2.count("("), row2.count(")"), "| 등장", row2.count(KEY))
else:
    print("중복 없음")
