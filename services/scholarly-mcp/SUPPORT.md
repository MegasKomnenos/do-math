49개 자료원의 지원 범위를 나타낸다. `partial`은 그 자료원의 일부 기능을 지원한다는 뜻이며 이번에 확인한 수리가 미완료라는 뜻으로 일괄 해석하지 않는다. `pending`은 미연결 또는 미구현, `deferred`는 사용자 지시에 따른 사용 보류다. 자료원별 입력은 `describe_source`, 검증 근거는 [검증 기록](VALIDATION.md), 남은 개별 조건은 [후속 인계](CONTINUATION.md)를 따른다.

| 자료원 | source | 경로 | 구현 | 기능 | 실측 표지 |
|---|---|---|---|---|---|
| MathSciNet | mathscinet | playwright | partial | source_guide, search, fetch, export | live_mcp_six_sorts_seven_facets_searched_candidates_four_exports_review_graph_windows |
| Web of Science Core Collection + CPCI | wos | playwright | partial | source_guide, search, fetch, export | live_mcp_editions_sorts_friendly_facets_windows_exports_citing_sorts_and_identity |
| Scopus | scopus | playwright | partial | source_guide, search, fetch, export | live_mcp_nine_sorts_thirteen_facets_exact_windows_native_facet_counts_and_relations |
| ACM Digital Library | acm-dl | playwright | partial | source_guide, search, fetch, export | live_mcp_edit_query_boolean_combined_filters_native_exports_html_tex_pdf_supplement_and_identity |
| IEEE Xplore / IEL | ieee-xplore | playwright | partial | source_guide, search, fetch, export | 원 내보내기·검색 창·PDF/HTML·참고문헌; DOI 인용 링크가 있는 Media 카드 MP4 복원 |
| PQDT Global | pqdt | playwright | partial | source_guide, search, fetch, export | live_mcp_21_facet_values_filtered_windows_zero_seven_exports_fulltext_supplement |
| zbMATH Open | zbmath | api | partial | source_guide, search, fetch, export | live_mcp_arbitrary_window_doi_legacy_link_license_state_references |
| arXiv | arxiv | api | partial | source_guide, search, fetch, export | live_mcp_search_pinned_html_source_archive_tex_extract |
| DBLP | dblp | api | partial | source_guide, search, fetch, export | live_mcp_native_timed_refresh_search_seven_exports_name_and_record_identity |
| DBLP Knowledge Graph | dblp-kg | api | partial | source_guide, search, fetch, export | 원 CSV/TSV와 JSON 기반 tsv_exact; RDF 원 문자열·자료형 검증·생성 실패 시 JSON 보존 |
| ECCC | eccc | playwright | partial | source_guide, search, fetch, export | live_mcp_name_candidates_search_and_pinned_revision_fetch |
| DROPS / LIPIcs | drops | fixed: metadata API; search/document links Playwright | partial | source_guide, search, fetch, export | live_mcp_native_exports_pdf_html_codemeta_and_supplementary_references |
| Theory of Computing | theory-of-computing | playwright | partial | source_guide, search, fetch, export | live_mcp_indexes_citation_pdf_source_ps_references_fetch_and_text_pagination |
| Crossref | crossref | api | partial | source_guide, search, fetch, export | live_mcp_search_native_citation_eight_formats_extract |
| Crossmark | crossmark | api | partial | source_guide, search, fetch, export | 정정·철회 incoming/outgoing 구분·중복 보존·형식 오류 unknown·요청 간격과 제한 헤더 |
| OpenAlex | openalex | api | partial | source_guide, search, fetch, export | live_mcp_arbitrary_window_group_cursor_abstract_relationships_name_doi |
| Semantic Scholar | semantic-scholar | api | partial | source_guide, search, fetch, export | 원본 bulk1000·cursor·title-match 검증; batch/BibTeX/관계 양성 이력·최신 batch429 구별 |
| OpenCitations | opencitations | api | partial | source_guide, search, fetch, export | live_mcp_native_csv_window_oci_fetch_reference_count |
| Unpaywall | unpaywall | api | deferred | source_guide | public_endpoint_contact_requirement_observed |
| CORE | core | api | partial | source_guide, search, fetch, export | 원본 검색·work/output8쪽·명시26쪽·files01복구48쪽·제거404 검증; indexed 안내와 rate 구별 |
| Project Euclid | project-euclid | playwright | partial | source_guide, search, fetch, export | live_mcp_21_condition_semantics_window_50_page_bound_citations_pdf_supplement |
| EuDML | eudml | api | partial | source_guide, search, fetch, export | CQL/NLM·실제 책 서지와14장 검증; 목차의 전문 오판 수리·간헐적504 구별 |
| Numdam | numdam | fixed: OAI/citation API; native search/DOI resolution Playwright | partial | source_guide, search, fetch, export | 11조건·날짜만 검색·한쪽 열린 범위·qdt 마지막 페이지·원 인용/JATS/PDF/DJVU |
| Mathlib | mathlib | api | partial | source_guide, search, fetch, export | live_mcp_pinned_source_search_file_fetch_line_comparison |
| Archive of Formal Proofs | afp | api | partial | source_guide, search, fetch, export | live_mcp_entry_search_pinned_metadata_and_proof_source_fetch_extract |
| Mathematical Components | math-comp | api | partial | source_guide, search, fetch, export | live_mcp_pinned_source_search_file_fetch_line_comparison |
| GitHub | github | api | partial | source_guide, search, fetch, export | live_mcp_arbitrary_search_window_native_pages_pinned_zip_file_same_bytes |
| Zenodo | zenodo | api | partial | source_guide, search, fetch, export | live_mcp_arbitrary_search_window_native_pages_file_checksum_fetch_extract |
| Figshare | figshare | api | partial | source_guide, search, fetch, export | 판본별 구성원·동일 current 판본의 REST 보완·과거 불일치 partial; 원 파일 size/MD5 |
| Software Heritage | software-heritage | api | partial | source_guide, search, fetch, export | 개별 파일·트리·cache 재개·원 archive 검증; 특정 Vault는 new·압축 미완료 |
| AMS publications | ams | playwright (전용 Chrome 창/CDP) | partial | source_guide, search, fetch, export | Title/Author 식 부분집합·첫 XLSX·Unicode·순번 공백과 이어받기 원본13검증; 미매핑 식 별도 |
| Cambridge University Press | cambridge | fixed: citation API; institutional search/document Playwright | partial | source_guide, search, fetch, export | live_mcp_filtered_search_ris_pdf_and_supplement_pdf_zip_source_extract |
| De Gruyter Brill | de-gruyter | playwright | partial | source_guide, search, fetch, export | DOI·DOI 없는 ISBN 책의 현재 CITE/RIS 복원; 원본7검증·PDF/첨부; 특정 옛 첨부404 별도 |
| JSTOR | jstor | fixed: citation/search API; institutional document Playwright | partial | source_guide, search, fetch, export | live_mcp_search_image_sorts_facets_citations_pdf_mp3_transcripts_supplement; native_video_download_disabled |
| Oxford University Press | oxford | playwright | partial | source_guide, search, fetch, export | 렌더된 검색 행·원 인용·문헌/첨부; 별도 title-list는 현재 CAPTCHA 도메인 오류 |
| ScienceDirect | science-direct | playwright (전용 Chrome 창/CDP) | partial | source_guide, search, fetch, export | 검색/선택 Export·상세 Cite·31쪽 PDF 원본검증; Preface 비구독·선택 상태와 결과 보존·검색 준비 수리 |
| Springer Nature | springer | playwright | partial | source_guide, search, fetch, export | live_mcp_advanced_search_citations_pdf_supplements_nature_springer_html_tex_figures |
| Taylor & Francis | taylor-francis | playwright | partial | source_guide, search, fetch, export | 원 검색/인용/PDF/첨부·표; 두 editorial의 초록 필드 부재와 초록 양성 대조 |
| Wiley | wiley | playwright | partial | source_guide, search, fetch, export | live_mcp_dynamic_advanced_rows_citations_pdf_zero_and_supplementary_zip |
| AIP | aip | playwright | partial | source_guide, search, fetch, export | live_mcp_advanced_search_citation_pdf_and_explicit_figshare_supplement_reference |
| APS 공개 접근 | aps | api | partial | source_guide, search, fetch, export | live_mcp_arbitrary_feed_window_native_pages_metadata_abstract_pdf |
| IOP | iop | fixed: newest RSS API; other sorts/extra filters/document Playwright | partial | source_guide, search, fetch, export | live_mcp_rss_ranked_filters_native_search_citations; pdf_html_tex_154_equations_manifest_images_supplement |
| SIAM | siam | playwright (전용 Chrome 창/CDP) | partial | source_guide, search, fetch, export | 52번째 조건17/17/0·자유 Author 보존·명시 exact 공동저자 AND 검증; 특정 기관 PDF 제한 |
| KNU FRIC | knu-fric | playwright | partial | source_guide, search, fetch, export | live_mcp_catalogue_pagination_issn_fetch_zero_result |
| KNU 개별 구독 저널 목록 | individual-subscription | playwright | partial | source_guide, search, fetch, export | live_mcp_two_catalogues_95_holdings_six_siam_csv_range_year_fetch_zero |
| 학회·저널 공식 사이트 | society-journal | fixed: public document Playwright; OJS native citation API | partial | source_guide, fetch, export | live_mcp_public_journal_metadata_abstract_pdf_native_citations; shared_dynamic_renderer_verified |
| 저자·기관 공개본 | author-repository | fixed: public document Playwright; OJS native citation API | partial | source_guide, fetch, export | live_mcp_public_author_pdf_dynamic_document_and_page_links |
| 일반 웹 후보 발견 | general-web | api (Mwmbl public search) | partial | source_guide, search, export | live_mcp_public_api_candidates_csv_extract_empty_result |
| APS 기관 구독 접근 | aps-institutional | playwright (전용 Chrome 창/CDP) | partial | source_guide, search, fetch, export | live_mcp_search_window_custom_multi_facets_bibtex_ris_abstract_pdf_supplement |

