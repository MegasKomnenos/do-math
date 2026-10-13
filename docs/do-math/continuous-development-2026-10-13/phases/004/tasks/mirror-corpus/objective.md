## 목적과 역할

phase 003 provider-smoke의 F2를 수리한다. 공식 미러 생성은 성공했지만 Claude CLI help 원자료의 `CLAUDE.md`가 `AGENTS.md`로 치환돼 미러의 원 SHA와 재생 판정이 실패했다. 현재 두 파일에서 재현되며 하나는 phase 003 이전부터 있던 녹화다. G7의 원출력 무결성과 G8의 정본/인도 일치를 회복하는 작은 작업이다.

현재 생성기는 `.agents/diff/_rules.json`의 `verbatim` 패턴을 텍스트 변환보다 먼저 적용해 바이트를 그대로 반환한다. 이미 있는 이 경계를 사용해 do-math 녹화 말뭉치를 보호한다. 새 생성 프레임워크나 공급자별 예외 처리를 만들지 않는다. Codex의 실제 maintenance schema HTTP 400 거부(F1)는 별도 후속 work다. 이 수리에서 모델을 재호출하거나 역할 schema·worker·parser를 바꾸지 않는다.

입력의 phase 003 report와 manager verification을 읽고 실제 `_rules.json`, `build_skill_mirrors.transform/build_target`, corpus manifest, structure/replay 소비를 대조한다. 과거 재검토는 이번 실패를 만든 현행 텍스트 치환/축자 복사 규칙의 필요한 도입 diff와 현재 소비 범위에 한정한다. PR15 전체를 다시 감사하지 않는다.

## 완료 조건

### A1 원바이트 변형과 영향 모집단을 확정

정본과 미러의 corpus 파일 전부를 경로·바이트 해시로 대조하고 manifest의 녹화 참조와 연결한다. 현재 관찰은 17개 항목·44개 파일이며 실행 시 실제 파일에서 다시 확정한다. 기존 `capabilities/claude-surface-1.txt`와 신규 `capabilities/claude-20261013-1.txt`의 정본 SHA `a58ca2282c01312250fc8d861088dae6e46340ad55346557fcdbc0053f415367`가 미러에서 `1804fa77a537f63782a027a44937d3219b8d3aaf0b344dd87d26cf61b02925a4`가 된 원인을 규칙과 실제 diff로 확인한다. phase 003 원보고의 4선택/2통과/2실패와 공식 --check 성공을 서로 다른 주장으로 유지한다. manager의 git-clean-observation.json에는 현재 정본 manifest, Lean 입력, scheduler 녹화 세 파일이 Git clean 개행 변환을 받는 추가 관찰도 있다. 이를 실제 Git 저장 완료의 실패와 구별하고 같은 원바이트 인도 범위에서 확인한다.

과거 실패 증거가 현재 바이트/규칙과 같으면 수리 전 공식 재생을 비용 없이 재사용할 수 있다. 기존 파일의 원 SHA/verdict를 변형된 미러에 맞춰 고치거나 녹화를 새 성공으로 덮어쓰지 않는다. 불일치가 다른 파일에도 생겼으면 그 파일·원인과 새 변경 여부를 구별해 보고한다.

### A2 기존 축자 복사 규칙으로 녹화 전체를 보존

현재 `_rules.json`의 `verbatim`으로 `do-math/scripts/tests/corpus/`의 manifest와 모든 녹화 파일이 그대로 생성되도록 한다. 실제 녹화 데이터 안의 `.claude/`, `CLAUDE.md`, 경로·개행·BOM 등은 런타임별 지시문 치환 대상이 아니다. 현재 두 help 이름만 열거하지 말고 이 원자료 경계 전체를 보호한다. 다른 스킬과 일반 do-math 지시문의 필요한 런타임 치환은 유지한다.

기존 생성기 시험에 이 실패를 검출하는 작은 회귀 검증을 추가한다. 저장소의 실제 규칙을 사용한 녹화 경로의 축자 보존과, 경계 밖 일반 지시문의 치환 유지가 관찰 가능해야 한다. 예상 bytes는 원문/계약에서 얻고 변형 함수를 그대로 복제하지 않는다. 기존 generator API로 충분하면 제품 생성기 코드는 변경하지 않는다. 동기화 정본 문서에는 이 데이터 경계와 이유를 필요한 만큼만 추가한다.

### A3 실제 생성 결과와 양쪽 재생을 검증

공식 생성 전 변경 예정 파일과 현재 dirty를 대조해 쓰기 범위 안인지 확인한다. 범위 밖 drift가 있으면 덮어쓰지 않고 원인을 보고한다. 공식 생성 뒤 corpus 전 파일의 경로/바이트가 정본과 같고 manifest의 모든 원 SHA/recording SHA가 맞아야 한다. 정본 원자료·manifest·역사 verdict 자체는 불변이어야 한다. 저장소의 현재 `.gitattributes`에 따른 clean 변환도 원바이트를 바꾸지 않도록 corpus에 한정한 데이터 속성을 적용하고 생성된 사본에도 반영한다. `git hash-object --no-filters <파일>`과 기본 clean 경로의 object ID 전건 동등성을 확인하되 stage/commit은 하지 않는다. 다른 제품/지시문의 개행 정책은 유지한다.

