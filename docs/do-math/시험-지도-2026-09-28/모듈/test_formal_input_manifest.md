# test_formal_input_manifest

| 항목 | 값 |
|---|---|
| 조각 | `foundation` |
| 원문 | `.claude/skills/do-math/scripts/tests/test_formal_input_manifest.py` (72행) |
| 클래스 / 테스트 | 1 / 1 |
| 시험 대상 제품 코드 | `do_math/formal.py`의 `project_source_identity`(내부의 `_git`, `cached_sha256`, `json_digest`); `do_math/context_store.py`의 `prepare_role_input`(내부의 `submission.install_tools`, `fit_context`); `do_math/execution_profiles.py`의 `build_profiles` |
| 사용하는 픽스처 모듈 | `record_fixtures.surface_state`, `research_fixtures.git_init` |
| 격리 표지 | 없음 |
| 시작 상태 | 1단 확장: 합성 도메인 기록(`surface_state`)을 메모리에서 만들고, 임시 폴더에 실제 Git 작업 트리와 Lean 소스 파일을 둔다. 엔진·템플릿은 쓰지 않는다 |

## 목적

모듈 docstring은 없다. 유일한 시험의 이름이 계약을 말한다. Lake 프로젝트의 소스 식별(`project_source_identity`)은 작게 유지되어 역할 입력의 한도를 지키고, 파일 내용·이름·존재의 변화를 모두 감지한다. 제품 근거는 `formal.py` 251–253행 주석이다. 소비자는 프로젝트 식별 전체만 비교하고 개별 항목을 읽지 않으므로, 파일 이름과 내용에 대한 감도는 그대로 두면서 큰 목록을 역할 프롬프트와 형식 결과마다 복사하지 않는다. 그래서 추적되지 않은 파일 목록은 `json_digest` 하나(`untracked_sha256`)와 개수(`untracked_file_count`)로 줄여 담는다.

`project_source_identity`(`formal.py` 221–257행)는 `root`, `git_tree`, `working_diff_hash`, `untracked_file_count`, `untracked_sha256` 다섯 필드를 돌려준다. `.lake` 폴더는 건너뛰고, `.lean` 확장자 파일과 `lean-toolchain`, `lake-manifest.json`, `lakefile.lean`, `lakefile.toml` 가운데 Git이 추적하지 않는 파일만 `cached_sha256`로 해시한다. Git 정보는 `_git`(24–31행)이 `subprocess.run`으로 실제 `git` 자식 프로세스를 띄워 읽는다.

시험 이름 속 "bounds role input"은 두 번째 절반이 확인한다. 식별을 담은 형식 검증기 맥락이 `intent_interpretation` 역할 입력에 들어가도 입력이 넘치지 않는다. 그 기대 도구 모음은 기계용 맥락 파일, 검증 맥락, 보이는 맥락에 그대로 도달한다.

## 모듈 수준 요소

- 행 8: `sys.path.insert(0, ...parents[1])`로 `scripts/`를 경로 앞에 넣는다(중복 확인 없음).
- 행 9–13: 제품과 픽스처 import.
- 행 71–72: 직접 실행하면 `unittest.main()`.

## FormalInputManifestTests (행 16–68)

`unittest.TestCase`를 상속한다. 표지, 클래스 속성, 설정·정리 훅, 도우미가 없다.

