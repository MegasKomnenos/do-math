import ast
import collections
import json
from pathlib import Path
from analyze import ROOT, RUN, OUT, SKILL, read, save, sha, snapshot

E='run:phases/028/tasks/role-glossary-names/evidence/'
R='repo:.claude/skills/do-math/scripts/'

bindings=[
    ('문서별 정적 소유','tests/structure/test_doc_code.py',
     ['test_identity_output_declarations_use_their_exact_stage_and_item','test_preparation_partial_examples_use_their_exact_extension_branch',
      'test_documented_scoped_fields_belong_to_their_actual_schema','test_all_dotted_document_fields_have_an_owner'],
     '027의 두 역할 계약 좌표와 dotted-owner 검사다. CLI 단독 출력·enum·JSON fence에는 같은 소유자가 자동 부여되지 않는다. observe의 다섯 변형은 새 공식 실행 없이 적용 가능한 helper의 동일 빈 진단을 확인했다.'),
    ('역할 응답 모양','tests/unit/test_submission_contracts.py',
     ['test_invalid_decisions_fail','test_every_role_has_closed_schema','test_plan_assessment_fields_are_required',
      'test_scope_planning_schema_reaches_domain_scope_validator','test_profile_references_use_the_sealed_provider_identity'],
     '역할별 폐쇄 객체·판정 enum·계획 필수 필드·정확 프로필을 직접 schema로 검사한다. CLI 문장을 읽는 검사는 아니다. c3의 해당 exact rows만 재사용한다.'),
    ('검토 단계 소비','tests/unit/test_review_cycle_stages.py',
     ['test_stage_schema_is_specific','test_organizer_omission_forgery_and_owner_checks','test_scope_false_match_rejected_and_incomplete_not_reviewed'],
     'stage_schema의 stage별 필수·금지 필드와 실제 검토 수신의 원 finding/owner·scope 조건을 검사한다. c3 exact rows를 재사용하며 CLI 문장과의 결속 공백은 F2다.'),
    ('신규 종류의 소비','tests/unit/test_submission_extension_semantics.py',
     ['test_proposed_kind_is_actually_registered_before_checking_its_consumer'],
     '실제 action_schema/extension_schema로 정상 외곽을 확인한 뒤 payload_issues를 호출한다. 같은 묶음의 bounded_note 제안과 knowledge 소비의 [] 및 invalid token의 정확 반려를 단언한다. 여기서는 본문 정적 확인만 했다. 이 시험의 새 성공을 보고하지 않는다.'),
    ('checkpoint 실경계','tests/unit/test_observation_checkpoint.py',
     ['test_repeated_checkpoint_reads_reuse_schema_but_recheck_value_and_evidence','test_duplicate_checkpoint_keys_are_invalid_live_and_at_final_capture','test_checkpoint_requires_available_preserved_evidence_paths'],
     '실제 read_checkpoint/수신 포착에서 enum·원자료 실재·중복 JSON 키·임시 자료 제외를 검사한다. CLI fence를 읽지 않으므로 문서 예제 오타는 별도 보강이다. 이번 관찰은 checkpoint_value의 구조 검사만 실행했다.'),
    ('역할/단계 입력의 분리','tests/unit/test_role_input_scoped_packaging.py',
     ['test_review_stage_requirements_cover_every_current_schema_branch','test_role_input_maps_context_its_scope_does_not_inline','test_independent_judgment_never_receives_its_blocked_context','test_control_binding_reaches_the_checker_context_but_not_the_prompt'],
     '현 stage 분기 모집단과 입력 요구의 대응, inline/map/blocked 및 checker-only 제거를 검사한다. 현재 본문의 정적 단언 대조다. N01-236의 모든 산문을 이 시험만으로 인증하지 않는다.'),
    ('024 지정 재시도 문장','tests/flows/test_engine_input_recovery.py',
     ['test_public_retry_replays_refails_resolves_and_rejects_after_close','test_resolved_retry_marker_survives_provider_deferral_and_repreparation'],
     '원 overflow 질문/artifact 보존, pause/resume와 retry 접수의 비해소, 재실패/새질문/성공 후 해소와 실제 한 번 원 action dispatch를 단언한다. 024 c2의 exact rows와 현재 이 시험 SHA가 일치해야 재사용한다.'),
    ('후보별 계약 확장','tests/unit/test_submission_contract_checks.py',
     ['test_every_candidate_needs_exactly_one_self_check','test_a_cited_sibling_contract_is_declared_at_its_current_revision','test_primary_and_extension_dependencies_both_wait_for_a_sibling_under_revision'],
     'contract_checks의 후보별 하나, 형제 경계의 현 revision 및 주/확장 의존 대기를 실제 contract_check_errors/수신으로 확인한다. c3 exact rows만 재사용한다.')]
