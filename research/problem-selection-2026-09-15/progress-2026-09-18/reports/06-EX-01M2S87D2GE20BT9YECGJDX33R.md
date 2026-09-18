과제 TK-01M2S813V9WRDCV05M42DK0TH1(S1 추측 6.5 해결 문헌의 현재성 재확인)을 2026-09-18 03:16–03:25 UTC에 수행했다. 상세 보고서는 evidence/검색-보고서.md, 호출 목록은 evidence/search-log.json이다. scholarly 원 응답 63건은 scholarly-data/manifests·blobs에 보존되어 있다.

0. 대상 확인. 입력 S1 저자 공개본(input/sources/0037-statistics-interval-parking-2025.pdf, sha256 ee0da697…)의 23쪽 §6 끝에 Conjecture 6.5가 있다. 같은 쪽의 정의 IPF_n(ℓ)^max={α∈PF_n: maxdisp(α)=ℓ}에 따라 a_ℓ=b_{n,ℓ}이다. 결론 'c∈{0,…,n−1}이 존재해 a_0≤…≤a_c≥…≥a_{n−1}'도 목표 P와 같은 명제다.

1. 판본(완료 기준 1). scholarly arXiv fetch(id_list=2507.07243)는 totalResults=1이고 최신 판본 2507.07243v1(2025-07-09T19:27:41Z, journal-ref 없음)을 반환했다(원 Atom artifact 5bde14e8…). v2 직접 요청은 HTTP 429로 실패했다(artifact e5f95556…). arXiv abs 페이지(WebFetch)도 판본 이력에 v1 하나만 표시한다. 저자 공개 PDF(jeremymartinmath.github.io/papers/StatisticsLIPF.pdf)를 scholarly author-repository로 다시 받았고, sha256 ee0da697…로 입력 원자료와 바이트가 같았다(artifact f1947e09…). 저자 논문 목록(최종 갱신 9/15/26)에는 'Preprint (7/9/25)', GRWC 목록에는 'submitted'로 표시된다. Crossref 제목+저자 검색 상위 10건에 S1의 저널 등록본은 없었다. 결론: 조회 범위에서 새 판본이나 게재본은 없다.

2. 인용 조회(완료 기준 2). 세 자료원에서 조회했다. Semantic Scholar citations(ARXIV:2507.07243, limit 100)는 received=0, total=null이었다. OpenAlex filter cites:W4416284076는 0건이었고, 레코드의 cited_by_count도 0이다. OpenCitations citations(doi:10.48550/arXiv.2507.07243)도 0건이었다. OpenAlex가 S1의 referenced_works도 0으로 색인하고 있어 인용 그래프가 불완전함이 분명하다. 따라서 0건을 '인용 문헌 부재'로 확대하지 않는다.

3. 동의어·추측명 검색(완료 기준 3). 사용한 검색은 다음과 같다. arXiv API abs:"parking functions" AND (abs:displacement OR abs:unimodal)는 3회 429 뒤 성공해 11건 전체를 반환했다. arXiv 웹 검색은 '"parking functions" displacement' 9건, 'parking unimodal' 5건, '"interval parking"' 11건이었다. zbMATH는 'parking & displacement' 15건, 'ti:parking & ti:interval' 9건, 'parking & unimodal' 4건이었다. OpenAlex는 세 검색식에서 각 21·21·14건, Crossref 제목 검색은 50건 창, Semantic Scholar bulk는 3건이었다. Mwmbl은 0건이었고 WebSearch 4건도 수행했다. 결과 창과 선별 근거는 보고서 §3 표에 있다. 선별 기준은 (a) 2025-07-09 이후 문헌, (b) 주차 함수의 최대 변위·ℓ-interval·단봉성을 다루는지, (c) 제목·초록에 해결 주장이 있는지다. 확률적 주차(Rényi형)·흡착, 차량 주차 등 동음이의 결과는 대상이 달라 제외했다.

4. 대조와 판정(완료 기준 4). S1 이후의 후보 문헌을 대조했다.
- arXiv:2601.20770v1(Harris 외, 2026-01): PDF 전문을 추출해 보존했다(evidence/arxiv-2601.20770v1.pdf, sha256 f7282c3a…). 본문에 'maximum/maximal displacement', 'unimodal', 'log-conc', 'conjecture'가 없고, 참고문헌 15건에 S1이 없다. 총변위 통계를 다룬다.
- arXiv:2607.01273v2와 2511.01997: 단위 구간(ℓ=1) 부분족의 열거를 다룬다.
- Stanley–Yin 'Some enumerative properties of parking functions', AAM 2025 새 통계 분포, 'Bounded Linear Probing Hashing'(AofA 2026), Shuffle-compatibility, Lehmer, Naples(EJC 2026-09-11): 초록을 대조했다.
- 2603.19194v2, 2508.11587, 2609.05131: 준비 단계에서 전문 독해한 판정을 유지했다.
모두 P의 증명·반증·부분 해결을 주장하지 않는다. 판정은 '조사 범위에서 S1 추측 6.5(=P)의 해결·반증·부분 해결 문헌과 S1 새 판본 미발견(2026-09-18 기준)'이다. 이 결과는 새로움 판정의 기준일을 2026-09-18로 갱신하는 근거이며, 해결 문헌이 없다는 보증은 아니다.

5. 미조사·실패 범위. scholarly arXiv 호출은 8회 중 2회만 성공했다(429·timeout). v2 직접 요청과 'interval parking' API 검색은 실패해 웹 검색 페이지로 대신했다. Semantic Scholar 관련도 검색 1건은 429였다. MathSciNet·Scopus·WoS 등 인증 자료원과 Google Scholar식 전문 인용 검색은 수행하지 않았다. 그러므로 본문에서만 추측 6.5를 언급하는 문헌은 놓쳤을 수 있다. 2607.01273·2511.01997·Stanley–Yin 등은 초록만 대조했다. WebFetch/WebSearch 응답은 요약이라 원 바이트를 보존하지 못했으나(2601.20770 PDF 제외), 핵심 사실(판본 v1, 인용 0건, 저자 PDF 동일)은 scholarly artifact로 따로 확인했다. 해싱 분야 문헌은 계약상 별도 과제(TK-01M2S813V989Y3X1GN5NKQBDEX)의 범위다. Stanley–Yin 논문이 Pollak 원형 논증을 쓴다는 점은 그 과제의 참고 단서로 적어 둔다.

6. 보존(완료 기준 5). evidence/검색-보고서.md, evidence/search-log.json, evidence/arxiv-2601.20770v1.pdf/.txt, scholarly-data/(manifest 63건과 blob)를 보존했다. 이 과제는 비형식 과제이며 Lean 결과가 없다.