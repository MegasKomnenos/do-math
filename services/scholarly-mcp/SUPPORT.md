전체 구현은 부분 완료다. 아래 표는 현재 등록된 자료원과 구현 상태를 대응시킨다. `partial`은 일부 기능 구현, `pending`은 미연결 또는 미구현이다. 자료원별 정확한 입력·제약은 `describe_source`가 제공한다. 실측 범위와 증거는 [검증 기록](VALIDATION.md)에 있다.

| 자료원 | source | 경로 | 구현 | 기능 | 실측 표지 |
|---|---|---|---|---|---|
| MathSciNet | mathscinet | playwright | partial | source_guide, search, fetch, export | live_mcp_search_export_fetch_extract |
| Web of Science Core Collection + CPCI | wos | playwright | partial | source_guide, search, fetch, export | live_mcp_search_full_record_export_extract |
| Scopus | scopus | playwright | partial | source_guide, search, fetch, export | live_mcp_pagination_extract_metadata_abstract_fetch |
| ACM Digital Library | acm-dl | playwright | partial | source_guide, search, fetch, export | live_mcp_search_export_original_pdf_fetch |
| IEEE Xplore / IEL | ieee-xplore | playwright | partial | source_guide, search, fetch, export | live_mcp_search_bibtex_extract_metadata_abstract_pdf_fetch |
| PQDT Global | pqdt | playwright | partial | source_guide, search, fetch, export | live_mcp_repeat_search_pagination_ris_pdf_fetch |
| zbMATH Open | zbmath | api | partial | source_guide, search, fetch, export | live_mcp_search_extract |
| arXiv | arxiv | api | partial | source_guide, search, fetch, export | live_mcp_search_extract |
| DBLP | dblp | api | partial | source_guide, search, fetch, export | access_challenge_observed |
| ECCC | eccc | playwright | partial | source_guide, search, fetch, export | live_mcp_search_revision_fetch |
| DROPS / LIPIcs | drops | fixed: metadata API; search/document links Playwright | partial | source_guide, search, fetch, export | live_mcp_search_metadata_abstract_pdf_fetch |
| Theory of Computing | theory-of-computing | playwright | partial | source_guide, search, fetch, export | live_mcp_indexes_citation_pdf_source_ps_references_fetch_and_text_pagination |
| Crossref | crossref | api | partial | source_guide, search, fetch, export | live_mcp_search_extract |
| Crossmark | crossmark | api | partial | source_guide, search, fetch, export | live_mcp_search_extract |
| OpenAlex | openalex | api | partial | source_guide, search, fetch, export | public_endpoint_search_observed |
| Semantic Scholar | semantic-scholar | api | partial | source_guide, search, fetch, export | rate_limit_observed |
| OpenCitations | opencitations | api | partial | source_guide, search, fetch, export | not_recorded |
| Unpaywall | unpaywall | api | partial | source_guide, search, fetch, export | public_endpoint_contact_requirement_observed |
| CORE | core | api | partial | source_guide, search, fetch, export | public_endpoint_success_and_rate_limit_observed |
| Project Euclid | project-euclid | playwright | partial | source_guide, fetch, export | live_adapter_metadata_abstract_pdf_fetch |
| EuDML | eudml | api | partial | source_guide, search, fetch, export | live_mcp_cql_rss_extract_nlm_fetch |
| Numdam | numdam | api | partial | source_guide, search, fetch, export | live_adapter_jats_pdf_fetch |
| Mathlib | mathlib | api | partial | source_guide, search, fetch, export | not_recorded |
| Archive of Formal Proofs | afp | api | partial | source_guide, search, fetch, export | live_mcp_entry_search_pinned_metadata_and_proof_source_fetch_extract |
| Mathematical Components | math-comp | api | partial | source_guide, search, fetch, export | not_recorded |
| GitHub | github | api | partial | source_guide, search, fetch, export | live_adapter_pinned_file_fetch |
| Zenodo | zenodo | api | partial | source_guide, search, fetch, export | live_mcp_search_file_checksum_fetch_extract |
| Software Heritage | software-heritage | api | partial | source_guide, search, fetch, export | live_adapter_origin_search_fetch |
| AMS publications | ams | under_investigation | pending | 미구현 | not_recorded |
| Cambridge University Press | cambridge | playwright | partial | source_guide, fetch, export | live_adapter_metadata_only |
| De Gruyter Brill | de-gruyter | under_investigation | pending | 미구현 | not_recorded |
| JSTOR | jstor | under_investigation | pending | 미구현 | not_recorded |
| Oxford University Press | oxford | playwright | partial | source_guide, fetch, export | live_adapter_metadata_pdf_fetch |
| ScienceDirect | science-direct | playwright | pending | 미구현 | not_recorded |
| Springer Nature | springer | playwright | partial | source_guide, fetch, export | live_adapter_metadata_abstract_pdf_fetch |
| Taylor & Francis | taylor-francis | under_investigation | pending | 미구현 | not_recorded |
| Wiley | wiley | under_investigation | pending | 미구현 | not_recorded |
| AIP | aip | playwright | partial | source_guide, fetch, export | live_adapter_metadata_abstract_fetch |
| APS 공개 접근 | aps | api | partial | source_guide, search, fetch, export | live_mcp_open_access_feed_metadata_abstract_pdf_fetch |
| IOP | iop | under_investigation | pending | 미구현 | not_recorded |
| SIAM | siam | under_investigation | pending | 미구현 | not_recorded |
| KNU FRIC | knu-fric | under_investigation | pending | 미구현 | not_recorded |
| 개별 구독 자료원 | individual-subscription | target_dependent | pending | 미구현 | not_recorded |
| 학회·저널 공식 사이트 | society-journal | target_dependent | pending | 미구현 | not_recorded |
| 저자·기관 공개본 | author-repository | target_dependent | pending | 미구현 | not_recorded |
| 일반 웹 후보 발견 | general-web | target_dependent | pending | 미구현 | not_recorded |
| APS 기관 구독 접근 | aps-institutional | playwright | partial | source_guide, fetch, export | live_adapter_metadata_and_fulltext_restriction |

개별 구독·학회 저널·저자 또는 기관 공개본·일반 웹은 아직 구체 서비스가 정해지지 않은 범주다. 이 표에 남겨 범위를 누락하지 않았으며 임의의 웹사이트를 지원하는 어댑터가 완료됐다는 뜻은 아니다.
