# do-math 정리 검토 — STO(저장·상태) 영역

작성: 2026-09-27. 공통 계약은 `C:/math/임시/do-math-정리-검토-2026-09-27/기준.md`다. 경로는 따로 밝히지 않으면 `C:/math/.claude/skills/do-math/` 기준의 상대 경로이고, 행 번호는 커밋 `9b434f4`의 작업 트리 기준이다.

## 1. 읽은 범위

### 전문을 읽은 파일

| 파일 | 행 수 |
|---|---|
| `scripts/do_math/repository.py` | 996 |
| `scripts/do_math/git_store.py` | 685 |
| `scripts/do_math/state_contract.py` | 226 |
| `scripts/do_math/state_checks.py` | 355 |
| `scripts/do_math/record_schemas/__init__.py` | 598 |
| `scripts/do_math/record_schemas/schemas.py` | 719 |
| `scripts/do_math/events.py` | 72 |
| `scripts/do_math/retention.py` | 357 |
| `scripts/do_math/context_store.py` | 969 |
| `scripts/do_math/input_basis.py` | 110 |
| `scripts/do_math/payloads.py` | 201 |
| `scripts/do_math/preflight.py` | 146 |
| `scripts/do_math/file_io.py` | 281 |
| `scripts/do_math/input_recovery.py` | 52 |
| `C:/math/임시/do-math-정리-검토-2026-09-27/기준.md` | 237 |
| `AGENTS.md` | 11 |
| `C:/math/docs/do-math/검사-경량화-이음새-계약.md` | 245 |
| `C:/math/임시/경량화-조사-2026-09-26/STO.md` | 769 |
| `C:/math/임시/경량화-조사-2026-09-26/결과-B.md` | 102 |
| `C:/math/임시/경량화-조사-2026-09-26/결과-K제품.md` | 116 |
| `C:/math/임시/시험-경량화-2026-09-26/작업자-노드/W-git-M-0350.md` | 65 |
| `C:/math/임시/시험-경량화-2026-09-26/작업자-노드/W-eng-M-0350.md` | 36 |
| `C:/math/기억/layer3/L-0020.md` | 148 |

### 세 커밋의 변경

- `9b434f4`: `repository.py`, `payloads.py`, `context_store.py`, `record_schemas/schemas.py`의 diff를 전부 읽었다. `git_store.py`의 diff는 삭제된 git 호출 줄만 검색으로 확인했고, 새 구현은 현재 원문 전문으로 검토했다.
- `8d2ffd0`: 영역 파일 9개(`repository`, `git_store`, `state_contract`, `state_checks`, `retention`, `payloads`, `input_basis`, `preflight`, `record_schemas/__init__`)의 추가된 줄을 전부 읽었다. `context_store.py`와 `file_io.py`는 변경 통계만 보고 현재 원문으로 검토했다.
- `379a171`: 변경 통계, 그리고 영역 파일에 추가된 주석·정의·캐시 줄을 검색으로 읽었다. `record_schemas/domains.py` → `schemas.py` 병합분(약 1,100행)은 줄 단위로 읽지 않았다. 대신 필드 이름 전수 검색(STO-05)으로 결과를 대조했다.

### 일부만 읽은 파일

이음새를 따라 판정에 필요한 범위만 읽었다.

- `scripts/do_math/engine.py`: 60-84, 280-300, 2815-2860, 3188-3310의 `fitted` 사용 줄(검색)
- `scripts/do_math/scheduler.py`: 60-95, 580-610
- `scripts/do_math/parallel.py`: 30-129
- `scripts/do_math/review_engine.py`: 216-247, 945-947
- `scripts/do_math/observations.py`: 94-97, 490-515
- `scripts/do_math/knowledge_records.py`: 127-131, 196-221
- `scripts/do_math/external.py`: 17-20
- `scripts/do_math/task_contracts.py`: 13-15, 116-117
- `scripts/do_math/knowledge.py`: 17-21
- `scripts/do_math/contracts.py`: 332-347
- `scripts/tests/research_fixtures.py`: 770-809
- `scripts/tests/test_boundary_repairs.py`: 28-48
- `scripts/tests/test_initialization_efficiency.py`: 80-90
- `scripts/tests/test_lifecycle_engine.py`: 796-808
- `scripts/tests/test_preflight.py`: 40-60
- `scripts/tests/test_redesign_LIFECYCLE.py`: 136-150
- `scripts/tests/test_research_reliability.py`: 335-352
- `scripts/tests/test_redesign_SURFACE.py`: 820-832
- `C:/math/기억/layer1/M-0350.md`: 저장 관련 줄(검색)

파견문이 정한 파일 가운데 읽지 못한 것은 없다. 4.1·4.2절의 종류 가운데 검토하지 못한 종류도 없다.

## 2. 영역 판정

STO의 현재 구조는 세 경량화의 방향성에 대체로 맞는다. 이음새 정본(`file_io`의 JSON·해시·지문, `sealed_bytes`, `check_sequence`, `check_path_segment`)이 한 곳에 있고, 9b434f4가 더한 프로세스 안 객체 쓰기와 artifact 사실 캐시는 CAS 불변식을 지키며 키가 커밋 OID 계보에 묶인 건전한 캐시다. 가장 큰 개선 여지는 제품 호출자가 없는 런타임 가족 등록 기구다(STO-01). 이 기구 때문에 저장소 객체마다 계약을 깊은 복사하고, 두 경량화가 그 위에 계약 세대 번호를 캐시 키와 게시 기준에 얹었다. 계약을 프로세스당 불변 하나로 두면 저장 계층이 하나의 단순한 구조로 정리된다. 두 번째 여지는 저장 계약 검증 안에서 "부모와 같은 레코드는 다시 검사하지 않는다"는 규칙이 가족 검증기와 수작업 비교 네 벌로 갈라져 있고, 검증이 엔진 믹스인에 기대는 점이다(STO-02, STO-03). 나머지는 생산자 없는 스키마 필드·조건·봉인 분기와 소형 잔재의 정리다. 판본 표지 단일화(STO-09)는 저장 형식을 바꾸므로 사용자 판단이 필요하다.

검토했고 없음: 파생상태, 문서, 결함, 임시방편

## 3. 후보

### 검토 1

#### STO-01 런타임 가족 등록과 계약 세대 추적이 시험만을 위해 제품에 남아 있다
- 검토: 1
- 종류: 미사용
- 좌표: `scripts/do_math/repository.py:101-106`, `:243-248`, `:258-259`, `:405-406`, `:421-425`; `scripts/do_math/state_contract.py:23-29`, `:49-63`, `:73-95`, `:110-122`, `:167-174`, `:211-226`; `scripts/do_math/task_contracts.py:116-117`
- 현상:
  - `ResearchRepository.register_family`는 저장소마다 가족을 더 등록한다. 외부 스키마는 `check_schema`로 메타 검사한다.
  - `StateContract.register_family`는 이미 설치된 가족의 재등록에서 검증기와 참조 함수를 합성한다(73-95행).
  - 이 기능을 허용하려고 제품은 다음을 한다.
    - `StateContract.default()`는 설치 템플릿을 저장소 객체마다 `deepcopy`한다.
    - `validation_generation`과 `installed_generation`으로 계약이 바뀌었는지 추적한다.
    - `_contract_key`는 설치본이 아닌 계약을 세대 번호와 함께 `_VALIDATED_READS` 키로 쓴다.
    - `validate_candidate`의 `basis`와 `save_validated`는 세대 번호를 대조한다.
    - `installed_checker`는 복사본이 검증기를 끌고 다니지 않게 템플릿에서 따로 검증기를 만든다(216-218행 주석).
  - 세대 기구 가운데 `installed_generation`·`_contract_key`·manifest 세대 메모는 8d2ffd0가, `save_validated`의 세대 기준과 `installed_checker`는 379a171이 더했다.
