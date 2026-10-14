## 목적과 역할

G3/G7의 마지막 확인된 T4 오류인 실제 JobsContract cleanup을 검증·수리한다.017의 두 exact 비교와015의12미통과 해소는 검수됐다. 최종 정본 c4는294passed/1error, 미러 m4는295passed였으며 측정은 양쪽 complete다. 이 work는 정확한 오류의 원인 대조·fixture 수정·관련 회귀와 최종 양쪽 전체 T4를 맡는다. 제품22경로의 커밋 판단은 후속 manager 책임이며 G4~G6/G8·다른 의미/문서/L01을 대신하지 않는다.

## 완료 조건

### A1 정확 오류와 종료 계약의 대조

017 manager source-inspected2675파일과 시작 상태를 대조하고 차이의 출처/영향을 기록한다. 실패 ID boundary.test_port_jobs.WindowsJobsContract.test_a_job_resumes_only_once의 실제 result/stderr, 앞선 동일 소스 통과와 미러 통과를 구별한다. JobsContract의 enterContext/addCleanup LIFO와 MARK child의 cwd, WindowsJob.close/terminate/wait/inspect, FakeJob·공유 계약을 읽는다. close의 kill-on-close와 종료 완료를 같은 사건으로 간주하지 않는다.

수리 전 자기 evidence의 작은 실제 Job 관측으로 PID/creation FILETIME·소유 Job·root signal·active count/process IDs·cwd와 cleanup 순서를 보존한다. 기존 실패 당시 상태는 없으므로 새 관측을 그 당시 상태로 서술하지 않는다. 시간 지연만 주입하거나 오류 문자열만으로 원인을 확정하지 말고 실제 미종료/종료 대조를 사용한다. 역사 오류의 재현 빈도를 추정하기 위해 전체 T4를 반복하지 않는다. 기존 실제 실패와 확인된 동기화 공백을 근거로 삼을 수 있으며 역사 race가 그대로 재현되지 않으면 그 사실을 밝힌다.

PR02의 해당 Job 소유/종료 slice만 Git 도입 diff·현재 소비·존재하는010/016 근거에 대조해 유지/교정 이유를 적는다. 전체 PR이나 없는 원보고 counts로 검토 범위를 넓히지 않는다.

### A2 실제 종료를 확인하는 최소 fixture 수리와 회귀

시험이 소유한 Job의 종료·빈Job을 확인한 뒤 핸들·TemporaryDirectory를 정리하도록 현 공개 API를 소비한다. JobsContract.launch의 공통 cleanup과 필요한 real/fake 시험만 최소 수정한다. already been resumed 반려, 시작 전 suspended, 정상 marker 실행, 시작 전 종료, 소유자/동명Job 식별 성질을 유지한다. close의 의미를 runtime에서 새 동기 barrier로 바꾸지 않는다. 핸들 해제는 오류 시에도 보장하되 원오류·종료 확인 실패를 숨기지 않는다.

실제 Windows Job에서 정리 전 root_signaled/active_processes/process_ids와 디렉터리 삭제의 성공을 연결한다. suspended·resumed·이미 종료된 시험 소유 Job 상태를 다루고 fake 쪽도 같은 계약을 따른다. 기존 시험으로 충분한 성질은 재사용하며 단순 구현 순서 복제만 검사하는 테스트를 늘리지 않는다. 외부 OS 경계를 대역으로 가려 실제 오류를 없애지 않는다. sleep만 추가·삭제오류 무시·skip·무조건retry·시간 초과를 성공 처리하는 수리는 금지한다. 관찰 대기에는 실제 종료 조건을 사용하고 시간 경과로 Job을 죽이는 새 정책을 도입하지 않는다.

정확 오류 ID와 boundary.test_port_jobs 및 contracts.test_port_jobs를 공식 runner로 검증한다. 두 모듈의 최종 선택·고유row·passed·exit0와 real/fake 차이, 새 반례가 있다면 수리 전후를 보존한다. 별도 원관측은 최종 동작의 증거이지 새 전체 실행을 대신하지 않는다.

### A3 최종 동일 판본의 양쪽 전체 T4

A2·공식 미러 생성 뒤 정본/미러 각각 --tier T4 --jobs 1 전체 선택을 완결한다. 현재 --list와 고유 실제 row가 전건 대응하고 failed/error/skipped/not_run가 없으며 실제 exit0여야 한다.295를 고정 분모로 쓰지 않는다.016의 별도910파일 baseline을 SHARED_INPUT_BASELINE_SCRIPTS로 공급해 exact2건이 실제로 실행되도록 한다.017 raw companion의 입력/현재 TestCase/WORKER/SNAPSHOT·계측이 불변이면 한정 재사용하며 다시 수집할 의무는 없다.

