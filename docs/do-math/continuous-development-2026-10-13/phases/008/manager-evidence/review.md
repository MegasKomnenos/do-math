# phase 008 manager 검수

document-recovery는 partial로 수신한다. A1~A4의 지정 성과를 승인하고 A5의 실패는009 document-callable로 넘긴다. report 형식 검사를 공용 문서 갱신 전에 실행했고, verify.py가 현재 파일·공식 원보고·실제 명령 종료·HEAD 원문을 대조했다. 이 검수는 최종 review phase가 아니다.

## 성과와 보존 범위

종료2640파일은 현재와 모두 같다.007 종료와008 시작의 차이는 이미 승인된 모델 정책의 작문 도구4파일이다.008의30변경은 report changes와 writes에 정확히 일치하며 양쪽 비용 캐시2개를 포함한다. runtime124·smoke입력3·corpus102경로는 불변이고 corpus 전건의 raw/clean을 실제 Git argv로 다시 확인했다.

운영-점검 및 CLI P01 문장을 core_engine._context의 evidence·recover·result_kind·checkpoint_source 분기와 대조했다. 두 입력을 다른 생산자의 동명 필드로 대신 증명하지 않는다. actual 객체별 문서 순회와 helper의 파일 읽기·hash/size/snapshot/원 artifact 대조, 오류 자료의 local_path 부재, null과 live 부재 검사를 확인했다. 반환 사본 교란과 실제 제품의 손상 입력 반려는 서로 다른 검사다. fixture의 UUID artifact는 재사용 template 저장소의 불변 경로 정체성을 지키며 제품 cache나 반려 조건을 바꾸지 않았다.

두 defer 입력의 담당 메서드와 실제 문서 검사 호출을 확인하는 AST 사용은 호출 책임의 검증이다. 제품의 최종 반환을 AST dict로 추정하던6지점은 실제 객체 검사로 대체됐으며 남은 일반 재개/B132~B134 경계를 유지했다. 빈 배열과 오류/null이 모든 모양을 입증하지는 않으므로 채워진 정상 표본·정확 손상 반례를 함께 확인했다. 구체적 파일/단언은 product.diff 및 task binding-review.md가 가리킨다.

독립-운영의 한 문장을 bootstrap.main의 manifest/snapshot_root 및 scheduled_operator.main의 installation_root 전달과 대조했다. 기존 bootstrap-info2건은 양쪽 최종 보고에서 passed다. N03 전체 이름 검토를 닫은 것은 아니다.

## 실패와 후속 결정

8개 공식 실행의 선택/고유row/실제exit와 Python 실행 전후 해시를 대조했다. 초기 red2건은 최종 동일 ID가 passed다. 중간 fixture/defer 오류는 최종에서 사라졌다. 정본110개 중106passed·4failed, 미러89개 중85passed·4failed이며 skip/error/미실행 없이 complete=true, successful=false다. 양쪽 최종 보고의 Python865파일이 현재와 일치한다. 생성 계획15경로와 비용 캐시1경로 재동기화, --check1305파일 및 skill-only verified의 exit0과 불변 판본을 확인했다.

네 실패의 원인은 CLI-실행-계약의 `provider_final.output_contract` 표기다. 현재와 HEAD의 정규화 문서 및 당시 helper 모두 이를 unowned 상태 필드로 읽는다. 해당 callable은 실제 존재하고, 현 function_reference_issues가 `provider_final.output_contract(...)`를 실제 함수로 검사함을 직접 확인했다. 이 결과는 텍스트/helper의 기준 판본 재현이며 과거 전체 시험을 다시 실행한 결과가 아니다. raw 개행 해시와 정규화 문서를 구별한다.

F1은 유효한 issue이며009에 carry한다.008 objective는 CLI의 P01 문장만 수정하도록 명시했으므로 작업자가 공급자 절의 표기를 범위 밖으로 보고한 판단을 승인한다. 다음 배정은 이 표기를 기존 함수 검사 경로에 연결하는 문서 변경이다. unknown owner 예외나 schema·runtime·시험 helper 수리는 필요하지 않다. 마지막 실패 원인을 닫은 뒤008의 문서·시험 단위를 함께 커밋한다.

F2는 해소된 보존 사실로 resolve한다. runtime/corpus 불변은 앞선 공급자 호출의 승인된 성질을 무효화하지 않는다. 제품 문서와 시험은 달라졌으므로 최종 일반/T3/변이/review는 새 판본 책임을 유지한다. G7의 다른 실제 연쇄와 나머지 의미·문서 질문도 그대로 남는다.

## 배정과 인도

009는 단일 work task다. 같은 문서와 전건 문서 순회·비용 캐시·미러 생성에 의존하는 작업을 나눠 병렬 실행하면 판본이 흔들린다. 다른 G7 실연쇄도 최종 설치 문서·shared cache/corpus를 사용하므로 이 짧은 수리 뒤에 배정한다. 읽기 전용 분석을 추가해 phase 수를 늘릴 필요는 없다. 모델은 정책대로 gpt-6.1-sol/high다.

관리 커밋에는 공용 현재본,009 배정,008 report·원근거·검수와 layer1 노드 하나를 담는다. 제품30경로는 검증 실패가 남아 staged 제품으로 제출하지 않으며 raw archive로 현재 바이트를 보존한다. archive는 당시 판본의 근거이지 자동 복원 명령이 아니다. 정확 보존 경로/해시는 preservation.json, Git 수신 기록은 로컬 commit.json에 둔다. 기존 dirty와 운영자 변경을 정리하거나 포함하지 않는다.
