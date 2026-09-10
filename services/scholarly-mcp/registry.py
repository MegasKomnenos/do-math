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
    ("individual-subscription", "개별 구독 자료원", "open_category", "", "target_dependent"),
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
    'exports':'json은 변수별 RDF binding 배열이다. 값의 type/value/datatype/xml:lang과 미결합 변수의 부재를 그대로 유지한다. native는 SPARQL 결과 JSON, csv·tsv는 같은 범위의 원 다운로드이며 값과 행을 대조한다. CSV는 변수명 fields로 추출한다. TSV는 원 표기와 ?변수 헤더를 보존하며 extract로 줄 구간을 읽는다. 원 TSV가 gYear를 정수로 출력하는 경우처럼 RDF term이 달라지면 partial/export_term_mismatch와 source_export의 원 파일을 반환한다. 파일을 고쳐 쓰지 않는다. RDF 자료형은 JSON을 기준으로 읽고 CSV가 이를 유지한다고 가정하지 않는다.',
    'fetch':'DBLP key·/rec/ URL·DOI는 일치하는 문헌의 RDF statement를 전건 회수한다. DOI 조회·대조는 대소문자를 구별하지 않으며 원 RDF DOI 표기는 유지한다. predicate/object의 RDF term을 유지한다. 이름은 제목의 대소문자 구별 없는 부분 문자열 후보로 반환한다. metadata·export·supplementary는 같은 문헌의 statements이며 연결된 저자·서명·인용 문헌을 재귀 회수하지 않는다. 여러 문헌이 같은 DOI에 연결되면 selection_required다. 초록·전문은 이 서지 지식 그래프의 제공 대상이 아니다.',
    'limits':'options는 비운다. 별도 키·계정·이메일 없는 DBLP 운영기관의 공개 API다. start 0부터, 구현 limit 1..1000. 전체 일치 건수는 별도로 세지 않아 total=null이다. provider_result_size는 원 제한 질의의 보고값이며 전체 검색 건수로 해석하지 않는다. 꽉 찬 마지막 페이지 뒤 빈 페이지를 읽을 수 있다. DBLP DOI 매핑 부재는 모든 자료원에서의 부재가 아니다. 기존 dblp 검색 API 실패 뒤 자동 전환하지 않으며 호출자가 dblp-kg를 선택한다.',
    'examples':[{'tool':'search','arguments':{'source':'dblp-kg','query':'PREFIX dblp: <https://dblp.org/rdf/schema#> SELECT ?publ ?title WHERE { ?publ dblp:title ?title . FILTER(REGEX(?title, "natural proofs", "i")) } ORDER BY ?publ','start':1,'limit':2,'export':'csv'}},{'tool':'fetch','arguments':{'source':'dblp-kg','target':'10.1006/jcss.1997.1494','parts':['metadata','supplementary']}}],
    'official':['https://sparql.dblp.org/','https://github.com/dblp/kg/wiki/dblp-KG-Tutorial','https://www.dagstuhl.de/en/dblp/news/2024/introducing-our-public-sparql-query-service'],
}

SOURCES["scopus"].implementation = "partial"
SOURCES["scopus"].usage = {
    "search": "KUDOS → 학술DB → Scopus → Advanced document search. query는 고급검색식 그대로 제출한다. 예: TITLE(\"P versus NP\"), TITLE-ABS-KEY(\"natural proofs\") AND PUBYEAR > 2020. AND·OR·AND NOT, 괄호, 큰따옴표 구문, 중괄호 정확 구문, W/n·PRE/n 근접 연산자는 Scopus 문법을 따른다.",
    "fields": {"TITLE": "제목", "ABS": "초록", "KEY": "키워드", "TITLE-ABS-KEY": "제목·초록·키워드", "AUTHLASTNAME": "저자 성", "AFFIL": "소속", "PUBYEAR": "발행연도", "DOI": "DOI", "EID": "Scopus 문서 ID"},
    "options": "options는 비운다. start는 0부터, limit는 1..1000. 기본 UI 정렬을 사용하며 primary 문서의 totalCount와 페이지를 대조한다. preprint 별도 집계는 섞지 않는다.",
    "exports": "json은 UI가 받은 전체 원 필드, csv는 같은 필드를 기계적으로 직렬화하며 중첩값은 JSON 셀이다. native RIS·BibTeX는 별도 웹 계정을 요구하므로 사용자 지시에 따라 보류한다. 요청 시 export_deferred와 검색 원자료를 반환하며 계정 입력을 요청하지 않는다.",
    "fetch": "EID(2-s2.0-숫자)·Scopus 문헌 URL·DOI로 색인의 서지·초록을 확보한다. 제목은 TITLE 후보 검색이다. supplementary는 현재 문헌의 References·Cited by 탭 목록이며 각 references/citations.artifact를 extract로 읽는다. 참고문헌은 text, 피인용 문헌은 itemTitle 등 원 필드를 보존한다. 출판사 원문은 별도 source로 선택한다.",
    "relationships": "참고문헌의 원 10건 페이지를 순회하고 시작 위치·전체 건수·실제 수신분을 대조한다. EID가 없는 참고문헌도 버리지 않는다. 피인용 응답은 탭 건수와 배열을 대조한다. 검색 요약의 search_metadata_count와 문헌 탭의 total이 다를 수 있어 별도로 보존한다. 일부 실패는 이미 회수한 관계 목록과 함께 표시한다.",
    "examples": [{"tool": "search", "arguments": {"source": "scopus", "query": "TITLE(\"P versus NP\")", "limit": 2, "export": "csv"}}],
    "official": ["https://www.elsevier.com/products/scopus/search"],
}

SOURCES["mathscinet"].usage = {
    "search": "query는 MathSciNet 검색창의 검색식이다. 고급 필드 태그를 query 안에 쓴다. 기관 인증은 서버가 KUDOS 로그인 → 검색 → 학술DB → MathSciNet 바로가기로 처리한다.",
    "fields": {"au": "저자", "aur": "저자 또는 관련 인물", "ti": "제목", "r": "리뷰 텍스트", "j": "저널", "se": "총서", "pc": "주 MSC", "sc": "부 MSC", "mr": "MR 번호", "doi": "DOI", "rn": "리뷰어", "any": "전체 필드"},
    "operators": "고급 필드 행 사이는 AND, OR, NOT. 문자열·구문은 자료원의 의미대로 입력한다. 따옴표 없는 공백 질의는 정확한 제목 일치를 보장하지 않는다.",
    "examples": [{"tool": "search", "arguments": {"source": "mathscinet", "query": "P versus NP", "limit": 5}}, {"tool": "search", "arguments": {"source": "mathscinet", "query": "ti:(\"P versus NP\")", "limit": 5, "export": "bibtex"}}],
    "limits": "검색 결과의 Article은 다른 출판사 자료일 수 있다. fetch는 MathSciNet 서지·리뷰·제공 요약·리뷰 PDF를 회수하며 Article을 다른 자료원에서 자동 확보하지 않는다. 리뷰와 논문 전문은 구별한다.",
    "export_formats": ["bibtex", "endnote", "amsref", "tex"],
    "fetch": "MR 번호·MathSciNet article 링크·DOI·이름을 지정한다. 이름은 제목 후보 목록이다. DOI는 원 검색이 유일한 MR 기록을 반환하고 그 원 BibTeX의 DOI가 일치할 때 해당 문헌을 조회한다. 확인되지 않으면 후보로 남긴다. metadata는 원 서지·리뷰 페이지이고 supplementary는 제공되는 Review PDF다. 논문 전문과 리뷰를 구별한다.",
    "exports": "fetch의 export.artifacts는 BibTeX·EndNote·AMSRef·TeX이며 기본 artifact는 BibTeX다. 검색 export에는 요청한 형식을 반환한다. 자료원이 형식화한 문자열을 빈 줄로 연결하며 다시 작성하지 않는다. 원 응답 순서 mr_order와 요청 순서 requested_mr_order를 보존한다. BibTeX MRNUMBER와 EndNote label도 응답의 MR 번호와 대조한다. 내보내기 실패 때 검색 레코드와 확보한 인용문을 보존한다.",
    "evidence": "2026-09-09 KUDOS 프록시 검색 입력·고급 필드·export 제어 실측. 다섯 도구의 실사용 검증은 별도 보고에 기록한다.",
}