rows027=[row for group in read(RUN/'phases/027/tasks/doc-policy/evidence/c3/report.json')['reports'] for row in group['rows']]
report024=read(RUN/'phases/024/tasks/document-waits/evidence/c2/report.json')
rows024=[row for group in report024['reports'] for row in group['rows']]
test_profiles=[]
for title,file,methods,meaning in bindings:
    path=SKILL/'scripts'/file
    text=path.read_text(encoding='utf-8-sig'); lines=text.splitlines(); tree=ast.parse(text)
    found={n.name:n for n in ast.walk(tree) if isinstance(n,ast.FunctionDef)}
    excerpts=[]
    for method in methods:
        assert method in found,(file,method)
        node=found[method]
        excerpts.append({'method':method,'lines':[node.lineno,node.end_lineno],'source':'\n'.join(lines[node.lineno-1:node.end_lineno])})
    reused=[]
    for origin,rows in [('027/c3',rows027),('024/c2',rows024)]:
        for row in rows:
            module='.'.join(row['id'].split('.')[:2])
            if file=='tests/'+module.replace('.','/')+'.py' and row['id'].split('.')[-1] in methods:
                hashes=(read(RUN/'phases/027/tasks/doc-policy/evidence/c3/report.json') if origin=='027/c3' else report024)['source_sha256']
                if hashes[file]==sha(path):
                    reused.append({'origin':origin,'row':row})
    test_profiles.append({'boundary':title,'path':R+file,'sha256':sha(path),'judgment':meaning,'methods':excerpts,'reused_exact_rows':reused})
save('test-bindings.json',test_profiles)

candidates=[
    {'id':'F1','kind':'문구 수정','sections':['N01-243'],'document':'repo:.claude/skills/do-math/references/CLI-실행-계약.md','lines':[748,748],
     'current':'kind enum은 실행 시점의 active knowledge 종류 정의에서 동적으로 만든다.',
     'expected':'knowledge의 kind는 문자열로 받고, 중앙 수신 검사가 입력의 활성 종류 또는 같은 편입 묶음에서 제안한 종류인지 확인한다고 설명한다. 신규 제안의 독립 의미 검사/활성화 권한은 유지한다.',
     'actual':'contracts.action_schema의 연구 생산자 분기는 knowledge.items.properties.kind를 TEXT로 교체한다. CoreEngineMixin._response_schema와 _governance_schema도 연구 kind enum을 만들지 않는다. submission._payload_issues는 신규 정의를 등록한 작업 사본에서 active-or-proposed를 검사한다.',
     'minimum_counterexample':'action_schema(research_work).properties.knowledge.items.properties.kind에 enum이 없고 type=string이다. 기존 ExtensionMeaningTests는 same-bundle bounded_note의 실제 소비를 단언한다. schema 관찰은 실행했고 소비 시험은 정적 본문 확인만 했다.',
     'files':['repo:.claude/skills/do-math/references/CLI-실행-계약.md',R+'tests/support/doc_code.py',R+'tests/structure/test_doc_code.py',R+'tests/unit/test_submission_extension_semantics.py'],
     'acceptance':'문구를 실제 구조/수신 역할 구분에 맞춘다. 현재 active token/새 제안 허용과 미등록 반려 단언을 유지하고, 이 문장이 거짓 active-enum 설명으로 돌아가면 잡는 좁은 단언을 추가한다. runtime을 enum으로 제한하지 않는다. 같은 통합 work에서 공식 미러와 관련 회귀를 확인한다.'},
    {'id':'F2','kind':'검사 보강','sections':['N01-250','N01-251','N01-252','N01-253','N01-256'],
     'document':'repo:.claude/skills/do-math/references/CLI-실행-계약.md','lines':[784,824],
     'current':'현재 네 단계 이름과 checkpoint 예제는 올바르지만 CLI 문장/예제의 오타·타단계 차용이 적용 가능한 문서 helper를 빠져나간다.',
     'expected':'현재 CLI의 명시 출력 절을 각 stage_schema/해당 원소에 연결하고 checkpoint JSON fence 하나는 CHECKPOINT_SCHEMA/checkpoint_value로 검사한다.',
     'minimum_counterexample':'schema-observations.json의 findings→findingz, organize root decision 추가, answers→answerz, judge issue decision approved→match, checkpoint current_claim→current_cliam 다섯 변형이다. 기존 scoped/unowned/function/constant 진단은 정상과 같이 모두 비어 있고 실제 stage owner/enum 또는 checkpoint_value는 해당 잘못된 이름/값을 허용하지 않는다. 완전 공식 suite의 거짓 green을 새로 실행한 주장은 아니다.',
     'files':[R+'tests/support/doc_code.py',R+'tests/structure/test_doc_code.py',R+'tests/unit/test_review_cycle_stages.py',R+'tests/unit/test_observation_checkpoint.py','repo:.claude/skills/do-math/references/CLI-실행-계약.md'],
     'acceptance':'정상 네 단계/원소 및 완전 checkpoint 객체를 실제 정의로 승인하고 위 다섯 반례·절/선언/JSON fence 부재를 반려한다. judge root decision과 issue_verdicts[].decision의 다른 enum, checkpoint 문자열과 파일 객체를 구별한다. 기존027 역할 계약 검사/부분 예제·P/PURE 반환 경계는 보존한다. 전역 자연어/단어 목록 추론기를 추가하지 않고 미러/관련 공식 검사를 한 통합 작업으로 확인한다.'}]
