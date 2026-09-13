"""Source scope and caller-facing capabilities. Pending work remains visible."""
from dataclasses import dataclass, field

from scholarly import ServiceError


@dataclass
class Source:
    id: str
    name: str
    role: str
    home: str
    transport: str
    usage: dict = field(default_factory=dict)
    implementation: str = "pending"
    verification: str = "not_recorded"
    capabilities: tuple[str, ...] | None = None

    def summary(self):
        return {"id": self.id, "name": self.name, "role": self.role, "transport": self.transport,
            "implementation": self.implementation, "verification": self.verification,
            "capabilities": list(self.capabilities) if self.capabilities is not None else ["source_guide", "search", "fetch", "export"] if self.implementation == "partial" else []}


ROWS = [
    ("mathscinet", "MathSciNet", "authenticated_search", "https://mathscinet.ams.org/", "playwright"),
    ("wos", "Web of Science Core Collection + CPCI", "authenticated_search", "https://www.webofscience.com/", "playwright"),
    ("scopus", "Scopus", "authenticated_search", "https://www.scopus.com/", "playwright"),
    ("acm-dl", "ACM Digital Library", "authenticated_search", "https://dl.acm.org/", "under_investigation"),
    ("ieee-xplore", "IEEE Xplore / IEL", "authenticated_search", "https://ieeexplore.ieee.org/", "playwright"),
    ("pqdt", "PQDT Global", "authenticated_search", "https://search.proquest.com/pqdtglobal", "under_investigation"),
    ("zbmath", "zbMATH Open", "public_primary", "https://zbmath.org/", "api"),
    ("arxiv", "arXiv", "public_primary", "https://arxiv.org/", "api"),
    ("dblp", "DBLP", "public_primary", "https://dblp.org/", "api"),
    ("dblp-kg", "DBLP Knowledge Graph", "public_primary", "https://sparql.dblp.org/", "api"),
    ("eccc", "ECCC", "public_primary", "https://eccc.weizmann.ac.il/", "under_investigation"),
    ("drops", "DROPS / LIPIcs", "public_primary", "https://drops.dagstuhl.de/", "under_investigation"),
    ("theory-of-computing", "Theory of Computing", "public_primary", "https://theoryofcomputing.org/", "under_investigation"),
    ("crossref", "Crossref", "supplement", "https://www.crossref.org/", "api"),
    ("crossmark", "Crossmark", "supplement", "https://www.crossref.org/services/crossmark/", "api"),
    ("openalex", "OpenAlex", "supplement", "https://openalex.org/", "api"),
    ("semantic-scholar", "Semantic Scholar", "supplement", "https://www.semanticscholar.org/", "api"),
    ("opencitations", "OpenCitations", "supplement", "https://opencitations.net/", "api"),
    ("unpaywall", "Unpaywall", "supplement", "https://unpaywall.org/", "api"),
    ("core", "CORE", "supplement", "https://core.ac.uk/", "under_investigation"),
    ("project-euclid", "Project Euclid", "supplement", "https://projecteuclid.org/", "under_investigation"),
    ("eudml", "EuDML", "supplement", "https://eudml.org/", "api"),
    ("numdam", "Numdam", "supplement", "https://www.numdam.org/", "api"),
    ("mathlib", "Mathlib", "formalization", "https://github.com/leanprover-community/mathlib4", "api"),
    ("afp", "Archive of Formal Proofs", "formalization", "https://isa-afp.org/", "under_investigation"),
    ("math-comp", "Mathematical Components", "formalization", "https://github.com/math-comp/math-comp", "api"),
    ("github", "GitHub", "code_data", "https://github.com/", "api"),
    ("zenodo", "Zenodo", "code_data", "https://zenodo.org/", "api"),
    ("figshare", "Figshare", "code_data", "https://figshare.com/", "api"),
    ("software-heritage", "Software Heritage", "code_data", "https://www.softwareheritage.org/", "api"),
    ("ams", "AMS publications", "fulltext", "https://www.ams.org/", "under_investigation"),
    ("cambridge", "Cambridge University Press", "fulltext", "https://www.cambridge.org/", "under_investigation"),
    ("de-gruyter", "De Gruyter Brill", "fulltext", "https://www.degruyterbrill.com/", "under_investigation"),
    ("jstor", "JSTOR", "fulltext", "https://www.jstor.org/", "under_investigation"),
    ("oxford", "Oxford University Press", "fulltext", "https://academic.oup.com/", "under_investigation"),
    ("science-direct", "ScienceDirect", "fulltext", "https://www.sciencedirect.com/", "playwright"),
    ("springer", "Springer Nature", "fulltext", "https://link.springer.com/", "playwright"),
    ("taylor-francis", "Taylor & Francis", "fulltext", "https://www.tandfonline.com/", "under_investigation"),
    ("wiley", "Wiley", "fulltext", "https://onlinelibrary.wiley.com/", "under_investigation"),
    ("aip", "AIP", "fulltext", "https://pubs.aip.org/", "under_investigation"),
    ("aps", "APS", "fulltext", "https://journals.aps.org/", "under_investigation"),
    ("iop", "IOP", "fulltext", "https://iopscience.iop.org/", "under_investigation"),
    ("siam", "SIAM", "fulltext", "https://epubs.siam.org/", "under_investigation"),
    ("knu-fric", "KNU FRIC", "fulltext", "https://kudos.knu.ac.kr/", "under_investigation"),
    ("individual-subscription", "KNU 개별 구독 저널 목록", "holdings_catalogue", "https://kudos.knu.ac.kr/", "playwright"),
    ("society-journal", "학회·저널 공식 사이트", "open_category", "", "target_dependent"),
    ("author-repository", "저자·기관 공개본", "open_category", "", "target_dependent"),
    ("general-web", "일반 웹 후보 발견", "discovery", "", "target_dependent"),
]

SOURCES = {row[0]: Source(*row) for row in ROWS}
SOURCES["aps-institutional"] = Source("aps-institutional", "APS 기관 구독 접근", "fulltext", "https://journals.aps.org/", "playwright")
SOURCES["mathscinet"].implementation = "partial"
SOURCES["wos"].implementation = "partial"
SOURCES['dblp-kg'].implementation='partial'
SOURCES['dblp-kg'].usage={
    'search':'query는 SPARQL SELECT문이다. 기본 접두사는 PREFIX dblp: <https://dblp.org/rdf/schema#>로 선언한다. 원 질의를 보존하고 도구 start/limit를 가장 바깥의 OFFSET/LIMIT로 적용한다. 쿼리 최상위에 LIMIT/OFFSET을 직접 쓰지 않는다. 하위 SELECT의 범위는 허용한다. 연속 페이지에 재현 가능한 순서가 필요하면 문헌 ID 등의 ORDER BY를 지정한다.',
    'fields':{'dblp:title':'문헌 제목','dblp:yearOfPublication':'발행연도','dblp:doi':'https://doi.org/DOI 형태의 IRI','dblp:authoredBy / dblp:editedBy':'저자·편집자 관계','dblp:hasSignature':'순서·역할이 있는 작성자 표지','dblp:publishedInStream':'저널·학회 시리즈','dblp:omid':'이 지식 그래프 안의 OpenCitations 식별자'},
    'operators':'WHERE의 triple pattern과 FILTER, OPTIONAL, UNION, VALUES, GROUP BY, HAVING, ORDER BY를 사용한다. 예: FILTER(REGEX(?title, "natural proofs", "i")). yearOfPublication은 xsd:gYear다. 연도 수치 조건은 PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>를 선언하고 FILTER(xsd:integer(STR(?year)) >= 2020)처럼 명시적으로 변환한다. 자료원 변경을 일으키는 SERVICE와 FROM은 거부한다. 현재 SELECT만 연결했으며 ASK·CONSTRUCT·UPDATE는 받지 않는다.',
    'exports':'json은 변수별 RDF binding 배열이다. 값의 type/value/datatype/xml:lang과 미결합 변수의 부재를 그대로 유지한다. native는 원 SPARQL 결과 JSON이다. csv·tsv는 같은 범위의 원 다운로드이며 각각 W3C가 정의한 Accept text/csv·text/tab-separated-values로 요청하고 값과 행을 대조한다. application/csv·application/tab-separated-values는 이 결과 형식의 표준 미디어 타입이 아니다. CSV는 표준상 RDF 자료형과 빈 문자열/미결합의 구별을 잃을 수 있다. 원 TSV가 gYear를 정수로 출력하는 경우처럼 JSON의 RDF term과 달라지면 partial/export_term_mismatch와 source_export의 원 파일을 반환하며 파일을 고쳐 쓰지 않는다. tsv_exact는 이미 받은 JSON binding에서 SPARQL 1.1 TSV를 별도로 생성해 datatype·언어·미결합을 보존하고, 산출물에 JSON evidence ref와 generated_lossless_tsv 역할을 기록한다. TSV 검증은 수치가 같더라도 숫자·Boolean 원 문자열이나 자료형이 다르면 불일치로 보고한다. RDF 1.1의 plain string과 xsd:string, 언어 태그 대소문자는 같은 항으로 대조한다. tsv_exact 생성은 JSON의 원 문자열·명시 자료형·언어 철자를 그대로 쓴다. 생성·저장 실패는 이미 받은 JSON과 함께 partial로 반환한다. tsv와 tsv_exact는 모두 extract로 줄 구간을 읽는다.',
    'fetch':'DBLP key·/rec/ URL·DOI는 일치하는 문헌의 RDF statement를 전건 회수한다. DOI 조회·대조는 대소문자를 구별하지 않으며 원 RDF DOI 표기는 유지한다. predicate/object의 RDF term을 유지한다. 이름은 제목의 대소문자 구별 없는 부분 문자열 후보로 반환한다. metadata·export·supplementary는 같은 문헌의 statements이며 연결된 저자·서명·인용 문헌을 재귀 회수하지 않는다. 여러 문헌이 같은 DOI에 연결되면 selection_required다. 초록·전문은 이 서지 지식 그래프의 제공 대상이 아니다.',
    'limits':'options는 비운다. 별도 키·계정·이메일 없는 DBLP 운영기관의 공개 API다. start 0부터, 구현 limit 1..1000. 전체 일치 건수는 별도로 세지 않아 total=null이다. provider_result_size는 원 제한 질의의 보고값이며 전체 검색 건수로 해석하지 않는다. 꽉 찬 마지막 페이지 뒤 빈 페이지를 읽을 수 있다. DBLP DOI 매핑 부재는 모든 자료원에서의 부재가 아니다. 기존 dblp 검색 API 실패 뒤 자동 전환하지 않으며 호출자가 dblp-kg를 선택한다.',
    'examples':[{'tool':'search','arguments':{'source':'dblp-kg','query':'PREFIX dblp: <https://dblp.org/rdf/schema#> SELECT ?publ ?title WHERE { ?publ dblp:title ?title . FILTER(REGEX(?title, "natural proofs", "i")) } ORDER BY ?publ','start':1,'limit':2,'export':'csv'}},{'tool':'fetch','arguments':{'source':'dblp-kg','target':'10.1006/jcss.1997.1494','parts':['metadata','supplementary']}}],
    'official':['https://sparql.dblp.org/','https://github.com/dblp/kg/wiki/dblp-KG-Tutorial','https://www.dagstuhl.de/en/dblp/news/2024/introducing-our-public-sparql-query-service'],
}

SOURCES["scopus"].implementation = "partial"
SOURCES["scopus"].usage = {
    "search": "KUDOS → 학술DB → Scopus → Advanced document search. query는 고급검색식 그대로 제출한다. 예: TITLE(\"P versus NP\"), TITLE-ABS-KEY(\"natural proofs\") AND PUBYEAR > 2020. AND·OR·AND NOT, 괄호, 큰따옴표 구문, 중괄호 정확 구문, W/n·PRE/n 근접 연산자는 Scopus 문법을 따른다.",
    "fields": {"TITLE": "제목", "ABS": "초록", "KEY": "키워드", "TITLE-ABS-KEY": "제목·초록·키워드", "AUTHLASTNAME": "저자 성", "AFFIL": "소속", "PUBYEAR": "발행연도", "DOI": "DOI", "EID": "Scopus 문서 ID"},
    "options": {"sort":"newest, oldest, cited-highest, cited-lowest, relevance, author-asc, author-desc, source-title-asc, source-title-desc. 생략하면 원 UI 기본 정렬을 사용한다.",
                "facet_filters":"분야별 {include:[정확한 표시 이름],exclude:[정확한 표시 이름]} 객체. 같은 분야의 include는 OR이며 다른 분야는 함께 제한한다. 같은 이름을 include와 exclude에 동시에 넣지 않는다.",
                "facet_group":"아래 분야의 현재·확장 후보를 facet_candidates artifact로 조회한다. 이 관측의 Scopus 후보 UI에는 문자열 검색 제어가 없어 facet_query를 받지 않는다."},
    "facet_fields":["year","subject_area","document_type","language","keyword","country_territory","source_type","source_title","author_name","publication_stage","affiliation","funding_sponsor","open_access"],
    "limits":"start는0부터, limit는1..1000이다. primary 문서의 전체 건수·페이지·고유 EID를 대조하고 preprint 별도 집계를 섞지 않는다. 선택 제어의 분야·값·include/exclude와 누적 조건, 지정한 정렬을 원 요청과 대조한다. 원 응답이 중간에 실패하거나 문헌이 중복되면 확보한 앞부분과 재개 위치를 partial로 보존한다. 기본 질의가0건이면 필터 제어를 기다리지 않는다.",
    "exports": "json은 UI가 받은 원 문헌 필드, csv는 같은 필드의 기계적 직렬화다. 중첩값은 JSON 셀이다. facet-counts는 개인 계정 없이 제공되는 Export filter counts 원 CSV이며 선택한 start/limit 문헌 창이 아니라 현재 전체 검색식의 분야별 후보·건수다. extract(export.ref)는 facet_group/label/count 행을, selection=raw는 설명문을 포함한 원 줄을 읽는다. 이 행 수는 문헌 수와 다르다. 원 응답과 내려받은 파일·현재 전체 검색식이 일치하는지 검사한다. 오류 때 records·정제 source_export·이미 받은 원 응답을 보존한다. 문헌 native RIS·BibTeX의 별도 웹 계정 경로는 사용자 지시에 따라 보류하며 export_deferred를 반환한다.",
    "fetch": "EID(2-s2.0-숫자)·Scopus 문헌 URL·DOI로 색인의 서지·초록을 확보한다. 제목은 TITLE 후보 검색이다. supplementary는 현재 문헌의 References·Cited by 탭 목록이며 각 references/citations.artifact를 extract로 읽는다. 참고문헌은 text, 피인용 문헌은 itemTitle 등 원 필드를 보존한다. 출판사 원문은 별도 source로 선택한다.",
    "relationships": "참고문헌의 원 10건 페이지를 순회하고 시작 위치·전체 건수·실제 수신분을 대조한다. EID가 없는 참고문헌도 버리지 않는다. 피인용 응답은 탭 건수와 배열을 대조한다. 검색 요약의 search_metadata_count와 문헌 탭의 total이 다를 수 있어 별도로 보존한다. 일부 실패는 이미 회수한 관계 목록과 함께 표시한다.",
    "examples": [{"tool":"search","arguments":{"source":"scopus","query":"TITLE(\"P versus NP\")","options":{"sort":"cited-highest","facet_filters":{"document_type":{"include":["Article","Review"]},"language":{"include":["English"]}}},"limit":2,"export":"csv"}},
                 {"tool":"search","arguments":{"source":"scopus","query":"TITLE(\"P versus NP\")","limit":1,"export":"facet-counts"}}],
    "official": ["https://www.elsevier.com/products/scopus/search"],
}

SOURCES["mathscinet"].usage = {
    "search": "query는 MathSciNet 검색창의 검색식이다. 고급 필드 태그를 query 안에 쓴다. 기관 인증은 서버가 KUDOS 로그인 → 검색 → 학술DB → MathSciNet 바로가기로 처리한다.",
    "fields": {"au": "저자", "aur": "저자 또는 관련 인물", "ti": "제목", "r": "리뷰 텍스트", "j": "저널", "se": "총서", "pc": "주 MSC", "sc": "부 MSC", "mr": "MR 번호", "doi": "DOI", "rn": "리뷰어", "any": "전체 필드"},
    "operators": "고급 필드 행 사이는 AND, OR, NOT. 문자열·구문은 자료원의 의미대로 입력한다. 따옴표 없는 공백 질의는 정확한 제목 일치를 보장하지 않는다.",
    "options": {"kind":"publications(기본), citations(들어오는 인용), references(나가는 참고문헌)", "sort":"newest(기본), oldest, relevance, citations, author-count, paging", "citation_basis":"kind=citations에서만 references(기본) 또는 reviews. 원 From References와 From Reviews를 구별한다.",
                "facet_filters":"publications 전용. 아래 분야별 {include:[정확한 표시 이름],exclude:[정확한 표시 이름]} 객체다. 같은 분야의 값은 OR, exclude는 NOT, 서로 다른 분야는 함께 제한한다.",
                "facet_group / facet_query":"publications의 후보 조회다. facet_group을 지정하고 필요한 경우 facet_query로 원 후보를 검색한다. 검색 제어는 authors, institutions, primary_classifications, journals에서 제공된다. 후보는 facet_candidates.ref를 extract해 읽는다."},
    "facet_fields":["review_status","publication_type","authors","institutions","primary_classifications","journals","publication_years"],
    "facets":"초기 목록 밖의 이름도 원 후보 검색에서 정확한 전체 이름과 ID를 대조해 선택한다. 호출자는 내부 ID나 화면 제어를 만들지 않는다. 앞 필터 뒤 후보를 새 검색식에 맞춰 갱신하고 같은 OR 집합의 순서는 의미를 바꾸지 않는다. 기본 질의가0건이면 filter_state로 요청 필터를 적용하지 않았음을 명시한다.",
    "relationships":"kind=citations/references의 query는 MR 번호 또는 DOI다. DOI는 유일한 MR 후보와 원 BibTeX의 DOI를 대조한다. citations는 선택 문헌을 인용하는 원 검색 결과이며 basis=reviews의 화면 집계 control_total과 실제 결과 result_total이 다르면 둘 다 보존한다. references는 원 참고문헌 중 MR로 검색 가능한 고유 부분집합이다. 원 항목 수·MR occurrence·고유 MR·중복을 relation에 따로 두고 MR 없는 원 항목은 relation.source_page로 보존한다. start는0부터, 이 검색 도구의 limit는1..100이며 다음 start로 계속 조회한다. 원 페이지와 요청 창을 대조하고 네 원 인용 형식은 관계 결과에도 사용할 수 있다.",
    "examples": [{"tool": "search", "arguments": {"source": "mathscinet", "query": "ti:(\"P versus NP\")", "limit": 5, "export": "bibtex"}},
                 {"tool":"search","arguments":{"source":"mathscinet","query":"ti:(algebra)","options":{"facet_filters":{"journals":{"include":["Topology Appl."]}}},"limit":1}},
                 {"tool":"search","arguments":{"source":"mathscinet","query":"MR0463157","options":{"kind":"citations","citation_basis":"reviews"},"limit":1,"export":"bibtex"}},
                 {"tool":"search","arguments":{"source":"mathscinet","query":"MR2733384","options":{"kind":"references"},"start":4,"limit":2,"export":"endnote"}}],
    "limits": "검색 start는0부터, limit는1..100이며 반환된 next.start로 계속 조회한다. 검색 결과의 Article은 다른 출판사 자료일 수 있다. fetch는 MathSciNet 서지·리뷰·제공 요약·리뷰 PDF를 회수하며 Article을 다른 자료원에서 자동 확보하지 않는다. 리뷰와 논문 전문은 구별한다.",
    "export_formats": ["bibtex", "endnote", "amsref", "tex"],
    "fetch": "MR 번호·MathSciNet article 링크·DOI·이름을 지정한다. 이름은 제목 후보 목록이다. DOI는 원 검색이 유일한 MR 기록을 반환하고 그 원 BibTeX의 DOI가 일치할 때 해당 문헌을 조회한다. 확인되지 않으면 후보로 남긴다. metadata는 원 서지·리뷰 페이지이고 supplementary는 제공되는 Review PDF다. 논문 전문과 리뷰를 구별한다.",
    "exports": "fetch의 export.artifacts는 BibTeX·EndNote·AMSRef·TeX이며 기본 artifact는 BibTeX다. 검색 export에는 요청한 형식을 반환한다. 자료원이 형식화한 문자열을 빈 줄로 연결하며 다시 작성하지 않는다. 원 응답 순서 mr_order와 요청 순서 requested_mr_order를 보존한다. BibTeX MRNUMBER와 EndNote label도 응답의 MR 번호와 대조한다. 내보내기 실패 때 검색 레코드와 확보한 인용문을 보존한다.",
    "evidence": "2026-09-09 KUDOS 프록시 검색 입력·고급 필드·export 제어 실측. 다섯 도구의 실사용 검증은 별도 보고에 기록한다.",
}

