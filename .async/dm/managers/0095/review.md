# manager 0095 — G4 수용과 한정 T3 후속

g45-final의 22파일을 workspaces.py integrate로 충돌 없이 반영하고 partial로 수용한다. 일반 검사 G4는 충족했다. 같은 판본의 전체 T3는 온전한 측정이지만 5모듈39arc/43행이 남아 G5는 미충족이다. 프로젝트는 active이며 G1~G3 최종 연결·G6·남은 G7/G8와 외부 조건을 완료 처리하지 않는다.

## 변경과 직접 확인

정본 시험6·시험지침1·참조문서4와 공식 미러11, 총22파일이다. runtime 변경은 없다. accepted-diff.txt는 시작판과 일치하는 통합 전 공용파일을 결과와 비교한 줄끝 정규화 diff다. Lake 시험은 compiler와 같은 설치의 형제 lake.exe를 소비한다. 연구 재시도 fixture는 실제 research_work role을 사용하고, 제거된 AST 모양 관측은 현재 action/ready/hold와 정확 ValueError의 행동 단언으로 교체했다. CAS의 정확 conflict 유형·문구, 유실 경로, shallow root 입력을 고쳤다. 문서는 함수/시험 참조와 실제 중첩 필드를 명시했다. 현재 task_contracts.validate_plan_dispositions의 직접 tasks 인덱싱, revisions.continue_repetition의 action_scope/hold/ready, formal.toolchain_root의 부모 깊이를 읽어 변경 이유와 대조했다. 실제 권한/현재성/수용 의미를 약화한 변경은 발견하지 않았다.

inspect_result.py·verification-review.json에 원6보고의 SHA, selected=고유 실제행, counts/fixture·complete/successful·실행중변경, 원명령과 exit를 기록했다. 최종 일반과 전체T3의 선택이 같고 919Python SHA가 서로 및 제출판과 같다. G6의 source/product manifest·보존 index·원report/coverage.data/coverage.json/entered/opened·store2파일의 주요10개 SHA를 대조했다. 원T3 gate의123판단모듈·미측정0·5미도달모듈39arc/43행·기존제외56,531새측정/재사용0·measurement_missing=[]·closing_eligible=true와 branch_gate.passed=false를 구별했다. manager 제품시험은0회다. worker 세부 request/raw·provenance companion345파일·Git/cache복원·공식미러1382파일 check는 작업자 근거를 명시된 범위로 재사용하며 새 전수 감사를 하지 않았다. 실제 report 검사와 integration이 변경 범위22파일을 확인했다.

| 원 실행 | 선택 | 실제 결과 | exit | 판단 |
|---|---:|---|---:|---|
| 정확 T4 입력 | 3 | 3passed | 0 | Lake/두 provenance 입력 질문 해결 |
| general-a | 4523 | 4511passed·3error·8failed·1skip | 1 | 수리 전 원실패 보존 |
| general-fix1 | 13 | 12passed·1failed | 1 | Windows 경로 regexp 추가 교정 전 |
| general-pin2 | 1 | 1passed | 0 | 한정 교정 확인 |
| general-b | 4523 | 4522passed·1skip | 0 | G4 충족 |
| t3-full-a | 4523 | 4522passed·1skip | 1 | 기능 성공, 분기관문 미충족 |

유일한 skip은 unit.test_context_catalog.ContextStoreTests.test_outside_symlink_is_reported_when_supported의 WinError1314다. 실제 file symlink 반려 실행 인증은 아니다. 소수 성공을 합해 전체 성공으로 만들지 않았으며 원 전체T4의301passed·1error·2skip/exit1은 그대로다. 이번 정확3선택은 미해결 입력 질문을 닫는 별도 증거이고 전체T4/G7 재실행 성공이 아니다. G4 wall5090.781초·T3 공식14910.2초의 소프트 기준 초과도 유지한다.

## 후속 배정과 재사용 판단

최신 사용자 sources/t3-targeted-direction-2026-10-16.md를 적용한다. g5-target은 다섯 모듈의 실제 잔여 질문·필요한 구현/관련시험/설명/미러를 한 작업으로 묶는다. core15함수31arc/32행, integration1arc/1행, lifecycle1arc와 환경6arc/10행을 현재 caller·생산·검사로 판단한다. 같은 core/helper/설명을 공유하므로 작은 task들로 반복 분할하지 않는다. 환경 입력 부재를 재probe하거나 불가능한 상태를 합성하지 않고 독립 수리를 마친다. 원39arc를 새시험39개 quota로 바꾸지 않는다.

