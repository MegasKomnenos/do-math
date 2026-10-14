# 현재 경계 계약의 사용

phase 001의 독립 분석과 phase 002~008의 work는 종료됐다. 변이 결과 형식은 tests/support/mutation.py의 validate_result와 도구 docstring이 정본이다. 공급자 호출의 의미는 contracts.action_schema·ModelRunner.run·model_call.classify_run·real_ports·adapter/parser가 정의한다. 현재 결과와 남김은 context C11/C12에 있다.

phase 006의 비결박 경로는 중앙 제출 control_binding 없이 CLI 최종 응답을 직접 받는 ModelRunner 호출이다. 이 Codex 전송의 정본은 do_math/provider_final.py의 output_contract·semantic_output이다. ModelRunner가 원 schema를 output.schema.json에 보존하고 전송 schema를 transport.schema.json으로 넘긴다. source_request·worker snapshot/hash·native final과 종료는 기존 수집 경계를 거쳐야 한다. classify_run은 전송을 해석한 의미 값을 canonical 검사와 원 schema로 검증한다. 선택 필드 부재/null/값과 원 제약은 유지한다. Claude는 직접 JSON을, control_binding은 별도 중앙 제출 계약을 유지한다. 코드 정의를 자연어의 별도 schema로 복제하지 않는다.

phase 007은 같은 경계의 fixture와 pair를 수리했고 manager가 지정 회귀를 검수했다. 제품 runtime은 불변이다. phase 008은 기존 _context 반환의 operational_evidence/recovery_materials를 문서와 실제 반환 검사로 연결한다. 일반 재개 restore_continuation과 동일한 필드명을 사용하더라도 다른 생산자다. 원자료의 정상/복원 오류/null/부재를 각 실제 객체에서 확인한다. 독립-운영의 설치 경로 설명도 현재 operator_bootstrap.main과 scheduled_operator.main 경계로 교정한다. 제품 계약 개정이나 새 task 사이 인터페이스가 없어 provides/uses는 빈 목록으로 유지하며 S 항목을 추가하지 않는다.

corpus 생성의 정본은 `.agents/diff/_rules.json`, `writing-skills/scripts/build_skill_mirrors.py`의 transform/build_target과 `writing-skills/references/멀티런타임_동기화.md`다. phase 004의 verbatim과005의 하위 manifest -text를 유지한다.007은 새 녹화 없이 기존 양쪽 전건 경로/바이트·명시 SHA·Git raw/clean 및 미러 생성 일치를 확인했다. 008도 corpus를 수정하지 않으며 허용된 문서·시험 사본만 공식 생성한다.

제품 공유 정의는 .claude/skills/do-math/scripts/이음새-정본.md 및 실제 타입·함수·스키마·포트 계약 시험을 원문으로 확인한다. report 형식은 서비스 protocol.md가 직접 규정한다. 후속 phase에서 외부 제공자/소비자를 분리 배정하려면 manager가 먼저 정본 파일·심볼, 입력/출력/오류/부수 효과, 경계 사례, 공유 검사와 실제 연결 책임을 해당 S 항목에 정한다. 같은 인터페이스는 같은 S ID를 유지하며 제품 내부 선택을 불필요한 seam으로 승격하지 않는다.

008의 운영/복구 및 설치 설명 지정 성과를 검수했으나 전건 문서 검사는 기존 CLI 함수 표기로4건 실패했다. 009는 해당 표기를 function_reference_issues의 현 함수 표기 계약에 맞추는 문서 수리이며 제품 경계·오류·입력 의미를 바꾸지 않는다. provides/uses는 계속 빈 목록이고 새 S 항목은 없다. 검수 근거는 run:phases/008/manager-evidence/review.md, 후속 책임은009 objective다.

