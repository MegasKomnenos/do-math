# 결함 기록 C: M-0348~M-0357 (2026-09-26~09-28)

이 문서는 `결함-기록-서식.md`에 따라 담당 C 기간의 결함을 기록한다. 이 기간에는 세 경량화(8d2ffd0, 379a171, 9b434f4)와 전면 정리(85a540c)가 있었다. 그 뒤로 검증런 넷(경량화 안정화 검증 bdccee3, 전면 검증 2차 8af1f5e, 3차 1라운드 1a8ce7a, 3차 2라운드 3552607)이 돌았고, 그 사이에 실제 모델로 시험 인스턴스 `RI-01M3HM0X`를 운전한 뒤 해석하고 수리했다(5ecc321).

영향 등급은 결함이 발동했을 때의 결과로 매겼다. 운전에서 발현되지 않은 결함도 발동하면 연구가 사람 개입 없이 멈추면 `정지`로 적었다. 이렇게 판정한 이유는 4절 관찰 7에 있다.

## 1. 읽은 범위

**기억 노드(전문).** `C:\math\기억\layer1\M-0348.md`부터 `M-0357.md`까지 10개를 모두 읽었다.

**검증런 문서.**

| 경로 | 범위 |
|---|---|
| `C:\math\임시\do-math_검증_20260927\장부.md` | 전문 |
| `C:\math\임시\do-math_검증_20260927\종료보고.md` | 전문 |
| `C:\math\임시\do-math_검증_20260927\동결.md` | 255~835행(목적 진술, 불변식, 영역 배분, 관점 필수 독해). 1~254행 산출물 목록은 제목만 확인했다 |
| `C:\math\임시\do-math_검증_20260927\기각보관\do-math-20260927-라운드1.md` | R1-28 절 전문. 나머지는 제목만 확인했다 |
| `C:\math\임시\do-math_검증_20260927-2\장부.md` | 전문 |
| `C:\math\임시\do-math_검증_20260927-2\종료보고.md` | 전문 |
| `C:\math\임시\do-math_검증_20260927-2\동결.md` | 259~408행(목적 진술~불변식). 영역 배분은 절 제목과 직전 런 배분을 옮겼다는 장부 기록으로 확인했다 |
| `C:\math\임시\do-math_검증_20260927-2\기각보관\do-math-20260927-2-라운드1.md` | 항목 제목만 확인했다 |
| `C:\math\임시\do-math_검증_20260928\장부.md` | 1~68행(신호·운영 기록·라운드 1 머리)과 두 라운드 본표 전 행 |
| `C:\math\임시\do-math_검증_20260928\종료보고.md` | 전문 |
| `C:\math\임시\do-math_검증_20260928\기각보관\do-math-20260928-라운드1.md` | R1-08 절의 원문·위치·영향·판정·근거 |
| `C:\math\임시\do-math_검증_20260928\기각보관\do-math-20260928-라운드2.md` | R2-07, R2-24, R2-M2 절의 원문·영향·근거 |

**전면 정리(M-0351) 자료.**

- `C:\math\임시\do-math-정리-검토-2026-09-27\보고서.md`: 64~112행(3절)
- `C:\math\임시\do-math-정리-검토-2026-09-27\검증\통합표.md`: ENG-01~22와 REV-01, RES-02·05·06·11·13, HIS-19 행
- `C:\math\임시\do-math-정리-구현-2026-09-27\결과-ENG.md`: grep한 행(25~39, 96, 110, 131~158)
- `C:\math\임시\do-math-정리-구현-2026-09-27\결과-병합IO.md`: 85~129행
- `C:\math\임시\do-math-정리-구현-2026-09-27\결과-IO.md`: grep한 행

**시험 인스턴스 자료.**

