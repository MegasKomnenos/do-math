# test_environment_validation

| 항목 | 값 |
|---|---|
| 조각 | `foundation` |
| 원문 | `.claude/skills/do-math/scripts/tests/test_environment_validation.py` (412행) |
| 클래스 / 테스트 | 4 / 23 |
| 시험 대상 제품 코드 | `do_math/trust_validation.py`의 `check_environment`, `environment_errors`, `register_request_errors`; `do_math/trust_inventory.py`(`read_record`, `identity_errors`, `observe_fingerprint`, `usable_errors`, `binding`, `writer_lock`, `validation_sha256`, `write_record`, `representative_check_seconds`); `do_math/formal.py`의 `toolchain_identity_errors`, `_project_identity`, `_job_run`; `scripts/setup_lean.py`의 `rerecord`, `check_contents`, `record_installation`, `write_trust_request`, `verify_environment`, `_settled_fingerprint`, `Refused`; `do_math/initialization.py`의 `observation_window_warnings`; `do_math/engine.py`의 `_record_control_result`; `do_math/execution_profiles.py`의 `build_profiles`, `seal_profile` |
| 사용하는 픽스처 모듈 | `research_fixtures`: `bare_engine`, `fixture_setup_lean`, `trust_environment`, `trust_fixture`(그리고 행 18에서 import하지만 이 모듈 안에서 부르지 않는 `validation_fixture`) |
| 격리 표지 | 없음 |
| 시작 상태 | 1단. 합성 도구 모음과 그 기록을 임시 폴더에 만든 뒤(`trust_fixture`) 검증기와 `setup_lean` 함수를 직접 부른다. 실제 Lean은 쓰지 않는다 |

## 목적

모듈 docstring은 "Toolchain records, identity and olean fingerprints under the accidental-change model."이다. 제품 `trust_inventory.py`의 docstring이 모델을 정의한다. 도구 모음 기록 파일 하나가 설치된 Lean/Mathlib 정체성 하나를 기술한다. `setup_lean.py`만 기록을 쓰고 연구 인스턴스는 읽기만 한다. 위협 모델은 우발적 변경(갱신, 재설치, 동기화, 실수, 디스크 손상)이다. 지문 행은 판단 파일 하나의 `scandir` 메타데이터(크기, 수정 시각, 생성 시각)다. 그래서 크기와 두 시각을 보존한 채 바뀐 바이트는 명시적 내용 검사로만 찾는다.

이 모듈은 네 영역을 검사한다.
1. 기록의 계약, 정체성, 지문, 재기록, 재결박, 설치 기록(`ToolchainRecordTests`).
2. 대표 컴파일 증거의 생산(`RepresentativeCompileTests`).
3. 채택된 관찰 창이 대표 컴파일보다 짧을 때의 경고(`ObservationWindowWarningTests`).
4. Lean 역할 프로필이 명령만 고정한다는 규칙(`ActivationProfileTests`).

`check_environment`(trust_validation.py 행 116 이하)의 docstring은 "Live admission: record contract, identity and the olean fingerprint."다. 다른 지문은 기록의 현재 기준선과 같고, 결박된 기준선이 더 오래되었고, 정체성이 그대로일 때만 받아들인다. 그때 호출자가 재결박한다. 이 함수는 기준선을 쓰지 않는다.

## 모듈 수준 요소

- 행 13: 스킬의 `scripts/` 폴더를 `sys.path` 앞에 넣는다. 행 14에서 `setup_lean`을 모듈로 import한다.
- `set_birthtime(path, nanoseconds)` (행 21–37): docstring은 "Change only the creation time (Windows SetFileTime)."이다. `ctypes.WinDLL('kernel32')`의 `CreateFileW`로 파일 핸들을 쓰기 속성 권한(`0x100`)으로 연다. 나노초를 Windows FILETIME 틱(100ns, 1601년 기준 오프셋 `116444736000000000`)으로 바꾸어 `SetFileTime`의 생성 시각에만 넣고 핸들을 닫는다. 실패하면 `ctypes.WinError`를 던진다. `test_fingerprint_detects_size_modification_creation_and_recreation`만 쓴다. Windows 전용이다.
- 행 411–412: 직접 실행하면 `unittest.main()`을 부른다.

## ToolchainRecordTests (행 40–291)

`unittest.TestCase`를 그대로 상속한다. 표지와 클래스 속성이 없다.

