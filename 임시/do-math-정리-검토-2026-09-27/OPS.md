# OPS 영역 정리 검토 (운영·초기화·스크립트)

기준 문서: `C:/math/임시/do-math-정리-검토-2026-09-27/기준.md`. 좌표는 따로 적지 않으면 `C:/math/.claude/skills/do-math/` 기준의 상대 경로이고, 행 번호는 main `9b434f4` 작업 트리(clean)의 현재 원문이다. 저장소의 어떤 파일도 고치지 않았고 시험도 실행하지 않았다. 동작 확인은 저장소를 바꾸지 않는 파이썬 한 줄 수준의 측정만 했으며, 명령과 결과는 해당 후보와 6절에 적었다.

## 1. 읽은 범위

### 전문을 읽은 파일

| 파일 | 행 수 |
|---|---|
| `C:/math/임시/do-math-정리-검토-2026-09-27/기준.md` | 238 |
| `AGENTS.md` | 11 |
| `C:/math/docs/do-math/검사-경량화-이음새-계약.md` | 245 |
| `scripts/do_math/governance.py` | 1191 |
| `scripts/do_math/governance_engine.py` | 434 |
| `scripts/do_math/initialization.py` | 264 |
| `scripts/do_math/reporting.py` | 257 |
| `scripts/do_math/repair_execution.py` | 216 |
| `scripts/do_math/trust_inventory.py` | 236 |
| `scripts/do_math/trust_validation.py` | 175 |
| `scripts/do_math/__init__.py` | 1 |
| `scripts/do_math.py` | 7 |
| `scripts/operator_bootstrap.py` | 176 |
| `scripts/check_coverage.py` | 357 |
| `scripts/setup_lean.py` | 286 |
| `scripts/probe_cli.py` | 141 |
| `scripts/operator_schedule.ps1` | 88 |
| `scripts/test_categories.py` | 92 |
| `C:/math/임시/경량화-조사-2026-09-26/OPS.md` | 357 |
| `C:/math/임시/경량화-조사-2026-09-26/결과-F.md` | 95 |
| `C:/math/임시/시험-경량화-2026-09-26/진단-B4-2.md` | 58 |
| `C:/math/기억/색인.md` | 41 |

세 커밋(`8d2ffd0`, `379a171`, `9b434f4`)이 영역 파일에 준 변경은 `git show <커밋> -- <경로>`로 모두 읽었다. `8d2ffd0`는 9개 파일(+666/−581), `379a171`은 8개 파일(+154/−183), `9b434f4`는 2개 파일(+7/−6)을 바꿨다. 이 가운데 `trust_inventory.py`와 `trust_validation.py`는 `8d2ffd0`에서 사실상 새로 쓰였으므로, 그 두 파일은 diff 대신 현재 원문 전문으로 검토했다.

### 일부만 읽은 파일

아래 파일은 영역과 이음새를 이루는 부분만 읽었다(기준 6절).

| 파일 | 읽은 행 |
|---|---|
| `C:/math/docs/do-math/검사-경량화-설계-2026-09-26.md` | 1-182(요약, 1-3절), 229-428(5-10절과 결정 근거). 파견문이 정한 3절과 5.3절이 모두 이 안에 든다 |
| `scripts/do_math/record_schemas/schemas.py` | 24-54, 400-431, 470-512, 558-566, 602-617, 653-672 |
| `scripts/do_math/record_schemas/__init__.py` | 120-145, 205-240, 330-345, 495-512 |
| `scripts/do_math/state_contract.py` | 135-148 |
| `scripts/do_math/state_checks.py` | 215-230 |
| `scripts/do_math/lifecycle_engine.py` | 95-124, 160-180, 205-216, 300-316, 478-485, 650-700, 855-866, 1176-1200 |
| `scripts/do_math/engine.py` | 252-268, 4095-4150 |
| `scripts/do_math/scheduled_operator.py` | 38-44, 120-217, 610-635 |
| `scripts/do_math/file_io.py` | 119-148, 212-217 |
| `scripts/do_math/git_store.py` | 8-27, 580-592 |
| `scripts/do_math/repository.py` | 955-996 |
| `scripts/do_math/control_contracts.py` | 73-77, 140-185 |
| `scripts/do_math/model_runner.py` | 36-52 |
| `scripts/do_math/preflight.py` | 94-134 |
| `scripts/do_math/planning.py` | 360-375 |
| `scripts/do_math/execution_profiles.py` | 393-407 |
| `scripts/do_math/submission.py` | 237-240 |
| `scripts/tests/test_redesign_EVIDENCE.py` | 1-40, 268-305, 352-356, 클래스·함수 목록 |
| `scripts/tests/test_environment_validation.py` | 175-195 |
| `scripts/tests/test_governance_engine.py` | 144-156, 414-424, `_governance_control` 호출 행 |
| `scripts/tests/test_walkthrough_repairs.py` | 86-104 |
| `scripts/tests/test_redesign_GOVERNANCE.py` | 782-790 |
| `references/초기화-효율과-정비.md` | 85-100 |
| `references/CLI-실행-계약.md` | 325-360 |
| `C:/math/기억/layer1/M-0350.md` | 45-60 |

파견문이 정한 파일 가운데 읽지 못한 것은 없다. 4.1·4.2절의 모든 종류를 검토했다.

## 2. 영역 판정

OPS 영역의 제품 모듈은 세 경량화의 방향을 대체로 따른다. `8d2ffd0`는 신뢰 환경을 툴체인 기록과 지문 대조로 다시 썼다. `379a171`은 grant 규칙, 판정 어휘, 설치 파일 집합, 초기화 중 목표 보기를 공유 정의 하나로 모았다. 그러나 두 곳이 방향에서 벗어나 있다.

가장 큰 개선 여지는 개발 도구 `check_coverage.py`와 역사적 추적표의 처리다. `9b434f4`가 opt-in 표지를 없앤 뒤로, 기본 foundation 조각이 Git이 추적하지 않는 로컬 보관소(`임시/*`)를 읽는다. 게다가 v5↔v9 역사 추적표는 리팩터마다 좌표를 고쳐야 하는 유지비를 만든다. 이 문제는 OPS-01~03으로 다룬다.

둘째 개선 여지는 신뢰 환경 두 모듈과 governance의 남은 사본과 옛 방식이다. 결박·환경 기록·기록 ID 형태가 두세 곳에 따로 정의되어 있고(OPS-05), 툴체인 기록 잠금은 공유 `os_lock` 대신 수동 복구 규칙이 붙은 잠금 파일을 쓴다(OPS-06). 결정 기록의 `revoked`·`status`에는 생산자가 없다(OPS-04). 나머지 후보는 작은 이음새, 잔재, 옛 표지다.

모듈 경계를 다시 그을 만한 개선 여지는 작다고 판단했다. `governance.py`는 크고 `repair_execution.py`는 세 관심사를 담지만, 둘로 쪼개도 지워지는 코드나 이음새가 생기지 않는다(4절).

검토했고 없음: 경계, 파생상태, 문서, 공백, 비대

## 3. 후보

