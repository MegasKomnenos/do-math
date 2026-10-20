# 실행 입구의 T3 남김 처분을 현행 계약에 맞춰 마무리

사용자 목표는 결함이 시험을 빠져나가는 기제를 막으면서 실제 제품을 사용할 수 있게 하는 것이다. g5-entry-io가 확보한 직접 child·동결 runtime의 동작 증거를 재사용하여, 원본 T3에 남은 script/import/frozen 13arc/25행을 원설계 5.5와 현재 코드에 맞게 처분한다. 같은 child를 다시 실행해 같은 측정상 남김을 보고하는 작업이 아니다. 필요한 구현·시험·설명·미러를 이 task에서 함께 끝낸다. 숫자를 지우는 것 자체가 완료 조건은 아니다.

## 입력과 소유

SESSION_JSON, task.json, inputs/context.md·plan.md·seams.md, 자기 workspace의 do-math AGENTS.md와 scripts/tests/시험-지침.md를 읽는다. managers/0077/review.md·verification-review.json, g5-entry-io의 report.json·evidence/judgment.md·gap-disposition.json과 필요한 원보고, 자기 gap-scope.json이 직접 입력이다. 원설계 C:/math/docs/do-math/시험-재편-2026-09-29/설계.md의 5.5와 10절 측정 한계, 3.3/A22, records/sources/storage-scope-direction-2026-10-15.md를 적용한다. records/docs는 읽기 전용이고 상대 제품 경로는 자기 workspace다.

실제 선행은 g5-entry-io 하나다. g5-core-rest·g5-trust-rest는 진행 중이며 정의와 입력을 바꾸거나 미완성 결과를 가져오지 않는다. core/formal/trust/knowledge 및 공용 이음새 문서·층 목록·branch_gate/선택색인·시험 실행기는 읽기 전용이다. task.json의 writes는 허용 상한이며 전수 수정·실행 quota가 아니다.

## 맡은 결과

1. 직접 script/bare import의 12arc/24행을 현행 명령 생산자와 연결해 판단한다. 대상은 claude_worker/codex_worker의 직접 root, control_server의 import·submit_draft import·main, control_transport의 bare import, operator_bootstrap의 독립 dispatch/main, probe_cli main이다. codex_adapter.LocalCLIAdapter.start와 control_server.mcp_server_config가 실제 caller이며 기존 boundary 시험이 입력 처리·영수증·기동 신원과 정산을 관찰했다. package로 호출할 수 있는 일반 처리 함수와 새 인터프리터의 import/bootstrap만 의미가 있는 구간을 구별한다. 원설계 5.5의 의도적 인프로세스 미도달에 해당하면 정확한 구간에 같은 행 사유를 적은 제외를 적용할 수 있다. 해당 실제 T4 증거와 책임을 설명에 연결한다. 기존 codex_worker의 direct-import 제외는 비교할 현재 사례이지 모든 남김의 자동 면제 근거가 아니다. 정상 처리·반려/검증 로직까지 포함하는 넓은 함수·모듈 제외는 하지 않는다. 이미 도달하는 반대쪽 분기까지 제외되는 경우에도 정확한 범위와 근거를 밝힌다.
2. scheduled_operator.run_engine의 인접 bootstrap-manifest 자동 선택 1arc/1행은 실제 동결 파일로 동작이 확인됐으나 원본 경로 측정은 아니다. 단순 파일 복사로 coverage 경로가 달라졌다는 이유만으로 일반 판단 로직을 제외하지 않는다. execute가 startup 근거를 얻고 run_engine이 manifest를 다시 찾는 현재 관계, operator_bootstrap.main의 bootstrap_evidence 전달, 명시 manifest API와 실제 caller를 확인하여 불필요한 중복/암묵적 결합을 줄일 수 있는지 먼저 판단한다. 자연스러운 현재 계약으로 단순화할 수 있으면 실제 caller·관련 시험·CLI 설명까지 함께 바꾼다. 시험 전용 매개변수·새 framework·제품 globals patch·가짜 __file__/co_filename·coverage 수동 매핑은 만들지 않는다. 동결 runtime/원 설치 신원, manifest 검증, 다른 설치 반려, 정확한 live child argv와 HOLD 기동 기록은 유지한다. 필요한 최소 T3로 실제 원본 코드의 판단을 확인하고, script 경계 책임은 기존 T4 근거를 재사용한다. 명시 계약상 더 타당한 처분이 있으면 그 이유를 설명한다.
3. gap-scope의 13arc/25행 각각을 현재 위치와 도달·제거·사유 있는 제외·미해결로 연결한다. 분모 변화와 원본 raw 도달, 별도 child/동결 행동 증거를 구분한다. T4 자료를 T3 report/coverage/함수진입/index에 합치지 않는다. 최종 fresh T3 성공을 미리 선언하지 않는다. 근거 있는 처분을 찾지 못한 항목은 정확한 이유를 남기고 partial로 보고하며 숫자를 맞추기 위해 강제 제외하지 않는다.

