# manager 0070 — core 부분 수용과 게시·지식·검토 후속

## 수용 판단

inbox.completed는 g5-core(exit0), running은 g5-inputs·g5-worker다. protocol.md의 manager 절차와 공용 context/plan/seams, g5-core의 objective/report·실제 변경·원증거를 읽었다. g5-core의 정본6제품·12시험·1설명과 공식미러19개를 workspaces.py integrate로 충돌 없이 통합했다. 유효한 수리는 accepted에 넣되 원보고 partial과 남은 165arc/197행을 유지한다. manager는 제품을 직접 편집하거나 제품시험을 실행하지 않았다.

## 변경과 근거

- core_engine.query_records는 Base64 안 JSON null/list/scalar를 객체처럼 접근해 TypeError를 내던 실제 결함을 수리했다. 커서 키는 parameters/snapshot/last이고 parameters는 객체, snapshot/last는 비어 있지 않은 문자열이어야 한다. 형식 오류는 invalid cursor, 조회 조건·명시 판본 변경은 cursor query or snapshot changed, 없는 마지막 레코드는 별도 반려다. 생산 형식과 고정 snapshot·limit 변경 허용은 유지한다. 원 cursor-before의 1failed/TypeError와 수리 뒤 정확 반려·페이지 연결·관계 방향·저장 bytes hash 단언을 대조했다.
- engine._init_process_state는 ResearchEngine.__init__에서 설치경로와 store를 설정한 뒤 호출한다. GitStateStore.__init__의 직전 PhysicalBoundary가 디렉터리·물리 root를 검사한다. 두 중복 fallback/검사를 제거했고 경계의 check/use 위협모델을 확대하지 않았다.
- lifecycle_engine의 UTC 기준값은 load-time validate_lifecycle가 검사하며 현재 lifecycle 스키마는 initializing/active/paused를 허용한다. paused의 허용 복구 또는 반려 뒤 무효 상태 fallback은 불필요하다. record_schemas._lifecycle_references도 StateContract.validate의 스키마 검사 뒤 필수 input_id를 직접 읽는다. 공개 형식·권한·현재성 검사는 유지한다.
- repository._decode_families의 두 실제 호출부 _descriptors/_read_documents가 payload reader를 제공하므로 keyword를 필수로 바꾸고 없는 reader fallback을 제거했다. 봉인 payload 읽기·검증은 유지한다. 위 여섯 arc의 제거는 실제 diff와 caller/검사 순서에 근거하며 새 pragma/skip·관문 완화는 없다.
- 추가 시험은 실제 엔진·Repository/저장 계약 및 기존 포트 대역을 소비한다. 활동 wait 종류, checkpoint 형식, 정비의 종료 확인, 설치 HEAD 관측 실패, 초기 권한/채택 프로필, overflow owner·queue, interrupted result의 예약/종결, record 참조·봉인 근거와 독립 판단의 정확 결과를 단언한다. 제품 판정을 패치하는 방식은 없다. producer_record_storage의 기존 표본에 참조 반례를 더하며 가족별 전필드/새reader/옛head 순회를 추가하지 않았다.

정본19파일 diff·미러19쌍을 읽고 비교했다. check.py report는 PASS report, 통합38경로는 보고 changes와 같으며 통합 뒤 공용 bytes와 제출판도 같다. verification-review.json·integration-check.json에 이 한정 확인을 남겼다.

## 실제 확인과 한계

verify.py는 보존 원보고와 invocation, 소유 제품 SHA와 전체 Python SHA, 실제 행/fixture, 원coverage 및 원좌표를 대조한다. t3-changed는27선택=고유27passed, t3-extra는11선택=고유11passed다. 두 실행의 fixture/failed/error/not_run/skip0·complete/successful=true·changed_during_run=[]와 재사용0을 확인했다. 부분T3이므로 둘 다 branch_gate=false·closing_eligible=false·관측exit1이다. 전체 G5 통과가 아니다.

