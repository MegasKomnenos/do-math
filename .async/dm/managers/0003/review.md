# r07 수용과 소유권 수리 배정

0003 inbox의 완료 사건은 r07이며 r18·r02-fix는 시작 당시 실행 중이었다. 기존 task의 spec은 유지한다. 이후 도착하는 사건은 다음 manager가 처리한다.

r07의 모집단 대응 조사는 완료로 수용한다. report 검사는 PASS이며 `workspaces.py integrate C:/math C:/math/.async/dm r07`은 `{"task":"r07","files":[]}`를 기록했다. 제품 변경·새 제품 시험·외부 호출은 없다. 수용은 조사 완료를 뜻하며 1-E 전체 충족이나 제품 전체 합격을 뜻하지 않는다.

## 직접 확인한 근거와 처분

현재 `provider_final.py:output_contract`, `values.py:json_copy`, `test_schema_builders.py`의 탐색·호출 목록·격리 단언, `이음새-정본.md` 5절, `model_runner.py:ModelRunner.run`, 기존 `sim/test_provider_schema.py`의 실제 단언을 읽었다. r07이 읽은 workspace 소스 29파일의 해시를 공용 소스와 대조해 모두 일치함을 확인했다. 정확 경로와 해시는 source-review.json에 있다.

F1은 실제 등록 공백이다. output_contract는 Codex/Claude용 schema dict를 반환하지만 세 호출 목록과 transformer/delegate 표에 없고 이름 탐색에도 걸리지 않는다. 기존 provider schema 시험은 Codex의 값·전송·입력 보존을 확인하며 반환 ID 격리나 Claude의 별칭은 확인하지 않는다. `_composition_calls`의 기존 반복 ID 검사에 두 분기를 넣으면 공백을 닫을 수 있다. 이름 탐색을 보편적인 반환 분석기로 확장할 이유는 없다.

F2는 기존 정본 5절의 결과 내부 격리 위반이다. 두 속성에 같은 leaf를 넣은 입력에서 deepcopy는 별칭을 보존하며, r07의 원 FunctionDef 순수 계산은 Claude의 형제 필드 변경을 관측했다. 원 입력·다른 반환은 불변이었다. probe의 소스 SHA가 현재 원문과 같음을 확인했다. manager는 이 계산을 재실행하지 않았으며 새 런타임 검증을 주장하지 않는다. 기존 json_copy가 요구된 분리를 제공하므로 이를 사용하는 수리를 배정한다.

현재 ModelRunner는 Codex에서만 output_contract를 호출하고 Claude는 원 schema를 바로 JSON으로 쓴다. F2를 Claude 실제 전송 실패나 원문 1-E의 다른 결과/전역 공유 실패로 확대하지 않는다. 공개 builder의 현재 계약과 검사 등록을 맞추는 수정은 같은 파일·성질에 속하므로 F1과 함께 처리한다.

ownership-map.json 39행과 registration-edition-comparison.json의 기존 38항목 유지 판정은 r07의 유한 범위에서 수용한다. 기존 named12/67변형, composition13/25변형, class4와 constant6 등의 입력축·borrowed 처분을 다시 구현하지 않는다. 정적 모집단 판정은 최종 전체 실행 증거가 아니다. PR06 중 B22 slice와 K-51의 제품 정본 소비 성질을 유지하되 저장/null/형식·windowless 및 다른 K/P2 전체로 넓히지 않는다.

보존 B116/schema 및 B117/related-before-fixture-fix 원보고를 직접 읽고 해시·schema 고유 row 8개/11개와 모두 passed를 확인했다. B117 전체 successful=false는 유지했다. Temp 원보고 5개의 현재 부재도 확인했다. 과거 결과를 합산하거나 전체 최종 판본 성공으로 승격하지 않는다. source-review.json은 이 최소 대조의 재현 결과다.

## 후속 작업과 병렬 경계

`r07-fix`는 r07만 선행으로 한다. provider_final·test_schema_builders·관련 정본 설명과 각 미러를 한 담당자가 고친다. 수리 전 최소 ID와 수리 후 구조 모듈을 공식 runner jobs1로 확인한다. 실제 불확실성이 없으면 provider 전반이나 전체 관문을 반복하지 않는다. 세부 입력·기대값·한계는 tasks/r07-fix/objective.md에 있다.

r18은 읽기 작업이며 r02-fix와 의미 있는 수정 파일은 겹치지 않는다. 두 수리 작업의 공식 runner가 각 사본의 .timings.json을 갱신할 수 있지만 비용 캐시 때문에 독립 수리를 직렬화할 필요는 없다. r07-fix는 그 자료를 자기 evidence에 보존한 뒤 자기 base의 두 캐시 원바이트로 복원해 최종 제품 delta에서 제외한다. r02-fix의 배정은 변경하지 않는다. 검증 증거는 공식 결과에 남는다.

## 공용 상태와 게시

R07/1-E는 모집단 읽기 완료·F1/F2 수리 대기다. G4~G8 및 이전 판본 한계, L01 Q1/Q2·UTF-8 byte, Windows1314 symlink 실반려 미검사와 다른 의미 미결은 유지한다. r02-fix와 r18의 결과는 이번에 판단하지 않는다.

context·plan·seams·objective를 먼저 갱신하고 기존 queue에 r07-fix와 accepted r07을 더한 임시파일을 만든다. 검사 후 그 파일을 queue.json으로 원자 교체한다. 상태는 active다. 제품 변경이 없어 이번 manager의 제품 commit은 없다. 게시 후 공용 변경은 종료한다.