개별 구독은 KUDOS의 KNU 개별전자저널·KNU P+O Journal 보유 목록으로 구체화했다. 목록 기재와 실제 원문 권한은 구별한다. 학회 저널·저자 또는 기관 공개본은 지정 URL을, 일반 웹은 공개 후보 검색을 제공한다. Unpaywall과 Scopus의 별도 웹 계정 내보내기는 보류하며 해당 자격 정보를 요청하지 않는다. [접근 조건 조사](ACCESS-RESEARCH.md)는 창 모드·실행 방식·기관 경로의 비교 근거를 담는다.


2026-09-13 KST의 전수조사는 [49개 자료원 재검토표](AUDIT-MATRIX.md)와 [실패 지점 분석](LIMITATIONS-AUDIT.md)에 정리했다.24개 CLI 과제와 root의 추가 검토에서 확인한 수리를 원본에 통합했고, 최종 전체633검사가 통과했다. 새 원본 SDK, 실제 전후 이미지, 저장 응답 재생의 범위를 검증 기록에서 구별한다. 현재 자료원 오류·문헌별 미제공·접근 제한은 구현 수리와 별개로 남긴다.

DBLP의 원본 재검증은 `data/access-research/user-criteria-dblp/root-sdk.json`과 `root-limits.json`에 있다. 검색·7형식 추출13호출과1,000개 고유 문헌 회수가 성공했다. 원 API의 현재100건 응답 크기를 전체 요청 범위의 한계로 쓰지 않으며, 중간 제한 때 부분 결과와 다음 위치를 보존한다.

SIAM의 PDF 제어·접근 상태 분류와 JSTOR의 지연 문헌/접근 확인 관찰을 수리했다. SIAM의 비공개 PDF와 JSTOR의 해당 영상 다운로드는 현재 접근·제공 상태가 계속 제한되지만, 공개 SIAM PDF와 JSTOR 오디오·전사문은 새 원본 SDK로 검증했다.
