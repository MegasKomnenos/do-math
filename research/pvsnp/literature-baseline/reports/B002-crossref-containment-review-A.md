# B002 Crossref title-containment 검토 A

대상은 현행 title-review의 `title_containment` DOI 오름차순 1–50이다. source slice는 50 DOI, candidate link는 52개다. 세부 대조는 [A1](B002-crossref-containment-review-A1.md)·[A2](B002-crossref-containment-review-A2.md)·[A3](B002-crossref-containment-review-A3.md)·[A4](B002-crossref-containment-review-A4.md)·[A5](B002-crossref-containment-review-A5.md)에 보존한다.

Crossref raw의 title·type·저자·ISBN·container·year와 B002 후보의 원 필드를 대조했다. 문자열 포함만으로 동일 저작을 확정하지 않았고, 공유 DOI는 후보별로 판정했다. PDF·인증 DB·크리덴셜은 사용하지 않았다.

## 집계와 경계

| 처분 | candidate link 수 |
|---|---:|
| `same_work_title_variant` | 27 |
| `component_of_candidate_work` | 23 |
| `different_volume_or_part_identifier_conflict` | 2 |
| `unresolved` | 0 |
| **합계** | **52** |

각 10개 DOI인 A1–A5 보고의 DOI 집합 합집합은 source slice 1–50과 같고 중복이 없다. candidate link가 DOI보다 2개 많은 이유는 다음 공유 DOI 두 건이다.

- `10.1007/978-1-4612-0985-0`: 공식 Springer record는 II/A인 `MR1033497`에 대응한다. II/B인 `MR1033498`에는 별도 DOI `10.1007/978-1-4612-0981-2`가 있으므로 후자는 식별자 충돌이다.
- `10.1007/978-3-642-33911-0`: 공식 Springer record는 Volume I인 `MR3051754`에 대응한다. `MR3051755`의 2013 Volume II 식별자는 이 공개 record로 확정할 수 없어 후자는 식별자 충돌로 남긴다.

이 판정은 후보를 삭제하거나 다른 권·판본을 병합하지 않는다. 원 후보와 별도의 DOI 관계 결정은 `catalog/B002-doi-relation-decisions.jsonl`에 보존한다.