#### OPS-01 기본 foundation 조각이 Git 밖 로컬 보관소를 읽어 clone·worktree에서 실패하고 시간 목표의 큰 몫을 쓴다
- 검토: 2
- 종류: 결함
- 좌표:
  - `scripts/check_coverage.py:90-100`(`_archive_directory`), `:103-153`(`validate_observations`), `:339-340`(`validate`)
  - `scripts/tests/test_redesign_EVIDENCE.py:300-301`(`test_full_trace_is_structurally_valid_not_an_execution_pass`), `:274-291`(`setUpClass`)
  - `scripts/test_categories.py:17-64`(`SHARDS`), `:65`(`LABELS`)
  - `C:/math/.gitignore:53`(`/임시/*/*`)
- 현상:
  - 전체 추적표 시험은 `check_coverage.validate`를 부른다. `validate`는 추적표의 `observed_runs` 15건마다 `_archive_directory`로 저장소 root와 그 조상에서 `임시/do-math-implementation-20260920/…`, `임시/do-math-resume-20260920/…`을 찾는다. 그 뒤 스냅숏 파일 5,161개를 해시한다.
  - 두 보관소는 `.gitignore:53`에 걸려 Git이 추적하지 않는다. 확인 명령은 `git check-ignore -v`, `git ls-files 임시/do-math-implementation-20260920`이며 결과는 0건이다.
  - `9b434f4` 이전에는 이 시험에 `@category('archive')`가 붙어 있었다. 당시 `test_categories.GROUPS`에 `archive`가 있어 이 시험은 요청할 때만 돌았다. `9b434f4`는 그룹을 조각(`SHARDS`)으로 바꾸면서 표지를 지웠다(`git show 9b434f4 -- scripts/tests/test_redesign_EVIDENCE.py`). 지금 `LABELS`는 `lean`, `resource`, `in_process`뿐이다. 따라서 이 시험은 foundation 조각을 돌릴 때마다 실행된다.
- 근거:
  - 보관소가 없는 worktree에서 이 시험이 실패한 사실이 두 곳에 기록되어 있다. `진단-B4-2.md:27`은 archive unavailable 15건, edition absent 1,284건, fixed run omits 231건을 적었다. `M-0350.md:51`은 이를 "환경 원인"으로 적고, worktree에서는 두 보관소(35MB, 384MB)를 복사하라고 남겼다. 원인을 고치지 않고 운용 지침으로 덮은 상태다.
  - 비용은 읽기 전용으로 세 번 쟀다. 명령은 `python -c "…import check_coverage as c; c.validate(T,S,Path('C:/math'))"`이다. 첫 실행은 63.08초, cProfile을 건 실행은 15.76초(그 가운데 `validate_observations` 12.95초), 파일 캐시가 데워진 뒤는 5.87초였고 오류는 모두 0건이었다.
  - `observed_runs`를 비운 구조 검사만 따로 재면 0.21-1.15초다. 조각 하나의 시간 목표는 120초다(`test_categories.py` 머리 주석).
  - `setUpClass`(`test_redesign_EVIDENCE.py:274-291`)는 `runs`와 `observed_runs`를 비우고 같은 `validate_data`를 돌린다. 오류가 있으면 실패한다. 따라서 좌표 존재와 대응 규칙은 이미 매번 검사된다. 전체 추적표 시험이 여기에 더하는 것은 역사적 실행 보관소의 무결성뿐이다.
- 제안: 보관소 대조를 기본 시험에서 빼고 명시적 명령으로만 남긴다. 방법은 `test_full_trace_is_structurally_valid_not_an_execution_pass`를 지우는 것이다. 표지 체계가 사라졌으므로 opt-in 표지를 되살리는 것보다 이쪽이 단순하다. 보관소 대조는 `python scripts/check_coverage.py`(`main`, `:343-355`)가 그대로 제공한다. 시험 파일 수정은 TSA 영역이다. 이 후보를 여기에 둔 것은 원인이 이 검사기의 Git 밖 보관소 의존에 있기 때문이다(5절에도 적었다).
- 실익:
  - clone과 worktree에서 foundation 조각이 환경 때문에 실패하는 경로가 사라진다. M-0350의 "두 보관소를 복사하라"는 운용 규칙도 필요 없어진다.
  - foundation 조각에서 측정값 기준 6-63초가 빠진다.
- 비용과 위험: 새 상태, 수명, 복구 규칙이 생기지 않는다. 역사 보관소의 바이트가 바뀌어도 기본 시험이 잡지 못한다. 다만 그 보관소는 Git 밖에 있어 원래 재현 가능한 시험 입력이 아니다.
- 기능·커버리지 영향: 있음. 기본 시험에서 역사 보관소 무결성 대조 1건이 빠지고, CLI로만 남는다.
- 사용자 결정 관련: 있음. "시험 커버리지는 크게 바꾸지 않는다. 범위 축소는 분명한 실익이 있을 때만 한다"는 결정에 해당한다. 새로 드러난 사실은 셋이다. `9b434f4`가 이 대조를 opt-in에서 기본으로 바꾼 것은 결정이 아니라 표지 체계 교체의 부수 효과였다. 이 대조는 Git 밖 입력에 의존한다. 비용은 측정했다.
- 확신도: 확인

#### OPS-02 `check_coverage.py`와 v5↔v9 추적표의 존재 이유를 다시 판정한다
- 검토: 1
- 종류: 기타. 개발 도구의 존재 이유 판정이며, 4.1절 어느 종류에도 딱 맞지 않는다.
- 좌표:
  - `scripts/check_coverage.py` 전체(357행), `:346-347`(대상 경로 기본값)
  - `C:/math/docs/do-math/implementation-v5/traceability.json`(1,349,970바이트)
  - `scripts/tests/test_redesign_EVIDENCE.py:273-404`(`TraceabilityCheckerTests`), `scripts/tests/test_redesign_EVIDENCE_binding.py`(118행), `scripts/tests/test_redesign_EVIDENCE_scope.py`(40행)
- 현상:
  - 이 도구는 v9 설계 명세의 원천 벡터(`통합-설계-명세-v9/source-vector-map.json`)와 v5 구현 좌표·시험 좌표를 잇는 추적표의 구조를 검사한다. 검사 대상은 AST로 확인한 좌표 존재, 대응 상태 규칙, 역사 실행 관찰이다. docstring(`:2-6`)은 "structural validity is never a feature pass"라고 스스로 밝힌다.
  - 추적표의 대응 상태는 `mapped` 5, `partial` 213, `gap` 50, `replaced` 9, `withdrawn` 3, `out_of_scope` 1이다. 구현 좌표 941개와 증거 좌표 687개를 담는다(읽기 전용 집계).
  - 스킬 문서는 이 추적표나 v9 명세를 가리키지 않는다. 확인한 검색은 Grep `traceability|통합-설계-명세|source-vector|implementation-v5`, 스킬 `*.md` 대상이며 결과는 0건이다.
  - 제품 코드를 리팩터하면 추적표도 고쳐야 한다. 최근 커밋의 추적표 변경은 `ded5952` +33/−33, `8d2ffd0` +7/−31, `9b434f4` +64/−133이다. `379a171`은 인용된 함수를 지우고도 추적표를 고치지 않아 시험이 깨졌고, `9b434f4`의 작업자 B4가 좌표 21곳과 항목 16개를 재판정해 고쳤다(`진단-B4-2.md:7`, `:14-22`).
