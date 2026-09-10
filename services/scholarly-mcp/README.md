학술자료 검색·확보용 로컬 stdio MCP 서버다. 공통 도구와 자료원 어댑터를 구현·검증 중이며, 전체 자료원에 대한 구현 완료를 선언한 상태는 아니다. 확정 요구사항은 [구현 인계](../../학술자료-MCP-구현-인계.md)를 따른다.

2026-09-09 사용자 교정에 따라 **공개 API는 별도 API 이용 자격 없이 호출할 수 있는 API**를 뜻한다. 별도 키·승인·계약을 요구하는 API는 구현 경로에서 제외한다. 그런 공개 API가 없는 인증 자료원은 KUDOS 로그인 → 검색 → 학술DB → 해당 바로가기 → 기관 프록시의 Playwright 경로를 사용한다. 어댑터 경로는 개발 시 정하며, 실행 중 API 오류를 이유로 브라우저로 전환하지 않는다. 기관 로그인 정보는 보호된 `.credentials/kudos.md`에서 서버가 직접 읽는다.

서버의 도구는 다음 다섯 개다. 자료의 연구상 가치와 다른 자료원의 추가 탐색 여부는 호출 AI가 결정한다.

| 도구 | 용도 |
|---|---|
| `list_sources` | 선정 자료원과 구현 상태를 조회한다. `pending`은 개발이 남았다는 뜻이다. |
| `describe_source` | 실제 입력 문법·필드·옵션·export·확보 범위·예제를 읽는다. |
| `search` | 지정 자료원에서 호출자가 작성한 검색식과 조건으로 검색한다. |
| `fetch` | 지정 자료원에서 자료의 정확한 식별자·링크·대상을 회수한다. 지원하는 대상 표기는 자료원 설명에 있다. |
| `extract` | 보존 자료에서 레코드·필드·줄·쪽·파일을 기계적으로 추출한다. |

일반적인 호출 순서는 다음과 같다.

1. `list_sources()`에서 사용할 자료원의 구현 상태를 확인한다.
2. `describe_source(source="mathscinet")`를 읽는다.
3. `search(source="mathscinet", query='ti:("P versus NP")', limit=5, export="bibtex")`를 호출한다.
4. 반환된 `records.ref`에 `extract(ref=…, fields=["mrnumber", "titles"], count=5)`를 호출해 대상을 선택한다. `export.ref`도 `extract`로 읽을 수 있다.
5. `fetch(source="mathscinet", target="MR2733384", parts=["metadata", "supplementary"])`로 서지와 리뷰 PDF를 받는다. MathSciNet의 리뷰 PDF는 논문 전문으로 표시하지 않는다. 논문 전문은 그 출판사를 별도 `source`로 지정한다.

`start`는 0부터 센다. `limit`는 검색에서 요청할 레코드 수이고, `count`는 추출할 레코드·줄·쪽·파일 수다. 자료원 고유의 페이지 제한은 `describe_source`가 정한다. `received`는 해당 결과에 보존한 레코드 수다. `total=null`은 자료원이 전체 검색 건수를 제공하지 않은 경우이며 0건을 뜻하지 않는다. 큰 결과는 파일로 보존하고 모델에는 참조·건수·작은 미리보기를 보낸다. 원자료 전체를 다시 받을 때는 같은 `scholarly://artifact/…` URI에 MCP `resources/read`를 호출한다.

자료 참조는 manifest와 파일의 SHA-256으로 검사한다. 같은 바이트를 서로 다른 자료원에서 얻어도 출처 manifest는 분리된다. 저장된 자료는 서버 재시작 뒤에도 회수할 수 있다. API JSON의 표현 정규화와 인증 정보 정제, 화면 HTML의 실행 코드 제거는 보존 사본에 적용된다. API XML은 네임스페이스를 유지하며 읽고 정제한 뒤 UTF-8로 직렬화하고 `xml_normalized`를 표시한다. 외부 XML 엔터티를 읽거나 확장하지 않는다. PDF·이미지·압축 파일과 저장소 원 파일은 원 바이트로 보존한다.

