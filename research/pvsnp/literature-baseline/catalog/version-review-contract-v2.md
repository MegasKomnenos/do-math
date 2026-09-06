# Version 내용 선별 실행 계약 v2

정책 의미 판본은 `pvsnp-version-screening/2`다. 이 계약은 [최종 절차 결정](../reports/version-review-procedure-decision.md)을 실행하는 작업자·검사기·집계기의 계약이다. v1 계약·코드·queue·판정·manifest는 변경하지 않는다. 현재 실행 가능 여부는 `STATUS.md`와 전환 수용 검사 결과가 정한다. 파일이 존재한다는 사실만으로 전환 관문을 통과하지 않는다.

## 1. 결과와 소유자

판정 단위는 version이며 같은 work의 다른 version으로 복사하지 않는다. 다섯 처분 `core_candidate`, `context_material`, `search_noise`, `relationship_only`, `defer`와 그 의미는 최종 결정문 4절을 따른다. 제목·인용 수·분류 표지만으로 처분하지 않는다. core_candidate는 후속 정확한 원문 판독의 후보이며 최종 핵심 문헌이 아니다.

생산자는 배정된 version마다 실제 기여와 재진입 역할을 판단한다. 검증자는 core_candidate·search_noise·defer 전건을 독립적으로 판독한다. context_material·relationship_only는 기계 참조 검사와 총괄 표본 감사를 받는다. 총괄은 서로 다른 처분뿐 아니라 기여·역할·판독 범위의 실질 차이를 원자료에서 해소하고, 합의된 오류도 감사한다. 정밀 판독과 논증 검증은 후속 단계다.

배정 정본은 `manifests/version-review-v2-batch-NNN.json`이다. 각 생산 그룹은 version ID·행 SHA, reviewer·실제 실행자 actor, 출력 경로를 갖는다. 검증과 resolution의 작성자·출력도 별도로 고정한다. 같은 version의 생산 소유자는 하나이고 작업자끼리 파일을 공유해 수정하지 않는다. 동시 실행은 총괄·생산 둘·검증 하나의 최대 네 기다.

분야·문서 유형은 기존 source의 MSC·서지·provenance에서 배정용으로 읽는다. 여러 분야와 미분류를 허용하며 열린 분야들을 순환한다. 배정용 표지는 queue나 내용 판정의 해시에 섞지 않는다. 정확한 판정 전에 전체 queue를 새 분야 체계로 분류하는 작업을 추가하지 않는다.

## 2. 실제 자료와 회수 기록

`scripts/version_review_evidence.py`가 원자료 회수·추출·선택 범위를 기록한다. `intake/`는 읽기 전용이다. 새 원격 자료·파생 표시물은 비추적 `originals/version-review/`, 자동 기록은 `catalog/version-review-evidence/`에 로컬 보존하고 Git에서 제외한다(2026-09-06 사용자 결정). 판정·감사·manifest는 계속 Git 추적 대상으로 유지한다. 자동 기록과 비추적 실물은 별도 백업 대상이며, Git만으로는 복구할 수 없다. 같은 실물을 공유할 수 있지만 판정과 이유는 최초 봉인 전 서로 보지 않는다.

자동 기록은 요청 version·입력 SHA, 시각, 출처·최종 URL 또는 원 export의 record/rank, 실제 실물·표시물의 경로·바이트·해시를 결박한다. 선택 범위는 PDF 쪽, HTML의 실제 보이는 정확한 구간, JSON pointer, 로컬 record의 필드다. HTTP 오류, 빈 응답, JS 화면, 추출 실패와 스캔을 구별한다. 확보·추출·표시 기록은 사람이든 AI든 실제로 이해했음을 증명하지 않는다.

근거 행의 정확 필드는 다음과 같다.

| 필드 | 값 |
|---|---|
| `receipt` | 자동 기록의 `{path, sha256}` |
| `read_scope` | 아래 여덟 값 중 실제 읽은 종류 |
| `locator` | 해당 자동 기록의 display 좌표. 접근 시도는 `receipt:request` |
| `target_relation` | `target_version`, `same_work_other_version`, `independent_work`, `unresolved` |
| `applicability` | 적용 관계 설명. 같은 work의 다른 판본은 별도 관계 근거를 반드시 기재 |
| `observation` | 그 위치에서 직접 확인한 사실과 한계 |

