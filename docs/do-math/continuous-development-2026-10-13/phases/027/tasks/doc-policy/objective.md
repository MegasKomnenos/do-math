## 목적과 역할

026의 고정판 조사에서 확인된 네 finding(policy F2/F3, role F1/F2)을 한 변경으로 통합한다. 문구 두 곳과 정책의 직접 저장 단언, 현재 문서에 있는 역할 단계·부분 JSON·operator mode의 검사 공백을 닫는다. 공유 doc_code/structure 검사·미러·관련 회귀를 한 번의 최종 판본에서 검증한다. N02 유지 판정과 P01~P11/PURE를 다시 구현하지 않는다.

## 완료 조건

### A1 정확한 문구 두 곳

026 source-inspected와 시작 SHA를 먼저 대조한다. 초기화-운전.md182의 adopt_default_review_policy는 현재 config.reviewers/review_rounds로 기본 방침을 생성·채택하고 실제 내용 해시를 저장한다는 설명으로 교정한다. 명시 review_policy를 함께 주면 그 객체를 사용하는 예외와 stale config/probe 절차는 유지한다. 독립-운영.md15의 operator probe는 정상 관찰의 model_called=false와 HOLD·상태 조회 실패 등 조기 반환을 구별한다. 모델 호출이 없다는 성질을 모든 반환의 필수 marker로 바꾸지 않는다. runtime과 권한은 바꾸지 않고 공식 미러에 반영한다.

### A2 기본 방침의 실제 채택과 저장

sim/test_initialization_controls.py의 기존 InitialAdoptionTests 경로를 이용한다. 현재 설정 reviewers=3/review_rounds=2, 기존 review_policy 부재 및 다른 유효 객체의 두 경우에서 default 채택이 minimum_initial_slots=3, round_limit=2, activity_execution_limit=17, judge_slots=[judge-0, judge-1, judge-2], required_perspectives=[], overflow_disposition=unresolved를 생성하는지 독립 기대값으로 검사한다. 같은 builder를 다시 호출해 기대를 만들지 않는다. 명시 policy 동시 제공의 우선도 실제 경로로 확인한다. 실제 채택/저장과 재시작의 객체·adoption.review_policy_sha256를 대조하고 기존 stale config 반려·정책 hash 불일치 활성화 missing을 유지한다. 직접 내부 helper 호출로 충분한 필드 검사와 공개 control/저장/복원을 구별해 적절한 기존 fixture를 쓴다.

### A3 연결 정책의 양쪽 저장

sim/test_lifecycle_engine_public.py의 실제 공개 conversation 경로에서 instance continue_authorized, 명시 pause attach, 새 generation의 정책 생략, 반대 명시 continue_authorized와 다시 생략을 확인한다. 매 단계 instance.conversation_loss_policy와 runtime.conversations[id].disconnect_policy를 각각 독립 기대와 비교한다. generation/source_ref, 저장 및 restart 후 양쪽 값도 직접 확인한다. 현재 instance 소비가 잘못된 연결행 정책을 가리지 않게 한다. 기존 lease의 전달 시각/정확 만료, 동세대 반려, resume 필요·원문 재전달 원자성을 유지한다. runtime 수리가 필요한 실행 반례가 생기면 범위 밖 변경 대신 finding으로 반환한다.

### A4 문맥을 구별하는 문서 검사

role-contract-names의 repair-candidates.R2에 지정된 세 축만 기존 doc_code.py와 structure/test_doc_code.py에서 보강한다. 현재 실제 문서의 정상 예시와 다음 최소 변형을 수리 전/후에 대조한다.

- 동일성 검토 initial의 decision/findings/scope_complete와 organize의 issues 및 issues[].finding_refs/answer_role_slot_id를 실제 stage_schema에 연결한다. organize 주 산출에 initial/judge의 decision을 차용하는 문장을 반려한다. 정확한 절·역할·단계의 소유를 명시하며 모든 산문 backtick을 필드로 추측하지 않는다.
- 후보-준비156~158의 contract_checks[].sibling_boundaries 원소,220~229의 assessment_targets 보충 평가/보류 예시를 현재 extension_schema의 정확 부분 객체와 연결한다. independent_of_next_revision 오타와 보충 task_id를 일반 task_title로 바꾸는 차용을 각각 반려한다. 전체 주 응답 schema로 부분 예시를 오검사하지 않는다. 문서 삭제/절·펜스 누락이 빈 성공이 되지 않도록 이 한정 대상의 존재도 확인한다.
- operator install/probe 및 do_math.py/$dmCli를 포함한 표기를 실제 parser mode choices로 검사하고 operator invent를 반려한다. 기존 top command·flag 검사를 유지한다.

허용 예시·오타·다른 역할 차용의 정확 실패 사유를 확인한다. 모든 출력에 공통인 전역 어휘 합집합, 자연어 소유자 추론기, 복제 제품 schema나026 조사표 전체를 새 제품 정본으로 만들지 않는다. 기존 source owner/별칭/배열·실제 반환/P01~P11·PURE 검사와 음성 단언은 유지한다.

