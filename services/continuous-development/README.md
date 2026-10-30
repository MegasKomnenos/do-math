# Phase 기반 연속 개발

개발 목표를 구체적인 작업 단위인 **task**로 나누고, 서로의 진행을 기다리지 않고 수행할 수 있는 task들을 **phase** 하나로 묶습니다. task 하나는 `codex exec` 호출 하나로 시작한 **세션** 하나가 수행합니다.

`run.py`는 한 phase의 task 세션들을 병렬 실행하고 모두 종료되면 **manager** 세션을 시작합니다. manager는 프로젝트의 공용 맥락과 계획, 각 task의 결과 보고를 읽고 다음 phase를 작성하거나 최종 검토 뒤 개발 완료를 선언합니다. 실행기는 다음 phase를 반복하며 manager가 `next: null`을 작성하면 끝납니다.

세션은 [protocol.md](protocol.md)의 용어 정의와 절차를 읽고 작업합니다. 공용 **context**는 프로젝트를 판단하는 데 필요한 현재 지식, **plan**은 남은 일과 선행 관계, task별 **objective**는 맡은 목표와 완료 조건입니다. **seam**은 외부 구성 요소 사이에서 제공하고 의존할 동작의 약속이며, **report**는 실제 결과·검증·발견·근거를 다음 manager에게 전달하는 보고서입니다.

Python 3.10 이상과 PATH에서 실행 가능한 Codex CLI가 필요합니다. Python 외부 패키지는 사용하지 않습니다. 모델·인증·권한 정책은 해당 프로젝트의 Codex 환경 설정을 사용합니다. 실행기는 `-C`로 프로젝트 루트를, `--add-dir`로 보고서를 쓸 실행 기록 디렉터리를 전달합니다.

## 구성

- [run.py](run.py): 파견, 대기, 로그 기록, 다음 phase 읽기.
- [check.py](check.py): 세션이 호출하는 phase/report/handoff 검사.
- [protocol.md](protocol.md): 준비·task·manager의 절차와 파일 형식.
- [시작 예제](examples/linecount/): 처리 함수와 CLI를 병렬 구현하도록 준비된 작은 프로젝트와 첫 배정.

수행 규격의 정본은 [protocol.md](protocol.md)입니다.

## 실제 프로젝트 시작

준비 세션에 protocol.md를 읽게 하고 프로젝트의 원래 요구를 전달합니다. 준비 세션은 사용자 요구·완료 기준·위임된 결정을 확인하고 다음을 작성합니다.

```text
records/
  sources/
  settings.json              # 선택: 모든 manager에 적용할 model·effort
  context.md
  plan.md
  seams.md
  phases/001/
    phase.json
    tasks/<task>/objective.md
    tasks/<task>/evidence/
    logs/
```

준비가 끝나면 검사한 뒤 실행합니다. 아래는 저장소 루트에서 실행하는 명령 형식입니다. `PROJECT`, `RECORDS`는 실제 경로로 바꿉니다. 프로젝트와 실행 기록은 별도 디렉터리로 두거나 실행 기록을 프로젝트 하위에 둘 수 있습니다. 실행 기록 안에 프로젝트 자체를 넣지는 않습니다.

```text
python output/continuous-development/check.py phase PROJECT RECORDS 001
python output/continuous-development/run.py PROJECT RECORDS 001
```

실행기는 검사기를 자동 호출하지 않습니다. 첫 명령은 준비 세션이 실행합니다. 그 이후 task와 manager가 각각 자기 검사 명령을 실행합니다.

```text
python output/continuous-development/check.py report PROJECT RECORDS 001 core
python output/continuous-development/check.py handoff PROJECT RECORDS 001
```

handoff는 `RECORDS/phases/001/manager.pending.json`을 읽습니다. 다른 후보 파일은 마지막 인수로 **해당 phase 기준 상대 경로**를 지정할 수 있습니다. 검사 후 manager가 pending 파일을 manager.json으로 이름 바꿉니다. `next`에는 새 phase ID 또는 JSON null을 씁니다.

`run.py`의 처음 세 인수 뒤에 붙인 옵션은 모든 `codex exec` 호출에 그대로 전달합니다. 예를 들어 프로젝트의 쓰기 권한을 CLI에서 지정하려면 `python output/continuous-development/run.py PROJECT RECORDS 001 --sandbox workspace-write`를 사용합니다. 세션이 프로젝트와 실행 기록에 쓸 수 있는 설정이 필요합니다.

## Task와 manager의 모델 설정

manager는 phase.json의 task마다 model·effort를 선택적으로 지정할 수 있습니다. 다음은 task 객체 하나의 예시입니다. 모델 이름과 effort는 사용할 환경에 맞게 정합니다.

```json
{
  "id": "core",
  "inputs": ["repo:src/linecount/contracts.py", "repo:contract_checks/s1.py"],
  "writes": ["src/linecount/core.py", "tests/test_core.py"],
  "provides": ["S1"],
  "uses": [],
  "model": "gpt-6-astra",
  "effort": "medium"
}
```

모든 phase의 manager 설정은 실행 기록 루트의 settings.json에 둡니다.

```json
{
  "manager": {
    "model": "gpt-6-astra",
    "effort": "high"
  }
}
```

