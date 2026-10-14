import json
import sys
from pathlib import Path
from work import REPO, HERE, save

SCRIPTS = REPO / '.claude/skills/do-math/scripts'
sys.path[:0] = [str(SCRIPTS), str(SCRIPTS / 'tests')]
from support import doc_code as doc
from do_math.cli_contract import build_parser

identity = (SCRIPTS.parent / '계약/동일성-검토.md').read_text(encoding='utf-8')
preparation = (SCRIPTS.parent / '계약/후보-준비.md').read_text(encoding='utf-8')
operator = (SCRIPTS.parent / '계약/독립-운영.md').read_text(encoding='utf-8')
options = doc.parser_options(build_parser())
flags = doc.tool_options(SCRIPTS)
schemas = doc.field_schemas()
defer = dict(defer_status=True, defer_operation_progress=True, defer_query_record=True, defer_query_result=True)
for arg, constant in [('cli_results', 'CLI_RESULT_BOUNDARIES'), ('role_inputs', 'ROLE_INPUT_BOUNDARIES'),
                      ('continuations', 'CONTINUATION_BOUNDARIES'), ('operational_inputs', 'OPERATIONAL_INPUT_BOUNDARIES'),
                      ('result_inputs', 'RESULT_INPUT_BOUNDARIES'), ('tool_inputs', 'TOOL_INPUT_BOUNDARIES'),
                      ('review_inputs', 'REVIEW_INPUT_BOUNDARIES'), ('delivery_inputs', 'DELIVERY_INPUT_BOUNDARIES'),
                      ('governance', 'GOVERNANCE_BOUNDARIES'), ('waits', 'WAIT_BOUNDARIES'), ('trust', 'TRUST_BOUNDARIES')]:
    defer['defer_' + arg] = tuple(getattr(doc, constant))

cases = [('identity-normal', 'identity', identity),
         ('initial-findings-typo', 'identity', identity.replace('와 `findings`를 반환한다', '와 `findingz`를 반환한다')),
         ('organize-decision-borrow', 'identity', identity.replace('쟁점 정리는 동일성을 승인하는 단계가 아니다.',
           '쟁점 정리는 동일성을 승인하는 단계가 아니다. 주 산출에는 `decision`을 반환한다.')),
         ('sibling-normal', 'preparation', preparation),
         ('sibling-field-typo', 'preparation', preparation.replace('"independent_of_next_revision":false', '"independent_of_revision":false')),
         ('supplement-task-title-borrow', 'preparation', preparation.replace('"task_id": "TK-one"', '"task_title": "TK-one"')),
         ('operator-normal', 'operator', operator)]
for prefix in ('', 'do_math.py ', '$dmCli '):
    cases.append(('operator-invent-' + (prefix.strip() or 'bare'), 'operator', '`' + prefix + 'operator invent`'))
rows = []
for name, owner, text in cases:
    old = [*doc.command_issues(text, options, flags), *doc.scoped_field_issues(text, schemas, **defer),
           *[('unowned', v) for v in doc.unowned_field_references(text, schemas)]]
    new = None
    if sys.argv[1] == 'after':
        new = doc.review_output_issues(text) if owner == 'identity' else (
            doc.preparation_example_issues(text) if owner == 'preparation' else doc.command_issues(text, options, flags))
    rows.append({'name': name, 'owner': owner, 'original_checks': old, 'new_issues': new})
    (HERE / (sys.argv[1] + '-' + name.replace('$', '') + '.md')).write_text(text, encoding='utf-8')
save('document-' + sys.argv[1] + '.json', rows)
print(json.dumps(rows, ensure_ascii=False, indent=2))
if sys.argv[1] == 'before':
    assert all(not r['original_checks'] for r in rows)
else:
    assert all(bool(r['new_issues']) == ('normal' not in r['name']) for r in rows)
