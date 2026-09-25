---
유형: 기각보관
출처: do-math-opus-20260925
라운드: 1
항목: 17
---

# 기각 보관 — do-math-opus-20260925 라운드1

## R1-03

### 원문
제목: CLI 제어 명령이 결과를 버리는 전체 status 재구성을 매번 수행한다

### 위치
- `.claude/skills/do-math/scripts/do_math/cli.py` 249행: `_control`이 `engine.process_controls()`의 반환값을 버린다.
- `.claude/skills/do-math/scripts/do_math/engine.py` 1523~1535행: `process_controls`는 제어를 적용한 뒤 끝에서 `self.status()`를 계산해 반환한다.

### 기준
`임시/do-math_검증_20260925_opus/동결.md` 261행(목적 진술):

```text
반복 검증·전체 상태 복사·파일 접근·Git 호출을 추적하고 불필요한 비용을 줄인다. 검증 경계의 의미와 오류 처분을 유지하며 측정하지 않은 성능 배율은 주장하지 않는다.
```

### 영향
공개 제어 명령 전건이 `cli._control`을 지난다. 해당 명령은 `pause`·`resume`·`close`·`input`·`configure`·`request`·`decision`·`knowledge`·`trust`·`external`·`conversation`·`source`·`quiesce`·`release-quiesce`와 `operator hold`·`release`다.

`_control`은 적용 뒤 `engine.control_result`(Git rev-list, engine.py 251~264행)로 영수증만 만든다. 그런데 `process_controls` 끝의 `self.status()`(1537~1602행)가 매번 다음 작업을 모두 수행하고, 그 결과는 cli.py 249행에서 버려진다.

- 상태 재적재
- `inspect_state` 전 영역 검사와 그 artifact 읽기(1564~1566행)
- `planning.research_wake_reasons`
- 제출 검사 요약의 check artifact 읽기(4719~4720행)
- inbox JSON 재열람(1581행)

이 비용은 실행·artifact 수에 비례해 커진다. 배율은 측정하지 않았다.

조각은 적용 부분을 `apply_controls`로 분리하고 CLI만 그것을 부른다. `process_controls`는 적용 뒤 status를 반환하는 기존 계약을 유지한다. `process_controls`를 부르는 곳은 cli.py 249행과 시험 60여 곳이며(grep), 시험은 반환된 status를 계속 쓴다(test_controls.py 39·41·43·70·82행). writer lock 경합 처리(cli.py 251~252행의 `GitStateStoreLockError`)는 `apply_controls` 안에서 그대로 발생한다. `control_result`는 `_save`로 갱신된 같은 head를 읽으므로 영수증도 달라지지 않는다. graphify `affected scripts/do_math/cli.py`는 engine.py, control_transport.py, context_store.py, decision_engine.py, delegations.py를 가리키지만, 이들은 `_control`을 부르지 않는다.

### 조각 1 — .claude/skills/do-math/scripts/do_math/engine.py 1523~1535행
원래:
```
    @engine_operation('controls')
    def process_controls(self) -> dict:
        """Apply queued user controls under the sole writer lock, without AI."""
        with self.store.writer_lock():
            self.head, self.instance, self.runtime = self.store.load()
            self._inspect_before_write()
            self._saved_state = self._state_signature()
            self.instance = knowledge_io.ensure_ontology(self.instance)
            self._controls()
            _, persisted_instance, persisted_runtime = self.store.load(self.head)
            if self.instance != persisted_instance or self.runtime != persisted_runtime:
                self._save()
        return self.status()
```
대체:
```
    @engine_operation('controls')
    def apply_controls(self) -> None:
        """Apply queued user controls under the sole writer lock, without AI."""
        with self.store.writer_lock():
            self.head, self.instance, self.runtime = self.store.load()
            self._inspect_before_write()
            self._saved_state = self._state_signature()
            self.instance = knowledge_io.ensure_ontology(self.instance)
            self._controls()
            _, persisted_instance, persisted_runtime = self.store.load(self.head)
            if self.instance != persisted_instance or self.runtime != persisted_runtime:
                self._save()

    def process_controls(self) -> dict:
        """Apply queued user controls, then report the published status."""
        self.apply_controls()
        return self.status()
```

### 조각 2 — .claude/skills/do-math/scripts/do_math/cli.py 249~249행
원래:
```
        engine.process_controls()
```
대체:
```
        engine.apply_controls()
```


### 판정
확정: 기각 · 승인기 [2, 3] · 기각기 [1] · 처분: 없음
최종 판정: 기각

### 근거
- 기 1: 관문 5 정합 미달. 비용 문제는 실재하지만, 독립 현행 제품 소비자가 없는 기존 인터페이스를 시험 때문에 유지한다. 동결문 불변식과 `AGENTS.md` 5·7행은 호출부와 시험을 새 계약으로 함께 정렬하고 구판 인터페이스를 살리는 래퍼를 남기지 않도록 정한다. 제안은 이 요구를 충족하지 않는다.

## R1-08

### 원문
제목: `authorize`가 `grant_scope_reason`의 상태·만료·효력 시작 검사를 중복 구현한다

### 위치
`.claude/skills/do-math/scripts/do_math/governance.py` 413행, 425~433행(`authorize`).

### 기준
`임시/do-math_검증_20260925_opus/동결.md` 261행(목적 진술):

```text
같은 계약·검사·인터페이스·기능을 단계별로 다르게 구현한 곳은 정의와 소비자 전건을 확인해 공통 구현으로 정리한다.
```

### 영향
두 함수가 같은 검사 세 개를 같은 순서로 따로 가진다.

- `authorize` 426~431행: `status != "active"` → "grant is not active", `expires_at <= now` → "grant expired", `valid_from > now` → "grant is not effective yet"
- `grant_scope_reason` 382~384행: 같은 세 검사, 같은 사유 문자열

`authorize`는 통과한 grant에 대해 곧 `grant_scope_reason`을 부르므로, 판정 결과와 사유는 어느 쪽이 먼저 걸러도 같다. 한쪽만 고치면 사유나 경계가 갈라진다.

`authorize`는 여러 곳에서 불린다(graphify `affected scripts/do_math/governance.py`: engine.py, academic_engine.py, context_store.py, delegations.py, external.py 등, grep 19곳).

- 정지 조사(engine.py 3549행)
- 형식 검사 정지(4589행)
- 제어 게시(1270행)
- 묶음 현재성(2269·2277행)

조각 뒤 반환값과 사유는 바뀌지 않는다. `at`의 형식 검사는 `grant_scope_reason`의 `timestamp(at)`가 맡는다.

### 조각 1 — .claude/skills/do-math/scripts/do_math/governance.py 413~413행
원래:
```
    now = timestamp(at)
```
대체:
```

```

### 조각 2 — .claude/skills/do-math/scripts/do_math/governance.py 425~433행
원래:
```
        reason = None
        if grant.get("status") != "active":
            reason = "grant is not active"
        elif grant.get("expires_at") and timestamp(grant["expires_at"]) <= now:
            reason = "grant expired"
        elif grant.get("valid_from") and timestamp(grant["valid_from"]) > now:
            reason = "grant is not effective yet"
        if reason is None:
            reason = grant_scope_reason(grant, action, runtime, at=at)
```
대체:
```
        reason = grant_scope_reason(grant, action, runtime, at=at)
```


### 판정
확정: 기각 · 승인기 [] · 기각기 [1, 2, 3] · 처분: 없음
최종 판정: 기각

### 근거
- 기 1: 관문 4 개선 및 관문 5 정합 미달. `grants={}`이거나 모든 grant가 역할·대상 필터에서 제외되면 대체 후에는 `timestamp(at)`가 한 번도 실행되지 않는다. 예를 들어 `at=''`는 원래 `ValueError`였지만 대체 후 일반 권한 거부 결과가 된다. 영향 칸의 “at의 형식 검사는 grant_scope_reason이 맡는다”는 전 입력에 성립하지 않는다. 동결문의 현재 입력 검사와 오류 처분 보존을 충족하지 못한다.
- 기 2: 관문 4·5 미달이다. 조각 1은 무조건 수행되던 시각 입력 검사를 없앤다. 예를 들어 grants가 비어 있고 `at=''`이면 원래는 ValueError지만 대체 뒤에는 `allowed=False`를 정상 반환한다. 영향 칸의 “at의 형식 검사는 grant_scope_reason이 맡는다”는 모든 경로에서 성립하지 않는다. 현재 입력 검사와 오류 처분을 보존한다는 불변식을 충족하지 못한다.
- 기 3: 관문 4·5: 대체안은 시각 입력 검사를 조건부로 바꾼다. 예를 들어 grants가 비어 있고 at이 잘못된 문자열이면 원래는 ValueError지만 대체 뒤에는 일반적인 허가 없음으로 반환한다. 영향 칸의 오류 처분 보존 주장과 다르며 현재 입력 검사 유지 불변식을 충족하지 않는다.

## R1-10

### 원문
제목: 판정 재심사를 여는 공개 명령과 자동 발동 생산자가 모두 없다

### 위치
산출물에 구현된 소비 경로:

- `.claude/skills/do-math/scripts/do_math/engine.py` 398~417행: `control()`이 `role="identity_review"`와 `assessment_reassessment`를 받는다.
- 같은 파일 1417~1421행: `_review_recovery_control`이 이를 소비한다.
- `.claude/skills/do-math/scripts/do_math/control_contracts.py` 88행: payload 형식.

원자료의 요구 좌표:

- `.claude/skills/do-math/GLOSSARY.md` 629행(「판정 사용 효력」)
- `.claude/skills/do-math/계약/동일성-검토.md` 21~27행

구현해야 할 자리 후보:

- `.claude/skills/do-math/scripts/do_math/cli.py` 145~154행: `request` 명령 표면. `--role` 선택지에 `identity_review`가 없고, 재심사 입력 인자도 없다.
- 검토 계보를 봉인·게시하는 지점: 자동 발동자.

### 기준
`.claude/skills/do-math/GLOSSARY.md` 629행:

```text
일반적인 결함 제보는 검토 입력으로 접수하며, 제보만으로 판정의 사용 효력을 바꾸지 않는다. 결정론 검사로 확인한 결함 또는 정식 독립 검토 활동이 제출한 구체적인 의미 이의가 있으면 해당 판정의 사용을 정지하고 유한한 재심사를 연다. 재심사는 원 판정의 정확성과 그 전제의 현재성을 각각 확인한다.
```

`임시/do-math_검증_20260925_opus/동결.md` 261행(목적 진술):

```text
사용자 요청에 따라 do-math 정본 전체의 불필요한 호환 요소·죽은 인자, 생산자와 소비자의 계약 불일치, 존재 목적을 위배하는 구현, 같은 기능을 불합리하게 수행하는 비효율, 최근 수리의 불충분함과 영향 누락을 발견하고 수리한다.
```

### 영향
사용자 쪽 경로가 닫혀 있다.

- 공개 `request --role`은 argparse 선택지(cli.py 148~150행)에서 `identity_review`를 거부한다.
- `--request-file` JSON 명령도 같은 parser를 거친다(cli.py 617~659행).
- 따라서 연구 책임자는 CLI로 재심사를 열 수 없다.

코드 안의 자동 생산자도 없다.

- `_start_assessment_reassessment`를 부르는 곳은 review_engine.py 70행 하나다.
- 그 함수 `_assessment_reassessment_control`은 engine.py 1421행, 즉 inbox 제어 소비에서만 불린다.
- 결정론 결함(원 검토자가 제안 작성자 문맥을 이어받음)과 봉인된 독립 이의를 가리는 적격 판정 `_qualified_assessment_defect`(review_engine.py 84~125행)는 구현돼 있으나, 이를 발동하는 지점이 없다.

그 결과, GLOSSARY 629행이 요구하는 결함이 확인돼도 해당 동일성 판정(IA)의 사용 효력은 정지되지 않는다. K 사용 판단과 목표 감사(`knowledge.assess_use`, `knowledge_records.usable_links`)는 그 판정을 계속 근거로 쓴다. 이 경로는 Python `control()`을 직접 부르는 시험(test_redesign_ENGINE.py 1199~1242행, test_redesign_REVIEWS.py)에서만 실행된다.

### 상신
#### 읽은 범위

지급 밖에서 연 곳:

- 정의: `.claude/skills/do-math/scripts/do_math/review_engine.py` 55~135행(재심사 제어·적격 결함 판정·시작부). `knowledge.py`의 `assessment_reassessment_proposal`(388행)·`apply_assessment_reassessment`(443행)는 grep 좌표만 확인했고 본문은 열지 않았다.
- 정본 문서: `.claude/skills/do-math/GLOSSARY.md` 625~631행, `.claude/skills/do-math/계약/동일성-검토.md` 21~27행.
- 결정: `docs/do-math/implementation-v5/traceability.json`의 재심사 항목(258행, 16868~16876행)을 grep으로만 확인했다. 공개 진입점이나 자동 발동을 정한 사용자 결정 문서는 찾지 못했다.

#### 세계 물음

행위자는 둘이다.

- 연구 책임자: 사용자 대화를 통해 과거 IA의 결함 근거를 건넨다. 근거는 작성자 문맥을 이어받은 검토 실행 ID이거나, 다른 봉인 검토가 `assessment:<IA>`를 근거로 든 finding이다. 연구 책임자는 이 근거로 해당 판정의 사용 정지와 재심사를 원한다.
- 기계 실행기: 새 검토 계보를 봉인할 때 그런 finding을 직접 관찰한다.

필요한 개체 가운데 재심사 요청 payload와 그 소비자(control_contracts.py 88행, engine.py 406~415행, review_engine.py 63~73행)는 정의 파일에 있다. 공개 명령 표면과 자동 발동 호출부는 정의 파일에 없다.

#### 선택지

1. 공개 명령 표면을 추가한다. 예: `request --role identity_review --reassessment-file PATH`(`assessment_id`·`assessment_sha256`·`evidence` JSON). README와 CLI 실행 계약에 절차를 더한다. 하류: 사용자가 알아챈 결함은 열 수 있다. 실행기가 관찰한 이의는 사람이 옮기기 전까지 열리지 않아, GLOSSARY "있으면 … 연다"는 일부만 충족된다.
2. 자동 발동을 연결한다. 검토 계보 봉인·게시 지점과 상태 검사에서 `_qualified_assessment_defect`가 인정하는 근거를 찾으면 `_start_assessment_reassessment`를 부른다. 하류: GLOSSARY 문언을 그대로 충족한다. 봉인 경로 변경과 시험 추가가 필요하고, 자동 사용 정지는 목표 감사와 K 사용을 즉시 바꾼다.
3. 1과 2를 모두 한다. 하류: 두 경로를 유지·시험하는 비용이 든다.
4. 소비 경로(control 수용, review_engine 재심사부, knowledge 재심사 함수, 관련 시험)를 제거하고 GLOSSARY 629행과 동일성-검토 21~27행을 개정한다. 하류: 판정 오류를 복원·철회할 수단이 사라지고, 확정 용어 정의를 바꿔야 한다.

#### 변형 물음

- 선택지 2의 대가(근거 없는 자동 정지): 적격 판정이 이미 일반 보고로는 정지하지 않도록 제한돼 있어(review_engine.py 84~125행, 동일성-검토 23행) 크게 줄어든다.
- 선택지 1의 대가(사용자가 해시·근거 JSON을 손으로 작성): `prepare-import-approval`처럼 IA ID에서 정확한 좌표 초안을 만드는 명령을 두면 줄어든다.

#### 추천

선택지 2를 추천한다. GLOSSARY 629행이 정한 두 근거(결정론 결함과 정식 독립 검토의 이의)는 모두 실행기가 직접 관찰하는 기록이다. 적격 판정도 이미 구현돼 있어, 자동 발동만으로 정의된 상태에 도달한다. 선택지 1이 더하는 사용자 경로는 GLOSSARY가 요구하지 않는 별도 표면이다. 선택지 4는 결함을 정의 쪽에서 지우므로 판정 오류에 대한 복구 수단을 잃는다.


### 판정
확정: 기각 · 승인기 [1] · 기각기 [2, 3] · 처분: 없음
최종 판정: 기각

### 근거
- 기 2: 관문 적용 전 항목 종류 대조에서 미달이다. 확인된 현행 요구는 적격 결함을 재심사 소비자에 연결하는 것이며, 그 구현·시험·문서는 모두 동결문 산출물 안에 있다. 상신 칸은 이 수리를 정하는 데 반드시 필요한 미확정 사용자 의도를 제시하지 않았다. 추천한 자동 발동 연결은 기존 요구를 구현하는 조각으로 닫을 수 있다. 별도 공개 명령을 추가하거나 현행 규범을 폐지하는 선택지를 함께 나열한 것만으로 현재 결함의 수리에 사용자 결정이 필요해지지는 않는다.
- 기 3: 항목 종류 대조: 확인된 규범 위반은 이미 정해진 자동 재심사 요구와 생산자 연결의 누락이다. 항목 자체의 선택지 2는 산출물 파일의 연결과 시험을 고쳐 그 요구를 충족한다고 설명한다. 별도 CLI 표면 추가나 규범 삭제는 그 결함을 수리하는 데 필수인 사용자 결정으로 입증되지 않았다. 선택적인 기능 확장과 규범 개정을 함께 나열했다는 이유만으로 상신 제안이 성립하지 않는다. 현행 요구를 충족하는 조각 항목으로 닫아야 한다.

## R1-16

### 원문
제목: 공통 CLI 어댑터가 실행 파일 경로를 codex_path와 cli_path 두 이름으로 보관해 Claude 어댑터에도 Codex 이름의 별칭이 남는다

### 위치
.claude/skills/do-math/scripts/do_math/codex_adapter.py 127~130행 `LocalCLIAdapter.__init__`, 156~163행과 171행 `describe`.

### 기준
.claude/skills/do-math/AGENTS.md 5행:

```
- 설계를 바꾸면 구현·호출부·스키마·테스트·예시·문서를 같은 변경에서 새 계약으로 교체한다. 구판 호환을 위한 이전 구현·이름 별칭·래퍼·구형 인자·무시되는 설정·버전별 분기·마이그레이션 경로를 남기지 않는다.
```

### 영향
`LocalCLIAdapter`는 Codex와 Claude가 함께 쓰는 공통 수명 어댑터다(121행 docstring, claude_adapter.py 17행 상속). 그런데 생성자 인자는 `codex_path`이고 같은 값을 `self.codex_path`와 `self.cli_path` 두 속성에 담는다. 공통 경로(`capability_identity` 134행, `observation_key` 150행, `start` 182행, claude_adapter.py `describe` 26~31행)는 `cli_path`만 읽는다. `codex_path`는 Codex 전용 `describe`(156~171행)만 읽는다. 그래서 `ClaudePrintAdapter`의 `codex_path` 속성에는 Claude 실행 파일 경로가 Codex 이름으로 들어 있다. 저장소 grep에서 어댑터의 `codex_path` 속성을 읽는 외부 소비자는 없다. 생성자는 모두 위치 인자로 호출된다(initialization.py 37·39행, cli.py 454·459행, model_runner.py 27·271·361행, 시험 전건). 따라서 인자 이름과 속성을 `cli_path` 하나로 정리해도 호출부는 바뀌지 않는다. model_runner.py `CodexModelRunner.codex_path`는 러너의 요청 필드용 속성이므로 이 수리와 무관하다.

### 조각 1 — .claude/skills/do-math/scripts/do_math/codex_adapter.py 127~130행
원래:
```
    def __init__(self, codex_path: str, *, describe_timeout: float = 10.0) -> None:
        self.codex_path = codex_path
        self.cli_path = codex_path
        self.describe_timeout = describe_timeout
```
대체:
```
    def __init__(self, cli_path: str, *, describe_timeout: float = 10.0) -> None:
        self.cli_path = cli_path
        self.describe_timeout = describe_timeout
```

### 조각 2 — .claude/skills/do-math/scripts/do_math/codex_adapter.py 156~163행
원래:
```
            version_result = subprocess.run([self.codex_path, "--version"], check=False, shell=False,
                                            capture_output=True, timeout=self.describe_timeout, creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
            global_help_result = subprocess.run([self.codex_path, "--help"], check=False, shell=False,
                                                capture_output=True, timeout=self.describe_timeout, creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
            help_result = subprocess.run([self.codex_path, "exec", "--help"], check=False, shell=False,
                                         capture_output=True, timeout=self.describe_timeout, creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
        except (OSError, subprocess.TimeoutExpired) as exc:
            return {"cli_path": self.codex_path, "verified": False, "error_type": type(exc).__name__}
```
대체:
```
            version_result = subprocess.run([self.cli_path, "--version"], check=False, shell=False,
                                            capture_output=True, timeout=self.describe_timeout, creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
            global_help_result = subprocess.run([self.cli_path, "--help"], check=False, shell=False,
                                                capture_output=True, timeout=self.describe_timeout, creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
            help_result = subprocess.run([self.cli_path, "exec", "--help"], check=False, shell=False,
                                         capture_output=True, timeout=self.describe_timeout, creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
        except (OSError, subprocess.TimeoutExpired) as exc:
            return {"cli_path": self.cli_path, "verified": False, "error_type": type(exc).__name__}
```

### 조각 3 — .claude/skills/do-math/scripts/do_math/codex_adapter.py 171~171행
원래:
```
                "cli_path": self.codex_path, "version_bytes": version, "version_sha256": _sha256(version),
```
대체:
```
                "cli_path": self.cli_path, "version_bytes": version, "version_sha256": _sha256(version),
```


### 판정
확정: 기각 · 승인기 [1, 3] · 기각기 [2] · 처분: 없음
최종 판정: 기각

### 근거
- 기 2: 관문 1·4·5 미달이다. 영향 칸의 외부 속성 소비자가 없다는 주장은 원문과 다르다. 대체는 `self.codex_path`를 제거하므로 현행 probe의 요청 구성에서 AttributeError를 일으킨다. 구현과 호출부를 같은 변경으로 맞춘다는 불변식도 충족하지 못한다.

## R1-24

### 원문
제목: 외부 operation의 요청·멱등 키 결박 검사가 네 곳에서 따로 계산된다

### 위치
같은 결박 계산이 네 곳에 따로 있다. .claude/skills/do-math/scripts/do_math/external.py 47행(`prepare_operation`)과 73행(`validate_operation`), .claude/skills/do-math/scripts/do_math/record_schemas/__init__.py 325~330행(`validate_semantics`), .claude/skills/do-math/scripts/do_math/state_checks.py 365~370행(`_inspect_area`의 tasks_activities_executions)이다.

### 기준
임시/do-math_검증_20260925_opus/동결.md 261행(목적 진술):

```
같은 계약·검사·인터페이스·기능을 단계별로 다르게 구현한 곳은 정의와 소비자 전건을 확인해 공통 구현으로 정리한다.
```

### 영향
operation의 결박은 두 규칙이다. `request_sha256`는 요청 JSON의 정준 해시이고, `idempotency_key`는 sha256(id + request_sha256)이다. 생산자 external.py 42~47행과 소비자 세 곳이 이 규칙을 각자 쓴다. record_schemas/__init__.py 326~329행은 `_hash`를 가져오지만 키 공식은 다시 쓴다. state_checks.py 366~369행은 `json.dumps(..., separators=(',', ':'))`로 요청 해시 자체를 다시 구현한다.

어느 한 곳에서 정준화나 키 공식이 바뀌면 나머지가 모르는 사이에 어긋난다. 예를 들어 생산자의 키 공식만 바뀌면 저장 검증(`validate_semantics`)이 모든 신규 operation을 거부한다. 반대로 state_checks만 바뀌면 `check`의 tasks_activities_executions 영역이 정상 원장을 "external request or idempotency binding changed"로 막는다. 네 곳의 현재 공식은 서로 같으므로 수리 전후의 판정 결과는 같다.

수리 후 생산자와 세 소비자는 external.py의 `idempotency_key`와 `request_binding_current`를 쓴다. `validate_operation`의 두 오류 문구와 판정 순서는 유지한다. state_checks는 지금처럼 map 키를 operation ID로 넘기므로 판정 대상이 같다.

### 조각 1 — .claude/skills/do-math/scripts/do_math/external.py 행 12 뒤
대체:
```
def idempotency_key(operation_id: str, request_sha256: str) -> str: return hashlib.sha256((operation_id + request_sha256).encode()).hexdigest()
def request_binding_current(operation: dict) -> bool:
    """The stored request bytes and idempotency key still bind this operation ID."""
    digest = _hash(operation.get("request"))
    return operation.get("request_sha256") == digest and operation.get("idempotency_key") == idempotency_key(operation.get("id", ""), digest)
```