- `setUp` (행 41–48): 테스트마다 새 임시 폴더를 만들고 `addCleanup`으로 정리한다. `trust_fixture(self.root, ['synthetic-lean'])`는 합성 설치(`toolchain/bin/lean.exe`, `lake.exe`, `libleanshared.dll`, `lib/lean/Init/Prelude.olean`)와 공유 도구 모음 기록, 등록 요청을 만든다. 검사기 정체성은 실제 `formal.py`다. 그 요청으로 `trust_environment`가 인스턴스 기록과 결박(`self.environment`, `self.binding`)을 만든다. 기록 경로는 `self.record_path`, 합성 olean은 `self.olean`이다.
- `record()` (행 50–51): 기록 파일을 `records.read_record`로 읽는다(계약 검사 포함).
- `rewrite(change)` (행 53–56): 기록 JSON을 계약 검사 없이 읽어 `change`로 고치고 다시 쓴다. 손상된 기록을 만들 때 쓴다.
- `recorded(*, validation=True)` (행 58–59): `fixture_setup_lean(self.request['toolchain'], self.root / 'smoke.lean', validation=...)` 문맥 관리자를 돌려준다. 이 픽스처는 `setup_lean.observe_identity`를 합성 정체성으로, `setup_lean.verify_environment`를 `validation_fixture` 결과(또는 `validation=False`면 `status='failed'`, `exit_code=1`)로 바꾸고, `do_math.file_io.RACY_NS`를 0으로 둔다.
- `rerecord()` (행 61–63): `recorded()` 안에서 `setup_lean.rerecord(['synthetic-lean'], <기록 폴더>, <root>/evidence, None)`을 부르고 결과를 돌려준다.

### `test_current_environment_is_verified_from_record_identity_and_fingerprint` (행 65–74)
- 성질: 방금 등록한 환경은 구조 검사와 등록 요청 검사를 통과하고, 기록·정체성·지문 검사로 `verified`가 되며, 재결박이 필요 없다. 지문의 판단 파일은 olean과 공유 라이브러리뿐이다.
- 준비: `setUp`의 합성 환경.
- 실행: `environment_errors`, `register_request_errors`(요청 사본), `check_environment(environment, binding)`.
- 단언: 앞의 두 검사가 빈 목록을 돌려준다. `check_environment`의 `status == 'verified'`, `identity_sha256 == exact_content_hash(toolchain)`, `fingerprint_sha256`이 결박의 값과 같고, `rebind` 키가 없다. 기록의 첫 기준선 지문 파일 집합이 `{'toolchain/bin/libleanshared.dll', 'toolchain/lib/lean/Init/Prelude.olean'}`이다.
- 대역: 없음(`trust_fixture`의 합성 파일).
- 비고: 판단 파일의 접미사는 `trust_inventory.JUDGMENT_SUFFIXES`(`.olean`, `.dll`, `.so`, `.dylib`)다. `lean.exe`와 `lake.exe`는 지문이 아니라 정체성 해시로 결박된다(같은 파일 행 26–27의 주석).

### `test_unknown_record_field_and_other_schema_are_rejected` (행 76–86)
- 성질: 기록 파일에 모르는 필드가 있거나, 다른 스키마를 말하거나, 기준선에 모르는 필드가 있거나, 정체성을 파일 안에서 고쳤으면 기록을 읽을 수 없는 것으로 보고 환경을 `invalid`로 판정한다.
- 준비: `subTest`로 네 변경을 `rewrite`로 가한다. (1) 최상위 `unrecognized=True`. (2) `schema='do-math-toolchain-record/2'`. (3) 첫 기준선에 `files=[]`. (4) `identity.version='edited'`. 원문 주석(행 77)은 "An identity edited inside one record file no longer matches its digest and ID."라고 밝힌다. 경우마다 원래 바이트로 되돌린다.
- 실행: `check_environment(environment, binding)`.
- 단언: `status == 'invalid'`이고, 첫 오류에 `'toolchain record unavailable'`이 들어 있다. 거부의 범주(읽기 실패)는 고정하지만, 네 경우의 세부 사유(`record_errors`의 메시지)는 구별하지 않는다.
- 대역: 없음.

### `test_success_label_cannot_replace_failed_representative_evidence` (행 88–95)
- 성질: 현재 기준선의 대표 검사가 실패했으면, 상태 표지 하나만으로 성공이 되지 않는다. 종료 코드와 상태가 모두 성공이어야 한다.
- 준비: `subTest`로 마지막 기준선의 `validation`에 `{'exit_code': 17}` 또는 `{'status': 'failed'}`를 덮어쓴다. 경우마다 되돌린다.
- 실행: `check_environment(environment, binding)`.
- 단언: `errors`에 `'current toolchain baseline has no successful representative check'`가 있다(`usable_errors`, trust_inventory.py 행 187–196).
- 대역: 없음.

