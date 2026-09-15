# 작문 독해 흐름의 구현 검증

`write-for-reader`에 작성 전 합의 등록, 별도 문맥의 독해, 메인의 합의 대조, 현재 판본에 대한 완료 검사를 연결했다. Codex 0.154.0의 실제 `Stop` 훅에서 미검토 작업이 재개되고 취소된 작업은 종료되는 것을 확인했다. 이 호스트의 훅 신뢰 등록도 완료했다.

## 구현과 동작 검사

정본은 `.claude/skills/write-for-reader/`이며 Codex는 생성된 `.agents/skills/write-for-reader/`를 사용한다. 실행기는 UTF-8 본문과 합의·독자 정보를 보존하고, 원고와 독자 정보만 별도 `codex exec`에 제공한다. 독해 원문과 실행 자료를 보존한 뒤 메인이 합의와 대조한다. 독해에 성공했다는 사실만으로 원고를 통과시키지는 않는다.

[동작 검사 29건](unit-tests.txt)이 통과했다. 검사 범위는 입력 변경에 따른 판정 무효화, 전체·표본 독해의 구별, 독해와 판정의 결박, 지적별 처분, 외부 실행 실패, 중단과 늦은 결과의 경합, 세션 식별, 자동 재개 반복 방지, 잘못된 CLI 응답과 제한 시간의 처리다. 이 검사에서 외부 CLI를 대역으로 바꾼 사례는 상태·오류 처분을 확인하며 실제 모델의 독해 품질을 검증하지 않는다.

구현 전에 독해 실행기와 프로젝트 Stop 등록이 없어서 초기 계약 검사 22건이 실패했다. 독립 코드 검토에서 새 독해 실패 뒤 과거 독해를 재사용하는 경로와 실행 UUID가 반복 재개 검사를 초기화하는 경로를 재현했다. 제한 시간에 무한대나 숫자가 아닌 값(NaN)을 입력한 경우와 잘못된 CLI 이벤트를 받은 경우에도 실행 중 상태가 남는 문제가 있었다. 각각의 회귀 실패를 확인한 뒤 수정했다. 루트 세션과 하위 thread의 식별자를 혼동하는 사례도 별도 재현으로 고쳤다.

최종 실행기 SHA-256은 `10d5d1eeca65403ed42c7b224cf52c8140802f835c4f633c09fce5af9b148a53`이다. 정본과 Codex 사본의 코드 바이트가 같으며 미러 생성기의 드리프트 검사를 통과했다. 마지막 실제 원고 독해·판정도 이 판본에서 수행했다.

## 실제 원고 작성과 독해

[합의](inputs/agreement.md), [독자 정보](inputs/audience.md), [최초 사용자 설명](inputs/original-request.txt), [사용자 첨삭 예문](inputs/user-example.md)을 제공하고, 별도 작성자가 수행계획서의 필요성 절을 새로 작성했다. 작성자는 [이전 실패 문단](inputs/previous-section.md)을 읽지 않았다. 입력의 출처는 [원 세션 좌표](inputs/source.json)에 기록했다.

[완성한 원고](practical/draft.md)는 비교 필요성, 정의와 사용 맥락을 확인하는 이유, 문헌 탐색·대조의 부담, 제안된 지원, 작성자의 판단을 연결해 설명한다. 메인은 원고 전문을 합의에 대조했다. 문서 내 의미를 외부 정의로 덮어쓰지 않는 조건과 표현·의미 양쪽의 유사성을 살피는 범위가 유지됐으며, 의미 차이를 일괄 오류로 취급하거나 효과가 입증됐다고 주장하지 않는다.

| 실행 | 실제 관찰과 처분 | 근거 |
|---|---|---|
| 첫 전체 독해 | 기존 에이전트의 범위와 조회 도구·분석 스킬의 역할 연결을 보완했다. | [독해](readings/practical-1/reader.json), [수정 판정](practical/decision-01.json) |
| 수정 뒤 전체 독해 | 독해자가 조회 도구와 분석 스킬의 역할을 정확히 설명했다. 스킬의 구체적 형태와 통제 방식 요구는 원문과 필요성 절의 범위를 근거로 기각했다. | [독해](readings/practical-2/reader.json), [대조](practical/decision-02.json) |
| 최종 코드의 전체 독해 | 원고를 바꾸지 않고 최종 실행 경로를 확인했다. 남은 지적 2건은 원문의 기능 설명과 합의 범위를 근거로 기각하고 원고를 유지했다. | [독해](readings/practical-3/reader.json), [최종 대조](practical/decision-03.json) |

세 독해는 `gpt-5.6-sol/high`로 실행했다. [실전 실행 보고](practical/validation-report.json)와 [최종 상태](practical/final-status.json)에 명령·판본·입력·검토 범위를 보존했다. 최종 원고는 전체 독해와 `accept` 판정에 연결되어 `ready`이며 `completion_problem`은 비어 있다. 이 실전 사례에서는 별도 세션 ID로 상태를 직접 확인했으며 실제 Stop 발화 검증은 아래의 다른 세션에서 수행했다.

