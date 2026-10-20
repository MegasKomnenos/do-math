# test_relation_dependencies

| 항목 | 값 |
|---|---|
| 조각 | `foundation` |
| 원문 | `.claude/skills/do-math/scripts/tests/test_relation_dependencies.py` (94행) |
| 클래스 / 테스트 | 2 / 5 |
| 시험 대상 제품 코드 | `do_math/planning.py`의 `task_ready`, `revision_waits`; `do_math/revisions.py`의 `capture_targets`; `do_math/questions.py`의 `link`, `user_waits`; `do_math/knowledge.py`의 `plan_impact`; `do_math/submission.py`의 `reported_references`; `do_math/task_scope.py`의 `assessment_basis`; 간접으로 `do_math/relation_refs.py`의 `relation_references`, `relation_evidence_references` |
| 사용하는 픽스처 모듈 | `engine_fixtures`(`start_query_repository`), `record_fixtures`(`approved_task`, `approve_task`, 함수 안에서 import하는 `specialist_assessment`, `completed_with_knowledge`). `specialist_assessment`는 다시 `knowledge_fixtures.verified_knowledge`를 부른다 |
| 격리 표지 | 없음 |
| 시작 상태 | `RelationReadTests`는 실제 Git 저장소에 공개 `initialize`로 만든 조회 저장소에서 기록 가족을 읽어 온 뒤, 사전 상태에 순수 함수를 부른다. `RelationEvidenceTests`는 1단(사전 기록에 순수 함수 직접 호출) |

## 목적

모듈 docstring은 "관계(relation)가 같은 의존을 일정 계획(scheduling), 판정(judgments), 제출(submission)에 똑같이 드러낸다"는 계약을 밝힌다. 관계 기록은 두 지식 기록(`source`, `target`)을 잇고, 선택적으로 증거 참조(`evidence_refs`, `formal_result_refs`, `assessment_refs`)를 단다. 제품은 관계의 현재 간선을 `relation_refs.relation_references`(끝점과 증거 참조의 합집합) 한 곳에서 읽고, 이력(`history`)과 산문(`evidence`)은 간선으로 만들지 않는다(`relation_refs.py` 14–15행 주석). 이 모듈은 그 한 정의가 네 소비자에서 같게 작동하는지 본다.

- 일정 계획: 과제가 관계를 입력으로 읽으면, 관계의 끝점을 고치는 작업과 그 과제의 작업이 서로 기다린다(`planning.revision_waits`). 끝점에 걸린 차단 질문도 그 과제를 막는다(`questions.user_waits`).
- 영향 분석: `knowledge.plan_impact`는 관계의 증거 파일 위치자(`workspace:...`)를 기록 의존으로 바꾸지 않는다.
- 제출: `submission.reported_references`는 출력과 확장의 관계 행에서 명시 참조만 모은다.
- 판정: `task_scope.assessment_basis`는 관계가 인용한 형식 결과·평가 사용의 현재 효력을 판정 근거의 해시에 포함하고, 끝점 지식 기록은 제출된 내용만 묶는다.

## 모듈 수준 요소

- 행 6: 스킬의 `scripts/` 폴더를 `sys.path` 앞에 넣는 공통 머리. 직접 실행이나 `unittest discover`에서도 `do_math`와 픽스처 모듈을 import할 수 있게 한다.
- 행 93–94: 직접 실행하면 `unittest.main()`으로 이 모듈의 시험을 돈다.

## RelationReadTests (행 12–40)

`unittest.TestCase`를 그대로 상속한다. 클래스 표지, 클래스 속성, 설정 훅, 도우미 메서드가 없다.

### `test_indirect_endpoints_obey_both_revision_directions_and_question_gates` (행 13–40)
- 성질: 과제가 관계 하나를 입력으로 읽으면 그 관계의 두 끝점 지식 기록이 과제의 간접 읽기 대상이 되어, 끝점을 개정하려는 작업과 과제의 작업이 양방향으로 서로 기다리고, 끝점에 걸린 차단 질문은 과제를 막으며, 무관한 대상의 차단 질문은 막지 않는다.
- 준비: `engine_fixtures.start_query_repository(self)`로 실제 Git 저장소에 공개 `initialize`로 인스턴스를 만들고 지식 두 개(`self.kids`: 정의 "One", 정리 "Two")와 관계 하나(`self.relation_id`, One이 Two를 지지)를 저장한 판(`self.old_head`)을 얻는다. 이 판을 `self.repository.load`로 읽어 `knowledge`, `formal_results`, `expositions`, `identity_assessments`, `assessment_uses`, `kind_definitions`, `relations` 일곱 가족을 `record_fixtures.approved_task()`의 인스턴스에 깊은 사본으로 옮긴다. 과제 `TK-1`의 `inputs`에 관계 ID를 더한 뒤 `approve_task`로 계약 검토를 바뀐 과제에 대해 다시 봉인한다.
- 실행: 먼저 `planning.task_ready`로 과제 상태를 본다. 그다음 두 끝점마다 `subTest(endpoint=...)` 안에서 세 판정을 한다.
  1. 개정 작업(writer) `AC-writer`(`research_preparation`, `revision_targets=revisions.capture_targets(instance, runtime, [endpoint])`)를, 과제를 읽는 작업(reader) `AC-reader`(`research_work`, `target=TK-1`)가 실행 `EX-reader`로 `running`인 상태에서 `planning.revision_waits(writer, ...)`로 판정한다.
  2. 실행을 비우고 writer를 `queue`에 넣은 뒤 `planning.revision_waits(reader, ...)`로 판정한다.
  3. 큐와 `question_links`를 비우고 `questions.link(..., owner='user', targets=[endpoint], blocks=True)`로 차단 질문을 건 뒤 `questions.user_waits(reader, ...)`로 판정한다.
  끝으로 질문 연결을 비우고 무관한 대상 `KN-unrelated`에 차단 질문을 건 뒤 `user_waits(reader, ...)`를 부른다.
