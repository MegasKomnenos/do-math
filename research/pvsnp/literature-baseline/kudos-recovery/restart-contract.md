이 문서는 2026-09-08 사용자 피드백에 따른 새 작업자의 재개 계약이다. `contract.md`의 수집 범위·증거·인증 계약에 다음 실행 방법과 완료 검사를 적용한다. 이전 작업자 세 명은 중단됐으며 새 작업자는 저장된 증거와 결과를 이어받는다. 디렉토리별 모델은 사용자가 지정한 `gpt-6-astra / medium`이다.

소비자는 다음 작업을 선택하는 작업자와 전체 완료를 판정하는 루트다. 소비자가 기대는 것은 자료마다 남은 일이 빠짐없이 드러나고, 유효한 결과와 이미 조사한 범위를 재사용할 수 있다는 것이다. `collection_stage`, 검색 한 차례 완료 표시, 처리 건수만으로 후보를 제외하지 않는다.

공통 지원 도구는 이 문서와 같은 디렉토리의 `work_queue.py`, `check_recovery.py`다. 전자는 파일을 변경하지 않고 남은 작업을 계산하고, 후자는 입력 결박·파일·해시 검사와 완료 조건을 검사한다. 다음 명령의 `gXX`는 자기 배정으로 바꾼다. 명령은 `C:/math`에서 실행한다.

```text
python research/pvsnp/literature-baseline/kudos-recovery/work_queue.py --assignment research/pvsnp/literature-baseline/kudos-recovery/gXX/assignment.json --output research/pvsnp/literature-baseline/kudos-recovery/gXX/work-queue.json
python research/pvsnp/literature-baseline/kudos-recovery/check_recovery.py --assignment research/pvsnp/literature-baseline/kudos-recovery/gXX/assignment.json --partial
python research/pvsnp/literature-baseline/kudos-recovery/check_recovery.py --assignment research/pvsnp/literature-baseline/kudos-recovery/gXX/assignment.json
```

부분 검사의 `passed`는 현재 저장된 파일의 검사가 통과했다는 뜻이다. 전체 완료는 `complete=true`이고, 입력 전건의 결과·세 구성요소의 판정·내용 검토·필요한 조사 범위가 모두 닫혔을 때만 가능하다. 큐의 `completion_candidates`도 파일 검사를 생략한 완료 후보 수다. 미해결·미처리·실행 실패를 부재로 바꾸어 검사기를 통과시키지 않는다.

재개 순서는 다음과 같다.

