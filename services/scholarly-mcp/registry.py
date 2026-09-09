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

SOURCES["scopus"].implementation = "partial"
SOURCES["scopus"].usage = {
    "search": "KUDOS → 학술DB → Scopus → Advanced document search. query는 고급검색식 그대로 제출한다. 예: TITLE(\"P versus NP\"), TITLE-ABS-KEY(\"natural proofs\") AND PUBYEAR > 2020. AND·OR·AND NOT, 괄호, 큰따옴표 구문, 중괄호 정확 구문, W/n·PRE/n 근접 연산자는 Scopus 문법을 따른다.",
    "fields": {"TITLE": "제목", "ABS": "초록", "KEY": "키워드", "TITLE-ABS-KEY": "제목·초록·키워드", "AUTHLASTNAME": "저자 성", "AFFIL": "소속", "PUBYEAR": "발행연도", "DOI": "DOI", "EID": "Scopus 문서 ID"},
    "options": "options는 비운다. start는 0부터, limit는 1..1000. 기본 UI 정렬을 사용하며 primary 문서의 totalCount와 페이지를 대조한다. preprint 별도 집계는 섞지 않는다.",
    "exports": "json은 UI가 받은 전체 원 필드, csv는 같은 필드를 기계적으로 직렬화하며 중첩값은 JSON 셀이다. native RIS·BibTeX는 별도 웹 계정을 요구하므로 사용자 지시에 따라 보류한다. 요청 시 export_deferred와 검색 원자료를 반환하며 계정 입력을 요청하지 않는다.",
    "fetch": "EID(2-s2.0-숫자) 또는 DOI로 색인의 서지·초록을 확보한다. 제목은 TITLE 후보 검색으로 돌려준다. 출판사 원문·인용 관계의 별도 조회는 이 구현의 확보 범위에 포함되지 않는다.",
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
    "evidence": "2026-09-09 KUDOS 프록시 검색 입력·고급 필드·export 제어 실측. 다섯 도구의 실사용 검증은 별도 보고에 기록한다.",
}

SOURCES["wos"].usage = {
    "search": "query는 Web of Science Core Collection의 Query Builder 검색식이다. KUDOS의 Web of Science CPCI 바로가기로 같은 Core Collection에 기관 접속한다. Editions=All의 기관 이용 범위를 사용한다.",
    "fields": {"TS": "주제", "TI": "제목", "AB": "초록", "AU": "저자", "AI": "저자 식별자", "AK": "저자 키워드", "GP": "단체 저자", "ED": "편집자", "KP": "Keywords Plus", "SO": "발행물명", "DO": "DOI", "PY": "발행연도", "CF": "학회", "AD": "주소", "OG": "소속", "OO": "기관", "SU": "연구 영역", "WC": "WoS 분류", "IS": "ISSN/ISBN", "UT": "접근번호", "DOP": "발행일", "LD": "색인일", "ALL": "전체 필드"},
    "operators": "FIELD=(조건), AND·OR·NOT, 괄호와 큰따옴표 구문. * 등 와일드카드와 날짜 범위는 WoS 문법을 따른다. 예: TS=(\"circuit lower bounds\") AND PY=(2020-2025). 세션 #번호 결합은 다른 호출에서 같은 세션을 보장하지 않으므로 독립 검색식으로 전달한다.",
    "options": "현재 options는 비운다. 검색식 안의 필드·연도 조건을 지원하며 UI의 추가 facet·정렬·edition 지정은 구현 중이다.",
    "fetch": "WOS:접근번호 또는 DOI. 전체 서지·초록·인용문헌을 해당 색인에서 회수한다. 논문 전문은 해당 출판사를 별도 source로 지정한다.",
    "exports": "기본 JSON 레코드는 Full Record and Cited References 텍스트 export를 손실 없이 파싱한다. plain은 같은 원파일. ris·bibtex·excel·tsv·html은 해당 native export의 Full Record이며 실제 제공 필드가 다를 수 있다.",
    "limits": "start는 0부터, limit는 1..1000. 큰 결과를 화면 카드 개수로 세지 않고 자료원의 count와 요청 범위의 export를 대조한다. 원 tags는 records의 fields 아래 소문자 키·원 줄 배열로 보존한다. cr은 인용문헌, ab는 초록, ut는 접근번호다.",
    "examples": [{"tool": "search", "arguments": {"source": "wos", "query": "TI=(\"P versus NP\")", "limit": 5, "export": "plain"}}],
    "official": ["https://webofscience.help.clarivate.com/en-us/Content/advanced-search.html", "https://clarivate.libguides.com/webofscienceplatform"],
}

