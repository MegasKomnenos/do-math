# test_installation_discovery

| 항목 | 값 |
|---|---|
| 조각 | `foundation` |
| 원문 | `.claude/skills/do-math/scripts/tests/test_installation_discovery.py` (85행) |
| 클래스 / 테스트 | 1 / 4 |
| 시험 대상 제품 코드 | `do_math/engine.py`의 `ResearchEngine._available_inputs`, `_lean_discovered`, `ResearchEngine._installation_manifest`(정적 메서드), 모듈 함수 `_installation_listing`과 모듈 전역 `_HASHED_INSTALLATION`; `do_math/file_io.py`의 `cached_sha256`, `RACY_NS`, `fingerprint_settled` |
| 사용하는 픽스처 모듈 | `research_fixtures`: `bare_engine` |
| 격리 표지 | 없음 |
| 시작 상태 | 1단. 첫 시험은 `bare_engine` 위에 손으로 만든 최소 상태를 두고, 나머지는 설치본이나 임시 폴더를 직접 읽는다 |

## 목적

모듈 docstring은 "Discovery of the host installation: the Lean executable and the installed skill files whose hashes name the edition."이다. 엔진은 호스트에서 두 가지를 주기적으로 발견한다. 하나는 로컬 Lean 실행 파일이고, 다른 하나는 판본(edition)을 이루는 설치 파일의 해시다. 이 모듈은 두 발견이 반복 호출에서 비싼 일을 되풀이하지 않는다는 성질을 검사한다. Lean은 1초에 한 번까지만 다시 찾는다. 설치 해시는 바뀌지 않은 파일을 다시 해시하지 않고, 디렉터리 목록이 그대로면 역할 지도(`reading_map`)조차 다시 읽지 않는다. 목록은 추가, 삭제, 같은 크기의 재작성을 드러내야 한다.

제품 좌표는 다음과 같다. `_lean_discovered`(engine.py 행 2374–2380)는 "Rediscover the local Lean at most once per second, the installation-check period."다. `_installation_manifest`(행 492–519)의 docstring은 마지막으로 해시한 판본의 디렉터리 목록이 같으면 역할 지도, glob, 해시 없이 그 판본을 돌려준다고 밝힌다. `_installation_listing`(행 107–137)은 `scripts/do_math` 아래의 모든 `.py`와 목록에 오른 문서의 `(size, modification, birth)` 지문을 `scandir` 한 번으로 모은다.

## 모듈 수준 요소

- 행 7: 스킬의 `scripts/` 폴더를 `sys.path` 앞에 넣는다.
- 행 8–9: `from do_math import engine as engine_module`, `from research_fixtures import bare_engine`.
- 행 84–85: 직접 실행하면 `unittest.main()`을 부른다.

## ToolDiscoveryTests (행 12–81)

`unittest.TestCase`를 그대로 상속한다. 표지, 클래스 속성, 설정 훅, 도우미가 없다.

### `test_lean_is_rediscovered_at_most_once_per_second` (행 13–27)
- 성질: 역할 입력마다 호스트 입력 참조를 파생하더라도, Lean 탐색은 단조 시계로 1초에 한 번까지만 다시 돈다. 1초가 지나면 탐색 결과의 변화(사라짐)가 반영된다.
- 준비: `bare_engine()`에 `instance={'config': {'scholarly_enabled': False, 'scholarly_server': None}, 'knowledge': {}, 'sources': []}`, `runtime={'tasks': {}}`를 둔다. 설정에 `lean_command`가 없으므로 Lean 가용성은 탐색에만 달린다. 시계 값은 목록 `clock=[100.0]`으로 둔다.
- 실행: `engine._available_inputs()`를 다섯 번 부른다. 이어서 탐색 결과를 `None`으로 바꾸고 시계를 1.0초 앞당긴 뒤 한 번 더 부른다.
- 단언: 처음 다섯 번은 모두 결과에 `'tool:lean'`이 있고, 탐색 함수 호출 수가 1이다. 여섯 번째에는 `'tool:lean'`이 없고, 호출 수가 2다.
- 대역: `patch.object(engine_module, 'discover_lean', return_value=['lean'])`, `patch.object(engine_module.time, 'monotonic', side_effect=lambda: clock[0])`.
- 비고: 제품은 `current >= self._next_lean_discovery`일 때 다시 찾고, 다음 시각을 `current + 1.0`으로 둔다. 따라서 정확히 1.0초 뒤의 호출이 재탐색 경계다. 이 시험은 그 경계값을 쓴다.

### `test_periodic_installation_check_rehashes_no_unchanged_file` (행 29–37)
- 성질: 목록 지름길을 쓰지 않는 전체 경로에서도, 지문이 바뀌지 않은 파일은 다시 해시하지 않는다.
- 준비: `file_io.RACY_NS`를 0으로 패치한다. 원문 주석(행 31)은 "Freshly edited files are not yet settled; age every fingerprint for this check."라고 밝힌다. 방금 고친 파일도 안정된 것으로 취급하게 해 `cached_sha256`의 캐시가 채워지게 한다. 이 상태에서 실제 설치본에 `_installation_manifest()`를 한 번 불러 기준값을 얻는다.
- 실행: `_HASHED_INSTALLATION`을 `None`으로 패치해 목록 지름길을 끈 채(주석 행 34 "Forget the hashed edition so the full walk runs, not the listing shortcut.") `_installation_manifest()`를 다시 부른다.
- 단언: 결과가 기준값과 같다. 이 호출 동안 `file_io.sha256_file`은 부르면 `AssertionError('unchanged file was rehashed')`를 던지도록 패치되어 있다. 따라서 결과가 나왔다는 것은 모든 파일이 `cached_sha256`의 지문 캐시에서 나왔다는 뜻이다.
- 대역: `patch.object(file_io, 'RACY_NS', 0)`, `patch.object(engine_module, '_HASHED_INSTALLATION', None)`, `patch.object(file_io, 'sha256_file', side_effect=AssertionError(...))`.
- 비고: 실제 설치된 스킬 폴더(`_SKILL_ROOT`)를 읽는다. 기준값을 얻는 첫 호출은 `_HASHED_INSTALLATION` 패치 밖에서 돌므로, 프로세스의 실제 전역을 채울 수 있다.

