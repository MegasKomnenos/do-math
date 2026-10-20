# 보존된 전체 T3로 G6 함수 모집단과 실행 배정을 준비한다

G6의 목적은 현재 대상 함수 전체의 극단 변이와 실제 정상 기준을 대응시켜 시험이 놓치는 함수를 드러내는 것이다. g45-final의 온전한 전체 T3가 함수진입·선택 입력을 제공했으므로, 독립적인 모집단/배정 준비를 지금 마친다. 병행 g5-target의 다섯 모듈 수리나 G1~G3 전체 완료를 기다릴 필요는 없다. 이 task는 writes=[]이며 제품·공용 문서·index를 바꾸거나 시험/변이를 실행하지 않는다. 이전 task의 미완성 결과도 소비하지 않는다.

SESSION_JSON·task.json·고정 inputs/context/plan/seams, managers/0095/review.md·handoff-delta.json, sources/t3-targeted-direction-2026-10-16.md·storage-scope-direction-2026-10-15.md·archive-resume-2026-10-16.md와 자기 workspace의 do-math AGENTS.md·시험-지침.md를 읽는다. 원설계6.3/5.3과 현재 scripts/do_math/layers.py:LAYERS, tests/support/mutation.py, selection.py, branch_gate.py가 실제 대상/규칙/선택 계약이다. 이전17파일 묶음과 관측 함수키3220은 고정 모집단이 아니다.

g45-final/evidence/G6-inputs.json이 원 전체 coverage·entered/opened·store 및 보존 index의 경로/SHA를 연결한다. 원본은 읽기 전용이고 index는 evidence/generated-final/.claude/skills/do-math/scripts/tests/.selection-index.json에 있다. manager는 원6보고의 행·집계, 최종919Python SHA와 주요10자료 SHA를 확인했다. 이미 충분한 원자료 무결성 감사를 반복하지 말고 실제 모집단/선택 결정을 하는 데 필요한 정보만 읽는다. 현재 source는 자기 workspace 판본을 사용하고 과거 파일은 필요한 경우에만 공식 `workspaces.py restore RECORDS g45-final result NEW_DIRECTORY PATH...`로 복원한다.

다음 결과를 한 작업에서 준비한다.

1. 현재 LAYERS의1~3층과 mutation.functions/body/rule_of/mutate의 실제 의미로 대상 함수를 정리한다. 중첩·반복 이름#n·generator/return_none/pass·trivial과 실제 파일/함수 위치를 보존한다. `--every`는 선택 모듈의 전체 함수를 대상으로 하므로 단순 변경분만으로 G6 전체를 대신하지 않는다. AST/기존 순수 helper를 읽거나 호출하는 정적 산출이면 충분하며 제품을 import하여 환경 동작을 시작하지 않는다.
2. 각 대상의 기존 index 진입 시험과 mutation.tests_for의 선택 의미를 연결한다. 전체 시험 ID 목록을 함수마다 중복 저장하지 않고 원index 참조/필요 집합과 수량을 사용할 수 있다. 무진입/새 함수/판본 변경·fallback과 trivial을 구별한다. 정상 소스에서 실제 통과한 선택의 실패만 killed가 되고 skip·환경/결과 오류·미실행·시간 초과가 성공이 아니라는 현재 계약을 실행 계획에 유지한다. 전체 일반 성공이 각 변이의 정상 child 증거를 대체하지 않는다.
3. source SHA/함수 단위 판본과 실행 선택을 기준으로 충돌 없는 유한 실행 묶음을 제안한다. 총 시험worker3 이하·각 작업 jobs1/명령1 원칙과 실제 원자료 경로, pseudo_tested.json의 공통 쓰기 소유를 고려한다. 같은 공통 파일을 여러 worker가 고치게 하지 않고, 별도 새 실행 프레임워크를 만들지 않는다. 기존 CLI의 --base/--every/--only/--output으로 가능한 명령과 제약을 구체적으로 적는다.
4. 병행 수리의 대상 context_store/core_engine/file_io/integration/lifecycle_engine은 별도 갱신 필요 집합으로 표시한다. 다른 모듈도 그 함수가 소비하는 시험/helper가 바뀔 수 있으므로 '모듈이 다르다'는 이유만으로 최종 유효성을 확정하지 않는다. 후속 수용diff에서 필요한 변경만 갱신할 수 있도록 고정 현재판과 선정 근거를 남긴다. 이 준비 완료를 G6 실행/최종 모집단 인증이라고 하지 않는다.

index.commit은 g45-final의 실제 독립 baseline HEAD 4dae85911f26f891fc3d79be9916bf4363e2d46f이다. workspace 정리로 Git 신원이 사라지는 것을 막기 위해 manager가 managers/0095/g45-index-baseline.bundle에 해당 HEAD의 실제 전체 history를 보존했고 verify했다. SHA/의미는 index-baseline.json이다. 이 bundle은 수용된 최종 제품 snapshot이 아니며 index/source의 bytes와 별개다. 현재 selection.usable/is_ancestor_of_head가 새 독립 task에서 어떤 실제 ancestry를 요구하는지 정적으로 판단하고, 실제 bundle의 원commit을 유지하는 최소 준비안을 적는다. 공용 Git에 쓰거나 가짜 HEAD/index commit 변경/검사 우회로 맞추지 않는다. 실행 작업이 필요하다면 manager가 그 구체 배정을 하도록 계획에 남긴다. 이번 task에서 Git 인계 실험·전체T3 재실행을 하지 않는다.

evidence/population.json과 evidence/execution-plan.md, report.json으로 반환한다. 필요한 보조 정적 스크립트는 자기 evidence에만 둔다. 함수마다 과거 전수 감사를 하거나 모든 원raw를 복사하는 일은 필요 없다. 소프트 시간 기준과 자료부재/미측정 한계를 유지하고, 새 제품 결함이 보이면 정확 심볼·영향·최소 다음 범위만 보고한다. report는 changes=[]이며 `python C:/math/services/async-development/check.py report C:/math/.async/dm g6-scope`로 확인한다.
