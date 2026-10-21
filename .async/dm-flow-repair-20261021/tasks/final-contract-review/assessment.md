# 최종 계약·사용자 목표 대조

**F1은 해소됐다. 이전 전체 리뷰의 R1~R7 판단과 한계를 이 수정판에 이어 적용할 수 있으며, 이번 개발의 사용자 목표는 확인한 범위에서 충족한다. 추가 필수 제품 수리 없이 manager가 최종 수용·완료를 판단할 것을 권고한다.** 실제 수학 연구의 성공이나 미래 모델의 계약 준수를 확인했다는 뜻은 아니다.

리뷰 배정은 완료했다. 제품 순변경은 없으며 `report.json`의 `status=complete`는 리뷰 수행 완료다. 프로젝트 완료 게시와 실행 중·미해결 task의 최종 확인은 manager가 맡는다.

## 판단 기준과 직접 확인한 범위

서비스 `C:/math/services/async-development/protocol.md`의 review·보고 절차, 자기 task의 `inputs/context.md`, `plan.md`, `seams.md`, `task.json`, `objective.md`, `RECORDS/user-messages.md`의 최신 정정과 제품 `AGENTS.md`를 읽었다. 제품 이음새 정본의 공유 원칙과 시험 지침의 최소 실행·판본·결과 해석을 적용했다. R4는 사전·적용 검사의 같은 판단을 한 구현으로 공유하는 현재 요구로 판단했다.

아래 `D/`는 자기 workspace의 `.claude/skills/do-math/`, `M/`는 그 `scripts/do_math/`, `R/`는 `C:/math/.async/dm-flow-repair-20261021/`다. 공식 미러는 `.agents/skills/do-math/`다. 이전 전체 리뷰는 `R/tasks/final-goal-review/{assessment.md,report.json,evidence/}`, 새 수리는 `R/tasks/academic-contract-guidance/{report.json,integration.json,evidence/}`를 읽었다. manager 0009·0010의 decision/verification-summary도 읽되 그 수용 판단을 이번 독립 결론의 대용으로 삼지 않았다.

직접 확인은 다음 범위다.

- 네 정본 문서의 수정 절·인접 계약과 실제 코드의 분기를 정적으로 대조했다. 보존된 diff의 변경 범위도 읽었다. 대응 미러 네 쌍의 bytes가 정본과 같음을 직접 확인했다.
- 자기 `evidence/verify_review.py`를 `python -B`로 실행해 이전 전체 리뷰의 baseline과 이번 baseline 차이가 정확히 문서 8개이고 `academic-contract-guidance/integration.json`의 시작·결과 SHA와 일치함을 확인했다. 현재 baseline 3,420파일의 bytes도 모두 일치한다. 코드·schema·시험·공통 지급표·검사기·저장 정의에 추가 변화가 없다.
- 수리 task가 저장한 코드 발췌 15개의 파일 SHA와 정확한 행 내용을 현재 코드에 대조했다. 저장된 정본/미러 각 두 역할의 프롬프트 네 개는 SHA·길이가 맞고, 각 8개 지급 문서의 전문·SHA·길이가 현재 사본과 같다.
- 이전 리뷰가 읽은 공식 실행 보고 4개의 SHA가 그대로이며, 마지막 `final-fixtures/report.json`의 Python 930개 SHA가 현재 코드와 모두 같다. 기존 실행 결과를 새로 실행한 결과로 표현하지 않는다.

정확한 변경 경로·SHA, 지급 프롬프트 SHA와 비교 결과는 자기 `evidence/review-comparison.json`에 있다. 충분한 저장 지급 근거가 있어 프롬프트 생성·공식 미러 생성기·제품 시험·벤치마크·live 호출은 반복하지 않았다. 서비스의 최종 `check.py report` 결과는 `evidence/report-check.json`에 남긴다.

## F1 해소: 세 분기와 정상 후속이 같은 계약이다

