# document-closeout의 판단과 인계

이 작업의 A1~A4는 문서 검사기 마감 범위의 조사·판정이다. 제품·시험·제품 문서를 수정하지 않았고 제품 모듈을 import하거나 시험을 실행하지 않았다. 아래 실행 증거는 기존 원보고이며, 새로 실행한 것은 표준 라이브러리로 원문·AST·Git diff·보고서 참조를 조사하는 evidence 스크립트와 서비스 형식 검사뿐이다. 13-C 또는 G1~G8 완료를 선언하지 않는다.

## 고정한 판본과 모집단

현재 HEAD는 `77b8f132c056bcb222e7b6ee431742aa4dc1f27e`이다. 준비 기준 HEAD와 다르지만 baseline의 제품 969개와 원자료 6개의 해시는 모두 현재 파일과 일치했다. 기존 dirty/untracked 변경은 그대로 두었다. `baseline-observation.json`, `reviewed-source-hashes.json` 및 제출 전 검사가 판본의 근거다.

`doc_code.documents()`는 SKILL·README·GLOSSARY 3개, references 10개, 계약 11개를 포함한다. 계약 폴더를 제외한 13개 문서 검토가 아니다. 현재 지원되는 inline 점/배열 필드 참조는 189회, 문서에 등장하는 lexical owner는 79개, `field_schemas()`가 노출하는 owner는 84개다. 별도 함수/상수/진단·파일명 분류와 명령/정책 참조도 원문 좌표를 보존했다.

34는 남은 AST helper 호출 **구문 지점**의 수다. 348행의 한 loop는 실행 창·학술·형식 검사 세 owner를 만들고, 환경 검사는 한 owner에 여러 호출을 쓴다. 34/84 또는 AST 제거 수를 의미 검증의 완료율로 계산하지 않는다. 실제 생산자를 구별하면 현재 같은 이름으로 처리하는 `result_source`, `checkpoint_source`는 각각 둘이다.

`binding-inventory.json`은 84개 owner 각각에 현재 문서 소비, 정의·생산자, 기존 시험, 유지/교체 판단을 둔다. 34개 구문 지점과 중간 `stored_file`, `retained`, `result`, `environment_base` 등의 조립도 연결한다. `source-census.json`은 이 목록의 기계적 원자료이며 새 제품 검사기가 아니다.

## 확인된 두 문서 검사 공백

### 운영 진단의 동명 필드

`계약/운영-점검.md:15`의 `checkpoint_source`는 `_context`의 `operational_evidence.checkpoint_source`이다. 21행의 `checkpoint_source`와 `result_source`는 `recovery_materials` 안에 있다. 후자는 `_context`의 중첩 `recover`가 만든다(`core_engine.py:1807–1864`). 일반 재개 문서 `references/공통-실행.md:45`의 `result_source`는 `context_store.restore_continuation`의 `continuation_history` 항목이다.

현재 `field_schemas`는 checkpoint 이름을 첫 생산자(282행)에만 결속하고, result 이름은 B133의 continuation 경계(37행/283행)에만 결속한다. B133 시험은 실제 재개 결과를 얻지만 24개 문서를 전부 그 owner 표로 검사하므로 운영 진단 21행도 재개 결과의 `local_path`로 통과한다(`test_role_input_packaging.py:338–353,406`). 이는 실제 반환 사용만으로 문맥의 소유자가 증명되지 않는 구체적 경우다.

재현 좌표는 운영 문서 15/21행의 현재 문자열과 위 결속·호출이다. 같은 `local_path`가 있다는 이유로 운영 진단 필드를 재개 결과로 증명하면 안 된다. `_context.recover`는 실패 시 `restoration_error`를 반환하고 `local_path`를 내지 않으며, 일부 정상 formal/child 실행의 `checkpoint_source`는 null이다. 이 task는 그 분기를 실행하지 않았고 제품 반환 자체의 결함을 주장하지 않는다.

**P01**에서 문서를 `operational_evidence`와 `recovery_materials`의 실제 중첩 경로로 명확히 하고 해당 실제 입력/복원 파일 경계에 연결한다. 문장의 읽기 지시도 정상·오류·부재 조건을 구별해야 한다. 일반 재개/반려/이전 출력의 B133 검증은 유지한다.

### bootstrap의 오래된 이름

