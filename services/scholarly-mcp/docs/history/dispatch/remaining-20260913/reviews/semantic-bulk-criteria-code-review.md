Semantic Scholar의 기존 CLI thread에서 bulk 검색 창 계약을 추가 검토한다. 자신의 기존 사본·전용 실행·근거 디렉터리만 수정한다. USER-CRITERIA.md와 기존 무자격·무자동fallback 계약을 유지한다. 429를 연타하거나 새 API 자격을 요구하지 않는다.

주 세션은 공식 https://api.semanticscholar.org/api-docs/snippets 의 Paper bulk search와 공식 tutorial을 확인했다. bulk는 원 token으로 다음 묶음을 받고 호출당 최대 1,000개를 반환한다. relevance의 offset/limit와 다른 계약이며 문서의 bulk 파라미터 목록에는 limit가 없다. 후보 semantic_scholar.py는 bulk에 limit를 보내고 len(rows)>limit이면 range_mismatch로 거부한다. 정상 두 문헌·total2 응답을 MockTransport로 주고 limit1을 호출하자 실제 range_mismatch가 재현됐다. 이전 정확 제목 한 건의 성공만으로 이 계약을 검증할 수 없다.

공식 문법과 실제 응답을 확인한 뒤 여러 결과가 나오는 적절한 공개 query로 limit1·소량 창·원 페이지·token을 비교한다. 입력 직전, 실제 응답 직후, 안정 화면을 캡처하고 직접 이미지 판독한다. 원 JSON과 화면·요청의 같은 시점을 결속한다. 429이면 그 응답과 다른 시점의 양성을 구별하고 제공된 안내와 적절한 간격을 지킨다.

정상 provider batch를 오류로 버리지 않도록 가장 간단한 의미 보존 구현을 선택한다. 기존 도구의 검색 창 계약과 일치해야 하며, 정상 기능을 피하려고 모든 호출자에게 limit1000을 강제하지 않는다. 원 페이지 일부만 반환하면서 다음 token으로 곧장 넘어가 나머지 문헌을 잃으면 안 된다. 원 응답과 남은 창을 보존하고, 필요한 경우 기존 artifact/cursor 방식을 재사용하되 query·options·source 결속을 검증한다. total은 추정 일치 건수라는 공식 의미도 caller guide에서 구별한다. 네이티브 전체 묶음 반환이 이미 허용된 계약이라면 그 실제 계약과 호환성을 먼저 입증하고 임의로 limit 의미를 바꾸지 않는다.

작은 요청 창보다 큰 정상 페이지, 페이지 내부 후속 조회, 마지막 남은 문헌, 다음 native token, 서로 다른 query/options cursor 오용, 반복·빈 중간 페이지를 오프라인 회귀와 필요한 실서비스 대조로 확인한다. 이전 batch/title-match/parts/BibTeX 수리는 보존하고 최종 원본 통합에 필요한 diff를 정리한다. 완료하거나 권한 안에서 실행 가능한 방법을 근거로 모두 소진했을 때만 반환한다. 기존 exhausted는 익명 relevance rate 상태의 판정이었으며 새 구현 결함을 닫는 근거가 아니다.
