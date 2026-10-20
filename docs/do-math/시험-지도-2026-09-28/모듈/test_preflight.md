# test_preflight

| 항목 | 값 |
|---|---|
| 조각 | `host` |
| 원문 | `.claude/skills/do-math/scripts/tests/test_preflight.py` (108행) |
| 클래스 / 테스트 | 2 / 10 |
| 시험 대상 제품 코드 | `do_math/preflight.py`의 `inspect_bundle`(행 33–85), `INSTALLED_DOCUMENTS`(행 20); `do_math/contracts.py`의 `reading_map`, `OPERATING_DOCUMENTS`(행 282); `do_math/lifecycle_engine.preserve_rejected_candidate`(행 32 이하); `do_math/record_schemas`의 `validate_lifecycle`; `do_math/repository.ResearchRepository`; `do_math/initialization.initialize_state` |
| 사용하는 픽스처 모듈 | `research_fixtures.git_init` |
| 격리 표지 | 없음 |
| 시작 상태 | `PersistedPreflightTests`: `git_init`한 실제 Git 저장소에 `initialize_state`의 초기 상태를 `ResearchRepository.initialize`로 게시한 상태(네 단 밖: 실제 Git 저장소 위의 초기화 직후 상태). `PreflightTests`: 설치 문서만 임시 폴더에 복사한 합성 스킬 폴더(1단에 준하는 파일 입력) |

## 목적

원문에는 모듈 docstring이 없다. 제품 `preflight.py`의 docstring은 "설치된 자기완결 스킬의 읽기 전용 구조 검사. 지역 계약을 적재할 뿐 의미의 옳음, 연구 품질, 실행 권한, 살아 있는 도구의 가용성은 확인하지 않는다"이다. `inspect_bundle`은 역할별 읽기 지도(`SKILL.md`의 배정 표)의 문서와 설치 문서(`INSTALLED_DOCUMENTS`: `README.md`, `references/CLI-실행-계약.md`, `requirements.txt`, `계약/독립-운영.md`, `scripts/operator_schedule.ps1`, `scripts/do_math.py`)가 스킬 안에 있고 비어 있지 않은지 확인해 해시를 적고, 역할 출력 스키마들이 유효한지 검사한다. 이 모듈의 `PreflightTests`가 이를 검사한다. `PersistedPreflightTests`는 이름과 달리 `preflight` 모듈이 아니라, 지속 상태의 사전 조건(거부된 후보의 보존, 손상된 헤드의 비재작성, 생애주기 고수위 시각의 형식)을 검사한다.

## 모듈 수준 요소

- 행 8: `scripts/` 폴더를 `sys.path` 앞에 넣는 공통 머리.
- 행 9–11: `INSTALLED_DOCUMENTS`, `inspect_bundle`, `reading_map`, `git_init`을 import한다.
- 행 107–108: 직접 실행하면 `unittest.main()`.

## PersistedPreflightTests (행 14–52)

`unittest.TestCase`를 그대로 상속하고 표지가 없다.

- `setUp` (행 15–25): 임시 폴더(`addCleanup`)에 `git_init`하고, 새 인스턴스 ID로 `ResearchRepository`를 연다. `initialize_state(instance_id=..., goal='G', workspace=root/'work', config={}, source_input='Original request')`로 초기 상태를 만들어 `store.initialize`로 게시하고 헤드를 `self.head`에 둔다. 함수 안의 `import subprocess`는 쓰이지 않는다.

### `test_good_head_preserves_rejected_raw_not_candidate_state` (행 27–33)
- 성질: 정상 헤드 위에서 거부된 후보를 보존하면 원 바이트만 새 스냅숏에 남고, 인스턴스·런타임 상태는 바뀌지 않는다.
- 준비: 클래스 절의 초기 상태.
- 실행: `preserve_rejected_candidate(store, head, raw=b'{broken candidate', reason='schema rejection')`.
- 단언: 결과의 `raw_ref`를 결과 `snapshot`에서 읽으면 원 바이트와 같다. 새 스냅숏에서 적재한 `(instance, runtime)`이 보존 전 적재값과 같다.
- 대역: 없음.
- 비고: 실제 Git 자식 프로세스를 쓴다.

### `test_damaged_head_is_not_rewritten_even_to_preserve_candidate` (행 35–44)
- 성질: 적재 검증을 통과하지 못하는 손상 헤드는, 거부된 후보를 보존하려는 목적이어도 다시 쓰지 않는다.
- 준비: 헤드의 레코드 가운데 `lifecycle` 가족 파일을 `b'{}\n'`로 바꾼 커밋을 저장소 원시 계층(`store._store.publish`)으로 만든다.
- 실행: 손상 헤드의 `store.load`, 이어 `preserve_rejected_candidate(store, damaged, raw=b'raw', reason='candidate rejected')`.
- 단언: 적재가 `ValueError`, `TypeError`, `KeyError`, `OSError`, `RuntimeError` 가운데 하나를 던진다(주석 행 39: 적재가 헤드를 검증하며 적재되지 않는 헤드는 손상이다). 보존이 `ValueError`(정규식 `damaged`; 제품 문구 `damaged current state cannot be rewritten: ...`)다. 저장소의 현재 헤드가 여전히 손상 헤드다(새 커밋 없음).
- 대역: 없음.

