from work import *
env=os.environ.copy()
env['PYTHONPATH']=str(E/'cwd-hooks')+os.pathsep+env.get('PYTHONPATH','')
argv=[PY,'-u','-B',str(REPO/'.claude/skills/do-math/scripts/run_tests.py'),
    'boundary.test_engine_cli.CliExitTests.test_help_and_input_error_exit_codes_are_structured',
    '--jobs','1','--output',str(E/'cwd')]
p=subprocess.run(argv,cwd=REPO,env=env)
rows=[]
for path in E.glob('cwd-audit-*.jsonl'):
    rows.extend(json.loads(line) for line in path.read_text(encoding='utf-8').splitlines())
resource=[row for row in rows if any(str(a).endswith('do_math.py') for a in row['argv'])]
assert p.returncode==0 and len(resource)==2,(p.returncode,resource)
assert all('boundary-isolated-000' in row['cwd'] and '/scratch/' in row['cwd'].replace('\\','/') for row in resource)
save('resource-cwd-confirmed.json',{'official_argv':argv,'exit_code':p.returncode,'environment_addition':{'PYTHONPATH_prefix':str(E/'cwd-hooks')},
    'reason':'The final full suites passed but did not expose child cwd. This single exact resource test is rerun to resolve that missing observation without changing product/test bytes.',
    'resource_cli_calls':resource,'cwd_lengths':[len(row['cwd']) for row in resource]})
print('Actual resource CLI cwd confirmed',[(row['cwd'],len(row['cwd'])) for row in resource])
sys.exit(p.returncode)
