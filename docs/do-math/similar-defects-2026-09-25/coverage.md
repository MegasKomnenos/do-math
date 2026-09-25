# 유형별 탐색 범위와 판정 근거

기준 판본·결함 설명은 [README.md](README.md), 정본 242개 파일·해시·검색 좌표는 [inventory.json](inventory.json)에 있다. 아래의 “추가 확정 없음”은 적힌 경로와 검증 범위의 결론이다. 모든 가능한 실행 순서·입력 조합을 증명했다는 뜻은 아니다.

## 빠짐을 줄인 방법

두 커밋의 의미를 8개 유형으로 나누고 유형마다 생산자→저장→전달→소비자를 확인했다. 정상 경로와 복구 경로, 직접 참조와 간접 참조, 같은 내용의 재사용과 변경, 검증 대상과 최종 게시 대상의 짝을 만들었다. 새로 발견한 입력 형식 오류와 오래된 가변 객체 갱신도 별도 행으로 확장했다. 독립 탐색 결과는 원문과 실제 재현으로 다시 심사했다.

기계 목록은 변경 파일에 한정하지 않는다. `build_inventory.py`가 `git ls-files`로 정본 전체를 열거하고 모든 파일에 같은 검색식을 적용한다. 테스트·문서는 구현과 구분한다. 그래프의 관계가 없다는 이유로 경로를 제외하지 않았다. 검색식·행 좌표는 탐색 기록이며 그 자체를 결함이나 전행 의미 검토의 증거로 삼지 않는다.

## 원인별 검사 원장

| 유형 | 조사한 생산자·소비자와 경계 | 결과 |
|---|---|---|
| T1 전체 신뢰 관측 | `manifest_errors`, `verify_environment_files`, `trust_environment_errors`, `activation_requirements`, `_formal_environment`, `verify_formal`, `EnvironmentChecks.observe/ready/discard`, `_observe_environment`, 동일성 편입·목표 완료 | 구조/live 검사 분리, 전후 전체 관측, 취소·실패·새 시도·CAS 재시도·executor 교체 분기를 대조. 추가 확정 없음. 구조 타입 예외는 D7로 확장 |
| T2 저장·재사용 | `seal_large/encode/decode`, `_read_documents`, `_validate_candidate`, `save_with_state`, Git artifact 불변성, query/read 구분 | D1·D2. 동일 활성 payload 공유·부모 OID/검사 계약 변경·가변 record 분리는 기존 검사 통과. 모든 큰 문자열/manifest가 같은 코덱 경계를 통과함을 확인 |
| T3 시작·종료 | `ticket/validate/validate_start/termination_confirmed`, `WindowsJob`, model runner, formal verifier, `SessionSlots`, engine recovery, provider settlement, scheduled recovery | 살아 있는 owner·다른 세션·Job 충돌·PID 정체성·종료 미확인 유지 대조. 추가 확정 없음. metadata-only fallback만으로 현행 시작 경로가 종료 검사를 우회한다는 후보는 재현 못해 미승격 |
| T4 관찰 시점·순서 | model runner buffer/offset, `ObservationBatch`, `_observe_running`, tracker `observe/_start_call`, delivery/acknowledgement, `ModelCalls.collect/pump` | 기존 수정의 부분행·전달 전 로그·종료 batch·결과 우선 회수 검사 통과. `_drain_review_observations`는 stopping 이후여서 새 live 의무를 만든다는 후보 기각 |
| T5 체크포인트 전달 | `read_checkpoint`, `capture_checkpoint_files`, `recovered_checkpoint`, `bind_checkpoint_artifact`의 모든 호출, engine live/종료/복구, `_context`, 저장 artifact 검증 | D3·D4. live 수집만이 아니라 종료·재시작 뒤 실제 검토 입력에서 원본 접근까지 확인 |
| T5 입력/처분 참조 | `prepare_role_input`, `fit_context`, `reference_catalog`, 보존 validation context, `admissible_basis_refs/require_basis_refs`, packaged submission, `_apply_operational_disposition` | producer/receiver가 같은 고정 검사 문맥 사용. 가독 참조와 처분 권한 목록 분리는 의도. 큰 checkpoint 및 작은 입력에서도 레지스트리 reference 제공 검사 통과. 추가 확정 없음 |
| T6 의미 현재성 | `assessment_basis/current`, `action_read_ids`, relation schema/producer, `contract_review_current`, `revision_waits`, `knowledge._impact_refs/apply_impact`, specialist support | D5. 같은 순회 누락의 다른 영향 후보를 조사했으나 정상 개정 후 완료 현재성 우회 주장은 기각. 아래에 그 이유 명시 |
| T7 사건·후속 | `_activate_initialization`, `_consume_action_events`, `_refresh_readiness`, `task_ready`, reporting/task catalog | 최초 사건의 action 귀속·수락 뒤 소비, 정상 점유와 실제 readiness 상실, terminal stale 후속 사건을 대조. 추가 확정 없음 |
| T8 정비·계측 | maintenance apply/settle, scheduler 새 배정 차단, deferred publication, operator guard/wake/recovery, trace context/phase/progress/timeline | 기존 계산을 끝까지 정산하는 것은 문서 의도. fence로 사용자 pause를 해제하지 않음. 불완전 span 종료 시각을 발명하지 않음. 수동 손상 telemetry 후보는 정상 생성 경로 미확인으로 제외 |
| 새 유형: 분리 객체 갱신 | `continuation_of` 등장 전체, `_save/save_with_state` 뒤 action 갱신, trust activation/check, activities/recovery/repair/external | D6. 유사 `trust_check`는 현재 queue에 다시 복사. 다른 후속 생성은 현재 runtime 변경 또는 queue 재삽입. trust activation 누락만 확정 |
| 새 유형: 입력 오류 정산 | 공개 action 14개, CLI `_json_document`, control 사전검사, handler chain, extended rollback, `_reject_control`, trust/governance 중첩 형식 | D7. CLI/API 도달 가능성 구분. 비정상 중첩 객체·시간 필드가 공통 반려 경계를 탈출. 아래 표와 실제 실행 JSON에 검사 범위 고정 |

