# 기반 1a·1d의 시험 경로와 정상 대역 판단

g23-handoff의 비B 기반 남김 중 1a 실행기/구조검사 도입과 1d Sim·정상 모델·Calls·템플릿/corpus 기초의 의미 판단을 맡는다. scope.json의 두 stage만 다룬다. 이미 수용한 B번호 검토나 K61/P2 판정을 다시 수행하는 작업이 아니며, 그 근거 밖에 남은 실제 hunk를 현재 정의·직접 소비에 연결해 처분한다.

SESSION_JSON/task.json/inputs 세 문서, 자기 workspace의 do-math AGENTS.md·시험-지침.md와 manager0089/review.md를 읽는다. g23-handoff/evidence/prior-review-state.json의 non_b_material, 원설계·진행.md·전환표, 실제 도입 diff가 입력이다. C:/math의 docs/기록/Git은 읽기 전용이며 과거 diff는 `git -C C:/math show/log`로 읽는다. 현재판은 자기 workspace 고정사본이다.

## 끝낼 질문

1. 1a 실행/구조검사의 최초 도입 hunk와 이후 실제 교정에서 선택 누락·fixture/subTest 실패·격리 미완료가 성공으로 사라지지 않는지, 기존 알려진 결함이 정상 기대값으로 굳어지지 않는지 판단한다. 구조검사의 목적과 실제 검출 대상을 구별한다. pr-records의 기준선/후보/PR05 차이 해명, keep-runner/keep-isolation/proof-baseline 및 B56의 이미 검토한 성질을 재사용하고 남은 hunk만 읽는다. 자료 부재를 같은 과거 실행 반복의 이유로 바꾸지 않는다.
2. 1d의 Sim/ModelDouble/Calls·템플릿 도입·A19/A25/corpus seed에 대해 정상 대역이 실제 제품의 제출/수신/영수증·종료 소유를 우회하지 않는지, 템플릿 복원이 준비의 계약·실패·필요 효과를 보존하는지 판단한다. B36/B48/B80과 keep-templates/keep-inputs/r14-fix/r15-r16의 한정 판단을 정확히 재사용한다. 합성 corpus 재생과 실제 공급자 호출의 증거 범위는 구별하며, 현재 quota/복수result 원자료를 새로 만들려고 실호출하지 않는다.
3. 최근 core 수용판의 receipt/활동 정산 변경은 managers/0089/handoff-delta.json·accepted-diff.txt로 연결한다. 이전 모델 계약에 맞춰 현행 제품을 되돌리지 않는다. 병행 pr-base-ports는 1b/1c, T4는 실제 현재 경계 실행을 맡으므로 그 미완성 자료를 기다리거나 읽지 않는다.

이 검토는 1932개 옛 시험/모든 disposition의 새 강도 감사가 아니다. PR05의1931→1932 차이는 pr-records에서 해명됐다. 1e/2 요구별 의미와 1f 이관의 수용된 K61/P2 근거는 그대로 재사용하며, 이 두 기반 질문에 필요한 직접 소비만 추적한다. 원래 G2/G3 남김을 자동 완료로 만들지 않되, 이미 충분한 근거를 '전체검토 아님' 문구만으로 무한히 재개방하지 않는다.

## 산출과 범위

writes=[]인 review·시험슬롯0이다. 제품 import/시험·실모델/환경probe·설치/예약·Git 쓰기·공용 문서/queue/state·graphify를 실행/변경하지 않는다. 정적 읽기와 자기 task/evidence 작성만 사용한다. 새 실제 결함은 정확한 trigger/현재 정의·영향·최소 수정범위와 기존근거가 부족한 이유를 보고한다. manager가 필요한 구현과 최소확인을 한 task에 배정한다.

evidence/judgment.md와 필요한 유한 evidence/decisions.json에 실제 읽은 hunk/commit·현재 파일/심볼·재사용 근거·처분·원보고 한계를 남긴다. 유지/이미 교정/정당 제거/구체 수리 필요/정확 자료 부재를 구별한다. 단순 locator를 다시 만드는 것으로 끝내지 않고 지정 의미 판단을 마친다. 과거 원보고가 없으면 당시 실행 인증은 보류하되 현재 정적 판단까지 불필요하게 미완료로 두지 않는다.

report.json의 changes=[]를 유지하고 `python C:/math/services/async-development/check.py report C:/math/.async/dm pr-base-tests`를 통과시킨다. complete는 지정 두 기반 질문의 검토 완료이며 G2/G3/G8 전체 인증이 아니다. 최종 관문·이관의 실제 남김·L01/환경/공급자 원자료는 별도다. 이 review를 T4/G4/G5의 선행으로 만들지 않는다.
