## 목적과 역할

phase 004 mirror-corpus의 A3/F1에 남은 Git manifest 바이트 보존 문제를 닫는다. 기존 verbatim 규칙으로 두 Claude help의 미러 치환은 수리됐고, 정본과 미러의 관련 재생은 각각 14개가 통과했다. 현재 남은 실패는 하위 `scripts/tests/corpus/.gitattributes`가 manifest에 텍스트 변환을 지정하여 Git clean 경로에서 CRLF 바이트가 달라지는 것이다. 이전 배정은 상위 속성만 수정하도록 허용해 실제 수정 위치가 빠졌다. 이번 배정은 그 하위 정본과 공식 생성 사본 두 파일의 쓰기를 명시적으로 허용한다.

G7의 녹화 근거 보존과 G8의 인도 일치에 기여하는 좁은 수리다. Codex 역할 schema의 HTTP 400과 다른 실제 연쇄·문서·최종 전체 관문은 후속 작업이다. 그 실패를 함께 고치거나 실호출로 재조사하지 않는다. phase 004의 history-attributes 원출력과 현재 속성·실제 Git 필터를 대조하며 이미 검토한 생성기나 PR15 전체를 다시 감사하지 않는다.

## 완료 조건

### A1 현재 실패와 재사용할 증거를 결속

시작 시 현재 양쪽 corpus의 전 경로·SHA256, manifest 항목과 명시 SHA 참조를 phase 004 종료 자료와 비교한다. 검수된 시작점은 각각 17항목·44파일·200872바이트, 41개 SHA 참조이며 실제 현재 파일로 확인한다. 소스 해시 목록과 큰 보고서는 프로그램으로 필요한 키를 읽고 전문을 출력하지 않는다. 이전 관리 커밋으로 HEAD가 달라진 것과 제품 바이트 변경을 구별한다.

현재 실패는 정본과 미러 manifest의 raw object ID `db61141dd64a6637124b623410517768fc031fe0`와 clean ID `89d1c078a9cf96b5b9b1c25c9d29484ad9f07fd4`의 차이다. 실제 `git check-attr --all -- <경로>`와 하위 `manifest.json text eol=lf whitespace` 규칙을 확인한다. 같은 파일 해시·속성·Git 환경이면 manager의 수리 전 전건 관찰을 재사용할 수 있다. 다르면 실제 입력과 새 관찰을 구별해 보고한다.

phase 004 F2의 경로 표기 반례는 이미 manager가 9개 argv를 재확인했다. Git 검사는 cwd `C:\math`에서 `/` 상대 경로를 사용하고 실제 argv·cwd·종료 코드를 보존한다. Lean/scheduler는 이 경로에서 바이트가 보존되므로 재작성하지 않는다. 과거 관찰의 정확한 argv를 추측하거나 예전 보고를 고치지 않는다.

### A2 실제 하위 속성으로 manifest 원바이트 보존

정본 corpus/.gitattributes의 manifest text 예외를 제거해 현재 manifest 원바이트가 clean 변환을 받지 않게 한다. phase 004의 미적용 제안은 `manifest.json -text whitespace`이며, 실제 효과를 확인해 적용한다. 기존 녹화의 `** -text -whitespace`, 속성 파일 자체의 텍스트 정책과 corpus 밖 정책은 유지한다. 상위 속성의 무효한 덧씌우기, 녹화별 예외 목록, 새 Git 설정이나 필터는 도입하지 않는다.

공식 생성 전에 예정 변경과 현재 dirty를 대조한다. 생성 미러의 이 속성 파일 하나만 달라져야 하며, 범위 밖 drift가 있으면 덮어쓰지 말고 정확히 보고한다. `build_skill_mirrors.py`로 생성하고 수기 미러 편집이나 확인 없는 `--bless`를 하지 않는다.

수리 후 양쪽 실제 파일 전부에 대해 `git hash-object --no-filters <경로...>`와 `git hash-object <경로...>`의 object ID가 전건 같아야 한다. 각 명령의 stdout 행 수가 경로 수와 같고 중복·누락이 없어야 하며 `check-attr` 원출력을 함께 남긴다. 두 속성 파일 이외의 corpus 파일은 시작 바이트 그대로여야 한다. 양쪽 경로/바이트가 같고 manifest의 항목·원 SHA·recording SHA·verdict는 불변이다. 속성 파일 자체를 포함한 실제 모집단을 사용하며, 두 manifest만 확인하고 전체 보존으로 보고하지 않는다.

