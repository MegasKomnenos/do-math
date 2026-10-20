# test_formal_runtime

| 항목 | 값 |
|---|---|
| 조각 | `host` |
| 원문 | `.claude/skills/do-math/scripts/tests/test_formal_runtime.py` (134행) |
| 클래스 / 테스트 | 1 / 8 |
| 시험 대상 제품 코드 | `do_math/formal.py`의 `_job_run`(행 277–326), `_check_file`(행 464–471), `verify_lean`, Lean 원천 상수 `_DEPENDENCY_EXTRACTOR`의 `DoMathDependencyAudit.exprEvidence`(형식 `lean-expr-dag/1`); `do_math/execution_profiles.py`의 `build_profiles`, `job_resource_limits`(행 177–185), `machine_invocation`(행 336 이하), `HOST_ROLES`; `do_math/session_slots.SessionSlots.acquire` |
| 사용하는 픽스처 모듈 | `provider_fixtures.actual_command`; 함수 안에서 `provider_fixtures.host_capacity_fixture`, `provider_fixtures.PROFILE_CONFIG`; `test_categories.test_group`(이름 `category`로 import) |
| 격리 표지 | 메서드 표지. `category('lean')` 4개(`test_shared_expression_evidence_does_not_expand_shared_subterms`, `test_flat_representation_preserves_literal_spaces_and_unicode_binders`, `test_dependency_representation_does_not_expand_layout_indentation`, `test_common_dependency_bodies_are_emitted_once`), `category('resource')` 1개(`test_output_larger_than_the_discarded_cap_is_preserved`). 클래스 표지 없음 |
| 시작 상태 | 네 단 밖(실제 Lean, 실제 Windows Job 자식 프로세스) 다섯 시험, 대역으로 막은 직접 호출 한 시험, 1단(프로필 계산과 메모리 런타임) 한 시험, 실제 Job을 쓰는 표지 없는 한 시험 |

## 목적

모듈 docstring은 "Lean은 실행 예산 없이 끝까지 돌고, 취소와 증거는 계속 관찰할 수 있다"고 밝힌다. 이 모듈은 두 갈래를 본다. 하나는 형식 검사의 무제한 계산 계약이다. `_job_run`은 기한 없이 Job 전체를 기다리고(docstring 행 279–282), `formal_check` 프로필은 호스트 자원 상한과 호출 시간 상한을 받지 않으며(`UNCAPPED_ROLES`, `machine_invocation`의 docstring "a Lean check has no deadline"), 출력은 잘리지 않는다. 다른 하나는 실제 Lean에서 의존 증거 추출기(`_DEPENDENCY_EXTRACTOR`)가 내는 식 표현의 모양이다. 식은 공유 부분식을 한 번만 적는 DAG(`lean-expr-dag/1`)로 직렬화되고, 문자열 리터럴의 공백과 유니코드 결속자 이름을 보존하며, 줄바꿈으로 펼쳐지지 않고, 공통 의존 본문은 한 번만 출력된다.

## 모듈 수준 요소

- 행 9: `scripts/` 폴더를 `sys.path` 앞에 넣는 공통 머리.
- 행 10–12: `test_categories.test_group`을 `category`로, `formal`, `provider_fixtures.actual_command`를 import한다.
- `_dependency_rows(source, declarations)` (행 15–25): docstring은 "검증기가 해시로 줄이는, 중앙 검사 파일의 의존 본문 행"이라고 밝힌다. 임시 폴더에 `formal._check_file(source.encode(), declarations, extract_evidence=True)`로 만든 `check.lean`을 쓰고, `formal._job_run([*actual_command(), check], workspace)`로 실제 Lean을 돌린다. 종료 코드가 0이 아니면 stdout과 stderr를 담은 `AssertionError`를 던진다. 출력에서 `__DO_MATH_DEPENDENCY__`로 시작하는 줄마다 접두를 떼고 JSON으로 읽은 목록을 돌려준다. `verify_lean`을 거치지 않으므로 검증기가 버리는 원 행을 그대로 볼 수 있다. 사용처는 행 59, 71, 126의 세 시험이다.
- 행 133–134: 직접 실행하면 `unittest.main()`.

## FormalRuntimeTests (행 28–130)

`unittest.TestCase`를 그대로 상속한다. 클래스 표지·설정 훅·도우미·속성이 없다. 표지는 메서드마다 붙는다.