- 근거:
  - 사용처 전수 검색은 Grep `check_coverage|probe_cli`, 스킬 디렉터리 대상(`__pycache__` 제외)이다. 결과 39행 가운데 `check_coverage` 관련은 23행이며 모두 시험 3개 모듈이다. 제품 코드와 스킬 문서의 사용처는 0이다.
  - 2라운드 보존 판정(`경량화-조사-2026-09-26/OPS.md:330`)은 이 도구를 스킬 밖으로 옮기는 안만 기각했다. 그 근거인 "`archive` 시험 그룹"은 `9b434f4` 뒤 존재하지 않는다(`test_categories.py:17-65`).
  - `test_redesign_EVIDENCE.py:21-28`의 `repository_root()`는 이 도구와 `docs/`가 함께 있어야 모듈 import 자체가 성공한다. 이 모듈을 import하는 `test_redesign_EVIDENCE_binding`, `_run`, `_walkthroughs`, `test_stop_flags`도 같은 조건에 묶인다.
- 제안: 추적표를 앞으로도 유지할 산출물로 둘지 사용자가 정한다.
  - 역사 기록으로 동결하는 경우: `check_coverage.py`, 추적표 검사 시험(`TraceabilityCheckerTests`, `test_redesign_EVIDENCE_binding.py`, `test_redesign_EVIDENCE_scope.py`), `repository_root()`의 `docs` 의존을 지운다. 추적표 파일은 당시 기록으로 남긴다.
  - 유지하는 경우: OPS-01과 OPS-03만 적용한다.
- 실익(동결하는 경우):
  - 검사기 357행과 추적표 검사 시험 약 290행(132+118+40)이 준다.
  - 리팩터마다 1.35MB 역사 문서를 고치는 유지비가 사라진다.
  - 네 시험 모듈의 `docs/` 의존이 사라진다.
  - 설치 파일 집합(`file_io.installation_files`)에서 개발 도구 하나가 빠져, 설치 복구 식별이 이 도구의 변경에 흔들리지 않는다.
- 비용과 위험: 제품 동작에는 영향이 없다. 설계 명세와 구현 사이의 기계적 추적성을 잃는다.
- 기능·커버리지 영향: 있음. 추적표 구조 검사와 그 음성 시험이 사라진다. 제품 기능 시험은 그대로다.
- 사용자 결정 관련: 있음. "시험 커버리지는 크게 바꾸지 않는다" 결정에 해당한다. 새로 드러난 사실은 셋이다. 추적표가 현행 스킬 문서와 연결되어 있지 않다. 경량화 리팩터가 이 추적표 때문에 시험을 깨뜨렸다. 보존 판정의 전제였던 `archive` 그룹이 사라졌다.
- 확신도: 확인. 사실은 모두 확인했고, 동결 여부는 사용자 판단이다.

#### OPS-03 실제 추적표에 입력이 없는 `check_coverage`의 두 검사 분기를 지운다
- 검토: 1
- 종류: 미사용
- 좌표:
  - `scripts/check_coverage.py:230-259`(`scope_artifact_errors`), `:265`(그 호출), `:284-311`(`runs`의 고정 실행·기계 보고 검사)
  - `scripts/tests/test_redesign_EVIDENCE_scope.py`(1개 시험), `scripts/tests/test_redesign_EVIDENCE.py:352-`(`test_fixed_run_rejects_changed_code_log_and_reported_outcome`)
- 현상:
  - `validate_data`는 추적표의 `scope_artifacts`, 각 행의 `adopted_scope`, `runs`(고정 실행, `report_path`, `report_sha256`)를 검사한다.
  - 실제 추적표에는 `scope_artifacts` 키가 없다. `adopted_scope`를 가진 행은 0개이고 `runs`는 빈 객체다. 확인 방법은 추적표를 읽기 전용으로 해석해 키 목록과 개수를 센 것이다.
  - 따라서 이 두 분기는 합성 시험 입력에서만 실행된다. `_item`의 실행 상태 검사는 `observed_runs`를 `runs`에 합친 값(`:312-313`)으로 실제 데이터에 쓰이므로 남긴다.
- 근거: 시험 쪽 사용처는 Grep `report_path|scope_artifacts|adopted_scope`로 찾았다. 추적표를 쓰는 곳은 `test_redesign_EVIDENCE.py`, `test_redesign_EVIDENCE_scope.py` 둘이다(`test_input_recovery.py`의 일치는 다른 개념). 생산자인 "MAIN run_checks.py"는 추적표 `contract.observed_runs` 문구가 가리키는 옛 도구이며, 스킬에 없다.
- 제안: 두 분기와 그 합성 시험을 지운다. OPS-02에서 동결을 택하면 이 후보는 거기에 흡수된다.
- 실익: 검사기 약 60행과 시험 약 80행이 준다. 생산자 없는 입력 형식의 검사가 사라진다.
- 비용과 위험: 새 상태가 생기지 않는다. 앞으로 추적표에 고정 실행을 다시 넣으려면 검사를 다시 써야 한다.
- 기능·커버리지 영향: 있음. 실제로 쓰이지 않는 입력 형식의 음성 시험 2개가 빠진다.
- 사용자 결정 관련: 없음
- 확신도: 확인

#### OPS-04 결정 기록의 `revoked`·`status`·`revoked_at`은 생산자가 없는데 네 모듈이 읽는다
- 검토: 1
- 종류: 미사용
- 좌표:
  - 스키마: `scripts/do_math/record_schemas/schemas.py:424-431`(`RECORDS["decisions"]`의 `revoked`, `status`, `revoked_at`)
  - 소비자: `scripts/do_math/governance.py:190`, `:473-474`, `:628`, `scripts/do_math/delegations.py:53`, `:55`, `scripts/do_math/task_scope.py:156`
  - 조건 문법: `scripts/do_math/planning.py:368`(`'decision': {'active','revoked','superseded','withdrawn'}`)
- 현상: grant는 `revoke` 결정으로, delegation은 `revoke_delegation`으로 철회된다(`governance.py:613-639`). 그러나 결정 기록 자체를 철회하는 결정 종류나 경로는 없다. 그런데도 grant 원천 검사, 거버넌스 승인 검사, 위임 검사, 과제 범위 검사가 `decision.get("revoked")`와 `decision.get("status", "active") != "active"`로 철회된 결정을 거부한다.
- 근거:
  - 결정 기록의 생산자를 전수 확인했다. 검색식은 `decisions"\]\[|decisions'\]\[|"decisions", {})\[|'decisions', {})\[`에 `= |update(`를 더한 것이고, 6행이 나왔다. 여기에 `lifecycle_engine.py:210-213`, `:302-304`를 읽었다. 생산자는 `governance.py:148`, `:317`, `:642`, `:700`, `lifecycle_engine.py:302`이며, 어느 것도 `revoked`, `status`, `revoked_at`을 쓰지 않는다.
  - 소비 검색식 `get(.revoked.)|get("revoked")|.get(.status., .active.)|get("status", "active")|revoked_at`은 14행을 냈다. 그 가운데 결정 기록 소비는 위 좌표 7행이고, 나머지는 grant·relation 필드다.
  - 시험 9곳이 결정에 이 필드를 직접 써 넣어 철회를 흉내 낸다. 해당 좌표는 `test_governance_engine.py:96`, `test_redesign_ENGINE.py:1473`, `test_redesign_GOVERNANCE.py:157`, `:807`, `:826`, `test_redesign_TASKS.py:482`, `:703`, `:727`, `test_walkthrough_repairs.py:128`이다.