### A5 최종 관련 검증·미러·근거

변경을 고정하고 정본·공식 생성 미러의 같은 관련 선택을 완결한다. 선택/고유 실제 row/exit와 소스 전후 SHA를 보존하고 fail/error/not_run을 숨기지 않는다. 아래 필수 선택과 변경 영향의 직접 소비를 합쳐 관련 묶음을 정하며, 새 반례/변경 없이 같은 검사를 반복하지 않는다. 현재 HOLD 경계는 새 실행 근거를 얻고 B129의 옛 통과로 대신하지 않는다. 이전 정확33 doc rows 및 기존 P 성질의 단언을 유지한다. 공식 미러 --check 및 skill-only 구조를 확인한다. 원 실패/보조 관찰 오류는 보존하고 새로운 통과와 분리한다. 새 증거의 의미·미검사·L01/최종관문 남김을 report로 인도한다.

## 판단과 경계

하나의 task가 공유 helper/직접 시험·문구·미러·비용 캐시를 소유한다. writes의 문서와 시험 파일만 수정한다. 현재 runtime, 제출/기록 schema, parser choices, 정책·권한 의미, runner, engine 및 graphify는 변경하지 않는다. tests/시험-지침.md는 이번 검사 책임을 실제로 달리 설명해야 할 때만 좁게 갱신한다. 다른 문서의 문구 교정이나 N01 전수 조사는 추가하지 않는다. 제안된 새 단언은 기존 계약의 기대를 검사하며 조사에서 실행 결함이 이미 관측됐다고 쓰지 않는다.

제품 검사는 총 worker3 이하·동시에 한 묶음·기본 jobs1이다. 검사 중 정본과 미러를 고정한다. 새 유료 모델/OS 예약/설치 변경/Lean/학술 호출·기존 연구 조작은 수행하지 않는다. 기존 공개 sim 및 임시 저장 fixture의 정상 부수 효과는 허용한다. 외부 TEMP/TMP/TMPDIR는 저장소 밖의 짧은 자기 전용 경로를 쓰며 상위 C:/math Git을 찾지 않는지 확인한다. resource output도 짧은 evidence/c와 m 등을 쓴다. 공유 캐시·미러 생성·Git index를 다른 작업과 동시에 쓰지 않는다. task는 commit/reset/checkout/push를 하지 않는다.

이전 원 report/evidence·공용 문서를 고치지 않는다.027은 G1/G2/G3 지정 공백의 수리이며 G4 전체 일반/G5 fresh T3/G6 전수 변이/G7 최종판 연결/G8 review를 대신하지 않는다. L01 Q1/Q2·원문 UTF-8 byte 요구/미충족 및 symlink1314를 유지한다. 026이 종결한 이름·정책 문장과 PR의 한정 slice는 새 반례가 없으면 재사용한다.

## 검증 방법

cwd C:/math, Python C:/Users/wogud/AppData/Local/Programs/Python/Python312/python.exe. 시작/끝 전체 SHA와 실제 변경 목록을026 manager source-inspected에 대조한다. 먼저 A4 최소 문서 변형의 현재 거짓 통과와 정상 대조를 자기 evidence에 보존한다. 정책의 새 단언이 처음부터 통과하면 그 사실을 그대로 기록하며 인위적 red를 만들지 않는다. 현 원문·소비·기존 시험 및026의 판정 근거로 수리하고, 최종 공식 선택은 다음을 포함한다.

`python -u -B .claude/skills/do-math/scripts/run_tests.py structure.test_doc_code sim.test_initialization_controls sim.test_lifecycle_engine_public sim.test_operator_finish_cli unit.test_review_cycle_stages unit.test_submission_contract_checks unit.test_submission_contracts --jobs 1 --output <자기 evidence/c>`

미러는 같은 선택을 .agents/skills/do-math/scripts/run_tests.py로 evidence/m에 실행한다. test_operator_finish_cli의 정상 probe/공개 HOLD 단언을 포함하고 필요한 실제 경계가 빠졌으면 같은 파일 안에 최소 검사를 추가한다. syntax/CLI 오타로 미수집이 생기면 성공으로 처리하지 않는다. 실제 저장·재시작 결과를 원파일 또는 반환 JSON으로 남기며 bytes가 있으면 JSON과 원시 파일을 분리한다. 관찰자를 고치려고 원 성공 report를 다시 쓰지 않는다.

공식 생성기의 정본은 .claude/skills/writing-skills/references/멀티런타임_동기화.md다. 생성 전 영향 경로를 확인하고 writes 밖이나 다른 작업의 변경을 덮지 않는다. 기존 mirror drift가 범위 밖이면 정확 차이와 영향만 반환한다. --check와 skill-only의 실제 출력/exit를 보존한다. 최종 report는 A1~A5 전부와 모든 findings를 연결하고 지정 Python으로 services/continuous-development/check.py report C:/math C:/math/docs/do-math/continuous-development-2026-10-13 027 doc-policy 를 통과한다.
