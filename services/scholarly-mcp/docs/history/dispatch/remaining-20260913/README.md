# 미해결 기능별 Codex CLI 파견

재검토는 [사용자 세 기준](USER-CRITERIA.md)을 적용했다. [과제별 연결](criteria-tasks.json)은 오류 전후 판독 누락 N27종·B15사례를 담당 과제에 연결한다. 처음에는23개 CLI 재개와 Springer 직접 검토로 시작했고 이후24개 과제 및 root가 찾은 추가 오류를 대조·수리했다. 원본 통합과 현행 조건은 [후속 인계](../../CONTINUATION.md)와 [최종 검토](FINAL-REVIEW.md)를 따른다. 최대8개·동일 자료원 순차 실행 원칙은 유지하며, CLI completed/exhausted만으로 root 검토 통과를 대신하지 않는다.

새 재개의 개별 결과는 각 실행 폴더의 criteria-review.json에 기록한다. 공식 문서나 정상 문헌의 이미지로 실패 API 요청의 전후를 대신하지 않으며, 로컬 진단 도구 화면은 원 사이트 UI와 구별한다. 기술 문제는 수리하고 재실행한다. 이미 거부된 KNU IdP 로그인은 다시 제출하지 않는다. 기존 검토 요청 목록은 review-requests-before-user-criteria-01.json에 보존했고 활성 목록은 과제당 최신 요청 하나만 둔다.

사용자 결정으로 보류한 Unpaywall, Scopus 개인 계정 내보내기, 인증이 필요한 GitHub 전역 코드 검색은 제외한다. 나머지 실패 기능과 미확정 검증을24개의 독립 임무로 나눴다. 앞 상태 설명의 묶음 항목은 개별 기능으로 분리했고, 지원표에 남아 있던 Springer HTML 음성 표본과 Figshare 과거 컬렉션 구성원도 포함했다. 자료원별로 이미 입증한 검색 결과 상한과 자료원의 역할 자체가 다른 기능은 실패 항목에 섞지 않았다.

다음 표는 최초 파견 시점의 문제 목록이다. 현재 상태표로 사용하지 않는다.

| ID | 개별 임무 | 기존 실패 또는 미확정 이유 |
|---|---|---|
| ams-expression | AMS 동적 고급 검색식 | 원 UI가 만든 식도 서버 null 오류 |
| siam-institution | SIAM 기관 구독 원문 | 프록시 진입 뒤 기관 인증·PDF 권한 미확인 |
| dblp-challenge | DBLP 공개 API | 접근 확인 재발 |
| semantic-scholar-rate | Semantic Scholar 공개 요청 | 최소 요청도429 |
| eudml-nlm | EuDML 단건 NLM | 응답 헤더 대기 시간초과 |
| core-indexed-text | CORE API 색인 전문 | 본문 대신 공개 API 제한 안내 |
| core-work-download | CORE work 다운로드 | 기존 표본404, 이후 표본의 전문 제거 확인 |
| core-output-download | CORE output 다운로드 | 장시간 무호출 대조 뒤에도429 |
| core-files01 | CORE files01 파일 | 특정 공식 색인 URL이522 |
| swh-vault | Software Heritage 특정 압축 작업 | new 상태와 원 URL404 |
| oxford-title-export | Oxford 대량 title-list export | CAPTCHA와 기능 범위 확인 필요 |
| jstor-video | JSTOR 동영상 다운로드 | 시험 표본의 원 제어 비활성 |
| degruyter-broken-supplement | De Gruyter 보충 ZIP | 현재 제어의 오래된 파일 URL404 |
| degruyter-citation | De Gruyter DOI 없는 자료의 citation | 자료원 ID 기반 export 존재 여부 확인 필요 |
| sciencedirect-export | ScienceDirect 일부 결과 export | 문헌 유형별 제어 부재 |
| sciencedirect-pdf | ScienceDirect 일부 문헌 PDF | PDF 제어 부재와 문헌 상태 구별 필요 |
| taylor-abstract | Taylor & Francis 초록 | 인용문 필드 누락과 문헌 초록 부재 구별 필요 |
| dblp-kg-tsv | DBLP KG TSV 자료형 | 원 JSON과 TSV의 RDF term 불일치 |
| siam-last-condition | SIAM52번째 검색 조건 | 문자열 보존은 확인, 의미 대조는 접근 오류 |
| numdam-date-only | Numdam 날짜 전용 검색 | 입력 전에 홈페이지 연결 실패 |
| ieee-media-flag | IEEE false Media flag | 실제 Media 제어를 놓치는지 미확정 |
| crossmark-semantics | Crossmark 정정·철회 필드 | 의미·방향·누락 범위의 전수 검증 미완료 |
| springer-html-negative | Springer 특정 구형 문헌 HTML | 기관 표시가 있으나 기존 본문 선택자 부재 |
| figshare-historical-members | Figshare 과거 컬렉션 구성원 | 과거 판본 metadata와 구성원 목록의 지원 차이 |

개별 계약은 [tasks.json](tasks.json), 공통 실행·판독·종료 계약은 [contract.md](contract.md)다. 각 세션에는 이 두 계약과 실제 사본·인증·보고 경로를 합친 독립 prompt.md를 전달한다. 스킬은 write-for-reader와 산문·AI 프롬프트·에이전트 채널·절차문·의도 발굴 참조를 읽고 적용했다.

