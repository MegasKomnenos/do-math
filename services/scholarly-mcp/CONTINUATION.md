# 학술자료 MCP 현행 구현과 재검토 인계

2026-09-14 KST의 추가 재검토를 반영한 인계다. 최초 입력은 사용자가 로컬에 제공한 `학술자료-MCP-구현-인계.md`이며 이 저장소에 함께 배포하는 파일은 아니다. 현행 계약은 아래에 보존했다. 실제 호출법은 [README](README.md)와 `describe_source`, 자료원별 상태는 [지원표](SUPPORT.md)를 따른다. 잔여 19개 항목의 실제 처리 과정과 해결 시도는 [partial 재검토](PARTIAL-REVIEW.md)에 있다. 과거 보고의 완료·불가 판정은 아래 최신 검증을 대신하지 않는다.

현재 작업은 결과 정리로 종료한다. 사용자는 형식 미제공 등의 조사 범위를 수용하고 잔여 문제의 추가 시도를 허용했으나, 도서관 연결에서 Google 도서까지 이어지자 범위가 계속 넓어진다고 지적했다. 이후 추가 탐색·지원 범위 확장을 멈추고 이미 얻은 결과만 정리하기로 했다. 이 후속에서 서비스 코드나 등록 자료원을 추가하지 않았다. PARTIAL-REVIEW의 재개 조건은 남은 문제의 기록이며 추가 조사 실행 지시가 아니다.

사용자의 후속 지시에 따라 13개 사이트의 자연스러운 화면 이용 흐름을 사이트별 독립 `codex exec`로 조사했다. 작업자는 페이지·메뉴·내용·가이드·UI를 이미지로 읽고 다음 행동을 정했고 root도 핵심 이미지를 열어 검토했다. 파견문·사이트별 보고·후속 요청은 로컬 `data/ui-walkthrough-20260914/`에 있다. `state.json`은 첫 실행만 추적하므로 후속 결과는 각 `report.md`와 `last-message-followup.md`를 따른다. 현재 판정은 [partial 재검토](PARTIAL-REVIEW.md)에 통합한다.

UI 후속에서 Title OR의 기존 지원 판정을 철회했다. 실제 Title 검색에서 `Quantum OR realization`은915건인데 같은 제목의 나머지 단어를 OR로 추가하면1건으로 좁아졌다. 공백으로 결합해도 같았다. 입력·결과 화면과 빠진 문헌을 확인한 뒤 여러 Title term의 OR 문자열 변환을 거부하도록 수리했다. 관련33검사와 전체639검사가 통과했다. 일반 query/field 검색과 기존 Author OR·서로 다른 Title/Author 조건은 유지한다. Digital Library 자체의 YEAR 단일 연도 필터는 정상 UI로 작동하지만 특정 expression 메타데이터 필드와 같다고 단정하지 않는다.

## 구현·검증 범위

24개 CLI 과제와 root가 추가로 찾은 구현 오류를 원본에 통합했다. 전체633검사가 통과했다. 새 원본 SDK에서 De Gruyter7판정, Semantic Scholar bulk/title-match, SIAM 저자 필터, AMS13판정, CORE 검색·work/output·파일 복구·제거 음성, ScienceDirect4기능과 검색 대기 수리를 확인했다. 자료원별 `partial`은 지원 기능의 범위이며, 아래 실제 접근 조건을 코드 미통합과 혼동하지 않는다.

추가 재검토에서는 API 오류 응답의 정제 artifact 보존, ScienceDirect 새 세션의 ISSN·ISBN 기반 후보 축소와 검색 행·상세 PDF 실패 보존을 수리했다. 수정 후 전체638검사가 통과했다. Semantic Scholar는 2026-09-13 15:31 UTC의 새 SDK에서 metadata·abstract·BibTeX·참고문헌30개가 available이었다. Software Heritage의 원 Vault는 여전히 new지만 기존92파일·20디렉터리로 같은 Git tree의 별도 압축물을 복원했다. 복원물과 원 작업의 완료는 구별한다.

ScienceDirect의 검색 Export·상세 Cite·PDF를 병합했고 정확한 한 행 선택과 기존 상태 복원, 정리 실패 시 주 결과 보존, 검색 준비 재확인을 수리했다. Preface의 실제 비구독은 PDF 확보 성공으로 세지 않는다. EuDML은 실제 책204358과14개 장의 서지·외부 링크를 확인하고, 목차를 전문으로 오인하던 판별을 고쳤다. 원본의 같은 실제 XML 재생은 metadata/supplementary available·fulltext not_offered이며 자료를 생략하지 않는다.