SOURCES["wos"].usage = {
    "search": "query는 Web of Science Core Collection의 Query Builder 검색식이다. KUDOS의 Web of Science CPCI 바로가기로 같은 Core Collection에 기관 접속한다. Editions=All의 기관 이용 범위를 사용한다.",
    "fields": {"TS": "주제", "TI": "제목", "AB": "초록", "AU": "저자", "AI": "저자 식별자", "AK": "저자 키워드", "GP": "단체 저자", "ED": "편집자", "KP": "Keywords Plus", "SO": "발행물명", "DO": "DOI", "PY": "발행연도", "CF": "학회", "AD": "주소", "OG": "소속", "OO": "기관", "SU": "연구 영역", "WC": "WoS 분류", "IS": "ISSN/ISBN", "UT": "접근번호", "DOP": "발행일", "LD": "색인일", "ALL": "전체 필드"},
    "operators": "FIELD=(조건), AND·OR·NOT, 괄호와 큰따옴표 구문. * 등 와일드카드와 날짜 범위는 WoS 문법을 따른다. 예: TS=(\"circuit lower bounds\") AND PY=(2020-2025). 세션 #번호 결합은 다른 호출에서 같은 세션을 보장하지 않으므로 독립 검색식으로 전달한다.",
    "options": {"kind":"publications(기본) 또는 citations. 두 종류 모두 아래 정렬을 지원한다. citations의 기본 date-descending은 date-newest의 호환 별칭이다. edition·facet 조건은 publications 전용이다.",
                "sort":"relevance, date-newest, date-oldest, citations-highest, citations-lowest, recently-added, usage-all-time, usage-180-days; conference-title/first-author/publication-title/document-title에 -asc 또는 -desc; background-highest, basis-highest, support-highest, differ-highest, discuss-highest. 마지막 다섯 값은 자료원이 분류한 인용 맥락의 정렬이다.",
                "editions":"SCI-EXPANDED, SSCI, AHCI, CPCI-S, CPCI-SSH, ESCI 중 비어 있지 않은 이름 배열. 생략하면 현재 기관의 전체 선택을 사용한다.",
                "facet_filters":"필터 분야 이름을 현재 표시 이름 배열에 대응시킨 객체. 예: {publication_titles:[\"COMPUTATIONAL COMPLEXITY\"],languages:[\"English\"]}. 한 분야 안의 값은 OR, 서로 다른 분야는 AND로 좁힌다.",
                "facet_group / facet_query":"한 분야의 후보 조회. facet_group에 아래 분야를 지정하고, 필요하면 facet_query 문자열로 후보를 검색한다. 검색 결과 집합을 좁히는 필터와 구별한다. facet_candidates 목록의 각 ref를 extract해 label·count를 읽는다."},
    "facet_fields":["publication_years","document_types","researcher_profiles","wos_categories","citation_topics_meso","citation_topics_micro","sustainable_development_goals","wos_indexes","affiliations","affiliation_departments","publication_titles","languages","countries_regions","publishers","research_areas","open_access_types","funding_agencies","conference_titles","group_authors","book_series_titles","editors","editorial_notices"],
    "facets":"각 분야의 현재 제어·추가 후보·검색을 통해 정확한 이름을 대조한다. 모호하거나 현재 선택할 수 없는 값은 selection_required와 후보를 반환한다. Open Access detail의 Free to Read처럼 표시 이름과 내부 값이 다른 경우도 원 제어에서 결속하며 호출자는 내부 코드를 만들지 않는다. 기존 INDEX.VALUE의 facets 입력은 호환용으로 유지한다.",
    "relationships":"kind=citations의 query에는 WOS 접근번호·DOI·Full Record URL을 지정한다. 원 Citing Articles 요청의 부모 UT를 대조하고 start/limit·원 export로 들어오는 문헌을 회수한다. relation의 control_total은 문헌 인용 표지, result_total은 해당 기관 범위의 결과 수다. 둘은 다를 수 있다. fetch supplementary의 references는 원 CR과 outgoing 방향이고 citations는 incoming 첫20건·전체 건수·다음 start다. 나머지는 같은 UT의 kind=citations 검색으로 요청한다.",
    "fetch": "WOS:접근번호·DOI·Web of Science full-record URL을 지정한다. 제목은 TI 구문 검색 후보와 selection_required를 반환하며 선택한 accession/DOI로 다시 요청한다. 전체 서지·제공되는 초록·인용문헌을 해당 색인에서 회수한다. 원 Full Record에 AB가 없으면 abstract는 not_found다. 논문 전문은 해당 출판사를 별도 source로 지정한다.",
    "exports": "기본 JSON 레코드는 Full Record and Cited References 텍스트 export를 손실 없이 파싱한다. plain은 같은 원파일. ris·bibtex·excel·tsv·html은 해당 native export의 Full Record이며 실제 제공 필드가 다를 수 있다.",
    "limits": "start는 0부터, limit는 1..1000. 큰 결과를 화면 카드 개수로 세지 않고 자료원의 count와 요청 범위의 export를 대조한다. 원 tags는 records의 fields 아래 소문자 키·원 줄 배열로 보존한다. cr은 인용문헌, ab는 초록, ut는 접근번호다.",
    "examples": [{"tool":"search","arguments":{"source":"wos","query":"TI=(\"P versus NP\")","options":{"editions":["CPCI-S"],"sort":"date-newest"},"limit":2,"export":"plain"}},
                 {"tool":"search","arguments":{"source":"wos","query":"TI=(\"P versus NP\")","options":{"facet_group":"publication_titles","facet_query":"Computational"},"limit":1}},
                 {"tool":"search","arguments":{"source":"wos","query":"TI=(\"P versus NP\")","options":{"facet_filters":{"publication_titles":["COMPUTATIONAL COMPLEXITY"],"languages":["English"]}},"limit":1}},
                 {"tool":"search","arguments":{"source":"wos","query":"WOS:000269418800023","options":{"kind":"citations"},"limit":2,"export":"plain"}}],
    "official": ["https://webofscience.help.clarivate.com/en-us/Content/advanced-search.html", "https://clarivate.libguides.com/webofscienceplatform"],
}

SOURCES["eccc"].transport = "playwright"
SOURCES["eccc"].implementation = "partial"
SOURCES["eccc"].usage = {
    "search": "query를 ECCC의 검색창에 그대로 제출한다. 현재 UI는 하나의 검색어 입력을 제공한다. options는 비운다. 원 검색의 중복 행과 snippet을 보존하며 자동으로 문헌을 합치지 않는다.",
    "fetch": "TRyy-nnn 또는 보고서 링크. TRyy-nnnrN 또는 revision/N/download 링크로 판본을 고정한다. 판본 생략 시 실제 페이지의 가장 높은 revision을 선택하고 정확한 번호와 다른 판본 목록을 반환한다. r0은 최초 보고서다. 이름은 원 일반 검색의 후보와 selection_required로 반환하며 결과를 제목 일치나 특정 판본으로 자동 확정하지 않는다. 형식이 잘못된 TRyy- 식별자는 이름으로 바꾸지 않는다.",
    "exports": "json은 기계 추출 레코드, html은 실제 검색 페이지다. 저자 초록과 원문 PDF는 fetch에서 지정 판본별로 확보한다.",
    "limits": "start 0부터, limit 1..1000. 전체 원 검색 페이지와 수신 레코드는 all_records로 보존한다. 서비스가 전체 색인의 검색 건수를 별도로 주지 않아 total은 null이고 stored_total은 보존한 행 수다. query 결과의 snippet은 abstract로 표시하지 않는다.",
    "examples": [{"tool": "search", "arguments": {"source": "eccc", "query": "natural proofs", "limit": 2}}, {"tool": "fetch", "arguments": {"source": "eccc", "target": "TR26-008r1", "parts": ["metadata", "abstract", "fulltext"]}}],
    "official": ["https://eccc.weizmann.ac.il/", "https://eccc.weizmann.ac.il/report/2026/008/"],
}

SOURCES["acm-dl"].transport = "playwright"
SOURCES["acm-dl"].implementation = "partial"
SOURCES["acm-dl"].usage = {
    "search": "query는 선택한 field 안의 ACM 검색어다. 검색어와 일반 검색 행 사이는 기본 AND다. 다른 field 사이의 OR·NOT이나 괄호 결합은 query를 비우고 options.expression에 원 검색식을 지정한다. Boolean 연산자는 대문자 AND·OR·NOT을 사용하며 서버가 입력의 대소문자를 바꾸지 않는다. 구문은 짝이 맞는 곧은 또는 굽은 큰따옴표로 감싼다. 작은따옴표는 구문 검색이 아니다. *는 여러 글자, ?는 한 글자 와일드카드이며 단어 첫머리나 따옴표 구문 안에 쓰지 않는다. 특수문자를 문자 그대로 찾으려면 ACM 문법에 따라 역슬래시로 이스케이프한다.",
    "fields": {"AllField": "Anywhere", "Title": "제목", "ContentGroupTitle": "발행물명", "ContribAuthor": "저자", "Abstract": "초록", "Fulltext": "전문", "Affiliation": "저자 소속", "Keyword": "저자 키워드", "ConferenceLocation": "학회 장소", "ConferenceSponsor": "학회 후원자", "Contrib": "이름", "PubIdSortField": "ISBN/ISSN", "DOI": "DOI"},
    "options": {"field": "위 필드 이름. 기본 AllField", "fields": "추가 {field,value} 배열. 일반 field 행은 기본 AND로 결합",
                "expression": "query는 빈 문자열로 두고 ACM Edit Query 원식을 지정한다. 예: (Title:(algebra) OR Abstract:(complexity)). field/fields와 병용하지 않는다. 날짜·collection·constraint·facet·sort는 함께 지정할 수 있다. 입력식을 그대로 제출하고 원 AllField 검색식과 일치하는지 대조한다.",
                "collection": "fulltext는 ACM Full-Text Collection, guide는 Guide to Computing Literature",
                "from_year,to_year,from_month,to_month": "발행 날짜의 사용자 지정 범위. 월에는 대응 연도가 필요하며 역전된 범위는 거부한다.",
                "sort": "EpubDate_asc, EpubDate_desc, downloaded, cited",
                "constraint": "{field,operator,values} 한 범주 행. field는 SeriesKey, Artifact, Funding, CCS, PrimaryCCS, PublisherRaw. operator는 And/Or/Nor, values는 현재 자동완성의 정확한 이름 배열이다. 연산자는 범주 안 값들에 적용하며 일반 검색 field와는 AND로 결합한다.",
                "facets": "순서 있는 {field,value,panel?} 배열. 현재 후보에서 field/value를 복사한다. field는 SeriesKey, ConceptID, ContentItemType, SpecifiedLevelConceptID, SponsorAcronymRaw, content. 같은 field가 여러 의미 패널에 있으면 후보의 panel로 구별한다. 단일 facet 객체도 사용할 수 있다."},
    "fetch": "ACM DOI·레코드 key·문헌 또는 PDF 링크를 지정한다. 이름은 제목 후보를 반환한다. 10.5555처럼 DOI 모양인 Guide key를 실제 등록 DOI로 단정하지 않는다. 원 CSL key·레코드 URL·제목을 대조하고 제공되는 DOI도 확인한다. 원 논문과 재수록본은 별도 식별자·연도로 보존하며 같은 ACM 문헌의 실제 파일 제어를 사용한다.",
    "exports": "json은 검색 행과 BibTeX 필드를 함께 보존한다. bibtex·endnote·acmref는 실제 UI 응답의 원 서지와 자료원이 제공한 CSL 스타일·처리기로 생성한다. 서지 응답과 처리기 참조도 보존한다. 넓은 검색에서 한 페이지의 결과와 요청한 선택 범위는 구별한다.",
    "supplementary":"문헌의 보충자료 목록에서 원 파일명·설명·DOI를 대조하고 파일을 회수한다. files의 artifact로 ZIP 등을 읽고 내부 파일을 selection으로 꺼낸다. 기존 참고문헌 문맥은 원 source_page에 유지한다. 인식하지 못한 다른 첨부 레이아웃은 source_page로 남긴다.",
    "fulltext_html":"같은 식별자의 원 HTML 전문 제어가 있으면 article의 bodymatter·backmatter를 보존한다. fulltext_html.math.artifact에는 span.core-tex의 원 TeX를 순서대로 보존하며 extract로 읽는다. HTML 제어가 없는 문헌을 HTML 전문으로 표시하지 않는다. PDF는 기존 fulltext 항목이다.",
    "facets":"현재 후보는 값·이름·건수·그룹·패널을 포함한다. 연속 선택에서는 이전 조건을 유지하는 원 링크만 따라가며 각 단계의 조건 추가를 대조한다. 모호하거나 현재 원 제어로 확인되지 않는 값은 selection_required다.",
    "limits": "KUDOS 기관 프록시와 기본 Firefox를 사용한다. start 0부터, limit 1..1000. 일반 field 행의 AND는 기본값이며 ACM의 Edit Query에서는 서로 다른 field도 OR·NOT으로 결합할 수 있다. 범주 입력은 한 행의 복수 값을 지원한다. 원 export가 추가 식별자를 포함하면 검색 행·원 CSL source_export·실제 포함 범위를 partial로 보존한다. 추가 자료의 관계를 추정하거나 요청 범위에 조용히 합치지 않는다. 파일별 실패는 확보한 metadata와 다른 성공 구성요소를 유지한다.",
    "examples": [{"tool":"search","arguments":{"source":"acm-dl","query":"","options":{"expression":"(Title:(algebra) OR Abstract:(complexity))"},"limit":2,"export":"bibtex"}},
                 {"tool":"search","arguments":{"source":"acm-dl","query":"algebra","options":{"field":"Title","constraint":{"field":"SeriesKey","operator":"Or","values":["Journal of the ACM","Communications of the ACM"]}},"limit":1,"export":"bibtex"}},
                 {"tool":"fetch","arguments":{"source":"acm-dl","target":"10.1145/3831699","parts":["metadata","fulltext","fulltext_html"]}},
                 {"tool":"fetch","arguments":{"source":"acm-dl","target":"10.1145/800157.805047","parts":["metadata","abstract","fulltext"]}}],
    "official": ["https://dl.acm.org/search/advanced"],
}

API_USAGE = {
    "crossref": {
        "search": "query는 관련도 검색어다. Boolean 필드 검색식으로 해석하지 않는다. 제목·저자 등은 options의 query.title, query.author, query.bibliographic, query.container-title, query.affiliation으로 지정한다.",
        "options": {"filter": "쉼표로 조건 결합. from-pub-date:YYYY-MM-DD,until-pub-date:YYYY-MM-DD,type:journal-article,has-abstract:true,has-full-text:true,doi:DOI,issn:ISSN 등", "sort": "relevance,published,created,updated,is-referenced-by-count 등", "order": "asc 또는 desc", "select": "호출자가 원하는 원 필드 이름의 쉼표 목록", "facet": "자료원이 지원하는 집계 필드:건수"},
        "fetch": "DOI 또는 https://doi.org/DOI. 이름은 query.title 후보 검색과 selection_required를 반환한다. 서지·등록 초록·참고문헌·relation·정정 정보를 원 필드로 보존한다. export를 요청하면 여덟 원 변환 형식을 artifacts에 보존한다. 전문 링크는 남기되 해당 출판사를 자동 방문하지 않는다.",
        "exports": "검색 export는 json/native, bibtex, ris, csl-json, plain, rdf, turtle, unixref, unixsd. 각 문헌의 Crossref transform 응답을 보존한다. plain에만 options.citation_style(예: apa), options.locale(예: en-US)을 적용한다. select로 검색 필드를 좁히면 원 인용문 export에 필요한 DOI를 포함한다. 변환 형식은 Crossref 원 등록 메타데이터의 모든 구별을 보존하지 않을 수 있으므로 원 JSON도 유지한다.",
        "limits": "limit 1..1000. 깊은 페이지는 cursor='*'로 시작하고 next.cursor를 사용한다. native 인용문은 문헌마다 별도 요청하므로 큰 검색 창은 그만큼 요청 수가 늘어난다. XML·RDF·CSL은 문헌별 artifacts, BibTeX·RIS·plain·Turtle은 결합 ref도 반환한다. 일부 실패는 원 검색 결과와 함께 표시한다.",
        "examples": [{"tool": "search", "arguments": {"source": "crossref", "query": "P versus NP", "options": {"filter": "from-pub-date:1970-01-01"}, "limit": 2}}, {"tool": "fetch", "arguments": {"source": "crossref", "target": "10.1145/321250.321251", "parts": ["metadata"]}}],
        "official": ["https://www.crossref.org/documentation/retrieve-metadata/rest-api/", "https://api.crossref.org/swagger-ui/index.html"]},
    "arxiv": {
        "search": "필드 태그 ti(제목),au(저자),abs(초록),cat(분류),co(주석),jr(저널),rn(보고번호),id(식별자),all(전체)을 쓴다. AND,OR,ANDNOT와 괄호로 결합하며 구문은 큰따옴표로 묶는다. 예: cat:cs.CC AND ti:\"circuit lower bounds\".",
        "options": {"sort_by": "relevance,lastUpdatedDate,submittedDate", "sort_order": "ascending,descending"},
        "fetch": "arXiv ID 또는 abs/pdf/html/src 링크. 이름은 제목 구문 검색 후보다. vN을 주면 그 판본, 생략하면 응답의 정확한 vN을 사용한다. fulltext는 기본 PDF이며 html·src 파일 URL을 지정하면 지정한 형식을 회수한다. supplementary는 같은 판본의 원 제출물이다. HTML을 PDF로 대체하지 않는다.",
        "limits": "limit 1..2000, start는 0부터. 호출 간 최소 3초. 검색 native export는 Atom, json은 추출 레코드. PDF 쪽, HTML CSS, source archive의 파일 목록·개별 파일·TeX 줄을 extract로 읽는다. 소스나 HTML 제공 여부는 판본마다 다르며 미제공과 접근 오류를 구별한다.",
        "examples": [{"tool": "search", "arguments": {"source": "arxiv", "query": "ti:\"P versus NP\"", "limit": 2}}],
        "official": ["https://info.arxiv.org/help/api/user-manual.html"]},
    "dblp": {
        "search": "대소문자를 구별하지 않는 접두어 검색이다. 공백은 AND, |는 OR이며 단어 뒤 $는 정확한 단어를 지정한다. 제목·저자·venue·연도 등 DBLP 검색 색인의 텍스트를 대상으로 한다.",
        "options": {}, "fetch": "journals/…·conf/…·books/… 등의 DBLP key나 /rec/ 링크는 원 XML의 key를 대조해 조회한다. 이름은 원 검색의 후보를 selection_required로 반환하므로 호출자가 고른다. metadata는 원 필드·속성을 구조화하고 native_metadata는 원 XML이다. 초록·논문 전문은 이 서지 색인의 제공 대상이 아니다.",
        "exports": "search의 export는 json/native 외에 bibtex·ris·xml·ntriples·turtle·rdf·plain을 받는다. 선택된 각 레코드의 원 파일을 export.artifacts로 제공한다. fetch parts=export는 7개 원 형식을 반환한다. XML·BibTeX·RIS·RDF의 문헌 식별자와 plain의 제목을 대조하고 일부 형식 실패 때 받은 파일과 metadata를 유지한다. BibTeX/RIS는 서지 필드, XML/RDF-XML은 XML 요소, Turtle/N-Triples/plain은 원 텍스트 줄을 extract한다.",
        "limits": "공식 검색 API의 limit 1..1000을 지원한다. 현재 원 응답이100건씩 반환하면 f를 이어 요청 범위를 채운다. start와 원 @first·@sent·total 및 문헌 key를 대조하며, 다음 페이지 실패 때 받은 레코드와 errors·next를 partial로 보존한다. 여러 원 응답은 native_pages에 있고 export=native의 export.artifacts에서 각각 추출한다. 검색어의 공백은 %20, 실제 +는 %2B로 직렬화한다. 연속 요청의 제한을 줄이기 위해 클라이언트가 최소 6.1초 간격을 두며, 이는 자료원이 보장한 고정 한도나 오류 해소 보장이 아니다. Anubis의 metarefresh 확인은 원 Refresh 헤더 또는 meta 태그의 대기 시간을 지켜 같은 API 클라이언트에서 처리한다. 확인 주소·원 검색 URL·일회성 값의 대응을 검사하며 쿠키와 확인 값은 내부에서만 사용한다. 다른 확인 방식이나 실패는 restricted다. 같은 운영기관의 공개 지식 그래프는 dblp-kg라는 별도 자료원으로 명시적으로 선택할 수 있다. 그 질의 문법은 SPARQL이며 이 검색식의 자동 대체가 아니다.",
        "examples": [{"tool": "search", "arguments": {"source": "dblp", "query": "P versus NP", "limit": 2}}],
        "official": ["https://dblp.org/faq/How+to+use+the+dblp+search+API.html", "https://dblp.org/faq/Which+mirror+sites+exist+for+dblp.html", "https://dblp.org/db/"]},
    "zbmath": {
        "search": "query는 zbMATH 문법이다. ti:제목,au:저자,cc:MSC,py:연도 등의 필드 태그와 & (AND), | (OR), 괄호를 사용한다. 구조화 검색에서는 query를 비우고 options에 Title, Author name, MSC, Year, DOI 등 표시 필드 이름과 값을 준다.",
        "options": {"Title": "문헌 제목", "Author name": "저자명", "MSC": "분류코드. * 접두사는 주분류로 한정", "Year": "연도 또는 2000-2020", "DOI": "DOI", "Document type": "j 저널논문,a 수록논문,b 책,p 프리프린트", "Database": "Zbl,JFM,eram,arxiv"},
        "fetch": "zbMATH ID·Zbl 번호·zbmath.org/ID·?q=an:번호·DOI를 지정한다. 제목은 후보 검색으로 반환한다. 문헌 ID와 DOI를 원 기록에서 대조한다. abstract는 원 editorial_contributions를 가리키며 review·summary 구분을 유지한다. 라이선스 충돌 안내문이면 restricted이며 저자 초록으로 표시하지 않는다. supplementary는 원 references 배열이며 반환한 selection으로 extract한다.",
        "limits": "limit 1..100, start는 0부터 임의 위치다. 경계를 넘으면 원 페이지를 더 읽고 요청 창만 반환한다. native export는 읽은 원 페이지들을 보존한다. 검색식과 구조화 필드는 한 요청에서 혼용하지 않는다. 추가 구조화 필드는 source_options 전체 목록에 있다.",
        "examples": [{"tool": "search", "arguments": {"source": "zbmath", "query": "", "options": {"Title": "P versus NP"}, "limit": 2}}],
        "official": ["https://api.zbmath.org/v1/openapi.json", "https://api.zbmath.org/"]},
    "openalex": {
        "search": "query는 works의 텍스트 검색이다. options.filter는 field:value를 쉼표로 결합하고 값의 |는 OR, !는 제외를 뜻한다. 날짜·종류·저자·source·인용 관계를 필터링한다.",
        "options": {"filter": "예: from_publication_date:2020-01-01,type:article 또는 cites:W…", "sort": "문헌 결과의 필드:asc/desc. 예: publication_date:desc", "select": "문헌 결과의 원 필드 이름 쉼표 목록", "group_by":"publication_year,type,authorships.institutions.id 등 원 집계 필드. sort/select와 함께 쓰지 않는다.","corpus":"생략 시 자료원의 기본 corpus. all은 추가 확장 기록을 포함하는 원 옵션"},
        "fetch": "W로 시작하는 ID, works/W… 또는 OpenAlex 문헌 URL·DOI를 지정한다. 이름은 텍스트 검색 후보를 반환한다. 원 ID와 canonical redirect를 대조하며 다른 canonical DOI로 해석되면 selection_required로 남긴다. abstract는 위치 색인을 검증해 단어 순서와 한 칸 공백으로 복원한 텍스트다. 누락·중복 위치를 추측해 채우지 않는다. 색인 원본은 metadata에 유지한다. supplementary는 referenced_works·related_works의 별도 배열이다. locations의 외부 전문은 자동 확보하지 않는다.",
        "limits": "limit 1..200, 일반 검색 start는 임의의 0 이상 정수다. 필요한 원 페이지를 합쳐 요청 창만 반환한다. cursor 사용 시 start=0으로 요청하고 결과 start=null은 커서로 정한 위치를 뜻한다. group_by는 기본부터 원 커서의 key 순서로 순회한다. total=null은 전체 그룹 수 미제공, matched_work_count는 문헌 수, page_group_count는 이번 페이지 그룹 수다. json/native export. 키 없는 공개 경로만 사용하며 429를 결과 없음으로 세지 않는다.",
        "examples": [{"tool": "search", "arguments": {"source": "openalex", "query": "\"natural proofs\"", "start":1,"limit": 2}},{"tool":"search","arguments":{"source":"openalex","query":"natural proofs","options":{"group_by":"publication_year"},"limit":2}},{"tool":"fetch","arguments":{"source":"openalex","target":"https://openalex.org/works/W2741809807","parts":["metadata","abstract","supplementary"]}}],
        "official": ["https://help.openalex.org/api/", "https://help.openalex.org/data/works/attributes/", "https://help.openalex.org/api/grouping/"]},
    "semantic-scholar": {
        "search": "kind=papers(기본)는 relevance-ranked plain-text 검색이며 Boolean 문법을 지원하지 않는다. kind=bulk는 원 Boolean 문법(+ AND, | OR, - NOT; 기본 모든 term 일치)·정렬·token cursor를 사용하는 별도 기능이며 papers의 fallback이나 동등한 결과 집합이 아니다. 한쪽의 성공은 다른 쪽의 성공을 뜻하지 않는다. 명시한 query는 바꾸지 않는다. bulk total은 정확한 일치 건수가 아니라 자료원이 제공한 추정치다. kind=references 또는 citations이면 query에 문헌 식별자를 주고 해당 관계의 범위를 조회한다.",
        "options": {"kind":"papers,bulk,references,citations", "year": "papers/bulk의 2020 또는 2020-2025", "fieldsOfStudy": "papers/bulk의 Computer Science,Mathematics 등", "publicationTypes": "papers/bulk의 JournalArticle,Conference,Review 등", "venue": "papers/bulk의 발행처 이름 쉼표 목록", "openAccessPdf": "papers/bulk에서 true는 공개 PDF 보유 조건, false/null은 그 필터 해제. 비공개 PDF만 고르는 뜻은 아니다.", "minCitationCount": "papers/bulk의 최소 인용 수", "publicationDateOrYear": "papers/bulk/citations의 날짜 또는 기간", "fields": "필요한 원 필드 이름 쉼표 목록. 예: title,authors,year,externalIds,url; 관계에는 contexts,intents,isInfluential도 제공된다.", "sort":"bulk 전용 field:order. paperId, publicationDate, citationCount와 asc/desc를 사용한다."},
        "fetch": "paperId·Semantic Scholar 문헌 URL·DOI·ARXIV:id·PMID:id·CorpusId:id는 공식 paper/batch에 한 ID를 보내 반환 정체성을 대조한다. 이름은 하이픈을 공백으로 바꾼 공식 title-match의 최대 한 후보를 반환하며, relevance 이름 검색과 동등한 후보 집합이 아니다. title-match는 후보 판독에 필요한 title,authors,year,externalIds,url,corpusId만 요청하고 원 이름을 보존하며 자동 선택하지 않는다. batch 공통 필드는 title,externalIds,corpusId다. metadata는 authors,year,url,openAccessPdf,publicationTypes,citationCount,referenceCount를, abstract는 abstract를, export는 citationStyles를 더한다. supplementary는 referenceCount와 별도 references 페이지를 사용해 나가는 참고문헌을 회수하고 부분 실패·원 count 차이를 남긴다. fulltext는 이 API에서 not_offered다. 들어오는 인용은 search kind=citations로 범위를 지정한다. openAccessPdf의 외부 호스트는 자동 방문하지 않는다.",
        "exports":"search의 json/native는 원 레코드·응답이다. papers의 bibtex와 fetch export는 citationStyles.bibtex 원 문자열이다. DOI가 양쪽에 있으면 DOI를 대조하고, 원 BibTeX가 DOI를 생략하면 metadata와 파싱된 BibTeX의 제목을 정규화해 대조한다. 잘못된 원 형식이나 다른 문헌은 고쳐 쓰지 않고 errors.source_export에 원 파일을 남긴다. 관계 페이지는 json/native로 보존한다.",
        "limits": "papers limit 1..100이며 start/next offset을 쓴다. bulk와 관계의 호출자 limit은 1..1000이다. bulk API에는 limit 파라미터가 없고 자료원이 호출당 최대1000건의 native batch와 선택적 token을 반환한다. MCP는 그 원 batch를 보존한 뒤 현재 native batch에서 최대 limit건을 반환한다. batch 경계에서는 남은 행만 반환하고 다음 cursor로 이어가므로 has_more=true여도 received가 limit보다 작을 수 있다. next.cursor는 같은 batch의 남은 행 또는 다음 native token에 결속된 불투명 artifact ref다. 같은 query·options·export에서만 cursor를 사용하고 start=0으로 둔다. 관계는 start/next offset을 쓴다. 관계 전체 건수는 제공되지 않아 total=null이다. 별도 자격 없는 요청은 모든 사용자가 공유하는 풀의 영향을 받고 혼잡 시 추가 제한될 수 있다. 클라이언트는 호출을 최소 1.05초 띄우지만 이는 429 회복 보장이 아니다. 429는 retryable 요청 제한으로 반환하고 Retry-After가 없으면 자동 재시도하지 않는다.",
        "examples": [{"tool":"search","arguments":{"source":"semantic-scholar","query":"natural proofs","limit":2}},{"tool":"search","arguments":{"source":"semantic-scholar","query":"natural + proofs","options":{"kind":"bulk","sort":"citationCount:desc"},"limit":2}},{"tool":"search","arguments":{"source":"semantic-scholar","query":"9a350a6787a5a79805ddb474feb256a5adfdbefb","options":{"kind":"citations"},"limit":2}}],
        "official": ["https://www.semanticscholar.org/product/api", "https://www.semanticscholar.org/product/api/tutorial", "https://api.semanticscholar.org/api-docs/snippets"]},
}
for identifier, usage in API_USAGE.items():
    SOURCES[identifier].usage = usage
    SOURCES[identifier].implementation = "partial"

