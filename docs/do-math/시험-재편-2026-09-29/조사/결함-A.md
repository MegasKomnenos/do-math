# 결함 기록 A: 기억 노드 M-0263~M-0332 기간 (2026-09-14~09-24)

담당 A가 [결함 기록 서식](결함-기록-서식.md)에 따라 작성했다. 파일 안의 경로는 저장소 루트 `C:\math` 기준 상대 경로이며, 커밋은 `git -C C:\math show <해시>`로 확인했다. 원 로그가 있던 인스턴스 폴더(`.skill-workspace/parking-unimodality-*`)는 모두 삭제되어 있었다. 따라서 실제 운전 결함의 증상은 노드와 추적 문서의 기술을 근거로 적고, 근본 원인과 수정은 커밋 diff로 확인했다. 영향 등급에 `(추론)`이 붙은 것은 원자료가 실제 결과를 말하지 않아 코드 경로와 원자료의 요지로 추론한 값이다.

## 1. 읽은 범위

### 1.1 기억 노드

`기억/색인_아카이브.md`의 M-0263~M-0332 제목 줄(70개)을 읽었다.

- **전문을 읽은 노드 48개**: M-0263, 0265, 0266, 0268, 0269, 0274, 0275, 0276, 0277, 0278, 0279, 0280, 0281, 0282, 0283, 0285, 0287, 0289, 0290, 0292, 0293, 0294, 0295, 0296, 0297, 0298, 0299, 0300, 0301, 0307, 0308, 0309, 0310, 0311, 0312, 0313, 0314, 0315, 0317, 0318, 0320, 0321, 0323, 0325, 0327, 0329, 0331, 0332. 이 가운데 M-0275·0276·0277(연구 문제 준비), M-0281·0285·0290(검증 임시 정리의 정책 차단), M-0331(graphify), M-0332(테스트 비용 원장)는 읽은 뒤 do-math 결함을 담지 않은 것으로 판정했다.
- **제외한 노드 22개**(do-math와 무관): M-0264, 0267, 0270, 0271, 0316(학술자료 MCP), 0272(교재 이동), 0273(작업 트리 정리), 0284, 0288, 0291(수행계획서), 0286, 0302, 0322(작문 스킬·규정), 0303(임시 정리), 0304(verify-rounds), 0305(extract-documents), 0306(gitignore), 0319, 0324, 0330(지침 파일), 0326(D-0007 결정·scholarly 사본), 0328(Jev CLI).

### 1.2 문서와 원자료

| 자료 | 읽은 범위 |
|---|---|
| `docs/do-math/review-2026-09-18/plan.md` | 전문 |
| `docs/do-math/review-2026-09-18/implementation-plan.md` | 전문 |
| `docs/do-math/review-2026-09-18/operator-2002-diagnosis.md` | 전문 |
| `docs/do-math/review-2026-09-18/dialogue-review.md` | 전문 |
| `docs/do-math/review-2026-09-18/sufficiency-review.md` | 전문 |
| `research/problem-selection-2026-09-15/progress-2026-09-18/analysis.md` | 전문 |
| `docs/do-math/efficiency-repair-2026-09-18.md` | 전문 |
| `docs/do-math/efficiency-repair-2026-09-18.json` | 일부(scope, initial_attempts, diagnostic, gates, differences_to_final) |
| `docs/do-math/claude-cli-validation-2026-09-18.json` | 일부(initial_live_failure, json_comparison_repair, limits, superseded_runs, regression 앞부분) |
| `docs/do-math/opus-only-validation-2026-09-18.json` | 전문 |
| `임시/parking-unimodality-analysis-20260916/분석.md` (9/15~16 Codex 운전 분석, M-0295·M-0303이 가리킴) | 전문 |
| `docs/do-math/개선-검증-2026-09-16/README.md` | 전문 |
| `docs/do-math/console-launch-2026-09-17.json` | 일부(before/after 외 키) |
| `docs/do-math/구현-검증-2026-09-14/cli-workflow/report.json` | 일부 |
| `docs/do-math/구현-검증-2026-09-14/feature2/README.md`, `observation/README.md`, `cli-profile/README.md`, `semantic/dispute/README.md` | 전문 |
| `docs/do-math/review-evidence/2026-09-23-static/report.md` | 전문 |
| `docs/do-math/정적-워크스루-연결결함-수리안-2026-09-23.md` | 1~170행(F1~F8 본문 전부) |
| `docs/do-math/정적-워크스루-후속-수리안-2026-09-23.md` | 서두 30행과 각 절의 `현재 문제` 단락 |
| `docs/do-math/정적-워크스루-수리결과-2026-09-23.md` | 앞 30행 |
| `docs/do-math/정적-워크스루-연결결함-수리결과-2026-09-23.json` | 일부(repairs, changed_source_files, verification 앞부분, limitations) |
| `docs/do-math/정적-검토-수리안-2026-09-23.md` | 1~44행과 각 절의 첫 단락 일부 |
| 검증런 장부 `임시/do-math_검증_2026-09-15/장부.md`, `임시/do-math_codex-full_검증_2026-09-15/장부.md`, `임시/do-math_astra-low_검증_2026-09-15/장부.md`, `임시/do-math_결정대조_검증_20260916/장부.md`, `임시/do-math_전면대조_20260917/장부.md` | 항목표 전 행(ID·요지·상태), 첫 장부의 R1-49·R1-65·R1-M3·R1-M4·R1-M6 기각 사유 |
| `.skill-workspace/do-math-claude/rate-before-init-red.log`, `output-types-red.log` | 앞부분 |
| 커밋 diff | 116cff2~7d2597e 사이 do-math 커밋의 파일 목록, 그리고 08eecbf(일부), d0024f5, d03f7d9(시험), b134089(시험), ef0863a(시험과 부모 판본 시험 파일), bc63b58(시험), 98ac7e5(시험), d57c016, f675902, 65ee301, 9d81400, b4ede4c(시험), edfafaf(시험), 120dde6(시험), 94cfb60(시험·contracts.py 부모 판본)의 diff와 부모 판본의 관련 시험 |

### 1.3 읽지 못했거나 읽지 않은 자료

- **원 인스턴스 로그**: `.skill-workspace/parking-unimodality-20260915/`, `-20260917/`, `-opus5-20260918/`, `-opus5-20260919/`는 존재하지 않았다. 분석 문서가 링크한 실행별 `final.txt`, `stdout.jsonl`, 운영 담당 `repair/` 자료를 직접 확인하지 못했다.
- **9/14 초기 구현 커밋(08eecbf, 3d7b280)**: 여러 결함이 같은 커밋 안에서 발견·수정되어 수정 전 판본이 커밋으로 남지 않았다. M-0268·M-0269의 기술과 `구현-검증-2026-09-14`의 보고로만 판정했다.
- **v5(9/20~9/23) 수정 전 판본**: 정적 검토 당시 작업 트리는 미커밋이었고, `review-evidence/2026-09-23-static/source/`에는 제품 소스 17개만 있고 시험 파일이 없다. 따라서 당시 시험의 유출 원인은 판정할 수 없었다.
- **9/15 검증런 장부의 적용 항목 상세**: 장부 표에는 요지만 있고 각 항목의 영향 기술은 라운드 폴더에 있었으나 삭제되어 있었다. 정지급 판정은 요지 문장에 근거했다.
- **읽지 않은 자료**: `review-2026-09-18/evidence.json`, `currentness-reassessment.json`, `dialogue-evidence.json`, `sufficiency-evidence.json`, `implementation-results/verification.json`. 필요한 수치는 plan.md 등 본문에 이미 인용돼 있어 재확인하지 않았다.
- **범위 경계의 미분석 커밋**: `8694693`(2026-09-24 00:34, "Repair do-math task contracts, goal audit recovery, and resource waits")과 `4b156be`(09-24 08:36)는 M-0331과 M-0332 사이에 있으나 어떤 기억 노드도 지목하지 않는다. 내용상 9/23 정적 검토 수리안의 구현으로 보이지만 확인하지 않았다.

## 2. 요약 표

| 번호 | 제목 | 영향 등급 | 결함 유형 | 위치 층 | 시험 유출 원인 | 범주 후보 |
|---|---|---|---|---|---|---|
| A-01 | CLI 샌드박스에서 작업자가 파일을 쓰지 못함 | 정지 | 외부 경계 | 경계 어댑터 | 환경 차이 | 외부 CLI 실동작 가정 |
| A-02 | 낡은 보충 조사 요청이 제어 inbox를 영구히 막음 | 정지 | 검사 | L2 | 시험 없음 | 대기·요청의 소비자 부재 |
| A-03 | 완료된 인스턴스를 pause/resume이 다시 엶 | 저하 | 검사 | L2 | 시험 없음 | 종결 상태 보호 누락 |
| A-04 | 계획 출력이 작업 ID 배열에 설명문을 섞고 미수행 과제를 완료 판정 | 저하 | 스키마·계약 불일치 | 계약·스키마 | 시험 없음 | 모델 출력과 소비자 계약의 불일치 |
| A-05 | 목표 감사 입력에서 완료된 동일성 검토를 숨김 | 저하 | 인터페이스 | L2 | 시험 없음 | 역할 입력 누락 |
| A-06 | 명시적 pause가 후속 처분에 의해 ready로 덮임(재발 포함) | 저하 | 대입·초기화 | L2 | 조합·순서 미탐색 | 사용자 제어의 덮어쓰기 |
| A-07 | 개정 계약의 완료 기준이 옛 기준과 합집합으로 저장됨 | 정지 | 알고리즘 | L2 | 합성 입력이 실제와 다름, 단언 약함 | 계약 저장 규칙 |
| A-08 | 종결 과제의 낡은 readiness 투영이 계획을 막음 | 정지 | 대입·초기화 | L2 | 조합·순서 미탐색 | 파생 상태의 전이 경계 정리 누락 |
| A-09 | resume이 수리 소진 계획을 그대로 되살려 같은 정지를 반복 | 정지 | 기능 | L2 | 조합·순서 미탐색 | 실패 행동의 재개·복구 경로 |
| A-10 | 계획 모집단 오류가 누락·과잉·중복을 구별하지 않음 | 저하 | 인터페이스 | L2 | 단언 약함 | 모델 출력과 소비자 계약의 불일치 |
| A-11 | 연구 실행에 scholarly MCP가 전달되지 않음 | 저하 | 외부 경계 | 경계 어댑터 | 시험 없음, 단언 약함 | 외부 CLI 실동작 가정 |
| A-12 | 새 operator 모듈이 표준 라이브러리 operator를 가려 자식 실패 | 정지 | 빌드·패키지 | L3 | 환경 차이 | 실행 환경의 import·직렬화 |
| A-13 | 예약 운영 영수증의 bytes를 JSON으로 쓰지 못함 | 정지 | 인터페이스 | L3 | 합성 입력이 실제와 다름 | 실행 환경의 import·직렬화 |
| A-14 | 실제 scholarly 설정의 timeout 키 때문에 설정 전체 거부 | 정지(추론) | 검사 | 경계 어댑터 | 합성 입력이 실제와 다름 | 외부 CLI 실동작 가정 |
| A-15 | HOLD 해제와 정지 적용의 경합 | 정지(추론) | 타이밍·직렬화 | L2 | 시험 없음 | 사용자 제어의 덮어쓰기 |
| A-16 | Git 자식 프로세스가 콘솔 창을 반복 표시 | 저하 | 외부 경계 | 경계 어댑터 | 환경 차이, 시험 없음 | 외부 CLI 실동작 가정 |
| A-17 | 최초 계획이 준비 결과 전에 실행돼 준비를 다시 요청 | 저하 | 타이밍·직렬화 | L2 | 시험 없음 | 판단 대상 없는 실행의 발동 |
| A-18 | 무변경 상태의 반복 커밋과 과다한 Git 프로세스 | 저하 | 알고리즘 | L3 | 단언 약함, 시간·규모 미재현 | 판단 대상 없는 실행의 발동 |
| A-19 | 모델 시작 전 정지에도 체크포인트 유예를 적용 | 저하 | 타이밍·직렬화 | L3 | 조합·순서 미탐색 | 기한·시간 경계 |
| A-20 | rate_limit_event가 init보다 먼저 와 정상 결과를 거부 | 정지 | 외부 경계 | 경계 어댑터 | 합성 입력이 실제와 다름 | 외부 CLI 실동작 가정 |
| A-21 | Claude CLI가 역할 스키마의 `$schema`·`x-contract-id`를 거부 | 정지 | 외부 경계 | 경계 어댑터 | 합성 입력이 실제와 다름 | 외부 CLI 실동작 가정 |
| A-22 | 주 모델을 지정해도 Haiku 보조 호출이 발생 | 저하 | 외부 경계 | 경계 어댑터 | 시험 없음, 대역이 가림 | 외부 CLI 실동작 가정 |
| A-23 | 같은 Claude 세션의 여러 결과 구간을 수집기가 거부 | 저하 | 외부 경계 | 경계 어댑터 | 합성 입력이 실제와 다름, 단언 약함 | 외부 CLI 실동작 가정 |
| A-24 | 공급자 세션 한도를 일반 실패로 처리해 진단 연쇄 실패·자동 재개 없음 | 저하 | 기능 | L3 | 시험 없음 | 대기·요청의 소비자 부재 |
| A-25 | 인용 과제·지식의 무관한 상태 변화로 반환을 거부 | 저하 | 검사 | L2 | 조합·순서 미탐색, 시간·규모 미재현 | 현재성 검사 범위 |
| A-26 | 실행기 기한 도래·직전 착수로 진행 중 실행이 끊김 | 저하 | 타이밍·직렬화 | L3 | 시간·규모 미재현 | 기한·시간 경계 |
| A-27 | 관찰 규칙이 정상 작업을 반복 운영 점검 | 저하 | 알고리즘 | L2 | 단언 약함 | 판단 대상 없는 실행의 발동 |
| A-28 | 생산자가 허용되지 않는 `used_sources`를 제출 | 저하 | 인터페이스 | L2 | 시험 없음 | 모델 출력과 소비자 계약의 불일치 |
| A-29 | Lean 선언명의 끝 작은따옴표를 거부 | 저하 | 검사 | L1 | 합성 입력이 실제와 다름 | 외부 도구 문법 가정 |
| A-30 | 독립 운영의 코드 수리가 검증·커밋 경계 없이 남음 | 저하 | 문서·계약 | 계약·스키마 | 시험 없음 | 운영 수리의 판본 관리 |
| A-31 | 준비 직후 무조건 계획을 열어 빈 계획이 반복 | 저하 | 알고리즘 | L2 | 단언 약함 | 판단 대상 없는 실행의 발동 |
| A-32 | 예약 조회가 null 다음 실행 시각에 메서드를 호출 | 저하(추론) | 외부 경계 | 경계 어댑터 | 대역이 가림 | 외부 CLI 실동작 가정 |
| A-33 | 미시작 개정 요청들이 서로를 기다리는 순환 | 저하 | 알고리즘 | L2 | 조합·순서 미탐색 | 대기 그래프 교착 |
| A-34 | 병합된 새 준비 요청이 개정 대상 은퇴와 함께 소실 | 저하 | 기능 | L2 | 조합·순서 미탐색 | 파생 상태의 전이 경계 정리 누락 |
| A-35 | 유지보수 역할이 확인할 개정 대기열 상태를 받지 못함 | 저하 | 인터페이스 | L2 | 시험 없음 | 역할 입력 누락 |
| A-36 | 같은 계약의 검토를 실행 중에 중복 개설 | 저하 | 검사 | L2 | 조합·순서 미탐색 | 현재성 검사 범위 |
| A-37 | 작업 예산 AI 실행에 운영 호출 기한(600초)을 적용 | 정지(추론) | 대입·초기화 | L3 | 시험 없음 | 기한·시간 경계 |
| A-38 | 목표 변경이 무관한 기계·검토 action을 대기열에서 삭제 | 정지(추론) | 기능 | L2 | 출발 상태가 경로를 건너뜀 | 파생 상태의 전이 경계 정리 누락 |
| A-39 | 지식 개정이 진행 중 동일성 검토를 닫지 않아 매 run 같은 예외 | 정지(추론) | 기능 | L2 | 확인 불가 | 예외 전파 |
| A-40 | 연구 수행 실패 뒤 운영 점검 revise로 과제가 performing에 고착 | 정지(추론) | 기능 | L2 | 시험 없음 | 대기·요청의 소비자 부재 |
| A-41 | 계약 검토 반려가 후보 준비로 반환되지 않음 | 정지(추론) | 기능 | L2 | 시험 없음 | 대기·요청의 소비자 부재 |
| A-42 | 작업 예산 소진 요청이 운영 예산 사용까지 막음 | 정지(추론) | 알고리즘 | L3 | 단언 약함 | 대기 그래프 교착 |
| A-43 | 설정·계약 개정 뒤에도 대기 행동이 옛 모델 배정을 유지 | 정지(추론) | 대입·초기화 | L2 | 시험 없음 | 파생 상태의 전이 경계 정리 누락 |
| A-44 | 학술 과제의 평가 반려 뒤 수리 경로 부재 | 정지(추론) | 기능 | L2 | 시험 없음 | 대기·요청의 소비자 부재 |
| A-45 | (v5) Lean 검사 중 pause 뒤 resume으로 검사가 재개되지 않음 | 정지(추론) | 기능 | L2 | 확인 불가 | 대기·요청의 소비자 부재 |
| A-46 | (v5) 동일성 검토 실행 한도 소진이 처리되지 않는 대기로 남음 | 정지(추론) | 기능 | L2 | 확인 불가 | 대기·요청의 소비자 부재 |
| A-47 | (v5) 검토 제안의 입력 초과를 사용자 대기로 보냄 | 정지(추론) | 기능 | L2 | 확인 불가 | 대기·요청의 소비자 부재 |
| A-48 | (v5) 검토 입력 복원 유예 중 예외가 스케줄러 전체로 번짐 | 정지(추론) | 타이밍·직렬화 | L3 | 확인 불가 | 예외 전파 |
| A-49 | (v5) 반복 문턱 뒤 재개 경로가 끊김 | 정지(추론) | 인터페이스 | L2 | 확인 불가 | 대기·요청의 소비자 부재 |

