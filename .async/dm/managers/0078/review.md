# manager 0078: core 부분 결과 수용과 남은 수신·복구 판단

지정 inbox의 completed는 g5-core-rest 한 건(returncode0), running은 g5-trust-rest·g5-entry-gate다. protocol의 manager 절차와 공용 context/plan/seams의 현재 상태·목표·자원, 사용자 저장범위 교정, 원설계3.3/A22·5.5, task objective/report와 관련 원증거를 읽었다. 제품 변경은 task 산출물의 공식 통합으로만 처리했다.

## 수용한 결과

g5-core-rest를 partial 그대로 수용한다. 정본 제품3(core_engine/external_engine/retention), 직접 시험6, 설명1과 공식미러10쌍, 총20파일을 검토하고 workspaces.py integrate로 충돌 없이 반영했다. 공개 형식/권한/현재성/정산을 유지하면서 제출·저장 경계 뒤의 중복 방어와 미생산 경로를 줄인 결과다. 새 사용자 동작 결함 수리 또는 전체G5 완료라고 판단하지 않는다.

정본10파일의 base→workspace diff를 읽었다. core의 제어 handler 후보 준비와 processed ID/receipt의 최종 게시 위치, 제출 경계의 knowledge_changes 역할·제목 유일성·공백 report·종류 verdict 검사, import_candidate의 기존 ID 반려, waiting map/action.id 의미검사, 관찰 feedback의 실제 생산/전달 경로를 확인했다. 외부 retry의 현재 grant 검사와 실행 등록·동기 persist 소유를 대조했다. retention의 source 이름은 저장 schema 필수가 아니라 실제 생산자와 record_storage/_source_errors 보장이다. 설명의 waiting→resume_activity→ready→assign_execution→working 순서도 현재 계약과 일치한다.

직접 시험에는 source 변경의 live 소비자 정지/원bytes 보존, grant 없는 요청의 저장된 사용자 질문/전송 없음, 공개 pause·grant 철회 반려, 실제 Git 게시/읽기 실패의 원대기·정산·영수증 보존, feedback 파일 실패와 재전달, self-check checkpoint 계수와 bytes가 포함된다. 제품 함수 패치 없이 기존 외부 포트 대역과 실제 Repository/StateContract를 사용한다. 실제 공급자/Job/Lean/공용설치 성공으로 확대하지 않는다.

## 원검증과 한계

manager는 제품시험을 다시 실행하지 않았다. verify.py의 정적 대조 결과는 verification-review.json이다. 부분T3 여섯 원보고의 선택=고유실제행(5/6/9/8/5/2), fixture0·실행중변경0, 실행별 PythonSHA 915/915/916/916/916/915의 보존bytes와 invocation SHA를 확인했다. 변경 시험본문19개는 각각 passing행의 보존AST와 같다(docstring 제외). 원좌표 raw도달은 원coverage 및 제출판과 같은 함수AST로 확인했고, 제거는 실제diff·현재 경계로 판단했다. 정본/미러10쌍도 bytes가 같다. report 검사는 PASS, 통합은20파일이다.

part1=4passed/1failed, part2=5passed/1failed, part3=6passed/3failed, part4=7passed/1error, part5=5passed, part6=2passed다. 전부 complete=true, 뒤둘만 successful=true이며 모든 부분gate/최상위passed/closing_eligible=false·관측exit1이다. 서로 다른 선택·판본을 단일 전체성공으로 합산하지 않는다. 실패는 bundle 선언 누락·미발급 self-check 선행 반려·기존artifact cache·기대문구·resolver 구분·없는 속성 등 시험구성 오류였고, 수정된 본문의 passing 근거를 확인했다. 원실패는 보존한다.

원96arc/126행은 raw도달12arc/21행·제거14arc/11행·남김70arc/94행이다. 남김은 core69/93과 integration1/1이며 과거좌표 처분이다. 제출판 전체gap 수가 아니다. 새제외는 없다. part1~3의 T3 store 개별복사 부재는 한계로 유지한다. 원report/coverage/source는 보존됐으며 여섯회 모두 재사용모듈0이다. 구조검사/미러 실행은 task의 final-commands/final-static 및 part5 원보고 범위로만 인정한다.

## 후속 범위와 자원

새 g5-core-gaps는 위70arc/94행의 실제 계약 질문·필요수리·최소확인·설명/미러를 함께 맡는다. 남김의 제안 시나리오를 의무로 만들지 않고 입력/저장·소유자 전이의 전제부터 판단한다. 작은 integration 안정화 질문은 core impact 게시와 함께 묶는다. 외부 retry/retention/grant부재·활동 설명의 완료분은 재배정하지 않는다. 전체 관문 재실행·미시작 저장가족 확대·별도 장기감사는 추가하지 않는다.

실제 선행은 g5-core-rest뿐이다. 같은 core 파일의 여러 질문을 동시에 수정하는 별도 task는 만들지 않는다. 진행 중 trust-rest/entry-gate 정의와 objective는 유지하며 새 허용경로와의 교집합을 assignment-scope.json에 기록한다. 각 시험슬롯1, 합계3·max_workers10·gpt-6.1-sol/high를 유지한다. G6는 최종 함수/색인이 필요하고 G7 공유 실환경은 별도 배정이 필요하므로 이번 부분판을 그 최종 근거로 사용하지 않는다.

사용자 저장범위 교정/A22에 따라 공통 codec·검증 저장·기존 업무 보장을 재사용하고 전가족/전필드/새reader/옛head quota를 추가하지 않았다. 환경6arc/10행은 WinError1314·실제POSIX 필요를 유지하며 동일 probe를 반복하지 않는다. 최종수용판G4/G5·G6~G8·G1~G3 연결·L01/실경계는 남아 있어 queue는 active다.

공용 문서와 objective를 먼저 작성하고 queue.pending.json을 검사한 뒤 같은 파일을 queue.json으로 원자 교체한다. 기존94정의/취소2건을 보존하고 g5-core-rest를 accepted에 추가한90수용, 새task 포함95정의를 게시한다. 실제 검사·게시 결과는 queue-check.txt 및 publication.json에 남긴다.
