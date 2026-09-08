g02 작업은 진행 중이며 전체 완료가 아니다. 완료 조건은 배정 5,138건 전부의 결과, 현재 의미 검토, 남은 작업 0, 공통 전체 검사 passed=true/complete=true다. g02의 worker/raw/private root만 수정한다. Git과 공통 계약·검사기는 루트 작업자 소유다.

현행 생산은 shard0 PID20148(runs/20260908T232335Z-20148.json), shard1 PID45720(runs/20260908T232554Z-45720.json)이다. 각각 원입력 위치 기준 2,569건을 소유하며 두 새 context 모두 로그아웃 표시로 인증 재사용을 확인했다. 로그는 runs/shard-0-book-review-production.log와 shard-1-book-review-production.log다. 재개할 때 실제 PID를 다시 확인한다. 이전 PID28060/45292는 원자 저장 오류 수리 경계에서, PID13992/22056은 한국어 초기화 화면 수리 경계에서 종료됐다. 실행 중 모듈이나 소유 결과를 다른 흐름이 수정하지 않는다.

진입점은 resume.py이며 원입력의 고정 분할을 결과 로드 전에 적용한다. 전체 실행은 미처리 후보를 먼저 조사한 뒤 기존 결과의 잔여 작업을 처리한다. 전역 진행은 snapshot_progress.py가 고유 paper_id로 집계한다. shard 진행 파일의 전체 수를 더하지 않는다. --saved-only --reassess는 완료 표시를 포함해 저장 증거를 재판정한다. 공통 검사 stdout은 파일로 보존하고 작은 요약만 출력한다.

과거 19:59 UTC 관측은 tdd/readiness-quality-regression.txt의 비실물 회귀 128개 통과와 runs/20260908T195945Z-44808.json의 저장 결과 956건 재판정/부분검사 exit0이다. 그 직후 전역 집계는 초록499, 원문4, 미처리4182, 저장 결과 잔여946, 전체 잔여 문헌5128이었다. 최신 수량은 진행 파일과 결과에서 다시 읽는다.

최근 실제 수리: no_resource를 접근 제한과 분리하고 uris/open_access_link를 저장된 완전 관측 문서에서 복원했다. selected-summary-decisions.json은 직접 읽은 DB 선정 인용을 출처/인용 해시에 결박하며 실제 resume에 연결돼 있다. abstract-content-decisions.json은 짧은 원시 값 중 목차·서지·서평·불확실 수식/발췌의 직접 판독을 결박한다. No detailed description placeholder, 전체 라이선스 안내, 기여자 안내는 초록으로 올리지 않는다. 정상 짧은 요약과 요약에 덧붙은 권리 문구는 유지한다. abstract-notices-impact.json에 11개 원시 값의 철회/재판정 이력이 있다.

De Gruyter의 HTTP202 초기 화면은 네비게이션 세 줄뿐일 수 있다. 실제 h1 또는 관측 PDF가 나타날 때까지 기다리며, 네비게이션 응답들의 실제 상태를 따로 기록한다. 과거 done 초기화 화면은 inventory가 retry로 다시 연다. 이 수리의 실제 green은 Epstein2012의 38쪽 PDF와 인쇄 Abstract 이미지다. mixed_source_scope.py는 실제 출판사 제한과 소진된 no_resource/특정 handle 부재 경로의 역할을 구별하며, 미방문 경로나 미판독 PDF가 있으면 음성을 닫지 않는다.

19:59 UTC에 확보했던 원문 네 가지는 Gradient flows(342쪽 책, 마지막 인쇄333), Viana interval exchange maps(94쪽 논문,7–100), Ciarlet differential geometry/elasticity(215쪽 논문 DOI 범위1–215), Epstein closure operations(38쪽 파일, 인쇄1–37와 빈38)이다. Ciarlet의 별도 foreword와 재조판 단행본을 혼합하지 않는다. Epstein의 인쇄 Abstract 이미지는 abstract-region-e5fda1993690990c.png다. Gradient의 훼손 Summon 값 철회와 별도 정상 MR 선정 요약은 서로 다른 출처로 보존한다.

checkpoint_apply.py는 두 수집기 중단 상태에서만 실행한 일회성 적용 기록이다. runs/20260908T194721Z-46112.json에 partial-pdf-decisions.json의7개 PDF 부속자료 판독, public-supplement-followups.json의 출처 연결, Ross1987의 독립 not_found 판독 적용을 기록했다. 원 결정 파일의 pending 표시는 적용 전 문서의 상태이며 실제 적용 정본은 이 manifest와 results다. Ross는 현재 두 항목 not_found/잔여0이다. 새 데이터가 나타나면 이전 음성을 덮어쓰기 전에 그 자료를 먼저 읽는다.

