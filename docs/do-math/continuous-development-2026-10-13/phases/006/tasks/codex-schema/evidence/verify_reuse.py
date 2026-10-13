"""Replay preserved Claude evidence with today's receipt, and inspect the stale pair fixture."""
import base64
import hashlib
import json
from pathlib import Path
import sys
from run_command import ROOT, EVIDENCE, snapshot, write_json

sys.path[:0] = [str(ROOT / '.claude/skills/do-math/scripts'), str(ROOT / '.claude/skills/do-math/scripts/tests')]
from do_math.contracts import action_schema
from do_math.claude_stream import parse_response, provider_limit
from do_math.cli_execution import collection_reasons
from do_math.model_call import classify_run
from do_math.provider_final import final_mismatch
from support.provider_live import smoke_request

OLD = ROOT / 'docs/do-math/continuous-development-2026-10-13/phases/003/tasks/provider-smoke/evidence'

def restore(value):
    if isinstance(value, dict):
        if 'base64' in value:
            return base64.b64decode(value['base64'], validate=True)
        return {k:restore(v) for k,v in value.items()}
    if isinstance(value,list): return [restore(v) for v in value]
    return value

smoke_path, = (OLD / 'live-02').rglob('smoke.json')
smoke = json.loads(smoke_path.read_bytes())
original_result = restore(smoke['result'])
collected = original_result['execution']['collect']
request = json.loads(collected['source_request']['raw'])
prompt, schema, expected, checkpoint = smoke_request(Path(request['cwd']), smoke['nonce'])
assert hashlib.sha256(prompt.encode('utf-8')).hexdigest() == smoke['prompt_sha256']
assert schema == json.loads((smoke_path.parent / 'call/output.schema.json').read_bytes()) == action_schema({'role':'maintenance'})
assert expected == smoke['expected_output'] and checkpoint == smoke['expected_checkpoint']
parsed = parse_response(collected['stdout']['raw'],request)
reasons = collection_reasons(collected['worker_status'],parsed,collected['final']['raw'],request,
    prompt_sha256=collected['source_prompt']['sha256'], request_sha256=collected['source_request']['sha256'],
    schema_sha256=smoke['schema_sha256'],final_check=final_mismatch)
assert reasons == []
collected['jsonl'] = parsed
result = classify_run(collected,started=original_result['execution']['started'],stopped=False,
    cli_model=smoke['inputs']['model'],claude_only_assigned_model=False,control_binding=None,
    output_schema=schema,evidence_dir=smoke_path.parent / 'call',execution_id=None,reference=None,
    provider_failure=provider_limit,now=lambda:smoke['ended_at'])
assert result['status']=='completed' and result['output']==expected
current = snapshot()
old = json.loads((OLD / 'source-final.json').read_bytes())
unchanged_names = ['claude_adapter','claude_worker','claude_stream','worker_request','cli_worker','cli_execution',
                   'codex_adapter','native_final','contracts','core_engine','wiring','windows_job']
unchanged = ['.claude/skills/do-math/scripts/do_math/'+n+'.py' for n in unchanged_names]
assert all(current[p]==old[p] for p in unchanged)
surface = json.loads((OLD / 'surfaces/claude.json').read_bytes())
environment = json.loads((EVIDENCE / 'environment.json').read_bytes())
old_identity = surface['report']['identity']
for key in ('version_sha256','exec_help_sha256'):
    assert surface['report'][key] == environment['surfaces']['claude']['verdict'][key]
assert Path(surface['report']['cli_path']) == Path(environment['surfaces']['claude']['cli'])
record = {'original_smoke':str(smoke_path),'result_status':result['status'],'result_output':result['output'],
    'checks':smoke['checks'],'collection_reasons':reasons,'prompt_unchanged':True,'schema_unchanged':True,
    'unchanged_modules':unchanged,'historical_cli_identity':old_identity,
    'tool_reuse_basis':'Same executable path, version and complete current help bytes; historical binary SHA was not recorded, so byte identity is not claimed.',
    'current_version':environment['surfaces']['claude']['version'],'new_claude_calls':0,
    'changed_shared_code':'model_runner Codex-only schema branch; model_call reads the verified source_request and semantic_output Claude branch performs the previous strict_json_loads. Bound returns precede decoding.'}
write_json(EVIDENCE / 'claude-reuse.json',record)
from contracts.pairs import _runner_result_samples
rows = [{'branch':branch,'status':value['status'],'error_kind':value.get('error_kind'),'error':value.get('error')}
        for branch,value in _runner_result_samples(EVIDENCE)]
write_json(EVIDENCE / 'pair-observation.json',rows)
print(json.dumps({'claude':record,'pair_rows':rows},ensure_ascii=False))