### 조각 2 — .claude/skills/do-math/scripts/do_math/external.py 47~47행
원래:
```
    return {"id":oid,"request":normalized,"request_sha256":digest,"grant_id":grant_id,"source_ref":source_ref,"status":"prepared","idempotency_key":hashlib.sha256((oid+digest).encode()).hexdigest(),"attempts":[],"credential_env":None, **scope}
```
대체:
```
    return {"id":oid,"request":normalized,"request_sha256":digest,"grant_id":grant_id,"source_ref":source_ref,"status":"prepared","idempotency_key":idempotency_key(oid,digest),"attempts":[],"credential_env":None, **scope}
```

### 조각 3 — .claude/skills/do-math/scripts/do_math/external.py 73~73행
원래:
```
    if operation.get("idempotency_key")!=hashlib.sha256((operation["id"]+operation["request_sha256"]).encode()).hexdigest(): raise ValueError("idempotency key changed")
```
대체:
```
    if operation.get("idempotency_key")!=idempotency_key(operation["id"],operation["request_sha256"]): raise ValueError("idempotency key changed")
```

### 조각 4 — .claude/skills/do-math/scripts/do_math/record_schemas/__init__.py 325~330행
원래:
```
    for row in runtime.get("external_operations", {}).values():
        import hashlib
        from ..external import _hash as request_hash
        if (request_hash(row["request"]) != row["request_sha256"] or row["idempotency_key"] !=
                hashlib.sha256((row["id"] + row["request_sha256"]).encode()).hexdigest()):
            raise ValueError("external operation request/key differs from sealed bytes")
```
대체:
```
    from ..external import request_binding_current
    for row in runtime.get("external_operations", {}).values():
        if not request_binding_current(row):
            raise ValueError("external operation request/key differs from sealed bytes")
```

### 조각 5 — .claude/skills/do-math/scripts/do_math/state_checks.py 365~370행
원래:
```
            if operation.get('request'):
                import json
                raw = json.dumps(operation['request'], ensure_ascii=False, sort_keys=True, separators=(',', ':')).encode()
                digest = hashlib.sha256(raw).hexdigest()
                if digest != operation.get('request_sha256') or hashlib.sha256((identifier + digest).encode()).hexdigest() != operation.get('idempotency_key'):
                    defect('external request or idempotency binding changed', identifier)
```
대체:
```
            if operation.get('request'):
                from .external import request_binding_current
                if not request_binding_current({**operation, 'id': identifier}):
                    defect('external request or idempotency binding changed', identifier)
```


### 판정
확정: 기각 · 승인기 [] · 기각기 [1, 2, 3] · 처분: 없음
최종 판정: 기각

### 근거
- 기 1: 관문 6 조각 규약 미달. 조각 1은 이웃 행의 `_hash` 정의에 기대는 삽입인데 `행 12 뒤`라는 틈 좌표만 둔다. 조각 계약 5절은 이웃 행의 논지를 전제하는 삽입에서 그 행을 구간에 포함하도록 정한다. 해당 정의 행을 포함하지 않아 의존이 교차로 드러나지 않는다.
- 기 2: 관문 6 미달이다. 새 결박 함수는 이웃 행에서 정의한 요청 해시 계산에 의존하므로 자족 삽입이 아니다. 조각 계약 5절은 이웃 행의 내용에 기대는 삽입에서 그 행을 구간에 포함하도록 요구한다. 제시된 `행 12 뒤` 좌표는 이 의존을 선언하지 않아 `_hash` 정의 변경과의 교차를 보장하지 못한다.
- 기 3: 관문 6: 조각 1은 이웃 12행의 _hash 정의를 전제로 하는 의존 삽입인데 그 행을 구간에 포함하지 않았다. 조각 계약 5절은 이웃 행의 용어·논지를 전제하는 삽입도 이웃 행을 포함한 교체 구간으로 작성하도록 요구한다. 결박 계산 공통화의 내용상 이점과 별개로 이 조각 규약을 통과하지 못한다.

## R1-40

### 원문
제목: knowledge 제어의 check-kind·activate-kind는 상태를 바꾸지 않는 사문 연산이며 완료 인스턴스를 ready로 되돌린다

### 위치
- `.claude/skills/do-math/scripts/do_math/engine.py` 1492행: 연산 목록.
- 같은 파일 1503~1513행: 두 연산의 분기. 검사만 하고 상태를 바꾸지 않는다.
- 같은 파일 1519~1520행: 모든 연산 뒤의 공통 후처리. 목표 현재성을 재평가하고 `waiting`·`completed`를 `ready`로 바꾼다.
- `.claude/skills/do-math/scripts/do_math/control_contracts.py` 91행: 두 연산만 쓰는 `check_ref` 입력.
- `.claude/skills/do-math/scripts/tests/test_knowledge_import_engine.py` 80~85행, 111행: 두 연산을 보내는 시험.

### 기준
`.claude/skills/do-math/AGENTS.md` 5행:

```text
구판 호환을 위한 이전 구현·이름 별칭·래퍼·구형 인자·무시되는 설정·버전별 분기·마이그레이션 경로를 남기지 않는다.
```

`.claude/skills/do-math/README.md` 476행 「운영 제어 명령의 용도」:

```text
| `knowledge --file` | candidate·종류 정의·관계를 수입하거나 기존 지식을 개정·무효화할 때 | candidate 수입은 K 편입이 아니다 |
```

`.claude/skills/do-math/README.md` 295행:

```text
- `completed`: 현재 CLI가 목표와 적용되는 학술 요구의 완료 조건을 충족했다고 계산한 상태다.
```

### 영향
종류 정의의 점검과 활성화는 독립 점검 결과를 받는 소비자가 한 번에 처리한다. `_apply_kind_definition_check`는 승인 판정을 받으면 `check_kind_definition`과 `activate_kind_definition`을 차례로 호출한다(engine.py 4315~4319행). 사용자 제어 `check-kind`·`activate-kind`는 이미 끝난 승인과 활성 상태를 다시 확인할 뿐이다(1503~1513행). 확인에 실패하면 거부되고, 통과해도 상태를 바꾸지 않는다. README 476행의 용도 목록에도 이 두 연산은 없다.

통과한 경우에는 부작용이 남는다. 1519~1520행이 실행되어 목표 현재성을 재평가하고 `completed`를 `ready`로 바꾼다. `_knowledge_io_control`에는 닫힘·완료 상태 검사가 없다(1488~1521행). 재현: 목표가 `mathematically_solved`이고 `status=completed`인 인스턴스에 이미 활성화된 종류의 `check-kind`를 보낸다 → 인스턴스가 `ready`로 돌아가고 다음 `run`이 새 action을 배정할 수 있다. README 295행의 `completed` 의미와 어긋난다.

시험 test_knowledge_import_engine.py 80~83행은 두 연산이 점검 전에 거부된다는 것만 확인한다. 111행은 이미 활성화된 뒤에 `activate-kind`를 보내 아무 효과도 내지 않는다. 112행의 확인은 그 앞 `_apply_kind_definition_check`의 결과다.

수리 뒤 `check-kind`·`activate-kind` 요청은 `_apply_extended_control`의 `_knowledge_control`로 넘어가고, `id`가 없어 `knowledge item does not exist`로 거부된다(lifecycle_engine.py 573~574행, 625~629행). `family`·`token`은 `withdraw-kind`가 계속 쓰므로 유지한다. grep 결과 `check_ref`의 소비자는 engine.py 1510행뿐이다.

### 조각 1 — .claude/skills/do-math/scripts/do_math/engine.py 1492~1492행
원래:
```
        if operation not in {"import", "register-kind", "check-kind", "activate-kind", "withdraw-kind", "import-relation"}: return False
```
대체:
```
        if operation not in {"import", "register-kind", "withdraw-kind", "import-relation"}: return False
```

### 조각 2 — .claude/skills/do-math/scripts/do_math/engine.py 1503~1513행
원래:
```
        elif operation in {"check-kind", "activate-kind"}:
            definition = knowledge_io._lookup_definition(self.instance, spec["family"], spec["token"])
            if not definition:
                raise ValueError("kind definition does not exist")
            check = definition.get("check", {})
            execution = self.runtime["executions"].get(check.get("execution_id"), {})
            if (check.get("decision") != "approved" or execution.get("outcome") != "output_accepted"
                    or (spec.get("check_ref") and spec["check_ref"] != check.get("execution_id"))):
                raise ValueError("kind activation requires a published independent semantic check")
            if definition["status"] != "active":
                raise ValueError("kind check is no longer active; submit a revised definition")
```
대체:
```

```

### 조각 3 — .claude/skills/do-math/scripts/do_math/control_contracts.py 91~91행
원래:
```
    'knowledge': obj({**fields(text='operation id reason family token check_ref'),
```
대체:
```
    'knowledge': obj({**fields(text='operation id reason family token'),
```

### 조각 4 — .claude/skills/do-math/scripts/tests/test_knowledge_import_engine.py 80~85행
원래:
```
        self.send(operation='check-kind', family='knowledge', token=definition['token'], check_ref='fixture:check')
        self.assertNotIn(definition['token'], kinds())
        self.send(operation='activate-kind', family='knowledge', token=definition['token'])
        self.assertNotIn(definition['token'], kinds())
        # A user control is not an independent semantic finding. Use the actual
        # central consumer with a separate v5 execution and synthetic AI verdict.
```
대체:
```
        # Only the central consumer of an independent check activates a kind.
        # Use a separate v5 execution and a synthetic AI verdict.
```

### 조각 5 — .claude/skills/do-math/scripts/tests/test_knowledge_import_engine.py 111~111행
원래:
```
        self.send(operation='activate-kind', family='knowledge', token=definition['token'], check_ref=eid)
```
대체:
```

```


### 판정
확정: 기각 · 승인기 [1] · 기각기 [2, 3] · 처분: 없음
최종 판정: 기각

### 근거
- 기 2: 관문 4·5 미달이다. 영향 칸은 제거한 연산의 요청에 id가 없다고 가정하지만 현행 입력 계약은 id를 허용한다. 활성 종류를 가리키는 check-kind 요청에 기존 지식 id까지 들어오면, 원래 분기는 그 지식의 검토를 건드리지 않는다. 대체 뒤에는 `_knowledge_control`이 검토·조사·실행을 먼저 바꾼 뒤 656행에서 지원하지 않는 연산으로 거부하며, 그 변경이 거부 저장에 포함된다. 제거한 연산을 부작용 없이 거부하는 경계가 없어 새로운 연구 이력 손상을 들인다.
- 기 3: 관문 4: id가 항상 없다는 영향 칸의 전제가 입력 계약에서 보장되지 않는다. 활성 인스턴스에 유효한 지식 id를 함께 넣은 check-kind 요청은 대체 뒤 지식의 진행 중 검토를 unresolved로 바꾸고 조사 취소·실행 정지 요청을 남긴 후 거절될 수 있다. 원래 두 연산에는 그 부작용이 없다. 삭제 대상 연산이 다른 변경 처리기로 넘어가기 전에 거절된다는 보장이 없어 새 결함을 들인다.

## R1-42

### 원문
제목: 시험 그룹 archive에는 시험이 하나도 없는데 README는 과거 실행 증거 검사로 안내한다

### 위치
- `.claude/skills/do-math/scripts/test_categories.py` 2행: `GROUPS`의 `archive`.
- `.claude/skills/do-math/README.md` 533행, 541행: `archive` 그룹 설명.
- 소비: `.claude/skills/do-math/scripts/run_tests.py` 259행(선택지)과 279~283행(선택 결과가 없으면 실패).

### 기준
`.claude/skills/do-math/AGENTS.md` 5행:

```text
구판 호환을 위한 이전 구현·이름 별칭·래퍼·구형 인자·무시되는 설정·버전별 분기·마이그레이션 경로를 남기지 않는다.
```

`.claude/skills/do-math/AGENTS.md` 11행:

```text
검증은 `python scripts/run_tests.py`의 관련 그룹부터 수행한다.
```

### 영향
시험 파일의 그룹 표지는 `test_group('unit')` 22건, `integration` 10건, `resource` 3건, `lean` 1건이다. `archive`는 0건이고, `do_math_test_group`을 직접 지정한 시험도 없다(grep, scripts/tests 전체). `group_for`는 표지가 없는 시험을 `unit` 또는 `integration`으로만 분류한다(test_categories.py 27~34행). 그러므로 `archive`에 드는 시험은 없다. `'archive'`는 7d2597e에서 들어왔다(git log -S).