### `test_shared_expression_evidence_does_not_expand_shared_subterms` (행 30–56)
- 성질: 식 증거는 공유 부분식을 펼치지 않는 DAG이고, 결속자 이름을 구분하며, 모든 참조가 앞선 노드를 가리킨다.
- 준비: `import Lean`, 제품의 `_DEPENDENCY_EXTRACTOR` 원문, `run_elab` 블록으로 된 Lean 원천. 블록은 `mkRawNatLit 0`에서 시작해 `Nat.add value value`를 20번 겹친 식의 증거를 출력하고, 결속자 이름만 `left`, `right`로 다른 두 람다를 적용한 식의 증거를 출력한다.
- 실행: 원천을 `sharing.lean`에 쓰고 `formal._job_run([*actual_command(), 원천], workspace)`로 실제 Lean을 돌린다.
- 단언: 종료 코드가 0이다. 출력 두 줄을 JSON으로 읽는다. 첫 증거의 `format`이 `lean-expr-dag/1`이고, 노드 수가 42 이하이며(공유를 펼치면 노드가 2의 20제곱 규모로 는다), 출력 전체가 10000자 미만이다. 둘째 증거의 노드 인자 가운데 `atom` 값 집합이 `` `left ``와 `` `right ``를 모두 포함한다. 두 증거 모두 모든 `ref` 인자가 자기 노드 번호보다 작다(자식이 부모보다 먼저 적힘).
- 대역: 없음.
- 비고: 메서드 표지 `category('lean')`. 실제 Lean(`actual_command()`, `DO_MATH_KNOWLEDGE_TEST_LEAN` 또는 `.skill-workspace/do-math-toolchains`)과 실제 Windows Job을 쓴다. Lean이 없을 때 건너뛰는 장치는 없다. 상한 42는 20층마다 `app` 노드 둘과 공유되는 `Nat.add` 상수 하나, 리터럴 하나를 센 값과 맞는다.

### `test_flat_representation_preserves_literal_spaces_and_unicode_binders` (행 59–68)
- 성질: 의존 본문 표현은 문자열 리터럴 안의 연속 공백과 이스케이프를 보존하고, 유니코드 결속자 이름을 유지한다.
- 준비: `textBase : String := "a  b\nc"`(Lean 원천 안의 역슬래시 n), `identityBase (Ω : Nat)`, 이를 참조하는 `textLeaf`, `functionLeaf`.
- 실행: `_dependency_rows(source, ['textLeaf', 'functionLeaf'])`로 실제 Lean의 의존 본문 행을 얻어 이름별 사전으로 만든다.
- 단언: `textBase`의 `evidence.value`(DAG JSON 문자열)를 다시 읽은 노드 인자의 `atom` 가운데 `"a  b\nc"`를 포함한 것이 있다. `identityBase`의 `evidence.type`에 `Ω`가 있다.
- 대역: 없음.
- 비고: 메서드 표지 `category('lean')`. 실제 Lean과 Windows Job.

### `test_dependency_representation_does_not_expand_layout_indentation` (행 71–76)
- 성질: 의존 본문의 형(type)과 값 표현에는 줄바꿈이 없다. 곧 Lean의 조판 들여쓰기로 펼쳐지지 않는다.
- 준비: `theorem good (p : Prop) : p ∨ ¬p := Classical.em p`.
- 실행: `_dependency_rows(원천, ['good'])`.
- 단언: 행이 하나 이상 있다. 모든 행의 `evidence.type`과 `evidence.value`(없으면 빈 문자열)에 `\n`이 없다. 실패 메시지는 행의 `name`이다.
- 대역: 없음.
- 비고: 메서드 표지 `category('lean')`. 실제 Lean과 Windows Job. 제품 추출기의 `flatFormat`(원천 상수 안)이 이 성질을 만든다.

### `test_uncapped_lean_admission_with_an_adopted_host_budget` (행 78–99)
- 성질: 호스트 자원 예산이 채택된 인스턴스에서도 형식 검사 프로필은 Job 자원 상한·호출 시간 상한 없이 입장하고, 예약 행을 만들지 않는다.
- 준비: 1단. `host_capacity_fixture()`에서 승인된 호스트 제약만 가져온다. 제약 없는 `build_profiles(PROFILE_CONFIG)`에서 `HOST_ROLES`에 드는 역할마다 요구(`jobs=1`, `memory_bytes=128 MiB`, `cpu_rate_basis_points=1000`)를 만든다. 그 제약과 요구, `lean_command=[sys.executable]`을 넣은 설정으로 인스턴스 프로필을 다시 짓고 `formal_check` 프로필을 고른다.
- 실행: `job_resource_limits(profile)`, `machine_invocation(profile, trust_environment={'toolchain': {'configured_command': [sys.executable]}})`, 빈 런타임에서 `SessionSlots(runtime, instance).acquire('EX-unlimited', profile=profile, execution=...)`.
- 단언: `job_resource_limits`가 `None`이다. 호출 인자에 `timeout_seconds`와 `resource_limits`가 없다. `acquire`가 참이고 `runtime['reservations']`가 빈 사전이다.
- 대역: 없음.
- 비고: 표지 없음. `formal_check`가 `HOST_ROLES`(=`PROFILE_ROLES - UNCAPPED_ROLES`)에 들지 않으므로 요구 표에서 빠지고 호스트 자원을 받지 않는다는 제품 규칙을 공개 함수로 확인한다. 프로세스를 띄우지 않는다.

