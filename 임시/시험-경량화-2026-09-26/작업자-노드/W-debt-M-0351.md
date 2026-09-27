---
worker_id: W-debt
layer: 1
title: do-math 기준선 실패 시험 16개의 원인 판정과 수리, 관찰 적용의 무한 소진으로 인한 소유 루프 기아 수리
convention_version: 27
---

## 맥락

do-math 시험 경량화 작업(공통 계약 `임시/시험-경량화-2026-09-26/계약.md`, Git 제외 경로라 정리로 사라질 수 있다)에서 W-debt 작업자로 기준 커밋 fe59ca0부터 실패하던 시험 16개의 수리를 맡았다. 작업은 worktree `C:/math-worktrees/t-debt`, 브랜치 `t-debt`에서 했다. 시험마다 제품 결함, 폐기된 계약을 기대하는 시험, 현행 계약의 입력을 만들지 못하는 fixture 중 어느 쪽이 원인인지 가리고 원인 쪽을 고쳤다.

원인은 여섯 묶음이었다.
- **폐기되거나 바뀐 계약을 기대한 시험.** `ControlQueueConnections`의 resume 부분 시험은 1라운드(fe59ca0)가 지운 도달 불가 엔진 분기를 겨냥했다. 실제 resume은 `lifecycle_engine._apply_extended_control`이 처리하고 행동을 대기열에 넣지 않는다. 문서 예시 grant 시험은 `초기화-운전.md`가 형식 예시라고 밝힌 만료 시각 자리표시자를 시각으로 파싱했다. 병렬 3호출 시험은 `check().passed`를 요구했지만, 현행 `state_checks`는 신뢰 환경이 있으면 `governance_trust`를 늘 미검사(incomplete)로 보고한다. 다른 시험(`test_engine.assert_persisted_state_clean`)은 이미 이 형태를 깨끗한 상태로 단언한다.
- **학술 증거 모집단.** 1라운드가 `academic.EVIDENCE_FAMILIES`에서 `runtime.artifacts`를 뺐다. 산출물 증거는 엔진이 저장 바이트로 해석한다(`_academic_evidence`). 시험 두 개는 여전히 `runtime["artifacts"]`에 증거를 두었다.
- **실행 프로필 판본.** 평가가 없는 작업 과제는 high 등급을 요구하는데(`model_policy.selection`), fixture가 low 판본 하나만 채택하거나 과제 후보에 프로필 참조를 비워 두었다.
- **ReviewFailureTests 5개.** 증상으로 보고된 초기 해석 `execution_incomplete`는 원인이 아니었다. 씨앗 fixture(`FakeEngine.activate`)가 일부러 그렇게 끝낸다. 실제로는 형식 검사가 `formal_authority` 대기로 멈췄다. formal_check 프로필의 명령(`['test-double']`)이 씨앗 신뢰 환경의 명령과 달랐다. `state_fixtures.ACTIVE_LEAN_COMMAND` 관례를 따르지 않은 것이다.
- **스케줄러 helper.** `test_session_scheduler.engine()`이 계획을 거치지 않고 `research_work`를 직접 넣었다. 그래서 `task_became_ready` 사건이 소비되지 않고 남았고, 엔진은 그 사건으로 `research_plan`을 예약했다. 결정 4 뒤로 운영 역할은 슬롯 없이 바로 배정되므로 이 계획이 작업 전용 runner로 가서 실패했다. helper는 이제 실제 계획(`ScriptedRunner`)이 준비된 과제를 선택하게 한다.
- **관찰 적용의 무한 소진.** 운영 병행 시험은 2라운드 `parallel.ModelCalls._apply_observations`의 `while future.observations`에서 막혔다. 실행 중인 호출이 관찰을 계속 붙이면 pump가 끝나지 않아, 소유 루프가 배정·live 운영 점검·제어를 하지 못했다. 계측으로 첫 작업 하나만 110초 동안 돌고 게시가 초당 1회 이어진 것을 확인했다. 진입 시점의 행 수만 적용하도록 고쳤다(2라운드 전 `events` 경로의 `qsize()` 한정과 같은 성질).

## 터득한 것