추출에서 JSON `selection`은 JSON Pointer다. 예를 들어 `/0/fields/cr`은 첫 Web of Science 레코드의 인용문헌 필드다. HTML은 CSS 선택자, XML은 ElementTree가 지원하는 XPath 부분집합을 사용한다. PDF는 원 텍스트 레이어를 추출하고, `render=true`이면 해당 쪽의 이미지도 보존한다. 이미지 ref를 다시 `extract`에 주면 MCP 이미지 내용으로 전달한다. 이미지 의미 판독과 OCR 교정은 서버가 수행하지 않는다. ZIP·tar 계열은 파일 목록을 반환하며 `selection`에 목록의 정확한 파일 이름을 주면 해당 바이트를 별도 자료로 보존한다. 압축 파일의 경로를 작업 디렉터리에 풀지 않는다. 원 저장소 파일과 압축 파일에서 꺼낸 파일은 원 바이트를 유지한다.

| 상태 | 의미 |
|---|---|
| `ok` | 요청한 해당 작업이 성공했다. 전체 프로젝트 완료나 내용의 학술적 타당성을 뜻하지 않는다. |
| `partial` | 요청 내용 중 일부를 회수했다. `components`의 각 상태를 확인한다. |
| `not_found` | 지정 자료원·대상·검색 창에서 결과가 없었다. 다른 자료원의 부재로 확장하지 않는다. |
| `restricted` | 인증·접근 제어·접근 확인 화면 때문에 해당 경로를 사용할 수 없었다. |
| `error` | 실행·통신·파싱·범위 대조 등이 실패했다. `code`와 재시도 안내를 확인한다. |
| `not_implemented` | 해당 기능의 개발이 남았다. 자료원 자체의 기능 부재와 다르다. |
| `unsupported` | 명시한 인터페이스나 공개 접근 범위에서 제공하지 않는 기능이다. 상세 이유를 함께 읽는다. |
| `selection_required` | 대상이 모호하다. 보존한 후보를 읽고 정확한 식별자로 다시 요청한다. |

설치는 저장소 루트에서 다음과 같이 한다. 현재 호스트에는 전용 환경을 설치했고 `.mcp.json`과 `.codex/config.toml`의 `scholarly` 항목에 등록했다. 기존 `dag-measure` 등록은 보존했다. 새 MCP 세션이 이 설정을 읽는다.

```powershell
python -m venv services/scholarly-mcp/.venv
& services/scholarly-mcp/.venv/Scripts/python.exe -m pip install -r services/scholarly-mcp/requirements.txt
& services/scholarly-mcp/.venv/Scripts/python.exe -m playwright install firefox
& services/scholarly-mcp/.venv/Scripts/python.exe services/scholarly-mcp/server.py
```

Chromium 어댑터는 호스트에 설치된 Chrome을 사용한다. 자료원별로 검증한 브라우저를 서버가 선택하며 호출 AI가 지정하지 않는다. stdio의 stdout은 MCP 메시지 전용이고 진단은 stderr로 보낸다.

오프라인 계약 검사는 `python -m unittest discover -s services/scholarly-mcp/tests -p 'test_*.py'`를 전용 Python으로 실행한다. `test_mcp.py`는 실제 SDK 클라이언트와 별도 서버 프로세스로 stdio·도구 조회·파일 추출·자료 읽기를 확인한다. 실서비스 흐름은 `tests/live_workflow.py --source <자료원>`으로 실행하며 지원하는 검증 시나리오는 그 파일에 있다. 오프라인 응답 대역의 통과는 실서비스 통과로 세지 않는다.

현재 실서비스 근거는 로컬 `data/validation/`과 [검증 기록](VALIDATION.md)에 있다. MathSciNet·Web of Science·ECCC·ACM·Scopus·IEEE·PQDT·DROPS·AFP의 구현 범위에 대해 실제 MCP 흐름을 수행했다. Crossref·Crossmark·arXiv·zbMATH는 MCP 검색·추출을 수행했다. GitHub의 고정 커밋 파일, Numdam의 JATS·PDF, Software Heritage의 origin 조회·cursor 순회, Springer의 서지·초록·PDF는 어댑터 직접 호출로 확인했다. 각 기록은 해당 시점·입력·호스트의 관측이며 모든 옵션의 검증으로 확대하지 않는다.

Scopus의 native 내보내기는 별도 웹 계정을 요구하므로 사용자 지시에 따라 보류한다. 검색 결과와 원 JSON·기계적 CSV는 사용할 수 있고, native RIS·BibTeX 요청에는 `export_deferred`와 보존 결과를 함께 반환한다. PQDT는 docview 번호와 학위논문 publication number를 구별하며 실제 RIS의 AN 필드로 대조한다. IEEE는 Command Search와 초록을 포함한 native 인용문 내보내기를 사용한다.