MORE_API_USAGE = {
    "opencitations": {
        "search": "query에 DOI 또는 doi:…,pmid:…,omid:… 식별자를 넣는다. 키워드 검색 대신 지정 문헌의 인용 관계를 조회한다.",
        "options": {"direction": "references(기본)는 나가는 참고문헌, citations는 들어오는 인용. reference-count·citation-count는 각 관계 건수, citation은 OCI 한 건, venue-citation-count는 issn:번호의 저널 인용 건수", "filter": "필드:값 또는 필드:>값, 필드:<값. 정규식 값도 서비스 문법대로 사용. 여러 조건은 배열", "sort": "asc(필드) 또는 desc(필드)", "require": "값이 존재해야 하는 필드 또는 필드 배열", "json": "원 API의 array(\"구분자\",필드) 또는 dict(\"구분자\",필드,새필드,...) 변환. CSV에는 사용하지 않는다."},
        "fetch": "DOI·PMID·OMID의 metadata·export는 전체 나가는 참고문헌 관계다. supplementary는 들어오는 인용 관계다. oci:두숫자-두숫자 또는 https://opencitations.net/oci/번호는 그 인용 관계 한 건을 반환한다. 연결된 논문은 자동 확보하지 않는다.",
        "limits": "API가 반환한 전체 관계는 evidence로 보존하고 start·limit 창은 records에 둔다. json/native/csv export. csv의 export는 요청 구간을 원 필드로 재직렬화한 파일이고 native_export는 전체 원 CSV다. DOI 등이 가진 관계 0건은 논문 자체의 부재를 입증하지 않는다. 초록·전문은 이 인용 색인의 제공 대상이 아니다.",
        "examples": [{"tool": "search", "arguments": {"source": "opencitations", "query": "doi:10.1145/321250.321251", "options": {"direction": "references"}, "limit": 2}}],
        "official": ["https://api.opencitations.net/index/v2"]},
    "numdam": {
        "search": "query가 있으면 공개 웹의 원 검색 폼을 사용한다. 단어 사이에는 AND가 적용된다. 대소문자·발음 구별 기호는 무시하며 완전한 단어를 찾는다. *는 단어 일부, 따옴표는 구문 검색이다. query를 비우고 Date terms만 주면 원 웹 검색의 match-all `*`와 발행연도 조건을 결합한다. Date의 한쪽 경계를 생략하면 Numdam 원 문법의 `*`를 빈 경계에 명시해 열린 범위로 검색한다. query를 비우고 field·terms를 생략하면 OAI collection/date 열거다.",
        "options": {"field": "all(기본), author, title, references, fulltext. 빈 query의 발행연도 전용 검색은 all이거나 field를 생략해야 한다.", "terms": "추가 조건 배열. 각 원 검색 필드는 AND로 결합된다. {field,query,not:false} 형식이며 field에는 keywords도 허용한다. 날짜 조건은 {field:'date',from:'2012',until:'2012'}처럼 쓰고, from 또는 until 중 한쪽만 주면 그 이후 또는 그 이전의 열린 범위를 검색한다. 둘 다 생략할 수 없다. 어댑터는 빠진 경계를 Numdam의 공식 wildcard `*`로 직렬화한다. 발행연도만 검색할 때는 query를 비우고 Date 조건만 둔다. not:true는 그 조건을 제외한다. 요청한 조건마다 원 행을 생성하고 입력을 대조한다.", "set": "OAI 전용 collection 식별자", "from": "OAI 전용 메타데이터 갱신 시작일 YYYY-MM-DD", "until": "OAI 전용 갱신 종료일", "metadata_format": "OAI 전용 eudml-article2 또는 oai_dc"},
        "fetch": "Numdam native ID·oai:numdam.org:ID·DOI·Numdam 문헌/파일 URL을 사용한다. 이름은 제목 검색 후보와 selection_required를 반환한다. metadata는 원 JATS를 포함하며 abstract는 그 원 초록이다. fulltext는 PDF, supplementary는 같은 레코드의 대체 전문 DJVU다. export는 원 BibTeX·RIS·EndNote 세 파일이다.",
        "exports": "웹 검색은 json(기본), html/native(원 페이지), bibtex, ris, endnote. 선택한 창의 문헌별 원 인용문과 결합 파일을 보존하며 일부 실패는 문헌별 표시한다. OAI 검색은 json/native(XML). BibTeX·RIS·EndNote는 extract로 필드를 읽거나 selection=raw로 원 줄을 읽는다. EndNote fields는 원 태그 T·A·R 등을 유지한다.",
        "limits": "웹 start는 0부터, limit 1..100, 원 페이지 20건이며 페이지 경계도 조회한다. OAI 페이지 크기는 자료원이 정하며 모든 수신분을 보존한다. OAI 다음 페이지는 next.cursor. 검색 날짜와 OAI 갱신 날짜를 구별한다. DJVU 원 바이트도 보존한다. extract의 start/count로0부터 쪽을 선택해 원 텍스트 레이어를 읽고 render=true로 페이지 이미지도 얻는다. 텍스트가 비면 이미지를 반환한다. 별도 파일을 참조하는 indirect DJVU는 외부 파일을 자동으로 읽지 않고 해당 상태를 반환한다. 뒤쪽 판독 실패는 앞쪽 성공분과 next_start를 partial로 유지한다.",
        "examples": [{"tool": "search", "arguments": {"source": "numdam", "query": "complexity", "start": 19, "limit": 2, "export": "ris"}}, {"tool": "search", "arguments": {"source": "numdam", "query": "", "options": {"terms": [{"field": "date", "from": "2012"}]}, "limit": 2}}, {"tool": "search", "arguments": {"source": "numdam", "query": "", "options": {"terms": [{"field": "date", "from": "2012", "until": "2012"}]}, "limit": 2}}, {"tool": "search", "arguments": {"source": "numdam", "query": "\"Three complexity functions\"", "options": {"field": "title", "terms": [{"field": "date", "from": "2012", "until": "2012"}]}, "limit": 2, "export": "bibtex"}}, {"tool": "fetch", "arguments": {"source": "numdam", "target": "10.1051/ita/2011126", "parts": ["metadata", "abstract", "fulltext", "export", "supplementary"]}}],
        "official": ["https://www.numdam.org/help/", "https://www.numdam.org/metadata/", "https://gricad-gitlab.univ-grenoble-alpes.fr/mathdoc/ptf"]},
    "core": {
        "search": "query는 CORE 검색식이며 공식 Works GET /v3/search/works/를 호출한다. title:\"P versus NP\"처럼 필드를 지정하고 id:WORK_ID로 Work를 찾는다. Output ID는 별도 Output 검색의 ID이며 Work ID와 혼동하지 않는다. 원 검색 결과의 모든 필드를 보존한다.",
        "options": {"sort": "CORE 정렬 조건. 제공자가 거절한 조건은 오류로 반환한다."},
        "fetch": "CORE works 번호·CORE works URL을 지정하며 이름은 원 검색 후보와 selection_required를 반환한다. 응답의 works ID를 대조한다. abstract가 비어 있으면 not_found다. fullText가 실제 비공백 문자열 본문이면 indexed text artifact로 보존한다. 공백 또는 공개 API 안내문이고 work metadata의 download URL이 outputs 관계의 같은 output ID를 가리키면 그 CORE PDF를 회수하며, 실패하면 metadata와 파일 오류를 함께 보존한다. 명시 output API download URL과 core.ac.uk·fileserver-az·files01의 문서화된 파일 URL도 받는다. Legacy files01의404·timeout·connection·5xx만 같은 output의 현재 metadata로 한 번 재해결한다. 429·401·403·410, disabled·removed output은 재해결하지 않는다. 각 redirect에서 output ID와 CORE 파일 호스트를 대조하며 다른 저장소·sourceFulltextUrls·브라우저로 자동 전환하지 않는다. 파일 입력의 metadata/export는 PDF 내장 정보다.",
        "limits": "별도 자격 없는 공개 접근만 사용한다. limit 1..100, start는 0부터. 호출 간격 최소 2.1초. 429에서는 표준 Retry-After를 우선하고 없으면 CORE의 X-RateLimit-Retry-After를 actionable 값으로 반환한다. 성공 응답의 custom timestamp는 rate metadata로만 보존한다. json/native export.",
        "examples": [{"tool": "search", "arguments": {"source": "core", "query": "title:\"P versus NP\"", "limit": 2}}, {"tool": "fetch", "arguments": {"source": "core", "target": "399925820", "parts": ["metadata", "fulltext"]}}, {"tool": "fetch", "arguments": {"source": "core", "target": "https://api.core.ac.uk/v3/outputs/213561553/download", "parts": ["metadata", "fulltext"]}}, {"tool": "fetch", "arguments": {"source": "core", "target": "https://files01.core.ac.uk/download/pdf/287883846.pdf", "parts": ["metadata", "fulltext"]}}],
        "official": ["https://core.ac.uk/services/api", "https://api.core.ac.uk/docs/v3"]},
    "figshare": {
        "search": "query는 공개 Figshare search_for에 그대로 전달한다. articles(기본) 또는 collections를 검색한다. 이름 fetch는 후보 선택을 반환한다.",
        "options": {"kind":"articles 또는 collections", "order":"created_date,published_date,modified_date,views,shares,cites; articles에는 downloads도 가능", "order_direction":"asc,desc", "institution":"기관 ID", "group":"그룹 ID", "resource_doi":"연결 문헌 DOI", "doi":"레코드 DOI", "handle":"Handle", "published_since":"ISO 날짜", "modified_since":"ISO 날짜", "item_type":"articles 자료 유형 숫자", "project_id":"articles 프로젝트 ID", "collection_id":"현재 구성원 목록: query는 빈 문자열, 다른 필터 없이 사용"},
        "fetch": "article:ID 또는 숫자, collection:ID, 공개 Figshare URL·DOI를 사용한다. @N 또는 DOI .vN으로 버전을 고정한다. article:ID@N#file:ID는 그 파일만 선택한다. metadata·export는 JSON, abstract는 저자 초록으로 단정하지 않은 repository description이다. articles의 fulltext·supplementary는 원 파일이며 크기·MD5를 검증한다. collection supplementary는 버전을 생략하면 현재 구성원, @N 또는 .vN이면 그 판본의 구성원 참조 목록이다. 각 DOI나 article ID를 선택해 파일을 받는다.",
        "limits": "자격증명 없는 공개 경로만 사용한다. 요청 간격 1.05초. limit 1..1000, start는 0부터다. offset 5000 이후에는 원 page/page_size로 요청 범위를 선택한다. OpenAPI의 page 5000·page_size 1000 범위 안에서 처리하며 실제 거절은 오류로 보존한다. 원 페이지와 정확히 선택한 records의 범위는 native_pages로 구별한다. 전체 검색 건수는 제공되지 않아 total=null이다. json/native export. 과거 컬렉션 구성원은 OpenAPI에 없는 공식 웹 UI의 first-party GraphQL 경로이며 collection ID와 version을 결합한 필터, 판본 metadata articles_count, 응답 count를 대조한다. 검색 subset과 metadata count가 다르면 확보한 subset을 partial artifact로 보존한다. 단, 요청 판본이 current임을 REST metadata로 목록 조회 전후 모두 확인하고 DOI·count·ID 포함관계가 맞을 때만 문서화된 current REST 관계로 완성하며 검색 subset과 차집합도 별도 보존한다. 다른 current 판본으로는 대체하지 않는다. historical GraphQL에는 REST 5,000,000행 상한을 적용하지 않고 응답 count·cursor·ID 고유성으로 종료와 일관성을 검사한다. schema나 응답 오류는 partial/error다. 외부 is_link_only 파일은 selection_required이며 자동 방문하지 않는다. 파일은 현재 metadata의 정확한 Figshare downloader/file ID에 결속한다. 그 요청이 실제 지정한 알려진 S3 전송 호스트의 파일도 회수하고 제공된 크기·MD5를 대조한다. 이 허용은 현재 파일의 원 redirect에만 적용되며 임의 저장소 URL 조회를 허용하지 않는다. 404는 비공개 자료의 읽기 권한 부재도 포함할 수 있다.",
        "examples": [{"tool":"search","arguments":{"source":"figshare","query":"","options":{"collection_id":7956296},"limit":2}},{"tool":"fetch","arguments":{"source":"figshare","target":"collection:5323961@1","parts":["metadata","supplementary"]}},{"tool":"fetch","arguments":{"source":"figshare","target":"10.60893/figshare.aip.29678765.v1","parts":["metadata","supplementary"]}}],
        "official": ["https://docs.figshare.com/v2/", "https://docs.figshare.com/swagger.json", "https://info.figshare.com/user-guide/collections/", "https://info.figshare.com/user-guide/how-versioning-works/"]},
    "zenodo": {
        "search": "query는 Zenodo 검색식이다. 필드:값, 따옴표 구문, AND·OR·NOT, 괄호를 사용한다. 예: metadata.title:mathlib.",
        "options": {"sort": "bestmatch,mostrecent 등", "communities": "커뮤니티 식별자", "type": "자료 유형", "subtype": "자료 하위 유형", "access_right": "접근 유형", "keywords": "키워드"},
        "fetch": "Zenodo record 번호, records/번호 URL, 10.5281/zenodo.번호 DOI 또는 해당 record의 파일 URL. fulltext·supplementary는 레코드의 파일을 회수하며, 파일 URL이면 그 파일만 선택한다. artifacts 배열에 이름과 참조를 반환한다. 파일 크기와 제공된 checksum을 원자료와 대조한다. abstract는 레코드의 description이다.",
        "limits": "검색 limit 1..100, start는 0부터 임의 위치를 지정한다. 필요한 원 페이지를 읽고 정확한 구간을 선택한다. json은 선택 records, native는 원 페이지이며 native_pages에서 두 범위를 구별한다. 파일 판본은 응답의 record_id로 고정한다. concept DOI가 개별 record로 해석되면 version_selection에 구별해 표시한다. 파일 실패도 이름별로 반환하며 다른 자료원으로 이동하지 않는다.",
        "examples": [{"tool": "search", "arguments": {"source": "zenodo", "query": "mathlib", "limit": 2}}],
        "official": ["https://developers.zenodo.org/"]},
}
for identifier, usage in MORE_API_USAGE.items():
    SOURCES[identifier].usage = usage
    SOURCES[identifier].implementation = "partial"
    SOURCES[identifier].transport = "api"

