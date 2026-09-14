# 실제 이의 심사 왕복

참인 자연수 항등식 `n + 0 = n`을 실제 Lean 4.32.0으로 검사했다. 이의 경로를 열기 위한 초기 판단 **2건은 명시적 합성 시험 자료**다. 이후 정리자 1회, 독립 판정자 3회, 원 논리 자리의 답변 1회, 같은 판정자 3회의 **총 8회는 실제 Codex CLI 실행**이다(`gpt-5.6-sol`, `medium`).

세 판정자가 도메인 이의를 기각했고, 원 자리의 답변자는 이의를 철회했다. 같은 세 판정자의 재심 뒤 `decision=match`, `identity_assessment.effective=true`가 기록됐다. 이 사례는 초기 검토까지 실제 모델이 수행한 사례가 아니며, 목표 감사나 일반적인 수학 정확도를 검증한 결과로 확대하지 않는다.

- [result.json](result.json): 실제 호출 수·단계·최종 효력·소요 시간.
- [post-run-audit.json](post-run-audit.json): 실제 재심 입력 3건의 자기 이전 응답 일치, 심사 입력 6건의 같은 회차 동료 결과 비노출, 입력·소스 해시와 Git bundle 대조.
- [actual-cli-invocations.json](actual-cli-invocations.json), `cli/`: 실제 응답·사용량, 원시 JSONL과 CLI 실행 기록. 합성 초기 판단은 `synthetic-initial-*.jsonl`로 구분한다.
- [state.bundle](state.bundle): 원래 Git 상태와 불변 입력·출력·스키마 산출물. 반복된 작업 공간과 `.git` 디렉터리는 별도로 복사하지 않았다.
- [tested-skill.zip](tested-skill.zip), [skill-source-manifest.json](skill-source-manifest.json): 이 실행에서 실제 사용한 고정 스킬 소스와 원래 manifest. zip 내부 경로는 manifest의 상대 경로와 같다.

원 보고·스크립트·manifest는 바이트를 바꾸지 않았다. 그 안의 절대 경로는 당시 실행 좌표다. 이동한 CLI 기록의 대응은 [package-manifest.json](package-manifest.json)에 있다. [verify-package.py](verify-package.py)는 복사 파일과 zip 항목의 크기·SHA-256만 검사하며 모델이나 Lean을 실행하지 않는다.