### `test_search_paths_outside_the_recorded_roots_are_rejected` (행 97–106)
- 성질: 정체성의 Lean 검색 경로는 기록된 도구 모음과 프로젝트 루트 안에 있어야 하고, 두 루트는 겹치면 안 된다.
- 준비: 요청 정체성의 사본에 `project`를 둔다. `source_identity.root`는 `<root>/project`이고, 검색 경로는 `<project>/.lake/build/lib/lean`과 루트 밖의 `<root>/outside`다.
- 실행: `records.identity_errors(identity)`를 두 번 부른다. 두 번째에는 프로젝트 루트를 도구 모음의 `lib` 폴더로 바꾼다.
- 단언: 첫 결과가 정확히 `['Lean search path is outside the recorded toolchain and project roots: ' + <outside>]`다. 두 번째 결과에 `'toolchain and project roots must not overlap'`이 있다.
- 대역: 없음.

### `test_identity_detects_executable_checker_and_project_input_changes` (행 108–145)
- 성질: 정체성 재계산은 실행 파일의 기록 해시, 명령에 속한 다른 실행 파일, 실행 중인 검사기, Lake 프로젝트 입력의 변경을 각각 따로 찾는다.
- 준비: `setUp`의 요청 정체성.
- 실행: `formal.toolchain_identity_errors`를 여섯 단계로 부른다.
  1. 원래 정체성.
  2. `sha256`만 `'0'*64`로 바꾼 정체성.
  3. `lake.exe`를 `b'replaced by an update'`로 덮어쓴 뒤의 원래 정체성.
  4. 검사기 `formal.py`를 루트에 복사하고 `verifier_path`만 그 사본으로 바꾼 정체성.
  5. 사본을 `b'another checker'`로 바꾸고 `verifier_sha256`도 그 해시로 맞춘 정체성.
  6. `<root>/project`에 `lean-toolchain`(`v4.32.0`)과 `lake-manifest.json`을 쓰고, `formal._project_identity(['lake', '--dir', <project>, 'env', 'lean'], workspace=<임시>, expected={'manifest_hashes': None, 'source_identity': None})`로 관찰 정체성을 얻는다. `lake.exe`를 원래 합성 바이트로 되돌린다. 그 뒤 `subTest`로 `lean-toolchain`을 `v4.33.0`으로, 또는 `lake-manifest.json`을 `{"packages": [1]}`로 바꾼다. 명령과 `project`를 관찰값으로 바꾼 정체성을 검사하고, 경우마다 원래 바이트로 되돌린다.
- 단언: 단계별 반환은 다음과 같다. 모두 목록 전체의 등식이다.
  1. 빈 목록.
  2. `['approved toolchain file changed: ' + <lean.exe>]`. 원문 주석(행 111)은 "Each recorded hash holds on its own, even when the executable is also a command file."이라고 밝힌다.
  3. `['approved toolchain file changed: ' + <lake.exe>]`.
  4. lake 변경 하나뿐인 목록. 주석(행 119–120)은 "The checker is its running bytes: a copy elsewhere is the same checker, other recorded bytes are not."라고 밝힌다.
  5. `['approved checker is not the running checker', <lake 변경>]`.
  6. 두 경우 모두 `['approved project inputs changed']`.
- 대역: 없음.
- 비고: `_project_identity`는 기대값과 다르면 Lake를 실행하지 않고 `search_paths=[]`를 돌려준다(formal.py 행 378–380의 주석 "Never execute changed project code merely to discover its environment."). 그래서 Lake 실행은 없다. 대신 `project_source_identity`가 프로젝트 폴더에 실제 `git rev-parse` 자식 프로세스를 실행한다(`formal._git`). 임시 폴더가 Git 저장소 밖이므로 결과는 빈 루트이고, 모든 입력을 미추적 파일로 해시한다.

### `test_fingerprint_detects_size_modification_creation_and_recreation` (행 147–171)
- 성질: olean 지문은 크기, 수정 시각, 생성 시각의 변경과 같은 바이트로의 재생성, 새 모듈의 추가를 모두 찾는다.
- 준비: olean의 원래 바이트와 `os.stat`을 떠 둔다. 지역 함수 `restore`는 바이트와 두 시각을 되돌리고 `set_birthtime`으로 생성 시각도 되돌린 뒤, 환경이 다시 `verified`인지 단언한다.
- 실행: 다섯 변경을 `subTest`로 가한 뒤 `check_environment`를 부른다. (1) 크기: 한 바이트를 덧붙인다. (2) 수정 시각을 1초 뒤로. (3) 생성 시각을 10초 앞으로(`set_birthtime`). (4) 지우고 같은 바이트로 다시 쓴 뒤 수정 시각을 1초 뒤로. (5) 같은 폴더에 `Extra.olean`을 만든다.
- 단언: 매번 `status == 'invalid'`이고, 첫 오류에 `'olean fingerprint differs'`가 있으며, `changed_files`가 비어 있지 않다. 경우마다 `Extra.olean`을 지우고 `restore()`가 `verified`로 돌아왔음을 확인한다.
- 대역: 없음. 파일 시각을 실제로 바꾼다.
- 비고: `set_birthtime`과 `st_birthtime_ns`를 쓰므로 Windows 전용이다. 재생성 경우는 지우고 같은 바이트로 다시 쓴 뒤 수정 시각을 1초 뒤로 옮긴다. NTFS의 파일 이름 터널링 때문에, 같은 이름으로 곧바로 다시 만든 파일은 이전 생성 시각을 물려받을 수 있다(이 기계에서 지우고 곧바로 다시 쓴 파일의 `st_birthtime_ns`가 그대로임을 확인했다). 그러므로 이 경우를 지문 차이로 드러내는 것은 수정 시각의 이동이다. 생성 시각의 변화에 기대지 않는다.

