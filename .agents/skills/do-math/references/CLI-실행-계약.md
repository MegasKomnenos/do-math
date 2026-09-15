# do-math CLI 실행 계약

이 문서는 `do-math-cli/1`, 기능 판본 2의 구체 인터페이스 참조다. 명령행 인자, 구조화 제어, 현재 저장 형식, CLI 상태 투영, AI 입력·출력과 산출 경로를 설명한다. do-math의 목적과 전체 연구 흐름은 `SKILL.md`, 보편 개념의 정의는 `GLOSSARY.md`, 역할별 판단·산출·실패 행동은 `계약/` 문서가 소유한다.

아래에서는 공통 개념과 역할 의무를 구현하는 필드와 절차, 실제 보증 범위와 미완료 기능을 설명한다.

## 호출과 공통 반환

실행 진입점은 다음과 같다.

```powershell
python .agents/skills/do-math/scripts/do_math.py <command> [options]
```

명령 예시는 스킬을 `.agents/skills/do-math/`에 설치한 경우다. 다른 위치에 설치했다면 명령의 이 경로를 실제 스킬 폴더 경로로 바꾼다. 운영할 때는 같은 설치본의 문서와 코드를 함께 사용한다. 별도 위치의 사본을 함께 참고한다면 두 사본의 판본이 같은지 먼저 확인한다.

`profile`을 제외한 모든 명령은 `--repository`와 `--instance`를 요구한다. `init`은 새 인스턴스를 만들므로 `--instance` 대신 목표와 `--workspace`를 받는다. JSON을 입력받는 제어 명령은 UTF-8 JSON 객체 하나를 담은 `--file`을 사용한다. 중복 JSON 키, 배열이나 scalar 최상위 값, 읽기·디코딩 실패는 입력 오류다.

### 종료 코드

| 코드 | 조건 |
|---|---|
| `0` | 명령 처리가 정상 종료됐다. 제어 명령은 `effect`를 따로 확인한다 |
| `1` | `check`가 결함을 찾았거나 `profile` 결과가 `verified`가 아니다 |
| `2` | 인자·파일·JSON·필드·대상 상태가 CLI 계약에 맞지 않는다. 응답 `kind=input_error` |
| `5` | Git 저장, OS, subprocess 같은 도구 계층이 실패했다. 응답 `kind=tool_error` |

exit 0은 요청이 수학적으로 승인됐거나 과제·활동·실행이 완료됐다는 뜻이 아니다. 제어 요청은 다음 공통 필드를 반환한다.

| 필드 | 뜻 |
|---|---|
| `accepted` | 요청이 control inbox에 불변 요청으로 기록됐다 |
| `request_id` | 그 요청의 CLI 식별자 |
| `effect` | `applied`, `rejected`, `pending engine processing` 중 현재 처리 결과 |
| `reason` | 거부 또는 처분 이유. 해당하지 않으면 null일 수 있다 |
| `status`, `snapshot` | 적용 뒤 CLI 상태와 상태 commit. lock이 busy이면 아직 없을 수 있다 |

동일 인스턴스의 writer lock을 다른 실행기가 보유하면 요청은 inbox에 남고 `effect="pending engine processing"`, `lock="busy"`를 반환한다. 다음 실행기 제어 처리에서 전제가 달라졌으면 해당 요청은 `effect="rejected"`와 이유를 남기고 소비된다. 접수 사실은 적용·실행·성공을 뜻하지 않는다.

## 현재 저장과 작업 경로

인스턴스의 권위 있는 머리는 `refs/heads/do-math/<instance_id>`다. 각 상태 commit은 직전 상태 commit 하나를 부모로 가지며 현재 CLI는 다음 두 JSON 루트와 추가 전용 artifact를 저장한다.

```text
research/instance.json
runtime/state.json
runtime/artifacts/<bundle_id>/...
```

`research/instance.json`은 goal·policy·config, 지식·관계·source, grant·결정·신뢰 환경과 목표 판정을 한 객체에 보존한다. `runtime/state.json`은 CLI 운전 상태, 과제·활동·실행, queue, 질문·이력·체크포인트·외부 operation과 학술 후속을 한 객체에 보존한다. GLOSSARY.md의 연구 정본과 실행 원장에 해당하는 내용을 각각 이 두 JSON의 내부 필드로 보존한다.

artifact는 기존 경로를 수정하지 않고 새 bundle에 추가한다. 대표 경로는 다음과 같다.

| 경로 | 내용 |
|---|---|
| `runtime/artifacts/<input_bundle>/input.txt` | 모델에 전달한 전체 prompt 바이트 |
| `runtime/artifacts/<input_bundle>/schema.json` | 그 실행의 출력 JSON Schema |
| `runtime/artifacts/<input_bundle>/manifest.json` | catalog와 구현 문서의 입력 manifest |
| `runtime/artifacts/<input_bundle>/input/implementation/<path>` | SKILL·GLOSSARY·공통 reference·역할 계약의 고정 사본 |
| `runtime/artifacts/<result_bundle>/result.json` | Codex 어댑터의 완료·실패·usage를 포함한 결과 |
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

## CLI 상태와 보편 개념의 대응

GLOSSARY의 보편 상태가 개념의 뜻을 소유한다. 아래 값은 현재 CLI가 두 JSON에 저장하는 구현 투영이다.

### 인스턴스 실행 루프 `runtime.status`

| CLI 값 | 현재 코드의 뜻 | 보편 개념과의 관계 |
|---|---|---|
| `ready` | 다음 action을 처리할 수 있거나 다음 `run`을 기다린다 | 보편 인스턴스 `active` 안의 실행 가능 국면으로 볼 수 있다. 활동 `ready`와 같은 값이 아니다 |
| `running` | `run`이 한 action을 실제 처리 중이다 | 인스턴스가 active이고 현재 실행이 있을 수 있다는 CLI 국면이다 |
| `paused` | 일반 배정을 닫고 명시적 재개를 기다린다 | 보편 일시 정지에 대응한다. 모든 프로세스·원격 호출·정산 완료를 뜻하지 않는다 |
| `waiting` | queue를 진행하려면 질문·입력·권한·사건 또는 명시적 재개가 필요하다 | 보편 인스턴스 상태를 새로 만든 값이 아니라 과제·활동 대기와 실행 루프 정지를 합쳐 보여 주는 CLI 상태다 |
| `budget_exhausted` | 작업 또는 운영 AI 실행 시도 한도에 닿았다 | 자원 조건이다. 연구 완료나 보편 일시 정지의 동의어가 아니다 |
| `completed` | 현재 CLI가 목표 상태와 적용 학술 요구의 완료를 계산해 queue를 닫았다 | 보편 과제·활동 completed가 아니다. 정확한 목표 감사와 학술 상태를 함께 읽는다 |
| `closed` | 사용자 close가 queue를 비우고 새 일반 연구를 막았다 | 사용자 종결의 CLI terminal 상태다. 수학적 해결을 뜻하지 않는다 |