`계약/독립-운영.md:21`은 bootstrap의 `LIVE_INSTALLATION_ROOT`를 이름으로 든다. 현재 `scripts/operator_bootstrap.py`에는 이 이름이 없다. `main` 168–169행은 manifest의 `installation_root` 또는 `snapshot_root`를 선택해 `scheduled_operator.main(..., installation_root=...)`에 전달한다. 소비자 `scheduled_operator.py:475`도 이 명시 인자를 받는다.

따라서 코드에 옛 전역 이름을 되살릴 이유가 없다. **N03**의 해당 고정 문서 절에서 실제 manifest/인자 전달에 맞춰 문장을 교정하고 기존 bootstrap-info 시험의 실제 원 설치 경로 증거를 재사용한다. 이는 정적 대조로 확인한 문서 이름 불일치이며 bootstrap 동작 실패 판정이 아니다.

## 최근 교체의 유지 판단

`history-verification.json`은 B130~B134의 red/green 12개와 B115 선택 인자 red/green 2개 원보고를 읽은 결과다. 14개 모두 저장된 SHA-256과 일치했다. B130~B134는 선택 시험 ID와 실제 row가 전건 대응한다. red의 실패 내용은 기대한 `ValueError not raised`이며 import나 인자 오류를 그럴듯한 red로 센 것이 아니다. B115 red는 선택 인자 예시에서 타 명령 옵션을 놓친 실제 단언 실패다.

| 범위 | 현재 코드·diff에서 확인한 성질 | 판정과 한계 |
|---|---|---|
| B115 | produced/written/consumed helper와 producer_nodes의 AST는 독립 검토 판본과 동일하다. 삭제·재대입 뒤의 키를 허용하는 R1/R2와 동등한 dict 생성 구문을 거부하는 R4의 과거 반례가 여전히 적용된다. | 소스 구문 추론 확대 중단 판단 유지. 새로 재현 실행하지 않았다. 대괄호 옵션 수리는 현재 strip/정상·반례와 원보고 17개 통과로 유지한다. |
| B130 | `_query_record(row)`의 실제 family와 CLI 파일 query의 실제 페이지/항목을 사용한다. 두 기존 단언은 각각 `record`, `file_page` 변수에 같은 반환을 담아 유지했다. | 유지. 22개 원보고는 해당 범위의 증거다. |
| B131 | init의 기존 원문·목표·SHA-256 단언, 프로필 선택 및 status의 기존 호출·단언이 보존됐다. init만 기존 scheduler 대역을 외부 포트로 넣어 실제 scheduling 결과를 함께 확인한다. | 유지. 실제 `cli.main`/저장소/엔진 경로이며 새 subprocess 검증이나 실제 Windows 예약 성공을 주장하지 않는다. 25개 통과. |
| B132 | 기존 `prepare_role_input` 한 호출의 최종 manifest/artifacts를 사용한다. catalog 생성 횟수·읽기 없음, private resume, artifact 검증·변조 거부 단언을 보존한다. | 유지. 빈 documents 배열과 항목 하나의 artifact_ref 삭제를 거부한다. green 두 개는 같은 26개 모집단의 단계별 결과이며 52개로 합산하지 않는다. |
| B133 | 기존 정상 복원, 단계 순서, 바이트·SHA-256·checkpoint, 최신/유지 파일, activity/cycle 거부 단언을 유지하고 실제 반려 응답 분기를 더했다. 실제 항목 키의 교집합을 사용한다. | continuation 경계 자체는 유지. 운영 진단 문서의 동명 소비만 P01에서 교정한다. 28개 통과가 모든 result_source 생산자를 증명하지 않는다. |
| B134 | 세 100kB 과제, 최초/재현 두 prepare 호출, 실제 source_ref 읽기·전체 ID·프로필·후보 순서·prompt 재현 단언이 보존됐다. | 유지. allowed_profiles 삭제가 실제 두 원문을 실패시킨다. 최종 원보고 28개 통과의 `source_sha256` 전건이 현재 파일과 일치한다. 그래도 전체 일반/T3 증거는 아니다. |

`scoped_field_issues`의 기본값은 실제 경계 표본이 없으면 거부다. 실제 경계 시험은 자신이 제공하는 owner를 구체 객체로 대체하고 나머지만 defer한다. 현재 검토한 경계가 모두 defer되어 사라지는 변경은 없었다. 다만 위 운영 진단 사례처럼 **잘못 붙인 owner**는 이 장치만으로 검출하지 못하므로 문서 문맥 대조가 필요하다.

