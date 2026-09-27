# ENG — 엔진 영역 정리 검토

검토 기준 시점은 main 커밋 `9b434f4`의 작업 트리다. 경로는 따로 적지 않으면 `C:/math/.claude/skills/do-math/` 기준의 상대 경로다. 저장소 파일은 이 산출 파일 말고는 하나도 고치지 않았고, 시험은 실행하지 않았다.

## 1. 읽은 범위

전문을 읽은 파일은 다음과 같다.

| 파일 | 행 수 |
|---|---|
| `C:/math/임시/do-math-정리-검토-2026-09-27/기준.md` | 238 |
| `AGENTS.md` | 11 |
| `C:/math/docs/do-math/검사-경량화-이음새-계약.md` | 245 |
| `scripts/do_math/engine.py` | 4,538 |
| `C:/math/임시/경량화-조사-2026-09-26/ENG.md` | 705 |
| `C:/math/임시/경량화-조사-2026-09-26/결과-이음새.md` | 283 |
| `C:/math/임시/시험-경량화-2026-09-26/작업자-노드/W-eng-M-0350.md` | 36 |
| 커밋 `9b434f4`의 `engine.py` 변경 | 91행 변경 전체 |

부분만 읽은 자료는 다음과 같다.

- **결과-A~E**: `engine`으로 검색해 걸린 항목만 읽었다. 대상은 결과-A 14-18·30-63행, 결과-B 19-37·53-56·87·102행, 결과-C 19-65·97-158행, 결과-D 16-29·41-47·88-110행, 결과-E 9·32-49·115-129행이다. 결과-K시험은 14-26·184-192행을 읽었다.
- **커밋 `8d2ffd0`·`379a171`의 `engine.py` 변경**: 더해진 줄과 hunk 머리는 전부 읽었다. 지워진 줄은 전문을 읽지 않았다. 대신 지워진 `def`와 모듈 상수 이름을 모두 뽑아, 그 이름이 현재 코드와 문서에 남아 있는지 검색했다. 걸린 이름은 `_evaluation_context_for`, `_input_artifacts`, `_review_observation_source`뿐이었다. 이 셋은 새 서명으로 다시 정의된 함수라 잔재가 아니다.
- **이음새를 따라 읽은 제품 모듈**:
  - `repository.py` 114-134·700-720
  - `git_store.py`: `_git`·`_validate_oid` 정의와 호출 행만
  - `question_engine.py` 1-35
  - `planning.py` 232-242·348-366·440-460·605-625
  - `task_contracts.py` 27-45
  - `control_contracts.py` 148-172·192-202
  - `governance_engine.py` 38-112
  - `governance.py` 830-842
  - `lifecycle_engine.py` 160-175·400-408·711-740·770-790·815-817·1095-1132·1196-1202·1262-1290·1313-1425
  - `scheduler.py` 15-35·75-120·165-180
  - `execution_profiles.py` 24-30·200-240·252-272·292-324
  - `model_runner.py` 50-66·160-200
  - `initialization.py` 205-264
  - `knowledge_io.py` 95-116
  - `record_schemas/schemas.py` 45-55·109-150·265-280
  - `record_schemas/__init__.py` 118-128·145-190
  - `submission.py` 1234-1266
  - `reporting.py` 140-182
  - `retention.py` 40·156·204-222행 부근
  - `file_io.py` 267-281
  - `repair_execution.py` 90-140
  - `activities.py` 152-177
  - `launch.py` 44-65
  - `academic.py` 232-262
  - `contracts.py` 270-298
  - `cli.py` 218-240·320-340
- **문서와 시험**:
  - `SKILL.md`의 역할 문서 지도 블록
  - `README.md` 226-250·386-396
  - `references/CLI-실행-계약.md` 154-176·258·289행
  - `tests/research_fixtures.py` 173-203
  - `tests/test_performance_repairs.py` 220-275
  - `tests/test_redesign_PROFILES.py` 760-775
  - `C:/math/docs/do-math/경량화-설계-2026-09-26.md`: 표의 ENG 행과 5절
  - `C:/math/docs/do-math/검사-경량화-설계-2026-09-26.md` 237-284
  - 2라운드 조사 파일 `RUN`·`STO`·`REV`·`RES`·`IO`·`OPS`·`TST`.md의 3절 가운데 `engine`이 걸린 보존 판정

파견문이 정한 파일 가운데 읽지 못한 것은 없다. 4.1·4.2절의 종류는 모두 검토했다.

## 2. 영역 판정

`engine.py`는 세 경량화의 방향성을 대부분 따른다. 공유 정본(`sealed_bytes`, `issued_input`, `config_schema`, 역할 집합, 제어 어휘)을 참조하고, 재적재·보존·무변경 판정도 한 경로로 모았다. 그래도 같은 규칙이 두 곳에 남아 이미 어긋난 이음새가 몇 개 있다. 운영자 보호 설정 키(ENG-01), 실행의 effort 출처(ENG-02), status 투영(ENG-03), 미리보기 응답(ENG-04)이 그 예다. 경량화가 더하고 치우지 못한 것도 남았다. 시험에만 이득이 있는 프로세스 전역 캐시(ENG-19)와 시험 대역을 위한 제품 분기(ENG-20)가 여기에 든다. 책임 경계에 대한 판정은 다음과 같다. 대기열·실행 수명 구동(`_call_steps`)·상태 게시(`_save`/`_reload`)·제어 inbox 적용·결과 수신(`_receive_submission`)은 엔진에 남는 것이 맞다. 반면 다른 모듈이 소유해야 할 지식은 옮기는 것이 맞다. 대상은 공용 도우미와 설정 기본값(ENG-10), git 명령과 정리 보관(ENG-09), status 투영(ENG-03), 형식 검사의 Lean 기계 실행 골격(ENG-08), 초기 상태(ENG-06)다. 파일을 크기만 보고 나누는 방안은 권하지 않는다. 믹스인이 모두 `self` 상태를 공유하므로, 이음새를 없애지 않는 분할은 결합을 줄이지 못하고 흩어 놓기만 한다.

검토했고 없음: 파생상태, 문서, 결함

## 3. 후보

### 검토 1

#### ENG-01 운영자가 바꿀 수 없는 설정 키 집합이 생산자와 수신자에서 다르다
- 검토: 1
- 종류: 이음새
- 좌표: `scripts/do_math/engine.py:355-362`, `scripts/do_math/governance_engine.py:51-53`
- 현상: 공개 `control()`은 운영자 출처의 configure 가운데 `session_limits`·`tier_models`·`role_tiers`·`claude_only_assigned_model` 네 키의 변경을 거부한다(`engine.py:360-362`). inbox를 적용하는 `_configure_candidate`는 여기에 `host_resources`를 더한 다섯 키로 거부한다(`governance_engine.py:51-53`). 그 결과 운영자가 `host_resources`를 바꾸는 요청은 CLI 접수 때 받아들여지고, 적용 때 거부 영수증이 된다.
- 근거: 검색식 `grep -rn "claude_only_assigned_model" scripts/do_math`의 결과 가운데 보호 집합을 이루는 곳은 두 곳이고, 원소가 다르다. 두 규칙은 같은 개념, 곧 "운영자 권한으로 바꿀 수 없는 자원·모델 배정 설정"이다. 기준 2절 1항이 없애려는 "양쪽이 따로 구현하고 같기를 기대하는 구조"에 해당하며, 이미 어긋났다.
- 제안: 보호 키 집합을 상수 하나로 둔다. 위치는 설정 절 정본이 있는 `record_schemas` 또는 `control_contracts`다. 두 검사가 모두 이 상수를 참조한다. 원소는 수신 쪽 다섯 키를 기준으로 한다.
- 실익: 정의 2벌이 1벌로 준다. 접수된 요청이 적용에서 반려되는 경로가 사라진다.
- 비용과 위험: 두 파일에서 몇 행을 고친다. 새 상태나 수명은 생기지 않는다. 운영자가 `host_resources`를 바꾸는 요청은 접수 단계에서 거부된다. 이것은 지금 적용 단계에서 일어나는 거부를 앞당길 뿐이다.
- 기능·커버리지 영향: 있음. 운영자의 `host_resources` configure가 접수 거부로 바뀐다. 최종 효과는 같다.
- 사용자 결정 관련: 없음
- 확신도: 확인