## D7: 공개 제어 입구 14개를 모두 대조

다음 표의 입력은 공개 Python API의 `config=[1]`이다. CLI는 JSON 파일 최상위 객체 검사라는 별도 관문을 가진다. API 재현은 실제 임시 Git 저장소에 공개 함수가 저장한 요청을 사용했다. 여러 잘못된 요청을 서로 섞지 않도록 `_inbox`만 해당 저장 요청 하나로 한정해 실제 `_controls`를 두 번 호출했다.

| action | 저장 전 관문 | 관측 |
|---|---|---|
| pause | 공통 config 타입 관문 없음 | 접수 후 두 번 AttributeError, 미처리 |
| resume | 같음 | 같음 |
| close | 같음 | 같음 |
| decision | 같음 | 같음 |
| knowledge | 같음 | 같음 |
| trust | 같음 | 같음 |
| external | 같음 | 같음 |
| conversation | 같음 | 같음 |
| input | text/responds_to 접근 | 접수 전에 AttributeError; 지속 inbox 장애 사례로 세지 않음 |
| configure | config merge/validate_config/build_profiles | 접수 전에 TypeError; 같은 제한 |
| request | role/retry/일부 target·reassessment 검사 | 접수 전에 AttributeError; 같은 제한 |
| source | dict 변환·바이트·해시·이름 검사 | 접수 전에 TypeError; 같은 제한 |
| quiesce | 공통 config 타입 관문 없음 | 접수까지 확인. ingestion은 이 행의 실행 검증 범위 밖. fast-path는 config 미사용 |
| release_quiesce | 공통 config 타입 관문 없음 | 접수까지 확인. ingestion은 이 행의 실행 검증 범위 밖. 현재 fence가 있을 때 config.get 사용을 원문 확인 |

중첩 형식의 실제 재현은 다음과 같다.

