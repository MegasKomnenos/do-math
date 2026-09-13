SIAM Author 후보를 기존 CLI thread에서 이어 검토한다. 원본 저장소는 주 세션이 수정한다. 자신의 기존 사본·전용 브라우저·근거 디렉터리만 사용하고, USER-CRITERIA.md와 기존 파견 계약을 그대로 지킨다. 새로운 API 자격이나 별도 IdP 로그인 재시도는 하지 않는다.

읽기 전용 독립 검토에서 두 회귀가 재현됐다. exact_author_filter는 A_B AND Smith, A_B OR Smith, A_B NOT Smith, (A_B), A_B*를 invalid_options로 거부한다. 그러나 직접 판독한 Search Tips는 Author의 Boolean·wildcard 문법을 지원한다고 설명한다. Title + Author A_B + Author C_D도 add_exact_author의 단일 facet 제한에서 거부된다. 원래 여러 행의 질의를 보낼 수 있었으므로, exact facet으로 변환하지 못한다는 이유만으로 원래 질의를 새로 차단하지 않는다.

각 실패를 실제 입력 직전·직후·안정 화면과 요청으로 다시 확인하고, 각 이미지를 직접 열어 판독한다. 자유 Contrib 질의와 정확 ContribRaw facet의 의미를 구분한다. 두 Author 행, 같은 필드 안 AND/OR/NOT, wildcard/괄호/escape를 시험하되 원 공식 문법을 먼저 확인한다. 제공자 UI에서 실제 반복 exact-author 필터를 생성할 수 있는지, 반복 ContribRaw가 AND인지 OR인지, 자유 Author 행과 exact 필터가 어떻게 결합되는지 양성·음성 대조로 실측한다. 추정으로 반복 파라미터를 구현하지 않는다.

가능한 exact 복합 질의 해결책을 조사한 뒤 가장 간단한 의미 보존 구현을 선택한다. 최소한 단일 안전 리터럴의 exact 처리는 기존 표현을 훼손하지 않는 적격성 판정이어야 한다. 복합 질의가 exact 변환에 적격하지 않으면 지원되는 원 자유 질의를 임의로 거부하지 않는다. 다만 원 자유 질의의 underscore 무시를 알고 있으면서 의도한 exact 검색이 성공했다고 보고하지도 않는다. 일부 행에만 exact를 붙여 전체 질의를 조용히 바꾸지 않는다. 의미 차이는 caller guide와 결과의 실제 직렬화 근거에 명시한다. 새 옵션이 더 정확한 계약이라면 현재 도구·UI와 정합하는 가장 작은 형태를 검토하되 불필요한 추상화를 추가하지 않는다.

회귀를 오류 거부가 성공이라는 기대값으로 고정한 tests/test_siam.py와 registry·report·criteria-review도 함께 고친다. 빈 remaining이나 세션 반환만으로 미시도 방법이 없다고 정리하지 않는다. 발견된 로컬 문법·경로·관찰 오류는 수리 후 같은 입력을 재시도한다. 완료하거나 권한 안에서 실행 가능한 방법을 근거로 모두 소진한 경우에만 최종 반환한다. 원본 SIAM 기관 PDF 수리를 사본 변경으로 되돌리지 않는다.
