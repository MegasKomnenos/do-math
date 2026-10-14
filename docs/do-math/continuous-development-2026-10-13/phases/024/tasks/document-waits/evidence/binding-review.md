# 024 document-waits의 한정 판정

시작 skills/diff 2675파일은 023 manager source-inspected와 전건 SHA가 같았다. 기존 canonical.py/repository.py, migration 자료와 작문 도구의 dirty를 그대로 보존했다. 작업의 정본 비교는 HEAD의 clean 여부가 아니라 start.json과 final.json이다. inputs-read.json은 배정 입력 46개의 실제 바이트를 결박하고, change-coordinates.json은 역사 P09/P11의 문장을 현재 제목·행·owner에 연결한다.

P09/P11의 기존 AST는 소비하거나 대입한 키의 이름만 확인했다. 실제 결정 입력이 없거나 dispatch_wait가 없고 값이 달라도 같은 소스 모양으로 통과했다. red/report.json의 한 시험에서 두 owner 모두 실제 경계 요구 없이 승인되는 두 subTest 실패를 보존했다. 새 WAIT_BOUNDARIES는 두 AST 조립만 대체한다. 일반 문서 순회는 두 경계를 명시적으로 위임하며, 구조 검사는 정확한 담당 메서드의 실제 문서 검사 호출과 owner 누락·오기·없는 메서드·다른 메서드 반례를 확인한다. 이 AST 사용은 담당 호출의 존재 검사이며 값의 의미 증거는 실제 실행에서 얻는다.

## P09 결정 입력

ReadinessConditionTests.test_documented_decision_value_uses_real_input_and_exact_types가 실제 evaluate_condition과 decision_is_current를 호출한다. 보존 사용자 source의 현재성, 일반 source SHA 변경, 사용자 아닌 actor, 없는 source·변조 SHA·변조 원문·change 부재를 구별한다. task_id 범위의 일치·불일치·평가 문맥 부재도 확인한다. bool/int/float의 자료형, 값 null, value 키 부재의 전체 change fallback과 빈 change를 독립적인 ready/not_ready 기대에 연결했다. 부재 결정의 정확 absence basis와 다른 가족 ID의 evaluation_error, 오류 전파·문서 표·JSON 문법은 기존 condition_validation와 planning_conditions 검사를 유지한다.

양성 change.value 문서 검사는 실제 값이 있는 입력의 철자를 검사한다. 이 검사가 get으로 읽는 value를 필수 출력으로 만들지는 않는다. 별도 부재/null 사례는 문서 필드의 양성 샘플을 대신하지 않고 함수의 fallback 동작을 검사한다. 누락·다른 wait 객체·true를 1로 바꾼 입력과 문서의 언급 삭제·없는 필드가 새 검사에 반려된다. kind/target/field는 추가 의미 조건으로 추론하지 않으며, 같은 비교값과 task_id에 대한 두 변경 모양은 현재 함수에 따라 ready다. 효과 적용·다른 변경 종류의 권한 전체를 이 연산의 판정으로 승인하지 않는다.

## P11과 D-06

PlanSettleTests는 실제 ResearchEngine의 _plan_settle_waits/_dispatchable와 Sim의 시계를 사용한다. 테스트 중 runtime 함수나 현재성 함수를 대역으로 교체하지 않았다. 문서의 dispatch_wait를 실제 queue action의 값에 결박하고 kind/since/limit_seconds를 독립 장면 사실과 비교한다.

| 정확 조건 또는 예외 | 실제 판정과 근거 |
|---|---|
| queue에 계약 검토 요청이 있음 | 최초 판정에서 plan_settle 대기를 생산한다. 기존 pending 검사와 새 실제 문서 검사를 사용한다. |
| 검토가 starting/running으로 등록됨 | 실제 _register_execution과 transition_execution 후 요청이 queue에 남으며 계획은 계속 기다린다. |
| 검토 요청이 queue에서 제거됨 | 다른 waiting_actions 객체나 남은 execution만으로 plan_settle을 생산하지 않는다. 배정의 다른 관문은 별도로 남는다. |
| 최초 기준 시각과 반복 판정 | 최초 now를 since/settle_started_at으로 유지한다. 299초에 다시 판정해도 기준 시각을 갱신하지 않는다. |
| 상한 전·동일 시각·이후 | 기본 300초를 독립 기대에 두며 299초에는 대기, 300초와 301초에는 해제한다. |
| requested_by 또는 recovery | 검토 요청이 있어도 이 대기를 우회한다. _dispatchable이 오래된 dispatch_wait를 제거한다. 이것은 다른 권한·현재성·용량 관문의 우회가 아니다. |
| 계약 검토 요청이 없음 | plan_settle을 시작하지 않는다. 다른 후보 준비 역할도 이 연구 계획 전용 대기를 사용하지 않는다. |
| 최초 준비의 초기 사건 | 첫 준비 action의 event_refs가 초기 pending_events를 소유한다. readiness 갱신만으로 소비하지 않으며 실제 수락된 준비 응답의 owner 경로 뒤 소비한다. |
| 실제 값이나 문서 결속 손상 | wait 부재·capacity 객체 차용·kind/since/limit 변경·since 삭제, 문서 언급 삭제·없는 필드가 반려된다. |