### `test_output_larger_than_the_discarded_cap_is_preserved` (행 102–108)
- 성질: Job 안에서 도는 명령의 표준 출력은 매우 커도(33 MiB) 잘리지 않고 전부 보존된다.
- 준비: `'x'`를 `33 * 1024 * 1024`개 쓰는 Python 명령.
- 실행: `formal._job_run([sys.executable, '-c', ...], Path(directory))`.
- 단언: 종료 코드가 0이고 stdout의 길이가 정확히 33 MiB다.
- 대역: 없음.
- 비고: 메서드 표지 `category('resource')`. 실제 Windows Job과 작업자·자식 프로세스를 쓴다. 이름의 "discarded cap"은 지금은 없는 출력 상한을 가리킨다. 제품 `_worker`는 파이프 없이 파일에 바로 쓴다고 주석으로 밝힌다(`formal.py`의 "no PIPE buffers, reader threads or output truncation").

### `test_formal_job_completes_without_deadline` (행 110–115)
- 성질: 형식 Job은 기한 없이 명령이 끝날 때까지 기다리고 그 출력을 돌려준다.
- 준비: 0.25초 자고 `completed`를 출력하는 Python 명령.
- 실행: `formal._job_run([...], Path(directory))`.
- 단언: 종료 코드가 0이고 stdout을 다듬은 값이 `completed`다.
- 대역: 없음.
- 비고: 실제 Windows Job을 쓰지만 표지·skip이 없다. 0.25초는 짧으므로 이 시험은 "기한이 없음"을 직접 증명하지 않고, 정상 완료 경로가 성공 결과를 낸다는 것을 확인한다. `_job_run`에는 시간 인자 자체가 없다.

### `test_formal_verification_does_not_apply_memory_or_cpu_caps` (행 117–123)
- 성질: `verify_lean`은 컴파일 Job에 메모리·CPU 상한을 넘기지 않는다.
- 준비: `formal.inspect_toolchain`을 `{}`로, `formal._job_run`을 `(1, '', 'fixture', False)`로 패치한다.
- 실행: `formal.verify_lean(source='', declarations=['good'], lean_command=[sys.executable])`.
- 단언: 패치된 `_job_run`의 마지막 호출 키워드에 `resource_limits`가 없거나 `None`이다.
- 대역: `inspect_toolchain`, `_job_run` 패치.
- 비고: 현재 `_job_run`에는 `resource_limits` 매개변수가 없으므로, 이 단언은 누군가 그 인자를 다시 넘기기 시작하는 회귀를 막는다. 반환된 종료 코드 1은 결과에 쓰이지 않는다.

### `test_common_dependency_bodies_are_emitted_once` (행 126–130)
- 성질: 두 선언이 같은 의존을 공유하면 실제 Lean 출력에서 그 의존 본문 행은 한 번씩만 나온다.
- 준비: `first`, `second` 두 정리(모두 `True.intro`).
- 실행: `_dependency_rows(원천, ['first', 'second'])`.
- 단언: 행 이름 집합이 `{'True', 'True.intro'}`이고 행 수가 정확히 2다.
- 대역: 없음.
- 비고: 메서드 표지 `category('lean')`. 실제 Lean과 Windows Job. `test_formal`의 `test_dependency_bodies_are_one_table_shared_by_the_declared_closures`가 합성 출력으로 본 성질의 실제 Lean 쪽이다.

## 관계

- 같은 제품 기능을 다른 층에서 보는 모듈: `test_formal`은 `verify_lean`의 판정·신원 확인과 `_job_run`의 정지·실패 보고를 보고, 이 모듈은 무제한 계산과 추출기 출력의 모양을 본다. `test_host_resources`와 `test_machine_parallel`은 호스트 자원 예약과 기계 역할 병렬 실행을, `test_execution_profiles`(`foundation` 조각)는 프로필 계산을 본다.
- 픽스처 의존: `provider_fixtures.actual_command`(실제 Lean 경로), `host_capacity_fixture`와 `PROFILE_CONFIG`(행 78 시험).
- 이 모듈에만 있는 도우미: `_dependency_rows`. `verify_lean`을 거치지 않고 `_check_file`과 `_job_run`을 직접 조합해, 검증기가 해시로 줄여 버리는 원 행을 관찰한다.
- 격리 표지: 실제 Lean 네 시험은 `lean`, 33 MiB 출력 시험은 `resource`다. 같은 실제 Job을 쓰는 `test_formal_job_completes_without_deadline`에는 표지가 없다.
