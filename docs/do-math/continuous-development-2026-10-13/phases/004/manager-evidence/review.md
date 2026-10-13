# phase 004 manager 검수와 후속 배정

mirror-corpus의 partial을 유지하고 phase 005 corpus-git-bytes를 배정한다. A1/A2/A4는 배정된 범위에서 통과했고 A3는 Git manifest 바이트 보존 조건이 미충족이다. 미러 생성 치환과 재생 실패는 해결됐다. 개발 전체 완료나 Codex 공급자 성공을 선언하지 않는다.

## 원보고와 현재 파일

protocol, 공용 문서, phase/objective와 report 전문을 읽었다. 공용 문서 편집 전에 report 검사 exit 0을 확인했고 report-check.json에 실제 명령과 출력을 보존했다. verify_inputs.py는 종료 소스 2624개의 SHA가 현재와 같고 변경 9개가 report changes와 writes에 일치함을 확인했다. phase 003 종료 2254개도 phase 004 시작과 같았다. 다른 dirty/untracked를 이번 변경으로 합치지 않았다.

생성기 전체 직접 실행 22개 통과와 수리 전 2시험 중 5개 하위 사례 실패, 공식 생성의 예정/실제 4개 변경 및 마지막 timing 사본 한 개 변경을 원출력과 전후 소스 목록으로 확인했다. 실제 코드의 verbatim 선적용과 추가된 경계/대조군 단언도 읽었다. 현재 생성기 본문·overlay manifest는 불변이다. 정본과 미러의 공식 보고는 각각 14선택/14실제 row/14passed이며 skip·fixture 오류·누락이 없고 exit 0이다. 각 보고의 Python 864개 해시는 현재와 같다. 두 실행 중 해당 timing 캐시만 바뀌었다. 최종 --check의 1297파일 drift 없음과 skill-only verified도 실제 종료 출력과 대조했다. manager가 제품 시험이나 모델 호출을 반복하지 않았다.

정본과 미러 각각의 17항목·44파일·200872바이트를 직접 읽고 41개 명시 SHA 참조를 검산했다. 두 Claude help가 원 SHA로 돌아왔으며 정본 manifest·원녹화·역사 verdict는 불변이다. 과거 4선택/2통과/2실패와 첫 검산 스크립트의 오류는 과거 실패 그대로 보존한다. 검산 도구의 최초 잘못된 가정과 실제 제품의 A3 실패를 구별했다.

## 두 발견의 처분

F1은 carry다. manager가 실제 Git 명령으로 양쪽 88개 파일을 검사해 manifest 두 개의 raw db61141d…와 clean 89d1c078… 차이를 재확인했다. 하위 corpus/.gitattributes의 manifest text 예외가 원인이며 상위 속성으로 해결되지 않은 task의 관찰과 현재 복원 해시도 확인했다. 이전 manager의 writes에는 상위 속성만 있었고 정본 corpus는 읽기 전용이었다. task의 범위 준수를 실패 은폐로 해석하지 않는다. phase 005는 실제 하위 정본과 생성 사본만 수정하도록 명시해 배정 누락을 해소한다. 제안 패치는 아직 미적용이며 새 task가 실제 clean 전건 보존으로 검증한다.

F2는 resolve다. Git 2.50.0.windows.2에서 같은 9개 argv를 다시 실행해 Lean/scheduler의 역슬래시 절대 경로와 슬래시 경로 사이의 차이를 확인했다. manifest는 모든 표기에서 변환된다. phase 003의 정확한 argv는 없으므로 당시 표기는 단정하지 않는다. C12와 다음 objective에 현재 검증 경로와 한계를 반영했다. 원녹화를 다시 쓰거나 예전 관찰을 고치지 않았다. parent trial은 제품을 건드리지 않고 보존된 원출력과 복원 해시로 검수했다.

## 공용 정보와 다음 작업

context C2/C5/C8에는 검수 상태와 다음 실행 단위를, C9에는 생성기/속성의 한정 재검토를, C11/C12에는 수리된 치환과 미해결 Git 속성·Codex 경계를 반영했다. C1/C3/C4/C6/C7/C10과 G1~G8의 문언을 유지한다. plan은 속성 수리 뒤 Codex 수리로 가까운 순서만 바꾸고 나머지 의미·문서·실제 연쇄·전체 관문·최종 review 책임을 유지한다. common-docs.diff와 common-docs-review.json이 전후 의미의 확인 근거다. seams는 공통 설명만 갱신하며 새 S ID나 제품 경계 계약의 변경은 없다.

005는 단일 work이며 두 속성 파일만 쓴다. 녹화·manifest·Python이 불변이면 이미 통과한 생성기 22개와 양쪽 재생 14개를 판본 대조로 재사용한다. 새로운 검증은 실제 Git 필터 전건 비교·해시·최종 공식 생성/구조 확인이다. 같은 corpus와 생성기를 쓰는 Codex 수리를 병렬 배정하지 않는다. 후속 실행은 run.py의 책임이며 manager가 새 task를 직접 기동하지 않는다.

## 관리 커밋과 증거 보존

commit-harness는 예정된 검증·교정 뒤 제품을 커밋하도록 정한다. 이번에는 A3 속성 실패와 앞선 Codex 실패가 남아 있어 제품 경로를 커밋하지 않는다. 관리 문서·원보고·실행 출력·새 배정과 M-0554를 한 커밋으로 보존한다. phase 003~004 변경 합집합 68개 파일의 현재 바이트는 pending-product-working-tree.zip과 product-snapshot.json에 보존한다. 실패 상태의 archive이며 승인된 제품 판본이나 자동 복원 지시가 아니다.

task report/evidence는 기존 바이트 그대로 선별한다. 최초/최종 소스 목록은 보존하고 명령마다 반복된 source-before/source-after는 로컬 보관으로 둔다. 검수에 사용한 그 비교 결과는 verification.json에 있다. service runtime/세션 logs, 임시 .before와 pathspec 파일, 무관 dirty/untracked·engine은 커밋 범위 밖이다. 구체적 선별 목록은 preservation.json을 따른다. 실제 staged blob을 파일 바이트와 대조하며 push·graphify 갱신·기존 연구 변경은 하지 않는다.