- `C:\math\임시\do-math_RI-01M3HM0X_해석\원고.md`: 전문
- `C:\math\임시\do-math_개선안_20260928\원고.md`: 전문
- `C:\math\.skill-workspace\nat-add-zero-20260927-01\` (읽기만 했다):
  - `config.json`과 폴더 목록
  - 저장소 `repo`의 ref `refs/heads/do-math/RI-01M3HM0XCF7D8N3M2QXABCEZ20`: 최종 커밋 `b1894a4`, 커밋 529개. 최종 커밋에서 `runtime/waiting_actions/state.json`과 `runtime/input_overflows/state.json`(앞부분), `runtime/self_check_obligations/` 세 기록을 읽었다.
  - `work/execution-control/.../outbox/`의 거부 영수증 2개
  - `work/runs/EX-01M3HN178J.../workspace/input/catalog/submission_failures.json`
  - `work/runs/EX-01M3HMRTDW.../evidence/stdout.jsonl`의 명령 실행 사건 전부(명령, 종료 코드, 출력 길이)
  - `work/operator/bootstrap/<hash>/scripts/do_math/*.py` 82개. 커밋별 원본과 바이트 대조만 했다.

**Git 판독.** 커밋 목록은 `git log 9b434f4^..3552607`로 봤다. 다음 커밋의 diff를 해당 파일 범위에서 읽었다.

- `5ecc321`: 통계, 추가 시험 이름
- `8af1f5e`: scheduler.py, record_schemas/schemas.py, 추가 시험 이름
- `1a8ce7a`: state_checks.py, test_state_checks.py, scheduled_operator.py, observations.py, 추가 시험 이름
- `3552607`: formal_engine.py, observations.py, planning.py, state_checks.py, test_lifecycle_engine.py, test_live_observation.py, 추가 시험 이름
- `9b434f4`: parallel.py, review_engine.py, 추가 시험 이름
- `85a540c`: review_cycle.py, planning.py, 추가 시험 이름

주입 커밋은 `git log -S`로 찾았다. 당시 판본은 `git show <커밋>:<경로>`로 필요한 행만 읽었다.

**읽지 못했거나 읽지 않은 자료.**

- 동결문: 3차 런(`임시/do-math_검증_20260928/동결.md`)은 읽지 않았다. 시험 인스턴스의 검증런 유출 판정은 M-0352·M-0354 두 런을 대상으로 하므로 필요가 없었다.
- 직접 처리 문서: 3차 런의 `직접처리/` 여섯 파일은 읽지 않았다.
- 2차 런 기각보관: 2차 런(`임시/do-math_검증_20260927-2/`)의 기각보관 본문은 읽지 않았다. 필요한 판정은 장부 사유 절과 종료 보고에 있었다.
- 개선안 폴더: `임시/do-math_개선안_20260928/`의 `입력감사.md`와 `입력재설계_결정.md`는 읽지 않았다.
- 인스턴스 기록: 첫 연구 수행(`MRTDW`)을 뺀 실행의 native 사건열과 운영 단계 기록은 읽지 않았다.
- 원문이 없는 항목: 승인·적용된 검증런 항목 본문은 라운드 디렉토리를 정리할 때 지워졌다. 해당 항목의 판정은 장부 요지, 종료 보고, 수리 커밋 diff로 했다.

## 2. 요약 표

### 2.1 개별 기록

| 번호 | 제목 | 영향 | 결함 유형 | 위치 층 | 시험 유출 원인 | 범주 후보 |
|---|---|---|---|---|---|---|
| C-01 | 동일성 검토 입력이 형식 증거로 한도 초과 | 정지 | 인터페이스 | L2 | 합성 입력이 실제와 다름, 시간·규모 미재현 | 판단 입력의 규모 폭주 |
| C-02 | 목표 감사 입력이 원출력 두 벌로 10.7MB | 정지 | 인터페이스 | L2 | 합성 입력이 실제와 다름, 시험 없음 | 판단 입력의 규모 폭주 |
| C-03 | 자기 점검 응답·안전 경계가 닫힌 저장 스키마에서 거부 | 정지 | 스키마·계약 불일치 | L2 | 대역이 가림, 단언 약함 | 생산자 필드와 닫힌 스키마의 어긋남 |
| C-04 | 도구 실행 중 열린 자기 점검 의무가 안전 경계 없이 응답 불가 | 저하 | 기능 | L2 | 조합·순서 미탐색 | 자기 점검 경로의 전이 공백 |
| C-05 | 자기 점검 응답 기한이 도구 실행 중에도 흐름 | 저하 | 타이밍·직렬화 | L2 | 조합·순서 미탐색 | 자기 점검 경로의 전이 공백 |
| C-06 | 운영 점검 제출 검사 안의 두 허용 집합 불일치 | 저하 | 스키마·계약 불일치 | L2 | 합성 입력이 실제와 다름 | 같은 규칙의 두 사본 |
| C-07 | 편입 단계의 전제 변경을 출력 오류로 분류해 수리 한도 소진 | 저하 | 검사 | L2 | 조합·순서 미탐색, 동시성 미재현 | 현재성 반환의 경로 오분류 |
| C-08 | 운영 점검 반복 실패의 대기를 풀 주체가 없음 | 정지 | 기능 | L2 | 시험 없음 | 탈출 경로 없는 대기 |
| C-09 | 예약 실행기의 `pythonw.exe`가 작업자 지급 명령에 들어감 | 저하 | 외부 경계 | 경계 어댑터 | 환경 차이 | OS·실행 환경 가정 |
| C-10 | 사전 검사 출력 1MB와 잘린 JSON | 저하 | 인터페이스 | 경계 어댑터 | 합성 입력이 실제와 다름 | 판단 입력의 규모 폭주 |
| C-11 | 관찰 창 120초가 대표 Mathlib 검사보다 짧음 | 저하 | 문서·계약 | 계약·스키마 | 시험 없음 | 설정값 근거 부재 |
| C-12 | 종결 인스턴스의 과제가 착수 가능으로 표시 | 저하 | 검사 | L2 | 시험 없음 | 종결 판정 사본 |
| C-13 | 입력 초과 기록이 비교에 쓴 예산 대신 전체 상한을 적음 | 저하 | 대입·초기화 | L2 | 단언 약함 | 기록과 판정 기준의 어긋남 |
| C-14 | 형식 결과 원출력 5.38MB를 그대로 보존 | 저하 | 알고리즘 | L2 | 합성 입력이 실제와 다름 | 판단 입력의 규모 폭주 |
| C-15 | 형식 검사 직전 판본 불일치가 환경 대기 대신 연구 재평가로 감 | 정지 | 인터페이스 | L2 | 단언 약함 | 탈출 경로 없는 대기 |
| C-16 | 정비 fence 아래 `run`이 `UnboundLocalError`로 사망 | 정지 | 대입·초기화 | L3 | 시험 없음 | 소유 루프 예외 사망 |
| C-17 | 허가 질문의 `question_kind`가 닫힌 저장 스키마에 없음 | 정지 | 스키마·계약 불일치 | L2 | 시험 없음 | 생산자 필드와 닫힌 스키마의 어긋남 |
| C-18 | `formal_authority`·`formal_stopped` 대기에 재개 경로 없음 | 정지 | 기능 | L2 | 시험 없음 | 탈출 경로 없는 대기 |
| C-19 | 신뢰 재검사가 배정 관문과 달리 grant를 요구해 정지 | 정지 | 검사 | L2 | 합성 입력이 실제와 다름 | 같은 규칙의 두 사본 |
| C-20 | 설치 복구 1회 제한이 판정 못 한 호출까지 세어 영구 차단 | 정지 | 검사 | L2 | 조합·순서 미탐색, 단언 약함 | 한도·계수의 잘못된 소진 |
| C-21 | `deadline_only` 관찰 입력 반려의 `followup: None`으로 엔진 사망 | 정지 | 대입·초기화 | L2 | 시험 없음 | 소유 루프 예외 사망 |
| C-22 | 목표 판정 무효화의 `invalidated_reason`이 스키마에 없어 이후 저장 전부 거부 | 정지 | 스키마·계약 불일치 | L2 | 단언 약함 | 생산자 필드와 닫힌 스키마의 어긋남 |
| C-23 | 공유 `TEXT` 노드 제자리 `enum`으로 보충 조사 제출 전건 거부 | 정지 | 대입·초기화 | L1 | 단언 약함 | 공유 스키마 노드 변이 |
| C-24 | `ModelCalls` 펌프가 관찰 행을 상한 없이 비워 소유 루프 고착 | 정지 | 타이밍·직렬화 | L3 | 확인 불가 | 소유 루프 기아 |
| C-25 | 신뢰 환경 조건 문법의 상태값이 실제와 달라 `candidate` 조건이 영원히 거짓 | 정지 | 스키마·계약 불일치 | L2 | 시험 없음 | 탈출 경로 없는 대기 |
| C-26 | 시작 전에 정지된 형식 검사가 종료 장벽에 보류 | 정지 | 기능 | L3 | 시험 없음 | 탈출 경로 없는 대기 |
| C-27 | 제어 전송 영수증 조회가 다른 전송의 영수증을 먼저 찾아 `pump`가 예외 | 정지 | 알고리즘 | L3 | 조합·순서 미탐색 | 소유 루프 예외 사망 |

**영향 등급별 건수.** 개별 기록은 27건이다. 정지 17건, 저하 10건, 잠재 0건이다.

- **시험 인스턴스에서 드러난 결함(C-01~C-14): 14건.** 정지는 4건으로 C-01, C-02, C-03, C-08이다. C-02는 인스턴스 해석 중 코드 추적으로 찾았고 운전에서는 발현되지 않았다. C-04는 운전에서 증상이 보였지만 원인은 3차 검증런이 판정했다.
- **검증런이 찾은 결함(C-15~C-22): 8건.** 모두 정지다.
- **기간 안의 그 밖의 발견(C-23~C-27): 5건.** 모두 정지이며, 시험 실행과 정적 검토로 찾았다.

### 2.2 개별 기록을 쓰지 않은 결함의 출처별 건수

검증런 장부는 제목 요지, 처분, 종료 보고, 수리 diff로 영향을 판정했다. `무영향`은 서식 3절 등급 밖의 분류다. 동작에 영향이 없는 잔재·사본·죽은 인자·문서·시험 구조 정리가 여기에 든다(4절 관찰 7).

| 출처 | 행·건 | 정지(개별) | 저하 | 잠재 | 무영향 | 비고 |
|---|---|---|---|---|---|---|
| 안정화 검증 장부(M-0352, 20260927) | 58 | 1(C-15) | 5: R1-06, R1-11, R1-32, R1-43, R1-50 | 2: R1-29, R1-49 | 50 | 무영향 가운데 R1-01·R1-21·R1-22는 수집되지 않던 시험이다(관찰 3) |
| 전면 검증 2차 장부(M-0354, 20260927-2) | 92 | 2(C-16, C-17) | 10: R1-02, R1-35, R1-41, R1-49, R1-50, R1-85, R1-86, R1-87, R1-88, R1-89 | 3: R1-05, R1-39, R1-54 | 77 | 통합 확인에서 시험 전제 결함 2건과 픽스처 회귀 1건이 따로 나왔다 |
| 전면 검증 3차 R1 장부(M-0356) | 69 | 1(C-18). R1-16·R1-40은 C-04로 개별 기록 | 23: R1-02, 03, 07, 11, 17, 19, 20, 24, 25, 31, 37, 38, 42, 43, 44, 45, 46, 50, 52, 62, 64, 66, 69 | 3: R1-01, R1-22, R1-61 | 40 | 장부 밖의 목표 감사 자리 운영 점검 누출 1건(저하, 세션 직접 처리)이 따로 있다 |
| 전면 검증 3차 R2 장부(M-0357) | 56 | 4(C-19~C-22) | 15: R2-02, 03, 13, 14, 15, 21, 25, 31, 32, 34, 38, 39, 40, 41, 46 | 4: R2-04, R2-05, R2-09, R2-29 | 33 | 최종 통합 확인이 찾은 `GRANT` 열린 모양은 R2-04와 같은 결함이다. 시험 전제 결함은 2건이다 |
| 정리 검토(M-0351) 보고서 3.1·잠재 | 14 | 1(C-25) | 9: ENG-01, RES-05, RES-06, RES-11, RES-13, REV-01, HIS-19, DOC-01, ENG-02(실패 경로 추정) | 2: REV-23/HIS-04, STO-18/HIS-15 | 2: DOC-08, OPS-01 | 후보 189건 가운데 3.1·잠재 목록 밖은 결함 판정 전의 정리 후보라 세지 않았다 |
| 정리 구현 중 발견(M-0351) | 2 | 2(C-26, C-27) | 0 | 0 | 0 | 최종 확인의 오류 5건은 시험 대역 결함이다 |
| 시험 경량화 작업의 시험 실행(M-0350) | 68 실패 | 2(C-23, C-24) | 1: `operation_trace` 타이머 핸들(같은 작업 안에서 생기고 고쳐져 출하되지 않음) | 0 | 나머지(원자료가 건수를 나누지 않음) | 나머지는 시험 대역·픽스처가 현행 계약을 따라가지 못한 것이다 |
| 검사 경량화 작업(M-0348) | 기록된 7종 | 0 | 1: R5 파일·디렉터리 이름 충돌 시 Git의 조용한 파일 폐기(기존 결함) | 0 | 개발 중 포착 4종(출하 전)과 시험 회귀 8건 | 출하 전 포착은 관찰 6 |
| 경량화 2라운드(M-0349) | 0 | 0 | 0 | 0 | 0 | 시험을 돌리지 않았다. 위험 목록만 있다 |
| 교재(M-0353) | 0 | 0 | 0 | 0 | 0 | do-math 결함 없음 |
| 시험 인스턴스 해석·구현(M-0355) | 2 | 0 | 1: 입력 재설계가 만든 목표 감사 누출(시험 실패 분석 중 발견) | 0 | 1: `CLI-실행-계약.md`의 `needs_reconstruction` 문서 불일치 | 인스턴스 결함은 C-01~C-14 |

## 3. 개별 기록

### C-01 동일성 검토 입력이 형식 증거로 한도 초과

- 출처: `C:\math\임시\do-math_RI-01M3HM0X_해석\원고.md` 4.5절·6.1절, `C:\math\임시\do-math_개선안_20260928\원고.md` 2절, 인스턴스 `repo`의 `runtime/input_overflows/state.json`(actual_bytes 663501). 수리 커밋 `5ecc321`.
- 발견 경위: 실제 운전
- 영향 등급: 정지. 인스턴스 자체는 멈추지 않았다. 연구 계획이 "소형 재제안" 과제를 만들어 우회했다. 그러나 동일성 판정이 없으면 K가 생기지 않는다. 이 제안은 `import Init`에 선언 다섯이었고, 선언마다 폐포가 603개였다. Mathlib를 쓰는 평범한 제안은 이보다 증거가 크다. 설정(`max_input_bytes`)이나 코드를 사람이 바꾸기 전에는 목표 감사 경로가 열리지 않는다.
- 증상: 23:46:48에 동일성 검토의 범위 계획 실행(NAD8K)이 모델 호출 전에 취소됐다(`mandatory_context_exceeds_limit`, 필수 411,989B). 검토 계보는 `unresolved`로 닫혔고, 목표 감사는 0회, 목표는 `unsolved`로 끝났다.
- 근본 원인: 판단 역할 입력의 형식 결과 투영에 기계 무결성 증거가 섞여 있었다(`review_cycle.py` 374~377행 `_FORMAL_FIELDS`, bdccee3 판본). 대상 필드는 `dependency_evidence`, `dependency_closure`, `declaration_evidence`다. `role_review` 322,189B 가운데 세 필드가 311,352B였고, 수학 내용은 약 1.2KB였다. 무결성은 이미 `verification` 전체 해시가 결박하고 있었다(개선안 2.3). 한도 비교가 전체 상한이 아니라 "상한 − 고정 부분(약 235,400B)"과 이루어진다는 점도 겹쳤다(`context_store.py` 636~640행).
- 수정: `5ecc321`. 판단용 투영 `knowledge_records.judged_verification`을 두었다. 역할 입력은 `context_store.INLINE_SCOPES`와 `BLOCKED_KEYS`로 싣기·지도·차단으로 나누고, 상한을 2,000,000B로 올렸다. 회귀 시험은 다음 둘이다.
  - `test_role_input.test_identity_review_proposal_carries_only_the_judged_formal_fields`
  - `test_configuration.test_default_input_limit_is_two_million_bytes_in_code_and_config_list`
- 결함 유형: 인터페이스
- 트리거: 실제 외부 도구 동작(Lean 실제 출력의 선언별 폐포 603개)과 장시간 누적(선언 수에 비례하는 증거 크기)
- 결함 위치 층: L2 인터페이스 요소(역할 입력 구성)
- 시험 유출 원인:
  - 합성 입력이 실제와 다름: bdccee3 판본 `tests/knowledge_fixtures.py` 50·56행의 형식 결과 픽스처는 폐포가 두 상수(`'fixture-type', 'fixture-value'`)다. 실제는 선언당 603개였다.
  - 시간·규모 미재현: 실제 크기의 형식 결과를 실제 `max_input_bytes`로 동일성 검토 입력까지 보내는 시험이 없었다.
  - 주입 커밋은 특정하지 못했다. 세 증거 필드는 `8d2ffd0^` 판본 `review_engine.py` 30행에 이미 있었고, 최초 도입 커밋은 찾지 않았다.
- 검증런 유출:
  - M-0352(앵커 85a540c): 해당 파일이 모두 범위 안이었다. `context_store.py`는 수리 3, `review_cycle.py`는 수리 4 영역이었고, 관점 7의 필수 독해 diff에도 두 파일이 들어 있었다(동결 722·752행). 찾을 결함 4(비효율), 8(그 밖)도 이 경우에 해당했다. 범위에 들었는데 놓쳤다.
  - M-0354(앵커 bdccee3, 인스턴스와 같은 코드): 같은 영역 배분이라 범위 안이었다. 이 런은 입력 축소 서술 불일치(R1-84)는 찾았지만 크기 초과 구조는 찾지 못했다. 범위에 들었는데 놓쳤다.
  - 두 런 모두 수리자가 코드를 실행하지 않는 정적 검토였고(2차 동결 397행), 통합 확인은 작은 픽스처로 통과했다.
- 가장 싼 포착 시험: 실제 Lean 검사 출력 하나를 픽스처로 고정한다. 크기는 선언 5개, 폐포 603개, 원출력 약 5MB다. 이 형식 결과를 가진 지식으로 `prepare_role_input(role='identity_review', stage='scope')`를 기본 설정의 `max_input_bytes`로 부르고, 결과가 초과 기록이 아니며 입력이 한도 안임을 단언한다. 모델도 Lean도 부르지 않는 순수 입력 구성 시험이다.
- 범주 후보: 판단 입력의 규모 폭주

### C-02 목표 감사 입력이 원출력 두 벌로 10.7MB

- 출처: `C:\math\임시\do-math_개선안_20260928\원고.md` 2.2절(`engine.py` 1740~1751행, `knowledge_records.py` 95~96행, `engine.py` 3070~3074행), `C:\math\기억\layer1\M-0355.md` 맥락 2항. 수리 커밋 `5ecc321`.
- 발견 경위: 정적 검토. 인스턴스 해석 뒤 조사 에이전트가 HEAD 코드를 추적해 찾았다.
- 영향 등급: 정지. 발동하면 목표 감사가 입력 초과로 사용자 차단 질문 경로에 들어간다(개선안 2.2). 그러면 사용자가 답할 때까지 멈춘다.
- 증상: 운전 미발현. 인스턴스가 동일성 검토에서 먼저 막혀 목표 감사까지 가지 못했다.
- 근본 원인: 목표 감사 입력은 지식마다 두 가지를 싣는다. 하나는 `proposal_view`로, 형식 결과 `verification` 전체를 복사한다. 다른 하나는 `formal_result` 기록 전체다. 저장소는 큰 문자열을 따로 보존하지만, `payloads.decode`가 적재할 때 원문을 메모리로 복원한다. 그래서 검사 원출력 5,381,117B가 두 번 실린다. 계약(`계약/목표-감사.md` 19행)은 선언·타입·공리·신뢰 환경만 대조하게 한다.
- 수정: `5ecc321`. 판단용 투영 하나를 동일성 검토·목표 감사·지식 파일에 함께 쓰게 했다. 회귀 시험은 `test_role_input.test_goal_audit_receives_the_judged_formal_result`와 `test_knowledge_files_carry_the_judged_formal_result`다.
- 결함 유형: 인터페이스
- 트리거: 실제 외부 도구 동작(Lean 원출력 크기)과 특정 전이 순서(동일성 판정 `match` 뒤 목표 감사)
- 결함 위치 층: L2 인터페이스 요소
- 시험 유출 원인:
  - 합성 입력이 실제와 다름: 픽스처 형식 결과의 원출력과 증거가 실제보다 작다(C-01과 같은 픽스처).
  - 시험 없음: 목표 감사 입력 크기를 단언하는 시험이 5ecc321 전에는 없었다(수리 커밋이 위 두 시험을 새로 더했다).
  - 주입 커밋: 특정하지 못했다.
- 검증런 유출: M-0352·M-0354 모두 `engine.py`(수리 2 영역)와 `knowledge_records.py`(수리 3 영역)를 범위에 넣었다. 범위에 들었는데 놓쳤다.
- 가장 싼 포착 시험: C-01과 같은 실제 크기 형식 결과로 `match` 판정까지 마친 지식을 시작 상태로 둔다. 목표 감사 역할 입력을 구성하고, 입력 바이트가 기본 상한 안이며 원출력 문자열이 입력에 없음을 단언한다.
- 범주 후보: 판단 입력의 규모 폭주

### C-03 자기 점검 응답·안전 경계가 닫힌 저장 스키마에서 거부

- 출처: 인스턴스 `work/execution-control/RI-01M3HM0X.../YnAJRMQaX9lYRlNpKAEvhesc/outbox/`의 두 영수증. 하나는 `self-check-SC-a7281327c7538201ad57.json`(`'control_call_ids' was unexpected`), 다른 하나는 `boundary-nat-add-zero-01.json`(`'boundary_receipt_ref' was unexpected`)이다. `C:\math\임시\do-math_개선안_20260928\원고.md` 3절. 주입 커밋 `7d2597e`, 수리 커밋 `5ecc321`.
- 발견 경위: 실제 운전
- 영향 등급: 정지. 제어 통로로 온 자기 점검 응답이 조건 없이 모두 거부됐다. 서식 3절의 "필수 역할 출력의 전건 거부"에 해당한다. 안전 경계 제출도 전부 거부됐다. 연구 수행 자체는 이어졌지만 자기 점검 의무 셋이 끝까지 `open`으로 남았다. 이 때문에 운영 점검 계보 1과 계보 3이 열렸다.
- 증상: 23:41 무렵 첫 응답이 거부됐다. 최대 간격 의무(SC-c0a6)의 안전 경계 제출도 거부됐다. 최종 스냅숏에서 세 의무는 모두 `status: open`이다(저장소 `runtime/self_check_obligations/`에서 확인).
- 근본 원인:
  - 필드 불일치: 추적기가 저장 기록에 쓰는 필드가 저장 스키마에 없다. `observations.py` 899행의 `control_call_ids`와 737행의 `boundary_receipt_ref`가 그렇고(bdccee3 판본), 응답에 `rule_proposal`이 있으면 927행의 `rule_update`도 쓴다. 스키마는 `record()`로 만든 닫힌 객체다(`schemas.py`의 `additionalProperties: false`).
  - 이중 정의: 저장 기록의 모양이 추적기 메모리 dict와 `schemas.py` 두 곳에 따로 정의돼 있다. 생산자는 저장 스키마로 스스로 검사하지 않는다.
  - 주입: `7d2597e` 판본에서 이미 `observations.py` 711·873행이 두 필드를 쓰는데, 같은 판본의 `record_schemas/schemas.py` 184~188행과 `domains.py` 213~222행은 이를 선언하지 않았다(`git show 7d2597e:` 판독).
- 수정: `5ecc321`.
  - 필드 처분: `control_call_ids`는 저장 기록에서 뺐다. `boundary_receipt_ref`와 `rule_update`는 스키마에 선언했다.
  - 생산자 검사: 생산 지점에서 저장 관문과 같은 검사기(`stored_obligations`)를 실행하게 했다.
  - 회귀 시험: `test_controls.test_self_check_response_and_its_rule_update_are_saved`, `test_controls.test_safety_boundary_is_saved_and_its_replay_redelivers_the_opened_obligation`, `test_observations.test_tracker_records_leave_through_the_storage_check`
- 결함 유형: 스키마·계약 불일치
- 트리거: 실제 모델 출력 형태(작업자가 MCP 도구로 자기 점검 응답을 실제로 보냄)
- 결함 위치 층: L2 인터페이스 요소(제어 요청 해석과 상태 저장)
- 시험 유출 원인:
  - 대역이 가림: 저장소 대역이 결함 지점을 대신했다. bdccee3 판본 `tests/test_controls.py` 183행이 `engine._save = create_autospec(engine._save, ...)`로 저장 계약 검사를 건너뛴다.
  - 단언 약함(결함 고정): 주입 시점 `7d2597e` 판본의 `tests/test_observation_audit1.py` 50행과 bdccee3 판본의 `tests/test_observations.py` 470행이 스키마 밖 필드 `control_call_ids`를 기대값으로 단언했다. 시험이 결함 동작을 계약으로 고정한 것이다(4절 관찰 7).
- 검증런 유출:
  - M-0352: `observations.py`와 `engine.py`는 수리 2, `record_schemas/schemas.py`는 수리 3 영역이었다. 동결문 찾을 결함 2가 "생산자와 소비자 사이의 계약 불일치"를 명시했다(동결 276행). 이 런은 같은 파일에서 체크포인트 스키마 사본(R1-51·R1-52)을 고쳤다. 범위에 들었는데 놓쳤다.
  - M-0354: 같은 영역 배분이고 찾을 결함 2가 같다(동결 278행). 이 런은 같은 `schemas.py`에서 같은 기제의 결함 R1-24(C-17, `question_kind`)를 찾았다. 또 `record_safe_boundary`의 죽은 인자 `self_check_only`(R1-15, `observations.py` 723~729행)를 고쳤는데, 이 자리는 `boundary_receipt_ref`를 쓰는 737행과 같은 함수 안이다. 범위에 들었는데 놓쳤다.
- 가장 싼 포착 시험: 추적기의 공개 동작 넷을 차례로 부른다. 의무 열기, 안전 경계 기록, 응답 기록(`rule_proposal` 포함), 의무 닫기다. 추적기가 내보내는 저장 기록마다 `default_state_contract().family(<가족>).checker`를 실행하고 오류가 없음을 단언한다. 엔진·저장소·모델 없이 L1 스키마 검사와 L2 추적기만 쓰는 시험이다. 모든 닫힌 가족에 대해 "생산자가 쓰는 키 ⊆ 스키마 properties"를 한 번에 단언하는 표 시험으로 일반화할 수 있다.
- 범주 후보: 생산자 필드와 닫힌 스키마의 어긋남

### C-04 도구 실행 중 열린 자기 점검 의무가 안전 경계 없이 응답 불가

- 출처: 인스턴스 `repo`의 `runtime/self_check_obligations/SC-7dc216c7ef4ca4c0fe73.json`과 `SC-c0a6bffbee0a6399672e.json`. 둘 다 `response_availability: awaiting_safe_boundary`, `deadline_offset_ms: None`, `status: open`이다. `C:\math\임시\do-math_검증_20260928\장부.md` R1-16·R1-40 행, 커밋 `1a8ce7a`의 `observations.py` diff.
- 발견 경위: 실제 운전에서 증상이 보였다. 원인은 검증런(3차 1라운드 R1-16·R1-40)이 판정했다.
- 영향 등급: 저하. 의무가 끝나지 않고, 경계 없이 보낸 응답은 `response_boundary_unconfirmed`로 반려되어 운영 점검을 연다(R1-40 요지). 연구 수행은 이어진다.
- 증상: 과제 2의 연구 수행 중 00:11:01에 열린 SC-7dc2가 안전 경계를 기다린 채 종결됐다. SC-c0a6의 경계 제출은 C-03 때문에 거부됐다.
- 근본 원인: 의무를 열 때 진행 중인 도구가 있으면 기한을 두지 않고 `awaiting_safe_boundary`로 둔다. 응답 검사는 그 상태면 오류를 낸다. bdccee3 판본 `observations.py` 835~839행과 1a8ce7a diff에서 지운 `response_availability` 분기가 이에 해당한다. 작업자가 경계를 따로 제출하지 않으면 풀리지 않는다. 5ecc321는 C-05를 고치면서 같은 원리(도구 실행 중 기한 정지)를 한 번 더 구현했고, 3차 검증은 이를 "두 번 구현"으로 판정했다(R1-16).
- 수정: `1a8ce7a`. 경계 대기를 자동 기한 정지로 대체하고 `response_boundary_unconfirmed` 검사를 지웠다. 회귀 시험은 다음 셋이다.
  - `test_observations.test_obligation_opened_during_a_research_call_is_held_until_the_call_ends`
  - `test_observations.test_call_reported_at_a_safe_boundary_stops_holding_the_deadline`
  - `test_controls.test_safety_boundary_releases_the_held_deadline_only_after_publication`
- 결함 유형: 기능
- 트리거: 특정 전이 순서(도구 실행 중 의무 열림, 이어서 응답)와 실제 모델 출력 형태(작업자가 경계를 제출하지 않고 응답)
- 결함 위치 층: L2 인터페이스 요소
- 시험 유출 원인: 조합·순서 미탐색. 경계 대기 자체는 시험됐지만(5ecc321의 `test_safety_boundary_is_saved_...`), "도구 실행 중 열림 → 경계 없이 응답" 순서의 결과는 시험되지 않았다. 주입 커밋은 특정하지 못했다(경계 대기 설계의 도입 시점을 찾지 않았다).
- 검증런 유출:
  - M-0352·M-0354: `observations.py`가 수리 2 영역으로 범위 안이었다. 범위에 들었는데 놓쳤다.
  - 3차 1라운드: 찾았다(R1-16·R1-40).
- 가장 싼 포착 시험: 추적기에 도구 호출 시작 사건을 넣고, 체크포인트로 의무를 연 뒤, 경계 제출 없이 유효한 응답을 기록한다. 응답이 수락되고 의무가 `answered`가 됨을 단언한다. 순수 추적기 시험이다.
- 범주 후보: 자기 점검 경로의 전이 공백

### C-05 자기 점검 응답 기한이 도구 실행 중에도 흐름

- 출처: `C:\math\임시\do-math_RI-01M3HM0X_해석\원고.md` 4.3절 1~4항, `C:\math\임시\do-math_개선안_20260928\원고.md` 6.4절 2항, 인스턴스 `repo`의 `SC-a7281327…`(`missed_reason: response_deadline_passed`). 수리 커밋 `5ecc321`.
- 발견 경위: 실제 운전
- 영향 등급: 저하. 기한이 지나 운영 점검 계보 1(MXWR8, N178J)이 열렸고, 그 처분이 예약한 재점검으로 계보 3(N750S, N8JM4)도 열렸다. 비용이 늘었다(운영 점검 여섯 실행의 입력 약 232만 토큰).
- 증상: 의무 SC-a728이 23:37:55에 열리고 기한은 120초였다. 작업자가 알림을 읽기 전에 사전 검사(`item_6`, Mathlib 적재로 120초 초과)를 시작했고, 그 사이 기한이 지났다. 명령 실행 목록에서 `item_6`이 종료 코드 1이었음을 확인했다.
- 근본 원인: 도구 실행 중 기한 정지는 의무를 열 때만 적용됐다. 열린 뒤 작업자가 새 도구를 시작하면 기한이 계속 흘렀다(개선안 6.4).
- 수정: `5ecc321`. 응답 전 연구 호출이 시작되면 남은 시간을 저장하고 기한을 멈추며, 호출이 모두 끝나면 다시 흐르게 했다. 회귀 시험은 `test_observations.test_research_calls_before_the_response_hold_its_deadline_until_all_of_them_end`와 `test_research_call_after_the_deadline_does_not_hold_it`이다.
- 결함 유형: 타이밍·직렬화
- 트리거: 시간 경과·기한, 특정 전이 순서(의무 열림 → 긴 도구 시작)
- 결함 위치 층: L2 인터페이스 요소
- 시험 유출 원인: 조합·순서 미탐색. 의무를 열 때의 도구 진행 여부만 시험됐고, 연 뒤 시작한 도구는 시험되지 않았다. 주입 커밋은 특정하지 못했다.
- 검증런 유출: M-0352·M-0354 모두 `observations.py`를 범위에 넣었다(수리 2 영역). 범위에 들었는데 놓쳤다.
- 가장 싼 포착 시험: 가짜 시계를 쓴 추적기에서 의무를 열고(기한 120초), 도구 시작 사건을 넣은 뒤 시계를 200초 진행한다. 의무가 기한 경과로 표시되지 않음을 단언한다. 이어 도구 종료 사건을 넣고 남은 시간만큼 뒤에 기한이 오는지 단언한다.
- 범주 후보: 자기 점검 경로의 전이 공백

### C-06 운영 점검 제출 검사 안의 두 허용 집합 불일치

- 출처: 인스턴스 `work/runs/EX-01M3HN178J…/workspace/input/catalog/submission_failures.json`. 네 이슈 모두 `submission.explicit_reference` 또는 `submission.output.used_sources.*`이고, 인용 대상은 `OF-…-15`와 `SC-a7281327…`이다. `C:\math\임시\do-math_개선안_20260928\원고.md` 4.1절. 주입 커밋 `c44dd7b`, 수리 커밋 `5ecc321`.
- 발견 경위: 실제 운전
- 영향 등급: 저하. 세 계보의 첫 출력이 모두 반려됐고, 수리본은 정당한 관찰 근거를 지워 통과했다. 이 반려가 수리 한도 1을 소모했기 때문에 C-07·C-08과 겹쳐 계보 2가 영구 대기로 떨어졌다.
- 증상: MXWR8, MZW1A, N750S의 첫 출력이 자기를 부른 관찰 ID나 의무 ID를 인용했다가 반려됐다.
- 근본 원인: 한 제출 검사 안에서 허용 집합이 둘로 갈렸다. 운영 점검 전용 검사 `require_basis_refs`는 `admissible_basis_refs`를 허용 집합으로 쓴다(`submission.py` 811~815행). 범용 참조 검사는 `_reference_index`를 쓰는데(511~517행), 이 인덱스는 `admissible_basis_refs`를 읽지 않는다. 문서 `계약/운영-점검.md` 39행의 "같은 참조 규칙"과도 다르다. `admissible_basis_refs`는 `c44dd7b`에서 처음 나타난다(`git log -S`).
- 수정: `5ecc321`. 참조 인덱스에 `admissible_basis_refs`를 합쳤다. 회귀 시험은 `test_role_input.test_every_advertised_basis_ref_passes_the_submission_check`다. 후속으로 3차 1라운드 R1-20·R1-52·R1-63이 남은 어긋남(읽기 색인에 없음, 생산자 없는 키 순회)을 고쳤다.
- 결함 유형: 스키마·계약 불일치
- 트리거: 실제 모델 출력 형태(생산자가 자기를 부른 관찰을 인용함)
- 결함 위치 층: L2 인터페이스 요소(제출 검사)
- 시험 유출 원인: 합성 입력이 실제와 다름. bdccee3 판본 `tests/test_role_input.py` 118~137행의 시험은 근거로 `EX-work` 하나만 넣었다. 이 원소는 두 허용 집합에 모두 있어 두 규칙이 우연히 일치했다. 관찰 ID(`OF-…`)나 의무 ID(`SC-…`)를 넣은 경우는 없었다.
- 검증런 유출:
  - M-0352: `submission.py`는 수리 4, `operational_dispositions.py`는 수리 2 영역이었고, 관점 7의 85a540c diff에 두 파일이 있었다. 범위에 들었는데 놓쳤다.
  - M-0354: 관점 8(역할 계약 열한 개와 코드의 대응)이 `계약/운영-점검.md`를 맡았다. 같은 문서의 다른 어긋남(R1-87 `task_assessments`)은 찾았지만 39행 서술과 코드의 차이는 놓쳤다. 범위에 들었는데 놓쳤다.
- 가장 싼 포착 시험: 운영 점검 역할 입력을 구성하고, 지급된 `admissible_basis_refs`의 원소마다 그 원소 하나만 `basis_refs`와 `used_sources`에 넣은 출력을 만든다. 각 출력에 `payload_issues`가 비어 있음을 단언한다. 속성 시험의 형태다: "지급한 근거는 모두 인용할 수 있다".
- 범주 후보: 같은 규칙의 두 사본

### C-07 편입 단계의 전제 변경을 출력 오류로 분류해 수리 한도 소진

- 출처: 인스턴스 `repo`의 `runtime/waiting_actions/state.json`. `AC-01M3HMYE06…`의 이슈는 `integration.application`, `invalid_basis_refs=['…BA-01M3HMT649…']`, `admissible_basis_refs=[…'BA-01M3HN4FAF…']`이다. `C:\math\임시\do-math_개선안_20260928\원고.md` 4.2절. 주입 커밋 `c44dd7b`, 수리 커밋 `5ecc321`.
- 발견 경위: 실제 운전
- 영향 등급: 저하. 이 결함 자체는 출력 수리 1회를 소모시킨다. 계보 2에서는 C-06이 한도를 이미 소모한 뒤라 곧바로 C-08의 영구 대기로 이어졌다.
- 증상:
  - 계보 2의 수리 실행 N3ZY2는 입력 시점에 정당했던 체크포인트를 인용했다. 적용 직전(14:43:32 UTC) 대상 연구 수행이 새 체크포인트를 써서 편입에서 반려됐다. 반려 문구 "outside its current input"은 사실과 다르다.
  - 연구 계획 N9VM6의 `integration.currentness` 반환도 재시도 NPXKF에 `repair` 블록을 달고 이어졌다(해석 4.6절).
- 근본 원인: 적용 검사는 적용 시점 상태로 허용 목록을 다시 계산한다(`engine.py` 3913~3919행). 목록은 최신 체크포인트 하나만 담는다(`operational_dispositions.py` 40~41행). 편입 단계의 현재성 반환은 갱신 경로(`decision_engine.py` 186~210행)가 아니라 출력 수리 경로(`repair_execution.py` 23~42행)로 갔다. 반려 문구 "cites evidence outside its current input"은 `c44dd7b`에서 처음 나타난다(`git log -S`).
- 수정: `5ecc321`. 입력 시점 목록에 있던 참조만 바뀐 경우와 `integration.currentness`를 갱신 경로로 보낸다. 회귀 시험은 다음 셋이다.
  - `test_currentness.test_operational_basis_replaced_after_input_is_refreshed_without_output_repair`
  - `test_currentness.test_replaced_operational_basis_with_another_application_error_stays_a_producer_repair`
  - `test_currentness.test_only_evidence_admitted_at_input_can_become_a_changed_premise`

  이 경로는 이후 세 번 더 고쳐졌다.
  - 3차 1라운드 R1-53: 부분 수락 뒤 현재성 반환 시험(`test_currentness_return_beside_an_accepted_bundle_is_refreshed_not_repaired`)
  - 3차 1라운드 R1-62: 갱신 요청이 옛 `repair` 블록 복사(`test_premise_refresh_of_an_output_repair_carries_no_previous_submission_issues`)
  - 3차 2라운드 R2-46: 갱신의 `continuation_of` 계보(`test_premise_refresh_of_an_output_repair_continues_the_refreshed_execution`)
- 결함 유형: 검사
- 트리거: 동시성·경합(운영 점검 실행 중 대상 실행이 체크포인트를 씀)과 특정 전이 순서
- 결함 위치 층: L2 인터페이스 요소(편입과 재시도 분류)
- 시험 유출 원인:
  - 조합·순서 미탐색: 입력 봉인과 적용 사이에 근거가 바뀌는 순서가 시험되지 않았다.
  - 시간·규모 미재현: 두 실행이 동시에 도는 경합이 재현되지 않았다.
- 검증런 유출: M-0352·M-0354 모두 `engine.py`·`repair_execution.py`(수리 2), `decision_engine.py`(수리 4)를 범위에 넣었다. 범위에 들었는데 놓쳤다.
- 가장 싼 포착 시험: 운영 점검 행동의 입력을 봉인한 뒤 대상 실행의 체크포인트를 교체한다. 그 뒤 입력 시점 체크포인트를 인용한 출력을 편입한다. 결과가 갱신 요청이고 출력 수리 계수가 그대로임을 단언한다. 모델 없이 엔진 상태만으로 가능하다.
- 범주 후보: 현재성 반환의 경로 오분류

### C-08 운영 점검 반복 실패의 대기를 풀 주체가 없음

- 출처: 인스턴스 `repo`의 `runtime/waiting_actions/state.json`. `kind: output_validation`, `next_owner: operational_review`, `reason: "Producer repair was rejected again; diagnose the preserved contract and receiver errors"`. `C:\math\임시\do-math_개선안_20260928\원고.md` 4.3절. 수리 커밋 `5ecc321`.
- 발견 경위: 실제 운전
- 영향 등급: 정지. 대기가 사람 개입 없이 풀리지 않는다. 수리본이 반려된 23:44 무렵부터 인스턴스 종결(00:12)까지 약 28분 남아 있었고, 감독 주기 7,200초 안에 처리된 기록이 없다(해석 4.4절).
- 증상: 계보 2(`AC-01M3HMYE06…`)가 수리 한도 1을 소진한 뒤 `waiting_actions`에 남아 종결까지 미해소였다.
- 근본 원인:
  - 재귀 차단: `repair_execution.py` 21~22행이 운영 점검이 다시 운영 점검을 부르는 재귀를 막는다. 그래서 운영 점검의 반복 실패는 표지만 달고 대기한다.
  - 소비자 부재: 이 표지를 소비하는 자동 경로가 없다.
  - 가시성 부재: 같은 대상의 다음 운영 점검은 `blocked_actions`를 대상 실행 ID로 거른다(`engine.py` 1880~1883행). 그런데 이 대기의 실행 ID는 실패한 점검 자신이라 보이지 않는다.
  - 주입 커밋: 반려 문구 "Producer repair was rejected again"은 `7d2597e`에서 처음 나타난다. 재귀 차단의 도입 시점은 찾지 않아 주입 커밋은 미확정이다.
- 수정: `5ecc321`. 같은 대상의 다음 운영 점검이 이 대기를 보고 해소하게 했다. 회귀 시험은 `test_role_input.test_next_review_of_the_same_target_can_resolve_an_exhausted_review`다.
- 결함 유형: 기능
- 트리거: 특정 전이 순서(운영 점검 출력 반려 → 수리본 반려)
- 결함 위치 층: L2 인터페이스 요소(대기 해소 규칙)
- 시험 유출 원인: 시험 없음. 운영 점검 자신의 수리 한도 소진 뒤 대기를 누가 푸는지 시험한 것이 5ecc321 전에는 없었다(수리 커밋이 위 시험을 새로 더했다).
- 검증런 유출: M-0352·M-0354 모두 `repair_execution.py`와 `engine.py`를 수리 2 영역에 넣었다. 범위에 들었는데 놓쳤다.
- 가장 싼 포착 시험: 모든 `waiting_actions.kind`와 `next_owner` 조합에 대해 그 대기를 재큐하거나 지우는 코드 경로가 하나 이상 있는지 표로 단언한다. 동적 확인은 운영 점검 행동을 두 번 반려시켜 대기에 넣은 뒤, 같은 대상의 다음 운영 점검 입력에 그 대기가 보이는지 단언한다.
- 범주 후보: 탈출 경로 없는 대기

### C-09 예약 실행기의 `pythonw.exe`가 작업자 지급 명령에 들어감

- 출처: 인스턴스 `work/runs/EX-01M3HMRTDW…/evidence/stdout.jsonl`의 `item_5`. 명령은 `…\Python312\pythonw.exe -B input/tools/check_lean.py …`, 종료 코드 0, 출력 7자다. 이어서 `item_6`에서 `python.exe`로 다시 실행했다. `C:\math\임시\do-math_개선안_20260928\원고.md` 5절. 수리 커밋 `5ecc321`.
- 발견 경위: 실제 운전
- 영향 등급: 저하. 작업자가 검사 출력을 잃고 한 번 더 실행했다.
- 증상: 지급된 사전 검사기를 `pythonw.exe`로 실행하자 출력이 없었다.
- 근본 원인: 예약 작업이 엔진을 `pythonw.exe`로 실행한다(`scheduled_operator.py` 132~133행). 작업자에게 주는 명령은 `submission.py` 1476·1482행에서 `sys.executable`로 만든다. `pythonw.exe`는 콘솔이 없는 GUI 하위 시스템 실행 파일이다. `submission.py`의 `sys.executable` 사용은 `cdbdc9e`(2026-09-16)까지 거슬러 간다(`git log -S`의 가장 오랜 결과). 예약 실행이 `pythonw`를 쓰게 된 시점은 찾지 않았다.
- 수정: `5ecc321`. 작업자·사람에게 주는 명령을 `console_python()`으로 만든다. 회귀 시험은 `test_lean_preview.test_worker_commands_use_the_console_interpreter_when_the_engine_runs_windowless`와 `test_operator.test_schedule_reconcile_uses_the_console_interpreter_when_run_windowless`다.
- 결함 유형: 외부 경계
- 트리거: 설정·환경(예약 작업의 창 없는 인터프리터), 실제 외부 도구 동작(Windows 하위 시스템)
- 결함 위치 층: 경계 어댑터
- 시험 유출 원인: 환경 차이. 시험은 `python.exe`로 돈다. bdccee3 판본에 `tests/test_schedule_pythonw.py`가 있었지만(M-0352 동결 491행의 영역 목록), 이 모듈은 예약 등록을 다룰 뿐 작업자 지급 명령을 다루지 않았다(수리 커밋이 지급 명령 시험을 새로 더했다).
- 검증런 유출: M-0352·M-0354 모두 `scheduled_operator.py`(수리 1)와 `submission.py`(수리 4)를 범위에 넣었다. 범위에 들었는데 놓쳤다.
- 가장 싼 포착 시험: `sys.executable`을 `…\pythonw.exe` 경로로 패치한다. 작업자 도구 지급 함수가 만든 명령 문자열의 인터프리터가 같은 폴더의 `python.exe`임을 단언한다.
- 범주 후보: OS·실행 환경 가정

### C-10 사전 검사 출력 1MB와 잘린 JSON

- 출처: 인스턴스 `work/runs/EX-01M3HMRTDW…/evidence/stdout.jsonl`의 `item_20`(출력 1,047,962자). `C:\math\임시\do-math_개선안_20260928\원고.md` 7.1절. JSON이 384,632번째 문자에서 깨졌다는 사실은 개선안의 판독이며 나는 재확인하지 않았다. 수리 커밋 `5ecc321`.
- 발견 경위: 실제 운전
- 영향 등급: 저하. 작업자가 받은 검사 결과가 해석할 수 없는 JSON이었다. 작업자는 판정을 읽어 진행했다.
- 증상: 사전 검사 한 번의 출력이 1MB를 넘었고 JSON이 잘렸다.
- 근본 원인: 작업자 사전 검사(`formal_preview`)가 중앙과 같은 `verify_lean`을 돌렸다. 그래서 작업자가 쓰지 않는 의존 폐포·식 DAG·해시 표를 모두 계산해 원출력과 함께 출력했다(`formal_preview.py` 36~40행, `formal.py` 505~507행).
- 수정: `5ecc321`. `extract_evidence=False`로 두고 `PREVIEW_FIELDS`만 출력하게 했다(534,902B → 2,346B). 회귀 시험은 `test_lean_preview.test_preview_attaches_no_dependency_extraction_and_prints_only_worker_fields`와 `test_preview_tool_and_compiler_worker_skip_unneeded_modules`다.
- 결함 유형: 인터페이스
- 트리거: 실제 외부 도구 동작(Lean 원출력 규모)
- 결함 위치 층: 경계 어댑터(Lean 실행 결과 출력)
- 시험 유출 원인: 합성 입력이 실제와 다름. 시험의 Lean 출력은 실제보다 작았다(C-01과 같은 픽스처 규모). 주입 커밋은 특정하지 못했다.
- 검증런 유출: M-0352·M-0354 모두 `formal_preview.py`와 `formal.py`를 수리 2 영역에 넣었다. 범위에 들었는데 놓쳤다.
- 가장 싼 포착 시험: 실제 Lean 원출력 하나(수 MB)를 입력으로 사전 검사 출력 함수를 부른다. 출력이 JSON 한 개로 해석되고 크기가 정해진 상한(예: 64KB) 이하임을 단언한다.
- 범주 후보: 판단 입력의 규모 폭주

### C-11 관찰 창 120초가 대표 Mathlib 검사보다 짧음

- 출처: 인스턴스 `config.json`(`self_check_response_window_seconds`와 `tool_review_window_seconds`가 모두 120), `C:\math\임시\do-math_RI-01M3HM0X_해석\원고.md` 6.4절, `C:\math\임시\do-math_개선안_20260928\원고.md` 8절. 수리 커밋 `5ecc321`.
- 발견 경위: 실제 운전
- 영향 등급: 저하. 연구가 정상 진행 중인데도 도구 관찰 창 초과로 운영 점검 계보 2가 열렸다.
- 증상: `import Mathlib` 사전 검사 한 번(`item_6`)이 120초를 넘어 23:40:14에 도구 무응답 관찰(`elapsed_ms 120609`)이 기록됐다.
- 근본 원인: 창 값에 제품 기본값이 없어 시작 대화가 정했다. 툴체인 기록에 대표 컴파일 소요 시간을 보여 주는 안내나 검사도 없었다(`observations.py` 1015~1030행은 호출 종류와 관계없이 고정 창을 쓴다).
- 수정: `5ecc321`. 대표 검사 시간을 요약에 싣고, 창이 그보다 짧으면 채택·등록 때 경고한다. 회귀 시험은 다음 셋이다.
  - `test_environment_validation.test_recorded_summary_reports_the_representative_compile_duration`
  - `test_environment_validation.test_windows_shorter_than_the_representative_compile_are_warned`
  - `test_environment_validation.test_adoption_and_registration_results_return_the_warnings`

  여유 배수는 사용자 결정 미정으로 남았다(M-0357).
- 결함 유형: 문서·계약
- 트리거: 설정·환경, 실제 외부 도구 동작(Mathlib 적재 약 30초 이상)
- 결함 위치 층: 계약·스키마
- 시험 유출 원인: 시험 없음. 설정값과 실제 도구 소요 시간의 관계를 보는 검사가 없었다. 주입 커밋은 해당 없음이다(값의 근거가 처음부터 없었다).
- 검증런 유출: M-0352·M-0354 모두 `references/초기화-운전.md`와 `configuration.py`를 수리 1 영역에 넣었다. 둘 다 동작 결함이 아니라 설정 안내 공백이라 결함 목록 밖으로 보였을 수 있으나, 원자료로는 확인할 수 없다. 범위 안이었다.
- 가장 싼 포착 시험: 툴체인 기록의 대표 검사 시간과 설정의 관찰 창을 입력으로 채택 검사를 부른다. 창이 짧으면 경고가 반환됨을 단언한다.
- 범주 후보: 설정값 근거 부재

### C-12 종결 인스턴스의 과제가 착수 가능으로 표시

- 출처: `C:\math\임시\do-math_RI-01M3HM0X_해석\원고.md` 5절·6.4절, `C:\math\임시\do-math_개선안_20260928\원고.md` 8절. 수리 커밋 `5ecc321`.
- 발견 경위: 실제 운전
- 영향 등급: 저하(잘못된 표시)
- 증상: `closed` 인스턴스에서 과제 2가 `status`에 `active`, 착수 가능 `ready`로 보였다.
- 근본 원인: `reporting.py`의 착수 가능 계산이 인스턴스 종결을 보지 않았다.
- 수정: `5ecc321`. `planning.instance_ended`를 두고 종결 인스턴스의 과제는 readiness를 계산하지 않게 했다. 회귀 시험은 `test_reporting.test_task_rows_of_an_ended_instance_carry_no_readiness`다. 3차 1라운드 R1-56이 이 판정의 사본 여덟 곳을 정본으로 모았다.
- 결함 유형: 검사
- 트리거: 사용자·운영 제어(`close`)
- 결함 위치 층: L2 인터페이스 요소
- 시험 유출 원인: 시험 없음. 주입 커밋은 특정하지 못했다.
- 검증런 유출: M-0352·M-0354 모두 `reporting.py`를 수리 3 영역에 넣었다. M-0354는 엔진 종료 판정 사본 22곳을 `_instance_closed`로 모았지만(R1-64) `reporting.py`의 착수 계산은 대상에 없었다. 범위에 들었는데 놓쳤다.
- 가장 싼 포착 시험: 종결 상태의 인스턴스와 미완료 과제 하나를 입력으로 `task_status`를 부르고, 착수 가능 표시가 없음을 단언한다.
- 범주 후보: 종결 판정 사본

### C-13 입력 초과 기록이 비교에 쓴 예산 대신 전체 상한을 적음

- 출처: `C:\math\임시\do-math_RI-01M3HM0X_해석\원고.md` 4.5절("필수 문맥 411,989바이트 … 한도 500,000"), `C:\math\임시\do-math_개선안_20260928\원고.md` 2.4절(`context_store.py` 650행). 수리 커밋 `5ecc321`.
- 발견 경위: 실제 운전(기록 분석)
- 영향 등급: 저하. 운영자와 연구 계획이 "필수 < 한도인데 초과"라는 모순된 기록을 받았다.
- 증상: 초과 기록의 `limit_bytes`가 전체 상한이라, 필수 문맥이 한도보다 작은데도 필수 초과로 읽혔다.
- 근본 원인: `context_store.py` 650행이 초과 기록의 `limit_bytes`를 전체 상한으로 덮어써, 실제 비교에 쓴 문맥 예산(상한 − 고정 부분)이 기록에 남지 않았다.
- 수정: `5ecc321`. `context_budget_bytes`를 기록한다. 회귀 시험은 `test_context_store.test_role_overflow_records_the_context_budget_it_compared`다.
- 결함 유형: 대입·초기화
- 트리거: 장시간 누적(입력 크기)
- 결함 위치 층: L2 인터페이스 요소
- 시험 유출 원인: 단언 약함. 초과 경로는 여러 시험이 거쳤다(bdccee3 판본 `test_context_store` 등 10개 모듈이 초과 어휘를 쓴다). 그러나 기록된 한도가 실제 비교 값과 같은지는 단언하지 않았다. 주입 커밋은 특정하지 못했다.
- 검증런 유출: M-0352·M-0354 모두 `context_store.py`를 수리 3 영역에 넣었다. 범위에 들었는데 놓쳤다.
- 가장 싼 포착 시험: 고정 부분이 큰 역할로 초과를 일으킨다. 기록의 `필수 바이트 > 기록된 예산` 관계가 항상 성립함을 단언한다.
- 범주 후보: 기록과 판정 기준의 어긋남

### C-14 형식 결과 원출력 5.38MB를 그대로 보존

- 출처: `C:\math\임시\do-math_RI-01M3HM0X_해석\원고.md` 6.4절, `C:\math\임시\do-math_개선안_20260928\원고.md` 7.1·7.2절 C5. 수리 커밋 `5ecc321`.
- 발견 경위: 실제 운전(기록 분석)
- 영향 등급: 저하. 487B 원문 하나의 형식 검사가 저장소에 5.38MB를 쌓았고, C-02의 원인이 됐다.
- 증상: 형식 결과 기록이 검사 표준 출력 5,381,117B를 payload로 보존했다. 그 가운데 의존 행 603줄이 4.28M자였다.
- 근본 원인:
  - 선언별 중복: `dependency_evidence`를 선언마다 복제했다(`formal.py` 593행).
  - 원출력 이중 보존: 이미 해시로 줄인 의존 본문 행을 원출력에도 그대로 남겼다.
- 수정: `5ecc321`. 폐포 합집합 `{상수: sha256}` 표 하나로 정규화하고, verified 원출력에서 의존 본문 행을 뺐다(사용자 결정). 회귀 시험은 다음 넷이다.
  - `test_formal.test_dependency_bodies_are_one_table_shared_by_the_declared_closures`
  - `test_formal.test_verified_output_omits_dependency_body_rows_reduced_to_hashes`
  - `test_knowledge.test_dependency_body_evidence_is_one_hash_table_over_the_declared_closures`
  - `test_knowledge.test_transition_targets_store_the_dependency_hash_table`
- 결함 유형: 알고리즘
- 트리거: 실제 외부 도구 동작
- 결함 위치 층: L2 인터페이스 요소(형식 결과 기록)
- 시험 유출 원인: 합성 입력이 실제와 다름(C-01의 픽스처 규모). 주입 커밋은 특정하지 못했다.
- 검증런 유출: M-0352·M-0354 모두 `formal.py`(수리 2)와 `knowledge_records.py`(수리 3)를 범위에 넣었다. 범위에 들었는데 놓쳤다.
- 가장 싼 포착 시험: 실제 Lean 출력 하나로 형식 결과 기록을 만들고, 기록 바이트가 원문 바이트와 선언 수의 선형 상한(예: 선언당 폐포 크기 × 상수) 안임을 단언한다.
- 범주 후보: 판단 입력의 규모 폭주

### C-15 형식 검사 직전 판본 불일치가 환경 대기 대신 연구 재평가로 감

- 출처: `C:\math\임시\do-math_검증_20260927\기각보관\do-math-20260927-라운드1.md` R1-28 절(영향), `C:\math\임시\do-math_검증_20260927\장부.md` 25행. 주입 커밋 `8d2ffd0`(항목 영향 칸), 수리 커밋 `bdccee3`.
- 발견 경위: 검증런(안정화 검증 R1-28, 관점 5). 심사는 문서 조각 때문에 1/3으로 기각했고, 세션이 코드 조각을 반영했다.
- 영향 등급: 정지. 스킬을 갱신하거나 실행 파일·DLL·Lake 입력이 바뀌면 형식 검사가 `research_plan`으로 가고, 같은 형식 검사를 다시 넣으면 같은 거부가 되풀이된다. `formal_environment` 대기가 없으므로 새 기록으로 전환해도 `_resume_environment_waits`가 다시 배정하지 않는다(항목 영향 칸).
- 증상: 운전 미발현
- 근본 원인: `8d2ffd0`가 판본 식별 확인을 `verify_formal`의 사전 검사(`identity=False`)에서 `verify_lean` 안으로 옮겼다. 그런데 `verify_lean`의 거부 반환(`formal.py` 474·479행)에는 `error_kind='trust_environment'`가 없다. 소비자 `formal_engine.py` 437~444행은 이 표지로 환경 대기와 연구 재평가를 가른다. 게시 관문(`trust_validation.require_active_environment`)은 같은 불일치를 `EnvironmentUnavailable`로 다룬다.
- 수정: `bdccee3`. `formal.py`의 두 반환에 `error_kind: trust_environment`를 더했다. 시험은 `test_execution_profiles.py` 652·669행 근처의 두 시험에 `error_kind` 단언을 더했다(새 시험 이름 없음).
- 결함 유형: 인터페이스
- 트리거: 재시작·복구·재개(스킬 갱신으로 설치본 확인이 실행기를 재시작)와 설정·환경(툴체인 파일 교체)
- 결함 위치 층: L2 인터페이스 요소(형식 결과 분류)
- 시험 유출 원인: 단언 약함. `verify_lean`을 직접 부르는 시험 다섯(`test_execution_profiles.py` 651·669행, `test_knowledge.py` 607행, `test_knowledge_import_engine.py` 326행, `test_formal.py` 104행)이 `status`와 `reason`만 단언해, 분류 표지의 부재를 판별하지 못했다(항목 영향 칸). 대기 분기 시험(`test_lifecycle_engine.py` 373~381행)은 지문 불일치 경로만 거쳤다.
- 검증런 유출: 이 기간 첫 검증런이 찾았다. 이전 기간의 검증런은 담당 밖이다.
- 가장 싼 포착 시험: `verify_lean`이 판본 식별 오류로 거부하는 경우 전부(명령 경로 불일치, 식별 오류 목록)에 대해 결과를 형식 엔진의 분류 함수에 넣는다. 결과가 `formal_environment` 대기임을 단언하는 표 시험이다. 더 일반적으로는 "환경 원인 거부는 모두 같은 분류로 간다"는 성질을 모든 거부 생산자에 대해 단언한다.
- 범주 후보: 탈출 경로 없는 대기(같은 규칙의 두 사본과도 겹친다)

### C-16 정비 fence 아래 `run`이 `UnboundLocalError`로 사망

- 출처: `C:\math\임시\do-math_검증_20260927-2\장부.md` 51행(R1-01), 같은 런 `종료보고.md` 70행. 주입 커밋 `ff9b2b9`, 수리 커밋 `8af1f5e`.
- 발견 경위: 검증런(전면 검증 2차 R1-01)
- 영향 등급: 정지. 실행기가 JSON 봉투 없이 비정상 종료한다.
- 증상: 운전 미발현
- 근본 원인: `scheduler._run_parallel`의 루프 안에서, 정비 fence 분기가 `break`로 빠져나간 뒤에야 `from .repair_execution import pending_installation_repair`가 실행되는 자리에 있었다. 루프 뒤 정산이 이 이름을 읽는다(bdccee3 판본 308·320·391행). fence 분기는 `ff9b2b9`에서 import 앞에 생겼다. `ff9b2b9` 판본 504·516행에서 확인했다. 바로 앞 커밋 `ded5952`에는 fence 분기가 없다.
- 수정: `8af1f5e`. import를 루프 앞으로 옮겼다. 회귀 시험은 `test_session_scheduler.test_run_that_starts_under_a_maintenance_fence_returns_without_an_execution`이다.
- 결함 유형: 대입·초기화
- 트리거: 사용자·운영 제어(`quiesce`로 정비 fence 설정)와 특정 전이 순서(fence가 선 채로 `run` 시작)
- 결함 위치 층: L3 배선(엔진 실행 루프)
- 시험 유출 원인: 시험 없음. 주입 시점의 fence 시험(`ff9b2b9` 판본 `test_initialization_efficiency.py` 206~226행)은 `engine_start_guard`가 기동을 거절하는지만 단언했고, fence 아래에서 `run` 루프를 실제로 돌리지 않았다.
- 검증런 유출: M-0352(앵커 85a540c)는 `scheduler.py`를 수리 1 영역에 넣었다. 범위에 들었는데 놓쳤다. M-0354가 찾았다.
- 가장 싼 포착 시험: fence가 선 상태를 입력으로 `run`을 한 번 부르고, 예외 없이 JSON 결과를 돌려주며 실행이 생기지 않음을 단언한다. 일반화하면 "소유 루프의 모든 탈출 분기(fence, 정지, 종결, 설치 복구)마다 `run`이 정상 반환한다"는 표 시험이다.
- 범주 후보: 소유 루프 예외 사망

### C-17 허가 질문의 `question_kind`가 닫힌 저장 스키마에 없음

- 출처: `C:\math\임시\do-math_검증_20260927-2\장부.md` 74행(R1-24), 같은 런 `종료보고.md` 71행, 커밋 `8af1f5e`의 `record_schemas/schemas.py` diff(`"question_kind": enum("grant")` 추가). 주입 커밋 `7d2597e`, 수리 커밋 `8af1f5e`.
- 발견 경위: 검증런(전면 검증 2차 R1-24)
- 영향 등급: 정지. 허가 없는 외부 요청을 사용자 질문으로 보존하는 순간 상태 게시가 스키마 위반으로 거부된다. 저장이 거부되면 상태가 전진하지 못한다.
- 증상: 운전 미발현
- 근본 원인: `engine._apply_extensions`가 질문 연결에 `question["question_kind"] = "grant"`를 쓴다(bdccee3 판본 `engine.py` 3504행). 그러나 `RECORDS["question_links"]`는 이 필드를 선언하지 않은 닫힌 객체였다. `question_kind`의 생산은 `98ac7e5`(2026-09-19)부터 있었고, 닫힌 저장 스키마 패키지는 `7d2597e`에서 처음 추가됐다(`schemas.py`의 `git log --diff-filter=A`). 그 뒤 어느 판본의 스키마에도 이 필드가 없었다.
- 수정: `8af1f5e`. 스키마에 `question_kind: enum("grant")`를 더했다. 회귀 시험은 `test_family_records.test_grant_question_kind_survives_storage`다.
- 결함 유형: 스키마·계약 불일치
- 트리거: 실제 모델 출력 형태(작업자가 `grant_id` 없는 외부 요청을 확장에 씀)
- 결함 위치 층: L2 인터페이스 요소
- 시험 유출 원인: 시험 없음. bdccee3 판본 시험 가운데 `external_requests`를 쓰는 곳은 `purpose_fixtures.py` 459행 하나이고, 이 픽스처는 늘 `grant_id`를 채운다. 허가 없는 분기는 어떤 시험도 거치지 않았다.
- 검증런 유출: M-0352는 `engine.py`(수리 2)와 `schemas.py`(수리 3)를 범위에 넣었다. 범위에 들었는데 놓쳤다. M-0354가 찾았다.
- 가장 싼 포착 시험: C-03과 같은 "생산자가 쓰는 키 ⊆ 닫힌 스키마 properties" 표 시험이다. 동적으로는 `grant_id` 없는 외부 요청 하나를 담은 확장을 적용한 뒤 `_save`를 실제 저장 계약으로 실행해 성공함을 단언한다.
- 범주 후보: 생산자 필드와 닫힌 스키마의 어긋남

### C-18 `formal_authority`·`formal_stopped` 대기에 재개 경로 없음

- 출처: `C:\math\임시\do-math_검증_20260928\기각보관\do-math-20260928-라운드1.md` R1-08 절(영향), `C:\math\임시\do-math_검증_20260928\장부.md` 76행과 운영 기록(구현 에이전트가 기각 사유를 해소해 반영). 수리 커밋 `1a8ce7a`.
- 발견 경위: 검증런(전면 검증 3차 1라운드 R1-08). 심사 2/3이었고 시험 도우미 배치 문제로 기각된 뒤 직접 처리로 반영됐다.
- 영향 등급: 정지. 이 두 대기에 들어간 형식 검사는 다시 돌지 않는다. 후보에 형식 결과가 생기지 않고 동일성 검토도 열리지 않는다. 사용자에게는 이를 풀 제어가 없다(항목 영향 칸).
- 증상: 운전 미발현
- 근본 원인: `_formal_steps`는 `waiting_actions`에 `formal_authority`와 `formal_stopped` 대기를 만든다. 그런데 대기를 다시 큐로 돌리는 경로 여섯 가운데 이 두 종류를 받는 것이 없다. `_resume_environment_waits`는 `formal_environment`만 받는다. 재현 경로는 셋이다(항목 영향 칸).
  1. 신뢰 전환이 `ready`인 동안 형식 검사가 배정된다.
  2. 무효화 뒤 새 환경을 등록하기 전에 형식 검사가 배정된다.
  3. 컴파일 중 입력이나 권한이 바뀐다.
- 수정: `1a8ce7a`. `_resume_formal_waits`로 세 종류를 재개한다. 회귀 시험은 `test_formal_engine.test_parked_check_returns_to_the_queue_once_an_environment_and_authority_admit_it`와 `test_only_a_check_stopped_by_changed_conditions_resumes`다.
- 결함 유형: 기능
- 트리거: 특정 전이 순서(전환 `ready` 중 배정)와 사용자·운영 제어(허가 변경)
- 결함 위치 층: L2 인터페이스 요소(대기 해소 규칙)
- 시험 유출 원인: 시험 없음. 재개 경로 시험(`test_formal_engine.py` 143~164행, `test_machine_parallel.py` 175·180행)은 `formal_environment`만 다뤘다.
- 주입 커밋: 특정하지 못했다. 두 대기는 `7d2597e` 판본부터 생성됐고(`git log -S "formal_authority"`), 한 종류만 다루는 재개 함수는 `8d2ffd0`에서 `recheck` 삭제와 함께 생겼다. `8d2ffd0` 전에 두 대기를 푸는 경로가 있었는지는 확인하지 않았다.
- 검증런 유출: M-0352와 M-0354는 `formal_engine.py`를 수리 2 영역에 넣었다. M-0352의 관점 5는 `8d2ffd0` diff 전체를 필수 독해로 받았다(동결 696행). 두 런 모두 범위에 들었는데 놓쳤다. M-0352는 바로 옆의 R1-28(C-15)을 찾았다.
- 가장 싼 포착 시험: 코드에서 `waiting_actions`의 모든 `kind` 생성 지점을 모은다. 각 `kind`마다 그 대기를 재큐하는 함수가 하나 이상 있음을 단언하는 정적 표 시험이다. 동적 확인은 전환 `ready` 중 형식 검사를 배정하고, 전환을 활성화한 뒤 스케줄러 한 바퀴에서 그 검사가 다시 큐에 들어감을 단언한다.
- 범주 후보: 탈출 경로 없는 대기

### C-19 신뢰 재검사가 배정 관문과 달리 grant를 요구해 정지

- 출처: `C:\math\임시\do-math_검증_20260928\장부.md` 217행(R2-01), 운영 기록의 최종 확인 1차 실패 분석, 커밋 `3552607`의 `formal_engine.py` diff(`should_stop`의 `authorize` 제거)와 `test_lifecycle_engine.py` 추가 시험. 수리 커밋 `3552607`.
- 발견 경위: 검증런(전면 검증 3차 2라운드 R2-01)
- 영향 등급: 정지. 문서(`초기화-운전` 3절)가 안내하는 연구 grant는 연구 역할과 `formal_check`만 이름으로 가진다. 그런 grant 아래에서 신뢰 전환의 재검사가 스스로 멈추고 인스턴스를 정지시킨다(장부 요지, 3552607 시험 주석).
- 증상: 운전 미발현
- 근본 원인: 배정 관문(`lifecycle_engine`)은 `trust_check`·`trust_activate`를 grant 권한 판정에서 뺀다. 반면 재검사의 정지 판단(`formal_engine._trust_check_steps`의 `should_stop`)은 `authorize()`를 요구했다. 같은 권한 규칙이 두 곳에서 다르게 적혀 있었다. `should_stop`의 `authorize` 줄은 `git log -S` 기준으로 `7d2597e`에 있었고 `85a540c`이 옮겼다. 주입 커밋은 `7d2597e`로 판단한다(그 전 판본은 찾지 않았다).
- 수정: `3552607`. `should_stop`에서 grant 확인을 지웠다. 회귀 시험은 `test_lifecycle_engine.test_trust_recheck_needs_no_grant_naming_the_trust_roles`다. 옛 불일치를 단언하던 시험은 `test_machine_parallel.test_revoking_research_grants_does_not_stop_a_trust_check`로 바꿨다.
- 결함 유형: 검사
- 트리거: 사용자·운영 제어(문서대로 만든 grant)와 재시작·복구·재개(신뢰 전환)
- 결함 위치 층: L2 인터페이스 요소(허가 판정)
- 시험 유출 원인: 합성 입력이 실제와 다름. 시험 픽스처의 grant는 신뢰 역할을 포함했다. 새 회귀 시험은 픽스처 grant에서 `trust_check`·`trust_activate`를 지워야 결함을 재현했다(3552607 `test_lifecycle_engine.py` 351~360행). 더해 기존 시험 `test_trust_revoked_authority_rejects_late_result`는 옛 불일치를 기대값으로 단언했다(장부 운영 기록).
- 검증런 유출: M-0352·M-0354·3차 1라운드 모두 `formal_engine.py`와 `lifecycle_engine.py`를 범위에 넣었다. 세 번 범위에 들었는데 놓쳤다.
- 가장 싼 포착 시험: 문서의 grant 예시를 그대로 파싱해 grant로 쓰는 시작 상태에서 신뢰 전환을 끝까지(`trust_check` 두 번, `trust_activate`) 돌린다. 환경이 활성화됨을 단언한다. 일반화하면 "각 역할에 대해 배정 관문의 허가 판정과 실행 중 정지 판정이 같은 값"이라는 표 시험이다.
- 범주 후보: 같은 규칙의 두 사본

### C-20 설치 복구 1회 제한이 판정 못 한 호출까지 세어 영구 차단

- 출처: `C:\math\임시\do-math_검증_20260928\기각보관\do-math-20260928-라운드2.md` R2-07 절(영향), `장부.md` 223행과 운영 기록(수리를 판정한 보류 호출은 계속 세도록 좁혀 반영). 주입 커밋 `7d2597e`, 수리 커밋 `3552607`.
- 발견 경위: 검증런(전면 검증 3차 2라운드 R2-07). 심사 2/3이었고, `recovery_verification_failed` 뒤의 보류까지 제외한다는 이유로 기각된 뒤 직접 처리로 좁혀 반영됐다.
- 영향 등급: 정지. 진단된 설치 결함이면 `pending_installation_repair`가 남아 스케줄러가 새 배정을 멈춘다. 실행기 시작 실패이면 복구만 반복한다. 사람이 설치 파일이나 실패 식별을 바꾸기 전까지 같은 반환이 반복된다(항목 영향 칸).
- 증상: 운전 미발현
- 근본 원인: 1회 제한을 "같은 `repair_identity`를 가진 recovery 실행이 있는가"로만 판정해, 수리 판정에 이르지 못한 호출까지 한 번으로 셌다(`scheduled_operator.py` 500~505행). 공급자 한도로 거절된 호출(`provider_limit` → `recovery_failed`)과 HOLD·정지로 보류된 호출(`recovery_held`)이 여기에 든다. 문구 "same failure and installation already attempted"와 `repair_identity`는 `7d2597e`에서 처음 나타난다.
- 수정: `3552607`. 공급자 한도는 `recovery_provider_limited`로 구별하고, 판정 못 한 호출은 세지 않는다. 회귀 시험은 `test_diagnosed_installation_recovery.test_a_provider_refused_or_held_call_does_not_use_up_the_one_repair`와 `test_a_judged_repair_counts_once_even_when_a_hold_holds_its_result`다.
- 결함 유형: 검사
- 트리거: 실제 외부 도구 동작(공급자 한도), 사용자·운영 제어(HOLD), 재시작·복구·재개
- 결함 위치 층: L2 인터페이스 요소(설치 복구 판정)
- 시험 유출 원인:
  - 조합·순서 미탐색: `test_diagnosed_installation_recovery.py` 110~122행은 공급자 한도 호출의 첫 결과만 봤다. 같은 실패로 다시 부르는 두 번째 호출은 시험하지 않았다.
  - 단언 약함(결함 고정): 116행이 `recovery_failed`를 기대값으로 단언했다(항목 영향 칸).
- 검증런 유출: M-0352·M-0354·3차 1라운드 모두 `scheduled_operator.py`를 범위에 넣었다(1·2차는 수리 1 영역). 3차 1라운드는 같은 함수의 활동 소유 키(R1-11)를 고쳤다. 세 번 범위에 들었는데 놓쳤다.
- 가장 싼 포착 시험: 복구 호출 대역이 한 번은 `provider_limit`, 다음은 정상 결과를 돌려주게 한다. 같은 실패로 `recovery`를 두 번 부르고, 두 번째에 모델이 호출됨을 단언한다. HOLD 경우도 같은 모양으로 subTest를 둔다.
- 범주 후보: 한도·계수의 잘못된 소진

### C-21 `deadline_only` 관찰 입력 반려의 `followup: None`으로 엔진 사망

- 출처: `C:\math\임시\do-math_검증_20260928\장부.md` 232행(R2-16), 커밋 `3552607`의 `observations.py` diff와 `test_live_observation.py` 추가 시험. 주입 커밋 `7d2597e`, 수리 커밋 `3552607`.
- 발견 경위: 검증런(전면 검증 3차 2라운드 R2-16)
- 영향 등급: 정지. 엔진의 관찰 적용이 `AttributeError`로 멈춘다(장부 요지).
- 증상: 운전 미발현
- 근본 원인: 관찰 입력 반려 행이 `deadline_only` 모드에서 `"followup": None`을 실었고, 엔진 소비자는 `followup`이 있으면 dict로 읽었다. 반려 행 생산 코드 `if self.mode != "deadline_only" else None`은 `7d2597e`에서 처음 나타난다(`git log -S`).
- 수정: `3552607`. `deadline_only`이면 `followup` 키를 넣지 않는다. 회귀 시험은 `test_live_observation.test_rejected_input_of_a_deadline_only_execution_is_recorded_without_a_review`다.
- 결함 유형: 대입·초기화
- 트리거: 실제 모델 출력 형태 또는 외부 도구 동작(형식이 틀린 관찰 사건)과 설정·환경(`deadline_only` 관찰 방식)
- 결함 위치 층: L2 인터페이스 요소(관찰 적용)
- 시험 유출 원인: 시험 없음. bdccee3 판본에서 `deadline_only` 추적기를 쓰는 시험 다섯(`test_checkpoint_persistence.py` 125행, `test_family_records.py` 847행, `test_live_observation.py` 221·498행 등)은 모두 정상 사건만 넣었다. 반려 경로를 엔진 적용까지 거친 시험이 없었다.
- 검증런 유출: M-0352·M-0354·3차 1라운드 모두 `observations.py`와 `engine.py`를 범위에 넣었다. 세 번 범위에 들었는데 놓쳤다.
- 가장 싼 포착 시험: 관찰 방식 셋(`event_driven`, `periodic`, `deadline_only`) × 잘못된 사건 하나의 조합마다 `engine._observe_running`을 부르고 예외가 없음을 단언하는 표 시험이다. 사건 입력을 무작위로 만드는 속성 시험으로 넓힐 수 있다.
- 범주 후보: 소유 루프 예외 사망

### C-22 목표 판정 무효화의 `invalidated_reason`이 스키마에 없어 이후 저장 전부 거부

- 출처: `C:\math\임시\do-math_검증_20260928\기각보관\do-math-20260928-라운드2.md` R2-24 절(영향), `장부.md` 240행과 운영 기록(`적용 --추가`로 반영). 주입 커밋 `7d2597e`, 수리 커밋 `3552607`.
- 발견 경위: 검증런(전면 검증 3차 2라운드 R2-24). 심사 0/3이었고, 사유는 조각 좌표 형식뿐이었다.
- 영향 등급: 정지. 목표 근거가 한 번 바뀐 인스턴스는 어떤 상태도 더 게시하지 못한다. 무효화 함수가 매 준비 갱신마다 불리기 때문이다(항목 영향 칸).
- 증상: 운전 미발현
- 근본 원인: `knowledge_engine._invalidate_goal_currentness`가 목표 판정에 `invalidated_reason`을 쓰는데, `RECORDS["goal_judgments"]`는 이를 선언하지 않은 닫힌 객체였다. 주입 시점 `7d2597e` 판본에서 목표 판정 스키마(`schemas.py` 208~210행과 `domains.py` 44~48행)에 이 필드가 없었다. 379a171가 스키마 파일을 합칠 때도 더하지 않았다(`379a171` 판본 `schemas.py` 530~537행).
- 수정: `3552607`. 선택 필드 `invalidated_reason: TEXT`를 더했다. `test_currentness.py`의 기존 무효화 시험(380~409행 근처)에 저장 계약 단언을 더했다(새 시험 이름 없음).
- 결함 유형: 스키마·계약 불일치
- 트리거: 특정 전이 순서(`mathematically_solved` 뒤 근거 변경)와 장시간 누적(매 갱신 재기록)
- 결함 위치 층: L2 인터페이스 요소
- 시험 유출 원인: 단언 약함. 주입 시점 `7d2597e` 판본 `tests/test_feature2_migration.py` 135~138행은 `_invalidate_goal_currentness()` 뒤 메모리 상태(`judgment['current']`, `goal_status`)만 단언하고 저장 계약을 거치지 않았다. bdccee3 판본 `test_currentness.py` 406~409행도 같았다(항목 영향 칸).
- 검증런 유출: M-0352·M-0354·3차 1라운드 모두 `schemas.py`와 `knowledge_engine.py`를 범위에 넣었다. M-0354는 같은 기제의 C-17을 같은 파일에서 찾았다. 네 번째 라운드에서야 찾았다.
- 가장 싼 포착 시험: C-03·C-17과 같은 "생산자 키 ⊆ 닫힌 스키마" 표 시험이다. 동적으로는 무효화 직후 `StateContract.validate`를 실행해 오류가 없음을 단언한다.
- 범주 후보: 생산자 필드와 닫힌 스키마의 어긋남

### C-23 공유 `TEXT` 노드 제자리 `enum`으로 보충 조사 제출 전건 거부

- 출처: `C:\math\기억\layer1\M-0350.md` 「2라운드 검증」의 제품 결함 1건, 커밋 `9b434f4`의 `review_engine.py` diff(1140행 근처 `schema['properties'][…]['enum'] = …` → 사본에 설정). 주입 커밋 `379a171`, 수리 커밋 `9b434f4`.
- 발견 경위: 시험 실행(시험 경량화 작업이 main 판본 전체를 돌렸을 때 드러난 68개 실패 가운데 하나)
- 영향 등급: 정지. 실제 보충 조사 제출이 전부 거부됐다(M-0350). 필수 역할 출력의 전건 거부다.
- 증상: 운전 미발현(이 기간에 운전 없음)
- 근본 원인: `379a171`이 `review_cycle.research_schema`의 모든 필드가 `TEXT` 노드 하나를 공유하게 바꿨다. 그런데 `review_engine._review_research_schema`가 그 노드에 `enum`을 제자리에서 설정해, 모든 문자열 필드가 요청 다이제스트 하나로 제한됐다. 제자리 설정 자체는 `3d7b280`(09-14)부터 있었다(`git log -S "def _review_research_schema"`). 결함은 379a171의 노드 공유와 결합하면서 활성화됐다.
- 수정: `9b434f4`. 생산 쪽과 소비 쪽을 모두 고치고 대조 단언을 더했다(M-0350, 시험 이름은 기록에 없다). 구조적 재발 방지로 `85a540c`이 `test_schema_builders_return_copies_that_share_no_node`를 더했다(REV-23).
- 결함 유형: 대입·초기화
- 트리거: 실제 모델 출력 형태(보충 조사의 문자열 필드)
- 결함 위치 층: L1 원시(스키마 빌더)
- 시험 유출 원인:
  - 단언 약함: 기존 거부 시험은 "이슈가 하나라도 있으면" 통과하는 단언이라 잡지 못했다(M-0350).
  - 시험 미실행: 주입 커밋 `379a171`에서는 사용자 결정으로 시험을 실행하지 않았다(M-0349 「결정」 시험 항). 확인은 `py_compile`, import, 미러, `probe_cli`뿐이었다. 다음 작업이 시험을 돌리자 드러났다. 이 사정은 서식 값에 없어 관찰 7에 적는다.
- 검증런 유출: 해당 없음. 이 기간 첫 검증런(M-0352) 전에 발견·수리됐다.
- 가장 싼 포착 시험: 스키마 빌더를 두 번 부르고, 첫 결과에 `enum`을 설정한 뒤 두 번째 결과와 모듈 전역 노드가 바뀌지 않았음을 단언한다(공유 노드 부재 속성). 동작 확인으로는 정상 보충 조사 출력 하나가 검사를 통과하고 이슈가 0개임을 단언한다.
- 범주 후보: 공유 스키마 노드 변이

### C-24 `ModelCalls` 펌프가 관찰 행을 상한 없이 비워 소유 루프 고착

- 출처: `C:\math\기억\layer1\M-0350.md` 「2라운드 검증」의 제품 활성 결함 1건, 커밋 `9b434f4`의 `parallel.py` diff(`while future.observations:` → 진입 시점 행 수만큼). 주입 커밋 `8d2ffd0`, 수리 커밋 `9b434f4`.
- 발견 경위: 시험 실행(C-23과 같은 전체 실행)
- 영향 등급: 정지. 실행 중인 호출이 관찰 행을 계속 덧붙이면 소유 루프가 그 호출에 묶여 배정·실시간 검토·제어를 처리하지 못한다(수리 커밋 주석).
- 증상: 운전 미발현
- 근본 원인: `_apply_observations`가 `while future.observations:`로 큐를 끝까지 비웠다. `while future.observations:`는 `8d2ffd0`에서 처음 나타난다(`git log -S`). 이 커밋은 소유 루프의 바쁜 폴링을 사건 기반 대기(`ModelCalls.wait`)로 바꿨다.
- 수정: `9b434f4`. 진입 시점에 쌓인 행만 적용한다. 회귀 시험은 `test_machine_parallel.test_one_pump_applies_only_the_rows_queued_before_it`다.
- 결함 유형: 타이밍·직렬화
- 트리거: 동시성·경합(작업 스레드의 연속 관찰 추가)과 장시간 누적
- 결함 위치 층: L3 배선(소유 루프와 작업 스레드)
- 시험 유출 원인: 확인 불가. `8d2ffd0`의 전체 실행(M-0348)은 실패 28개를 분류했고, 그 가운데 `ParallelEngineTests` 5개를 기존 결함으로 분류했다. 이 결함이 그 안에 가려졌는지, 경로가 시험되지 않았는지는 원자료로 가를 수 없다.
- 검증런 유출: 해당 없음. 이 기간 첫 검증런 전에 수리됐다.
- 가장 싼 포착 시험: 관찰 행을 무한히 덧붙이는 가짜 호출 하나와 대기 중인 제어 요청 하나를 둔다. 소유 루프 한 바퀴가 유한 시간 안에 돌아와 제어를 처리함을 단언한다. 진행성(liveness) 속성의 시험이다.
- 범주 후보: 소유 루프 기아

### C-25 신뢰 환경 조건 문법의 상태값이 실제와 달라 `candidate` 조건이 영원히 거짓

- 출처: `C:\math\임시\do-math-정리-검토-2026-09-27\보고서.md` 74행(RES-02), `검증\통합표.md` RES-02 행과 247행(이력 정정), 커밋 `85a540c`의 `planning.py` diff(`'trust-environment': {'candidate','active','invalid','superseded'}` 제거). 주입 커밋 `7d2597e`, 수리 커밋 `85a540c`.
- 발견 경위: 정적 검토(전면 정리 검토, 재현 확인)
- 영향 등급: 정지. 과제가 `candidate` 상태의 신뢰 환경을 기다리는 조건을 가지면 그 조건은 영원히 참이 되지 않아 과제가 끝없이 대기한다. `registered`를 기다리는 조건은 제출 때 거부된다(저하 쪽 발현).
- 증상: 운전 미발현
- 근본 원인: 조건 문법의 상태값 집합이 실제 상태값·스키마와 어긋났다. `7d2597e` 판본 `domains.py` 70행의 스키마는 `registered`를 포함하고, 문법은 `candidate`를 썼다. 조건 문법 줄은 `git log -S`에서 `7d2597e`에 처음 나타난다. 통합표 정정에 따르면 어긋남은 8d2ffd0 전부터 있었고, 8d2ffd0는 스키마만 고치고 문법을 남겼다.
- 수정: `85a540c`(RES-01·RES-02, 상수화). 회귀 시험 이름은 확인하지 않았다(`85a540c`은 시험 모듈 재편이 커 추가 시험 이름으로 특정하지 못했다).
- 결함 유형: 스키마·계약 불일치
- 트리거: 실제 모델 출력 형태(연구 계획이나 준비가 신뢰 환경 조건을 씀)
- 결함 위치 층: L2 인터페이스 요소(조건 문법)
- 시험 유출 원인: 시험 없음. 신뢰 환경 조건을 실제 상태 전이와 함께 평가한 시험의 존재를 원자료에서 찾지 못했다. 검토 보고서는 재현으로 확인했다고만 적는다.
- 검증런 유출: 해당 없음. 이 기간 첫 검증런 전에 수리됐다.
- 가장 싼 포착 시험: 조건 문법의 가족별 상태값 집합과 저장 스키마 `enum`이 같은지 단언하는 표 시험이다. 동적으로는 상태 전이 기계가 도달하는 모든 상태에 대해 해당 조건이 한 번은 참이 됨을 단언한다.
- 범주 후보: 탈출 경로 없는 대기(생산자·수신자 어휘 불일치와 겹친다)

### C-26 시작 전에 정지된 형식 검사가 종료 장벽에 보류

- 출처: `C:\math\임시\do-math-정리-구현-2026-09-27\결과-ENG.md` 110·133·146행, `C:\math\기억\layer1\M-0351.md` 「결과」. 수리 커밋 `85a540c`.
- 발견 경위: 정적 검토. 형식 검사 종료 처리를 통일하는 구현(ENG-08) 중 드러났다.
- 영향 등급: 정지. 검사가 `stopping`, `local_termination=unknown`으로 종료 장벽에 보류됐다(결과-ENG 133행). 발사표를 반환 표시하지 않아 용량이 돌아오지 않는 상태다.
- 증상: 운전 미발현
- 근본 원인: 옛 형식 검사 종료가 `mark_returned` 없이 `release_or_hold`를 불렀다(결과-ENG 146행).
- 주입 커밋: 특정하지 못했다. `release_or_hold`는 `git log -S`에서 `379a171`에 처음 나타난다. 그러나 형식 검사 종료 경로가 그 커밋부터 이 함수를 불렀는지는 확인하지 않았다.
- 수정: `85a540c`. `_end_machine_execution` 하나로 통일했다. 회귀 시험은 `test_connection_repairs.FormalContinuationTests.test_check_stopped_before_start_ends_and_returns_its_capacity`다(결과-ENG 110행. 수리 전 형태로 되돌리면 `('stopping', 'unknown') != ('ended', 'confirmed')`로 실패함을 확인했다고 적혀 있다).
- 결함 유형: 기능
- 트리거: 특정 전이 순서(형식 검사 배정 → 컴파일 시작 전 정지)
- 결함 위치 층: L3 배선(기계 실행 수명)
- 시험 유출 원인: 시험 없음. 수리 커밋이 재현 시험을 새로 더했다.
- 검증런 유출: 해당 없음. 이 기간 첫 검증런 전에 수리됐다.
- 가장 싼 포착 시험: 기계 실행 종류마다(형식 검사, 신뢰 검사, 외부 작업) "시작 전 정지"를 일으키고, 실행이 `ended`, 종료 확인 `confirmed`, 용량 반환 상태로 끝남을 단언하는 표 시험이다.
- 범주 후보: 탈출 경로 없는 대기

### C-27 제어 전송 영수증 조회가 다른 전송의 영수증을 먼저 찾아 `pump`가 예외

- 출처: `C:\math\임시\do-math-정리-구현-2026-09-27\결과-병합IO.md` 89~104·124~128행, `C:\math\기억\layer1\M-0351.md` 「결과」. 주입 커밋 `7d2597e`, 수리 커밋 `85a540c`.
- 발견 경위: 시험 실행. 병합 뒤 시험 `test_control_transport_io.…test_request_id_rejected_without_engine_record_stays_taken_in_every_transport`가 약 절반의 확률로 실패했다.
- 영향 등급: 정지. 다른 전송이 같은 요청 ID를 재사용해 거부된 뒤, 원래 전송의 정당한 재전달이 `pump` 밖으로 `ValueError("request_id was already received with different content")`를 던진다(결과-병합IO 97·102행). `pump`는 소유 루프의 제어 처리에서 불린다. 이 예외가 실행기를 끝내는지는 원자료가 직접 적지 않는다. 결과-병합IO는 이를 제품 결함으로 판정했다.
- 증상: 운전 미발현
- 근본 원인: `_receipt`가 요청을 보낸 전송 자신의 outbox를 먼저 보지 않고, 모든 outbox에서 처음 찾은 영수증을 돌려줬다. `9b434f4` 판본 `control_transport.py` 480~488행은 `glob("*/outbox/" + request_id + ".json")`의 첫 결과를 쓴다. 전송 ID는 무작위이고 `pump`는 ID 정렬 순서로 처리하므로, 결과가 순서에 따라 갈린다. 예외 문구와 glob 조회는 `7d2597e`에서 처음 나타난다.
- 수정: `85a540c`. 요청을 보낸 전송 자신의 outbox를 먼저 조회한다(M-0351). 회귀 시험은 위 시험이다. 결과-병합IO는 두 순서를 모두 강제하면 결정적이 된다고 적었다. 수리 뒤 시험이 두 순서를 강제하는지는 확인하지 않았다.
- 결함 유형: 알고리즘
- 트리거: 동시성·경합(여러 전송)과 특정 전이 순서(재사용 거부 → 원 전송 재전달)
- 결함 위치 층: L3 배선(제어 수송)
- 시험 유출 원인: 조합·순서 미탐색. 전송 ID가 무작위라 한 순서만 우연히 시험됐다. IO 작업자의 인계 확인(`io-r3`)은 운 좋게 통과했다(결과-병합IO 101행).
- 검증런 유출: 해당 없음. 이 기간 첫 검증런 전에 수리됐다.
- 가장 싼 포착 시험: 전송 ID 두 개를 고정해 두 정렬 순서를 모두 강제한다. 각 순서에서 "타 전송 재사용 거부 → 원 전송 재전달"을 수행하고, `pump`가 예외 없이 원 영수증을 재생함을 단언한다.
- 범주 후보: 소유 루프 예외 사망

