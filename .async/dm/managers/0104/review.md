# 0104: 중단된 G6 결과의 보존과 정확한 잔여 배정

이번 inbox는 g6p-run 종료1 사건 하나이며 running은 없다. sources/resume-g6-2026-10-18.md의 재개 지시와 mutation-recheck-direction-2026-10-17.md를 적용했다. manager0103의 source-review.json·candidate-diff.txt를 재사용하고 미완료 판단만 이어갔다. 제품 시험을 실행하지 않았다.

## 원실행과 후속 결과

g6p-run/report.json은 9묶음 시점의 중간본이다. 이를 완료 보고로 수정하지 않는다. 보존 execution-summary.json·assess-main.py는 원20묶음/1677함수의 누락 없는 연결과 killed1613·survived10·execution_error22·trivial32를 기록한다. 이번에는 이 기존 전수 연결을 재사용하며 모든 child를 새로 전수 감사하지 않았다. 당시 runtime123모듈은 현재 공용판과 후보판 모두 같은 SHA다. 원실행 결과는 최종 G6 성공이 아니다.

완료된 repair-b02/b03/b04/b05는 각각6/29/15/54함수를 기록하며, 그중 원문제7개에 대해 mutant 실제 비fixture 실패행, child exit0/finished, 대응 정상의 실제 passed행과 exit0/finished를 대조했다. 부모 exit1은 남은 사유 없는 listing 때문이고 미완료를 뜻하지 않는다. 104개를 원1613개에 단순 합산하지 않는다. 이미 수행한 모듈 단위 재확인을 새 배정의 방식으로 복사하지 않는다.

repair-summary.json의 repair-b09 부분15개도 오래됐다. 외부 원출력에는43개 outcome이 있으나 부모 mutation.json과 종료 기록이 없다. 원문제인 planning.review_basis_key, planning._shared_index, planning_engine.PlanningEngineMixin._ensure_model_assessments 세 함수만 raw outcome/attempt/result/spec와 정상7/10/23을 직접 대조했다. 변이와 정상의 각 child가 실제 exit0·finished이고 killed_by가 변이의 비fixture 실패행과 정상 passed행에 동시에 존재한다. 이 독립적으로 끝난 세 함수의 결과만 재사용한다. 배치 전체 완료로 승격하지 않는다. 필요한30파일을 managers/0104/evidence/repair-b09에 byte-exact 보존했다. raw 경로를 명령줄에 쓰는 Python 프로세스는 현재 조회되지 않았다.

LocalCLIAdapter.provider_failure는 docstring과 무조건 return None뿐인 현재 구현이며 pass와 동등하다. 원 survivor와 provider-failure-equivalence.json의 정확 사유/SHA를 유지한다. 따라서 원문제32개는 후속 해결10·동등1·미해결21(생존8/실행오류13)로 이어진다. 정확 module/function/rule과 출처는 remaining-functions.json이다. 원 killed1613·trivial32 및 위10개는 관련 판본/선택의 범위에서 재사용한다.

## 변경의 검토와 통합 보류

0103이 발견한300경로의 후보/공용 SHA를 다시 대조하여 변화 없음을 확인했다. 생성 항목256개와 실제 시험·설명44경로(정본31/기존 중간 미러13)가 섞여 있다. 정본 중19개는 현재 후보 미러와 다르다. 21개 경로는 중간 report.changes에도 없다. workspaces.py.integrate는 모든 실제 변경을 한 번에 처리하며 선택적 통합 기능은 없다. 이 상태를 통합하면 생성 캐시·실행용 index/timings·미완성 listing/미러와 잘못된 보고 연결이 함께 게시된다.

따라서 g6p-run은 **미수용·미통합 상태로 보존하고 cancelled에 추가**한다. 원 report·workspace·evidence는 편집하지 않았다. 원 task 재파견, 성공 표시, 사본 전체 덮어쓰기를 하지 않는다. 새 결과를 통합할 수 있게 만드는 일은 새 g6-finish가 맡는다. 실제 수용 가능한 새 결과가 없으므로 이번 integrate/accepted 추가는0이다.

정본31파일은 candidate/에 SHA와 함께 별도 보존했다. candidate-manifest.json은 원 baseline·현재 공용·후보 SHA와 새 task의 가져오기 규칙을 잇는다. 실제 diff는 기존0103/candidate-diff.txt다. 주요 변경은 callable 문서 표기, 제품 준비 실패를 실제 시험 본문에서 관측하도록 하는 예열/저장 fixture 조정, 유한한 합성 Sim 초기화, 제품 변이에 종속되지 않는 Job cleanup, 어댑터 효과·빈 관측 tick·builtin callback·생존 반환/반려/준비중단의 직접 단언이다. 기존 생산 순서·모집단·단언을 유지하는 변경이며 runtime 수리는 없다. 새 가족별 저장 입증이나 시험 quota를 추가하지 않는다.

정본 Python 후보들은 source-snapshot-r10과 같다. 정상 수리의 r8 19passed/1입력오류, r9 재실패, r10 정확1passed는 판본별로 보존하고 기존 reuse-impact/assertion-preservation과 원보고의 범위에서 사용한다. 이들을 최종판20개 전체 재실행으로 표현하지 않는다. 최종 미러 생성과 listing의 정확 갱신은 미완료다.

## 다음 작업과 남김

g6-finish는 수용된 mutation-parallel 공용판에서 시작하여 후보31파일만 비교·이식한다. 작은 정확 함수 선택을 기존 mutation 도구에 구현하고 미해결21개만 필요한 시험 입력과 함께 확인한다. 직접 관련 수리·listing·설명·미러·정확 보고까지 같은 task에 묶는다. 기존 `--only`가 모듈만 고른다는 이유로 이웃 정상함수를 실행하지 않는다. 원 전체20묶음, repair-arguments의 미실행 모듈 명령, 전체T3, 새 전수 준비를 재실행하지 않는다. 단일 명령 내 변이/정상 합계3슬롯이고 다른 시험 명령과 겹치지 않는다.

이번 후보와 선택 도구·수리·listing은 같은 결과를 완성하는 연관 작업이며 새 독립 기능 결함은 확인되지 않았다. 이들을 인위적으로 나누거나 G1~G3 문서 작업을 실행 선행으로 추가하지 않는다. 수용 후 최종 연결과 후속 관문을 이어간다. G1~G3 최종 연결, 원G4/전체T3의 판본 구분, G5 환경6arc/10행 및 부분index/자동재사용 한계, G7 L01 Q1/Q2/원UTF-8 byte·현재 공급자 조건, G8 최종 review는 열린 상태다. 저장 A22의 공통 보장 재사용과 지정5모듈만 추가T3 지시는 유지한다.

queue는123정의/accepted116/cancelled6/미해결1, active로 준비한다. 기존122개 정의와 objective는 그대로이며 새 g6-finish만 추가한다. 공용 context/plan/seams와 objective를 먼저 완성하고 queue.pending.json을 check.py queue로 검사한 뒤 queue.json으로 원자 교체한다. 그 게시가 이번 manager의 마지막 공용 변경이다.