SOURCES["eccc"].transport = "playwright"
SOURCES["eccc"].implementation = "partial"
SOURCES["eccc"].usage = {
    "search": "query를 ECCC의 검색창에 그대로 제출한다. 현재 UI는 하나의 검색어 입력을 제공한다. options는 비운다. 원 검색의 중복 행과 snippet을 보존하며 자동으로 문헌을 합치지 않는다.",
    "fetch": "TRyy-nnn 또는 보고서 링크. TRyy-nnnrN 또는 revision/N/download 링크로 판본을 고정한다. 판본 생략 시 실제 페이지의 가장 높은 revision을 선택하고 정확한 번호와 다른 판본 목록을 반환한다. r0은 최초 보고서다.",
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
    "limits": "KUDOS 기관 프록시와 기본 Firefox를 사용한다. start 0부터, limit 1..1000. 추가 분류 facet·필드 사이 OR 편집·HTML 전용 전문·첨부파일 자동 회수는 구현 중이다.",
    "examples": [{"tool": "search", "arguments": {"source": "acm-dl", "query": "\"The complexity of theorem-proving procedures\"", "options": {"field": "Title", "collection": "fulltext"}, "limit": 2, "export": "bibtex"}}, {"tool": "fetch", "arguments": {"source": "acm-dl", "target": "10.1145/800157.805047", "parts": ["metadata", "abstract", "fulltext"]}}],
    "official": ["https://dl.acm.org/search/advanced"],
}