- 제안: 스키마의 세 필드, 소비자의 해당 조건, 조건 문법의 `'decision'` 상태 값, 이 필드를 써 넣는 시험 단언을 지운다. 결정 철회가 필요해지면 생산자와 함께 새로 설계한다.
- 실익: 생산자 없는 신호 하나와 그 사본 7곳이 사라진다. 두 가지 철회 표현(`revoked` 불리언과 `status`)이 공존하던 불일치도 함께 사라진다. 조건 문법이 결코 참이 될 수 없는 결정 상태를 받지 않게 된다.
- 비용과 위험: 여러 영역(STO 스키마, REV `task_scope`, RES `planning`·`delegations`)을 함께 고쳐야 한다. 새 상태는 생기지 않는다. 시험 9곳은 철회를 흉내 내는 대신 다른 거부 사유로 다시 쓰거나 지워야 한다.
- 기능·커버리지 영향: 있음. 존재하지 않는 기능인 "철회된 결정의 거부"를 흉내 내던 시험 단언이 사라진다.
- 사용자 결정 관련: 없음. 결정 3·6의 "생산자 없는 신호는 지운다"와 같은 방향이다.
- 확신도: 확인

#### OPS-05 신뢰 결박·환경 기록·툴체인 기록 ID의 형태가 두세 곳에 따로 정의되어 있다
- 검토: 1
- 종류: 이음새
- 좌표:
  - 결박 형태: 생산자 `scripts/do_math/trust_inventory.py:156-161`(`binding`), 수신 `scripts/do_math/trust_validation.py:18`, `:23-28`(`BINDING_FIELDS`, `binding_errors`), 저장 스키마 `scripts/do_math/record_schemas/schemas.py:666-669`(`trust_bindings`)
  - 환경 기록 필드 집합: `scripts/do_math/trust_validation.py:16-17`, `:46-47` ↔ `scripts/do_math/record_schemas/schemas.py:494-500`
  - 기록 ID와 파일 이름: `scripts/do_math/trust_inventory.py:56`(스키마 `^TC-[0-9a-f]{64}$`), `:148`(`record_id`), `:232`(`TC-*.json`), `scripts/do_math/trust_validation.py:20`(`_RECORD_ID`), `:35`(`<ID>.json`), `scripts/setup_lean.py:119`, `:132`
- 현상:
  - 결박의 네 필드는 세 곳에 따로 적혀 있다. 생산자 `binding()`, 수신자 `binding_errors`, 저장 스키마 `trust_bindings`다.
  - 환경 기록의 필수 6개와 선택 2개 필드는 `ENVIRONMENT_FIELDS`·`OPTIONAL_FIELDS`와 `RECORDS["trust_environments"]`에 두 번 적혀 있다.
  - 툴체인 기록 ID 형식은 두 모듈의 정규식 두 개로, 파일 이름 규칙은 네 곳으로 흩어져 있다.
  - 저장된 상태를 읽을 때(`record_schemas/__init__.py:504-505`, `state_checks.py:222-226`)는 스키마 검증 뒤 `environment_errors`가 같은 필드 집합과 결박 모양을 다시 검사한다.
- 근거: 검색식 `trust_bindings|toolchain_record|TC-|environment_errors|trust_validation|trust_inventory`, `scripts/do_math` 대상으로 전수 확인했다(`__pycache__`를 빼고 두 모듈 자신을 포함해 58행). 이음새 계약 6절은 "신뢰 환경 기록과 툴체인 기록의 형태는 G1만 정의한다"고 정했지만, 저장 스키마에 사본이 남았다.
- 제안: `trust_validation.py`에 `BINDING_SCHEMA`, `ENVIRONMENT_PROPERTIES`와 필수 목록, `RECORD_ID_PATTERN`을 JSON Schema 조각으로 한 번 둔다. `schemas.py`, `trust_inventory.RECORD_SCHEMA`, `binding_errors`, `record_reference_errors`, `environment_errors`의 필드 검사는 이 이름을 참조한다. `<ID>.json` 파일 경로 규칙은 `trust_inventory`에 `record_path(directory, record_id)` 하나로 두고 `setup_lean.py`가 쓴다.
  - import 순서 제약은 없다. `trust_validation.py`의 모듈 수준 import는 `copy`, `pathlib`, `re`, `.file_io`뿐이고 `trust_inventory`는 함수 안에서만 import하므로, `schemas.py`와 `trust_inventory.py`가 이 모듈을 import해도 순환이 생기지 않는다.
- 실익: 필드 하나를 바꿀 때 고칠 곳이 셋에서 하나로 준다. 저장 스키마와 G1 검사가 서로 다르게 바뀔 여지가 사라진다. 사본 약 15행이 준다.
- 비용과 위험: `schemas.py`(STO)를 함께 고친다. 새 상태, 수명, 복구 규칙은 생기지 않는다. 오류 메시지 문구가 스키마 오류 형식으로 바뀔 수 있으므로, 문구를 단언하는 시험을 확인해야 한다.
- 기능·커버리지 영향: 없음
- 사용자 결정 관련: 없음
- 확신도: 확인

#### OPS-06 툴체인 기록 잠금이 공유 `os_lock` 대신 수동 복구가 필요한 잠금 파일을 쓴다
- 검토: 1
- 종류: 불일관
- 좌표: `scripts/do_math/trust_inventory.py:210-225`(`writer_lock`), 사용처 `scripts/setup_lean.py:113`, `:144`, `:163`, 정본 `scripts/do_math/file_io.py:119`(`os_lock`), 문서 `references/초기화-효율과-정비.md:91`, 시험 `scripts/tests/test_environment_validation.py:183-187`
- 현상:
  - `writer_lock`은 `records/.lock`을 `open('x')`로 배타 생성하고 `finally`에서 지운다.
  - 프로세스가 강제 종료되면 잠금 파일이 남는다. 그래서 docstring과 운영 문서에 수동 복구 절차가 붙었다. 문서의 절차는 "`Get-CimInstance Win32_Process`의 `CommandLine`에서 실행 중인 `setup_lean.py`가 없음을 확인한 뒤 사람이 지운다"이다.
  - 같은 제품의 다른 잠금(`git_store.writer_lock`, 엔진 inbox, 설치 정비)은 모두 이음새 계약 11절의 정본 `file_io.os_lock`을 쓴다. `os_lock`은 OS 권고 잠금이라 프로세스가 끝나면 풀린다.
