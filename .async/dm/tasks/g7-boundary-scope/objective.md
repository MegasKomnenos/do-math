# 최종 실경계 검증에 필요한 기존 증거·실행·외부 입력 확정

사용자 목표는 현재 do-math가 실제 제품 경로에서 동작하고 그 결함을 시험이 놓치지 않게 하는 것이다. G5의 core/entry 수리는 별도 task가 계속 맡는다. 그 종료를 기다리지 않고, G7과 L01에 남은 실경계 질문을 기존 원증거와 자기 시작판에 연결해 다음 manager가 필요한 실제 실행을 바로 배정하거나 정확한 외부 결정을 요청할 수 있게 한다. 새로운 전체 감사나 중간판 전체 시험을 만드는 작업이 아니다. 제품 변경 없는 한정 조사이며, 이 task의 complete는 G7/L01 완료를 뜻하지 않는다.

## 입력·작업 경계

SESSION_JSON, task.json, inputs/context.md·plan.md·seams.md, 자기 workspace의 do-math AGENTS.md와 scripts/tests/시험-지침.md를 읽는다. 실제 선행은 g5-trust-rest·g5-entry-io·r19-r20의 수용 결과다. managers/0079/review.md·assignment-scope.json에서 시작 시점 진행 중인 g5-entry-gate/g5-core-gaps의 소유 범위를 확인한다. 동료 workspace·진행 중 결과를 읽거나 배정을 변경하지 않는다. 읽기 대상 제품은 자기 고정 workspace다.

과거 기록의 루트는 C:/math/docs/do-math/continuous-development-2026-10-13이다. phases/003·006·010~014·018의 지정 manager-evidence/review.md와 아래 필요한 task 보고가 과거 실증의 진입점이다. 우선 해당 검수와 보고를 읽고 이번 판단에 필요한 원자료만 따라간다. 과거 전체 트리 해시·모든 raw·모든 task/요구 ID를 다시 감사하지 않는다. 과거 성공을 최종판 성공으로 복사하지 않으며 원파일이 없으면 그 한계를 남긴다.

현재 수용 기록은 C:/math/.async/dm/tasks/r19-r20/evidence/judgment.md, g5-entry-io/evidence/judgment.md, g5-trust-rest/evidence/judgment.md다. 원설계 C:/math/docs/do-math/시험-재편-2026-09-29/설계.md의 G7에 관련된 T4/T5·실경계·5.5와 sources/user-decisions.md, 사용자 저장범위 교정 C:/math/.async/dm/sources/storage-scope-direction-2026-10-15.md를 적용한다. 과거 서비스 운영 절차는 현재 ENGINE/protocol.md로 대체되었으며 과거 호출 권한이 자동으로 확대되지 않는다.

쓰기 범위는 []다. 자기 task/evidence와 report.json만 작성한다. 제품·정본/미러·공용 문서·queue/state·기존 기록은 읽기 전용이다. 공식 시험·새 모델 호출·새 세션·Lean 실행/설치·예약 변경·WSL/권한 probe·새 도구 호스트 기동은 이 조사에 필요하지 않으므로 하지 않는다. 기존 환경6arc/10행의 WinError1314/WSL 관측을 반복하지 않는다. 제품 결함을 발견하면 실제 caller·반례·최소 수정 파일과 확인할 동작을 보고하여 구현과 필요한 검증을 한 후속 work로 묶게 한다.

## 맡은 유한 질문

