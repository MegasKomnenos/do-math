# manager 0069 — I/O 부분 수용과 worker·제어·CLI 후속

## 판단과 범위

inbox.completed는 g5-io(exit0)이고 running은 g5-core·g5-inputs다. 종료 사실과 task의 partial 보고를 구별해 변경 원문과 실행 근거를 검토했다. g5-io의 정본5제품·8시험 및 공식미러13개를 workspaces.py integrate로 충돌 없이 통합하고 accepted에 추가한다. 원보고의 partial 상태와 환경상 미검증6arc/10행은 유지한다. manager는 제품 코드를 직접 수정하거나 제품시험을 실행하지 않았다.

protocol.md의 manager 절차, 공용 context/plan/seams, 사용자 저장범위 지시와 원설계3.3/A22·5.5를 적용했다. 원설계 A22는 저장 가족별 모든 실제 생산자 표본을 필수화하지 않고 상시 저장검증·제품 전체 구조검사·T3 분기 도달로 책임을 나눈다. 이번 후속은 실제 측정 공백만 다루며 공통codec/기존업무 보장을 재사용한다. storage-questions/storage-task-state 취소와 기존 산출물은 보존하고 전가족/전필드/새reader/옛head quota·장기감사를 되살리지 않는다.

## 변경을 수용한 이유

- context_store.safe_path는 relative_path의 절대/부모/드라이브 반려와 _physical_root/no_reparse의 물리 구성요소 검사 뒤 중복 resolve/탈출 판정을 없앴다. materialize_inputs/write_source_catalog의 직전 물리 root 확인도 재사용한다. PhysicalBoundary의 현재 check/use 범위를 확대하거나 원자 보안을 인증한 변경은 아니다. prepare_role_input의 reader_task는 reader/runtime task 집합 동등성, ready ID 검사, returned/preparation의 task 순회로 존재가 보장되는 값을 읽는다. 중복 absent 반려만 제거하며 원문·snapshot·profile·review seat 반려를 유지한다.
- file_io.atomic_replace는 첫5시도와 마지막1시도를 나눠 6회 상한, 0/.01/.025/.05/.1/.2 지연, Windows5/32/33만 재시도하고 마지막 오류를 전파하는 의미를 유지한다. 실제 공유 충돌 뒤 교체, 영구 실패 때 source/target 보존, CRT 변환 실패 때 HANDLE 종료 및 물리 경계 오류/identity drift를 정확 결과와 대조하는 시험을 확인했다. ctypes/msvcrt/os/time 등 실제 외부 경계의 대역과 제품 판정을 구별했다.
- observations._self_check_obligation의 유일 caller observe는 due boundary를 consumed_rules에 먼저 기록한다. 변경 규칙 revision과 최대간격 basis가 새 의무를 구별하므로 중복 생성 반환을 제거했다. 기존 반복 checkpoint·동일 규칙·최대간격 시험을 재사용하며 정확 receipt/poll 신원·반려·기한 상태 및 동시쓰기 omission 시험을 더했다.
- parallel.ModelCalls.start_call/_observed가 future당 고정 callback 하나를 queue에 넣으므로 인접 callback identity 비교는 중복이다. 인자수·stream·barrier·receipt시각·row 연속성 분리는 유지·단언한다. scheduler의 두 생산자 _run_machine_steps/_call_steps는 등록된 execution_id를 공급하며 start_call의 nonempty 검사를 받는다. _abort_parallel_calls는 모든 소유 반환의 원bytes를 보존하고 실제 Repository에 같은 결과를 게시한다. machine과 모델 생산 경로의 ID를 읽어 확인했다.
- operation_trace의 append/cleanup/close 실패와 model_runner의 pinned Job drift·stdout 생성 지연은 기존 제품 판정을 실제 파일/Jobs 경계로 실행해 결과와 이후 행 보존을 단언한다. runtime/schema/public API의 새 계약은 없다.

정본13파일 diff와 대응미러13쌍의 byte동일을 확인했다. check.py report는 PASS이고 integration.json의26경로는 보고 changes와 같다. 통합 후 해당26파일의 공용 bytes가 제출판과 동일함을 확인했다. 준비/원자료의 전체 이력을 재감사하지 않고 실제 수용 판단에 필요한 소스·행·coverage만 대조했다.

## 실제 확인과 한계

