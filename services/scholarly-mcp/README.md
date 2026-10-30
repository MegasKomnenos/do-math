# Scholarly MCP

학술자료를 검색하고 서지·초록·원문·보충자료를 확보하는 로컬 MCP(Model Context Protocol) 서버입니다. MCP 클라이언트가 다섯 도구를 호출하면 서버는 선택한 자료원을 조회하고, 확보한 파일을 로컬에 보존합니다. 큰 결과는 자료 참조(`scholarly://artifact/…`)로 반환하며 필요한 부분을 다시 읽을 수 있습니다.

**이 README가 서비스의 공식 진입점입니다.** 처음 사용하는 사람은 아래 설치와 호출 순서를, 구현을 살펴보는 사람은 [개발 안내](docs/DEVELOPMENT.md)를 읽으세요.

| 알아볼 내용 | 문서 |
|---|---|
| 자료원별 지원 기능과 제한 | [지원표](docs/SUPPORT.md) |
| 호출 인자·결과 상태·추출 형식·자료원별 상세 설명 | [사용 안내](docs/USAGE.md) |
| 코드 구성·검증·데이터 관리 | [개발 안내](docs/DEVELOPMENT.md) |

## 지원 범위

등록 자료원은 49개입니다. 공개 API·공개 웹·경북대학교 KUDOS 기관 접근을 자료원별로 사용합니다. 48개 자료원은 지원 범위가 일부인 `partial`, Unpaywall은 사용을 보류한 `deferred`입니다. 이 표지는 개별 요청의 성공 여부와 다릅니다. 정확한 검색 문법과 확보 가능한 형식은 실행 중인 서버의 `describe_source`가 제공합니다.

한 호출은 지정한 자료원에서 끝납니다. API 실패를 이유로 브라우저나 다른 자료원으로 자동 전환하지 않습니다. 서버는 자료를 보존하고 기계적으로 추출하며, 논문의 학술적 가치 판단과 이미지 의미 판독은 호출자가 맡습니다. 기관 구독·사이트 접근 제한·형식 미제공 때문에 일부 구성요소만 회수될 수 있습니다.

## 설치와 실행

다음 명령은 **저장소 루트에서 Windows PowerShell로** 실행합니다. Python과 pip가 필요합니다. 의존성 버전은 [requirements.txt](requirements.txt)에 고정되어 있습니다. 브라우저를 사용하는 자료원에는 Firefox 또는 호스트의 Google Chrome이 필요하며, 어댑터가 사용할 브라우저를 선택합니다. 이 저장소의 실행·검증 기준 환경은 Windows입니다.

```powershell
python -m venv services/scholarly-mcp/.venv
& services/scholarly-mcp/.venv/Scripts/python.exe -m pip install -r services/scholarly-mcp/requirements.txt
& services/scholarly-mcp/.venv/Scripts/python.exe -m playwright install firefox
& services/scholarly-mcp/.venv/Scripts/python.exe services/scholarly-mcp/server.py --help
```

설치 명령이 실패하면 오류를 해결한 뒤 해당 단계부터 다시 실행합니다. 마지막 명령이 `--data-dir`와 `--credential-root`를 표시하면 서버 진입점을 실행할 수 있습니다.

MCP 클라이언트에는 전용 Python을 실행 명령으로, `server.py`의 **절대 경로**를 인자로 등록합니다. 다음은 저장소가 `C:\math`인 경우의 JSON 설정 예입니다. 다른 위치에 복제했다면 두 경로를 실제 위치로 바꾸세요. 클라이언트가 이 형식을 지원하는 설정 파일에 `scholarly` 항목을 넣습니다.

```json
{
  "mcpServers": {
    "scholarly": {
      "command": "C:/math/services/scholarly-mcp/.venv/Scripts/python.exe",
      "args": ["C:/math/services/scholarly-mcp/server.py"]
    }
  }
}
```