009는 기존 함수 참조 표기만 교정해 정본110·미러89 전건 관련 회귀를 통과했고 manager가 원자료/현재 소스를 대조했다. 제품 경계 계약의 개정은 없다.010 host-smoke는 기존 windows_job/Jobs·실제 worker·console_python/PowerShell 출력 계약을 소비하며 테스트 공유화는 한 task 내부다.010 reading-limits는 고정된 운전 문서·CLI 입력 경로와 외부 호스트 읽기 계약을 독립 조사한다. 서로의 결과를 제공/소비하지 않아 S 항목을 새로 만들지 않는다. runtime 경계 변경이 필요하면 별도 finding과 후속 배정으로 돌린다.

010 host의 기존 runtime 소비 성과와 reading 조사를 검수했다.011은 현 _job_run의 필수 clock/environment를 기존 fixture에 전달하고 지정 음성 단언과 읽기 문구만 교정한다. 기존코드정본/실포트의입력·반환·오류의미는바꾸지않는다. 전건검사/미러/캐시소유를한task로모아제공자/소비자분리가없으며S항목·provides/uses는추가하지않는다. 읽기출력byte요구나운전host지정은이work의재량밖이다.

011의 기존 포트 fixture·정확 음성 단언·읽기 문구 수리를 검수했다.012는 현재 setup_lean.verify_environment/inspect_toolchain/verify_lean과 real_ports를 소비하는 Lean/Mathlib 최소 실연쇄다. 입력/반환/실패의 정본은 기존 함수·lean_evidence·trust_inventory이며 별도 형식 복제나 제품 계약 개정은 없다. 새 smoke/helper·녹화/재생과 미러를 한 task가 소유해 provides/uses는 빈 목록이고 S 항목은 추가하지 않는다. 설치/신뢰 상태 변경이나 runtime 수리가 필요하면 반례를 다음 배정으로 반환한다.

012 Lean/Mathlib의 기존 API 소비와 새 full 녹화/재생을 검수했다.013은 기존 PowerShellScheduler.run → operator_schedule.ps1, scheduled_operator.schedule/hold와 operator_bootstrap의 실제 OS 경계를 소비한다. 인자·Task-View 반환·실패의 정본은 이 코드와 ports/scheduler.py 및 현 계약 시험이며 별도 schema나 새 의미를 만들지 않는다. smoke/helper·corpus·미러를 한 task가 소유하므로 S 항목과 provides/uses는 추가하지 않는다. task 이름의 부재 확인·자기 소유 증거·정리는 외부 부수 효과의 범위이며 기존 예약/연구를 변경할 권한이 아니다. runtime/OS 권한 변경이 필요하면 후속 판단으로 반환한다.

013의 기존 예약 API 소비와 실제 OS 발화/정리·녹화 재생을 검수했다.014는 resolve_scholarly_server의 command/args, ModelRunner.run의 scholarly_server 및 worker의 실행별 scholarly-data 격리, native 도구 사건과 services/scholarly-mcp/server.py의 list_sources/ToolResult·registry.Source.summary를 소비한다. 시작 도구명과 완료 성공 응답은 구별한다. 새 시험·작은 지원 정의·corpus/reader·미러를 한 task가 소유하며 기존 제품 인터페이스를 개정하지 않으므로 S 항목·provides/uses는 추가하지 않는다. runtime·서버·공유 설정 변경이 필요하면 정확 반례와 후속 책임으로 반환한다.

014의 기존 scholarly API 소비·성공 완료/양 본문·격리와 녹화 재생을 검수했다.015는 run_tests.py의 main/_isolated/_worker/결과 집계와 tests/support/branch_gate.py의 측정/저장/병합 정의, do_math.layers.LAYERS를 기준으로 T4 보고를 연결한다. 시험 결과와 측정 완전성·분기 도달 보고는 구별하고 T3 gate·선택 색인·증분 저장소 의미를 유지한다. 같은 task가 생산자/소비자·회귀를 함께 수정하므로 별도 S 항목이나 provides/uses는 추가하지 않는다. 새 보고 형식의 정본은 구현의 실제 선언과 검증으로 두며 자연어의 중복 schema를 만들지 않는다.015 task가 지침과 생산/소비 시험을 같은 변경으로 맞춘다.

