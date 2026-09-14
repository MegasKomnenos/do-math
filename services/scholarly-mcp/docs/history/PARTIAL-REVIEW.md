2026-09-14 KST에 CONTINUATION의 잔여 항목을 재검토한 기록이다. 원 자료원 호출과 함께, 13개 사이트에 별도 `codex exec`를 파견해 일반 사용자가 보는 페이지·메뉴·도움말·기관 경로를 따라갔다. 각 작업자는 실제 스크린샷을 읽었으며 root도 결론을 가르는 입력·결과·다운로드 화면을 직접 이미지로 열어 대조했다. 아래 관측을 모든 문헌이나 미래 가용성으로 확대하지 않는다.

처음에는 AMS의 비상식적인 건수만으로 논리 연산이 아니라고 결론지었지만, 사용자는 실제 화면에서 검색이 어떻게 수행됐는지 확인하라고 교정했다. 이어 코드·프로브 중심 방법을 내려놓고 사이트가 안내하는 자연스러운 이용 흐름을 살피도록 지시했다. 후속 조사는 이 방법으로 수행했다. 기관 목록의 약칭을 놓친 일, 검색 범위를 잘못 선택한 일, 고정 모달이 빠진 전체 페이지 캡처를 사이트 고장으로 오인한 일도 재검토하여 바로잡았다.

확인한 구현 결함 세 가지를 수정했다. AMS의 여러 Title term을 공백 문자열로 합쳐 논리 OR로 취급하던 변환을 거부한다. ScienceDirect의 새 세션 문헌 조회는 원 메타데이터의 ISSN·ISBN으로 제목 후보를 좁히며, 검색 행과 상세 PDF 경로의 실패를 함께 보존한다. API 어댑터는 HTTP 오류의 정제한 응답 본문·상태 코드·요청 방식·재시도 헤더를 artifact로 보존한다. 전체 639개 검사가 통과했다. Semantic Scholar의 현재 batch 가용성도 새 SDK에서 확인했다. Software Heritage는 기존 원 객체로 같은 Git tree를 갖는 별도 압축물을 복원했다.

지원표와 요청 결과의 `partial`은 다른 값이다. `registry.py`의 구현 표지는 현재 49개 자료원 중 48개에 명시적으로 설정된 부분 지원 범위이며, 나머지 하나는 사용자 결정으로 보류한 Unpaywall이다. 실패 건수에서 계산한 값이 아니다. 개별 요청의 `partial`은 요청한 구성요소들의 실제 상태를 집계한 값이다. 예를 들어 Semantic Scholar가 서지·초록·인용문·참고문헌을 모두 반환해도, 함께 요청한 원문 파일은 해당 API의 제공 범위 밖이므로 요청 전체는 `partial`이다.

사용자는 형식 미제공 등의 UI 조사 범위를 수용한 뒤 잔여 문제의 추가 시도를 허용했다. 도서관 연결을 따라 Google 도서까지 확인하자 조사 범위가 계속 넓어진다고 지적했고, 이후 추가 탐색과 지원 범위 확장을 멈추고 기존 결과만 정리하기로 했다. 이 후속 작업에서는 서비스 코드와 자료원 지원을 추가하지 않았다. 아래 재개 조건은 남은 불확실성을 설명하는 기록이며 새로운 탐색의 실행 지시가 아니다.

**AMS의 실제 처리 과정**

최초 건수 비교는 의도한 AND·NOT와 결과가 다르다는 반례였다. 그것만으로 원인을 설명한 판단을 보완했다. 해당 실행의 `3-before/after.png`, `4-before/after.png`를 직접 열었고, 별도의 새 실행에서는 실제 Search 버튼 클릭 전·후·안정 화면과 입력 제어 전체, POST 본문을 함께 기록했다.

1. Advanced Search의 Title 입력칸 하나에 문자열을 넣었다. Author·ISBN·Book Text 등 다른 입력은 비어 있었다. 결과 화면의 조건도 `Product Title: algebra AND topology` 또는 `Product Title: algebra NOT topology`였다.
2. 렌더된 사이트의 `performSearch()`를 직접 읽었다. 기본 분기는 입력값을 정규화·URL 인코딩한 뒤 `/browse?ProductTitle=...&newSearch=y`로 이동한다. 동적 논리식 분기는 별도로 `condition`, `queryElements`를 만든다.
3. 실제 `/product/browseproducts` POST는 `advancedSearch=ProductTitle=algebra AND topology`처럼 전체 문자열을 보냈다. `dynamicAdvancedSearch`, `filterString`, `simpleSearch`는 비어 있었다. 페이지 번호는 1, 표시 크기는 12였다. 이전 검색의 필터 누적이나 다른 필드로의 이동은 관측되지 않았다.
4. 응답의 `TotalRows`와 실제 결과 화면의 건수를 대조했다. 입력칸·조건 표시·응답·화면이 일치했으므로 로컬 건수 파싱 오류가 원인은 아니다.
5. 아래 대조로 기본 Title 검색이 AND·NOT를 일반 검색어로 처리하는 것을 확인했다. OR의 처리는 다르므로 모든 연산자 문자열이 같은 방식으로 처리된다고 일반화하지 않는다.

