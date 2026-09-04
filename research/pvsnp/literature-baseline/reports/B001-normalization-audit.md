# B001 정규화·B002 교차 연결 검사

검사일: 2026-09-04 KST

판정: **통과.** B001의 20개 원시 export, 20,746개 출현을 전부 파싱해 같은 자료원 안정 ID 기준 20,429개 후보로 모았고, B002와 함께 DOI·서지 fingerprint 관계 후보 2,378묶음을 만들었다. 원시 `intake/`는 수정하지 않았다.

## 1. 전수성과 재현성

[`../catalog/B001-normalization-contract.md`](../catalog/B001-normalization-contract.md)에 따라 [`../scripts/build_b001_catalog.py`](../scripts/build_b001_catalog.py)를 검사 우선으로 작성했다. ACM·IEEE BibTeX 2,239건, MathSciNet BibTeX 500건, RIS 2,348건, Scopus CSV 15,659건으로 총 20,746건이다. 자료원별 합계는 다음과 같다.

| 자료원 | 원시 출현 | source-ID 후보 | 반복 출현 |
|---|---:|---:|---:|
| ACM DL | 2,175 | 2,079 | 96 |
| IEEE Xplore | 64 | 64 | 0 |
| MathSciNet | 500 | 469 | 31 |
| PQDT | 218 | 210 | 8 |
| Scopus | 15,659 | 15,498 | 161 |
| Web of Science | 2,130 | 2,109 | 21 |
| **합계** | **20,746** | **20,429** | **317** |

manifest의 20개 경로·바이트·SHA-256·레코드 수를 실제 파일과 다시 비교했고 불일치는 0이다. 후보의 `occurrence_count` 합도 20,746이며 모든 provenance는 source·query ID·검색 내 rank·원시 파일과 record hash를 가진다. 생성기를 같은 입력으로 다시 실행했을 때 후보·관계·review queue·manifest 파일의 SHA-256이 모두 같았다. 정규화기·원시 review locator 검사는 14건이고 direct-title·direct-axis 결정 결박 검사는 각각 2건이다.

ACM A02의 한 초록에는 중괄호가 하나 더 있고 IEEE entry는 `},@INPROCEEDINGS`처럼 개행 없이 이어진다. 파서는 초록의 중괄호 균형을 서지 entry 경계로 쓰지 않고 record/field 시작을 사용해 두 형식을 모두 전수 처리했다. 초록·참고문헌 전문은 추적 catalog에 복제하지 않았다.

## 2. 후보 분포와 예외

20,429개 source-ID 후보 중 DOI가 있는 후보는 17,666, 초록이 있는 후보는 19,303, 참고문헌이 있는 후보는 16,411이다. 출판형태의 큰 층은 article 11,468, Scopus `conference paper` 5,848, BibTeX `inproceedings` 1,040, review 690, book chapter 475, book 306, thesis 210이다. source가 준 형식명을 보존했으므로 conference paper와 inproceedings를 자동 통합하지 않았다.

예외는 다음처럼 원 record를 유지한다.

- 제목 누락 1건: Scopus EID `2-s2.0-34250131297`. DOI·저자·venue는 있으나 export title이 비어 있다.
- 연도 누락 1건: `MR978379`. MathSciNet export의 year가 비어 있다.
- creator 누락 96건: 주로 conference review·proceedings·ACM 집합/수록 record다. 저자를 창작하지 않는다.
- 안정 source ID 누락 0건, manifest 불일치 0건, 관계가 가리키는 미존재 후보 0건이다.

## 3. B002와의 연결

B001 MathSciNet 후보 469개 중 108개 MR은 B002의 같은 MR 기본키와 정확히 겹친다. 이는 같은 자료원의 직접 식별자이므로 두 저작으로 세지 않는다. B001 20,429개와 B002 5,472개의 안전한 기본키 합집합은 **25,793개**다. 이 수는 다른 자료원 record를 DOI만으로 합친 work 수가 아니라, 명백한 같은-source ID 중복만 제거한 후보 수다.

다른 자료원끼리는 다음 관계만 만들었다.