- 근거: 검색식 `writer_lock|os_lock`(시험 제외)이 18행을 냈다. 그 가운데 `os_lock`을 쓰지 않는 잠금은 `trust_inventory.writer_lock` 하나다.
- 제안: `writer_lock` 본문을 `os_lock(directory / '.lock', blocking=False)`로 바꾼다. 문서 91행의 수동 삭제 절차를 지우고, 시험(`:186`)은 `OSError`를 기대하게 고친다. `setup_lean.main`은 이미 `OSError`를 종료 코드 2로 처리한다(`:277-279`). 지금의 `RuntimeError`도 같은 코드이므로 종료 코드 계약은 바뀌지 않는다.
- 실익: 잠금 구현이 하나로 모이고, 남은 잠금 파일이라는 상태와 사람이 수행하는 복구 규칙이 사라진다(방향 8의 비용 계산에 맞는 감소). 약 10행이 준다.
- 비용과 위험: 새 상태는 없다. `os_lock`은 Windows에서 같은 프로세스의 두 번째 핸들도 막는다. 이 성질은 `git_store`가 이미 기대고 있다. 시험 1곳과 문서 1문장을 고친다.
- 기능·커버리지 영향: 없음
- 사용자 결정 관련: 없음
- 확신도: 확인

#### OPS-07 재분석 지점 거부 규칙이 bootstrap과 `git_store`에 두 벌 있다
- 검토: 1
- 종류: 이음새
- 좌표: `scripts/operator_bootstrap.py:17`, `:20-26`(`_ordinary_path`), 호출 `:33`, `:64`, `:83`, `:102-103`, `:113`, `:139`, 정본 `scripts/do_math/git_store.py:580-591`(`no_reparse`)
- 현상: 두 함수는 같은 규칙이다. 경로와 모든 조상의 `lstat`에서 심볼릭 링크이거나 `st_file_attributes & 0x400`이면 거부한다. 이음새 계약 11절은 `no_reparse`를 이 규칙의 정본으로 적었다. bootstrap이 사본을 가진 이유는 따로 있다. frozen bootstrap은 스냅숏을 검증하기 전에 `do_math.file_io` 하나만 import해야 하는데(`결과-F.md:77`, 시험 `test_operator_bootstrap.test_changed_frozen_code_is_rejected_before_import`), `git_store`는 `operation_trace` 등을 import한다(`git_store.py:9-27`).
- 근거:
  - 검색식 `no_reparse|_ordinary_path|_REPARSE_POINT|0x400`(시험 제외)이 21행을 냈고, 구현은 둘이다.
  - bootstrap은 파일마다 모든 조상을 다시 걷는다. 설치 root 깊이 5, 파일 113개에서 `_source_paths`는 0.168초가 걸렸고, 같은 집합의 `installation_files`만은 0.041초였다. 명령은 `python -c "…b._source_paths(root,fio)…"`이다. `verify_snapshot`은 파일마다 한 번, `_source_paths`에서 한 번 더 걷는다(`:83`, `:93`).
- 제안: `no_reparse`를 `file_io.py`로 옮긴다. `installation_files`가 bootstrap 때문에 그곳에 있는 것과 같은 이유다. `git_store`는 이미 `os_lock`처럼 `file_io`에서 import한다. bootstrap은 `_ordinary_path`와 `_REPARSE_POINT`를 지우고, root는 `no_reparse(root)`로 한 번, 파일은 `no_reparse(path, below=root)`로 검사한다.
- 실익: 규칙 사본 하나(약 8행)가 사라진다. 예약 작업 기동마다 파일당 조상 재탐색이 root까지로 줄어든다. 절감량은 측정 조건에서 약 0.1초 이상이고, 스냅숏이 더 깊은 `workspace/operator/bootstrap/<sha>`에 있으므로 실제로는 더 크다(추정).
- 비용과 위험: 새 상태는 없다. `git_store`, `context_store`, `repository`, `retention`의 import 출처가 바뀐다(4개 모듈, STO). 검사 범위는 같다.
- 기능·커버리지 영향: 없음
- 사용자 결정 관련: 없음
- 확신도: 확인

#### OPS-08 `_governance_control`이 시험만 쓰는 두 번째 요청 모양을 받는다
- 검토: 2
- 종류: 임시방편
- 좌표: `scripts/do_math/governance_engine.py:207-208`, `:226-227`(`change = spec.get('change', spec)`), 비교 `scripts/do_math/lifecycle_engine.py:461`, `:548-556`, `scripts/do_math/cli.py:378`, `scripts/do_math/control_contracts.py:152`
- 현상:
  - 공개 `decision` 제어의 config는 `{'change': …}`이다. CLI가 그렇게 감싸고(`cli.py:378`), 제어 스키마도 그 모양이다(`control_contracts.py:152`). `lifecycle_engine`은 `config['change']`만 읽는다.
  - `_governance_control`과 `_reject_governance_import`만 `change`가 없으면 config 자체를 결정으로 읽는다. 이 두 번째 모양을 쓰는 곳은 시험뿐이다. `test_governance_engine.py:148`과 `AuditRepairTests.checked_import`(`test_redesign_GOVERNANCE.py:786`)가 감싸지 않은 config로 `_governance_control`을 부른다. 후자는 `test_governance_engine.py:61`, `:76-122`에서 쓰인다.
- 근거: 검색식 `\['change'\]|get('change'|\["change"\]|get("change"`(`scripts/do_math`)이 10행을 냈다. 제어 config를 읽는 곳은 4곳이고, 대체값을 두는 곳은 `governance_engine`의 2곳뿐이다. 제품의 `decision` 생산자는 CLI 하나이며, 검색식 `'decision'`에 action·command를 더한 결과로 확인했다.
- 제안: 두 줄을 `change = spec.get('change', {})`로 바꾼다. 시험은 config를 `{'change': …}`로 감싼다. `apply_import_control`이 풀린 config를 받는 내부 계약은 `_governance_control`이 정규화하므로 그대로 둔다.
- 실익: 한 제어 종류의 모양이 하나로 준다. 방향 4의 "구형 인자·래퍼를 남기지 않는다"와 "시험을 살리려고 제품에 예외를 넣지 않는다"에 맞는다.
- 비용과 위험: 새 상태는 없다. 시험 2곳의 요청 구성만 바뀐다.
- 기능·커버리지 영향: 없음
- 사용자 결정 관련: 없음
- 확신도: 확인

#### OPS-09 초기 상태의 모양을 `initialize_state`와 `engine.init`이 나누어 정하고, 이미 있는 키를 여러 곳에서 다시 채운다
- 검토: 1
- 종류: 이음새
- 좌표:
  - `scripts/do_math/initialization.py:235-264`(`initialize_state`)
  - `scripts/do_math/engine.py:251-264`(`contract_id`·`grants={}` 재설정 `:258`, `question_links` 재설정 `:260-261`, `ensure_governance` `:262`, `feature_version` 재설정 `:264`)
  - `scripts/do_math/governance.py:348-354`(`ensure_governance`), `:552`, `:109`, `:144`, `:148-149`(`setdefault`)