영향 등급별 건수: **정지 24건**(관측 9건: A-01·02·07·08·09·12·13·20·21, 추론 15건: A-14·15·37~49), **저하 25건**(이 중 A-32는 추론), **잠재 0건**.

### 2.1 개별 기록을 쓰지 않은 결함의 출처별 건수

서식 1절의 대상에 들지 않아(실제 운전에서 드러나지 않았고 정지급도 아님) 개별 기록을 쓰지 않은 결함이다. 검증런은 수리가 적용되거나 무처분으로 결함이 인정된 항목만 세고, 기각 항목은 결함 실재가 확정되지 않았으므로 별도 행에 적는다.

| 출처 | 개별 기록 없는 결함 수 | 비고 |
|---|---:|---|
| 9/15 검증런 1차(M-0279·0280, `임시/do-math_검증_2026-09-15/장부.md`) | 35 | 적용 41행 중 A-06·A-37~41로 기록한 6행 제외. 문서·계약 표현, 시험 약점(R1-28~31), 지식 전파·관계·학술 등 |
| 9/15 codex-full 검증런(M-0282·0283) | 20 | 적용 20행 중 A-42(R1-12) 제외 19행, 무처분 R1-04 1건 |
| 9/15 astra-low 검증런(M-0289) | 9 | 적용 8행, 무처분 R1-06 1건 |
| 9/16 결정대조 검증런(M-0299) | 8 | 적용 7행, 상신 R1-04 1건(사용자 결정으로 평가 보충 구현). 같은 시각 제어 순서 결함(재현 발견) 포함 시 9 |
| 9/17 전면대조 검증런(M-0300) | 8 | 적용 11행 중 A-43(R1-07·08·12) 제외 |
| 9/16 형식·절차 감사와 직접 수리(M-0298) | 약 6 | 제출 검사 도구 부재, 현재성 결박, 보류 뒤 요청 재생성, 허가 철회 뒤 늦은 응답 수락, 누적 입력, 지식 의존 제외 목록의 중복 할당. 노드가 항목 수를 세지 않아 근사 |
| 9/15 문서·입력 전달 대조(M-0274) | 약 5 | 공통 참조 문서 미전달(`contracts.py`), 준비·계획의 설정 누락, 관찰 규칙 덮어쓰기, 원자료 변경의 완료 과제 재개, 운영 점검 자료 누락 |
| 9/15 단독 설치 검증(M-0287) | 3 | 외부 명세 의존 검사, 얕은 경로의 Lean 탐색·부모 경로 인덱스 예외 |
| 9/14 CLI 기반 구현 검토(M-0263·0265) | 3 | `codex_argv` 자유 꼬리, `turn.completed`만의 완료 판정, 샌드박스 프로필 간 ACL 공유(외부 도구 한계) |
| 9/14 기능 판본 2 구현 중 소비자 대조(M-0269) | 약 5 | 의무 이전의 완료 판정 미반영, 검토 입력 누설, 신뢰 재검사의 자동 승계, 관계 결박, 철회 답변 반복. 발견 경위(실운전/정적)를 원자료로 가리지 못함 |
| 9/16 구현 중 시험(M-0295) | 1 | 같은 밀리초 ULID의 제어 순서 역전 |
| 9/18 Claude 연동(M-0308) | 1 | JSON `True == 1`·중복 키로 인한 잘못된 일치 |
| 9/18 실행 분석의 코드 확인·대역 실험(M-0311·0313, plan.md P05·충분성 검토) | 4 | 역할 접두어로 실패 안내 일괄 삭제, 질문 존재만으로 대기, 다중 결과 사용량 오집계, 개정 뒤 기존 승인 재사용(대역 실험). 모두 운전 미발현 |
| 9/19 구현 중 발견(M-0315) | 3 | 위임 과제의 자기 차단, 수행 중 지식 개정의 waiting 전파, 근거 키 추가 때 대기열 재삽입으로 순서 변경 |
| 9/23 정적 검토 세 건(M-0329) | 약 18 | 정적 검토 수리안 1~8, 연결결함 F4~F8, 후속 수리안 4~8 |
| 9/19 실행 분석의 계약 개선(M-0321·0325·0327) | 2 | 첫 계약 검토 반려율 7/12, 형식화 제안이 재량이라 K 0건. 코드 결함이 아닌 계약 품질 문제로 분류 |
| **합계** | **약 131** | 근사 표시 항목 때문에 정확한 합계가 아니다 |

검증런이 제기했으나 **기각·결번된 항목**은 심사 항목 기준으로 1차 28건(1라운드 26, 2라운드 2)·결번 1묶음(R2-01·R2-11), codex-full 4건, astra-low 1건, 결정대조 4건(행 기준 5), 전면대조 5건이다. 1차 1라운드는 병합 묶음 때문에 행 기준으로는 35행이 기각됐다. 이 가운데 뒤에 실제 운전이나 다른 라운드에서 결함으로 확인된 것은 R1-65(→A-07), R1-M3(R1-09·R1-68, A-09와 인접), R1-M4(R1-10·R1-45 → A-42), 결정대조 R1-05(→A-18), 전면대조 R1-01·13·15(→A-44), 1차 R1-18·27·32(→2라운드 R2-09로 적용)다.

## 3. 개별 기록

### A-01 CLI 샌드박스에서 작업자가 파일을 쓰지 못함

- 출처: `기억/layer1/M-0269.md` 「실행에서 확인한 경계」, `docs/do-math/구현-검증-2026-09-14/feature2/cli-profile/README.md`, `feature2/observation/README.md`(elevated-failure 행), `기억/layer1/M-0265.md` 「확인한 능력과 실패」; 수정 커밋 3d7b280
- 발견 경위: 실제 운전(기능 판본 2 구현 중 실제 `codex exec` 연구 실행)
- 영향 등급: 정지 — 연구 수행 작업자가 파일 변경을 끝내지 못해 산출·체크포인트가 생기지 않았다. 모든 작업 실행에 같은 설정이 적용되므로 연구가 진행될 수 없다.
- 증상: elevated 모드에서 `ShellExecuteExW` 설정 도우미 오류 1223이 나고 `file_change.started` 뒤 완료되지 않았다. unelevated `workspace-write`는 상대 경로와 절대 작업경로 모두에서 쓰기가 거부됐다. 60초 무활동이 운영 점검을 일으켰다.
- 근본 원인: Codex CLI의 Windows 샌드박스(elevated 도우미와 workspace-write 정책)가 이 호스트의 비대화 실행에서 작업 폴더 쓰기를 허용하지 않았다. 구현은 샌드박스 쓰기가 된다는 M-0265의 단일 프로필 시험을 전제로 했다.
- 수정: 3d7b280에서 기본 CLI 실행을 승인 정책 never와 `danger-full-access` 로컬 권한으로 바꾸고, 절대 작업경로와 shell workdir를 모델에 전달했다. 회귀 시험 대신 실제 쓰기·읽기 확인(`feature2/cli-profile/local-access-pass/report.json`)으로 검증했다.
- 결함 유형: 외부 경계
- 트리거: 실제 외부 도구 동작(Codex CLI 샌드박스, Windows 권한), 설정·환경(비대화 실행)
- 결함 위치 층: 경계 어댑터
- 시험 유출 원인: 환경 차이 — M-0265의 쓰기 성공은 사용자가 승인한 elevated 설정 직후 단일 프로필에서 관찰됐고, 실제 연구 흐름의 자동 실행 조건과 달랐다. 1223이 UAC 취소에 해당한다는 해석은 추론이며 원자료에 없다.
- 검증런 유출: 해당 없음(검증런 시작 전 구현 단계에서 발견)
- 가장 싼 포착 시험: 실제 CLI 한 번 호출. 채택한 샌드박스 프로필로 "작업 폴더에 `probe.txt`를 쓰고 다시 읽어 내용을 출력하라"는 고정 프롬프트를 비대화 경로(예약 작업과 같은 부모)로 실행하고, 종료 뒤 파일 존재와 내용 일치를 단언한다.
- 범주 후보: 외부 CLI 실동작 가정

### A-02 낡은 보충 조사 요청이 제어 inbox를 영구히 막음

- 출처: `기억/layer1/M-0268.md` 「실제 실행에서 확인한 수리」 셋째 단락; 수정 커밋 08eecbf
- 발견 경위: 실제 운전(Codex CLI 연구 운전 구현 중 실제 실행)
- 영향 등급: 정지 — 원자료가 "inbox를 영구히 막는 경로"라고 적는다. inbox가 막히면 이후 pause·resume·input·configure 요청이 적용되지 않는다.
- 증상: 접수 뒤 전제가 바뀐 보충 조사 요청이 처리되지 못한 채 inbox 머리에 남아 뒤의 제어 요청이 소비되지 않았다.
- 근본 원인: 제어 요청을 접수 시점의 전제로만 검사하고, 적용 시점에 전제가 사라진 요청을 거부·소비하는 분기가 없었다. 원문 좌표는 08eecbf의 inbox 처리 코드이며 수정 전 판본은 커밋되지 않았다.
- 수정: 08eecbf에서 거부된 요청도 이유와 함께 소비하고 후속 요청을 처리하게 했으며, CLI가 접수와 적용·거부를 구별해 반환하게 했다. 회귀 시험 이름은 커밋에서 특정하지 못했다(`test_controls.py`가 이 커밋에서 신설됨).
- 결함 유형: 검사
- 트리거: 특정 전이 순서(요청 접수 → 전제 변경 → 적용), 사용자·운영 제어
- 결함 위치 층: L2 인터페이스 요소
- 시험 유출 원인: 시험 없음 — 코드가 같은 커밋에서 처음 작성됐다.
- 검증런 유출: 해당 없음
- 가장 싼 포착 시험: 메모리 저장소 실행기에 보충 조사 요청을 inbox에 넣고, 그 대상 검토 cycle을 닫은 뒤 pause 요청을 추가한다. 제어 처리 한 번 뒤 보충 요청이 거부 사유와 함께 소비되고 pause가 적용됐음을 단언한다.
- 범주 후보: 대기·요청의 소비자 부재

### A-03 완료된 인스턴스를 pause/resume이 다시 엶

- 출처: `기억/layer1/M-0268.md` 「실제 실행에서 확인한 수리」 셋째 단락; 수정 커밋 08eecbf; 부모 판본 이후 시험 `test_controls.py::test_pause_and_resume_cannot_reopen_a_completed_instance`
- 발견 경위: 실제 운전
- 영향 등급: 저하 — 종결된 연구가 다시 실행 가능한 상태가 되어 불필요한 실행과 잘못된 상태를 만들 수 있다.
- 증상: 완료(`completed`) 상태에 pause/resume을 보내면 상태가 다시 열렸다.
- 근본 원인: 제어 적용이 종결 상태를 검사하지 않고 lifecycle을 바꿨다.
- 수정: 08eecbf. 시험 `test_pause_and_resume_cannot_reopen_a_completed_instance`가 d03f7d9 이전 판본에 존재한다.
- 결함 유형: 검사
- 트리거: 사용자·운영 제어, 특정 전이 순서
- 결함 위치 층: L2 인터페이스 요소
- 시험 유출 원인: 시험 없음 — 코드와 같은 커밋에서 작성됐다.
- 검증런 유출: 해당 없음
- 가장 싼 포착 시험: 완료 상태의 인스턴스에 pause·resume을 차례로 적용하고 상태가 `completed`로 남으며 대기열에 새 action이 없음을 단언한다.
- 범주 후보: 종결 상태 보호 누락

### A-04 계획 출력이 작업 ID 배열에 설명문을 섞고 미수행 과제를 완료 판정

- 출처: `기억/layer1/M-0268.md` 「실제 실행에서 확인한 수리」 첫 단락; 수정 커밋 08eecbf
- 발견 경위: 실제 운전(첫 CLI 계획 출력)
- 영향 등급: 저하 — 출력이 거부되어 수리 호출이 필요했다.
- 증상: 연구 계획 출력의 작업 ID 배열에 설명 문장이 섞였고, 수행 전 과제까지 완료 판정에 넣었다.
- 근본 원인: 출력 스키마는 문자열 배열만 정했고, 필드가 소비하는 대상 상태와 정확한 ID 복사 방법이 역할 입력에 없었다. 노드 원문: "schema에 문자열 배열이 있다는 사실만으로 소비자가 기대는 의미가 전달되지는 않았다."
- 수정: 08eecbf에서 대상 상태와 ID 복사 방법을 입력에 명시하고 오류와 이전 출력을 돌려주는 한정 수리를 추가했다.
- 결함 유형: 스키마·계약 불일치
- 트리거: 실제 모델 출력 형태
- 결함 위치 층: 계약·스키마
- 시험 유출 원인: 시험 없음 — 대역 응답은 올바른 ID만 담아 실제 모델 출력 형태를 재현하지 않았다(추론).
- 검증런 유출: 해당 없음
- 가장 싼 포착 시험: 계획 출력 수신 함수에 ID 배열 원소가 설명문인 응답과 `ready`가 아닌 과제의 완료 판정을 넣고, 둘 다 구체적 사유와 함께 거부됨을 단언한다. 또한 실제 모델 1회로 계획 역할을 호출해 출력의 모든 ID가 입력 ID 집합에 속하는지 단언한다.
- 범주 후보: 모델 출력과 소비자 계약의 불일치

### A-05 목표 감사 입력에서 완료된 동일성 검토를 숨김

- 출처: `기억/layer1/M-0268.md` 「실제 실행에서 확인한 수리」 둘째 단락; 수정 커밋 08eecbf
- 발견 경위: 실제 운전(목표 감사)
- 영향 등급: 저하 — 목표 감사가 과거 수행 보고의 "검사 예정" 문장을 최신 사실처럼 사용했다. 판정의 근거가 틀렸다.
- 증상: 목표 감사자가 완료된 동일성 검토 결과를 보지 못하고, 오래된 예정 문장을 현재 상태로 읽었다.
- 근본 원인: 같은 단계 동료 판정의 비공개 규칙을 이전 단계의 완료 근거까지 확대해 입력에서 제외했다.
- 수정: 08eecbf에서 이번 동료 판정의 비노출과 이전 단계의 완료 근거 제공을 구별하고, 예정 문장과 후속 결과의 시점을 함께 해석하도록 역할 계약을 고쳤다.
- 결함 유형: 인터페이스
- 트리거: 특정 전이 순서(동일성 검토 완료 → 목표 감사)
- 결함 위치 층: L2 인터페이스 요소
- 시험 유출 원인: 시험 없음 — 같은 커밋에서 작성됐다.
- 검증런 유출: 해당 없음
- 가장 싼 포착 시험: 동일성 검토가 `match`로 완료된 상태에서 목표 감사 입력을 구성하고, 입력에 그 검토 판정과 시각이 들어 있음을 단언한다.
- 범주 후보: 역할 입력 누락