소유11제품의 SHA는 두 실행과 제출판이 같다. t3-extra의913Python SHA는 제출판과 모두 같고 t3-changed 뒤5시험 파일은 달라졌으므로 별도 시험판으로 남긴다. 결과를 단일 최종판의38passed로 합산하지 않는다. structure-final은 한 smell 구조시험1passed/exit0·29.2초이며 전체 구조검사 성공을 뜻하지 않는다. 공식 mirror check의 exit0 기록과 실제19쌍 bytes를 확인했다. t3-changed72.8초/t3-extra245.9초 및 소프트 초과는 원보고에 보존한다. 앞 구성 오류는 추가 제품결함으로 세지 않는다.

원258arc/302행은 누락 없이 coordinate-judgment와 대응하며 원coverage에서87arc/99행 도달을 확인했다. 실제 diff/caller로6arc/6행 제거를 확인했고165arc/197행은 미완료다. 이는 과거 유한 좌표의 처분이며 새 커서 분기까지 포함한 최종 전체 gap 수는 아니다. remaining-scope.json·remaining-functions.md가 다음 소유자에게 원/현재 좌표와 함수를 제공한다. 현재 최종판의 전체G4/G5·G6~G8·G1~G3 연결·L01/실경계는 남는다.

## 범위 교정과 다음 배정

사용자 저장범위 지시와 원설계3.3/A22·5.5를 대조했다. A22는 모든 저장 생산자 표본 등록을 채택하지 않고 상시 저장검증·제품 전체 구조검사·T3 도달로 역할을 나눈다. 이번 수용은 실제 커서 결함과 관측된 공백에 한정한다. 기존 codec/업무 보장을 재사용하며 전가족·전필드·새reader·옛head quota, 새로운 framework/장기감사를 추가하지 않는다. 취소된 storage-questions/storage-task-state와 기존 원자료는 그대로 보존한다.

새 g5-publish는 아직 배정하지 않은 게시·지식·검토9모듈58arc/50행의 관련수리·최소확인·설명을 맡는다. g5-full만 실제 선행으로 두며 g5-core 수용판을 포함한 새 사본에서 시작한다. 9제품 파일은 원측정 SHA와 같다. 허용 상한은 정본117경로와 대응미러117경로이고 g5-inputs·g5-worker와 쓰기교집합0이다. g5-inputs 소유 unit/test_review_wait_contract.py는 제외했다. 위임 등의 기존 직접시험이 다른 소유라면 허용한 publication_branch_contracts/publication_branches에서 가장 작은 직접 확인을 한다. 설명을 별도 task로 나누지 않았다.

총시험슬롯은 inputs1·worker1·publish1=3이고 max_workers10·worker gpt-6.1-sol/high를 유지한다. 기존86정의/objective·진행중2배정·취소2건을 유지하고 accepted는82개, 새task 포함87정의다. 수행 중 결과를 이번 완료 사건으로 선취하지 않는다.

미배정 남김은 core_engine132arc/168행, 나머지7모듈33arc/29행, Lean·신뢰3모듈43arc/68행이다. 다음 슬롯 해제 때 core 잔여부터 실제파일 충돌에 맞춰 배정하고 독립 Lean·신뢰/저장·수명 후속도 가용 슬롯에서 준비한다. 일부러 모든 동료 종료를 기다리거나 자원만을 위한 depends_on을 넣지 않는다. g5-io의 환경6arc/10행은 실제 file symlink 조건 또는 non-nt/현재 지원계약의 구체 처분으로 이어간다. 같은 권한probe·중간판 전체T3 반복은 하지 않는다.

공용 문서와 objective/gap-scope를 먼저 갱신한 뒤 queue.pending.json을 check.py queue로 검사하고 동일 파일을 원자 교체한다. queue는 active다. 게시가 이번 manager의 마지막 공용 변경이다.
