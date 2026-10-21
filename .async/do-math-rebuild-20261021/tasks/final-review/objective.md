# 새 do-math의 최종 독립 개발 검토

## 맡은 결과

사용자가 승인한 새 do-math의 목적·확정 조건·완료 기준을 수용된 전체 제품과 실제 사용 근거에 대조해, 개발을 완료할 수 있는지 판단한다. 제품은 수정하지 않는다. 파일 존재나 형식 검사 통과만으로 판단하지 않고, 사용자가 SKILL.md로 연구를 시작하고 세션들이 공개 지식을 축적·검토해 목표를 달성할 수 있는지를 본다.

먼저 inputs/context.md, inputs/plan.md, inputs/seams.md와 task.json을 읽는다. 확정 요구 원문은 `C:/math/.async/do-math-rebuild-20261021/user-messages.md`다. 제품은 자기 workspace의 `.claude/skills/do-math/`이며, mixed-completion의 Windows 상태 교체 수정까지 통합된 사본이다. 이전 do-math 코드나 Git 이력을 설계 기준으로 사용하지 않는다. 그래프 갱신과 `.agents` 사본 작성은 이 배정 밖이다.

## 읽기 경로와 판단 범위

1. 사용자 원문과 context 2~6절에서 핵심 요구를 찾고, SKILL.md → RUNTIME.md/CLI.md/protocol.md → 실제 runner.py/cli_adapter.py/check.py로 따라간다. 요구에서 제품으로 가며 중요한 누락을 찾고, 제품 설명에서 실제 코드·근거로 돌아가 정확성도 판단한다. 사용자 대화에서 목표·설정 준비, 자체 Git 인스턴스 init, 독립 start와 새 PID·로그 확인, 결과 위치 반환, 조회·STOP·입력·개별 CLI 종료·재기동까지 후속 독자가 수행할 수 있는지 읽는다.
2. 실제 세션의 input.json과 프롬프트에서 common/protocol/goal, 범주 문서, task의 작업특정요소로 이어지는 경로를 읽는다. 계획의 미완료 요청·실패 원 과제 읽기, 부분 결과·실패·질문 환류, 전체 기록 대체와 상충 검토 판단, 연구 해설과 실제 확인 범위, 공개 자료만으로 하는 독립 검토 및 세 가지 판단의 분리가 충분히 전달되는지 확인한다. 작성자만 아는 맥락이나 기록 링크만 있고 중요한 본문이 빠진 부분은 결함으로 판단한다.
3. context 4절의 정해진 흐름과 불변식 열 가지를 관련 코드에 대조한다. 공식 검사는 구조·참조 실재이며 Lean·수학적 판단으로 확장되지 않아야 한다. CLI 로그는 한도 신호만 소비하고 정상 산출은 종료 코드와 관계없이 공식 재검사로 판단해야 한다. 한도/STOP/외부 입력/완료의 별도 파견 조건, 끝난 세션의 처리, 전체 동시 상한·단일 실행기, 새 파일과 Git 반영을 확인한다. 환경 고정·봉인·감시 체계나 실행 시간 상한을 새로 요구하지 않는다.
4. 실제 완료 근거는 RECORDS의 `tasks/mixed-completion/evidence.md`에서 시작한다. 최종 인스턴스는 `C:/math/.async/do-math-rebuild-20261021/tasks/mixed-completion/evidence/instance-add-zero-fixed-20261021/`다. goal.md와 settings.json을 읽고 다음 공개 기록의 본문·근거를 대조한다.
   - 연구 `knowledge/k3812dd40113a4425b0b901de60dfd0bc/`: output.json, exposition.md, Proof.lean, lean-verification.json. 0 포함·전칭 정리·해설 논증·실제 판본/컴파일 범위를 확인한다.
   - 독립 연구 검토 `knowledge/kf5af23be4e1b4e0588de16f547142351/`: output.json과 review-notes.md. target 연결, 공개 원문 재컴파일, 주장·Lean·해설 판단과 한계를 읽는다.
   - 다음 계획 `knowledge/k886da92b6d4f49a8a83840b838feff00/output.json`과 목표 검토 `knowledge/kc7325f0829e84ab5ab14fdfd5938ca33/`: output.json, goal-review-notes.md, lean-recheck.json 및 필요한 보조 Lean. achieved가 실제 사용자 목표를 충족하는지, OfNat 표기 생략·한 판본 확인 한계의 판단이 합리적인지 본다.
   - evidence/final-status.json, session-evidence.json, git-evidence.txt에서 실제 Codex 3세션·Claude 2세션, 각 공식 검사 호출과 성공, 공개 반영, complete·기존 세션 종료·실행기 종료를 확인한다. 필요할 때만 원 sessions의 launch/input/process/exit/로그 발췌와 실제 Git을 확인한다. 개발 실행 흐름 확인에 로그를 사용할 수 있으나 공개 수학 검토를 작성자 로그로 대신하지 않는다. 최종 인스턴스와 실패한 첫 인스턴스를 혼동하지 않는다.
5. mixed-completion의 제품 변경은 runner.py:write_json의 Windows 오류 5/32/33에 대한 최대 1초 교체 재시도, RUNTIME 설명, tests/test_state_write.py다. base/workspace diff와 보고를 읽어 사용 결함에 맞는 작은 수정인지, 지속 거부·다른 오류와 기존 완전 상태의 의미가 보존되는지 확인한다. 당시 독자를 특정하지 못했다는 사실과 열린 파일 재현 근거를 구분한다. 기존 runner·어댑터 시험의 근거는 tasks/runner/report.json, CLI 출력 의미의 근거는 tasks/cli-discovery/cli-evidence.md다.

## 최소 확인과 보고

이미 수용한 시험이나 실제 혼합 연구를 반복 실행하지 않는다. 정적 읽기와 공개 실행 근거로 충분하면 거기서 끝낸다. 구체적인 미확인 동작이 완료 판단을 막을 때만 작은 입력·호출로 확인하고, 산출은 자기 task 기록에 둔다. 새 모델 연구·Lean 재컴파일·광범위 시험을 관례적으로 추가하지 않는다. Linux·재부팅·실제 계정 한도·장기 어려운 연구·다른 Lean 판본은 이번 완료 기준이 아니며 미확인 한계로 구분한다.

자기 task 폴더에 review.md와 report.json을 작성한다. review.md에는 요구별 결론과 실제 근거 파일·심볼·내용, 읽은 소비자 경로, 직접 수행한 확인과 한계, 완료를 막는 결함 및 선택적인 보완을 구분해 적는다. 결함은 정확한 위치·발생 조건·사용자 결과에 미치는 영향·필요한 수정 범위를 적어 manager가 후속 task를 배정할 수 있게 한다. 프로세스나 파일이 존재한다는 사실을 완료 근거로 대신하지 않는다. report의 status는 검토 작업 수행 상태이며 제품 합격 여부는 summary/findings에 명시한다. 제품 changes는 []다.

제출 전 `python C:/math/services/async-development/check.py report C:/math/.async/do-math-rebuild-20261021 final-review`를 수행한다. 최종 완료 게시와 추가 수정 배정은 manager가 담당한다.