| 실제 Title 입력 | 원 응답과 화면의 건수 | 판독한 내용 |
|---|---:|---|
| `algebra` | 6,589 | 대조 검색 |
| `topology` | 593 | 대조 검색 |
| `algebra topology` | 7,094 | 같은 필드의 기본 결합 |
| `algebra AND topology` / `algebra and topology` | 각각 30,485 | 대소문자를 바꿔도 같음 |
| `algebra NOT topology` / `algebra not topology` | 각각 10,343 | topology가 있는 문헌도 반환 |
| `zzzxqvnever` / `qvvxzznever` | 각각 0 | 두 음성 검색어를 각각 확인 |
| `AND` | 25,566 | 첫 화면에 제목 “Andrei Andreevich Shkalikov…”가 있음 |
| `zzzxqvnever AND qvvxzznever` | 25,566 | 첫 화면에 “The A₂ Andrews–Gordon identities and cylindric partitions”가 있음 |
| `NOT` | 3,398 | “Notions…”, “Note…”가 원 레코드에 있음 |
| `zzzxqvnever NOT qvvxzznever` | 3,398 | 첫 화면에 “Notions of numerical Iitaka dimension do not coincide”가 있음 |
| `algebra OR topology` | 7,094 | 공백 결합과 같은 건수 |
| `OR` | 4,810 | 단독 입력에서는 “Order-topological…”, “Orthogonal…”를 반환 |
| `zzzxqvnever OR qvvxzznever` | 0 | 단어 사이의 OR는 AND·NOT와 다른 취급 |

따라서 30,485건과 10,343건은 논리식을 실행한 뒤 집합 크기를 잘못 센 현상으로 설명할 수 없다. 기본 제목 검색에 AND·NOT라는 어휘가 더해져 검색 범위가 넓어진 것이다. OR를 구분자로 취급하는 동작은 위 대조에서 확인되지만, 비공개 서버의 구체적인 토큰화 코드나 SQL을 확보한 것은 아니다. 정렬 순서가 달라질 수 있으므로 건수가 같다는 사실을 레코드 배열의 동일성으로 쓰지 않는다.

실제 논리식 분기도 별도로 시험했다. 사이트의 Custom Search에서 Title / contains / algebra 한 조건과 바깥 AND 그룹을 표시했고, 그 구조가 `dynamicAdvancedSearch`에 전달되는 것을 확인했다. 이때 응답은 HTTP 200이지만 97바이트의 `Result is null` 오류 문자열이며, 화면은 이를 0건처럼 표시했다. 일반 제목 검색의 성공과 구별한다. 정상 전송, 상품 조회 POST의 JSON 필드만 한 번 디코딩한 전송, 앞선 browse POST의 JSON 필드만 한 번 디코딩한 전송을 대조했으나 모두 같은 오류였다. 따라서 추가 URL 인코딩만을 이 오류의 원인으로 단정할 수 없다. 왜 서버가 null을 반환하는지의 내부 원인은 현재 공개 응답으로 확정하지 못했다.

이 근거로 가시 기본 필드에 의미를 보존해 매핑할 수 있는 부분집합은 유지한다. AND·NOT를 문자열로 끼워 넣어 지원한 것으로 처리하지 않는다. equals나 다단어 원자도 contains·공백 분리 검색으로 임의 변환하지 않는다.

후속의 정상 UI 탐색에서는 **Title OR의 일반적인 합집합 보장도 철회**했다. 전체 제목 `Quantum realization of the finite element method`는 1건, 짧은 `Quantum realization`은 915건이었고 따옴표로 묶어도 915건이었다. 명시적으로 `Quantum OR realization`을 입력하면 915건이지만 나머지 제목 단어를 OR로 추가하면 1건으로 좁아졌다. 짧은 검색의 두 번째 결과였던 `Hybrid quantum-classical algorithms for quantum optimal control`은 quantum을 포함하는데 더 큰 OR 결과에는 없었다. 다른 입력은 비어 있고 결과 조건도 입력한 문자열과 일치했다. 단순 건수 변화 외에 실제 입력과 빠진 레코드를 함께 확인한 반례다. 여러 Title term의 문자열 결합을 지원하던 코드를 수리했다. 기존 Author OR의 별도 검증에는 이 Title 반례를 확대하지 않았다.

