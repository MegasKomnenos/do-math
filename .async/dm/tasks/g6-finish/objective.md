# 남은 G6 문제 함수만 재확인하고 수리 결과를 통합 가능한 상태로 마친다

사용자가 원하는 결과는 결함이 시험을 빠져나가는 공백을 실제로 막고 그 근거를 사용할 수 있게 만드는 것이다. 최초20묶음은 완료됐다. 이 작업은 그 실행을 반복하는 일이 아니라, 중단된 g6p-run의 유효한 수리31파일을 새 사본에 가져와 남은21개 함수의 변이/정상 대응과 listing·미러·보고를 마치는 일이다.

## 시작과 권위

SESSION_JSON·task.json·고정 inputs/context.md/plan.md/seams.md, 자기 do-math AGENTS.md·시험-지침.md를 읽는다. RECORDS의 sources/resume-g6-2026-10-18.md·mutation-recheck-direction-2026-10-17.md가 과거의 '최소 모듈 전체 재확인'보다 우선한다. sources/t3-targeted-direction-2026-10-16.md·storage-scope-direction-2026-10-15.md·mutation-parallel-direction-2026-10-16.md의 범위/자원 제약도 유지한다. manager0104/review.md·candidate-manifest.json·remaining-functions.json·verification-review.json이 이번 인계다.

실제 선행은 수용된 mutation-parallel이며 g6-inputs/g5-remainder가 그 선행에 포함돼 있다. g6p-run은 cancelled·미수용이고 의존관계에 넣지 않는다. 그 report는9묶음 시점의 중간본이다. 옛 report나 사본·원자료를 편집하거나 그 ID를 재파견하지 않는다.

## 이미 끝난 결과와 정확한 남김

원 execution-summary는1677함수=1613killed/10survived/22execution_error/32trivial이다. 원모집단·index·선택·실제 정상 대응과 판본을 그대로 재사용한다. 원32문제 중7개는 완료 repair-b02/b03/b04/b05에서 해결됐다. 세 planning 함수는 부모가 미완료인 repair-b09에서도 개별 mutant/normal child가 각각 완료됐으며 manager가 raw 결과를 대조해 따로 보존했다. 이10개를 다시 실행하지 않는다. LocalCLIAdapter.provider_failure의 pass는 현재 무조건 None 반환과 동등하고 정확 사유가 있다. remaining-functions.json의 pending21개(생존8/실행오류13)가 실행 출발 목록이며 module/function/rule을 정확히 소비한다. 숫자는 quota가 아니며 실제 직접 영향으로 범위가 달라지면 이유를 명시한다.

repair-b09의 외부43 outcome과 stale repair-summary의15를 배치 완료로 합치지 않는다. 재사용할 세 함수의 원30파일은 managers/0104/evidence/repair-b09에 영구 보존돼 있다. 다른 이미 유효한 결과를 단순히 이전 exit1·report partial·판본 변경 때문에 재실행하지 않는다. 기존 reuse-impact.json·assertion-preservation.json·b01-reuse.json과 source-snapshot/edition을 필요한 변경 범위에서 재사용한다. 전수 증거 재감사나 새 모집단 준비는 하지 않는다.

## 미완성 변경을 자기 사본에 가져오기

manager0104/candidate-manifest.json의 canonical_files31개와 candidate/ 파일만 이식 후보로 사용한다. 각 목적 파일의 자기 baseline/현재 bytes를 manifest의 baseline/source와 비교하고, 일치하면 보존 후보 SHA를 확인해 자기 workspace에 적용한다. 새 baseline과 다르면 해당 hunk의 목적을 비교해 조정하고 기록한다. 후보의 실제 diff는 managers/0103/candidate-diff.txt이며 기존 검토를 반복 생성하지 않는다.

옛 workspace 전체, 중간 .agents 미러, .hypothesis cache, 실행용 .selection-index/.timings/.t3-store를 복사하지 않는다. 후보 정본19개는 옛 미러와 다르므로 이식 후 자기 정본에서 공식 build_skill_mirrors.py로 미러를 만든다. 실제 runtime123모듈은 공용판/후보판/원G6 모두 같고 정본 Python 후보는 source-snapshot-r10에 대응한다.

이식 내용은 callable 표기, fixture 예열의 오류를 실제 소비 시험으로 전달, 유한한 합성 초기화, Job cleanup, 직접 단언 보완이다. 원 생산자·생산순서·모집단·기존 단언을 유지한다. 가까운 보완과 새로 드러난 직접 제품 결함은 이 task에서 함께 고친다. 원래 예열의 이름만 보고 다른 모듈을 일괄 정리하거나 저장 가족별 보장을 다시 입증하지 않는다.

## 기존 도구에 정확 함수 선택을 작게 추가한다

현재 scripts/tests/support/mutation.py:run/main은 --only 모듈 glob, --test 명시 시험, --every와 --jobs를 제공하지만 정확 함수 선택은 없다. 기존 경로에 반복 가능한 **--function scripts-relative-module:qualified-function-key** 선택을 추가한다. 예: `--only do_math/submission.py --every --function 'do_math/submission.py:_payload_issues.<locals>.resolution'`. API도 같은 의미의 선택 인자를 제공하고 실제 이름/형식은 이음새에 설명한다. 함수 키는 기존 functions/changed_functions가 만드는 정본 키를 사용한다.

