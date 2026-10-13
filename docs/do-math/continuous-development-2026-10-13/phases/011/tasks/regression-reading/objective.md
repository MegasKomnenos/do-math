## 목적과 역할

010 host-smoke의 A3를 막는 두 기존 회귀 문제와 reading-limits F2의 구체적인 문구 반례를 수리한다. G3/G7의 실제 취소 경로, G1/G3의 정확한 오류 단언과 누락 없는 읽기 절차를 복구하는 한정 work다. 새 host T5 정본3·미러3의 성공과 reading 조사 완료를 보존하며 전체 G 또는 13-C/L01의 충족으로 확대하지 않는다.

세 시험 파일과 SKILL의 읽기 문단만 다룬다. 문서 전건 검사는 SKILL과 다른 시험을 읽고 공식 미러 생성기는 정본 전체를 읽으며 비용 캐시도 공유하므로 하나의 task로 소유한다. 다른 task나 미완성 결과에 의존하지 않는다. 기존 host 코드와 runtime을 다시 구현하지 않는다.

## 완료 조건

### A1 기존 취소 시험이 현재 실제 포트 계약을 소비

시작 제품 해시를010 manager source-inspected와 대조한다. 관리 커밋과 제품 판본을 구분하고 차이가 있으면 해당 근거의 재사용 범위를 판정한다. `boundary.test_scheduling_call_jobs.CallJobTests.test_real_job_cancellation_uses_owner_judgment_and_collects_once`의 `_job_run` 필수 clock/environment 누락을 현 실제 `real_ports`/environment 계약으로 교정한다. 인접 publication-failure 시험의 현 패턴과 `_job_run` 반환/ModelCalls 예외 처리 원문을 확인한다. runtime에 기본값·fallback을 추가하지 않는다.

owner thread의 시작 callback, 시작 뒤 명시 취소, 정확한 반환 구조/정지 결과, 한 번의 continuation 수집, 빈 실제 Job 및 추가 collect=0을 유지한다. 실패 dict가 tuple 인덱싱 KeyError로 가려지지 않게 기대 반환을 먼저 명확히 검사한다. Job·clock·worker·ModelCalls를 대역으로 가리지 않는다. 기존 실패는010 related 및 baseline-repro-02의 원보고로 유지하고 같은 정확 ID의 새 통과 row를 대응시킨다. 시간 경과 자체를 정상 취소나 종료 성공으로 세지 않는다.

### A2 네 반례가 의도한 오류를 정확히 검사

`structure/test_doc_code.py`의 deferred owner 검사 한 지점과 `sim/test_knowledge_currentness.py`의 RecoveryMaterialTests 세 지점에서 포괄적인 `assertRaises(AssertionError)`를 실제 기대한 반려 원인에 결속한다. 대상은010 F2와 manager review의 원문 위치다. 단일 지점 안에 여러 fault가 있으면 각 fault의 기대 문구/issue 또는 caught.exception의 구체 정보를 구별한다. 임의 AssertionError·넓은 정규식·현재 실패 메시지의 무분별한 복사로 통과시키지 않는다. 기대값은 정상/교란 입력과 실제 검사 계약에서 얻는다.

정상 대조군, wrong/missing owner/method, 복원 오류에서 읽을 수 없는 바이트의 local_path 반례, 일반 continuation/운영 checkpoint를 result_source로 바꾼 두 소유자 반례를 유지한다. 기존 helper/schema/smell_rules와 제품은 변경하지 않는다. 네 문제를 제외하거나 파일을 스캔 모집단에서 빼지 않고 전건 `structure.test_test_smells.SmellTests.test_new_system_tests_have_no_smell`을 통과한다. 관련 문서/운영 복구 성질을 약화하지 않았다는 diff·정상/정확 음성 결과를 남긴다.

### A3 구간 읽기가 머리·꼬리 및 합산 절단을 처리

SKILL의 진입 역할 절에서 긴 문서를 읽는 기존 문단만 최소 교정한다. 온전히 받은 연속 접두 구간 또는 명시 구간별 수신 확인으로 다음 범위를 정하고 중간 공백을 전부 회수한다. 마지막에 보이는 꼬리·끝표지·exit0·파일 해시는 전문 수신의 근거가 아니다. 개별 도구 결과와 최종 합산 출력의 절단을 모두 확인하고 필요하면 구간/동시 출력 수를 줄인다. 긴 한 행에서 일부 문자만 받은 경우도 온전한 행으로 세지 않는다. 기존 필수 문서 순서·판본 재사용·전문 후 다음 문서 이동·내부 역할 stdin 경계는 유지한다.

010의 두 fixture와 16페이지/합산 절단 원자료에 새 문구를 대조해 END:080만 보고81행으로 건너뛰는 반례가 닫히는지 설명한다. 필요하면 자신의 evidence에서만 제한된 실제 읽기를 수행한다. 문구를 그대로 흉내 내는 제품 시험이나 범용 호스트 추론기를 만들지 않는다. 조사 결과는 특정 개발 task의 관측이며 실제 operator의 보편 한도/준수 증명이 아니다.

