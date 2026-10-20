# 목적과 완료할 결과

R02/1-A 작업자 요청 가족의 확인된 시험 공백 F1을 수리한다. 기존 계약 pair가 `worker_request_fields`만 직접 호출하고 첫 machine 프로필을 참조하는 상태에서, 유효한 AI 배정으로 실제 `ModelRunner.run`이 저장한 요청을 두 공급자의 adapter·worker가 소비하는 상태로 바꾼다. 사용자 목표는 실제 제품 경로의 결함이 시험을 빠져나가지 않게 하는 것이다. 이 작업은 시험·필요한 fixture·미러와 관련 검증을 함께 끝내는 work이며 최종 review가 아니다.

## 입력과 범위

SESSION_JSON의 workspace와 고정 inputs/context.md·plan.md·seams.md, task.json을 기준으로 일한다. 스킬 상대 경로는 workspace 기준이다. C:/math/.async/dm/tasks/r02/report.json과 evidence/conclusion.md·branch-field-map.json·source-symbols.json·history-and-reports.json, managers/0002/review.md·source-review.json은 읽기 전용 수용 결과다. 원문 판단 원칙은 C:/math/docs/do-math/continuous-development-2026-10-13/sources/user-decisions.md와 document-batching-2026-10-14.md다. 과거 run: 경로는 같은 continuous-development-2026-10-13 루트로 해석한다.

제품 쓰기는 task.json의 정확한 시험 경로와 대응 미러에 한정한다. 기본 수정은 `scripts/tests/contracts/pairs.py`와 `test_pairs.py`이며, 필요하면 기존 `sim/test_provider_pinned_runner.py`와 `support/provider_runs.py`를 함께 고친다. 같은 의미의 helper를 여러 시험에 복제하지 않는다. 두 .timings.json은 공식 실행기가 실제로 바꾼 비용 자료만 허용한다. runtime 수정 필요성은 아직 확인되지 않았으므로 제품 runtime을 고치지 않는다. 범위 밖 실제 결함을 발견하면 최소 반례와 정확 파일을 보고하고 맡은 범위의 유효한 결과를 남긴다.

다른 task의 진행 중 결과나 공용 소스 변경을 소비하지 않는다. r07·r18의 종료는 선행 조건이 아니다. 공용 context/plan/seams/queue/state·engine·과거 증거·다른 task·Git index를 수정하지 않는다. graphify 갱신, 원격 모델 호출, 설치·예약·기존 연구 인스턴스 변경은 하지 않는다.

## 구현과 완료 판단

1. 기존 `_worker_request_samples`의 두 공급자와 identity/limits/control/scholarly/lock 축을 실제 producer 경로로 연결한다. 현재 각20개의 유효 입력과 limits/control이 identity 없이 있을 수 없다는 조건을 보존한다. schema는 control의 유무에 따른 값이며 새로운 독립 축으로 늘리지 않는다. 전체40입력의 존재를 세는 것만으로 완료하지 않고 실제 runner가 성공적으로 저장·수신 경로를 통과했는지 확인한다.
2. pinned 표본은 `build_profiles`에서 명시적으로 적합한 AI 역할을 고른다. 모델·effort·tools·lock·host demands를 해당 profile에 맞추고 `dispatched`, `prompt_seal`, 필요한 `on_started`를 사용한다. `support/provider_inputs.py:host_capacity_fixture` 등 기존 준비를 재사용한다. pinned tools/lock을 별도 caller override로 전달하지 않는다. unpinned 표본에는 identity 전제를 만들지 않는다. 실제 profile 검사나 ModelRunner/adapter/worker/collector를 대역으로 교체하지 않는다. 외부 Job과 공급자 CLI만 기존 `ProviderJobs`/`ScriptedCLI`로 대체한다.
3. pair의 값은 실제 저장 요청에서 얻는다. 두 worker의 load/run과 CLI에 도달했다는 근거를 남긴다. identity/ref, limits, control, scholarly, lock의 정확 값·부재와 schema 의미를 fixture 입력 및 실제 계약에 대조한다. 원 요청→staged 요청에서 prompt/schema 경로만 바뀌는 성질도 확인한다. 파일 경로가 사라진 뒤 메타데이터만 비교하거나 생성 helper로 기대값과 관찰값을 함께 만들지 않는다. 필요한 관찰은 기존 경계 fake에서 수집한다.
4. 최소 누락 조합인 Claude의 pinned research_work + host limits + control + scholarly + lock=True를 실제 경로로 확인한다. 올바른 ticket/seal/host start publication, 정확 request binding, bound schema 부재, CLI 한 호출, 실제 scholarly/model-lock 인자, Job 정리까지 단언한다. 해당 성질이 기존 pair 안에서 충분히 확인되면 별도 중복 시험을 추가하지 않는다.
5. 기존 필수+선택 필드 역방향, Codex lock=False/True의 CLI 요청 효과 없음, Claude True에서만 lock 필드·CLI 제한이 적용되는 성질을 보존한다. 실제 profiles의 lock 값이 달라지면 SHA/id도 달라진다. 각 request.profile_ref가 자기 profile_ref와 정확히 같은지 먼저 단언하고, 서로 다른 프로필 참조나 별도 실행 경로를 억지로 동일하게 만들지 않는다. 경로를 정규화해야 하면 필드와 이유를 한정하고 binding 검사를 지우지 않는다. 기존 runner 결과의 collected/bound/incomplete/stopped 8표본과 의미 단언도 유지한다.
6. scholarly args의 `[]`, `[absolute_server]`, `[absolute_server, '--flag']`를 유효 command와 함께 실제 생산→저장→worker CLI로 연결하고 순서·값 및 추가 data-dir를 확인한다. 두 공급자의 각 argv 계약을 검사하되 모든 bool 조합에 이 목록 축을 무조건 곱할 필요는 없다. scholarly 부재는 빈 args 표본의 대체가 아니다. identity/control 등 단일 객체를 여러 개로 만드는 새 요구는 없다.