최종 EuDML NLM 요청은 도구가 전역 주입한 식별 헤더 대신 실제 HTTPX 라이브러리의 기본 식별값을 쓰도록 범위를 한정했다. Accept·redirect·대기 한도·CQL·다른 자료원은 그대로다. 수정 후 새 원본 API는14:08:13UTC에200/XML8,336바이트를 반환했고 metadata·14개 장·본문 미제공을 구별하는6판정이 통과했다. 특정 시각의 성공을 영구 가용성으로 확대하지 않는다.

## 읽을 근거

| 경로 | 역할 |
|---|---|
| [지원표](SUPPORT.md) |49개 자료원의 구현과 실제 검증 범위 |
| [감사표](AUDIT-MATRIX.md) | 잘못된 제한을 수리한 항목과 실제 접근·자료 상태 |
| [검증 기록](VALIDATION.md) | 원본 회귀·새 SDK·전후 이미지 및 원 응답의 대조 |
| [partial 재검토](PARTIAL-REVIEW.md) | 잔여19항목의 원인·해결 시도·현재 판정; AMS 실제 화면·전송 경로와 어휘 대조 |
| [실패 지점 분석](LIMITATIONS-AUDIT.md) | 최초 실패 원인과 후속 정정 |
| [접근 이력](ACCESS-RESEARCH.md) | 기관 경로와 공유 상태·인증값 출력 사건 |
| `data/dispatch/20260913T021511Z/root-integration-status.json` | 과제별 root 통합·커밋 상태; CLI 완료 주장과 구별 |
| `data/dispatch/20260913T021511Z/ROOT-PROGRESS.md` | 최종 상태 요약과 실행 이력·private 근거의 연결 |
| `data/dispatch/20260913T021511Z/<task>/criteria-review.json` | 실패별 재현·직전/직후/안정 이미지·실제 판독·수리·남은 조건 |
| `data/access-research/user-criteria-*/root-*.json` | 정제한 원본 SDK 및 root 검토 근거 |
| [기억 색인](../../기억/색인.md) | 관련 L 노드와 최신 커밋별 M 노드 |

`data/`와 원시 private 자료는 로컬 실행 근거다. 추적 문서와 기억이 현재 계약을 보존하며, 로컬 근거가 없으면 실서비스 성공을 다시 했다고 주장하지 않는다.

## 남은 조건을 해석하는 기준

오류나0건만으로 자료원 불가를 확정하지 않는다. 실패를 같은 입력으로 재현하고 실제 직전·직후 이미지를 열어 읽으며, 원 요청·응답·오류 로그를 대조한다. 문법·필드·인코딩·selector·경로·timeout 등 로컬 실수는 수리하고 다시 검증한다. 저장 HTML 재생이나 로컬 SDK 콘솔은 그 사실을 명시한다. HTTP429는 자료 부재가 아니며, 서버가 안내한 재시도 시각을 지킨다.

## 현재 확보하지 못하는 기능·자료

사용자 결정으로 제외한 기능은 아래 표에 넣지 않았다. 각 행의 확인 표본과 범위를 다른 자료원 전체의 불가로 확대하지 않는다.

