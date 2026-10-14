from work import *
paths = ['structure/test_doc_code.py', 'unit/test_role_input_packaging.py',
    'boundary/test_engine_cli.py', 'unit/test_engine_trace_report_corruption.py',
    'unit/test_storage_record_queries.py', 'unit/test_storage_report_projections.py']
old = "defer_review_inputs=('role_review', 'pending_findings', 'review_research', 'review_sources')"
for name in paths:
    path = REPO/'.claude/skills/do-math/scripts/tests'/name
    raw = path.read_bytes()
    assert old.encode() in raw
    path.write_bytes(raw.replace(old.encode(), (old + ", defer_delivery_inputs=('submission_check', 'repair')").encode()))
    print(name, raw.count(old.encode()))
