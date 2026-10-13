from pathlib import Path
root = Path('C:/math/.claude/skills/do-math/scripts/tests')
for name in ('unit/test_engine_trace_report_corruption.py', 'unit/test_storage_record_queries.py',
             'unit/test_storage_report_projections.py', 'boundary/test_engine_cli.py'):
    path = root / name
    lines = path.read_text(encoding='utf-8').splitlines(keepends=True)
    output = []
    for line in lines:
        if 'defer_role_inputs=' in line:
            indent = line[:len(line) - len(line.lstrip())]
            output.append(indent + "defer_operational_inputs=('operational_evidence', 'recovery_materials'),\n")
        output.append(line)
    path.write_text(''.join(output), encoding='utf-8')