13-C 원문의 UTF-8 출력 byte 기준, G 기준, 공급자별 운전 host/model/tool/설정은 이 task가 개정하지 않는다. 사용자 답변이 공용 입력에 확정되지 않았다면 기존 기준과 L01 미인증을 유지한다. token/character를 byte로 임의 환산하지 않는다. 새 Claude/모델 세션이나 유료 호출은 수행하지 않는다.

### A4 관련 회귀와 미러를 완결해 인계

수리한 정확 실패 ID와 해당 문서/복원 시험을 먼저 확인한다. 최종 정본에서010 related-results의61개 전체 선택을 포함하고 `structure.test_doc_code`, `sim.test_knowledge_currentness.RecoveryMaterialTests`, `sim.test_role_input_context.OperationalInputTests`, `flows.test_knowledge_impact_retry.UnreadableBeforeReviewTests`, `unit.test_role_input_packaging`, `unit.test_role_input_scoped_packaging`의 관련 문서/복구 범위를 결합해 한 묶음으로 완결한다. 선택은 현재 runner와009의 공식 report.selected에서 확인하고 중복은 제거한다. 전체 일반/T3/변이/유료 T5를 실행하지 않는다. 선택/고유row/실제exit/전후 소스 해시를 대조하고 skip/error/미실행은 성공으로 세지 않는다.

공식 생성기의 계획·실제 변경이 phase writes 안인지 확인하고 대응 미러를 생성한다. 미러에서는 같은 취소 및 문서/복원·smell 성질의 관련 선택을 검사한다. 검사 뒤 비용 캐시만 공식 재동기화하고 --check와 probe_cli --skill-only를 통과한다. 그 과정에010의 아직 미커밋 host 파일은 불변이어야 한다. 전체 생성 범위 밖 변경이 필요하면 자기 판단으로 범위를 넓히지 않는다.

010 host-final/mirror-host 성공의 재사용은 host helper·시험·worker/runtime·실행 경로/도구 조건의 불변으로 설명한다. 이 task는 해당 host 코드를 바꾸지 않으므로 새 실패나 판본 변화가 없으면 OS 실행을 반복하지 않는다. 기존 공급자 runtime124·입력3·양쪽 corpus102경로의 재사용 조건도 유지한다. 외부 문제를 발견하면 정확한 반례·A/G 영향·필요 쓰기 범위로 반환한다. 모든 A와 검사/변경/미검증·자원 정리를 report에 담는다.

## 판단과 경계

모델 gpt-6.1-sol/high. 쓰기는 phase.json에 지정된 세 시험·SKILL·비용 캐시와 대응 미러뿐이다. support/helper·runtime·smell 규칙·공급자/host T5·corpus·생성 규칙·공용 문서·engine·원 보고를 수정하지 않는다. 프로젝트 검사는 이 task만 jobs1로 한 묶음씩 실행하고 실행 중 정본을 고정한다. 자신이 만든 Job/임시 출력만 정리하고 다른 프로세스·연구 인스턴스는 건드리지 않는다.

Git stage/commit/reset/checkout/push, graphify 갱신, 설치/설정/OS 예약 변경, 새 연구 시작·재개·삭제를 하지 않는다. manager가010~011 제품 단위의 검수·기억·Git 마감을 맡는다. 공통 seam의 개정이나 분리된 제공자/소비자가 없어 provides/uses는 빈 목록이다.

## 검증 방법

cwd C:\math, Python C:\Users\wogud\AppData\Local\Programs\Python\Python312\python.exe. 공식 runner에 `-u -B`, 정확 선택과 `--jobs 1 --output <자기 evidence의 새 경로>`를 전달한다. argv/cwd/PID/시작·종료/exit 및 stdout/stderr 원자료와 소스 전후를 보존한다. 실행 중 결과 관찰은 file_io.read_bytes_shared를 사용한다.010 실패 원자료로 이미 입증된 동일 반례를 이유 없이 다시 실행하지 않으며 새 검증 실패 뒤에는 정확 실패와 영향받는 범위만 교체한다.

정본 runner `.claude/skills/do-math/scripts/run_tests.py`, 미러 runner `.agents/skills/do-math/scripts/run_tests.py`, 생성기 `.claude/skills/writing-skills/scripts/build_skill_mirrors.py`, 구조 검사 `.claude/skills/do-math/scripts/probe_cli.py --skill-only`를 사용한다. source hash/선택/row/실제exit가 맞아야 하며 형식 통과를 제품 통과로 대체하지 않는다. 마지막에 `python -B services/continuous-development/check.py report C:\math C:\math\docs\do-math\continuous-development-2026-10-13 011 regression-reading`을 통과하고 report 경로·상태를 반환한다.
