from work import *
ids=json.loads((RUN/'phases/021/tasks/document-review/evidence/related-selection.json').read_text(encoding='utf-8-sig'))
ids += ['unit.test_review_transcript_contract','unit.test_review_engine_transcripts',
        'unit.test_review_engine_stages','flows.test_review_owner_flows',
        'unit.test_submission_checks','unit.test_submission_check_invariants','sim.test_repair_routing']
ids=list(dict.fromkeys(ids))
save('related-selection.json',ids)
sys.path.insert(0,str(REPO/'.claude/skills/writing-skills/scripts'))
import build_skill_mirrors as build
rules=build.load_rules(REPO/'.agents/diff')
allowed=json.loads((RUN/'phases/022/phase.json').read_text(encoding='utf-8-sig'))['tasks'][0]['writes']
planned=[]
for rel,path in build.iter_files(REPO/'.claude/skills').items():
    target=REPO/'.agents/skills'/rel
    overlay=REPO/'.agents/diff'/rel
    transformed=overlay.read_bytes() if overlay.is_file() else build.transform(rel,path.read_bytes(),rules)
    if not target.exists() or transformed!=target.read_bytes():
        planned.append(target.relative_to(REPO).as_posix())
assert set(planned)<=set(allowed),set(planned)-set(allowed)
save('mirror-plan.json',{'changes':planned,'all_within_writes':True})
print('Suite modules',len(ids),'mirror plan',len(planned))
print(json.dumps(planned,ensure_ascii=False))
