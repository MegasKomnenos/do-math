---
유형: 기각보관
출처: do-math-opus55
라운드: 1
항목: 34
---

# 기각 보관 — do-math-opus55 라운드1

## R1-17

### 원문
제목: `goal_kind`의 `research` 예약 입력과 내부 잔재를 유지할지 결정이 필요하다

### 위치
- 공개 입력면: `.claude/skills/do-math/scripts/do_math/cli.py` 96행이 `choices=("mathematical", "research")`를 선언하고, 277~278행이 `research`를 `unsupported`로 거부한다. `.claude/skills/do-math/references/CLI-실행-계약.md` 223행과 237행, `.claude/skills/do-math/README.md` 45행은 이 예약 상태를 적는다.
- 내부 수용: `.claude/skills/do-math/scripts/do_math/engine.py` 206~207행(`initialize`)과 `.claude/skills/do-math/scripts/do_math/initialization.py` 287행(`initialize_state`)이 `research`를 받는다. `.claude/skills/do-math/scripts/do_math/record_schemas/schemas.py` 223행은 `goal_kind: enum("mathematical", "research")`를 둔다.
- 도달 불가 분기: `.claude/skills/do-math/scripts/do_math/governance.py` 160행 `governance_view`는 `goal_kind`를 항상 `"mathematical"`로 낸다. 그래서 `.claude/skills/do-math/scripts/do_math/engine.py` 4370~4371행과 `.claude/skills/do-math/scripts/do_math/governance_engine.py` 420~421행의 `goal_kind != 'mathematical'` 검사는 참이 될 수 없다. `.claude/skills/do-math/scripts/do_math/governance.py` 171행은 `goal_status`를 `unsolved`·`mathematically_solved`로 제한한다. 그러므로 `.claude/skills/do-math/scripts/do_math/lifecycle_engine.py` 611행 집합의 `'research_goal_satisfied'`는 저장 상태에 나타날 수 없다.
- 역할 계약: `.claude/skills/do-math/계약/목표-감사.md` 9행의 `goal_kind=research` 잔존 입력 처리 문장.
- 시험: `scripts/tests/test_engine.py` 216~228행, `scripts/tests/test_observation_admission.py` 136행, `scripts/tests/test_walkthrough_contract_repairs.py` 22~38행, `scripts/tests/test_lifecycle_engine.py` 892행이 `goal_kind='research'`를 구성한다.

### 기준
`.claude/skills/do-math/AGENTS.md` 5행:

```
- 설계를 바꾸면 구현·호출부·스키마·테스트·예시·문서를 같은 변경에서 새 계약으로 교체한다. 구판 호환을 위한 이전 구현·이름 별칭·래퍼·구형 인자·무시되는 설정·버전별 분기·마이그레이션 경로를 남기지 않는다.
```

`.claude/skills/do-math/AGENTS.md` 9행:

```
- 사용자가 구체적인 대상과 기간을 지정해 호환성을 명시적으로 요구한 경우에만 예외를 둔다. 미래 사용자나 이전 기록의 존재를 추측해서 호환 계층을 만들지 않는다.
```

`.claude/skills/do-math/README.md` 45행 (현행 존치 문언):

```
- `--goal-kind`: 현재 지원하는 진입값은 `mathematical`이다. 형식 결과·동일성 판정·목표 감사를 거쳐 `mathematically_solved`를 판단한다. `research` 진입값은 현재 `unsupported`로 거부하며 저장소·작업 공간·예약 작업을 만들지 않는다. 관련 내부 분기와 기록은 후속 작업을 위해 유지한다. 수학 목표 안의 문헌 조사·계산·비형식 과제는 계속 사용할 수 있다.
```

### 영향
`research`로 시작하는 공개 경로는 없다. 그런데 Python 진입점 `engine.initialize`와 `initialize_state`는 `research`를 받아 입력 기록의 `config.goal_kind`에 남긴다. 반면 `governance_view`와 그것을 읽는 모든 역할 문맥은 목표 종류를 늘 `mathematical`로 본다. 두 입력면이 서로 다른 목표 종류를 말하고, 최종 보증 쪽의 비수학 분기 둘과 `research_goal_satisfied` 상태값은 도달하지 않는다. 목표 감사 역할은 9행 때문에 현행 입력에 없는 `goal_kind=research`를 대비한 판단 규칙을 읽는다.

README 45행은 이 잔재를 "후속 작업을 위해 유지한다"고 적는다. 이 문언이 사용자의 명시적 존치 결정인지, 그리고 AGENTS.md 9행이 말하는 "구체적인 대상과 기간"을 갖춘 예외인지는 산출물만으로 확정할 수 없다. 그래서 수리 결과가 사용자 의도에 따라 갈린다.

### 상신
#### 읽은 범위

지급 밖에서 연 파일과 자리는 다음과 같다.
- `.claude/skills/do-math/README.md` 45행
- `.claude/skills/do-math/references/CLI-실행-계약.md` 223행, 237행, 627행, 633행
- `.claude/skills/do-math/scripts/do_math/cli.py` 96행, 277~289행
- `.claude/skills/do-math/scripts/do_math/initialization.py` 283~308행
- `.claude/skills/do-math/scripts/do_math/governance.py` 138행, 155~171행
- `.claude/skills/do-math/scripts/do_math/governance_engine.py` 416~423행
- `.claude/skills/do-math/scripts/do_math/record_schemas/schemas.py` 223행
- `.claude/skills/do-math/scripts/do_math/record_schemas/domains.py` 16행
- `.claude/skills/do-math/계약/목표-감사.md` 7~9행
- `.claude/skills/do-math/계약/후보-준비.md` 43행
- `.claude/skills/do-math/계약/연구-계획.md` 23행
- `기억/layer1/M-0327.md`: `goal_kind` 언급을 확인했다. `research` 존치 결정은 담고 있지 않다.

개체 `goal_kind`의 정의는 `schemas.py` 223행과 `governance.py` 160행에서, 정본 문서는 README 45행과 CLI-실행-계약 237행에서 열었다. 결정 기록으로는 README 45행의 존치 문언만 찾았다. `기억/` 그래프에서 이를 세운 별도 결정 노드는 찾지 못했다.

#### 세계 물음

이용자는 `init --goal-kind`로 연구 목표의 종류를 고른다. 운영자와 목표 감사 AI는 역할 문맥의 `goal_kind`로 최종 보증 경로를 판단한다. 비수학 연구 목표를 받아들이려면 그 목표의 최종 보증 상태와 판정 경로가 정의되어 있어야 한다. 정의 파일에는 그 개체가 없다. `governance.py` 171행은 `goal_status`를 `unsolved`·`mathematically_solved`로 닫고, `governance_view`는 목표 종류를 `mathematical`로 고정한다. 목표 감사 계약 9행도 비형식 최종 보증 경로를 만들지 않는다고 적는다. 현재 세계에서 `research` 목표로 할 수 있는 일은 없다.

#### 선택지

A. `research`를 전부 제거한다.
- cli.py의 `choices`를 `("mathematical",)`로 줄이고 277~278행의 수동 거부를 지운다. argparse와 cli.py 528~529행의 JSON 요청 스키마가 같은 선택지로 거부한다.
- `engine.initialize`·`initialize_state`는 `mathematical`만 받는다. `schemas.py` 223행의 열거값도 `mathematical` 하나로 줄인다.
- `engine.py` 4370~4371행과 `governance_engine.py` 420~421행의 도달 불가 검사, `lifecycle_engine.py` 611행의 `'research_goal_satisfied'`를 지운다.
- 목표-감사 9행의 잔존 입력 문장을 지우고, README 45행과 CLI-실행-계약 223·237행을 현행 단일 값으로 고친다.
- `research`를 구성하는 네 시험은 수학 목표로 바꾸거나, 폐기 기능만 검사하면 제거한다.

하류 영향: 목표 종류가 공개·내부·문서에서 하나로 맞춰지고 도달 불가 분기가 사라진다. 나중에 비수학 목표를 도입하면 그때 새 계약으로 설계한다.

B. README 45행대로 현 상태를 유지한다.

하류 영향: 공개 입력면은 거부하고 내부 입력면은 수용하는 불일치가 남는다. 도달 불가 분기와 상태값, 역할 계약의 대비 문장도 계속 유지 비용을 만든다. AGENTS.md 5·9행과의 긴장도 남는다.

C. A의 변형이다. 내부 잔재는 A처럼 모두 지우되, CLI 오류문과 README·CLI-실행-계약의 한 문장으로 "`research`는 지원하지 않는다"는 안내만 남긴다.

하류 영향: 내부 계약은 A와 같다. 공개 문서에는 지원하지 않는 값을 알리는 안내 한 줄이 남는다.

#### 변형 물음

A의 대가는 README가 적은 "후속 작업"을 위한 코드 자리가 사라지는 것이다. 이 대가는 C로 줄어든다. C는 사용자가 기대할 만한 입력값을 문서로 안내하면서 내부 호환 계층은 두지 않는다. B의 대가인 입력면 불일치와 도달 불가 분기를 없애는 변형은 결국 A나 C가 된다.

#### 추천 하나

A를 추천한다. 세 선택지를 승인한 뒤의 최종 상태를 비교하면, A는 목표 종류가 모든 입력면·저장 스키마·역할 계약에서 `mathematical` 하나인 상태다. 지원하지 않는 값은 argparse와 JSON 스키마가 표준 오류로 거부한다. B는 결함을 남긴 채 예약 구조를 유지하며, 그것을 요구하는 독립 소비자나 기간이 명시된 호환 요구를 산출물에서 찾지 못했다. C는 A와 내부 상태가 같지만, 표준 선택지 오류가 이미 전달하는 정보를 별도 안내문으로 한 번 더 유지한다.


### 판정
확정: 기각 · 승인기 [1] · 기각기 [2, 3] · 처분: 없음
최종 판정: 기각

### 근거
- 기 2: 항목 종류 대조에서 성립하지 않는다. README의 존치 문장이 사용자 확정 기록이라는 근거는 제시되지 않았고, 이번 동결문의 제거 지시는 명시적이다. 지원하지 않는 종류의 잔재를 제거하는 데 새로운 사용자 의도나 외부 사정이 필요하다고 볼 수 없다. A와 C의 안내 문구 차이도 현재 지원 계약에 대한 별도 사용자 결정을 필수로 만들지 않는다. 산출물 파일만 고쳐 닫을 수 있는 문제를 상신 제안으로 냈으므로 기각한다.
- 기 3: 관문 적용 전 항목 종류가 맞지 않는다. README의 작성 주체를 확정할 수 없다는 사정만으로 새 사용자 선택의 필요성이 서지 않는다. 제시된 A는 산출물 파일만 고쳐 현재 기준을 충족하는 수리다. 미래 기능 유지 여부를 다시 묻기보다 동결된 제거 방향에 맞는 조각 항목이어야 한다.

## R1-42

### 원문
제목: README와 CLI 실행 계약의 종료 코드 5 설명이 contract_error와 예약 등록 실패 반환을 빠뜨렸다

### 위치
`.claude/skills/do-math/README.md` 384행(「오류와 반환 코드」 표의 `5` 행)과 `.claude/skills/do-math/references/CLI-실행-계약.md` 28행(「종료 코드」 표의 `5` 행).

### 기준
```
2. 생산자와 소비자 사이의 계약 미스매치를 수리한다. 구현·호출부·스키마·시험·예시·문서가 같은 현재 계약을 사용하게 한다.
```
(임시/do-math_검증_20260924_opus55/동결.md 239행, 목적 진술 2)

### 영향
README는 exit 5를 도구 오류로만 설명하고 "응답 `kind`는 `tool_error`다"라고 단정한다. 실제 CLI는 exit 5를 두 경우에 더 쓴다. 첫째, `TypeError`·`KeyError`·`RuntimeError`를 `kind="contract_error"`, `next_owner="maintenance"`로 돌려준다(cli.py 653~662행). 둘째, `init`·`configure`가 상태는 저장했으나 예약 등록에 실패하면 `error`가 아닌 `result`에 `operator_schedule.status="failed"`를 담아 exit 5로 돌려준다(cli.py 263~266행, 295행, 325행). `--describe`도 `'error_exit_codes':{'input_error':2,'tool_error':5,'contract_error':5}`를 공표한다(cli.py 558행). README만 읽은 운전자는 두 경우를 Git·OS 오류로 오인해 운영 담당에게 넘기거나 같은 명령을 반복한다. 실제로 필요한 것은 각각 유지보수로 넘기는 일과 예약 재조정이다. README 5행은 정확한 명령·필드의 정본이 CLI 실행 계약이라고 정한다. 그런데 그 문서의 종료 코드 표(28행)도 exit 5를 "도구 계층 실패, `kind=tool_error`"로만 적는다. 같은 문서 30행은 "성공 값은 `result`, 오류의 `kind`·`message`·후속 정보는 `error`"라고 적어, exit 5와 함께 `result`가 오는 예약 실패 반환을 설명하지 못한다. README만 고치면 정본 문서와 README가 서로 어긋나므로 두 표를 같은 사실로 고친다. 확인 경로: graphify `affected "README.md"`와 `affected "references/CLI-실행-계약.md"`가 두 문서의 상호 참조(「문서별 책임」, 「운영 제어 명령의 경계」)를 반환했고, 이를 따라 `rg "tool_error|contract_error"`로 두 표를 대조했다.

### 조각 1 — .claude/skills/do-math/README.md 384~384행
원래:
```
| `5` | Git 저장·저장소 작업, OS 또는 subprocess 도구 오류다. `run`이 다른 실행기가 보유한 writer lock을 얻지 못한 경우도 여기에 속하며, 이때는 그 실행기가 끝난 뒤 다시 실행한다. 응답 `kind`는 `tool_error`다. 제어 명령의 lock 경합은 오류가 아니라 exit 0과 `lock="busy"`로 반환한다 |
```
대체:
```
| `5` | Git 저장·저장소 작업, OS 또는 subprocess 도구 오류이면 응답 `kind`는 `tool_error`다. `run`이 다른 실행기가 보유한 writer lock을 얻지 못한 경우도 여기에 속하며, 이때는 그 실행기가 끝난 뒤 다시 실행한다. 제어 명령의 lock 경합은 오류가 아니라 exit 0과 `lock="busy"`로 반환한다. 구현이 요청을 처리하지 못한 내부 계약 오류이면 `kind`는 `contract_error`이고 `next_owner`는 `maintenance`다. `init`·`configure`가 상태를 저장했으나 예약 등록에 실패한 경우에도 exit 5이며, 이때는 `result.operator_schedule`에 `status="failed"`와 그대로 실행할 재조정 명령이 들어 있다 |
```

### 조각 2 — .claude/skills/do-math/references/CLI-실행-계약.md 28~28행
원래:
```
| `5` | Git 저장, OS, subprocess 같은 도구 계층이 실패했다. 응답 `kind=tool_error` |
```
대체:
```
| `5` | Git 저장, OS, subprocess 같은 도구 계층이 실패했으면 응답 `kind=tool_error`다. 구현이 요청을 처리하지 못한 내부 계약 오류이면 `kind=contract_error`, `next_owner=maintenance`다. `init`·`configure`가 상태를 저장한 뒤 예약 등록에 실패한 경우에도 exit 5이며, 이때는 `error` 대신 `result.operator_schedule`에 `status="failed"`와 재조정 명령이 담긴다 |
```


### 판정
확정: 기각 · 승인기 [1, 2] · 기각기 [3] · 처분: 없음
최종 판정: 기각

### 근거
- 기 3: 관문 4를 통과하지 못한다. README 대체 문면은 현재 반환값을 “그대로 실행할 재조정 명령”이라고 새로 단정한다. 이 항목의 두 문서 조각만으로는 현재 실행 불가능한 인자열이 고쳐지지 않는다. 별도 항목의 적용을 전제하지 않는 문면이어야 하며, 다른 수리의 승인을 근거로 이 단정을 승인할 수 없다.

## R1-50

### 원문
제목: 중단된 유지보수 정리의 실패 기록은 어떤 후속 삭제로도 해소되지 않아 점검을 영구히 degraded로 만든다

### 위치
`.claude/skills/do-math/scripts/do_math/retention.py` 242~246행(`pending_cleanup_failures`의 `maintenance_cleanup_failed` 처리). 실패 사건 생산자는 `.claude/skills/do-math/scripts/do_math/engine.py` 2425~2426행이다. 시험은 `.claude/skills/do-math/scripts/tests/test_redesign_SURFACE.py` 256~259행.

### 기준
```
5. 절차와 스크립트 안팎에서 발견한 다른 문제도 실제 근거에 따라 해결한다.
```
(임시/do-math_검증_20260924_opus55/동결.md 242행, 목적 진술 5)

```
2. 생산자와 소비자 사이의 계약 미스매치를 수리한다. 구현·호출부·스키마·시험·예시·문서가 같은 현재 계약을 사용하게 한다.
```
(임시/do-math_검증_20260924_opus55/동결.md 239행, 목적 진술 2)

### 영향
`_maintenance_cleanup`이 예외로 중단되면 실행기는 경로 없이 `{"kind": "maintenance_cleanup_failed", "execution_id", "reason", "next_owner"}`를 이력에 남긴다(engine.py 2425~2426행). `pending_cleanup_failures`는 이 사건을 `runtime/history/<index>` 키로 등록하는데, 이 키를 지우는 곳은 없다. 경로 실패는 `result.deleted`의 같은 경로가 지운다(250~251행). 그러나 사건 참조는 삭제 경로와 결코 같지 않으므로 이 등록은 영원히 남는다. 이 함수의 설명문("Only deletion of that exact path establishes cleanup completion")은 해소 수단이 정확한 경로의 삭제라고 정한다. 그런데 경로 없는 사건에는 그 수단이 없다. `state_checks.py` 254~257행은 이 목록의 각 항목을 `degraded` 결함으로 올리고, `reporting.snapshot_report`는 이를 `cleanup_failures`로 보여 준다. 따라서 일시적 잠금·권한 오류로 정리가 한 번 중단되면 운전자가 같은 범위를 다시 정리해 파일을 모두 지워도 `check`가 계속 exit 1을 반환한다. 사용자 승인 정리 범위는 action의 `cleanup_execution_ids`와 정확히 같으므로(`_cleanup_scope`, engine.py 4014~4026행), 실패 사건에 그 경로를 담으면 경로별 삭제로 해소할 수 있다. 확인 경로: `rg "maintenance_cleanup_failed"`로 생산자 하나(engine.py 2425행), 소비자 하나(retention.py 242행), 시험 하나(test_redesign_SURFACE.py 256행)를 찾았다. 수리 뒤 사건은 늘 `paths`를 가지므로 경로 없는 형태는 현행 계약이 아니다.