AFP는 공식 Heptapod의 별도 인증 없는 API를 사용한다. 기본 대상은 개발 저장소 `afp-devel`이며, 조회한 Mercurial 커밋을 파일 요청에 고정한다. 항목 검색 결과의 `target`을 fetch에 전달하면 같은 커밋의 항목 메타데이터와 증명 소스를 회수한다. `fulltext`는 이 자료원에서 Isabelle 소스 묶음을 뜻하며, 증명 실행이나 수학적 타당성 판정은 수행하지 않는다.

응답의 `components`에는 부분별 상태가 들어간다. `available`은 해당 자료를 확보했다는 뜻이고, `source_page`는 원 페이지를 보존했으나 요청 내용을 개별 자료로 분리·확보하지 못한 상태다. `not_offered`는 명시된 endpoint가 그 내용을 제공하지 않는 경우다. 이를 자료원 전체의 기능 부재나 구현 완료로 해석하지 않는다.

ACM 인용문 생성은 실제 검색 UI가 수신한 원 서지·CSL 스타일·locale과 자료원이 제공한 citeproc 처리기를 사용한다. 처리기는 외부 통신을 막은 별도 렌더 페이지에서 실행한다. 사이트의 인용문 미리보기 초기화 오류가 자료 확보를 막지 않으며, 서버에 문헌을 해석하는 AI를 넣지 않는다. 서지 응답·처리기·생성 파일의 참조를 함께 보존한다.

`.venv/`와 `data/`는 Git에서 제외한다. 재현에 쓰는 작은 공개 응답은 `tests/fixtures/`에 보존한다. 실행 자료를 다른 환경으로 옮길 때는 `data/` 전체와 해시 검사를 함께 보존한다. 인증 상태는 `.credentials/scholarly-mcp/`에 따로 두며 자료·로그·커밋에 포함하지 않는다. 전체 선정 범위와 아직 조사·개발 중인 자료원은 [지원표](SUPPORT.md), `registry.py`, `list_sources`에 남아 있다.

Theory of Computing은 공식 저자·주제 색인과 저널이 지정한 검색 엔진을 사용한다. PDF·초록 텍스트·BibTeX 외에 제공되는 PostScript·LaTeX 소스 ZIP·HTML 참고문헌·저자 안내를 회수한다. 본문 검색은 웹페이지 단위이며 같은 문헌의 여러 페이지가 결과에 포함될 수 있다. 압축에서 꺼낸 `.bib`·`.ris`도 서지 형식으로 추출하며, BibTeX·RIS·WOS·CSV의 `selection="raw"`는 원 줄을 읽는다.

EuDML은 CQL/OpenSearch와 NLM 메타데이터 API를 사용한다. 참고문헌의 ID를 현재 문헌의 ID로 쓰지 않으며, 외부 원문 링크를 자동 방문하지 않는다. Zenodo는 레코드나 특정 파일 URL로 파일을 받아 제공된 크기·checksum과 대조한다. 파일 URL을 지정하면 해당 파일을 선택하고, 레코드에 fulltext·supplementary를 요청하면 그 레코드의 파일들을 회수한다.

AIP의 Figshare 보충자료는 AIP 호출의 `source`·`target` 참조를 읽고 `figshare`를 명시적으로 선택한다. Figshare 공개 API의 검색·현재 컬렉션 구성원·버전별 문헌 파일을 연결했으며 별도 계정이나 토큰을 사용하지 않는다. 다운로드한 파일은 제공된 크기와 MD5를 대조한다. 과거 컬렉션 구성원 조회는 현재 목록으로 대체하지 않으며 외부 저장소 링크도 자동 방문하지 않는다. 공개 repository description은 저자 초록으로 단정하지 않는다.

`aps`는 별도 자격 없는 공개 Harvest API의 OA 자료 범위다. `aps-institutional`은 KUDOS를 거치는 기관 구독 접근으로 별도 등록했다. 호출자가 자료원을 선택하며 한 호출 안에서 접근 경로를 바꾸지 않는다. APS 기관 경로의 추가 검색 기능은 개발 중이다.

연락 이메일을 요구하는 Unpaywall은 사용자 지시에 따라 사용을 보류한다. `describe_source`에는 보류 상태를 표시하며, 검색·확보 호출은 네트워크 요청 없이 `source_deferred`를 반환한다. 별도 웹 계정이나 연락 이메일은 요청하지 않는다.

