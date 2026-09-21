# Jev CLI

판단할 자료와 질문을 전달하면 TypeSafe의 Jev가 선택·점수·참일 확률을 JSON으로 돌려주는 명령줄 도구입니다. 질문과 판단 기준은 호출할 때마다 바꿀 수 있습니다. 도구는 인증 정보 읽기, HTTP 요청, 응답 검사와 제한된 재시도를 처리합니다.

Python 3.10 이상과 표준 라이브러리만 사용합니다. 별도 Python 패키지는 설치하지 않습니다. `jev.py`를 원하는 폴더로 복사해 사용할 수 있으며, 예제를 따라 하려면 이 폴더 전체를 복사하세요. Windows·macOS·Linux에서 같은 입력 형식을 사용하도록 작성했습니다. 인터넷 연결과 유효한 TypeSafe API 키가 필요합니다.

## 처음 실행하기

아래 명령은 `jev.py`와 `examples/`가 있는 폴더에서 실행합니다. 다른 폴더에서 실행할 때는 스크립트와 입력 파일의 절대 경로를 사용하세요. 모든 입력 파일은 UTF-8로 저장합니다. UTF-8 BOM이 있는 파일도 읽을 수 있습니다.

### 1. Python 확인

Windows PowerShell:

```powershell
python --version
python jev.py --help
```

macOS·Linux의 bash/zsh:

```sh
python3 --version
python3 jev.py --help
```