API_USAGE = {
    "crossref": {
        "search": "query는 관련도 검색어다. Boolean 필드 검색식으로 해석하지 않는다. 제목·저자 등은 options의 query.title, query.author, query.bibliographic, query.container-title, query.affiliation으로 지정한다.",
        "options": {"filter": "쉼표로 조건 결합. from-pub-date:YYYY-MM-DD,until-pub-date:YYYY-MM-DD,type:journal-article,has-abstract:true,has-full-text:true,doi:DOI,issn:ISSN 등", "sort": "relevance,published,created,updated,is-referenced-by-count 등", "order": "asc 또는 desc", "select": "호출자가 원하는 원 필드 이름의 쉼표 목록", "facet": "자료원이 지원하는 집계 필드:건수"},
        "fetch": "DOI 또는 https://doi.org/DOI. 서지·등록 초록·참고문헌·relation·정정 정보를 원 필드로 보존한다. 전문 링크는 남기되 해당 출판사를 자동 방문하지 않는다.",
        "limits": "limit 1..1000. 깊은 페이지는 cursor='*'로 시작하고 next.cursor를 사용한다. 결과와 원응답 export는 json/native. 다른 서지 export 형식의 개발 상태는 호출 결과로 구별한다.",
        "examples": [{"tool": "search", "arguments": {"source": "crossref", "query": "P versus NP", "options": {"filter": "from-pub-date:1970-01-01"}, "limit": 2}}, {"tool": "fetch", "arguments": {"source": "crossref", "target": "10.1145/321250.321251", "parts": ["metadata"]}}],
        "official": ["https://www.crossref.org/documentation/retrieve-metadata/rest-api/", "https://api.crossref.org/swagger-ui/index.html"]},
    "arxiv": {
        "search": "필드 태그 ti(제목),au(저자),abs(초록),cat(분류),co(주석),jr(저널),rn(보고번호),id(식별자),all(전체)을 쓴다. AND,OR,ANDNOT와 괄호로 결합하며 구문은 큰따옴표로 묶는다. 예: cat:cs.CC AND ti:\"circuit lower bounds\".",
        "options": {"sort_by": "relevance,lastUpdatedDate,submittedDate", "sort_order": "ascending,descending"},
        "fetch": "arXiv ID 또는 abs/pdf/src 링크. vN을 주면 그 판본을 요구한다. 생략하면 응답의 정확한 vN을 결박한다. fulltext는 PDF, supplementary는 arXiv가 제공한 TeX/source 묶음이며 소스 파일의 존재는 자료마다 다르다.",
        "limits": "limit 1..2000, start는 0부터. 호출 간 최소 3초. 검색 native export는 Atom, json은 추출 레코드. PDF 텍스트와 이미지 읽기는 extract.",
        "examples": [{"tool": "search", "arguments": {"source": "arxiv", "query": "ti:\"P versus NP\"", "limit": 2}}],
        "official": ["https://info.arxiv.org/help/api/user-manual.html"]},
    "dblp": {
        "search": "대소문자를 구별하지 않는 접두어 검색이다. 공백은 AND, |는 OR이며 단어 뒤 $는 정확한 단어를 지정한다. 제목·저자·venue·연도 등 DBLP 검색 색인의 텍스트를 대상으로 한다.",
        "options": {}, "fetch": "journals/… 또는 conf/… 형태의 DBLP key나 /rec/ 링크. 원 XML 서지를 보존한다. 초록과 논문 전문을 제공하는 색인이 아니다.",
        "limits": "현재 limit 1..100. start로 순회. json/native 검색 export. API가 HTML 접근 확인 화면을 반환하면 restricted이며 브라우저로 전환하지 않는다.",
        "examples": [{"tool": "search", "arguments": {"source": "dblp", "query": "P versus NP", "limit": 2}}],
        "official": ["https://dblp.org/faq/How+to+use+the+dblp+search+API.html", "https://dblp.org/db/"]},
    "zbmath": {
        "search": "query는 zbMATH 문법이다. ti:제목,au:저자,cc:MSC,py:연도 등의 필드 태그와 & (AND), | (OR), 괄호를 사용한다. 구조화 검색에서는 query를 비우고 options에 Title, Author name, MSC, Year, DOI 등 표시 필드 이름과 값을 준다.",
        "options": {"Title": "문헌 제목", "Author name": "저자명", "MSC": "분류코드. * 접두사는 주분류로 한정", "Year": "연도 또는 2000-2020", "DOI": "DOI", "Document type": "j 저널논문,a 수록논문,b 책,p 프리프린트", "Database": "Zbl,JFM,eram,arxiv"},
        "fetch": "zbMATH 문헌 ID 또는 zbmath.org/ID. 리뷰·요약은 원래 필드와 제공 상태를 보존한다.",
        "limits": "limit 1..100. start는 limit의 배수. 검색식과 구조화 필드는 한 요청에서 혼용하지 않는다. 추가 구조화 필드는 source_options 전체 목록에 있다.",
        "examples": [{"tool": "search", "arguments": {"source": "zbmath", "query": "", "options": {"Title": "P versus NP"}, "limit": 2}}],
        "official": ["https://api.zbmath.org/v1/openapi.json", "https://api.zbmath.org/"]},
    "openalex": {
        "search": "query는 works의 텍스트 검색이다. options.filter는 field:value를 쉼표로 결합하고 값의 |는 OR, !는 제외를 뜻한다. 날짜·종류·저자·source·인용 관계를 필터링한다.",
        "options": {"filter": "예: from_publication_date:2020-01-01,type:article 또는 cites:W…", "sort": "필드:asc/desc. 예: publication_date:desc", "select": "반환할 원 필드 이름의 쉼표 목록"},
        "fetch": "W로 시작하는 OpenAlex ID 또는 DOI. 초록은 abstract_inverted_index 원자료로 보존한다. locations는 후보 링크이며 외부 전문을 자동 확보하지 않는다.",
        "limits": "limit 1..200. start는 limit의 배수 또는 cursor='*'와 next.cursor 사용. 실행 환경에서 확인한 키 없는 접근은 향후 접근 보장을 뜻하지 않는다.",
        "examples": [{"tool": "search", "arguments": {"source": "openalex", "query": "P versus NP", "limit": 2}}],
        "official": ["https://developers.openalex.org/"]},
    "semantic-scholar": {
        "search": "query는 논문 텍스트 검색어다. 연도·학문 분야·발행 유형·venue·공개 PDF 조건은 options로 준다.",
        "options": {"year": "2020 또는 2020-2025", "fieldsOfStudy": "Computer Science,Mathematics 등", "publicationTypes": "JournalArticle,Conference,Review 등", "venue": "발행처 이름의 쉼표 목록", "openAccessPdf": "공개 PDF 존재 조건", "minCitationCount": "최소 인용 수", "publicationDateOrYear": "날짜 또는 기간", "fields": "필요한 원 필드 이름의 쉼표 목록"},
        "fetch": "paperId, DOI, ARXIV:id 또는 CorpusId:id. 초록·서지·인용 관계를 보존한다. openAccessPdf의 외부 호스트는 자동 방문하지 않는다.",
        "limits": "limit 1..100, start로 순회. 별도 자격 없는 공개 접근만 사용한다. 429는 요청 제한이며 자료 부재가 아니다. 실행 중 브라우저로 전환하지 않는다.",
        "examples": [{"tool": "search", "arguments": {"source": "semantic-scholar", "query": "P versus NP", "limit": 2}}],
        "official": ["https://api.semanticscholar.org/api-docs/graph"]},
}
for identifier, usage in API_USAGE.items():
    SOURCES[identifier].usage = usage
    SOURCES[identifier].implementation = "partial"