## 4. 관찰

### 1. 사용자 관찰 ①: 검증런이 반복해서 정지급 결함을 찾았는가

**사실.** 이 기간 검증런마다 정지급 결함이 나왔다.

- 안정화 검증(M-0352): 1건(C-15)
- 전면 검증 2차(M-0354): 2건(C-16, C-17)
- 3차 1라운드: 1건(C-18)
- 3차 2라운드: 4건(C-19~C-22)

3차 2라운드는 마지막 라운드였는데도 가장 많이 냈다. 종료 보고는 이 런이 "라운드 상한으로 끝났으므로 수렴이나 무결함을 뜻하지 않는다"고 적었다(`임시/do-math_검증_20260928/종료보고.md` 44행).

**사실.** 기간 전체의 개별 기록 가운데 정지는 17건이다. 시험 인스턴스에서 4건, 검증런에서 8건, 시험 실행·정적 검토에서 5건이다. 사용자가 관찰한 "20~30개"는 이 기간만으로는 채워지지 않는다. 다른 기간과 합친 수는 담당 A·B의 기록과 함께 봐야 한다.

**기록과 판정의 차이.** 3차 런 종료 보고 6절은 "연구를 멈추던 결함"에 R1-25(신뢰 전환 뒤 영구 `blocked`), R1-69(재개 뒤 pause 재생), R2-25(`check` exit 1), R2-34(거짓 순환)도 넣었다. 나는 이 넷을 저하로 판정했다. 근거는 다음과 같다.