| 관계 후보 | 묶음 | B002 member가 있는 묶음 | B001 내부 묶음 |
|---|---:|---:|---:|
| `same_doi_candidate` | 1,892 | 3 | 1,889 |
| `same_bibliographic_fingerprint_candidate` | 486 | 4 | 482 |
| **합계** | **2,378** | **7** | **2,371** |

DOI 묶음은 2-member 1,759개, 3-member 130개, 4-member 3개다. 네 자료원에서 같은 DOI로 잡힌 예에는 Razborov–Rudich *Natural Proofs*가 있다. 이 일치는 강한 연결 신호지만, B002 Crossref 감사에서 실제 wrong/component/set DOI를 발견했으므로 모두 `unverified_candidate`로 둔다. fingerprint도 정규화 제목·creator 전체·연도가 같은 경우만 만들며 자동 병합하지 않는다.

B001 감사의 과거 **18,039개 작업**은 DOI 또는 제목·연도를 즉시 묶은 1차 추정이었다. 현재 20,429는 원 record를 잃지 않는 안전한 source-ID 후보 수이며 두 값은 서로 다른 판정 단위다. 판본·학회판·저널판·번역을 검토하기 전에는 18,039를 고유 저작 확정치로 쓰지 않는다.

## 4. 남은 선별

B001은 직접 P/NP 검색뿐 아니라 구두점이 무너진 `P = NP`와 넓은 `computational complexity` 검색의 잡음을 의도적으로 포함한다. 따라서 20,429개를 모두 핵심 문헌으로 채택하지 않는다. 다음 단계는 query별 제목·초록·venue를 이용해 직접·인접·먼 분야 연결·동음이의 잡음으로 분류하고, B002 핵심 후보 및 공개 TCS 씨앗과 relation group을 판본별로 처분하는 일이다.

초록·keyword 전문을 catalog에 복제하지 않고 검색 신호의 **존재 위치만** 계산한 1차 판독 대기열은 다음과 같다. 이는 채택 점수나 관련성 확정이 아니다.

| 검토 경로 | 후보 수 |
|---|---:|
| 제목·초록·keyword에 직접 P-vs-NP 표현 | 2,514 |
| proof/circuit/natural-proofs/relativization 등 명시 축 | 8,272 |
| 일반 `computational complexity` 표현 | 5,257 |
| NP-hardness·polynomial-time·lower-bound 등 일반 경계 신호 | 546 |
| M04·M05의 MSC 대조 seed | 200 |
| export의 제목·초록·keyword에는 명시 신호 없음 | 3,640 |

마지막 3,640건은 폐기나 무관 판정이 아니다. ACM full-text/참고문헌 hit, 인용 관계, 분야 control record일 수 있으므로 원 query와 relation을 보고 처분한다. 반대로 직접 표현이 있는 2,514건도 P/NP 해결 주장이나 핵심성을 자동 승인하지 않는다.

이 가운데 **제목 자체**에 직접 표현이 있는 165개 source record는 107개 cluster로 전수 검토했다. 권위/역사 9, 표준 연구 11, 조건부 결과 17, 대체 모형·상대화 35, 교육·논평 20, 해결 주장 8, 비-TCS 오탐 3, full-text 필요 4다. source queue·처분 집합의 대칭차는 0이며 결과는 [`B001-direct-title-review.md`](B001-direct-title-review.md)에 있다.

제목 밖 직접 신호 2,349건 중 P/NP 문맥과 proof·circuit·relativization 등 named axis가 함께 있는 186개 source record도 156개 cluster로 전수 판독했다. core method 26, 표준 하위축 46, 조건부 문제 결과 24, 응용/먼 교량 27, 대체 모형 18, survey/commentary 8, full-text 필요 7이다([`B001-direct-axis-review.md`](B001-direct-axis-review.md)). 나머지 2,163건은 일반 계산복잡도·문제별 조건부 결과·인용 문맥 대기열로 남긴다.

정확한 계수·입력·출력 해시는 [`../manifests/B001-normalized.json`](../manifests/B001-normalized.json)에, 후보와 관계는 `catalog/B001-candidates.jsonl`·`catalog/B001-relations.jsonl`에 있다.