일반 사용자의 문헌 찾기는 여전히 가능하다. 전체 제목으로 찾거나 Title `Quantum`과 Author `M. Deiml`을 각각 입력하면 대상 한 건을 얻는다. 다만 한 건이 나왔다는 사실은 equals 연산의 구현 증거가 아니다. 결과 왼쪽 `YEAR`의 `Use Single Year`는 별도로 작동한다. 체크 후 2025를 입력하고 `Apply Filter(s)`를 누르면 `Year: 2025` 칩과 132건, 2024를 적용하면 `Year: 2024`와 182건이었다. 입력만 바꾸면 이전 칩이 남으며 Apply가 실제 적용 단계다. 전체 범위를 복원하면 Year 칩이 사라졌다. 이 비교 시점의 원 검색은 919건으로 이전 915건과 달랐으며 그 차이의 원인은 확인하지 않았다. YEAR가 내부적으로 특정 PublicationYear 필드인지 화면이 정의하지 않으므로 expression의 그 필드와 임의로 동일시하지 않는다. 현재 MCP 옵션에는 이 연도 제어를 추가하지 않았고, 한 해 제한이 필요한 사용자의 정상 UI 경로로 기록한다.

Digital Library의 자체 지원·사서·저자 안내도 읽었다. MathSciNet의 별도 고급 검색에서는 Boolean·연도 제어가 작동했지만 다른 서비스와 검색 집합이므로 Digital Library 기능 복원으로 세지 않았다. 후속 입력·결과·연도 화면은 로컬 `data/ui-walkthrough-20260914/ams/report.md`에 연결되어 있다.

AMS 근거의 공통 디렉터리는 로컬 `data/partial-investigation-20260914/`다. 그 아래 `ams-152531/`, `ams-processing-153545/`, `ams-processing-154001/`, `ams-152809/`, `ams-encoding-153826/`에 각 실행의 보고서가 있다. 원 요청·응답과 이미지, 렌더된 함수는 보고서에 연결된 전용 private 디렉터리에 있다. 이 글에서 판독했다고 한 이미지는 실제 이미지 입력으로 열었다. 정적 browse.js의 별도 HTTP 요청은 403이어서 그 본문을 검색 코드 근거로 사용하지 않았다.

**인계된 19개 항목의 판정**