- R1-25와 R2-25: `blocked`는 `status`·`check`의 점검 투영 필드다. 1a8ce7a·3552607 판본에서 배정 관문인 `scheduled_operator.engine_start_guard`와 `supervision_block`은 런타임 `status`만 읽고 점검 결과를 읽지 않는다(5ecc321 판본 298~335행, 190~203행).
- R2-34: 거짓 순환이 바뀔 때 `research_plan`을 한 번 넣을 뿐이다(1a8ce7a 판본 `lifecycle_engine.py` 549~554행).
- R1-69: 연구가 멈추지 않는 제어 실패다.

독립 운영 AI가 점검 결과를 보고 연구를 멈추게 하는 운영 절차가 있다면 판정이 달라질 수 있다. 그 절차 문서는 읽지 않았다.

### 2. 사용자 관찰 ②: 시험 인스턴스의 결함은 앞선 검증런을 어떻게 통과했나

**사실.** 시험 인스턴스는 bdccee3 코드로 돌았다. 인스턴스의 `work/operator/bootstrap/<hash>/scripts/do_math/*.py` 82개가 `bdccee3`와 바이트까지 같았다. 85a540c과는 38개, 8af1f5e와는 54개가 달랐다.

따라서 앞선 검증런의 위치는 이렇다.

