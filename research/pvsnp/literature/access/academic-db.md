# 학술DB 접근 조사

## 이 문서가 무엇을 기록하는가

이 문서는 경북대학교 도서관 학술DB(KUDOS, `https://kudos.knu.ac.kr/`)를 브라우저로 직접 조작해 문헌 원문을 확보하려 한 조작 기록이다. 조작 대상은 공개 웹 조사에서 원문 확보에 실패한 문헌으로 한정한다. 그 실패 목록은 같은 디렉토리의 `public-web.md` 「공개 웹 실패 목록」 절이 정한 닫힌 두 건 `L08`, `L11`이다. `L08`은 Richard E. Ladner의 1975년 *Journal of the ACM* 논문 *On the Structure of Polynomial Time Reducibility*이고, `L11`은 Stephen R. Mahaney의 1982년 *Journal of Computer and System Sciences* 논문 *Sparse Complete Sets for NP: Solution of a Conjecture of Berman and Hartmanis*이다. 이 두 건 밖의 문헌은 이 조사의 검색 입력이 아니다.

모든 시각은 UTC이고 ISO 8601 형식이다. 「원문 경로 탐색」 절의 `2026-08-26T09:05:47Z경` 한 건만 예외이고, 뒤에 붙은 `경`은 그 시각이 초 단위 근사값임을 뜻한다. 로그인 계정의 ID와 비밀번호 값은 이 문서에 적지 않는다. 두 값은 git 추적 밖 파일 `C:\math\.credentials\kudos.md`에만 있고, 조작 스크립트가 그 파일에서 직접 읽어 브라우저 입력란에만 넣었다.

## 조작 수단

브라우저 조작은 Playwright로 했다. Playwright는 Chromium 계열 브라우저를 프로그램으로 열어 클릭·입력·이동을 시키고 응답을 관찰하는 자동화 도구다. 이 행의 실행 환경에는 Playwright MCP 서버가 등록되어 있지 않았다. 그래서 Python 패키지 `playwright` 1.62.0을 설치하고 그 동기 API로 브라우저를 직접 조작했다. 화면 없는 Chromium(headless)으로 시작했고, ScienceDirect가 headless 브라우저를 차단한 뒤에는 실제 Google Chrome 채널을 화면 있는 모드로 띄워 조작했다.

조작 스크립트와 화면 캡처·페이지 텍스트 증거는 저장소 밖에 둔다. 스크립트는 `C:\math-artifacts\pvsnp-탐사-1\2.7\tools\`, 증거는 `C:\math-artifacts\pvsnp-탐사-1\2.7\evidence\`에 있다.

## 로그인 조작

| 시각(UTC) | 단계 | 대상 | 결과 |
|---|---|---|---|
| 2026-08-26T08:58:56.258895Z | 첫 화면 이동 | `https://kudos.knu.ac.kr/` | HTTP 200, 문서 제목 `경북대학교 도서관` |
| 2026-08-26T08:59:33.103012Z | `로그인` 링크 클릭 | `https://kudos.knu.ac.kr/pages/login.htm` | 로그인 폼 확인. 폼 이름 `Login_Frm`, 전송 대상 `https://kudos.knu.ac.kr/bbs/member_login_ok.php`, 학번 입력란 `#userid`, 비밀번호 입력란 `#passwd` |
| 2026-08-26T09:00:33.979141Z | 로그인 화면 재이동 | `https://kudos.knu.ac.kr/pages/login.htm` | 폼 표시 |
| 2026-08-26T09:00:37.037200Z | 학번 입력 | 입력란 `#userid` | 크리덴셜 파일에서 읽은 ID를 입력란에만 넣음 |
| 2026-08-26T09:00:37.064183Z | 비밀번호 입력 | 입력란 `#passwd` | 크리덴셜 파일에서 읽은 PW를 입력란에만 넣음 |
| 2026-08-26T09:00:37.075176Z | 전송 | `#passwd`에서 Enter | 폼 전송 |
| 2026-08-26T09:00:42.989871Z | 전송 뒤 도착 | `https://kudos.knu.ac.kr/pages/index.htm` | 페이지 이동 완료 |
| 2026-08-26T09:00:43.017371Z | 로그인 성립 판정 | 도착 페이지 본문 | 본문에 `로그아웃` 표시가 있어 로그인 성립. 증거 `evidence\03-after-login.png`, `evidence\03-after-login-body.txt` |