현재 SKILL.md의 「준비된 과제 중 다음 연구를 선택한다」는 최초 지식 유무에 따른 역할 선택, 초기 사건의 수락 후 소비, 준비·계획 병렬 진행과 계획 정산의 분리를 설명한다. D-06의 실제 8694693 diff에 있는 낡은 초기 준비 장벽 제거를 유지했다. CLI 문장에는 queue의 정확 표현·최초 시각 유지·같은 시각 해제·오래된 wait 제거를 보충했다. 모든 후보 준비를 끝까지 기다리는 장벽이나 실시간 timeout은 추가하지 않았다.

## 정확 N 문장과 정책 이름

section-semantic-review.json은 022의 N01-237 세 이름, N02-002 두 이름, N01-260 세 이름에 해당하는 현재 원문 문장 8개를 확인하고 실제 소비자와 기존 시험 ID를 연결한다. N 절 전체를 완료 처리하지 않는다.

입력 초과의 공개 retry는 pending 요청을 만들며 질문을 즉시 해소하지 않는다. 실제 재포장이 성공하면 해소되고 다시 실패하면 원 질문을 교체하면서 새 열린 질문과 두 실패를 보존한다. 기존 공개 flow에 retry 수락 직후의 open, 일반 pause/resume의 비해소, 원 source artifact 바이트 보존을 더했다. 기존 marker의 사용자 해소 이력 보존·provider deferral·재포장·close 반려와 실제 planner 선택→원 수행→독립 incomplete assessment를 유지한다. 선택 입력의 allowed profile, 계약·질문 현재성, 다른 역할 및 중복/미제공 선택 반려는 기존 overflow_connections와 공유 제출 검사로 확인한다.

운영 retry의 현재 소비는 선행 실행 종료·로컬 종료 확인·unknown 외부 효과 대조·봉인 manifest/support의 무결성을 요구한다. 같은 활동의 명시 continuation과 새 입력/공간, 기존 미편입 묶음·현재 프로필/권한 관문을 유지한다. FreshInputRetryTests의 실제 정상 경로 앞에 live predecessor와 manifest 불일치의 정확 반려·queue 무변경을 보완했다. 설치 repair의 별도 진단/target/권한/HOLD/잠금/실제 검사 근거는 기존 repair_execution 및 운영 repair 반려 시험을 재사용하며, retry를 설치 수정 권한으로 바꾸지 않았다.

policy-name-decisions.json은 conversation_loss_policy, disconnect_policy, model_policy, external_policy, adopt_default_review_policy의 현재 문장 8회와 실제 정의·owner를 기록한다. model_policy는 모델 대응 모듈 이름과 잠금 불일치 실패 분류라는 두 문맥을 구별한다. 나머지는 초기 채택·attach의 현재 정책 변경·외부 허가·기본 검토 정책 채택의 소유자로 연결한다. 문장은 유지하며 lexical 존재 검사의 통과를 이 정책들 전체의 의미 인증으로 확대하지 않는다. 그 broader owner의 남은 검토와 다른 N/P08/TRUST/L01은 후속 범위다.

## 과거 변경·검증·인도