SOURCES["wos"].usage = {
    "search": "query는 Web of Science Core Collection의 Query Builder 검색식이다. KUDOS의 Web of Science CPCI 바로가기로 같은 Core Collection에 기관 접속한다. Editions=All의 기관 이용 범위를 사용한다.",
    "fields": {"TS": "주제", "TI": "제목", "AB": "초록", "AU": "저자", "AI": "저자 식별자", "AK": "저자 키워드", "GP": "단체 저자", "ED": "편집자", "KP": "Keywords Plus", "SO": "발행물명", "DO": "DOI", "PY": "발행연도", "CF": "학회", "AD": "주소", "OG": "소속", "OO": "기관", "SU": "연구 영역", "WC": "WoS 분류", "IS": "ISSN/ISBN", "UT": "접근번호", "DOP": "발행일", "LD": "색인일", "ALL": "전체 필드"},
    "operators": "FIELD=(조건), AND·OR·NOT, 괄호와 큰따옴표 구문. * 등 와일드카드와 날짜 범위는 WoS 문법을 따른다. 예: TS=(\"circuit lower bounds\") AND PY=(2020-2025). 세션 #번호 결합은 다른 호출에서 같은 세션을 보장하지 않으므로 독립 검색식으로 전달한다.",
    "options": "현재 options는 비운다. 검색식 안의 필드·연도 조건을 지원하며 UI의 추가 facet·정렬·edition 지정은 구현 중이다.",
    "fetch": "WOS:접근번호·DOI·Web of Science full-record URL을 지정한다. 제목은 TI 구문 검색 후보와 selection_required를 반환하며 선택한 accession/DOI로 다시 요청한다. 전체 서지·제공되는 초록·인용문헌을 해당 색인에서 회수한다. 원 Full Record에 AB가 없으면 abstract는 not_found다. 논문 전문은 해당 출판사를 별도 source로 지정한다.",
    "exports": "기본 JSON 레코드는 Full Record and Cited References 텍스트 export를 손실 없이 파싱한다. plain은 같은 원파일. ris·bibtex·excel·tsv·html은 해당 native export의 Full Record이며 실제 제공 필드가 다를 수 있다.",
    "limits": "start는 0부터, limit는 1..1000. 큰 결과를 화면 카드 개수로 세지 않고 자료원의 count와 요청 범위의 export를 대조한다. 원 tags는 records의 fields 아래 소문자 키·원 줄 배열로 보존한다. cr은 인용문헌, ab는 초록, ut는 접근번호다.",
    "examples": [{"tool": "search", "arguments": {"source": "wos", "query": "TI=(\"P versus NP\")", "limit": 5, "export": "plain"}}],
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
    "search": "query는 선택한 field 안의 ACM 검색어다. AND·OR·NOT, 큰따옴표 구문, * 여러 글자·? 한 글자 와일드카드를 사용한다. 와일드카드는 단어 첫머리나 따옴표 구문 안에 쓰지 않는다.",
    "fields": {"AllField": "Anywhere", "Title": "제목", "ContentGroupTitle": "발행물명", "ContribAuthor": "저자", "Abstract": "초록", "Fulltext": "전문", "Affiliation": "저자 소속", "Keyword": "저자 키워드", "ConferenceLocation": "학회 장소", "ConferenceSponsor": "학회 후원자", "Contrib": "이름", "PubIdSortField": "ISBN/ISSN", "DOI": "DOI"},
    "options": {"field": "위 필드 이름. 기본 AllField", "fields": "추가 {field,value} 배열. native AND로 결합", "collection": "fulltext는 ACM Full-Text Collection, guide는 Guide to Computing Literature", "from_year,to_year,from_month,to_month": "발행 날짜의 사용자 지정 범위", "sort": "EpubDate_asc 또는 EpubDate_desc"},
    "fetch": "ACM DOI 또는 ACM 문헌·PDF 링크. 이름은 제목 검색 후보를 반환하므로 정확한 DOI를 선택한다. 원 논문과 재수록본은 별도 DOI·연도로 보존한다. 같은 ACM 문헌의 실제 PDF 제어만 사용한다.",
    "exports": "json은 검색 행과 BibTeX 필드를 함께 보존한다. bibtex·endnote·acmref는 실제 UI 응답의 원 서지와 자료원이 제공한 CSL 스타일·처리기로 생성한다. 서지 응답과 처리기 참조도 보존한다. 넓은 검색에서 한 페이지의 결과와 요청한 선택 범위는 구별한다.",
    "supplementary":"문헌의 보충자료 목록에서 원 파일명·설명·DOI를 대조하고 파일을 회수한다. files의 artifact로 ZIP 등을 읽고 내부 파일을 selection으로 꺼낸다. 기존 참고문헌 문맥은 원 source_page에 유지한다. 인식하지 못한 다른 첨부 레이아웃은 source_page로 남긴다.",
    "limits": "KUDOS 기관 프록시와 기본 Firefox를 사용한다. start 0부터, limit 1..1000. 추가 분류 facet·필드 사이 OR 편집·HTML 전용 전문은 구현 중이다.",
    "examples": [{"tool": "search", "arguments": {"source": "acm-dl", "query": "\"The complexity of theorem-proving procedures\"", "options": {"field": "Title", "collection": "fulltext"}, "limit": 2, "export": "bibtex"}}, {"tool": "fetch", "arguments": {"source": "acm-dl", "target": "10.1145/800157.805047", "parts": ["metadata", "abstract", "fulltext"]}}],
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
        "options": {}, "fetch": "journals/… 또는 conf/… 형태의 DBLP key나 /rec/ 링크. 원 XML 서지를 보존한다. 초록과 논문 전문을 제공하는 색인이 아니다.",
        "limits": "현재 limit 1..100. start로 순회. json/native 검색 export. API가 HTML 접근 확인 화면을 반환하면 restricted이며 브라우저로 전환하지 않는다. 같은 운영기관의 공개 지식 그래프는 dblp-kg라는 별도 자료원으로 명시적으로 선택할 수 있다. 그 질의 문법은 SPARQL이며 이 검색식의 자동 대체가 아니다.",
        "examples": [{"tool": "search", "arguments": {"source": "dblp", "query": "P versus NP", "limit": 2}}],
        "official": ["https://dblp.org/faq/How+to+use+the+dblp+search+API.html", "https://dblp.org/db/"]},
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
        "search": "kind=papers(기본)는 원 plain-text 논문 검색이다. Boolean 등 별도 검색 문법은 없고 명시한 query는 바꾸지 않는다. 원 API에서 하이픈 검색어가 매칭되지 않을 수 있다. kind=references 또는 citations이면 query에 문헌 식별자를 주고 해당 관계의 범위를 조회한다.",
        "options": {"kind":"papers,references,citations", "year": "papers의 2020 또는 2020-2025", "fieldsOfStudy": "papers의 Computer Science,Mathematics 등", "publicationTypes": "papers의 JournalArticle,Conference,Review 등", "venue": "papers의 발행처 이름 쉼표 목록", "openAccessPdf": "papers에서 true는 공개 PDF 보유 조건, false/null은 그 필터 해제. 비공개 PDF만 고르는 뜻은 아니다.", "minCitationCount": "papers의 최소 인용 수", "publicationDateOrYear": "papers/citations의 날짜 또는 기간", "fields": "필요한 원 필드 이름 쉼표 목록. 예: title,authors,year,externalIds,url; 관계에는 contexts,intents,isInfluential도 제공된다."},
        "fetch": "paperId·Semantic Scholar 문헌 URL·DOI·ARXIV:id·PMID:id·CorpusId:id를 대조한다. 이름은 원 API 특성에 맞춰 하이픈을 공백으로 바꿔 후보를 찾고 원 이름도 보존한다. 자동으로 후보를 고르지 않는다. metadata 조회에 전체 인용 배열을 붙이지 않는다. supplementary는 나가는 참고문헌의 페이지들을 회수하며 부분 실패·원 count와의 차이를 남긴다. 들어오는 인용은 search kind=citations로 범위를 지정한다. openAccessPdf의 외부 호스트는 자동 방문하지 않는다.",
        "exports":"search의 json/native는 원 레코드·응답이다. papers의 bibtex와 fetch export는 citationStyles.bibtex 원 문자열이며 한 문헌과의 결합 및 파싱을 검사한다. 잘못된 원 형식은 고쳐 쓰지 않고 errors.source_export에 원 파일을 남긴다. 관계 페이지는 json/native로 보존한다.",
        "limits": "papers limit 1..100, 관계 limit 1..1000. start와 원 next offset으로 순회하며 cursor는 사용하지 않는다. 관계 전체 건수는 제공되지 않아 total=null이다. 원 API가 count보다 앞서 순회를 끝내면 continuation_limited를 표시한다. 별도 자격 없는 공개 접근만 사용하고 호출 간격은 최소 1.05초다. 429는 요청 제한이며 자료 부재가 아니다. 신규 관계·BibTeX 실서비스 검증은 호출 제한으로 미완료다.",
        "examples": [{"tool":"search","arguments":{"source":"semantic-scholar","query":"natural proofs","limit":2}},{"tool":"search","arguments":{"source":"semantic-scholar","query":"9a350a6787a5a79805ddb474feb256a5adfdbefb","options":{"kind":"citations"},"limit":2}}],
        "official": ["https://api.semanticscholar.org/api-docs/graph", "https://api.semanticscholar.org/graph/v1/swagger.json"]},
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
        "search": "query가 있으면 공개 웹의 원 검색 폼을 사용한다. 단어 사이에는 AND가 적용된다. 대소문자·발음 구별 기호는 무시하며 완전한 단어를 찾는다. *는 단어 일부, 따옴표는 구문 검색이다. query를 비우고 field·terms를 생략하면 OAI collection/date 열거다.",
        "options": {"field": "all(기본), author, title, references, fulltext", "terms": "추가 조건 배열. 각 원 검색 필드는 AND로 결합된다. {field,query,not:false} 형식이며 field에는 keywords도 허용한다. 날짜 조건은 {field:'date',from:'2012',until:'2012'}처럼 쓴다. not:true는 그 조건을 제외한다. 최초 조건 포함 최대 10개.", "set": "OAI 전용 collection 식별자", "from": "OAI 전용 메타데이터 갱신 시작일 YYYY-MM-DD", "until": "OAI 전용 갱신 종료일", "metadata_format": "OAI 전용 eudml-article2 또는 oai_dc"},
        "fetch": "Numdam native ID·oai:numdam.org:ID·DOI·Numdam 문헌/파일 URL을 사용한다. 이름은 제목 검색 후보와 selection_required를 반환한다. metadata는 원 JATS를 포함하며 abstract는 그 원 초록이다. fulltext는 PDF, supplementary는 같은 레코드의 대체 전문 DJVU다. export는 원 BibTeX·RIS·EndNote 세 파일이다.",
        "exports": "웹 검색은 json(기본), html/native(원 페이지), bibtex, ris, endnote. 선택한 창의 문헌별 원 인용문과 결합 파일을 보존하며 일부 실패는 문헌별 표시한다. OAI 검색은 json/native(XML). BibTeX·RIS·EndNote는 extract로 필드를 읽거나 selection=raw로 원 줄을 읽는다. EndNote fields는 원 태그 T·A·R 등을 유지한다.",
        "limits": "웹 start는 0부터, limit 1..100, 원 페이지 20건이며 페이지 경계도 조회한다. OAI 페이지 크기는 자료원이 정하며 모든 수신분을 보존한다. OAI 다음 페이지는 next.cursor. 검색 날짜와 OAI 갱신 날짜를 구별한다. DJVU는 바이너리로 보존하며 현재 extract의 문서 판독 대상은 PDF다.",
        "examples": [{"tool": "search", "arguments": {"source": "numdam", "query": "complexity", "start": 19, "limit": 2, "export": "ris"}}, {"tool": "search", "arguments": {"source": "numdam", "query": "\"Three complexity functions\"", "options": {"field": "title", "terms": [{"field": "date", "from": "2012", "until": "2012"}]}, "limit": 2, "export": "bibtex"}}, {"tool": "fetch", "arguments": {"source": "numdam", "target": "10.1051/ita/2011126", "parts": ["metadata", "abstract", "fulltext", "export", "supplementary"]}}],
        "official": ["https://www.numdam.org/help/", "https://www.numdam.org/metadata/"]},
    "core": {
        "search": "query는 CORE 검색식이다. title:\"P versus NP\"처럼 필드를 지정할 수 있다. 원 검색 결과의 모든 필드를 보존한다.",
        "options": {"sort": "CORE 정렬 조건. 제공자가 거절한 조건은 오류로 반환한다."},
        "fetch": "CORE works 번호·CORE works URL을 지정하며 이름은 원 검색 후보와 selection_required를 반환한다. 응답의 works ID를 대조한다. abstract가 비어 있으면 not_found다. fullText가 실제 문자열 본문이면 별도 텍스트 artifact로 보존한다. 공개 API 접근 제한 안내문이면 restricted이며 본문으로 표시하지 않는다. 다른 저장소의 링크는 자동 방문하지 않는다.",
        "limits": "별도 자격 없는 공개 접근만 사용한다. limit 1..100, start는 0부터. 호출 간격 최소 2.1초. json/native export.",
        "examples": [{"tool": "search", "arguments": {"source": "core", "query": "title:\"P versus NP\"", "limit": 2}}],
        "official": ["https://core.ac.uk/services/api", "https://api.core.ac.uk/docs/v3"]},
    "figshare": {
        "search": "query는 공개 Figshare search_for에 그대로 전달한다. articles(기본) 또는 collections를 검색한다. 이름 fetch는 후보 선택을 반환한다.",
        "options": {"kind":"articles 또는 collections", "order":"created_date,published_date,modified_date,views,shares,cites; articles에는 downloads도 가능", "order_direction":"asc,desc", "institution":"기관 ID", "group":"그룹 ID", "resource_doi":"연결 문헌 DOI", "doi":"레코드 DOI", "handle":"Handle", "published_since":"ISO 날짜", "modified_since":"ISO 날짜", "item_type":"articles 자료 유형 숫자", "project_id":"articles 프로젝트 ID", "collection_id":"현재 구성원 목록: query는 빈 문자열, 다른 필터 없이 사용"},
        "fetch": "article:ID 또는 숫자, collection:ID, 공개 Figshare URL·DOI를 사용한다. @N 또는 DOI .vN으로 버전을 고정한다. article:ID@N#file:ID는 그 파일만 선택한다. metadata·export는 JSON, abstract는 저자 초록으로 단정하지 않은 repository description이다. articles의 fulltext·supplementary는 원 파일이며 크기·MD5를 검증한다. collection supplementary는 현재 구성원 참조 목록이다. 각 DOI를 선택해 파일을 받는다.",
        "limits": "자격증명 없는 공개 경로만 사용한다. 요청 간격 1.05초. limit 1..1000, start 0..5000(OpenAPI); 실제 거절은 오류로 보존한다. 전체 검색 건수는 제공되지 않아 total=null이다. json/native export. 버전을 지정한 컬렉션의 과거 구성원 목록은 공개 경로가 없어 not_implemented다. 외부 is_link_only 파일은 selection_required이며 자동 방문하지 않는다. 파일 CDN은 확인된 Figshare downloader와 AIP S3 저장소만 허용하며 다른 저장소 경로는 source_boundary로 남긴다. 404는 비공개 자료의 읽기 권한 부재도 포함할 수 있다.",
        "examples": [{"tool":"search","arguments":{"source":"figshare","query":"","options":{"collection_id":7956296},"limit":2}},{"tool":"fetch","arguments":{"source":"figshare","target":"10.60893/figshare.aip.29678765.v1","parts":["metadata","supplementary"]}}],
        "official": ["https://docs.figshare.com/v2/", "https://docs.figshare.com/swagger.json"]},
    "zenodo": {
        "search": "query는 Zenodo 검색식이다. 필드:값, 따옴표 구문, AND·OR·NOT, 괄호를 사용한다. 예: metadata.title:mathlib.",
        "options": {"sort": "bestmatch,mostrecent 등", "communities": "커뮤니티 식별자", "type": "자료 유형", "subtype": "자료 하위 유형", "access_right": "접근 유형", "keywords": "키워드"},
        "fetch": "Zenodo record 번호, records/번호 URL, 10.5281/zenodo.번호 DOI 또는 해당 record의 파일 URL. fulltext·supplementary는 레코드의 파일을 회수하며, 파일 URL이면 그 파일만 선택한다. artifacts 배열에 이름과 참조를 반환한다. 파일 크기와 제공된 checksum을 원자료와 대조한다. abstract는 레코드의 description이다.",
        "limits": "검색 limit 1..100, start는 limit의 배수. json/native export. 파일 판본은 응답의 record_id로 고정한다. concept DOI가 개별 record로 해석되면 version_selection에 구별해 표시한다. 파일 실패도 이름별로 반환하며 다른 자료원으로 이동하지 않는다.",
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
    "limits": "별도 자격 없는 API만 사용한다. 검색 limit 1..100, start는 limit의 배수, 서비스는 한 검색에서 최대 1000건을 노출한다. 별도 인증이 필요한 전역 코드 검색은 사용하지 않는다. 파일 ref는 40자리 SHA 또는 태그·브랜치이며 /를 포함하는 ref는 owner/repo@ref:path 형식을 쓴다.",
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
    "search": "query는 보존된 origin URL을 찾는 문자열이다. 결과는 원 저장소 주소와 Software Heritage의 보존 기록 링크다.",
    "options": {"with_visit": "방문 기록을 가진 origin으로 한정하는 서비스 조건"},
    "fetch": "swh:1:cnt|dir|rev|rel|snp:40자리해시, archive.softwareheritage.org/swh:… 또는 n2t.net/swh:… 링크, 원 저장소 URL. 일반 URL은 Software Heritage 안의 origin 식별자이며 외부 사이트를 방문하지 않는다. cnt는 metadata의 SWHID·길이·체크섬과 실제 전체 파일의 sha1_git를 대조한다. 오류 때 이미 받은 metadata를 보존한다.",
    "qualifiers": "origin·visit·anchor·path·lines를 보존하며 중복·잘못된 값을 거부한다. origin은 해독·정제하고 path는 URI 이스케이프 표기를 유지한다. 이 문맥의 사실관계는 검증하지 않아 context_verified=false다. path를 다른 파일의 선택 경로로 해석하지 않는다. cnt의 lines=9-15는 1부터 시작하는 포함 범위이며 lines=9는 한 줄이다. fulltext/supplementary의 기본 artifact는 선택한 조각, complete_content는 검증된 전체 파일이다. integrity는 전체 파일에 대한 검사다. 범위가 없으면 기본 artifact가 전체 파일이다. 범위 초과는 not_found와 전체 파일 참조를 남기며 잘라 맞추지 않는다.",
    "archives": "dir의 fulltext/supplementary는 원 tar.gz 압축본이다. rev는 원 metadata의 directory에 해당하는 압축본을 반환하고 archive_selection에 그 관계를 남긴다. 준비된 압축본이 없으면 이메일 없이 생성을 요청한다. pending이면 retry_after_seconds 뒤 retry 입력으로 다시 조회한다. 전체 파일 내용·이름·권한·심볼릭 링크를 Git 트리 방식으로 해시해 디렉터리 SWHID와 대조한다. 불일치 또는 미지원 항목은 오류와 source_archive에 원 파일을 보존한다. extract로 목록을 읽고 selection에 정확한 경로를 주면 내부 파일 참조를 받는다. 그 참조를 다시 extract해 내용을 읽는다.",
    "limits": "별도 자격 없는 공개 API. start는 0으로 두고 다음 페이지에는 반환된 next.cursor를 그대로 준다. limit 1..100. 전체 origin 검색 건수는 서비스가 주지 않아 total=null. 파일 바이트를 실행하지 않는다. octet-stream으로 받은 UTF-8/NUL 없는 내용은 text/plain으로 읽고 원 MIME도 남긴다. 줄 선택은 이런 UTF-8 content에 한정한다. Vault는 flat 디렉터리 형식이며 Git 전체 이력, release·snapshot 아카이브는 아직 연결하지 않았다. 트리 검증은 일반 파일·디렉터리·심볼릭 링크를 지원한다. 하드 링크 등 다른 항목은 원 압축본과 미지원 상태를 반환한다.",
    "examples": [{"tool": "search", "arguments": {"source": "software-heritage", "query": "mathlib", "limit": 2}}, {"tool": "fetch", "arguments": {"source": "software-heritage", "target": "https://github.com/leanprover-community/mathlib4", "parts": ["metadata"]}}],
    "official": ["https://archive.softwareheritage.org/api/"],
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
    "search": "Crossmark에 등록된 갱신·정정·철회 정보는 Crossref 공개 REST API로 조회한다. query와 필드 옵션은 Crossref 문법이다. options.filter에 has-update-policy:true(갱신 정책 등록), has-update:true(다른 DOI로 갱신됨), is-update:true(다른 DOI의 갱신 문헌), updates:DOI(지정 문헌의 갱신) 등을 목적에 맞게 지정한다.",
    "fetch": "DOI의 원 등록 메타데이터 전체를 보존한다. update-policy·update-to·assertion·relation·content-domain 필드의 존재와 값을 extract로 확인한다. 필드가 없다는 사실로 정정이나 철회가 없다고 단정하지 않는다.",
    "examples": [{"tool": "search", "arguments": {"source": "crossmark", "query": "", "options": {"filter": "is-update:true"}, "limit": 2}}],
    "official": ["https://www.crossref.org/services/crossmark/", "https://www.crossref.org/documentation/retrieve-metadata/rest-api/rest-api-filters/"],
}

