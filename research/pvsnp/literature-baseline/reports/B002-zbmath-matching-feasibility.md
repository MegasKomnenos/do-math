# B002 DOI 없는 후보의 zbMATH Open 대조 가능성

기준 시각: 2026-09-04 KST  
대상: B002 후보 중 정규화 DOI가 빈 **2,710개**.  
상태: **전수 실행 전 가능성 평가. 후속 전수 결과는 [`B002-zbmath-matching-audit.md`](B002-zbmath-matching-audit.md)에 있다.**

## 결론

zbMATH citation matcher의 공식 POST batch는 DOI 없는 B002 후보의 **주 대조 경로로 기술적으로 가능**하다. 공식 문서는 batch당 최대 100 queries를 허용하므로, 2,710건은 최대 **28개 순차 batch**(27×100 + 10)다. API 약관은 reasonable request rate를 요구하고 과부하·DB 갱신 때 지연·중단·rate-limit/block이 가능하다고 밝힌다. 따라서 **한 batch씩, 명시 threshold, 성공 응답 검산, 지수 backoff 재시도, 후보/판본 사람 대조**로 운용한다.

수치 rate는 공식 문서가 제공하지 않는다. 아래의 `≤1 POST/s`, 동시성 1, 429/5xx/timeout 뒤 backoff는 약관의 “reasonable rate”를 구현하는 **조사자 권고**이지 zbMATH가 공표한 한도가 아니다.

## 1. 공식 계약

