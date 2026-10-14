# 028 cli-control-names 조사

배정된 N01-209~235의 27절 판정을 완료했다. 제품을 고치지 않은 work 조사이며, 유지14·기존 근거 재사용8·검사 보강3·문구 수정2절이다. 수정 후보의 실제 연결 검증은 다음 통합 work의 책임이다. G1~G8의 전체 충족이나 최종 review를 선언하지 않는다.

정본 좌표는 `section-decisions.json` 하나에 있다. 각 출현은 현재 행·열·형태·절의 SHA와 해당 문맥의 owner group에 연결된다. `owner-profiles.json`은 이 group의 입력/출력과 실제 함수·상수·schema·소비 시험의 현재 행/SHA를 보존한다. `check-bindings.json`은 원 공식 row와 현재 실제 단언을 연결하며, 같은 출현표를 다시 만들지 않는다. `section-inventory.json`은 결정 전 추출 자료로, 최종 판단 정본이 아니다.

현재 27절의 제목/행 경계는 원 slice와 같다. 027 manager의 2,675소스와 시작/종료 해시는 전건 같고, 입력30파일도 불변이다. 원 모집단692는 전체 inline 수가 아니라 packet의 각 `distinct_tokens`에 속한 `candidate_occurrences` 합이다. 당시 전체 inline은847, 현재는849이며 024에서 승인한234행의 `dispatch_wait.since`와 `dispatch_wait.limit_seconds`만 추가됐다. 원692후보를 전부 포함해 현재 inline849와 코드펜스 이름374, 총1,223출현을 판정했다. 이름 없는 N01-219/231은 구분 제목이라 출현0의 이유를 남겼다. 코드펜스23 JSON은 완전 control, 설정fragment, relation_claim/academic_requirements 부분객체를 구별했다. 명령 synopsis의 PATH/TEXT/OID/ID/N, Python예시의 stdlib/지역변수, 파일경로와 외부환경·CLI이름은 실제제품필드라고 승인하지 않았다.

126행의 `ready`, `performing`, `assessing`, `needs_revision`은 과제상태가 아니라는 명시 음성예시다. 실제 tasks.status의 다섯 값과 각각의 반려를 대조했고 그대로 유지했다. supplemental request의 ready도 task.status가 아니라 `task_ready(...).state`다. 활동·실행·외부operation의 동명 상태와 output_accepted/succeeded를 별개로 연결했다.

F1은 knowledge487/512/514/546/573의 정확 문구 수리다. 현재 여섯 operation과 기존ID import 거부, revise의 새 replacement ID/supersedes·원권한 보존, 현재usable formal의 조건부 재사용, withdrawn 종류의 재등록 예외를 문서에 반영해야 한다. 동일ID import를 수리한다는 이유로 runtime에서 허용하지 않는다. 기존 공개control과 순수domain시험은 정확 반려/원기록불변/새ID·oldformal·oldjudgment보존을 이미 단언한다. 이 도메인 반례를 새로 실행하지 않았으므로 정적 대조로 보고한다.

F2는 external609의 정확 문구 수리다. 전송원장은 prepared와 transmitted/transmission_phase로 보존하고, running은 별도 execution의 상태다. HTTP수신만으로 confirmed라고 안내하면409의 failed/unknown 두 분기와 모순된다. 2xx는confirmed/True, 효과부재근거가있는비2xx는failed/False, 미입증비2xx는unknown/None으로 안내해야 한다. 현재 execute_operation·engine persist와 기존 소비단언을 대조했다. HTTP/OS/네트워크/모델/저장 실행은 하지 않았다.

F3은 공유doc_code의 한정검출 공백이다. 정상문서와 다음5변형을 `-B`의 순수helper관찰로 확인했다: summary→summray, import→improt, capacity_waiting→capacity_waitng, reviewers기본2→200, query방향both→sideways. 기존 command/scoped/unowned/policy/function검사는 변형5개를 모두 놓친다. actual control shape는 improt를반려하지만 candidate키 shape는개방돼summray를즉시반려하지않는다. 같은제품 candidate_shape_errors가 summary누락을반려하며 실제importer의저작필드검사도별도다. actual JSONparser는sideways와잘못된조회조합을반려한다. 따라서 부분구조shape를전체domain의의미검증이라고표현하지않는다.

보강은 현재 CLI의 runtime상태표, 설정목록의 단일키기본값/enum, knowledge완전JSON의 실제operation/candidate형태, query direction synopsis의 actualchoices에 한정한다. 부분객체와 자리값을 완전응답으로 검사하지 않고, 음성예시/기존동명owner 보호를 유지한다. 전역자연어추론기·조사표의제품schema복제는 필요없다. F1/F2의문구·공유helper/직접소비·공식미러/관련검사를다른028결과의같은수리단위와함께한work로묶을수있다. 정확완료조건은 findings.json에 있다.

027 c3의 raw보고 SHA81433763071a634c750c94f1c8fec1fdb2fbbfeaadb6cb08f80b8ecfb8cffaae, selected와고유38문서row의passed,875Python의현재SHA를재확인했다. 새시험통과38건으로세지않는다. P03/P06/P08/P10의지정문장,026정책및027연결/probe/단계·부분JSON/mode의이미검수한정확성질을재사용한다. B132~B134의원보고경로/SHA도확인했다. 이후바뀐helper파일의옛전판본을그대로재사용하지않으며, 원래역할입력packet밖다른문장에승인을확대하지않는다. used reports와현재/과거source차이는 reuse-profile.json에있다.

보조분석초기의실패는제품실패가아니다. 첫스크립트이름inspect.py가stdlib inspect와충돌하고인자없는import에서IndexError를냈다. 자기evidence의이름을bounded_io.py로고치고import를수정했다. owner좌표검산은잘못가정한모듈/심볼을반려했고실제정의를찾아수정했다. 첫verification은692후보를전체inline로가정해실패했으며원packet의필터와847→849의정확차이를확인해수정했다. 원verify-process.json의exit1은보존하고최종verify-final-process.json의exit0과구분한다. 성공판정에실패를더하지않는다.

L01 Q1/Q2·UTF8 byte요구와미충족,Windows1314심볼릭링크실제반려미검사,기본전체/freshT3/전수변이/최종판연결/최종review는그대로남는다. 제품/시험/미러/공용문서/과거자료/캐시/index/graphify/Git상태를변경하지않았다. 제품import는pure-observations.json에기록한순수schema/parser/문서helper만호출했다. 새로운제품시험은0건이다.