SOURCES["springer"].implementation = "partial"
SOURCES["springer"].capabilities = ("source_guide", "fetch", "export")
SOURCES["pqdt"].implementation = "partial"
SOURCES["pqdt"].transport = "playwright"
SOURCES["pqdt"].usage = {
    "search": "KUDOS → 학술DB → PQDT Global에서 query를 자료원 검색창에 그대로 제출한다. 예: TI(\"P versus NP\"). 필드 괄호와 AND·OR·NOT·큰따옴표 구문을 결합한다. TI는 제목, AU는 저자, AB는 초록, SU는 주제다. 화면의 개별 필터 제어는 개발 중이다.",
    "exports": "json은 검색 행과 native RIS의 원 필드를 함께 보존한다. ris는 Citation, abstract, indexing 옵션의 실제 원파일이다. html은 보존 검색 페이지의 참조다. 다른 native 형식 연결은 개발 중이다.",
    "fetch": "docview 문서 번호 또는 ProQuest docview 링크를 지정한다. publication number와 docview 번호는 다르다. metadata·abstract·export·fulltext·supplementary를 요청할 수 있다. 제목은 TI 후보 검색으로 반환한다. PDF는 같은 ProQuest의 실제 Download PDF 링크에서 회수한다.",
    "supplementary":"현재 docview의 Supplemental files 탭에서 원 건수·파일명·다운로드 제어를 대조하고 개별 파일을 회수한다. files의 artifact를 extract로 읽는다. 내부 다운로드 서명은 반환하지 않는다. 해당 탭이 노출되지 않은 문헌은 source_page로 보존하며 파일 부재로 단정하지 않는다.",
    "limits": "options는 비운다. start는 0부터, limit는 1..1000. 선택한 문서 ID와 RIS의 AN 필드를 대조한다. 일부 페이지 이동 제어는 검증 중이다. 첨부는 파일별 상태와 성공 자료를 유지하며 연구 코드를 실행하지 않는다.",
    "examples": [{"tool": "search", "arguments": {"source": "pqdt", "query": "TI(\"P versus NP\")", "limit": 1, "export": "ris"}}, {"tool": "fetch", "arguments": {"source": "pqdt", "target": "2618193239", "parts": ["metadata", "abstract", "fulltext"]}}],
}

