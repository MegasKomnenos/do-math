# do-math 실행기

do-math는 기존 Codex CLI 로그인으로 수학 연구를 운전하고, Lean 형식 검사·다단계 동일성 검토·목표 감사·학술 후속을 Git 정본에 보존한다. 별도 OpenAI API 키를 요구하지 않는다. 현재 영속 계약은 `do-math-cli/1`, 기능 판본은 2다. 과거 `do-math-draft/*/9` wire 형식을 그대로 구현한다는 뜻은 아니다.

현재 동작의 정본은 [CLI 실행 계약](references/CLI-실행-계약.md)이다. 통합 설계 목적별 구현·검증 상태는 [기능 완료 대응](../../../docs/do-math/기능-완료-대응.md), 판본별 실제 증거는 [구현 진행](../../../docs/do-math/구현-진행.md)에서 확인한다.

## 준비와 시작

Python 3.12, Git, 로그인한 Codex CLI와 `requirements.txt`의 의존성이 필요하다. Lean은 `lean_command` 설정, PATH, 저장소의 portable Lean 순서로 찾는다. 실제 실행파일·버전·hash가 없는 결과는 활성 신뢰 환경에 결박하지 않는다.

```powershell
python .agents/skills/do-math/scripts/do_math.py init --create-repository `
  --repository .skill-workspace/my-math/repo `
  --workspace .skill-workspace/my-math/work `
  --goal-file .agents/skills/do-math/examples/nat-add-zero.txt `
  --model gpt-5.6-luna --effort low
```

반환된 `instance_id`로 `run`, `status`, `check`를 실행한다. `run --max-steps N`은 N개 action 뒤 상태를 보존한다. `run --watch`는 waiting 중에도 실행 기한까지 control·대화 lease·관찰 사건을 재확인한다. 비형식 산출 자체가 목표이면 `init --goal-kind research`를 사용한다.

## 명령

`profile`을 제외한 명령은 `--repository`와 `--instance`를 받는다. JSON 제어는 object 하나를 담은 `--file`을 사용한다. 구문·파일 오류는 exit 2다. 접수 뒤 전제가 바뀐 요청은 exit 0의 `effect="rejected"`와 이유로 소비되어 뒤 요청을 막지 않는다.

| 명령 | 현재 효과 |
|---|---|
| `pause`, `resume`, `close` | 정지·재개·종결 요청을 inbox에 기록하고 단일 writer가 적용한다 |
| `input --text/--file` | 사용자 원문을 보존하고 의도 해석과 후보 준비에 연결한다 |
| `configure --config-file` | 모델·예산·시간·검토·관찰 설정을 개정한다. 학술 요구는 `decision`으로 개정한다 |
| `request --role ...` | 준비·계획·보충 조사·운영 점검·유지보수 action을 모델 호출 없이 연다 |
| `decision --file` | 목표·정책·과제 범위·grant·학술 요구의 명시적 사용자 결정을 적용한다 |
| `source --file [--name]` | 접수 시점 raw bytes를 base64·SHA-256으로 고정한 뒤 Git artifact와 source record로 수입한다 |
| `knowledge --file` | 지식 개정·철회와 구조화 candidate·kind definition·relation 수입을 요청한다 |
| `trust --file` | 신뢰 환경 등록·전환·무효화를 요청한다 |
| `external --file` | HTTP grant에 결박된 외부 행동 준비, unknown 결과 대조, 알려진 실패의 명시적 재시도를 요청한다 |
| `conversation --file` | 대화 세대 attach·heartbeat·detach와 소실 정책을 기록한다 |
| `query`, `read`, `export` | 고정 snapshot의 기록·파일·관계를 조회하거나 새 디렉터리로 내보낸다 |
| `check` | 현재 정본의 관계·상태 불변식을 검사한다 |
| `profile` | 설치된 Codex CLI 명령 표면과 미확인 능력을 보고한다 |

예시 JSON:

```json
{"kind":"policy","text":"Use reproducible source coordinates","expected_revision":1}
```

```json
{"operation":"invalidate","id":"KN-...","reason":"The cited source was withdrawn"}
```

```json
{"operation":"attach","id":"conversation-1","generation":1,"disconnect_policy":"pause","lease_seconds":60}
```

Knowledge candidate는 수입만으로 K가 되지 않는다. 종류·참조·provenance를 검사해 `candidate`로 저장하고 Lean source가 있으면 formal check, 이어 전체 identity review를 수행한다. Custom knowledge·relation kind는 의미와 고정된 제약을 먼저 등록해야 한다. Research relation은 근거 있는 연결일 뿐 수학적 함의가 아니다. Mathematical relation은 정확한 edge와 범위의 `relation_claim`을 가진 proof record, 그 record의 유효한 formal 결과와 동일성 assessment에 결박되어야 한다.

## 실행 중 보존과 제어

각 AI 실행은 새 Codex 세션과 workspace를 사용한다. 입력은 `input/` 아래에 hash manifest로 고정한다. 큰 catalog와 history는 원문 파일을 보존한 채 prompt에는 정확한 source ref와 ready universe를 남긴다. Mandatory 입력 자체가 한도를 넘으면 실행하지 않고 overflow 원인과 크기를 기록한다.

작업자는 긴 작업 전과 상태 변경 뒤 `checkpoint.json`을 갱신할 수 있다. 실행기는 JSONL 사건·checkpoint·idle·사용자 observation rule을 관찰하고 필요한 operational review를 연다. Pause·close·권한 변경·기한 도래 시 `stop-request.json`으로 새 연구를 막고 Job 종료 장벽 뒤 workspace의 모델 작성 파일과 부분 산출을 회수한다.