Springer는 제목·저자·저널·날짜의 고급검색, 검색 결과 페이지 조회와 문헌별 BibTeX·RIS·EndNote 인용문을 제공한다. `export=csv`는 검색 레코드의 기계적 CSV다. 사이트의 일괄 CSV 다운로드가 이동하는 로그인 경로는 사용하지 않는다. Wiley는 원 고급검색 필드와 날짜·발행물 조건, 선택 문헌의 native citation 다운로드를 제공한다. 인용문 파일은 `export.artifact` 또는 `export.artifacts`에 있으며 해당 자료원 설명의 예제를 따른다.

Oxford와 AIP는 원 검색 필드와 문헌별 인용문을 연결했다. Oxford 결과에는 저널·그림도 있으므로 `type`을 확인한다. 검색 HTML의 건수와 실제 행을 대조하지 못하면 근거 참조와 파싱 실패를 반환한다. AIP 초록은 현재 문헌의 native BibTeX `abstract` 필드로 확보하며 인용문 요청과 같은 파일을 재사용한다.

Cambridge의 Supplementary materials 표와 Oxford의 Supplementary data 위젯은 개별 파일 회수를 지원한다. 같은 제목을 가진 파일도 각각 보존한다. 보충 PDF·ZIP은 `components.supplementary.files`의 artifact로 읽고, ZIP 구성 항목을 선택하면 내부 소스 파일도 줄 단위로 읽을 수 있다. 연구 코드를 실행하거나 직렬화된 실행 환경을 불러오지 않는다.

IEEE의 `supplementary`에는 참고문헌과 그래픽 초록의 미디어 파일·표지가 각각 들어간다. MP4는 서버의 byte range 응답을 파일 버전·위치·길이와 대조해 조립한다. 일부 자료 회수가 실패해도 먼저 받은 자료는 남긴다. 이미지 참조는 extract로 읽을 수 있으며 동영상 자체는 원 파일로 보존한다. 별도 Media 탭의 다른 첨부는 아직 개발 중이다.

PQDT의 `supplementary`는 현재 문헌의 Supplemental files 탭에서 파일 목록과 원 다운로드 제어를 읽는다. 원 건수와 파일명을 대조하고 파일별 artifact를 반환한다. 해당 탭이 표시되지 않은 문헌은 원 페이지를 보존하며 파일이 없다고 단정하지 않는다. 인증된 다운로드 URL은 내부 처리에만 사용한다.

Taylor & Francis는 원 보충 파일과 본문 표의 native CSV를 함께 회수하되 각각 `supplementary_file`·`article_table` 역할로 구별한다. 표의 id와 원 CSV 헤더를 유지한다. 문헌 DOI는 citation 메타데이터 외에 Dublin Core·publication_doi에서도 읽으며, 사용자가 입력한 DOI와 페이지에서 관측한 DOI를 별도로 표시한다.

De Gruyter Brill도 원 Supplementary Material 목록의 개별 파일 회수를 지원한다. 문헌에 제어가 있어도 파일이 404이면 파일별 실패와 나머지 확보 자료를 함께 반환한다. ZIP 내부의 텍스트 파일은 기존 줄 추출로 읽는다.

ACM은 문헌 보충자료 목록의 파일명·설명·DOI를 보존하고 ZIP 등의 원 파일을 회수한다. 참고문헌이 포함된 원 페이지도 유지한다. 페이지에 문법이 잘못된 URL이 있으면 그 URL은 표시용 표지로 바꾸고 나머지 문헌의 보존을 계속한다.

CORE의 `fullText`에 공개 API 접근 제한 안내문이 들어 있으면 `restricted`로 반환한다. 실제 색인 본문은 별도 텍스트 artifact로 제공하며 원 메타데이터도 보존한다. 이름은 검색 후보로 반환하고 CORE works 번호를 선택한 뒤에는 응답의 ID를 대조한다.

OpenAlex는 임의 검색 창과 원 그룹 집계의 커서 페이지를 지원한다. 그룹의 문헌 수와 이번 페이지 그룹 수를 구별하며 전체 그룹 수는 추정하지 않는다. 위치 색인의 단어 순서로 초록 텍스트를 복원하고, 원 색인과 참고·관련 문헌 ID 배열도 보존한다. 이 초록은 OpenAlex의 색인상 초록이며 출판사 원문과의 대조는 별도다.

