# 정확 snapshot의 payload 읽기 묶기

R7.3의 저장 복원 경로를 수정했다. `ResearchRepository._read_documents`는 비artifact 파일을 이미 한 번에 읽었지만, 그 뒤 각 고유 payload와 snapshot 노드를 `GitStateStore.read_bytes`로 따로 읽었다. `GitStateStore.read_many(commit, paths)`와 `GitProcess.read_objects`는 이미 정확 commit의 여러 blob을 한 `git cat-file --batch` 프로세스로 읽고 바이너리 길이로 응답을 해석하므로, 새 Git 포트나 상주 프로세스 없이 이 경로를 재사용했다.

## 구현과 보존한 의미

정본 파일은 `.claude/skills/do-math/scripts/do_math/repository.py`와 `payloads.py`다.

- `_read_documents`의 읽기 콜백은 같은 명시적 `head`에서 누락된 경로를 최대 64개씩 `read_many`로 읽는다. 이 복원 안에서는 같은 경로의 bytes를 한 번만 읽는다.
- `_decode_families`는 엄격 JSON으로 읽은 문서를 재사용하고 `payloads.prefetch`에 봉투들을 전달한다. 최상위 payload 참조를 먼저 모으고, 구조 snapshot은 검증한 부모에서 확인된 자식 집합을 차례로 읽는다. 다른 artifact와 과거의 미참조 payload/snapshot을 전부 읽지 않는다.
- `payloads._references`, `_snapshot_node`, `_snapshot_cell`은 기존 decode의 참조·노드·셀 규칙을 추출한 공통 정의다. 선읽기와 실제 복원이 같은 규칙을 쓴다. 자식 경로는 부모의 SHA256·선언 길이·정규 JSON을 `_read_json_blob`으로 확인한 뒤에만 발견한다.
- 실제 `decode/_decode_snapshot`는 좌표·중복·객체 branch/목록 prefix의 관계, 필수 외부화, 재인코딩 일치를 계속 검사한다. 크기와 해시가 맞아도 비정규 JSON이나 잘못된 그래프는 반려한다. `FrozenText` 공유는 유지하고, 반환하는 dict/list는 논리 좌표마다 독립적이다.
- 상태 계약·사건 순서·artifact 증거 검사는 그대로 뒤따른다. `sealed_bytes`, `VERIFIED_ARTIFACTS`와 `_read_json_blob`의 등록된 정규 JSON 변종을 대체하지 않았다. Git OID·경로·blob 타입·응답 길이·누락 처리는 기존 저장 포트가 맡는다.
- 새 전역 바이트/논리값 캐시는 없다. 임시 참조 집합은 한 복원 안에서만 살고, 읽은 bytes는 기존 `_VALIDATED_READS` 항목에 들어간다. 기존 4개 비보존 snapshot 한도와 live 입력 snapshot 보존 규칙도 유지한다.

## 정확 감사 snapshot 비교

영구 근거 위치는 `C:\math\.async\dm-flow-repair-20261021\tasks\batch-payload-reads\evidence`다. 감사 `records.json`의 489개 기록 및 `snapshot/`의 1,951개 파일, `status-profile.txt`를 대조했고, 원 연구 저장소의 `.git`을 별도의 `audit-before/.git`, `audit-after/.git`에 복사해 읽었다. 원 연구·work·감사 파일·HOLD·예약은 수정하지 않았다. 과거 자료를 위한 호환·변환 코드는 추가하지 않았다.

입력은 양쪽 모두 정확 commit `811c4576af7fc8a5054181ad0208db42ddd329c6`이다. 개선 전 코드는 서비스 `workspaces.py restore ... baseline`로 `evidence/baseline`에 복원한 이 task의 시작판이며 과거 감사 코드/계측의 재사용이 아니다. 개선 후는 이 task 정본 코드다. 두 Python 프로세스는 각자 새로 시작해 application 캐시가 비었고, warm은 같은 reader와 같은 명시 commit을 다시 읽은 것이다. OS 파일 캐시와 호스트 전체 부하는 통제하지 않았다.

| 조건 | 개선 전 Git 자식 | 개선 후 Git 자식 | 개선 전 경과 | 개선 후 경과 |
|---|---:|---:|---:|---:|
| cold, 시험 종료 후 연속 비교 | 260 | 23 | 31.261 s | 3.677 s |
| warm, 같은 프로세스/reader/head | 0 | 0 | 0.024859 s | 0.037647 s |

측정 범위는 `ResearchRepository.load(explicit_snapshot)`이며 반환 사본 생성까지 포함한다. store 생성의 `describe` 1회는 `setup_commands`에 따로 기록했다. cold 내부는 전후 모두 `ls-tree` 1회이며 `cat-file --batch`가 259회에서 22회로 줄었다. 측정 콜백은 실제 `subprocess.run`을 호출하며 각 명령의 argv·반환 코드·경과를 원자료에 남겼다. Python mock의 호출 수로 프로세스 감소를 추정하지 않았다.

양쪽의 복원 상태를 정규 JSON으로 직렬화한 SHA256은 `894efcdf56e52387afa870a4819f16e1950ba87ba7546f3192650ecc8603249f`로 같다. 보관된 정확 파일 765개(비artifact 508개, payload/snapshot 257개), 총 4,399,529 bytes의 경로·길이·SHA256 전부도 일치한다. `comparison.json`은 두 원자료의 전체 파일 맵과 논리 해시를 실제 대조한 결과다. 실제 bytes와 저장 bytes의 직접 동일성은 아래 판본/독립성 시험에서도 확인했다.