read_scope는 `bibliographic`, `abstract`, `publisher_description`, `table_of_contents`, `front_matter`, `selected_body`, `full_text`, `access_attempt`로 닫는다. 서론은 selected_body, 저자·편집자 서문은 front_matter, 제목면·판권면은 bibliographic이다. 소개와 목차를 함께 읽으면 근거를 나눈다. 전문을 확보했지만 일부만 읽었으면 full_text로 기록하지 않는다. 신규 행에 selected_full_text를 쓰지 않는다.

target_relation은 대상 판본 자체, 같은 work의 다른 판본, 별개의 후속·비판 저작, 귀속 미확정을 뜻한다. 다른 판본·다른 저작을 대상 본문 판독량에 넣지 않는다. 후속 저작은 역할 근거이지 대상 본문의 대체물이 아니다.

실물은 자동 폐기하지 않는다. 활성 선별·정밀 판독·동결 패키지·후속 수입이 참조하는 동안 유지한다. 폐기는 사용자가 명시적으로 승인한 정확한 범위에서만 수행한다. 작업공간 이관 때 자동 회수 근거 기록과 Git 비추적 실물도 전달하고 목적지 경로·해시를 확인한다. 유실되면 영향받은 근거 의무만 다시 열고 역사적 결과는 보존한다. 인증 헤더·Cookie·크리덴셜은 기록하지 않는다.

## 3. 판정 행과 독립 판정

신규 판정의 필드는 다음 열 개다. 알 수 없는 필드는 수리 대상으로 반환한다.

`schema_version`, `policy_version`, `version_id`, `version_sha256`, `reviewer`, `disposition`, `basis`, `role_in_field`, `evidence`, `limitations`.

schema_version은 `pvsnp-version-review-decision/2`다. policy_version은 위 정책 의미 판본이다. reviewer는 배정값과 같아야 한다. evidence는 2절의 실제 근거 행을 담는 비어 있지 않은 목록이다. resolution만 `compared_sha256s`를 추가하며 비교한 현재 생산·독립 판정 SHA 전부를 결박한다.

basis는 실제 자료가 제공하는 정의·결과·방법·종합·반론과 그 대상·가정을 설명한다. role_in_field는 어느 분야에 어떤 역할로 다시 읽어야 하는지 설명한다. 새 결과가 있다는 말만으로 핵심 후보의 역할을 대신하지 않는다. 서지상의 주장과 검토자의 추론을 구별한다. limitations는 읽지 못한 범위·조건과 남은 불확실성을 적는다.

자료와 역할이 초록에서 분명하면 추가 완독을 요구하지 않는다. 처분을 바꿀 불확실성이 있으면 필요한 서론·주요 결과·관계 자료까지만 더 읽는다. 실제 정보 부족은 defer가 될 수 있지만 미실행·시간 부족·도구 오류·검토자의 낯섦은 처분이 아니라 남은 작업이다.

생산·검증 판정은 최초 봉인 전 상대의 처분·이유와 총괄의 새 결론을 보지 않는다. 실제 실행자와 허용 입력·봉인 순서는 파견 기록에 남긴다. reviewer 문자열 자체가 독립 실행을 증명하지 않는다. 검증자가 먼저 제출해도 수락하며 그 version만 생산 대기로 남긴다.

## 4. 총괄 감사

생산·필수 검증·근거 검사·차이 해소가 끝난 행은 `pending`이며 대기 이유는 `audit`다. 이 시점의 배정 안에서 준비된 행 전부를 `audit-template`으로 먼저 고정한다. 도구가 `catalog/version-reviews-v2/scopes/`에 immutable 입력 집합과 그 판정 SHA를 저장한다. 표본을 고른 뒤 집합에서 행을 빼지 않는다.

총괄은 고정 집합에 존재하는 합의 core, 합의 noise, 역할 감사가 없던 분야·다분야·미분류, 소개·목차·전면부 의존, context, relationship 범주를 최소 한 표본씩 감사한다. 한 표본이 여러 범주를 충족할 수 있다. 없는 범주는 빈 목록으로 남긴다. 이는 위험 감사이며 오류율 추정용 통계 표본이 아니다.