015의 T4 보고 정의는 tests/support/adapter_coverage.py의 AdapterMeasurement·validate_publication과 run_tests의 실제 소비가 정본이다. manager는 실제 worker 자료와 양쪽70회귀를 검수했고 T3 의미는 유지했다.016 t4-fixture-repair는 기존 trust_inventory/ModelRunner/ResearchRepository/formal/실포트 계약의 fixture 소비만 고친다. provenance-baseline은 Git 원바이트 입력을 자기 evidence에 준비하며 같은 phase의 다른 task와 제공/소비하지 않는다. SHARED_INPUT_BASELINE_SCRIPTS의 실제 소비는 기존 test_shared_input_provenance.py가 정의하고 후속 연결 task가 맡는다. 제품 인터페이스 개정이나 병렬 제공자/소비자 분리가 없어 S 항목과 provides/uses는 추가하지 않는다.

016은 현재 fixture 소비만 교정했고 Git과 과거 입력 원바이트를 검수했다.017은 기존 SHARED_INPUT_BASELINE_SCRIPTS 소비·TestCase/WORKER/SNAPSHOT·run_tests/AdapterMeasurement의 실제 연결을 검증한다. 두 task 사이 새 인터페이스를 구현하지 않고 한 task가 고정된 제공/소비를 함께 실행하므로 S 항목·provides/uses는 추가하지 않는다. 의미/형식/오류의 정본은 기존 코드와015 측정 정의이며 과거910파일을 새 제품 계약이나 호환 분기로 만들지 않는다.

017의 두 exact 비교와 실제 T4 측정·게시 연결을 검수했다.018은 현 Jobs 포트의 launch/resume/terminate/wait/inspect/close를 사용하는 시험 fixture cleanup만 교정한다. close의 핸들 닫기/kill-on-close와 root/빈Job 종료 관측을 구별하며 제품 API 의미를 개정하지 않는다. real/fake 공유 fixture와 관련 시험·전체 T4를 한 task가 소유하므로 새 S 항목·provides/uses는 없다. runtime/계약 개정 필요성은 정확 반례로 다음 manager에 반환한다.

018의 기존 Jobs API 소비와 최종 양쪽T4 연결을 검수했다.019는 기존 write_source_catalog·_preserve_outputs·_apply·_context·prepare_role_input의 생산/저장/복원을 실제 소비하는 문서 검사 수리다. 정본은 해당 함수·contracts/record schema이며 별도 제품 형식을 만들지 않는다. 같은task가 doc_code와 직접소비/helper·미러를 소유하고 독립 제공자/소비자로 나누지 않으므로 S항목·provides/uses는 추가하지 않는다. runtime/입출력 의미 개정이 필요하면 반례로 후속 판단에 반환한다.

019의 P02 실제 생산/저장/복원 문서 결속을 검수했다.020은 기존 _context·record_map·prepare_role_input·install_tools의 실행 안내와 지급 도구 경계를 소비한다. 명령/설치파일/오류/조건부 부재는 현 코드가 정본이고 문서 검사용 별도 schema를 제품 계약으로 만들지 않는다. 같은task가 helper와 직접 소비·미러를 소유하며 제품 인터페이스를 개정하지 않으므로 S항목·provides/uses는 추가하지 않는다. record_map 기본 반환, preview 지급과 실제 검증 결과의 차이, scholarly 설정과 실호출의 차이를 유지한다.

020의 P03 실제 설치/최종 입력 결속을 검수했다.021은 기존 review_cycle.context_for/accept_result·ReviewEngineMixin의 검토 준비/봉인/고정 조사/원자료 물질화 경계를 소비한다. stage별 가시성·정확 ref·proposal/request digest·고정 snapshot/복원 오류는 기존 코드/공유 계약이 정본이며 새 의미를 만들지 않는다. P04/P05 네 owner와 helper·직접 소비·미러를 한 task가 소유하므로 S항목·provides/uses는 추가하지 않는다. runtime나 권한 계약 개정은 범위 밖 반례로 반환한다.