## 이 작업에 넣지 않는 환경 남김

context_store의 실제 파일 symlink omission과 file_io의 실제 POSIX 경로 6arc/10행은 별도 환경 미충족이다. 동일 호스트 WinError1314와 WSL2 HCS_E_HYPERV_NOT_INSTALLED 관측을 재사용하며 권한/WSL probe를 반복하지 않는다. 현행 지원 코드에 있으므로 호스트 부재만으로 제외하거나 POSIX 지원을 폐기하지 않는다. 이 두 모듈은 읽기 전용이며 새 환경·권한/도구 설정 변경을 하지 않는다. 적합한 실제 환경 확보 뒤 필요한 작은 확인으로 이어질 조건을 현재 설명에서 유지한다. 이 환경 미완료는 script/frozen 처분을 막는 선행조건이 아니다.

## 최소 확인과 제출

시험슬롯1·--jobs 1, 다른 두 task와 총시험worker3 이하다. 실행 코드를 바꾸지 않은 구간은 현재 원보고·SHA와 정적 판단을 재사용한다. 제외 주석을 바꾸면 정확한 범위/같은 행 사유와 기존 구조 규칙을 확인한다. 실행 코드를 바꾸면 해당 동작의 가장 작은 공식 선택을 한 번 실행하고 실패/남은 불확실성에 필요한 경우만 추가한다. 경계 명령/적재가 달라진 경우에만 해당 작은 로컬 T4를 재확인한다. 전체 G4/fresh 전체 T3·전체 변이·전체 T4/T5·유료 모델/실예약·공용 설치/권한 변경은 범위 밖이다. 최종 관문을 생략하거나 임계값을 완화하지 않는다.

T3가 실제 Git root를 필요로 하면 g5-entry-io/evidence/prepare.py 또는 g5-full/evidence/prepare.py를 참고해 자기 workspace의 독립 .git/실제 소스 기준 로컬commit만 사용할 수 있다. 시작/준비 뒤 bytes와 실제 root/HEAD를 남긴다. 공용 Git·다른 .git 복사·가짜HEAD·global설정·remote/push는 하지 않는다. 기존 GIT_CEILING_DIRECTORIES를 보존하고 자기 부모와 외부 짧은 temp root를 추가한다. 자기 HEAD는 공용 main/성공 인증이 아니다.

원명령/cwd/관측exit·stdout/stderr/report/coverage·선택/고유행·fixture·실행 전후 SHA를 필요한 실행마다 보존한다. 서로 다른 선택/판본은 전체 통과로 합산하지 않는다. 소프트 비용 초과를 시간만의 실패·중단·skip으로 처리하지 않는다. 생성 cache/index/store는 보존 뒤 시작 bytes/부재로 복원한다. 공통 codec·저장 검증·기존 업무 증거를 재사용하고 가족별 전필드/새 reader/옛 head quota·장기 감사를 만들지 않는다.

evidence/judgment.md와 report.json에 사용자가 얻는 결과, 유지/축소한 구조, 실제 확인/미확인, 각 남김 처분을 담는다. 설명은 허용된 references/CLI-실행-계약.md와 해당 docstring에 묶고 공식 build_skill_mirrors.py로 대응 미러를 갱신·check한다. 공용 소스·context/plan/seams·queue/state·engine·다른 task·기존 연구·graphify는 수정하지 않는다. python C:/math/services/async-development/check.py report C:/math/.async/dm g5-entry-gate를 통과시킨다.
