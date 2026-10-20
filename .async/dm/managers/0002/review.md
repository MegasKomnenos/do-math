# r02 수용과 후속 배정

0002 inbox의 완료 사건은 r02 하나이며 r07·r18은 시작 당시 실행 중이었다. 이 세 task의 기존 배정은 변경하지 않았다. 이후 도착하는 사건은 다음 manager가 처리한다.

r02는 맡은 요청 가족의 읽기 판정을 완료했다. `check.py report`는 PASS이며 `workspaces.py integrate C:/math C:/math/.async/dm r02`는 `{"task":"r02","files":[]}`를 기록했다. 따라서 변경 파일의 실제 목록도 비어 있다. 이번 수용은 조사 결과의 수용이며 제품 전체 합격이 아니다.

## 확인한 사실과 판단

현재 `tests/contracts/pairs.py:_worker_request_samples`와 `test_pairs.py`의 실제 단언을 읽었다. pair는 `build_profiles`의 첫 값을 골라 worker_request_fields를 직접 부른다. `execution_profiles.py:build_profiles`는 sorted(PROFILE_ROLES)를 순회하고 machine 역할에는 ai를 만들지 않는다. 첫 external_action 프로필에는 ai가 없다. `model_call.py:runner_assignment`는 ticket을 검증한 뒤 ai 모델/effort와 입력 seal을 확인하므로 그 프로필은 같은 AI runner 배정에 맞지 않는다. 이것은 코드에서 확인한 fixture/연결 반례이며 런타임 실패를 실행한 결과가 아니다.

`ModelRunner.run`의 배정 검사·요청 저장과 `codex_adapter.py:LocalCLIAdapter.start`의 첫 load_request·snapshot 저장, `support/provider_runs.py`의 실제 worker 실행을 확인했다. 기존 ProviderJobs/ScriptedCLI가 제품 내부 경로를 유지하므로 새 runner fake 없이 공백을 고칠 수 있다. `worker_request.py`의 필수·선택 상수와 validate_execution_binding은 reference 형식 검사를 제공하며 profile registry의 AI 의미를 판정하지 않는다. worker 경계를 확대할 이유는 없다.

r02의 fields 35행·sample_branch_rows 40행은 정적 대응표로 수용한다. 기존 필수+선택 역방향과 Codex only=True 무효과 회귀는 유지한다. 중첩 값·실제 저장·worker 수신의 전 조합 성공으로 확대하지 않는다. `source-review.json`은 task가 참조한 현재33파일의 SHA를 공용 소스와 대조하고, 유지하는007 원보고의 실제 관련 row·command exit·해시를 확인한 결과다. B49 Temp raw의 부재는 그대로 남기며 기록된 counts를 새 성공으로 합산하지 않는다. 모든 과거 의존 판본과 설치·실호출을 재인증하지 않는다.

## F1을 처리할 한 작업

`r02-fix`는 r02만 선행으로 하는 시험 수리다. 유효 AI 프로필과 ticket/seal/host start publication으로 기존40입력을 실제 runner 저장·adapter·worker에 연결하고 scholarly args의0/1/여럿을 함께 보강한다. 같은 pairs/test_pairs 및 필요한 provider_runs·pinned_runner, 미러와 관련 검증을 한 담당자에게 묶었다. runtime 결함은 확인되지 않았으므로 runtime 쓰기 권한은 넣지 않는다. 원격 모델 호출은 필요하지 않다.

보고의 비교 제안은 한 점을 구체화했다. 실제 profile의 ai lock 값이 달라지면 sealed profile_ref도 바뀐다. 각 요청의 ref를 자기 profile에 정확히 대조하고 lock의 전송 효과를 따로 확인해야 한다. 다른 프로필 ref를 같게 강제하거나 정규화로 identity 검사를 없애는 배정으로 해석하지 않는다. 이는 현재 profile 구성과 seal 호출에서 확인한 구현 조건이다.

r07·r18은 고정 사본에서 읽기만 하므로 r02-fix와 쓰기 충돌·실제 선행 관계가 없다. 기다리는 phase 장벽을 만들지 않고 후속을 게시한다. 새 독립 기능이나 추가 감사는 이 결과로 필요성이 확인되지 않았다. 작업자는 jobs1의 기존 계약/직접 소비 시험으로 변경을 확인하고 미러 일치는 생성기 검사로 확인한다. 전체 관문 반복은 배정하지 않는다.

## 남은 목표와 게시

R02/1-A의 요청 가족은 읽기 완료·F1 수리 대기다. K-78 요청 slice 및 PR18의 기존 성질을 유지하며 다른 요청/저장 가족·K/P2는 종결하지 않는다. F2와 G4~G8, 029 판본 한계, L01 및 Windows1314 symlink 실제 반려 미검사는 계속 열린 상태다.

context·plan·seams와 새 objective를 먼저 작성한다. 게시할 queue는 managers/0002/queue.pending.json에 준비하고 `check.py queue`로 검사한 뒤 동일 파일을 queue.json으로 원자 교체한다. accepted에는 r02만 추가하며 status는 active다. 제품 변경이 없으므로 이번 manager의 제품 commit은 없다. queue 게시 뒤 공용 변경은 종료한다.