| 개별 기능·자료 | 현재 상태와 이유 |
|---|---|
| AMS 같은 Title 필드의 OR 식 | 기본 Title 문자열은 논리 합집합을 보장하지 않는다. 정상 화면에서 OR 조건을 추가했는데915건에서1건으로 좁아진 반례를 확인했고 잘못된 문자열 변환을 거부하도록 수리했다. Author 필드의 별도 기존 검증과 구별한다. |
| AMS 같은 필드의 AND 식 | 기본 Title 칸의 AND는 일반 검색어로 처리된다. 실제 입력·결과 화면, 원 POST, 단독 AND와 음성어 대조로 확인했다. 동적 Custom Search는 별도 경로이며 한 조건도97바이트 null 오류를 반환했다. 인코딩 대조도 같았고 서버 내부 원인은 미확정이다. |
| AMS 같은 필드의 NOT 식 | 기본 Title 칸의 NOT는 일반 검색어로 처리된다. 단독 NOT와 두 음성어 사이 NOT 모두3,398건이며 화면·원 응답이 일치했다. 제외 연산의 정상 실행 경로는 확보하지 못했다. |
| AMS 서로 다른 필드의 OR 식 | 검증된 기본 필드 간 결합은 AND다. 필드 간 OR로 자동 바꾸지 않는다. |
| AMS equals 조건 | expression 매핑은 미지원이다. Title/Author equals와 별도로, 실제 결과의 YEAR → Use Single Year → 연도 입력 → Apply Filter(s)는 정확한 한 해 제한을 제공한다. 2025·2024 적용을 확인했으며 현재 MCP 옵션에 추가한 기능은 아니다. |
| AMS expression의 다단어·문장부호 원자 | 기본 필드 문자열로 옮기면 의미가 바뀔 수 있어 `expression_mapping_unavailable`이다. 임의로 한 토큰 또는 다른 논리식으로 바꾸지 않는다. |
| SIAM DOI10.1137/24M1711108의 출판사 PDF | 공식 KNU2026 개별전자저널 목록은1997–current로 기재하지만 목록 링크·호 목차·공식 프록시 뒤에도 Get Access다. 통합 포털의2011 종료 기재와도 다르며 내부 권한 원인은 미확정이다. 같은 논문의 accepted arXiv2411.07981v2 PDF28쪽을 별도 확보했다. |
| ScienceDirect Preface S0065230X26000631의 PDF | 후보 누락 수리는 완료했지만 정확한 행의 다운로드는 비구독이었다. 추가 도서·제공리스트·도서관 연결에서도 원문을 확보하지 못했다. 총서명 검색0건과 달리 서명 전방일치로 시리즈 기록은 찾았으나 확인한 소장은최대v.122였다. 기관360LINK는 이용 가능한 전자자료가 없다고 했고, Google 연결의 다른eBook ISBN 샘플도 Preface 페이지 미리보기를 제공하지 않았다. 원PDF 확보나 새로운MCP 지원으로 세지 않는다. |
| ScienceDirect Book review S1765462926000553의 PDF | 해당 문헌이 Purchase PDF와 비구독 상태를 표시했다. 다른 문헌의31쪽 PDF 양성과 구별한다. |
| Oxford 검색별 Export title list | KUDOS OUP 경로에서 CAPTCHA 사이트 키 도메인 오류가 지속하고 Download가 파일을 주지 못했다. 공식 가이드는 인증 상태에서 Export가 나타난다고 설명한다. 별도 전체 도서 Excel·OSO/UPSO KBART·장 RIS는 확보했지만 검색별 title export와 구별한다. |
| JSTOR community.39197180 영상 다운로드 | 후속 실제 UI에서는 FREE 영상이 재생되고 전사문0:22 링크로 이동한다. Download는 비활성이다. 앞선 별도 호출의 Client Challenge를 현재 영상 시청 불가로 확대하지 않는다. 옛 기관 저장소는 폐지 안내이며 Handle은 같은 JSTOR 항목으로 돌아온다. |
| De Gruyter snde1089_supplementary_2.zip | 문헌의 기관 PDF11쪽은 확보했지만 현행 Data and code 링크는404다. 당시 동일 논문의 bepress Supporting Files 화면은 Belaire_Contreras.zip을 Data and code로 명시한다. 그26,379바이트 ZIP의6개국 데이터·Ox·FORTRAN·README는 확보했다. 당시 첨부의 정체는 확인했으나 현재 ZIP과 byte 동일성은 미확정이다. |
| Taylor & Francis의 두 editorial 초록 | 실제 전체 HTML과 Citation & abstract RIS에 초록이 없었다. 둘째 문헌은 View PDF → 새 뷰어 → Download PDF로187,178바이트·서지표지 포함10쪽도 확보했다. 뷰어 전환 오류를 PDF 미제공으로 판정하지 않으며 일반 description으로 초록을 채우지 않는다. |
| Springer DOI10.1007/s00037-008-0249-x의 HTML 본문 | 실제 main-content가 비어 있다. 같은 문헌 PDF는 확보했고 미식별 레이아웃 전체로 일반화하지 않는다. |
| EuDML 책204358의 NLM 전문 | XML은 서지·14개 장 metadata·외부 링크를 제공하며 책 본문은 없다. 원 링크의 GDZ에서는 실제 전체책 PDF412쪽·IIIF·METS를 확보했다. 서지 표지1쪽+스캔411쪽 및14개 부분의 면 대응을 구별하며 EuDML XML 전문으로 세지 않는다. |
| CORE 일부 문헌의 indexed fullText 필드 | 최신 Output213561553도 실제 본문 대신 공개 API 안내문을 준다. 먼저429의 재시도 시각을 지킨 뒤200의 필드를 확인했다. 같은 work의 검증된 공개 PDF가 있으면 별도 파일로 회수하며 전체 CORE PDF 부재를 뜻하지 않는다. |
| Semantic Scholar Graph API의 원문 파일 bytes | Graph API의 제공 범위 밖이다. 대상의 빈 openAccessPdf·isOpenAccess=false와 달리 실제 Reader·arXiv는 원문을 제공했다. 외부 arXiv v2 PDF698,413바이트·28쪽을 확보했으며 Graph 파일 반환으로 세지 않는다. |

