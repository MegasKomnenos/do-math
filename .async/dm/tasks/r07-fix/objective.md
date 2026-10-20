# 목적과 완료할 결과

R07/1-E 조사에서 확인한 `provider_final.output_contract`의 검사 등록 누락 F1과 Claude 반환 내부의 가변 노드 공유 F2를 한 작업에서 수리한다. 실제 생성자의 두 공급자 분기를 기존 소유권 검사에 연결하고, 반환한 필드의 변경이 형제 필드·입력·다른 반환에 전파되지 않게 한다. 제품·시험·관련 설명·미러와 최소 검증까지 완료하는 work이며 최종 review가 아니다.

## 입력과 쓰기 범위

SESSION_JSON의 workspace 및 고정 inputs/context.md·plan.md·seams.md와 task.json을 기준으로 일한다. 스킬 상대 경로는 자기 workspace 기준이다. C:/math/.async/dm/tasks/r07/report.json 및 evidence/conclusion.md·ownership-map.json·output-contract-probe.json·requirement-links.json·historical-evidence.json, managers/0003/review.md·source-review.json은 수용된 읽기 전용 근거다. 과거 run: 경로는 C:/math/docs/do-math/continuous-development-2026-10-13 기준이다.

기본 수정은 `.claude/skills/do-math/scripts/do_math/provider_final.py`와 `scripts/tests/structure/test_schema_builders.py`다. `scripts/이음새-정본.md` 5절의 현재 빌더 설명에도 이 함수의 두 분기와 검사 연결을 필요한 만큼 반영한다. 세 경로의 `.agents` 미러를 같은 작업에서 생성한다. values.py·ModelRunner·공유 provider_runs helper의 변경은 필요하지 않으며 쓰기 범위에 없다. 범위 밖 실제 결함은 정확 반례와 필요한 파일을 보고한다.

두 `scripts/tests/.timings.json`은 공식 실행기가 자기 사본에 기록할 수 있도록 writes에 포함했다. r02-fix도 자기 사본에서 같은 캐시를 갱신할 수 있으므로 이 작업은 시험 종료 후 생성된 비용 자료를 자기 evidence에 보존하고 해당 두 파일만 자기 base의 원바이트로 되돌린다. 최종 changes에는 비용 캐시 차이를 남기지 않는다. 다른 제품 변경은 되돌리지 않는다. 검증 증거는 공식 보고서와 소스 판본에 보존되므로 캐시 반영을 독립 수리의 선행 조건으로 만들지 않는다.

다른 task의 중간 결과·공용소스 변경을 소비하지 않는다. r02-fix·r18의 종료는 선행 조건이 아니다. 공용 문서·queue/state·engine·과거 증거·다른 task·Git index를 수정하지 않는다. graphify 갱신이나 새 원격 모델·설치·예약·기존 연구 변경은 이번 배정에 없다.

## 구현과 완료 판단

1. `provider_final.output_contract(provider, schema)`를 `_composition_calls`에 명시 등록한다. 이름에 schema가 없으므로 현 `_schema_functions` 탐색만으로는 발견되지 않는다. codex/claude 두 분기를 기존 `_isolation_problems`의 반복 호출·전역/결과 간/결과 내부 ID 검사에 연결한다. 각 분기에 두 속성이 같은 가변 leaf를 가리키는 유효 JSON schema를 넣어 F2가 기존 구현에서 드러나게 한다. 새 일반 탐색 프레임워크나 전체 빌더 재감사는 필요하지 않다.
2. Claude 분기의 `deepcopy(schema)`를 기존 정본 `values.json_copy(schema)`로 교체한다. Codex의 닫힌 `output_json` 문자열 봉투와 원 schema의 description 직렬화, 지원하지 않는 provider의 ValueError는 유지한다. 새 복사기·호환 분기를 만들지 않는다.
3. 반례는 `leaf={'type':'string'}`, `schema={'type':'object','properties':{'left':leaf,'right':leaf}}`다. 반환 left에 enum을 넣어도 right·원 입력·두 번째 반환이 바뀌지 않아야 한다. 값이 원 schema와 같고 노드가 분리되는지 실제 함수로 확인한다. 기존 소유권 단언이 충분히 보장하는 부분은 중복 시험으로 늘리지 않는다. 값의 기대는 계약과 명시 입력에서 구한다.
4. 기존 named/composition/class/constant 빌더·transformer·borrowed lookup의 처분과 유한 입력축을 유지한다. `repetition_outcome`/`recovery_outcome`에 새 복사 의무를 만들거나 검사 자체의 반례 시험을 약화시키지 않는다.
5. 현재 `ModelRunner.run`은 Codex에만 output_contract를 호출하고 Claude schema는 바로 직렬화한다. 이 수리를 Claude 실제 전송 실패의 수정으로 보고하지 않는다. 원문 1-E의 다른 결과/전역 격리와 정본 5절의 결과 내부 격리를 구별한다.

