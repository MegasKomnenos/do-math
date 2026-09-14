# do-math CLI 실행 계약

이 문서는 `do-math-cli/1` 기능 판본 2의 운전·기록 계약이다. 통합 설계의 연구 목적과 판정 분리는 유지하되 특정 v9 wire 형식·OS 수단을 완료 조건으로 삼지 않는다. 기능 목적에 필수인 동작은 다른 수단을 쓰더라도 실제로 연결하고 검증한다.

목적별 완료와 남은 증거는 [기능 완료 대응](../../../../docs/do-math/기능-완료-대응.md)이 추적한다.

## 정본과 판본

인스턴스별 Git ref 하나가 `research/instance.json`, `runtime/state.json`, `runtime/artifacts/`를 한 커밋으로 가리킨다. 인스턴스별 writer lock 하나만 정본을 바꾼다. 저장된 `contract_id`와 `feature_version`을 검사하며 알 수 없는 미래 판본을 현재 코드로 해석하지 않는다.

각 execution은 시작 때 engine source, 역할 문서와 입력 manifest의 hash를 고정한다. 실행 중 설치 파일이 바뀌면 결과 적용을 멈추고 pause한다. 과거 execution·artifact는 생성 당시 판본과 함께 보존한다. 별도 변환 없이 오래된 결과를 새 계약 결과로 다시 쓰지 않는다.

## 상태와 판단

인스턴스 상태는 ready, running, paused, waiting, budget_exhausted, completed, closed다. 과제는 planned, ready, needs_revision, performing, waiting, assessing, completed, closed다. 활동은 active, finished, unresolved, 실행은 starting, running, ended를 쓴다. 실행 종료, 활동 종료, 과제 완료, usable K, mathematically_solved, academic validation은 서로를 대신하지 않는다.

형식 타당성, 해설 동일성, 목표 충족, 행동 허가, 실행 상태는 각각 지정된 검사와 기록으로만 성립한다. Command exit 0과 schema 통과는 다른 판단의 증거가 아니다.

## 입력·컨텍스트·산출

각 AI execution은 새 Codex session과 workspace를 받는다. SKILL·GLOSSARY·역할 계약·output schema, 현재 목표·정책·action·과제·필수 proposal·review 자료를 고정한다. 원자료는 `input/` 아래에 raw bytes와 path·SHA-256·size manifest로 복사한다.

큰 tasks·knowledge·history·sources는 canonical catalog 파일에 전건 보존한다. Prompt가 한도에 들어가지 않으면 최근 history 창과 상세 배열을 exact source ref로 바꾸되 mandatory key와 ready task universe ID를 유지한다. Mandatory 자료 자체가 한도를 넘거나 필수 ref를 회수할 수 없으면 실행을 시작하지 않고 실제 크기·원인·다음 행동을 기록한다.

종료 장벽 뒤 `input/`, `.git`, `__pycache__`를 제외한 모델 작성 source·실험 데이터·checkpoint를 bytes 그대로 수집한다. Required path 부재, 변경 중 파일, reparse·root 탈출, read error, 수집 한도 초과를 구별한다. 제출되지 않은 부분 파일을 최종 의미 결과로 추측하지 않는다.

## 연구 흐름과 의무

후보 준비는 질문·범위·입력·기대 변화·완료 기준을 가진 과제를 만든다. 계약 검토는 현재 goal·policy·task revision과 contract hash에 결박된다. 계획은 ready 과제 전건을 선택 또는 보류하고 assessing·waiting 과제의 정확한 완료 기준을 판정한다.

Goal·policy·source·지식 변경은 실제로 의존한 미완료 과제의 currentness를 갱신한다. Scope transfer는 원 과제의 남은 의무를 대상 과제의 completion criteria에 합쳐야 한다. Candidate revision도 기존 미완료 의무를 근거 없이 삭제하지 않는다.

작업과 운영 예산은 CLI execution 시도 단위로 분리한다. 실패·중단도 소비에 포함한다. CLI turn usage는 별도 관찰값이며 공급자 내부 호출별 예약·원격 사용량을 보증하지 않는다. 실행은 순차 배정하여 동시 slot 교착을 피한다.

