부분 완료 상태의 중간 검증 기록이다. 2026-09-09~10 KST의 Windows 호스트에서 공통 서버와 아래 호출 경로를 확인했다. 보고 파일 이름의 시각은 UTC다. 선정 자료원 전체의 구현 완료 기록은 아니다.

공통·자료원 검사 76개가 통과했다. 공개 응답 fixture와 오류 경로의 대역 검사, 실제 SDK 클라이언트와 서버 프로세스의 stdio 검사를 포함한다. 테스트 명령은 README에 있으며, 구현의 새 변경에는 관련 검사를 다시 적용한다.

| 자료원 | 실제로 수행한 범위 | 로컬 근거 |
|---|---|---|
| MathSciNet | KUDOS 로그인·학술DB 프록시, 제목 검색, 5건 BibTeX, 필드 추출, MR2733384 서지·리뷰 PDF, PDF MR 번호 대조 | `data/validation/mathscinet-workflow.json` |
| Web of Science | KUDOS CPCI 바로가기, Core Collection 고급검색, 5건 Full Record and Cited References, 첫 문헌의 참고문헌 47개 보존 | `data/validation/wos-workflow.json` |
| ECCC | 실제 검색 UI, 검색 결과 추출, TR26-008 revision 1의 초록·PDF 확보 | `data/validation/eccc-workflow.json` |
| ACM | 새 stdio 서버·Firefox 세션, 제목 검색, 1971/2023 판본 분리, 실제 UI 서지 응답의 CSL export, 1971년 원 논문 8쪽 PDF | `data/validation/20260909T061851319824Z-acm-dl-workflow.json` |
| Crossref·arXiv·zbMATH | 실제 MCP 검색·보존·레코드 추출 | `data/validation/crossref-workflow.json`, `arxiv-workflow.json`, `zbmath-workflow.json` |
| GitHub | v4.22.0을 commit `79e94a093aff4a60fb1b1f92d9681e407124c2ca`로 고정한 뒤 Mathlib의 lean-toolchain 파일 회수 | `data/validation/github-fetch.json` |
| Numdam | AIF_1956__6__1_0의 공개 JATS 메타데이터와 4,134,102바이트 PDF 회수 | `data/validation/numdam-fetch.json` |
| Software Heritage | origin 검색·조회 및 서로 다른 두 페이지의 실제 cursor 순회 | `data/validation/software-heritage-search.json`, `software-heritage-fetch.json`, `software-heritage-pagination.json` |
| DROPS | 실제 MCP 검색, Schema.org 서지·초록, CSL 2020 문헌의 2쪽 PDF | `data/validation/20260909T065015654334Z-drops-workflow.json` |
| Scopus | 실제 MCP 제목 고급검색, 1·2페이지 경계의 2건 회수·CSV·추출, 선택 EID 서지·초록 | `data/validation/20260909T075610151008Z-scopus-workflow.json` |
| PQDT | 실제 MCP 제목 검색, RIS의 AN과 docview 번호 대조, 초록·40쪽 PDF; 첫 쪽의 제목·저자를 별도로 대조 | `data/validation/20260909T082208134145Z-pqdt-workflow.json` |
| IEEE | 실제 MCP Command Search, 초록 포함 native BibTeX, DOI 추출 대조, 문헌 10488889의 서지·초록·PDF | `data/validation/20260909T082509108744Z-ieee-xplore-workflow.json` |
| Crossmark | Crossref 공개 API를 통한 실제 MCP 검색·추출; 갱신 필드별 해석 전수 검증은 수행하지 않음 | `data/validation/20260909T080306742349Z-crossmark-workflow.json` |
| AFP | 실제 MCP의 Cook–Levin 항목 검색, 같은 Mercurial 커밋의 서지·초록·증명 소스 archive, 22개 내부 항목 목록 추출 | `data/validation/20260909T083738397452Z-afp-workflow.json` |
| Springer | 문헌 DOI로 KUDOS 기관 경로의 서지·초록·PDF 직접 어댑터 호출 | `data/validation/20260909-publisher-springer.json` |
| PQDT 연속 호출 | 기존 문헌의 RIS·PDF 뒤 다른 검색을 수행하고 7,575건 결과의 다음 페이지에서 한 문헌을 선택·export | `data/validation/20260909T095059741823Z-pqdt-workflow.json` |
| Theory of Computing | 주제 색인·BibTeX, gs010의 초록·166쪽 PDF·소스 ZIP·PS·참고문헌 HTML, 본문 검색의 다음 페이지 | `data/validation/20260909T094041248208Z-theory-of-computing-workflow.json` |
| EuDML | CQL 검색의 offset 1·2건·전체 8건 대조, RSS 항목 추출, 문헌 196516의 NLM ID 대조 | `data/validation/20260909T111337280394Z-eudml-workflow.json` |
| Zenodo | 실제 MCP 검색·레코드 822080의 파일 회수·제공 checksum 대조·PDF 추출 | `data/validation/20260909T111615002171Z-zenodo-workflow.json` |
| APS 공개 접근 | OA 피드 날짜 조건·2건, 공개 문헌의 서지·초록·PDF, 첫 쪽 제목 대조 | `data/validation/20260909T113649749504Z-aps-workflow.json` |
| arXiv·Numdam 재검증 | 공통 HTTP/XML 처리 변경 뒤 MCP 검색·추출 또는 NLM·PDF 회수·추출 | `data/validation/20260909T114546540681Z-arxiv-workflow.json`, `20260909T114546540681Z-numdam-workflow.json` |

각 실서비스 기록은 해당 입력·시점의 관측이다. 이후 공통 코드 변경의 회귀 검사와 자료원별 실서비스 검사를 구별한다. 위 기록을 각 자료원의 모든 검색 옵션·문헌·형식에 대한 검증으로 확대하지 않는다. Mathlib·Mathematical Components의 소스 문자열 검색, GitHub·Zenodo의 전체 archive, Numdam의 키워드 검색 등 추가 기능은 별도 실서비스 검증이 필요하다.

DBLP는 공개 검색 API와 공식 미러가 HTTP 200의 접근 확인 HTML을 반환했다. Semantic Scholar와 CORE에서는 429를 관측했고, CORE의 별도 자격 없는 성공 응답도 확인했다. Zenodo와 EuDML에는 timeout·504 관측이 있다. 이들을 정상 검색의 성공이나 해당 자료원의 문헌 부재로 세지 않는다. API 실패에 따른 브라우저 전환은 구현하지 않았다.

Scopus의 native Export 제어는 기관 접속에 더해 Scopus 웹 계정 로그인을 요구했다. 사용자 지시에 따라 이 경로는 `export_deferred`로 보류하고 원 검색 JSON과 기계적 CSV를 제공한다. Scopus의 preprint 별도 집계와 primary 문서 집계를 분리한다. 실제 1건 응답에서도 itemCount가 10이었으므로 이를 페이지 수용량으로 처리하고 수신 건수·전체 건수·offset을 대조한다.

PQDT는 지연 표시되는 쿠키 창과 별도 export 창을 처리한다. RIS 응답을 원 검색 탭의 download 이벤트에서만 기다리면 정상 파일을 놓쳤다. 현재는 같은 ProQuest의 RIS 응답과 선택 문서 AN을 대조한다. PDF 화면에서는 해당 docview 번호의 다운로드 제어를 확인한다. 연속 검색과 다음 페이지의 한 문헌 회수는 추가 검증을 통과했고, 다른 범위·형식 검증은 남아 있다.

출판사 초기 시험에서는 Project Euclid의 메타데이터와 PDF, AIP의 메타데이터와 초록, Oxford의 메타데이터를 회수했다. 당시 Oxford PDF는 watermark02.silverchair.com으로 이동해 허용 범위 검사에서 중단됐고, 이후 재검증에서 해당 전송 호스트를 확인해 회수했다. AMS는 pubs.ams.org로 이동했으며 호스트 목록을 보완했다. Cambridge·JSTOR·SIAM에는 대기 실패가, ScienceDirect 프록시에는 CPE 오류가 있었다. 초기 관측의 근거는 `data/validation/20260909-publisher-*.json`이며, 최신 상태는 아래 재검증 기록과 지원표를 따른다.

