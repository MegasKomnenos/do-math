이 문서는 g02가 실제 화면에서 관찰한 인터페이스다. 실행·완료 계약은 contract.md와 restart-contract.md이며, 관찰을 다른 문헌의 성공이나 제한으로 복제하지 않는다.

KUDOS 학술DB 화면은 https://kudos.knu.ac.kr/pages/sub.htm?nav_code=kud1641346542 이다. #search_order에 DB명을 넣고 Enter를 누른 뒤 대응 바로가기를 클릭한다. 새 context는 assignment의 보호 bootstrap을 읽는다. 로그인·쿠키·인증 헤더는 원자료에 기록하지 않는다.

MathSciNet은 관측한 기관 경유 publications-search에서 #searchTextInput에 MR을 입력하고 Enter를 누른다. 상세의 해당 MR h1이 실제 표시될 때까지 기다린 뒤, 단일 MR은 main, 공동 서평의 여러 MR은 해당 h1을 포함하는 div.article로 서지를 한정한다. 표제·저자·연도·판본·쪽을 검토하고 Article 연결을 조사한다. Review PDF와 공유 서평은 논문/책 전문이 아니다.

Summon은 https://knu.summon.serialssolutions.com/ko-KO/search?ho=t&q= 에서 시작한다. #ho0에 Space를 누르고 checked를 확인해 비구독 포함 ho=f를 사용한다. 보이는 input[id^=searchBox_]와 같은 form의 검색 submit 버튼을 사용한다. 실제 제출에는 500ms leading debounce가 있으므로 550ms 이상 간격을 둔다. UI가 발생시킨 /api/search 응답을 수신하며 직접 API를 호출하지 않는다. query.original_query와 query_string의 s.ho=f를 대조한다.

검색 완료 표시가 중복될 수 있어 Done Loading Results의 첫 일치 요소를 기다린다. 다음 페이지는 보이는 a[aria-label="다음"]이다. 응답 뒤 이 링크가 다시 표시될 때까지 기다린다. Digraphs 제목·저자·연도 검색의 55건을 25+25+5로 실제 순회했다. 결과 수는 서비스 중 갱신될 수 있으므로 실제 관찰한 응답과 처리 수를 보존한다.

대응 Summon 행의 link/fulltext_link/link_to_html, MR Article, 입력 source_urls를 출처 작업으로 연결한다. 자료 페이지에서 실제 관측한 PDF·원문 링크를 조사한다. Chrome이 PDF 응답 대신 작은 viewer 문서를 body로 반환할 수 있다. Duke의 ambrosio.pdf는 content-type application/pdf와 약 2MB Content-Length에도 body 536바이트를 반환했다. 그 브라우저 응답에서 관측한 동일 URL을 context.request.get으로 받아 정상 342페이지 PDF를 회수했고 실제 실패·통과 시험을 남겼다.

Springer는 KUDOS의 Springer 바로가기로 기관 연결을 확인했다. Digraphs 상세에는 Kyungpook 표시가 있어도 subscription preview가 나타났고, 제공된 다운로드는 bfm/bbm 앞·뒤 부속 자료였다. 이 파일을 전체 원문으로 세지 않는다. IEEE 418, 소스 HTTP 500, 빈 렌더링, 접근 제한은 서로 다른 관찰로 남긴다. 특정 handle을 찾을 수 없다고 명시한 응답은 그 링크의 실패이며 다른 출처에 복제하지 않는다.

공개 검색은 단서를 찾는 수단이고 회수·문헌 검증은 실제 UI와 관측 링크에서 수행한다. RSL의 Vorobev 1973 상세는 정확한 서지를 제공했지만 실제 화면에 온라인 열람이 없었다. 숨은 Читать онлайн 링크의 href=#를 다운로드 경로로 사용하지 않는다. BMSTU의 2002년 상세에서 관련문헌의 1973년 подробнее를 실제 클릭해 /Catalog/Details/311031로 이동했다. 그 페이지의 주 서지와 Аннотация부터 УДК 직전까지가 1973년 판본의 서지와 초록 구획이다.
