# g05 재개 수리와 확인 근거

이 문서는 새 작업자의 수리 진행 기록이다. 전체 382건 완료를 선언하지 않는다. 현행 실행 진입점은 `resume.py`이며 공통 `work_queue.build_queue`가 반환한 후보를 소비한다. 기존 `collect.py`, `acm_collect.py`, `summon_collect.py`의 독립 `main`은 이전 실행 방식이다. 현행 진입점은 그 함수들을 필요한 단계에 호출하며, 이전 `main`의 완료·범위 표시를 종료 판정에 쓰지 않는다.

| 피드백 | 판정과 근거 | 수리·검증 |
|---|---|---|
| 원문 found이면 초록 미해결을 제외 | confirmed. 기존 ACM main의 fulltext만 확인하는 skip 분기 | 새 inventory는 구성요소별 검토를 유지한다. `test_restart.py`의 저장 원문·미해결 초록 시험, `tdd/restart-red2.log` → `restart-green.log` |
| scope_review만으로 후보 제외 | confirmed. 기존 Summon main의 summon_beyond_holdings skip 분기 | 현행 resume는 공통 큐·검토·실제 증거를 소비한다. 전건 inventory 후에도 382건의 실제 남은 일이 표시됐다. |
| 첫 정상 PDF가 다른 자료이면 후속 후보 미방문 | confirmed. ACM 식별 실패 break 및 Summon 무조건 break | 실제 Lee 논문과 다른 서평 PDF 바이트를 사용한 흐름 축소시험. `restart-red.log`, `restart-acm-pdf-red.log` → 대응 green 로그. 네트워크는 대역이며 실제 PDF와 별도 실제 UI 회귀를 구분한다. |
| 개별 다운로드 오류가 다른 후보를 막음 | confirmed. Summon PDF 루프의 예외가 외부 전체 source try로 나감 | 다운로드별 오류 보존 후 다음 링크 방문. `restart-link-error-red.log` → green. HTTP503와 Retry-After 시험은 `restart-http-red.log` → green. |
| Summon 잘린 결과 | confirmed. one은 첫 /api/search 응답만 처리 | 관찰한 다음 UI 링크를 사용하는 next_search_page 및 전체 페이지 순회 search_pages를 연결했다. 실제 ho=f·query·pn=2 시험은 `restart-pagination-red.log` → green. 후속 페이지에만 있는 후보의 수신 시험은 `restart-all-pages-red.log` → green. |
| 영역 제안과 실제 내용 검토의 인계 | confirmed. regions 독립 main은 목록만 저장 | 외부 PDF/영역 목록을 work_state로 인수했다. root 예약 10건은 첫·끝 원본 렌더와 ACM 서지를 직접 읽고 기록했다. 5건의 원문 초록 구획도 직접 확인했다. |
| 영역 제안의 실제 경계 | confirmed. Atallah PDF의 분절 OCR 행 때문에 오른쪽 문장이 잘렸고 Baeten 초록이 누락됐다. Lieberherr의 gEY WORDS OCR 표지 때문에 키워드가 포함됐다. | 같은 실제 PDF의 실패 시험을 먼저 보존했다. 분절 행 결합과 해당 키워드 표지를 최소 수정했다. `restart-fragmented-*`, `restart-gey-*`; 기존 사례 포함 7개 영역 시험 통과. 제안 자체는 의미상 완료가 아니다. |
| 첫 inventory 뒤 새 후보가 목록에서 빠짐 | confirmed. 초안 resume는 version 변경 시만 inventory 실행 | 매 대상 전후 refresh_inventory로 새 후보를 합류시키고 기존 닫힌 처분은 유지한다. 공통 pending_work의 추가 작업도 인계한다. `restart-refresh-red.log` → green. |
| 완전한 DB 초록의 회수 | confirmed. 후보 상태로 남아 있는 다문장 초록들이 있었다. | 실제 UI 응답의 제목·DOI·연도·저자·유형과 후보 원문을 대조한다. 완결된 대상 본문은 database_indexing_abstract, authorship unknown, attribution과 원시값을 보존한다. citation-only·잘림·서로 다른 제공 버전은 직접 검토한다. `restart-saved-review-*`. |
| DB 본문과 하이라이트 혼합 | confirmed. 실제 제공 문자열에 선행 또는 후행 bullet highlights가 합쳐져 있었다. | 본문과 bullet 줄을 분리하고 원시 combined artifact를 보존한다. 서로 다른 abstract 배열 값은 자동 결합을 철회해 비교 대기로 둔다. `restart-highlights-*`; --reassess --offline로 기존 완료 후보까지 재적용했다. |
| 일반 다운로드 링크의 문헌 범위 | confirmed. 관련 도서의 -pdf URL과 참고문헌 다운로드가 후보가 될 수 있었다. | `link_scope.py`는 실제 문헌 문맥·DOI·PII·검토한 상위 자료에 결박된 제어를 선택한다. 추천·참고문헌·계정 저장·전역 디렉터리·참고문헌 내보내기는 제외한다. 전체 책·수록집·미리보기는 역할을 보존하고 원문 범위를 별도 검토한다. 실제 Perlego·Springer 반례와 책·NIPS 양성 UI 시험이 통과했다. |
| non-PDF 응답과 초기화 실패의 보존 | confirmed. Preparing your download HTML과 빈 Loading DOM을 PDF·접근제한으로 해석할 위험이 있었다. | 실제 응답 본문과 오류 원인을 보존하고, 빈 원시 파일은 보존한 채 진단 JSON을 증거로 사용한다. 실제 View PDF 활성화·클릭 결과도 따로 기록한다. CPE는 구독권한 거절로 단정하지 않는다. `test_science_direct.py`, `test_collect.py`의 재시도·응답·초기화 회귀가 통과했다. |
| 전문 HTML의 MathJax와 그림 보존 | confirmed. 본문 외 참고문헌·제목에도 CHTML 수식이 있었다. | 실제 MathItem의 원래 MathML과 DOM 이미지에 대응하는 브라우저 응답을 보존한다. 0500a5b의 전문 HTML은 오프라인에서 수식 1,309개·내장 그림 두 개·참고문헌 38개·HTTP 요청 0을 직접 확인했다. 원래 MathML을 회수하지 못한 복잡한 수식은 검토 대기다. 2bb97c의 단일 Unicode k는 동일 파일의 실제 표시를 읽은 좁은 수동 승인이다. |
| 기존 수동 PDF 판독의 재사용 | confirmed. 014dd490 서평의 제목 변형으로 자동 식별이 탈락한 뒤 기존 verified 판독이 공통 검토에 인계되지 않았다. | `review_reuse.py`는 명시적 판독 목록·현재 동일 PDF SHA·대상 DOI·검토 이미지·현재 채택 사유를 대조한다. 실제 서평자 Haris Aziz 사례와 철회·해시 변경·다른 DOI·판독 목록 없음의 음성 회귀가 통과했다. |

