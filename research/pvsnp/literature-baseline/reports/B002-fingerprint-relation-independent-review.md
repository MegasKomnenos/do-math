# B002 fingerprint 관계 처분 독립 검증

검토일: 2026-09-04 KST  
판정: **PASS — 10행 재검증, 잔여 결함 0건.**

## 검사 방법과 경계

`catalog/B002-fingerprint-relation-decisions.jsonl`의 10행을 `B002-relations.jsonl`과 `B002-candidates.jsonl`에 다시 대조했다. 모든 relation은 `same_bibliographic_fingerprint_candidate`였고, `relation_id`와 members는 **10/10 일치**했다. 이어 각 member의 원문 title, creator, year, edition, volume, series, publisher, pages, ISBN, NOTE를 확인하고, 제공된 공개 출판사·서지 record를 직접 열었다.

외부 record는 서지·판본의 확인 범위일 뿐 원문 전체나 출판 계약의 증거가 아니다. 공식 record가 없는 행은 B002 NOTE/필드가 직접 말하는 범위까지만 인정했다. publisher page의 403·timeout은 결과 없음으로 바꾸지 않았다.

## 행별 판정

| relation_id · members | 원자료·공개 대조 | 판정 |
|---|---|---|
| `B002-REL-6ca441009be676af359f` · MR997295, MR1345386 | Arnol'd, *Mathematical methods of classical mechanics*, GTM 60, 같은 ISBN. MR1345386 NOTE는 “Corrected reprint of the second (1989) edition”을 명시하고, 앞쪽 쪽수만 `xvi+508` 대 `xvi+516`이다. [Springer record](https://link.springer.com/book/10.1007/978-1-4757-2063-1)는 같은 제목·저자·GTM 60·1989 second edition을 확인한다. | `same_work_corrected_reprint`, `confirmed_from_b002_note_and_public_record`: **통과**. |
| `B002-REL-440275a2fabc060b635a` · MR2284176, MR3443454 | Bhatia, *Positive definite matrices*, 같은 series·저작연도 2007, hardback ISBN `978-0-691-12918-1` 대 paperback ISBN `978-0-691-16825-8`. [Princeton 2016 catalog](https://assets.press.princeton.edu/catalogs/math16.pdf)은 후자를 2015 paperback으로 명시한다. | `same_work_paperback_reissue`, `confirmed_from_isbn_and_publisher_catalog`: **통과**. B002의 2007 year는 원저작년으로 남아 있고 2015 발행년과 혼동하지 않았다. |
| `B002-REL-99478980e31304ce2e05` · MR886476, MR2975988 | Brieskorn–Knörrer, *Plane algebraic curves*, 1986·같은 번역자. MR2975988 NOTE가 “2012 reprint of the 1986 edition”을 직접 명시하며 Modern Birkhäuser Classics/새 ISBN만 다르다. [Springer record](https://link.springer.com/book/10.1007/978-3-0348-5097-1)도 저자·원 저작연도·Birkhäuser record를 제공한다. | `same_work_reissue`: **통과**. |
| `B002-REL-98dec534e176fc054b8f` · MR769102, MR921235 | Cao–Kim–Roush, *Incline algebra and applications*: title·creator·1984·publisher·series·ISBN `0-85312-765-4`가 같고, `xiii+165` 대 `xiv+165`, MSC/reviewer만 다르다. 이 검사에서도 두 MR이 왜 분리됐는지 설명하는 공식 record를 찾지 못했다. | `probable_duplicate_catalog_records_unresolved`, `unresolved`: **통과**. 같은 ISBN이더라도 두 MR을 병합하거나 원인을 창작하지 않은 것이 정확한 경계다. |
| `B002-REL-c1dc478c743aa53b781b` · MR1634015, MR3025306 | Facchini, *Module theory*, 1998, 같은 subtitle·쪽수. MR3025306 NOTE가 “2012 reprint of the 1998 original [MR1634015]”라고 직접 쓴다. [Springer record](https://link.springer.com/book/10.1007/978-3-0348-0303-8)도 Modern Birkhäuser Classics·2012 eBook/softcover와 1998 copyright를 확인한다. | `same_work_reissue`, `confirmed_from_b002_note`: **통과**. NOTE가 직접 근거이므로 DOI 부재는 결함이 아니다. |
| `B002-REL-791457a178df8c07914f` · MR504338, MR509213 | Grätzer, *General lattice theory*, 1978, 같은 `xiii+381`이지만 Birkhäuser Band 52 / ISBN `3-7643-0813-3`와 Academic Press Pure and Applied Mathematics 75 / ISBN `0-12-295750-4`로 갈린다. [Springer DOI record](https://link.springer.com/book/10.1007/978-3-0348-7633-9)와 Crossref는 1978 Birkhäuser record를 확인하지만 Academic Press imprint나 두 record의 계약·동일 publication 관계는 명시하지 않는다. 현재 결정은 그 한계를 반영해 `probable_parallel_imprint_unresolved`, `unresolved`로 수리됐다. | **수리 재검증 통과.** 이전 `same_publication_parallel_imprint`/`confirmed_from_bibliographic_identity`는 과도했으나, 현 처분은 병행 imprint를 가능성으로만 남기고 별도 동시판·territorial edition을 배제하거나 병합하지 않는다. |
| `B002-REL-87a8b3cfc4b5d6986770` · MR2078728, MR2098410 | Klein, *Elementary mathematics from an advanced standpoint*, 같은 2004 Dover reprint이나 NOTE가 각각 *Geometry*와 *Arithmetic, algebra, analysis*, 원 번역연도 1949/1932, 214/274쪽, ISBN을 명시한다. | `same_series_distinct_parts`, `confirmed_from_b002_notes`: **통과**. 같은 일반 제목은 병합 근거가 아니다. |
| `B002-REL-39868880344716644037` · MR465760, MR465761 | Kummer, *Collected papers* I/II: 원 NOTE가 I=number theory, II=function theory·geometry를 구별하고, 쪽수도 955/877이다. [Springer I](https://link.springer.com/book/9783662488324)와 [Springer II](https://link.springer.com/book/9783662633458)는 title·subtitle·author·editor·각 volume을 독립적으로 확인한다. | `same_work_distinct_volumes`, `confirmed_from_b002_notes_and_public_records`: **통과**. |
| `B002-REL-9349ed8608313cbb4835` · MR1395371, MR1477155 | Nathanson, *Additive number theory*, GTM 164 *The classical bases* 대 GTM 165 *Inverse problems and the geometry of sumsets*, 다른 ISBN·342/293쪽이다. [Springer GTM 164 record](https://link.springer.com/book/10.1007/978-1-4757-3845-2)는 첫 권의 title·GTM 164·1996을 확인하며, B002 NOTE가 둘째 권을 독립 volume으로 식별한다. | `same_series_distinct_volumes`: **통과**. 링크는 첫 권을 확인할 뿐 둘째 권의 모든 외부 판본 이력을 증명하지 않는다는 한계는 남는다. |
| `B002-REL-bdbc66c14856d94f0ec4` · MR1347691, MR1347692 | Zeidler, *Applied functional analysis*: AMS 108 *Applications to mathematical physics* 대 AMS 109 *Main principles and their applications*, 서로 다른 ISBN·479/404쪽. [Springer AMS 108](https://link.springer.com/book/10.1007/978-1-4612-0815-0) 및 [AMS 109](https://link.springer.com/book/10.1007/978-1-4612-0821-1)은 title/subtitle·volume을 구별한다. | `same_series_distinct_volumes`, `confirmed_from_b002_notes_and_public_records`: **통과**. |

## 결론

관계 식별자와 members의 기계적 일치는 재검증에서도 10/10이다. MR769102/MR921235는 외부 설명이 없다는 사실을 중복 확정으로 바꾸지 않아 적절했다. DOI가 없는 reprint·distinct-part 처분도 B002 NOTE가 직접 재발행·부제·volume을 말하는 범위에서는 과도하지 않았다.

이전 검사에서 MR504338/MR509213의 `same_publication_parallel_imprint`/확정 confidence를 결함으로 지적했다. 현 결정은 정확히 `probable_parallel_imprint_unresolved`와 `unresolved`로 낮췄고, basis도 두 publisher의 관계를 직접 확인하지 못했으며 병합하지 않는다고 한정한다. 이는 확인한 1978 Birkhäuser record와 확인하지 못한 Academic Press 관계를 구분한다. 따라서 이전 결함은 해소됐고, 이 10행 묶음의 현행 판정은 **PASS, 잔여 결함 0건**이다.
