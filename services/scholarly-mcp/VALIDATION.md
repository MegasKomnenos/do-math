부분 완료 상태의 중간 검증 기록이다. 2026-09-09 Windows 호스트에서 공통 서버와 아래 호출 경로를 확인했다. 선정 자료원 전체의 구현 완료 기록은 아니다.

공통 검사는 `test_core.py` 17개, `test_api.py` 12개, `test_browser.py` 13개, 실제 stdio 클라이언트를 사용하는 `test_mcp.py` 1개와 DROPS·출판사·Scopus·PQDT·IEEE·AFP의 검사 8개로, 합계 51개가 통과했다. 공개 응답 fixture와 오류 경로의 대역 검사를 포함한다. 테스트 명령은 README에 있으며, 구현의 새 변경에는 관련 검사를 다시 적용한다.

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

각 실서비스 기록은 해당 입력·시점의 관측이다. 이후 공통 코드 변경의 회귀 검사와 자료원별 실서비스 검사를 구별한다. 위 기록을 각 자료원의 모든 검색 옵션·문헌·형식에 대한 검증으로 확대하지 않는다. Mathlib·Mathematical Components의 소스 문자열 검색, GitHub·Zenodo의 전체 archive, Numdam의 키워드 검색 등 추가 기능은 별도 실서비스 검증이 필요하다.

DBLP는 공개 검색 API와 공식 미러가 HTTP 200의 접근 확인 HTML을 반환했다. Semantic Scholar와 CORE에서는 429를 관측했고, CORE의 별도 자격 없는 성공 응답도 확인했다. Zenodo와 EuDML에는 timeout·504 관측이 있다. 이들을 정상 검색의 성공이나 해당 자료원의 문헌 부재로 세지 않는다. API 실패에 따른 브라우저 전환은 구현하지 않았다.

Scopus의 native Export 제어는 기관 접속에 더해 Scopus 웹 계정 로그인을 요구했다. 이 경로의 RIS·BibTeX는 restricted로 남기고 원 검색 JSON과 기계적 CSV를 제공한다. Scopus의 preprint 별도 집계와 primary 문서 집계를 분리한다. 실제 1건 응답에서도 itemCount가 10이었으므로 이를 페이지 수용량으로 처리하고 수신 건수·전체 건수·offset을 대조한다.

PQDT는 지연 표시되는 쿠키 창과 별도 export 창을 처리한다. RIS 응답을 원 검색 탭의 download 이벤트에서만 기다리면 정상 파일을 놓쳤다. 현재는 같은 ProQuest의 RIS 응답과 선택 문서 AN을 대조한다. PDF 화면에서는 전체 리소스 로딩이나 불일치하는 접근성 이름 대신 해당 docview 번호의 다운로드 제어를 확인한다. 추가 페이지 범위·연속 검색·다른 native 형식은 별도 검증이 남았다.

Springer 외 출판사 어댑터 후보는 계속 검증 중이다. 실제로 Project Euclid의 메타데이터와 PDF, AIP의 메타데이터와 초록, Oxford의 메타데이터를 회수했다. Oxford PDF는 watermark02.silverchair.com으로 이동해 현재 다운로드 허용 범위 검사에서 중단됐다. AMS는 pubs.ams.org로 이동했으며 호스트 목록을 보완했다. Cambridge·JSTOR·SIAM에는 대기 실패가, ScienceDirect 프록시에는 CPE 오류가 있었다. 이 관측을 자료원 부재나 전체 접근 불가로 확대하지 않는다. 근거는 `data/validation/20260909-publisher-*.json`이다. 이 후보 전체가 MCP에 연결된 상태는 아니다.

나머지 출판사·보완 자료원과 구체 서비스가 정해지지 않은 범주의 상태는 `registry.py`에 유지한다. `pending`이나 `not_implemented`는 개발이 남았다는 뜻이며 자료원 자체의 기능 부재를 뜻하지 않는다. Unpaywall은 키 없는 API의 연락 이메일 요구를 HTTP 422로 확인했고, 사용할 실제 이메일 입력이 남았다.

검사 중 수리한 사례에는 stdio 출력 스키마의 상태 필드, 자료 참조·바이트 무결성, 본문을 감싼 HTML form의 내용 보존, BibTeX 구분자를 보존하는 URL 정제, 공개 commit 서명과 페이지 cursor의 보존, 압축 안의 JSON 원 바이트 보존, Software Heritage의 무시되는 offset, ACM의 초기 미리보기 스크립트 의존이 있다. ACM에서는 선택한 서지 응답은 정상인데 페이지의 `UX.CSL` 초기화가 실패했다. 자료원이 제공한 처리기와 스타일을 외부 통신 없는 렌더 페이지에서 실행하여 같은 선택 문헌을 export하도록 수리했다.

진단 중 ProQuest 상대 링크의 CSRF 값과 PDF 전송 URL의 서명 매개변수 `_a`·`_s`가 각각 도구 출력에 포함되는 사고가 있었다. 사용자에게 즉시 알렸고 값을 재기재하지 않았다. 해당 조사 브라우저는 종료했으며 앞선 도구 출력 자체를 삭제한 것은 아니다. 상대 URL·서명 매개변수·중첩 URL의 정제를 수리하고 회귀 검사를 추가했다. 저장된 KUDOS 세션을 재사용해도 ID/PW가 정제기에 등록되도록 보완했다. 확인한 9개 값은 출력하지 않고 새 서버의 코드·문서·fixture·20MB 이하 로컬 산출에서 원 표현과 URL 디코딩 표현을 검사했으며 일치 파일은 없었다. 이 검사는 모든 비밀 형식이나 PDF 내부의 압축·이미지 표현에 대한 증명이 아니다. 인증 상태와 원 진단 자료는 Git에서 제외된 `.credentials/`에 유지한다.

문헌 화면의 명시적 이동은 이동 전후의 자료원 호스트를 검사하고 외부 자료원의 결과를 거부한다. 다운로드는 외부 redirect 대상에 다음 요청을 보내기 전에 중단하며 이 동작을 대역 검사했다. 브라우저 다운로드의 시간 초과는 원 예외 URL을 노출하지 않는 typed error로 변환한다. 검색 응답도 지정 자료원 호스트와 원 검색식을 대조한다. 이 검사를 모든 브라우저 하위 리소스의 네트워크 격리로 표현하지 않는다.

남은 구현·검증을 계속 진행한다. 전체 완료에는 선정 범위의 대응, 자료원별 고급검색과 형식, 제한·실패·부분 결과, 브라우저 경계와 실제 caller 흐름의 검증이 모두 필요하다.
