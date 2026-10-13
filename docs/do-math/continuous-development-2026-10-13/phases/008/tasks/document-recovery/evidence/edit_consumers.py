from pathlib import Path
root = Path('C:/math/.claude/skills/do-math/scripts/tests')
paths = ['structure/test_doc_code.py', 'unit/test_role_input_packaging.py',
         'unit/test_engine_trace_report_corruption.py', 'unit/test_storage_record_queries.py',
         'unit/test_storage_report_projections.py', 'boundary/test_engine_cli.py']
for name in paths:
    path = root / name
    text = path.read_text(encoding='utf-8')
    lines = text.splitlines(keepends=True)
    output = []
    for line in lines:
        output.append(line)
        if "defer_cli_results=('init_result', 'scheduling_result', 'selection_result')," in line:
            indent = line[:len(line) - len(line.lstrip())]
            output.append(indent + "defer_operational_inputs=('operational_evidence', 'recovery_materials'),\n")
    text = ''.join(output)
    if name == 'structure/test_doc_code.py':
        text = text.replace("            '`operational_evidence.activity_continuations`', schemas), [])",
                            "            '`operational_evidence.activity_continuations`', schemas,\n            defer_operational_inputs=('operational_evidence',)), [])")
        text = text.replace("            '`checkpoint_source.local_path`', schemas), [])", "            '`action.role`', schemas), [])")
        text = text.replace("'`question_details[].id` `recovery_materials.output_files[].restoration_error`', actual), [])",
                            "'`question_details[].id`', actual), [])")
    path.write_text(text, encoding='utf-8')