다음 T3는 정확 관련 시험 ID/모듈을 선택한 jobs1 추가 측정만 배정했다. 전체T3·전체 --full·전체 일반 자동반복은 배정하지 않았다. 기존 원전체 coverage/store/index·판본은 보존하고 변경 없는 범위의 유효성을 대조하여 재사용한다. 현재 run_tests._t3_plan은 선택한 시험 모듈만 universe로 쓰고 _finish_t3는 그 plan.reuse만 합친다. 부분 선택은 closing_eligible=false이고 전체 index를 갱신하지 않는다. 이 기술 제약은 알려진 한계로 인계하며 전체실행 강제·원자료 수동 합산·closing_eligible 변경으로 우회하지 않는다. 기존 context의 G5 일반 설명과 plan 종료절도 최신 사용자 지시를 반영하도록 갱신했다.

g6-scope는 독립 읽기 전용 작업으로 현재 LAYERS/mutation 규칙과 보존 index를 연결해 함수 모집단·실행 묶음·정상 기준/선택 계획을 준비한다. 시험슬롯0·writes=[]이고 g5-target을 선행 장벽으로 삼지 않는다. 현재판의 준비 산출은 수리5모듈/영향시험의 후속diff만 반영하면 되도록 판본을 명시한다. 전체 변이는 아직 실행하지 않는다. index가 가리키는 실제 baseline HEAD를 workspace 정리 후에도 쓸 수 있게 g45-index-baseline.bundle을 만들고 Git bundle verify로 확인했다. 실제 HEAD 4dae8591…이며 공용 Git은 읽거나 수정하지 않았다. 최종 소스 snapshot과 이 baseline은 구별한다.

G1/g23의 원인계와0094까지의 근거는 보존하며 이번 수용은 handoff-delta.json으로 보충한다. 현재 별도 G1~G3 재감사나 이미 끝난 기반review 반복을 만들 필요는 없다. 남은 G7의 공급자 quota/복수result/동적 역할schema, L01 Q1/Q2/원 UTF-8 byte와 실제 환경 조건은 이전 정확한 남김을 유지한다. 저장범위/A22에 따라 공통codec·게시·기존업무 보장을 재사용하며 가족별quota·원자료 부재만을 이유로 한 반복실호출·장기감사를 배정하지 않는다.

## 비의도 설치의 운영상 남김

첫 일반 실행의 shallow fixture가 실제 C:/.skill-workspace/do-math-toolchains로 들어가 약4GB의 Lean 다운로드/압축해제 및 Mathlib 설정2파일을 만들었다. stderr StringIO.fileno 오류로 Lake child는 시작되지 않았으며 Mathlib 준비 성공도 없다. 이것은 제한된 입력 준비의 성공이 아니라 시험 오류의 부작용이다. task evidence/unintended-install.json·unintended-install-files.json의 원경로·시각·신원을 보존한다. 실제 사용한 C:/math/.skill-workspace 설치와 다른 경로다.

작업자 기록상 자동 승인 검토가 그 생성물의 재귀 Remove-Item을 `blocked by policy`로 거부했고 추가 세부 이유는 없다. 삭제는 실행되지 않았다. 이번 manager는 우회 삭제를 시도하지 않았으며 독립 개발을 막지 않는 운영 정리 남김으로 인계한다. 수용 workspace의 공식 archive/cleanup과 이 외부 생성물은 별개다.

## 게시

inbox.completed는 g45-final 한 건, inbox.running은0이다. 기존115개 task 정의는 유지한다. 수용111·취소4, 신규 g5-target/g6-scope를 더해117정의·미해결2로 active를 게시한다. 모델은 기존 gpt-6.1-sol/high이고 max_workers10을 바꾸지 않는다. 공용 문서·두 objective와 입력을 먼저 완성한 뒤 queue.pending.json을 check.py queue로 검사하고 그 파일을 queue.json으로 원자 교체한다. 게시 후 공용 수정은 끝낸다. 수용·종료 사본 정리는 실행기 소유다.