#### ENG-02 AI 실행의 effort가 고정 프로필과 현재 설정 두 곳에서 정해진다
- 검토: 1
- 종류: 이음새
- 좌표: `scripts/do_math/engine.py:641-642`, `:3091`, `:3300`, `:3413-3414`, `scripts/do_math/model_runner.py:59-61`, `scripts/do_math/execution_profiles.py:252-256`, `:319-324`
- 현상: 정본은 `_register_execution`이다. 이 함수는 실행의 `model`·`effort`를 선택된 프로필의 `ai`에서 정한다(`:642`). 그런데 `_call_steps`가 실행 기록을 다시 만들면서 `effort`를 `config["effort"]`로 덮는다(`:3300`). 여기서 `config`는 `{**instance["config"], **runtime_config(profile)}`이다. `runtime_config`에는 effort가 없으므로(`execution_profiles.py:319-324`), 결국 인스턴스의 현재 설정값이 쓰인다. 러너는 이 값을 받아 고정 프로필의 `ai.effort`와 비교하고, 다르면 `runner assignment differs from the pinned execution profile`을 낸다(`model_runner.py:59-61`).
- 근거: 옛 판본의 프로필은 등록된 채 남는다(`apply_editions`, `execution_profiles.py:253`). 과제는 `profile_refs`로 판본을 고정한다. configure는 호스트 변경일 때만 과제 프로필을 다시 준비하게 한다(`governance_engine.py:88-103`). 따라서 effort만 바꾸는 configure 뒤에는, 옛 판본을 고정한 과제의 연구 수행에서 두 값이 갈린다. 원문을 추적한 결과이며 실행으로 재현하지는 않았다. `:3300`은 `9e5e120`에서 왔고 세 경량화가 들인 줄은 아니다.
- 제안: `:3300`에서 `"effort": config["effort"]`를 지운다. 실행의 effort는 `_register_execution`이 프로필에서 정한 값 하나만 쓴다. `:3413-3414`의 러너 인자는 이미 `execution["effort"]`를 읽으므로 따로 고칠 것이 없다.
- 실익: 같은 사실의 출처 2개가 1개로 준다. effort를 바꾸는 configure 뒤에 고정 과제의 연구 수행이 러너 검사에서 실패하는 경로가 사라진다(추정).
- 비용과 위험: 1행을 고친다. 새 상태는 생기지 않는다. 고정 프로필의 effort를 따르는 것은 러너 검사의 현행 계약과 같다.
- 기능·커버리지 영향: 있음. 설정값과 고정 프로필이 다를 때, 실행 기록의 `effort`가 고정 프로필 값이 된다.
- 사용자 결정 관련: 없음
- 확신도: 두 출처의 존재는 확인이다. 실패 경로는 추정이며, effort만 바꾸는 configure 뒤 기존 과제를 한 번 실행하면 확정된다.

#### ENG-03 `status` 명령의 JSON이 `--snapshot` 유무에 따라 서로 다른 두 투영에서 나온다
- 검토: 1
- 종류: 경계
- 좌표: `scripts/do_math/cli.py:328-335`, `scripts/do_math/engine.py:1498-1559`, `scripts/do_math/reporting.py:149-178`, `README.md:233-248`
- 현상: `status`에 `--snapshot`이 없으면 `ResearchEngine.status()`가 약 50개 필드를 만든다. `--snapshot`이 있으면 `reporting.snapshot_report`가 약 15개 필드를 만든다. README의 필드 표(`knowledge`, `questions`, `budget`, `pending_controls`, `user_pause`, `waiting_actions`, `external_operations`, `active_trust_environment`)는 앞쪽에만 있다. 반대로 `cleanup_failures`, `host_observation`은 뒤쪽에만 있다. `research_effectiveness`는 두 곳에 있지만 사유 문구가 다르다. `engine.status(snapshot=...)`의 `snapshot` 인자는 제품 호출자가 없다. 호출자는 `cli.py:331`, `scheduled_operator.py:222`, `engine.py:1591·1595`이고 모두 인자 없이 부른다.
- 근거: 원문 대조. 검색식 `grep -rn "\.status(\|snapshot_report" scripts/do_math`로 제품 호출자를 전수 확인했다.
- 제안: status 투영을 함수 하나로 둔다. 이 함수는 한 snapshot의 저장 상태에서 필드를 계산하고, 호스트 관찰(`operation_progress`, `pending_controls`, 관찰 시각)은 호출자가 넘기게 한다. 이 모양은 이미 `snapshot_report`의 설계이며, 위치는 `reporting`이다. `engine.status`는 호스트 사실을 모아 이 함수를 부르는 얇은 층이 되고, 쓰이지 않는 `snapshot` 인자는 지운다.
- 실익: 한 명령의 JSON 모양이 하나가 된다. 필드 정의 약 60행 중 겹치는 부분이 한 벌로 준다. README 표와 어긋나는 경로가 사라진다.
- 비용과 위험: `engine.py`, `reporting.py`, `cli.py`를 고친다. 사람용 렌더러 두 개(`cli._human_status`, `reporting.render_human_report`)도 하나로 맞출지 함께 정해야 한다. `scheduled_operator`가 읽는 키(`provider_waits` 등)는 유지해야 한다.
- 기능·커버리지 영향: 있음. `status --snapshot --json`의 필드 집합이 커진다.
- 사용자 결정 관련: 없음
- 확신도: 확인

#### ENG-04 후보 미리보기 응답 `do-math-candidate-preview/5`를 두 모듈이 따로 만든다
- 검토: 1
- 종류: 이음새
- 좌표: `scripts/do_math/engine.py:2323-2326`, `scripts/do_math/submission.py:1259-1265`
- 현상: 봉인 검사가 포착 부적격이면 엔진이 직접 응답을 만든다. 이 응답에는 `check_id`·`schema_ref`·`input_hashes`가 없고, `not_checked`가 `["candidate_application", "mathematical_meaning", "Lean"]`이다. 정상 경로의 `submission.preview_submission`은 앞의 세 필드를 넣고 `not_checked=["mathematical_meaning", "Lean", "future_application_currentness"]`를 쓴다. 두 곳이 같은 계약 ID를 문자열로 따로 적는다.
- 근거: 검색식 `grep -rn "do-math-candidate-preview/5" --include=*.py`는 제품 2건(위 두 좌표)과 시험 1건을 찾았다. 이 응답의 스키마는 따로 없으므로 두 생산자가 모양을 따로 정한다.
- 제안: 포착 부적격 분기를 `submission.preview_submission`에 넣는다. 이 함수는 이미 `check`를 받는다. `check["capture_eligible"]`이 거짓이면 같은 응답 골격에 후보 적용 없이 채워 돌려준다. 엔진은 결과를 그대로 넘긴다.
- 실익: 응답 계약의 정의가 1벌이 된다. 엔진에서 4행과 계약 문자열 사본 1개가 준다.
- 비용과 위험: 두 파일을 고친다. 새 상태는 없다. 부적격 응답에 필드가 더해진다.
- 기능·커버리지 영향: 있음. 부적격 미리보기 응답에 `check_id` 등이 생기고 `not_checked` 목록이 통일된다.
- 사용자 결정 관련: 없음
- 확신도: 확인

#### ENG-05 외부 작업의 학술 결박이 세 번 되풀이되고, 인자를 인스턴스 속성으로 몰래 넘긴다
- 검토: 1
- 종류: 이음새
- 좌표: `scripts/do_math/engine.py:3662-3681`, `:4051-4060`, `scripts/do_math/lifecycle_engine.py:711-733`, `:815-817`
- 현상: `_apply_extensions`가 외부 요청을 준비하는 과정은 세 단계다.
  1. 엔진이 `self._external_preparation_binding`에 결박을 넣고 `_external_control`을 부른 뒤 되돌린다(`:3665-3673`). 인자를 속성으로 전달하는 방식이다.
  2. `lifecycle_engine._external_control`은 그 속성을 읽어 `academic_binding`을 넣는다. 학술 grant이거나 결박이 있으면 `bind_external_prerequisite`로 `academic_basis`까지 넣은 뒤 `_validate_external`을 부른다(`lifecycle_engine.py:725-733`).
  3. 엔진이 `_validate_external`을 재정의해, 같은 조건에서 `academic_binding`을 다시 넣고 `academic_basis`가 없을 때만 다시 결박한다(`engine.py:4051-4060`). 호출이 돌아오면 엔진이 `entry["academic_binding"]`을 세 번째로 넣는다(`:3676-3679`).
