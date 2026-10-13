# 전체 완료로 이어지는 현재 계획

이 파일은 현재 남김과 다음 판단을 관리한다. 상세한 과거 이력은 sources와 기존 repo 자료에 연결하고 여기에 반복 복사하지 않는다. 상태·근거·구체적 다음 질문 없이 '추가 감사 필요'만 적지 않는다.

## phase 001~004의 결과와 현재 상태

phase 001 세 분석 task의 A1~A4와 phase 002 mutation-baseline의 A1~A5를 manager가 검수했다. 정상 child의 증거 부재가 변이 포착으로 바뀌던 경로를 수리했고 관련 58개 시험 및 실제 child 19개 fixture의 원자료를 대조했다. phase 003은 공급자 smoke를 구현했으나 Codex schema 거부와 미러 원바이트 변형 때문에 partial이었다. Claude 최종 실호출과 정본 오프라인 23개 성공은 그 범위에서 승인했다. phase 004는 미러 치환과 양쪽 재생을 수리했으나 Git manifest 속성의 쓰기 범위가 부족해 A3를 완료하지 못했다. 남은 위치와 다음 수리는 아래에 지정한다. 최종 전체 관문은 아직 실행하지 않았다. 현재 상태의 근거는 context C9~C12와 다음 자료다.

- 요구별 종료 질문: run:phases/001/tasks/closure-map/evidence/requirement-state.json. 원래 19/11/61/12 항목을 보존한다. 1-D/11-A/11-B 및 이미 검토한 부분은 최종 판본 연결로 넘기고 새 결함 없이 재구현하지 않는다.
- 기존 109작업·25영역 재검토: 같은 evidence의 tracking-state.json과 prior-review-state.json. PR23과 PR06/B22의 완료 범위를 재사용하고 필요한 slice를 실제 수리/의미 확인과 결합한다. 없는 임시 원보고의 counts는 역사 주장으로 남긴다.
- 문서의 고정 잔여: run:phases/001/tasks/document-closeout/evidence/followup-packets.json 및 binding-inventory.json. 후보15묶음을 고정 phase15개로 만들지 않는다.
- 관문 준비와 미충족 조건: run:phases/001/tasks/gate-readiness/evidence/gate-readiness.json. 제안 명령의 출력 경로·최종 HEAD·검증된 모델 값은 실행 task가 실제 값으로 결속한다.
- 정상 기준 수리·직접 소비 검증: run:phases/002/tasks/mutation-baseline/report.json 및 run:phases/002/manager-evidence/verification.json. CLI/T3 공통 passed의 비통과, D9·failfast·정상 실패 제외·시도별 근거를 확인했다. 최종 G6는 이 판본의 baselines/attempt 구조를 사용한다. PR01 중 이 slice만 검토를 종결했다.

- 공급자 실호출의 부분 결과: run:phases/003/tasks/provider-smoke/report.json 및 run:phases/003/manager-evidence/verification.json. task 종료 2254파일과 원보고/실호출 원자료를 대조했다. F1 Codex 거부는 미해결이고 F2의 후속 현재 상태는 다음 항목에 있다. F3 background의 한정 재사용과 PR15/B86/B87 지정 slice만 승인했다.
- 미러 수리와 Git 남김: run:phases/004/tasks/mirror-corpus/report.json 및 run:phases/004/manager-evidence/verification.json. 종료 2624파일과 변경 9개, 양쪽 14선택/14passed, 원자료 44파일·각 41개 SHA 참조를 대조했다. 생성 치환은 해결됐고 하위 corpus/.gitattributes의 manifest text 예외는 미해결이다. 이전 Lean/scheduler clean 관찰은 경로 표기에 따른 차이이며 현재 슬래시 경로에서 보존된다.

분류는 완료율이 아니다. 검토된 성질은 최종 증거 대기, 확정된 공백은 수리, 아직 모르는 성질은 한 종료 질문, 실행 관문은 최종 고정판 검증으로 구별한다. 오래된 109개 task를 그대로 재파견하지 않는다.

## 다음 phase: 005

work task `corpus-git-bytes` 하나를 배정한다. phase 004 F1의 실제 위치인 정본 `scripts/tests/corpus/.gitattributes`와 그 생성 사본 두 파일의 쓰기를 허용한다. manifest의 텍스트 변환 예외를 원바이트 보존 속성으로 고치고 공식 생성 뒤 양쪽 전 파일의 raw/clean object ID와 원 SHA를 대조한다. 정본 녹화·manifest 바이트는 그대로 둔다. 속성만 바뀌면 이미 검수된 생성기 22개와 양쪽 재생 14개 결과를 판본 확인으로 재사용한다.