기존 두 문서도 각각 독해했다. [이전 실패 문단의 독해](readings/previous/reader.json)는 `difficulties`가 비었지만, 계획서가 학술 문서 작성자에게 제공하려는 도움을 주로 저자의 설명을 오해하지 않게 하는 것으로 재구성했다. 작성자가 기존 학술 개념과의 관계를 검토하는 가치가 충분히 전달됐는지는 합의와 별도로 대조해야 했다. [사용자 첨삭문의 독해](readings/user-example/reader.json)는 세 작업과 활용 목적을 재구성하면서 표현에 관한 지적 4건을 냈다. 이 지적 수만으로 사용자 원고가 더 나쁘다고 판단하지 않았다. 두 문서는 범위와 구성이 다르며 통제된 성능 비교가 아니다. 두 관찰 작업은 원고 채택 없이 종료했다.

이 자료는 한 실전 과제에서 독해 지적에 따른 수정과 근거 있는 기각이 수행된 사례다. 모든 작문 유형이나 독자의 이해, 다른 모델 대비 우위, 재발률 감소를 입증하는 실험은 아니다. HWP 편집·렌더링과 제안 연구 시스템의 실제 성능은 이 검증에 포함하지 않았다.

## 훅 등록과 실제 자동 재개

Windows 명령은 Codex 0.154.0의 실제 `COMSPEC /C`와 raw command 인자 방식으로 실행했다. [명령 검증](hook-command/results.json)에서 저장소 하위 디렉터리의 실행, PowerShell을 거친 stdin JSON 전달, 첫 `block`과 반복 시 `continue:false`를 확인했다. 처음 시도한 Python argv 배열 모사는 Codex와 인용 방식이 달라 명령 문자열을 출력했으므로 해당 실패를 훅 설정 결함으로 판정하지 않았다.

새 `.codex/hooks.json`의 Stop 항목만 공식 app-server의 `hooks/list`와 `config/batchWrite` 경로로 신뢰 등록했다. 이는 이 버전의 `/hooks` TUI가 사용하는 경로다. 등록 직전 정의·경로·해시를 대조하고 등록 뒤 같은 해시에 `trusted`가 반환되는 것을 확인했다. [등록 기록](hook-trust/activation.json)에 전후 상태와 RPC를 보존했다. 신뢰 우회 플래그나 신뢰 DB 직접 편집은 사용하지 않았다.

[실제 Codex 세션](live-stop/summary.json)은 현재 세션 ID로 검증용 원고를 등록한 뒤 `FIRST_STOP_PROBE`로 종료를 시도했다. 훅의 후속 지시를 받은 다음 검증용 작업을 취소하고 `HOOK_CONTINUATION_CONFIRMED`를 반환했다. CLI는 exit 0으로 끝났으며 등록 작업은 `cancelled`였다. 이 과정의 [입력](live-stop/prompt.txt), [CLI 이벤트](live-stop/events.jsonl), [오류 출력](live-stop/stderr.txt)을 보존했다.

`Stop`은 이미 전달한 메시지를 회수하지 않고 후속 지시로 작업을 이어간다. 훅은 등록된 세션의 작업만 검사하므로 작문 스킬과 작업 등록 자체의 누락을 모두 발견하지 못한다. 새 호스트나 훅 정의가 바뀐 환경에서는 다시 신뢰 상태와 실제 발화를 확인해야 한다. 사용자 권한으로 수정할 수 있는 상태 파일을 악의적 조작에 대한 보안 경계로 취급하지 않는다.

## 재현과 자료 보존

저장소 루트에서 다음 명령을 실행한다.

```powershell
python .agents/skills/write-for-reader/scripts/test_writing_flow.py
python .claude/skills/writing-skills/scripts/build_skill_mirrors.py --check
python .agents/skills/skill-creator/scripts/quick_validate.py .claude/skills/write-for-reader
```

실제 독해는 위 입력과 새 작업 폴더를 사용하여 스킬의 `begin/read/decide/status` 순서로 재실행할 수 있다. 새 실행의 모델 응답은 달라질 수 있다. `read`에 필요한 Codex 로그인과 모델 사용 가능 여부를 확인한다. 읽기 전용 모드는 현재 Windows 호스트에서 실제 실행했지만 모든 설치 환경의 호환성을 보장하지 않는다.

[manifest.json](manifest.json)은 복사한 증거 파일의 원래 위치, 바이트 수, SHA-256을 기록한다. 내부 JSON의 절대 경로는 당시 실행 위치를 나타내며, 이 문서의 상대 링크가 저장소 내 보존 자료의 위치다. 증거 파일의 바이트는 Git 텍스트 정규화에서 제외한다.