### `test_fingerprint_does_not_see_content_changed_with_all_metadata_preserved` (행 173–188)
- 성질: 크기와 두 시각을 모두 보존한 바이트 변경은 지문으로 보이지 않는다. 명시적 내용 검사만 그것을 찾고, 찾은 뒤에는 그 기준선을 사용할 수 없게 된다.
- 준비: olean의 첫 바이트를 한 비트 뒤집고 수정 시각을 원래대로 되돌린다. 생성 시각이 그대로임을 단언한다.
- 실행: `check_environment`. 이어서 `recorded()` 안에서 `setup_lean.check_contents(<기록 폴더>, None, ['synthetic-lean'])`. 다시 `check_environment`.
- 단언: 첫 검사가 `verified`다(모델의 선언된 한계). 내용 검사의 `status == 'mismatch'`이고, `check.mismatched == ['toolchain/lib/lean/Init/Prelude.olean']`이다. 마지막 검사는 `invalid`이고, 오류에 `'a content check found files that differ from the current toolchain baseline'`이 있다.
- 대역: `fixture_setup_lean`(정체성 관찰의 대역). `check_contents`에 기록 ID를 주지 않으므로, 제품은 `observe_identity`로 현재 정체성을 관찰해 그 정체성의 유일한 기록을 찾는다.
- 비고: docstring은 "The declared limit of the accidental-change model; only a content check finds it."이다.

### `test_content_check_passes_records_history_and_never_blocks_readers` (행 190–199)
- 성질: 기록 작성자의 잠금은 읽는 인스턴스를 막지 않고 다른 작성자만 막는다. 통과한 내용 검사는 검사 이력에 남고, 환경은 계속 `verified`다.
- 준비: `records.writer_lock(<기록 폴더>)`을 잡는다.
- 실행: 잠금 안에서 `check_environment`와 `self.rerecord()`. 잠금을 푼 뒤 `setup_lean.check_contents(<기록 폴더>, <기록 ID>, None)`와 `check_environment`.
- 단언: 잠금 안의 검사가 `verified`다(주석 행 192 "Instances only read the record; a running writer never blocks them."). 잠금 안의 재기록은 `OSError`를 던진다. 내용 검사 결과의 `(status, check.baseline)`이 `('passed', 0)`이다. 기록의 `checks`가 `[result['check']]`다. 마지막 검사가 `verified`다.
- 대역: 재기록 쪽에만 `fixture_setup_lean`. 잠금은 실제 OS 잠금이다(같은 프로세스 안의 다른 기술자끼리도 충돌한다).
- 비고: 이 시험의 `check_contents`는 기록 ID를 받으므로 정체성을 관찰하지 않는다(`resolve_record`가 ID로 기록을 바로 읽는다). 그래서 명령 인자가 `None`이어도 된다.

### `test_rerecord_after_metadata_only_change_rebinds_each_instance_once` (행 201–221)
- 성질: 메타데이터만 바뀐 설치는 재기록으로 새 기준선을 얻는다. 같은 기록을 결박한 모든 인스턴스는 각자 한 번씩 재결박 표지를 받고, 새 결박을 쓴 뒤에는 표지가 없다.
- 준비: 같은 요청으로 두 번째 환경 `TE-other`와 결박을 만든다. olean의 수정 시각을 1초 뒤로 옮긴다.
- 실행: `check_environment`. `self.rerecord()`. 두 환경에 각각 `check_environment`. 새 결박으로 첫 환경을 다시 검사한다.
- 단언: 재기록 전 검사가 `invalid`다. 재기록 결과의 `status == 'recorded'`다. 기록의 기준선이 둘이고, 둘째의 `content`가 첫째와 같다. `records.binding(record)`가 결과의 `binding`과 같다. 두 환경 모두 `verified`이고, `rebind.previous`가 원래 결박, `rebind.current`와 `binding`이 새 결박이다. 새 결박으로 다시 검사하면 `verified`이고 `rebind`가 없다.
- 대역: `fixture_setup_lean`(재기록 안에서).