### A3 인도와 기존 재생 근거의 유효성을 확인

최종 공식 `build_skill_mirrors.py --check`와 `probe_cli.py --skill-only`를 통과한다. 입력·종료 소스 해시를 대조하여 변화가 허용된 두 속성 파일뿐임을 확인한다. 양쪽 Python 소스 각 864개의 해시와 녹화/manifest 바이트가 phase 004의 공식 보고 및 종료 자료와 같다면 기존 정본/미러 각 14개 통과와 생성기 22개 결과를 재사용한다. 이번 속성만 바뀐 경우 관련 시험·모델 호출·전체 검사를 반복하지 않는다. 재사용 조건이 깨졌다면 영향과 필요한 검증을 finding으로 정확히 반환하며 범위 밖 코드를 수정하지 않는다.

report는 004 A3의 남은 clean 실패를 어떤 새 근거로 해소했는지, 기존 A1/A2/A4와 재생 증거 중 무엇을 재사용했는지 설명한다. 실제 stage/commit/checkout을 수행한 증거라고 확대하지 않는다. manager가 제품 커밋 전에 staged blob의 원바이트와 관련 실패의 잔존 여부를 별도로 검수한다. Codex 거부·G7 전체·G8 최종 review는 여전히 남으며 task complete를 개발 완료로 쓰지 않는다.

## 판단과 경계

writes는 정본 및 생성 사본의 corpus/.gitattributes 두 파일이다. manifest를 포함한 다른 corpus 파일, 상위 .gitattributes, `_rules.json`, 생성기·시험·제품 코드·문서·.timings는 읽기 전용이다. 이번 배정은 phase 004의 실제 쓰기 범위 누락을 해소하며 원래 G1~G8이나 원바이트 의무를 줄이지 않는다.

기존 제품 dirty/untracked와 phase 003~004 report/evidence를 보존한다. 자기 report/evidence만 별도로 쓸 수 있다. 공용 context/plan/seams·engine·다른 task 기록을 수정하지 않는다. Git add/commit/reset/checkout/push, graphify 갱신, 모델 실호출, 패키지·인증 변경, 기존 연구/OS 예약 변경은 수행하지 않는다. manager가 Git 마감을 맡는다.

새 프레임워크나 제품 회귀 시험은 필요하지 않다. 이 변경의 직접 증거는 현재 원파일과 실제 Git 필터 출력이다. 환경 실패나 범위 밖 수리가 필요하면 실패를 보존하고 가능한 부분을 반환한다. 검사 묶음은 순차 실행하며 timeout을 추가하지 않는다.

## 검증 방법

cwd는 `C:\math`, Python은 `C:\Users\wogud\AppData\Local\Programs\Python\Python312\python.exe`다. 각 실행의 argv·cwd·PID·시각·stdout/stderr·실제 종료 코드를 evidence에 남긴다.

1. phase 004 종료 해시·원보고와 현재 파일을 대조하고 A1의 실패 및 재사용 조건을 확인한다. `git --version`, `git check-attr --all -- <슬래시 상대 경로들>`을 기록한다.
2. 정본 하위 속성만 수정한다. 기존 생성기 API/규칙으로 예정 생성 변경이 미러 속성 하나인지 확인한 뒤 `& '<Python>' -B .claude/skills/writing-skills/scripts/build_skill_mirrors.py`를 실행한다.
3. 양쪽 corpus 전건에 대해 A2의 raw/clean 명령을 실행하고 원출력·파일 해시·manifest 참조를 대조한다. Git clean 성공을 원파일 재작성으로 만들지 않았는지 전후 바이트로 확인한다.
4. `& '<Python>' -B .claude/skills/writing-skills/scripts/build_skill_mirrors.py --check`와 `& '<Python>' -u -B .claude/skills/do-math/scripts/probe_cli.py --skill-only`를 실행한다. 기존 22개/양쪽 14개 근거의 소스·입력 불변을 확인하고 실행하지 않은 재검사는 재사용으로 명확히 적는다.
5. A1~A3의 판정과 변경 두 파일·근거·남김을 report.json에 작성한다. `& '<Python>' -B services/continuous-development/check.py report 'C:\math' 'C:\math\docs\do-math\continuous-development-2026-10-13' 005 corpus-git-bytes`를 통과한 뒤 report 경로와 상태를 반환한다.