나머지 출판사·보완 자료원과 구체 서비스가 정해지지 않은 범주의 상태는 `registry.py`에 유지한다. `pending`이나 `not_implemented`는 개발이 남았다는 뜻이며 자료원 자체의 기능 부재를 뜻하지 않는다. Unpaywall은 연락 이메일을 요구하므로 사용자 지시에 따라 보류했다. MCP 호출이 네트워크 요청 없이 `source_deferred`를 반환하고 기능 목록에는 사용 안내만 표시하는 검사를 통과했다.

검사 중 수리한 사례에는 stdio 출력 스키마의 상태 필드, 자료 참조·바이트 무결성, 본문을 감싼 HTML form의 내용 보존, BibTeX 구분자를 보존하는 URL 정제, 공개 commit 서명과 페이지 cursor의 보존, 압축 안의 JSON 원 바이트 보존, Software Heritage의 무시되는 offset, ACM의 초기 미리보기 스크립트 의존이 있다. ACM에서는 선택한 서지 응답은 정상인데 페이지의 `UX.CSL` 초기화가 실패했다. 자료원이 제공한 처리기와 스타일을 외부 통신 없는 렌더 페이지에서 실행하여 같은 선택 문헌을 export하도록 수리했다.

진단 중 ProQuest 상대 링크의 CSRF 값과 PDF 전송 URL의 서명 매개변수 `_a`·`_s`가 각각 도구 출력에 포함되는 사고가 있었다. 사용자에게 즉시 알렸고 값을 재기재하지 않았다. 해당 조사 브라우저는 종료했으며 앞선 도구 출력 자체를 삭제한 것은 아니다. 상대 URL·서명 매개변수·중첩 URL의 정제를 수리하고 회귀 검사를 추가했다. 저장된 KUDOS 세션을 재사용해도 ID/PW가 정제기에 등록되도록 보완했다. 확인한 9개 값은 출력하지 않고 새 서버의 코드·문서·fixture·20MB 이하 로컬 산출에서 원 표현과 URL 디코딩 표현을 검사했으며 일치 파일은 없었다. 이 검사는 모든 비밀 형식이나 PDF 내부의 압축·이미지 표현에 대한 증명이 아니다. 인증 상태와 원 진단 자료는 Git에서 제외된 `.credentials/`에 유지한다.

문헌 화면의 명시적 이동은 이동 전후의 자료원 호스트를 검사하고 외부 자료원의 결과를 거부한다. browser_download의 HTTP 파일 요청은 외부 redirect 대상에 다음 요청을 보내기 전에 중단하며 이 동작을 대역 검사했다. 명시적 PDF의 native 브라우저 download는 요청한 경로·쿼리와 대응시키고 파일을 읽기 전에 다운로드 URL의 자료원 호스트를 대조한다. 이 경우는 브라우저 문헌 이동과 같은 사후 호스트 검사 범위다. HTTP 다운로드의 시간 초과는 원 예외 URL을 노출하지 않는 typed error로 변환한다. 검색 응답도 지정 자료원 호스트와 원 검색식을 대조한다. 이 검사를 모든 브라우저 하위 리소스의 네트워크 격리로 표현하지 않는다.

추가 수리에서는 XML 요청에 JSON Accept 헤더를 보내 EuDML이 HTTP 406을 반환하던 조건을 재현했다. 형식에 맞는 Accept를 보내도록 바꿨다. URL 정제가 XML의 `&amp;`를 깨뜨리던 오류는 네임스페이스를 보존하는 XML 처리로 수리했다. 엔터티 선언·참조의 확장을 거부하며 외부 파일을 읽지 않는 검사도 통과했다. 인증 정보가 없는 URL은 원 표현을 유지하여 공개 서명 payload의 URL이 달라지지 않도록 했다.

Theory of Computing의 옛 HTTP Google loader는 HTTPS 페이지에서 검색 입력을 초기화하지 못했다. 같은 저널이 공개한 엔진 ID를 현재 공개 위젯으로 렌더링해 검색·페이지 이동을 통과시켰다. 별도 Google API 키는 사용하지 않았다. 소스 ZIP의 `.bib`가 Windows MIME 추정에서 text/plain이 되던 문제와 엔트리 밖 `#OK` 주석 때문에 파서가 멈추던 문제도 수리했으며, 해당 gs010.bib의 84개 서지 레코드를 추출했다.

출판사 재검증에서는 Oxford의 실제 PDF 전송 호스트를 파일 다운로드에 한해 허용해 PDF를 확보했고, Project Euclid의 초록 영역을 확인해 서지·초록·PDF를 확보했다. Cambridge의 현재 표본은 문헌 메타데이터와 접근 안내를 반환했고, AIP는 서지·초록을 반환했다. 이들의 근거는 `data/validation/20260909-publisher-recheck-*.json`이다. APS는 OA 문헌의 API JSON·PDF 성공과 다른 DOI의 HTTP 401을 확인했다. 별도로 시험한 기관 접근에서는 메타데이터를 얻었지만 PDF는 제한됐다(`data/validation/20260909-aps-institutional.json`). 공개 API 경로와 기관 경로를 별도 source로 제공한다.

Springer의 실제 MCP 고급검색·문헌별 BibTeX 추출, DOI `10.1007/s00037-008-0249-x`의 서지·초록·28쪽 PDF·인용문, 19·20번째 위치 경계 조회를 통과했다. 근거는 `data/validation/20260909T144928167948Z-springer-workflow.json`이다. native BibTeX의 DOI가 항목 키에만 있는 형식도 대조한다. 기존 논문 화면의 Download citation과 새 장 화면의 .RIS/.ENW/.BIB는 같은 citation endpoint와 형식 매개변수를 사용했다. 일괄 CSV 제어는 idp 로그인 경로로 이동했다. 현재 `export=csv`는 회수 레코드의 기계적 CSV이며 원 사이트의 일괄 CSV 다운로드로 표시하지 않는다.

Wiley의 실제 MCP 제목 고급검색, 684건 중 19·20번째 위치의 두 문헌과 native BibTeX, `10.1002/rsa.21210`의 서지·초록·18쪽 PDF, PDF 첫 쪽 제목 대조와 이후 0건 검색을 통과했다. 근거는 `data/validation/20260909T145413656979Z-wiley-workflow.json`이다. 내보내기 선택 창의 체크박스는 focus·Space로 조작하고 값의 DOI를 결과와 대조한다. 인용문의 DOI URL 표기와 DOI 자체를 같은 식별자로 대조하되 원 파일 표현은 보존한다.

Wiley의 문헌 PDF 링크는 뷰어 HTML을 반환했다. 실제 뷰어 iframe의 `file` 값이 채워진 시점의 src를 같은 관찰에서 회수하고, 그 파일 링크를 자료원 경계 안에서 다운로드하여 PDF 형식을 검사한다. 초기 빈 `file` 값과 나중의 다운로드 값을 구별한다. 0건 화면에는 양성 결과의 `.result__count`가 없고 `.result__current`와 `.search-result__no-result`가 있어 이 별도 레이아웃을 처리했다. 실패 기록은 `completed=false`로 보존하며 이후 성공 기록과 구별한다.

Oxford는 실제 MCP에서 제목 구문 검색 1건, 문헌별 BibTeX·서지·초록, complexity 제목 검색의 19·20번째 위치를 회수했다. 성공 근거는 `data/validation/20260909T170011179553Z-oxford-workflow.json`이다. 새 서버 재검증 중 범위 대조 실패도 있었으므로 그 실패 기록을 성공으로 바꾸지 않는다. 동일 코드의 별도 범위 조회에서는 75,732건 중 두 위치를 다시 회수했다. 페이지 사이의 전체 건수 또는 시작 위치가 달라지면 대조 실패를 반환한다.

