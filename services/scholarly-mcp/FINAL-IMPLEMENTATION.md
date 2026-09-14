# 학술자료 MCP 최종 구현 정리

2026-09-14 KST 기준, 기존 scholarly-mcp 범위의 구현 통합과 partial 재검토에서 확인한 수리를 완료했다. 최종 로컬 회귀 검사 639개가 38.080초에 통과했다. 이번 마감 점검에서는 추가 코드 결함을 발견하지 않았으며 문서의 최신 상태와 읽기 경로를 정리했다. 새로운 자료원 지원은 추가하지 않았다.

등록 자료원은 49개다. `registry.py`를 직접 읽어 48개 `partial`, Unpaywall 1개 `deferred`, `pending` 0개와 자료원별 사용 설명의 존재를 확인했다. `partial`은 각 자료원에서 지원하는 기능이 일부라는 구현 표지다. 모든 문헌·형식·조건 조합을 구현하거나 검증했다는 뜻은 아니다. 개별 요청의 `partial`은 실제 회수한 구성요소의 상태로 별도 판단한다.

## 제공하는 기능

| 영역 | 최종 구현 |
|---|---|
| 공통 인터페이스 | 로컬 stdio MCP의 `list_sources`, `describe_source`, `search`, `fetch`, `extract` 다섯 도구 |
| 자료원별 검색·회수 | 각 자료원의 원 검색 문법·필드·필터·식별자를 사용한다. 지원하는 검색 창·내보내기·문헌·첨부 형식은 `describe_source`에 명시한다. |
| 접근 경로 | 자료원별로 별도 API 자격 없이 호출하는 공개 API, 확인한 공개 웹 경로, KUDOS 기관 경로를 사용한다. 한 호출은 지정 자료원 안에서 끝난다. |
| 자료 보존 | 큰 결과를 artifact와 출처 manifest로 보존하고 SHA-256을 대조한다. 기회수 자료와 후속 실패를 함께 반환한다. 정제·정규화한 표현과 원 파일 바이트를 구별한다. |
| 기계적 추출 | JSON·XML·HTML·인용문·표·PDF·DjVu·이미지·압축 내부 파일 등 구현된 형식을 선택·범위 지정하여 읽는다. 문헌의 학술적 판단과 이미지 의미 판독은 호출 AI가 맡는다. |
| 상태·오류 | 성공, 부분 결과, 접근 제한, 미제공, 선택 필요, 실행 오류를 구별한다. 원 HTTP 오류의 정제한 응답과 재시도 정보를 근거로 보존한다. |

실제 사용은 [README](README.md)의 호출 예와 설치 절차를 따른다. 49개 자료원별 기능은 [지원표](SUPPORT.md), 코드의 입력 계약은 `describe_source`가 제공한다. 구현의 주요 진입점은 `server.py`, 자료원 계약은 `registry.py`, 보존·추출은 `scholarly.py`, 접근·자료원 처리는 개별 어댑터에 있다.

## partial 재검토에서 완료한 수리

| 문제 | 최종 동작과 근거 |
|---|---|
| AMS Title OR가 논리 합집합을 보존하지 않음 | 여러 Title 조건의 OR를 기본 문자열로 변환하지 않고 지원 범위 밖으로 반환한다. 실제 화면의 입력·결과와 빠진 문헌을 대조한 반례가 근거다. 단일 Title/Author, 기존 Author OR, 검증된 서로 다른 필드 AND는 유지한다. |
| ScienceDirect 새 세션의 Preface 후보 누락 | 원 메타데이터의 유효한 ISSN·ISBN으로 제목 후보를 좁혀 정확한 PII를 대조한다. 검색 행과 상세 PDF 경로가 모두 실패하면 두 실패를 보존한다. 대상 선택 수리와 PDF 구독 권한은 구별한다. |
| API HTTP 오류에서 원 응답 근거 소실 | 응답 본문·HTTP 상태·요청 방식·재시도 헤더를 정제한 `provider_error_response` artifact에 보존한다. 근거 저장 실패가 원 HTTP 오류를 덮어쓰지 않으며 자동 재시도를 추가하지 않는다. |

