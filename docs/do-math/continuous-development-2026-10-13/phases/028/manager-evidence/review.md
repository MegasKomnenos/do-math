# 028 manager 검수

세 task의 A1~A4 조사 완료를 승인한다. 세 report를 전문으로 읽고 각각 `check.py report`를 통과시켰다. 제품 합격이나 G1~G8 완료 판정은 아니다. 다음은 029/doc-names 단일 work다.

## 실제로 대조한 범위

`verify.py`는 제품을 import하거나 실행하지 않고 현재 정본/미러/diff 2675파일을 027 manager 및 세 task의 시작/끝 SHA와 대조했다. 추가·삭제·내용 차이는 없다. 세 task의 report/objective/evidence 92파일을 검산 전후 보존했다. 배정 ID는 N01-001~288을 정확히 한 번 덮는다. 66/27/195절의 현재 제목·행과 이름 좌표 655/1223/634개, 현재 정의·시험 파일 118개의 SHA를 확인했다. 가운데 1223은 inline849와 fence374의 합이므로 세 작업의 숫자를 같은 이름 모집단으로 합산하지 않는다.

027 c3 원보고의 134선택과 고유 실제 row, 그중 문서 38passed 및 현재 Python875개 SHA를 대조했다. 이번 새 공식 실행은 0건이다. task들이 현재 문서 helper의 빈 진단을 제품 전체 성공으로 표현하지 않았고, 과거 전체 실행에서 이후 바뀐 helper를 통째로 재사용하지 않은 한계를 유지한다. 024 지정 문장 재사용은 같은 문장·현재 정의·해당 단언에 한정된다. 외부 이름은 해당 OS 소비자의 이름이며 Python 심볼 부재를 수리 이유로 삼지 않는다.

유지241절·기존 근거 재사용29절·문구 수정4절·검사 보강14절이다. 보강14절은 14개의 서로 독립적인 구현 과제가 아니다. 소유가 같은 반복 문장이 있으며 실제 후속 findings는 issue8개다. role F3 fact는 조사/보존 사실로 종결한다. 나머지 여덟 발견은 029 완료 조건에 각각 연결한다.

## 판단을 좌우한 원문과 코드

- operator F1: setup_lean/probe_cli의 main에 있는 실제 argparse 선언과 문서 helper의 적용 대상을 대조했다. 타도구 flag 차용 두 건의 빈 진단은 순수 helper 관찰이며, 당시 두 main의 반려 실행은 없었다. 029는 실제 parser를 부수효과 없이 공유할 출구를 만들고 실제 main도 같은 정의를 사용하게 한다. 정의 복제와 런타임 동작 개정은 허용하지 않는다.
- operator F2: README 설정과 초기화 grant 예시를 실제 config/DECISION/GRANT 검사에 연결해야 한다. `session_limitz`와 grant의 `budget_kind`는 실제 검사기가 반려하지만 문서 helper가 놓친 관찰이다. 완전한 설정 입력 예시도 저장 설정 전체를 필수로 적어야 한다는 뜻은 아니다. 생략 기본값·날짜/ID placeholder를 유지하며 권한 적용을 수행하지 않는다.
- operator F3: 초기화180행의 Codex7/Claude10 열거와 실제 identity_modules14/17, capability_identity의 전건 해시 생산을 대조했다. 누락7개는 control_protocol, values, codex_stream, provider_final, control_server, worker_request, cli_execution이다. 문구와 실제 클래스 집합을 연결한다. 어댑터 목록과 과거 모델 호출 근거는 바꾸지 않는다.
- cli F1: 현재 knowledge_io.import_candidate의 기존 ID 명시 반려, knowledge.replace_knowledge의 새 ID/supersedes/revision+1·옛 기록 보존·조건부 formal 재사용, register_kind_definition의 withdrawn 예외와 기존 직접 소비 단언을 읽었다. 487/512/514/546/573행은 현재 경계를 설명하도록 교정한다. 동일 ID import를 허용하는 제품 변경은 아니다.
- cli F2: execute_operation의 prepared 두 번 저장·transmitted/transmission_phase와 2xx/비2xx+효과부재/불확실의 세 결과를 읽었다. existing test_persist_before_send_confirm_and_redact 및 test_non_2xx_is_failed_only_when_effect_absence_is_evidenced가 이 독립 기대를 이미 단언한다. execution.running과 operation 원장을 구분해609행을 교정한다. 별도 schema에 running이 있다는 사실로 생산자의 전송 상태를 추정하지 않는다.
- cli F3: 최소 오타5개와 실제 operation/candidate_shape_errors/query 정의의 반려를 대조했다. 개방 candidate shape 통과와 summary 의미 검사 반려는 서로 다른 단계다. 029는 runtime 상태표·단일 설정키 기본값/enum·query direction·완전 knowledge JSON만 결속한다. 부분 객체와 명시 음성 예시는 그대로 구별한다.
- role F1: action_schema의 research producer kind=TEXT, submission의 활성 또는 같은 묶음 제안 검사와 기존 ExtensionMeaningTests 직접 단언을 대조했다. CLI748의 동적 enum 설명은 틀리며 문구를 교정한다. 신규 종류를 enum으로 막는 런타임 변경은 하지 않는다.
- role F2: CLI 네 검토 단계와 checkpoint fence의 오타/타단계 차용5개를 현재 stage_schema와 checkpoint_value에 연결한다. 027 helper는 다른 문서 좌표를 검사하므로 이번 CLI 문장을 자동으로 인증하지 않는다. 같은 정본 schema를 쓰되 절·선언·예제 부재도 실패로 드러내도록 한다.