- 근거: 외부 작업을 만드는 곳은 `prepare_operation` 호출 `lifecycle_engine.py:724` 하나다. 검색식 `grep -rn "prepare_operation(" scripts/do_math`의 결과는 정의, 이 호출, `submission.py:965`의 미리보기용 호출이다. 이 경로는 결박과 `academic_basis`를 `_validate_external` 전에 이미 채운다. 따라서 엔진 재정의의 재결박 조건 `not operation.get("academic_basis")`는 prepare 경로에서 참이 될 수 없다. 다른 호출(`lifecycle_engine.py:783`, `:1270`, `:1284`)에서는 `_external_preparation_binding`이 `None`이다. 학술 grant의 작업은 prepare 때 이미 `academic_basis`를 가진다. 검색식 `grep -rn "_external_preparation_binding\|_validate_external" scripts/do_math`는 제품 11건을 찾았고 모두 위 좌표다.
- 제안: 결박을 `_external_control`의 명시 인자(예: `config["academic_binding"]`)로 넘긴다. 결박 규칙은 `lifecycle_engine._external_control` 한 곳에만 둔다. 엔진의 `_validate_external` 재정의와 `:3676-3679`의 사후 대입, 속성 저장·복원을 지운다.
- 실익: 엔진에서 약 20행이 준다. 같은 규칙 3벌이 1벌이 되고, 암묵 전달용 인스턴스 속성이 사라진다.
- 비용과 위험: `engine.py`와 `lifecycle_engine.py`를 고친다. 새 상태는 없다. 재정의가 잡던 경로가 정말 없는지는 원문 추적으로만 확인했다.
- 기능·커버리지 영향: 없음
- 사용자 결정 관련: 없음
- 확신도: 확인. 동적 경로를 포함해 `_validate_external` 호출자 넷을 모두 원문으로 추적했다.

#### ENG-06 초기 상태를 두 모듈이 나눠 만들고, 같은 필드를 두 번 쓰며, 별칭 `CONTRACT`가 남아 있다
- 검토: 1
- 종류: 이음새
- 좌표: `scripts/do_math/engine.py:64`, `:251-264`, `scripts/do_math/initialization.py:242-262`, `scripts/tests/test_query_records.py:17`
- 현상: `initialize_state`는 인스턴스의 `feature_version`·`contract_id`·`grants={}`와 런타임의 `feature_version`·`contract_id`·`question_links=[]`를 이미 넣는다. `engine.initialize`는 이 필드들을 다시 넣는다(`:258`, `:260`, `:264`). 여기에 `cycles`·`processed_controls`·`updated_at`·`reservations`·`provider_waits`를 더한다. `CONTRACT = STATE_CONTRACT_ID`는 이 두 줄과 시험 하나만 쓰는 이름 별칭이다.
- 근거: 두 원문 대조. 검색식 `grep -rnw "CONTRACT" --include=*.py`에서 `STATE_CONTRACT`를 뺀 결과는 제품 2건(`engine.py:258`, `:260`)과 시험 1건이다.
- 제안: 런타임 초기 필드를 모두 `initialize_state`로 옮기고 엔진의 재대입을 지운다. `CONTRACT` 별칭을 지우고, 시험은 `STATE_CONTRACT_ID`를 쓴다. 엔진의 `initialize`에는 설정 결합, 프로필 판본 채택, 원자료 보관, 게시만 남긴다.
- 실익: 초기 상태의 정의가 한 모듈에 모인다. 약 5행과 별칭 하나가 사라진다.
- 비용과 위험: 파일 3개를 고친다. 9b434f4의 시험 시작 상태 템플릿이 실제 `initialize` 결과에서 만들어지는지는 확인하지 않았다. 템플릿이 필드를 따로 적었다면 함께 고쳐야 한다.
- 기능·커버리지 영향: 없음(같은 초기 상태)
- 사용자 결정 관련: 없음
- 확신도: 확인

#### ENG-07 `query`의 기록 가족 이름이 조건 문법의 가족 어휘와 다르게 반쯤만 별칭된다
- 검토: 1
- 종류: 불일관
- 좌표: `scripts/do_math/engine.py:431-440`, `scripts/do_math/planning.py:352-362`, `references/초기화-운전.md:169`, `:174`, `:212`, `references/CLI-실행-계약.md:579`
- 현상: `_query_record`는 저장 가족 이름 12개만 공개 이름(`trust-environment`, `review-cycle`, `grant` 등)으로 바꾼다. 나머지는 저장 이름 그대로 낸다(`execution_profiles`, `formal_results`, `identity_assessments`, `goal_judgments`, `governance_sources`, `capability_evidence`, `intent_imports` 등). 조건 문법의 정본 `planning.RECORD_FAMILIES`는 같은 가족을 `execution-profile`, `formal-result`, `identity-assessment`, `goal-judgment`, `governance-source`로 부른다. 그래서 운전 문서도 `--kind trust-environment`와 `--kind execution_profiles`를 섞어 쓴다.
- 근거: 두 표를 대조했다. 검색식 `grep -rn -- "--kind [a-z_-]*" references README.md`는 12건을 찾았고, 두 방식이 섞여 있다.
- 제안: `query`의 공개 가족 이름을 `RECORD_FAMILIES`의 역표(저장 이름 → 공개 이름)에서 파생한다. 표에 없는 가족(`question_links` → `question` 등)만 엔진에 둔다.
- 실익: 공개 가족 어휘가 1벌이 된다. 조회하는 AI·사용자가 가족마다 이름 형식을 외울 필요가 없어진다.
- 비용과 위험: 공개 출력이 바뀐다. `formal_results`가 `formal-result`가 되는 식이다. 문서의 `--kind` 예시를 함께 고쳐야 한다.
- 기능·커버리지 영향: 있음. `query --kind` 값과 결과의 `family` 값이 바뀐다.
- 사용자 결정 관련: 없음
- 확신도: 확인

#### ENG-08 두 Lean 기계 실행(형식 검사, 신뢰 검사)의 골격이 두 모듈에 따로 있다
- 검토: 1
- 종류: 경계
- 좌표: `scripts/do_math/engine.py:4288-4445`, `scripts/do_math/lifecycle_engine.py:1313-1425`, `:1099-1113`
- 현상: `_formal_steps`(엔진)와 `_trust_check_steps`(`lifecycle_engine`)는 같은 순서로 일한다.
  1. `_register_execution`으로 실행을 등록한다.
  2. 정지 판정 클로저를 만든다. 판정 기준은 실행기 정지, 실행 정지 요청, 권한, 환경 변경, 근거 변경이다.
  3. `machine_invocation(..., on_started=self._machine_started)`와 같은 검증기 인자 묶음을 만든다. 인자는 `source`, `declarations`, `workspace`, `environment`, `binding`, `verifier`, `allowed_axioms`, `launch_ticket`, `should_stop`이다.
  4. 시작 전 정지를 확인한다.
  5. `yield`로 계산을 넘긴다.
  6. 반환 원문을 새 BA 묶음에 보존한다(`result_ref`와 `raw_result_ref`를 같게 두었다가 나중에 교체한다).
  7. 정지를 다시 확인한다.
  8. `_apply_trust_rebind`를 적용한다.
  9. `MACHINE_OUTPUT_RECEIPT`를 만든다.

  종료 처리는 둘이 다르다. 신뢰 검사는 `_end_machine_execution`(`mark_returned`, `release_or_hold`, 전이)을 쓰고, 형식 검사는 `release_or_hold`와 전이를 직접 쓴다.