SOURCES["ieee-xplore"].implementation = "partial"
SOURCES["ieee-xplore"].usage = {
    "search": "KUDOS → 학술DB → IEEE → Command Search에서 query를 그대로 입력한다. 필드 이름을 큰따옴표로 감싸고 콜론 뒤에 조건을 쓴다. 예: \"Document Title\":\"P versus NP\". AND·OR·NOT·괄호, 구문 따옴표, * 와일드카드 등을 IEEE 문법대로 사용한다.",
    "fields": ["All Metadata", "Full Text & Metadata", "Full Text Only", "Document Title", "Authors", "Publication Title", "Abstract", "Index Terms", "Article Number", "Author Affiliations", "Author Keywords", "DOI", "Funding Agency", "IEEE Terms", "ISBN", "ISSN", "Publisher", "Standard Number"],
    "exports": "json은 UI의 원 문헌 필드·초록이다. bibtex·ris·plain은 native Citations의 Citation and Abstract, csv는 native Results export다. 여러 페이지의 파일은 export.artifacts로 나누어 보존한다.",
    "fetch": "IEEE 문헌 번호, /document/번호 링크 또는 DOI를 지정한다. 서지·초록·원문 PDF를 해당 IEEE에서 회수한다. 제목은 후보 검색으로 반환한다. supplementary.references는 문헌 번호를 대조한 원 참고문헌 배열이며 artifact를 extract로 읽는다. order·id·title·text·links 등 원 필드를 보존하고 외부 인용 링크는 따라가지 않는다. supplementary.attachments는 문헌 metadata의 graphicalAbstract 파일·표지와 원 Media 탭 파일이다. 같은 파일이 두 화면 영역에 표시돼도 한 번만 회수하며 일반 도움말 링크는 제외한다. 파일별 역할·상태·artifact를 유지한다. MP4는 HTTP byte range와 버전 검증자를 대조하며 전체 바이트를 조립하고 각 요청의 제한은 45초다. 동영상 분석이나 연구 코드 실행은 수행하지 않는다. Media 탭의 파일은 supplementary_media 역할이며 native_index에 설명·파일명을 보존한다. 원 MP4 컨테이너와 40MB 다운로드를 실제 검증했으며 다른 파일 형식의 실측으로 확대하지 않는다. 원 metadata의 multimedia=false와 그래픽 초록 부재는 해당 문헌의 not_found이며 자료원 전체의 부재가 아니다.",
    "limits": "options는 비운다. start 0부터, limit 1..1000. 자료원의 25건 페이지를 순회한다. 추가 UI facet과 일부 페이지 이동 제어는 검증 중이다. 요청한 원 검색식과 실제 UI 요청을 대조한다.",
    "examples": [{"tool": "search", "arguments": {"source": "ieee-xplore", "query": "\"Document Title\":\"P versus NP\"", "limit": 1, "export": "bibtex"}}, {"tool": "fetch", "arguments": {"source": "ieee-xplore", "target": "10488889", "parts": ["metadata", "abstract", "fulltext"]}}],
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
    "fetch": "196516 같은 문헌 번호, urn:eudml:doc:번호 또는 eudml.org/doc/번호 링크. eudml-nlm 원 메타데이터를 확보하고 현재 문헌의 article/book metadata header에 있는 EuDML ID를 대조한다. 제목 입력은 defName 후보 검색으로 반환한다.",
    "exports": "json은 파싱한 레코드, native·rss는 원 RSS 표현, xml·html은 같은 검색 조건의 자료원 export다. year는 RSS dc:date이며 pubDate와 구별한다. fetch의 metadata·export·supplementary는 원 NLM 메타데이터다.",
    "limits": "options는 비운다. start는 0부터, limit는 1..1000. 원 RSS의 totalResults·startIndex를 대조한다. NLM에 본문이 없고 외부 원문 링크만 있는 경우 fulltext는 not_offered다. 원 저장소를 호출 AI가 별도 자료원으로 선택한다. XML 내부 항목은 extract selection에 ./front/article-meta/article-id 또는 .//{*}abstract 같은 경로로 지정한다.",
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
    "limits": "limit 1..100, start는 limit의 배수. 전체 건수는 null, native next 링크로 후속 페이지를 판단한다. 수백 명 이상의 저자도 records에는 전부 보존하고 preview에는 저자 수만 표시한다. metadata·abstract의 title/abstract는 자료원이 제공한 value와 format 객체를 유지한다.",
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
    'options': {'field': '기본 Anywhere, fields 중 하나', 'terms': '추가 고급검색 행 최대 두 개: [{field: Title, query: 검색식}]. 원 사이트의 행 결합을 사용한다.', 'publication': '저널·책·참고서 제목', 'after_year': '시작 연도 정수', 'after_month': '시작 월 1..12', 'before_year': '끝 연도 정수', 'before_month': '끝 월 1..12', 'sort': 'relevance(기본) 또는 date; 사이트의 Relevance/Date 제어'},
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
    'fulltext_html':'Nature 문헌 URL에서는 parts에 fulltext_html을 지정해 원 HTML 본문·TeX 수식·PNG/JPEG 그림을 별도로 회수한다. artifact의 HTML은 CSS selection으로 읽고 figures의 각 artifact는 extract로 이미지를 읽는다. HTML의 그림 src는 보존된 artifact ref다. 추천 문헌 위젯은 제외하며 초록만 있는 화면을 전문으로 표시하지 않는다. 그림 실패 때 본문과 파일별 오류를 partial로 보존한다. 이 추가 항목은 관측된 Nature 레이아웃에 한정하며 다른 Springer 레이아웃은 not_implemented다. MathJax 실행이나 이미지 의미 판독은 하지 않는다.',
    'supplementary':'현재 문헌의 원 Supplementary Information·Peer Review File 등 첨부 제어를 읽는다. supplementary.files의 각 artifact를 extract로 읽고 index는 파일 목록이다. 파일 경로에 다른 DOI가 있으면 해당 문헌을 명시적으로 선택하도록 반환한다. 일부 파일 실패 때 받은 파일은 유지한다. 첨부 제어를 인식하지 못한 레이아웃은 source_page로 보존한다.',
    'limits': 'KUDOS 기관 바로가기를 사용한다. start 0부터, limit 1..1000, 원 페이지는 20건이다. 문헌별 전문 제공 여부는 기관 이용 범위에 따른다. 검색 snippet을 저자 초록으로 표시하지 않는다.',
    'examples': [{'tool':'search','arguments':{'source':'springer','query':'P versus NP','options':{'field':'Title'},'limit':2,'export':'bibtex'}}],
    'official':['https://link.springer.com/advanced-search'],
}

