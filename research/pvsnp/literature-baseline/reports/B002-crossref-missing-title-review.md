# B002 Crossref missing-title 검토

검토일: 2026-09-04 KST. `catalog/B002-crossref-title-review.jsonl`의 `missing_crossref_title`은 한 건이다.

| DOI · MR | Crossref 상태 | 독립 공개 대조 | 처분 |
|---|---|---|---|
| `10.1070/RD2000v005n01ABEH000123` · `MR1784729` | HTTP 200 work record이지만 title 배열이 비어 있음 | [MathNet 공식 record](https://www.mathnet.ru/eng/rcd861)와 [Regular and Chaotic Dynamics 공식 article page](https://rcd.ics.org.ru/RD2000v005n01ABEH000123/)가 Grammaticos–Ramani, *The Hunting for the Discrete Painleve Equations*, vol. 5 no. 1 (2000), 53–66, 같은 DOI를 명시 | `same_work_external_record_confirmed_crossref_title_missing` |

Crossref의 title 누락을 문헌 부재나 DOI 오류로 해석하지 않는다. 후보 원문 title·저자·연도·쪽·DOI와 두 공식 공개 record가 일치하므로 이 DOI–MR 연결은 외부 record로 확인했지만, Crossref 응답 자체는 수정하거나 보충하지 않는다.
