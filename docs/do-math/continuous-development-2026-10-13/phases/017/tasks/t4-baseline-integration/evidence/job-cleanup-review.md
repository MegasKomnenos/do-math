# 현재 실제 Job의 cleanup 오류

짧은 출력 c4와 외부 짧은 parent TEMP의 전체 정본 결과는294passed/1error다. 정확 실패 ID는 `boundary.test_port_jobs.WindowsJobsContract.test_a_job_resumes_only_once`이고 실제 원오류는 `c4/boundary-isolated-027/result.json`, `stderr.txt`, 부모 `report.json`에 보존됐다. worker 요청/게시/branch DB는 완전하고 Python875파일은 실행 전후/현재와 같다. 두 앞선 동일 소스 전체의 해당 ID는 passed다. 원결과를 소급 교정하거나 실패를 통과로 집계하지 않는다.

현재 `tests/support/port_contracts/jobs.py`의 setUp는 TemporaryDirectory context를 TestCase cleanup에 등록한다. launch는 실제 jobs.launch의 반환 job.close를 나중에 등록하므로 LIFO상 close가 디렉터리 정리보다 먼저 호출된다. 정확 메서드는 resume→같은job의다시resume 반려를 검사하고 root 종료/빈Job을 기다리지 않는다. `windows_job.WindowsJob.close`는 thread/job/process핸들을 닫고 남은 프로세스를 Job close로 종료시키지만 wait/inspect는 호출하지 않는다. 이는 코드 관측이다.

실제 오류는 TemporaryDirectory의 os.rmdir에서 WinError32(사용중), Python의 추가 unlink/rmtree에서 WinError5/32다. child의 cwd가 이 디렉터리라는 입력은 launch의 actual argv/cwd 코드에 있다. root 종료/커널 cwd 해제와 삭제가 경쟁했을 가능성이 있지만 오류 순간의 PID/FILETIME·핸들·root signaled/active count는 별도로 보존되지 않았다. 다른 OS 프로세스의 관여를 배제하지 않았고 불안정성의 빈도나 과거 bootstrap WinError5의 원인을 확정하지 않았다.

writes는 비용캐시4개뿐이라 fixture나runtime을수리하지않는다. 다음work는정확이한메서드·공유JobsContract.launch cleanup과현WindowsJob.close의의미를검토하고real/fake계약을유지하는종료동기화를구현·검증해야한다. 필요시실제processhandle/PID/FILETIME·root/빈Job·cwd해제상태를cleanup전에관측한다. skip/삭제오류무시/무조건재시도로판정을바꾸지않는다. 관련회귀뒤양쪽전체T4를새최종판본에서완결해야한다. 현재실행의부분성공이나미러성공을정본전체합격으로합산하지않는다.