남은 직접 검토: Fine1986의 Summon 수식은 (√5−1) 뒤 줄의2가 분수인지 불명확하여 철회/검토로 열었다. MR0826667은 독립 서평이므로 대체 초록이 아니다. g05/science_direct.py의 abstract_html과 #abstracts 내부 Abstract 부모 컨테이너 보존, test_science_direct.py 및 g05의 실제 MathML fixture가 참고 경로다. 해당 코드는 읽기만 하며 g02에 연결할 때 실제 g02 입력·DOM으로 시험한다. 수식을 평문에서 추측 복원하지 않는다.

공개 보완으로 Kelly2005의 TAC 상세와 Rochester PDF, Banach Spaces II1979의 도서관/합본 PDF, Tadmor 책의 Cambridge 상세를 관측해 출처 작업에 연결했다. Kelly의 오자 수정일과 원판, Banach 합본 내 Part II, Tadmor의 입력2013 대 출판사2011/2012를 실제 UI/PDF로 대조해야 한다. 아직 확보로 선언하지 않는다. URL없음/MR Article없음/Summon0 음성 분기는 루트 계약의 제목·저자/확인 발행정보 공개 보완을 끝낸 뒤 닫는다.

루트가 보호 bootstrap을 갱신한다. 새 context에서 현재 파일을 읽고 로그아웃 표시를 확인하며 값은 출력하지 않는다. Chrome ScienceDirect CPE는 Firefox의 정상 KUDOS gateway와 해당 공개/기관 경로를 확인하기 전 종결 근거가 아니다. 최근 5xx는 개별 hdl.handle.net 문서의 cannot-be-found 본문이었다. 본문/API의 요청 제한이 늘면 한 흐름으로 줄인다. 그 전에는 허용된 두 고정 흐름을 유지한다.

최근 범위 수리 정본은 scoped_links.py와 scope_prune.py다. source-scope-final-regression.txt의142회귀, runs/20260908T211735Z-43476.json의 실제2문헌 수집/부분검사exit0을 통과했다. Springer 참고문헌 Article, Wiley linkLocation=Reference, Perlego 관련 제품 -pdf slug, Europe PMC 전역 FTP/PDF 디렉터리로의 확장을 제외한다. 기존6결과의무관한 발견작업56,168개와파생파일검토는 원 증거/이유와 함께 not_needed로 보존했다. 최초발견 수와중단 시전체 수, 실행 단계/SDK다운로드하한은 scope-expansion-impact-before.json에 있다. 정확한 과거 SDK재시도 수는 복구할 수 없어 하한으로만 보고했다.

반복수리에서 부모 출처 증거를 자식 산출물로 취급하지 않도록 scope_original_evidence_paths와원출처 제외를 적용했다. inventory와reopen_cpe_routes는 scope_relation=unrelated를 건너뛴다. 이를 빠뜨렸을 때 Swanson 한 건에서7.39GB의동일 증거를 다시 읽는 비용이 실제로 생겼다. 이후 단계별 source_visits/download_attempts/pdf_responses/new_pdf_files 차이를 request_metrics에 기록한다.

공개 자료2개의Save chapter인증성 query는 제거했다. 원본은g02보호.credentials에만보존한다. 정제본은 fixtures/springer-scope-links-5f3a22b10ef1df0e.json 및Ciarlet의ciarlet-official-article-links-86e0ddb2acc11feb.json이다. 모든g02공개참조/해시를갱신했고 실제_csrf/Save chapter방문0건을확인했다. session-query-redaction-audit.json을참조한다.

공용bootstrap은루트가2026-09-08T21:13:22Z에갱신하고독립Chrome/Firefox재사용을확인했다. 이후실제수집시험을통과했다. 앞선로그인만표시된상태를자료접근제한으로기록하지않았다.

2026-09-08 22:48 UTC 재개 단위: copyright_notice.py를 pdf_review에 연결했다. 명시적인 판권 줄의 연도 집합이 배정 연도 하나일 때만 인정하며 출판사명은 연도와 기호 사이에 올 수 있다. extent/title/ISBN/끝쪽 기준은 완화하지 않았다. literal_references.py로 명시적인 References 구획 안의 그대로 표시된 URL을 기존 scope_prune에 추가했고 Tall2025가 인용한 College Board/Keisler 직접PDF를 대상외로 처분했다.

book-checkpoint-regression.txt의156회귀와1128결과 재판정/부분검사exit0(20260908T224318Z-15612.json)을 통과했다. Micromechanics2018의723쪽 전체책을 직접 구성 검토 proof와 함께found/남은작업0으로 적용했다. micromechanics-completeness-proof.json에는 표지1+구성722쪽, 목차 공백1곳 차이, publisher page-label의 번호간격을 기록했다. root의 operator-checks/micromechanics-root-review.json도 이를 지지한다.