재현: `python scripts/run_tests.py --group archive` → 선택 결과가 비어 `No tests selected; no pass was established.`와 함께 종료 코드 2로 끝난다(run_tests.py 281~283행). AGENTS.md 11행대로 관련 그룹을 고르는 검증자는 README 533행을 보고 과거 실행 증거 검사를 기대한다. 그러나 그런 검사는 없다. README 541행은 없는 그룹의 시간 상한 규칙을 설명한다.

영향 범위: graphify `affected scripts/test_categories.py`는 README.md·run_tests.py와 `test_group`을 import하는 시험 파일들을 반환했다. 그중 `archive`를 쓰는 곳은 없다. 시험 가운데 `GROUPS`를 참조하는 곳도 없다(grep). run_tests.py의 선택지는 `GROUPS`에서 파생되므로(259·293행) 따로 고칠 필요가 없다.

### 조각 1 — .claude/skills/do-math/scripts/test_categories.py 2~2행
원래:
```
GROUPS = ('unit', 'integration', 'lean', 'resource', 'archive')
```
대체:
```
GROUPS = ('unit', 'integration', 'lean', 'resource')
```

### 조각 2 — .claude/skills/do-math/README.md 533~533행
원래:
```
`--group unit`은 순수 규칙과 임시 파일 중심의 검사, `integration`은 실제 저장·프로세스 등 통합 검사, `lean`은 실제 컴파일러 검사, `resource`는 CPU·메모리·큰 출력 부하 검사, `archive`는 과거 실행 증거의 전체 무결성 검사다. `--group`을 반복해 조합할 수 있으며 생략하면 모두 실행한다. `--match`는 테스트 ID의 glob으로 선택하고 `--list`는 수집 결과만 표시한다. 선택 결과가 없으면 실패로 끝난다.
```
대체:
```
`--group unit`은 순수 규칙과 임시 파일 중심의 검사, `integration`은 실제 저장·프로세스 등 통합 검사, `lean`은 실제 컴파일러 검사, `resource`는 CPU·메모리·큰 출력 부하 검사다. `--group`을 반복해 조합할 수 있으며 생략하면 모두 실행한다. `--match`는 테스트 ID의 glob으로 선택하고 `--list`는 수집 결과만 표시한다. 선택 결과가 없으면 실패로 끝난다.
```

### 조각 3 — .claude/skills/do-math/README.md 541~541행
원래:
```
결과 디렉터리는 새 경로나 빈 디렉터리를 지정한다. 생략하면 고유한 임시 디렉터리를 만든다. `report.json`은 테스트별 결과·시간, 느린 검사 목록, 코드 판본과 실행 중 변경 여부를 기록한다. 격리 실행의 stdout·stderr와 진행 기록도 남긴다. 격리 작업자의 임시 파일은 해당 결과 디렉터리의 `scratch/` 아래에 만들므로, 강제 종료로 정리되지 않은 Lean 입력·출력도 그곳에서 찾을 수 있다. 시간 초과 때에는 해당 Job의 자식까지 종료하고, 같은 작업자에서 끝내지 못한 검사는 미실행으로 기록하며 다른 검사 그룹을 계속한다. 부분 실행을 전체 통과로 표시하지 않는다. 일반 `integration`·`unit`·`archive` 그룹에는 이 프로세스 시간 상한을 적용하지 않는다.
```
대체:
```
결과 디렉터리는 새 경로나 빈 디렉터리를 지정한다. 생략하면 고유한 임시 디렉터리를 만든다. `report.json`은 테스트별 결과·시간, 느린 검사 목록, 코드 판본과 실행 중 변경 여부를 기록한다. 격리 실행의 stdout·stderr와 진행 기록도 남긴다. 격리 작업자의 임시 파일은 해당 결과 디렉터리의 `scratch/` 아래에 만들므로, 강제 종료로 정리되지 않은 Lean 입력·출력도 그곳에서 찾을 수 있다. 시간 초과 때에는 해당 Job의 자식까지 종료하고, 같은 작업자에서 끝내지 못한 검사는 미실행으로 기록하며 다른 검사 그룹을 계속한다. 부분 실행을 전체 통과로 표시하지 않는다. 일반 `integration`·`unit` 그룹에는 이 프로세스 시간 상한을 적용하지 않는다.
```


### 판정
확정: 기각 · 승인기 [] · 기각기 [1, 2, 3] · 처분: 없음
최종 판정: 기각

### 근거
- 기 1: 관문 1: archive 시험이 하나도 없다는 지적이 현재 원문에서 성립하지 않는다. 관문 4·5: GROUPS에서 archive만 지우면 남은 데코레이터가 모듈 수집 중 unknown test group 오류를 낸다. 유지하는 시험과 새 계약을 함께 맞춰야 한다는 개발 원칙도 충족하지 못한다.
- 기 2: 관문 1에서 「archive 시험 0건」이라는 지적이 성립하지 않는다. 별칭으로 사용한 현행 소비자가 있다. 관문 4·5에서도 GROUPS에서만 archive를 지우면 이 데코레이터가 모듈을 불러오는 중 `unknown test group`을 발생시키므로 기존 시험 수집을 깨뜨린다. 실제 소비자를 남긴 채 안내와 선택지만 제거하는 수리는 승인할 수 없다.
- 기 3: 관문 1의 실재가 성립하지 않는다. `archive` 시험이 없다는 지적은 별칭으로 사용한 장식자를 놓쳤다. 제안대로 `GROUPS`에서만 빼면 기존 시험 모듈의 장식자 평가가 `unknown test group`으로 실패한다. 관문 4도 통과하지 못한다. 해당 시험의 다른 문제를 이 항목의 승인 근거로 대체하지 않는다.

## R1-45

### 원문
제목: 기각된 Codex 샌드박스 구성만 검사하는 probe_native_isolation.py·probe_codex.py를 둘지 정해야 한다

### 위치
- `.claude/skills/do-math/scripts/probe_native_isolation.py` 1행, 120~130행: `windows.sandbox="elevated"` 읽기 루트 격리를 재현한다. 문서가 참조하지 않는다.
- `.claude/skills/do-math/scripts/probe_codex.py` 1~3행, 62~63행, 134행: `read-only`·`workspace-write` 샌드박스와 기본 `elevated`로 어댑터를 직접 호출한다.
- `.claude/skills/do-math/references/CLI-실행-계약.md` 912행: probe_codex를 「어댑터 실호출 검사」로 안내한다.
- 생산 설정: `.claude/skills/do-math/scripts/do_math/model_runner.py` 31~32행(`danger-full-access`, `unelevated`), README 501행.
- 비생산 값의 유일한 소비자: `.claude/skills/do-math/scripts/do_math/codex_worker.py` 30~31행, 111·125행.

### 기준
`.claude/skills/do-math/AGENTS.md` 3행:

```text
do-math는 프리알파 프로토타입이다. 이 디렉토리는 현재 구현과 계약 하나만 지원한다.
```

`.claude/skills/do-math/AGENTS.md` 5행:

```text
구판 호환을 위한 이전 구현·이름 별칭·래퍼·구형 인자·무시되는 설정·버전별 분기·마이그레이션 경로를 남기지 않는다.
```

`.claude/skills/do-math/README.md` 501행:

```text
현재 기본 Windows 실행은 Codex의 `danger-full-access`·승인 정책 `never`, Claude의 `bypassPermissions`로 기존 사용자 권한을 쓴다.
```

### 영향
제품의 Codex 실행은 `ModelRunner`가 `sandbox="danger-full-access"`, `windows_sandbox="unelevated"`로 고정한다(model_runner.py 31~32행). probe_native_isolation.py는 제품이 쓰지 않는 elevated 샌드박스의 순차·동시 격리를 재현한다. probe_codex.py는 `read-only`·`workspace-write`와 기본 `elevated`로 실행한다. 두 도구가 통과해도 설치된 제품 경로가 작동한다는 근거가 되지 않는다. 실패해도 제품 결함의 근거가 되지 않는다.

CLI 계약 912행을 읽는 검증자는 probe_codex 통과를 Codex 실행 경로의 실호출 증거로 받아들일 수 있다. codex_worker.py가 `read-only`·`workspace-write`·`elevated`를 계속 받는 것도 이 도구 때문이다. grep 결과 제품 호출자는 model_runner.py 31~32행의 고정값뿐이다. 제품 경로의 실호출 검사는 이미 `probe_cli.py --provider codex`가 `ModelRunner`를 거쳐 수행한다(probe_cli.py 66~70행, structured·files·stop).

영향 범위: graphify `affected scripts/probe_native_isolation.py`는 test_native_probe.py와 test_standalone.py만 반환했다. `affected scripts/probe_codex.py`는 GLOSSARY.md·README.md·CLI-실행-계약.md·모델과-실행예산.md·preflight.py·test_preflight.py·test_probe_codex.py를 반환했다. 문서의 직접 언급은 CLI 계약 912행뿐이다(grep). 파일 삭제는 조각으로 표현할 수 없고, 도구를 없앨지는 사용자 결정이 필요하다. 그래서 상신으로 올린다.

### 상신
#### 읽은 범위

- `docs/do-math/구현자-결정과-변명.md` 121~123행: elevated와 unelevated `workspace-write`를 시험하고 기각한 뒤 `danger-full-access`를 기본으로 둔 결정.
- `기억/layer1/M-0269.md` 1~30행: 같은 결정의 기억 기록.
- git log: probe_native_isolation.py는 7cac2fe(「Codex elevated 격리 한계를 재현하고…」)와 133fec9, probe_codex.py는 116cff2·7cac2fe·133fec9·9e5e120.
- `scripts/do_math/codex_worker.py`: 29~31·96~156행은 grep 좌표로만 확인했다. 파일 전문은 열지 않았다.
- `scripts/do_math/model_runner.py` 25~45행, `scripts/tests/test_probe_codex.py` 전문, `scripts/tests/test_native_probe.py` 전문. `scripts/tests/test_standalone.py`는 13·23~26행을 grep으로만 확인했다.
- 정본 문서 절: README 501행 「현재 지원 범위」, CLI 계약 902·912행.

#### 세계 물음

운전자나 개발자는 설치된 Codex 실행 경로가 실제로 작동하는지 모델 호출로 확인한다. 이때 필요한 개체는 제품 설정 그대로 실행하는 실호출 검사다. 정의 파일에 `probe_cli.py --provider codex`가 이미 있다. elevated 격리 재현과 비생산 샌드박스 실행에는 제품 소비자가 없다. 제품은 그 구성을 결정으로 기각했다(구현자-결정과-변명 121~123행).

#### 선택지

- A. 두 도구를 제거한다. probe_native_isolation.py와 그 시험(test_native_probe.py, test_standalone.py의 해당 시험, test_categories.py의 `test_native_probe`), probe_codex.py와 test_probe_codex.py의 해당 시험, CLI 계약 912행의 probe_codex 문장을 지운다. codex_worker.py의 샌드박스 값은 `danger-full-access`와 `unelevated`로 좁힌다. 하류: 실호출 검사는 probe_cli 하나로 모인다. 어댑터 단위 `text`·`tool`·`cancel` 사례는 사라지지만 probe_cli의 structured·files·stop이 같은 어댑터를 제품 설정으로 지난다.
- B. probe_native_isolation.py만 제거하고, probe_codex.py는 제품 설정(`danger-full-access`, `unelevated`)으로 고정해 어댑터 단위 실호출 검사로 남긴다. 하류: codex_worker.py의 비생산 값은 좁힐 수 있다. 실호출 도구는 두 벌로 남는다.
- C. 둘 다 유지하고, CLI 계약에 「기각된 격리 설계의 재현 도구이며 제품 경로의 증거가 아니다」라고 적는다. 하류: codex_worker.py는 제품이 쓰지 않는 샌드박스 값을 계속 지원해야 한다.

#### 변형 물음

A의 대가는 어댑터 단위 사례를 잃는 것이다. probe_cli에 `cancel`에 해당하는 `stop`과 도구 사용인 `files`가 이미 있어 대가는 작다. 격리 연구를 다시 할 필요가 생기면 git 기록(7cac2fe)에서 도구를 되살릴 수 있다. B는 A의 대가를 없애는 변형이다. 대신 같은 목적의 실호출 도구가 두 벌 남는다.

