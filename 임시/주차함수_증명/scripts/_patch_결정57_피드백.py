# -*- coding: utf-8 -*-
"""외부 피드백 반영: 세션 결정 57(작성자 판단 문장 표지를 칼표 †로)을 적고, 작업 장부에 피드백 처리 항목을 더한다."""
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


D57 = (
    "57. **작성자 판단의 문장 표지(2026-11-13 새벽; 외부 독자 피드백).** 증명 안 문장 앞의 「(작성자 판단)」 낱말 표지는 출판 원고에서 거칠다는 피드백을 받아, 문장 표지를 칼표 †로 바꾼다(진술 머리의 덧붙임 「작성자 판단」은 그대로). 1.5에 「본문에서는 그 단계가 시작하는 문장 앞에 칼표 †를 붙인다」로 설명한다. 지침 4.4의 문장 표지 규정도 같은 뜻으로 읽는다(기존 62곳 일괄 치환; 이후 집필은 †). 감사 정보(어느 단계가 기록에 없는가)는 유지된다.\n"
)


def patch_decisions(s):
    if "57. **작성자 판단의 문장 표지" in s:
        return s
    assert "56. **집필자 글자와 그 장의 전역의 겹침" in s
    return s.rstrip("\n") + "\n" + D57


rw(os.path.join(ROOT, "대조v2", "장부_설계_세션결정.md"), patch_decisions)


ENTRY = (
    "- 2026-11-13 03:2x **외부 피드백 처리**(사용자 전달; 조립 1차본에 대한 독자 지적 8종): (1) 부록 A·C에 사전의 작업 메모(첫 판 참조·세션 결정·2차 대조·회수) 노출 — 부록 A 60행·C 24행 확인 → `부록_v2.py`에 뜻·비고·대응 열 정화기 `clean()`(작업 메모가 든 괄호·쌍반점 조각 제거)와 부록 C 영어 열 제거(영어는 용어 칸에 괄호로) 추가; 설계 에이전트는 1.2·1.3·2·3·7절의 첫 판 번호 38곳을 라벨로 바꿈. (2) 글자 치환이 만든 깨진 명령 — `\\ley`·`\\leU`·`\\inftyy`·`\\fracy`·`\\mathfrak sy`·`\\mathfrak am` 11곳 세션 복구; 6장의 역참조 잔재 `_\\1` 31곳(Σ_1·Σ_2·Σ_3·U_d 첨자 소실)은 6장 집필자 긴급 재개(커밋 원문 대조). (3) 3장 로그오목 꼬리 합 $T_hT_{3I}\\to T_IT_{3I}$ 복구. (4) 7A 정리 7.20 증명의 옛 $T$ 5곳 → $\\mathcal J^{\\mathrm S}$. (5) 7B 식 번호 (7.1)–(7.29)가 7A (7.1)과 겹침 → 7B·부록 D의 119곳을 (7.2)–(7.30)으로. (6) 부록 C 짧은 식별자 r9e782·r8d685(사전 7절; 설계 에이전트 재생성이 되돌린 것) → 장부에서 r9e782f5·r8d6850a로 9곳. (7) 7A 부록 D의 표 값 가족 $\\mathfrak K$(세션 치환으로 일부가 km이 된 것) → $\\mathrm{pw}$ 가족 27곳. (8) 「(작성자 판단)」 문장 표지 62곳 → 칼표 †(세션 결정 57; 1.5 설명 문장 변경). 깨진 명령은 KaTeX 렌더(PDF 단계)로 다시 전수 확인할 것."
)


def patch_ledger(s):
    old = "\n## 재개 기록\n"
    assert s.count(old) == 1
    if "**외부 피드백 처리**" in s:
        return s
    return s.replace(old, "\n" + ENTRY + "\n" + old)


rw(os.path.join(ROOT, "작업_장부.md"), patch_ledger)
