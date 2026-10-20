# 0075: 상태·수명 결과 수용과 직접 실행/I/O 경계 후속

inbox의 완료 사건은 g5-state(exit0) 하나다. 정본 제품3·시험/helper9·설명1과 대응 미러13쌍, 총26파일을 검토했다. check.py report PASS 뒤 workspaces.py integrate로 충돌 없이 통합했다. 제품 수정은 task의 결과이며 manager 제품시험은 0회다. 한정 배정의 complete를 수용하되 전체 G5 성공으로 해석하지 않는다.

## 코드·현재 계약 판단

dispatch_engine._dispatchable의 같은 과제 연구 재검사는 앞선 planning.task_ready의 occupied 및 같은 action ID 검사와 중복이다. task_ready는 다른 action의 미종료 실행이 과제를 점유하면 not_ready를 반환한다. lifecycle_engine._limited_recovery_control은 허용 역할/정확 프로필을 먼저 확인하고 _recovery_action_basis가 role/profile_ref를 포함해 승인 사건에 결속한다. _check_limited_recovery는 그 hash·원승인·pause·유효기간·현재 profile identity·권한/능력을 보존하면서 같은 역할 검사를 줄였다. 공개 config 객체형 검사는 입력 경계에 유지한다.

기계 실행의 _register_execution→SessionSlots.acquire는 성공한 입장의 launch_ticket을 공급한다. 입장 실패는 None으로 돌아오고 해당 정산에 도달하지 않는다. _release_machine_execution은 이 표를 직접 mark_returned하며, 종료 장벽은 release_or_hold가 계속 소유한다. 새 시험은 실제 등록된 owner_thread의 stopping→ended·한 번의 종료·finished 표와 저장 결과를 확인한다. 실제 OS 자식 종료 성공을 이 시험으로 주장하지 않는다.

state_checks.inspect_state는 기존부터 적재 검사를 통과한 상태를 입력 계약으로 가진다. core_engine.check가 store.load 뒤 이를 호출하는 것을 확인했다. 바깥 중복 malformed-record 포착을 제거했지만 _inspect_area.run의 실제 불변식/증거 오류 보고와 unknown area·누락 증거의 incomplete는 유지한다. 비artifact 학술 참조는 적재 시 해소되고 academic.evidence_record가 기록을 먼저 찾으므로 내부 reader 래퍼를 줄였다. 여러 활성 신뢰 환경·종료 과제의 live worker·이관 의무 누락·완료 상태의 학술 요구 미충족은 여전히 inspector가 보고하며 운영-점검.md에 이 책임을 설명했다.

시험 변경은 현재 생산자/준비물을 사용해 staged 전이·review input·위임·impact 대기 결속의 정확 반려와 입력 보존, 기동 mismatch 뒤 closed 보존, readiness 사건 재사용과 재고 시각, 실제 pause 뒤 trust continuation, 시계 포트 오류 전후 초기 retry 정산을 확인한다. repository는 기존 1024-link/64MiB cache 한도와 immutable artifact namespace 검사를 직접 확인하며 대량의 무관한 저장 게시를 만들지 않았다. 종료 시험은 KeyboardInterrupt의 정확한 calculation interrupted 사유를 고정하고 원결과/정산 단언을 유지했다. 새 사용자 동작 결함을 수리했다는 주장은 하지 않는다.

## 확인과 한계

verify.py와 verification-review.json은 원 focused1~3의 report/coverage·외부 원파일 SHA, 선택/고유실제행·실행중변경·원좌표·소유제품 SHA, source3의 소유Python23개 AST(함수 docstring 제외), 정본/미러13쌍을 대조한다. 원33arc/29행은 도달26arc/21행·제거7arc/8행, 남김/새제외0이다. 이는 과거좌표 처분이며 새 통합판 전체 gap 수가 아니다.

focused1은18행=12passed/4failed/2error, focused2는9행=8passed/1error, focused3은3행=3passed다. fixture 오류/실행중변경0·complete=true이고 마지막만successful=true다. 모두 부분gate/최상위passed/closing_eligible=false·관측exit1이다. 공식/외부시간은328.0/329.953초,257.7/259.297초,63.1/64.078초다. 소프트 초과·앞선 실패는 원자료에 유지한다.

첫 실행의 서로 다른 실패6건은 이후 passing행으로 연결됐다. 시작표가 없다고 가정한 시험은 실제 등록된 표를 확인하는 이름/내용으로 교정됐으므로 단순 동일 ID 재통과와 구별한다. 나머지도 현행 schema·생산자·호출시점의 구성 오류였다. source3/제출23Python의 AST 일치는 마지막 문구 보충을 설명하며 모든 앞선 시험 본문의 byte동일 증명은 아니다. 변경시험 원문을 정적으로 검토했고 서로 다른 부분판을 하나의 최종 전체 성공으로 합산하지 않는다. 최종판 G4/G5는 남는다.

## 후속과 저장범위 지시 적용

새 g5-entry-io는 g5-worker의 script/import/frozen13arc/25행과 g5-io의 환경6arc/10행을 묶는다. 실제 선행은 두 수용 task뿐이다. 직접 Python Job/MCP/독립 bootstrap·probe 입구와 frozen manifest 선택, 파일 reparse omission·비Windows I/O를 현재 지원 계약 및 실제 실행 경계로 판단한다. 기존 경계시험과 필요한 최소 로컬 T4 실행을 허용한다. T4 자식 결과를 T3 coverage/gate/index에 수동 합치지 않고, 원설계5.5의 행별 계약 근거가 있는 제외와 환경 미확인을 구분한다. 단지 현재 호스트에서 실행할 수 없다는 이유로 제외하지 않는다.

파일 symlink WinError1314는 기존 사실이며 같은 probe를 반복할 새 이유는 없다. 적합한 기존 환경이 있으면 최소 확인하고, 없으면 정확한 조건을 남긴다. 플랫폼 지원의 명시 근거 없이 POSIX 경로를 지우거나 Windows 전용으로 새로 선언하지 않는다. 유료 호출·실예약·설치·권한/호스트 정책 변경·새 환경 구축은 새 배정에 포함하지 않는다. 작은 남김을 모든 G7 또는 새 측정 framework로 확대하지 않는다.

사용자 storage-scope-direction-2026-10-15와 원설계3.3/A22를 대조했다. 이번 수용은 구체 좌표의 계약 판단과 직접 단언이며 공통codec/저장검증·기존 업무 성질을 재사용했다. 새 후속에서도 전가족·전필드·새reader·옛head quota·장기감사를 추가하지 않는다. 원래 G1~G8과 L01·실경계의 미완료는 유지한다.

inbox.running의 g5-trust·g5-core-rest 정의와 objective는 그대로 유지한다. 기존91개 정의·취소2건을 보존하며 g5-state를 추가해 accepted87개, 새 task 포함92개 정의·active다. 새 쓰기 범위와 두 running의 교집합0을 assignment-scope.json으로 확인한다. trust1/core-rest1/entry-io1의 시험슬롯3, max_workers10·gpt-6.1-sol/high를 유지한다. 이후 도착한 완료 사건은 다음 manager가 처리한다.

공용 context/plan/seams와 새 objective를 먼저 완성하고 queue.pending.json을 check.py queue로 확인한 뒤 queue.json에 원자 교체한다. 게시 후 이번 manager의 공용 변경은 끝낸다.