#### 추천

A를 추천한다. 승인 뒤 최종 상태에서 Codex 실호출 검사는 제품 설정으로 실행하는 probe_cli 하나가 되고, codex_worker는 제품이 쓰는 샌드박스 값만 받는다. 이는 AGENTS.md 3·5행과 맞는다. C는 결함을 남긴 채 설명만 더하는 대체 구조다. 이 구조를 유지해야 할 독립 소비자·호환 계약·이행 제약을 찾지 못했으므로 추천하지 않는다. B는 A보다 도구 표면이 크고, A가 잃는 사례는 probe_cli가 덮는다.


### 판정
확정: 기각 · 승인기 [1] · 기각기 [2, 3] · 처분: 없음
최종 판정: 기각

### 근거
- 기 2: 관문 1에서 「기각된 구성만 검사하므로 현행 검사로 둘 이유가 없다」는 전제를 지급된 기준 원문으로 확정할 수 없다. 현재 문서는 제품의 기본 실행과 어댑터·sandbox 검사를 구별한다. 항목이 기각 결정의 근거로 든 외부 결정 문서·기억·Git 기록은 이번 심사의 허용 원문에 없으므로 역사적 결정을 확인한 것으로 취급하지 않았다.

관문 8의 추천 근거도 충분하지 않다. A는 어댑터 사례를 없애면서 probe_cli가 그 사례를 덮는다고 주장하지만, 모델 응답 도중 도구 없이 취소하는 경로와 도구 시작 뒤 정지하는 경로는 다르다. 남는 검사와 사라지는 검사의 차이를 축소한 상태로 제거안을 추천하므로 기각한다.
- 기 3: 관문 1에서 지적의 결함이 확정되지 않는다. 제품 기본 설정과 다른 진단 설정이라는 사실만으로 구판 호환 경로나 기각된 구성만의 무효한 검사가 되지는 않는다. 현행 문서는 어댑터 진단의 범위를 구별하고 있으며, 제품 경로 전체의 성공 증거라고 단정하지 않는다. 상신 칸이 기각 결정의 근거로 든 런 밖 결정문·기억은 이번 파견의 열람 자료가 아니므로 근거로 채택하지 않았다. 또한 추천 A의 사례 대체 주장도 stop과 cancel의 발동 지점 차이를 해소하지 못한다. 확인된 결함 없이 제거 여부를 사용자에게 올리는 것으로 승인할 수 없다.

## R1-09

### 원문
제목: 신뢰 등록 요청의 생산자들이 수신 검사의 기초 공리 집합을 각자 하드코딩한다

### 위치
- `.claude/skills/do-math/scripts/setup_lean.py` 81행: `write_trust_request`가 등록 요청의 `allowed_axioms`를 목록 literal로 쓴다. 19행은 import를 더할 자리다.
- `.claude/skills/do-math/scripts/do_math/trust_inventory.py` 194~198행: `collect_manifest`가 `foundation_profile.allowed_axioms`를 같은 literal로 쓴다.

### 기준
`임시/do-math_검증_20260925_opus/동결.md` 261행(목적 진술):

```text
같은 계약·검사·인터페이스·기능을 단계별로 다르게 구현한 곳은 정의와 소비자 전건을 확인해 공통 구현으로 정리한다.
```

`임시/do-math_검증_20260925_opus/동결.md` 272행(불변식):

```text
- 현재 구현과 계약 하나를 지원한다. 구현·호출부·스키마·시험·예시·문서는 같은 새 계약으로 정렬한다. 독립 현행 소비자가 없는 구판 호환 경로를 남기지 않는다.
```

### 영향
수신자 `trust_validation.py`는 15행 `AXIOMS`를 정본으로 쓴다.

- 59행: `set(environment['allowed_axioms']) != AXIOMS`면 거부한다.
- 62행: `foundation.get('allowed_axioms') != sorted(AXIOMS)`면 거부한다.

두 생산자(`setup_lean.py --trust-file`과 그것이 부르는 `collect_manifest`)는 같은 값을 따로 적는다. `AXIOMS`가 바뀌면 README 72·77행과 초기화-운전 241~247행의 절차로 만든 등록 요청이 `trust register`에서 거부된다. 거부된 뒤에야 불일치가 드러난다.

조각은 두 생산자가 수신자의 집합을 읽게 한다. `sorted(AXIOMS)`는 현재 literal `['Classical.choice','Quot.sound','propext']`와 같으므로 생성 바이트는 바뀌지 않는다. `trust_validation`은 `trust_inventory`를 함수 안에서만 import하므로(37·77·177행) 순환 import가 생기지 않는다.

graphify `affected scripts/setup_lean.py`와 `affected scripts/do_math/trust_inventory.py`는 formal.py, execution_profiles.py, environment_checks.py, initialization.py, lifecycle_engine.py, trust_validation.py, research_fixtures.py, test_environment_validation.py, test_knowledge_import_engine.py를 가리킨다. 시험 fixture의 자체 상수(research_fixtures.py 24행)는 수신 검사를 거치는 입력이라 그대로 둔다.

### 조각 1 — .claude/skills/do-math/scripts/setup_lean.py 19~19행
원래:
```
from do_math.trust_inventory import SMOKE, validation_program, collect_manifest, collect_inventory
```
대체:
```
from do_math.trust_inventory import SMOKE, validation_program, collect_manifest, collect_inventory
from do_math.trust_validation import AXIOMS
```

### 조각 2 — .claude/skills/do-math/scripts/setup_lean.py 81~81행
원래:
```
             'allowed_axioms':['Classical.choice','Quot.sound','propext'],
```
대체:
```
             'allowed_axioms':sorted(AXIOMS),
```

### 조각 3 — .claude/skills/do-math/scripts/do_math/trust_inventory.py 194~198행
원래:
```
    from .repository import exact_content_hash
    observed=collect_inventory(toolchain) if observed_inventory is None else observed_inventory
    scope,files=observed['scope'],observed['files']
    manifest={'command':toolchain['configured_command'],'scope':scope,'files':files,
        'foundation_profile':{'allowed_axioms':['Classical.choice','Quot.sound','propext'],
```
대체:
```
    from .repository import exact_content_hash
    from .trust_validation import AXIOMS
    observed=collect_inventory(toolchain) if observed_inventory is None else observed_inventory
    scope,files=observed['scope'],observed['files']
    manifest={'command':toolchain['configured_command'],'scope':scope,'files':files,
        'foundation_profile':{'allowed_axioms':sorted(AXIOMS),
```


### 판정
확정: 승인 · 승인기 [1, 2, 3] · 기각기 [] · 처분: 승인하되 고치지 않는다
최종 판정: 승인
최종 처분: 승인하되 고치지 않는다

### 근거
- 기 1: 승인하되 고치지 않는다
- 기 2: 수리한다
- 기 3: 수리한다

## R1-31

### 원문
제목: 검토 엔진이 전사 봉인 바이트 인코딩을 따로 복제해 정의한다

### 위치
- `.claude/skills/do-math/scripts/do_math/review_engine.py` 43~48행 `_transcript_bytes` 정의
- 같은 파일 10~15행 `review_cycle` 가져오기
- 사용처: `review_engine.py` 671·920·929·1096·1178행
- 원본 인코딩: `.claude/skills/do-math/scripts/do_math/review_cycle.py` 26~31행 `_bytes`·`_digest`

### 기준
`임시/do-math_검증_20260925_opus/동결.md` 「목적 진술」 261행:

```
같은 계약·검사·인터페이스·기능을 단계별로 다르게 구현한 곳은 정의와 소비자 전건을 확인해 공통 구현으로 정리한다.
```

같은 절:

```
생산자와 소비자의 계약 불일치
```

### 영향
`review_engine.py` 44~45행의 주석이 밝히듯 `_transcript_bytes`는 `review_cycle._bytes`가 봉인하는 압축 JSON 인코딩과 같아야 한다. 현재는 같은 식을 두 모듈이 각각 적는다. 계약이 두 방향으로 걸려 있다.

- 소비: 671~675행은 `review_cycle`이 manifest에 봉인한 해시(`record_turn` 1031행)를 `_transcript_bytes`로 다시 계산해 전사 원문을 대조한다.
- 생산: 1096~1097행은 보충 조사 원자료(`inline`)의 `sha256`·`bytes`를 `_transcript_bytes`로 만든다. `review_cycle.validate_sealed_review` 311~313행은 이를 `_bytes(source['inline'])`로 재검증한다. 1178행의 조사 원자료 materialize도 같은 값을 대조한다.

한쪽 정의만 바뀌면 정상 전사가 `review source hash does not match its sealed transcript` 복구 사건으로 바뀐다. 또는 봉인 검토 재생이 `supplemental source bytes changed`로 실패한다. 수정은 `review_cycle`의 `_bytes`를 같은 이름 `_transcript_bytes`로 가져오고 복제 정의를 지운다. 기존 주석의 근거(저장소 JSON과 다른 인코딩)는 가져오기 자리에 남긴다. 사용처 다섯 곳과 계산 결과는 바뀌지 않는다. `json`은 299·644·971행 등에서 계속 쓰인다. graphify `affected scripts/do_math/review_engine.py` 결과는 `engine.py`, `record_schemas/__init__.py`, `review_engine.py`이다.

### 조각 1 — .claude/skills/do-math/scripts/do_math/review_engine.py 15~15행
원래:
```
                          resource_disposition, validate_resource_disposition)
```
대체:
```
                          resource_disposition, validate_resource_disposition,
                          # Transcript seals use review_cycle's compact encoding, not repository
                          # JSON (which uses indentation and a terminal newline).
                          _bytes as _transcript_bytes)
```

### 조각 2 — .claude/skills/do-math/scripts/do_math/review_engine.py 43~48행
원래:
```
def _transcript_bytes(value):
    # review_cycle seals this canonical, compact encoding, rather than repository
    # JSON (which uses indentation and a terminal newline).
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False).encode('utf-8')


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
- 기 2: 수리한다
- 기 3: 수리한다

## R1-32

### 원문
제목: 보충 조사 요청 다이제스트를 생산자와 재생 검증자가 따로 계산한다

### 위치
- 생산자: `.claude/skills/do-math/scripts/do_math/review_engine.py` 1134~1140행 `_defer_review_for_research`
- 검증자: `.claude/skills/do-math/scripts/do_math/review_cycle.py` 305~308행 `validate_sealed_review`
- 공통 구현을 둘 자리: `review_cycle.py` 596행 `research_schema` 앞

### 기준
`임시/do-math_검증_20260925_opus/동결.md` 「목적 진술」 261행:

```
같은 계약·검사·인터페이스·기능을 단계별로 다르게 구현한 곳은 정의와 소비자 전건을 확인해 공통 구현으로 정리한다.
```

`GLOSSARY.md` 635행:

```
상위 활동이 고정한 질문·대상·필수 원자료에 대해 실제 근거, 답과 미해결을 반환하는 작업 예산의 활동이다.
```

### 영향
고정 조사 요청의 `request_digest`는 질문·제안 판본·원자료 `ref`/`sha256`/`bytes`를 묶는 봉인이다. 생산자 `review_engine.py` 1138~1140행은 이 값을 `canonical_json({'question', 'proposal_digest', 'sources'})`의 SHA-256으로 계산한다. 재생 검증자 `review_cycle.py` 305~308행은 같은 식을 다시 적어 대조한다. 같은 값은 조사 스키마의 `enum`(`review_engine.py` 1165행)과 조사자 출력 검사(`review_cycle.py` 658행)에도 쓰인다. 두 식 중 하나만 바뀌면 이미 수행된 조사를 포함한 봉인 검토가 `supplemental fixed source digest changed`로 재생에 실패하고, 재심·활성화(`review_engine.py` 116·181행, `knowledge.py` 463·704행)가 막힌다.

수정은 `review_cycle.research_request_digest` 하나로 계산을 모으고 양쪽이 호출한다. `canonical_json`은 키를 정렬하므로 사전 구성 순서와 무관하게 결과 바이트가 같다. 기존 봉인 값도 그대로 검증된다. 원자료가 없는 요청의 비교(`review_cycle.py` 315~316행)는 바꾸지 않는다.

### 조각 1 — .claude/skills/do-math/scripts/do_math/review_cycle.py 305~308행
원래:
```
                    from .repository import canonical_json
                    payload = {'question': record['question'], 'proposal_digest': cycle['proposal_digest'],
                               'sources': [{k: s[k] for k in ('ref', 'sha256', 'bytes')} for s in sources]}
                    if hashlib.sha256(canonical_json(payload)).hexdigest() != record['request_digest']:
