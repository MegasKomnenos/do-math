# phase 001 manager 검수

세 report를 전문으로 읽고 공용 문서를 바꾸기 전에 지정 Python의 check.py report를 각각 실행했다. 세 결과는 exit 0이며 원출력은 task별 report-check.stdout/stderr.txt에 있다. status complete는 배정된 분석의 완료로 인정하고 제품 G 완료로 해석하지 않는다.

verify_inputs.py는 제품 모듈을 import하지 않고 현재 원문과 기록을 대조했다. baseline 979파일의 해시 차이 0, 원래 19/11/61/12 ID·원문 대응, 원보고 14개의 해시 및 선택/row 대응, 현재 LAYERS 123모듈, 빈 T5 폴더를 확인했다. 최초 검수 도우미는 P2에도 original 키가 있다고 가정해 KeyError로 끝났고, P2의 historical_expectation을 해당 mapping 원문과 대조하도록 고친 뒤 exit 0을 확인했다. 이 도우미 오류는 제품 시험 실패나 제품 red가 아니다. 실제 제품 검사·변이·공급자 호출은 수행하지 않았다.

소스 검수의 중요한 결론은 다음과 같다. mutation의 정상 실행은 failing 집합 membership만 기억하므로 결과 부재가 False로 축약된다. mutant 자체의 CHILD_NO_RESULT 차단과 비대칭이고, _child는 실행 수·skip·종료 증거를 정상 통과 판정에 전달하지 않는다. loader 문자열에도 정상 성공 대조가 없다. 따라서 문서 P01보다 이 공백의 재현·수리를 먼저 배정했다. 현재는 정적 확인이며 phase 002 A1/A4의 실제 실행 근거가 필요하다.

운영 진단 문서의 동명 필드는 서로 다른 producer다. doc_code가 일반 continuation 및 operational_evidence의 필드로 recovery_materials도 통과시키는 연결을 원문에서 확인했다. bootstrap의 LIVE_INSTALLATION_ROOT 이름도 현재 파일에 없다. 이 두 사안은 P01/N03 후속 work로 남기고 B130~B134의 이미 검토된 실제 경계는 유지한다. T4의 Measurement 조건, T5 빈 선택 거부, adapter 분기 별도 보고라는 설계5.5도 직접 대조했다. 근거의 현재 해시와 발췌는 source-excerpts.json이다.

17변이 분할의 7파일 제외는 설계5.5/6.3·LAYERS·mutation module filter에 따라 판정했다. adapter5는 T4/T5의 별도 책임이며 runner2는 도구 시험과 실제 G4/G5 실행 책임이다. 이들을 현재 G6 layer1/2/3 분모에 포함시키려고 도구 대상을 바꾸지 않는다. 최종 함수 모집단은 fresh T3 뒤 확정한다.

## 공용 문서의 의미 변경

- C1/G2: 원래 보존61개를 연속 K-01~K-61로 읽힐 수 있는 표기를 원래 비연속 K ID 모집단으로 바로잡았다. ID 추가·삭제나 요구 축소는 없다.
- C2: phase 001 분석 완료와 실제 검수 범위를 덧붙였다. 기존 B129 실패/skip, B130~B134 부분 성공과 최종 관문 한계는 유지했다.
- C5/C8: 준비 시점의 미래형을 phase 001 종료와 phase 002 단일 task 상태로 바꿨다. 개발 서비스 기동을 제품 T5 실호출 성공으로 혼동하지 않게 했다. worker3·한 검사 묶음·기본 모델 정책은 그대로다.
- C9: 요구별 질문, 이전 검토의 실제 범위, 없는 임시 보고의 한계, 현 시험 경로와 역사 수단의 해석을 추가했다.
- C10: 현재 문서 목록·동명 생산자/옛 이름 문제·유한 후보 범위와 L01의 host/단위 미정을 추가했다.
- C11: 정상 기준 공백, 7파일의 변이 분모 제외와 별도 검증 책임, T4/T5·실환경 미확인을 추가했다.
- plan: 완료된 첫 분석 배정을 현재 결과/phase002로 교체했다. 전체 구현 네 묶음, 증거 재사용과 수리 조건, 최종 일반/fresh T3/변이/T4/T5/review의 책임은 유지했다. G7 확인을 문서 마감 이후로 계속 미루지 않도록 가까운 배정에 뒀다.
- seams: S ID나 제품의 외부 경계 계약은 바꾸지 않았다. phase002의 parent/child를 단일 task가 함께 다루므로 신규 병렬 제공자/소비자 seam이 필요하지 않음을 명시했다.

common-docs.diff는 git 기준선과 실제 편집의 차이다. context C3/C4/C6/C7 및 G1/G3~G8의 문언·ID가 유지되는지 별도로 비교한다. manager.pending의 finding 처분은 세 report의 전체 18개에 각각 대응한다. carry는 아직 끝나지 않은 일이며 G 충족이나 허용 잔여 판정이 아니다.
