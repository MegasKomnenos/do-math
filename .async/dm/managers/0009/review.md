# manager 0009: r05 수용과 관찰·공급자 입구 후속

이번 inbox의 완료 사건은 r05이고 시작 당시 실행 중인 작업은 r03·r14다. 두 작업의 정의와 고정 입력을 유지했다. manager 도중 발생한 다른 완료 사건은 이번 수용에 포함하지 않는다.

## 수용 판단

r05의 실제 base/workspace 차이는 보고한 정본 시험/helper5·미러5와 일치한다. 변경 전 공용 파일은 각각 base와 같았고 다섯 미러 쌍의 원바이트도 같다. 관련 runtime·helper21파일은 base/workspace/공용판에서 일치한다. report 검사 PASS 뒤 workspaces.py integrate로 10파일을 충돌 없이 통합했다. integration.json에 실제 경로가 있으며 queue.accepted에 r05를 추가한다. manager가 제품을 직접 수정하거나 제품 시험을 새로 실행하지 않았다.

공급자 사건은 두 실제 worker/runner/collector와 owner/store를 거쳐 9 JSON 축을 검사한다. 안전 저장 영역 밖 숫자의 공개 내용은 compact JSON 문자열이고 영수증의 숫자는 json_safe 투영이다. 원 stream·artifact bytes, offset, SHA와 투영의 서로 다른 책임을 확인했다. 저장 float/큰 정수/bytes 반려는 정확 사유와 caller/head/상태 불변을 단언한다. 관련 변경은 기존 숫자·정상 후속·중복·StateContract 검사를 보존한다.

학술 요구 ID는 scholarly 설정이 아닌 academic.requirement_record의 문자열 ID다. exact Unicode·주변 공백·독립 직렬화 해시와 trim된 다른 ID의 조회 반려를 검사한다. _requirement의 생략/명시 null grant_id 생산과 effect_receipts의 null 의미를 직접 확인한다. 모델 extension은 load_extensions의 안전 값 검사와 check_submission의 실제 형식/의미/integration·해시 소비를 연결한다. 파일 부재·알려진 빈 list 가족과 root/family null의 다른 처분은 현행 정의와 일치한다. 실제 charter 승인·지식 적용·scheduler 정산의 새 실행 증거로 확대하지 않는다.

세 공식 원보고의 선택/실제 고유 row·하위 report·SHA를 대조했다. focused-1은8선택/7passed/1failed, related-final은44선택/43passed/1failed다. 실패는 새 maintenance fixture의 snapshot 누락과 새 단언의 integration 배열 가족 오류 누락이며 현재 계약과 대조해 수정됐다. 마지막 extension-final은5선택/5passed이고 Python876해시가 제출판과 모두 같다. related-final 이후 Python 변경은 그 새 모듈 하나뿐이므로 나머지39passed를 변경 없는 관련 코드의 근거로 유지한다. 39+5를 단일 최종판44전건 통과로 표현하지 않는다. exit1/1/0은 task 관측 기록이며 manager 재실행 결과가 아니다. 실행 중 변경·fixture 오류는 원보고에서 없고 비용 캐시 두 개는 증거 보존 후 base로 복원됐다. 상세 대조는 source-review.json과 inspect_result.py다.

R05/1-C의 네 값 경계 질문과 확인된 시험 수리는 해결·최종 통합판 증거 대기로 옮긴다. R06은 tasks/r05/evidence/boundary-map.json의 null slice만 판단한다. deadline_only의 followup은 현재 생략이며 생산되지 않는 followup=None 고장을 주장하지 않는다. PR15/B35·PR06/B58·K-51/76/78·P2 C-03의 지정 성질만 유지하고 나머지 모집단과 과거 Temp 원보고 부재는 남긴다. G4~G8, L01 Q1/Q2·원문 UTF-8 byte, Windows1314 실제 symlink 반려 미검사는 해소되지 않았다.

## 다음 배정

r10은 R10/2-A 관찰·공급자 입구의 반려/양순서/재전달을 기존 세 ingress 시험과 provider_native_inputs에서 판정하고 확인된 수리·미러·최소 확인을 한 번에 맡는다. r05의 공유 helper와 followup 단언을 보존해야 하므로 r05만 선행이다. r03의 저장 record 계약과 r14의 진행성/정산은 별도 질문이고, r10은 그 중간 결과를 요구하지 않는다. 비용 캐시 이외의 쓰기 경로는 두 진행 중 작업과 겹치지 않는다.

이미 있는 raw7축×공급자2×mode3·결속/충돌 양순서·native 재전달 검사를 다시 만드는 작업이 아니다. 충분한 실제 정의/단언/원보고를 유지하고 현재 누락만 수리한다. 관찰 입력의 상태 소실은 실제 owner의 실행 전제와 종결 뒤 사실 보존 계약에 맞게 판단한다. 모든 입구의 같은 반려를 임의 강제하지 않는다. 해당 입구의 실제 runtime 고장이 확인되면 지정한 수신·owner 파일에서 현행 계약을 유지해 함께 고칠 수 있다. 변경이 없으면 새 시험도 요구하지 않는다.

R06 전 제품 null 모집단, R08 공개 제어·수송, R09 제출 입구, R15/R16 전체 반환 조합은 그대로 남는다. R10 완료를 2-A 전체 완료로 쓰지 않는다. 공용 문서와 objective를 먼저 완성하고 queue.pending.json을 check.py queue로 검사한 뒤 그 파일만 queue.json으로 원자 교체한다. status는 active를 유지한다.
