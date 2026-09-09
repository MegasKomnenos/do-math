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

    def summary(self):
        return {"id": self.id, "name": self.name, "role": self.role, "transport": self.transport,
            "implementation": self.implementation, "verification": self.verification,
            "capabilities": ["source_guide", "search", "fetch", "export"] if self.implementation == "partial" else []}


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
        "fetch": "Zenodo record 번호, records/번호 URL 또는 10.5281/zenodo.번호 DOI. 현재 레코드와 파일 목록까지 구현했으며 파일별 선택 다운로드는 개발 중이다.",
        "limits": "limit 1..100. start는 limit의 배수. json/native export. 특정 파일의 판본은 record ID로 고정하며 concept DOI는 단일 파일 판본을 뜻하지 않는다.",
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
    "zenodo": "timeout_observed",
    "acm-dl": "live_mcp_search_export_original_pdf_fetch",
    "scopus": "institutional_browser_landing_observed",
    "ieee-xplore": "institutional_browser_landing_observed",
    "pqdt": "institutional_browser_landing_observed",
}.items():
    SOURCES[identifier].verification = level


def source_info(identifier):
    try:
        return SOURCES[identifier]
    except KeyError:
        raise ServiceError("unknown_source", "Unknown source; use list_sources") from None
