"""Seal review evidence, check handoff, publish, and commit this management unit."""
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys
import zipfile
from verify import R, RUN, O, T, read, sha, save, snapshot

def git(*args):
    return subprocess.check_output(['git', *args], cwd=R)

def command(name, args):
    p = subprocess.run(args, cwd=R, capture_output=True)
    result = dict(command=args, exit_code=p.returncode, stdout=p.stdout.decode('utf-8', 'replace'), stderr=p.stderr.decode('utf-8', 'replace'))
    save(name, result)
    assert p.returncode == 0, result
    return result

def main():
    head = git('rev-parse', 'HEAD').decode().strip()
    verification = read(O / 'verification.json')
    assert head == verification['head']
    assert not (RUN / 'phases/027/manager.json').exists()
    assert not git('diff', '--cached', '--name-only', '-z')
    assert snapshot() == read(O / 'source-inspected.json')
    task_files = read(O / 'task-files.json')
    assert all(sha(RUN / p) == h for p,h in task_files.items())
    assert max(p.stem for p in (R / '기억/layer1').glob('M-*.md')) == 'M-0577'
    assert 'convention_version: 27' in (R / '기억/세칙.md').read_text(encoding='utf-8-sig')
    index = R / '기억/색인.md'
    text = index.read_text(encoding='utf-8-sig')
    assert 'M-0577' not in text
    text = text.replace('## layer-1\n', '## layer-1\n\n- M-0577 [정책 저장과 문서 검사 수리를 검수하고 N01 고정판 조사를 나눔] -- 양쪽134건·실제반환/기존단언 검수,027 마감과288절의 독립 읽기 세 배정\n', 1)
    index.write_text(text, encoding='utf-8')
    command('memory-check.json', [sys.executable, '-B', '기억/scripts/validate_memory_index.py'])

    before = (O / 'context.md.before').read_text(encoding='utf-8-sig')
    after = (RUN / 'context.md').read_text(encoding='utf-8-sig')
    assert before.split('## C2 ')[0] == after.split('## C2 ')[0]
    parts = lambda s: {m.group(1): m.group(2).strip() for m in re.finditer(r'^## (C\d+) [^\n]+\n(.*?)(?=^## C\d+ |\Z)', s, re.M | re.S)}
    b,a = parts(before), parts(after)
    unchanged = [k for k in b if a[k] == b[k]]
    for k in b:
        if k != 'C5': assert a[k].startswith(b[k]), k
    assert set(b) == set(a)
    save('common-comparison.json', dict(criteria_unchanged=True, ids_unchanged=True, unchanged_context_sections=unchanged, changed_context_sections=[k for k in b if a[k] != b[k]], removed_meaning='C5 current phase paragraph superseded by 028; its source/slot/shared-write limits retained. Plan next-step paragraphs and two table status cells updated. No G, unresolved external question, historical evidence, or S behavior removed.', after={name:sha(RUN / name) for name in ('context.md','plan.md','seams.md')}))

    v = 'run:phases/027/manager-evidence/verification.json'
    raw = 'run:phases/027/manager-evidence/return-check.json'
    review = 'run:phases/027/manager-evidence/review.md'
    common = 'run:phases/027/manager-evidence/common-docs.diff'
    next_ref = 'run:phases/028/assignments.json'
    updates = [
        ('C2', '027의 지정 완료·실패 이력·판본과 실제 검수 범위를 추가했다.', [v,raw,review]),
        ('C5', '현재 배정을028의 독립 읽기 셋으로 교체하고 정규 TEMP 표기 조건을 보충했다. 공유 쓰기/검사 슬롯 제한은 유지한다.', [v,next_ref,common]),
        ('C8', '사용자 지정 gpt-6.1-sol/high를028 세 task에 그대로 승계했다.', ['run:sources/model-policy-2026-10-14.md','run:phases/028/phase.json']),
        ('C10', '026 네 발견을027 근거로 종결하고 남은 N01 이름/조합의 정확 책임을028에 배정했다. L01와 기존 성질의 한계는 유지한다.', [v,raw,review,next_ref]),
        ('C11', '부분134passed와 기존 symlink 미검사·최종 G 관문을 구별해 보존했다.', [v,review]),
        ('C12', '16비캐시 제품 인도,196원자료 보존·제한된 하위성질 재사용과 추적 범위를 명시했다.', [v,review,'run:phases/027/manager-evidence/preservation.json'])
    ]
    manager = dict(
        next='028',
        decision='027 doc-policy report를 전문으로 읽고 report 검사를 통과한 뒤 실제 파일·공식 row/종료·저장과 CLI 원반환을 대조해 A1~A5 complete를 승인한다. 시작2675소스는026 검수본과 같고 종료/현재도 일치한다. 허용18변경 중16비캐시 경로가 이번 제품 마감 범위이며 다른 dirty/untracked 변경은 포함하지 않는다. 최종 정본/미러 동일134선택·고유row134passed·exit0, 각875Python 판본과 실제반환각84개를 확인했다. 기존33문서시험/나머지helper/기존단언과 초기실패 기록을 유지한다.\n\n026 policy F2/F3와 role F1/F2의 문구·저장/restart·단계/부분JSON/operator mode 남김을 종결한다. 현재 정책/권한/runtime을 바꾸지 않고 기존 계약을 검사하도록 수리했다. 정상 probe의 marker와 HOLD/조회오류 반환을 구별하고, 기본방침 생성과 명시정책 우선·연결4세대 양쪽저장을 독립 기대로 확인했다. 초기 fixture/검사 오류와 TEMP 표기 반례·Git 바이트 보조오류는 원실패와 교정근거를 각각 보존한다.\n\n다음은 work 028이다. N01 288절의 현재 이름/조합을 operator-names66절, cli-control-names27절, role-glossary-names195절로 나눈다. 제품 쓰기·공식 시험·공유 캐시·미완성 결과 의존이 없어 독립 병렬 가능하다. 이미 승인한 정확 문장/정의/시험 성질을 재사용하고 필요한 수리만 후속 공유 helper·문서·미러/관련 회귀 작업으로 통합한다. 문서번호별 반복 구현이나 새로운 전체 의미 감사는 배정하지 않는다. 모델은 사용자 지정 gpt-6.1-sol/high다. L01 외부결정과 원문byte 미충족·symlink 미검사·G4~G8 최종관문이 남고 직전도 work이므로 개발 완료나 next:null을 제출할 수 없다.',
        reports=[dict(task='doc-policy', state='read', detail='A1~A5 pass의 지정 범위를 승인했다.7공식 실행의 선택/고유row/종료와 판본,원반환/원실패·18변경 범위 및196원파일 불변을 독립 검산했다. 최종134passed는 전체 G 성공이 아니다.', evidence=['run:phases/027/tasks/doc-policy/report.json','run:phases/027/manager-evidence/report-check.json',v,raw,review])],
        dispositions=[
            dict(item='027/doc-policy/F1', action='resolve', destination=['run:context.md#C10'], reason='026 네 carry 발견의 정확 문구·저장/restart·문서검사 공백이 새 독립 기대/반례/실제반환/최종 관련 실행으로 해소됐다. 원report는 유지하며 전체문서 의미 합격으로 확대하지 않는다.', evidence=[v,raw,review,'run:phases/027/manager-evidence/assertion-preservation.json']),
            dict(item='027/doc-policy/F2', action='resolve', destination=['run:context.md#C5'], reason='집중3실패와TEMP표기1실패는 최종 정확ID에서 해소됐다. 단언·runtime을 약화하지 않았고 보조Git/개행오류도시작SHA일치archive로 구별했다. 후속 정규TEMP 조건과 원실패 보존을 반영해 새 제품issue로 전파하지 않는다.', evidence=[v,review,'run:phases/027/tasks/doc-policy/evidence/final-c.stderr','run:phases/027/tasks/doc-policy/evidence/verify.stderr','run:phases/027/tasks/doc-policy/evidence/verify2.stderr']),
            dict(item='027/doc-policy/F3', action='carry', destination=['run:context.md#C10','run:context.md#C11','run:context.md#C12','run:plan.md','run:phases/028/tasks/operator-names/objective.md','run:phases/028/tasks/cli-control-names/objective.md','run:phases/028/tasks/role-glossary-names/objective.md'], reason='18변경 밖 소스와기존단언의 보존·불변하위성질만 재사용한다. N01의 나머지 판정은028에 맡기며 L01 외부결정/원문byte 미충족·symlink1314미검사와최종G관문은 그대로 후속책임이다. 과거모델호출로 새문서독해/준수나전판본성공을 주장하지 않는다.', evidence=[v,review,next_ref,'run:phases/027/manager-evidence/preservation.json'])
        ],
        context_updates=[dict(item=k, action='amend', destination=['run:context.md#'+k], reason=reason, evidence=evidence) for k,reason,evidence in updates],
        plan_update='027 수리/관련회귀를 검수한 현재상태를 추가하고 다음 배정을028 고정판 N01 세 독립 읽기 작업으로 교체했다.288절 합집합·0중복/0누락과각후속수리의통합책임을명시했다. 가까운배정·두표상태외의기존요구/PR재검토·외부질문·G4~G8순서와완료기준은유지한다. 공용의미차이는 common-docs.diff 및 common-comparison.json에 대조했다.',
        seam_updates=[], completion=None)
    pending = RUN / 'phases/027/manager.pending.json'
    pending.write_text(json.dumps(manager, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')

    products = verification['noncache_changes']
    archive = O / 'raw-evidence.zip'
    members = {str((RUN / p).relative_to(R)).replace('\\','/'): h for p,h in task_files.items()}
    members.update({p:sha(R / p) for p in products})
    with zipfile.ZipFile(archive, 'w', zipfile.ZIP_DEFLATED, compresslevel=6) as z:
        for p in sorted(members): z.write(R / p, p)
    with zipfile.ZipFile(archive) as z:
        assert set(z.namelist()) == set(members)
        assert all(hashlib.sha256(z.read(p)).hexdigest() == h for p,h in members.items())
    runrel, orel = RUN.relative_to(R).as_posix(), O.relative_to(R).as_posix()
    selected_task = [p for p in task_files if not p.endswith(('-source-before.json','-source-after.json'))]
    files = {runrel+'/'+p for p in selected_task} | set(products)
    files.update(runrel+'/'+p for p in ('context.md','plan.md','seams.md','phases/027/manager.json'))
    files.update(p.relative_to(R).as_posix() for p in (RUN / 'phases/028').rglob('*') if p.is_file())
    files.update(('기억/layer1/M-0577.md','기억/색인.md'))
    managed = ['verify.py','prepare_handoff.py','submit.py','verification.json','report-check.json','source-inspected.json','task-files.json','verified-changes.diff','assertion-preservation.json','return-check.json','common-comparison.json','common-docs.diff','assignment-check.json','review.md','preservation.json','unrelated-dirty-preserved.json','raw-evidence.zip']
    files.update(orel+'/'+p for p in managed)
    dirty = set(filter(None,git('diff','--name-only','-z').decode('utf-8').split('\0')))
    untracked = set(filter(None,git('ls-files','--others','--exclude-standard','-z').decode('utf-8').split('\0')))
    unrelated = {p:sha(R/p) for p in sorted(dirty | {p for p in untracked if p.startswith(('.claude/','.agents/'))}) if p not in files and (R/p).is_file()}
    save('unrelated-dirty-preserved.json', dict(head=head, sha256=unrelated, note='Existing paths outside this unit, excluded from staging and checked unchanged after commit.'))
    save('preservation.json', dict(task_file_count=len(task_files), task_files=task_files, selected_task_files=selected_task, noncache_product_paths=products, archive=dict(path='run:phases/027/manager-evidence/raw-evidence.zip', sha256=sha(archive), members=members), intended_tracked_paths=sorted(files), local_only=['phases/027/logs/','manager-evidence/*.before','manager-evidence/commit-plan.json','manager-evidence/commit-paths.nul','manager-evidence/commit-message.txt','manager-evidence/*-check.json administrative receipts','manager-evidence/stage-command.json','manager-evidence/stage.json','manager-evidence/commit.json','manager-evidence/post-commit.json']+[p for p in task_files if p not in selected_task], note='All196 original task files and16 inspected product working-tree byte versions are archived without rewriting the originals. Excluded repeated source snapshots remain available through archive members even if local original paths are cleaned. Selected evidence files and archive preserve exact Git bytes; ordinary product/Markdown/assignment text uses repository newline normalization. No restore instruction or historical-result replacement.'))
    save('commit-plan.json', dict(head=head, paths=sorted(files), products=products, memory='M-0577'))
    command('worktree-diff-check.json', ['git','diff','--check','--',runrel+'/context.md',runrel+'/plan.md',runrel+'/seams.md','기억/색인.md',*products])
    assert all(sha(RUN/name) == h for name,h in read(O/'common-comparison.json')['after'].items())
    assert snapshot() == read(O/'source-inspected.json')
    assert all(sha(RUN/p) == h for p,h in task_files.items())
    # From this successful check onward, submitted inputs are immutable.
    command('handoff-check.json', [sys.executable,'services/continuous-development/check.py','handoff',str(R),str(RUN),'027'])
    pending_sha = sha(pending)
    pending.rename(RUN/'phases/027/manager.json')
    assert sha(RUN/'phases/027/manager.json') == pending_sha
    (O/'commit-paths.nul').write_bytes(b'\0'.join(p.encode('utf-8') for p in sorted(files))+b'\0')
    command('stage-command.json', ['git','add','-f','--pathspec-from-file='+str(O/'commit-paths.nul'),'--pathspec-file-nul'])
    staged = set(filter(None,git('diff','--cached','--name-only','-z').decode('utf-8').split('\0')))
    assert staged and staged <= files
    assert {p for p in staged if p.startswith('기억/layer1/')} == {'기억/layer1/M-0577.md'}
    assert {p for p in staged if p.startswith(('.claude/','.agents/'))} == set(products)
    command('staged-diff-check.json', ['git','diff','--cached','--check'])
    blob_hashes = {}
    normalized = []
    for path in sorted(files):
        blob = git('show', ':'+path)
        data = (R/path).read_bytes()
        blob_hashes[path] = hashlib.sha256(blob).hexdigest()
        raw_path = path.startswith(orel+'/') or '/evidence/' in path or path.endswith(('/report.json','/manager.json'))
        if raw_path: assert blob == data, path
        else:
            assert blob == data or blob == data.replace(b'\r\n',b'\n'), path
            if blob != data: normalized.append(path)
    save('stage.json',dict(head=head,staged_count=len(staged),planned_count=len(files),paths=sorted(staged),blob_sha256=blob_hashes,line_ending_normalized=normalized))
    assert all(sha(R/p) == h for p,h in unrelated.items())
    assert snapshot() == read(O/'source-inspected.json')
    assert git('rev-parse','HEAD').decode().strip() == head
    assert staged == set(filter(None,git('diff','--cached','--name-only','-z').decode('utf-8').split('\0')))
    assert max(p.stem for p in (R/'기억/layer1').glob('M-*.md')) == 'M-0577'
    (O/'commit-message.txt').write_text('정책 저장·문서 검사 수리를 검수하고 남은 이름 판정을 병렬 배정함\n',encoding='utf-8')
    command('commit.json', ['git','commit','-F',str(O/'commit-message.txt')])
    newhead = git('rev-parse','HEAD').decode().strip()
    committed = set(filter(None,git('diff-tree','--no-commit-id','--name-only','-r','-z',newhead).decode('utf-8').split('\0')))
    assert committed == staged and not git('diff','--cached','--name-only','-z')
    assert all(sha(R/p) == h for p,h in unrelated.items())
    assert snapshot() == read(O/'source-inspected.json')
    assert all(sha(RUN/p) == h for p,h in task_files.items())
    assert sha(RUN/'phases/027/manager.json') == pending_sha
    save('post-commit.json',dict(commit=newhead,paths=len(committed),product_paths=len(products),unrelated_paths_preserved=len(unrelated),task_files_preserved=len(task_files),manager_sha256=pending_sha,staged_empty=True,pushed=False))
    print(json.dumps(read(O/'post-commit.json'),ensure_ascii=False,indent=2))

if __name__ == '__main__': main()