| 위치/입력 | 실행 경로 | 결과 |
|---|---|---|
| trust manifest `foundation_profile=[]` | 공개 control → 새 engine.process_controls, 재시작 | AttributeError, 두 차례 같은 실패·미처리 |
| trust manifest `validation=[]` | 같음 | 같음 |
| charter `record.content=[]` | 실제 CLI `decision --file` → process_controls | CLI exit 1, 뒤 처리 두 번 실패·영수증 없음 |
| grant `expires_at=1` | 실제 CLI `decision --file` → process_controls | 같음 |
| decision `change=[]` | Python control API | 접수 후 반복 AttributeError |
| request `review_replacement.action=[]` | Python control API | 접수 후 반복 AttributeError |
| conversation `lease_seconds=1e300` | Python control API | canonical JSON의 float 금지로 접수 전 거절. OverflowError 주장 기각 |

전체 JSON 조합이나 각 도메인의 모든 중첩 필드를 fuzzing한 결과는 아니다. 공통 원인은 **공개 입력의 구조가 확인되기 전에 `.get/.items/.replace` 등 타입 의존 연산을 수행하고, 그 오류가 처리 완료/반려로 정산되지 않는 것**이다. 수리 범위는 trust의 두 필드에만 국한하지 말고 이 공통 입력·오류 경계와 표의 모든 공개 입구를 포함해야 한다.

`_apply_extended_control`의 rollback이 있어도 예외를 다시 던지므로 inbox 정산을 대신하지 않는다. 반대로 이 앞의 short-circuit handler에 공통 rollback이 없다는 정적 사실만으로 부분 상태가 잘못 게시된다고 주장하지 않았다. source 입력도 공개 함수가 바이트를 정규화하므로, 직접 inbox 파일을 변조해서만 생기는 오류를 이번 확정 목록에 넣지 않았다.

## 중요한 기각과 제한

1. **관계 참조 누락 = 완료 현재성 우회:** 성립을 입증하지 못했다. 정상 지식 개정은 `knowledge._impact_refs`가 정식 relation edge를 따라가고 `apply_impact`가 관련 관계와 과제 판정을 별도로 무효화한다. 축약 레코드의 불변 판정/형식 원문을 직접 바꾼 초기 실험은 허용된 상태 전이 재현이 아니므로 확정 증거에서 제외했다.
2. **정비 요청 뒤 기존 계산이 계속된다:** 문서는 새 배정 차단과 기존 계산의 정상 정산을 요구한다. 무조건 즉시 중단해야 한다는 지적을 기각했다.
3. **종료 후 raw JSONL drain이 새 운영 점검을 연다:** 호출 전에 tracker가 stopping으로 바뀌므로 live 평가가 수행되지 않는다.
4. **입력 압축 뒤 검사 문맥이 달라진다:** 실행기가 배포 도구와 같은 저장 validation context를 다시 읽는 경로를 확인했다.
5. **D2가 일반 모델 응답으로 바로 발생한다:** 그런 도달 경로를 재현하지 않았다. 직접 저장소 API에서 artifacts 경로가 충돌할 때의 결함이다.
6. **D6 때문에 취소된 활동이 고아가 된다:** 실제 후속은 같은 활동이며 정상 수락됐다. 선행 실행의 명시적 연결만 빠졌다.
7. **telemetry 손상으로 일반 연구가 실패한다:** 수동으로 조작한 sidecar 외 정상 생성 반례를 확인하지 않아 주요 결함에서 제외했다.

## 보존·재검증

`run_reproductions.py`는 7개 진단 스크립트를 별도 프로세스로 실행한다. 각 스크립트는 폐기 가능한 fixture 저장소를 만들며, 현재 사용자 연구·예약 작업·모델 서비스에는 쓰지 않는다. [reproductions.json](reproductions.json)의 스크립트 해시와 stdout/stderr는 이 위치에서 다시 실행한 결과다. 기존 회귀 검사와 설치 구조 검사는 별도 결과로 보존한다.

이 감사에서 확인하지 않은 영역은 실제 공급자 서비스의 장기 실행, 모든 OS/프로세스 중단 타이밍, 전체 do-math 테스트 스위트, 미지의 모든 JSON·연구 상태 조합이다. 확인된 유형과 재현 범위 안에서는 정상 사례·유사 경로·기각 근거까지 연결했으며, 미확정 영향을 확정 결함 수에 넣지 않았다.
