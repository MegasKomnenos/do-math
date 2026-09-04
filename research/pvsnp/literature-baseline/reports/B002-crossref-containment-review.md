# B002 Crossref title-containment 전수 검토

대상은 `catalog/B002-crossref-title-review.jsonl`에서 `classification=title_containment`인 148 DOI다. DOI 오름차순으로 [A: 1–50](B002-crossref-containment-review-A.md), [B: 51–99](B002-crossref-containment-review-B.md), [C: 100–148](B002-crossref-containment-review-C.md)로 나누어 Crossref raw와 B002 후보의 저자·제목·연도·ISBN·container·권·판본을 대조했다.

## 결과

공유 DOI 때문에 148 DOI는 153 candidate link를 만든다. 모든 link를 처분했고 `unresolved`는 없다.

| 처분 | A | B | C | 합계 |
|---|---:|---:|---:|---:|
| `same_work_title_variant` | 27 | 33 | 29 | 89 |
| `same_work_reissue_or_edition` | 0 | 9 | 14 | 23 |
| `component_of_candidate_work` | 23 | 5 | 2 | 30 |
| `different_volume_or_part_identifier_conflict` | 2 | 2 | 1 | 5 |
| `wrong_identifier` | 0 | 2 | 1 | 3 |
| `shared_set_or_generic_title` | 0 | 0 | 2 | 2 |
| `related_but_distinct_work` | 0 | 0 | 1 | 1 |
| **candidate link 합계** | **52** | **51** | **50** | **153** |

## 해석

- 148건 모두 제목 포함 관계만으로 후보를 병합하지 않았다.
- 89건은 DOI·저자·ISBN 또는 출판 맥락이 맞고 부제·권 표기만 달랐다.
- 53건은 특정 권·chapter·재발행·판본 관계이므로 원 MR 레코드를 그대로 보존한다.
- 5건은 다른 권·부분의 DOI 충돌, 3건은 잘못 붙은 식별자다. 이 8건은 DOI를 자동 동일성 키로 쓰면 안 된다.
- 2건은 set/generic DOI이고 1건은 원 논문에 대한 comment이므로 서로 다른 저작을 병합하지 않는다.

세 slice의 source DOI 집합은 각각 50·49·49건이고 서로 겹치지 않으며 합계 148건이다. 이 보고서는 정규화 후보를 고치지 않고, 판정 근거와 보존 경계를 기록한다.