- M-0352: 인스턴스 바로 앞의 런이다. 앵커 85a540c을 검증해 bdccee3를 만들었다.
- M-0354: 앵커가 bdccee3로 인스턴스와 같은 코드를 검증했다. 시각상으로는 인스턴스 운전(23:24~00:12)과 겹쳐 돌았다.

C-01~C-14의 코드 파일은 두 런 모두 영역 배분 안에 있었다. 두 런은 253개 파일 전체를 영역 넷에 겹침 없이 나눴다. 따라서 모든 경우가 "범위에 들었는데 놓침"이다. 범위 밖이었던 결함은 없다.

**사실.** 놓친 결함들은 동결문의 찾을 결함 목록에 해당했다. C-03(자기 점검 저장 거부)과 C-06(운영 점검 인용 규칙)은 두 런의 찾을 결함 2 "생산자와 소비자 사이의 계약 불일치"에 정확히 들었다(M-0352 동결 276행, M-0354 동결 278행). M-0354는 같은 기제의 C-17을 같은 `schemas.py`에서 찾았고, C-03 결함 행 737행과 같은 함수 안의 죽은 인자(R1-15)를 고쳤다.

**사실.** 두 런의 구조는 두 층이었다.

- 수리 층: 수리자는 코드를 실행하지 않았다(M-0354 동결 397행 "수리자는 코드를 실행하지 않는다").
- 확인 층: 적용 뒤 통합 확인 세 묶음이 1,840~1,841건을 통과했다.

