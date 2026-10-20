# test_payloads

| 항목 | 값 |
|---|---|
| 조각 | `foundation` |
| 원문 | `.claude/skills/do-math/scripts/tests/test_payloads.py` (125행) |
| 클래스 / 테스트 | 4 / 6 |
| 시험 대상 제품 코드 | `do_math/payloads.py`의 `seal_large`, `encode`, `decode`, `LIMIT`(65536); `do_math/repository.py`의 `ResearchRepository`(`initialize`, `load`, `save_with_state`, `validate_candidate`, `_publish_candidate`, `read`, `read_many`, `list_files`), `canonical_json`, `new_id` |
| 사용하는 픽스처 모듈 | `research_fixtures`: `current_state`, `git_init`, `installed_contract` |
| 격리 표지 | 없음 |
| 시작 상태 | `PayloadCodecTests`, `PayloadEncodingTests`: 1단(코덱 순수 함수). `PayloadPublicationTests`, `PayloadStorageTests`: 네 단 밖. `git_init`으로 만든 실제 Git 저장소 위의 `ResearchRepository`에 `current_state`의 최소 상태를 발행한다 |

## 목적

모듈 docstring은 이 모듈이 세 가지를 검사한다고 밝힌다. 페이로드 참조의 정준 순서, 블롭 재사용, 발행 전 충돌 거부다. 제품 `payloads.py`는 큰 문자열(`LIMIT // 6` 글자 이상이고 정준 JSON이 `LIMIT`=65536바이트 이상)을 봉인해 `runtime/artifacts/payload-<sha256>/value.json` 블롭으로 떼어 내고, 레코드에는 `None` 자리와 `payloads` 참조 목록을 남긴다(docstring "Content-addressed immutable large JSON leaves, with exact logical values."). `decode`는 블롭 바이트를 digest와 대조하고, 정준 인코딩을 다시 만들어 원 봉투와 같은지 확인한다. 이 모듈은 코덱의 정확성과 공유, 그리고 저장소 발행 경계에서 블롭 불변성을 검사한다.

## 모듈 수준 요소

- 행 8: 스킬의 `scripts/` 폴더를 `sys.path` 앞에 넣는 공통 머리다.
- 행 9–15: `ResearchRepository`, `new_id`, `canonical_json`과 코덱 함수 `decode`, `encode`, `seal_large`, 모듈 `payloads`, `deepcopy`, `patch`, 그리고 픽스처 `current_state`, `git_init`, `installed_contract`를 import한다.
- 행 124–125: 직접 실행하면 `unittest.main()`으로 이 모듈의 시험을 돈다.

## PayloadCodecTests (행 17–23)

`unittest.TestCase`를 그대로 상속하고 훅과 도우미가 없다.

### `test_multiple_payload_references_follow_canonical_key_order` (행 18–23)
- 성질: 한 레코드에 페이로드가 여럿이면 참조 목록은 정준 키 순서를 따르고, 정준 JSON을 거친 봉투도 원 값으로 복원된다.
- 준비: 1단. `{'z': 'z'*70000, 'a': 'a'*70000}`을 `seal_large`로 봉인해 `contract_id`와 `family`가 `'test'`인 봉투의 `record`로 둔다.
- 실행: `encode(봉투)`로 봉투와 블롭을 얻고, 봉투를 `canonical_json`으로 직렬화했다가 `json.loads`로 되읽는다. 그 결과를 `decode(stored, lambda path: blobs[path])`로 복원한다.
- 단언: `stored['payloads']`의 `tokens` 목록이 `[['a'], ['z']]`다. 삽입 순서는 `z`가 먼저지만 `encode`가 키를 정렬해 방문하므로 `a`가 앞선다. 복원값이 원 값과 같다.
- 대역: 없음. 블롭 읽기는 사전 조회 람다다.

## PayloadPublicationTests (행 26–72)

`unittest.TestCase`를 그대로 상속한다. `setUp` (행 27–33)은 임시 폴더를 만들어 정리를 등록하고, `git_init(root)`로 빈 Git 저장소를 복사해 둔다. 이어서 `ResearchRepository(root, new_id('RI'))`를 만들고, `initialize(*current_state({'title': 'initial'}))`로 첫 상태를 발행해 `self.head`에 둔다. `current_state`는 상태 계약이 받는 가장 작은 `(instance, runtime)`에 호출자의 필드를 더한다. 저장소 쓰기와 읽기는 `git_store`의 Git 자식 프로세스를 통한다.