### 과제 `task.status`

| CLI 값 | 대응 |
|---|---|
| `planned` | 작업 계약을 저작했지만 현재 독립 검토·착수 검사를 마치지 않은 보편 planned 과제 |
| `ready` | 계약 검토와 현재 착수 검사를 통과해 배정 후보가 된 planned 과제의 CLI 표시 |
| `needs_revision` | 계약·목표·정책·범위 변화 때문에 새 정련 또는 계약 검토가 필요한 planned 과제 |
| `performing` | 연구 수행이 선택·배정된 보편 active 과제 |
| `assessing` | 결과를 반환했고 지정 판정자가 완료 기준을 확인하는 보편 active 과제 |
| `waiting` | 필수 입력·결정·권한·복구를 기다리는 보편 waiting 과제 |
| `completed` | 완료 기준 전건과 근거 있는 독립 완료 판정을 기록한 흡수 상태여야 한다 |
| `closed` | 철회·이전·대체의 근거와 범위 처분으로 닫은 흡수 상태여야 한다 |

같은 이름의 source가 갱신되거나, 과제가 참조한 지식이 개정·무효화되거나, 그 지식의 신뢰 환경이 무효화돼도 `completed`·`closed` 과제의 상태와 종결 이력은 유지한다. 현재 완료 판정은 `current=false`, `invalidated_reason`으로 사용을 정지한다. 단순 `task_disposition_is(completed)` 이력 질의는 완료 사실을 유지하지만, 실제 task dependency의 착수 검사는 낡은 완료 판정을 사용할 수 없다. 새 검증 의무는 후속 과제로 연결한다. 아직 끝나지 않은 과제가 지식 변경의 영향을 받으면 `waiting`으로 돌아가 현재 착수 검사를 다시 받는다.

### 목표와 학술 후속 상태

`goal_status`는 현재 CLI에서 `unresolved`, `mathematically_solved`, `research_goal_satisfied`를 사용한다. 첫 값은 해결 불가능 판정이 아니다. `mathematically_solved`는 수학 목표에 필요한 현재 K와 독립 감사가 갖춰진 경우, `research_goal_satisfied`는 비형식 연구 목표의 지정 산출과 감사가 갖춰진 경우다.

`academic_validation.status`는 `not_applicable`, `pending`, `active`, `externally_rejected`, `completed`, 그리고 해결 근거를 읽지 못한 `incomplete`를 구별한다. 수학적 해결과 학술 검증 완료는 별도다.

status의 `knowledge.K`, `knowledge.F`, `knowledge.suspended_K`는 각각 `verified`이면서 현재 사용할 수 있는 record 수, `status!=verified` record 수, `verified`지만 현재 사용할 수 없는 record 수를 계산한 CLI 보기다. 특히 `knowledge.F`라는 필드명은 GLOSSARY의 가시 연구 프런티어를 완전히 분류한 목록이 아니다.

### 활동·실행·외부 operation

| 대상 | CLI 값 | 대응과 한계 |
|---|---|---|
| 활동 | `active`, `finished`, `unresolved` | `active`는 실행을 배정한 진행 국면이다. `finished`는 출력 수신·적용 성공, `unresolved`는 실행 또는 출력 적용 미완료라는 현재 CLI terminal 결과다. 보편 활동 상태 `ready/working/waiting/finished`의 완전한 wire 구현이 아니다 |
| 실행 | `starting`, `running`, `ended` | queue의 action은 실행 생성 전 `queued` 역할을 하고 stop request가 `stopping` 역할을 하지만 현재 execution status 값으로 저장하지 않는다. `ended.outcome`이 `output_accepted`, `execution_incomplete`, `output_preserved_after_close` 등을 구별한다 |
| 외부 operation | `prepared`, `running`, `confirmed`, `failed`, `unknown`, reconciliation의 `cancelled` | `running`은 전송 의도 기록 뒤의 CLI 내부 단계다. `confirmed`는 HTTP 응답 또는 명시적 대조를 확보했다는 뜻이며 `succeeded`를 별도로 확인한다 |

## 설정 계약

허용 필드와 기본값의 기계 정본은 `scripts/do_math/engine.py`의 `DEFAULT_CONFIG`와 `validate_config`다. 인스턴스에 실제 적용된 값은 해당 snapshot의 `research/instance.json` 안 `config`가 소유한다. 이 문서는 그 목록을 따로 복제하지 않고 설정 가족이 어떤 동작을 바꾸는지 설명한다.

- 실행 선택: `model`, `effort`, `role_models`가 기본 모델·추론 노력과 역할별 모델 override를 정한다. effort는 실행 코드가 허용한 닫힌 값만 받는다.
- 작업·운영 용량: `work_calls`, `operations_calls`는 각각 작업·운영 예산의 AI execution 시도 한도다. 공급자 내부 호출이나 토큰 한도가 아니다.
- 실행 시간과 반복: `call_timeout_seconds`는 운영 예산 AI 실행 하나의 기한이다. 작업 예산 AI 실행(연구 수행·보충 조사·작업 계약 검토·동일성 검토·목표 감사)에는 이 기한을 적용하지 않으며, 그 실행은 제출, `run_timeout_seconds`가 정한 `run` 호출의 기한, pause·close와 권한·입력 변경으로 끝난다. Lean timeout, 자동 후보 준비 회차, 출력 수리 횟수, 검토 회차와 보충 조사 한도는 각 대응 설정이 정한다.
- 입력·산출: 모델 입력과 한 실행의 artifact 회수 바이트 한도를 정한다.
- 형식 검사: `lean_command`는 argv 배열이며, 없으면 실행기가 지원 경로에서 Lean을 탐색한다. 허용 공리 목록은 중앙 공리 감사의 기준이다.
- 관찰: event-driven·periodic 모드, 관찰·idle 간격, 한 실행의 점검 수와 checkpoint 유예를 정한다.

다음은 일부 설정을 명시하는 예다. 생략한 필드는 현재 코드의 기본값을 사용한다.

```json
{
  "model":"gpt-5.6-sol",
  "effort":"medium",
  "work_calls":40,
  "operations_calls":30,
  "call_timeout_seconds":600,
  "run_timeout_seconds":7200,
  "lean_command":["C:/Lean/bin/lean.exe"],
  "observation_mode":"event_driven"
}
```