writing-skills/scripts의 `test_*.py`는 각 파일 직접 실행해 통과한다. 정본과 미러 각각 공식 `run_tests.py structure.test_corpus unit.test_corpus_replay contracts.test_doubles_follow_corpus --jobs 1 --output <새 evidence 경로>`를 순차 실행해 선택과 실제 rows 전건 대응, 실패/오류/skip/미실행 부재, exit 0을 확인한다. 생성기 --check가 성공했다는 이유로 실제 미러 재생을 생략하지 않는다. 검사 중 제품과 시험 정본을 고정하고 전후 소스 해시와 실제 종료 상태를 보존한다.

### A4 인도 판본과 남은 책임을 분리

최종 공식 `build_skill_mirrors.py --check`와 do-math `probe_cli.py --skill-only`를 통과한다. 시험으로 변경된 `.timings.json`만 필요한 경우 공식 생성기로 동기화하고 최종 corpus 바이트 동일성을 확인한다. 수기 미러 수정이나 무관 drift 정리를 하지 않는다.

report에는 phase 003 F2의 해결 범위, 기존/신규 녹화 보존, 현재 source 변화와 규칙의 적용 경계, 양쪽 실제 재생 결과를 적는다. phase 003 A5 중 미러 결함의 후속 근거이며 A2의 Codex 거부와 G7/G8 전체는 여전히 미충족임을 명시한다. 유효한 Claude 실호출/background 증거는 호출 경로 변경이 없으면 재사용한다. manager가 단계별 제품 커밋을 판단할 수 있도록 이번 변경과 이미 존재하던 phase 003 변경을 해시로 구별한다.

## 판단과 경계

phase.json의 writes만 수정한다. `_rules.json`의 기존 축자 복사, corpus에 한정한 `.gitattributes`, 생성기 시험과 동기화 설명, 허용된 공식 생성물과 실행 캐시만 맡는다. 정본 do-math corpus·manifest·schema·worker·adapter·parser·smoke 코드는 읽기 전용이다. 생성기 본문 변경 없이 해결할 수 없다면 확인한 반례와 필요한 위치를 finding으로 반환한다. `.agents/diff/_manifest.json`은 이번 영향 대상이 아니며 확인 없는 --bless를 하지 않는다.

서비스 실행 기록·공용 문서·기존 phase report/evidence는 수정하지 않는다. 자신의 report/evidence는 쓸 수 있다. Git commit/reset/checkout/push·graphify 갱신·패키지/인증 설정 변경·기존 연구 재개/삭제·OS 예약 변경·실제 모델 호출은 이 배정에 없다. manager가 별도 검수와 Git 마감을 맡는다.

검사 묶음은 순차, worker 1로 실행한다. timeout을 추가하지 않으며 도구 yield 만료를 실패로 세지 않는다. 실패 판정이나 범위 밖 변화가 보이면 실패를 보존하고 독립적으로 가능한 작업만 완료한다. 새 규칙을 적용해 전체 관문이나 현재 Codex schema 수락까지 통과했다고 확대하지 않는다.

## 검증 방법

cwd는 `C:\math`, Python은 `C:\Users\wogud\AppData\Local\Programs\Python\Python312\python.exe`다. 최초/최종 입력 SHA와 실행 argv·PID·시각·stdout/stderr·exit를 자신의 evidence에 기록한다.

1. 현재 corpus 양쪽의 전 경로/해시와 규칙을 읽어 A1의 모집단과 실제 두 변형을 확인한다. phase 003의 실패 원출력과 manager verification을 현재 상태와 대조한다.
2. 기존 verbatim 규칙과 작은 회귀 검증·동기화 문서를 수정한다. `& '<Python>' -B .claude/skills/writing-skills/scripts/test_build_skill_mirrors.py` 등 해당 디렉터리의 모든 test_*.py를 각각 직접 실행한다.
3. 생성 예정 변경을 확인한 뒤 `& '<Python>' -B .claude/skills/writing-skills/scripts/build_skill_mirrors.py`로 생성한다. corpus 정본의 전후 SHA 불변과 양쪽 전건 바이트 일치를 확인한다.
4. A3에 지정한 공식 정본 검사와 미러 검사를 새 출력 디렉터리에서 순차 실행한다. 명령의 Python에는 위 실제 경로를 사용하고 `-u -B`를 붙인다. 이미 통과한 관련 검사를 새 변경 이유 없이 반복하지 않는다. 최종 생성 일치와 skill-only도 확인한다.
5. A1~A4와 변경/근거/남김을 report.json에 적고 `& '<Python>' -B services/continuous-development/check.py report 'C:\math' 'C:\math\docs\do-math\continuous-development-2026-10-13' 004 mirror-corpus`를 통과해 제출한다. partial/blocked면 실패한 A와 다음 수리 책임을 정확히 연결한다.
