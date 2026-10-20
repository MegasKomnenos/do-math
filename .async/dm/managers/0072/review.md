# manager 0072 — worker·제어·CLI 부분 수용과 수명/상태 후속

## 판단과 통합

inbox.completed는 g5-worker(exit0), running은 g5-publish·g5-calls다. protocol.md의 manager 절차와 현재 context/plan/seams, 저장 범위 사용자 지시, 원설계 A22·5.5, do-math AGENTS.md와 관련 시험 지침을 읽었다. g5-worker의 objective/report·정본16파일 diff·현재 caller와 시험 단언·원보고/coverage를 검토했다. workspaces.py integrate로 정본5제품·10시험·1설명과 공식미러16개, 총32파일을 충돌 없이 통합하고 부분 수용한다. integration-check.json에서 report 변경목록·통합목록·공용/제출 bytes를 대조했다. manager는 제품 코드를 직접 수정하거나 제품시험을 다시 실행하지 않았다.

## 변경을 받아들인 이유

control_transport.ControlTransport.receive가 공개 입력의 객체형을 먼저 검사하고 _validate_request를 호출하므로 내부 중복만 제거했다. publisher의 preview 객체·최종 상태·published/snapshot 확인과 요청 ID·내용 보존은 유지한다. 새 직접시험은 OS stat/open/link 경계에서 파일 경합만 제어하고 실제 수송의 다음 요청 처리, 영수증 소멸 오류, closed 상태의 unsettled_deliveries와 원bytes를 단언한다.

LocalCLIAdapter의 기본 parse_response는 호출되는 구현이 아니며 ADAPTERS에 등록된 CodexExecAdapter/ClaudePrintAdapter가 각각 제공한다. 미사용 NotImplementedError 몸체만 제거했다. cli.execute의 마지막 arm은 parser의 닫힌 command 집합에서 operator이고, scheduled_operator.execute는 main의 세 choices 및 cli의 고정 check/wake/run-engine 호출을 소비한다. 모든 현재 caller와 앞선 반환을 확인해 마지막 unknown 방어 제거를 수용한다. 직접 임의 Namespace/action을 공개 API로 확대한 변경으로 해석하지 않는다.

operator_bootstrap.freeze의 staging은 함수가 만든 고정 .building-UUID이며 cleanup 바로 앞의 no_reparse가 경로·조상을 확인한다. 같은 parent/name의 반복 검사를 제거했으며 no_reparse와 실제 cleanup은 유지한다. 실제 freeze/verify로 다른 설치 manifest의 spawn 전 반려와 사라진 live 설치의 unavailable/기존 frozen identity·원bytes를 확인한 결과를 수용한다. 이는 frozen runtime에서 자동 manifest를 고르는 남은 분기를 입증하지 않는다.

CLI의 실제 입력 파일 부재/UTF-8/JSON 반려, 접수 후 pending/next_owner, Git 포트 게시 실패의 같은 request_id·원bytes·정상 재처리, HOLD cleanup 실패 후 pause/HOLD 보존과 wake 차단, binary snapshot의 base64/원bytes/SHA/provenance를 확인하는 단언을 보완했다. 제품 내부를 가리는 대역은 없고 OS·Git/Jobs 포트 대역은 실제 구현 판단과 구별된다. timezone 시험도 제품 ZoneInfo를 대체하지 않고 표준 데이터 가용성만 제어한다. CLI-실행-계약.md가 cli._control/main/execute와 scheduled_operator.run_engine, operator_bootstrap.startup_evidence의 현재 의미를 설명한다.

## 확인 범위와 미완료

verify.py/verification-review.json은 두 원보고의 선택=고유실제행·결과 counts·fixture·실행중변경·913Python SHA를 대조한다. 제출판과 다른 시험은 보존 bytes의 원SHA 및 docstring 제거 AST로 확인했다. focused1 뒤 비용docstring 변경과 CLI 시험3개 추가, focused2 뒤 비용docstring 변경만 있으며 모든 소유제품 bytes는 두측정/제출판이 같다. 원좌표/현재좌표는 diff와 원coverage로 대조했다. 제출 정본/미러16쌍과 외부원자료18개 SHA를 확인했으며 공식미러 --check 기록은1376파일 drift없음/exit0이다. check.py report는 PASS다.