### A-06 명시적 pause가 후속 처분에 의해 ready로 덮임(재발 포함)

- 출처: `기억/layer1/M-0269.md` 「실행에서 확인한 경계」 셋째 단락, `docs/do-math/구현-검증-2026-09-14/feature2/observation/README.md`(inline-and-pause-defect), `임시/do-math_검증_2026-09-15/장부.md` R1-43; 수정 커밋 3d7b280, b4ede4c
- 발견 경위: 실제 운전(실제 긴 명령 중 별도 운영 CLI로 pause); 재발 경로는 검증런
- 영향 등급: 저하 — 사용자 정지가 무시되고 운영 점검과 재시도가 이어진다. 연구가 멈추지 않는 방향의 결함이다.
- 증상: pause 요청은 처리됐지만 구버전 `after_stop` 경로가 최종 상태를 `ready`로 덮었다. 9/15 검증런은 "정지 유예 중 실행이 실패로 끝나면 사용자 pause가 ready로 덮여 운영 점검과 재시도가 이어진다"는 다른 경로를 찾았다.
- 근본 원인: 실행 종료 뒤 후속 처분이 lifecycle 상태를 무조건 대입했다. 3d7b280은 정상 종료 경로만 고쳤고, 실패 종료 경로의 같은 대입은 남았다.
- 수정: 3d7b280에서 명시적 pause와 운영 stop을 유지하게 하고 실제 고정본으로 `paused`를 확인했다(`feature2/observation/pause-fixed`). 실패 경로는 b4ede4c(R1-43)에서 고쳤다. 전용 회귀 시험 이름은 diff에서 특정하지 못했다.
- 결함 유형: 대입·초기화
- 트리거: 사용자·운영 제어, 특정 전이 순서(pause → 유예 → 정상 또는 실패 종료)
- 결함 위치 층: L2 인터페이스 요소
- 시험 유출 원인: 조합·순서 미탐색 — 첫 발견 때 probe의 성공 조건이 "pause 요청 전송"까지여서 최종 상태를 단언하지 않았다(`observation/README.md`: "최상위 `passed: true`도 그 probe가 pause 요청 전송까지만 성공 조건으로 삼았다"). 수정 뒤에는 실패 종료 조합이 시험되지 않았다.
- 검증런 유출: 재발 경로는 9/15 1차 검증런이 찾아 적용했다(R1-43).
- 가장 싼 포착 시험: 대역 실행기로 실행 중 pause를 보내고, 종료 결과를 정상·실패·타임아웃 세 가지로 바꿔 각각 최종 lifecycle이 `paused`임을 단언하는 매개변수화 시험.
- 범주 후보: 사용자 제어의 덮어쓰기

### A-07 개정 계약의 완료 기준이 옛 기준과 합집합으로 저장됨

- 출처: `임시/parking-unimodality-analysis-20260916/분석.md` §2, `기억/layer1/M-0293.md` 마지막 단락, `기억/layer1/M-0295.md` 「확정한 권한과 기본값」, `docs/do-math/개선-검증-2026-09-16/README.md` 분석 대응표 §2 행, `임시/do-math_검증_2026-09-15/장부.md` R1-65; 결함 도입 3d7b280, 수정 d03f7d9
- 발견 경위: 실제 운전(9/15~16 Codex 인스턴스 RI-01M2JP80…, 기록 분석으로 확정)
- 영향 등급: 정지 — 세 과제가 계약 승인을 받을 수 없었다. 분석 원문: "같은 삭제 요청을 다시 제출해도 저장 결과가 달라질 수 없다." 연구는 사용자 HOLD로 끝났다.
- 증상: 후보 준비가 옛 기준을 뺀 새 계약을 제출하면 실행기가 다시 합쳐 저장했다. 자리 보존 사상은 마지막 제안 7개 기준이 16개로, 순열별 곱은 6개가 24개로 저장됐다. 검토자는 모순을 반려하고 준비자는 다시 빼는 순환이 판본 8까지 이어졌다.
- 근본 원인: `engine.py`(d03f7d9 부모 판본 1467행) `criteria = list(dict.fromkeys([*old["completion_criteria"], *criteria]))`. 미완료 의무 보존을 문장 누적으로 구현했다.
- 수정: d03f7d9에서 현행 기준을 교체하고 과거 문면을 이력으로 보존. 회귀 시험 `test_research_recovery.py::test_revised_contract_replaces_obsolete_criteria_and_preserves_history`.
- 결함 유형: 알고리즘
- 트리거: 특정 전이 순서(계약 반려 → 기준을 줄인 개정), 실제 모델 출력 형태(기준 문장의 삭제·재표현)
- 결함 위치 층: L2 인터페이스 요소
- 시험 유출 원인: 합성 입력이 실제와 다름, 단언 약함 — 부모 판본의 개정 시험(`test_purpose_engine.py` 174행, `test_document_followup.py` 44행)은 `candidate()` 도우미가 같은 제목에 같은 기준 문장을 만들어 합집합이 항등이었다. 개정 뒤 기준 목록을 단언하는 시험도 없었다.
- 검증런 유출: 9/15 1차 검증런이 R1-65로 찾았으나 수리 조각 대신 "상신 제안"으로 제출되어 1/3로 기각됐다(심사 사유: "기준 문장을 고칠 수 있게 하는 데 새 사용자 의도를 정할 필요가 있다는 근거가 없다"). 결함 자체는 부정되지 않았으나 수리되지 않은 채 다음 날 실제 운전에서 발현했다.
- 가장 싼 포착 시험: 기준 ["a","b"]인 과제에 기준 ["a'"]인 개정 후보를 적용하고, 저장된 `completion_criteria == ["a'"]`와 이력에 옛 목록이 있음을 단언한다.
- 범주 후보: 계약 저장 규칙

### A-08 종결 과제의 낡은 readiness 투영이 계획을 막음

- 출처: `기억/layer1/M-0294.md`, `기억/layer1/M-0293.md` 마지막 단락, `임시/parking-unimodality-analysis-20260916/분석.md` §3.1; 수정 커밋 d0024f5
- 발견 경위: 실제 운전(독립 운영 담당이 paused 인스턴스를 진단)
- 영향 등급: 정지 — 연구 계획 출력과 수리가 같은 모집단 검사에서 거부되어 인스턴스가 paused였다. 독립 운영 AI가 스킬 코드를 고칠 때까지 풀리지 않았다.
- 증상: task 목록에 ready 과제가 없는데 `runtime.task_readiness`에 completed 과제 두 개가 `ready`로 남아, 계획 AI가 그 과제를 보류 목록에 넣고 거부됐다.
- 근본 원인: `lifecycle_engine._refresh_readiness`가 스케줄 불가 상태의 과제를 건너뛰면서 기존 투영을 지우지 않았다(d0024f5 diff 373행).
- 수정: d0024f5에서 스케줄 불가 과제의 readiness 항목을 제거. 회귀 시험 `test_lifecycle_engine.py::test_completed_task_does_not_retain_ready_projection`.
- 결함 유형: 대입·초기화
- 트리거: 특정 전이 순서(ready 평가 → completed 전이 → 재평가)
- 결함 위치 층: L2 인터페이스 요소
- 시험 유출 원인: 조합·순서 미탐색 — 부모 판본의 readiness 시험은 terminal 전이 뒤의 재평가를 다루지 않았다. 분석 문서에 따르면 운영 담당의 첫 재현 시험도 교체 전 객체를 수정해 한 번 잘못 실패했다.
- 검증런 유출: 9/15 두 검증런 장부에 해당 경로를 지적한 항목이 없다(표 대조).
- 가장 싼 포착 시험: 과제를 ready로 평가한 뒤 status를 completed로 바꾸고 `_refresh_readiness`를 다시 호출해, readiness에 그 과제가 없음을 단언한다. 일반형은 "모든 전이 뒤 `task_readiness`의 키 ⊆ 스케줄 가능 과제" 불변식 검사다.
- 범주 후보: 파생 상태의 전이 경계 정리 누락

### A-09 resume이 수리 소진 계획을 그대로 되살려 같은 정지를 반복

- 출처: `임시/parking-unimodality-analysis-20260916/분석.md` §4, §9 표, `기억/layer1/M-0295.md` 「실패를 수정 가능한 단계로 돌린 변경」, `docs/do-math/개선-검증-2026-09-16/README.md` §4 행; 수정 커밋 d03f7d9
- 발견 경위: 실제 운전(기록 분석)
- 영향 등급: 정지 — 01:03:45와 01:11:19 두 재개에서 같은 계획 action이 다시 실행되어 바로 일시 정지로 돌아갔다. 사용자 HOLD 전까지 풀리지 않았다.
- 증상: 출력 수리 1회를 소진한 계획이 `waiting_actions`에 보관됐다. resume이 이를 수리 횟수와 과거 실패 출력째 대기열에 되돌렸고, 재실행이 실패하자 추가 수리 없이 전체 일시 정지했다. 한 행동의 실패가 다른 준비·검토까지 멈췄다.
- 근본 원인: `engine.py`(d03f7d9 부모 판본 411행)의 resume이 `waiting_actions`의 행동을 모두 queue로 되돌렸고, 수리 소진 실패가 인스턴스 전체를 pause했다.
- 수정: d03f7d9. 회귀 시험 `test_research_recovery.py`의 `test_resume_keeps_failed_output_out_of_execution_queue`, `test_exhausted_output_repair_does_not_stop_unrelated_work`, `test_output_failure_opens_diagnosis_without_replaying_rejected_plan`, `test_diagnosed_plan_retry_uses_fresh_input_and_keeps_failure_evidence`, `test_diagnosis_wait_does_not_block_independent_actions`.
- 결함 유형: 기능
- 트리거: 재시작·복구·재개, 특정 전이 순서(출력 실패 → 수리 실패 → pause → resume)
- 결함 위치 층: L2 인터페이스 요소
- 시험 유출 원인: 조합·순서 미탐색 — 부모 판본의 resume 시험(`test_engine.py::test_work_budget_pause_resume_preserves_queue` 등)은 예산 정지 뒤 재개만 다뤘고, 출력 수리 소진 뒤 재개는 없었다.
- 검증런 유출: 9/15 1차 검증런의 R1-M3(R1-09·R1-68: "실패 진단이 stop이나 wait를 내도 실패한 action이 대기열에 남아 … 재실행된다")가 인접 경로를 찾았으나 수리안이 같은 과제의 새 action 경로를 막지 못한다는 이유로 0/3 기각됐다. resume 경로 자체를 지목한 항목은 없었다.
- 가장 싼 포착 시험: 대역 모델이 계획에 항상 모집단 오류를 내게 하고 `max_output_repairs=1`로 실행한다. 정지 뒤 resume하고, 같은 action ID가 입력 변경 없이 다시 실행되지 않으며 독립 준비 action은 실행됨을 단언한다.
- 범주 후보: 실패 행동의 재개·복구 경로

### A-10 계획 모집단 오류가 누락·과잉·중복을 구별하지 않음

- 출처: `임시/parking-unimodality-analysis-20260916/분석.md` §3.2, `docs/do-math/개선-검증-2026-09-16/README.md` §3.2~3.3 행, `임시/do-math_전면대조_20260917/장부.md` R1-10; 수정 커밋 d03f7d9, f341b26
- 발견 경위: 실제 운전(기록 분석)
- 영향 등급: 저하 — 네 번의 거부가 모두 "plan must select or defer every ready task exactly once" 하나로 전달되어 수리가 어려웠다. 분석은 이것을 실패의 유일한 원인으로 입증하지 않았다고 적는다.
- 증상: 넣지 말아야 할 과제를 넣은 오류도 같은 문구로만 전달됐다.
- 근본 원인: 수신 검사(`engine.py` 1695행, 분석 인용)가 차이 집합을 계산하지 않고 한 문장 오류를 냈다. 생산자와 수신자가 같은 `ready_task_ids`를 공유하지도 않았다.
- 수정: d03f7d9 `test_plan_rejection_names_missing_unexpected_and_duplicate_ids`, `test_plan_input_always_has_authoritative_ready_ids`. 완료 판정 쪽 같은 결함은 f341b26(전면대조 R1-10).
- 결함 유형: 인터페이스
- 트리거: 실제 모델 출력 형태
- 결함 위치 층: L2 인터페이스 요소
- 시험 유출 원인: 단언 약함 — 거부 여부만 단언하고 오류 내용을 고정하지 않았다(부모 판본 시험 대조로 확인한 것은 해당 전용 시험의 부재뿐이며, 기존 시험의 오류 문구 단언 여부는 확인하지 않았다).
- 검증런 유출: 해당 없음(9/15 검증런 장부에 해당 항목 없음). 완료 판정 쪽은 9/17 검증런이 찾았다.
- 가장 싼 포착 시험: ready 집합 {A}에 대해 {A,B}, {}, {A,A}를 제출하는 세 계획을 수신하고, 오류가 각각 과잉 B, 누락 A, 중복 A를 명시함을 단언한다.
- 범주 후보: 모델 출력과 소비자 계약의 불일치

### A-11 연구 실행에 scholarly MCP가 전달되지 않음

- 출처: `임시/parking-unimodality-analysis-20260916/분석.md` §5.1, `기억/layer1/M-0293.md` 마지막 단락, `기억/layer1/M-0295.md` 「실패를 수정 가능한 단계로 돌린 변경」 둘째 단락; 수정 커밋 d03f7d9
- 발견 경위: 실제 운전(기록 분석)
- 영향 등급: 저하 — 문헌 과제의 준비 AI가 "scholarly를 제공하는 실행 프로필과 문법이 없다"며 계약을 내지 못했고, 해당 과제는 끝내 수행에 배정되지 않았다. 인스턴스는 다른 과제로 진행했다.
- 증상: 연구 실행 43회의 도구 로그에 MCP 호출이 없었다. 별도 운영 담당만 scholarly를 호출했다.
- 근본 원인: `codex_worker.py`(d03f7d9 부모 판본 109행)가 `--ignore-user-config`로 실행하면서 scholarly 설정을 명시적으로 전달하지 않았다. 분석은 이 옵션 하나를 미적재의 원인으로 확정하지 않았다.
- 수정: d03f7d9 `scholarly.py` 추가, 설정 회수와 worker 전달. 회귀 시험 `test_codex_adapter.py::test_scholarly_is_the_only_explicit_mcp_and_uses_workspace_data_directory`, `test_research_recovery.py::test_scholarly_configuration_reaches_the_actual_runner_call`, `test_model_runner.py::test_scholarly_server_is_written_to_the_immutable_worker_request`.
- 결함 유형: 외부 경계
- 트리거: 설정·환경, 실제 외부 도구 동작(Codex CLI의 설정 적재)
- 결함 위치 층: 경계 어댑터
- 시험 유출 원인: 시험 없음, 단언 약함 — 부모 판본 `test_codex_adapter.py` 31행은 `--ignore-user-config`가 argv에 있음을 단언해 격리만 고정했고, 사용자가 요구한 도구가 작업자에게 도달하는지는 어떤 시험도 확인하지 않았다.
- 검증런 유출: 9/15 검증런 장부에 해당 항목이 없다. 당시 scholarly 전달은 구현 범위에 없었다.
- 가장 싼 포착 시험: 프로젝트 `config.toml`에 scholarly 서버가 있는 임시 저장소에서 worker 요청을 생성하고, 요청의 MCP 구성에 scholarly가 있음을 단언한다. 추가로 실제 CLI 1회로 `list_sources` 호출 성공을 확인한다.
- 범주 후보: 외부 CLI 실동작 가정

### A-12 새 operator 모듈이 표준 라이브러리 operator를 가려 자식 실패

