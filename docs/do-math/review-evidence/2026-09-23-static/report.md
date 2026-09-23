검증을 통과하지 못했습니다. 실행 흐름의 연결 문제 7건과 문서 불일치 1건을 확인했습니다. 특히 중단되거나 한도에 걸린 작업을 기록한 뒤, 그 의무를 다음 실행·계획으로 연결하는 부분이 부족합니다.

검토 대상은 .claude/skills/do-math이며, 아래 지적은 검토 끝에 보존한 파일 판본을 기준으로 합니다. SKILL과 README의 진입점에서 초기화 → 후보 준비 → 계약 검토 → 계획·배정 → 입력 구성·실행·관찰 → 제출·편입 → 형식 검사·동일성 검토 → 목표 감사·학술 후속까지 추적했습니다. 사용자 입력·개정·정지·재개·운영 복구·산출 보존과 정리의 연결도 함께 확인했습니다. do-math와 그 테스트는 실행하지 않았고, 검토 대상 파일도 수정하지 않았습니다. 아래의 발생 경로는 소스에서 확인한 조건부 동작이며 실제 운전에서 재현했다는 뜻은 아닙니다. 검토 중 원본 변경을 확인했으므로, 근거 파일은 사본과 SHA-256으로 보존했습니다. 아래 링크는 그 보존 사본을 가리킵니다.