SOURCES['oxford'].capabilities = ('source_guide','search','fetch','export')
SOURCES['oxford'].usage = {
    'search': 'query를 선택 필드의 Query Builder에 제출한다. exact=true는 구문 일치다. exact=false이면 해당 필드의 원 검색식으로 처리한다. 문헌 결과와 자료원의 표시 건수가 일치한 뒤 반환한다.',
    'options': {'field':'All(기본 검색), Full Text(고급검색의 본문 필드), Keywords, Title, Author, Abstract, References', 'exact':'구문 일치 여부, 기본 false', 'sort':'relevance(기본), newest, oldest, title_asc, title_desc'},
    'exports': 'json·html은 실제 문헌 결과, csv는 그 레코드의 기계적 CSV다. bibtex·ris·endnote·plain은 선택 문헌의 native citation 다운로드이며 export.artifacts의 ref로 읽는다. 사이트 Export title list는 책·저널 제목 목록이며 문헌 CSV와 다르고 CAPTCHA를 요구하므로 사용하지 않는다.',
    'fetch': 'Oxford Academic의 정확한 문헌 URL 또는 이 플랫폼으로 연결되는 DOI. 검색 결과의 url을 사용하면 같은 플랫폼의 해당 판본을 지정한다. metadata·abstract·fulltext·export·supplementary를 요청한다. export는 native BibTeX이며 그 DOI를 문헌 metadata와 대조한다. 제목 입력은 Title 검색 후보를 반환한다.',
    'supplementary':'문헌의 ArticleDataSupplements 위젯에 나열된 원 파일을 회수한다. 파일명·설명·DOI를 부호화한 경로를 보존하고 문헌 DOI와 대조한다. supplementary.files의 artifact를 extract로 읽는다. 다른 첨부 레이아웃은 source_page로 남긴다.',
    'limits': 'KUDOS 기관 접속. start 0부터, limit 1..1000, 원 페이지 20건. 제휴 출판사의 책, 저널·그림 같은 결과도 포함하므로 type을 보고 문헌을 선택한다. All과 Full Text는 다른 검색 범위다. 별도 계정이나 CAPTCHA가 필요한 기능을 자동 수행하지 않는다.',
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
    'exports':'json·html은 원 결과, csv는 같은 레코드의 기계적 CSV다. ris·native는 문헌에 연결된 RIS 다운로드이며 DOI를 대조한다. export.artifacts로 읽는다. DOI가 없는 자료 유형은 인용문 미확보를 따로 표시한다.',
    'fetch':'De Gruyter Brill의 DOI 또는 문헌 URL로 metadata·abstract·fulltext·export·supplementary를 요청한다. export는 native RIS다. 검색에는 책·장·논문 외 자료도 있으므로 type을 확인한다.',
    'supplementary':'Supplementary Material 목록의 원 다운로드 파일을 회수한다. downloadAsset 경로의 문헌 DOI를 대조하고 파일명·설명·파일별 상태를 유지한다. ZIP은 files의 artifact를 extract한 뒤 원 내부 파일 이름을 selection으로 선택한다. 오래된 제어가 404를 반환하면 그 파일의 not_found와 전체 partial을 보존한다.',
    'limits':'KUDOS의 De Gruyter 기관 바로가기를 사용한다. start 0부터, limit 1..1000, 원 페이지 10건. 자료원에 표시된 검색 건수와 실제 회수 행을 대조한다.',
    'examples':[{'tool':'search','arguments':{'source':'de-gruyter','query':'title:(complexity)','limit':2,'export':'ris'}}],
    'official':['https://www.degruyterbrill.com/search/advanced'],
}

