import hashlib
import json
from pathlib import Path

ROOT = Path(r'C:\math')
RUN = ROOT / 'docs/do-math/continuous-development-2026-10-13'
OUT = Path(__file__).resolve().parent

def replace(path, old, new):
    text = path.read_text(encoding='utf-8')
    assert text.count(old) == 1, old
    path.write_text(text.replace(old,new),encoding='utf-8',newline='\n')

replace(RUN/'context.md',
    '현재 phase 007 작업자(PID 33604)는 기존 `gpt-6-astra` / `max` 세션을 끝까지 유지하고, 새 실행기가 그 종료를 기다린 뒤 007 manager부터 새 설정으로 호출한다. 원 실행기는 작업자를 종료하지 않고 교체했으며 task와 로그를 재실행·덮어쓰지 않는다.',
    '모델 전환 당시 phase 007 작업자(PID 33604)는 기존 `gpt-6-astra` / `max` 세션을 유지했다. 교체 실행기는 그 작업자의 exit 0을 확인한 뒤 007 manager를 새 설정으로 호출했다. 검수 때 상태는 manager_running이었으며 관찰 사본은 run:phases/007/manager-evidence/model-policy-observation.json에 있다. 원 실행기는 작업자를 종료하지 않고 교체했고 task와 로그도 재실행·덮어쓰지 않았다.')
replace(RUN/'context.md', '1-A의 원문 인용은 보존하되 A20의 필수+선택 필드 역방향을 적용한다.',
    '1-A의 원문 인용은 보존하되 A20의 필수+선택 필드 역방향을 적용한다. 이 역방향 검사는 수신자가 선언한 필수·선택 필드 전부가 실제 생산 표본에서 나오는지 확인한다.')
replace(RUN/'context.md', 'L01은 실제 운전 host/tool/version/read-call과 같은 단위의 한도가 미확정이다.',
    'L01은 실제 운전의 host/tool/version/read-call별 읽기·출력 한도와 그 측정 단위(byte 또는 token)가 미확정이다.')
replace(RUN/'phases/008/tasks/document-recovery/objective.md',
    '전체 field_schemas/scoped_field_issues 검사는 실제 반환을 검증할 책임이 명시된 경계만 위임하며, 위임 목록 오기·누락·타 경계의 임의 통과를 거부한다.',
    '일반 문서 순회(field_schemas/scoped_field_issues)는 실제 반환 객체 없이 판정할 수 없는 소유자만 그 객체를 생산하는 회귀 검사에 맡긴다. 작업자는 넘긴 소유자 ID와 담당 시험을 대응시켜 실제 검사가 빠지지 않았음을 확인한다. 기존 defer_* 방식을 재사용할 수 있으나 목록의 오기·누락이나 다른 소유자를 함께 건너뛰는 경우를 검사로 거부해야 한다. 이 책임을 구현하는 구체적 함수 구성은 재량이다.')
replace(OUT/'review.md',
    '최초 snapshot에 없거나 줄끝 때문에 비교되지 않은9파일은 현재 전체 Git diff가 보고된 Codex 전송 문장·corpus verbatim 규칙·생성기 반례와 일치하는지 직접 확인한다.',
    '최초 snapshot에 없거나 바이트 해시가 HEAD와 직접 대응하지 않은9파일은 현재 전체 Git diff를 직접 대조했다. 차이는 검수된 Codex 전송 문장·corpus verbatim 규칙·생성기 반례와 일치한다. 추가 diff --check의 exit 2는 원바이트를 보존한 양쪽 manifest의 공백 표시에 한정됐다. corpus 밖124파일 후보의 나머지는 exit 0이며 manifest는 내용·명시SHA·raw/clean 검산을 통과해 재작성하지 않는다. 원출력과 처분은 product-diff-check.json 및 product-diff-check-review.json에 보존한다.')
replace(OUT/'prepare_decision.py',
    "    'C10': 'P01과 N03-003 확정 불일치를008의 정확한 책임으로 연결했다. 다른 packet·L01 남김은 유지한다.',",
    "    'C9': 'A20 역방향의 의미를 수신 필수·선택 필드 전체와 실제 생산 표본의 대응으로 풀어 썼다. 기존 보존 성질·원문 좌표·이전 검토 범위는 유지한다.',\n    'C10': 'P01과 N03-003 확정 불일치를008의 정확한 책임으로 연결했다. L01의 실행 조건과 측정 단위를 구별해 표현했고 한도 미확정·다른 packet 남김은 유지한다.',")
files = [ROOT/'services/continuous-development/protocol.md', RUN/'context.md', RUN/'plan.md', RUN/'seams.md',
         RUN/'phases/008/phase.json', RUN/'phases/008/tasks/document-recovery/objective.md', OUT/'review.md', ROOT/'기억/layer1/M-0557.md']
(OUT/'handoff-reading.md').write_text('\n\n'.join('# 입력 문서: '+p.relative_to(ROOT).as_posix()+'\n\n'+p.read_text(encoding='utf-8') for p in files),encoding='utf-8',newline='\n')
(OUT/'reading-inputs.json').write_text(json.dumps({p.relative_to(ROOT).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in files},ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
print('Updated current model-transition state and clarified the four accepted reading findings.')