이 통합 시험이 C-03 경로에서는 저장 대역(`test_controls.py` 183행)을, C-06 경로에서는 두 규칙이 우연히 일치하는 입력(`test_role_input.py` 118~137행)을, C-01·C-10·C-14 경로에서는 폐포 두 상수짜리 픽스처를 썼다.

**추론.** 검증런의 정적 판정과 시험 체계의 대역·합성 입력이 같은 사각을 공유했다. 정적 수리자는 "스키마가 닫혀 있으니 거부된다" 같은 추론을 원문 대조로만 한다. 3차 2라운드의 R2-04(`GRANT` 열린 모양)는 수리자·심사자 모두 이 추론을 틀렸고, 최종 통합 확인이 잡았다(M-0357). C-03은 그 반대 방향(생산자가 쓰는 키가 닫힌 스키마에 없음)을 수리자가 볼 계기가 없었고, 시험은 대역 때문에 보지 못했다.

**사실(충분히 발견할 수 있었던 종류인가).** 가장 싼 포착 시험은 대부분 모델과 Lean을 부르지 않는 L1·L2 시험이다.

- C-03·C-17·C-22: 닫힌 스키마 키 포함 관계의 표 시험 하나로 셋을 모두 잡는다.
- C-06: "지급한 근거는 모두 인용 가능" 속성 시험 하나로 잡는다.
- C-09: 인터프리터 경로 패치 하나로 잡는다.
- C-01·C-02·C-10·C-14: 실제 Lean 출력 하나를 고정 픽스처로 두면 한꺼번에 잡는다.

