# 첫 세 과제 이외의 종료 판단 검토

이 문서는 초기 반환을 대조한1차 기록이다. 이후 수리·원본 통합과 현행 조건은 [최종 검토](FINAL-REVIEW.md)와 [후속 인계](../../CONTINUATION.md)를 따른다. 아래의 검토 대기·미확정 상태를 현재 상태로 사용하지 않는다.

AMS·SIAM 기관 접근·Oxford를 다시 열었다는 사실은 나머지21개 과제의 소진 판단을 승인했다는 뜻이 아니다. 이 문서는 각 반환의 방법·성공 범위·남은 조건을 선별한1차 대조표다. 원본 코드 통합과 독립 회귀 검증은 별도다. 보고서의 remaining_executable_methods 빈 배열이나 experiments.executed=true를 그 자체로 소진 증명으로 쓰지 않는다.

| 과제 | 현재 구별해야 할 상태 | 이번 검토의 처분 |
|---|---|---|
| DBLP | 검색·단건·7내보내기 양성, 요청간격·파서 수리 후보 | 해결 후보로 코드·실험·통합 검증 대기. 모든 미래 접근의 보증 아님 |
| Semantic Scholar | bulk/match/관계와 최소 batch 양성, relevance와 full-parts batch 실패 잔존 | 추가 검증을 지정해 같은 thread 재개 |
| EuDML NLM | read timeout을 좁은 단건 경로에 조정해51.6초 응답 양성 | 수리 범위와 통합 검증 대기 |
| CORE 색인본문 | API의 indexed fullText 제한과 공개 PDF 성공은 별개 | 현재 no-key 필드 경계의 근거가 있음. 표본·정책 대조 검토 대기 |
| CORE work 다운로드 | 기존 세션의 새 화면·work/file 연결 조사 중 | 종료 판단 전, 계속 수행 |
| CORE output 다운로드 | custom retry 헤더 전달 수리. no-key API PDF 자체 성공은 아님 | 오류 안내 개선과 원문 기능을 구별해 검토 |
| CORE files01 | legacy522 뒤 공식metadata의동일문헌현재파일URL로회수 | 같은자료원·같은output·부분오류보존과통합검증대기 |
| SWH Vault | 특정원작업은new,다른작업은양성,같은대상의개별파일92개는회수됨 | 전체내용회수와특정원압축작업을구별. 서버작업이해결됐다고세지않음 |
| JSTOR video | 확인표본들의공식다운로드disabled,재생·자막은가능 | 해당표본의상태는근거있음. 플랫폼전체의영구미지원판정으로확대하지않음 |
| De Gruyter 깨진ZIP | 현재파일404,보존조회기간공백발견 |2003발행과2013–2026 ZIP조회범위를대조해추가조사재개 |
| De Gruyter DOI없는citation |ISBN도서의모달·원citation양성 | 식별자·도서판본·코드변경통합검증대기 |
| ScienceDirect export |지연렌더링제어와동일PII bulk선택경로양성 | 요청선택·해제·부분결과·통합검증대기 |
| ScienceDirect PDF |같은PII상세화면대조,양성PDF와음성2표본분리 | 미제공/권한/미식별레이아웃분류범위검토대기 |
| Taylor초록 |두편집자서문에는원초록부재,양성표본및10건대조 | 해당문헌판정근거있음. 임의페이지설명을초록으로승격하지않음 |
| DBLP KG TSV |원TSV자료형손실은유지,원JSON기반정확TSV를별도생성 | 별도생성형식의의미·원파일보존·통합검증대기 |
| SIAM52번째조건 |원UI/SDK17·17·0의미대조완료 | 새로운기능복원보다기존동작검증. 증거정체성검토대기 |
| Numdam날짜전용 |빈query/date를원wildcard와qdt경로에연결,976·0검증 | 입력정규화·날짜범위·교차페이지통합검증대기 |
| IEEE Media flag |55표본의false+Media반례0.별도MP4 parser결함은수리 | flag불일치의보편적부재를입증하지않음. MP4수리와분리검토 |
| Crossmark |원API의업데이트의미·방향·누락을구조화하고새증거수리 | 원자료의정보완전성과로컬처리정확성을구별해통합검증대기 |
| Springer구형HTML |특정문헌HTML부재·28쪽PDF양성,오류분류변경 | 표본판정과미식별레이아웃의일반처리범위를구별해검토 |
| Figshare과거구성원 |공개GraphQL로v1 2건/v2 3건과SDK양성 | 판본결속·커서·실패시보존·통합검증대기 |

## 새로 확인한 구체 공백

De Gruyter의 보존 crossref.json에는 DOI10.2202/1558-3708.1089의 published date가2003-01-11로 기록돼 있다. wayback-asset.json의year_queries는2013부터2026까지14개 연도만 포함한다. article HTML의2003–2026조회를정확한ZIP파일의같은기간조회로대체할수없다.2013이전URL이존재하지않았다는공식이관근거가있다면그근거로범위를닫을수있지만,그러한근거를현재보고에서확인하지못했다. 해당기간과원래플랫폼의실제링크를조사하도록재개했다.

Semantic Scholar는공식대체endpoint를연결한진전이있다. 그러나report의실측에는full-parts batch429와relevance429가남고,마지막새SDK batch양성은최소export-only다. 이를metadata·abstract·supplementary등모든요청parts의양성으로확대할수없다. 지원약속과실제검증의필드별대조,미검증full-parts와남은relevance범위를분리하도록재개했다. 미래에모든외부요청이항상성공한다는보장을요구하는것은아니다.

두추가지시는reviews/degruyter-broken-supplement.md와reviews/semantic-scholar-rate.md에있다. 실행폴더review-requests.json에기존세건과함께등록했고두원thread가다시running임을확인했다. 현재재개과제는총5개다. 이다섯개외에추가공백이없다고확정한목록이아니며,새근거가있으면같은기준으로다시연다.
