# test_unicode_flow

| 항목 | 값 |
|---|---|
| 조각 | `foundation` |
| 원문 | `.claude/skills/do-math/scripts/tests/test_unicode_flow.py` (99행) |
| 클래스 / 테스트 | 1 / 5 |
| 시험 대상 제품 코드 | `do_math/repository.py`의 `canonical_json`, `ResearchRepository.initialize`, `load`, `read_record`; `do_math/git_store.py`의 `GitStateStore.publish`(`repository._store`로 부름); `do_math/state_contract.py`의 `StateContract.register_family`; `do_math/context_store.py`의 `write_source_catalog`, `read_source`, `build_role_manifest` |
| 사용하는 픽스처 모듈 | `research_fixtures`: `current_state`, `git_init`, `installed_contract` |
| 격리 표지 | 없음 |
| 시작 상태 | 1단(`canonical_json`, 문맥 저장 함수 직접 호출) 3개. 실제 Git 저장소에 시험용 가족을 등록한 계약으로 직접 `initialize`한 상태 2개(네 단 밖: 저장소 계층 직접 초기화) |

## 목적

모듈 docstring은 없다. 다섯 시험은 한 성질로 모인다. 유니코드 문자열은 저장·해시·역할 입력의 어느 경로에서도 정규화나 치환 없이 입력된 코드 포인트 그대로 보존된다. 표본 값은 결합 문자열 `"e\u0301"`(NFD 형태의 é)과, 서로 다른 두 키 `"K"`(U+212A KELVIN SIGN, 원문 행 32·57·83)와 `"K"`(ASCII U+004B)다. 원문은 결합 문자열을 이스케이프로 적고, 켈빈 기호는 문자 그대로 적는다. NFC나 NFKC 정규화를 거치면 앞의 것은 `"\u00e9"`로, 켈빈 기호는 ASCII `K`로 합쳐진다. 따라서 이 표본은 정규화가 끼어들면 드러난다. 제품 좌표는 `repository.py`의 `canonical_json`과 레코드 봉투 적재, `context_store.py`의 원천 카탈로그와 역할 목록이다.

## 모듈 수준 요소

- `SCRIPTS` (행 11): 스킬의 `scripts/` 폴더. 행 12–13에서 `sys.path`에 없으면 맨 앞에 넣는다.
- `INSTANCE_ID` (행 20): `"RI-"` 뒤에 0이 26개인 인스턴스 ID. 저장소를 여는 두 시험이 쓴다.
- 행 98–99: 직접 실행하면 `unittest.main(verbosity=2)`로 이 모듈의 시험을 돈다.

## UnicodeFlowTests (행 23–95)

`unittest.TestCase`를 그대로 상속하고 표지와 클래스 속성이 없다.

- `setUp` (행 24–26): `tempfile.TemporaryDirectory`를 열고 그 경로를 `self.root`로 둔다.
- `tearDown` (행 28–29): 임시 폴더를 정리한다.

### `test_exact_json_keeps_nfd_and_distinct_mathematical_keys` (행 31–38)
- 성질: `canonical_json`은 NFD 문자열과, 정규화하면 겹치는 두 키를 그대로 보존하고 항상 같은 바이트를 낸다.
- 준비: `{"text": "e\u0301", "names": {"K": "kelvin", "K": "ascii"}}`. 앞 키는 켈빈 기호 U+212A, 뒤 키는 ASCII `K`다.
- 실행: `canonical_json(value)`를 두 번 부르고, `canonical_json("e\u0301")`과 `canonical_json("\u00e9")`를 비교한다.
- 단언: 두 번의 직렬화 결과가 같다(결정성). `json.loads`로 되읽으면 원래 값과 같다. UTF-8로 풀어 낸 문자열에 켈빈 키와 ASCII 키가 각각 따옴표에 싸여 들어 있다. NFD의 `"e\u0301"`과 NFC의 `"\u00e9"`는 서로 다른 바이트로 직렬화된다.
- 대역: 없음.
- 비고: 원문 행 36과 37은 화면에서 같은 `'"K"'`로 보이지만, 행 36의 K는 U+212A이고 행 37의 K는 ASCII다.

