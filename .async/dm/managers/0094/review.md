# manager 0094: 전체 T4 부분 수용과 남은 입력 연결

g7-t4r의 정본 시험 두 파일·시험 지침과 대응 미러, 총 6파일을 `workspaces.py integrate`로 충돌 없이 반영하고 부분 결과로 수용한다. 전체 T4 성공이나 G7 완료로 판정하지 않는다. inbox의 완료 사건은 이 task 하나이며 running은 비어 있다. 현재 state에서도 실행 중 task가 없고 g45-final은 시작 기록이 없다.

## 수리의 의미

`tests/boundary/test_mutation_baseline.py:ActualBaselineTests._run_fixture`는 외부 scratch가 개발 저장소 아래에 있다는 잘못된 전제를 없앴다. scratch에 실제 독립 Git과 빈 commit을 만들어 기준에 없는 subject의 의미를 유지하고, CLI repository_root와 T3의 SCRIPTS도 같은 fixture로 연결했다. 정상 child의 결과·비정상 exit·fixture/skip·다음 witness 및 CLI/T3 판정의 기존 단언은 유지된다. 전체 함수의 극단 변이를 수행한 성과는 아니다.

`tests/boundary/test_operator_bootstrap.py:BrokenEngineProbeTests`는 `scheduled_operator.execute`가 원 failure와 startup을 별도 게시한 뒤 `{**result, 'startup': startup}`을 반환하는 현재 계약을 정확히 검사한다. 저장된 두 레코드와 전체 stdout을 대조하고 live bootstrap/runtime/설치 신원도 단언한다. 제품 runtime은 불변이며 예전 기대값을 살리기 위한 제품 호환 분기는 없다. 지침과 미러가 두 수정의 의미를 반영한다. 공식 restore로 시작판 세 정본 파일을 읽었고 전체 diff는 accepted-diff.txt에 남겼다.

## 직접 확인한 범위

원 report 네 개의 selected와 고유 실제 행·집계·완결·성공 여부·실행 중 변경 및 execution.json의 명령/exit를 대조했다. a는 304선택/292passed·9error·1failed·2skipped/exit1, fix는 9선택/8passed·1error/exit1, fix2는 1passed/exit0이다. 최종 b는 304선택/301passed·1error·2skipped/exit1이며 중복·누락·여분과 fixture 행이 없다. complete=true, successful=false, changed_during_run=[]다. fix의 마지막 오류는 T3 fixture 경로 연결 누락이며 최종 b의 수정 대상 9행은 모두 passed다. 서로 다른 판본을 합산하지 않는다. 최종 공식 1570.4초의 소프트 기준 초과는 유지한다.

최종 source_sha256 919개를 제출판과 대조했다. 통합 전 공용 소스의 차이는 수정한 시험 두 파일뿐이다. 정본/미러 세 쌍은 동일 bytes이며 Python 두 쌍은 동일 AST다. adapter.complete/tests_complete=true·problems=[]·61 worker의 기록을 읽고 Lake 오류 worker011, mutation worker015, bootstrap worker019의 request/run/source_after·게시 artifact SHA·실제 원행을 직접 대조했다. 나머지 worker의 branch DB, 2881 raw copy의 SHA, 문서 전체 판본·Git 준비·종료 장벽/잔존 PID는 작업자의 audit/verification 근거를 범위대로 수용했으며 manager가 전부 다시 실행·재감사하지 않았다. manager 제품시험은 0회다. `check.py report`가 통과했고 integration.json의 여섯 경로를 수용한다. 상세 직접 확인은 verification-review.json이다.

## 남은 입력은 확보 가능하다

Lake 오류의 원 traceback은 workspace 기본 `.skill-workspace`에 lake.exe가 없어 발생한 WinError2다. 현재 시험은 compiler용 명시 환경 입력을 공유하지 않고 `portable_bin(toolchain_root())`를 직접 쓴다. manager는 공용 설치의 `C:/math/.skill-workspace/do-math-toolchains/lean-4.32.0/lean-4.32.0-windows/bin/lake.exe`와 lean.exe의 실제 존재·크기·SHA를 확인했다. Lake/Mathlib 실행 성공을 확인한 것은 아니다. 외부 설치 부재로 영구 차단하지 않고 이 실제 입력을 시험에 연결하는 작은 수리를 다음 준비에 포함한다.

두 provenance skip은 이번 실행에 SHARED_INPUT_BASELINE_SCRIPTS를 지정하지 않은 결과다. phase016/provenance-baseline/evidence/review.md와 baseline-manifest.json에 기존 pre-fix scripts가 보존돼 있다. 도입 bbe64043f49d46fb7c3b6e768b99a8acbaa125cf의 실제 첫 부모가 010b059700115f6d5d3df1bf24e931cf78eaa44a임을 Git 읽기로 확인했고, 보존 입력의 필수 일곱 파일 SHA를 manifest와 대조했다. manager는 새 추출이나 old/new 실행을 하지 않았다. 910개 전체 준비의 기존 근거를 재사용하며 현재판·임의 구판으로 대체하지 않는다.

## 다음 배정

미시작 g45-final의 기존 두 관문 준비에 Lake 입력 연결과 위 세 정확 T4 선택을 묶는다. 실행은 같은 task의 jobs1로 먼저 마치고 전체 일반/fresh T3는 기존 jobs3로 순차 수행한다. 실제 입력 경로·원 기준 근거·이번 수용 기록을 inputs에 추가하며 depends_on=g7-t4r와 쓰기 범위/모델은 유지한다. 나머지 114개 정의는 변경하지 않는다. 독립 기능이나 새 제공자 수리가 발견된 것이 아니므로 이 소수 입력 보완을 별도 task로 나누지 않는다.

이미 끝난 전체 T4를 세 남김 때문에 자동 반복하지 않는다. 세 직접 결과와 기존 불변 성질의 재사용은 각각 기록하며, 원 전체 보고의 unsuccessful를 successful로 바꾸지 않는다. 후속 소스 변경이 기존 T4 성질에 영향을 주면 영향받은 범위만 설명하고 필요한 확인을 한다. 전체 G7 완료 여부는 나머지 실경계/원자료와 함께 별도로 판단한다.

공용 context/plan/seams와 objective를 먼저 갱신하고 검사한 임시 큐를 마지막으로 원자 게시한다. 게시안은 115정의·accepted110·취소4·미해결1·active다. G6는 stable fresh T3/함수 진입 색인을 실제 소비한 뒤 준비한다. G1~G3 최종 연결과 한정 검토 밖의 실제 남김, L01 Q1/Q2/원 UTF-8 byte, 환경6arc/10행, 현지원 공급자 quota/복수result/역할 동적 schema, 나머지 G7/G8은 유지한다. 저장범위/A22에 따라 공통 codec·검증 게시·충분한 업무 보장을 재사용하며 가족별 quota·반복 유료호출·장기 감사는 추가하지 않는다. workspace 정리는 manager 종료 뒤 실행기가 맡는다.