`configure`는 기존 설정 위에 제공 필드를 덮어쓴 뒤 전체 설정을 다시 검사한다. 알 수 없는 필드는 거부한다. 대부분의 수치 설정은 양의 정수이고, 출력 수리 횟수만 0을 허용한다. 정확한 현재 값은 `read --path research/instance.json`으로 확인한다.

## 명령 표면

### `init`

```text
init --repository PATH [--create-repository] --workspace PATH
     (--goal TEXT | --goal-file PATH) [--title TEXT]
     [--goal-kind mathematical|research] [--policies-file PATH]
     [--source PATH ...] [--config-file PATH] [--model NAME] [--effort VALUE]
```

목표·정책·설정과 초기 source를 한 인스턴스로 저장하고 첫 후보 준비 action을 queue에 넣는다. 응답은 `instance_id`, `snapshot`, `status`다. `--create-repository`는 없거나 빈 디렉터리에만 Git 저장소를 만든다. 기존 비어 있지 않은 경로와 Git이 아닌 저장소는 거부한다.

### `run`, `status`, `check`, `profile`

- `run [--max-steps N] [--watch]`는 writer lock 안에서 control을 적용하고, 사라진 실행을 복구하며, queue의 AI·형식·신뢰·외부 action을 순차 처리한다. `N`은 양의 action 수다.
- `status [--json]`은 현재 snapshot의 파생 보기를 반환한다. JSON 필드는 README의 운영 표를 따른다.
- `check`는 상태 관계와 보존 artifact의 해시·크기를 검사해 `{passed, errors, ...}`를 반환한다. 결함이 있으면 exit 1이다. 자연어 의미를 새로 검증하지 않는다.
- `profile [--codex-path PATH]`은 설치된 Codex CLI 표면을 조사한다. 인스턴스 인자는 받지 않는다.

### `pause`, `resume`, `close`, `input`, `configure`, `request`

- `pause|resume|close [--reason TEXT]`는 제어 요청을 inbox에 기록한다. `resume`은 CLI `closed`와 `completed`를 열지 않는다.
- `input (--text TEXT|--file PATH)`는 비어 있지 않은 사용자 원문을 보존하고 `intent_interpretation`을 먼저 queue에 넣는다.
- `configure --config-file PATH`는 지원 설정만 갱신한다. 목표·정책·grant·학술 요구는 각각 `decision`을 사용한다.
- `request --role ROLE [--target ID] [--reason TEXT|--text TEXT]`는 모델을 호출하지 않고 action을 queue 맨 앞에 넣는다. 지원 role은 `research_preparation`, `research_plan`, `supplemental_research`, `operational_review`, `maintenance`다. 보충 조사는 현재 `ready` 과제 ID, 운영 점검은 존재하는 execution ID를 target으로 요구한다.

`request`는 새 권한이나 완료 판정을 만들지 않는다. `completed`와 `closed` 인스턴스에는 새 요청을 넣지 않는다.

## 구조화 제어 JSON

`decision`, `knowledge`, `trust`, `external`, `conversation`은 `--file`의 JSON 객체를 control inbox에 보존한 뒤 writer가 현재 전제를 검사해 적용한다.

### `decision`

#### 목표와 정책

```json
{"kind":"goal","goal":"새 목표 원문","goal_kind":"mathematical","expected_revision":1}
```

`goal_kind`를 생략하면 현재 값을 유지한다. `expected_revision`을 생략하면 적용 시점의 현재 revision을 사용하지만, 동시 변경을 명시적으로 방지하려면 현재 값을 제공한다. 목표 변경은 미완료 과제를 `needs_revision`으로 보내고 목표 상태를 다시 판단하게 한다.

```json
{"kind":"policy","text":"정책 원문","expected_revision":1}
```

정책 변경은 미완료 과제를 다시 계약 검토하고 연구 계획을 열게 한다.

#### 로컬·HTTP grant

```json
{
  "kind":"grant",
  "grant":{
    "kind":"local",
    "roles":["research_work","identity_review"],
    "task_ids":[],
    "expires_at":null,
    "checkpoint_allowed":true
  }
}
```

로컬 grant의 `roles`는 지원 역할의 비어 있지 않은 목록이고, `task_ids`가 비어 있으면 그 role의 모든 과제를 대상으로 한다. `valid_from`과 `expires_at`을 지정할 수 있다. 새 grant의 만료 시각은 적용 시점보다 뒤여야 한다.

