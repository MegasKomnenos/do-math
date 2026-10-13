# phase 010 host-smoke의 현재 경계와 검토

시작 HEAD는 03a281b13ae6f559604536b2d8450ce005106057이고 종료까지 같다. 009 manager가 검수한 당시 HEAD 0af5dd66와 관리 마감 커밋을 구분한다. start.json의 dirty에는 기존 canonical/repository·migration·다른 스킬·운영자 설정과 미추적 자료가 있다. source-start.json의 2640파일은 009 task source-final과 전건 동일하다. 기존 dirty를 이 task에 귀속하거나 정리하지 않았다. 마지막 verification.json의 2644파일 중 실제 변화14개는 phase writes와 정확히 같고,4개는 새 정본/미러 host 시험·지원 파일이다.

## 현재 실제 호출 경로

Job 연쇄는 wiring.real_ports(environment=...) → WindowsJobs → ModelRunner.run → CodexAdapter/LocalCLIAdapter.start → codex_worker.load_request → cli_worker.run_cli → 실제 subprocess.Popen이다. LocalCLIAdapter.start가 prompt/schema/request를 스냅숏으로 고정하고 worker_argv=(현재 Python, 실제 codex_worker.py, 스냅숏 request)를 만든다. WindowsJob._create_job은 kill-on-close·비상속 Job을 만들며 breakaway를 허용하지 않는다. _create_suspended_root는 PROC_THREAD_ATTRIBUTE_JOB_LIST와 CREATE_SUSPENDED/CREATE_NO_WINDOW를 함께 사용해 사용자 코드 이전에 소유를 확정한다. ModelRunner가 process_identity의 PID/십진 문자열 FILETIME·Job 이름을 on_started로 공개한 뒤 resume한다.

새 T5는 이 경로에서 외부 공급자 CLI만 자기 scratch의 local-cli.cmd/local-cli.py로 대신한다. 실제 .cmd 중간 프로세스와 Python CLI·child·grandchild는 모두 같은 Job에 들어간다. OpenJobObjectW/QueryInformationJobObject/IsProcessInJob/GetProcessTimes/held process WaitForSingleObject로 제품 collector와 독립된 커널 관측을 얻는다. should_stop callback에서 marker를 읽고 소유를 관측한 뒤 정상/exit7 사례는 release를 지급하고, 취소 사례는 release 없이 True를 반환한다. LocalCLIAdapter.stop의 TerminateJobObject → wait_for_termination → collect → close를 실제 실행한다. 마지막 root_signaled=true/active_processes=0/process_ids=[]와 네 held handle의 신호0, named_job_empty=true를 대조한다. 각 외부 프로세스 argv/cwd/PID·worker argv/cwd·시작/종료·스냅숏 request/schema/prompt·stdout/stderr·원결과/파싱 결과는 scratch의 smoke.json과 call/에 남는다. PID 숫자의 재사용을 기다리거나 경과 시간을 종료 증거로 쓰지 않는다.

pythonw 연쇄는 같은 Python 설치의 pythonw.exe → 실제 submission.install_tools → file_io.console_python → context.record_map.read_tool.command → PowerShell 실제 호출 → 지급된 python.exe -B input/tools/read_input.py → input_tool.read_main → context_store의 고정 snapshot 읽기·READ_LOG 기록이다. 준비의 make_repository는 최소 Git 레이아웃만 만든다. 이후 GitStateStore.publish와 설치된 읽기 도구는 real_ports.GitProcess로 실제 Git object/HEAD를 쓰고 읽으며 대역 backend를 전달하지 않는다. WINDOWLESS_READ를 support.host_live의 단일 정본으로 옮겨 boundary와 T5가 함께 사용한다. pythonw 부모의 console=0·부모 PID/FILETIME/argv/cwd/Python 판본, PowerShell 5.1.22621.6133의 PID/경로/argv/cwd, 지급된 command, 원 stdout/stderr 파일 및 JSON 파싱 결과, 정확 exit0/exit1·성공 레코드·권한 거부와 읽기 기록을 보존했다. 실제 예약 cmdlet은 호출하지 않았다. powershell_scheduler.run/operator_schedule.ps1의 OS 예약 등록·발화·해제는 별도 후속 책임이다.

## 충분한 기존 검사와 T5에 추가한 성질

test_scheduling_windows_job는 root 보류·정확 cwd/env·자손 terminate·빈 Job·owner 소실의 kill-on-close·핸들 비상속/비breakaway·무관 핸들 격리와 커널 실패를 이미 검사한다. owned_job_children는 held identity·nested Job·CPU 부하 중 local control을 검사한다. SnapshotReadToolTests는 실제 pythonw의 설치/read 성공/반려를 이미 검사한다. 기존 테스트 메서드21개의 AST 본문과 단언은 변경 전과 전건 동일하다. 기다림의 기존 10/15초 상한도 소비자가 그대로 지급한다. process_kernel/release_process/reached 및 snapshot 준비/context/pythonw 실행만 공용 support로 이동했다. 시험 모듈 간 import는 없다.

새 T5는 기존 adapter 단위 정상/오류 검사와 달리 실제 ModelRunner→스냅숏→worker→외부 CLI→자손→collector 조합을 실행하고 그 OS 자료를 runner scratch에 보존한다. 정상 최종 응답은 원 schema 의미 값과 UTF-8 한글을 검사한다. 음성은 외부 CLI 자체의 exit7/stderr와 정확한 execution_failure·collection reasons를 검사한다. 취소는 외부 자손이 실제 시작·소유된 다음에만 발동한다. pythonw 경로는 기존 준비를 그대로 호출하며 파일 위치/파싱/판본 자료만 추가했다. 큰 boundary 시나리오를 시험 간 복사하지 않았다.

