# B002 Crossref relation 검토

조회일: 2026-09-04 KST  
상태: **relation이 비어 있지 않은 B002 DOI 18행을 처리함; 판본·정정 추적 기록이지 수학 내용·최신 권위·핵심층 판정이 아님.**

## 범위와 대조 방법

대상은 [`../catalog/B002-crossref.jsonl`](../catalog/B002-crossref.jsonl)에서 `crossref.relation`이 비어 있지 않은 행 전부다. 각 행에서 다음 세 실물을 대조했다.

1. `source.raw_path`의 원시 Crossref envelope 안 `response_text.message.relation`과 `updated-by`.
2. 같은 source DOI의 현재 [Crossref Works 단건 endpoint](https://api.crossref.org/works/) 응답.
3. Crossref `resource.primary.URL` 및 DOI resolver가 가리키는 공식 출판사·운영기관 record.

원시 envelope는 모두 HTTP 200으로 저장되어 있었다. 현재 source DOI 단건도 18/18이 HTTP 200이었고, 원시 relation과 현재 relation의 구조 비교는 18/18 일치했다. `asserted-by`는 Crossref deposit의 관계 주장 주체이지 독립 검증이나 수학적 판단이 아니다.

relation target은 DOI 20개와 arXiv 식별자 2개(버전 표기와 비버전 표기)를 포함한다. target DOI 20개 중 Crossref 단건은 19개가 HTTP 200이었다. `10.48550/arXiv.2306.00425`만 Crossref 단건 HTTP 404였으나, DOI resolver와 [arXiv 원 레코드](https://arxiv.org/abs/2306.00425)는 HTTP 200이었다. 이는 **target Crossref 검색 실패 1건**이며 relation 부재가 아니다.

## 관계 종류 집계

| 종류 | relation이 있는 source DOI 수 | relation assertion 수 | 비고 |
|---|---:|---:|---|
| `correction` | 4 | 4 | target은 correction/erratum record |
| `is-translation-of` | 2 | 3 | 한 source는 동일 DOI를 `subject`와 `object` 양쪽으로 주장 |
| `new_version` | 1 | 1 | 후속 버전 target |
| `is-identical-to` | 10 | 12 | 두 source가 각각 DOI target 둘을 가짐 |
| `has-preprint` | 1 | 1 | arXiv version target |
| `is-same-as` | 1 | 2 | arXiv ID와 arXiv DOI target |
| **합계** | **18 DOI 행** | **23 assertions** | source-kind 중복을 허용 |

## 18행 대조 결과

표의 `raw/current`은 원시 envelope와 현재 Crossref 단건의 relation 일치 여부다. target의 `200`은 현재 Crossref 단건 status이고, `404`는 실제 target 검색 실패다. DOI 링크와 resource 링크는 각각 DOI resolver와 Crossref가 준 공식 record 경로다.

| # | 연결 MR 후보와 source record | relation · asserted-by · target | target / 공식 record 대조 | 현재 후보에 미치는 의무 |
|---:|---|---|---|---|
| 1 | `MR3967086`; *Quantitative Geosciences…* (book), [10.1007/978-3-030-17860-4](https://doi.org/10.1007/978-3-030-17860-4) | `correction` · object · [10.1007/978-3-030-17860-4_25](https://doi.org/10.1007/978-3-030-17860-4_25) | raw/current 일치; target 200, book-chapter *Corrections to…*, Springer [record](https://link.springer.com/chapter/10.1007/978-3-030-17860-4_25) | correction target을 source 판본과 함께 보관·후속 판독 대상으로 표시. source를 자동 대체하지 않음. |
| 2 | `MR1798479`; *Relativity, Groups, Particles* (book), [10.1007/978-3-7091-6234-7](https://doi.org/10.1007/978-3-7091-6234-7) | `correction` · object · [10.1007/978-3-7091-6234-7_11](https://doi.org/10.1007/978-3-7091-6234-7_11) | 일치; target 200, book-chapter *Correction to…*, Springer [record](https://link.springer.com/chapter/10.1007/978-3-7091-6234-7_11) | correction target을 함께 대조. 자동 대체 금지. |
| 3 | `MR4371036`; *Fundamentals of Astrophysical Fluid Dynamics* (book), [10.1007/978-981-15-4174-2](https://doi.org/10.1007/978-981-15-4174-2) | `correction` · object · [10.1007/978-981-15-4174-2_27](https://doi.org/10.1007/978-981-15-4174-2_27) | 일치; target 200, book-chapter *Correction to…*, Springer [record](https://link.springer.com/chapter/10.1007/978-981-15-4174-2_27) | correction target을 함께 대조. 자동 대체 금지. |
| 4 | `MR1608967`; *Hirota’s difference equations* (journal-article), [10.1007/BF02634165](https://doi.org/10.1007/BF02634165) | `is-translation-of` · object · [10.4213/tmf1074](https://doi.org/10.4213/tmf1074) | 일치; target 200, bilingual *A survey of Hirota's difference equations*, Steklov/MathNet [record](http://mi.mathnet.ru/tmf1074) | 번역 관계 후보로 두 언어·판본을 분리 보존하고 실제 대응 범위를 확인. |
| 5 | `MR1623229`; *Singularity Theorems and Their Consequences* (journal-article), [10.1023/A:1018801101244](https://doi.org/10.1023/A:1018801101244) | `correction` · object · [10.1007/s10714-014-1746-7](https://doi.org/10.1007/s10714-014-1746-7) | 일치; target 200, article *Erratum to…*, Springer [record](https://link.springer.com/article/10.1007/s10714-014-1746-7) | erratum을 source와 함께 대조. 자동 대체 금지. |
| 6 | `MR1777352`; *Metric regularity and subdifferential calculus* (journal-article), [10.1070/rm2000v055n03abeh000292](https://doi.org/10.1070/rm2000v055n03abeh000292) | `is-translation-of` · subject **및** object · [10.4213/rm292](https://doi.org/10.4213/rm292) | 일치; target 200, bilingual 동명 article, Steklov/MathNet [record](http://mi.mathnet.ru/rm292). Source resolver는 403이어서 page body는 미판독. | 번역/판본 후보를 병합하지 말고 두 record의 언어·서지 범위를 재확인. |
| 7 | `MR1728882`; *Critical Phenomena in Gravitational Collapse* (journal-article), [10.12942/lrr-1999-4](https://doi.org/10.12942/lrr-1999-4) | `new_version` · object · [10.12942/lrr-2007-5](https://doi.org/10.12942/lrr-2007-5) | 일치; target 200, 동명 journal article, Springer [record](https://link.springer.com/article/10.12942/lrr-2007-5) | source와 new version을 함께 보관하고 차이·정정·인용 판본을 우선 대조. 최신 권위를 자동 판정하지 않음. |
| 8 | `MR2262054`; *Google's PageRank and Beyond* (edited-book), [10.1515/9781400830329](https://doi.org/10.1515/9781400830329) | `is-identical-to` · object · [10.2307/j.ctt7t8z9](https://doi.org/10.2307/j.ctt7t8z9) | 일치; target 200, 동명 PUP monograph, [JSTOR record](https://www.jstor.org/stable/10.2307/j.ctt7t8z9) | 동일성 주장을 판본/host 대조 후보로 기록; 자동 병합·내용 동일 판정 금지. |
| 9 | `MR2675288`; *Graph Theoretic Methods in Multiagent Networks* (edited-book), [10.1515/9781400835355](https://doi.org/10.1515/9781400835355) | `is-identical-to` · object · [10.2307/j.ctt1287k9b](https://doi.org/10.2307/j.ctt1287k9b) | 일치; target 200, 동명 PUP monograph, [JSTOR record](https://www.jstor.org/stable/10.2307/j.ctt1287k9b) | 동일성 주장을 판본/host 대조 후보로 기록. |
| 10 | `MR2791531`; *Totally Nonnegative Matrices* (edited-book), [10.1515/9781400839018](https://doi.org/10.1515/9781400839018) | `is-identical-to` · object · [10.23943/princeton/9780691121574.001.0001](https://doi.org/10.23943/princeton/9780691121574.001.0001) | 일치; target 200, 동명 PUP monograph, [OUP/PUP record](https://academic.oup.com/princeton-scholarship-online/book/37322) | 동일성 주장을 판본/host 대조 후보로 기록. |
| 11 | `MR3202834`; *Spaces of PL Manifolds and Categories of Simple Maps* (edited-book), [10.1515/9781400846528](https://doi.org/10.1515/9781400846528) | `is-identical-to` · object · [10.23943/princeton/9780691157757.001.0001](https://doi.org/10.23943/princeton/9780691157757.001.0001) | 일치; target 200, 동명 PUP monograph, [OUP/PUP record](https://academic.oup.com/princeton-scholarship-online/book/13551) | 동일성 주장을 판본/host 대조 후보로 기록. |
| 12 | `MR3241695`; *Topics in Quaternion Linear Algebra* (edited-book), [10.1515/9781400852741](https://doi.org/10.1515/9781400852741) | `is-identical-to` · object · [10.2307/j.ctt6wpz0p](https://doi.org/10.2307/j.ctt6wpz0p), [10.23943/princeton/9780691161853.001.0001](https://doi.org/10.23943/princeton/9780691161853.001.0001) | 일치; 두 target 모두 200, 동명 PUP monograph, [JSTOR](https://www.jstor.org/stable/10.2307/j.ctt6wpz0p) 및 [OUP/PUP](https://academic.oup.com/princeton-scholarship-online/book/13796) | 두 host DOI를 source와 분리 보존하고 판본/배포 관계를 대조. |
| 13 | `MR858706`; *A Source Book in Mathematics, 1200-1800* (edited-book), [10.1515/9781400858002](https://doi.org/10.1515/9781400858002) | `is-identical-to` · object · [10.2307/j.ctt7zvf7h](https://doi.org/10.2307/j.ctt7zvf7h) | 일치; target 200, 동명 PUP monograph, [JSTOR record](https://www.jstor.org/stable/10.2307/j.ctt7zvf7h) | 동일성 주장을 판본/host 대조 후보로 기록. |
| 14 | `MR3309240`; *Mathematical Methods in Elasticity Imaging* (edited-book), [10.1515/9781400866625](https://doi.org/10.1515/9781400866625) | `is-identical-to` · object · [10.23943/princeton/9780691165318.001.0001](https://doi.org/10.23943/princeton/9780691165318.001.0001), [10.2307/j.ctt1287kr2](https://doi.org/10.2307/j.ctt1287kr2) | 일치; 두 target 모두 200, 동명 PUP monograph, [OUP/PUP](https://academic.oup.com/princeton-scholarship-online/book/35849) 및 [JSTOR](https://www.jstor.org/stable/10.2307/j.ctt1287kr2) | 두 host DOI를 source와 분리 보존하고 판본/배포 관계를 대조. |
| 15 | `MR3559188`; *Quantal Response Equilibrium* (edited-book), [10.1515/9781400880928](https://doi.org/10.1515/9781400880928) | `is-identical-to` · object · [10.23943/princeton/9780691124230.001.0001](https://doi.org/10.23943/princeton/9780691124230.001.0001) | 일치; target 200, 동명 PUP monograph, [OUP/PUP record](https://academic.oup.com/princeton-scholarship-online/book/30673) | 동일성 주장을 판본/host 대조 후보로 기록. |
| 16 | `MR3586373`; *Optimal Transport Methods in Economics* (monograph), [10.1515/9781400883592](https://doi.org/10.1515/9781400883592) | `is-identical-to` · object · [10.23943/princeton/9780691172767.001.0001](https://doi.org/10.23943/princeton/9780691172767.001.0001) | 일치; target 200, 동명 PUP monograph, [OUP/PUP record](https://academic.oup.com/princeton-scholarship-online/book/30675) | 동일성 주장을 판본/host 대조 후보로 기록. |
| 17 | `MR3821507`; *Lectures on the Infrared Structure of Gravity and Gauge Theory* (monograph), [10.23943/9781400889853](https://doi.org/10.23943/9781400889853) | `is-identical-to` · object · [10.2307/j.ctvc777qv](https://doi.org/10.2307/j.ctvc777qv) | 일치; target 200, 동명 PUP monograph, [JSTOR record](https://www.jstor.org/stable/10.2307/j.ctvc777qv) | 동일성 주장을 판본/host 대조 후보로 기록. |
| 18 | `MR4683663`; *Non-associative algebraic structures: classification and structure* (journal-article), [10.46298/cm.11419](https://doi.org/10.46298/cm.11419) | `has-preprint` · subject · arXiv `2306.00425v1`; `is-same-as` · subject · arXiv `2306.00425` 및 [10.48550/arXiv.2306.00425](https://doi.org/10.48550/arXiv.2306.00425) | source relation 일치; CCSD [official record](https://cm.episciences.org/12504) 200. arXiv target 200. arXiv DOI의 Crossref 단건만 404. | preprint와 journal record를 분리 보존하고 판본·수정·발표 관계를 대조. Crossref target 실패를 relation 부재로 바꾸지 않음. |

Princeton University Press source DOI들의 resolver는 Crossref chooser로 도달했지만, 현재 Crossref `resource.primary.URL`과 target 단건은 위의 De Gruyter/JSTOR/OUP-PUP 운영 record와 PUP publisher metadata를 가리킨다. 이는 host/배포 record 대조 근거이며 원문 또는 edition identity의 완결 판정은 아니다.

## 즉시 후속 판독·대조 목록

다음 다섯 source는 correction 또는 new version 관계가 있어, 해당 source를 실제로 쓰기 전에 target record와 함께 먼저 대조해야 한다. 이 목록은 target을 내려받거나 수학 내용을 판정했다는 뜻이 아니다.

| MR | source DOI | 관계 target | 필요한 다음 확인 |
|---|---|---|---|
| `MR3967086` | `10.1007/978-3-030-17860-4` | `10.1007/978-3-030-17860-4_25` | correction의 범위와 적용 대상 |
| `MR1798479` | `10.1007/978-3-7091-6234-7` | `10.1007/978-3-7091-6234-7_11` | correction의 범위와 적용 대상 |
| `MR4371036` | `10.1007/978-981-15-4174-2` | `10.1007/978-981-15-4174-2_27` | correction의 범위와 적용 대상 |
| `MR1623229` | `10.1023/A:1018801101244` | `10.1007/s10714-014-1746-7` | erratum의 범위와 적용 대상 |
| `MR1728882` | `10.12942/lrr-1999-4` | `10.12942/lrr-2007-5` | new version의 차이, 인용·판독에 쓸 판본 |

## 현재 효과와 한계

20개 DOI target은 B002 후보 DOI 색인에 없었다. 그러므로 현 B002 MR 후보를 target으로 자동 대체하거나 병합하지 않는다. correction/new_version은 판본 추적의 우선 의무를 만들고, translation·identical·preprint 관계는 정확한 판본·언어·host 관계를 다시 확인할 의무를 만든다.

relation은 책·논문·번역·host가 수학적으로 같은 내용인지, target이 더 권위 있거나 최신인지, correction이 특정 주장에 영향을 주는지를 자체로 결정하지 않는다. 그런 판단은 필요한 공식 record와 원문/정정문을 실제로 대조한 뒤에만 할 수 있다.