원자료는 `benchmark.py`, `audit-before-quiet.json`, `audit-after-quiet.json`, `comparison.json`이다. 각 JSON에 네 저장 모듈의 실제 소스 SHA256을 남겼다. `git_store.py`와 `git_process.py`는 전후 같은 판본이다. 첫 비교 `audit-before.json`/`audit-after.json`도 보존했다(40.401/3.757 s, 260/23회). 첫 baseline 실행이 boundary 시험과 일부 겹쳤으므로 표에는 시험 종료 뒤 비교를 썼다. 뒤 비교도 호스트 독점을 보장하지 않으며, 반복 통계나 모든 연구의 속도를 뜻하지 않는다. 과거 38.717초·274회 관측은 이번 개선 전 재측정으로 사용하지 않았다.

실행 명령은 `evidence/commands.ps1`에 남긴다. 재실행 시 `BASE`는 보존 baseline의 scripts, `AFTER`는 서비스 result 복원판 또는 수용된 같은 정본의 scripts를 가리켜야 한다. 이 task workspace가 정리되면 `workspaces.py restore RECORDS batch-payload-reads result NEW_DIRECTORY .claude/skills/do-math/scripts`로 복원할 수 있다. 현재 audit 복사본도 단순 읽기용이며 이후 원 연구 운전용으로 쓰지 않는다.

## 선택 검증과 한계

`unit.test_repository_payload_reads`는 실제 저장소 복원에서 두 판본 분리, 저장 bytes 동일성, 반환 컨테이너 독립성, 무관 artifact 미선읽기, text/node 누락·손상, 잘못된 길이·경로, hash-matched 비정규 JSON과 잘못된 자식 참조를 검사한다. 손상 사례마다 새 저장소를 만들어 기존 봉인/검증 캐시가 반려를 가리지 않게 했다.

`boundary.test_storage_batch_process_counts`는 실제 Git 자식의 `subprocess.Popen` 감사 사건을 센다. 80개의 서로 다른 큰 text와 공유 중첩 snapshot의 정확 복원, cold 호출 감소, warm 0회와 기존 export/query의 batch 계약을 확인했다. 데이터는 `tests/support/storage_snapshot_cases.py:payload_state`에서 현행 설치 스키마로 만든다.

저장/payload/반려 모듈의 첫 선택 실행은 57개 중 55개가 통과하고 두 개가 실패했다. 하나는 `read_many`가 상태+payload 두 batch를 맡게 되면서 달라진 기존 호출 수 단언이었고, 다른 하나는 선읽기가 미선언 파일의 기존 오류 사유를 먼저 바꾼 것이었다. 호출 수 단언을 갱신하고 payload 참조가 없는 문서는 선읽기 단계에서 건너뛰어 기존 반려 사유를 보존했다. 수정한 시험과 관련 경로 6개를 재실행해 모두 통과했다. 마지막 실행 결과를 합치면 서로 다른 선택 시험 58개가 통과 상태다. 전체 회귀는 수행하지 않았으며 통합자가 맡는다. 결과/실패 근거는 `storage-tests/report.json`, `focused-recheck/report.json`에 있다.

공식 writing-skills 생성기로 Codex 미러를 생성했고 `--check`가 1,389개 파일에서 drift 없음을 확인했다. 시험 도구가 갱신한 두 `.timings.json`은 시작판 bytes로 돌려 배정 밖 생성 변경을 제외했다. `.agents/diff`는 변경하지 않았다.

64는 한 batch의 경로 수 한도이며 byte 한도는 아니다. 하나의 큰 blob 전체를 읽는 기존 계약은 유지한다. 아주 긴 단일 목록 prefix처럼 다음 참조가 부모 한 개에만 들어 있는 경우에는 깊이에 따른 Git 호출이 남는다. 중첩 snapshot은 선읽기 때 검증해 파싱하고 실제 materialization에서도 파싱하므로 그 CPU 비용은 남는다. 전체 복원 bytes는 기존 snapshot 캐시가 보관하며, 이번 변경은 그 캐시의 용량 정책 개선을 주장하지 않는다.

## manager가 공통 이음새 정본에 반영할 정의

`scripts/이음새-정본.md`는 다른 task가 소유하므로 여기서는 수정하지 않았다. 다음 문장을 저장 복원·봉인 snapshot 절에 연결할 수 있다.

> `payloads.prefetch(envelopes, read_payload, git_dir=None)`는 읽기 일정만 정한다. reader에 `prefetch(paths)` 콜백이 있으면 최상위 payload와 검증한 snapshot 노드의 도달 가능한 참조 집합을 차례로 공급하고, 콜백이 없으면 아무 작업도 하지 않는다. `ResearchRepository._read_documents`의 reader는 같은 명시 commit에서 경로를 최대 64개씩 기존 `GitStateStore.read_many`로 읽고 한 복원 안에서 bytes를 재사용한다. `payloads._references/_snapshot_node/_snapshot_cell`은 선읽기·decode의 공통 구조 검사다. `_read_json_blob`은 기존 해시·길이·정규 JSON 변종 정본으로 유지하며, decode의 관계·좌표·재인코딩 및 저장 계약/사건/evidence 검사는 생략하지 않는다. 임시 선읽기 집합을 새 전역 캐시로 보관하지 않고 기존 snapshot 캐시 규칙을 따른다.

외부 GitBackend/GitStateStore 포트의 시그니처·상태 스키마·업무 전이는 변경하지 않았다.
