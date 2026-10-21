# 사용자 요구와 수용된 전체 do-math의 최종 독립 대조

## 얻어야 할 결과

수용한 전체 변경이 사용자의 R1~R7을 충족해 do-math의 실제 연구 진행을 막던 역할·단계 인계·검사 공백을 고쳤는지 독립적으로 판단한다. 제품을 수정하지 않는 review다. 구현자의 완료 주장이나 통과 수를 그대로 승인하지 않고 실제 현재 계약과 생산자·소비자·후속 상태를 연결해 판단한다. 최종 프로젝트 완료는 이 report를 수용한 manager가 결정한다.

먼저 inputs/context.md, plan.md, seams.md와 `C:\math\.async\dm-flow-repair-20261021\user-messages.md`의 최신 정정을 읽는다. 정본의 AGENTS.md와 관련 `scripts/이음새-정본.md`·`scripts/tests/시험-지침.md`도 읽는다. 현행 요구는 context R1~R7이고 원문 5~7번 정정에 따라 사전/적용 공통 판단을 한곳에서 호출하는 구조를 평가한다. 설계의 구체 enum/필드 수·예전 제안은 사용자 요구가 아니다.

## 입력과 정확한 판본

선행 `integration-repair-check`가 수용된 현재 사본을 검토한다. 그 의존관계는 role-flow-design, shared-validation-hashes, batch-payload-reads, windows-patch-guidance, codex-refresh-diagnostics, role-question-flow, intent-check-evidence의 모든 work를 포함한다. 정본은 workspace의 `.claude/skills/do-math`, 공식 Codex 사본은 `.agents/skills/do-math`다.

