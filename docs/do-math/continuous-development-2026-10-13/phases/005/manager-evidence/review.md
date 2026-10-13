# phase 005 manager 검수와 후속 배정

corpus-git-bytes의 A1~A3 complete를 승인하고 phase 006 codex-schema를 배정한다. phase 004 A3/F1의 manifest clean 실패는 새 증거로 해소됐다. 이전 partial report와 실패 원자료는 유지한다. Codex schema HTTP 400과 G1~G8의 나머지 완료 의무는 남는다.

## 실제 근거 대조

현재 protocol, 공용 context/plan/seams, phase/objective와 task report를 읽었다. 공용 문서를 편집하기 전에 report 검사를 실행해 exit 0을 확인했고 report-check.json에 명령·실제 출력을 보존했다. verify_inputs.py가 종료 소스 2624개를 현재 파일과 대조했으며 차이는 0개다. 작업 전후 변경은 배정된 두 corpus/.gitattributes와 report changes에 정확히 대응한다.

양쪽 corpus 각각의 17항목·44파일·200866바이트와 모든 명시 SHA 참조 41개를 원파일에서 검산했다. manifest와 녹화는 시작 바이트 그대로이며 6바이트 감소는 각 속성 파일의 한 줄 변화다. task의 수리 전/후 실제 argv·cwd·raw/clean 행을 대조했고 manager도 같은 / 상대 경로로 전88파일의 Git raw/clean·속성 출력을 확인했다. 현재 차이는 0개이며 두 manifest의 clean 값은 원 raw db61141d…다. text unset과 상속 eol 표시를 함께 보존하되 판정은 실제 바이트에 따른다.

공식 생성은 사본 속성 한 파일만 갱신했고 최종 --check는 1297파일 일치, --skill-only는 verified 및 exit 0이다. 각 실행 전후 해시의 실제 변경도 확인했다. 기존 양쪽 재생 보고는 각 14선택/14고유 row/14passed/exit 0이고 Python 각 864개가 현재와 같다. 생성기·그 시험·규칙의 해시와 이전 22 tests/OK 출력도 동일하다. 관련 시험과 모델 호출을 반복하지 않고 그 범위의 결과를 재사용한다. 해시·공식 row와 단순 보고 성공을 구별했다.

## 발견 처분

F1은 resolve다. 004 F1과 A3의 마지막 Git clean 남김을 이번 전건 새 근거로 닫는다. 작업트리/clean 검증이며 staged blob·제품 커밋 완료의 주장으로 넓히지 않는다. 제품 인도 시에는 그때의 corpus 원바이트와 staged blob을 별도로 대조한다.

F2도 resolve다. 004 종료와 005 시작 사이의 유일한 소스 차이는 protocol.md이며, 005 작업과 이번 검수 중에는 불변이다. 첫 보조 검산은 제품과 engine을 구별하지 않은 불변 단언 때문에 exit 1이었다. 당시 스크립트와 실패 출력, 뒤의 교정된 검산을 모두 보존한다. 현재 protocol을 따랐으며 engine 변경의 주체·내용을 SHA만으로 추정하지 않는다. 제품 재검증이나 engine 수리 배정의 근거로 삼지 않는다.

## 공용 정보와 다음 책임

context C2에는 005 검수와 기존 engine 차이를, C5/C8에는 종료 상태와 006 실행 단위를 반영했다. C9/C11/C12의 manifest 미해결 상태는 실제 새 근거로 종결하고 Codex 다음 수리를 구체화했다. C1/C3/C4/C6/C7/C10과 G1~G8 문언은 보존했다. common-docs.diff와 common-docs-review.json은 전후 의미 대조의 좌표다. plan의 완료 Git 수리는 결과로 옮기고 다른 문서·의미·실제 연쇄·전체 관문·최종 review 책임을 유지했다. seams 공통 설명만 갱신했고 S ID나 역할의 원 계약을 개정하지 않았다.

현재 코드에서 ModelRunner.run의 비결박 schema 전달과 model_call.classify_run의 원 schema 검사, worker/native final 결속, control_binding 분기를 확인했다. 006은 실제 비결박 호출자를 확정하고 원 의미를 유지하는 표현/수신 수리와 관련 회귀, Codex 새 대표 실호출·녹화·미러를 맡는다. 선택 필드의 부재와 null을 합치거나 역할 schema를 필수화/축소하는 해법은 허용하지 않는다. 구체적인 공급자 표현은 구현자가 결정하며 아직 구현됐다고 보고하지 않는다. 별도 연구/Job/Lean/예약/학술/L01을 동시에 확대하지 않는다.

원 schema·공통 수신 경로·시험 캐시·생성기를 공유하므로 006은 단일 task다. 다른 task가 이 미완성 제품을 읽어 검증하게 하는 병렬 배정을 하지 않는다. 고정판의 독립 읽기 review에서는 병렬성을 사용할 수 있다. 실제 다음 세션의 기동은 run.py가 맡으며 manager는 새 task를 기동하지 않는다.

## 관리 기록의 보존

phase 003부터 이어진 공급자 단위에는 Codex 실패가 남아 있다. 이번 커밋은 관리 문서·report/evidence·006 배정과 기억 노드 M-0555를 보존한다. 제품 경로를 stage하지 않는다. phase 004가 보존한 68파일 archive는 유지하고 이번 두 속성의 현재 바이트는 pending-attributes.zip에 추가 보존한다. 두 자료는 후보의 기록이며 승인된 제품 인도나 자동 복원 지시가 아니다.

원 report/evidence 바이트와 초기/최종 소스 목록을 보존한다. 명령마다 반복된 source-before/source-after는 로컬 보관으로 두며 비교 결과는 verification.json에 남긴다. 서비스 세션/runtime 로그, 임시 .before 및 pathspec 파일, 무관한 dirty/untracked와 engine은 커밋 범위 밖이다. 실제 선별 목록은 preservation.json에 있다. pending handoff와 기억 색인 검사를 통과한 뒤 manager.json으로 게시하고 내용 변경 없이 커밋한다. stage된 자료는 원바이트와 대조한다. 제품 수리 완료와 별도의 최종 검토가 있어야 개발 완료를 판단한다.