- 근거:
  - 제품 등록자는 `record_schemas.install` 하나다. 검색식 `\.register_family(`를 `scripts/do_math`에서 `contract.register_family`·`def register_family`·`record_schemas/__init__.py`를 빼고 돌리면 0건이다.
  - `ResearchRepository.register_family`의 호출은 시험 7개 파일의 21건이 전부다(`test_boundary_repairs` 1, `test_initialization_efficiency` 3, `test_redesign_STORAGE` 7, `test_repository` 2, `test_state_contract_registration` 5, `test_storage_validation` 1, `test_unicode_flow` 2).
  - `validation_generation|installed_generation|_contract_key`는 `repository.py`, `state_contract.py`와 `tests/test_state_contract_registration.py`에만 나온다.
  - 실측(아래 6절 명령): 새 계약 하나에 `StateContract.default()` 14.6ms, 첫 `manifest()` 6.3ms, 가족 100개의 검증기 생성 6.6ms가 든다. 저장소 객체는 `cli.py` 6곳, `engine._repository`, `scheduled_operator.py` 3곳에서 만들어진다.
- 제안:
  - 설치 계약을 프로세스당 하나 만들어 공유한다. `default_state_contract()`는 그 객체를 돌려준다.
  - 다음을 지운다.
    - `ResearchRepository.register_family`와 `check_schema`
    - 재등록 합성 분기
    - `installed_generation`과 `_contract_key`의 세대 분기(키는 "설치 계약" 또는 계약 객체 자신)
    - `basis`의 `validation_generation`(기준은 head만)
    - `_default_template(cls)`의 인자
  - `installed_checker`는 공유 계약의 `family(...).checker`로 바꾼다.
  - 모든 식별 가족의 `id`가 스키마 `ID`(`RECORD_ID` 패턴)로 검사되므로, `StateContract.validate`의 `re.fullmatch(RECORD_ID, ...)` 재검사(167-170행)도 지울 수 있다. Windows 장치명 검사(`check_path_segment`)는 스키마로 표현할 수 없으므로 남긴다.
  - 시험은 자기 계약(`StateContract()` + `install` + 필요한 가족 등록)을 만들어 `ResearchRepository(..., contract=)`로 넘긴다. 설치 가족에 거부 검증기를 끼워 넣던 시험은 실제로 계약을 어기는 레코드로 같은 경로를 검사한다.
- 실익:
  - 제품 코드가 약 50-60행 준다.
  - 첫 저장소 뒤의 저장소 객체마다 약 27ms(측정값의 합)가 준다.
  - `_VALIDATED_READS` 키와 게시 기준에서 세대 차원이 사라진다.
  - 기준 2.4("시험을 살리려고 제품에 예외를 넣지 않는다")와 2.5에 맞는다.
- 비용과 위험:
  - 시험 7개 파일 21곳을 고친다. `test_state_contract_registration`의 등록 기능 시험 다섯은 기능과 함께 지운다.
  - 공유 계약을 누가 변경하면 모든 저장소에 번진다. 설치 뒤에는 등록 경로를 제품에서 부르지 않게 하는 것으로 막는다.
  - 새 상태·수명·복구 규칙은 없다.
- 기능·커버리지 영향: 있음. 제품 호출자가 없는 "외부 가족 등록" 기능과 그 시험이 사라진다. 설치 계약의 검증과 manifest 다이제스트는 같다.
- 사용자 결정 관련: 없음
- 확신도: 확인

#### STO-02 레코드 국소 의미 규칙의 부모 동등 생략이 네 벌로 따로 구현되고, 일부 규칙에는 없다
- 검토: 1
- 종류: 불일관
- 좌표: `scripts/do_math/state_contract.py:157-166`; `scripts/do_math/record_schemas/__init__.py:189-191`, `:220-231`, `:239-261`, `:344-365`, `:374-381`, `:527-557`
- 현상:
  - `StateContract.validate`에는 일반 규칙이 이미 있다. 부모와 같은 레코드는 스키마와 가족 검증기를 건너뛴다(157-166행).
  - `validate_semantics`는 같은 생략을 규칙마다 손으로 다시 구현한다. `governance_sources`(220-223), `academic_resolution_records`(`_prior_rows`, 347-350), `observation_facts`(376-378), `intent_imports`(529-532), 그리고 `grants`의 복합 조건(224-231)이다.
  - 다음 레코드 국소 규칙은 부모와 같아도 저장마다 다시 돈다.
    - 실행의 종료 증거·`stop_phase`·수락 영수증·실행 창·권한 회수(247-261)
    - 외부 작업의 요청 결속(`json_digest` 재계산)·재시도 증거·confirmed/failed(354-365)
    - 운영 처분(344-345)
    - 위임 적용의 `json_digest` 두 가지와 고유 실행 검사(538-557 가운데 레코드 안에서 끝나는 부분)
- 근거:
  - 수작업 생략 네 곳과 일반 생략 한 곳은 원문으로 확인했다.
  - 기준 2.6은 "같은 사실의 반복 확인"을 없애라고 한다. 부모와 같은 불변 레코드의 해시를 저장마다 다시 계산하는 것이 여기에 해당한다.
- 제안:
  - 레코드 하나로 결정되는 규칙을 `install`에서 해당 가족의 검증기로 등록한다. 그러면 `StateContract.validate`의 일반 생략이 부모와 같은 레코드를 자동으로 건너뛴다.
  - 대상은 실행 국소 규칙, 외부 작업, 운영 처분, 학술 봉인, 관찰 사실 원문, 의도 수입 봉인, 위임 적용의 digest, `governance_sources`다.
  - `_prior_rows`와 수작업 prior 비교 네 곳을 지운다.
  - 레코드 사이의 규칙(프로필 대조, 참조 해석, 활성 grant의 원천·결정 결속)은 `validate_semantics`에 남긴다.
- 실익:
  - 생략 방식이 하나가 된다. 약 15행이 순감한다.
  - 변경 없는 실행·외부 작업·위임 적용 레코드의 재해시와 재검사가 저장마다 사라진다. 레코드 수에 비례하며 규모는 측정하지 않았다.
- 비용과 위험:
  - 한 파일 안에서 규칙을 옮긴다. 가족 검증기는 `deepcopy(record)`를 받으므로(`state_contract.py:166`) 바뀐 레코드에만 작은 복사 비용이 생긴다.
  - 오류 문구는 그대로 옮길 수 있다. 새 상태는 없다.
- 기능·커버리지 영향: 없음. 적재(부모 없음)에서는 모든 규칙이 지금처럼 돈다.
- 사용자 결정 관련: 없음
- 확신도: 추정. 구조는 원문으로 확인했다. 비용 규모는 `operation_trace`의 `candidate_validation` 구간을 실제 인스턴스 크기의 상태에서 저장 1회 기준으로 전후 비교하면 확정된다.

#### STO-03 저장 계약 검증이 엔진 믹스인을 빌려 staged 후보를 다시 만들고, 역사 사이클의 기준 해시를 저장마다 다시 계산한다
- 검토: 1
- 종류: 경계
- 좌표: `scripts/do_math/record_schemas/__init__.py:457-460`, `:463-488`; `scripts/do_math/review_engine.py:218-245`, `:945-947`; `scripts/do_math/review_cycle.py:378`
- 현상:
  - `validate_semantics`는 `from ..review_engine import ReviewEngineMixin`으로 엔진 층을 가져온다.
    - `ReviewEngineMixin._identity_assessment`는 `review_cycle.identity_assessment`를 그대로 부르는 staticmethod다(945-947행).
    - checking·ready 전이의 사이클마다 `ReviewEngineMixin()`을 생성자 없이 만들고 `instance`·`runtime` 속성을 붙여 `_staged_review_candidate`를 부른다(484-488행). 이 메서드는 `self.instance`와 `self.runtime`만 읽는 순수 계산이다(218-245행).
  - 비용도 있다.
    - `staged_candidate`나 `transition_id`가 있는 모든 사이클은 저장마다 `transition_basis`를 `exact_content_hash`로 다시 계산한다(478행). 완료된 역사 사이클도 포함된다.
    - 진행 중인 전이의 사이클은 저장마다 후보 전체를 다시 만든다. 여기에는 `validate_basis`, `record_digest` 둘, `validate_formal_evidence`, `formal_overlay`, `identity_basis`, 해시가 든다.
