# 결함 기록 B — M-0333~M-0347 (2026-09-24~09-25)

담당 B가 기억 노드 M-0333~M-0347 기간(2026-09-24~09-25)의 do-math 결함을 `결함-기록-서식.md`에 따라 기록한 문서다. 기록 번호 접두는 `B`다.

## 1. 읽은 범위

### 1.1 기억 노드

`C:\math\기억\layer1\M-0333.md`부터 `M-0347.md`까지 15개를 모두 전문으로 읽었다. 모두 do-math 노드이며 제외한 노드는 없다. M-0335는 graphify 갱신 기록이어서 결함 원천이 없었다.

노드가 없는 커밋 `a0e6c2f`(09-25 01:52, 예약 등록·Mathlib 캐시 수리)도 기간 안에 있다. M-0340·M-0341이 이 커밋을 가리키므로 원천에 넣었다.

### 1.2 전문으로 읽은 문서

- `C:\math\docs\do-math\수리-구현-결과-2026-09-24.md`
- `C:\math\docs\do-math\initialization-repairs-20260925.md`
- `C:\math\docs\do-math\connection-audit-2026-09-25.md`
- `C:\math\docs\do-math\초기화-효율-개선계획-2026-09-25.md`
- `C:\math\docs\do-math\초기화-효율-구현결과-2026-09-25.md`
- `C:\math\docs\do-math\boundary-repairs-2026-09-25\README.md`
- `C:\math\docs\do-math\similar-defects-2026-09-25\coverage.md`
- `C:\math\docs\do-math\similar-defects-2026-09-25\README.md`(D1~D7의 정의가 여기 있어 함께 읽었다)
- `C:\math\.skill-workspace\research-reliability-20260925\design-review.md`
- `C:\math\.skill-workspace\research-reliability-20260925\implementation-review.md`
- `C:\math\.skill-workspace\research-timeline-20260925\report.md`
- `C:\math\.skill-workspace\research-timeline-20260925\deep-analysis.md`
- `C:\math\.skill-workspace\research-timeline-20260925\source-audit.md`
- `C:\math\.skill-workspace\research-timeline-20260925\scheduling-audit.md`
- `C:\math\.skill-workspace\research-timeline-20260925\execution-ledger.md`(앞 약 60행의 실행 원장·제어 표)
- `C:\math\.skill-workspace\initialization-review-20260925\review.md`(RI-B의 F01~F14 원천. M-0346이 가리킨다)
- 검증런 VR1 장부 `C:\math\임시\do-math_검증_2026-09-24\장부.md`

### 1.3 일부만 읽은 자료