### 조각 1 — .claude/skills/do-math/scripts/do_math/retention.py 242~246행
원래:
```
        if event.get('kind') == 'maintenance_cleanup_failed':
            reference = 'runtime/history/' + str(index)
            pending[reference] = {'path': None, 'error': event.get('reason'), 'status': 'degraded',
                'next_owner': 'maintenance', 'execution_id': event.get('execution_id'), 'evidence_ref': reference}
            continue
```
대체:
```
        if event.get('kind') == 'maintenance_cleanup_failed':
            # An aborted attempt names its approved run paths. Only a later
            # deletion of each exact path completes that path.
            for path in event['paths']:
                pending[path] = {'path': path, 'error': event.get('reason'), 'status': 'degraded',
                    'next_owner': 'maintenance', 'execution_id': event.get('execution_id'),
                    'evidence_ref': 'runtime/history/' + str(index)}
            continue
```

### 조각 2 — .claude/skills/do-math/scripts/do_math/engine.py 2425~2426행
원래:
```
                self.runtime["history"].append({"kind": "maintenance_cleanup_failed", "execution_id": execution_id,
                    "reason": str(error), "next_owner": "maintenance"})
```
대체:
```
                self.runtime["history"].append({"kind": "maintenance_cleanup_failed", "execution_id": execution_id,
                    "paths": ["runs/" + identifier for identifier in action["cleanup_execution_ids"]],
                    "reason": str(error), "next_owner": "maintenance"})
```

### 조각 3 — .claude/skills/do-math/scripts/tests/test_redesign_SURFACE.py 256~259행
원래:
```
        runtime['history'] = [{'kind':'maintenance_cleanup_failed','execution_id':'EX-maint',
                              'reason':'root inaccessible','next_owner':'maintenance'}]
        result=inspect_state(instance,runtime,requested_areas=['record_storage'])
        self.assertEqual(result['status'],'degraded')
```
대체:
```
        runtime['history'] = [{'kind':'maintenance_cleanup_failed','execution_id':'EX-maint',
                              'paths':['runs/EX-1'],'reason':'root inaccessible','next_owner':'maintenance'}]
        result=inspect_state(instance,runtime,requested_areas=['record_storage'])
        self.assertEqual(result['status'],'degraded')
        self.assertTrue(any('runs/EX-1' in str(row) for row in result['findings']))
        runtime['history'].append({'kind':'maintenance_cleanup','execution_id':'EX-maint-2',
            'result':{'status':'healthy','deleted':['runs/EX-1'],'failures':[]}})
        self.assertEqual(inspect_state(instance,runtime,requested_areas=['record_storage'])['status'],'healthy')
```


### 판정
확정: 기각 · 승인기 [] · 기각기 [1, 2, 3] · 처분: 없음
최종 판정: 기각

### 근거
- 기 1: 관문 3·4 미통과. 대체는 예외 시점이나 이미 완료한 삭제와 무관하게 승인 범위 전건을 새 실패로 등록한다. 삭제 성공 이력이 먼저 있고 마지막 저장에서 예외가 난 경우, 그 성공 이력 뒤에 이미 삭제된 경로가 다시 pending으로 올라간다. 이후에는 디렉터리가 없어 같은 경로의 성공 삭제를 만들 수 없다. 따라서 영향 칸의 영구 degraded 손상이 남거나 이미 해소된 경로로 옮겨 간다. 제안 시험은 아직 존재하는 단일 경로의 가상 후속 삭제만 넣어 이 경우를 다루지 않는다.
- 기 2: 관문 3·4를 통과하지 못한다. 제안은 바깥 예외가 난 위치와 무관하게 승인 범위의 모든 경로를 새 실패로 등록한다. 실제 삭제와 성공 이력 추가 뒤 마지막 저장에서 예외가 나면, 성공 이력의 삭제가 앞서 해소한 경로를 뒤의 실패 사건이 다시 미해소로 만든다. 그 디렉터리는 이미 없으므로 후속 정리에서 다시 삭제할 수 없다. 영향 칸이 주장한 영구 degraded 손상이 이 경로에 남으며, 이미 완료한 경로까지 미완료로 분류한다. 추가 시험은 실패 뒤 정상 삭제의 경우만 다뤄 이 경로를 해결하지 않는다.
- 기 3: 관문 3을 통과하지 못한다. 실제 삭제와 maintenance_cleanup 이력 추가까지 끝난 뒤 마지막 저장이 예외로 중단되면, 대체 문면은 이미 삭제된 경로도 뒤의 실패 사건에서 다시 pending으로 등록한다. 다음 정리에서 존재하지 않는 경로의 rmtree는 성공한 삭제를 만들지 못하므로 그 실패가 다시 영구히 남을 수 있다. 승인 범위와 실제 미완료 경로를 동일시하여 영향 칸의 영구 degraded 손상을 없애지 못한다.

## R1-52

### 원문
제목: init의 --goal-kind research는 받자마자 거부되는데 선택지·내부 분기·저장 열거가 후속 작업용으로 남아 있다

### 위치
- `.claude/skills/do-math/scripts/do_math/cli.py` 96~97행(`choices=("mathematical", "research")`)과 277~278행(거부)
- `.claude/skills/do-math/scripts/do_math/initialization.py` 287~288행(`{"mathematical", "research"}` 허용)
- `.claude/skills/do-math/scripts/do_math/engine.py` 4370~4371행, `.claude/skills/do-math/scripts/do_math/governance_engine.py` 420~421행(`goal_kind != "mathematical"` 분기)
- `.claude/skills/do-math/scripts/do_math/record_schemas/schemas.py` 223행(`goal_kind` 열거)
- `.claude/skills/do-math/README.md` 45행("관련 내부 분기와 기록은 후속 작업을 위해 유지한다")
- `.claude/skills/do-math/scripts/tests/test_connection_repairs.py` 251행(`goal_kind='research'` fixture)

### 기준
```
미래 사용자나 이전 기록의 존재를 추측해서 호환 계층을 만들지 않는다.
```
(.claude/skills/do-math/AGENTS.md 9행)

```
사용자가 구체적인 대상과 기간을 지정해 호환성을 명시적으로 요구한 경우에만 예외를 둔다.
```
(.claude/skills/do-math/AGENTS.md 9행)

```
1. 더 이상 활용되지 않는 호환성 요소, 죽은 패러미터, 무시되는 설정과 유사한 잔재를 제거한다. 현재 입력의 유효성·권한·근거·현재성 검사는 유지한다.
```
(임시/do-math_검증_20260924_opus55/동결.md 238행, 목적 진술 1)

### 영향
`research`는 argparse 선택지로 받아들여지지만 `execute`가 곧바로 입력 오류로 돌려보낸다. 따라서 이 인자값은 죽은 패러미터다. 통치 보기는 `goal_kind`를 늘 `"mathematical"`로 고정한다(governance.py 160행). 그러므로 engine.py 4370행과 governance_engine.py 420행의 `!= "mathematical"` 분기는 도달할 수 없다. 저장 스키마의 `goal_kind` 열거는 `record_schemas/domains.py` 16~17행이 `RESEARCH_FIELDS`에서 제거하므로 저장되지도 않는다. 결국 `research`를 받아들이는 곳은 `initialize_state`와 그것을 직접 부르는 시험 fixture 하나뿐이다. README 45행은 이 잔재를 "후속 작업을 위해 유지한다"고 적는다. 이 문장을 추가한 커밋(`7d2597e`)과 기억 그래프에서 사용자가 대상·기간을 정해 예외를 지시한 기록은 찾지 못했다. 이 잔재를 지울지, 사용자 예외로 확정할지는 사용자의 향후 계획에 달렸다. 방치하면 운전자는 `--goal-kind`에 지원 예정 값이 있다고 읽고, 유지보수자는 도달할 수 없는 분기를 유지 대상으로 취급한다.

### 상신
#### 읽은 범위

- 정의: cli.py 88~101행·276~296행, initialization.py 283~314행, record_schemas/schemas.py 221~232행, record_schemas/domains.py 13~17행, governance.py 154~164행
- 정본 문서: README.md 41~46행, 79~104행
- 결정: `git log -S"후속 작업을 위해 유지한다"`로 찾은 커밋 `7d2597e`(README에 이 문장을 추가한 판본 5 커밋). `기억/` 전체 검색(`goal-kind`, `goal_kind`, `후속 작업을 위해`)에서는 M-0327만 나왔고, 그 노드는 `goal_kind=mathematical` 조건의 후보 준비 규칙을 다룰 뿐 research 유지 결정을 담지 않는다. research 유지를 지시한 사용자 확정 기록은 열지 못했다. 찾은 기록 안에는 없다.
- 소비처: engine.py 1773행·4340행·4369~4371행, governance_engine.py 413~421행, test_connection_repairs.py 243~266행

#### 세계 물음

이 산출물이 그리는 세계에서 행위자는 인스턴스를 만드는 운전자다. 운전자는 `init --goal-kind`로 목표 종류를 고른다. `research` 목표를 실제로 수행할 개체는 정의 파일에 없다. 저장 필드(`goal_kind`)는 저장 스키마에서 제거되고, 통치 보기는 언제나 `mathematical`을 낸다. research 목표의 완료 조건·감사 경로도 정의돼 있지 않다. 따라서 현재 세계에서 `research`를 고르는 행위는 거부 말고 다른 결과를 낳지 않는다.

#### 선택지

- A. 잔재를 모두 지운다. `--goal-kind` 선택지를 `mathematical` 하나로 줄이거나 옵션 자체를 없앤다. `initialize_state`의 허용 집합, engine.py·governance_engine.py의 도달 불가 분기, schemas.py의 `research` 열거값, README 45행의 유지 문장, 시험 fixture의 `goal_kind='research'`를 함께 고친다. 하류 영향: 역할 문맥의 `goal_kind` 필드와 후보 준비 계약의 `goal_kind=mathematical` 조건은 그대로 유지된다. research 목표를 설계할 때 CLI 선택지와 분기를 새 계약으로 다시 만든다.
- B. 사용자가 대상(research 목표 종류)과 기간을 지정한 예외로 확정한다. 코드는 두고, README 45행에 예외의 근거·대상·기간을 명시한다. 하류 영향: 도달 불가 분기와 죽은 선택지가 유지되며, 유지보수 때마다 이 예외의 만료 여부를 확인해야 한다.
- C. research 목표를 실제로 지원한다. 완료 조건·감사·통치 보기를 설계한다. 하류 영향: 이번 검증 범위를 넘어서는 새 기능 설계다.

#### 변형 물음

A의 대가는 나중에 research를 설계할 때 선택지를 다시 추가하는 일이다. 이 대가는 새 계약을 만들 때 어차피 치르는 비용이므로 줄일 필요가 작다. B의 대가는 죽은 코드의 상시 유지다. 예외 기간이 끝나면 A로 넘어가도록 만료 시각을 기록하는 변형으로 그 대가를 줄일 수 있다. C의 대가는 설계 전체다. 이번 범위에서는 줄일 변형이 없다.

#### 추천 하나

A. 최종 상태를 비교하면 A는 지원 범위와 코드·문서가 일치하고, 거부되는 값이 CLI 표면에 남지 않는다. B의 대체 구조(도달 불가 분기)를 유지해야 할 독립 소비자·호환 계약·이행 제약은 찾지 못했다. 옵션 자체를 없앨지, 선택지 하나로 남길지는 README 예시(90행 `--goal-kind mathematical`)와 함께 정한다. 목표 종류를 명시하는 표면을 유지하려면 선택지 하나로 남기는 편이 문서 수정이 작다.


### 판정
확정: 기각 · 승인기 [1] · 기각기 [2, 3] · 처분: 없음
최종 판정: 기각

### 근거
- 기 2: 항목 종류 대조에서 성립하지 않는다. 상신 이유가 미래 지원 계획 또는 존치 문언이 사용자 예외일 가능성인데, 그 예외를 확정한 지급 기록은 없다. 현재 확정된 제거 지시와 프리알파 원칙으로 잔재를 정리할 수 있다. 미래 기능을 새로 설계하는 C는 이 결함 수리의 필수 대안이 아니고, 옵션을 단일 값으로 둘지의 구현 선택도 현재 지원 범위를 바꾸지 않는다. 산출물 안에서 닫히는 문제를 상신 제안으로 제출했으므로 기각한다.
- 기 3: 관문 적용 전 항목 종류가 맞지 않는다. 확인되지 않은 미래 예외를 새로 만들지 여부는 현재 결함 수리에 필요한 결정이 아니다. 문서에 남은 존치 설명을 이번 확정 방향에 맞춰 고칠 수 있고, 제시된 A도 산출물 안에서 닫힌다. 현행 단일 값을 유지하는 조각 항목으로 작성할 수 있으므로 상신 필요성이 성립하지 않는다.

## R1-53

### 원문
제목: 외부 operation 재시도의 권한 규칙이 문서·저장 스키마와 실제 실행기 사이에서 갈라졌다

### 위치
- `.claude/skills/do-math/references/CLI-실행-계약.md` 561행(retry 규칙)과 370행(HTTP grant 예시의 `"allow_idempotent_retry":true`)
- `.claude/skills/do-math/scripts/do_math/record_schemas/schemas.py` 166행(`"allow_idempotent_retry": BOOL`)
- `.claude/skills/do-math/scripts/do_math/lifecycle_engine.py` 745~790행(retry 소비자)
- `.claude/skills/do-math/scripts/do_math/external.py` 149~160행(`prepare_retry`)
- `.claude/skills/do-math/scripts/tests/test_external.py` 46행(fixture grant의 `'allow_idempotent_retry':True`), 89~95행

### 기준
```
2. 생산자와 소비자 사이의 계약 미스매치를 수리한다. 구현·호출부·스키마·시험·예시·문서가 같은 현재 계약을 사용하게 한다.
```
(임시/do-math_검증_20260924_opus55/동결.md 239행, 목적 진술 2)

```
1. 더 이상 활용되지 않는 호환성 요소, 죽은 패러미터, 무시되는 설정과 유사한 잔재를 제거한다. 현재 입력의 유효성·권한·근거·현재성 검사는 유지한다.
```
(임시/do-math_검증_20260924_opus55/동결.md 238행, 목적 진술 1)

### 영향
문서 561행은 세 가지를 요구한다. retry는 `failed`·`cancelled`만 받는다. 전송 가능성이 있었으면 grant의 `allow_idempotent_retry=true`가 필요하다. `unknown`은 먼저 reconcile해야 한다. 실행기는 다르게 동작한다. `unknown`도 직접 retry할 수 있다(lifecycle_engine.py 750행, external.py 150행). 그때 사용자가 낸 `verified_idempotency` 증거(요청 해시·idempotency key·만료 전 `valid_until`)가 필요하다(external.py 156~157행). `failed`는 `effect_absent` 증거로, 전송 전 `cancelled`는 증거 없이 retry할 수 있다(lifecycle_engine.py 758~767행). grant의 `allow_idempotent_retry`는 저장 스키마가 받고 문서·시험 fixture가 쓰지만, `rg`로 확인하면 그 값을 읽는 코드가 없다. 무시되는 설정이다. 운전자는 문서대로 grant에 이 값을 넣으면 재시도 위험이 grant 단위로 통제된다고 믿는다. 실제로는 값과 무관하게 사용자 증거만으로 재시도가 열린다. 반대로 문서만 따르면 unknown 재시도를 못 한다고 판단해, 가능한 복구를 하지 않는다. 어느 쪽을 현재 계약으로 삼을지는 외부 효과 재시도에 대한 사용자의 위험 허용도에 달렸다.

### 상신
#### 읽은 범위

- 정의: external.py 1~183행 전체, record_schemas/schemas.py 160~170행
- 정본 문서: CLI-실행-계약.md 355~379행, 530~561행
- 소비처: lifecycle_engine.py 690~790행, governance.py 502~515행(`_dispose_grant_consumers`), test_external.py 1~110행 전체
- 결정: `기억/` 전체 검색(`allow_idempotent_retry`, `verified_idempotency`)에서 결과가 없었다. 이 규칙을 정한 사용자 확정 기록은 찾지 못했다.

#### 세계 물음

행위자는 외부 HTTP 행동을 허가한 사용자와, 결과가 불명확한 operation을 다시 보내려는 운전자다. 재시도에 필요한 개체는 셋이다. 첫째, operation 원장의 상태·전송 표지(`transmitted`, `transmission_phase`)다. 둘째, 사용자가 제출하는 요청 결박 증거(`effect_absent`, `verified_idempotency`)다. 셋째, grant다. 첫째와 둘째는 정의 파일에 있고 실행기가 검사한다. grant의 `allow_idempotent_retry`는 정의(스키마)에는 있으나 소비자가 없다.

#### 선택지

- A. 실행기를 현재 계약으로 삼는다. 저장 스키마·문서 예시·시험 fixture에서 `allow_idempotent_retry`를 지운다. 561행은 실제 규칙으로 다시 쓴다. unknown은 `verified_idempotency` 증거로, failed는 `effect_absent` 증거로, 전송 전 cancelled는 증거 없이 재시도하며, 식별자 유지와 이력 추가는 그대로다. 하류 영향: 재시도 권한은 매번의 사용자 retry 제어와 증거가 맡는다.
- B. 문서를 현재 계약으로 삼는다. 전송 가능성이 있었던 operation의 retry에서 grant의 `allow_idempotent_retry=true`를 검사하고, `unknown` 직접 retry를 금지해 reconcile을 먼저 요구한다. 하류 영향: `test_retries_need_exact_nonexpired_idempotency_evidence` 등 unknown 재시도 시험과 `prepare_retry`의 unknown 허용을 바꾼다. 멱등성 증거로 unknown을 복구하는 경로가 사라진다.
- C. 실행기 규칙은 유지하면서, 전송 가능성이 있었던 재시도(`verified_idempotency` 경로)에는 grant의 `allow_idempotent_retry=true`를 추가로 요구한다. 하류 영향: grant 설계 시점의 사전 허가와 재시도 시점의 사용자 증거를 둘 다 요구한다. lifecycle_engine.py retry 분기에 검사 하나를 더하고 문서를 두 요건으로 고친다.

#### 변형 물음

B의 대가는 unknown operation 복구 경로의 상실이다. 이 대가를 없애는 변형이 C다. C는 unknown 복구를 유지하면서 grant 수준 통제를 되살린다. C의 대가는 같은 사용자가 두 번 허가하는 중복이다. retry 제어 자체가 사용자 출처(`source='user'`)이므로, grant 플래그를 생략하는 변형이 곧 A다.

#### 추천 하나

A. 모든 선택지를 승인한 뒤의 최종 상태를 비교하면, A는 재시도 권한이 retry 시점의 사용자 제어와 요청 결박 증거 한 곳에 모이고, 무시되는 설정이 사라진다. C가 더하는 grant 플래그는 retry 제어가 이미 사용자 결정이라는 점에서 권한을 새로 좁히지 못한다. 이 플래그를 유지해야 할 독립 소비자·호환 계약·이행 제약도 찾지 못했다. 다만 grant 설계 시점에 외부 효과의 재전송 자체를 금지하려는 사용자라면 C가 그 의도를 담는다.


### 판정
확정: 기각 · 승인기 [2] · 기각기 [1, 3] · 처분: 없음
최종 판정: 기각