### `test_exact_json_preserves_scalars_and_rejects_surrogates` (행 40–46)
- 성질: `canonical_json`은 BMP 경계와 보조 평면의 스칼라 값을 보존하고, 짝 없는 서로게이트는 값과 키 어디에 있든 거부한다.
- 준비: `"\ud7ff\ue000\U00010000\U0010ffff e\u0301 K K"`. 서로게이트 구간 바로 앞(U+D7FF)과 바로 뒤(U+E000), 보조 평면의 처음(U+10000)과 끝(U+10FFFF), NFD `e\u0301`, 켈빈 기호(U+212A, 원문에서도 문자 그대로)와 ASCII `K`를 담는다.
- 실행: 이 문자열을 키와 값으로 쓴 사전을 직렬화한 뒤 되읽는다. 이어서 서로게이트 다섯 가지를 두 자리에 넣어 직렬화한다. 다섯 가지는 `"\ud800"`, `"\udbff"`, `"\udc00"`, `"\udfff"`, 그리고 파이썬 문자열 안에서 이어 쓴 높은·낮은 서로게이트 쌍 `"\ud800\udc00"`(원문의 이스케이프 표기 그대로)이다. 두 자리는 `{"text": "prefix"+invalid+"suffix"}`의 값과 `{invalid: "value"}`의 키다.
- 단언: 앞의 사전은 되읽은 결과가 원래 값과 같다. 뒤의 열 경우는 모두 `ValueError`를 정규식 `"surrogate"`로 던진다. 거부 사유는 메시지 조각까지 고정된다.
- 대역: 없음.
- 비고: `subTest(value=repr(value))`로 열 경우를 나눈다. 서로게이트 쌍 `"\ud800\udc00"`도 거부된다. 파이썬 `str` 안의 두 서로게이트 코드 포인트는 U+10000 한 글자와 다른 값이기 때문이다. U+10000 한 글자는 앞의 사전에 들어 있고 보존된다.

### `test_git_save_reload_stores_the_record_as_exact_json` (행 48–63)
- 성질: Git에 저장한 레코드는 적재와 원시 레코드 읽기 모두에서 유니코드를 포함해 원래 값 그대로 돌아온다.
- 준비: `installed_contract()`로 설치된 가족을 모두 가진 새 `StateContract`를 만들고, 거기에 연구 가족 `unicode_fixture`를 등록한다. 스키마는 `id`(문자열)와 `payload`(객체)만 허용하고 둘 다 필수다. `git_init(self.root/"repository")`로 만든 저장소에 그 계약으로 `ResearchRepository`를 연다. `current_state`에 `unicode_fixture: {"UF-1": record}`를 더해 `initialize`한다. `record`의 `payload`는 첫 테스트와 같은 NFD 문자열과 두 K 키를 담는다.
- 실행: `repository.load(head)`, `repository.read_record("UF-1", head)`.
- 단언: 적재된 `instance["unicode_fixture"]["UF-1"]`이 `record`와 같다. `read_record`가 돌려준 `bytes`를 `json.loads`한 봉투의 `record` 필드도 `record`와 같다.
- 대역: 없음.
- 비고: 실제 Git 저장소를 쓴다. `git_init`은 프로세스당 한 번 `git init` 자식 프로세스로 만든 모형의 `.git`을 복사한다(`research_fixtures.py` 행 945–960). 저장소 객체는 제품이 프로세스 안에서 쓰지만, 참조 이동(`update-ref`)과 읽기(`cat-file`)는 Git 자식 프로세스로 돈다(`git_store.py` 행 370의 주석, 행 328, 146–186). 시험용 가족을 기본 계약이 아니라 새 계약에 등록하는 이유는 `installed_contract`의 docstring에 있다. 저장소들이 공유하는 `default_state_contract()`에는 가족이 더해지지 않는다.

