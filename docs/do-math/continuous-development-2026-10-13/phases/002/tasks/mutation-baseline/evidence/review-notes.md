# PR01/B56 중 이번에 판정한 범위

대상은 mutation child 결과, 정상 기준, CLI/T3의 공통 passed 소비다. PR01의 T3 저장소·전체 실행기·공유 입력 provenance 재검토는 이번 완료 범위에 들지 않는다.

## 이전 변경과 현재 소비

`bbe64043f49d46fb7c3b6e768b99a8acbaa125cf`의 실제 diff를 `bbe64043.patch`에 보존했다. B56은 mutant 결과 부재를 execution_error로 분리하고 CLI 및 run_tests._finish_t3에 mutation.passed를 연결했다. loader의 TypeError를 보존하고 모듈별 저비용 순서·다음 모듈 진행 시험을 보강했다. 이 성질들은 유지한다. 단, failing 문자열 집합만 반환하는 계약에서는 정상 child 결과 부재가 정상 통과로 간주되고, loader 오류 문구도 정상 검증 없이 killer가 됐다. 이번 실제 red2 반례와 단일 결과 계약으로 이 부분을 교정한다.

`f56a277231b9260cb15d163564e8465b99b3ccc7`의 실제 diff는 `f56a2772.patch`다. timeout 인자·mutant_timeout·시간에 따른 kill과 baseline timeout 경로를 제거하고 process.wait()로 실제 종료를 기다리게 바꾼 것은 최신 사용자 지시와 맞아 유지한다. B56 board의 timeout 문언을 현재 요구로 복원하지 않는다. 새 코드도 대기에 timeout을 주지 않는다. elapsed=10000초인 process 경계 대역의 정상 실행은 survived로 기록한다.

현재 mutation.main과 run_tests._finish_t3는 이미 동일한 mutation.passed를 호출한다. runner 제품 구현의 변경은 필요하지 않았다. baseline_failing 상태의 소비 시험을 unit.test_runner_tiers에 보강했다. boundary.test_mutation_baseline은 작은 모집단을 주입한 실제 mutation.run, 실제 Python child를 CLI와 T3 소비에 연결해 정상 기준 통과/결과 부재를 각각 관찰한다. T3의 분기 측정만 독립 대역이고, mutation 결과 dict를 미리 만들어 주지 않는다. 이 시험은 전체 T3 측정의 대체 증거가 아니다.

## 원보고의 한계

board의 `/current_work/measurement_integration`을 원문으로 확인했고, 지정한 네 원보고 경로를 실제 조회했다. `changed_area`, `structure`, `timing_red`, `exact_baseline_comparison`의 외부 임시 파일은 모두 현재 없다. 위치·과거 해시·존재 여부는 `prior-review.json`에 보존했다. 따라서 board의 83통과/2skip 등 과거 counts를 이번 실제 검증 결과에 합산하지 않는다. 삭제 원인은 추정하지 않는다. 이번 범위의 유지/교정 판정은 실제 commit diff, 현재 직접 소비자, 새 공식 시험과 실제 child 원출력에 근거한다. 나머지 PR01 원보고 회수·대체 검증 필요 여부는 해당 후속 범위에서 판단한다.

## 실제 재현과 한계

`red`의 첫 fixture 실행은 Git stdin-paths에 하위 cwd 상대 경로를 준 준비 오류로 2 error였다. 결함 red로 세지 않는다. repo 상대 경로로 fixture를 바로잡은 `red2`는 정상 대조군 1 pass, 정상 결과 부재 반례 1 fail이었다. 실패 단언은 `killed == killed`이며 정상 결과 파일이 없는데 보고가 killed/통과가 된 실제 경로를 입증한다.

`focused1`은 최초 수정의 29 pass다. `related-green`은 확장한 관련 선택 58개 중 57 pass/1 fail이며, 부분 실행 fixture가 ID 정렬 이후 실제로 누락한 ID와 단언의 ID가 달랐다. 부모의 오류 판정은 올바랐다. fixture가 완료할 ID를 명시해 교정한 최종 판본은 `related-final`에서 판정한다. 이전 출력은 덮어쓰지 않았다.

유한 오류 행렬은 process/file 경계의 Popen 대역을 쓴다. 실제 부모의 파일 읽기·검사·정상 기준·재시도 판정은 그대로 실행한다. 실제 child 시험은 격리 Job의 scratch에 원본 소스·임시 mutant·모든 시도와 보고를 남긴다. 작업 트리 제품은 변이하지 않는다. 일반 전체·fresh T3·대상 함수 전체 변이·T4/T5 전체는 수행하지 않았다.
