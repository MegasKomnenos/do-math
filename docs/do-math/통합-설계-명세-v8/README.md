# v8 규범 명세 묶음

이 묶음은 통합-설계-초안.md의 구현 전 명세다. 설치된 실행기나 검증된 어댑터를 뜻하지 않는다.
기계 형식은 schemas가, 행동의 의미와 원자성은 설계 본문의 소유 절이 정한다.
build_spec.py는 이 묶음의 선언에서 스키마·레지스트리·계약·템플릿과 초안 §16.4의 지정 표를 생성하고, 초안의 벡터 대응을 고정한다.
verify_spec.py는 스키마·codec·명세 검사와 합성 반례를 실행한다. 실제 모델·OS·Lean 시험은 수행하지 않는다.

실행 명령:

    python build_spec.py
    python verify_spec.py

위 명령은 이 디렉터리 기준이며 저장소 루트에서는 파일의 전체 상대 경로를 사용한다.

| 파일 | 소유 내용 |
|---|---|
| schemas/ | JSON Schema Draft 2020-12의 닫힌 자료 형식 |
| schema-registry.json | 생성한 스키마 ID·저장 위치·소유 절·해시 |
| command-contracts.json | 명령별 호출자·선행조건·효과·오류·재시도 |
| role-contracts.json | 활동·단계·AI/기계별 필수 입력·출력 가족·권한·미완료 반환 |
| relation-templates.json | 인스턴스에 자동 활성화되지 않는 표준 관계 저작 템플릿 |
| toolchain-lock.json | 실제 명세 검증에 사용한 Python·파서·스키마 검사기 판본 |
| semantic-rules.json | 스키마만으로 판정할 수 없는 관계적·의미적 의무 |
| transitions.json | 허용 전이와 추가 전제 규칙 |
| source-vector-map.json | 초안의 V 벡터 200개·Q 계약 21개 원문 대응. 실제 실행 상태는 별도 |
| fixtures/ | 합성 입력과 독립 반례 |
| validation-report.json | 실제 수행한 명세 검사의 범위·결과 |
| review/ | 각 검토가 고정한 판본의 독립 적대 검토와 작성자 판단. 이전 판본의 통과를 현행 통과로 승계하지 않음 |

스키마 URI의 do-math.invalid는 오프라인 식별자다. 네트워크로 해석하지 않는다.
예제 참조·영수증은 합성 자료다. 스키마 통과를 실제 대상 실재·권한·종료·수학 판정의 증거로 사용하지 않는다.

| 가족 | 계약 ID | 소유 절 | 저장 위치 |
|---|---|---|---|
| action-result | do-math-draft/action-result/8 | 3.2.1,10.3,13.2,16.3,19.7 | runtime/actions/results/{id}.json |
| activity | do-math-draft/activity/8 | 3.2.1,19.5 | runtime/activities/{id}/record.json |
| activity-result | do-math-draft/activity-result/8 | 3.2.1,5.4,9.2.1,13.1,19.5 | runtime/artifacts/{bundle_id}/{path} |
| artifact | do-math-draft/artifact/8 | 6.5,7.1,19.2 | runtime/artifacts/{id}/manifest.json |
| assessment | do-math-draft/assessment/8 | 5.4,9.4,11,19.6 | research/formal/assessments/{id}.json |
| assessment-use | do-math-draft/assessment-use/8 | 11.8,19.6 | research/formal/uses/{id}.json |
| budget | do-math-draft/budget/8 | 4,19.4 | research/governance/budgets/{id}.json |
| command-request | do-math-draft/command-request/8 | 16.3,19.7 | transport |
| command-response | do-math-draft/command-response/8 | 16.3,19.7 | transport |
| common | do-math-draft/common/8 | 19.2 | schema_only |
| conversation-state | do-math-draft/conversation-state/8 | 3.3,19.4 | runtime/conversations/{id}.json |
| decision | do-math-draft/decision/8 | 13.1,19.3 | research/governance/decisions/{id}.json |
| execution | do-math-draft/execution/8 | 6,12,19.4 | runtime/executions/{id}/record.json |
| execution-profile | do-math-draft/execution-profile/8 | 6.1,6.4.1,12.1,16.1,16.2,19.4 | research/governance/profiles/{id}.json |
| explanation | do-math-draft/explanation/8 | 11.1,19.6 | research/formal/explanations/{id}.json |
| external-action | do-math-draft/external-action/8 | 13.3,19.4 | runtime/actions/{id}.json |
| formal-result | do-math-draft/formal-result/8 | 1.2,11.1,11.6,15,19.6 | research/formal/results/{id}.json |
| governance | do-math-draft/governance/8 | 1.4,13.1,13.2,19.3 | research/governance/{id}.json |
| implementation-manifest | do-math-draft/implementation-manifest/8 | 14.5,16.5,19.1 | installed/implementation-manifest.json |
| input-manifest | do-math-draft/input-manifest/8 | 8,13.1,16.5,19.5 | runtime/artifacts/{bundle_id}/input-manifest.json |
| instance | do-math-draft/instance/8 | 1.4,14.1,19.2 | research/instance.json |
| integration | do-math-draft/integration/8 | 10,19.6 | research/integrations/{id}.json |
| issue-state | do-math-draft/issue-state/8 | 8.3,11.3,11.4,19.6 | runtime/activities/{activity_id}/issues/{id}.json |
| kind-definition | do-math-draft/kind-definition/8 | 7.3,19.3 | research/knowledge/{path}.md#frontmatter |
| knowledge | do-math-draft/knowledge/8 | 7.3,19.3 | research/knowledge/{path}.md#frontmatter |
| machine-check | do-math-draft/machine-check/8 | 16.3,19.8 | runtime/artifacts/{bundle_id}/checks/{path}.json |
| migration | do-math-draft/migration/8 | 14.5,19.8 | research/integrations/migrations/{id}.json |
| operational-review | do-math-draft/operational-review/8 | 12,19.4 | runtime/activities/{activity_id}/reviews/{id}.json |
| plan | do-math-draft/plan/8 | 9,19.5 | runtime/artifacts/{bundle_id}/plan.json |
| proposal | do-math-draft/proposal/8 | 11.1,11.4,19.6 | runtime/artifacts/{bundle_id}/proposal.json |
| provider-operation | do-math-draft/provider-operation/8 | 4.2,6.1,13.3,19.4 | runtime/provider-operations/{id}/record.json |
| resource-reservation | do-math-draft/resource-reservation/8 | 4.2,4.5,19.4 | runtime/reservations/{id}.json |
| review-plan | do-math-draft/review-plan/8 | 11.3,19.6 | runtime/artifacts/{bundle_id}/review-plan.json |
| review-policy | do-math-draft/review-policy/8 | 11.3,19.6 | research/governance/review-policies/{id}.json |
| review-result | do-math-draft/review-result/8 | 11.3,11.4,11.4.1,19.6 | runtime/artifacts/{bundle_id}/review-result.json |
| runtime | do-math-draft/runtime/8 | 3.1,9.1,13.5,14.2,19.2 | runtime/state.json |
| runtime-event | do-math-draft/runtime-event/8 | 3.2.1,9.1,12.1.1,13.1.1,19.4 | runtime/events/{id}.json |
| status | do-math-draft/status/8 | 9.4,16.6,19.8 | derived/status.json |
| task | do-math-draft/task/8 | 5,9.4,19.5 | runtime/tasks/{id}/record.json |
| trust-environment | do-math-draft/trust-environment/8 | 15,19.6 | research/trust/{id}.json |