- 현상:
  - `initialize_state`는 `grants`, `decisions`, `governance`, `governance_sources`, `contract_id`, `feature_version`, `question_links`를 이미 만든다(`initialization.py:242-262`). 그런데 `engine.init`이 바로 뒤에서 같은 키를 다시 설정한다. `ensure_governance`를 거쳐 네 키에 `setdefault`도 다시 한다.
  - `engine.init`은 나머지 초기 필드(`reservations`, `provider_waits`, `processed_controls`, `cycles`, 실행 프로필, 온톨로지, 기록 가족)도 채운다. 따라서 `initialize_state`만 부르는 시험 12개 모듈은 제품과 다른 시작 상태에서 출발한다. 호출 행은 17개이며, `grep -rn "initialize_state(" tests`로 셌다.
  - `apply_decision`(`governance.py:552`), `initialize_governance`, `_install_record`의 `setdefault`는 초기화 뒤에는 늘 있는 키를 채운다.
  - 저장소는 빈 map 가족도 manifest의 `ids: []`로 복원한다(`repository.py:968-993`). 따라서 적재한 상태에서 이 키들이 빠지는 경로는 없다.
- 근거: 위 원문을 읽었고, `initialize_state(`의 제품 호출자가 `engine.py:251` 하나임을 확인했다.
- 제안:
  - 작은 단계: `engine.init`의 중복 재설정 4곳과 `ensure_governance`를 지운다. governance 함수의 `setdefault`는 직접 색인으로 바꾼다.
  - 선택 단계: `engine.init`이 채우는 초기 필드를 `initialize_state` 하나로 옮겨, 시험과 제품이 같은 시작 상태를 쓰게 한다.
- 실익: 초기 상태 지식이 한 함수로 모인다. 작은 단계만으로 약 12행이 줄고, 존재하지 않는 옛 상태를 위한 기본값 보충(AGENTS.md 6행)이 사라진다.
- 비용과 위험: 새 상태는 없다. 최소 인스턴스(`{"id": "I", "feature_version": 5}` 등)로 `apply_decision`이나 `initialize_governance`를 부르는 시험은 현행 시작 상태 템플릿으로 바꿔야 한다. 이런 시험의 수는 세지 않았다. `engine.py`는 ENG 영역이다.
- 기능·커버리지 영향: 없음
- 사용자 결정 관련: 없음
- 확신도: 추정. 중복 재설정과 무효한 `setdefault`는 확인했다. 확정하려면 `apply_decision`·`initialize_governance`·`_install_record`를 governance 키 없는 인스턴스로 부르는 시험을 전수 세야 한다.

#### OPS-10 불변 원문 기록 `{text, sha256, bytes}`의 규칙이 governance와 initialization에 두 벌 있다
- 검토: 1
- 종류: 이음새
- 좌표:
  - `scripts/do_math/governance.py:36-50`(`preserve_source`, `validate_source`), `:127-129`(초기 입력과 원천 대조)
  - `scripts/do_math/initialization.py:16-23`(`original_input_bytes`), `:113-115`(검증 직후 같은 해시 재계산), `:240`, `:250`, `:257`(`initialize_state`가 같은 바이트를 두 번 해시)
- 현상: "원문의 UTF-8 바이트 SHA-256과 바이트 수를 기록하고, 읽을 때 같은지 확인한다"는 한 규칙이 두 번 구현되어 있다. `preserve_source`/`validate_source`와 `original_input_bytes`/`initialize_state`다. `initial_intent_evidence`는 `original_input_bytes`가 기록된 해시를 검증한 직후, 같은 바이트의 해시를 다시 계산한다(`:114-115`).
- 근거: 두 모듈의 원문을 읽었다. `lifecycle_engine.py:208`은 불변 입력의 `text`로 `preserve_source`를 만들고, `initialize_governance`가 세 필드를 대조한다. 두 구현이 같은 결과를 낼 것을 전제하는 이음새다.
- 제안: `governance`에 원문 기록을 만드는 함수 하나(`{text, sha256, bytes}`)를 두고 `preserve_source`와 `initialize_state`가 쓰게 한다. `original_input_bytes`의 검증도 같은 함수로 기대값을 만든다. `initial_intent_evidence`는 `original['sha256']`을 쓴다.
- 실익: 규칙 사본 하나와 재계산 두 곳, 약 6행이 준다.
- 비용과 위험: 새 상태는 없다. 저장 값의 형태는 바뀌지 않는다.
- 기능·커버리지 영향: 없음
- 사용자 결정 관련: 없음
- 확신도: 확인

#### OPS-11 intent import 묶음의 상수 필드 `coordinate_unit`·`basis_scope`는 읽는 곳이 없다
- 검토: 1
- 종류: 미사용
- 좌표: 생산 `scripts/do_math/governance.py:989`, 스키마 `scripts/do_math/record_schemas/schemas.py:562`, `:564-565`(required)
- 현상: `prepare_import`는 모든 묶음에 `"coordinate_unit": "unicode_codepoint"`와 `"basis_scope": "referenced-v1"`를 기록하고, 스키마는 이 둘을 단일 값 enum으로 강제한다. 두 필드를 읽는 코드는 없다. 모델에게 좌표 단위를 알리는 것은 별도의 문맥 키 `source_coordinate_unit`(`governance_engine.py:134`)이다.
- 근거: 검색식 `coordinate_unit|basis_scope|referenced-v1|source_coordinate_unit`(스킬 `*.py`·`*.md`)이 4행을 냈다. 생산 1, 스키마 2, 다른 키 1이며 시험은 0건이다.
- 제안: 두 필드를 묶음과 스키마에서 지운다. 묶음 봉인 해시의 입력이 바뀌지만, 결정 1에 따라 보존할 저장 인스턴스는 없다.
- 실익: 소비자 없는 필드 둘과, 레코드 안에 남은 판본 표지(`referenced-v1`)가 사라진다.
- 비용과 위험: 새 상태는 없다. `schemas.py`(STO)를 함께 고친다.
- 기능·커버리지 영향: 없음
- 사용자 결정 관련: 없음
- 확신도: 확인

#### OPS-12 능력 증거의 식별 ID를 사용할 때마다 다시 해시한다
- 검토: 1
- 종류: 불일관
- 좌표: `scripts/do_math/initialization.py:41-44`, 생산 `scripts/do_math/execution_profiles.py:384`, `:417`, 저장 검사 `scripts/do_math/record_schemas/__init__.py:335-336`
- 현상:
  - `capability_requirements`는 부를 때마다 모든 능력 증거 행의 `'CE-' + exact_content_hash(행)`을 다시 계산하고, ID와 다르면 그 행을 조용히 뺀다.
  - 그런데 ID는 생성 시점에 같은 식으로 기록되고(`execution_profiles.py:384`, `:417`), 저장 검증은 ID를 확인하지 않는다.
  - 방향 6("식별은 생성 시점에 한 번 계산")과, 다른 가족이 봉인 해시를 저장 경계에서 한 번 보는 방식과 다르다.