- 근거: 두 원문 대조. 세 경량화는 이 골격을 합치지 않았다. 2라운드 조사 ENG-06은 동기 경로만 다뤘다.
- 제안: Lean 기계 실행의 공통 골격(인자 조립, 원문 보존, 종료 처리)을 기계 실행을 소유한 `lifecycle_engine` 한 곳에 둔다. 형식 검사는 판정 뒤 처리만 엔진에 남긴다. 판정 뒤 처리는 `record_formal_result`, 동일성 검토 시작, 계획 재요청이다. 종료 처리는 `_end_machine_execution` 하나를 쓴다.
- 실익: 약 40-60행이 줄 것으로 추정한다. 정지 사유 규칙과 보존 규칙을 한 곳에서 고칠 수 있게 된다. 엔진 파일에서 기계 실행의 책임이 빠진다.
- 비용과 위험: 형식 검사는 `release_or_hold`가 실패하면 결과를 기록하지 않고 멈춘다. 공통 종료 처리로 옮길 때 이 순서를 보존해야 한다. 정지 사유를 형식 검사는 목록으로, 신뢰 검사는 불리언으로 다루므로 공통형을 정해야 한다.
- 기능·커버리지 영향: 없음(같은 동작을 목표로 한다)
- 사용자 결정 관련: 없음
- 확신도: 추정. 두 골격의 대응은 원문으로 확인했다. 합친 뒤의 행 수와 순서 보존은 실제 수정안을 만들어 봐야 확정된다.

#### ENG-09 엔진이 다른 모듈의 비공개 내부를 직접 쓴다
- 검토: 1
- 종류: 경계
- 좌표:
  - `scripts/do_math/engine.py:287`, `:290`: `store._store._validate_oid`, `store._git("rev-list", ...)`
  - `scripts/do_math/repository.py:719-720`: `_git` 전달 메서드
  - `scripts/do_math/engine.py:4003`, `:4005`: `retention._run_path`, `retention._inventory`
  - `scripts/do_math/engine.py:4065`: `knowledge_io._lookup_definition`
  - `scripts/do_math/engine.py:2211`: `question_engine._pointer`
  - `scripts/do_math/engine.py:2851`: `candidate._fact`, 곧 `ObservationTracker._fact`
- 현상:
  - `_control_result`는 git 명령(`rev-list --first-parent`)과 OID 검사를 엔진에서 직접 조립한다. `ResearchRepository._git`의 제품 호출자는 이 한 곳뿐이다.
  - `_maintenance_cleanup`은 retention의 비공개 함수로 실행 폴더 목록을 만든다. 이어서 보관 manifest와 종료 증거를 엔진에서 조립한다. retention 자신도 같은 두 함수로 정리 후보를 만든다(`retention.py:216`, `:222`).
- 근거: 검색식 `grep -nE "\b(store|retention|knowledge_io|candidate)\._[a-z]" engine.py`는 6건을 찾았다. `grep -rn "\._git(" scripts/do_math`에서 `git_store`·`formal` 밖의 호출자는 `engine.py:290`과 `repository.py:720`(정의) 둘이다.
- 제안:
  - 저장소에 공개 조회 하나(예: `first_descendant(parent, head)`)를 두고 `ResearchRepository._git`을 지운다.
  - 실행 폴더 보관 조립(목록, 보관 행, 종료 증거)을 retention의 공개 함수 하나로 옮긴다. 엔진은 게시와 `mark_artifact_verified`만 한다.
  - 나머지 세 곳은 소유 모듈이 공개 이름을 주거나, 엔진이 이미 있는 공개 함수를 쓴다.
- 실익:
  - git 지식이 저장소 층에만 남는다.
  - 정리 보관의 규칙이 retention 한 모듈에 모인다. 엔진에서 약 20행이 빠진다.
  - 비공개 이름을 바꿀 때 엔진이 깨지는 결합 6곳이 사라진다.
- 비용과 위험: `repository`, `retention`, `knowledge_io`, `question_engine`, `observations`에 공개 이름을 더한다. 동작은 같다.
- 기능·커버리지 영향: 없음
- 사용자 결정 관련: 없음
- 확신도: 확인

#### ENG-10 `engine.py`가 공용 도우미의 저장소가 되어, 믹스인과 도메인 모듈이 엔진을 거꾸로 import한다
- 검토: 1
- 종류: 경계
- 좌표:
  - `scripts/do_math/engine.py:67-69`(`_repository`), `:97-115`(`DEFAULT_CONFIG`), `:118-119`(`now`), `:122-138`(`json_safe`), `:205-232`(`validate_config`)
  - 역방향 import: `scripts/do_math/academic_engine.py:54`, `scripts/do_math/governance_engine.py:40`, `scripts/do_math/governance.py:837`, `scripts/do_math/scheduler.py:89`, `scripts/do_math/reporting.py:23`, `scripts/do_math/cli.py:16`, `:18`, `scripts/probe_cli.py:10`
- 현상:
  - 엔진 import 그래프 아래에 있는 모듈들이 순환을 피하려고 함수 안에서 엔진을 import한다. `governance_engine`과 `governance`는 설정 검사를, `academic_engine`은 `now`를, `scheduler`는 `json_safe`를 가져간다.
  - `probe_cli.py`는 `json_safe` 하나를 쓰려고 엔진 전체를 적재한다.
  - `cli.py:18`은 비공개 `_repository`를 `ResearchRepository`라는 별칭으로 가져온다. 그래서 같은 이름이 다른 뜻을 가진다.
  - 설정 지식은 흩어져 있다. 키·형·범위는 `record_schemas.config_schema`, 기본값은 `engine.DEFAULT_CONFIG`, 교차 규칙은 `engine.validate_config`, configure 모양은 `control_contracts`에 있다.
- 근거: 검색식 `grep -rn "from \.engine import\|from do_math.engine import" scripts/do_math scripts/*.py`는 제품 9건을 찾았다. 이 가운데 엔진을 정당하게 소비하는 곳은 `cli.py:16`과 `scheduled_operator.py:221`뿐이다. `now()`와 같은 식은 `observations.utc_now`(`observations.py:247`)와 여러 모듈의 인라인 식에도 있다.
- 제안:
  - `DEFAULT_CONFIG`와 `validate_config`를 설정 절 정본 옆(`record_schemas` 또는 설정 전용 모듈)으로 옮긴다. 그러면 설정 표 하나가 키·형·범위·기본값을 담는다.
  - `json_safe`는 저장 값 영역을 소유한 `payloads` 또는 `file_io`로 옮긴다.
  - `_repository`는 `ResearchRepository`의 기본 계약 생성자로 옮긴다.
  - `now`는 `file_io`(`parse_utc`와 같은 곳)로 옮긴다.
- 실익: 역방향 import 7곳이 사라진다. 엔진 파일에서 약 60행이 빠지고, 엔진이 바뀌는 이유에서 설정·직렬화가 빠진다. `probe_cli`가 엔진을 적재하지 않는다.
- 비용과 위험: 약 10개 파일의 import가 바뀐다. 시험 65개 파일이 `DEFAULT_CONFIG`를 `engine`에서 가져오는지 확인해야 한다(검색식 `grep -rln DEFAULT_CONFIG tests`, 65건). 새 import 순환이 생기지 않는지 모듈별 새 프로세스 import로 확인해야 한다.
- 기능·커버리지 영향: 없음
- 사용자 결정 관련: 없음
- 확신도: 확인

#### ENG-11 `_controls`가 inbox 적용과 여러 하위 체계의 주기 정리를 한 함수에서 하고, 입력 준비 도중에도 전부 돈다
- 검토: 1
- 종류: 경계
- 좌표: `scripts/do_math/engine.py:885-1025`, `:3171`, `:3197-3206`, `scripts/do_math/lifecycle_engine.py:1290`
- 현상: `_controls`는 세 가지 일을 한다.
  - 호출·transport를 펌프한다.
  - inbox 제어를 적용한다.
  - 여덟 가지 정리를 한다. 대상은 운영 점검 예약, 제출 게시 재시도, 영향 검토 재시도, 검토 호스트 프로필 조정, 초기 재시도, 운영 수리, 평가 재심, 피드백 재전달이다.

  입력 준비 도중의 두 호출(`:3171`, `:3197`)과 외부 전송의 정지 판정(`lifecycle_engine.py:1290`)은 사용자 제어를 반영하려는 목적이다. `:3202`의 주석이 이를 밝힌다. 그런데 이 호출들도 정리 전부를 실행한다. 정리가 head를 움직이면 `:3202`의 비교가 준비한 입력을 버린다.