SOURCES['jstor'].implementation='partial'
SOURCES['siam'].implementation='partial'
SOURCES['siam'].transport='playwright'
SOURCES['siam'].capabilities=('source_guide','fetch','export')
SOURCES['siam'].usage={
    'search':'원 SIAM 검색 화면은 존재하지만 현재 고급검색 연결과 실서비스 검증이 남아 있다. 검색은 publisher_search_not_implemented를 반환한다. 공개 홈페이지 뒤 convex optimization 검색은 접근 확인 화면이었다.',
    'fetch':'SIAM DOI·문헌 URL은 원 문헌 페이지에서 서지·초록·PDF를 조회한다. .pdf 주소와 epubs.siam.org/doi/pdf/DOI는 정확히 지정한 파일을 회수한다. 이 파일 경로의 metadata는 PDF 내장 정보이며 출판사 문헌 페이지의 서지와 구별한다.',
    'exports':'명시적 PDF 파일의 export는 그 원 PDF다. 문헌별 RIS·BibTeX 등 native 인용문 내보내기는 아직 연결하지 않았다. 기본 문헌 페이지 export의 source_metadata_json과 구별한다.',
    'limits':'기관 구독이나 추가 웹 계정 없이 제공되는 자료를 회수한다. 접근 제한은 그 문헌·경로의 결과이며 자료원 전체의 부재를 뜻하지 않는다. 책의 Front Matter·Back Matter는 별도 파일이다. 전체 책으로 확대하지 않는다.',
    'examples':[{'tool':'fetch','arguments':{'source':'siam','target':'https://epubs.siam.org/doi/pdf/10.1137/1.9781611974997.fm','parts':['metadata','fulltext']}}],
    'official':['https://epubs.siam.org/faq'],
}
SOURCES['ams'].implementation='partial'
SOURCES['ams'].transport='playwright'
SOURCES['ams'].capabilities=('source_guide','search','fetch','export')
SOURCES['ams'].usage={
    'search':'KUDOS → 학술DB → AMS 바로가기의 원 고급검색을 사용한다. options.field는 Title(기본), Author, ProductCode, BookText, ISBN, MSC다. BookText는 책 본문 검색이며 일반 전 자료원 본문 검색으로 바꾸지 않는다. MSC는 두 자리 분류이며 쉼표로 복수를 입력할 수 있다.',
    'options':'추가 title, author, product_code, book_text, isbn, msc를 결합할 수 있다. 주 field와 같은 추가 필드는 중복 지정하지 않는다. content_type은 All(기본), EBook, Journal, Abstracts다. start는 0부터, limit는 1..1000이며 원 페이지의 건수·위치를 대조한다.',
    'records':'Title와 Subtitle을 구별한다. ProductCode, DOI, PII, ContentType, RelatedCustomers, Abstract, ProductDescription 등 원 필드를 보존한다. target은 선택한 원 문헌 URL이다. 책(B)·논문(A)·학회 초록(ABS)이 섞이며 DOI가 없는 결과도 유지한다.',
    'exports':'json은 요청 창의 원 레코드, native는 해당 창을 회수하면서 읽은 원 JSON 페이지들, html은 방문한 검색 페이지들이다. csv는 같은 레코드를 기계적으로 직렬화한다. 사이트의 native 파일 내보내기는 HTTP 403 이후 미검증이며 구현 완료로 세지 않는다.',
    'fetch':'책 ProductCode 또는 /view?ProductCode= URL은 같은 원 고급검색으로 식별한다. 현재 서버에서 검색한 target·DOI는 원 메타데이터를 재사용한다. 다른 DOI·문헌 URL은 원 문헌 페이지를 조회하며 추가 접근 확인을 반환할 수 있다. 책의 ProductDescription은 출판사 책 소개이며 논문 초록과 구별한다. .pdf 링크는 정확히 지정한 파일과 PDF 내장 메타데이터를 회수한다. 발췌·부속 파일을 전체 책으로 확대하지 않는다.',
    'verification_limit':'원 브라우저의 algebra 검색 6,587건 중 12건과 혼합 레코드는 관측했다. 신규 어댑터는 이후 접근 확인·서비스 불가 응답 때문에 연속 검증을 완료하지 못했다. 서비스 불가는 provider_unavailable, 접근 확인은 restricted이며 0건이나 영구적인 기능 부재로 표시하지 않는다.',
    'examples':[{'tool':'search','arguments':{'source':'ams','query':'algebra','start':11,'limit':2,'export':'csv'}},{'tool':'fetch','arguments':{'source':'ams','target':'https://www.ams.org/books/gsm/128/gsm128-endmatter.pdf','parts':['metadata','fulltext']}}],
    'official':['https://pubs.ams.org/AdvancedSearch'],
}
SOURCES['project-euclid'].capabilities=('source_guide','search','fetch','export')
SOURCES['project-euclid'].usage={
    'search':'공개 원 고급검색 UI를 사용한다. 기본 query는 All Fields 검색이며 사이트의 어근·구문 처리를 유지한다. options.field는 ALL, ABSTRACT, AUTHORNAME, AFFILIATION, DOI_ISSN_ISBN, FIGURETABLECAPTIONS, KEYWORDS, TITLE 중 하나다.',
    'options':'terms는 추가 조건 배열이며 각 항목의 query, field, operator(AND/OR/NOT)를 원 UI에 입력한다. 첫 조건과 합계 20개까지다. year_from/year_to는 발행연도 정수이며 publication_titles는 정확한 발행물 제목 배열이다. 검색 결과 facets.ref를 extract(selection=/publication_titles)로 읽어 가능한 제목을 선택한다. sort는 Relevance, PubDateDesc, PubDateAsc, TitleAsc, TitleDesc이며 page_size는 25(기본), 50, 75, 100이다.',
    'pagination':'start는 0부터, limit는 1..1000이다. 표시된 원 페이지의 범위를 대조한다. 원 사이트는 50쪽까지 노출하므로 start+limit는 50*page_size 이하로 지정하고 더 먼 결과는 검색 조건을 좁힌다. 다음 쪽의 미리 받기 응답을 현재 쪽으로 사용하지 않는다.',
    'exports':'json은 보존한 문헌 레코드, html은 검색 페이지, csv는 같은 레코드의 기계적 CSV다. ris·bibtex·endnote·citation-pdf는 선택된 각 문헌의 Citation & Abstract 원 다운로드다. citation-pdf는 서지와 초록의 인쇄용 PDF이며 논문 전문은 fetch fulltext로 받는다. 실패한 문헌과 이미 받은 export를 함께 표시한다.',
    'fetch':'Project Euclid 문헌 URL·DOI로 서지·초록·PDF·원 인용문을 확보한다. 이름은 후보 검색이다. export는 BibTeX·RIS·EndNote·인용문 PDF를 반환한다. supplementary는 Supplemental Content 탭의 문헌별 PDF·ZIP을 회수한다. 원 문헌 DOI와 supplement_doi를 구별하고 파일명·설명·파일별 상태를 보존한다. 설명 속 외부 저장소는 자동 방문하지 않는다. files의 artifact로 ZIP 항목을 선택하고 내부 텍스트를 줄 단위로 읽는다. 탭 제어 부재는 source_page이며 실제 파일 링크의 오류를 보충자료 전체의 부재로 해석하지 않는다.',
    'examples':[{'tool':'search','arguments':{'source':'project-euclid','query':'complexity','options':{'field':'TITLE'},'start':24,'limit':2,'export':'csv'}}],
    'official':['https://projecteuclid.org/'],
}
SOURCES['jstor'].transport='api (native citation); browser search/document pending'
SOURCES['jstor'].capabilities=('source_guide','fetch','export')
SOURCES['jstor'].usage={
    'fetch':'JSTOR stable 번호, j.…·jj.… 도서/장 ID, stable URL 또는 10.2307 DOI로 metadata·abstract·export를 요청한다. 별도 자격 없는 native citation API를 사용한다. 도서와 논문의 원 RIS 유형·필드를 유지한다.',
    'exports':'export.artifacts에 원 RIS와 BibTeX를 반환한다. 기본 artifact는 RIS이며 제공자 안내문은 source_preamble로 유지한다. JSTOR의 Text file은 실제 BibTeX이고 source_media_type은 text/plain이다. RIS의 UR·BibTeX의 url에 있는 stable ID를 요청 대상과 대조하며 BibTeX DOI 필드가 없다고 실패시키지 않는다. 형식별 오류와 먼저 받은 인용문을 함께 보존하고 잘못된 문헌의 원 파일도 오류의 source_export로 읽을 수 있다.',
    'limits':'검색과 전문·첨부 회수는 아직 연결하지 않았다. 기관 검색은 실제 CAPTCHA를 반환했으며 자료원 자체의 문헌 부재로 해석하지 않는다. 초록이 없는 RIS에는 not_offered를 표시한다.',
    'examples':[{'tool':'fetch','arguments':{'source':'jstor','target':'345683','parts':['metadata','abstract','export']}}],
    'official':['https://www.jstor.org/'],
}

