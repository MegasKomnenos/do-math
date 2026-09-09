부분 완료 상태의 중간 검증 기록이다. 2026-09-09 Windows 호스트에서 공통 서버와 아래 호출 경로를 확인했다. 선정 자료원 전체의 구현 완료 기록은 아니다.

공통·자료원 검사 65개가 통과했다. 공개 응답 fixture와 오류 경로의 대역 검사, 실제 SDK 클라이언트와 서버 프로세스의 stdio 검사를 포함한다. 테스트 명령은 README에 있으며, 구현의 새 변경에는 관련 검사를 다시 적용한다.

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

전체 구현은 부분 완료이며 나머지 출판사·추가 기능의 구현을 계속한다. 별도 웹 계정 또는 연락 이메일을 요구하는 기능은 사용자 지시에 따라 보류하고 입력을 요청하지 않는다. 위 성공 기록은 해당 시점·입력의 검증이며 모든 옵션의 검증으로 확대하지 않는다.