```json
{
  "kind":"grant",
  "grant":{
    "kind":"http",
    "allowed_origins":["https://example.org"],
    "allowed_methods":["POST"],
    "allowed_path_prefixes":["/submissions/"],
    "credential_env":{"Authorization":"MATH_SUBMISSION_TOKEN"},
    "allow_idempotent_retry":true,
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

```json
{"kind":"task_scope","task_id":"TK-...","disposition":"revise","reason":"필수 범위를 다시 정해야 한다."}
```

`disposition`은 `revise`, `transfer`, `withdraw`다. `transfer`는 서로 다른 미완료 대상의 `target_task_id`를 요구하고 양쪽의 미종료 실행이 없어야 한다. 현재 CLI는 받는 과제의 기존·이전 완료 기준을 합쳐 revision을 올리고 계약 검토를 다시 연다. `withdraw`와 `transfer`는 원 과제를 `closed`로 만든다.

#### 학술 요구와 외부 거부

```json
{
  "kind":"academic_requirements",
  "requirements":[
    {
      "id":"paper-reproduction",
      "scope":"해설과 Lean 결과를 독립적으로 재현할 자료를 만든다.",
      "assessor":"research_plan",
      "criteria":["새 환경에서 Lean 결과를 재빌드했다.","해설의 가정과 선언 대응을 기록했다."],
      "required_inputs":[],
      "external_effects":[]
    }
  ]
}
```

각 requirement는 고유한 `id`, 비어 있지 않은 `scope`, `assessor="research_plan"`, 중복 없는 비어 있지 않은 `criteria`를 요구한다. `required_inputs`는 정확한 입력 참조 목록이다. `external_effects`의 각 항목은 고유 `id`, `scope`, 선택적 `grant_id`를 가진다. 요구 목록의 변경은 새 revision과 SHA-256을 만들고 현재 해결 근거에 결박된 새 과제를 생성한다.

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

`knowledge`는 다섯 operation을 지원한다.

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

`kind`는 현재 종류 정의 레지스트리에 있어야 한다. `title`, `statement`, `explanation`, `summary`는 비어 있지 않아야 하고 `lean_code`가 있으면 중복 없는 `declaration_names`가 필요하다. `dependencies`는 존재하는 다른 knowledge ID만 받는다. `id`를 제공해 기존 기록을 개정할 수 있으며 revision과 history를 보존한다. 실행기 소유 필드인 검증 status·formal 결과·review·identity assessment는 candidate가 제공할 수 없다.

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

`family`는 현재 CLI에서 `knowledge` 또는 `relation`이다. `token`은 소문자로 시작하는 영문 소문자·숫자·underscore 문자열이고 기존 token과 중복될 수 없다. 수학 주장 종류는 `requires_formal_results`와 `requires_assessments`가 자동으로 참이 된다. 이 `knowledge` family는 현재 CLI 레지스트리의 구현 이름이며 GLOSSARY.md의 F 객체 의미를 새로 정의하지 않는다.

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

```json
{"operation":"register","toolchain":{"executable":"C:/Lean/lean.exe","sha256":"...","version":"..."},"allowed_axioms":["propext","Classical.choice","Quot.sound"]}
```

`toolchain`은 비어 있지 않은 객체, `allowed_axioms`는 중복 없는 문자열 목록이다. 현재 구현은 구조를 보존하지만 register 자체가 실행파일 지문을 다시 측정해 준다고 가정하지 않는다.

```json
{"operation":"transition","env_id":"TE-..."}
```

전환 대상은 등록됐고 invalid가 아니며 `toolchain.sha256`을 가져야 한다. 현재 verified K 전건을 같은 source와 basis에서 재검사하고 모두 verified일 때만 활성 환경을 바꾼다. 전환은 환경 원인의 사용 정지만 해소한다.

```json
{"operation":"invalidate","env_id":"TE-...","reason":"무효화 근거"}
```

무효화는 해당 환경을 쓰는 K의 형식 사용을 정지하고 실제 의존 과제·목표 판정을 다시 계획하게 한다.

### `external`

```json
{
  "operation":"prepare",
  "grant_id":"GR-...",
  "id":"optional-stable-operation-id",
  "request":{"method":"POST","url":"https://example.org/submissions/1","body":"UTF-8 text"}
}
```

현재 HTTP method는 `GET`, `POST`, `PUT`, `DELETE`다. URL은 http/https, host와 안전한 path를 가져야 하고 userinfo·fragment·`.`·`..` path segment를 허용하지 않는다. redirect는 거부한다. request를 정규화해 hash와 idempotency key를 만들고 active HTTP grant의 origin·method·path·기간을 검사한다.

실행기는 `prepared`, `running`, `transmitted`를 저장한 뒤 전송한다. transport 결과를 확정할 수 없으면 `unknown`이다. HTTP 응답을 받으면 `confirmed`, `http_status`, body hash를 기록하고 `succeeded`는 실행 기록에서 2xx 여부로 별도 계산한다.

```json
{"operation":"reconcile","id":"EO-...","result":"confirmed","succeeded":true,"evidence":"외부 영수증 좌표"}
```

reconcile은 현재 `unknown` operation에만 적용하고 result는 `confirmed`, `failed`, `cancelled`다. `succeeded`는 confirmed일 때만 명시적 boolean으로 줄 수 있다.

```json
{"operation":"retry","id":"EO-...","grant_id":"GR-..."}
```

retry는 알려진 `failed` 또는 `cancelled`만 받는다. 전송 가능성이 있었으면 현재 grant의 `allow_idempotent_retry=true`가 필요하다. 같은 operation ID·request hash·idempotency identity를 유지하고 새 execution과 시도 이력을 만든다. `unknown`은 retry 전에 reconcile한다.

### `conversation`

```json
{"operation":"attach","id":"conversation-1","generation":1,"disconnect_policy":"pause","lease_seconds":60}
```

`generation`은 양의 정수이고, 재연결은 이전보다 큰 generation을 사용한다. `disconnect_policy`는 `pause` 또는 `continue_authorized`이며 `continue` 입력은 후자로 정규화된다. lease는 유한한 양수 초다.

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

구조화 record를 ID 순서로 조회한다. `kind`는 record family 또는 구체 kind와 일치한다. text는 정규 JSON 전체를 대소문자 구분 없이 찾는다. 관계 이웃 조회는 relation record와 반대편 endpoint를 함께 반환한다.

응답은 `snapshot`, 전체 `total`, 이번 `loaded`, `truncated`, `items`, `next_cursor`다. 각 item은 `record`와 그 정규 JSON `sha256`을 가진다. cursor는 query 인자와 snapshot에 결박되며 조건을 바꾸어 재사용할 수 없다.

### raw file `query --files`

```text
query --files [--snapshot OID] [--prefix research/|runtime/.../] [--text TEXT]
              [--limit N] [--cursor CURSOR]
