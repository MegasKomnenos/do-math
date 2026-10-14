from work import *
import re
root=REPO/'.claude/skills/do-math/scripts/tests'
paths=['structure/test_doc_code.py','unit/test_role_input_packaging.py','unit/test_storage_report_projections.py','unit/test_storage_record_queries.py','unit/test_engine_trace_report_corruption.py','boundary/test_engine_cli.py']
for name in paths:
    path=root/name
    text=path.read_text(encoding='utf-8')
    text,n=re.subn(r'(?m)^(\s*)defer_operational_inputs=\(', r"\1defer_result_inputs=('source_ref', 'materialized_output_files', 'research_sources', 'results'),\n\1defer_operational_inputs=(",text)
    path.write_text(text,encoding='utf-8',newline='\n')
    print(name,n)
