# Lean/Mathlib 실연쇄의 판단 근거

시작 source-start의2644파일은011 manager source-inspected와 전건 같았다. gate-readiness가 관찰한 PATH의 lean/lake 부재를 미설치로 해석하지 않고 현 formal.toolchain_root/discover_lean을 사용했다. 실제 command는 portable Lake --dir mathlib-4.32.0 env portable Lean이며, 현 lean-toolchain/lake-manifest/ready marker와9의존 저장소의 HEAD/rev를 직접 읽었다. 설치/신뢰 기록 채택이나 다운로드 없이 real_ports의 jobs/clock/environment/git_backend를 그대로 전달했다.

대표 프로그램은 trust_inventory.validation_program의 SMOKE 정본이다. import Mathlib, n+0=n의 rfl, 실수2+2=4의 norm_num을 setup_lean.verify_environment에서 실제 컴파일했다. live-02의 대표 컴파일308.275825초와 live-final의21.170028초는 각 원validation의 측정이며 다른 파일 캐시 조건의 관찰이다. 코드 속도 개선이나 시간 제한의 근거가 아니다. 현재 사용자 정정대로 시간은 소프트 기준이다.

정상 입력은 직접 작성한 두 선언이다. Mathlib의 자연수 표기ℕ를 소스에도 명시하고 서명은 그 입력과 수학적 내용으로 고정했다. n+0=n의 rfl과 True.intro는 sorry/선택 공리 없이 확인될 증명이다. signature_hash는 사전 정의한 정확 서명 맵의 exact_content_hash와 비교한다. 전체 증거의 선언 키·의존 합집합·Nat/Eq.refl과 True/True.intro의 존재를 확인한다. 짝 오류는 같은 첫 선언의 rfl을 True.intro로 바꾼 타입 불일치이며 실제 exit1/failed/lean rejected/타입 진단이어야 한다. full evidence=True이고 preview로 전체 증거를 주장하지 않는다.

검증기는 제품 formal/lean_evidence/setup/wiring 그대로다. ObservedCalls의 sys.monitoring이 실제 _job_run의 시작과 실제 WindowsJob.close를 관측한다. 닫히기 직전의 spool을 자기 scratch에 복사해 원out/err/status/request와 proposal.lean을 보존한다. Job/clock/worker/compiler/parser 교체는 없다. 관측 실패는 smoke 실패로 남기되 실제close를 막지 않도록 자기 callback 오류만 기록한다. 최종5Job에서 실제 root signaled·active0·PID목록빈값·close·named Job 비어 있음과 자기workspace 정리를 확인했다. ThreadCalls는 실행기 생성자가 아니라 factory이므로 실제 new 호출0으로 추가 계산 부재를 확인한다.

live-01은 도우미의 active_processes 정수를 목록으로 읽은 오류와 ThreadCalls.futures 접근 오류 때문에 공식error1이다. live-02는 실제 대표/정상/타입오류 컴파일을 수행했지만 동일ThreadCalls.futures 접근 오류로 공식error1이고 성공으로 세지 않는다. 첫 Nat 기대서명도 Mathlib의ℕ 표기와 달랐다. 도우미의 실제 타입/포트 계약을 읽고 수정했으며 소스에Mathlib 표기를 명시했다. 실패 보고/원spool/정상·오류JSON은 그대로 보존했다. live-final의20판정전부true와 공식passed1/exit0만 새 완료 근거다. 실패 자료는 보존을 위해 scratch에 남기며 활성 Job이나 기존연구 자원은 아니다.

새 corpus는 live-final의 normal 원out71704bytes를 자르거나 다시작성하지 않고 복사했다. source120bytes/compiled6597bytes와빈stderr도 원파일 복사다. recording.json은 판본·정확argv/cwd·시각·Job/PID/FILETIME·범위·전체증거/원출력SHA와 제품 축약stdoutSHA를 결속한다. 제품 결과 stdout은 dependency body를 해시로 줄이므로 원출력과 구별한다. 대표컴파일·오류입력·설치fingerprint는 실행evidence에 유지하고 출하corpus는 작은 정상녹화만 담는다. 기존18entries/verdict와50비manifest파일은 변경하지 않았다. 기존reader는 preview=False 전용이어서 새로운full 녹화에만 명시extract_evidence=True와서명해시/의존증거판정을 사용하도록 확장했다. 기존두Lean 항목은 같은preview 경로를 따른다.

B38/8afa57c7 slice는 history-b38.stdout의 실제 formal/setup/GitProcess/GitBackend hunk와 현재 함수를 대조했다. formal 직접_git을 없애고 project_repository_root/project_snapshot을 필수backend에 맡기며, memo 키를 backend identity+path로 둔 계약을 유지한다. None Git root/미추적소스/관련subtree와.lake 제외, strictUTF8/stop/오류 의미는 포트 정의 및 현 ProjectSourceIdentityTests와 대응한다. setup.observe_identity/기록진입과inspect/verify/identity_error가 같은backend를 전달하며 새smoke도 real_ports backend를 전달한다. GitProcess의 프로젝트 읽기환경과 저장/CLI초기화환경은 서로 다른 계약을 유지한다. 현재8개의관련sim선택을 더해 이 재사용slice의 정상/경계를 확인한다. 이미 검수한host/console은 다시실행하지 않는다.

원보고 selector10개는 b38-review/b38-tracking에서 찾아 history-original-reports의 실제file 존재를 검사했지만 모두 없다. 과거2/68/46등counts는 역사주장으로 남기며 새성공에 합산하지 않는다. 이번 slice는 현재code+실환경+지정회귀로 유지 판정하며 PR02전체를 종료하지 않는다. 원문설계3.3의corpus 순회,4.5의원바이트/판본/판정,5.1의T5/격리,결함범주9-C의실대표컴파일 요구와 시험지침을 대조했다. objective의설계5.6은 현재 원문에제목이없다. 현5.1 T5·4.5·9-C·마지막시간정정의실제내용으로 해석했으며 계약이나목표를 줄이지 않았다.

기존 공급자/host T5는011에서 승인한 성질과 제한만 재사용한다. 새유료호출·host T5·예약변경·학술호출은0이다. runtime124·공급자입력3·host입력과기존corpus102경로/규칙의불변은 최종source/Git raw-clean검산으로 결속한다. 최종일반·freshT3·전함수변이·나머지G7/읽기조건·최종review와Git 마감은manager/후속task의책임이다.
