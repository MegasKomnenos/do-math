학술자료 검색·확보용 로컬 stdio MCP 서버다. 공통 도구와 자료원 어댑터를 구현·검증 중이며, 전체 자료원에 대한 구현 완료를 선언한 상태는 아니다. 확정 요구사항은 [구현 인계](../../학술자료-MCP-구현-인계.md)를 따른다.

2026-09-09 사용자 교정에 따라 **공개 API는 별도 API 이용 자격 없이 호출할 수 있는 API**를 뜻한다. 별도 키·승인·계약을 요구하는 API는 구현 경로에서 제외한다. 그런 공개 API가 없는 인증 자료원은 KUDOS 로그인 → 검색 → 학술DB → 해당 바로가기 → 기관 프록시의 Playwright 경로를 사용한다. 어댑터 경로는 개발 시 정하며, 실행 중 API 오류를 이유로 브라우저로 전환하지 않는다. 기관 로그인 정보는 보호된 `.credentials/kudos.md`에서 서버가 직접 읽는다.

서버의 도구는 다음 다섯 개다. 자료의 연구상 가치와 다른 자료원의 추가 탐색 여부는 호출 AI가 결정한다.

| 도구 | 용도 |
|---|---|
| `list_sources` | 선정 자료원과 구현 상태를 조회한다. `pending`은 개발이 남았다는 뜻이다. |
| `describe_source` | 실제 입력 문법·필드·옵션·export·확보 범위·예제를 읽는다. |
| `search` | 지정 자료원에서 호출자가 작성한 검색식과 조건으로 검색한다. |
| `fetch` | 지정 자료원에서 자료의 정확한 식별자·링크·대상을 회수한다. 지원하는 대상 표기는 자료원 설명에 있다. |
| `extract` | 보존 자료에서 레코드·필드·줄·쪽·파일을 기계적으로 추출한다. |

일반적인 호출 순서는 다음과 같다.

1. `list_sources()`에서 사용할 자료원의 구현 상태를 확인한다.
2. `describe_source(source="mathscinet")`를 읽는다.
3. `search(source="mathscinet", query='ti:("P versus NP")', limit=5, export="bibtex")`를 호출한다.
4. 반환된 `records.ref`에 `extract(ref=…, fields=["mrnumber", "titles"], count=5)`를 호출해 대상을 선택한다. `export.ref`도 `extract`로 읽을 수 있다.
5. `fetch(source="mathscinet", target="MR2733384", parts=["metadata", "supplementary"])`로 서지와 리뷰 PDF를 받는다. MathSciNet의 리뷰 PDF는 논문 전문으로 표시하지 않는다. 논문 전문은 그 출판사를 별도 `source`로 지정한다.

`start`는 0부터 센다. `limit`는 검색에서 요청할 레코드 수이고, `count`는 추출할 레코드·줄·쪽·파일 수다. 자료원 고유의 페이지 제한은 `describe_source`가 정한다. `received`는 해당 결과에 보존한 레코드 수다. `total=null`은 자료원이 전체 검색 건수를 제공하지 않은 경우이며 0건을 뜻하지 않는다. 큰 결과는 파일로 보존하고 모델에는 참조·건수·작은 미리보기를 보낸다. 원자료 전체를 다시 받을 때는 같은 `scholarly://artifact/…` URI에 MCP `resources/read`를 호출한다.

자료 참조는 manifest와 파일의 SHA-256으로 검사한다. 같은 바이트를 서로 다른 자료원에서 얻어도 출처 manifest는 분리된다. 저장된 자료는 서버 재시작 뒤에도 회수할 수 있다. API JSON의 표현 정규화와 인증 정보 정제, 화면 HTML의 실행 코드 제거는 보존 사본에 적용된다. PDF·이미지·압축 파일은 원 바이트로 보존한다.

추출에서 JSON `selection`은 JSON Pointer다. 예를 들어 `/0/fields/cr`은 첫 Web of Science 레코드의 인용문헌 필드다. HTML은 CSS 선택자, XML은 ElementTree가 지원하는 XPath 부분집합을 사용한다. PDF는 원 텍스트 레이어를 추출하고, `render=true`이면 해당 쪽의 이미지도 보존한다. 이미지 ref를 다시 `extract`에 주면 MCP 이미지 내용으로 전달한다. 이미지 의미 판독과 OCR 교정은 서버가 수행하지 않는다. ZIP·tar 계열은 파일 목록을 반환하며 `selection`에 목록의 정확한 파일 이름을 주면 해당 바이트를 별도 자료로 보존한다. 압축 파일의 경로를 작업 디렉터리에 풀지 않는다. 원 저장소 파일과 압축 파일에서 꺼낸 파일은 원 바이트를 유지한다.