### `test_rerecord_refuses_changed_content_identity_or_failed_compile` (행 223–239)
- 성질: 재기록은 판단 파일의 내용이 바뀌었거나, 설치 정체성이 기록과 다르거나, 대표 컴파일이 실패하면 거부하고 기준선을 더하지 않는다.
- 준비: `setUp`의 환경.
- 실행: 세 번의 재기록.
  1. olean의 첫 바이트를 `b'Z'`로 덮어쓰고(크기는 그대로) `self.rerecord()`를 부른다.
  2. olean을 원래 합성 바이트(`'CORE_TESTS synthetic lib/lean/Init/Prelude.olean for synthetic-lean'`)로 되돌린다. `setup_lean.observe_identity`가 `version='Lean test 4.33.0'`인 정체성을 돌려주게 하고, 기록 ID를 주어 `setup_lean.rerecord`를 부른다.
  3. `recorded(validation=False)` 안에서 `setup_lean.rerecord(..., None)`을 부른다.
- 단언: 세 번 모두 `setup_lean.Refused`가 난다. 1의 결과 `mismatched == ['toolchain/lib/lean/Init/Prelude.olean']`, 2의 결과 `reason`에 `'identity differs'`, 3의 결과 `status == 'failed'`다. 끝으로 기록의 기준선이 여전히 하나다.
- 대역: `patch.object(setup_lean, 'observe_identity', ...)`, `fixture_setup_lean`.
- 비고: 2단계는 `fixture_setup_lean` 밖이라 `RACY_NS`가 패치되어 있지 않지만, 정체성 비교가 지문 관찰보다 먼저이므로 대기 없이 거부된다(setup_lean.py `rerecord`).

### `test_rebind_requires_the_current_baseline_and_the_same_identity` (행 241–252)
- 성질: 재결박은 관찰 지문이 기록의 현재 기준선과 같을 때만, 그리고 정체성이 그대로일 때만 일어난다.
- 준비: olean 수정 시각을 1초 뒤로 옮기고 재기록해 두 번째 기준선을 만든다.
- 실행: (1) 수정 시각을 2초 뒤로 옮기고 원래 결박으로 `check_environment`. (2) 수정 시각을 다시 1초 뒤(현재 기준선과 같은 지문)로 되돌리고, 실행 파일 `lean.exe`를 다른 바이트로 바꾼 뒤 `check_environment(..., identity=False)`.
- 단언: (1)은 `invalid`다. (2)는 `invalid`이고 `rebind`가 없다.
- 대역: `fixture_setup_lean`(재기록 안에서).
- 비고: `identity=False`는 형식 검사 직전의 입장 경로(`verify_formal`)가 쓰는 모드다. 이 모드에서도 재결박 직전에는 정체성을 다시 확인한다는 제품 분기(trust_validation.py 행 152–160)를 (2)가 검사한다.

### `test_install_records_once_and_never_appends_a_baseline` (행 254–269)
- 성질: 설치 기록은 같은 정체성의 기록을 한 번만 만들고 기준선을 덧붙이지 않는다. 메타데이터가 바뀐 같은 설치는 재기록을 요구하며 거부된다. 정체성이 다르면 새 기록을 만든다.
- 준비: `setUp`의 환경.
- 실행: (1) `recorded()` 안에서 `setup_lean.record_installation(['synthetic-lean'], <기록 폴더>, <evidence>)`. (2) 같은 문맥에서 olean 수정 시각을 1초 뒤로 옮기고 다시 부른다. (3) 버전만 다른 정체성으로 `fixture_setup_lean`을 새로 열고 부른다.
- 단언: (1)의 `(status, created) == ('recorded', False)`다. (2)는 `Refused`이고 결과의 `status == 'rerecord_required'`다. 이때 기록의 기준선이 여전히 하나다. (3)의 `created`가 참이고, `record_id`가 원래 기록 ID와 다르며, 기록 폴더의 `TC-*.json`이 둘이다.
- 대역: `fixture_setup_lean`.

