g02의 2026-09-08 재개 피드백을 현행 코드와 저장 증거에 대조한 판정이다. 소비자는 복구 구현과 실제 수집 범위를 검사하는 루트다. 전체 완료 판정은 `restart-contract.md`와 공용 검사기가 맡는다.

| 피드백 | 판정과 근거 | 수정과 검증 상태 |
|---|---|---|
| 단계 표시로 미해결 문헌 제외 | confirmed. 기존 `run.py`의 `iter_batches`와 main이 두 collection_stage를 건너뛰었다. 첫 실제 결과는 초록 found·원문 unresolved인데 제외됐다. | `test_restart.py` 실패 재현 후 배치 선택을 수정했다. 현행 진입점 `resume.py`는 공용 pending_work와 명시적 작업 상태를 소비한다. |
| HTTP 500·묶음 오류 전체 종료 | confirmed. `blocker.json`의 VER-2a20cc1ccaddd97f89693ecf는 실제 HTTP 500이며 기존 두 예외 분기가 SystemExit(1)을 실행했다. | 배치 실패는 개별 재시도로 돌린다. `resume.py`는 검색의 유한 재시도와 작업별 오류 저장 뒤 다음 작업 계속을 구현했다. 축소 실패 응답 시험을 통과했다. |
| DOI/ISBN 없는 정확한 서지 대응 | confirmed. document_matches의 식별자 분기가 다른 서지 일치에도 False를 반환했다. | 실제 양성 응답에서 식별자만 제거한 재현을 통과했다. 제목·모든 저자 성·연도·유형·권호쪽을 대조하며 부제 분리는 권과 시작·끝 쪽 앵커를 요구한다. DOI 충돌과 MathML 차이 회귀를 유지했다. |
| 단건 검색의 잘린 페이지 | confirmed. 기존 코드는 unvisited_search_pages만 쓰고 다음 페이지를 방문하지 않았다. | 실제 UI 다음 링크를 확인한 뒤 `Digraphs Bang-Jensen 2009`의 55건을 3페이지에 걸쳐 전부 처리했다. 페이지 전환 뒤 다음 링크가 다시 표시되는 것을 기다리도록 수리했다. 넓은 digraphs 28,581건은 UI 탐색 관찰이며 생산 실행의 의무 범위가 아니다. |
| 보존한 Article·출판사 링크의 원문 단계 누락 | confirmed. provider_link와 observed_source_links를 저장한 뒤 실행할 원문 루프가 없었다. | `inventory`가 입력 source_urls·Article·대응 Summon 링크를 모두 작업으로 만든다. 실제 IEEE/기관/Summon 경로와 Springer 다운로드를 방문했다. Digraphs의 20쪽 앞부분·73쪽 뒤부분은 전체 원문으로 승격하지 않았다. |
| 책의 완전한 DB 초록을 유형만으로 제외 | confirmed. run.py의 record_type 분기가 책을 additional_content로만 저장했다. 기존 abstract_reclassify의 후처리와 실행 경로가 분리돼 있었다. | `consume_response`는 문헌 유형으로 초록 후보를 제외하지 않는다. 완결성·내용 유형 판별 뒤 실제 판독 후보로 연결하며 2009 Digraphs 응답 시험을 통과했다. |

재현 기록은 `tdd/restart-red.txt`, `resume-red.txt`, `pagination-source-red.txt`, `continuation-red.txt`와 각 통과 파일에 있다. 수정 시험은 직접 Python 실행으로 통과했다. 실물 Summon 양성·0건·책 판본 전환 세 건도 통과했다. 재개 계약의 보완에 따라 실물 TDD로 검증한 문헌 대응·초록 유형 규칙을 실제 입력에 적용한 판정도 코드·시험·증거를 결박해 자동 기록한다. 손상 문자, 추천사, 불확실한 판본·PDF는 별도 검토한다.

추가 실물 회귀는 `damaged-abstract-*`, `actual-bibliography-*`, `endorsement-*`, `mr-title-*` 기록에 있다. Gradient flows의 단어 내부 물음표와 훼손 수식이 있는 원시값은 보존하고 확보 판정을 철회했다. AMS 책의 primary 유형은 Journal Article이지만 같은 응답의 Book/eBook·DOI·ISBN·서지가 일치하는 경우와, Hartley의 정확한 제목·저자·연도·eBook 응답에 ISBN이 없는 경우를 재현해 수리했다. DB 추천사와 설명문도 분리했다.

실행 지표는 다운로드 요청 수 `download_attempts`, 정상 PDF 응답 수 `pdf_responses`, 새로 저장한 중복 없는 파일 수 `new_pdf_files`로 구분한다. 초기 2건 실행의 `downloads=8`은 요청과 정상 응답을 같은 필드에 더한 구형 값이며 요청 수로 읽지 않는다. 현재 실행은 식별자 최대 6개 묶음 검색을 재사용하고 묶음 검색·분할·후보 재사용 수를 기록한다.

`resume.py --saved-only`는 기존 870건의 증거를 읽어 작업 목록을 구성했고 부분 검사 exit 0을 얻었다. 실행 PID·인자·코드 SHA와 검사 출력은 `runs/20260908T143740Z-24452.json` 및 짝을 이루는 검사 파일에 있다. 전수 완료는 아직 아니다.
