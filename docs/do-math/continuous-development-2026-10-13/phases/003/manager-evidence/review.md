# phase 003 manager 검수와 후속 배정

provider-smoke의 partial을 유지하고 phase 004 mirror-corpus를 배정한다. A1/A3/A4는 해당 범위에서 충족했으며 A2의 Codex 역할 schema 거부와 A5의 미러 재생 실패는 남는다. G7이나 개발 전체가 완료된 상태가 아니다.

## 원보고와 현재 파일의 대조

report 전문과 objective를 읽고 공용 문서 갱신 전에 report 검사를 통과했다. manager의 verify_inputs.py가 기록한 실제 PASS는 report-check.stdout.txt에 있다. task 종료 2254개 파일의 SHA가 현재와 일치하고 시작/종료 변경 62개가 report changes 및 writes와 같다. 그중 .timings 캐시가 두 개다. 기존 canonical/repository 및 다른 dirty/untracked 변경은 task 시작부터 있던 별도 상태로 유지한다.

live-01은 2선택/2실패/exit 1, live-02는 Claude 1선택/1통과/exit 0이다. 정본 offline-01은 23선택/23통과이고 미러 재생은 4선택/2통과/2실패다. 각 원보고의 선택과 실제 rows, 중복/누락 부재, 종료 PID/시각/exit와 실행 중 소스 불변을 확인했다. 정본 및 미러의 최종 보고가 가진 Python 864개 해시는 현재와 일치한다. live-02 뒤 세 오프라인 corpus 검사만 바뀌었고 호출 경로는 불변이다. 새 제품 시험과 유료 호출을 manager가 다시 실행하지 않았다.

세 실제 호출의 raw schema가 현재 action_schema와 같고 worker의 schema/prompt SHA 및 raw stdout SHA가 맞았다. Claude 마지막 호출의 실제 nonce 파일, checkpoint JSON, 선택된 final, 성공 Bash tool ID에 대응한 정확 JSON 읽기, local termination barrier를 대조했다. Codex raw는 integration_bundles가 required에 없다는 HTTP 400 invalid_json_schema로 실패했고 worker exit 1, parse_complete=true, turn_failed=true, 최종 응답·파일·checkpoint 부재였다. 첫 Claude 실패는 checkpoint가 읽기 출력에 섞인 경우이며, 첫 원판정과 두 실패 stream 모두 유지했다.

정본 corpus는 17항목·44파일·200872바이트이며 기존 raw 변경은 없다. 두 Claude help만 미러에서 다르고 원문 CLAUDE.md 치환이 원 SHA 불일치를 만든다. _rules.json과 transform/build_target 원문에서 기존 verbatim이 텍스트 변환 전에 바이트를 그대로 반환함을 확인했다. manager의 추가 Git clean 관찰은 manifest, Lean 입력, scheduler 녹화의 CRLF가 변환된다는 사실이다. stage/commit/checkout을 수행한 결과가 아니며 git-clean-observation.json에 읽기 전용 명령과 전44개 결과를 남겼다.

## 발견의 처분

F1은 Codex schema/전달/수신 경계의 수리로 carry한다. 제품 선택 필드의 부재/null/값 의미를 유지해야 하며 첫 오류가 유일한 제약이라는 가정은 하지 않는다. 인증 부재나 연구 control_binding 실패라고 추정하지 않는다. F2는 phase 004가 원바이트 인도 경계 전체에서 해결한다. 현재 두 파일명만 예외로 만들거나 원 manifest의 해시를 바꾸는 수리는 허용하지 않는다. 기존 verbatim과 corpus 한정 .gitattributes를 사용하고 일반 지시문의 변환·개행 정책은 유지한다.

F3의 한정 재사용은 resolve다. 기존 background 원자료 9파일 해시, 동일 task_id/tool_use_id·사건 순서, nonce·종료 barrier와 현재 코드 해시를 대조했다. 과거 actual_wait_tool=false 및 passed=false는 그대로다. 같은 판본의 native completion/파일/로컬 종료만 재사용하며 maintenance/schema/저장까지 확대하지 않는다. PR15/B86/B87의 지정 slice 판단을 승인하고 다른 PR15 범위는 남긴다.

## 공용 문서와 다음 작업

context C2/C5/C8에는 003 검수와 실행 시점을, C9에는 지정 역사 slice를 반영했다. C11의 빈 T5/옛 corpus/미판정 background는 시작 관찰로 명시하고 C12에 현재 부분 성공·결함·재사용·다음 책임을 추가했다. C1/C3/C4/C6/C7/C10과 G1~G8은 그대로다. plan은 004 미러 수리 뒤 Codex 수리로 가까운 순서만 바꿨고 다른 의미/문서/최종 관문을 보존했다. common-docs.diff를 직접 읽어 변경·보존 의미를 확인했다. seams는 공통 사용 설명만 갱신했으며 S 항목은 없다.

004는 기존 생성기·규칙·실제 corpus라는 확정된 경계의 단일 task다. 양쪽 공식 재생과 전파일 해시, 실제 Git clean 바이트 보존, 회귀 시험과 --check/skill-only를 책임진다. Codex 수리와 같은 phase로 묶으면 공유 미러·말뭉치·캐시를 함께 수정하므로 순차 배정한다. 개발 완료를 선언하거나 실행기를 직접 기동하지 않는다.

## 관리 커밋과 보존 범위

commit-harness의 검증-커밋 선후 규칙은 “검증 통과와 교정 반영 후에 커밋”이다. 이번 제품/시험 변경은 A2/A5 교정 전이므로 제품 경로를 커밋하지 않고 작업트리에 유지한다. 관리 기록·원자료·공용 문서·새 배정 및 한 layer1 기억 노드만 정확 경로로 커밋한다. 제품 62개 변경 파일의 현재 바이트는 provider-smoke-working-tree.zip과 product-snapshot.json에 별도로 보존한다. 이 archive는 실패 상태의 증거이며 승인된 제품 판본도 자동 복원 지시도 아니다.

task의 report·필요 원보고·명령 출력·live scratch의 실제 입출력과 historical-background 원자료는 보존 목록에 넣는다. 반복된 source-before/source-after 스냅샷은 최초 입력과 최종 source-final로 대표하고 그 밖의 중복본은 로컬에 그대로 둔다. 서비스 runtime/세션 logs, manager의 임시 .before와 pathspec 파일 및 제외한 중복 스냅샷은 Git에 보존했다고 주장하지 않는다. 실제 선택 목록은 preservation.json에 있다. 원자료를 읽기 좋게 다시 직렬화하지 않으며 stage의 Git blob을 작업트리 bytes와 대조한다. push·graphify 갱신·기존 연구 변경은 하지 않는다.
