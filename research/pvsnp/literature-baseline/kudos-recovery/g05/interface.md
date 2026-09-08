# g05 실행 진입점과 실제 UI 관찰

현행 재개 진입점은 `resume.py`다. 실행 전에 `../contract.md`, `../restart-contract.md`, `assignment.json`, `progress.json`, `work-queue.json`과 선택 문헌의 결과·검토 목록을 읽는다. 수집·검토·완료 기준은 두 계약을 우선한다. 이 문서는 확인된 UI 경로와 실행 방법을 설명한다.

`C:/math`에서 `python research/pvsnp/literature-baseline/kudos-recovery/g05/resume.py`를 실행하면 공통 큐가 반환한 남은 작업을 소비한다. 실행할 작업에 ScienceDirect가 포함되면 `--engine firefox`를 붙인다. `--only <paper_id>`는 문헌을, `--limit <건수>`는 이번 실행의 큐 항목 수를 제한한다. `--offline --reassess`는 저장 증거와 현재 판별 규칙을 대조하며 새로운 브라우저 조사를 수행하지 않는다. 실행 프로세스의 코드판본은 `runs/<시각>/manifest.json`의 PID·인자·SHA256으로 확인한다.

원문과 초록 중 미확보된 구성요소, 새 후보, 직접 판독이 필요한 작업은 각각 유지한다. 검증된 원문과 초록이 모두 확보된 문헌은 추가 수집을 닫을 수 있다. 미해결 판독은 결과와 `work_state`에 남기며, 공통 전체 검사에서 `passed=true`와 `complete=true`가 함께 나와야 382건 완료다.

## 2026-09-08 초기 관찰

2026-09-08 Playwright Chrome의 독립 context에서 bootstrap 저장 상태를 읽어 관찰했다. 인증 상태의 내용은 이 문서에 포함하지 않는다.

KUDOS 홈페이지 `https://kudos.knu.ac.kr/pages/index.htm`의 학술DB 메뉴는 `https://kudos.knu.ac.kr/pages/sub.htm?nav_code=kud1641346542`로 이어진다. 학술DB 화면의 ACM Open 설명은 컴퓨터 공학 전자저널과 회의자료 원문 제공이다. 홈페이지 전자자원 통합검색 링크는 `https://knu.summon.serialssolutions.com/ko-KO/search?ho=t&q=`다. 학술DB 전체 본문에는 다른 서비스의 접근정보가 섞일 수 있으므로 전체 본문을 산출물로 보존하지 않는다.

Summon에서는 `input[name=q]:visible`에 DOI 또는 제목을 입력하고 Enter를 누른다. DOI 10.1145/3749740.3749756과 10.1145/2902945.2902948의 초기 검색은 0건이었다. 제목 검색과 DOI 검색의 범위가 같다고 가정하지 않는다. 첫 문헌의 제목 검색에는 다른 논문 세 건이 나타났으므로 제목 단어의 검색 적중을 동일성으로 채택하지 않는다.

`button[data-aid=quick-look-button]:visible`은 실제 표시된 Quick Look 상세보기다. `get_by_text('Quick Look', exact=True).first`는 숨겨진 중복 요소를 잡아 30초 timeout을 발생시켰다. visible 조건으로 고친 뒤 2024년 Dash·Dubey 논문의 상세보기가 정상으로 열렸다. `.modal.quick-look[role=dialog]` 안의 `[data-aid=abstract]`가 전체 초록이며 결과 목록의 축약문과 분리되어 있다. 상세보기에 DOI, 발행일자, 권호, 페이지가 표시된다. Escape로 상세보기를 닫는다.

Dash·Dubey 제목 검색에는 2024년 출판판과 2021년 사전공개본이 함께 나타났다. 대상 DOI `10.1016/j.disopt.2023.100821`이 표시된 2024년 상세보기에서만 대상 초록을 채택했다. 기관 원문 링크는 `https://www-sciencedirect-com.libproxy.knu.ac.kr/science/article/pii/S1572528623000634`로 이어졌으나 CPE00001 오류 화면이었다. 이 화면은 전문이 아니다.

첫 문헌 DOI `https://doi.org/10.1145/3749740.3749756`은 `https://dl.acm.org/doi/10.1145/3749740.3749756`으로 이동한 뒤 Cloudflare 보안 확인 화면에 머물렀다. 이 관찰은 해당 시도에만 적용하며 미시도 문헌의 실패를 뜻하지 않는다.

이 초기 단계에서는 `collect.py`의 독립 실행을 사용했다. 현재는 `resume.py`가 필요한 수집 함수를 호출하고 공통 큐와 검토 상태를 갱신한다.

## 기관 ACM의 확인된 정상 경로