## 실행과 상태

기준 코드는07b9c9c이며514개 검사를 통과한 상태다. 실행 루트는 C:/math다. 각 작업은 해당 커밋의 서비스 사본과 전용 KUDOS 인증·브라우저 상태 사본을 사용한다. 원본 코드·공유 인증·등록 MCP·다른 세션은 변경하지 않는다. 모델은 설치된 CLI에서 제공하는 gpt-5.6-sol, reasoning high다. 동시 실행은 최대8개이며 동일 자료원은 한 세션씩 실행해 요청 한도와 상태 간섭을 줄인다. 이8개는 완료 기준이나 전체 세션 수의 상한이 아니다.

현재 실행 폴더는 C:/math/services/scholarly-mcp/data/dispatch/20260913T021511Z다. INDEX.md는24개 파견문을 연결한다. state.json에는 작업별 실제 thread_id·PID·시도 수·상태가 있고, 각 작업 폴더에는 progress.json·실험 원장·직접 이미지 판독·최종 보고가 쌓인다. CLI 원 로그·원 HTML·signed URL·인증 사본은 .credentials/scholarly-mcp/probes/cli-dispatch 아래에만 저장한다.

```powershell
& services/scholarly-mcp/.venv/Scripts/python.exe services/scholarly-mcp/docs/history/dispatch/remaining-20260913/run.py status
```

queued는 아직 CLI 작업을 시작하지 않은 상태, running은 실행 중, resume_queued는 중단된 작업의 재개 대기다. thread_id가 없으면 모델 세션 시작 전에 실패한 것으로 구별한다. awaiting_review는 세션이 completed 또는 exhausted를 주장하고 필수 파일 검사를 통과했지만 주 세션의 내용 검토·통합은 아직 남았다는 뜻이다. 이를 구현 완료로 표시하지 않는다.

운영기는 정상 완료 파일이 없거나 incomplete로 반환된 작업을 같은 thread_id로 재개한다. --last로 다른 세션을 선택하지 않는다. 작업 시간·재개 횟수의 임의 상한으로 과제를 완료 처리하지 않는다. completed에는 실제 검증, exhausted에는 실행한 방법·남은 외부 조건·미시도 방법0의 근거를 요구한다. 화면 판독 보고뿐 아니라 실제 이미지 파일이 있어야 최종 검토 대상으로 넘어간다. 이 검사는 파일 존재의 기계 검사이며 내용의 진실성을 대신하지 않는다. 주 세션이 이미지·요청·원 파일·변경을 직접 대조한다.

사용자의 후속 지시로 동시 실행 수를4개에서8개로 늘렸다. 실행 한도는 limits.json에서 읽으며 다음 명령으로 갱신한다. 운영기를 교체할 때도 기록된 PID의 실행 파일과 해당 작업의 정확한 출력 경로를 명령줄에서 대조해 기존 CLI를 인계받는다. 신원이 맞지 않으면 중복 실행하지 않고 controller_recovery_required로 남긴다. 이번 변경에서는 기존4개의 PID·thread를 보존한 채 추가4개를 시작한 것을 확인했다.

```powershell
& services/scholarly-mcp/.venv/Scripts/python.exe services/scholarly-mcp/docs/history/dispatch/remaining-20260913/run.py limit --max-parallel 8
```

모델 세션이 시작되기 전 첫 CLI 구성에서 비활성 MCP 설정만 남겨 transport가 없다는 오류가 있었다. 원 설정을 수정하지 않고 파견 프로세스에 한정해 MCP 서버 목록을 빈 값으로 지정했다. 등록 MCP를 재시작하지 않았으며 각 작업은 자신의 사본 server.py로 검증한다.

후속 상태 점검에서 CLI resume가 최초 exec의 실행·쓰기 권한을 유지하지 않아 읽기 전용 환경에서 반복 중단되는 결함을 확인했다. 재개에도 이 작업에 이미 허용된 권한을 명시하도록 수정했으며, 자신의 output_dir에서 파일 읽기·쓰기 확인을 먼저 수행하게 했다. 일부 thread는 활성 turn의 출력 스키마와 충돌해 ActiveTurnOutputSchemaMismatch가 발생했다. 이 정확한 오류를 관측한 thread의 재개에서만 스키마 옵션을 생략하고 기존 JSON 반환 계약과 파일 검사를 유지한다. SWH·Crossmark의 같은 thread에서 실제 명령 실행 복구를 확인했다. 이 운영 오류를 자료원 접근 실패나 방법 소진으로 세지 않는다.

주 세션은 결과를 원본에 통합하기 전에 변경 범위·실험·실서비스 결과를 검토하고 영향받는 검사를 수행한다. 서로 같은 공통 파일을 수정한 사본은 차이를 대조해 통합하며 자동 덮어쓰기하지 않는다. 작업 사본과 보고를 보존하고, 원본 커밋·기억 결정화·푸시는 기존 commit-harness 계약을 따른다.

실제 이미지 열람의 rollout 대조와 종료판단 재검토는 [VISUAL-AUDIT.md](VISUAL-AUDIT.md)에 있다. 검토자가 실행폴더의 review-requests.json에 고유요청ID·task_id·prompt_path를 기록하면 운영기는 검토대기반환을보존하고같은thread를재개한다. 이미running인작업이나처리된요청을중복실행하지않는다. 새로운검토지시는실제재개프롬프트에포함한다.
