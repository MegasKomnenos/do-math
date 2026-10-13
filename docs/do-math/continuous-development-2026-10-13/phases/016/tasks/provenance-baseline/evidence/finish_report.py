"""Write the task report from preserved observations, without touching product state."""
import json
import subprocess
from pathlib import Path
from investigate import REPO, RUN, OUT, sha, write

base='run:phases/016/tasks/provenance-baseline/evidence/'
def refs(*names):
    return [base+name for name in names]

inputs=json.loads((OUT/'input-manifest.json').read_text(encoding='utf-8'))
final=[]
for row in inputs:
    kind,rel=row['reference'].split(':',1)
    path=(REPO if kind=='repo' else RUN)/rel
    actual=sha(path.read_bytes())
    assert actual==row['sha256'],row['reference']
    final.append(dict(reference=row['reference'],start_sha256=row['sha256'],end_sha256=actual,equal=True))
write('input-final-comparison.json',dict(files=final,all_equal=True,
    scope='Assigned inputs/common documents only. No claim about other task writes or whole working-tree cleanliness.'))
checks=[]
for p in sorted(OUT.glob('*.command.json')):
    record=json.loads(p.read_text(encoding='utf-8'))
    assert record['exit_code']==0,p.name
    names=[p.name]
    for key in ('stdout','stderr','stdin','stdout_original'):
        value=record.get(key)
        if value and (OUT/value).is_file() and value not in names:
            names.append(value)
    checks.append(dict(command=subprocess.list2cmdline(record['argv']),cwd='repo:.',result='pass',
        exit_code=record['exit_code'],evidence=refs(*names),
        detail='실제 argv/cwd/exit와 원출력을 보존한 Git 읽기/정적 입력 검증이다. 제품 import나 시험 실행 성공을 뜻하지 않는다.'))