### `test_malformed_or_naive_high_water_is_rejected` (행 46–52)
- 성질: 생애주기 검증은 UTC 고수위 시각이 시각이 아니거나, 시간대가 없거나, UTC가 아닌 시간대이면 거부한다.
- 준비: 세 `subTest(value=...)`: `not-a-time`, `2026-09-20T00:00:00`(시간대 없음), `2026-09-20T09:00:00+09:00`.
- 실행: `runtime['last_observed_utc']`에 값을 넣고 `validate_lifecycle(instance, runtime)`.
- 단언: 모두 `ValueError`(정규식 `high-water`; 제품 문구 `current lifecycle contract: the persisted UTC high-water is absent or invalid`)다.
- 대역: 없음.
- 비고: `setUp`이 만든 Git 저장소는 이 시험에서 쓰이지 않고 초기 상태 사전만 쓰인다. 서브테스트 사이에 같은 `self.runtime`을 고쳐 쓴다.

## PreflightTests (행 55–104)

`unittest.TestCase`를 그대로 상속하고 표지가 없다.

- `setUp` (행 56–66): 임시 폴더 아래 `skill`을 만든다. 실제 스킬 폴더의 `reading_map(skill_root=source)`에 배정된 모든 문서 이름과 `INSTALLED_DOCUMENTS`를 모아, 같은 상대 경로로 복사한다. 나머지 파일(파이썬 코드 등)은 복사하지 않는다.

### `test_current_installation_has_all_roles_and_schemas` (행 68–72)
- 성질: 현재 설치의 문서 사본은 구조 검사를 통과하고, 두 검사 모두 10개 역할을 세며, 문서 의미는 검증 범위 밖으로 밝힌다.
- 준비: 클래스 절의 사본.
- 실행: `inspect_bundle(root)`.
- 단언: `status`가 `verified`다. `checks`의 `roles` 값이 `[10, 10]`이다(설치 문서 검사의 역할 수와 역할 출력 스키마 검사의 `len(ROLES)`). `not_verified`에 `document_semantics`가 있다.
- 대역: 없음.
- 비고: 역할 수 10은 시험에 직접 적힌 값이다. 역할이 늘거나 줄면 이 시험을 고쳐야 한다.

### `test_missing_required_document_is_incomplete` (행 74–76)
- 성질: 읽기 지도에 배정된 필수 문서가 없으면 설치는 불완전하다.
- 준비: 사본에서 `GLOSSARY.md`를 지운다.
- 실행: `inspect_bundle(root)`.
- 단언: `status`가 `incomplete`다.
- 대역: 없음.

### `test_reading_map_cannot_escape_skill` (행 78–82)
- 성질: 읽기 지도가 스킬 폴더 밖의 경로를 가리키면 설치는 불완전하다.
- 준비: 사본의 `SKILL.md`에서 `` `GLOSSARY.md` ``를 `` `../outside.md` ``로 바꾼다.
- 실행: `inspect_bundle(root)`.
- 단언: `status`가 `incomplete`다.
- 대역: 없음.
- 비고: 거부 사유(`reason`)는 단언하지 않으므로, 탈출 거부와 파일 부재 거부가 구분되지 않는다(`../outside.md`는 실제로도 없다).

### `test_missing_operating_contract_is_incomplete` (행 84–86)
- 성질: CLI 실행 계약 문서가 없으면 설치는 불완전하다.
- 준비: 사본에서 `references/CLI-실행-계약.md`를 지운다.
- 실행: `inspect_bundle(root)`.
- 단언: `status`가 `incomplete`다.
- 대역: 없음.

### `test_missing_independent_operator_contract_is_incomplete` (행 88–90)
- 성질: 독립 운영 계약 문서가 없으면 설치는 불완전하다.
- 준비: 사본에서 `계약/독립-운영.md`를 지운다.
- 실행: `inspect_bundle(root)`.
- 단언: `status`가 `incomplete`다.
- 대역: 없음.

### `test_missing_scheduler_entrypoint_is_incomplete` (행 92–94)
- 성질: 예약 작업 진입점 스크립트가 없으면 설치는 불완전하다.
- 준비: 사본에서 `scripts/operator_schedule.ps1`을 지운다.
- 실행: `inspect_bundle(root)`.
- 단언: `status`가 `incomplete`다.
- 대역: 없음.

### `test_read_only_and_observed_document_hashes` (행 96–104)
- 성질: 구조 검사는 스킬 폴더의 어떤 파일도 바꾸지 않고, 보고한 문서 해시는 실제 파일 바이트의 해시와 같다.
- 준비: 검사 전 사본의 모든 파일 해시.
- 실행: `inspect_bundle(root)`, 검사 뒤 모든 파일 해시.
- 단언: 검사 전후 해시가 같다. 첫 검사(`installed_documents`)의 `documents`에 적힌 각 해시가 검사 전 해시와 같다.
- 대역: 없음.

## 관계

- 같은 제품 기능을 다른 층에서 보는 모듈: `test_reading_map`(`foundation` 조각)은 `SKILL.md`의 배정 표 해석을, `test_contracts`는 역할 스키마를, `test_installation_discovery`는 설치 파일 집합을 본다. 거부된 후보 보존과 생애주기 검증은 `test_lifecycle_engine`·`test_checkpoint_persistence`(`lifecycle` 조각)와 `test_state_contract`(`foundation` 조각)가 다른 경로에서 본다.
- 픽스처 의존: `research_fixtures.git_init`(`PersistedPreflightTests.setUp`).
- 이 모듈에만 있는 도우미: 없음.
- 겹침과 보완: `PreflightTests`의 다섯 음성 시험(행 74–94)은 모두 `status`만 단언하고 `reason`을 보지 않는다. 양성 시험(행 68)은 `status`와 함께 역할 수와 `not_verified`를, 읽기 전용 시험(행 96)은 `status` 대신 파일 해시를 단언한다. 필수 문서 부재는 읽기 지도 문서(`GLOSSARY.md`)와 세 설치 문서로 나뉜다.
