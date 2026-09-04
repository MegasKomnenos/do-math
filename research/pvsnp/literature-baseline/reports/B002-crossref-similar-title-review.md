# B002 Crossref similar-title 검토

검토일: 2026-09-04 KST  
상태: **49/49 상세 처분 완료; 미확정 1건.**

대상은 현행 `catalog/B002-crossref-title-review.jsonl`의 `classification=similar_title` 49 DOI–MR 행이다. 제목 유사도는 발견 신호로만 사용하고, 후보 BibTeX와 Crossref 원시 응답의 저자·연도·ISBN·container·권·판·redirect를 대조했다. PDF·인증·크리덴셜은 사용하지 않았다.

상세 행은 다음 세 보고서에 있다.

- [`B002-crossref-similar-title-review-A.md`](B002-crossref-similar-title-review-A.md): 16행
- [`B002-crossref-similar-title-review-B.md`](B002-crossref-similar-title-review-B.md): 16행
- [`B002-crossref-similar-title-review-C.md`](B002-crossref-similar-title-review-C.md): 16행

나머지 한 행은 아래의 권 충돌이다. 세 상세 보고서 48행과 이 행의 DOI–MR 집합을 source 49행과 비교한 결과 누락·추가·중복의 대칭차는 0이다.

## 처분 집계

| 처분 | 수 |
|---|---:|
| `same_work_title_variant` | 41 |
| `same_work_reissue_or_edition` | 3 |
| `component_of_candidate_work` | 2 |
| `related_but_distinct_work` | 1 |
| `different_volume_or_part_identifier_conflict` | 1 |
| `unresolved` | 1 |
| **합계** | **49** |

## 권 충돌과 미확정

- [`10.1090/gsm/117`](https://doi.org/10.1090/gsm/117)은 Crossref에서 Terence Tao의 *An Epsilon of Room, I: Real Analysis*를 가리키지만 B002 `MR2780010`은 *An epsilon of room, II*다. 제목 유사도 0.763636은 권 차이를 없애지 못하므로 `different_volume_or_part_identifier_conflict`로 처분했다.
- [`10.1007/978-0-387-74315-8`](https://doi.org/10.1007/978-0-387-74315-8)은 Crossref 제목이 *Robot Dynamics Algorithms*, B002 `MR2676219`은 Roy Featherstone의 *Rigid Body Dynamics Algorithms*다. 저자는 같지만 현재 대조만으로 제목 metadata 오류와 다른 판을 구별하지 못해 `unresolved`로 유지했다.

## 판정 경계

41개 title variant는 TeX/Unicode, 하이픈, 관사, 단복수, 수식 표기의 차이였고 같은 DOI의 저자·연도·출판 맥락이 일치했다. 재발행·component·관련 별도 작업은 원 MR 레코드를 합치지 않는다. 위 처분은 DOI 배정과 서지 관계만 다루며 같은 내용, 수학적 타당성, 핵심층 채택을 자동 판정하지 않는다.
