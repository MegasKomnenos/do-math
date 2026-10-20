# manager 0017: 비용 결과 수용과 null 조사 부분 수용

inbox의 완료 사건 r23-r24·r06을 검수했다. 시작 당시 r14-fix·r21-r22는 실행 중이고, 기존 r12-r13-fix는 실제 core 선행 대기다. 기존 배정과 진행 중 사본은 유지한다. 세션 중 새 완료 사건은 다음 manager에게 남긴다.

## 수용과 직접 근거

inspect_results.py와 source-review.json은 base/baseline/workspace의 실제 변경, 공용 시작판, 미러쌍, AST, 실행 원보고와 하위 row, Python SHA를 대조한다. r23-r24는 정본 2·미러 2, r06은 정본 1·미러 1이며 두 check.py report는 PASS다. workspaces.py integrate로 각 4·2파일을 충돌 없이 반영했고 integration.json과 공용 결과 bytes를 확인했다. runtime·공통 helper는 불변이고 비용 캐시는 각 base와 같다. manager의 제품 시험 재실행은 0이다.

r23-r24는 query 페이지의 전체 path/size/SHA, readiness의 반환 순간 snapshot·전체 instance/runtime 보존·중첩 basis/profile_ids 변경 뒤 저장값 격리, idle 공개 pause 뒤 실제 반환·head·restart를 보완했다. 기존 N·이력·byte batch·계수 상한과 정상 경로는 유지됐다. Returns/ObservedCalls·observe_idle·lifecycle_engine._refresh_readiness를 읽어 관찰 snapshot 복사와 owner 복사 계수의 구별, 실제 제품 호출의 보존을 확인했다. 제품 결함 수리가 아닌 시험 단언 보완이다.

r06은 실제 활동/실행/window의 null 저장과 제한 없음·finish 요청 없음·timeline/CSV, 외부 503의 null/부재·unknown start의 정확 반려·reconciliation/retry, 질문 미해결 text=null과 resolve_user 후 재저장을 보완했다. 실제 생산자·소비자 본문과 변경 단언을 대조했다. 기존 43메서드는 AST상 보존되고 2메서드를 보완·1메서드를 추가했다. 원보고 partial을 유지하며 128파일 후보와 27가족 관계표를 모든 소비자 확인으로 승격하지 않는다.

## 실행 판본과 한계

두 task는 각 3선택·3고유 passed, complete/successful=true이며 fixture_counts/changed_during_run이 비어 있다. 실제 하위 row가 같고 각 Python 876개 SHA가 제출판과 일치한다. 비용 task는 관측 exit0·11.8초이며 readiness 10.094초는 2초 소프트 기준을 초과한다. null task는 0.3초이고 관측 exit 메타데이터가 없어 null로 보존한다. 보고 성공과 프로세스 종료코드를 구별하며 exit 확보만을 위해 재실행하지 않았다. 서로 다른 사본의 3+3을 통합판 6전건 실행으로 세지 않는다. task의 미러 build/check 기록과 실제 3쌍 bytes 일치를 확인했다.

비용 B129 원보고 SHA와 정확 7고유 cost row를 직접 대조했고 전체 successful=false를 유지했다. 직접 소비 runtime/helper의 제출판과 공용판은 같으며, 통합 전 차이는 이번 두 수정 시험뿐이었다. 56,230개 소형 파일과 8.55GB 실내용, 외부 포트 계수와 실제 Git 프로세스 성능은 구별한다. Temp 원보고 9개의 부재는 그대로 두고 수치를 재사용하지 않는다. r06의 B58 외부 storage hunk→현재 producer/수신자/정확 ID와 기존 반려 단언을 읽었으며 Temp 3개 부재·다른 hunk/PR 전체 미검토를 유지한다.

r06 제품 128파일의 공용 차이는 r09의 integration.inspect_bundles뿐이다. AST상 issue/failure_kind/submission_outcome는 불변이고 새 guard는 비문자 mutation target을 schema 반려로 연결한다. 이번 세 producer 시험은 이 함수를 소비하지 않는다. cross와 제출 시험의 다른 변경도 현재 전체 통합판 실행으로 주장하지 않는다.

## 다음 작업 선택

R23/R24·10-B의 지정 다섯 비용 질문은 의미 검토·한정 보완 완료이며 최종 통합판 증거를 기다린다. R06은 M1~M5가 남아 부분 수용이다. 상태 snapshot의 provider_waits=null과 start_guard의 잠재 예외는 현재 live caller만 확인됐으므로 도달 결함으로 단정하지 않는다.

남은 null 범위를 한 세션에서 다시 모두 조사시키지 않는다. 기존 후보와 관계표를 재사용하고 생산·시험 경계에 따라 두 작업으로 나눴다. r06-domain은 제출/검토/계획의 M1/M2와 domain 생산의 M4, r06-edges는 상태/관찰/외부의 M3/M5와 나머지 M4다. null-followup-scope.json은 128개 생산 소스를 51/77개로 중복·누락 없이 분담한다. 소비자는 파일 경계를 넘어 끝까지 읽는다. 이 표는 배정 근거이며 제품 registry가 아니다. 단순 미실행은 미충족과 구별하고 정적으로 충분한 관계는 종료한다.

두 작업은 r06만 선행이다. 직접 시험/helper와 지정 runtime 쓰기는 독립이며 r14-fix·r21-r22·r12-r13-fix와 겹치는 파일은 읽기 전용이다. 비공유 파일에서 확인한 null 결함은 관련 시험·미러·최소 확인과 함께 수리하도록 맡겼다. assignment-review.json에서 기존 정의 불변과 새 writes 교집합이 복원할 캐시뿐임을 확인한다. 두 report의 범위 완료를 합쳐 원래 R06의 남김을 판단하며 G4~G8·L01·Windows1314를 닫지 않는다.

## 게시

context/plan/seams와 두 objective를 먼저 갱신했다. 새 배정과 두 accepted만 더한 queue.pending.json을 check.py queue로 확인한 뒤 검사한 원바이트를 queue.json으로 원자 교체한다. 검사·게시 근거는 queue-check.json이다. status는 active이며 게시 뒤 이번 manager의 공용 변경을 마친다.
