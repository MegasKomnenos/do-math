2026-09-12 접근 조건 조사 기록이다. 이 문서는 남은 접근 문제의 진단 근거를 정리하며, 기능 지원 여부의 정본은 [지원표](SUPPORT.md), 구현 검증의 정본은 [검증 기록](VALIDATION.md)이다. 전체 구현은 부분 완료다.

사용자는 자료원별 서브에이전트 조사와 headless가 아닌 브라우저 옵션의 비교를 요청했다. 비교는 기존 기관 인증 상태를 자료원·시험별로 복사해 수행한다. 같은 엔진·브라우저 채널·초기 저장 상태·경로·검색어·화면 크기·대기 시간을 사용하고 창 표시 여부를 바꾼다. 별도 엔진이나 공개 경로의 관측은 추가 변수를 가진 실험으로 구별한다. 실제 검색 제어·검색 결과·요청 파일을 성공 기준으로 삼으며, HTTP 200이나 숨은 성공 문구만으로 통과를 선언하지 않는다.

공유 `kudos-chromium.json`·`kudos-firefox.json`은 진단 상태 저장 대상으로 사용하지 않는다. 원 HTML·화면·상태 파일은 `.credentials/scholarly-mcp/probes/access-research-20260912/` 아래에, 정제된 보고는 `data/validation/access-research-20260912/` 아래에 보존한다. 실행 코드는 `data/access-research/`에 있다. Codex나 등록 MCP 연결은 재시작하지 않는다. 별도 API 키·계정·연락 이메일과 자동 자료원 전환은 사용하지 않는다.