SOURCES["github"].implementation = "partial"
SOURCES["github"].usage = {
    "search": "query는 GitHub 검색 문법이다. repo:소유자/저장소, user:소유자, language:언어, in:name,description,readme 등의 한정자를 사용할 수 있다.",
    "options": {"kind": "repositories(기본),commits,issues", "sort": "해당 GitHub 검색 종류의 정렬값", "order": "asc 또는 desc"},
    "fetch": "owner/repo@revision:path 또는 GitHub blob/tree URL. revision 생략 시 실제 기본 브랜치를 조회한다. 파일을 받기 전에 revision을 commit SHA로 고정한다. 경로 없는 저장소의 fulltext·supplementary 요청은 그 commit의 ZIP 원본이다.",
    "exports": "검색 export=json은 요청 창의 레코드 배열이고 native는 전체 건수·불완전 응답 표지를 포함한 해당 원 API JSON 페이지다. native의 결과 배열은 extract selection=/items로 읽는다. 별도의 CSV·서지 파일은 이 어댑터에서 제공하지 않는다. fetch의 export는 metadata JSON이고 소스 파일·저장소 ZIP은 fulltext로 요청한다.",
    "limits": "별도 자격 없는 API만 사용한다. 검색 limit 1..100, start는 0..999의 임의 위치다. 필요한 원 페이지에서 정확한 구간을 선택하며 native_pages로 원 내보내기와 선택 범위를 구별한다. 서비스는 한 검색에서 최대 1000건을 노출한다. 별도 인증이 필요한 전역 코드 검색은 사용하지 않는다. 파일 ref는 40자리 SHA 또는 태그·브랜치이며 /를 포함하는 ref는 owner/repo@ref:path 형식을 쓴다.",
    "examples": [{"tool": "fetch", "arguments": {"source": "github", "target": "leanprover-community/mathlib4@v4.22.0:lean-toolchain", "parts": ["metadata", "fulltext"]}}],
    "official": ["https://docs.github.com/en/rest/search/search", "https://docs.github.com/en/rest/repos/contents"],
}
for identifier, repository in [("mathlib", "leanprover-community/mathlib4"), ("math-comp", "math-comp/math-comp")]:
    SOURCES[identifier].implementation = "partial"
    SOURCES[identifier].usage = {
        "search": "query는 선언 또는 소스에 나타나는 축자 문자열이다. 해당 라이브러리의 고정 commit 소스에서 일치 줄을 회수하며 수학적 동의성이나 증명 검사를 대신하지 않는다.",
        "options": {"revision": "태그·브랜치·commit SHA. 생략 시 실제 기본 브랜치", "path": "검색할 저장소 상대 경로 접두사", "case_sensitive": "대소문자 구별 여부. 기본 true"},
        "fetch": "revision:path 또는 " + repository + "@revision:path. 경로 생략 시 commit과 요청한 소스 ZIP을 반환한다. 공개 GitHub 배포 원본을 사용하고 정확한 SHA를 기록한다.",
        "limits": "검색은 고정 commit의 .lean·.v·.thy·.md·lean-toolchain 파일에 대한 기계적 문자열 검색이다. start 0부터, limit 1..100. ZIP의 특정 파일은 extract의 selection으로 회수한다. release와 선언의 실재는 코드 원자료와 도구체인 파일로 확인한다.",
        "examples": [{"tool": "fetch", "arguments": {"source": identifier, "target": ("v4.22.0:lean-toolchain" if identifier == "mathlib" else repository), "parts": ["metadata", "fulltext"]}}],
        "official": ["https://github.com/" + repository],
    }

SOURCES["software-heritage"].implementation = "partial"
SOURCES["software-heritage"].usage = {
    "files": "parts에 files를 지정하면 Vault 준비를 기다리지 않고 directory/content API의 원 객체를 회수한다. dir·rev와 그 트리를 가리키는 rel은 경로별 manifest를 반환한다. 각 file/symlink 행의 artifact를 extract로 읽는다. 디렉터리의 이름·원 mode·자식 ID를 Git tree 해시로, 파일은 길이·sha1_git·제공된 체크섬으로 검증한다. 심볼릭 링크는 대상 문자열 바이트를 보존하며 따라가지 않고, revision_reference는 별도 참조다. root mode는 부모 항목이 없어 null이다. 비 UTF-8 경로는 escaped 표시와 path_bytes_hex를 함께 보존한다. cnt 또는 content를 가리키는 rel은 그 원 파일을 반환한다. snapshot·origin에서 한 working tree가 필요하면 명확한 directory/revision을 먼저 선택한다.",
    "verified_cache": "files 회수는 같은 ArtifactStore의 기존 객체를 재사용한다. source·역할·정확한 원 API URI를 대조하고 저장 SHA-256 및 Git tree/blob 해시와 원 체크섬을 다시 검사한다. cached_directories/cached_files는 재사용 수이며 원 retrieved_at을 유지한다. 새 자료와 기존 자료를 합쳐도 같은 content-addressed 대상임을 확인한다. 중간 오류는 확보한 manifest·파일과 함께 partial로 남기고 첫 429에서 추가 원격 요청을 중단한다. 같은 data-dir로 다시 요청하면 확보한 객체를 재사용하고 남은 객체를 요청한다.",
    "search": "query는 보존된 origin URL을 찾는 문자열이다. 결과는 원 저장소 주소와 Software Heritage의 보존 기록 링크다.",
    "options": {"with_visit": "방문 기록을 가진 origin으로 한정하는 서비스 조건"},
    "fetch": "swh:1:cnt|dir|rev|rel|snp:40자리해시, archive.softwareheritage.org/swh:… 또는 n2t.net/swh:… 링크, 원 저장소 URL. 일반 URL은 Software Heritage 안의 origin 식별자이며 외부 사이트를 방문하지 않는다. cnt는 metadata의 SWHID·길이·체크섬과 실제 전체 파일의 sha1_git를 대조한다. 오류 때 이미 받은 metadata를 보존한다.",
    "qualifiers": "origin·visit·anchor·path·lines를 보존하며 중복·잘못된 값을 거부한다. origin은 해독·정제하고 path는 URI 이스케이프 표기를 유지한다. 이 문맥의 사실관계는 검증하지 않아 context_verified=false다. path를 다른 파일의 선택 경로로 해석하지 않는다. cnt의 lines=9-15는 1부터 시작하는 포함 범위이며 lines=9는 한 줄이다. fulltext/supplementary의 기본 artifact는 선택한 조각, complete_content는 검증된 전체 파일이다. integrity는 전체 파일에 대한 검사다. 범위가 없으면 기본 artifact가 전체 파일이다. 범위 초과는 not_found와 전체 파일 참조를 남기며 잘라 맞추지 않는다.",
    "archives": "dir의 fulltext/supplementary는 원 tar.gz 압축본이다. rev는 원 metadata의 directory에 해당하는 압축본을 반환하고 archive_selection에 그 관계를 남긴다. 준비된 압축본이 없으면 이메일 없이 생성을 요청한다. pending은 준비 중 상태이며 retry 입력을 보존한다. retry_after_seconds=60은 이 서버의 재조회 간격 권고로 retry_basis에 구별하며 자료원의 완료 예정 시각이 아니다. 익명 API의 시간당120회 범위를 다른 호출과 함께 고려한다. 원 파일은 files 경로로도 회수할 수 있다. 전체 파일 내용·이름·권한·심볼릭 링크를 Git 트리 방식으로 해시해 디렉터리 SWHID와 대조한다. 불일치 또는 미지원 항목은 오류와 source_archive에 원 파일을 보존한다. extract로 목록을 읽고 selection에 정확한 경로를 주면 내부 파일 참조를 받는다.",
    "limits": "별도 자격 없는 공개 API. start는 0으로 두고 다음 페이지에는 반환된 next.cursor를 그대로 준다. limit 1..100. 전체 origin 검색 건수는 서비스가 주지 않아 total=null. 파일 바이트를 실행하지 않는다. octet-stream으로 받은 UTF-8/NUL 없는 내용은 text/plain으로 읽고 원 MIME도 남긴다. 줄 선택은 이런 UTF-8 content에 한정한다. rel은 원 target_type/target을 따라 디렉터리 또는 리비전의 트리를 회수하고 content 대상은 파일을 회수한다. archive_selection에 관계와 원 metadata 근거를 남긴다. 릴리스 연쇄는32개까지이며 순환·식별자 불일치를 거부한다. history는 dir·rev·rel·snp의 원 Git 압축본이다. snp의 fulltext/supplementary도 이 압축본을 반환한다. Git 객체 해시·연결 관계와 요청 객체를 대조하고 snapshot은 전체 브랜치 metadata의 해시와 압축본 refs도 대조한다. dir의 Git 형식에는 디렉터리를 가리키는 합성 커밋이 하나 있다. 검사에 Git 실행 파일이 필요하지만 보존 소스·설정·훅을 실행하지 않는다. 원 저자의 이메일이 없는 tag는 missingEmail 형식 경고를 보존하며 객체 무결성 검사와 구별한다. 트리 검증은 일반 파일·디렉터리·심볼릭 링크를 지원한다. 하드 링크 등 다른 항목은 원 압축본과 미지원 상태를 반환한다.",
    "examples": [{"tool": "fetch", "arguments": {"source": "software-heritage", "target": "swh:1:rel:fc8e44c5bb3fabe81e5ebe46ac013a2510271616", "parts": ["metadata","files"]}}, {"tool": "search", "arguments": {"source": "software-heritage", "query": "mathlib", "limit": 2}}],
    "official": ["https://archive.softwareheritage.org/api/", "https://docs.softwareheritage.org/devel/faq/index.html#what-are-the-usage-limits-for-swh-apis"],
}

SOURCES["drops"].implementation = "partial"
SOURCES["drops"].transport = "fixed: metadata API; search/document links Playwright"
SOURCES["drops"].usage = {
    "search": "query를 DROPS Search All Entities 입력에 그대로 제출한다. 문헌·volume·artifact 등 실제 검색 결과를 보존한다. options는 비운다.",
    "fetch": "10.4230/… DOI 또는 drops.dagstuhl.de/entities/… 링크. artifacts. DOI는 artifact로 해석한다. 서지·초록은 공개 metadata/schema-org API다. fulltext는 현재 문헌의 Files 영역에 있는 PDF·HTML 파일들을 회수한다. /storage/의 PDF·HTML 파일 URL을 직접 지정하면 문헌과 링크를 대조해 해당 파일만 받는다. supplementary는 현재 문헌의 부가자료 설명과 링크이며 외부 저장소 파일을 방문하지 않는다.",
    "exports": "검색은 json·html 또는 원 bibtex·xml·acm-xml·doaj-xml·schema-org·codemeta-json. 선택한 결과의 문헌별 파일과 실패를 보존한다. BibTeX에는 결합 파일 ref도 있다. fetch export는 논문의 Schema.org·BibTeX·XML·ACM-XML·DOAJ-XML이며 소프트웨어 artifact는 Schema.org·BibTeX·XML·CodeMeta다. CodeMeta의 identifier는 SWHID일 수 있으며 DOI와 구별한다.",
    "limits": "start 0부터, limit 1..1000. 서지·내보내기는 공개 API, 검색·문헌 파일 링크 발견은 Playwright로 고정한다. BibTeX·CodeMeta는 원 다운로드 endpoint를 사용한다. XML의 현재 문헌 헤더와 요청 DOI를 대조하며 참고문헌 DOI로 대체하지 않는다. 자료 유형에 없는 export 형식은 해당 결과의 실패로 구별한다. 외부 부가파일은 링크만 보존한다.",
    "examples": [{"tool": "search", "arguments": {"source": "drops", "query": "P versus NP", "limit": 2}}, {"tool": "fetch", "arguments": {"source": "drops", "target": "10.4230/LIPIcs.CSL.2020.5", "parts": ["metadata", "abstract", "fulltext"]}}],
    "official": ["https://drops.dagstuhl.de/metadata", "https://drops.dagstuhl.de/oai"],
}

SOURCES["crossmark"].implementation = "partial"
SOURCES["crossmark"].usage = {
    **SOURCES["crossref"].usage,
    "search": "Crossmark와 신뢰 자료원이 등록한 갱신·정정·철회 정보는 Crossref 공개 REST API로 조회한다. options.filter의 has-update:true는 다른 자료가 이 문헌을 갱신한 incoming 문헌, is-update:true는 이 자료가 다른 문헌을 갱신하는 outgoing 공지다. updates:DOI는 지정 DOI를 갱신하는 공지를, update-type은 공지의 유형을 찾는다. update-type 값은 addendum, clarification, correction, corrigendum, erratum, expression_of_concern, new_edition, new_version, partial_retraction, removal, retraction, withdrawal다. has-update-policy:true는 정책 DOI가 있다는 뜻일 뿐 개별 정정·철회를 뜻하지 않는다.",
    "fetch": "DOI의 원 등록 메타데이터를 보존하고 crossmark 요약을 함께 반환한다. 필드가 존재하지만 예상 타입과 다르면 schema_warnings와 partial을 반환하며 원 값은 보존한다. 잘못된 갱신 필드는 부재로 간주하지 않고 unknown으로 구별한다. updated-by는 이 문헌에 적용된 갱신 공지 목록이고, update-to는 이 공지가 갱신하는 대상 원 문헌 목록이다. 각 항목의 DOI·type·label·updated 날짜·source를 함께 읽는다. source는 publisher 또는 retraction-watch일 수 있고 같은 사건의 중복·불일치가 가능하므로 항목을 합치지 않는다. assertion은 선택적 비서지 메타데이터이며 갱신 관계가 아니다. relation은 별도의 일반 Crossref 관계다. update-policy는 출판사의 정책 DOI이고 content-domain은 유지되는 사본의 도메인 범위다. 필드 부재는 현재 Crossref 레코드에 등록된 갱신을 찾지 못했다는 뜻이며 실제 세계에 정정·철회가 없다는 증거가 아니다.",
    "limits": SOURCES["crossref"].usage["limits"] + " 무인증 public pool에서 단일 레코드는 초당 5건, 검색·filter 같은 목록 요청은 초당 1건이며 동시성은 1이다. 이 어댑터는 실제 연속 목록 요청 대조에서 1.05초가 429를 낸 여유 구간까지 피하도록 호출 시작 간격을 최소 1.5초로 둔다. 응답의 x-rate-limit-limit·x-rate-limit-interval·x-rate-limit-type·x-concurrency-limit을 evidence에 보존한다. 429는 자료 부재가 아니라 요청 제한이다. Retry-After가 있으면 오류에 보존하며, 없으면 성공 응답의 x-rate-limit-interval과 공식 제한보다 여유 있게 감속한 뒤 호출자가 재시도할 수 있다. 자동 재시도나 무제한 가용성을 보장하지 않는다.",
    "examples": [
        {"tool": "search", "arguments": {"source": "crossmark", "query": "", "options": {"filter": "has-update:true"}, "limit": 2}},
        {"tool": "search", "arguments": {"source": "crossmark", "query": "", "options": {"filter": "is-update:true,update-type:retraction"}, "limit": 2}},
        {"tool": "search", "arguments": {"source": "crossmark", "query": "", "options": {"filter": "updates:10.5555/12345678"}, "limit": 2}},
    ],
    "official": ["https://www.crossref.org/services/crossmark/", "https://www.crossref.org/documentation/crossmark/participating-in-crossmark", "https://www.crossref.org/documentation/retrieve-metadata/rest-api/rest-api-filters/", "https://www.crossref.org/documentation/retrieve-metadata/rest-api/access-and-authentication/", "https://www.crossref.org/blog/announcing-changes-to-rest-api-rate-limits/", "https://community.crossref.org/t/refining-rest-api-limits-for-improved-stability-and-reliability/16137", "https://www.crossref.org/documentation/retrieve-metadata/retraction-watch/"],
}

SOURCES["springer"].implementation = "partial"
SOURCES["springer"].capabilities = ("source_guide", "fetch", "export")
SOURCES["pqdt"].implementation = "partial"
SOURCES["pqdt"].transport = "playwright"
SOURCES["pqdt"].usage = {
    "search": "KUDOS → 학술DB → PQDT Global에서 query를 자료원 검색창에 그대로 제출한다. 예: TI(\"P versus NP\"). 필드 괄호와 AND·OR·NOT·큰따옴표 구문을 결합한다. TI는 제목, AU는 저자, AB는 초록, SU는 주제다.",
    "options":{"sort":"relevance(기본), oldest, recent", "publication_date":"{from:YYYY-MM-DD,to:YYYY-MM-DD} 발행 날짜 범위",
               "facets":"subjects, index_terms, universities, locations, languages의 각 값에 {include:[정확한 이름],exclude:[정확한 이름]}를 지정한다. 같은 그룹 include는 OR, exclude는 NOT이며 서로 다른 그룹은 함께 제한한다.",
               "export_content":"RIS/Text/RTF/XLS/서지 PDF/EndNote에서 citation_abstract_indexing(기본) 또는 citation_abstract. 원 내용 선택을 매번 지정·검증한다. BibTeX는 Cite의 고정 범위이므로 이 옵션을 함께 지정하지 않는다."},
    "exports": "json은 검색 행과 원 RIS 필드, html은 원 검색 페이지다. ris/text/rtf/xls/pdf는 선택 문헌의 원 서지 내보내기이며 pdf는 논문 전문과 다르다. endnote는 실제 동일 RIS 형식의 별칭이다. bibtex는 Cite의 BIB_TEX 원 문자열이고 키가 없으면 빈 id와 citation_key_missing 경고를 보존한다. RTF는 텍스트 줄, XLS는 시트·행, PDF는 쪽, RIS·BibTeX는 서지 항목으로 extract한다. 실패해도 검색 기록과 이미 확보한 파일을 보존한다.",
    "fetch": "docview 문서 번호 또는 ProQuest docview 링크를 지정한다. publication number와 docview 번호는 다르다. metadata·abstract·export·fulltext·supplementary를 요청할 수 있다. 제목은 TI 후보 검색으로 반환한다. PDF는 같은 ProQuest의 실제 Download PDF 링크에서 회수한다.",
    "supplementary":"현재 docview의 Supplemental files 탭에서 원 건수·파일명·다운로드 제어를 대조하고 개별 파일을 회수한다. files의 artifact를 extract로 읽는다. 내부 다운로드 서명은 반환하지 않는다. 해당 탭이 노출되지 않은 문헌은 source_page로 보존하며 파일 부재로 단정하지 않는다.",
    "facets":"기본 후보와 More에서 확인한 이름·건수·include/exclude 상태를 facets artifact로 반환한다. 현재 원 후보를 정확히 선택하며 이전 검색의 조건은 값별로 해제한 뒤 새 요청을 적용한다. 그룹당20값의 구현 상한은 제거했다. 이름 안의 OR·NOT·괄호는 이름 자체로 대조하며 연산자로 분해하지 않는다.",
    "limits": "start는0부터, limit는1..1000이고 원 페이지20행을 순회한다. 선택 문서 ID·제목·원 파일 구조와 범위를 대조한다. RTF와 서지 PDF의 문헌 ID는 hyperlink·URI annotation에도 있을 수 있다. RefWorks·NoodleTools·EasyBib의 외부 import는 제출하지 않고 external_import_required로 반환한다. 첨부는 파일별 상태와 성공 자료를 유지하며 연구 코드를 실행하지 않는다.",
    "examples": [{"tool":"search","arguments":{"source":"pqdt","query":"TI(algebra)","options":{"sort":"recent","publication_date":{"from":"2020-01-01","to":"2024-12-31"},"facets":{"subjects":{"include":["mathematics","computer science"],"exclude":["mathematics education"]},"languages":{"include":["English"]}},"export_content":"citation_abstract"},"start":19,"limit":2,"export":"text"}},
                 {"tool":"search","arguments":{"source":"pqdt","query":"TI(\"P versus NP\")","limit":1,"export":"bibtex"}},
                 {"tool":"fetch","arguments":{"source":"pqdt","target":"2618193239","parts":["metadata","abstract","fulltext"]}}],
}