1. **[높음] Lean 검사 중 일시 정지하면, 일반 재개로 그 검사가 이어지지 않습니다.**

   형식 검사가 실행 중일 때 `pause`가 들어오면 검사 결과는 `stopped`가 됩니다. `_formal_steps`는 원래 action을 queue에서 지우고 `waiting_actions`에 `kind="formal_stopped"`, `next_owner="trust_governance"`로 옮깁니다. 그러나 실제 `resume` 경로는 lifecycle과 실행 상태를 복구할 뿐 이 대기를 다시 배정하지 않습니다. `formal_stopped`를 소비하는 전용 경로도 없습니다. 따라서 사용자 일시 정지가 해소되고 같은 허가·신뢰 환경이 유지돼도 해당 결과의 형식 검사는 대기 상태에 남습니다. 새 연구가 진행되는 것과 이 검사 의무가 이어지는 것은 다릅니다. [검사 종료 처리](source/.claude/skills/do-math/scripts/do_math/engine.py#L4437), [실제 resume 분기](source/.claude/skills/do-math/scripts/do_math/lifecycle_engine.py#L558).

   정지 원인을 구별해 보존하고, 사용자 재개 뒤 현재 허가·환경·로컬 종료를 확인하여 같은 검사 의무의 후속을 배정해야 합니다. 현재 대기 기록에는 종료된 검사 `execution_id`도 없어, 일반 복구의 실행 계보 대조에 필요한 연결도 보충해야 합니다.

2. **[높음] 동일성 검토의 실행 한도가 소진되면, 미해결 결과를 반환하지 않고 처리되지 않는 대기로 남습니다.**

   범위 계획의 `activity_execution_limit`은 양수이고 정책 상한 이하인지만 검사합니다. 필요한 검토 자리 수와 이미 소비한 범위 계획 실행을 합친 하한은 검사하지 않습니다. 예를 들어 초기 자리 둘을 제안하면서 한도를 1로 반환해도 이 검사를 통과합니다. 범위 계획 자체가 한 실행을 썼으므로 다음 초기 검토에서 바로 한도가 소진됩니다. [범위 계획 검사](source/.claude/skills/do-math/scripts/do_math/review_policy.py#L95), [한도 검사](source/.claude/skills/do-math/scripts/do_math/review_policy.py#L119).

   실행기는 이 경우 `review_budget_exhausted`를 반환하고 action을 `next_owner="review_policy"`인 대기로 옮깁니다. 검토 cycle은 `working`으로 남고, `overflow_disposition`을 읽어 `unresolved`로 닫거나 재구성 계획을 여는 소비자가 없습니다. 이 필드는 작성·검사·보존되지만 실제 초과 처분을 결정하지 않습니다. 이는 필수 검토를 끝내지 못하면 실제 완료 범위와 남은 의무를 미해결 결과로 남긴다는 계약과 맞지 않습니다. [배정 거부](source/.claude/skills/do-math/scripts/do_math/review_engine.py#L330), [대기 전이](source/.claude/skills/do-math/scripts/do_math/engine.py#L635), [미완료 검토의 계약](source/.claude/skills/do-math/GLOSSARY.md#L623).

   계획 수신에서 필수 실행 몫을 대조하고, 실행 도중 소진된 경우에도 기존 검토 결과와 남은 의무를 다음 계획으로 반환하는 경로를 연결해야 합니다.

3. **[중간] 검토할 제안 자체가 입력 한도를 넘는 경우에도, 재구성 계획 대신 사용자 대기로 보냅니다.**

   입력 생성기는 동일성 검토의 초과 원인을 `current_proposal_or_required_sources`와 `restored_dialogue`로 구별하고, 전자에는 `suggested_disposition="unresolved_to_review_plan"`까지 기록합니다. 하지만 대체 프로필을 찾는 분기는 `research_work`에만 있어, 동일성 검토의 실제 `resolution_question.next_owner`는 항상 `user`가 됩니다. 실행기는 그 소유자 값으로 대기와 차단 질문을 만들며, 앞서 계산한 권고 처분은 사용하지 않습니다. [원인 분류와 소유자 결정](source/.claude/skills/do-math/scripts/do_math/context_store.py#L600), [대기 처리](source/.claude/skills/do-math/scripts/do_math/engine.py#L3184).

   따라서 제안을 독립적으로 인증할 수 있는 결과들로 재구성하도록 다음 계획에 돌리는 설계가 이 경로에서는 작동하지 않습니다. 실제로 더 큰 프로필을 승인해야 하는 경우와, 현재 권한 안에서 연구를 재구성할 경우를 이미 분류한 원인에 따라 연결하면 됩니다. [설계의 반환 절차](source/docs/do-math/통합-설계.md#L1198).

4. **[중간] 승인된 과제 의무 이전이, 수신 과제가 선택 후보가 아니라는 이유로 거부됩니다.**

   사용자 `task_scope` 결정은 서로 다른 미완료 과제 사이의 의무 이전을 허용합니다. 계획자에게도 `task_catalog`를 통해 전체 과제의 고정 원문이 제공됩니다. 그런데 계획 적용기는 `input_tasks`를 `ready_task_ids ∪ returned_task_ids`에 해당하는 축소 목록에서만 만듭니다. 이후 이전 적용기는 수신 과제가 이 `input_tasks`에 없으면 입력에 결박되지 않았다고 거부합니다. [이전 승인 조건](source/.claude/skills/do-math/scripts/do_math/governance.py#L731), [계획 입력 선별](source/.claude/skills/do-math/scripts/do_math/context_store.py#L499), [적용 입력 구성](source/.claude/skills/do-math/scripts/do_math/engine.py#L4309), [수신 과제 검사](source/.claude/skills/do-math/scripts/do_math/task_scope.py#L348).

   예를 들어 결과가 돌아온 A의 남은 의무를, 아직 계약 검토가 끝나지 않은 B로 옮기는 승인된 계획이 해당합니다. B는 실제로 제공된 과제지만 선택·완료 판정 모집단에는 없으므로 이전이 막힙니다. 선택 모집단은 그대로 유지하면서, 이전 대상의 판본 확인에는 같은 snapshot의 전체 과제 원문을 사용해야 합니다.

5. **[중간] 고정 질문 보충 조사의 참조 검사가 정의만 되고 호출되지 않습니다.**

   `submission.py`에서 보충 조사의 `used_sources`와 `evidence_refs`를 검사할 `source()`를 정의하지만, `check(..., source)`가 그 함수 내부에 들여쓰기돼 있습니다. 바깥 반복문은 함수를 정의하기만 하므로 고정 원자료 집합 대조가 실행되지 않습니다. 일반 `used_sources` 검사도 이 역할에서는 건너뜁니다. [호출이 빠진 검사](source/.claude/skills/do-math/scripts/do_math/submission.py#L839).

   예를 들어 `evidence_refs`는 지정된 원자료를 가리키되 `used_sources`에 그 조사에 허용되지 않은 참조가 들어간 응답은, 이 누락 때문에 공유 제출 검사를 통과할 수 있습니다. 뒤의 `_apply_review_research`는 그 허용되지 않은 `used_sources` 항목을 고정 원자료 목록에 대조해 반려합니다. 생산자 진단과 중앙 구조 검사가 놓친 오류가 편입 단계에서 드러나 불필요한 수리로 이어집니다. 해당 호출을 함수 정의 바깥으로 옮겨야 합니다. [최종 소비자의 검사](source/.claude/skills/do-math/scripts/do_math/review_engine.py#L1115).

6. **[중간] 독립 묶음 하나의 구조 오류가 정상 묶음까지 모두 반려시킵니다.**

   묶음 적용기는 전체 오류와 `integration_id`가 붙은 묶음별 오류를 구분하여, 정상 묶음은 적용하고 잘못된 묶음만 반환하도록 작성돼 있습니다. 그러나 그 앞의 `seal_submission`은 검사 문제가 하나라도 있으면 후보 전체를 봉인하지 않습니다. 정상 최종 응답에서 이 경우가 발생하면 `_receive_submission`은 `bundles=[]`로 즉시 반환하여 묶음별 적용기에 도달하지 않습니다. 명시적 조기 제출도 같은 봉인 검사를 사용합니다. [묶음별 처리](source/.claude/skills/do-math/scripts/do_math/integration.py#L478), [전체 봉인 거부](source/.claude/skills/do-math/scripts/do_math/submission.py#L1403), [전체 반환](source/.claude/skills/do-math/scripts/do_math/engine.py#L2254).

   가령 독립적으로 선언한 A·B 중 B의 지식 의존 참조만 잘못돼도 A를 먼저 보존·활용하는 효과가 사라집니다. 부분 편입이 모든 경우에 불가능하다는 뜻은 아닙니다. 봉인 뒤 현재성·적용 단계에서 생긴 오류는 부분 처리할 수 있지만, 이미 묶음별로 식별한 구조 오류에는 그 기능이 연결되지 않았다는 문제입니다. 전체 봉인을 막아야 할 오류와 개별 묶음의 오류를 같은 기준으로 전달해야 합니다. [묶음별 수신 계약](source/.claude/skills/do-math/references/공통-실행.md#L218).

7. **[중간] 호스트 자원 제한 구현을 공개 설정 경로에서 사용할 수 없습니다.**

   `build_profiles`는 `config.host_resources`로 승인된 호스트 제약과 역할별 자원 요구를 받아 프로필·예약에 연결합니다. 저장 스키마도 이 필드를 허용합니다. 그러나 `init`과 `configure`가 먼저 호출하는 `validate_config`의 허용 키 집합에는 `host_resources`가 없어, 해당 설정은 프로필 생성 전에 거부됩니다. [프로필 생성](source/.claude/skills/do-math/scripts/do_math/execution_profiles.py#L167), [저장 스키마](source/.claude/skills/do-math/scripts/do_math/record_schemas/__init__.py#L176), [공개 경로의 설정 검사](source/.claude/skills/do-math/scripts/do_math/engine.py#L165).

   이는 자원 기능이 전혀 구현되지 않았다는 지적이 아니라, 구현된 기능과 실제 채택 진입점이 끊겼다는 지적입니다. 공개 설정에서 정확한 구조 검사를 거쳐 연결하거나, 지원하지 않을 기능이라면 지원 범위와 내부 구현을 정리해야 합니다. 공개 경로를 연결할 때에도 `formal_check`·`trust_check`의 Lean 컴파일에 상한을 적용하지 않는 현행 계약은 유지해야 합니다.

8. **[낮음] 자체 형식화 조건에, 현재 연구 실행에는 없는 기한이 남아 있습니다.**

   연구 수행 계약은 같은 실행에서 형식화할 조건으로 “실행 기한 안에 결과를 제출할 시간이 남았다고 판단”할 것을 요구합니다. 현재 실행기는 작업 예산 AI에 `call_deadline=None`을 적용하고, README도 시간 제한이 없다고 설명합니다. 기한 없는 실행에서 그 조건을 어떻게 판단하는지는 정하지 않았습니다. 따라서 형식화를 언제 시도할지에 불필요한 해석 차이가 생깁니다. 실제 형식화가 반드시 생략된다고 단정할 근거는 없지만 문서 조건은 현행 실행 계약에 맞춰야 합니다. [역할 조건](source/.claude/skills/do-math/계약/연구-수행.md#L54), [실행기의 기한 분기](source/.claude/skills/do-math/scripts/do_math/engine.py#L3324), [운영 계약](source/.claude/skills/do-math/README.md#L111).

복잡성에 관한 수정 방향도 위 지적에서 구체화됩니다. `overflow_disposition`과 `suggested_disposition`처럼 생성하지만 처분에 쓰지 않는 값, 묶음별 처리를 앞에서 다시 전체 거부하는 중복 관문, 내부 기능에 닿지 못하는 설정 경계를 먼저 정리하는 편이 좋습니다. 코드 분량만으로 새 구조나 검사를 추가할 이유는 확인되지 않았습니다.