### `test_baseline_waits_for_settled_fingerprints_and_refuses_a_changing_install` (행 271–278)
- 성질: 기준선은 모든 판단 파일의 지문이 안정 구간(racy window)을 벗어난 뒤에만 기록한다. 세 번 기다려도 안정되지 않으면 설치가 아직 바뀌는 중이라며 거부한다.
- 준비: `setUp`에서 방금 쓴 합성 파일. 원문 주석(행 272)은 "The fixture files were just written, so their fingerprints are inside the racy window."라고 밝힌다. `RACY_NS`는 패치하지 않는다.
- 실행: `setup_lean.observe_identity`를 합성 정체성으로, `setup_lean.time.sleep`을 대역으로 바꾸고 `setup_lean.rerecord(...)`를 부른다.
- 단언: `RuntimeError`의 메시지가 `'still changing'`에 맞는다. `sleep` 호출 수가 3이다. 기록의 기준선이 하나다.
- 대역: `patch.object(setup_lean, 'observe_identity', ...)`, `patch.object(setup_lean.time, 'sleep')`.
- 비고: 제품 `_settled_fingerprint(identity, attempts=3)`는 매 시도 뒤 `RACY_NS / 1e9`초를 잔다. 대기를 대역으로 바꾸어 실제 시간 없이 세 번의 시도를 관찰한다. 이 시험은 `setUp`과 이 시험의 첫 관찰 사이가 2초(`RACY_NS`)보다 짧다는 시간 전제를 둔다.

### `test_recorded_summary_reports_the_representative_compile_duration` (행 280–283)
- 성질: 설치 기록 요약은 현재 기준선의 대표 컴파일 시간을 초 단위로 보고한다.
- 준비: `setUp`의 기록. 그 기준선의 검증 증거는 `validation_fixture`가 만든 것으로, 시작 `2026-09-20T00:00:00Z`, 끝 `00:00:01Z`다.
- 실행: `recorded()` 안에서 `setup_lean.record_installation(...)`.
- 단언: `representative_check_seconds == 1`.
- 대역: `fixture_setup_lean`.

### `test_trust_request_names_the_record_and_its_current_baseline` (행 285–291)
- 성질: 등록 요청 파일은 기록의 정체성, 허용 공리, 기록 참조, 현재 기준선의 결박을 담는다. 이미 있는 경로에는 쓰지 않는다.
- 준비: `{'record_path': <기록 경로>, 'binding': records.binding(<기록>)}`.
- 실행: `setup_lean.write_trust_request(result, <root>/request.json)`를 두 번 부른다.
- 단언: 처음 쓴 파일의 JSON이 `trust_fixture`가 돌려준 요청(`self.request`)과 같다. 두 번째 호출은 `FileExistsError`다(제품은 `'x'` 모드로 연다).
- 대역: 없음.

## RepresentativeCompileTests (행 294–333)

`unittest.TestCase`를 그대로 상속한다. 표지, 속성, 훅, 도우미가 없다. 컴파일러는 모두 `do_math.formal._job_run` 대역이나 `WindowsJob` 대역으로 바꾼다.

### `test_validation_preserves_source_output_and_exact_command` (행 295–306)
- 성질: 대표 컴파일 증거는 원본 파일, 출력, 실제로 실행한 명령을 그대로 보존하고, 같은 내용을 `validation.json`으로 증거 폴더에 남긴다.
- 준비: 정체성 `{'executable': <임시>/lean/bin/lean.exe, 'project': None}`.
- 실행: `_job_run`이 `(0, 'ok', '', False)`를 돌려주게 하고 `setup_lean.verify_environment(['test-lean'], <임시>/evidence, identity)`.
- 단언: `status == 'verified'`, `scope == 'lean_core_representative_proofs'`다. `command`가 `_job_run`의 첫 위치 인자와 같다. `stdout == 'ok'`다. `source_sha256`이 원본 파일 바이트의 SHA-256이다. 원본 옆의 `validation.json`이 반환 기록과 같다.
- 대역: `patch('do_math.formal._job_run', return_value=(0, 'ok', '', False))`.
- 비고: 프로젝트가 없으므로 원본은 Lean 코어만 쓰는 `CORE_SMOKE`다. 제품은 `operation_trace.tracing`으로 증거 폴더 아래 `operations` 기록도 남기지만, 이 시험은 그것을 단언하지 않는다.

### `test_failure_and_stop_never_produce_verified_evidence` (행 308–315)
- 성질: 컴파일 실패나 정지는 `verified` 증거를 만들지 않고, 진단 출력을 보존한다.
- 준비: `subTest`로 두 반환. `(1, '', 'diagnostic', False)`(종료 코드 1)와 `(None, '', '', True)`(정지)다.
- 실행: `setup_lean.verify_environment(...)`.
- 단언: `status == 'failed'`이고, `stderr`가 반환의 셋째 값과 같다.
- 대역: `_job_run` 대역.

### `test_evidence_inside_a_recorded_root_is_rejected` (행 317–321)
- 성질: 대표 컴파일 증거 폴더는 기록되는 도구 모음과 프로젝트 루트 밖에 있어야 한다.
- 준비: 정체성의 실행 파일이 `<임시>/lean/bin/lean.exe`이므로 도구 모음 루트는 `<임시>/lean`이다.
- 실행: 증거 폴더를 `<임시>/lean/evidence`로 주고 `verify_environment`.
- 단언: `ValueError`의 메시지가 `'outside the recorded'`에 맞는다.
- 대역: 없음(컴파일 전에 거부되므로 `_job_run`을 부르지 않는다).