구체적인 단언 배치는 담당자가 정한다. 기존 검사 확장으로 충분하면 새 파일이나 helper를 만들지 않는다.

## 필요한 확인과 미러

스킬 AGENTS.md와 scripts/tests/시험-지침.md를 따른다. 실행에는 자기 workspace의 공식 `scripts/run_tests.py`를 사용한다. F1 등록 후 기존 구현에서 F2를 드러내는 가장 작은 시험 ID를 한 번 확인하고, 수리 후 `structure.test_schema_builders --jobs 1 --output <새 짧은 절대 경로>` 한 모듈로 인계한다. 수리 전 실패가 import/fixture 오류가 아닌 공유노드 반례인지 기록한다. 과거 원 FunctionDef 순수 probe는 실제 모듈 회귀를 대체하지 않는다.

Codex 반환 본문이 그대로이고 값 보존을 직접 확인했다면 provider 전반을 재실행하지 않는다. 전송 의미에 실제 불확실성이 남을 때만 기존 `sim.test_provider_schema.ProviderSchemaTests.test_full_maintenance_contract_is_carried_without_requiring_optional_fields` 등 최소 기존 ID를 더한다. 외부 Job/CLI 대역을 사용하는 기존 provider 시험은 필요 시 허용하지만 내부 제품 함수를 대역으로 가리지 않는다. 새 실제 모델/Job/Lean/예약 호출, 전체 일반/T3/변이/T4/T5는 배정하지 않는다.

실행 중 자기 소스를 고정하고 jobs1로 수행한다. 출력은 workspace 밖 자기 task/evidence 또는 저장소 밖 짧은 새 경로에 둔다. 선택 ID·실제 row·exit·소스 해시·실패와 한계를 보존하고 충분한 확인은 반복하지 않는다.

정본 수정 후 workspace의 `.claude/skills/writing-skills/scripts/build_skill_mirrors.py --target .agents`로 미러를 생성한다. 예상 밖 변경은 원인을 확인하고 허용 범위에 한정한다. 비용 캐시의 evidence 보존 및 자기 base 복원은 모든 실행이 끝난 뒤 수행한다. 미러 대응과 생성기 `--check --target .agents`로 충분하면 같은 시험을 미러에서 반복하지 않는다.

## 제출과 남김

자기 evidence에 F1/F2의 변경·시험 연결, 수리 전후 결과와 판본·한계를 기록한다. r07 원보고는 수정하지 않는다. async `report.json`의 status, summary, changes, verification, findings에 실제 최종 변경과 결과를 적고 `python C:/math/services/async-development/check.py report C:/math/.async/dm r07-fix`의 PASS를 확인한다.

완료 판정은 두 수리의 성립 여부다. 1-E/R07을 최종 판본 증거 대기로 넘길 근거를 남기되 G4~G8, L01 Q1/Q2·UTF-8 byte, Windows1314 symlink 실반려 미검사와 다른 미결은 유지한다. 공용 통합·accepted·관리 마감은 manager가 맡는다.