- 검증런 VR2~VR7의 `장부.md`: 본표 전 행을 내가 직접 읽었다. 항목별 diff 대조와 당시 시험 판본 확인, 장부 사유 절·종료 보고·`직접처리.json` 대조는 세 조사 에이전트가 나눠 수행했다. 에이전트가 읽지 않은 것은 VR1~VR3의 `동결.md`·`기각보관/`, VR5의 `추가관찰.json` 세부, VR6·VR7의 `기각보관/`·`검증결과.json`·`검토근거.zip`이다. 에이전트 판정 가운데 B-35, B-38, B-43, B-46, B-49의 수정 diff는 내가 직접 다시 대조했다.
- `C:\math\docs\do-math\initialization-repairs-20260925.json`: `closure`와 `static_performance_candidates`만 읽었다.
- `validation-summary.json` 세 개(`.skill-workspace\do-math-initialization-implementation\`, `.skill-workspace\research-reliability-20260925\verification-summary.json`, `docs\do-math\boundary-repairs-2026-09-25\`)는 특정 시험 이름의 출현만 검색했다.
- `C:\math\docs\do-math\정적-검토-수리안-2026-09-23.md`: 1~49행(개요 표)만 읽었다.
- 커밋 diff와 부모 판본 시험 파일: 기록마다 필요한 부분을 `git show`·`git grep`으로 확인했다. 대상 커밋은 `a0e6c2f`, `ff9b2b9`, `c44dd7b`, `c4d7838`, `735d464`, `a299fd8`, `6b39cac`이다.

### 1.4 읽지 못했거나 읽지 않은 자료

- M-0340 세션 `01a0d419-…`의 원 로그(사용자 홈 `.codex/sessions/`)는 읽지 않았다. B-01·B-02는 노드 기술과 수정 diff를 근거로 썼다.
- RI-A 앞의 두 초기화 실험(`nat-add-zero-20260925`, `-run2`)은 인스턴스 폴더가 남아 있지 않다. deep-analysis도 이 둘을 합산하지 않았으므로 결함을 따로 기록하지 않았다.
- VR4 종료 보고가 가리키는 `_기각보관/astra8-3-라운드1.md`는 폴더에 없다(조사 에이전트 보고).
- `research-reliability-20260925\implementation.md`는 읽지 않았다. 구현 요약이며 결함 원천은 `implementation-review.md`와 M-0342로 확인했다.

### 1.5 기간 경계 문서

`수리-구현-결과-2026-09-24.md`는 원천 목록에 있어 전문을 읽었다. 그러나 이 문서의 수정 커밋 `8694693`(09-24 00:34)과 원인 문서(`정적-검토-수리안-2026-09-23.md`)는 M-0330 이전, 곧 담당 A의 기간에 속한다. 그래서 그 8개 수리 항목과 원인 미확정 시험 실패 2건은 개별 기록 없이 2절에서 건수만 셌다. 이 문서를 가리키는 기억 노드는 없으므로, 담당 A가 이 항목들을 다루는지 집계자가 확인할 필요가 있다. 그중 3번(부정·미해결 감사 결과의 후속 누락)과 4번(감사 중복·원 생산자 마무리)은 원인 문서를 봐야 등급을 정할 수 있다.

## 2. 요약 표

### 2.1 개별 기록

| 번호 | 제목(요약) | 영향 | 결함 유형 | 층 | 시험 유출 원인 | 범주 후보 |
|---|---|---|---|---|---|---|
| B-01 | 예약 등록의 pythonw 출력 미수집 | 정지 | 외부 경계 | 경계 어댑터 | 대역이 가림, 환경 차이 | 외부 프로세스 출력 수집 의미의 가정 |
| B-02 | 생산자 없는 `build_kind=clean` 요구 | 정지 | 스키마·계약 불일치 | L1 | 합성 입력이 실제와 다름 | 생산자 없는 수신 요구 |
| B-03 | 신뢰 환경 반복 전수 관측 | 저하 | 알고리즘 | L2 | 시간·규모 미재현 | 구조 검사와 실측 관측의 책임 혼합 |
| B-04 | 대형 불변 원문의 다중 인라인 복제 | 저하 | 알고리즘 | L2 | 시간·규모 미재현 | 불변 대형 원문의 다중 인라인 복제 |
| B-05 | 동기 관찰 callback에 의한 결과 회수 지연 | 저하 | 타이밍·직렬화 | L3 | 시간·규모 미재현 | 관찰 처리와 완료 회수의 직렬 결합 |
| B-06 | 처리 시각 기준 관찰 판정 | 저하 | 타이밍·직렬화 | L2 | 시험 없음 | 사건 발생 시각과 처리 시각의 혼동 |
| B-07 | live 운영 점검의 checkpoint 미지급 | 저하 | 인터페이스 | L2 | 단언 약함 | 역할 계약이 요구하는 근거의 입력 미지급 |
| B-08 | 처분 근거 허용 집합 불일치 | 저하 | 스키마·계약 불일치 | L2 | 합성 입력이 실제와 다름 | 생산자 광고 집합과 수신 검사 집합의 분리 |
| B-09 | 완료 판정 근거 해시의 과민 | 저하 | 검사 | L2 | 단언 약함 | 판정 근거 해시의 범위 과잉 |
| B-10 | 초기화 사건의 별도 빈 계획 | 저하 | 기능 | L2 | 시험 없음 | 사건 발동·소유의 과잉 |
| B-11 | 정상 점유를 준비 상실로 계획에 전달 | 저하 | 기능 | L2 | 시험 없음 | 사건 발동·소유의 과잉 |
| B-12 | 정비 정지가 미접수 정상 결과를 무권한화 | 저하 | 기능 | L2 | 시험 없음 | 운영 정지와 사용자 정지의 의미 미분리 |
| B-13 | 운전 중 수리를 생성 사본에만 적용 | 잠재 | 빌드·패키지 | 계약·스키마(근사) | 시험 없음(근사: 검사 미실행) | 정본·생성 사본의 이원화 |
| B-14 | 신뢰 manifest 모집단 완전성 미검사 | 저하 | 검사 | L2 | 합성 입력이 실제와 다름, 시험 없음 | 선언 모집단의 완전성 미검사 |
| B-15 | 검증 증거 내용 미판독 | 잠재 | 검사 | L1 | 합성 입력이 실제와 다름 | 성공 라벨을 증거 내용 대신 소비 |
| B-16 | 준비 판정과 프로필 선택의 규칙 분기 | 저하 | 검사 | L2 | 합성 입력이 실제와 다름 | 같은 판단의 소비자별 규칙 분기 |
| B-17 | 운영 retry와 자동 후속의 경합 → 설치 수리 대기 | 정지 | 타이밍·직렬화 | L2 | 조합·순서 미탐색 | 복구 계보의 단일 소유자 부재 |
| B-18 | 사용자 요청 원문 축약 보존 | 저하 | 인터페이스 | L3 | 시험 없음 | 사용자 원문 보존 범위의 축소 |
| B-19 | 운영자 선택과 사용자 결정의 출처 혼동 | 저하 | 문서·계약 | 계약·스키마 | 시험 없음 | 결정 출처의 혼동 |
| B-20 | 필수 문서 절단 독해 | 저하 | 문서·계약 | 계약·스키마 | 시험 없음 | 필수 입력의 절단 독해 |
| B-21 | 프로필·승인 해시 수작업 조립 | 저하 | 인터페이스 | L3 | 시험 없음 | 운전자 수작업 조립 경로 |
| B-22 | 제한 실행이 활성화를 넘어 진행 | 저하 | 인터페이스 | L3 | 시험 없음 | 제한 실행의 종료 조건 불일치 |
| B-23 | 역할 입력의 프로필 본문 반복 | 저하 | 알고리즘 | L2 | 시간·규모 미재현 | 역할 입력의 중복 전문 삽입 |
| B-24 | 계측 오류 정보 유실과 Windows 원자 교체 실패 | 저하 | 외부 경계 | 경계 어댑터 | 시간·규모 미재현 | OS 파일 교체 의미의 가정 |
| B-25 | 준비용 Lean 컴파일의 Job·진행 관측 부재 | 저하 | 기능 | 경계 어댑터 | 대역이 가림 | 외부 프로세스 수명 관리의 경로별 불일치 |
| B-26 | 차단 사유 요약 부재와 감독 wake 지연 | 저하 | 기능 | L3 | 시험 없음 | 차단 상태의 가시성·복구 트리거 부재 |
| B-27 | export의 파일별 Git 프로세스 | 저하 | 알고리즘 | 경계 어댑터 | 시간·규모 미재현 | 저장소 읽기의 파일별 프로세스 호출 |
| B-28 | 재등장한 큰 원문의 재저장 거부 | 정지 | 알고리즘 | L2 | 조합·순서 미탐색, 합성 입력 | 내용 주소 저장의 재등장 처리 누락 |
| B-29 | 공개 제어 입력 형식 오류의 반복 처리 실패 | 정지 | 검사 | L2 | 시험 없음 | 입력 형식 오류의 반려 경계 이탈 |
| B-30 | payload 참조 순서와 정렬 키 불일치 | 정지 | 스키마·계약 불일치 | L1 | 합성 입력(+시험 미실행) | 직렬화 왕복 불변식 위반 |
| B-31 | 단계 제한 실행의 게시 정산 누락 | 정지 | 타이밍·직렬화 | L3 | 조합·순서 미탐색(+시험 미실행) | 비동기 완료 뒤 정산 의무의 누락 |
| B-32 | 선택 표시 항목의 필수 재분류로 입력 초과 | 정지 | 인터페이스 | L2 | 합성 입력, 시험 없음 | 필수 입력 분류의 이중 정의 불일치 |
| B-33 | 보충 조사에 연구 수행 규칙 전달 | 정지 | 기능 | L3 | 조합·순서 미탐색 | 역할 분기 조건의 과잉 포함 |
| B-34 | 관계 끝점 근거의 목록·객체 불일치 | 정지 | 스키마·계약 불일치 | 계약·스키마 | 대역이 가림, 시험 없음 | 생산자·저장 스키마 모양 불일치 |
| B-35 | Claude 잠금 표지가 Codex 요청에 유입 | 정지 | 스키마·계약 불일치 | 경계 어댑터 | 대역이 가림 | 요청 생산자·작업자 수신 스키마 불일치 |
| B-36 | 정지 중 제한 복구의 일괄 거부 | 정지 | 검사 | L3 | 대역이 가림 | 일괄 정지 게이트와 예외 허가의 불일치 |
| B-37 | 반려된 준비를 무산출로 계수 | 정지 | 알고리즘 | L2 | 조합·순서 미탐색 | 반복 계수의 결과 분류 오류 |
| B-38 | 계약 검토 대기 미해제 | 정지 | 대입·초기화 | L2 | 조합·순서 미탐색 | 대기 해소 조건 누락 |
| B-39 | 학술 요구 전부 제거 시 완료 불능 | 정지 | 기능 | L2 | 조합·순서 미탐색 | 빈 집합 경계의 완료 전이 누락 |
| B-40 | 공유 형식 결과 전환의 저장 거부 | 정지 | 스키마·계약 불일치 | L1 | 조합·순서 미탐색 | 저장 의미 검사의 식별 키 부족 |
| B-41 | 학술 요구 ID 값 영역 불일치 | 정지 | 스키마·계약 불일치 | 계약·스키마 | 합성 입력이 실제와 다름 | 생산자·저장 스키마 모양 불일치 |
| B-42 | 파일명으로 지목한 누락 자료의 재평가 누락 | 정지 | 인터페이스 | L2 | 합성 입력이 실제와 다름 | 대기 해소 조건의 식별자 형식 불일치 |
| B-43 | 비객체 knowledge_metadata로 실행기 반복 종료 | 정지 | 검사 | L2 | 시험 없음 | 입력 형식 오류의 반려 경계 이탈 |
| B-44 | 작업 공간 루트 참조로 실행기 반복 종료 | 정지 | 검사 | L1 | 시험 없음 | 입력 형식 오류의 반려 경계 이탈 |
| B-45 | 공급자 이벤트의 수로 실행기 종료 | 정지 | 외부 경계 | L2 | 합성 입력, 대역이 가림 | 공급자 값 영역과 저장 값 영역의 불일치 |
| B-46 | Claude 사용량 필드의 저장 거부 | 정지 | 스키마·계약 불일치 | 계약·스키마 | 합성 입력, 시험 없음 | 생산자·저장 스키마 모양 불일치 |
| B-47 | 확장 검토 자리의 개정 재검토 거부 | 정지 | 검사 | L2 | 조합·순서 미탐색 | 확장된 실제 상태를 정책 기본값으로 재검사 |
| B-48 | `result: None` 보충 조사로 질문 연결 예외 | 정지 | 스키마·계약 불일치 | L2 | 조합·순서 미탐색 | 명시적 null과 누락 기본값의 혼동 |
| B-49 | PATH Lean의 경로 이중 정규화 | 정지 | 외부 경계 | 경계 어댑터 | 합성 입력, 환경 차이 | 동일 식별자의 이중 정규화 |

**영향 등급별 건수**: 전체 49건 가운데 정지 25건, 저하 22건, 잠재 2건이다. 발견 경위별로 보면 다음과 같다.

| 발견 경위 | 기록 | 건수 | 정지 |
|---|---|---:|---|
| 실제 운전 | B-01~B-27 | 27 | 3건(B-01, B-02, B-17) |
| 정적 검토 | B-28, B-29 | 2 | 2건 |
| 시험 실행 | B-30, B-31 | 2 | 2건 |
| 검증런 | B-32~B-49 | 18 | 18건 |

### 2.2 개별 기록을 쓰지 않은 결함의 출처별 건수

검증런 장부는 본표 행 단위로 셌다. 같은 결함의 중복 제기와 병합 구성원도 각각 한 행이다. "정지(기록)"는 개별 기록으로 옮긴 행이다.

| 출처 | 전체 | 정지(기록) | 기록하지 않음: 저하 | 잠재 | 문서·정리 | 결함 아님 |
|---|---:|---:|---:|---:|---:|---:|
| VR1 장부(R1 7 + R2 12) | 19 | 1 | 7 | 1 | 10 | 0 |
| VR2 장부 | 41 | 6(결함 5) | 12 | 1 | 21 | 1 |
| VR3 장부 | 26 | 6(결함 5) | 10 | 4 | 6 | 0 |
| VR4 장부 | 25 | 3 | 9 | 3 | 10 | 0 |
| VR5 장부(직접 수리 9행 포함) | 111 | 0 | 19 | 0 | 92 | 0 |
| VR6 장부 | 37 | 3(결함 2) | 21 | 3 | 10 | 0 |
| VR7 장부 | 69 | 2 | 34 | 0 | 31 | 2 |

검증런 장부의 저하 건수에는 반복 복사·재계산 같은 비용 항목이 포함된다. 특히 VR5는 4건, VR7은 34건 가운데 대부분이 비용 항목이다.

| 출처 | 기록하지 않은 건수와 내역 |
|---|---|
| 유형 확장 감사 D1~D7(`similar-defects-2026-09-25`) | 5. D2 잠재(내부 저장소 API로만 도달), D3·D4 저하(checkpoint 근거 연결 유실, 마지막 유효 checkpoint 폐기), D5 저하(관계를 통한 독자의 개정 대기 누락), D6 잠재(취소된 신뢰 검사 재실행의 계보 미저장). D1·D7은 B-28·B-29로 기록했다 |
| 정적 연결 감사 F1~F7(`connection-audit-2026-09-25.md`) | 5. F1 잠재(벽시계 역행 때 제어 순서 역전), F2~F4 잠재(빈 목록을 빈 객체로 치환해 형식 검사 우회), F5 문서. F6·F7은 B-30·B-31로 기록했다 |
| 초기화 효율 개선계획 | 2. starting 도중 시작 정보가 공개되지 않은 실행의 복구 불능(잠재, 정적 발견, `ff9b2b9`의 launch ticket으로 수리). 공급자 이름만으로 묶는 능력 관측 재사용의 전제 미명시(잠재) |
| research-timeline 분석 | 1. 운영 점검 `continue`의 `next_review.at`이 접수 때 이미 과거여서 즉시 재점검이 반복될 수 있음(잠재, 처분이 반려돼 미발현) |
| 작업 중 발견·커밋 전 수정(M-0341·M-0342·M-0343, `implementation-review.md`) | 8. 컴파일 후 환경 확인의 중앙 스레드 잔류, 미리보기·실행기 없는 제어 경로의 동기 검사 회귀, 취소 결과가 재개를 계속 막음, 이전 실행기의 미소비 관측 재사용, 완료 근거에서 관계 끝점 누락, 부분 JSONL 행 경계 오판, 영향 분석의 locator 회귀, 새 입력 검사가 기존 유효 입력을 좁힘 |
| 시험 자체의 결함(fixture·드라이버·도우미) | 15. M-0336의 시험 조각 2, M-0337의 시험 전제 모순 1, M-0338의 `test_repair_plan` 모형 1, M-0339의 `{"passed": true}` 증거·runtime만 paused·일회 허가 행동 ID 누락·`observer.close()` 잔존 4, M-0345의 제출 도우미 참조 순회·고정 15초 정지 시험·지운 import 3, M-0346의 운영 실행 횟수=모델 호출 가정·입력 초과 시험의 전역 호출 수 가정 2, M-0347의 `verifier_path` 없는 승인 fixture·공통 메서드 없는 대역 2 |
| 원인 미확정 | 1. M-0346 종료 시점 형식 흐름 시험의 게시 단언 실패(순차 진단은 11단계에 K 게시, 병렬 진단은 중단. 교착 여부 미확정). `수리-구현-결과-2026-09-24.md`의 `independent_intent` 전 paused 시험 2건은 아래 기간 경계 행에 센다 |
| 기간 경계(`수리-구현-결과-2026-09-24.md`, 커밋 `8694693`) | 10. 수리 항목 8건(1.5절)과 원인 미확정 시험 실패 2건 |
| VR1 R1-06 적용 회귀 | 0(VR1 장부 행에 포함). 실패한 하위 시험 뒤 건너뛴 하위 시험이 오면 부모 실패가 skipped로 덮이는 회귀를 적용 뒤 재현이 잡아 제외했다(M-0333). 시험 결과 기록기의 결함이다 |

## 3. 개별 기록

기록 순서는 발견 원천별이다. B-01~B-02는 첫 실사용 초기화 세션(M-0340), B-03~B-13은 실사용 인스턴스 `RI-01M3AB8E1KYF02E3T0G7BFEVAC`(이하 RI-A, M-0341·M-0342), B-14~B-27은 실사용 인스턴스 `RI-01M3BXA1GTK78NEXX9DAW13H67`(이하 RI-B, M-0346), B-28~B-31은 정적 경계·연결 감사(M-0343·M-0344), B-32 이후는 전면 검증런 장부에서 가려낸 정지급 결함이다.

실사용 인스턴스가 돌린 코드의 판본은 다음과 같다. RI-A는 2026-09-25 03:36 KST에 생성됐고 `a0e6c2f` 이후의 설치(초기화 세션에서 `.agents` 사본에 가한 임시 수리 포함 가능)로 운전했다. 따라서 이 기간의 검증런 VR1~VR5가 모두 그 코드를 범위에 넣었다. RI-B는 같은 날 18:10에 생성됐고 조사 당시 HEAD `d4d273a`, 즉 VR6 적용 뒤의 코드로 운전했다. 검증런 약칭은 다음과 같다.

| 약칭 | 기억 노드 | 수리 커밋 | 폴더 |
|---|---|---|---|
| VR1 | M-0333·M-0334 | `bc56bc3`(R1), `6b39cac`(R2) | `C:\math\임시\do-math_검증_2026-09-24\` |
| VR2 | M-0336 | `967218e` | `C:\math\임시\do-math_검증_2026-09-24_astra8\` |
| VR3 | M-0337 | `9a3d345` | `C:\math\임시\do-math_검증_2026-09-24_astra8_신규\` |
| VR4 | M-0338 | `9c5356d` | `C:\math\임시\do-math_검증_2026-09-24_astra8_3차\` |
| VR5 | M-0339 | `ded5952` | `C:\math\임시\do-math_검증_20260924_opus55\` |
| VR6 | M-0345 | `d4d273a` | `C:\math\임시\do-math_검증_20260925_full\` |
| VR7 | M-0347 | `fe59ca0` | `C:\math\임시\do-math_검증_20260925_opus\` |

일곱 검증런은 모두 do-math 정본 전 파일을 영역으로 나눠 읽었다. 그러므로 아래 "검증런 유출"에서 "범위 안"은 결함 코드가 그 검증런의 독해 범위에 들어 있었다는 뜻이다.

### B-01 예약 등록이 pythonw의 freeze 출력을 수집하지 못해 초기화가 끝나지 않음

- 출처: `C:\math\기억\layer1\M-0340.md` 「맥락」 셋째 문단·「확인 범위와 남은 작업」 둘째 문단, `C:\math\기억\layer1\M-0341.md` 「맥락」 둘째 문단(선행 커밋 언급), 커밋 `a0e6c2f`(`scripts/operator_schedule.ps1`, `scripts/tests/test_schedule_pythonw.py`). 원 세션 로그(`.codex/sessions/`의 `01a0d419-b36c-7730-88a2-6d0e5239cefc`)는 읽지 않았고, 노드 기술과 수정 diff를 근거로 썼다.
- 발견 경위: 실제 운전
- 영향 등급: 정지
- 증상: 새 인스턴스 초기화 중 예약 등록이 stdout 오류로 실패했다. 예약 상태 조회에는 연구·감독 작업이 없었고, 상태 조회에는 내부 실행 0건과 grant·대기 요청 0건이 나타났다. 초기화는 미완료로 끝났고 운전 대화는 직접 Lean 증명과 미완료 보고로 마쳤다. 같은 freeze를 Python으로 직접 실행하면 성공했다.
- 근본 원인: `operator_schedule.ps1`의 install 분기가 `$frozenText = & $Python $liveBootstrap --freeze ...`로 bootstrap을 호출했다. 예약 작업은 `$Python`에 `pythonw.exe`를 쓰는데, PowerShell은 파이프 없이 호출한 GUI 서브시스템 실행 파일의 종료를 기다리지 않고 stdout도 수집하지 않는다. 그 결과 빈 텍스트가 `ConvertFrom-Json`에 넘어갔다. 수정 diff의 주석이 이 기제를 적고 있다("An explicit pipeline makes PowerShell wait for GUI executables such as pythonw.exe and collect their stdout and exit code"). 추가된 시험은 stderr에 `Invalid argument`가 없음을 단언한다.
- 수정: `a0e6c2f`가 호출을 `| Out-String` 파이프로 바꾸고, `$LASTEXITCODE`가 null인 경우와 빈 출력을 거부하게 했다. 회귀 시험은 `test_schedule_pythonw.SchedulePythonwTests.test_real_freeze_json_is_collected_before_registration`, `test_failed_freeze_cannot_register_tasks_even_with_json_stdout`이다. 둘 다 실제 `pythonw.exe`로 install 분기를 실행한다.
- 결함 유형: 외부 경계
- 트리거: 실제 외부 도구 동작(PowerShell이 GUI 실행 파일을 호출하는 의미), 설정·환경(예약 작업의 인터프리터로 `pythonw.exe` 사용)
- 결함 위치 층: 경계 어댑터
- 시험 유출 원인: 대역이 가림, 환경 차이. `a0e6c2f^`의 `test_operator.py`에 있는 `test_init_keeps_created_instance_when_schedule_registration_fails`와 `test_new_instance_installs_the_operator_every_two_hours_by_default`는 `cli.scheduled_operator.schedule`을 `patch`로 대체해 PowerShell 어댑터를 실행하지 않았다(예약 어댑터 대역). `test_schedule_lifetime.py`는 ps1을 AST로 파싱해 설정 식 두 개만 평가했고 install 분기는 돌리지 않았다. `pythonw.exe`로 어댑터를 실행한 시험은 없었다.
- 검증런 유출: 결함 행은 `7d2597e`(2026-09-23)에서 들어왔다(`git log -S`). VR1~VR5가 모두 범위 안에서 놓쳤다. VR5 R1-40은 같은 등록 실패 경로에서 재조정 명령의 `--repository` 누락을 지적했지만 출력 수집 결함은 제기하지 않았다. PowerShell의 GUI 실행 파일 호출 의미는 원문 독해만으로 드러나기 어려운 외부 경계다.
- 가장 싼 포착 시험: Windows에서 `Register-ScheduledTask` 등 예약 cmdlet만 함수로 가린 PowerShell harness로 실제 `operator_schedule.ps1 -Action install -Python <pythonw.exe>`를 실행한다. 단언은 세 가지다. 종료 코드 0, 등록 호출 2회, stdout JSON의 키가 `{engine, operator, wake}`다. 모델·예약 작업 등록 없이 약 1초 안에 끝난다.
- 범주 후보: 외부 프로세스 출력 수집 의미의 가정

### B-02 신뢰 환경 검사가 생산자가 만들지 않는 `build_kind=clean`을 요구해 캐시 Mathlib 환경을 등록할 수 없음

- 출처: `C:\math\기억\layer1\M-0340.md` 「맥락」 셋째 문단, `C:\math\기억\layer1\M-0341.md` 「맥락」 둘째 문단, 커밋 `a0e6c2f`(`scripts/do_math/initialization.py`, `scripts/setup_lean.py`, `references/초기화-운전.md`, `scripts/tests/test_environment_validation.py` 신규)
- 발견 경위: 실제 운전
- 영향 등급: 정지
- 증상: 같은 초기화 세션에서 "Mathlib 클린 빌드 증거 부족"으로 신뢰 환경을 활성화하지 못했고, 초기화가 미완료로 끝났다. 노드는 필요한 신뢰 증거를 찾지 못한 상태를 검증 완료로 바꾸지 않았다고 적는다.
- 근본 원인: `initialization.trust_environment_errors`(`a0e6c2f^` 기준 120행)는 `manifest.get("build_kind") != "clean"`이면 `clean Mathlib build evidence absent`를 반환했다. 그런데 설치 도구 `setup_lean.py`는 `lake exe cache get`으로 미리 빌드된 캐시를 받는 경로만 제공했고 `build_kind`를 생산하지 않았다. `초기화-운전.md`의 예시만 운전자에게 `"build_kind": "clean"`을 쓰게 했다. 캐시를 받은 실제 환경은 참으로 clean 빌드라고 기록할 수 없으므로, 정직한 운전으로는 수신 검사를 통과할 방법이 없었다. 수신자만 있고 생산자가 없는 필드였다.
- 수정: `a0e6c2f`가 `build_kind` 검사를 지우고 manifest 필드 집합을 `{command, foundation_profile, files, validation}`으로 고정했다. 또 `setup_lean.py --verify-only`가 실제 smoke 컴파일(Mathlib import와 대표 증명)의 명령·출력·종료 코드·전후 toolchain을 검증 기록으로 남기게 했다. 회귀 시험은 `test_environment_validation.EnvironmentValidationTests`의 네 개다(`test_cached_environment_requires_evidence_and_unchanged_files`, `test_unknown_manifest_field_is_not_silently_ignored`, `test_validation_preserves_source_output_and_exact_toolchain`, `test_failure_and_toolchain_change_never_produce_verified_evidence`).
- 결함 유형: 스키마·계약 불일치
- 트리거: 설정·환경(Mathlib을 캐시로 설치한 실제 환경)
- 결함 위치 층: L1 원시(단일 값 검증기 `trust_environment_errors`. 짝이 되는 생산자는 `setup_lean.py`)
- 시험 유출 원인: 합성 입력이 실제와 다름. `a0e6c2f^`의 `research_fixtures.py:308`, `test_approved_five_repairs.py:82`, `test_lifecycle_engine.py:86`은 모두 `'build_kind': 'clean'`을 손으로 넣은 manifest를 썼다. 실제 생산자인 `setup_lean.py`의 출력을 수신 검사에 넣는 시험은 없었다.
- 검증런 유출: 검사 행은 `7d2597e`(2026-09-23)에서 들어왔다. VR1~VR5가 모두 범위 안에서 놓쳤다. 생산자 없는 필드는 이 검증런들의 초점("생산자와 소비자의 계약 불일치")에 정확히 해당한다.
- 가장 싼 포착 시험: 생산자에서 수신자로 가는 왕복 계약 시험이다. `setup_lean`의 manifest 조립 경로가 만든 manifest(임시 디렉터리의 가짜 파일 몇 개로 충분)를 그대로 `trust_environment_errors`에 넣고 오류 목록이 비었음을 단언한다. 반대로 수신자가 읽는 모든 필드가 생산자 출력에 있는지도 단언한다.
- 범주 후보: 생산자 없는 수신 요구(fixture의 수기 필드가 가림)

### B-03 신뢰 환경의 구조 검사와 관문이 설치 파일 전체를 반복 관측해 초기화가 느림

- 출처: `C:\math\.skill-workspace\research-timeline-20260925\deep-analysis.md` 3절, `C:\math\docs\do-math\초기화-효율-개선계획-2026-09-25.md` 「앞선 세 수리에 대한 판정」·48행·「작업 2·3」, `C:\math\docs\do-math\초기화-효율-구현결과-2026-09-25.md`, `C:\math\기억\layer1\M-0341.md`, 커밋 `ff9b2b9`(`scripts/do_math/trust_validation.py`·`environment_checks.py` 신규, `initialization.py`, `lifecycle_engine.py`)
- 발견 경위: 실제 운전(초기화 세션의 사용자 지적과 기록 분석)
- 영향 등급: 저하
- 증상: RI-A 초기화에서 신뢰 환경 등록에 2분 25.1초, 전환 요청에 2분 45.9초, 실제 활성화에 2분 31.9초가 걸렸다. 사용자가 긴 준비 시간을 문제로 지적했다. 과거 실행에서 전수 스캔이 정확히 몇 회 있었는지는 로그로 확정되지 않았다(deep-analysis 3절).
- 근본 원인: 당시 `initialization.trust_environment_errors`는 `verify_files=False`인 구조 검사에서도 모든 경로에 `Path.resolve()`를 실행했다. 그래서 저장 계약 검사와 status도 호스트 파일 시스템을 전수 접근했다. live 검사는 각 파일 전체를 `read_bytes()`로 읽어 해시했고, `require_trust_environment`는 기본으로 live 검사를 했다. 이 함수는 등록·전환·최종 전환·초기화 관문·형식 사용 관문에서 각각 호출됐다(개선계획 48행). 초기화 세션의 임시 수리(8-thread `Executor.map`)는 작업 전체를 먼저 제출하고 파일을 통째로 읽어 대기열·메모리 상한이 없었다(개선계획 27행).
- 수정: `ff9b2b9`이 구조 검사와 실제 파일 관측을 `trust_validation.py`로 분리했다. 전체 관측은 활성화에서 한 번 하고, 스트리밍 해시와 제한된 in-flight 큐(worker 4개, 최대 8개)를 쓰며, 환경 관측을 worker 경로(`environment_checks.py`)로 옮겼다. 회귀 시험은 `test_environment_validation.py`의 `test_large_manifest_rechecks_every_file_and_keeps_ordered_findings`, `test_structure_never_resolves_host_paths_and_live_hashing_streams`와 `test_initialization_efficiency.py`의 `test_activation_batch_reuses_only_the_current_provider_observation`, `test_publication_observation_is_deferred_and_not_reused_after_an_attempt`다.
- 결함 유형: 알고리즘
- 트리거: 장시간 누적(56,230개 파일, 8,551,731,741바이트의 실제 환경)
- 결함 위치 층: L2 인터페이스 요소
- 시험 유출 원인: 시간·규모 미재현. 당시 fixture `research_fixtures.trust_fixture`는 역할마다 합성 파일 하나, 총 6개로 manifest를 만들었다. 구조 검사의 호스트 접근 횟수나 초기화 한 번의 전수 관측 횟수를 단언하는 시험은 없었다.
- 검증런 유출: 이 경로는 VR1 앵커(`fa49372`)에 이미 있었다. VR1~VR5가 모두 범위 안에서 놓쳤다. 다섯 검증런은 모두 "지나친 비효율"을 초점으로 삼았지만, 장부 요지에 이 경로를 지적한 항목은 없다.
- 가장 싼 포착 시험: 파일 N개(예: 1,000개)짜리 합성 manifest를 준비하고 `Path.resolve`와 파일 열기를 계수기로 감싼다. 단언은 두 가지다. 구조 검사와 status가 호스트 파일에 0회 접근하고, 등록→전환→활성화→관문 재평가의 초기화 한 사이클에서 파일당 읽기가 정확히 1회다.
- 범주 후보: 구조 검사와 실측 관측의 책임 혼합(반복 전수 관측)

### B-04 큰 불변 원문(56,230항목 manifest·제어 요청)이 여러 상태 레코드와 역할 입력에 거듭 인라인 복제됨

- 출처: `deep-analysis.md` 6.1절, `초기화-효율-개선계획-2026-09-25.md` 50행·「작업 5」, `초기화-효율-구현결과-2026-09-25.md` 「실제 측정」, `C:\math\기억\layer1\M-0341.md` 「판단과 구현 중 확인한 경계」, 커밋 `ff9b2b9`(`scripts/do_math/payloads.py` 신규, `repository.py`, `context_store.py`, `submission.py`)
- 발견 경위: 실제 운전(기록 분석)
- 영향 등급: 저하
- 증상: artifact를 뺀 권위 레코드의 논리 바이트가 다음과 같이 늘었다.

  | 시점 | 바이트 |
  |---|---|
  | 첫 원문 해석 입력 | 386,549 |
  | 신뢰 활성화 입력 | 118,770,815 |
  | 동일성 scope 입력 | 158,945,406 |

  최종 상태의 큰 파일은 `runtime/history`(40.0MB), `runtime/extended_controls`(40.0MB), review cycle(39.7MB), governance source(20.4MB), trust environment(17.9MB)였다. 한 독립 검사 입력에서는 `recent_history`가 약 35.6MB, 파생 참조 목록이 약 23.6MB(56,271항목)였다.
- 근본 원인: trust 등록 제어 원문(56,230개 파일 목록)이 history·extended_controls·review cycle의 `publication_premises`와 `review_input_basis`·governance source·trust environment에 각각 inline으로 직렬화됐다. 당시 저장은 매번 부모를 decode·검증하고 후보를 깊게 복사한 뒤 전체를 인코딩했다. 역할 입력은 원문을 담은 최근 이력으로 참조 목록을 만든 뒤에야 prompt를 줄였다.
- 수정: `ff9b2b9`이 큰 불변 manifest와 문자열을 내용 주소형 payload로 한 번만 저장해 공유하게 했다. 검증한 부모 snapshot은 OID·계약·검증기 판본으로 재사용하고, 큰 과거 제어 원문은 참조 목록을 만들기 전에 상세 파일로 옮긴다. 효과로 한 사례의 이력 표현이 19,019,294바이트에서 490바이트로 줄었다. 회귀 시험은 `test_initialization_efficiency.py`의 `test_large_control_is_archived_before_reference_catalog_construction`, `test_payloads_are_exact_shared_and_immutable`, `test_large_payload_storage_and_cached_parent_remain_exact`와 `test_reference_catalog.py`의 `test_large_manifest_is_indexed_once_without_authorizing_the_projection`이다.
- 결함 유형: 알고리즘
- 트리거: 장시간 누적(입력 크기)
- 결함 위치 층: L2 인터페이스 요소(저장소 게시, 역할 입력 구성)
- 시험 유출 원인: 시간·규모 미재현. 시험 fixture의 trust manifest는 6개 항목이었고, 상태 크기의 증폭 배수를 단언하는 시험은 없었다.
- 검증런 유출: VR1~VR5가 범위 안에서 놓쳤다. VR2 R1-38, VR5 R1-103 같은 복사 비용 지적은 다른 경로였다. 이 수정이 새 결함 B-28(재등장 원문 재저장 거부)과 B-30(참조 순서 불일치)을 들여왔다.
- 가장 싼 포착 시험: 10만 항목 합성 manifest로 trust 등록 제어를 한 번 처리한다. 단언은 두 가지다. 저장된 논리 레코드의 총 바이트가 manifest 원문의 k배(예: 1.2배) 이하이고, 다음 역할 입력의 `recent_history` 바이트가 고정 상한 이하다.
- 범주 후보: 불변 대형 원문의 다중 인라인 복제

### B-05 관찰 사건마다 동기 callback과 전체 상태 저장을 기다려 완료된 실행의 결과 회수가 수십 분 늦어짐

- 출처: `deep-analysis.md` 4절·5절·6.2절·6.3절, `C:\math\기억\layer1\M-0342.md` 「맥락」·「확인한 원인과 설계 판단」 첫 문단, 커밋 `c44dd7b`(`scripts/do_math/model_runner.py`, `parallel.py`, `observation_transport.py` 신규, `engine.py`)
- 발견 경위: 실제 운전(기록 분석)
- 영향 등급: 저하
- 증상: worker 종료 기록 뒤 중앙 접수까지 걸린 시간은 다음과 같다.

  | 실행 | 지연 |
  |---|---|
  | 후보 준비 | 13분 36초 |
  | 계약 검토 | 10분 18초(worker 종료 뒤 전체) |
  | 선택 계획 | 6분 11초 |
  | 연구 수행 | 20분 36초 |
  | 동일성 scope | 58분 58초(미수락 정산까지) |

  native 결과가 있는 13개 실행의 구간 합으로 보면 약 79.6%가 worker 종료 뒤에 놓였다. 동일성 worker 종료 뒤 59분 동안 commit 47개가 계속 생겼다.
- 근본 원인: `model_runner.observe()`가 stdout chunk의 사건마다 `on_observation`을 동기 호출했다. `ModelCalls._callback`은 owner queue에 넣고 `Future.result()`로 처리 완료를 기다렸다. `_observe_running`은 tracker·instance·runtime을 복사하고 `_save()`를 했는데, 당시 `_save`는 큰 상태 전체를 canonical JSON으로 직렬화했다. 결과 회수(`collect`)는 이 callback이 끝나야 진행됐다. 함수별 정확한 시간 분배는 당시 trace가 없어 확정되지 않았다(deep-analysis 6.3절).
- 수정: `c44dd7b`가 native stream을 순서 보존 배치로 묶어 한 owner 트랜잭션으로 적용하고, 완료 결과의 회수를 관찰 callback보다 먼저 하게 했다. 저장 쪽 비용은 B-04 수정과 함께 줄었다. 회귀 시험은 `test_research_reliability.py`의 `ObservationCollectionTests.test_one_native_chunk_is_one_owner_transaction`, `test_returned_result_is_collected_before_unrelated_observation_callbacks`, `NativeBatchTests.test_real_job_completion_is_observed_before_delayed_batch_application`이다.
- 결함 유형: 타이밍·직렬화
- 트리거: 장시간 누적(대형 상태, 사건 수), 동시성·경합(병행 실행의 완료가 겹침)
- 결함 위치 층: L3 배선
- 시험 유출 원인: 시간·규모 미재현. 당시 시험은 작은 상태와 소수 사건으로 callback을 즉시 처리했다. owner 처리 지연과 결과 회수 시점의 관계를 단언하는 시험은 없었다.
- 검증런 유출: VR1~VR5가 범위 안에서 놓쳤다. 비효율 초점이었지만 이 이음새를 지적한 장부 항목은 없다. 정적 독해로는 대형 상태에서만 커지는 지연이 잘 보이지 않는다.
- 가장 싼 포착 시험: owner 처리에 인위 지연(사건당 0.5초)을 넣은 가짜 owner를 준비한다. 한 chunk에 start·tool·final이 든 스트림과 이미 종료한 worker를 준다. 단언은 두 가지다. 결과 반환 callback이 관찰 사건 수와 무관하게 상수 시간 안에 호출되고, owner 트랜잭션이 chunk당 1회다.
- 범주 후보: 관찰 처리와 완료 회수의 직렬 결합(backlog 기아)

### B-06 늦게 처리한 과거 native 사건을 처리 시각의 새 행동으로 판정해 허위 자기 점검 위반과 종료 뒤 운영 점검을 만듦

- 출처: `deep-analysis.md` 7절, `C:\math\.skill-workspace\research-timeline-20260925\scheduling-audit.md` 2절, `C:\math\기억\layer1\M-0342.md` 「확인한 원인과 설계 판단」 둘째 문단, 커밋 `c44dd7b`(`scripts/do_math/observations.py`, `model_runner.py`, `control_transport.py`)
- 발견 경위: 실제 운전(기록 분석)
- 영향 등급: 저하
- 증상: 연구 worker는 05:11:19에 이미 종료 기록과 final을 남겼다. 중앙은 05:11:39에 checkpoint 규칙으로 자기 점검 SC-b113을 열었고, 05:15:55에 그 stdout에 들어 있던 과거 첫 command의 `item.started`를 처리하면서 SC-b113에 `research_action_before_response`를 붙였다. 운영 점검 5건은 모두 대상 native worker의 종료 파일보다 95~804초 뒤에 발동했다. 이 점검들은 이미 끝난 실행을 대상으로 한 불필요한 모델 실행이었다.
- 근본 원인: `ObservationTracker.observe`가 provider 사건의 발생 시각이 아니라 callback 처리 시점의 `clock()`을 썼다. `_start_call`은 처리 시점에 열린 의무와 비교해 응답 전 연구 행동을 판정했다. `execution_status`가 running인 동안에는 periodic 점검도 같은 clock으로 발생했다. `model_runner.observe()`는 한 chunk의 행 사이에 native Job 종료를 다시 확인하지 않았다(scheduling-audit 2절이 인용한 당시 `observations.py:894`·`592`·`979`, `model_runner.py:138`·`186`). 현행 tracker에 지연된 사건을 주입하는 격리 재현으로 같은 판정이 확인됐다.
- 수정: `c44dd7b`가 행의 시작·끝 오프셋과 수신 시각을 보존하고, 의무 전달 시점과 사건의 행 위치를 비교하게 했다. 정확한 요청을 반환한 poll 수신 확인이 없으면 이후 명령을 응답 전 행동으로 분류하지 않는다. 종료된 stream을 재생할 때 live 점검을 만들지 않고, `.control/self-checks/`에 전달 사본을 둔다. 회귀 시험은 `test_research_reliability.py`의 `test_buffered_command_before_delivery_is_not_a_new_action_violation`, `test_terminated_stream_replay_preserves_events_without_live_reviews`, `test_native_poll_ack_requires_the_exact_successful_returned_request`, `test_native_command_after_delivery_without_ack_is_only_missing_response_evidence`, `test_self_check_is_discoverable_inside_the_assigned_workspace`다.
- 결함 유형: 타이밍·직렬화
- 트리거: 시간 경과·기한(자기 점검 창·300초 주기), 특정 전이 순서(worker 종료 뒤 backlog 재생 중 의무 개설)
- 결함 위치 층: L2 인터페이스 요소(관찰 판정 규칙)
- 시험 유출 원인: 시험 없음. `c44dd7b^`의 시험 트리에서 `research_action_before_response`를 언급하는 시험은 0건이다(`git grep`). 의무 개설과 과거 사건 처리의 순서 역전은 시험된 적이 없다.
- 검증런 유출: 판정 행(`observations.py`의 `_miss(obligation, "research_action_before_response")`)은 VR1 앵커 `fa49372`의 610행에 이미 있었다. VR1~VR5가 범위 안에서 놓쳤다.
- 가장 싼 포착 시험: `ObservationTracker` 단위 시험으로, 가상 clock을 쓴다. t=0에 생긴 command 사건을 준비하고, t=301에 자기 점검 의무를 연 뒤, t=400에 그 command 사건을 처리하게 한다. 단언은 `research_action_before_response`가 생기지 않는 것이다. 대조로 전달 뒤에 새로 생긴 사건은 여전히 판정됨을 단언한다.
- 범주 후보: 사건 발생 시각과 처리 시각의 혼동

### B-07 live 운영 점검 입력에 이미 봉인된 대상 checkpoint가 지급되지 않음

- 출처: `deep-analysis.md` 8.2절, `scheduling-audit.md` 3절, `C:\math\기억\layer1\M-0342.md` 「확인한 원인과 설계 판단」 셋째 문단, 커밋 `c44dd7b`(`scripts/do_math/engine.py`의 `_context`, `context_store.py`)
- 발견 경위: 실제 운전(기록 분석)
- 영향 등급: 저하
- 증상: 운영 점검 `EX-01M3AGV6JNJJCYVWRCVZQV4KDP`의 입력 snapshot에는 05:11:39에 봉인된 대상 연구 수행의 `ready_to_submit` checkpoint(artifact와 sha256 포함)가 있었다. 그러나 지급된 catalog 어디에도 그 참조가 없었다. 점검 모델은 "체크포인트 원문이 지급되지 않아 진전을 확인할 수 없다"고 보고했다.
- 근본 원인: 당시 `engine._context`는 `live_review=False`인 복구 경로에서만 `recovery_materials`와 대상 checkpoint를 복원했다. live 점검에는 실행 레코드·발동 observation·task만 주었다(당시 `engine.py:1902`·`1909`·`1959`). 반면 역할 계약 `계약/운영-점검.md:11`은 실제 checkpoint·산출과 진전을 대조하라고 하면서 다른 runs나 중앙 저장소를 직접 읽지 못하게 한다. 계약이 요구하는 근거를 입력 생산자가 주지 않았다.
- 수정: `c44dd7b`가 live와 복구에 공통인 대상 증거 묶음을 만들었다. checkpoint 본문과 그때 포착한 증거 파일을 정확한 참조로 지급하고, 누락·크기 초과·읽기 실패를 명시한다. 회귀 시험은 `test_research_reliability.OperationalInputTests`의 `test_live_review_receives_the_already_sealed_target_checkpoint`, `test_live_review_receives_exact_checkpoint_evidence_files`, `test_large_checkpoint_stays_readable_without_becoming_mandatory_prompt_text`, `test_changed_checkpoint_file_bytes_are_rejected_before_review`다.
- 결함 유형: 인터페이스
- 트리거: 특정 전이 순서(실행 중 checkpoint가 봉인된 뒤 live 점검 발동)
- 결함 위치 층: L2 인터페이스 요소(역할 입력 구성)
- 시험 유출 원인: 단언 약함. `c44dd7b^`의 `test_session_scheduler.py:483` `test_failed_live_review_stops_its_parent_and_preserves_independent_work`와 `test_submission_tools.py:333` `test_legacy_live_review_validates_sidecar_before_applying_continue`는 live 점검을 실제로 돌렸다. 그러나 점검 입력에 대상 checkpoint가 들어 있는지는 단언하지 않았다.
- 검증런 유출: VR1~VR5가 범위 안에서 놓쳤다. 역할 계약 문서와 입력 생산자의 불일치는 이 검증런들의 "생산자·소비자 계약" 초점 안이다. 이 수정 뒤에도 같은 계열의 결함이 남아, 정적 감사(`c4d7838`)가 D3(종료 때 checkpoint 근거 연결 유실)와 D4(재시작 복구가 마지막 유효 checkpoint를 버림)로 다시 찾았다.
- 가장 싼 포착 시험: 봉인된 checkpoint를 가진 running 대상에 live `operational_review` 입력을 `prepare_role_input`으로 만든다(모델 불필요). 단언은 입력 manifest에 checkpoint artifact 참조와 sha256이 있고, 그 파일을 입력 경로에서 읽을 수 있다는 것이다.
- 범주 후보: 역할 계약이 요구하는 근거의 입력 미지급

### B-08 운영 점검의 처분 근거 허용 집합이 입력에 광고되지 않아 정상 처분이 반려됨

- 출처: `deep-analysis.md` 9절, `C:\math\.skill-workspace\research-timeline-20260925\source-audit.md` 1절, `C:\math\기억\layer1\M-0342.md` 「확인한 원인과 설계 판단」 셋째 문단, 커밋 `c44dd7b`(`scripts/do_math/operational_dispositions.py`의 `admissible_basis_refs`, `context_store.py`, `submission.py`, `계약/운영-점검.md`)
- 발견 경위: 실제 운전(기록 분석)
- 영향 등급: 저하
- 증상: 운영 점검 두 건(`EX-01M3AGV6JNJJCYVWRCVZQV4KDP`, `EX-01M3AM2S6BBNFKW4925EGY5NAK`)이 정상 JSON과 `continue` 의견을 반환했다. 그러나 적용에서 `operational disposition cites evidence outside its current input`으로 반려돼 처분이 적용되지 않았다. 두 실행의 점유 시간 합은 1,252.6초다. 중앙 구조 검사 `check_passed=true`와 도메인 적용 거절이 공존했다.
- 근본 원인: `engine._apply_operational_disposition`의 `current_refs`는 대상 EX, action의 `observation_refs`·`obligation_ids`, 반복 보류 event, 대상 결과·checkpoint artifact로만 구성됐다. 그런데 역할 계약은 과제 계약과 권한을 읽고 판단하라고 하고, 입력에는 과제 TK·grant GR·`input/catalog/*.json` 경로가 보였다. 허용 집합은 입력·스키마·문서 어디에도 광고되지 않았다. 모델이 읽은 근거(TK, GR, catalog 경로)를 인용하자 `basis_refs ⊆ current_refs`가 깨졌다. 두 오류 모두 격리 재현으로 확인됐다(source-audit 1절).
- 수정: `c44dd7b`가 하나의 resolver `admissible_basis_refs`로 입력의 허용 참조 목록과 제출·적용 검사를 함께 구성했다. 회귀 시험은 `test_research_reliability.py`의 `test_review_gets_the_same_canonical_basis_set_as_application`, `test_packaged_operational_submission_checks_the_advertised_basis`, `test_assigned_role_uses_exact_registry_references_even_below_input_limit`다.
- 결함 유형: 스키마·계약 불일치
- 트리거: 실제 모델 출력 형태
- 결함 위치 층: L2 인터페이스 요소(제출 검사·처분 적용)
- 시험 유출 원인: 합성 입력이 실제와 다름. `c44dd7b^`의 합성 운영 점검 응답은 `basis_refs`를 항상 대상 실행 ID 하나로 채웠다. 예는 `test_engine.py:116`의 `"basis_refs": [ctx["action"]["target"]]`, `test_observation_audit1.py`의 `["EX-1"]`이다. 이 값은 우연히 허용 집합에 드는 유일한 모양이었다. 거절 문자열을 단언하는 시험은 0건이다.
- 검증런 유출: 거절 행은 VR1 앵커 `fa49372`의 `engine.py:4225`에 있었다. VR1~VR5가 범위 안에서 놓쳤다. 입력 생산자와 적용 검사의 계약 불일치는 이 검증런들의 핵심 초점이었다.
- 가장 싼 포착 시험: 운영 점검 입력을 생성하고, 입력에 광고된 참조 각각을 `basis_refs`로 한 처분을 적용 guard에 넣는 속성 시험이다. 단언은 "입력이 광고한 허용 집합 = 적용 guard가 받는 집합"이다. 모델은 필요 없다.
- 범주 후보: 생산자 광고 집합과 수신 검사 집합의 분리

### B-09 완료 판정 근거의 해시가 후속 형식 수락과 검토 계보 추가에도 바뀌어 완료 과제가 stale이 됨

- 출처: `deep-analysis.md` 11절, `source-audit.md` 2절, `C:\math\.skill-workspace\research-reliability-20260925\design-review.md` 1·2절, `C:\math\기억\layer1\M-0342.md` 「확인한 원인과 설계 판단」 넷째 문단, 커밋 `c44dd7b`(`scripts/do_math/task_scope.py`, `lifecycle_engine.py`, `reporting.py`, `record_schemas/domains.py`)
- 발견 경위: 실제 운전(기록 분석)
- 영향 등급: 저하. 이 인스턴스에서는 완료 판정의 현재성이 틀리게 기록되는 데 그쳤다. 후속 의존 과제가 있으면 `planning.py:555`에서 막힌다는 정지 영향은 코드 경로 추론이며, 이 인스턴스에서는 발현되지 않았다.
- 증상: 05:53:11 snapshot의 과제는 completed, `assessment.current=true`였다. 06:03:46 snapshot에서는 과제 레코드의 유일한 차이가 `assessment.current=false`였다. 그 사이 FR이 candidate/suspended에서 accepted/active로 바뀌며 검증 결과가 붙었고, KN에 `review_cycle_id`가 추가됐을 뿐 증명·해설·제출 의무는 그대로였다. 상태 출력은 이 무효화와 사유를 보여 주지 않았다.
- 근본 원인: `task_scope.assessment_basis`(`fa49372` 기준 215행)는 `planning.action_read_ids(role=research_work)`로 KN에서 FR·XP·IA까지 근거를 넓힌 뒤 레코드 전체를 해시했다. 그래서 관리 정보의 추가도 판정 근거 변경으로 잡혔다. 또 lifecycle은 completed·closed를 자동 재판정에서 제외하고, 상태 보고는 `assessment.current`를 노출하지 않았다.
- 수정: `c44dd7b`가 제출 의무에는 제출 내용 projection을 근거로 쓰고, 지정 전문 판정의 효력 보호는 유지하게 했다. 실제 근거가 바뀐 terminal 과제에는 다시 열지 않고 후속 사건을 한 번 만든다. 회귀 시험은 `test_research_reliability.CompletionBasisTests`의 6개(`test_submission_completion_survives_later_formal_verification_and_review_id` 등)와 `SchedulingResponsibilityTests.test_terminal_stale_assessment_gets_one_followup_without_reopening`이다.
- 결함 유형: 검사(검증 조건 과잉)
- 트리거: 특정 전이 순서(완료 판정 뒤 중앙 형식 수락·동일성 검토 개시)
- 결함 위치 층: L2 인터페이스 요소
- 시험 유출 원인: 단언 약함. `c44dd7b^`의 `test_six_connections.py`에 있는 `test_terminal_history_remains_closed_when_assessment_evidence_changes`는 무관한 원자료 `SO-new` 하나를 추가한 뒤 `assessment.current`가 False가 되고 계획이 생기지 않음을 기대값으로 단언했다. 과잉 무효화와 책임 누락을 정상 동작으로 고정한 셈이다. 완료 뒤 형식 수락이 이어지는 순서는 시험되지 않았다.
- 검증런 유출: VR1~VR5가 범위 안에서 놓쳤다. `task_scope.py`는 보존 bootstrap과 조사 당시 현행이 byte-identical이었다(source-audit 2절).
- 가장 싼 포착 시험: 완료된 과제 fixture에서 근거 KN에 `review_cycle_id`만 추가하고 FR을 candidate에서 accepted로 바꾼 뒤 `assessment_current`가 True임을 단언한다. 짝 시험으로 `lean_code`를 바꾸면 False이고 후속 사건이 정확히 1회 생김을 단언한다.
- 범주 후보: 판정 근거 해시의 범위 과잉(관리 정보 포함)

### B-10 초기화 사건을 첫 후보 준비와 별도로 계획에 전달해 할 일 없는 계획 실행이 생김

- 출처: `deep-analysis.md` 4절 끝·8.1절, `scheduling-audit.md` 1절, `design-review.md` 3절, 커밋 `c44dd7b`(`scripts/do_math/lifecycle_engine.py`)
- 발견 경위: 실제 운전(기록 분석)
- 영향 등급: 저하
- 증상: 첫 연구 계획 `EX-01M3ACRN7DHR3AW9SSBDVJQBES`가 초기화 사건 6개(사용자 결정 2, trust 등록·전환 시작·전환 활성화, 초기화 활성화)를 소유했다. 후보 준비가 아직 진행 중이어서 선택·판정·준비 요청이 모두 빈 결과를 냈다. B-11의 빈 계획과 합쳐 보고 입력 토큰 499,786, 생성→정산 점유 33분 40초다.
- 근본 원인: 활성화가 `initialization_activated`를 보존하고 첫 준비를 배정했다. 그러나 미처리 초기화 사건은 `research_reconsider_due` 이외 모든 pending event를 research_plan에 연결하는 경로로 별도 계획을 즉시 열었다. 사건의 소비 책임이 첫 준비와 분리돼 있었다.
- 수정: `c44dd7b`가 초기화 사건의 정확한 ID를 첫 preparation의 `event_refs`에 결박하고, 수락된 뒤에만 소비하게 했다. 회귀 시험은 `test_research_reliability.SchedulingResponsibilityTests.test_initial_preparation_owns_initial_events_until_accepted`다.
- 결함 유형: 기능
- 트리거: 특정 전이 순서(지식 0인 초기화 활성화 직후)
- 결함 위치 층: L2 인터페이스 요소(상태 전이 규칙)
- 시험 유출 원인: 시험 없음. `c44dd7b^`의 시험 트리에 `initialization_activated`를 언급하는 시험이 0건이다.
- 검증런 유출: VR1~VR5가 범위 안에서 놓쳤다. 비용 결함이며, 장부 요지에 이 경로를 지적한 항목은 없다.
- 가장 싼 포착 시험: 지식 없는 인스턴스를 초기화 활성화까지 진행시키고 lifecycle을 한 번 새로 고친다. 단언은 queue에 research_preparation 하나만 있고 research_plan이 없으며, 초기화 사건이 그 준비의 `event_refs`에 있다는 것이다.
- 범주 후보: 사건 발동·소유의 과잉(판단할 것 없는 계획 배정)

### B-11 정상 착수로 생긴 과제 점유를 준비 상태 상실 사건으로 계획에 올림

- 출처: `deep-analysis.md` 8.1절, `scheduling-audit.md` 1절, `design-review.md` 4절, 커밋 `c44dd7b`(`scripts/do_math/planning.py`, `lifecycle_engine.py`)
- 발견 경위: 실제 운전(기록 분석)
- 영향 등급: 저하
- 증상: 세 번째 계획 `EX-01M3AG828853ZK832JPEPX9NNK`가 `task_readiness_lost` 두 건을 처리했다. 두 사건의 오류는 모두 `task is occupied or has an unresolved wait`였다. 계획은 "연구 수행이 시작 중이므로 기다린다"는 빈 결과를 냈다.
- 근본 원인: `planning.task_ready`(`fa49372` 기준 608행)는 queued·running action의 점유와 미해결 대기를 같은 not_ready 오류 문자열로 합쳤다. lifecycle은 ready→not_ready 전환마다 `task_readiness_lost`를 만들어 research_plan에 보냈다. 정상 착수라는 배정상의 변화가 전략 재판단 사건으로 올라갔다.
- 수정: `c44dd7b`가 정상 점유를 구조적으로 식별해, 계약·권한·원자료·대기 조건이 유효한 점유는 계획 사건으로 만들지 않게 했다. 회귀 시험은 `test_research_reliability.SchedulingResponsibilityTests.test_normal_dispatch_occupancy_does_not_request_a_new_plan`이다.
- 결함 유형: 기능
- 트리거: 특정 전이 순서(계획 선택 → queue → running)
- 결함 위치 층: L2 인터페이스 요소
- 시험 유출 원인: 시험 없음. `c44dd7b^`의 시험 트리에 `task_readiness_lost`를 언급하는 시험이 0건이다.
- 검증런 유출: VR1~VR5가 범위 안에서 놓쳤다.
- 가장 싼 포착 시험: 준비된 과제를 선택해 queue에 넣고 running으로 바꾼 뒤 lifecycle을 새로 고친다. 단언은 새 research_plan이 queue에 없다는 것이다. 대조로 같은 상태에서 grant를 철회하면 계획이 생김을 단언한다.
- 범주 후보: 사건 발동·소유의 과잉(판단할 것 없는 계획 배정)

### B-12 정비용 정지가 종료됐지만 아직 접수되지 않은 정상 결과를 무권한 후보로 만듦

- 출처: `deep-analysis.md` 10절, `C:\math\.skill-workspace\research-timeline-20260925\report.md` 「운영 점검과 정지」, `초기화-효율-개선계획-2026-09-25.md` 「작업 1」 정비 절, 커밋 `ff9b2b9`(`scripts/do_math/maintenance_gate.py` 신규, `scheduled_operator.py`, `cli.py`, `engine.py`)
- 발견 경위: 실제 운전(기록 분석)
- 영향 등급: 저하
- 증상: 동일성 scope 실행의 final은 06:07:39에 완성돼 있었다. 그러나 06:39:12의 설치 교체용 operator pause가 중앙 접수보다 먼저 처리됐고, 07:06:37에 `native candidate no longer has current submission authority`로 미수락 정산됐다. 마지막 운영 점검 결과도 같은 이유로 수락되지 않았다. 동일성 검토와 목표 감사가 이어지지 못했다. pause 요청에서 적용 공개까지 6분 14초가 걸렸다.
- 근본 원인: 당시 운영자가 쓸 수 있는 정지는 사용자 pause 하나였고, 그 의미는 모든 미접수 native 후보의 제출 권한 상실이었다(`engine._capture_native_submission`). 새 배정만 막고 이미 끝난 계산은 정산하는 정비 drain이 없었다. B-05의 접수 지연이 이 상호작용을 키웠다. 보호 규칙 자체는 잘못이 아니며, 정비 목적의 정지 의미가 없었던 것이 결함이다(deep-analysis 10절).
- 수정: `ff9b2b9`이 사용자 pause·HOLD와 구별되는 공개 `quiesce`·`release-quiesce`와 정비 fence를 추가했다. fence는 새 배정을 막고 진행 중 실행을 정산하며, 공개 대기 중인 봉인 산출을 보존한다. 예약 감독도 fence를 확인한다. 회귀 시험은 `test_initialization_efficiency.py`의 `test_quiescence_does_not_release_unknown_execution_or_user_pause`, `test_public_maintenance_fence_survives_restart_and_preserves_user_pause`, `test_sealed_response_survives_deferred_domain_observation_and_git_publication`이다.
- 결함 유형: 기능
- 트리거: 사용자·운영 제어(설치 교체를 위한 정지), 특정 전이 순서(worker 종료 뒤·중앙 접수 전)
- 결함 위치 층: L2 인터페이스 요소(제어 요청 해석)
- 시험 유출 원인: 시험 없음. 정비 drain 의미가 없었으므로 "worker 종료 뒤 접수 전 정지"를 다루는 시험도 없었다.
- 검증런 유출: 해당 없음에 가깝다. 정비 정지는 기능 부재였고 VR1~VR5의 초점(호환 요소·계약 불일치·비효율) 밖이다.
- 가장 싼 포착 시험: native final이 로컬에 완성됐지만 중앙이 아직 접수하지 않은 실행을 fixture로 만들고 정비 정지를 제출한다. 단언은 그 결과가 봉인 보존되고 fence 해제 뒤 편입되며, 사용자 pause였다면 무권한 처리된다는 것이다.
- 범주 후보: 운영 정지와 사용자 정지의 의미 미분리

### B-13 운전 중 임시 수리를 생성 사본 `.agents`에만 적용함

- 출처: `초기화-효율-개선계획-2026-09-25.md` 13행과 「앞선 세 수리에 대한 판정」 표, `C:\math\기억\layer1\M-0341.md` 「맥락」, 커밋 `ff9b2b9`(정본 반영)
- 발견 경위: 실제 운전(초기화 세션의 수리 검토)
- 영향 등급: 잠재
- 증상: 운전 발현은 없다. RI-A 초기화 세션에서 느림을 줄이려고 가한 수리 5파일(`submission.py`의 참조 목록 인덱스 재사용, `initialization.py`의 파일 검사 병렬화, 능력 관측 재사용 등)이 생성 사본 `.agents/skills/do-math`에만 있었다. `build_skill_mirrors.py --check --target .agents`는 이 5파일의 드리프트를 보고했다. 정본에서 사본을 재생성하면 수리가 사라지는 상태였다.
- 근본 원인: 설치본을 운전 중에 직접 고치는 경로에, 정본 `.claude/skills` 선반영과 드리프트 검사를 요구하는 절차가 없었다. 두 폴더는 링크가 아니고 생성기는 `.claude`를 정본으로 삼는다.
- 수정: `ff9b2b9`이 수리를 정본으로 옮겨 재검토하고, 보완한 판본으로 사본을 다시 생성했다. 절차적 재발 방지 장치는 추가되지 않았다.
- 결함 유형: 빌드·패키지
- 트리거: 사용자·운영 제어(운전 중 긴급 수리)
- 결함 위치 층: 계약·스키마(배포 규범). 5절의 어느 값에도 정확히 맞지 않아 가장 가까운 값을 골랐다(관찰 절 참조).
- 시험 유출 원인: 시험 없음에 가장 가깝다. 드리프트를 잡는 `build_skill_mirrors.py --check`는 있었지만, 운전 중 수리 경로에서 그것을 실행하게 하는 장치가 없었다. 나중에 실행하자 정확히 5파일을 보고했다. 서식에 "있는 검사가 실행되지 않음"에 해당하는 값이 없다(관찰 절 참조).
- 검증런 유출: 해당 없음(운전 중 설치본 변경)
- 가장 싼 포착 시험: 설치본으로 연구 실행기를 기동하기 전에 `build_skill_mirrors.py --check`를 실행하고, 드리프트가 있으면 기동을 거부한다. bootstrap의 설치 manifest 대조와 같은 위치에 둘 수 있다.
- 범주 후보: 정본·생성 사본의 이원화

### B-14 신뢰 manifest의 모집단 완전성을 검사하지 않아 여섯 파일 목록으로 환경이 활성화됨

- 출처: `C:\math\.skill-workspace\initialization-review-20260925\review.md` 2절 F01·4-4절·5절, `C:\math\docs\do-math\initialization-repairs-20260925.md` 「발견별 처리」 F01·F02·「신뢰 환경과 형식 검사의 범위」, `C:\math\기억\layer1\M-0346.md` 「수리 과정에서 수정한 판단」 첫 문단, 커밋 `a299fd8`(`scripts/do_math/trust_inventory.py` 신규, `trust_validation.py`, `setup_lean.py`)
- 발견 경위: 실제 운전(RI-B 초기화 검토)
- 영향 등급: 저하. 신뢰 환경이 실제 실행 환경을 덮지 못한 채 active가 됐다. 형식 결과의 보증 범위가 틀린 상태이며, 거짓 정리가 통과한 사례는 관측되지 않았다.
- 증상: 운전자가 전체 환경 대신 `lean.exe`, `Prelude.lean`, `lake.exe`, `Mathlib.lean`, `Mathlib.olean`, `formal.py` 여섯 파일로 manifest를 등록했다. 활성화 영수증은 정확히 6개 파일, 1,658,605바이트만 검사했다고 기록했다. DLL, 표준 라이브러리 `.olean`, Mathlib 전이 import의 빌드 파일은 목록에 없었다.
- 근본 원인: `trust_validation.manifest_file_errors`(RI-B 당시 80행)는 여섯 role의 존재·절대 경로·중복·해시 모양만 검사했다. `_verify_environment_files`는 그 목록만 순회했다. 실제 Lean 명령의 실행 파일이 목록에 있는지, checker role이 실제 검사 코드인지, 필요한 `.olean`·DLL이 빠졌는지는 확인하지 않았다. 격리 재현에서 평범한 텍스트 파일 여섯 개에 role을 붙이자 `verified`가 반환됐다(review 5절). 운전자의 축소 등록이 직접 원인이고, 수신 검사가 그것을 거부하지 못한 것이 제품 결함이다.
- 수정: `a299fd8`이 `trust_inventory.py`로 채택 root의 파일 전건 inventory를 만들고, 준비·활성화·형식 사용에서 같은 제외 규칙으로 관측하게 했다. root 중첩, 경로 식별 충돌, reparse, 목록 추가·누락을 거부하고, 실행 파일과 검색 경로가 채택 범위 안인지 결박한다. 회귀 시험은 `test_environment_validation.py`의 `test_inventory_detects_omissions_additions_and_unrelated_executables`, `test_inventory_does_not_silently_collapse_ambiguous_path_identities`, `test_membership_changes_during_scan_are_not_verified`, `test_external_search_roots_are_not_covered_by_an_unchanged_local_manifest`, `test_library_change_with_unchanged_toolchain_metadata_fails_validation`, `test_compiler_job_does_not_inherit_unregistered_library_overrides`다.
- 결함 유형: 검사(누락)
- 트리거: 사용자·운영 제어(운전자가 작성한 manifest), 설정·환경(대용량 설치)
- 결함 위치 층: L2 인터페이스 요소(신뢰 등록·활성화 관문)
- 시험 유출 원인: 합성 입력이 실제와 다름, 시험 없음. `a299fd8^`의 `research_fixtures.trust_fixture`는 여섯 role마다 `"CORE_TESTS synthetic " + role` 텍스트 파일 하나로 manifest를 만들었다. 결함 패턴 자체가 정상 fixture였고, 모집단 완전성을 단언하는 시험은 없었다. review 13절도 기존 11개 검사의 통과가 목록 완전성을 보증하지 못한다고 적었다.
- 검증런 유출: 같은 역할 집합 검사(`required_roles`)는 VR1 앵커 `fa49372`의 `initialization.py:98`에 이미 있었다. `ff9b2b9`에서 `trust_validation.py`로 옮겨졌다. VR1~VR6이 모두 범위 안에서 놓쳤다. 특히 VR6은 "최근 실사용 수리의 불충분함과 파급 누락"을 명시 초점으로 삼았는데도 놓쳤다.
- 가장 싼 포착 시험: 실제 Lean 없이 임시 root에 실행 파일·DLL·`.olean` 등 N개 파일을 둔다. 첫 시험은 그중 하나를 뺀 manifest로 등록하고 거부를 단언한다. 둘째 시험은 목록 밖 파일을 바꾼 뒤 활성화하고 invalid를 단언한다. 파일 시스템만 쓰며 1초 안에 끝난다.
- 범주 후보: 선언 모집단의 완전성 미검사(라벨을 완전성으로 대체)

### B-15 환경 검증 증거의 내용을 읽지 않고 `verified` 문자열만 소비함

- 출처: `review.md` 2절 F02·6절, `initialization-repairs-20260925.md` F01·F02, `C:\math\기억\layer1\M-0346.md`, 커밋 `a299fd8`(`scripts/do_math/trust_validation.py`, `setup_lean.py`)
- 발견 경위: 실제 운전(RI-B 초기화 검토의 격리 재현)
- 영향 등급: 잠재. RI-B의 실제 validation 파일은 정상 성공 기록이어서 잘못된 증거가 쓰이지는 않았다.
- 증상: 운전 미발현. 재현에서 세 가지가 모두 통과했다. 존재하지 않는 validation 경로, `status=failed`·exit_code 17·다른 toolchain을 가진 파일, 목록 밖 의존 파일의 변경이다. 대조로 목록 안 파일을 바꾸면 invalid였다.
- 근본 원인: `trust_validation.manifest_errors`(RI-B 당시 73행)는 `validation.status == "verified"`와 비어 있지 않은 `evidence_refs`만 확인했다. 참조의 바이트·해시·상태·종료 코드·명령·toolchain은 읽지 않았고, 증거는 외부 절대 경로 문자열로만 참조했다.
- 수정: `a299fd8`이 실제 소스·명령·종료 코드·출력·시작·종료 시각·전후 toolchain·inventory 해시를 담은 자체 완결 검증 record를 요구하고, 중앙이 그 내용을 대조하게 했다. 회귀 시험은 `test_environment_validation.test_success_label_cannot_replace_failed_or_mismatched_evidence`다.
- 결함 유형: 검사(누락)
- 트리거: 기타(잘못되거나 실패한 검증 기록이 제출될 때)
- 결함 위치 층: L1 원시(단일 값 검증기)
- 시험 유출 원인: 합성 입력이 실제와 다름. `a299fd8^`의 `trust_fixture`는 `evidence_refs`에 `"CORE_TESTS synthetic trust fixture; not a Lean build"`라는 자유 문자열을 넣었고, `test_approved_five_repairs.py`는 `['fixture']`를 넣었다. fixture 자체가 이 결함에 기대어 통과했다.
- 검증런 유출: 이 조건은 VR1 앵커 `fa49372`의 `initialization.py:120` 부근에 이미 있었다. VR1~VR6이 범위 안에서 놓쳤다.
- 가장 싼 포착 시험: 표 기반 단위 시험이다. 없는 경로, 손상 JSON, `status=failed`, 명령 불일치, toolchain 불일치 각각을 `evidence_refs`로 준 manifest에 대해 오류를 단언한다.
- 범주 후보: 성공 라벨을 증거 내용 대신 소비

### B-16 과제 준비 판정과 실제 프로필 선택이 다른 규칙을 써서 계획 제출이 반려됨

- 출처: `review.md` 2절 F03·7절, `initialization-repairs-20260925.md` F03, `C:\math\기억\layer1\M-0346.md` 「수리 과정에서 수정한 판단」 둘째 문단, 커밋 `a299fd8`(`scripts/do_math/planning.py`의 `task_ready`, `model_policy.py`의 `work_profile_selection`)
- 발견 경위: 실제 운전
- 영향 등급: 저하. 첫 계획이 반려되고 계약 개정으로 돌아갔다. 인스턴스 정지는 이어진 B-17 때문이다.
- 증상: 최초 과제는 `difficulty=low`, `importance=high`였고, 요구 등급은 high인데 유일한 `profile_refs`는 low 연구 수행 프로필이었다. 두 프로필의 실제 모델은 모두 gpt-6-sol이었다. `task_ready`는 ready를 반환했고, 독립 계약 검토도 approved했다. 그러나 18:31:41에 첫 연구 계획이 "모델 요구를 만족하는 허용 프로필 없음"으로 반려됐다.
- 근본 원인: `planning.task_ready`(`a299fd8^` 기준 513행 이하)는 계약 검토가 승인한 프로필이 현재 판본인지만 봤다. 과제 평가와 역할 하한으로 계산하는 `model_policy.selection`의 선택 가능성은 확인하지 않았다. 후보 수신·평가 보충·준비 상태·최종 배정이 서로 다른 선택 규칙을 썼다.
- 수정: `a299fd8`이 `task_ready`에서 `work_profile_selection`을 호출해, 계약이 승인한 프로필 밖이면 not_ready와 `contract_revision` 대기를 반환하게 했다. 불일치한 미착수 과제는 재준비로 돌린다. 회귀 시험은 `test_initialization_review_repairs.WorkProfileAdmissionTests`의 `test_reviewed_contract_cannot_be_ready_with_an_inadequate_allowed_profile`, `test_policy_change_reprepares_an_unstarted_incompatible_contract`다.
- 결함 유형: 검사(누락)
- 트리거: 실제 모델 출력 형태(후보 준비가 low 프로필 하나만 지정), 설정·환경(모든 등급이 같은 모델)
- 결함 위치 층: L2 인터페이스 요소
- 시험 유출 원인: 합성 입력이 실제와 다름. `a299fd8^`의 `research_fixtures.bind_candidates`는 후보의 `profile_refs`에 전달된 모든 research_work 프로필(전 등급)을 넣었다. 그래서 요구 등급과 허용 프로필의 불일치가 fixture에서 생길 수 없었다.
- 검증런 유출: `task_ready`와 `selection`의 규칙 분리는 VR1 앵커 이전부터 있었다. VR1~VR6이 범위 안에서 놓쳤다. 두 소비자의 규칙 불일치는 "생산자·소비자 계약" 초점에 해당한다.
- 가장 싼 포착 시험: 속성 시험이다. (difficulty, importance) 조합과 등급별 profile_refs 부분집합을 모두 열거하고, `task_ready`가 ready이면 `selection`이 예외 없이 그 허용 목록 안의 프로필을 고른다는 것을 단언한다. 순수 함수만 쓴다.
- 범주 후보: 같은 판단의 소비자별 규칙 분기

### B-17 운영 retry가 살아 있는 자동 후속과 충돌하고, 그 충돌이 설치 결함으로 승격돼 인스턴스가 설치 수리 대기에 멈춤

- 출처: `review.md` 2절 F04·8절, `initialization-repairs-20260925.md` F04·「수정한 전제와 제외한 구현」, `C:\math\기억\layer1\M-0346.md` 「맥락」 둘째 문단·「수리 과정에서 수정한 판단」 셋째 문단, 커밋 `a299fd8`(`scripts/do_math/activities.py`의 `successor_state`, `operational_dispositions.py`의 `reconcile_recovery`, `repair_execution.py`의 `resume_installation_repair`, `engine.py`)
- 발견 경위: 실제 운전
- 영향 등급: 정지
- 증상: 사건 순서는 다음과 같다.
  1. 18:32:08 반려된 계획의 같은 활동에서 자동 후속 실행이 시작됐다.
  2. 18:32:12 이전 실패를 대상으로 운영 점검이 시작됐다.
  3. 18:33:51 운영 retry가 `continuation requires the activity's current attempts to end`로 반려됐다.
  4. 18:35:17 후속 계획이 accepted로 끝나 계약 개정을 요청했다.
  5. 18:37:22 운영 점검이 앞의 retry 오류를 설치 결함으로 판단한 repair 처분이 적용됐다.
  6. 18:41:03 엔진이 종료 코드 0으로 끝나고 설치 수리 대기(pending 2, 활성 실행 0)에 들어갔다.

  수행 가능한 독립 영향 검토도 전역 설치 수리 fence 뒤에서 기다렸다. 다음 감독 tick은 2시간 주기였다. 사용자가 HOLD·pause·quiescence로 원 인스턴스를 멈추고 수리했다.
- 근본 원인: 운영 처분 적용(RI-B 당시 `engine.py:4336`)이 target 실행 하나의 종료만 확인하고, 이미 시작된 같은 활동의 후속과 현재 의무를 반영하지 않은 채 `activities.continue_activity`를 호출했다. 이 함수의 정당한 방어 오류가 운영 점검에서 설치 결함으로 해석됐다. 설치 수리의 target 검사(`repair_execution.py:146`)도 원 실패의 종료·error·artifact만 보고, 성공한 후속이 그 실패 의무를 해소했는지는 확인하지 않았다. 과거 snapshot으로 같은 오류가 재현됐다(review 8절).
- 수정: `a299fd8`이 명시적 continuation 계보를 읽는 `activities.successor_state`를 추가했다. 이를 모든 retry·resume 소비자와 운영 처분 허용 근거에서 쓰고, 이미 후속이 있으면 retry 처분을 `superseded`로 정산한다. 설치 수리가 끝났을 때 기존 후속이 있으면 새 시도를 만들지 않는다. 회귀 시험은 `test_initialization_review_repairs.RecoveryOwnershipTests`의 6개와 `test_repair_execution.test_operational_retry_of_an_ended_attempt_keeps_its_registered_successor`다.
- 결함 유형: 타이밍·직렬화
- 트리거: 동시성·경합(자동 후속과 운영 retry가 동시에 발생), 재시작·복구·재개
- 결함 위치 층: L2 인터페이스 요소(복구 처분 적용)
- 시험 유출 원인: 조합·순서 미탐색. `a299fd8^`의 시험 트리에서 `continuation requires the activity's current attempts to end`를 다루는 시험은 0건이다. 운영 retry와 설치 수리 시험은 후속이 없는 실패 대상만 썼다.
- 검증런 유출: 방어 행(`activities.py:147`)은 VR1 앵커 `fa49372`에 이미 있었다. VR1~VR6이 범위 안에서 놓쳤다. 관련 계보 결함인 VR4 R1-21("새 계획이 실패 의무를 해소해도 기존 활동은 대기로 남는다")과 정적 감사 D6(취소된 신뢰 검사 재실행의 계보 미저장)은 따로 찾아졌다.
- 가장 싼 포착 시험: 실패 실행 E1과 같은 활동의 running 후속 E2가 있는 runtime에 E1 대상 retry 처분을 적용한다. 단언은 세 가지다. 오류 없이 superseded로 정산되고, 설치 수리 대기가 생기지 않으며, 후속 실행이 정확히 하나다. 모델 없이 메모리 상태로 가능하다.
- 범주 후보: 복구 계보의 단일 소유자 부재(자동 후속과 운영 처분의 경합)

### B-18 초기화가 사용자 요청 전문 대신 축약한 수학 목표를 원입력으로 보존함

- 출처: `review.md` 2절 F05·9절, `initialization-repairs-20260925.md` F05, 커밋 `a299fd8`(`scripts/do_math/cli.py`)
- 발견 경위: 실제 운전
- 영향 등급: 저하
- 증상: 불변 원입력은 30코드 포인트·54바이트의 수학 문장뿐이었다. 사용자의 모델 상한(gpt-6-sol), 새 인스턴스 요구, 절차 준수 요구가 원문 해석의 모집단에 없었다. 독립 검사가 사용자 요청 전체를 확인했다고 말할 수 없었다.
- 근본 원인: `initialize(... source_input=goal)` 구조가 전체 요청과 정련된 목표를 하나로 다뤘다. CLI에 원문을 따로 넘기는 인자가 없었다.
- 수정: `a299fd8`이 `init --request-text`·`--request-text-file`을 추가해 원문을 별도로 보존한다. 생략하면 목표 문자열을 원문으로 쓴다. 회귀 시험은 `test_cli.test_original_request_is_preserved_separately_from_the_mathematical_goal`이다.
- 결함 유형: 인터페이스
- 트리거: 사용자·운영 제어(수학 목표 외 제약이 있는 요청)
- 결함 위치 층: L3 배선(CLI 진입)
- 시험 유출 원인: 시험 없음. 원문 보존 필드가 따로 없었으므로 그 속성을 단언할 대상도 없었다.
- 검증런 유출: VR1~VR6 범위 안이지만, 결함이라기보다 요구 누락이어서 코드 독해로 드러나기 어렵다.
- 가장 싼 포착 시험: 제약 문장을 포함한 요청으로 `init`을 실행한다. 단언은 불변 원입력의 바이트가 요청 전문과 같고, 목표 필드와 구별된다는 것이다.
- 범주 후보: 사용자 원문 보존 범위의 축소

### B-19 운영자가 위임 범위에서 정한 설정과 사용자의 직접 결정이 같은 출처로 기록됨

- 출처: `review.md` 2절 F06·9절, `initialization-repairs-20260925.md` F06, 커밋 `a299fd8`(`references/초기화-운전.md` 절차 보완)
- 발견 경위: 실제 운전
- 영향 등급: 저하
- 증상: grant 만료 2026-12-31, 관찰 window 120초, 독립 지속 정책은 운전자가 정했다. 그러나 통치 기록은 이 구조화 JSON을 `actor=user`로 남겼고, 선택 이유는 보존되지 않았다.
- 근본 원인: 초기화 운전 절차가 위임 범위의 운영 선택과 그 이유, 선택자를 기록하게 하지 않았다. 제어 기록에도 둘을 구별하는 필드가 없었다.
- 수정: `a299fd8`이 운전 절차에서 승인된 위임 범위에서 정한 설정과 그 이유를 기록하게 했다. 새 사용자 확인 단계는 추가하지 않았고, 코드상 출처 필드 추가는 확인되지 않았다(구현 문서 표 F06의 "운전 절차 보완"). 회귀 시험은 없다.
- 결함 유형: 문서·계약
- 트리거: 사용자·운영 제어
- 결함 위치 층: 계약·스키마
- 시험 유출 원인: 시험 없음. 문서 절차의 결함이다.
- 검증런 유출: 해당 없음(운전 절차의 요구 누락)
- 가장 싼 포착 시험: 통치 제어 스키마에 `selected_by`와 이유 필드를 두고, operator 출처 요청이 `actor=user`로 저장되지 않음을 단언하는 저장 시험이다. 문서만으로는 결정적 시험이 어렵다.
- 범주 후보: 결정 출처의 혼동

### B-20 운전 대화가 필수 용어집을 잘린 출력으로 읽고도 전문을 읽은 것으로 진행함

- 출처: `review.md` 2절 F07·3절 1~2행·9절, `initialization-repairs-20260925.md` F07, 커밋 `a299fd8`(진입 문서의 구간별 완독 절차)
- 발견 경위: 실제 운전
- 영향 등급: 저하
- 증상: 첫 도구 호출이 GLOSSARY와 README를 병렬로 읽었고 출력 전체가 잘렸다. 이후 일부만 다시 읽어 "GLOSSARY 전문을 먼저 읽는다"는 절차가 이행되지 않았다. 이어진 F08·F03류 오조작의 배경이 됐다.
- 근본 원인: 진입 문서가 필수 문서의 크기(GLOSSARY 76,126바이트)와 도구 출력 한도를 고려한 구간 읽기와 잘린 구간 회수를 요구하지 않았다.
- 수정: `a299fd8`이 진입 문서에 문서별·구간별 완독과 잘린 구간 회수 절차를 명시했다. 회귀 시험은 없다.
- 결함 유형: 문서·계약
- 트리거: 설정·환경(운전 도구의 출력 한도)
- 결함 위치 층: 계약·스키마
- 시험 유출 원인: 시험 없음(운전 AI의 절차 준수)
- 검증런 유출: 해당 없음
- 가장 싼 포착 시험: 소프트웨어 시험으로 결정적으로 잡기 어렵다. 가장 싼 대리 검사는 진입 절차가 한 번에 읽게 하는 필수 문서의 바이트 합이 운전 도구의 출력 한도 이하인지를 확인하는 정적 검사다.
- 범주 후보: 필수 입력의 절단 독해

### B-21 운전자가 프로필과 승인 해시를 수작업으로 조립해 초기 채택이 반려됨

- 출처: `review.md` 2절 F08·3절 11~12행·9절, `initialization-repairs-20260925.md` F08, 커밋 `a299fd8`(`scripts/do_math/cli.py`의 `select-profile`, `prepare-import-approval`)
- 발견 경위: 실제 운전
- 영향 등급: 저하
- 증상: 최초 adopt에 low 의도 해석 프로필을 지정해 역할 하한 때문에 반려됐다. high로 바꿔 재시도했다. 같은 수작업 선택 문제가 후보 과제(B-16)에서도 반복됐다.
- 근본 원인: 역할·과제 평가에서 선택 가능한 정확한 프로필을 조회하는 공개 경로가 없었다. 전체 프로필 표에는 모든 등급이 같은 모델로 표시돼 tier 차이가 눈에 띄지 않았다.
- 수정: `a299fd8`이 읽기 전용 `select-profile`과 독립 검사 결과에서 승인 초안만 만드는 `prepare-import-approval`을 추가했다. 회귀 시험은 `test_cli.test_profile_selection_respects_the_role_floor_without_model_execution`과 `test_initialization_review_repairs.ApprovalDraftTests.test_exact_draft_reaches_existing_consumer_without_mutating_source_state`다.
- 결함 유형: 인터페이스
- 트리거: 사용자·운영 제어
- 결함 위치 층: L3 배선(CLI 진입)
- 시험 유출 원인: 시험 없음(조회 경로 부재)
- 검증런 유출: 해당 없음(도구 부재)
- 가장 싼 포착 시험: 역할별 하한이 있는 설정으로 `select-profile --role intent_interpretation`을 실행한다. 단언은 반환 프로필이 하한 등급 이상이고 adopt가 그대로 수락한다는 것이다.
- 범주 후보: 운전자 수작업 조립 경로

### B-22 초기화용 제한 실행이 활성화를 넘어 후보 준비와 계약 검토까지 진행함

- 출처: `review.md` 2절 F09·3절 16~19행·10절, `initialization-repairs-20260925.md` F09, 커밋 `a299fd8`(`scripts/do_math/cli.py`, `scheduler.py`의 `run --until-active`)
- 발견 경위: 실제 운전
- 영향 등급: 저하
- 증상: `run --max-steps 4`가 trust 활성화, 독립 의도 검사, 후보 준비, 작업 계약 검토까지 수행했다. 활성화 뒤 약 4분을 운전 대화가 직접 기다렸다.
- 근본 원인: `max-steps`는 활성화 관문이 아니라 action 개수를 세었다. 초기화 관문 통과 시 반환하는 종료 조건이 없었다.
- 수정: `a299fd8`이 `run --until-active`를 추가했다. 활성화 직후 연구 배정 전에 반환하고 후속 queue는 보존한다. `research_fixtures.py`가 `engine.run(until_active=True)`를 쓰고, `test_cli_advanced.py`가 인자 전달을 확인한다. 전용 회귀 시험 이름은 확인되지 않았다.
- 결함 유형: 인터페이스
- 트리거: 사용자·운영 제어
- 결함 위치 층: L3 배선(엔진 실행 루프, CLI 진입)
- 시험 유출 원인: 시험 없음(종료 조건 부재)
- 검증런 유출: 해당 없음
- 가장 싼 포착 시험: 활성화 직전 상태의 인스턴스로 `run(until_active=True)`를 실행한다. 단언은 lifecycle이 active이고 research 역할 실행이 0건이라는 것이다.
- 범주 후보: 제한 실행의 종료 조건 불일치

### B-23 역할 입력에 같은 프로필 본문이 반복 삽입돼 입력이 큼

- 출처: `review.md` 2절 F10·10절, `initialization-repairs-20260925.md` F10·「비용 측정과 검증 자료」, `C:\math\기억\layer1\M-0346.md` 「실익과 검증의 경계」, 커밋 `a299fd8`(`scripts/do_math/context_store.py`)
- 발견 경위: 실제 운전(입력 실측)
- 영향 등급: 저하
- 증상: 네 초기 역할의 최초 prompt가 324,018~401,754바이트였고, 보고 input tokens 합계는 1,687,206(cached 1,290,624)이었다. 준비·계획에는 `profile_selection` 약 64KB가 직접 들어갔다.
- 근본 원인: 37개 프로필의 직접 입력을 전문으로 반복 제공했다. 공통 문서(GLOSSARY 76KB, 공통 실행 77KB)도 크지만, 이번 수리는 프로필 반복만 대상으로 삼았다.
- 수정: `a299fd8`이 작은 비교 목록과 정확한 전문 참조를 제공하게 했다. 같은 37개 프로필의 직접 입력이 60,381바이트에서 12,529바이트로 줄었다. 전용 회귀 시험 이름은 확인되지 않았다.
- 결함 유형: 알고리즘
- 트리거: 장시간 누적(입력 크기)
- 결함 위치 층: L2 인터페이스 요소(역할 입력 구성)
- 시험 유출 원인: 시간·규모 미재현(입력 바이트 상한을 단언하는 시험 없음)
- 검증런 유출: VR1~VR6 범위 안이다. 입력 비용은 VR5 R1-31·R1-32 등 다른 경로에서 지적됐고, 이 경로는 놓쳤다.
- 가장 싼 포착 시험: 프로필 37개 설정으로 계획 역할 입력을 만든다. 단언은 프로필 관련 직접 입력 바이트가 고정 상한(예: 16KB) 이하이고, 모든 프로필 전문이 참조로 도달 가능하다는 것이다.
- 범주 후보: 역할 입력의 중복 전문 삽입

### B-24 계측 쓰기 실패의 원인 정보를 버리고, Windows 원자 교체가 열린 독자와 충돌해 실패함

- 출처: `review.md` 2절 F11·11절, `initialization-repairs-20260925.md` F11·「수정한 전제와 제외한 구현」 둘째 문단, `C:\math\기억\layer1\M-0346.md` 「수리 과정에서 수정한 판단」 넷째 문단, `C:\math\docs\do-math\수리-구현-결과-2026-09-24.md` 「검증 결과」(시험 중 결과 파일 교체 오류 2회), 커밋 `a299fd8`(`scripts/do_math/file_io.py` 신규, `operation_trace.py`, `observations.py`, `run_tests.py`)
- 발견 경위: 실제 운전(`operation telemetry write failed` 경고), 시험 실행(WinError 5 재현)
- 영향 등급: 저하
- 증상: 제한 run과 독립 엔진에서 `operation telemetry write failed` 경고가 실제로 났지만, 원인 연산과 errno는 남지 않았다. 수리 검증 중 Windows에서 최종 JSON 보고서 교체가 WinError 5로 실패했다. 삭제 공유를 허용한 reader를 추가해도 `MoveFileEx` 교체는 실패했다. 2026-09-24 시험 실행에서도 결과 파일 교체 오류가 두 번 났다.
- 근본 원인: 두 가지다. 첫째, `OperationTrace.emit`은 `OSError`를 잡되 실패한 파일 연산·errno·winerror를 버렸다. 둘째, 공통 원자 교체가 `MoveFileEx`에 기대어, 다른 프로세스가 대상을 열고 있으면 Windows에서 교체가 거부됐다. 실제 계측 경고의 원인이 둘째와 같은지는 정보가 없어 확정되지 않았다(review 13절).
- 수정: `a299fd8`이 `file_io.py`에 `FileRenameInfoEx`의 `REPLACE_IF_EXISTS | POSIX_SEMANTICS` 교체를 도입했다. 제어·감독·관찰·계측·시험 보고 파일에 적용하고, 같은 파일명 교체에만 제한된 재시도를 둔다. 계측 실패는 연산과 오류 번호를 남긴다. 가변 파일명 버퍼의 끝 문자 공간 누락도 실제 교체 검사에서 고쳤다. 회귀 시험은 `test_file_io.MetadataPublicationTests`의 5개와 `test_initialization_efficiency.test_telemetry_failure_identifies_operation_without_leaking_exception_text`다.
- 결함 유형: 외부 경계
- 트리거: 실제 외부 도구 동작(Windows 파일 공유 의미), 동시성·경합(열린 독자와 교체의 겹침)
- 결함 위치 층: 경계 어댑터
- 시험 유출 원인: 시간·규모 미재현. 열린 독자가 있는 상태의 교체를 결정적으로 만드는 시험이 없었다. 실패는 병행 시험 실행 중에 우연히만 드러났다.
- 검증런 유출: VR1~VR6 범위 안이지만 Windows 파일 공유 의미는 정적 독해로 드러나기 어렵다. VR7 R1-14·R1-50은 수정 뒤에도 관찰 제어·worker 상태 파일이 이 공통 게시 경로를 쓰지 않는 파급 누락을 찾았다.
- 가장 싼 포착 시험: Windows에서 대상 파일을 한 핸들로 열어 둔 채 공통 원자 교체를 호출한다. 단언은 교체가 성공하고, 열린 핸들은 옛 내용을, 새로 연 핸들은 새 내용을 읽는다는 것이다. 수 밀리초 안에 끝난다.
- 범주 후보: OS 파일 교체 의미의 가정

### B-25 준비용 Lean 컴파일이 소유 Job과 진행 관측 없이 실행됨

- 출처: `review.md` 2절 F12·3절 13행·11절, `initialization-repairs-20260925.md` F12, 커밋 `a299fd8`(`scripts/setup_lean.py`, `scripts/do_math/formal.py`)
- 발견 경위: 실제 운전
- 영향 등급: 저하
- 증상: `setup_lean --verify-only`가 316.398초 동안 출력 없이 실행돼, 운전자가 프로세스 목록으로 진행을 확인했다. 실행 자체는 성공했고 고아 프로세스는 관측되지 않았다.
- 근본 원인: `setup_lean.verify_environment`(`a0e6c2f`에서 도입)가 smoke 컴파일을 일반 `subprocess.run`으로 실행했다. formal 쪽 `_job_run`의 Job 수명 관리와 진행 sidecar를 쓰지 않았다.
- 수정: `a299fd8`이 준비 프로세스가 Windows Job Object로 compile의 자식 프로세스를 소유하고 종료를 확인하게 했다. 설치 관측 전후와 compile의 단계·시간·프로세스 정보도 보존한다. 관련 시험 변경은 `test_environment_validation.py`에 있으나, Job 소유를 직접 단언하는 전용 시험 이름은 확인되지 않았다.
- 결함 유형: 기능
- 트리거: 장시간 누적(Mathlib import 컴파일)
- 결함 위치 층: 경계 어댑터(Lean 실행)
- 시험 유출 원인: 대역이 가림. `a0e6c2f`와 `a299fd8^`의 `test_environment_validation` 시험은 `setup_lean.subprocess.run`을 `patch`로 대체해 실제 프로세스 생성 경로를 돌리지 않았다.
- 검증런 유출: 이 함수는 `a0e6c2f`(09-25 01:52)에서 들어왔다. 그 뒤의 VR6이 범위 안에서 놓쳤다.
- 가장 싼 포착 시험: 컴파일 명령 대신 자식 프로세스를 하나 더 띄우는 작은 Python 스크립트를 `verify_environment`에 주고 완료시킨다. 단언은 부모 종료 뒤 자식이 남지 않고, 진행 sidecar에 단계·PID가 기록된다는 것이다.
- 범주 후보: 외부 프로세스 수명 관리의 경로별 불일치

### B-26 시작·대기·설치 수리의 차단 사유와 다음 담당이 흩어져 있고, 설치 수리 요청 뒤 감독이 정기 주기까지 기다림

- 출처: `review.md` 2절 F13·11절, `initialization-repairs-20260925.md` F13, 커밋 `a299fd8`(`scripts/do_math/reporting.py`의 `operating_summary`, `scheduled_operator.py`, `cli.py`)
- 발견 경위: 실제 운전
- 영향 등급: 저하
- 증상: B-17로 설치 수리 대기에 들어간 뒤 엔진은 종료 코드 0으로 끝났다. 공개 status의 일반 `waiting_actions` 요약만 보면 영향 검토 대기로 오해하기 쉬웠고, 검토자도 추가 필드를 읽고서야 원인을 바로잡았다. 정기 감독의 다음 예약은 20:11:11, 즉 최대 2시간 뒤였다.
- 근본 원인: 현재 인스턴스의 최상위 차단 사유·다음 소유자·실제 실행 여부·다음 예약을 한 곳에 싣는 조회가 없었다. 설치 결함 진단이 수락돼도 모델 없는 즉시 감독 wake가 없었다.
- 수정: `a299fd8`이 현재·과거 상태에 `operating_summary`를 제공하고, 설치 결함 진단이 수락되면 모델 없이 상태를 검사하는 예약 감독을 즉시 요청하게 했다. HOLD·pause·fence는 존중한다. 회귀 시험은 `test_operator.test_accepted_installation_repair_requests_supervisor_without_periodic_delay`다.
- 결함 유형: 기능
- 트리거: 시간 경과·기한(정기 감독 주기), 재시작·복구·재개
- 결함 위치 층: L3 배선(예약 운영자)
- 시험 유출 원인: 시험 없음(즉시 wake 경로 부재)
- 검증런 유출: 해당 없음(기능 부재)
- 가장 싼 포착 시험: 설치 결함 처분을 수락시키고 예약 어댑터 대역의 호출 기록을 본다. 단언은 즉시 wake 요청이 1회 기록되고, status 요약의 차단 사유가 `installation_repair`라는 것이다.
- 범주 후보: 차단 상태의 가시성·복구 트리거 부재

### B-27 snapshot export가 파일마다 Git 자식 프로세스를 시작함

- 출처: `review.md` 2절 F14·11절, `initialization-repairs-20260925.md` F14·「비용 측정과 검증 자료」, 커밋 `a299fd8`(`scripts/do_math/repository.py`의 `export`, `git_store.py`)
- 발견 경위: 실제 운전(검토용 export)
- 영향 등급: 저하
- 증상: 인계 snapshot 1,043파일 export가 파일마다 `git cat-file blob` 자식 프로세스를 만들었다.
- 근본 원인: `ResearchRepository.export`(`fa49372` 기준 334행)가 파일마다 `read_bytes`를 호출했다. 이미 있던 배치 읽기 `read_many`를 쓰지 않았다.
- 수정: `a299fd8`이 최대 64파일·8MiB 묶음 읽기로 바꿨다. 수정 뒤 같은 export가 17번의 묶음 읽기와 총 19번의 Git 호출로 끝났다. 회귀 시험은 `test_repository.test_export_reads_bounded_batches_and_preserves_binary_contents`다.
- 결함 유형: 알고리즘
- 트리거: 장시간 누적(기록 수)
- 결함 위치 층: 경계 어댑터(Git 자식 프로세스)
- 시험 유출 원인: 시간·규모 미재현(Git 호출 수를 단언하는 시험 없음)
- 검증런 유출: VR1~VR6이 범위 안에서 놓쳤다. VR5 R1-102·R1-103 등 같은 저장소 읽기 비용 지적은 다른 함수였다.
- 가장 싼 포착 시험: 파일 200개 snapshot을 export하면서 Git 자식 프로세스 생성을 계수한다. 단언은 호출 수가 ⌈200/64⌉+상수 이하이고 바이트가 같다는 것이다.
- 범주 후보: 저장소 읽기의 파일별 프로세스 호출

### B-28 참조가 끊겼다가 다시 나타난 큰 원문을 불변 artifact 재기입으로 오인해 저장을 거부함

- 출처: `C:\math\docs\do-math\similar-defects-2026-09-25\README.md` D1, `C:\math\docs\do-math\boundary-repairs-2026-09-25\README.md` D1, `C:\math\기억\layer1\M-0343.md`, 커밋 `c4d7838`(`scripts/do_math/repository.py`의 `save_with_state`)
- 발견 경위: 정적 검토(유형 확장 감사와 재현)
- 영향 등급: 정지(재현 확인, 운전 미발현). 같은 레코드가 A 값을 다시 쓰는 한 저장이 매번 거부돼 상태가 전진하지 못한다. 감사는 이 항목을 진행 차단 때문에 먼저 고칠 P1로 분류했다.
- 증상: 운전 미발현. 재현 절차는 큰 문자열 A 저장 → 작은 문자열 B로 교체 → A로 복귀이며, 마지막 저장이 `existing runtime artifact bundles are immutable`로 거부됐다.
- 근본 원인: `repository.py` 94~108행은 현재 레코드가 참조하는 payload만 `old_files`에 넣었다. 188행은 그 목록에 없는 예전 payload를 신규 파일로 게시하려 했고, Git에 이미 남아 있는 같은 불변 artifact를 `git_store.py` 378행이 재기입으로 거부했다. 같은 내용의 재사용을 변경 시도로 오인한 것이다. 이 코드는 B-04의 수정 `ff9b2b9`(payload 도입)이 들여왔다.
- 수정: `c4d7838`가 현재 레코드에서 사라진 payload도 고정 Git 부모의 기존 바이트와 대조해 재사용하게 했다. 다른 바이트로의 교체는 계속 거절한다. 회귀 시험은 `test_boundary_repairs.test_unreferenced_payload_can_be_reused_without_rewriting_the_blob`이다.
- 결함 유형: 알고리즘
- 트리거: 특정 전이 순서(A→B→A)
- 결함 위치 층: L2 인터페이스 요소(저장소 게시)
- 시험 유출 원인: 조합·순서 미탐색, 합성 입력이 실제와 다름. `c4d7838^`의 `test_initialization_efficiency.PayloadStorageTests.test_large_payload_storage_and_cached_parent_remain_exact`는 같은 텍스트를 두 필드에 넣어 payload 하나로 한 번 저장·재저장했을 뿐이다. 값이 바뀌었다가 돌아오는 순서는 시험되지 않았다.
- 검증런 유출: 해당 없음. 결함은 `ff9b2b9`(09-25 09:06)에서 들어와 `c4d7838`(같은 날 14:56)에서 고쳐졌고, 그 사이에 이 기간의 검증런이 없었다. 도입 뒤 첫 검증런인 VR6(`d4d273a`, 18:13)은 이미 고쳐진 코드를 봤다.
- 가장 싼 포착 시험: 임시 Git 저장소에서 A→B→A 세 번 저장하고 `load()`한다. 단언은 마지막 저장이 성공하고 A 바이트가 그대로 읽힌다는 것이다. 모델 불필요, 1초 안쪽이다.
- 범주 후보: 내용 주소 저장의 재등장 처리 누락

### B-29 공개 제어 입력의 중첩 형식 오류가 반려되지 않고 같은 처리 실패를 반복함

- 출처: `similar-defects-2026-09-25\README.md` D7, `similar-defects-2026-09-25\coverage.md` 「D7: 공개 제어 입구 14개를 모두 대조」, `boundary-repairs-2026-09-25\README.md` D7·「구현을 구체화하며 바꾼 판단」, `C:\math\기억\layer1\M-0343.md` 「수리 과정에서 달라진 판단」 셋째 문단, 커밋 `c4d7838`(`scripts/do_math/control_contracts.py` 신규, `engine.py`, `trust_validation.py`, `governance.py`)
- 발견 경위: 정적 검토(유형 확장 감사와 재현)
- 영향 등급: 정지(재현 확인, 운전 미발현). 요청이 processed로 기록되지 않고, 새 실행기를 만들어도 같은 요청에서 다시 실패한다. 재현은 공개 API와 실제 CLI `decision --file`로 도달했다.
- 증상: 운전 미발현. 재현 결과는 다음과 같다.
  - `control(..., action='trust')`에 `manifest.foundation_profile=[]` 또는 `manifest.validation=[]`를 주면 접수는 성공하지만 `process_controls()`가 `AttributeError`로 끝난다. 재시작 뒤에도 두 번 같은 실패가 났다.
  - CLI `decision --file`에서 헌장 `record.content=[]`, grant `expires_at=1`을 주면 CLI는 exit 1로 끝나고, 뒤 처리가 두 번 실패하며 영수증이 없다.
  - Python API로 8개 action에 `config=[1]`을 주거나 `decision.change=[]`, `request.review_replacement.action=[]`를 주어도 같은 반복 실패가 났다.
- 근본 원인: 공개 입력의 구조를 확인하기 전에 `.get`·`.items`·`.replace` 같은 타입 의존 연산을 수행했다(`trust_validation.py` 33·47행, `governance.py` 306·337행). 그런데 반려 경계(`engine.py` 910행)는 `ValueError`·`KeyError`·`TypeError`만 처리했다. 그래서 형식 오류가 정상 반려를 벗어나 지속적인 처리 장애가 됐다.
- 수정: `c4d7838`가 접수와 수신에 같은 순수 구조 검사(`control_contracts.py`)를 두었다. 도메인 검사를 값 사용 전으로 옮기고, 시간 입력과 신뢰 manifest의 중첩 구조를 확인한다. `AttributeError`를 넓게 잡는 안은 채택하지 않았다. 회귀 시험은 `test_control_shapes.py`의 12개다. 대표는 `test_all_public_actions_reject_nonobject_config_without_creating_inbox`, `test_nested_shapes_are_rejected_before_publication`, `test_receiver_rejects_bad_payload_once_then_processes_following_valid_control`, `test_trust_manifest_nested_structures_return_errors_without_host_io`, `test_time_boundaries_reject_nonstrings_instead_of_treating_falsy_input_as_now`다.
- 결함 유형: 검사(누락)
- 트리거: 사용자·운영 제어(잘못된 모양의 공개 입력)
- 결함 위치 층: L2 인터페이스 요소(제어 요청 해석)
- 시험 유출 원인: 시험 없음. `c4d7838^`의 시험 트리에 비객체 `config`나 빈 목록 중첩 필드를 넣는 시험이 0건이다(`git grep`).
- 검증런 유출: 같은 계열인 VR3 R1-07("제어 요청의 비문자열 필드가 거부 응답 대신 실행기 예외를 만든다")이 `9a3d345`에서 한 필드만 고쳤다. 공통 입력 경계는 VR1~VR5 범위 안에서 놓쳤다.
- 가장 싼 포착 시험: 공개 action 14종 × {비객체 config, 각 중첩 필드에 잘못된 타입} 표 기반 시험이다. 각 요청을 `control`로 넣고 `process_controls`를 두 번 부른다. 단언은 첫 호출에서 구조화된 반려 영수증이 생기고, 둘째 호출에서 같은 요청이 다시 처리되지 않으며, 뒤의 정상 요청이 처리된다는 것이다. 모양 생성은 속성 기반 시험으로 넓힐 수 있다.
- 범주 후보: 입력 형식 오류의 반려 경계 이탈

### B-30 여러 큰 값을 가진 레코드의 payload 참조 순서가 정렬된 저장 키와 달라 재읽기 정본 검사가 기록을 거부함

- 출처: `C:\math\docs\do-math\connection-audit-2026-09-25.md` F6·「최종 검사」, `C:\math\기억\layer1\M-0344.md` 「맥락과 판단」 둘째 문단, 커밋 `735d464`(`scripts/do_math/payloads.py`의 `encode`)
- 발견 경위: 시험 실행(정적 연결 감사 마지막 단계의 통합 시험 `test_academic_engine.test_explicit_requirement_blocks_runtime_completion_until_independent_assessment`가 실패)
- 영향 등급: 정지(시험에서 발현, 운전 미발현). 한 레코드에 큰 값이 둘 이상이면 저장은 되지만 재읽기가 거부돼 다음 적재부터 진행하지 못한다. 노드는 이 두 이음새(B-30·B-31)가 "실제 연구 흐름을 막는 결함"으로 드러났다고 적는다.
- 증상: 운전 미발현. 학술 후속 통합 사례가 실제 Git 상태를 거치다 저장 코덱에서 실패했다.
- 근본 원인: `payloads.encode`의 `visit`가 dict를 `value.items()`의 삽입 순서로 방문하며 payload 참조 목록을 만들었다. 저장 JSON은 키를 정렬해 직렬화했으므로, 재읽기의 정본 인코딩 검사가 같은 논리 값을 다른 참조 순서로 재구성해 거부했다. 이 코드는 `ff9b2b9`(B-04 수정)이 들여왔다(`git log -S`).
- 수정: `735d464`가 방문 순서를 `sorted(value)`로 고정했다. 회귀 시험은 `test_boundary_repairs.test_multiple_payload_references_follow_canonical_key_order`다.
- 결함 유형: 스키마·계약 불일치(인코더와 정본 검사기의 순서 계약)
- 트리거: 기타(한 레코드에 임계 크기를 넘는 값이 둘 이상이고 삽입 순서가 정렬 순서와 다를 때)
- 결함 위치 층: L1 원시(직렬화)
- 시험 유출 원인: 합성 입력이 실제와 다름, 그리고 서식 값에 없는 사유(있는 시험을 돌리지 않음). 도입 시점의 단위 시험 `test_large_payload_storage_and_cached_parent_remain_exact`는 같은 텍스트를 두 필드에 넣어 payload가 하나뿐이었으므로 순서 문제가 생길 수 없었다. 결함을 잡은 통합 시험은 `ff9b2b9` 이전부터 있었지만, `ff9b2b9`·`c44dd7b`·`c4d7838`의 검증 집계(`validation-summary.json` 세 개)에 그 시험 이름이 0회 나온다. 선택 실행에서 빠진 것이다.
- 검증런 유출: 도입(09:06) 뒤 수정(16:37)까지 사이에 이 기간 검증런이 없었다. 해당 없음.
- 가장 싼 포착 시험: 서로 다른 큰 값 두 개를 삽입 순서가 역정렬인 키(`{'z': big1, 'a': big2}`)로 가진 레코드를 `encode` → 정본 직렬화 → `decode`·정본 검사한다. 단언은 왕복이 성공하는 것이다. 더 일반적으로는 임의 dict에 대한 `decode(encode(x)) == x` 속성 시험이다.
- 범주 후보: 직렬화 왕복 불변식 위반

### B-31 단계 제한 실행이 완료된 환경 관측을 회수한 뒤 봉인 제출의 재적용 없이 끝나 다음 실행이 같은 대기를 반복함

- 출처: `connection-audit-2026-09-25.md` F7, `C:\math\기억\layer1\M-0344.md` 「맥락과 판단」 둘째 문단·「작업 너머」, 커밋 `735d464`(`scripts/do_math/scheduler.py`의 실행 루프)
- 발견 경위: 시험 실행(B-30과 같은 통합 시험이 두 결함을 순서대로 드러냄)
- 영향 등급: 정지(코드 경로 추론, 운전 미발현). 문서는 "다음 실행이 관측을 다시 열면 대기 상태가 반복될 수 있었다"고 적는다. 초기화 운전이 `run --max-steps`를 쓰므로 정상 운전 경로로 도달한다.
- 증상: 운전 미발현. `run(max_steps=1)`에서 환경 관측 작업의 완료를 회수한 직후 루프가 종료돼, 봉인된 제출의 재적용이 남았다.
- 근본 원인: `scheduler` 실행 루프는 `draining`(단계 상한 도달)이고 진행 중 future가 없으면 즉시 break했다. 방금 `collect()`가 완료를 회수해 봉인 제출의 게시 정산이 가능해진 경우를 구별하지 않았다. 지연 게시(`ff9b2b9`)와 함께 생긴 이음새다.
- 수정: `735d464`가 이번 반복에서 완료된 호출을 회수했으면 제어·게시 정산을 한 번 더 거친 뒤 종료하게 했다(`collected` 플래그). 새 단위 회귀 시험은 없고, 기존 통합 사례가 끝까지 통과하는 것으로 재검증했다(733초).
- 결함 유형: 타이밍·직렬화
- 트리거: 사용자·운영 제어(단계 제한 실행), 특정 전이 순서(완료 회수와 루프 종료 조건의 겹침)
- 결함 위치 층: L3 배선(엔진 실행 루프)
- 시험 유출 원인: 조합·순서 미탐색. `c4d7838^`의 `test_sealed_response_survives_deferred_domain_observation_and_git_publication`은 `_apply_submission_bundles`를 직접 세 번 부르고 `calls.collect()`를 손으로 돌렸다. 실행 루프 `run(max_steps=n)`의 종료 조건을 거치지 않았다. 결함을 잡은 통합 시험은 B-30과 같은 이유로 선택 실행에서 빠져 있었다.
- 검증런 유출: 해당 없음(도입 뒤 수정까지 이 기간 검증런이 없음)
- 가장 싼 포착 시험: 환경 관측 대역이 즉시 완료되는 봉인 제출을 하나 둔 엔진으로 `run(max_steps=1)`을 한 번 호출한다. 단언은 반환 직후 그 제출이 accepted로 게시돼 있다는 것이다. 즉 "단계 제한 실행이 반환될 때 회수했지만 적용하지 않은 완료가 없다"는 불변식이다.
- 범주 후보: 비동기 완료 뒤 정산 의무의 누락

B-32~B-49는 검증런 장부 일곱 개에서 정지로 판정한 결함이다. 판정·diff 대조·당시 시험 판본 확인은 세 조사 에이전트가 장부별로 나눠 수행했다. 그중 다섯 건(B-35, B-38, B-43, B-46, B-49)은 수정 diff를 직접 다시 대조해 주장과 일치함을 확인했다. 모든 항목은 운전에서 발현되지 않았고, 영향 등급은 코드 경로 추론이다.

### B-32 역할 입력 용량 계산이 선택 표시 항목을 다시 필수로 묶어 입력 초과 대기에 빠짐

- 출처: `C:\math\임시\do-math_검증_2026-09-24\장부.md` R1-04(67행), 같은 폴더 `종료보고.md` 41행("선택 자료를 다시 필수 입력으로 세어 실행을 멈추던 경로"), 커밋 `bc56bc3`(`scripts/do_math/context_store.py`)
- 발견 경위: 검증런(VR1 1라운드)
- 영향 등급: 정지(코드 경로 추론, 운전 미발현). overflow가 나면 활동이 `user_decision` 대기(research_work이면 research_plan 대기)로 가므로 사람의 결정이 필요하다.
- 증상: 운전 미발현
- 근본 원인: `context_store.prepare_role_input`(부모 판본 555~556행)은 goal·policies·implementation_documents를 governance의 레거시 표시 사본으로 보고 필수 목록에서 뺐다. 그런데 `fit_context`(810행)가 `role_direct_keys(role, context)`로 이 세 키를 다시 필수에 넣었다. 부푼 필수 바이트가 한도를 넘으면 축소 루프가 즉시 멈추고 `mandatory_context_exceeds_limit` overflow를 낸다. 세 키는 모두 source catalog 항목이어서 참조로 줄일 수 있었다.
- 수정: `bc56bc3`이 `fit_context`의 `role_direct_keys`에서 세 키를 제외했다. 회귀 시험은 추가되지 않았다.
- 결함 유형: 인터페이스(호출자가 확정한 필수 목록을 피호출자가 다시 넓힘)
- 트리거: 장시간 누적(입력 크기가 한도 − 레거시 사본 크기 ~ 한도 구간에 들 때)
- 결함 위치 층: L2 인터페이스 요소(역할 입력 구성)
- 시험 유출 원인: 합성 입력이 실제와 다름, 시험 없음. 부모 판본의 `fit_context` 시험(`test_context_store.py:109,147,152`, `test_redesign_SURFACE.py:399,457`, `test_submission_boundaries.py:393,408,435`)은 모두 `mandatory_keys=['goal', ...]`로 goal을 스스로 필수에 넣었다. `test_context_store.py:152`는 goal이 통째로 남고 overflow가 나는 것을 정상으로 단언했다. `prepare_role_input`을 거쳐 레거시 사본이 커지는 경로는 실행되지 않았다.
- 검증런 유출: 해당 없음. 결함 코드는 `7d2597e`에서 들어왔고, 이 기간 첫 검증런인 VR1이 제기했다.
- 가장 싼 포착 시험: `fit_context({'governance': {...}, 'action': {'id': 'A'}, 'goal': 'g'*800, 'policies': 'p'*800}, max_bytes=1200, mandatory_keys=['governance','action'], role='research_plan')`을 호출한다. 단언은 `overflow is None`이고 축소 목록에 goal·policies가 있다는 것이다.
- 범주 후보: 필수 입력 분류의 이중 정의 불일치

### B-33 과제 기반 보충 조사에 연구 수행용 자기 점검 규칙을 넘겨 실행 준비가 예외로 끝남

- 출처: `C:\math\임시\do-math_검증_2026-09-24_astra8\장부.md` R1-01(57행)과 신호 처리 절, `C:\math\기억\layer1\M-0336.md` 「터득한 것」 둘째 문단, 커밋 `967218e`(`scripts/do_math/engine.py`, `scripts/tests/test_redesign_ENGINE.py`)
- 발견 경위: 검증런(VR2). 심사는 1/3이었고, 사용자 후속 지시로 운전자가 직접 수리했다.
- 영향 등급: 정지(코드 경로 추론, 운전 미발현). 해당 행동은 모델 호출 전에 매번 거절된다. 준비 예외가 재시도로 가는지 실행기 종료로 가는지는 확정하지 않았다.
- 증상: 운전 미발현
- 근본 원인: `engine._call_steps`(부모 판본 3100~3103행)는 `role in {"research_work","supplemental_research"}`이면 과제의 `initial_observation_rules`를 가져왔다. 그러나 `$execution` 결속은 research_work에만 했다(3114~3116행). 보충 조사 프로필의 `rule_bindings`는 빈 목록이므로, 3336행의 `ObservationTracker` 생성에서 `validate_execution_rules`가 ValueError를 던졌다. 이 생성은 ValueError를 관찰 대기로 바꾸는 try 블록(3111~3130행) 밖에 있었다.
- 수정: `967218e`가 규칙 선택 조건을 `role == "research_work"`로 좁혔다. 회귀 시험은 `test_redesign_ENGINE.TaskObservationRoleTests.test_task_rules_follow_the_selected_roles_observation_contract`다. M-0336에 따르면 처음 제출된 시험 조각은 엔진 모사체에 `head`를 채우지 않아 실패했고, 운전자가 시험을 다시 썼다.
- 결함 유형: 기능(역할 조건 분기의 과잉 포함)
- 트리거: 특정 전이 순서(`initial_observation_rules`를 가진 과제에 review_cycle 없는 supplemental_research가 배정됨)
- 결함 위치 층: L3 배선(`_call_steps` 안의 역할별 관찰 입력 구성)
- 시험 유출 원인: 조합·순서 미탐색. 부모 판본의 `initial_observation_rules` 시험(`test_six_connections.py:468`, `test_walkthrough_repairs.py:27,36`, `test_model_assessment_flow.py:127`)은 research_work만 실행했다. supplemental_research 시험은 규칙이 비어 있는 review_cycle 경로였다.
- 검증런 유출: 결함 코드는 `7d2597e`에서 들어왔다. VR1이 범위 안에서 놓쳤다.
- 가장 싼 포착 시험: `build_profiles(DEFAULT_CONFIG)`의 각 작업 역할 프로필과 `$execution` 주체 규칙을 가진 과제를 조합한다. 엔진과 같은 선택식으로 `tracker_config` → `ObservationTracker('EX-1', tmp, config)`를 호출하고, 예외가 없으며 research_work가 아니면 규칙이 비어 있음을 단언한다.
- 범주 후보: 역할 분기 조건의 과잉 포함

### B-34 관계 주장 지식의 끝점 근거를 생산자는 목록으로, 저장 스키마는 객체로 다뤄 저장이 거부됨

- 출처: `C:\math\임시\do-math_검증_2026-09-24_astra8\장부.md` R1-04(60행)·R1-32(88행, 묶음 R1-M2), 커밋 `967218e`(`scripts/do_math/record_schemas/schemas.py`)
- 발견 경위: 검증런(VR2, 수리자 두 기가 독립 제기)
- 영향 등급: 정지(코드 경로 추론, 운전 미발현)
- 증상: 운전 미발현
- 근본 원인: `record_schemas/schemas.py`(부모 판본 51행)는 `"relation_endpoint_basis": EVIDENCE`였고 `EVIDENCE = {"type": "object"}`였다. 그런데 생산자 `knowledge_io.import_candidate`(306행)는 `knowledge.capture_basis(...)`의 `list[dict]`를 저장했다. 그래서 relation_claim을 가진 지식 후보가 편입되면 저장 검사가 후보 게시 전체를 거부했다.
- 수정: `967218e`가 스키마를 `array(obj({"id","sha256","status"}))`로 바꿨다. 회귀 시험은 `test_knowledge_io.KnowledgeIoTests.test_relation_claim_endpoint_basis_matches_the_storage_contract`와 `test_redesign_STORAGE.StorageRedesignTests.test_relation_claim_endpoint_basis_survives_storage_and_remains_typed`다.
- 결함 유형: 스키마·계약 불일치
- 트리거: 실제 모델 출력 형태(연구 수행이 `knowledge_metadata.relation_claim`을 가진 새 지식을 제출)
- 결함 위치 층: 계약·스키마(저장 스키마 선언)
- 시험 유출 원인: 대역이 가림, 시험 없음. `test_redesign_EVIDENCE_walkthroughs.py:178`의 관계 흐름은 저장소를 `InputSnapshot` 대역으로 바꾼 `engine_fixture`를 썼다(`test_redesign_EVIDENCE.py` 49~86행). `test_redesign_KNOWLEDGE`와 `test_knowledge_io.py:103`은 메모리 상태만 다뤘다. relation_claim 지식을 저장 계약으로 검사한 시험은 없었다.
- 검증런 유출: 스키마 행은 `7d2597e`에서 들어왔다. VR1이 범위 안에서 놓쳤다.
- 가장 싼 포착 시험: `import_candidate`로 끝점 둘과 relation_claim 지식을 만든 뒤 `jsonschema.validate(record, 저장 계약의 knowledge 스키마)`를 단언한다. 일반형은 "knowledge_io의 모든 생산물은 저장 스키마를 통과한다"는 속성 시험이다.
- 범주 후보: 생산자·저장 스키마 모양 불일치

### B-35 Claude 모델 잠금 표지가 고정 프로필을 거쳐 Codex 작업자 요청에 들어가 Codex 실행이 기동 전에 거부됨

- 출처: `C:\math\임시\do-math_검증_2026-09-24_astra8\장부.md` R1-07(63행), 커밋 `967218e`(`scripts/do_math/model_runner.py`)
- 발견 경위: 검증런(VR2)
- 영향 등급: 정지(코드 경로 추론, 운전 미발현). 설정을 켜면 Codex에 배정된 모든 역할 실행이 실패한다.
- 증상: 운전 미발현
- 근본 원인: `ModelRunner.run`(부모 판본 274행)은 Codex 경로에서 `claude_only_assigned_model` 인자를 뺐다. 그러나 `CodexModelRunner.run`의 고정 프로필 분기(67행)가 프로필에 복사된 값을 다시 읽어 요청에 `claude_only_assigned_model: true`를 넣었다(105~106행). 수신자 `codex_worker.load_request`(103~105행)는 모르는 필드를 `unknown worker request fields`로 거부했다.
- 수정: `967218e`가 조건을 `if claude_only_assigned_model and "claude_path" in request`로 바꿨다(diff 직접 확인). 회귀 시험은 `test_claude_adapter.ClaudeTests.test_claude_lock_in_pinned_profile_keeps_codex_request_valid`다.
- 결함 유형: 스키마·계약 불일치(요청 생산자와 작업자 수신 스키마)
- 트리거: 설정·환경(`claude_only_assigned_model=true`이고 어느 역할에든 Codex 모델이 배정됨)
- 결함 위치 층: 경계 어댑터(Codex 작업자 요청 구성)
- 시험 유출 원인: 대역이 가림. 부모 판본 `test_claude_adapter.test_model_lock_is_opt_in_and_reaches_only_claude`(31~52행)가 `runner.codex = Mock()`으로 Codex 러너 전체를 대역으로 바꿔, 고정 프로필 분기와 `load_request`가 한 번도 실행되지 않았다.
- 검증런 유출: 결함 코드는 `7d2597e`에서 들어왔다. VR1이 범위 안에서 놓쳤다. VR1 2라운드는 같은 파일의 다른 함수를 수리했다.
- 가장 싼 포착 시험: 가짜 어댑터를 붙인 `CodexModelRunner`로, `claude_only_assigned_model: True` 설정의 Codex 역할 프로필 실행을 한 번 호출한다. 단언은 `codex_worker.load_request(evidence/request.json)`가 예외 없이 끝난다는 것이다.
- 범주 후보: 요청 생산자·작업자 수신 스키마 불일치

### B-36 일시 정지 중 승인된 제한 복구가 실제 AI 호출 경로의 일괄 정지 거부에 막혀 실행되지 않음

- 출처: `C:\math\임시\do-math_검증_2026-09-24_astra8\장부.md` R1-35(91행), 커밋 `967218e`(`scripts/do_math/engine.py`)
- 발견 경위: 검증런(VR2)
- 영향 등급: 정지(코드 경로 추론, 운전 미발현). 사람이 승인한 복구 경로가 작동하지 않아 재개나 코드 수정이라는 추가 개입이 필요하다.
- 증상: 운전 미발현
- 근본 원인: `lifecycle_engine._execution_stop_requested`·`_limited_recovery_allowed`(부모 판본 485~503행)는 정지 중에도 승인된 maintenance·trust 복구를 허용하도록 만들어져 있었다. 그러나 `engine._call_steps`(3204행)는 `runtime["status"]`가 paused·closed·completed이면 입력을 폐기하고 `return False`했다. 관찰 루프 정지 판정(3407행), 종료 결과 처리(3478행), native final 수용(2898·2948행)도 같은 일괄 거부를 썼다. `b134089`(09-18)의 일괄 거부 위에 `7d2597e`이 제한 복구를 추가하면서 AI 호출 경로를 고치지 않은 결합 결함이다.
- 수정: `967218e`가 해당 판정을 모두 `_execution_stop_requested(action, execution)`로 바꾸고, 정지 중에는 status를 running으로 덮지 않게 했다. 회귀 시험은 `test_research_recovery.LimitedRecoveryCallTests.test_actual_ai_call_keeps_pause_and_honors_a_new_stop`다.
- 결함 유형: 검사(정지 게이트의 과잉 거부)
- 트리거: 사용자·운영 제어(pause 뒤 limited_recovery 결정 승인)
- 결함 위치 층: L3 배선(실행 준비·관찰 루프)
- 시험 유출 원인: 대역이 가림. 부모 판본 `test_lifecycle_engine.test_scheduler_scopes_maintenance_dispatch_with_executor_double`(709~737행)이 `e._call_steps`를 대역으로 바꿨다. `test_scheduler_runs_only_approved_machine_recovery_and_stays_paused`는 기계 역할 경로만 실행했다.
- 검증런 유출: 결합 결함은 `7d2597e`에서 성립했다. VR1이 범위 안에서 놓쳤다.
- 가장 싼 포착 시험: 실제 `_call_steps`를 쓰고 러너만 어댑터 층에서 대역으로 둔 엔진에서 maintenance 행동을 큐에 넣는다. pause와 limited_recovery 결정 뒤 `run(max_steps=1)`을 실행한다. 단언은 러너 호출 1회와 lifecycle 상태 `paused` 유지다.
- 범주 후보: 일괄 정지 게이트와 예외 허가의 불일치

### B-37 반려되거나 전제가 바뀐 후보 준비를 무산출 준비로 세어 사용자 반복 보류를 조기에 엶

- 출처: `C:\math\임시\do-math_검증_2026-09-24_astra8\장부.md` R1-37(93행), 커밋 `967218e`(`scripts/do_math/revisions.py`)
- 발견 경위: 검증런(VR2)
- 영향 등급: 정지(코드 경로 추론, 운전 미발현). 선택 설정 `exhaustion_empty_limit`을 채택했을 때만 해당하며, 보류가 열리면 준비 계보가 사용자 결정을 기다린다. 기본 설정에서는 거부마다 불필요한 research_plan 후속이 쌓이는 저하다.
- 증상: 운전 미발현
- 근본 원인: `revisions.record_execution_outcome`(부모 판본 369~383행)은 research_preparation 결과를 `accepted`와 무관하게 `exhaustion_empty` 계보의 `empty`로 기록했다. 호출자는 거부 수신(`revision_engine._record_task_receipt`)과 전제 변경(`decision_engine._refresh_changed_decision`의 `accepted=False`)이다. `record_repetition`(229~237행)은 한도에 이르면 `repetition_hold`와 `owner='user'` 질문을 열었다.
- 수정: `967218e`가 `if preserved or accepted:`일 때만 세게 했다. 회귀 시험은 `test_redesign_TASKS.py`의 `test_rejected_preparation_does_not_count_as_an_empty_research_result`와 `test_partially_accepted_contract_still_records_its_real_production`이다.
- 결함 유형: 알고리즘(반복 계수의 결과 분류 오류)
- 트리거: 설정·환경(`exhaustion_empty_limit` 채택), 실제 모델 출력 형태(반려되는 준비 응답), 특정 전이 순서(준비 중 전제 변경)
- 결함 위치 층: L2 인터페이스 요소(반복 한도 규칙)
- 시험 유출 원인: 조합·순서 미탐색. `accepted=False` 시험은 research_plan만 다뤘다(`test_walkthrough_followup.test_receiver_failure_categories_count_once_and_success_ends_streak`, `test_redesign_TASKS.py:550`). exhaustion_empty 시험은 `accepted=True`의 무산출만 다뤘다.
- 검증런 유출: 결함 코드는 `7d2597e`에서 들어왔다. VR1이 범위 안에서 놓쳤다.
- 가장 싼 포착 시험: `config={'exhaustion_empty_limit': 1}`, execution `{'role':'research_preparation','error_kind':'output_schema'}`로 `record_execution_outcome(..., accepted=False)`를 호출한다. 단언은 `outcome='empty'` 이력이 없고 `repetition_hold`가 None이라는 것이다.
- 범주 후보: 반복 계수의 결과 분류 오류

### B-38 선택이 취소된 과제의 계약 검토 대기가 새 검토 승인 뒤에도 남아 과제가 다시 준비되지 않음

- 출처: `C:\math\임시\do-math_검증_2026-09-24_astra8_신규\장부.md` R1-01(61행), 커밋 `9a3d345`(`scripts/do_math/engine.py`, `scripts/tests/test_revision_obligations.py`)
- 발견 경위: 검증런(VR3)
- 영향 등급: 정지(코드 경로 추론, 운전 미발현, 과제 단위 영구 대기). 다른 과제는 진행할 수 있다(관찰 절의 판정 일관성 참조).
- 증상: 운전 미발현
- 근본 원인: `revision_engine._selected_action_current`(부모 판본 78~81행)는 선택된 계약이 바뀌면 `task['waiting']={'kind':'contract_review',...}`를 기록했다. 그런데 `engine._apply`의 task_contract_review 분기(3955~3957행)는 승인 시 status만 `planned`로 바꾸고 `waiting`을 지우지 않았다. `planning.task_ready`(603~607행)는 `waiting`이 있으면 not_ready를 반환했다.
- 수정: `9a3d345`가 승인이고 `waiting.kind`가 contract_review이면 `task.pop("waiting")`하게 했다(diff 직접 확인). 새 시험 함수는 없고, 기존 `test_revision_obligations.RevisionObligationTests.test_plan_selection_and_predispatch_use_actual_current_input`에 재검토 승인 뒤 대기 제거와 ready 단언을 더했다.
- 결함 유형: 대입·초기화(대기 필드 미해제)
- 트리거: 특정 전이 순서(선택 → 발송 전 계약 개정 → 선택 무효 → 새 계약 검토 승인)
- 결함 위치 층: L2 인터페이스 요소(상태 전이 규칙)
- 시험 유출 원인: 조합·순서 미탐색. 부모 판본의 같은 시험(108~117행)은 research_plan이 큐에 들어간 데서 끝나고, 재검토 승인 전이를 실행하지 않았다.
- 검증런 유출: 두 코드 모두 `7d2597e`에서 들어왔다. VR1·VR2가 범위 안에서 놓쳤다.
- 가장 싼 포착 시험: `waiting={'kind':'contract_review'}`와 status `waiting`을 가진 과제에 승인 contract_review 출력을 `_apply`로 적용한다. 단언은 `'waiting' not in task`이고 `task_ready(...)['state']=='ready'`라는 것이다.
- 범주 후보: 대기 해소 조건 누락

### B-39 학술 요구를 모두 제거하면 옛 학술 과제와 대기열이 남아 인스턴스가 완료되지 않음

- 출처: `C:\math\임시\do-math_검증_2026-09-24_astra8_신규\장부.md` R1-05(65행), `C:\math\기억\layer1\M-0337.md` 「터득한 것」 셋째 문단, 커밋 `9a3d345`(`scripts/do_math/academic_engine.py`, `scripts/tests/test_academic_engine.py`)
- 발견 경위: 검증런(VR3). 적용 뒤 선택 통합 시험 하나가 실패했다. 원인은 새 완료 분기와 시험의 합성 전제(목표 미해결인데 해결 근거를 모사)가 모순된 것이었고, 시험의 `goal_status`를 고쳤다.
- 영향 등급: 정지(코드 경로 추론, 운전 미발현, 완료 불능)
- 증상: 운전 미발현
- 근본 원인: `academic_engine._ensure_academic_followup`(부모 판본 64~69행)은 `requirements.items`가 비면 곧바로 반환해, 옛 요구의 미완료 과제를 닫지 않고 대기열도 비우지 않았다. 124행은 `academic_status == "completed"`만 완료로 봐서 요구가 없을 때의 `not_applicable`은 영원히 완료되지 않았다. 목표가 이미 해결됐으면 재고 사건도 멈춰 인스턴스가 미완료로 남는다.
- 수정: `9a3d345`가 조기 반환을 없애고 완료 조건을 `{"completed","not_applicable"}`로 넓혔다. 회귀 시험은 `test_academic_engine.AcademicEngineTests.test_removing_all_requirements_retires_old_tasks_and_completes_followup`과 `test_removing_all_requirements_preserves_unresolved_external_rejection`이다.
- 결함 유형: 기능(빈 집합 경계의 완료 전이 누락)
- 트리거: 사용자·운영 제어(학술 요구를 빈 목록으로 바꾸는 헌장 결정), 특정 전이 순서(해결된 목표와 열린 학술 과제)
- 결함 위치 층: L2 인터페이스 요소(상태 전이 규칙)
- 시험 유출 원인: 조합·순서 미탐색. 부모 판본의 요구 변경 시험(143·163행)은 요구가 하나 이상 남았고, 빈 요구 분기는 처음부터 요구가 없는 시험(197행 이하)에서만 실행됐다.
- 검증런 유출: 조기 반환은 `3d7b280`(09-14)에서 들어왔다. VR1·VR2가 범위 안에서 놓쳤다. VR1 R2-04는 같은 파일의 `_solution_basis`를 재구성하기까지 했다.
- 가장 싼 포착 시험: 목표 해결 상태와 학술 요구 1개, 열린 학술 과제 1개를 가진 fixture에 `academic_requirements=[]` 결정을 보내고 `_ensure_academic_followup()`을 호출한다. 단언은 runtime.status `completed`, 옛 과제 `closed`, 빈 대기열이다.
- 범주 후보: 빈 집합 경계의 완료 전이 누락

### B-40 하나의 형식 결과를 공유하는 두 해설의 신뢰 환경 전환이 저장 의미 검사에서 거부됨

- 출처: `C:\math\임시\do-math_검증_2026-09-24_astra8_신규\장부.md` R1-06(66행)·R1-22(82행, 묶음 R1-M1), 커밋 `9a3d345`(`scripts/do_math/knowledge.py`, `record_schemas/__init__.py`, `record_schemas/domains.py`)
- 발견 경위: 검증런(VR3)
- 영향 등급: 정지(코드 경로 추론, 운전 미발현)
- 증상: 운전 미발현
- 근본 원인: `knowledge.begin_transition`(부모 판본 616행)의 targets에 `exposition_id`가 없었다. `validate_semantics`(381행)는 상속 동일성 평가의 전환 target을 `formal_result_id`만으로 찾았다. 그래서 형식 결과를 공유하는 해설이 둘이면 target이 2개가 돼 ValueError가 났고, 전환 활성 뒤의 상태를 저장할 수 없었다. 공유 자체는 `formal_result_ref` 재사용이라는 정상 경로다.
- 수정: `9a3d345`가 targets에 `exposition_id`를 추가하고 의미 검사가 두 키로 target을 찾게 했다. 회귀 시험은 `test_redesign_KNOWLEDGE.KnowledgeAudit2.test_shared_formal_result_continuity_round_trips_for_each_exposition`이다.
- 결함 유형: 스키마·계약 불일치(저장 의미 검사의 식별 키 부족)
- 트리거: 특정 전이 순서(형식 결과 재사용 해설 → 신뢰 환경 전환), 사용자·운영 제어(`trust transition`)
- 결함 위치 층: L1 원시(저장 의미 검사)
- 시험 유출 원인: 조합·순서 미탐색. 형식 결과 재사용(`test_redesign_KNOWLEDGE.py:146`)과 전환(190행)이 따로 시험됐다.
- 검증런 유출: 결함 코드는 `7d2597e`에서 들어왔다. VR1·VR2가 범위 안에서 놓쳤다.
- 가장 싼 포착 시험: 지식 A와 A의 형식 결과를 재사용한 지식 B를 만들고, `begin_transition` → `record_transition_result` ×2 → `activate_transition` 뒤 `repo.validate_candidate`가 통과함을 단언한다.
- 범주 후보: 저장 의미 검사의 식별 키 부족(다대일 관계)

### B-41 사용자 학술 요구 ID를 과제 저장이 전역 기록 ID 패턴으로 검사해 학술 과제를 저장할 수 없음

- 출처: `C:\math\임시\do-math_검증_2026-09-24_astra8_신규\장부.md` R1-20(80행), 커밋 `9a3d345`(`scripts/do_math/record_schemas/schemas.py`)
- 발견 경위: 검증런(VR3)
- 영향 등급: 정지(코드 경로 추론, 운전 미발현). ASCII 패턴 밖의 요구 ID가 있으면 목표 해결 직후 학술 과제를 포함한 상태 게시가 매번 거부된다.
- 증상: 운전 미발현
- 근본 원인: 저장 스키마(부모 판본 134행)는 `"academic_requirement_id": ID`였고 `ID`는 `^[A-Za-z0-9][A-Za-z0-9_.-]*$`였다. 그런데 생산자 `academic.py`(21~23행)는 비어 있지 않은 임의 문자열을 받았고, `_ensure_academic_followup`(117행)이 그대로 과제에 복사했다.
- 수정: `9a3d345`가 비어 있지 않은 문자열 스키마로 완화했다. 새 시험 함수는 없고, 기존 `test_academic_engine.AcademicTaskPersistenceTests.test_user_requirement_task_keeps_charter_provenance_without_invented_execution`의 요구 ID를 `"원고 검토"`로 바꿨다.
- 결함 유형: 스키마·계약 불일치(값 영역)
- 트리거: 사용자·운영 제어(한글·공백이 든 학술 요구 ID)
- 결함 위치 층: 계약·스키마(저장 스키마 선언)
- 시험 유출 원인: 합성 입력이 실제와 다름. 게시까지 가는 시험이 있었지만 fixture의 요구 ID가 `"writeup"`(28행)이었다.
- 검증런 유출: 결함 코드는 `7d2597e`에서 들어왔다. VR1·VR2가 범위 안에서 놓쳤다. VR2는 같은 파일 51행(B-34)을 고치면서 134행은 제기하지 않았다.
- 가장 싼 포착 시험: 생산자가 받는 값 영역의 표본(`"원고 검토"`, `"a b"`)이 저장 스키마의 해당 속성을 통과함을 단언한다. 즉 "생산자 수용 영역 ⊆ 저장 스키마 영역" 시험이다.
- 범주 후보: 생산자·저장 스키마 모양 불일치

### B-42 누락 원자료를 파일명으로 지목한 과제 평가가 자료 도착 뒤에도 재평가를 열지 않음

- 출처: `C:\math\임시\do-math_검증_2026-09-24_astra8_신규\장부.md` R1-23(83행), 커밋 `9a3d345`(`scripts/do_math/task_scope.py`, `scripts/tests/test_redesign_TASKS.py`)
- 발견 경위: 검증런(VR3)
- 영향 등급: 정지(코드 경로 추론, 운전 미발현, 과제 단위 영구 대기). 주기 재고 같은 다른 경로가 과제를 다시 열 가능성은 끝까지 배제하지 못했다.
- 증상: 운전 미발현
- 근본 원인: `task_scope.assessment_basis`(부모 판본 211~228행)는 평가의 `unresolved[].missing_inputs` 참조를 기록 ID로만 찾았다. 아직 ID가 없는 누락 자료는 평가자가 파일명(`new.txt`)으로 지목할 수밖에 없는데, 그 참조가 도착 전후 모두 `None`으로 해시돼 `assessment_current`가 바뀌지 않았다.
- 수정: `9a3d345`가 ID가 없으면 `input_basis.aliases(source)`로 원자료를 찾게 했다. 회귀 시험은 기존 `test_redesign_TASKS.AssessmentApplicationTests.test_missing_assessment_input_arrival_reopens_assessment_without_new_work`를 `SO-new`·`new.txt`·`source:new.txt`·`sources/new.txt` subTest로 넓힌 것이다.
- 결함 유형: 인터페이스(참조 식별자 형식 불일치)
- 트리거: 실제 모델 출력 형태(평가자가 누락 자료를 파일명으로 지목), 사용자·운영 제어(원자료 추가)
- 결함 위치 층: L2 인터페이스 요소
- 시험 유출 원인: 합성 입력이 실제와 다름. 부모 판본의 같은 시험은 도착할 원자료의 미래 ID `'SO-new'`를 missing_inputs에 미리 넣었다. 실제 평가자는 그 ID를 알 수 없다.
- 검증런 유출: 결함 코드는 `7d2597e`에서 들어왔다. VR1·VR2가 범위 안에서 놓쳤다.
- 가장 싼 포착 시험: `missing_inputs=['new.txt']`인 불완전 평가를 적용한 뒤 `{'id':'SO-new','name':'new.txt','path':'sources/new.txt'}`를 추가한다. 단언은 `refresh_task_assessments(...) == ['TK-1']`이다.
- 범주 후보: 대기 해소 조건의 식별자 형식 불일치

### B-43 객체가 아닌 knowledge_metadata 값이 제출 검사를 AttributeError로 깨뜨리고 제어 수송을 뚫어 실행기를 반복 종료시킴

- 출처: `C:\math\임시\do-math_검증_2026-09-24_astra8_3차\장부.md` R1-04(47행), 커밋 `9c5356d`(`scripts/do_math/integration.py`)
- 발견 경위: 검증런(VR4)
- 영향 등급: 정지(코드 경로 추론, 운전 미발현)
- 증상: 운전 미발현. 추론 경로는 다음과 같다. 모델이 `knowledge_metadata` 원소를 객체가 아닌 값으로 쓰고 제출한다. `seal_submission` → `check_submission` → `payload_issues` → `inspect_bundles`의 `value.get("title")`이 AttributeError를 낸다. `_publish_control_request`는 (ValueError, KeyError, TypeError, OSError)만 잡고, `ControlTransport.receive`·`pump`는 ValueError만 잡는다(`control_transport.py` 171·225행). 예외가 `_controls` 밖으로 빠져 실행기가 종료한다. 요청 파일이 영수증 없이 남아 재시작마다 같은 예외가 난다.
- 근본 원인: `integration.inspect_bundles`(부모 판본 404~405행)가 member 값의 모양을 확인하지 않고 `refs.add(value.get("title"))`를 실행했다. 여기에 제출 검사 경로가 내는 예외 종류와 상위 경계가 잡는 종류가 어긋나 있었다.
- 수정: `9c5356d`가 `isinstance(value, dict) and isinstance(value.get("title"), str)` 가드를 넣었다(diff 직접 확인). 예외 경계(pump·seal의 except 범위)는 바꾸지 않았다. 회귀 시험은 `test_redesign_CONTRACTS.ContractBoundaryTests.test_malformed_metadata_returns_its_bundle_without_losing_independent_output`이다.
- 결함 유형: 검사(입력 모양 검증 누락)
- 트리거: 실제 모델 출력 형태
- 결함 위치 층: L2 인터페이스 요소(제출 검사). 전파는 L3 배선(제어 수송 pump, 실행기 루프)을 거친다.
- 시험 유출 원인: 시험 없음. 부모 판본의 `test_metadata_cannot_split_from_its_new_record`(912~920행)와 `test_redesign_EVIDENCE.py` 244~249행은 dict 값만 썼다. ValueError가 아닌 예외를 제어 pump에 흘리는 시험도 없었다.
- 검증런 유출: 결함 행은 `7d2597e`에서 들어왔다. VR1~VR3이 범위 안에서 놓쳤다.
- 가장 싼 포착 시험: `payload_issues`에 member 좌표 `activity-extensions.json/knowledge_metadata/0`과 값 `None`을 준다. 단언은 예외가 없고 그 좌표의 이슈가 반환된다는 것이다. 계열 전체에는 "모든 확장 가족에 {None, [], 0, "x"}를 넣어도 `payload_issues`가 이슈 목록 외의 예외를 내지 않는다"는 경계 계약 시험을 둔다.
- 범주 후보: 입력 형식 오류의 반려 경계 이탈

### B-44 작업 공간 루트 참조(`.`)가 IndexError로 제출 검사를 뚫고 실행기를 반복 종료시킴

- 출처: `C:\math\임시\do-math_검증_2026-09-24_astra8_3차\장부.md` R1-05(48행), 커밋 `9c5356d`(`scripts/do_math/context_store.py`)
- 발견 경위: 검증런(VR4)
- 영향 등급: 정지(코드 경로 추론, 운전 미발현)
- 증상: 운전 미발현. 모델 출력의 `used_sources` 등에 `"."`·`"./"`·`"workspace:."`가 들어가면, `submission.validate_reference`에서 `Path(".").parts[0]`이 IndexError를 낸다(부모 판본 489행 부근). `_payload_issues`의 `check()`와 상위 경계가 이 예외를 잡지 않아 B-43과 같은 반복 종료로 이어진다.
- 근본 원인: `context_store._relative`(부모 판본 32~35행)가 빈 parts를 안전하지 않은 경로로 거부하지 않았다(`3d7b280`부터). 소비자 `validate_reference`는 `parts[0]`을 무조건 색인했다(`7d2597e`부터). 예외 경계의 어긋남은 B-43과 같다.
- 수정: `9c5356d`가 `_relative`에 `not path.parts` 조건을 넣어 ValueError로 반려하게 했다. 회귀 시험은 `test_reference_catalog.CatalogTests.test_workspace_root_reference_returns_a_submission_issue`다.
- 결함 유형: 검사(경로 검증 조건 누락)
- 트리거: 실제 모델 출력 형태
- 결함 위치 층: L1 원시(경로 검증기). 전파는 L3를 거친다.
- 시험 유출 원인: 시험 없음. 부모 판본의 참조 시험은 `KN-missing`, catalog 경로, `workspace:input/knowledge/K.json` 같은 정상 모양만 썼다.
- 검증런 유출: VR1~VR3이 범위 안에서 놓쳤다.
- 가장 싼 포착 시험: `_relative`에 `"."`, `"./"`, `""`, `"a/.."`를 넣는 표 기반 시험으로, 모두 ValueError를 단언한다.
- 범주 후보: 입력 형식 오류의 반려 경계 이탈

### B-45 동일성 검토의 공급자 이벤트에 든 실수·큰 정수가 정수 전용 저장 해시에서 예외를 내 실행기를 종료시킴

- 출처: `C:\math\임시\do-math_검증_2026-09-24_astra8_3차\장부.md` R1-07(49행), 커밋 `9c5356d`(`scripts/do_math/review_engine.py`)
- 발견 경위: 검증런(VR4)
- 영향 등급: 정지(코드 경로 추론, 운전 미발현)
- 증상: 운전 미발현. identity_review 실행 중 공급자 이벤트(도구 인자·결과)에 `0.25`나 `2**53` 같은 수가 들어가면, `_record_review_observation`의 `kr.digest(event)`가 `canonical_json` → `validate_storage_value`에서 ValueError를 낸다. generator가 커서가 전진하지 않은 같은 이벤트를 다시 읽어 같은 예외를 내고, 예외가 `ModelCalls.collect`·`_run_parallel` 밖으로 전파돼 실행기가 종료한다.
- 근본 원인: `review_engine._record_review_observation`(부모 판본 924~927행)이 공급자 이벤트 원문의 해시를 정수 전용 저장 정규화기로 계산하고, 공급자 JSON 값을 그대로 저장 기록에 넣었다. 공급자 JSON의 수 영역이 저장 계약의 수 영역보다 넓다는 점을 경계에서 다루지 않았다.
- 수정: `9c5356d`가 `event_sha256`를 원문 바이트 해시로 바꾸고, 정규화할 수 없는 값은 정확한 JSON 텍스트로 보존하게 했다. 회귀 시험은 `test_review_engine.ReviewEngineTests.test_public_provider_numbers_survive_storage_and_slot_restoration`이다.
- 결함 유형: 외부 경계(공급자 이벤트 JSON의 수 표현에 대한 가정)
- 트리거: 실제 모델 출력 형태, 실제 외부 도구 동작(CLI 이벤트가 그 값을 그대로 실음)
- 결함 위치 층: L2 인터페이스 요소(검토 관찰 기록). 전파는 L3를 거친다.
- 시험 유출 원인: 합성 입력이 실제와 다름, 대역이 가림. 부모 판본 `test_actual_prompt_and_public_provider_events_restore_only_to_their_slot`(226~245행)은 문자열과 `exit_code: 0`만 든 이벤트를 썼다. `test_redesign_ENGINE.py` 1413행은 drain·observe 경로 시험에서 `_record_review_observation`을 `Mock()`으로 바꿨다.
- 검증런 유출: 결함 행은 `7d2597e`에서 들어왔다. VR1~VR3이 범위 안에서 놓쳤다.
- 가장 싼 포착 시험: 검토 cycle이 있는 엔진 fixture에서 `{'arguments': {'x': 0.5}, 'result': {'y': 2**53}}`를 담은 이벤트로 `_record_review_observation`을 호출한다. 단언은 예외가 없고 `canonical_json(review_cycle)`이 성공한다는 것이다.
- 범주 후보: 공급자 값 영역과 저장 값 영역의 불일치

### B-46 Claude 실행의 사용량 필드를 실행 기록 저장 스키마가 거부해 결과 저장이 실패함

- 출처: `C:\math\임시\do-math_검증_20260925_full\장부.md` R1-12(묶음 R1-M6)·R1-31, 커밋 `d4d273a`(`scripts/do_math/record_schemas/domains.py`)
- 발견 경위: 검증런(VR6)
- 영향 등급: 정지(코드 경로 추론, 운전 미발현). Claude 공급자 프로필의 AI 실행이 끝날 때마다 활성화된다. 이 기간 실사용 인스턴스는 모두 Codex(gpt-6-sol)로 운전해 도달하지 않았다.
- 증상: 운전 미발현
- 근본 원인: 모델 러너(`model_runner.py` 227행 부근)가 Claude 스트림 파서의 `usage_segments`·`model_usage_reported`·`usage_scope`·`reported_models`를 결과에 복사했다. 엔진(`engine.py` 3710행 부근)은 이를 실행 기록에 복사한 뒤 `_save`했다. 그런데 `RECORDS["executions"]`는 `additionalProperties: False`로 닫혀 있었고 네 필드가 등록돼 있지 않았다. 복사 코드는 `98ac7e5`(09-19)부터, 닫힌 스키마는 `7d2597e`(09-23)부터 있었다.
- 수정: `d4d273a`이 `domains.extend()`의 executions 속성에 네 필드를 엄격한 모양으로 추가했다(diff 직접 확인). 회귀 시험은 `test_claude_stream.StreamTests.test_native_usage_metadata_fits_the_execution_storage_contract`와 `test_reporting.ReportingTests.test_claude_usage_projection_survives_git_and_timeline`이다.
- 결함 유형: 스키마·계약 불일치
- 트리거: 설정·환경(Claude 모델 프로필), 실제 모델 출력 형태(Claude stream-json의 usage·modelUsage)
- 결함 위치 층: 계약·스키마(저장 스키마 선언)
- 시험 유출 원인: 합성 입력이 실제와 다름, 시험 없음(파서→저장 결합). `d4d273a^`의 시험 트리에 `usage_segments`는 0건이다. `reported_models`는 파서만 검사하는 시험과 설치 복구 시험에만 나온다. 엔진 경로의 러너 대역은 Claude 스트림 필드가 없는 결과를 돌려줬다.
- 검증런 유출: VR1~VR5가 범위 안에서 놓쳤다.
- 가장 싼 포착 시험: 최소 Claude stream-json(`system/init` 한 줄, usage와 modelUsage를 가진 `result` 한 줄)을 파서에 넣고, 러너가 복사하는 키를 유효한 실행 기록 fixture에 병합해 `RECORDS['executions']` 검증을 통과함을 단언한다. 더 싼 정적 대조로는 "엔진이 러너 결과에서 실행 기록으로 복사하는 키 튜플 ⊆ 실행 기록 스키마의 properties"를 단언한다.
- 범주 후보: 생산자·저장 스키마 모양 불일치

### B-47 범위 평가가 늘린 검토 자리가 있으면 개정판 동일성 검토 시작이 예외로 막힘

- 출처: `C:\math\임시\do-math_검증_20260925_full\장부.md` R1-17, 커밋 `d4d273a`(`scripts/do_math/review_engine.py`의 `_start_identity_review`)
- 발견 경위: 검증런(VR6)
- 영향 등급: 정지(코드 경로 추론, 운전 미발현)
- 증상: 운전 미발현. `engine._call_steps`가 개정 지식의 identity_review 행동에 `_start_identity_review(..., previous_cycle_id=...)`를 호출하면 `ValueError('new revision cannot remove existing reviewer slots')`가 난다. 예외가 `_remove_action`보다 먼저 나서 행동이 큐에 남고, 스케줄러 루프가 예외를 다시 던져 run이 중단된다. 다음 run에서도 같은 행동이 선택된다.
- 근본 원인: `_start_identity_review`(`735d464` 449~455행)는 새 cycle의 자리 수를 정책 최소값으로 다시 계산하고, 이전 cycle의 자리가 더 많으면 거부했다. 그런데 범위 평가의 `initial_slots`가 정책 최소값보다 많은 자리를 만드는 것은 정상 경로다. 거부 문자열은 `3d7b280`(09-14)에서 들어왔다.
- 수정: `d4d273a`이 이전 cycle의 `reviewer_slots`를 그대로 유지하게 했다. 회귀 시험은 `test_review_scope_wire.ExpandedScopeRevisionTests.test_revision_retains_all_prior_slots_above_the_policy_minimum`이다.
- 결함 유형: 검사(과잉)
- 트리거: 특정 전이 순서(범위 평가로 자리가 늘어난 cycle → 지식 개정 → 개정판 동일성 검토 시작)
- 결함 위치 층: L2 인터페이스 요소(검토 상태 전이 규칙)
- 시험 유출 원인: 조합·순서 미탐색. 부모 판본의 개정 뒤 재검토 시험 두 개는 자리 수가 정책 최소값과 같은 cycle만 다뤘고, 범위 평가 시험은 개정 경로를 지나지 않았다.
- 검증런 유출: VR1~VR5가 범위 안에서 놓쳤다.
- 가장 싼 포착 시험: `reviewer_count=2` 정책과 `initial_slots` 3개짜리 scope_assessment로 검토를 시작·완료한 뒤, `_start_identity_review(new_kid, previous_cycle_id=...)`가 예외 없이 이전 자리 3개를 모두 포함함을 단언한다.
- 범주 후보: 확장된 실제 상태를 정책 기본값으로 재검사

### B-48 한도 종결 때 결과 없는 보충 조사(`result: None`)로 검토 질문 연결이 AttributeError를 냄

- 출처: `C:\math\임시\do-math_검증_20260925_opus\장부.md` R1-26, 커밋 `fe59ca0`(`scripts/do_math/question_engine.py`의 `_record_review_questions`)
- 발견 경위: 검증런(VR7)
- 영향 등급: 정지(코드 경로 추론, 운전 미발현). 예외가 `integration.py`의 `except Exception`에 잡혀 생산자 반송이 되는지, run 루프 밖으로 빠지는지는 확정하지 못했다. 어느 쪽이든 상태에 의존하는 결정적 반복 실패여서 그 지식의 동일성 검토 공개가 막힌다.
- 증상: 운전 미발현
- 근본 원인: `review_cycle.py`(`a299fd8` 643행)는 보충 조사 요청을 `"result": None`으로 저장했다. 한도·예산 종결 때 `_publish_identity_review_result`가 `_record_review_questions`를 호출하는데, 거기서 `request.get("result", {})`는 키가 있으므로 None을 돌려줬고 이어지는 `.get`이 AttributeError를 냈다. 생산자의 명시적 null과 소비자의 "키 없음" 기본값 가정이 어긋났다.
- 수정: `fe59ca0`가 `(request.get("result") or {})`로 바꿨다. 회귀 시험은 `test_questions.QuestionTests.test_review_questions_include_pending_research_without_a_result`다.
- 결함 유형: 스키마·계약 불일치(생산자 null과 소비자 누락 가정)
- 트리거: 특정 전이 순서(한 자리의 보충 조사가 pending인 채 cycle이 한도·예산으로 종결)
- 결함 위치 층: L2 인터페이스 요소
- 시험 유출 원인: 조합·순서 미탐색. `a299fd8`의 시험 트리에 `_record_review_questions`를 부르는 시험이 없었다. 한도 종결 엔진 시험(`test_review_research.py` 약 170행)은 다른 자리의 pending 요청이 남는 조합이 아니었다.
- 검증런 유출: VR1~VR6이 범위 안에서 놓쳤다.
- 가장 싼 포착 시험: research에 `{"status": "pending", "result": None}` 한 건이 있는 cycle로 `_record_review_questions`를 호출해 예외가 없음을 단언한다. 일반형은 생산자 `defer_for_research`가 만든 레코드를 그대로 소비자에 넣는 왕복 시험이다.
- 범주 후보: 명시적 null과 누락 기본값의 혼동

### B-49 verify_lean과 inspect_toolchain의 실행 파일 경로 정규화가 달라 PATH로 찾은 Lean의 형식 검사를 항상 거부함

- 출처: `C:\math\임시\do-math_검증_20260925_opus\장부.md` R1-47, 커밋 `fe59ca0`(`scripts/do_math/formal.py`의 `verify_lean`)
- 발견 경위: 검증런(VR7)
- 영향 등급: 정지(코드 경로 추론, 운전 미발현). 형식 검사 전건이 거부된다. `setup_lean`의 portable 준비를 마친 설치에서는 기본 탐색이 절대 경로를 쓰므로 활성화되지 않는다.
- 증상: 운전 미발현. 모든 형식 검사가 `approved toolchain changed before execution`으로 거부된다.
- 근본 원인: `verify_lean`(`a299fd8` 약 418행)은 PATH 탐색 경로를 `Path(shutil.which(...))`로 두고 `.resolve()`하지 않았다. 승인 toolchain을 만드는 `inspect_toolchain`(359행)은 `.resolve(strict=True)`를 기록했다. `_approved_files_current`(385행)가 둘을 문자열 비교했는데, Windows에서 `shutil.which`는 PATHEXT 확장자를 대문자로 붙이고 `resolve`는 디스크 표기를 돌려줘 항상 달랐다. 두 줄 모두 `7d2597e`에서 들어왔다.
- 수정: `fe59ca0`가 `verify_lean`에서도 `.resolve()`하게 했다(diff 직접 확인). 회귀 시험은 `test_formal.T.test_path_lookup_spelling_matches_the_inspected_executable`(Windows 전용)이고, 기존 두 시험이 `inspect_toolchain` 생산자를 쓰도록 바뀌었다.
- 결함 유형: 외부 경계(Windows `shutil.which`·PATHEXT 표기). 생산자·검사자의 정규화 이중 구현도 원인이다.
- 트리거: 실제 외부 도구 동작(Windows PATHEXT, 대소문자 비구분 파일 시스템), 설정·환경(PATH 탐색 Lean 또는 사용자 `lean_command`)
- 결함 위치 층: 경계 어댑터(Lean 실행)
- 시험 유출 원인: 합성 입력이 실제와 다름, 환경 차이. `test_formal.test_changed_approved_executable_is_rejected_before_version_execution`은 `expected_toolchain`을 생산자 대신 손으로 만들었다. `inspect_toolchain`을 실제로 쓰는 시험 셋은 모두 절대 경로·정규 표기만 썼다.
- 검증런 유출: VR1~VR6이 범위 안에서 놓쳤다.
- 가장 싼 포착 시험: 임시 폴더의 `x.exe`를 `X.EXE` 표기나 PATH 이름으로 지정하고 `expected = inspect_toolchain(command)`을 구한 뒤, 같은 command로 `verify_lean(expected_toolchain=expected)`을 호출해 거부 사유가 toolchain 변경이 아님을 단언한다(Windows 러너). OS와 무관하게는 생산자와 검사자가 같은 식별자 함수를 쓰는지 정적으로 대조한다.
- 범주 후보: 동일 식별자의 이중 정규화

## 4. 관찰

### 4.1 사실: 이 기간 정지급 결함의 발견 경위

개별 기록 49건 가운데 정지는 25건이다.

- 실제 운전에서 드러난 정지는 3건이다. B-01·B-02는 첫 초기화 세션의 초기화 미완료, B-17은 RI-B의 설치 수리 대기다.
- 나머지 22건은 운전에서 발현되지 않았다. 정적 감사의 재현 2건(B-28, B-29), 감사 마지막 단계의 시험 실행 2건(B-30, B-31), 검증런 장부 18건(B-32~B-49)이다.

사용자의 관찰 중 "연구 인스턴스의 작동을 멈추게 하는 결함이 20~30개 섞였다"는 이 기간에 대해 이렇게 나뉜다. 정지급으로 분류된 결함은 25건이지만, 실제 운전을 멈춘 것은 3건이다. 나머지는 코드 경로 추론이나 시험·재현에서 확인된 것이다.

실사용에서 드러난 결함 26건(B-01~B-27 가운데 B-13 제외)을 앞선 검증런이 미리 찾은 사례는 없다.

- RI-A 결함 10건(B-03~B-12)의 코드는 VR1~VR5의 범위 안에 있었다.
- RI-B 결함 14건(B-14~B-27)의 코드는 대부분 VR1~VR6의 범위 안에 있었다.
- B-01·B-02는 VR1~VR5의 범위 안에 있었다.

특히 B-07(역할 계약이 요구하는 근거를 입력이 주지 않음)과 B-08(입력 광고 집합과 적용 검사 집합의 불일치)은 이 검증런들의 명시 초점인 "생산자·소비자 계약 불일치"에 정확히 드는 결함이다. B-14는 "최근 실사용 수리의 불충분함"을 명시 초점으로 삼은 VR6이 놓쳤다.

### 4.2 사실: 검증런은 수렴하지 않았다

검증런 장부의 정지급 결함 18건은 모두 이 기간 첫 검증런의 앵커(`fa49372`)보다 먼저 들어왔다. 15건은 `7d2597e`(09-23, 기능 판본 5)에서 성립했다. 이 15건에는 앞선 코드와 결합해 그때 성립한 B-36·B-44·B-46이 포함된다. 나머지 3건(B-39, B-47, B-48)은 그보다 앞선 `3d7b280`(09-14)·`98ac7e5`(09-19)에서 들어왔다. 그런데도 각 검증런이 새로 찾은 정지급 결함 수는 다음과 같다.

| 검증런 | VR1 | VR2 | VR3 | VR4 | VR5 | VR6 | VR7 |
|---|---:|---:|---:|---:|---:|---:|---:|
| 새로 찾은 정지급 | 1 | 5 | 5 | 3 | 0 | 2 | 2 |

뒤의 검증런은 앞 검증런이 범위 안에서 놓친 결함을 계속 찾았다. VR5는 제기 111건 가운데 92건이 정리·문서 항목이었고 정지급은 0건이었다.

VR1 1라운드는 관점 수리자 둘이 독해 계약 미충족으로 결번이었다. VR2·VR3의 관점 수리자는 영역 하나만 필수로 통독했다. 그러므로 "범위 안에서 놓침"의 무게는 런마다 다르다(VR1~VR3 조사 에이전트 보고).

### 4.3 사실: 반복된 결함 기제

- **생산자·저장 스키마 모양 불일치(닫힌 저장 스키마).** B-02, B-34, B-40, B-41, B-46, B-48이 여기에 들고, 저하로 분류된 VR4 R1-19(`description`)와 VR5 R1-01(질문 해소 필드)도 같은 기제다. 공통 사실이 둘 있다. 생산자가 실제로 만든 출력이 저장 검사를 통과하는지 한 번도 대조되지 않았고, 대부분 대역이나 손으로 만든 fixture가 그 대조를 건너뛰었다. 가장 싼 포착 시험은 모두 "생산자 출력 → 수신 스키마" 왕복 대조라는 같은 모양이다.
- **입력 형식 오류의 반려 경계 이탈.** B-29, B-43, B-44, B-45가 여기에 들고, VR3 R1-07(잠재)도 같은 기제다. 구조를 확인하기 전에 타입 의존 연산을 하고, 상위 경계는 일부 예외 종류만 잡는다. 그래서 실행기 예외 종료나 영구 반복 실패가 된다. 네 번의 수정(`9a3d345`, `9c5356d`, `c4d7838`)은 모두 개별 입구에 가드를 더했고, 예외 경계 자체는 바꾸지 않았다.
- **합성 입력이 결함을 정상으로 고정함.** 다음 사례에서는 당시 fixture가 결함 패턴을 그대로 담았거나, 결함 동작을 기대값으로 단언했다.
  - B-14·B-15: `trust_fixture`가 여섯 role 파일과 자유 문자열 증거로 manifest를 만들었다.
  - B-16: `bind_candidates`가 전 등급 프로필을 넣었다.
  - B-08: 합성 처분이 우연히 허용되는 참조 하나만 썼다.
  - B-09: 과잉 무효화를 기대값으로 단언했다.
  - B-32: `goal`을 필수로 넣고 overflow를 정상으로 단언했다.
  - B-42: 미래 ID를 missing_inputs에 넣었다.
- **대역이 결함 지점을 가림.** B-01(예약 어댑터), B-25(`subprocess.run`), B-34(저장소 `InputSnapshot`), B-35(Codex 러너 `Mock`), B-36(`_call_steps` 대역), B-45(`_record_review_observation` `Mock`)가 여기에 든다. 모두 결함이 있는 바로 그 함수나 층을 대역이 대체했다.
- **수리가 새 정지급 결함을 들여옴.** 실사용 결함을 고친 `ff9b2b9`이 B-28, B-30을 들여왔고, 지연 게시와 함께 B-31의 이음새를 만들었다. `c44dd7b`의 checkpoint 전달 수정 뒤에도 같은 계열의 D3·D4(저하)가 남았다. `a299fd8`의 공통 원자 교체 뒤에는 VR7 R1-14·R1-50의 파급 누락이 남았다. 기억 노드 M-0341·M-0342·M-0343에는 구현 중 자체 검토로 잡힌 결함도 더 있다(2절 표의 "작업 중 발견"). 이 결함들은 커밋 전에 고쳐졌다.
- **있는 시험이 실행되지 않음.** B-30·B-31을 드러낸 통합 시험은 결함 도입 전부터 있었다. 그러나 `ff9b2b9`·`c44dd7b`·`c4d7838`의 검증 집계 세 개(`validation-summary.json`)에 그 이름이 한 번도 나오지 않는다. 같은 기간의 모든 수리 작업이 "선택 시험"만 돌렸고, 전체 통합 시험의 완주 기록은 없다(M-0334, M-0339, M-0344, M-0346, M-0347). VR5·VR6·VR7에서는 앵커 판본에서도 실패하던 시험(`{"passed": true}` 증거, 누락된 `verifier_path`, 옛 입력 형식을 읽는 제출 도우미)이 뒤늦게 발견됐다. 시험 자체가 현행 계약과 어긋난 채 돌지 않고 있었다는 뜻이다.
- **규모·시간 의존 결함은 모두 실사용에서만 드러남.** B-03, B-04, B-05, B-06, B-23, B-27은 56,230개 파일·159MB 상태·실제 사건 backlog에서만 드러났다. 당시 fixture는 6개 파일과 소수 사건이었다.

### 4.4 추론: 재편 설계에 주는 시사

아래는 위 사실에서 끌어낸 추론이며 검증된 결론이 아니다.

- 이 기간 정지급 결함의 다수는 L1·L2 층의 두 계약 경계에 있다. 하나는 생산자 출력과 수신 스키마의 경계, 다른 하나는 공개 입력과 반려 경계다. 두 경계 모두 "생산자가 만드는 모든 모양 ⊆ 수신자가 받는 모양"과 "모든 잘못된 모양 → 구조화된 반려"라는 두 속성 시험으로 결정적으로, 그리고 모델·프로세스 없이 싸게 잡을 수 있었다.
- 실사용 정지 3건 가운데 B-01은 L3 배선과 경계 어댑터에 있고, B-17은 L2 조합 순서에 있다. B-01은 실제 OS 실행 한 번, B-17은 메모리 상태의 조합 시험 하나로 잡을 수 있었다.
- 실사용 저하 결함은 대부분 규모와 시간 의존이다. 소형 fixture 중심의 시험 체계로는 원리상 잡히지 않는다. 호출·읽기·바이트 수를 계수하는 불변식 단언이 가장 싼 대안이다.

### 4.5 판정 일관성과 한계

- **과제 단위 영구 대기의 등급이 조사자마다 다르다.** B-38·B-42(VR3)는 과제 단위 영구 대기를 정지로 판정했다. VR6 조사자는 같은 종류인 R1-18·R1-37(활동 `/role` 조건을 쓴 과제의 영구 not_ready)을 "다른 작업은 계속된다"며 저하로 판정했다. 나는 B-09를 저하로 두고 잠재적 정지 영향을 따로 적었다. 서식 3절의 정지 정의("연구 인스턴스가 더 진행하지 못한다")는 인스턴스 단위라서, 과제 하나만 멈추는 경우를 가르지 않는다. 집계자가 한 기준으로 다시 맞출 필요가 있다.
- **정지와 저하의 경계로 보고된 저하 항목.** 각 조사 에이전트가 경계에 있다고 보고한 항목은 다음과 같다.
  - VR1 R2-11
  - VR3 R1-02(무한 재시도의 제동 없음)
  - VR4 R1-19, R1-02·R1-22, R1-20
  - VR5 R1-01, R1-100
  - VR6 R1-01, R1-08
  - VR7 R1-01(복구 실행 실패 시 `recovery_waiting` 고착), R1-49
- **정지 판정은 모두 코드 경로 추론이다.** B-32~B-49의 정지 판정은 시험을 실행하지 않은 추론이다. 예외 전파 경로를 끝까지 확정하지 못한 항목은 B-33, B-48이다. 조사자 보고에 따르면 현행 HEAD의 seal·pump 예외 경계도 여전히 좁다. 같은 계열의 다른 예외가 지금도 실행기를 종료시킬 수 있는지는 확인되지 않았다.
- **구현 중 자체 검토로 잡힌 결함.** `research-reliability-20260925\implementation-review.md`의 두 P1(완료 근거에서 관계 끝점 누락, 부분 JSONL 행 경계 오판)이 여기에 든다. 커밋 전 작업 중에 잡혀 기록 대상에서 뺐고 2절에서 건수로만 셌다.

### 4.6 서식 결함

- **4절 시험 유출 원인에 "있는 시험·검사를 실행하지 않음" 값이 없다.** B-13(드리프트 검사), B-30·B-31(통합 시험)이 이 경우인데, 가장 가까운 값을 고르고 설명을 붙였다. 4.3의 사실로 보면 이 기간의 주요 유출 경로 가운데 하나다.
- **3절 영향 등급의 기준축이 섞여 있다.** "잠재"는 운전 미발현을 기준으로, "정지·저하"는 결과를 기준으로 정의돼 있다. 그래서 운전 미발현인 정지급 결함(1절이 기록 대상으로 명시)의 등급이 정의상 둘 다에 걸린다. 나는 결과 기준을 우선해 "정지(코드 경로 추론, 운전 미발현)"로 표기했다.
- **5절 결함 위치 층에 배포·패키징(정본과 생성 사본)과 시험 인프라 자체의 층이 없다.** B-13은 가장 가까운 "계약·스키마"로 분류했다.
- **3절이 과제 단위 정지와 인스턴스 단위 정지를 구별하지 않는다(4.5).**