### 근거
- 기 1: 관문 8 미통과. 추천은 C가 추가하는 grant 조건이 사용자 retry 제어 때문에 권한을 새로 좁히지 못한다고 주장한다. 그러나 동일한 사용자 retry와 유효 증거가 있어도 기존 grant의 플래그가 false 또는 누락이면 C는 거부하고 A는 허용한다. 두 최종 상태는 사전 승인 범위의 구속력에서 다르다. 추천 끝에서도 C가 사전 재전송 금지 의도를 담는다고 인정해 앞 근거와 모순된다. 이 차이를 중복 허가로 없애 버린 비교로는 외부 효과 위험에 대한 선택을 올릴 수 없다.
- 기 3: 관문 8을 통과하지 못한다. C를 채택하면 사용자 retry 제어와 유효한 멱등 증거가 있어도 grant 플래그가 false인 경우 거부하므로 A와 허용 행동이 실제로 다르다. 같은 사용자의 제어라는 이유로 이 사전 제약의 효과가 없어지는 것은 아니다. 또한 A의 “failed는 effect_absent 증거로”라는 최종 상태 설명은 현재 구현의 failed에 대한 verified_idempotency 경로를 빠뜨린다. 권한 선택 자체는 상신 사안이지만, 추천의 최종 상태 비교가 정확하지 않다.

## R1-81

### 원문
제목: `init --goal-kind research`는 예약만 된 진입값이며 내부 분기가 도달 불가능하거나 서로 어긋난다

### 위치
- 공개 표면: .claude/skills/do-math/scripts/do_math/cli.py 96~97행(`choices=("mathematical", "research")`), 277~278행(거부), .claude/skills/do-math/README.md 45행("관련 내부 분기와 기록은 후속 작업을 위해 유지한다"), .claude/skills/do-math/references/CLI-실행-계약.md 223행, 237행
- 내부 수용: .claude/skills/do-math/scripts/do_math/engine.py 206~207행, .claude/skills/do-math/scripts/do_math/initialization.py 287~288행
- 도달 불가 분기: .claude/skills/do-math/scripts/do_math/engine.py 4370~4371행, .claude/skills/do-math/scripts/do_math/governance_engine.py 420~421행
- 시험: .claude/skills/do-math/scripts/tests/test_walkthrough_contract_repairs.py 22~36행

### 기준
```
- 사용자가 구체적인 대상과 기간을 지정해 호환성을 명시적으로 요구한 경우에만 예외를 둔다. 미래 사용자나 이전 기록의 존재를 추측해서 호환 계층을 만들지 않는다.
```
.claude/skills/do-math/AGENTS.md 9행

```
1. 더 이상 활용되지 않는 호환성 요소, 죽은 패러미터, 무시되는 설정과 유사한 잔재를 제거한다. 현재 입력의 유효성·권한·근거·현재성 검사는 유지한다.
```
임시/do-math_검증_20260924_opus55/동결.md 238행(목적 진술)

### 영향
`governance_view`는 활성 헌장만으로 연구 관점을 만들고, `goal_kind`를 언제나 `"mathematical"`로 반환한다(governance.py 160행). `validate_governance_state`는 인스턴스에 `goal_kind`가 있으면 거부한다(governance.py 169~170행). 최종 목표 상태도 `unsolved`와 `mathematically_solved` 둘만 허용한다(171행).

그래서 engine.py 4370행과 governance_engine.py 420행의 `goal_kind != "mathematical"` 분기는 도달할 수 없다. 반면 공개 CLI는 `research`를 선택지로 보여 준 뒤 거부한다. 내부 `initialize`와 `initialize_state`는 `research`를 받아 초기 control 기록에 `goal_kind: "research"`로 남긴다(initialization.py 308행). 그 인스턴스의 통치 관점은 `mathematical`로 보고되므로, 한 인스턴스 안에서 기록과 관점이 어긋난다.

운영자에게는 쓸 수 없는 선택지가 `--describe` 스키마와 도움말에 계속 노출된다. 유지보수자는 비형식 목표 경로가 부분적으로 살아 있다고 오인한다. 한편 README 45행은 이 잔재를 "후속 작업을 위해 유지"한다고 명시한다. 이것은 예약 진입값을 둘지에 관한 설계 결정이므로, 제거 여부는 산출물만으로 정할 수 없다.

### 상신
#### 읽은 범위

- 정의 파일: .claude/skills/do-math/scripts/do_math/governance.py 130~172행(`governance_view`, `validate_governance_state`), engine.py 204~218행·4362~4376행, governance_engine.py 414~424행, initialization.py 283~310행, record_schemas/schemas.py 219~229행, record_schemas/domains.py 13~17행
- 정본 문서의 절: README.md 45행, references/CLI-실행-계약.md 223행·237행, 계약/목표-감사.md 7~9행, 계약/연구-계획.md 23행, 계약/후보-준비.md 43행
- 결정 파일: docs/do-math/구현자-결정과-변명.md 455행(구현 당시 "`goal_kind=research`의 비형식 목표 경로도 지원"이라고 적은 구현자 기록). 기억 노드 M-0327. 도입 커밋 7d2597e("do-math 기능 판본 5와 정적 검토 수리·근거를 보존"). 이 사본들에서 `research` 진입값을 후속 작업용으로 남기라는 사용자 결정 문면은 찾지 못했다.
- 시험: tests/test_walkthrough_contract_repairs.py 22~36행

#### 세계 물음

do-math의 세계에서 운영자는 `init`으로 연구 목표를 세우고, AI 역할들은 헌장과 목표 감사로 목표 충족을 판정한다. `research` 목표를 운전하려면 비형식 목표의 완료 판정 개체가 있어야 한다. 예를 들면 `mathematically_solved`에 대응하는 최종 상태, 목표 감사의 비형식 판정 규칙, `governance_view`의 목표 종류 보존이다. 정의 파일에는 이 개체가 없다. 최종 상태는 두 값으로 닫혀 있고(governance.py 171행), 목표 감사는 수학 목표 계약만 따르며(계약/목표-감사.md 9행), `governance_view`는 종류를 고정한다. 따라서 현행 세계에서 운영자가 `research`로 할 수 있는 일은 거부를 받는 것뿐이다.

#### 선택지

- A. `research` 진입값과 목표 종류 입력을 모두 제거한다. cli.py 96~97행의 `--goal-kind` 인자, 277~278행, 289행의 전달, engine.py `initialize`와 initialization.py `initialize_state`의 `goal_kind` 매개변수와 `{"mathematical", "research"}` 검사를 없앤다. 초기 control 기록의 `goal_kind`는 `"mathematical"` 고정값으로 남기거나 지운다. engine.py 4370~4371행과 governance_engine.py 420~421행의 도달 불가 분기, README.md 45행과 90행 예시의 `--goal-kind mathematical`, CLI-실행-계약.md 223·237행, test_walkthrough_contract_repairs.py의 unsupported 시험을 새 계약에 맞춘다. 하류 영향: 공개 CLI 인자가 하나 줄어든다. 역할 context의 `goal_kind`(`governance_view` 값 `mathematical`)는 계약 문서들이 읽으므로 유지한다.
- B. 공개 인자 `--goal-kind`는 두되 선택지를 `mathematical` 하나로 줄이고, 내부 `research` 수용과 도달 불가 분기를 제거한다. 하류 영향: 기록과 관점의 불일치는 사라진다. 그러나 값이 하나뿐인 인자가 남으므로 죽은 인자 문제는 형태만 바뀐다.
- C. 현행대로 예약 진입값을 유지하되, 내부 `initialize`와 `initialize_state`도 `research`를 거부하게 해서 기록·관점 불일치만 없앤다. 하류 영향: README 45행의 결정은 보존된다. 도달 불가 분기와 노출된 선택지는 남는다.

#### 변형 물음

A의 대가는 공개 CLI 인자 제거다. 이 대가를 줄이는 변형이 B다. B는 인자를 남기되 유효값을 하나로 닫는다. C의 대가는 도달 불가 분기의 존속이다. 이를 줄이는 변형은 C에 engine.py 4370~4371행과 governance_engine.py 420~421행 분기 제거를 더하는 것이다. 다만 그 경우 A와의 차이는 CLI 표면과 문서뿐이다.

#### 추천 하나

A. 프리알파 원칙은 미래 사용자나 기능을 추측해 계층을 남기지 않는다고 정한다(AGENTS.md 9행). 비형식 목표 경로에는 완료 판정 개체가 전혀 없으므로, 후속 작업이 열리면 그때 계약·스키마·CLI를 함께 새로 설계해야 한다. 지금 남긴 선택지와 분기는 그 설계를 돕지 않고 현행 독해만 흐린다. B는 값이 하나뿐인 인자를 남겨 같은 종류의 결함을 유지한다. C는 README의 결정을 존중하지만 도달 불가 코드를 보존한다. A를 승인한 뒤의 최종 상태가 가장 단순하고, 통치 관점(`mathematical` 고정)과 입력 표면이 일치한다.


### 판정
확정: 기각 · 승인기 [] · 기각기 [1, 2, 3] · 처분: 없음
최종 판정: 기각

### 근거
- 기 1: 항목 종류 대조에서 사용자 결정의 필요성이 성립하지 않는다. README의 현행 설명과 상위 기준의 충돌 자체를 사용자 확정 문면의 충돌로 취급했지만, 그 예약을 사용자가 확정했다는 지급 기록은 없다. B·C가 남기는 잔재는 항목 자체도 현행 기준 위반으로 설명한다. 조각으로 현행 기준에 맞출 수 있는 결함을 상신 제안으로 제출했으므로 기각한다.
- 기 2: 관문 적용 전 항목 종류 대조에 실패한다. 사용자 확정으로 확인되지 않은 README의 예약 문장을 새 사용자 결정이 필요한 이유로 삼았다. 지원하지 않는 입력과 죽은 분기를 현재 수학 목표 계약에 맞춰 제거하는 방향은 동결문에서 이미 정해져 있다. B·C는 항목 자체가 지적한 죽은 입력 또는 분기를 남기므로, 현행 정본을 충족하는 비동등한 결과가 둘 이상이라는 근거도 되지 못한다. 산출물 안의 구현·호출부·문서를 함께 고치는 조각으로 제출해야 한다.
- 기 3: 관문 적용 전 항목 종류가 성립하지 않는다. 상신 근거는 산출물에 예약 보존 문장이 있다는 사실뿐이며, 이를 사용자 확정 문면으로 뒷받침하는 기록은 제시하지 않았다. 현재 사용자 지시와 기준 원문이 이미 미사용 진입값·분기 제거 방향을 정한다. 제시한 B·C도 잔재를 남기는 결함을 스스로 인정하므로 현행 정본에 맞는 비동등한 대안이라는 근거가 되지 않는다. 산출물의 코드·문서·시험을 함께 고칠 조각 항목으로 닫을 수 있다.

## R1-95

### 원문
제목: 지원하지 않는 `goal_kind=research`와 `research_goal_satisfied`가 초기화·목표 감사·목표 상태 전이에 잔재로 남아 있다

### 위치
`research`는 입력으로 받아들여지지만 실제로는 버려진다. 그 값을 받는 자리는 다음과 같다.

`.claude/skills/do-math/scripts/do_math/engine.py` 206~207행(`initialize`)과 `.claude/skills/do-math/scripts/do_math/initialization.py` 287~288행(`initialize_state`)이 `goal_kind`로 `research`를 받아들인다.

같은 값을 다루는 분기 가운데 실행될 수 없는 것은 다음과 같다.

`.claude/skills/do-math/scripts/do_math/governance_engine.py` 420~421행과 `.claude/skills/do-math/scripts/do_math/engine.py` 4370~4371행은 `goal_kind != 'mathematical'`을 거부하는 분기다. `.claude/skills/do-math/scripts/do_math/lifecycle_engine.py` 611행은 목표 상태 `research_goal_satisfied`를 되돌리는 분기다.

역할 계약이 존재하지 않는 입력을 다루도록 지시하는 자리도 있다. `.claude/skills/do-math/계약/목표-감사.md` 9행의 마지막 두 문장이 그렇다.

예약을 선언한 문서는 `.claude/skills/do-math/README.md` 45행, `.claude/skills/do-math/references/CLI-실행-계약.md` 223행, 237행이다. CLI 진입부는 `.claude/skills/do-math/scripts/do_math/cli.py` 96행, 277~278행이다.

`research`를 쓰는 시험은 여섯 곳이다. `scripts/tests/test_engine.py` 216~228행, `scripts/tests/test_connection_repairs.py` 251행, `scripts/tests/test_lifecycle_engine.py` 892행, `scripts/tests/test_observation_admission.py` 21행, `scripts/tests/test_session_scheduler.py` 467행, `scripts/tests/test_walkthrough_contract_repairs.py` 33행이다.

### 기준
```
- 설계를 바꾸면 구현·호출부·스키마·테스트·예시·문서를 같은 변경에서 새 계약으로 교체한다. 구판 호환을 위한 이전 구현·이름 별칭·래퍼·구형 인자·무시되는 설정·버전별 분기·마이그레이션 경로를 남기지 않는다.
```

출처: `.claude/skills/do-math/AGENTS.md` 5행.

```
- 사용자가 구체적인 대상과 기간을 지정해 호환성을 명시적으로 요구한 경우에만 예외를 둔다. 미래 사용자나 이전 기록의 존재를 추측해서 호환 계층을 만들지 않는다.
```

출처: `.claude/skills/do-math/AGENTS.md` 9행.

```
- 권한·입력·참조·증거·현재성 검사는 현행 계약에 맞게 유지한다. 조용한 기본값 보충으로 오류를 숨기지 않는다.
```

출처: `임시/do-math_검증_20260924_opus55/동결.md` 「불변식 목록」 260행.

### 영향
`governance.py` 160행의 `governance_view`는 헌장이 채택된 뒤 `goal_kind`를 언제나 `"mathematical"`로 돌려준다. 같은 파일 170~171행의 `validate_governance_state`는 목표 상태로 `unsolved`와 `mathematically_solved`만 허용한다. `academic.py` 243행의 `apply_goal_assurance`는 그 밖의 최종 보증을 거부한다. 이 사실에서 네 가지 결과가 나온다.

첫째, 사용자 설정이 조용히 바뀐다. CLI는 `research`를 거부한다(`cli.py` 277~278행). 하지만 Python 진입점 `engine.initialize`와 `initialization.initialize_state`는 이 값을 받아 최초 입력의 `config.goal_kind`에 저장한다. 초기화 동안 `_governance`(engine.py 500~510행)는 이 값을 의도 해석 입력에 그대로 넘긴다. 헌장이 채택되면 모든 역할은 `mathematical`을 받는다. 연구 책임자가 준 값이 어떤 기록이나 오류도 없이 다른 값으로 바뀌는 것이다.

둘째, 목표 감사 계약이 도착할 수 없는 입력을 다룬다. `계약/목표-감사.md` 9행은 감사자에게 "입력에 `goal_kind=research`가 남아 있어도 … 지원 계약과 배정의 불일치를 반환"하라고 지시하고, 존재하지 않는 목표 상태 `research_goal_satisfied`를 언급한다. 목표 감사는 헌장 채택 뒤에만 배정되므로 이 입력은 오지 않는다. 감사자는 불가능한 분기를 판단 절차의 일부로 읽게 된다.

셋째, 거부 분기가 실행될 수 없다. `governance_engine.py` 420~421행과 `engine.py` 4370~4371행은 목표 감사와 계획의 목표 감사 요청에서 비수학 목표를 거부한다. 그러나 조건이 언제나 거짓이다.

넷째, 되돌릴 대상이 없는 상태 이름이 남아 있다. `lifecycle_engine.py` 611행은 판정 근거를 잃었을 때 `research_goal_satisfied`도 `unsolved`로 되돌린다. 그런데 이 상태는 상태 검증이 금지하므로 존재할 수 없다.

반면 `README.md` 45행과 `references/CLI-실행-계약.md` 237행은 이 분기와 기록을 "후속 작업을 위해 유지"한다고 선언한다. 산출물 안의 문서가 기준 원문의 금지와 반대 방향의 결정을 적고 있으므로, 어느 쪽으로 수리할지는 사용자 결정이 필요하다.

### 상신
#### 읽은 범위

지급 밖에서 연 자료는 네 가지다.

첫째, 루트 `AGENTS.md` 전문과 `.claude/skills/do-math/AGENTS.md` 전문이다.

둘째, `기억/` 전역을 `goal_kind`·`goal-kind`·`research_goal_satisfied`로 문자열 검색한 결과다. 일치한 파일은 `기억/layer1/M-0327.md` 21행 하나였다. 이 행은 `goal_kind`가 모든 역할 문맥의 필수 키라는 사실만 적고 있고, `research` 예약을 결정한 기록은 아니다.

셋째, `README.md`의 예약 문장("후속 작업을 위해 유지")을 도입한 커밋이다. `git log -S`로 찾은 결과는 `7d2597e`("do-math 기능 판본 5와 정적 검토 수리·근거를 보존")이었다. 커밋 메시지에는 예약 이유가 없다.

넷째, 추적 대상 개체별 자료다. 개체는 `goal_kind` 값과 목표 상태 `research_goal_satisfied` 둘이다. 정의 파일로는 `engine.py` 203~207행, `initialization.py` 283~288행, `cli.py` 96행, `governance.py` 138·160·169~171행, `academic.py` 241~261행을 열었다. 정본 문서 절로는 `README.md` 45행, `references/CLI-실행-계약.md` 223·237·627·633행, `계약/목표-감사.md` 7~9행, `계약/연구-계획.md` 23행, `계약/후보-준비.md` 43행을 열었다. 결정·불변식 파일로는 `.claude/skills/do-math/AGENTS.md` 5·9행과 동결문 238·260행을 열었다. 이 예약을 사용자가 결정했음을 보여 주는 결정 기록은 찾지 못했다.

#### 세계 물음

행위자는 연구 인스턴스를 초기화하는 연구 책임자다. 연구 책임자는 목표와 함께 목표 종류를 고르며, 정의 파일이 받아들이는 값은 `mathematical`과 `research` 둘이다.

`mathematical`에는 필요한 개체가 모두 정의돼 있다. 최종 보증 `mathematically_solved`, 목표 감사, 형식 결과가 그것이다.

`research`를 골랐을 때 행위자가 기대하는 결과는 비형식 최종 보증이다. 그러나 그 보증에 필요한 개체는 정의 파일에 없다. 목표 상태 `research_goal_satisfied`는 `validate_governance_state`가 금지한다. 해당 보증 경로는 `apply_goal_assurance`가 거부한다. 따라서 현재 세계에서 `research`는 받아들여진 뒤 버려지는 값이다.

#### 선택지

선택지 1: `research` 값만 제거하고 `goal_kind` 필드는 `mathematical` 하나로 남긴다. 변경 대상은 다음과 같다.

