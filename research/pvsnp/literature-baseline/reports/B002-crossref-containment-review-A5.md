# B002 Crossref title-containment 검토 A5

대상은 DOI 오름차순 source slice 41–50이다. 후보와 Crossref raw의 author·ISBN·year·container·volume를 대조했다. PDF·인증·크리덴셜은 사용하지 않았다.

| DOI · MR | 대조 필드 | 처분 |
|---|---|---|
| `10.1007/978-3-540-89394-3` · MR1890629 | Bourbaki 2002 *Lie Groups and Lie Algebras, Chapters 4–6*, ISBN `3-540-42650-7`; Crossref 같은 연도·ISBN의 포괄 title | `component_of_candidate_work` |
| `10.1007/978-3-642-01546-5` · MR2742588 | 2010 *Handbook of Geomathematics* vol.1–2, ISBN `…01545-8`; Crossref 2010 ISBN `…01545-8/01546-5`, 같은 set | `same_work_title_variant` |
| `10.1007/978-3-642-15202-3` · MR2731561 | Talagrand 2011 *Mean Field Models for Spin Glasses Vol. I*, vol.54; Crossref 같은 저자·연도·ISBN의 포괄 title | `component_of_candidate_work` |
| `10.1007/978-3-642-15708-0_4` · MR2762556 | Schlichting 2011 chapter; DOI suffix `_4`, Crossref book-chapter/LNM container, 같은 저자·ISBN | `component_of_candidate_work` |
| `10.1007/978-3-642-33911-0` · MR3051754 | Uchaikin 2013 *Fractional Derivatives … Vol. I*; 공식 Springer record가 이 DOI를 Volume I: *Background and Theory*에 배정 | `same_work_title_variant` |
| `10.1007/978-3-642-33911-0` · MR3051755 | Uchaikin 2013 *Fractional Derivatives … Vol. II*; 공식 DOI record는 Volume I이며 2013 Volume II의 대체 DOI는 미확정 | `different_volume_or_part_identifier_conflict` |
| `10.1007/978-3-642-54551-1` · MR3523845 | 2015 *Handbook of Geomathematics* vol.1–3, ISBN `…54550-4/54551-1/54552-8`; Crossref 같은 set ISBN | `same_work_title_variant` |
| `10.1007/978-3-642-58004-8` · MR1295030 | Dautray–Lions 1993 *… Vol. 6*, candidate ISBN `3-540-50206-8/66102-6`; Crossref record는 2000 포괄 title로 반환 | `component_of_candidate_work` |
| `10.1007/978-3-642-58090-1` · MR1156075 | Dautray–Lions 1992 *… Vol. 5*, candidate ISBN `3-540-50205-X/66101-8`; Crossref 2000 포괄 title | `component_of_candidate_work` |
| `10.1007/978-3-642-59126-6` · MR1469992 | 1997 *Handbook of Formal Languages Vol. 1*, ISBN `3-540-60420-0`; Crossref 같은 연도·set ISBN의 포괄 title | `component_of_candidate_work` |
| `10.1007/978-3-642-59315-4` · MR2013000 | Bourbaki 2004 *Functions of a Real Variable*, ISBN `3-540-65340-6`; Crossref 같은 저자·연도·ISBN, series title만 추가 | `same_work_title_variant` |

처분 합계: `component_of_candidate_work=6`, `same_work_title_variant=4`, `different_volume_or_part_identifier_conflict=1`, 합계=11 candidate links. source slice DOI 집합과 보고 DOI 집합 대칭차는 0, source DOI 수는 10이다.