각 model·effort는 생략할 수 있습니다. 지정한 항목은 해당 세션에 한해 공통 CLI 옵션보다 우선하고, 생략한 항목은 공통 CLI 옵션과 Codex 기본 설정을 따릅니다. settings.json은 실행 시작 시 한 번 읽으며 파일을 생략하거나 `{"manager": {}}`로 두어도 됩니다. manager에게 모델 선택을 맡길 때는 사용할 모델과 effort 값, 선택 기준을 공용 context에 적습니다.

Codex의 설정 이름과 모델별 effort 지원 범위는 [공식 설정 레퍼런스](https://learn.chatgpt.com/docs/config-file/config-reference)를 참고하세요. 이 도구는 model을 `--model`, effort를 `-c model_reasoning_effort=...`로 전달합니다.

## 예제를 준비하고 실행하기

예제는 아직 구현하지 않은 줄 집계 프로그램입니다. 첫 phase의 core·cli task가 실제 코드를 작성하고, manager가 그 결과에 따라 연결 검증과 review를 배정합니다. 예제 안에 성공 report나 가짜 증거를 미리 넣지 않았습니다.

공유 인터페이스의 [타입 정의](examples/linecount/project/src/linecount/contracts.py)와 [실행 가능한 검사](examples/linecount/project/contract_checks/s1.py)는 준비되어 있습니다. 제공자는 실제 함수로 같은 검사를 실행하고, 소비자는 그 타입 정의에서 만든 테스트 대역을 사용합니다.

저장소 루트에서 새 작업 디렉터리로 복사합니다. 대상은 아직 존재하지 않는 경로를 사용합니다.

```powershell
python -c "import shutil; shutil.copytree('output/continuous-development/examples/linecount', 'workspace/linecount-run')"
git -C workspace/linecount-run/project init
python output/continuous-development/check.py phase workspace/linecount-run/project workspace/linecount-run/records 001
```

실제 Codex 세션들을 실행하려면 다음 명령을 사용합니다. 코드는 복사한 project에, 실행 기록은 records에 남습니다.

```powershell
python output/continuous-development/run.py workspace/linecount-run/project workspace/linecount-run/records 001 --sandbox workspace-write
```

각 세션 로그는 `records/phases/<phase>/logs/`에 있습니다. 결과 정본은 task의 report.json과 phase의 manager.json입니다. 새 세션은 대화를 이어받지 않고 부트스트랩에서 지정한 protocol과 파일들을 읽습니다.

## 동작 범위

프로세스가 종료됐다고 목표를 달성한 것은 아닙니다. 실행기는 반환 코드를 해석하거나 재시도하지 않습니다. task가 nonzero로 종료해도 나머지 task 종료 후 manager가 호출됩니다. manager가 보고와 실제 파일을 읽어 후속 작업을 정합니다.

manager.json이 없거나 JSON을 읽을 수 없으면 일반 Python 오류로 실행이 끝납니다. 파일 부재를 성공 종료로 간주하지 않습니다. 실행 중단 뒤 같은 phase를 다시 지정하면 task들이 다시 실행됩니다. 자동 재개·복구·시간 제한·최대 phase 수는 없습니다.

공용 문서는 task 실행 중 고정하고 manager만 갱신합니다. 같은 S 항목은 그 ID를 유지해 개정합니다. 과거 보고서의 근거 참조는 유지합니다. 형식 검사는 인터페이스의 실제 의미나 자연어 이해를 판정하지 않습니다.

JSON 보고서는 상세 산문을 담을 수 있습니다. task의 narrative는 작업 보고 본문이고, detail·reason·manager의 decision도 여러 문단과 Markdown을 허용합니다. 검사기는 식별자·상태·참조·필수 필드를 검사하며 본문의 길이나 내부 구성을 제한하지 않습니다.

## 개발 검증

```text
python -m unittest discover -s output/continuous-development/tests -v
```

테스트는 가짜 Codex 프로세스로 병렬 실행과 phase 전환을 확인하고, 검사기에 정상·불완전·잘못된 제출물을 입력합니다. 실제 모델 호출 없이 실행할 수 있습니다.

Windows / Python 3.14.3에서 도구 테스트 31개 중 30개가 통과했습니다. 심볼릭 링크 검사는 생성 권한이 없어 1개를 건너뛰었습니다. 모델·effort의 역할별 전달과 우선순위, 상세 산문의 보존, 호출 인자·반환 구조 불일치, Python 최적화 모드에서도 유지되는 seam 검사를 포함합니다.

실제 Codex로 복사한 예제도 실행했습니다. 구현 task 두 개, 연결 검증 task 한 개, 최종 review task 한 개와 각 phase의 manager가 3개 phase를 수행했습니다. 마지막 manager의 `next: null` 뒤 실행기가 종료 코드 0으로 끝났습니다. 생성된 프로그램의 테스트 30개와 S1 검사를 별도로 실행해 통과를 확인했습니다. 이 실행은 모델·effort 기본값을 사용했고, 새 선택 기능의 역할별 인수 전달은 도구 테스트로 확인했습니다.

실제 검증 환경에서는 읽기 전용으로 시작한 첫 시도가 파일 쓰기와 Windows 프로세스 생성 단계에서 실패했습니다. 이후 현재 작업 환경과 같은 `--sandbox danger-full-access -c 'approval_policy="never"'`를 검증용 호출에 명시해 위 전체 실행을 완료했습니다. 실행기가 권한 정책을 자동 변경하는 동작은 없습니다.