helper와 단언의 구체적인 배치는 구현자가 결정한다. 기존 pair 인터페이스와 fixture를 우선 사용하고 새 등록부·프레임워크를 만들지 않는다. 이 task는 F1을 닫는 데 필요한 시험 수리로 끝내며 다른 요청 가족·공급자 전체·과거 K/P2 전수 감사로 확장하지 않는다.

## 최소 검증과 미러

스킬 AGENTS.md와 scripts/tests/시험-지침.md를 따른다. 새 단언이 기존 helper만의 표본으로는 성립하지 않음을 보여 주는 가장 작은 기존 시험 ID를 먼저 선택하고, 실패의 원인과 실제 보고를 남긴다. 단순 import/fixture 오류를 의미 반례로 세지 않는다. 수리 후 공식 `scripts/run_tests.py contracts.test_pairs --jobs 1 --output <새 짧은 절대 경로>`를 기본으로 사용한다. shared helper나 sim 시험을 실제로 바꾼 경우 그 직접 소비자 중 변경 성질을 확인하는 최소 ID만 더한다. 코드·정적 소비자 확인으로 충분한 부분은 반복 실행하지 않는다. 새 전체 일반/T3/변이/T4/T5는 이번 배정에 없다.

관련 실행 중 자기 소스를 고정한다. fixture와 출력은 workspace 밖 자기 evidence 또는 저장소 밖 짧은 임시 경로에 두고, 필요한 증거를 자기 task/evidence에 보존한다. 직접/간접 실제 모델 호출 없이 runner·worker를 시험하는 구분을 보고한다. 선택 ID·실제 row·exit·소스 판본·미실행/실패를 실제 결과대로 남기며 시간 초과를 통과로 세지 않는다.

정본 수정 후 workspace의 `.claude/skills/writing-skills/scripts/build_skill_mirrors.py --target .agents`로 미러를 생성하고 허용된 경로만 바뀌었는지 확인한다. 예상 밖 생성 변경은 그대로 제출하지 않고 원인을 확인한다. 대응 미러의 내용 일치와 공식 생성기 `--check --target .agents`로 충분하면 동일 시험을 미러에서 반복하지 않는다. 비용 캐시를 제품 의미 변경처럼 설명하지 않는다.

## 제출과 남김

자기 task/evidence에 F1의 입력축→실제 시험 ID/단언 대응, 실제 실행 근거, 변경 이유와 한계를 간결하게 남긴다. 원본 r02의 조사 파일은 고치지 않는다. `report.json`은 async protocol의 status, summary, changes, verification, findings를 사용하고 실제 workspace 변경 전부를 changes에 적는다. F1 수리 완료와 최종 판본 실행 대기 F2를 구별한다. G4~G8, L01 Q1/Q2·UTF-8 byte 미충족, Windows1314 symlink 미검사 및 다른 미결은 그대로 유지한다.

마지막에 `python C:/math/services/async-development/check.py report C:/math/.async/dm r02-fix`의 PASS를 확인한다. 공용 소스 통합·accepted·commit은 manager가 맡는다.