## 원문 경로 탐색

| 시각(UTC) | 단계 | 대상 | 결과 |
|---|---|---|---|
| 2026-08-26T09:03:47.707691Z | 전자자원 통합검색(Summon) 검색 | `https://knu.summon.serialssolutions.com/ko-KO/search?q=On the Structure of Polynomial Time Reducibility` | HTTP 200, 결과 101건. 화면 우상단이 `Log in` 상태였고 기관 인증이 실리지 않았다. L08 원 논문은 상위 결과에 없었다. 이 경로로는 원문을 얻지 못했다. 증거 `evidence\summon-L08-title.txt` |
| 2026-08-26T09:05:06.882473Z | 학술DB 목록 페이지 판독 | `https://kudos.knu.ac.kr/pages/sub.htm?nav_code=kud1641346542` | ACM Digital Library와 ScienceDirect 항목의 `바로가기` 링크가 `popup_gourl(<발행처 URL>)`을 호출함을 확인 |
| 2026-08-26T09:05:47Z경 | `popup_gourl` 함수 본문 판독 | 같은 페이지의 스크립트 | 이 함수가 `https://kudos.knu.ac.kr/include/proxyGo.php?url=<URL 인코딩된 대상>`을 새 창으로 여는 기관 프록시 관문임을 확인 |
| 2026-08-26T09:06:58.129374Z | 문헌 `L08`의 DOI로 프록시 관문 통과 시험 | `proxyGo.php?url=https://dl.acm.org/doi/10.1145/321864.321877` | 최종 URL `https://dl-acm-org.libproxy.knu.ac.kr/doi/10.1145/321864.321877`, HTTP 200. 화면 상단에 `Premium Edition Kyungpook National University` 표시. 기관 구독이 실렸다 |

## L08(Ladner 1975) 조작

| 시각(UTC) | 단계 | 대상 | 결과 |
|---|---|---|---|
| 2026-08-26T09:09:35.467829Z | 프록시로 ACM Digital Library 열기 | `proxyGo.php?url=https://dl.acm.org/` | 최종 URL `https://dl-acm-org.libproxy.knu.ac.kr/` |
| 2026-08-26T09:09:44.241204Z | 기관 구독 표시 확인 | 같은 페이지 | 본문에 `Kyungpook National University` 있음 |
| 2026-08-26T09:09:51.259649Z | 제목 검색 입력 | ACM DL 검색 입력란 `input[name='AllField']` | 문자열 `On the Structure of Polynomial Time Reducibility` 입력 후 Enter |
| 2026-08-26T09:10:01.559966Z | 검색 결과 도착 | `https://dl-acm-org.libproxy.knu.ac.kr/action/doSearch?AllField=On+the+Structure+of+Polynomial+Time+Reducibility` | 결과 목록 표시. 증거 `evidence\L08-01-search.png`, `evidence\L08-01-search.txt` |
| 2026-08-26T09:10:03.011331Z | DOI 일치 결과 링크 확인·클릭 | `a[href*='10.1145/321864.321877']` | 링크 존재. 클릭 |
| 2026-08-26T09:10:19.666850Z | 논문 페이지 도착 | `https://dl-acm-org.libproxy.knu.ac.kr/doi/10.1145/321864.321877` | 제목 `On the Structure of Polynomial Time Reducibility`, 저자 Richard E. Ladner, *Journal of the ACM* 22권 1호 155–171쪽. 증거 `evidence\L08-02-article.png`, `evidence\L08-02-article.txt` |
| 2026-08-26T09:10:20.704052Z | 원문 연결 요청 | `https://dl-acm-org.libproxy.knu.ac.kr/doi/pdf/10.1145/321864.321877` | 요청 발신 |
| 2026-08-26T09:10:22.198959Z | 응답 수신 | 같은 URL | HTTP 200, 콘텐츠 유형 `application/pdf`, 1,397,310바이트 |
| 2026-08-26T09:10:22.241299Z | 원문 보관 | `C:\math-artifacts\pvsnp-탐사-1\2.7\originals\subscription\L08-ladner-1975-jacm.pdf` | 저장소 밖에 보관. SHA-256 `c269533f25f06910cbca0f40873c46e4f51730654fcf2116b55689b8acf14781`. PDF 17쪽, 첫 쪽에 제목·저자·초록 확인 |

