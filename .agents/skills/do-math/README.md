# do-math CLI 운영 안내

이 문서는 do-math 연구 인스턴스를 만들고 운전하는 사람을 위한 진입점이다. do-math의 목적과 전체 연구 흐름은 [SKILL.md](SKILL.md), 공통 용어의 뜻은 [GLOSSARY.md](GLOSSARY.md), 정확한 명령·필드·상태 투영과 역할별 JSON은 [CLI 실행 계약](references/CLI-실행-계약.md)이 소유한다.

현재 실행 계약은 `do-math-cli/1`이다. 새 세션 예산 인스턴스는 기능 판본 3을 사용하고, 기존 판본의 실행횟수 운전도 지원한다. 기존 Codex CLI 로그인을 사용하므로 별도의 OpenAI API 키를 요구하지 않는다. 이 구현은 수학 연구의 후보 준비, 작업 계약 검토, 연구 계획, 연구 수행, Lean 검사, 동일성 검토, 목표 감사와 학술 후속을 한 인스턴스 상태로 연결한다. 각 기능이 무엇을 보증하는지는 서로 다르다. 명령 성공이나 실행 종료는 형식 타당성·해설 동일성·목표 충족을 대신하지 않는다.

## 시작 전에 준비할 것

검증에 사용한 환경은 Python 3.12, Git, 로그인된 Codex CLI다. Python 의존성은 `requirements.txt`에 고정돼 있으며 현재 직접 의존성은 `jsonschema==4.26.0`이다.

```powershell
python -m pip install -r .agents/skills/do-math/requirements.txt
codex --version
git --version
python .agents/skills/do-math/scripts/do_math.py profile
```

`profile`은 설치된 Codex CLI의 명령 표면을 조사한다. 종료 코드 0과 `verified=true`는 그 조사 항목이 확인됐다는 뜻이다. 연구 역할의 품질, Lean 설치, 파일 격리나 원격 공급자 상태까지 보증하지 않는다.

연구를 시작하기 전에 다음 경로를 정한다.

- `--repository`: 인스턴스의 권위 있는 상태와 산출 묶음을 저장할 Git 저장소다. `--create-repository`를 쓰려면 경로가 없거나 빈 디렉터리여야 한다.
- `--workspace`: 실행별 작업 공간, 제어 inbox와 복구 자료를 둘 로컬 경로다. Git 정본과 다른 역할을 하며, 작업 공간 파일만으로 공용 기록이 되지는 않는다.
- `--goal` 또는 `--goal-file`: 연구 헌장의 현재 목표가 될 원문이다. 둘 중 하나만 사용한다.
- `--goal-kind`: `mathematical`은 형식 결과·동일성 판정·목표 감사를 요구하는 수학 목표이고, `research`는 헌장이 요구한 비형식 연구 산출로 충족될 수 있는 목표다.

초기화 때 정책, 원자료와 설정을 함께 넣을 수 있다. `--source`는 여러 번 지정할 수 있다. 모델별 배정과 예산은 설정 파일의 `tier_models`, `role_tiers`, `session_limits`를 사용한다. `--effort`는 설정 파일의 추론 노력보다 우선한다. 구 실행횟수 호환 모드의 `--model`도 같은 필드의 파일 설정보다 우선한다. 생략한 필드는 코드의 기본값을 사용한다.

독립 운영의 기본값은 `operator_enabled=true`, `operator_interval_seconds=7200`이다. 새 인스턴스는 상·중·하 모델마다 운영 3개와 작업 3개의 동시 세션을 사용한다. [모델과 실행예산](references/모델과-실행예산.md)의 기본 대응과 배정 기준을 확인하고, 다른 용량이나 수동 운영이 필요하면 설정 파일에 지정한다. `init`은 독립 운영이 활성일 때 연구 운전과 독립 운영 점검을 맡는 두 Windows 예약 작업을 등록하며, 그 자체로 모델이나 연구 실행을 시작하지는 않는다. 첫 정기 점검은 등록 후 설정한 주기에 도래한다. 주기 trigger는 운영 점검에만 적용한다. 연구 작업에는 고정 반복 주기를 두지 않고 운영 담당이 필요할 때 시작하며, 실행 기한으로 종료된 뒤의 재개도 다음 운영 점검에서 판단한다.