| 경우 | 현재 원문과 실제 정의의 대조 | 판단 |
|---|---|---|
| 필수 판단 자료 부족 `unresolved` | `D/계약/후보-준비.md:216`, `D/계약/작업-계약-검토.md:151`은 기존 평가·관찰 규칙 보존, 실제 질문 담당과 `contract_review_input`, 이 판정 자체로 개정·보충 미생성을 설명한다. `M/core_engine.py:3434`의 `_apply`는 미해결 item의 route를 실제 QU scope에 연결하고 읽은 receipt basis·계약 SHA·검토 basis를 저장한다. 이 분기에는 평가·규칙 삭제나 새 revision_requested 생성이 없다. | 일괄 재준비·현행 분리라는 옛 지시는 제거됐다. 자료 부족과 AI 저작 결함을 구별한다. |
| 같은 계약의 새 근거 | 두 계약과 CLI는 관련 고정 질문 scope 전부 해소와 읽지 않은 영수증, 또는 실제 review basis 변화 뒤 새 독립 검토를 설명한다. `M/question_engine.py:267`의 `_resume_contract_review_waits`는 같은 계약 SHA, scope별 해소/basis, 기존 검토 실행 종료를 확인한다. | 이미 읽은 영수증이나 QU 전체 상태만으로 반복하는 설명이 아니다. 질문 close가 승인이라는 지시도 없다. |
| 실제 `revision_required`, contract 미포함 | `D/계약/후보-준비.md:217`, 검토 계약 153행과 예산·CLI 요약은 지적된 필드만 history로 옮기고 나머지는 유지한다고 설명한다. `M/planning_engine.py:106`의 `_ensure_model_assessments`는 현재 요청·현재 계약의 최신 수정 필요 검토에서 item별 revision_fields를 모은다. 136~144행은 평가와 관찰 규칙 각각을 지적된 경우에만 분리하며 판본·해시·원 검토 실행 참조를 보존한다. 후속 missing/missing_rules가 실제 부족한 항목을 배정한다. | 평가만, 규칙만, 둘 모두의 실제 결함을 구별하며 두 항목 일괄 재준비를 요구하지 않는다. 기존 미평가·규칙 누락/무효의 일반 보충도 설명한다. |
| revision_fields에 contract 포함 | 후보 준비 218행과 다른 세 문서는 필드 분리 대신 사용자 원 계약을 보존하는 일반 개정 요청 처리로 보낸다. `_ensure_model_assessments` 121~129행은 contract를 먼저 처리하고 continue한다. contract와 다른 필드가 함께 있어도 이 우선 분기다. | 사용자 계약을 후보 준비가 다시 저작하라는 지시가 없다. 실제 사용자 결정 경로와 AI 요청 처분의 권한이 구별된다. |
| 보충·예외 처분 뒤 독립 판단 | 후보 준비 210·241~249행은 지정된 산출의 보충과 보류, 새 독립 검토를 유지한다. `_finish_assessment_preparation`은 배정 판본의 준비를 반영하고 필요한 평가·규칙이 갖춰진 뒤 새 task_contract_review를 요청한다. `revisions.submission_errors` 148~153행과 resolved_targets는 근거 있는 AI 요청 dismissal만 허용하고 사용자 revise 출처는 보존한다. revision_engine의 기존 후속 정의는 이번에 바뀌지 않았다. | 정상 개정을 유지하고 예외의 기각·자료/사용자 결정 대기를 허용한다. 무수정 처분은 독립 승인·사용자 의무 면제·연구 완료가 아니다. |

후보 준비의 「기존 과제의 평가와 관찰 규칙을 보충하는 실행」을 상세 정본으로 유지했고, `D/references/모델과-실행예산.md:68`, `D/references/CLI-실행-계약.md:145` 및 검토 계약의 요약은 그 절을 가리킨다. 새로운 보편 증명·승인 관문이나 모든 요청의 재심사 의무를 추가한 것으로 보이지 않는다. 검토 계약 147~149행의 지적 전 자기 오독·반대 근거 확인 및 수행자의 미래 도구 성공을 사전 입증 의무로 만들지 않는 책임 경계도 유지된다.