save('repair-candidates.json',candidates)

# Exact allocation, current coordinates, owner refs, historical hashes, invariance.
assigned=next(t for t in read(RUN/'phases/028/assignments.json')['tasks'] if t['task']=='role-glossary-names')
mapped=read(OUT/'slice-map.json'); decisions=read(OUT/'section-decisions.json'); profiles=read(OUT/'owner-profiles.json')
assert {d['id'] for d in decisions}=={s['id'] for s in assigned['slices']}
assert len(mapped)==len(decisions)==195
assert len([x for x in decisions if 'GLOSSARY.md' in x['document']])==162
for d,s in zip(decisions,mapped):
    assert d['id']==s['id']
    lines=(ROOT/s['document'].split(':',1)[1]).read_text(encoding='utf-8-sig').splitlines()
    assert sha(ROOT/s['document'].split(':',1)[1])==s['sha256']
    assert '\n'.join(lines[s['current_start']-1:s['current_end']])==s['text']
    original=collections.Counter((o['name'],o['line']) for o in s['inline_occurrences'])
    produced=collections.Counter((o['name'],ln) for o in d['names'] for ln in o['lines'])
    assert original==produced,d['id']
    for name in d['names']:
        assert name['reason'] and (name['owner_profile'] is None or name['owner_profile'] in profiles)
for profile in profiles.values():
    assert all((ROOT/p.split(':',1)[1]).is_file() for p in profile['definitions'])
for profile in read(OUT/'source-profiles.json'):
    assert sha(ROOT/profile['path'].split(':',1)[1])==profile['sha256']
for item in read(OUT/'input-profiles.json'):
    p=(ROOT if item['reference'].startswith('repo:') else RUN)/item['reference'].split(':',1)[1]
    assert sha(p)==item['sha256'],item['reference']
end=snapshot();start=read(OUT/'source-start.json')
assert start==end
current_paths={p.relative_to(ROOT).as_posix() for top in ('.claude/skills','.agents/skills','.agents/diff') for p in (ROOT/top).rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.suffix!='.pyc'}
assert current_paths==set(start),(len(current_paths),len(start),sorted(current_paths-set(start))[:10],sorted(set(start)-current_paths)[:10])
save('source-end.json',end)
verification={'assigned_sections':195,'glossary_sections':162,'cli_sections':33,'missing':[],'duplicates':[],
              'source_files':len(end),'source_changes':[],'source_additions':[],'source_deletions':[],
              'inline_occurrences':sum(len(s['inline_occurrences']) for s in mapped),
              'conclusions':dict(collections.Counter(d['conclusion'] for d in decisions)),
              'resolved_schema_paths':len(read(OUT/'schema-observations.json')['resolved_schema_paths']),
              'new_helper_counterexamples':len(read(OUT/'schema-observations.json')['counterexamples']),
              'reused_027_doc_rows':38,'reused_027_python_files':875,
              'test_binding_groups':len(test_profiles),'repair_candidates':len(candidates),'product_changes':0,
              'new_official_test_runs':0,'new_model_OS_network_store_calls':0}
save('verification.json',verification)
print(json.dumps(verification,ensure_ascii=False))