SOURCES['numdam'].transport = 'fixed: OAI/citation API; native search/DOI resolution Playwright'

SOURCES['science-direct'].implementation = 'partial'
SOURCES['science-direct'].capabilities = ('source_guide','fetch','export')
SOURCES['science-direct'].usage = {
    'fetch':'DOI·ScienceDirect PII·문헌 URL을 지정한다. KUDOS의 ScienceDirect 바로가기로 기관 접속한 뒤 원 RIS에서 서지·초록을 회수한다. RIS의 UR에 있는 PII와 DO의 DOI를 입력과 대조한다. PII와 DOI는 다른 식별자다.',
    'exports':'export는 RIS·BibTeX·plain의 원 파일이다. 제목은 RIS의 T1이며 초록은 AB다. BibTeX·plain도 같은 DOI를 대조한다. 원 서지와 초록을 파일 그대로 보존한다.',
    'limits':'검색·이름 후보와 첨부파일은 아직 연결하지 않았다. 문헌 HTML/abs 페이지의 접근 오류와 정상 기관 citation endpoint를 구별한다. fulltext가 실패해도 이미 받은 서지·초록·인용문을 보존하고 component별 실패를 반환한다. PDF 주소의 준비 HTML을 PDF로 표시하지 않는다. 별도 Elsevier API 키·웹 계정은 요구하지 않는다.',
    'examples':[{'tool':'fetch','arguments':{'source':'science-direct','target':'10.1006/jcss.1997.1494','parts':['metadata','abstract','export']}}],
    'official':['https://www.sciencedirect.com/'],
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
SOURCES['iop'].transport = 'playwright'
SOURCES['iop'].capabilities = ('source_guide','fetch','export')
SOURCES['iop'].usage = {
    'fetch':'IOP DOI 또는 정확한 iopscience.iop.org 문헌 URL을 지정한다. KUDOS IOP 바로가기를 거쳐 기관 문헌의 서지 태그와 PDF를 회수한다. 초록은 원 wd-jnl-art-abstract 영역을 사용한다.',
    'exports':'문헌에 표시된 BibTeX·RIS 링크의 DOI와 원 응답 DOI를 대조하는 코드를 연결했다. 이 추가 export의 실서비스 검증은 기관 진입 CAPTCHA 때문에 완료하지 못했다.',
    'limits':'검색·이름 후보는 아직 연결하지 않았다. 서지·16쪽 PDF를 실제 어댑터에서 확보한 기록, 이후 실제 MCP의 서지·초록 성공, 후속 기관 진입·파일 요청의 접근 제한을 구별한다. validate.perfdrive.com 등 접근 확인 목적지는 restricted로 반환하며 요청을 따라가지 않는다. XML·추가 첨부 형식은 연결하지 않았다.',
    'examples':[{'tool':'fetch','arguments':{'source':'iop','target':'https://iopscience.iop.org/article/10.1088/0022-3727/34/10/311/meta','parts':['metadata','fulltext']}}],
    'official':['https://iopscience.iop.org/'],
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

for category in ('author-repository','society-journal'):
    SOURCES[category].implementation = 'partial'
    SOURCES[category].transport = 'fixed: public document Playwright; OJS native citation API'
    SOURCES[category].capabilities = ('source_guide','fetch','export')
    SOURCES[category].usage = {
        'fetch':'알려진 공개 문서의 절대 HTTP(S) URL을 target으로 지정한다. 인증 상태를 공유하지 않는 공개 context로 PDF·HTML·기타 파일을 직접 회수한다. 등록된 플랫폼의 주소면 사용할 source를 반환한다. 임의 URL의 제목·DOI를 외부 서비스에서 추정하지 않는다.',
        'parts':'metadata는 PDF 내장 정보 또는 HTML의 공개 서지 태그 JSON. export는 OJS의 실제 citation_formats 제어가 있으면 공개 RIS·BibTeX API의 원 파일이며 DOI를 대조한다. 해당 제어가 없으면 서지 JSON이다. fulltext는 지정 URL의 내용이며 HTML에 같은 호스트의 citation_pdf_url이 있으면 그 PDF도 회수한다. abstract는 HTML에 표시된 abstract 영역. supplementary는 해당 페이지의 링크 목록이며 연결 파일 자체의 확보를 뜻하지 않는다.',
        'limits':'이 범주는 단일 검색 색인을 갖지 않는다. 이름·검색식·플랫폼 고급검색에는 구체 자료원을 먼저 선택한다. 직접 URL과 같은 호스트의 리디렉션만 허용하며 로컬·사설망 주소는 거부한다. 스크립트만 있는 초기 화면은 문서로 성공 처리하지 않는다. 별도 로그인은 수행하지 않는다.',
        'examples':[{'tool':'fetch','arguments':{'source':category,'target':'https://www.cs.toronto.edu/~sacook/homepage/ptime.pdf','parts':['metadata','fulltext']}}] if category=='author-repository' else [{'tool':'fetch','arguments':{'source':category,'target':'https://www.combinatorics.org/ojs/index.php/eljc/article/view/v1i1r1','parts':['metadata','abstract','fulltext','export']}}],
    }

for identifier, level in {
    "mathscinet": "live_mcp_search_exact_mr_four_citations_name_doi_review_pdf",
    "wos": "live_mcp_search_full_record_title_url_native_xls_extract",
    "eccc": "live_mcp_name_candidates_search_and_pinned_revision_fetch",
    "crossref": "live_mcp_search_native_citation_eight_formats_extract",
    "arxiv": "live_mcp_search_pinned_html_source_archive_tex_extract",
    "zbmath": "live_mcp_arbitrary_window_doi_legacy_link_license_state_references",
    "github": "live_adapter_pinned_file_fetch",
    "mathlib": "live_mcp_pinned_source_search_file_fetch_line_comparison",
    "math-comp": "live_mcp_pinned_source_search_file_fetch_line_comparison",
    "opencitations": "live_mcp_native_csv_window_oci_fetch_reference_count",
    "knu-fric": "live_mcp_catalogue_pagination_issn_fetch_zero_result",
    "general-web": "live_mcp_public_api_candidates_csv_extract_empty_result",
    "author-repository": "live_mcp_public_author_pdf_and_page_links",
    "society-journal": "live_mcp_public_journal_metadata_abstract_pdf_native_citations",
    "numdam": "live_mcp_native_search_citations_jats_pdf_djvu_fetch_pagination",
    "software-heritage": "live_mcp_verified_content_fragments_directory_revision_vault_extract; origin_adapter_observed",
    "openalex": "live_mcp_arbitrary_window_group_cursor_abstract_relationships_name_doi",
    "core": "live_mcp_search_extract; fetch_rate_limit; fulltext_notice_regression",
    "semantic-scholar": "live_mcp_search_extract; new_workflow_rate_limited; schema_regressions",
    "dblp": "access_challenge_observed",
    "dblp-kg": "live_mcp_sparql_window_native_csv_tsv_key_doi_name; native_tsv_year_type_mismatch",
    "zenodo": "live_mcp_search_file_checksum_fetch_extract",
    "figshare": "live_mcp_public_search_window_collection_versioned_file_md5_pdf_extract",
    "acm-dl": "live_mcp_search_citation_pdf_and_supplement_zip_inner_pdf_extract",
    "scopus": "live_mcp_search_fetch_references_pagination_cited_by_extract",
    "drops": "live_mcp_native_exports_pdf_html_codemeta_and_supplementary_references",
    "springer": "live_mcp_advanced_search_citations_pdf_supplements_and_nature_html_tex_figure",
    "ieee-xplore": "live_mcp_search_citation_pdf_references_graphical_and_native_media_tab",
    "crossmark": "live_mcp_search_extract",
    "afp": "live_mcp_entry_search_pinned_metadata_and_proof_source_fetch_extract",
    "unpaywall": "public_endpoint_contact_requirement_observed",
    "theory-of-computing": "live_mcp_indexes_citation_pdf_source_ps_references_fetch_and_text_pagination",
    "pqdt": "live_mcp_repeat_search_ris_pdf_and_supplemental_png_fetch_extract",
    "eudml": "live_mcp_cql_rss_extract_nlm_fetch",
    "aps": "live_mcp_open_access_feed_metadata_abstract_pdf_fetch",
    "aps-institutional": "live_adapter_metadata_and_fulltext_restriction",
    "project-euclid": "live_mcp_advanced_search_four_citations_pdf_and_supplement_zip_text_extract",
    "cambridge": "live_mcp_filtered_search_ris_pdf_and_supplement_pdf_zip_source_extract",
    "oxford": "live_mcp_search_citation_metadata_abstract_pagination_and_supplement_pdf",
    "aip": "live_mcp_advanced_search_citation_pdf_and_explicit_figshare_supplement_reference",
    "wiley": "live_mcp_advanced_search_citations_pdf_empty_repeat_and_supplementary_zip",
    "taylor-francis": "live_mcp_search_citation_pdf_dublin_doi_supplement_zip_tables_nested_source",
    "de-gruyter": "live_mcp_search_ris_pdf_and_supplement_zip_cif_lines; broken_link_observed",
    "jstor": "live_mcp_public_ris_bibtex_article_and_jj_book; web_search_pending",
    "iop": "live_mcp_metadata_abstract; earlier_adapter_pdf; file_and_gateway_challenge",
    "siam": "live_mcp_public_front_matter_pdf_fetch_extract; search_challenge_observed",
    "ams": "live_mcp_explicit_pdf; native_browser_mixed_search; search_adapter_restricted",
    "science-direct": "live_mcp_institutional_ris_bibtex_plain_metadata_abstract_fetch",
}.items():
    SOURCES[identifier].verification = level


def source_info(identifier):
    try:
        return SOURCES[identifier]
    except KeyError:
        raise ServiceError("unknown_source", "Unknown source; use list_sources") from None