### `test_compiler_job_does_not_inherit_unregistered_library_overrides` (행 323–333)
- 성질: 컴파일러 Job은 등록되지 않은 라이브러리 덮어쓰기 환경변수(`LEAN_PATH`, `LEAN_SYSROOT`, `LAKE_HOME`)를 물려받지 않는다.
- 준비: 세 변수를 `'outside'`로 둔 환경. `formal.WindowsJob`을 호출 인자를 기록하고 `RuntimeError('observe job arguments')`를 던지는 대역으로 바꾼다.
- 실행: `formal._job_run(['unused-compiler'], <임시>)`.
- 단언: `RuntimeError`가 난다. `WindowsJob`에 넘긴 키워드 인자 `env`에 세 변수가 없다.
- 대역: `patch.dict('os.environ', ...)`, `patch.object(formal, 'WindowsJob', side_effect=RuntimeError(...))`.
- 비고: 실제 Job을 만들기 직전에 멈추므로 자식 프로세스는 생기지 않는다.

## ObservationWindowWarningTests (행 336–391)

클래스 docstring은 "Adopted observation windows against the representative compile of a registered toolchain."이다. `unittest.TestCase`를 그대로 상속한다. 표지와 속성이 없다.

- `setUp` (행 338–349): 임시 폴더에 `trust_fixture`로 기록을 만든다. 첫 기준선의 검증 증거 `finished_at`을 `'2026-09-20T00:03:59.2Z'`로 바꾼다(주석: 시작 뒤 239.2초). `validation_sha256`을 다시 계산하고 `records.write_record`로 쓴다. 결박을 새로 계산하고, `trust_environment(request, status='registered')`로 등록 상태의 환경과 결박을 둔다. 제품의 `representative_check_seconds`는 올림하므로 대표 컴파일 시간은 240초가 된다.
- `state(**windows)` (행 351–358): `build_profiles({**DEFAULT_CONFIG, **windows})`의 프로필을 가진 인스턴스를 만든다. 인스턴스는 `config={}`, 위의 신뢰 환경 하나, `lifecycle={'state': 'initializing', 'adoption': {}}`를 가진다. 런타임은 `status='initializing'`, 빈 `history`, 결박을 가진다.

### `test_windows_shorter_than_the_representative_compile_are_warned` (행 360–372)
- 성질: 도구 검토 창(`tool_review_window_seconds`)이 등록된 도구 모음의 대표 컴파일보다 짧으면, 그 창을 쓰는 프로필마다 경고가 나온다. 같거나 길면 경고가 없다.
- 준비: `state(tool_review_window_seconds=120, self_check_response_window_seconds=240)`.
- 실행: `observation_window_warnings(instance, runtime)`. 이어서 도구 검토 창 240으로 다시 부른다.
- 단언: 첫 결과가 비어 있지 않고, 경고의 역할에 `research_work`가 있다. 모든 경고의 `field`, `window_seconds`, `environment_id`, `representative_check_seconds`가 `('tool_review_window_seconds', 120, <환경 ID>, 240)`이다. 두 번째 결과는 빈 목록이다.
- 대역: 없음.
- 비고: 제품 docstring(initialization.py 행 149–155)은 이 경고가 조언일 뿐 거부가 아니라고 밝힌다. 컴파일에 묶이는 창은 `COMPILE_BOUND_WINDOWS = ('tool_review_window_seconds',)` 하나다.

### `test_the_self_check_response_window_is_not_bound_by_a_compile` (행 374–378)
- 성질: 자기 점검 응답 창은 컴파일 시간보다 짧아도 경고하지 않는다.
- 준비: `state(tool_review_window_seconds=240, self_check_response_window_seconds=60)`.
- 실행: `observation_window_warnings(instance, runtime)`.
- 단언: 빈 목록이다.
- 대역: 없음.
- 비고: 원문 주석(행 375)이 이유를 밝힌다: 컴파일 같은 연구 호출이 응답 마감을 붙잡아 둔다(`ObservationTracker._hold_deadlines`). 이 붙잡기는 `test_observations.ObservationRuleTests`의 마감 시험들이 검사한다.

