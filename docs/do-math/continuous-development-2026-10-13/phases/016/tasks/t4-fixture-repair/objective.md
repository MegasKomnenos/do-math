## 목적과 역할

015는 T4 측정을 구현했으나 양쪽295건에서6error·4failed·2skip이 남았다. 이 task는 G1/G3/G7의 정확6error·4failed를 현 계약에 맞는 fixture와 실제 OS 관측으로 해결한다.015의 runner/측정 성과는 유지한다. 병렬 provenance-baseline은 과거 비교 입력만 준비하며 그 산출물을 이 task에서 읽거나 기다리지 않는다. 전체 T4와 두 skip 비교는 후속 연결 task 책임이다.

## 완료 조건

### A1 시작 판본과 반례의 실제 원인

015 manager source-inspected와 시작 소스를 대조하고 verification.suites의 정확 ID/원trace를 읽는다. formal_consumer4·lean_storage2는 installed_request의 nonempty fingerprint/empty content, observation_real_job은 미선언 ok/닫힌 schema, WriterLock child는 backend 부재, archive preview child는 ports/env 부재다. 현재 공개 정의와 fixture 입력에서 각각 확인하고 기존 원red가 현재 소스와 같으면 재사용한다. 불명확하거나 새 음성 단언이 필요할 때만 최소 red를 수행한다. 소스·원보고·실행 관측과 추론을 구별한다. 해당 fixture/콘솔 도입 Git diff와 기존010~012 검수의 관련 slice만 대조해 유지/교정 범위를 정한다. PR 전체나 사라진 원보고 counts를 새로 승인하지 않는다.

### A2 현재 계약의 fixture 수리와 정확 성공

installed_request의 기록은 실제 identity의 fingerprint/content 모집단 및 원바이트 의미에 맞는 현재 producer로 만든다. 신뢰 승인·설치 기록을 바꾸거나 content 검사를 무력화하지 않는다. 이미 있는 support/trust_inputs·knowledge_installed_lean의 정본을 재사용하고 의미가 같은 규칙을 복제하지 않는다. 합성 부분과 실제 compiler/저장/authoritative consumer 경계를 명시한다. observation fixture는 원 의미 schema와 현재 Codex 전송/수신을 함께 맞추며 실제 Job 종료·지연 batch 적용과 ok=true 단언을 유지한다. WriterLock의 자식도 현재 필수 backend를 전달해 실제 lock 경쟁과 해제 후 획득을 검사한다. zip preview 자식은 필요한 실포트/환경을 자기 프로세스에서 구성해 실제 archive formal의 동일 checker bytes와 errors=[]를 검증한다. TypeError/NameError나 failed 상태를 정상 기대값으로 바꾸지 않는다.

정확9개 fixture 오류/실패가 새 공식 row에서 passed여야 한다. 해당 기존 시험의 결과/근거/현재성·바이트·identity·실제 Job/컴파일 단언을 보존한다. 쓰기 범위 안에서 필요한 최소 보강만 허용한다. 제품 runtime 변경이 필요한 반례는 별도로 반환하고 해당 A를 통과로 만들지 않는다.

### A3 Windows 관측의 원인 판별과 재검증

015 F6의 real_git_descendants는 첫 정본에서 passed, 최종 양쪽에서 store.publish/update-ref의 stdin DuplicateHandle WinError6이었다. 현재 같은 pythonw probe가 AttachConsole/FreeConsole 뒤 저장하는 순서가 있지만 원인은 아직 가설이다. 정확 ID의 child stdout/stderr·핸들 관측과 정상 대조를 보존하고 실제 제품 실패인지 시험 관찰자의 부수 효과인지 판별한다. 관측을 별도 자기 child로 분리하거나 명시 I/O를 쓰는 수리는 계약/원인 근거가 있을 때만 수행한다. 실제 Git/자손·양성 console 대조·visible window 없음·binary 저장 성질을 대역이나 무조건 retry/skip으로 가리지 않는다. 원인이 범위 안이면 수리 후 정확 ID를 검증하고 원인이 runtime에 있으면 최소 재현·필요 파일·기대/실제를 반환한다.

