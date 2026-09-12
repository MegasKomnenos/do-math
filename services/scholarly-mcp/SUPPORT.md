전체 구현은 부분 완료다. `partial`은 일부 기능 구현, `pending`은 미연결 또는 미구현, `deferred`는 사용자 지시에 따른 사용 보류다. 자료원별 입력·제약은 `describe_source`, 실제 검증 범위는 [검증 기록](VALIDATION.md)을 따른다.

| 자료원 | source | 경로 | 구현 | 기능 | 실측 표지 |
|---|---|---|---|---|---|
| MathSciNet | mathscinet | playwright | partial | source_guide, search, fetch, export | live_mcp_search_four_exports_review_pdf_mr_doi_incoming_reviews_outgoing_subset_windows |
| Web of Science Core Collection + CPCI | wos | playwright | partial | source_guide, search, fetch, export | live_mcp_editions_sorts_friendly_facets_discovery_windows_exports_citing_and_identity |
| Scopus | scopus | playwright | partial | source_guide, search, fetch, export | live_mcp_search_fetch_references_pagination_cited_by_extract |
| ACM Digital Library | acm-dl | playwright | partial | source_guide, search, fetch, export | live_mcp_edit_query_boolean_combined_filters_native_exports_html_tex_pdf_supplement_and_identity |
| IEEE Xplore / IEL | ieee-xplore | playwright | partial | source_guide, search, fetch, export | live_mcp_native_exports_filtered_windows_typeahead_pdf_html_identity_references_media |
| PQDT Global | pqdt | playwright | partial | source_guide, search, fetch, export | live_mcp_filtered_windows_zero_seven_exports_extract_fulltext_pdf_supplement_png |
| zbMATH Open | zbmath | api | partial | source_guide, search, fetch, export | live_mcp_arbitrary_window_doi_legacy_link_license_state_references |
| arXiv | arxiv | api | partial | source_guide, search, fetch, export | live_mcp_search_pinned_html_source_archive_tex_extract |
| DBLP | dblp | api | partial | source_guide, search, fetch, export | live_mcp_native_timed_refresh_search_seven_exports_name_and_record_identity |
| DBLP Knowledge Graph | dblp-kg | api | partial | source_guide, search, fetch, export | live_mcp_sparql_window_native_csv_tsv_key_doi_name; native_tsv_year_type_mismatch |
| ECCC | eccc | playwright | partial | source_guide, search, fetch, export | live_mcp_name_candidates_search_and_pinned_revision_fetch |
| DROPS / LIPIcs | drops | fixed: metadata API; search/document links Playwright | partial | source_guide, search, fetch, export | live_mcp_native_exports_pdf_html_codemeta_and_supplementary_references |
| Theory of Computing | theory-of-computing | playwright | partial | source_guide, search, fetch, export | live_mcp_indexes_citation_pdf_source_ps_references_fetch_and_text_pagination |
| Crossref | crossref | api | partial | source_guide, search, fetch, export | live_mcp_search_native_citation_eight_formats_extract |
| Crossmark | crossmark | api | partial | source_guide, search, fetch, export | live_mcp_search_extract |
| OpenAlex | openalex | api | partial | source_guide, search, fetch, export | live_mcp_arbitrary_window_group_cursor_abstract_relationships_name_doi |
| Semantic Scholar | semantic-scholar | api | partial | source_guide, search, fetch, export | live_mcp_search_extract; new_workflow_rate_limited; schema_regressions |
| OpenCitations | opencitations | api | partial | source_guide, search, fetch, export | live_mcp_native_csv_window_oci_fetch_reference_count |
| Unpaywall | unpaywall | api | deferred | source_guide | public_endpoint_contact_requirement_observed |
| CORE | core | api | partial | source_guide, search, fetch, export | live_mcp_name_metadata_abstract_and_restricted_fulltext_notice |
| Project Euclid | project-euclid | playwright | partial | source_guide, search, fetch, export | live_mcp_advanced_search_four_citations_pdf_and_supplement_zip_text_extract |
| EuDML | eudml | api | partial | source_guide, search, fetch, export | live_mcp_cql_rss_extract_nlm_fetch |
| Numdam | numdam | fixed: OAI/citation API; native search/DOI resolution Playwright | partial | source_guide, search, fetch, export | live_mcp_native_search_citations_jats_pdf_djvu_fetch_pagination |
| Mathlib | mathlib | api | partial | source_guide, search, fetch, export | live_mcp_pinned_source_search_file_fetch_line_comparison |
| Archive of Formal Proofs | afp | api | partial | source_guide, search, fetch, export | live_mcp_entry_search_pinned_metadata_and_proof_source_fetch_extract |
| Mathematical Components | math-comp | api | partial | source_guide, search, fetch, export | live_mcp_pinned_source_search_file_fetch_line_comparison |
| GitHub | github | api | partial | source_guide, search, fetch, export | live_mcp_arbitrary_search_window_native_pages_pinned_zip_file_same_bytes |
| Zenodo | zenodo | api | partial | source_guide, search, fetch, export | live_mcp_arbitrary_search_window_native_pages_file_checksum_fetch_extract |
| Figshare | figshare | api | partial | source_guide, search, fetch, export | live_mcp_beyond_offset_window_collection_native_file_redirect_md5_and_text_extract |
| Software Heritage | software-heritage | api | partial | source_guide, search, fetch, export | live_mcp_verified_content_trees_git_history_snapshot_and_release; direct_release_flat_pending |
| AMS publications | ams | playwright (전용 Chrome 창/CDP) | partial | source_guide, search, fetch, export | live_mcp_native_search_window_zero_xlsx_product_fetch_pdf; dynamic_ui_provider_error |
| Cambridge University Press | cambridge | fixed: citation API; institutional search/document Playwright | partial | source_guide, search, fetch, export | live_mcp_filtered_search_ris_pdf_and_supplement_pdf_zip_source_extract |
| De Gruyter Brill | de-gruyter | playwright | partial | source_guide, search, fetch, export | live_mcp_search_ris_pdf_and_supplement_zip_cif_lines; broken_link_observed |
| JSTOR | jstor | fixed: citation/search API; institutional document Playwright | partial | source_guide, search, fetch, export | live_mcp_search_image_sorts_facets_citations_pdf_mp3_transcripts_supplement; native_video_download_disabled |
| Oxford University Press | oxford | playwright | partial | source_guide, search, fetch, export | live_mcp_search_citation_metadata_abstract_pagination_and_supplement_pdf |
| ScienceDirect | science-direct | playwright (전용 Chrome 창/CDP) | partial | source_guide, search, fetch, export | live_mcp_search_cross_page_ris_zero_facets_exact_publication_three_citations_pdf_supplement_video |
| Springer Nature | springer | playwright | partial | source_guide, search, fetch, export | live_mcp_advanced_search_citations_pdf_supplements_nature_springer_html_tex_figures |
| Taylor & Francis | taylor-francis | playwright | partial | source_guide, search, fetch, export | live_mcp_search_citation_pdf_dublin_doi_supplement_zip_tables_nested_source |
| Wiley | wiley | playwright | partial | source_guide, search, fetch, export | live_mcp_dynamic_advanced_rows_citations_pdf_zero_and_supplementary_zip |
| AIP | aip | playwright | partial | source_guide, search, fetch, export | live_mcp_advanced_search_citation_pdf_and_explicit_figshare_supplement_reference |
| APS 공개 접근 | aps | api | partial | source_guide, search, fetch, export | live_mcp_open_access_feed_metadata_abstract_pdf_fetch |
| IOP | iop | fixed: newest RSS API; other sorts/extra filters/document Playwright | partial | source_guide, search, fetch, export | live_mcp_rss_ranked_filters_native_search_citations; pdf_html_tex_figures_supplement_pdf_verified |
| SIAM | siam | playwright (전용 Chrome 창/CDP) | partial | source_guide, search, fetch, export | live_mcp_advanced_terms_topic_publication_dates_five_citations_cross_page_book_fetch_zero |
| KNU FRIC | knu-fric | playwright | partial | source_guide, search, fetch, export | live_mcp_catalogue_pagination_issn_fetch_zero_result |
| KNU 개별 구독 저널 목록 | individual-subscription | playwright | partial | source_guide, search, fetch, export | live_mcp_two_catalogues_95_holdings_six_siam_csv_range_year_fetch_zero |
| 학회·저널 공식 사이트 | society-journal | fixed: public document Playwright; OJS native citation API | partial | source_guide, fetch, export | live_mcp_public_journal_metadata_abstract_pdf_native_citations; shared_dynamic_renderer_verified |
| 저자·기관 공개본 | author-repository | fixed: public document Playwright; OJS native citation API | partial | source_guide, fetch, export | live_mcp_public_author_pdf_dynamic_document_and_page_links |
| 일반 웹 후보 발견 | general-web | api (Mwmbl public search) | partial | source_guide, search, export | live_mcp_public_api_candidates_csv_extract_empty_result |
| APS 기관 구독 접근 | aps-institutional | playwright (전용 Chrome 창/CDP) | partial | source_guide, search, fetch, export | live_mcp_search_window_custom_multi_facets_bibtex_ris_abstract_pdf_supplement |

개별 구독은 KUDOS의 KNU 개별전자저널·KNU P+O Journal 보유 목록으로 구체화했다. 목록 기재와 실제 원문 권한은 구별한다. 학회 저널·저자 또는 기관 공개본은 지정 URL을, 일반 웹은 공개 후보 검색을 제공한다. Unpaywall과 Scopus의 별도 웹 계정 내보내기는 보류하며 해당 자격 정보를 요청하지 않는다. [접근 조건 조사](ACCESS-RESEARCH.md)는 창 모드·실행 방식·기관 경로의 비교 근거를 담는다.