앞선 24개 CLI 과제의 통합 및 자료원별 수리는 [감사표](AUDIT-MATRIX.md), 위 세 수리와 실제 UI 과정은 [partial 재검토](PARTIAL-REVIEW.md)에 기록했다. 조사 과정에서 얻은 외부 원고, 역사 첨부, 도서 목록, Software Heritage 재구성 압축물은 원 서비스 기능의 복구와 구별한다.

## 남은 제한의 최종 처리

기존 조사에서 확인한 다음 조건은 유지한다. 이 목록은 실행을 대기하는 개발 작업 목록이 아니다. 구체적인 대상·시점·화면·원 응답·재개 조건은 [후속 인계](CONTINUATION.md)와 [partial 재검토](PARTIAL-REVIEW.md)에 있다.

| 구분 | 해당 범위와 처리 |
|---|---|
| 검증된 의미 보존 경로가 없음 | AMS의 나머지 Boolean·equals·원자 매핑은 지원하지 않는다. UI의 일반 문자열 검색과 구조화된 논리식을 혼동하지 않는다. |
| 접근권한·다운로드·export 문제 | SIAM 대상 출판사 PDF, ScienceDirect 두 대상 PDF, Oxford 검색별 title export, JSTOR 대상 영상 다운로드, De Gruyter 현행 첨부 링크는 확보 성공으로 표시하지 않는다. 일부 대체 파일 확보는 별도로 기록했다. |
| 해당 형식·필드 미제공 | T&F 두 editorial 초록, Springer 대상 HTML 본문, EuDML 대상 NLM 전문, CORE 대상 indexed fullText, Semantic Scholar Graph 원문 파일은 기존의 미제공 판정을 유지한다. 다른 경로에서 받은 PDF와 구별한다. |
| 제공자 상태·역사 관계 미확정 | SWH 원 Vault 작업은 마지막 확인에서 `new`였다. Figshare 과거 v6는 17개 표기와 16개 공개 구성원의 불일치를 유지하며 후보를 확정 구성원으로 삽입하지 않는다. |
| 사용자 결정으로 제외 | Unpaywall, 별도 Scopus 개인 계정의 export, 자격이 필요한 GitHub 전역 code search는 보류한다. |

추가 자료원·외부 링크 탐색은 종료했다. Google 도서 지원은 추가하지 않았다. 공급자 내부 원인이나 모든 외부 경로의 부재를 확정한 것으로 해석하지 않는다.

## 최종 검증과 실행 상태

저장소 루트에서 전용 Python으로 실행했다.

```powershell
& services/scholarly-mcp/.venv/Scripts/python.exe -m unittest discover -s services/scholarly-mcp/tests -p 'test_*.py'
```

결과는 **639개, 실패·오류·건너뜀 없이 통과, 38.080초**다. 로그는 로컬 `data/final-implementation-tests-20260914.txt`에 보존했다. 이 검사는 응답 대역을 이용한 회귀와 실제 별도 SDK stdio 서버의 도구 조회·파일 추출·자료 읽기 계약을 포함한다. 이번 마감에서 실서비스를 다시 호출하거나 전체 사이트 UI를 다시 탐색하지 않았다. 실서비스 성공 주장은 [검증 기록](VALIDATION.md)의 개별 입력·시점에 한정한다.

등록되어 실행 중인 사용자의 MCP·Codex·브라우저는 재시작하지 않았다. 새 서버 프로세스는 현재 구현을 읽는다. 기존 프로세스에 수정 사항이 자동 반영되었다고 보장하지 않는다. `data/`와 비공개 원시 근거는 로컬 자료이며 Git에 배포하는 최종 상태는 이 문서와 연결 문서에 보존한다.
