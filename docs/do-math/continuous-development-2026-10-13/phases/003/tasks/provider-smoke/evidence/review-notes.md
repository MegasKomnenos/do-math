# provider-smoke 판정 근거

## 실제 호출과 schema

현재 프로젝트/사용자 설정의 Codex 모델은 gpt-6-astra, Claude 모델은 opus다. effort는 짧은 파일 스모크용 low를 명시했다. Codex models_cache의 해당 모델 지원 effort와 Claude 설치 help의 low 지원을 확인했다. 전역 설정은 바꾸지 않았다. environment.json은 허용한 model/effort 필드만 담고 인증 자료를 포함하지 않는다. 호출 때 관찰한 CLI는 Codex 0.162.1과 Claude 2.1.289다. Claude가 보고한 실제 모델은 두 번 모두 claude-opus-5-5다. Codex 실패 stream에는 실제 모델 보고가 없다.

core_engine.CoreEngineMixin._response_schema의 보통 maintenance 분기는 action_schema(action)를 고르고, 역할별 추가 변형을 거치지 않으며, GovernanceEngineMixin._governance_schema도 그대로 반환한다. 마지막 with_integration_schema는 현재 action_schema의 envelope에 대해 같은 결과다. verification.json은 연구를 초기화하지 않고 실제 ResearchEngine 클래스의 이 무상태 분기를 호출해 전체 schema 동등성을 확인했다. 실제 세 호출의 output.schema.json 모두 이 결과와 같고 worker의 schema_sha256도 b4458e001449bf0c485d343cab7ba26b25f05969bdc7f6b12754e62bd8818dca로 일치한다. integration_bundles와 repair_responses는 삭제하거나 required로 바꾸지 않았다.

live-01은 두 공급자를 선택해 두 row 모두 실행했으며 exit 1이다. Claude는 유효한 최종 maintenance 응답, 정확한 nonce 파일, read_checkpoint의 valid 결과, 실제 Bash 읽기, 완료 stream 및 종료 barrier를 얻었다. 다만 nonce 읽기 tool_result에 checkpoint JSON도 이어 출력해 시험의 정확한 단일 JSON 비교에 실패했다. 실패 보고와 원출력을 유지했다. prompt에 checkpoint 검증은 조용히 하고 전용 nonce 읽기 결과에는 다른 출력을 붙이지 말라고 명확히 한 뒤 live-02에서 Claude 한 건만 다시 실행해 9개 checks가 모두 true, 공식 row passed, exit 0을 확인했다. 입력·worker·parser·판정 단언을 약화하지 않았다.

Codex는 실제 HTTP 400 invalid_json_schema를 반환했다. 정확한 메시지는 schema.required가 properties의 모든 키를 포함해야 하고 integration_bundles가 빠졌다는 내용이다. stream은 thread.started → turn.started → error → turn.failed로 완결되며 parser의 parse_complete=true, turn_failed=true다. 파일/checkpoint/최종 응답은 없고 worker CLI exit 1이다. Job barrier는 confirmed=true다. timeout이나 인증 오류라고 추정하지 않았다. 제품 schema/전달 경계를 바꿀 쓰기 권한은 없으므로 원출력을 보존하고 후속 수리를 요청한다. 선택 필드를 제거하거나 필수로 바꾸는 우회는 하지 않았다. 이 첫 오류가 스키마의 유일한 비호환 지점이라고 주장하지 않는다.

신규 ModelRunner 호출은 Codex 1회·Claude 2회, 총 3회다. Claude의 native num_turns는 각각 4와 5이며 이는 CLI 호출 횟수와 다르다. reported total_cost_usd는 0.22765720000000003과 0.2354444다. 합계 약 0.4631016은 공급자가 보고한 list cost이며 실제 청구액의 증명이 아니다. Codex 거부에는 비용·usage가 없어 0으로 추정하지 않았다. 준비 오류로 버린 model 호출, 자동 재시도, background 추가 호출은 없다.

최종 live-02 이후 smoke 모듈과 provider_live 도우미 및 제품 코드는 불변이다. 이후 Python 변경은 오프라인 corpus 검사 세 모듈뿐이며 녹화와 지침을 추가했다. live-01과의 provider_live 차이는 위 prompt 명확화다. Codex의 schema 거부는 prompt를 실행하기 전의 같은 schema에 대한 증거로 유지하되 최종판 성공 row로 바꾸지 않는다. 최종 전체 T5 성공은 없다. 검증한 마지막 정본 오프라인 23개 시험의 Python 해시는 인도 판본과 일치한다.

## PR15/B86/B87 한정 재검토

B86의 실제 도입은 46a67a7faaeac5488fb1600671a7eb0f1f573029다. diff에서 protocol_probe의 문자열 type 누락 교정, Codex error→turn.failed의 완결 실패 프로토콜 처리, 성공/실패 native 녹화와 Claude 재생 reader 추가를 확인했다. 현재 probe_cli는 명시 type을 유지하고 현재 codex_stream은 실패 turn의 error 사건을 parse_complete 실패와 구별한다. 이번 Codex 실제 오류가 그 분류를 다시 통과한다. 이 성질을 유지하며 작은 protocol_probe 수락을 전체 역할 schema 수락으로 확대하지 않는다. 일반 maintenance schema의 거부는 새로 확인한 별도 제품 경계 문제다.

