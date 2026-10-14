# phase 018 Job cleanup 계약 대조

## 시작과 정확 역사 오류

시작 source-start.json의 skills/diff 2675파일은017 manager source-inspected.json과 전건 동일하다. 입력31개는 input-audit.json에 원바이트 SHA와 형식을 기록했고, 실제 코드·원trace·관련 report를 읽었다.017 c4의 boundary.test_port_jobs.WindowsJobsContract.test_a_job_resumes_only_once는 다시 resume 반려를 통과한 뒤 TemporaryDirectory cleanup의 WinError32/5로 error였다. 앞선 동일 소스 정본과 미러의 passed는 이 실패를 없애지 않는다. 오류 순간 PID/FILETIME·소유 Job·cwd 핸들 상태는 과거 자료에 없다.

JobsContract.setUp의 enterContext는 TemporaryDirectory.__exit__를 cleanup에 등록한다. launch가 나중에 job.close를 등록하므로 LIFO에서는 close가 먼저 호출된다. MARK root의 cwd는 해당 directory이며 정확 메서드는 root/빈 Job을 기다리지 않는다. WindowsJob.close는 비상속 Job의 마지막 소유 핸들을 닫아 남은 프로세스를 죽이고 process/thread 핸들을 닫는다. wait나 inspect를 호출하지 않는다. wait는 root signal만 확인하고, inspect는 accounting/PID/root를 별도로 관측한다. 제품 종료 조건의 정본은 cli_execution.termination_confirmed다.

## 실제 관측과 한계

job-observation-before2.json은017 당시 상태가 아니라018의 새 실제 관측이다. 실제 IsProcessInJob·PID/십진 FILETIME·이름·cwd를 기록했다. 초기 suspended/live 상태와 초기화된 resumed 프로세스를 구별했다. 명시 ready marker 뒤 살아 있는 Job의 cwd 삭제는 WinError32였다. 명시 terminate→wait→root_signaled=true/active_processes=0/process_ids=[]→close 뒤 같은 디렉터리 삭제는 성공했다. 대조용 프로그램은 파일 ready를 지급한 뒤 외부 release가 없는 상태를 유지했고, 시간 경과로 죽이지 않았다. 소유 Job 전체를 명시 terminate했다.

원fixture lifecycle의 suspended와 정확 resumes-only-once를 각각 한 번 관측했다. close 전에는 root 미신호/active1이었고, close 직후 Job handle을 복제하지 않고 보존한 process handle의 WaitForSingleObject(0)는258이었다. 이름 조회는 Job 자체가 사라져 true였으므로 종료 증거로 사용하지 않는다. 이 두 실제 root 관측은 close가 동기 종료 barrier가 아니라는 증거다. 디렉터리 삭제 자체는 모두 성공해서017 역사 race를 그대로 재현하지 않았다. 빈도·다른 프로세스의 관여·역사 인과를 확정하지 않는다. 추가 전체 실행으로 빈도를 추정하지 않았다.

첫 observe-before exit1은 suspended root의 cwd가 이미 삭제될 수 있는데 종료 후 rmdir가 경로 존재를 가정한 보조 코드 오류였다. 최초 스크립트 observe_job-v1.py와 stdout/stderr/command/source를 보존했다. 실제 초기화된 프로세스의 ready marker를 사용해 대비 절차만 교정했고 before2 exit0으로 위 관측을 얻었다. 이 오류를 제품 실패나 성공으로 합산하지 않는다.

## 최소 수리

공통 launch는 self._cleanup_job를 등록한다. 이 cleanup은 시험이 소유한 Job을 terminate하고 무기한 root wait를 확인한 뒤 기존 termination_confirmed를 조건 폴링한다. 조건이 참인 뒤 finally에서 close한다. 잠깐의 sleep은 미충족 관측 사이의 폴링 간격이며 단독 종료/삭제 증거나 시간에 따른 종료 정책이 아니다. wait/inspect/assertion 오류도 finally의 handle release를 실행하며 unittest는 시험 본문의 오류와 cleanup 오류를 별도로 보고한다. runtime close, port, fake implementation은 바꾸지 않았다.

job-observation-after.json의 suspended·resumed exact·이미 자연 종료한 marker 메서드는 모두 close 전에 root_signaled=true/active0/PID빈목록이고 directory가 존재했다. close 뒤 보존 process handle의 signal0과 최종 directory_removed=true를 대조했다. 실제 원fixture와 TestCase lifecycle을 호출하고 close를 관측용 wrapper로 감쌌으며 동작을 대역으로 교체하지 않았다. 오류 반려·suspended·정상 marker·시작전 terminate·owner/동명 Job의 기존 공유11개 test method는 변경하지 않았다. 정본/미러 각각 real11·fake11·live fake5, 총27선택이 공식 runner에서 전건 passed다. exact 원오류 ID도 별도1passed다.