report=dict(
    status='complete',
    narrative='공유 입력 provenance 도입 commit bbe64043f49d46fb7c3b6e768b99a8acbaa125cf의 실제 diff/첫 부모와 PR01/B56 원기록·도입 당시 M-0472를 대조해 pre-fix 010b059700115f6d5d3df1bf24e931cf78eaa44a를 확정했다. 당시에도 같은 baseline을 사용했다는 명시 기록이 있다. 현재보다 오래된 날짜나 다른 경로만으로 선정하지 않았다.\n\n해당 commit canonical scripts의 추적 파일910개/9,901,995바이트를 자기 evidence/pre-provenance/scripts에 Git blob 원바이트로 추출했다. manifest에 전 경로/mode/blob/SHA256/크기와 commit/tree/명령을 남겼다. 새 Git 객체 조회로 전건 readback을 재검산했고 파일 모집단·바이트·Git object ID·SHA가 모두 같았다. 경로 이탈/symlink/gitlink/Windows 충돌/reparse point를 거부하고 현재 파일·Git index·공용 문서·미러·캐시·설치를 수정하지 않았다.\n\n기존 비교의 ordinary 결과/읽기 횟수와 literal entered(빈 label 포함)/opens/import_opens/coverage의 files-contexts-lines-arcs 보존, 명시 shared marker 차이와 두 worker raw union을 읽었다. baseline의 공통 측정/runner API와 새 API 부재, baseline mode의 새 API 비호출을 AST로 확인했다. 상대 writes 밖의 세 정의는015 source-inspected와 작업 시작/끝 해시가 같다. 배정 입력과 공용문서19개도 끝까지 불변이다.\n\n후속 SHARED_INPUT_BASELINE_SCRIPTS 절대 경로, 정본/미러의 두 정확 ID 및 전체 T4 공식 명령, raw snapshot의 teardown 전 보존 방법과 소스/도구 판본 기록을 review.md에 인계했다. 제품 import/시험/old-new 실행은 배정상 수행하지 않았으므로 입력 준비 완료만 주장한다.015의 두 skip과 G2/G3/G7의 실제 비교 미충족, G4~G6/G8 및 다른 남김을 유지한다. B56의 네 임시 원보고가 현재 없다는 한계와 requirement-state에는 P10/P11 ID가 없다는 namespace 차이를 별도로 기록했고 과거2passed를 새 성공에 합산하지 않았다.',
    acceptance=[
        dict(id='A1',result='pass',detail='두 exact-baseline/PROBE/SNAPSHOT/WORKER/merge·ordinary/읽기·literal/marker/coverage/worker union 성질을 검토했다. Git log -S/diff/부모 및 도입 M-0472/B56 원기록으로 선택 판본을 확정했고 기존 공통 API를 정적 대조했다. PR01 및 requirement-state 원문 진입점을 추적하면서 P10/P11이 그103개 ID가 아니라 현 비교/역사 표기임을 명시했다. 네 역사 raw 부재는 보존 기록과 구별했다.',
             evidence=refs('review.md','history-selection.json','fix-search.stdout','fix-diff.stdout','history-parents.stdout',
                           'fix-memory.stdout','pr01-slice.json','requirement-trace.json','b56-original-record.json',
                           'historical-report-availability.json','api-static-verification.json')),
        dict(id='A2',result='pass',detail='새 pre-provenance/scripts 절대 경로에 당시 scripts 전체910개를 섞임/개작 없이 추출했다. 전 경로/Git blob/SHA256/크기와 tree·명령을 manifest에 기록하고 새 cat-file 조회로 전건 바이트 동등성을 확인했다. Git tracked mode는 일반 blob뿐이며 실제 reparse point/경로 이탈은0이다. 필수 runner/support/제품 의존 파일이 있으며 현재 SCRIPTS와 다른 경로다. 정적 분석만 수행했다.',
             evidence=refs('baseline-manifest.json','baseline-verification.json','extraction-tree.command.json',
                           'extraction-objects.command.json','verify-objects.command.json','baseline-verify.command.json',
                           'baseline-verify.stdout','stable-source-comparison.json','input-final-comparison.json')),
        dict(id='A3',result='pass',detail='review.md에 실제 환경변수 경로, 양쪽 공식 runner의 정확 두ID·순차 jobs1 명령, 기대 skip0/선택-row-exit 검증과 후속 전체 T4 책임, 실제 old/new raw 및 tool/source 보존 방법을 제공했다. 임시 fixture teardown으로 raw가 사라지는 현재 동작을 밝혔고 cleanup 전 companion 관측을 후속 방법으로 구분했다. 비교 실행/정상 도달/통과는 주장하지 않으며015 skip·역사 raw 부재·최종 G 남김은 유지한다.',
             evidence=refs('review.md','tool-edition.json','baseline-manifest.json','baseline-verification.json',
                           'historical-report-availability.json'))
    ],changes=[],seams=[],
    findings=[
        dict(id='F1',kind='fact',
             detail='검증된 pre-fix 입력은010b059700115f6d5d3df1bf24e931cf78eaa44a의 scripts910개이며 도입bbe64043의 실제 부모/원기록과 일치한다. SHARED_INPUT_BASELINE_SCRIPTS는 review.md의 evidence/pre-provenance/scripts 절대 경로다. 기존 공통 API의 정적 적합성만 확인했고 ordinary/측정 비교나 공식 시험은 수행하지 않았다.015의 양쪽 두 exact-baseline skip이 자동 해소된 것은 아니다.',
             evidence=refs('baseline-manifest.json','baseline-verification.json','api-static-verification.json','review.md'),
             affects=['run:context.md#C11','run:context.md#G2','run:context.md#G3','run:context.md#G7','run:plan.md'],
             next_action='manager가 입력 자격/바이트를 검수한 뒤 fixture 수리 결과와 함께 후속 단일 연결 work에 두 정확 비교·raw 관측 보존과 양쪽 전체 T4 선택/row/exit/worker 판본 대조를 배정한다. 입력과 현재 source/도구가 바뀌면 재검산한다.'),
        dict(id='F2',kind='fact',
             detail='B56의 changed_area/structure/timing_red/exact_baseline_comparison 네 Temp 원보고는 현재 해당 경로에 없다. 도입 commit M-0472 및 현 단계전환표에는 동일010b0597 baseline과 역사2passed15.2초 주장이 존재하지만 raw 재검산 증거는 아니다. requirement-state의103row에는P10/P11 ID/문자열이 없으며 이는 해당 exact 비교/역사 표기다. 관련 원문은 PR01/B56와 설계5.3~5.5/A29 및 requirement-state K05/K06 진입점으로 연결했다. 문서 packet이나 다른 계획의 동명 P10/P11과 합치지 않았다.',
             evidence=refs('historical-report-availability.json','b56-original-record.json','fix-memory.stdout',
                           'requirement-trace.json','pr01-slice.json','review.md'),
             affects=['run:context.md#C9','run:context.md#C11','run:context.md#G2','run:plan.md'],
             next_action='과거 수치를 현 성공에 합산하지 않고 새 실제 비교를 별도 근거로 확보한다. 후속 인계에서 P10/P11은 정확 시험 이름/역사 표기임을 유지하며 없는 requirement-state ID나 원보고 존재를 만들어 쓰지 않는다.')
    ],checks=checks)
(OUT.parent/'report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(dict(status=report['status'],acceptance=len(report['acceptance']),checks=len(checks),report=str(OUT.parent/'report.json')),ensure_ascii=False))
