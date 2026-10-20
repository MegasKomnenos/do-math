# 실제 종류 판정의 저장 표본과 ontology 계약시험을 함께 고친다

사용자 목표는 실제 생산값의 저장을 막지 않으면서, 수신 schema의 필수·선택 필드가 실제 생산 표본과 공통 역방향 검사에 연결되게 하는 것이다. storage-inputs가 복원한 실제 `kind_definitions.check`와 기존 ontology 표본/단언 사이의 F2를 한 task에서 마친다. 별도 읽기 task나 필드별 수리로 나누지 않는다.

SESSION_JSON, task.json, inputs/context.md·plan.md·seams.md와 `.claude/skills/do-math/AGENTS.md`, scripts/tests/시험-지침.md를 읽는다. 원요구는 C:/math/docs/do-math/continuous-development-2026-10-13/sources/user-decisions.md·requirements-index.json의 R01/1-A·1-B/K-78과 C:/math/docs/do-math/시험-재편-2026-09-29/설계.md 3.3/A20이다. 원문·모델/묶음 지시는 queue.inputs의 같은 sources 파일을 따른다. 읽기 전용 근거는 C:/math/.async/dm/managers/0058/review.md·verification-review.json, tasks/storage-inputs/report.json·evidence/judgment.md·families.json 및 private-corrected-3/run/report.json, storage-authority의 기존 보고·표본이다.

## 직접 확인된 사실

`CoreEngineMixin._apply_kind_definition_check`는 정확 현재 정의와 독립 checker의 input_basis를 확인하고 definition의 `check`에 원 output의 definition_id/definition_sha256/decision/findings 및 execution_id를 쓴다. storage-authority는 domain의 `knowledge_io.check_kind_definition` 표본만 검사하면서 이 슬롯을 미생산으로 잘못 제거했다. storage-inputs는 기존 sim의 실제 정상 판정 후 저장 실패를 재현하고 `RECORDS['kind_definitions']['properties']['check'] = EVIDENCE`를 복원했다. history/checks/activation은 계속 미생산이다.

기존 `tests/support/storage_authority_pairs.py:ontology_samples`에는 core가 생산한 check 표본이 없고 `tests/contracts/test_storage_authority_pairs.py:AuthorityFieldPairs.test_ontology_fields_reach_the_actual_map_and_list_receivers`는 check를 제거필드로 기대한다. private-corrected-3의 해당 부모 row는 역방향 missing check와 check=[]에 대한 옛 Additional properties 기대 불일치 두 subTest로 실패했다. 같은 실행의 새 private helper 준비 오류 두 건은 후속 교정됐지만 ontology 실패는 아직 남아 있다. 이를 새 입력4가족 시험 통과로 해결됐다고 보지 않는다.

## 완료할 결과

1. 실제 제안·독립 checker·현재 정의/hash·판정 적용을 거쳐 검증 게시되고 새 reader로 decode된 `kind_definitions.check` 표본을 기존 ontology Pair에 연결한다. 최종 Pair는 기존 종류와 관계의 필수/선택·중첩 필드 검사를 그대로 수행한다. check를 수동으로 채우거나 schema/Pair를 약화하거나 실제 writer를 지워 통과시키지 않는다.
2. check를 제거목록에서 빼고 저장된 object가 원 definition ID/hash·decision/findings·실제 checker 실행 ID와 정확히 같은지 독립 기대값으로 단언한다. 승인/수정요구/미해결의 실제 판정·종류 상태·독립성·정확 pending만 제거하는 의미는 storage-inputs의 기존 근거와 단언을 보존한다. 그 세 판정을 새 장면에서 모두 중복 실행할 필요는 없다. 새 연결에 필요한 최소 실제 표본을 선택하고 근거 범위를 설명한다.
3. 나머지 미생산 11필드의 정확 추가필드 반려/옛head 불변, 관계 revision/history·승인/철회·봉인 근거와 기존 optional drift 검사를 보존한다. check의 열린 object 내용은 독립 값 단언으로 검사하며 임의 evidence 키의 필드 의무를 만들지 않는다.
4. 가까운 helper/직접 소비자 수리는 함께 처리한다. 현재 storage_input_pairs가 storage_authority_pairs._named_fields를 import하므로 무작정 반대 방향 import를 추가하지 않는다. 필요하면 실제 종류 준비/검사 장면만 작은 `tests/support/storage_kind_checks.py`로 옮기고 두 helper/직접 시험이 그 정본을 소비하게 한다. 별도 registry·역방향 알고리즘·범용 추상화·test module 간 import를 만들지 않는다. 기존 별도 reader와 실제 저장을 유지한다.

## 소유와 선행

직접 선행은 수용된 storage-inputs 하나다. storage-actions와 storage-recovery는 이 시험 수리를 소비하지 않으며 기다릴 이유가 없다. 두 작업의 배정과 제품 runtime/schema/저장기반/공유 설명은 본 task가 수정하지 않는다. 이미 제품 정본 설명은 check의 실제 writer와 미생산11개로 교정됐다. 기존 ontology/helper, 필요시 입력 helper/직접시험·새 공통 종류 helper 및 공식미러만 task.json.writes에서 수정한다. 비용캐시는 관측 보존 뒤 own base로 복원한다. 범위밖 결함이면 정확 경로/영향/최소 반례를 보고한다.

## 필요한 확인과 보고

자기 workspace 공식 run_tests.py --jobs 1로 실패했던 정확 ontology row와 실제로 바꾼 helper 소비자만 최소 선택한다. 기존 수용된 단언/원보고로 충분한 성질은 반복하지 않는다. 새 실제 종류 helper로 이동한다면 그 소비자인 입력 pending 시험도 확인한다. 독립 storage-actions가 자기 jobs1로 진행할 수 있으며 동시 공식시험 상한3이다. 전체 일반/freshT3/변이/T4/T5·실provider/Lean/HTTP/native Job/설치/OS예약은 이 배정이 아니다.

원보고·최초 실패/교정판·selected/고유 실제row/counts/fixture·실제 exit·source SHA/changed_during_run·소프트 초과를 보존한다. 공식 build_skill_mirrors.py 생성/check, 변경 경로/캐시 복원을 확인한다. report.json에는 F2 해소와 기존 kind 가족 질문의 현재 범위, 남은 최종판 확인을 구별하고 `python C:/math/services/async-development/check.py report C:/math/.async/dm storage-ontology-fix`를 통과시킨다. 공용 source/context/plan/seams/queue/state·다른 task·engine·Git index/commit·graphify·기존 연구는 수정하지 않는다.