Oxford의 검색에는 저널·그림·책·논문이 함께 나온다. 일부 제목 링크에 article-link 클래스가 없는데 그 클래스를 필수로 삼아 실제 행을 인식하지 못한 결함을 수리했다. 이 결함을 자료원 자체의 결과 부재로 분류하지 않는다. 인식할 수 없는 응답에는 `search_parse_failed`와 원 HTML 근거·이미 회수한 레코드를 반환한다. All 기본 검색과 고급검색의 Full Text 필드는 별도 요청으로 보존한다. 실제 0건 응답, 결과 범위가 맞지 않는 응답과 미인식 레이아웃을 구별한다.

Oxford 인용문 창의 형식을 선택한 뒤에도 다운로드 버튼이 CSS disabled 상태에 남는 사례를 확인했다. 형식 재선택과 안정된 컨트롤 선택에서는 실제 파일이 내려왔다. 현재는 문헌의 실제 citationModal GET form에 있는 resourceId·resourceType과 제공된 citationFormat 값을 사용하고 `/Citation/Download`의 결과 DOI를 대조한다. 폼에서 얻지 않은 문헌 ID나 다른 자료원으로 교체하지 않는다. 일괄 Export title list는 책·저널 목록이며 CAPTCHA를 요구해 사용하지 않는다.

AIP는 실제 MCP에서 quantum computation 제목 검색, 서지·초록·native BibTeX와 페이지 경계의 2건을 회수했다. 최신 성공 근거는 `data/validation/20260909T170612399307Z-aip-workflow.json`이다. 10.1119/5.0328433의 native BibTeX DOI를 대조했으며 abstract 필드의 830자를 확보했다. 초기 문헌 HTML에는 초록 위젯이 아직 없을 수 있어 abstract는 검증된 native citation 필드를 사용한다. 같은 fetch의 export와 파일을 재사용한다. Tools 메뉴의 Cite가 제공하는 실제 BibTex·RIS·EndNote 링크를 사용한다. 이 흐름은 AIP PDF·첨부 영상 확보의 통과 기록이 아니다.

Cambridge는 별도 키·계정·이메일 없이 공개 RIS API에서 두 문헌의 인용문을 함께 회수했고, RIS UR의 product ID와 요청 ID를 대조했다. 실제 MCP에서는 기관 이용 가능 Articles로 제한한 2건, RIS·추출, DOI 10.1017/S1062798713000598의 서지·초록·16쪽 PDF·RIS와 67,908건 결과의 페이지 경계를 통과했다. 최신 근거는 `data/validation/20260909T170612296273Z-cambridge-workflow.json`이다. RIS의 DOI: 접두어, 온라인 날짜와 인쇄 날짜, 서명 역할 A2 등 원 필드를 유지한다.

