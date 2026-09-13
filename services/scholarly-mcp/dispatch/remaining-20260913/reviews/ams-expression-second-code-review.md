AMS의 같은 CLI thread에서 최종 후보의 세 회귀를 고친다. 자신의 사본·전용 브라우저·근거만 사용하고 기존 source/인증 경계와 사용자 세 기준을 유지한다. 원본 통합과 Git은 주 세션이 담당한다.

첫째, options.expression이 있으면 공통 if cursor 분기에서 오류를 내지 않고 cursor를 버린 채 공개 검색까지 진행한다. cursor='opaque'와 유효 Title expression을 주자 public_page('ams-expression-public')가 호출되는 것이 독립 로컬 재현됐다. 원격 접근 전에 기존 cursor 미지원 계약을 일관되게 검증한다. expression이라는 이유로 호출자 입력을 무시하지 않는다. start/limit/export/options 검증도 같은 경계에서 회귀로 확인한다.

둘째, 새 세션 첫 AMS 호출이 expression+export=xlsx이면 export_products가 기관 페이지를 만들기도 전에 gateway.pages['ams']를 요구해 export_page_unavailable로 실패한다. 검색은 ams-expression-public만 열기 때문에 생긴 회귀다. 각 ProductCode의 기관 검색이 실제 페이지를 준비한 뒤 검사하도록 순서를 고치거나 같은 목적의 가장 작은 수리를 한다. expression XLSX를 새로 거부하지 않는다. 빈 세션에서 expression 검색, 해당 문헌 선택, 실제 XLSX 회수와 ID/행 대조까지 새 SDK로 검증한다.

셋째, 지원한다고 안내한 3항 Title OR의 algebra topology analysis가 range_mismatch로 실패한 원 응답을 다시 연다. 독립 검토가 HTTP200, TotalRows8685, RowsPerPage12, Products11과 실제 화면의 Showing 1 - 11 of 8685 results를 대조하고 후보 product_records에서 같은 실패를 재현했다. RowsPerPage를 항상 채워야 하는 정확한 수신 수로 간주할 근거가 없다. report의 strict parser 정당 판정과 실패 표본을 geometry로 바꾼 완료 근거를 수정한다. 정상 다른 예제 성공은 원 실패를 해결하지 않는다.

같은 algebra topology analysis를 실제 원 문법·같은 입력으로 다시 제출하고 직전·직후·안정 이미지를 직접 판독한다. 해당 원 응답과 다음·인접 페이지의 실제 표시 범위, page number, 제품 ID, TotalRows, 페이지 용량을 대조한다. 용량보다 적지만 양수인 정상 페이지와 자료 부재를 구별한다. 이미 확보한 정상 검색 창을 버리지 말고, 더 필요한 행은 실제 다음 페이지로 이어 받을 수 있는지 확인한다. 인접 페이지에 ordinal 공백이나 중복이 있으면 그것을 숨겨 정확한 창이라고 주장하지 않는다. 충분히 확인된 prefix와 근거를 partial로 보존한다. 빈 중간 페이지·변하는 total·중복·마지막 페이지 경계도 필요한 회귀로 확인한다. 단순히 strict 검사를 모두 없애는 수리나 임의의 결과 합침은 하지 않는다.

문제의 직전·직후 화면뿐 아니라 정확한 응답·실패 단계·수리 후 같은 입력을 결속한다. 로컬 경로·시간초과·계측 오류는 고쳐 다시 실행한다. 세 결함의 회귀와 현재 Unicode/중첩 OR/Title+Author AND/BOOKREV 제어를 함께 검증한다. source가 실제 제공하지 않는다고 확인한 legacy builder 상태와 위 로컬 오류를 구별한다. 완료하거나 권한 안의 실행 가능한 방법을 근거로 모두 소진한 때만 반환하고, 남은 문제를 성공 예제로 가리지 않는다.