- 근거:
  - 영역 파일의 엔진 import는 검색식 `from \.\.(engine|review_engine|lifecycle_engine|...)`로 찾았고 이 두 곳뿐이다.
  - 메서드 본문의 `self.` 사용은 `instance`와 `runtime`뿐이다(218-245행 검색).
- 제안:
  - `_staged_review_candidate`의 본문을 `review_cycle`의 순수 함수 `staged_review_candidate(instance, runtime, transition_id, knowledge_id)`로 옮긴다. 엔진 메서드와 저장 계약이 함께 이 함수를 부른다.
  - 저장 계약은 `review_cycle.identity_assessment`를 직접 부른다.
  - 사이클, 그 전이, 대상 환경이 모두 부모와 같으면 `transition_basis`와 staged 후보 재계산을 건너뛴다(STO-02와 같은 생략 원리).
- 실익:
  - 저장 계층에서 엔진 층으로 올라가는 의존이 사라진다. 엔진 믹스인을 바꾸면 저장 검증이 영향을 받는 경로도 없어진다.
  - 변경 없는 사이클의 저장당 재계산이 사라진다. 전이·사이클 수에 비례하며 측정하지 않았다.
- 비용과 위험:
  - REV 모듈 둘(`review_engine`, `review_cycle`)을 고친다.
  - 생략 조건에 세 레코드(사이클·전이·환경)를 모두 넣지 않으면 바뀐 입력을 놓친다.
  - 새 상태는 없다.
- 기능·커버리지 영향: 없음
- 사용자 결정 관련: 없음
- 확신도: 추정. 의존과 호출 형태는 확인했다. 비용 규모는 전이 진행 중인 상태에서 `validate_semantics` 시간을 재면 확정된다.

#### STO-04 preflight가 서로 무관한 세 책임을 담고, 상태 관문에 도달하지 않는 분기와 시험 전용 반환 형태가 있다
- 검토: 1
- 종류: 경계
- 좌표: `scripts/do_math/preflight.py:1-4`, `:33-69`, `:72-91`, `:94-146`; `scripts/do_math/record_schemas/__init__.py:205-208`; `scripts/do_math/record_schemas/schemas.py:336`, `:610`, `:653`; `scripts/do_math/task_contracts.py:13`
- 현상:
  - 모듈 docstring은 "설치된 스킬의 읽기 전용 구조 검사"라고 하지만, 모듈은 세 가지를 담는다.
    - 스킬 구조 검사: `inspect_bundle`, `INSTALLED_DOCUMENTS`
    - 모든 상태 검증에 걸리는 수명 주기 관문: `inspect_current_state`
    - 상태를 게시하는 쓰기: `preserve_rejected_candidate`. 제품 호출자는 `lifecycle_engine` 둘이다.
  - `inspect_current_state`는 `{"valid", "errors", "feature_version"}` dict를 돌려준다. 제품 호출자는 `validate_semantics` 하나이고, 이 호출자는 무효면 예외로 바꾼다(205-208행). dict 형태를 읽는 것은 시험(`test_lifecycle_engine.py:800-806`, `test_preflight.py:46-51`)뿐이다.
  - `derived_readiness` 검사(67-68행)는 도달하지 않는다.
    - 과제 `status`는 `LIFECYCLE_STATES`의 enum이고(`schemas.py:336`), 이 집합에는 `ready`가 없다(`task_contracts.py:13`).
    - `StateContract.validate`는 스키마를 `validate_semantics`보다 먼저 검사하고, 부모와 같은 레코드는 이미 검증된 부모의 것이다.
  - 수명 주기 상태 집합과 runtime 상태 집합은 코드에만 있다. 스키마에서 `lifecycle.state`(`schemas.py:610`)와 runtime `status`(`:653`)는 `TEXT`다. 2라운드 STO-02가 실행·과제 상태를 스키마 enum으로 옮긴 방식과 다르다.
- 근거: 검색식 `inspect_current_state`는 제품 2건(`record_schemas`), 시험 11건이다. `derived_readiness`는 시험에서 이 검사를 부르는 곳이 없다(`test_redesign_LIFECYCLE.py:138`은 엔진 메모리의 파생값을 본다).
- 제안:
  - 관문을 `record_schemas`(검증 층)로 옮기고, 예외를 내는 검사로 바꾼다.
  - `lifecycle.state`와 runtime `status`의 값 집합은 스키마 enum으로 표현한다.
  - `derived_readiness`는 지운다.
  - `preserve_rejected_candidate`는 호출자 옆(`lifecycle_engine`)이나 `repository`로 옮긴다.
  - `preflight`에는 스킬 구조 검사만 남긴다.
- 실익:
  - 모듈 책임이 하나가 되고 docstring이 사실이 된다.
  - 상태 값 집합의 정의가 스키마 하나가 된다.
  - 약 10행이 준다.
- 비용과 위험:
  - `record_schemas`, `lifecycle_engine`과 시험 넷(`test_preflight`, `test_lifecycle_engine`, `test_redesign_LIFECYCLE`, `research_fixtures`의 docstring)을 고친다.
  - enum을 더하면 manifest 다이제스트가 바뀐다. 구판 호환 요구는 없다(AGENTS.md).
  - 새 상태는 없다.
- 기능·커버리지 영향: 없음. 거부되는 상태 집합이 같다.
- 사용자 결정 관련: 없음. 저장 검증을 약하게 하지 않고 같은 강도로 옮긴다.
- 확신도: 확인

#### STO-05 저장 스키마에 생산자도 소비자도 없는 필드 이름이 38개 있다
- 검토: 1
- 종류: 미사용
- 좌표(모두 `scripts/do_math/record_schemas/schemas.py`):
  - `knowledge`: `change_reasons`·`impact_plan` 178
  - `relations`: `endpoint_basis` 208
  - `kind_definitions`: `withdrawal` 220
  - `events`: `subject_ref` 225. `record_schemas/__init__.py:57`의 참조 표에도 있다.
  - `executions`
    - `input_bytes` 269
    - `resume_from` 275
    - `initialization_id` 276
    - `return_reason` 285
    - `protocol`·`provider_execution` 290
    - `elapsed_milliseconds`·`return_code` 302
  - `tasks`
    - `created_by` 347
    - `knowledge_basis` 351
    - `change_reasons` 352
    - `stages` 355
  - `grants`: `used_by` 419
  - `decisions`: `initial_registration` 425, `intent_check_ref` 428
  - `observation_facts`: `monotonic_seconds` 463
  - `self_check_obligations`: `deadline_monotonic` 471, `safe_boundary_ref`·`close_reason`·`closed_at` 475
  - `operational_dispositions`: `source_execution_id` 488. `record_schemas/__init__.py:49`의 참조 표에도 있다.
  - `trust_transitions`: `semantic_pending` 551, `semantic_results` 552
  - `recoveries.dispositions`: `reservation_reconciled` 570, `process_alive`·`workspace_preserved` 571
  - `lifecycle`
    - `initial_profile_id`·`requires_initial_profile` 612
    - `resume_state` 613
    - `closed_at` 620
  - `observations`: `due_offset_ms`·`started_offset_ms` 652
  - runtime 필드
    - `clock_guard.high_water` 658
    - `interpretation_history` 663
  - `waiting_actions`: `waiting_since` 693