모델 출력의 실제 모양이 필요한 결함은 C-05·C-07(작업자가 알림 전에 긴 도구를 시작, 두 실행의 경합)처럼 순서·경합이 걸린 것뿐이다. 이들도 가짜 시계와 순서 강제로 결정적으로 재현할 수 있다.

### 3. 같은 기제의 라운드별 반복

- **생산자 필드와 닫힌 저장 스키마의 어긋남.** 세 가족 모두 `7d2597e`에서 주입됐다(닫힌 스키마 도입 시점에 생산자 필드를 선언하지 않음). 한 번 발견될 때마다 그 가족만 고쳤다.
  - C-17(2차, `question_links`)
  - C-03(시험 인스턴스, `self_check_responses`·`self_check_obligations`)
  - C-22(3차 2라운드, `goal_judgments`)
  - 반대 방향(열린 입력 모양이 지운 키를 통과): 3차 2라운드 최종 확인의 `GRANT`(R2-04와 같은 결함)
- **탈출 경로 없는 대기.**
  - C-25(정리 검토)
  - C-26(정리 구현)
  - C-15(안정화 검증)
  - C-08(시험 인스턴스)
  - C-18(3차 1라운드)
  - C-20(3차 2라운드, 1회 제한의 영구 차단)

  대기 종류를 만드는 코드와 푸는 코드가 따로 쓰였고, "모든 대기 종류에 해소 경로가 있다"는 성질을 단언하는 시험이 없었다.