| 번호 | 대상 | 확인한 원인·범위 | 해결 시도와 현재 판정 |
|---:|---|---|---|
| 1 | AMS 같은 필드 AND | 위 기본 Title 경로는 AND를 검색어로 처리한다. 실제 Custom Search 경로는 null 오류를 반환한다. | 화면·원 요청·대소문자·음성어 대조와 동적 JSON 인코딩 대조를 수행했다. 의미 동등한 정상 실행 경로는 아직 확보하지 못했다. |
| 2 | AMS 같은 필드 NOT | 기본 Title에서 NOT가 포함 어휘로 사용되며, 제외 연산으로 실행되지 않는다. | 단독 NOT와 두 음성어 사이 NOT가 같은 3,398건인 것을 실제 화면과 응답으로 확인했다. 지원되는 논리 NOT로 표시하지 않는다. |
| 3 | AMS 서로 다른 필드 OR | 현행 기본 필드의 검증된 결합은 AND다. 복합식을 위한 동적 경로는 현재 오류 상태다. | 기본 필드 간 OR로 임의 변경하지 않는다. 이번 동적 한 조건 시험도 실패했으므로 복합 OR 복원으로 세지 않는다. |
| 4 | AMS equals | Title·Author의 부분 문자열 검색은 equals와 같지 않다. 결과 화면에는 별도로 정확한 한 해를 제한하는 YEAR 제어가 있다. | expression의 `expression_mapping_unavailable`은 유지한다. 한 해 제한은 위 `Use Single Year` 정상 동선으로 가능하다. |
| 5 | AMS 다단어·문장부호 원자 | 한 원자를 공백으로 나누면 여러 검색어의 결합이 된다. punctuation도 원 문법의 일부가 될 수 있다. | 위 실제 처리 경로로 의미 변경 위험을 확인했다. 단어 삭제·분리·자의적 인용으로 기능을 복원했다고 하지 않는다. |
| 6 | SIAM `10.1137/24M1711108` PDF | 공식 KNU2026 보유표는 대상 저널을 1997–current로 기재하지만 그 링크·호 목차·공식 프록시를 거쳐도 Get Access다. 통합 전자저널 포털의 2011 종료 기재와도 다르다. | 구독 부재로 단정하지 않는다. 기관 권한 성립의 내부 원인은 미확정이다. 같은 논문의 accepted arXiv v2 PDF 28쪽을 별도 확보했다. |
| 7 | ScienceDirect Preface `S0065230X26000631` PDF | 로컬 제목 단독 후보 누락은 수리했다. 기관 레코드는 ClinicalKey 접근을 표시하지만 권 목차는 No access, 정확한 Preface 선택 다운로드는 비구독이다. | 제목·시리즈·권의 정상 검색으로도 정확한 한 건에 도달했다. ClinicalKey 직접 링크는 content-not-found이며 Books 검색·Browse의 전체/구독 목록에서도 모책을 찾지 못했다. 원문은 미확보다. |
| 8 | ScienceDirect Book review `S1765462926000553` PDF | 새 호출의 정확한 상세 문헌은 Purchase PDF에 해당하는 접근 제한이다. | 수정한 원본으로 재검증해 같은 `restricted/fulltext_access_restricted`를 확인했다. 다른 문헌의 PDF 성공으로 대체하지 않는다. |
| 9 | Oxford 검색별 Export title list | 실제 모달의 reCAPTCHA가 사이트 키 도메인 오류를 표시한다. KUDOS의 OUP 경로에서도 정상 Download는 파일을 주지 못한다. | OUP 약칭과 공식 검색 가이드로 경로 부재 오판을 고쳤다. 별도 제품별 전체 도서 Excel·OSO/UPSO KBART와 장 RIS를 확보했지만 검색별 export 성공으로 세지 않는다. |
| 10 | JSTOR `community.39197180` 영상 | 후속 UI는 FREE 영상의 실제 재생과 전사문 시간 이동을 제공하지만 Download는 비활성이다. 앞선 challenge는 이번 화면까지의 접근 실패를 뜻하지 않는다. | 재생 및 0:22 이동을 확인했다. 옛 기관 저장소는 폐지 안내, Handle은 같은 JSTOR 항목으로 돌아왔다. 원 영상 파일은 미확보이며 관련 카드의 다운로드를 대상 파일로 세지 않는다. |
| 11 | De Gruyter `snde1089_supplementary_2.zip` | 문헌 PDF가 실제 기관 라이선스로 열리는 세션에서도 같은 Data and code 링크는 404다. | 논문 11쪽 PDF와 같은 호의 Replication 표시를 확인했으나 ZIP 대체 링크는 없었다. 첨부 기록 부재나 문헌 인증 실패로 분류하지 않는다. 역사 ZIP과의 byte 동일성은 미입증이다. |
| 12 | Taylor & Francis 두 editorial 초록 | `10.1080/21642583.2021.1892260`, `10.1080/1551806X.2013.768873`의 전체 HTML과 Citation & abstract RIS 모두 별도 초록을 제공하지 않는다. | 두 번째 문헌은 View PDF → 새 ePDF 뷰어 → Download PDF로 실제 파일도 확보했다. 저장 파일의 서지 표지1쪽+논문9쪽을 구별하며 본문 첫 문단을 초록으로 승격하지 않는다. |
| 13 | Springer `10.1007/s00037-008-0249-x` HTML 본문 | 기관 Full access 상태에서도 페이지의 Sections는 Abstract 다음에 Article PDF를 제공하며 HTML 본문을 제공하지 않는다. | KUDOS Springer Archive의 연도에 맞는 경로로 28쪽 PDF를 확보했다. HTML 선택에서의 미제공을 문헌 전체 원문 부재로 넓히지 않는다. |
| 14 | EuDML 책 204358 NLM 전문 | 새 HTTP 200의 XML에는 14개 book-part-meta가 있고 본문 p·sec·table·formula·book-body가 없다. | 원 링크의 GDZ에서 전체책 PDF 156,700,606바이트·412쪽과 IIIF/METS를 확보했다. 서지 표지1쪽과411개 스캔을 구별하고14개 부분의 면 대응을 보존했다. 외부 본문을 EuDML XML 전문으로 표시하지 않는다. |
| 15 | CORE indexed fullText | 15:26:45 UTC 요청은 429였고 재시도 시각은 15:36:45였다. 15:37:31의 허용된 재조회는 HTTP 200과 원 안내문을 반환했다. | Output 213561553의 `fullText`는 `Not available for public API users.`다. 제한 시각을 지키고 원 필드를 확인했다. 이 필드와 별도 PDF 제공은 다르다. |
| 16 | Semantic Scholar Graph API 원문 파일 | Graph 응답은 서지·원문 위치 메타데이터를 제공하며 파일 바이트를 제공하지 않는다. 해당 논문의 OA 값은 실제 웹 접근과도 다르다. | full-parts 호출에서 나머지 네 구성요소는 available, fulltext만 not_offered다. 별도 UI의 Reader → arXiv에서 실제 v2 PDF 28쪽을 확보했다. |
| 17 | Semantic Scholar 현재 batch 가용성 | 15:06의 같은 대상은 429였고, 15:31의 새 SDK는 실제 payload를 받았다. | **해소.** 메타데이터·초록·BibTeX·참고문헌 30개가 available이며 reported 30과 일치한다. 미래 가용성을 보증하지 않는다. |
| 18 | Software Heritage 원 Vault 작업 | 15:31 새 SDK의 task 419779186은 new다. 이후 정상 UI의 tarball 요청·성공 알림·Downloads도 같은 SWHID를 new로 표시하며 완료 링크가 없다. | 고정 모달이 빠진 전체 화면 캡처를 탭 고장으로 오인한 판정은 철회했다. 별도로 기존 92파일·20디렉터리로 899,228바이트 tar.gz를 복원하고 Git tree를 검증했다. 원 작업의 대기 내부 원인은 미확정이다. |
| 19 | Figshare collection 4046897 v6 구성원 | 버전 메타데이터는 17건인데 실제 UI·검색·Cite all items의 TXT/RIS는 모두 같은 16개 제목이다. 아이템의 Back은 최신 v8로 돌아간다. | v6 URL을 다시 열어 판본을 고정하고 실제 TXT·RIS 및 첫 구성원의 원 ZIP을 받았다. 인용 파일의 아이템별 판본 DOI도 보존했다. 정확한 17번째 ID와 불일치 원인은 미확정이며 v8로 채우지 않는다. |