| 실행 | 선택=실제 | 결과 | complete/successful | 공식/관측 초 | gate·exit |
|---|---:|---|---|---:|---|
| focused1 부분T3 | 39 | 38passed/1failed, fixture0 | true/false | 443.1/448.031 | false·1 |
| focused2 부분T3 | 3 | 3passed, fixture0 | true/true | 146.1/149.953 | false·1 |

실행중변경은 둘다0이다. focused1의 실패는 structure.test_test_smells가 기존 tests/sim/test_scheduling_close_parallel.py:133의 test_aborted_owner_preserves_the_actual_exception_result_and_clears_live_ids에서 unpinned_rejection을 찾은 것이다. 해당 파일은 worker의 시작/제출판 SHA가 같고 쓰기 범위 밖이었다. 원문에서도 future.result의 KeyboardInterrupt 종류만 확인하며 사유를 고정하지 않는다. 원실패를 보존하고 새 g5-state에 작은 수리로 묶는다. 두 선택/시험판을 단일 최종판 전체성공으로 합산하지 않는다.

원29arc/74행의 처분은 도달12arc/44행·제거/변경4arc/5행·남김13arc/25행이다. 이는 과거좌표 처분이며 최종전체 gap 수가 아니다. 남김은 claude_worker/codex_worker/control_server/control_transport/operator_bootstrap/probe_cli의 직접 script/import 입구와 scheduled_operator.run_engine의 frozen manifest 선택이다. 기존 경계시험의 존재를 이번 실행 성공으로 세지 않으며 child/T4 도달을 T3에 수동 합치지 않는다. 새제외/skip·층/분모/임계값 완화는 없다. 현재 수용판 전체 G4/G5·G6~G8와 G1~G3 연결도 남는다.

## 후속 배정과 범위 교정

g5-publish·g5-calls의 기존 정의/objective와 실행 사본은 유지한다. 새 g5-state는 g5-core의 수리/잔여와 g5-worker의 수용판/실패 발견을 실제 선행으로 core 나머지7모듈33arc/29행과 정확 반려 누락1건을 함께 맡는다. 대상은 dispatch_engine/engine/lifecycle_engine/record_schemas/repair_execution/repository/state_checks이며 정확한 현재좌표·수용 SHA는 gap-scope.json에 있다. 관련 시험/허용 설명·미러를 포함한 정본24/미러24 상한은 두 running과 쓰기교집합0이다. core_engine/call_engine와 기존 공유 helper·README/착수조건/초기화정비·이음새-정본.md 소유를 보존한다. 필요할 때만 두 새 시험/helper 경로를 사용한다.

각 시험슬롯1로 합계3, max_workers10·gpt-6.1-sol/high를 유지한다. 기존88정의·취소2건을 보존하고 g5-worker accepted 추가로84개 수용, 새task 포함89정의다. 다음 가용슬롯에서 독립 Lean·신뢰3모듈43arc/68행을 이어간다. worker script/frozen13arc/25행은 I/O환경6arc/10행과 관련된 작은 실경계/지원계약 및 설계5.5 처분으로 이어간다. 자원만을 위한 의존성이나 모든동료종료 장벽을 만들지 않는다.

사용자 저장범위 지시와 A22의 차이를 다시 적용했다. 새state 배정은 관측된 잔여33arc/29행과 실제smell1건만 요구한다. 공통codec/저장검증·기존업무 성과를 재사용하며 가족별 전생산자/전필드/새reader/옛head 재입증·장기감사·새framework를 추가하지 않는다. 원 산출물/증거와 원래G1~G8은 유지한다.

공용 context/plan/seams·objective를 먼저 완성하고 queue.pending.json을 check.py queue로 검사한 뒤 같은 파일을 queue.json으로 원자 교체한다. 그 게시가 이번 manager의 마지막 공용 변경이다.