## 지식·관계·현재성

Raw source 수입과 의미 candidate 수입을 구별한다. Source는 접수 시점 bytes·hash·name·revision·provenance를 보존한다. Structured knowledge import는 등록된 kind와 dependency를 검사하고 같은 ID revision history를 유지하며 항상 candidate로 시작한다. Lean source가 있으면 formal check, 그 뒤 identity review를 통과해야 usable K가 된다.

Knowledge와 relation kind는 의미와 고정된 제약을 가진 definition registry에 등록한다. Custom kind를 허용하지만 정의 없이 새 token을 사용하지 않는다. Supports·challenges·analogous_to 같은 research relation은 실제 evidence가 있는 연결이며 함의를 보증하지 않는다.

Mathematical relation은 정확한 `{kind, source, target, confirmed_scope}`를 적은 `relation_claim` proof record를 요구한다. 그 proof record의 formal result가 current·verified이고 동일한 claim을 전체 identity review한 effective assessment가 있어야 mathematical authority를 가진다. 무관한 K나 assessment를 붙여 relation을 인증할 수 없다.

지식 개정은 이전 revision을 history에 보존하고 candidate·새 formal·새 review로 돌아간다. 철회는 삭제하지 않는다. Dependencies와 실제 knowledge ID 근거만 따라 downstream K 사용, 과제 assessment, 목표 판단을 정지한다. 파일 path·snapshot·slot 같은 source locator를 존재하지 않는 K로 오해하지 않는다.

## 형식 검사와 동일성 검토

Lean 검사는 실제 executable·version·hash, project manifest와 dirty fingerprint, source hash, declaration signature, 전이적 axiom 의존을 보존한다. Allowed axiom 밖의 의존과 `sorryAx`를 거부한다. 형식 검사는 source 실행의 모든 host 효과나 자연어 의미를 보증하지 않는다.

동일성 검토는 initial batch를 서로 숨긴 채 전건 봉인한다. 이의가 없고 모두 complete match면 끝낼 수 있다. 이의가 있으면 organize가 원 finding refs를 issue로 묶고 독립 judge 3명이 issue와 proposal 전체를 판정한다. 기각·미해결 쟁점에는 원 slot이 답하고 같은 judge들이 재심한다. Round·예산 상한에서 unresolved와 followup을 보존한다. 새 proposal revision은 이전 판정을 자동 승계하지 않는다.

K 사용에는 exact formal source·활성 trust environment·effective identity assessment와 dependency currentness가 모두 필요하다. 어느 한 축이 정지되면 과거 결과를 삭제하지 않고 `use_suspended` 원인을 typed history로 보존한다.

## 신뢰 환경

Trust environment는 toolchain fingerprint와 allowed axioms를 등록한다. 최초 실제 compiler 결과는 활성 환경을 세울 수 있다. 환경 무효화는 그 환경을 쓰는 K와 실제 downstream 판단을 정지한다.

새 환경 전환은 고정 target K 전건을 같은 source·basis에서 실제 재검증한다. 전건이 verified일 때만 active 환경을 바꾸며 실패하면 기존 환경 또는 무환경 정지를 유지한다. 성공은 이전 환경 원인만 해소하고 semantic·dependency·원인 불명 legacy 정지는 자동 해제하지 않는다. Candidate·withdrawn을 formal 결과만으로 verified로 올리지 않는다.

## 관찰·checkpoint·복구

실행기는 JSONL 사건, tool 진행, idle 시간, checkpoint와 worker observation rule을 추적한다. 조건이 발생하면 operational review를 열고 동일 관찰을 중복 소비하지 않는다. 작업자는 `checkpoint.json`에 이미 얻은 사실·근거·시도·남은 일을 기록한다.

Pause·close·권한 또는 입력 currentness 변화·기한 도래는 stop request를 기록한다. 새 연구를 시작하지 않고 허용된 checkpoint grace 뒤 Job을 종료한다. Root signal·active process 0·빈 PID 목록을 모두 확인한 뒤 산출을 수집한다. 원격 termination·provider operation ID는 확인할 수 없으면 unknown으로 남긴다.

