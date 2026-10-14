# P03 실제 설치와 최종 입력의 문서 결속

시작 skills/diff 2,675파일은 019 manager source-inspected.json과 전건 SHA256이 같다(start-comparison.json). 시작 Git HEAD/status/diff/index는 따로 보존했으며 기존 변경을 이번 task에 귀속하지 않는다. input-audit.json은 배정 원자료의 판본을 보존한다. P03 역사 행 번호는 현재 문서의 제목·필드와 실제 _context, prepare_role_input, record_map, install_tools에서 확인했다. 13-C의 명령/인자/필드/정책 존재 의무만 이번 packet에 적용하며 읽기 출력 한도 L01을 인증하지 않는다.

| 소유자 | 실제 결과 및 담당 검사 | 성질과 한계 |
|---|---|---|
| execution_window | PreparedInputTests.test_installed_tools_match_the_final_role_input_and_reject_damage의 실제 _context → prepare_role_input | self_check_directory 및 path/finish/stop/feedback 경로와 최종 지급 일치. _context는 안내를 만들며 동적 알림 파일의 발생을 증명하지 않는다. 기존 RoleScopeContextTests의 실제 인용·scratch 배제 검사는 그대로 유지한다. |
| scholarly | 같은 method의 실제 build_profiles → 고정 profile_ref → _context → prepare_role_input | 비구성/구성 표본, enabled/configured와 runner_tools의 정확 설정·scholarly-data. fixture-scholarly는 명시 설정 표본이며 서버를 시작하지 않는다. 기존 PreparedInputTests의 실제 runner/worker request와 override 반려·추가 worker 0 단언을 유지한다. configured는 호출 성공이 아니다. |
| formal_verifier | 같은 method의 설치 전 _context와 설치 후 최종 입력 | 중앙 mechanism과 command/environment/toolchain/allowed_axioms가 실제 생산 결과와 같다. 설치가 preview만 추가한다. goal_audit의 참조 객체는 원래 source_ref 파일의 SHA/bytes와 내용까지 읽으며 파일 손상 반려도 확인한다. |
| preview | 같은 method, LeanPreviewTests 및 FormalInputManifestTests의 실제 설치 결과 | formal_verifier.preview를 따로 순회한다. 두 개의 생산 결과를 합치지 않는다. 정확 check_lean.py 명령·wrapper와 authoritative=false, 같은 archive/source 판본. 기존 FormalInputManifestTests의 실제 project 입력 변경/Lean 반려·worker 미기동을 유지한다. preview 반환 JSON은 이 객체와 다른 경계다. |
| record_map.read_tool | 같은 method의 실제 prepare_role_input → install_tools | 정확 read_input.py wrapper/command/log_path, record_map 기본 실제 반환·record_index 가족별 수·snapshot·readable/supplied_only 권한 범위. 기존 기본 record_map 검사 및 실제 읽기 성질을 유지한다. |
| submission_contract | 같은 method의 실제 install_tools 및 schema/context 파일 | 정확 check_submission.py·workspace·schema/ext 경로와 실제 공유 schema, limits.checkpoint_bytes/max_artifact_bytes, archive의 tool_sha256와 모든 출하 member 원바이트. 다른 파일과 그 파일의 일관된 해시를 함께 차용해도 member 모집단/바이트 검사에서 반려한다. |

일반 scoped_field_issues는 이번 여섯 owner를 실제 입력 없이 통과시키지 않는다. 기존 일반 문서 순회는 정확 여섯 owner만 defer한다. structure의 로컬 담당 검사는 PreparedInputTests의 해당 method 안에 여섯 실제 assert_tool_documents 호출이 있는지 확인한다. owner 오기·담당 누락·실제 호출 누락 및 다른 owner 동시 건너뜀은 실패한다. 이 AST 사용은 검사 담당 확인이며 반환값 추론이 아니다. 다른 P01/P02·B130~B134의 실제 결과와 음성 검사는 유지한다. 전역 담당 등록부나 범용 소스 추론기를 추가하지 않았다.

수리 전 red는 기존 AST 결속이 여섯 owner를 실제 입력 없이 모두 통과시키는 공백을 같은 여섯 필드의 ValueError not raised로 확인했다. green은 같은 method의 기본 반려와 개별 defer, 실제 설치 정상 표본 및 반환 후 사본 교란을 연결한다. self_check_directory, 각 지급 command, checkpoint_bytes, max_artifact_bytes 누락을 문서 필드 검사에서 반려한다. command의 다른 도구 차용, wrapper 파일 차용, archive 해시 변조와 잘못된 archive/해시 쌍, 정확 catalog 파일의 누락·손상을 추가로 반려한다. 생산·설치·포장을 대역으로 가리지 않으며 반례는 생산 뒤 사본/자기 임시 파일을 손상시킨다.