Semantic Scholar는 문헌 검색과 참고·피인용 관계 검색을 `options.kind`로 구별한다. `openAccessPdf=false`는 공개 PDF 필터를 해제한다. 이름·문헌 링크를 받아 후보 또는 대조한 문헌을 반환하며, 기본 서지 조회에 전체 인용 배열을 붙이지 않는다. 원 BibTeX와 관계 페이지는 연결했으나 신규 실서비스 흐름은 호출 제한으로 아직 검증하지 못했다.

Cambridge는 저자·연도·자료 유형·기관 이용 가능 여부의 검색 조건과 공개 RIS API를 사용한다. 주제·저널·출판사·학회 필터 ID는 검색 결과의 `facets.ref`를 `extract`로 읽어 선택한다. RIS의 `UR`에 있는 문헌 ID를 요청한 ID와 대조한다. 온라인 발행일과 인쇄 발행일을 원 검색 기록에 함께 보존한다.

Taylor & Francis는 원 고급검색 필드와 연도·정렬, native BibTeX·RIS와 문헌 PDF를 연결했다. De Gruyter Brill은 title·familyName 등의 원 검색식, 가시성·정렬과 문헌 RIS를 연결했다. 자료원별 형식·조회 범위는 `describe_source`를 따른다.

JSTOR는 별도 자격 없는 RIS 조회로 metadata·abstract·export를 제공한다. stable 번호나 URL, 10.2307 DOI를 사용한다. 웹 검색과 전문 회수는 아직 연결하지 않았다. `source_preamble`은 RIS 앞의 원 제공자 안내문이며, 인용문 레코드와 구별한다.

Numdam은 공개 웹의 검색 필드·추가 조건·발행연도 검색과 OAI 갱신일 열거를 구별해 제공한다. DOI 페이지의 내부 식별자를 OAI 메타데이터와 연결하고 원 BibTeX·RIS·EndNote, PDF와 DJVU를 회수한다. EndNote의 `fields`는 원 태그 대소문자와 반복 필드를 유지하며 `selection="raw"`로 원 줄도 읽을 수 있다.


DROPS는 문헌별 원 XML·BibTeX 등 내보내기, PDF·HTML 전문과 소프트웨어 artifact의 CodeMeta를 지원한다. 직접 파일 URL은 문헌의 Files 목록과 대조한다. 부가자료의 외부 저장소 링크는 설명과 함께 반환하며 다른 자료원으로 자동 이동하지 않는다.

OpenCitations는 인용 관계·건수와 OCI 단건 조회를 제공한다. CSV 검색의 export는 요청 창, native_export는 전체 원 CSV다. Mathlib·Mathematical Components의 검색 결과는 정확한 커밋·파일·줄 좌표를 포함하며, 이를 같은 판본의 fetch·extract에 사용할 수 있다.


Crossref의 검색 export는 원 BibTeX·RIS·CSL JSON·plain·RDF·Turtle·UNIXREF·UNIXSD를 지원한다. 원 등록 JSON도 유지한다. WOS는 제목 후보와 full-record URL을 받아 accession을 선택·조회할 수 있다. arXiv의 html/src URL은 지정 형식과 판본을 유지하며 source archive의 TeX 파일도 extract로 읽는다.

KNU FRIC는 경북대 센터의 공개 소장 목록 검색·ISSN 조회와 CSV를 제공한다. 직원에게 원문 복사를 신청하는 제출 동작은 포함하지 않는다. author-repository·society-journal은 알려진 공개 문서 URL의 회수 경로이며 단일 검색 색인은 아니다. general-web은 Mwmbl의 별도 자격 없는 공개 검색 API를 사용하며, 반환된 후보 묶음 크기와 웹 전체 일치 건수를 구별한다.


ScienceDirect는 KUDOS 기관 context의 원 citation endpoint로 서지·초록·RIS·BibTeX·plain을 회수한다. 문헌 화면·검색·PDF 준비 경로의 실패와 인용문 성공을 구별한다. AIP는 실제 PDF 전송 호스트를 파일 다운로드에 한해 허용한다. IOP의 서지·PDF 양성 관측과 이후 기관 접근 확인 때문에 미검증인 추가 내보내기는 지원표에 구분한다.