| 상태 | 의미 |
|---|---|
| `ok` | 요청한 해당 작업이 성공했다. 전체 프로젝트 완료나 내용의 학술적 타당성을 뜻하지 않는다. |
| `partial` | 요청 내용 중 일부를 회수했다. `components`의 각 상태를 확인한다. |
| `not_found` | 지정 자료원·대상·검색 창에서 결과가 없었다. 다른 자료원의 부재로 확장하지 않는다. |
| `restricted` | 인증·접근 제어·접근 확인 화면 때문에 해당 경로를 사용할 수 없었다. |
| `error` | 실행·통신·파싱·범위 대조 등이 실패했다. `code`와 재시도 안내를 확인한다. |
| `not_implemented` | 해당 기능의 개발이 남았다. 자료원 자체의 기능 부재와 다르다. |
| `unsupported` | 명시한 인터페이스나 공개 접근 범위에서 제공하지 않는 기능이다. 상세 이유를 함께 읽는다. |
| `selection_required` | 대상이 모호하다. 보존한 후보를 읽고 정확한 식별자로 다시 요청한다. |

설치는 저장소 루트에서 다음과 같이 한다. 현재 호스트에는 전용 환경을 설치했고 `.mcp.json`과 `.codex/config.toml`의 `scholarly` 항목에 등록했다. 기존 `dag-measure` 등록은 보존했다. 새 MCP 세션이 이 설정을 읽는다.

```powershell
python -m venv services/scholarly-mcp/.venv
& services/scholarly-mcp/.venv/Scripts/python.exe -m pip install -r services/scholarly-mcp/requirements.txt
& services/scholarly-mcp/.venv/Scripts/python.exe -m playwright install firefox
& services/scholarly-mcp/.venv/Scripts/python.exe services/scholarly-mcp/server.py
```

Chromium 어댑터는 호스트에 설치된 Chrome을 사용한다. 자료원별로 검증한 브라우저를 서버가 선택하며 호출 AI가 지정하지 않는다. stdio의 stdout은 MCP 메시지 전용이고 진단은 stderr로 보낸다.

오프라인 계약 검사는 `tests/test_core.py`, `tests/test_api.py`, `tests/test_browser.py`, `tests/test_mcp.py`를 전용 Python으로 각각 실행한다. `test_mcp.py`는 실제 SDK 클라이언트와 별도 서버 프로세스로 stdio·도구 조회·파일 추출·자료 읽기를 확인한다. 실서비스 흐름은 `tests/live_workflow.py --source <자료원>`으로 실행하며 지원하는 검증 시나리오는 그 파일에 있다. 오프라인 응답 대역의 통과는 실서비스 통과로 세지 않는다.

현재 실서비스 근거는 로컬 `data/validation/`에 있다. MathSciNet·Web of Science·ECCC·ACM은 실제 MCP 클라이언트 흐름을 수행했고, Crossref·arXiv·zbMATH는 MCP 검색·추출을 수행했다. GitHub의 고정 커밋 파일, Numdam의 JATS·PDF, Software Heritage의 origin 검색·조회·cursor 순회는 어댑터 직접 호출로 확인했다. 각 기록은 해당 시점·입력·호스트의 관측이며 다른 자료원이나 모든 기능에 복제하지 않는다.

ACM 인용문 생성은 실제 검색 UI가 수신한 원 서지·CSL 스타일·locale과 자료원이 제공한 citeproc 처리기를 사용한다. 처리기는 외부 통신을 막은 별도 렌더 페이지에서 실행한다. 사이트의 인용문 미리보기 초기화 오류가 자료 확보를 막지 않으며, 서버에 문헌을 해석하는 AI를 넣지 않는다. 서지 응답·처리기·생성 파일의 참조를 함께 보존한다.

`.venv/`와 `data/`는 Git에서 제외한다. 재현에 쓰는 작은 공개 응답은 `tests/fixtures/`에 보존한다. 실행 자료를 다른 환경으로 옮길 때는 `data/` 전체와 해시 검사를 함께 보존한다. 인증 상태는 `.credentials/scholarly-mcp/`에 따로 두며 자료·로그·커밋에 포함하지 않는다. 전체 선정 범위와 아직 조사·개발 중인 자료원은 `registry.py`와 `list_sources`에 남아 있다.