`cli.py` 96행의 선택지를 `("mathematical",)`로 줄이고, 277~278행의 거부 분기를 지운다. `engine.initialize`와 `initialization.initialize_state`는 `mathematical`이 아닌 값을 거부한다. `governance_engine.py` 420~421행과 `engine.py` 4370~4371행의 도달 불가 분기를 지운다. `lifecycle_engine.py` 611행의 조건을 `mathematically_solved` 하나로 줄인다. `계약/목표-감사.md` 9행의 마지막 두 문장을 지운다. `README.md` 45행과 `references/CLI-실행-계약.md` 223·237행의 예약 문장을 현행 단일 값 설명으로 바꾼다. 시험 여섯 곳의 `research` 입력은 `mathematical`로 바꾼다. 그중 `test_engine.py` 216~228행은 존재하지 않는 목표 상태를 검사하므로 `goal_status != "mathematically_solved"`만 확인하도록 고친다.

하류 영향은 다음과 같다. 역할 문맥에 값이 하나뿐인 `goal_kind`가 계속 남는다. `계약/연구-계획.md` 23행과 `계약/후보-준비.md` 43행의 조건문도 그대로 유지된다.

선택지 2: `goal_kind` 필드 자체를 제거한다. 선택지 1의 변경을 모두 포함하고 다음을 더한다.

CLI의 `--goal-kind` 인자와 `README.md` 90행의 예시 인자를 없앤다. `initialize`·`initialize_state`의 매개변수, 최초 입력 `config`, `governance.py` 138·160·169행의 필드, `engine.py` 1773행 문맥과 4340행 기준 키의 필드도 없앤다. `계약/목표-감사.md` 7행과 `계약/연구-계획.md` 23행에서 `goal_kind` 읽기를 지운다. `계약/후보-준비.md` 43행은 조건 없이 목표 명제의 형식 정의를 준비하도록 고쳐 쓴다. `goal_kind='mathematical'`을 넘기는 시험 약 스무 곳에서도 인자를 지운다.

하류 영향은 다음과 같다. 죽은 매개변수가 남지 않는다. 대신 CLI 사용법과 시험 fixture가 넓게 바뀌고, 목표 감사 기준 키의 해시 값이 달라진다.

선택지 3: README와 CLI 계약의 예약을 유지한다. 대신 Python 진입점도 CLI와 같이 `research`를 거부하게 해서 조용한 값 치환만 없앤다.

하류 영향은 다음과 같다. 사용자 값이 조용히 바뀌는 결함은 사라진다. 그러나 도달할 수 없는 거부 분기 두 곳, 존재할 수 없는 목표 상태 분기, 목표 감사 계약의 불가능한 입력 지시는 그대로 남는다.

#### 변형 물음

선택지 2의 대가는 CLI 인자 제거와 시험 약 스무 곳의 기계적 수정이다. 이 대가를 줄이는 변형이 선택지 1이다. 선택지 1은 필드를 남기고 값 집합만 하나로 닫아서, 사용자 결정 없이도 조용한 치환과 도달 불가 분기를 없앤다.

선택지 3의 대가는 도달 불가 분기를 남긴다는 것이다. 이 대가를 줄이는 변형은 README와 CLI 계약의 예약 문장을 "공개 진입값으로도 내부 값으로도 받지 않는다"로 고쳐 쓰는 것이다. 그러나 그 변형은 예약을 사실상 폐기하므로 선택지 1과 같아진다.

#### 추천 하나

선택지 2를 추천한다.

각 선택지를 승인한 뒤의 최종 상태를 비교하면 다음과 같다. 선택지 2만 값이 하나뿐인 필드와 그 필드를 조건으로 삼는 계약 문장을 남기지 않는다. 동결문 목적 1이 말하는 "죽은 패러미터"가 없어진다. 선택지 1은 필드를 남기므로, 역할 계약이 앞으로도 의미 없는 조건(`goal_kind`가 `mathematical`이면)을 계속 설명하게 된다.

선택지 3은 결함을 남긴 채 예약이라는 대체 구조를 유지한다. 예약을 소비하는 현재 소비자나 호환 계약, 이행 제약은 찾지 못했다. 예약 문장 자체가 "후속 작업"이라는 미래 추측을 근거로 삼는데, `.claude/skills/do-math/AGENTS.md` 9행은 바로 그런 추측을 근거로 계층을 만들지 말라고 한다.


### 판정
확정: 기각 · 승인기 [] · 기각기 [1, 2, 3] · 처분: 없음
최종 판정: 기각

### 근거
- 기 1: 항목 종류 대조에서 상신 필요성이 입증되지 않는다. 산출물의 README가 상위 기준과 다른 설명을 한다는 사실만으로 사용자 확정 규범의 변경이 되는 것은 아니다. 사용자 확정 기록이나 외부 사정이 없고, 추천안은 이미 확정된 죽은 인자 제거 방향이다. 비동등한 두 결과가 모두 현행 기준을 충족한다는 설명도 없으므로 조각 항목으로 닫을 결함을 상신 제안으로 제출한 것으로 판정한다.
- 기 2: 관문 적용 전 항목 종류 대조에 실패한다. 산출물의 예약 선언과 상위 기준이 충돌한다는 사실만으로 새 사용자 결정을 요구할 수 없다. 이 항목은 예약을 유지하라는 사용자 확정 기록을 제시하지 않았고, 추천 2는 기존 잔재 제거 지시를 적용하는 수리다. 선택지 1에 남는 죽은 입력과 선택지 3에 남는 도달 불가 경로는 해당 지시를 충족하는 대안이 아니다. 현재 역할 문맥의 의미를 유지하면서 입력·분기·문서·시험을 고치는 조각 항목으로 닫아야 한다.
- 기 3: 관문 적용 전 항목 종류가 어긋난다. 산출물 문서의 보존 선언을 사용자 결정으로 볼 근거가 없으며, 현재 확정된 잔재 제거 지시를 적용하는 데 새로운 사용자 선택은 필요하지 않다. 선택지 1은 의미 없는 필드·조건을 남긴다고 항목 자체가 인정하고 선택지 3은 기준 원문의 미래 호환 추측 금지와 충돌한다. 따라서 이 대안들은 상신을 성립시키는 현행 정본 내의 복수 결과가 아니다. 제시된 결함은 산출물 전건 안에서 조각으로 수리할 수 있다.

## R1-99

### 원문
제목: 동일성 검토 계약이 봉인 판정 기록에 없는 `identity_assessment.status` 필드를 설명한다

### 위치
`.claude/skills/do-math/계약/동일성-검토.md` 107행.

생산자는 `.claude/skills/do-math/scripts/do_math/knowledge_records.py` 260~262행(`record_identity_assessment`)과 `.claude/skills/do-math/scripts/do_math/review_cycle.py` 374~384행(`identity_assessment`)이다.

### 기준
```
2. 생산자와 소비자 사이의 계약 미스매치를 수리한다. 구현·호출부·스키마·시험·예시·문서가 같은 현재 계약을 사용하게 한다.
```

출처: `임시/do-math_검증_20260924_opus55/동결.md` 「목적 진술」 239행.

### 영향
`review_cycle.identity_assessment`가 만드는 판정 수령증의 키는 여섯 개다. `review_cycle_id`, `proposal_digest`, `decision`, `execution_ids`, `scope_complete`, `summary`다. `record_identity_assessment`는 봉인할 때 `effective`와 `status`를 명시적으로 뺀다(260행). 그러고 `id`, `family`, `formal_result_id`, `exposition_id`, `policy_ref`, `basis`를 더한다.

봉인 판정 기록에는 `status` 필드가 없다. 게다가 `unresolved`로 끝난 계보도 같은 경로로 판정 기록을 남긴다. 판정 사용 효력은 별도 기록 `assessment_uses[].status`(`active`·`suspended`·`withdrawn`)에 있다.

107행은 "`identity_assessment.status=completed`는 … `match`와 `mismatch` 모두에 나타날 수 있다"고 말한다. 이 문장을 읽은 동일성 검토자와 후속 역할은 존재하지 않는 필드를 판정 완결의 표지로 찾게 된다. `unresolved` 판정 기록이 봉인된다는 사실도 이 문장에서는 빠진다.

### 조각 1 — .claude/skills/do-math/계약/동일성-검토.md 107~107행
원래:
```
`identity_assessment.status=completed`는 검토 결과가 완결됐다는 기록으로 `match`와 `mismatch` 모두에 나타날 수 있다. 그 값 하나를 K 편입이나 현재 사용 가능성으로 읽지 않는다. 판정값과 판정 사용 효력, 형식 사용 효력을 함께 확인한다.
```
대체:
```
검토 계보가 끝나면 실행기는 `identity_assessments`에 판정 기록 하나를 봉인한다. 이 기록의 `decision`은 `match`, `mismatch`, `unresolved` 가운데 하나이며, 기록이 있다는 사실이나 `decision` 값 하나를 K 편입이나 현재 사용 가능성으로 읽지 않는다. 판정값과 `assessment_uses`의 판정 사용 효력, 형식 사용 효력을 함께 확인한다.
```


### 판정
확정: 기각 · 승인기 [1, 2] · 기각기 [3] · 처분: 없음
최종 판정: 기각

### 근거
- 기 3: 관문 4에 어긋난다. 대체 첫 문장인 “검토 계보가 끝나면 실행기는 identity_assessments에 판정 기록 하나를 봉인한다”는 계보 종료 전건에 대해 성립하지 않는다. 원래의 없는 status 필드를 고치는 대신, 자원 부족·대체·종료 등으로 끝난 계보에서도 반드시 판정 기록이 생긴다는 새 오해를 만든다. 실제 판정이 공개되는 경로와 단순히 계보가 끝나는 경로를 구별해야 한다.

## R1-101

### 원문
제목: 한 번의 저장이 같은 부모 커밋의 전체 트리를 최대 네 번 나열한다

### 위치
.claude/skills/do-math/scripts/do_math/git_store.py 318~330행(`_tree_paths`)과 82행 뒤(`__init__`의 상태 초기화). 반복 호출은 repository.py 84·200행과 git_store.py 178행에서 일어난다.

### 기준
임시/do-math_검증_20260924_opus55/동결.md 241행(목적 진술 4):

```
4. 같은 목적과 기능을 더 합리적인 로직으로 달성할 수 있는 과도한 비효율을 개선한다.
```

### 영향
`ResearchRepository.save_with_state`(repository.py 152~171행)는 한 번의 저장에서 같은 `expected_head`를 `_tree_paths`로 여러 번 나열한다. 첫째는 `_read_documents`의 84행이다. 둘째는 같은 함수가 부르는 `_validate_artifact_evidence`의 200행이다. 셋째는 `_validate_candidate`가 부르는 `_validate_artifact_evidence`의 200행이다. 넷째는 `GitStateStore.publish`의 178행이다. 둘째와 셋째는 학술 해소 기록이나 관찰 증거 참조가 있을 때만 일어난다. 그러니 저장 한 번에 적어도 두 번, 많게는 네 번 나열한다. `load()`도 84행과 200행에서 두 번 나열한다.

`_tree_paths`는 매번 `git ls-tree -r`를 새 프로세스로 실행한다. `_git`(413~451행)은 호출마다 두 물리 경계를 검사한다. 이어서 돌려받은 모든 경로에 `_validate_path`를 적용한다. 나열 대상은 `runtime/artifacts/` 아래의 모든 봉인 묶음을 포함하는 전체 트리다. 실행마다 입력 묶음이 추가되므로 이 트리는 연구가 진행될수록 커진다. 커밋 OID는 트리 내용을 고정하므로 같은 커밋을 다시 나열해도 결과는 항상 같다. 반복 나열은 결과를 바꾸지 않고 비용만 두세 배로 늘린다. 엔진은 상태가 바뀔 때마다 저장하므로 이 비용은 저장 빈도만큼 누적된다.

수리는 마지막으로 나열한 커밋 하나의 결과를 기억한다. 저장 한 번 안에서 같은 부모의 나열은 한 번으로 줄고, 다음 저장의 새 부모에서는 한 번만 새로 나열한다. 기억하는 항목이 하나뿐이므로 메모리 사용이 늘어나지 않는다. 반환형을 `frozenset`으로 바꾸어 호출자가 기억된 결과를 변경할 수 없게 한다. 호출자를 확인했다. `publish`는 `set(existing_paths)`로 복사하고, repository.py 84행은 정렬만 하며, 200행은 소속 검사만 한다. test_git_store.py 65~66행은 `assertIn`·`assertNotIn`으로만 쓴다. 따라서 호출자는 바꿀 필요가 없다. rg로 `_tree_paths`의 사용처가 이 네 곳과 시험 두 행뿐임을 확인했다.

### 조각 1 — .claude/skills/do-math/scripts/do_math/git_store.py 행 82 뒤
대체:
```
        self._listed: tuple[str, frozenset[str]] | None = None
```

### 조각 2 — .claude/skills/do-math/scripts/do_math/git_store.py 318~330행
원래:
```
    def _tree_paths(self, commit: str) -> set[str]:
        raw_paths = self._git("ls-tree", "-r", "-z", "--name-only", commit).stdout.split(b"\0")
        paths: set[str] = set()
        for raw_path in raw_paths:
            if not raw_path:
                continue
            try:
                path = raw_path.decode("utf-8")
            except UnicodeDecodeError as error:
                raise GitStateStoreError("existing state contains a non-UTF-8 path") from error
            self._validate_path(path)
            paths.add(path)
        return paths
```
대체:
```
    def _tree_paths(self, commit: str) -> frozenset[str]:
        # A commit's tree is immutable. One save lists its parent once for the
        # parent read, artifact evidence checks and publication.
        if self._listed is not None and self._listed[0] == commit:
            return self._listed[1]
        raw_paths = self._git("ls-tree", "-r", "-z", "--name-only", commit).stdout.split(b"\0")
        paths: set[str] = set()
        for raw_path in raw_paths:
            if not raw_path:
                continue
            try:
                path = raw_path.decode("utf-8")
            except UnicodeDecodeError as error:
                raise GitStateStoreError("existing state contains a non-UTF-8 path") from error
            self._validate_path(path)
            paths.add(path)
        self._listed = (commit, frozenset(paths))
        return self._listed[1]
```


### 판정
확정: 기각 · 승인기 [2, 3] · 기각기 [1] · 처분: 없음
최종 판정: 기각

### 근거
- 기 1: 관문 4·5에서 기존 물리 경계 검사가 보존되지 않는다. 캐시를 채운 뒤 같은 커밋을 요청할 때 경로가 재분석 지점으로 바뀌거나 볼륨 경계가 달라지면 원래 함수는 검사 오류를 내지만 대체 함수는 캐시 값을 바로 반환한다. 커밋의 불변성은 현재 저장소 경로의 물리적 동일성을 보장하지 않는다. 반복 나열을 줄이는 이점은 인정하지만 동결문의 현행 입력·근거 검사 유지 조건까지 충족하는 대체가 아니다.

## R1-05

### 원문
제목: 소진 판정이 저장 계약에 없는 활동 `obligations` 필드를 검사한다

### 위치
`.claude/skills/do-math/scripts/do_math/planning.py` 654~655행 (`exhaustion_state`). 활동 기록의 저장 스키마는 `.claude/skills/do-math/scripts/do_math/record_schemas/schemas.py` 92~100행이다.

### 기준
`임시/do-math_검증_20260924_opus55/동결.md` 「목적 진술」 238행:

```
1. 더 이상 활용되지 않는 호환성 요소, 죽은 패러미터, 무시되는 설정과 유사한 잔재를 제거한다. 현재 입력의 유효성·권한·근거·현재성 검사는 유지한다.
```

### 영향
활동 기록 스키마의 속성은 `activity_kind`부터 `finished_at`까지이며 `obligations`가 없다. 스키마는 `additionalProperties: False`라서 저장된 활동은 이 필드를 가질 수 없다. 사본 전체에서 활동에 `obligations`를 쓰는 생산자가 없다. `unfinished_activity_obligations` 사유를 읽는 소비자도 없다. 따라서 654행 조건은 항상 거짓이고, 소진 판정을 읽는 사람에게 존재하지 않는 활동 의무 개념을 보여 준다. 실제 미완료 작업은 바로 위 반환 작업 검사와 외부 대기 검사, 바로 아래 준비·검토 진행 검사가 다룬다. 삭제해도 판정 결과는 바뀌지 않는다.

### 조각 1 — .claude/skills/do-math/scripts/do_math/planning.py 654~655행
원래:
```
    if any(a.get('status')!='finished' and a.get('obligations') for a in runtime.get('activities',{}).values()):
        answer.update(reasons=['unfinished_activity_obligations']);return answer
```
대체:
```

```


### 판정
확정: 승인 · 승인기 [1, 2, 3] · 기각기 [] · 처분: 승인하되 고치지 않는다
최종 판정: 승인
최종 처분: 승인하되 고치지 않는다

### 근거
- 기 1: 수리한다
- 기 2: 승인하되 고치지 않는다
- 기 3: 수리한다

## R1-21

### 원문
제목: 입력 측정치의 token_estimate가 언제나 null인 죽은 필드다

### 위치
`.claude/skills/do-math/scripts/do_math/contracts.py` 346~347행의 `prompt_metrics`와 `.claude/skills/do-math/scripts/do_math/record_schemas/domains.py` 397~399행의 `metrics` 스키마다.

### 기준
`임시/do-math_검증_20260924_opus55/동결.md` 238행(목적 진술 1):

```text
더 이상 활용되지 않는 호환성 요소, 죽은 패러미터, 무시되는 설정과 유사한 잔재를 제거한다.
```

### 영향
`prompt_metrics`는 `token_estimate`를 언제나 `None`으로 쓰고, 저장 스키마는 이 필드를 `{"type": "null"}`로 고정한 채 필수로 요구한다. 산출물 전체에서 이 필드를 읽는 코드·문서·시험은 두 정의 지점밖에 없다. 그래서 모든 `input_metrics`와 입력 초과 기록의 `prompt_metrics`가 정보를 담을 수 없는 필드를 하나씩 저장한다. 기록을 읽는 운영자나 모델은 토큰 추정 기능이 있다고 오해할 수 있다. 수리 뒤 측정치는 실제로 측정한 바이트 값만 담는다.

### 조각 1 — .claude/skills/do-math/scripts/do_math/contracts.py 346~347행
원래:
```
            "framing_bytes": len(prompt.encode("utf-8")) - context_bytes - schema_bytes - sum(document_bytes.values()),
            "token_estimate": None}
```
대체:
```
            "framing_bytes": len(prompt.encode("utf-8")) - context_bytes - schema_bytes - sum(document_bytes.values())}
```

### 조각 2 — .claude/skills/do-math/scripts/do_math/record_schemas/domains.py 397~399행
원래:
```
        "framing_bytes": INTEGER, "token_estimate": {"type": "null"}},
        ("unit", "prompt_bytes", "context_bytes", "schema_bytes", "document_bytes",
         "context_component_value_bytes", "framing_bytes", "token_estimate"))
```
대체:
```
        "framing_bytes": INTEGER},
        ("unit", "prompt_bytes", "context_bytes", "schema_bytes", "document_bytes",
         "context_component_value_bytes", "framing_bytes"))
```