- 단언: `task_ready(...)['state']`가 `'ready'`다. 끝점마다 (1) writer의 대기 목록이 참(비어 있지 않음), (2) reader의 대기 목록이 참, (3) `user_waits`의 첫 행 `question_id`가 방금 만든 질문의 `id`다. 마지막 무관 질문에서는 `user_waits`가 빈 목록이다. 대기 사유의 `kind`나 `record_ids`는 단언하지 않고 목록이 비었는지만 본다.
- 대역: 없음. Git과 공개 초기화는 실제이고, 판정은 제품 함수를 직접 부른다.
- 비고: `subTest` 케이스는 `self.kids`의 두 끝점. 실제 외부 자원으로 Git 자식 프로세스(`git_store`의 `subprocess.run`)를 쓴다. 이름의 "both revision directions"는 (1) 읽는 쪽이 실행 중일 때 개정자가 기다림과 (2) 개정자가 대기 중일 때 새 읽는 쪽이 기다림, 곧 `revision_waits` docstring의 "Declared writers wait for existing readers ...; new dependent readers wait"의 두 방향을 가리킨다.

## RelationEvidenceTests (행 43–90)

`unittest.TestCase`를 그대로 상속한다. 클래스 표지, 속성, 설정 훅, 도우미 메서드가 없다. 네 시험 모두 사전 기록을 만들어 제품 함수를 직접 부르는 1단이다.

### `test_impact_analysis_does_not_turn_evidence_file_locators_into_record_dependencies` (행 44–50)
- 성질: 관계의 `evidence_refs`에 있는 작업 공간 파일 위치자(`workspace:proof.md`)는 영향 분석에서 미해결 기록 참조로 취급되지 않는다.
- 준비: 지식 `KN-a` 하나와, `KN-a`를 자기 자신에 잇고 `evidence_refs=['workspace:proof.md']`를 단 관계 `RL-a`를 가진 최소 인스턴스.
- 실행: `knowledge.plan_impact(instance, {}, ['KN-a'], ['RL-a'])`(함수 안에서 import).
- 단언: 계획의 `unresolved_refs`가 `[]`이고 `requires_independent_review`가 거짓이다.
- 대역: 없음.

### `test_output_and_extension_relations_report_every_explicit_reference` (행 52–58)
- 성질: 제출 출력의 `relations`든 확장의 `relations`든, 관계 행에서 보고되는 참조는 끝점과 세 증거 참조 필드뿐이고 이력과 산문은 빠진다.
- 준비: 끝점 `KN-source`·`KN-target`, `evidence_refs=['SO-evidence']`, `formal_result_refs=['FR-proof']`, `assessment_refs=['IA-proof']`, 이력 `history=[{'source': 'KN-history'}]`, 산문 `evidence='KN-prose'`를 가진 관계 하나. 기대 집합은 앞의 다섯 ID다.
- 실행: 관계를 출력 쪽에 둔 경우(`({'relations': [relation]}, {})`)와 확장 쪽에 둔 경우(`({}, {'relations': [relation]})`) 각각 `submission.reported_references(output, extensions)`.
- 단언: 두 경우 모두 반환 목록의 집합이 기대 집합과 정확히 같다. 따라서 `KN-history`와 `KN-prose`가 들어가지 않음도 확인된다.
- 대역: 없음.
- 비고: `subTest`는 쓰지 않고 두 경우를 한 반복문에서 단언한다.

