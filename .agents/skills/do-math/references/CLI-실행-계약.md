# do-math CLI 실행 계약

초기화의 검사 분리, 큰 불변 payload의 저장 코덱, `launch_ticket`, `quiesce`/`release-quiesce`, 신뢰 환경의 툴체인 기록·재기록, `timeline --include-operations`는 [초기화 효율과 정비](초기화-효율과-정비.md)의 현행 계약을 함께 따른다. `maintenance_fence`와 `operation_progress`는 각각 정비 상태와 별도 로컬 진행 관측이며 수학적 완료 판정이 아니다.

이 문서는 현행 do-math의 구체 인터페이스 참조다. 역할 응답의 wire 계약은 `do-math-cli/5`, 저장 계약은 `do-math-state/9`이며 서로 같은 스키마가 아니다. 명령행 인자, 구조화 제어, 저장 형식, CLI 상태 투영, AI 입력·출력과 산출 경로를 설명한다. do-math의 목적과 전체 연구 흐름은 `SKILL.md`, 보편 개념의 정의는 `GLOSSARY.md`, 역할별 판단·산출·실패 행동은 `계약/` 문서가 소유한다.

역할 응답, 기록 저장과 소비 API는 정확한 판본·해시를 대조하며, 옛 필드를 암묵 변환해 현재 계약으로 취급하지 않는다.

아래에서는 공통 개념과 역할 의무를 구현하는 필드와 절차, 실제 보증 범위와 미완료 기능을 설명한다.

## 호출과 공통 반환

실행 진입점은 다음과 같다.

```powershell
python .agents/skills/do-math/scripts/do_math.py <command> [options]
```

명령 예시는 스킬을 `.agents/skills/do-math/`에 설치한 경우다. 다른 위치에 설치했다면 명령의 이 경로를 실제 스킬 폴더 경로로 바꾼다. 운영할 때는 같은 설치본의 문서와 코드를 함께 사용한다. 별도 위치의 사본을 함께 참고한다면 두 사본의 판본이 같은지 먼저 확인한다.

`profile`은 인스턴스 식별 인자를 받지 않는다. `init`은 `--repository`와 목표·`--workspace`를 받아 새 인스턴스를 만든다. 나머지 명령은 `--repository`와 `--instance`를 요구한다. JSON을 입력받는 제어 명령은 UTF-8 JSON 객체 하나를 담은 `--file`을 사용한다. 중복 JSON 키, 배열이나 scalar 최상위 값, 읽기·디코딩 실패는 입력 오류다. 제어의 `--origin`은 `user`가 기본이며 승인된 자동 운영 제어는 `operator`를 사용한다. 자동 출처는 `pause`, `resume`, `request`, `configure`, `source`, `quiesce`, `release-quiesce`를 사용할 수 있고 예산·모델 대응·역할 등급을 변경할 수 없다. 정비 해제에는 해당 출처가 해제할 수 있는 현재 fence를 정확히 지정해야 한다.

<a id="exit-codes"></a>

### 종료 코드

| 코드 | 조건 |
|---|---|
| `0` | 명령 처리가 정상 종료됐다. 제어 명령은 `effect`를 따로 확인한다 |
| `1` | `check`가 결함을 찾았거나 `profile` 결과가 `verified`가 아니다 |
| `2` | 인자·파일·JSON·필드·대상 상태가 CLI 계약에 맞지 않는다. 응답 `kind=input_error` |
| `5` | Git 저장, OS, subprocess 같은 도구 계층이 실패했으면 응답 `kind=tool_error`다. `run`이 다른 실행기가 보유한 writer lock을 얻지 못한 경우도 여기에 속하며, 그 실행기가 끝난 뒤 다시 실행한다. 제어 명령의 lock 경합은 오류가 아니라 exit 0과 `lock="busy"`로 반환한다. 구현이 요청을 처리하지 못한 내부 계약 오류이면 `kind=contract_error`, `next_owner=maintenance`다. `init`·`configure`가 상태를 저장한 뒤 예약 등록에 실패한 경우에도 exit 5이며, 이때는 `error` 대신 `result.operator_schedule`에 `status="failed"`와 재조정 명령이 담긴다 |

JSON 응답의 최상위 필드는 `schema_version`, `response_contract`, `request_id`, `command`, `exit_code`와 `result` 또는 `error`다. 성공 값은 `result`, 오류의 `kind`·`message`·후속 정보는 `error`에서 읽는다. `result`와 `error`는 함께 나타나지 않는다. 사람용 `status`와 CSV `timeline` 출력은 텍스트이며, `--request-file` 호출은 이 값도 JSON 봉투의 `result`로 반환한다.

exit 0은 요청이 수학적으로 승인됐거나 과제·활동·실행이 완료됐다는 뜻이 아니다. 제어 요청은 `result` 안에 다음 공통 필드를 반환한다.

| 필드 | 뜻 |
|---|---|
| `accepted` | 요청이 control inbox에 불변 요청으로 기록됐다 |
| `request_id` | 그 요청의 CLI 식별자 |
| `effect` | `applied`, `rejected`, `pending engine processing` 중 현재 처리 결과 |
| `reason` | 거부 또는 처분 이유. 해당하지 않으면 null일 수 있다 |
| `status`, `snapshot` | 적용 뒤 CLI 상태와 상태 commit. lock이 busy이면 아직 없을 수 있다 |

초기화 채택(`decision`의 `kind=initialization`, `operation=adopt`)과 툴체인 등록(`trust`의 `operation=register`)이 적용되면 결과에 `observation_window_warnings` 배열이 더 붙는다. 각 항목은 역할별 현행 프로필이 쓰는 `tool_review_window_seconds`가 등록된 툴체인 기록의 대표 검사 소요 시간보다 짧다는 경고이며, `role`, `profile_id`, `field`, `window_seconds`, `environment_id`, `representative_check_seconds`를 담는다. `self_check_response_window_seconds`는 연구 도구 호출 동안 응답 기한이 멈추므로 경고 대상이 아니다. 소요 시간은 결박한 기준 항목의 대표 검사 시작·종료 시각의 차를 초 단위로 올림한 값이다. 경고는 채택이나 등록을 막지 않는다. 등록된 환경이 없거나 기록을 읽을 수 없으면 배열은 비어 있다.

동일 인스턴스의 writer lock을 다른 실행기가 보유하면 요청은 inbox에 남고 `effect="pending engine processing"`, `lock="busy"`를 반환한다. 다음 실행기 제어 처리에서 전제가 달라졌으면 해당 요청은 `effect="rejected"`와 이유를 남기고 소비된다. 접수 사실은 적용·실행·성공을 뜻하지 않는다.

공개 Python 제어와 CLI는 같은 payload 구조 검사를 사용한다. `config`는 객체이며, 생략을 뜻하는 Python `None`만 빈 객체로 처리한다. 중첩 결정·과거 실행 복구·신뢰 환경 등의 값도 사용 전에 해당 구조를 확인한다. 수신자는 inbox의 식별 가능한 요청을 다시 검사하고, 잘못된 payload를 거절 영수증과 함께 한 번 정산한 뒤 다음 요청을 처리한다. 입력 구조 검사는 현재 권한·참조·환경 관측을 대신하지 않는다. JSON 해석이나 요청 정체성 자체가 손상된 파일은 정상 사용자 요청으로 간주하지 않는다.

`pause`, `resume`, `close`, `quiesce`, `release-quiesce`, `input`, `configure`, `request`, `decision`, `knowledge`, `trust`, `external`, `conversation`, `source`는 제어 요청의 재전송과 새 적용을 구별한다. `--request-id`를 생략하면 인스턴스·명령·출처·원문·payload·선택적 `--idempotency-key`에서 요청 ID를 계산한다. `pause`와 `resume`은 상태를 오가는 제어이므로, `--idempotency-key` 없이 보낸 요청의 ID에는 마지막으로 접수된 반대 제어(`pause`에는 `resume`, `resume`에는 `pause`)의 요청 ID도 들어간다. 아직 처리되지 않은 반대 제어도 접수된 것으로 센다. 같은 내용의 재전송은 이미 처리한 효과를 반복하지 않고 최초 영수증을 `replayed=true`로 돌려준다. 그래서 재개 뒤 같은 이유로 다시 보낸 정지는 새 요청으로 적용되고, 그 사이에 반대 제어가 없는 정지의 재전송은 재생된다. 이 영수증의 상태와 snapshot은 현재 상태가 아니므로 현재 상태는 `status`로 조회한다.

같은 내용을 새 결정으로 다시 적용하려면 새 `--idempotency-key`를 지정한다. 그 적용의 재전송에는 같은 키를 유지한다. 예를 들어 설정을 A→B→A로 되돌릴 때에는 마지막 요청에 새 키가 필요하다. `--idempotency-key`를 지정한 요청의 ID는 키와 내용으로만 정해진다. 그래서 같은 키로 다시 보낸 `pause`·`resume`은 그 사이에 반대 제어가 있었어도 최초 영수증을 재생한다. `--request-id`로 요청 ID를 직접 지정할 수도 있으며, 같은 ID에 다른 payload를 보내면 거부된다. 두 옵션은 함께 사용할 수 없다. JSON 명령도 같은 이름의 `request_id`·`idempotency_key`를 사용한다.

## 현재 저장과 작업 경로

인스턴스의 권위 있는 머리는 `refs/heads/do-math/<instance_id>`다. 각 상태 commit은 직전 상태 commit 하나를 부모로 가지며, 저장소는 등록된 기록군을 `research/<family>/...`와 `runtime/<family>/...` 아래에 분리해 저장한다. `runtime/artifacts/<bundle_id>/...`의 불변 산출은 추가 전용으로 보존한다. 정확한 기록군·shape·스키마는 설치본의 `do-math-state/9` manifest가 소유한다.

일시적으로 재구성되는 `instance`·`runtime` 객체는 코드 내부 view이며 그 자체로 정본에 저장되지 않는다. 등록되지 않은 기록군, 알려지지 않은 필드, 중복 전역 ID와 잘못된 참조는 공개 전에 거부된다. 사건 기록군 `events`는 목록 형태로만 저장한다.

artifact는 기존 경로를 수정하지 않고 새 bundle에 추가한다. 대표 경로는 다음과 같다.

| 경로 | 내용 |
|---|---|
| `runtime/artifacts/<input_bundle>/input.txt` | 모델에 전달한 전체 prompt 바이트. manifest의 `prompt.artifact_ref`가 이 경로다 |
| `runtime/artifacts/<input_bundle>/schema.json` | 그 실행의 출력 JSON Schema |
| `runtime/artifacts/<input_bundle>/manifest.json` | catalog·구현 문서·제출 검사 도구와 스키마의 입력 manifest |
| `runtime/artifacts/<input_bundle>/input/catalog/<key>.json` | 역할 입력 문맥의 항목별 정규 JSON(문맥 카탈로그). 직접 지급한 항목과 `source_ref`로 바꾼 항목이 모두 여기에 있다 |
| `runtime/artifacts/<input_bundle>/input/implementation/<path>` | SKILL·GLOSSARY·공통 reference·역할 계약의 원문. 입력 묶음에 한 벌만 있으며 manifest `documents[].artifact_ref`가 이 경로를 가리킨다 |
| `runtime/artifacts/<input_bundle>/input/tools/<path>` | 제출 검사 진입점과 실행별 고정 코드 ZIP |
| `runtime/artifacts/<input_bundle>/input/submission/<path>` | 주 JSON·확장 스키마와 작업자에게 공개된 고정 검사 입력 |
| `runtime/artifacts/<result_bundle>/result.json` | 배정된 CLI 어댑터의 완료·실패·usage를 포함한 결과 |
| `runtime/artifacts/<result_bundle>/output.json` | schema를 통과하기 전에도 보존하는 모델 JSON 출력 |
| `runtime/artifacts/<result_bundle>/files/<path>` | workspace에서 회수한 모델 작성 파일 |
| `runtime/artifacts/<result_bundle>/output-manifest.json` | 회수한 파일의 경로·해시·크기 |
| `runtime/artifacts/<result_bundle>/omitted.json` | 누락·변경 중·reparse·읽기 실패·한도 초과 파일 |
| `runtime/artifacts/<result_bundle>/checkpoint-recovery.json` | 정상 checkpoint 또는 관찰된 부분 상태 |
| `runtime/artifacts/<formal_bundle>/proposal.lean` | 중앙 형식 검사에 사용한 Lean 원문 |
| `runtime/artifacts/<formal_bundle>/formal.json` | Lean·공리 검사 결과와 도구체인 근거 |

로컬 workspace의 주요 경로는 다음과 같다.

```text
<workspace>/control/<instance_id>/<request_id>.json
<workspace>/runs/<execution_id>/workspace/
<workspace>/runs/<execution_id>/evidence/
<workspace>/formal/<execution_id>/
```

control inbox는 요청 전달 통로이고 정본이 아니다. 실행별 workspace는 입력 사본과 모델 작성 파일을 두며, 파일은 수신·해시·artifact 저장을 통과해야 후속이 안정적으로 참조할 수 있다.

같은 snapshot의 자료는 Git 배치 읽기로 회수하고, 한 저장의 blob은 필터 없이 묶어서 쓴다. 원자료 제공 범위·바이트와 불변 artifact, 단일 부모 및 ref의 compare-and-swap 공개는 유지한다. artifact 추가 없이 등록된 기록군의 내용이 같으면 새 commit을 만들지 않는다. `updated_at`만의 차이는 상태 변경으로 세지 않는다. 과제의 착수 가능 판정(`task_readiness`)은 저장 기록군이 아니며, 역할 입력과 배정 검사가 현재 상태에서 그때 계산한다.

## CLI 상태와 보편 개념의 대응

GLOSSARY의 보편 상태가 개념의 뜻을 소유한다. 아래 값은 CLI가 저장 기록군에서 재구성하는 구현 투영이다.

같은 상태 이름만 비교하지 않는다. `ready`, `waiting`, `completed`는 아래 표가 정한 소유 대상과 함께 읽는다. `runtime.status`는 인스턴스 실행 루프, `task.status`는 한 과제, 활동 상태는 활동 record의 지속 의무를 가리킨다. CLI의 집계 표시는 이 세 대상의 상태를 새로 같은 종류로 만들지 않는다.

### 인스턴스 실행 루프 `runtime.status`

| CLI 값 | 현재 코드의 뜻 | 보편 개념과의 관계 |
|---|---|---|
| `initializing` | 불변 원입력은 보존했지만 공개 활성화 관문의 일부가 남아 있다 | 보편 인스턴스 `initializing`에 대응한다. 연구 queue나 연구 권한의 존재를 뜻하지 않는다 |
| `ready` | 다음 action을 처리할 수 있거나 다음 `run`을 기다린다 | 보편 인스턴스 `active` 안의 실행 가능 국면으로 볼 수 있다. 활동 `ready`와 같은 값이 아니다 |
| `running` | `run`이 한 action을 실제 처리 중이다 | 인스턴스가 active이고 현재 실행이 있을 수 있다는 CLI 국면이다 |
| `paused` | 일반 배정을 닫고 명시적 재개를 기다린다 | 보편 일시 정지에 대응한다. 모든 프로세스·원격 호출·정산 완료를 뜻하지 않는다 |
| `capacity_waiting` | 모든 미처리 요청이 동시 슬롯 또는 호스트 용량을 기다림 | 점유 반환·허용된 설정 변경 뒤 재검사하며 모델을 자동 대체하지 않음 |
| `waiting` | 지금 배정 가능한 action이 없고 용량 이외의 대기 사유가 있다 | 각 요청의 `dispatch_waits`에서 공급자·입력·권한 등의 원인과 다음 소유자를 확인한다 |
| `completed` | 현재 CLI가 목표 상태와 적용 학술 요구의 완료를 계산해 queue를 닫았다 | 보편 과제·활동 completed가 아니다. 정확한 목표 감사와 학술 상태를 함께 읽는다 |
| `closed` | 사용자 close가 queue를 비우고 새 일반 연구를 막았다 | 사용자 종결의 CLI terminal 상태다. 수학적 해결을 뜻하지 않는다 |

### 과제 `task.status`

`status.waiting_actions`는 저장된 행동 대기의 실제 `kind`, `reason`, `next_owner`와 당시 판정 자료를 표시한다. `coordinates`는 원 행동과 대기의 action·활동·프로필·허가·검토 자리·실행·질문·환경 등 실제 제공된 좌표다. 새 판정을 계산하거나 담당자를 추정하지 않는다. 과제 대상이 없는 행동도 JSON과 사람용 출력에 나온다. 사람용 행동 행의 사유·담당자 다음 줄에 좌표를 JSON으로 표시하며, 과거 snapshot을 조회하면 그 snapshot에 고정된 자료를 읽는다.

| 저장·공개 값 | 뜻 |
|---|---|
| `planned` | 계약을 준비하거나 독립 검토·착수 조건을 확인할 과제 |
| `active` | 선택됐거나 실행 중인 과제. 실제 실행 여부는 `active_execution_ids`로 확인한다 |
| `waiting` | 입력·후속 계획·판정을 기다리는 미완료 과제 |
| `completed` | 독립 완료 판정을 기록한 종결 과제 |
| `closed` | 범위 처분 근거로 닫은 종결 과제 |

`readiness`는 배정 대기를 제외한 계약·근거 평가다. 이것만으로 현재 선택 모집단이라고 판단하지 않는다. 실행 중이거나 종결된 과제에는 `readiness`가 null이다. 인스턴스가 `closed`나 `completed`이면 새 배정이 없으므로 모든 과제의 `readiness`가 null이고, 과제의 `status`는 종결 시점의 값으로 남는다. 결과 판정이 필요하면 `assessment_pending=true`이며 계획 입력의 `returned_task_ids`가 전건을 지정한다. `ready`, `performing`, `assessing`, `needs_revision`은 이 API가 반환하는 과제 상태값이 아니다.

`dispatch_waits`는 미시작 queue 요청의 보존된 대기 사유다. `capacity`는 동시 슬롯, `host_capacity`는 호스트 자원이다. 현재 예약 충돌은 제약 종류와 좌표를 함께 생산한다. 알려지지 않은 제약 종류를 새 대기로 대신 해석하지 않는다. 각 행의 `next_owner`, `profile_ref`, `constraint_id` 또는 `provider`로 후속을 확인한다. `status.budget`은 현행 설정의 요약이며 요청의 사유는 그 요청에 고정된 프로필·제약 판본을 따른다. 한도 변경은 재평가를 열지만 고정 프로필을 자동 교체하지 않는다. 과거 snapshot 조회는 새 예약 검사를 실행하지 않는다.

같은 이름의 source가 갱신되거나, 과제가 참조한 지식이 개정·무효화되거나, 그 지식의 신뢰 환경이 무효화돼도 `completed`·`closed` 과제의 상태와 종결 이력은 유지한다. 현재 완료 판정은 `current=false`, `invalidated_reason`으로 사용을 정지한다. 단순 `task_disposition_is(completed)` 이력 질의는 완료 사실을 유지하지만, 실제 task dependency의 착수 검사는 낡은 완료 판정을 사용할 수 없다. 새 검증 의무는 후속 과제로 연결한다. 아직 끝나지 않은 과제가 지식 변경의 영향을 받으면 `waiting`으로 돌아가 현재 착수 검사를 다시 받는다.

### 목표와 학술 후속 상태

최종 목표 상태는 `unsolved`와 `mathematically_solved`다. `unsolved`는 현재 해결 보증이 없다는 뜻이며 불가능 판정이 아니다. `mathematically_solved`에는 현재 사용할 수 있는 형식 결과, 해설과 동일성 판정, 정확한 목표 근거에 대한 필수 독립 감사가 필요하다. 비형식 조사·비교·기록 과제는 수행하고 계약에 따라 완료할 수 있지만, 그 과제의 완료를 별도 비형식 최종 목표 보증으로 올리지 않는다.