### 판정
확정: 승인 · 승인기 [1, 2, 3] · 기각기 [] · 처분: 승인하되 고치지 않는다
최종 판정: 승인
최종 처분: 승인하되 고치지 않는다

### 근거
- 기 1: 승인하되 고치지 않는다
- 기 2: 승인하되 고치지 않는다
- 기 3: 수리한다

## R1-23

### 원문
제목: revision_roots의 changes 인자가 결과에 쓰이지 않는 죽은 인자다

### 위치
`.claude/skills/do-math/scripts/do_math/knowledge.py` 487행의 `revision_roots(instance, knowledge_id, changes)`는 본문(488~492행)에서 `changes`를 읽지 않는다. 호출부는 `knowledge.py` 552행, `integration.py` 88행과 시험 14곳이다.

### 기준
`.claude/skills/do-math/AGENTS.md` 5행:

```text
구판 호환을 위한 이전 구현·이름 별칭·래퍼·구형 인자·무시되는 설정·버전별 분기·마이그레이션 경로를 남기지 않는다.
```

`임시/do-math_검증_20260924_opus55/동결.md` 238행(목적 진술 1):

```text
더 이상 활용되지 않는 호환성 요소, 죽은 패러미터, 무시되는 설정과 유사한 잔재를 제거한다.
```

### 영향
개정 뿌리는 언제나 대상 지식과 그 해설 두 개이며, 주석(490~491행)이 밝히듯 형식 결과는 원천이 바뀌어도 뿌리가 되지 않는다. 그런데 인자 목록은 바뀐 필드에 따라 뿌리가 달라진다는 인상을 준다. 예컨대 `lean_code` 개정이 형식 결과를 뿌리에 더한다고 읽게 된다. 선언 영향(`impact_set`)을 계산하는 생산자와 시험 작성자가 이 인상에 따라 잘못된 기대를 세울 수 있다. 16개 호출부가 모두 의미 없는 값을 계산해 넘긴다. 수리 뒤 뿌리가 개정 내용과 무관하다는 계약이 서명에 드러난다.

### 조각 1 — .claude/skills/do-math/scripts/do_math/knowledge.py 487~487행
원래:
```
def revision_roots(instance, knowledge_id, changes):
```
대체:
```
def revision_roots(instance, knowledge_id):
```

### 조각 2 — .claude/skills/do-math/scripts/do_math/knowledge.py 552~552행
원래:
```
    roots = revision_roots(instance, knowledge_id, changes)
```
대체:
```
    roots = revision_roots(instance, knowledge_id)
```

### 조각 3 — .claude/skills/do-math/scripts/do_math/integration.py 88~88행
원래:
```
        target_roots = knowledge.revision_roots(instance, change["id"], change["changes"])
```
대체:
```
        target_roots = knowledge.revision_roots(instance, change["id"])
```

### 조각 4 — .claude/skills/do-math/scripts/tests/test_knowledge.py 66~66행
원래:
```
        declared_impact=declaration(state, runtime, k.revision_roots(state, kid, changes)))
```
대체:
```
        declared_impact=declaration(state, runtime, k.revision_roots(state, kid)))
```

### 조각 5 — .claude/skills/do-math/scripts/tests/test_knowledge_import_engine.py 227~227행
원래:
```
        impact = declaration(e.instance, e.runtime, k.revision_roots(e.instance, kid, changes))
```
대체:
```
        impact = declaration(e.instance, e.runtime, k.revision_roots(e.instance, kid))
```

### 조각 6 — .claude/skills/do-math/scripts/tests/test_purpose_engine.py 543~543행
원래:
```
        roots = knowledge.revision_roots(engine.instance, kid, changes)
```
대체:
```
        roots = knowledge.revision_roots(engine.instance, kid)
```

### 조각 7 — .claude/skills/do-math/scripts/tests/test_redesign_ENGINE.py 1092~1092행
원래:
```
            roots = knowledge.revision_roots(engine.instance, change["id"], change["changes"])
```
대체:
```
            roots = knowledge.revision_roots(engine.instance, change["id"])
```

### 조각 8 — .claude/skills/do-math/scripts/tests/test_redesign_ENGINE.py 1094~1094행
원래:
```
        roots = set().union(*(knowledge.revision_roots(engine.instance, change["id"], change["changes"])
```
대체:
```
        roots = set().union(*(knowledge.revision_roots(engine.instance, change["id"])
```

### 조각 9 — .claude/skills/do-math/scripts/tests/test_redesign_EVIDENCE_walkthroughs.py 224~224행
원래:
```
        roots = knowledge.revision_roots(e.instance, kid, changes)
```
대체:
```
        roots = knowledge.revision_roots(e.instance, kid)
```

### 조각 10 — .claude/skills/do-math/scripts/tests/test_redesign_KNOWLEDGE.py 683~683행
원래:
```
        roots = knowledge.revision_roots(self.state, self.kid, changes)
```
대체:
```
        roots = knowledge.revision_roots(self.state, self.kid)
```

### 조각 11 — .claude/skills/do-math/scripts/tests/test_redesign_KNOWLEDGE.py 888~888행
원래:
```
        roots = knowledge.revision_roots(self.state, self.kid, changes)
```
대체:
```
        roots = knowledge.revision_roots(self.state, self.kid)
```

### 조각 12 — .claude/skills/do-math/scripts/tests/test_review_research.py 223~223행
원래:
```
        roots = knowledge.revision_roots(engine.instance, item['id'], changes)
```
대체:
```
        roots = knowledge.revision_roots(engine.instance, item['id'])
```

### 조각 13 — .claude/skills/do-math/scripts/tests/test_review_research.py 243~243행
원래:
```
        roots = knowledge.revision_roots(engine.instance, item['id'], changes)
```
대체:
```
        roots = knowledge.revision_roots(engine.instance, item['id'])
```

### 조각 14 — .claude/skills/do-math/scripts/tests/test_submission_boundaries.py 197~197행
원래:
```
                    revision_roots(engine.instance, kid, changes), [])
```
대체:
```
                    revision_roots(engine.instance, kid), [])
```

### 조각 15 — .claude/skills/do-math/scripts/tests/test_submission_tools.py 558~558행
원래:
```
            roots = revision_roots(engine.instance, context['action']['target'], changes)
```
대체:
```
            roots = revision_roots(engine.instance, context['action']['target'])
```

### 조각 16 — .claude/skills/do-math/scripts/tests/test_submission_tools.py 635~635행
원래:
```
                roots = revision_roots(engine.instance, kid, changes)
```
대체:
```
                roots = revision_roots(engine.instance, kid)
```

### 조각 17 — .claude/skills/do-math/scripts/tests/test_task_scope.py 169~169행
원래:
```
        roots=knowledge.revision_roots(engine.instance,ids['KN-reading'],changes)
```
대체:
```
        roots=knowledge.revision_roots(engine.instance,ids['KN-reading'])
```


### 판정
확정: 승인 · 승인기 [1, 2, 3] · 기각기 [] · 처분: 승인하되 고치지 않는다
최종 판정: 승인
최종 처분: 승인하되 고치지 않는다

### 근거
- 기 1: 수리한다
- 기 2: 승인하되 고치지 않는다
- 기 3: 수리한다

## R1-25

### 원문
제목: 영향 계획이 존재하지 않는 plans·permissions·questions 레코드 가족을 순회한다

### 위치
`.claude/skills/do-math/scripts/do_math/knowledge.py` 226~233행의 `_impact_records`다.

### 기준
`임시/do-math_검증_20260924_opus55/동결.md` 238행(목적 진술 1):

```text
더 이상 활용되지 않는 호환성 요소, 죽은 패러미터, 무시되는 설정과 유사한 잔재를 제거한다.
```

`임시/do-math_검증_20260924_opus55/동결.md` 241행(목적 진술 4):

```text
같은 목적과 기능을 더 합리적인 로직으로 달성할 수 있는 과도한 비효율을 개선한다.
```

### 영향
`plans`와 `permissions`는 설치 저장 계약에 등록된 가족이 아니다. `StateContract.validate`는 등록되지 않은 최상위 키를 `unregistered family`로 거부하므로(`state_contract.py` 110~112행) 유효한 상태에는 나타나지 않는다. `runtime.questions`는 문자열 목록(`schemas.py` 238행 `array(TEXT)`)이라 `isinstance(row, dict)`에서 모두 걸러진다. 그래서 이 반복은 영향 계획에 아무 레코드도 더하지 않는다. 그런데도 `plan_impact`와 `_apply_impact_effects`가 부를 때마다 실행되고, 읽는 사람에게는 영향 분석이 계획·허가·질문을 포함한다는 잘못된 인상을 준다. 수리 뒤 영향 대상은 실제로 존재하는 레코드 가족(`_records`)으로 한정된다.

### 조각 1 — .claude/skills/do-math/scripts/do_math/knowledge.py 226~233행
원래:
```
def _impact_records(instance, runtime):
    records = dict(_records(instance, runtime))
    for key in ("plans", "questions", "permissions"):
        values = runtime.get(key, instance.get(key, {}))
        for row in values.values() if isinstance(values, dict) else values:
            if isinstance(row, dict) and row.get("id"):
                records[row["id"]] = row
    return records
```
대체:
```
def _impact_records(instance, runtime):
    return dict(_records(instance, runtime))
```


### 판정
확정: 승인 · 승인기 [1, 2, 3] · 기각기 [] · 처분: 승인하되 고치지 않는다
최종 판정: 승인
최종 처분: 승인하되 고치지 않는다

### 근거
- 기 1: 수리한다
- 기 2: 승인하되 고치지 않는다
- 기 3: 수리한다

## R1-28

### 원문
제목: 상태 점검이 실행 레코드 안의 self_check_obligations라는 존재하지 않는 필드를 검사한다

### 위치
`.claude/skills/do-math/scripts/do_math/state_checks.py` 468~472행이다.

### 기준
`임시/do-math_검증_20260924_opus55/동결.md` 238행(목적 진술 1):

```text
더 이상 활용되지 않는 호환성 요소, 죽은 패러미터, 무시되는 설정과 유사한 잔재를 제거한다.
```

### 영향
실행 레코드 스키마(`schemas.py` 101~117행과 `domains.py`의 추가 속성)는 닫힌 객체이며 `self_check_obligations` 속성이 없다. 자기 점검 의무는 별도 가족 `runtime/self_check_obligations`에 저장되고, 같은 영역 452~461행이 이미 그 가족을 검사한다. 472행이 보는 `fulfilled`·`resolved` 상태도 의무 스키마의 상태값(`open`, `answered`, `closed`, `schemas.py` 189행)에 없다. 따라서 이 반복은 언제나 빈 목록을 돌며, 읽는 사람에게 의무가 실행 레코드에도 내장된다는 잘못된 계약을 보여 준다. 수리 뒤 의무 검사는 실제 저장 가족 한 곳에만 남는다.

### 조각 1 — .claude/skills/do-math/scripts/do_math/state_checks.py 468~472행
원래:
```
            for obligation in execution.get('self_check_obligations', []):
                if not obligation.get('id') or not obligation.get('status'):
                    defect('self-check obligation lacks identity or state', identifier)
                if obligation.get('status') in {'fulfilled', 'resolved'} and not obligation.get('response_ref'):
                    defect('closed self-check lacks response reference', identifier)
```
대체:
```

```


### 판정
확정: 승인 · 승인기 [1, 2, 3] · 기각기 [] · 처분: 승인하되 고치지 않는다
최종 판정: 승인
최종 처분: 승인하되 고치지 않는다

### 근거
- 기 1: 수리한다
- 기 2: 승인하되 고치지 않는다
- 기 3: 수리한다

## R1-37

### 원문
제목: 형식 입력 manifest 시험이 폐기된 timeout_seconds 필드로 검증기 입력을 구성한다

### 위치
`.claude/skills/do-math/scripts/tests/test_formal_input_manifest.py` 50행의 `verifier` 고정물이다.

### 기준
`.claude/skills/do-math/AGENTS.md` 7행:

```text
테스트도 현행 계약을 직접 구성한다. 구형 fixture나 인터페이스를 살리려고 제품 코드에 예외를 넣지 않는다.
```

`.claude/skills/do-math/references/공통-실행.md` 75행:

```text
계산 시간 상한은 적용하지 않으며, 작업 실행의 정지 요청이나 기한에 따라 종료될 수 있다.
```

### 영향
현행 생산자 `engine.py` 1814~1821행의 `formal_verifier` 입력에는 `timeout_seconds`가 없고, Lean 검증에는 시간 상한을 두지 않는다. 다른 시험들은 오히려 `timeout_seconds`가 없음을 확인한다(`test_formal_runtime.py` 91행, `test_lifecycle_engine.py` 833행). 이 시험만 폐기된 필드를 넣은 입력으로 "기계 전용 목록이 의도 해석을 막지 않는다"는 주장을 확인하므로, 검증 대상이 현행 입력 형태가 아니다. 시험을 읽는 사람은 검증기에 시간 상한 입력이 있다고 오해할 수 있다. 수리 뒤 고정물은 현행 입력 필드만 가진다.

### 조각 1 — .claude/skills/do-math/scripts/tests/test_formal_input_manifest.py 50~50행
원래:
```
                        'timeout_seconds': 30, 'environment_id': 'TE-fixed', 'environment_status': 'active'}
```
대체:
```
                        'environment_id': 'TE-fixed', 'environment_status': 'active'}
```


### 판정
확정: 승인 · 승인기 [1, 2, 3] · 기각기 [] · 처분: 승인하되 고치지 않는다
최종 판정: 승인
최종 처분: 승인하되 고치지 않는다

### 근거
- 기 1: 승인하되 고치지 않는다
- 기 2: 승인하되 고치지 않는다
- 기 3: 수리한다

## R1-38

### 원문
제목: 의미 검증의 과제 관찰 규칙 검사가 새어 나온 반복 변수에 기대는 뒤틀린 반복문이다

### 위치
`.claude/skills/do-math/scripts/do_math/record_schemas/__init__.py` 357~360행이다.

### 기준
`임시/do-math_검증_20260924_opus55/동결.md` 241행(목적 진술 4):

```text
같은 목적과 기능을 더 합리적인 로직으로 달성할 수 있는 과도한 비효율을 개선한다.
```

`임시/do-math_검증_20260924_opus55/동결.md` 242행(목적 진술 5):

```text
절차와 스크립트 안팎에서 발견한 다른 문제도 실제 근거에 따라 해결한다.
```

### 영향
원소 하나짜리 튜플을 도는 첫 반복은 `name`을 묶고 가져오기만 하며, 실제 검사 반복은 그 밖으로 내어쓰기된 채 새어 나온 `name`에 기대고 본문만 12칸 들여쓰기되어 있다. 읽는 사람은 중첩 반복으로 오독하기 쉽다. 누군가 튜플에 가족을 하나 더하면 마지막 가족만 검사되고 앞 가족은 조용히 빠진다. 수리 뒤 같은 검사를 한 번의 직접 반복으로 수행한다.

### 조각 1 — .claude/skills/do-math/scripts/do_math/record_schemas/__init__.py 357~360행
원래:
```
    for name in ("task_observation_rules",):
        from ..observations import validate_rules
    for rules in runtime.get(name, {}).values():
            validate_rules(rules, allow_empty=True)
```
대체:
```
    from ..observations import validate_rules
    for rules in runtime.get("task_observation_rules", {}).values():
        validate_rules(rules, allow_empty=True)
```


### 판정
확정: 승인 · 승인기 [1, 2, 3] · 기각기 [] · 처분: 승인하되 고치지 않는다
최종 판정: 승인
최종 처분: 승인하되 고치지 않는다

### 근거
- 기 1: 승인하되 고치지 않는다
- 기 2: 승인하되 고치지 않는다
- 기 3: 승인하되 고치지 않는다

## R1-61

### 원문
제목: ModelCalls가 생산자 없는 `on_control` 콜백 키를 소유 스레드로 옮긴다

### 위치
`.claude/skills/do-math/scripts/do_math/parallel.py` 40행이다. `start_call`이 소유 스레드 콜백으로 감쌀 인자 이름 목록에 `on_control`이 들어 있다.

### 기준
```
1. 더 이상 활용되지 않는 호환성 요소, 죽은 패러미터, 무시되는 설정과 유사한 잔재를 제거한다. 현재 입력의 유효성·권한·근거·현재성 검사는 유지한다.
```
출처: `임시/do-math_검증_20260924_opus55/동결.md` 「목적 진술」 238행.

### 영향
사본 `scripts/` 전체를 단어 단위로 검색하면 `on_control`은 이 행에만 나온다. 러너(`model_runner.py` 36~45행), 형식 검사기, 호출부(`scheduler.py` 27행과 552행) 어디도 이 이름의 콜백을 넘기거나 받지 않는다. 남은 세 이름(`on_started`, `on_observation`, `should_stop`)이 실제 계약이다. 없는 콜백 이름이 목록에 있으면, 제어 요청을 콜백으로 받는 경로가 있다고 독자가 오해한다. 실제 제어는 `ControlTransport` 파일 전달과 실행기의 pump가 맡는다.

### 조각 1 — .claude/skills/do-math/scripts/do_math/parallel.py 40~40행
원래:
```
        for key in ("on_started", "on_observation", "should_stop", "on_control"):
```
대체:
```
        for key in ("on_started", "on_observation", "should_stop"):
```


### 판정
확정: 승인 · 승인기 [1, 2, 3] · 기각기 [] · 처분: 승인하되 고치지 않는다
최종 판정: 승인
최종 처분: 승인하되 고치지 않는다

### 근거
- 기 1: 승인하되 고치지 않는다
- 기 2: 승인하되 고치지 않는다
- 기 3: 수리한다

## R1-62

### 원문
제목: CLI 실행 계약의 학술 요구 검사 문단이 두 번 실려 있다

### 위치
`.claude/skills/do-math/references/CLI-실행-계약.md` 「학술 요구와 외부 거부」 절의 410행과 412행이다. 두 문단은 같은 검사 네 가지를 같은 순서로 적는다. 마지막 문장만 "새 판본과 내용 해시"와 "새 revision과 SHA-256"으로 표현이 다르다.

### 기준
```
2. 생산자와 소비자 사이의 계약 미스매치를 수리한다. 구현·호출부·스키마·시험·예시·문서가 같은 현재 계약을 사용하게 한다.
5. 절차와 스크립트 안팎에서 발견한 다른 문제도 실제 근거에 따라 해결한다.
```
출처: `임시/do-math_검증_20260924_opus55/동결.md` 「목적 진술」 239행, 242행.

### 영향
charter 결정을 작성하는 운영자나 구현자는 연속한 두 문단을 서로 다른 규칙으로 읽을 수 있다. "새 판본과 내용 해시"와 "새 revision과 SHA-256"이 별개의 두 요구인지 확인하려고 구현을 다시 대조하게 된다. 한 문단을 지워도 전달되는 조건은 줄지 않는다. 남기는 410행은 같은 절의 "새 헌장" 용어와 맞는다.