- 근거: 원문. 검색식 `grep -rn "self._controls(" scripts/do_math`는 7건을 찾았다.
- 제안: `_controls`를 inbox 적용(펌프 포함)과 주기 정리 둘로 나눈다. 입력 준비의 확인점과 외부 전송의 정지 판정은 inbox 적용만 부른다. 소유 루프, `run` 시작, `process_controls`, 호출 종료는 둘 다 부른다.
- 실익: 함수 하나가 한 가지 책임을 가진다. 입력 준비 중에 무관한 게시가 일어나 준비가 버려지는 경로가 준다.
- 비용과 위험: `engine.py`와 `lifecycle_engine.py`를 고친다. 정리가 늦어지는 시간은 소유 루프 한 회차(0.25초) 이내다. 정리 가운데 입력 준비 전에 반드시 일어나야 하는 것이 없는지 확인해야 한다.
- 기능·커버리지 영향: 없음(정리가 다음 회차로 미뤄질 수 있다)
- 사용자 결정 관련: 없음
- 확신도: 추정. 구조는 확인했다. 실제로 준비가 버려지는 빈도는 `input preparation interrupted` 종료 사유를 운전 기록에서 세면 확정된다.

#### ENG-12 과제의 `pending_withdrawal`은 생산자가 없는데, 매 저장마다 소비 루프가 돈다
- 검토: 1
- 종류: 미사용
- 좌표: `scripts/do_math/engine.py:824-836`, `scripts/do_math/record_schemas/schemas.py:353`
- 현상: `_save`는 저장할 때마다 모든 과제를 돌며 `pending_withdrawal`을 찾는다. 찾으면 실행 전건을 대조해 과제를 닫는다. 이 필드를 쓰는 코드는 없다.
- 근거: 검색식 `grep -rn "pending_withdrawal" --include=*.py --include=*.md .`는 3건(`engine.py:825`, `:834`, `schemas.py:353`)을 찾았다. 시험과 문서에는 없다. 생산자는 커밋 `9e5e120`(구판 호환 경로 제거)이 `governance`의 옛 과제 범위 결정과 함께 지웠다(`git show 9e5e120`의 `task["pending_withdrawal"] = deepcopy(task["scope_disposition"])` 삭제 줄).
- 제안: `_save`의 루프 13행과 스키마 필드를 지운다.
- 실익: 13행이 준다. 저장마다 하던 과제 전건 순회가 사라진다.
- 비용과 위험: 없음. 저장 스키마에서 필드가 빠지지만 생산자가 없으므로 기존 상태에 값이 있을 수 없다.
- 기능·커버리지 영향: 없음
- 사용자 결정 관련: 없음
- 확신도: 확인

#### ENG-13 `runtime.installation`과 `implementation_history`는 읽는 곳이 없는데, 판본이 바뀔 때마다 설치 manifest 전체 두 벌을 쌓는다
- 검토: 1
- 종류: 미사용
- 좌표: `scripts/do_math/engine.py:1576-1581`, `scripts/do_math/record_schemas/schemas.py:662-663`
- 현상: `run`이 시작할 때 설치 판본이 저장값과 다르면 `implementation_history`에 행을 더한다. 이 행은 `{"from": 이전 manifest, "to": 현재 manifest}`다. 동시에 `runtime.installation`을 현재 manifest로 바꾼다. 설치 판본 일관성은 프로세스 메모리의 `self._installation`과 비교하는 `_check_installation`(`:740-753`)이 지킨다. 저장된 두 필드는 이 검사에 쓰이지 않는다.
- 근거:
  - 검색식 `grep -rn "implementation_history\|\"installation\"\]\|get(\"installation\")" scripts/do_math`는 4건을 찾았다. 셋은 위 쓰기 좌표이고, 하나는 스키마다.
  - 시험에는 `runtime["installation"]`을 단언하는 곳이 없다. `test_performance_repairs.py:353`은 임의 값을 넣는 대역이다.
  - 크기는 `python -c`로 한 번 쟀다. `ResearchEngine._installation_manifest()`의 결과는 파일 98개, `canonical_json` 10,517바이트였다. 따라서 행 하나가 약 21KB이고, 게시마다 직렬화되는 runtime에 판본 변경 횟수만큼 쌓인다.
- 제안: 두 필드의 쓰기와 스키마를 지운다. 기동 때의 기준 판본은 지금처럼 `run` 시작 시점에 한 번 계산해야 한다. 그러므로 `_run_executor`에서 `self._installation`을 한 번 평가하는 줄은 남긴다.
- 실익: 6행이 준다. runtime에서 약 10KB와 판본 변경당 약 21KB가 빠지고, 이후 모든 게시의 직렬화·비교 비용이 준다.
- 비용과 위험: 판본 이력이라는 증거가 저장에서 사라진다. 이 이력을 읽는 제품·문서 소비자는 없다. 기동 때의 계산 시점을 지키지 않으면, 적재와 첫 검사 사이의 설치 변경을 놓친다.
- 기능·커버리지 영향: 있음. 저장 상태에서 두 필드가 빠진다.
- 사용자 결정 관련: 있음. 2절 12항 "설치 판본 일관성"을 약하게 하지 않는다. 탐지는 메모리 비교가 하므로 이 불변 조건은 바뀌지 않는다. 다만 저장된 판본 기록을 이 조건의 증거로 볼지는 사용자가 판단할 수 있다.
- 확신도: 확인

#### ENG-14 `ensure_ontology`가 엔진 생성과 `process_controls`에서만 적재 상태를 보충하고, `run`의 재적재에서는 하지 않는다
- 검토: 1
- 종류: 불일관
- 좌표: `scripts/do_math/engine.py:517`, `:1495`, `:262`, `:818-821`, `scripts/do_math/knowledge_io.py:95-103`, `:144`, `:255`, `:390`
- 현상:
  - `ensure_ontology`는 인스턴스 전체를 deepcopy한 뒤 내장 지식 종류를 `setdefault`로 채운다.
  - 내장 종류는 `initialize`가 이미 저장한다(`:262`).
  - 엔진은 생성자(`:517`)와 `process_controls`(`:1495`)에서 적재 상태에 이 함수를 다시 적용한다. `run`의 `_reload`(`:820`)는 적용하지 않는다. 그래서 생성자의 보충은 첫 `_reload`에서 버려진다.
  - 이 보충이 쓰이는 경로는 `knowledge_io`의 함수들이다. 이 함수들은 스스로 `ensure_ontology`를 부른다(`:144`, `:255`, `:390`).
- 근거: 검색식 `grep -rn "ensure_ontology(" scripts/do_math`는 9건을 찾았다. 엔진 3건 가운데 적재 상태에 적용하는 것은 2건이다. 이 보충은 설치 코드에 내장 종류가 추가됐을 때 기존 인스턴스를 채우는 효과를 낸다. 이는 AGENTS.md가 금지한 "예전 자료를 읽기 위한 기본값 보충"에 해당한다.
- 제안: `:517`과 `:1495`의 호출을 지운다. 내장 종류는 `initialize` 때만 넣는다.
- 실익: 2행이 준다. `process_controls`마다 하던 인스턴스 전체 deepcopy 1회가 사라진다. 적재 경로에 따라 상태가 달라지는 불일관이 사라진다.
- 비용과 위험: 내장 종류가 없는 상태를 손으로 만든 시험이 있으면 그 시험을 현행 초기 상태로 고쳐야 한다.
- 기능·커버리지 영향: 없음(현행 계약으로 만든 상태에는 내장 종류가 이미 있다)
- 사용자 결정 관련: 없음
- 확신도: 확인

#### ENG-15 살아 있는 AI 실행마다 1초 관찰 틱이 runtime과 tracker 전체를 deepcopy한다
- 검토: 1
- 종류: 비용
- 좌표: `scripts/do_math/engine.py:2785-2867`, `scripts/do_math/model_runner.py:175-179`, `C:/math/docs/do-math/검사-경량화-설계-2026-09-26.md:254`
- 현상: 러너는 새 바이트가 없어도 1초마다 `on_observation`을 부른다(`model_runner.py:176`). `_observe_running`은 호출마다 다음을 한다.
  1. `deepcopy(tracker)`
  2. `deepcopy(self.runtime)`(롤백용)
  3. `_save()`. 그 안의 `_unchanged()`가 상태 전체를 비교한다.

  빈 틱은 대개 상태를 바꾸지 않고 `_unchanged()`로 끝난다. 그래도 두 번의 전체 복사는 매번 일어난다.