각 `resume.py` 실행의 `runs/<시각>/manifest.json`에는 실제 PID, 인자, 로컬 코드 SHA256이 있다. `metrics.json`과 `check.json`은 실행 관측과 실제 공통 전체 검사 결과다. `check_passed=false` 또는 `complete=false`인 실행을 완료로 보고하지 않는다. `--offline`은 저장 증거 재판정이며 브라우저 조사 범위를 늘리지 않는다. `--reassess`는 판별 규칙 변경 뒤 기존 완료 후보도 다시 평가할 때 사용한다.

현행 HTML 흐름은 `resume.py` → `science_direct.py` → `native_article.py`이며, `resource_snapshot.py`와 `fulltext_html.py`가 원래 수식·그림 보존과 오프라인 검증을 담당한다. 저장 증거 재사용은 `saved_article.py`로 검증했다. 코드판본과 실제 실행판본은 manifest로 구별한다. 체크포인트의 최종 코드 100개 시험과 부분 파일 검사는 통과했으며, 70건 실제 HTML 순회의 제공 오류·정상 전문을 문헌별로 기록했다.

남은 일은 미해결 서지·초록·원문과 출처 범위의 판독, 필요한 UI 재실행, 유효한 기존 판독의 공통 큐 인계와 전체 완료 검사다. non-PDF 응답 보존과 HTML 수집은 구현됐지만, 개별 자료의 외부 제공 오류가 모두 해결된 것은 아니다. 새 함수의 존재나 한 실행의 종료로 전체 수집 완료를 선언하지 않는다.