Python이 없거나 3.10보다 낮으면 [Python 설치 안내](https://www.python.org/downloads/)를 따라 설치한 뒤 다시 확인하세요. `--help`가 명령 사용법을 출력하면 실행 준비가 된 것입니다.

### 2. 인증 설정

[TypeSafe 콘솔](https://console.typesafe.ai/)에서 발급받은 키를 실행할 셸의 `TYPESAFE_API_KEY` 환경변수에 설정합니다. 아래의 `YOUR_API_KEY`는 실제 키로 바꾸세요. 설정은 현재 셸과 그 셸이 실행하는 프로그램에 적용됩니다.

PowerShell:

```powershell
$env:TYPESAFE_API_KEY = 'YOUR_API_KEY'
```

bash/zsh:

```sh
export TYPESAFE_API_KEY='YOUR_API_KEY'
```

자동화 시스템에서는 비밀값 설정 기능으로 같은 환경변수를 전달하세요. API 키를 요청 JSON이나 저장소에 넣지 마세요. 에이전트가 이미 실행 중이면 그 프로세스에도 환경변수가 전달되었는지 확인해야 합니다.

### 3. 요청 확인과 실제 호출

먼저 API 호출 없이 예제의 형식을 검사합니다. `--dry-run`은 키가 없어도 실행되며, 모델 기본값이 적용된 요청 JSON을 출력합니다. Jev의 판단이나 서버 측 유효성 검사는 수행하지 않습니다.

```sh
python jev.py --input examples/request.json --dry-run
```

macOS·Linux에서는 이 명령과 아래의 `python`을 `python3`로 바꾸세요. 실제 호출은 `--dry-run`을 빼면 됩니다. 이때 입력한 자료가 TypeSafe API로 전송되고 서비스 요금이 발생할 수 있습니다.

```sh
python jev.py --input examples/request.json
```

예제는 한 고객 메시지에 대해 환불 요청 여부, 담당 부서, 시간적 긴급성을 함께 묻습니다. 정상 실행은 종료 코드 0과 결과 JSON을 반환합니다. 표준오류에 오류가 나오면 아래의 오류 표에 따라 원인을 해결한 뒤 다시 호출하세요.

## 자료와 판단 정의하기

기본 요청은 `state`와 `questions` 두 필드로 구성합니다. `state`에는 판단할 자료와 필요한 맥락을 넣습니다. 문자열·객체·배열을 사용할 수 있습니다. `questions`에는 질문 ID를 키로 사용해 여러 질문을 넣습니다.

```json
{
  "state": {
    "message": "중복 결제를 환불해 주세요.",
    "policy": "중복 결제는 확인 후 환불할 수 있다."
  },
  "questions": {
    "refund_requested": {
      "type": "noul",
      "instructions": "`message`에서 환불을 요청하는가?"
    },
    "department": {
      "type": "choice",
      "instructions": "`message`를 처리할 부서는 어디인가?",
      "criteria": {
        "billing": "결제와 환불",
        "delivery": "배송",
        "other": "어느 부서에도 해당하지 않음"
      }
    },
    "urgency": {
      "type": "score",
      "instructions": "`message`에 표현된 시간적 긴급성은 어느 정도인가?",
      "criteria": [
        "처리 기한이나 즉시 대응을 요구하지 않는다.",
        "빠른 처리를 요청하지만 즉시 대응을 요구하지는 않는다.",
        "지금 즉시 처리해야 한다고 명시한다."
      ]
    }
  }
}
```

| 원하는 판단 | `type` | `criteria` | 핵심 결과 |
|---|---|---|---|
| 조건이 성립하는가 | `noul` | 선택 사항. `true`·`false`의 의미를 담는 객체 | `noul`: 참일 확률, 0~1 |
| 주어진 후보 중 어느 것인가 | `choice` | 후보 ID와 설명의 객체, 최대 255개 | `choice`, `probabilities`, `confidence` |
| 설명한 단계 중 어느 정도인가 | `score` | 낮은 단계부터 순서대로 쓴 설명 배열, 2~10개 | `score`, `legend`, `probabilities`, `confidence` |

질문 ID는 결과를 찾기 위한 이름이며 모델에 질문 내용으로 전달되지 않습니다. 질문의 의미는 `instructions`에 완전하게 적으세요. 중첩 자료는 예제처럼 백틱으로 감싼 경로를 써서 가리킬 수 있습니다. 예를 들면 `ticket.messages[0].text`입니다.

`instructions`, Choice의 각 후보 설명, Score의 각 단계 설명, Noul의 `criteria.true`·`criteria.false` 값에는 문자열·객체·배열·`null`을 사용할 수 있습니다. 이 허용 범위는 각 설명의 값에 적용됩니다. Choice의 `criteria` 전체는 객체, Score의 `criteria` 전체는 배열이어야 합니다. Noul의 `criteria`는 생략할 수 있으며, 제공하면 객체여야 합니다.

`instructions` 필드 자체는 필수입니다. 값으로 `null`을 전달할 수는 있지만, 질문의 의미가 분명하도록 내용을 작성하는 것을 권장합니다. 도구는 구조를 임의로 문자열로 바꾸지 않습니다.

```json
{
  "type": "choice",
  "instructions": {
    "question": "`message`에 가장 적합한 담당 부서는 어디인가?",
    "rule": "고객이 실제로 요청한 해결 내용을 기준으로 판단한다."
  },
  "criteria": {
    "billing": {"includes": ["중복 결제", "환불"], "excludes": ["배송 조회만 요청"]},
    "delivery": {"includes": ["배송 조회", "분실 신고"]},
    "other": "제시된 부서에 해당하지 않는 요청"
  }
}
```

같은 `state`로 답할 수 있는 독립적인 질문은 한 요청에 묶으세요. 묶인 질문은 서로의 답을 볼 수 없습니다. 앞선 답을 알아야 다음 자료나 선택지를 만들 수 있다면, 첫 결과를 읽은 뒤 새로운 요청을 보내세요. Choice로 값을 추출할 때는 후보에 원하는 값이 포함되어 있어야 합니다. 여러 항목이 동시에 참일 수 있으면 각 항목을 별도 Noul로 물을 수 있습니다.

## 파일과 파이프로 연결하기

통합 요청 JSON을 파일로 지정하거나 표준입력으로 전달할 수 있습니다. `--input`을 생략하면 표준입력을 읽습니다. 경로는 명령을 실행한 현재 디렉터리를 기준으로 해석합니다.

PowerShell 7 이상:

```powershell
Get-Content -Raw -Encoding utf8 examples/request.json | python jev.py
```

Windows PowerShell 5.1에서는 한글을 파이프로 전달하기 전에 `$OutputEncoding = [System.Text.UTF8Encoding]::new($false)`를 설정하세요. 파일 입력을 쓰면 이 설정이 필요 없습니다.

bash/zsh:

```sh
cat examples/request.json | python3 jev.py
```

자료와 질문을 분리하면 같은 질문을 다른 자료에 재사용하기 쉽습니다. `questions.json`은 `questions` 필드의 **내용만** 담은 객체입니다. `--state`의 기본 형식은 일반 텍스트입니다.

```sh
python jev.py --state document.txt --questions questions.json
python jev.py --state context.json --state-format json --questions questions.json
```

위의 `document.txt`, `context.json`, `questions.json`은 사용자가 준비하는 파일명입니다. 이 폴더에는 통합 예제인 `examples/request.json`이 들어 있습니다. `--state-format json`을 지정하면 자료의 JSON 구조를 보존합니다. 지정하지 않으면 파일 내용 전체를 하나의 문자열로 보냅니다.

`--state` 또는 `--questions` 중 하나를 `-`로 지정하면 그 부분을 표준입력에서 읽습니다. 둘을 동시에 `-`로 지정할 수는 없습니다. 통합 입력인 `--input`과 분리 입력인 `--state`·`--questions`를 함께 사용할 수도 없습니다.

## 결과 사용하기

아래는 출력 구조를 보여 주는 예시 값입니다. 실제 호출의 수치는 달라질 수 있습니다.

```json
{
  "model": "jev-1.13.0",
  "answers": {
    "refund_requested": {"type": "noul", "noul": 0.98},
    "department": {
      "type": "choice", "choice": "billing",
      "confidence": 1.0,
      "probabilities": {"billing": 1.0, "delivery": 0.0, "other": 0.0}
    },
    "urgency": {
      "type": "score", "score": 0.37, "confidence": 0.45,
      "legend": {"0": "기한 요구 없음", "1": "빠른 처리 요청", "2": "즉시 처리 요구"},
      "probabilities": {"0": 0.63, "1": 0.37, "2": 0.0}
    }
  },
  "usage": {"input_tokens": 547, "output_tokens": 70}
}
```

Noul의 0.5는 참과 거짓의 확률이 비슷하다는 뜻입니다. 강도가 중간이라는 뜻으로 해석하지 마세요. Noul에는 별도의 `confidence`가 없습니다. Score는 정의한 단계 번호의 확률 가중 평균이므로 소수일 수 있습니다.

Choice·Score의 `confidence`는 확률이 한 후보나 단계에 얼마나 모이는지를 0~1로 나타냅니다. 두 후보의 확률이 0.5씩이면 뚜렷한 우세가 없고, 0.99와 0.01이면 한 후보에 집중되어 있습니다. 이 값은 서비스가 계산해 반환하며 CLI가 다시 계산하지 않습니다. `confidence`가 0.9라고 해서 판단이 정답일 확률이 90%라는 뜻은 아닙니다. 자동 행동의 임계값은 사용하는 자료와 오판 결과에 맞춰 정해야 합니다.

정상 호출은 응답 필드와 확률 범위를 검사한 뒤 JSON 한 개를 표준출력에 씁니다. 확률의 합, 판단 내용의 사실성, 업무상 행동의 타당성까지 검증하지는 않습니다. 서비스가 추가한 응답 필드도 보존합니다. 출력은 UTF-8이며 로그를 섞지 않습니다. 입력·출력 파일은 자동으로 저장하지 않으므로 보관하려면 호출자가 리다이렉션하거나 직접 저장하세요. `--help`는 일반 도움말을, `--dry-run`은 결과 대신 요청 JSON을 출력합니다.

PowerShell에서 결과를 읽는 예:

```powershell
$json = python jev.py --input examples/request.json
if ($LASTEXITCODE -ne 0) { throw 'Jev 호출 실패: 표준오류를 확인하세요.' }
$result = $json | ConvertFrom-Json
$result.answers.department.choice
```

Python 프로그램이나 에이전트가 만든 자동화에서는 인자를 배열로 전달하면 셸 따옴표 문제를 피할 수 있습니다. 아래의 `request`에는 위 형식의 Python 딕셔너리를 넣습니다. `jev_script`는 복사한 스크립트의 실제 경로로 바꿉니다.

```python
import json
from pathlib import Path
import subprocess
import sys

jev_script = Path("/absolute/path/to/jev.py")  # Windows 예: Path("C:/tools/jev.py")
request = {
    "state": {"message": "중복 결제를 환불해 주세요."},
    "questions": {
        "refund": {"type": "noul", "instructions": "`message`에서 환불을 요청하는가?"}
    },
}
completed = subprocess.run(
    [sys.executable, str(jev_script)],
    input=json.dumps(request, ensure_ascii=False),
    encoding="utf-8", capture_output=True,
)
if completed.returncode != 0:
    raise RuntimeError(completed.stderr)
result = json.loads(completed.stdout)
print(result["answers"]["refund"]["noul"])
```

에이전트에는 이 설명서와 `jev.py`의 실제 위치를 알려 주세요. 에이전트는 상황별 자료와 질문을 구성하고 CLI를 호출한 뒤, 종료 코드와 JSON을 읽어 다음 행동을 정하면 됩니다. 호출 방법과 무관하게 필요한 맥락과 판단 기준은 매번 요청에 포함해야 합니다.

## 모델과 오류 처리

모델 선택의 우선순위는 `--model` → 통합 요청의 `model` → `TYPESAFE_DEFAULT_MODEL` 환경변수 → `jev-latest`입니다. 같은 모델 버전으로 재현해야 할 때는 [현재 모델 목록](https://docs.typesafe.ai/models)에서 확인한 버전을 지정하세요.

```sh
python jev.py --input examples/request.json --model jev-latest --timeout 60 --retries 2
```

`--timeout`은 소켓 연결·읽기 작업의 제한 시간이며 기본 60초입니다. 전체 프로세스의 절대 종료 시간을 뜻하지 않습니다. 전체 작업 시간 제한이 필요하면 호출한 프로세스에서 별도로 설정하세요.

`--retries`는 최초 시도 이후 추가 시도 횟수로, 기본 2회이며 0~10을 허용합니다. HTTP 429·500·502·503·504·529에만 재시도합니다. 서버의 `Retry-After` 또는 `retry-after-ms`를 우선 사용하고, 없으면 0.5초부터 지수적으로 기다리되 회당 8초를 넘지 않습니다. 서버가 30초를 넘는 대기를 요구하면 자동 재시도를 종료하고 오류를 반환합니다. 서버가 지시한 시간보다 일찍 재시도하지 않습니다.

연결 중단·시간 초과·응답 형식 오류는 서버의 처리 완료 여부가 불분명할 수 있어 자동 재시도하지 않습니다. 호출자가 재실행하면 별도 요청으로 처리될 수 있습니다. HTTP 오류도 재시도할 때마다 서버에 새로운 요청을 보내므로, 재시도를 원하지 않으면 `--retries 0`을 지정하세요.

오류는 표준오류에 다음 형태의 JSON으로 반환하며 정상 결과를 출력하지 않습니다. API 키 값은 HTTP·네트워크 오류 메시지에서 가립니다.

```json
{"error":{"kind":"http","message":"HTTP 401: ...","status":401}}
```

| 종료 코드 | `error.kind` | 의미와 다음 행동 |
|---|---|---|
| 0 | 해당 없음 | 정상 결과, 요청 검사 또는 도움말 출력 성공 |
| 2 | `input` | 입력 파일·JSON·인자·질문 형식을 고친 뒤 재실행 |
| 2 | `configuration` | 실행 프로세스의 `TYPESAFE_API_KEY` 설정 확인 |
| 1 | `http` | `status`와 메시지 확인. 401은 키, 422는 서버가 지적한 요청 필드를 확인 |
| 1 | `network` | 인터넷·인증서·프록시·시간 제한을 확인한 뒤 재실행 여부 판단 |
| 1 | `response` | 성공 응답이 계약을 충족하지 않음. 서비스 상태와 API 변경 여부 확인 |
| 1 | `io` | 입출력·문자 인코딩 실패. 파일·파이프 환경 확인 |
| 130 | `interrupted` | 호출자가 실행을 중단함 |

알 수 없는 요청 필드, 중복 JSON 키, 비표준 수치인 NaN·Infinity는 오류로 처리합니다. 서비스 주소는 공식 HTTPS 주소로 고정하며 리다이렉트는 따라가지 않습니다. 회사 프록시와 인증서가 필요한 환경에서는 Python의 표준 HTTPS 환경을 설정하세요. 인증서 검증을 끄는 옵션은 없습니다.

## 검증과 공식 문서

외부 서비스 호출 없이 회귀 검사를 실행하려면 다음 명령을 사용합니다. 테스트 역시 표준 라이브러리만 사용하며 로컬 HTTP 서버를 잠깐 실행합니다.

```sh
python test_jev.py
```

Windows의 Python 3.12.10에서 파일·표준입력·한글·구조화된 질문·오류·제한된 재시도와 실제 HTTP 리다이렉트 차단을 검사했습니다. 실제 Jev API에서도 포함된 세 질문 예제를 호출해 응답을 확인했습니다. 이 표본 호출은 도메인별 판단 정확도 평가가 아닙니다. Linux는 이 호스트의 WSL 가상화 기능 부재로 실행하지 못했고, macOS와 다른 Python 버전에서도 아직 실행 검증하지 않았습니다.

API와 질문 계약은 2026-09-22 확인한 다음 공식 문서를 기준으로 합니다.

- [HTTP API](https://docs.typesafe.ai/api)
- [질문 유형과 일괄 호출](https://docs.typesafe.ai/primitives)
- [구조화된 질문과 기준](https://docs.typesafe.ai/primitives/advanced)
- [신뢰도 해석](https://docs.typesafe.ai/confidence)
- [독립 질문을 묶는 예제](https://docs.typesafe.ai/cookbooks/parallel_questions)