B119의 record_map 기본 키와 B120의 operating_summary·supervision 키는 실제 순수 반환 사용을 유지한다. `record_map.read_tool`만 P03의 설치 경계에 남는다. B121/B122의 실제 저장소 status/파일 progress, B130/B131의 CLI, B132/B134의 역할 메타데이터를 다시 구현할 작업으로 배정하지 않는다.

## 남은 작업의 경계와 실익

`followup-packets.json`은 새 phase 배정이 아닌 manager용 후보다. P01 운영 증거·복구, P02 원자료·과제 결과, P03 실행 안내·설치 도구로 `_context`를 나눈다. P04/P05는 검토 자리와 고정 질문, P06/P07은 수입과 제출/반려, P08은 신뢰 검사, P09는 change 소비, P10은 헌장·학술 조회 두 경로, P11은 D-06 대기 정책이다. 각 묶음에 원문 좌표·정확한 심볼·재사용 시험·정상/반례·종료·남김이 있다. 공유 doc_code와 호출자를 고치는 작업은 한 번에 하나씩 배정한다.

명시적 문서 점 경로가 없는 다섯 owner를 모두 쓸모없다고 삭제하지 않는다. config/profile은 하위 결속, execution은 저장/역할 입력의 구별 시험이 소비한다. recovery_source는 두 다른 결속의 실제 의존이다. **instance**는 현재 문서·하위 결속·문서 시험의 명시 소비가 없어 노출과 research-root 조립을 제거할 후보로 남겼다. 실제 AST 소비자 교체가 끝난 뒤에만 구문 helper와 그 구문 전용 시험을 제거하고 소유자/배열/누락 거부는 보존한다.

N01~N03은 남은 단독/조합 이름과 역할 산출 이름의 서로 겹치지 않는 문서 영역이다. 제목별 범위는 정확한 원문 좌표이며 task 수가 아니다. 관리자가 닫힌 정의와 이미 검증된 이름을 재사용하여 미결이 있는 절만 배정할 수 있게 했다. 새 이름을 만날 때마다 범용 추론기를 확장하는 방법은 제안하지 않는다.

과거 lexical 미결 17개는 inventory에서 각각 분류했다. F/U는 용어집, needs_revision은 명시적 비상태 예시, import_unit/question_detail은 배열 원소를 부르는 산문 이름, checkpoint_schema는 실제 keyword 생산이다. PT0S는 PowerShell 설정과 표시값의 관계이고 FileRenameInfoEx는 숫자 API 결속이다. Windows 속성·rg·조건부 TaskOutput과 scholarly 경계 어휘를 내부 필드처럼 추가하지 않는다. scholarly의 실제 판본/응답은 G7에서 확인해야 한다. 17개를 17개 결함으로, 3494회 소문자 단독 표기를 3494개 작업으로 세지 않는다.

정책 이름 존재와 정책 의미는 다르다. policy 접미의 5개 lexical 이름을 추출했다고 대기 예외·권한·외부 행동의 의미를 검증한 것은 아니다. P11은 원문 D-06의 명시 조건/예외를 기존 시계 주입 시험과 닫는다. 다른 이름의 해당 문장과 소유자 의미는 N의 배정 문맥에서 확인하며 확정된 차이만 반환한다.

읽기 한도 **L01**은 기존 `reading_boundary_review`를 재사용한다. 역할의 전체 문서는 prompt의 stdin 입력이고, 운전 문서는 순차·구간 읽기를 지시한다. 둘을 하나의 shell 출력 바이트 합으로 비교하지 않는다. 실제 운전 host/tool/version/read-call 설정과 같은 단위의 권위 있는 한도가 아직 특정되지 않았다. 기존 CLI 버전이나 이번 도구의 token 예산을 보편적 byte 상한으로 바꾸지 않는다. manager가 gate-readiness 결과와 이 질문을 통합해야 하며 이 미정을 13-C 통과로 처리할 수 없다.

이번 조사의 종료는 이 고정 범위의 목록·유지 판단·후속 조건을 반환하는 것이다. 새로운 실행을 기다려야 하는 증거, 현재 의미 수리가 필요한 항목, 정적 이름 검사만 있는 항목을 구별했다. 제품 수리와 최종 일반/T3/변이/T4/T5는 여기서 수행하지 않았다.