1. 자기 배정, `shared-findings.md`, 기존 소스·시험·진행 파일·차단 기록을 읽는다. 자기 결과 전건을 큐로 만들고 이전 결과의 초록·원문·식별 상태와 별도 검토 목록을 대조한다. `g05/root-pdf-review.json`에 있던 루트 검토 예약 10건도 새 g05 작업자가 인수한다. 루트가 그 10건의 검토를 끝냈다고 가정하지 않는다.
2. 저장된 증거를 먼저 판독·재판정한다. 판별 함수만 바뀐 경우 증거에서 다시 검사하고, 근거가 부족한 작업만 브라우저 큐로 보낸다. 이미 확보한 유효 초록과 원문은 유지한다. 잘못 결합된 자료를 발견하면 철회 사유와 원본을 보존하고 올바른 자료를 계속 찾는다.
3. 아래 자기 묶음의 결함을 실물 입력으로 재현하고, 실패 시험을 관찰한 뒤 최소 수정한다. 기존 회귀 시험과 실제 UI의 소규모 실행을 통과시킨다. 실패와 통과의 명령·exit code·입력 좌표를 `tdd/`에 기록한다. 전수 브라우저 실행은 이 수리 이후 시작한다.
4. 자기 디렉토리에 새 실행 진입점 `resume.py`를 만든다. 기존 수집·추출 함수를 사용하되 남은 작업에 따라 저장 증거 재판정, 필요한 브라우저 단계, PDF·초록 후보 처리, 검사를 연결한다. 기본 실행은 담당 전체이고 `--limit`는 실물 시험을 위한 후보 수 상한이다. 한 후보의 초록이 확보돼도 원문 작업을 버리지 않고, 원문이 확보돼도 초록 검토를 버리지 않는다.
5. 자동으로 처리 가능한 작업은 실행기가 계속 처리한다. 일시적 타임아웃·HTTP 429/5xx는 실제 응답과 서버 안내에 따라 제한된 재시도와 대기를 적용한다. 재시도를 소진한 건은 원인과 다음 작업을 저장하고 다른 건으로 진행한다. 영구 권한 제한과 일시적 서비스 오류는 구별한다. 한 후보의 오류로 전체 후보를 실패 처리하지 않는다.
6. 실행기가 사람이 읽어야 하는 후보나 코드 수리를 반환하면 작업자가 실제 이미지·본문을 읽고, 필요한 회귀 시험·수정·검사를 수행한 뒤 같은 진입점을 다시 실행한다. 이 반복의 소유자는 작업자다. 단순 실행기가 스스로 코드나 의미 판단을 고친다고 주장하지 않는다. 프로세스 종료, 한 번의 순회, 검토 큐 생성은 작업자 종료 조건이 아니다.
7. 전체 검사를 통과하면 `report.md`에 최종 확보·부재·접근 제한 수, 실제 검사와 한계, 재개 명령을 남기고 루트에 반환한다. 공용 도구 결함은 좌표·재현·영향을 즉시 루트에 보내고 독립 작업을 계속한다. 현재 권한으로 해결 불가능한 실제 장벽은 근거와 필요한 조치를 루트에 보고한다. 같은 무진전 명령을 무한 반복하지 않는다.

새 결과 필드 `work_state`의 형식은 `work_queue.py`가 검사한다. 기존 결과 외피 `kudos-recovery-result/1`은 유지한다.

```json
{
  "work_state": {
    "version": "remaining-work/1",
    "tasks": [
      {
        "key": "자료 안에서 고유한 작업 키",
        "kind": "search",
        "target": "실제 검색어 또는 URL·파일·검토 대상",
        "status": "pending",
        "reason": "이 작업이 남은 이유"
      }
    ],
    "reviews": {}
  }
}
```

`kind`는 `search`, `source`, `pdf`, `review`, `repair` 중 하나다. `status`는 `pending`, `retry`, `needs_review`, `done`, `not_needed` 중 하나다. 앞의 셋은 열린 작업이다. `done`과 `not_needed`에는 구체적인 이유와 `evidence_paths`가 필요하고, 경로들은 같은 결과의 `evidence` 또는 초록·원문 `artifacts`에 보존돼 있어야 한다. `not_needed`는 목표 내용이 이미 검증돼 확보됐거나 후보가 다른 자료임이 입증되어 더 방문할 실익이 없는 경우처럼 해당 작업의 필요가 사라진 처분이다. 시도 상한 도달은 이 처분의 근거가 아니다.

검색 페이지나 다운로드 후보를 일부만 처리했으면 같은 단위의 `discovered`, `attempted`, `remaining`을 모두 기록한다. 세 값은 음이 아닌 정수이고 `discovered = attempted + remaining`이다. `remaining > 0`인 작업은 `done`이 될 수 없다. 페이지 수와 문헌 수를 더하지 않는다. 실제 후보별 작업을 따로 만들었으면 발견한 목록과 각 작업의 처분으로 범위를 추적할 수 있다.

`reviews`에는 `identity`, `abstract`, `fulltext`별 검토가 들어간다. 각 검토는 `basis_sha256`, `reason`, `evidence_paths`를 가진다. `basis_sha256`은 `work_queue.component_basis(result, component)`로 계산한다. 이 함수는 해당 구성요소와 그 식별 전제에만 기댄다. 다른 후보의 진전이나 진행 시각 때문에 검토가 무효화되지 않는다. 결과를 실제로 검토한 뒤 해시를 기록한다. 해시 생성은 내용 검토를 대신하지 않는다.