- 근거: 원문. 설계 R14는 "관찰마다 제어 적용과 상태 전체 deepcopy"를 "줄인다"로 처분했다. 8d2ffd0는 instance 복사를 없애고 runtime 복사를 남겼다.
- 제안: 틱의 관찰 결과와 스트림 상태 변화를 tracker 사본에서 먼저 계산한다. runtime에 쓸 것이 있을 때만 runtime 롤백 사본을 만들고 저장한다. 쓸 것이 없으면 tracker 사본만 반영하고 돌아간다.
- 실익: 대기 중인 실행 하나당 초당 runtime 전체 deepcopy 1회와 상태 비교 1회가 사라진다. 크기는 runtime에 비례하며 측정하지 않았다.
- 비용과 위험: `engine.py` 한 함수를 고친다. 새 상태는 없다. 롤백 범위를 좁히는 것이므로, 쓸 것이 없다고 판정한 틱이 정말 runtime을 건드리지 않는지 확인해야 한다. `_record_review_observation`은 행이 있을 때만 부른다.
- 기능·커버리지 영향: 없음
- 사용자 결정 관련: 없음. R14의 "줄인다" 방향을 잇는다.
- 확신도: 추정. `operation_trace`의 `observation_application` 측정값으로 빈 틱의 비용을 재면 확정된다.

#### ENG-16 `status`·`check` 출력에 생산자도 소비자도 없는 상수 필드가 있다
- 검토: 1
- 종류: 미사용
- 좌표: `scripts/do_math/engine.py:1517`, `:1526`, `:1538`, `:4538`
- 현상:
  - `research_effectiveness: {"status": "not_evaluated"}`는 `status`와 `check`에 늘 같은 값으로 들어간다. `reporting.py:176`에도 사유 문구가 다른 같은 필드가 있다.
  - `budget_observed_at`은 바로 옆 `research_observed_at`과 같은 시각을 한 번 더 찍는다.
  - `question_scope: "open_user_questions"`는 상수다.
- 근거:
  - 검색식 `grep -rn "research_effectiveness\|budget_observed_at\|question_scope" --include=*.py --include=*.md .`로 찾았다. 코드의 읽기는 0건이다. `research_observed_at`만 `cli.py:500`이 읽는다.
  - 문서 일치 가운데 `question_scope`는 계약 검토 항목 이름이라는 다른 개념이다(`계약/작업-계약-검토.md:95`, `contracts.py:162`).
  - 시험 단언은 0건이다. README의 status 필드 표에도 셋 다 없다.
- 제안: 세 필드를 `status`에서 지우고 `research_effectiveness`를 `check`에서 지운다. ENG-03을 채택하면 `reporting` 쪽 사본도 함께 정리한다.
- 실익: 출력 필드 4개와 약 4행이 준다. 공개 출력의 필드가 문서와 맞는다.
- 비용과 위험: 공개 JSON 출력이 바뀐다. 사람이 이 필드를 읽는지는 저장소 밖의 사실이라 확인할 수 없다.
- 기능·커버리지 영향: 있음. 출력 필드가 줄어든다.
- 사용자 결정 관련: 없음
- 확신도: 확인(저장소 안의 소비자 부재)

#### ENG-17 도달할 수 없는 분기와 읽히지 않는 쓰기 네 곳
- 검토: 1
- 종류: 미사용
- 좌표: `scripts/do_math/engine.py:4187`, `:639`, `:3097-3098`, `:1584`
- 현상:
  - `:4187` `retry.pop("after_stop", None)`의 `retry`는 대기열 action이다. `after_stop`은 실행 기록의 필드다(`scheduler.py:175`). 닫힌 action 스키마 `_ACTION`(`record_schemas/schemas.py:109`, `additionalProperties: false`)에는 이 필드가 없다.
  - `:639` `execution.pop("activity_id", None)`: `_register_execution`의 호출자 5곳(`engine.py:3144`, `:4337`, `lifecycle_engine.py:1126`, `:1198`, `:1329`)은 이 키를 넘기지 않는다. `create_execution`도 만들지 않는다.
  - `:3097-3098` `observation_mode == "deadline_only"`이면 규칙을 비운다. 그러나 규칙은 `research_work`일 때만 채워지고, 그 역할의 관찰 모드는 설정값(`event_driven`·`periodic`)이다(`execution_profiles.py:209-210`). tracker도 이 조합을 거부한다(`observations.py:449-450`).
  - `:1584` `recovery_checked = True`: 이 값을 읽는 곳은 `activation_requirements` 하나다(`initialization.py:213`). 그 유일한 엔진 쪽 호출 직전에 `_activate_initialization`이 값을 다시 계산해 덮는다(`lifecycle_engine.py:168`).
- 근거: 검색식은 `grep -rn "after_stop"`, `grep -rn "_register_execution("`, `grep -rn "deadline_only"`, `grep -rn "recovery_checked\|activation_requirements("`이다(모두 `scripts/do_math`). 각 결과는 위 좌표로 전수 확인했다.
- 제안: 네 곳을 지운다.
- 실익: 약 5행이 준다. 읽는 사람이 없는 조건을 해석할 부담이 사라진다.
- 비용과 위험: 없음
- 기능·커버리지 영향: 없음
- 사용자 결정 관련: 없음
- 확신도: 확인

#### ENG-18 모듈 최상단에서 이미 import한 모듈을 함수 안에서 다시 import한다
- 검토: 1
- 종류: 불일관
- 좌표: `scripts/do_math/engine.py:254`, `:567`, `:1036`, `:1668`, `:2025`, `:2211`, `:2590`, `:2836`, `:2895`, `:3099`, `:3105`, `:3642`, `:4169`, `:4289`
- 현상: 함수 안 import 25건 가운데 14건은 모듈 최상단에서 이미 import한 모듈(`governance_engine`, `contracts`, `trust_validation`, `launch`, `context_store`, `question_engine`, `model_runner`, `observations`)에서 가져온다. 이 14건은 순환 회피가 이유일 수 없다. `_settle_activity`의 `review_cycle` import(`:694`)처럼 자주 도는 경로에도 함수 안 import가 있다.
- 근거: AST로 `engine.py`의 함수 안 `ImportFrom`을 모두 모아 최상단 import 모듈과 대조했다. 25건 중 14건이 겹쳤다. 나머지 11건(`control_contracts` 4, `maintenance_gate` 2, `record_schemas`, `review_cycle`, `input_recovery`, `platform` 등)은 순환 여부를 확인하지 않았다.
- 제안: 14건은 최상단 import의 이름으로 바꾼다. 나머지 11건은 새 프로세스 import 확인으로 순환이 없으면 최상단으로 옮긴다.
- 실익: import 문 14-25건이 준다. M-0350이 찾은 "함수 안 import의 반복 비용"이 엔진의 반복 경로에서 사라진다.
- 비용과 위험: 없음(14건). 나머지는 순환 확인이 필요하다.
- 기능·커버리지 영향: 없음
- 사용자 결정 관련: 없음
- 확신도: 14건은 확인이다. 나머지 11건은 추정이며, 모듈별 새 프로세스 import로 확정된다.

### 검토 2

#### ENG-19 `_CONTROL_READERS`는 제품에서 재사용되지 않는 프로세스 전역 캐시다
- 검토: 2
- 종류: 비대
- 좌표: `scripts/do_math/engine.py:11`, `:72-84`, `:326`, `scripts/do_math/cli.py:221-234`, `scripts/tests/test_performance_repairs.py:250-259`
- 현상: 9b434f4가 `control()`용 읽기 저장소를 (저장소, 인스턴스)마다 LRU 8개까지 보관하게 했다.
  - 제품의 `control()` 호출자는 `cli.py:223` 하나다. CLI는 명령마다 새 프로세스로 뜬다. 감독도 `subprocess`로 CLI를 부른다(`scheduled_operator.py:156`, `:268`).
  - 같은 CLI 호출 안에서 이어 만드는 `ResearchEngine`(`cli.py:230`)은 이 캐시를 쓰지 않고 새 저장소를 만든다.
  - 따라서 캐시가 두 번째 호출에서 쓰이는 곳은 한 프로세스에서 `control()`을 여러 번 부르는 시험뿐이다. 시험 하나는 이 캐시를 비우려고 모듈 내부를 패치한다.
