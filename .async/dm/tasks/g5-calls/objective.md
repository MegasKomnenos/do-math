# 제어·복구·호출 처리의 남은 분기를 현재 계약으로 마무리

g5-core와 g5-inputs의 유효한 수리를 부분 수용했다. 전체G5는 아직 미충족이다. 이 task는 core_engine.py의 잔여132arc/168행과 call_engine.py의 잔여5arc/5행, 총137arc/173행을 현재 계약에 따라 판정하고 관련 구현·직접시험·설명·공식미러를 함께 끝낸다. 좌표는 관측된 공백이며 도달가능성이나 제품결함의 사전 판정이 아니다. 파일 쓰기상한은 전수수정/전수실행 의무가 아니다.

## 시작과 입력

SESSION_JSON·task.json·inputs/context.md/plan.md/seams.md와 자기 workspace의 do-math AGENTS.md·scripts/tests/시험-지침.md를 읽는다. 추가 절대경로는 공용 소스/기록을 읽기 전용으로 소비하라는 뜻이다. managers/0071/review.md, g5-core/report.json·evidence/remaining-scope.json·remaining-functions.md, g5-inputs/report.json·evidence/judgment.md·scope-coordinates.json과 자기 gap-scope.json을 필요한 범위에서 읽는다. gap-scope는 두 원자료의 잔여 좌표와 수용판 SHA를 연결하는 인계 자료이며 새로운 계약이 아니다. 시작판과 다르면 실제 diff로 연결한다.

사용자 저장범위 지시 sources/storage-scope-direction-2026-10-15.md와 원설계3.3/A22·5.5 및 시간 정정을 적용한다. 공통codec/저장검증과 기존업무 단언을 재사용한다. 전가족·전필드·새reader·옛head quota, 새 검증 framework나 장기감사는 만들지 않는다. 과거 전체T3는 tasks/g5-full/evidence/full1에 있다. 보존 index는 evidence/observed-caches/.claude/skills/do-math/scripts/tests/.selection-index.json이며 원 workspace 캐시는 복원됐으므로 소비하지 않는다. 함수 진입은 결과 단언의 증거가 아니다.

## 구현 범위와 완료 판단

제품 수정은 core_engine.py·call_engine.py에 한정한다. task.json의 직접시험/helper·관련문서와 공식미러도 함께 소유한다. 진행 중 g5-worker/g5-publish의 소스·helper·CLI 설명·scripts/이음새-정본.md는 읽기전용이다. review_engine/submission/knowledge 등 제공자나 schema/lifecycle 수정이 실제로 필요하면 정확한 원인·파일·요구 변화를 보고하며 다른 task 사본을 변경하지 않는다.

1. core의 원/현재 잔여 좌표는 gap-scope와 remaining-functions에 있다. 제어 접수/적용과 정산, 게시 재시도, 실제 봉인 입력/복구, 관찰·결과 수신, 확장 적용·초기수신·운영 처분의 caller/불변식부터 읽는다. 불필요한 중복 방어·죽은 계약은 제거/축소를 먼저 검토한다. 공개 형식·참조·권한·증거·현재성 검증을 약하게 해 도달 수를 줄이지 않는다.
2. call의 현재149→150은 review admission 거절 뒤 준비 저장,177→180은 impact wait 없는 SealedSubmissionError의 일반 격리,558→589/568→589/584→589는 실패 handler 뒤 pause/close 보존이다. 남은 행150/151/180/183/205 중183/205의 GitStateStoreError 전파도 함께 판단한다. g5-inputs의 review_scene 표본은 실제 등록 진입0회여서 철회됐다. 그 실패를 제품결함/죽은분기 증거로 쓰거나 역할 최소등급·공용helper를 완화해 살리지 않는다. 유효한 실제 생산 전제 또는 호출 불변식으로 좁게 해결한다.
3. 도달가능한 누락에는 가장 싼 기존 시험에 유효 입력과 정확한 결과·반려·저장/정산 단언을 보완하고 관련 결함을 같은 작업에서 고친다. 이미 충분한 codec/업무 성질은 반복하지 않는다. 내부 제품패치·호출만 하는 시험·이유 없는 예외포착·빈단언은 해결책이 아니다. 해당 경계가 요구할 때 외부 포트의 실제 실패 대역은 사용할 수 있다.
4. 의도적 미도달은 설계5.5와 현재 caller/불변식의 구체 사유로 처리한다. 필요한 코드를 blanket no-cover·새skip·층/분모/임계값 완화로 덮지 않는다. T4/subprocess 실행을 T3 도달에 수동 합치지 않는다. 좌표만 덮고 결과를 단언하지 않는 시험을 만들지 않는다. 서로 다른 부분 판본은 단일 최종 성공으로 합산하지 않는다.

## 최소 검증과 자원

시험슬롯1, 공식 scripts/run_tests.py의 기본 --jobs 1·한 명령씩이다. 다른 두task와 합계3 이하를 유지한다. 병렬 자식을 만드는 meta/전체관문·새전체G4/T3·전체변이·T4/T5·유료호출·실예약/설치변경은 이번 범위가 아니다. 정적 판단으로 충분한 부분은 실행하지 않는다. 필요한 시험이 지정 분기에 도달하는지 불확실하면 가장 작은 선택에 --tier T3를 붙여 원coverage를 보존한다. 같은 확인을 일반/T3로 중복하지 않고 실제 불확실성이 해결되면 다음 항목으로 진행한다.

측정에 Git root가 필요한 경우에만 자기 workspace에 독립 .git/실제소스 로컬 기준commit을 준비할 수 있다. tasks/g5-full/evidence/prepare.py를 자기 경로로 적용하고 준비 전후 제품bytes·자기root/HEAD를 기록한다. 이는 공용main/통과 인증이 아니다. 다른.git 복사·공용Git/index/commit·global설정·가짜HEAD·remote/push는 금지한다. 기존 GIT_CEILING_DIRECTORIES를 유지하고 자기 task 부모/외부 임시root를 더한다. 임시자료/store/output은 evidence 또는 저장소밖 짧은 고유 경로에 둔다. 외부권한은 변경하지 않는다.

실행한 확인의 command/cwd·관측exit·원report/stdout/stderr·선택/고유실제행·fixture·판본SHA·실행중변경을 보존한다. coverage는 해당 소스bytes와 원/현재 좌표·도달/남김을 연결한다. 부분선택의 gate=false/exit1과 실제 시험 실패를 구별하고 결과를 전체G5로 확대하지 않는다. 시간 초과는 소프트 기록이며 중단/skip/변이포착 수단이 아니다. 생성 index/timing/store는 원자료 보존 후 base 바이트/부재로 복원한다.

## 제출

evidence/judgment.md와 report에 어떤 사용자 결과/불확실성을 해결했고 어떤 기존 근거를 재사용했는지, 좌표 묶음별 수리·제거·사유 있는 제외·구체 남김을 적는다. 유효한 범위는 끝내고 남김이 있으면 partial/blocked로 사실대로 보고한다. 필요한 설명은 허용 문서에서 구현과 함께 마치며 공용 seams에 필요한 의미는 파일·심볼과 함께 report에 전달한다.

정본과 대응미러는 공식 build_skill_mirrors.py로 생성/check하고 범위 밖 파일은 제출하지 않는다. 공용 context/plan/seams/queue/state와 engine·다른task·graphify는 수정하지 않는다. `python C:/math/services/async-development/check.py report C:/math/.async/dm g5-calls`를 통과시킨다. 최종 통합판 전체G4/G5·G6~G8 및 G1~G3 연결은 별도 후속이다.