감사 파일은 `catalog/version-reviews-v2/audit-NNN-<checkpoint>.json`이다. 고정 양식의 members·categories·scope_ref를 보존하고 다음을 채운다.

- `samples`: version_id·decision_sha256·basis·evidence_refs·conclusion. evidence_refs는 2절의 실제 근거 행 목록이며 URL 문자열만 쓰지 않는다.
- `comparisons`: 생산·독립 판정 둘 이상이 있는 각 version ID를 비교한 전체 decision SHA 목록에 연결한다. 총괄이 기여·역할·판독 범위의 실질 차이를 대조한 뒤에만 채운다. label 일치만으로 자동 생성해 완료하지 않는다.
- `reviewer`: coordinator. `conclusion`: 모든 필요한 검사와 결함 해소 뒤 pass. 미해소 내용 차이는 원자료 resolution으로 먼저 닫는다.

새 행은 자체 감사 집합을 갖는다. 과거 집합의 표본으로 새 집합의 최소 표본 수를 대신하지 않는다. 같은 행을 전환·재개할 때 유효한 실물·판독은 재사용한다. 과거 감사의 변경되지 않은 행은 보존하고 현재 SHA가 바뀐 행만 현재 감사 적용에서 제외한다. 공통 오류가 입증되면 그 원인이 영향을 준 범위만 재검토한다.

## 5. 검사·상태·실패 처리

집계 상태는 pending·conflict·complete 세 값이다. 대기 이유는 production·verification·evidence·audit·repair 중 필요한 항목의 집합이다. 미해소 실질 차이는 conflict를 우선 표시한다. 현재 최종 처분은 complete에서만 노출한다. 구계약의 역사적 처분은 별도 표지로 보존한다.

행 JSON·필드·범위·실물 검사가 실패하면 파일·줄·줄 SHA·영향 ID·원인을 남기고 해당 행만 격리한다. ID를 판독할 수 없으면 배정 범위에서 영향을 가리며, 그동안 그 범위의 완료만 보류한다. 정상 행을 삭제하거나 조용히 오류 행을 건너뛰지 않는다. 파일 부재와 중복 제출도 검사 통과가 아니다.

의미를 바꾸지 않는 형식 수리는 작성자가 처리한다. 기여·역할·처분을 바꾸는 수리는 해당 판단 책임자 또는 총괄 resolution이 처리한다. 원자료 접근 부족은 개별 의무로 남긴다. 새로운 인증·비용·외부 연락이나 승인 범위 확장이 필요할 때만 사용자에게 상신한다.

초기 입력 세대 생성·새 배정·최종 전수 종료에는 전체 manifest와 source/version/work 참조를 검사한다. 일상 제출·감사는 관련 version 행·정책·근거·판정·resolution·감사에 한정한다. 보고서 문구와 배정 표지의 변경을 내용 재판정으로 바꾸지 않는다. v2 구현 코드의 해시는 검사 재현 이력이다.

## 6. 기존 판정의 의미보존 전환

`scripts/version_review_migration.py`는 보존된 v1 state에서 현재 효력 원행 또는 resolution과 실제 독립 판정 SHA를 찾는다. 전환은 `catalog/version-reviews-v2/legacy-adoptions.jsonl`에 추가하며 과거 판정을 새 독립 판독으로 다시 작성하지 않는다.

adoption의 정확 필드는 schema_version(`pvsnp-version-review-adoption/2`), policy_version, version_id, historical_decision_sha256, decision, semantic_review, preserved_decision_sha256s다. decision은 3절의 v2 행이며 현재 receipt 근거를 갖는다. disposition·basis·role_in_field·limitations는 현재 효력 v1 원행과 같아야 한다. 의미가 바뀌면 이 경로로 확정하지 않고 해당 version을 재판정 대상으로 남긴다.

