# 현행 개발 계획 — manager 0011 · 완료

사용자가 얻을 결과는 do-math의 역할·검사·운영 질문 연결을 실제 수학 연구에 사용할 수 있게 수리하고 정상 처리와 예외 재량을 같은 현행 계약으로 제공하는 것이다. 요구 R1~R7은 context.md 2절, 실제 인터페이스는 seams.md의 수용판 정의를 따른다. context 17절과 seams 17절이 최종 상태다.

## 수용 결과

| task | 최종 결과와 해석 |
|---|---|
| role-flow-design | 역할 모집단·생산/소비 설계 수용. 실제 정의는 후속 수용 구현을 따른다 |
| shared-validation-hashes | partial 수용 이력 유지. 공통 입력/해시/오류 복구와 당시 시험 잔여는 후속 역할·통합 수리에서 해소 |
| batch-payload-reads | 정확 snapshot 복원과 검사 보존, 실제 Git cold 260→23회 한 쌍 수용. 일반 성능 보장 아님 |
| windows-patch-guidance | common Windows/패치 안내와 실제 지급·무해 호출 근거 수용. 미래 준수 미확인 |
| codex-refresh-diagnostics | 원 stderr 바이트 진단·기존 artifact 보존·완료/실패 구별 수용. 외부 원인 미확정 |
| role-question-flow | 전체 역할 책임·개정 예외 재량·QU 실제 배정/근거 처분/후속·저장/미러 수용 |
| intent-check-evidence | 같은 원문/import 묶음의 근거 대기→새 독립 검사·봉인/이력/계보 수용 |
| integration-repair-check | catalog 투영·필수 부모 정산·schema/문서 소비·fixture 수리와 필요한 통합 확인 수용. 관측한 비통과 잔여 없음 |
| final-goal-review | 전체 R1~R7 독립 대조 수용. 학술 지급 문서 F1만 후속 수리로 남겼음 |
| academic-contract-guidance | 네 정본/미러 문서의 unresolved 보존·필드별 보충·사용자 원 계약 요청 처리 정합화 및 실제 지급 근거 수용 |
| final-contract-review | F1 해소·실제 지급·이전 전체 리뷰 결론 유지·사용자 목표 충족 독립 판단을 변경 없음으로 통합·수용 |

## 완료 판단과 남은 범위

최종 리뷰와 manager의 공용 소스 대조에 따라 사용자 개발 목표는 확인 범위에서 충족한다. 최종 review는 모든 work를 직접 또는 간접 선행으로 포함한다. inbox의 실행 중 task는 없고 state의 11개 task도 모두 exited다. 최종 review를 accepted에 추가하면 모든 배정이 수용되며 미해결 필수 수리나 독립 후속 기능이 없다. 기존 task 정의를 유지하고 새 배정 없이 complete로 게시한다.

manager가 check.py report PASS와 integrate files=[]/changes={}를 확인했다. 현재 공용 baseline 3,420파일, 이전 전체 리뷰 이후 문서 8개 변화, 정본/미러 네 쌍, 저장 코드 발췌 15개의 SHA/전문, 저장 프롬프트 네 개와 지급 문서 전문이 리뷰 판본/근거와 일치한다. 문서와 실제 core/planning/question 분기를 정적으로 대조했다. CLI는 해당 두 역할의 직접 지급 목록 밖이다. 같은 제품 시험·생성기·프롬프트 생성·live 호출을 반복하지 않았다.

여러 판본의 최신 관측 4,618 passed/1 skipped를 최종 판본 전체 회귀 성공으로 해석하지 않는다. 최종 전체 회귀/T3 full/T5·새 live 모델/scholarly/실제 Lean/설치 복구 AI·미래 역할 준수/수학 연구 효능은 미확인이다. Windows symlink 권한 skip의 OS 동작, Codex 외부 timeout 원인·요청 시간은 미확인/미확정이며 Git 성능은 기존 한 쌍의 범위다. 이 한계 자체로 새 blocker를 만들지 않는다. 원 연구는 계속 정지 상태이며 연구 재개는 이번 개발 완료에 포함하지 않는다.

## 영구 근거와 게시

최종 판단은 tasks/final-contract-review/{report.json,assessment.md,integration.json,evidence/}, 전체 대조는 tasks/final-goal-review/{assessment.md,evidence/}, manager 직접 확인은 managers/0011/{decision.md,verification-summary.json,verify_result.py}에 남는다. 수리의 실제 지급 근거는 tasks/academic-contract-guidance/evidence/다. 정리된 판본은 workspaces.py restore baseline/result로 복원하고 삭제될 workspace를 영구 입력으로 삼지 않는다.

공용 context/plan/seams를 먼저 갱신한 뒤 final-contract-review 수용과 complete 사유를 담은 managers/0011/queue.pending.json을 검사한다. 검사한 같은 파일을 queue.json으로 원자 교체하는 것이 이번 manager의 마지막 공용 변경이다. workspace 정리는 실행기가 manager 종료 뒤 수행한다. 원 연구·감사·HOLD·예약·graphify·state.json은 수정하거나 재개하지 않는다.
