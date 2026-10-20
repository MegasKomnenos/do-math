# 현재 통합 후보의 전체 일반 검사와 발견한 결함 수리

현재 수용된 do-math 제품·시험 판본에서 G4 전체 일반 검사를 완결한다. 이전 task의 관련 선택 성공을 합산한 상태에서 벗어나, 공식 실행기의 기본 전체 선택이 하나의 고정된 최종 판본에서 실제로 모두 실행되는지 확인하는 작업이다. 실제 실패가 드러나면 원인 판정·필요한 제품/시험 수리·직접 확인·설명/공식 미러를 이 task에서 함께 마친다. 별도 저장 가족 전수 감사나 새 프레임워크를 만들지 않는다.

SESSION_JSON, task.json, inputs/context.md·plan.md·seams.md, workspace의 do-math AGENTS.md와 scripts/tests/시험-지침.md를 먼저 읽는다. C:/math/.async/dm/managers/0063/review.md와 sources/storage-scope-direction-2026-10-15.md를 적용한다. 사용자 목표/G1~G8은 유지하며 이번 배정의 완료 범위는 G4다. 저장의 상시 검증/공통 codec/기존 업무 시험은 유지하고, 전생산자·전필드·새reader·옛head를 가족별 새 선행조건으로 확대하지 않는다.

## 실행과 자원

1. 자기 workspace가 현재 수용판을 받은 상태인지 inputs와 baseline으로 확인한다. C:/math 공용 소스와 다른 task 사본은 읽기 전용이다. 모든 수용 work를 포괄하는 선행13개 끝점이 task.json에 있다. 과거 task의 서로 다른 판본 통과를 이번 성공으로 대체하지 않는다.
2. 정본 `.claude/skills/do-math/scripts/run_tests.py`를 **위치 선택·--tier·--match 없이** 실행한다. 현재 DEFAULT_FOLDERS=TIERS['T3']는 structure/unit/contracts/sim/flows의 일반 선택이며, --tier T3 측정 실행과는 다르다. 기본 명령은 `python -u -B .claude/skills/do-math/scripts/run_tests.py --jobs 3 --output <새 출력 경로>`다. manager가 이번 단독 전체 일반 작업에 기계 시험 슬롯3개 전부를 배정했다. 별도 시험 명령을 동시에 실행하지 않으며, 다른 시험 실행이 있음을 확인하면 합계3 이하로 jobs를 낮춘다. 무거운 실행을 이유 없이 폴더별로 중복하거나 미러에서 같은 전체를 다시 실행하지 않는다.
3. 출력/임시 자료는 workspace 밖 task/evidence 또는 저장소 밖 짧은 고유 경로에 둔다. TEMP/TMP/TMPDIR와 GIT_CEILING_DIRECTORIES의 기존 격리 규약을 따른다. 외부 fixture의 cwd가 상위 C:/math Git을 집지 않도록 확인한다. `--output`이 길어져 설치 snapshot 경계에 영향을 주지 않게 짧은 경로를 택하고 최종 원자료 위치를 보고한다. 실행 중 소스/시험/문서/미러를 편집하지 않는다. 시간은 소프트 기준이며 timeout·시간에 따른 강제 종료를 도입하지 않는다.
4. 실행 전후 해당 제품·시험·문서 판본을 기록한다. 공식 report.source_sha256/changed_during_run은 scripts의 Python 범위라는 한계를 유지하고 문서·미러의 판본/공식 생성기 check도 별도로 연결한다. 전체 소스 전수 의미 감사는 필요 없다. 비용캐시 .timings.json은 관측 자료를 evidence에 보존한 뒤 자기 base로 복원하여 제품 변경에서 제외한다.

## 실패 처리와 수리 범위

실패하면 원 report/traceback과 해당 정의·호출부를 먼저 읽고 제품 결함, 현행 계약과 어긋난 fixture/기대값, 환경 준비 오류를 구별한다. 실행이 있어야 가를 수 있는 경우에만 정확한 실패 ID와 작은 입력을 사용한다. 현재 실패를 '기존 실패'로 면제하지 않는다. 기준과 비교가 필요하면 own base의 정확한 시험만 쓰며 과거 공용 소스를 수정하거나 stash하지 않는다.

관련 구현·직접 소비 시험·helper·설명을 같은 수리로 묶는다. task.json.writes는 미지의 실제 실패를 수리할 수 있도록 do-math 정본/미러 디렉터리를 포함하지만, 권한은 이 전체 일반 검사에서 확인된 결함과 직접 연관된 경로에 한한다. 단언 약화, skip/모집단 축소, timeout, 임의 내부 대역, 구판 호환/저장 이전 계층, 무관 정리로 성공을 만들지 않는다. 비용 초과만으로 기능 실패를 만들거나 별도 최적화 작업을 확장하지 않는다.

수리했으면 가장 작은 관련 공식 선택으로 확인하고, 공식 build_skill_mirrors.py로 대응 미러 생성/check를 마친다. 생성기·다른 스킬·overlay·서비스는 수정 범위 밖이다. 이미 관측한 실패 보고는 그대로 보존한다. 최종 수리판을 고정한 뒤 기본 전체 선택을 한 번 완결하여 G4 증거를 만든다. 이후 소스가 다시 바뀌지 않았다면 성공한 전체를 재실행하지 않는다. 해결할 수 없는 외부 조건/범위 밖 결함이나 여러 큰 독립 수리가 드러나면 정확한 실패와 영향·유효 수리·남은 목표를 partial/blocked로 보고하고 전체 통과를 주장하지 않는다. 관련 수리를 별도 task로 자동 쪼개지는 않는다.

## 완료와 인계

최종 기본 전체 실행의 command/cwd/비밀 아닌 필요한 환경, 실제 시작/종료와 관측 exit code, 원 stdout/stderr와 report를 보존한다. selected와 fixture가 아닌 reports[].rows의 ID가 중복·누락 없이 대응해야 한다. counts뿐 아니라 fixture_counts, 각 row/subTest, complete/successful, changed_during_run, source_sha256과 최종 제출판 일치도 대조한다. 실패·오류·미실행이 없어야 하며 skip/expected_failure가 있으면 원문 계약상 정당성을 정확한 ID/이유로 별도 판정한다. 그 행을 passed로 세지 않으며 boolean successful만으로 G4를 닫지 않는다. 시간/소프트초과는 실제 관측대로 남긴다.

제품 변경이 없으면 정본의 고정판 전체 실행과 공식 미러 check로 마친다. 변경이 있으면 검증한 최종 제품·시험·문서와 생성 미러를 제출한다. 보고에는 G4 충족 여부, 원실패→수리의 이유와 직접 근거, 마지막 전체판의 정확 결과 및 남김을 분명히 적는다. G1~G3 의미 판정 전체나 G5~G8을 이 성공으로 닫지 않는다. fresh T3(--tier T3 --full), 극단 변이, T4/T5·모델/HTTP/Lean/설치·OS예약 실호출은 이번 일반 검사에 덧붙이지 않는다. 후속 manager가 G4 실제 수용판을 기준으로 fresh T3와 나머지 명시 관문을 배정한다.

최소한 evidence의 판정 문서와 원보고 위치/판본/exit 연결을 남기고 report.json을 작성한다. `python C:/math/services/async-development/check.py report C:/math/.async/dm g4-general`을 통과시킨다. source_repo·공용 context/plan/seams/queue/state·다른task·engine·Git index/commit·graphify·기존 연구는 수정하지 않는다.
