# 0077: 직접 실행 입구의 부분 수용과 T3 남김 처분

이번 inbox.completed는 g5-entry-io(returncode 0) 한 건이다. 보고의 partial을 유지해 유효한 시험·설명을 수용한다. 정본 4개 diff와 대응 미러 4개, 현재 명령 생산자와 실행 입구를 검토했다. check.py report PASS 뒤 workspaces.py integrate C:/math C:/math/.async/dm g5-entry-io로 8파일을 충돌 없이 통합했다. 제품 실행 코드 9개는 배정의 수용 SHA와 같으며 새로운 사용자 동작 결함을 고친 결과는 아니다. 진행 중 g5-core-rest·g5-trust-rest의 정의/objective를 유지한다.

## 실제 결과와 확인 한계

두 provider direct Python root의 새 시험은 실제 요청 파일을 받아 외부 CLI 자리의 현재 Python이 공급자 플래그를 거부하는 경계를 확인한다. worker 자체 exit0과 외부 CLI exit2, 요청/prompt/schema/argv SHA, 실행/profile 신원, 원 stdout과 정확 오류 첫 행을 단언한다. 유료 공급자·모델 응답 성공을 확인한 결과가 아니다. codex_adapter.LocalCLIAdapter.start의 direct worker 명령과 claude_worker/codex_worker의 실제 입구를 대조했다.

기존 frozen bootstrap 시험은 손상된 live repository.py 대신 검증된 동결 package를 적재한 뒤 check를 실제 child로 실행한다. HOLD 결과·원bytes·빈 연구 repository, startup.json과 결과의 일치, 동결 runtime/원 설치 경로·snapshot hash·정확 파일 차이를 확인한다. 새 인프로세스 시험은 실제 동결 scheduled_operator 파일의 __file__/SKILL_ROOT와 인접 manifest 선택을 유지하고 기존 Jobs 포트 대역을 통해 live child 전체 argv·1회 전달·정산·게시 기록을 확인한다. 제품 globals를 패치하지 않지만 실제 엔진 child 운전이나 원본 파일 T3 도달은 아니다. 기존 MCP/submit_draft·독립 설치 probe 시험도 재사용했다. CLI 설명은 이 경계와 실제 scripts/operator_bootstrap.py 링크를 반영한다.

verify-result.py와 verification-review.json은 각 원report의 선택/고유 실제행·counts·fixture/실행중변경, 보존 원자료 SHA와 제출 Python SHA를 대조한다. boundary1은 8행=6passed/2failed·exit1, boundary2는 실패한 두 사례만 2passed·exit0이다. 최초 실패는 새 시험의 Python 오류 문자열 콜론 기대 한 줄이며 보존 시험과 최종판의 차이가 그 한 줄뿐임을 확인했다. focused1은 새 frozen 시험과 기존 smell 검사 2passed이나 부분T3 gate/최상위passed/closing_eligible=false·exit1이다. 세 실행은 complete=true, 뒤 두 실행만 successful=true, fixture/실행중변경은 모두0이다. 세 판본을 전체8통과나 G5 성공으로 합산하지 않는다.

각 실행의 917 Python SHA 중 boundary1의 보존 시험 1개를 제외하면 제출판과 모두 byte동일이고 boundary2/focused1은 전건 같다. T4 adapter 보고는 둘 다 complete=true·problems=[]·모든 필요 worker merged다. 공식/외부 시간은 boundary1 72.3/79.360초, boundary2 8.6/15.219초, focused1 63.8/64.547초다. 원자료는 task/evidence에 보존한다. manager 제품시험은0이며 통합 뒤 실제 공용 bytes는 integration-check.json으로 대조한다.

