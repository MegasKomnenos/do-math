# -*- coding: utf-8 -*-
"""작업 장부: 11장 회수, 11.2 채움, 11장 발견 다섯 처리, 전체 조립과 검사 통과, 일관성 검토 파견."""
import io
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = os.path.join(ROOT, "작업_장부.md")
s = io.open(P, encoding="utf-8").read()
ENTRY = (
    "- 2026-11-13 03:4x **11장 회수와 전체 조립**: 11장(opus-high, 31분) — `장v2/장11.md`(22KB, 98행; 11.1 두 문단, 11.2 표 틀, 11.3 산문 여섯 문단+표 셋(공유 15·첫째 고유 6·둘째 고유 4; 장v2 머리~∎의 의존 그래프에서 두 닫는 정리의 닫힘을 구해 교집합·차집합), 11.4 문헌 20편·표 22행 — Fekete·Hermite–Hadamard는 본문에 없어 제외), `대조v2/장11_집필대조.md`(행별 근거). 세션: 11.2 표 47행을 `_gen_11_2표.py --fill`로 채움(절단 없음). "
    "11장 집필자가 조립본에서 찾은 다른 장의 어긋남 다섯을 세션이 정확 문자열로 고침(`_fix_11장발견.py`): 10.7 셋째 고리의 old-6-17(나)→src-plus, 9.6의 판정 V 인용 old-6-19→V-all, 10.38·old-8-10·old-8-14 머리 「비형식 증명」→「증명됨」(손 조립; 결정 38), 등급 서식 셋(7A 「와」→쉼표, 6장 괄호 안 쌍반점→쉼표, 7B 「계산 증거, 계산 보조」→「비형식 증명, 계산 보조」). 서지 보충 확인 요(Ibragimov·Tanner·Jensen 제목·학술지, Wallis 1656, Flajolet–Sedgewick 출판사)는 일관성 검토 담당 ㄴ에. "
    "**전체 조립**(`원고.md` 1–11장+부록 A–D, 2.13MB·11,449행): 라벨 432 해소, 부록 D 47, [todo] 0, 불변식 0, KaTeX 34,233식 오류 0, 수식 균형 0, 예약 글자 0, 부록 메모 0. 다음: 일관성 검토 셋(ㄱ·ㄴ·ㄷ) 파견 → 결과 반영(장당 한 번) → 독립 독해 → verify-rounds → PDF → 커밋."
)
old = "\n## 재개 기록\n"
assert s.count(old) == 1
if "**11장 회수와 전체 조립**" not in s:
    s = s.replace(old, "\n" + ENTRY + "\n" + old)
s = s.replace("(조립 2차: 자동 검사 전부 통과 — KaTeX 0·불변식 0·균형 0·예약 글자 0; 11장 집필 진행 중)", "(전체 조립 완료·자동 검사 전부 통과; 일관성 검토 파견 단계)")
io.open(P, "w", encoding="utf-8", newline="\n").write(s)
print("patched 작업_장부.md")