MORE_API_USAGE = {
    "opencitations": {
        "search": "query에 DOI 또는 doi:…,pmid:…,omid:… 식별자를 넣는다. 키워드 검색 대신 지정 문헌의 인용 관계를 조회한다.",
        "options": {"direction": "references는 나가는 참고문헌, citations는 들어오는 인용", "filter": "필드:값 또는 필드:>값, 필드:<값. 정규식 값도 서비스 문법대로 사용", "sort": "asc(필드) 또는 desc(필드)", "require": "값이 존재해야 하는 필드"},
        "fetch": "지정 식별자의 참고문헌 관계를 반환한다. 연결된 논문은 자동 확보하지 않는다.",
        "limits": "API가 반환한 전체 관계는 evidence로 보존하고 start·limit 창은 records에 둔다. json/native export. 전체 반환을 모든 자료원의 인용 관계로 해석하지 않는다.",
        "examples": [{"tool": "search", "arguments": {"source": "opencitations", "query": "doi:10.1145/321250.321251", "options": {"direction": "references"}, "limit": 2}}],
        "official": ["https://api.opencitations.net/index/v2"]},
    "numdam": {
        "search": "현재 공개 OAI의 collection/date 열거를 지원한다. query는 비운다. 웹의 키워드 검색은 아직 구현 중이며 그 부재를 서비스 자체의 한계로 보지 않는다.",
        "options": {"set": "OAI collection 식별자", "from": "메타데이터 갱신 시작일 YYYY-MM-DD", "until": "메타데이터 갱신 종료일", "metadata_format": "eudml-article2 또는 oai_dc"},
        "fetch": "Numdam native ID를 사용한다. JATS 원 메타데이터와 원문 링크를 보존하고 요청한 PDF를 같은 Numdam에서 받는다. 링크·DOI·이름 해석은 후속 구현 대상이다.",
        "limits": "OAI 페이지 크기는 자료원이 정한다. 모든 수신분을 보존하고 extract로 선택한다. 다음 페이지는 next.cursor. PDF와 DJVU는 구별하며 현재 자동 원문 확보는 PDF.",
        "examples": [{"tool": "fetch", "arguments": {"source": "numdam", "target": "AIF_1956__6__1_0", "parts": ["metadata", "fulltext"]}}],
        "official": ["https://www.numdam.org/metadata/"]},
    "core": {
        "search": "query는 CORE 검색식이다. title:\"P versus NP\"처럼 필드를 지정할 수 있다. 원 검색 결과의 모든 필드를 보존한다.",
        "options": {"sort": "CORE 정렬 조건. 제공자가 거절한 조건은 오류로 반환한다."},
        "fetch": "CORE works 번호 또는 core.ac.uk/works/번호. 해당 레코드의 서지·초록·fullText를 회수한다. 다른 저장소의 링크는 자동 방문하지 않는다.",
        "limits": "별도 자격 없는 공개 접근만 사용한다. limit 1..100, start는 0부터. 호출 간격 최소 2.1초. json/native export.",
        "examples": [{"tool": "search", "arguments": {"source": "core", "query": "title:\"P versus NP\"", "limit": 2}}],
        "official": ["https://core.ac.uk/services/api", "https://api.core.ac.uk/docs/v3"]},
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
    "fetch": "swh:1:cnt|dir|rev|rel|snp:40자리해시 또는 원 저장소 URL. URL은 Software Heritage 안의 origin 식별자로 조회하며 그 외부 사이트를 방문하지 않는다. cnt는 요청한 파일 바이트도 회수한다.",
    "limits": "별도 자격 없는 공개 API. start는 0으로 두고 다음 페이지에는 반환된 next.cursor를 그대로 준다. limit 1..100. 전체 origin 검색 건수는 서비스가 주지 않아 total=null. directory·revision의 재귀 아카이브 생성은 아직 지원하지 않는다.",
    "examples": [{"tool": "search", "arguments": {"source": "software-heritage", "query": "mathlib", "limit": 2}}, {"tool": "fetch", "arguments": {"source": "software-heritage", "target": "https://github.com/leanprover-community/mathlib4", "parts": ["metadata"]}}],
    "official": ["https://archive.softwareheritage.org/api/"],
}

