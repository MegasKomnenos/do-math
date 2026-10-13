"""Improve report prose without changing findings, source, or test judgments."""
import json
from run_command import EVIDENCE, write_json

path = EVIDENCE.parent / 'report.json'
report = json.loads(path.read_bytes())
(EVIDENCE / 'format-check-command/report.json').write_bytes(path.read_bytes())
acceptance = {
 'A1': '시작 소스와 Git 상태, phase 005 종료 자료, 원 Codex 오류·schema·prompt·worker 및 공식 선택/row/exit를 결속했다. maintenance·repair·probe의 실제 비결박 소비와 연구 중앙 제출을 구분했다. 부재/null/중첩/추가 필드 제약, 현재 CLI·모델 입력과 공식 공급자 제약을 근거로 표현을 정했다. B49의 한정 slice에서 역사 원보고가 없는 사실도 기록했다.',
 'A2': '원 schema와 prompt를 보존하며 Codex 봉투의 전달·해석을 제품의 한 정의에서 처리한다. 의미 값은 기존 원 검증을 거치며 부재/null/빈 값/중첩 값을 합치지 않는다. native final·worker hash·종료 및 Claude/control_binding의 계약을 유지했고, 실제 CLI가 전달 형식을 수락한 증거가 있다. provider_final은 기존 layer 1과 identity 목록에 이미 포함되어 새 등록이나 범용 변환기는 필요하지 않았다.',
 'A3': '핵심 의미 보존과 오류 검출, 기존 native/종료/Claude/bound 회귀를 확인했다. 현재 전송 계약을 읽는 외부 대역으로 실제 probe 소비도 통과했다. 그러나 직접 소비 검사 45건 중 11건이 배정 밖 fixture에서 실패했고, 통과하는 contracts.pairs에도 성공 표본 누락이 있다. 후속 수정 대상과 미실행 예측 사례를 F2/F3에 명시했으며 전체 관련 회귀 완료를 주장하지 않는다.',
 'A4': '허용 범위의 오프라인 핵심 수리 뒤 Codex 대표 실호출을 한 번 수행했다. 공식 1선택/1passed/exit 0과 11개 판정을 확인했다. 실제 worker schema snapshot·argv 해시·원 final·의미 output·파일 읽기·checkpoint·종료가 대응한다. 새 Claude 호출은 없으며, 비변경 경로의 원자료 재수신·판본·입력 대조를 근거로 phase 003 성공을 한정 재사용했다. 미보고 비용과 실제 모델명을 추정하지 않았다.',
 'A5': '녹화·문서·공식 미러, 양쪽 corpus 전건 검사, Git 바이트와 최종 해시 인도는 완료했다. 기존 17항목이 불변이며 각 18항목/51파일/50개 SHA, 102경로 raw=clean, 정본 18passed/미러 14passed 및 --check/skill-only 통과를 확인했다. 다만 이 조건에 포함된 관련 회귀 전건 통과는 A3의 11건과 F3 때문에 미충족이므로 완료로 올리지 않는다.',
}
for row in report['acceptance']:
    row['detail'] = acceptance[row['id']]
findings = {
 'F1': (
  'phase 003의 Codex maintenance schema 거부는 원 계약을 보존하는 문자열 봉투 수리 후 실제 대표 호출에서 해소됐다. 명시 model=gpt-6-astra/effort=low, CLI 0.162.1이며 1회/1passed/11개 판정 true다. 원/전송 schema와 실제 raw/worker/종료를 새 녹화에 보존했다. G7 전체의 충족으로 확대하지 않는다.',
  'manager가 phase 003 F1의 대표 역할 전달 실패를 새 근거로 처분한다. 후속 fixture만 바뀌고 제품 실행 경로가 불변이면 이번 유료 호출을 재사용할 수 있다. 다른 G7 연쇄는 별도로 배정한다.'),
 'F2': (
  'consumers의 45선택 중 11실패는 새 Codex 전송 형식과 배정 밖 fixture의 불일치다. support.operator_finish_scene는 CLI schema의 최상위 속성을 의미 schema로 읽고, support.operator_probe_inputs는 nonce 속성을 직접 찾는다. sim.test_operator_finish_recovery의 한 단언도 call.schema가 원 schema와 같기를 요구한다. flows.test_provider_native_storage의 한 시험은 명시 stdout/final을 구 {}로 제공한다. 이 자료를 자동 재작성하거나 제품에 구형 fallback을 넣지 않았다. 추가 정적 조회에서는 sim.test_observation_delivery의 단일 chunk 시험에도 같은 구 final/completed 기대가 있는 것을 확인했으며, 이 시험은 이번에 실행하지 않았다.',
  '새 work에서 해당 정본·미러 파일을 writes에 포함하고, 전송 schema와 원 semantic schema를 명시적으로 구분하도록 외부 CLI fixture를 교체한다. 원 관찰 바이트·수치·오류·정산 단언을 유지하면서 11개 실패와 단일 chunk 시험을 재검증한다. malformed raw ingress도 원 collector 반려가 출력 형식 반려에 가려지지 않는지 확인한다. 이 불일치를 허용된 잔여사항으로 닫지 않는다.'),
 'F3': (
  'contracts.pairs._runner_result_samples의 두 비결박 collected 표본에는 실제 collector가 항상 생산하는 source_request가 없다. 현재 classify_run은 공급자를 그 검증된 요청에서 판별하므로 두 표본은 output_validation/KeyError source_request가 된다. Pair 검사는 결과의 저장 가능성만 보아 여전히 통과하며 비결박 성공 branch의 검증을 잃는다. 실제 수집 성공과 구별되는 시험 공백이고 이 fixture도 writes 밖이다.',
  '같은 후속 fixture 작업에서 실제 collection의 요청·원바이트 계약을 따르는 성공·결박·실패·정지 표본을 만든다. 표본 이름에 의존하지 않고 실제 status와 분기를 검사한다. 실제 ModelRunner/collector를 가리는 대역이나 누락 요청 fallback으로 해결하지 않는다.'),
 'F4': (
  'Claude와 기존 background의 승인된 성질은 한정 재사용한다. Claude 원 smoke를 현재 parser/collection_reasons/classify_run으로 다시 받아 completed와 정확한 output을 확인했다. prompt/schema, 도구 관련 12개 모듈, 설치 경로·버전·help가 같았다. 역사 surface identity는 빈 객체이므로 당시 CLI 바이너리 SHA의 동등성은 입증하지 않는다. 도구·입력 조건을 유지하며 Codex 분기만 바뀐 점과 실제 경로를 사용하는 Claude 회귀에 근거한다. 새 유료 Claude 호출은 없다.',
  'manager는 재사용 범위와 역사 바이너리 SHA가 미기록인 한계를 유지한다. 이후 Claude 실행·입력·도구 조건이 바뀌면 영향을 받는 대표 실호출을 배정한다. background·연구 저장·G7 전체 성공으로 확대하지 않는다.'),
}
for row in report['findings']:
    row['detail'], row['next_action'] = findings[row['id']]
write_json(path,report)
print('Report prose clarified; partial and A1/A2/A4 pass, A3/A5 fail unchanged.')