**수정과 복원의 근거**

일반 UI에서 찾은 자원과 안내는 다음 경로로 다시 이용할 수 있다. 아래 링크의 보고서에는 첫 화면의 구성, 읽은 안내, 실제 클릭 순서와 이미지 파일명이 있다. 이들은 로컬 실행 근거이며 `data/`를 제외한 배포 사본에는 포함되지 않는다. 외부 원고나 제품별 목록의 확보는 원 자료원의 제한된 API 필드·검색별 export를 복원한 것으로 세지 않는다.

| 사이트별 화면 기록 | 실제로 유효했던 흐름·자원과 남은 경계 |
|---|---|
| [AMS](../../data/ui-walkthrough-20260914/ams/report.md) | 전체 제목 또는 Title+Author로 문헌 찾기, YEAR의 단일 연도 적용. 자체 지원·사서·저자 안내와 MathSciNet을 구별했다. 논리 Title OR의 잘못된 변환은 수리했다. |
| [SIAM](../../data/ui-walkthrough-20260914/siam/report.md) | KUDOS 개별전자저널 제공리스트 → 공식 저널 → Vol.40 Issue3 → 대상 PDF까지 확인했다. Help와 기관 IP 설정 가이드는 개인 가입이 기관 권한을 대신하지 않음을 설명한다. 별도 accepted arXiv2411.07981v2 500,107바이트 PDF를 확보했다. |
| [ScienceDirect](../../data/ui-walkthrough-20260914/science-direct/report.md) | Preface + 출판물 자동완성 Advances in Cancer Research → Volume171 필터로 정확한 한 건. 권 목차와 ClinicalKey Books까지 확인했다. 일반 검색의 PII 오류를 검색 전체 장애로 넓히지 않는다. Patient Access는 해당 자격의 이메일 요청 절차여서 실행하지 않았다. |
| [Oxford](../../data/ui-walkthrough-20260914/oxford/report.md) | KUDOS의 약칭 OUP → 실제 바로가기 → Title 검색 → Export 모달. 검색 가이드와 별도 사서용 title list/KBART 안내를 읽고 전체 도서 Excel 61,709개 데이터 행, OSO/UPSO ZIP, 대상 장 RIS를 받았다. 제품 목록은 검색 결과의 장·논문 목록과 다르다. |
| [JSTOR](../../data/ui-walkthrough-20260914/jstor/report.md) | 대상 영상 Play, Transcript의 시간 링크, Item details의 옛 저장소·Handle을 따라갔다. FREE 시청과 비활성 Download는 다른 권한이다. Related images and media는 각자 ID를 가진 독립 문헌이다. |
| [De Gruyter](../../data/ui-walkthrough-20260914/de-gruyter/report.md) | DOI 검색 → Supplementary Material → Data and code. 기관에서 논문 PDF 179,743바이트·11쪽은 받았지만 ZIP은404다. 오른쪽 Replication은 같은 호의 현재 논문 유형이며 별도 자료 링크가 아니다. PDF에도 목표 ZIP의 대체 URL이 없다. |
| [Taylor & Francis](../../data/ui-walkthrough-20260914/taylor-francis/report.md) | 다른 저널의 DOI는 This Journal 범위가 아닌 홈의 전체 검색에서 찾았다. KUDOS의 Taylor 약칭으로 기관 Full access를 얻었다. View PDF는 새 뷰어를 여는 제어이며 그 안의 Download PDF로 두 번째 문헌187,178바이트·10쪽을 받았다. 두 editorial의 전체 HTML과 RIS에 없는 초록을 본문으로 채우지 않는다. |
| [Springer](../../data/ui-walkthrough-20260914/springer/report.md) | KUDOS Springer Archive의 2014년까지 제공 범위에 맞는 경로로 2008년 대상 PDF 372,391바이트·28쪽을 받았다. 기관 검색의 결과 없음은 구독 부재 증거가 아니다. 기관 Full access 페이지도 HTML 대신 Article PDF를 제공한다. |
| [EuDML](../../data/ui-walkthrough-20260914/eudml/report.md) | 책204358 → GDZ → Export의 PDF·IIIF Manifest·METS를 확보했다. METS로14개 부분의 면을 연결하고 페이지 선택에서 Preface(물리3)와 Table X(물리405)의 실제 판면을 읽었다. PDF는 서지 표지 때문에 각각4쪽·406쪽이다. EuDML NLM metadata를 전문으로 세지 않는다. |
| [CORE](../../data/ui-walkthrough-20260914/core/report.md) | Services → API → 다운로드 정책을 읽었다. Reader의 자동 이동 대기 뒤 화면의 click here로 실제 PDF를 받았다. CORE 배너가 있는 329,196바이트와 Sofia University 원출처의 280,823바이트는 같은 논문의 서로 다른 파일이며 둘 다8쪽이다. indexed fullText의 공개 API 제한과 구별한다. |
| [Semantic Scholar](../../data/ui-walkthrough-20260914/semantic-scholar/report.md) | paper ID 검색의0건 뒤 정식 문헌 → Semantic Reader → arXiv View PDF로 실제 v2 PDF 698,413바이트·28쪽을 받았다. Graph의 isOpenAccess=false와 빈 openAccessPdf는 실제 원문 부재를 뜻하지 않았다. arXiv comments의26 pages와 실제28쪽 차이를 Reader 변환으로 추론한 표현도 바로잡았다. |
| [Software Heritage](../../data/ui-walkthrough-20260914/software-heritage/report.md) | 디렉터리 Download as tarball → 요청 모달 → Downloads 상태를 확인했고 개별 README는 내려받았다. 전체 페이지 캡처에서 빠진 고정 모달은 viewport 이미지로 확인했다. 새 요청 후에도 new이며 내부 대기 사유는 공개되지 않았다. |
| [Figshare](../../data/ui-walkthrough-20260914/figshare/report.md) | v6의 Cite all items로 TXT 2,813바이트·RIS 16,058바이트를 받았다. 첫 아이템17081231v1의 DataCite XML과 원 ZIP 9,456,363바이트도 확보했다. 직접 HTTP202/빈본문을 브라우저 다운로드 실패와 동일시하지 않는다. |