SOURCES["ieee-xplore"].implementation = "partial"
SOURCES["ieee-xplore"].usage = {
    "fulltext_html": "parts에 fulltext_html을 지정하면 현재 문헌의 원 HTML 전문을 회수한다. 문헌 번호·DOI·제목과 실제 본문 영역을 대조하며 showHtml flag나 임의 글자 수 하한으로 배제하지 않는다. fulltext는 PDF 요청이다. HTML 제어가 있는데 본문이 준비되지 않으면 오류와 source_page를 보존하고, 현재 제어와 본문이 모두 없으면 그 문헌에서 확인하지 못한 상태를 반환한다.",
    "search": "KUDOS → 학술DB → IEEE → Command Search에서 query를 그대로 입력한다. 필드 이름을 큰따옴표로 감싸고 콜론 뒤에 조건을 쓴다. 예: \"Document Title\":\"P versus NP\". AND·OR·NOT·괄호, 구문 따옴표, * 와일드카드 등을 IEEE 문법대로 사용한다.",
    "fields": ["All Metadata", "Full Text & Metadata", "Full Text Only", "Document Title", "Authors", "Publication Title", "Abstract", "Index Terms", "Article Number", "Author Affiliations", "Author Keywords", "DOI", "Funding Agency", "IEEE Terms", "ISBN", "ISSN", "Publisher", "Standard Number"],
    "exports": "json은 UI의 원 문헌 필드·초록이다. bibtex·ris·plain은 native Citations의 Citation and Abstract, csv는 native Results export다. 여러 페이지의 파일은 export.artifacts로 나누어 보존한다. BibTeX·RIS·CSV는 형식과 선택 건수를 대조한다. 다른 형식 또는 건수를 받으면 source_export에 원 파일을 남긴다. 내보내기 실패 때 검색 레코드는 유지하고 export.errors와 partial을 반환한다. 네 형식의 연속 호출과 CSV의 선택 범위를 실제 MCP로 검증했다.",
    "fetch": "IEEE 문헌 번호, /document/번호 링크 또는 DOI를 지정한다. 서지·초록·원문 PDF를 해당 IEEE에서 회수한다. 제목은 후보 검색으로 반환한다. supplementary.references는 문헌 번호를 대조한 원 참고문헌 배열이며 artifact를 extract로 읽는다. order·id·title·text·links 등 원 필드를 보존하고 외부 인용 링크는 따라가지 않는다. supplementary.attachments는 문헌 metadata의 graphicalAbstract 파일·표지와 원 Media 탭 파일이다. 같은 파일이 두 화면 영역에 표시돼도 한 번만 회수하며 일반 도움말 링크는 제외한다. 파일별 역할·상태·artifact를 유지한다. MP4는 HTTP byte range와 버전 검증자를 대조하며 전체 바이트를 조립하고 각 요청의 제한은 45초다. 동영상 분석이나 연구 코드 실행은 수행하지 않는다. Media 탭의 파일은 supplementary_media 역할이며 native_index에 설명·파일명을 보존한다. 원 MP4 컨테이너와 40MB 다운로드를 실제 검증했으며 다른 파일 형식의 실측으로 확대하지 않는다. 원 metadata의 multimedia=false와 그래픽 초록 부재는 해당 문헌의 not_found이며 자료원 전체의 부재가 아니다.",
    "options": {"sort":"relevance(기본), newest, oldest, most_cited_papers, most_cited_patents, most_popular, publication_title_az, publication_title_za",
                "access":"all(기본), subscribed, open_access", "year":"YYYY 또는 순서가 맞는 YYYY-YYYY 문자열",
                "content_types / authors / affiliations / publication_titles / publishers / supplemental_items / conference_locations / publication_topics":"현재 facet의 value를 복사한 중복 없는 문자열 배열. publication_titles는 자유 텍스트 발행물 검색과 달리 해당 발행물 조건을 정확히 선택한다."},
    "facets":"검색 결과의 facets artifact를 extract하면 그룹별 value·label·count·selected 후보를 읽는다. 초기 후보 밖의 정확한 이름은 원 후보 검색으로 확인하고 유일할 때 선택한다. 추가로 찾은 후보도 같은 artifact에 보존한다. 현재 후보 목록을 전체 IEEE vocabulary로 표시하지 않으며 모호한 이름은 selection_required다.",
    "limits": "start 0부터, limit 1..1000. 자료원의 25건 페이지를 순회하며 전체 건수·페이지 수·시작/끝·고유 문헌 번호를 대조한다. 원 검색식·정렬·접근 범위·연도·facet을 실제 요청과 응답에서 확인하고 이전 검색 조건이 남으면 거부한다. 기존 Firefox 경로를 유지한다.",
    "examples": [{"tool":"search","arguments":{"source":"ieee-xplore","query":"\"Document Title\":complexity","options":{"sort":"newest","content_types":["Journals"],"publication_titles":["IEEE Access"],"year":"2020-2024"},"start":24,"limit":2,"export":"csv"}},
                 {"tool":"search","arguments":{"source":"ieee-xplore","query":"\"Document Title\":complexity","options":{"publication_titles":["Artificial Life"]},"limit":1}},
                 {"tool":"fetch","arguments":{"source":"ieee-xplore","target":"10488889","parts":["metadata","abstract","fulltext","fulltext_html"]}}],
}

SOURCES["afp"].implementation = "partial"
SOURCES["afp"].transport = "api"
SOURCES["afp"].usage = {
    "search": "공식 Heptapod 공개 API에서 고정 커밋의 AFP 항목 메타데이터를 받아 검색한다. query는 선택 필드에 대한 대소문자 무시 부분 문자열이다. 메타데이터의 TOML 원문과 archive를 보존하며 검색 결과는 항목 ID 순서다. 논리적 정리 검색이나 의미 유사도 검색을 수행하지 않는다.",
    "options": {"project": "기본 afp-devel(개발판), 또는 실제 AFP 릴리스 저장소명 afp-2025 등", "revision": "Mercurial ref 또는 정확한 40자리 커밋. 생략하면 해당 저장소 기본 branch를 먼저 커밋으로 고정한다", "fields": "id/title/abstract/topics/authors 중 배열; 기본 title와 abstract", "topic": "공식 topics 배열 값의 정확 일치", "author": "공식 authors 객체의 저자 ID 정확 일치"},
    "fetch": "항목 ID Cook_Levin, AFP 항목 URL, project@revision:파일경로, 또는 검색 레코드의 target을 지정한다. target의 thys/항목/은 해당 커밋의 항목 서지·초록과 증명 소스 묶음이다. 파일 지정 시 원 바이트를 회수한다.",
    "exports": "검색 json은 정규화 메타데이터, native는 원 TOML 파일의 archive다. 날짜는 JSON에서 ISO 문자열이며 원 TOML은 archive 안에 보존한다. fulltext는 Isabelle 증명 소스이며 PDF나 검증 성공 판정을 뜻하지 않는다.",
    "limits": "start 0부터, limit 1..1000. API 자격 없이 호출한다. AFP 개발판과 안정 릴리스를 구별하고 응답의 project·commit을 확인한다. 같은 커밋의 archive는 서버 세션 안에서 재사용한다.",
    "examples": [{"tool": "search", "arguments": {"source": "afp", "query": "Cook-Levin", "limit": 2}}, {"tool": "fetch", "arguments": {"source": "afp", "target": "Cook_Levin", "parts": ["metadata", "abstract", "fulltext"]}}],
    "official": ["https://isa-afp.org/download/", "https://foss.heptapod.net/isa-afp/afp-devel", "https://docs.gitlab.com/api/repositories/", "https://docs.gitlab.com/api/repository_files/"],
}

SOURCES["unpaywall"].implementation = "deferred"
SOURCES["unpaywall"].capabilities = ("source_guide",)
SOURCES["unpaywall"].usage = {
    "search": "query는 제목 검색식이다. 공백으로 나눈 단어는 기본 AND, 큰따옴표는 구문, OR는 선택, -는 제외다. 예: \"natural proofs\" OR \"circuit complexity\". 제목 이외 필드 검색을 제공하는 endpoint로 해석하지 않는다.",
    "options": {"is_oa": "true면 OA, false면 비OA, 생략·null이면 OA 여부로 제한하지 않음"},
    "fetch": "DOI 또는 DOI resolver 링크로 OA 상태·서지·모든 OA location 메타데이터를 받는다. 외부 원문 링크는 반환 자료에 보존하며 그 호스트를 자동 방문하지 않는다.",
    "exports": "json은 레코드, native는 원 DOI 응답 또는 검색 응답들의 JSON 참조다. 저자 초록이나 문헌 전문을 제공하는 서비스로 표시하지 않는다.",
    "limits": "start는 0부터, limit는 1..1000. 원 API의 50건 페이지를 사용한다. 전체 건수를 제공하지 않으면 total=null이다. 마지막 수신 페이지가 50건이면 다음 페이지 조회 전까지 끝 여부가 확정되지 않는다. 공식 호출 제한은 하루 100,000회다.",
    "configuration": "연락 이메일을 요구하므로 사용자 지시에 따라 사용을 보류한다. 서버는 이 자료원에 네트워크 요청을 보내지 않고 source_deferred를 반환한다. 이메일이나 계정을 요청하지 않는다.",
    "examples": [{"tool": "search", "arguments": {"source": "unpaywall", "query": "\"natural proofs\"", "options": {"is_oa": True}, "limit": 2}}, {"tool": "fetch", "arguments": {"source": "unpaywall", "target": "10.1038/nature12373", "parts": ["metadata"]}}],
    "official": ["https://unpaywall.org/api"],
}

SOURCES["theory-of-computing"].implementation = "partial"
SOURCES["theory-of-computing"].transport = "playwright"
SOURCES["theory-of-computing"].usage = {
    "search": "options.field는 text(기본), author, category다. text는 저널이 지정한 Google 검색 엔진의 웹페이지 검색으로, 큰따옴표 구문·OR·-제외·intitle: 등 그 검색 문법을 사용한다. 같은 문헌의 본문·저자 안내·주제 색인 페이지가 별도 결과일 수 있다. snippet을 저자 초록으로 표시하지 않는다.",
    "indexes": "author와 category는 저널의 공식 저자·주제 색인을 선택한다. query를 표시 이름과 먼저 정확 일치하고, 없으면 부분 일치한다. 여러 항목이 맞으면 selection_required로 후보 이름을 반환한다. 예: field=category, query=geometric complexity theory 또는 field=author, query=Ikenmeyer, Christian.",
    "fetch": "gs010 또는 v022a005 같은 문헌 ID, DOI, 저널 안의 문헌·웹페이지 링크를 지정한다. 현재 문헌 페이지에 연결된 PDF·PS·Source ZIP 등의 파일 URL도 받을 수 있다. 지정 파일을 다른 판본으로 바꾸지 않는다. 일반 웹페이지는 content_kind=web_page의 HTML로 보존한다.",
    "exports": "검색의 json·html은 실제 결과, bibtex는 문헌 ID가 있는 행의 native 인용문 참조다. 웹페이지 행 중 인용문이 없는 것은 별도로 표시한다. fetch의 export는 native BibTeX, abstract는 plain text, 기본 fulltext는 PDF다. supplementary는 제공되는 Source ZIP·PostScript·HTML 참고문헌·저자 안내를 보존한다.",
    "limits": "text 검색은 첫 100개 위치까지이며 Google 추정 건수는 reported_total에 표시하고 total은 null로 둔다. 저자·주제 목록은 실제 문헌 건수를 센다. API 키를 요구하는 Google JSON API는 사용하지 않는다. 저널이 공개한 기존 엔진 ID를 현재 검색 위젯으로 렌더링하여 옛 HTTP loader 문제를 처리한다.",
    "examples": [{"tool": "search", "arguments": {"source": "theory-of-computing", "query": "geometric complexity theory", "options": {"field": "category"}, "limit": 2, "export": "bibtex"}}, {"tool": "fetch", "arguments": {"source": "theory-of-computing", "target": "gs010", "parts": ["metadata", "abstract", "fulltext", "supplementary"]}}],
    "official": ["https://theoryofcomputing.org/search.html", "https://theoryofcomputing.org/articles/main/index.html", "https://developers.google.com/custom-search/docs/element"],
}

SOURCES["eudml"].implementation = "partial"
SOURCES["eudml"].usage = {
    "search": "query는 EuDML OpenSearch의 CQL 검색식이다. 필드·관계·조건을 쓴다. 예: all=\"P versus NP\" 또는 defName=\"Matematika\". 큰따옴표로 구문을 감싸고 AND·OR·NOT·괄호로 조건을 결합한다. 검색식을 서버가 새로 작성하지 않는다.",
    "fields": {"all": "전체 검색 영역", "defName": "제목", "authorCoauthorName": "저자 이름", "language": "ISO 639-1 언어", "journalName": "저널명", "published": "발행일", "id": "식별자"},
    "fetch": "196516 같은 문헌 번호, urn:eudml:doc:번호 또는 eudml.org/doc/번호 링크. eudml-nlm 원 메타데이터를 확보하고 현재 문헌의 article/book metadata header에 있는 EuDML ID를 대조한다. 실제 책204358의 서지와14개 장 정보도 검증했다. 제목 입력은 defName 후보 검색으로 반환한다.",
    "exports": "json은 파싱한 레코드, native·rss는 원 RSS 표현, xml·html은 같은 검색 조건의 자료원 export다. year는 RSS dc:date이며 pubDate와 구별한다. fetch의 metadata·export·supplementary는 원 NLM 메타데이터다.",
    "limits": "options는 비운다. start는 0부터, limit는 1..1000. 원 RSS의 totalResults·startIndex를 대조한다. CQL 요청의 응답 대기 한도는90초, NLM 요청은120초이며 연결 대기는20초다. NLM에 본문이 없고 목차·장별 서지·외부 원문 링크만 있는 경우 fulltext는 not_offered다. XML에 body 태그가 있다는 이유만으로 전문으로 세지 않으며 서지·장 정보·링크는 계속 보존한다. 원 저장소를 호출 AI가 별도 자료원으로 선택한다. XML 내부 항목은 extract selection에 ./front/article-meta/article-id, .//{*}book-part-meta 또는 .//{*}abstract 같은 경로로 지정한다.",
    "examples": [{"tool": "search", "arguments": {"source": "eudml", "query": "all=\"P versus NP\"", "start": 1, "limit": 2, "export": "rss"}}, {"tool": "fetch", "arguments": {"source": "eudml", "target": "196516", "parts": ["metadata"]}}],
    "official": ["https://wiki.eudml.org/mediawiki/eudml/images/D6.4.pdf", "https://eudml.org/api/search?q=all%3D%22P%20versus%20NP%22&count=2&format=rss"],
}

SOURCES["aps"].implementation = "partial"
SOURCES["aps"].transport = "api"
SOURCES["aps"].name = "APS 공개 접근"
SOURCES["aps"].usage = {
    "search": "공개 Harvest API의 openaccess 집합을 조회한다. query는 비우고 options의 날짜·저널 조건을 사용한다. API가 제공하는 피드이며 키워드 검색을 대신 수행하지 않는다.",
    "options": {"from": "시작 날짜 YYYY-MM-DD", "until": "종료 날짜 YYYY-MM-DD", "date": "published 또는 modified", "journals": "PRL 등 저널 식별자, 복수값은 서비스 문법에 맞춘 문자열"},
    "fetch": "10.1103/... DOI. 공개 접근 범위의 서지·초록·PDF를 키 없이 회수한다. supplementary는 제공되는 XML·BagIt ZIP이다. 제한된 DOI에 대해 API 자격을 요구하거나 브라우저로 자동 전환하지 않는다. 기관 구독 접근은 aps-institutional을 별도 source로 선택한다.",
    "limits": "limit 1..100, start는0부터의 임의 위치다. 원 페이지에서 요청 범위를 정확히 선택하고 native_pages에 원 페이지와 선택 건수를 남긴다. 전체 건수는 null이며 원 next 링크와 마지막 페이지의 남은 행으로 후속 범위를 판단한다. 중간 실패·중복 문헌은 확보분을 partial로 보존한다. 수백 명 이상의 저자도 records에는 전부 보존하고 preview에는 저자 수만 표시한다. metadata·abstract의 title/abstract는 자료원이 제공한 value와 format 객체를 유지한다.",
    "exports": "json 또는 native는 제공자 JSON이다. DOI별 제공 범위가 다르며 APS API에서 OA 문헌의 JSON·PDF 성공과 다른 문헌의 HTTP 401을 각각 확인했다.",
    "examples": [{"tool": "search", "arguments": {"source": "aps", "query": "", "options": {"from": "2026-09-01", "until": "2026-09-02", "date": "published"}, "limit": 2}}, {"tool": "fetch", "arguments": {"source": "aps", "target": "10.1103/PhysRevLett.116.061102", "parts": ["metadata", "abstract", "fulltext"]}}],
    "official": ["https://harvest.aps.org/", "https://harvest.aps.org/docs/harvest-api"],
}

for identifier, label in (("project-euclid", "Project Euclid"), ("cambridge", "Cambridge"), ("oxford", "Oxford"), ("aip", "AIP"), ("aps-institutional", "APS 기관 구독")):
    SOURCES[identifier].implementation = "partial"
    SOURCES[identifier].transport = "playwright"
    SOURCES[identifier].capabilities = ("source_guide", "fetch", "export")
    SOURCES[identifier].usage = {
        "fetch": label + "의 DOI 또는 정확한 문헌 페이지 링크로 서지·초록 영역·문헌 PDF를 요청한다. 기관 경로가 있는 자료원은 KUDOS 학술DB 바로가기를 거친다. Project Euclid는 공식 공개 사이트를 사용한다.",
        "exports": "metadata·export는 페이지의 citation/DC/prism/Schema.org 메타데이터를 보존한 JSON이다. supplementary는 원 문헌 페이지다. 다른 native citation 형식과 개별 첨부 파일의 연결은 개발 중이다.",
        "search": "문헌 조회 어댑터다. 해당 사이트의 고급검색·키워드 검색 연결은 개발 중이며 not_implemented를 반환한다. 검색 기능이 제공되지 않는 사이트로 해석하지 않는다.",
        "limits": "인식하지 못한 초록 영역은 source_page, PDF가 아닌 응답은 오류로 구별한다. 단순 OG 페이지 제목만으로 논문 메타데이터 확보를 선언하지 않는다. 다른 출판사 링크를 자동 시도하지 않는다.",
    }

SOURCES['wiley'].implementation = 'partial'
SOURCES['wiley'].transport = 'playwright'
SOURCES['wiley'].usage = {
    'search': 'query를 선택 필드의 Wiley 고급검색식으로 제출한다. 큰따옴표 구문과 AND·OR·NOT·괄호는 자료원의 검색 문법을 따른다. 검색 결과의 문헌별 DOI와 페이지 범위를 보존한다.',
    'fields': ['Anywhere', 'Title', 'Author', 'Keywords', 'Abstract', 'Author Affiliation', 'Funding Agency'],
    'options': {'field': '기본 Anywhere, fields 중 하나', 'terms': '순서 있는 추가 고급검색 행 배열: [{field: Title, query: 검색식}]. 필요한 원 행을 추가하고 모든 field/query의 보존을 확인한다. 추가 제어가 없으면 일부 조건만으로 검색하지 않고 오류를 반환한다.', 'publication': '저널·책·참고서 제목', 'after_year': '시작 연도 정수', 'after_month': '시작 월 1..12', 'before_year': '끝 연도 정수', 'before_month': '끝 월 1..12', 'sort': 'relevance(기본) 또는 date; 현재 Date 제어는 Earliest를 제출한다.'},
    'exports': 'json·html은 실제 검색 결과다. bibtex·ris·plain·endnote·medlars는 선택 문헌의 native 인용문 다운로드다. BibTeX·RIS의 DOI를 선택 문헌과 대조한다. export.artifact.ref로 인용문 파일을 추출한다.',
    'fetch': 'DOI 또는 Wiley 문헌 URL로 metadata·abstract·fulltext·export·supplementary를 요청한다. 제목은 Title 검색 후보를 반환하므로 정확한 DOI를 선택한다.',
    'supplementary':'Supporting Information 표의 원 파일명·설명·DOI를 보존하고 파일을 회수한다. supplementary.files의 artifact를 extract로 읽는다. ZIP은 구성 항목을 먼저 읽고 selection에 경로를 주어 꺼낸 뒤 해당 artifact의 내용을 읽는다. 내려받은 코드를 실행하지 않는다.',
    'limits': 'KUDOS 기관 바로가기를 사용한다. start 0부터, limit 1..1000이며 원 페이지는 20건이다. 검색 결과와 export 실패는 각각 보존한다. 문헌별 이용 권한에 따라 전문이 제한될 수 있다.',
    'examples': [{'tool': 'search', 'arguments': {'source': 'wiley', 'query': 'random graphs', 'options': {'field': 'Title'}, 'start': 19, 'limit': 2, 'export': 'bibtex'}}],
    'official': ['https://onlinelibrary.wiley.com/search/advanced'],
}

SOURCES['springer'].capabilities = ('source_guide','search','fetch','export')
SOURCES['springer'].usage = {
    'search': 'query는 검색식이다. field=Anywhere(기본), Title, Author를 선택한다. 큰따옴표는 구문, AND·OR·NOT·괄호는 Springer 검색 문법을 따른다. 추가 제목·저자·저널·날짜 조건은 고급검색의 해당 필드로 제출한다.',
    'options': {'field': 'Anywhere, Title, Author', 'title': '제목 조건', 'author': '저자 조건', 'journal': '저널 제목', 'date_from': '시작 연도', 'date_to': '끝 연도', 'content_type': 'Article, Chapter, Conference Paper, Research 등 사이트의 표시 값', 'open_access': 'true이면 공개 접근으로 한정', 'language': 'En 등 사이트 언어 코드', 'subject': '사이트 주제 값', 'discipline': '사이트 학문 분야 값', 'subdiscipline': '사이트 세부 분야 값', 'sort': 'relevance, newest, oldest'},
    'exports': 'json·html은 원 결과를 보존한다. csv는 같은 레코드의 기계적 CSV다. 사이트 일괄 CSV 제어는 로그인 경로로 이동하며 사용하지 않는다. bibtex·ris·endnote는 각 선택 문헌의 native citation 다운로드이며 export.artifacts에 파일 참조를 반환한다.',
    'fetch': 'DOI 또는 link.springer.com·link.springernature.com·www.nature.com의 문헌 URL. metadata·abstract·fulltext·export·supplementary를 요청한다. export는 해당 문헌의 native BibTeX다. 제목은 검색 후보로 반환하므로 정확한 문헌을 선택한다.',
    'fulltext_html':'Nature와 Springer의 문헌 URL에서 parts에 fulltext_html을 지정해 원 HTML 본문·TeX 수식·PNG/JPEG 그림을 회수한다. artifact의 HTML은 CSS selection으로, figures의 각 artifact는 extract로 읽는다. HTML의 그림 src는 보존된 artifact ref다. Nature 본문 영역과 Springer의 원 SecN 본문 영역을 각각 판정하며 초록·서지·PDF 제어만 있는 페이지를 HTML 전문으로 표시하지 않는다. 기관 접근 표시·PDF 제어·HTML 본문 제공은 별개다. 초록과 Article PDF가 있고 원 main-content가 비어 있는 확인된 레이아웃은 not_found/html_fulltext_not_available로 반환한다. 식별하지 못한 본문 요소가 남아 있으면 not_implemented/html_fulltext_not_identified를 유지한다. 그림 실패 때 본문과 파일별 오류를 partial로 보존한다. MathJax 실행이나 이미지 의미 판독은 하지 않는다.',
    'supplementary':'현재 문헌의 원 Supplementary Information·Peer Review File 등 첨부 제어를 읽는다. supplementary.files의 각 artifact를 extract로 읽고 index는 파일 목록이다. 파일 경로에 다른 DOI가 있으면 해당 문헌을 명시적으로 선택하도록 반환한다. 일부 파일 실패 때 받은 파일은 유지한다. 첨부 제어를 인식하지 못한 레이아웃은 source_page로 보존한다.',
    'limits': 'KUDOS 기관 바로가기를 사용한다. start 0부터, limit 1..1000, 원 페이지는 20건이다. 문헌별 전문 제공 여부는 기관 이용 범위에 따른다. 검색 snippet을 저자 초록으로 표시하지 않는다.',
    'examples': [{'tool':'search','arguments':{'source':'springer','query':'P versus NP','options':{'field':'Title'},'limit':2,'export':'bibtex'}}],
    'official':['https://link.springer.com/advanced-search'],
}