SOURCES["drops"].implementation = "partial"
SOURCES["drops"].transport = "fixed: metadata API; search/document links Playwright"
SOURCES["drops"].usage = {
    "search": "query를 DROPS Search All Entities 입력에 그대로 제출한다. 문헌·volume·artifact 등 실제 검색 결과를 보존한다. options는 비운다.",
    "fetch": "10.4230/… DOI 또는 drops.dagstuhl.de/entities/… 링크. 서지·초록은 별도 자격 없는 metadata/schema-org 응답으로 회수한다. 원문을 요청하면 해당 문헌 페이지의 실제 PDF 링크를 찾아 같은 DROPS에서 받는다.",
    "exports": "검색은 json 또는 html. fetch의 metadata·export는 원 Schema.org JSON이다. XML·BibTeX 등 나머지 native 형식의 연결은 구현 중이다.",
    "limits": "start 0부터, limit 1..1000. 기능별 경로는 고정되어 있다. 서지 API 실패를 브라우저 전환 조건으로 쓰지 않는다. 추가 첨부파일은 source_page에 보존하되 자동 분류·회수는 구현 중이다.",
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
SOURCES["springer"].usage = {
    "fetch": "Springer 문헌의 DOI 또는 정확한 link.springer.com·link.springernature.com 문헌 링크를 지정한다. KUDOS Springer eJournal 경로로 접속한 뒤 문헌 페이지의 서지·초록·문헌 PDF를 회수한다. metadata·abstract·fulltext·export·supplementary를 선택할 수 있다.",
    "exports": "export는 페이지가 제공하는 서지 필드를 보존한 JSON이다. supplementary는 부록 링크가 포함된 정제 원 페이지이며 첨부파일 자동 회수는 구현 중이다.",
    "search": "출판사의 검색·고급검색·native citation export 연결은 개발 중이다. 제목으로 fetch하는 기능도 개발 중이므로 정확한 DOI 또는 문헌 링크를 사용한다.",
    "limits": "별도 자격 없는 API 경로가 아닌 기관 웹 경로로 고정한다. PDF와 HTML 전용 자료를 구별하며 인식하지 못한 형식은 not_implemented로 표시한다.",
    "examples": [{"tool": "fetch", "arguments": {"source": "springer", "target": "10.1007/s00037-008-0249-x", "parts": ["metadata", "abstract", "fulltext"]}}],
}

SOURCES["pqdt"].implementation = "partial"
SOURCES["pqdt"].transport = "playwright"
SOURCES["pqdt"].usage = {
    "search": "KUDOS → 학술DB → PQDT Global에서 query를 자료원 검색창에 그대로 제출한다. 예: TI(\"P versus NP\"). 필드 괄호와 AND·OR·NOT·큰따옴표 구문을 결합한다. TI는 제목, AU는 저자, AB는 초록, SU는 주제다. 화면의 개별 필터 제어는 개발 중이다.",
    "exports": "json은 검색 행과 native RIS의 원 필드를 함께 보존한다. ris는 Citation, abstract, indexing 옵션의 실제 원파일이다. html은 보존 검색 페이지의 참조다. 다른 native 형식 연결은 개발 중이다.",
    "fetch": "docview 문서 번호 또는 ProQuest docview 링크를 지정한다. publication number와 docview 번호는 다르다. metadata·abstract·export·fulltext를 요청할 수 있다. 제목은 TI 후보 검색으로 반환한다. PDF는 같은 ProQuest의 실제 Download PDF 링크에서 회수한다.",
    "limits": "options는 비운다. start는 0부터, limit는 1..1000. 선택한 문서 ID와 RIS의 AN 필드를 대조한다. 별도 첨부파일과 일부 페이지 이동 제어는 검증 중이다.",
    "examples": [{"tool": "search", "arguments": {"source": "pqdt", "query": "TI(\"P versus NP\")", "limit": 1, "export": "ris"}}, {"tool": "fetch", "arguments": {"source": "pqdt", "target": "2618193239", "parts": ["metadata", "abstract", "fulltext"]}}],
}

SOURCES["ieee-xplore"].implementation = "partial"
SOURCES["ieee-xplore"].usage = {
    "search": "KUDOS → 학술DB → IEEE → Command Search에서 query를 그대로 입력한다. 필드 이름을 큰따옴표로 감싸고 콜론 뒤에 조건을 쓴다. 예: \"Document Title\":\"P versus NP\". AND·OR·NOT·괄호, 구문 따옴표, * 와일드카드 등을 IEEE 문법대로 사용한다.",
    "fields": ["All Metadata", "Full Text & Metadata", "Full Text Only", "Document Title", "Authors", "Publication Title", "Abstract", "Index Terms", "Article Number", "Author Affiliations", "Author Keywords", "DOI", "Funding Agency", "IEEE Terms", "ISBN", "ISSN", "Publisher", "Standard Number"],
    "exports": "json은 UI의 원 문헌 필드·초록이다. bibtex·ris·plain은 native Citations의 Citation and Abstract, csv는 native Results export다. 여러 페이지의 파일은 export.artifacts로 나누어 보존한다.",
    "fetch": "IEEE 문헌 번호, /document/번호 링크 또는 DOI를 지정한다. 서지·초록·원문 PDF를 해당 IEEE에서 회수한다. 제목은 후보 검색으로 반환한다. supplementary는 원 문헌 페이지이며 개별 부록 다운로드는 개발 중이다.",
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
    'limits': 'KUDOS 기관 바로가기를 사용한다. start 0부터, limit 1..1000이며 원 페이지는 20건이다. 검색 결과와 export 실패는 각각 보존한다. 문헌별 이용 권한에 따라 전문이 제한될 수 있다.',
    'examples': [{'tool': 'search', 'arguments': {'source': 'wiley', 'query': 'random graphs', 'options': {'field': 'Title'}, 'start': 19, 'limit': 2, 'export': 'bibtex'}}],
    'official': ['https://onlinelibrary.wiley.com/search/advanced'],
}

SOURCES['springer'].capabilities = ('source_guide','search','fetch','export')
SOURCES['springer'].usage = {
    'search': 'query는 검색식이다. field=Anywhere(기본), Title, Author를 선택한다. 큰따옴표는 구문, AND·OR·NOT·괄호는 Springer 검색 문법을 따른다. 추가 제목·저자·저널·날짜 조건은 고급검색의 해당 필드로 제출한다.',
    'options': {'field': 'Anywhere, Title, Author', 'title': '제목 조건', 'author': '저자 조건', 'journal': '저널 제목', 'date_from': '시작 연도', 'date_to': '끝 연도', 'content_type': 'Article, Chapter, Conference Paper, Research 등 사이트의 표시 값', 'open_access': 'true이면 공개 접근으로 한정', 'language': 'En 등 사이트 언어 코드', 'subject': '사이트 주제 값', 'discipline': '사이트 학문 분야 값', 'subdiscipline': '사이트 세부 분야 값', 'sort': 'relevance, newest, oldest'},
    'exports': 'json·html은 원 결과를 보존한다. csv는 같은 레코드의 기계적 CSV다. 사이트 일괄 CSV 제어는 로그인 경로로 이동하며 사용하지 않는다. bibtex·ris·endnote는 각 선택 문헌의 native citation 다운로드이며 export.artifacts에 파일 참조를 반환한다.',
    'fetch': 'DOI 또는 Springer 문헌 URL. metadata·abstract·fulltext·export·supplementary를 요청한다. export는 해당 문헌의 native BibTeX다. 제목은 검색 후보로 반환하므로 정확한 문헌을 선택한다.',
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
    'limits': 'KUDOS 기관 접속. start 0부터, limit 1..1000, 원 페이지 20건. 제휴 출판사의 책, 저널·그림 같은 결과도 포함하므로 type을 보고 문헌을 선택한다. All과 Full Text는 다른 검색 범위다. 별도 계정이나 CAPTCHA가 필요한 기능을 자동 수행하지 않는다.',
    'examples': [{'tool':'search','arguments':{'source':'oxford','query':'P versus NP','options':{'field':'Title','exact':True},'limit':2,'export':'bibtex'}}],
    'official':['https://academic.oup.com/search-results'],
}

SOURCES['aip'].capabilities = ('source_guide','search','fetch','export')
SOURCES['aip'].usage = {
    'search': 'query를 AIP Query Builder의 선택 필드에 제출한다. 추가 검색 행은 terms로 AND·OR·NOT을 결합한다. exact는 화면의 Exact Match 설정이다. 자료원의 검색 확장·어간 처리까지 문자열 동일성으로 해석하지 않는다.',
    'options': {'field':'All(기본), Title, Author, Author Affiliations, Full Text, Abstract, Keyword, DOI, ISBN, EISBN, ISSN, EISSN, Issue, Volume, References', 'exact':'화면의 Exact Match 설정, 기본 false', 'terms':'추가 행 배열. 각 행은 field와 query, 선택적으로 condition(AND·OR·NOT, 기본 AND), exact(기본 false)를 지정한다.', 'sort':'relevance, newest, oldest'},
    'exports': 'json·html은 실제 문헌 결과, csv는 같은 레코드의 기계적 CSV다. bibtex·ris·endnote는 문헌별 native citation 다운로드다. export.artifacts의 ref로 읽는다.',
    'fetch': 'AIP 플랫폼의 DOI 또는 정확한 문헌 URL로 metadata·abstract·fulltext·export·supplementary를 요청한다. abstract는 현재 문헌의 native BibTeX abstract 필드를 보존하며 export와 같은 파일을 재사용한다. 제목은 Title 검색 후보를 반환한다. 문헌 PDF의 이용 권한은 해당 출판물에 따른다.',
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
    'limits':'KUDOS의 De Gruyter 기관 바로가기를 사용한다. start 0부터, limit 1..1000, 원 페이지 10건. 자료원에 표시된 검색 건수와 실제 회수 행을 대조한다.',
    'examples':[{'tool':'search','arguments':{'source':'de-gruyter','query':'title:(complexity)','limit':2,'export':'ris'}}],
    'official':['https://www.degruyterbrill.com/search/advanced'],
}

SOURCES['jstor'].implementation='partial'
SOURCES['jstor'].transport='api (native citation); browser search/document pending'
SOURCES['jstor'].capabilities=('source_guide','fetch','export')
SOURCES['jstor'].usage={
    'fetch':'JSTOR stable 번호, stable URL 또는 10.2307 DOI로 metadata·abstract·export를 요청한다. 별도 자격 없는 native RIS API를 사용한다.',
    'exports':'export는 원 RIS다. 제공자 안내문을 source_preamble로 유지하며 원 파일도 그대로 보존한다. UR의 stable ID와 요청 대상을 대조한다.',
    'limits':'검색과 전문·첨부 회수는 아직 연결하지 않았다. 기관 검색은 실제 CAPTCHA를 반환했으며 자료원 자체의 문헌 부재로 해석하지 않는다. 초록이 없는 RIS에는 not_offered를 표시한다.',
    'examples':[{'tool':'fetch','arguments':{'source':'jstor','target':'345683','parts':['metadata','abstract','export']}}],
    'official':['https://www.jstor.org/'],
}

for identifier, level in {
    "mathscinet": "live_mcp_search_export_fetch_extract",
    "wos": "live_mcp_search_full_record_export_extract",
    "eccc": "live_mcp_search_revision_fetch",
    "crossref": "live_mcp_search_extract",
    "arxiv": "live_mcp_search_extract",
    "zbmath": "live_mcp_search_extract",
    "github": "live_adapter_pinned_file_fetch",
    "numdam": "live_adapter_jats_pdf_fetch",
    "software-heritage": "live_adapter_origin_search_fetch",
    "openalex": "public_endpoint_search_observed",
    "core": "public_endpoint_success_and_rate_limit_observed",
    "semantic-scholar": "rate_limit_observed",
    "dblp": "access_challenge_observed",
    "zenodo": "live_mcp_search_file_checksum_fetch_extract",
    "acm-dl": "live_mcp_search_export_original_pdf_fetch",
    "scopus": "live_mcp_pagination_extract_metadata_abstract_fetch",
    "drops": "live_mcp_search_metadata_abstract_pdf_fetch",
    "springer": "live_mcp_advanced_search_native_citations_pdf_fetch_pagination",
    "ieee-xplore": "live_mcp_search_bibtex_extract_metadata_abstract_pdf_fetch",
    "crossmark": "live_mcp_search_extract",
    "afp": "live_mcp_entry_search_pinned_metadata_and_proof_source_fetch_extract",
    "unpaywall": "public_endpoint_contact_requirement_observed",
    "theory-of-computing": "live_mcp_indexes_citation_pdf_source_ps_references_fetch_and_text_pagination",
    "pqdt": "live_mcp_repeat_search_pagination_ris_pdf_fetch",
    "eudml": "live_mcp_cql_rss_extract_nlm_fetch",
    "aps": "live_mcp_open_access_feed_metadata_abstract_pdf_fetch",
    "aps-institutional": "live_adapter_metadata_and_fulltext_restriction",
    "project-euclid": "live_adapter_metadata_abstract_pdf_fetch",
    "cambridge": "live_mcp_filtered_search_native_ris_abstract_pdf_fetch_pagination",
    "oxford": "live_mcp_search_citation_metadata_abstract_fetch_and_mixed_pagination",
    "aip": "live_mcp_advanced_search_native_citation_abstract_fetch_pagination",
    "wiley": "live_mcp_advanced_search_native_bibtex_pdf_fetch_empty_repeat",
    "taylor-francis": "live_mcp_native_search_citation_abstract_pdf_fetch_pagination",
    "de-gruyter": "live_mcp_native_search_ris_abstract_pdf_fetch_pagination",
    "jstor": "live_mcp_public_ris_metadata_abstract_fetch; web_captcha_observed",
    "iop": "institution_redirect_to_captcha_observed",
    "siam": "browser_access_challenge_observed",
    "ams": "browse_shell_and_script_restriction_observed",
    "science-direct": "native_advanced_form_and_search_cpe_observed",
}.items():
    SOURCES[identifier].verification = level


def source_info(identifier):
    try:
        return SOURCES[identifier]
    except KeyError:
        raise ServiceError("unknown_source", "Unknown source; use list_sources") from None