ScienceDirect 수정 전 실제 보존 레코드에는 query `"Preface"`, options `{"field":"Title"}`, total 63,148, received 100이 있었고 대상 PII는 없었다. 수정 후에는 원 `citation_issn=0065-230X`를 사용한 검색이 45건을 반환했으며 대상 PII가 있었다. 그 행을 다시 정확히 선택한 뒤 원 다운로드 제어가 현재 세션의 비구독을 명시했다. 검색 후보와 PII·제목 검증은 유지한다. 같은 흐름은 인용문 내보내기의 행 선택에도 쓰인다. 회귀 검사에서는 ISSN·ISBN이 필요한 새 세션 사례와 두 경로의 오류 보존을 먼저 실패시킨 뒤 수정해 통과시켰다.

GDZ의 PDF 클릭은120초 동안 브라우저 다운로드 이벤트로 확인되지 않았다. 이후 화면이 제공한 정확한 PDF 링크의 응답에서 원파일을 확보했다. IIIF와 METS는 클릭 후 열린 JSON·XML 원문 주소의 응답을 저장했다. 따라서 세 파일 확보와 브라우저 다운로드 이벤트 성공은 구별한다. PDF 쪽수와 표제지·Preface·Table X의 표본 판면은 대조했지만411개 스캔의 이미지 바이트를 모두 일대일 비교한 것은 아니다. 별도 DFG-Viewer는403이어서 목차 UI를 확인하지 못했다. EuDML 화면에 NLM 라벨이 없었다는 이유로 이미 확인한 원 NLM API를 MCP 생성물로 해석하지 않는다.

API 오류 응답은 이전에 상태 코드 분기에서 버려졌다. 이제 JSON의 민감 필드를 정제하고 HTML의 실행 코드·입력 제어를 제거한 뒤 `provider_error_response` 역할로 저장한다. 상태 분류와 재시도 여부는 바꾸지 않는다. 저장 실패도 원래의 429 등을 덮어쓰지 않는다. CORE의 실제 429에서 0바이트 응답과 재시도 헤더를 보존한 것을 확인했다. 이 변경은 과거 원시 로그 전체의 정제나 과거 노출의 삭제를 뜻하지 않는다.

Software Heritage 복원물은 `data/partial-investigation-20260914/software-heritage/7057a716afab8ca80728aa7c6c2cc4bd03b0f45b-reconstructed.tar.gz`다. SHA-256은 `2158abf9fc2ce4703c5677c955d4764fb3369a3d45dd26956f048d7bc170a8e6`이다. 원 객체는 저장소 SHA-256과 Git blob/tree 해시로 재검증했고 새 원격 요청 없이 묶었다. 완성한 압축물을 다시 읽어 디렉터리 해시 `7057a716afab8ca80728aa7c6c2cc4bd03b0f45b`를 확인했다. 압축 시간·소유자 등은 로컬 생성값이다. 파일 내용·경로·실행 비트에 대한 Git tree 동일성은 입증했지만 원 Vault 압축 바이트와의 동일성은 주장하지 않는다. 새 서버 옵션 대신 기존 files 산출물을 이용한 독립 복원물이다.

