import hashlib
import json
from pathlib import Path

ROOT=Path(r'C:\math')
RUN=ROOT/'docs/do-math/continuous-development-2026-10-13'
OUT=Path(__file__).resolve().parent

def replace(p, old, new):
    s=p.read_text(encoding='utf-8')
    assert s.count(old)==1, old
    p.write_text(s.replace(old,new),encoding='utf-8',newline='\n')

replace(RUN/'context.md',
    '두 동명 생산자 오류를 구별해야 한다. 운영-점검.md의 operational_evidence.checkpoint_source와 recovery_materials 안의 result_source/checkpoint_source는 일반 재개 restore_continuation의 결과로 대신 입증할 수 없다.',
    '문서 결속은 실행 중 operational_evidence.checkpoint_source와 종료 후 recovery_materials.result_source/checkpoint_source의 생산 객체를 구별해야 한다. 일반 재개 restore_continuation의 반환으로 이 운영/복구 필드들을 대신 입증할 수 없다.')
replace(RUN/'context.md','F3의 한정 재사용을 승인했다. 보존된 Claude background',
    'phase 003 F3의 한정 재사용을 승인했다. 보존된 Claude background')
replace(RUN/'seams.md',
    'phase 006이 구현한 Codex 비결박 전송의 정본은',
    'phase 006의 비결박 경로는 중앙 제출 control_binding 없이 CLI 최종 응답을 직접 받는 ModelRunner 호출이다. 이 Codex 전송의 정본은')
replace(RUN/'phases/008/tasks/document-recovery/objective.md',
    'C8에 기록된 운영자 작문 도구4파일 차이와 이후 manager의 공용 문서/기억·Git 변경을 제품 변화와 구별한다.',
    'C2와007 manager verification에 기록된 운영자 작문 도구4파일 차이 및 이후 manager의 공용 문서/기억·Git 변경을 제품 변화와 구별한다. 모델 선택 정책은 C8을 따른다.')
replace(RUN/'phases/008/tasks/document-recovery/objective.md',
    '일반 문서 순회(field_schemas/scoped_field_issues)는 실제 반환 객체 없이 판정할 수 없는 소유자만 그 객체를 생산하는 회귀 검사에 맡긴다. 작업자는 넘긴 소유자 ID와 담당 시험을 대응시켜 실제 검사가 빠지지 않았음을 확인한다. 기존 defer_* 방식을 재사용할 수 있으나 목록의 오기·누락이나 다른 소유자를 함께 건너뛰는 경우를 검사로 거부해야 한다. 이 책임을 구현하는 구체적 함수 구성은 재량이다.',
    '문서 검사에서 입력 이름은 field_schemas()가 반환하는 dict의 키이며, 문서 필드 경로의 첫 이름이다. 예를 들어 operational_evidence.checkpoint_source.local_path의 입력 이름은 operational_evidence이고, recovery_materials.result_source.local_path의 입력 이름은 recovery_materials다. 이 두 입력의 구조를 AST 추정에서 실제 반환 검사로 옮기면, 일반 문서 순회는 실제 객체를 받는 회귀 시험에 그 검사를 맡겨야 한다. 작업자는 각 입력 이름을 실제 객체를 제공하는 시험 메서드와 대응시키고 해당 메서드가 문서의 필드를 검사하는지 확인한다. 기존 defer_* 방식처럼 일반 순회에서 이 검사를 잠시 건너뛰는 목록을 사용한다면, 이름 오기·빠진 담당 시험·다른 입력까지 함께 건너뛰는 경우를 검사로 거부한다. 함수 구성은 재량이며 새로운 전역 등록부를 요구하지 않는다.')
replace(OUT/'review.md','corpus 밖124파일 후보의 나머지는 exit 0이며',
    '124개 전체 후보 중 Git diff가 검사한 corpus 외부 변경은 exit 0이며')
files=[ROOT/'services/continuous-development/protocol.md',RUN/'context.md',RUN/'plan.md',RUN/'seams.md',
       RUN/'phases/008/phase.json',RUN/'phases/008/tasks/document-recovery/objective.md',OUT/'review.md',ROOT/'기억/layer1/M-0557.md']
(OUT/'handoff-reading.md').write_text('\n\n'.join('# 입력 문서: '+p.relative_to(ROOT).as_posix()+'\n\n'+p.read_text(encoding='utf-8') for p in files),encoding='utf-8',newline='\n')
(OUT/'reading-inputs.json').write_text(json.dumps({p.relative_to(ROOT).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in files},ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
print('Resolved source coordinates, precise parser input names and the Git diff population.')