## PR02의 한정 재검토

history-job-origin.stdout은 116cff28의 WindowsJob 실제 도입 diff다. 초기 close도 핸들 해제/kill-on-close이며 종료 관측 API와 구별된다. history-job-port.stdout은0b05e8ab의 Jobs 포트/real-fake 계약 도입 diff다. 원 shared fixture의 addCleanup(job.close)와 suspension·marker·시작전 종료·재resume 반려를 현재 소비와 대조했다. history-job-migration.stdout은23cc4df3의 실제 OS 시험 이행 diff다. close 뒤 held process handle로 종료를 기다리는 기존 시험과 terminate 뒤 root/빈Job을 기다리는 자손 시험을 유지한다. kill-on-close를 즉시 완료로 재정의하지 않는 기존 기대값이 이번 수리와 일치한다.

010 host-smoke의 review/history-existing-reports와 실제 collector consumer는 terminate→wait_for_termination→collect→close를 이미 사용한다.016의 실제 Job/Git 관측도 root signal/빈Job/exit를 별도 확인한다. 이러한 기존 승인 성질은 유지하고 shared test fixture의 생략된 종료 확인만 교정한다. PR02 전체·다른 setup/저장/예약·존재하지 않는 원보고 counts를 검토 완료로 넓히지 않는다.

## 환경과 후속 책임

parent TEMP/TMP/TMPDIR는 각 실행마다 저장소 밖 dm018-* 전용 경로이며 명령 수신에 git rev-parse exit128/빈stdout을 보존한다. resource worker는 output 하위 scratch를 사용하므로 전체 output은 evidence/c4·m4로 따로 줄였다. path-preflight.json은 불변 installed-probe TestCase의 고정폭 임시 이름/bootstrap 해시 경로를 대조해 최종 cwd 구성229자를 계산했다.017 성공241자보다 짧다는 이 환경의 배정 조건을 확인하며 보편 Windows 상한으로 쓰지 않는다. 시험 지침에 두 경로 조건과 Job 종료 관측 의미만 추가했다.

017 raw의 TestCase·WORKER/SNAPSHOT·runner·adapter/branch 측정 정의는 불변이다. raw-reuse-basis.json의 해시로 정본 companion만 한정 재사용한다. 미러는 새 공식 suite에서 직접 실행하며 미러 companion raw를 확보했다고 쓰지 않는다. 기존 raw/원보고를 수정하지 않는다. shared fixture와 시험 운전 지침 변화는 모델/Lean/예약/학술 실호출의 입력·runtime·녹화·도구를 바꾸지 않는다. 기존 실호출은 승인된 범위만 유지하고 새 유료 호출·실예약·학술 호출은 없다.

최종 전체 T4 결과·측정 재검산·보존 전수 해시는 별도 verification과 report에 결속한다. 전체일반 G4/freshT3 G5/전수변이 G6/최종review G8, 남은 의미·문서·L01 외부 결정과015~016 제품22경로 Git 마감은 후속 manager 책임이다.017의 과거 실패/미관측 한계와 bootstrap WinError5 원인 미확인은 유지한다.

## 오류 경로의 추가 실제/대역 확인

cleanup-faults.json의 작은 real/fake 각 한 사례는 fixture의 inspect 관측에만 명시 오류를 주입했다. test 본문의 ValueError와 cleanup의 ObservationFault가 unittest 결과에 별도 두 오류로 보존됐다. Job terminate/root wait/close는 실제 real/fake 구현 그대로 실행했고 close 호출·실제 process handle의 closed 반려/대역의 closed/done·directory 삭제를 확인했다. exit0은 이 의도한 오류 처리 성질의 검증 성공이며 일반 제품 시험에서 두 오류를 통과로 바꾼 것이 아니다.

## 기존 제품22경로와 이번 명시 수정 범위의 겹침

015~016 제품22목록에는 정본/미러 시험-지침.md도 포함된다.018 objective가 이 지침의 환경 교훈 반영을 명시적으로 요구하고 writes에도 두 경로를 허용한다. 따라서 수리 범위 밖20경로는 바이트 불변을 확인하고, 지침2경로는 허용된 단락 추가를 별도 기록한다. 원본문을 삭제/교체하지 않았고 새 두 단락의 역변환 바이트가 source-start SHA와 정확히 같은지 확인해 guidance-source-before.md/mirror-guidance-source-before.md에 보존했다. 이 좌표는 사전 복사 주장이 아니라 명시 역편집과 시작 SHA의 대조이며 before-reconstruction.json에 방법을 밝혔다. 기존22경로 전부가 불변이라고 쓰지 않고 후속 manager의 원래22+이번fixture/지침 Git마감 판단에 두 변경을 포함한다.