### 조각 1 — .claude/skills/do-math/references/CLI-실행-계약.md 411~412행
원래:
```

각 requirement는 고유한 `id`, 비어 있지 않은 `scope`, `assessor="research_plan"`, 중복 없는 비어 있지 않은 `criteria`를 요구한다. `required_inputs`는 정확한 입력 참조 목록이다. `external_effects`의 각 항목은 고유 `id`, `scope`, 선택적 `grant_id`를 가진다. 요구 목록의 변경은 새 revision과 SHA-256을 만들고 현재 해결 근거에 결박된 새 과제를 생성한다.
```
대체:
```

```


### 판정
확정: 승인 · 승인기 [1, 2, 3] · 기각기 [] · 처분: 승인하되 고치지 않는다
최종 판정: 승인
최종 처분: 승인하되 고치지 않는다

### 근거
- 기 1: 승인하되 고치지 않는다
- 기 2: 승인하되 고치지 않는다
- 기 3: 승인하되 고치지 않는다

## R1-69

### 원문
제목: 실행기 상태 `budget_exhausted`는 설정되는 곳이 없는데 상태 조건 다섯 곳에 남아 있다

### 위치
- .claude/skills/do-math/scripts/do_math/engine.py 895행, 981행
- .claude/skills/do-math/scripts/do_math/academic_engine.py 63행
- .claude/skills/do-math/scripts/do_math/lifecycle_engine.py 978행
- .claude/skills/do-math/scripts/do_math/scheduler.py 100행
- .claude/skills/do-math/scripts/tests/test_purpose_engine.py 429행

### 기준
```
1. 더 이상 활용되지 않는 호환성 요소, 죽은 패러미터, 무시되는 설정과 유사한 잔재를 제거한다. 현재 입력의 유효성·권한·근거·현재성 검사는 유지한다.
```
임시/do-math_검증_20260924_opus55/동결.md 238행(목적 진술)

```
- 테스트도 현행 계약을 직접 구성한다. 구형 fixture나 인터페이스를 살리려고 제품 코드에 예외를 넣지 않는다. 폐기한 기능만 검사하는 테스트는 제거하고, 유지하는 기능의 검사는 새 계약에 맞춘다.
```
.claude/skills/do-math/AGENTS.md 7행

### 영향
do_math 모듈 전체에서 `runtime["status"]`에 `budget_exhausted`를 대입하는 곳을 찾았으나 없었다. 문자열 대입, `runtime.update(status=...)`, 변수 대입을 모두 grep했다. 이 값은 위의 다섯 집합 멤버십 검사에서만 나온다. CLI 실행 계약의 status 표(97~102행)도 `budget_exhausted` 실행기 상태를 정의하지 않는다. 따라서 이 멤버십은 어떤 입력으로도 참이 되지 않는다.

그런데도 이 조건들은 유지보수자에게 누적 예산 소진이라는 실행기 정지 상태가 있다고 알린다. 이 상태는 같은 이름의 대기 종류 `budget_exhausted`와 혼동된다. 그 대기 종류도 현재 생산자가 없으며, 별도 항목 「누적·고정 구간 사용량 제약 경로가 생산자 없이 예약 계산·스키마·대기 어휘에 남아 있다」가 제거한다. 시험 test_purpose_engine.py 429행도 도달할 수 없는 상태를 조기 실패 조건으로 둔다.

### 조각 1 — .claude/skills/do-math/scripts/do_math/engine.py 895~895행
원래:
```
                if self.runtime["status"] in {"waiting", "budget_exhausted", "capacity_waiting"}: self.runtime["status"] = "ready"
```
대체:
```
                if self.runtime["status"] in {"waiting", "capacity_waiting"}: self.runtime["status"] = "ready"
```

### 조각 2 — .claude/skills/do-math/scripts/do_math/engine.py 981~981행
원래:
```
                if self.runtime["status"] in {"waiting", "budget_exhausted", "capacity_waiting"}:
```
대체:
```
                if self.runtime["status"] in {"waiting", "capacity_waiting"}:
```

### 조각 3 — .claude/skills/do-math/scripts/do_math/academic_engine.py 63~63행
원래:
```
        if basis is None or self.runtime["status"] in {"paused", "closed", "budget_exhausted"}: return
```
대체:
```
        if basis is None or self.runtime["status"] in {"paused", "closed"}: return
```

### 조각 4 — .claude/skills/do-math/scripts/do_math/lifecycle_engine.py 978~978행
원래:
```
        if self.runtime.get('status') in {'paused', 'closed', 'completed', 'budget_exhausted'}:
```
대체:
```
        if self.runtime.get('status') in {'paused', 'closed', 'completed'}:
```

### 조각 5 — .claude/skills/do-math/scripts/do_math/scheduler.py 100~100행
원래:
```
                'paused', 'closed', 'completed', 'budget_exhausted'}:
```
대체:
```
                'paused', 'closed', 'completed'}:
```

### 조각 6 — .claude/skills/do-math/scripts/tests/test_purpose_engine.py 429~429행
원래:
```
            if engine.runtime['status'] in {'paused', 'closed', 'budget_exhausted', 'waiting'}:
```
대체:
```
            if engine.runtime['status'] in {'paused', 'closed', 'waiting'}:
```


### 판정
확정: 승인 · 승인기 [1, 2, 3] · 기각기 [] · 처분: 승인하되 고치지 않는다
최종 판정: 승인
최종 처분: 승인하되 고치지 않는다

### 근거
- 기 1: 승인하되 고치지 않는다
- 기 2: 승인하되 고치지 않는다
- 기 3: 수리한다

## R1-71

### 원문
제목: `SessionSlots.acquire`가 `role_profile_refs`의 문자열 참조를 허용하는 죽은 분기를 가진다

### 위치
.claude/skills/do-math/scripts/do_math/session_slots.py 155행

### 기준
```
- 설계를 바꾸면 구현·호출부·스키마·테스트·예시·문서를 같은 변경에서 새 계약으로 교체한다. 구판 호환을 위한 이전 구현·이름 별칭·래퍼·구형 인자·무시되는 설정·버전별 분기·마이그레이션 경로를 남기지 않는다.
```
.claude/skills/do-math/AGENTS.md 5행

### 영향
`role_profile_refs`의 값은 `build_profiles`가 만든 `profile_ref` 객체 목록이다(execution_profiles.py 236행). 저장 계약도 객체 배열만 받는다. record_schemas/schemas.py 228행은 `array(PROFILE_REF)`로 받고, record_schemas/__init__.py 141~146행은 역할마다 `minItems: 1`인 `PROFILE_REF` 배열로 등록한다. 같은 파일의 `snapshot`(session_slots.py 346행)도 `ref["id"]`로만 읽는다. 그런데 155행만 `reference["id"] if isinstance(reference, dict) else reference`로 문자열 참조를 받아 준다.

이 분기에 도달하는 입력은 없다. 그런데도 역할 프로필 참조가 문자열일 수 있다는 폐기된 형태를 한 곳에서만 인정하므로, 같은 필드의 해석이 파일 안에서 갈린다.

### 조각 1 — .claude/skills/do-math/scripts/do_math/session_slots.py 155~155행
원래:
```
                    active_profile = self.instance["execution_profiles"][reference["id"] if isinstance(reference, dict) else reference]
```
대체:
```
                    active_profile = self.instance["execution_profiles"][reference["id"]]
```


### 판정
확정: 승인 · 승인기 [1, 2, 3] · 기각기 [] · 처분: 승인하되 고치지 않는다
최종 판정: 승인
최종 처분: 승인하되 고치지 않는다

### 근거
- 기 1: 승인하되 고치지 않는다
- 기 2: 승인하되 고치지 않는다
- 기 3: 수리한다

## R1-82

### 원문
제목: 묶음 권한 검사와 참조 검사기가 생산자 없는 컨텍스트 키 authority_catalog를 읽는다

### 위치
`.claude/skills/do-math/scripts/do_math/integration.py` 415~416행의 `inspect_bundles`는 묶음의 `authority_refs`를 대조할 허가 집합을 `grants`, `decisions`, `authority_catalog` 세 키에서 모은다. `.claude/skills/do-math/scripts/do_math/submission.py` 451~453행의 `_reference_ids`도 제출 참조로 허용할 ID를 모으면서 같은 `authority_catalog` 키를 읽는다.

### 기준
```
.claude/skills/do-math/AGENTS.md 5행
- 설계를 바꾸면 구현·호출부·스키마·테스트·예시·문서를 같은 변경에서 새 계약으로 교체한다. 구판 호환을 위한 이전 구현·이름 별칭·래퍼·구형 인자·무시되는 설정·버전별 분기·마이그레이션 경로를 남기지 않는다.
```

```
임시/do-math_검증_20260924_opus55/동결.md 239행 (목적 진술)
2. 생산자와 소비자 사이의 계약 미스매치를 수리한다. 구현·호출부·스키마·시험·예시·문서가 같은 현재 계약을 사용하게 한다.
```

### 영향
사본 전체(`scripts/`, `references/`, `계약/`, 시험 포함)에서 `authority_catalog`는 위 두 소비 지점에만 나온다. 역할 컨텍스트를 만드는 `engine.py`의 `_context`(1686행 이하), `governance_engine.py` 137~152행, `context_store.prepare_role_input`, `submission.install_tools` 가운데 어느 것도 이 키를 쓰지 않는다. 실제 허가 원천인 `context["grants"]`(engine.py 1778행)와 `context["decisions"]`(engine.py 1847행)는 이미 같은 두 소비 지점이 함께 읽는다.

따라서 이 키는 어떤 입력에서도 빈 목록으로 평가된다. 코드를 읽는 유지보수자와 검토자는 권한 카탈로그라는 별도 허가 원천이 있다고 오해한다. 생산자 없는 소비 경로가 남으면 앞으로 누가 같은 이름의 키를 컨텍스트에 넣을 때 검토 없이 새 허가 원천이 열린다. 두 지점에서 키를 지워도 현재 동작은 바뀌지 않는다. 사본 시험에도 이 키를 쓰는 곳이 없다.

### 조각 1 — .claude/skills/do-math/scripts/do_math/integration.py 415~416행
원래:
```
    authorities = {row["id"] for key in ("grants", "decisions", "authority_catalog")
                   for row in context.get(key, []) if row.get("id")}
```
대체:
```
    authorities = {row["id"] for key in ("grants", "decisions")
                   for row in context.get(key, []) if row.get("id")}
```

### 조각 2 — .claude/skills/do-math/scripts/do_math/submission.py 451~453행
원래:
```
    for key in ("user_inputs", "events", "external_operations", "external_rejections", "question_links", "decisions",
                "authority_catalog", "activities", "executions", "self_check_obligations", "observation_facts",
                "governance_records", "delegations", "goal_judgments"):
```
대체:
```
    for key in ("user_inputs", "events", "external_operations", "external_rejections", "question_links", "decisions",
                "activities", "executions", "self_check_obligations", "observation_facts",
                "governance_records", "delegations", "goal_judgments"):
```


### 판정
확정: 승인 · 승인기 [1, 2, 3] · 기각기 [] · 처분: 승인하되 고치지 않는다
최종 판정: 승인
최종 처분: 승인하되 고치지 않는다

### 근거
- 기 1: 승인하되 고치지 않는다
- 기 2: 승인하되 고치지 않는다
- 기 3: 수리한다

## R1-83

### 원문
제목: 묶음 검사가 어떤 생산자도 채우지 않는 computed_impacts를 소비한다

### 위치
`.claude/skills/do-math/scripts/do_math/integration.py` 427~430행의 `inspect_bundles`는 `context["computed_impacts"]`에서 묶음별 계산 영향을 찾는다. 선언한 `impact_set`이 그 값과 다르면 `integration.impact_review` 문제를 반환한다.

### 기준
```
.claude/skills/do-math/AGENTS.md 5행
- 설계를 바꾸면 구현·호출부·스키마·테스트·예시·문서를 같은 변경에서 새 계약으로 교체한다. 구판 호환을 위한 이전 구현·이름 별칭·래퍼·구형 인자·무시되는 설정·버전별 분기·마이그레이션 경로를 남기지 않는다.
```

```
임시/do-math_검증_20260924_opus55/동결.md 239행 (목적 진술)
2. 생산자와 소비자 사이의 계약 미스매치를 수리한다. 구현·호출부·스키마·시험·예시·문서가 같은 현재 계약을 사용하게 한다.
```

### 영향
사본 전체에서 `computed_impacts`는 이 한 줄에만 나오고, 컨텍스트에 이 키를 쓰는 코드는 없다. 사본 전체에서 `integration.impact_review` 규칙 ID를 읽는 소비자도 없다. 그래서 이 분기는 어떤 실행에서도 `computed`가 `None`이 되어 건너뛰어진다.

현행 계약에서 선언 영향과 계산 영향의 차이는 다른 경로가 처리한다. 적용 시점에 `bundle_impact_request`(74~133행)가 `knowledge.plan_impact`로 계산 영향을 만든다. 차이가 있으면 `require_bundle_impact_review`(175~219행)가 지정된 독립 영향 검토를 요구한다. 따라서 이 분기를 남기면 코드를 읽는 사람이 제출 구조 검사가 선언 영향을 계산 영향과 대조한다고 오해하고, 실제 관문의 위치를 잘못 짚는다. 분기를 지워도 현재 동작은 바뀌지 않는다.

### 조각 1 — .claude/skills/do-math/scripts/do_math/integration.py 427~430행
원래:
```
        computed = context.get("computed_impacts", {}).get(ident)
        if computed is not None and set(bundle["impact_set"]) != set(computed):
            issues.append(issue("integration.impact_review", "output/integration_bundles",
                                "declared impact differs from computed dependencies; independent review required", ident))
```
대체:
```

```


### 판정
확정: 승인 · 승인기 [1, 2, 3] · 기각기 [] · 처분: 승인하되 고치지 않는다
최종 판정: 승인
최종 처분: 승인하되 고치지 않는다

### 근거
- 기 1: 승인하되 고치지 않는다
- 기 2: 승인하되 고치지 않는다
- 기 3: 수리한다

## R1-93

### 원문
제목: 검토 실행 수락에서 소유 활동 결박이 두 번 적혀 있고 두 번째는 참이 될 수 없다

### 위치
`.claude/skills/do-math/scripts/do_math/review_engine.py` 342~344행(`_admit_review_execution`).

### 기준
```
1. 더 이상 활용되지 않는 호환성 요소, 죽은 패러미터, 무시되는 설정과 유사한 잔재를 제거한다. 현재 입력의 유효성·권한·근거·현재성 검사는 유지한다.
```

출처: `임시/do-math_검증_20260924_opus55/동결.md` 「목적 진술」 238행.

```
4. 같은 목적과 기능을 더 합리적인 로직으로 달성할 수 있는 과도한 비효율을 개선한다.
```

출처: 같은 파일 241행.

### 영향
같은 함수의 330~332행이 이미 `cycle.get('owner_activity_id') is None`일 때 소유 활동을 결박하고 `review_input_basis`를 다시 포착한다. 이 결박은 예산 소진(333행)·범위 부족(335~339행)·후속 예약(340~341행)으로 반환하기 전에 무조건 먼저 실행된다. 301~302행이 `owner`가 비어 있으면 예외를 던지므로 330행 뒤에는 `cycle['owner_activity_id']`가 항상 채워져 있다. 그러므로 342~344행의 같은 조건은 어떤 입력에서도 거짓이다.

이 중복 때문에 검토 활동의 상태 전이를 읽는 사람이 잘못 해석할 수 있다. 342~344행만 보면 소유 활동이 "수락이 성공한 뒤에만" 결박되는 것처럼 보인다. 실제로는 수락이 거부될 때도 먼저 결박된다. 삭제해도 동작은 같다. 대신 결박 시점이 330~332행 하나로 드러난다.

### 조각 1 — .claude/skills/do-math/scripts/do_math/review_engine.py 342~344행
원래:
```
        if cycle.get('owner_activity_id') is None:
            cycle['owner_activity_id'] = owner
            cycle['review_input_basis'] = capture_review_input_basis(cycle)
```
대체:
```

```


### 판정
확정: 승인 · 승인기 [1, 2, 3] · 기각기 [] · 처분: 승인하되 고치지 않는다
최종 판정: 승인
최종 처분: 승인하되 고치지 않는다

### 근거
- 기 1: 승인하되 고치지 않는다
- 기 2: 승인하되 고치지 않는다
- 기 3: 수리한다

## R1-94

### 원문
제목: 작업 계약 검토 수락에서 저자 독립성 검사를 두 곳이 서로 다른 범위로 중복 수행한다

### 위치
`.claude/skills/do-math/scripts/do_math/engine.py` 3948~3949행(`_apply`의 `task_contract_review` 분기).

### 기준
```
4. 같은 목적과 기능을 더 합리적인 로직으로 달성할 수 있는 과도한 비효율을 개선한다.
```

출처: `임시/do-math_검증_20260924_opus55/동결.md` 「목적 진술」 241행.

```
- 권한·입력·참조·증거·현재성 검사는 현행 계약에 맞게 유지한다. 조용한 기본값 보충으로 오류를 숨기지 않는다.
```

출처: 같은 파일 「불변식 목록」 260행.

### 영향
3948~3949행은 `task.get("producer_execution") == execution_id`만 검사한다. 불과 몇 행 뒤인 3954행이 호출하는 `planning.seal_contract_review`는 그 231~232행에서 같은 조건을 검사한다. 거기에 `author_execution_ids`까지 포함해 거부한다. 두 검사 사이의 3950~3953행은 계약 해시만 비교하고 상태를 바꾸지 않는다. 따라서 3948~3949행이 막는 입력은 모두 3954행에서도 막힌다.

같은 권한 규칙이 오류 문구가 다른 두 자리에 있다. 한쪽만 고치면 독립성 규칙이 갈라질 수 있고, 유지보수자는 어느 자리가 정본인지 판단해야 한다. 삭제하면 저자 독립성 거부는 `seal_contract_review` 한 곳에서 더 넓은 범위로 수행된다. 사본의 시험에는 `contract author cannot review its own contract` 문구를 검사하는 곳이 없다.

### 조각 1 — .claude/skills/do-math/scripts/do_math/engine.py 3948~3949행
원래:
```
            if task.get("producer_execution") == execution_id:
                raise ValueError("contract author cannot review its own contract")
```
대체:
```

```


### 판정
확정: 승인 · 승인기 [1, 2, 3] · 기각기 [] · 처분: 승인하되 고치지 않는다
최종 판정: 승인
최종 처분: 승인하되 고치지 않는다

### 근거
- 기 1: 승인하되 고치지 않는다
- 기 2: 승인하되 고치지 않는다
- 기 3: 수리한다

## R1-106

### 원문
제목: 아무 일도 하지 않는 SessionSlots.close()를 위해 호출부가 try/finally를 둔다