- **같은 규칙의 두 사본(관문 사이 불일치).**
  - C-15: 형식 결과 분류와 게시 관문의 환경 오류 분류
  - C-06: 운영 점검 허용 집합 둘
  - C-19: 배정 관문과 실행 중 정지 판정의 권한 규칙
- **소유 루프 예외 사망.**
  - C-16(2차)
  - C-21(3차 2라운드)
  - C-27(정리 구현)
  - 기아형: C-24(시험 경량화)
- **자기 점검 경로.** 네 라운드에 걸쳐 같은 하위 체계가 고쳐졌다.
  - C-03·C-05(시험 인스턴스, 5ecc321)
  - C-04(3차 1라운드 R1-16·R1-40)
  - 3차 1라운드 R1-17(자기 체크포인트 인용 불가)
  - 3차 2라운드 R2-14(반려 영수증의 오류 누락)
  - 3차 2라운드 R2-13·R2-38(효력 없는 `observation-rules.json`의 제출 반려)
- **현재성 반환의 경로 분류.** C-07(시험 인스턴스) 뒤로 3차 1라운드 R1-53·R1-62, 3차 2라운드 R2-46이 같은 경로를 세 번 더 고쳤다.
- **독립성 누출.** 5ecc321 구현 중 목표 감사 누출(입력 재설계가 `research/`를 열어 봉인 즉시 기록된 목표 판정이 보임)이 있었다. 3차 1라운드 직접 처리에서 같은 목표 감사 자리를 대상으로 한 운영 점검 경유 누출(여섯 경로)이 이어졌다. 둘 다 저하라 개별 기록은 하지 않았다.
- **수집되지 않거나 결함을 고정한 시험.**
  - 수집되지 않은 시험: 안정화 검증 R1-01·R1-21·R1-22에서 85a540c 재편이 `__main__` 블록 뒤에 시험을 둬 이중 프로필 회귀 시험이 한 번도 돌지 않았다.
  - 결함 동작을 기대값으로 단언한 시험: C-03의 `control_call_ids` 단언, C-20의 `recovery_failed` 단언, C-19의 grant 철회 단언. 3차 2라운드는 이를 "승인된 설계 변경이 옛 성질 시험을 남긴다"로 기록했다(M-0357).

### 4. 주입 시점의 분포

**사실.** 정지 17건의 주입 커밋은 다음과 같다(미확정 포함).

| 주입 커밋 | 기록 |
|---|---|
| `7d2597e`(09-23, 기능 판본 5) | C-03, C-17, C-19, C-20, C-21, C-22, C-25, C-27. C-08·C-18은 후보 |
| `ff9b2b9`(09-25) | C-16 |
| `8d2ffd0`(09-26) | C-15, C-24. C-18은 후보 |
| `379a171`(09-26) | C-23. C-26은 후보 |
| 특정하지 못함 | C-01, C-02 |

**추론.** 이 기간 검증런이 찾은 정지급 결함의 다수는 이 기간의 경량화가 새로 들인 것이 아니다. 기능 판본 5에서부터 남아 있던 결함이다. 반복 검증이 새 결함만이 아니라 오래된 잠복 결함을 계속 캐내고 있었다. 경량화가 들인 정지급 결함(C-15, C-23, C-24)은 이 기간 안에서 시험 실행이나 첫 검증런이 잡았다.

### 5. 시험 미실행과 정적 검증 위주의 절차

**사실.**

- 379a171(M-0349)은 사용자 결정으로 시험을 돌리지 않고 커밋했고, C-23이 이 커밋에서 활성화됐다.
- 네 검증런 모두 수리자의 코드 실행을 금했다.
- 3차 2라운드의 R2-04 결함은 코드를 실행하지 않는 수리·심사가 모두 통과시켰고, 마지막 통합 확인이 잡았다(M-0357 "마지막 통합 확인은 생략할 수 없다").
- 실제 모델 운전은 이 기간 시험 인스턴스 하나뿐이었다. 5ecc321 이후의 세 커밋(5ecc321, 1a8ce7a, 3552607)은 실제 모델로 운전하지 않았다(M-0355·M-0357 「남은 것」).

### 6. 개발 중 포착되어 출하되지 않은 결함(개별 기록 안 함)

검사 경량화(M-0348)는 다음을 커밋 전에 잡았다.

- 이음새 요청 셋: artifact 키에 크기 누락은 기존 시험 2개가 잡았다. racy-git 지문과 나노초 시각의 안전 정수 초과도 이음새 요청으로 반영했다.
- `recheck` 삭제 뒤 대기를 재개할 경로 부재: 성격상 정지형이지만 같은 작업 안에서 새 경로를 만들었다.
- 매 바퀴 게시가 드러낸 시험 쪽 데이터 경합

시험 경량화(M-0350)는 `operation_trace` 타이머의 핸들 잔류를 통합 단계에서 잡았다. 서식 1절은 발견 경위를 가리지 않고 정지급을 기록하라고 하지만, 이들은 어떤 커밋에도 들어가지 않아 유출이 아니므로 개별 기록에서 뺐다.

### 7. 서식 적용에서 생긴 사정

- **영향 등급의 두 해석.** "잠재: 운전에서 발현되지 않았고, 발현 조건이 드물거나 아직 도달하지 않았다"를 문언대로 적용하면, 운전 없이 검증런이 찾은 결함은 모두 잠재가 된다. 그러면 1절의 "발견 경위와 무관한 정지급 결함"이 성립하지 않는다. 그래서 등급을 "발동했을 때의 결과"로 매겼고, 잠재는 발동해도 정지·저하로 이어지는지 불분명한 결함에만 썼다. 개별 기록에는 잠재가 없다. 운전 미발현은 증상 칸에 적었다. 서식이 두 축(발현 여부, 발동 시 결과)을 한 칸에 담고 있다.
- **인스턴스 단위와 경로 단위.** C-01·C-03은 인스턴스가 계속 돌았지만, 목표 경로나 필수 출력 경로가 사람 개입 없이 풀리지 않아 정지로 매겼다. 서식 3절의 예시 "필수 역할 출력의 전건 거부"는 경로 단위이고, 본문 정의 "연구 인스턴스가 더 진행하지 못한다"는 인스턴스 단위다.
- **무영향 분류.** 검증런 장부의 대다수 행(잔재, 죽은 인자, 규칙 사본, 문서, 시험 구조)은 서식 3절 세 등급 어디에도 맞지 않아 2.2절에 `무영향`으로 셌다.
- **시험 유출 원인 값의 공백.** 두 경우는 값 목록에 없어 가장 가까운 값을 골랐다.
  - 시험 미실행: 시험은 있었으나 주입 커밋에서 돌리지 않았다(C-23). `단언 약함`을 고르고 사정을 적었다.
  - 결함 고정: 시험이 결함 동작을 기대값으로 단언했다(C-03, C-19, C-20). `단언 약함`으로 적고 괄호에 "결함 고정"을 붙였다.
- **발견 경위.** C-02는 인스턴스 해석이 계기였지만 운전 중에 드러난 것이 아니라 코드 추적으로 찾았으므로 `정적 검토`로 적었다. C-04는 운전 증상과 검증런 원인 판정이 섞여 있어 둘 다 적었다.
- **판정 근거의 한계.** 승인·적용된 검증런 항목의 원문은 라운드 디렉토리 정리로 사라졌다. C-16·C-17·C-19·C-21의 영향과 원인은 장부 요지, 종료 보고, 수리 diff로 판정했다. 기각보관에 원문이 남은 C-15·C-18·C-20·C-22는 항목 영향 칸을 근거로 삼았다.