`academic_validation.status`는 적용 학술 요구와 현재 해결 근거를 함께 읽어 해석한다. 수학적 해결과 후속 원고·재현·외부 검토의 완료는 별도다. `status.knowledge`는 현재 사용할 수 있는 `K` 수와 `formal_results`, `expositions`, `identity_assessments`의 기록 수를 제공한다. 기록 수는 성공 판정 수가 아니다.

### 활동·실행·외부 operation

활동은 여러 실행에 걸쳐 의무와 대기·후속을 소유한다. 실행은 그 활동의 개별 시도다. 종료한 실행의 결과와 활동의 남은 의무를 함께 읽는다.

| 대상 | 상태 | 의미 |
|---|---|---|
| 활동 | `ready`, `working`, `waiting`, `finished` | 배정 가능, 수행 중, 조건 대기, 활동 종결을 구별한다. `finished`의 결과가 미해결일 수 있다 |
| 실행 | `queued`, `starting`, `running`, `stopping`, `ended` | 준비부터 종료까지의 실행 수명이다. 종료 종류·산출 처분은 별도 필드다 |
| 외부 operation | `prepared`, `running`, `confirmed`, `failed`, `unknown`, `cancelled` | 전송·결과 대조의 상태다. `confirmed`에서도 `succeeded`를 별도로 확인한다 |

`unresolved`는 의미 판정이나 활동 결과에 나타날 수 있으며 활동의 생명주기 값이 아니다. 실행의 `output_accepted`도 수학적 성공이나 과제 완료를 대신하지 않는다.

## 설정 계약

허용 설정 키와 각 키의 자료형·범위의 기계 정본은 저장 스키마의 설정 절 `record_schemas.config_schema()`이고, 기본값의 기계 정본은 `scripts/do_math/configuration.py`의 `DEFAULT_CONFIG`다. 모델 대응·역할 등급·세션 용량의 기본값은 `model_policy`가 정한다. 인스턴스에 실제 적용된 값은 해당 snapshot에서 재구성한 `config` 기록이 소유한다.

<a id="config-list"></a>