scholarly는 기본 활성이다. `scholarly_server`에 `command`·`args`를 직접 지정하거나, 초기화 명령의 작업 위치에서 상위로 찾은 `.codex/config.toml`의 scholarly 항목을 사용한다. 프로젝트 설정이 없으면 Codex 사용자 설정에서 같은 항목을 찾는다. 실행에 필요한 서버 경로는 고정해 인스턴스 설정에 보존하고, 하위 실행에는 이 MCP 설정만 명시적으로 전달한다. 서버 설정을 찾지 못한 것과 외부 자료원 접근 실패는 다르다. 사용 가능한 도구는 각 실행에서 확인한다.

## 모델과 동시실행 예산 설정

모델의 기본 대응과 배정 기준은 [모델과 실행예산](references/모델과-실행예산.md)에 있다. 아래 JSON을 설정 파일로 저장해 `init --config-file` 또는 `configure --config-file`에 전달하면 모델별 동시 세션 수를 명시할 수 있다. 과제의 난이도·중요도에 맞춘 모델의 슬롯이 없으면 그 과제는 대기한다.

```json
{
  "tier_models": {"high": "gpt-6-astra", "medium": "gpt-5.6-sol", "low": "gpt-5.6-terra"},
  "session_limits": {
    "work": {"gpt-6-astra": 3, "gpt-5.6-sol": 3, "gpt-5.6-terra": 3},
    "operations": {"gpt-6-astra": 3, "gpt-5.6-sol": 3, "gpt-5.6-terra": 3}
  }
}
```

이 예시는 기본 구성과 같다. 세션은 종료 후 재사용하며 두 예산은 자동 차용하지 않는다. 모델 이름이나 수를 바꾸면 두 예산 맵에도 해당 모델을 명시한다. 기존 실행횟수 인스턴스는 위 설정으로 명시적으로 전환하기 전까지 기존 계약을 유지한다. 기존 `role_models`를 썼다면 전환 설정에 `"role_models": {}`도 넣는다. 상세 호환 조건은 CLI 실행 계약의 설정 절을 따른다.

## 첫 인스턴스 만들기

아래 예시는 새 Git 저장소와 작업 공간을 만들고 수학 목표를 시작한다. PowerShell에서 현재 디렉터리는 저장소 루트라고 가정한다.

```powershell
python .agents/skills/do-math/scripts/do_math.py init `
  --create-repository `
  --repository .skill-workspace/my-math/repo `
  --workspace .skill-workspace/my-math/work `
  --goal-file .agents/skills/do-math/examples/nat-add-zero.txt `
  --title "자연수 덧셈의 오른쪽 항등원" `
  --goal-kind mathematical `
  --effort medium
```

성공 응답은 `instance_id`, 첫 `snapshot`, CLI `status`를 가진 JSON 객체다. 이후 명령에는 같은 `--repository`와 `--instance`를 사용한다.

```json
{"instance_id":"RI-...","snapshot":"<git-oid>","status":"ready"}
```

독립 운영을 등록했으면 응답의 `operator_schedule`에서 실제 두 작업을 확인한다. 저장은 성공했지만 예약 등록이 실패하면 생성된 인스턴스 ID·snapshot과 실패·재조정 명령을 반환한다. 같은 연구를 다시 `init`하지 말고 해당 인스턴스의 설치 문제를 해결한다.

여기서 CLI `ready`는 실행기가 다음 action을 처리할 수 있다는 구현 상태다. GLOSSARY의 보편 연구 인스턴스 상태를 새로 정의하지 않으며, 연구 목표가 준비됐거나 해결됐다는 뜻도 아니다.

초기화는 입력 goal과 policy를 저장하고, 등록된 지식·관계 종류와 로컬 역할 실행 grant를 현재 CLI 형식으로 만든 뒤 첫 후보 준비 action을 queue에 넣는다. 이 로컬 grant는 do-math 역할 실행을 위한 현재 구현 기록이며 외부 전송·공개·계정 작업의 허가가 아니다.

## 정상 운영

지속 연구는 다음 명령으로 별도 연구 예약 작업을 시작한다. 이 대화와 운영 담당이 끝나도 연구 프로세스는 자신의 예약 작업에서 계속된다. 즉시 운영 판단을 받으려면 `operator start-operator`로 별도 운영 작업을 시작한다.

```powershell
python .agents/skills/do-math/scripts/do_math.py operator start `
  --repository .skill-workspace/my-math/repo --instance RI-...
```