```
대체:
```
                    if research_request_digest(record['question'], cycle['proposal_digest'], sources) != record['request_digest']:
```

### 조각 2 — .claude/skills/do-math/scripts/do_math/review_cycle.py 596~596행
원래:
```
def research_schema():
```
대체:
```
def research_request_digest(question, proposal_digest, sources):
    """Bind a fixed investigation to its question, proposal edition and exact source bytes."""
    from .repository import canonical_json
    return hashlib.sha256(canonical_json({'question': question, 'proposal_digest': proposal_digest,
        'sources': [{key: source[key] for key in ('ref', 'sha256', 'bytes')} for source in sources]})).hexdigest()


def research_schema():
```

### 조각 3 — .claude/skills/do-math/scripts/do_math/review_engine.py 1134~1140행
원래:
```
        for request, specs in zip(requests, source_specs):
            request_id = f"{execution_id}:{request['id']}"
            record = updated['research'][request_id]
            record['source_records'] = specs
            record['request_digest'] = hashlib.sha256(canonical_json({'question': record['question'],
                'proposal_digest': updated['proposal_digest'],
                'sources': [{key: s[key] for key in ('ref', 'sha256', 'bytes')} for s in specs]})).hexdigest()
```
대체:
```
        from .review_cycle import research_request_digest
        for request, specs in zip(requests, source_specs):
            request_id = f"{execution_id}:{request['id']}"
            record = updated['research'][request_id]
            record['source_records'] = specs
            record['request_digest'] = research_request_digest(record['question'], updated['proposal_digest'], specs)
```


### 판정
확정: 승인 · 승인기 [1, 2, 3] · 기각기 [] · 처분: 승인하되 고치지 않는다
최종 판정: 승인
최종 처분: 승인하되 고치지 않는다

### 근거
- 기 1: 승인하되 고치지 않는다
- 기 2: 수리한다
- 기 3: 수리한다

## R1-33

### 원문
제목: 대체 자리의 위임 권한 결속을 입장 허가와 입력 기록이 따로 구성한다

### 위치
- `.claude/skills/do-math/scripts/do_math/review_engine.py` 314~320행 `_admit_review_execution`
- 같은 파일 851~859행 `_record_review_input`
- 공통 구현을 둘 자리: 630행 `_review_replacement_authority` 정의 앞
- 소비자: `.claude/skills/do-math/scripts/do_math/review_cycle.py` 432~454행 `replacement_authority`

### 기준
`임시/do-math_검증_20260925_opus/동결.md` 「목적 진술」 261행:

```
같은 계약·검사·인터페이스·기능을 단계별로 다르게 구현한 곳은 정의와 소비자 전건을 확인해 공통 구현으로 정리한다.
```

`.claude/skills/do-math/AGENTS.md` 8행:

```
현재 입력의 구조·참조·권한·증거·현재성 검사는 유지한다.
```

### 영향
위임으로 승인된 대체 자리는 적용된 위임 신청 해시와 두 판정 실행 해시를 `delegation_authority`로 봉인한다. 이 결속을 두 곳이 각각 만든다. 입장 허가 결속 `admissions[eid]`는 314~320행이 만들고, 전달 입력 결속 `input_bindings[eid]`는 851~859행이 만든다. `review_cycle.replacement_authority` 432~454행은 둘 중 하나를 읽어 위임 신청·판정 실행이 입장 뒤 바뀌지 않았는지 검사한다. 두 구성은 지금 같은 필드를 쓰지만 표기가 다르다. 314~320행은 `app['id']`를 쓰고, 851~859행은 `replacement['case']['application_id']`를 쓰며 들여쓰기도 다르다. 한쪽만 바뀌면 같은 실행에 대해 두 결속이 달라지고, 권한 재검사가 어느 결속을 읽느냐에 따라 결과가 갈린다.

수정은 `_delegation_authority_binding(cycle, action)` 한 메서드가 결속을 만들고 두 호출자가 공유한다. 대체가 아닌 행동과 위임 없는 대체에서는 `None`을 돌려 기존처럼 필드를 만들지 않는다. 결속 값은 바뀌지 않는다. `app`는 `application_id` 키로 찾은 레코드이므로 두 식의 `application_id` 값도 같다. 영향 범위는 `review_engine.py`의 두 메서드, 이를 부르는 `engine.py` 683행 `_register_execution`, `review_engine.py` 975·1116행의 입력 기록 경로이다.

### 조각 1 — .claude/skills/do-math/scripts/do_math/review_engine.py 314~320행
원래:
```
        if action.get('replacement_for') is not None:
            replacement = cycle['replacement_actions'][f"{action['stage']}:{action['round']}:{action['slot']}"]
            if replacement.get('delegation_id'):
                app = self.runtime['delegation_applications'][replacement['case']['application_id']]
                binding['delegation_authority'] = {'application_id': app['id'], 'application_sha256': kr.digest(app),
                    'judgment_executions': {j['execution_id']: kr.digest(self.runtime['executions'][j['execution_id']])
                                           for j in app['judgments'].values()}}
```
대체:
```
        delegation_authority = self._delegation_authority_binding(cycle, action)
        if delegation_authority is not None:
            binding['delegation_authority'] = delegation_authority
```

### 조각 2 — .claude/skills/do-math/scripts/do_math/review_engine.py 630~630행
원래:
```
    def _review_replacement_authority(self, action, execution_id=None):
```
대체:
```
    def _delegation_authority_binding(self, cycle, action):
        """Seal the applied delegation behind a replacement slot, if one authorizes it."""
        if action.get('replacement_for') is None:
            return None
        replacement = cycle['replacement_actions'][f"{action['stage']}:{action['round']}:{action['slot']}"]
        if not replacement.get('delegation_id'):
            return None
        app = self.runtime['delegation_applications'][replacement['case']['application_id']]
        return {'application_id': app['id'], 'application_sha256': kr.digest(app),
                'judgment_executions': {j['execution_id']: kr.digest(self.runtime['executions'][j['execution_id']])
                                        for j in app['judgments'].values()}}

    def _review_replacement_authority(self, action, execution_id=None):
```

### 조각 3 — .claude/skills/do-math/scripts/do_math/review_engine.py 851~859행
원래:
```
        if action.get('replacement_for') is not None:
            key = f"{action['stage']}:{action['round']}:{action['slot']}"
            replacement = cycle['replacement_actions'][key]
            if replacement.get('delegation_id'):
                application_id = replacement['case']['application_id']
                app = self.runtime['delegation_applications'][application_id]
                binding['delegation_authority'] = {'application_id': application_id, 'application_sha256': kr.digest(app),
                    'judgment_executions': {j['execution_id']: kr.digest(self.runtime['executions'][j['execution_id']])
                                             for j in app['judgments'].values()}}
```
대체:
```
        delegation_authority = self._delegation_authority_binding(cycle, action)
        if delegation_authority is not None:
            binding['delegation_authority'] = delegation_authority
```


### 판정
확정: 승인 · 승인기 [1, 2, 3] · 기각기 [] · 처분: 승인하되 고치지 않는다
최종 판정: 승인
최종 처분: 승인하되 고치지 않는다

### 근거
- 기 1: 승인하되 고치지 않는다
- 기 2: 수리한다
- 기 3: 수리한다

## R1-35

### 원문
제목: 철회 검사가 공통 철회 검증기가 이미 거부한 학술 요구 과제를 다시 검사한다

### 위치
- `.claude/skills/do-math/scripts/do_math/task_scope.py` 35~36행 `_validate`
- `.claude/skills/do-math/scripts/do_math/submission.py` 844행 `_payload_issues`의 `disposition`
- 공통 검증기: `task_scope.py` 58~59행 `validate_withdrawal_scope`

### 기준
`임시/do-math_검증_20260925_opus/동결.md` 「목적 진술」 261행:

```
같은 계약·검사·인터페이스·기능을 단계별로 다르게 구현한 곳은 정의와 소비자 전건을 확인해 공통 구현으로 정리한다. 반복 검증·전체 상태 복사·파일 접근·Git 호출을 추적하고 불필요한 비용을 줄인다.
```

### 영향
`validate_withdrawal_scope`(`task_scope.py` 50~69행)는 수신자·생산자가 함께 쓰는 공통 철회 범위 검사다. 이 검사는 58~59행에서 `academic_requirement_id`가 있는 과제를 `protected obligations require authoritative item dispositions`로 거부한다.

- 수신자 `_validate`는 31행에서 이 검증기를 먼저 부른다. 그래서 35~36행의 `academic requirement task cannot be withdrawn autonomously`에는 도달하지 못한다.
- 생산자 검사 `submission.py` 838행도 같은 검증기를 먼저 부른다. 그래서 844행 `require(not task.get("academic_requirement_id"), ...)`는 항상 참이다.

두 줄은 같은 경계를 서로 다른 문구로 다시 적은 죽은 검사다. 독자가 학술 요구 과제의 철회 거부를 세 곳에서 따로 유지해야 하는 것처럼 읽게 만든다. 지워도 거부되는 입력과 실제로 보고되는 오류 문구는 바뀌지 않는다. 이 문구를 기대하는 시험은 없다(저장소 전체 검색). graphify `affected scripts/do_math/task_scope.py` 결과에는 `submission.py`, `decision_engine.py`, `engine.py`, `test_task_scope.py`, `test_redesign_TASKS.py` 등이 포함된다.

### 조각 1 — .claude/skills/do-math/scripts/do_math/task_scope.py 35~36행
원래:
```
    if task.get("academic_requirement_id"):
        raise ValueError("academic requirement task cannot be withdrawn autonomously: " + task_id)
```
대체:
```

```

### 조각 2 — .claude/skills/do-math/scripts/do_math/submission.py 844~844행
원래:
```
            require(not task.get("academic_requirement_id"), "academic requirements cannot be withdrawn autonomously")
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
- 기 2: 수리한다
- 기 3: 수리한다

## R1-36

### 원문
제목: `repetition_hold`가 읽지 않는 `instance` 인자를 받는다

### 위치
- 정의: `.claude/skills/do-math/scripts/do_math/revisions.py` 131~132행
- 호출: `revisions.py` 149·213·234·248·253·282행, `.claude/skills/do-math/scripts/do_math/planning.py` 690행
- 시험 호출: `.claude/skills/do-math/scripts/tests/test_questions.py` 97~98행, `.claude/skills/do-math/scripts/tests/test_redesign_TASKS.py` 591·592·827·866행, `.claude/skills/do-math/scripts/tests/test_walkthrough_followup.py` 331·354행

### 기준
`임시/do-math_검증_20260925_opus/동결.md` 「목적 진술」 261행:

```
사용자 요청에 따라 do-math 정본 전체의 불필요한 호환 요소·죽은 인자, 생산자와 소비자의 계약 불일치, 존재 목적을 위배하는 구현, 같은 기능을 불합리하게 수행하는 비효율, 최근 수리의 불충분함과 영향 누락을 발견하고 수리한다.
```

`.claude/skills/do-math/AGENTS.md` 5행:

```
설계를 바꾸면 구현·호출부·스키마·테스트·예시·문서를 같은 변경에서 새 계약으로 교체한다.
```

### 영향
`repetition_hold(instance, runtime, lineage, lineage_id)`의 본문은 `active_repetition_holds(runtime)`만 읽는다(132행). 모든 호출자가 `instance`를 넘기지만 값은 쓰이지 않는다. 보류 판정이 인스턴스 설정(예: `*_limit`)이나 결정에 기대는 것처럼 읽히므로, 호출자는 인스턴스를 바꾸면 보류가 풀리는지 확인해야 하는 잘못된 전제를 갖게 된다. 실제 해소는 `runtime.history`의 `continued` 영수증(126~127행)뿐이다.

수정은 인자를 지우고 제품 호출 7곳과 시험 호출 7곳을 새 서명으로 바꾼다. `tests/test_static_review_repairs.py` 563·569행은 `patch('do_math.revisions.repetition_hold', return_value=False)`라 서명과 무관하다. 문서(`GLOSSARY.md`, `README.md`, `references/CLI-실행-계약.md`)는 레코드 종류 `repetition_hold`만 언급하고 이 함수 서명은 적지 않는다. 동작과 반환값은 바뀌지 않는다. graphify `affected scripts/do_math/revisions.py` 결과에는 `planning.py`, `revision_engine.py`, `governance.py`, `test_questions.py`, `test_redesign_TASKS.py` 등이 포함된다.