SOURCES['oxford'].capabilities = ('source_guide','search','fetch','export')
SOURCES['oxford'].usage = {
    'search': 'query를 선택 필드의 Query Builder에 제출한다. exact=true는 구문 일치다. exact=false이면 해당 필드의 원 검색식으로 처리한다. 문헌 결과와 자료원의 표시 건수가 일치한 뒤 반환한다.',
    'options': {'field':'All(기본 검색), Full Text(고급검색의 본문 필드), Keywords, Title, Author, Abstract, References', 'exact':'구문 일치 여부, 기본 false', 'sort':'relevance(기본), newest, oldest, title_asc, title_desc'},
    'exports': 'json·html은 실제 문헌 결과, csv는 그 레코드의 기계적 CSV다. bibtex·ris·endnote·plain은 선택 문헌의 native citation 다운로드이며 export.artifacts의 ref로 읽는다. 사이트 Export title list는 아래의 현재 접근에서 검증되지 않은 별도 기능이며 이 export 인자에 포함되지 않는다.',
    'title_list_export': {
        'status': 'currently_unavailable',
        'format': 'csv',
        'scope': '현재 검색 결과에 포함된 책·저널 제목을 결과 수가 많은 순으로 최대 2000개 집계한다. 문헌 레코드 CSV나 문헌별 citation이 아니다.',
        'observed_boundary': 'KUDOS의 현재 OUP 바로가기는 프록시 호스트로 이동한다. 같은 브라우저·같은 1건 검색에서 프록시는 제어를 노출하지만 reCAPTCHA 사이트 키가 프록시 도메인을 허용하지 않아 정상 과제를 만들지 못했고, Oxford 직접 호스트는 title-list 제어를 서버 마크업부터 노출하지 않았다.',
        'validation': '현행 공식 코드는 /Solr/ExportResults에 captchaResponse를 POST하고 blob을 기대한다. UI는 유효한 응답 전 요청을 막으며, 빈 captchaResponse를 보낸 음성 대조는 HTTP 200 text/csv, 선언 길이140, 관찰 body0바이트였으며 유효한 CSV 파일을 확보하지 못했다. 이 음성 대조를 정상 CAPTCHA 경로의 가용성 증거로 사용하지 않는다.',
        'institution_discovery': '직접 호스트의 SAMS Sigma 목록은 Abertay University 양성 대조를 포함한 2,483개 기관을 정상 필터링했다. Kyungpook National University·Kyungpook·Kyung Pook National University·KNU·knu.ac.kr·경북대학교는 원 기관 링크와 화면 결과 모두 0건이었다.',
        'related_holdings_list': {
            'status': 'separate_portal_control',
            'format': 'xlsx',
            'scope': 'KUDOS의 OUP 제공리스트는 252개 OUP 저널의 ISSN·제공연도·URL을 담은 기관 보유목록이다.',
            'not_equivalent': '검색어로 집계한 책·저널 title-list CSV가 아니므로 비가용 title-list export의 대체 성공으로 세지 않는다.',
        },
    },
    'fetch': 'Oxford Academic의 정확한 문헌 URL 또는 이 플랫폼으로 연결되는 DOI. 검색 결과의 url을 사용하면 같은 플랫폼의 해당 판본을 지정한다. metadata·abstract·fulltext·export·supplementary를 요청한다. export는 native BibTeX이며 그 DOI를 문헌 metadata와 대조한다. 제목 입력은 Title 검색 후보를 반환한다.',
    'supplementary':'문헌의 ArticleDataSupplements 위젯에 나열된 원 파일을 회수한다. 파일명·설명·DOI를 부호화한 경로를 보존하고 문헌 DOI와 대조한다. supplementary.files의 artifact를 extract로 읽는다. 다른 첨부 레이아웃은 source_page로 남긴다.',
    'limits': 'KUDOS 기관 접속. start 0부터, limit 1..1000, 원 페이지 20건. 제휴 출판사의 책, 저널·그림 같은 결과도 포함하므로 type을 보고 문헌을 선택한다. All과 Full Text는 다른 검색 범위다. title-list의 현재 호스트/CAPTCHA 경계는 title_list_export를 본다.',
    'examples': [{'tool':'search','arguments':{'source':'oxford','query':'P versus NP','options':{'field':'Title','exact':True},'limit':2,'export':'bibtex'}}],
    'official':['https://academic.oup.com/search-results'],
}

SOURCES['aip'].capabilities = ('source_guide','search','fetch','export')
SOURCES['aip'].usage = {
    'search': 'query를 AIP Query Builder의 선택 필드에 제출한다. 추가 검색 행은 terms로 AND·OR·NOT을 결합한다. exact는 화면의 Exact Match 설정이다. 자료원의 검색 확장·어간 처리까지 문자열 동일성으로 해석하지 않는다.',
    'options': {'field':'All(기본), Title, Author, Author Affiliations, Full Text, Abstract, Keyword, DOI, ISBN, EISBN, ISSN, EISSN, Issue, Volume, References', 'exact':'화면의 Exact Match 설정, 기본 false', 'terms':'추가 행 배열. 각 행은 field와 query, 선택적으로 condition(AND·OR·NOT, 기본 AND), exact(기본 false)를 지정한다.', 'sort':'relevance, newest, oldest'},
    'exports': 'json·html은 실제 문헌 결과, csv는 같은 레코드의 기계적 CSV다. bibtex·ris·endnote는 문헌별 native citation 다운로드다. export.artifacts의 ref로 읽는다.',
    'fetch': 'AIP 플랫폼의 DOI 또는 정확한 문헌 URL로 metadata·abstract·fulltext·export·supplementary를 요청한다. abstract는 현재 문헌의 native BibTeX abstract 필드를 보존하며 export와 같은 파일을 재사용한다. supplementary는 인식한 Figshare DOI를 selection_required와 source/target으로 반환한다. 파일은 별도 figshare 호출로 선택한다. 다른 첨부 레이아웃은 source_page로 보존한다. 제목은 Title 검색 후보를 반환한다. 문헌 PDF의 이용 권한은 해당 출판물에 따른다.',
    'limits': 'KUDOS 학술DB 기관 바로가기를 사용한다. start 0부터, limit 1..1000, 원 페이지 20건. 검색 snippet과 저자 초록을 구별한다.',
    'examples': [{'tool':'search','arguments':{'source':'aip','query':'quantum computation','options':{'field':'Title','exact':True},'limit':2,'export':'json'}}],
    'official':['https://pubs.aip.org/advanced-search'],
}

SOURCES['cambridge'].capabilities = ('source_guide','search','fetch','export')
SOURCES['cambridge'].transport = 'fixed: citation API; institutional search/document Playwright'
SOURCES['cambridge'].usage = {
    'search': 'query는 Cambridge Core의 검색식이다. 큰따옴표 구문과 AND·OR·NOT은 원 검색 문법을 따른다. 저자·연도·자료 유형·기관 이용 가능 여부를 별도 조건으로 지정할 수 있다.',
    'options': {'author':'저자 검색 문자열','from_year':'시작 연도','to_year':'끝 연도','content_type':'Articles, Chapters, Books, Elements 중 하나 또는 배열','available':'true이면 기관에서 이용 가능한 내용으로 제한','subject':'검색 결과 facets.ref에서 얻은 주제 ID','journal':'facets.ref의 저널 ID','publisher':'facets.ref의 출판사 ID','society':'facets.ref의 학회 ID','sort':'relevance, title, newest'},
    'exports': 'json·html은 검색 결과, csv는 같은 레코드의 기계적 CSV다. ris와 native는 Cambridge의 별도 자격 없는 API가 반환하는 RIS다. export.artifacts의 ref를 추출한다. RIS의 UR과 선택 문헌 product ID를 대조한다.',
    'fetch': 'Cambridge의 DOI 또는 정확한 문헌 URL. metadata·abstract·fulltext·export·supplementary를 요청한다. export는 native RIS이며, DOI 필드는 원 파일에서 DOI: 접두어를 포함할 수 있다. 제목은 후보 검색으로 반환한다.',
    'supplementary':'Supplementary materials 표의 파일을 각각 회수한다. 같은 제목의 PDF·ZIP도 별도 파일로 보존한다. 원 파일명의 PII와 현재 PDF 메타데이터의 PII가 있으면 대조한다. files의 artifact를 extract로 읽고 ZIP은 구성 항목 선택 뒤 내부 파일을 읽는다. 코드를 실행하지 않는다.',
    'limits': '기관 검색과 문헌 접근은 KUDOS 바로가기를 사용한다. RIS API는 별도 키·계정·이메일 없이 호출한다. start 0부터, limit 1..1000, 원 페이지 20건. 온라인 발행일과 인쇄 발행일을 구별한다.',
    'examples': [{'tool':'search','arguments':{'source':'cambridge','query':'"P versus NP"','options':{'content_type':'Articles','available':True},'limit':2,'export':'ris'}}],
    'official':['https://www.cambridge.org/core/search','https://www.cambridge.org/core/services/aop-easybib/export'],
}

SOURCES['taylor-francis'].implementation='partial'
SOURCES['taylor-francis'].transport='playwright'
SOURCES['taylor-francis'].usage={
    'search':'query를 선택 필드의 Taylor & Francis 고급검색식으로 제출한다. 큰따옴표와 AND·OR·NOT은 원 검색 문법을 따른다.',
    'options':{'field':'Anywhere(기본), Title, Author, Keywords, Abstract, Affiliation, Funder','after_year':'시작 연도 정수','before_year':'끝 연도 정수','sort':'relevance(기본), newest, oldest, most_cited, most_read'},
    'exports':'json·html은 원 결과, csv는 같은 레코드의 기계적 CSV다. bibtex·ris는 선택 문헌들의 native citation POST 응답이며 DOI 집합을 대조한다. export.artifacts의 ref로 읽는다.',
    'fetch':'DOI 또는 Taylor & Francis 문헌 URL. metadata·abstract·fulltext·export·supplementary를 요청한다. abstract는 native BibTeX에 제공된 abstract 필드를 보존하고 export와 재사용한다. 제목은 Title 검색 후보를 반환한다.',
    'supplementary':'원 Supplemental 영역의 ZIP 등 파일과 본문 표의 native Download CSV를 회수한다. files의 role은 supplementary_file 또는 article_table이며 표에는 table_id가 있다. 표 CSV의 파일명은 그 id로 붙인다. 보충 파일·표를 같은 의미로 합치지 않는다. ZIP 내부의 압축 파일도 selection으로 꺼낸 뒤 다시 extract할 수 있다.',
    'limits':'KUDOS 학술DB에서 Taylor를 조회해 기관 바로가기에 진입한다. start 0부터, limit 1..1000, 원 페이지 20건. 별도 API 자격을 사용하지 않는다. native 내보내기에 초록이 없는 문헌은 source_page로 표시한다.',
    'examples':[{'tool':'search','arguments':{'source':'taylor-francis','query':'complexity','options':{'field':'Title'},'start':19,'limit':2,'export':'bibtex'}}],
    'official':['https://www.tandfonline.com/search/advanced'],
}

SOURCES['de-gruyter'].implementation='partial'
SOURCES['de-gruyter'].transport='playwright'
SOURCES['de-gruyter'].usage={
    'search':'query는 자료원의 고급검색이 생성하는 검색식이다. title:(complexity), familyName:(Goldreich), title:(complexity) AND familyName:(Goldreich)처럼 필드와 괄호를 사용한다. 원 문자열을 그대로 제출한다.',
    'options':{'sort':'relevance(기본), mostrecent, leastrecent, alphabetical, reversealpha','visibility':'all(기본), available(이용 가능), explicit(라이선스), open(OA), public(공개)'},
    'exports':'json·html은 원 결과, csv는 같은 레코드의 기계적 CSV다. ris·native는 문헌의 CITE THIS 제어에 연결된 RIS 다운로드다. DOI 문헌은 DOI를, DOI 없는 ISBN 도서는 ISBN을 대조한다. export.artifacts로 읽는다. 현재 문헌에 CITE THIS 제어가 없을 때만 document_citation_unavailable로 표시한다.',
    'fetch':'De Gruyter Brill의 DOI 또는 문헌 URL로 metadata·abstract·fulltext·export·supplementary를 요청한다. export는 native RIS다. 검색에는 책·장·논문 외 자료도 있으므로 type을 확인한다.',
    'supplementary':'Supplementary Material 목록의 원 다운로드 파일을 회수한다. downloadAsset 경로의 문헌 DOI를 대조하고 파일명·설명·파일별 상태를 유지한다. ZIP은 files의 artifact를 extract한 뒤 원 내부 파일 이름을 selection으로 선택한다. 오래된 제어가 404를 반환하면 그 파일의 not_found와 전체 partial을 보존한다.',
    'limits':'KUDOS의 De Gruyter 기관 바로가기를 사용한다. start 0부터, limit 1..1000, 원 페이지 10건. 자료원에 표시된 검색 건수와 실제 회수 행을 대조한다.',
    'examples':[{'tool':'search','arguments':{'source':'de-gruyter','query':'title:(complexity)','limit':2,'export':'ris'}}],
    'official':['https://www.degruyterbrill.com/search/advanced'],
}

SOURCES['jstor'].implementation='partial'
SOURCES['siam'].implementation='partial'
SOURCES['siam'].transport='playwright'
SOURCES['siam'].capabilities=('source_guide','search','fetch','export')
SOURCES['siam'].usage={
    'search':'query를 SIAM 기본검색에 그대로 전달한다. options.field가 있으면 고급검색의 해당 필드에 전달한다. Author 자유식도 밑줄·공백·Boolean·따옴표·wildcard를 자동 exact 변환하지 않고 그대로 보낸다. 밑줄이 든 자유 Author 식은 원 UI에서 exact 저자 식별과 같은 결과를 보장하지 않았음을 query_semantics 경고로 알린다. 원 페이지의 전체 건수·행 범위·문헌 DOI와 다음 페이지의 검색 조건을 대조한다.',
    'options':{'field':'Anywhere, Title, Author, Keywords, Abstract, Affiliation',
               'terms':'추가 검색 행의 순서 있는 {field, query} 배열. 요청한 각 행의 필드·값·순서를 원 요청과 대조한다. 원 UI에는 행별 AND/OR/NOT 선택 제어가 없어 operator를 받지 않는다.',
               'authors_exact':'원 Authors/Editors 필터에 표시된 정확한 저자명 하나 이상의 배열. 각 값을 ContribRaw로 보내고 여러 값은 파라미터를 반복하며 실측 의미는 AND다. 자유 Author 행과 함께 지정하면 자유식과 모든 exact 저자 조건을 AND로 결합한다.',
               'topic':'현재 자동완성에 나오는 정확한 주제명. 후보가 유일하지 않으면 selection_required와 후보를 반환한다.',
               'publication':'현재 자동완성에 나오는 정확한 발행물명. 예: SIAM Journal on Optimization. 사용자가 내부 ID를 만들지 않는다.',
               'published_within':'month, six_months, year. 현재 원 제어의 상대 기간을 선택하며 절대 범위와 함께 사용하지 않는다.',
               'published_after / published_before':'두 경계를 함께 {year, month}로 지정한다. 현재 원 제어에 없는 연도·월과 역전된 범위는 거부한다.',
               'content_type':'article, chapter, book',
               'sort':'relevance(기본), date, most_read, most_cited, title. date는 원 Date 정렬이며 별도 방향을 지정하지 않는다.',
               'page_size':'20(기본), 50, 100'},
    'range':'start는0부터, limit는1..1000. 다음 페이지는 원 링크를 따른다. JSON/CSV는 정확한 요청 창, html은 정제된 원 페이지 목록이다. 추가 조건은 매번 새 고급검색 폼에서 설정해 이전 검색의 필터가 섞이지 않게 한다.',
    'fetch':'SIAM DOI·문헌 URL은 원 문헌 페이지에서 서지·초록·PDF를 조회한다. 이름은 원 검색 후보와 selection_required를 반환한다. 책의 publication_doi와 실제 본문 제목을 대조하며 사이트 이름을 문헌 제목으로 사용하지 않는다. .pdf 주소와 epubs.siam.org/doi/pdf/DOI는 정확히 지정한 파일을 회수하며 metadata는 PDF 내장 정보다.',
    'exports':'검색은 json/html/csv/bibtex/ris/endnote/medlars/refworks. 원 인용문은 선택 DOI·제목·순서를 대조하고 페이지별 원 파일을 export.artifacts로 반환한다. BibTeX/RIS/EndNote는 서지 항목, Medlars는 원 태그가 있는 줄로 extract한다. RefWorks는 SIAM의 import HTML에 포함된 RIS 문자열을 보존한 decoded_textarea이며 외부 RefWorks로 제출하지 않는다. 문헌 export는 같은 DOI의 다섯 형식이다. 명시 PDF 파일의 export는 그 원 PDF다.',
    'limits':'별도 계정 없이 제공되는 SIAM 경로다. 서버가 전용 Chrome 창을 표시해 처리한다. 기관 구독 목록의 기재는 individual-subscription에서 조회하며 실제 비공개 원문 권한을 뜻하지 않는다. 접근 제한은 문헌·경로별 결과다. 현재 DOI에 결속된 PDF 제어를 인식하며 같은 DOI의 접근 제한 화면으로 돌아오면 access_restricted로 반환한다. 책의 Front Matter·Back Matter는 별도 파일이며 전체 책으로 확대하지 않는다.',
    'examples':[{'tool':'search','arguments':{'source':'siam','query':'algebra','options':{'field':'Title'},'start':19,'limit':2,'export':'ris'}},
                {'tool':'search','arguments':{'source':'siam','query':'optimization','options':{'publication':'SIAM Journal on Optimization','published_within':'year'},'limit':2,'export':'csv'}},
                {'tool':'search','arguments':{'source':'siam','query':'linear algebra','options':{'topic':'Linear Algebra and Matrix Theory','published_after':{'year':2024,'month':1},'published_before':{'year':2026,'month':9}},'limit':2}},
                {'tool':'fetch','arguments':{'source':'siam','target':'https://epubs.siam.org/doi/book/10.1137/1.9780898717976','parts':['metadata','export']}},
                {'tool':'fetch','arguments':{'source':'siam','target':'https://epubs.siam.org/doi/pdf/10.1137/1.9781611974997.fm','parts':['metadata','fulltext']}}],
    'official':['https://epubs.siam.org/search/advanced','https://epubs.siam.org/faq'],
}
SOURCES['ams'].implementation='partial'
SOURCES['ams'].transport='playwright'
SOURCES['ams'].capabilities=('source_guide','search','fetch','export')
SOURCES['ams'].usage={
    'search':'KUDOS → 학술DB → AMS 바로가기의 원 고급검색을 사용한다. options.field는 Title(기본), Author, ProductCode, BookText, ISBN, MSC다. BookText는 책 본문 검색이며 일반 전 자료원 본문 검색으로 바꾸지 않는다. MSC는 두 자리 분류이며 쉼표로 복수를 입력할 수 있다.',
    'options':'추가 title, author, product_code, book_text, isbn, msc를 결합할 수 있다. 주 field와 같은 추가 필드는 중복 지정하지 않는다. content_type은 All(기본), EBook, Journal, Abstracts다. start는 0부터, limit는 1..1000이며 cursor는 지원하지 않아 원격 접근 전에 거부한다. 원 페이지의 건수·위치를 대조하되 RowsPerPage보다 적은 양성 페이지 자체를 폐기하지 않는다. 원 화면에도 보이는 ordinal 공백이 요청과 겹치면 확인된 prefix, source_range_gap과 다음 안전한 start를 partial로 반환한다. options.expression은 아래 입증된 부분집합만 원 기본 필드로 실행한다. 현재 AMS 제어가 의미를 보존하지 않는 Boolean 조합은 provider_feature_unavailable, 로컬 adapter가 아직 의미 동등하게 매핑하지 않은 field/operator/value는 expression_mapping_unavailable로 브라우저 이동 전에 구별한다.',
    'expression':'각 term은 {field, operator, value}다. Title contains 또는 Author contains를 쓰고 value는 공백·연산자 없는 Unicode 영숫자 한 토큰이어야 한다. 단일 term, 같은 필드의 term 두 개 이상을 묶는 OR, 같은 OR의 의미동등 중첩, 그리고 겹치지 않는 Title 식과 Author 식의 AND를 지원한다. Title term 두 개 이상의 OR와 Author term 두 개 이상의 OR는 AMS가 같은 합집합으로 해석하는 공백 구분으로 각각의 원 기본 칸에 보낸다. AMS 화면은 Gödel 같은 입력을 보존해 받되 실제 요청에서는 공식 JavaScript와 같이 결합부호를 제거한다. 서로 다른 Title/Author는 원 두 필드의 교집합으로 실행한다. NOT·같은 필드의 AND·필드 간 OR·equals·공백이나 문장부호를 포함한 원자값·그 밖의 필드는 지원하지 않는다.',
    'records':'Title와 Subtitle을 구별한다. ProductCode, DOI, PII, ContentType, RelatedCustomers, Abstract, ProductDescription 등 원 필드를 보존한다. target은 선택한 원 문헌 URL이다. 책(B)·논문(A)·학회 초록(ABS)이 섞이며 DOI가 없는 결과도 유지한다.',
    'exports':'json은 확인된 요청 창의 원 레코드, native는 방문한 원 JSON 페이지들, html은 방문한 검색 페이지들이다. source_range_gap이나 후속 오류가 있으면 records·native·html은 확인된 prefix와 partial 상태만 보존하며 요청 창 전체라고 표시하지 않는다. csv는 같은 확인 레코드의 기계적 직렬화다. xlsx는 선택한 각 논리 상품의 원 workbook을 export.artifacts[].artifact에 반환한다. 한 상품의 ISBN 변형이 여러 물리 행으로 나올 수 있으며 integrity.logical_products와 physical_rows를 구별한다. 빈 Product Code 셀을 채우지 않는다. 일부 파일이 실패해도 원 검색 결과와 상품별 오류를 함께 보존한다.',
    'fetch':'책 ProductCode 또는 /view?ProductCode= URL은 같은 원 고급검색으로 식별한다. 현재 서버에서 검색한 target·DOI는 원 메타데이터를 재사용한다. 다른 DOI·문헌 URL은 원 문헌 페이지를 조회하며 추가 접근 확인을 반환할 수 있다. 책의 ProductDescription은 출판사 책 소개이며 논문 초록과 구별한다. .pdf 링크는 정확히 지정한 파일과 PDF 내장 메타데이터를 회수한다. 발췌·부속 파일을 전체 책으로 확대하지 않는다.',
    'verification_limit':'전용 Chrome의 실제 MCP에서 기본 algebra 검색6,589건·13건 범위·페이지 경계11/2·0건·원 XLSX의3개 ISBN 변형 행·상품조회/추출을 통과했다. 2026-09-13 UTC 최종 재실측은 Title 3항 OR와 의미동등 중첩 OR를 각각8,150건, Title OR/Author AND를38건, Author OR를30건, Unicode Gödel expression과 일반 검색을 각각5건으로 확인했다. algebra topology analysis는 TotalRows8,685와 RowsPerPage12에서 page1이11개/화면1–11, page2가12개/13–24, page3이12개/25–36, page724가9개/8,677–8,685였다. 첫 요청 limit20은11개 partial/source_range_gap과 next start12, 이어 start12는20개 ok로 실제 SDK에서 통과했다. ProductId는 서로 다른 초록 행에 재사용되므로 전체 native row로 중복을 구별한다. 새 세션 첫 expression+XLSX도 SURV/168 한 논리 상품·3개 물리 행으로 available이었다. 일반 검색은 기관 gateway 도착 호스트, expression은 호출마다 새 별도 공개 페이지를 사용했고 뒤 XLSX와51쪽 PDF도 통과했다. 따옴표·+/−·&&·||·!와 AND/NOT 문자열은 AND/NOT 의미를 보존하지 않았다. 공식 초기 화면은 동적 진입 제어와 Publication Year 기본 필드를 노출하지 않는다. 잔존 원 UI의 OR 선택은 정확히 직렬화돼 과거 OR→AND 관측은 조사 하네스 오류로 폐기했다. 그러나 정상 토큰·동일 세션의 동적 단일·OR·중첩식도 검색 API가 HTTP200 97바이트 message-only 오류를 반환했고 Edit는 HTTP500 AdvancedSearch.cshtml 91행 NullReferenceException으로 끝났다. BOOKREV의 유일한 중첩 제목은 provenance와 함께 읽되 원 payload를 바꾸지 않는다. 서비스 불가는 provider_unavailable, 접근 확인은 restricted이며 0건이나 영구적 기능 부재로 표시하지 않는다.',
    'examples':[{'tool':'search','arguments':{'source':'ams','query':'algebra','start':11,'limit':2,'export':'csv'}},
                {'tool':'search','arguments':{'source':'ams','query':'','options':{'expression':{'condition':'OR','terms':[{'field':'Title','operator':'contains','value':'algebra'},{'field':'Title','operator':'contains','value':'topology'},{'field':'Title','operator':'contains','value':'geometry'}]}},'limit':2}},
                {'tool':'search','arguments':{'source':'ams','query':'','options':{'expression':{'condition':'OR','terms':[{'field':'Author','operator':'contains','value':'Boykan'},{'field':'Author','operator':'contains','value':'Jech'}]}},'limit':2}},
                {'tool':'search','arguments':{'source':'ams','query':'algebra','limit':1,'export':'xlsx'}},
                {'tool':'fetch','arguments':{'source':'ams','target':'https://www.ams.org/books/gsm/128/gsm128-endmatter.pdf','parts':['metadata','fulltext']}}],
    'official':['https://pubs.ams.org/AdvancedSearch'],
}
SOURCES['aps-institutional'].capabilities=('source_guide','search','fetch','export')
SOURCES['aps-institutional'].usage={
    'search':'KUDOS → 학술DB → APS 바로가기를 거쳐 APS 원 검색을 사용한다. query는 첫 조건의 값이며 options.field의 기본값은 all이다. 검색 결과의 원 조건·정렬·페이지·건수를 대조한다.',
    'fields':['all','author','abstract','abstitle','title','refauth','affiliation','collaboration'],
    'options':'terms는 추가 {field, query, operator} 배열이며 operator는 AND/OR/NOT이다. 원 조건 순서를 유지한다. sort는 relevance/recent/oldest/most_cited다. date는 week/month/year다. 절대 범위는 start_date와 end_date를 YYYY-MM-DD로 함께 지정하며 상대 기간과 섞지 않는다. journal/article_type/category/physh_concept/physh_discipline은 원 값 하나 또는 중복 없는 배열이다. 검색 응답 facets 참조에서 현재 값·이름·건수를 읽어 사용한다.',
    'results':'title·doi·url·authors_display·citation_display·publication_date_display·listing·html·abstract·abstract_html을 보존한다. display 필드는 출판사의 표시 문자열이며 저자 목록이나 날짜를 새로 해석한 값이 아니다. 원 응답 HTML을 사용하여 MathJax가 숨은 수식을 빈 자리로 바꾸기 전의 MathML을 유지한다. 원 페이지는 evidence, 정확한 요청 창은 records다.',
    'exports':'json은 정확한 요청 창의 레코드이고 csv는 같은 필드의 기계적 직렬화다. html/native는 읽은 원 HTML 페이지 배열이다. bibtex/ris는 선택한 각 문헌의 원 인용 파일을 받아 DOI를 대조한다. export.artifacts의 format/artifact를 읽는다. 인용문 실패는 해당 DOI별 오류와 검색 레코드를 함께 보존한다.',
    'fetch':'DOI·문헌 URL은 기관 문헌의 서지·초록·PDF를 요청한다. 이름은 후보 검색이다. export는 문헌의 원 BibTeX·RIS다. supplementary는 현재 DOI에 결속된 원 파일 제어에서만 회수한다. 별도 계정이나 API 키를 요구하지 않는다.',
    'limits':'start는 0부터, limit는 1..1000이다. 20건짜리 원 페이지에서 요청한 창을 회수하고 건수와 현재 페이지를 대조한다. 동일 조건의 start>0 후속 요청은 최근에 받은 해당 페이지를 재사용할 수 있으며 evidence의 원 수신 시점을 유지한다. start=0은 새 검색이다. 후속 페이지 실패 때 이미 받은 요청 창의 일부는 partial로 보존한다. 접근 제한을 문헌 부재로 해석하지 않는다.',
    'verification':'전용 Chrome의 실제 MCP에서 첫 페이지·CSV·원 MathML·페이지 경계·제목 필드·선택 문헌 서지와 초록을 통과했다. journal=[prd,prl]와1960-01-01~1980-12-31 조건847건·선택1건의RIS/BibTeX·14쪽PDF·추출, 별도문헌의16쪽보충PDF도 검증했다. 모든조건조합이나모든보충파일형식의검증으로확대하지않는다.',
    'examples':[{'tool':'search','arguments':{'source':'aps-institutional','query':'algebra','limit':2,'export':'csv'}},
                {'tool':'search','arguments':{'source':'aps-institutional','query':'algebra','options':{'journal':['prd','prl'],'start_date':'1960-01-01','end_date':'1980-12-31'},'limit':1,'export':'ris'}},
                {'tool':'fetch','arguments':{'source':'aps-institutional','target':'https://journals.aps.org/prl/abstract/10.1103/PhysRevLett.115.250402','parts':['supplementary']}}],
    'official':['https://journals.aps.org/search'],
}