Windows 로그인, 켜져 있고 절전하지 않는 PC, 네트워크와 유효한 Codex 인증이 필요하다. 화면 잠금과 로그아웃은 다르다. 놓친 예약은 실행 가능한 상태에서 처리하도록 등록한다. 연구 실행의 내부 관찰·점검과 2시간마다 수행하는 전체 운영 점검은 별도로 유지된다.

### 1. 현재 상태를 읽는다

```powershell
python .agents/skills/do-math/scripts/do_math.py status `
  --repository .skill-workspace/my-math/repo `
  --instance RI-...
```

사람용 출력은 목표, 목표 상태, CLI 상태와 snapshot, 모델별 작업·운영 세션 점유, 과제 상태와 보증 범위 요지를 보여 준다. 자동 처리나 세부 진단에는 `--json`을 쓴다.

```powershell
python .agents/skills/do-math/scripts/do_math.py status `
  --repository .skill-workspace/my-math/repo `
  --instance RI-... `
  --json
```

JSON status에서 먼저 볼 필드는 다음과 같다.

| 필드 | 운영에서 읽는 뜻 |
|---|---|
| `snapshot` | 이번 상태가 고정된 Git commit OID |
| `status` | 실행 루프의 현재 CLI 상태 |
| `goal_status` | 현재 목표 감사 근거에 대한 CLI 목표 상태 |
| `pending_actions` | 실행기가 아직 처리하지 않은 action 수 |
| `tasks` | 과제 ID·제목·현재 CLI 단계 |
| `knowledge.K`, `knowledge.F`, `knowledge.suspended_K` | 현재 CLI가 계산한 사용 가능 K, `status!=verified` 기록, 사용 정지 K의 수. 여기서 `F` 수치는 보편 F의 완전한 의미 목록이 아니라 CLI 상태 집계다 |
| `questions` | 사용자 입력이나 결정을 기다리는 질문 |
| `budget` | 세션 모드의 작업·운영 모델별 한도·점유·여유 또는 구 모드의 실행횟수 한도·누적 사용 |
| `pending_controls` | inbox에 접수됐지만 아직 적용되지 않은 제어 수 |
| `user_pause` | 명시적 사용자 재개를 기다리는 정지의 요청 ID·이유·시각 |
| `waiting_actions` | 해소되지 않은 행동의 역할·대상·실패 종류·이유·실행 ID 요지 |
| `external_operations` | 외부 HTTP operation의 원장 상태 |
| `active_trust_environment` | 현재 CLI가 활성으로 기록한 신뢰 환경 ID |
| `academic_validation` | 현재 해결 근거와 학술 요구에 상대적인 후속 상태 |
| `assurance` | 읽기·공급자·사용량·형식·검토에 관해 실제 제공하는 보증의 범위 |

수량과 상태 문자열만으로 수학적 결론을 판단하지 않는다. 필요한 기록은 `query`와 `read`로 정확한 snapshot에서 확인한다.

### 2. 연구를 정해진 수만큼 전진시킨다

```powershell
python .agents/skills/do-math/scripts/do_math.py run `
  --repository .skill-workspace/my-math/repo `
  --instance RI-... `
  --max-steps 5
```

`--max-steps`는 이번 `run` 호출이 처리할 action 수의 상한이다. 수학 연구 단계나 모델 호출 수와 항상 같지는 않는다. 형식 검사·외부 행동 같은 기계 action도 한 step으로 처리될 수 있고, 하나의 AI 실행 안에서 Codex CLI가 수행한 내부 동작 수를 세지 않는다.

`--max-steps`를 생략하면 실행기는 queue와 현재 설정이 허용하는 동안 진행한다. `--watch`를 함께 쓰면 CLI 상태가 `waiting`이어도 `run_timeout_seconds`까지 제어 inbox, 대화 lease와 관찰 사건을 다시 확인한다. 사용자 결정을 자동으로 만들거나 waiting 과제의 조건을 임의로 해소하지 않는다.