docs/는 snapshot_paths 밖이다. 다음 결과 문서는 공용 소스 `C:\math\docs\do-math\flow-repair-20261021\`에서 읽기 전용으로 사용한다: `role-flow-design.md`, `shared-validation-hashes.md`, `batch-payload-reads.md`, `windows-patch-guidance.md`, `codex-refresh-diagnostics.md`, `role-question-flow.md`, `intent-check-evidence.md`, `integration-repair-check.md`. 각 문서는 안내이며 판단은 실제 현재 코드와 원 영구 evidence로 뒷받침한다.

각 task의 report.json·evidence/·integration.json은 `C:\math\.async\dm-flow-repair-20261021\tasks\TASK-ID\`에 남는다. 최근 판본 대조는 `managers\0008\verification-summary.json`과 `decision.md`, 실제 실행은 `tasks\integration-repair-check\evidence\{t2-flows,recheck-1,boundaries-and-recheck,final-fixtures}\report.json`에 있다. 초기 감사 입력·원 응답은 context 3절의 경로를 필요한 만큼 읽는다. 원자료의 사본 재현과 현행 schema의 정상 적용을 혼동하지 않는다. 정리된 과거 workspace를 영구 입력으로 쓰지 않는다. 과거 파일이 꼭 필요하면 서비스의 `workspaces.py restore RECORDS TASK baseline|result NEW_DIRECTORY [PATH ...]`로 별도 디렉터리에 복원한다.

## 대조할 실제 사용 결과

1. **R1 역할 전체의 적합성.** SKILL 읽기 대응표·contracts.ROLES와 동적 역할/독립 운영·설치 복구의 실제 모집단, common/role 지급, 입력 생성과 출력 소비를 대조한다. 유지/수정한 목적·책임·판단 범위·재량·인계가 전체 연구 목적에 맞는지 평가한다. 검토자가 지적의 타당성·원문·반대 근거·자기 오독을 확인하도록 하고, 수행자가 착수 후 할 도구 확인·연구 결과 입증을 검토 승인 의무로 넓히지 않았는지 본다. 명확한 실제 허가 부재·미지원 지적은 계속 가능해야 한다. 몇 역할만 읽고 전체 평가로 확대하지 않는다.
2. **R2 정상 처리와 예외 재량.** 정상 개정은 수행되며 잘못된 AI 요청의 무수정 종결은 실제 요청 의무를 정산하는지 본다. 사용자 목표/권한·사용자 revise·독립 승인·연구 완료를 AI 처분으로 대신하지 않아야 한다. 자료 부족은 실제 대기로, 새 근거는 실제 독립 후속 판단으로 이어지고 같은 기초의 무한 재검토를 만들지 않아야 한다. 개정 외 단계 연결도 설계의 전체 모집단과 실제 소비를 대조한다. 이번 `revisions.resolved_targets(...,consumer_targets=...)`의 부모·자동 실패·명시 해소에서 선택적 자식 unchanged가 필수 소비자를 지우지 않는지도 포함한다. 일반 요청마다 의심·반려·새 필수 증명 절차를 추가한 것으로 바꾸지 않는다.
3. **R3 질문의 실제 처리.** 원 보고/안정된 의무→실제 담당 action/execution→봉인 근거/처분→해소·대기·이관→영향받은 계약/개정/계획/의도 검사 후속을 코드와 실행 근거로 연결한다. 같은 의무 재전달/재시작·고정 generation/대상·늦은 결과·새 대상/관찰 보존, 사용자 pause/HOLD에서 재개하지 않는 범위를 본다. QU 전체 status나 영수증 존재만으로 후속을 반복하지 않으며 질문 해소는 승인·완료와 구별돼야 한다. 의도 검사는 같은 원문/import_id/묶음 SHA·이전 봉인/history·새 독립 검사 실행 계보·명시 승인/owner 적용 경계를 포함한다.
4. **R4~R5 공통 판단·입력·복구.** 생산자 사전/중앙 접수/preview/적용이 같은 의미의 고정 입력과 공통 inspect를 소비하고 live 효력·권한·출처·내용·CAS 추가 검사는 위치에 맞게 유지하는지 본다. previous_hashes 누락·잘못된 값·검사 입력 결함·실제 전제 변경이 올바른 오류와 출력 수리/재판단/대기로 이어지는지 원 응답 재현과 현재 소비를 대조한다. planning의 catalog→저장 과제 투영이 원 content_sha256이나 필수 검사 자체를 제거하지 않으며 정상 완료 평가를 허용하는지 포함한다.
5. **R6과 R7.1 실제 안내 지급.** PowerShell/cmd/JSON과 패치 도구 계약에 맞는 예시가 명령 작성 역할의 실제 common 프롬프트에 지급되는지 확인한다. 선행 무해 호출·실제 패치 거부/재독/단일 Update 다중 hunk와 지급 근거를 사용한다. 미확보 과거 패치 본문·wrapper argv나 미래 모델 준수까지 인증하지 않는다.
6. **R7.2 진단 개선과 한계.** 목록 갱신 timeout의 확인된 위치·자료·부가 stderr 원바이트 색인·result artifact 보존/소비가 완료 판정과 분리되는지 본다. 정상 final 수락 실행을 전체 실패로 바꾸거나 외부 원인을 단정하지 않아야 한다. 현재 call_result 문서 소유자와 실제 소비 시험의 연결도 포함한다. 외부 네트워크/공급자 내부 원인 미확정은 사실로 남긴다.
7. **R7.3 정확 복원과 Git 호출.** 같은 exact snapshot의 선읽기/재사용·공통 구조/해시/길이/정확 판본/입출력·후속 decode 검사가 유지되는지 보고, 원 snapshot 실제 bytes·논리 해시·Git 수/시간 한 쌍과 현재 실제 Git 경계의 근거를 대조한다. 한 쌍을 일반 성능 보장으로 확대하지 않는다.
8. **같은 현행 계약.** 역할 문서/입력 지급·schema·코드·첫 reader·저장/retention·시험·제품 이음새·공식 미러가 같은 의미를 가리키는지 본다. 선행 설계 문서의 제안보다 현재 수용판을 우선한다. 구판 호환·변환이나 불필요한 일반 검증 장치를 추가하지 않았는지도 사용자 목적에 비추어 판단한다.

## 필요한 만큼만 확인한다

현재 영구 evidence를 읽고 정적 판단으로 충분하면 종료한다. 통합 task는 T2+flows 4610개를 한 번 실행한 뒤 실패/미실행과 수정 영향만 179→32→2개로 재확인했다. 최초 127 비통과와 후속 관측 비통과는 후속 기록에서 모두 passed이며 Windows symlink 권한 skip 1개는 미확인이다. 이들은 여러 판본이므로 마지막 판본의 전체 회귀 통과가 아니다. 최종 두 fixture 전후 제품 Python은 같고 최종 report의 Python 930개 hash가 공용 소스와 일치한다. 실제 Git/CLI/설치 도구의 작은 boundary, probe verified, 공식 미러 drift 없음 근거도 있다.

기존 근거가 답하지 못하는 구체적 동작이 있으면 먼저 불확실성을 명시하고 필요한 작은 기존 입력/선택만 확인한다. 제품 시험이 필요하면 공식 run_tests.py와 제품 시험 지침을 따르고 출력/임시 근거는 task evidence에 남긴다. 실행 중 소스 편집이나 최종 순변경을 남기지 않는다. 전체 모집단·과거 성능/무해 명령/원 CLI 재생·새 live 모델/scholarly/실제 Lean/설치 복구 AI를 일괄 반복할 필요는 없다. 모델/Lean 대역의 통과는 실제 모델 판단 정확도나 일반 연구 효능의 증거가 아니다.

원 연구·감사·HOLD·예약·graphify·서비스 state/queue/공용 문서·다른 task는 수정하거나 재개하지 않는다. writes는 빈 목록이다. 새로운 제품 수리는 manager가 관련 구현·최소 확인을 한 work로 배정한다.

## 결과 인계

task 디렉터리의 `assessment.md`에 R1~R7별 결론·실제 경로/함수·사용 결과·실행 또는 정적 근거·확인 한계를 남긴다. 역할 전체/파이프라인 모집단 검토 범위와 남은 미확인 부분도 구체적으로 적는다. 실제 사용을 막는 발견은 재현 조건·영향·최소 후속 범위를 적고 선택 개선·확인되지 않은 외부 원인과 구별한다. 문제가 없으면 그 결론의 범위를 명시하고 새 개선 작업을 억지로 만들지 않는다.

report.json은 protocol의 기존 형식으로 작성한다. changes는 [], verification은 실제 읽은/실행한 근거와 한계, findings에는 발견 및 사용자 목표 충족에 대한 최종 판단을 담는다. status는 이 review 배정 완료 여부이며 제품이 통과했다고 자동 해석되지 않는다. 제출 전 `python C:\math\services\async-development\check.py report C:\math\.async\dm-flow-repair-20261021 final-goal-review`로 형식/순변경 범위를 확인한다. 최종 review 수용과 전체 완료 판단은 manager의 후속이다.