다른 작업자가 실제로 관찰한 `https://dl-acm-org.libproxy.knu.ac.kr/doi/abs/10.1145/2488608.2488677`을 독립 context에서 열어 정상 논문 화면을 재확인했다. 여기의 `input[name=AllField]:visible`에 대상 DOI를 넣고 Enter를 누르면 실제 ACM 검색 결과가 나온다. Lee 1980 DOI 검색은 올바른 제목·저자·쪽수 604–618을 반환했다. 결과의 제목 링크를 따라간 상세보기는 대상 h1·DOI를 보여 주며, PDF 링크를 실제로 제공한다. 그 관찰된 링크를 `context.request.get`으로 수신하자 805,111 bytes의 열리는 15쪽 PDF를 얻었다.

검색결과 화면은 이전 검색 조건을 입력칸 밖 태그에 유지한다. 같은 입력칸을 fill하는 것만으로는 이전 조건이 지워지지 않아 여러 DOI가 연결된 0건 검색을 실측했다. `acm_collect.py`는 문헌마다 위 정상 상세 시작 화면의 빈 전역 검색 폼으로 돌아간다. 문제 시도와 수리 후 단일 DOI 검색 화면은 서로 다른 해시 파일로 보존했다.

ACM의 `#abstracts` 컨테이너는 대상 초록이다. 추천 문헌의 `.issue-item__abstract`는 대상 초록이 아니므로 제외한다. 오래된 논문에서는 대상 HTML 초록 컨테이너가 비어 있어도 PDF에 명시적 ABSTRACT가 존재한다. PDF 초록은 명시적 Abstract/ABSTRACT부터 키워드·분류·Introduction 경계까지 추출하며, OCR 오류가 있거나 경계가 불명확하면 원문 첫 페이지를 렌더해 판독한다.

ACM 원문은 실제 대상 DOI 링크, 첫 페이지 제목·저자·연도와 입력 페이지 범위를 대조한다. OCR·TeX 표기 또는 발행연도 미표시로 기계 검사를 통과하지 못한 파일은 보존한 뒤 수동 판독한다. Torán 1991의 실제 인쇄 쪽수는 753–774이며 입력 752–773과 다르다. Education Forum의 출판사 PDF는 인쇄 13–18쪽을 담되 14쪽이 중복되어 물리적으로 7쪽이다. 이 차이를 결과 JSON에 보존했다.

기관 ACM을 처음 확장한 단계에서는 `acm_collect.py`를 독립 실행했다. 현재 ACM 작업도 `resume.py`에서 인계한다. Summon의 조사 범위에는 실제 비구독 확장 UI `#searchInfoBeyondHoldings`와 `ho=f` 응답을 사용한다. 큰 검색은 제목·저자 필드로 좁히고, 필요한 후속 결과 페이지는 관찰한 UI로 방문한다.

## ScienceDirect 전문 HTML과 원래 수식·그림

확인된 정상 흐름은 Firefox에서 KUDOS 학술DB의 ScienceDirect 바로가기를 열고 실제 제공자 홈페이지의 `#qs`가 나타날 때까지 기다린 뒤, 같은 context에서 문헌별 관측 링크를 여는 것이다. 새 탭을 사용해 앞 문헌의 CAPTCHA·오류 화면을 다음 문헌의 증거로 붙이지 않는다. 초기 Loading 화면과 CPE00001은 전문이 아니다. CPE는 원인 미확인의 콘텐츠 제공 오류로 기록하며, 자료별 정상 상세와 PDF·HTML 제공 상태를 따로 판정한다.

`science_direct.py`의 HTML 경로는 `native_article.py`에서 대상 DOI·제목·저자·날짜와 실제 `#body`, 초록, 절 목록, 참고문헌을 대조한다. `Full text access` 표시만으로 전문을 확정하지 않는다. `resource_snapshot.py`는 실제 MathJax 요소에 대응하는 원래 MathML 입력을 보존하고, 문헌 이미지의 `currentSrc`와 정확히 일치하는 브라우저 응답만 수집한다. `fulltext_html.py`는 이 수식과 내장 그림을 포함한 로컬 HTML을 만든다. `saved_article.py`는 이미 저장한 DOM·원래 MathML·그림 증거를 재사용한다.

오프라인 검증은 본문·초록·제목·참고문헌의 수식, 절과 참고문헌 수, 그림 해상도·로딩, HTTP 요청을 확인한다. 그림이나 서지 차이의 의미 판독은 직접 검토로 남긴다. 0500a5b의 실제 전문은 수식 1,309개, 내장 그림 두 개, 참고문헌 38개와 HTTP 요청 0으로 직접 검증했다. 2bb97c 참고문헌의 단일 Unicode 기울임 k는 동일 파일의 실제 표시를 별도로 읽어 승인했다. 이 수동 판정은 임의의 복잡한 CHTML 수식에 일반화하지 않는다.