```powershell
python .agents/skills/do-math/scripts/do_math.py run `
  --repository .skill-workspace/my-math/repo `
  --instance RI-... `
  --watch
```

### 3. 반환 상태를 다시 확인한다

`run`은 마지막 status JSON을 반환한다. 다음 경우에는 세부 기록을 읽고 다음 행동을 정한다.

- `ready`: 처리할 action이 남았거나 다음 `run`에서 계속할 수 있다.
- `waiting`: `questions`, 대기 과제 또는 외부 사건을 확인한다. 입력·결정 없이 같은 `run`을 반복해도 조건이 바뀌지 않는다.
- `capacity_waiting`: 배정된 모델의 세션 슬롯을 기다린다. 같은 인스턴스의 점유와 설정을 확인하고, 반환 뒤 `run` 또는 `run --watch`로 이어간다.
- `budget_exhausted`: 구 실행횟수 호환 모드에서 작업 또는 운영 실행 시도 한도에 닿았다. 실제 결과와 실패를 검토한 뒤 필요한 경우 `configure`로 명시적으로 한도를 바꾼다.
- `paused`: 사용자 정지, 실행기 복구, 설치 문서 변경 또는 실행 실패의 원인을 확인한다. `resume` 전에 `check`, status의 questions와 최근 실행 기록을 읽는다.
- `completed`: 현재 CLI가 목표와 적용되는 학술 요구의 완료 조건을 충족했다고 계산한 상태다. 정확한 목표 감사, K·해설·동일성 판정과 학술 근거를 별도로 읽는다.
- `closed`: 사용자가 인스턴스를 종결했다. `resume`으로 다시 열 수 없다.

## 입력과 결정을 제공하는 법

### 자유 형식 사용자 입력

새 연구 정보나 요청은 `input`으로 원문을 보존한다.

```powershell
python .agents/skills/do-math/scripts/do_math.py input `
  --repository .skill-workspace/my-math/repo `
  --instance RI-... `
  --text "보조정리 H의 가정이 실제 목표 범위와 같은지 다시 조사하세요."
```

긴 입력은 `--file`을 사용한다. 입력은 의도 해석과 독립 대조를 거쳐 현재 구현이 지원하는 내부 변경이나 다음 후보 준비에 연결된다. 자유 문장을 곧바로 권한이나 목표 변경으로 적용하지 않는다.

### 구조화된 사용자 결정

목표·정책·grant·과제 범위·학술 요구처럼 효과가 정해진 변경은 JSON 객체를 파일로 만든 뒤 `decision --file`로 보낸다.

```json
{
  "kind": "policy",
  "text": "사용한 문헌은 내부 보존 사본과 정확한 절 좌표를 남긴다.",
  "expected_revision": 1
}
```

```powershell
python .agents/skills/do-math/scripts/do_math.py decision `
  --repository .skill-workspace/my-math/repo `
  --instance RI-... `
  --file .skill-workspace/my-math/policy-decision.json
```

구조화 결정의 정확한 종류와 필드는 CLI 실행 계약에서 확인한다. `expected_revision`이 현재 판본과 다르거나 대상 상태가 이미 바뀌었다면 요청은 거부된다.

### 원자료 수입

```powershell
python .agents/skills/do-math/scripts/do_math.py source `
  --repository .skill-workspace/my-math/repo `
  --instance RI-... `
  --file C:\research\paper.pdf `
  --name paper.pdf