이 작업을 먼저 하는 이유는 확인된 원바이트 인도 실패가 두 manifest에 남아 있고 모델 재호출 없이 작은 속성 수정으로 닫을 수 있기 때문이다. 004의 A3는 요구를 줄이지 않고 실제 수정 위치를 배정해 해소한다. Codex schema 수리는 별도 다음 단위다. 동일 생성기·말뭉치를 쓰는 두 수리를 병렬화하지 않는다. 상세 쓰기 범위와 A1~A3는 run:phases/005/tasks/corpus-git-bytes/objective.md다. manager는 제품을 직접 수정하지 않는다.

## 가까운 후속 배정과 선행 관계

005 결과를 검수한 뒤 우선 Codex schema 전달·수신 경계의 확인된 실패를 한정 work로 배정한다. 그 밖의 구체적 남김은 아래와 같다. 먼저 해야 할 수리가 늘어나면 원래 G와 반례를 붙여 반환하고, 확인된 부분은 다시 탐색하지 않는다.

| 남김 | 다음 담당 작업과 끝나는 조건 | 선행/한계 |
|---|---|---|
| G7/G8 녹화 원바이트와 미러 | phase 004의 미러 치환 수리·양쪽 14개 재생 성공은 검수했다. phase 005는 하위 corpus 속성을 고쳐 두 manifest의 Git clean 변환만 해소한다. | 실제 argv/cwd와 슬래시 경로를 기록하고 전건 raw/clean·원 SHA·--check를 확인한다. Lean/scheduler 녹화와 공급자 호출은 바꾸지 않는다. |
| G7 Codex schema 수락·말뭉치 | phase 003 F1: 보통 maintenance의 선택 integration_bundles가 required에 없다는 실제 HTTP 400이다. 후속 task가 역할 schema와 공급자 전달/수신 경계의 현재 호출자를 확인하고 선택 필드 의미를 보존하는 수리·관련 검사·Codex 새 실호출과 녹화를 수행한다. | 005 뒤 단일 work로 배정한다. 부재/null/값과 다른 schema 제약을 확인하며 단순 필드 삭제·필수화를 하지 않는다. 기존 Codex 실패는 보존하고 Claude 성공/background는 경로 불변이면 재사용한다. |
| G7 Job/Lean/예약/학술 및 L01 | 공급자 최소 경계와 구별해 실제 Job/pythonw, Lean/Mathlib, 시험 전용 예약 등록·발화·해제, 학술 list_sources를 기존 실제 경로로 검증한다. L01은 현재 Codex/Claude 운전 read-call의 host·판본·절단 규칙·한도 단위를 특정한다. | 개별 실제 연쇄로 한 문맥에서 끝나는 task를 만든다. 역할 stdin을 운전 출력 한도로 대체하지 않는다. byte/token 권위 근거가 없으면 결정 질문을 남긴다. |
| G1/G3 문서 P01 | operational_evidence와 recovery_materials의 동명 result/checkpoint를 실제 생산자별로 결속하고 정상·restoration_error·null/부재 조건의 문서 지시와 반례를 확인한다. | B133 일반 재개 경계는 유지. doc_code/역할 입력 공유 파일을 단일 task가 수정한다. |
| G1/G8 문서 N03 확정 불일치 | 독립-운영.md의 LIVE_INSTALLATION_ROOT 설명을 실제 installation_root 전달로 교정하고 기존 bootstrap-info 근거와 미러를 연결한다. | 해당 문서 절만 배정 가능하며 옛 전역 변수를 제품에 복원하지 않는다. |
| G1/G3 나머지 문서·정책 | P02~P11·N01~N03의 미결 절만 실제 반환/공유 계약·기존 시험에 연결한다. 명시 소비 없는 instance는 제거 가능성을 판정한다. | 34 AST 구문지점의 제거 수로 진척을 세지 않고 마지막 소비자 뒤 helper를 정리한다. |
| G7 T4 adapter 보고 | T4 단독 전체 boundary 선택에 별도 adapter 분기 측정을 연결해 실제 보고를 만든다. | 설계5.5상 보고이며 통과 임계 관문으로 바꾸지 않는다. 최종 T3 선택과 분리한다. |
| G1/G2 남은 의미 질문·과거 재검토 | requirement-state의 해당 생산자/소비자/입력/단언 질문과 관련 PR slice만 배정한다. 이미 충분하면 유지하고 빠진 축만 수리한다. | R05/R06은 현 test_provider_native_storage 경로 사용. 없는 원보고는 해당 slice에서만 회수/대체 증거 필요를 판정한다. |

