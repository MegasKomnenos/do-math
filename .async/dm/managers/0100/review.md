# manager 0100 판단

2026-10-17, 이번 inbox의 g6-run 사용자 중단 사건만 처리한다. g6-run은 cancelled·미수용으로 유지한다. 완료 report.json이 없으며 실행 준비 중 선택 색인을 교체한 한 파일 외에 정본/미러 변경은 없다. 수용할 제품 수리나 완료 결과가 아니므로 workspaces.py integrate를 호출하지 않고 accepted를 늘리지 않는다. 실행 중 mutation-parallel의 배정은 그대로 유지하며 전체 G6는 그 개선을 검수·통합·수용한 뒤 새 ID로 배정한다.

## 직접 확인한 근거

protocol.md의 manager 절차, 공용 context/plan/seams의 현재 상태·완료 기준·후속 경계, inbox와 queue/state, 사용자 mutation-parallel·지정5모듈T3·저장범위 지시, mutation-parallel objective와 고정 task.json을 읽었다. inbox.running은 비어 있었지만 확인 시 state에서 mutation-parallel은 running이었다. 해당 task의 queue 정의와 고정 task.json이 같음을 확인했으며 정의·objective·writes·선행을 수정하지 않았다. 작업자의 진행 중 결과는 이번 수용 대상으로 삼지 않았다.

g6-run의 baseline과 workspace의 정본/미러 쓰기 범위를 SHA-256으로 대조했다. 실제 차이는 `.claude/skills/do-math/scripts/tests/.selection-index.json` 하나로, 시작판4f2f8299에서 원측정판3d30a04e로 바뀌었다. 이는 기존 population/실행의 준비 입력이고 독립된 제품 변경이 아니다. 원 workspace·baseline·objective·session.log·evidence는 유지했다. 취소 task를 수용해 정리 대상으로 만드는 방식은 사용하지 않았다.

운영 중단 원자료 `runtime/g6-parallel-interruption-2026-10-16.json`과 g6-run의 마지막 session.log, `evidence/b01-execution.json`을 읽었다. task returncode와 b01 exit_code는 null이고 최종 batch 보고는 없다. 실행 래퍼가 끝의 보존 단계를 마치지 못해 `tasks/g6-run/evidence/runs/b01`도 없다. 외부 원출력 `C:/g6run-g6-exec/b01`의40파일·1,919,262 bytes를 이 manager의 `evidence/g6-run-b01/`에 그대로 복사하고 파일별 SHA 일치를 확인했다. 외부 원본은 그대로 두었다. `verification-review.json:raw_output_manifest`가 목록과 해시를 제공한다.

`mutant-0004/attempt-0001/attempt.json`은 exit4294967295와 result 파일부재를 기록한다. 사용자 중단이며 timeout·killed·정상완료가 아니다. `mutant-0005/attempt-0000/result.json`은 존재하나 attempt.json과 관측 종료값은 없으므로 정상 종료를 추정하지 않는다. 나머지 개별 attempt/result도 보존했지만 이 manager는 killed 집계나 전체 결과를 새로 구성하지 않았다. 후속 실행자는 source/index/selection/정상 기준/관측 종료가 갖춰진 개별 결과만 실제 재사용 가능성을 판단한다.

## 정상 기준에서 드러난 작은 보완

`evidence/g6-run-b01/unmutated-0001/`의 spec/result/attempt/output에서 정상 시험 `unit.test_storage_report_projections.ReportProjections.test_human_report_preserves_loaded_initialization_blocker_and_machine_finding`이 실패했음을 확인했다. child exit0이지만 row는 failed이며 정상 통과가 아니다. 원 traceback은 `references/과제-착수조건.md`의 `submission.payload_issues` 토큰을 미소유 필드로 지적한다.

공용판의 해당 문서89행, 시험128~173행, `tests/support/doc_code.py:unowned_field_references`·`function_reference_issues`, `do_math/submission.py:payload_issues`를 읽었다. 함수는 존재하고 문서가 기존 callable 표기 대신 dotted field 표기를 사용한다. 관련 네 파일의 공용판과 중단판 SHA가 같음을 확인했다. 후속 G6 task에서 기존 함수 참조 규칙에 맞춘 문서·미러 보완과 이 정확한 정상 시험의 필요한 확인을 묶는다. 단언이나 필드 검사 완화, runtime 우회, 저장 가족별 재입증은 필요하지 않다. 작은 표기 수리만을 위한 별도 task를 만들지 않는다.

manager의 제품시험·변이·성능실험 재실행은0회다. 기존 raw 실패·현재 코드·판본 비교로 후속 범위를 정하기에 충분하다. 변화 없는 결과의 반복 실행이나 전체 감사는 하지 않았다. 소스 비교·원출력 보존·큐 정의 확인 절차는 prepare_update.py, 판단 자료는 verification-review.json, 다음 G6가 소비할 책임은 handoff-delta.json에 남겼다.

## 후속과 게시

mutation-parallel은 개선 수단을 직접 선택하여 구현·작은 실제 검증·설명·미러까지 마친다. 총 mutant/normal child3 이하, worker gpt-6.1-sol/high, max_workers10을 유지한다. 실제 개선 API·CLI·중단/실패/결과 통합 방식은 아직 수용되지 않았으므로 새 G6 objective를 추측해 게시하지 않는다. 수용 뒤 새 ID를 만들고 그 실제 사용법을 적용한다. 구 g6-run의 child1 규칙을 자동 복사하지 않는다. 전체 G6 책임은 plan에 남겼으며 실행 개선만으로 전체 목표가 끝난 것으로 처리하지 않는다.

후속 G6는 수용된 g6-inputs/g5-remainder와 g6-run의 population·source snapshot·색인/명시 입력 준비를 실제 판본에 맞춰 재사용한다. 원123모듈/1677함수·20묶음은 준비판의 수이지 quota가 아니다. 별도 전수준비나 전체T3·전체일반 재실행을 이번에 배정하지 않는다. G5 환경6arc/10행과 부분측정/index 한계, G1~G3 최종 연결, 실제 G6, 남은 G7/G8 및 L01/공급자 조건은 계속 미해결이다.

저장범위/A22 지시는 기존 공통 보장의 재사용과 구체적인 문서 실패만 좁게 보완하는 데 적용했다. 가족별quota·반복실호출·새 장기감사를 추가하지 않았다. 지정5모듈의 관련추가T3만 허용하는 최신 지시와 원전체/부분 추가판본의 구분도 유지했다. graphify 갱신·외부설치 정리·기존 연구 변경은 하지 않았다.

공용 context/plan/seams에서 현재 상태를0100으로 갱신하고0099의 즉시실행 안내를 당시 이력으로 표시했다. queue는 기존121정의·accepted115·취소5·미해결1·active를 유지한다. 새 task·새 수용·통합은0이다. 모든 task 정의와 진행 중 objective는 불변이다. 공용 문서를 먼저 완성한 뒤 같은 내용의 queue.pending.json을 공식 검사하고, 검사한 파일을 queue.json으로 원자 교체한다. 검사 결과는 queue-check.json, 게시 기록은 publication.json에 남긴다.
