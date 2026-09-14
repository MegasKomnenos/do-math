# 개발과 유지 관리

[공식 진입점](../README.md)에서 서비스 개요와 실행 방법을 확인할 수 있습니다. 이 문서는 구현을 읽거나 검증하고 로컬 파일을 관리하는 개발자를 위한 안내입니다.

## 디렉토리와 코드

```text
scholarly-mcp/
├── README.md              공식 진입점과 빠른 시작
├── server.py              stdio MCP, 도구 등록, 어댑터 연결
├── registry.py            자료원 정의와 describe_source 입력 계약
├── scholarly.py           자료 보존, 정제, 추출과 오류 모델
├── *_adapters.py          공통 API·브라우저 접근 구현
├── 기타 Python 모듈       자료원별 처리와 형식별 추출
├── requirements.txt       고정 Python 의존성
├── setup_djvu.py          선택적 DjVu 도구 빌드
├── docs/
│   ├── USAGE.md           상세 사용 설명
│   ├── SUPPORT.md         자료원별 지원표
│   ├── DEVELOPMENT.md     개발과 유지 관리
│   └── history/           검증·조사·인계 기록과 과거 dispatch
├── tests/
│   ├── test_*.py          회귀 검사와 SDK stdio 계약 검사
│   ├── fixtures/          검사가 읽는 고정 입력
│   └── live/              외부 자료원에 접속하는 검증 스크립트
├── data/                  Git에서 제외하는 로컬 데이터
└── .venv/                 Git에서 제외하는 전용 Python 환경
```

`server.py`는 `registry.py`의 자료원 계약과 개별 어댑터를 연결합니다. `search`와 `fetch`는 하나의 worker에서 실행되어 브라우저 세션을 소유합니다. `ArtifactStore`는 보존 파일과 출처 manifest를 관리하고, `extract_artifact`는 형식별 추출을 선택합니다. `api_adapters.py`, `browser_adapters.py`, `native_browser.py`를 읽은 뒤 관심 있는 자료원 모듈로 이동하면 호출 경로를 따라갈 수 있습니다.

구현 모듈은 서비스 루트의 동일한 import 경로를 사용합니다. 새 자료원이나 인자를 변경할 때는 실제 구현과 `registry.py`의 사용 계약, 지원표를 함께 대조합니다. 구체적인 과거 실서비스 관측은 `docs/history/`에 보존합니다.

## 검증 실행

저장소 루트에서 README의 회귀 검사 명령을 실행합니다. `test_mcp.py`는 별도 서버 프로세스를 띄워 다섯 도구의 스키마와 파일 추출·자료 읽기를 검증합니다. `fixtures/`는 재현 입력이므로 임시 파일로 삭제하지 않습니다.

실서비스 검증이 필요한 경우에는 먼저 `tests/live/`의 해당 스크립트를 읽고 대상, 필요한 자격, 출력 위치를 확인합니다. 이 스크립트들은 네트워크·기관 로그인·다운로드를 수행하며 특정 문헌과 시점에 맞춘 검증 조건을 포함합니다. 일반 회귀 검사에는 포함되지 않습니다. 대표 흐름은 다음과 같습니다.

```powershell
& services/scholarly-mcp/.venv/Scripts/python.exe services/scholarly-mcp/tests/live/live_workflow.py --source crossref
```

성공 여부는 스크립트의 종료 코드와 보존한 보고서를 함께 확인합니다. 실패하면 보고서의 원 응답과 현재 `describe_source` 계약을 대조한 뒤 수정 또는 재검증 범위를 정합니다. 응답 대역 검사와 실서비스 관측을 같은 검증으로 기록하지 않습니다.

## 로컬 데이터 관리

| 경로 | 역할과 보존 기준 |
|---|---|
| `data/blobs/`, `data/manifests/` | 원 파일과 출처·해시·자료 참조. 기존 artifact를 계속 읽으려면 함께 보존합니다. |
| `data/tools/` | DjVu 빌드와 실행 도구. `runtime/`은 추출에 필요하며 라이선스·manifest도 함께 보존합니다. |
| `data/validation/` | 실서비스 검증 보고서. 추적 문서의 주장을 뒷받침하는 로컬 근거입니다. |
| `data/access-research/`, `data/partial-investigation-20260914/`, `data/ui-walkthrough-20260914/`, `data/dispatch/`, `data/observations/` | 과거 조사 원자료. 문서와 내부 파일의 경로 관계를 유지합니다. |
| `data/research/` | 과거에 data 루트에 흩어졌던 일회성 조사 스크립트·응답·로그. 역사 자료이며 실행 지원 대상이 아닙니다. |
| `data/codex-app-schema/`, `data/codex-reload-inspect/` | 과거 도구 조사 자료. 서비스의 실행 의존성에 포함되지 않습니다. |
| `data/research/retired/` | 사용하지 않는 조사 환경과 캐시·GPU 로그의 보관 위치. 자동 승인 정책이 삭제를 차단해 보관했으며 디스크 공간은 회수하지 않았습니다. JSTOR 조사 환경의 패키지 버전은 `data/research/jstor-audio-requirements.txt`에 있습니다. |
| `.venv/` | 현재 서버가 사용하는 Python 환경. 재설치는 requirements에서 수행합니다. |
| `__pycache__/`, `*.pyc`, `NVIDIA Corporation/umdlogs/` | 재생성되는 캐시·GPU 로그. 보존 자료로 사용하지 않습니다. |

`data/` 전체를 캐시로 간주하면 기존 자료 참조와 검증 근거가 사라집니다. 정리할 때는 파일 역할과 참조를 먼저 확인합니다. 사용자별 인증 정보와 브라우저 상태는 서비스 밖의 보호된 `.credentials/` 또는 지정한 `--credential-root`에 있습니다.

## 기록의 위치 변경

2026-09-14 구조 정리에서 기존 루트 README의 상세 내용은 `docs/USAGE.md`로, `SUPPORT.md`는 `docs/SUPPORT.md`로 이동했습니다. 나머지 루트 조사·검증·인계 문서는 같은 이름으로 `docs/history/`에 있으며, 기존 `dispatch/`는 `docs/history/dispatch/`에 있습니다. `tests/live_*.py`는 `tests/live/live_*.py`로 이동하고 서비스 루트 계산을 수정했습니다.

과거 기록에 남은 `data/<파일명>`의 단일 파일 경로는 `data/research/<파일명>`에서 찾을 수 있습니다. 디렉토리 아래에 있던 원자료 경로는 유지했습니다. 과거 조사 스크립트의 절대 경로나 실행 가정은 당시 환경의 기록이며, 재실행하려면 현재 경로·자격·대상을 먼저 검토해야 합니다.