### `test_unchanged_installation_listing_reuses_the_hashed_edition` (행 39–50)
- 성질: 마지막으로 해시한 판본의 목록이 그대로면 역할 지도를 다시 읽지 않고 그 판본 객체를 그대로 돌려준다. 목록이 달라지면 역할 지도를 한 번 다시 읽어 판본을 다시 만든다.
- 준비: `RACY_NS=0`, `_HASHED_INSTALLATION=None`으로 패치하고 `_installation_manifest()`를 불러 기준값을 얻는다. 이 호출이 패치된 전역에 `(documents, listing, manifest)`를 저장한다.
- 실행: (1) `reading_map`을 부르면 `AssertionError('role map reread')`를 던지게 한 채 다시 부른다. (2) 저장된 목록에 가짜 항목 `'scripts/do_math/added.py': (1, 1, 1)`을 더한 `changed`를 만든다. `_installation_listing`이 처음에는 `changed`를, 두 번째에는 원래 목록을 돌려주게 하고, `reading_map`은 실제 함수를 감싼 대역으로 둔 채 다시 부른다.
- 단언: (1)의 결과는 기준값과 같은 객체다(`assertIs`). (2)의 결과는 기준값과 같은 값이고(`assertEqual`), `reading_map` 호출 수가 1이다.
- 대역: `patch.object(engine_module, 'reading_map', side_effect=AssertionError(...))`, `patch.object(engine_module, '_installation_listing', side_effect=[changed, listing])`, `patch.object(engine_module, 'reading_map', wraps=engine_module.reading_map)`.
- 비고: (2)는 목록 불일치 뒤 제품이 역할 지도 읽기, 목록 재취득, 파일 해시의 전체 경로로 들어가는지를 본다. 가짜 항목은 실제 파일이 아니므로 전체 경로의 결과는 기준값과 같다.

### `test_installation_listing_reports_added_removed_and_rewritten_files` (행 52–81)
- 성질: 설치 목록은 `scripts/do_math` 아래 `.py`와 지정 문서만 담는다. 해시 대상이 아닌 파일은 목록을 움직이지 않는다. 추가, 삭제, 같은 크기의 재작성은 목록에 드러난다.
- 준비: 임시 루트에 `scripts/do_math/a.py`, `scripts/do_math/sub/b.py`, `docs/x.md`, `SKILL.md`를 `'v1'`로 쓴다. 문서 목록은 `('SKILL.md', 'docs/x.md')`다.
- 실행: 단계마다 `engine_module._installation_listing(root, documents)`를 부른다. (1) 처음 목록. (2) `__pycache__/a.cpython-312.pyc`와 목록에 없는 `docs/unlisted.md`를 만든 뒤. (3) 새 하위 폴더에 `new/c.py`를 만든 뒤. (4) `new/c.py`와 `sub/b.py`를 지운 뒤. (5) `docs/x.md`와 `scripts/do_math/a.py`를 각각 같은 크기의 `'v2'`로 다시 쓰고 수정 시각을 이전 값보다 1초 뒤로 설정한 뒤.
- 단언: (1)의 키 집합이 네 파일과 같다. (2)의 목록이 (1)과 같다. (3)에서 새로 생긴 키가 `scripts/do_math/new/c.py` 하나다. (4)에서 사라진 키가 `scripts/do_math/sub/b.py` 하나다. (5)에서 두 파일의 지문이 이전 값과 다르다(`subTest`가 아닌 반복문이며, 실패 메시지에 상대 경로를 싣는다).
- 대역: 없음.
- 비고: 원문 주석(행 79)은 "same size: only the time moves"라고 밝힌다. 수정 시각을 명시적으로 옮기는 이유는 Windows 파일 시각의 분해능 안에서 같은 크기의 재작성이 같은 지문을 가질 수 있기 때문이다(`file_io.py` 행 172–176의 racy-git 주석).

## 관계

- 설치 판본의 해시를 쓰는 다른 경로, 곧 수리 실행의 설치 정체성 `repair_execution.installation_sha256`은 `test_repair_execution.InstallationIdentityTests`가 검사한다. 그 함수는 `file_io.installation_files`로 스킬 전체(시험 제외)를 해시한다. 이 모듈의 `_installation_manifest`는 `scripts/do_math`의 `.py`와 역할·운영 문서만 해시한다. 두 정체성은 대상 집합이 다르다.
- `discover_lean`을 부르는 시험 모듈은 이 모듈 밖에서는 `test_standalone`(얕은 설치에서 `None`) 하나뿐이다. `test_formal`, `test_knowledge`, `provider_fixtures`는 `portable_bin(toolchain_root())`로 Lean 경로를 직접 만들 뿐 `discover_lean`의 탐색 순서(준비 표지가 있는 Mathlib 프로젝트, PATH, 휴대용 `lean.exe`)를 검사하지 않는다.
- `research_fixtures.bare_engine`은 첫 시험에서만 쓴다. 저장소 없이 엔진의 프로세스 지역 상태(`_next_lean_discovery`, `_lean_found`)만 초기화한 엔진을 준다.