- 출처: `기억/layer1/M-0295.md` 「실패를 수정 가능한 단계로 돌린 변경」 둘째 단락; 수정 커밋 d03f7d9
- 발견 경위: 실제 운전(구현 중 실제 child 실행)
- 영향 등급: 정지 — "실제 child가 실패했다." 자식 프로세스가 import 단계에서 실패하면 그 경로의 모든 실행이 불가능하다.
- 증상: 스크립트 폴더가 import 경로에 올라간 자식 Python에서 표준 `operator` 대신 새 `operator.py`가 적재되어 실패했다.
- 근본 원인: 새 모듈 이름이 표준 라이브러리 모듈과 같았다. 패키지 경로에서 import하는 시험 환경에서는 충돌하지 않는다(추론).
- 수정: d03f7d9에서 `scheduled_operator.py`로 개명하고 경로 우회를 제거. 직접 실행 import 시험 `test_codex_adapter.py::test_worker_remains_importable_as_its_direct_job_root`가 같은 커밋에 추가됐으나, 이 시험이 이름 충돌을 겨냥한 것인지는 diff만으로 확정하지 못했다.
- 결함 유형: 빌드·패키지
- 트리거: 설정·환경(자식 프로세스의 `sys.path`)
- 결함 위치 층: L3 배선
- 시험 유출 원인: 환경 차이 — 시험은 `do_math` 패키지로 import했고 실제 자식은 스크립트를 직접 실행했다(추론, 수정 전 코드가 커밋되지 않아 확인 불가).
- 검증런 유출: 해당 없음
- 가장 싼 포착 시험: 스크립트 폴더의 모든 모듈 이름이 `sys.stdlib_module_names`와 겹치지 않음을 단언하는 정적 시험. 그리고 각 자식 진입 스크립트를 실제 `python <script> --help`로 실행해 import 오류가 없음을 단언한다.
- 범주 후보: 실행 환경의 import·직렬화

### A-13 예약 운영 영수증의 bytes를 JSON으로 쓰지 못함

- 출처: `기억/layer1/M-0295.md` 「실패를 수정 가능한 단계로 돌린 변경」 셋째 단락; 수정 커밋 d03f7d9
- 발견 경위: 실제 운전(실제 Windows 예약 probe)
- 영향 등급: 정지 — 예약 운영 경로의 CLI가 결과를 직렬화하지 못해 실패했다. 독립 운영 점검이 보고를 남기지 못하면 자동 운영이 성립하지 않는다(운영 경로에 한정).
- 증상: raw bytes가 든 모델 영수증을 JSON으로 쓰다 실패했다.
- 근본 원인: 운영 결과 반환과 최신 보고에 bytes 필드를 가진 영수증을 그대로 넣었다.
- 수정: d03f7d9 공통 `json_safe`, 원 영수증은 실행별 result에 두고 보고에는 요약·경로만. 회귀 시험 `test_operator.py::test_cli_emits_byte_bearing_operator_receipt_as_json`.
- 결함 유형: 인터페이스
- 트리거: 실제 외부 도구 동작(모델 영수증의 실제 형태)
- 결함 위치 층: L3 배선
- 시험 유출 원인: 합성 입력이 실제와 다름 — 신설 시험의 대역 영수증에 bytes가 없었다(추론; 수정 전 시험 판본은 커밋되지 않음).
- 검증런 유출: 해당 없음
- 가장 싼 포착 시험: bytes 필드를 가진 실제 형태의 영수증을 대역 runner가 반환하게 하고 `operator check` CLI의 stdout이 유효한 JSON임을 단언한다.
- 범주 후보: 실행 환경의 import·직렬화

### A-14 실제 scholarly 설정의 timeout 키 때문에 설정 전체 거부

- 출처: `기억/layer1/M-0295.md` 「실패를 수정 가능한 단계로 돌린 변경」 둘째 단락; 수정 커밋 d03f7d9
- 발견 경위: 기타(구현 중 실제 프로젝트 설정으로 실행)
- 영향 등급: 정지(추론) — 설정이 거부되면 scholarly를 전달하는 모든 연구 실행이 시작 전에 실패한다. 원자료는 "설정을 거부하던 새 구현 오류"라고만 적는다.
- 증상: 프로젝트 `config.toml`의 scholarly 테이블에 `startup_timeout_sec`·`tool_timeout_sec` 같은 키가 있었고, command·args 두 키만 허용하는 검사가 테이블 전체를 거부했다.
- 근본 원인: 추출할 키만 고르지 않고 테이블 전체를 닫힌 검사에 넘겼다.
- 수정: d03f7d9. 회귀 시험 `test_scholarly.py::test_project_config_beats_code_home_and_extracts_only_scholarly`(픽스처에 두 timeout 키 포함), `test_rejects_non_scholarly_fields_and_data_directory_override`.
- 결함 유형: 검사
- 트리거: 설정·환경(실제 사용자 설정 파일의 형태)
- 결함 위치 층: 경계 어댑터
- 시험 유출 원인: 합성 입력이 실제와 다름 — 초기 픽스처가 command·args만 가졌다(추론).
- 검증런 유출: 해당 없음
- 가장 싼 포착 시험: 실제 `.codex/config.toml` 사본(또는 그 키 구성을 복제한 픽스처)으로 설정 해석 함수를 호출해 command·args만 추출됨을 단언한다.
- 범주 후보: 외부 CLI 실동작 가정

### A-15 HOLD 해제와 정지 적용의 경합

- 출처: `기억/layer1/M-0295.md` 「실패를 수정 가능한 단계로 돌린 변경」 넷째 단락, `docs/do-math/개선-검증-2026-09-16/README.md` 「확정된 동작」 넷째 단락, `hold-race-*-green.txt`; 수정 커밋 d03f7d9
- 발견 경위: 정적 검토(구현 중 경로 검토 후 재현)
- 영향 등급: 정지(추론) — 이미 해제한 HOLD의 정지가 나중에 남으면, 자동 운영은 사용자 정지를 풀 수 없으므로 사람이 풀 때까지 연구가 멈춘다. 반대 경우에는 다른 사용자 정지를 풀어 버린다.
- 증상: 운전 미발현
- 근본 원인: 해제를 접수 시점에만 확인해, 아직 적용되지 않은 HOLD의 pause와 순서가 뒤집힐 수 있었다.
- 수정: d03f7d9에서 해제 요청이 정확한 HOLD ID의 예상 정지 사유를 함께 내고 실행기가 적용 시 최신 `user_pause`와 대조. 회귀 시험 `test_research_recovery.py::test_conditional_hold_release_preserves_a_different_user_pause`, `test_conditional_hold_release_handles_a_pause_still_in_the_inbox`, `test_operator.py::test_release_submits_a_conditional_resume_even_before_hold_pause_is_applied`.
- 결함 유형: 타이밍·직렬화
- 트리거: 동시성·경합, 사용자·운영 제어
- 결함 위치 층: L2 인터페이스 요소
- 시험 유출 원인: 시험 없음 — HOLD 기능이 같은 커밋에서 스킬로 옮겨졌다.
- 검증런 유출: 해당 없음
- 가장 싼 포착 시험: inbox에 hold-pause와 release를 연달아 넣은 뒤 제어를 한 번에 처리하고 최종 `user_pause`가 없음을 단언한다. 다른 사용자 pause가 있을 때는 그것이 남음을 단언한다.
- 범주 후보: 사용자 제어의 덮어쓰기

### A-16 Git 자식 프로세스가 콘솔 창을 반복 표시

- 출처: `기억/layer1/M-0307.md` 첫 단락과 다섯째 단락, `docs/do-math/console-launch-2026-09-17.json`(before flags 0, after 134217728), `docs/do-math/efficiency-repair-2026-09-18.md` 표 10행; 수정 커밋 b134089
- 발견 경위: 사용자 지적(실제 운전 중 반복되는 창)
- 영향 등급: 저하 — 연구 실행 중 사용자 화면에 창이 반복적으로 나타났다.
- 증상: pythonw로 도는 실행기의 Git 호출마다 conhost가 붙은 콘솔이 생겼다(`console_handle` 비0).
- 근본 원인: Windows Job 경로(`windows_job.py` 390행)만 `CREATE_NO_WINDOW`를 썼고, Git 저장소 호출은 플래그 없이 프로세스를 만들었다.
- 수정: b134089. 회귀 시험 `test_background_processes.py::test_real_git_descendants_are_observed_without_visible_windows`, `test_all_managed_subprocess_calls_explicitly_prevent_console_creation`, `test_pythonw_git_calls_have_no_console_and_preserve_binary_state`.
- 결함 유형: 외부 경계
- 트리거: 설정·환경(콘솔 없는 pythonw 부모), 실제 외부 도구 동작(Windows 프로세스 생성)
- 결함 위치 층: 경계 어댑터
- 시험 유출 원인: 환경 차이, 시험 없음 — 시험은 콘솔이 있는 python에서 돌아 창이 새로 생기지 않는다. 부모 판본에서 creationflags를 단언한 시험은 Windows Job 시험(`test_windows_job.py` 185행) 하나였다.
- 검증런 유출: 해당 없음
- 가장 싼 포착 시험: 제품 코드의 모든 `subprocess` 호출이 `creationflags`에 `CREATE_NO_WINDOW`를 갖는지 AST로 검사하는 정적 시험.
- 범주 후보: 외부 CLI 실동작 가정

### A-17 최초 계획이 준비 결과 전에 실행돼 준비를 다시 요청

- 출처: `기억/layer1/M-0307.md` 셋째 단락, `docs/do-math/efficiency-repair-2026-09-18.md` 표 2행과 「초기 계획이 기다리는 조건」; 수정 커밋 b134089
- 발견 경위: 사용자 지적(호출·입력 수 문제 제기) 뒤 기록 분석
- 영향 등급: 저하 — 불필요한 준비·계획 왕복과 입력 비용.
- 증상: 시작 전 학술 요구 등록이 계획 요청을 만들었고, 최초 준비와 병렬로 시작한 계획이 준비 정보 없이 다시 준비를 요청했다. 실행기는 그 의무를 보수적으로 보존했다.
- 근본 원인: 초기 등록 계획에 첫 판단 자료를 기다리는 조건이 없었다.
- 수정: b134089. 회귀 시험 `test_efficiency.py::test_initial_registration_waits_but_preserves_its_event`, `test_scheduler_first_plan_receives_an_approved_candidate_and_consumes_registration`, `test_empty_or_failed_initial_preparation_does_not_wait_forever`, `test_plan_receives_public_running_preparation_without_private_output`. 이 대기 기제는 뒤에 8694693에서 폐기됐다(`docs/do-math/시험-지도-2026-09-28/README.md` 344행).
- 결함 유형: 타이밍·직렬화
- 트리거: 특정 전이 순서(초기화 → 준비·계획 병렬)
- 결함 위치 층: L2 인터페이스 요소
- 시험 유출 원인: 시험 없음 — 호출 수·왕복을 단언하는 시험이 없었다.
- 검증런 유출: 해당 없음
- 가장 싼 포착 시험: 대역 모델로 초기화부터 첫 연구 수행 배정까지 돌리고, 역할별 호출 수(준비 1, 계획 1)와 계획 입력에 준비 결과가 있음을 단언한다.
- 범주 후보: 판단 대상 없는 실행의 발동

### A-18 무변경 상태의 반복 커밋과 과다한 Git 프로세스

- 출처: `기억/layer1/M-0307.md` 넷째 단락, `docs/do-math/efficiency-repair-2026-09-18.md` 「저장 비용의 관찰」, `docs/do-math/console-launch-2026-09-17.json`(`unchanged_idle_save_location`), `임시/do-math_결정대조_검증_20260916/장부.md` R1-05, `기억/layer1/M-0299.md` R1-05 단락; 수정 커밋 b134089
- 발견 경위: 실제 운전(9/17 인스턴스의 저장 관찰); 먼저 검증런이 찾음
- 영향 등급: 저하 — 원자료 38개 읽기에 Git 38회, 한 저장에 Git 50회. `--watch` 대기 순회가 새 사건 없이 상태 커밋을 만들었다.
- 증상: 대기 순회마다 `updated_at`만 다른 상태 커밋이 생겼고, 원자료와 상태를 파일별 Git 프로세스로 읽고 썼다.
- 근본 원인: 저장 비교에 `updated_at`이 포함됐고, 준비 평가 시각이 내용과 무관하게 갱신됐으며, Git 입출력이 파일 단위였다.
- 수정: b134089. 회귀 시험 `test_efficiency.py::test_repeated_idle_save_does_not_publish_but_real_changes_do`, `test_reopened_idle_engine_does_not_publish_again`, `test_readiness_timestamp_changes_only_with_its_evidence`, `test_task_result_materialization_batches_reads_without_losing_files`, `test_git_store.py::test_many_blobs_use_one_hash_process_and_preserve_raw_bytes`, `test_batch_read_is_exact_and_missing_blob_is_an_error`.
- 결함 유형: 알고리즘
- 트리거: 장시간 누적(대기 순회 반복, 원자료 수)
- 결함 위치 층: L3 배선
- 시험 유출 원인: 단언 약함, 시간·규모 미재현 — 시험은 저장 결과를 단언했지만 커밋 수·프로세스 수를 단언하지 않았고, 대기 순회를 반복시키지 않았다.
- 검증런 유출: 9/16 결정대조 검증런이 R1-05("세션 모드 --watch 대기 루프가 0.2초마다 새 상태 커밋을 공개한다")로 찾았으나, 수리안이 head와 status만 비교해 같은 순회의 실제 사건 저장까지 생략할 수 있다는 이유로 기각됐다. 다음 날 실제 운전에서 관찰됐다.
- 가장 싼 포착 시험: 대기열이 빈 실행기를 `--watch` 순회 20회 돌리고 ref의 커밋 수가 늘지 않음을 단언한다. 원자료 N개 복원에서 Git 프로세스 수가 상수임을 단언한다.
- 범주 후보: 판단 대상 없는 실행의 발동

### A-19 모델 시작 전 정지에도 체크포인트 유예를 적용

- 출처: `기억/layer1/M-0307.md` 넷째 단락 끝, `docs/do-math/efficiency-repair-2026-09-18.md` 표 3행, 「검증과 한계」 마지막 단락(약 35초 정지); 수정 커밋 b134089
- 발견 경위: 실제 운전(정지 지연 관찰 뒤 재현)
- 영향 등급: 저하 — 사용자 정지가 늦게 적용됐다(원자료가 "과거 정지에 걸린 약 35초"라고 적으며 원인별 비중은 확정하지 않음).
- 증상: 입력 준비 중·모델 시작 전 정지에도 수행 중 실행과 같은 체크포인트 유예를 기다렸다. 입력 준비 중 다른 실행의 알림이 입력을 반복 폐기하게 할 위험도 함께 발견됐다.
- 근본 원인: 정지 확인이 모델 시작 여부를 구별하지 않았다.
- 수정: b134089. 회귀 시험 `test_efficiency.py::test_pause_received_during_input_preparation_prevents_model_start`, `test_pause_before_model_resume_has_no_checkpoint_grace`, `test_running_model_keeps_checkpoint_grace_after_initial_check`.
- 결함 유형: 타이밍·직렬화
- 트리거: 사용자·운영 제어, 특정 전이 순서(입력 준비 중 정지)
- 결함 위치 층: L3 배선
- 시험 유출 원인: 조합·순서 미탐색 — 정지 시점을 입력 준비 단계에 두는 시험이 없었다(부모 판본에서 전용 시험 부재만 확인).
- 검증런 유출: 해당 없음
- 가장 싼 포착 시험: 입력 준비 콜백 안에서 pause를 보내고, 모델 runner가 한 번도 호출되지 않으며 종료까지 걸린 시간이 유예 시간보다 짧음을 단언한다.
- 범주 후보: 기한·시간 경계

### A-20 rate_limit_event가 init보다 먼저 와 정상 결과를 거부

