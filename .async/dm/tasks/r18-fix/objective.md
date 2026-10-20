# 목적과 완료할 결과

R18/9-A 조사에서 확인한 F1을 수리한다. 현재 Windows 파일 교체의 native binding과 alias 소비를 기존 소유권 검사가 실제로 발견하여, 교체 구현이 공통 owner인 file_io 밖으로 옮겨지면 실패하게 한다. 검사·최소 반례·관련 설명·미러·필요한 확인을 한 작업에서 마친다. 제품 runtime 고장은 관측되지 않았으며 최종 review가 아니다.

## 입력과 쓰기 범위

SESSION_JSON의 workspace와 고정 inputs/context.md·plan.md·seams.md, task.json을 기준으로 일한다. 스킬 상대 경로는 자기 workspace 기준이다. C:/math/.async/dm/tasks/r18/report.json 및 evidence/conclusion.md·boundary-map.json·predicate-observations.json·native-replacement-counterexample.json·historical-report-slices.json, managers/0004/review.md·source-review.json은 수용된 읽기 전용 근거다. 과거 run:은 C:/math/docs/do-math/continuous-development-2026-10-13 기준이다.

수정 범위는 `.claude/skills/do-math/scripts/tests/structure/test_boundary_invariants.py`와 대응 `.agents` 미러다. native 검사 의미에 필요한 설명은 해당 모듈의 docstring/주석에 반영한다. file_io.py 및 다른 runtime, 다른 구조 시험·helper, 이음새-정본.md는 읽기 전용이다. 범위 밖 실제 결함을 발견하면 정확 반례와 필요한 파일을 보고한다.

두 `scripts/tests/.timings.json`은 공식 실행기가 자기 사본에 기록할 수 있어 writes에 포함했다. 시험 종료 후 생성된 비용 자료를 자기 evidence에 보존하고 이 두 파일만 자기 base 원바이트로 복원하여 최종 changes에서 제외한다. 다른 변경은 되돌리지 않는다. r02-fix·r07-fix와 의미 있는 파일은 독립적이며 두 작업의 종료는 선행 조건이 아니다. 공용 문서·queue/state·engine·다른 task·Git index·과거 증거를 수정하지 않는다.

## 현재 사실과 구현 판단

1. `file_io._windows_files`는 `rename=kernel.SetFileInformationByHandle`을 tuple의 네 번째 값으로 반환한다. `_replace_once`는 이를 받아 `rename(handle,22,buffer,size)`로 교체하고 handle을 닫는다. 현 `test_only_file_io_replaces_files`는 ast.Call의 os.replace/shutil.move Attribute만 찾으므로 이 native 경로를 전혀 발견하지 않는다. 현재 runtime owner는 올바르다.
2. 같은 소유권 검사에서 현재 native binding과 alias 소비를 발견하도록 최소한으로 확장한다. 발견 결과에 `_windows_files`의 binding과 `_replace_once`의 소비가 실제 source에서 포함되고 그 owner가 file_io라는 것을 확인한다. 단지 허용 목록에 두 함수명을 추가하거나 문자열 rename을 모두 교체 호출로 간주하는 방식은 이 사실을 입증하지 못한다. 실제 코드의 binding·반환·소비 형태를 다루는 데 필요한 범위만 구현하며 임의 Python 별칭/동적 우회 전수 분석으로 넓히지 않는다.
3. 같은 탐색/소유 판정 경로로 정상 현재 source는 수용하고, 동일 native binding과 소비를 다른 모듈로 옮긴 순수 AST source fixture는 반려한다. 소비만 file_io 밖으로 옮긴 경우에도 owner 위반을 감출 수 없는지 현재 tuple 소비 형태로 확인한다. fixture는 메모리의 source/AST로 충분하며 실행 가능한 제품 파일이나 WinAPI 호출은 필요하지 않다. file_io의 일반 파일 읽기와 관계없는 rename 이름을 교체로 오인하지 않도록 발견 조건을 실제 연결에 둔다. 구체적 helper·단언 배치는 담당자가 정한다.
4. os.replace/shutil.move 검사와 기존 process/native Job/인터프리터/정규화/stdlib 검사의 모집단 및 정확 단언을 유지한다. 파일 교체 runtime, 재시도 정책, 제품 스키마·API는 바꾸지 않는다. 일반 파일시스템·보안 전수 감사나 새 등록 프레임워크는 필요하지 않다.

## 필요한 확인과 미러

AGENTS.md와 scripts/tests/시험-지침.md를 따른다. 자기 workspace의 공식 `scripts/run_tests.py`를 사용한다. 먼저 가장 작은 반례가 기존 발견 조건의 누락을 드러내는지 확인하고, 수정 후 `structure.test_boundary_invariants --jobs 1 --output <새 짧은 절대 경로>` 한 모듈로 인계한다. 기존 6 ID와 추가한 최소 정상/음성 단언의 선택·실제 row·exit·소스 판본을 남긴다. 준비/import 오류를 결함 재현으로 세지 않는다. 이미 충분한 확인을 반복하지 않는다.

구조 소유권의 불확실성은 AST로 해결할 수 있다. 새 실제 모델/Job/Lean/예약/네트워크, Windows 파일 교체 실경계 재실행, 전체 일반/T3/변이/T4/T5는 이 배정에 필요하지 않다. 기존 `boundary/test_storage_atomic_replace.py`의 4 ID 및 018 원보고는 runtime을 변경하지 않은 성질의 근거이며 새 실행으로 보고하지 않는다.

실행 중 자기 소스를 고정하고 jobs1을 사용한다. 출력은 workspace 밖 자기 task/evidence 또는 저장소 밖 짧은 새 경로에 둔다. 정본을 고친 뒤 workspace의 `.claude/skills/writing-skills/scripts/build_skill_mirrors.py --target .agents`로 미러를 생성하고 예상 범위 밖 변경이 없는지 확인한다. 미러 대응과 생성기 `--check --target .agents`로 충분하면 같은 시험을 미러에서 반복하지 않는다. 모든 실행 뒤 비용 캐시를 evidence에 보존하고 자기 base로 복원한다. graphify 갱신과 기존 연구 변경은 하지 않는다.

## 제출과 남김

evidence에 F1의 실제 source 연결, 기존 조건에서의 반례와 수리 후 결과, 최종 판본·범위·한계를 기록한다. r18 원보고는 수정하지 않는다. async report.json의 status, summary, changes, verification, findings에 결과를 적고 `python C:/math/services/async-development/check.py report C:/math/.async/dm r18-fix`에서 PASS를 확인한다.

완료 조건은 현재 native 교체 경로의 구조 검사 공백을 닫는 것이다. R18/9-A를 최종 판본 증거 대기로 옮길 근거를 남기되 PR02 전체·관련 K/P2 전체, G4~G8, L01 Q1/Q2·UTF-8 byte, Windows1314 symlink 실반려 미검사와 다른 의미 질문은 종결하지 않는다. 통합·accepted·관리 마감은 manager가 맡는다.