이 판단의 코드 좌표는 `decisive-sources.json`, 관찰 원자료는 세 task의 minimal-counterexamples/pure-observations/schema-observations에 있다. manager는 도메인 반례를 새 실행한 것으로 기록하지 않았다. task의 보조 스크립트 실패도 원자료 그대로 보존하고 제품 결함이나 성공 수에 섞지 않는다.

## 배정과 의미 보존

029는 문구 네 묶음, 14개 최소 helper 반례, 모듈 목록의 누락/차용 반례와 필요한 부재 검사를 한 담당자에게 준다. doc_code.py/test_doc_code.py·공식 미러·캐시와 최종 관련 검사가 겹치므로 병렬 구현은 이득이 없다. 이미 끝난288절 조사는 재파견하지 않는다. parser 추출은 두 진입 스크립트의 정확 쓰기 범위에서만 가능하며 입력/기본값/모드/오류와 제품 의미를 보존한다. 후속은 기존 실제 소비 시험을 재사용하고 필요한 새 문서 결속만 추가한다.

공용 문서 변경은 C2의 이번 검수, C5의 독립 조사 종료/통합 소유, C8 모델 승계, C9 한정 재사용, C10 여덟 남김/유지 부분, C12 원자료 직접 추적이다. plan의 현재 phase와 근접 책임을029로 바꾼다. seams에는 같은 제품 정의를 소비하는 단일 소유라는 사실만 덧붙이며 S 계약 개정은 없다. 기존 G1~G8·역사 실패·L01 Q1/Q2와 UTF-8 byte 미충족·symlink1314 실제 반려 미검사·최종 관문을 삭제하거나 축소하지 않는다. `common-docs.diff`와 실제 전후 내용을 대조한다.

이번 관리 커밋은 원task92파일을 직접 추적하고 중복 archive를 만들지 않는다. 제품 변경은 없으며, 기존 dirty/untracked 제품·운영자 변경은 포함하지 않는다. 진행 로그와 stage/commit 행정 수신은 로컬 보관으로 정리 시 사라질 수 있다. 근거 진입점과 원자료 SHA는 preservation.json에 기록한다. handoff 검사 후 manager.json을 게시하고 정확 관리 파일만 커밋한다.