- 출처: `기억/layer1/M-0308.md` 넷째 단락, `docs/do-math/claude-cli-validation-2026-09-18.json` `initial_live_failure`, `.skill-workspace/do-math-claude/rate-before-init-red.log`; 수정 커밋 ef0863a
- 발견 경위: 실제 운전(Claude 2.1.274 scholarly 실호출)
- 영향 등급: 정지 — 해석기가 정상 결과를 거부했다. 이 사건 순서가 나오는 실행은 모두 실패한다.
- 증상: `rate_limit_event`가 `system/init`보다 먼저 도착했고, 시작 사건이 첫 줄이어야 한다는 검사가 결과를 거부했다.
- 근본 원인: 사건 순서를 CLI 명세 추정으로 고정했다.
- 수정: ef0863a에서 시작 전 제한 알림만 허용하고 시작 전 실제 작업·세션 혼합·중복 결과는 계속 거부. 회귀 시험 `test_claude_adapter.py::test_rate_notification_can_precede_init_but_work_cannot`.
- 결함 유형: 외부 경계
- 트리거: 실제 외부 도구 동작(CLI 판본별 사건 순서)
- 결함 위치 층: 경계 어댑터
- 시험 유출 원인: 합성 입력이 실제와 다름 — red 로그에 따르면 기존 7개 시험은 모두 통과했고, 모든 픽스처가 `INIT`으로 시작했다(`ef0863a:test_claude_adapter.py`의 `stream(INIT, …)`).
- 검증런 유출: 해당 없음(검증런은 Claude 연동 전에 끝났다)
- 가장 싼 포착 시험: 실제 CLI 호출에서 녹화한 원 JSONL을 골든 픽스처로 보존하고 해석기가 `parse_complete=True`를 반환함을 단언한다.
- 범주 후보: 외부 CLI 실동작 가정

### A-21 Claude CLI가 역할 스키마의 `$schema`·`x-contract-id`를 거부

- 출처: `기억/layer1/M-0309.md` 둘째 단락, `docs/do-math/opus-only-validation-2026-09-18.json` `initial_errors`, `research/problem-selection-2026-09-15/progress-2026-09-18/analysis.md` 첫 표 11:51~12:06 행; 수정 커밋 bc63b58
- 발견 경위: 실제 운전(인스턴스 RI-01M2S6Y5… 시작)
- 영향 등급: 정지 — 모델 응답 전에 실패했다. 모든 역할 스키마에 두 주석이 있으므로 모든 Claude 실행이 실패한다. 인스턴스를 종결하고 새로 시작했다.
- 증상: "no schema with key or ref https://json-schema.org/draft/2020-12/schema", 이어서 "strict mode: unknown keyword: x-contract-id".
- 근본 원인: 역할 스키마 원본을 그대로 `--json-schema`에 넘겼다. Claude CLI는 Draft 2020-12 메타 스키마와 사용자 정의 키워드를 받지 않았다.
- 수정: bc63b58에서 Claude 전달 사본에서만 두 주석 제거. 회귀 시험 `test_claude_adapter.py::test_role_schemas_reach_claude_without_unsupported_meta_schema`.
- 결함 유형: 외부 경계
- 트리거: 실제 외부 도구 동작
- 결함 위치 층: 경계 어댑터
- 시험 유출 원인: 합성 입력이 실제와 다름 — ef0863a의 worker 시험은 `{"type":"object"}` 스키마를 썼고 실제 역할 스키마를 한 번도 전달하지 않았다. M-0309 원문: "작은 실호출 스키마 검증은 실제 역할 스키마의 CLI 수용성과 보조 모델 소비를 확인하지 않았던 범위다."
- 검증런 유출: 해당 없음
- 가장 싼 포착 시험: 실제 역할 스키마 10개 전건을 Claude 전달 경로로 변환한 결과에 `$schema`와 `x-` 접두 키가 없음을 단언한다. 실제 CLI 1회로 가장 복잡한 역할 스키마를 넘겨 구조화 응답이 나옴을 확인한다.
- 범주 후보: 외부 CLI 실동작 가정

### A-22 주 모델을 지정해도 Haiku 보조 호출이 발생

- 출처: `기억/layer1/M-0309.md` 셋째 단락, `docs/do-math/opus-only-validation-2026-09-18.json` `before_model_lock`, `research/.../analysis.md` 232행; 수정 커밋 bc63b58
- 발견 경위: 실제 운전(실제 응답의 `modelUsage` 확인)
- 영향 등급: 저하 — 사용자의 Opus 전용 정책에 어긋나는 소비가 발생했다.
- 증상: `modelUsage`에 `claude-haiku-4-5-20251001`과 `claude-opus-5`가 함께 나왔다. 수정 중 `CLAUDE_CODE_SUBAGENT_MODEL_FORCE`에 모델명을 넣는 오류도 공식 문서 대조로 발견됐다(값은 `1`이어야 함).
- 근본 원인: 주 모델 지정과 작업 배정만으로 CLI 내부 보조 모델 선택이 제한되지 않았다.
- 수정: bc63b58 인스턴스 옵션 `claude_only_assigned_model`(availableModels·fallback·환경 변수 강제). 회귀 시험 `test_claude_adapter.py::test_model_lock_is_opt_in_and_reaches_only_claude`.
- 결함 유형: 외부 경계
- 트리거: 실제 외부 도구 동작
- 결함 위치 층: 경계 어댑터
- 시험 유출 원인: 시험 없음, 대역이 가림 — 모델 runner 대역은 `modelUsage`를 보고하지 않았다.
- 검증런 유출: 해당 없음
- 가장 싼 포착 시험: 모델 잠금이 켜진 설정으로 worker 인자·환경을 생성해 availableModels·fallback·보조 모델 변수를 단언하고, 실제 CLI 1회 응답의 `modelUsage` 키가 배정 모델 하나뿐임을 단언한다.
- 범주 후보: 외부 CLI 실동작 가정

### A-23 같은 Claude 세션의 여러 결과 구간을 수집기가 거부

- 출처: `docs/do-math/review-2026-09-18/plan.md` P01, 시각표 12:16:22~12:22:50 행, `기억/layer1/M-0311.md` 셋째 단락, `기억/layer1/M-0315.md` 「Claude Code CLI 2.1.276」 단락, `research/.../analysis.md` 138행; 수정 커밋 98ac7e5
- 발견 경위: 실제 운전(첫 정확 계산 실행)
- 영향 등급: 저하 — 한 실행의 반환이 수집 실패로 끝나 재시도로 회수했다. 긴 계산을 백그라운드로 돌리는 모든 실행이 같은 경로에 걸린다.
- 증상: 같은 `session_id`에서 `system/init` 3개와 `result` 3개가 나왔고 뒤의 두 결과는 `origin.kind=task-notification`이었다. 재생 결과 `invalid_session_start`, `invalid_terminal_count_or_position`. 수정 구현 중 CLI 2.1.276은 최종 응답 뒤 백그라운드 작업의 종료 정리 사건도 냈다.
- 근본 원인: `claude_adapter.parse_jsonl`이 init·result가 각각 하나이고 result가 마지막이라고 요구했고, `claude_worker.run`은 마지막 사건에서만 `structured_output`을 꺼냈다.
- 수정: 98ac7e5 공통 `claude_stream.py`. 회귀 시험 `test_claude_stream.py`(신설)의 `test_three_segments_choose_correction_and_separate_usage_scopes`, `test_trailing_noop_retains_submission_but_new_work_requires_submission`, `test_later_failure_or_truncation_cannot_fall_back_to_old_success`, `test_native_terminal_cleanup_preserves_partial_submission_and_stop_evidence`, `test_all_reported_models_survive_last_segment_overwrite`.
- 결함 유형: 외부 경계
- 트리거: 실제 외부 도구 동작(백그라운드 작업 알림), 실제 모델 출력 형태(긴 계산을 백그라운드로 실행)
- 결함 위치 층: 경계 어댑터
- 시험 유출 원인: 합성 입력이 실제와 다름, 단언 약함 — ef0863a의 `test_error_truncation_duplicate_terminal_and_session_mismatch_fail`이 `stream(INIT, RESULT, RESULT)`를 거부해야 한다고 단언해, 실제로 정상인 형태를 오류로 고정했다.
- 검증런 유출: 해당 없음
- 가장 싼 포착 시험: 12:16 실행의 원 JSONL을 골든 픽스처로 보존하고 마지막 완결 구간의 제출이 선택됨을 단언한다. 실제 CLI 1회로 "백그라운드로 sleep 5 후 파일 쓰기, 완료 확인 뒤 제출" 프롬프트를 실행해 수집 성공을 확인한다.
- 범주 후보: 외부 CLI 실동작 가정

### A-24 공급자 세션 한도를 일반 실패로 처리해 진단 연쇄 실패·자동 재개 없음

- 출처: `docs/do-math/review-2026-09-18/operator-2002-diagnosis.md`, `plan.md` P02, `research/.../analysis.md` 「연구가 멈춘 직접 원인」, `기억/layer1/M-0310.md` 넷째 단락, `기억/layer1/M-0311.md` 셋째 단락; 수정 커밋 98ac7e5
- 발견 경위: 실제 운전
- 영향 등급: 저하 — 15:34~15:37에 원 작업 8건과 그 진단 8건이 한도로 실패했고, 16:02·18:02 독립 운영도 실패했다. 18:20 해제 뒤 20:02 독립 운영 AI가 수동 진단을 요청하기까지 연구가 `waiting`이었다. 사람이 아닌 예약 운영 AI가 풀었으므로 서식상 정지는 아니지만, 실행기만으로는 풀리지 않았다.
- 증상: 429 "You've hit your session limit"를 `execution_failure`로 분류해 같은 한도에 걸릴 운영 점검을 연쇄로 열었다. 해제 시각에 깨어날 주체가 없었다.
- 근본 원인: `model_runner`가 실패 종류를 구조화하지 않았고, 공급자 대기 상태와 재관찰 예약이 없었다(운영 진단 원문: "한도 초기화 뒤에도 수동 진단 요청 없이는 재개되지 않는다").
- 수정: 98ac7e5 `provider_waits` 공유 게이트, `operator wake` 일회성 예약. 회귀 시험 `test_provider_recovery.py`(신설)의 `test_quota_preserves_original_action_without_diagnostic_calls_then_restores_files`, `test_wake_keeps_hold_and_user_pause_and_only_requests_engine`, `test_provider_wait.py`(신설)의 `test_restriction_blocks_both_pools_and_survives_another_owner`, `test_late_success_does_not_release_a_newer_rejection`, `test_unknown_limit_uses_bounded_backoff_and_known_limit_preserves_time`, `test_dead_probe_owner_is_reconciled_without_claiming_success`, `test_two_real_processes_admit_one_probe`.
- 결함 유형: 기능
- 트리거: 실제 외부 도구 동작(공급자 한도), 시간 경과·기한
- 결함 위치 층: L3 배선
- 시험 유출 원인: 시험 없음
- 검증런 유출: 해당 없음
- 가장 싼 포착 시험: 대역 runner가 세 실행에 모두 429 한도 결과를 반환하게 하고, 이후 모델 호출 0회, 운영 점검 생성 0건, 재관찰 예약 1건을 단언한다. 가짜 시계를 해제 시각 뒤로 옮겨 원 action이 한 번 재실행됨을 단언한다.
- 범주 후보: 대기·요청의 소비자 부재

### A-25 인용 과제·지식의 무관한 상태 변화로 반환을 거부

- 출처: `docs/do-math/review-2026-09-18/plan.md` P03, `dialogue-review.md`, `research/.../analysis.md` 140~144행, `기억/layer1/M-0310.md`·`M-0311.md`·`M-0312.md`; 수정 커밋 98ac7e5(14:02 독립 운영의 미커밋 수리를 포함해 통합)
- 발견 경위: 실제 운전
- 영향 등급: 저하 — 169실행 중 현재성 거부 40건(계약 검토 5, 계획 17, 준비 5, 운영 점검 8 + 추가 5). 판본 대조로 26건은 계약·결과·종결이 유지된 변화였다. 선형 구간 과제의 승인 응답은 13:20경 수락되지 않아 오래 대기했다. 이 40건 전부가 오거부라는 판정은 원자료에 없다.
- 증상: 계획자가 과제 A를 인용하는 동안 다른 실행이 A의 상태를 바꾸면 전체 레코드 해시 변화로 출력이 거부됐다.
- 근본 원인: `knowledge.capture_basis/validate_basis`가 인용 기록 전체 해시와 상태를 비교했다(implementation-plan 02절).
- 수정: 98ac7e5 `decision_basis`(내용·효력·대상 적용 조건 분리). 회귀 시험 `test_currentness_recovery.py::test_cited_task_lifecycle_change_during_plan_does_not_reject_the_plan`, `test_cited_task_contract_change_during_plan_rejects_the_plan`, `test_decision_basis.py::test_task_bookkeeping_and_appended_results_are_not_content_changes`, `test_verified_upgrade_keeps_identical_content_but_not_unknown_author_fields`, `test_planning.py::test_cited_task_basis_ignores_lifecycle_and_appended_results_but_not_contract_rewrites`.
- 결함 유형: 검사
- 트리거: 동시성·경합(세션 예산 병렬 실행), 특정 전이 순서
- 결함 위치 층: L2 인터페이스 요소
- 시험 유출 원인: 조합·순서 미탐색, 시간·규모 미재현 — 병렬 배정(b6fc99d, 9/16) 이후에야 인용 기록이 실행 중에 바뀌는 조합이 흔해졌다. 기존 시험은 전제 변경 시 거부만 단언했다(부모 판본의 개별 시험 내용은 확인하지 않음).
- 검증런 유출: 해당 없음(검증런은 과소 검사 쪽 R1-09 `workspace:` 별칭을 찾았다)
- 가장 싼 포착 시험: 계획 실행 중 인용 과제의 status를 `ready→performing`으로 바꾸고 검토 기록을 하나 추가한 뒤 반환을 수신해 수락됨을 단언한다. 같은 조건에서 계약 필드를 바꾸면 거부됨을 단언한다.
- 범주 후보: 현재성 검사 범위

### A-26 실행기 기한 도래·직전 착수로 진행 중 실행이 끊김

- 출처: `docs/do-math/review-2026-09-18/plan.md` P04, 시각표 14:07 행, `research/.../analysis.md` 146행, `기억/layer1/M-0321.md` 「기한 임박 가드」; 수정 커밋 98ac7e5, 9d81400
- 발견 경위: 실제 운전
- 영향 등급: 저하 — 14:07:07~14:07:12에 2시간 실행기 기한으로 진행 중 실행 3개가 종료됐다. 9/19 운전에서는 계획 #64가 기한 94초 전에 시작해 미완료로 끝났다.
- 증상: 작업자는 실제 남은 시간을 받지 못했고(`execution_limits`에 원 설정값만 있음), 기한 직전에도 새 실행이 시작됐다.
- 근본 원인: 실제 기한 전달과 종료 예고, 착수 여유 검사가 없었다. 98ac7e5가 추가한 가드는 예고 시간 60초만 고려했다.
- 수정: 98ac7e5(`execution-window.json`, `finish-request.json`; 시험 `test_execution_window.py`의 `test_actual_remaining_time_and_notice_do_not_revoke_authority`, `test_operational_window_obeys_both_run_and_call_bounds`), 9d81400(`dispatch_reserve_seconds`; 시험 `test_run_feedback.py`의 `test_no_ordinary_execution_starts_inside_the_reserve_before_the_run_deadline`, `test_reserve_follows_the_notice_idiom_and_never_exceeds_a_tenth_of_the_run`). run 기한은 9/23 후속 수리 1번에서 제거됐다.
- 결함 유형: 타이밍·직렬화
- 트리거: 시간 경과·기한
- 결함 위치 층: L3 배선
- 시험 유출 원인: 시간·규모 미재현 — 시험은 짧은 run과 짧은 대역 작업을 써서 기한 도래 시점의 진행 중 실행을 만들지 않았다(추론).
- 검증런 유출: 해당 없음. 9/15 1차 R1-34(A-37)는 다른 기한(운영 호출 기한의 오적용)이다.
- 가장 싼 포착 시험: 가짜 시계로 run 기한을 100초로 두고 남은 시간 50초에서 착수 요청을 넣어, 일반 실행이 시작되지 않음과 진행 중 실행의 입력 창 파일에 실제 기한이 기록됨을 단언한다.
- 범주 후보: 기한·시간 경계

### A-27 관찰 규칙이 정상 작업을 반복 운영 점검