### `test_adoption_and_registration_results_return_the_warnings` (행 380–391)
- 성질: 신뢰 환경 등록 제어와 초기화 채택 결정의 제어 결과에는 관찰 창 경고가 실린다. 그 밖의 제어(멈춤)에는 실리지 않는다.
- 준비: `state(tool_review_window_seconds=120, self_check_response_window_seconds=60)`와 그 경고 `expected`. 그 상태를 가진 `bare_engine(instance, runtime)`.
- 실행: `subTest`로 두 제어의 결과를 기록한다. `('trust', {'operation': 'register'})`와 `('decision', {'change': {'kind': 'initialization', 'operation': 'adopt'}})`이며, `engine._record_control_result({'id': 'RQ-' + action, ...})`로 기록한다. 이어서 `RQ-pause`(`pause`)를 기록한다.
- 단언: 두 제어의 마지막 이력 행의 `result.observation_window_warnings`가 `expected`와 같다. 멈춤 제어의 결과에는 그 키가 없다.
- 대역: 없음(제어를 실제로 적용하지 않고 결과 기록 함수만 부른다).
- 비고: 제품은 `_adopts_observation_or_toolchain(request)`로 대상 제어를 가린다(engine.py 행 788–797).

## ActivationProfileTests (행 394–408)

`unittest.TestCase`를 그대로 상속한다. 표지, 속성, 훅, 도우미가 없다.

### `test_lean_roles_pin_only_the_command_and_activation_has_no_machine_settings` (행 395–408)
- 성질: Lean 역할(`formal_check`, `trust_check`)의 기계 프로필은 `lean_command` 하나만 고정한다. 신뢰 활성화(`trust_activate`) 프로필은 기계 설정을 갖지 않는다. 그 밖의 설정을 넣은 판본은 봉인되지 않는다.
- 준비: `build_profiles({**DEFAULT_CONFIG, 'lean_command': ['synthetic-lean']})`의 기계 프로필을 역할별로 모은다.
- 실행: 두 번의 `profiles.seal_profile`. (1) `trust_activate` 본문에 `machine={'mechanism': 'full_environment_scan', 'workers': 4}`를 넣는다. (2) `formal_check` 본문에 `machine={'lean_command': [...], 'tool_manifest': []}`를 넣는다.
- 단언: `trust_activate` 프로필에 `machine` 키가 없다. `formal_check`와 `trust_check`의 `machine`이 `{'lean_command': ['synthetic-lean']}`이다. 두 봉인 모두 `ValueError`의 메시지가 `'machine profile settings differ'`에 맞는다.
- 대역: 없음.
- 비고: 제품 주석(execution_profiles.py 행 91–92)은 "Lean roles pin only the command; the approved trust environment fixes its identity. Activation reads the toolchain record and needs no machine settings."라고 밝힌다. (1)은 Lean 역할이 아닌 기계 역할에 설정이 있으면 거부하는 분기를, (2)는 Lean 역할의 설정 키가 정확히 `{'lean_command'}`가 아니면 거부하는 분기를 검사한다(같은 파일 행 93–96).

## 관계

- 이 모듈은 도구 모음 기록과 입장 검사를 함수 단위로 검사한다. 같은 검사가 엔진 경로에서 쓰이는 모습은 `test_trust_continuation`(신뢰 활성화 생성기와 게시 관문)이 검사한다. 실제 Lean을 쓰는 경로는 `host` 조각의 `test_formal`, `test_formal_runtime`, `test_lean_preview`가 다룬다.
- `setup_lean.py`의 설치 모드와 준비 표지는 `test_standalone`이 검사한다.
- 관찰 창 경고의 반대쪽, 곧 마감이 연구 호출 동안 붙잡히는 규칙은 `test_observations`가 검사한다.
- 픽스처 의존은 다음과 같다(`consumers.json`). `research_fixtures.trust_fixture`와 `trust_environment`는 이 모듈과 `test_trust_continuation`을 포함해 여러 시험 모듈과 픽스처 모듈(`engine_fixtures`, `knowledge_fixtures`, `review_fixtures`)이 쓴다. `fixture_setup_lean`은 이 모듈 밖에 `test_lifecycle_engine`, `test_machine_parallel`, `test_submission_flow`가 쓴다. `consumers.json`은 `validation_fixture`의 시험 모듈 소비자로 이 모듈 하나를 적지만, 이 모듈은 그 기호를 행 18에서 import만 하고 부르지 않는다. 이 모듈의 검증 증거는 `trust_fixture`와 `fixture_setup_lean`이 안에서 부르는 `validation_fixture`로 간접적으로 만들어진다. 픽스처 쪽에서는 `knowledge_fixtures`가 쓴다. `bare_engine`은 이 모듈에서 관찰 창 경고 시험 하나만 쓴다.
- 이 모듈에만 있는 도우미는 `set_birthtime`과 `ToolchainRecordTests`의 `record`, `rewrite`, `recorded`, `rerecord`, `ObservationWindowWarningTests.state`다.
