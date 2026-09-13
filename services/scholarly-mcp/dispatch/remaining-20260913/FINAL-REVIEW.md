# 사용자 기준 재검토의 최종 통합 판정

24개 CLI 과제와 root의 추가 검토에서 확인한 생산 수리를 원본에 통합했다. 최종 전체633검사가 통과했다. 실제 API·원 UI의 전후 판독, 새 원본 SDK, 저장 응답 재생을 구별해 검증했고, 코드 수리와 자료원·문헌별 상태를 분리했다. 현행 상세 목록은 [후속 인계](../../CONTINUATION.md),49개 자료원의 범위는 [지원표](../../SUPPORT.md), 수치와 원 근거는 [검증 기록](../../VALIDATION.md)을 따른다.

다음의 완료는 조사·수리·원본 통합 판정이다. 모든 문헌의 모든 기능이 제공되거나 모든 호출이 항상 성공한다는 뜻은 아니다.

| 과제 | 원본 통합·검증 결론 | 남는 자료원 조건 |
|---|---|---|
| ams-expression | 가시 Title/Author 식 부분집합·첫 XLSX·Unicode·순번 공백과 이어받기, 새 SDK13판정 | 같은 필드 AND/NOT·필드 간 OR·equals·안전하게 매핑하지 못한 원자는 미지원 |
| siam-institution | 실제 PDF 제어와 접근 상태 분류, 공개53쪽 대조 | 특정 비공개 문헌의 현재 기관 인증 미성립 |
| dblp-challenge | 공백 인코딩·현재 응답 크기에 따른 페이지 연결·7내보내기·1000개 고유 문헌 | 호출 제한의 영구 소멸을 보장하지 않음 |
| semantic-scholar-rate | batch/title-match·native bulk cursor·원 BibTeX와 관계 범위 구현, 원본 bulk/match 검증 |13:53UTC 최신 batch는429, 자료 부재와 구별 |
| eudml-nlm | 경로별 대기·실제 책·목차 오판·NLM 요청의 HTTPX 기본 식별값, 최종 원본200과6판정 | metadata·장 링크만 있는 책 XML은 전문이 아님;504는 시점·조건별로 구별 |
| core-indexed-text | whitespace·실제 본문·접근 안내문을 구별 | 일부 indexed 필드는 안내문이며 공개 PDF와 다른 범위 |
| core-work-download | 같은 output 관계에 결속된8쪽 PDF, metadata 보존 | 제거·제한 문헌은 그 상태 유지 |
| core-output-download | 명시 API download와8쪽 파일 정체성, reset 뒤 제거404 |429를 문헌 부재로 세지 않음 |
| core-files01 | 원522 뒤 같은 output의 현행 URL로48쪽 회수 | 옛 호스트 자체가 복구됐다는 뜻은 아님 |
| swh-vault | 원 task·SWHID·상태와 개별 파일 회수의 차이 검증 |13:53UTC에도 task419779186은 new, 압축 미완료 |
| oxford-title-export | 일반 검색 렌더 준비와 인용을 복원하고 title-list 범위를 구별 | 별도 title-list는 CAPTCHA 도메인 오류 |
| jstor-video | 지연 식별/접근 확인 관찰 수리, 오디오·전사문 대조 | 해당 영상의 native download 비활성 |
| degruyter-broken-supplement | 현재404·원 보존 링크·역사 ZIP10개 구성원 검산 | 현재 깨진 파일과 역사 ZIP의 byte-equivalence는 미입증 |
| degruyter-citation | 현재 CITE·DOI 없는 ISBN 책 RIS, 원본7판정 | 원 CITE가 없는 Journal 행은 별도 미제공 |
| sciencedirect-export | 정확 행/상단 Export와 상세 Cite, 세 인용 형식과 정체성 | 문헌별 실제 제어·접근 상태를 보존 |
| sciencedirect-pdf | 원본31쪽 PDF·정확 선택 다운로드·선택 상태와 주 결과 보존·검색 대기 수리 | Preface는 비구독, 상세 HTML 복귀도 함께 보존 |
| taylor-abstract | 두 editorial의 UI·Citation & abstract·원 파일 동일성 검증 | 해당 두 문헌의 실제 초록 부재 |
| dblp-kg-tsv | 원 RDF term 손실 판별·tsv_exact·실패 시 JSON 보존 | 제공자 원 TSV의 자료형 손실은 원 파일과 함께 표시 |
| siam-last-condition |52번째 Title17/17/0·자유 Author 보존·명시 exact 공동저자 AND | underscore 자유식을 exact 저자 신원으로 해석하지 않음 |
| numdam-date-only | 날짜만·한쪽 열린 범위·qdt 마지막 페이지를 원본 SDK로 검증 | 기록된 검색 조건·시점의 결과 |
| ieee-media-flag | DOI 링크를 영상으로 오인한 파서 수리, MP4·30참고문헌 | 조사 표본에 flag 모순이 없었다는 범위만 확인 |
| crossmark-semantics | 방향·중복·알 수 없는 타입·partial과 원 값 보존, 원본9호출 | 원 자료의 누락을 임의로 채우지 않음 |
| springer-html-negative | 실제 Springer HTML 지원과 빈 본문의 구별, 같은28쪽 PDF | 해당 구형 문헌의 실제 HTML 부재 |
| figshare-historical-members | 판본별2/3건, 같은 current 판본의21건 보완, 과거 보존 | 과거 v6은16/17 불일치로 partial |

## 완료 판단을 바꾼 추가 확인

Root는 초기 완료 반환을 그대로 승인하지 않았다. AMS의 실제 순번 공백, Semantic Scholar의 원1000건과 caller limit 차이, SIAM의 자동 underscore 변환, ScienceDirect의 loopback404 귀속과 선택 상태, EuDML의 metadata-only body를 전문으로 세던 오류를 재현하고 수리했다. EuDML의504도 전역 헤더 조건과 실제 HTTPX 기본 식별값을 대조해 최소 호환 수리까지 확인했다. 각 수리는 원 입력과 이미 확보한 자료를 보존한다.

완료·미제공·미지원·접근 제한·현재 호출 제한·부분 결과는 서로 다른 판정이다. 사용자 결정으로 제외한 Unpaywall·Scopus 개인 계정 내보내기·자격이 필요한 코드 검색은 이24개 실패 과제에 다시 넣지 않았다. 추가 키·계정·연락 이메일·구매·지원 문의를 사용하지 않았다.

CLI state의 awaiting_review는 운영기가 반환 파일을 수용한 상태다. Root의 내용 검토와 최종 통합 상태는 data/dispatch/20260913T021511Z/root-integration-status.json에 별도로 있다. 등록 MCP·Codex·사용자 브라우저를 재시작하지 않았으며, 소유한 새 SDK 서버와 브라우저로 검증했다. 원시 응답과 인증은 private, 정제 근거는 data/access-research에 보존한다.