스킬 문서에서 설정의 기본값과 허용 값을 적는 곳은 다음 설정 목록 하나다. 다른 문서는 수치를 다시 적지 않고 이 목록을 가리킨다. 모델 대응과 모델별 작업 슬롯 수의 기본값은 [모델과 실행예산의 모델 표](모델과-실행예산.md#model-table)가, 역할별 최소 등급의 기본값은 같은 문서의 [역할 하한](모델과-실행예산.md#role-tiers)이 정본이다. "양의 정수"는 1 이상의 정수다.

| 설정 | 기본값 | 허용 값 |
|---|---|---|
| `tier_models` | 모델 표의 등급별 기본 모델 | `low`, `medium`, `high` 세 등급 전부를 비어 있지 않은 모델 이름에 대응한 객체 |
| `role_tiers` | 역할 하한의 기본 등급 | 역할 이름을 등급에 대응한 객체. 생략한 역할에는 기본값을 적용한다 |
| `session_limits` | `work`만 두고 모델별 값은 모델 표를 따른다 | `{"work": {모델 이름: 0 이상의 정수}}`. `tier_models`의 모델을 모두 명시한다 |
| `effort` | `medium` | `minimal`, `low`, `medium`, `high`, `xhigh` |
| `operator_effort` | `high` | `effort`의 값과 `max`, `ultra` |
| `call_timeout_seconds` | 600 | 양의 정수 |
| `reviewers` | 2 | 양의 정수 |
| `goal_auditors` | 2 | 양의 정수 |
| `max_input_bytes` | 2000000 | 양의 정수 |
| `max_output_repairs` | 1 | 0 이상의 정수 |
| `lean_command` | `null` | `null` 또는 항목이 하나 이상인 argv 배열. 각 항목은 NUL 문자가 없는 비어 있지 않은 문자열이다 |
| `review_rounds` | 3 | 양의 정수 |
| `review_research_limit` | 3 | 양의 정수 |
| `research_reconsider_seconds` | 86400 | 양의 정수 |
| `observation_mode` | `event_driven` | `event_driven`, `periodic` |
| `observation_interval_seconds` | 300 | 양의 정수 |
| `plan_settle_seconds` | 300 | 양의 정수 |
| `max_artifact_bytes` | 268435456 | 양의 정수 |
| `operator_enabled` | `true` | 불리언 |
| `operator_interval_seconds` | 7200 | 양의 정수 |
| `operator_timeout_seconds` | 5400 | 양의 정수 |
| `scholarly_enabled` | `true` | 불리언 |
| `scholarly_server` | `null` | `null` 또는 `command`·`args` 객체 |
| `claude_only_assigned_model` | `false` | 불리언 |
| `provider_retry_initial_seconds` | 300 | 양의 정수 |
| `provider_retry_max_seconds` | 7200 | `provider_retry_initial_seconds` 이상의 양의 정수 |
| `finish_notice_seconds` | 60 | 양의 정수 |
| `tool_review_window_seconds` | 없음 | 양의 정수 |
| `self_check_response_window_seconds` | 없음 | 양의 정수 |
| `no_progress_limit` | 없음 | 양의 정수 |
| `import_rework_limit`, `selection_failure_limit`, `exhaustion_empty_limit`, `proposal_version_limit`, `contract_revision_limit` | 없음. 설정하지 않은 계보에는 횟수 한도를 두지 않는다 | 양의 정수 |
| `host_resources` | 없음 | `null` 또는 아래 호스트 자원 설정 |

기본값이 "없음"인 설정은 제품이 값을 대신 정하지 않는다. 이 목록에 없는 키는 거부된다.

`host_resources`는 선택적인 구조화 설정으로 `constraint`와 `demands_by_role`을 받는다. 제약은 `execution_profiles.host_constraint(host_id=..., limits=..., control_reserve=..., authority_refs=...)`가 내용에서 계산한 용량 제약 식별자(CP ID)를 포함해야 한다. `host_id`는 실제 로컬 호스트 이름이다. `limits`의 `jobs`는 동시 Job 수, `memory_bytes`는 committed memory 바이트, `cpu_rate_basis_points`는 1/10000 단위의 CPU 비율이며 최대 10000이다. 같은 세 단위의 `control_reserve`는 각 한도 이하이고 작업이 차용하지 않는다. `demands_by_role`은 호스트 상한을 적용하는 역할 전건을 키로 사용하고 역할마다 `jobs=1`, 양의 `memory_bytes`, 1~10000의 `cpu_rate_basis_points`를 명시한다. 상한을 적용하지 않는 `formal_check`, `trust_check`, `trust_activate`의 요구량은 설정하지 않는다. 숫자는 사용자 승인 값에서 받으며 자동 기본 상한은 없다.

`authority_refs`에는 저장된 사용자 결정·출처 ID를 넣는다. 직접 제출하는 설정 원문 자체를 승인 출처로 삼으려면 `configuration:request`를 명시한다. 중앙은 그 설정을 불변 user 출처로 보존하고 이 참조를 실제 출처 ID로 치환한 뒤 제약 ID를 다시 계산한다. 원 설정에 없던 수치나 권한을 추가하지 않는다. 초기화에는 이 방법으로 출처까지 함께 보존할 수 있다. 기존 출처를 지정하면 실제로 존재하는 사용자 출처인지 검증한다.

다음 예는 사용자가 수치와 역할별 요구를 이미 정한 `approved-host.json`에서 공개 설정 파일을 만드는 절차다. 입력은 `host_id`, `limits`, `control_reserve`, `demands_by_role` 네 필드를 가진다. 생성은 인스턴스에 적용하지 않으며, 생성 파일을 기존 `init` 또는 `configure`의 `--config-file`로 전달한다.

```python
import json, sys
from pathlib import Path
sys.path.insert(0, '.agents/skills/do-math/scripts')
from do_math.execution_profiles import host_constraint
approved = json.loads(Path('approved-host.json').read_text(encoding='utf-8'))
constraint = host_constraint(host_id=approved['host_id'], limits=approved['limits'],
    control_reserve=approved['control_reserve'], authority_refs=['configuration:request'])
settings = {'host_resources': {'constraint': constraint,
                              'demands_by_role': approved['demands_by_role']}}
Path('host-config.json').write_text(json.dumps(settings, ensure_ascii=False, indent=2), encoding='utf-8')
```

호스트 설정의 채택·변경·해제는 사용자 권한으로 실행기가 정지하고 모든 execution이 ended이며 held 예약이 없을 때 적용한다. inbox의 요청도 실제 적용 시 이 조건을 다시 검사한다. 같은 설정의 재적용은 제약을 바꾸지 않는다. `host_resources=null`은 해제이고, 부분 configure에서 필드를 생략하면 기존 설정을 유지한다. `operator`는 호스트 설정을 바꿀 수 없다. 과거 제약·프로필은 종료 실행의 근거로 남긴다. 바뀐 호스트 승인과 맞지 않는 과제 프로필은 재준비·독립 계약 검토로 갱신하며, 이미 고정된 검토 프로필은 덮어쓰지 않고 미완료 사유와 함께 계획으로 반환한다. `formal_check`, `trust_check`, `trust_activate`에는 호스트 상한을 붙이지 않는 현행 Lean 계약을 유지한다.

중앙 Lean 검사는 완료까지 기다리며 실행 시간·메모리·CPU·출력량 상한을 적용하지 않는다. 정지 요청이나 실행 권한 변경에 따른 취소는 유지한다. 공통 의존 선언의 타입·본문은 한 검사에서 한 번만 전송한다. 결과는 선언별 의존 폐포(`dependency_closure`)와, 폐포들의 합집합에 든 상수마다 타입·본문의 해시 하나를 담은 표(`dependency_evidence`)로 보존한다. 선언별 공리는 폐포 안의 공리 상수로 도출해 `#print axioms` 출력과 대조하며, 둘이 다르면 검사는 실패한다. `verified` 결과의 원출력에서는 해시로 환원한 의존 본문 행을 빼고 나머지를 모두 보존하며, 그 밖의 결과는 원출력 전체를 보존한다.

일반 형식 검사와 신뢰 환경 전환 검사는 기존 병렬 호출 관리에서 실행하며, 두 종류의 동시 실행 수를 합해 인스턴스당 최대 한 건으로 제한한다. 메인은 고정 입력·프로필·권한과 Job 식별자를 저장한 뒤 계산 시작을 허용한다. 계산 중에도 제어 요청과 독립 AI의 배정·완료를 처리한다.

`run`에는 전체 실행 시간 제한이 없다. `--max-steps`는 새 action 시작 수만 제한하며 진행 중 실행의 종료·결과 회수는 계속한다. 작업 예산 AI와 중앙 Lean 검사는 경과 시간만으로 취소하지 않는다. Windows 연구 예약은 `ExecutionTimeLimit=PT0S`를 명시하고 운영 담당 예약은 기존 유한 제한을 유지한다.

정지·종결·권한 회수·필수 전제 변경 뒤에 도착한 해당 실행의 결과는 보존하되 정상 승인으로 편입하지 않는다. 예약과 슬롯은 로컬 종료가 확인된 뒤 반환한다. 종료가 확인되지 않은 실행은 기존 복구 절차에 남긴다.

- 실행 선택: 세션 모드는 `tier_models`의 상·중·하 모델 대응과 `role_tiers`의 역할별 최소 등급을 사용한다. 난이도·중요도·근거의 저작과 선택은 [모델과 실행예산](모델과-실행예산.md)을 따른다. `effort`는 공통 추론 노력이다.
- 작업 용량: `session_limits.work`는 작업 역할 실행의 모델 이름별 동시 세션 상한이다. 값 0은 그 모델의 새 작업 실행을 대기시킨다. 운영 역할은 슬롯을 예약하지 않으므로 이 상한을 쓰지 않는다. 실행 이력은 계속 보존한다.
- 운영 AI 실행 기한: `call_timeout_seconds`는 실행기 안의 운영 AI 실행 하나에 적용한다. 실패 전용 설치 복구 AI에는 이 값 대신 아래 `operator_timeout_seconds`를 적용한다.
- 작업 AI 실행 종료: 연구 수행·보충 조사·작업 계약 검토·동일성 검토·목표 감사에는 실행 기한을 적용하지 않는다. 이 실행들은 제출, pause·close, 권한·입력 변경과 수락된 운영 처분에 따라 종료한다. 하위 CLI 요청의 `max_runtime_seconds=null`도 기한 없음을 뜻하며, 0이나 임의의 큰 시간값으로 바꾸지 않는다.
- 그 밖의 반복 한도: 출력 수리 횟수, 검토 회차, 검토의 보충 조사 한도와 반복 계보별 횟수 한도는 설정 목록의 대응 설정이 정한다. 계보별 한도의 뜻은 GLOSSARY의 「반복 교정 문턱」을 따른다.
- 입력·산출: 모델 입력과 한 실행의 artifact 회수 바이트 한도를 정한다.
- 형식 검사: `lean_command`는 argv 배열이며, 없으면 실행기가 지원 경로에서 Lean을 탐색한다. 탐색은 `setup_lean.py`가 준비를 마친 Mathlib 프로젝트, `PATH`의 `lean`, 같은 위치의 Lean 단독 툴체인 순서다. 탐색은 내려받지 않으며 준비는 README의 `setup_lean.py`가 맡는다. 중앙 공리 감사는 활성 신뢰 환경에 기록된 허용 공리(`propext`, `Classical.choice`, `Quot.sound`)를 기준으로 하며, 이 목록은 설정으로 바꾸지 않는다.
- 관찰: 설정은 새 프로필을 저작하는 입력이다. 실행은 선택한 프로필의 모드·고정 window와 `{source,operator,subject_kind,unit}` 항목으로 이루어진 `rule_bindings`를 사용한다. 실제 실행 ID와 카운터 이름은 실행 문맥에서 결박한다. 연구 수행의 자기 점검, 다른 작업 예산 AI의 주기 관찰, 운영 AI·기계의 `deadline_only` 책임을 구별한다. `tool_review_window_seconds`, `self_check_response_window_seconds` 같은 필요한 값이 없으면 임의 기본값이나 작업자의 timeout으로 대신하지 않는다. 아래 관찰 계약과 「공통 실행」·「자기 점검」 문서를 따른다.

프로필 채택·활성화와 실행 직전은 같은 관찰 설정 검사를 사용한다. 주기·사건 관찰에는 `tool_review_window_seconds`·`observation_interval_seconds`, 연구 수행에는 `self_check_response_window_seconds`가 필요하다. 누락이나 잘못된 값은 `observation_configuration`과 역할·프로필 ID·필드별 오류로 표시한다. 초기화의 `activation.observation_errors`는 활성화 검사에서 확인한 세부 오류다. 초기화에서는 아직 없는 과제의 규칙을 요구하지 않는다. 이미 활성화된 인스턴스에서 설정 문제를 만나면 해당 실행을 기다리게 하고 다른 허용된 역할은 계속 처리한다. 새 설정 프로필은 원래 프로필과 함께 보존하며, 과제에 고정된 참조의 변경은 재준비와 새 독립 계약 검토를 거친다.
- 계획과 착수: `plan_settle_seconds`는 연구 계획이 대기·실행 중인 작업 계약 검토의 종료를 기다리는 상한이며, 기다리는 계획의 `dispatch_wait.kind`는 `plan_settle`이다. 사용자·독립 운영이 요청한 계획에는 적용하지 않는다.
- 독립 운영: `operator_enabled`는 예약 감독의 활성 여부이고, `operator_interval_seconds`는 정상 감독의 주기다. `operator_timeout_seconds`는 설치 복구 AI 호출 하나의 기한이며, 운영 예약 작업의 시간 상한은 이 값에 종료 여유 300초를 더한 값이다. `operator_effort`는 설치 복구 AI의 추론 노력이다. 정상 감독은 모델 없이 상태·예약·HOLD를 검사하고 엔진 작업을 요청한다. 엔진을 읽을 수 없는 실제 실패가 보존됐거나 운영 점검의 설치 결함 진단이 수락됐을 때 복구 AI를 열며, 이 AI는 `role_tiers.recovery` 등급에 대응한 `tier_models`의 모델로 작업 슬롯을 예약하지 않고 실행된다. 이는 내부 `research_reconsider_seconds`가 정하는 후보 밖 탐색 주기와 별개다.
- 학술자료: `scholarly_enabled`는 학술자료 도구를 실행에 연결할지 정한다. `scholarly_server`는 null 또는 `command`·`args` 객체이며 초기화 때 명시 설정이나 Codex 설정의 scholarly 항목에서 회수한다. command/서버 파일 경로는 실행 위치와 무관하게 사용할 수 있도록 고정한다. 다른 MCP와 사용자 훅은 하위 연구 실행에 자동 상속하지 않는다. 서버의 자료 저장 위치는 실행별 `scholarly-data/`로 지정한다.

모델 이름이 `claude:`로 시작하면 그 접두어를 제거해 Claude CLI의 `--model`에 전달한다. `claude-`로 시작하는 전체 ID는 그대로 Claude에 전달하고 나머지는 Codex에 전달한다. 모델은 `tier_models`로 설정한다. `claude:` 뒤에는 비어 있지 않은 모델 이름이 필요하다. 별칭과 전체 ID를 포함해 동일 모델의 설정 표기를 통일한다. 슬롯은 접두어를 포함한 원래 설정 문자열별로 계산하며 CLI가 해석한 실제 모델 ID를 기준으로 합치지 않는다.

Claude는 기존 CLI 로그인을 사용한다. `PATH`에서 실행 파일을 찾으며 `CLAUDE_CONFIG_DIR`와 Windows의 `CLAUDE_CODE_GIT_BASH_PATH`를 전달한다. API 키·API 공급자 변경 환경변수는 전달하지 않는다. `--setting-sources`를 비우고 사용자 훅·자동 기억·스킬 호출·내부 Agent/Task 도구를 비활성화하며, `--strict-mcp-config`로 인스턴스에 고정된 scholarly만 연결한다. Claude만 사용하는 인스턴스도 scholarly의 자동 탐색 위치는 작업 경로에서 부모 방향으로 찾는 `.codex/config.toml`, 이어 `CODEX_HOME/config.toml`(미설정이면 사용자 홈의 `.codex/config.toml`) 순서이며, 다른 위치의 설정은 `scholarly_server`에 직접 지정한다.

`effort`와 `operator_effort`의 허용 값은 이 절의 설정 표가 정한다. 그 가운데 `minimal`과 `ultra`는 Claude에 전달할 수 없다. Claude worker는 지원하지 않는 수준을 CLI 시작 전에 거부한다. 모델 접근 권한과 해당 모델의 노력 수준 지원은 실제 CLI 응답으로 확인하며, 실패를 다른 모델·수준으로 우회하지 않는다.

다음은 일부 설정을 명시하는 예다. `init`에서 생략한 필드는 코드의 기본값을 사용하고, `configure`에서 생략한 최상위 필드는 기존 값을 유지한다.

```json
{
  "tier_models":{"high":"gpt-6-astra","medium":"gpt-5.6-sol","low":"gpt-5.6-terra"},
  "session_limits":{
    "work":{"gpt-6-astra":3,"gpt-5.6-sol":3,"gpt-5.6-terra":3}
  },
  "effort":"medium",
  "call_timeout_seconds":600,
  "lean_command":["C:/Lean/bin/lean.exe"],
  "observation_mode":"event_driven"
}
```

`configure`는 기존 설정 위에 제공 필드를 덮어쓴 뒤 전체 설정을 다시 검사한다. 알 수 없는 필드는 거부한다. 운영자 출처(`--origin operator`)의 `configure`는 `session_limits`, `tier_models`, `role_tiers`, `claude_only_assigned_model`, `host_resources`를 바꿀 수 없으며, 이 키를 바꾸는 요청은 접수 단계에서 거부된다. 각 설정의 자료형·범위는 설정 목록을 따르며, 저장된 설정도 적재할 때 같은 설정 절로 검사한다. 자료형·범위 오류는 `config/<키 경로>: <검사 메시지>` 형식의 문구로 반환된다. `tier_models`와 `session_limits`는 지정할 때 해당 맵 전체를 전달한다. 역할 최소 등급은 지정한 `role_tiers` 항목을 사용하고 생략한 역할에는 기본값을 적용한다. 정확한 현재 값은 고정 snapshot의 등록된 설정 기록 경로를 `query --files`로 찾은 뒤 `read --path`로 확인한다.

모델별 동시 세션 용량과 모델 대응은 `configure --config-file`로 함께 적용한다.

JSON status의 `budget`과 역할 입력의 `resources`는 `budget_unit=concurrent_sessions`와 함께 작업 슬롯의 모델별 표 하나로 `limit`, `used`, `available`, `execution_ids`를 제공한다. 운영 역할과 설치 복구 AI는 슬롯을 예약하지 않으므로 이 표의 점유에 들어가지 않으며, 모델 없는 정상 감독도 마찬가지다. status의 `execution_attempts`는 누적 실행 이력을 작업 역할(`work`)과 그 밖의 역할(`operations`)로 나누어 센 값이며 세션 상한과 별개다. `active_executions`와 `active_execution`은 저장 필드가 아니라 status가 조회한 snapshot에서 계산하는 값이다. `active_executions`는 종료되지 않은 내부 실행 ID 전건이고, `active_execution`은 그 첫 ID이거나 없으면 `null`이다. `capacity_waiting`에는 슬롯이나 호스트 용량을 기다리는 미시작 요청의 모델 배정을 표시한다.

한도를 점유보다 낮추면 새 배정을 대기시킨다. 현재 실행의 모델은 고정하고 종료를 강제하지 않는다. 설정 변경 권한이 없는 운영 AI는 세션 상한·모델 대응·역할 등급을 바꿀 수 없다. 모델별 동시 세션 한도와 모델 대응의 변경에는 예산 모드 전환이나 전체 실행 종료가 필요하지 않다. 별도로 설정한 호스트 자원의 변경·해제에는 앞의 호스트 설정 절이 정한 정지·미종료 실행·예약 조건을 적용한다. 설정 변경이 HOLD를 해제하지는 않는다. 실행 시간·검토 회차·행동 허가는 각각의 계약을 따른다.

## 명령 표면

### `init`

```text
init --repository PATH [--create-repository] --workspace PATH
     (--goal TEXT | --goal-file PATH) [--title TEXT]
     [--source PATH ...] [--config-file PATH] [--effort VALUE]
     [--request-text TEXT | --request-text-file PATH]
```

`init`은 원입력과 설정·초기 source를 보존하고 `initializing` 인스턴스를 만든다. `--create-repository`는 새 경로나 빈 디렉터리에만 Git 저장소를 만든다. 생성 응답의 `instance_id`와 `snapshot`을 보존하고 이후 같은 인스턴스에 제어를 보낸다. 생성 시 grant와 연구 queue는 비어 있다.

원입력은 `lifecycle.immutable_input`의 `text`, `sha256`, `bytes`에 하나의 정확한 UTF-8 표현으로 보존한다. 수학 목표와 전체 요청이 다르면 `--request-text` 또는 `--request-text-file`을 지정한다. 이 원문을 의도 해석과 독립 검사의 대상으로 삼고, 수학 목표는 `runtime.inputs`의 최초 입력 행에 있는 `config` 객체의 `goal`로 별도로 보존한다. 이는 연구 설정 레코드의 필드가 아니다. 별도 원문을 지정하지 않은 경우에는 goal 자체가 원문이다. 결정론 JSON은 문자열과 객체 키의 코드 포인트열을 바꾸지 않으며 NFC 사본이나 별도 Base64 원문을 만들지 않는다. 바이트 보존과 그 원문을 의미 해석에 실제 사용했다는 보증은 별개이므로, 문자열의 철자·코드 포인트 자체가 의미인 입력에서는 해석·피복·검사 대상이 이 `text`와 일치하는지 확인한다.

공개 명령의 실행 순서, 완전한 요청 객체, 현행 프로필의 능력 관측과 채택, 능력·신뢰 근거의 출처와 현재 승인 연결의 한계는 [초기화 운전](초기화-운전.md)을 따른다. 초기화의 probe와 채택은 대상 설정을 `config_sha256`(`status`의 `result.config_sha256`)으로 지정하며, 현재 설정의 해시와 다르면 거부된다. 활성화는 채택된 통치·설정·정책, 초기화와 연구의 별도 권한, 채택된 설정의 역할별 현행 프로필과 그 현재 능력 증거, 실제 적용된 독립 의도 검사, 활성 신뢰 환경·복구 검사를 대조한다. 이미 채택된 값은 같은 근거를 재사용하며, 연구 권한이나 미확인 증거를 기본값에서 추론하지 않는다.

독립 운영이 활성인 설정이면 CLI는 저장 뒤 Windows 작업 두 개를 등록한다. 예약 등록이 실패해도 이미 생성된 인스턴스를 다시 만들지 않는다. 응답에 남은 ID·snapshot과 실패·재조정 명령을 사용한다. 저장과 운영체제의 예약 효과는 별도의 성공 조건이다. 재조정 명령과 작업자에게 지급하는 검사 명령(`submission_contract.command`, `formal_verifier.preview.command`)의 Python은, 실행기가 예약 작업에서 콘솔 없는 `pythonw.exe`로 돌 때에도 같은 설치의 `python.exe`다. PowerShell은 `pythonw.exe`를 기다리지 않고 그 출력도 보여 주지 않기 때문이다.

### `run`, `status`, `check`, `profile`

`init`은 수학적 질문을 연구 목표로 받는다. 초기화가 완료된 뒤 형식 결과·동일성 판정·목표 감사로 해결 여부를 판정한다. 문헌 조사·계산·비형식 과제는 이 목표를 위한 작업 계약으로 수행한다.

- `run [--max-steps N] [--watch] [--until-active]`는 writer lock 안에서 control을 적용하고, 사라진 실행을 복구하며, 모델별 용량 안에서 AI action을 병렬로 실행한다. 쓰기 전에는 현재 기록이 참조하는 보존 artifact가 있고 저장 길이가 기록과 같은지 확인한다. 제어 적용도 같은 사전 점검을 거친다. 전 바이트 대조는 `check`가 맡는다. 형식·신뢰·외부 기계 action과 상태 반영은 소유 실행기가 처리한다. `N`은 새로 처리할 action 수의 양의 상한이며, 도달한 뒤에는 새 일반 action을 열지 않고 이미 시작한 모델 호출을 회수한다. 그 호출의 생존·복구에 필요한 live 운영 점검은 슬롯을 예약하지 않는 운영 역할로 계속 처리하며 일반 step 수에 넣지 않는다.
- `--until-active`는 lifecycle이 active가 되면 연구 action을 배정하기 전에 반환한다. 이미 active인 인스턴스에도 새 연구를 시작하지 않는다. 누락 관문이 있는 반환은 활성화 성공이 아니다.
- `select-profile --role ROLE [--task TK-ID] [--snapshot OID]`는 현재 역할 하한·과제 평가·허용 프로필을 실제 선택과 같은 규칙으로 대조한다. 반환은 선택과 정확한 프로필 원문이며 실행·채택은 하지 않는다.
- `prepare-import-approval --import-id IM-ID [--snapshot OID] --output NEW-PATH`는 독립 검사를 통과한 현행 수입의 정확한 승인 좌표를 새 파일로 생성한다. 파일 생성은 승인·적용이 아니며, 실제 결정은 기존 `decision --file`을 사용한다.
- `status [--json] [--snapshot OID]`은 같은 Git snapshot에서 연구 상태·예약·예산·공급자 대기를 재구성한다. `config_sha256`은 그 snapshot의 설정 내용 해시이며, 초기화의 probe와 채택이 대상 설정을 지정할 때 쓴다. 저장된 기록을 보고하며, `inspection`은 기록 관계와 참조 artifact의 존재·저장 길이만 확인한다. 보존 artifact를 다시 읽는 제출 검사 진단은 계산하지 않고 `submission_checks.status=not_evaluated`로 둔다. 실제 새 배정은 최신 머리에서 권한과 여유를 다시 검사하고 예약한다. 별도 운영 로그나 현장 프로세스 관측을 함께 읽을 때에는 그 관측 시각과 범위를 구별한다. JSON 필드는 README의 운영 표를 따른다. `--snapshot`을 주면 그 과거 snapshot을 같은 필드로 재구성하며, 조회 순간에 이 호스트에서 관측하는 필드는 null이다.
- `check [--snapshot OID] [--kinds AREA ...]`는 상태 관계와 보존 artifact의 전 바이트 해시·크기를 검사하고 제출 검사 진단을 계산해 `{passed, errors, ...}`를 반환한다. 결함이 있으면 exit 1이다. `--kinds`는 검사할 점검 영역의 이름이며, 생략하면 등록된 영역 전건을 검사한다. 등록되지 않은 영역 이름은 `inspection.status=incomplete`와 exit 1로 반환된다. 자연어 의미를 새로 검증하지 않는다.
- `status`의 `inspection`과 `check`는 적재 검증을 통과한 상태만 본다. 저장 스키마·ID 유일성·수명 주기 관문 같은 적재 조건은 상태를 읽을 때 이미 검사했으므로 다시 보고하지 않으며, 각 점검 영역의 `checked_invariants` 첫 항목 `load-time state contract validation`이 이 사실을 가리킨다. 역할 입력의 보존본 비교는 `start_import_input` 영역이 입력 manifest로 수행한다. 참조한 artifact가 저장소에 없으면 해당 영역의 `artifact is missing` 결함으로 보고한다.
- `profile [--provider codex|claude] [--codex-path PATH | --claude-path PATH]`은 선택한 CLI 표면을 조사한다. 기본 공급자는 `codex`이며 경로 옵션은 선택한 공급자와 일치해야 한다. 인스턴스 인자는 받지 않는다. `verified=true`는 명령 표면의 확인이며 로그인·모델 이용 가능성이나 실제 작업 성공의 증거는 아니다.

### `pause`, `resume`, `close`, `input`, `configure`, `request`

- `pause|resume|close [--reason TEXT]`는 제어 요청을 inbox에 기록한다. `resume`은 CLI `closed`와 `completed`를 열지 않는다.
- `input (--text TEXT|--file PATH) [--responds-to QU-ID ...]`는 비어 있지 않은 사용자 원문을 보존하고 `intent_interpretation`을 먼저 queue에 넣는다.
- `configure --config-file PATH`는 지원 설정만 갱신한다. 목표·정책·grant·학술 요구는 각각 `decision`을 사용한다.
- `request --role ROLE [--target ID] [--reason TEXT]`는 모델을 호출하지 않고 새 action을 queue에 접수한다. 새 운영 요청은 기존 운영 요청 뒤에 배정한다. 지원 role은 `research_preparation`, `research_plan`, `supplemental_research`, `operational_review`, `maintenance`다. 보충 조사는 현재 `ready` 과제 ID, 운영 점검은 존재하는 execution ID를 target으로 요구한다.
- `request --retry-action AC-ID [--request-id UC-ID]`는 입력 초과로 보류된 action 또는 초기화 중 기술적 실행 실패로 끝난 원입력의 의도 해석을 명시적으로 다시 처리한다. `--role`, `--target`, `--reason`와 함께 쓸 수 없다. 원 action ID와 owner activity를 유지하고 현재 채택 프로필과 권한을 다시 검사한다. 정상 종료한 native 최종 응답이 정확한 원문·실행 근거와 함께 보존돼 있으면 현재 재시도 권한으로 그 응답을 중앙 접수·편입에 재사용한다. 이 경우 새 모델 실행을 만들지 않으며 원 실행의 종료 시각·원 결과 참조·실패 이력을 보존한다. 재사용 조건을 충족하는 정상 응답이 없으면 같은 원입력과 활동을 잇는 새 실행을 배정한다. 기존 봉인 후보를 다른 final로 대체하거나 오류·중단 응답을 정상 응답으로 취급하지 않는다.

입력 초과의 재시도는 원 grant를 유지하며 아래 입력 크기·질문 계약을 따른다. 초기 해석의 재시도는 `initializing` 상태에서 최초 불변 입력을 대상으로 한 `execution_failure`에만 적용한다. 전 실행이 `execution_incomplete`로 끝났고 로컬 종료가 확인됐으며 그 실행의 예약이 회수돼야 한다. 원 활동은 대기 중이어야 하고 같은 해석이나 그 실패를 진단하는 실행이 진행 중이면 거부한다. 보존 응답을 재사용하든 새 실행을 배정하든 현재 초기 운영 권한을 확인하고 실패 실행·원 대기·시작하지 않은 이전 진단을 이력으로 보존한다. 새 실행이 필요하면 현재 채택 초기 프로필로 배정하고 `continuation_of`로 선행 실행을 연결한다.

`request --assessment-reassessment-file PATH`는 원 동일성 판정의 결함을 보고한다. JSON 파일에는 정확한 `assessment_id`, `assessment_sha256`, `evidence`를 넣는다. `evidence.kind=author_context`는 원 검토자의 `execution_id`를, `independent_objection`은 봉인된 독립 검토의 `review_cycle_id`, `result_key`, `finding_id`를 가리킨다. 실행기는 원 판정과 근거의 결박을 검사하고, 적격 결함이면 판정 사용을 정지한 뒤 원 정책에 따른 유한 재심사를 연다. 일반 보고는 사용 효력을 바꾸지 않으며 같은 근거의 재전송은 기존 재심사를 재사용한다. 이 형식은 `--role`, `--retry-action`, `--target`, `--reason`과 함께 쓰지 않는다. 파일을 제출했다는 사실만으로 원 판정이 잘못됐다고 확정하지 않는다.

`request`는 새 권한이나 완료 판정을 만들지 않는다. `--retry-action` 접수는 입력 초과 해소 선언도 아니다. `completed`와 `closed` 인스턴스에는 새 요청을 넣지 않는다.

사용자 출처의 pause는 `runtime.user_pause`에 요청 ID·이유를 보존한다. operator 출처의 resume은 유효한 user_pause가 있으면 거부한다. 사용자 resume은 이 표시를 해제한다. 일반 resume은 `waiting_actions` 중 `output_validation`·`execution_failure`·`revision_dependency`를 재실행하지 않는다. 진단이나 새 역할 요청으로 이어 가며, 위 조건을 충족하는 초기 해석 실패에는 `request --retry-action`을 사용한다. 성공한 후속 실행은 대응하는 실패 행동을 해결 이력으로 옮기고 원 실패 실행·산출을 보존한다.

### `operator`

```text
operator install|uninstall|status|start|start-operator|check|probe|engine|wake|hold|release
         --repository PATH --instance ID [--workspace PATH] [--reason TEXT]
```

workspace는 인스턴스에 보존된 경로와 같아야 한다. `install`은 현재 설정으로 모델 없는 정상 감독과 주문형 연구 엔진의 두 예약 작업을 등록하고, `uninstall`은 해당 두 작업과 인스턴스의 일회성 wake 작업을 제거한다. `status`는 실제 등록 상태를 읽는다. `start`는 별도 연구 엔진 작업을, `start-operator`는 별도 정상 감독 작업을 시작한다. 명령 접수 뒤 실제 실행 결과를 다시 확인한다.

`check`는 상태·기록·HOLD·예약 상태를 모델 없이 감독하고 실행 가능할 때 엔진 작업을 요청한다. 엔진 상태를 읽지 못했거나 보존된 최근 엔진 실패 또는 수락된 설치 결함 진단이 있을 때 실패 전용 설치 복구를 열 수 있다. `probe`는 같은 상태를 읽되 복구나 예약 변경을 하지 않고 `model_called=false` 또는 실패 증거를 반환한다. `engine`은 예약 작업에서 연구를 운전하는 진입점이며 HOLD·사용자 정지·현재 상태를 다시 검사한다. `hold`는 고유 ID의 HOLD와 사용자 pause를 만들고, `release`는 같은 HOLD가 만든 현재 사용자 정지에만 재개를 적용한다.

예약은 현재 Windows 사용자의 Interactive 로그인, IgnoreNew, StartWhenAvailable로 구성한다. 작업 이름은 저장소·인스턴스로 구별한다. 운영과 연구 프로세스는 서로 별도 예약 작업에 속한다. 운영 예약의 시간 상한은 [설정 계약](#config-list)의 독립 운영 설명대로 운영 timeout에 종료 여유를 더한 값이다. 연구 예약은 `ExecutionTimeLimit=PT0S`로 실행하며, 두 작업의 중복 억제와 연구 저장소의 writer lock을 함께 사용한다.

예약 bootstrap은 설치 시점의 파일 manifest·해시에 고정되며 실행할 때 재분석 지점과 경로를 검사한다. 실패 복구는 writer lock과 설치 유지보수 lock, 종료된 선행 실행, 고정 복구 프로필·능력 증거와 착수 조건(공급자 대기, 설정된 호스트 자원)을 검사한 뒤 live 설치만 수리한다. 연구 기록·사용자 설정·예약 작업을 고치지 않고, 설치 정적 검사가 통과한 경우에만 lock을 놓은 뒤 엔진 재시작을 요청한다. 이 경계는 같은 사용자 OS 권한 안의 지시 계약이지 인증된 호출자나 강한 격리가 아니다. 로그와 복구 근거는 `workspace/operator/` 아래에 있다. 복구 AI의 호출·CLI 사용량은 engine 내부 운영 호출과 구별하며, 독립 운영 계약은 `계약/독립-운영.md`가 소유하고 내부 `operational_review`를 대신하지 않는다.

## 구조화 제어 JSON

`decision`, `knowledge`, `trust`, `external`, `conversation`은 `--file`의 JSON 객체를 control inbox에 보존한 뒤 writer가 현재 전제를 검사해 적용한다.

구조화 JSON은 한 번 바이트로 읽어 해석한 payload와 같은 정확한 원문을 함께 control에 전달한다. 특히 사용자 결정은 JSON에서 계산된 요약이 아니라 그 파일 원문으로 보존된다. 줄 끝·코드 포인트를 바꾼 복사본으로 승인 원문을 대신하지 않는다.

### `decision`

#### 검사된 수입의 사용자 승인

독립 검사가 승인한 수입을 적용하려면, 검사된 `intent_imports` record에서 정확한 `import_id`, `bundle_sha256`, `check_sha256`, 비어 있지 않은 각 unit의 ID와 payload의 canonical hash를 읽는다. 다음 객체만이 그 수입의 승인 원문이다. `unit_hashes`에는 승인하려는 모든 비어 있지 않은 unit을 정확히 한 번 넣는다.

```json
{
  "kind": "import_approval",
  "import_id": "IM-실제-조회-ID",
  "bundle_sha256": "검사된-묶음-해시",
  "check_sha256": "검사-해시",
  "unit_hashes": {
    "IU-실제-단위-ID": "그-payload의-canonical-hash"
  }
}
```

이 객체를 JSON 파일로 보존하고 공개 CLI에 그대로 준다.

```powershell
python $dmCli decision --repository $dmRepository --instance $dmInstance --file 08-import-approval.json
```

CLI는 파일을 한 번 읽어 payload와 그 정확한 원문을 함께 전달한다. 적용기는 사용자 출처·`import_approval` 종류·수입 묶음·검사·단위 해시의 정확한 일치와 비어 있지 않은 승인 원문을 검사한 뒤, 그 하나의 검사된 묶음만 적용한다. 해시를 계산하거나 기록에서 읽는 일은 사용자 승인 결정을 만들지 않는다. 반대로 그 값들이 바뀌었거나 원문이 없으면 적용되지 않으며, 새 해석이나 새 검사를 승인 대신 실행하지 않는다.

적용 뒤에는 `query --kind intent_imports`의 응답이 돌려준 `snapshot`을 읽고, 그 OID를 `read --snapshot OID --id IM-...`에 넣어 같은 snapshot의 수입·검사 record와 적용 결과를 읽는다. `status --json`으로 초기화 관문과 다음 queue를 확인한다. 이 승인 경로는 이미 검사된 봉인 묶음의 편입 경로이므로, 적용만을 위해 `input`이나 `run`으로 원문 해석을 다시 시작하지 않는다.

#### 목표와 정책

목표 변경은 `kind="charter"`와 새 헌장 `record`를 제출한다. 먼저 같은 snapshot에서 활성 헌장을 조회·읽는다. 새 `record`에는 새 `id`, `kind="charter"`, 다음 `revision`, 대체할 활성 헌장 ID의 `supersedes`, 완전한 `content`를 쓴다. 기존 `content`에서 사용자가 승인한 목표·범위·성공 기준의 변경만 반영하고, 다른 조건과 학술 요구는 보존한다. 저장된 `status`, `approval_ref`, `source_ref`, `content_sha256` 같은 메타데이터는 새 제안에 복사하지 않는다. `content`의 필수 구조는 [입력 소비자](입력-소비자.md)의 charter 계약을 따른다.

정책도 `kind="policy"`와 완전한 새 `record`를 사용한다. 다음 예시의 ID·범위·근거·문면은 실제 승인한 값으로 바꾼다.

```json
{
  "kind": "policy",
  "record": {
    "id": "PO-source-evidence",
    "kind": "policy",
    "revision": 1,
    "supersedes": [],
    "content": {
      "rule_id": "source-evidence",
      "text": "사용한 문헌은 내부 보존 사본과 정확한 절 좌표를 남긴다.",
      "scope": ["연구 수행"],
      "reason_refs": ["CH-실제-현행-헌장-ID"],
      "audit_refs": []
    }
  }
}
```

같은 `rule_id`의 활성 정책을 바꾸려면 새 ID와 전체 문면을 제출하고 `supersedes`에 그 정책 ID를 넣는다. 적용기는 대체 대상의 종류·활성 상태와 새 ID를 검사한다. 승인된 목표·정책 변경은 영향받은 미완료 과제의 현행 통치 근거를 다시 확인하게 하며, 후속 준비 또는 계획으로 연결한다.

#### 반복 보류의 계속 결정

채택된 반복 한도 뒤의 계속은 `decision --file`에 `kind=repetition_continue`인 JSON을 제출한다. 필수 값은 `lineage`, `lineage_id`, `hold_event_ref`, `allowed_action`이다. `lineage`는 `import_rework`, `selection_failure`, `exhaustion_empty`, `proposal_version`, `contract_revision` 중 하나다. 현행 `repetition_hold`의 계보와 근거 사건을 그대로 사용한다. 제안·계약 판본 계보에서는 현재 집계 이력의 마지막 판본을 `baseline_revision`으로 함께 지정한다.

`allowed_action`은 승인할 현재 큐 또는 대기 action의 범위 객체다. 그 action에 존재하는 `id`, `role`, `target`, `stage`, `owner_activity_id`, `continuation_of`, `revision_targets`, `repetition_bases`, `import_id`, `previous_import_id`, `intent_repair`, `review_cycle_id`, `grant_id`, `assessment_targets`, `observation_rule_targets`만 값 그대로 복사한다. 없는 필드는 추가하지 않는다. `reason`과 배정 캐시처럼 범위를 바꾸지 않는 나머지 필드는 복사하지 않는다. 실행기는 이 객체를 현재 요청과 정확히 대조하고 다른 계보·과거 보류·넓어진 범위·이미 실행 중인 시도를 거부한다.

수락한 결정은 과거 이력을 보존한 채 해당 보류를 해소하고 새 집계 구간을 연다. 같은 `decision_id`·보존 원문 참조·결정 내용의 재처리는 중복 적용하지 않는다. 사용자 정지·grant·입력 복원 등 다른 대기는 그대로 검사한다. AI의 기술 수리 처분은 반복 한도 보류를 해제하거나 이 사용자 결정을 대신하지 않는다.

정상 수신된 무산출 준비가 `exhaustion_empty` 문턱에 도달했고 같은 계보의 다음 요청이 아직 없으면, 계속 결정과 새 요청을 함께 만들 수 있다. 이 경우의 `allowed_action`은 `{"id":"아직 사용하지 않은 AC 식별자","role":"research_preparation","repetition_bases":{"exhaustion_empty":"현재 lineage_id"},"revision_targets":{}}` 형식이다. 같은 계보에 큐 또는 대기 요청이 이미 있으면 그 기존 요청의 범위를 승인한다. 무산출 준비 실행이 수신 실패로 끝났다면 현재 큐 또는 대기에 보존된 수리 요청의 정확한 범위를 승인한다. 이 경우 계속 결정으로 새 일반 준비 요청을 만들 수 없다. 이 결정은 사용자가 명시적으로 요청한 준비이며 자동 고갈 재생성 시각만으로 열린 준비와 구별한다.

#### 로컬·HTTP grant

```json
{
  "kind":"grant",
  "grant":{
    "kind":"local",
    "roles":["research_work","identity_review"],
    "task_ids":[],
    "reuse":"reusable",
    "expires_at":null
  }
}
```

로컬 grant의 `roles`는 지원 역할의 비어 있지 않은 목록이고, `task_ids`가 비어 있으면 그 role의 모든 과제를 대상으로 한다. `valid_from`과 `expires_at`을 지정할 수 있다. 새 grant의 만료 시각은 적용 시점보다 뒤여야 한다. `reuse`는 `once` 또는 `reusable`이다. `once` grant는 한 사례에만 권한을 준다. 로컬 grant의 한 사례는 action 하나이며, 같은 action의 재시도도 같은 사례다. HTTP grant의 한 사례는 외부 operation 하나다. 다른 사례가 그 grant를 이미 쓴 뒤에는 새 사례를 허가하지 않는다. `reusable` grant는 효력 기간과 범위 안의 모든 사례에 쓸 수 있다. `reuse`를 생략하면 `once`로 저장된다. 그러므로 여러 과제나 여러 실행에 걸쳐 쓸 권한에는 `reusable`을 명시한다.

```json
{
  "kind":"grant",
  "grant":{
    "kind":"http",
    "allowed_origins":["https://example.org"],
    "allowed_methods":["POST"],
    "allowed_path_prefixes":["/submissions/"],
    "credential_env":{"Authorization":"MATH_SUBMISSION_TOKEN"},
    "reuse":"once",
    "expires_at":"2026-12-31T00:00:00+00:00"
  }
}
```

`credential_env`는 HTTP header 이름을 환경 변수 이름에 연결한다. 비밀 값은 JSON에 넣지 않는다. grant의 origin·method·path prefix를 모두 만족해야 외부 operation을 준비할 수 있다. ID를 생략하면 실행기가 부여한다.

```json
{"kind":"revoke","grant_id":"GR-..."}
```

철회는 해당 grant를 쓰는 미종료 실행에 정지 요청을 남기고 새 queue 요청을 제거한다. 수학 판정을 직접 바꾸지는 않는다.

#### 과제 범위

아래 예시에는 미완료 과제의 현행 `revision`과 그 판본의 실제 계약 해시를 넣는다. `contract_sha256`은 과제 전체 조회 record의 해시와 구별한다. ID·판본·해시 자리를 실제 값으로 바꾼 뒤 제출한다.
```json
{"kind":"task_scope","task_id":"TK-...","revision":1,"contract_sha256":"조회한-현행-계약-해시","disposition":"revise","reason":"필수 범위를 다시 정해야 한다."}
```

`task_scope`는 미완료 과제의 현행 `revision`과 `contract_sha256`을 요구한다. `disposition`은 `revise`, `waive`, `transfer`다. `revise`는 후보 준비에 계약 개정을 요청한다. `waive`와 `transfer`는 비어 있지 않은 `obligation_ids`로 승인 대상 완료 의무를 지정하며, `transfer`에는 서로 다른 미완료 수신 과제의 `target_task_id`도 필요하다. 면제와 이전은 원 과제를 즉시 닫지 않고, 연구 계획이 승인 근거와 의무별 처분을 대조하도록 요청한다.

#### 학술 요구와 외부 거부

학술 요구 변경도 위의 `charter` 결정으로 제출한다. 현행 헌장의 다른 내용은 보존하고 `record.content.academic_requirements`를 승인된 요구 배열로 교체한다. 다음은 그 필드에 넣는 배열의 예시이며, 독립된 결정 객체가 아니다.

```json
[
  {
    "id":"paper-reproduction",
    "scope":"해설과 Lean 결과를 독립적으로 재현할 자료를 만든다.",
    "assessor":"research_plan",
    "criteria":["새 환경에서 Lean 결과를 재빌드했다.","해설의 가정과 선언 대응을 기록했다."],
    "required_inputs":[],
    "external_effects":[]
  }
]
```

각 requirement는 고유한 `id`, 비어 있지 않은 `scope`, `assessor="research_plan"`, 중복 없는 비어 있지 않은 `criteria`를 요구한다. `required_inputs`는 정확한 입력 참조 목록이다. `external_effects`의 각 항목은 고유 `id`, `scope`, 선택적 `grant_id`를 가진다. 요구 목록을 바꾼 새 헌장은 새 판본과 내용 해시를 가지며 현재 해결 근거에 결박된 새 과제를 생성한다.

```json
{"kind":"academic_rejection","actor":"외부 검토자 식별","text":"보존할 거부 원문"}
```

외부 거부는 현재 수학적 해결의 정확한 solution basis가 있을 때만 접수한다. 연구 계획이 원문을 대조하기 전에는 해소되지 않은 학술 근거이며 Lean 형식 결과를 자동 무효화하지 않는다.

### `source`

```text
source --file PATH [--name FILE_NAME]
```

로컬 파일을 읽어 접수 시점의 base64·SHA-256·바이트 수를 control 요청에 고정한다. `--name`은 디렉터리 구분자 없는 파일명이어야 한다. 적용 시 바이트 해시를 다시 검사하고 `runtime/artifacts/<bundle>/source.bin`에 보존한다. 같은 이름·같은 해시는 변경 없음이고, 같은 이름·다른 내용은 같은 source ID의 새 revision이다.

완료 과제와 source 변경의 처리는 앞의 과제 상태 절을 따른다.

### `knowledge`

`knowledge`는 다섯 operation을 지원한다. `closed`·`completed` 인스턴스에는 어느 operation도 적용하지 않고 거부된 제어로 기록한다.

#### candidate 수입

```json
{
  "operation":"import",
  "candidate":{
    "kind":"conjecture",
    "title":"후보 제목",
    "statement":"정확한 주장",
    "explanation":"가정·범위와 논증",
    "summary":"목차 요약",
    "lean_code":"",
    "declaration_names":[],
    "dependencies":[],
    "origin_refs":[],
    "source_refs":[],
    "confirmed_scope":"현재 확인 범위",
    "epistemic_status":"open",
    "selection_relevance":"다음 선택과의 관계"
  }
}
```

`kind`는 현재 종류 정의 레지스트리에 있어야 한다. `title`, `statement`, `explanation`, `summary`는 비어 있지 않아야 하고 `lean_code`가 있으면 중복 없는 `declaration_names`가 필요하고, 각 선언명은 형식 검사가 받는 선언명 문법(「연구 수행」의 선언명 절)을 따라야 한다. 문법에 맞지 않는 선언명은 가져오기 단계에서 거부된다. `dependencies`는 존재하는 다른 knowledge ID만 받는다. `id`를 제공해 기존 기록을 개정할 수 있으며 revision과 history를 보존한다. 실행기 소유 필드인 검증 status·formal 결과·review·identity assessment는 candidate가 제공할 수 없다.

`import`에 기존 ID를 넣는 방식은 완전한 후보 본문으로 그 기록을 대체할 때 사용한다. 필요한 필드를 모두 제출하며 생략한 선택 필드가 옛 값으로 유지된다고 가정하지 않는다. 기존 기록의 일부 필드만 바꾸려면 아래의 `operation="revise"`와 `changes`를 사용한다. 두 경로 모두 과거 판본을 보존하고 후보 상태로 돌아가며, Lean 원문이 있으면 형식·동일성 검토를 다시 받는다.

수학 관계를 입증하는 형식 candidate에는 선택적으로 다음 `relation_claim`을 둔다.

```json
{"kind":"formally_implies","source":"KN-...","target":"KN-...","confirmed_scope":"정확한 범위"}
```

관계 종류와 양끝은 이미 존재해야 한다. 이 claim의 제출은 관계 승인이 아니며 중앙 Lean 검사와 전체 동일성 검토 뒤 실제 관계 수입에서 다시 대조한다.

#### 종류 정의 등록

```json
{
  "operation":"register-kind",
  "definition":{
    "family":"relation",
    "token":"specializes",
    "meaning":"출발 기록이 도착 기록의 조건을 더 구체화한다.",
    "constraints":{
      "mathematical_claim":false,
      "requires_evidence":true,
      "requires_formal_results":false,
      "requires_assessments":false
    }
  }
}
```

`family`는 현재 CLI에서 `knowledge` 또는 `relation`이다. `token`은 소문자로 시작하는 영문 소문자·숫자·underscore 문자열이고 기존 token과 중복될 수 없다. 스킬에 설치된 지식·관계 종류의 token은 인스턴스를 만들 때 이미 활성으로 정의되므로 다시 등록하지 않는다. 수학 주장 종류는 `requires_formal_results`와 `requires_assessments`가 자동으로 참이 된다. 이 `knowledge` family는 현재 CLI 레지스트리의 구현 이름이며 GLOSSARY.md의 F 객체 의미를 새로 정의하지 않는다.

#### 관계 수입

```json
{
  "operation":"import-relation",
  "relation":{
    "kind":"supports",
    "source":"KN-...",
    "target":"KN-...",
    "evidence":"관계 방향과 범위의 근거",
    "evidence_refs":["SO-..."],
    "confirmed_scope":"확인 범위"
  }
}
```

양끝과 종류 정의가 존재해야 한다. 종류가 요구하면 근거가 필요하다. 수학 관계는 비어 있지 않은 `formal_result_refs`, `assessment_refs`를 요구하며, 각 형식 결과의 `relation_claim`이 종류·source·target·confirmed_scope와 정확히 같고 현재 사용할 수 있어야 한다.

#### 기존 지식 개정·무효화

```json
{"operation":"revise","id":"KN-...","changes":{"summary":"새 요약"},"reason":"개정 근거"}
```

```json
{"operation":"invalidate","id":"KN-...","reason":"사용 정지 근거"}
```

개정은 이전 revision과 검토 계보를 보존하고 candidate·새 형식 검사·새 동일성 검토로 돌린다. 무효화는 기록을 삭제하지 않고 현재 사용을 정지하며 실제 의존을 다음 연구 계획에 알린다.

### `trust`

`trust`의 연산은 `register`, `transition`, `invalidate` 셋이다.

`register`에는 `toolchain`(판본 식별), `allowed_axioms`, `toolchain_record`(툴체인 기록 파일의 절대 경로와 기록 ID), `binding`(결박할 기준 항목의 번호, 지문 다이제스트, 내용 해시 다이제스트, 대표 검사 요약 해시)이 필요하다. `setup_lean.py --verify-only --trust-file <새 경로>`나 설치의 `--trust-file`이 기록의 현재 기준으로 이 요청을 만든다. 완전한 요청 형식과 각 값의 출처는 [초기화 운전](초기화-운전.md)의 5절에 있다. 수신기는 요청 구조를 검사한 뒤 기록 파일을 읽어 ID·판본 식별·결박 다이제스트가 요청과 같은지, 현재 기준의 대표 검사가 성공했고 불일치 점검이 없는지 확인하고 비활성 후보를 보존한다. 설치 파일은 읽지 않는다. 사전 빌드 캐시를 허용하며 클린 빌드는 요구하지 않는다. 대표 검사의 통과는 명시한 예제에 상대적이며 전체 라이브러리 재검증을 뜻하지 않는다. 현재 판본 식별과 지문의 대조는 전환 뒤 활성화 기계 작업이 수행한다. 등록 성공이나 준비 표지 하나로 환경을 활성화하지 않는다.

```json
{"operation":"transition","env_id":"TE-실제-등록-ID"}
```

등록 응답 뒤 `query --kind trust-environment`로 대상 ID와 내용을 확인한다. `transition`은 그 환경을 대상으로 전환 기록을 만들고, 현재 형식 결과를 가진 K마다 `trust_check` 기계 요청을 만든다. 재검사할 K가 없으면 곧바로 `trust_activate`를 만들고, 있으면 재검사가 모두 끝난 뒤 `trust_activate`가 이어진다. `run`이 이를 처리하며, 현재 형식 결과의 재검사와 필요한 의미 대조가 끝나기 전에는 새 환경을 활성으로 사용하지 않는다. 형식 재검사 성공만으로 이전 동일성 결론을 새 의미에 승계하지 않는다. 상태는 전환 기록과 `active_trust_environment`에서 확인한다.

```json
{"operation":"invalidate","env_id":"TE-실제-등록-ID","reason":"실제로 확인한 무효화 근거"}
```

무효화는 해당 환경에 의존하는 현재 사용을 정지한다. 원 형식 결과와 판정 이력은 보존하며 실제 영향 범위의 후속 판단을 연다.

지문 불일치로 멈춘 형식 검사를 다시 진행시키는 `trust` 연산은 없다. 판본이 같고 메타데이터만 바뀌었으면 사용자나 운전자가 `setup_lean.py --rerecord`로 기준을 덧붙이고, 판본이 바뀌었으면 새 기록을 `register`·`transition`한다. 실행기는 툴체인 기록 파일의 크기나 수정 시각이 바뀌었거나 활성 환경이 바뀐 것을 보고 멈춘 작업을 다시 배정한다. 재기록, 재결박, 선택적 전수 점검(`--check-contents`)과 종료 코드는 [초기화 효율과 정비](초기화-효율과-정비.md)를 따른다.

### `external`

```json
{
  "operation":"prepare",
  "grant_id":"GR-...",
  "id":"optional-stable-operation-id",
  "request":{"method":"POST","url":"https://example.org/submissions/1","body":"UTF-8 text"}
}
```

현재 HTTP method는 `GET`, `POST`, `PUT`, `DELETE`다. URL은 http/https, host와 안전한 path를 가져야 하고 userinfo·fragment·`.`·`..` path segment를 허용하지 않는다. redirect는 거부한다. body는 문자열이어야 하며 `GET`·`DELETE`에서는 생략하거나 빈 문자열만 허용한다. `POST`·`PUT`의 비어 있지 않은 body는 UTF-8로 전송한다. 이 형식은 요청 해시를 만들기 전과 전송 전에 검사한다. request를 정규화해 hash와 idempotency key를 만들고 active HTTP grant의 origin·method·path·기간을 검사한다.

실행기는 `prepared`·`running` 상태를 기록하고, 전송 직전에 불리언 `transmitted=true`를 저장한 뒤 전송한다. transport 결과를 확정할 수 없으면 `unknown`이다. HTTP 응답을 받으면 `confirmed`, `http_status`, body hash를 기록하고 `succeeded`는 실행 기록에서 2xx 여부로 별도 계산한다.

```json
{"operation":"reconcile","id":"EO-...","result":"confirmed","evidence":{"operation_id":"EO-...","request_sha256":"<operation의 request_sha256>","idempotency_key":"<operation의 idempotency_key>","fact":"succeeded","evidence_ref":"외부 영수증 좌표","observed_at":"2026-09-20T00:00:00+00:00"}}
```

reconcile은 현재 `unknown` operation에만 적용하고 result는 `confirmed`, `failed`, `cancelled`다. `evidence`는 객체다. `operation_id`·`request_sha256`·`idempotency_key`에는 대조할 operation의 `id`·`request_sha256`·`idempotency_key`를 그대로 넣고, 외부에서 확인한 좌표 `evidence_ref`, 시간대가 있는 관측 시각 `observed_at`, 확인한 사실 `fact`를 함께 넣는다. `fact`는 result가 `confirmed`이면 `succeeded`, `failed`이면 `effect_absent`, `cancelled`이면 `not_transmitted`여야 한다. 실행기는 `succeeded`와 `effect_absent`를 이 `fact`에서 기록하므로 요청에 따로 적지 않는다. 선택 필드 `external_id`와 `idempotency_evidence`는 대조 기록에 함께 보존된다.

```json
{"operation":"retry","id":"EO-...","grant_id":"GR-..."}
```

retry는 사용자 제어로 `unknown`, `failed`, 전송 전 `cancelled` operation에 요청한다. 원 operation의 현재 유효한 HTTP grant를 명시하고 요청 범위·권한·학술 전제를 다시 검사한다. `unknown`은 요청 해시와 idempotency key에 결박된 만료 전 `verified_idempotency` 증거가 필요하다. `failed`는 효과 부재가 확인된 `effect_absent` 증거 또는 같은 멱등성 증거를 사용한다. 전송·시도 이력이 없는 `cancelled`는 전송 전 요청을 다시 준비할 수 있다. 같은 operation ID·request hash·idempotency identity를 유지하며, 새 execution과 이전 결과·시도 이력을 보존한다.

### `conversation`

```json
{"operation":"attach","id":"conversation-1","generation":1,"disconnect_policy":"pause","lease_seconds":60}
```

`generation`은 양의 정수이고, 재연결은 이전보다 큰 generation을 사용한다. `disconnect_policy`는 `pause` 또는 `continue_authorized`다. attach에서 이 값을 지정하면 연결 기록과 인스턴스의 `conversation_loss_policy`를 함께 갱신한다. 생략하면 인스턴스의 현행 값을 사용한다. 초기화 때 continue_authorized를 채택했어도 이후 attach가 pause를 지정하면 그 현행 정책으로 대화 소실을 처리한다. lease는 유한한 양수 초다.

```json
{"operation":"heartbeat","id":"conversation-1","generation":1}
```

```json
{"operation":"detach","id":"conversation-1","generation":1}
```

heartbeat와 detach는 현재 connected generation에만 적용한다. lease가 만료된 generation은 heartbeat로 되살리지 않고 새 generation으로 attach한다. `pause` 정책의 연결 소실은 CLI를 paused로 만들고 미종료 실행에 정지를 요청한다. `continue_authorized`는 기존 grant 범위만 유지한다.

## 조회 명령

### record `query`

```text
query [--snapshot OID] [--kind KIND] [--text TEXT] [--limit 1..1000]
      [--cursor CURSOR] [--related-to ID]
      [--direction incoming|outgoing|both]
```

구조화 record를 ID 순서로 조회한다. `kind`는 record family 또는 구체 kind와 일치한다. `--kind`와 결과 `record.family`의 가족 이름은 조건 문법의 기록 가족 이름(`planning.RECORD_FAMILIES`, [과제 착수 조건](과제-착수조건.md)의 가족 목록)이다. 그 목록에 없는 저장 가족은 저장 이름을 그대로 쓰고, 질문 행은 `question`이다. text는 정규 JSON 전체를 대소문자 구분 없이 찾는다. 관계 이웃 조회는 relation record와 반대편 endpoint를 함께 반환한다. `--direction`은 `--related-to`와 함께 사용하며 생략하면 `both`다. `--prefix`는 파일 조회 전용이므로 이 모드에서 지정하면 입력 오류다.

응답은 `snapshot`, 전체 `total`, 이번 `loaded`, `truncated`, `items`, `next_cursor`다. 각 item의 `record`는 조회용 표현이다. `sha256`과 `bytes`는 `path`가 가리키는 저장 파일의 원 바이트를 식별하며 `byte_scope`는 `persisted_file`이다. `logical_sha256`은 외부 payload를 복원한 저장 레코드의 정규 해시다. 조회용 family 표기가 붙은 `record`를 재직렬화한 해시와 구별한다. 외부 payload가 있으면 `payload_refs`와 `json_pointer_scope=decoded_record`도 제공한다. cursor는 query 인자와 snapshot에 결박되며 조건을 바꾸어 재사용할 수 없다.

### raw file `query --files`

```text
query --files [--snapshot OID] [--prefix research/|runtime/.../] [--text TEXT]
              [--limit N] [--cursor CURSOR]
```

경로와 UTF-8 query byte가 일치하는 snapshot 파일을 POSIX 경로 순으로 반환한다. 각 항목은 path·size·SHA-256을 가진다. prefix는 `research/` 또는 `runtime/` 아래에서 `/`로 끝나야 하며 생략하면 `research/`다. 파일 조회에서 `--kind`, `--related-to`, `--direction`을 지정하면 입력 오류다. 같은 조합 검사를 JSON 명령 요청에도 적용한다.

### `read`

```text
read [--snapshot OID] --id RECORD_ID
read [--snapshot OID] --path POSIX_PATH [--output PATH]
```

`--id`는 구조화 `record`와 record query의 동일한 파일·논리 해시 및 출처 필드를 반환한다. `sha256`은 저장 파일의 원 바이트 해시이고 `logical_sha256`은 복원한 저장 레코드의 정규 해시다. `--path`는 exact snapshot의 파일을 읽어 UTF-8이면 `text`, 아니면 `base64`로 반환한다. `--output`은 `--path`와 함께 사용할 때 바이트를 로컬 파일로 쓰고 path·snapshot·size를 반환한다. `--id`와 `--output`을 함께 쓰면 입력 오류다.

### `export`

```text
export --destination PATH [--snapshot OID] [--all]
```

기본은 `research/`만, `--all`은 `research/`와 `runtime/`을 새 경로나 빈 디렉터리에 복사한다. reparse point를 지나는 목적지와 비어 있지 않은 디렉터리는 거부한다. export 결과는 snapshot 사본이며 새 정본이나 쓰기 작업 공간이 아니다.

## AI 실행 입력

각 AI 실행은 배정된 provider의 새 CLI session과 `<workspace>/runs/<execution_id>/workspace`를 받는다. 자동 제공 문서와 순서의 정본은 `SKILL.md`의 역할 읽기 대응표다. 기계 실행기는 그 표의 공통 문서와 해당 역할 문서 전건을 선언된 순서로 프롬프트에 넣고, 같은 바이트를 `input/implementation/`과 input artifact에 보존한다. 이 문서에 별도 입력 목록을 유지하지 않는다.

`references/CLI-실행-계약.md`는 CLI를 운전하거나 구현을 고치는 독자를 위한 참조이며 모든 AI 역할에 자동 주입되지 않는다. 역할이 판단할 현행 필드와 단계는 자기 계약, canonical input context와 실행별 출력 schema가 소유한다.

입력 context의 구성요소는 싣기·지도·차단 세 분류 가운데 하나다. 모든 역할에 싣는 필드는 현재 snapshot과 workspace, 통치 기록 `governance`, action, 대상 task, knowledge catalog, sources, grant 요지, kind definitions, 학술자료 도구 안내, 시간 한도, 제출 계약과 참조 목록, 기록 지도 요약 `record_map`이다. 과제 목록은 과제를 비교·선택하거나 집계하는 의도 해석·후보 준비·연구 계획·운영 점검·목표 감사·유지보수에 싣고, 과제 하나를 배정받은 연구 수행·보충 조사·작업 계약 검토에는 지도로 준다. goal·policies와 그 판본, relations, 사용자 입력, 열린 질문, 최근 이력, 자원 표와 모델 정책, 중앙 형식 검사 설명(`formal_verifier`), 학술 요구·상태, 외부 operation과 거부, 반복 보류는 역할 계약이나 제출 검사가 그 필드를 읽는 역할과 단계에 싣고, 다른 역할과 단계에는 `input/catalog/<key>.json`의 원문 참조 `{source_ref, total}`(지도)로만 준다. 실행 프로필 전체 목록과 역할별 프로필 선택(`execution_profiles`, `role_profile_refs`)은 모든 역할에 지도로 준다. 독립 판단(동일성 검토, 검토 자리의 고정 질문 조사, 검토 자리 실행의 운영 점검, 목표 감사, 의도 해석의 검사·위임, 작업 계약 검토)은 계약이 막은 비공개 필드와 기록 가족을 받지 않고(차단, 예: 목표 감사는 감사 자리마다 봉인되는 `research/goal_judgments`를 읽거나 인용하지 않는다), 실행 원장 기록은 입력이 지급한 것만 읽고 인용한다. 세 분류의 정본은 `scripts/do_math/context_store.py`의 `INLINE_SCOPES`, `BLOCKED_KEYS`와 `input_class`다. 모든 역할은 읽고 인용할 수 있는 입력 스냅숏 기록의 ID를 `root/family`별로 담은 `record_index`(지도)를 받는다. 제출 검사는 입력이 보여 준 참조와 이 ID를 인용 모집단으로 쓰고, 필드별 규칙을 따로 적용한다. 읽기 도구 `input/tools/read_input.py`는 입력 스냅숏 커밋만 읽고 요청마다 `checks/reads.jsonl`에 기록하며, 중앙 봉인은 그 기록을 제출 산출물 `reads.jsonl`로 보존한다. 역할용 설명은 「공통 실행」의 「기록 지도와 읽기 도구」에 있다. 후보 준비·연구 계획과 위임 판단이 아닌 의도 해석은 활성 설정 전문도 `configuration_source`의 원문 참조로 받는다. `available_input_refs`는 저장 상태의 필드가 아니라 역할 입력을 만들 때 계산해 넣는 목록이다. `task_readiness`는 연구 계획·후보 준비의 입력에 전 과제의 착수 판정으로, 연구 수행의 입력에 자기 과제의 착수 판정으로만 들어간다. `supplied_record_ids`는 후보 준비·연구 계획·운영 점검의 입력에만 들어가며, 입력이 보여 주거나 `record_index`에 있는 기록 색인(`planning.record_index`)의 ID다. 제어 통로 결박 `control_binding`과 읽기 도구의 저장소 결박 `record_store`는 도구가 읽는 `input/submission/context.json`에만 두고 프롬프트에는 넣지 않는다. 역할과 action에 따라 proposal, review context, eligible knowledge, operational observation, intent interpretation 입력, 이전 output 파일과 checkpoint가 추가되거나 비공개 자료가 제거된다.

모든 knowledge와 source 원문은 `input/knowledge/`, `input/sources/`, `input/task-results/` 아래의 실행별 사본으로 물질화한다. 완료된 동일성 검토의 기록은 그것을 읽는 목표 감사의 입력에만 `input/review-cycles/` 아래에 물질화한다. 독립 판단이 아닌 역할은 `runtime/review_cycles`를 읽기 도구로 읽는다. catalog의 `path`나 `local_path`는 이 workspace 안의 파일을 가리킨다. 해시와 목록이 있다는 사실은 모델이 원문을 읽었다는 뜻이 아니다.

### 입력 크기 조정

기계 실행기는 최종 prompt의 UTF-8 바이트를 `max_input_bytes` 안에 맞춘다. goal, policies와 action별 필수 판단 정보를 보존한다. 현재 작업 계약과 검토 제안의 전문은 필요한 역할에 제공하고, 누적 이력 때문에 같은 전문을 여러 곳에 중복하지 않는다. 검토 계보의 제안은 `role_review.proposal`에 한 번 제공한다. 판단 역할이 받는 형식 결과는 동일성 검토의 제안, 목표 감사의 `eligible_knowledge`, 지식 사본이 모두 같은 판단용 투영(`knowledge_records.judged_verification`: 선언·타입·서명, 공리와 신뢰 환경의 허용 공리, 검사한 원문 해시, 검사 결과 원문 참조)이다. 검사 원출력과 커널 의존 증거는 이 투영에 넣지 않고, 그것을 쓰는 기계 검사가 저장 기록에서 읽는다. 판정 전제는 형식 결과의 `verification` 전체를 해시하므로 투영 밖 필드가 바뀌어도 편입 관문이 거부한다.

크기가 넘으면 필수 직접 입력이 아닌 항목을 큰 것부터 통째로 `{source_ref, total}`로 바꾼다. `source_ref`는 `input/catalog/<key>.json`의 exact source reference이고 `total`은 원래 항목 수다. action, 역할별 대상 task·검토 자리·운영 대상, 재개·진단 자료 같은 필수 직접 입력은 줄이지 않는다. 지도 필드는 크기와 관계없이 항상 참조로 준다. 모든 역할의 `execution_profiles`·`role_profile_refs`와 연구 수행·보충 조사·작업 계약 검토의 `tasks`도 지도 필드다. tasks 목록의 표현을 바꿔도 계획이 대조할 고정 모집단 `ready_task_ids`를 보존한다. 역할은 필요한 원문을 그 경로에서 읽어야 한다.

필수 판단 정보와 ready 모집단을 보존하고도 입력을 맞출 수 없으면 AI 실행을 시작하지 않는다. 동일성 검토 자리는 복원한 대화를 빼고도 제안과 필수 원자료만으로 한도를 넘는 경우에만 제안 자체의 입력 초과로 보고, 아래 「형식 검사, 동일성 검토와 목표」 절의 자원 처분으로 그 검토를 정산해 연구 계획의 `review_followups`에 넘긴다. 자기 검토 이력이나 다른 입력의 증가로 넘은 경우에는 수학 제안의 결함으로 바꾸지 않고 `input_overflow`로 보류한다. 다른 역할도 해당 요청과 오류를 보류한다. 같은 근거의 보류된 작업 계약 검토와 검토 자리를 새 ID로 자동 재생성하지 않는다.

`input_overflow`는 원 action, owner activity, 취소된 입력 준비 실행, 입력 크기·원인·현재 한도, 공개 질문과 그 source artifact를 보존한다. 문맥은 한도 전체가 아니라 한도에서 지급 문서·출력 스키마·틀의 고정 부분을 뺀 문맥 예산과 비교되므로, 기록은 한도(`limit_bytes`)와 함께 그 예산(`context_budget_bytes`)을 남긴다. `status --json`의 `question_links`는 이 artifact의 `resolution_question/question`을 원문으로 읽는다. 설치·필수 입력·승인 설정이 실제로 달라진 뒤 `request --retry-action AC-ID`로 같은 action을 다시 포장할 수 있다. 일반 `resume`은 이 대기를 해제하지 않는다.

재시도 요청을 적용하면 상태는 “재시도 중”이며 요청 자체로 질문을 해소하지 않는다. 현재 포장이 한도 안에 들어온 사실을 확인하면 아직 열린 질문을 해소하고 `input_overflow_retry_resolved`를 기록한다. 다른 적법한 결정이 이미 질문을 해소했다면 그 근거와 이력을 보존한다. 다시 넘치면 아직 열린 이전 질문을 새 실패 질문으로 대체했다는 해소 이력과 `input_overflow_retry_failed`를 기록하고, 새 질문과 같은 action을 다시 보류한다. 과거 overflow detail·source manifest·질문 원문은 삭제하거나 현재 성공으로 덮지 않는다. 원문이나 필수 직접 입력을 몰래 줄이지 않으며, 승인되지 않은 프로필·범위·자원·권한 변경을 재시도 명령으로 대신하지 않는다.

### 입력 고정과 현재성

실행 기록은 input snapshot, 입력 manifest와 그 prompt 해시(`input_manifest.prompt.sha256`), input bundle, 모델·effort, goal·policy revision, 작업 계약 hash, 실제 지식·과제·source basis와 grant를 고정한다. 착수 전 명시된 의존에 더해, 응답의 `used_sources`, 새 지식의 dependencies와 지원되는 확장 참조에서 드러난 실제 의존도 원 입력 snapshot의 판본에 결박한다. 수신 시점의 새 판본을 대신 기록하지 않는다. 제공된 지식 파일 경로와 source ID·이름·`source:이름`·제공 경로는 원 입력의 대응표로 해석한다. 입력에 제공됐다는 이유만으로 모든 source를 사용 의존으로 잡지 않으며, 과거 산출의 고정 artifact 참조를 최신 지식 의존으로 바꾸지 않는다. 결과 적용 직전에 다음을 다시 검사한다.

- goal·policy와 학술 요구 판본
- 대상 작업 계약 hash와 closed 여부
- 실제 사용 지식·과제·source basis
- 현재 grant와 역할 권한
- 실행 중 설치 코드·역할 문서의 변경

전제가 바뀌면 결과를 정본에 적용하지 않고 원 출력과 부분 파일을 보존한다. 무관한 snapshot 전진만으로 모든 결과를 버리지는 않는다.

## 역할별 주 JSON

모든 AI 응답은 실행별 `schema.json`을 만족하는 JSON 객체 하나여야 한다. 이 실행별 schema와 수신 검사 코드가 필드·자료형·필수 여부·닫힌 값의 기계 정본이다. 아래 설명은 소비자가 각 역할 필드를 어떻게 해석하는지 밝히며 완전한 필드 목록을 별도 정본으로 만들지 않는다. Markdown fence나 JSON 밖의 설명은 허용하지 않는다.

모든 역할은 이번 판단·결과를 설명하는 `summary`, 실제 사용한 제공 ID·reference·workspace 좌표의 `used_sources`, 결과를 바꿀 미해결 질문의 `questions`와 선택적 `repair_responses`를 가진다. `integration_bundles`를 선언해야 하는 경우와 생략했을 때의 묶음 구성은 아래 「제출, 보존과 편입」 절을 따른다. 빈 배열과 필드 부재는 다르며, 실행별 schema가 요구한 필드는 생략하지 않는다.

### 후보 준비 `research_preparation`

주 산출 `candidates`는 새 과제와 기존 미완료 과제의 개정을 구별한다. 새 과제는 `revises_task_id=null`, 개정은 정확한 task ID를 쓴다. 각 후보는 질문, `scope.included`·`scope.excluded`, `expected.outputs`·`expected.research_change`, ID와 필요 증거를 가진 진전 기준, ID·판정자·필요 증거를 가진 완료 의무, 정확한 입력·재사용·의존·프로필·권한·생성 근거와 formal/nonformal 작업 구별을 제공한다. 개정의 완료 의무는 전체 현행 목록으로 교체하며 이전 계약은 개정 이력에 보존한다.

후보의 `profile_refs`는 허용할 각 프로필의 정확한 `{id, revision, sha256}` 배열이다. 문자열 ID나 `{id, version}`을 대신 쓰지 않는다. 실행기는 선택 시 이 참조가 현행 불변 프로필과 일치하는지, 해당 역할·입력 한도·도구·중단 표면에 필요한 능력 증거가 현재인지 다시 검사한다.

### 작업 계약 검토 `task_contract_review`

`item_reviews`는 `question_scope`, `inputs_reuse`, `outputs_obligations_judges`, `stage_boundaries`, `tools_authority_profiles`를 정확히 한 번씩 검토한다. 각 항목은 `approved`, `revision_required`, `unresolved`와 근거 참조·발견·누락 입력·다음 소유자를 가진다. 승인에는 근거가 필요하고 누락 입력이 없어야 하며, 미해결에는 누락 입력이 필요하다. 실행기는 수정 필요를 우선하고 그다음 미해결을 반영해 전체 판정을 집계한다. 승인은 정확한 task revision, contract hash와 goal·policy revision에 결박되며 과제를 곧바로 실행하지 않는다.

### 연구 계획 `research_plan`

계약의 `evidence_requirements`는 선택적인 증거 설명 목록이고 `evidence_required`는 반드시 인용할 기존 참조 목록이다. 의무별 `item_dispositions[].evidence_refs`는 실제 근거를 가리킨다. 필수 자료를 읽고 미이행을 확인했으면 `open`, 읽기 실패를 현재 권한·환경에서 해결할 수 없어 판정하지 못하면 `unresolved`에만 기록한다. `item_dispositions`와 `unresolved`에 같은 의무를 중복하지 않는다. 완료 집계자는 이 과제의 결과에 대한 현재 유효한 FR·IA·목표 감사 기록을 인용해 지정 전문 판정을 소비할 수 있다. 대상·값·현재성이 맞지 않는 판정은 완료를 만들지 않는다.

`dispositions`는 현재 ready 과제 전건을 정확히 한 번씩 `selected`, `not_selected`, `not_assessable`로 처분한다. 각 항목은 이유·불확실성, 병행 과제 ID, 기대 연구 변화, 사건·시각 재검토 조건, 누락 입력과 다음 소유자를 가진다. `preparation_requests`는 후보 준비가 처리할 정련·탐색을, `goal_audit`는 현재 근거로 목표 감사를 열지를 표현한다.

`task_assessments`는 실제 결과를 반환한 과제만 대상으로 한다. 계약의 안정된 완료 의무 ID마다 `fulfilled`, `open`, 권위 참조가 있는 `waived`, 또는 권위와 대상 과제·의무가 있는 `transferred`를 기록하고 실제 `evidence_refs`를 결박한다. `completed`에는 의무 전건의 이행 또는 적격 면제가 필요하다. `transferred`는 원 과제의 완료 근거가 아니며, 권위 있는 `closed`와 수신 과제의 의무 보존으로 연결한다. 판정하지 못한 의무는 unresolved에만 의무 ID, 누락 입력과 다음 소유자를 남기며 item_dispositions에 중복하지 않는다. 수행 전 과제를 판정하거나 ready 과제를 assessment에 넣지 않는다.

수신자는 ready 모집단의 모든 ID가 `dispositions`에 정확히 한 번 있는지, 선택 집합과 모델 평가가 일치하는지 검사한다. `not_assessable`은 전략적 미선택이 아니므로 누락 입력과 다음 소유자를 요구한다.

입력의 `ready_task_ids`와 수신 검사는 계획 입력 스냅샷의 같은 모집단을 사용한다. 입력 이후 새로 준비된 과제는 후속 계획에서 판단하고, 선택한 과제가 착수할 수 있는지는 적용 직전에 다시 확인한다. 오류는 현재 ID 목록과 `missing`, `unexpected`, `duplicate`를 구분해 반환한다. 완료 과제의 과거 준비 표시나 이전 실패 출력으로 이 모집단을 바꾸지 않는다.

### 연구 수행 `research_work`와 과제 기반 `supplemental_research`

두 역할의 기본 주 schema는 같다. `outcome`은 `submitted`, `partial`, `waiting`, `no_result`를 구별하고, `report`는 실제 수행 범위·근거·결과·한계를 설명한다. 새 knowledge와 relations, remaining_work의 남은 의무와 문자열 checkpoint의 최종 인계 요지도 함께 반환한다.

knowledge 항목은 주장·해설·목차 요지와 형식 원문·선언·의존을 함께 표현한다. kind enum은 실행 시점의 active knowledge 종류 정의에서 동적으로 만든다. Lean 원문이 있으면 정확한 declaration names가 필요하다. dependencies는 기존 knowledge ID 또는 같은 응답의 유일한 title을 사용한다.

relation 항목은 `kind`, `source`, `target`, `evidence`를 가진다. source와 target은 기존 ID 또는 같은 응답의 유일한 title이다. 종류·근거·수학 판정의 추가 제약은 적용 시 kind definitions와 `activity-extensions.json`의 metadata를 함께 검사한다.

### 기본 동일성 검토 `identity_review`

`action.stage=scope`에서는 독립 `scope_assessment`를 반환한다. 평가 ID, 정책 ID, 필수 관점, 관점·필수 원자료 참조를 가진 초기 자리, 선택한 불변 프로필의 정확한 `{id, revision, sha256}`, 활동 실행 상한과 초과 처분(`unresolved` 또는 `defer`)을 구조화한다. 필수 관점은 적어도 한 초기 자리에 배정하고 자리 ID는 scope·organize·judge 자리와 겹치지 않는다. 범위 계획 자체는 동일성 판정이 아니다.

일반 수학 제안의 동일성 검토는 아래 검토 계보의 단계별 동적 schema를 사용한다. 계보가 없는 요청은 실행기가 먼저 독립 범위 계획과 검토 계보를 만든 뒤 처리한다. 생산자는 배정된 `action.stage`의 실행별 schema에 맞춰 응답한다.

### 목표 감사 `goal_audit`

`decision`은 `satisfied`, `not_satisfied`, `unresolved`이고 `reason`과 `scope_complete`를 요구한다. 같은 basis의 독립 감사 전건이 완료돼야 집계한다. 수학 목표는 현재 사용할 수 있는 K 없이 해결 상태가 될 수 없다.

### 운영 점검 `operational_review`

주 응답은 `decision`이 아니라 `disposition` 객체를 가진다. 종류는 `continue`, `repair`, `resume`, `retry`, `task_disposition`, `user_decision`이며 모두 근거 참조·다음 소유자·이유를 요구한다. 각 종류는 다음 점검, 의미 보존 수리와 검증, 체크포인트와 재개 범위, 재시도 범위와 재생 안전성, 권위 있는 과제 상태 처분, 사용자 질문과 효과 중 자기 필드를 추가로 요구한다.

### 의도 해석 `intent_interpretation`

`action.stage=interpret`에서는 `summary`, `used_sources`, `import_units`, `questions`, `question_details`와 재작업 때의 선택적 `repair`를 사용한다. 각 `import_unit`은 고유 ID, 원문의 반열림 `source_range`, 해석, 등록된 `owner_kind`·`owner_ref`, 그 소비자의 `payload`, 결정·질문 참조를 가진다. 단위 구간은 보존 원문 전체를 빈틈·겹침 없이 순서대로 정확히 한 번 덮는다. 소유 종류는 닫힌 goal·policy 열거가 아니며, 현재 등록된 거버넌스·설정·지식 소비자를 실제 payload와 정확히 연결한다.

`action.stage=check`에서는 `decision=approved|revision_required|unresolved`, `findings`, `scope_complete`, 검사 대상의 정확한 `bundle_sha256`, `unit_ids`, `question_ids`로 독립 대조한다. 승인은 적용이 아니다. 적용은 승인된 정확한 단위와 사용자 승인, 각 소유자의 현재 스키마·권한 검사를 별도로 통과해야 한다. 사례 위임 범위 판단은 일반 가져오기 단위 대신 동적 `delegation_judgment`를 사용하며, 같은 봉인 입력을 받은 두 독립 실행이 `within_scope`, `outside_scope`, `unresolved` 중 하나를 낸다.

### 유지보수 `maintenance`

기본 응답은 `report`와 `remaining_work`를 요구한다. 구체 대상·권한·성공 조건은 maintenance를 연 action과 호출 절차가 제공한다. 이 역할 이름만으로 임의 기계 작업이나 수학 판단 권한이 생기지 않는다.

종류 정의의 독립 의미 검사에는 동적 `kind_definition_check`가 추가된다. `definition_id`·`definition_sha256`은 입력 후보와 정확히 같아야 하고, `decision`은 `approved`, `revision_required`, `unresolved`, `findings`는 의미·제약·권한 경계의 근거다. 승인된 `{family, token, meaning, constraints}`만 활성화되어 이후 종류 catalog에 들어간다.

배정된 동적 단계가 `impact_review`이면 정확한 원 묶음과 변경별 영향 계획을 읽고 제공된 `impact_review` 스키마로 판단한다. 일반 유지보수 보고만으로 수리 효과나 편입 승인을 만들지 않는다. 운영의 입력 손상은 아래 제출·편입 절의 `retry` 계약을 따른다.

## 동일성 검토 계보의 동적 JSON

검토 계보 action은 `proposal_digest`, `summary`, `used_sources`, `questions`를 모든 단계에서 요구한다. action이 고정한 stage·slot·round와 다른 출력을 받지 않는다.

### `initial`

`decision=match|mismatch|unresolved`, `scope_complete`, `findings`를 추가한다. 각 finding은 비어 있지 않은 `id`, `statement`, `evidence[]`를 가진다. mismatch에는 정확한 좌표와 논증의 근거가 있어야 하고, 범위를 마치지 못했으면 unresolved다.

### `organize`

`issues`를 추가하며 승인 decision을 내지 않는다. 각 issue는 `id`, `finding_refs`, `answer_role_slot_id`를 가진다. finding ref는 원 `stage=initial|judge|answer`, 양의 `round`, `slot`, finding `id`를 정확히 복사한다.

### `answer`

`answers`와 `new_findings`를 추가한다. answer는 `issue_id`, `disposition=maintain|revise|split|withdraw`, `statement`, `evidence[]`를 가진다. new finding은 `id`, `statement`, `evidence[]`, `parent_issue_ids[]`를 가진다. 이 단계는 제안 전체의 최종 decision을 만들지 않는다.

### `judge`

제안 전체의 `decision=match|mismatch|unresolved`, `scope_complete`, `issue_verdicts`, `new_findings`를 추가한다. issue verdict는 `issue_id`, `decision=approved|rejected|unresolved`, `reason`, `evidence[]`를 가진다. 이의 성립 여부와 제안 전체 동일성은 별도 필드다.

### 검토 자리의 고정 질문 보충 조사

동일성 검토가 `activity-extensions.json`으로 고정 질문을 요청하면 별도 `supplemental_research` 실행은 일반 과제 schema 대신 조사 전용 schema를 받는다. 입력의 research request ID와 digest를 정확히 복사하고, `answered` 또는 `unresolved` 결과와 실제 answer·scope completeness·evidence references를 돌려준다. `answered`는 범위가 완결되고 정확한 evidence가 있으며 남은 질문이 없을 때만 허용한다. 실행 미완료는 answered가 될 수 없다. 결과는 요청한 검토 자리의 transcript와 근거 사슬로 돌아가며 다른 자리의 이번 판정에는 미리 공개되지 않는다.

## 작업 공간의 보조 파일

### `checkpoint.json`

실행 중 관찰·복구용 checkpoint는 작업 공간 루트의 `checkpoint.json`이다. 연구 수행 주 JSON의 문자열 `checkpoint`와 다른 자료다. 파일은 다음 필드를 요구한다.

```json
{
  "current_claim":"현재 주장과 판단",
  "evidence_paths":["relative/evidence.json"],
  "attempts":["실제로 시도한 방법"],
  "remaining_work":["남은 의무"],
  "next_step":"다음 재개 행동",
  "progress_state":"working",
  "iteration":0,
  "counters":{}
}
```

`progress_state`는 `working`, `blocked`, `no_progress`, `ready_to_submit`이다. 선택 필드 `iteration`은 음수가 아닌 정수다. 선택 필드 `counters`는 이름별 관찰값을 담은 객체이며 각 값이 음수가 아닌 정수다. 파일은 workspace 안의 일반 파일이어야 하고 4 MiB 이하이며 완전한 JSON Schema를 만족해야 한다. `evidence_paths`에는 실제 존재하는 파일의 상대 POSIX 경로를 쓴다. `.scratch/`와 그 아래 `.scratch/.execution-temp/`처럼 산출에서 제외되는 임시 파일을 근거로 삼지 않는다. 쓰는 중인 파일과 invalid 파일은 이전에 관찰한 유효 checkpoint를 대체하지 않는다.

### 자기 점검 규칙의 실행 중 교체

실행 중 자기 점검 규칙은 유효한 자기 점검 응답의 `rule_proposal`로만 교체한다. 제안은 `{current_revision, reason, rules}` 객체이며, 실행기가 현재 revision과 선택 프로필의 `observation.rule_bindings`에 대조한 수신 결과를 응답의 수신 기록에서 확인한다. 교체가 반려되면 이전 유효 규칙을 유지한다. 작업 공간에 규칙 파일을 두어 교체하는 경로는 없다. 문법 검사는 `validate_rules`, 실행에서 허용되는 증거·대상 검사는 `validate_execution_rules`가 맡는다.

작업자의 규칙이나 최대 자기 점검 간격이 도래하면 자기 점검 의무를 만든다. 응답은 의무·실행·규칙 판본과 도래한 규칙 전건, 실제 증거, 진전과 다음 방법을 연결한다. 첫 tick에서 카운터 이름이 아직 없다는 사실만으로 운영 AI를 부르거나 값을 0으로 만들지 않는다. 선택 프로필의 첫 관찰 구간이 끝날 때도 필요한 신호가 측정되지 않았으면 `observation_unavailable` 진단과 그 후속을 기록한다. 정상 자기 점검 응답 자체는 운영 AI를 새로 부르는 이유가 아니다. 결함·판단 불가·계약 부적합·계약 한도에 도달한 반복 무진전 또는 응답 기한 소진은 그 근거에 맞는 후속 점검으로 연결된다.

호출별 도구 무응답, 별도의 주기 점검과 명시적 재점검은 직접 운영 점검을 여는 다른 발동 근거다. 모든 운영 점검을 자기 점검 뒤로 미루지 않는다. 승인된 프로필의 고정 window와 실제 호출 ID를 사용하며 작업자가 선언한 timeout을 그 window 대신 쓰지 않는다. 규칙 형식과 예시는 [공통 실행](공통-실행.md)의 「관찰 규칙의 형식」 절을, 작업자의 자기 점검 응답 절차는 [자기 점검](자기-점검.md)을 따른다.

### `activity-extensions.json`

주 JSON 밖의 선택적 요청·메타데이터를 담는 객체다. `submission.py`가 역할별 확장 스키마와 공통 parser를 제공하며, 실행기는 도메인별 적용 함수에서 권한·의미·현재성을 다시 검사한다. 작업자에게도 같은 판본의 스키마와 검사 코드를 제공한다. 역할이 사용할 수 있는 가족과 의미는 `references/공통-실행.md`와 역할 계약이 설명한다.

현재 확장 파일은 후보 과제의 발생 조건·의존·최초 관찰 규칙과 후보별 계약 자기점검 `contract_checks`, 부수 연구 통찰, 외부 행동 요청, 기존·신규 지식의 metadata와 관계, 검토 자리의 고정 질문, 관찰 규칙과 학술 외부 거부의 해소 근거를 전달한다. 예를 들어 새 knowledge의 `confirmed_scope`는 주 JSON의 유일한 title에 결박하고, 검토 보충 조사는 원 검토 자리의 질문 ID와 exact source references에 결박한다.

`contract_checks`는 후보 준비가 후보마다 하나씩 제출하는 `{task_title, sibling_boundaries}`다. 중앙 검사는 선언과 계약 문면을 입력 상태에 대조하며, 선택적 로컬 검사도 같은 함수를 사용한다. 대조 항목은 문면에 인용한 `TK-`·`KN-` 기록의 실재, 인용한 과제의 경계 선언과 현행 revision 일치, 개정 중인 과제에 달린 경계다. 후보 전건에 필요하다. 실행기는 이 선언을 생산 실행의 확장 기록으로 보존하며 과제 계약과 계약 검토 입력에는 넣지 않는다. 필드의 의미와 점검 순서는 후보 준비 계약을 따른다.

`task_dispositions`는 후보 준비와 연구 계획이 AI 생성 미완료 과제를 철회하는 경로다. `{task_id, disposition:"withdraw", reason}`를 받으며 입력 스냅샷의 계약 해시·생성 계보·현재 상태·실행 부재를 검사한다. 부분 결과는 보존하고 `closed` 처분과 제거한 미시작 요청을 기록한다. 완료·닫힘·수행 중 과제나 사용자 학술 요구에는 적용하지 않는다. 전체 의미와 예시는 공통 실행 문서를 따른다.

파일이 없으면 확장 없음이다. 알려진 가족의 빈 배열은 요청 없음으로 정규화하며 원 파일은 그대로 보존한다. 알 수 없는 가족, 배열이 아닌 값, 역할에 없는 비어 있지 않은 요청, 잘못된 ID·관계·현재성은 수신 실패다. 확장 적용 중 실패하면 그 확장이 속한 편입 묶음의 주 JSON·확장·관계 후보 변경을 함께 반환한다. 별도로 이미 공개된 독립 묶음과 원 출력·파일·오류는 보존한다. 전체가 하나의 판단인 계획 등은 단일 묶음이므로 그 응답 전체가 함께 적용되거나 반환된다. 작업자는 정상 본문을 재사용하면서 지적된 부분을 수리할 수 있다.

### 정지·운영 피드백 파일

관리 디렉터리 `.control/`의 `stop-request.json`은 정지 이유, 즉시 여부, checkpoint 기한과 “이미 얻은 결과만 보존” 지시를 가진다. 작업자는 새 연구·외부 행동을 시작하지 않고 가능한 범위의 checkpoint와 제출 초안을 마친다. `.control/observation-feedback.json`은 실행 중 운영 점검의 checkpoint 처분과 확인 요청을 전달한다. 두 파일은 연구 산출 manifest에 들어가지 않으며 사용자 결정이나 수학 판정도 아니다.

## 제출, 보존과 편입

묶음 안에서 새 형제 지식을 참조할 때는 `submission_contract.command --new-knowledge-id`로 `{"replacement_id":"KN-..."}`를 얻는다. 이 명령에는 `--output`이나 대기 시간을 주지 않는다. ID 생성은 저장·예약·허가가 아니며, 이를 사용하는 변경은 최종 편입의 전역 중복·참조 검사와 Git 공개를 거친다. 다른 새 형제 참조가 없는 변경은 `replacement_id`를 생략할 수 있다.

작업자는 실행별 스키마를 만족하는 완전한 JSON 값 하나를 정상 최종 응답으로 반환한다. 중앙은 native stream의 정상 완료, 입력·출력 결속과 로컬 종료를 확인한 뒤 정확한 최종 응답 바이트와 종료된 작업 공간의 확장·참조·모집단·수집 파일을 한 번 포착한다. 같은 실행 중 결과를 먼저 봉인해야 할 때에는 `submit_draft(draft_path=<draft>)` 또는 `submission_contract.command --output <draft> --submit --wait-seconds N`으로 초안 하나를 명시적으로 조기 제출할 수 있다. 두 조기 제출 경로가 중앙에 보내는 의미 입력은 작업 공간 상대 `draft_path` 하나다. 중앙은 어느 전달 방식에서도 실제 포착본에서 검사 ID·해시·스키마·도구 판본·파일 크기와 manifest를 자동 생성하며, 작업자는 이 값을 전사하거나 검사 보고를 증빙으로 다시 제출하지 않는다. 명시 제출의 CLI 반환은 `delivery`이며 `state=accepted`일 때만 조기 접수됐다.

필요할 때만 `submit_draft`의 `preview=true` 또는 셸 명령의 `--preview --wait-seconds N`으로 경로를 미리 진단한다. 셸에서 `--submit`과 `--preview` 없이 `--output <draft>`만 실행하면 로컬 `producer_check`의 `passed`와 문제 목록을 얻지만, 이 결과는 최종 접수의 필수 증거가 아니며 중앙으로 전송되지 않는다. `--preview`는 로컬 `check`와 별도로 중앙이 그 호출에서 포착한 후보의 `delivery.state=previewed`를 돌려준다. Preview는 비권위 결과이며 Git 공개, 외부 효과, 운영 수리, 수학 판정을 실행하지 않는다. 명시적 조기 제출과 정상 final은 각각의 호출 또는 정상 완료에서 포착한 정확한 바이트를 같은 봉인 규칙으로 처리한다.

검사 결과의 `check.passed`는 전건 구조 검사 통과를 뜻한다. `capture_eligible`은 그 정확한 후보를 봉인할 수 있는지를 뜻하며, 두 값은 중앙 접수 결과인 `delivery.state=accepted`와 별개다. 「공통 실행」의 독립 묶음 조건을 만족하면 국소 오류가 남아도 후보를 접수하여 정상 묶음부터 적용할 수 있다. 로컬 `--output`의 종료 코드는 전체 검사 결과를 나타내므로 중앙 `delivery.state=accepted`와 구별한다. 접수된 후보의 국소 오류는 후속 수리에서 다루며 다른 final로 후보를 대체하지 않는다. Preview와 로컬 검사를 생략해도 정상 최종 응답을 접수할 수 있다.

중앙 실행기는 구조 검사 뒤 실제 권한·입력 판본·현재성·참조·영향을 추가 대조한다. 정확한 제출 바이트와 확장·수집 파일·기계 검사·manifest를 불변 후보로 보존하고 정상 종료·허가된 복구·재시작에서 같은 후보를 사용한다. 이미 접수된 조기 봉인 후보가 있으면 그것만 사용하고 뒤의 다른 final로 바꾸지 않으며, 봉인본이 손상돼도 다른 final로 fallback하지 않는다. 봉인 후보가 없을 때에만 완전한 native stream, 정상 완료, 입력·출력 결속, 현재 권한과 로컬 종료가 확인된 final을 같은 중앙 경로로 포착한다. 오류·중단·불완전하거나 혼합된 stream, 정지, 권한·현재성 위반의 응답과 파일은 보존만 한다.

`integration_bundles`를 반드시 선언해야 하는 경우는 [공통 실행](공통-실행.md)의 「주 응답의 의미와 보존」 절이 정한다. 그 밖의 응답에서 생산자가 `integration_bundles`를 생략하면, 기계가 주 응답·확장 구성원 전건을 한 묶음으로 만든다. 독립성을 추측해 나누지 않으며 기계 ID·구성원 좌표·지급 권한을 생산자에게 다시 쓰게 하지 않는다. 생산자가 split을 명시했거나 선언이 필요한 경우에는 그 선언과 이전 근거를 유지한다. 개정 구성원이 없는 묶음이 비어 있지 않은 `impact_set`을 명시하면 중앙 접수 전에 구조 오류로 반환하고 조용히 지우지 않는다. 각 묶음은 Git CAS 한 번으로 공개되거나 전부 반환된다.

한 묶음의 실패는 그 묶음의 후보 변경을 버린다는 뜻이다. 이미 수락된 다른 독립 묶음이나 보존된 원 산출까지 되돌리지 않는다. 재시도는 원 묶음의 정체성과 입력·산출 해시를 대조하며 이미 수락된 묶음을 중복 적용하지 않는다. 기계가 선언을 통과시켰다는 사실은 묶음의 수학적 독립성을 입증하지 않는다.

실행기는 계산된 의존을 생산자의 선언과 관계없이 적용한다. 생산자가 계산된 의존 밖의 기록을 영향으로 선언했거나, 계산이 해석하지 못한 참조가 남거나, 변경이 목적·권한·신뢰·완료 기준에 영향을 주면 지정 독립 의미 검토가 필요하다. 선언이 계산된 의존의 일부를 빠뜨린 것만으로는 검토를 열지 않는다. 검토의 승인도 계산된 의존을 덮어야 하므로, 빠뜨린 선언은 적용 결과를 바꾸지 못하기 때문이다. 계산된 의존이 따라가는 참조 필드는 [공통 실행](공통-실행.md)의 편입 묶음 절이 정하며, 과제가 `basis_refs`·`authority_refs`·`profile_refs`로 가리킨 기록의 개정도 그 과제를 계산된 영향에 넣는다. 독립 검토는 정확한 원 묶음과 변경별 영향 계획에 결박되어야 하며, 생산자가 자기 응답에 승인 문구를 붙여 대신할 수 없다. 해당 검토·현재성·권한이 해소되지 않은 묶음은 보류하고 실제 다음 소유자에게 반환한다.

출력 형식 수리는 `max_output_repairs` 안에서 같은 의무를 잇는 새 실행으로 처리한다. 새 실행 ID·정확한 프로필·예산 예약과 이전 산출·오류를 기록한다. 한도 뒤에는 실패 요청과 남은 의무를 보존하고 운영 점검에 넘긴다. 실행 종료가 활동을 자동 종결하지 않으며 활동은 후속이나 대기 조건을 계속 소유한다. `resume`만으로 보류된 출력 실패를 재생하지 않는다.

운영 응답의 `disposition.kind`는 `continue`, `repair`, `resume`, `retry`, `task_disposition`, `user_decision` 중 하나다. 처분과 현재 근거·권한을 검사한 뒤 실행 유지, 종료 후 후속, 과제 처분 또는 필요한 사용자 결정을 연결한다. 대기는 처분의 다음 소유자·해소 조건으로 표현하며, 전체 사용자 정지는 공개 `pause` 제어로 구별한다. 상세 판단 기준은 [운영 점검](../계약/운영-점검.md)에 있다.

입력 손상에 쓰는 `retry`와 설치 결함에 쓰는 `repair` 가운데 무엇을 고를지, `scope`·`replay_safety`·`repair_target`에 무엇을 적을지는 [운영 점검](../계약/운영-점검.md)이 정한다. 중앙은 `retry`를 받으면 선행 실행의 종료와 봉인된 입력을 확인하고 같은 활동의 후속 요청을 만든다. 다음 실행은 새 작업 공간과 현재 입력을 받으며 현재 프로필·권한·예산 관문을 다시 통과한다. 설치 수리의 진단·권한·잠금·검증은 아래 실행 수명·복구 절과 「독립 운영」 계약을 따른다.

늦은 산출이 이미 닫힌 과제나 종결된 검토 자리를 가리키면 그 산출은 보존하되 대상을 다시 열지 않는다. 원문을 읽지 못한 실행, 실패한 공급자 호출과 의미상 미해결 결과도 구별해 기록한다.

영향 검토를 준비할 때 생산자의 봉인 제출을 읽지 못하면 해당 생산자의 미시작 영향 검토 요청을 이력에 보존하고 제출 실패 대기로 넘긴다. 같은 요청을 다음 소유자 회차마다 다시 준비하지 않는다. 운영 진단의 복구 자료도 검증할 수 없는 파일 바이트를 입력 파일로 전달하지 않는다. `recovery_materials.output_files[].restoration_error`는 원래 artifact·snapshot·기대 해시·크기와 함께 오류 종류·사유, 읽은 경우의 실제 해시·크기를 제공한다. 이 행에는 복구 파일의 `local_path`가 없으며 수학적 산출의 수락 근거로 쓸 수 없다. 정상 파일의 복구·원문 접근 계약은 그대로 적용한다.

## 실행 수명과 복구

운영 점검의 `repair_target=installation:<스킬 상대 파일 경로>`는 수락된 의미 보존 설치 결함 진단을 바깥 복구 담당에게 전달한다. 엔진은 새 배정을 멈추고 현재 호출 종료 뒤 잠금을 반환한다. 예약 감독은 `installation_repair_pending` 또는 `installation_repair_waiting` 처분의 원 진단·실패 산출을 확인하고 기존 recovery 프로필과 잠금으로 수리한다. 동일 실패·설치 판본의 자동 시도는 한 번이다. 실제 검사 근거와 설치 검사를 확인하면 원 수리 계보를 유지한 후속을 연다. `probe`는 진단만 반환하고 모델·예약을 실행하지 않는다. 상세 범위는 「운영 점검」과 「독립 운영」을 따른다.

`run`은 인스턴스 writer lock을 얻어 현행 정본을 읽고 제어 inbox를 적용한다. 옛 판본의 자동 변환·재개는 지원하지 않는다. 이후 사라진 실행을 대조하고 현재 수명·권한·능력·신뢰·용량을 통과한 action을 배정한다. 모델 호출은 병행할 수 있지만 정본 갱신은 소유 실행기의 Git 공개 경계를 따른다.

각 실행은 정확한 활동·action·프로필·입력 snapshot에 결박된다. Windows Job과 로컬 프로세스 식별자를 기록하고 시작·종료 사실을 확인한다. 실행기 소실 복구 기록은 실제 관찰값인 `local_termination_confirmed`, 직접 확인하지 못한 `remote_termination="unknown"`, 복구 처리가 닫힌 `finished_at`을 보존한다. 로컬 종료가 확인되지 않았으면 후속 적용과 예약 반환을 진행한 것처럼 쓰지 않는다. 종료된 실행을 다시 열지 않으며 재개·수리는 `continuation_of`와 실제 입력 계보를 가진 새 실행이다. 같은 과제의 가장 최근 실행이라는 이유만으로 문맥을 승계하지 않는다.

### 실행기 소실 뒤 처분

새 실행기는 먼저 복구 기록에 대상 실행을 고정해 공개하고 각각의 상태를 대조한다.

- `queued`이고 실행·예약이 없으면 미공개 준비를 끝내고 원 의무의 후속을 연결할 수 있다. 예약이 남아 있으면 먼저 예약을 대조한다.
- 시작 여부나 로컬 종료를 확인하지 못하면 실행 공간·예약과 미확인 사실을 보존하고 다음 소유자를 남긴다. 확인 없이 실행을 닫거나 용량을 반환하지 않는다.
- 로컬 종료와 예약 정산을 확인하면 실제 파일·체크포인트를 회수하고 미완료 실행으로 종결한다. 실패 action과 부분 산출을 운영 점검에 연결하여 재개·수리·재시도 여부를 판단한다.

복구가 끝났다는 이유로 인스턴스 전체를 일괄 `paused`로 만들지 않는다. 미해소 의무와 기존 사용자 정지·대화 정책·권한을 유지하며 독립 작업의 진행 가능성은 현재 관문에서 정한다. 로컬 종료를 확인했어도 공급자 원격 종료는 별도 미관찰 사실로 남는다.

외부 효과는 원장의 전송 사실과 실제 영수증을 대조한다. 전송됐을 수 있는 요청은 `unknown`으로 보존하고 자동 재전송하지 않는다. 효과 부재가 확인된 실패와 멱등성·재시도 허가를 갖춘 경우만 외부 retry 계약으로 돌린다.

### 정지와 현재성

사용자 pause·close, 권한 철회·만료, 실행 근거 변경과 기한은 해당 실행의 정지·회수 경계를 연다. `.control/finish-request.json`과 `.control/stop-request.json`이 각각 무엇을 뜻하고 어느 실행에 오는지는 「전제·대기·조회 계약」 절의 `finish_notice_seconds` 문단이 정한다. 허용된 마무리 시간에는 이미 얻은 결과와 남은 의무를 보존한다. Windows Job의 로컬 종료 확인은 호스트 격리나 원격 종료의 보증이 아니다.

`run`은 기동할 때 설치 코드·필수 문서를 해시해 기준으로 삼는다. 실행 중에는 파일 지문(크기·수정 시각·생성 시각)이 바뀐 파일만 다시 해시해 기준과 대조하고, 해시가 바뀌면 일관된 설치본에서 재시작하도록 정지한다. 세 값을 모두 보존한 채 내용만 바뀐 경우는 이 대조로 잡지 않는다. 입력 준비·확정·결과 수신 경계의 검사와 순회 검사는 파일 변경 즉시 감지와 다르다. 이미 고정한 입력·산출은 당시 판본으로 보존한다. 입력 준비 중 제어로 전제가 바뀌면 아직 공개하지 않은 입력 준비를 정리하고 현재 입력으로 다시 판단한다.

## 형식 검사, 동일성 검토와 목표

Lean source가 있는 knowledge candidate는 중앙 `formal_check` action으로 간다. 실행기는 컴파일 전에 툴체인 기록과 판정 파일의 지문을 대조하고, 실제 실행파일, version·hash, 프로젝트 소스 식별, source hash, 선언 signature와 전이 공리 의존을 보존하고 `allowed_axioms` 밖 의존과 `sorryAx`를 거부한다. 형식 검사는 Lean 실행이 만든 다른 host 효과나 수학 해설의 의미를 보증하지 않는다.

형식 검사가 사용자 pause·HOLD로 멈추면 프로세스 종료와 예약 반환 뒤 원 action·활동과 종료 execution의 계보를 남긴다. 정상 resume·release 뒤에는 동일한 소스·선언·신뢰 환경과 현재 허가를 다시 확인하여 새 execution으로 검사한다. 컴파일러의 중간 메모리를 복원하는 것은 아니다. 소스·환경·허가가 바뀌었거나 인스턴스가 닫혔으면 이 일시 정지 재개를 적용하지 않는다.

작업자의 `formal_verifier.preview.command`는 `input/tools/check_lean.py`를 실행한다. `--source`와 반복 가능한 `--declaration`을 받고 JSON을 반환한다. `verified`이면 exit 0, 그 밖의 `rejected`, `failed`, `unavailable`, `stopped`는 exit 1이다. `authoritative=false`이며 성공한 검사의 해시는 읽은 UTF-8 소스 바이트에 결박된다. `submission-support.zip` 안의 같은 검증 코드와 입력의 구성 명령·허용 공리로 커널 검사, 선언 서명과 `#print axioms` 공리 감사를 하지만 의존 증거는 추출하지 않는다. 반환 JSON은 `status`, `reason`, `source_sha256`, `declarations`, `declaration_signatures`, `axioms`, `toolchain`, 신뢰 환경 거부의 `identity_errors`, Lean 출력 `stdout`·`stderr`와 `authoritative`, `input_snapshot`, `assurance`만 담는다. 컴파일은 별도 임시 작업 폴더와 Windows Job에서 수행한다. 다만 preview는 작업자의 로컬 Job 소유 범위에 속하므로 작업자의 기한·정지에 따라 함께 종료될 수 있다. 공유 라이브러리·Lake 프로젝트·빌드 캐시의 불변성이나 격리는 보증하지 않는다. 중앙 `formal_check`는 사전 검사 결과를 승계하지 않고 제출된 소스를 다시 검사한다.

형식 검사를 통과하면 현재 CLI는 동일성 검토 계보의 initial 결과를 서로 숨긴 채 봉인한다. 전건 complete match이고 열린 finding이 없으면 직접 집계한다. 그 밖에는 organize, 독립 judge 세 자리, 원 initial 자리의 answer와 같은 judge의 재심을 `review_rounds` 안에서 수행한다. 보충 조사, 실행 미완료와 남은 쟁점은 같은 계보에 보존한다.

실행기는 제안 판정 전에 별도 scope 실행을 열고, 채택된 검토 정책에 상대적인 `scope_assessment`를 기록한다. 범위 계획은 각 초기 자리의 제안 전건 검토를 유지하면서 필요한 전문 관점과 추가 원자료를 정하고, 자리별 필수 원자료, 정확한 선택 프로필 참조, 활동 실행 상한과 초과 처분을 고정한다. 실행기는 이 계획을 검증한 뒤에만 initial 자리를 만들며, 범위 계획자는 후속 자리의 동일성 결론을 미리 내리지 않는다.

initial 결과는 서로 숨긴 채 봉인한다. 열린 finding이 있으면 organize가 쟁점을 원 finding 좌표와 answer 자리로 연결하고, 원 자리의 answer와 세 독립 judge 자리가 정해진 계보 안에서 판단한다. 자리가 실패하거나 대화 자료가 손상된 경우에는 승인된 대체 자리와 검증된 transcript manifest만 이어받고, 누락된 턴을 복원했다고 꾸미지 않는다. 추가 전문 근거가 필요하면 고정 질문 보충 조사를 원 자리로 돌려보낸다. 실행 상한을 넘으면 계획의 `overflow_disposition`에 따라 미해결 또는 유예로 끝내며 새 자리를 무한히 만들지 않는다.

범위 계획에는 이미 사용한 횟수 `scope_executions_used`, 개정 판본에서 이어받는 초기 자리 `retained_reviewer_slots`, 그리고 정책 최소 자리 수와 이어받은 자리 수 가운데 큰 값 기준의 `minimum_scope_execution_limit`을 지급한다. 상한은 범위 계획의 필수 초기 검토·쟁점 정리·심사·답변 몫을 포함해야 한다. 배정 불가능·한도 소진·제안 자체의 입력 초과는 해당 검토의 실행 종료와 예약 반환을 확인한 뒤 실제 범위와 함께 `research_plan`의 `review_followups`로 전달한다. 자원 처분만으로 동일성 판정 기록(IA)을 만들거나 신뢰 환경을 활성화하거나 옛 판정 사용을 복원하지 않는다. 대화 복원 자료나 공통 문서만 큰 경우는 제안 재구성으로 분류하지 않는다. 유예는 기존 단계와 사용 횟수를 보존하며, 제안의 실제 개정·철회 또는 인스턴스 종결 때 그 검토를 정산한다. 새 실행 하한은 앞으로의 범위 수용·배정에 적용하고, 과거에 완료된 검토의 재열람은 당시 실제 실행·판정 증거로 검증한다.

최종 `match`, current formal source, active trust environment와 실제 dependency currentness가 있어야 현재 CLI가 K를 사용할 수 있다고 계산한다. K 편입과 목표 해결은 별도다. 목표 감사는 현재 goal basis의 독립 감사 전건을 집계하고 수학 목표는 사용할 K 없이 `mathematically_solved`가 될 수 없다.

목표 판정은 승인 헌장의 학술 요구사항을 제외한 내용과 문서를 `governance.mathematical_goal_basis`로 해시하여 `goal_basis_sha256`에 기록한다. 현재성은 이 수학적 전제와 정책·원천·지식 근거를 대조한다. `goal_revision`은 판정 당시 헌장 판본의 출처이며, 학술 요구사항만 바꾼 새 판본이 수학적 해결을 무효화하지 않는다. 목표·범위·문서 또는 정책·증거의 변경은 각각 해당 근거의 현재성 검사로 다룬다.

학술 요구가 없으면 학술 후속은 `not_applicable`이다. 요구가 있으면 현재 solution basis와 요구 revision에 결박된 과제를 만든다. 후보 준비는 그 과제의 관찰 규칙을 준비하고 난이도·중요도도 평가한다. 이 보충의 배정(`assessment_targets`, `observation_rule_targets`)·반환·보류는 [후보 준비](../계약/후보-준비.md)의 기존 과제 보충 절이 정한다. 필요한 준비가 끝나면 독립 계약 검토로, 승인 뒤에는 연구 계획의 선택과 연구 수행 및 criterion별 독립 판정으로 이어진다. 이 보충은 사용자 질문·범위·완료 의무를 바꾸지 않는다. 모든 요구가 satisfied이고 필수 외부 효과마다 같은 task·requirement·solution basis에 결박된 `confirmed`이면서 `succeeded=true`인 영수증이 있어야 academic validation이 `completed`다.

## 계획 이력과 현재 입력 범위

후보 준비와 연구 계획의 `recent_history`에는 이전에 종료한 `research_plan` 실행을 제공한다. 후보 준비에만 더하는 `preparation_history`에는 이전에 종료한 `research_preparation` 실행을 제공한다. 각 행은 `execution_id`, `role`, `outcome`, `error`, `action`을 가지며 결과 artifact가 있으면 `artifact_ref`, 실행 입력에 복원한 `local_path`, `sha256`, `bytes`를 함께 가진다. 활동 상태 필드는 이 이력 행에 넣지 않는다. 반려·실행 미완료·무산출도 제외하지 않는다.

종료되지 않은 후보 준비는 두 역할의 `ongoing_work`에 `role=research_preparation` 실행 행으로 나타난다. 이 행은 다른 실행 행의 `execution_id`, `status`, `target`, `stage`, `reason`, `input_snapshot`, `event_refs`에 더해 `goal_revision`, `policy_revision`, `revision_targets`, `assessment_targets`, `observation_rule_targets`를 제공한다. 미공개 산출이나 동료의 추론은 제공하지 않는다. 미시작 action의 병합은 서로 다른 `reasons`, `event_refs`, 사용자 요청의 `requested_by_refs`를 보존하며, `starting`, `running`, `stopping` 실행의 입력에는 새 요청을 합치지 않는다.

두 역할의 `task_catalog`는 현재 과제 전건의 요약과 각 과제의 고정 `source_ref`를 제공한다. `tasks`는 후보 준비나 계획의 현재 처분 모집단으로 제한된다. 종료 과제의 `results[].report`와 미종결 과제의 현행 계약이 필요하면 `task_catalog`에서 원문을 연다. `ongoing_work`는 미종결 실행과 대기 행동의 대상·단계·이유·공개 참조를 직접 제공한다. 이 두 조회 경로는 `ready_task_ids`의 선택 권한을 늘리지 않는다.

최초 계획·준비를 여는 조건, 헌장 변경의 전달과 준비·계획의 병렬 진행은 `SKILL.md`의 「준비된 과제 중 다음 연구를 선택한다」 절이 정한다.

이력과 다른 큰 입력은 `input/catalog/` 원문으로 바뀔 수 있으며 source reference에서 다시 읽는다. 최근 이력의 inline window가 작다는 사실은 과거 결과가 없다는 뜻이 아니다.

과거 수리 action의 previous_output 전문은 inline 이력에서 반복하지 않고 `action_source`가 가리키는 정확한 JSON으로 제공한다. 실패와 미결 사항의 원문은 계속 읽을 수 있으며, 현재 상태와 과거의 거부된 주장을 구분해 사용한다.

후보 준비와 연구 계획은 현재 goal·policies, `configuration_source`가 가리키는 활성 설정 전문, 자원과 실행 한도를 받는다. 입력 manifest와 `input/catalog/` 사본이 실제 제공한 판본·경로·해시를 고정한다. 의도 해석도 설정 변경 단위를 작성할 수 있도록 같은 `configuration_source`를 받는다. 이 세 역할 밖의 역할은 자기 판단에 필요한 설정 필드만 받고, 입력에 없는 설정값을 추측하지 않는다.

## 표현 방식과 보증 범위의 차이

현행 구현이 제공하는 기능은 다음과 같다. 각 항목의 실제 성공은 그 실행의 판본·입력·영수증과 적용 결과에서 확인한다.

- 배정된 모델에 따라 기존 CLI 로그인으로 `codex exec` 또는 `claude --print`를 호출하고 실행별 prompt·schema·문서·입력·원 출력을 보존한다.
- 인스턴스별 Git ref와 writer lock으로 기록군과 추가 전용 artifact를 Git CAS로 공개한다.
- 모델별 동시 세션 용량은 작업 역할만 예약하고, 운영 역할은 슬롯 없이 배정해 작업 점유가 계획·점검·복구를 막지 않는다.
- source·지식 candidate·종류 정의·관계, goal·policy·grant·학술 요구, 신뢰 환경·대화와 외부 HTTP 제어를 현재 schema로 처리한다.
- 중앙 Lean·공리 검사, 현재 동일성 이의 왕복, 독립 목표 감사와 학술 요구·외부 효과 영수증을 연결한다.
- checkpoint·부분 파일·실패와 external unknown을 보존해 새 실행의 복구 근거로 연결한다.

GLOSSARY.md의 공통 개념과 현행 모듈의 표현은 각각 다음처럼 해석한다.

- 연구 정본·실행 원장은 등록된 `research`·`runtime` 기록군으로 보존한다. 기록의 의미와 현재성을 판단할 때는 기록 내용과 후속 검사를 함께 확인한다.
- 활동 상태는 `ready/working/waiting/finished`, 실행 상태는 `queued/starting/running/stopping/ended`의 분리된 수명주기를 사용한다. 활동은 여러 실행을 가질 수 있으며 실행 종료로 활동이나 과제가 자동 종료되지 않는다.
- 연구 계획은 `not_assessable`을 전략적 `not_selected`와 구조적으로 구별하고 누락 입력·다음 소유자를 보존한다.
- 동일성 검토는 `scope_assessment`로 필수 관점·자리·원자료·프로필·실행 상한을 먼저 계획한다. 이 구조가 실제 독립성·전문성이나 검토 품질을 보증하지는 않는다.
- 작업 계약 검토는 고정된 다섯 항목을 근거·결함·누락 입력·다음 소유자와 함께 구조화한다. 구조화된 승인도 계약 판본과 목표·정책의 현재성 검사 없이 재사용하지 않는다.

현재 기본 Windows 실행은 Codex의 `danger-full-access`·승인 정책 `never`, Claude의 `bypassPermissions`로 기존 사용자 권한을 사용한다. Windows Job은 로컬 프로세스 수명과 자손 종료를 관리한다. 이 조합은 모든 host 파일·network·credential 접근을 차단하는 격리가 아니다. 역할 경계는 고정 문서·선별 입력, 별도 session·workspace와 같은 단계 동료 결과 비제공으로 운전하며 통계적 독립성이나 강한 OS 읽기 격리를 보증하지 않는다.

예산 예약과 공급자 대기는 인스턴스의 Git 원장에 기록한다. 정상 엔진과 실패 전용 설치 복구는 writer lock으로 상호 배제된 상태에서 같은 예약 계약을 사용한다. 현행 인스턴스의 AI 예산은 작업 역할 실행이 모델별 작업 슬롯을 점유하는 로컬 동시 점유이며, 운영 역할은 슬롯 없이 배정된다. `execution_attempts`는 누적 실행 이력의 수이며 예산 한도가 아니다. 실패·취소 후에도 로컬 종료와 정산을 확인하기 전에는 예약을 반환하지 않는다. 동시 세션 한도는 공급자 내부 호출 수나 실제 청구 상한을 나타내지 않는다. Codex·Claude가 실제 보고한 사용량과 공급자 원격 미관찰 범위는 실행 증거에 구별해 보존한다.

Claude의 원본 `stream-json`은 그대로 보존한다. 수신자는 같은 세션에서 이어지는 `init`·`result` 구간의 순서·세션 ID를 검사하고 최종 구간의 응답 하나를 선택한다. 성공 여부, worker 영수증과 로컬 Job 종료도 함께 검사한다. 실행 중 `submit_draft`로 유효한 후보를 먼저 봉인했다면 그 후보만 검사하며 뒤의 native final로 바꾸지 않는다. 그런 봉인 후보가 없다면, 수집기가 정상적으로 끝난 stream에서 선택한 응답의 최종 텍스트로 final 바이트를 한 번 도출해 보존하고, 종료된 workspace 산출과 함께 포착한다. Claude worker는 stdout을 해석하거나 최종 파일을 쓰지 않으며, Claude worker 요청에는 `final_path`가 없다. 이 텍스트는 출력 스키마를 만족하는 완전한 JSON 값이어야 하며, 역할 실행에 공급자 측 `structured_output`을 요구하지 않는다. JSON이 아닌 텍스트, 잘린 결과, CLI 오류·중단, 입력 결속·권한·현재성 실패는 정상 제출로 편입하지 않고 진단·복구 자료로만 보존하며, 손상된 봉인 후보에서 다른 final로 fallback하지 않는다. 진행 관찰은 Claude의 도구 요청·결과와 메시지도 반영한다. Claude가 보고한 `modelUsage`와 비용 추정은 원 실행 증거에 보존하며 동시 세션 예산이나 실제 청구액으로 해석하지 않는다.

Codex는 CLI가 쓴 최종 파일 `final.txt`를 final 바이트로 사용한다. 수집기는 일반 수집에서도 그 바이트를 종료 직전 `agent_message`의 본문과 대조하며, 둘이 다르면 정상 최종 응답으로 포착하지 않는다.

## 검증 근거의 해석

검증 증거는 실행 당시 코드·문서 판본과 사례 범위에 결박해 읽는다. 실행 명령과 입력, 실제 출력, 통과·실패·미실행 범위, 사용한 도구와 모델·신뢰 환경의 판본을 함께 보존한다. 과거 검증 기록이 현재 설치본의 검증을 대신하지 않는다.

스킬의 `scripts/tests/`는 회귀 검사를, `scripts/probe_cli.py --skill-only`는 모델 없는 설치 구조 검사를 제공한다. `probe_cli.py`의 실호출 검사는 provider·모델·새 증거 경로를 명시해 실행하며, Codex와 Claude 모두 제품 실행 경로로 호출한다. 설치 구조 검사와 실호출 검사는 보증 범위가 다르다. 실제 실행·중단·도구 호출은 해당 실행 증거에서, 수학적 결과는 형식 검사·동일성 판정·목표 감사에서 확인한다.

한 작은 수학 사례와 합성 fixture의 통과를 일반 연구 성능이나 수학 판단의 무오류성으로 확대하지 않는다. 현재 source를 검증하려면 안정된 사본에서 관련 테스트를 실행하고, 실제 Codex·Claude·Lean·HTTP·Windows 프로세스가 필요한 검사는 model-double 단위 검사와 구별한다.


## 전제·대기·조회 계약

`action.revision_targets`는 고칠 기존 과제의 revision·계약 해시 또는 지식의 revision·본문 해시다. 예정된 개정에 의존하는 미시작 작업은 슬롯을 잡기 전에 기다린다. 개정 위임은 `waiting_actions.kind=revision_dependency`, `revision_targets`, `delegated_targets`와 수행 과제의 `revision_request_action_id`로 연결한다. 대상별 `revision_resolutions`와 후속의 실제 개정이 의무를 해소한다. 준비·계획 입력의 `pending_revisions`는 미해소 대상을 보여 준다. 유지보수 입력도 대기열 수리를 확인할 수 있도록 이 필드와 전체 `blocked_actions`를 받는다. 선언·처분·역할 권한은 공통 실행의 확장 계약을 따른다.

`decision_basis`는 판단에 사용한 계약·기존 결과·지식 본문·원자료·사용 효력을 비교한다. 일반적인 내용 인용은 진행 표시나 검토 기록이 추가되거나 기존 결과를 바꾸지 않는 결과가 추가돼도 현재성을 유지한다. 내용과 출처가 같은 reviewing→verified 승인 상승도 현재성을 유지하지만, 철회·사용 정지·신뢰 전제 변경은 다시 확인해야 한다.

완료 판정은 판단할 결과 집합 전체를, 선택은 현재 계약·승인·착수 조건을 검사한다. `review_basis_key`는 같은 계약에 대한 검토라도 외부 전제가 달라진 경우를 구별한다. 옛 승인은 이력으로 남기되 현재 사용할 때 그 전제가 유효한지 다시 확인한다.

| 실행의 error_kind | 후속과 보존 |
|---|---|
| `output_parse`·`output_schema`·`output_contract`·`input_failure` | 중앙 수신 검사가 주 응답·확장·편입 묶음을 반려했다. 각각 파싱·출력 스키마·계약 수신·제출 파일 읽기 실패다. 반려된 묶음은 `max_output_repairs` 안에서 같은 의무의 생산자 수리로 잇는다. 한도를 넘으면 대기 행동 `kind=output_validation`으로 보존하고 운영 점검(초기화 중에는 유지보수)의 진단으로 넘긴다 |
| `publication_failure` | 검사를 통과한 묶음의 Git 공개가 실패했다. 실행기가 현재 Git 상태를 다시 읽어 공개되지 않은 묶음만 다시 적용하며 작업자의 의미 오류로 처리하지 않는다 |
| `submission_failure` | 수신·편입 처리 자체가 예외로 끝났다. 보존된 원 산출과 함께 대기 행동을 남기고 운영 진단으로 연결한다 |
| `currentness_changed` | 실행 중이나 편입의 현재성 검사에서 판단 전제가 바뀌었다. 편입 반환은 모든 문제가 `integration.currentness`일 때만 이 분류이고, 다른 문제가 섞이면 생산자 반려다. 원 역할이 변경표·이전 산출·새 입력으로 판단을 갱신하며 출력 수리 횟수는 쓰지 않는다. 같은 lineage의 자동 갱신은 한 번이다 |
| `provider_limit` | 원 행동·부분 자료를 보존하고 공급자 공통 대기로 연결한다. 같은 한도를 진단하는 모델은 호출하지 않는다 |
| `execution_failure` | 원인 미확정 호출 실패를 기존 운영 진단으로 연결한다 |
| `model_policy` | 잠금과 다른 실제 모델이 보고되어 후속을 정지한다 |

`lineage_id`는 같은 의무의 수리·재시도를 연결한다. `refresh`는 전제 변경과 원 실행을, `recovery`는 복구할 원 실행을 식별한다. 원 응답·파일·체크포인트와 실패 이력은 보존한다.

`question_links`는 원문 위치·발생 실행·owner(user/research/operations/unclassified)·영향 대상·status(open/resolved/superseded)·해소 근거다. 해소 근거는 해소마다 `{kind, resolution_ref, affected_ids}`와 선택적 `evidence`를 쌓는 `resolution_history`로 남는다. 주 응답의 `questions` 문자열 형식은 유지한다. 입력 명령의 `--responds-to <QU-ID>`는 반복할 수 있고 원문과 함께 보존된다. 독립 의도 대조의 `confirmed_question_ids`가 실제 답변을 확인한 뒤 해당 질문만 해소한다. 구조화 결정은 `resolves_questions`를 사용할 수 있으며 결정의 영향 대상과 질문 대상을 검사한다. 명시적인 답변 결정은 `{"kind":"question_answer","text":"사용자 답변","resolves_questions":["QU-..."],"target_ids":["실제-미해소-대상-ID"]}`다. `target_ids`는 비어 있지 않은 목록이며, 열거한 각 질문의 `unresolved_target_ids`(그 필드가 없으면 `target_ids`) 중 이번 답으로 실제 해소하는 대상만 넣는다. 서로 다른 대상 집합의 질문은 각각 답한다. 질문 해소가 grant나 수학 승인을 대신하지 않는다.

`claude_only_assigned_model`의 효과와 공급자 한도의 대기·재관찰 절차는 [모델과 실행예산](모델과-실행예산.md)의 「인스턴스의 Claude 모델 잠금과 공급자 대기」 절이 정한다. 기록은 같은 Git 원장의 `provider_waits`와 예약에 남는다. 인증 문맥 하나를 사용하는 인스턴스 안에서 `waiting/checking/available`을 구별하며, 오래된 정상 응답으로 새로운 제한 generation을 해제하지 않는다. status `provider_waits`의 공급자 행은 지금 새 호출을 허용하는지를 `open`으로 보여 준다.

독립 의도 대조가 보류한 질문에 공개 답변 결정을 적용하면 다음 소유자 회차에서 `import_user_decision` 대기가 풀리고 같은 원문의 재해석이 한 번 배정된다. 초기화 중과 활성 상태 모두 이 경로를 사용한다. 해소 이력은 당시 대기 전문과 실제 답변 결정 참조를 보존하며 같은 공개 요청의 재전달은 배정을 늘리지 않는다. `import_application_authority`는 정확히 봉인된 import 승인으로 해소된다.

`operator wake`는 모델 없이 연구 진입점을 깨운다. 실제 action, HOLD·사용자 정지·허가·슬롯은 다시 검사한다. wake 등록이 실패하거나 사라지면 정기 감독의 Python 진입부가 엔진 요청 전에 재조정한다. `operator status`는 wake를 함께 조회하고 `hold`는 wake 예약을 정리하며, 정리에 실패했어도 HOLD가 호출을 차단한다. 공급자 해제는 외부 unknown 요청의 재전송 허가가 아니다.

`finish_notice_seconds`는 운영 AI의 마무리 예고 상한이다. 실제 예고 구간은 이 값과 개별 호출 기한의 1/10 중 작은 것이다. 단조 시계가 그 기한을 제어하며 `.control/execution-window.json`은 실제 UTC 기한·시작 잔여 시간·예고 시각을 설명한다. 작업 예산 AI는 `deadline_source=none`이고 `effective_deadline_at`, `remaining_ms_at_start`, `finish_notice_at`은 null, `effective_notice_ms`는 0이다. 시간에 따른 마무리 예고도 만들지 않는다. `.control/finish-request.json`은 기한이 있는 운영 실행에 정상 부분 제출을 요청하고, `.control/stop-request.json`은 해당 실행의 새 연구 권한을 회수한다. 사용자 정지·권한 회수와 로컬 종료 장벽은 기한의 유무와 별개로 적용한다.

Claude 수집기는 같은 세션에서 이어진 init·result 구간 중 origin.kind가 task-notification인 알림 후속 구간을 지원한다. 이 구간들을 검사해 최종 완결 구조화 응답을 고르고 선택 행·구간·해시를 남긴다. 후속 작업의 무제출·실패·잘린 출력은 앞 성공으로 덮지 않는다. 반환 뒤 관측된 백그라운드 종료 정리 사건은 별도 보존한다. `usage_segments`와 합산 가능한 구간 카운터 `usage`, 마지막 누적 `model_usage_reported`, 범위 `usage_scope`를 구별한다. 누적값을 구간마다 다시 더하지 않는다.

```text
timeline --repository PATH --instance RI-ID [--snapshot OID]
         [--format json|csv] [--timezone Asia/Seoul] [--include-operations]
```

타임라인은 고정 snapshot의 내부 실행별 배정·보고 모델, 시작·종료·기한, 결과·실패, 계보·입력 snapshot·보존 자료·후속을 제공한다. UTC 원문과 날짜·offset을 가진 현지 시각을 함께 제공하며 과거에 기록하지 않은 시각은 null이다. 별도 운영 로그를 포함하면 파일 해시·관측 시각을 가진 다른 집계 단위로 추가한다. 연구 상태·예산 예약·공급자 대기는 같은 Git snapshot에 속한다. 별도 운영 로그와 현장 프로세스 관측은 그 snapshot 바깥의 자료이므로 각각의 해시·관측 시각·확인 범위를 구별한다.

`input_metrics`는 UTF-8 바이트로 센 문서·스키마·문맥 구성과 프롬프트 크기다. 토큰이나 실제 청구액으로 환산해 확정하지 않는다. 축소된 과제 목록은 `source_ref`의 원문으로 회수하고 ready·returned 전건과 제출 검사기의 원 집합을 유지한다.

`status.operating_summary`는 같은 snapshot에서 lifecycle, 실행·목표 상태, 최상위 차단 원인과 다음 소유자, 지속 정책, workspace, grant 만료, 감독 설정을 함께 제공한다. 실제 프로세스와 예약의 관측은 `operator status` 및 호스트 정보로 별도 확인한다.