```

`source`는 접수 시점 바이트와 SHA-256을 제어 요청에 고정한 뒤 산출 묶음과 source record로 보존한다. 같은 이름·같은 해시는 변경 없음으로 처리한다. 같은 이름의 내용이 바뀌면 새 revision을 보존하고, 실제로 그 source에 의존한 지식·진행 중 실행과 과제의 현재성을 다시 평가한다.

같은 이름의 source가 바뀌어도 이미 `completed`인 과제의 상태와 완료 이력은 보존한다. 대신 그 과제의 `assessment.current`를 false로 바꾸고 `invalidated_reason`에 변경 근거를 남긴다. 단순 이력 조회는 완료 상태를 보존하지만, 다른 과제가 그 완료 판정을 실제 dependency로 사용하려면 현재성 검사를 통과해야 한다. 새 source 판본의 재검증은 완료 과제를 다시 여는 대신 후속 의무로 연결한다.

## 조회와 결과 회수

### 기록 조회

`query`는 지식, 관계, 과제, 활동, 실행, grant, 결정, 외부 operation, 검토 계보, 신뢰 환경, source와 종류 정의를 한 record 목록으로 조회한다.

```powershell
python .agents/skills/do-math/scripts/do_math.py query `
  --repository .skill-workspace/my-math/repo `
  --instance RI-... `
  --kind knowledge `
  --text "right identity" `
  --limit 50
```

`--related-to ID`는 관계의 이웃과 관계 기록을 찾는다. `--direction incoming|outgoing|both`로 방향을 구별한다. 결과의 `snapshot`, `total`, `loaded`, `truncated`, `next_cursor`를 함께 읽는다. 다음 페이지는 같은 query 조건과 `--cursor`를 사용하며 cursor가 고정한 snapshot을 바꾸지 않는다.

### 정확한 기록 읽기

```powershell
python .agents/skills/do-math/scripts/do_math.py read `
  --repository .skill-workspace/my-math/repo `
  --instance RI-... `
  --snapshot <git-oid> `
  --id KN-...
```

`--id`는 구조화 record를 JSON과 SHA-256으로 반환한다. `--path`는 snapshot 안의 파일 바이트를 읽는다. UTF-8이면 `text`, 아니면 `base64`로 반환한다. 큰 바이너리를 파일로 받으려면 `--output`을 지정한다.

### 파일 목록과 snapshot 내보내기

파일 자체를 찾으려면 `query --files`를 쓴다. 기본 prefix는 `research/`이고, prefix는 `research/` 또는 `runtime/` 아래의 `/`로 끝나는 POSIX 경로여야 한다.

```powershell
python .agents/skills/do-math/scripts/do_math.py query `
  --repository .skill-workspace/my-math/repo `
  --instance RI-... `
  --files `
  --prefix runtime/artifacts/ `
  --text formal.json
```

`export`는 기본적으로 한 snapshot의 `research/`만 새 경로나 빈 디렉터리로 복사한다. `--all`을 지정하면 `runtime/`도 포함한다.

```powershell
python .agents/skills/do-math/scripts/do_math.py export `
  --repository .skill-workspace/my-math/repo `
  --instance RI-... `
  --snapshot <git-oid> `
  --destination .skill-workspace/my-math/export
```

내보낸 파일은 조회 사본이며 새 정본이 아니다.

## 정지, 재개와 종결

```powershell
python .agents/skills/do-math/scripts/do_math.py pause `
  --repository .skill-workspace/my-math/repo `
  --instance RI-... `
  --reason "정책 변경 전 상태를 검토합니다."
```

제어 명령은 먼저 workspace의 inbox에 요청을 기록한다. 같은 인스턴스의 writer lock을 얻을 수 있으면 즉시 적용하고, 다른 실행기가 lock을 보유하면 `effect="pending engine processing"`, `lock="busy"`를 반환한다. 이 경우 현재 실행기나 다음 `run`이 요청을 적용한다.

실행 중 pause·close, grant 철회, 필수 입력·목표·정책의 현재성 변경 또는 기한 도래가 확인되면 실행기는 `stop-request.json`을 기록한다. 허용된 짧은 checkpoint 구간 뒤 로컬 Job의 종료를 확인하고 부분 산출과 체크포인트를 회수한다. 현재 구현이 관찰하지 못한 원격 종료와 공급자 내부 호출은 `unknown` 범위로 남는다.

```powershell
python .agents/skills/do-math/scripts/do_math.py check `
  --repository .skill-workspace/my-math/repo `
  --instance RI-...

python .agents/skills/do-math/scripts/do_math.py resume `
  --repository .skill-workspace/my-math/repo `
  --instance RI-... `
  --reason "검사 결과와 남은 범위를 확인했습니다."
