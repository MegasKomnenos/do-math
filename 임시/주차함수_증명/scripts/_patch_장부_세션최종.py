# -*- coding: utf-8 -*-
"""설계 에이전트의 마지막 재생성 뒤 세션 몫의 사전 패치(멱등):
(1) 1.2 Riemann 제타 상수 행의 쓰이는 장에 7(7A 부록 D)을 더한다.
(2) 0절 R1′ 예외에 Riemann 제타 함수 ζ(s)(인수 있는 꼴)를 셋째 예외로 더하고 6절에 행을 둔다(세션 결정 58).
또 세션 결정 58을 세션 결정 파일에 적는다."""
import io
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def rw(path, fn):
    s = io.open(path, encoding="utf-8").read()
    t = fn(s)
    if t != s:
        io.open(path, "w", encoding="utf-8", newline="\n").write(t)
        print("patched", os.path.relpath(path, ROOT))
    else:
        print("unchanged", os.path.relpath(path, ROOT))


def patch_ledger_v2(s):
    # (1)
    a = "— 5B 집필 회수) | 5.5 | 5, 8, 9 | 없음 |"
    if s.count(a) == 1:
        s = s.replace(a, "— 5B 집필 회수) | 5.5 | 5, 7, 8, 9 | 없음 |")
    # (2) 0절
    b = "첨자의 수와 꼴로 갈린다(세션 결정 2)."
    if s.count(b) == 1 and "셋째 예외" not in s:
        s = s.replace(b, b + " 셋째 예외로 Riemann 제타 함수 $\\zeta(s)$는 인수를 가진 함수 꼴로만 쓰며 1장의 중앙 창 좌표 $\\zeta$(인수 없음)와 그 꼴로 갈린다; 세 값 $\\zeta(\\tfrac12)$, $\\zeta(-\\tfrac12)$, $\\zeta(\\tfrac32)$는 명명 상수 $\\mathsf z_{1/2}$, $\\mathsf z_{-1/2}$, $\\mathsf z_{3/2}$로 적는다(세션 결정 34·58).")
    # 6절 행
    c = "| $l$(라틴 소문자 엘) |"
    row = "| $\\zeta(s)$(Riemann 제타 함수; 셋째 예외) | 1장 중앙 창 좌표 $\\zeta$와 바탕 글자가 같으나 함수 꼴 $\\zeta(\\cdot)$로만 쓴다(5.2의 $\\cot$ 전개, 8.2의 Euler–Maclaurin 식; 세션 결정 58) | 인수 있는 꼴 그대로; 세 값은 $\\mathsf z_{1/2}$, $\\mathsf z_{-1/2}$, $\\mathsf z_{3/2}$ |\n"
    if s.count(c) == 1 and "셋째 예외) |" not in s:
        s = s.replace(c, row + c)
    return s


rw(os.path.join(ROOT, "장부_v2.md"), patch_ledger_v2)

D58 = (
    "58. **Riemann 제타 함수의 글자(2026-11-13 새벽).** 5.2의 $\\cot$ 전개($\\zeta(2m)$)와 8.2의 Euler–Maclaurin 식($\\zeta(\\beta)$)은 Riemann 제타 함수를 인수를 가진 꼴로 쓴다. 1장 전역 $\\zeta$(중앙 창 좌표)와 바탕 글자가 같지만 함수 꼴로만 쓰이므로 $d$·$x$에 이어 셋째 예외로 둔다(0절·6절). 세 값은 결정 34·48대로 $\\mathsf z$ 명명 상수(5.5 정의; 8장의 중복 정의 문장은 5.5를 가리키는 문장으로 바꿈).\n"
)


def patch_decisions(s):
    if "58. **Riemann 제타 함수의 글자" in s:
        return s
    assert "57. **작성자 판단의 문장 표지" in s
    return s.rstrip("\n") + "\n" + D58


rw(os.path.join(ROOT, "대조v2", "장부_설계_세션결정.md"), patch_decisions)
