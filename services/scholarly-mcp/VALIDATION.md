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

문헌 화면의 명시적 이동은 이동 전후의 자료원 호스트를 검사하고 외부 자료원의 결과를 거부한다. 다운로드는 외부 redirect 대상에 다음 요청을 보내기 전에 중단하며 이 동작을 대역 검사했다. 브라우저 다운로드의 시간 초과는 원 예외 URL을 노출하지 않는 typed error로 변환한다. 검색 응답도 지정 자료원 호스트와 원 검색식을 대조한다. 이 검사를 모든 브라우저 하위 리소스의 네트워크 격리로 표현하지 않는다.

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
