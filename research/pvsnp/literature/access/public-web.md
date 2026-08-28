# 공개 웹 접근 조사

## 판정 기준과 재추출

조사 시각은 UTC다. 요청 경로 `직접 GET`은 원자료 URL에 `curl -L`로 본문을 요청했다는 뜻이다. `대체 GET`은 제목과 DOI로 공개 저자본·기관 저장소를 검색한 뒤 후보 원문을 같은 방식으로 요청했다는 뜻이다. `PUBLIC_PASS`는 원자료 URL 또는 확인한 대체 URL이 크리덴셜 없이 의도한 페이지나 원문을 반환했음을 뜻한다. DOI가 원문 파일 대신 서지·초록 페이지, 발행처 연결 페이지, 발행처 장 페이지만 반환하면 공개 원문 접근으로 세지 않았다. `PUBLIC_FAIL`은 직접 경로와 대체 공개본 검색에서 원문을 확인하지 못했음을 뜻한다.

원자료 `C:\math\research\p-vs-np-statement-and-prior-work.md`의 Markdown 인라인 링크를 정규식 `\[[^\]]*\]\((https?://[^)]+)\)`로 다시 추출했다. 링크 출현은 70건이고, 첫 출현 순서를 보존한 고유 URL은 22건이다. 아래 `L01`~`L22`는 기준선 표의 번호가 아니라 이 재추출 순서다.

## 22행 대응표와 접근 판정

