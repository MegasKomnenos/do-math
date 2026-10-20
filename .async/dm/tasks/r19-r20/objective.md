# R19/R20: 실제 녹화에서 현재 parser와 소비까지

원문9-B의 공급자·비공급자 녹화 재생 질문을 같은 corpus manifest/직접 소비 시험 경계로 묶어 마친다. 다른 실행 중 작업의 결과는 필요하지 않다. 실제 원자료를 현재 parser·독립 판정·소비에 대응하고 확인된 가까운 오프라인 공백의 수리·미러·최소 확인을 이 task에서 수행한다.

SESSION_JSON workspace, task.json, 고정 inputs/context.md/plan.md/seams.md를 먼저 읽는다. 사용자 원문은 C:/math/docs/do-math/continuous-development-2026-10-13/sources의 user-decisions.md/model-policy-2026-10-14.md/document-batching-2026-10-14.md/requirements-index.json이다. 결함-범주.md의9-B, 단계-전환표-2026-10-03.json의 obligations9-B/provider_corpus_integration/external_corpus_replay, closure-map evidence의 R19/R20 및 requirement-state9-B/관련 보존 slice를 읽는다. 과거 run:은 continuous-development 루트다. 원자료는 읽기 전용이며 새 workspace에 docs가 없다고 제품 누락으로 판단하지 않는다.

## 현재 사실과 결과

현재 tests/corpus/manifest.json, structure/test_corpus.py, unit/test_corpus_replay.py, contracts/test_doubles_follow_corpus.py가 시작점이다. 구조 검사는 지원 공급자별 versioned stream·원bytes SHA·entry/file 선언을, 재생 READERS는 현재 parser의 결과와 manifest verdict를 대조한다. 이 목록 자체가 외부 출력 해석 함수 전건/지원 판본의 의미 검증은 아니다. 과거003~007 공급자·012 Lean·013 예약·014 학술·018 및 managers/0001 이관과 r21-r22의 녹화 scale 성과는 정확 판본·성질 범위로 재사용한다. 새 실호출 성공으로 합산하지 않는다.

1. Codex JSONL/Claude stream-json/공급자 실패 분류, Lean 출력·선언명, 예약 조회 JSON, scholarly·codex 설정, capability surface의 실제 해석 정의와 현재 사용 경로를 찾는다. 지원 판본은 현재 정본 정의/manifest/보존된 tool evidence로 판단하며 설치 CLI 업데이트나 웹의 최신 판본을 새 요구로 삼지 않는다. 보존 원자료의 실제 출처·명령·판본·SHA와 독립 verdict가 어떤 정상/경계를 입증하는지 연결한다.
2. 원문에 명시한 init 앞 rate_limit, quota/한도, 한 세션 여러 result 구간·task-notification·종료정리, 작은따옴표 선언, timeout키 있는 실제 설정, 역할 schema의 현행 모집단을 정확히 판정한다. 한 대표 maintenance 성공이나 합성 입력을 전체 역할/실제 녹화 전건으로 바꾸지 않는다. 과거 요구의 timeout 수단이 최신 사용자 결정으로 폐기됐으면 실제 계약과 근거로 처분한다. 없어진 parser/버전을 호환용으로 복원하지 않는다.
3. 충분한 기존 근거는 그대로 종료한다. 실제 녹화가 있지만 소비/추출/반려 단언이 빠졌다면 현재 실제 parser→consumer를 사용하는 가장 작은 시험과 필요한 직접 수리를 추가한다. verdict는 실제 원자료/명시 계약에서 얻고 현재 parser 출력을 그대로 기대값으로 복사하지 않는다. 별도 관리 registry나 범용 replay 프레임워크는 만들지 않는다.
4. 필요한 실제 녹화가 corpus 밖의 보존 원자료에 있으면 출처·해시를 대조하고 적법한 범위에서 완전한 원bytes/필요 provenance를 corpus에 연결할 수 있다. 기존 원bytes를 재작성/정규화하지 않는다. 자료가 없으면 정확 parser·판본·입력 사건·기존 합성 시험 범위·필요 실호출을 남겨 G7 판단에 연결한다. 합성 변형은 반례라는 표기를 유지하고 실제 녹화로 등록하지 않는다. 없는 quota 사건을 얻으려고 호출을 반복하지 않는다.

## 권한과 검증

task.json writes 내 corpus/manifest·해당 구조/unit/contracts 시험, 직접 parser와 허용 helper·미러만 수정한다. core/governance/review/schema, scheduler/parallel/call/formal engine과 저장/null 후속은 읽기 전용이다. tests/corpus의 기존 원자료는 보존하고 변경이 필요하다면 manifest의 현재 의미/독립 판정만 실제 근거로 교정한다. 과거 로그/docs의 원자료는 바꾸지 않는다. corpus .gitattributes/raw byte·미러 규칙을 유지한다. generator나 설치 설정 변경이 필요하다고 추측해서 범위를 넓히지 않는다.

새 외부 모델/Lean/예약/학술 실호출·설치 변경은 이 배정에 없다. 현재 원자료와 코드로 충분한 관계는 정적으로 끝낸다. 새 시험/수리의 실제 불확실성에 필요한 최소 ID만 공식 run_tests.py jobs1로 실행한다. 과거 전체 counts나 다른 판본의 성공을 더하지 않는다. 최초 실패/fixture 오류·선택/실제row·exit·SHA·미확인·소프트초과를 남긴다. 공식 mirror build/check 완료 뒤 changed-pair bytes를 확인하고 동일 미러 시험은 반복하지 않는다. 비용캐시2개는 evidence 보존 후 own base로 복원한다.

report.json은9-B의 충분한 성질/새 수리/정확 raw 부재를 구별하고 check.py report C:/math/.async/dm r19-r20 PASS를 확인한다. G4~G8·L01·Windows1314의 미결을 전체9-B 완료로 숨기지 않는다. 공용소스/문서/queue/state·다른 task·Git index·graphify는 수정하지 않는다.