### `test_unreferenced_payload_can_be_reused_without_rewriting_the_blob` (행 35–48)
- 성질: 한때 쓰이다 참조가 끊긴 페이로드 블롭은, 같은 값이 다시 저장될 때 다시 쓰이지 않고 같은 바이트로 재사용된다.
- 준비: `setUp`의 저장소. 값은 `'exact 원문\n' * 20000`이다.
- 실행: 세 번 저장한다. (1) `title`을 큰 값으로 바꿔 `save_with_state`로 발행하고, 그 head의 `runtime/artifacts/payload-` 경로들과 바이트(`read_many`)를 기록한다. (2) `title`을 `'short'`로 바꿔 발행한다. 이 시점에 블롭은 트리에 남지만 참조되지 않는다. (3) `title`을 다시 큰 값으로 바꿔 발행한다.
- 단언: 마지막 head를 `load`하면 `title`이 큰 값과 같다. 같은 경로들의 바이트가 (1)의 바이트와 같다.
- 대역: 없음. 실제 Git 저장소다.
- 비고: 제품 근거는 `repository._publish_candidate`의 주석이다: "Unreferenced payloads remain immutable Git blobs. They are reusable even when the parent decoder did not need to read them into old_files." 이 분기는 트리에 있으나 부모 디코딩에서 읽지 않은 artifact를 읽어 대조한다.

### `test_payload_collision_is_rejected_by_validation_and_publication_before_cas` (행 50–59)
- 성질: 인코딩된 상태의 페이로드 경로에 다른 바이트를 artifact로 넘기면, 검증 경계와 발행 경계 모두에서 거부되고 참조(ref)는 움직이지 않는다.
- 준비: `setUp`의 저장소에서 `title`을 `'new exact 원문\n' * 20000`으로 바꾼다. `validate_candidate`로 후보를 만들어 그 `files`에서 `runtime/artifacts/`로 시작하는 첫 경로를 고른다.
- 실행: 두 경계에 `artifacts={path: b'different bytes'}`를 넘긴다. 하나는 `self.repo.validate_candidate`이고, 다른 하나는 `save_with_state(h, i, r, **kw)`로 감싼 람다다.
- 단언: 두 경우 모두 `ValueError`이고 메시지가 정규식 `'artifact.*differs|collision'`에 맞는다. 제품에서 걸리는 문구는 `validate_candidate`의 "immutable artifact differs from encoded state: <path>"다. 끝으로 `self.repo._store.read_snapshot().head`가 `self.head`와 같다. 곧 비교 후 교체(CAS) 발행에 이르기 전에 거부되었다.
- 대역: 없음.
- 비고: `subTest(boundary=...)`의 두 케이스는 위의 두 경계다.

### `test_matching_payload_and_separate_artifact_publish_exact_validated_bytes` (행 61–72)
- 성질: 인코딩과 같은 바이트의 페이로드 artifact와 별도 artifact는 함께 발행되고, 발행된 뒤에는 그 페이로드 바이트를 바꿀 수 없다.
- 준비: 앞 테스트와 같이 큰 `title`의 후보를 만들어 페이로드 경로 `path`와 그 바이트 `raw`를 얻는다.
- 실행: `save_with_state(self.head, instance, runtime, artifacts={path: raw, 'runtime/artifacts/BA-new/result.txt': b'result'})`로 발행한다. 이어서 새 head에서 `artifacts={path: b'changed'}`로 다시 저장을 시도한다.
- 단언: `load(head)`가 발행이 돌려준 `(head, normalized, saved)`와 같다. `read(path, head)`가 `raw`와 같다. 두 번째 저장은 `ValueError`이고 메시지가 `'immutable'`을 포함한다(정규식). 제품에서 이 문구를 가진 거부는 `validate_candidate`의 "immutable artifact differs from encoded state"와 `git_store`의 "existing runtime artifact bundles are immutable" 둘이다. 테스트는 둘 가운데 어느 것인지 고정하지 않는다.
- 대역: 없음.

## PayloadEncodingTests (행 75–90)

`unittest.TestCase`를 그대로 상속하고 훅과 도우미가 없다.

### `test_payloads_are_exact_shared_and_immutable` (행 76–90)
- 성질: 같은 큰 문자열이 한 레코드의 두 자리에 있으면 블롭은 하나만 만들어지고, 봉투는 작게 유지되며, 복원하면 두 자리가 같은 불변 객체를 공유하고, digest를 바꾼 참조는 거부된다.
- 준비: 1단. `text = '원문 코드포인트\n' * 20000`을 `{'title': text, 'source': {'text': text}}`의 두 자리에 두고 `payloads.seal_large`로 봉인한다.
- 실행: `payloads.encode(봉투)`로 봉투와 블롭을 얻는다. 블롭 사전을 읽는 함수 `read`에 `decoded={}` 속성을 달아 `payloads.decode(encoded, read)`로 복원한다. 이어서 첫 참조의 `sha256`을 `'0'*64`로 바꾼 사본을 다시 `decode`한다.
- 단언: 블롭이 1개다. 경로가 digest로 정해지므로 두 참조가 같은 경로를 쓴다. `canonical_json(encoded)`가 1500바이트 미만이다. 복원값이 봉인값과 같다. `restored['title'] is restored['source']['text']`가 참이다(실패 메시지 "one immutable value should be shared"). `decode`는 `read.decoded` 캐시에 `(path, sha256, bytes)`마다 봉인 객체 하나를 두고 재사용한다. 변조한 사본은 `ValueError`를 던진다. 예외 유형만 확인한다. 제품에서는 참조의 `path`가 바뀐 `sha256`과 맞지 않아 "invalid immutable payload reference"로 먼저 거부된다. 바이트 해시 대조까지 가지 않는다.
- 대역: 없음.

