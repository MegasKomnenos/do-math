# B002 동일 DOI 관계 감사

검사일: 2026-09-04 KST

판정: **14개 묶음 전건 처분 완료. 서로 다른 MR 레코드는 병합하지 않는다.**

## 범위와 판정 방법

`catalog/B002-relations.jsonl`의 `same_doi_candidate` 14묶음을 전부 검사했다. 각 MR 레코드의 제목·저자·연도·판본·권·series·쪽수·ISBN·출판사를 다시 읽고, Crossref 단건 응답과 DOI가 가리키는 공식 출판사 페이지를 대조했다.

DOI 일치는 같은 지적 작업을 시사할 수 있지만 같은 판본을 보장하지 않았다. 실제 14묶음에는 새 판, 재발행, 공동 출판사의 병행 레코드, 다권본의 세트 식별자와 잘못 붙은 다른 권의 DOI가 모두 있었다. 판정은 [`../catalog/B002-doi-relation-decisions.jsonl`](../catalog/B002-doi-relation-decisions.jsonl)에 기계 판독형으로 보존했다.

## 결과

| DOI | MR 레코드 | 처분 | 근거 요지 |
|---|---|---|---|
| `10.1007/978-1-4612-0985-0` | `MR1033497`, `MR1033498` | `identifier_conflict_between_volumes` | [Springer II/A](https://link.springer.com/book/10.1007/978-1-4612-0985-0)와 [II/B](https://link.springer.com/book/10.1007/978-1-4612-0981-2)는 별도 DOI다. B002의 II/B DOI가 충돌한다. |
| `10.1007/978-3-0348-5097-1` | `MR886476`, `MR2975988` | `same_work_reissue` | [공식 페이지](https://link.springer.com/book/10.1007/978-3-0348-5097-1)는 같은 1986 저작의 후속 softcover/eBook 발행을 연결한다. |
| `10.1007/978-3-642-04295-9` | `MR1460488`, `MR2841334` | `same_work_reissue` | [공식 페이지](https://link.springer.com/book/10.1007/978-3-642-04295-9)는 1997 hardcover와 2009 softcover/eBook을 구별한다. |
| `10.1007/978-3-642-18808-4` | `MR2095471`, `MR2095472` | `identifier_conflict_between_volumes` | Springer는 [Volume I](https://link.springer.com/book/10.1007/978-3-642-18808-4)과 [Volume II](https://link.springer.com/book/10.1007/978-3-642-18810-7)에 다른 DOI를 준다. |
| `10.1007/978-3-642-33911-0` | `MR3051754`, `MR3051755` | `identifier_conflict_between_volumes` | [공식 DOI 페이지](https://link.springer.com/book/10.1007/978-3-642-33911-0)는 Volume I이다. B002의 Volume II가 같은 DOI를 가지며 2013 Volume II의 정확한 대체 DOI는 아직 미확정이다. |
| `10.1007/978-3-642-61497-2` | `MR1065136`, `MR1996773` | `same_work_reissue` | 같은 Hörmander Volume I의 1990 second edition과 [2003 Classics 재발행](https://link.springer.com/book/10.1007/978-3-642-61497-2)이다. |
| `10.1007/978-3-642-61631-0` | `MR867687`, `MR881386` | `same_publication_parallel_imprint` | 제목·번역자·연도·쪽수는 같고 Akademie-Verlag와 [Springer 영어판](https://link.springer.com/book/9783540159674)의 ISBN·imprint가 다르다. 계약상 공동 출판 여부는 확정하지 않았다. |
| `10.1007/978-3-642-96750-4` | `MR705278`, `MR717035` | `identifier_conflict_between_volumes` | DOI는 [Volume I](https://link.springer.com/book/10.1007/978-3-642-96750-4)이다. `MR705278`은 Volume II이며 후속 [Volume II 재발행](https://link.springer.com/book/10.1007/b138375)도 별도 DOI를 쓴다. |
| `10.1007/978-3-662-02500-0` | `MR873945`, `MR881220` | `same_publication_parallel_imprint` | VEB와 Springer 레코드는 제목·부제·연도·쪽수가 같으며 [공식 페이지](https://link.springer.com/book/9783662025024)는 공동 출판 맥락을 보존한다. |
| `10.1017/cbo9780511618123` | `MR1648555`, `MR1648559` | `identifier_conflict_between_volumes` | Cambridge는 [Volume 2](https://www.cambridge.org/core/books/string-theory/2D456468D20AA8A9CE10CEB08B95B9DC)와 [Volume 1](https://www.cambridge.org/core/books/string-theory/30409AF2BDE27D53E275FDA395AB667A)에 다른 DOI를 준다. |
| `10.1017/cbo9781139644174` | `MR1410064`, `MR1411911` | `identifier_conflict_between_volumes` | Cambridge는 [Volume 2](https://www.cambridge.org/core/books/quantum-theory-of-fields/0E0C89894938BE38EE0BCCDB1BC857E5)와 [Volume 1](https://www.cambridge.org/core/books/quantum-theory-of-fields/22986119910BF6A2EFE42684801A3BDF)에 다른 DOI를 준다. |
| `10.1090/gsm/014` | `MR1415616`, `MR1817225` | `same_work_new_edition` | *Analysis*의 1997 초판과 [2001 제2판](https://bookstore.ams.org/gsm-14/)이다. |
| `10.1090/gsm/019` | `MR1625845`, `MR2597943` | `same_work_new_edition` | *Partial Differential Equations*의 1998 초판과 [2010 제2판](https://bookstore.ams.org/gsm-19/)이다. |
| `10.1515/9783110218114` | `MR2985554`, `MR2985654` | `same_work_distinct_volumes_shared_set_identifier` | Volume 1·2는 쪽수가 이어지고 부제가 다르며 같은 세트 ISBN과 [De Gruyter 전자 DOI](https://www.degruyterbrill.com/document/doi/10.1515/9783110218114/html)를 공유한다. |

처분 분포는 권간 식별자 충돌 6, 같은 저작 재발행 3, 병행 imprint 2, 새 판 2, 다권본 세트 식별자 1이다.

## 영향과 남은 일

- DOI 일치 14묶음을 자동 중복 병합하면 서로 다른 권 7쌍과 서로 다른 판본을 잃는다. 현재 후보 레코드 보존 정책을 유지한다.
- 식별자 충돌 6묶음은 MathSciNet의 DOI 필드를 후보 식별자로만 사용하고 공식 출판사 DOI를 판본 기록에 우선해야 한다.
- `MR3051755`의 2013 Volume II 정확한 전자 식별자는 공개 공식 페이지에서 추가 확인해야 한다. 이는 그 MR 레코드의 존재나 제목을 부정하지 않는다.
- DOI보다 약한 364개 제목·저작자 관계 후보는 이 감사의 완료 범위가 아니다. Crossref 전수 대조와 분야별 판독 결과를 이용해 같은 방식으로 순차 처분한다.