SOURCES['project-euclid'].capabilities=('source_guide','search','fetch','export')
SOURCES['project-euclid'].usage={
    'search':'공개 원 고급검색 UI를 사용한다. 기본 query는 All Fields 검색이며 사이트의 어근·구문 처리를 유지한다. options.field는 ALL, ABSTRACT, AUTHORNAME, AFFILIATION, DOI_ISSN_ISBN, FIGURETABLECAPTIONS, KEYWORDS, TITLE 중 하나다.',
    'options':'terms는 추가 조건 배열이며 각 항목의 query, field, operator(AND/OR/NOT)를 원 UI에 입력한다. 현재 폼의 첫10행은 원 UI로 입력하고 추가 행은 같은 원 검색식 문법으로 결합한다. 각 필드·연산자·값이 보존되는지 대조한다. year_from/year_to는 발행연도 정수이며 publication_titles는 정확한 발행물 제목 배열이다. 검색 결과 facets.ref를 extract(selection=/publication_titles)로 읽어 가능한 제목을 선택한다. sort는 Relevance, PubDateDesc, PubDateAsc, TitleAsc, TitleDesc이며 page_size는 25(기본), 50, 75, 100이다.',
    'pagination':'start는 0부터, limit는 1..1000이다. 표시된 원 페이지의 범위를 대조한다. 현재 원 검색 코드의50쪽 제한과 실제50쪽 응답·51쪽 빈 응답을 대조했으므로 start+limit는 50*page_size 이하로 지정하고 더 먼 결과는 검색 조건을 좁힌다. 다음 쪽의 미리 받기 응답을 현재 쪽으로 사용하지 않는다.',
    'exports':'json은 보존한 문헌 레코드, html은 검색 페이지, csv는 같은 레코드의 기계적 CSV다. ris·bibtex·endnote·citation-pdf는 선택된 각 문헌의 Citation & Abstract 원 다운로드다. citation-pdf는 서지와 초록의 인쇄용 PDF이며 논문 전문은 fetch fulltext로 받는다. 실패한 문헌과 이미 받은 export를 함께 표시한다.',
    'fetch':'Project Euclid 문헌 URL·DOI로 서지·초록·PDF·원 인용문을 확보한다. 이름은 후보 검색이다. export는 BibTeX·RIS·EndNote·인용문 PDF를 반환한다. supplementary는 Supplemental Content 탭의 문헌별 PDF·ZIP을 회수한다. 원 문헌 DOI와 supplement_doi를 구별하고 파일명·설명·파일별 상태를 보존한다. 설명 속 외부 저장소는 자동 방문하지 않는다. files의 artifact로 ZIP 항목을 선택하고 내부 텍스트를 줄 단위로 읽는다. 탭 제어 부재는 source_page이며 실제 파일 링크의 오류를 보충자료 전체의 부재로 해석하지 않는다.',
    'examples':[{'tool':'search','arguments':{'source':'project-euclid','query':'complexity','options':{'field':'TITLE'},'start':24,'limit':2,'export':'csv'}}],
    'official':['https://projecteuclid.org/'],
}
SOURCES['jstor'].transport='fixed: citation/search API; institutional document Playwright'
SOURCES['jstor'].capabilities=('source_guide','search','fetch','export')
SOURCES['jstor'].usage={
    'search':'query는 원 JSTOR 검색식이다. 따옴표로 구절을 묶고 AND/OR/NOT와 괄호를 사용한다. 필드는 au: 저자, ti: 제목, ab: 초록, ca: 캡션, jo: 저널 이름, jcode: 저널 코드, la: 언어다. cty:journal AND ty:fla는 전문 논문, ty:brv는 서평, cty:chapter는 장, cty:research_report는 연구 보고서 조건이다. 검색식을 다시 작성하지 않고, 별도 API 자격 없는 원 검색 JSON API를 KUDOS 기관 세션에서 호출한다.',
    'options':'sort는 relevance/newest/oldest, access는 available/all이며 기본은 relevance와 available이다. 이미지·파노라마만 고른 content_types에는 title_asc/title_desc, creator_asc/creator_desc, resolution 정렬도 쓸 수 있다. resolution은 높은 해상도부터다. available은 현재 기관에서 접근할 수 있는 자료, all은 접근할 수 없는 자료도 포함한다. start_date/end_date는 CE의 YYYY, YYYY/MM, YYYY/MM/DD 또는 BCE 연도인 -0500 같은 음수다. BCE 연도는 0을 허용하지 않는다. snippets=true이면 선택한 결과의 원 검색 발췌문을 함께 회수한다(기본 false). content_types·subjects·languages는 원 facet label의 배열이다. 반환된 facets를 extract하면 field별 label·display·count·selected를 읽을 수 있다. content_types 예는 journal, chapter, research_report, contributed_documents, contributed_books, contributed_serials, contributed_images, contributed_audio, contributed_video다. subjects 예는 mathematics-discipline·compsci-discipline, English의 languages 값은 eng OR en OR EN이다. 추가 조건은 facets={field:[label,...]}로 지정한다. 반환 facets에서 display로 원하는 항목을 찾고 그 항목의 label을 값으로 복사한다. cc_media_resolution은 이미지 해상도, geography는 지역, classification은 분류, cc_portal_id는 제공기관, cc_compilation_ids는 컬렉션이다. 같은 필드를 content_types/subjects/languages와 facets에 중복 지정하지 않는다. 계층의 하위 컬렉션 값은 제공기관을 고른 뒤 반환 facets에서 얻을 수 있다.',
    'range':'start는0부터, limit는1..1000이다. 원25건 페이지의 표식을 따라 요청 창을 회수한다. 여러 결과군이 반환되면 start/limit를 각 결과군에 각각 적용하므로 전체 received가 limit보다 클 수 있다. result_groups가 각 범위·건수·상태를 표시하고 records의 result_group이 귀속을 보존한다. 전체 결과는 원 결과군 순서이며 결과군 사이의 통합 관련도 순위를 만들지 않는다. 이미지 미리보기는 전체 이미지 순위의 첫 구간이 아니므로 원 결과군을 펼쳐 처음부터 순회한다. total은 반환된 결과군 전체 건수의 합, source_total은 최초 응답의 전체 건수다. 현재 화면에 없는 다른 결과군이 source_total에 포함될 수 있다. 후속 페이지가 실패하면 다른 결과군을 계속 처리하고 확보한 요청 범위를 partial로 보존한다. 이때 retry로 같은 창을 다시 요청할 수 있다.',
    'snippets':'snippets=true의 레코드에는 snippet.status·query·html·text가 있다. 원 발췌문은 질의 문맥이며 저자 초록으로 표시하지 않는다. 원 응답의 순서 대신 정규화한 JSTOR 식별자로 대응한다. 발췌문이 없거나 실패한 문헌은 별도 상태를 남기고 검색 레코드를 유지한다. snippet_evidence는 별도 원 응답이다.',
    'search_exports':'json/csv는 요청 창이며 native는 사용한 원 JSON 페이지다. 원 응답의 세션 관련 필드는 정제된다. bibtex/ris는 선택된 각 문헌의 원 파일을 export.artifacts에 제공한다. 일부 인용문 실패가 검색 결과를 버리지 않으며 파일별 오류를 남긴다. 연구용 연도는 원 표시 서지도 대조한다. 일부 원 year가0이거나 비정상적인 연도일 수 있으며 어댑터가 새 연도를 만들어 넣지 않는다.',
    'fetch':'JSTOR stable 번호, j.…·jj.… 도서/장 ID, community.… ID, stable URL 또는 JSTOR에 수록된 DOI를 사용한다. 이름은 제목 검색 후보를 반환한다. metadata·abstract·export는 원 citation API를 사용하며 도서와 논문의 RIS 유형·필드를 유지한다. fulltext는 KUDOS로 선택 문헌을 열고 원 Download와 필요한 이용 조건 확인을 거쳐 PDF·JPEG/PNG 이미지·MP3 오디오를 회수한다. 원 PDF의 표지·서지 쪽도 포함한다. 원 다운로드가 restricted이면 접근 제한, disabled이면 해당 자료의 not_offered다. 식별자 로딩 중 늦게 나타난 접근 확인을 구별하며, 끝내 로드되지 않으면 재시도 가능한 document_load_timeout으로 반환한다. 이미지 파일은 extract가 ImageContent로 전달한다.',
    'supplementary':'선택 문헌의 원 supplement 목록과 파일을 회수한다. 부모 stable ID·원 첨부 경로·제공된 파일 크기를 대조한다. 오디오·동영상에 원 전사문이 있으면 WebVTT도 포함한다. 파일의 transcript_type=auto는 자료원이 자동 생성한 전사문이며 서버가 작성하거나 정확성을 판정한 내용이 아니다. VTT는 extract의 start/count로 줄을 읽는다. 문헌 파일과 첨부를 함께 요청하면 같은 원 문헌 페이지를 사용한다.',
    'exports':'export.artifacts에 원 RIS와 BibTeX를 반환한다. 기본 artifact는 RIS이며 제공자 안내문은 source_preamble로 유지한다. JSTOR의 Text file은 실제 BibTeX이고 source_media_type은 text/plain이다. RIS의 UR·BibTeX의 url에 있는 stable ID를 요청 대상과 대조하며 BibTeX DOI 필드가 없다고 실패시키지 않는다. 형식별 오류와 먼저 받은 인용문을 함께 보존하고 잘못된 문헌의 원 파일도 오류의 source_export로 읽을 수 있다.',
    'limits':'문자 확인을 통과한 기관 세션에서 검색·페이지 경계·CSV·RIS·원 기간/유형/주제/언어 조건·이미지 검색·이름 후보·비2307 DOI·11쪽 PDF를 실제 MCP로 검증했다. 다시 접근 확인이 필요하면 restricted를 반환한다. 서버가 확인 과제를 인식하지 않는다. 초록이 없는 RIS에는 not_offered를 표시한다. JPEG 이미지·MP3 오디오·오디오/동영상 전사문·21쪽 보충 PDF도 실제 MCP에서 확인했다. 동영상 표본은 원 다운로드가 disabled였으므로 동영상 파일 자체의 회수 성공으로 세지 않는다. 검색 발췌문·BCE 연도·혼합 결과군의 페이지 경계와 CSV, 이미지 정렬과 해상도·지역·제공기관 조건도 실측했다. 모든 조건 조합의 검증으로 확대하지 않는다.',
    'examples':[{'tool':'search','arguments':{'source':'jstor','query':'ti:algebra AND au:Sawyer','limit':2,'export':'ris'}},
                {'tool':'search','arguments':{'source':'jstor','query':'algebra','start':24,'limit':2,'options':{'content_types':['contributed_images']}}},
                {'tool':'fetch','arguments':{'source':'jstor','target':'24931626','parts':['metadata','export','fulltext']}}],
    'official':['https://support.jstor.org/hc/en-us/articles/115004732567-Searching-Using-Fields-and-Advanced-Search','https://support.jstor.org/hc/en-us/articles/4405598751255-Searching-Using-Filters-and-Facets'],
}

SOURCES['numdam'].transport = 'fixed: OAI/citation API; native search/DOI resolution Playwright'

SOURCES['science-direct'].implementation = 'partial'
SOURCES['science-direct'].capabilities = ('source_guide','search','fetch','export')
SOURCES['science-direct'].usage = {
    'search':'KUDOS의 실제 ScienceDirect 바로가기를 거친 기관 웹 검색이다. query는 options.field가 선택한 원 필드에 그대로 전달한다. 기본 Anywhere는 참고문헌을 제외한 문헌 전체를 검색한다.',
    'fields':['Anywhere','Title','TitleAbstractKeywords','Author','Affiliation','Publication','References','ISSNISBN'],
    'syntax':'현재 웹 검색의 Boolean은 대문자 AND/OR/NOT와 제외 하이픈이다. 우선순위는 NOT, AND, OR이며 괄호로 결합한다. 큰따옴표는 이웃한 단어의 구문 검색이지만 구두점·복수형·철자 변형까지 정확히 고정하지 않는다. W/n·PRE/n 근접 연산자는 지원하지 않는다. 오래된 별도 API 문법으로 바꾸지 않는다.',
    'options':{'field':'위 fields 중 하나. 기본 Anywhere. 같은 필드를 추가 옵션으로 중복 지정하지 않는다.',
               'publication / authors / affiliations / title / references / doc_id':'추가 필드의 문자열. publication은 발행물 제목 검색어, doc_id는 ISSN/ISBN이며 PII가 아니다. 다른 조건이 있으면 query를 비울 수 있다.',
               'publication_exact':'현재 자동완성에서 선택할 정확한 저널명. 예: Journal of Algebra. 서버가 후보와 고유 식별자를 대조하며 유일하지 않으면 selection_required와 후보를 반환한다. publication 문자열·field=Publication·publication_titles와 함께 지정하지 않는다.',
               'date':'YYYY 또는 순서가 맞는 YYYY-YYYY. 결과 화면의 연도 범위와 같은 조건이다.',
               'volume / issue / page':'숫자 또는 숫자 범위 문자열. page에는 숫자로 된 article number도 지정할 수 있다.',
               'article_types / publication_titles / subject_areas / languages / access_types':'현재 검색 응답 facets의 해당 그룹 value를 복사한 문자열 배열. 같은 그룹의 값은 OR, 다른 그룹은 AND로 결합한다. 예: article_types=["FLA","REV"], subject_areas=["2600"].',
               'subscribed_only':'true이면 기관이 구독한 저널로 제한한다. 기본 false.',
               'sort':'relevance(기본) 또는 date'},
    'search_exports':'json은 정확한 결과 창, csv는 같은 필드의 기계적 직렬화, html/native는 회수한 원 결과 페이지 목록이다. ris/bibtex/plain은 선택한 각 PII의 원 검색 인용 제어에서 받은 파일이며 export.artifacts의 순서로 읽는다. 일부 내보내기가 실패해도 검색 레코드와 파일별 오류를 보존한다. 원 검색 행에 DOI가 없으면 null로 유지한다.',
    'facets':'현재 결과의 추가 후보를 펼친 뒤 group/value/label/count/selected를 반환한다. facet_groups.complete와 visible_candidates는 이번 화면에서 확인한 범위다. 발행물 자동완성과 발행물 facet은 별도 제어다.',
    'fetch':'DOI·ScienceDirect PII·문헌 URL을 지정한다. 원 문헌 페이지의 서지·초록을 회수하고 PII·제목·DOI를 같은 문헌의 검색 행과 대조한다. 이름은 Title 검색 후보와 selection_required를 반환한다. 서지와 초록을 인용문 파일의 접근 상태와 따로 보존한다.',
    'exports':'fetch의 export는 같은 PII·제목·제공 DOI를 대조한 RIS·BibTeX·plain 원 파일 목록이다. 기본 artifact는 RIS다. 현재 검색 행의 원 인용 제어를 사용하며 파일을 다른 서지 서비스로 재작성하지 않는다.',
    'fulltext':'정확한 PII의 View PDF 제어에서 PDF를 회수한다. 최종 파일 경로, PDF 형식, 첫 두 쪽 DOI와 제목을 대조한다. supplementary는 같은 PII의 mmc 원 파일과 설명이다. 파일 artifact는 resources/read 또는 해당 형식의 extract로 읽는다. 보충 제어가 없는 표본은 원 source_page와 관측 범위를 반환한다.',
    'limits':'start는0부터, limit는1..1000이며 원 페이지25행을 순회한다. 원 페이지 번호·전체 건수·PII·요청하지 않은 조건의 부재를 검사한다. fulltext가 실패해도 확보한 서지·초록·인용문과 component별 오류를 보존한다. PDF 준비 HTML이나 Chrome viewer를 원 PDF로 표시하지 않는다. 별도 Elsevier API 키·웹 계정은 요구하지 않는다.',
    'examples':[{'tool':'search','arguments':{'source':'science-direct','query':'algebra','options':{'article_types':['FLA','REV'],'subject_areas':['2600'],'date':'2020-2025','subscribed_only':True},'limit':2,'export':'csv'}},
                {'tool':'search','arguments':{'source':'science-direct','query':'algebra','options':{'publication_exact':'Journal of Algebra'},'limit':2}},
                {'tool':'fetch','arguments':{'source':'science-direct','target':'S156042922600065X','parts':['metadata','abstract','export','fulltext']}},
                {'tool':'fetch','arguments':{'source':'science-direct','target':'S0167278924001155','parts':['metadata','supplementary']}}],
    'official':['https://www.sciencedirect.com/','https://www.elsevier.support/sciencedirect/answer/how-do-i-use-the-advanced-search'],
}

