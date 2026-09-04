# B002 MathSciNet 자동 수집 검사

판정: **통과**

검사일: 2026-09-04 KST

## 1. 검증 대상

[`../scripts/mathscinet_collect.py`](../scripts/mathscinet_collect.py)가 KUDOS 인증과 기관 프록시를 거쳐 MathSciNet의 `B002-queries.tsv` 63개 검색을 실행하고, 각 검색의 인용순 첫 페이지를 BibTeX로 저장하는지 검사했다.

수집 범위는 분야당 최대 100개 citation이다. 프로그램은 원문·Review PDF·두 번째 결과 페이지를 요청하지 않았다. Playwright 1.62.0과 시스템 Google Chrome 채널을 사용했다.

## 2. 수동 결과와의 독립 대조

프로그램을 기존 B002 출력과 다른 `intake/B002-probe/`에서 00·01·03에 다시 실행했다. 사용자가 만든 수동 export를 기대 결과로 사용했다.

| 분야 | 전체 검색 결과 | 수동 레코드 | 자동 레코드 | MR 키 집합 | MR 키 순서 | LF 정규화 전체 바이트 |
|---|---:|---:|---:|---|---|---|
| `00` | 583 | 100 | 100 | 동일 | 동일 | 동일 |
| `01` | 1,118 | 100 | 100 | 동일 | 동일 | 동일 |
| `03` | 1,749 | 100 | 100 | 동일 | 동일 | 동일 |

정규화한 BibTeX SHA-256도 수동·자동 사이에 각각 일치했다.

- `00`: `8b7d96f4d94d41560c6079ba598efb313c2532d564a8a1925a45565a8123fd81`
- `01`: `71093f051e93fe18106ec248cfecae0ae8e069a4f7eeab63be66cddd7e331f81`
- `03`: `7a0a5152958ccd7db39493b4a05002ef09849b6652a09d4957e536f2f9c3ba7e`

수동 파일은 CRLF이고 프로그램 파일은 LF여서 원시 바이트 크기는 달랐다. 줄바꿈을 LF로 맞추면 내용 전체가 같다.

## 3. 발견하고 수리한 결함

실물 probe에서 다음 세 결함을 순서대로 재현하고 고쳤다.

1. 최초 검색 URL은 MathSciNet의 `OR` 대신 다른 서비스의 `|` 연산자를 사용해 전체 4,674,413건을 반환했다. 검색표와 MathSciNet 화면이 사용하는 `OR`로 고친 뒤 00 검색이 583건을 반환했다.
2. SPA의 정적 결과 컨테이너를 검색 완료로 오인했다. 실제 결과 checkbox 또는 명시적 0건 문면이 나타날 때까지 기다리게 고쳤다.
3. Bootstrap-Vue checkbox의 숨은 input을 Playwright가 직접 누를 때 label이 포인터를 가로챘다. 실제 label의 native click을 발생시키고 100개 선택 상태를 확인하게 고쳤다.

citation 저장 뒤 모달 `OK`를 누르는 동작은 다음 검색의 URL 이동에 필요하지 않으며 포인터 경합만 만들었다. 그 동작을 제거했다.

## 4. 전체 실행 결과

00·01·03의 수동 결과를 보존하고 나머지 60개 분야를 한 세션에서 순차 실행했다. 각 자동 결과는 다음을 통과한 뒤 저장됐다.

- BibTeX 엔트리 한 개 이상, 100개 이하
- BibTeX 키 중복 없음
- 요청한 MSC 코드가 적어도 한 엔트리의 `mrclass`에 존재
- metadata의 `exported_records`와 실제 엔트리 수 일치
- 임시 파일을 최종 파일로 원자 교체

전체 산출은 63개 분야, 6,233개 레코드다. 분야별 결과 수 분포는 다음과 같다.

| export 레코드 수 | 분야 수 | 설명 |
|---:|---:|---|
| 100 | 60 | 인용순 첫 페이지 |
| 89 | 1 | MSC `19`, 전체 결과 89건 |
| 85 | 1 | MSC `85`, 전체 결과 85건 |
| 59 | 1 | MSC `97`, 전체 결과 59건 |

63개 검색의 전체 hit 수 합은 61,500건이다. 분야가 겹치므로 이는 고유 문헌 수가 아니다.

일부 기록은 현행 요청 코드가 아니라 역사적 MSC나 연결 분류만 `mrclass`에 보인다. 이는 동일한 수동 검색에서도 나타나는 MathSciNet 결과 특성이다. 01의 수동·자동 100건이 완전히 같았다는 대조와 분야 가족 포함을 함께 보존하며, 후속 정규화에서 판본별 MSC 이력을 확인한다.

## 5. 회귀 검사

다음을 실행해 통과했다.

```powershell
python -m unittest research/pvsnp/literature-baseline/tests/test_mathscinet_collect.py
python research/pvsnp/literature-baseline/scripts/mathscinet_collect.py --dry-run
```

단위 검사 8건이 통과했다. dry run은 `pending=0`, `skipped=63`을 반환해 기존 유효 결과를 다시 검색하거나 덮어쓰지 않음을 확인했다.

파일별 경로·크기·SHA-256·검색 hit 수·export 수는 [`../manifests/B002.json`](../manifests/B002.json)에 있다.
