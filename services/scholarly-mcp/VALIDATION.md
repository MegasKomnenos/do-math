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

IEEE 문헌 10488889와 7780459의 실제 화면에는 Media 탭이 없었다. [IEEE의 공식 동영상 수상 목록](https://ieeeaccess.ieee.org/authors/awards/)에서 확인한 문헌 11259066, A Comparative Study of Coherent Ising Machine Architectures Through a Unified Simulation Model도 sections.multimedia=false였지만 graphicalAbstract에는 video·file·coverImage가 있었다. 따라서 Media 탭 부재를 모든 부가 파일의 부재로 보지 않는다. 문헌의 xplGlobal.document.metadata JSON을 실행 없이 파싱하고 문헌 번호·허용 필드를 대조해 그래픽 초록과 표지를 회수한다. userInfo와 운영 설정은 보존 대상에서 제외한다.

같은 문헌 경로의 표지 JPEG는 36,328바이트로 바로 회수됐다. 표시 크기 99.32MB의 MP4는 일반 요청에서 45초·180초 모두 시간 초과였고 실제 MCP `data/validation/20260910T084913Z-ieee-media-mcp.json`은 partial/미완료로 남겼다. 제한 시간을 계속 늘리지 않고 실제 Range bytes=0-65535 응답을 확인했다. HTTP 206, Content-Range bytes 0-65535/104143825, video/mp4, Last-Modified가 있었고 ETag는 없었다.

MP4 회수는 4MiB 단위 요청으로 바꿨다. 모든 응답의 Content-Range 시작·끝·전체 크기·실제 바이트 길이와 같은 URL을 검사한다. 강한 ETag를 우선 사용하며 없으면 충분히 분리된 Date/Last-Modified를 사용한다. [RFC 9110의 validator·If-Range 규칙](https://www.rfc-editor.org/rfc/rfc9110.html#section-13.1.5)을 따르고 날짜 비교에는 60초의 보수적 간격을 둔다. weak ETag나 검증자 부재는 조립 실패이며, 원 45초 요청 제한을 유지한다. 일반 browser_download에는 필요한 상태·range·validator 헤더만 선별해 전달하는 내부 옵션을 추가했다.

최종 실제 MCP `data/validation/20260910T085604Z-ieee-media-mcp.json`은 completed=true다. 문헌 11259066의 참고문헌 30건, 표지 JPEG, 25개 구간의 MP4 104,143,825바이트와 이미지 추출을 확인했다. 원 MP4 컨테이너 서명과 저장 해시를 확인했으며 동영상 내용을 판독하지 않았다. 이어 문헌 10488889는 참고문헌 22건·첨부 not_found로 구별했다. 참고문헌과 첨부는 독립적으로 처리해 한쪽 실패가 다른 쪽의 자료를 버리지 않는다. 별도 multimedia=true 레코드의 Media 탭 회수는 미구현으로 남는다. 중첩 다운로드 URL 정제를 포함한 공통 검사 142개가 통과했다.

PQDT 문헌 2485541561의 원 Supplemental files 탭에는 TLTC_Teaching_Learning_Teaching_Continuum.PNG 하나가 있었다. KUDOS의 PQDT 바로가기로 기관에 접속한 뒤 해당 문헌 탭을 선택했다. Document includes N supplemental file(s) 건수와 .suppFiles의 개별 제어 수를 대조한다. 원 Terms of Use의 다운로드 동작은 현재 파일명을 경로 인자로 포함하므로 표시명과 대조한다. 서명된 내부 URL은 제어 수행에만 사용하며 반환 파일 목록에는 넣지 않는다.

원 PNG는 529,775바이트로 확보됐다. 실제 MCP `data/validation/20260910T091220Z-pqdt-supplement-mcp.json`은 metadata·supplementary 회수와 extract의 구조화 이미지 결과 및 MCP ImageContent를 확인해 completed=true다. 파일 목록의 누락·건수 불일치·잘못된 파일명과 명시적 0건을 구별하는 검사를 추가했고 공통 검사 145개가 통과했다. 파일별 실패 때 성공 파일은 유지한다. Supplemental files 탭이 없는 문헌은 source_page로 남기며 다른 권한·레이아웃의 파일 부재를 추론하지 않는다.

Taylor & Francis DOI 10.1080/10618600.2017.1349663, Goodness of Fit of Logistic Regression Models for Random Graphs의 첫 진단은 citation_title만 기다려 시간 초과였다. 보존 페이지를 확인하니 dc.Title·dc.Identifier·publication_doi를 제공하는 정상 문헌이었다. 진단 대기를 현재 메타데이터에 맞췄다. 공통 Publisher의 DOI 인식도 citation_doi 외 실제 Dublin Core·publication_doi를 받아들인다. 숫자 native ID 1349663과 DOI를 구별하고, URL 입력에서 관측한 DOI를 requested_doi로 잘못 표시하지 않도록 별도 보존하는 검사를 추가했다.

원 #supplemental-material-section의 /action/downloadSupplement에는 ucgs_a_1349663_sm4648.zip이 있었다. 본문 .tableDownloadOption의 /action/downloadTable?downloadType=CSV 제어는 t0001·t0003 두 표였다. 문헌 DOI를 대조하며 보충 ZIP과 본문 표 CSV의 역할을 구별한다. 표의 반환 파일명은 table_id에 .csv를 붙인다. 원 CSV에는 각각 데이터 행 3개·열 4개가 있고 두 번째 표의 첫 열 헤더는 빈 문자열로 유지한다.

실제 MCP `data/validation/20260910T092557Z-taylor-francis-supplements-mcp.json`은 metadata·native BibTeX·초록, ZIP 1,111,477바이트·항목 5개, CSV 195바이트·230바이트와 각 표의 행 추출을 통과했다. 그 뒤 입력 DOI와 관측 DOI의 구분은 오프라인 URL fetch 검사로 교정했다. ZIP에는 설명 텍스트, PDF 3개와 code.tar.gz가 있었다. 후속 실제 MCP `data/validation/20260910T092834Z-taylor-archive-mcp.json`은 내부 tar.gz의 항목 14개와 code/gof.R 90줄 중 앞 3줄을 읽어 completed=true로 통과했다. R·C++ 코드를 실행하거나 포함된 패키지를 설치하지 않았다. 공통 검사 148개가 통과했다.

De Gruyter Brill DOI 10.2202/1558-3708.1089는 첫 기관 이동 실패 뒤 재조회에서 정상 서지와 Data and code (zip file) 제어를 제공했다. .supplementary-material-list a.ga_download_supplementary 제어의 downloadAsset 경로에서 DOI·파일명을 읽는다. 구형 제어는 /suppl 중간 경로 없이 파일명이 바로 붙었다. 실제 MCP `data/validation/20260910T093333Z-de-gruyter-supplements-mcp.json`에서는 snde1089_supplementary_2.zip 요청이 404였으므로 metadata available, 파일 not_found, supplementary partial을 보존했다. 문헌의 제어 존재를 파일 회수 성공으로 세지 않는다.

두 번째 문헌 DOI 10.1524/zkri.2013.1610의 원 zkri.1610_supplmat.zip은 6,379바이트로 회수됐다. 실제 MCP `data/validation/20260910T093526Z-de-gruyter-supplements-mcp.json`은 metadata·보충 ZIP·구성 항목 한 개를 확인해 completed=true다. 후속 `data/validation/20260910T093733Z-degruyter-archive-mcp.json`은 내부 Cobtcsub.cif 19,132바이트를 추출하고 512줄 중 앞 3줄을 읽었다. 기존 UTF-8 텍스트 추출이 작동했으며 CIF 사전 해석이나 결정 구조 분석기를 추가하지 않았다. 공통 검사 149개가 통과했다.

ACM DOI 10.1145/3425501, Greed Is Good: Exploration and Exploitation Trade-offs in Bayesian Optimisation의 원 문헌에는 .core-supplementary-materials 아래 george.zip이 있었다. 최초 진단은 HTML 정제 과정에서 잘못된 포트를 가진 URL 한 개 때문에 ValueError로 끝났다. 값이나 원 예외 메시지를 출력하지 않고 스택의 파일·행·함수만 확인했다. Sanitizer는 잘못된 포트·IPv6 등 파싱할 수 없는 URL을 표시용 표지로 바꾸고 주변 문헌은 유지하도록 수리했다. 인증 정보가 포함된 합성 잘못된 URL과 주변 텍스트 보존을 회귀 검사했다. 이 관측에서는 새 인증값 노출을 확인한 것이 아니다.

ACM 보충 제어의 /doi/suppl/DOI/suppl_file/파일명 경로를 현재 DOI와 대조하며 원 설명을 유지한다. 공유 보충 회수 함수에 ACM의 파일 호스트 집합을 전달하도록 연결했다. 실제 MCP `data/validation/20260910T094619Z-acm-supplement-mcp.json`은 metadata·초록·원 BibTeX·ZIP 9,708,127바이트와 구성 항목 2개를 확인해 completed=true다. 후속 `data/validation/20260910T094946Z-acm-archive-mcp.json`은 george/3425501.suppl.pdf 10,527,022바이트를 추출하고 27쪽 중 첫 쪽을 읽었다. 원 참고문헌 문맥은 기존 source_page에 유지하며 다른 미인식 첨부 레이아웃은 source_page로 남긴다. 공통 검사 151개가 통과했다.

공개 API 재검증 `data/validation/20260910T094831Z-public-followup-mcp.json`에서 Semantic Scholar·OpenAlex·CORE의 natural proofs 검색 2건과 추출이 성공했다. DBLP는 access_challenge였다. 후속 `data/validation/20260910T095105Z-public-fetch-followup-mcp.json`에서 Semantic Scholar·CORE의 ID fetch는 rate_limited였고 OpenAlex는 서지 메타데이터를 확보했다. 검색의 양성 결과를 전체 fetch 성공으로 확대하지 않는다.

CORE의 실제 검색 기록 340524929에는 fullText가 35자 안내문 Not available for public API users.였다. 기존 fetch가 같은 레코드를 받으면 이 비어 있지 않은 문자열을 fulltext available로 표시하는 결함을 원 응답 fixture로 재현했다. 접근 안내문은 restricted/public_fulltext_restricted, 빈 필드는 not_found, 실제 색인 본문은 별도 text/plain artifact로 구별했다. 문헌 ID를 대조하고 이름은 원 검색 후보로 반환한다. 이 교정과 실제 텍스트 보존·빈 초록·잘못된 ID의 오프라인 검사가 통과했다.

신규 CORE 전체 실서비스 흐름 `data/validation/20260910T100059Z-core-public-mcp.json`은 이름 후보 요청부터 rate_limited여서 completed=false다. 새 입력·fulltext 상태 처리 전체를 실제 MCP 성공으로 기록하지 않는다. 별도 API 자격을 요청하거나 다른 자료원으로 자동 이동하지 않았다. 공통 검사 154개가 통과했다.

OpenAlex의 현행 공식 문서는 [help.openalex.org](https://help.openalex.org/api/)로 이동했다. 기본 계정·키 없는 API 사용을 명시하며 실제 익명 검색·단건·그룹 요청도 성공했다. 일반 개요의 최대 100건 설명과 달리 실제 per_page=200 요청은 200건과 meta.per_page=200을 반환했다. 기존 200 상한을 유지하고 이 실측을 문서 한 줄만으로 축소하지 않았다.

기존 OpenAlex group_by는 원 group_by 배열을 results로 읽어 실패했다. 원 응답과 [집계 명세](https://help.openalex.org/api/grouping/)에 맞춰 그룹을 별도로 반환한다. meta.count는 집계 대상 문헌 수, groups_count는 현재 페이지의 그룹 수이며 전체 그룹 수가 아니다. group_by는 처음부터 원 커서의 key 순서를 사용하며 문헌 sort/select와 함께 요청하면 명시적 오류다. 일반 커서의 끝을 전체 count와 잘못 비교해 빈 마지막 페이지를 오류로 만들던 처리도 수정했다.

일반 검색은 필요한 원 페이지를 결합해 임의 start/limit 창을 회수하고 모든 근거 참조를 기록한다. 뒷 페이지 요청 실패 때 앞서 받은 창을 partial로 남긴다. 이름은 원 검색 후보, OpenAlex의 짧은 ID·works/ID·URL·DOI는 단건 조회다. 문헌 ID를 대조하되 공식 canonical redirect는 기록하며 허용한다. DOI가 다른 canonical DOI로 해석되면 후보 선택을 요구한다. 원 HTTP redirect와 후속 페이지 실패는 대역 검사로 확인했다.

OpenAlex abstract_inverted_index는 단어와 위치의 원 대응을 검증해 한 칸 공백으로 복원한다. 중복·음수·잘못된 위치·빈 구간을 추측해 채우지 않는다. 원 색인은 metadata에 남는다. [공식 속성 설명](https://help.openalex.org/data/works/attributes/)처럼 이 색인상 초록은 출처가 다양하고 원 저자 초록과 다른 텍스트를 포함할 수 있으므로 출판사 원문과의 동일성을 주장하지 않는다. supplementary에는 나가는 referenced_works와 related_works를 별도 배열로 보존하며 연결 문헌을 자동 확보하지 않는다.

실제 MCP `data/validation/20260910T101414398637Z-openalex-workflow.json`은 completed=true다. 구문 검색의 앞 4건과 start=1/limit=2를 대조하고, 그룹 두 페이지, works/W2741809807 URL·1,630바이트 복원 초록·참고 54개·관련 10개, 이름 후보, DOI 10.1006/jcss.1997.1494의 초록 not_found·참고 36개를 확인했다. 공통 검사 162개가 통과했다.

Semantic Scholar의 [공식 Swagger](https://api.semanticscholar.org/graph/v1/swagger.json)에서 문헌 조회·참고/피인용 페이지·citationStyles·필터 의미를 확인했다. openAccessPdf는 값 없는 존재 필터라 기존 false 직렬화도 필터를 켤 수 있었다. true일 때만 빈 값으로 보내고 false/null은 제외하도록 수리했다. 이름 조회에는 문서화된 하이픈 제약을 반영하되 명시적 search query는 바꾸지 않는다. 원 요청 이름도 보존한다.

Semantic Scholar 문헌 URL·별칭 ID를 대조하고, 문헌 검색 100건·관계 검색 1000건 상한과 원 offset/next를 구별했다. relation record의 paperId=null도 버리지 않는다. supplementary는 나가는 참조 페이지를 회수하며 뒤에서 제한되면 이미 받은 참조와 원 reported count를 유지한다. 피인용은 search kind=citations로 필요한 범위를 지정한다. 기본 metadata 요청에 references/citations 전체 배열을 포함하지 않는다. 원 citationStyles.bibtex는 파싱 가능한 한 건인지와 제공되는 DOI를 대조하며, 잘못된 원 파일은 고쳐 쓰지 않고 오류와 source_export로 보존한다.

이 신규 Semantic Scholar 범위의 검증은 원 검색 record fixture와 공식 응답 구조에 근거한 대역 검사다. 새 실제 MCP `data/validation/20260910T103916Z-semantic-scholar-mcp.json`은 첫 검색에서 rate_limited라 completed=false다. 앞선 공개 검색 양성 기록과 이 미완료 기록을 구별하며, 관계·BibTeX가 실제 API에서 통과했다고 주장하지 않는다. 429 뒤 후속 원격 요청을 계속하지 않았다. 공통 검사 171개가 통과했다.

현재 Codex에 등록된 scholarly의 describe_source(openalex)를 직접 호출하자 이전 public_endpoint_search_observed 설명이 반환됐다. 새 코드 검증은 매번 새 stdio 프로세스를 띄운 SDK 호출이며, 이 기존 연결을 갱신한 것으로 세지 않는다. 설치된 CLI의 mcp 관리 명령에는 재시작이 없었다. 생성한 app-server 명세에는 config/mcpServer/reload가 있었지만 이 Windows 환경의 기본 제어 소켓에 연결하지 못했고 daemon 관리도 Unix 전용이었다. 관련 없는 서버 프로세스를 종료하거나 원격 제어를 활성화하지 않았다. [공식 MCP 안내](https://developers.openai.com/codex/mcp/)의 클라이언트 재시작 절차를 사용해야 한다.

프로젝트 scholarly 설정의 tool_timeout_sec는 HEAD와 작업 파일 모두 180이었다. 실제 성공한 대용량 회수 시간을 수용하도록 이 값만 1800으로 바꿨다. 나머지 작업 파일 바이트가 같음을 비교했고, HEAD 기준의 이 한 줄 변경만 index에 적용해 기존 사용자 설정 변경을 커밋에 섞지 않았다. TOML 파싱으로 설정값을 검증했다. 이 설정 변경 시점의 연결에는 재시작이 필요했다. 후속 갱신 확인은 아래 기록을 따른다.


2026-09-10 사용자 재시작 뒤 등록된 Codex scholarly 연결의 describe_source(openalex)는 live_mcp_arbitrary_window_group_cursor_abstract_relationships_name_doi와 group_by 사용법을 반환했다. 새 코드가 실제 연결에 반영된 검증을 통과했다. 요약 보고는 data/validation/20260910T122338Z-registered-restart.json이다. 같은 연결의 AMS algebra 검색은 restricted/publisher_access_challenge, IOP 문헌 조회는 publisher_redirect 단계의 같은 제한으로 끝났다. 연결 갱신과 기관 워크플로 완료를 구별하며 보고의 completed는 false다.

AMS의 원 66바이트 서비스 불가 HTML을 fixture로 보존했다. 이전 input_value TimeoutError를 provider_unavailable로 분류하고, HTTP 오류·접근 확인·미준비 제어를 구별한다. 실제 MCP 20260910T111551961664Z-ams-workflow.json은 앞선 gateway_navigation_failed에서 끝났으므로 새 분기 검증으로 세지 않는다. IOP의 20260910T112043832340Z-iop-workflow.json은 metadata·abstract만 available이며 fulltext·BibTeX·RIS는 validate.perfdrive.com 이동이었다. 공유 다운로드 함수는 이 접근 확인 목적지로 요청을 보내기 전에 restricted를 반환한다. 허용 호스트를 확대하지 않았다. 새 실제 재검증은 기관 진입에서 막혔고, 파일 리디렉션 분기는 합성 응답으로 후속 요청 부재·민감 값 비노출을 확인했다. 공통 검사 173개가 통과했다.


Project Euclid의 Supplemental Content는 기본 문헌 HTML에 없는 별도 탭이었다. 실제 #sup 클릭 뒤 divARTICLECONTENTCITEDTop의 다운로드 행을 파싱한다. 파일 경로의 원 문헌 DOI, supplement_doi, 제목·설명을 구별하며 설명의 외부 GitHub 링크는 따라가지 않는다. 첫 DOI 10.1214/25-AOAS2099의 두 파일은 원 GET에서 문헌 HTML을 반환하고 UI 클릭도 다운로드를 발생시키지 않았다. 실제 MCP data/validation/20260910T123332Z-project-euclid-supplements-mcp.json은 partial/미완료로 남겼다. 다른 DOI 10.1214/14-AOS1230은 원 UI에서 333524바이트 PDF가 다운로드됐다.

DOI 10.1214/24-AOAS1990의 새 MCP data/validation/20260910T124043Z-project-euclid-supplements-mcp.json은 completed=true다. aoas1990suppa.zip 18431바이트·8항목, aoas1990suppb.pdf 2174641바이트·26쪽을 회수·추출했다. 등록된 MCP의 data/validation/20260910T124410Z-euclid-archive-mcp.json에서도 ZIP 안의 Analysis 텍스트 449줄 중 앞 3줄을 읽었다. 연구 코드를 실행하지 않았다. 해당 변경 시점 공통 174개 검사가 통과했다.

재시작 이후 기관 검색 재확인: JSTOR 홈페이지는 Shadow DOM 안에 Query 입력을 제공했다. 실제 algebra 입력 뒤 Client Challenge와 capInput이 나타났다(.credentials/scholarly-mcp/probes/20260910T122819Z-jstor-native-search.html). SIAM algebra는 Just a moment(20260910T122547Z-siam-native-search.html), APS 기관 quantum computation도 같은 접근 확인(20260910T123205Z-aps-native-search.html)이었다. ScienceDirect의 실제 Submit quick search로 random graphs를 제출한 결과는 CPE 안내(20260910T123815Z-science-direct-native-search.html)였다. 이 조사는 직접 브라우저 제어 관측이며 새 검색 어댑터의 MCP 성공으로 세지 않는다. CAPTCHA를 해결하거나 파일 허용 호스트를 확대하지 않았다.


IEEE 문헌 8626436, Bio-LSTM: A Biomechanically Inspired Recurrent Neural Network for 3-D Pedestrian Pose and Gait Prediction은 metadata.sections.multimedia=true와 Media 탭의 원 MP4를 제공했다. 실제 등록 MCP의 기존 구현은 해당 첨부를 not_implemented로 반환했다. 원 화면은 media-tab 영역을 두 번 렌더했으며 두 다운로드 href가 같았다. .media-item의 문헌 번호가 포함된 파일만 파싱하고 URL로 중복을 제거한다. 옆의 /Xplorehelp/Help_Multimedia.html은 일반 도움말이라 제외한다. 원 설명과 파일명은 native_index에 보존한다.

새 SDK stdio의 data/validation/20260910T124350Z-ieee-media-tab-mcp.json은 completed=true다. BioLSTM_RA-L_video.mp4 40381857바이트를 10개의 HTTP 구간으로 회수했고 Last-Modified 검증자·구간 위치·총 크기와 MP4 컨테이너를 대조했다. 같은 문헌의 참고문헌 30개도 확보됐다. 동영상 의미 판독은 수행하지 않았다. 새 Media 탭 파싱 검사와 기존 그래픽 초록·구간·실패 보존 회귀를 포함한 공통 175개 검사가 통과했다. 다른 Media 탭 파일 형식의 실제 성공으로 확대하지 않는다.


Nature의 명시적 fulltext_html 요청은 기존 실제 MCP에서 invalid_parts였다. 관측된 c-article-body/main-content 영역, 원 TeX 표현, 문헌 DOI에 묶인 MediaObjects의 PNG/JPEG 그림을 회수하도록 추가했다. 추천 문헌 위젯을 제외하고 초록만 있는 화면을 전문으로 표시하지 않는다. 그림 요청 실패 때 HTML과 각 오류를 보존한다. 그림 src는 저장된 artifact ref이며 일반 브라우저용 독립 웹페이지 렌더링을 검증한 것은 아니다.

새 SDK stdio data/validation/20260910T125713Z-nature-html-mcp.json은 completed=true다. The complexity of NISQ의 HTML 151275바이트·TeX 두 항목·PNG 그림 56058바이트(685×220)와 실제 ImageContent 한 개를 확인했다. 기계적 PNG 검사만 수행했고 이미지 의미 판독·MathJax 실행은 추가하지 않았다. 이 경로는 현재 관측된 Nature 레이아웃이며 다른 Springer 문헌 전체의 성공으로 확대하지 않는다. 원 fixture·초록 전용·그림 실패 검사와 공통 178개 검사가 통과했다.

CORE와 Semantic Scholar의 후속 새 SDK stdio 재검증도 각각 data/validation/20260910T125019Z-core-public-mcp.json, data/validation/20260910T125018Z-semantic-scholar-mcp.json에 보존했다. 두 경로 모두 첫 실제 요청에서 rate_limited였고 completed=false다. 추가 API 자격을 사용하지 않았으며 반복 후속 요청을 하지 않았다.


DBLP의 기본 검색 API와 Trier·Dagstuhl 미러는 익명 요청에서 모두 HTTP 200의 HTML 접근 확인을 반환했다. [운영기관의 공개 SPARQL 안내](https://www.dagstuhl.de/en/dblp/news/2024/introducing-our-public-sparql-query-service)와 [현행 KG 사용법](https://github.com/dblp/kg/wiki/dblp-KG-Tutorial)을 확인하고 sparql.dblp.org/sparql에서 실제 무자격 서지 응답을 받았다. 이 질의 문법은 기존 DBLP 검색과 다르므로 dblp-kg로 명시적으로 선택한다. 기존 경로의 자동 실패 대체는 하지 않는다. SPARQL SELECT를 RDFLib 구문 구조로 검증하며 SERVICE·FROM과 최상위 LIMIT/OFFSET을 거부한다. 하위 SELECT 범위와 문자열·주석은 보존한다. 서버에서 RDF 질의를 실행하거나 외부 RDF를 로딩하지 않는다.

첫 실제 MCP data/validation/20260910T132325Z-dblp-kg-mcp.json은 검색·native JSON/CSV/TSV·key 조회 후 DOI not_found로 미완료였다. 원 문헌 statement의 DOI는 10.1006/JCSS.1997.1494였다. 대소문자를 구별하지 않는 DOI 조회·대조로 수리한 새 data/validation/20260910T132715Z-dblp-kg-mcp.json은 completed=true다. 앞 4건과 start1/limit2 대조, 원 세 형식, key·DOI의 32 statements, 이름 후보와 SERVICE 거절을 확인했다. 원 RDF 값의 대소문자·datatype·xml:lang·미결합 변수를 유지한다. 전체 검색 건수를 세지 않아 total=null이며 provider_result_size를 전역 수로 해석하지 않는다.

직접 어댑터 data/validation/20260910T132945Z-dblp-kg-terms.json에서는 원 JSON의 xsd:gYear 1997이 TSV에서 정수 표기로 바뀌었다. 이 파일을 고쳐 쓰지 않고 partial과 source_export로 보존한다. 당시 오류 코드는 export_range_mismatch였으며 현재는 export_term_mismatch로 구별한다. 원 fixture로 같은 불일치를 검증했다. data/validation/20260910T133158Z-dblp-kg-extra-terms.json은 저자 수·언어 표지와 개행/따옴표·미결합 변수·빈 결과를 직접 검증해 completed=true다. 이 직접 어댑터 검사를 MCP 검증으로 확대하지 않는다. RDFLib 7.6.0·pyparsing 3.3.2를 고정했고 공통 186개 검사와 pip check를 통과했다.

APS 원 인용문 조사에서 최초 직접 요청은 www.aps.org 바로가기 origin에 저널 경로를 붙여 잘못된 호스트에 요청했으므로 유효한 인용문 검증에서 제외했다. 이후 KUDOS를 통해 journals.aps.org로 진입한 뒤 이전 원 Download Citation 링크 /prl/export/10.1103/PhysRevLett.89.190402의 BibTeX를 요청했지만 HTTP 403이었다. 보호된 관측은 .credentials/scholarly-mcp/probes/20260910T130807Z-aps-citation-failure.html이다. 이 경로의 native citation 구현·실측 완료로 세지 않는다.


JSTOR의 [공식 내보내기 안내](https://support.jstor.org/hc/en-us/articles/115004871747-Citation-Management-Exporting-Citations-from-JSTOR)와 실제 공개 응답을 대조했다. citation/text/345683은 text/plain 1308바이트의 BibTeX이며 citation/bibtex 경로는 404였다. 실제 작동하는 Text file 경로를 연결하고 원 바이트를 application/x-bibtex로 보존하며 원 MIME도 기록한다. DOI 필드는 없었으나 url이 요청 문헌의 stable ID를 식별했다. jj.8306294는 원 RIS가 BOOK을 반환하지만 기존 식별자 검증이 거부하던 현행 도서 ID였다.

새 SDK stdio data/validation/20260910T223621032180Z-jstor-workflow.json은 completed=true다. 문헌 345683의 서지·초록·원 RIS·BibTeX, jj.8306294 도서의 서지·두 인용문을 회수·추출했다. 원 제공자 안내문과 도서 유형·필드를 유지한다. 추가 형식 실패·다른 문헌 반환을 검사해 먼저 받은 서지/RIS 및 잘못된 원 export의 source_export를 보존했다. JSTOR 신규 회귀 4개가 통과했다. 검색·전문 회수는 이 성공 범위에 포함하지 않는다.


MathSciNet의 mr:(2733384) 검색은 검색 API 한 건을 받은 뒤 문헌 화면으로 자동 이동했다. 기존 결과 목록·checkbox 내보내기는 source_timeout이었다. 실패 보고 data/validation/20260910T224121Z-mathscinet-lookup-probe.json을 보존했다. 문헌 Cite의 원 publications/format 응답은 paperId별 ams/bib/tex/end 문자열 배열이었다. 같은 기관 Playwright context에서 이 원 형식 응답을 회수하고 요청 MR 집합·중복 및 BibTeX MRNUMBER·EndNote label을 대조한다. 문자열을 다시 작성하지 않고 빈 줄로 연결하며 제공자 배열 순서와 요청 순서를 따로 기록한다.

새 SDK stdio data/validation/20260910T225607960428Z-mathscinet-workflow.json은 completed=true다. 제목 검색 5건, MR2733384 네 인용문 형식·3쪽 Review PDF, MR 단건 검색 내보내기, 이름 후보 14건, Natural Proofs DOI 10.1006/jcss.1997.1494를 통한 MR1473047 조회·내보내기를 확인했다. DOI는 원 BibTeX를 대조한 뒤 따라가며 이름과 미확인 DOI는 후보로 남긴다. 이 보고는 인용문 내부 MR 대조를 추가한 뒤의 검사다. 공통 196개 검사가 통과했다.


ECCC 이름 입력을 원 일반 검색 후보로 연결했다. data/validation/20260910T230446363549Z-eccc-workflow.json은 새 SDK stdio에서 completed=true다. natural proofs 후보 20건·검색 2건 추출·TR26-008r1의 서지·초록·PDF와 판본 번호를 확인했다. 이름을 정확한 제목·판본으로 자동 확정하지 않고 잘못된 보고서 번호도 이름으로 바꾸지 않는다. 공통 198개 검사가 통과했다. 없는 보고서의 HTTP 200/404 제목은 기존 처리 대상이며 새 결함으로 보고하지 않았다.

JSTOR 배포 query-builder의 new-search 경로를 기관 프록시로 확인했으나 Client Challenge·capInput이 나타났다. 보호된 원 관측은 .credentials/scholarly-mcp/probes/20260910T225843Z-jstor-new-search.html이다. JSON 한 건의 path/resolutionTrace는 결과 목록이 아니어서 검색 성공으로 세지 않았다.


Software Heritage의 [공식 SWHID 설명](https://docs.softwareheritage.org/devel/swh-model/persistent-identifiers.html)을 대조했다. 기존 fetch는 qualifiers를 받아 놓고 버렸으며 원 바이트의 고유 해시도 검사하지 않았다. 공식 content 예 4d99d2d18326621ccdd70f5ea66c2e2ac236ad8b의 metadata와 파일 527바이트·27줄을 익명 API로 확보했다. 전체 바이트의 길이·Git blob SHA-1과 제공된 체크섬을 검사하고 원 API MIME도 보존한다. origin 문맥은 해독·정제하고 path는 이스케이프된 표기를 유지하며 외부 원 저장소를 방문하지 않는다.

처음 SDK data/validation/20260910T231934Z-swh-content-mcp.json은 조각 회수 뒤 전체 content의 octet-stream 추출에서 실패해 미완료다. UTF-8/NUL 없는 텍스트를 읽을 수 있게 한 뒤 data/validation/20260910T232052Z-swh-content-mcp.json은 completed=true다. 9~15행을 전체 파일과 대조했고 SWHID URL의 한 줄 선택·범위 초과·실제 0바이트 파일을 확인했다. 손상 바이트·metadata 불일치·403·잘못된/중복 qualifier·인코딩된 origin 정제와 범위 초과 회귀를 포함한 공통 204개 검사가 통과했다. integrity는 전체 content에 대한 것이며 조각이 부모 SWHID의 해시를 가진다고 표시하지 않는다. context_verified=false로 문맥의 미검증을 구별한다.


2026-09-11 Software Heritage의 [Vault flat API](https://docs.softwareheritage.org/devel/swh-web/uri-scheme-api-vault.html)를 연결했다. 실제 SDK stdio `data/validation/20260910T234218Z-swh-vault-mcp.json`은 빈 디렉터리 155바이트, 디렉터리 01d2169c88d0783182b1b7facffa522ba09b5957의 압축본 218076바이트·69파일·16디렉터리와 revision 2db189928c94d62a3b4757b3eec68f0a4d4113f0의 선택 관계를 확인했다. 내부 simplefarm.ml 27줄은 별도 content SWHID 회수와 같았다. 파일 내용·이름·권한·링크를 Git 트리 방식으로 다시 해시했으며 파일을 실행하지 않았다. 앞선 20260910T234131Z 보고는 검사 코드가 압축 선택 뒤 반환된 파일 참조를 다시 extract하지 않아 실패한 기록이다.

Tools 디렉터리 93ea4d40f1ace5b45af5a4a65993a87ad6e900d1의 준비 전 GET은 404였고, `data/validation/20260910T234346Z-swh-prepare-mcp.json`은 익명 생성 요청 뒤 pending 세 번과 네 번째 available·트리 해시 일치로 completed=true다. 이메일이나 별도 API 자격을 사용하지 않았다. 새 실제 다운로드 호스트는 SWH Vault의 Azure 컨테이너로 한정했다. Azure URL의 sig와 경로 안 중첩 URL을 정제하고 동명 공개 RDF 변수를 보존하는 회귀를 추가했다. 공통 검사 212개가 통과했다. Git 전체 이력·release·snapshot 아카이브는 미연결로 남는다.


2026-09-11 AMS의 AND/OR 중첩 그룹과 필드별 조건을 연결했다. 원 AdvancedSearch HTML·advancedSearch.js와 공식 jQuery 3.7.1로 외부 통신 없는 재현을 수행했다. 이것은 실제 검색·현재 서비스 환경과 다르다. `data/validation/20260910T235329Z-ams-dynamic-offline.json`은 원 제출 키 dynamicAdvancedSearch와 예상 키가 달라 실패했고, `20260910T235527Z-ams-dynamic-offline.json`은 원 조건 복원과 이중 인코딩 POST가 입력과 같았다. 같은 ID의 Delete/Search 중 정확한 Search를 선택하도록 고쳤다. 동적 페이지 전환은 원 함수로 연결했으나 실제 순회는 미검증이다.

실제 SDK `data/validation/20260910T234814714383Z-ams-workflow.json`과 `20260910T235700Z-ams-expression-mcp.json`은 모두 restricted/publisher_access_challenge이며 completed=false다. www.ams.org/AdvancedSearch의 별도 404는 현재 pubs.ams.org 고급검색 결과가 아니다. ScienceDirect의 원 홈페이지 폼은 결과 요청이 관측되지 않았고 /search 심층 링크는 CPE00001이었다. 공통 검사 214개가 통과했으며 AMS 원 파일 export와 실제 동적 검색은 완료로 세지 않는다.


2026-09-11 일곱 자료원을 직접 재검증했다. IEEE는 프록시 진입 실패 뒤 다시 정상 진입했고 실제 내보내기 결함 둘을 찾았다. Citations 모달이 다운로드 후 남아 다음 호출을 막았으며, CSV 요청은 이전 Plain Text 선택을 이어받았다. 남은 모달만 닫고 CSV의 Results 탭을 지정했다. 20260911T011646Z·012006Z-ieee-native-export-probe.json은 이 실패를, 013009Z 보고는 네 형식의 실제 성공을 보존한다. 새 형식·건수 검사와 실패 시 검색 레코드 보존도 추가했다.

`data/validation/20260911T015517Z-ieee-exports-mcp.json`은 completed=true다. 문헌 10488889의 네 형식과 DOI를 대조하고, complexity 검색의 첫 1건·두 번째부터 2건의 CSV를 원 검색 레코드 DOI 배열과 비교했다. 앞선 013544Z 보고는 시간 초과, 014608Z는 프록시 진입 실패였다. 015139Z는 총 1건인 P versus NP 제목 검색에서 start=1을 요청해 올바른 빈 결과를 받았으므로 다건 범위의 양성 시험으로 세지 않았다. 직접 어댑터의 다섯 연속 검색은 014306Z-ieee-repeat-search.json에서 통과했다.

AMS 한국어 확인 화면의 실제 DOM 일부로 기존 분류 실패를 재현하고 AMS 및 공통 Publisher 조회에서 restricted로 구별하도록 고쳤다. `20260911T013103Z-ams-challenge-lifecycle.json`과 `012311Z-siam-challenge-lifecycle.json`은 90초까지 결과 화면으로 전환되지 않았다. SIAM 홈페이지 검색도 같은 상태였다. IOP의 `011850Z-iop-firefox-recovery.json`은 정상 문헌 화면, `013757Z-iop-chromium-recovery.json`은 Radware/hCaptcha 진입 제한이다. ScienceDirect의 `012543Z-science-direct-chromium-recovery.json`은 CPE00001이다. JSTOR 문자 확인은 입력 후에도 통과하지 못했다. 이 관측은 접근 실패를 서비스 기능 부재로 해석하는 근거가 아니다.

APS는 문헌에서 모달을 열고 중복 쿠키 조작을 제거한 뒤에도 원 파일 GET이 403이었다. `20260911T013858Z-aps-native-download.json`의 실제 다운로드 클릭도 403이다. 반면 `014507Z-aps-firefox-recovery.json`의 기관 algebra 검색은 37987건 중 20건을 반환했다. 새 검색 구현은 후속 작업이며 이 관측만으로 어댑터 완료를 주장하지 않는다. 공통 검사 218개가 통과했다.


2026-09-11 APS 기관 검색을 연결했다. `data/validation/20260911T021223Z-aps-search-mcp.json`은 algebra 37987건 중 요청한 첫2건과 CSV의 DOI 배열 일치를 확인했다. 원 HTTP HTML에는 MathML22개와 lazy0개가 있었으며, 늦은 DOM에는 숨은 초록 수식이 빈 자리로 바뀌었다. 원 응답을 파싱하고 원 카드·MathML fixture로 회귀 검사했다. 표시 저자·서지·발행일을 별도 문자열 필드로 제공한다.

같은 조건의 후속 범위는 최근 원 페이지와 evidence 수신 시점을 재사용한다. `20260911T021913Z-aps-search-mcp.json`은 start19/limit2에서 1건을 보존한 partial이다. 원 Next의 화면 내부 요청은 HTTP403이었고, `023237Z`·`024034Z` 보고에서도 연속 페이지·추가 조건·선택 문헌 조회는 미완료다. 전체 completed를 true로 바꾸지 않았다.

별도 기관 진입으로 원 Next 주소를 열면 페이지2의20건·start20·total37987을 확인했다. 보호된 `20260911T023101Z-aps-exact-next-deep.html`이 정확한 원 쿼리를 사용한 기록이다. 문서 탐색으로 연결한 뒤에도 같은 세션의 연속 호출은 제한되어, 이 독립 성공을 워크플로 성공으로 확대하지 않는다. `20260911T023616Z-aps-same-context-deep.json`은 선택 문헌의 공개 주소와 후속 페이지의 같은 세션 실패를 보존한다. 공통 검사222개가 통과했다.

SIAM은 최소화한 일반 표시 모드 Chrome에서도 접근 확인이었다. `20260911T022325Z-siam-chromium-recovery.json`을 보존했다. IOP 진단에서는 한국어 iframe 제목 때문에 영어 제목 선택자가 실패했음을 확인하고 실제 위젯 속성으로 교정했다. 이 관측은 원문이나 인용문 회수 성공이 아니다.


2026-09-11 IOP의 표시된 접근 확인을 현재 세션에서 판독·입력하여 통과했다. 보호된 쿠키 상태를 저장한 Chrome에서 `data/validation/20260911T030426Z-iop-verified-session-fetch.json`은 서지·초록·16쪽 PDF·RIS를 회수했다. BibTeX 오류는 원 키 J Batina_2001의 공백을 엄격 파서가 거부한 것이었다. 원 키·바이트를 유지하는 경고 방식의 추출 옵션을 추가했으며 연구 parser의 엄격한 기본 동작은 유지한다. IOP 파싱·DOI 오류 때 받은 파일도 source_export에 보존한다.

`data/validation/20260911T032405640853Z-iop-workflow.json`은 실제 SDK의 서지·초록·16쪽 PDF·BibTeX·RIS 회수와 DOI 추출을 completed=true로 통과했다. 별도 기계적 추출에서 PDF 첫 페이지의 제목 구절도 대조했다. 파일의 키 공백 경고를 확인했고 공통224검사·연구 parser15검사가 통과했다. IOP는 이 확인 상태를 검증한 Chrome gateway에 연결했다. 검증을 서버의 CAPTCHA 자동 인식 기능으로 표현하지 않는다.

IOP 홈페이지의 Search 버튼으로 메뉴를 열고 complexity를 검색하면 /nsearch 결과가 나왔다. 원 화면은 상위500건 중1-10건을 표시했고 문헌 카드10개에 기사 링크20개가 있었다. 전체 일치 건수와 노출 상한, 문헌 수와 링크 수를 구별한다. 검색·RSS·필터의 생산 구현은 후속 작업이다.


2026-09-11 IOP 검색을 연결했다. 최신순 RSS API는 원 HTML의500건 상한 뒤에도 자료를 반환한다. 관련도·오래된 순 요청은 RSS가 무시하므로 원 검색 경로로 고정한다. 저널·문헌 유형·공개 접근 조건, 페이지 크기와 기간은 원 필드값을 유지한다. 검색 API가 실패했다고 HTML로 자동 전환하지 않는다. 익명 RSS의 XML200과 후속 접근 확인을 모두 관측했고, 생산 API 요청은 승인된 KUDOS 기관 프록시 세션을 사용한다.

원 RSS의 rdf:Seq는 빈 rdf:li들로만 구성됐다. 참조가 전부 비어 있고 항목 수가 같은 경우만 원 item 순서를 유지하고 경고를 남긴다. API의 페이지2·pageLength20·페이지51·저널 조건은 `20260911T042252Z-iop-rss-parameters.json`·`043051Z-iop-rss-parameters.json`에서 대조했다. 이 API에 웹 노출 상한500을 적용하지 않는다.

`data/validation/20260911T050214Z-iop-search-mcp.json`은 completed=true다. API 페이지 경계와 start500 이후2건, 관련도 페이지 경계·CSV·저널1742-6596/문헌 유형article/공개 접근/oldest 조건, 원 웹 상한 초과와 실제0건을 확인했다. `045825Z`의0건 필터 대조 실패는 원 화면이 체크박스 대신 숨은 기간 값을 제공한 사례이며 수정 후 통과했다. 이름은 관련도5후보 중 대상 DOI가 첫 결과였고 `iop-name-relevance.json`에 직접 어댑터 관측을 남겼다.

갱신된 브라우저 상태를 엔진별 보호 파일로 저장하고 최초에만 기존 kudos.json으로 시작한다. 엔진 간 비혼입·갱신 상태 저장·읽기 경로 검사를 추가했다. 재확인 성공은 `20260911T041819Z-iop-verification-control.json`에 있다. 공통234검사가 통과했다. 이 관측은 향후 인증 조건이나 모든 검색 조건 조합의 성공 보장이 아니다.


JSTOR는 Chrome의 원 음성 확인 파일도 회수했다. `data/validation/20260911-jstor-audio-diagnostic.json`은 WAV106312바이트·13.2835초, 현재 모델의 audio 입력 미지원, 로컬 PocketSphinx 인식에서 신뢰할 정답을 확인하지 못한 상태를 기록한다. 실제 키보드 입력 뒤에도 Client Challenge였다. 음성 회수를 웹 접근 통과로 세지 않으며, 별도 진단 환경의 인식기를 MCP 본체에 추가하지 않았다.


2026-09-12 IOP 보충자료 진단 URL에서 서명은 제거됐지만 AWS 자격 쿼리 값이 남아 사용자에게 알렸다. 딕셔너리 정제와 URL 정제가 서로 다른 필드 목록을 사용한 결함이며 URL도 기존 secret_fields를 적용하도록 수정했다. URL·산문·HTML·중첩 경로·fragment의 실패 재현 뒤 공통235검사를 통과했다. `data/validation/20260912-iop-signed-url-sanitization.json`은 실제 원 링크1건의 자격 필드가 정제 후0개이고 서명도0개임을 값 출력 없이 대조한 기록이다. 이미 표시된 출력 삭제·원 URL 무효화·전체 과거 산출물 감사는 미확인이다.


2026-09-12 IOP의 [Mastering data complexity beyond traditional computation](https://iopscience.iop.org/article/10.1088/1367-2630/add557)을 기관 경로에서 확보했다. 접근 확인 성공은 `data/validation/20260912T031727Z-iop-verification-control.json`이며 본문·보충자료 원 관측은 `032001Z`·`032112Z-iop-chromium-recovery.json`이다. 원 본문 영역·수식·그림·보충 탭을 연결했다. data-src에 있던 실제 주소를 처리하고 그림5개를 회수했다. 본문에는 TeX154개가 있으며 수식 이미지 파일 자체의 다운로드와 구별한다.

`20260912T032900Z-iop-content-mcp.json`의 첫 실제 호출은 본문과 그림 성공, 보충 파일 connection_error로 partial이었다. `033040Z-iop-attachment-probe.json`은 원 프록시 호스트의 최대 DNS 레이블65자·연결 실패와 같은 서명·경로의 원 IOP 저장소 호스트에서 PDF250714바이트·2쪽 성공을 대조했다. 확인한 저장소 하나에 한해 원 호스트로 복원한다. API 실패에 따른 브라우저 전환이나 다른 자료원 탐색은 없다.

`033208Z-iop-content-mcp.json`은 모든 회수·추출에 성공했으나 검사자가 추정한 Supplementary 문자열이 실제 제목의 Supplements와 달라 completed=false였다. PDF 첫 페이지의 실제 제목으로 대조한 `data/validation/20260912T033324Z-iop-content-mcp.json`은 completed=true다. 원 TeX 선택·그림 ImageContent·보충 PDF 첫 페이지 제목과2쪽을 확인했다. 다른 DOI의 보충 페이지를 거부하고 초록만 있는 페이지를 본문으로 세지 않는 검사까지 공통238검사를 통과했다. 이 표본에서 본문 XML 다운로드 제어는 발견하지 못했으며 XML 회수는 미연결이다.


2026-09-12 Software Heritage의 릴리스 대상 회수를 연결했다. [공식 보존 자료 구조](https://docs.softwareheritage.org/devel/swh-deposit/specs/spec-loading.html)와 [Vault](https://docs.softwareheritage.org/devel/swh-web/uri-scheme-api-vault.html)를 대조하고, 실제 directory/revision 대상 metadata를 확보했다. `data/validation/20260912T035041Z-swh-release-mcp.json`은 release22ece559cc7cc2364edc5e5593d63ae8bd229f9f에서 revision e9c6243371087d04848b7686888f6dd29dfaef0e를 거쳐 directory a8eded6a2d062c998ba2dcc3dcb0ce68a4e15a58의 원 압축본86943878바이트·파일1666개·디렉터리139개를 실제 MCP로 회수하고 트리 해시와 압축 항목 추출을 completed=true로 통과했다.

직접 directory를 가리키는 release fc8e44c5bb3fabe81e5ebe46ac013a2510271616은 실제 대상 관계와 Vault 준비 요청을 확인했지만 `034324Z`·`034916Z-swh-release-mcp.json`에서 각20회 조회 동안 pending이었다. 이 표본의 회수 완료는 주장하지 않는다. 순환 릴리스·다른 revision ID·원 metadata 보존 검사를 포함한 공통240검사가 통과했다. 연쇄 release와 content 대상은 코드·검사 범위와 실제 회수 범위를 구별하며, Git 전체 이력·snapshot 압축은 미연결이다.


2026-09-12 JSTOR의 실제 표시 문자 확인을 판독·입력해 통과했다. /new-search는 그 뒤404였고 정식 /action/doBasicSearch의 `data/validation/20260912T034048Z-jstor-search-observe.json`은 원 결과25건과 JSON을 확보했다. [공식 필드 검색 설명](https://support.jstor.org/hc/en-us/articles/115004732567-Searching-Using-Fields-and-Advanced-Search)과 [필터 설명](https://support.jstor.org/hc/en-us/articles/4405598751255-Searching-Using-Filters-and-Facets)을 대조했다. 익명 API 요청은200의 확인 HTML이었으나 기관 세션의 원 JSON POST는 성공했다. API 자격·연락 이메일을 요구하지 않고 API 실패로 브라우저 검색에 전환하지 않는다.

`034641Z-jstor-api-probe.json`에서 pageNumber만2로 바꾸면 첫 페이지가 반복됐다. `035000Z-jstor-controls.json`의 실제 Next는 pageParams의 groupEfq·pageMark를 함께 보냈다. 원 문헌 결과군197779건과 이미지 포함 전체198021건을 구별했다. `035445Z-jstor-controls.json`의 저널·2020~2025 조건은7837건이다. appliedFacets만으로는 유형 조건이 적용되지 않았고 실제 msFacetFields를 연결했다. 이미지 조건은242건의 별도 결과군을 반환했다.

`data/validation/20260912T041802Z-jstor-search-mcp.json`은 completed=true다. 문헌과 이미지의 페이지 경계·CSV 배열·기간/저널·필드 검색9건과 RIS·전체 접근 범위·실제0건·oldest/수학/영어 조건95971건·이름 후보·비2307 DOI 내보내기를 실제 MCP로 확인했다. 앞선 `041512Z`는 영어 언어 코드 eng OR en OR EN이 원 선택 표시에서 eng OR en으로 줄어 false mismatch였고 미완료로 보존한다. 언어 코드 대소문자 중복을 비교할 때만 정규화하고 원 데이터와 연구 검색식은 유지한다.

JSTOR 문헌24931626의 첫 Download는 이용 조건 모달 때문에 대기했다. 원 Accept and download 후 `040328Z-jstor-download-probe.json`은 PDF2651715바이트·11쪽을 확보했다. production의 다운로드 이벤트 등록에 내장 list.append를 넘기면 Playwright가 AttributeError를 내는 것을 로컬 브라우저에서도 재현하고 함수로 감쌌다. `data/validation/20260912T041112Z-jstor-document-mcp.json`은 metadata·RIS/BibTeX·11쪽 PDF와 첫 쪽 stable ID·두 번째 쪽 제목을 completed=true로 통과했다. 문헌 화면의 본문10쪽과 내려받은 전체11쪽을 혼동하지 않는다. 첫 `040543Z`의 미구현과 `040627Z`의 부분 결과도 보존한다. 공통248검사가 통과했다. PDF 외 원 파일·추가 첨부·복수 결과군·BCE 날짜와 모든 조건 조합의 검증은 미완료다.


2026-09-12 후속 재검증에서 `data/validation/20260912-jstor-guide-workflow.json`은 describe_source가 반환한 첫 예제를 그대로 호출해2건·ok로 completed=true였다. AMS의 `20260912T042311Z-ams-api-recheck.json`은 원 /product/browseproducts 요청을 기관·공개 주소에서 각각403으로 확인했다. APS의 `042406Z-aps-firefox-recovery.json`은 /search?q=algebra&page=2도 확인 화면이었다. 기존 성공 범위와 후속 실패를 구별한다.

`data/validation/20260912T043004Z-core-public-mcp.json`은 이름 후보, works340524929의 metadata·abstract, 원 fullText 접근 안내문의 restricted 구별을 실제 MCP에서 completed=true로 통과했다. 본문 자체를 회수했다는 뜻은 아니다. 같은 시각의 semantic-scholar-mcp.json은 rate_limited로 completed=false였다. `043051828874Z-dblp-workflow.json`은 access_challenge이며, `043051Z-dblp-alternate-hosts.json`의 dblp.uni-trier.de와 www.dblp.org도200의 HTML 확인 응답으로 JSON 검색을 제공하지 않았다. 전체 구현은 계속 부분 완료다.


2026-09-12 Software Heritage의 [원 Git 보관 형식](https://docs.softwareheritage.org/devel/swh-web/uri-scheme-api-vault.html)과 [snapshot 해시 규격](https://docs.softwareheritage.org/devel/apidoc/swh.model.git_objects.html)을 대조했다. history 항목과 snapshot의 원 압축 회수를 연결했다. `data/validation/20260912T053018Z-swh-git-mcp.json`은 revision2db189928c94d62a3b4757b3eec68f0a4d4113f0의337920바이트·349객체·55커밋과 snapshot2611ba3c6ee63b2078ac02e597ee0e40df930a66의870400바이트·1084객체·296커밋·175브랜치(HEAD 포함)를 실제 MCP로 검증했다. 객체 해시·연결 관계·snapshot manifest 해시·refs 대응과 압축 항목 추출이 completed=true다.

`053213Z-swh-git-mcp.json`은 빈 directory의 Git 형식을 회수했지만 release의 원 tag에 missingEmail이 있어 Git 형식 검사에서 실패했다. 원 바이트를 보존하고 해당 형식 경고만 낮춘 뒤 `053701Z-swh-git-mcp.json`에서 releasefc8e44c5bb3fabe81e5ebe46ac013a2510271616의 Git 압축 회수가 completed=true였다. 해시·객체 연결 검사는 유지한다. 앞선 대기는 MCP 자체가 아니라 Git 검증 하위 프로세스의 파이프 종료 대기였으며, 표준입력과 창 생성을 분리한 새 SDK 호출로 해소했다. 기존 클라이언트·등록 MCP는 재시작하지 않았다. 원 Git config·hooks·외부 objects 참조를 적재하지 않고 소스 코드를 실행하지 않는다. 경로 이탈·pack 손상·누락 snapshot·원 형식 경고 검사를 포함해 공통257검사가 통과했다. 직접 directory 대상 release의 flat 작업 대기와 Git 형식 성공은 구별한다.


2026-09-12 JSTOR의 갱신된 접근 확인에서 두 번의 입력 실패 뒤 현재 표시된 다른 과제를 판독·입력해 정상 검색25건에 도달했다. 보호된 원 관측은 `20260912T051530Z-jstor-after-challenge.html`이며 엔진별 상태를 저장했다. 원 발췌문 API·BCE 입력·혼합 결과군을 조사한 정제 보고는 `data/validation/20260912T051726Z-jstor-remaining-probe.json`과 `052118Z-jstor-bce-mixed.json`이다. 원 화면의 BCE 0500~0100은 -500~-100으로 제출돼14936건을 반환했다. 발췌문은 검색 결과와 다른 순서로 오며 숫자 stable ID를10.2307 DOI로 반환하므로 식별자를 대조해 연결한다.

혼합 검색의 carousel5건 다음 표식을 그대로 사용하면 전체 이미지 결과와 중복이 생겼다. `053615Z-jstor-group-order.json`은 원 이미지 결과군을 처음부터 펼친25건과 다음25건의 중복0건을 확인했다. 그 경로로 각 결과군의 start/limit를 적용하며 처음의 미리보기 원 응답도 evidence로 유지한다. group_efq의 유형 배열 순서는 바뀔 수 있어 집합으로 비교하되 요청에는 원 표식을 그대로 사용한다.

`data/validation/20260912T053806Z-jstor-extended-mcp.json`은 원 발췌문2건·BCE14936건 중2건·journal과image 혼합178962건의각 start24/limit2·합계4건과 CSV ID 대조가 completed=true다. 앞선053213Z는 원 날짜 표기 B.C와BCE를 하나의 철자로 단언한 시험이 실패했으며 원 표기를 대조해 시험을 고쳤다. 공통257검사가 통과했다. 후속 이미지·음성·동영상 파일과 첨부 회수는 별도 작업으로 남긴다.


2026-09-12 [IOP의2026년7월 XML 공급 안내](https://ioppublishing.org/legal/textanddataminingpolicy/)를 확인했다. 현재 안내된 공급 방식은 출판사에 문헌·형식·사용 목적을 제출하고 검토를 받는 경로이며 XML의 일반 다운로드 제어는 앞선 문헌 표본에서 발견하지 못했다. 별도 연락·자격을 요구하는 경로를 사용하지 않는 사용자 결정에 따라 이 XML 공급 경로는 제외한다. 안내는 MCP 등 자동 접근에도 별도 서면 합의를 요구한다고 명시하며, 기관의 실제 합의 여부를 이번 기능 검증으로 확인한 것은 아니다. 추가 연락·신청은 하지 않았다.


2026-09-12 DBLP의 확인 응답은 [Anubis metarefresh](https://github.com/TecharoHQ/anubis/blob/main/docs/docs/admin/configuration/challenges/metarefresh.mdx)였다. Chromium의060822Z-dblp-verification.json은Access Denied였지만 HTTP 클라이언트에 제공된 원 확인은 JavaScript가 필요하지 않았다. `data/validation/20260912T063810Z-dblp-refresh.json`은 실제 Refresh 헤더가 지정한2초 대기, 확인302, 원 API JSON2건을 확인했다. 최초 별도 관측에서는 같은 지시가 meta 태그에 있었다. 두 형식을 같은 원 요청으로 처리한다.

`data/validation/20260912T064842387254Z-dblp-workflow.json`은 describe_source→P versus NP 검색49건 중2건→extract를 실제 MCP로 completed=true 통과했다. 확인 주소가 다른 호스트로 나가거나 검색식이 바뀌는 경우를 요청 전에 거부하고 일회성 확인 값이 artifact에 남지 않는 검사를 추가했다. 다른 Anubis 방식은 처리했다고 주장하지 않는다. 공통261검사가 통과했다. 원 서지 형식·이름 후보의 추가 구현과 검증은 이어서 수행한다.


2026-09-12 JSTOR의 [원 이미지 다운로드](https://support.jstor.org/hc/en-us/articles/4410046169751-Images-on-JSTOR-Getting-Started)를 확인했다. `data/validation/20260912T062834Z-jstor-image-mcp.json`은 community.13581670의 JPEG168854바이트·1024×821, 실제 ImageContent, community.39607963의 원 restricted 구별을 completed=true로 통과했다. `063140Z-jstor-document-mcp.json`은 기존 문헌24931626의11쪽 PDF 회귀도 통과했다. 구조용 #cdt는 비어 있는 div이므로 visible을 기다린060317Z 시험은 완료되지 않았고 attached로 읽도록 고쳤다.

`063423Z-jstor-extra-inventory.json`은 오디오와 동영상의 원 상태,26581894의 원 보충 링크를 찾았다. 오디오 원 요청은 /audio/download/UUID에서 허용된 Artstor 저장소로 이동했다.071522Z는 MP3·VTT·보충 PDF를 모두 회수했으나 보충 첫 쪽에 주 문헌 제목이 있을 것이라는 시험 전제가 틀렸다. 실제 보충본은34번 쪽에서 시작하며 ATHEY, TIBSHIRANI AND WAGER를 표시하는21쪽의 후속 부분이다. 초기 직접 파일 요청070854Z의45초 대기도 기록했다. 생산 경로는 원 Download로 고정하고 오디오는 선택된 UUID endpoint에서의 실제 redirect 연쇄를 대조한다.

`data/validation/20260912T074059Z-jstor-extras-mcp.json`은 MP3의24416379바이트, 자동 생성 WebVTT33159바이트의 줄 추출, 보충 PDF863887바이트·21쪽과 첫 쪽 저자 표시, 동영상 표본community.39197180의 원 disabled 구별과 전사문 회수를 completed=true로 통과했다. 문헌 파일과 첨부는 같은 원 페이지를 사용하며 원 byte·부모 문헌·파일 크기·transcript_type을 보존한다. 별도 공급자의 인식기를 실행하지 않는다. 이 작업트리의 공통267검사는 진행 중인 DBLP 원 문헌 검사3개도 포함한 수치다.


2026-09-12 DBLP의 conf/stoc/Cook71 원 문헌 페이지에서 내보내기 링크를 확인하고7개 형식을 회수했다. XML472·BibTeX778·RIS532·N-Triples6162·Turtle3287·RDF/XML4551·plain81바이트다. source key를 XML·BibTeX·RIS·RDF에서, 제목을 plain에서 대조한다. 이름은 후보 검색으로 반환하고 XML의 다른 key를 거부한다.

`data/validation/20260912T072659Z-dblp-documents-mcp.json`은 문헌 key 조회와7개 형식의 실제 extract, 이름 후보4건, P versus NP의start1/limit2와 원 RIS2개를 completed=true로 통과했다. Native N-Triples는 원 텍스트 줄로 추출하며 그래프 질의 기능을 추가한 것은 아니다. 손상된 BibTeX 식별자·XML 식별자 불일치·다른 export 보존 검사를 포함한 공통267검사가 통과했다. 별도 DOI 질의를 시도한 기록의0건을 해당 문헌의 DBLP 부재로 해석하지 않는다. Native key·문헌 URL·이름이 이 fetch의 입력 범위다.


2026-09-12 JSTOR 이미지 화면의5개 추가 정렬과 원 조건을 확인했다. `data/validation/20260912T082405Z-jstor-image-controls.json`은 제목·제작자 양방향과 해상도의 sort/sortOrder,10MP 초과 조건47건을 보존한다. 추가 facets는 원 field와 label을 받고 선택 상태를 대조한다. 제공기관은 label만 전송하면 조건이 무시돼242건 그대로였으며083058Z MCP는 이를 filter_mismatch로 거부했다.084340Z의 원 요청은 내부적으로 cc_portal_id#식별자를 사용했다. 하위 컬렉션은085108Z에서 접두사 없는 label로22건을 반환했다.

`data/validation/20260912T085459Z-jstor-image-search-mcp.json`은 이미지 정렬5개, 해상도47·Europe5·Northern State University26·하위 NSU Pasque Collection22건과 필요한 facet 추출을 completed=true로 통과했다. 제작자 표시는 creators에 보존한다. 표시 이름은 선택용이며 label의 내부 구성을 호출자가 만들지 않는다. 공통269검사가 통과했다.


2026-09-12 IOP의 문헌별 원 인용문을 검색 export에 연결했다. 첫090332Z-iop-search-citations-mcp.json은 접근 확인으로 제한됐다.090654Z-iop-verification-control.json은 현재 표시된 나무 제품 과제를 판독·선택해 확인 응답을 얻었지만 제출 후 동일 페이지의 URL 대기는 timeout이었다. 그 보고를 성공으로 고치지 않았다. 이후 `data/validation/20260912T091136Z-iop-search-citations-mcp.json`은 새 SDK에서 최신순 RSS의 BibTeX와 관련도 검색의 RIS, 각각 선택한1건과 실제 추출의 DOI add557을 completed=true로 통과했다. 원 파일 회수 성공은 이 별도 보고가 입증한다.

RSS의 페이지 경계에서 선택한2건 중 두 번째 인용문이 제한되는 재현으로 검색 레코드·첫 파일·오류가 함께 유지됨을 확인했다. 자료원이나 검색 방식을 바꾸지 않고 형식에 따라 원 문헌 내보내기를 연결한다. 공통270검사가 통과했다. IOP XML의 별도 연락·검토 공급 경로는 계속 제외한다.

2026-09-12 자료원별 창 모드와 접근 조건을 별도 조사했다. [접근 조건 기록](ACCESS-RESEARCH.md)에 통제 변수·기관 경로·후속 양성 근거와 비밀값 노출 사고·자동 삭제 거부의 처리 범위를 보존했다. 초기 `data/validation/access-research-20260912/mcp-before-integration.json`은 SIAM 검색과 individual-subscription 검색이 실제 SDK에서 각각 publisher_search_not_implemented와 adapter_not_implemented였음을 기록한다.

`data/validation/access-research-20260912/individual-subscription-mcp.json`은 새로운 SDK 서버에서 KNU 두 보유 목록95행을 검증했다. SIAM6건의 JSON·CSV 식별자, 행 fetch·extract, 개별전자저널36행 metadata와 fulltext not_offered, 2026년 조건1건, start35/limit3의 두 목록 경계, 0건과 외부 URL 거부가 completed=true다. 원 XLSX는 artifact에 저장하지 않는다. 실제 목록에 포함된 별도 ID/PW는 모든 workbook의 셀·하이퍼링크·주석을 내부에서 먼저 확인한 뒤 정제한다. 알려진 workbook 값2개를 실제 SDK 파일23개와 스테이징 파일에서 대조해 일치0건이었다. 이 검사는 임의의 모든 비밀 형식이나 과거 출력 삭제를 검증한 것이 아니다.

`data/validation/20260912T114646Z-siam-mcp.json`은 전용 Chrome 실행부를 연결한 실제 SDK에서 제목 algebra 검색1,320건 중2건과 CSV·extract를 대조했다. start19/limit2의 페이지 경계를 BibTeX·RIS·EndNote·Medlars·RefWorks 각각으로 조회해 페이지별 원 artifact2개와 실제 extract를 통과했다. 정확한 책 URL의 metadata·다섯 인용 형식과 DOI 대조, 0건 결과까지 completed=true다. RefWorks는 외부 폼을 제출하지 않고 SIAM 응답의 textarea RIS를 읽는다. 문헌 화면과 인용문의 쉼표 앞 공백 차이는 제한된 제목 비교 정규화로 처리하며 원 파일은 고치지 않는다.

SIAM 정상 책 페이지는 citation/DC title 없이 publication_doi·og:title·본문 h1을 제공했다. 공통 준비 검사가 이 페이지를 거절하는 실패를 재현한 뒤 해당 문헌 신호와 실제 본문 제목을 연결했다. OG title만 있는 페이지는 여전히 문헌으로 인정하지 않는다. 같은 페이지의 요청하지 않은 선택 DOI 해제, Article Medlars의 TI와 저널명 TA 분리, 빈 책 TI의 TA 제목 보완도 실물·회귀로 대조했다. 추가 Topic·발행물·날짜·다중 행의 연결은 별도 검증 단위로 진행한다.

`data/validation/20260912T121025Z-siam-advanced-mcp.json`은 추가 검색 조건의 실제 SDK 검증을 completed=true로 통과했다. Title algebra와 Author Stetter는17건, Anywhere polynomial을 더한 세 행은16건이었다. optimization·SIAM Journal on Optimization·현재 원 Year 조건은89건이며 start19/limit2에서 두 페이지의 Article 행과 발행물명을 대조했다. linear algebra·Linear Algebra and Matrix Theory·2024년1월부터2026년9월 조건은11건이며 결과 연도를 대조했다. 각 JSON·CSV의 DOI가 일치하고 모호한 publication=SIAM은 후보와 selection_required를 반환했다. 자동완성은 현재 선택 제어의 ID를 제출 URL과 대조하고 요청하지 않은 조건이 남으면 거부한다.

`data/validation/20260912T115954Z-aps-search-mcp.json`은 새 실행부에서 기관 검색37,997건 중2건·CSV와 원 레코드 추출·start19/limit2·제목 검색814건·선택 문헌 metadata와 abstract를 completed=true로 통과했다. 직전115721Z는 초록 selector가 원 #abstract-section-content를 찾지 못해 partial이었고 이 결함을 수정했다. 원 인용문과 추가 facet·날짜의 검증은 별도 단위다.

`data/validation/20260912T120447Z-ams-export-mcp.json`은 algebra 전체6,589건·선택1건·next1을 유지한 원 XLSX 회수와 실제 Products 시트 추출, 선택 ProductCode의 metadata·책 소개 회수를 completed=true로 통과했다. XLSX는 한 논리 상품·세 ISBN 변형 행과 제목 행을 포함해 extract total4였다. 기존 native는 원 JSON 페이지 의미를 유지하고 xlsx를 별도로 추가했다. 중첩 검색식120154Z는 원 서버 오류가 JSON 문자열 안에 반환돼 일반 AttributeError였으며 non-object 오류 분류를 수정한 뒤 원 제출 계약을 추가 조사하고 있다.

`data/validation/20260912T125646Z-ams-search-mcp.json`은 기본검색의13건 회수와 추출, start11/limit2의 원 페이지 경계와 앞 결과의 동일성, 실제0건을 completed=true로 통과했다. 직전124315Z의0건은 TotalRows=0, Products=null, PageNumber=1, RowsPerPage=12의 원 응답을 거절했다. 이 구조만 빈 결과로 읽고 원 JSON은 보존하도록 수정했으며, TotalRows>0인데 Products=null인 응답은 여전히 오류다. AMS 전용15검사가 통과했다.

동적식은 `data/access-research/ams-expression-summary.json`의 실제 수동 UI 단일조건과 같은 세션의 정상 기본검색으로 구별했다. scalar·sortBy는 같고 원 dynamic POST 자체가 product 객체 대신 내부 message 문자열을 반환했다. dynamicAdvancedSearch만 한 단계 덜 인코딩한 대조도 같았다. 복원 함수나 인코딩 깊이 하나의 오류로 판단하지 않고 현재 제공자의 동적 실행 오류로 기록한다. 다항·중첩식 수동 실행은 완료하지 못했으므로 그 범위까지 직접 검증했다고 쓰지 않는다.

전용 실행부의 추가 교차 검토에서 빈 환경 경로의 상대 Chrome 선택, KNU styled blank 행의 허위 레코드, 정확한 목록 fetch의 무관 목록 장애 의존, header-only workbook의 역전 좌표를 재현해 수정했다. 현재 원 목록에는 빈 행이 없어 실측95건은 변하지 않았다. `data/access-research/integration-review.md`가 재현·수리 후 검토 범위를 소유한다.

APS PDF의 HTTP 200 application/pdf 응답이 실제로는 Chrome 내장 viewer의536바이트 HTML이고 후속13,573바이트 HTML도 viewer embed인 것을 확인했다. 새로 만든 전용 프로필에 plugins.always_open_pdf_externally=true를 적용하자 원 제어에서2,382,611바이트·29쪽 PDF를 받았다. 같은 설정을 NativeChromeGateway에 반영했다. 기존 사용자 프로필이나 시스템 정책은 수정하지 않았다.

`data/access-research/siam-institutional.json`은 실제 KUDOS 로그인·학술DB·개별전자저널 목록에 기재된 SJDM의 원 popup_gourl과 libproxy 경로를 검증했다. 최종 공개 SIAM 저널 화면은 정상200이고 확인 화면이 없었다. 최신 비공개 논문10.1137/24M1711108은 제목·DOI가 일치했으나 기관 권한 표지가 없고 구매 안내를 표시했다. 원 PDF 제어는 같은 DOI 초록 화면으로302 복귀했으며 PDF embed·Playwright/CDP download가 모두0이었다. 이 관측은 기관 경로의 정상 연결과 해당 문헌 권한의 미확보를 구별하며 SIAM 전체 원문 부재로 확대하지 않는다.

새 PDF 설정으로 SIAM 명시 PDF의 Playwright 이벤트가 없고 CDP 이벤트만 시작되는 회귀도 재현했다. navigation 전에 CDP 이벤트를 관찰하고, navigation BrowserError 뒤에도 같은 host/path/query의 새 이벤트가 있을 때만 완료를 기다리도록 공통 explicit_pdf를 연결했다. 다음 event-loop tick의 callback도 최대10회·100ms로 관찰하며 끝내 일치 이벤트가 없으면 원 오류를 유지한다. `data/access-research/pdf-regression.json`은 최신 SIAM Front Matter284,966바이트·10쪽·첫 쪽 제목/추출을 통과했다. `data/validation/20260912T131217Z-ams-pdf-mcp.json`은 기존 AMS51쪽 명시 PDF·내장 metadata·extract 회귀를 completed=true로 통과했다.

`data/validation/20260912T130617Z-aps-extended-mcp.json`은 실제 SDK에서 algebra·journal=[prd,prl]·1960-01-01~1980-12-31 조건847건 중1건, 원 RIS·BibTeX, metadata·abstract와PDF14쪽·1,148,858바이트 및 각 extract를 completed=true로 통과했다. 복수 facet의 원 query는 journal[] 반복 필드이며 HTML 응답의 MathML과 실제 checked 상태를 구별해 대조한다. 사용자 입력 날짜는 YYYY-MM-DD를 엄격히 검사한다.

`data/validation/20260912T131701Z-aps-extended-mcp.json`은 supplement-only 범위다. 문헌10.1103/PhysRevLett.115.250402의 같은 DOI direct 제어에서 LHFSupplementary.pdf 1,884,893바이트·16쪽을 회수·extract하고 completed=true였다. 늦게 나타나는 제어는 supplementary 요청에 한해 최대10초 기다린다. 중복된 같은 URL을 제거하고 다른 DOI/host·landing 링크로 자동 이동하지 않는다. 제어가 없는 다른 표본은 source_page이며 사이트 전체의 부재로 표시하지 않는다.

`data/validation/20260912T134143Z-semantic-scholar-public-final.json`은 별도 새 SDK에서 initialize·describe를 통과했으나 첫 원격 검색이 rate_limited였다. 뒤의 원격 요청은0회이며 새 문헌·관계·인용문 흐름을 완료로 바꾸지 않는다. 별도의 `134214Z-software-heritage-public-final.json`은 직접 directory 대상 release의 metadata를 확보했지만 fulltext가 여전히 pending이었다. 준비 중인 파일을 반복 요청하거나 미확보 압축본의 무결성을 검증했다고 쓰지 않는다.

`data/validation/20260912T134822Z-github-mcp.json`은 일반 github 자료원에서 검색·원 JSON export·레코드 추출, 저장소 ZIP·내부 파일 추출, 같은 커밋의 개별 파일 회수를 completed=true로 통과했다. 작은 공개 검증 표본 octocat/Hello-World의 commit7fd1a60b01f91b314f59955a4e4d4e80d8edf11d에 고정한 ZIP387바이트와 README13바이트를 대조했고 압축 안 파일과 단건 파일의 추출 내용이 같았다. 소스 코드는 실행하지 않았다. 앞선134555Z는 검증 스크립트가 이 어댑터의 미지원 CSV를 요청했고134633Z는 압축 항목의 path를 name으로 읽어 실패했다. 스크립트를 실제 JSON·압축 반환 계약에 맞추고 사용 설명에 원 export 형식을 명시했다.

ScienceDirect의 `data/validation/20260912T141311Z-science-direct-extended-mcp.json`은 content 범위의 새 SDK다. 긴 제목으로 PII S156042922600065X 한 건을 검색해 RIS·BibTeX·plain의 각 원 파일과 추출을 대조했다. 같은 PII의 metadata·abstract·세 원 인용문과 PDF1,031,171바이트·31쪽을 회수하고 첫 두 쪽 DOI를 확인해 completed=true였다. 이전135804Z의 검색 준비 대기,140813Z의 단건 Export 제어 부재 판정은 실패 기록으로 남긴다. 원 화면의 `1 result found`를 파서가 거절하던 문제와 Export 버튼 자체·클릭 후 메뉴가 각각 늦게 나타나는 문제를 분리해 교정했다.

`data/validation/20260912T141127Z-science-direct-extended-mcp.json`은 facets 범위다. algebra·Research/Review·Mathematics·구독 저널·2020–2025년 조건33,229건 중2건의 JSON·CSV를 대조했고, Journal of Algebra의 현재 자동완성 cid272332·21,628건 중2건과 발행물명이 일치해 completed=true였다. 자동완성은 저널을 먼저 확정한 뒤 본 검색과 결합해 입력 갱신 충돌을 피한다. 별도 함수 실측에서 Show more로 펼친 후보는 논문 유형23·발행물25·주제10·언어9·공개접근1개였으며 처음 보이는 일부를 전체로 표시하지 않는다.

`data/validation/20260912T141704Z-science-direct-extended-mcp.json`은 supplementary 범위다. 원 문헌 S0167278924001155의 Appendix D·Video S1에 결속된 mmc1.mp4를 회수했다. MCP resources/read의1,315,119바이트와 MP4 ftyp를 대조해 completed=true였으며 동영상 의미를 분석하지 않았다. 원 제어에서 확인한 ars.els-cdn.com과 PDF 전송 호스트는 해당 자료원의 파일 다운로드에만 허용한다.

`data/validation/20260912T142839Z-science-direct-search-mcp.json`은 최신 코드에서 제목 Natural Proofs의2건·CSV, algebra start24/limit2의 두 원 페이지·각 RIS와 PII 추출,0건을 completed=true로 통과했다. 직전141842Z는 수식의 text node 경계가 만든 공백 차이를 원 제어의 문헌 불일치로 판단했다. 실제 같은 PII의 제목이 `W- algebras`와 `W-algebras`로 나타나는 것을 대조한 뒤 비교에서만 공백을 제외했다. 문자·기호·대소문자와 원 레코드·인용문 바이트는 보존하고 PII 제어·문헌 경로 검사를 유지한다. 비문자 field가 일반 TypeError로 끝나는 반례도 invalid_options로 교정했다. ScienceDirect 전용21검사가 통과했다.

MathSciNet의 실제 SDK 기록은 `data/access-research/mathscinet-citations/live-sdk.json`이다. MR2733384의 incoming3건에서 start1/limit2·BibTeX, 원 참고문헌48개 중44MR occurrence·42고유MR의 outgoing 검색에서 start4/limit2 두 페이지·EndNote와 추출, DOI 동일성 확인을 통과했다. 추가 MR0463157은 원 서지가 Algebraic geometry임을 확인하고 From Reviews 제어76과 실제 검색72를 각각 보존했다. 원 리뷰 검색식으로1건과 BibTeX를 회수·추출했으며 MR2733384의 리뷰0건은 검색식을 발명하지 않고 반환했다. 관련39검사가 통과했고 원 MR 없는 참고문헌은 별도 source_page에 남긴다.

`data/validation/20260912T141742Z-wos-citations-mcp.json`은 WOS:000269418800023·DOI10.1145/1562164.1562186의 실제 Citing Articles 원 요청과 부모 UT를 대조했다. 첫2건·plain/JSON 추출, DOI 기반 start124/limit2의 마지막1건, fetch의 outgoing CR·incoming 문헌 분리를 completed=true로 통과했다. 문헌 화면의136회와 기관 결과125건을 함께 보존한다. 직전141617Z는 늦은 Citations 제어의 준비 대기를 수리하기 전 실패 기록이다. 관련26검사가 통과했으며 WOS 정렬·facet·개별 edition은 별도로 계속 구현 중이다.

2026-09-12 위 구현을 공통 서버에 연결한 전체 오프라인·SDK 계약 검사378개가 통과했다. 첫 전체 실행에서 기존 explicit PDF 시험의 범용 MagicMock이 실제 KudosGateway에 없는 native_download까지 만들어 새로운 분기를 잘못 탔다. 대역을 실제 KudosGateway 인터페이스로 제한하고, 다른 자료원의 Playwright 다운로드를 읽거나 보존하지 않는 원 검증을 유지했다. 이 교정 뒤378개를 다시 통과했다. 새 실서비스 성공 범위와 오프라인 통과를 구별하며 WOS·ACM·IEEE·PQDT의 남은 고급검색 구현을 계속한다.

2026-09-13 KST, `data/validation/20260912T152024Z-rtf-mcp.json`은 실제 PQDT에서 회수한 RTF 내보내기6,680바이트를 새 SDK의 extract로 검증했다. 원 문헌2618193239의 제목,19개 텍스트 줄 중 처음3개와 다음16개, 원 바이트 보존을 대조해 completed=true였다. 이 기록은 기회수 파일의 기계적 추출이며 새 PQDT fetch/export 연결의 완료 증거로 확대하지 않는다. [striprtf](https://pypi.org/project/striprtf/)0.0.33을 고정하고 코드페이지·Unicode·바이너리 그림의 길이 경계를 처리했다. 한글·서로게이트 쌍·8비트 문자·줄 범위·잘린 바이너리의 회귀4개가 통과했다. 바이너리 그림이나 포함 객체는 실행하지 않는다.

그 뒤 독립 검토에서 RTF 그룹의 닫힘·초과 구분자·Unicode 인자 검증을 보강했다. u는 signed16 code unit, uc는 숫자 존재와 비음수를 확인하며 근거 없는 uc 상한은 두지 않는다. `data/validation/20260912T162049Z-rtf-mcp.json`은 원 HYPERLINK의 문헌 번호까지 독립 대조하고 같은19줄과 원 바이트를 다시 통과했다. RTF6검사와 실제 파일 검토가 통과했다.

PQDT Cite가 제공한 BibTeX2,098바이트에는 인용 키가 없었다. 원11개 필드와 raw_text를 유지하면서 명시적 빈 key 또는 brace-delimited 첫 field에 한해 id 빈 문자열과 citation_key_missing을 반환한다. quote-first는 정상 key와 모호해 복구하지 않는다. 기존 공용 catalog parser는 strict 기본값을 유지하고 MCP만 opt-in한다. native BibTeX2검사·기존catalog16검사, RTF와 두 원 파일을 대조한 `data/access-research/native-format-review.json`의 독립 검토가 PASS였다.

IEEE의 `data/access-research/ieee-search/sdk-live.json`은 생산과 같은 headless Firefox의 새 SDK 검증이다. newest·Journals·IEEE Access·2020–2024년을 결합한217건에서 start24/limit2의 두 페이지와 고유 문헌2건, 페이지별 CSV2개·DOI 순서를 대조했다. 뒤의 기본 문헌 번호 검색은 전체1건과 relevance/all 조건 초기화를 확인했고 OA 검색은767건과 open-access 행을 확인해 completed=true였다. 여덟 정렬은 별도 NativeChrome 함수 실측으로 원 상태값을 대조했으며 전체를 새 MCP 사례로 확대하지 않는다. 생산 transport와 기존 네 export·PDF·references·media 회수 코드는 유지했다.

`data/access-research/ieee-search/sdk-extended-facet.json`은 초기25개 발행물 후보에 없던 Artificial Life의 추가 검증이다. 원 후보 검색의 exact label로24건·문헌1건·발행물 일치와 native_typeahead 후보 추가를 생산 Firefox SDK에서 통과했다. 검사·보고 저장 뒤 출력문 오타로 최초 wrapper가 exit1이었으며 출력문을 교정했다. 실제 SDK 호출·검사 완료와 wrapper 오류를 구별한다. IEEE 관련20검사가 통과했다. 진단의 userInfo 출력 사고와 알려진 field/value 쌍 복제0건의 검사 범위는 `ACCESS-RESEARCH.md`와 `ieee-search/incident.json`에 보존한다.

Semantic Scholar의 `data/validation/20260912T153332Z-semantic-scholar-fetch-mcp.json`은 검색을 거치지 않은 별도 fetch-first 검증이다. 기존 공개 paperId9a350a6787a5a79805ddb474feb256a5adfdbefb에 metadata·abstract·export를 요청했으나 첫 원격 요청부터 rate_limited, retry_after=null이었다. 뒤의 search·references·citations는 호출하지 않았다. 현재 공개 요청 제한을 재현했으며 새로운 생산 코드 결함은 확인하지 못했다.

ACM의 `data/access-research/acm-advanced/live-sdk-multiselect.json`은 제목 algebra와 JACM·CACM의 Match Any 범주 조건93건, CACM의 원1,781건에서 Research Article을 더한220건·원 BibTeX를 실제 SDK로 검증했다. Match Any는 범주 값 사이의 OR이며 제목 조건과는 AND다. 두 번째 범주 행은 현재 UI에서 생성되지 않아 지원한다고 쓰지 않는다. 여러 facet은 순서대로 해당 패널을 열고 이전 조건을 보존하는 원 링크를 대조한다. ConceptID가 여러 의미 패널에 쓰이는 구별도 후보에 보존한다.

`acm-advanced/live-sdk-html.json`은 문헌10.1145/3831699의 원 HTML·bodymatter·backmatter와 TeX30개를 대조했다. 같은 문헌의31쪽 PDF도 앞 실제 SDK에서 회수했다. 동적 HTML 사본의 크기와 구조 단위가 달라도 DOI·제목·본문 영역·TeX 조건은 같았다. Source HTML에 없는 MathML을 만들지 않고 span.core-tex를 별도 기계 자료로 보존한다.

`acm-advanced/live-sdk-boundaries.json`은 양성만으로 닫지 않고 실제 오류 표본을 수리한 검증이다. SIGPLAN은 선택 DOI10.1145/2499370.2462176 외에10.1145/2491956.2462176을 원 CSL에 포함했다. 요청1·포함2·추가1을 명시하고 검색 record와 원 source_export를 partial로 보존하며 관계명을 추정하지 않는다. JMLR key10.5555/3814246.3814390은 BibTeX DOI가 없어도 exact CSL key·레코드 URL·세 제목을 대조해 metadata/export를 회수했다. PDF·HTML 실패는 성공한 구성요소를 지우지 않도록 교정했다. 관련44검사가 통과했다.

PQDT의 `data/access-research/pqdt-final/sdk-live.json`은 생산 Firefox의 새 SDK에서 recent·2020-01-01부터2024-12-31·Subject 두 include/한 exclude·English를 결합한148건의 start19/limit2 두 페이지와 Text4,012바이트를 대조했다. 이전 조건을 값별로 해제한 다음 검색·0건도 통과했다. 문헌2618193239의 RIS2,707·Text2,726·RTF6,680·XLS9,216·서지 PDF51,994바이트, RIS와 같은 EndNote alias, 키 없는 BibTeX2,098바이트의 일곱 형식과 각 extract가 completed=true였다. 내용 선택은 원 제어에서 명시적으로 적용한다. 서지 PDF1쪽과 논문 전문40쪽은 별도 역할이다.

`pqdt-final/sdk-supplement.json`은 기존 Supplemental PNG529,775바이트와 실제 MCP ImageContent를 재검증했다. 새 export 경로에서 예비204·빈 응답을 파일로 세지 않고 HTTP200·형식·문헌 ID·제목·범위를 검사한다. RTF와 서지 PDF의 ID는 원 hyperlink·URI annotation에서도 대조한다. 외부 reference-manager import는 제출하지 않으며 새 계정·연락 이메일을 사용하지 않는다. PQDT·supplement10검사와 RTF6검사가 통과했다.

WOS의 `data/validation/20260912T163503Z-wos-advanced-mcp.json`은21개 현재 정렬 메뉴·여섯 edition·22개 실제 필터 분야의 연결을 검증한 최신 대표 흐름이다. CPCI-S 단독의 원 WOS.ISTP·1건·WE 필드, OA/Article·인용 수 정렬·마지막 창, 처음5개 밖의2013년 후보, 발행물 후보 검색, COMPUTATIONAL COMPLEXITY와 English를 결합한1건·원 SO/LA 필드·DOI fetch 동일성이 completed=true였다. 모든 정렬·분야 조합을 전수 실측했다는 뜻은 아니다.

초기 analyze만으로 닫지 않고 각 collapsed section의 원 analyze 요청·입력 name/value/표시 count를 대조했다. See all의 별도 제어와 후보 검색을 연결하고, 같은 이름·건수가 다른 분야와 섞이지 않게 section 안에서 선택한다. 분야별 OR와 분야 간 순차 AND는 각 요청이 앞 결과 QID를 계승하는 원 동작을 대조한다. `facet_filters`와 `facet_group/facet_query`는 호출자에게 내부 index나 DOM 지식을 요구하지 않는다. `163654Z-wos-citations-mcp.json`도125건 citing·DOI 경계·양방향 fetch를 다시 통과했다.

독립 검토에서 IEEE DOI fetch가 잘못된 단일 DOI를 거절하지 못하는 반례, 원 citation의 count만 검사하는 반례, 초기 비JSON403을 잘못 분류하는 반례를 재현해 수리했다. 요청·반환 DOI, BibTeX/RIS/CSV/plain의 선택 문헌·제목·순서, JSON 파싱 전 HTTP 상태를 검사한다. 이미 보존한 실제 export6개가 새 검사를 통과했고 실패 파일은 source_export로 남긴다. WOS 일반 fetch에도 DOI·UT 동일성 검사를 추가했다. IEEE·WOS·browser 관련54검사가 통과했으며 `data/access-research/ieee-rtf-review.json`에 검토와 수리 범위를 기록했다.

PQDT의 독립 검토 네 반례는 `data/access-research/pqdt-final/review.json`에서 교정 후 PASS로 확인됐다. 선택1건에 중복된 RIS/BibTeX2건을 반환하면 count·순서 검사가 거부하고 실패 원파일을 보존한다. fulltext timeout도 metadata를 유지한 partial이다. 같은 label이 다른 그룹에 등장하는 경우에는 그룹별 More 제어의 include/exclude 상태와 한 번의 적용 전후 occurrence 변화를 결속하고 이전 그룹을 유지한다. 최종 Counter만으로 그룹을 추정하지 않는다. BibTeX는 fixed_cite_bibtex이며 export_content와 함께 지정하면 브라우저 전에 거부한다. None/JSON/HTML에도 명시 export_content를 묵살하지 않는다. `sdk-recheck.json`과 PQDT12·RTF6검사가 교정 뒤 통과했다.

WOS의 최종 교정은 `data/validation/20260912T170140Z-wos-advanced-mcp.json`과 `170340Z-wos-citations-mcp.json`에서 completed=true였다. Friendly 조건으로18건을1건으로 좁힌 뒤 반환 facet도 원 DT16에서 최종 DT1로 갱신한다. Refine과 후보 요청은 현재 QID에 결속하고 후보 조회의 결과 건수·선택 상태 불변을 확인한다. 검증 결과에는 원 QID 대신 일치 여부를 남긴다. 같은 분야의 두 label이 한 value 배열로 전달되는9건 조합도 확인했다. 추가 export 실패는 기본 plain·records·evidence를 보존한 partial이다. `data/access-research/wos-final-review.json`에서 원 세 반례를 재실행한 독립 재검토가 PASS였다.

2026-09-13 KST 최종 통합 상태의 전체 서비스 검사422개와 기존 문헌 catalog parser16개가 통과했다. 의존성 검사도 정상이며 공유 kudos-chromium.json·kudos-firefox.json은 접근 조사 시작 때의 SHA-256과 같았다. 구현·실측의 성공 범위를 향후 모든 문헌·모든 UI 조합의 보증으로 확대하지 않는다. 별도 자격 없는 Semantic Scholar의 현재429, 특정 Software Heritage flat 작업 대기, AMS의 동적식 제공자 오류와 SIAM의 확인된 비공개 문헌 권한 실패는 외부 조건으로 남긴다.

2026-09-13 KST, ACM의 일반 검색 행 AND 기본값을 Boolean 지원의 한계로 단정했던 판단을 교정했다. 사용자가 제공한 현재 Search Tips에는 Edit Query에서 다른 연산자를 지정할 수 있다고 명시되어 있다. 실제 View Query Syntax 아래 editableQuery에서 Title:(algebra) 2,327건, Abstract:(complexity) 93,527건, 교차 field AND 320건·OR 95,534건·NOT 2,007건을 대조했다. 괄호를 둔 OR도 같은95,534건이며 소문자 or/not는320건으로 대문자 Boolean과 다르게 작동했다. 원식의 대소문자·따옴표·이스케이프를 서버가 바꾸지 않는다. 공식 ACM 사용자 안내13쪽의 대문자 권고와 현 Search Tips의 편집 예외가 이 실측과 일치한다. 공식 안내: https://libraries.acm.org/binaries/content/assets/libraries/acm-digital-library-user-guide.pdf .

새 계약은 빈 query와 options.expression이다. field/fields 병용은 거부하고 다른 날짜·범주·facet·sort 제어는 함께 적용한다. 입력값·결과 AllField 검색식·collection 보존을 대조하며 원 검색식을 반환한다. data/access-research/acm-boolean-recheck/live-sdk.json의 새 SDK는 교차 field OR 95,534건과 Title 내부 OR에2024–2026년·JACM/CACM·Research Article·cited를 결합한13건, 각각 원 BibTeX를 completed=true로 확인했다. 관련46검사와 root의 전용13검사가 통과했다. Guide collection 전체 조합의 새 실측으로 확대하지 않는다. 이전의422검사는 이 Boolean 교정 전 통합 관측이다. 사용자의 후속 지시에 따라49개 자료원에서 과거 불가·보류·제한 판단을 별도로 전수조사하며 이 커밋을 전체 작업 완료로 세지 않는다.

2026-09-13 KST 제한 판단 전수조사의 공개 API 교정이다. Figshare는 현 OpenAPI가 offset<=5000과 함께 page<=5000/page_size<=1000을 제공한다. data/access-research/limitations-audit/figshare-pagination-probe.json은 offset5000/limit2와page2501/size2의 ID 일치, offset5002의400과 같은위치page2502의200을 대조했다. 기존 start>5000 사전거부를 제거하고 원 페이지의 정확한 구간을 선택한다. figshare-pagination-sdk.json은 start5000·5001·5002 각2개, 겹치는 ID와 원 export의 선택 범위를 completed=true로 검증했다. 컬렉션 구성원도 기존5000 제한에서 중단하지 않는다. 현재 OpenAPI에 버전별 구성원 경로가 없는 문제와 이 페이지 제한 오판은 별개다.

같은 조사에서 GitHub·Zenodo의 start가 limit 배수여야 한다는 구현 제한도 제거했다. Public numbered page의 포함 구간을 선택하고 원 페이지와 records를 구별한다. 두 번째 페이지의 실패·중복·건수 변화는 확보한 첫 결과와 근거를 partial로 유지한다. GitHub의 원1000건 상한과 incomplete_results는 보존한다. public-window-sdk.json은 GitHub user:octocat 6건, Zenodo algebra 15,833건에서 처음4건과 start1/limit2의 ID·원 export를 대조해 두 자료원 모두 completed=true였다. 새5검사, 기존 API19·Zenodo2검사가 통과했다.

Figshare의 공개 record3625458/file5714205는 native downloader에서 AIP와 다른 S3 저장소로 전달되는데 기존 고정 bucket 검사에 막혔다. figshare-default-file.json의 source_boundary를 재현한 뒤, 선택 파일의 exact downloader 요청이 제공한 현재 S3 redirect에 한해 허용했다. 전역 bucket 권한을 넓히지 않으며 제공된 크기·MD5를 대조한다. Figshare10검사에 허용 전달·무관한 호스트 거부·전역 URL 비허용이 포함된다. 해당39,316바이트 CIF는 MIME이 octet-stream이어서 첫 SDK의 파일 회수·checksum은 성공했지만 extract가 unsupported였다. 실패 기록은 figshare-file-sdk-before-text-extract.json에 보존한다.

공통 extract에서 NUL 없는 유효 UTF-8 octet-stream을 줄로 읽도록 교정했다. 알려지지 않은 바이너리에 문자 인코딩을 발명하지 않으며 원 MIME·바이트는 유지한다. Core23검사가 통과했고 figshare-file-sdk.json은 같은파일39,316바이트·MD5·1,045줄 중2줄 추출을 completed=true로 검증했다. 이를 CIF 의미 해석이나 모든 바이너리 형식 파싱으로 확대하지 않는다.

2026-09-13 KST, Wiley 원 UI가3행 뒤에도 Add로 최소9행을 생성하는 것을 확인해 추가2행 상한을 제거했다. data/access-research/limitations-audit/independent-wiley-sdk.json은 Title algebra와 AllField matrix·methods·analysis·polynomial의 서로 다른5행을 정확한순서로 유지하고667건·문헌1건을 회수했다. 기존3행·Date의 원 Earliest 정렬도 통과했다. 더 적은 조건으로 조용히 검색하지 않고 요청한 각 행의 생성·원 요청·페이지 변경 뒤 보존을 확인한다.

IEEE의 ieee-html-sdk.json은10488889의 원 HTML44,364자·heading18개·heading extract20개와 기존12쪽 PDF를 completed=true로 검증했다. 검색 showHtml=false인7780459도 HTML을 제공했다.1000자·heading2·paragraph2 같은 임의 하한은 제거하고 native 구조가 있는 짧은 문단의 회귀를 추가했다. HTML 제어가 있는데 본문이 준비되지 않은 경우는 html_document_not_ready 오류이며, 제어와 본문이 모두 없었던825845의 관측과 구별한다. 원 자료 없는 메타데이터 flag를 문헌 형식의 절대 부재로 해석하지 않는다.

비Nature Springer의 independent-springer-sdk.json은 DOI10.1016/S1018-3639(18)30727-X의 본문7개·HTML86,902바이트·TeX13개·그림8개를 completed=true로 확인했다. Negative10.1007/s00037-008-0249-x의 도착·안정화·초록·PDF 영역·서지 이미지는 root가 직접 열어 판독했다. 기관 접근 표시와 PDF 제어가 있으므로 초기 paywall 설명을 철회했다. 이 관측에서 PDF 바이트는 검증하지 않았고 HTML 본문 SecN은0이었다. 초록·서지·PDF 제어와 HTML 전문을 구별하며 구체 근거는 independent-springer-negative.json과 root-image-review.md에 있다.

공개 문서 WebDocuments는 script-only 응답을 격리된 공개 브라우저에서 렌더한다. 전역 unique h1과100자 하한을 제거하고 짧은 페이지·복수 heading·무제목 visible 페이지를 허용한다. 빈 로딩 상태·로그인·보안 확인은 성공하지 않으며 정제 source_page를 보존한다. OSF preprint의 main h1은 이 레이아웃에서 확인한 준비 신호다. 초기 중간 실행은 navigation shell의 제목 OSF를 너무 일찍 읽어 검증에 실패했으며 그 조건을 수리했다. independent-webdocuments-osf-sdk.json은 실제9apsq_v1의 정확한 제목·HTML168,088바이트·extract를 completed=true로 확인했다. IEEE·Wiley·publisher HTML·공개 문서의 결합52검사가 통과했다.

2026-09-13 KST, Software Heritage의 특정 Vault 준비 대기를 개별 파일 회수 불가로 확대했던 범위를 다시 열었다. limitations-audit/swh-vault-timeline.json은18:02:01.952454Z 요청 뒤 약1.672초의HTTP200 JSON, 동일directory/status new/progress_message null을 기록한다. source directory/content API의 별도 실측은20개 directory의Git tree ID와92개 고유 blob·2,763,387바이트를 모두 대조했다. 이 단계의 자료는 swh-direct-tree-probe.json, swh-directory-integrity.json, swh-direct-files-probe.json에 보존한다.

새 files part의 첫 SDK는5개 파일 뒤429여서 partial이었다. swh-files-sdk-rate-limited.json은 Retry-After가 없었던 이 실패를 보존한다. 공식 SWH FAQ의 익명 한도는 시간당120회다. 같은작업을 처음부터 반복해 이미 받은 객체를 다시 요청하지 않도록 ArtifactStore의검증된directory/content를 재사용한다. Source·role·exact HTTPS/native URI·저장 SHA-256·Git tree/blob 해시·원 길이/체크섬을 다시 대조한다. 조작된 manifest, 다른SWHID, 잘못된 provenance URI의 캐시는 받아들이지 않는다. 부분1파일+429 뒤 새adapter가 남은1파일만 요청하는 독립 반례 검증도 통과했다.

swh-files-cache-sdk.json은18:35:06.561279Z~18:35:15.107626Z의 fresh SDK다. validation_mode=previously_retrieved_live_objects로 명시하고 실제 기회수20directory·92blob 전부를 재검증해112개 manifest 항목·2,763,387바이트와17줄 중2줄 추출을 completed=true로 확인했다. 이것을 신규 원격 호출 성공으로 표시하지 않는다.

호출 제한 시간이 지난 뒤 swh-files-sdk.json의19:07:12.765400Z~19:09:48.638738Z는 source_and_verified_cache 모드로 실제 재개했다. 이전directory1개·file5개를 재사용하고 나머지를 원 API에서 회수해 총20directory·92file·112manifest·2,763,387바이트와 추출을 completed=true로 검증했다. 기존 new 상태의 Vault 압축본과 개별 객체의 완료를 구별한다. 재조회 권고는 client_poll_interval_for_anonymous_api_budget으로 출처를 명시하고60초로 조정했다. 자료원이 완료시각을 제시한 것으로 해석하지 않는다.

SWH manifest의 중첩 directory mode 누락과 비UTF-8 Git 파일명의 JSON 직렬화 오류는 독립 검토에서 재현해 수리했다. 원 mode와 root의null을 보존하고, 비UTF-8 경로는 escaped 표시·path_bytes_hex로 왕복한다. 원 JSON의 surrogate escape를 유효한 UTF-8 JSON으로 보존하며 정상 Unicode는 변하지 않는다. 디렉터리·파일·캐시·Vault/Git의28검사와 공통core23검사가 통과했고 root-api-review.json/md의 최종 판정도 PASS다. 심볼릭 링크나 보존 코드를 실행하지 않는다.


2026-09-13 KST, 검색 조건 수를 자료원 한계로 오인한 네 곳을 교정했다. PQDT는 그룹당20값, Numdam은 전체10행, SIAM은 전체51필드의 구현 상한을 제거했다. 실제 PQDT의21개 주제 include는3,335건, Numdam11조건은4,804건, SIAM52필드는17건을 반환했다. PQDT의 실패 화면을 root가 직접 판독했을 때 이미21개 OR 조건과 정상 결과가 있었으므로 원 검색의 거절이 아니었다. 원 applied chip의 방향 표시 문자·공백·복수 조건의 바깥 괄호 차이를 검증기가 잘못 거부한 것이다. 후속 독립 반례에서 이름 자체의 OR·NOT·괄호를 연산자로 잘못 분해하는 문제도 발견해 이름을 그대로 비교하도록 수리했다. 같은 그룹의 include/exclude와 여러 그룹의 중복 occurrence는 보존한다. 저장된 실제21조건 HTML도 새 검사를 통과했다.

Project Euclid의 원 폼은10행 뒤 Add 제어가 사라지지만 같은 검색 endpoint는 더 긴 원 검색식을 처리했다. 처음10개 또는20개를 모두 불일치 OR 조건으로 두고 마지막11번째·21번째 조건만 complexity 또는 TITLE:(complexity)로 바꾸어 각각7,662건·2,806건을 확인했다. 마지막 AND 불일치·NOT 자기조건의0건도 대조해 단순히 같은 말을 반복한 요청을 성공 증거로 삼지 않았다. 첫10행은 원 폼으로 직렬화하고 추가 조건은 그 FIELD:(query)·AND/OR/NOT 문법으로 연결하며 필드·연산자·값의 보존을 대조한다. data/access-research/range-cap-audit-live.json의 새 SDK는21조건7,662건, 마지막 TITLE만 양성인2,806건, 같은식에2020–2025년·PubDateDesc·start24/limit2를 결합한239건을 completed=true로 검증했다.

Euclid의 페이지 제한은 별도로 확인했다. 재구성 URL의 실패 화면에는 hCaptcha가 있었으므로 그0행을 페이지 상한의 증거로 사용하지 않는다. 정상 headed 세션에서는50쪽의 AJAX가200·전체7,662·100행을 반환했다. 같은 원 AJAX 요청의 page만51로 바꾸면200·전체0·0행·빈 HTML이었다. 현재 원 검색 코드에도50쪽 제한이 명시되어 있어 이 경로의 range_limit=50*page_size는 유지한다. 정제 근거는 euclid-ajax-boundary/terms 관련 보고와 limitations-audit/root-image-review.md에 보존한다.

APS 공개 Harvest의 start가limit의 배수여야 한다는 구현 제약을 제거했다. data/validation/20260912T185844Z-aps-public-window-mcp.json은 처음4건과start1/limit2의 정확한 ID 겹침, 원 페이지2개·내보내기2개·다음start3을 completed=true로 확인했다. 원 total은 제공되지 않아null이고 마지막 원 페이지 안에 아직 선택하지 않은 행도 has_more에 반영한다. 후속 페이지 실패·중복 ID는 정확한 창으로 성공하지 않고 확보분을partial로 보존한다. 중복 반례는 수정 전 실패·수정 후 통과했다. APS5·PQDT9·Euclid4·SIAM27검사가 통과했다.


2026-09-13 KST, Numdam의 대체 DjVu를 현재 디코더가 없다는 이유로 기계 추출 미지원에 남겼던 판단을 다시 열었다. 기존139,763바이트 원파일에는 TXTz10개가 있었고 PyMuPDF 직접 열기는 FileDataError였다. 공식 DjVuLibre의 Windows 패키지를 기존7-Zip으로 전용 폴더에 풀자10쪽·첫 쪽 텍스트2,084바이트·39줄과 페이지 이미지가 생성됐다. 설치 프로그램이나 시스템 등록은 실행하지 않았다. Root가 이미지를 직접 열어 THREE COMPLEXITY FUNCTIONS와 DOI10.1051/ita/2011126을 판독했다.

생산 경로에는 현재 공식 upstream의4847901fa2d81cdf8db89cc22f63ae5de85f963a를 고정하고 기존MSVC로 세 도구를 빌드했다. setup_djvu.py는 전용 data/tools/djvulibre에 소스·로그·실행 파일·라이선스·SHA-256을 보존한다. 세 standalone 도구의 합계는2,613,760바이트다. 각 실행 전에 저장 해시를 대조하며 원 DjVu는 임시 파일에 그대로 전달한다. 현재 코드의 BUNDLED·OLD_BUNDLED 분기는 참조 파일을 같은 원 묶음 안에서만 해석한다. Indirect DIRM, 단일 문서의INCL·NDIR은 외부 파일을 읽기 전에 구별해 중단한다. 원 텍스트 레이어를 읽고 새 OCR은 하지 않는다.

limitations-audit/djvu-sdk.json은20:07:12.110452Z~20:07:20.899846Z의 fresh SDK다. basis는 previously_retrieved_native_djvu로 실제 기회수 원파일의 새로운 디코딩·MCP 전달을 검증하며 새 원격 다운로드로 표시하지 않는다. 전체10쪽·첫 쪽 제목/DOI·349,564바이트 PNG·MCP ImageContent1개, start1/count2의2·3쪽/next3, start9/count2의마지막10쪽/next없음이 completed=true였다. 잘못된 컨테이너·외부 component·잘못된selection·시간초과·원 stderr 비노출·후속 쪽 실패의앞부분/next_start 보존·디코더 해시 변조 거부를 포함한7검사와 공통core23검사가 통과했다. 공식 도구 기능은 https://djvu.sourceforge.net/doc/man/djvutxt.html 과 https://djvu.sourceforge.net/doc/man/ddjvu.html 에서 확인했다.


2026-09-13 KST, IOP 수식 이미지를 alt/class 단어로 세었던41개 판정을 교정했다. 원 span.texImage > img[src]는 고유154개이며 TeX도154개다. 원 제어의 호스트·문헌 asset 경로·최종 파일 경로와 실제 이미지 바이트를 대조해 GIF/PNG/JPEG를 보존한다. DOI 일부가 들어간 특정 파일명 패턴이나 h2 존재를 필수로 요구하던 조건도 제거했다. 본문 식별 영역과 의미 있는 문단은 계속 대조한다.

처음 production SDK는 IOP 진입의 PerfDrive 확인 화면에서 막혔다. Root가 직접 판독한 후속 화면에는 자동집계0과 달리 iframe의 hCaptcha 체크박스와 Submit이 있었다. 체크박스 뒤에는 이미지 선택 과제가 Submit을 덮고 있었으며, 그 상태에서 뒤쪽 Submit을 누르려던 동작이 timeout이었다. 별도 소유 세션에서 현재 과제를 직접 판독하고 확인·Submit을 마치자 정상 프록시 홈페이지와 같은 수식 파일의200 image/gif·577바이트를 확인했다. 앞264바이트 HTML의 원본문은 미보존이므로 정확한 내용은 특정하지 않는다. 같은 파일의 후속 양성은 파일 부재를 반증한다.

data/validation/20260912T201746Z-iop-content-mcp.json은 이 전용 상태로 실행한 production Chromium headless의 새 SDK다. 전체 fetch가ok이며 수식154/154·그림5개·원TeX·보충PDF2쪽과 수식/그림 ImageContent를 completed=true로 검증했다. 사용자 브라우저나 등록 MCP를 재시작하지 않았고, 서버에 인식 AI·외부 solver를 추가하지 않았다. 고유 실행의 화면과 정제 timeline은 data/access-research/iop-challenge-interact.json 및 root-image-review.md에서 참조한다.

마지막 응답 검토에서 수식154개의 파일·artifact·ref 배열을 중복 반환하던 문제를 발견했다. 전체 파일별 상태를 JSON manifest로 옮기고 HTML metadata도 그 manifest 하나를 참조한다. math_images에는 건수·상태·manifest와 첫 이미지 artifact가 남는다. 20260912T202658Z-iop-equation-manifest-mcp.json은 이미 검증한 원 파일을 재사용해 새 직렬화와 fresh SDK 추출을 검사했다. component JSON은267,279바이트에서10,734바이트로 줄었고 manifest154행의 첫1번·마지막154번과 ImageContent가 일치했다. 이 검증은 새 원격 다운로드로 표시하지 않는다. 최종 root의 publisher HTML8검사와 앞선 browser 결합검사가 통과했다.

DjVu 독립 검토에서 실행 파일과 같은 폴더의 manifest 해시만 비교하면 다른 upstream/commit을 가진 도구도 수용되는 반례를 재현했다. 생성기와 추출기가 같은 고정 UPSTREAM/COMMIT/LICENSE/TOOLS를 사용하고 정확한 출처 필드·세 도구 이름·실제 파일 해시를 대조하도록 보강했다. 잘못된 upstream·commit·license 각각의 RED→GREEN, 실제 세 도구 수용과 독립 재검토가 통과했다. 로컬 빌드의 일관성 검사이며 별도의 서명된 바이너리 인증으로 확대하지 않는다.


2026-09-13 KST, 검색 행을 받아들였다는 관측과 마지막 행의 조건이 실제 결과를 바꾼다는 검증을 구별해 Numdam·SIAM의 추가 대조를 수행했다. Numdam의 새 algebra 양성 대조는 정상20개 제목을 표시했지만 기존 직접 자식 row 선택자가 마지막19·20번을 감싼 i 요소 때문에18개만 읽었다. Root가 전후 이미지를 직접 열고 원 HTML의 제목20개·직접 row18개를 대조했다. 제목의 가장 가까운 결과 row를 중복 없이 선택하도록 수리했으며 저장된 실제20개·고유문헌20개·전체26,761건을 다시 확인했다. test_numdam6개가 통과했다.

전용 credential-root/data-dir의 semantic-cap-final.json은11개 algebra 조건의26,761건과 같은 앞10조건에11번째 불일치 조건을 넣은0건을 대조했다. 마지막 조건이 실제로 적용됨을 확인한 것이다. 기존4,804건은 complexity의 다른 표본이며 이 대조의 기준으로 사용하지 않는다. 재현 스크립트도 특정 과거 총건수에 묶지 않고 동일 실행의 양성·음성과 입력 보존을 검사한다.

SIAM의 추가 대조는 조건 의미를 확인하기 전에 접근 단계에서 멈췄다. Root가 연203956Z의 후속 화면은 Cloudflare 보안 확인이고,204451Z는 Chrome ERR_CONNECTION_TIMED_OUT이다. 초기HTTP403만으로 provider_error를 내던 부분은 현재 HTML이 확인 화면이면 기존의 제한된 준비 대기를 따르도록 수정했다. 확인이 풀리면 정상 결과를 읽고 남아 있으면restricted이며 일반HTTP 오류는provider_error다. 이 세 경우를 포함한 SIAM28검사가 통과했다.52개 원 입력 보존·17건 양성은 기존 근거로 유지하지만 마지막52번째 조건만의 효과는 현재 실접속 실패로 미확정이다.51개 구현 상한을 다시 만들지 않는다.
