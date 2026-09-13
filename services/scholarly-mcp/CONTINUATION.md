# 학술자료 MCP 현행 구현과 재검토 인계

2026-09-13 작업을 잇는 문서다. 최초 입력은 사용자가 로컬에 제공한 `학술자료-MCP-구현-인계.md`이며 이 저장소에 함께 배포하는 파일은 아니다. 현행 계약은 아래에 보존했다. 실제 호출법은 [README](README.md)와 `describe_source`, 자료원별 상태는 [지원표](SUPPORT.md)를 따른다. 과거 보고의 완료·불가 판정은 아래 최신 검증을 대신하지 않는다.

## 구현·검증 범위

24개 CLI 과제와 root가 추가로 찾은 구현 오류를 원본에 통합했다. 전체633검사가 통과했다. 새 원본 SDK에서 De Gruyter7판정, Semantic Scholar bulk/title-match, SIAM 저자 필터, AMS13판정, CORE 검색·work/output·파일 복구·제거 음성, ScienceDirect4기능과 검색 대기 수리를 확인했다. 자료원별 `partial`은 지원 기능의 범위이며, 아래 실제 접근 조건을 코드 미통합과 혼동하지 않는다.

ScienceDirect의 검색 Export·상세 Cite·PDF를 병합했고 정확한 한 행 선택과 기존 상태 복원, 정리 실패 시 주 결과 보존, 검색 준비 재확인을 수리했다. Preface의 실제 비구독은 PDF 확보 성공으로 세지 않는다. EuDML은 실제 책204358과14개 장의 서지·외부 링크를 확인하고, 목차를 전문으로 오인하던 판별을 고쳤다. 원본의 같은 실제 XML 재생은 metadata/supplementary available·fulltext not_offered이며 자료를 생략하지 않는다.

최종 EuDML NLM 요청은 도구가 전역 주입한 식별 헤더 대신 실제 HTTPX 라이브러리의 기본 식별값을 쓰도록 범위를 한정했다. Accept·redirect·대기 한도·CQL·다른 자료원은 그대로다. 수정 후 새 원본 API는14:08:13UTC에200/XML8,336바이트를 반환했고 metadata·14개 장·본문 미제공을 구별하는6판정이 통과했다. 특정 시각의 성공을 영구 가용성으로 확대하지 않는다.

## 읽을 근거

| 경로 | 역할 |
|---|---|
| [지원표](SUPPORT.md) |49개 자료원의 구현과 실제 검증 범위 |
| [감사표](AUDIT-MATRIX.md) | 잘못된 제한을 수리한 항목과 실제 접근·자료 상태 |
| [검증 기록](VALIDATION.md) | 원본 회귀·새 SDK·전후 이미지 및 원 응답의 대조 |
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
| AMS 같은 필드의 AND 식 | 가시 기본 제어의 동일 필드 결합은 OR이며 동등한 AND 실행 경로를 확인하지 못했다. 숨은 builder는 원 오류를 반환했다. |
| AMS 같은 필드의 NOT 식 | 현재 원 제어에서 의미를 보존해 실행할 경로를 확인하지 못했다. |
| AMS 서로 다른 필드의 OR 식 | 검증된 기본 필드 간 결합은 AND다. 필드 간 OR로 자동 바꾸지 않는다. |
| AMS equals 조건 | 현재 검증한 contains 부분집합에 포함되지 않는다. 원 제어의 실패와 구별해 미지원으로 반환한다. |
| AMS expression의 다단어·문장부호 원자 | 기본 필드 문자열로 옮기면 의미가 바뀔 수 있어 `expression_mapping_unavailable`이다. 임의로 한 토큰 또는 다른 논리식으로 바꾸지 않는다. |
| SIAM DOI10.1137/24M1711108의 비공개 PDF | 실제 기관 경로 뒤에도 Get Access 및 같은 문헌 초록 복귀였다. 현재 인증 미성립이며 행정적 구독권 부재를 입증한 것은 아니다. |
| ScienceDirect Preface S0065230X26000631의 PDF | 정확 Title+ISSN 행을 선택한 다운로드가 비구독을 명시했다. 상세 HTML 복귀도 함께 기록했다. |
| ScienceDirect Book review S1765462926000553의 PDF | 해당 문헌이 Purchase PDF와 비구독 상태를 표시했다. 다른 문헌의31쪽 PDF 양성과 구별한다. |
| Oxford 검색별 Export title list | 현재 proxy의 CAPTCHA 사이트 키 도메인 오류로 정상 제출이 안 됐다. 같은 직접 호스트에는 제어가 없었다. 개별 문헌 CSV·인용과 다른 기능이다. |
| JSTOR community.39197180 영상 다운로드 | 원 다운로드 제어가 비활성이다. 전사문 및 별도 오디오 양성을 영상 파일 확보로 세지 않는다. |
| De Gruyter snde1089_supplementary_2.zip | 현재 원 링크는404다. 역사 보존 Belaire_Contreras.zip은 별도 확보했으나 같은 bytes라는 근거는 없다. |
| Taylor & Francis의 두 editorial 초록 | 실제 본문과 Citation & abstract 파일에 초록이 없었다. 일반 description으로 채우지 않는다. |
| Springer DOI10.1007/s00037-008-0249-x의 HTML 본문 | 실제 main-content가 비어 있다. 같은 문헌 PDF는 확보했고 미식별 레이아웃 전체로 일반화하지 않는다. |
| EuDML 책204358의 NLM 전문 | 이 XML은 서지·14개 장 metadata·외부 링크를 제공하며 책 본문은 없다. metadata와 목차는 보존한다. |
| CORE 일부 문헌의 indexed fullText 필드 | 실제 본문 대신 공개 API 안내문을 준다. 같은 work의 검증된 공개 PDF가 있으면 별도 파일로 회수하며 전체 CORE PDF 부재를 뜻하지 않는다. |
| Semantic Scholar Graph API의 원문 파일 bytes | Graph API의 제공 범위 밖이다. 외부 openAccessPdf와 모든 논문의 PDF 부재를 동일시하지 않는다. |

