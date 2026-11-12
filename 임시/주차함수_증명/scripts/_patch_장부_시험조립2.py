# -*- coding: utf-8 -*-
"""작업 장부: 둘째 시험 조립(검사기 좁힘 뒤)의 남은 실패와 장별 재개 때 포함할 세션 지적을 적는다."""
import io
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = os.path.join(ROOT, "작업_장부.md")
s = io.open(P, encoding="utf-8").read()

ENTRY = (
    "- 2026-11-12 23:2x 둘째 시험 조립(9장 수정본·검사기 좁힘 뒤): 라벨 427 해소, 부록 D 45, [todo] 0; 불변식 실패 9(라벨 중복 5:weight-envelope와 그 귀결 번호 중복, 부록 B 부재, 나머지 아래). **재개 때 포함할 세션 지적**(2차 대조 보고서와 함께 집필자에게 보냄): "
    "6장 — `{{6:small-k-bulk}}` 머리 「계산 증거(정리 5.1의 인증 자료)와 계산 보조(…)」를 「비형식 증명, 계산 보조(배정밀도 평가, 인증 아님), 정리 5.1·명제 `{{5:witness-position-bound}}`에 의존」 꼴로; `{{6:prop-W}}` 머리 「(라)는 정리 6.49의 기저 계산에 의존하는 비형식 증명」→「(라)는 비형식 증명, 계산 보조(정확 정수·유리수), 정리 `{{6:theorem-D}}`에 의존」; 어느 머리의 「고정밀 평가, 인증 아님」은 기록의 실제 자릿수로(「<정밀도> 평가」). "
    "7A — 7.2 열 인증 보증 문단 둘의 「검토가 고친 두 자리」·「검토가 찾아 고친 결함과 재인증」(정정 이력; 지침 4.6) 삭제·정정값만; `{{7:fourier-lemmas}}` 머리 「(바)는 비형식 증명(Faà di Bruno 공식의 문헌 인용)」→ Faà di Bruno는 교과서 표준(결정 38)이라 「증명됨」, 괄호 설명 제거. "
    "7B — 산술 등급 이름 넷만: `{{7:…}}` 7.4 세 머리의 「binary64 바깥 부풀림 구간 산술; 정확 유리수」→「binary64 사전 오차 해석·정확 정수·유리수」(쉼표/가운뎃점으로 나열, 괄호 안 쌍반점 금지), 「정확 유리수」×2→「정확 정수·유리수」, 「binary64 사전 오차 해석; 정확 유리수」→「binary64 사전 오차 해석, 정확 정수·유리수」. "
    "5B — `{{5:weight-envelope}}`(5.5의 [r8a9b11e] 보조정리 U2)를 5A의 등록 라벨과 겹치지 않는 새 라벨(예 `{{5:mass-envelope-U2}}`)로 바꾸고 부록 D의 대응 항목 참조도 함께(`{{D:weight-envelope-U2}}`는 그대로 둬도 됨). "
    "세션이 직접 할 것: 10.7 넷째·다섯째·여섯째 고리의 절 참조를 `{{7:qstar-columns}}`·`{{7:qstar-implies-wlflat}}`·`{{7:flat-threshold}}`(라)로 치환(#19)."
)
old = "\n## 재개 기록\n"
assert s.count(old) == 1
if "둘째 시험 조립(9장 수정본" not in s:
    s = s.replace(old, "\n" + ENTRY + "\n" + old)
io.open(P, "w", encoding="utf-8", newline="\n").write(s)
print("patched 작업_장부.md (둘째 시험 조립)")