SOURCES['general-web'].implementation = 'partial'
SOURCES['general-web'].transport = 'api (Mwmbl public search)'
SOURCES['general-web'].home = 'https://mwmbl.org/'
SOURCES['general-web'].capabilities = ('source_guide','search','export')
SOURCES['general-web'].usage = {
    'search':'Mwmbl 공개 웹 색인에 query를 검색어 문자열로 전달한다. 검증된 예: natural proofs. 이 경로에 별도 계정·API 키·연락 이메일을 제공하지 않는다. 다른 검색 엔진의 고급 연산자 의미를 이 API에 임의로 부여하지 않는다.',
    'options':{},
    'exports':'json은 URL·제목·snippet과 native 필드. native는 강조 표시 조각을 포함한 원 JSON 배열 전체다. csv는 요청 창의 기계적 CSV다. snippet은 후보 발견용이며 문헌의 원문 근거가 아니다.',
    'limits':'start 0부터, limit 1..100. start/limit는 해당 응답의 결과 묶음 안에서 선택한다. returned_set_size는 원 배열 크기이며 웹 전체 검색 건수가 아니다. total=null이고 API의 추가 서버 페이지·cursor는 제공하지 않는다. 전체 원 배열은 evidence.ref를 extract로 읽을 수 있다. 다른 source로 자동 전환하지 않는다.',
    'fetch':'검색 엔진의 후보 URL을 선택한 뒤 해당 출판사 또는 공개 문서 source를 지정해 fetch한다. 이 엔진 자체에서 논문 전문을 확보하지 않는다.',
    'examples':[{'tool':'search','arguments':{'source':'general-web','query':'natural proofs','limit':2,'export':'csv'}}],
    'official':['https://mwmbl.org/','https://github.com/mwmbl/mwmbl'],
}

SOURCES['iop'].implementation = 'partial'
SOURCES['iop'].transport = 'fixed: newest RSS API; other sorts/extra filters/document Playwright'
SOURCES['iop'].capabilities = ('source_guide','search','fetch','export')
SOURCES['iop'].usage = {
    'search':'query는 IOP terms 검색어다. 기본 sort=newest는 별도 API 자격이 없는 RSS API를 KUDOS 기관 프록시 세션에서 호출한다. sort=relevance/oldest 또는 pub_type/open_access 조건은 해당 기능이 있는 기관 원 검색 경로로 고정한다. API 실패 때문에 브라우저로 자동 전환하지 않는다.',
    'search_options':'sort는 newest/relevance/oldest, period는 anytime/lastThirtyDays/lastTwelveMonths/lastFiveYears다. journals는 ISSN 배열, page_size는 10/20/50이다. pub_type은 article/chapter/book 배열, open_access는 boolean이며 이 조건은 원 검색 경로로 처리한다. 검색어 문법을 임의로 변환하지 않는다.',
    'search_range':'start는0부터다. 최신순 API limit는1..1000이며 start500뒤 자료도 실제로 확인했다. API는 전역 일치 건수를 주지 않아 total=null이다. 원 검색 경로는 start+limit<=500이며 accessible_total은 노출된 상위 결과 수이고 전체 일치 건수가 아니다. 요청 범위를 조용히 잘라 맞추지 않는다.',
    'search_exports':'json/csv는 정확한 요청 창이다. 최신순 API의 rss/xml/native는 원 XML 페이지이며 그 밖의 검색에서 html/native는 원 HTML 페이지다. 원 RSS의 순서 참조가 빈 항목이면 item 등장 순서를 유지하고 empty_rdf_sequence_used_item_order 경고를 남긴다. 원문 XML은 evidence에 보존한다.',

    'fetch':'IOP DOI 또는 정확한 iopscience.iop.org 문헌 URL을 지정한다. 이름은 관련도 순의 원 검색 후보로 반환한다. KUDOS IOP 바로가기를 거쳐 기관 문헌의 서지 태그와 PDF를 회수한다. 초록은 원 wd-jnl-art-abstract 영역을 사용한다. fulltext_html은 본문 HTML·원 TeX·그림 파일을, supplementary는 해당 DOI의 원 보충자료 탭과 파일을 회수한다. 그림은 figures의 artifact를 extract하며 수식은 HTML의 script[type^="math/tex"]를 선택한다. math_images.manifest.ref를 extract하면 모든 원 수식 이미지의 번호·상태·artifact를 구간별로 읽을 수 있다. math_images.artifact는 첫 성공 이미지다. HTML과 원 TeX를 유지하며 이미지별 실패는 manifest에 보존한다.',
    'exports':'검색에서도 export=bibtex/ris로 선택한 창의 각 문헌 원 파일을 받는다. 최신순 RSS와 관련도/필터 검색의 경로는 유지하며 인용문 회수 오류가 검색 레코드를 지우지 않는다. 문헌의 BibTeX·RIS 링크와 원 파일의 DOI를 대조한다. 두 형식의 실제 MCP 회수를 검증했다. 원 BibTeX 키에 공백이 있으면 원 키와 바이트를 유지하고 citation_key_contains_whitespace 경고와 함께 필드를 추출한다. 파일을 정상 키로 고쳐 쓰지 않는다. 파싱·식별자 검사 실패 때 source_export에 받은 파일을 보존한다.',
    'limits':'현재 확인된 기관 세션에서 서지·초록·16쪽 PDF·BibTeX·RIS를 실제 MCP로 회수했다. API의 페이지 경계·start500 이후, 관련도 순의 경계·CSV·원 저널/문헌 유형/공개 접근 조건과 0건을 실제 MCP로 검증했다. 별도 문헌에서 본문 TeX154개·수식 이미지154개·그림5개·보충 PDF2쪽과 ImageContent를 검증했다. 수식 전체 목록은 manifest로 보존하고 응답에 반복하지 않는다. 기간 기본값 anytime, page_size10/20과 명시된 예제가 실측 범위이며 모든 조건 조합의 검증으로 확대하지 않는다. 접근 확인이 다시 필요하면 restricted를 반환한다. 본문 XML 다운로드 제어는 이 표본에서 발견하지 못했다. 현재 공식 XML 공급 경로는 별도 연락·검토를 요구하므로 추가 자격·연락 경로를 사용하지 않는 범위에 따라 제외한다.',
    'examples':[{'tool':'search','arguments':{'source':'iop','query':'complexity','start':500,'limit':2,'options':{'page_size':10},'export':'rss'}},
                {'tool':'search','arguments':{'source':'iop','query':'complexity','start':9,'limit':2,'options':{'sort':'relevance','page_size':10},'export':'csv'}},
                {'tool':'fetch','arguments':{'source':'iop','target':'https://iopscience.iop.org/article/10.1088/0022-3727/34/10/311/meta','parts':['metadata','fulltext','export']}},
                {'tool':'fetch','arguments':{'source':'iop','target':'https://iopscience.iop.org/article/10.1088/1367-2630/add557','parts':['metadata','fulltext_html','supplementary']}}],
    'official':['https://iopscience.iop.org/','https://ioppublishing.org/legal/textanddataminingpolicy/'],
}

SOURCES['knu-fric'].implementation = 'partial'
SOURCES['knu-fric'].transport = 'playwright'
SOURCES['knu-fric'].home = 'https://fric.knu.ac.kr/'
SOURCES['knu-fric'].usage = {
    'search': '경북대 FRIC 공개 소장 목록에서 query를 원 검색창에 그대로 입력한다. 학술지와 수록 논문을 구별하며 RISS의 링크는 참조로 보존한다.',
    'options': {'field':'journal(기본)은 학술지명/ISSN, article은 수록 논문명. 별도 Boolean 문법을 추정해 변환하지 않는다.'},
    'fetch': 'issn:2263-8733처럼 ISSN을 지정한다. 유일하게 일치하는 소장 기록이면 metadata·export를 반환한다. 제목은 후보 검색과 selection_required다. 검색 결과의 target 필드를 사용할 수 있다. RISS URL의 자동 열람은 이 경로에 포함하지 않는다.',
    'exports':'json은 원 제목·ISSN·소장처·표시 필드·공개 기록 링크. csv는 선택 창의 기계적 CSV, html은 원 검색 페이지다.',
    'limits':'start 0부터, limit 1..100, 원 페이지 10건. 등록 키가 필요한 FRIC OpenAPI는 사용하지 않는다. 이 소장 목록 endpoint에는 논문 전문·초록의 즉시 다운로드가 없다. 원문 복사 신청 안내 URL을 제공하며 신청서는 자동 제출하지 않는다.',
    'examples':[{'tool':'search','arguments':{'source':'knu-fric','query':'computer','start':9,'limit':2,'export':'csv'}},{'tool':'fetch','arguments':{'source':'knu-fric','target':'issn:2263-8733','parts':['metadata','export']}}],
    'official':['https://fric.knu.ac.kr/','https://www.fric.kr/user/openspace/openApi/openApiS.do'],
}

SOURCES['individual-subscription'].implementation = 'partial'
SOURCES['individual-subscription'].capabilities = ('source_guide', 'search', 'fetch', 'export')
SOURCES['individual-subscription'].usage = {
    'search': 'KUDOS 로그인 후 학술DB의 KNU 개별전자저널·KNU P+O Journal 제공 목록을 회수해 조회한다. query는 정제된 저널명·출판사·ISSN·URL의 대소문자를 구별하지 않는 부분 문자열이다. 빈 문자열은 목록 전체다. 내려받은 목록의 기계적 조회이며 출판사 논문 검색식이나 정규식으로 해석하지 않는다.',
    'options': {'catalogue': 'all(기본), knu-individual-electronic-journals, knu-print-online-journals',
                'field': 'all(기본), title, publisher, issn, url',
                'coverage_year': '네 자리 정수. 목록의 시작·종료 범위를 조회한다. current는 해당 목록의 기준연도까지만 포함하며 현재 개별전자저널은2026년, P+O는2025년이다. 원문 이용권의 실측을 뜻하지 않는다.'},
    'range': 'start는 0부터, limit는 1..1000이다. 필터 뒤 원 목록 순서의 정확한 창을 반환한다. cursor는 사용하지 않는다.',
    'fetch': 'search 레코드의 id 또는 catalogue 식별자를 target으로 사용한다. id는 catalogue·원 workbook hash 접두어·sheet·row를 포함한다. 원 파일이 바뀌면 이전 행 id는 not_found이며 새 검색에서 다시 선택한다. metadata·export는 정제된 보유 정보다. abstract·fulltext·supplementary는 이 목록의 제공 대상이 아니다. 외부 출판사 URL은 방문하지 않는다.',
    'exports': 'json 또는 csv. CSV는 같은 결과 창의 기계적 직렬화다. 원 XLSX에는 별도 서비스의 자격 정보가 포함될 수 있어 그대로 제공하지 않는다. 정제된 위치는 redactions의 좌표·표지로 남긴다.',
    'records': '원 ISSN·E-ISSN과 검증 상태, 표시 URL·hyperlink target의 충돌, 시작·종료 원문과 해석을 구별한다. 자격 정보와 안전하게 파싱할 수 없는 URL은 정제한다. 보유 목록의 기재와 실제 출판사 문헌 접근 권한은 별개다.',
    'examples': [{'tool': 'search', 'arguments': {'source': 'individual-subscription', 'query': 'SIAM', 'limit': 10, 'export': 'csv'}},
                 {'tool': 'fetch', 'arguments': {'source': 'individual-subscription', 'target': 'knu-individual-electronic-journals', 'parts': ['metadata', 'export']}}],
    'official': ['https://kudos.knu.ac.kr/eng/sub.htm?nav_code=eng1643175350'],
}

for category in ('author-repository','society-journal'):
    SOURCES[category].implementation = 'partial'
    SOURCES[category].transport = 'fixed: public document Playwright; OJS native citation API'
    SOURCES[category].capabilities = ('source_guide','fetch','export')
    SOURCES[category].usage = {
        'fetch':'알려진 공개 문서의 절대 HTTP(S) URL을 target으로 지정한다. 인증 상태를 공유하지 않는 공개 context로 PDF·HTML·기타 파일을 직접 회수한다. 등록된 플랫폼의 주소면 사용할 source를 반환한다. 임의 URL의 제목·DOI를 외부 서비스에서 추정하지 않는다.',
        'parts':'metadata는 PDF 내장 정보 또는 HTML의 공개 서지 태그 JSON. export는 OJS의 실제 citation_formats 제어가 있으면 공개 RIS·BibTeX API의 원 파일이며 DOI를 대조한다. 해당 제어가 없으면 서지 JSON이다. fulltext는 지정 URL의 내용이며 HTML에 같은 호스트의 citation_pdf_url이 있으면 그 PDF도 회수한다. abstract는 HTML에 표시된 abstract 영역. supplementary는 해당 페이지의 링크 목록이며 연결 파일 자체의 확보를 뜻하지 않는다.',
        'limits':'이 범주는 단일 검색 색인을 갖지 않는다. 이름·검색식·플랫폼 고급검색에는 구체 자료원을 먼저 선택한다. 직접 URL과 같은 호스트의 리디렉션만 허용하며 로컬·사설망 주소는 거부한다. 스크립트만 있는 초기 화면은 격리된 공개 브라우저로 렌더하고 실제 visible 내용·문서 제목과 알려진 준비 신호를 확인한다. 짧은 문서나 복수 heading을 임의로 배제하지 않는다. 빈 로딩 화면·로그인·보안 확인은 성공한 문헌으로 표시하지 않고 준비 실패의 source_page를 보존한다. 별도 로그인은 수행하지 않는다.',
        'examples':[{'tool':'fetch','arguments':{'source':category,'target':'https://www.cs.toronto.edu/~sacook/homepage/ptime.pdf','parts':['metadata','fulltext']}}] if category=='author-repository' else [{'tool':'fetch','arguments':{'source':category,'target':'https://www.combinatorics.org/ojs/index.php/eljc/article/view/v1i1r1','parts':['metadata','abstract','fulltext','export']}}],
    }

for identifier, level in {
    "mathscinet": "live_mcp_six_sorts_seven_facets_searched_candidates_four_exports_review_graph_windows",
    "wos": "live_mcp_editions_sorts_friendly_facets_windows_exports_citing_sorts_and_identity",
    "eccc": "live_mcp_name_candidates_search_and_pinned_revision_fetch",
    "crossref": "live_mcp_search_native_citation_eight_formats_extract",
    "arxiv": "live_mcp_search_pinned_html_source_archive_tex_extract",
    "zbmath": "live_mcp_arbitrary_window_doi_legacy_link_license_state_references",
    "github": "live_mcp_arbitrary_search_window_native_pages_pinned_zip_file_same_bytes",
    "mathlib": "live_mcp_pinned_source_search_file_fetch_line_comparison",
    "math-comp": "live_mcp_pinned_source_search_file_fetch_line_comparison",
    "opencitations": "live_mcp_native_csv_window_oci_fetch_reference_count",
    "knu-fric": "live_mcp_catalogue_pagination_issn_fetch_zero_result",
    "general-web": "live_mcp_public_api_candidates_csv_extract_empty_result",
    "author-repository": "live_mcp_public_author_pdf_dynamic_document_and_page_links",
    "society-journal": "live_mcp_public_journal_metadata_abstract_pdf_native_citations; shared_dynamic_renderer_verified",
    "numdam": "live_mcp_11_conditions_native_search_citations_jats_pdf_djvu_page_text_image_windows",
    "software-heritage": "live_mcp_verified_tree_files_cache_resume_and_native_git_archives; selected_flat_job_unprepared",
    "openalex": "live_mcp_arbitrary_window_group_cursor_abstract_relationships_name_doi",
    "core": "원본 검색·work/output8쪽·명시26쪽·files01복구48쪽·제거404 검증; indexed 안내와 rate 구별",
    "semantic-scholar": "원본 bulk1000·cursor·title-match 검증; batch/BibTeX/관계 양성 이력·최신 batch429 구별",
    "dblp": "live_mcp_native_timed_refresh_search_seven_exports_name_and_record_identity",
    "dblp-kg": "live_mcp_sparql_window_native_csv_tsv_key_doi_name; native_tsv_year_type_mismatch",
    "zenodo": "live_mcp_arbitrary_search_window_native_pages_file_checksum_fetch_extract",
    "figshare": "live_mcp_beyond_offset_window_collection_native_file_redirect_md5_and_text_extract",
    "acm-dl": "live_mcp_edit_query_boolean_combined_filters_native_exports_html_tex_pdf_supplement_and_identity",
    "scopus": "live_mcp_nine_sorts_thirteen_facets_exact_windows_native_facet_counts_and_relations",
    "drops": "live_mcp_native_exports_pdf_html_codemeta_and_supplementary_references",
    "springer": "live_mcp_advanced_search_citations_pdf_supplements_nature_springer_html_tex_figures",
    "ieee-xplore": "live_mcp_native_exports_filtered_windows_typeahead_pdf_html_identity_references_media",
    "crossmark": "live_mcp_search_extract",
    "afp": "live_mcp_entry_search_pinned_metadata_and_proof_source_fetch_extract",
    "unpaywall": "public_endpoint_contact_requirement_observed",
    "theory-of-computing": "live_mcp_indexes_citation_pdf_source_ps_references_fetch_and_text_pagination",
    "pqdt": "live_mcp_21_facet_values_filtered_windows_zero_seven_exports_fulltext_supplement",
    "eudml": "CQL/NLM·실제 책 서지와14장 검증; 목차의 전문 오판 수리·간헐적504 구별",
    "aps": "live_mcp_arbitrary_feed_window_native_pages_metadata_abstract_pdf",
    "aps-institutional": "live_mcp_search_window_custom_multi_facets_bibtex_ris_abstract_pdf_supplement",
    "project-euclid": "live_mcp_21_condition_semantics_window_50_page_bound_citations_pdf_supplement",
    "cambridge": "live_mcp_filtered_search_ris_pdf_and_supplement_pdf_zip_source_extract",
    "oxford": "live_mcp_search_citation_metadata_abstract_pagination_and_supplement_pdf",
    "aip": "live_mcp_advanced_search_citation_pdf_and_explicit_figshare_supplement_reference",
    "wiley": "live_mcp_dynamic_advanced_rows_citations_pdf_zero_and_supplementary_zip",
    "taylor-francis": "live_mcp_search_citation_pdf_dublin_doi_supplement_zip_tables_nested_source",
    "de-gruyter": "DOI·DOI 없는 ISBN 책의 현재 CITE/RIS 복원; 원본7검증·PDF/첨부; 특정 옛 첨부404 별도",
    "jstor": "live_mcp_search_image_sorts_facets_citations_pdf_mp3_transcripts_supplement; native_video_download_disabled",
    "iop": "live_mcp_rss_ranked_filters_native_search_citations; pdf_html_tex_154_equations_manifest_images_supplement",
    "siam": "52번째 조건17/17/0·자유 Author 보존·명시 exact 공동저자 AND 검증; 특정 기관 PDF 제한",
    "individual-subscription": "live_mcp_two_catalogues_95_holdings_six_siam_csv_range_year_fetch_zero",
    "ams": "Title/Author 식 부분집합·첫 XLSX·Unicode·순번 공백과 이어받기 원본13검증; 미매핑 식 별도",
    "science-direct": "live_mcp_search_cross_page_ris_zero_facets_exact_publication_three_citations_pdf_supplement_video",
}.items():
    SOURCES[identifier].verification = level


def source_info(identifier):
    try:
        return SOURCES[identifier]
    except KeyError:
        raise ServiceError("unknown_source", "Unknown source; use list_sources") from None