B87의 실제 도입은 87fd1c1b406a575916a2b5ca795f4e0de11f4aca다. TaskOutput 이름 존재 검사를 task_id/tool_use_id 동일성, local_bash·is_backgrounded, completed 상태와 시작 < 완료 < selected result 순서로 교체하고 timeout 입력을 없앴다. 현재 probe_cli 및 직접 소비자 sim.test_operator_probe_contract의 identity·상태·완료 위치 교란 시험을 대조했다. 호출 이름을 필수로 고집하던 과거 조건을 복원하지 않는다.

historical-background-source에는 실제 이전 report·stdout·stderr·worker 상태·입력/schema·완료 파일·pending 파일을 바이트 그대로 복사했다. 원 stream 해시는 기존 corpus와 같고 현재 background_completed_before_result는 true다. 완료 파일의 nonce가 선택된 structured_output과 같고 실제 종료 barrier는 root_signaled=true, active_processes=0, process_ids=[]다. 원보고의 actual_wait_tool=false 및 passed=false는 그대로다. 현재 probe·Claude parser·ModelRunner·collector·termination 판정은 B87과 동일하다. claude_worker의 Git blob/작업트리 해시 차이는 CRLF/LF뿐이며 git diff는 없다. 같은 CLI 버전의 기존 native completion·파일·로컬 종료 성질을 재사용할 근거가 충분하다. 현재 maintenance schema 호출이나 연구 저장까지 과거 background 증거로 대체하지 않는다.

B86의 related/report/ledger-and-replay와 B87 report 네 원보고는 현재 모두 존재하며 기재 해시와 같고 각 selected↔rows의 95/12/7/100 passed를 직접 읽었다. historical-reports.json에 row를 보존했다. 이 수를 이번 검사 수에 합산하지 않는다. 이 slice에서 필요한 원보고 부재는 없었다. PR15의 나머지 B10/B16/B19/B35/B49/B52/B89나 다중 결과·취소·계정 한도 전체 녹화는 이번에 재검토 완료하지 않았다.

## corpus와 미러

세 신규 시도의 완전 stdout/stderr, schema, prompt, worker-status와 존재하는 selected final을 새 파일로 승격했다. 실패한 Claude 첫 smoke도 live_passed=false로 남겼으며 native structured response 성공과 구별했다. worker.build_argv로 보존 source_request에서 실제 argv를 재구성했고 exited worker의 argv_sha256과 모두 일치했다. 전체 원자료와 시작 worker PID는 각 live scratch에 있다. 원바이트 절단은 없다. 기존 corpus raw 및 비공급자 항목은 보존됐고 corpus 전체는 약 201 KB로 5 MiB 미만이다.

현재 command-surface 항목은 실제 adapter.help_commands와 version 관찰을 가리킨다. 이전 항목은 *-command-surface-20261004로 보존했다. Codex는 version 0.160.0→0.162.1, exec help에는 cyber-access-program 설명이 추가됐고 기존 요구 flag는 유지된다. Claude version/help는 이전 원바이트와 같다. 둘의 surface_report는 verified=true다. 이것은 모델/schema 수락과 다른 관찰이다.

정본의 structure.test_corpus, unit.test_corpus_replay, contracts.test_doubles_follow_corpus, structure.test_test_smells, unit.test_provider_live는 23/23 통과했다. 새 maintenance 녹화의 현재 schema·정확한 final 선택을 순회한다. 성공한 Claude native 응답은 실제 ClaudeModelDouble의 출력과 같은 parser로 대조한다. 현재 Codex 거부를 성공 대역과 동등하다고 만들지 않는다.

공식 미러 생성기는 배정 안의 31개 파일만 변경했고 --check 및 probe_cli --skill-only는 통과했다. 그러나 .agents/diff/_rules.json의 CLAUDE.md→AGENTS.md 치환이 raw CLI help에도 적용되어 capabilities/claude-surface-1.txt와 claude-20261013-1.txt의 원 SHA256 a58ca228…가 1804fa77…로 바뀐다. 이전 파일도 시작 snapshot에서 이미 불일치했다. manifest에 원 해시를 유지한 상태로 미러 4개 검사를 실행해 2 passed/2 failed, exit 1을 재현했다. 생성기 --check는 규칙을 따른 생성 일치일 뿐 녹화 원바이트 보존을 보증하지 않는다. 미러 재생 뒤 비용 캐시만 공식 생성기로 다시 맞추고 --check를 통과했다. .agents/diff와 writing-skills 생성기는 이번 writes 밖이므로 수정하지 않았다. 녹화 전체의 축자 보존 규칙을 별도 task가 수리하고 양쪽 재생을 다시 확인해야 한다.

G7의 Codex 역할 수락, Job/pythonw 전용 연쇄, Lean/Mathlib, 예약 등록·발화·해제, 학술 MCP, L01은 남는다. 전체 일반 검사·fresh T3·전체 함수 변이·T4 전체·G7 전체를 실행하거나 충족했다고 보고하지 않는다. 연구 인스턴스·OS 예약·패키지·인증 설정 변경, Git commit/reset/checkout/push, graphify 갱신은 수행하지 않았다.
