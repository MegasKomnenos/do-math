# 전체 회귀 실패 수습 기록

이 디렉터리는 272건 전체 회귀에서 실패한 세 묶음만 다시 검증한 기록이다. 이미 통과한 나머지 테스트는 반복하지 않았다. 최초 전체 회귀 결과는 아래 원문을 수정하지 않고 참조한다.

- 원문: `../verification-20260915-v1/result.json`
- SHA-256: `99b2c6e4a0d7e063169bf2be0ee4bbde3cb680c355be7c3685f5395e07038410`
- 최초 결과: 272건 실행, HTTP fixture 실패 1건, Lean 경로 결손 실패 1건, preflight 지원 자료 경로 결손 오류 14건, 권한상 symlink 검사 skip 1건

## preflight 14건과 formal 1건

원 전체 회귀가 보존한 v1 skill snapshot을 그대로 사용했다. 제품 코드는 고치지 않았다. snapshot 안 `test_preflight.py`가 계산하는 저장소 위치에 루트 지원 자료를 바이트 동일하게 복사하고, 보존 Lean 4.32.0의 `bin`을 PATH 앞에 명시했다.

- 고정 skill source: `../verification-20260915-v1/skill`
- 저장소 지원 source: `C:\math`
- 지원 자료 사본: `docs/`
- Lean bin: `C:\math\.skill-workspace\do-math-toolchains\lean-4.32.0\lean-4.32.0-windows\bin`
- 실행 결과: `runs/preflight-formal-v1/result.json`
- 테스트 로그: `runs/preflight-formal-v1/tests.txt`
- skill manifest: `runs/preflight-formal-v1/manifest.json`
- source·지원 자료 manifest: `runs/preflight-formal-v1/support-manifest.json`
- 결과: 15건 전부 통과

주요 파일 해시는 다음과 같다.

| 파일 | SHA-256 |
|---|---|
| `runs/preflight-formal-v1/result.json` | `7a025406ea92f746e93ea069f22c8145809093ee2e04c60ecffc1ad4a02c8811` |
| `runs/preflight-formal-v1/manifest.json` | `fc29fccdcd3ffed35358e98d82d60efbc9da43133a136b92e88a46bc297f7092` |
| `runs/preflight-formal-v1/support-manifest.json` | `cc4d8acf498a724308eb0a870eee5a9ad74d7d31f69d6b3cee4b8015411574a7` |

`verify_snapshot.py`에는 기존 `--destination`과 `--module`을 유지하고 `--skill-source`, `--repository-support`, `--lean-bin`을 선택 인자로 추가했다. 검증기는 실제 source와 materialized 지원 자료의 경로·해시·크기를 `support-manifest.json`에 기록한다. 현재 스크립트 SHA-256은 `4c920abfca474a3680eadd1291ac406c6e44d715394e9ce9d0bb311ea72e68d3`이다.

## HTTP fixture 수리

실패한 known-failure handler는 POST 본문을 소비하지 않았고 성공 응답 본문의 `Content-Length`도 보내지 않았다. 같은 결함이 있던 실제 이웃 fixture만 함께 고쳤다.

- `test_lifecycle_engine.py`: 실제 loopback GET 응답 길이, 의도적 unknown POST 본문 소비, known-failure POST 본문 소비와 성공 응답 길이
- `test_state_checks.py`: GET 응답 길이와 의도적 unknown POST 본문 소비
- `test_external.py`: POST 본문 소비·응답 길이와 body 없는 redirect의 길이 0
- `test_academic_engine.py`: non-2xx·unknown POST 본문 소비와 non-2xx 응답 길이

의도적으로 `unknown`을 만드는 handler는 요청 본문을 받은 뒤 응답을 보내지 않는 동작을 유지한다. 제품의 외부 행동 코드는 바꾸지 않았다.

- 관련 회귀 결과: `runs/http-fixtures-current/result.json`
- 관련 회귀 로그: `runs/http-fixtures-current/tests.txt`
- 고정 source manifest: `runs/http-fixtures-current/manifest.json`
- source·지원 자료 manifest: `runs/http-fixtures-current/support-manifest.json`
- 결과: lifecycle·state check·external·academic의 관련 11건 전부 통과

known-failure 재시도는 같은 수정 source를 매번 새 snapshot으로 떠서 다섯 번 연속 실행했다. `runs/known-failure-retry-1/`부터 `runs/known-failure-retry-5/`까지 각 디렉터리에 `result.json`, `tests.txt`, `manifest.json`, `support-manifest.json`이 있다. 다섯 결과는 모두 1건 통과이며 각 `result.json`의 SHA-256은 `6e9c9cc82a3e1a88de271f3d65e4ab31b9f4c8a602d0081b8aed0af5cf087ac7`이다.

## 판정

preflight와 formal 실패 묶음은 필요한 지원 자료와 Lean 경로를 snapshot 실행에 제공하지 않은 검증 환경 결손이었다. 같은 v1 source에 그 입력만 명시했을 때 15건이 전부 통과했으므로 제품 코드 결함으로 판정하지 않는다.

known-failure HTTP 실패는 성공 응답을 완결하지 않은 테스트 fixture의 결함이었다. HTTP 메시지를 완결한 뒤 관련 11건과 known-failure 단독 5회가 통과했다. 외부 행동 제품 코드는 수정하지 않았다.