- 근거: 검색식 `grep -rnE "import .*\bcontrol\b|_control_reader|_CONTROL_READERS" scripts`의 제품 결과는 `cli.py:16`과 엔진 정의뿐이다. 기준 2절 8항은 새 상태를 비용으로 센다. 2절 11항은 시험이 제품 내부를 비우는 것을 경계 신호로 본다.
- 제안: `_CONTROL_READERS`, `_control_reader`, `OrderedDict` import, 해당 시험을 지운다. `control()`은 `_repository`를 직접 부른다. 시험의 반복 비용이 문제라면 시험 픽스처가 저장소를 들고 다닌다.
- 실익: 제품 약 14행과 시험 약 10행, 그리고 프로세스 전역 상태 하나가 사라진다.
- 비용과 위험: 시험 스위트의 `control()` 호출마다 저장소 생성(git 조회 1회)이 다시 생긴다. 41개 시험 파일이 `control(`을 부른다. 기준 3절의 조각 시간 목표에 미칠 영향은 측정하지 않았다.
- 기능·커버리지 영향: 없음(제품 동작 불변)
- 사용자 결정 관련: 있음. 시험 경량화(결정: 조각 120초·합계 300초 목표)의 시간 이득과 맞바꾼다. 새로 드러난 사실은 이 캐시의 이득이 제품이 아니라 시험에만 있다는 점이다.
- 확신도: 확인. 시험 시간 영향은 추정이며, 캐시를 끈 채 해당 조각의 시간을 재면 확정된다.

#### ENG-20 `_save`가 저장소 캐시 정책(`retain_reads`)을 쥐고, 시험 대역을 위해 `git_dir`의 부재와 형을 검사한다
- 검토: 2
- 종류: 임시방편
- 좌표: `scripts/do_math/engine.py:849-853`, `:196-202`, `scripts/do_math/repository.py:114-116`, `scripts/tests/research_fixtures.py:173-195`, `C:/math/docs/do-math/검사-경량화-이음새-계약.md:108`
- 현상:
  - 9b434f4가 `_save`에 두 가지를 넣었다. 하나는 게시 뒤 살아 있는 실행의 input snapshot 읽기 캐시를 LRU 밖에 붙잡는 코드다. 다른 하나는 `getattr(self.store, "git_dir", None)`과 `isinstance(git_dir, (str, Path))` 검사다.
  - 시험의 메모리 저장소 대역 `StateStore`에는 `git_dir`이 없다. `Mock` 저장소의 `git_dir`은 `Mock`이다. 이 두 대역을 통과시키려는 분기다.
  - 8d2ffd0의 `_evaluation_context_for`도 `getattr(store, "git_dir", None)`을 쓴다(`:201`).
  - 반면 엔진의 다른 경로(`_sealed_bytes`, `_issued_input` 등)는 `self.store.git_dir`을 직접 읽는다.
- 근거: 원문. 이음새 계약 4절(`:108`)은 "캐시 채우기는 `repository.save_with_state` 안(저장소 층)에서 한다. `engine._save`에서 하지 않는다"고 정했다. AGENTS.md는 "구형 fixture나 인터페이스를 살리려고 제품 코드에 예외를 넣지 않는다"고 정했다.
- 제안: 붙잡을 head 집합을 `save_with_state`의 인자(예: `retain=`)로 넘기고, 저장소가 `retain_reads`를 부른다. `StateStore` 대역은 이 인자를 받아 무시한다. `_evaluation_context_for`는 `store.git_dir`을 직접 읽고, 대역은 `git_dir`을 가진다.
- 실익: 제품의 시험용 분기 2곳이 사라진다. 캐시 정책이 저장소 층에 모인다. `git_dir` 접근 방식이 하나로 통일된다.
- 비용과 위험: `engine.py`, `repository.py`, 시험 대역을 고친다. 새 상태는 없다.
- 기능·커버리지 영향: 없음
- 사용자 결정 관련: 없음
- 확신도: 확인

#### ENG-21 프로세스 지역 상태 다섯 가지가 `_init_process_state` 밖에서 `getattr` 기본값으로 생긴다
- 검토: 2
- 종류: 잔재
- 좌표: `scripts/do_math/engine.py:519-534`, `:1016`, `:1025`, `:1030`, `:1034`, `:2488-2491`, `:3665`, `:4053`, `:4244-4246`
- 현상: 379a171은 "엔진의 모든 프로세스 지역 상태는 여기서 시작한다"는 `_init_process_state`를 두었고, 방어 `getattr` 14곳과 추가 5곳을 지웠다. 그러나 조사 목록에 없던 다섯 가지는 여전히 `getattr(self, name, 기본값)`으로 처음 쓸 때 생긴다. 대상은 `_feedback_delivered`, `_retrying_publication`, `_next_lean_discovery`·`_lean_found`, `_external_preparation_binding`, `_goal_audit_contract`다. 같은 종류가 믹스인에도 있다(`lifecycle_engine.py:89`, `scheduler.py:46`).
- 근거: 검색식 `grep -n "getattr(self, " engine.py`는 6건을 찾았다. `결과-K시험.md:18`, `:184-189`와 `결과-A.md:63`은 처리한 목록이 조사 목록에 한정됐음을 기록했다.
- 제안: 다섯 속성의 초기값을 `_init_process_state`로 옮기고 직접 접근으로 바꾼다. `_external_preparation_binding`은 ENG-05를 채택하면 사라진다.
- 실익: 프로세스 지역 상태의 목록이 한 곳에 모인다. 메모(`_goal_audit_contract`, `_lean_found`)의 수명을 한 곳에서 읽을 수 있다. 약 6개의 `getattr`이 준다.
- 비용과 위험: 없음. 메모의 무효화 규칙(설치 변경 시 정지, 1초 재탐색)은 그대로다.
- 기능·커버리지 영향: 없음
- 사용자 결정 관련: 없음
- 확신도: 확인

#### ENG-22 2라운드 조사 ENG-22(한 곳짜리 포장과 반복 투영)는 설계 처분표에 없고, 원문에 그대로 남아 있다
- 검토: 2
- 종류: 공백
- 좌표:
  - `scripts/do_math/engine.py:2774-2775`(`_read_extensions`, 유일 호출자 `:2371`)
  - 사용자 제어 요청 조회 4곳: `:281-283`, `:1453-1454`, `:2018-2019`, `:3968-3969`
  - 미종료 실행의 action ID 집합 3곳: `:1820`, `:3579`, `:3875`
  - `lambda snapshot, path: self.store.read(path, snapshot)` 8곳
  - 형식 검사의 `reference` 두 번 대입(`:4378`, `:4388`)과 `proposal.lean`의 두 묶음 보존(`:4382`, `:4392`, `:4435`)
- 현상: 2라운드 조사 `ENG.md`의 ENG-22가 제안한 정리가 하나도 적용되지 않았다. `C:/math/docs/do-math/경량화-설계-2026-09-26.md`의 처분표와 5절(기각·보류·보존)에는 ENG-22가 없다. 채택도 기각도 되지 않고 빠진 것이다.
- 근거:
  - 검색식 `grep -n "ENG-22" C:/math/docs/do-math/경량화-설계-2026-09-26.md`는 0건이다. 결과-A~E에서도 0건이다.
  - 현재 원문의 반복 횟수는 `grep -c`로 셌다. 람다는 8건이다. `_read_extensions`는 `grep -rn "_read_extensions" scripts`로 정의 1건과 호출 1건을 찾았고, 시험의 교체는 0건이다.
  - 람다의 원인은 인자 순서 차이다. 저장소 `read(path, snapshot)`과 콜백 관례 `(snapshot, path)`가 서로 다르다.
- 제안: 조사 제안을 현재 좌표에 적용한다.
  - `_read_extensions`를 지운다.
  - `_user_control_request(request_id)`와 `_live_action_ids()`를 두어 반복을 한 번씩 정의한다.
  - 저장소에 `(snapshot, path)` 순서의 읽기 메서드를 두어 람다 8개를 없앤다.
  - 형식 검사 원문은 원 반환 묶음 한 곳에만 둔다.
- 실익: 약 25행이 준다. 같은 조회 규칙이 한 번씩만 정의된다.
- 비용과 위험: `engine.py`와 `repository.py`를 고친다. `proposal.lean`의 보존 위치를 바꾸면 형식 결과의 `artifact_ref` 묶음 구성이 바뀐다. 이 묶음을 읽는 운영 점검 입력 경로를 함께 확인해야 한다.
- 기능·커버리지 영향: 형식 검사 묶음의 파일 배치만 바뀐다(선택)
- 사용자 결정 관련: 없음
- 확신도: 확인

