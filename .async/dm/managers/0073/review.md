# 0073: 게시 부분 수용과 Lean·신뢰 후속

## 판단과 반영

inbox의 완료 사건은 g5-publish(exit0) 하나다. report는 partial이고 그 상태를 유지한다. 정본8제품·9시험·1설명과 공식미러18쌍, 총36파일을 읽고 `check.py report` PASS 뒤 `workspaces.py integrate C:/math C:/math/.async/dm g5-publish`로 충돌 없이 통합했다. integration의36경로와 보고 변경 목록, 통합 뒤 공용/제출 bytes가 같다. 수용은 이 부분 결과와 유효한 수리의 수용이며 전체 G5 완료가 아니다. 근거는 integration-check.json과 원 task integration.json이다.

제품 수정은 manager가 직접 하지 않았다. 다음 큐에는 g5-publish를 accepted에 넣고 기존89개 정의·취소2개와 진행 중 g5-calls/g5-state의 정의/objective를 보존한다. 새g5-trust 포함90개 정의·85개 수용·active다.

## 원코드 대조

- delegations.prepare_application은 같은 delegation/case를 먼저 순회해 원case·현재/보존basis를 검사한다. 뒤 hash-ID 재조회만 제거했고 정확한 보존 승인/hash·stale 반려와 입력 불변 단언을 보완했다.
- integration._reviewed_impact_request는 실제 read_sealed_submission과 중앙 payload의 영향 검토 확장 금지·maintenance 단일 응답 계약을 소비한다. 지정 action·독립성·실제 게시 영수증·계산/선언 영향 합집합 검사는 남는다. 중복 bundle-count 검사 제거를 현재 생산/수신과 대조했다.
- knowledge.replace_knowledge의 동일한 usable Lean 원문은 knowledge_records.create_candidate가 임시 formal result를 만든다는 전제 아래 기존 FR 재사용을 수행한다. proposal_view는 실제 저장 참조와 trust_validation.ENVIRONMENT_REQUIRED의 allowed_axioms 필수성을 소비한다. 누락 환경/필드를 정상처럼 보충하는 경로를 줄였다.
- retention._run_path는 check_path_segment와 _physical의 reparse 반려를 사용하므로 뒤 parent 이탈 검사를 반복하지 않는다. 실제 junction 반려는 파일 symlink 조건의 증거가 아니다.
- review_cycle.accept_result는 next_actions가 반환한 정확한 기록 대체 action만 받는다. 그 뒤 continuity break와 grant ID/hash 검사는 유지한다. review_engine의 source path/sha256은 닫힌 저장형식의 필수값이며 fixed_research_reference_path는 이미 지급된 source에 None을 돌려준다. initialization.activation_requirements는 실제 build_review_policy와 채택hash 검사를 수행하고 lifecycle_engine._activate_initialization가 소비한다. 이 전제와 retry의 활성 상태/현재hash 검사를 대조했다.
- submission.payload_issues의 배열 오류는 검사 slice의 정수 index를 원member 좌표로 돌린다. container 전역 반려와 실제 봉인 bytes/check/capture eligibility는 유지한다. 새/기존시험의 정확 rule/path/receipt·원bytes·입력불변 단언을 확인했다.

새 설명에는 작은 부정확성이 있다. scripts/이음새-정본.md §3의 `initialization.activation_gaps`는 현재 존재하지 않고 실제 함수는 `activation_requirements`다. review_engine의 `validate_lifecycle already built` 주석도 검증 주체를 정확히 연결해야 한다. 동작 수용과 별개로 이 두 설명 정정을 g5-trust에 묶었다. manager가 제품 문서를 직접 수정하지 않았다.

## 필요한 검수와 한계

submitted/invocation.json·raw/report.json·coverage.json을 직접 읽었다. 선택41=고유실제41행=41passed, fixture/failed/error/not_run/skip0, complete/successful=true, changed_during_run=[]다. 914Python 원SHA가 현재 제출판과 모두 같고 정본/미러18쌍도 같다. 제출 원report·coverage와 외부 원위치 두 파일의 SHA가 같다. 원9제품의 base/전체T3/제출측정 SHA, 원미도달 목록과 좌표별 실제 raw도달도 대조했다. manager 제품시험0이다. 검수 스크립트와 결과는 verify.py·verification-review.json이다.