```

`resume`은 `closed`와 `completed` 상태를 다시 열지 않는다. 거부된 출력이나 진단에서 대기로 남긴 실패 행동을 일반 재개로 실행 대기열에 되살리지 않는다. 먼저 원인을 고치고 운영 점검의 재시도나 현재 입력의 새 역할 요청으로 이어 간다. 새 실행은 필요한 결과·체크포인트를 재사용하되 과거의 잘못된 판정을 현재 상태로 복사하지 않는다.

`close`는 queue를 비우고 인스턴스를 종결한다. 진행 중 실행의 회수 기록은 남길 수 있지만 새 연구를 시작하지 않는다.

### 독립 운영의 설정과 정지

`operator status`는 실제 예약 작업을 조회한다. `operator install`은 현재 인스턴스 설정으로 등록을 다시 맞추고 `operator uninstall`은 그 인스턴스의 두 예약 작업만 제거한다. 운영 주기와 기한은 `configure`의 `operator_enabled`, `operator_interval_seconds`, `operator_timeout_seconds`, `operator_effort`로 바꾼다. 세션 모드의 모델은 `tier_models`와 `role_tiers.independent_operator`를 사용하고, 구 실행횟수 모드는 `operator_model`을 사용한다. 적용된 운영 설정 변경은 예약에 반영되며, 제어가 아직 대기 중이면 적용 뒤 설치를 재조정한다. 비활성화나 예약 제거가 이미 실행 중인 연구까지 정지했다는 뜻은 아니다.

사용자가 연구와 자동 운영을 함께 멈출 때는 `operator hold`를 쓴다. 이 명령은 고유 ID의 HOLD를 만들고 사용자 정지를 요청한다. `operator release`는 그 HOLD를 해제하며, 현재 사용자 정지가 정확히 같은 HOLD에서 왔을 때만 재개한다. 이후의 다른 사용자 정지는 그대로 유지한다.

독립 담당이 보내는 자동 제어는 `--origin operator`로 표시한다. 이 경로는 사용자 정지를 해제하거나 목표·정책·학술 요구·외부 행동·신뢰 판정을 만들지 못한다. 사용자 제어의 기본 출처는 `user`다. 출처 구별은 같은 사용자 권한에서의 운영 계약이며 보안 격리 장치는 아니다.

설치 검사에는 `operator probe`를 사용한다. 실제 Codex 실행으로 상태·기록을 읽고 scholarly의 자료원 목록만 확인하며, 연구와 예약 상태를 변경하지 않는다. 독립 운영 보고는 `<workspace>/operator/latest-report.json`, 연구 예약 실행의 결과는 같은 `operator/` 아래 실행별 로그에 보존된다. 내부 `operations_calls`와 별도 운영 담당의 CLI 사용량은 분리해 읽는다. 이 대화로 자동 알림이 전송되지는 않는다.

## 운영 제어 명령의 용도

| 명령 | 사용할 때 | 중요한 경계 |
|---|---|---|
| `configure --config-file` | 모델 대응·역할 등급·세션 한도, 시간, 검토·관찰·산출 한도를 바꿀 때 | 목표·정책·학술 요구·외부 허가는 설정이 아니다 |
| `request --role ...` | 지원하는 후보 준비·연구 계획·보충 조사·운영 점검·유지보수 action을 명시적으로 열 때 | 요청 생성은 모델 실행이나 결과 승인이 아니다 |
| `knowledge --file` | candidate·종류 정의·관계를 수입하거나 기존 지식을 개정·무효화할 때 | candidate 수입은 K 편입이 아니다 |
| `trust --file` | 신뢰 환경을 등록·전환·무효화할 때 | 전환 성공은 무관한 의미·의존 정지 원인을 해소하지 않는다 |
| `external --file` | grant에 결박된 HTTP 행동을 준비하거나 unknown을 대조하고 알려진 실패를 재시도할 때 | `confirmed`와 HTTP 성공 여부는 별도다 |
| `conversation --file` | 대화 연결 세대·lease·소실 정책을 기록할 때 | 대화 연결은 실행 권한이 아니다 |
| `check` | 저장·참조·상태 불변식과 보존 artifact 해시를 검사할 때 | 자연어 의미와 수학적 타당성을 새로 판정하지 않는다 |

구조화 JSON의 전체 형식과 예시는 CLI 실행 계약을 따른다.

## 오류와 반환 코드

모든 명령은 JSON을 반환하며 `status`만 `--json`이 없을 때 사람이 읽는 텍스트를 반환한다.

| 종료 코드 | 뜻 |
|---|---|
| `0` | 명령 처리가 끝났다. 제어 요청은 `effect`를 확인해야 하며 다른 수학·완료 판단을 뜻하지 않는다 |
| `1` | `check`가 결함을 찾았거나 `profile`이 요청한 표면을 확인하지 못했다 |
| `2` | 명령 인자, JSON, 대상 ID·상태 또는 요청 계약이 잘못됐다. 응답 `kind`는 `input_error`다 |
| `5` | Git 저장·저장소 작업, OS 또는 subprocess 도구 오류다. `run`이 다른 실행기가 보유한 writer lock을 얻지 못한 경우도 여기에 속하며, 이때는 그 실행기가 끝난 뒤 다시 실행한다. 응답 `kind`는 `tool_error`다. 제어 명령의 lock 경합은 오류가 아니라 exit 0과 `lock="busy"`로 반환한다 |

제어 명령은 구문이 맞아도 접수 뒤 전제가 바뀌면 exit 0과 `effect="rejected"`, `reason`을 반환할 수 있다. `accepted=true`는 inbox 접수를 뜻하고 적용·실행·성공과 다르다.

## 현재 지원 범위

현재 CLI는 인스턴스별 Git ref와 writer lock, 두 JSON 상태 루트와 불변 artifact, 모델별 슬롯 안의 병렬 AI 실행과 순차 결과 반영, Codex CLI 구조화 출력, Lean·공리 검사, 동일성 검토의 이의 왕복, 목표·학술 후속, source·지식·관계·신뢰·외부 HTTP·대화 제어를 구현한다.

새 인스턴스의 작업·운영 예산은 모델별 로컬 AI 실행의 동시 점유로 계산한다. 기존 실행횟수 모드는 명시적인 설정 전환 전까지 보존한다. Codex CLI가 보고한 turn usage는 보존하지만 공급자 내부 호출별 ID·예약·원격 종료를 보증하지 않는다. 현재 기본 Windows 실행은 `danger-full-access`와 승인 정책 `never`로 기존 사용자 권한을 쓴다. Windows Job은 로컬 프로세스 수명과 자손 종료를 관리하지만 모든 host 파일·network·credential 접근을 차단하지 않는다. 별도 세션·작업 공간과 동료 결과 비제공은 입력 경계를 만들지만 통계적 독립성이나 강한 OS 격리의 증거가 아니다.

## 설치본 검사

스킬 폴더 전체를 설치한 뒤 다음 명령으로 역할별 필수 문서와 출력 스키마를 확인한다. 경로는 실제 설치 위치에 맞춘다.

```powershell
python .agents/skills/do-math/scripts/probe_codex.py --skill-only
```

이 검사는 스킬 폴더 안의 문서와 코드만 읽으며 모델을 호출하지 않는다. `scope="installed_skill_structure"`, `status="verified"`는 역할 읽기 대응표의 문서와 운영 문서를 읽었고 역할 출력 스키마의 형식 검사를 통과했다는 뜻이다. 문서 내용의 정확성, 실행 환경이나 연구 성능까지 검증한 결과는 아니다. `--spec-only`는 같은 검사의 호환 별칭이다.

현재 코드의 회귀 검사는 unittest discovery로 `scripts/tests/test_*.py`를 수집해 실행한다. 일부 시험 파일은 직접 실행해도 시험을 시작하지 않으므로 파일별 종료 코드만으로 회귀 검사를 완료했다고 판단하지 않는다.

```powershell
python -m unittest discover -s .agents/skills/do-math/scripts/tests -p "test_*.py"
```

실제 Codex·Lean·HTTP·Windows 프로세스가 필요한 검사는 각 시험의 환경 조건과 실행 결과를 확인한다. 검증 결과는 검사한 판본, 사례, 통과·실패·미실행 범위와 함께 보존하고, 해석 기준은 [CLI 실행 계약](references/CLI-실행-계약.md)의 「검증 근거의 해석」을 따른다.