### 위치
.claude/skills/do-math/scripts/do_math/session_slots.py 364~367행(`close`). 호출부는 .claude/skills/do-math/scripts/do_math/scheduler.py 137~142행(`_session_resources`)과 584행(`_run_parallel`의 `finally`), .claude/skills/do-math/scripts/do_math/governance_engine.py 73~75행, .claude/skills/do-math/scripts/do_math/provider_engine.py 81~86행, .claude/skills/do-math/scripts/tests/test_claude_adapter.py 241행이다.

### 기준
임시/do-math_검증_20260924_opus55/동결.md 238행(목적 진술 1):

```
1. 더 이상 활용되지 않는 호환성 요소, 죽은 패러미터, 무시되는 설정과 유사한 잔재를 제거한다. 현재 입력의 유효성·권한·근거·현재성 검사는 유지한다.
```

.claude/skills/do-math/AGENTS.md 5행:

```
구판 호환을 위한 이전 구현·이름 별칭·래퍼·구형 인자·무시되는 설정·버전별 분기·마이그레이션 경로를 남기지 않는다.
```

### 영향
`SessionSlots.close()`의 본문은 `pass`뿐이다. 주석도 "The repository owns the writer lock and CAS; this view owns neither."라고 적는다. 클래스 설명(47~52행)도 이 뷰가 잠금·파일·카운터를 소유하지 않는다고 밝힌다. 그런데 호출부 네 곳은 이 빈 메서드를 부르려고 `try/finally`나 별도의 정리 행을 둔다. 읽는 사람은 슬롯 뷰가 해제해야 할 자원을 가진다고 오해한다. 같은 클래스를 만드는 다른 호출부(scheduler.py 471·490행, initialization.py 182행, scheduled_operator.py 284·494행)는 `close()`를 부르지 않는다. 그래서 정리 계약이 호출부마다 다르게 보인다.

수리는 빈 메서드와 그 의례를 모두 지운다. 동작은 바뀌지 않는다. 시험 test_claude_adapter.py 241행의 `slots.close()`도 함께 지운다. test_walkthrough_contract_repairs.py 270행의 `SimpleNamespace(close=lambda:None)` 대역은 호출되지 않는 속성을 하나 더 가질 뿐이므로 그대로 동작한다. 이 항목은 engine.py 1512행의 `_classic_provider_slots.close()`를 다루지 않는다. 그 행은 대입되지 않는 속성 아래에 있어 실행되지 않으며, 별도 항목 「한 번도 대입되지 않는 _classic_provider_slots를 세 곳에서 읽는다」가 지운다. 따라서 두 항목은 한쪽만 반영되어도 깨지지 않는다.

### 조각 1 — .claude/skills/do-math/scripts/do_math/session_slots.py 364~367행
원래:
```


    def close(self):
        pass  # The repository owns the writer lock and CAS; this view owns neither.
```
대체:
```

```

### 조각 2 — .claude/skills/do-math/scripts/do_math/scheduler.py 137~142행
원래:
```
        slots = SessionSlots( observer=True,
                             runtime=self.runtime, instance=self.instance)
        try:
            return slots.snapshot()
        finally:
            slots.close()
```
대체:
```
        return SessionSlots(self.runtime, self.instance, observer=True).snapshot()
```

### 조각 3 — .claude/skills/do-math/scripts/do_math/scheduler.py 584~584행
원래:
```
            self._slots.close()
```
대체:
```

```

### 조각 4 — .claude/skills/do-math/scripts/do_math/governance_engine.py 73~75행
원래:
```
        slots = SessionSlots( runtime=state, instance=result)
        try: slots.configure(candidate['session_limits'])
        finally: slots.close()
```
대체:
```
        SessionSlots(state, result).configure(candidate['session_limits'])
```

### 조각 5 — .claude/skills/do-math/scripts/do_math/provider_engine.py 81~86행
원래:
```
        observer = SessionSlots( observer=True,
                                runtime=self.runtime, instance=self.instance)
        try:
            return observer.provider_snapshot()
        finally:
            observer.close()
```
대체:
```
        return SessionSlots(self.runtime, self.instance, observer=True).provider_snapshot()
```

### 조각 6 — .claude/skills/do-math/scripts/tests/test_claude_adapter.py 241~241행
원래:
```
            slots.close()
```
대체:
```

```


### 판정
확정: 승인 · 승인기 [1, 2, 3] · 기각기 [] · 처분: 승인하되 고치지 않는다
최종 판정: 승인
최종 처분: 승인하되 고치지 않는다

### 근거
- 기 1: 승인하되 고치지 않는다
- 기 2: 승인하되 고치지 않는다
- 기 3: 수리한다

## R1-110

### 원문
제목: write_source_catalog의 도달할 수 없는 소속 검사

### 위치
.claude/skills/do-math/scripts/do_math/context_store.py 233~234행.

### 기준
임시/do-math_검증_20260924_opus55/동결.md 238행(목적 진술 1):

```
1. 더 이상 활용되지 않는 호환성 요소, 죽은 패러미터, 무시되는 설정과 유사한 잔재를 제거한다. 현재 입력의 유효성·권한·근거·현재성 검사는 유지한다.
```

### 영향
232행의 `for key in sorted(context):`는 `context`의 키를 순회한다. 반복 본문은 `context`를 바꾸지 않는다. 그러므로 233~234행의 `if key not in context: continue`는 참이 될 수 없는 검사다. 읽는 사람은 순회 중에 카탈로그 대상이 빠질 수 있다고 오해하고, 그런 경로가 어디인지 찾게 된다. 지워도 동작은 바뀌지 않는다.

### 조각 1 — .claude/skills/do-math/scripts/do_math/context_store.py 233~234행
원래:
```
        if key not in context:
            continue
```
대체:
```

```


### 판정
확정: 승인 · 승인기 [1, 2, 3] · 기각기 [] · 처분: 승인하되 고치지 않는다
최종 판정: 승인
최종 처분: 승인하되 고치지 않는다

### 근거
- 기 1: 승인하되 고치지 않는다
- 기 2: 승인하되 고치지 않는다
- 기 3: 승인하되 고치지 않는다

## R1-M1

### 원문
구성: R1-02 · R1-92

### 위치
`.claude/skills/do-math/scripts/do_math/question_engine.py` 57~58행이다. 이 두 행은 `_record_output_questions` 함수 안에서 의도 해석 역할의 기본 소유자를 `user`로 바꾸는 분기다. 같은 함수의 40~41행이 이 역할을 먼저 반환시킨다.

### 기준
`임시/do-math_검증_20260924_opus55/동결.md` 「목적 진술」 238행:

```
1. 더 이상 활용되지 않는 호환성 요소, 죽은 패러미터, 무시되는 설정과 유사한 잔재를 제거한다. 현재 입력의 유효성·권한·근거·현재성 검사는 유지한다.
```

### 영향
`_record_output_questions`는 40~41행에서 `action.get("role") == "intent_interpretation"`이면 곧바로 반환한다. 39행 주석도 의도 해석 질문은 검사 뒤 `governance.apply_import`만 게시한다고 적는다. 따라서 57행의 조건은 어떤 입력에서도 참이 될 수 없고, 57~58행은 실행되지 않는 잔재다. 호출부도 같은 결론을 준다. `engine.py`의 `_apply`는 3834행에서 의도 해석 역할을 걸러 낸 뒤에만 3835행에서 이 함수를 부른다. `review_engine.py` 1048행은 검토 주기의 생산자 산출을 넘긴다. 이 분기를 삭제해도 동작은 바뀌지 않는다. 그대로 두면 읽는 사람은 의도 해석의 `needs_clarification` 질문이 이 경로에서 사용자 소유로 게시된다고 오해하고, 사용자 질문의 소유 경계를 두 곳에서 찾게 된다. 실제 게시 경로는 통치 편입 하나뿐이다.

### 근거
두 구성 항목은 위치, 기준, 수리가 같다. 기준 인용은 동결문 238행에서 실재를 확인했다. 사본에서 40~41행의 조기 반환과 39행 주석, 57~58행의 축자를 확인했다. R1-92가 든 호출부 근거도 사본에서 확인해 옮겼다. `engine.py` 3834행은 `role != "intent_interpretation"` 조건 행이고, 실제 호출은 3835행이다. `review_engine.py` 1048행의 호출도 실재한다. R1-92의 "동일성 검토 산출만 넘긴다"라는 표현은 사본의 해당 행만으로는 확인하지 못해 옮기지 않고, 검토 주기의 생산자 산출을 넘긴다고만 적었다. 이 사실은 40~41행의 조기 반환만으로도 결론이 서므로 근거의 강도를 바꾸지 않는다. 두 항목 사이에 어긋남은 없다. 구성 항목의 대체 블록은 빈 줄 하나를 담고 있었다. 조각 계약에서 빈 줄 대체는 삭제와 구별되지 않으므로, 의도대로 빈 블록인 삭제로 썼다. 지급 키 밖의 새 결함은 보지 못했다.

### 조각 1 — .claude/skills/do-math/scripts/do_math/question_engine.py 57~58행
원래:
```
        if action["role"] == "intent_interpretation" and output.get("needs_clarification"):
            default_owner = "user"
```
대체:
```

```


### 판정
확정: 승인 · 승인기 [1, 2, 3] · 기각기 [] · 처분: 승인하되 고치지 않는다
최종 판정: 승인
최종 처분: 승인하되 고치지 않는다

### 근거
- 기 1: 승인하되 고치지 않는다
- 기 2: 승인하되 고치지 않는다
- 기 3: 수리한다

## R1-M2

### 원문
구성: R1-06 · R1-91

### 위치
`.claude/skills/do-math/scripts/do_math/engine.py` 4330~4333행 `_goal_basis_key`, 4332행의 필드 목록. 과제 계약의 기대 산출 필드는 `expected`다. 사본의 `scripts/do_math/planning.py` 13행 `CONTRACT_FIELDS`가 이 이름을 쓴다.

### 기준
출처: `임시/do-math_검증_20260924_opus55/동결.md` 「목적 진술」 239행.

```
2. 생산자와 소비자 사이의 계약 미스매치를 수리한다. 구현·호출부·스키마·시험·예시·문서가 같은 현재 계약을 사용하게 한다.
```

### 영향
`_goal_basis_key`는 과제마다 고른 필드를 해시해 목표 감사의 기준 키를 만든다. 사본 전역에서 `expected_outputs`는 4332행에만 나온다. 그래서 과제마다 `expected_outputs: null`이 해시되고, 과제 계약의 실제 필드 `expected`(`outputs`와 `research_change`를 담는 객체)는 기준 키에 들어가지 않는다. 이 키는 과제 계약의 현행 필드 이름과 다른 이름을 결박하므로 생산자와 소비자 사이의 계약 미스매치다.

다만 실제로 드러나는 피해는 제한적이다. 과제 계약을 개정하면 `contracts.py` 57행이 `revision`을 올리고, `revision`은 이미 기준 키에 들어 있다. 따라서 `expected`만 바뀌고 `revision`은 그대로인 경로는 확인되지 않았다. 목표 감사가 낡은 입력을 수락한 사례도 확인되지 않았다. 남는 피해는 두 가지다. 하나는 `revision` 증가에 기대지 않고 `expected` 자체를 결박하려던 이 필드 목록의 의도가 무효라는 것이다. 다른 하나는 목표 감사의 현재성 근거를 추적하는 유지보수자가 존재하지 않는 필드를 결박 대상으로 믿게 된다는 것이다.

### 근거
두 구성 항목은 위치, 기준, 수리가 같다. 수리는 4332행의 `"expected_outputs"`를 `"expected"`로 바꾸는 것이다. 사본에서 다음을 확인했다.

- 4332행의 축자와, `expected_outputs`가 사본 전역에서 이 행에만 나온다는 사실
- `planning.py` 13행 `CONTRACT_FIELDS`에 `expected`가 있다는 사실
- `governance_engine.py` 419행의 `action['basis'] != self._goal_basis_key()` 검사
- 동결문 239행 기준 인용의 실재

두 구성 항목은 영향의 강도에서 어긋난다. R1-06은 `expected`가 개정되어도 기준 키가 바뀌지 않아 봉인된 감사 슬롯이 419행 검사를 통과한다고 주장했다. R1-91은 개정 때 `revision`이 오르므로 그런 경로를 찾지 못했다고 적었다. 사본의 `contracts.py` 51~58행을 보면 기존 과제를 개정할 때 `revision = previous["revision"] + 1`이 실행되고, `revision`은 기준 키 필드에 포함되어 있다. 따라서 근거가 더 강한 R1-91의 한정된 영향을 취하고, R1-06의 우회 통과 주장은 버렸다.

R1-06이 위치의 근거로 든 `test_redesign_TASKS.py` 51행, `research_fixtures.candidate`, 과제 스키마는 대조하지 않았다. R1-91이 추가로 든 `academic_engine.py` 97행과 `계약/작업-계약-검토.md` 27행도 대조하지 않았다. 대조한 `CONTRACT_FIELDS` 하나로 현행 필드 이름이 성립하므로 병합 항목에는 이것만 옮겼다. 지급 키 밖에서 새 결함은 보지 못했다.

### 조각 1 — .claude/skills/do-math/scripts/do_math/engine.py 4332~4332행
원래:
```
                  ("id", "revision", "question", "scope", "completion_obligations", "expected_outputs", "results", "status")}
```
대체:
```
                  ("id", "revision", "question", "scope", "completion_obligations", "expected", "results", "status")}
```


### 판정
확정: 승인 · 승인기 [1, 2, 3] · 기각기 [] · 처분: 승인하되 고치지 않는다
최종 판정: 승인
최종 처분: 승인하되 고치지 않는다

### 근거
- 기 1: 승인하되 고치지 않는다
- 기 2: 승인하되 고치지 않는다
- 기 3: 승인하되 고치지 않는다

## R1-M4

### 원문
구성: R1-09 · R1-109

### 위치
.claude/skills/do-math/scripts/do_math/scheduler.py 533행. `_run_parallel`의 빈 큐 분기에 있는 `from .questions import open_links` 한 행이다.

### 기준
임시/do-math_검증_20260924_opus55/동결.md 「목적 진술」 238행:

```
1. 더 이상 활용되지 않는 호환성 요소, 죽은 패러미터, 무시되는 설정과 유사한 잔재를 제거한다. 현재 입력의 유효성·권한·근거·현재성 검사는 유지한다.
```

### 영향
533행은 `open_links`를 import하지만 그 이름을 쓰지 않는다. scheduler.py 전체에서 `open_links`가 나오는 곳은 이 행뿐이다. 바로 아래 534~536행 주석은 빈 큐나 오래된 순환 계수가 새 작업을 만들 권한이 아니며, 그 판단은 `_refresh_readiness`가 맡는다고 적는다. 이 분기가 실제로 하는 일은 상태를 `waiting`으로 두는 것뿐이다. 따라서 이 import는 예전에 이 분기에서 열린 질문을 조회하던 경로의 잔재다.

이 행을 남겨 두면 읽는 사람은 이 분기가 질문 대기를 여기서 다시 확인한다고 오해한다. 또 루프가 빈 큐 분기에 들어갈 때마다 쓸모없는 import 문이 실행된다. 이 행을 지워도 동작은 바뀌지 않는다. 입력의 유효성·권한·근거·현재성 검사에도 닿지 않는다.

### 근거
두 구성 항목(R1-09, R1-109)은 같은 행, 같은 기준, 같은 삭제 수리를 제시하며 서로 어긋나지 않는다. 기준 인용은 동결문 238행에서 축자로 일치함을 확인했다. 사본의 scheduler.py를 grep해 `open_links`가 533행에만 나옴을 확인했다. R1-09의 「scheduler.py 안에서 533행 외에 쓰이지 않는다」가 R1-109의 「`_run_parallel` 본문 안」보다 범위가 넓어서 R1-09의 표현을 취했다. 534~536행 주석 내용은 사본에서 대조해 R1-109의 서술을 취했다. 두 구성 항목의 대체 블록은 빈 줄 하나를 담고 있었다. `계약/조각.md` 3절은 빈 줄 하나로 바꾸는 대체가 삭제와 구별되지 않는다고 적는다. 두 항목의 취지가 행 삭제이므로 병합 조각은 빈 블록, 곧 삭제로 썼다. 지급 키 밖의 결함은 발견하지 못했다.

### 조각 1 — .claude/skills/do-math/scripts/do_math/scheduler.py 533~533행
원래:
```
                    from .questions import open_links
```
대체:
```

```


### 판정
확정: 승인 · 승인기 [1, 2, 3] · 기각기 [] · 처분: 승인하되 고치지 않는다
최종 판정: 승인
최종 처분: 승인하되 고치지 않는다

### 근거
- 기 1: 승인하되 고치지 않는다
- 기 2: 승인하되 고치지 않는다
- 기 3: 승인하되 고치지 않는다

## R1-M5

### 원문
구성: R1-15 · R1-26

### 위치
`.claude/skills/do-math/scripts/do_math/state_checks.py`의 두 곳이다. 197행은 `preparation_selection` 영역의 기록군 목록이고, 423~428행은 `runtime['plans']`를 도는 계획 처분 검사다.

### 기준
`임시/do-math_검증_20260924_opus55/동결.md` 238행(목적 진술 1):

```text
1. 더 이상 활용되지 않는 호환성 요소, 죽은 패러미터, 무시되는 설정과 유사한 잔재를 제거한다. 현재 입력의 유효성·권한·근거·현재성 검사는 유지한다.
```

`임시/do-math_검증_20260924_opus55/동결.md` 260행(불변식):

```text
- 권한·입력·참조·증거·현재성 검사는 현행 계약에 맞게 유지한다. 조용한 기본값 보충으로 오류를 숨기지 않는다.
```

### 영향
`plans`와 `preparations`는 등록된 저장 기록군이 아니며, 사본 전체에서 이 두 런타임 최상위 기록군을 만드는 생산자도 없다. `integration.py`·`engine.py`에 나오는 `request["plans"]`는 영향 검토 요청 안의 필드일 뿐 런타임 최상위 기록군이 아니다. 따라서 197행 목록의 두 이름은 204~217행의 스키마 검사에서 언제나 `name not in container`로 건너뛰어지고, 423~428행의 반복문은 한 번도 돌지 않는다.

연구 계획의 전 후보 처분 검사는 실제로 수신 경계에서 이루어진다. `planning.py` 256~260행이 `validate_plan_dispositions`를 호출한다. 그런데도 남아 있는 죽은 검사는 상태 점검 결과나 코드를 읽는 사람에게 저장된 계획 기록을 점검한다는 인상을 준다. 그 결과 존재하지 않는 기록군을 기준으로 점검을 확장할 위험이 생긴다.

수리한 뒤에도 이 영역이 실제로 수행하는 검사는 그대로 남는다. 남는 검사는 실시간 준비·선택 실행의 단일성, 대기열 작업의 작업 참조, 보충 조사 요청의 소유다. 따라서 불변식이 요구하는 현행 검사는 줄어들지 않는다.