원래 1-A는 A20의 필수+선택 역방향을 적용하고 역사 SHARDS/저장대역/timeout 표현은 현재 의미로 판정한다. 의미를 모르는 항목을 일괄 final-evidence로 올리지 않는다. G7이 외부 조건에 막혀도 독립 수리는 진행하며, 모든 행동이 막히면 context C7의 정확한 상신 절차를 따른다.

## 구현과 기존 작업 재검토

확인된 공백과 관련 과거 변경을 같은 한정 단위에서 처리한다. 25개 재검토 영역 전체의 완료를 모든 구현의 선행 장벽으로 만들지 않는다. 기존 실제 코드·시험을 재사용하고 source/diff/원보고가 입증한 성질은 계약 변경이나 새 반례가 있을 때만 다시 연다.

전체 범위는 다음 네 묶음으로 보존한다. phase 001의 구체적 종료 질문과 이후 결과로 가까운 순서를 정하며 무관한 발견으로 방향을 바꾸지 않는다.

1. 대기·계수·관측·정산: 모든 지정 상태 공간의 생성, 유지, 해소, 담당자, 후속 호출과 실제 표시.
2. 입력·평가·근거: 역할 변형, 실제 생산/수신, 판정 함수와 교란 축, 원래 평가자 쌍·보존/P2 기대값.
3. 소유자·시간·발동: 실패 격벽, 타 단위 진행, 시간 규칙의 국면, 대상·사건별 실제 발동/비발동.
4. 기동·문서·경계·규모: 설치/기동 판본, 문서 실제 계약, 필수 자료·읽기/출력 한도, 입력 규모와 읽기·해시·복사 비용, 실제 경계/말뭉치.

문서 검사기는 source-owner 전부를 임의로 지원하는 새 추론기로 키우지 않는다. 현재 원문이 참조하는 계약을 실제 반환/공유 계약에 연결하고, 불필요한 결속이나 중복은 제거 후보로 판정한다. DOC-RETURN-ROLE의 _context, REVIEW, TRUST와 이름·정책·읽기 한계는 서로 구분해 종료한다. AST 제거 개수는 전체 완료율이 아니다.

새 API/공유 계약을 병렬 개발하려면 먼저 seams에 실제 정본·의미·오류·공유 검사와 실제 연결 책임을 정의한다. 그 전에는 같은 phase의 미완성 구현에 기대는 검사를 배정하지 않는다. 반복 검증의 명확한 병목이 있으면 같은 경로·단언의 전후 근거로 그 좁은 병목을 개선할 수 있다. 예산만 맞추려는 우회는 하지 않는다.

## 최종 관문과 완료 review

필요한 실제 경계 호출·녹화와 코드 수리를 먼저 끝내 최종 판본을 고정한다. G4 전체 일반 → G5 fresh T3 → G6 정상 기준/현재 함수 전체 극단 변이의 근거를 확보하고 G7의 실제 경계·녹화 판본을 연결한다. G6 담당 작업이 fresh T3 뒤 현 함수·rule·trivial·선택 시험 manifest를 확정한다. context C11의 adapter5·runner2 제외 처분을 명시하고 layer1/2/3 변이 분모와 별도 검증을 혼합하지 않는다. 공유 pseudo_tested 목록을 쓰는 분할은 순차 실행한다. 오래된 함수 수나 분할 개수를 성공의 분모로 사용하지 않는다.

후속 변경이 생기면 어떤 기존 증거가 무효화됐는지 기록하고 그 범위의 검증을 교체한다. 최종 동일 판본 조건이 필요한 전체 관문은 필요한 시점에 다시 완결한다. 중간 부분 통과를 합산하지 않는다. 유효한 기존 실제 경계 결과의 재사용은 코드·도구 판본과 성질을 대조해 판단한다.

완성됐다고 판단하면 review kind의 phase를 배정한다. 고정된 제품을 대상으로 요구 충족/검출력·기존 개선 보존/실환경·인도 증거를 독립적으로 검토할 수 있다. 모든 G를 충족하는 근거와 미해결 finding의 처분을 manager가 확인해야 next:null을 제출한다. 문제를 발견하면 정확한 work task 뒤 다시 review한다. 검토 인원이나 반복 횟수 자체를 종료조건으로 삼지 않는다.
