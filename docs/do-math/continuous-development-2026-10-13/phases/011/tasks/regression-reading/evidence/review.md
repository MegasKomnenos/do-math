# phase 011 regression-reading 검증과 인계

시작 HEAD는 start-verification.json에 있으며 source-start의 2,644개 해시는 010 manager source-inspected와 전건 일치한다. 관리 커밋과 미커밋 제품을 구분했고 Git 변경·기존 연구 운전·graphify 갱신·새 공급자 호출은 수행하지 않았다. 최종 제품 변경은 허용된 정본 네 파일과 대응 미러 네 파일, 비용 캐시 두 파일이다. verification-final은 기존 소스의 해시뿐 아니라 네 소스 루트의 파일 집합도 대조한다. changes.diff는 시작 해시와 일치하는 HEAD 바이트(필요한 경우 CRLF)를 기준으로 한 실제 차이다. SKILL은 14행 한 문단만 바뀌고 기존 개행·나머지 행·필수 문서 순서·판본 재사용·내부 역할 경계는 보존됐다.

## 취소와 단일 수집

현 formal._job_run은 필수 jobs/clock/environment를 받아 실제 Job을 보류 상태로 생성하고 on_started 뒤 resume하며 명시 stop에만 terminate한다. 명시 취소 반환 계약은 `(None, stdout, stderr, True)`이다. parallel.ModelCalls는 start callback과 stop 판단을 owner thread에서 수행하고, 계산 예외를 model_call.failed_result의 dict로 바꾸어 continuation에 전달한다. 인접 publication-failure 시험의 entry/real_ports 패턴을 소비해 실제 clock/WindowsJobs/environment를 전달했다. ModelCalls·worker·Job·clock을 대역으로 대체하지 않았다.

시작 callback과 should_stop 모두 owner thread를 단언한다. started가 생긴 뒤에만 should_stop=True다. collect 합계와 continuation 각각 1건, started 1건, tuple 형식과 정확 `(None, '', '', True)`, 빈 실제 named Job, 추가 collect=0을 검사한다. 15초 상한에 도달해 미수집 future가 남으면 실패하며 경과 시간을 성공으로 세지 않는다. finally calls.close와 임시 디렉터리가 자기 자원을 정리한다. 010 related와 baseline-repro-02의 정확 error ID를 canonical/mirror의 새 passed row로 연결했다. 수리 전 반례는 재실행하지 않았고 원보고를 보존했다.

## 네 음성 단언과 기대값의 근거

deferred owner 검사의 정상 mapping과 wrong_owner/missing_owner/missing_method/wrong_method 네 입력을 그대로 유지했다. 실제 OPERATIONAL_INPUT_BOUNDARIES 집합, 해당 클래스의 실제 method와 assert_operational_documents(owner=...) 호출을 검사한다. 집합 및 method 검사에 원인 메시지를 추가했고, 각 교란의 누락/예상 밖 owner, 누락 method, 해당 owner의 실제 문서 검사 부재를 각각 별도의 리터럴로 결속한다. re.escape와 끝 앵커를 써서 넓은 정규식을 만들지 않았다.

복원 오류 반례는 정상·inline 정상과 missing checkpoint/result/output·hash/size 오류 원래 입력을 보존했다. 문서의 조건부 필드는 오류 행에서 local_path를 허용하는 것으로 해석하지 않는다. support.engine_context.assert_operational_documents의 파일 경계 `assertNotIn('local_path', source)`가 local_path 노출을 반려한다. 정확한 키와 `unexpectedly found in` 시작 문구를 검사하고 오류 행의 다른 데이터 전체를 기대 메시지에 복사하지 않는다. 정상 실파일/봉인 바이트, 오류의 원인·관측 hash/bytes, local 파일 부재와 실제 packaging 대조도 유지됐다.

일반 continuation 소스는 같은 execution의 실제 restore_continuation 생산물이다. artifact_ref/snapshot/hash/bytes 등 local_path 외 전 좌표가 정상 recovery result_source와 같다는 추가 대조와 `input/resume-history/` 소유 경로를 확인한다. 정상 recovery 경로는 `input/operational-review/<execution>/`다. 이 조건에서는 기존 checker의 문서·execution·artifact·snapshot 검사가 통과하고 local_path 접두 검사만 false이며, continuation 파일 자체는 input 안에 있고 정상 봉인 바이트와 같다. 따라서 captured exception의 정확한 args `('False is not true',)`를 그 경로 교란 및 정상 대조와 함께 결속한다. 임의 AssertionError를 받는 것만으로 통과하지 않는다. 이 메시지를 새 제품 오류 코드로 승격하거나 checker를 수정하지 않았다.

