# -*- coding: utf-8 -*-
"""작업 장부: 6장 2차 대조의 출력 한도 중단과 재개, 다른 2차 대조 셋에 보낸 예방 통지를 적는다."""
import io
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = os.path.join(ROOT, "작업_장부.md")
s = io.open(P, encoding="utf-8").read()

ENTRY = (
    "- 2026-11-12 23:3x 6장 2차 대조(a034b02a01474e198) **출력 한도 중단**: 보고서를 한 번의 Write로 쓰다 64,000 출력 토큰 한도에 걸려 종료(보고서 파일 없음, 분석 맥락은 보존). SendMessage로 재개 — 대조 반복 없이 보고서만 절 경계에서 네댓 조각(`_장6_2차대조_p*.md`, 호출당 12,000 토큰 이하)으로 쓰고 `python -c`로 이어 붙이게 함. 완료 판정은 `대조v2/장6_2차대조.md`의 실재. "
    "같은 실패를 막으려 실행 중인 5B·7B·5A 2차 대조에도 조각 쓰기 지시를 보냄(7B에는 세션 결정 42·43과 7A 2차 대조의 판정 — 394행 old-6-9 인용 오류, polar-R (나)·P′·G′ 새 라벨 — 도 함께; 5A에는 예약 글자 잔존 목록). "
    "교훈: 2차 대조 파견문 생성기와 공통 계약에 「보고서는 조각으로 나누어 쓴다(호출당 12,000 토큰 이하)」를 넣어야 한다(`scripts/_gen_2차대조v2_파견문.py` 수정; 다음 파견부터)."
)
old = "\n## 재개 기록\n"
assert s.count(old) == 1
if "출력 한도 중단**" not in s:
    s = s.replace(old, "\n" + ENTRY + "\n" + old)
io.open(P, "w", encoding="utf-8", newline="\n").write(s)
print("patched 작업_장부.md (6장 2차 대조 재개)")