선택을 지정하면 그 정확한 함수만 계획하고 변이·정상 child를 만든다. 중첩 함수 키를 지원하며 오타/없는 함수/범위밖 모듈/해석되지 않는 선택은 실행 전에 명확히 실패시킨다. 0건 성공이나 전체모듈 fallback으로 바꾸지 않는다. 선택을 생략한 기존 호출의 동작은 유지한다. 기존 원index+명시시험 합집합·cheap-first/failfast·실패후보 정상 확인·실제 정상 통과 판정·jobs 합계상한·중단/출력/exit 의미는 유지한다. update_list는 정확 실행 결과가 있는 항목만 갱신하고 선택 밖 항목을 지우지 않는다.

선택 로직과 실제 작은 fixture에서 대상1/비대상1(필요하면 nested key 포함)으로 의도한 함수만 실행되고 오타가 child 전에 실패함을 판단할 최소한의 검사를 한다. 이미 검증된 병렬기 전체를 반복 시험하지 않는다. 새 executor·명령간cache·함수별 resume 시스템·자동 outcome 합치기 framework는 만들지 않는다. 관련 코드·시험·이음새·시험 지침·미러는 같이 마친다.

## 잔여21개 실행과 결과 마감

1. 문제 함수의 원 batch/selection·추가 시험ID를 기존 population.json·execution-arguments.json·repair-arguments.json에서 가져오되 **옛 모듈 전체 repair argv를 그대로 실행하지 않는다**. 미해결 정확 키로 제한하고 그 함수의 원 유효 index 선택을 보존한다. 이미 추가된 관련 직접시험ID를 합친다. 원index 진입과 새 명시 선택을 구별한다. 원색인 SHA는3d30a04ea8e68cb138995e0f5a913981faa6cb0afc02fa0b8d682fa9b9a58824, commit은4dae85911f26f891fc3d79be9916bf4363e2d46f다.
2. 자기 workspace에 독립 Git을 준비할 권한이 있다. managers/0095/g45-index-baseline.bundle과 g6p-run의 git-preparation/index-preparation을 재사용하여 raw bytes를 바꾸지 않는 mixed reset·자기 snapshot commit으로 ancestry를 잇는다. core.autocrlf=false, hooks/gpgsign/fsmonitor 비활성, info/attributes의 `* -filter -text -ident`를 사용한다. checkout/--hard·공용/전역 Git 수정은 금지다. 준비 전후 필요한 bytes·root/ancestor/색인 사용 가능성을 확인한다. 원자료/색인을 고치거나 전체T3로 색인을 다시 만들지 않는다.
3. 자기 generated 입력은 시작 bytes/부재를 보존하고 실행 뒤 복원한다. TEMP/TMP/TMPDIR/output은 저장소 밖 짧고 새 경로, 예컨대 C:/g6finish-0104를 사용한다. 기존 raw 출력은 비우거나 이어 쓰지 않는다. 명령 하나씩 **--jobs 3**, 변이+정상 합계 최대3개를 사용한다. 일반/선택기 검사는 변이 명령과 겹치지 않게 jobs1로 수행한다. 시간은 소프트이며 경과시간을 실패/포착으로 삼지 않는다. 명령 동안 source·시험·index·timings를 바꾸지 않는다.
4. 비동등 생존과 오류에는 실제 계약·소비·실패 원인에 필요한 단언/수리만 보완하고 그 정확 항목을 재확인한다. 정상 failed·fixture/load error·skip·0건·결과부재·비정상 exit·중단을 killed로 바꾸지 않는다. 수리가 다른 결과의 의미에 실제 영향을 주면 그 구체적인 함수/시험과 이유를 밝히고 직접 범위만 확인한다. 같은 모듈이라는 이유나 포괄적인 판본 변경 이유는 범위 확대 근거가 아니다.
5. listing은 옛 generated 파일을 그대로 최종 결과로 복사하지 않는다. 원 main-pseudo_tested.json·동등 사유·10해결 항목·새 결과를 연결해 현재 살아 있는 정확 항목과 정당 사유를 기록한다. 이미 해결된 _shared_index처럼 부모 미완료 때문에 남은 listing 항목은 보존된 실제 child/normal 근거를 명시해 정리한다. 빈 사유 면제, 오류 은폐, 최종 전체 재실행 성공 주장은 하지 않는다.
6. 기존 정상 수리 r8의19passed/1error와 r9재실패, r10정확1passed는 다른 판본이다. 기존 충분한 정상 결과를 재사용하고 새 선택 도구/실제 수리에 필요한 정확 일반시험만 수행한다. 모든 raw attempt/result/spec/output·native exit·실행 판본을 자기 영구 evidence 또는 이미 보존된 evidence에 연결한다. 새 실행 결과는 command 종료 때마다 간단한 진행 기록을 갱신해 중단 시에도 마지막 완결 범위를 알 수 있게 한다.

완료는31후보와 직접 후속 수정이 자기 정본/미러에 일치하고, 원1677함수의 원실행·유효 재사용·정당 동등·필요한 정확 재확인과 남김이 누락/중복 없이 연결되며, 실제 비동등 공백/실행오류가 해소되고 listing·report가 현재 상태를 반영하는 것이다. 미해결이 남으면 partial과 정확 남김을 보고한다. 세부 판단은 evidence/judgment.md와 간단한 함수별 처분에 담고 `python C:/math/services/async-development/check.py report C:/math/.async/dm g6-finish`를 통과시킨다.

이 task는 전체 일반/T3/T4/T5·실공급자 호출·설치·예약·graphify·공용 Git/push·기존 연구 운전을 하지 않는다. G1~G3최종연결·G5 환경/부분index 조건·G7/G8은 별도이며 이번 결과로 함께 성공 처리하지 않는다. 공용 context/plan/seams/queue/state와 이전 task/manager 기록은 읽기전용이다. 과거 파일이 필요하면 공식 workspaces.py restore로 별도 새 경로에 필요한 baseline/result만 복원한다.