부재·접근 제한 판정의 검토에는 `scope_complete=true`와 실제 확인 범위에 대한 이유가 필요하다. 작업 목록에도 실제 검색 범위와 원문 연결 경로의 확인을 나타내는 `search`·`source` 항목이 있어야 한다. 모든 후보가 실제로 시도됐거나, 근거와 함께 불필요해졌어야 한다. 초록과 원문이 모두 검증돼 확보됐다면 그 내용을 얻기 위한 추가 검색을 강제하지 않는다. 한 구성요소라도 미확보이면 원래 계약의 필수 조사 범위를 적용한다.

이전 `unvisited_link`, `unvisited_search_pages`, `collection_error`, `needs_mathscinet_revisit`는 현재 남은 일을 가리는 방식으로 지우지 않는다. 대응 작업을 해결하거나 실제 근거로 종전 기록을 대체한 뒤 이력에 보존하고 활성 표지만 해제한다. 외부 검토 목록도 `work_state.tasks`로 연결하여 누락을 방지한다.

각 `resume.py` 실행은 시작 시각·PID·정확한 인자·실제로 사용하는 로컬 코드 파일과 SHA256을 자기 `runs/`에 저장한다. 실행 중 소스를 수정하면 해당 프로세스에 반영됐다고 가정하지 않는다. 그 프로세스를 체크포인트에서 종료하고 수정 후 시험을 통과한 새 프로세스를 연다. 처음에는 작업자당 브라우저 흐름 하나를 사용한다.

각 실행은 검색·출처 방문·다운로드의 실제 횟수와 소요 시간, 저장 증거 재사용 수, 검토 대기 수를 기록한다. 진행 수는 시작 시 한 번 집계하고 이후 변경된 후보의 이전·새 상태 차이로 갱신하거나 일정한 간격으로만 다시 집계한다. 중복 집계가 성능의 가장 큰 병목이라고 가정하지 않고 실측으로 판단한다.

묶음별 수리 범위는 다음과 같다.

| 묶음 | 수리하고 실제 경로로 검증할 내용 |
|---|---|
| g02 | 단계 표시로 미해결 후보를 제외하는 조건, HTTP 500·묶음 오류의 전체 종료, DOI/ISBN 없는 정확한 서지의 대응, 단건 검색의 잘린 페이지, 보존한 Article·출판사 링크의 원문 수집 연결, 책의 완전한 DB 제공 초록을 유형만으로 제외하는 분기 |
| g05 | ACM·Summon·PDF 영역 제안·실제 내용 검토의 인계, 초록만 또는 원문만 남은 후보의 재개, 첫 정상 PDF가 다른 자료일 때 뒤 후보 순회, Summon의 잘린 결과 범위, 기존 수집기의 위치와 현행 진입점 구별 |
| g08 | 저장 증거로 끝난 단계의 불필요한 브라우저 재실행, Article의 새 탭·같은 탭 이동, PDF 앞 3개 상한과 실제 방문 수, 미방문 링크가 남은 부재 판정, 원문 상태만으로 초록을 부재 처리하는 분기, 두 프로세스 진행 집계의 중복, 책의 DB 초록 유형 처리 |

이 표는 사용자가 제공한 피드백의 수리 대상이며 현재 소스와 실제 기록을 대조하여 각 항목을 `confirmed`, `already_fixed`, `not_reproduced` 중 하나로 `feedback-response.md`에 판정한다. `not_reproduced`는 무시할 허가가 아니다. 반례와 현재 분기를 제시하고 필요한 실물 검사를 수행한다. 확정된 결함에는 수리 파일·시험·실물 실행·결과를 연결한다.