### 근거
두 구성 항목은 위치, 결함 기제, 조각 두 개의 좌표와 대체 문면이 모두 같으므로 같은 결함을 가리킨다. 서로 어긋나는 곳은 없다.

R1-15에서는 생산자 부재와 영향 검토 요청 필드의 구별, 목적 진술 1의 전문 인용을 취했다. R1-26에서는 불변식 260행 인용, `planning.py` 256~260행이라는 수신 경계 위치, 점검 확장 오해라는 영향을 취했다. R1-26은 불변식 260행의 앞 문장만 인용했는데, 이 병합 항목은 원문 행 전체를 인용했다. R1-15가 graphify 조회로 호출자를 찾았다는 서술은 결함의 근거가 아니므로 옮기지 않았다.

사본에서 다음을 확인했다.
- 197행과 423~428행의 축자.
- 204~217행의 `name not in container` 건너뛰기.
- `validate_plan_dispositions`의 호출처가 `planning.py` 260행과 `state_checks.py` 426행뿐이라는 것.
- `'plans'` 기록군을 만드는 생산자가 없다는 것.

197행의 대체 `()`는 빈 기록군 목록이 된다. 이 목록이 204행 반복에서 아무 일도 하지 않으므로 영역 분기와 사전 키 구조는 유지된다. 423~428행의 삭제 뒤에는 422행의 `run(...)`이 `elif` 본문의 끝이 되므로 문법상 문제가 없다.

지급 키 밖에서 새 결함은 발견하지 않았다.

### 조각 1 — .claude/skills/do-math/scripts/do_math/state_checks.py 197~197행
원래:
```
        'preparation_selection': ('plans', 'preparations'),
```
대체:
```
        'preparation_selection': (),
```

### 조각 2 — .claude/skills/do-math/scripts/do_math/state_checks.py 423~428행
원래:
```
        for plan in runtime.get('plans', []):
            from .task_contracts import validate_plan_dispositions
            if isinstance(plan.get('ready_ids'), list):
                run('plan all-candidate dispositions', lambda p=plan: validate_plan_dispositions(p, runtime.get('tasks', {}), p['ready_ids']), plan.get('id', 'plan'))
            else:
                omitted('plan fixed candidate population')
```
대체:
```

```


### 판정
확정: 승인 · 승인기 [1, 2, 3] · 기각기 [] · 처분: 승인하되 고치지 않는다
최종 판정: 승인
최종 처분: 승인하되 고치지 않는다

### 근거
- 기 1: 승인하되 고치지 않는다
- 기 2: 승인하되 고치지 않는다
- 기 3: 수리한다

## R1-M9

### 원문
구성: R1-39 · R1-76

### 위치
`.claude/skills/do-math/scripts/do_math/contracts.py` 189행의 `SCHEMAS["intent_interpretation"]` 항목과, 196행에서 `schema_for`가 역할 이름을 검사하는 조건이다.

### 기준
`임시/do-math_검증_20260924_opus55/동결.md` 239행(목적 진술 2):

```text
2. 생산자와 소비자 사이의 계약 미스매치를 수리한다. 구현·호출부·스키마·시험·예시·문서가 같은 현재 계약을 사용하게 한다.
```

`.claude/skills/do-math/AGENTS.md` 5행:

```text
- 설계를 바꾸면 구현·호출부·스키마·테스트·예시·문서를 같은 변경에서 새 계약으로 교체한다. 구판 호환을 위한 이전 구현·이름 별칭·래퍼·구형 인자·무시되는 설정·버전별 분기·마이그레이션 경로를 남기지 않는다.
```

### 영향
`SCHEMAS["intent_interpretation"]`은 `interpretation`, `requested_changes`, `needs_clarification` 필드로 된 응답 계약을 선언한다. 하지만 `schema_for`는 198~200행에서, `action_schema`는 215~217행에서 이 역할에 언제나 `governance.interpretation_schema`를 반환한다. 따라서 이 사전 값은 반환되지 않고, 196행의 역할 소속 검사에 그 키만 쓰인다. 사본 전체에서 `SCHEMAS`를 참조하는 파일은 contracts.py 하나뿐이다. 역할 응답 계약의 정본 자리인 contracts.py를 읽는 사람과 도구는 현행 의도 해석 계약에 없는 옛 형식을 응답 계약으로 오인하게 된다. 수리하면 역할 소속은 같은 열 개 역할을 담은 `ROLES`(18~22행)로 검사되고, 의도 해석의 응답 계약은 거버넌스 스키마 하나로 남는다.

### 근거
두 구성 항목은 위치, 기준, 조각 두 개의 원래·대체 문면이 서로 같다. 그래서 어긋나는 부분이 없고, 취지를 하나로 합쳤다. 사본에서 확인한 사실은 다음과 같다. 189행과 196행의 축자가 일치한다. 198~200행의 `schema_for`와 215~217행의 `action_schema`는 거버넌스 스키마를 반환한다. `ROLES`(18~22행)는 `intent_interpretation`을 포함한 열 개 역할을 담으며, `SCHEMAS`의 키 집합과 같다. `SCHEMAS`를 참조하는 곳은 사본 전체에서 contracts.py 안(172·196·201행)뿐이다. 기준 인용 두 개도 원문 행과 축자가 일치한다.

R1-39는 동결문 목적 진술 2와 AGENTS.md 5행의 일부를 인용했고, R1-76은 AGENTS.md 5행 전문을 인용했다. 병합 항목은 두 원문을 모두 온전한 행으로 옮겼다. R1-76이 든 "import 때 `with_integration_schema`·`identify_schema` 계산만 치른다"는 부수 비용 서술은 이 병합에서 직접 확인하지 않았으므로 영향에 옮기지 않았다. 결함의 성립은 이 서술 없이도 유지된다. 두 항목의 조각 1 대체 블록에는 빈 줄 하나가 들어 있었다. 이를 빈 블록으로 바꾸어, 조각 규약이 정한 삭제로 명확히 표현했다. 이렇게 하면 189행이 빈 줄 없이 제거되어 사전 리터럴이 그대로 이어진다. 196행 다음의 `copy.deepcopy(SCHEMAS[role])`(201행)는 그대로 유효하다. `intent_interpretation`은 200행에서 먼저 반환되므로 삭제된 키를 조회하지 않는다.

### 조각 1 — .claude/skills/do-math/scripts/do_math/contracts.py 189~189행
원래:
```
    "intent_interpretation": _schema({"interpretation": STRING, "requested_changes": STRINGS, "needs_clarification": {"type": "boolean"}}),
```
대체:
```

```

### 조각 2 — .claude/skills/do-math/scripts/do_math/contracts.py 196~196행
원래:
```
    if role not in SCHEMAS:
```
대체:
```
    if role not in ROLES:
```


### 판정
확정: 승인 · 승인기 [1, 2, 3] · 기각기 [] · 처분: 승인하되 고치지 않는다
최종 판정: 승인
최종 처분: 승인하되 고치지 않는다

### 근거
- 기 1: 승인하되 고치지 않는다
- 기 2: 승인하되 고치지 않는다
- 기 3: 수리한다

## R1-M12

### 원문
구성: R1-48 · R1-108

### 위치
`.claude/skills/do-math/scripts/do_math/git_store.py` 290~292행. 호출자가 없는 `GitStateStore._subtree_oid` 메서드와 그 뒤의 빈 줄이다.

### 기준
임시/do-math_검증_20260924_opus55/동결.md 238행(목적 진술 1):

```
1. 더 이상 활용되지 않는 호환성 요소, 죽은 패러미터, 무시되는 설정과 유사한 잔재를 제거한다. 현재 입력의 유효성·권한·근거·현재성 검사는 유지한다.
```

### 영향
`_subtree_oid(commit_or_tree, name)`는 `_subtree_oids(commit_or_tree, (name,))[name]`를 감싼 한 줄짜리 래퍼다. do-math 스킬 전체를 시험 파일까지 포함해 검색하면 이 이름은 290행의 정의에만 나온다. 저장 계층의 실제 호출자는 모두 복수형을 쓴다. 193행과 219행은 `_subtree_oids`로 research·runtime 두 하위 트리를 한 번에 읽고, 105행은 `_parse_subtree_oids`를 쓴다. 따라서 이 래퍼는 쓰이지 않는 두 번째 진입점으로만 남아 저장 경계의 읽기 표면을 넓힌다. 지워도 동작은 바뀌지 않는다. `_subtree_oids`가 하는 이름 제한과 OID 검증은 그대로 남으므로, 목적 진술 1이 유지를 요구하는 입력 검사도 잃지 않는다.

### 근거
두 구성 항목(R1-48, R1-108)은 같은 위치와 같은 기준을 들고, 같은 삭제 조각을 제시한다. 서로 어긋나는 데가 없어 둘의 근거를 합쳤다. 사본을 대조한 결과는 다음과 같다. 290~292행의 축자가 지급 조각과 일치한다. 기준 인용이 동결문 238행에 실재한다. `_subtree_oid\b`를 검색하면 사본과 원본 모두 정의 한 곳에만 걸린다(바이너리 캐시 제외). 105·193·219행의 호출도 확인했다. R1-108이 인용한 graphify 질의 결과는 다시 실행하지 않았고, 대신 rg 결과로 같은 결론을 확인했다. 조각은 290~292행(정의 두 줄과 뒤따르는 빈 줄)을 삭제한다. 삭제 뒤에는 289행의 빈 줄 하나가 앞 메서드의 끝과 `_subtree_oids` 사이에 남으므로, 메서드 사이의 빈 줄 규약이 유지된다. 구성 항목의 대체 블록에는 빈 줄 하나가 들어 있지만, 조각 계약상 이는 삭제와 구별되지 않으므로 빈 블록으로 썼다. 지급 키 밖의 새 결함은 발견하지 못했다.

### 조각 1 — .claude/skills/do-math/scripts/do_math/git_store.py 290~292행
원래:
```
    def _subtree_oid(self, commit_or_tree: str, name: str) -> str:
        return self._subtree_oids(commit_or_tree, (name,))[name]

```
대체:
```

```


### 판정
확정: 승인 · 승인기 [1, 2, 3] · 기각기 [] · 처분: 승인하되 고치지 않는다
최종 판정: 승인
최종 처분: 승인하되 고치지 않는다

### 근거
- 기 1: 승인하되 고치지 않는다
- 기 2: 승인하되 고치지 않는다
- 기 3: 승인하되 고치지 않는다

## R1-M13

### 원문
구성: R1-60 · R1-107

### 위치
.claude/skills/do-math/scripts/do_math/session_slots.py 84~86행. `SessionSlots.admission_available` 메서드와 그 뒤의 빈 줄이다.

### 기준
출처는 임시/do-math_검증_20260924_opus55/동결.md 「목적 진술」 238행이다.

```
1. 더 이상 활용되지 않는 호환성 요소, 죽은 패러미터, 무시되는 설정과 유사한 잔재를 제거한다. 현재 입력의 유효성·권한·근거·현재성 검사는 유지한다.
```

### 영향
`admission_available(profile)`은 `admission_check(profile)['allowed']`만 돌려주는 한 줄 래퍼다. 사본의 do-math 전체(시험 포함)에서 이 이름은 정의에만 나온다. 입장 판정을 쓰는 곳은 모두 `admission_check`를 직접 부른다. scheduler.py 471·490행은 대기 사유(`wait`)까지 쓰고, 시험도 같은 메서드를 부른다. 이 래퍼가 남으면 입장 판정의 공개 입구가 둘로 보인다. 그러면 새 호출자가 대기 사유를 버리고 불리언만으로 배정을 판단하는 경로를 만들 여지가 생긴다. 호출자가 없으므로 지워도 동작은 바뀌지 않는다. 목적 진술 1이 유지하라고 한 검사는 `admission_check`에 그대로 남는다.

### 근거
두 구성 항목의 위치·기준·영향·조각은 같다. 기준 인용이 동결문 238행에 축자로 실재함을 확인했다. 사본에서 `admission_available`과 `admission_check`를 검색했다. 앞의 이름은 session_slots.py 84·85행에만 나온다. 뒤의 이름은 scheduler.py 471·490행, test_redesign_PROFILES.py, test_repair_plan.py에서 불린다. 따라서 두 항목의 사실 주장이 성립한다. R1-107이 든 graphify 호출 간선 근거는 사본 검색과 같은 결론이므로 따로 옮기지 않았다. 구성 항목 사이에 어긋남은 없다.

두 항목의 대체 블록은 빈 줄 하나였다. 조각 계약은 빈 줄 하나로의 대체를 삭제와 구별하지 않는다. 그래서 대체를 빈 블록, 곧 삭제로 썼다. 삭제 뒤에는 82행의 `return`과 87행의 `def configure` 사이에 83행의 빈 줄 하나가 남는다. 따라서 메서드 사이 간격이 유지된다. 지급 키 밖의 새 결함은 보지 못했다.

### 조각 1 — .claude/skills/do-math/scripts/do_math/session_slots.py 84~86행
원래:
```
    def admission_available(self, profile):
        return self.admission_check(profile)['allowed']

```
대체:
```

```


### 판정
확정: 승인 · 승인기 [1, 2, 3] · 기각기 [] · 처분: 승인하되 고치지 않는다
최종 판정: 승인
최종 처분: 승인하되 고치지 않는다

### 근거
- 기 1: 승인하되 고치지 않는다
- 기 2: 승인하되 고치지 않는다
- 기 3: 승인하되 고치지 않는다

## R1-M15

### 원문
구성: R1-90 · R1-105

### 위치
`.claude/skills/do-math/scripts/do_math/engine.py` 814~816행(`_save`), 1443~1445행(`status`), 1511~1513행(`run`의 `finally`).

### 기준
동결문의 목적 진술 1은 더 이상 쓰이지 않는 잔재를 제거하라고 한다.

```
1. 더 이상 활용되지 않는 호환성 요소, 죽은 패러미터, 무시되는 설정과 유사한 잔재를 제거한다. 현재 입력의 유효성·권한·근거·현재성 검사는 유지한다.
```

출처: `임시/do-math_검증_20260924_opus55/동결.md` 「목적 진술」 238행.

do-math의 프리알파 개발 원칙도 구판 호환용 구현과 래퍼를 남기지 말라고 한다.

```
- 설계를 바꾸면 구현·호출부·스키마·테스트·예시·문서를 같은 변경에서 새 계약으로 교체한다. 구판 호환을 위한 이전 구현·이름 별칭·래퍼·구형 인자·무시되는 설정·버전별 분기·마이그레이션 경로를 남기지 않는다.
```

출처: `.claude/skills/do-math/AGENTS.md` 5행.

### 영향
사본 전역에서 `_classic_provider_slots`는 engine.py의 세 자리에만 나온다. 814행과 1443행은 `getattr(..., None)`으로 읽기만 한다. 1511~1513행은 값이 `None`이 아닐 때만 닫고 다시 `None`을 대입한다. 이 속성에 슬롯 관리자를 대입하는 곳은 없으므로, 세 분기는 언제나 `None`을 보고 아무 일도 하지 않는다. 폐기된 이전 공급자 슬롯 경로의 잔재다.

동작 결과는 달라지지 않는다. 그러나 코드를 읽는 유지보수자와 수리자는 현재 슬롯 뷰가 `self._slots`와 "고전" 공급자 슬롯 둘이라고 오해한다. `run()`의 `finally`는 존재하지 않는 자원을 닫는 정리 절차처럼 읽힌다. 그 결과 슬롯의 수명과 반환을 추적할 때 존재하지 않는 경로까지 조사하게 된다. 실제 슬롯 뷰는 `self._slots` 하나다.

수리는 두 동기화 지점이 `self._slots`만 다루게 하고 `run()`의 죽은 정리 세 행을 지운다. `hasattr(slots, "runtime")` 가드는 그대로 두므로, `runtime` 속성이 없는 대역 객체로 `_slots`를 바꾸는 시험도 이전과 같게 처리된다. 1513행을 지운 뒤에도 `finally`에는 1510행의 `self._executor_running = False`가 남아 문법상 유효하다.

### 근거
두 구성 항목은 위치·결함 판정·조각 세 개의 대체 문면이 모두 일치한다. 어긋남은 없다.

- 기준: R1-90의 두 인용(동결문 238행, do-math AGENTS.md 5행)을 모두 취했다. 둘 다 기준 원문에서 축자 실재를 확인했다. R1-105의 인용은 R1-90의 동결문 인용과 같다.
- 영향: 사본 전역을 검색해 `_classic_provider_slots`가 814·1443·1511~1513행에만 나오고 대입은 1513행의 `None` 대입뿐임을 다시 확인했다. R1-90의 오해 경로 서술과 R1-105의 `self._slots` 단일성·시험 대역 서술을 취했다. R1-105가 인용한 provider_engine.py docstring, scheduler.py 497행, provider_engine.py 71행, test_walkthrough_contract_repairs.py 270행은 판정에 꼭 필요한 근거가 아니다. 이 병합에서 행 위치를 다시 확인하지 않았으므로 행 번호와 함께 옮기지 않았다.
- 조각 3: 두 구성 항목은 대체 블록 안에 빈 줄 하나를 두었다. 조각 계약상 이 형태는 빈 줄 하나로 바꾸는 대체처럼 읽힐 수 있다. 의도는 세 행 삭제이므로 빈 블록으로 썼다.
- 지급 키 밖의 새 결함은 발견하지 않았다.

### 조각 1 — .claude/skills/do-math/scripts/do_math/engine.py 814~816행
원래:
```
        for slots in (getattr(self, "_slots", None), getattr(self, "_classic_provider_slots", None)):
            if slots is not None and hasattr(slots, "runtime"):
                slots.runtime, slots.instance = self.runtime, self.instance
```
대체:
```
        slots = getattr(self, "_slots", None)
        if slots is not None and hasattr(slots, "runtime"):
            slots.runtime, slots.instance = self.runtime, self.instance
```

### 조각 2 — .claude/skills/do-math/scripts/do_math/engine.py 1443~1445행
원래:
```
        for slots in (getattr(self, "_slots", None), getattr(self, "_classic_provider_slots", None)):
            if slots is not None and hasattr(slots, "runtime"):
                slots.runtime, slots.instance = self.runtime, self.instance
```
대체:
```
        slots = getattr(self, "_slots", None)
        if slots is not None and hasattr(slots, "runtime"):
            slots.runtime, slots.instance = self.runtime, self.instance
```

### 조각 3 — .claude/skills/do-math/scripts/do_math/engine.py 1511~1513행
원래:
```
            if getattr(self, "_classic_provider_slots", None) is not None:
                self._classic_provider_slots.close()
                self._classic_provider_slots = None
```
대체:
```

```


### 판정
확정: 승인 · 승인기 [1, 2, 3] · 기각기 [] · 처분: 승인하되 고치지 않는다
최종 판정: 승인
최종 처분: 승인하되 고치지 않는다

### 근거
- 기 1: 승인하되 고치지 않는다
- 기 2: 승인하되 고치지 않는다
- 기 3: 수리한다