### `test_relation_judgment_edges_keep_formal_and_assessment_use_current` (행 60–77)
- 성질: 과제 평가가 관계를 증거로 인용하면, 그 관계가 증거 필드로 가리키는 형식 결과나 신원 평가의 현재 효력(`formal_use`, 평가 사용의 `status`)이 평가 근거 해시에 들어가, 효력이 정지되면 근거가 바뀐다.
- 준비: 세 필드(`formal_result_refs`, `assessment_refs`, `evidence_refs`)마다 `record_fixtures.specialist_assessment()`로 새 상태를 만든다. 이 상태에는 검증된 정리 `kid`(형식 결과와 신원 평가 `aid`를 가짐)와 과제 `TK-1`이 있다. 관계 `RL-proof`(`supports`, 끝점 둘 다 `kid`)의 해당 필드에, `assessment_refs`면 `aid`를, 나머지 둘이면 형식 결과 ID를 넣는다. 평가는 `RL-proof`만 증거로 인용한다.
- 실행: `task_scope.assessment_basis(task, assessment, instance, runtime)`로 기준값을 뜬 뒤, `assessment_refs`면 모든 `assessment_uses`의 `status`를 `'suspended'`로, 나머지 둘이면 형식 결과의 `formal_use`를 `'suspended'`로 바꾸고 다시 부른다.
- 단언: 두 결과가 다르다(`assertNotEqual`).
- 대역: 없음.
- 비고: `subTest(field=...)` 세 경우. `evidence_refs`에 형식 결과 ID를 넣은 경우도 같은 효과를 내는데, 제품의 `relation_evidence_references`가 세 필드를 같게 읽고, `assessment_basis`가 그 참조 가운데 형식 결과·신원 평가·평가 사용·목표 판정 가족에 속한 것을 "strict"로 올려 그 연결까지 따라가기 때문이다(`task_scope.py` 235–242행 주석 "Explicit expert evidence has the same force here as a direct assessment citation").

### `test_relation_endpoints_still_bind_submitted_content_not_later_review_bookkeeping` (행 79–90)
- 성질: 증거 필드가 없는 관계의 끝점 지식은 평가 근거에 제출된 내용으로만 묶인다. 뒤에 붙는 검토 장부(검토 주기 ID, 형식 결과의 사용 상태와 검증 표지)는 근거를 바꾸지 않고, 해설 본문이 바뀌면 근거가 바뀐다.
- 준비: `record_fixtures.completed_with_knowledge()`의 상태(정리 `KN-proof`, 형식 결과 `FR-proof`, 해설 `XP-proof`). 관계 `RL-content`(`supports`, 끝점 둘 다 `KN-proof`, 증거 필드 없음)를 두고, 평가는 `RL-content`만 인용한다.
- 실행: `assessment_basis`로 기준값을 뜬다. 지식에 `review_cycle_id='RC-new'`를 달고 `FR-proof`를 `formal_use='active'`, `verification={'status': 'verified'}`로 바꾼 뒤 다시 부른다. 이어서 해설 첫 항목의 `text`를 `'changed argument'`로 바꾸고 다시 부른다.
- 단언: 장부 변경 뒤의 결과는 기준값과 같고(`assertEqual`), 해설 변경 뒤의 결과는 다르다(`assertNotEqual`).
- 대역: 없음.
- 비고: 앞 시험과 짝을 이룬다. 앞 시험은 관계가 전문가 증거를 명시하면 그 효력이 근거에 들어감을, 이 시험은 끝점만 있는 관계에서는 효력 장부가 들어가지 않음을 본다.

## 관계

- 같은 제품 기능을 다른 층에서 검사하는 모듈:
  - `revision_waits`와 `capture_targets`: `test_revision_obligations`, `test_decision_basis`, `test_academic_preparation`, `test_planning_engine`.
  - `user_waits`: `test_questions`, `test_governance`.
  - `reported_references`: `test_reference_catalog`, `test_role_input`.
  - `assessment_basis`: `test_academic`, `test_academic_preparation`, `test_family_records`, `test_model_metadata_boundary`, `test_state_checks`, `test_task_completion`.
  - `plan_impact`: `test_knowledge`, `test_impact_review`, `test_task_scope` 등 원문에 이름이 나오는 모듈이 이 모듈을 포함해 14개다.
- 픽스처 의존: `engine_fixtures.start_query_repository`는 이 모듈 밖에서 `test_query_records`, `test_control_shapes`도 쓴다. `record_fixtures`의 `approved_task`·`approve_task`·`specialist_assessment`·`completed_with_knowledge`는 과제 계약 계열 모듈과 공유한다.
- 이 모듈에만 있는 도우미: 없다.
- 겹치거나 보완하는 시험: 이 모듈은 관계라는 한 기록 종류가 네 소비자에서 같은 간선을 내는지를 가로로 본다. 각 소비자의 일반 규칙(개정 대기의 순서, 질문 경로, 평가 근거의 가족별 규칙)은 위의 소비자별 모듈이 세로로 본다.