- 현상: 이 이름들은 닫힌 스키마(`additionalProperties: False`)에 선언돼 있다. 그러나 제품 어디에서도 쓰거나 읽지 않는다.
- 근거:
  - 1차 검색: `RECORDS`와 `RESEARCH_FIELDS`·`RUNTIME_FIELDS`를 재귀로 훑어 속성 이름 933개를 모았다. 그다음 `record_schemas` 밖의 모든 제품 `.py`에서 `'이름'`, `"이름"`, `이름=` 형태를 찾았다. 일치가 없는 이름이 38개다.
  - 2차 확인: 38개마다 `grep -rlw`를 제품(`record_schemas` 제외), 시험, 스킬 전체 `.md`에 돌렸다.
    - 제품 일치 5건(`input_bytes`, `protocol`, `stages`, `withdrawal`와 `state_checks`의 함수명)은 원문을 확인한 결과 모두 지역 함수명·주석·다른 낱말이었다.
    - 시험 일치 3건(`endpoint_basis`, `reservation_reconciled`, `input_bytes`)도 다른 이름의 일부이거나 지역 변수다.
    - 문서 일치는 0건이다.
  - `git log -S`로 보면 대부분 7d2597e부터 있었고, 379a171은 `domains.py` 병합으로 옮기기만 했다. 경량화가 만든 것은 아니다.
- 제안: 38개 속성과 참조 표의 두 항목(`subject_ref`, `source_execution_id`)을 지운다.
- 실익:
  - 닫힌 스키마가 실제 생산자와 같아진다(기준 2.5).
  - 스키마 항목 약 40개가 준다.
  - 오타 필드를 적재 전에 거부할 여지가 커진다.
- 비용과 위험:
  - `schemas.py`와 참조 표만 고친다. manifest 다이제스트가 바뀐다.
  - 이름 단위 판정이라, 같은 이름이 다른 가족에서 쓰이는 미사용 필드는 이 목록에 들지 않았다. 실제 미사용 필드는 더 있을 수 있다.
  - 새 상태는 없다.
- 기능·커버리지 영향: 없음
- 사용자 결정 관련: 없음
- 확신도: 확인

#### STO-06 호출자 없는 저장소 함수 둘: `_canonical_object`와 시험 전용 `ResearchRepository.records`
- 검토: 1
- 종류: 미사용
- 좌표: `scripts/do_math/repository.py:520-527`, `:723-726`
- 현상:
  - `_canonical_object`에는 호출자가 없다.
  - `records(snapshot, family=, root=)`는 시험만 부른다. 제품은 같은 서술자를 `load_records`와 `read_record`로 쓴다.
- 근거:
  - 영역 모듈의 최상위 정의·메서드마다 이름 경계 정규식으로 저장소 전체 `.py`의 참조를 셌다. `_canonical_object`는 제품 0, 시험 0이다. 마지막 호출자는 7d2597e에서 지워졌다(`git log -S"_canonical_object("`).
  - `\.records(`는 제품 0건, 시험 6건이다. 그 가운데 `test_redesign_ACTIVITIES.py:118`은 다른 객체의 메서드다.
- 제안: 둘 다 지운다. 시험 다섯 곳은 `load_records(head)[3]`을 거른다.
- 실익: 약 12행이 준다. 공개 API 표면이 하나 준다.
- 비용과 위험: 시험 4개 파일을 고친다. 새 상태는 없다.
- 기능·커버리지 영향: 없음
- 사용자 결정 관련: 없음
- 확신도: 확인

#### STO-07 정리 적격 판정이 생산자 없는 필드를 조건으로 읽는다
- 검토: 1
- 종류: 미사용
- 좌표: `scripts/do_math/retention.py:245`, `:254`
- 현상:
  - `cleanup_candidates`는 `execution.get('recovery_pending') or execution.get('checkpoint_required')`를 복구 대기 사유로 본다.
  - 대기 행동에 대해서는 `not waiting.get('resolved')`를 조건으로 쓴다.
- 근거:
  - 실행 스키마(`schemas.py:260-317`)와 대기 행동 스키마(`:691-709`)는 닫혀 있고, 세 필드가 없다.
  - 검색식 `recovery_pending|checkpoint_required|'resolved'`의 제품 일치는 이 두 줄과, 다른 가족의 `resolved`(외부 거부, 질문 상태)뿐이다.
  - 따라서 검증된 상태에서 앞의 두 조건은 늘 거짓이고, `not waiting.get('resolved')`는 늘 참이다. 두 줄 모두 7d2597e부터 있었다.
- 제안: 두 조건을 지운다. 실제 조건(`recovery_disposition`의 세 값, 대기 행동이 실행 ID를 포함함)만 남긴다.
- 실익: 삭제 안전 판정이 실제 계약을 드러낸다. 되돌릴 수 없는 삭제의 조건을 읽는 사람이 없는 보호 장치를 믿는 일이 없어진다.
- 비용과 위험: 2행을 고친다. 판정 결과는 같다. 새 상태는 없다.
- 기능·커버리지 영향: 없음
- 사용자 결정 관련: 없음
- 확신도: 확인

#### STO-08 판본 상수의 리터럴 사본이 역할 입력 manifest에 있다
- 검토: 1
- 종류: 이음새
- 좌표: `scripts/do_math/context_store.py:694`, `:746`, `:761`. 영역 밖 사본: `scripts/do_math/contracts.py:91`, `:98`, `:110`; `scripts/do_math/cli.py:635`; `scripts/do_math/engine.py:211`
- 현상:
  - 역할 입력 manifest는 `feature_version=5`를 쓰고, 검증은 `!= 5`와 비교한다. `state_contract.STATE_FORMAT_VERSION`을 참조하지 않는다.
  - 응답 계약 `'do-math-cli/5'`는 정의 상수 없이 다섯 곳에 리터럴로 있다.
- 근거: 검색식 `feature_version|do-math-cli/5`.
- 제안:
  - `context_store`는 `STATE_FORMAT_VERSION`을 쓴다.
  - 응답 계약 ID는 `contracts`에 상수 하나를 두고 모두 참조한다.
  - STO-09를 채택하면 manifest의 `feature_version` 필드 자체가 없어지므로, 이 후보는 응답 계약 ID 부분만 남는다.
- 실익: 판본을 올릴 때 고칠 곳이 준다. 한쪽만 고쳐 모든 역할 입력이 거부되는 경로가 사라진다.
- 비용과 위험: 3개 모듈의 리터럴만 바꾼다. 새 상태는 없다.
- 기능·커버리지 영향: 없음
- 사용자 결정 관련: 없음
- 확신도: 확인

#### STO-09 계약 판본 표지가 저장 경계 밖의 레코드와 metadata에 여러 벌 복제돼 있다
- 검토: 1
- 종류: 이음새
- 좌표:
  - `scripts/do_math/record_schemas/schemas.py:360`, `:375`, `:397`, `:403`, `:603`, `:621`, `:653`
  - `scripts/do_math/record_schemas/__init__.py:120-124`
  - `scripts/do_math/repository.py:843`, `:899-900`, `:921-928`, `:941`, `:983`
  - `scripts/do_math/preflight.py:44-49`
  - 영역 밖: `scripts/do_math/initialization.py:242-254`, `scripts/do_math/engine.py:258-264`, `scripts/do_math/execution_profiles.py:49`, `:66`, `scripts/do_math/budget.py:204`
- 현상: 현재 저장 계약이 하나뿐인데, 같은 사실("이 기록은 현행 계약으로 쓰였다")이 다음 자리에 따로 기록되고 따로 검사된다.
  1. 루트 manifest의 `contract`
  2. 모든 레코드 봉투의 `contract_id`
  3. research·runtime metadata의 `contract_id`
  4. research·runtime metadata의 `feature_version`
  5. `execution_profiles.feature_version`(필수)
  6. `tasks.feature_version`(선택)
  7. `reservations.schema_version`
  8. `review_policy.version`

  이 값은 모두 상수이고, 스키마의 `const`와 `preflight`가 대조한다.