## 결과가 일부이거나 현재 검증을 마치지 못한 항목

| 개별 항목 | 확인한 사실·남은 불확실성 |
|---|---|
| Software Heritage 원 Vault 압축 작업 |2026-09-14 10:21KST의 저장 상태 재개와 공식GET 모두 같은task419779186·new·progress null이다. 공식 Vault Operational 및 장애 이력에도 이 작업의 대기 사유는 없다. 새 POST·재큐잉·반복 polling 없이 종료했다. 별도899,228바이트 tar.gz는 기존92파일·20디렉터리의 같은Git tree 복원물이며 원Vault 완료로 세지 않는다. |
| Figshare collection4046897 과거 v6의 전체 구성원 | 추가 대조의metadata/UI·RIS는 v5 15/15, v6 17/16, v7 19/18이다. 현재v8의REST/UI 유일 차이17061347.v1이 v6보다2분45초 먼저 게시되어 가장 강한 후보로 좁혀졌다. 실제2021년 보고서PDF19,298,271바이트·41쪽은 확보했다. v6의역사ID관계 증명은 없어16개partial을 유지하며 후보를 자동 삽입하지 않는다. |

Semantic Scholar의 현재 batch 가용성은 미확정 목록에서 해소했다. 15:06UTC의429 뒤15:31UTC에 같은 대상의 새 payload·초록·BibTeX·참고문헌30개를 받았고 metadata의 referenceCount30과 일치했다. fulltext까지 요청한 전체 응답의 partial은 Graph API가 원문 파일을 제공하지 않는 범위 때문이며 batch 실패가 아니다. Figshare 후보 원문 회수와 v6의역사관계 확정은 구별한다. 공개 판본별 ID 목록이 없으므로 과거 전체 구성원을 확정하려면 제공자 또는 소유자의 관계 근거가 필요하다.

CORE의 work/output 및 files01 복구, SIAM52번째 조건·저자 필터, Numdam 날짜만/한쪽 범위, IEEE Media 파싱, Crossmark 의미, DBLP·KG 형식과 원 범위, De Gruyter DOI 없는 책 인용은 더 이상 위 미확정 목록에 남기지 않는다. 새 실패나 원 서비스 변화가 생기면 해당 입력과 근거를 새로 기록한다.

## 작업·권한 경계

추가 API키·계정·승인·연락 이메일을 요구하는 경로는 쓰지 않는다. Unpaywall, Scopus 개인 웹계정 내보내기, 자격이 필요한 GitHub 전역 code search는 사용자 결정으로 제외했다. KUDOS가 필요한 자료원은 실제 바로가기와 기관 프록시를 사용한다. 이미 거부된 KNU IdP 자격을 다시 제출하지 않는다. 한 호출은 지정 source 안에서 끝나며 API 실패를 이유로 브라우저나 다른 source로 자동 전환하지 않는다.

CLI는 최대8개, 같은 source는 하나씩 실행한다. `state.json`은 controller가 소유하며 root가 완료로 덮어쓰지 않는다. `review-requests.json`에는 task당 최신 요청 하나만 둔다. 원본/Git은 root만 수정하고 각 worker는 private 사본을 쓴다. 오래된 전체 registry나 공통 모듈을 복사하지 말고 최소 변경만 현재 기준선에 적용한다. 등록 MCP·Codex·사용자의 브라우저를 재시작하지 않는다. 별도 소유 SDK 서버와 브라우저를 사용하고 종료한다.

인증 파일과 원시 로그를 넓은 내용 검색에 포함하지 않는다.11:50–11:51UTC root 검색이 credential JSON을 포함해 실제 쿠키·토큰 일부를 도구 출력에 노출한 사건은 ACCESS-RESEARCH와 M0254에 기록했다. 값을 다시 인용하지 않으며 인증 상태를 임의 복원·폐기하지 않는다. 기존 출력의 삭제를 확인하지 못했다. 기관IP·표시명 때문에 캡처를 다시 만들지는 않는다.

커밋마다 새 M 노드 하나와 색인을 함께 포함하고, 메모리 검증과 staged 인증값 검사의 실제 exit code를 각각 확인한다. 무관한 dirty 파일은 보존한다. 전체 작업이 끝난 뒤에만 push한다.
