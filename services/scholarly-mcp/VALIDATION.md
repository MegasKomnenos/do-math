부분 완료 상태의 중간 검증 기록이다. 2026-09-09 Windows 호스트에서 공통 서버와 아래 호출 경로를 확인했다. 선정 자료원 전체의 구현 완료 기록은 아니다.

공통 검사는 `test_core.py` 15개, `test_api.py` 12개, `test_browser.py` 8개, 실제 stdio 클라이언트를 사용하는 `test_mcp.py` 1개로, 합계 36개가 통과했다. 공개 응답 fixture와 오류 경로의 대역 검사를 포함한다. 테스트 명령은 README에 있으며, 구현의 새 변경에는 관련 검사를 다시 적용한다.

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

각 실서비스 기록은 해당 입력·시점의 관측이다. 이후 공통 코드 변경의 회귀 검사와 자료원별 실서비스 검사를 구별한다. 위 기록을 각 자료원의 모든 검색 옵션·문헌·형식에 대한 검증으로 확대하지 않는다. Mathlib·Mathematical Components의 소스 문자열 검색, GitHub·Zenodo의 전체 archive, Numdam의 키워드 검색 등 추가 기능은 별도 실서비스 검증이 필요하다.

DBLP는 공개 검색 API와 공식 미러가 HTTP 200의 접근 확인 HTML을 반환했다. Semantic Scholar와 CORE에서는 429를 관측했고, CORE의 별도 자격 없는 성공 응답도 확인했다. Zenodo와 EuDML에는 timeout·504 관측이 있다. 이들을 정상 검색의 성공이나 해당 자료원의 문헌 부재로 세지 않는다. API 실패에 따른 브라우저 전환은 구현하지 않았다.

Scopus·IEEE·PQDT는 KUDOS 학술DB를 거친 기본 Firefox에서 정상 서비스 화면을 확인했다. 고급검색·export·개별 자료 확보의 MCP 연결은 개발 중이다. 나머지 출판사·보완 자료원과 구체 서비스가 정해지지 않은 범주의 상태는 `registry.py`에 유지한다. `pending`이나 `not_implemented`는 자료원 자체의 기능 부재를 뜻하지 않는다.

검사 중 수리한 사례에는 stdio 출력 스키마의 상태 필드, 자료 참조·바이트 무결성, 본문을 감싼 HTML form의 내용 보존, BibTeX 구분자를 보존하는 URL 정제, 공개 commit 서명과 페이지 cursor의 보존, 압축 안의 JSON 원 바이트 보존, Software Heritage의 무시되는 offset, ACM의 초기 미리보기 스크립트 의존이 있다. ACM에서는 선택한 서지 응답은 정상인데 페이지의 `UX.CSL` 초기화가 실패했다. 자료원이 제공한 처리기와 스타일을 외부 통신 없는 렌더 페이지에서 실행하여 같은 선택 문헌을 export하도록 수리했다.

KUDOS ID/PW 두 값을 출력하지 않고 새 서버의 코드·문서·fixture·로컬 텍스트 산출에서 직접 검색했으며 일치 파일은 없었다. 이 검사는 전 세계의 모든 비밀 형식에 대한 증명이 아니다. 인증 값은 `.credentials/` 안의 서버 전용 상태로 유지한다.

남은 구현·검증을 계속 진행한다. 전체 완료에는 선정 범위의 대응, 자료원별 고급검색과 형식, 제한·실패·부분 결과, 브라우저 경계와 실제 caller 흐름의 검증이 모두 필요하다.
