# test_cli_surface

| 항목 | 값 |
|---|---|
| 조각 | `foundation` |
| 원문 | `.claude/skills/do-math/scripts/tests/test_cli_surface.py` (57행) |
| 클래스 / 테스트 | 1 / 2 |
| 시험 대상 제품 코드 | `do_math/cli.py`의 `build_parser`, `execute`, `_json_arguments`, `_require_git`, `_Parser.error`(`CliInputError`); `do_math/repository.py`의 `ResearchRepository.initialize`, `list_files`, `new_id` |
| 사용하는 픽스처 모듈 | `research_fixtures`: `current_state`, `git_init` |
| 격리 표지 | 없음 |
| 시작 상태 | 첫 테스트는 `git_init`으로 만든 빈 저장소에 `current_state`의 최소 상태를 직접 `initialize`한다(네 단 밖: 저장소 계층 직접 초기화). 둘째 테스트는 1단(파서와 JSON 요청 변환기 직접 호출) |

## 목적

모듈 docstring은 "명령행 표면: 인자와 JSON 요청은 어떤 효과보다 먼저 검증되고, 읽기는 자기 스냅숏을 이름으로 밝힌다"고 요약한다. 두 성질을 한 테스트씩 검사한다. 하나는 `query --files`와 `read` 명령이 결과에 해석된 스냅숏(커밋)을 출처로 싣는다는 것이다. 다른 하나는 알 수 없는 `init` 옵션이 argv 경로와 JSON 요청 경로 모두에서 Git 확인(`_require_git`)이나 파일 생성보다 먼저 거부된다는 것이다. 제품 좌표는 `cli.py`의 `build_parser`(행 82), `execute`(행 275), `_json_arguments`(행 541), `_require_git`(행 64)이다. `_Parser.error`(행 37–39)는 argparse 오류를 `CliInputError`(`ValueError`의 하위 클래스, 행 33)로 바꾼다.

## 모듈 수준 요소

- 행 8: 스킬의 `scripts/` 폴더를 `sys.path` 맨 앞에 넣는다. 다른 모듈처럼 `SCRIPTS` 이름을 두지 않고 존재 여부도 확인하지 않은 채 바로 넣는다.
- 행 9–11: `do_math.cli`를 모듈로 import한다. 둘째 테스트가 `patch.object(cli, '_require_git')`로 이 모듈 속성을 바꾸기 위해서다.
- 행 56–57: 직접 실행하면 `unittest.main()`으로 이 모듈의 시험을 돈다.

## CliSurfaceTests (행 14–53)

`unittest.TestCase`를 그대로 상속한다. 표지, 클래스 속성, 설정 훅, 도우미가 없다. 각 테스트는 `tempfile.TemporaryDirectory`를 스스로 연다.

### `test_file_query_and_read_include_resolved_snapshot_provenance` (행 15–37)
- 성질: CLI의 파일 질의와 파일 읽기는 결과에 자기가 읽은 스냅숏을 싣는다.
- 준비: 임시 폴더를 `git_init`으로 빈 Git 저장소로 만들고, `new_id("RI")`로 새 인스턴스 ID를 뽑는다. `ResearchRepository(root, identifier).initialize`에 `current_state`의 최소 상태를 넘긴다. instance에는 `id`, 빈 `sources`·`knowledge`·`trust_environments`를, runtime에는 빈 `tasks`·`executions`·`queue`·`question_links`와 `status="ready"`를 더한다. 반환된 커밋이 `head`다. 엔진 활성화 없이 저장소 계층으로 첫 스냅숏만 만든다.
- 실행: `build_parser()`의 파서로 `query --repository <root> --instance <id> --files --prefix research/ --limit 1`을 해석하고 `execute`에 넘긴다. 이어서 `store.list_files("research/", head)`의 첫 경로로 `read --repository ... --instance ... --path <path>`를 실행한다. 두 명령 모두 자식 프로세스 없이 같은 프로세스에서 `execute`를 직접 부른다.
- 단언: 두 호출의 종료 코드가 0이다. 질의 결과의 `provenance.snapshot`이 `head`이고 `provenance.filters.prefix`가 `"research/"`다. 읽기 결과의 `snapshot`이 `head`이고, `sha256`의 길이가 64다(값 자체는 비교하지 않는다).
- 대역: 없음.
- 비고: 행 16–17의 주석은 "CLI가 ENGINE을 import하므로, 이 경계 시험은 동시에 진행되는 엔진·관찰 구현 작업과 독립으로 둔다"고 밝힌다. 주석은 함수 안의 `build_parser`·`execute` import 바로 앞에 있다. 다만 모듈 행 9가 이미 `do_math.cli`를 모듈 수준에서 import하므로, 함수 안의 import는 이 모듈이 적재될 때 엔진을 import하지 않게 막지 못한다. `git_init`은 프로세스마다 `git init`을 한 번 돌리고 그 뒤로는 `.git`을 복사한다. `ResearchRepository`의 쓰기와 읽기는 실제 Git 저장소를 쓴다.