1. **공급자 호출·녹화.** phases/003의 provider-smoke, 006의 codex-schema 검수와 r19-r20의 정확한 세 남김을 대조한다. 유지 가능한 원 CLI 호출·schema/응답·원bytes 성질과 현재 지원판에서 새로 확인해야 할 성질을 구분한다. base10/동적 schema 모든 조합을 새 실호출 quota로 만들지 않는다. 원 요구가 요구하는 실제 수용 질문을 구체화하고, 대표 입력으로 충분한 이유 또는 추가 입력이 필요한 이유를 설명한다. 자연발생 quota/복수 result/후속 실패의 raw 부재는 인위적 반복 호출로 채울 목표가 아니다. 합성표본·--version·역사판 원문을 현재판 실호출 성공으로 세지 않는다.
2. **실제 Job/pythonw·Lean/Mathlib·예약·학술 경계.** phases/010~014·018의 지정 실증과 현재 smoke/test_host_live.py·test_lean_live.py·test_scheduler_live.py·test_scholarly_live.py, 필요한 support/제품 caller만 연결한다. 기존 검수된 성질 중 현 caller/입력 변화가 영향을 주는 부분을 판정한다. 파일이 바뀌었다는 사실만으로 원 실증 전부를 폐기하지 않는다. 재사용이 가능한 성질은 그 이유와 해당 심볼을 적고, 새 실실행이 필요한 경우 가장 작은 공식 선택·실제 input 경로/조건·기대 결과·정리 책임을 구체적으로 제시한다. 기존 실제 환경의 존재/판본은 기록된 사실과 현재 읽기로 확인한 사실을 구분한다. 경로 존재만으로 실행 가능성을 인증하지 않는다. 전체 T4의 최종판 연결과 개별 실제 T5 성질도 구별한다.
3. **L01/13-C의 실제 운전 읽기.** phases/010/tasks/reading-limits/report.json·evidence/reading-boundaries.json·review.md, phases/011/manager-evidence/review.md를 사용한다. 해결된 절단 설명을 다시 열지 않는다. Q1 실제 operator host/tool/version/read-call과 Q2 출력 단위의 미결을 정확 원문에 연결한다. 현재 task host를 제품 운전 프로필로 추정하거나 token/character를 UTF-8 byte로 환산하지 않는다. 기존 위임 안에서 선택 가능한 부분과 사용자만 정할 요구 변경을 구분하고, 필요한 경우 답변 가능한 짧은 질문·선택의 영향·권고 근거를 작성한다. 과거 조사로 충분한 내용을 재측정하지 않는다.

## 결과와 완료 판단

evidence/judgment.md에 위 경계별로 원 요구/실증의 범위, 현 시작판의 관련 파일·심볼/필요 SHA, 유지 가능한 보장, 남은 정확한 불확실성, 다음 행동을 적는다. 긴 역사 재서술이나 새 범용 registry/API는 만들지 않는다. 보고서를 읽은 manager가 다음 중 하나를 바로 선택할 수 있어야 한다: 기존 증거 한정 재사용, 구체 최소 실행 배정, 구체 수정+확인 배정, 정확 외부 입력 요청.

실행 제안에는 workspace 기준 공식 command/selection, 외부 입력과 현재 확인 여부, 공유 자원/시험슬롯, 기존 권한의 정확 원문, 성공·실패에서 보존할 결과와 자기 자원 정리를 넣는다. 입력이 없는 명령을 실행 가능하다고 쓰지 않는다. 이미 허용된 일을 다시 승인받도록 만들지 말고, 확인되지 않은 권한을 합의된 조건으로 채우지도 않는다. G4/G5/G6 뒤에만 해야 한다는 포괄 장벽을 만들지 않는다. 필요한 실제 제공자 결과만 선행으로 제시한다.

진행 중 core/entry가 영향을 줄 수 있는 파일은 현재 판단의 유효 조건으로 표시한다. 미래 코드를 추측하거나 기다리지 않고 시작판에서 가능한 판단을 마친다. 최종 통합 뒤 해당 경계의 실제 diff만 확인하면 되게 한다. 환경6arc/10행은 기존 증거·정확 조건을 참조하되 이번에 해결했다고 쓰지 않는다.

검증은 직접 읽기·필요한 정적 비교로 끝낸다. 새 시험·실호출0을 명시하고 정적 근거로 실환경 성공을 주장하지 않는다. 충분한 기존 근거와 새 불확실성을 구분하는 것이 완료 기준이지 새 문서 수나 파일 전수 비교가 아니다. 사용자 저장범위/A22에 따라 전가족/전필드/새 reader/옛 head quota를 추가하지 않는다. G1~G8을 줄이지 않고 최종 검증에 필요한 수단을 최소화한다.

report.json에 변경없음, 판정과 이유, 직접 확인/미확인, 구체 후속을 적고 `python C:/math/services/async-development/check.py report C:/math/.async/dm g7-boundary-scope`로 제출한다. 조사 질문에 답했다면 complete로 보고할 수 있으나, 외부 자료가 없어서 해당 판단 자체를 못한 부분은 partial/blocked와 정확한 이유를 남긴다. 최종 제품 review는 별도다.