- 근거:
  - 적재는 표지와 무관하게 모든 레코드를 설치 스키마로 검증한다(`repository.py:927-928` 주석과 코드).
  - AGENTS.md 8행은 "형식 검사는 저장·입력 경계에 모으고 내부 로직에서 제품 버전을 반복 확인하지 않는다"고 정한다.
  - 검색식 `feature_version|schema_version|STATE_FORMAT_VERSION|"version"` 결과 가운데 이 여덟 자리를 확인했다.
- 제안:
  - 판본 식별은 저장 경계(루트 manifest의 `contract`, 필요하면 봉투의 `contract_id`)에만 둔다.
  - 레코드와 metadata의 표지 필드, 그 생산자, `preflight`의 `feature_version` 검사를 지운다.
- 실익:
  - 판본을 올릴 때 고칠 곳이 여덟 자리 이상에서 한두 곳으로 준다.
  - 표지 검사 코드와 레코드당 필드가 준다.
- 비용과 위험:
  - 저장 형식이 바뀐다. 계약 식별자를 올리고 인스턴스를 새로 초기화해야 한다.
  - 프로필 sha256이 바뀐다(`feature_version`이 해시 대상이다).
  - 생산자 5개 모듈을 고친다. 새 상태는 없다.
- 기능·커버리지 영향: 없음. 경계의 판본 거부는 유지된다.
- 사용자 결정 관련: 있음. 기준 2절 12항의 "저장 계약 `do-math-state/6`의 형식과 검증"과 결정 1(계약 교체)에 해당한다. 결정 이후 새로 확인한 사실은 두 가지다. 표지가 여덟 자리에 상수로 복제돼 있다. 적재는 표지와 무관하게 설치 스키마로 전부 검증하므로, 표지가 검증에 더하는 정보가 없다.
- 확신도: 확인

#### STO-10 결정 전제 기록이 내부 로직에서 판본 표지를 확인하고, 자기 digest를 다시 대조한다
- 검토: 1
- 종류: 낡음
- 좌표: `scripts/do_math/input_basis.py:34-47`, `:63-80`
- 현상:
  - `capture_review_input_basis`는 `{"version": 5, "values", "sha256": json_digest(values)}`를 저장한다. `review_input_basis_changes`는 `version != 5`이거나 저장된 `sha256`이 같은 기록의 `values`와 다르면 변경으로 보고한다.
  - `capture_decision_basis`는 `version: 1`을 저장하고, `decision_basis_changes`가 이를 확인한다.
- 근거:
  - 검색식 `review_input_basis`: 이 `sha256`을 읽는 곳은 `input_basis.py:46` 하나다. `test_redesign_REVIEWS.py:191`은 `version == 5`를 단언한다.
  - 저장된 값은 적재 때 검증된 상태 안의 같은 레코드에 있다. 그래서 자기 digest 재대조는 기준 2절 6항의 "변조 방어"이거나 "같은 사실의 반복 확인"이다.
  - 판본 확인은 AGENTS.md 8행이 금하는 "내부 로직의 제품 버전 반복 확인"이다.
- 제안:
  - 기록에는 `values`만 둔다(또는 `version`·`sha256`을 뺀다).
  - 두 비교 함수는 기록의 존재만 확인한 뒤 필드를 비교한다.
- 실익: 판정 분기 셋과 호출마다의 `json_digest`가 사라진다. 약 6행이다.
- 비용과 위험:
  - `review_engine`의 생산 호출은 그대로이고, 시험 단언 둘 안팎을 고친다.
  - 기록이 들어가는 `review_cycles.review_input_basis`와 `decision_basis`는 열린 `EVIDENCE` 필드라 스키마는 바뀌지 않는다. 새 상태는 없다.
- 기능·커버리지 영향: 없음
- 사용자 결정 관련: 없음(결정 D3의 "변조 방어: 없앤다"와 같은 방향)
- 확신도: 확인

#### STO-11 레코드 하나의 불변식 일부가 저장 계약이 아니라 상태 점검에만 있다
- 검토: 1
- 종류: 불일관
- 좌표: `scripts/do_math/state_checks.py:249-251`, `:278-283`; `scripts/do_math/record_schemas/__init__.py:247-248`, `:354-365`
- 현상:
  - 외부 작업의 불변식이 둘로 나뉜다. `confirmed`→성공 증거, `failed`→효과 부재는 저장 계약이 검사한다. `unknown`인데 `succeeded`가 확정값, `cancelled`인데 미전송 미확인, `reconciled`인데 증거 없음은 `inspect_state`만 본다.
  - 실행 `outcome`도 같다. 저장 계약은 값이 있는지만 보고, `OUTCOMES` 소속은 점검만 본다.
  - 그래서 이런 상태는 게시될 수 있고, `status`만 `blocked`로 보고한다.
- 근거: 두 파일의 원문. 2라운드는 `outcome ∈ OUTCOMES`를 점검 전용으로 남겼다(결과-B STO-02 행). 이 판단은 "사본을 지운 뒤 남은 것을 둔다"는 처분이었고, 어느 층이 맞는지는 판단하지 않았다.
- 제안: 레코드 하나로 판정되는 이 규칙들을 저장 계약(STO-02의 가족 검증기)으로 옮기고 점검 사본을 지운다.
- 실익:
  - 무효 상태가 게시되기 전에 거부된다. 규칙이 한 층에 모인다.
  - `inspect_state`는 적재된 상태만 받으므로(기준이 된 2라운드 STO-01), 점검 사본이 필요 없어진다.
- 비용과 위험:
  - 동작이 바뀐다. 현재 생산 경로가 이 규칙을 잠깐이라도 어기는 상태를 저장하면, 저장이 실패하기 시작한다.
  - 새 상태는 없다.
- 기능·커버리지 영향: 있음. 위반이 점검 결함에서 저장 거부로 바뀐다.
- 사용자 결정 관련: 없음
- 확신도: 추정. 외부 작업 상태를 바꾸는 생산자(`external.py`, `engine`의 외부 행동 경로)와 `outcome`을 쓰는 곳이 이 규칙을 항상 지키는지 전수 확인하면 확정된다.

#### STO-12 역할 입력 준비가 소비자 없는 원본 프롬프트 전체를 매번 렌더링한다
- 검토: 1
- 종류: 비용
- 좌표: `scripts/do_math/context_store.py:636-649`, `:726-727`
- 현상:
  - `prepare_role_input`은 줄이지 않은 문맥으로 `render(value)`를 늘 실행한다. 이 렌더링에는 역할 문서 본문과 문맥 전체의 JSON이 들어간다.
  - 결과는 초과(overflow) 분기와 반환값 `original_bytes`에만 쓰인다.
  - 반환값 `original_bytes`를 읽는 제품 코드는 없다.
- 근거:
  - 검색식 `original_bytes|fitted\[`: 엔진은 `prompt`, `overflow`, `artifacts`, `manifest`, `actual_bytes`, `reductions`, `context`만 읽는다(`engine.py:3196-3310`).
  - 시험의 `original_bytes`는 `fit_context` 반환(`test_context_store.py:120`, `test_research_reliability.py:350`)과 overflow 기록(`test_redesign_SURFACE.py:829`)을 읽는다.
- 제안: `render(value)`와 그 UTF-8 길이 계산을 `actual > limit` 분기 안으로 옮기고, 반환값의 `original_bytes`를 지운다.
- 실익: 역할 입력 하나마다 렌더링 세 번 중 한 번(문서 본문 수백 KB와 문맥 전체)과 인코딩 두 번이 준다. 규모는 측정하지 않았다.
- 비용과 위험: 한 함수 안에서 고친다. 새 상태는 없다.
- 기능·커버리지 영향: 없음
- 사용자 결정 관련: 없음
- 확신도: 추정. 소비자 부재는 확인했다. 절감 크기는 `role_input_preparation` 구간 시간을 전후 비교하면 확정된다.