bootstrap-info의 첫 WinError5와 최종 양쪽 passed를 구별한다. 지정 관련 묶음에서 두 bootstrap-info ID와 실제 freeze/원설치·manifest·반려를 확인한다. 관측 결과가 통과하면 새 근거의 범위만 인정하며 과거 원인 규명을 주장하지 않는다. 재현되는 결함이면 범위 안 수리 또는 정확 후속 조치로 보고한다.

### A4 지정 회귀·미러·보존 인계

정본과 공식 미러에서 다음 모듈의 실제 선택/고유row/exit·소스 전후를 확인한다: boundary.test_knowledge_formal_consumer, boundary.test_knowledge_lean_storage, boundary.test_observation_real_job, boundary.test_scheduling_host_processes, boundary.test_scheduling_background_processes, boundary.test_submission_lean_preview, boundary.test_operator_bootstrap_info. support fixture를 직접 검증하는 기존 unit.test_trust_environment, unit.test_knowledge_storage_roundtrip 및 structure.test_test_smells를 포함한다. 단순 참조 검색 전체를 새 실행 범위로 만들지 않는다. 바뀐 fixture의 추가 직접 소비자는 AST/정의·import를 확인하고 새 구체적 위험이 있을 때 정확 ID만 추가한다. 같은 소스의 이미 성공한 관련 묶음을 이유 없이 반복하지 않는다.

공식 미러 생성 전 예상 변경을 writes와 대조하고 정본/미러의 지정 회귀 뒤 비용 캐시만 동기화해 --check와 skill-only를 확인한다. runtime·015 runner/측정·공급자/host/Lean/예약/학술 입력·corpus 원바이트의 보존과 기존 실호출 재사용 한계를 기록한다.015의12제품 원바이트 archive와 현재 변경을 구별하고 Git 마감은 manager에 맡긴다. P10/P11 두 비교와 정본/미러 전체 T4, 전체 일반/fresh T3/변이·최종 review는 수행하지 않았음을 명시하고 후속 연결 책임을 넘긴다.

## 판단과 경계

phase.json의 정확 fixture/경계 시험·비용 캐시와 공식 대응 미러만 수정한다. 필요한 helper의 내부 구현은 현재 공개 검사를 만족하는 범위에서 재량이다. runtime·runner·측정·corpus·설치 신뢰 기록·제품 요구·서비스·공용 문서·다른 task 자료·과거 보고는 변경하지 않는다. 실제 compiler/Job/Git·시험 전용 새 workspace와 임시 프로세스는 사용할 수 있다. 유료 공급자·실예약 변경·학술 검색·기존 연구 재개·권한 상승·graphify·Git stage/commit/reset/checkout/push는 하지 않는다. 과거 baseline task는 시험/제품 import를 하지 않으므로 이 task가 공식 시험/미러/캐시의 유일한 소유자다.

## 검증 방법

cwd C:\math. Python C:\Users\wogud\AppData\Local\Programs\Python\Python312\python.exe. 공식 정본/미러 scripts/run_tests.py를 -u -B, 정확 ID/모듈, --jobs 1, --output <자기 evidence 새 폴더>로 사용한다. T4 측정도 확인할 때 boundary 선택에 --tier T4를 붙이고 unit/structure는 별도 명령으로 실행한다. 총 worker3 이하, 한 묶음씩, 실행 중 제품/시험 소스 고정. command/PID/시작/종료/exit·전후 SHA와 원보고/실제 child 관측을 보존한다. 진행 result는 read_bytes_shared로 읽으며 대기 도구 yield나 시간 경과로 실패/성공을 만들지 않는다. 실패는 원인 확인 후 필요한 경우만 재실행한다. 마지막 check.py report C:\math C:\math\docs\do-math\continuous-development-2026-10-13 016 t4-fixture-repair를 통과하고 report 경로/상태를 반환한다.
