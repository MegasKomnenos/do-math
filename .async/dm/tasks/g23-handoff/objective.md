# 기존 보존 요구와 재검토 영역을 현재 수용 근거·남김에 연결한다

g1-handoff는 원래 stage1 19·stage2 11 의무의 인계를 마쳤다. 이번 독립 작업은 G2의 K 보존61·P2 12와 G3의 기존 재검토25영역에 현재 수용된 판단·실제 근거·구체적인 남김을 연결한다. 충분한 기존 판단을 재사용하고 남은 일이 무엇인지 구별할 수 있는 인계가 결과다. 행을 채운 사실을 전체 G2/G3 충족으로 선언하거나 최종 G8 review를 대신하지 않는다. 제품 변경은 없다.

## 원문과 입력

SESSION_JSON, task.json, 고정 inputs/context.md·plan.md·seams.md와 workspace의 do-math AGENTS.md를 읽는다. 기준은 manager0082의 수용판이다. 실제 선행은 g1-handoff와 g5-core-gaps의 수용 결과다. g5-core-tail과 g7-scheduler는 진행 중이므로 그 workspace/미완성 보고를 소비하거나 기다리지 않는다.

legacy root는 C:/math/docs/do-math/continuous-development-2026-10-13이다. requirements-index.json의 group=preservation은 K-01~K-78의 비연속61개이며 group=p2는 원12개다. 원문 source와 user-decisions.md가 권위다. phases/001/tasks/closure-map/evidence/requirement-state.json의 해당73행과 prior-review-state.json의 review_units25개는 초기 질문·근거의 출발점이다. 초기 classification을 현재 사실로 복사하지 않는다. tracking-state.json과 당시 board는 관련 연결이 불명확할 때 해당 slice만 읽는다. run:은 legacy root, repo:는 자기 workspace 또는 명시된 원자료다.

현재 수용표와 records/tasks/ID/report.json, evidence/judgment.md 또는 기존 conclusion.md, 해당 manager review와 integration을 먼저 사용한다. keep-runner/templates/isolation/inputs/storage/evidence/contracts/proof/rejections 및 proof-baseline, storage 후속, r/structure/g4/g5 결과를 필요한 K/P2/PR 성질에만 연결한다. g1-handoff/evidence/obligation-state.json은 공유 근거를 찾는 자료이고 managers/0082/handoff-delta.json은 최신 core 수용분의 한정 보충이다. 이전 판단을 무관한 전체 로그·SHA·Git 이력 재수집으로 다시 감사하지 않는다. 실제 diff가 아직 검토되지 않은 질문을 매핑·파일 존재·task.complete만으로 유지 판정해서도 안 된다.

## 맡은 결과

1. evidence/preservation-state.json에 원 K61+P2 12를 중복·누락 없이 담는다. 원문 위치/성질, 관련 수용 task·manager·원보고, 현행 제품/시험의 정확한 파일·심볼, 확인된 범위와 판본·구체적 남김·최소 다음 행동을 기록한다. 과거 timeout 등 폐기된 수단은 최신 사용자 판단과 현재 계약으로 처리하며 결함 동작을 보존해야 할 정상 기대값으로 만들지 않는다.
2. evidence/prior-review-state.json에는 원 PR25 ID와 해당 역사 변경의 실제 검토 범위를 연결한다. 원 history_ids/review_slices를 수용된 실제 diff·현재 소비자·원보고 판단에 연결해 유지/교정/제거/추가판정 필요를 구별한다. 이미 근거가 충분한 slice는 재사용한다. 미검토 slice는 정확한 역사 ID·파일/심볼·질문·필요한 원자료와 최소 다음 검토를 남긴다. 25영역 매핑 완료와 실제 검토 완료는 다르며 누락된 근거를 추정해 채우지 않는다. 연결을 해명하는 좁은 정적 대조가 충분하면 이 task에서 마치되 무관한 전체 재감사는 하지 않는다.
3. 저장 K/PR에는 사용자 storage-scope-direction-2026-10-15.md·원설계3.3/A20/A22를 함께 적용한다. 기존 공통codec·검증게시·업무 시험과 최종 T3의 쓰기도달을 재사용한다. 철회한 전가족/전필드/새 reader/옛 head quota와 취소된 storage-questions/storage-task-state를 되살리지 않는다. 구체적 참조·게시·필드 결함 수리의 성과는 보존한다.
4. 현재 의미 판단이 충분하고 최종판 실행만 남은 상태, 진행 중 core/예약의 수용 diff만 필요한 상태, 외부 입력이 필요한 상태, 실제 미검토 질문을 구별한다. 진행 중 작업은 영향을 줄 성질과 나중에 확인할 diff만 적는다. g7-boundary-scope와 L01 Q1/Q2·원자료 공백을 새 조사·probe·질문 반복으로 대신하지 않는다. 전체 G4/fresh G5·G6·G7/G8의 소비판/관문 대기를 명시하고 부분 통과를 합산하지 않는다.
5. evidence/judgment.md는 재사용한 판단과 실제 남김·후속 소유를 간명하게 설명한다. 새 제품 결함을 확인하면 정확 근거·영향·최소 수정 범위만 보고한다. 기존 원문30의무 전체 재작성이나 새로운 추적 framework는 필요 없다.

## 최소 확인과 제출

writes=[]·시험슬롯0이다. 제품/시험/설명/미러·공용 context/plan/seams/queue/state·engine·다른 task·기존 원자료는 수정하지 않는다. 실행·새 시험·실호출·환경 변경·graphify 갱신은 하지 않는다. 필요한 과거 Git 조회는 git -C C:/math로 읽기 전용 수행한다.

73개 원요구와25개 원영역의 ID 일치, 판단의 참조 경로·현행 정의와 범위, 실제 남김의 누락 여부를 정적으로 확인하면 충분하다. 모든 과거 원보고를 다시 실행하거나 모든 파일 hash를 재수집하지 않는다. 인계 완료는 모든 의미 미결의 해소를 뜻하지 않는다. report.json에 직접 확인한 범위와 미확인을 구별하고 changes=[]로 제출한다. python C:/math/services/async-development/check.py report C:/math/.async/dm g23-handoff를 통과시킨다.