## 과거 변경의 한정 판단

prior-review-state의 관련 PR02/PR11 범위와 현재 board의 Job/pythonw slice를 대조했다. history-slices.json은 B14/B50/B62 진입점이며, 그 중 setup 콘솔/Git/스케줄 전체는 이 작업의 검토 범위로 넓히지 않는다. history-original-reports.json의 외부 Temp 원보고들은 현재 없다. 당시 counts를 새 통과 근거로 합산하지 않는다. 초기 helper가 저장한 0541a8ab/91e92a8b/a52ffd61의 지정경로 diff는0바이트다. 이는 당시 파일 위치·대상경로 차이이고 해당 도입 검토 근거로 사용하지 않았다.

Job 시험의 실제 도입/이행은 23cc4df3 diff를 읽어 현재 소비자와 대조했다. 초기 suspension/owner-close/descendant/barrier 단언을 유지한다. synthetic PID locator와 held handle의 구분, nested Job 및 CPU local control 성질도 유지한다. 7d2597ec diff는 해당 Job 초기 동작 부분만 확인했고 다른 제출/평가 변경의 유지 판정에는 사용하지 않았다. 현재 관련 실제 커널 시험과 port 양쪽은 새 related-results에서 통과했다. 원보고 없는 옛 counts는0건 재사용이다.

pythonw 도입c71053d6의 실제 diff는 install_tools가 지급한 명령을 PowerShell에서 그대로 소비하고 parent executable/console·정상/반려 JSON/exit를 검사한다. 현재 해당 성질을 유지하고 공용 helper로 이동한다. B117의 존재하는 두 원보고는 history-existing-reports.json의 SHA와 실제 row를 확인했다. 최초19passed/2error는 tuple arguments fixture 오류였고 windowless-after의 정확 두 ID는 passed다. 46aaa333/B118 diff의 console 형제 부재 명시 반려와 설치 전 실행기 선택은 그대로 유지한다. B118의 존재하는 before/fixture-path-failure/focused/report 원자료 SHA·관련 row를 확인했고 역사 실패를 지우지 않는다. 현재 runtime을 바꾸거나 형제 부재 fallback을 복원하지 않았다. B117/B118 다른 builder/저장/예약 정책까지 새 검토 완료로 올리지 않는다.

## 실제 결과와 남김

host-01은3선택/2passed/1failed/exit1이다. 정상 로컬 CLI 표본에서 turn.started가 빠져 실제 parser가 invalid_lifecycle_order/jsonl_parse_incomplete를 반환했다. 제품을 바꾸지 않고 표본에 실제 lifecycle 사건을 추가했고 host-02는 실패한1선택/1passed/exit0이다. Python 판본 기록과 exit7의 정확 error/reasons 단언을 보강한 최종 host-final은3선택/3passed/exit0, mirror-host도3선택/3passed/exit0이다. verification.json은 최종 소스 해시·선택/고유row/counts/실제process exit 및 양쪽 각4개 OS 관측 파일을 원자료에서 대조했다. 로컬 CLI 표본은 실제 공급자 native 녹화가 아니며 corpus에 넣지 않았다.

related-results는61선택/59passed/1failed/1error/exit1이다. 수정한 boundary21건과 Job 포트 양쪽/기타 지정 구조는 통과했다. 실패는 기존 structure.test_test_smells의 unpinned_rejection4건(문서검사1·knowledge_currentness3)이고 오류는 수정하지 않은 call_jobs의 cancellation 검사다. 시작 바이트와 동일한976파일의 독립 사본에서 정확 두 ID를 공식 runner로 실행해 동일 failed1/error1을 재현했다. call-jobs-diagnosis.json은 실제 _job_run 호출에서 필수 clock/environment 부재 TypeError를 기록한다. ModelCalls가 이를 failed-result dict로 돌려준 후 옛 tuple 단언[-1]이 KeyError를 만들어 Job 취소를 실행하지 못한다. task 쓰기 밖이므로 수정하지 않고 A3 미충족으로 반환한다. 냄새 검사의4개 issue는 전부 수정 범위 밖이고 현재 host/수정 boundary의 개별 smell_issues와 지원코드 product_patch 결과는 빈 목록이다.

첫 baseline 구성은 HEAD의 문서 LF와 작업본 CRLF 차이를 해시가 반려해 exit1이었고, 그 불완전 사본의 runner는 missing folder로 exit2였다. 후속 baseline-tree-02는 후보 개행 바이트 중 source-start SHA와 정확히 같은 것만 선택하고976파일을 대조한 후 재현했다. source-start의 최초 보조 호출도 잘못 적은 source-end 파일명 때문에 실패했고 source-final 정본을 사용해 정정했다. 이 준비 오류를 제품 실패나 재현 성공으로 세지 않는다. 최초 원자료와 오류는 보존한다.

미러 계획은7경로 전부 writes 안이며 build 실제7변경과 같다. 미러 실행 후 비용 캐시만 공식 재생성했다. 최종 --check는1307파일 드리프트 없음, skill-only는 verified/exit0이고 source 변화가 없다. runtime124·기존 공급자 smoke 입력3·corpus102경로(각18항목/51파일/223685바이트/50명시SHA)는 시작과 동일하다. 승인된003/006~009의 한정 재사용 조건을 유지하되 새 모델 호출 성공이나 corpus 녹화로 넓히지 않는다. G4 전체 일반·G5 fresh T3·G6 변이·G8 최종 review 및 G7의 Lean/Mathlib·OS 예약·학술·L01은 남는다.