9제품의 base/배정/제출 SHA와 focused1 raw coverage에서 원본 T3 미도달 19arc/35행을 확인했다. 삭제·새제외·원본 raw도달은 모두0이다. 이 중 12arc/24행은 실제 child, 1arc/1행은 실제 동결 파일의 독립 동작 근거가 있다. 행동 확인을 원본 경로의 측정값으로 바꾸지 않는다. 해당 좌표는 과거 유한 목록이며 최종 통합판 전체 gap 수가 아니다.

파일 symlink/reparse omission 1arc/3행과 실제 POSIX replace/shared-reader/fcntl/PhysicalBoundary 5arc/7행은 미검증이다. 같은 호스트의 WinError1314를 재사용하고 junction을 대체 근거로 삼지 않았다. 등록 WSL2의 시작 실패 HCS_E_HYPERV_NOT_INSTALLED는 worker 관측이며 별도 native exit/원bytes가 없어 공식 실행 증거보다 약한 환경 설명으로만 유지한다. 새 환경/권한 조정 없이 다시 같은 probe를 배정하지 않는다. 실제 파일 symlink가 가능한 환경과 실제 POSIX 실행 조건이 필요하며 G7/최종 미결에서 숨기지 않는다.

## 다음 배정과 이유

새 g5-entry-gate는 이미 행동이 확인된 script/import/frozen의 13arc/25행을 한 작업으로 처분한다. 원설계5.5는 T3 인프로세스 분모와 T4 외부 경계를 구별하며 의도적 미도달에 같은 행 사유를 요구한다. codex_worker의 direct-import에는 이미 이 규칙의 좁은 제외가 있다. 새 task는 실제 독립 interpreter에서만 의미가 있는 입구와 일반 판단을 나누고, 근거 있는 좁은 제외 또는 현재 계약의 단순화·최소 시험을 함께 수행한다. 제외를 미리 확정하거나 정상 로직·전체 모듈을 감추지 않는다.

scheduled_operator의 인접 manifest 선택은 파일 사본이 측정 밖이라는 사실만으로 제외할 수 없다. execute의 startup 근거와 run_engine의 재탐색, bootstrap.main의 전달 관계에서 불필요한 중복/암묵적 결합을 줄일 수 있는지 판단하도록 했다. live argv/설치 신원·검증·HOLD를 유지하며 test-only 매개변수나 coverage 보정 framework를 만들지 않는다. 기존 T4 증거가 충분한 부분은 재실행하지 않고 실제 실행 계약을 바꿀 때만 필요한 작은 경계를 확인한다. 환경 6arc/10행은 이 작업에서 제외하고 적합한 환경 확보 조건으로 유지한다. 이는 지원코드 삭제/무근거 no-cover를 허용한다는 뜻이 아니다.

사용자 저장범위 지시와 원설계3.3/A22에 따라 공통 저장/codec·기존 업무 단언을 재사용하고 가족별 전생산자/전필드/새reader/옛head quota·장기 감사를 만들지 않는다. 후속은 반복 실행이 해결하지 못한 구체적인 측정/계약 질문으로 좁혔다. 원래 G1~G8은 유지한다. 최종 통합판 G4/G5·최종함수색인에 따른 G6·G7 실환경·G1~G3 최종연결·L01·G8 review는 미완료다.

기존93정의·취소2건을 보존하고 g5-entry-io를 accepted에 추가해89개 수용한다. 새 g5-entry-gate 포함94정의·active다. 실제 선행은 g5-entry-io뿐이고 새 쓰기 범위는 inbox.running 두 task와 겹치지 않는다. core-rest1·trust-rest1·entry-gate1의 시험슬롯 합계3, max_workers10·gpt-6.1-sol/high를 유지한다. 전체 동료 종료나 자원만을 위한 의존성을 만들지 않는다. 이 세션 도중 추가로 종료한 task는 다음 manager가 처리한다.

공용 context/plan/seams와 새 objective/gap-scope를 먼저 완성한다. 별도 queue.pending.json을 check.py queue로 검사한 뒤 그 동일 bytes를 queue.json으로 원자 교체하며 이번 공용 변경을 끝낸다.