부분선택이므로 branch_gate/최상위passed=false·closing_eligible=false·관측exit1이다. 공식45.3초/외부46.062초·소프트초과17행을 유지한다. 원58arc/50행은42arc/42행 도달·9arc/5행 제거·7arc/3행 남김이다. 제거는 실제 diff와 위 계약으로 판단했으며 과거좌표 처분을 새 분기까지 포함한 최종전체 gap 수로 해석하지 않는다. 새skip/제외·층/임계값 변경은 없다.

앞focused1/2/3·final·seat-final의 실패/오류와 수정 이력은 보존하며 이번 단일 제출판41passed/도달에 합산하지 않았다. 앞focused2의 구조시험 unpinned_rejection은 배정 밖 test_scheduling_close_parallel.py이고 base/제출 SHA가 같다. 이 문제는 이미 g5-state에 배정돼 있어 중복 배정하지 않는다. 외부 과거증거 전체 감사·이전시험 재실행은 하지 않았다. 로컬 Git HEAD는 측정 기준일 뿐 공용main/성공 인증이 아니다.

## 실제 남김과 배정

g5-publish의 남김 중 knowledge2arc/1행은 Lean·신뢰 후속과 실제로 연결된다. `_basis_records`의 BASIS_FAMILIES에는 kind-definition/trust-environment가 있으나 `_apply_impact_effects`의 generic else가 쓰는 input_current/use_history는 record_schemas의 kind_definitions 및 trust_validation의 환경 형식에 없다. 이 정적 불일치는 확인했지만 실제 합법적인 영향 생산자로 게시 실패를 재현하지는 않았다. 새task는 도달/의미를 먼저 확인하며, 불필요 분기 축소 또는 필요한 생산/저장/소비 수리를 선택한다. 임의의 필드 추가를 완료 조건으로 정하지 않는다. invalidate_environment의 독립 active use 남김도 함께 맡긴다.

새g5-trust는 미배정 formal.py·formal_engine.py·setup_lean.py의43arc/68행과 위2arc/1행·두 설명 정정을 맡는다. 앞3제품은 원전체측정SHA와 공용판이 같다. g5-full·g5-publish는 실제 원측정/수용지식 결과 선행이며 두running 종료나 자원 슬롯을 가짜 depends_on으로 표현하지 않는다. 허용정본36/미러36경로는 running 두task와 교집합0이고 각시험슬롯1로 총3이다. max_workers10·gpt-6.1-sol/high를 유지한다. 상세 입력·허용파일·현재SHA·좌표·남김은 task objective.md·gap-scope.json과 assignment-scope.json에 있다.

나머지 게시5arc/2행은 external_engine의 무선행retry/게시신원 불일치, integration의 영향검토 제외 안정화, retention의 nameless source alias, submission의 grant 없는 학술영수증이다. 실제caller/계약을 확인할 작은 보완으로 묶어 다음 가용슬롯에 배정한다. worker의 script/frozen13arc/25행과 I/O환경6arc/10행도 남는다. 이들은 지원계약/원설계5.5의 사유 있는 처분 또는 실제 조건의 직접 근거가 필요하다. 자식/T4 도달을 T3에 수동 합치거나 Windows1314 조건을 같은 권한probe로 반복하지 않는다. 전체관문과 G7 실경계는 별도다.

## 사용자 저장 범위 지시의 적용

sources/storage-scope-direction-2026-10-15.md와 원설계3.3/A22·5.5를 읽었다. 이미 수용된 공통codec/저장검증/업무시험은 재사용한다. 새task는 유한한 실제 gap과 확인한 형식 불일치만 다루며 전가족·전필드·새reader·옛head quota나 장기감사를 부활시키지 않는다. 설명 정정은 같은 task에 묶고 별도 문서task/반복시험을 만들지 않았다. 필수 G1~G8을 줄이지 않는다.

수리 후 최종수용판 전체G4/G5와 G6~G8, G1~G3 최종연결·L01·실경계 조건이 남아 complete를 게시할 수 없다. 공용 context/plan/seams와 objective를 완성한 뒤 임시 queue를 검사하고 마지막으로 원자교체한다. 이후 새 완료 사건은 다음 manager가 처리한다.