### `test_project_identity_bounds_role_input_and_detects_file_changes` (행 17–68)
- 성질: 프로젝트 소스 식별은 1KiB 미만으로 작고, 파일 수정·이름 변경·삭제를 모두 다른 식별로 드러내며, 같은 상태에서는 같은 값을 낸다. 이 식별을 담은 형식 검증기 맥락은 역할 입력을 넘치게 하지 않고 기계용·검증용·보이는 맥락에 기대 도구 모음을 그대로 전달하며, 호출자의 맥락을 바꾸지 않는다.
- 준비: `record_fixtures.surface_state()`가 준 합성 `instance`와 `runtime`. `config['max_input_bytes']`를 500000으로 올리고 `build_profiles`로 실행 프로필을 다시 만든 뒤, 역할이 `intent_interpretation`인 프로필을 고른다. 임시 폴더 아래 `project/`에 `git_init`으로 저장소를 만들고(커밋 없음), `lakefile.toml` 하나와 `Module0.lean`~`Module39.lean` 40개를 쓴다.
- 실행: 전반부는 `project_source_identity(project)`를 다섯 번 부른다. 처음 상태, `Module0.lean` 내용 변경 뒤, `Renamed.lean`으로 이름 변경 뒤, 그 파일 삭제 뒤, 그리고 같은 상태에서 한 번 더다. 후반부는 삭제 뒤의 식별을 `toolchain.project.source_identity`에 넣는다. 그 `toolchain`(`version 'Lean test edition'`, `executable 'test-lean'`, `sha256 'b'*64`)을 관측·기대 도구 모음으로 둔 검증기 맥락 `formal_verifier`(`environment_id 'TE-fixed'`, `environment_status 'active'`)를 만든다. 이를 `intent_interpretation` 행동 맥락(사용자 요청 `'For every n : Nat, n + 0 = n'`)에 담아 `prepare_role_input(..., role='intent_interpretation', snapshot='a'*40, activity_id='AC-1', install_submission_tools=True, artifact_prefix='runtime/artifacts/BA-input')`를 부른다.
- 단언:
  - 처음 식별의 `json.dumps` UTF-8 길이가 1024 미만이다.
  - `untracked_file_count`가 41이다(Lean 파일 40개와 `lakefile.toml`).
  - 내용 변경, 이름 변경, 삭제 뒤의 식별이 각각 직전 식별과 다르다.
  - 삭제 뒤 `untracked_file_count`가 40이고, 같은 상태에서 다시 부른 식별과 같다(결정성).
  - `fitted['overflow']`가 `None`이다. 실패 메시지는 "Machine-only inventory should not prevent intent interpretation"이다.
  - `fitted['actual_bytes']`가 프로필의 `input.max_input_bytes`보다 작다.
  - 작업 폴더의 `input/submission/context.json`을 읽은 기계용 맥락의 `formal_verifier.expected_toolchain`이 `toolchain`과 같다.
  - `fitted['validation_context']['formal_verifier']['expected_toolchain']`이 `toolchain`과 같다.
  - 보이는 맥락 `fitted['context']['formal_verifier']`의 `observed_toolchain.version`이 같고, `expected_toolchain`이 `toolchain`과 같다.
  - 호출 뒤 원래 `context['formal_verifier']`가 `verifier`와 같다(입력 불변).
- 대역: 없음. 검증기와 도구 모음은 합성 값이며 실제 Lean은 부르지 않는다.
- 비고: 실제 Git 자식 프로세스를 쓴다. `project_source_identity`가 `git rev-parse`, `git diff`, `git ls-files`를 `subprocess.run`으로 부른다. 저장소 생성은 `git_init`이 맡는다. 이 도우미는 프로세스에서 처음 불릴 때만 `git init`을 한 번 돌리고, 그 뒤로는 만들어 둔 빈 `.git` 폴더를 복사한다(`research_fixtures.py` 945–960행). 커밋이 없으므로 `git_tree`는 `None`이고 모든 파일이 추적되지 않은 것으로 잡힌다. 이름은 "bounds role input"이지만 식별 크기에 대한 직접 단언은 `json.dumps` 길이 < 1024 하나다. 역할 입력 쪽은 넘침이 없고 실제 바이트가 한도 안이라는 것만 본다. 한도는 시험이 500000으로 올려 둔 값이다.

## 관계

- `project_source_identity`의 다른 쪽, 곧 형식 검증 경로에서 프로젝트 식별이 바뀌면 결과를 거부하는 성질은 `test_formal`이 다룬다. 원문에 이 함수 이름이 나오는 시험 모듈은 이 모듈과 `test_formal` 둘이다.
- `prepare_role_input`의 일반 규칙(차단·지도·싣기 분류, 넘침 처리)은 `test_role_input` 등 역할 입력 모듈이 검사한다. 이 모듈은 형식 검증기 맥락 하나가 그 경로를 무사히 지나는지만 본다.
- 픽스처 의존: `record_fixtures.surface_state`는 합성 도메인 상태다. `consumers.json`에 따르면 이 모듈을 포함한 시험 모듈 10개와 픽스처 모듈 `engine_fixtures`가 쓴다. `research_fixtures.git_init`은 시험마다 `git init` 자식 프로세스를 띄우지 않도록, 프로세스당 한 번 만든 빈 저장소의 `.git`을 복사하는 도우미다.
- 이 모듈에만 있는 도우미는 없다.