### 조각 1 — .claude/skills/do-math/scripts/do_math/revisions.py 131~131행
원래:
```
def repetition_hold(instance, runtime, lineage, lineage_id):
```
대체:
```
def repetition_hold(runtime, lineage, lineage_id):
```

### 조각 2 — .claude/skills/do-math/scripts/do_math/revisions.py 149~149행
원래:
```
        hold=repetition_hold(instance,runtime,lineage,key)
```
대체:
```
        hold=repetition_hold(runtime,lineage,key)
```

### 조각 3 — .claude/skills/do-math/scripts/do_math/revisions.py 213~213행
원래:
```
        change=decision.get('change',{});hold=repetition_hold(instance,runtime,lineage,lineage_id)
```
대체:
```
        change=decision.get('change',{});hold=repetition_hold(runtime,lineage,lineage_id)
```

### 조각 4 — .claude/skills/do-math/scripts/do_math/revisions.py 234~234행
원래:
```
    if limit is not None and count>=limit and not repetition_hold(instance,runtime,lineage,lineage_id):
```
대체:
```
    if limit is not None and count>=limit and not repetition_hold(runtime,lineage,lineage_id):
```

### 조각 5 — .claude/skills/do-math/scripts/do_math/revisions.py 248~248행
원래:
```
    if outcome in {'revised','authored','reauthored'} and not repetition_hold(instance,runtime,lineage,lineage_id):
```
대체:
```
    if outcome in {'revised','authored','reauthored'} and not repetition_hold(runtime,lineage,lineage_id):
```

### 조각 6 — .claude/skills/do-math/scripts/do_math/revisions.py 253~253행
원래:
```
        if repetition_hold(instance, runtime, lineage, lineage_id):
```
대체:
```
        if repetition_hold(runtime, lineage, lineage_id):
```

### 조각 7 — .claude/skills/do-math/scripts/do_math/revisions.py 282~282행
원래:
```
    hold = repetition_hold(instance, runtime, lineage, key)
```
대체:
```
    hold = repetition_hold(runtime, lineage, key)
```

### 조각 8 — .claude/skills/do-math/scripts/do_math/planning.py 690~690행
원래:
```
        hold = repetition_hold(instance,runtime,'exhaustion_empty',receipt['lineage_id'])
```
대체:
```
        hold = repetition_hold(runtime,'exhaustion_empty',receipt['lineage_id'])
```

### 조각 9 — .claude/skills/do-math/scripts/tests/test_questions.py 97~98행
원래:
```
        original = revisions.repetition_hold(host.instance, host.runtime,
                                             'selection_failure', 'population')
```
대체:
```
        original = revisions.repetition_hold(host.runtime, 'selection_failure', 'population')
```

### 조각 10 — .claude/skills/do-math/scripts/tests/test_redesign_TASKS.py 591~591행
원래:
```
        self.assertTrue(revisions.repetition_hold(instance, runtime, 'selection_failure', 'population-1'))
```
대체:
```
        self.assertTrue(revisions.repetition_hold(runtime, 'selection_failure', 'population-1'))
```

### 조각 11 — .claude/skills/do-math/scripts/tests/test_redesign_TASKS.py 592~592행
원래:
```
        self.assertFalse(revisions.repetition_hold(instance, runtime, 'selection_failure', 'population-2'))
```
대체:
```
        self.assertFalse(revisions.repetition_hold(runtime, 'selection_failure', 'population-2'))
```

### 조각 12 — .claude/skills/do-math/scripts/tests/test_redesign_TASKS.py 827~827행
원래:
```
        self.assertEqual(revisions.repetition_hold(i,r,'selection_failure','population')['owner'],'user')
```
대체:
```
        self.assertEqual(revisions.repetition_hold(r,'selection_failure','population')['owner'],'user')
```

### 조각 13 — .claude/skills/do-math/scripts/tests/test_redesign_TASKS.py 866~866행
원래:
```
                self.assertTrue(revisions.repetition_hold(instance, runtime, 'exhaustion_empty', 'same-input'))
```
대체:
```
                self.assertTrue(revisions.repetition_hold(runtime, 'exhaustion_empty', 'same-input'))
```

### 조각 14 — .claude/skills/do-math/scripts/tests/test_walkthrough_followup.py 331~331행
원래:
```
        hold = revisions.repetition_hold(engine.instance, engine.runtime, 'selection_failure', receipts[-1]['lineage_id'])
```
대체:
```
        hold = revisions.repetition_hold(engine.runtime, 'selection_failure', receipts[-1]['lineage_id'])
```

### 조각 15 — .claude/skills/do-math/scripts/tests/test_walkthrough_followup.py 354~354행
원래:
```
        hold = revisions.repetition_hold(engine.instance, engine.runtime, 'selection_failure', lineage)
```
대체:
```
        hold = revisions.repetition_hold(engine.runtime, 'selection_failure', lineage)
```


### 판정
확정: 승인 · 승인기 [1, 2, 3] · 기각기 [] · 처분: 승인하되 고치지 않는다
최종 판정: 승인
최종 처분: 승인하되 고치지 않는다

### 근거
- 기 1: 승인하되 고치지 않는다
- 기 2: 수리한다
- 기 3: 수리한다

## R1-M3

### 원문
구성: R1-13 · R1-52

### 위치
.claude/skills/do-math/scripts/do_math/execution_profiles.py 233행(`build_profiles`가 profile의 `ai.provider`를 정함)과 .claude/skills/do-math/scripts/do_math/model_runner.py 284~293행(`ModelRunner.run`이 실제 실행 CLI를 고름). 같은 판정의 정의는 .claude/skills/do-math/scripts/do_math/provider_wait.py 6~7행 `provider_for`다. 가져오기를 넣을 자리는 execution_profiles.py 15행과 model_runner.py 18행 뒤다.

### 기준
임시/do-math_검증_20260925_opus/동결.md 261행(목적 진술):

```
같은 계약·검사·인터페이스·기능을 단계별로 다르게 구현한 곳은 정의와 소비자 전건을 확인해 공통 구현으로 정리한다.
```

.claude/skills/do-math/references/모델과-실행예산.md 11행:

```
Claude와 Codex는 같은 모델 배정·예산 절차를 사용한다. `claude:` 뒤에 Claude 모델 이름이나 별칭을 쓰거나 `claude-`로 시작하는 전체 모델 ID를 쓰면 Claude CLI가 실행한다. 그 밖의 이름은 Codex CLI에 전달한다.
```

### 영향
문서가 정한 규칙은 하나다. "`claude:`·`claude-` 접두면 Claude, 나머지는 Codex"다. 그런데 같은 모델 문자열에서 세 값이 따로 나온다.

- profile의 `ai.provider`: execution_profiles.py 233행이 정한다. initialization.py `adapter_for`가 이 값을 소비한다.
- 공급자 한도 대기의 키: provider_wait.py `provider_for`가 정한다. 호출자는 provider_engine.py 95·112행과 provider_wait.py 52행이다.
- 실제 실행 CLI: model_runner.py 285~291행이 고른다.

지금은 세 구현의 결과가 같다. 하지만 한 자리만 고치면 서로 어긋난다. 예를 들어 profile은 codex로 봉인되고 러너는 Claude CLI를 실행할 수 있다. 그러면 공급자 한도 대기(`PW-<provider>`)와 능력 증거가 실제로 실행한 CLI와 다른 공급자에 묶인다. 운영 점검이 읽는 profile 공급자도 실제 실행과 달라진다.

수리하면 판정이 모두 `provider_for` 하나를 거친다. 입력별 결과는 바뀌지 않는다. `claude:haiku`는 `haiku`로 Claude에 가고, `claude-...` 전체 ID는 `removeprefix("claude:")`를 거쳐도 그대로 Claude에 간다. 그 밖의 이름은 Codex에 간다. `claude:` 뒤가 비면 내는 오류와 Codex 경로의 `claude_only_assigned_model` 제거도 러너에 남는다. provider_wait.py는 datetime·math만 가져오므로 새 가져오기가 순환을 만들지 않는다.

### 근거
두 구성 항목은 위치·기준·수리 방향이 같다. 차이는 가져오기의 형태와 러너 조각의 범위뿐이다. 사본에서 execution_profiles.py 233행, model_runner.py 284~293행, provider_wait.py 6~7행·2~3행의 import를 확인했다. provider_engine.py 6·95·112행과 provider_wait.py 52행의 `provider_for` 호출도 확인했다. 두 기준 인용은 동결.md 261행과 모델과-실행예산.md 11행에서 실재를 확인했다.

R1-13에서 모델과-실행예산.md 11행 기준 인용과 `adapter_for` 소비 경로를 취했다. R1-52에서 운영 점검이 읽는 profile 공급자라는 영향과 호출자 목록을 취했다. R1-13이 인용한 test_claude_adapter.py 208~218행의 라우팅 시험 통과 주장은 옮기지 않았다. 병합자는 변경본을 실행하지 않으므로 확인할 수 없다.

가져오기 조각은 이렇게 처리했다. execution_profiles.py는 조각 1(15행)을 `.provider_wait`·`.state_contract` 두 줄로 다시 썼다. 기존 상대 가져오기의 알파벳 순서를 지키려는 것이다. 그래서 틈 삽입 조각 2는 원래대로 둔다. model_runner.py는 `do_math.claude_stream` 뒤에 붙이는 것이 R1-13과 R1-52에서 같은 결과다. 그래서 조각 4는 원래대로 두고 틈 삽입 조각 5로 넣는다. 러너 조각 6은 R1-52의 넓은 범위(284~293행)를 따라 `def` 줄과 Codex 경로까지 원문대로 유지하고 분기 두 개를 하나로 합친다.

### 조각 1 — .claude/skills/do-math/scripts/do_math/execution_profiles.py 15~15행
원래:
```
from .state_contract import STATE_FORMAT_VERSION
```
대체:
```
from .provider_wait import provider_for
from .state_contract import STATE_FORMAT_VERSION
```

### 조각 2 — .claude/skills/do-math/scripts/do_math/execution_profiles.py 행 15 뒤
대체:
```

```

### 조각 3 — .claude/skills/do-math/scripts/do_math/execution_profiles.py 233~233행
원래:
```
                provider = "claude" if model.startswith(("claude:", "claude-")) else "codex"
```
대체:
```
                provider = provider_for(model)
```

### 조각 4 — .claude/skills/do-math/scripts/do_math/model_runner.py 18~18행
원래:
```
from do_math.claude_stream import provider_limit
```
대체:
```
from do_math.claude_stream import provider_limit
```

### 조각 5 — .claude/skills/do-math/scripts/do_math/model_runner.py 행 18 뒤
대체:
```
from do_math.provider_wait import provider_for
```

### 조각 6 — .claude/skills/do-math/scripts/do_math/model_runner.py 284~293행
원래:
```
    def run(self, *, model: str, **options) -> dict:
        if model.startswith("claude:"):
            name = model.removeprefix("claude:")
            if not name.strip():
                raise ValueError("claude: requires a Claude model name or alias")
            return self.claude.run(model=name, **options)
        if model.startswith("claude-"):
            return self.claude.run(model=model, **options)
        options.pop("claude_only_assigned_model", None)
        return self.codex.run(model=model, **options)
```
대체:
```
    def run(self, *, model: str, **options) -> dict:
        if provider_for(model) == "claude":
            name = model.removeprefix("claude:")
            if not name.strip():
                raise ValueError("claude: requires a Claude model name or alias")
            return self.claude.run(model=name, **options)
        options.pop("claude_only_assigned_model", None)
        return self.codex.run(model=model, **options)
```


### 판정
확정: 승인 · 승인기 [1, 2, 3] · 기각기 [] · 처분: 승인하되 고치지 않는다
최종 판정: 승인
최종 처분: 승인하되 고치지 않는다

### 근거
- 기 1: 승인하되 고치지 않는다
- 기 2: 승인하되 고치지 않는다
- 기 3: 수리한다

## R1-M5

### 원문
구성: R1-15 · R1-51

