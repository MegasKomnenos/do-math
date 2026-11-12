# -*- coding: utf-8 -*-
"""9장 2차 대조 뒤 세션 몫: 장부 3절 두 행 정정, 지침 7.3에 지위 표지 관례 한 문장, 5절 여유 글자의 예약 h 점검."""
import io
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def rw(path, fn):
    s = io.open(path, encoding="utf-8").read()
    t = fn(s)
    if t != s:
        io.open(path, "w", encoding="utf-8", newline="\n").write(t)
        print("patched", os.path.relpath(path, ROOT))
    else:
        print("unchanged", os.path.relpath(path, ROOT))


def patch_ledger(s):
    lines = s.split("\n")
    in3 = False
    for i, ln in enumerate(lines):
        if ln.startswith("## 3. 낱말 사전"):
            in3 = True
        elif ln.startswith("## 4."):
            in3 = False
        if not in3:
            continue
        if ln.startswith("| 조건부 수준 질량 |"):
            lines[i] = ln.replace("$kc_N(k-1)/s_N(k)$", "$c_N(k-1)/s_N(k)$").replace("| 9.3 |", "| 7.5 |")
        if ln.startswith("| 분할 무게, 문턱 단위, 성장률, 생존비, 둘째 층 한 칸 비교, 실질 잔여, 증가 시작점, 개수 장부 |"):
            cells = ln.split(" | ")
            cells[0] = "| 분할 무게, 문턱 단위, 성장률, 생존비, 둘째 층 한 칸 비교, 실질 잔여, 개수 장부"
            cells[1] = cells[1].replace("7.7의 도구 이름", "7.7의 도구 이름(증가 시작점 $m_1(k)$은 9.1)")
            lines[i] = " | ".join(cells)
    s = "\n".join(lines)
    # 5절 여유 글자에서 예약 바탕 글자 h 점검(남아 있으면 제거)
    i5 = s.index("## 5. 장별 배정과 여유 글자"); i6 = s.index("## 6. 예약 글자")
    sec5 = s[i5:i6]
    n = len(re.findall(r"\$h\$, ", sec5))
    sec5 = re.sub(r"\$h\$, ", "", sec5)
    print("5절 여유 글자에서 $h$ 제거:", n)
    return s[:i5] + sec5 + s[i6:]


rw(os.path.join(ROOT, "장부_v2.md"), patch_ledger)


def patch_guide(s):
    a = "식별자 자리는 그 결과를 세운 기록의 식별자이고, 결과 자체가 문헌의 것이면 「표준」이다."
    assert s.count(a) == 1
    add = (" 지위 낱말은 그 진술 자체의 증명 지위다: 증명이 손으로 완결되었으나 계산 증거·계산 보조 진술에 기대면 「증명됨, X에 의존; r…」, 증명 안에 계산 단계가 있으면 「비형식 증명, 계산 보조(산술 등급)」(필요하면 「, X에 의존」을 더한다).")
    if "지위 낱말은 그 진술 자체의 증명 지위다" not in s:
        s = s.replace(a, a + add)
    return s


rw(os.path.join(ROOT, "파견", "집필_공통지침_v2.md"), patch_guide)