| ID | URL | 원자료 문헌 좌표 | 시도 시각 | 요청 경로와 응답 또는 실패 증거 | 대체 공개본 탐색 결과 | 판정 | 판독 기록 좌표 |
|---|---|---|---|---|---|---|---|
| L01 | https://www.claymath.org/millennium/p-vs-np/ | 5행, CMI P vs NP 현행 페이지 | 2026-08-25T06:35:32.7469417Z | 직접 GET → HTTP 200, HTML, 107,440바이트, 리디렉션 0회 | CMI 도메인·제목 검색. 별도 대체본은 필요하지 않았고 공식 페이지가 직접 열렸다. | `PUBLIC_PASS` | `research/pvsnp/literature/records/L01.md` |
| L02 | https://www.claymath.org/millennium-problems/ | 5행, CMI Millennium Prize Problems 목록 | 2026-08-25T06:35:34.8832915Z | 직접 GET → HTTP 200, HTML, 88,917바이트, 리디렉션 0회 | CMI 도메인 검색. 공식 목록이 직접 열렸다. | `PUBLIC_PASS` | `research/pvsnp/literature/records/L02.md` |
| L03 | https://www.claymath.org/wp-content/uploads/2022/06/pvsnp.pdf | 7행, Stephen Cook의 공식 문제 설명 | 2026-08-25T06:35:37.2171564Z | 직접 GET → HTTP 200, PDF, 176,204바이트, 리디렉션 0회 | Cook의 University of Toronto 홈페이지에서도 CMI 원고의 PostScript 연결을 확인했다. 판독에는 CMI 공식 PDF를 사용했다. | `PUBLIC_PASS` | `research/pvsnp/literature/records/L03.md` |
| L04 | https://doi.org/10.1007/978-1-4684-2001-2_9 | 51행, Karp (1972) | 2026-08-25T06:35:38.8633154Z | 직접 GET → Springer 최종 URL, HTTP 200, HTML, 224,171바이트, 리디렉션 5회. 발행처 장 페이지다. | 제목·DOI 검색 → George Washington University 공개 PDF `https://www2.seas.gwu.edu/~simhaweb/champalg/tsp/papers/KarpOriginal.pdf`; 2026-08-25T06:38:23.6054963Z GET, HTTP 200, PDF, 10,879,201바이트. | `PUBLIC_PASS` | `research/pvsnp/literature/records/L04.md` |
| L05 | https://doi.org/10.1145/800157.805047 | 53행, Cook (1971) | 2026-08-25T06:35:41.5015280Z | 직접 GET → ACM 최종 URL, HTTP 403, HTML, 45,218바이트, 리디렉션 2회. | 저자명·제목 검색 → University of Toronto 저자 홈페이지 PDF `https://www.cs.utoronto.ca/~sacook/homepage/1971.pdf`; 2026-08-25T06:38:32.6284306Z GET, HTTP 200, PDF, 3,195,533바이트. | `PUBLIC_PASS` | `research/pvsnp/literature/records/L05.md` |
| L06 | https://doi.org/10.2307/2273702 | 67행, Cook–Reckhow (1979) | 2026-08-25T06:35:42.2899687Z | 직접 GET → Cambridge 최종 URL, HTTP 200, HTML, 822,151바이트, 리디렉션 3회. 초록 페이지다. | 저자명·제목 검색 → University of Toronto 저자본 `https://www.cs.utoronto.ca/~sacook/homepage/cook_reckhow.pdf`; 2026-08-25T06:38:35.0892973Z GET, HTTP 200, PDF, 393,905바이트. | `PUBLIC_PASS` | `research/pvsnp/literature/records/L06.md` |
| L07 | https://www.claymath.org/millennium-problems/rules/ | 73행, CMI 상금 규칙 | 2026-08-25T06:35:45.2588484Z | 직접 GET → HTTP 200, HTML, 79,319바이트, 리디렉션 0회 | CMI 도메인 검색. 공식 규칙 페이지가 직접 열렸다. | `PUBLIC_PASS` | `research/pvsnp/literature/records/L07.md` |
| L08 | https://doi.org/10.1145/321864.321877 | 81행, Ladner (1975) | 2026-08-25T06:35:46.9877584Z | 직접 GET → ACM 최종 URL, HTTP 200, HTML, 141,889바이트, 리디렉션 1회. 서지·초록 페이지다. | 제목·DOI·저자 PDF 검색. Mendeley 서지 페이지는 2026-08-25T06:38:36.5410329Z HTTP 200 HTML만 반환했다. 원 논문 공개 PDF는 확인하지 못했다. | `PUBLIC_FAIL` | `research/pvsnp/literature/records/L08.md` |
| L09 | https://doi.org/10.1145/2559903 | 89행, Williams (2014) | 2026-08-25T06:35:49.5421223Z | 직접 GET → ACM 최종 URL, HTTP 403, HTML, 5,500바이트, 리디렉션 1회. | 원자료의 바로 다음 저자 공개본 L10을 확인했다. L10은 HTTP 200 PDF다. | `PUBLIC_PASS` | `research/pvsnp/literature/records/L09.md` |
| L10 | https://www.cs.cmu.edu/~ryanw/acc-lbs-ccc.pdf | 89행, Williams 저자 공개 원고 | 2026-08-25T06:35:50.1489226Z | 직접 GET → HTTP 200, PDF, 357,396바이트, 리디렉션 0회 | 제목·저자 검색도 같은 CMU 저자 PDF를 반환했다. | `PUBLIC_PASS` | `research/pvsnp/literature/records/L10.md` |
| L11 | https://doi.org/10.1016/0022-0000%2882%2990002-2 | 93행, Mahaney (1982) | 2026-08-25T06:35:52.8618475Z | 직접 GET → Elsevier linkinghub, HTTP 200, HTML, 2,689바이트, 리디렉션 1회. 발행처 연결 페이지다. | 제목·DOI·저자 PDF 검색. ScienceDirect 후보는 2026-08-25T06:38:41.3657019Z HTTP 403 HTML을 반환했다. 공개 저자본·기관 원문은 확인하지 못했다. | `PUBLIC_FAIL` | `research/pvsnp/literature/records/L11.md` |
| L12 | https://doi.org/10.1006/jcss.2000.1727 | 105행, Impagliazzo–Paturi (2001) | 2026-08-25T06:35:54.0731247Z | 직접 GET → Elsevier linkinghub, HTTP 200, HTML, 2,642바이트, 리디렉션 1회. | 제목·저자 검색 → UC San Diego 저자본 `https://cseweb.ucsd.edu/~paturi/myPapers/pubs/ImpagliazzoPaturi_2001_jcss.pdf`; 2026-08-25T06:38:41.5402292Z GET, HTTP 200, PDF, 116,938바이트. | `PUBLIC_PASS` | `research/pvsnp/literature/records/L12.md` |
| L13 | https://doi.org/10.1137/0204037 | 112행, Baker–Gill–Solovay (1975) | 2026-08-25T06:35:55.2176771Z | 직접 GET → SIAM 최종 URL, HTTP 200, HTML, 418,971바이트, 리디렉션 1회. 발행처 페이지다. | 제목 검색 → University of Colorado Denver 기관 PDF `https://cse.ucdenver.edu/~cscialtman/complexity/Relativizations%20of%20the%20P%3DNP%20Question%20%28Original%29.pdf`; 2026-08-25T06:38:43.3174785Z GET, HTTP 200, PDF, 1,543,240바이트. | `PUBLIC_PASS` | `research/pvsnp/literature/records/L13.md` |
| L14 | https://doi.org/10.1006/jcss.1997.1494 | 114행, Razborov–Rudich (1997) | 2026-08-25T06:35:57.2859302Z | 직접 GET → Elsevier linkinghub, HTTP 200, HTML, 2,630바이트, 리디렉션 1회. | 제목·저자 검색 → Steven Rudich의 CMU 저자 페이지와 `https://www.cs.cmu.edu/~rudich/papers/natural.ps`; 2026-08-25T06:38:45.4800463Z GET, HTTP 200, PostScript, 232,411바이트. 같은 논문의 ECCC 공개 기술보고서 PDF `https://eccc.weizmann.ac.il/report/1994/010/download/`도 대체 공개본으로 확인하고 판독했다. 2026-08-26T08:23:24.711845Z에 ECCC TR94-010 PDF를 다시 GET했다. 최종 URL은 `https://eccc.weizmann.ac.il/report/1994/010/download/`였다. HTTP 200, `application/pdf`, 380,659바이트, 리디렉션 0회였다. | `PUBLIC_PASS` | `research/pvsnp/literature/records/L14.md` |
| L15 | https://doi.org/10.1145/1490270.1490272 | 116행, Aaronson–Wigderson (2009) | 2026-08-25T06:35:58.5782539Z | 직접 GET → ACM 최종 URL, HTTP 403, HTML, 5,596바이트, 리디렉션 2회. | 원자료의 바로 다음 저자 공개본 L16을 확인했다. 2026-08-25T06:38:47.3842613Z 재검에서도 HTTP 200 PDF였다. | `PUBLIC_PASS` | `research/pvsnp/literature/records/L15.md` |
| L16 | https://www.scottaaronson.com/papers/alg.pdf | 116행, Aaronson–Wigderson 저자 공개 원고 | 2026-08-25T06:35:59.3608442Z | 직접 GET → HTTP 200, PDF, 491,873바이트, 리디렉션 0회 | 제목·저자 검색도 같은 저자 PDF를 반환했다. | `PUBLIC_PASS` | `research/pvsnp/literature/records/L16.md` |
| L17 | https://theory.cs.princeton.edu/complexity/book.pdf | 128행, Arora–Barak 공개 초고 | 2026-08-25T06:36:00.7896033Z | 직접 GET → HTTP 200, PDF, 4,572,986바이트, 리디렉션 0회 | 제목·저자·Princeton 도메인 검색. 공식 저자 공개 초고가 직접 열렸다. | `PUBLIC_PASS` | `research/pvsnp/literature/records/L17.md` |
| L18 | https://zenodo.org/records/15095752 | 134행, SAT Competition 2024 데이터셋 | 2026-08-25T06:36:03.6919187Z | 직접 GET → HTTP 200, HTML, 62,121바이트, 리디렉션 0회 | Zenodo 기록명 검색. 공식 공개 기록 페이지가 직접 열렸다. 4.3 GB 파일 묶음은 이 접근 조사에서 내려받지 않았다. | `PUBLIC_PASS` | `research/pvsnp/literature/records/L18.md` |
| L19 | https://satcompetition.github.io/2026/ | 134행, SAT Competition 2026 안내 | 2026-08-25T06:36:05.4384503Z | 직접 GET → HTTP 200, HTML, 5,723바이트, 리디렉션 0회 | 행사명·연도 검색. 공식 GitHub Pages 안내가 직접 열렸다. | `PUBLIC_PASS` | `research/pvsnp/literature/records/L19.md` |
| L20 | https://uds-psl.github.io/cook-levin/ | 138행, Gäher–Kunze Coq/Rocq 자료 | 2026-08-25T06:36:05.8656379Z | 직접 GET → HTTP 200, HTML, 5,174바이트, 리디렉션 0회 | 제목·저자 검색. 공식 프로젝트 페이지가 직접 열렸다. 공개 저장소 `https://github.com/uds-psl/cook-levin`에 2026-08-26T08:23:46.4822893Z `git ls-remote --symref <repository> HEAD`를 실행했다. exit 0으로 성공했고, `HEAD`와 `refs/heads/paper-cook-levin`은 판독 커밋 `e24a92af25746f6758a09ea1dc51e57491508e60`을 반환했다. | `PUBLIC_PASS` | `research/pvsnp/literature/records/L20.md` |
| L21 | https://isa-afp.org/entries/Cook_Levin.html | 140행, Balbach AFP 자료 | 2026-08-25T06:36:06.1506574Z | 직접 GET → HTTP 200, HTML, 9,788바이트, 리디렉션 0회 | 항목명·AFP 검색. 공식 Archive of Formal Proofs 항목이 직접 열렸다. 공식 proof document PDF `https://isa-afp.org/browser_info/current/AFP/Cook_Levin/document.pdf`를 2026-08-26T08:23:28.605465Z에 다시 GET했다. 최종 URL은 `https://isa-afp.org/browser_info/current/AFP/Cook_Levin/document.pdf`였다. HTTP 200, `application/pdf`, 4,411,247바이트, 리디렉션 0회였다. | `PUBLIC_PASS` | `research/pvsnp/literature/records/L21.md` |
| L22 | https://github.com/PierreSenellart/descriptive-complexity | 142행, Senellart Lean 4 저장소 | 2026-08-25T06:36:07.5543560Z | 직접 GET → HTTP 200, HTML, 342,527바이트, 리디렉션 0회 | 저장소명·저자 검색. 공개 GitHub 저장소가 직접 열렸다. | `PUBLIC_PASS` | `research/pvsnp/literature/records/L22.md` |

## 공개 웹 실패 목록

`PUBLIC_FAIL` ID의 닫힌 목록은 `L08`, `L11`이다.

## 원문 보관 증거

이 행에서 내려받은 원문은 L03 한 건이다. 저장소 밖 보관 경로는 `C:\math-artifacts\pvsnp-탐사-1\2.7\originals\public\L03-cook-p-vs-np.pdf`다. 파일 크기는 176,204바이트다. SHA-256은 `018f3d473d16c35e807e8cdfbd0bed3ccf7a56452e3e10c6b1d84b56eaf2cf59`다. 저장소에는 외부 원문을 넣지 않았다.

## 한계

HTTP 200은 원문의 공개 접근을 자동으로 뜻하지 않는다. L08과 L11처럼 서지·초록 또는 연결 페이지만 확인된 경우는 실패로 남겼다. 검색은 2026-08-25의 공개 검색 결과와 위 후보 URL에 한정한다. 공개 검색에서 찾지 못한 저자 개인 보관본이 존재할 가능성은 배제하지 않는다.