```

경로와 UTF-8 query byte가 일치하는 snapshot 파일을 POSIX 경로 순으로 반환한다. 각 항목은 path·size·SHA-256을 가진다. prefix는 `research/` 또는 `runtime/` 아래에서 `/`로 끝나야 한다.

### `read`

```text
read [--snapshot OID] (--id RECORD_ID | --path POSIX_PATH) [--output PATH]
```

`--id`는 구조화 record와 정규 JSON hash를 반환한다. `--path`는 exact snapshot의 파일을 읽어 UTF-8이면 `text`, 아니면 `base64`로 반환한다. `--output`을 주면 바이트를 로컬 파일로 쓰고 path·snapshot·size를 반환한다.

### `export`

```text
export --destination PATH [--snapshot OID] [--all]
```

기본은 `research/`만, `--all`은 `research/`와 `runtime/`을 새 경로나 빈 디렉터리에 복사한다. reparse point를 지나는 목적지와 비어 있지 않은 디렉터리는 거부한다. export 결과는 snapshot 사본이며 새 정본이나 쓰기 작업 공간이 아니다.

## AI 실행 입력

각 AI 실행은 새 Codex CLI session과 `<workspace>/runs/<execution_id>/workspace`를 받는다. 기계 실행기는 SKILL의 역할 읽기 대응표를 파싱해 다음 문서를 선언된 순서로 입력에 넣고, 같은 바이트를 `input/implementation/`과 input artifact에 보존한다.

1. `SKILL.md`
2. `GLOSSARY.md`
3. `references/공통-실행.md`
4. `references/지식-저작과-재사용.md`
5. 해당 `계약/<역할>.md`

`references/CLI-실행-계약.md`는 운영자와 구현자를 위한 참조이며 모든 AI 역할에 자동 주입되지 않는다. 역할이 판단할 현행 필드와 단계는 자기 계약, canonical input context와 실행별 출력 schema가 소유한다.

입력 context의 공통 필드는 현재 snapshot과 workspace, goal·goal_kind·policies, action, 대상 task, 과제 목록, knowledge catalog, relations, sources, 사용자 입력, 열린 질문, 최근 이력, grant 요지, 자원·시간 한도, kind definitions, 중앙 형식 검사 설명, 학술 요구·상태와 외부 operation을 포함한다. 후보 준비와 연구 계획은 활성 `config` 전문도 받는다. 역할과 action에 따라 proposal, review context, eligible knowledge, operational observation, intent interpretation 입력, 이전 output 파일과 checkpoint가 추가되거나 비공개 자료가 제거된다.

모든 knowledge와 source 원문은 `input/knowledge/`, `input/sources/`, `input/task-results/`, `input/review-cycles/` 아래의 실행별 사본으로 물질화한다. catalog의 `path`나 `local_path`는 이 workspace 안의 파일을 가리킨다. 해시와 목록이 있다는 사실은 모델이 원문을 읽었다는 뜻이 아니다.

### 입력 크기 조정

기계 실행기는 최종 prompt의 UTF-8 바이트를 `max_input_bytes` 안에 맞춘다. goal, goal_kind, policies, action, 대상 task·proposal·review context·사용자 원문처럼 action별 mandatory key는 제거하지 않는다.

크기가 넘으면 recent history의 오래된 항목을 줄이고, 큰 tasks·knowledge·source 등의 상세 배열을 `input/catalog/<key>.json`의 exact source reference로 바꾼다. tasks를 바꿀 때는 `ready_universe_ids`와 가능한 `ready_listing`을 남긴다. mandatory context가 넘거나 ready 모집단을 보존하고도 입력을 맞출 수 없으면 AI 실행을 시작하지 않는다. identity review 제안 자체가 넘으면 현재 CLI는 지식 상태를 `needs_reconstruction`으로 표시하고 후보 준비에 분해 요청을 보낸다. 다른 역할은 waiting action과 질문으로 남긴다.

### 입력 고정과 현재성

실행 기록은 input snapshot, prompt hash, input bundle, engine hash, 모델·effort, goal·policy revision, 작업 계약 hash, 실제 지식·source basis와 grant를 고정한다. 결과 적용 직전에 다음을 다시 검사한다.

- goal·policy와 학술 요구 판본
- 대상 작업 계약 hash와 closed 여부
- 실제 사용 지식·source basis
- 현재 grant와 역할 권한
- 실행 중 설치 코드·역할 문서의 변경

전제가 바뀌면 결과를 정본에 적용하지 않고 원 출력과 부분 파일을 보존한다. 무관한 snapshot 전진만으로 모든 결과를 버리지는 않는다.

## 역할별 주 JSON

모든 AI 응답은 실행별 `schema.json`을 만족하는 JSON 객체 하나여야 한다. 이 실행별 schema와 수신 검사 코드가 필드·자료형·필수 여부·닫힌 값의 기계 정본이다. 아래 설명은 소비자가 각 역할 필드를 어떻게 해석하는지 밝히며 완전한 필드 목록을 별도 정본으로 만들지 않는다. Markdown fence나 JSON 밖의 설명은 허용하지 않는다.

모든 역할은 이번 판단·결과를 설명하는 `summary`, 실제 사용한 제공 ID·reference·workspace 좌표의 `used_sources`, 결과를 바꿀 미해결 질문의 `questions`를 가진다. 빈 배열과 필드 부재는 다르며, 실행별 schema가 요구한 필드는 생략하지 않는다.

### 후보 준비 `research_preparation`

주 산출 `candidates`는 새 과제와 기존 미완료 과제의 개정을 구별한다. 새 과제는 `revises_task_id=null`, 개정은 정확한 task ID를 쓴다. 각 후보는 질문·범위·기대 결과, 중복 없는 완료 기준, 정확한 입력·재사용 참조와 formal/nonformal 작업 구별을 제공해야 한다. 수신자는 기존 미완료 기준을 개정안에 합치고 새 과제를 `planned`로 만들며 독립 작업 계약 검토를 queue에 넣는다. 후보 결과가 비어 있을 수 있지만 그 경우도 실제 탐색 범위와 다음 조건을 설명한다.

### 작업 계약 검토 `task_contract_review`

주 decision은 `approved`, `revision_required`, `unresolved`를 구별하고 findings에 항목별 근거·결함·남은 질문을 남긴다. 승인은 정확한 task revision, contract hash와 goal·policy revision에 결박된다. `approved`는 task를 곧바로 실행하지 않고 다음 착수 검사와 연구 계획의 입력으로 보낸다.

### 연구 계획 `research_plan`

`selections`에는 현재 ready 과제의 정확한 ID만 실행 순서대로 두고, `deferred`에는 선택하지 않은 ready 과제의 ID와 이유를 둔다. `preparation_requests`는 후보 준비가 처리할 정련·탐색을, `goal_audit`는 현재 근거로 목표 감사를 열지를 표현한다. `task_assessments`는 이미 결과를 반환한 assessing·waiting 과제에만 사용한다. 각 완료 판정은 계약의 completion criterion 원문을 정확히 한 번 복사해 충족 여부와 실제 evidence를 연결한다. 수행 전 과제를 판정하거나 ready 과제를 assessment에 넣지 않는다.

수신자는 ready 모집단의 모든 ID가 selections와 deferred 중 정확히 한 번 있는지 검사한다. 현재 기본 schema에는 판단 불가를 별도 후보 처분으로 표현하는 필드가 없다. 판단할 수 없는 후보를 일반 보류와 같은 의미로 숨기지 않고 `deferred.reason`, `questions`와 준비 요청에 실제 원인을 보존해야 하며, 보편 처분을 충실히 구조화하는 필드는 미완료다.

### 연구 수행 `research_work`와 과제 기반 `supplemental_research`

두 역할의 기본 주 schema는 같다. `outcome`은 `submitted`, `partial`, `waiting`, `no_result`를 구별하고, `report`는 실제 수행 범위·근거·결과·한계를 설명한다. 새 knowledge와 relations, 남은 의무와 최종 인계 요지도 함께 반환한다.

knowledge 항목은 주장·해설·목차 요지와 형식 원문·선언·의존을 함께 표현한다. kind enum은 실행 시점의 active knowledge 종류 정의에서 동적으로 만든다. Lean 원문이 있으면 정확한 declaration names가 필요하다. dependencies는 기존 knowledge ID 또는 같은 응답의 유일한 title을 사용한다.

relation 항목은 `kind`, `source`, `target`, `evidence`를 가진다. source와 target은 기존 ID 또는 같은 응답의 유일한 title이다. 종류·근거·수학 판정의 추가 제약은 적용 시 kind definitions와 `activity-extensions.json`의 metadata를 함께 검사한다.

### 기본 동일성 검토 `identity_review`

검토 계보 action이 아닌 이전 단순 검토 경로에서는 `decision`, `findings`, `scope_complete`를 사용한다. decision은 `match`, `mismatch`, `unresolved`다. 현재 기능 판본의 일반 수학 제안은 아래 검토 계보의 동적 schema를 사용한다.

### 목표 감사 `goal_audit`

`decision`은 `satisfied`, `not_satisfied`, `unresolved`이고 `reason`과 `scope_complete`를 요구한다. 같은 basis의 독립 감사 전건이 완료돼야 집계한다. 수학 목표는 현재 사용할 수 있는 K 없이 해결 상태가 될 수 없다.

### 운영 점검 `operational_review`

종료된 실패 진단의 decision은 `retry`, `revise`, `wait`, `stop`이다. 실행 중 관찰로 열린 `live_review=true`에서는 `continue`, `checkpoint`, `revise`, `wait`, `stop`을 쓴다. `reason`은 관찰한 상태, 처분의 목적과 재개 조건을 설명한다. live checkpoint 처분은 부모 workspace에 `observation-feedback.json`으로 전달한다.

### 의도 해석 `intent_interpretation`

`action.stage=interpret`에서는 `interpretation`, `proposed_changes`, `needs_clarification`을 사용한다. 각 proposed change는 `kind=goal|policy|none`, `text`, `reason`을 가진다. `action.stage=check`에서는 `decision=match|mismatch|unresolved`, `findings`, `scope_complete`로 보존 원문과 해석을 독립 대조한다.

현재 schema가 구조화하는 변경은 goal과 policy뿐이다. 연구 맥락·설정·grant 등 다른 내부 소유자의 의미 변경을 이미 적용한다고 문서로 확대하지 않는다. 그런 입력은 확인한 정보와 다음 소유자를 보존한 뒤 해당 구조화 decision 경로가 필요하다.

### 유지보수 `maintenance`

`report`와 `remaining_work`를 요구한다. 구체 대상·권한·성공 조건은 maintenance를 연 action과 호출 절차가 제공한다. 이 역할 이름만으로 임의 기계 작업이나 수학 판단 권한이 생기지 않는다.

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

`progress_state`는 `working`, `blocked`, `no_progress`, `ready_to_submit`이다. iteration과 counters는 선택 필드이며 음수가 아닌 정수다. 파일은 workspace 안의 일반 파일이어야 하고 4 MiB 이하이며 완전한 JSON Schema를 만족해야 한다. 쓰는 중인 파일과 invalid 파일은 이전에 관찰한 유효 checkpoint를 대체하지 않는다.

### `observation-rules.json`

작업자가 실행 중 관찰 규칙을 바꾸는 파일이다. 배열·필드·연산자·크기 한도와 작성 예시는 실제 생산 역할에도 제공되는 [공통 실행](공통-실행.md)의 「진행을 기록하고 관찰 요청에 응답한다」 절을 따른다. 기계 검사는 `scripts/do_math/observations.py`의 `validate_rules`와 `ObservationTracker.observe`가 수행한다. 규칙 도래는 운영 점검을 열 뿐 연구 진전·실패·중단을 판정하지 않으며, 잘못된 갱신은 마지막 유효 규칙을 바꾸지 않는다.

후보 준비가 새·개정 과제에 최초 관찰 규칙을 제안할 때는 `activity-extensions.json`의 `task_conditions` 항목에 `observation_rules`를 넣고 같은 결과의 `task_title` 또는 정확한 `task_id`에 결박한다. 실행기는 이를 `initial_observation_rules`로 작업 계약 hash와 계약 검토에 포함하고, 실제 연구 수행 tracker의 시작 규칙으로 사용한다.

### `activity-extensions.json`

주 JSON 밖의 선택적 요청·메타데이터를 담는 객체다. 허용 top-level 가족의 기계 목록은 `engine.py`의 확장 파일 parser와 적용 함수가 소유하고, 역할이 사용할 수 있는 가족과 의미는 `references/공통-실행.md`와 역할 계약이 설명한다.

현재 확장 파일은 후보 과제의 발생 조건·의존·최초 관찰 규칙, 부수 연구 통찰, 외부 행동 요청, 기존·신규 지식의 metadata와 관계, 검토 자리의 고정 질문, 관찰 규칙과 학술 외부 거부의 해소 근거를 전달한다. 예를 들어 새 knowledge의 `confirmed_scope`는 주 JSON의 유일한 title에 결박하고, 검토 보충 조사는 원 검토 자리의 질문 ID와 exact source references에 결박한다.

파일이 없으면 확장 없음이다. 알 수 없는 가족, 배열이 아닌 값, 역할에 없는 권한, 잘못된 ID·관계·현재성은 수신 실패다. 확장 적용 중 하나가 실패하면 주 JSON의 의미 적용도 이전 상태로 되돌리고 원 출력·파일·오류를 보존한다.

### 정지·운영 피드백 파일

`stop-request.json`은 정지 이유, 즉시 여부, checkpoint 기한과 “이미 얻은 결과만 보존” 지시를 가진다. 작업자는 새 연구·외부 행동을 시작하지 않고 가능한 범위의 checkpoint와 주 산출을 마친다. `observation-feedback.json`은 실행 중 운영 점검의 checkpoint 처분과 확인 요청을 전달한다. 두 파일은 사용자 결정이나 수학 판정이 아니다.

## 출력 수신과 한정 수리

Codex 어댑터가 완료를 반환하면 실행기는 주 JSON Schema, workspace 파일 수집, goal·policy·계약·지식·source·학술 요구·grant의 현재성을 검사한다. 모두 통과해야 execution outcome을 `output_accepted`로 유지하고 역할 결과와 확장 파일을 적용한다.

검사 실패 시 원 모델 output, result, 파일 manifest와 오류를 artifact에 보존하고 실행 outcome을 `execution_incomplete`, 활동을 `unresolved`로 바꾼다. `max_output_repairs`가 남아 있으면 같은 action에 `repair.error`와 `repair.previous_output`을 넣은 새 실행을 한정적으로 연다. 수리는 새 실행이므로 새 ID와 실행 시도 예산을 사용한다. 수리 한도를 넘으면 action을 waiting으로 보존하고 인스턴스를 paused로 만든다.

모델 호출 자체가 실패하면 부분 파일과 checkpoint를 보존하고, 기본적으로 한 번의 operational review를 먼저 queue에 넣어 복구를 판단한다. 같은 실패를 새 ID만 바꾸어 자동 반복하지 않는다.

## 실행 수명과 복구

`run`은 writer lock을 얻은 뒤 현재 상태를 다시 읽고 다음 순서로 운전한다.

1. 저장된 계약 판본과 알려진 additive feature 2 필드를 현재 runtime에 맞춘다.
2. control inbox를 순서대로 적용한다.
3. 이전 실행기가 남긴 미종료 execution을 회수한다.
4. 현재 수학적 해결과 학술 요구에서 필요한 후속 과제를 확인한다.
5. queue의 순서를 유지하면서 해당 AI 예산이 소진된 action을 건너뛰고, 남은 예산으로 진행할 수 있는 첫 AI action 또는 기계 action을 처리한다. 각 action의 권한·착수 조건은 해당 실행 경로에서 다시 검사한다.
6. 결과와 artifact를 저장하고 후속 action·현재성을 갱신한다.

AI 실행을 시작할 때 현재 예산과 grant, 대상 과제의 readiness를 다시 검사한다. 현재 Codex 어댑터는 `codex_worker.py`를 Windows Job의 루트이자 실행 래퍼로 시작한다. 루트의 PID·생성 시각과 Job 프로세스 집합을 추적하고, 래퍼는 고정 prompt·schema로 `codex exec`을 호출해 JSONL·최종 응답·상태 파일을 남긴다. 한 예산의 실행 시도 수가 설정 한도에 닿으면 그 예산을 쓰는 요청은 queue의 원래 위치에 남기고, 다른 예산의 요청과 기계 action은 계속 검사한다. queue에 남은 요청 전부가 해당 예산의 소진으로 진행할 수 없으면 `budget_exhausted`로 끝난다. grant가 없으면 action을 waiting으로 옮기며 다른 queue action은 계속할 수 있다.

실행 중 pause·close, goal·policy·계약·지식·source·학술 요구 변경, grant 철회, 운영 예산 실행의 call deadline 또는 `run` 기한을 감지하면 `stop-request.json`을 쓴다. 즉시 중단 조건이 아니면 `checkpoint_grace_seconds` 동안 이미 얻은 결과를 보존할 기회를 준 뒤 Codex 실행의 로컬 프로세스 트리를 끝낸다. 현재 실행의 실제 Job 종료와 output 수집을 확인하지만 공급자 내부 원격 호출 종료는 보증하지 않는다.

### 실행기 소실 뒤 재개

새 실행기는 `starting` 또는 `running`으로 남은 execution마다 workspace 파일, adapter evidence와 checkpoint를 회수한다. 그 execution을 `ended/execution_incomplete`로 닫고 활동을 `unresolved`로 기록한다. 원 action은 `recovery={execution_id, reason}`을 가진 새 queue action으로 연결한다. 이전 실행을 다시 열거나 checkpoint에 없는 결과를 추측하지 않는다.

외부 operation이 `running`이었다면 원장의 `transmitted`를 확인한다. 실행기는 요청을 보내기 직전에 `transmitted=true`를 공개하므로, 그 값이 `true`이거나 없으면 요청이 나갔을 수 있어 `unknown`으로 바꾸고 자동 재전송하지 않는다. `transmitted=false`로 남았으면 요청이 나가기 전에 멈춘 것이므로 효과 부재가 확정된 `failed`로 닫고, 같은 요청은 `external` retry 절차로만 다시 준비한다. 모든 미종료 실행을 정리한 뒤 CLI는 `paused`가 되며 운영자가 status·check·원자료를 확인하고 명시적으로 resume해야 한다.

실행 중 설치 코드나 역할 문서의 hash가 바뀌면 현재 `run`은 `paused`로 전환하고 일관된 새 실행기 판본에서 재시작하도록 질문을 남긴다. 이미 고정한 과거 input·output artifact는 생성 당시 판본으로 보존한다.

## 형식 검사, 동일성 검토와 목표

Lean source가 있는 knowledge candidate는 중앙 `formal_check` action으로 간다. 실행기는 실제 실행파일, version·hash, project fingerprint, source hash, 선언 signature와 전이 공리 의존을 보존하고 `allowed_axioms` 밖 의존과 `sorryAx`를 거부한다. 형식 검사는 Lean 실행이 만든 다른 host 효과나 수학 해설의 의미를 보증하지 않는다.

형식 검사를 통과하면 현재 CLI는 동일성 검토 계보의 initial 결과를 서로 숨긴 채 봉인한다. 전건 complete match이고 열린 finding이 없으면 직접 집계한다. 그 밖에는 organize, 독립 judge 세 자리, 원 initial 자리의 answer와 같은 judge의 재심을 `review_rounds` 안에서 수행한다. 보충 조사, 실행 미완료와 남은 쟁점은 같은 계보에 보존한다.

현재 구현은 별도 AI 범위 계획과 review-plan을 만들지 않고 고정 전면 배정을 사용한다. `reviewers` 수만큼 initial 자리를 바로 만들고 기본값은 2이며, 세 judge 자리도 제안 전문을 받는다. 역할 계약은 모든 initial 검토자와 judge가 논증 재구성·범위 반박·의미 동일성의 세 기본 관점으로 제안 전건을 대조하게 한다. 이 고정 배정은 범위 선택에서 일부 항목이 빠지는 경로를 줄이기 위한 수단 대체다.

전문 분야를 별도 자리로 자동 선정·배정하는 기능과 독립 범위 계획 기록은 없다. 검토자가 추가 전문성이 필요하다고 판단하면 `unresolved`, 고정 질문 보충 조사와 후속 질문으로 반환할 수 있다. 이 대체가 일반 수학 제안에서 동적 범위 계획과 같은 검토 강도·전문성·비용을 제공한다는 평가는 아직 없다. 현재 역할 schema에 존재하지 않는 review-plan을 출력하라고 요구하지 않는다.

최종 `match`, current formal source, active trust environment와 실제 dependency currentness가 있어야 현재 CLI가 K를 사용할 수 있다고 계산한다. K 편입과 목표 해결은 별도다. 목표 감사는 현재 goal basis의 독립 감사 전건을 집계하고 수학 목표는 사용할 K 없이 `mathematically_solved`가 될 수 없다.

학술 요구가 없으면 학술 후속은 `not_applicable`이다. 요구가 있으면 현재 solution basis와 요구 revision에 결박된 과제를 만들고 연구 계획이 각 criterion을 평가한다. 모든 요구가 satisfied이고 필수 외부 효과마다 같은 task·requirement·solution basis에 결박된 `confirmed`이면서 `succeeded=true`인 영수증이 있어야 academic validation이 `completed`다.

## 계획 이력과 현재 입력 범위

후보 준비와 연구 계획의 `recent_history`에는 이전에 종료한 `research_plan` 실행을 제공한다. 후보 준비에만 더하는 `preparation_history`에는 이전에 종료한 `research_preparation` 실행을 제공한다. 각 행은 `execution_id`, `role`, `outcome`, `error`, `action`을 가지며 결과 artifact가 있으면 `artifact_ref`, 실행 입력에 복원한 `local_path`, `sha256`, `bytes`를 함께 가진다. 활동 상태 필드는 이 이력 행에 넣지 않는다. 반려·실행 미완료·무산출도 제외하지 않는다.

이력과 다른 큰 입력은 `input/catalog/` 원문으로 바뀔 수 있으며 source reference에서 다시 읽는다. 최근 이력의 inline window가 작다는 사실은 과거 결과가 없다는 뜻이 아니다.

후보 준비와 연구 계획은 현재 goal·policies, 활성 config 전문, 자원과 실행 한도를 받는다. 입력 manifest와 `input/catalog/` 사본이 실제 제공한 판본·경로·해시를 고정한다. 다른 역할은 자기 판단에 필요한 설정 필드만 받고, 입력에 없는 설정값을 추측하지 않는다.

## 표현 방식과 보증 범위의 차이

현재 구현이 실제로 연결하고 검사한 범위는 다음과 같다.

- 기존 Codex 로그인으로 `codex exec`을 호출하고 실행별 prompt·schema·문서·입력·원 출력을 보존한다.
- 인스턴스별 Git ref와 writer lock으로 두 JSON 루트와 추가 전용 artifact를 순차 공개한다.
- 작업·운영 AI 실행 시도 수를 분리해 한쪽이 다른 쪽의 설정 한도를 자동 차용하지 않는다.
- source·지식 candidate·종류 정의·관계, goal·policy·grant·학술 요구, 신뢰 환경·대화와 외부 HTTP 제어를 현재 schema로 처리한다.
- 중앙 Lean·공리 검사, 현재 동일성 이의 왕복, 독립 목표 감사와 학술 요구·외부 효과 영수증을 연결한다.
- checkpoint·부분 파일·실패와 external unknown을 보존해 새 실행의 복구 근거로 연결한다.

GLOSSARY.md의 공통 개념과 현재 CLI의 표현 차이는 각각 다음처럼 해석한다.

- 연구 정본·실행 원장은 각각 두 JSON 루트의 내부 필드로 보존한다. 기록의 의미와 현재성을 판단할 때는 필드 내용과 후속 검사를 함께 확인한다. 지원하는 저장 형식은 이 문서의 `do-math-cli/1` 형식이며, 다른 계약 판본의 기록을 그대로 수입할 수 있다고 가정하지 않는다.
- 활동 상태는 `active/finished/unresolved`, 실행 상태는 `starting/running/ended`로 압축한다. queue action, stop request, 실행 outcome과 활동 result를 함께 읽어 보편 상태의 의미를 복원한다. 상태 문자열 하나만으로 생략된 전이를 추측하지 않는다.
- 연구 계획 후보 처분에는 `not_assessable` 전용 필드가 없다. 현재는 판정 불가 원인을 deferred reason·questions·준비 요청에 보존한다. 이 표현이 판정 불가와 전략적 보류를 기계적으로 구별하지 못하는 영향은 남는다.
- 동일성 검토는 독립 범위 계획 대신 전면 검토 고정 배정을 쓴다. 세 기본 관점을 역할 계약으로 요구하지만 전문 분야의 독립 자리 자동 선정은 없고, 동적 범위 계획과의 검토 강도 동등성은 미평가다.
- 작업 계약 검토의 현재 주 JSON은 판정과 findings에 항목별 판단을 서술한다. 정확한 계약·goal·policy basis는 실행기가 결합하지만, 항목별 승인 유효성의 근거를 별도 구조 필드로 표현하지 않는다. 의미 전건이 실제 findings에 보존되는지는 역할 결과와 검증에서 확인해야 한다.

현재 기본 Windows 실행은 `danger-full-access`와 승인 정책 `never`로 기존 사용자 권한을 사용한다. Windows Job은 로컬 프로세스 수명과 자손 종료를 관리한다. 이 조합은 모든 host 파일·network·credential 접근을 차단하는 격리가 아니다. 역할 경계는 고정 문서·선별 입력, 별도 session·workspace, 순차 배정과 같은 단계 동료 결과 비제공으로 운전하며 통계적 독립성이나 강한 OS 읽기 격리를 보증하지 않는다.

작업·운영 예산은 AI execution 시도 단위다. 실패·취소도 소비한다. Codex CLI가 반환한 turn usage를 보존하지만 공급자 내부 호출별 ID·예약·사용량·원격 종료를 관찰하지 않는다. 실행 수와 공급자 호출 수를 같다고 간주하지 않는다.

## 검증 근거의 해석

검증 증거는 실행 당시 코드·문서 판본과 사례 범위에 결박해 읽는다. 실행 명령과 입력, 실제 출력, 통과·실패·미실행 범위, 사용한 도구와 모델·신뢰 환경의 판본을 함께 보존한다. 과거 검증 기록이 현재 설치본의 검증을 대신하지 않는다.

스킬의 `scripts/tests/`는 회귀 검사를, `scripts/probe_codex.py`는 설치 문서·역할 스키마 검사와 실제 CLI 실행 검사를 제공한다. 설치 구조 검사 `--skill-only`와 모델을 호출하는 실제 검사는 보증 범위가 다르다. 실제 실행·중단·도구 호출은 해당 실행 증거에서, 수학적 결과는 형식 검사·동일성 판정·목표 감사에서 확인한다.

한 작은 수학 사례와 합성 fixture의 통과를 일반 연구 성능이나 수학 판단의 무오류성으로 확대하지 않는다. 현재 source를 검증하려면 안정된 사본에서 관련 테스트를 실행하고, 실제 Codex·Lean·HTTP·Windows 프로세스가 필요한 검사는 model-double 단위 검사와 구별한다.