운영 checkpoint를 result_source에 넣는 교란은 별개다. checker의 result artifact_ref 기대는 execution.result_ref이고 실제 교란은 operational_evidence.checkpoint_source.artifact_ref다. caught.exception의 문자열 차이에 두 완전한 artifact 좌표의 `-`/`+` 행을 검사해 local path 반례와 구별했다. 앞선 정상 _context/파일/해시와 일반 continuation 대조군을 유지했다. helper/schema/smell_rules/runtime은 불변이며 scan 모집단을 줄이지 않고 전건 smell 검사가 양쪽에서 passed다.

## 읽기 문구와 기존 실제 관측

reading-verification.json은 010의 두 원 fixture와 capped 결과, 16개 실제 수신 페이지 및 합산 절단 자료를 다시 대조한 결과다. ASCII는 온전한 접두 1~17 뒤 18~63(46행)이 누락됐고 Unicode는 1~15 뒤 16~65(50행)가 누락됐다. 둘 다 END:080이 보이므로 81행으로 가면 누락이 남는다. 새 문구로 접두 다음을 정하면 각각 18/16행부터 이어 읽어야 한다. 명시 구간 방식에서는 기존 10행씩 16페이지의 전 160행이 원문 순서·문자와 정확히 맞고 모든 공백이 회수된다.

합산 150-token 결과는 내부 두 10행 결과가 완전했지만 최종 수신에서 ASCII 4~10, Unicode 1~5행을 완전히 전달하지 않았다. 새 문구는 개별/합산 절단을 별개로 확인하고 구간 또는 동시 출력 수를 줄이도록 한다. 부분 문자만 받은 긴 한 행을 온전한 행으로 세지 않도록 명시했다. 파일 해시·exit0·끝표지는 전문 수신·독해의 근거가 아니다. 이 task가 새 operator의 보편 용량이나 절차 준수를 시험한 것은 아니다. 제품에 문구를 그대로 흉내 내는 시험이나 범용 host 추론기를 만들지 않았다.

13-C의 원문 UTF-8 출력 byte 기준은 그대로이며 단위 환산을 하지 않았다. 실제 공급자별 operator host/model/tool/유효 설정 및 Q1/Q2 결정은 공용 입력에 확정되지 않았다. L01/13-C의 읽기 한도는 계속 미인증이며 B-20의 AI 준수 한계도 유지된다. 새 Claude/모델 세션이나 유료 호출은 없다.

## 최종 회귀·미러와 기존 실경계 재사용

공식 runner의 --list와 009 report.selected를 대조해 010 related 61개 및 지정 문서/복구 75개, 합계 136개를 확정했다. focused는 6건 모두 passed다. 최종 정본과 미러는 각각 136선택/136고유row/136passed·exit0이며 skip/error/미실행은 없다. 실행 중 changed_during_run은 없고 양쪽 각 867개 Python 해시가 최종 실제 파일과 같으며 문서 등 전체 소스 전후도 캐시 외 불변이다. 실제 argv/cwd/PID/시각/exit와 stdout/stderr는 각 execution.json/log에 있다. 비용은 canonical 114.9초이며 미러 실제 시간은 verification-final에 기록했다. 정상/정확 음성 단언을 줄여 예산에 맞추지 않았다.

공식 미러 계획 5변경과 실제 생성의 5변경이 동일하고 모두 writes 안이다. 미러 검사 뒤 비용 캐시 한 파일만 공식 재동기화했다. --check는 1,307파일 드리프트 없음, probe_cli --skill-only는 verified/exit0이며 이 두 명령의 제품 변화는 0이다. 생성 규칙·manifest·010의 host 파일은 불변이다.

010 host-final/mirror-host의 각각 3passed 및 원자료 8개를 해시/판정으로 대조했다. host helper·시험·worker/runtime·읽기 지급 코드·실행 경로는 그대로이며 Python/pythonw 바이너리 SHA와 Python 판본, PowerShell 경로/판본은 기존 자료와 같다. PowerShell의 당시 바이너리 SHA는 없으므로 실행 파일의 역사 바이트 동등성을 주장하지 않는다. 경로/판본과 입력/실행 조건에 새 변화 근거가 없어 이미 통과한 host T5를 반복하지 않았다. 이번 관련 boundary 회귀는 별도로 실제 실행했다.

공급자 runtime124·smoke 입력3·양쪽 corpus102경로, 대응 미러와 규칙/속성이 보존됐다. 승인된 기존 공급자 실호출·명시 SHA/Git raw-clean의 한정 증거는 유지한다. 이번 회귀로 전체 일반/T3/극단 변이, Lean/Mathlib·실제 예약 등록/발화/해제·학술 연쇄 또는 프로젝트 최종 review를 대신하지 않는다. Git 마감과 기존 발견의 최종 처분은 manager 책임이다.