- 근거: 호출자는 `activation_requirements`(`:205`), `lifecycle_engine.py:101`(`_queue_initial_intent`, 제한 복구)이다. 증거는 디스크 왕복을 거치므로 방향 2의 수신 검사 면제 조건 3이 성립하지 않는다. 따라서 검사를 없애기보다 저장 경계로 옮기는 것이 맞다.
- 제안: CE ID 대조를 `capability_evidence` 가족의 저장 검증기로 옮겨, 새로 들어오거나 바뀐 행마다 한 번만 한다. 사용 경로의 재해시와 조용한 제외는 지운다.
- 실익: 사용 경로의 재계산이 사라진다. 손상된 증거가 "증거 없음"으로 조용히 바뀌지 않고 저장 경계에서 오류로 드러난다.
- 비용과 위험: 새 상태는 없다. `record_schemas/__init__.py`(STO)를 고친다. 호출 빈도가 낮아 시간 절감은 작다.
- 기능·커버리지 영향: 없음
- 사용자 결정 관련: 없음
- 확신도: 확인

#### OPS-13 import 승인 한 번에 같은 현재성 검사를 두 번 한다
- 검토: 1
- 종류: 비용
- 좌표: `scripts/do_math/governance.py:1139`(`apply_import_control`의 `_current_import`), `:1152` → `:1084`(`apply_import`의 `_current_import`)
- 현상: `apply_import_control`은 `_current_import`로 묶음을 검증한 뒤 `apply_import`를 부르고, `apply_import`는 같은 값으로 `_current_import`를 다시 부른다. 그 사이에 바뀌는 것은 승인 원천 하나(`governance_sources[request id]`)뿐이다. 이 원천은 `_import_basis`가 참조하는 ID가 아니다. 한 번의 `_current_import`는 원천 검증, 공개 입력 복원(초기 입력이면 해시 재검증), 봉인 해시, 전체 기록 색인 위의 `_import_basis`, `_owner_basis`를 계산한다.
- 근거: 두 함수의 원문을 읽었다(`:1001-1021`, `:1079-1156`).
- 제안: `apply_import_control`은 `runtime['intent_imports']`에서 묶음을 조회해 존재만 확인한다. 승인 대조(`bundle_sha256`, `check_sha256`, `unit_hashes`)는 그대로 하고, 현재성은 `apply_import`에 맡긴다.
- 실익: 사용자 승인 한 번마다 전체 기록 색인과 기저 해시 계산이 한 번 준다. 방향 6의 "같은 사실의 반복 확인"을 없앤다. 승인은 드문 사건이라 시간 절감은 작다.
- 비용과 위험: 새 상태는 없다. 대체된 묶음을 승인하면 거부 문구가 바뀔 수 있다.
- 기능·커버리지 영향: 없음
- 사용자 결정 관련: 없음
- 확신도: 확인

#### OPS-14 governance에 옛 판본 표지 검사와 도달하지 않는 기본값이 남아 있다
- 검토: 2
- 종류: 낡음
- 좌표: `scripts/do_math/governance.py:173-174`(최상위 `goal` 등 5개 키 거부, 문구 "in feature 5"), `:671`(문구 "v5 scope approval"), `:475`(`decision.get("source_sha256", source["sha256"])`), `scripts/do_math/governance_engine.py:411`(`view.get('goal_revision', 1)`, `view.get('policy_revision', 1)`)
- 현상:
  - `validate_governance_state`는 옛 상태의 최상위 권한 필드 다섯 개가 있으면 거부한다. 그러나 저장 계약은 등록되지 않은 최상위 가족을 이미 거부한다(`state_contract.py:141-143`). 다섯 키는 어느 가족에도 등록되어 있지 않다. 확인 명령은 `python -c "…[k for k in (…) if k in RECORDS or k in RESEARCH_FIELDS]"`이고 결과는 `[]`다. AGENTS.md 8행의 "내부 로직에서 제품 버전을 반복 확인하지 않는다"에도 어긋난다.
  - `governance_view`는 `goal_revision`과 `policy_revision`을 늘 돌려준다(`governance.py:164-165`). 그래서 `.get(..., 1)`의 기본값은 도달하지 않는다. 게다가 `policy_revision`의 실제 값은 해시 문자열이다.
  - grant 결정은 늘 `source_sha256`을 가진다(`governance.py:566`). 따라서 대체값은 도달하지 않고, 도달한다면 대조를 무력화한다.
- 근거: 시험이 이 문구나 기본값에 기대는지 검색했다. 검색식 `parallel governance|feature 5|v5 scope`의 시험 결과는 0건이다.
- 제안: 173-174행을 지운다. 두 오류 문구에서 판본 표지를 뺀다. 두 `.get` 기본값과 `source_sha256` 대체값을 직접 색인으로 바꾼다.
- 실익: 옛 형식 검사 하나와 무효한 기본값 셋이 사라진다. `source_sha256` 대조가 빠질 수 있는 경로도 닫힌다.
- 비용과 위험: 새 상태는 없다. 약 5행을 바꾼다.
- 기능·커버리지 영향: 없음
- 사용자 결정 관련: 없음
- 확신도: 확인

#### OPS-15 영역 파일의 미사용 import와 같은 함수 안의 중복 계산
- 검토: 2
- 종류: 잔재
- 좌표:
  - 미사용 import: `scripts/do_math/governance_engine.py:40`(`DEFAULT_CONFIG`), `scripts/do_math/initialization.py:6`(`Path`), `scripts/operator_bootstrap.py:6`(`os`), `scripts/probe_cli.py:7`(`sys`)
  - 중복 import: `scripts/do_math/initialization.py:9`, `:186`(`resolve_profile`)
  - 중복 계산: `scripts/do_math/governance_engine.py:64-65`, `:70`, `:103`(`live`와 `waiting`을 같은 입력으로 다시 계산)
- 현상: 위 이름은 모듈에서 쓰이지 않거나, 같은 함수 안에서 바뀌지 않은 입력으로 다시 계산된다.
- 근거: 영역 Python 파일 11개를 AST로 검사했다. import한 이름 가운데 본문의 `Name`이나 `Attribute`로 참조되지 않는 것을 찾았고, 결과는 위 4개다. 세 경량화 이전(`8d2ffd0^`)에도 쓰이지 않았다.
- 제안: 지운다.
- 실익: 약 8행이 준다. 크지 않지만 비용이 없는 정리다.
- 비용과 위험: 없음
- 기능·커버리지 영향: 없음
- 사용자 결정 관련: 없음
- 확신도: 확인

## 4. 보존 판정

- **`scripts/probe_cli.py`는 존재 이유가 있다.**
  - `--skill-only`는 제품 계약의 일부다. 설치 복구 뒤 감독이 live 설치에서 이 명령을 새 프로세스로 실행하고(`scheduled_operator.py:622-627`), `계약/독립-운영.md:55`와 `AGENTS.md:11`이 이 명령을 지정한다.
  - 모듈 머리에서 `engine`, `model_runner`, `observations`, `scholarly`를 import한다. 이 import 자체가 수리된 코드가 적재되는지를 보는 확인이 된다.
  - 실호출 사례(`run_case`)는 `probe_codex.py` 삭제 뒤 제품 `ModelRunner` 경로로 두 공급자를 실제로 부르는 유일한 도구다(`README.md:549-552`, `references/CLI-실행-계약.md:962`). 그 인자는 현재 `ModelRunner.run` 서명(`model_runner.py:36-46`)과 일치한다.