CLI의 인접 `contract_revision`·`contract_review_input` 표(137~138행)도 실제 개정 요청 처리와 자료 대기를 구별한다. 147행의 `status.tasks[].waits/next_owner`, `selected_actions`와 `active_execution_ids`는 `M/reporting.py:52`의 `task_status` 55~58·100~110행의 실제 투영과 맞는다. 사람 출력의 queued/active_records와 질문 조회의 handling/resolution_history 연결은 수리 task의 정적 근거 및 현재 동일 코드에서 확인했다. 요청 ID·실행 ID·질문 해소·계약 승인·과제 완료가 뒤섞이지 않는다.

## 실제 지급과 판본의 연결

`M/contracts.py:reading_map`은 SKILL의 common+역할 대응표를 소비하고 `_document/prompt_documents`(332~342행)는 파일 전문과 SHA를 읽는다. `render_prompt`는 이 내용을 프롬프트에 넣는다. 해당 코드와 `D/SKILL.md`의 지급표는 이전 전체 리뷰 이후 바뀌지 않았다.

`academic-contract-guidance/evidence/verify_delivery.py`의 실제 호출 방법을 읽고 `delivery-{claude,agents}.json` 및 보존된 `prompt-*.txt`를 현재 파일에 독립 대조했다. 네 조합 모두 각 8개 문서의 정확한 전문이 보존 프롬프트에 있다. 후보 준비에는 수정된 후보 준비 계약과 예산 문서가, 계약 검토에는 수정된 검토 계약과 예산 문서가 실제 지급됐다. 문서가 표에 선언됐다는 사실만을 근거로 한 결론이 아니다.

CLI 문서는 두 역할의 직접 reading_map 밖이다. CLI에 대한 결론은 수정 문구·실제 상태 투영의 정적 대조와 미러 bytes 일치이며 해당 두 프롬프트에 CLI 전문이 지급됐다고 주장하지 않는다.

공식 미러 생성기의 1,394파일 drift 없음은 수리 task와 이전 전체 리뷰의 실행 근거다. 이번에는 이전 리뷰 판본 이후 다른 파일 변화가 없고 변경 문서 네 쌍이 정확히 같음을 확인했다. 미러 일치만으로 문서 의미의 정확성을 대신하지 않았다.

## 이전 전체 R1~R7 판단의 유지와 사용자 목표

이 절의 전체 역할·런타임·원자료 검증은 `final-goal-review/assessment.md`와 영구 evidence의 기존 판단을 이어 적용한다. 이번 직접 확인은 문서 의미·지급·판본 차이에 집중했으며 전체 역할 모집단이나 런타임을 다시 감사한 것이 아니다. 이전 리뷰와 달라진 정확한 8파일은 모두 F1 설명 수리이고, 관련 코드와 나머지 계약은 그대로다.

