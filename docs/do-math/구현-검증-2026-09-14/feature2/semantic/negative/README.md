# 실제 초기 검토의 의미 불일치 탐지

실제 Lean 4.32.0으로 참인 명제 `∀ n : Nat, ∃ m : Nat, m = n + 1`을 검사했다. 증인은 각 `n`에 대한 `n + 1`이다. 해설과 요약은 의도적으로 `∃ m, ∀ n, m = n + 1`을 주장하도록 만든 시험 입력이다. 이 오류 표지는 보존용 `case.json`에 두었으며 검토자에게 기대 판정을 제공하지 않았다.

**초기 검토 2건 모두 실제 Codex CLI 실행**이다(`gpt-5.6-sol`, `medium`). 두 검토자 모두 양화 순서의 차이를 `mismatch`로 반환했다. 첫 검토자는 하나의 `m`이 `n=0`과 `n=1`에서 각각 1과 2여야 한다는 반례도 제시했다. 합성 검토 결과는 없다.

K 승인은 생성되지 않았고 `identity_assessment.effective=false`였다. **`organize` 단계 실행 전에 중단**했으므로, 활동은 그 단계의 대기 상태이며 최종 심사를 거친 시스템 전체의 `mismatch` 판정은 아니다. 이 사례는 지정한 부정 예제의 초기 탐지와 승인 차단을 검증한다.

- [result.json](result.json): 두 실제 판정·발견·입력 해시·승인 차단 상태.
- [actual-formal-result.json](actual-formal-result.json): 실제 Lean 소스·선언 시그니처·활성 신뢰 환경의 근거.
- [actual-cli-invocations.json](actual-cli-invocations.json), `cli/`: 실제 응답·사용량, 원시 JSONL과 CLI 실행 기록.
- [state.bundle](state.bundle): 원래 Git 상태와 불변 입력·출력·스키마 산출물. 반복된 작업 공간과 `.git` 디렉터리는 별도로 복사하지 않았다.
- [tested-skill.zip](tested-skill.zip), [skill-source-manifest.json](skill-source-manifest.json): 이 실행에서 실제 사용한 고정 스킬 소스와 원래 manifest. zip 내부 경로는 manifest의 상대 경로와 같다.

원 보고·스크립트·manifest는 바이트를 바꾸지 않았다. 그 안의 절대 경로는 당시 실행 좌표다. 이동한 CLI 기록의 대응은 [package-manifest.json](package-manifest.json)에 있다. [verify-package.py](verify-package.py)는 복사 파일과 zip 항목의 크기·SHA-256만 검사하며 모델이나 Lean을 실행하지 않는다.