## PayloadStorageTests (행 93–121)

`unittest.TestCase`를 그대로 상속하고 훅과 도우미가 없다.

### `test_large_payload_storage_and_cached_parent_remain_exact` (행 94–121)
- 성질: 큰 값을 가진 두 가족의 레코드가 저장소에 하나의 블롭으로 떼어져 저장되고, 새 저장소 객체의 디코딩도 한 값을 공유하며, 같은 객체가 발행한 부모 head는 다시 읽지 않고, 호출자의 변경은 발행된 상태를 오염시키지 않는다.
- 준비: 네 단 밖. 임시 폴더에 `git_init`을 하고 `new_id('RI')`로 식별자를 만든다. 도우미 클로저 `labelled()`는 `installed_contract()`에 `register_family('research', 'label', shape='metadata', schema={'type': 'string'}, identity=False)`를 더한 새 계약을 만든다. 이 계약으로 `ResearchRepository`를 만들고, `text = 'exact 원문\n' * 20000`을 `title`과 `label` 둘 다에 둔 `current_state`로 `initialize`한다.
- 실행: 여러 단계를 차례로 밟는다.
  1. head의 `research/_state/metadata.json`을 읽는다.
  2. 같은 저장소 객체로 `load(head)`를 부른다.
  3. 같은 계약으로 새 저장소 객체 `reader`를 만들어 `load(head)`를 부른다.
  4. `repo._store.read_many`를 `wraps`로 감싼 채 `save_with_state(head, instance, {**runtime, 'status': 'ready'})`로 발행한다.
  5. 새 head를 `load`한다.
  6. `instance['title']`을 `'caller mutation'`으로 바꾼 뒤 옛 head를 다시 `load`한다.
  7. 두 head에서 페이로드 경로의 바이트를 읽는다.
- 단언:
  - 저장된 `record.title`은 `None`이다.
  - `payloads`의 서로 다른 `path`는 1개다. `title`과 `label`이 같은 블롭을 쓴다.
  - 적재한 `instance['title']`이 `text`다.
  - `reader`의 복원값에서 `decoded['title'] is decoded['label']`이 참이다(실패 메시지 "decoded values should share immutable bytes"). 행 111의 주석은 이것이 이 저장소 객체가 발행하지 않은 head의 디코딩임을 밝힌다.
  - 감싼 `read_many` 호출 가운데 첫 인자가 `head`인 것이 0개다. 곧 저장소 객체가 발행해 기억한 부모는 다시 읽지 않았다.
  - `load(new_head)`가 발행 결과 세 값과 같다.
  - 호출자가 `instance`를 바꾼 뒤에도 `load(head)[1]['title']`은 `text`다.
  - 두 head에서 읽은 페이로드 바이트가 같다.
- 대역: `patch.object(repo._store, 'read_many', wraps=...)`. 동작은 그대로 두고 호출을 기록한다.

## 관계

- 같은 제품 기능의 다른 층: 페이로드는 `repository`의 저장 경로 전체에 걸쳐 있다. 저장소 발행, 부모 캐시, artifact 증거는 `test_repository`, `test_git_store` 같은 저장 모듈도 다룬다. 이 모듈은 큰 값의 외부화와 그 블롭 불변성에 집중한다.
- 픽스처 의존: `research_fixtures`의 `current_state`(최소 상태), `git_init`(빈 Git 저장소 복사), `installed_contract`(설치 가족을 담은 새 `StateContract`).
- 이 모듈에만 있는 도우미: `test_large_payload_storage_and_cached_parent_remain_exact` 안의 지역 함수 `labelled()`.
- 겹치거나 보완하는 시험: 공유 성질은 두 층에서 확인된다. `test_payloads_are_exact_shared_and_immutable`은 코덱 수준에서, `test_large_payload_storage_and_cached_parent_remain_exact`는 저장소 적재 수준에서 본다. 충돌 거부는 `test_payload_collision_is_rejected_by_validation_and_publication_before_cas`가 발행 전을, `test_matching_payload_and_separate_artifact_publish_exact_validated_bytes`가 발행 후 불변성을 본다.