각 report/adapter-coverage·worker의 요청/run_id/소스/게시SHA·branch DB·부모 합집합과 현 adapter5개의 정보 분모를 확인한다. 정보 도달률의 일치/임계 통과는 요구하지 않는다. 측정complete와 기능합격은 별개다.017의 정확 cleanup 오류, 이전015의12미통과와017 환경7ID를 새 전체 row에 대응시킨다. 현재 소스와 도구/실행 전후해시·PID/시작·종료·exit·원자료를 보존한다. 기존 부분성공의 합산이나 미러 성공으로 정본 전체를 통과시키지 않는다.

### A4 환경·보존·인도와 후속 책임

parent TEMP/TMP/TMPDIR는 저장소 밖 짧은 자기 전용 경로를 사용하고 git rev-parse --show-toplevel이 비저장소를 나타내는지 기록한다. resource worker는 output 하위 scratch를 다시 사용하므로 출력도 자기 evidence/c4·m4처럼 짧게 둔다. 현재 기존 installed probe의 실제 최종 cwd가017 성공 조건241자보다 길어지지 않는지 사전에 경로 구성을 확인한다.241자는 이 환경의 보수적 배정 조건이며 보편적인 Windows 상한으로 문서화하지 않는다. 관련 운전 지침에 parent TEMP와 resource output이 서로 다른 경로 조건이라는 실제 교훈을 필요한 만큼 반영한다. 전역 환경이나 OS 정책을 바꾸지 않는다.

수리 범위 밖 runtime139입력·corpus144경로/150명시SHA·host8원자료/도구·baseline910파일·index/pseudo/T3-store와015~016 제품22경로의 바이트를 보존한다. 이번 shared fixture 변경이 기존 실호출의 승인 성질에 영향을 주는지 명시한다. 미러는 공식 생성기의 사전 예상변경을 writes와 대조한 뒤 생성하고 --check/skill-only를 통과한다. 캐시는 성공 근거가 아니다. 이전 report·raw를 고치지 않으며 역사 실패/미관측 한계, G4~G6/G8·남은 의미/문서/L01·제품22경로 Git마감을 유지한다.

## 판단과 경계

변경은 phase writes의 Jobs 공유 fixture·그 real/fake 시험·시험 운전 지침 및 공식 대응 미러/캐시로 한정한다. runtime windows_job·ports·fakes 구현·runner·측정/과거 baseline·설계/요구·공유 계약·corpus·설치 신뢰/기존 연구·다른 phase·공용 문서·Git/기억·engine은 수정하지 않는다. runtime 계약 위반이 실제 원인이라 fixture만으로 해결할 수 없으면 최소 반례/필요파일/소비자 영향을 finding으로 반환하고 해당 A를 fail/not_run으로 기록한다. 별도 권한 요청 없이 허용 범위의 진단과 수리는 진행한다.

task가 소유한 실제 Job/프로세스·전용 임시 경로만 제어한다. 시스템 전체 프로세스 정리·기존 예약·유료 공급자/학술 호출·graphify 갱신·stage/commit/reset/checkout/push는 수행하지 않는다. 바뀌지 않은 전영역 재검토나 무관한 추가 개선은 이 work에 넣지 않는다.

## 검증 방법

cwd C:\math, Python C:\Users\wogud\AppData\Local\Programs\Python\Python312\python.exe. -u -B와 공식 .claude/.agents/skills/do-math/scripts/run_tests.py를 사용한다. 정확 ID 및 boundary.test_port_jobs contracts.test_port_jobs --jobs 1 --output <자기 evidence의 짧은 새 경로>로 관련 검사를 수행한다. 이후 양쪽 전체 --tier T4 --jobs 1 --output <자기 evidence/c4 또는 m4>를 순차 수행한다. 실제 --list·명령·cwd·환경·선택·row·종료를 남긴다. baseline은 C:\math\docs\do-math\continuous-development-2026-10-13\phases\016\tasks\provenance-baseline\evidence\pre-provenance\scripts 이며 전후 manifest 해시를 확인한다.

총worker3 이하·한 묶음씩, 실행 중 제품/시험 판본 고정. result.json 진행 읽기는 do_math.file_io.read_bytes_shared를 사용한다. 도구 yield/관찰 대기 만료를 실제 실패/성공으로 읽지 않는다. 실패 시 해당 원자료를 보존하고 새 수정/명확한 대조 이유 없이 전체를 반복하지 않는다. 이전 성공 검사는 새 영향/실패가 있는 범위만 다시 수행한다. 마지막 지정 Python으로 check.py report C:\math C:\math\docs\do-math\continuous-development-2026-10-13 018 job-cleanup 을 통과하고 report 경로와 상태를 반환한다.