- **`scripts/operator_schedule.ps1:2`의 `ValidateSet`과 `scheduled_operator.SCHEDULE_ACTIONS`.** 두 목록은 같은 동작 이름이다. 그러나 수신자는 다른 프로세스(PowerShell)라 방향 2의 수신 검사 면제 조건을 충족하지 못한다. 어긋나면 어댑터가 즉시 실패하므로 조용한 오류가 생기지 않는다.
- **`scripts/operator_bootstrap.py:14-15`, `:49-54`, `:88-96`의 지문 표지 캐시(`bootstrap-fingerprints.json`).** 캐시의 키는 파일 이름이고, 값은 정착한 지문이다. 지문이 다르거나 정착하지 않았으면 manifest의 해시로 다시 대조한다. 내용 주소 스냅숏은 불변이므로 입력이 키에 모두 담기고, 무효화는 대조 한 곳에서 일어난다.
- **`scripts/check_coverage.py:29-33`의 `_syntax` `lru_cache`.** 키가 원문 전체 텍스트라 입력을 모두 담고, 무효화가 필요 없다.
- **`scripts/do_math/reporting.py:27-35`의 `Asia/Seoul` 고정 오프셋 대체.** `requirements.txt`에 `tzdata`가 없어 Windows에서는 이 대체가 실제 경로다. 증상을 덮는 코드가 아니다.
- **`scripts/setup_lean.py:95-107`의 `_settled_fingerprint` 대기.** 기준으로 기록할 지문이 racy 창(`RACY_NS`)을 지나야 한다는 이음새 계약 1절의 규칙을 구현한다.
- **`engine.py:4109`와 `repair_execution.py:167`의 `validate_installation_target` 두 번 호출.** 첫 호출은 처분을 적용할 때, 둘째는 대상 실행이 끝난 뒤 수리를 요청할 때다. 그 사이 대상 실행 상태와 설치 파일이 바뀔 수 있으므로 판정 시점과 사용 시점 사이의 재확인에 해당한다.
- **`governance.py:135`, `:191-192`의 `input_source_ref` 대체값.** 초기화 승인만 원천과 승인 원천을 나눈다(`lifecycle_engine.py:212`). 뒤의 결정으로 승인된 기록에서는 대체값이 곧 규칙이다.
- **`trust_validation.check_environment`의 `identity` 인자.** 활성화(`lifecycle_engine.py:1181`)는 판본 식별까지, 형식 검사(`verify_formal`)는 검사기가 따로 보는 식별을 빼고 부른다. 재결박 분기에서는 `identity=False`여도 식별을 확인한다(`:132-133`). 설계 3.4의 조건에 맞는다.
- **`governance.py`의 크기(1,191행)와 `repair_execution.py`의 세 관심사.** 각각 거버넌스·grant·의도 import와 제출 반환·초기 진단·설치 수리를 담는다. 나눠도 지워지는 코드나 이음새가 없고, 시험의 import 경로만 바뀐다. 그래서 경계 후보로 내지 않았다.
- **2라운드 보존 판정 가운데 이 영역의 것.** `operator_bootstrap`의 네 번 해시, `governance_engine`의 `validate_config` 두 번, 의도 import의 스키마와 수신 검사 중복은 현재 원문에서도 근거가 유효하다.

## 5. 영역 밖 관찰

- TSA: `scripts/tests/test_redesign_EVIDENCE.py:278-279`의 주석 "Check the complete archive once in the integration test below"는 사라진 그룹 체계를 가리킨다. 같은 파일 `:300-301`의 표지 제거가 OPS-01의 직접 원인이다.
- RES: `scripts/do_math/planning.py:369`의 조건 문법 `'trust-environment': {'candidate','active','invalid','superseded'}`는 저장 스키마의 상태 `registered`(`record_schemas/schemas.py:496`)를 받지 않는다. 대신 어디서도 생기지 않는 `candidate`를 받는다(검색 `'registered'|'candidate'`).
- RUN: `scripts/do_math/lifecycle_engine.py:170`의 `getattr(self, '_governance_owner_handlers', lambda: None)()`는 늘 있는 mixin 메서드를 위한 대체다. `379a171`이 `governance_engine`에서 같은 모양의 `getattr` 대체를 지운 것과 같은 종류다.
- REV·STO: 엄격 JSON 해석이 두 벌이다. 하나는 `submission.load_json`(`:237-240`, BOM 허용과 `canonical_json` 검사)이고, 다른 하나는 이음새 계약 11절의 정본 `file_io.strict_json_loads`(`:212-217`)다. 이 영역의 `setup_lean.py:250`은 비상태 입력인 `--command-file`을 앞의 것으로 읽는다.
- HIS(여러 영역 패턴): "비어 있지 않은 텍스트" 검사 도우미가 7개 모듈에 따로 있다(`governance.py:462`, `control_transport.py:78`, `knowledge.py:24`, `knowledge_io.py:89`, `activities.py:16`, `task_contracts.py:65`, `execution_lifecycle.py:23`). "서로 다른 비어 있지 않은 문자열 목록"도 4개 모듈에 있다(`governance.py:53`, `academic.py:11`, `retention.py:50`, `review_policy.py:16`).
- ENG: `scripts/do_math/engine.py:251-264`가 `initialize_state`가 만든 키를 다시 설정한다(OPS-09와 같은 사실).
- HIS: `C:/math/docs/do-math/검사-경량화-이음새-계약.md:36`의 "`trust_validation.py:136`은 G1이 교체"는 `8d2ffd0`로 다시 쓰인 파일의 옛 좌표다.

## 6. 작업 기록

- `C:/math` 전체를 대상으로 한 `grep -rn`이 120초 시한을 넘겼다. 그래서 스킬 디렉터리와 `docs/do-math`로 범위를 나눈 Grep으로 바꿨다. `docs/do-math`의 69개 일치는 과거 증거 JSON의 파일 목록이라 판정에서 뺐다.
- 전체 추적표 검사의 소요 시간이 실행마다 크게 달랐다. 63.08초(첫 실행), 15.76초(cProfile), 5.87초(캐시가 데워진 뒤)였다. 파일 캐시 상태가 지배적이라 OPS-01에는 세 값을 모두 적었다.
- 처음에는 `check_coverage.py`를 2라운드 보존 판정대로 둘 생각이었다. `9b434f4`의 시험 diff에서 `@category('archive')` 제거를 발견한 뒤, 보존 판정의 전제가 사라졌음을 확인하고 OPS-01·02로 바꿨다.
- `ensure_governance`에 기대는 시험의 수는 세지 못했다. 최소 인스턴스 구성이 다양해 전수 검색식을 확정하지 못했기 때문이다. OPS-09는 그래서 추정이다.
- `write-for-reader` 스킬의 합의·독자 파일과 `writing_flow.py` 독해는 수행하지 않았다. 기준 7절이 쓰는 파일을 산출 파일 하나로 제한하기 때문이다. 스킬의 품질 계약과 참조 문서(명료한 산문, AI 프롬프트, 경중 배분)의 규칙만 적용했다.