### 검토 2

#### STO-13 딕셔너리 봉인 분기가 8d2ffd0에서 생산자를 잃은 뒤에도 남아 있다
- 검토: 2
- 종류: 잔재
- 좌표: `scripts/do_math/payloads.py:14-33`, `:46-53`, `:182`; `scripts/do_math/repository.py:30`, `:220`, `:772`; `scripts/tests/test_boundary_repairs.py:34-48`; `scripts/tests/test_initialization_efficiency.py:84-85`
- 현상:
  - `_eligible`은 긴 문자열 외에 `'foundation_profile'`을 가진 `manifest` 딕셔너리도 봉인한다. 주석은 이것을 "trust manifests"라고 부른다.
  - 이 분기를 위해 `FrozenDict`, `FrozenList`, `frozen()`이 있고, `repository`의 값 검사와 `canonical_json`이 `FrozenDict`를 구별한다.
  - 시험 둘은 이 분기만 검사하려고 가짜 `manifest` 가족을 등록하거나 직접 봉인한다.
- 근거:
  - 검색식 `foundation_profile`: 제품 일치는 `payloads.py:50` 하나이고, 나머지는 시험 2건이다.
  - `git log -S foundation_profile`로 보면 8d2ffd0가 신뢰 환경 manifest(`foundation_profile` 생산자)를 지웠다.
  - `payloads`를 import하는 제품 모듈은 `repository` 하나다.
- 제안:
  - `_eligible`을 "길이 `LIMIT // 6` 이상의 문자열"로 줄인다.
  - `FrozenDict`, `FrozenList`, `frozen()`을 지우고, `repository`의 구별을 `FrozenText`로 좁힌다.
  - 폐기한 기능만 검사하는 두 시험 부분을 지운다(기준 2절 5항).
- 실익: 제품 약 20행과 불변 컨테이너 형식 둘이 사라진다. 봉인 규칙이 "큰 문자열" 하나가 된다.
- 비용과 위험:
  - 루트 payload(토큰 없음)의 `_eligible` 호출은 `'manifest'`라는 자리표시 키를 쓴다(182행). 이 호출도 함께 고친다.
  - 새 상태는 없다.
- 기능·커버리지 영향: 있음. 폐기된 기능의 시험 두 부분이 사라진다.
- 사용자 결정 관련: 없음
- 확신도: 확인

#### STO-14 `state_errors`가 379a171에서 마지막 사용자를 잃었다
- 검토: 2
- 종류: 잔재
- 좌표: `scripts/do_math/state_checks.py:58-62`
- 현상: `state_errors(instance, runtime)`는 `inspect_state`의 blocked 메시지만 뽑는 감싸개다.
- 근거:
  - 저장소 전체 `git grep state_errors`의 결과는 정의 두 곳(스킬 정본과 `.agents` 미러)과 옛 증거 사본뿐이다.
  - 379a171이 마지막 시험 사용자(`test_state_checks`의 import와 단언)를 지웠다(`git show 379a171`).
- 제안: 함수를 지운다.
- 실익: 5행, 공개 이름 하나가 준다.
- 비용과 위험: 없음. 새 상태는 없다.
- 기능·커버리지 영향: 없음
- 사용자 결정 관련: 없음
- 확신도: 확인

#### STO-15 경량화가 소비자를 없앤 소형 잔재 셋
- 검토: 2
- 종류: 잔재
- 좌표: `scripts/do_math/git_store.py:42-46`, `:557`; `scripts/do_math/repository.py:251`, `:254`, `:433`, `:452`, `:713`; `scripts/do_math/record_schemas/__init__.py:346`, `:537`
- 현상과 근거:
  1. **`StateSnapshot`**: 필드가 `head` 하나뿐인 dataclass다. 379a171이 `research_tree`·`runtime_tree`를 지운 뒤(`git show 379a171 -- git_store.py`) 소비자는 `repository`의 `.head` 다섯 곳뿐이다.
  2. **`commit.gpgSign=false`**: 9b434f4 뒤 `_git`이 넘기는 이 설정의 소비자가 없다. 커밋을 프로세스 안에서 쓰고(`_write_commit`), 제품이 띄우는 git 명령은 `rev-parse`, `cat-file`, `ls-tree`, `update-ref`뿐이다(검색식 `commit-tree|hash-object|update-index|write-tree|read-tree`는 제품에서 docstring 1건). `user.name`·`user.email`·`core.hooksPath`는 `update-ref`의 reflog와 reference-transaction 훅 때문에 여전히 필요하다.
  3. **중복 import**: 8d2ffd0의 `json_digest` 교체가 `validate_semantics` 안에 `from ..file_io import json_digest`를 두 번 남겼다(346, 537, blame 8d2ffd0). 같은 함수 안에 `exact_content_hash`(468, 528)와 `ReviewEngineMixin`(457, 484)도 두 번씩 import된다.
- 제안:
  - `publish`와 `read_snapshot`은 `str | None`을 돌려준다.
  - `commit.gpgSign` 인자를 지운다.
  - `validate_semantics`의 import는 함수 머리에 한 번씩 둔다.
- 실익: 약 12행이 준다. 소비자 없는 설정이 사라진다.
- 비용과 위험: `repository`의 다섯 곳과 시험 5건(`StateSnapshot`)을 고친다. 새 상태는 없다.
- 기능·커버리지 영향: 없음
- 사용자 결정 관련: 없음
- 확신도: 확인

#### STO-16 S3 메모 가족의 키에 저장 바이트의 식별이 없어, 시험이 세 모듈의 사설 캐시를 비운다
- 검토: 2
- 종류: 비대
- 좌표: `scripts/do_math/repository.py:34-66`; `scripts/do_math/planning.py:31-32`, `:539-548`; `scripts/do_math/submission.py:108-130`; `scripts/tests/research_fixtures.py:783-795`
- 현상:
  - 대조 결과 메모 셋이 모두 `(git 디렉터리 경로, artifact 경로, sha256)`을 키로 쓴다. `VERIFIED_ARTIFACTS`(8d2ffd0), `planning._VALID_ARTIFACTS`(8d2ffd0), `submission._ISSUED_INPUTS`(379a171)다.
  - "저장된 바이트가 이 sha256과 맞다"는 결과는 실제 blob에 달려 있는데, 키에는 blob의 식별이 없다. 같은 경로에 저장소를 다시 만들면 옛 대조가 새 저장소에 적용된다.
  - 그래서 9b434f4의 `forget_repository_caches`가 세 모듈의 사설 전역 dict와 `_VALIDATED_READS`를 이름으로 지운다.
  - 기준 2절 11항은 이것을 "제품 내부 구현이 경계 밖으로 드러난 신호"로 본다.
  - 대조로, 9b434f4의 `_ARTIFACT_FACTS`와 `_VALIDATED_READS`는 키에 커밋 OID(내용 주소)가 들어 있어 경로 재사용에도 건전하다. 시험도 `_ARTIFACT_FACTS`를 지우지 않는다.
- 근거: 네 좌표의 원문. `forget_repository_caches`의 도입 커밋은 `git log -S`로 9b434f4다.
- 제안(둘 가운데 하나):
  - (가) 메모 키를 blob OID로 바꾼다. 스냅숏 트리의 항목 OID는 `GitStateStore._tree(commit).directories`에 이미 있다. 이 경우 `sealed_bytes`·`artifact_verified`가 스냅숏을 받아야 한다.
  - (나) 키는 두고 `repository`가 S3 메모 가족 전체를 한 번에 잊는 함수 하나를 소유한다. 다른 두 모듈은 `artifact_key`로 등록한다.
  - (가)가 기준 2절 9항(키가 결과를 정하는 입력을 모두 담는다)에 맞는다. (나)는 시험 도우미를 제품에 두는 형태라 기준 2절 4항과 긴장한다.