### `test_record_envelope_with_an_unknown_field_is_rejected_without_conversion` (행 65–80)
- 성질: 레코드 봉투에 알 수 없는 필드가 끼면 적재가 그것을 버리거나 바꾸지 않고 거부한다.
- 준비: 앞 테스트처럼 새 계약에 `unicode_fixture`를 등록한다. 이번 스키마는 `id`와 `text`(문자열)만 허용한다. `UL-1` 레코드(`text="e\u0301"`)로 `initialize`한다.
- 실행: `read_record("UL-1", head)`로 저장된 봉투를 읽어 `unexpected_field: True`를 더한다. `canonical_json`으로 다시 직렬화한 바이트를 제품 저장소 내부의 `repository._store.publish(head, {경로: 바이트})`로 같은 경로에 새 커밋으로 발행한다. 그 커밋으로 `repository.load(corrupt)`를 부른다.
- 단언: `ValueError`를 정규식 `"invalid record envelope"`로 던진다. 거부 사유는 메시지 조각까지 고정된다.
- 대역: 없음. 다만 `ResearchRepository`의 검증을 거치지 않도록 내부 `_store.publish`로 손상 바이트를 직접 써 넣는다.
- 비고: 이름의 "without conversion"은 원문에 풀이가 없다. 단언은 적재가 `"invalid record envelope"`로 거부한다는 것만 확인한다. 알 수 없는 필드를 버리거나 NFD 문자열을 바꾼 채 적재하지 않는다는 것은 거부가 났다는 사실로만 드러난다. 손상에 쓴 레코드는 NFD 문자열 `text`를 담는다. 적재에서 이 봉투를 먼저 거부하는 곳은 `payloads.decode`의 필드 집합 검사다(`payloads.py` 행 139–140, 메시지 `invalid record envelope fields`). 앞 테스트처럼 실제 Git 저장소와 Git 자식 프로세스를 쓴다.

### `test_source_catalog_and_direct_input_hash_exact_bytes` (행 82–95)
- 성질: 역할 문맥 저장의 원천 카탈로그와 직접 입력 목록은 유니코드 값의 정확한 정규 JSON 바이트를 해시한다.
- 준비: 첫 테스트와 같은 값. 새 임시 폴더를 작업 공간으로 쓴다.
- 실행: `write_source_catalog({"proposal": value}, workspace)`로 카탈로그를 쓴다. 그 `entries["proposal"]` 참조로 `read_source(workspace, source_ref, limit=1_000_000)`를 부른다. `build_role_manifest({"proposal": value}, workspace=..., role="research_work", direct_keys=["proposal"], reference_keys=[])`로 역할 목록을 만든다.
- 단언: 읽은 원천의 `bytes`가 `canonical_json(value)`와 같다. 되읽으면 원래 값과 같다. 카탈로그 참조의 `sha256`과 목록의 `direct[0]["sha256"]`이 둘 다 그 바이트의 SHA-256 16진수와 같다.
- 대역: 없음.

## 관계

- `canonical_json`의 다른 성질(부동소수 거부, 정수 영역, 값 영역과 직렬화의 일치)은 `test_repository`의 `StorageValueTests`가 검사한다. 그 가운데 `test_value_validation_and_serialization_keep_the_same_domain`(행 454–471)은 서로게이트 값 `'\ud800'`과 키 `'\udfff'`의 거부도 단언하므로, 이 모듈의 `test_exact_json_preserves_scalars_and_rejects_surrogates`와 겹친다. 이 모듈은 코드 포인트 보존을 더 넓은 표본(스칼라 경계, 서로게이트 쌍, 켈빈 키, NFD 대 NFC)으로 검사한다.
- Git 경로 이름의 유니코드 보존은 `test_git_store`의 `test_unicode_artifact_path_preserves_the_supplied_code_points`가 검사한다. 이 모듈은 레코드 내용만 다룬다.
- 원천 카탈로그와 역할 목록의 다른 성질(크기, 해시, 넘침)은 `test_context_store`가 검사한다.
- 픽스처 의존: `research_fixtures.current_state`, `git_init`, `installed_contract`.
- 이 모듈에만 있는 도우미는 없다.
