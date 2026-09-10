전체 구현은 부분 완료다. `partial`은 일부 기능 구현, `pending`은 미연결 또는 미구현, `deferred`는 사용자 지시에 따른 사용 보류다. 자료원별 입력·제약은 `describe_source`, 실제 검증 범위는 [검증 기록](VALIDATION.md)을 따른다.

| 자료원 | source | 경로 | 구현 | 기능 | 실측 표지 |
|---|---|---|---|---|---|
| MathSciNet | mathscinet | playwright | partial | source_guide, search, fetch, export | live_mcp_search_export_fetch_extract |
| Web of Science Core Collection + CPCI | wos | playwright | partial | source_guide, search, fetch, export | live_mcp_search_full_record_title_url_native_xls_extract |
| Scopus | scopus | playwright | partial | source_guide, search, fetch, export | live_mcp_search_fetch_references_pagination_cited_by_extract |
| ACM Digital Library | acm-dl | playwright | partial | source_guide, search, fetch, export | live_mcp_search_citation_pdf_and_supplement_zip_inner_pdf_extract |
| IEEE Xplore / IEL | ieee-xplore | playwright | partial | source_guide, search, fetch, export | live_mcp_search_citation_pdf_references_and_graphical_video_ranges_cover |
| PQDT Global | pqdt | playwright | partial | source_guide, search, fetch, export | live_mcp_repeat_search_ris_pdf_and_supplemental_png_fetch_extract |
| zbMATH Open | zbmath | api | partial | source_guide, search, fetch, export | live_mcp_arbitrary_window_doi_legacy_link_license_state_references |
| arXiv | arxiv | api | partial | source_guide, search, fetch, export | live_mcp_search_pinned_html_source_archive_tex_extract |
| DBLP | dblp | api | partial | source_guide, search, fetch, export | access_challenge_observed |
| ECCC | eccc | playwright | partial | source_guide, search, fetch, export | live_mcp_search_revision_fetch |
| DROPS / LIPIcs | drops | fixed: metadata API; search/document links Playwright | partial | source_guide, search, fetch, export | live_mcp_native_exports_pdf_html_codemeta_and_supplementary_references |
| Theory of Computing | theory-of-computing | playwright | partial | source_guide, search, fetch, export | live_mcp_indexes_citation_pdf_source_ps_references_fetch_and_text_pagination |
| Crossref | crossref | api | partial | source_guide, search, fetch, export | live_mcp_search_native_citation_eight_formats_extract |
| Crossmark | crossmark | api | partial | source_guide, search, fetch, export | live_mcp_search_extract |
| OpenAlex | openalex | api | partial | source_guide, search, fetch, export | live_mcp_arbitrary_window_group_cursor_abstract_relationships_name_doi |
| Semantic Scholar | semantic-scholar | api | partial | source_guide, search, fetch, export | rate_limit_observed |
| OpenCitations | opencitations | api | partial | source_guide, search, fetch, export | live_mcp_native_csv_window_oci_fetch_reference_count |
| Unpaywall | unpaywall | api | deferred | source_guide | public_endpoint_contact_requirement_observed |
| CORE | core | api | partial | source_guide, search, fetch, export | live_mcp_search_extract; fetch_rate_limit; fulltext_notice_regression |
| Project Euclid | project-euclid | playwright | partial | source_guide, search, fetch, export | live_mcp_advanced_filters_repeat_sorted_pagination_four_citations_pdf_fetch |
| EuDML | eudml | api | partial | source_guide, search, fetch, export | live_mcp_cql_rss_extract_nlm_fetch |
| Numdam | numdam | fixed: OAI/citation API; native search/DOI resolution Playwright | partial | source_guide, search, fetch, export | live_mcp_native_search_citations_jats_pdf_djvu_fetch_pagination |
| Mathlib | mathlib | api | partial | source_guide, search, fetch, export | live_mcp_pinned_source_search_file_fetch_line_comparison |
| Archive of Formal Proofs | afp | api | partial | source_guide, search, fetch, export | live_mcp_entry_search_pinned_metadata_and_proof_source_fetch_extract |
| Mathematical Components | math-comp | api | partial | source_guide, search, fetch, export | live_mcp_pinned_source_search_file_fetch_line_comparison |
| GitHub | github | api | partial | source_guide, search, fetch, export | live_adapter_pinned_file_fetch |
| Zenodo | zenodo | api | partial | source_guide, search, fetch, export | live_mcp_search_file_checksum_fetch_extract |
| Figshare | figshare | api | partial | source_guide, search, fetch, export | live_mcp_public_search_window_collection_versioned_file_md5_pdf_extract |
| Software Heritage | software-heritage | api | partial | source_guide, search, fetch, export | live_adapter_origin_search_fetch |
| AMS publications | ams | playwright | partial | source_guide, search, fetch, export | live_mcp_explicit_pdf; native_browser_mixed_search; search_adapter_restricted |
| Cambridge University Press | cambridge | fixed: citation API; institutional search/document Playwright | partial | source_guide, search, fetch, export | live_mcp_filtered_search_ris_pdf_and_supplement_pdf_zip_source_extract |
| De Gruyter Brill | de-gruyter | playwright | partial | source_guide, search, fetch, export | live_mcp_search_ris_pdf_and_supplement_zip_cif_lines; broken_link_observed |
| JSTOR | jstor | api (native citation); browser search/document pending | partial | source_guide, fetch, export | live_mcp_public_ris_metadata_abstract_fetch; web_captcha_observed |
| Oxford University Press | oxford | playwright | partial | source_guide, search, fetch, export | live_mcp_search_citation_metadata_abstract_pagination_and_supplement_pdf |
| ScienceDirect | science-direct | playwright | partial | source_guide, fetch, export | live_mcp_institutional_ris_bibtex_plain_metadata_abstract_fetch |
| Springer Nature | springer | playwright | partial | source_guide, search, fetch, export | live_mcp_advanced_search_citations_pdf_pagination_and_supplementary_files |
| Taylor & Francis | taylor-francis | playwright | partial | source_guide, search, fetch, export | live_mcp_search_citation_pdf_dublin_doi_supplement_zip_tables_nested_source |
| Wiley | wiley | playwright | partial | source_guide, search, fetch, export | live_mcp_advanced_search_citations_pdf_empty_repeat_and_supplementary_zip |
| AIP | aip | playwright | partial | source_guide, search, fetch, export | live_mcp_advanced_search_citation_pdf_and_explicit_figshare_supplement_reference |
| APS 공개 접근 | aps | api | partial | source_guide, search, fetch, export | live_mcp_open_access_feed_metadata_abstract_pdf_fetch |
| IOP | iop | playwright | partial | source_guide, fetch, export | live_adapter_metadata_pdf; citation_unverified_after_gateway_challenge |
| SIAM | siam | playwright | partial | source_guide, fetch, export | live_mcp_public_front_matter_pdf_fetch_extract; search_challenge_observed |
| KNU FRIC | knu-fric | playwright | partial | source_guide, search, fetch, export | live_mcp_catalogue_pagination_issn_fetch_zero_result |
| 개별 구독 자료원 | individual-subscription | target_dependent | pending | 미구현 | not_recorded |
| 학회·저널 공식 사이트 | society-journal | fixed: public document Playwright; OJS native citation API | partial | source_guide, fetch, export | live_mcp_public_journal_metadata_abstract_pdf_native_citations |
| 저자·기관 공개본 | author-repository | fixed: public document Playwright; OJS native citation API | partial | source_guide, fetch, export | live_mcp_public_author_pdf_and_page_links |
| 일반 웹 후보 발견 | general-web | api (Mwmbl public search) | partial | source_guide, search, export | live_mcp_public_api_candidates_csv_extract_empty_result |
| APS 기관 구독 접근 | aps-institutional | playwright | partial | source_guide, fetch, export | live_adapter_metadata_and_fulltext_restriction |

개별 구독·학회 저널·저자 또는 기관 공개본·일반 웹은 구체 서비스가 정해지지 않은 범주다. 범위를 누락하지 않도록 목록에 유지한다. Unpaywall과 Scopus의 별도 웹 계정 내보내기는 보류하며 해당 자격 정보를 요청하지 않는다.