[Semantic Scholar 공식 안내](https://www.semanticscholar.org/product/api)는 비인증 요청들이 한도를 공유하며 혼잡할 때 추가 제한될 수 있다고 설명한다. 이번 429의 내부 버킷을 특정하는 근거는 없으나, 같은 입력의 후속 성공으로 영구적인 문헌 부재나 구현 불가라는 해석은 배제된다. [Figshare 버전 규칙](https://info.figshare.com/user-guide/how-versioning-works/)은 컬렉션 구성원 변경과 판본을 연결하므로 다른 current 판본을 v6의 구성원 증거로 쓸 수 없다. [Software Heritage 설명](https://docs.softwareheritage.org/devel/getting-started/api.html)은 Vault 압축이 비동기 작업임을 명시한다. 공개 상태 응답은 작업이 왜 시작되지 않았는지까지 설명하지 않는다.

실행 근거의 공통 위치는 로컬 `data/partial-investigation-20260914/`다. `source-inventory.json`, `fresh-sdk/results.json`, `software-heritage/recovery.json`, `baseline-tests.txt`, `final-tests.txt`와 자료원별 result/report가 있다. raw 인증 상태와 화면은 전용 private 경로에 두었다. 새 SDK와 어댑터 직접 호출, 기회수 객체 재검증, 과거 원 응답 재판독을 서로 다른 검증 방식으로 기록했다. 이 로컬 근거가 없는 배포 사본에서는 같은 실행을 했다고 주장하지 않는다.

확보한 주요 PDF의 경로·바이트 수·SHA-256·실제 페이지 수는 로컬 `data/ui-walkthrough-20260914/verified-downloads.json`에 root가 다시 확인해 보존했다. 각 문헌의 판본·외부 출처 경계는 위 사이트 보고서를 함께 따른다. 전체639검사 통과 기록은 같은 디렉터리의 `integration-tests.txt`다.

확정한 것은 위 화면·응답·파일이 보여 준 발생 지점과 동작이다. AMS 동적 조회의 null 및 비공개 검색 구현, SIAM 기관 권한 성립 조건과 보유표 충돌, ScienceDirect–ClinicalKey 접근 표지의 불일치, Vault 대기 사유, Figshare v6의 정확한 누락 구성원은 현재 공개 근거만으로 내부 원인을 확정할 수 없다. Oxford의 오류는 사이트 키 도메인 문제를 명시하지만 어떤 운영 설정을 고쳐야 하는지까지 확인한 것은 아니다. De Gruyter의404도 파일의 실제 삭제·이동 여부를 증명하지 않는다. 이 한계를 공급자 전체의 영구 불가로 바꾸지 않는다. 새 공식 제어·원 응답·정확한 권한 상태가 생기면 해당 입력에서 재개한다. 자격 추가, IdP 재제출, 지원팀 연락은 이번에 실행하지 않았다.

**추가 조사와 종료 판정**

Figshare·Software Heritage·ScienceDirect의 후속 조사와 도서관 검색 보완을 별도 CLI로 수행했다. De Gruyter 역사 첨부도 실제 원 화면·README와 다시 대조했다. 사용자의 범위 제한에 따라 추가 탐색은 종료하고 아래 확인 결과를 보존한다. 모든 공급자 문제를 해결하거나 가능한 모든 경로를 소진했다는 뜻은 아니다.

| 대상 | 마지막 확인·조치 | 남은 문제를 재개할 조건 |
|---|---|---|
| AMS 논리 검색 | 기본 Title·동적 경로·자체 도움말·가이드 탐색을 대조했고, 추가 공식 도메인 문서 검색에서도 새 문법 근거를 얻지 못했다. 입력 문자열을 바꿔 같은 null을 반복하거나 다른 서비스의 Boolean을 이 기능으로 세지 않는다. | Digital Library의 해당 문법에 대한 공식 안내 또는 정상 실행 사례, 동적 검색 응답의 변화. |
| SIAM 출판사 PDF | 공식 보유표·프록시·기관 선택·실제 호 목차를 이미 확인했다. 새 자격 없이 다른 정상 기관 경로가 발견되지 않아 잠금 화면을 다시 요청하지 않았다. accepted arXiv v2는 확보되어 있다. | 기관의 실제 계약·등록 IP·프록시 연동 확인 또는 정상 기관 세션의 성립. |
| ScienceDirect 두 대상 원문 | 별도 ClinicalKey eBook 경로와 다섯 제공리스트를 확인했다. ClinicalKey Books 제목 필터, 소장 eBook의 서명·총서명 완전일치에서 Preface 모책을 찾지 못했다. Book review 저널은 네 저널 목록에 일치 행이 없었다. 실제 PDF 접근 상태를 바꾸는 새 경로는 얻지 못했다. | 대상2026년 권·문헌을 포함하는 실제 기관 권한, 정상 도서 제공 경로 또는 ScienceDirect–ClinicalKey 연결의 교정. |
| Preface의 도서관 연결 | 총서명0건 뒤 서명 전방일치에서 시리즈1건을 찾았다. 확인한 물리 소장은 중앙 최대v.116·의학분관 최대v.122이며 대상ISBN 조회는0건이다. Summon의 시리즈·171·2026 검색10건 중9건은171권,1건은169권이었다. 기관 ProQuest의 한171권 장은 MEDLINE 서지·초록이고360LINK는 이용 가능한 전자자료가 없다고 했다. Google 연결의 다른eBook ISBN 샘플도 Preface xiii–xviii의 페이지 미리보기를 제공하지 않았다. | 대상171권의 실제 원문 제공 또는 접근 상태 변화. 다른 장·ISBN의 자료와 검색 스니펫을 Preface 원문 확보로 세지 않는다. |
| Oxford 검색별 title export | 실제 기관 OUP 경로의 사이트 키 도메인 오류와 공식 인증 안내를 확인했다. 같은 Download 재시도나 새 개인 계정 생성은 수행하지 않았다. 제품별 목록·장 인용은 별도 확보 상태다. | CAPTCHA 설정 수정 또는 기관이 제공하는 다른 정상 인증 경로. |
| JSTOR 대상 영상 파일 | 실제 시청·전사문 시간 이동은 가능하지만 원 Download가 비활성이고 옛 원 저장소는 같은 JSTOR 항목으로 돌아간다. 새 정상 파일 링크가 없어 같은 동선을 반복하지 않았다. | 기여 기관의 다운로드 활성화 또는 별도의 공식 파일 제공. |
| De Gruyter 데이터·코드 | 당시 동일 논문 화면의 Supporting Files가 Belaire_Contreras.zip을 Data and code로 명시함을 root가 이미지로 재확인했다. ZIP에는6개국 데이터·Ox2파일·FORTRAN·README가 있다. 당시 첨부 확보는 확정하며 새 다운로드로 세지 않는다. | 현재 ZIP의 정상 제공 또는 과거 첨부와 현재 파일의 이관·교체 근거. 현재 링크의 byte 동일성은 미확정이다. |
| Software Heritage 원 Vault | 2026-09-14 10:21 KST의 저장 상태 재개와 공식 GET 모두 같은 task419779186·new·progress null이다. Vault Operational 및 공개 장애 이력에서도 이 작업의 대기를 설명하는 사건은 발견하지 못했다. 새 POST·재큐잉·반복 polling을 하지 않았다. | 제공자 측 작업 진행이나 구체적인 운영 안내. 기존 원 객체 기반 재구성 tar.gz는 별도로 이용할 수 있다. |
| Figshare v6 구성원 | 인접 판본의 metadata/UI·RIS는 v5 15/15, v6 17/16, v7 19/18이다. v6보다2분45초 먼저 게시된17061347.v1은 현재v8 REST/UI의 유일한 차이 항목이며 가장 강한 후보로 좁혀졌다. 실제 후보 PDF19,298,271바이트·41쪽을 확보했다. | v6의 역사적 관계 ID 목록이나 소유자·제공자의 확인. 후보를 확정된17번째로 삽입하지 않는다. |

Figshare 후보 PDF의 SHA-256은 `c1ed6815d3138343f3538f3ade4277dff8f6d9e9a30a1550a68d452f191f5e78`이다. root가 파일 크기·쪽수·표지를 대조했다. 후보가 공개되어 있고 정상 다운로드되는 사실은 확정했지만, v6의17/16 차이를 만든 내부 처리 원인은 여전히 미확정이다. 역사 ID 관계가 없는 상태에서 current 관계를 소급해 채우면 과거 판본을 바꾸므로 기존 partial 보존은 유지한다.

ScienceDirect 추가 조사에서 받은 ClinicalKey eBook 목록은1,039개 도서와2010–2025 Copyright Year를 담고, 별도 ClinicalKey 콘텐츠 목록은2026-04-15 갱신 표기다. ScienceDirect의2025 목록은2,596행 모두 Journal이다. 이 저널 목록에 책 시리즈가 없다는 사실은 도서 계약 부재의 증거가 아니며,2025 목록으로2026년 최신 권한을 확정할 수도 없다. Book review의 실제 비구독 화면과 오래된 목록의 부재를 별도 근거로 유지한다. root는 원 XLSX의 범위·헤더·대상 제목·ISSN·시점을 대조했고 로컬 `science-direct/root-list-review.json`에 파일 확인값을 보존했다.

새 근거는 [Figshare 후속](../../data/ui-walkthrough-20260914/figshare/report-close.md), [Vault 후속](../../data/ui-walkthrough-20260914/software-heritage/report-close.md), [ScienceDirect 도서·제공리스트](../../data/ui-walkthrough-20260914/science-direct/report-close.md), [도서관 연결 확인](../../data/ui-walkthrough-20260914/catalog-close/report.md), [De Gruyter 역사 첨부 대조](../../data/ui-walkthrough-20260914/de-gruyter/report-close.md)에 있다. 각 보고서가 실제 이미지·원응답·다운로드 경로를 제공한다. Google 도서 확인은 기존 Preface의 연결 경로 조사였으며 MCP 자료원 추가나 자동 대체 기능 구현이 아니다. 이후에는 새 연결을 따라 조사 범위를 넓히지 않는다.
