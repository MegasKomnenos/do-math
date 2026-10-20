# manager 0010: r03 부분 수용과 관찰 저장 계약 수리

이번 inbox의 완료 사건은 r03이다. 실행 중 r14·r10의 정의와 고정 입력은 유지한다. manager 도중 도착한 다른 완료 사건은 다음 inbox에서 판단한다.

## 수용한 결과

r03의 실제 변경은 정본 시험/helper 7개와 미러 7개이며 보고와 일치한다. 변경 전 공용판은 각 base와 같았고 미러 7쌍도 바이트가 같다. 관련 runtime·helper·기존 시험 20파일은 base/workspace/공용판에서 같다. 기존 함수 AST를 대조해 trust 표본 생산자와 일반 pair의 신뢰 파일 단언 추가 외에는 기존 함수가 유지됨을 확인했다. report 검사 PASS 뒤 workspaces.py integrate로 14파일을 충돌 없이 반영했다. queue.accepted에 r03을 넣되 report.status=partial과 F2 미결을 유지한다. 근거는 source-review.json·inspect_result.py와 tasks/r03/integration.json이다.

F1은 실제 setup의 record_installation/rerecord/write_trust_request에서 게시한 요청을 pair가 읽도록 수리됐다. core와 project 검색 경로 0/1/2 × 새 기록/재사용/재기록의 12표본에 실제 source/evidence·compile 횟수·baseline·정확 binding 단언이 있다. 공개 등록·환경/runtime binding 저장·재시작은 두 대표를 확인하며 12개 전부의 공개 owner 실행으로 확대하지 않는다. compile 실패·판단파일 이동 반려, metadata 변경 뒤 재사용 거절과 기존 record 불변을 검사한다. 외부 Lean/Job/Lake는 기존 대역이므로 실제 설치나 실Lean 인증이 아니다.

F3은 tracker 전체 record를 StateContract의 실제 수신 단위에 연결했다. observations는 metadata map이고 나머지 세 가족은 개별 record다. source·delivery/ack·hold·응답/rule_update와 유효 관계/세 mode를 직접 생산해 검사한다. C-03은 bound transport의 open→boundary→rule proposal 응답→정상 제출 execution stopping→저장/restart를 거친다. 경계 영수증은 executions.safe_boundary_report.receipt_id에서 control_receipts로 연결된다. 의무 answered와 execution stopping이 이번에 확인한 종결 경계이며 native 종료나 tracker 메모리 복원·진행성 전체를 증명하지 않는다. 기존 rule_ids pair는 여전히 조각 검사다.

최종 원보고는 16선택·16고유 passed·task 관측 exit0이며 제출판 Python875개 해시와 모두 일치한다. fixture 오류·실행 중 변경은 없고 23.4초와 개별 소프트 예산 초과 6건을 보존한다. 초기 records/tracker 실패는 새 fixture/기대 오류였고, 교정 전후 보고를 모두 대조했다. 초기 실행과 최종 실행 counts를 합산하지 않는다. B76 원보고 SHA와 지정 6행을 확인했으며 현재 통과에 더하지 않는다. 관련 source와 정확 단언의 한정 재사용이다. 캐시 2개는 증거 보존 후 base로 복원됐다. manager는 제품 시험을 추가 실행하지 않았다.

## 남은 문제와 다음 배정

F2는 현재 정상 기록이 저장에 실패하는 문제는 아니다. 관찰 수신 스키마에 현행 생산자가 없는 선택 필드 16개와 의무 status=closed가 남아 설계 3.3/A20의 역방향을 충족하지 못한다. record_schemas/schemas.py와 observations의 fact/observe/record_self_check_response, core_engine의 실제 저장 쓰기를 대조했다. fact의 event/elapsed_ms는 현행 event_json/event_sha256/monotonic_offset_ms와 구별하고, response/reason은 response_json/errors와 구별한다. response 내부 rule_update의 필드를 observations top-level 생산 증거로 쓰지 않는다. checkpoint_status도 비저장 reminder에만 있다.

r03-fix는 이 네 가족의 저장 스키마 정리, 실제 생산 표본을 기존 PAIRS의 전체 필드 역방향에 연결하는 수리, 낡은 필드/closed 반려와 현재 저장 단언, 필요한 미러·설명을 한 묶음으로 맡는다. 현행 의미에 필요 없는 허용 필드를 제거하며 생산자에 옛 필드를 보충하거나 호환 경로를 만들지 않는다. observation_facts의 event 대체 oneOf를 없애더라도 현행 JSON/SHA/offset 필수 조건과 내용 검사를 유지해야 한다. 중첩 rule_update와 실제 필수·선택 필드를 지우는 식으로 검사 모집단을 줄이지 않는다.

선행은 수용한 r03만 필요하다. r14의 진행성 및 r10의 입구 반려는 별도 결과이며 시작 배정을 바꾸지 않는다. r03-fix는 두 task의 생산자·owner·진행성 파일을 수정하지 않는다. 그 task들이 runtime을 수정해 제출하면 통합 manager가 좁아진 저장 계약과의 관련 영향을 함께 판단한다. 비용 캐시 외 쓰기 교집합은 없다. 전체 R06, 다른 1-A/2-A·PR08/PR18·K/P2, G4~G8, L01 및 Windows1314 미검사는 남긴다.

공용 문서·objective를 먼저 갱신하고 queue.pending.json을 check.py queue로 검사한 뒤 검사한 파일 자체를 원자 교체한다. status는 active다. 공용 게시 후 이번 manager의 변경을 마친다.
