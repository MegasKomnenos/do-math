# B002 DOI escape 결함의 수리 검증

검토일: 2026-09-04 KST. 이 보고서는 과거 `crossref_not_found` 65건의 **정규화 결함 진단·수리 검증 사례**다. 현행 Crossref 색인을 과거 404 상태로 읽지 않는다.

## 현행 결론

DOI 정규화기가 BibTeX 표기 `\_`를 DOI 문자 `_`로 복원한 뒤 후보·manifest·Crossref 수집을 재생성했다. 실제 `catalog/B002-crossref.jsonl` 2,748행을 다시 집계하면 `found=2,693`, `found_alias=55`, active `crossref_not_found=0`이다. 이 상태는 [`manifests/B002-crossref.json`](../manifests/B002-crossref.json)과 [`manifests/B002-crossref-title-review.json`](../manifests/B002-crossref-title-review.json)의 같은 `found`·`found_alias` 계수와도 일치한다.

과거 65개 404 응답은 삭제하지 않고 `intake/B002-public/crossref-invalid-doi-escape/`에 격리했다. 격리 디렉터리의 파일 수는 65다. 따라서 과거 404는 현행 DOI 부재나 Crossref 비등록의 증거가 아니라, escape가 남은 요청 문자열의 실패 기록이다.

## 원인과 대표 대조

과거 requested DOI에는 모두 `\_`가 있었고, 이를 `_`로 복원한 DOI를 Crossref agency endpoint에 순차 요청했을 때 65/65가 HTTP 200, agency `crossref`를 반환했다. 첫 8건은 DOI Registration Agency API도 HTTP 200, `RA=Crossref`로 독립 대조했다.

| 연결 MR | 과거 requested DOI | 교정 DOI | 확인 범위 |
|---|---|---|---|
| MR1919825 | `10.1007/0-387-21791-6\_1` | `10.1007/0-387-21791-6_1` | Crossref agency 200; Crossref; RA API 200 |
| MR2126642 | `10.1007/0-8176-4430-x\_3` | `10.1007/0-8176-4430-x_3` | Crossref agency 200; Crossref; RA API 200 |
| MR2159215 | `10.1007/1-4020-2307-3\_9` | `10.1007/1-4020-2307-3_9` | Crossref agency 200; Crossref; RA API 200 |
| MR2210125 | `10.1007/1-4020-3817-8\_2` | `10.1007/1-4020-3817-8_2` | Crossref agency 200; Crossref; RA API 200 |
| MR2219821 | `10.5209/rev\_rema.2006.v19.n1.16621` | `10.5209/rev_rema.2006.v19.n1.16621` | Crossref agency 200; Crossref |

공식 요청 형식은 `https://api.crossref.org/works/<URL-encoded DOI>/agency`와 `https://doi.org/ra/<DOI>`다. 이 검토는 등록기관·식별자 상태만 확인했으며 PDF·원문·크리덴셜을 사용하지 않았다.

## 집합 검산과 경계

- 과거 escape 원시 집합: 65 DOI, 65 MR 연결.
- 교정 DOI 집합: 65 DOI, active Crossref 색인에 65/65 존재·응답 성공.
- 원시 집합과 교정 집합은 각 원소에서 `\_ → _`만 적용한 일대일 대응이다. MR 연결과 행 수의 대칭차는 0이다.
- active 상태: `found=2693`, `found_alias=55`, `crossref_not_found=0`.

따라서 이전 보고의 `invalid_identifier`는 현재 후보 데이터의 영구 상태가 아니라 입력 escape 결함의 역사적 진단이다. 실제 후보 JSONL과 Crossref 색인은 이번 수리에서 정규화·재생성·재수집되었으며, 이 보고서는 그 변경을 수행하지 않고 현행 산출물을 감사한다.