공식 [zbMATH Citation Matcher API 문서](https://zbmath.org/static/citation-matching-api.pdf)는 base URL을 `https://zbmath.org/citationmatching/`로, 단건 endpoint를 `GET match`, batch endpoint를 `POST match`로 정한다.

- POST body는 UTF-8 JSON `{"queries":[…]}`다.
- 한 batch에는 최대 100 query를 넣는다.
- query에는 raw citation `q` 또는 구조화 필드 `t`(title), `a`/`a[]`(여러 author), `j`, `v`, `i`, `p`, `y`, `f`, `n`, `m`을 넣을 수 있다.
- response는 `{"results":[result_array_0,…]}`이며 각 result에는 `score`, `probability`, `zbl_id`, `title`, `authors`, `source`, `pagination`, `year`가 있다. 문서는 결과가 score 내림차순이라고 설명한다.

공식 [FAQ](https://zbmath.org/frequently-asked-questions/)는 raw reference string도 matcher에 넣을 수 있고 fuzzy search가 최소 유사도 이상인 가까운 entry를 돌려준다고 설명한다. 공식 [API Terms](https://static.zbmath.org/legal/api-terms-and-conditions.html)는 API 자료가 완전성·정확성·시의성을 보증하지 않으며, traffic-control best practice를 지키지 않으면 rate-limit/block할 수 있고 과부하·갱신 중에는 재시도가 필요할 수 있다고 정한다.

## 2. 실제 POST batch 계약 실측

### 성공 batch

2026-09-04 KST에 다음 3-query POST를 실행했다.

```json
{
  "queries": [
    {"t":"Shape theory","a":["Cordier","Porter"],"y":"1989","n":3},
    {"t":"Parameterized complexity theory","a":["Flum","Grohe"],"y":"2006","n":3},
    {"q":"Definitely non-existent title 9qz","n":3}
  ]
}
```

HTTP 200, `application/json`, `results` 배열 길이 3을 받았다. `results[i]`는 입력 `queries[i]`와 같은 순서로 대응하며, response 자체에는 input ID가 없다. 따라서 대량 실행자는 batch 번호·입력 배열 인덱스·원 citation을 별도 보존해야 한다.

이 batch에서 존재하지 않는 문구에도 score 0의 후보가 반환됐다. 이어 `m=5`을 각 query에 명시한 3-query batch를 실행하면 Shape theory에는 2개(점수 약 13.05, 13.03)가 남고, Parameterized complexity theory와 존재하지 않는 문구에는 각각 빈 배열이 돌아왔다. 즉 **비어 있지 않은 response는 match가 아니며**, `m`을 명시해도 제목·저자·연도·판본을 다시 대조해야 한다.

### 실패와 batch 원자성

유효 query와 `a:42`(list여야 하나 scalar)을 같은 POST body에 넣으면 HTTP 422, `body.queries[1].a` type error가 반환되고 `results`는 전혀 없다. `queries` 필드가 없는 body도 HTTP 422다. 이 실측은 validation failure가 개별 result를 섞어 돌려주지 않는 **batch-level failure**임을 보인다.

따라서 client commit 규칙은 다음과 같다.

1. HTTP 200이고 `results.length == queries.length`일 때만 batch를 처리한다.
2. 422/429/5xx/timeout이면 그 batch 전체를 미처리로 남기고 원 payload 그대로 재시도한다.
3. 빈 result array는 `no_match_under_explicit_threshold`, 422 등은 `request_failed`, 결과가 있어도 서지 충돌이면 `candidate_rejected_after_review`로 구분한다.

## 3. 대표 10건 실측

### 표집

DOI 없는 후보의 형태는 book 2,442, article 106, incollection 152, inproceedings 8, proceedings 2다. 재현 가능한 표집으로 book은 MR ID 오름차순 6분위 위치, 나머지 네 유형은 각 유형 MR ID 오름차순 중앙 위치를 택했다. 이는 형식·시대·저자/편집자 입력의 실패 모드를 보는 표집이며, 전체 match rate의 무작위 추정치가 아니다.

아래 10건은 `t`, 저자/편집자 성, `y`, `n=3`을 POST했으며, 사람이 title·author/editor·year를 B002 원문과 다시 대조해 accepted 여부를 판정했다. `Zbl`은 matcher response의 식별자다.

| # | B002 MR · 유형 · year · provenance | 입력 title / creator | 상위 관련 response와 사람 대조 | 결과 |
|---:|---|---|---|---|
| 1 | `MR1000348`; book; 1989; 18#73 | *Shape theory*; Cordier, Porter | `Zbl 0663.18001`, 1989, *Shape theory: categorical methods of approximation*, 두 저자, score 13.03. 더 높은 2008 Dover reprint도 함께 반환. | `accepted_candidate`; year가 맞는 1989 판본을 선택, 2008 reprint와 자동 병합하지 않음. |
| 2 | `MR1451876`; book; 1997; 26#9 | *Convex analysis*; Rockafellar | `Zbl 0932.90001`, 1997, 동명·동저자, score 14.85. | `accepted_candidate` |
| 3 | `MR2238686`; book; 2006; 68#11 | *Parameterized complexity theory*; Flum, Grohe | 반환 3건은 2002–04의 다른 parameterized-complexity 논문이고 score 0. explicit `m=5` batch에서는 빈 배열. | `no_match_under_explicit_threshold`; 색인 부재·판본 차이·matcher 누락 중 무엇인지는 미확정. |
| 4 | `MR3752129`; book; 2018; 82#36 | *Statistical mechanics of lattice systems*; Friedli, Velenik | `Zbl 1407.82001`, 2018, 부제 추가·두 저자, score 14.82. | `accepted_candidate` |
| 5 | `MR638719`; book; 1981; 12#14 | *Lectures on the theory of algebraic numbers*; Hecke | `Zbl 0504.12001`, 1981, 번역자 부가 표기·저자, score 14.78. | `accepted_candidate`; 번역/판본 관계는 후속 대조. |
| 6 | `MR999922`; book; 1989; 43#16 | *Analysis on semigroups*; Berglund, Junghenn, Milnes | `Zbl 0727.22001`, 1989, 부제 추가·세 저자, score 13.23. | `accepted_candidate` |
| 7 | `MR441835`; article; 1976; 01#16 | *Classical theorems on quadratic residues*; Berndt | `Zbl 0337.10031`, 1976, 동명·동저자, score 6.31/probability 0.565. | `accepted_candidate`; 낮은 score라도 서지 대조가 맞음을 보이는 사례. |
| 8 | `MR1826251`; incollection; 2000; 53#94 | *Spaces and questions*; Gromov | `Zbl 1006.53035`, 2000, 동명·동저자, score 3.91/probability 0.446. | `accepted_candidate`; default threshold에만 의존하면 놓칠 수 있는 사례. |
| 9 | `MR1648040`; inproceedings; 1998; 86#38 | *Mathematical problems in geophysical wave propagation*; Papanicolaou | 상위는 1998 edited volume *Wave propagation in complex media*; 두 번째 `Zbl 1125.86314`가 동명·동저자, score 10.60. | `accepted_candidate`; 첫 결과만 채택하면 오탐이 되는 사례. |
| 10 | `MR1427985`; proceedings; 1997; 86#51 | *Inverse problems in geophysical applications*; editors Engl, Louis, Rundell | `Zbl 0857.00035`, 1997, 동명 proceedings·세 편집자, score 5.86. | `accepted_candidate` |

실측 10건에서 9건은 사람 대조로 후보가 맞았고 1건은 explicit threshold 아래 no-match였다. 이 비율은 전수 정답률로 일반화하지 않는다. 특히 sample 1·5는 재판/번역 신호, sample 9는 top-1 오탐 위험, sample 7·8·10은 낮은 score의 참 양성 위험을 동시에 보인다.

## 4. Document search와 citation matcher의 역할 분리

document search는 `https://api.zbmath.org/v1/document/_search`에서 `ti:`, `au:`, `py:`를 결합해 candidate를 재조사하는 데 적합하다. 이 조사에서 `ti:"Shape theory" & au:Cordier & py:1989`은 HTTP 502, 더 단순한 `ti:Shape & au:Cordier & py:1989`은 client timeout, `ti:Convex & au:Rockafellar & py:1997`은 HTTP 502을 실제로 반환했다. 이 세 실패는 문법상 no-result가 아니라 transport/service failure다.

따라서 2,710 DOI 없는 후보의 첫 pass에는 title·author·year를 한 body에 보존하는 citation matcher POST를 권장한다. document search는 다음에만 쓴다.

- matcher가 빈 배열이지만 표준화 제목/저자 변형을 별도 점검할 때,
- matcher가 여러 후보를 돌려주고 edition·container·ISBN을 더 비교할 때,
- 입력 검증 오류나 batch failure를 좁혀 재현할 때.

## 5. 현실적 전수 계획과 한계

| 단계 | 실행 단위 | 성공 조건 | 실패·오탐 방지 |
|---|---|---|---|
| 준비 | 2,710 input에 B002 MR, 원문 title, creator role/list, year, provenance를 붙임 | 28개 100개 이하 payload 생성 | 저자 없는 편집서에는 `ed` 또는 raw `q`를 쓰고 역할을 보존 |
| matcher | POST 1 batch씩, `n=3`, 명시 `m` | HTTP 200 및 배열 길이 일치 | 동시성 1, 권고 `≤1 POST/s`; 429/5xx/timeout은 전체 batch backoff 재시도 |
| 서지 심사 | result별 title·creator·year·type·source 비교 | exact/판본 관계/충돌을 별도 처분 | top-1, score, probability만으로 채택 금지 |
| 보완 | 필요한 항목만 document search/공식 publisher record | 판본·ISBN·container 확인 | empty result, request failure, unindexed work를 구별 |

공식 문서는 maximum 100 queries/batch를 주지만 일일 quota나 수치 RPS를 공표하지 않는다. 후속 실행은 사용자가 요청한 공개 자료원 조사 범위 안에서 28개 batch를 동시성 1·3초 간격으로 완료했고, 각 batch의 request/response hash·시각·status·result count를 남겼다. 결과는 별도 전수 감사에 기록한다.

## 판정

**가능:** citation matcher POST의 입력/출력 계약과 10-query batch, explicit threshold, validation failure의 batch-level 동작을 실제로 확인했다. 2,710건은 공식 최대치에 맞춰 28 batch로 분할할 수 있다.

**불확정:** 전수 precision/recall과 matcher가 비색인 문헌·판본 변형을 어떻게 분리하는지는 전수 응답만으로 확정되지 않는다. 실제 2,710건 결과도 문자열 분류를 서지 동일성으로 승격하지 않고 사람 대조 대기열로 둔다.