B110~B114의 실제 diff·현재 소비와 존재 원보고 7개의 SHA를 대조했다. P09/P11 두 AST 추가는 B113 hunk에 있다. 그 두 조립을 실제 입력/대기 문서 검사로 교체하고 owner/별칭/함수 참조 및 다른 packet의 소비는 유지했다. change-coordinates.json은 doc_code의 field_schemas/scoped_field_issues 외 기존 함수와 engine_context의 기존 함수가 시작 바이트와 같음을 확인한다. 마지막 다른 소비자가 남은 AST helper는 삭제하지 않았다. PURE 네 원보고는 023의 검수된 경계와 원 좌표를 유지하며 역사 counts를 새 성공에 합산하지 않는다.

최종 선택은 현재 field_schemas/scoped_field_issues 소비 모듈 6개, 실제 조건/정산/입력 초과/운영 처분/질문 검사와 기존 제안 단일 지급·봉인 복원 담당으로 정했다. selection-decisions.json에는 023의 비소비 모듈 제외와 판본 근거가 있다. 이전 460개를 고정 누적하지 않았다. c2와 m은 동일 254선택/고유row가 전부 passed·exit0이며, 각875 Python과 비캐시 전후 SHA가 같다. 실제 반환 각107개와 제안 최종 입력 각18개를 보존하고 독립 전문 개수=1을 재귀 재검산했다. 이번 선택에는 symlink 검사가 없으므로 과거 Windows1314 skip이나 실제 탈출 반려 미검사가 해소된 것은 아니다.

첫 focus의 잘못된 unrelated binding 진단/fixture의 waiting_actions 부재와 corrected의 basis.status=None 기대 누락은 자기 helper/시험을 고친 뒤 최종 같은 ID의 통과에 대응시켰다. 첫 c는 자기 관찰 도구가 공유 operation_trace 데코레이터를 포장 함수 본체로 오인해 KeyError를 일으켰다. inspect.unwrap으로 관찰 대상만 교정했고 c와 c2의 제품 Python 판본/선택은 같다. 원 c의 실패·오류·not_run과 fixture 실패는 보존한다.

원 최종 suite가 resource 자식 cwd를 보존하지 않아 정확 resource 한 시험만 evidence-only Python audit hook과 함께 추가 관측했다. 제품 시험은 1passed·worker exit0이며 실제 두 CLI cwd는 scratch 아래 141자다. 첫 후처리의 argv 목록 가정은 Windows의 실제 문자열을 놓쳤으며 raw jsonl을 바꾸거나 시험을 반복하지 않고 별도 verify_cwd로 검산했다. 이 한정 관측 때문에 비용 캐시를 다시 동기화하고 최종 --check를 재실행했다. parent TEMP/TMP/TMPDIR는 C:/t/p024이고 그곳의 Git 상위 저장소 미발견도 확인했다.

보존 검산은 runtime/실호출 입력139·고정 경계258·corpus144/명시SHA150/Git raw-clean·host8/도구5·baseline910 및 완료 원task891파일을 확인했다. 새 문서 두 문단은 미래 역할 prompt와 설치 문서 hash에 영향을 준다. 과거 공급자/worker·host·Lean·held 예약·학술 실호출은 불변 하위 성질만 재사용하며, 새 문서 독해나 최종 전체 설치/T4 판본 인증으로 쓰지 않는다. 공식 미러의 사전 15변경 범위 확인·생성·캐시 동기화·최종 --check1336·skill-only를 완료했다. 실제 제품 변화는 양쪽28비캐시 경로와 비용캐시2경로다.

새 유료/예약/학술 호출, 기존 연구 재개/삭제, graphify 갱신 및 Git stage/commit/reset/checkout/push는 수행하지 않았다. 전체 일반/fresh T3/전수 변이/G7 최종판 연결/제품 수정 없는 최종 review와 P08/TRUST·다른 N/L01은 계속 남는다. 이번 complete는 A1~A5의 한정 task 완료다.

변경 diff의 보조 검산도 원실패를 남겼다. HEAD의 Git clean 바이트와 현재 시작 원문을 곧바로 같은 것으로 간주한 시도, 개행 전체 정규화 시도는 초기 혼합 개행 문서의 SHA와 맞지 않았다. 최종 diff-raw는 원 archive 또는 Git 바이트를 실제 start SHA와 대조하고, 두 문서는 확인한 역사 문장과 현재 나머지 원바이트에서 복원한 이전 문장이 start SHA와 정확히 같을 때만 비교에 사용했다. 따라서 changes.diff는 28비캐시 파일의 실제 시작/종료 차이다. 검산 실패 때문에 작업 트리나 Git을 복원하지 않았다.
