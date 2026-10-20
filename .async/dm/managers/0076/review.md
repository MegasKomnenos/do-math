# 0076: 지식 영향 수리의 부분 수용과 Lean·신뢰 남김

이번 inbox.completed는 g5-trust(returncode0) 한 건이다. 보고의 partial을 유지하여 유효한 수리와 확인을 수용한다. 실제 정본9개 diff와 공식미러9개를 읽었고, `check.py report` PASS 후 `workspaces.py integrate C:/math C:/math/.async/dm g5-trust`로 18파일을 충돌 없이 통합했다. 원보고는 변경하지 않았다. 진행 중 g5-core-rest·g5-entry-io의 정의/objective와 입력 사본은 유지한다.

## 제품 결과와 근거

`knowledge._apply_impact_effects`의 generic else가 kind_definitions/trust_environments에 저장 계약 밖 input_current/use_history를 추가하던 처분을 제거했다. `_basis_records`의 BASIS_FAMILIES, plan_impact의 선언 ID 허용/계산·선언 합집합, _confirmed_impact의 독립 확인, integration.bundle_impact_request→apply_reviewed_impacts 연결과 두 닫힌 저장 형식을 직접 읽었다. 다른 가족은 기존 전용 처분으로 처리되고 남은 두 권위 및 실행/활동은 원기록을 보존한다. 영향 ID는 knowledge_reassessment_required 사건과 후속 research_plan에 계속 남는다. 종류 효력 변경은 knowledge_io.withdraw_kind_definition, 신뢰 효력 변경은 knowledge.invalidate_environment가 소유한다. 스키마를 늘리지 않은 작은 정합 수리다.

새 ImpactAuthorityContracts 시험은 실제 종류 등록과 활성 Sim 신뢰 환경, 공개 지식 import에서 만든 current plan에 도메인 독립 확인 표본을 주어 apply_impact를 실행한다. 권위 원내용·상태/정확 사건·후속 역할과 실제 검증 게시·복원을 단언한다. 원 코드와 닫힌 형식의 불일치는 정적으로 대조했고 별도 수정 전 red 실행은 없다. 도메인 확인 표본을 새 봉인 모델 검토 실행이라고 주장하지 않는다. 기존 봉인/독립성 입구 근거는 재사용하며 외부 모델은 호출하지 않았다.

시험 diff는 독립 환경의 assessment use 보존, 부분 해소 후 원 owner 대기 보존, 공개 revise 후 input_changed·원 proposal·중단 결과 보존을 확인한다. 새 발견/설치·관찰 시험은 실제 임시 파일과 외부 I/O 대역을 사용한다. Path.resolve의 제한된 임시 위치 해석은 제품 discovery/verifier 반환 대역이 아니다. trust registration의 정확 baseline 거절, invalidation 후 활성화 실패·이전 권위 보존, 종료 미관측의 stopping/unknown과 원결과 보존, 재입장의 실행 비증가도 직접 단언한다. 이를 실제 Lean/Mathlib·Windows Job 종료·공용설치 성공으로 확대하지 않는다.

`review_engine` 변경은 주석뿐이다. initialization.activation_requirements가 review_policy.build_review_policy를 호출하고 lifecycle_engine._activate_initialization가 그 요구를 소비하는 실제 코드를 대조했다. 없는 activation_gaps 심볼과 잘못된 검증 주체 설명을 관련 이음새/지식 문서와 함께 정정했다.

## 확인 범위

verify.py·verification-review.json은 단일 final1 원report/coverage와 보존 사본의 SHA, 선택48=고유 실제48행/전건passed, fixture0·complete/successful=true·실행중변경0을 대조한다. 제출판917PythonSHA 전건 일치, 새store 측정5모듈·재사용0이다. gate/최상위passed=false·closing_eligible=false·관측exit1인 부분 T3이며 전체 G5 성공이 아니다. 공식98.6초/외부99.437초·소프트 초과8행은 원보고에 남는다. 앞판본 실패·성공·coverage를 합산하지 않았다. manager 제품시험은0이다.

원45arc/69행의 처분은 raw 도달35arc/58행·제거1arc/1행·남김9arc/10행이다. 4제품의 base/측정/제출SHA, 모든 reached좌표와 raw executed_branches/lines, remaining 목록을 대조했다. 삭제1/1은 knowledge의 위 generic 처분 diff와 연결했다. 새 제외는 없다. 이 수치는 과거 유한 좌표의 처분이며 최종 통합판 전체 gap 수가 아니다. 미러8쌍은 byte동일이고 새 test_trust_branch_contracts 한 쌍은 공식 .claude/→.agents/ 치환만 있다. integration-check.json은 통합 경로와 공용bytes를 확인한다.

## 후속 판단

새 g5-trust-rest는 수용 g5-trust만 선행으로 formal.py의 stopped return 1arc와 formal_engine.py의 guard8arc/10행을 묶는다. 같은 stop 동작 반복보다 try/finally·한 줄 반환과 raw좌표 해석을 먼저 확인한다. environment lexical 중복, 등록 None의 실제 review/activity/slot 입장, trust check의 초기 invalid guard, 같은 K 원문 변경 생산자, 최종 stop/정산 뒤 publication 오류를 현재 caller와 연결한다. 필요 없는 방어는 줄이고 필요한 입력/권한/증거/현재성·원결과 보존은 유지한다. None 불가능을 uncapped 역할만으로 단정하거나 합성 내부 오염으로 도달시키지 않는다.

이번 남김을 전수 생산자 감사나 새 시나리오 quota로 만들지 않는다. 사용자 storage-scope-direction과 원설계3.3/A22에 따라 공통 저장 검증·기존 업무 단언을 재사용하고, 구체 불확실성을 해소할 최소 수리/확인만 맡긴다. 이미 수용한 설치 CLI·영향 처분을 재개발하지 않으며 전가족/전필드/새reader/옛head quota·장기감사를 추가하지 않는다. 원래 G1~G8은 유지한다.

기존92정의·취소2건을 유지하고 g5-trust를 accepted에 추가해88개 수용한다. 새task 포함93정의·active, max_workers10·gpt-6.1-sol/high다. assignment-scope.json은 새 정확 writes와 두 running의 교집합0 및 배정/기존 objective 불변을 확인한다. core-rest1·entry-io1·trust-rest1의 시험슬롯 합계3이다. 진행 중 제공자는 자기 시작판에서 읽기전용으로 사용하며 미완성 코드를 가져오지 않는다. 실제 제공자 수정 필요가 발견되면 좁은 반례를 보고하도록 했다. 자원만의 의존관계와 모든 동료 종료 장벽을 만들지 않는다.

구체 잔여 처분 뒤 최종 수용판 G4/G5를 잇고, 최종 함수/진입색인이 필요한 G6와 G7 실경계·G1~G3 연결·L01·G8 review는 남긴다. 지금 중간판 전체 검사를 반복하지 않는다. 이 세션 중 뒤늦게 온 완료 사건은 다음 manager가 처리한다.

공용 context/plan/seams·새 objective와 gap-scope를 먼저 완성하고 queue.pending.json을 검사한다. 검사한 같은 bytes를 queue.json으로 원자 교체한 뒤 이번 공용 변경을 끝낸다.