미설치 prepare_role_input은 preview/submission_contract/tool 파일이 없는 별도 조건이다. 이를 정상 installed 표본으로 사용하면 반려한다. windowless 시험은 기존 fake Python 파일과 sys.executable 외부 환경 선택만 사용하며 실제 install_tools를 실행한다. 같은 설치의 python.exe 선택, sibling 부재 FileNotFoundError.filename 및 context/디렉터리 무부수효과를 유지했다. 이 시험의 빈 실행 파일은 명령 실행 성공 증거가 아니다.

010 host review의 실제 pythonw → console_python → PowerShell → 지급 read_input.py → fixed snapshot/reads log와 정상·권한반려 JSON/exit 성질은 이번 runtime/도구 바이트 불변 조건에서만 재사용한다. 012 Lean review의 실제 정상/타입오류/full 의존 증거와 기존 preview 경계는 별도로 유지한다. 새 모델·Lean·학술·예약 실호출은 수행하지 않았다. 현재 preview 명령 지급을 과거 full 검증의 성공으로 대체하지 않는다.

B110~B114의 도입 actual diff와 현재 소비를 P03 slice에 한정해 검토했다. B110의 _context 세 owner와 install_tools preview/read_tool/submission_contract AST 조립은 실제 반환·설치 검사로 교체한다. record_map 기본 실제 반환, 저장 execution과 실행 입력의 구별, B111/B112의 명시 owner/별칭/함수·진단 표기를 유지한다. B113의 다른 actual-return/continuation과 B114의 P02/REVIEW 소비는 범위를 늘리지 않는다. 존재하는 원보고 7개의 SHA는 history-verification.json에서 전건 대조했으며 역사 counts를 현재 성공에 합산하지 않는다. PR24 전체 종결이 아니다.

초기 focus의 AttributeError는 extension_schema 정본을 contracts로 잘못 지정한 자기 helper 오류였다. 실제 submission.extension_schema로 교정한 corrected 4passed를 보존한다. augmented의 실패는 maintenance의 formal_verifier가 map일 것이라는 시험 가정이 실제 INLINE_SCOPES와 달랐기 때문이다. 현재 goal_audit의 실제 map에 참조 검사를 연결했고 초기 실패를 소급 성공으로 바꾸지 않았다.

문서 수정은 공통-실행의 preview가 formal_verifier.preview의 설치 후 객체이고 부재 시 지급 명령을 가정하지 않는다는 두 문장이다. 기한/정지/정상 종료 요청, authoritative=false 및 중앙 재검사, scholarly 설정과 실제 노출/성공 차이, console Python 조건은 보존했다. 런타임 API·입출력 의미·원 schema를 바꾸지 않았다. 향후 일반 역할 prompt에는 이 문장이 반영되므로 역사 고정 실호출 prompt의 성공을 새 문서 읽기/준수로 확대하지 않는다.

최종 실행/선택/고유 row/실제 exit 및 소스 불변은 verification.json, c/m 공식 report와 process/before/after에서 확인한다. 보존 모집단은 preservation.json이다. 기존 Windows symlink 권한 조건의 skip은 통과나 실제 탈출 반려 증거로 세지 않는다. P03 필수 성질에는 skip이 없으며 G4 조건부 환경 판단은 후속 책임이다. P04~P11·REVIEW/TRUST·나머지 P/N·L01, G4 전체 일반·G5 fresh T3·G6 전수 변이·G8 최종 review는 남는다.

최종 검산 결과는 정본/미러 동일200선택·각199passed/1skipped·exit0이며 각각255.0/253.8초다. 각875Python과 실행 tree의 비캐시 전후 바이트가 같다. 변경26경로는 정본12·미러12·비용캐시2로 전부writes안이다. 공식생성13갱신·마지막캐시1동기화·--check1336파일 일치·skill-only 및 보존검사exit0을 확인했다. Runtime139입력, host8원자료, 도구5SHA, baseline910바이트/Gitblob, corpus144경로/Gitraw-clean/150명시SHA, runtime/T4고정258경로가 보존됐다. parent TEMP C:\t\p020에서 실제git rev-parse는exit128이며 상위저장소를 찾지 않는다.
