from work import *
import ast
tests = REPO / '.claude/skills/do-math/scripts/tests'
selected = []
consumers = []
for path in tests.rglob('test_*.py'):
    if path.parent.name not in ('structure', 'unit', 'contracts', 'sim', 'flows', 'boundary'):
        continue
    tree = ast.parse(path.read_text(encoding='utf-8'))
    names = {n.id for n in ast.walk(tree) if isinstance(n, ast.Name)}
    if {'field_schemas', 'scoped_field_issues'} & names:
        name = '.'.join(path.relative_to(tests).with_suffix('').parts)
        selected.append(name)
        consumers.append({'id': name, 'sha256': digest(path)['sha256'],
            'reason': 'Actual document walker affected by trust boundary deferral.'})
selected += ['unit.test_trust_environment', 'unit.test_toolchain_records', 'sim.test_toolchain_tools',
    'sim.test_knowledge_project_identity', 'sim.test_trust_transition', 'sim.test_formal_wait_contract',
    'unit.test_knowledge_formal_runtime',
    'boundary.test_knowledge_lean_verifier.ToolchainContractTests',
    'boundary.test_knowledge_lean_verifier.LakeEnvironmentTests',
    'unit.test_review_research_owner_contract', 'sim.test_submission_review_inputs',
    'boundary.test_review_source_restoration']
# The existing trust flow establishes registration versus activation, old
# environment preservation on failure, exact rebound event and compile gates.
path = tests / 'flows/test_lifecycle_engine_trust.py'
selected.append('flows.test_lifecycle_engine_trust')
selected = list(dict.fromkeys(selected))
prior = json.loads((RUN/'phases/024/tasks/document-waits/evidence/related-selection.json').read_text())
excluded = []
for name in prior:
    if name in selected: continue
    path = tests / ('/'.join(name.split('.')[:2]) + '.py')
    excluded.append({'id': name, 'sha256': digest(path)['sha256'],
        'reason': 'No changed document walker or trust helper consumption. 024 wait/retry producers and their helper remain unchanged; their exact retained evidence is reused. Final whole gates remain separate.'})
save('related-selection.json', selected)
save('selection-decisions.json', {'consumers': consumers, 'selected': selected,
    'excluded_024': excluded, 'excluded_installed': [
        {'id': 'boundary.test_knowledge_formal_consumer', 'sha256': digest(tests/'boundary/test_knowledge_formal_consumer.py')['sha256'],
         'reason': 'No modified producer/consumer here; installed compiler/storage/currentness property retained from 012/016/018. The two current installed P08 owners run once per tree.'},
        {'id': 'boundary.test_knowledge_formal_runtime', 'sha256': digest(tests/'boundary/test_knowledge_formal_runtime.py')['sha256'],
         'reason': 'Job/compiler output/stop runtime unchanged; existing 012/016/018 property evidence retained. No reason to repeat complete Lean/T4.'}],
    'basis': 'Six actual document-walk modules, three trust owners, exact existing trust registration/activation/formal/wait consumers, project Git/files scenes and single-proposal/restoration guards.'})
print('Selected', len(selected), 'modules/classes', selected)