**보고된 증상과 실패 원인을 구별해야 했다.** ReviewFailureTests의 공통 증상은 초기 해석 실패였지만, 그 실행들은 fixture가 의도적으로 만든 것이었다. drive가 멈춘 시점의 `waiting_actions`를 출력하니 원인이 바로 드러났다. 대기 사유와 대기열을 먼저 보는 진단이 증상 목록보다 빨랐다.

**helper 하나를 제품 경로에 맞추면 그 helper를 쓰는 다른 시험의 전제가 드러난다.** helper를 실제 계획 선택으로 바꾸자 이전에 통과하던 `test_blocked_high_priority...`가 실패했다. 선택된 작업은 계획의 모델 판단을 들고 있어, 과제의 모델 평가를 바꾼 뒤 옛 대기열을 되돌리는 시험의 조작이 더는 통하지 않았다. 제품에서는 계약이 바뀐 과제의 선택이 풀리고 새 계획이 다시 선택하므로, 시험도 그 경로를 따르도록 고쳤다.

**운영 병행 시험은 fixture가 제품보다 열 배 가혹했다.** 시험 worker는 0.1초마다 관찰을 보냈지만, 실제 runner는 stdout 조각마다 한 번, 한가하면 1초에 한 번 보낸다(`model_runner.observe`). 관찰 하나의 적용은 runtime 깊은 복사와 때로 게시를 포함해 부하 아래 0.1초를 넘는다. 실제 주기로 맞추고 걸림 방지 기한을 20초에서 120초로 늘리면(형제 runner와 같은 값) 제품 수리 없이도 통과했다. 그래서 제품 수리는 이 시험의 필요조건이 아니라 독립된 활성 결함의 수리로 보고했다. 한정 없는 소진은 실제 출력이 흐르는 호출(0.2초 폴링)에서도 같은 기아를 낼 수 있다. 직접 단위 시험(`test_machine_parallel...test_one_pump_applies_only_the_rows_queued_before_it`)으로 고정했으며, 수리 전 코드에서는 한 번의 pump가 행 0~51을 모두 적용해 실패한다.

**계획 목록 밖 실패 3건을 발견했다.** 같은 `AcademicConsumerTests` 클래스에서 목록에 없던 시험 3개가 main에서 실패했다. 과제 평가에 현행 계획 출력 스키마가 요구하는 `reason`·`unresolved`가 없었다. 같은 파일의 같은 fixture 결함이라 함께 고쳤다.

**남은 두 실패는 반복 실행 대신 정적 분석으로 풀었다(사용자 지시).** 반복 실행은 부하에 따라 결과가 흔들려 원인을 가리지 못했고, 코드 경로를 읽는 편이 빨랐다.
- `test_large_own_review_history...`: 검토 입력 한도는 고정된 프로필의 `input.max_input_bytes`다(`context_store.prepare_role_input`, 7d2597e부터). 시험이 바꾼 `config["max_input_bytes"]`는 한 번도 효과가 없었다. 2MB 한도 아래의 840KB 이력은 들어가서 호출이 났다. 이력이 실제 한도를 넘게 고쳤다. `role_review`가 필수 입력이라 넘치면 `restored_dialogue` 원인으로 호출 없이 멈춘다.
- 운영 병행 시험의 부하 의존 실패: 시험 worker의 운영 점검이 자기 산출을 제출하기 전에 작업을 풀어 주었다. 작업이 먼저 끝나면 엔진이 live 점검을 폐기 대상으로 보고 제출을 거부한다(`_obsolete_action_reason`, `_publish_control_request`). 제출 수락 뒤에 풀어 주도록 고쳤다. 허용 결과 `output_preserved_after_target_change`는 현행 outcome이 아니다. 현재는 `result_disposition.kind`로 표현된다.

## 작업 너머 시사점

- 관찰 하나당 소유 루프 비용(`_observe_running`의 runtime·tracker 깊은 복사, `_unchanged` 비교, 게시)이 부하 아래 관찰 도착 간격보다 크다. 호출 여럿이 출력을 흘리면 소진을 한정해도 적용 대기 관찰이 쌓인다. 경량화의 제품 비용 항목(직렬화·게시)과 같은 뿌리이므로 dream에서 묶을 후보다.
- 병렬 브랜치 작업자가 각자 layer-1 번호를 고르므로 번호 충돌 가능성이 있다. 이 노드는 t-git의 M-0350 다음 번호를 골랐고, t-eng·t-fix와의 충돌은 통합자가 처리한다.