- 실익: 시험이 제품 사설 캐시 네 개를 이름으로 지우는 결합이 사라진다. (가)는 저장소 경로 재사용에도 건전해져 무효화 규칙이 필요 없다.
- 비용과 위험:
  - (가)는 `sealed_bytes` 호출자 약 15곳(엔진 13곳 어댑터 포함, `planning`, `submission`, `review_cycle`, `review_engine`, `retention`, `context_store`)의 인자를 바꾸는 넓은 변경이다.
  - 새 상태는 없다.
- 기능·커버리지 영향: 없음
- 사용자 결정 관련: 없음
- 확신도: 추정. 실익의 크기는 "운영 중 같은 경로에 저장소를 다시 만드는 흐름이 없다"는 판단에 달려 있다. 이 흐름이 없으면 결합 제거가 주된 실익이고, 있으면 (가)가 정확성 수리가 된다. `init`·복구 경로가 기존 경로에서 저장소를 지우고 다시 만드는지 확인하면 확정된다.

#### STO-17 artifact 사실 캐시에만 잠금이 있고, 같은 스레드에서만 쓰이는 나머지 전역 캐시에는 없다
- 검토: 2
- 종류: 비대
- 좌표: `scripts/do_math/repository.py:19`, `:138`, `:156`, `:166`, `:188`, 비교 대상 `:39`, `:97`, `:111`; `scripts/do_math/parallel.py:40-59`; `scripts/do_math/scheduler.py:82`, `:598`
- 현상:
  - 9b434f4는 `_ARTIFACT_FACTS`와 `_PUBLISHED_PARENTS`에 `threading.Lock`을 두었다.
  - 같은 모듈의 `VERIFIED_ARTIFACTS`, `_VALIDATED_READS`(순회와 `move_to_end`를 한다), `_RETAINED_READS`에는 잠금이 없다.
- 근거:
  - 작업 스레드에서 도는 함수는 `runner.run`, `verify_lean`/`verify_formal`, `check_environment`뿐이다(`scheduler.py:82`, `:598`, `engine.py:4290`, `lifecycle_engine.py:1182`, `:1311`).
  - 이 함수들이 부르는 모듈(`model_runner`, `formal`, `trust_validation`)은 `repository`에서 순수 함수(`canonical_json`, `exact_content_hash`)만 가져온다(검색식 `repository`).
  - 콜백은 `parallel.py`가 소유 스레드로 넘긴다(40-59행).
  - 따라서 저장소 캐시는 소유 스레드만 만진다.
- 제안: `_artifact_lock`을 지우거나, 저장소 전역 캐시가 소유 스레드 전용이라는 전제를 모듈 주석 한 곳에 적고 잠금 없이 통일한다.
- 실익: 약 5행이 준다. 잠금 여부가 캐시마다 다른 불일관이 사라진다.
- 비용과 위험: 앞으로 작업 스레드가 저장소를 읽게 되면 모든 캐시에 동기화가 필요해진다. 이 전제를 한 곳에 명시하는 것으로 막는다. 새 상태는 없다.
- 기능·커버리지 영향: 없음
- 사용자 결정 관련: 없음
- 확신도: 확인

#### STO-18 부모 동등(`==`) 생략이 값의 형을 구별하지 않아, 잘못된 형이 저장 검사를 건너뛸 수 있다
- 검토: 2
- 종류: 공백
- 좌표: `scripts/do_math/repository.py:396`, `:861`, `:890-891`; `scripts/do_math/state_contract.py:163`; `scripts/do_math/payloads.py:67-95`; 출처 `C:/math/임시/경량화-조사-2026-09-26/결과-B.md` 4절 3항
- 현상:
  - 379a171 뒤 후보 검증은 상태 전체의 값 영역 검사를 하지 않는다. 부모와 `==`인 레코드는 두 가지를 건너뛴다.
    - 스키마 검사(`state_contract.py:163`)
    - 직렬화와 그 안의 값 영역 검사(`repository.py:890-891`, 부모 파일 바이트 재사용)
  - 파이썬에서 `1 == 1.0`, `1 == True`다. 따라서 생산자가 정수 자리에 `1.0`이나 `True`를 넣어도, 부모 값과 같으면 검사를 건너뛰고 부모 바이트가 게시된다.
  - 그 결과 메모리와 `_remember_published` 캐시에는 잘못된 형이 남고, 디스크에는 정수가 남는다. 그 레코드가 나중에 다른 이유로 바뀌면 관계없는 저장에서 `floating-point numbers are not permitted`로 늦게 실패한다.
  - 379a171 전에는 전체 값 검사가 같은 저장에서 즉시 거부했다.
- 근거:
  - 세 좌표의 원문.
  - 결과-B는 이 위험을 "생산 코드가 형만 바꾸는 경로는 찾지 못했다"는 미확인으로 남겼다. 이후 확인 기록은 없다.
  - 스키마에서 정수와 불리언을 함께 허용하는 필드는 `_ACTION.required` 하나다(`schemas.py:114`).
- 제안:
  - 저장마다 모든 노드를 이미 방문하는 `seal_large`의 순회(`payloads.py:67-95`)에서 `float`를 만나면 거부한다. 형 판정은 순회가 이미 하고 있어 추가 비용이 거의 없다.
  - 불리언/정수 혼동은 해당 필드가 하나뿐이므로 공백으로 명시해 둔다.
- 실익: 값 영역 위반이 생긴 저장에서 바로 드러난다. 캐시와 디스크가 형으로 어긋날 여지가 준다.
- 비용과 위험: 한 함수에 한 분기를 더한다. 새 상태는 없다.
- 기능·커버리지 영향: 없음
- 사용자 결정 관련: 없음
- 확신도: 추정. 제품이 저장 상태에 `float`나 정수 자리의 `bool`을 쓰는 경로가 있는지 전수 확인해야 한다. 실행 기록의 시간 계산, `/` 나눗셈 결과를 상태에 넣는 곳을 찾으면 된다. 경로가 없으면 이 후보는 예방 조치로 남는다.

## 4. 보존 판정

- **`_ARTIFACT_FACTS`·`_PUBLISHED_PARENTS`**(`scripts/do_math/repository.py:127-194`, `:536-583`, 9b434f4): 기준 4.2의 세 확인을 통과한다.
  - 키 `(git 디렉터리, 경로)`와 그 경로가 존재함을 안 head로 결과를 정한다. 조회는 이 프로세스가 그 head에서 게시한 계보에서만 성립한다.
  - 기존 번들은 바뀌거나 지워지지 않으므로(`git_store.py:508-517`) 무효화가 필요 없다.
  - 커밋 OID가 내용 주소라 시험의 경로 재사용에도 건전하다. 시험도 이 캐시를 지우지 않는다.

  남은 문제는 잠금 불일관(STO-17)뿐이다.
- **`_VALIDATED_READS`와 `retain_reads`**(`scripts/do_math/repository.py:92-125`): 키가 커밋 OID와 계약이라 건전하다. 살아 있는 실행의 입력 스냅숏만 LRU 밖에 두어 메모리를 필요한 head로 제한한다. LRU를 크게 늘리는 대안은 전체 상태 사본을 더 오래 쥐므로 택하지 않는다.
- **`check_path_segment`의 `lru_cache`**(`scripts/do_math/git_store.py:82-97`): 인자 하나의 순수 함수다. 예외는 캐시되지 않으므로 거부 판정이 가려지지 않는다.
- **`file_io.cached_sha256`의 `_hashed`**(`scripts/do_math/file_io.py:250-264`): 이음새 계약 2절의 정본이다. 정착한 지문만 재사용한다. 스레드 풀(`trust_inventory`)의 동시 사용도 dict 원자 연산으로 충분하다.
- **9b434f4의 프로세스 안 객체 쓰기**(`scripts/do_math/git_store.py:256-395`):
  - 기준 2절 12항의 원자성은 그대로다. 참조 이동은 `update-ref` CAS 하나이고, 객체는 임시 파일, fsync, 이름 바꾸기 순서로 놓인다.
  - W-git 노드의 남은 위험(기존 객체 freshen 생략, 저장소 로컬 `core.fsync` 등 무시, DST 미확인)은 plumbing만 쓰는 사용 조건에서 받아들인 경계다. 후보로 올리지 않는다.