실행기 재시작은 미종료 execution을 성공으로 추측하지 않는다. workspace 산출·checkpoint·외부 operation을 회수하고 원래 action을 recovery 근거와 함께 다시 연결한다. 실행 중 설치 code·역할 문서가 바뀌면 같은 실행을 계속하지 않고 pause하여 일관된 판본으로 재시작하게 한다.

## 검토·신뢰 환경·학술 후속

Lean이 통과한 제안은 initial reviewer 전건을 먼저 봉인한다. 이의가 있으면 organize가 쟁점을 정리하고 독립 judge 3명이 판정한다. 기각·미해결 쟁점은 원 slot의 answer와 같은 judge들의 재심으로 유한하게 이어진다. 동료의 같은 batch 결과는 전건이 봉인되기 전 공개하지 않는다. 최종 match와 exact formal source·환경 currentness가 함께 있어야 usable K가 된다.

신뢰 환경 무효화는 해당 환경의 K 사용을 정지하고 실제 의존 과제·목표 판단을 재평가한다. 새 환경 전환은 대상 K 전건을 같은 source와 basis에서 다시 검사한 뒤 활성화한다. 환경 원인만 해소하며 별도 semantic·dependency 정지는 자동 해제하지 않는다.

사용자가 academic requirements를 설정했다면 `mathematically_solved` 뒤에도 원고·재현·외부 검토 같은 현재 요구를 research plan이 평가한다. 모든 현재 요구가 충족되어야 academic validation이 completed다. 외부 거부는 별도 기록이며 Lean 결과를 자동 무효화하지 않는다.

학술 요구는 `decision --file`에 `kind="academic_requirements"`와 requirements 배열을 전달한다. 각 요구는 id·scope·criteria·assessor="research_plan"을 가지며, 추가 required_inputs와 external_effects를 지정할 수 있다. 외부 효과는 id·scope·선택적 grant_id로 정의한다. 그 효과의 실제 성공 원장이 같은 과제·요구 판본·해결 근거에 결박돼야 학술 완료가 가능하다.

## 외부 행동과 격리 한계

외부 HTTP 행동은 활성 grant의 origin·method·path·credential 이름에 결박한다. Prepared→running을 먼저 저장한 뒤 전송하고 confirmed·failed·unknown을 구별한다. Unknown은 사용자나 adapter 근거로 대조하기 전 재전송하지 않는다. 같은 operation ID는 같은 요청 identity를 유지한다.

`external`의 `operation="retry"`는 id와 같은 grant_id를 지정한다. 알려진 failed·cancelled만 대상이며 전송 가능성이 있으면 grant의 allow_idempotent_retry가 필요하다. 요청·멱등 키는 유지하고 새 실행과 이전 결과를 기록한다. Unknown은 먼저 `operation="reconcile"`에서 evidence와 result를 명시한다. HTTP 응답 없이 성공을 확인했다면 result="confirmed"와 succeeded=true를 함께 제공해야 하며, confirmed라는 값만으로 성공을 추측하지 않는다.

Windows Job은 로컬 프로세스 수명과 자손 종료를 소유한다. 현재 Windows 운전은 `--sandbox danger-full-access --ask-for-approval never`로 기존 사용자 권한을 사용한다. 이 환경의 elevated 모드는 설정 도우미 오류 1223, unelevated workspace-write는 실제 작업 폴더 쓰기 거부가 확인됐다. 로컬 권한 모드에서는 지정 폴더의 실제 쓰기·읽기를 검증했다. 실행기는 절대 workspace 경로를 전달하며 도구 호출에 명시적 workdir와 절대 파일 경로를 사용하게 한다.

이 선택은 강한 host 파일·network·credential 격리를 제공하지 않는다. 현재 역할 경계는 순차 배정, 선별 입력, 별도 세션·workspace와 동료 결과 비제공으로 운전한다. 공급자 내부 호출별 ID와 원격 종료도 관찰 가능한 로컬 Job 종료와 구별한다.

## 검증 증거의 범위

증거는 판본별로 읽는다.

- `docs/do-math/구현-검증-2026-09-14/cli-workflow/`: 초기 CLI1 판본의 실제 9 AI 실행·1 formal 실행, Lean 5사례와 양화 순서 의미 반례다.
- 같은 날짜의 과거 회귀 보고: 당시 코드의 97개 검사다. 최신 feature2 전체의 검증 수로 사용하지 않는다.
- 현재 `scripts/tests/`: feature2 lifecycle·review·context·knowledge·academic·external·trust 기능의 단위 및 model-double 검사다.
- [Feature 2 전체 흐름](../../../docs/do-math/구현-검증-2026-09-14/feature2/workflow/report.json): 실제 CLI 18회와 Lean 1회로 수학적 해결과 재현 설명의 학술 요구까지 완료했다.
- [Feature 2 의미 검토](../../../docs/do-math/구현-검증-2026-09-14/feature2/semantic/README.md): 이의 왕복의 실제 CLI 8회와 양화 순서 오류의 실제 초기 검토 2회를 구별해 보존한다.
- [Feature 2 회귀](../../../docs/do-math/구현-검증-2026-09-14/feature2/regression/README.md): 전체 261건 중 260건 통과·1건 환경상 skip, 마지막 변경 관련 45건 통과를 정확한 소스와 연결한다.

```powershell
python -m unittest discover -s .claude/skills/do-math/scripts/tests -p "test_*.py" -v
```

실행 중 canonical source가 바뀌면 installation currentness gate가 의도적으로 pause할 수 있으므로 안정된 판본에서 최종 결과를 기록한다. 실제 adapter probe와 native 격리 진단은 각각 `probe_codex.py`, `probe_native_isolation.py`를 사용한다. Probe의 `passed`는 그 입력 사례만 뜻하며 전체 구현 완료를 뜻하지 않는다.