semantic_review는 coordinator의 실제 대조 basis와 당시 조사 보고의 immutable report_ref를 갖는다. template의 빈 basis는 자동 승인을 막기 위한 미완성 표시이며 총괄이 실제 대조한 후에만 채운다. 보고서 snapshot은 support/ 아래 내용 해시로 한 번 보존하므로 원 보고서의 후속 문구 변경이 이미 전환한 판정을 무효화하지 않는다.

전환 검사는 근거·형식·의미보존의 요건만 확인한다. 통과 후에도 pending/audit이며, `audit-template --batch 0`으로 그때 준비된 legacy 행을 고정해 총괄 감사해야 complete가 된다. 새로 준비된 legacy 행은 다음 감사 집합에 넣고 이미 닫힌 집합은 보존한다. 70개 전부가 준비될 때까지 기다릴 필요는 없다.

```powershell
python research/pvsnp/literature-baseline/scripts/version_review_migration.py template --help
python research/pvsnp/literature-baseline/scripts/version_review_migration.py check --adoptions research/pvsnp/literature-baseline/catalog/version-reviews-v2/legacy-adoptions.jsonl
python research/pvsnp/literature-baseline/scripts/build_version_review_v2.py audit-template --batch 0
```

## 7. 실행 명령

아래는 저장소 루트 `C:\math`에서 실행한다. initialize는 기존 manifest·참조를 확인하고 v2 입력 세대와 70개 전환 의무를 별도 파일로 만든다. 기존 결과를 덮어쓰지 않는다.

```powershell
python research/pvsnp/literature-baseline/scripts/build_version_review_v2.py initialize
python research/pvsnp/literature-baseline/scripts/build_version_review_v2.py check-generation
python research/pvsnp/literature-baseline/scripts/version_review_evidence.py --help
python research/pvsnp/literature-baseline/scripts/version_review_evidence.py view --help
python research/pvsnp/literature-baseline/scripts/build_version_review_v2.py check --batch 2 --decisions catalog/version-reviews-v2/production-002-a.jsonl
python research/pvsnp/literature-baseline/scripts/build_version_review_v2.py audit-template --batch 2
python research/pvsnp/literature-baseline/scripts/build_version_review_v2.py results
```

check의 PASS는 지정 파일의 기계 검사를 통과했다는 뜻이며 내용 감사나 version 선별 완료가 아니다. PARTIAL/exit 2이면 반환된 좌표만 수리하고 재검사한다. results는 정상 범위·미완료 ID·결함을 함께 보존하며 `catalog/version-review-state-v2.jsonl`, `catalog/work-review-state-v2.jsonl`, `catalog/version-review-v2-issues.jsonl`, `manifests/version-review-results-v2.json`을 갱신한다.

새 배정은 전환 수용 시험과 독립 검토, 기존 70개 의무의 ID·원인·담당 추적을 결박한 `manifests/version-review-v2-transition-gate.json`이 통과한 뒤에만 연다. gate의 passed 문자열만으로는 부족하다. 실제 검사 보고·계약·입력 세대·전환 기록의 필수 참조를 확인한다. gate는 기존 70개 모두의 v2 완료를 요구하지 않는다.

```powershell
python research/pvsnp/literature-baseline/scripts/build_version_review_v2.py batch --batch 2 --size 4 --after-field MSC:04 --actor-a /root/bulk002_a --actor-b /root/bulk002_b --actor-v /root/bulk002_verify
python -m unittest discover -s research/pvsnp/literature-baseline/tests -p 'test_*.py'
python -m compileall -q research/pvsnp/literature-baseline/scripts research/pvsnp/literature-baseline/tests
```

actor 인자는 실제 파견 작업의 정규 이름과 맞춘다. --size는 생산자별 최대 배정 수이며 완료 목표나 문헌 선별 기준이 아니다. 같은 배정 번호로 재개하면 새 ID를 만들지 않는다.

최종 전수 선별 종료에는 현재 version 전건의 처분 하나, 남은 작업·필수 검증 누락·미해소 이의·검사 결함 0, work 집계·참조 폐쇄·manifest·동일 입력 재현성·전체 테스트 통과가 필요하다. 구성요소 전개·참고문헌 추출·최종 누락 검사와 문헌 집합 동결은 아직 시작하지 않는다.