- **`retention._inventory`의 `marks`와 `cached_sha256`**(`scripts/do_math/retention.py:156-186`): 둘 다 지문으로 해시를 재사용하지만 합칠 수 없다. `_inventory`는 물리 경계 검사로 읽은 바이트를 보관용으로 돌려주고, 그 증명을 재사용한다. `cached_sha256`은 밖에서 계산한 해시를 받아 둘 방법이 없다.
- **`retention.PROTECTED_REFERENCE_KEYS`와 `record_schemas.REFERENCES`**(`scripts/do_math/retention.py:23-27`, `scripts/do_math/record_schemas/__init__.py:24-64`): 서로 다른 개념이다. 두 어휘를 대조하면 무결성 표에만 있는 필드가 41개이고, 대부분 `execution_id`·`owner_activity_id` 같은 실행 연결이다. 이것을 보호 폐포에 넣으면 모든 실행 폴더가 보호되어 정리가 불가능해진다.
- **`record_schemas.install`의 가족 배치 표**(`scripts/do_math/record_schemas/__init__.py:115-124`): 루트·형태 배치를 `RECORDS` 정의 옆으로 옮겨도 행 수와 오류 여지가 거의 같다. 실익이 없다.
- **`file_io.atomic_replace`의 재시도**(`scripts/do_math/file_io.py:18-27`): 시간 지연 재시도지만 경쟁을 가리는 임시방편이 아니다. POSIX 의미 교체는 공유 삭제로 연 읽기를 이미 허용한다. 재시도는 공유 삭제 없이 파일을 잡는 외부 프로그램(검사기·색인기)의 일시 잠금(winerror 5·32·33)에 대한 것이고, 같은 이름 바꾸기만 반복한다.
- **`context_store`의 `_safe_path`·`_read_stable`·`_excluded`**(`scripts/do_math/context_store.py:44-111`): 네 모듈이 이 사설 이름을 가져다 쓰지만, 정의는 하나다. 이음새 원칙에 맞는 공유이고, 사설 표기만 문제다(5절에 적음).
- **2라운드 조사 `STO.md` 3절의 보존 판정 12건**: 현재 원문에서 근거가 틀렸다는 사실을 찾지 못했다. 다시 제안하지 않는다.

## 5. 영역 밖 관찰

- ENG `scripts/do_math/engine.py:290`: `_control_result`가 `store._git(...)`과 `store._store._validate_oid(...)`로 저장소와 Git 저장의 사설 메서드를 부른다.
- ENG `scripts/do_math/engine.py:4003-4005`: 엔진이 `retention._run_path`와 `retention._inventory`(사설)를 직접 부른다.
- IO·RES `scripts/do_math/observations.py:15`, `:414`, `scripts/do_math/control_transport.py:337`, `scripts/do_math/formal_preview.py:7`: `context_store`의 사설 함수 `_safe_path`, `_read_stable`, `_excluded`가 네 모듈의 공유 작업 공간 규칙이다. 이음새 계약 11절 표에 없다.
- HIS `C:/math/docs/do-math/검사-경량화-이음새-계약.md:109`: 4절이 없어진 `self._state_generation`(R12)을 여전히 설명한다. 현재 무변경 판정은 `published_state` 비교다. 결과-B 3절이 이 갱신을 요청했지만 반영되지 않았다.
- HIS 같은 문서 3절·11절: 9b434f4가 더한 `retain_reads`(엔진이 저장소에 보존할 head를 알려 주는 이음새), `_ARTIFACT_FACTS`, 프로세스 안 객체 쓰기가 정본 목록에 없다.
- TSB `scripts/tests/research_fixtures.py:792`: `forget_repository_caches`가 `_VALIDATED_READS`도 지운다. 이 캐시의 키는 커밋 OID라 경로 재사용에도 건전하므로, 지울 필요가 없다(STO-16과 함께 볼 것).
- REV·IO `scripts/do_math/contracts.py:91`, `:98`, `:110`, `scripts/do_math/cli.py:534`, `:577`, `:635`, `scripts/do_math/control_contracts.py:29`: 응답 계약 `do-math-cli/5`와 `schema_version: 5` 리터럴이 여러 곳에 있다(STO-08의 짝).
- RUN `scripts/do_math/budget.py:204`, `scripts/do_math/execution_profiles.py:49`, `:66`: 레코드 판본 표지의 생산·검사(STO-09의 짝).

## 6. 작업 기록

- 기준 6절에 따라 graphify는 쓰지 않았다.
- 저장소를 바꾸지 않는 확인 명령 넷을 실행했다. 모두 `C:/math/.claude/skills/do-math/scripts`에서 실행했다.
  1. 계약 복사 비용: `python -c "…StateContract.default()를 50회…"` → `default() ms 14.569`
  2. manifest·검증기 비용: `python -c "c=StateContract.default(); c.manifest(); [f.checker for f in c.families()]"`에 시간 측정 → `manifest ms 6.283`, `all checkers ms 6.574 100`
  3. 스키마 필드 이름 전수 검색(STO-05): `RECORDS`·`RESEARCH_FIELDS`·`RUNTIME_FIELDS`를 재귀로 훑은 짧은 스크립트 → `933 names; 38 with no quoted occurrence outside record_schemas`
  4. 영역 모듈 정의의 참조 계수(AST로 최상위 정의·메서드 이름을 모아 이름 경계 정규식으로 전체 `.py`를 셈) → 제품 참조 0은 `_canonical_object`와 `state_errors` 둘. `records`, `register_family`처럼 흔한 이름은 이 방식으로 판정할 수 없어 따로 검색했다.
- 접근을 바꾼 지점이 셋이다.
  - `retention._inventory`의 `marks`를 `cached_sha256`으로 합치는 후보를 검토했다. `_inventory`가 보관용 바이트를 함께 돌려줘야 하고 `cached_sha256`에 해시를 넣어 둘 방법이 없어, 보존으로 돌렸다.
  - 9b434f4의 `_ARTIFACT_FACTS`를 처음에는 `비대` 후보로 보았다. 키가 커밋 계보에 묶여 건전하고, 그 실익(방금 게시한 artifact의 git 재독 회피)을 반박할 측정이 없어 보존으로 돌리고, 잠금만 STO-17로 남겼다.
  - 보호 참조 어휘와 무결성 참조 표의 통합을 검토했다. 두 집합을 대조해 실행 연결 필드가 의도적으로 빠져 있음을 확인하고 보존으로 돌렸다.
- 예상과 달랐던 결과가 넷이다.
  - 런타임 가족 등록 기능에 제품 호출자가 전혀 없었다(STO-01).
  - 닫힌 스키마에 어디에서도 쓰이지 않는 이름이 38개 있었다(STO-05).
  - `inspect_current_state`의 `derived_readiness` 분기는 2라운드의 enum 이동 뒤 도달할 수 없게 되었다(STO-04).
  - 시험 도우미가 지우는 캐시 가운데 `_VALIDATED_READS`는 지울 필요가 없고, 지우지 않는 `_ARTIFACT_FACTS`는 실제로 지울 필요가 없었다(STO-16, 5절).
- 작문: 프로젝트 지침에 따라 `write-for-reader` 스킬과 참조 문서를 적용했다. 그러나 그 독해 절차(`writing_flow.py begin/read`)는 합의·독자 파일과 `.codex/writing-flow/` 상태를 새로 쓴다. 기준 7절("쓰는 파일은 파견문이 정한 산출 파일 하나")과 충돌하므로 실행하지 않았다. 별도 독해 검증은 하지 않은 상태다.
