# 기반 1b·1c의 실제 경계·층 분리 판단

manager0091 복구 배정이다. 원 pr-base-ports는 기존 base/workspace 때문에 기동이 거절됐고 task.json·baseline.json·session.log·report/evidence가 없다. 원 기록과 사본은 보존하며 완료한 검토로 소비하지 않는다. managers/0091/review.md·recovery-review.json과 sources/archive-resume-2026-10-16.md를 먼저 읽고, 이번 새 workspace의 고정판에서 아래 두 질문을 수행한다. scope.json은 원0089의 두 stage와 제외 범위를 그대로 복사했다. 새 전수 감사·시험 의무는 추가하지 않는다.

새 task는 base 디렉터리가 없으며 시작판은 자기 baseline.json과 records/objects다. 과거 코드가 실제로 필요할 때만 `python C:/math/services/async-development/workspaces.py restore C:/math/.async/dm TASK baseline|result NEW_DIRECTORY PATH ...`로 필요한 파일을 별도 새 디렉터리에 복원한다. 과거 report/evidence/integration은 기존 task 디렉터리에서 읽고, 정리된 workspace/base를 영구 입력으로 요구하거나 원 pr-base-ports의 불완전 사본을 이어 사용하지 않는다. 병행 pr-base-tests·g7-t4r의 미완성 결과는 소비하지 않는다.

g23-handoff는 기존 근거를 연결했지만 비B 기반 변경의 의미 보존을 자동 인증하지 않았다. 이번 review는 그중 1b 포트 도입/이행 기본값 제거와 1c 판정·효과 이동/절단의 남은 실제 hunk를 판단한다. scope.json의 두 stage가 범위다. 새 전수 감사나 매핑 작업을 만들지 않고, 이미 판단된 성질은 재사용해 이 유한 질문의 실제 처분을 끝낸다.

SESSION_JSON/task.json/inputs 세 문서, workspace의 do-math AGENTS.md·시험-지침.md, manager0089/review.md를 읽는다. g23-handoff/evidence/prior-review-state.json의 non_b_material은 길찾기 자료이며 원문은 docs/do-math/시험-재편-2026-09-29/설계.md·진행.md·단계-전환표-2026-10-03.json과 실제 Git diff다. C:/math는 읽기 전용 원자료이며 과거 Git은 `git -C C:/math show/log`로 읽는다. 현재 코드 판단은 자기 workspace의 고정판을 사용한다.

## 끝낼 질문

1. 1b의 실제 도입·기본값 제거 diff에서 어떤 외부 효과가 어느 포트로 넘어갔는지, 현행 생산자/소비자가 같은 필수 포트를 전달하고 실제 adapter와 fake가 같은 입출력·오류·소유 계약을 소비하는지 판단한다. pr-ports의 B38 실제 Git, r07 반환소유·r18 외부경계와 수용된 다른 경계 성질은 명시 범위에서 재사용한다. 이름/프로토콜 선언만으로 효과 의미가 보존됐다고 하지 않는다.
2. 1c의 진행.md 첫~다섯 이동 단위를 실제 변경 diff에서 확인한다. 분리 전 판정과 현재 공유 정본/caller, 순수층과 효과층의 책임, 예외/권한·현재성·owner 인계가 유지됐는지 남은 hunk만 읽는다. B07 wait_rules의 현재 layer1/engine 단일등록과 기존 구조 수리는 완료 근거로 재사용하고 다시 열지 않는다. 구판 fallback/중복 규칙의 제거가 현행 입력 검사까지 지웠는지 실제 연결에서 판단한다.
3. 수용된 후속 수리가 기존 결함을 이미 고쳤다면 그 현재 정의와 수용 근거로 처분한다. 과거 실패 동작의 보존을 요구하지 않는다. 최근 core recover의 저장 경계·등록 action·공통 operational target 검사 변경은 managers/0089/handoff-delta.json과 accepted-diff.txt를 소비한다. 병행 T4 작업의 workspace/미완성 결과는 읽지 않는다.

기존72구간의 모든 밖을 새 quota로 열거나 모든 제품 파일/1932 disposition을 다시 검토하지 않는다. scope의 실제 diff에서 이 두 질문에 필요한 생산·소비 연결만 따른다. 충분한 수용된 검토가 해당 hunk/성질을 이미 설명하면 그 정확한 범위를 인용해 마친다. 원보고 부재는 과거 실행 재인증의 한계로 남기되 현재 hunk의 정적 판단을 가능한 만큼 끝낸다. 자료 부재만으로 동일 시험을 반복할 의무를 만들지 않는다.

## 산출과 범위

writes=[]인 review이며 제품·미러·공용 문서/queue/state를 바꾸지 않는다. 시험슬롯0, 제품 import/시험/실호출/설치/예약/Git mutation/graphify 갱신을 하지 않는다. 정적 읽기와 자기 task/evidence 기록만 사용한다. 발견한 실제 결함은 정확한 trigger·현재 정의/영향·최소 수정파일과 기존근거가 부족한 이유를 적어 manager가 구현·최소확인을 한 work로 묶게 한다.

evidence/judgment.md에는 단계별 실제 본 hunk/commit·현재 파일/심볼·재사용한 보호성질과 미검토 부분의 처분·원보고 한계를 적는다. 필요한 유한 목록은 evidence/decisions.json에 기록하되 새로운 전수 원장으로 확장하지 않는다. 유지/이미 교정/정당 제거/구체 수리 필요/정확 자료 부재를 구별한다. 모든 것을 최종판 대기나 다음 조사에 넘기지 않고 맡은 의미 판단을 끝낸다.

report.json은 changes=[]로 작성하고 `python C:/math/services/async-development/check.py report C:/math/.async/dm pr-base-ports-r`를 통과시킨다. complete는 두 기반 질문의 판단 완료이며 G2/G3/G8 전체 인증이 아니다. 최종 관문 결과 연결·다른 이관 강도/한정검토 밖·환경/L01/실원자료의 기존 남김은 별도다. 이 review는 T4나 G4/G5의 선행이 아니다.