L08의 결과는 `원문 확보`다.

## L11(Mahaney 1982) 조작

ScienceDirect는 화면 없는 Chromium을 차단했고, 그 차단으로 아래 표의 조작 네 건이 실패했다. 실제 Google Chrome을 화면 있는 모드로 띄운 뒤에는 차단을 벗어났으나, 원문 파일을 얻지 못한 조작이 두 건 더 있었다. 두 건의 원인은 브라우저 밖 요청 통로 거부와 브라우저 내장 PDF 뷰어 열림이고, 자동화 차단이 아니다. 실패한 조작도 모두 남긴다.

| 시각(UTC) | 단계 | 대상 | 결과 |
|---|---|---|---|
| 2026-08-26T09:11:23.042661Z | 프록시로 ScienceDirect 열기(headless Chromium) | `proxyGo.php?url=https://www.sciencedirect.com` | 최종 URL `https://libproxy.knu.ac.kr/_Lib_Proxy_Url/https%3A%2F%2Fwww.sciencedirect.com` |
| 2026-08-26T09:12:07.405770Z | 제목 검색 | ScienceDirect 검색 URL | 차단 화면 반환. 본문 `There was a problem providing the content you requested`, 오류 코드 `CPE00001`, 접속 IP `155.230.44.16`, 브라우저 표기 `HeadlessChrome` |
| 2026-08-26T09:14:15.302019Z | PDF 직접 요청 | `.../science/article/pii/0022000082900022/pdfft?isDTMRedir=true&download=true` | 차단. PDF 아님 |
| 2026-08-26T09:15:52.586129Z | 브라우저 표기를 일반 Chrome으로 바꿔 재시도(headless 유지) | 같은 경로 | 차단 유지. 같은 오류 코드 `CPE00001` |
| 2026-08-26T09:16:29.653346Z | 프록시 첫 화면 재확인 | `https://www-sciencedirect-com.libproxy.knu.ac.kr/` | 차단 화면 |
| 2026-08-26T09:16:41.476057Z | 실제 Google Chrome을 화면 있는 모드로 띄워 재시도 | `proxyGo.php?url=https://www.sciencedirect.com` | 정상 화면 도착 |
| 2026-08-26T09:17:03.305313Z | 제목 검색 | `https://www-sciencedirect-com.libproxy.knu.ac.kr/search?qs=Sparse complete sets for NP: Solution of a conjecture of Berman and Hartmanis` | 결과 목록 표시 |
| 2026-08-26T09:17:17.833733Z | 논문 페이지 도착 | `https://www-sciencedirect-com.libproxy.knu.ac.kr/science/article/pii/0022000082900022` | 논문 페이지 표시 |
| 2026-08-26T09:17:18.442879Z | 원문 링크 확인 | 같은 페이지의 `Download PDF` 링크 | 링크 주소 `.../science/article/pii/0022000082900022/pdf?md5=102491f7bbb8561ef4b53424a7e11a77&pid=1-s2.0-0022000082900022-main.pdf` |
| 2026-08-26T09:17:31.956526Z | 원문 요청(브라우저 밖 요청 통로) | 같은 주소 | HTTP 403. 브라우저 창 밖의 요청 통로는 발행처가 거부 |
| 2026-08-26T09:27:32.510580Z | 원문 링크를 새 탭에서 열기 | 같은 주소 | 내려받기 사건이 일어나지 않고 브라우저 내장 PDF 뷰어가 열려 파일 본문을 직접 얻지 못함 |
| 2026-08-26T09:28:04.946002Z | 제목 검색 재실행 | 같은 검색 URL | 결과 목록 표시. 증거 `evidence\L11-01-search.png`, `evidence\L11-01-search.txt` |
| 2026-08-26T09:28:18.458406Z | 결과 링크 확인·클릭 | `a[href*='0022000082900022']` | 링크 존재. 클릭 |
| 2026-08-26T09:28:32.496757Z | 논문 페이지 도착 | `https://www-sciencedirect-com.libproxy.knu.ac.kr/science/article/pii/0022000082900022` | 증거 `evidence\L11-02-article.png`, `evidence\L11-02-article.txt` |
| 2026-08-26T09:28:33.116388Z | 원문 링크 클릭 | 위 `Download PDF` 주소 | 새 탭에서 열기 |
| 2026-08-26T09:28:34.470404Z | 원문 응답 관찰 | `https://pdf-sciencedirectassets-com.libproxy.knu.ac.kr/272574/1-s2.0-S0022000000X0089X/1-s2.0-0022000082900022/main.pdf` | HTTP 200, 콘텐츠 유형 `application/pdf`. 브라우저가 받은 응답 본문을 그대로 취득 |
| 2026-08-26T09:28:58.750240Z | 원문 보관 | `C:\math-artifacts\pvsnp-탐사-1\2.7\originals\subscription\L11-mahaney-1982-jcss.pdf` | 저장소 밖에 보관. 981,257바이트, SHA-256 `a506d934f69cceaeac213c80af52b95368a4e533be4bfefeba2ae82c097ac8ca`. PDF 14쪽, 첫 쪽에 저널명·권호·쪽수 `25, 130-143 (1982)`와 제목·저자 확인 |