### `test_unknown_init_option_has_no_repository_or_workspace_effect` (행 39–53)
- 성질: 알 수 없는 `init` 옵션은 argv 경로와 JSON 요청 경로 모두에서 Git 확인이나 파일 효과가 생기기 전에 거부된다.
- 준비: 빈 임시 폴더. 저장소와 작업 공간 경로는 그 아래의 `repo`와 `work`로, 아직 없는 경로다.
- 실행: (1) `cli.build_parser().parse_args`에 `init --repository ... --workspace ... --goal 'Compare methods' --invented-option value`를 준다. (2) `schema_version=5`, `command='init'`, payload에 `repository`·`workspace`·`goal`과 알 수 없는 키 `invented_option`을 담은 요청을 `cli._json_arguments(cli.build_parser(), request)`에 준다.
- 단언: (1)은 `ValueError`를 정규식 `'unrecognized'`로 던진다. 곧 argparse의 "unrecognized arguments" 메시지를 `_Parser.error`가 `CliInputError`로 바꾼 것을 확인한다. `_require_git` 대역은 불리지 않았다(`assert_not_called`). 임시 폴더는 여전히 비어 있다. (2)는 `ValueError`를 정규식 `'unknown|unrecognized|unexpected'`로 던지고, 여기서도 `_require_git`은 불리지 않았다. 두 번째 경우의 정규식은 세 낱말 가운데 하나만 요구하므로 거부된 단계를 고정하지 않는다. 제품의 `_json_arguments`는 요청 스키마(`WIRE_VERSION=5`) 검사 뒤 명령별 `payload_schema` 검사에서 `"invalid command payload: ..."`를 낸다. jsonschema의 추가 속성 메시지에는 "unexpected"가 들어간다.
- 대역: `patch.object(cli, '_require_git')` 두 번. 실제 `git -C ... rev-parse`나 `git init` 자식 프로세스가 돌지 않게 막는 동시에 호출 여부를 기록한다.
- 비고: 빈 폴더 단언은 (1) 뒤에만 한다. (2) 뒤에는 파일 효과를 다시 확인하지 않는다. 다만 `_json_arguments`는 argv로 바꿔 `parse_args`를 부르는 데까지만 가고 명령을 실행하지 않는다.

## 관계

- 같은 CLI 표면을 더 넓게 검사하는 모듈은 `test_cli`, `test_cli_advanced`다. 이 모듈은 두 경계 성질만 본다. 스냅숏에 묶인 파일 질의 커서는 `test_repository`의 `test_query_cursor_is_bound_to_snapshot_and_query_and_has_no_empty_page`가 저장소 계층에서, `test_query_records`가 엔진 질의 함수 층에서 검사한다.
- 픽스처 의존: `research_fixtures.current_state`(최소 유효 상태), `git_init`(프로세스 안 `git init` 대체).
- 이 모듈에만 있는 도우미는 없다.
- 이 모듈은 `run_cli`를 쓰지 않는다. 첫 테스트는 `execute`를, 둘째 테스트는 `build_parser`와 `_json_arguments`를 직접 부른다. 그래서 JSON 봉투, 오류 종류별 종료 코드(`ERROR_EXIT_CODES`), 표준 출력 인코딩은 이 모듈의 검사 대상이 아니다.