## 결과가 일부이거나 현재 검증을 마치지 못한 항목

| 개별 항목 | 확인한 사실·남은 불확실성 |
|---|---|
| Semantic Scholar 현재 batch full-parts 가용성 |13:53:07UTC의 최신 원본 요청도429/174바이트, Retry-After 없음이었다. 이전 batch·BibTeX·참고문헌 양성은 있으나 현재 새 payload는 받지 못했다. bulk/title-match 성공과 별개다. |
| Software Heritage 원 Vault 압축 작업 |13:53:02UTC의 정확한 상태 GET은 task419779186과 같은 SWHID의 `new`였다. 완료 시각은 알 수 없다. 별도92파일·20디렉터리 회수는 이 압축 작업 완료가 아니다. |
| Figshare collection4046897 과거 v6의 전체 구성원 | metadata17건과 실제 목록16건이 달라16건 partial로 보존한다. current v8의21건으로 과거를 채우지 않는다. |

CORE의 work/output 및 files01 복구, SIAM52번째 조건·저자 필터, Numdam 날짜만/한쪽 범위, IEEE Media 파싱, Crossmark 의미, DBLP·KG 형식과 원 범위, De Gruyter DOI 없는 책 인용은 더 이상 위 미확정 목록에 남기지 않는다. 새 실패나 원 서비스 변화가 생기면 해당 입력과 근거를 새로 기록한다.

## 작업·권한 경계

추가 API키·계정·승인·연락 이메일을 요구하는 경로는 쓰지 않는다. Unpaywall, Scopus 개인 웹계정 내보내기, 자격이 필요한 GitHub 전역 code search는 사용자 결정으로 제외했다. KUDOS가 필요한 자료원은 실제 바로가기와 기관 프록시를 사용한다. 이미 거부된 KNU IdP 자격을 다시 제출하지 않는다. 한 호출은 지정 source 안에서 끝나며 API 실패를 이유로 브라우저나 다른 source로 자동 전환하지 않는다.

CLI는 최대8개, 같은 source는 하나씩 실행한다. `state.json`은 controller가 소유하며 root가 완료로 덮어쓰지 않는다. `review-requests.json`에는 task당 최신 요청 하나만 둔다. 원본/Git은 root만 수정하고 각 worker는 private 사본을 쓴다. 오래된 전체 registry나 공통 모듈을 복사하지 말고 최소 변경만 현재 기준선에 적용한다. 등록 MCP·Codex·사용자의 브라우저를 재시작하지 않는다. 별도 소유 SDK 서버와 브라우저를 사용하고 종료한다.

인증 파일과 원시 로그를 넓은 내용 검색에 포함하지 않는다.11:50–11:51UTC root 검색이 credential JSON을 포함해 실제 쿠키·토큰 일부를 도구 출력에 노출한 사건은 ACCESS-RESEARCH와 M0254에 기록했다. 값을 다시 인용하지 않으며 인증 상태를 임의 복원·폐기하지 않는다. 기존 출력의 삭제를 확인하지 못했다. 기관IP·표시명 때문에 캡처를 다시 만들지는 않는다.

커밋마다 새 M 노드 하나와 색인을 함께 포함하고, 메모리 검증과 staged 인증값 검사의 실제 exit code를 각각 확인한다. 무관한 dirty 파일은 보존한다. 전체 작업이 끝난 뒤에만 push한다.