verification-review.json과 verify.py는 다섯 원보고의 선택=고유실제행, counts/fixture, 실행중변경, 관측exit 및 보존 report/coverage/stdout/stderr SHA를 대조한다. focused1은30passed/3failed/1error(34행), focused2는8passed/1failed/2error(11행), focused3는12passed다. 새 fixture/receiver 기대 교정의 이력이며 이를 제품 결함 수나 최종 전체 성공으로 합산하지 않는다.

final1은53선택=53passed, final2는 부족 용량 profile 입력을 더한1선택=1passed다. 두 실행은 fixture/failed/error/not_run/skip0, complete/successful=true·실행중변경0이지만 부분T3의 전체분모 미도달로 최상위passed=false·runner exit1이다. closing_eligible=false이며 G5 완료 증거가 아니다. 최종 제품 SHA는 두 실행/제출판 모두 같다. final2의912Python 중910은 제출판과 바이트 동일하고 나머지2시험은 비용 이유 docstring만 추가됐음을 보존 전bytes의SHA와 docstring 제외 AST로 대조했다. final1의 overflow 시험과 final2의 확장 시험은 별도 판본으로 보존한다.

원63arc/93행의 좌표는 누락 없이 gap-disposition.json과 일치한다. 원coverage를 대조해49arc/79행 도달, 실제 diff/caller로8arc/4행 변경·제거를 확인했고6arc/10행이 남는다. 이것은 한정 좌표의 처분이며 전체 측정의 수치와 수동 합집합하지 않는다. 공식시간 final1 37.0초/외부37.828초, final2 24.5초/외부25.609초와 소프트 초과를 보존했다. 공식미러 check의1375파일 drift없음/exit0 기록을 확인했다. manager 제품시험0이다.

## 남김과 다음 행동

1. context_store.collect_outputs의 파일 symlink/reparse_file omission: 원185→186 및186~188행, 수용판182→183 및183~185행. 실제 directory junction 반려는 이 조건을 대신하지 않는다. os-condition.json의 파일 symlink 생성은 WinError1314이며 실제 symlink가 있는 호스트 조건의 확인이 남는다. 권한 변경·새skip은 없다.
2. file_io의 non-Windows _replace_once/shared_reader/fcntl lock·unlock/PhysicalBoundary.check 종료: 원66→67,95→96,142→146,156→159,337→-333 및7행. 수용판69→70,98→99,145→149,159→162,340→-336이다. 실제 non-nt 측정 또는 현재 지원 범위와 원설계5.5에 따른 구체 처분이 필요하다. 플랫폼 내부 패치/가짜fcntl/무근거 제외로 해결하지 않는다. 다음 환경/경계 배정에서 이 두 조건을 함께 처리하고 그 전의 전체T3를 반복하지 않는다.
3. 기존 g4-final/G5-full은 이전 소스판의 근거로 보존한다. 이번 제품/시험 변경 뒤 현재판의 전체G4/G5는 아직 확인하지 않았다. 남은 gap 수리를 수용한 최종판에서 연결한다. G6 최종 모집단/색인·G7 실자원·G1~G3 연결·L01·G8 최종review는 남는다.

g5-core/g5-inputs의85개 기존 정의·objective를 보존하고 g5-worker만 새로 준비한다. g5-worker는 원full1에서 아직 배정하지 않은 worker/control/CLI12모듈29arc/74행의 관련수리·최소확인·설명을 묶는다. 제품12·기존직접시험/helper55·선택새시험/helper2·CLI설명1의 정본70경로와 미러70경로가 허용 상한이다. running 소유 control_transport 시험/helper는 읽기 전용이고 필요 시 새 허용 시험에서 같은 제공자를 확인한다. 실제 쓰기경로 교집합은 없다. 선행은 미도달 원측정 g5-full만이며 자원만을 위한 가짜 의존성은 없다.

시험슬롯은 core1·inputs1·worker1=3, max_workers10·gpt-6.1-sol/high를 유지한다. 남은 게시/지식/검토9모듈58arc/50행과 Lean/신뢰3모듈43arc/68행은 다음 슬롯이 풀리는 순서로 실제충돌을 확인해 배정한다. 전체동료 종료장벽을 만들지 않는다. 환경 남김은 구체 조건이 없는 같은 probe를 반복하는 task로 만들지 않는다.

공용 문서와 objective/gap-scope를 먼저 완성하고 queue.pending.json을 check.py queue로 검사한 뒤 원자 교체해 게시한다. 기존85정의·취소2건을 유지한86개 task, accepted81개, status=active다. 게시 이후 이 세션의 공용 변경은 끝낸다.
