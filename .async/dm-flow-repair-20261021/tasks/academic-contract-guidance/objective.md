# 학술 계약의 자료 대기·수정 필드 설명을 실제 지급 문서에 맞춘다

## 얻을 결과

`final-goal-review`가 확인한 F1(P2)을 수리해, 후보 준비와 계약 검토가 받는 학술 계약 설명이 현재 코드의 자료 대기·실제 수정·사용자 원 계약 처리와 같은 의미가 되게 한다. 문서 네 개와 공식 미러의 작은 수리다. 구현·필요한 확인을 이 task에서 끝낸다.

먼저 inputs/context.md, plan.md, seams.md와 task.json을 읽는다. 정본 `.claude/skills/do-math/AGENTS.md` 및 관련 제품 이음새를 읽고 현행 프리알파 계약을 따른다. 정확한 발견과 반대 근거는 `C:\math\.async\dm-flow-repair-20261021\tasks\final-goal-review\assessment.md`의 F1과 `evidence\contract-consistency.json`이다. 사용자 원문은 `C:\math\.async\dm-flow-repair-20261021\user-messages.md`다. 기존 결과의 정리될 workspace에 의존하지 않는다.

## 수정 범위와 의미

정본의 다음 네 파일과 대응 `.agents/skills/do-math/` 미러만 수정한다.

- `계약/후보-준비.md`의 「기존 과제의 평가와 관찰 규칙을 보충하는 실행」, 특히 현재 214행.
- `references/모델과-실행예산.md`의 현재 68행 일반화.
- `references/CLI-실행-계약.md`의 현재 144행 학술 반려 설명 및 인접 대기 표의 contract_revision/contract_review_input 구분.
- `계약/작업-계약-검토.md`의 현재 143행 학술 반려 설명과 뒤의 revision_fields/unresolved 설명을 함께 읽고 같은 의미로 정리한다.

판단 근거는 자기 workspace의 현재 실제 코드다. `scripts/do_math/core_engine.py:CoreEngineMixin._apply`의 task_contract_review 분기와 `planning_engine.py:PlanningEngineMixin._ensure_model_assessments`를 읽는다. 다음 의미를 정확하게 설명한다.

1. 필수 판단 자료 부족의 unresolved는 기존 평가·관찰 규칙을 보존하며 `contract_review_input`과 question_routes로 연결한 실제 질문 담당을 기다린다. 근거 해소 뒤 같은 계약을 새 독립 검토가 판단한다.
2. 실제 revision_required의 item_reviews.revision_fields에서 model_assessment/initial_observation_rules로 지적된 항목만 해당 history와 판본·해시·원 검토 참조에 보존해 현행에서 분리하고 보충한다. 계약 변경이 포함된 경우의 분기를 실제 코드대로 설명한다. 일반적인 미평가·규칙 누락 보충은 계속 설명한다. 두 값을 항상 재준비하거나 자료 부족을 AI 저작 결함으로 취급하지 않는다.
3. revision_fields의 contract는 사용자 원 계약을 보존하는 개정 요청 처리다. 잘못된 AI 요청의 근거 있는 기각, 필요한 자료·실제 사용자 결정의 대기 등 수용된 재량과 사용자 권위·독립 승인의 구별을 유지한다. AI가 사용자 원 계약을 다시 쓰게 하거나 무수정 처분을 승인으로 설명하지 않는다.

이 세 경우와 기존 보충 후 독립 검토를 읽는 사람이 다시 추론하지 않아도 분명하게 이해할 수 있도록 작성한다. 후보 준비의 기존 보충 절이 상세 정본인 구조를 활용하고 다른 문서는 해당 상세 절과 모순 없이 필요한 요약·링크를 제공한다. 새 보편 증명·승인 절차나 요청 재심사 의무를 추가하지 않는다. CLI의 상태·요청 ID·실행 ID 조회 설명도 실제 후속을 가리키게 한다.

제품 Python/schema/시험 수정은 배정하지 않았다. 현재 런타임을 옛 문서 설명에 맞추지 않는다. 구체적으로 추가 수리가 반드시 필요한 사실을 찾으면 실제 심볼·영향·최소 범위를 report에 남긴다.

## 필요한 확인과 미러

수정 문구를 현재 코드와 정적으로 대조하고, 기존 `contracts.reading_map/prompt_documents/render_prompt`의 작은 호출로 후보 준비와 작업 계약 검토에 수정 전문이 지급되는지 확인한다. exact path/문구·SHA와 지급 결과를 자기 task의 evidence에 남긴다. CLI 문구는 실제 코드/대기 정의와 대조한다. 제품 시험 추가나 전체 회귀·벤치마크·원자료 재생·live 모델/학술/Lean 호출은 필요하지 않다. 이 문서 수리의 의미와 지급 확인으로 한정한다.

공식 `.claude/skills/writing-skills/scripts/build_skill_mirrors.py`의 기존 절차로 대응 미러를 생성하고 `--check --target .agents`로 확인한다. 생성기의 전체 입력 범위와 배정 writes를 구별하고 관계없는 스킬 변경을 남기지 않는다. 원 연구/감사/HOLD/예약·graphify·서비스 state/queue·공용 맥락 문서는 변경하거나 재개하지 않는다.

report.json에 수정한 의미·이유·실제 확인과 한계·변경 파일을 기록한다. 마지막으로 `python C:\math\services\async-development\check.py report C:\math\.async\dm-flow-repair-20261021 academic-contract-guidance`로 보고·실제 변경 범위를 확인한다. 최종 완료 판단은 수정 수용 뒤 독립 review와 manager가 수행한다.