| 요구 | 이 수정판의 결론과 기존 근거의 연결 |
|---|---|
| R1 역할 전체와 인계 | 이전 리뷰의 내부 AI 열 역할·동적 단계·기계 action·독립 운영/설치 복구 모집단과 실제 지급/출력 소비 판단을 유지한다. 남았던 학술 지급 설명 F1은 위 세 분기와 실제 지급 대조로 해소됐다. 역할 책임과 현재 구현이 같은 계약을 설명한다. |
| R2 정상 처리·예외 재량 | 기존 revisions와 부모/자기/실패 정산, 필수 부모 consumer_targets, 독립 재검토·반복 충돌 대기 판단은 유지된다. 새 문서도 정상 개정과 근거 있는 AI 요청 기각·대기 및 실제 사용자 권위를 보존한다. |
| R3 운영 질문과 실제 후속 | 기존 QU 의무/원 보고→실제 action/execution→봉인 근거 처분→대기/이관/계약·계획 후속, 의도 검사의 같은 import 새 독립 check·history·계보 판단은 유지된다. 새 unresolved 설명도 이 실제 질문 경로를 따른다. pause/HOLD 해제나 승인·완료를 질문 close에 부여하지 않는다. |
| R4 공통 검사 | inspect_bundles와 공통 입력 구성, 고정/live 선언 누락 정본 및 위치별 권한·효력·현재성·CAS 추가 검사에 대한 기존 판단을 유지한다. 클래스 계층이나 새 검사 장치를 완료 조건으로 만들지 않는다. |
| R5 해시·실패 의미 | content_sha256 공급, previous_hashes 오류와 실제 CurrentnessChanged 구별, 출력 수리/refresh/엔진 대기의 기존 판단 및 원바이트 공통 검사 대조 범위를 유지한다. 과거 응답 전체를 현행 schema로 적용한 성공으로 확대하지 않는다. |
| R6 Windows 안내 | common 지급의 실제 Windows 예시와 무해 호출·정본/미러 20프롬프트 근거는 바뀌지 않았다. 미래 모델 준수는 미확인이다. |
| R7 세 추가 문제 | 패치 한 파일 한 Update/여러 hunk와 거부 뒤 재독, Codex 원 stderr 진단·기존 result artifact 보존 및 성공/실패 구별, exact snapshot Git batch 복원/검사 보존에 관한 이전 판단을 유지한다. 새 CLI 수정은 진단 절이나 결과 artifact 소유자를 바꾸지 않았다. |

사용자가 요청한 것은 특정 보류 하나의 제거를 넘어 역할·검사·운영 질문과 후속을 실제 연구에 사용할 수 있게 수리하는 것이다. 이전 전체 리뷰가 확인한 구현과 이번 F1 해소를 합하면 그 개발 결과를 수용할 근거가 갖춰졌다. 확인한 범위에서 결과 사용을 막는 추가 결함이나 별도 필수 기능의 필요는 찾지 못했다. 추가 선택 개선이나 미확정 외부 원인을 새 blocker로 만들 이유도 확인되지 않았다. **개발 목표 완료 판단을 권고하며 원 연구의 재개·수학 결과의 성공은 별도의 실제 운전과 판단으로 남긴다.**

## 유지하는 한계

- 기존 여러 판본의 최신 관측 4,618 passed/1 skipped는 최종 판본의 전체 회귀 성공이 아니다. 공식 실행은 전체 T2+flows 4,610개 뒤 수리/영향 179개, 실제 경계/잔여 32개, 마지막 fixture 2개의 서로 다른 판본이다. 마지막 Python 930개 SHA 일치는 판본 연결이며 모든 시험을 그 마지막 판본에서 실행했다는 뜻이 아니다.
- 최종 전체 회귀·T3 full/T5, 새 live 모델/scholarly/실제 Lean·설치 복구 AI, 미래 역할 준수와 수학 연구 효능은 미확인이다. Windows symlink 1개는 생성 권한 부족 skip이며 해당 OS 동작도 미확인이다.
- Codex 목록 timeout의 네트워크/공급자 내부 원인·실제 요청 기한/소요는 미확정이다. 전체 실행 467.066195초를 목록 요청 시간으로 해석하지 않는다. 이전 재생은 과거 종료 장벽의 대역이며 새 OS 종료 관측이 아니다.
- Git cold 260→23회와 31.261→3.677초, warm 양쪽 0회 및 snapshot 765파일/4,399,529 bytes 동일은 기존 한 쌍의 기록이다. 캐시·호스트 부하 미통제이며 일반 성능 보장이 아니다. 이번에 벤치마크나 원자료 provenance 검사를 반복하지 않았다.

보고·assessment·근거만 자기 task 디렉터리에 작성했다. canonical source_repo·다른 task·서비스 state/queue·원 연구/감사/HOLD/예약은 수정하거나 재개하지 않았고 graphify도 갱신하지 않았다.
