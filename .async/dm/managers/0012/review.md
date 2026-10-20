# manager 0012: r14 부분 수용과 독립 제출 입구 배정

이번 inbox의 완료 사건은 r14이며 r03-fix·r08은 실행 중이다. 시작한 두 배정과 입력은 바꾸지 않았다. 이후 도착하는 사건은 다음 manager가 처리한다.

## 수용 결과와 한계

r14 report 검사는 PASS다. 정본 parallel.py·scheduler.py·progress 시험과 미러의 실제6변경, 미러3쌍, 관련 불변20파일, 기존 progress3메서드의 AST를 대조했다. 변경 파일의 공용판은 모두 task base와 같았다. workspaces.py integrate는 충돌 없이6파일을 반영했다. 구체적인 SHA·원보고 비교는 source-review.json, 통합 처리는 tasks/r14/integration.json이다. manager 제품 시험은0이다.

F1은 scheduler가 생산자와 같은 guard 아래 owner 바퀴의 future별 진입 관찰량을 고정하고, 여러 pump/collect가 같은 잔여 허용량을 차감하여 해결했다. 단독 pump도 진입 관찰·callback queue의 양을 함께 고정한다. F2는 완료가 있으면 pump가 경쟁 관찰을 양보하고 collect가 관찰 부채가 작은 future부터 처리하여 해결했다. controls 뒤 continuation을 받는 순서, 본인 관찰을 모두 적용한 뒤 본인 결과를 수신하는 순서, 오류/stop/close의 책임을 유지한다. 이미 처리 중인 큰 callback 내부의 완료 지연까지 해결된 것은 아니다.

red-machine의32/512초와 red-pass3의(entry1,applied2)는 정확 실패 row에서 확인했다. 제출된 두 새 회귀는 같은 native1/64/1024입력·사건당 가상0.25초·완료→실제 기계 수신≤1초/owner≤1, 실제 새 묶음 도착과 해당 바퀴(1,1), 뒤 pause·정산을 검사한다. 1초는 기존 시험의 고정 상한이며 제품의 벽시계 SLA가 아니다. 준비 미흡 red-pass와 native 미도착 red-pass2는 runtime 반례와 구별한다.

related-final은16선택/16고유row 중15passed·구조1failed/exit1, final-snapshots는4선택/4passed/exit0이다. 마지막875 Python SHA는 제출판과 전건 일치하고 실행 중 변경은 없다. 앞 보고와의 차이는 parallel/scheduler의 snapshot lock이다. 서로 다른 판본의 결과를 단일 전체 통과로 합산하지 않는다. 각 하위 원보고 row·선택·해시·기록된 exit를 직접 비교했다. 미러3쌍과 비용 캐시의 base 복원도 확인했다.

구조 실패44개 unpinned_rejection은 task가 저장한 base/workspace 비교 배열이 정확히 같으며 검사기도 불변이다. manager가 그 정적 분석을 새로 재실행한 것은 아니다. 이번 수리에 새로 생긴 실패로 보지 않지만, 원래 존재했다는 이유로 면제하지 않는다. G3/G4 전에 관련 단언/helper를 묶어 실제 이슈인지 검사기 판정 문제인지 해결할 남김으로 plan에 기록한다. 개별44개 task로 나누지 않는다.

F3는 실제 관찰 함수 진입에서 held Lean worker를 완료시키는 atomic-counterexample의64/1024입력에서 가상32/512초 지연으로 남는다. diagnostic 원문 SHA가 원보고와 같다. 마지막 snapshot lock 전 판본이며 core의 관찰 본문은 제출판까지 불변이다. 따라서 미해결로 유지하되 제출판에서 재실행했다고 하지 않는다. 관측기가 함수 진입에서 묶음 전체 비용을 먼저 부과하므로, 후속은 제품의 실제 처리 단위와 이 비용 모델의 대응도 판단해야 한다. core 내부에 양보를 추가하는 특정 방법을 확정 요구로 삼지 않는다.

r14는 부분 수용한다. R14/8-A와 PR11 진행성 slice의 F1/F2는 수리됐고 F3는 열려 있다. R11의 종료 판정, R15/R16 전체 정산, 다른 K/P2, G4~G8·L01·Windows1314 미검사는 그대로다. runtime 변경이 관찰 record 모양·내용을 바꾸지 않았으므로 진행 중 r03-fix의 schema 전제는 유지된다.

## 후속과 실제 선행 관계

r14-fix는 F3의 실제 원인 수리·지속 회귀·관찰 순서/원 bytes/receipt/저장 보존을 한 task로 맡는다. r14와 r08이 선행이다. r14는 수리의 출발점이며 r08은 core_engine.py의 이미 시작한 쓰기 소유권 때문에 필요하다. r03-fix나 r09의 종료는 요구하지 않는다. 전체 묶음의 원자 처리 전제를 줄이는 방법부터 검토하며 특정 새 스케줄링 체계를 지시하지 않는다. input1/64/1024·사건 비용·고정 상한을 줄여 통과시키지 않는다. 실제 처리 단위가 바뀌면 비용 관측도 그 단위에 연결하고 총입력/비용 보존과 변경 이유를 남긴다.

r09는 별도 제출 확장·참조 경계의 원래 R09/2-A 질문을 실제 생산/중앙 수신/봉인·적용·재전달에 연결한다. 기존13모듈/81사례라는 역사 수치를 현재 전건 인증으로 쓰지 않는다. 현재 submission_obligations/owner helper와 직접 시험에서 가까운 공백·수리·최소 확인을 묶고 PR07 B29/B47의 관련 slice를 함께 판단한다. r05에서 수용한 null/외부 값 성질을 재사용한다. 관찰/제어/core/record schema는 읽기 전용이며 r08·r03-fix·r14-fix와 의미 있는 쓰기가 독립이다. 선행은 없고 즉시 파견 가능하다. 핵심 owner 결함에 core 변경이 실제 필요하면 정확 반례와 필요한 파일을 보고한다.

공용 context·plan·seams와 두 objective를 먼저 완성하고, 기존 task 정의를 보존한 queue.pending.json을 검사한다. 검사한 파일 자체를 os.replace로 queue.json에 마지막 게시한다. r14를 accepted에 추가하되 전체 status는 active다. 제품 수정은 task에 맡기고 manager는 검수·통합·기록·배정만 수행했다.
