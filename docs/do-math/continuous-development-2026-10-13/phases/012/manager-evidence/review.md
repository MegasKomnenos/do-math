# phase 012 관리 검수

lean-smoke의 A1~A4 complete를 승인한다. report 형식 검사 뒤 현재2658파일·종료 해시와 파일 집합,011 manager/시작 해시 동일, 허용22변경 및 report 대응을 확인했다. 초기 live-01/02의 error1·exit1은 역사 실패 그대로다. 마지막 정본/미러 T5 각1passed와 관련 각48passed·exit0, 각869 Python과 실행 전후 해시를 원보고에서 대조했다. 재실행한 유료/Lean/host 호출은 없고 manager의 확인은 원자료 검산과 순수 parser 재생이다.

기존 Lean4.32.0/Lake5.0.0/Mathlib v4.32.0에서 setup_lean의 대표 프로그램이 실제 import Mathlib·rfl·norm_num을 컴파일했다. 실제 identity와9의존 HEAD/manifest revision, 실행 파일/설치 입력 SHA,11094판단파일 전후 메타데이터와 신뢰 기록 바이트를 확인했다. 정상 선언의 수학적 내용과 미리 적은 서명에서 기대값을 얻으며 빈 공리·full32의존·정확 compiled input을 원out으로 재생했다. 타입 오류는 실제 exit1/failed/lean rejected와 진단에 연결된다. 각5Job의 request/status/실제 종료 관측과20판정, workspace 정리를 대조했다. 설치 신뢰 승인이나 연구 저장/평가 성공은 이 근거가 말하지 않는다.

새 corpus는 정상 원out71704바이트와 source/compiled input/빈 stderr의 원복사다. 제품이 줄인 stdout과 원out SHA가 다른 이유가 provenance에 기록돼 있다. full 옵션은 새 항목에만 명시돼 기존 두 Lean preview 및 다른18항목/verdict를 보존한다. 현재 각19항목·56파일·320687바이트, 총112경로 raw/clean·명시 SHA·양쪽 바이트와1314파일 --check를 확인했다. runtime124·공급자 입력3·host 입력/8원자료는 불변이고 승인된 성질만 재사용한다. 초기 도우미 타입/Calls 오류와 Mathlib 표기 교정은 최종 코드에 반영됐으며 과거 실패를 성공으로 다시 쓰지 않았다.

B38/8afa57c7의 formal/setup hunk를 현재 필수 git_backend 전달·identity별 memo·None/미추적/.lake 제외와 대조했다. 관련8 sim과 실제 경계 근거로 이 slice를 유지한다. 원보고10개가 현재 없는 한계와 PR02 전체 미종결을 유지한다. objective의 설계5.6은 현 설계에 없는 위치이며 실제3.3/4.5/5.1/8과9-C 내용으로 판정했다. 요구나 G를 줄이는 해석은 하지 않았다.

013은 단일 scheduler-smoke다. 현 실제 포트/PS/동결 bootstrap과 pythonw를 사용하고 새 시험 workspace의 제품 HOLD로 유료/기존 연구 경로를 차단한다. task 이름의 시작 부재·소유 action·등록/발화/해제 원자료와 마지막 부재를 요구한다. start 수락·옛 결과0·status만으로 발화를 인정하지 않는다. OS 정책/권한이나 runtime 수리는 이 task의 재량이 아니다. corpus/생성기/캐시와 OS 자원을 공유하므로 제품 task를 병렬 배정하지 않는다. 학술·T4 보고·나머지 문서/의미 질문·L01 외부결정·최종 관문은 남는다.

common-docs.diff에서 공용 갱신 전후를 대조했다. C2에012 검수, C5에013 자원 소유, C8에모델, C9에B38 한정 유지, C10에L01 미정과 독립 진행, C11에Lean 종결/예약 책임, C12에112경로와제품20경로 마감을 반영했다. 기존 C/G 의미·완료 기준·역사 예외와 미해결 조건은 보존한다. seam의 동작 변경이나 새 S는 없다. 다음 phase/objective와 관리 기록·기억을 먼저 확정하고 handoff 검사 뒤 manager.json 게시·정확 stage/commit 순서로 마감한다. 원보고/원자료는 수정하지 않는다.