- 출처: `docs/do-math/review-2026-09-18/plan.md` P04 셋째 단락(120초 무활동 점검), `기억/layer1/M-0321.md` 「발동 횟수의 원인」 운영 점검 29회; 수정 커밋 98ac7e5, 9d81400
- 발견 경위: 실제 운전(기록 분석)
- 영향 등급: 저하 — 9/19 운전의 운영 점검 29회는 5분 넘게 돈 실행 14개에 붙은 것이며 판정은 continue 17, checkpoint 10, 폐기 2였다. [[M-0325]]에 따르면 운영 점검은 비용의 14.4%다.
- 증상: 9/18 판본은 120초 동안 완성된 사건이 없으면 점검을 열었다. 이를 고친 98ac7e5 판본은 event_driven 모드에서도 도구 대기·출력 전송 상태가 300초 지나면 점검을 열어 사실상 5분 타이머가 됐다.
- 근본 원인: `observations.py`의 tool_wait/output_streaming 분기가 `when - self.last_review >= interval`만으로 발동했다(9d81400 diff).
- 수정: 9d81400 event_driven에서 선언 timeout 초과·무기한 대기(600초)만 발동, 첫 체크포인트 알림은 실행기가 직접 기록. 회귀 시험 `test_observations.py::test_event_driven_wait_inside_a_declared_tool_timeout_is_not_reviewed_by_elapsed_time`, `test_event_driven_wait_on_a_tool_without_timeout_is_reviewed_once_per_unbounded_wait`, `test_event_driven_streaming_with_work_events_is_not_reviewed_by_elapsed_time`, `test_periodic_mode_still_reviews_waiting_states_each_interval`, 그리고 같은 파일의 체크포인트 알림 시험 3개(`test_missing_checkpoint_reminder_is_emitted_once_for_checkpointing_roles_only` 등).
- 결함 유형: 알고리즘
- 트리거: 시간 경과·기한, 실제 모델 출력 형태(긴 도구 실행)
- 결함 위치 층: L2 인터페이스 요소
- 시험 유출 원인: 단언 약함 — 9d81400 부모 판본의 `test_transport_and_tool_wait_are_bounded_without_becoming_math_progress`(25~36행)가 기본 모드에서 interval 경과 뒤 `output_streaming_review`가 나와야 한다고 단언해 타이머 동작을 기대값으로 고정했다. 서식의 값 중 가장 가까운 것을 골랐다(4절 참고).
- 검증런 유출: 9/15 1차 R1-17("정직한 no_progress 체크포인트 하나가 곧바로 운영 점검을 열고")이 인접 발동 규칙을 지적했으나 기각됐다. 타이머 자체는 검증런 이후에 도입됐다.
- 가장 싼 포착 시험: timeout 3,600초를 선언한 도구가 20분간 실행 중인 관찰 기록을 재생하고 운영 점검 요청이 0건임을 단언한다.
- 범주 후보: 판단 대상 없는 실행의 발동

### A-28 생산자가 허용되지 않는 `used_sources`를 제출

- 출처: `docs/do-math/review-2026-09-18/plan.md` P08, `research/.../analysis.md` 137행; 수정 커밋 98ac7e5
- 발견 경위: 실제 운전
- 영향 등급: 저하 — 2건의 반환이 적용되지 않았다.
- 증상: 응답의 `used_sources`가 입력에 제공된 근거가 아닌 실행 ID·action ID를 가리켰다.
- 근본 원인: 허용 참조의 종류·위치가 생산자 입력과 오류 안내에 연결되지 않았다. 사전 검사 도구는 있었지만 허용값 목록을 주지 않았다.
- 수정: 98ac7e5 `reference_catalog`와 별칭 정규화. 회귀 시험 `test_reference_catalog.py`(신설)의 `test_current_aliases_and_historical_bytes_remain_distinct`, `test_fixed_question_catalog_only_exposes_its_source_set`.
- 결함 유형: 인터페이스
- 트리거: 실제 모델 출력 형태
- 결함 위치 층: L2 인터페이스 요소
- 시험 유출 원인: 시험 없음 — 허용 참조 목록이 입력에 있는지 확인하는 시험이 없었다(추론).
- 검증런 유출: 해당 없음
- 가장 싼 포착 시험: 각 역할의 입력 문맥을 생성해, 제출 검사기가 허용하는 참조 집합이 입력의 참조 목록과 같음을 단언한다.
- 범주 후보: 모델 출력과 소비자 계약의 불일치

### A-29 Lean 선언명의 끝 작은따옴표를 거부

- 출처: `docs/do-math/review-2026-09-18/plan.md` P08 둘째 단락, `기억/layer1/M-0315.md` 「Windows의 일회성 wake」 단락; 수정 커밋 98ac7e5
- 발견 경위: 실제 운전
- 영향 등급: 저하 — Lean이 받는 `sumTo_succ'` 같은 이름이 사전 검사·중앙 검사에서 거부됐다.
- 증상: 실제 Lean에서 통과한 작은 정리가 선언명 검사에서 거부됐다.
- 근본 원인: `formal._ident`가 알파벳·숫자·밑줄만 허용했다.
- 수정: 98ac7e5. 회귀 시험 `test_formal.py`의 `test_prime_names_keep_the_existing_identifier_boundary`, `test_actual_prime_declarations_have_signatures_and_axioms`.
- 결함 유형: 검사
- 트리거: 실제 모델 출력 형태(관용적 Lean 이름)
- 결함 위치 층: L1 원시
- 시험 유출 원인: 합성 입력이 실제와 다름 — 시험의 선언명이 모두 단순 식별자였다(추론).
- 검증런 유출: 해당 없음
- 가장 싼 포착 시험: `_ident`에 `foo'`, `N.foo''`, `α_1`을 넣어 허용, `'`, `a b`, `a;b`를 넣어 거부를 단언하는 표 시험.
- 범주 후보: 외부 도구 문법 가정

### A-30 독립 운영의 코드 수리가 검증·커밋 경계 없이 남음

- 출처: `docs/do-math/review-2026-09-18/plan.md` P10, `research/.../analysis.md` 148행, `기억/layer1/M-0320.md` 「검증」 셋째 항목; 수정 커밋 98ac7e5(`계약/독립-운영.md`)
- 발견 경위: 실제 운전
- 영향 등급: 저하 — 14:02 운영 담당의 수리 8개 파일(정본·사본 각 4)이 미커밋으로 남아 실행 중인 설치본이 커밋 판본과 달랐다. 9/19에는 운영 담당의 수리가 전체 회귀 도중 HOLD로 끊겨 미커밋으로 남았고 사용자 세션이 패치를 커밋했다. 운영 보고의 원인 집계(32건)도 판본 대조(26/6/3)와 달랐다.
- 증상: 수리된 코드가 어느 판본으로 검증·배포됐는지 원장에 결박되지 않았다.
- 근본 원인: 독립 운영 계약이 기술 수리의 종료 조건(재현, 동기화, 검증 설치본, 커밋 또는 미완료 소유)을 정하지 않았다.
- 수정: 98ac7e5에서 `계약/독립-운영.md`의 수리·반환 절 보완. 회귀 시험 없음.
- 결함 유형: 문서·계약
- 트리거: 사용자·운영 제어(HOLD가 수리 중 운영 실행을 끊음), 기타(운영 AI의 코드 수리)
- 결함 위치 층: 계약·스키마
- 시험 유출 원인: 시험 없음
- 검증런 유출: 해당 없음
- 가장 싼 포착 시험: 실행기 시작 시 설치 manifest 해시와 저장소 HEAD의 스킬 해시를 비교해 불일치를 보고하는 검사, 그리고 운영 보고 스키마에 수리 판본·커밋 필드가 필수인지 단언하는 스키마 시험.
- 범주 후보: 운영 수리의 판본 관리

### A-31 준비 직후 무조건 계획을 열어 빈 계획이 반복

- 출처: `docs/do-math/review-2026-09-18/plan.md` P06(무선택 계획 8건), `기억/layer1/M-0321.md` 「발동 횟수의 원인」 연구 계획 21회; 수정 커밋 9d81400
- 발견 경위: 실제 운전(기록 분석)
- 영향 등급: 저하 — 9/19 운전의 계획 21회 중 빈 계획 6회는 모두 준비 수락 직후 열렸다. 실행 중 도착한 승인이 별도 계획을 만든 쌍이 4개였다.
- 증상: 준비 직후에는 새 계약이 검토를 받지 않아 고를 과제가 없었다.
- 근본 원인: 준비 수락이 조건 없이 계획을 열었고, `_enqueue`는 미시작 요청에만 병합했다.
- 수정: 9d81400에서 착수 가능·판정 대기 과제가 없고 계약 검토가 대기 중이면 건너뜀, 계획 정착 대기(`plan_settle_seconds`). 회귀 시험 `test_run_feedback.py`의 `test_new_contracts_awaiting_review_do_not_open_a_plan_with_nothing_to_decide`, `test_preparation_still_opens_a_plan_when_a_ready_task_awaits_a_decision`, `test_a_plan_waits_for_pending_contract_reviews_so_nearby_approvals_share_one_decision`, `test_the_settle_wait_ends_at_its_configured_limit`.
- 결함 유형: 알고리즘
- 트리거: 특정 전이 순서(준비 수락 → 계약 검토 대기)
- 결함 위치 층: L2 인터페이스 요소
- 시험 유출 원인: 단언 약함 — b134089의 `test_regular_empty_plan_can_still_dispatch`와 `test_initial_plan_uses_first_ready_task_without_waiting_for_other_reviews`는 빈 계획이 실행되는 동작을 정상으로 고정했다. 역할별 호출 수를 단언하는 시험이 없었다.
- 검증런 유출: 해당 없음
- 가장 싼 포착 시험: 대역 모델로 후보 3개를 내는 준비를 수락시킨 뒤 계약 검토가 끝날 때까지 돌리고, 연구 계획 호출이 1회임을 단언한다.
- 범주 후보: 판단 대상 없는 실행의 발동

### A-32 예약 조회가 null 다음 실행 시각에 메서드를 호출

- 출처: `기억/layer1/M-0317.md` 「연구 예약 조회의 null 다음 실행 시각」, `임시/parking-unimodality-analysis-20260916/분석.md` §7 표 셋째 행, `docs/do-math/개선-검증-2026-09-16/README.md` §7 행; 결함 도입 98ac7e5, 수정 커밋 d57c016
- 발견 경위: 실제 운전(새 인스턴스 초기화 전 `operator status`)
- 영향 등급: 저하(추론) — `operator status`가 실패했다. 같은 함수가 install·uninstall·start 뒤에도 실행되므로 초기화의 예약 확인도 실패로 보고된다. 예약 등록 자체가 실패했는지는 원자료가 말하지 않는다.
- 증상: trigger 없는 연구 예약의 `NextRunTime`이 null일 때 `ToUniversalTime()` 호출이 실패했다.
- 근본 원인: `operator_schedule.ps1` 31행. d03f7d9 판본은 `[string]$info.NextRunTime`으로 null을 빈 문자열로 처리했으나, 98ac7e5가 UTC 변환을 추가하며 null 분기를 빠뜨렸다. 9/16 분석이 같은 호출 오류를 운영 보조 명령에서 이미 관찰했고 9/16 개선에서 처리했던 경계다.
- 수정: d57c016 한 줄(null이면 null). 회귀 시험 없음(`test_operator*.py` 12건 재실행만).
- 결함 유형: 외부 경계
- 트리거: 실제 외부 도구 동작(Windows 작업 스케줄러가 trigger 없는 작업에 null 반환), 설정·환경
- 결함 위치 층: 경계 어댑터
- 시험 유출 원인: 대역이 가림 — d57c016 부모 판본의 `test_operator.py`는 예약 스크립트 호출을 `runner` 대역(`CompletedProcess(argv, 0, '{"operator":"ready"}')`)으로 바꿔 PowerShell이 실행되지 않았다. 9/16의 실제 재현은 회귀 시험으로 남지 않았다.
- 검증런 유출: 해당 없음
- 가장 싼 포착 시험: trigger 없이 `-Disable`로 등록한 임시 예약 작업에 대해 `operator_schedule.ps1`의 조회 함수를 실제 PowerShell로 실행하고, 종료 코드 0과 `next_run: null`을 단언한다.
- 범주 후보: 외부 CLI 실동작 가정

### A-33 미시작 개정 요청들이 서로를 기다리는 순환

- 출처: `기억/layer1/M-0318.md` 「맥락」「원인」「수리」; 수정 커밋 f675902
- 발견 경위: 실제 운전(독립 운영 실행이 운영 소유 질문을 받아 수리)
- 영향 등급: 저하 — 순환이 연구 계획 두 번을 소모했다. 둘째 계획이 과제 두 개를 철회하고 새 준비로 다시 열어 순환을 끊었다. 계획이 과제를 철회하지 않았다면 두 개정은 진행하지 못했다.
- 증상: 요청 A가 X를, B가 Y를 개정하고 X·Y가 서로를 읽으면 A는 B를, B는 A를 기다렸다. 계획의 결합 요청이 세 번째 참여자가 되어 순환을 키웠다.
- 근본 원인: `planning.revision_waits`가 선언된 개정 요청 자신에게도 "다른 미해소 개정의 대상을 읽으면 대기" 규칙을 적용했다. 설계 문서(`implementation-plan.md` 342행)는 순환을 "정상 대기로 숨기지 않는다 … 계획·준비에 재설계를 요청한다 … 기계가 임의로 간선을 지우지 않는다"로 정해, 교착을 예방하지 않고 계획에 넘겼다.
- 수정: f675902 미시작 개정은 자기보다 먼저 요청된 미시작 개정만 기다림. 회귀 시험 `test_decision_basis.py::test_unstarted_writers_reading_each_others_targets_drain_oldest_first`.
- 결함 유형: 알고리즘
- 트리거: 특정 전이 순서(서로 경계를 참조하는 과제 둘의 동시 개정 요청)
- 결함 위치 층: L2 인터페이스 요소
- 시험 유출 원인: 조합·순서 미탐색 — f675902 부모 판본의 순환 시험은 dependencies 순환 보고(`test_dependency_cycles_are_reported_with_the_actual_edges`)와 순환 없음 단언(`test_revision_obligations.py` 162행)뿐이었고, 미시작 개정 요청 둘이 서로의 대상을 읽는 경우가 없었다.
- 검증런 유출: 해당 없음(검증런 종료 뒤 도입된 코드)
- 가장 싼 포착 시험: 서로를 inputs로 가진 과제 A·B에 각각 개정 요청을 넣고 `planning.revision_cycles(...) == []`를 단언한다. 일반형은 "대기 그래프에 순환 없음" 속성 시험을 무작위 개정 요청 집합에 적용하는 것이다.
- 범주 후보: 대기 그래프 교착

### A-34 병합된 새 준비 요청이 개정 대상 은퇴와 함께 소실

- 출처: `기억/layer1/M-0318.md` 「병합된 새 준비 요청의 소실」; 수정 커밋 f675902
- 발견 경위: 실제 운전(snapshot 3d338c9 → f98ae1c 추적)
- 영향 등급: 저하 — 계획이 요청한 새 준비 요청 3건이 대기열에서 조용히 사라졌다. 운영 담당이 원문을 다시 열어 복구했다.
- 증상: 수락 뒤 대기열에 연구 계획 하나만 남았다.
- 근본 원인: `_enqueue`가 대상 없는 새 요청을 대기 중인 개정 요청에 병합했고, `_retire_closed_revision_targets`가 대상이 모두 닫힌 요청을 통째로 제거했다.
- 수정: f675902 `unbound_request` 표지. 회귀 시험 `test_revision_obligations.py::test_a_merged_new_request_survives_when_all_revision_targets_close`.
- 결함 유형: 기능
- 트리거: 특정 전이 순서(병합 → 같은 계획의 철회 → 은퇴)
- 결함 위치 층: L2 인터페이스 요소
- 시험 유출 원인: 조합·순서 미탐색 — 병합과 은퇴를 각각 시험했으나 둘의 조합은 없었다(부모 판본에 해당 시험 부재 확인).
- 검증런 유출: 해당 없음
- 가장 싼 포착 시험: 개정 요청과 대상 없는 요청을 병합한 뒤 대상 과제를 닫고 은퇴를 실행해, 대상 없는 요청의 이유가 대기열에 남음을 단언한다. 일반형은 "병합 전 요청 이유의 합집합 ⊆ 이후 대기열·이력" 보존 불변식이다.
- 범주 후보: 파생 상태의 전이 경계 정리 누락

### A-35 유지보수 역할이 확인할 개정 대기열 상태를 받지 못함

