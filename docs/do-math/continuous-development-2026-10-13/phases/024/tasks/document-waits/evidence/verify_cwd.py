from work import *
rows=[json.loads(line) for path in E.glob('cwd-audit-*.jsonl') for line in path.read_text(encoding='utf-8').splitlines()]
resource=[row for row in rows if 'do_math.py' in row['argv']]
report=json.loads((E/'cwd/report.json').read_text(encoding='utf-8'))
assert report['complete'] and report['successful'] and report['counts']=={'passed':1}
assert not report['changed_during_run'] and len(resource)==2
assert all('boundary-isolated-000' in row['cwd'] and '/scratch/' in row['cwd'].replace('\\','/') for row in resource)
worker=json.loads((E/'cwd/boundary-isolated-000/worker-report.json').read_text(encoding='utf-8'))
assert worker['returncode']==0
save('resource-cwd-confirmed.json',{'official_report':'cwd/report.json','worker_exit_code':0,
    'resource_cli_calls':resource,'cwd_lengths':[len(row['cwd']) for row in resource],
    'reason':'No child cwd was retained by c2/m. One exact resource test with an evidence-only Python audit hook captured the actual two Popen cwd values. The test passed; the first postprocessor incorrectly assumed argv was a list, whereas Windows supplies its command-line string. Raw records are untouched and verified here without another test run.'})
print('Actual resource CLI cwd',[(row['cwd'],len(row['cwd'])) for row in resource])