실행기 재시작은 미종료 execution workspace와 checkpoint를 회수하고 execution_incomplete로 끝낸 뒤 원래 action을 recovery basis와 연결한다. Running external operation은 unknown으로 보존한다. 완료된 외부 효과나 비가역 작업을 추측해 반복하지 않는다.

## 사용자 결정·대화·외부 행동

Control inbox는 요청 전달 통로이며 정본이 아니다. Decision·knowledge·source·trust·external·conversation 요청은 접수 ID와 bytes에 결박된다. 적용 시 revision·대상 상태가 바뀌었으면 `effect=rejected`와 이유로 소비한다. 같은 실패 요청이 inbox를 영구히 막지 않는다.

Conversation은 ID·generation·lease·disconnect policy를 가진다. Heartbeat는 현재 generation만 갱신한다. Detach·lease 만료는 lost 사건을 한 번 기록하고 pause 정책이면 실행 정지를 요청한다. Continue-authorized는 기존 grant 범위만 유지한다.

External HTTP operation은 사용자 grant의 origin·method·path·credential environment 이름에 결박한다. Prepared와 running을 전송 전에 저장하고 confirmed·failed·unknown을 구별한다. HTTP 응답 확보와 2xx 성공 여부도 별도 필드다. Unknown은 명시적 reconcile 전 재시도하지 않으며 같은 operation ID는 같은 request hash·idempotency identity를 유지한다.

명시적 retry는 failed·cancelled에만 적용한다. 이전 전송이 가능했으면 현재 grant의 멱등 재시도 허가를 확인한다. 요청·멱등 키와 이전 결과 이력은 유지하고 새 실행을 배정한다. HTTP 응답 없는 reconcile은 성공 여부도 별도 boolean 근거로 기록한다.

## 목표와 학술 후속

Goal audit는 현재 usable K·과제 결과·정책·source·review basis에 결박된다. 과거 stale audit는 새 goal basis를 무효화하지 않는다. 수학 목표는 usable K 없이 mathematically_solved가 될 수 없다.

Academic requirements가 없으면 학술 후속은 not_applicable이다. 요구가 있으면 mathematically_solved 뒤에도 current solution basis와 requirement revision에 결박된 assessment를 수행한다. 모든 요구가 satisfied여야 academic validation completed다. 외부 거부는 해결·근거와 함께 별도 관리하며 형식 결과를 자동 철회하지 않는다.

요구의 required_inputs는 실제 과제 입력에 합친다. External effects는 해당 과제·요구 판본·해결 근거·효과 ID에 결박된 confirmed·succeeded 영수증 전건을 확인한다. 같은 요구가 바뀌거나 해결 근거가 변하면 과거 수행과 전송을 자동 승계하지 않는다. 전송 전에도 이 현재성을 다시 검사한다.

## 검증과 한계

2026-09-14 초기 CLI1의 실제 9 AI·1 formal 흐름과 당시 97개 회귀는 이전 판본의 증거다. Feature 2는 [별도 증거 묶음](../../../../docs/do-math/구현-검증-2026-09-14/feature2/README.md)에 실제 CLI 18회·Lean 1회의 목표·학술 완료, 이의 왕복, 의미 반례, 관찰·정지와 신뢰 전환을 보존한다. 각 사례의 합성 선행조건·실제 호출·동결 소스·검사 범위를 구별한다. 전체 회귀 261건 중 260건과 마지막 변경 관련 45건이 통과했고, symlink 생성 권한이 필요한 1건은 환경상 건너뛰었다.

Windows Job의 로컬 수명 보증과 host 파일·network·credential 격리는 별도다. 현재 기본 CLI는 `danger-full-access`와 승인 정책 `never`로 기존 사용자 권한에서 실행한다. 실제 쓰기가 실패한 elevated·unelevated 제한 모드를 실행의 선행조건으로 두지 않는다. 역할 경계는 순차 실행, 별도 session·workspace, 선별 입력과 peer-result 비제공으로 운전한다. 통계적 독립성이나 모든 host path·network·credential 접근 차단을 보증하지 않는다.