#### ENG-23 모듈 docstring이 공급자를 Codex만으로 적는다
- 검토: 2
- 종류: 낡음
- 좌표: `scripts/do_math/engine.py:1-6`
- 현상: 379a171은 같은 docstring의 계약 판본 줄을 `do-math-state/6`으로 고쳤다. 그러나 첫 줄 "observable Codex CLI executions"는 남겼다. 현행 어댑터는 Codex와 Claude 둘이다(`claude_adapter.ADAPTERS`, 이음새 계약 11절).
- 근거: 원문 대조
- 제안: "observable provider CLI executions(Codex, Claude)"처럼 현행 공급자 범위로 고친다.
- 실익: 모듈의 첫 설명이 현행 계약과 맞는다.
- 비용과 위험: 없음
- 기능·커버리지 영향: 없음
- 사용자 결정 관련: 없음
- 확신도: 확인

## 4. 보존 판정

- **설치 판본 목록 메모 `_HASHED_INSTALLATION`·`_installation_listing`**(`engine.py:158-193`, `:546-575`)
  - 목록 키에 `SKILL.md`(역할 문서 지도의 원천)와 모든 `.py`가 들어가므로, 결과를 정하는 입력이 키에 모두 있다.
  - 무효화는 목록 비교 한 곳에서 일어나고, 정착하지 않은 지문은 재사용하지 않는다.
  - M-0350이 경합 중 0.26-0.85초를 약 1ms로 줄였음을 제품에서 측정했다.
  - 목록(`scandir`)과 해시 대상(`rglob`)이 같은 파일 집합을 두 번 열거하는 것은 작은 흠이다. 어긋나도 재계산이 늘 뿐 결과는 틀리지 않는다.
- **엔진 설치 manifest가 `file_io.installation_files`보다 좁은 것**(`engine.py:566-571`): 역할 문서와 코드만 보는 "실행 중 판본" 개념이다. OPS 조사 3절의 보존 판정과 같다.
- **`_inspect_before_write`의 존재·길이 확인**(`engine.py:4488-4507`): 검사 경량화 설계 R37의 사용자 처분이다.
- **`_controls`가 요청마다 `_save`하는 것**(`engine.py:908-1005`): `_control_result`가 "게시 부모의 첫 후손에 영수증이 있다"는 규칙으로 영수증을 찾으므로, 요청 하나에 CAS 하나가 필요하다.
- **`_sealed_bytes`·`_issued_input`의 얇은 포장**(`engine.py:1060-1064`, `:1370-1373`): 저장소와 head를 묶어 각각 15곳과 10곳의 인자 반복을 없앤다. `_read_extensions`(ENG-22)와 달리 실익이 있다.
- **후보 적용 때 엔진 상태를 잠시 바꿔 끼우는 방식**(`engine.py:2175-2202`, `:2219-2266`): 믹스인 메서드가 모두 `self.instance`·`self.runtime`에 묶여 있어서 생긴 방식이다. 없애려면 믹스인 전체를 상태 인자형으로 바꿔야 해 실익에 비해 비용이 크다. RES 조사 3절의 믹스인 분할 보존 판정과 같은 이유다.
- **`_publish_control_request`·`_capture_native_submission`의 사전 deepcopy와 게시 확인 복구**(`engine.py:1268-1335`, `:2990-3003`): 2라운드 ENG 조사 3절의 보존 판정이다. ENG-15는 이 둘이 아니라 `_observe_running`만 다룬다.
- **`_available_inputs`의 `lean_command` 선판정**(`engine.py:2496`): `available_input_refs`와 조건이 겹치지만, 설정된 경우 Lean 탐색 자체를 건너뛰는 비용 절감이다. `test_performance_repairs.py:224-238`이 이 동작을 확인한다.
- **질문 원문 포인터와 조건 포인터의 두 구현**(`question_engine.py:8-11`, `planning.py:445-458`): RES 조사 3절의 보존 판정(계약이 다름)과 같다. ENG-09는 엔진의 비공개 import만 다룬다.
- **`validate_control_payload`를 접수와 적용 양쪽에서 부르는 것**(`engine.py:319`, `:894`): IO 조사 3절의 보존 판정과 같다. ENG-01은 이와 별개인 보호 키 집합을 다룬다.

## 5. 영역 밖 관찰

- `governance_engine.py:40`은 `DEFAULT_CONFIG`를 import하지만 쓰지 않는다(OPS).
- `scheduler.py:448`의 `get("plan_settle_seconds", 300)`은 `DEFAULT_CONFIG`의 기본값을 다시 적은 사본이다. `initialize`가 기본값을 병합하므로 저장 설정에는 이 키가 늘 있다(RUN).
- `lifecycle_engine.py:1106`의 `mark_returned`는 `scheduler._local_call_returned`가 이미 한 표시를 다시 한다. 멱등이라 해는 없다(RUN).
- `lifecycle_engine.py:89`, `:172`, `:341`, `:725`, `:730`, `:732`와 `scheduler.py:46`에 방어 `getattr`·`hasattr`가 남아 있다. 이 가운데 믹스인 메서드의 존재를 확인하는 것도 있다(RUN).
- `recovery_checked`는 `lifecycle_engine.py:168`이 정지 판정에서 계산해 저장하고, 곧바로 `initialization.py:213` 한 곳만 읽는 파생 저장값이다(RUN·OPS).
- `submission.issued_input`은 경로가 아닌 `git_dir`(시험 대역)이면 메모하지 않는다(`결과-C.md:128`). ENG-20과 같은 시험 수용 분기다(REV).
- `cli.py:18`의 `from .engine import _repository as ResearchRepository`는 비공개 함수에 다른 클래스 이름을 붙인 별칭이다(IO).
- `reporting.snapshot_report`와 `engine.status`, 그리고 `cli._human_status`와 `reporting.render_human_report`가 각각 같은 명령의 두 구현이다. ENG-03의 반대편이다(OPS·IO).
- `tests/test_performance_repairs.py:241-272`은 `_HASHED_INSTALLATION`·`_CONTROL_READERS`를 패치한다. `test_lifecycle_engine.py:774`, `:823`과 `test_redesign_ENGINE.py:542`는 `_available_inputs`를 대역으로 바꾼다(`결과-C.md:116`이 남겨 둔 것)(TSB·TSA).
- `C:/math/docs/do-math/검사-경량화-이음새-계약.md` 4절의 head 이동 지점 좌표(`engine.py:891`, `:2313`, `:1331`)는 기준 커밋의 행 번호라 현재 원문과 맞지 않는다(HIS).

## 6. 작업 기록

- **예상과 달랐던 결과**:
  - `contract_revision_limit` 등 다섯 설정 키는 처음에 소비자가 없어 보였다. 검색해 보니 `revisions.py:235`가 `lineage + '_limit'`로 동적으로 읽었다. 그래서 후보에서 뺐다.
  - `_available_inputs`의 `lean_command` 조건은 중복으로 보였다. 그러나 탐색을 건너뛰는 비용 절감이고 시험이 그 동작을 확인하므로, 보존으로 돌렸다.
  - 엔진의 `_validate_external` 재정의는 처음에 필요한 확장으로 보였다. `_validate_external` 호출자 넷을 모두 추적한 뒤 효과가 없음을 확인했다(ENG-05).
- **접근을 바꾼 지점**:
  - 모듈 크기를 기준으로 경계를 판정하려던 접근을 버렸다. 대신 함수별 행 수(`_call_steps` 520행, `_context` 377행)와 역방향 import, 비공개 접근, 두 벌 구현을 근거로 삼았다.
  - 크기만 줄이는 분할은 이음새를 없애지 못한다고 판단해 후보로 내지 않았다.
- **막힌 지점**: `write-for-reader` 스킬의 독해 절차(합의·독자 파일 작성, `writing_flow.py`)는 새 파일을 만든다. 기준 7절이 산출 파일 하나만 쓰게 하므로 실행하지 않았다. 스킬의 `명료한_산문.md`·`AI_프롬프트.md`·`에이전트_채널.md`는 읽고 적용했다.
- **실행한 확인**: 한 번 실행했다. 명령은 `python -c "... from do_math.engine import ResearchEngine; m=ResearchEngine._installation_manifest(); print(len(m['files']), len(canonical_json(m)))"`이고, 결과는 `98 10517`이다. 저장소 파일은 바꾸지 않았다.