서버는 stdio로 통신합니다. 직접 실행하면 MCP 클라이언트의 입력을 기다리며, 웹페이지나 HTTP 포트를 열지 않습니다. stdout은 프로토콜 메시지 전용입니다. 설정이나 Python 구현을 변경한 뒤에는 클라이언트에서 새 서버 프로세스를 시작해야 합니다.

| 시작 옵션 | 기본값과 용도 |
|---|---|
| `--data-dir` | 서비스의 `data/`. 확보한 파일과 manifest를 저장합니다. |
| `--credential-root` | 저장소 루트의 `.credentials/`. 기관 자격과 브라우저 인증 상태를 읽고 보존합니다. |

공개 자료원 사용에는 KUDOS 자격이 필요하지 않습니다. 기관 자료원을 사용할 때는 보호된 자격 디렉토리의 `kudos.md`에 `ID: …`와 `PW: …`를 각각 한 줄로 둡니다. 자격값을 도구 인자나 버전 관리 문서에 넣지 마세요. 기관 자격이 없으면 해당 접근은 `restricted`로 반환됩니다. 별도 실행의 인증 상태를 분리하려면 `--credential-root`를 지정합니다.

DjVu 텍스트·이미지 추출이 필요하면 MSVC C++ 컴파일러, Windows SDK, Git이 설치된 호스트에서 아래 명령을 추가로 실행합니다. 고정된 DjVuLibre 소스를 빌드하며 실행 도구·라이선스·해시는 `data/tools/djvulibre/runtime/`에 보존합니다. 이 위치는 `--data-dir`로 바뀌지 않습니다.

```powershell
& services/scholarly-mcp/.venv/Scripts/python.exe services/scholarly-mcp/setup_djvu.py
```

## 첫 호출

다음은 클라이언트가 보내는 도구 이름과 JSON 인자입니다. `search` 예시는 공개 Crossref 자료원을 사용합니다. 검색 결과는 시점에 따라 달라집니다.

| 순서 | 도구 | 인자와 다음 행동 |
|---|---|---|
| 1 | `list_sources` | `{}` — 자료원과 구현 상태를 확인합니다. |
| 2 | `describe_source` | `{"source":"crossref"}` — 문법과 지원 범위를 읽습니다. |
| 3 | `search` | `{"source":"crossref","query":"P versus NP","limit":5}` |
| 4 | `extract` | `{"ref":"검색 결과의 records.ref 값","count":5}` — 실제 반환된 참조로 바꾸고 레코드에서 대상을 선택합니다. |
| 5 | `fetch` | `{"source":"crossref","target":"선택한 레코드의 DOI","parts":["metadata"]}` — 실제 DOI로 바꿉니다. |

`fetch`의 `parts`를 생략하면 `metadata`, `abstract`, `fulltext`를 요청합니다. 다른 형식은 `describe_source`에서 지원 여부를 확인한 뒤 명시합니다. `start`는 0부터 세며 검색의 `limit`는 요청 건수, 추출의 `count`는 레코드·줄·쪽 등의 수입니다.

매 호출의 `status`를 확인하세요. `selection_required`이면 후보를 읽고 정확한 식별자로 다시 요청합니다. `partial`이면 `components`의 개별 상태를 확인하고 이미 받은 자료를 사용할 수 있습니다. `restricted`는 접근 제한, `error`는 실행·통신 등의 실패입니다. `total: null`은 전체 건수를 알 수 없다는 뜻입니다. 상태 전체와 형식별 추출 방법은 [사용 안내](docs/USAGE.md)에 있습니다.

## 검증

외부 자료원을 호출하지 않는 회귀 검사와 별도 SDK stdio 서버 검사는 다음 명령으로 실행합니다.

```powershell
& services/scholarly-mcp/.venv/Scripts/python.exe -m unittest discover -s services/scholarly-mcp/tests -p 'test_*.py'
```

이 검사의 성공은 외부 사이트의 현재 접근 가능성을 보증하지 않습니다. 실서비스 검증은 [개발 안내](docs/DEVELOPMENT.md)의 별도 절차를 따릅니다.