### 위치
.claude/skills/do-math/scripts/do_math/codex_adapter.py 291행(`LocalCLIAdapter.collect`). 같은 함수 249~255행이 `barrier`를 한 번 계산하고, 거짓이면 `termination_barrier_unconfirmed` 사유와 함께 `incomplete`를 즉시 반환한다. `barrier`는 그 뒤 다시 계산되지 않으므로 291행에 도달할 때 항상 참이다.

### 기준
동결문 임시/do-math_검증_20260925_opus/동결.md 261행(목적 진술):

```
사용자 요청에 따라 do-math 정본 전체의 불필요한 호환 요소·죽은 인자, 생산자와 소비자의 계약 불일치, 존재 목적을 위배하는 구현, 같은 기능을 불합리하게 수행하는 비효율, 최근 수리의 불충분함과 영향 누락을 발견하고 수리한다.
```

### 영향
291행 `if not barrier: reasons.append(...)`는 어떤 입력에서도 실행되지 않는 죽은 분기다. 그런데도 이 행은 산출을 읽은 뒤 종료 장벽을 다시 확인하는 것처럼 보인다. 그래서 읽는 사람은 장벽 미확인이 수집 뒤 `reasons`에도 들어갈 수 있다고 오해한다. `reasons`와 `termination_barrier.confirmed`를 소비하는 model_runner.py `verified_native_final`(311~317행)을 고치는 사람도 이미 250~255행에서 닫힌 경로를 한 번 더 방어하게 된다. 행을 지워도 동작은 같다. 조기 반환(250~255행)과 수집 결과의 `termination_barrier.confirmed`(299~300행)가 장벽 계약을 그대로 표현한다. 시험 영향: scripts/tests/test_codex_adapter.py 191행의 장벽 미확인 시험은 252행 조기 반환의 사유를 검사하므로 삭제 뒤에도 통과한다. 291행 분기만 검사하는 시험은 없다.

### 근거
두 구성 항목은 같은 행을 같은 동결문 기준으로 지적하고, 같은 조각(291행 삭제)을 낸다. 어긋남은 없다. 사본 codex_adapter.py 249~255행·291행·299~300행, model_runner.py 311~317행, 동결문 261행을 대조해 성립을 확인했다. R1-15의 시험 좌표 「test_codex_adapter.py 181~191행」은 경로를 scripts/tests/test_codex_adapter.py로 바로잡고, 사유 단언이 있는 191행만 옮겼다. R1-51의 「운영 점검처럼 `reasons`를 읽는 소비자」는 구체 좌표가 없어서 버렸다. 두 항목의 대체 블록은 빈 줄 하나였다. 조각 계약상 빈 줄 대체는 삭제와 구별되지 않고, 두 항목의 취지가 행 삭제이므로 빈 블록(삭제)으로 썼다. 지급 키 밖의 새 결함은 보지 못했다.

### 조각 1 — .claude/skills/do-math/scripts/do_math/codex_adapter.py 291~291행
원래:
```
        if not barrier: reasons.append("termination_barrier_unconfirmed")
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

## R1-M10

### 원문
구성: R1-30 · R1-65

### 위치
`.claude/skills/do-math/scripts/do_math/review_cycle.py`:

- 생산자: `authorize_record_replacement`의 전사 검증 1112~1123행, 봉인 입력 1129~1132행
- 검증자: `_replay_replacement`의 전사 검증 404~416행, 봉인 입력 417~419행
- 공통 구현을 둘 자리: 387행 `_replay_replacement` 정의 앞

### 기준
`임시/do-math_검증_20260925_opus/동결.md` 「목적 진술」 261행:

```
같은 계약·검사·인터페이스·기능을 단계별로 다르게 구현한 곳은 정의와 소비자 전건을 확인해 공통 구현으로 정리한다.
```

같은 문단:

```
반복 검증·전체 상태 복사·파일 접근·Git 호출을 추적하고 불필요한 비용을 줄인다. 검증 경계의 의미와 오류 처분을 유지하며
```

`.claude/skills/do-math/AGENTS.md` 8행:

```
현재 입력의 구조·참조·권한·증거·현재성 검사는 유지한다.
```

### 영향
대체 승인(`authorize_record_replacement`)은 손상된 자리의 전사에서 해시가 맞는 메시지만 골라 보존하고, 누락 위치를 나눈다(1112~1123행). 그다음 봉인 입력을 만들어 `sealed_input_sha256`과 `omitted_indices`를 기록한다(1129~1137행). `validate_sealed_review`(355행)가 부르는 `_replay_replacement`는 보관 전사로 같은 선별과 같은 봉인 입력을 다시 만든다(404~419행). 그 결과를 기록값과 대조한다(420~422행). 두 구현의 선별 조건과 봉인 입력의 여섯 필드는 지금 같은 값을 내지만 따로 적혀 있다. 한쪽만 바뀌면 정상 승인된 대체의 재생이 `replacement sealed input changed`로 실패해 봉인 검토 전체가 무효가 된다. 조건이 느슨해진 쪽이 생기면 서로 다른 입력이 같은 것으로 통과해 검증 경계가 약해진다.

수리는 선별(`_verified_transcript`)과 봉인 입력(`_replacement_sealed_input`)을 한 번씩 정의하고 두 호출자가 공유하게 한다. 선별 결과, 누락 위치, 봉인 해시는 바뀌지 않는다. 승인 쪽은 계속 변경 전 `cycle`로, 재생 쪽은 `replay`로 봉인 입력을 만든다. 두 값이 쓰는 필드(`proposal_digest`, `identity_basis`, `policy_ref`, `scope_assessment`, `results`, `sealed`)는 같다. 영향 범위는 이 파일의 두 함수와 그 호출자다. 호출자는 `review_engine.py` 744행 `_authorize_review_replacement`와 `validate_sealed_review` 호출자(`review_engine.py` 116·181행, `knowledge.py` 463·704행)다. 관련 시험은 `test_review_engine.py` 651·692행의 대체 시험과 `test_review_cycle.py`다.

### 근거
두 구성 항목은 위치·기준·조각 구간이 같다. 차이는 둘이다.

첫째, 공통 선별 함수가 항목을 깊은 복사하느냐다. R1-65는 승인 쪽의 `copy.deepcopy`를 공통 함수에 옮겼다. R1-30은 복사를 뺐다. R1-30을 취했다. 사본에서 확인한 근거는 이렇다. 승인 쪽 `turns`·`manifests`는 1098행에서 이미 깊은 복사한 `n`의 목록이다. 1124~1126행 보관본은 따로 깊은 복사한다. 1127행은 새 목록을, 1128행은 새 manifest 사전을 만든다. 따라서 저장된 전사와 보관본이 객체를 공유하지 않는다. 재생 쪽은 원래 복사하지 않았고, 복사를 넣으면 검증할 때마다 보관 전사를 복사하는 비용만 더해진다. 동결문의 「전체 상태 복사」 비용 절감과도 맞는다.

둘째, 봉인 입력 함수의 이름이다. R1-65는 `_replacement_input`, R1-30은 `_replacement_sealed_input`을 썼다. 기록 필드 `sealed_input_sha256`과 지역 변수 `sealed_input`에 맞춰 R1-30의 이름을 취했다. 독스트링에는 R1-65의 「승인과 봉인 재생이 같은 값을 해시한다」는 뜻을 옮겼다.

R1-65의 「조건 아홉 개」와 R1-30의 「조건 8개」는 세는 방식이 다를 뿐이라 영향 칸에서 개수를 적지 않았다. 옮긴 인용 셋은 동결문 261행과 `.claude/skills/do-math/AGENTS.md` 8행에서 실재를 확인했다. `copy` 모듈은 8행에서 이미 import하므로 조각 1의 공통 함수가 새 import 없이 선다. 지급 키 밖의 새 결함은 보지 못했다.

### 조각 1 — .claude/skills/do-math/scripts/do_math/review_cycle.py 387~387행
원래:
```
def _replay_replacement(replay, cycle, action, instance, runtime):
```
대체:
```
def _verified_transcript(turns, manifests):
    """Pair each message whose original hash still verifies with its manifest; list the rest."""
    verified, omitted = [], []
    for position in range(max(len(turns), len(manifests))):
        if (position < len(turns) and position < len(manifests)
                and isinstance(turns[position], dict) and {'role', 'content'} <= turns[position].keys()
                and isinstance(manifests[position], dict)
                and {'sha256', 'bytes', 'index', 'proposal_digest', 'ref'} <= manifests[position].keys()
                and manifests[position]['index'] == position
                and _digest(turns[position]) == manifests[position].get('sha256')
                and len(_bytes(turns[position])) == manifests[position].get('bytes')):
            verified.append((turns[position], manifests[position]))
        else:
            omitted.append(position)
    return verified, omitted


def _replacement_sealed_input(cycle, verified_manifests):
    """Sealed replacement input; authorization and sealed replay hash this same value."""
    return {'proposal_digest': cycle['proposal_digest'], 'identity_basis': cycle.get('identity_basis'),
            'policy_ref': cycle.get('policy_ref'), 'scope_assessment': cycle.get('scope_assessment'),
            'sealed_results': {k: cycle['results'][k] for k in cycle['sealed']},
            'verified_transcript': verified_manifests}


def _replay_replacement(replay, cycle, action, instance, runtime):
```

### 조각 2 — .claude/skills/do-math/scripts/do_math/review_cycle.py 404~419행
원래:
```
    verified, omitted = [], []
    for pos in range(max(len(archive['turns']), len(archive['manifest']))):
        if (pos < len(archive['turns']) and pos < len(archive['manifest'])
                and isinstance(archive['turns'][pos], dict)
                and {'role', 'content'} <= archive['turns'][pos].keys()
                and isinstance(archive['manifest'][pos], dict)
                and {'sha256', 'bytes', 'index', 'proposal_digest', 'ref'} <= archive['manifest'][pos].keys()
                and archive['manifest'][pos]['index'] == pos
                and _digest(archive['turns'][pos]) == archive['manifest'][pos].get('sha256')
                and len(_bytes(archive['turns'][pos])) == archive['manifest'][pos].get('bytes')):
            verified.append(archive['manifest'][pos])
        else:
            omitted.append(pos)
    sealed_input = {'proposal_digest': replay['proposal_digest'], 'identity_basis': replay.get('identity_basis'),
        'policy_ref': replay.get('policy_ref'), 'scope_assessment': replay.get('scope_assessment'),
        'sealed_results': {k: replay['results'][k] for k in replay['sealed']}, 'verified_transcript': verified}
```
대체:
```
    verified, omitted = _verified_transcript(archive['turns'], archive['manifest'])
    sealed_input = _replacement_sealed_input(replay, [manifest for _, manifest in verified])
```

### 조각 3 — .claude/skills/do-math/scripts/do_math/review_cycle.py 1112~1123행
원래:
```
    verified, omitted = [], []
    for position in range(max(len(turns), len(manifests))):
        if (position < len(turns) and position < len(manifests)
                and isinstance(turns[position], dict) and {'role', 'content'} <= turns[position].keys()
                and isinstance(manifests[position], dict)
                and {'sha256', 'bytes', 'index', 'proposal_digest', 'ref'} <= manifests[position].keys()
                and manifests[position]['index'] == position
                and _digest(turns[position]) == manifests[position].get('sha256')
                and len(_bytes(turns[position])) == manifests[position].get('bytes')):
            verified.append((copy.deepcopy(turns[position]), copy.deepcopy(manifests[position])))
        else:
            omitted.append(position)
```
대체:
```
    verified, omitted = _verified_transcript(turns, manifests)
```

### 조각 4 — .claude/skills/do-math/scripts/do_math/review_cycle.py 1129~1132행
원래:
```
    sealed_input = {'proposal_digest': cycle['proposal_digest'], 'identity_basis': cycle.get('identity_basis'),
                    'policy_ref': cycle.get('policy_ref'), 'scope_assessment': cycle.get('scope_assessment'),
                    'sealed_results': {k: cycle['results'][k] for k in cycle['sealed']},
                    'verified_transcript': [manifest for _, manifest in verified]}
```
대체:
```
    sealed_input = _replacement_sealed_input(cycle, [manifest for _, manifest in verified])
```


### 판정
확정: 승인 · 승인기 [1, 2, 3] · 기각기 [] · 처분: 승인하되 고치지 않는다
최종 판정: 승인
최종 처분: 승인하되 고치지 않는다

### 근거
- 기 1: 승인하되 고치지 않는다
- 기 2: 수리한다
- 기 3: 수리한다