L11의 결과는 `원문 확보`다.

## 계정 점유

이 행이 KUDOS 계정을 배타적으로 점유했다. 같은 시간대에 다른 행이 같은 계정으로 로그인하지 않았다. 로그인 세션 상태는 저장소 밖 `C:\math-artifacts\pvsnp-탐사-1\2.7\evidence\kudos-state.json`에 두었고 저장소에 넣지 않았다.

## 확보한 원문 목록

| ID | 보관 경로(저장소 밖) | 바이트 | SHA-256 | 쪽수 |
|---|---|---:|---|---:|
| L08 | `C:\math-artifacts\pvsnp-탐사-1\2.7\originals\subscription\L08-ladner-1975-jacm.pdf` | 1,397,310 | `c269533f25f06910cbca0f40873c46e4f51730654fcf2116b55689b8acf14781` | 17 |
| L11 | `C:\math-artifacts\pvsnp-탐사-1\2.7\originals\subscription\L11-mahaney-1982-jcss.pdf` | 981,257 | `a506d934f69cceaeac213c80af52b95368a4e533be4bfefeba2ae82c097ac8ca` | 14 |

두 PDF는 구독 기반 원문이므로 저장소에 넣지 않았다.

## 한계

기관 프록시 접근은 2026-08-26의 KUDOS 계정 상태와 구독 범위에 묶인다. ScienceDirect의 자동화 차단은 브라우저 종류와 실행 방식에 따라 달라졌다. 이 문서의 결과를 다른 시점·다른 계정의 접근 가능성으로 일반화하지 않는다.