생산 `KudosGateway.start()`는 `headless=True`이며 Chromium에 `channel="chrome"`을 지정한다. 설치된 Chrome의 파일 버전은 152.0.7977.83이다. Playwright 문서에 따르면 Chrome 채널은 새 headless 구현을 사용한다. 따라서 현재 Chromium 경로를 별도 구형 headless shell과 같은 것으로 해석하지 않는다. 창 표시가 개별 자료원의 접근을 개선하는지는 실측으로 판정한다. [Playwright 브라우저 문서](https://playwright.dev/python/docs/browsers)

Cloudflare는 Playwright 등 자동화 브라우저를 production challenge 지원 환경에서 제외한다. 이는 이번 출판사별 실패의 원인을 확정하지 않는다. 공식 문제 해결 문서는 네트워크·브라우저 설정·스크립트 실행·프록시·탐지 오류 등을 구분하며, Private Access Token 요청의 401은 정상적으로 나타날 수 있다고 설명한다. 따라서 해당 401 하나를 차단의 원인으로 삼지 않는다. [지원 환경](https://developers.cloudflare.com/cloudflare-challenges/reference/supported-browsers/), [문제 해결](https://developers.cloudflare.com/cloudflare-challenges/troubleshooting/challenge-solve-issues/)

KUDOS의 공개 목록에는 KNU FRIC 개별전자저널, KNU P+O Journal, KNU 개별전자저널이 실제로 있다. 이 중 FRIC의 제공 목록은 공개 XLSX이며 나머지 두 항목은 로그인 안내 동작을 갖는다. `catalogue-discovery.json`이 항목별 제어의 근거다. 공개 `KNU_FRIC_2025.xlsx`는 HTTP 200, 15,340바이트, 한 시트 52행이었고 SIAM 또는 Industrial and Applied라는 문구의 일치는 없었다. `catalogue-workbook.json`이 근거다. 이 관측은 해당 2025년 목록 한정이며, 다른 목록이나 현재 온라인 권한의 부재로 확대하지 않는다. 이후 로그인된 제공 목록 두 개를 회수해 아래와 같이 개별 구독 범주를 구체화했다. [KUDOS 학술DB 목록](https://kudos.knu.ac.kr/eng/sub.htm?nav_code=eng1643175350)

로그인 후 KUDOS가 노출한 `KNU2026.xlsx`는 14,709바이트·37행이며 SIAM Journal on Discrete Mathematics가 1997–current로 기재돼 있다. `2025knupo.xlsx`는 17,755바이트·60행이며 Multiscale Modeling and Simulation, SIAM Journal on Computing, SIAM Journal on Control and Optimization, SIAM Journal on Scientific Computing, SIAM Review가 2025년까지의 기간으로 기재돼 있다. 두 파일의 회수는 HTTP 200이었다. 근거는 비공개 원본 `siam/catalogue-files/`와 그 `report.json`이다. 목록의 기재와 실제 문헌 다운로드 성공을 구별하며, 2025년 목록으로 2026년 신규 문헌의 권한을 단정하지 않는다.

일반 Chrome을 직접 실행한 별도 시험에서는 SIAM 검색이 열렸다. 새 빈 영구 프로필을 사용해 창을 표시하고, 로컬 Chrome DevTools Protocol로 연결했다. Playwright의 `connect_over_cdp(no_defaults=True)`를 사용했으며 기존 사용자 브라우저에 연결하지 않았다. 실제 `algebra` 결과 화면은 28,378건 중 1–20 범위를 표시했고 자료 유형별 건수는 Article 22,425, Chapter 5,762, Book 191이었다. 원 화면 `native-browser/094759Z/screen-1.png`와 HTML, 정제 보고 `native-browser-094759Z.json`이 근거다. 초기 15초에는 확인 화면이었고 Tab 입력과 추가 대기 뒤 결과를 관측했다. 체크박스는 클릭하지 않았다. Playwright 문서는 이 연결 방식의 지원과 기본 연결보다 낮은 기능 호환성을 설명한다. [CDP 연결 문서](https://playwright.dev/python/docs/api/class-browsertype#browser-type-connect-over-cdp)

같은 일반 Chrome 실행 방식에 `--headless=new`를 추가하고 다른 빈 프로필로 수행한 시험은 확인 화면에 머물렀다. Tab, 현재 화면에서 초점이 확인된 체크박스에 Space, 추가 대기 뒤에도 검색 입력과 문헌 링크는 0이었다. `native-browser-095112Z.json`이 근거다. 창 모드의 실제 화면은 1267×807·배율 2, headless는 1254×800·배율 1이었으며, 두 시험 모두 `navigator.webdriver`는 false였다. 모드와 함께 실제 화면 특성과 시점도 달라졌으므로 단일 원인을 확정하지 않는다. 이 두 시험의 root 소유 브라우저는 종료했고 관련 Chrome 프로세스 0개를 확인했다.

최초 일반 Chrome 보고의 영어 문구 기반 검사는 한국어 확인 화면을 탐지하지 못했다. 해당 원 관측값을 보존한 채 검토 주석으로 바로잡았고 다음 시험에는 공통 확인 화면 판별기를 사용했다. 실제 검색 성공은 검색어·건수·결과 행이 보이는 원 화면으로 판정했다.

일반 Chrome에서 KUDOS의 로그인 제어를 찾았지만 클릭 안정성 검사에서 멈추는 문제를 별도로 재현했다. 요소의 위치와 hit-test는 정상이고 `bring_to_front()` 뒤에도 `focused=true`, `visibility=hidden`이었다. `--disable-backgrounding-occluded-windows`를 추가한 다음 시험은 rAF 두 프레임, 로그인, 검색 메뉴, 학술DB 이동을 모두 통과했다. 근거는 `native-gateway-101851Z.json`과 `native-gateway-102246Z.json`이다. Playwright의 안정성 검사는 연속 두 애니메이션 프레임을 요구하며 Chrome의 해당 옵션은 가려진 창의 실행 억제를 끈다. [Playwright 실행 가능성 검사](https://playwright.dev/docs/actionability), [Chrome 도구용 옵션](https://github.com/GoogleChrome/chrome-launcher/blob/main/docs/chrome-flags-for-tools.md)

이 조건을 `NativeChromeGateway`에 연결했다. 서버가 만든 별도 프로필과 프로세스만 소유하고, Windows의 TCP listener 소유 PID를 확인한 뒤 로컬 CDP에 연결한다. 다운로드는 전용 폴더의 GUID 파일과 완료 이벤트를 대조한다. 인증 상태는 `kudos-native-chromium.json`에 따로 저장한다. 첫 실서비스 시험 `native-class-smoke.json`은 SIAM 결과 20행·visible 상태·종료 후 자체 프로필 정리를 통과했다. 전용 검사는 다른 프로세스의 포트 거부, 다른 프로필·상태 보존, 초기화 실패 시 기존 상태 보존, 원 다운로드 경계, 드라이버 오류 뒤 자체 프로세스 회수와 일시 파일 잠금 처리를 확인했다.

자료원별 초기 조사와 후속 양성 근거는 다음과 같다. 아래 파일은 `data/validation/access-research-20260912/` 기준이다.

| 자료원 | 확인한 접근 조건 | 근거 |
|---|---|---|
| AMS | 같은 Firefox 상태의 두 모드는 프록시 고급검색 403. 공개 폼은 표시됐으나 제출이 제한됐다. NativeChromeGateway로 실제 KUDOS 기관 경로를 재검증하자 고급검색·검색 6,589건 중 요청 1건과 단일 상품 원 XLSX가 열렸다. | `ams.json`, `ams-native.json` |
| SIAM | 일반 Chrome에서 기본 28,378건, 제목 검색 1,320건, 원 인용문을 회수했다. 원 RefWorks 응답도 외부 가져오기 폼 안에 RIS를 포함하며 외부 제출 없이 읽을 수 있었다. | `siam.json`; `data/access-research/siam-contract/ris-summary.json`, `refworks-final.json` |
| ScienceDirect | Playwright Chrome headless 두 번은 홈 CPE00001, headed는 실제 검색에서403이었다. 전용 Chrome의 KUDOS 입력 대기를 교정한 뒤 실제 기관 검색이 열렸다. 최신 MCP에서 제목 검색·두 페이지 RIS·0건, facet·저널 자동완성, 세 원 인용문·PDF31쪽·보충 동영상의 회수와 자료 읽기를 통과했다. | `science-direct.json`; `data/validation/20260912T142839Z-science-direct-search-mcp.json`, `141127Z/141311Z/141704Z-science-direct-extended-mcp.json` |
| APS 기관 | Firefox headless는 검색에서 확인 화면이었다. 전용 Chrome으로 실제 기관 검색, 복수 저널·날짜 범위, 원 인용문 두 형식, 본문 PDF14쪽과 보충 PDF16쪽을 실제 MCP로 통과했다. | `aps-institutional.json`; `data/validation/20260912T130617Z-aps-extended-mcp.json`, `20260912T131701Z-aps-extended-mcp.json` |
| Semantic Scholar | 공개 HTTP에서 논문·저자·자동완성·검색의 양성 레코드를 받았다. 같은 시간대에도 다른 요청과 마지막 현행 어댑터는 429였고 Retry-After는 없었다. | `semantic-scholar.json` |
| Software Heritage | 특정 directory의 metadata는 200·19항목. 원 flat 작업 상태는 `new`, 원 파일은 404다. 다른 완성 작업의 218,076바이트와 69파일·16디렉터리의 트리 해시는 통과했다. | `software-heritage.json` |
| 개별 구독 목록 | KUDOS의 두 실제 제공 파일에서 36·59개의 보유 기록과 SIAM 6종을 확인했다. 목록의 기재와 원문 권한은 구별한다. | `individual-subscription.json` |

ScienceDirect 공식 설명은 CPE 화면을 비정상 활동에 따른 접근 IP 차단과 연결하고 자동 해제될 수 있다고 안내한다. 현재 기관 프록시 경유 요청이 거절된 사실과 정확한 서버 차단 원인을 구별한다. [ScienceDirect 오류 안내](https://www.elsevier.support/sciencedirect/answer/why-am-i-getting-an-error-message-indicating-that-my-ip-address-has-been-blocked)

조사 중 P+O 원본의 제목 셀 네 개에 포함된 별도 서비스 ID/PW가 한 진단 출력에 노출됐다. 값을 재기재하거나 사용하지 않았다. 분석기와 구현은 모든 workbook의 셀·하이퍼링크·주석에서 발견한 값을 내부 정제기에 먼저 적재하며 원 XLSX를 artifact나 fixture로 제공하지 않는다. 알려진 값 검사는 해당 범위에 한정한다. 이미 나온 출력의 삭제나 해당 자격의 폐기·교체는 확인하지 않았다.

한 조사자의 Windows `chrome.exe --version` 호출은 기존 브라우저 세션으로 전달됐다는 메시지를 반환했다. 정확한 UTC는 남지 않았으며 이후 같은 호출을 사용하지 않는다. 버전은 실행 파일 속성에서만 읽는다. 별도로, 초기 실행의 `owned-rwfpkp09` 임시 폴더 수동 삭제는 자동 승인 검토가 거부했다. 해당 폴더는 보존하며 다른 도구로 삭제를 재시도하지 않는다. 새 실행의 정상 종료 후 일시 잠금 처리는 해당 실행이 만든 프로필에만 적용한다.

다운로드 문제도 브라우저 진입 제한과 따로 확인했다. APS의 application/pdf 응답은 Chrome viewer HTML이었고 새 전용 프로필에 PDF 외부 열기 설정을 적용하자 원 PDF 다운로드가 발생했다. 명시적 PDF 탐색의 BrowserError와 CDP 이벤트의 도착 순서 차이는 새로 발생한 정확한 다운로드 이벤트에 한해서 처리했다. SIAM Front Matter10쪽과 AMS 명시적 PDF51쪽의 회귀가 통과했다. 기존 사용자 Chrome의 설정은 바꾸지 않았다. [Chrome PDF 정책 설명](https://chromeenterprise.google/policies/always-open-pdf-externally/)

SIAM의 기관 경로는 보유 목록을 읽는 것에서 끝내지 않고 실제로 검증했다. KUDOS 로그인·학술DB에서 KNU2026.xlsx의 SJDM 링크에 원 popup_gourl을 적용하자 KUDOS proxyGo, libproxy 로그인과 제공된 프록시 경로를 거쳐 공개 epubs.siam.org의 저널 화면으로 도착했다. 확인 화면은 없었지만 기관명·access-provided 표지도 없었다. 최신 비공개 논문10.1137/24M1711108은 문헌 식별이 일치해도 구매 안내를 표시했고 PDF 제어는 같은 DOI의 초록 페이지로302 복귀했다. PDF embed와 Playwright·CDP download는 모두0이었다. 목록의1997–current 기재, 정상 기관 진입, 이 문헌의 원문 권한 미확보를 구별한다. 공개 SIAM 경로를 기관 구독 성공으로 바꾸지 않는다. 근거는 `data/access-research/siam-institutional.json`과 같은 이름의 Markdown이다.

이 기록은 접근 조건의 실측이며 전체 기능 구현 완료를 뜻하지 않는다. 현재 코드에 연결한 범위와 실제 MCP 검증은 `VALIDATION.md`와 `SUPPORT.md`를 따른다.
