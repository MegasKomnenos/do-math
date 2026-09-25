# do-math CLI 운영 안내

초기화의 구조 검사·전체 파일 관측·결과 적용, 정상 정비와 단계별 시간 조회는 [초기화 효율과 정비](references/초기화-효율과-정비.md)를 따른다. 설치 교체 전에는 `quiesce`로 정산하고 실제 종료를 확인한다. 큰 manifest의 등록은 비활성 후보 보존이며 실제 파일 검사는 활성화 기계 작업이 수행한다.

이 스킬은 프리알파이며 현재 판본 하나만 지원한다. 이전 코드·설정·저장 형식과의 호환성이나 마이그레이션을 제공하지 않는다. 계약 변경 뒤에는 새 인스턴스로 실험한다. 개발 시 [AGENTS.md](AGENTS.md)의 원칙을 따른다.

이 문서는 do-math 연구 인스턴스를 만들고 운전하는 사람을 위한 진입점이다. do-math의 목적과 전체 연구 흐름은 [SKILL.md](SKILL.md), 공통 용어의 뜻은 [GLOSSARY.md](GLOSSARY.md), 정확한 명령·필드·상태 투영과 역할별 JSON은 [CLI 실행 계약](references/CLI-실행-계약.md)이 소유한다.

사용자 대화의 선행 읽기와 역할은 SKILL.md의 [진입 절차](SKILL.md#이-문서를-읽는-실행의-역할)를 따른다. 아래 [운전 책임과 실행 구조](#operating-model)를 바탕으로 요청에 맞는 경로를 선택한다.

- [새 연구를 시작하고 인계하기](#start-guide): 인스턴스 준비부터 별도 연구 프로세스의 시작 확인과 보고까지 수행한다.
- [기존 연구 조회·제어](#existing-control): 지정된 인스턴스의 상태를 읽거나 입력·정지·재개 요청의 효과를 확인한다.
- [직접 전진·수동 운전](#manual-run): 해당 절의 적용 조건을 확인한 뒤 허가된 범위를 직접 실행한다.

역할 응답 스키마는 `do-math-cli/5`, 저장 계약은 `do-math-state/5`다. 중앙 실행기, 설치 manifest와 역할별 소비자는 이 판본을 함께 사용하며 다른 판본의 필드를 섞지 않는다.

역할 응답 계약은 후보 준비, 항목별 작업 계약 검토, 연구 계획의 전건 처분, 생산자 선언 편입 묶음과 독립 동일성 검토의 범위 계획을 정의한다. 각 기능이 무엇을 보증하는지는 서로 다르며, 명령 성공·스키마 통과·실행 종료는 형식 타당성·해설 동일성·목표 충족을 대신하지 않는다.

<a id="operating-model"></a>

## 운전 책임과 실행 구조

사용자 대화가 연구 시작 요청을 받았을 때의 작업은 승인된 연구가 실제로 수행될 조건을 마련하고, 독립 실행으로 이어졌는지 확인하는 것이다. 연구 목표는 인스턴스가 계속 소유한다. 대화는 공개 CLI를 통해 사용자의 요청·결정과 실제 환경의 증거를 연결하며, 지금 수행하는 준비·진단·수리가 연구 시작을 어디까지 전진시키는지 판단한다. 운전 중 직접 얻은 증명이나 계산 결과는 그 자체로 초기화·실행·인계의 상태를 바꾸지 않는다.

인스턴스에는 프로세스가 끝난 뒤에도 목표, 권한, 연구 기록과 미완료 의무가 남는다. 기계 실행기는 현재 입력·권한·프로필·자원이 허용하는 요청을 AI 역할이나 기계 작업에 배정하고, 산출을 검사하여 기록과 후속 처리에 연결한다. 요청을 기록한 사실, 실행이 시작된 사실, 결과가 적용된 사실은 각각 그 다음 처리가 어디까지 가능해졌는지를 설명하는 근거다. 프로세스가 없더라도 보존된 의무와 재개 조건이 있을 수 있으며, 프로세스가 살아 있어도 특정 후속 요청이 배정됐다는 뜻은 아니다.

예약 감독은 연구 실행기와 별도 수명으로 동작하면서 현재 상태와 시작 조건을 대조하고, 시작 가능한 연구 실행기를 깨운다. 실제 연구 배정은 실행기가 맡는다. 대화 이후에도 이 연결이 이어지려면 승인된 대화 소실 정책과 유효한 허가, 실제 예약·실행 경로가 갖춰져 있어야 한다. 설치 복구 AI도 보존된 실패 또는 수락된 설치 결함 진단과 정해진 관문에서 열린다. 감독의 존재만으로 미완료 준비나 임의의 오류가 자동 처리되지는 않는다. 정확한 감독·복구 범위는 [독립 운영 계약](계약/독립-운영.md)을 따른다.

따라서 남은 일을 누가 이어받았는지는 그 일을 소유하는 실제 기록과 처리 경로로 판단한다. 오류 응답의 `next_owner`나 보고서의 담당 명칭은 진단상 책임을 가리킬 수 있지만, 후속 요청의 접수·배정·실행을 증명하지는 않는다. 사용자 대화는 현재 상태에서 다음 행동이 무엇에 의해 일어날 수 있는지, 필요한 입력과 권한이 어디에 있는지, 이 대화 이후에도 그 경로가 유지되는지를 근거로 [계속 수행·인계·종료를 판단한다](#handoff-judgment). 주체와 상태의 뜻은 [GLOSSARY.md](GLOSSARY.md)의 공통 정의를 그대로 사용한다.

<a id="start-guide"></a>

## 새 연구를 시작하고 인계하기

이 절은 기본 독립 운영으로 새 연구를 시작하는 절차다. 각 단계의 완료 근거를 확인하고 다음 단계로 간다. 계속 수행과 대화 종료는 [책임·인계 판단 기준](#handoff-judgment)에 따라 판단하고, 확인한 결과는 [5단계](#report-handoff)에서 보고한다.

### 1. 요청과 설정 확정

목표 원문과 사용자 제약을 보존하고, 생성에 필요한 경로·모델·설정을 확정한다. 기존에 승인된 결정은 재사용한다. 사용자만 정할 중요한 결정이 빠져 있으면 해당 항목을 질문하며, 이후 채택 단계에서 확정할 항목과 구별한다.

새 인스턴스는 아래의 기본 운영 구성을 사용한다. 사용자 제약과 실제 실행 환경 때문에 필요한 항목을 변경하고 이유를 기록한다. 모델 상한은 사용할 모든 등급의 작업·운영 모델과 예산 설정에 반영하며, 설치 복구 AI의 모델도 포함한다. 예약 감독과 문헌 조사 도구인 scholarly의 설정 변경은 별도로 판단한다. 문제의 난이도만으로 수동 운영을 선택하지 않는다.

#### 실행 환경과 초기 설정

아래 명령 예시는 Codex 설치 경로인 `.agents/skills/do-math/`를 사용한다. 이 저장소에서 Codex로 운전할 때는 이 경로를 쓴다. 다른 위치에 설치한 경우에는 예시의 스킬 경로를 실제 설치 폴더로 바꾸고, 그 폴더의 문서와 코드를 함께 사용한다.

Windows에서 Python 3.12, Git과 사용할 모델의 CLI를 준비한다. Codex 모델에는 로그인된 Codex CLI, Claude 모델에는 로그인된 Claude CLI가 필요하다. Python 의존성은 `requirements.txt`에 고정돼 있으며 현재 직접 의존성은 `jsonschema==4.26.0`이다.

현재 Windows 구현은 배정된 모델에 따라 `codex exec` 또는 `claude --print`를 호출하고 각 CLI의 기존 로그인을 사용한다. 별도의 API 키를 요구하지 않는다. 두 CLI 모두 모델별 작업·운영 세션 예산과 같은 역할 계약을 따른다.

```powershell
python -m pip install -r .agents/skills/do-math/requirements.txt
codex --version
git --version
python .agents/skills/do-math/scripts/do_math.py profile
```

`profile`은 설치된 Codex CLI의 명령 표면을 조사한다. 종료 코드 0과 `verified=true`는 그 조사 항목이 확인됐다는 뜻이다. 연구 역할의 품질, Lean 설치, 파일 격리나 원격 공급자 상태까지 보증하지 않는다.

Claude를 사용할 때에는 `claude auth status`로 로그인 상태를 확인하고 `python .agents/skills/do-math/scripts/do_math.py profile --provider claude`로 필요한 명령 표면을 검사한다. CLI는 `PATH`에서 찾으며 `CLAUDE_CONFIG_DIR`로 지정한 로그인 설정 위치도 전달한다. API 키나 별도 API 공급자로 자동 전환하지 않는다. Claude의 `--bare` 모드는 구독 로그인을 사용하지 않으므로 이 실행 경로에서는 사용하지 않는다.

형식 검사에는 Lean이 필요하다. `setup_lean.py`는 이 머신의 인스턴스들이 함께 쓰는 Lean 4.32.0 툴체인과, 같은 판본의 Mathlib 태그에 고정한 Lake 프로젝트를 저장소 루트의 `.skill-workspace/do-math-toolchains/`에 준비한다.

```powershell
python .agents/skills/do-math/scripts/setup_lean.py
```

툴체인이 없으면 Lean 배포본을 내려받고, Mathlib을 복제한 뒤 미리 빌드된 캐시를 받는다. 수 GB의 디스크와 네트워크를 사용하며, 이미 끝난 단계는 다시 실행해도 건너뛴다. 마지막에 검사기가 실제로 쓸 명령으로 `import Mathlib` 파일을 컴파일하고, 성공했을 때에만 준비 표지를 남기고 그 명령을 JSON의 `lean_command`로 출력한다. 컴파일이 끝날 때까지 기다리며 실행 시간으로 중단하지 않는다. 컴파일이 실패하면 표지를 지우고 종료 코드 1로 끝나며, 이때 실행기는 이 프로젝트를 선택하지 않는다.

준비 표지가 있으면 `lean_command`를 생략한 인스턴스는 이 프로젝트를 거쳐 Lean을 실행하므로 제출 소스에서 Mathlib을 import할 수 있다. 설정에 명시한 `lean_command`는 언제나 이 탐색보다 우선한다. 준비 전과 후에는 탐색되는 명령이 다르므로 검사 결과에 기록되는 toolchain도 달라진다.

사전 빌드 캐시를 사용할 수 있으며 클린 빌드는 요구하지 않는다. 준비 완료 출력에는 등록에 사용할 완전한 `toolchain`과 실제 환경 검사의 `validation` 참조가 들어간다. 검사 원문·명령·출력·종료 코드·검사 전후 도구 정보는 `.skill-workspace/do-math-toolchains/validation/`의 고유 디렉터리에 보존한다. `validation.status=verified`는 Mathlib import와 대표 증명 검사의 통과를 뜻하며 전체 라이브러리 재검증을 뜻하지 않는다. 이미 설치된 환경은 `setup_lean.py --inspect-only`로 도구 정보만 관측할 수 있으며, 별도 명령은 `--command-file`로 지정한다. 이 관측은 실행 파일과 프로젝트의 식별이며 환경 검사나 채택은 아니다. 실제 등록과 증거의 결합은 [초기화 운전](references/초기화-운전.md)을 따른다.

이미 설치한 환경은 다음 명령으로 다운로드 없이 검사하고 등록용 검증 참조를 얻는다. `--evidence-dir`는 선택 사항이며 증거를 둘 상위 경로를 바꾼다. 환경의 소스·빌드 디렉터리 밖을 사용한다.

```powershell
python .agents/skills/do-math/scripts/setup_lean.py --verify-only
```

명시적인 명령은 `--command-file`로 지정할 수 있다. 이 검사는 신뢰 환경 등록·사용자 채택을 자동 수행하지 않는다. 실제 파일·판본·검증 증거의 결합은 [초기화 운전](references/초기화-운전.md)을 따른다.

연구를 시작하기 전에 다음 경로를 정한다.

- `--repository`: 인스턴스의 권위 있는 상태와 산출 묶음을 저장할 Git 저장소다. `--create-repository`를 쓰려면 경로가 없거나 빈 디렉터리여야 한다.
- `--workspace`: 실행별 작업 공간, 제어 inbox와 복구 자료를 둘 로컬 경로다. Git 정본과 다른 역할을 하며, 작업 공간 파일만으로 공용 기록이 되지는 않는다.
- `--goal` 또는 `--goal-file`: 연구 헌장의 현재 목표가 될 원문이다. 둘 중 하나만 사용한다.
- 목표는 수학적 질문이다. 형식 결과·동일성 판정·목표 감사를 거쳐 `mathematically_solved`를 판단한다. 그 목표를 위한 문헌 조사·계산·비형식 과제도 사용할 수 있다.

초기화 때 정책, 원자료와 설정을 함께 넣을 수 있다. `--source`는 여러 번 지정할 수 있다. `--effort`는 설정 파일의 추론 노력보다 우선하며, 생략한 필드는 코드의 기본값을 사용한다.

관찰 설정의 `tool_review_window_seconds`와 `self_check_response_window_seconds`에는 제품 기본값이 없다. 프로필을 채택하기 전에 사용할 두 값을 확정하여 `init --config-file`이나 `configure --config-file`로 전달한다. 이미 승인된 설정에 있으면 그대로 사용한다. 주기·사건 관찰에는 도구 검토 window와 관찰 주기가 필요하고, 연구 수행에는 자기 점검 응답 window도 필요하다. 누락되거나 유효하지 않은 값은 역할·프로필 ID·필드와 함께 반환되며 연구 활성화가 완료되지 않는다. 구체적인 설정 보충과 프로필 재조회는 [초기화 운전](references/초기화-운전.md)의 1단계와 4단계를 따른다.

모델 대응·역할별 최소 등급·모델별 동시 세션 예산은 설정 파일의 `tier_models`, `role_tiers`, `session_limits`로 정한다. 구체적인 설정은 아래 「모델과 동시실행 예산 설정」을 따른다.

독립 운영의 기본값은 `operator_enabled=true`, `operator_interval_seconds=7200`이다. 새 인스턴스는 상·중·하 모델마다 운영 3개와 작업 3개의 동시 세션을 사용한다. [모델과 실행예산](references/모델과-실행예산.md)의 기본 대응과 배정 기준을 확인하고, 다른 용량이나 수동 운영이 필요하면 설정 파일에 지정한다. `init`은 독립 운영이 활성일 때 정상 감독과 연구 엔진을 맡는 두 숨김 Windows 예약 작업을 등록하며, 그 자체로 모델이나 연구 실행을 시작하지는 않는다. 첫 정기 감독은 등록 후 설정한 주기에 도래한다. 정상 감독은 저장 상태와 예약 상태를 모델 없이 검사하고 필요할 때 연구 엔진 작업만 요청한다. 연구 작업에는 고정 반복 주기를 두지 않는다. 엔진을 읽을 수 없는 실제 실패가 보존됐거나 운영 점검의 설치 결함 진단이 수락됐을 때 별도 설치 복구 AI 경로를 열 수 있다.

scholarly는 기본 활성이다. `scholarly_server`에 `command`·`args`를 직접 지정하거나, 초기화 명령의 작업 위치에서 상위로 찾은 `.codex/config.toml`의 scholarly 항목을 사용한다. 프로젝트 설정이 없으면 Codex 사용자 설정에서 같은 항목을 찾는다. 실행에 필요한 서버 경로는 고정해 인스턴스 설정에 보존하고, 하위 실행에는 이 MCP 설정만 명시적으로 전달한다. 서버 설정을 찾지 못한 것과 외부 자료원 접근 실패는 다르다. 사용 가능한 도구는 각 실행에서 확인한다.

#### 모델과 동시실행 예산 설정

모델의 기본 대응과 배정 기준은 [모델과 실행예산](references/모델과-실행예산.md)에 있다. 아래 JSON을 설정 파일로 저장해 `init --config-file` 또는 `configure --config-file`에 전달하면 모델별 동시 세션 수를 명시할 수 있다. 과제의 난이도·중요도에 맞춘 모델의 슬롯이 없으면 그 과제는 대기한다.

```json
{
  "tier_models": {"high": "gpt-6-astra", "medium": "gpt-5.6-sol", "low": "gpt-5.6-terra"},
  "session_limits": {
    "work": {"gpt-6-astra": 3, "gpt-5.6-sol": 3, "gpt-5.6-terra": 3},
    "operations": {"gpt-6-astra": 3, "gpt-5.6-sol": 3, "gpt-5.6-terra": 3}
  }
}
```

이 예시는 기본 구성과 같다. 세션은 종료 후 재사용하며 작업·운영 예산은 자동 차용하지 않는다. 모델 이름이나 수를 바꾸면 두 예산 맵에도 해당 모델을 명시한다.

Claude를 배정하려면 `claude:opus`, `claude:sonnet`, `claude:haiku`처럼 `claude:` 뒤에 CLI 모델 이름이나 별칭을 적는다. `claude-`로 시작하는 전체 모델 ID도 사용할 수 있다. 다른 이름은 Codex로 전달한다. 같은 등급·모델 선택 규칙을 연구·검토·운영 역할에 적용한다. 정상 예약 감독은 모델 슬롯을 쓰지 않으며, 엔진 실패 뒤 허용된 live 설치 수리를 수행하는 복구 AI만 배정된 운영 슬롯을 사용한다.

[Claude·Codex 혼합 설정 예시](examples/claude-codex-sessions.json)는 상 등급에 `claude:opus`, 중 등급에 `gpt-5.6-sol`, 하 등급에 `claude:haiku`를 배정하고 각 모델의 작업·운영 슬롯을 각각 3개로 둔다. `init --config-file`이나 `configure --config-file`에 이 파일을 전달할 수 있다. 예시를 적용할 때에만 해당 모델과 용량을 사용하며 기본값은 위 Codex 구성이다. 각 등급에는 모델 하나를 지정한다. 모델별 예산의 식별자는 설정 문자열이므로 `tier_models`와 두 예산 맵의 표기를 일치시키고, 같은 모델을 별칭과 전체 ID로 중복 등록하지 않는다.

두 CLI를 함께 쓸 때 공통 `effort`에는 `low`, `medium`, `high`, `xhigh`를 사용할 수 있다. Claude의 `operator_effort`는 이 값들과 `max`를 지원하며 `minimal`·`ultra`는 지원하지 않는다. 지원하지 않는 노력 수준이나 사용할 수 없는 모델로 호출하면 실패로 기록하고 자동으로 다른 모델이나 수준을 선택하지 않는다. Claude 별칭은 CLI가 현재 제공하는 모델로 해석하므로 판본을 고정하려면 사용 가능한 전체 ID를 지정한다.

### 2. 인스턴스 생성

아래 예시는 새 Git 저장소와 작업 공간을 만들고 수학 목표를 시작한다. PowerShell에서 현재 디렉터리는 저장소 루트라고 가정한다.

```powershell
python .agents/skills/do-math/scripts/do_math.py init `
  --create-repository `
  --repository .skill-workspace/my-math/repo `
  --workspace .skill-workspace/my-math/work `
  --goal-file .agents/skills/do-math/examples/nat-add-zero.txt `
  --title "자연수 덧셈의 오른쪽 항등원" `
  --effort medium
```

성공 응답의 `result`에 `instance_id`, 첫 `snapshot`, CLI `status`가 들어 있다. 이후 명령의 `--instance`에는 `result.instance_id`를 넣고 같은 `--repository`를 사용한다. 생성 성공은 초기화 완료가 아니다. 다음 예시는 초기화 결과를 담은 응답 봉투다.

```json
{"schema_version":5,"response_contract":"do-math-cli/5","request_id":"QR-...","command":"init","exit_code":0,"result":{"instance_id":"RI-...","snapshot":"<git-oid>","status":"initializing"}}
```

독립 운영을 등록했으면 응답의 `result.operator_schedule`에서 실제 두 작업을 확인한다. 저장은 성공했지만 예약 등록이 실패하면 생성된 인스턴스 ID·snapshot과 실패·재조정 명령을 반환한다. 같은 연구를 다시 `init`하지 말고 해당 인스턴스의 설치 문제를 해결한다.

이 단계의 완료 근거는 보존된 인스턴스 ID·snapshot과 실제 예약 등록 결과다. 연구의 활성화는 다음 단계에서 확인한다.

<a id="activate-instance"></a>

### 3. 초기화 완료

`init`은 입력 문자열의 코드 포인트열과 그 UTF-8 바이트 해시·크기를 `immutable_input.text/sha256/bytes`에 한 번만 보존하고 설정·초기 source를 고정한다. 이름과 원문을 정규화하거나 별도 원문 사본으로 바꾸지 않는다. 첫 commit에는 실행 grant나 연구 queue가 없다. 이후 [초기화 운전](references/초기화-운전.md)의 공개 명령과 요청 예시를 순서대로 따른다. 그 문서는 통치·권한 채택, 실제 프로필 참조 조회, 능력 증거, 신뢰 환경과 최초 의도 해석·검사·적용을 설명한다. 이미 채택한 기본값은 같은 승인 근거를 재사용한다.

초기화의 독립 검사와 실제 적용, 현재 능력·신뢰·용량·복구 관문이 모두 충족된 경우에만 연구가 활성화된다. 초기화 운전의 마지막 절에 따라 현재 인스턴스의 승인 원문, 독립 검사와 수입 적용 기록을 확인한다. 미완료 관문을 내부 함수 호출이나 저장 파일 편집으로 우회하지 않는다.

독립 인계에는 `conversation_loss_policy=continue_authorized`가 승인·적용되어 있는지도 확인한다. 이 정책에서는 대화의 attach·heartbeat 없이 허가된 연구를 계속할 수 있다. 초기화 관문은 `pause` 정책도 허용하므로, 활성화만으로 대화 종료 후의 지속 실행을 보장하지 않는다. 기존 승인 근거를 재사용하고, 다른 정책이 승인되어 있으면 그 결정을 임의로 바꾸지 않는다. 새 사용자 결정이 필요한 경우에는 그 조건의 영향과 대기 범위를 명시한다. 사용자 정지·HOLD·허가 만료와 철회는 계속 적용된다.

초기화 관문 전건과 실제 적용 기록, 독립 인계의 정책 조건을 확인하면 [4단계](#start-engine)로 간다. 수동 운영으로 정한 인스턴스는 [직접 전진·수동 운전](#manual-run)으로 이어 간다.

<a id="start-engine"></a>

### 4. 독립 실행 시작과 관측

먼저 `operator status`와 `status --json`으로 대상 인스턴스의 예약 작업과 연구 상태를 읽는다. 같은 인스턴스의 연구 프로세스가 이미 실행 중이면 그 실행을 확인한다. 실행 중이 아니고 시작 조건이 충족되면 다음 명령으로 별도 연구 예약 작업을 시작한다.

```powershell
python .agents/skills/do-math/scripts/do_math.py operator start `
  --repository .skill-workspace/my-math/repo --instance RI-...
```

Windows 로그인, 켜져 있고 절전하지 않는 PC, 네트워크와 배정된 모델 CLI의 유효한 인증이 필요하다. 화면 잠금과 로그아웃은 다르다. 놓친 예약은 실행 가능한 상태에서 처리하도록 등록한다. 연구 실행의 내부 관찰·점검과 `operator_interval_seconds`의 주기(기본 2시간)마다 수행하는 모델 없는 예약 감독은 별도로 유지된다. 감독은 HOLD·정지·종결·완료·모델 정책 위반과 엔진 작업 상태를 읽고, 실행 가능할 때 엔진 작업을 요청한다.

`operator start-operator`는 별도 정상 감독 작업을 즉시 요청한다. 정상 감독은 모델을 호출하지 않으며, 실패 시 설치 복구 AI가 열리는 조건은 [독립 운영 계약](계약/독립-운영.md)을 따른다.

시작 요청 뒤 다음 관측을 수행한다. 시작 관측 구간은 30초로 두고, 그 안에 필요한 근거를 얻으면 보고 단계로 간다. 이 구간은 대화의 시작 확인 범위이며, 연구 프로세스나 계산을 종료하는 시간 제한이 아니다.

1. 명령의 반환 내용을 확인한다. `operator start`는 시작 조건이 충족되지 않으면 `held`, `paused`, `not_started` 등의 결과와 종료 코드 0을 반환할 수 있다. 예약 시작 요청이 수행된 반환과 조건에 따른 비시작 반환을 구별한다.
2. `operator status`로 연구·감독 작업을 조회한다. 감독의 등록·활성 상태·주기·다음 실행 시각을 확인한다. 연구 작업의 `Running` 상태는 bootstrap 실행도 포함하므로, 대상 저장소와 인스턴스 ID의 실제 연구 명령이 실행 중인지 호스트 프로세스 정보와 대조한다.
3. `status --json`으로 사용자 정지·대기 이유·현재 연구 상태를 읽는다. 호스트 관측과 저장 상태는 관측 시각이 다르므로 각각의 시각을 남긴다. AI 작업이 아직 배정되지 않았다는 사실만으로 연구 실행기의 시작을 부정하지 않는다.

```powershell
python .agents/skills/do-math/scripts/do_math.py operator status `
  --repository .skill-workspace/my-math/repo --instance RI-...
python .agents/skills/do-math/scripts/do_math.py status `
  --repository .skill-workspace/my-math/repo --instance RI-... --json
```

Windows에서는 `Get-CimInstance Win32_Process`의 `ProcessId`, `ParentProcessId`, `CommandLine`으로 대상 인스턴스의 프로세스를 대조할 수 있다. 연구 예약 작업은 bootstrap을 거쳐 `do_math.py run --repository <대상 저장소> --instance <대상 ID> --watch`를 실행한다. 이미 실행 중이던 같은 인스턴스의 프로세스는 현재 관측으로 확인하고, 종료된 과거 실행 기록을 새로운 시작의 근거로 쓰지 않는다.

시작 조건을 통과한 실행의 기록은 `<workspace>/operator/engine/<실행 디렉터리>/`에 있다. `result.json`의 `outcome=running`은 자식 프로세스 생성 전에 기록되므로 단독 시작 증거가 아니다. 이후 실행·종료 결과는 해당 디렉터리와 `<workspace>/operator/latest-engine.json`에 보존된다. 시작 조건에 따른 정상 비시작 반환에서는 두 기록이 새로 생성되지 않을 수 있고, 시작 조건 조회의 예외는 `latest-engine.json`에만 기록될 수 있다. 새 기록의 부재만으로 성공이나 실패를 추측하지 않는다.

관측 전에 실행이 끝났으면 이번 시작에 대응하는 종료 기록과 현재 연구 상태를 읽는다. 종료 코드 0이나 `outcome=completed`는 프로세스 종료 사실이며 수학적 목표 완료를 뜻하지 않는다. [보고 단계](#report-handoff)에서 관측한 상태를 구별한다.

<a id="report-handoff"></a>

### 5. 인계 결과 보고

<a id="handoff-judgment"></a>

#### 계속 수행·인계·종료의 판단 기준

이번 대화의 성과는 승인된 연구의 준비·실행·후속 처리가 실제로 어디까지 연결됐는지로 판단한다. 계속할 작업의 가치는 현재 권한 안에서 무엇을 확인하거나 바꿀 수 있고, 그것이 시작을 막는 조건이나 불확실성을 어떻게 해소하는지에 있다. 실패 횟수나 같은 명령의 반복 자체는 복구 가능성 또는 불가능성의 근거가 아니다. 아직 확인하지 못한 사항과 실제로 확인한 차단 조건을 구별한다.

인계 판단에는 남은 의무의 대상과 수신 주체, 그 주체가 읽을 보존 자료, 실제 요청·배정의 상태, 현재 또는 재개 조건 충족 뒤 작동할 실행 경로가 함께 필요하다. 이 근거로 준비 중인 인계, 접수된 후속, 실행 중인 처리와 미배정 의무를 구별한다. 인계가 성립했다고 설명하려면 이 대화가 끝나도 누가 어떤 조건과 근거로 남은 일을 처리할 수 있는지 밝혀져 있어야 한다. 최초 연구 시작의 인계 완료는 앞 단계에서 확인한 초기화·정책·예약 조건과 실제 연구 실행을 근거로 한다.

대화를 마치는 판단은 남은 의무가 어떻게 보존되고 처리될지 설명할 수 있어야 한다. 추가 작업을 이 대화에서 수행할 수 있는 범위, 이미 이어진 처리 경로, 사용자 결정이나 외부 입력에 의존하는 범위를 함께 평가한다. 실제 수신이나 실행 경로가 확인되지 않은 의무는 미인계로 남긴다. 대기와 관측 불확실성을 설명하는 일은 이미 승인된 독립 작업까지 중단할 이유가 되지 않는다. 사용자 정지와 권한 경계는 이 판단에 계속 적용된다.

#### 시작 요청의 결과를 전달한다

최종 보고는 독립 실행 인계의 결과와 현재 연구 상태, 남은 의무를 먼저 설명한다. 시작을 확인하지 못했거나 초기화가 미완료인 범위도 이 중심 결과에 포함한다. 이어 인스턴스 ID와 저장소·작업 공간, 적용한 모델 제한, 시작 관측 시각과 근거, 감독 상태·주기, 실제 후속 담당과 재개 조건, 조회 방법을 제시한다. 관측하지 못한 값과 아직 배정되지 않은 담당은 그 사실대로 적는다.

이번 프로세스의 종료 상태와 연구 목표의 해결 상태는 각 근거로 보고한다. 수학적 목표 완료는 목표 감사와 적용되는 학술 요구의 근거를 확인한다. 운전 과정에서 별도로 얻은 증명·계산·Lean 검사 결과는 확인 범위를 밝힌 부수 결과로 전달한다. 그러한 결과의 획득을 이유로 시작 요청의 성과나 남은 운전 책임을 바꾸지 않는다. 사용자에게 전달할 중심 결과가 수학 풀이로 옮겨가지 않도록 보고의 분량과 순서도 이 목적에 맞춘다.

<a id="existing-control"></a>

## 기존 연구 조회·제어

사용자가 지정했거나 현재 대화에서 식별된 인스턴스의 저장소와 ID를 사용한다. 조회는 아래 절차를, 변경 요청은 [입력과 결정](#입력과-결정을-제공하는-법), [정지·재개·종결](#정지-재개와-종결), [운영 제어 명령](#운영-제어-명령의-용도)의 해당 절차를 따른다. 제어 요청은 접수와 실제 적용을 구별하고 효과를 확인한다.

### 현재 상태를 읽는다

```powershell
python .agents/skills/do-math/scripts/do_math.py status `
  --repository .skill-workspace/my-math/repo `
  --instance RI-...
```

사람용 출력은 목표, 목표 상태, CLI 상태와 snapshot, 모델별 작업·운영 세션 점유, 과제 상태·`assessment_pending`·보존된 `dispatch_waits` 사유와 보증 범위 요지를 보여 준다. 자동 처리나 세부 진단에는 `--json`을 쓴다.

```powershell
python .agents/skills/do-math/scripts/do_math.py status `
  --repository .skill-workspace/my-math/repo `
  --instance RI-... `
  --json
```

JSON status에서 먼저 볼 필드는 다음과 같다.

| 필드 | 운영에서 읽는 뜻 |
|---|---|
| `snapshot` | 이번 상태가 고정된 Git commit OID |
| `status` | 실행 루프의 현재 CLI 상태 |
| `goal_status` | 현재 목표 감사 근거에 대한 CLI 목표 상태 |
| `pending_actions` | 실행기가 아직 처리하지 않은 action 수 |
| `tasks` | 과제 ID·제목·현재 CLI 단계 |
| `knowledge` | 현재 사용 가능한 `K` 수와 `formal_results`, `expositions`, `identity_assessments`의 기록 수. 기록 수를 성공 판정 수로 읽지 않는다 |
| `questions` | 사용자 입력이나 결정을 기다리는 질문 |
| `budget` | 작업·운영 모델별 동시 세션 한도·점유·여유 |
| `pending_controls` | inbox에 접수됐지만 아직 적용되지 않은 제어 수 |
| `user_pause` | 명시적 사용자 재개를 기다리는 정지의 요청 ID·이유·시각 |
| `waiting_actions` | 해소되지 않은 행동의 역할·대상·실패 종류·이유·실행 ID 요지 |
| `external_operations` | 외부 HTTP operation의 원장 상태 |
| `active_trust_environment` | 현재 CLI가 활성으로 기록한 신뢰 환경 ID |
| `academic_validation` | 현재 해결 근거와 학술 요구에 상대적인 후속 상태 |
| `assurance` | 읽기·공급자·사용량·형식·검토에 관해 실제 제공하는 보증의 범위 |

수량과 상태 문자열만으로 수학적 결론을 판단하지 않는다. 필요한 기록은 `query`와 `read`로 정확한 snapshot에서 확인한다.

<a id="manual-run"></a>

## 직접 전진·수동 운전

이 절은 독립 운영을 끈 인스턴스를 수동으로 운전할 때, 또는 `operator status`와 `status`로 예약 연구 작업이 실행 중이 아님을 확인한 뒤 허가된 범위를 정해 직접 전진시킬 때 사용한다. 초기화 중 제한 실행은 [초기화 운전](references/초기화-운전.md)이 지정한 단계와 적용 결과를 따른다.

독립 운영이 활성인 인스턴스의 지속 연구는 [독립 실행 절차](#start-engine)가 확인한 연구 예약 작업이 맡는다. 사용자 대화는 그 예약 작업이 실행 중일 때 `run`을 함께 실행하지 않는다. 대화가 `run --watch`를 붙잡으면 연구 진행이 대화의 수명에 묶이고, 뒤에 시작한 예약 작업은 writer lock을 얻지 못해 실패로 끝난다.

`run`에는 전체 실행 시간 제한이 없다. 실행기는 현재 권한·입력·자원이 허용하는 연구와 검토를 배정하고 결과를 회수한다. 작업 예산 AI와 이미 시작한 Lean 계산은 경과 시간만으로 종료하지 않는다. 운영 예산 AI에는 `call_timeout_seconds`가 정하는 개별 호출 기한을 적용한다. 중앙의 일반 형식 검사와 신뢰 환경 전환 검사는 두 종류의 동시 실행 수를 합해 인스턴스당 최대 한 건으로 제한한다. 사용자 정지·종결·권한 회수·필수 전제 변경과 수락된 운영 처분은 해당 실행의 종료·회수 경로를 따른다.

### 정해진 수만큼 전진시킨다

```powershell
python .agents/skills/do-math/scripts/do_math.py run `
  --repository .skill-workspace/my-math/repo `
  --instance RI-... `
  --max-steps 5
```

`--max-steps`는 이번 `run` 호출이 처리할 action 수의 상한이다. 수학 연구 단계나 모델 호출 수와 항상 같지는 않는다. 형식 검사·외부 행동 같은 기계 action도 한 step으로 처리될 수 있고, 하나의 AI 실행 안에서 모델 CLI가 수행한 내부 동작 수를 세지 않는다.

`--max-steps`는 새 action 시작 수의 상한이며 이미 시작한 실행을 시간으로 끊지 않는다. 생략하면 실행기는 queue와 현재 설정이 허용하는 동안 진행한다. `--watch`를 함께 쓰면 CLI 상태가 `waiting`이어도 제어 inbox, 대화 lease와 관찰 사건을 계속 확인한다. 사용자 정지·종결·목표 완료 또는 지정한 시작 수에 따른 회수가 끝나면 반환한다. 사용자 결정을 자동으로 만들거나 waiting 과제의 조건을 임의로 해소하지 않는다.

```powershell
python .agents/skills/do-math/scripts/do_math.py run `
  --repository .skill-workspace/my-math/repo `
  --instance RI-... `
  --watch
```

### 반환 상태를 다시 확인한다

`run`은 마지막 status JSON을 반환한다. 다음 경우에는 세부 기록을 읽고 다음 행동을 정한다.

- `ready`: 처리할 action이 남았거나 다음 `run`에서 계속할 수 있다.
- `waiting`: `questions`, 대기 과제 또는 외부 사건을 확인한다. 입력·결정 없이 같은 `run`을 반복해도 조건이 바뀌지 않는다.
- `capacity_waiting`: 배정된 모델의 세션 슬롯을 기다린다. 같은 인스턴스의 점유와 설정을 확인하고, 반환 뒤 `run` 또는 `run --watch`로 이어간다.
- `paused`: 사용자 정지, 실행기 복구, 설치 문서 변경이나 인스턴스 전체의 중단 사유를 확인한다. `resume` 전에 `check`, status의 questions와 최근 실행 기록을 읽는다. 개별 실행의 실패는 해당 요청을 보류하고 운영 점검으로 연결하며, 독립 작업은 계속한다.
- `completed`: 현재 CLI가 목표와 적용되는 학술 요구의 완료 조건을 충족했다고 계산한 상태다. 정확한 목표 감사, K·해설·동일성 판정과 학술 근거를 별도로 읽는다.
- `closed`: 사용자가 인스턴스를 종결했다. `resume`으로 다시 열 수 없다.

## 역할 산출과 실패 처리

모든 내부 작업자에게 실행별 주 JSON·확장 스키마, 고정 입력과 `submission_contract.command`를 제공한다. 작업자는 스키마를 만족하는 완전한 JSON 값 하나를 최종 응답으로 반환한다. 중앙은 정상 완료한 native stream의 정확한 최종 바이트와 로컬 종료 뒤 작업 공간 산출을 같은 접수 절차로 포착해 검사·봉인한다. 실행 중 결과를 먼저 봉인하려면 `.scratch/submission.json` 같은 초안 경로를 `--submit` 또는 `submit_draft`에 넘길 수 있다. 이 명시 제출은 선택적 조기 전달이며, 이미 접수된 봉인 후보가 있으면 뒤의 다른 최종 응답으로 대체하지 않는다. 명령의 무옵션 로컬 검사와 preview도 오류를 미리 찾는 선택적 진단이며, 그 결과를 최종 접수 증거로 제출하지 않는다. `.scratch/`와 그 아래 `.scratch/.execution-temp/`는 버릴 중간 파일용이며 산출·근거로 수집하지 않는다. 검사 범위, 파일 한도와 정확한 제출 절차는 [공통 실행](references/공통-실행.md)을 따른다. 검사 통과나 정상 CLI 완료는 수학적 승인, 과제 완료 또는 수신 시점의 현재성 승인이 아니다.

신규·개정 후보에는 모델 평가가 하나씩 있어야 한다. 기존 미평가 과제는 평가를 보충하고, 학술 과제는 관찰 규칙도 준비한 뒤 독립 계약 검토를 받는다. 필요한 입력이 없으면 해당 보충을 보류한다. 평가와 규칙을 같은 실행에 배정할 수 있지만 사용자 질문·범위·완료 의무는 바꾸지 않는다. 구체적인 반환과 재개 조건은 [후보 준비 계약](계약/후보-준비.md)의 기존 과제 보충 절과 [모델과 실행예산](references/모델과-실행예산.md)을 따른다.

출력 수리나 진단 후 재시도까지 실패한 요청은 원 출력·오류·체크포인트와 함께 보류한다. 일반 `resume`은 이를 다시 실행하지 않는다. 연구가 활성화된 인스턴스에서는 실제 원인을 수리한 뒤 `request --role operational_review --target EX-...`로 해당 실패 실행의 진단을 명시적으로 요청할 수 있다. 이 진단이 `retry`를 선택하면 새 입력에서 한 번 더 실행하며, 다시 실패하면 재차 보류한다.

초기화 중 최초 원입력의 의도 해석이 기술적 실행 실패로 끝났다면 원인을 고친 뒤 `request --retry-action AC-... --request-id UC-...`로 그 해석을 다시 요청한다. 실행기는 전 실행의 로컬 종료와 예약 회수, 불변 원입력, 현재 채택 프로필과 초기 운영 권한을 확인한다. 같은 action과 활동을 이어 간다. 정상 종료한 native 최종 응답이 정확한 실행 근거와 함께 보존돼 있으면 새 모델 실행 없이 그 응답을 중앙에서 다시 처리하며, 원 실행의 종료 시각·결과 참조·실패 이력을 보존한다. 재사용할 정상 응답이 없으면 실패 실행을 선행 기록으로 연결한 새 실행을 배정한다. 아직 시작하지 않은 해당 실패의 운영 진단은 재시도로 대체한 이력에 남긴다. 이 요청은 새로운 연구를 열거나 의미를 승인하지 않는다.

`input_overflow`로 보류된 입력은 설치나 필수 입력을 수리했거나 사용자가 현재 설정을 적법하게 바꾼 뒤 `request --retry-action AC-... --request-id UC-...`로 정확한 action 하나를 명시적으로 다시 포장할 수 있다. 이 요청은 원 activity와 action ID를 유지하면서 현재 grant와 현재 채택 프로필을 다시 검사할 뿐, 입력 초과가 해소됐다고 선언하거나 새 권한을 만들지 않는다. 재시도에 따른 자동 질문 해소는 실제 포장이 현재 한도 안에 들어온 사실에 근거한다. 이미 적법한 결정으로 해소된 질문은 그 해소 근거를 유지한다. 다시 넘치면 원 실패와 질문은 이력으로 보존되고 새 실패와 새 질문이 같은 activity를 이어받는다. 같은 `request-id`의 재전송은 최초 효과만 재생한다.

## 입력과 결정을 제공하는 법

### 자유 형식 사용자 입력

새 연구 정보나 요청은 `input`으로 원문을 보존한다.

```powershell
python .agents/skills/do-math/scripts/do_math.py input `
  --repository .skill-workspace/my-math/repo `
  --instance RI-... `
  --text "보조정리 H의 가정이 실제 목표 범위와 같은지 다시 조사하세요."
```

긴 입력은 `--file`을 사용한다. 입력은 의도 해석과 독립 대조를 거쳐 현재 구현이 지원하는 내부 변경이나 다음 후보 준비에 연결된다. 자유 문장을 곧바로 권한이나 목표 변경으로 적용하지 않는다.

### 구조화된 사용자 결정

목표·정책·grant·과제 범위·학술 요구처럼 효과가 정해진 변경은 JSON 객체를 파일로 만든 뒤 `decision --file`로 보낸다. 목표와 학술 요구 변경은 현행 헌장 전체를 읽어 `kind="charter"`의 새 `record`로 작성한다. 정책은 다음 구조를 사용한다. 예시의 ID·범위·근거·문면은 실제 승인한 값으로 바꾸고, 기존 정책을 대체하면 그 활성 ID를 `supersedes`에 넣는다.

```json
{
  "kind": "policy",
  "record": {
    "id": "PO-source-evidence",
    "kind": "policy",
    "revision": 1,
    "supersedes": [],
    "content": {
      "rule_id": "source-evidence",
      "text": "사용한 문헌은 내부 보존 사본과 정확한 절 좌표를 남긴다.",
      "scope": ["연구 수행"],
      "reason_refs": ["CH-실제-현행-헌장-ID"],
      "audit_refs": []
    }
  }
}
```

```powershell
python .agents/skills/do-math/scripts/do_math.py decision `
  --repository .skill-workspace/my-math/repo `
  --instance RI-... `
  --file .skill-workspace/my-math/policy-decision.json
```

구조화 결정의 정확한 종류·필드와 현행 기록 조회 절차는 CLI 실행 계약에서 확인한다. 통치 기록은 새 ID·판본과 완전한 `content`로 제출하고, `supersedes`가 가리키는 기록이 적용 시점에 활성인 같은 종류인지 검사한다. 반환의 `effect`와 `reason`으로 적용 여부를 확인한다.

### 원자료 수입

```powershell
python .agents/skills/do-math/scripts/do_math.py source `
  --repository .skill-workspace/my-math/repo `
  --instance RI-... `
  --file C:\research\paper.pdf `
  --name paper.pdf
```

`source`는 접수 시점 바이트와 SHA-256을 제어 요청에 고정한 뒤 산출 묶음과 source record로 보존한다. 같은 이름·같은 해시는 변경 없음으로 처리한다. 같은 이름의 내용이 바뀌면 새 revision을 보존하고, 실제로 그 source에 의존한 지식·진행 중 실행과 과제의 현재성을 다시 평가한다.

같은 이름의 source가 바뀌어도 이미 `completed`인 과제의 상태와 완료 이력은 보존한다. 대신 그 과제의 `assessment.current`를 false로 바꾸고 `invalidated_reason`에 변경 근거를 남긴다. 단순 이력 조회는 완료 상태를 보존하지만, 다른 과제가 그 완료 판정을 실제 dependency로 사용하려면 현재성 검사를 통과해야 한다. 새 source 판본의 재검증은 완료 과제를 다시 여는 대신 후속 의무로 연결한다.

## 조회와 결과 회수

### 기록 조회

`query`는 지식, 관계, 과제, 활동, 실행, grant, 결정, 외부 operation, 검토 계보, 신뢰 환경, source와 종류 정의를 한 record 목록으로 조회한다.

```powershell
python .agents/skills/do-math/scripts/do_math.py query `
  --repository .skill-workspace/my-math/repo `
  --instance RI-... `
  --kind knowledge `
  --text "right identity" `
  --limit 50
```

`--related-to ID`는 관계의 이웃과 관계 기록을 찾는다. `--direction incoming|outgoing|both`로 방향을 구별한다. 결과의 `snapshot`, `total`, `loaded`, `truncated`, `next_cursor`를 함께 읽는다. 다음 페이지는 같은 query 조건과 `--cursor`를 사용하며 cursor가 고정한 snapshot을 바꾸지 않는다.

### 정확한 기록 읽기

```powershell
python .agents/skills/do-math/scripts/do_math.py read `
  --repository .skill-workspace/my-math/repo `
  --instance RI-... `
  --snapshot <git-oid> `
  --id KN-...
```

`--id`는 구조화 record를 JSON과 SHA-256으로 반환한다. `--path`는 snapshot 안의 파일 바이트를 읽는다. UTF-8이면 `text`, 아니면 `base64`로 반환한다. 파일 바이트를 로컬 파일로 받으려면 `--path`와 `--output`을 함께 지정한다. `--id`에는 `--output`을 사용할 수 없다.

### 파일 목록과 snapshot 내보내기

파일 자체를 찾으려면 `query --files`를 쓴다. 기본 prefix는 `research/`이고, prefix는 `research/` 또는 `runtime/` 아래의 `/`로 끝나는 POSIX 경로여야 한다.

```powershell
python .agents/skills/do-math/scripts/do_math.py query `
  --repository .skill-workspace/my-math/repo `
  --instance RI-... `
  --files `
  --prefix runtime/artifacts/ `
  --text formal.json
```

`export`는 기본적으로 한 snapshot의 `research/`만 새 경로나 빈 디렉터리로 복사한다. `--all`을 지정하면 `runtime/`도 포함한다.

```powershell
python .agents/skills/do-math/scripts/do_math.py export `
  --repository .skill-workspace/my-math/repo `
  --instance RI-... `
  --snapshot <git-oid> `
  --destination .skill-workspace/my-math/export
```

내보낸 파일은 조회 사본이며 새 정본이 아니다.

## 정지, 재개와 종결

```powershell
python .agents/skills/do-math/scripts/do_math.py pause `
  --repository .skill-workspace/my-math/repo `
  --instance RI-... `
  --reason "정책 변경 전 상태를 검토합니다."
```

제어 명령은 먼저 workspace의 inbox에 요청을 기록한다. 같은 인스턴스의 writer lock을 얻을 수 있으면 즉시 적용하고, 다른 실행기가 lock을 보유하면 `effect="pending engine processing"`, `lock="busy"`를 반환한다. 이 경우 현재 실행기나 다음 `run`이 요청을 적용한다.

같은 내용의 제어 명령을 다시 보내면 최초 영수증을 재생하며 효과를 반복하지 않는다. 재개 뒤 같은 이유로 다시 정지하거나 이전 설정을 새로 적용하려면 명령에 새 `--idempotency-key`를 붙인다. 예를 들어 위 정지를 새로 적용할 때에는 `--idempotency-key pause-review-2`를 추가하고, 그 요청을 재전송할 때는 같은 키를 유지한다. `replayed=true` 응답의 상태·snapshot은 최초 처리 시점의 값이므로 현재 상태는 `status`로 확인한다. 직접 요청 ID를 지정하는 방법과 전체 적용 범위는 [CLI 실행 계약](references/CLI-실행-계약.md)의 공통 반환 절을 따른다.

AI 실행 중 pause·close, grant 철회, 필수 입력·목표·정책의 현재성 변경 또는 그 AI 실행에 적용된 기한 도래가 확인되면 실행기는 관리 디렉터리 `.control/`에 정지 요청을 기록한다. 작업자는 새 연구나 외부 행동을 시작하지 않고 이미 얻은 사실과 가능한 제출·체크포인트를 남긴다. 중앙은 정지 전에 미리 접수한 봉인 후보가 있으면 그 원문만 회수한다. 정지 뒤 도착한 native final이나 파일은 보존 자료일 수 있지만 새 의미 후보로 승인하지 않는다. 실행기는 로컬 Job의 종료를 확인한 뒤 예약을 반환한다. 현재 구현이 관찰하지 못한 원격 종료와 공급자 내부 호출은 `unknown` 범위로 남는다.

```powershell
python .agents/skills/do-math/scripts/do_math.py check `
  --repository .skill-workspace/my-math/repo `
  --instance RI-...

python .agents/skills/do-math/scripts/do_math.py resume `
  --repository .skill-workspace/my-math/repo `
  --instance RI-... `
  --reason "검사 결과와 남은 범위를 확인했습니다."
```

`resume`은 `closed`와 `completed` 상태를 다시 열지 않는다. 거부된 출력이나 진단에서 대기로 남긴 실패 행동과 `input_overflow`를 일반 재개로 실행 대기열에 되살리지 않는다. 먼저 원인을 고치고 운영 점검의 재시도, `request --retry-action`, 또는 현재 입력의 새 역할 요청으로 이어 간다. 새 실행은 필요한 결과·체크포인트를 재사용하되 과거의 잘못된 판정을 현재 상태로 복사하지 않는다.

`close`는 queue를 비우고 인스턴스를 종결한다. 진행 중 실행의 회수 기록은 남길 수 있지만 새 연구를 시작하지 않는다.

### 독립 운영의 설정과 정지

`operator status`는 실제 예약 작업을 조회한다. `operator install`은 현재 인스턴스 설정으로 정상 감독·연구 엔진 작업을 다시 맞추고 `operator uninstall`은 그 인스턴스의 연구·정기 감독·일회성 wake 예약을 제거한다. 운영 주기와 기한은 `configure`의 `operator_enabled`, `operator_interval_seconds`, `operator_timeout_seconds`, `operator_effort`로 바꾼다. `operator_effort`, `tier_models`와 `role_tiers.independent_operator`은 실패 시 설치 복구 AI에 적용된다. 정상 감독에는 모델 배정이 없다. 즉시 적용된 운영 설정 변경은 CLI가 예약에 반영한다. 제어가 아직 대기 중이면 운전자는 적용을 확인한 뒤 같은 인스턴스에서 `operator install`로 예약을 재조정한다. 비활성화나 예약 제거가 이미 실행 중인 연구까지 정지했다는 뜻은 아니다.

연구 예약의 Windows 실행 제한은 무제한을 뜻하는 `PT0S`다. 운영 담당 예약에는 `operator_timeout_seconds`에 종료 여유 300초를 더한 유한 제한을 적용한다. 기존 설치를 갱신할 때는 같은 인스턴스에서 `operator install`을 사용하고 `operator status`의 `execution_limit`을 확인한다. 재설치는 기존 예약의 Disabled 상태를 보존하며 HOLD나 사용자 정지를 해제하지 않는다.

사용자가 연구와 자동 운영을 함께 멈출 때는 `operator hold`를 쓴다. 이 명령은 고유 ID의 HOLD를 만들고 사용자 정지를 요청한다. `operator release`는 그 HOLD를 해제하며, 현재 사용자 정지가 정확히 같은 HOLD에서 왔을 때만 재개한다. 이후의 다른 사용자 정지는 그대로 유지한다.

독립 운영 경로가 보내는 자동 제어는 `--origin operator`로 표시한다. 이 경로는 사용자 정지를 해제하거나 목표·정책·학술 요구·외부 행동·신뢰 판정을 만들지 못한다. 사용자 제어의 기본 출처는 `user`다. 출처 구별과 복구 지시는 같은 사용자 OS 권한 안의 실행 계약이며 인증된 호출자 경계나 보안 격리 장치가 아니다.

설치 감독을 읽기 전용으로 시험하려면 `operator probe`를 사용한다. 이 명령은 상태·기록을 모델 없이 읽고 연구나 예약 상태를 변경하지 않으며, 엔진 읽기 실패가 있어도 복구 AI를 시작하지 않고 실패 증거만 반환한다. 정상 `operator check`는 같은 감독 뒤 실행 가능한 엔진 작업을 요청할 수 있고, 엔진 시작 실패의 실제 증거나 수락된 설치 결함 진단이 있을 때 복구 AI를 연다.

예약 작업이 실행하는 bootstrap은 설치 시점의 파일 manifest와 해시에 고정된 복사본이다. bootstrap은 재분석 지점·파일 해시와 경로를 검사하고, 실행 중인 live 설치와 구별된다. 복구 AI는 writer lock과 별도 설치 유지보수 lock, 종료된 선행 실행, 고정 복구 프로필과 현재 능력 증거, 운영 용량을 모두 확인한 뒤 live 설치만 수리할 수 있다. 연구 기록·사용자 전역 설정·예약 작업·사용자 결정을 고치지 않는다. 수리 뒤 설치본의 `probe_cli.py --skill-only`가 통과한 경우에만 두 lock을 놓고 엔진 재시작을 요청한다. 이는 지시 기반 경계이며 다른 사용자 권한·파일·네트워크·자격 증명 접근을 OS가 차단한다는 뜻이 아니다. 실행별 근거와 결과는 `<workspace>/operator/` 아래에 보존되며 이 대화로 자동 알림이 전송되지는 않는다.

## 운영 제어 명령의 용도

| 명령 | 사용할 때 | 중요한 경계 |
|---|---|---|
| `configure --config-file` | 모델 대응·역할 등급·세션 한도, 시간, 검토·관찰·산출 한도를 바꿀 때 | 목표·정책·학술 요구·외부 허가는 설정이 아니다 |
| `request --role ...` | 지원하는 후보 준비·연구 계획·보충 조사·운영 점검·유지보수 action을 명시적으로 열 때 | 요청 생성은 모델 실행이나 결과 승인이 아니다 |
| `request --retry-action AC-...` | 수리 뒤 입력 초과를 다시 포장하거나, 기술적 실패로 끝난 초기 원입력의 의도 해석을 다시 시도할 때 | 같은 action·활동과 원 실패를 보존하며, 해소 선언이나 새 승인·범위 변경을 만들지 않는다 |
| `knowledge --file` | candidate·종류 정의·관계를 수입하거나 기존 지식을 개정·무효화할 때 | candidate 수입은 K 편입이 아니다 |
| `trust --file` | 신뢰 환경을 등록·전환·무효화할 때 | 전환 성공은 무관한 의미·의존 정지 원인을 해소하지 않는다 |
| `external --file` | grant에 결박된 HTTP 행동을 준비하거나 unknown을 대조하고 알려진 실패를 재시도할 때 | `confirmed`와 HTTP 성공 여부는 별도다 |
| `conversation --file` | 대화 연결 세대·lease·소실 정책을 기록할 때 | 대화 연결은 실행 권한이 아니다 |
| `check` | 저장·참조·상태 불변식과 보존 artifact 해시를 검사할 때 | 자연어 의미와 수학적 타당성을 새로 판정하지 않는다 |

구조화 JSON의 전체 형식과 예시는 CLI 실행 계약을 따른다.

## 오류와 반환 코드

모든 명령은 JSON을 반환하며 `status`만 `--json`이 없을 때 사람이 읽는 텍스트를 반환한다.

| 종료 코드 | 뜻 |
|---|---|
| `0` | 명령 처리가 끝났다. 제어 요청은 `effect`를 확인해야 하며 다른 수학·완료 판단을 뜻하지 않는다 |
| `1` | `check`가 결함을 찾았거나 `profile`이 요청한 표면을 확인하지 못했다 |
| `2` | 명령 인자, JSON, 대상 ID·상태 또는 요청 계약이 잘못됐다. 응답 `kind`는 `input_error`다 |
| `5` | Git 저장·저장소 작업, OS 또는 subprocess 도구 오류이면 응답 `kind`는 `tool_error`다. `run`이 다른 실행기가 보유한 writer lock을 얻지 못한 경우도 여기에 속하며, 이때는 그 실행기가 끝난 뒤 다시 실행한다. 제어 명령의 lock 경합은 오류가 아니라 exit 0과 `lock="busy"`로 반환한다. 구현이 요청을 처리하지 못한 내부 계약 오류이면 `kind`는 `contract_error`이고 `next_owner`는 `maintenance`다. `init`·`configure`가 상태를 저장했으나 예약 등록에 실패한 경우에도 exit 5이며, 이때는 `result.operator_schedule`에 `status="failed"`와 그대로 실행할 재조정 명령이 들어 있다 |

제어 명령은 구문이 맞아도 접수 뒤 전제가 바뀌면 exit 0과 `effect="rejected"`, `reason`을 반환할 수 있다. `accepted=true`는 inbox 접수를 뜻하고 적용·실행·성공과 다르다.

## 현재 지원 범위

판본 5는 인스턴스별 Git ref와 writer lock, 기록군 저장, 활동·다중 실행 수명, 불변 프로필, 구조화 작업 의무·처분, 편입 묶음, 독립 동일성 검토의 범위 계획과 자기 점검 규칙을 정의한다. 각 명령과 역할의 성공은 그 소비자가 실제로 검사·적용한 범위에만 효력이 있다. 스키마 적합, 로컬 생산자 검사, 중앙 미리보기, 제출 의도 접수, 저장 적용, 형식 검사와 독립 의미 판정은 서로 다른 증거다.

새 인스턴스의 작업·운영 예산은 모델별 로컬 AI 실행의 동시 점유로 계산한다. Codex의 turn usage와 Claude의 최종 result usage는 보존하지만 공급자 내부 호출별 ID·예약·원격 종료를 보증하지 않는다. 현재 기본 Windows 실행은 Codex의 `danger-full-access`·승인 정책 `never`, Claude의 `bypassPermissions`로 기존 사용자 권한을 쓴다. Windows Job은 로컬 프로세스 수명과 자손 종료를 관리하지만 모든 host 파일·network·credential 접근을 차단하지 않는다. 별도 세션·작업 공간과 동료 결과 비제공은 입력 경계를 만들지만 통계적 독립성이나 강한 OS 격리의 증거가 아니다.

## 기능 판본과 결과의 시각을 확인한다

판본 5 저장소는 세분된 기록군과 사건을 권위 있는 Git 상태로 공개한다. 구현·저장 계약을 바꾸면 현행 계약으로 새 인스턴스를 초기화한다. 필요한 과거 산출은 정확한 출처·실제 확인 범위를 가진 새 입력으로 제공한다. 이전 runtime·queue·승인·질문을 변환해 재개하거나 옛 거부를 소급 수락하지 않으며, 설치본 수리로 기존 HOLD를 해제하지 않는다.

`status --json`은 한 Git snapshot에서 과제 단계, 선택된 미시작 요청, 저장된 실행·예약·슬롯 예산·`provider_waits`, 마지막 수락 결과, 미해소 의무와 대기 이유를 함께 재구성한다. 이 snapshot은 저장된 원장 상태를 일관되게 보여 주지만 조회 순간의 호스트 프로세스나 공급자의 현재 상태를 원자적으로 관찰한 값은 아니다. 실제 프로세스·예약 작업·별도 운영 로그를 함께 볼 때에는 각 관측 시각과 범위를 구별한다. 열린 사용자 질문은 `questions`, 출처·소유·대상·해소는 `question_links`, 실패 의무는 `waiting_actions`에서 확인한다.

고정 snapshot의 실행 시각과 계보는 다음 명령으로 내보낸다. JSON은 원시 UTC와 현지 날짜·UTC offset을 함께 보존하고 CSV도 같은 실행 행을 사용한다. 과거에 기록하지 않은 시각은 null 또는 빈 셀이다.

```powershell
python .agents/skills/do-math/scripts/do_math.py timeline --repository <repo> --instance <RI-ID> --snapshot <OID> --format json --timezone Asia/Seoul
```

`--include-operator`는 현재 로컬 운영 로그도 별도 집계 단위로 포함한다. 각 파일의 해시와 관측 시각이 붙으며 그 내용이 해당 연구 snapshot에 포함됐다는 뜻은 아니다. 겹친 실행 시간의 합계를 실제 경과 시간으로 사용하지 않는다.

## 설치본 검사

스킬 폴더 전체를 설치한 뒤 다음 명령으로 역할별 필수 문서와 출력 스키마를 확인한다. 경로는 실제 설치 위치에 맞춘다.

```powershell
python .agents/skills/do-math/scripts/probe_cli.py --skill-only
```

이 검사는 스킬 폴더 안의 문서와 코드만 읽으며 모델을 호출하지 않는다. `scope="installed_skill_structure"`, `status="verified"`는 역할 읽기 대응표의 문서와 운영 문서를 읽었고 역할 출력 스키마의 형식 검사를 통과했다는 뜻이다. 문서 내용의 정확성, 실행 환경이나 연구 성능까지 검증한 결과는 아니다.

회귀 검사는 `run_tests.py`로 실행한다. 실행기는 unittest discovery로 `scripts/tests/test_*.py`를 수집하고 기본으로 전체를 순차 실행한다. 실제 Lean·부하 검사는 Windows Job이 소유한 별도 프로세스에서 실행한다. 별도 프로세스에서 실행하는 검사는 같은 클래스의 공통 준비를 한 번 수행하며, 각 검사와 그 준비·종료 단계의 제한 시간은 기본 300초다. `--timeout`으로 초 단위 상한을 바꿀 수 있다. 이 값은 테스트 실행기의 운영 기본값이며 제품 Lean의 무제한 계산 계약을 바꾸지 않는다.

```powershell
python .agents/skills/do-math/scripts/run_tests.py --output 임시/do-math-tests-all
```

`--group unit`은 순수 규칙과 임시 파일 중심의 검사, `integration`은 실제 저장·프로세스 등 통합 검사, `lean`은 실제 컴파일러 검사, `resource`는 CPU·메모리·큰 출력 부하 검사, `archive`는 과거 실행 증거의 전체 무결성 검사다. `--group`을 반복해 조합할 수 있으며 생략하면 모두 실행한다. `--match`는 테스트 ID의 glob으로 선택하고 `--list`는 수집 결과만 표시한다. 선택 결과가 없으면 실패로 끝난다.

```powershell
python .agents/skills/do-math/scripts/run_tests.py --group unit --output 임시/do-math-tests-unit
python .agents/skills/do-math/scripts/run_tests.py --group lean --timeout 600 --output 임시/do-math-tests-lean
python .agents/skills/do-math/scripts/run_tests.py --match "*test_performance_save*" --list
```

결과 디렉터리는 새 경로나 빈 디렉터리를 지정한다. 생략하면 고유한 임시 디렉터리를 만든다. `report.json`은 테스트별 결과·시간, 느린 검사 목록, 코드 판본과 실행 중 변경 여부를 기록한다. 격리 실행의 stdout·stderr와 진행 기록도 남긴다. 격리 작업자의 임시 파일은 해당 결과 디렉터리의 `scratch/` 아래에 만들므로, 강제 종료로 정리되지 않은 Lean 입력·출력도 그곳에서 찾을 수 있다. 시간 초과 때에는 해당 Job의 자식까지 종료하고, 같은 작업자에서 끝내지 못한 검사는 미실행으로 기록하며 다른 검사 그룹을 계속한다. 부분 실행을 전체 통과로 표시하지 않는다. 일반 `integration`·`unit`·`archive` 그룹에는 이 프로세스 시간 상한을 적용하지 않는다.

기존 `python -m unittest discover -s .agents/skills/do-math/scripts/tests -p "test_*.py"`도 사용할 수 있지만, 그룹 선택·시간 보고·외부 프로세스 종료 관리는 제공하지 않는다. 새 실제 Lean·부하 테스트에는 `test_categories.test_group`으로 그룹을 명시한다. 분류하지 않은 새 테스트는 보수적으로 `integration`에 들어간다. 일부 시험 파일은 직접 실행해도 시험을 시작하지 않으므로 파일별 종료 코드만으로 회귀 검사를 완료했다고 판단하지 않는다.

실제 Codex·Claude·Lean·HTTP·Windows 프로세스가 필요한 검사는 각 시험의 환경 조건과 실행 결과를 확인한다. 검증 결과는 검사한 판본, 사례, 통과·실패·미실행 범위와 함께 보존하고, 해석 기준은 [CLI 실행 계약](references/CLI-실행-계약.md)의 「검증 근거의 해석」을 따른다.

### Claude 전용 검사와 실행 제한

특정 연구를 Opus 5만으로 운영하려면 모든 등급·실제 역할·독립 운영 배정을 `claude-opus-5`로 맞추고 그 인스턴스의 `claude_only_assigned_model=true`를 사용한다. 옵션 기본값은 false이며 다른 연구의 모델 정책은 바뀌지 않는다. 모델 잠금은 내부 보조 모델을 제한하고 보고 모델을 대조하며, 모든 역할을 자동으로 Claude로 바꾸는 옵션은 아니다.

`probe_cli.py --skill-only`는 정적·동적 역할 스키마와 문서 구조만 검사한다. 대표 실호출은 provider와 모델, 새 증거 경로를 명시한다. `structured`·`files`·`stop`은 두 공급자에 사용하며, `background`와 `--only-assigned-model`은 Claude 전용이다. 이 명령은 실제 모델 예산을 사용하므로 해당 인스턴스의 모델 정책을 따른다.

```powershell
python .agents/skills/do-math/scripts/probe_cli.py --provider claude --model claude-opus-5 --only-assigned-model --cases structured files background stop --scholarly --output-dir <새-증거-경로>
```

### 공급자 한도와 재관찰

공급자 한도는 Claude 등 모델 공급자가 새 호출을 제한하는 상태다. 확정된 한도는 작업·운영 호출 양쪽에서 기다린다. 일회성 `operator wake` 예약은 모델을 부르지 않고 연구 진입점을 깨운다. 실제 재관찰은 허가된 action 하나로 수행한다. HOLD·사용자 정지가 있으면 이 예약으로 연구나 모델을 시작하지 않는다. `operator status`는 wake 예약도 보여 주고 `uninstall`은 그 인스턴스의 wake를 함께 제거한다. 자동 등록 실패는 운영 원장에 남으며 정기 Python 진입부가 다시 맞춘다.

### 사용자 질문에 답하기

사용자 질문에 답하는 자유 입력에는 `input --responds-to <QU-ID>`를 반복 지정할 수 있다. 그 원문은 독립 의도 대조를 거친 뒤 대응 질문만 해소한다. 구조화 결정은 `resolves_questions`에 해당 ID를 넣는다. 일반 재개는 공급자 실패나 개정 위임의 보류 의무를 무조건 queue로 되살리지 않는다.