Cambridge RIS 경로는 [Zotero의 Cambridge Core 번역기](https://github.com/zotero/translators/blob/master/Cambridge%20Core.js)를 조사 출발점으로 삼고 실제 Cambridge 응답으로 검증했다. 해당 코드를 복제해 실행하지 않았다. 현재 구현에서 native RIS를 제공하며, 다른 exportType 탐색의 빈 응답·오류를 다른 형식의 지원 근거로 세지 않는다. 주제·저널·출판사·학회 ID는 원 검색 facet에서 회수하여 `facets.ref`로 제공한다.

Taylor & Francis는 KUDOS 목록을 Taylor로 조회해 기관 프록시에 접속했다. native field1·text1 검색과 0부터 세는 startPage, 20건 페이지를 확인했다. 실제 MCP에서 40,675건 중 페이지 경계 두 문헌의 BibTeX, 10.1080/09557571.2011.558053의 서지·초록·23쪽 PDF·인용문을 통과했다. 근거는 `data/validation/20260909T180900949894Z-taylor-francis-workflow.json`이다. PDF 첫 쪽에서는 제목·저자와 DOI를 별도로 읽었다. 현재 문헌 DOI와 일치하는 Download PDF 제어를 선택하며 View PDF 뷰어나 관련 논문의 PDF로 바꾸지 않는다.

Taylor & Francis의 `/action/downloadCitation`은 기관 context에서 두 DOI를 포함한 POST에 두 BibTeX 레코드를 반환했다. 공개 직접 POST의 HTTP 403과 구별한다. POST 리디렉션은 허용 호스트를 다음 요청 전에 검사하고, 303 등에서는 본문을 재전송하지 않는 GET으로 전환한다. 이 경계는 별도의 오류 경로 검사도 통과했다. KUDOS 진입 실패에는 로그인·학술DB·목록 조회·바로가기·자료원 이동·준비 중 어느 단계였는지를 안전한 이름으로 남긴다.

De Gruyter Brill은 title:(complexity)와 familyName:(Goldreich)의 결합, 검색 가시성, 10건 페이지의 startItem을 확인했다. 실제 MCP에서 available 범위의 654건 중 두 문헌 RIS·추출, 서지·초록·9쪽 PDF·RIS와 9·10번째 위치의 검색을 통과했다. 근거는 `data/validation/20260909T183631515680Z-de-gruyter-workflow.json`이다. Download in RIS format 제어의 원 링크를 회수하고 doi: 접두어를 식별자 대조에 사용한다. all에는 저널 등 DOI가 없는 결과도 포함되며 그 인용문 미확보를 문헌별로 표시한다.

JSTOR의 공개 `/citation/ris/345683`은 별도 자격 없이 원 RIS를 반환했다. 실제 MCP에서 10.2307/345683의 서지·초록·RIS와 추출을 통과했다(`data/validation/20260909T183927702687Z-jstor-workflow.json`). RIS의 TY 앞에 있는 Provider·Database·Content 안내문을 source_preamble로 보존하도록 추출기를 확장했다. 웹 검색과 전문 회수의 통과 기록은 아니다.

추가 접근 관측에서는 JSTOR 검색의 이미지 CAPTCHA, IOP 기관 바로가기의 validate.perfdrive.com CAPTCHA, Project Euclid 검색의 Incapsula 차단, SIAM 검색의 Cloudflare 확인 화면을 기록했다. AMS는 browse 화면 틀을 열었지만 결과 준비를 확인하지 못했고 browse.js의 공개·기관 요청에서 HTTP 403을 관측했다. ScienceDirect는 고급검색 입력까지 열렸으나 검색 제출 뒤 CPE00001을 반환했다. 이 관측을 영구적인 서비스 부재로 해석하지 않으며, 미구현·미검증 기능은 지원표에 남긴다.

이번 진단에서도 보안 규칙 위반이 두 번 발생했다. 압축 HTML의 첫 줄을 직접 출력하면서 Cloudflare 접근 확인 토큰이 포함됐고, Numdam 폼의 숨은 입력값 출력에 CSRF 토큰이 포함됐다. 사용자에게 즉시 알렸으며 값을 재기재하지 않았다. 해당 브라우저는 종료됐지만 기존 도구 출력은 삭제하지 않았고 토큰 폐기를 주장하지 않는다. 원 Numdam HTML은 보호된 probes로 이동했다. URL의 Cloudflare 토큰은 기존 정제 대상이었으며, 이번에는 구조화된 challenge 객체와 csrfmiddlewaretoken의 정제를 추가 검사했다. 이 수리가 원자료 직접 출력의 절차 위반 자체를 자동 방지한다고 주장하지 않는다. 이후 진단에는 원 HTML·숨은 입력값을 직접 출력하지 않는 경계가 필요하다.

전체 구현은 부분 완료다. 나머지 자료원 검색·내보내기, 일부 문헌·첨부 형식 등은 남아 있다. 별도 웹 계정 또는 연락 이메일을 요구하는 기능은 사용자 지시에 따라 보류하고 입력을 요청하지 않는다. 위 성공 기록은 해당 시점·입력의 검증이며 모든 옵션의 검증으로 확대하지 않는다.


2026-09-10 Numdam 확장에서는 실제 웹 폼의 키워드·제목 필드와 추가 발행연도 조건, 20건 페이지를 연결했다. `complexity`의 4,804건 중 19·20번째 위치와 원 RIS 두 건, DOI 10.1051/ita/2011126의 내부 ID ITA_2012__46_1_67_0, JATS·초록·10쪽 PDF·DJVU·BibTeX·RIS·EndNote를 실제 MCP에서 회수했다. PDF 첫 쪽의 제목을 추출해 대조했다. 제목 구문과 2012년 조건의 1건, 무작위 문자열의 0건, 이후 native ID AIF_1956__6__1_0의 43쪽 PDF 조회도 통과했다. 전체 성공 근거는 `data/validation/20260910T001118529519Z-numdam-workflow.json`이다.

앞선 `20260910T000809975203Z-numdam-workflow.json`은 새 기능 검증을 통과한 뒤 기존 native ID의 OAI 요청에서 connection_error를 반환했다. 독립 재호출과 후속 전체 흐름은 성공했으며, 실패 기록은 completed=false로 유지한다. 이 관측만으로 원인을 특정하거나 서비스의 영구 제한이라고 판단하지 않았다.

Numdam이 제공한 실제 EndNote 파일에 extract를 호출하여 format_not_supported를 재현한 뒤 공통 추출기를 확장했다. 원 태그의 대소문자, 반복 저자, 이어지는 줄과 원 레코드 텍스트를 보존한다. 실제 공개 파일은 `tests/fixtures/numdam.enw`, 정제한 검색 응답은 `tests/fixtures/numdam-search.html`이다. 새 회귀 검사를 포함해 공통 검사 81개가 통과했다. 검색 문법은 [Numdam 도움말](https://www.numdam.org/help/), OAI의 역할은 [메타데이터 안내](https://www.numdam.org/metadata/)와 대조했다. OAI 갱신일과 웹 검색의 발행연도를 같은 필터로 취급하지 않는다.

같은 날 ScienceDirect의 공개 citation endpoint는 HTTP 403의 HTML을 반환했고, KUDOS 기관 경로에서 Natural Proofs의 정확한 PII 문헌 조회는 publisher_access_restricted였다. AMS의 DOI 10.1090/jams/1019 기관 문헌 조회도 publisher_access_restricted였다. 이 확인을 검색·전문 구현 완료나 자료 부재의 근거로 사용하지 않는다. 원 HTML·숨은 입력값·인증 URL을 출력하지 않고 허용한 상태·제어 이름·공개 문헌 식별자만 진단에 사용했다.


2026-09-10 DROPS의 추가 검색 내보내기와 원문 형식을 실제 MCP에서 검증했다. P versus NP 44건 중 두 문헌의 native BibTeX와 추출, 10.4230/LIPIcs.CSL.2020.5의 Schema.org·BibTeX·XML·ACM-XML·DOAJ-XML 및 2쪽 PDF를 회수했다. 10.4230/LIPIcs.DNA.31.9의 정확한 HTML 파일 URL은 현재 문헌의 Files 영역과 대조해 HTML만 회수했고 article 선택 추출과 부가자료 설명·링크 보존을 통과했다. 10.4230/artifacts.27685는 소프트웨어 artifact로 해석해 Schema.org·BibTeX·XML·CodeMeta를 받았다. CodeMeta의 identifier는 SWHID이며 DOI로 바꾸지 않는다. 외부 코드 저장소는 방문하지 않았다. 최신 전체 근거는 `data/validation/20260910T003901636855Z-drops-workflow.json`이다.

DROPS의 /metadata/bibtex와 /metadata/codemeta-json은 원 파일의 HTML 미리보기였다. 미리보기에 제공된 /download 링크를 실제로 확인했고, 최종 구현은 이 공개 API로 원 파일을 받는다. XML의 article와 artifact 헤더를 구별하며 참고문헌 DOI를 현재 문헌의 식별자로 취하지 않는다. 공개 XML·BibTeX·CodeMeta 응답은 tests/fixtures에 보존했다.

이 조사에서 바이너리 요청이 받은 HTML을 그대로 보존하던 공통 경계의 결함을 확인했다. 임시 DROPS 응답 3건에 폼 토큰이 저장되어 있었으며 값은 도구 출력에 표시하지 않았다. 세 blob과 manifest를 `.credentials/scholarly-mcp/probes/quarantine-drops-20260910/`으로 이동해 일반 artifact 저장소에서 격리했다. 토큰 폐기를 수행한 것은 아니다. 바이너리·JSON·XML 요청에 HTML이 오면 저장 전에 거부하고, 명시적인 HTML 요청은 활성 요소와 폼 값을 제거한 뒤 보존하도록 수리했다. 합성 토큰을 쓴 실패 재현과 회귀 검사를 통과했다. 이 수리를 모든 과거 산출물의 전수 보안 감사로 확대하지 않는다.

Mathlib는 고정 커밋의 Mathlib/Computability/에서 theorem 문자열 1,014개, Mathematical Components는 algebra/에서 Lemma 문자열 5,284개 중 각 두 소스 줄을 검색했다. 선택한 첫 줄의 파일을 같은 커밋으로 fetch하고 해당 줄의 원문이 정확히 같은지 실제 MCP extract로 대조했다. 이는 소스 회수 검증이며 Lean·Rocq의 형식 검증 실행은 아니다. 근거는 `data/validation/20260910T002906509697Z-mathlib-workflow.json`과 `20260910T002944472828Z-math-comp-workflow.json`이다. Mathematical Components의 첫 0건은 검증 입력의 오래된 mathcomp/ssreflect/ 경로였고 실제 archive의 현재 경로를 확인해 입력을 고쳤다.

OpenCitations에서는 DOI 10.1186/1756-8722-6-59의 참고문헌 72건 원 CSV와 start=1, limit=2 창, 해당 OCI의 단건 조회, reference-count의 72건 대조를 실제 MCP에서 통과했다. 근거는 `data/validation/20260910T003511813034Z-opencitations-workflow.json`이다. 첫 MCP CSV 요청은 Accept: text/csv에도 JSON을 받아 실패했으므로 제공자가 문서화한 format=csv를 명시했고, JSON에도 format=json을 사용한다. 선택 CSV의 원 필드와 순서는 보존하되 파일 재직렬화와 전체 native CSV를 구별한다. 원인으로 캐시를 단정하지 않는다.

새 회귀 검사를 포함해 공통 검사 89개가 통과했다. 별도 자격 없는 OpenAlex·CORE 검색도 실제 응답했으며 CORE는 다른 검색식과 무작위 문자열의 0건을 대조했다. DBLP는 두 공식 호스트의 검색 API와 단건 XML·BibTeX에서 접근 확인 화면, Semantic Scholar는 rate_limited를 반환했다. 이러한 접근 상태를 전체 문헌 부재나 어댑터 기능의 검증 완료로 표시하지 않는다.


2026-09-10 Crossref의 공개 transform API 여덟 형식을 연결했다. DOI 10.1145/321250.321251의 BibTeX·RIS·CSL JSON·plain·RDF·Turtle·UNIXREF·UNIXSD를 실제로 회수했고, MCP에서 DOI filter 검색의 BibTeX와 여덟 export 및 CSL DOI를 대조했다. `data/validation/20260910T005047117230Z-crossref-workflow.json`이 전체 성공 기록이다. 이 DOI의 문헌은 A Turing Machine Simulator이며 P versus NP의 연구상 관련성을 판정한 사례가 아니다. 원 등록 JSON과 변환된 형식을 함께 보존한다. Crossmark는 같은 구현을 상속하지만 새 여덟 형식의 별도 Crossmark MCP 재검증을 한 것으로 세지 않는다.

WOS는 제목 후보 조회와 full-record URL의 accession 해석을 추가했다. 실제 The status of the P versus NP problem의 제목 후보 1건을 받고 그 accession의 URL로 서지·참고문헌을 회수했다. 해당 원 Full Record에는 AB 필드가 없어 abstract가 not_found이고 전체 fetch는 partial이다. 처음에는 모든 component가 available이어야 한다고 잘못 단언했으나 원 응답의 초록 부재를 확인하고 검증 기준을 교정했다. 전체 성공 보고 `data/validation/20260910T005047054448Z-wos-workflow.json`은 이런 부분 결과의 정확한 구분도 검사한다.

arXiv는 HTML URL을 입력해도 PDF를 반환하던 결함과 TeX 파일의 format_not_supported를 실제 2408.02321v1로 재현했다. HTML/src URL의 요청 형식을 유지하고 application/x-tex·application/x-latex를 줄 단위로 읽도록 수리했다. 실제 MCP에서 제목 검색·지정 판본 HTML·제목 추출·원 제출물 11개 파일·main.tex 564줄 중 앞 3줄 추출을 통과했다. 근거는 `data/validation/20260910T005450318569Z-arxiv-workflow.json`이다. 수식의 의미 판독이나 TeX 컴파일은 하지 않았다.

KNU FRIC는 등록 키가 필수인 OpenAPI를 제외하고 경북대 센터의 공개 웹 소장 목록을 연결했다. computer 1,121건의 9·10번째 위치, 기계적 CSV, ISSN 2263-8733의 단일 소장 기록, 무작위 문자열의 0건을 실제 MCP에서 확인했다. 0건 화면의 안내 li를 문헌으로 세지 않는다. `data/validation/20260910T010727692014Z-knu-fric-workflow.json`이 성공 근거다. 원 기록의 RISS 링크는 참조로 보존하며 자동 방문하지 않는다. 이 목록 endpoint에서 즉시 제공하지 않는 논문 원문·초록은 구별하고 복사 신청 안내 경로를 반환한다. 신청서를 제출하거나 직원에게 메시지를 보내지 않았다.

저자·기관 공개본과 학회·저널 범주는 알려진 공개 문서 URL 회수를 연결했다. 기관 인증 상태와 분리한 context에서 URL과 같은 호스트의 리디렉션·citation PDF만 처리하고, 사설망·로컬 주소를 거부한다. 저자 홈페이지의 Bellantoni–Cook 논문 14쪽 PDF와 홈페이지 링크 128개를 실제 MCP에서 회수했다(`data/validation/20260910T011434892309Z-author-repository-workflow.json`). Electronic Journal of Combinatorics DOI 10.37236/1181의 서지·초록·10쪽 PDF·공개 OJS RIS/BibTeX와 DOI 대조도 통과했다(`20260910T011745037521Z-society-journal-workflow.json`). 임의 플랫폼의 고급검색이 구현된 것으로 확대하지 않는다.

일반 웹 후보 검색은 추가 확인이 남았다. Bing HTML과 RSS는 입력 문자열을 유지했지만 무작위 문자열에 Apple·Anne Kennedy 등 무관한 결과를 반환했다. Google에서는 결과 목록이 없는 페이지, DuckDuckGo HTML에서는 HTTP 202와 결과 목록 부재를 관측했다. 이 관측을 정상적인 학술 후보 검색 검증으로 세지 않는다. FRIC 진단 중 형제 요소의 텍스트를 나열하다 공개 select 변경 JavaScript가 출력된 적이 있어 이후 출력 대상을 다시 제한했다. 그 출력에 비밀값은 확인되지 않았으며 원 JS를 일반 진단 출력으로 사용하지 않는다.

공통 검사 96개가 통과했다. 실제 성공한 형식·대상만 지원표 실측 표지에 반영했다. 전체 자료원의 구현 완료를 선언하지 않으며 남은 기관 검색·첨부·일반 웹 및 추가 입력 범위를 계속 처리한다.


2026-09-10 ScienceDirect의 기관 citation endpoint를 연결했다. KUDOS 바로가기에서 발급된 기관 context로 /sdfe/arp/cite를 요청하면 Natural Proofs, PII S002200009791494X, DOI 10.1006/jcss.1997.1494의 원 RIS와 994자 초록을 받았다. RIS는 제목 T1·DOI URL을 유지한다. 원 형식은 application/x-research-info-systems, text/x-bibtex, text/plain이며 Crossref의 MIME을 그대로 사용하면 provider_error였다. 실제 MCP에서 서지·초록·RIS·BibTeX·plain과 식별자 대조를 통과했다. 근거는 `data/validation/20260910T014021322060Z-science-direct-workflow.json`이다. fulltext 실패 시에도 이미 회수한 citation 구성요소는 보존한다.

ScienceDirect 문헌과 abs 경로는 접근 오류였다. pdfft는 Preparing your download HTML을 반환했고, Firefox와 Chrome의 실제 준비 페이지에서 30초 동안 PDF 응답이나 download 이벤트를 확인하지 못했다. 기본 검색은 Enter와 실제 submit 모두에서 검색 URL로 바뀌었지만 45초 뒤에도 홈페이지 내용을 표시했고 결과 목록을 확인하지 못했다. 검색·PDF·첨부는 완료로 세지 않는다.

AIP의 OA 문헌 10.1063/5.0281142에서는 PDF 요청이 watermark02.silverchair.com으로 이동해 기존 파일 호스트 검사에 막혔다. 이 호스트를 파일 다운로드에만 허용한 뒤 16쪽 PDF를 확보했다. 실제 MCP에서 기존 제목 검색·인용문·초록·페이지 경계와 새 문헌의 서지·초록·PDF·인용문, PDF 첫 쪽 DOI를 대조했다. `data/validation/20260910T015241129838Z-aip-workflow.json`이 성공 근거다. AAPT 문헌 10.1119/5.0328433의 PDF HTML 응답을 모든 AIP 문헌의 동일한 실패로 확대하지 않는다.

IOP의 명시적 /article/10.1088/0022-3727/34/10/311/meta 주소에서는 기존 문헌 어댑터로 서지와 16쪽 PDF를 받았다(`data/validation/20260910T020131Z-iop-fetch.json`). 원 초록 영역과 BibTeX·RIS 제어도 확인해 코드를 연결했다. 이후 두 MCP 재검증과 정상 KUDOS 깊은 문헌 링크·native export 확인은 validate.perfdrive.com으로의 접근 확인 때문에 완료하지 못했다. 인용문 응답의 실측 통과를 주장하지 않는다. gateway 오류에는 호스트만 추가해 원 URL 없이 진입 실패를 구별하고, 알려진 접근 확인 호스트로의 이동은 restricted로 분류한다. CAPTCHA 호스트를 자료원 호스트에 추가하지 않았다.

일반 웹 후보 발견은 별도 자격 없는 Mwmbl의 /search/?s= 공개 API로 연결했다. natural proofs의 관련 결과 25건, 그중 2건 CSV·원 강조 표시 조각의 보존과 추출, qzjxwv947231의 빈 결과를 실제 MCP에서 확인했다. `data/validation/20260910T023008496145Z-general-web-workflow.json`이 성공 근거다. returned_set_size는 API가 반환한 묶음의 크기이며 전체 웹 일치 건수가 아니므로 total=null이다. 앞선 다른 무작위 문자열의 20초 HTTP timeout도 있었으나 현재 어댑터는 공통 45초 제한과 typed timeout을 사용한다. API 실패 시 다른 검색 엔진으로 전환하지 않는다.

MCP 구조화 반환에도 공통 Sanitizer를 적용했다. 중첩 component의 서명 URL과 CSRF 필드가 정제 없이 반환되던 합성 값 사례를 재현하고 수리했다. 원 공개 서명·cursor 보존 규칙은 기존 정제기를 그대로 따른다. 새 회귀 검사를 포함해 공통 검사 101개가 통과했다. JSTOR 기관 PDF 주소는 별도 확인에서 HTML을 반환했고 SIAM의 공개 citation GET·POST는 HTTP 403이었다. 이 관측을 문헌 부재로 표시하지 않는다. 전체 구현은 여전히 부분 완료다.

Scopus 문헌 2-s2.0-77957268169의 References·Cited by 탭을 연결했다. 실제 MCP에서 참고문헌 47건을 다섯 페이지로 회수하고 피인용 문헌 3건을 추출했다. 검색 요약의 참고문헌 수는 48이고 문헌 탭·응답은 47이므로 search_metadata_count와 total을 구별한다. EID가 없는 참고문헌도 버리지 않는다. 성공 보고는 `data/validation/20260910T030610Z-scopus-relations.json`, 기존 미구현 재현은 `20260910T030257Z-scopus-relations.json`이다. 현재 /pages/publications/숫자 URL의 EID 해석도 회귀 검사했다.

KUDOS가 공개 제공한 ACM Open TitleList(2026).xlsx 원본 1,708,542바이트와 WOS savedrecs.xls 7,680바이트를 fixture로 보존했다. XLSX MIME의 openxml 문자열 때문에 ZIP을 XML로 파싱하던 결함을 재현하고 XML MIME 판정을 수정했다. XLSX의 세 시트 선택, Journal 178행, 수식 문자열·숫자 표시 형식·날짜 추출을 검사했다. XLS는 저장된 값·표시 형식을 읽으며 수식 정의나 매크로를 실행하지 않는다.

WOS 실제 Excel 응답은 XLS OLE 파일이어서 기존 고정 XLSX MIME으로는 추출이 실패했다. 파일 서명에 따라 MIME을 결정한 뒤 UT=(WOS:000269418800023)의 검색·native Excel·I/BE/BS 열 추출이 실제 MCP에서 통과했다. DOI 10.1145/1562164.1562186과 accession을 대조했으며 성공 보고는 `data/validation/20260910T033101Z-wos-excel-mcp.json`이다. 앞선 전체 WOS 흐름의 검색 TimeoutError와 Excel 파일 형식 결함을 구별한다.

로컬 Excel 검사는 통과했지만 MCP 호출 중 처음 openpyxl을 import하면 NumPy의 Windows native module 초기화에서 정지했다. 진단 스택으로 위치를 확인하고 stdio 스레드 시작 전에 openpyxl을 준비해 해결했다. `20260910T032427Z-wos-excel-mcp.json`은 검색 후 추출에서 멈춘 미완료 기록이며 성공으로 변경하지 않았다. 실제 stdio 회귀 검사는 XLSX 시트 선택과 XLS 필드 추출을 포함한다.

Project Euclid는 이전 Incapsula 관측 이후 원 공개 검색에서 양성 결과를 확인해 고급검색과 문헌별 내보내기를 연결했다. All Fields complexity는 7,662건, TITLE 검색은 2,806건이었다. 초기 Loading 화면을 0건으로 세지 않는다. 화면은 첫 페이지 25건을 표시하면서 /searchajax/Search/results의 page=2 응답을 미리 받았다. 이 JSON의 Query.Page와 화면 페이지는 달랐으므로 현재 표시된 페이지와 행 수를 기준으로 회수한다. 별도 HTTP 클라이언트의 같은 Ajax 주소는 HTTP 200 HTML을 반환했고 공개 API 동작으로 검증하지 못했다. 구현은 원 브라우저 경로로 고정했다.

고급검색은 필드·AND/OR/NOT 추가 조건·연도·발행물 선택을, 결과 조회는 정렬·25/50/75/100건 페이지를 지원한다. 원 50쪽 제한을 range_limit로 표시한다. 실제 고급검색 링크는 href 없는 a였고 첫 가시 제어가 다른 요소에 가려지는 경우가 있었다. 홈페이지의 마지막 가시 Advanced Search 제어와 발행물 목록을 여는 titleButton을 사용한다. 가능한 발행물은 search.facets.ref의 publication_titles에 보존한다.

연속 검색에서는 이전 저자·발행물 조건이 복원되어 TITLE complexity가 잘못 0건이 됐다. 검색식을 대조해 요청하지 않은 PubTitle을 탐지했다. 개별 입력과 체크박스를 해제해도 이 값이 남았으므로 공개 검색마다 빈 브라우저 컨텍스트를 만들고 원 홈페이지에서 시작하도록 바꿨다. 복잡한 UI 초기화 코드는 제거했다. `data/validation/20260910T035647Z-euclid-extended.json`은 잘못된 0건 재현이고, `20260910T035836Z-euclid-extended.json`·`20260910T035945Z-euclid-extended.json`은 남은 필터를 오류로 탐지한 기록이다.

DOI 10.1214/10-AOS798의 원 RIS·BibTeX·EndNote·인용문 PDF를 확보했다. EndNote는 %R 대신 %DOI 태그를 사용해 기존 파서가 실패했으며, 이 원 태그를 fields.DOI로 유지하도록 수리했다. 인용문 PDF는 서지·초록을 담은 1쪽이고 논문 전문은 38쪽이다. 두 PDF를 같은 자료로 표시하지 않는다. 원 세 텍스트 형식과 양성·0건 검색 HTML을 회귀 fixture로 보존했다.

최종 실제 MCP 보고는 `data/validation/20260910T040355588723Z-project-euclid-workflow.json`이며 completed=true다. 제목·두 저자·NOT 조건·발행물·2010년을 결합한 1건과 EndNote 추출, 다음 제목 검색의 최신순 100건 페이지 경계 2건, 문헌 서지·초록·38쪽 PDF·네 가지 원 인용문, PDF 첫 쪽 DOI와 후속 무작위 0건을 확인했다. 앞선 `20260910T040132369795Z-project-euclid-workflow.json`은 검색들은 통과했지만 문헌 서지 인식에서 실패한 부분 기록이다. 후속 직접·홈 경유 문헌 관측은 둘 다 정상이라 실패 원인을 경로 차이로 단정하지 않는다. 문헌 준비 대기가 일반 h1·og:title만으로 통과할 수 있던 조건은 실제 파서가 사용하는 citation/DC title 기준에 맞췄다.

이번 공통 검사 109개가 통과했다. Project Euclid의 부가 첨부 개별 회수 등은 남아 있으며, 전체 자료원 구현의 완료로 확대하지 않는다.

AMS는 algebra를 다시 검색해 원 브라우저에서 6,587건 중 첫 12건을 확보했다. /js/browse.js가 200으로 응답했고 /product/getbrowsefilters·/product/browseproducts의 원 응답도 받았다. 상품 응답은 Products·TotalRows·PageNumber·RowsPerPage 등을 포함한다. 책 SURV/168, 논문 DOI 10.1090/jams/1045와 학회 초록이 섞였다. Title·Subtitle은 별도 필드이며 DOI가 없는 자료도 유지한다. 원 응답 12건을 tests/fixtures/ams-products.json에 보존하고 행 수 불일치를 검사했다.

신규 AMS 어댑터는 원 기본 고급검색 필드·내용 유형·원 JSON·CSV·HTML을 연결했다. 동적 조건 그룹 편집과 native 파일 export의 검증은 남아 있다. 이후 어댑터의 algebra·topology 요청은 /browse에서 Just a moment를 반환했고, 실제 MCP 보고 `data/validation/20260910T043446741740Z-ams-workflow.json`도 restricted로 끝났다. 초기 양성 원 브라우저 관측을 신규 어댑터의 전체 MCP 통과로 표현하지 않는다. 원 exportproducts는 일반 context 요청과 사이트의 exportResults 함수를 사용한 정상 브라우저 요청 모두 HTTP 403이었다. 이를 XLSX나 문헌 부재로 해석하지 않는다. 책·논문 페이지 표본도 접근 확인을 반환했다.

별도로 AMS의 명시적 PDF 링크는 실제 다운로드에 성공했다. KUDOS 기관 경로의 gsm128-endmatter.pdf는 607,667바이트·51쪽이며, 파일 다운로드 시작 때문에 Playwright의 문헌 이동이 Download is starting 예외를 던졌다. 기존 MCP에서는 execution_error였고 `data/validation/20260910T044238Z-ams-pdf-mcp.json`에 재현을 남겼다. 단순 proxy URL 구성 뒤 context.request로 받는 시험은 403이라 그 방법으로 교체하지 않았다.

Publisher의 명시적 .pdf 파일 경로는 실제 native download 이벤트를 회수한다. 경로·쿼리가 요청과 같은 다운로드를 고르고, 허용한 자료원 URL인지 확인한 뒤 바이트를 읽는다. PDF 서명과 파서를 확인하고 파일·내장 메타데이터를 구별해 보존한다. 이벤트 listener와 해당 작업에서 연 페이지를 정리한다. 외부 자료원 download는 파일을 읽거나 artifact로 보존하지 않는 대역 검사도 통과했다. 브라우저 이동의 사후 호스트 검사와 HTTP 다운로드의 redirect 사전 검사를 같은 보장으로 표현하지 않는다.

수리 후 실제 MCP의 PDF fetch·메타데이터 구분·51쪽 파일 추출이 `data/validation/20260910T044529Z-ams-pdf-mcp.json`에서 completed=true로 통과했다. 재실행 도구는 tests/live_ams_pdf.py다. 이 파일은 별도 부속 PDF이며 전체 책 51쪽을 확보했다고 주장하지 않는다. 공통 검사 113개가 통과했고 AMS의 검색·원 파일 내보내기 전체 검증은 계속 남아 있다.

SIAM 공개 홈페이지는 정상이었지만 convex optimization 검색은 /action/doSearch의 접근 확인 화면이었다. 문헌 앞부분의 실제 PDF 주소 /doi/pdf/10.1137/1.9781611974997.fm은 별도 계정 없이 10쪽 파일을 반환했다. 이 URL 형식을 명시적 파일 경로로 연결하고 SIAM 어댑터를 등록했다. 실제 MCP fetch·PDF 내장 메타데이터 구분·첫 쪽 제목·10쪽 추출이 `data/validation/20260910T050425088629Z-siam-workflow.json`에서 통과했다. 별도 직접 어댑터 관측에서는 SIAM News June 2025 PDF 12쪽도 회수했다. 책 Front Matter의 /doi/abs 페이지는 PDF 회수 후에도 document_not_ready였으므로 웹 서지·검색·인용문 전체를 검증한 것으로 확대하지 않는다.

IEEE 문헌 10488889의 supplementary 분기에는 단순 h1 대기가 있었다. 실제 문헌에는 문헌 제목·Alerts·References의 h1 세 개가 있어 strict-mode 오류였다. 문헌 제목 h1.document-title과 가시 References 탭으로 좁혔다. 그 뒤 화면은 References is not available for this document라고 표시했지만 원 /rest/document/10488889/references 응답의 articleNumber는 10488889이고 references 배열은 22건이었다. 첫 항목은 PRIMES is in P, DOI 10.4007/annals.2004.160.781이었다. 화면 안내로 원 응답까지 없다고 잘못 보고한 부분은 배열 확인 후 정정했다.

IEEE 원 참고문헌의 문헌 번호와 배열 형식을 대조하고 order·id·title·text·context·links 등 각 항목의 원 필드를 유지했다. userInfo와 사용자 설정 상태를 빼고 문헌·참고문헌에 해당하는 응답을 보존한다. 외부 인용 링크는 자동 방문하지 않는다. 실제 MCP에서 22건을 회수·추출한 보고는 `data/validation/20260910T051301Z-ieee-references-mcp.json`이며 completed=true다. 개별 첨부는 아직 미구현이어서 fetch 전체와 supplementary는 partial, references는 available로 구별한다. 공통 검사 115개가 통과했다.

Springer Nature의 원 부가자료 제어를 supplements.py에 연결했다. KUDOS Springer 경로로 연 Nature Communications의 DOI 10.1038/s41467-023-41217-6 문헌에 Supplementary Information과 Peer Review File 두 PDF가 있었다. 실제 파일 호스트는 media.springernature.com이었으며 파일 다운로드 허용 목록에만 추가했다. 문헌 전용 보충 자료 제어의 제목·설명·URL과 파일 경로에 표시된 DOI를 보존하고, 다른 문헌 DOI이면 명시적 선택을 요구한다. 페이지의 다른 PDF 링크를 첨부로 섞지 않는 검사도 통과했다.

실제 MCP 보고 `data/validation/20260910T052618Z-springer-supplements-mcp.json`은 completed=true다. 두 파일의 native PDF를 보존하고 각각 42쪽·19쪽과 첫 쪽 추출을 확인했다. 파일 하나의 실패가 먼저 받은 파일을 없애지 않도록 전체 목록·파일별 상태·성공 파일을 함께 반환하는 대역 검사도 통과했다. 부가자료 제어가 없는 다른 레이아웃은 source_page로 남기며 파일 부재라고 단정하지 않는다. 원 제어 두 개만 기계적으로 선택한 HTML을 fixture로 보존했다. 뒤에서 덮어쓰던 오래된 Springer 사용 설명도 제거해 현행 설명 한 곳으로 정리했다. 공통 검사 117개가 통과했다.

zbMATH 문헌 1079979, Zbl 0884.68055, DOI 10.1006/jcss.1997.1494의 원 editorial_contributions는 summary 한 개였지만 텍스트는 라이선스 충돌로 내용을 제공하지 않는다는 75자 안내문이었다. 기존 fetch가 이를 abstract available로 반환하던 결함을 재현해 restricted/content_license_restriction으로 수리했다. 실제 텍스트가 있는 review·summary는 원 유형과 source_page 상태를 유지하고 저자 초록으로 추론하지 않는다. 정상 빈 배열·다른 문헌 ID 응답·라이선스 제한을 별도로 검사했다. 원 참고문헌 40건은 supplementary로 회수한다.

zbMATH의 start를 limit 배수로 제한하던 구현도 바꿨다. 필요한 원 페이지를 조합하고, 전체 건수·원 행 수를 대조한 뒤 요청 창만 반환한다. 원 페이지들을 evidence와 native export로 보존하고 문헌 artifact에 모든 근거 참조를 기록한다. 실제 MCP에서 start=1, limit=2의 두 문헌을 start=0, limit=4 결과의 같은 구간과 대조했다. DOI, 제목 후보, ?q=an:0884.68055 링크와 참조 40건도 통과했다. 성공 보고는 `data/validation/20260910T055908908091Z-zbmath-workflow.json`이다.

DOI는 현재 문헌 links의 doi 항목과 대조하며 참고문헌 DOI로 식별하지 않는다. ID와 Zbl 번호도 원 record.id·identifier와 각각 대조한다. 10.으로 시작하는 점 구분 번호를 DOI로 잘못 해석하지 않도록 DOI의 슬래시 형태를 구별했다. /v1/openapi.json은 별도 자격 없이 받았으며 두 웹 BibTeX 후보 URL 시험은 403이었다. 이 후보 경로의 존재나 native BibTeX 회수 성공을 주장하지 않는다. 공통 검사 122개가 통과했다.

Wiley DOI 10.1002/rsa.70063, Models of Random Spanning Trees의 Supporting Information 표는 rsa70063-sup-0001-Supinfo.zip과 Data S1. 설명을 제공했다. 원 제어는 /action/downloadSupplement의 doi·file 매개변수였다. 이 표의 파일만 선택하고 DOI·파일명·설명을 보존하도록 연결했다. 원 ZIP을 검사해 application/zip으로 보존하며 HTML 응답을 자료로 저장하지 않는다. 파일별 상태와 성공 파일을 유지하는 처리는 기존 Springer Nature와 공유한다.

실제 MCP 회수와 ZIP 구성 항목 조회는 `data/validation/20260910T062556Z-wiley-supplements-mcp.json`에서 completed=true로 통과했다. 디렉터리 anc/와 anc/dimension_bounds.py·anc/internal_external.py를 확인했다. 이어 `data/validation/20260910T063011Z-wiley-archive-extract-mcp.json`에서 두 파일을 각각 선택·추출하고 260줄·303줄 중 앞 3줄을 실제 MCP로 읽었다. 원 코드를 실행하지 않았다. 회귀 fixture에는 Supporting Information 표만 보존했으며 Python 원문을 추가하지 않았다. 공통 검사 123개가 통과했다.

ScienceDirect의 추가 관측에서는 초기 홈페이지 폼의 action이 비어 있었고 Enter 뒤 /?qs=algebra에 머물렀다. 페이지 새로고침·프레임 확인도 검색 결과를 만들지 않았다. 원 스크립트는 모두 200 JavaScript였고 pageerror가 없었으므로 자산 로딩 결함을 원인으로 단정하지 않았다. 이후 React 입력·submit handler가 준비된 상태에서 실제 키보드 입력은 /search/autosuggest/keyword 응답을 받았다. 원 Submit quick search 버튼을 클릭하자 실제 /search?qs=algebra로 이동했지만 문서 응답은 HTTP 403, CPE00001이었다. KUDOS의 해당 자료원 깊은 링크로 검색 주소에 직접 진입해도 CPE 오류였다. 정상 검색 경로의 접근 실패로 기록하며 0건이나 특정 장애 원인으로 해석하지 않는다. 코드에 확인되지 않은 검색 API를 추가하지 않았다.

AIP DOI 10.1063/5.0282369의 원 supplementary material 링크는 별도 Figshare 컬렉션 DOI 10.60893/figshare.aip.c.7956296이었다. 문헌 section의 실제 링크와 문구를 읽고 중복을 제거해 source=figshare·target DOI·selection_required로 반환한다. AIP 호출에서는 외부 파일을 받지 않는다. 실제 MCP `data/validation/20260910T082756Z-aip-supplement-mcp.json`은 참조 1개·파일 0개와 정확한 DOI를 확인해 completed=true다.

Figshare는 [공식 공개 API 명세](https://docs.figshare.com/swagger.json)의 security=[] 경로와 별도 인증 없는 실제 응답을 확인해 독립 자료원으로 추가했다. public articles/collections 검색 POST, metadata GET, 현재 컬렉션 구성원 조회, 명시적 article 버전 파일 회수를 연결했다. 검색 전체 건수는 제공되지 않아 total=null로 남긴다. 공식 본문과 OpenAPI의 offset 상한 설명은 각각 1000·5000으로 달라 현재 OpenAPI의 5000을 구현 상한으로 사용하고 실제 서버 거절은 보존한다. 높은 offset 범위의 실서비스 통과를 주장하지 않는다. 호출 간격은 공식 권고에 따라 1.05초다.

실제 MCP `data/validation/20260910T082645946023Z-figshare-workflow.json`은 quantum 검색 3건과 start=1/limit=2의 일치, 현재 컬렉션 7956296의 구성원 29678765, 문헌 DOI 10.60893/figshare.aip.29678765.v1의 버전 1과 Supp.pdf 추출을 확인해 completed=true다. 파일은 2,790,536바이트·5쪽이며 제공된 MD5 bdfa565f42075d264cf31684d21d7635와 일치했다. ndownloader.figshare.com의 파일 경로가 실제 AIP S3 저장소로 연결되는 것을 관측하고 그 저장소 경로만 허용했다. 다른 저장소는 source_boundary로 남는다.

Figshare 공개 명세에는 과거 collection version metadata 경로가 있지만 버전별 구성원 목록 경로는 없다. 해당 추측 경로의 실제 응답도 404였다. 버전을 지정한 컬렉션의 supplementary는 not_implemented이며 현재 목록으로 바꾸지 않는다. current collection의 페이지별 참조와 건수를 보존하고 제한·후속 실패·중복 행을 partial로 구별한다. 외부 is_link_only는 selection_required이며 다운로드하지 않는다. 공개 파일 제한 플래그·잘못된 문헌/버전·체크섬 오류와 POST 리디렉션 경계를 회귀 검사했다. 정규화 레코드에서 url_private_*를 제외하며 원 공개 응답은 evidence로 보존한다.

Figshare 단위의 공통 검사 130개가 통과했다. 이어 Cambridge·Oxford 보충자료를 원 문헌 제어에서 회수하도록 연결하고 공통 검사 133개가 통과했다. Cambridge DOI 10.1007/s11336-020-09720-7의 원 #supplementary-materials-tab .materials-table__item에는 같은 제목의 PDF·ZIP 두 파일이 있었다. 다운로드 앵커 자체는 텍스트가 없어서 앵커 문구로 파일을 발견할 수 없었다. 실제 표의 제어·제목·설명을 읽으며 파일명 PII를 문헌 PDF 메타데이터의 PII와 대조한다. static.cambridge.org는 파일 호스트로만 허용했다.

Cambridge 실제 MCP `data/validation/20260910T083607Z-cambridge-supplements-mcp.json`은 S0033312300006608sup001.pdf 6쪽과 S0033312300006608sup002.zip의 구성 항목 3개를 확인해 completed=true다. 후속 `data/validation/20260910T083826Z-cambridge-archive-extract-mcp.json`은 code_to_reproduce/·PMET.RData·PMET.R 목록과 R 소스 154줄 중 앞 3줄 추출을 실제 MCP로 검증했다. R 코드를 실행하거나 RData 실행 환경을 불러오지 않았다.

Oxford DOI 10.1093/restud/rdag022에는 본문에 같은 보충 PDF를 가리키는 링크가 반복됐다. 파일 목록은 본문 링크 전체 대신 .widget-ArticleDataSupplements .dataSuppLink a에서 읽는다. 실제 파일 호스트 oup.silverchair-cdn.com을 파일 회수에만 허용하고 경로의 10.1093_restud_rdag022를 현재 DOI의 부호화 결과와 대조했다. 밑줄을 일괄 슬래시로 복호화해 원 DOI를 추측하지 않는다. 실제 MCP `data/validation/20260910T083741Z-oxford-supplements-mcp.json`은 rdag022_supplementary_data.pdf 32쪽과 첫 쪽 추출이 completed=true로 통과했다. 두 출판사의 회귀 fixture는 보충자료 제어 영역만 보존하며 원 연구 파일은 커밋에 넣지 않았다.

PQDT 문헌 2485541561의 보충 파일 조사에서 다운로드 동작 URL은 Tapestry 형식의 경로 인자로 서명된 미디어 URL을 포함했다. 진단이 호스트·경로를 안전한 정보로 취급해 이 경로를 출력한 누락이 있었다. 사용자에게 즉시 알렸으며 서명 값을 이 기록에 반복하지 않는다. 기존 정제기는 일반 쿼리의 인증 필드를 제거했지만 $2f·$3f·$3d로 인코딩된 경로 내부 URL을 처리하지 못했다.

Sanitizer는 Tapestry 또는 percent 인코딩된 경로 내부 URL에서 인증 쿼리·userinfo가 발견되면 그 내부 URL 인자를 제거하고 원 다운로드 동작·파일명은 유지한다. 합성 값으로 URL·문자열·구조화 필드와 일반 공개 DOI 참조 보존을 검사했다. 진단 자체는 이제 다운로드 경로를 출력하지 않고 이름·호스트·제어 구조만 읽는다. 로컬 pqdt-supplements-clean.html도 다시 정제해 해당 인자를 제거했다. 보호된 원 응답은 .credentials 아래에 남겼다. 이미 표시된 도구 출력 삭제나 서명 무효화는 확인하지 않았으며 전체 과거 로그를 감사했다고 주장하지 않는다. 이 정제 단위의 새 검사 2개가 통과했다.