- 출처: `기억/layer1/M-0320.md`; 수정 커밋 65ee301
- 발견 경위: 실제 운전(독립 운영 실행)
- 영향 등급: 저하 — 유지보수 실행이 확인을 맡은 필드를 받지 못해 운영 소유 질문을 닫지 못하고 새 질문을 남겼다. 운영 소유 질문은 유지보수·운영 점검만 닫을 수 있어 해소 경로가 없었다.
- 증상: 유지보수 요청은 "`revision_cycles`가 비었는지 확인하라"고 지시했지만 입력에 그 필드가 없었다.
- 근본 원인: `engine._context`가 `pending_revisions`·`revision_cycles`·`blocked_actions`를 준비·계획에만 넣었다.
- 수정: 65ee301. 회귀 시험 `test_revision_obligations.py::test_maintenance_reads_the_revision_queue_it_is_asked_to_check`.
- 결함 유형: 인터페이스
- 트리거: 사용자·운영 제어(운영 담당이 연 유지보수 요청)
- 결함 위치 층: L2 인터페이스 요소
- 시험 유출 원인: 시험 없음 — 역할별 문맥과 역할 계약이 요구하는 입력의 대응을 검사하는 시험이 없었다.
- 검증런 유출: 해당 없음
- 가장 싼 포착 시험: 각 역할 계약이 이름으로 요구하는 입력 필드 목록(계약 문서에서 추출하거나 표로 선언)과 `_context(role)`의 키를 대조하는 표 시험.
- 범주 후보: 역할 입력 누락

### A-36 같은 계약의 검토를 실행 중에 중복 개설

- 출처: `기억/layer1/M-0321.md` 「발동 횟수의 원인」 계약 검토 18회, 「중복 검토」 항목; 수정 커밋 9d81400
- 발견 경위: 실제 운전(기록 분석)
- 영향 등급: 저하 — 같은 판본의 중복 검토 1회. 재현 중 기존 코드가 실행 중인 검토의 action까지 대기열에서 지우고 있었음이 드러났다.
- 증상: 검토가 도는 중 그 과제가 입력으로 읽는 형제 과제가 승인되자 검토 기준 키가 바뀌어 새 검토가 열렸다.
- 근본 원인: `lifecycle_engine._refresh_readiness`의 검토 개설 조건이 실행 중 검토를 보지 않았다(9d81400 diff 421행).
- 수정: 9d81400 `live_review` 조건. 회귀 시험 `test_run_feedback.py::test_a_running_review_of_the_same_contract_is_not_doubled_when_its_outside_premises_move`.
- 결함 유형: 검사
- 트리거: 동시성·경합(검토 실행 중 형제 과제 승인)
- 결함 위치 층: L2 인터페이스 요소
- 시험 유출 원인: 조합·순서 미탐색
- 검증런 유출: 해당 없음
- 가장 싼 포착 시험: B의 계약 검토 실행을 running으로 둔 상태에서 B가 읽는 A를 승인하고 `_refresh_readiness`를 호출해, B 대상 검토 요청이 새로 생기지 않고 실행 중 action이 유지됨을 단언한다.
- 범주 후보: 현재성 검사 범위

### A-37 작업 예산 AI 실행에 운영 호출 기한(600초)을 적용

- 출처: `임시/do-math_검증_2026-09-15/장부.md` R1-34(`engine.py` 1086행), `기억/layer1/M-0279.md`; 수정 커밋 b4ede4c
- 발견 경위: 검증런(9/15 1차)
- 영향 등급: 정지(추론) — 장부 요지: "긴 연구가 기한마다 인스턴스를 정지시킨다." 600초를 넘는 연구 수행은 끝날 수 없다.
- 증상: 운전 미발현
- 근본 원인: 작업 예산 AI 실행에도 운영 예산의 `call_timeout_seconds`를 적용했다.
- 수정: b4ede4c. 회귀 시험 `test_purpose_engine.py::test_work_budget_execution_is_not_bounded_by_operations_call_timeout`.
- 결함 유형: 대입·초기화
- 트리거: 시간 경과·기한, 장시간 누적(긴 연구)
- 결함 위치 층: L3 배선
- 시험 유출 원인: 시험 없음 — b4ede4c 부모 판본 시험에 `call_timeout`을 다루는 곳이 없었다(git grep 확인).
- 검증런 유출: 검증런이 찾아 적용했다.
- 가장 싼 포착 시험: `call_timeout_seconds=1`로 역할별 runner 호출의 timeout 인자를 기록하고, 작업 역할은 1보다 크고 운영 역할은 1 이하임을 단언한다(추가된 시험 그대로).
- 범주 후보: 기한·시간 경계

### A-38 목표 변경이 무관한 기계·검토 action을 대기열에서 삭제

- 출처: `임시/do-math_검증_2026-09-15/장부.md` R1-42(`governance.py` 118행); 수정 커밋 b4ede4c
- 발견 경위: 검증런(9/15 1차)
- 영향 등급: 정지(추론) — 장부 요지: "신뢰 전환과 동일성 검토가 영구히 멈춘다."
- 증상: 운전 미발현
- 근본 원인: 목표 변경 결정이 대기열 전체를 비우고 준비 요청만 넣었다.
- 수정: b4ede4c. 회귀 시험 `test_governance.py::test_goal_change_keeps_goal_independent_queue_actions`.
- 결함 유형: 기능
- 트리거: 사용자·운영 제어(목표 변경), 특정 전이 순서
- 결함 위치 층: L2 인터페이스 요소
- 시험 유출 원인: 출발 상태가 경로를 건너뜀 — 부모 판본 `test_governance.py::test_goal_policy_and_idempotence`의 setUp은 `queue: []`여서 대기열 삭제 경로가 비교 대상 없이 지나갔다.
- 검증런 유출: 검증런이 찾아 적용했다.
- 가장 싼 포착 시험: 대기열에 trust_check·identity_review·intent_interpretation·research_work를 둔 상태에서 목표 변경을 적용하고, 앞의 세 역할이 남음을 단언한다(추가된 시험 그대로).
- 범주 후보: 파생 상태의 전이 경계 정리 누락

### A-39 지식 개정이 진행 중 동일성 검토를 닫지 않아 매 run 같은 예외

- 출처: `임시/do-math_검증_2026-09-15/장부.md` R1-48(`engine.py` 1252~1258행); 수정 커밋 b4ede4c
- 발견 경위: 검증런(9/15 1차)
- 영향 등급: 정지(추론) — 장부 요지: "실행기가 매 run 같은 예외로 멈춘다."
- 증상: 운전 미발현
- 근본 원인: 연구 수행의 지식 개정 적용이 그 지식의 진행 중 동일성 검토 cycle을 닫지 않아, 이후 검토 처리에서 예외가 반복됐다(요지에서 추론).
- 수정: b4ede4c. 전용 회귀 시험 이름은 diff에서 특정하지 못했다.
- 결함 유형: 기능
- 트리거: 특정 전이 순서(동일성 검토 진행 중 → 같은 지식의 개정)
- 결함 위치 층: L2 인터페이스 요소
- 시험 유출 원인: 확인 불가 — 장부 상세가 삭제되어 예외 지점과 당시 시험의 대응을 특정할 수 없었다.
- 검증런 유출: 검증런이 찾아 적용했다.
- 가장 싼 포착 시험: 지식 K의 동일성 검토 cycle을 working으로 둔 채 K를 개정하는 연구 결과를 적용하고, run을 두 번 돌려 예외 없이 cycle이 미해결로 닫힘을 단언한다.
- 범주 후보: 예외 전파

### A-40 연구 수행 실패 뒤 운영 점검 revise로 과제가 performing에 고착

- 출처: `임시/do-math_검증_2026-09-15/장부.md` R1-53(`engine.py` 1512~1516행, 병합 R1-M10에 R1-52 포함); 수정 커밋 b4ede4c
- 발견 경위: 검증런(9/15 1차)
- 영향 등급: 정지(추론) — 장부 요지: "과제가 performing에 남아 개정도 재배정도 할 수 없다." 과제 수준의 영구 정지다.
- 증상: 운전 미발현
- 근본 원인: 운영 점검의 revise 처분이 과제 상태를 performing에서 개정 가능한 상태로 옮기지 않았다(요지에서 추론).
- 수정: b4ede4c. 전용 회귀 시험 이름은 diff에서 특정하지 못했다.
- 결함 유형: 기능
- 트리거: 특정 전이 순서(수행 실패 → 운영 점검 revise)
- 결함 위치 층: L2 인터페이스 요소
- 시험 유출 원인: 시험 없음 — b4ede4c 부모 판본 시험의 `revise`는 모두 지식 개정 제어였고 운영 점검 처분의 revise는 없었다(git grep 확인).
- 검증런 유출: 검증런이 찾아 적용했다.
- 가장 싼 포착 시험: 대역 수행을 실패시키고 운영 점검이 `revise`를 반환하게 한 뒤, 과제가 `needs_revision`이고 후보 준비 요청이 대기열에 있음을 단언한다.
- 범주 후보: 대기·요청의 소비자 부재

### A-41 계약 검토 반려가 후보 준비로 반환되지 않음

- 출처: `임시/do-math_검증_2026-09-15/장부.md` R1-54(`engine.py` 1390행); 수정 커밋 b4ede4c
- 발견 경위: 검증런(9/15 1차)
- 영향 등급: 정지(추론) — 반려된 과제를 고칠 주체가 호출되지 않으면 과제는 승인될 수 없다.
- 증상: 운전 미발현
- 근본 원인: `revision_required`·`unresolved` 판정이 후보 준비 요청을 만들지 않았다.
- 수정: b4ede4c. 전용 회귀 시험 이름은 diff에서 특정하지 못했다.
- 결함 유형: 기능
- 트리거: 실제 모델 출력 형태(검토 반려)
- 결함 위치 층: L2 인터페이스 요소
- 시험 유출 원인: 시험 없음 — b4ede4c 부모 판본 시험에 `revision_required`가 한 번도 나오지 않았다(git grep 확인). 모든 대역 검토가 승인만 반환했다.
- 검증런 유출: 검증런이 찾아 적용했다.
- 가장 싼 포착 시험: 대역 계약 검토가 `revision_required`를 반환하게 하고, 다음 대기열에 그 과제를 대상으로 한 후보 준비 요청이 있음을 단언한다. 일반형은 "각 판정값마다 후속 소유자가 존재" 표 시험이다.
- 범주 후보: 대기·요청의 소비자 부재

### A-42 작업 예산 소진 요청이 운영 예산 사용까지 막음

- 출처: `임시/do-math_codex-full_검증_2026-09-15/장부.md` R1-12(`engine.py` 544행), `임시/do-math_검증_2026-09-15/장부.md` R1-M4(R1-10·R1-45); 수정 커밋 edfafaf
- 발견 경위: 검증런(9/15 codex-full 1라운드)
- 영향 등급: 정지(추론) — 대기열 머리의 작업 요청 하나가 운영 예산의 계획·진단까지 막아 인스턴스가 `budget_exhausted`로 멈춘다. 당시 기본 예산은 유한(40·30)이었다.
- 증상: 운전 미발현
- 근본 원인: 배정 루프가 첫 요청의 예산 소진에서 전체 실행을 멈췄다.
- 수정: edfafaf. `test_engine.py`의 기존 시험을 운영 예산으로 계획이 실행됨을 단언하도록 바꿨다.
- 결함 유형: 알고리즘
- 트리거: 장시간 누적(예산 소진), 특정 전이 순서
- 결함 위치 층: L3 배선
- 시험 유출 원인: 단언 약함 — edfafaf 부모 판본의 `test_engine.py` 시험이 `work_calls=1`에서 `status == "budget_exhausted"`를 단언해 결함 동작을 기대값으로 고정했다(diff의 삭제 줄).
- 검증런 유출: 9/15 1차 검증런이 R1-10·R1-45로 먼저 찾았으나 병합 수리안이 예산별 보고 손상까지 해소하지 못한다는 이유로 1/3 기각됐다. 다음 검증런에서 적용됐다.
- 가장 싼 포착 시험: `work_calls=1, operations_calls=10`에서 작업 예산을 소진시킨 뒤 계획 요청을 넣고, 계획이 실행되고 작업 요청은 대기열에 남음을 단언한다.
- 범주 후보: 대기 그래프 교착

### A-43 설정·계약 개정 뒤에도 대기 행동이 옛 모델 배정을 유지

- 출처: `임시/do-math_전면대조_20260917/장부.md` R1-07·R1-08·R1-12, `기억/layer1/M-0300.md` 「수리한 실행과 인계 경계」 첫 단락; 수정 커밋 f341b26
- 발견 경위: 검증런(9/17 전면대조)
- 영향 등급: 정지(추론) — M-0300 원문: "재개 뒤 옛 모델을 쓰거나 존재하지 않는 모델 슬롯을 계속 기다릴 수 있었다." 후자는 풀리지 않는 대기다.
- 증상: 운전 미발현
- 근본 원인: 모델 대응·역할 하한 변경 때 큐의 요청만 갱신하고 보류 행동의 저장된 배정은 남겼다. 계약 개정 때도 대기 계약 검토의 해시만 바꾸고 이전 평가로 고른 모델을 유지했다.
- 수정: f341b26 두 경계에서 미시작 요청의 배정 삭제·재선택. 커밋 diff에 새 시험 메서드는 없고 `test_session_scheduler.py`가 수정됐다. 런의 집중 검사는 커밋되지 않았다.
- 결함 유형: 대입·초기화
- 트리거: 설정·환경(configure), 재시작·복구·재개
- 결함 위치 층: L2 인터페이스 요소
- 시험 유출 원인: 시험 없음 — 설정 변경 뒤 보류 행동의 배정을 단언하는 시험이 없었다(추론, 부모 판본 개별 대조 미수행).
- 검증런 유출: 검증런이 찾아 적용했다.
- 가장 싼 포착 시험: 모델 A 배정의 보류 행동을 둔 채 `tier_models`를 B로 바꾸고 resume한 뒤, 배정 요청의 모델이 B이고 A 슬롯 대기가 없음을 단언한다.
- 범주 후보: 파생 상태의 전이 경계 정리 누락

### A-44 학술 과제의 평가 반려 뒤 수리 경로 부재

- 출처: `임시/do-math_전면대조_20260917/장부.md` R1-01·R1-13·R1-15, `기억/layer1/M-0300.md` 「기각과 남은 두 문제」, `기억/layer1/M-0301.md`; 수정 커밋 120dde6
- 발견 경위: 검증런(9/17 전면대조), 수리는 사용자 지시에 따른 직접 수리
- 영향 등급: 정지(추론) — 장부 요지: "평가나 계약을 고칠 주체가 없어 과제가 멈춘다", "과제가 needs_revision에 고정된다." 사용자 학술 요구 과제가 멈추면 연구의 학술 완료도 멈춘다.
- 증상: 운전 미발현
- 근본 원인: 학술 과제는 일반 후보 개정이 금지돼 있었고, 평가만 다시 쓰는 `assessment_targets` 경로가 반려 이후에는 연결되지 않았다.
- 수정: 120dde6. 회귀 시험 `test_model_assessment_flow.py`의 `test_rejected_rating_is_preserved_and_replaced_by_assessment_only_request`, `test_repaired_and_unchanged_ratings_both_receive_fresh_independent_review`, `test_preexisting_rejection_enters_repair_on_refresh`, `test_repair_deferral_preserves_obligation_until_resume`, `test_late_repair_cannot_overwrite_a_changed_user_contract`.
- 결함 유형: 기능
- 트리거: 실제 모델 출력 형태(검토의 평가 반려)
- 결함 위치 층: L2 인터페이스 요소
- 시험 유출 원인: 시험 없음 — 평가 반려를 다루는 시험이 120dde6에서 처음 추가됐다.
- 검증런 유출: 검증런이 세 수리자에게서 찾았으나 수리안이 사용자 선택으로 상신되어 기각됐다. 사용자가 잔여 결함으로 직접 수리를 지시했다.
- 가장 싼 포착 시험: 학술 과제의 계약 검토가 `revision_required`를 반환하게 하고, 다음 대기열에 평가 전용 후보 준비 요청이 있고 과제 계약은 바뀌지 않음을 단언한다.
- 범주 후보: 대기·요청의 소비자 부재

### A-45 (v5) Lean 검사 중 pause 뒤 resume으로 검사가 재개되지 않음