범위 회귀의 실시간 results 의존을 제거했다: scope-record-cases-f106b6ef0289c5af.json(3문헌/12작업), whole-book-control-dbf7894651333359.json, literal-reference-tasks-d4c6d0f16a783a20.json은고정원자료다. 당시142시험 snapshot은46ae527(M-0147)에보존되어있고후속156시험단위는별도다. original_title.py/test_original_title.py는원출처해시/TeX스타일을검증하는독립5시험준비본이며현재수집흐름에연결하지않았다.

22:48 UTC 확보 원문은 앞의 네 가지에 Micromechanics2018(723쪽)와 Ocean Wave Energy Conversion2017(305쪽, 마지막 E1 정오표 포함)을 더한 여섯 가지였다. 현재는 Moonshine1998의 공식 출판 원문을 더한 일곱 가지다. Ocean Wave의 실제 판권은 편집자/저자 ©2017이며 입력 ISBN·제목·편집자와 마지막 페이지를 대조했다. ocean-wave-book-review.json에 그 검토를 보존했다. 22:48 UTC 판본의 전체 156시험과 독립 original_title 시험 준비본은 루트가 e8cd7a0(M-0149)에 보존했다.

후속 저장 수리는 run.py의 원자적 결과 교체에만 적용했다. PermissionError에 한해 최대 6회 시도하고 총 3.1초를 기다린다. 영구 오류는 기존 JSON과 새 임시본을 남긴 채 상위로 전달한다. 다른 파일 오류는 재시도하지 않는다. atomic-store-red.txt의 실제 실패와 atomic-store-green.txt의 3시험, atomic-store-regression.txt의 전체 159시험이 근거다. VER-3965d82460c7c949f9755f39의 기존/임시 결과는 runs/atomic-store-crash-prior-*.json 및 pending-*.json에 해시 이름으로 보존했다. 같은 ID, 기존 시도·증거 보존, 공통 validate_record 오류 0을 확인한 뒤 새 시도 1개와 증거 2개가 담긴 임시본을 결과로 복구했다. 운영체제가 접근을 거절한 구체 원인은 확인하지 못했다.

23:23 UTC 수리 단위는 tdd/book-review-regression.txt의 166시험을 통과했다. 한국어 초기 화면 단독 문구 불러오는 중...를 retry로 판정하고 실제 본문 전환을 최대30초 기다린다. 영향16문헌/77작업을 모두 다시 열었다. 실제 pilot은 같은6출처에서 정상 EBSCO Sandholm2011 상세·설명·ISBN으로 전환됐다(runs/20260908T231537Z-19940.json). 이용하기(eBook) 버튼의 reader/다운로드 후속 UI는 아직 열려 있다. g08이 전달한 루트 실물은 #ebook-toc-lp_Cover-label 대기 후 다운로드, 전체 eBook의 MyEBSCO 별도 개인 로그인과 챕터 선택 combobox 경로이며 자동으로 기관 권한 부재를 선언하지 않는다.

Book Review를 Book 부분 문자열로 통과시킨 유형 오류를 고쳤다. Book/eBook/Book Chapter 실제 양성, Book Review와 혼합 태그 음성, 정상 reviews 연구문구 양성을 고정 fixture로 검증했다. 직접 서평 안내 한 문장은 abstract-content-decisions.json의 원문 해시로만 분류한다. 영향은2문헌/서평 출처8개였고 기존 문서·잘못된 값·철회 이력을 보존했다. runs/20260908T232048Z-17788.json은 완료 표시까지 포함한1200결과 재판정/부분검사exit0이며, 후속 직접 적용은 runs/20260908T232311Z-18960.json이다.

Moonshine의 공식 EMS 장 PDF fulltext-candidate-e57d3e3837d3a5bb.pdf는10쪽이다. 실제 제목·저자·1998 ICM/Documenta 표기, 본문607–615의 연속 페이지·끝 참고문헌/저자주소를 읽었고616은 머리말/꼬리말 외에 내용이 없는 빈 페이지임을 이미지로 확인했다. moonshine-fulltext-decision.json에 결박해 fulltext found/남은작업0으로 반영했다. 8쪽 arXiv v1과 전체664쪽 수록집은 별도로 보존했다. 23:24 UTC 고유 결과 집계는1200결과,미처리3938,초록631,원문7,저장결과잔여1185,전체잔여문헌5123이었다.

다음 정상 체크포인트의 별도 판독 자료는 book-parts-second-review-decisions.json(20개 저장 부속자료)이다. 실행 중 결과에는 아직 반영하지 않았다. 대부분 표제/목차·챕터·부록이며 Micromechanics 구성7개는 이미 완전판 구성 검증 근거다. Pascucci 책의 도서관 상세가 연결한 Schwarze 독일법학 목차PDF와 Cyberlibris 이용약관PDF는 실제 다른 내용으로 확인했다. 원문이나 초록을 확보했다고 올리지 않는다.