Scopus의 supplementary는 현재 문헌 References·Cited by 탭의 목록이다. references와 citations 각각의 artifact를 extract로 읽는다. 검색 요약의 건수와 문헌 탭의 건수가 다르면 둘을 별도 필드로 보존한다. 색인 EID가 없는 참고문헌도 유지하며 원 RIS·BibTeX의 별도 계정 요구는 계속 보류한다.

Excel 내보내기는 XLS와 XLSX를 구별해 보존하고 추출한다. extract의 selection은 시트명, fields는 A·B·AA 같은 열 문자다. start는 0부터이며 반환 row는 원 시트의 1부터 시작하는 행 번호다. 여러 시트가 있으면 먼저 selection_required와 시트 목록을 반환한다. XLSX 수식은 실행하지 않고 원 문자열로 반환한다. XLS는 저장된 값과 표시 형식을 읽으며 수식 정의·링크·삽입 개체는 원 파일에 남아 있다. WOS의 실제 Excel 표본은 XLS였으며 I·BE·BS 열에서 제목·DOI·accession을 확인했다.

Project Euclid는 원 고급검색의 필드·AND/OR/NOT 추가 조건·발행연도·발행물 선택과 정렬·페이지 크기를 제공한다. 발행물 이름은 검색 결과 facets.ref에서 선택한다. 현재 페이지와 다음 페이지의 미리 받기를 구별하며 원 50쪽 제한을 표시한다. 문헌별 RIS·BibTeX·EndNote와 인용문 PDF를 내보낸다. 인용문 PDF에는 서지·초록이 있으며 논문 전문은 fetch의 fulltext로 받는다. EndNote의 원 %DOI 태그는 fields.DOI로 유지한다.

AMS는 기관 고급검색의 원 상품 JSON을 연결했다. 책·논문·학회 초록의 ContentType과 제목·부제·DOI·제품 코드를 유지한다. 원 브라우저 검색의 양성 관측과 이후 어댑터의 접근 확인 실패는 지원표에서 구별한다. 원 파일 export는 추가 검증이 남아 있다.

Publisher 어댑터에 .pdf 링크를 직접 주면 그 파일의 바이트와 PDF 내장 메타데이터를 회수한다. 브라우저의 Download is starting 이동 예외와 실제 파일 회수 성공을 구별한다. metadata.kind가 embedded_pdf_metadata이면 PDF 내부 정보다. 파일이 발췌·부속 자료인 경우 전체 책을 확보했다는 뜻으로 해석하지 않는다. 이 경로의 실제 MCP 검증은 AMS gsm128-endmatter.pdf 51쪽으로 수행했다.

SIAM의 /doi/pdf/DOI 주소도 명시적 PDF 파일로 처리한다. First-Order Methods in Optimization의 Front Matter 10쪽은 실제 MCP에서 회수·추출했다. 검색과 native 인용문 연결은 남아 있다. IEEE supplementary.references에는 문헌 번호를 대조한 원 참고문헌 배열이 있으며 extract로 order·title·text·links 등을 읽는다. IEEE 개별 첨부 회수는 남아 있으므로 supplementary 전체는 partial로 표시한다.

Springer Nature의 인식된 Supplementary Information·Peer Review File 제어는 실제 파일을 회수한다. supplementary.index는 원 파일 목록이고 files의 각 artifact를 extract로 읽는다. 파일별 실패와 이미 회수한 파일을 함께 반환한다. Nature Communications의 The complexity of NISQ에서 보충 설명 42쪽과 심사 기록 19쪽을 실제 MCP로 확인했다. 다른 레이아웃에서 제어를 찾지 못하면 원 페이지와 source_page 상태를 유지한다.

zbMATH는 DOI·이름·Zbl 번호·기존 문헌 링크를 받아 조회하고, 검색의 임의 start 위치를 원 페이지에서 조합한다. 리뷰·요약은 원 editorial_contributions 유형을 유지한다. 라이선스 충돌 안내는 abstract available로 표시하지 않는다. supplementary의 selection을 extract에 전달하면 원 참고문헌 배열을 읽을 수 있다.

Wiley의 Supporting Information 표에서도 원 파일을 회수한다. Models of Random Spanning Trees의 보충 ZIP을 실제 MCP로 받고, 내부 Python 파일 두 개를 선택해 줄 단위로 읽었다. 코드 실행은 포함하지 않는다. 파일명·설명·연결 DOI와 실제 ZIP 형식을 확인하며, Springer Nature와 파일별 실패 보존 처리를 공유한다.