- 출처: `docs/do-math/review-evidence/2026-09-23-static/report.md` 1번, `docs/do-math/정적-워크스루-연결결함-수리안-2026-09-23.md` F1; 수정 커밋 7d2597e(`docs/do-math/정적-워크스루-연결결함-수리결과-2026-09-23.json`)
- 발견 경위: 정적 검토
- 영향 등급: 정지(추론) — 보고서 원문: "같은 허가·신뢰 환경이 유지돼도 해당 결과의 형식 검사는 대기 상태에 남습니다." 형식 검사 의무가 사람 개입 없이 이어지지 않는다(의무 수준).
- 증상: 운전 미발현
- 근본 원인: `_formal_steps`가 stopped 결과를 `formal_stopped` 대기로 옮기고 action을 지웠는데, `resume` 경로와 다른 어떤 소비자도 그 대기를 재배정하지 않았다.
- 수정: 7d2597e. 회귀 시험은 `test_connection_repairs.py` 등(수리 결과 JSON의 변경 파일 목록).
- 결함 유형: 기능
- 트리거: 사용자·운영 제어, 재시작·복구·재개
- 결함 위치 층: L2 인터페이스 요소
- 시험 유출 원인: 확인 불가 — 수정 전 v5 판본은 커밋되지 않았고 보존 사본에 시험 파일이 없다.
- 검증런 유출: 해당 없음(정적 검토가 발견)
- 가장 싼 포착 시험: 형식 검사 실행 중 pause → 종료 회수 → resume 순서를 대역 Lean으로 재생하고, 새 형식 검사 실행이 배정됨을 단언한다. 일반형은 "모든 `waiting_actions.kind`에 대해 이를 소비하는 전이가 코드에 존재" 정적 표 검사다.
- 범주 후보: 대기·요청의 소비자 부재

### A-46 (v5) 동일성 검토 실행 한도 소진이 처리되지 않는 대기로 남음

- 출처: `docs/do-math/review-evidence/2026-09-23-static/report.md` 2번, `정적-워크스루-연결결함-수리안-2026-09-23.md` F2; 수정 커밋 7d2597e
- 발견 경위: 정적 검토
- 영향 등급: 정지(추론) — 보고서 원문: "검토 cycle은 working으로 남고, overflow_disposition을 읽어 … 닫거나 재구성 계획을 여는 소비자가 없습니다." 초기 자리 둘에 한도 1을 반환하면 바로 이 상태가 된다.
- 증상: 운전 미발현
- 근본 원인: 범위 계획 검사가 필요한 실행 몫 하한을 검사하지 않았고, `review_budget_exhausted` 대기(`next_owner="review_policy"`)를 소비하는 코드가 없었다.
- 수정: 7d2597e.
- 결함 유형: 기능
- 트리거: 실제 모델 출력 형태(범위 계획의 한도 값), 장시간 누적
- 결함 위치 층: L2 인터페이스 요소
- 시험 유출 원인: 확인 불가 — 위와 같은 이유.
- 검증런 유출: 해당 없음
- 가장 싼 포착 시험: 범위 계획이 자리 2·한도 1을 반환하게 하고 수신에서 거부됨을, 한도를 실행 도중 소진시키면 cycle이 unresolved로 닫히고 계획 요청이 생김을 단언한다.
- 범주 후보: 대기·요청의 소비자 부재

### A-47 (v5) 검토 제안의 입력 초과를 사용자 대기로 보냄

- 출처: `docs/do-math/review-evidence/2026-09-23-static/report.md` 3번, `정적-워크스루-연결결함-수리안-2026-09-23.md` F3; 수정 커밋 7d2597e
- 발견 경위: 정적 검토
- 영향 등급: 정지(추론) — 보고서 원문: "동일성 검토의 실제 `resolution_question.next_owner`는 항상 `user`가 됩니다." 사용자 결정 없이 풀리지 않는 차단 질문이 생긴다.
- 증상: 운전 미발현
- 근본 원인: 입력 생성기가 `suggested_disposition="unresolved_to_review_plan"`을 계산했지만 대체 분기가 `research_work`에만 있었다.
- 수정: 7d2597e.
- 결함 유형: 기능
- 트리거: 장시간 누적(입력 크기)
- 결함 위치 층: L2 인터페이스 요소
- 시험 유출 원인: 확인 불가 — 위와 같은 이유.
- 검증런 유출: 해당 없음. 9/15 astra-low 검증런 R1-07("공통 문서만으로 한도를 넘는 동일성 검토를 제안 재구성에 잘못 보낸다")은 반대 방향의 오배정을 고쳤다.
- 가장 싼 포착 시험: 제안 본문만 한도를 넘는 동일성 검토 입력을 만들고, 사용자 질문이 생기지 않으며 계획 입력의 `review_followups`에 측정값이 들어감을 단언한다.
- 범주 후보: 대기·요청의 소비자 부재

### A-48 (v5) 검토 입력 복원 유예 중 예외가 스케줄러 전체로 번짐

- 출처: `docs/do-math/정적-워크스루-후속-수리안-2026-09-23.md` 2절, `정적-워크스루-수리결과-2026-09-23.md` 표 2행; 수정 커밋 7d2597e
- 발견 경위: 정적 검토
- 영향 등급: 정지(추론) — 원문: "`_discard_prepared_input()`에 도달하지 못하고 전체 스케줄러의 오류 처리로 번진다." 실행기 비정상 종료에 해당한다.
- 증상: 운전 미발현
- 근본 원인: `_call_steps`가 `ReviewPreparationDeferred`를 받으면 아직 미종료인 실행이 있는데 `activities.wait_for()`를 호출했고, 이 함수는 배정 실행이 모두 ended일 때만 허용해 예외를 냈다.
- 수정: 7d2597e(복구 의무 기록 후 준비 실행 종료, 뒤에 활동 정산).
- 결함 유형: 타이밍·직렬화
- 트리거: 특정 전이 순서(검토 입력 파일 읽기 실패·해시 불일치)
- 결함 위치 층: L3 배선
- 시험 유출 원인: 확인 불가 — 위와 같은 이유.
- 검증런 유출: 해당 없음
- 가장 싼 포착 시험: 공개 실행 경로에서 검토 입력 파일의 해시를 어긋나게 만들고 run 한 번이 예외 없이 끝나며 다른 실행이 계속됨을 단언한다.
- 범주 후보: 예외 전파

### A-49 (v5) 반복 문턱 뒤 재개 경로가 끊김

- 출처: `docs/do-math/정적-워크스루-후속-수리안-2026-09-23.md` 3절, `정적-워크스루-수리결과-2026-09-23.md` 표 3행과 「계속 승인과 복구의 연결」; 수정 커밋 7d2597e
- 발견 경위: 정적 검토
- 영향 등급: 정지(추론) — 원문: `authorize_repetition_repair()`가 호출되지 않고, 허용 함수가 원 action ID의 과거 실행이 있으면 거부하며, 공개 결정 적용기가 `repetition_continue`를 지원하지 않았다. 반복 한도 보류(`repetition_hold`)에 걸린 의무를 운영 처분도 사용자 결정도 풀 수 없다.
- 증상: 운전 미발현
- 근본 원인: 생산자(허용 기록)와 소비자(문턱 검사), 공개 결정 경로가 서로 연결되지 않았다.
- 수정: 7d2597e(`repetition_continue` 결정 연결, 호출되지 않던 `authorize_repetition_repair()` 제거).
- 결함 유형: 인터페이스
- 트리거: 장시간 누적(반복 횟수), 사용자·운영 제어
- 결함 위치 층: L2 인터페이스 요소
- 시험 유출 원인: 확인 불가 — 위와 같은 이유. 후속 수리안은 "테스트가 만들어 넣은 허용 영수증이나 대체한 호출부만으로 연결 완료를 주장하지 않는다"를 공통 조건으로 두었는데, 이는 당시 시험이 대역 영수증을 썼을 가능성을 시사한다(추론).
- 검증런 유출: 해당 없음
- 가장 싼 포착 시험: 실제 계약 개정 반려를 문턱 횟수만큼 반복해 `repetition_hold`를 만들고, 공개 `decision repetition_continue`를 적용해 후속 실행이 정확히 하나 배정됨을 단언한다.
- 범주 후보: 대기·요청의 소비자 부재

## 4. 관찰

### 4.1 기록에서 확인되는 사실

1. **이 기간의 정지 결함 규모.** 실제 운전(구현 중 실운전 포함)에서 관측된 정지 결함은 9건이다(A-01·02·07·08·09·12·13·20·21). 검증런과 정적 검토가 찾은 정지급 결함은 15건이다(A-14·15·37~49). 사용자가 관찰한 "정지 결함 20~30개"는 전체 기간을 대상으로 한 것이므로 이 기간만으로 확인할 수 없다. 이 기간의 관측 정지 9건 가운데 5건(A-12·13·20·21, A-01)은 공급자 CLI·Windows·Python 실행 환경과의 경계에서 났다.
2. **검증런이 찾았지만 기각되어 운전으로 새어 나간 사례가 있다.** 완료 기준 합집합(A-07)은 9/15 검증런 R1-65가 정확히 지적했지만, 수리 조각이 아닌 상신으로 제출되어 기각됐다. 다음 날 실제 운전에서 세 과제를 정지시켰다. 무변경 커밋(A-18)도 9/16 R1-05가 찾았으나 수리안의 부작용 때문에 기각됐고, 다음 날 운전에서 관찰됐다. 작업 예산 소진의 전체 정지(A-42)는 9/15 1차에서 기각되고 codex-full에서 적용됐다. 장부 처분은 수리안의 품질을 판정했으며, 결함 존재가 반박되지 않은 항목도 후속 추적 없이 닫혔다.
3. **시험이 결함 동작을 기대값으로 고정한 사례가 네 건 있다.** Claude 파서 시험이 `INIT, RESULT, RESULT`를 거부해야 한다고 단언했다(A-23). 관찰 시험이 기본 모드의 interval 점검을 단언했다(A-27). 엔진 시험이 작업 예산 소진 뒤 `budget_exhausted`를 단언했다(A-42). adapter 시험이 `--ignore-user-config`만 단언했다(A-11). 9/15 검증런 R2-09도 "시험 다섯 곳이 그 동작을 기대값으로 고정함"을 지적했다. 이 경우 시험은 결함을 드러내지 못했을 뿐 아니라, 수리를 회귀 실패로 보이게 만든다.
4. **대역·합성 입력이 실제 형태와 달랐다.** 외부 CLI의 사건 순서(A-20), 역할 스키마(A-21), 다중 결과 구간(A-23), 모델 영수증의 bytes(A-13), 실제 설정 파일의 추가 키(A-14), 같은 제목이면 같은 기준을 만드는 후보 도우미(A-07), 예약 스크립트 대역(A-32)이 있다. 이 가운데 A-20·21·23은 실제 CLI 출력 한 번을 골든 픽스처로 녹화했다면 잡을 수 있었다. A-21은 노드 원문이 이를 직접 인정한다.
5. **전이 조합에서만 활성화되는 결함이 많다.** readiness 투영(A-08), 수리 소진 뒤 재개(A-09), 병합 뒤 은퇴(A-34), 미시작 개정의 상호 대기(A-33), pause 뒤 실패 종료(A-06), 실행 중 검토의 중복(A-36)이 여기에 든다. 각 단계는 시험됐지만 순서가 시험되지 않았다.
6. **대기 상태를 만들고 소비자를 두지 않은 결함이 반복된다.** 보충 조사 요청(A-02), 공급자 한도(A-24), 운영 점검 revise(A-40), 계약 반려(A-41), 학술 평가 반려(A-44), `formal_stopped`(A-45), `review_policy`(A-46), 사용자 대기로 잘못 보낸 초과(A-47), 반복 보류(A-49)가 그렇다. 9/18 충분성 검토는 가상 `provider_limit` 종류가 기존 해소 함수에서 남는 것을 대역 실험으로 확인해 이 기제를 미리 지적했다(`sufficiency-review.md` 3절).
7. **실제 재현으로만 확인한 경계가 회귀로 남지 않아 다시 깨졌다.** 예약 작업의 null 다음 실행 시각은 9/16 개선에서 "실제 시험에서 재현해 처리"됐으나 회귀 시험으로 남지 않았고, 9/19 판본에서 UTC 변환을 추가하며 다시 깨졌다(A-32).
8. **설계 문서가 교착을 명시적으로 허용했다.** implementation-plan 342행은 개정 대기의 순환을 예방하지 않고 계획에 재설계를 요청하도록 정했다. 실제 운전에서 이 순환은 계획이 과제 둘을 철회하는 것으로만 풀렸다(A-33).

### 4.2 기록에서 추론한 것

1. **가장 싼 포착 수단이 반복된다.** 개별 기록의 "가장 싼 포착 시험"은 대체로 네 가지로 모인다. 실제 외부 출력의 골든 픽스처(A-13·14·20·21·23·29), 한 번의 실제 CLI·OS 스모크(A-01·11·16·22·32), 전이 뒤 불변식 검사(A-08·33·34·43·45; "readiness 키 ⊆ 스케줄 가능 과제", "대기 그래프 무순환", "병합된 이유 보존", "모든 대기 종류에 소비자 존재"), 역할별 호출 수 단언(A-17·18·27·31)이다.
2. **사용자의 두 번째 관찰은 이 기간에서 부분적으로 지지된다.** A-07·A-18·A-42는 검증런이 이미 찾았다. A-20·A-21·A-32는 실제 출력이나 실제 스크립트 한 번으로 잡을 수 있었다. 반면 A-24(공급자 한도)나 A-25(병합 실행의 현재성)는 실제 장시간 병렬 운전 전에는 발생 조건 자체가 드물었다.
3. **범주가 넘나든다.** 병렬 배정(9/16) 도입이 현재성 과잉 검사(A-25)와 중복 검토(A-36)를 자주 활성화했고, 효율 수리(98ac7e5)가 관찰 타이머(A-27)와 ps1 회귀(A-32)를 새로 들여왔다. 한 수리가 다른 범주의 결함을 도입하는 경로도 시험 설계에서 다뤄야 할 것으로 보인다.

### 4.3 서식의 분류 값으로 담기지 않은 사항

1. **"기대값이 결함을 고정" 유출 원인이 없다.** 4.1의 3번 사례는 경로가 실행됐고 단언도 강했지만 기대값 자체가 틀렸다. 가장 가까운 `단언 약함`을 골랐다(A-11·23·27·31·42). 오라클 오류(oracle error)를 별도 값으로 두는 것이 집계에 유리해 보인다.
2. **개발 중 첫 실운전에서 발견된 결함의 "시험 유출"이 모호하다.** A-02~05·12~14·20은 코드가 같은 커밋 또는 미커밋 상태에서 처음 작성되던 중 실운전으로 발견됐다. "수정 전 시점의 시험"이 존재하지 않아 `시험 없음`으로 적었으나, 출시 뒤 유출과 출시 전 포착을 구별하는 항목이 있으면 좋겠다.
3. **검증런·정적 검토가 찾은 정지급 결함의 영향 등급.** 3절의 `잠재`는 "운전에서 발현되지 않았고 발현 조건이 드물거나 아직 도달하지 않았다"여서, 운전 미발현이지만 발현 시 정지하는 결함과 겹친다. 이 파일은 발현 조건이 일반 운전에서 도달 가능하면 `정지(추론)`, 드물면 `잠재`로 적었다. 그 결과 잠재 0건이다.
4. **"사람의 개입" 기준.** 독립 운영 AI가 스킬 코드를 고쳐 푼 정지(A-08)와 운영 AI의 판단만으로 풀린 대기(A-24)를 구별했다. 전자는 정상 운전 경로 밖의 코드 수정이므로 정지로, 후자는 저하로 적었다. 서식이 운영 AI의 개입을 어떻게 셀지 정하면 일관성이 높아진다.
5. **"결함 위치 층"에 오라클·계약 설계가 섞인 경우.** A-33은 코드(L2)와 설계 문서의 순환 처리 규정이 함께 원인이다. 층을 하나만 고르게 되어 있어 L2로 적고 근본 원인에 설계 문서를 적었다.
6. **범위 경계.** 8694693·4b156be는 이 기간(M-0331과 M-0332 사이)에 있으나 기억 노드가 지목하지 않아 분석하지 않았다. 다른 담당 기간과 겹치는지 집계자가 확인할 필요가 있다.
