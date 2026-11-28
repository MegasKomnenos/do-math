"""The stand-in that tests/test_search.py launches in place of the Claude CLI of a light session.

Run as `light_cli.py <scenario folder> <the options a light session's CLI is given>` it reads the system
prompt from the file that --system-prompt-file names and the request from its standard input, finds in
<scenario>/script.json what to do, and writes the stream that the Claude CLI writes in print mode.

script.json is a list of rules, tried in order. A rule applies when the text of `system`, if it has one,
occurs in the system prompt and the text of `request`, if it has one, occurs in the request; with `times`
it applies only to the first so many calls it matches, so that a later rule answers the next. The first rule
that applies says what the call does, by one of
    "answer": <text>      the session ends with this text as its final answer
    "refuse": <reason>    the provider or the model refuses: usage_limit, model_requires_usage_credits, model_refusal
    "exit": <code>        the CLI ends with this exit code and reports no result
    "error": <text>       the CLI ends the session with an error that is no refusal
and it may carry "hold": <file name>, for which the call waits under the scenario folder before it does
anything, and "seconds", for which it sleeps. A call that no rule applies to answers with an empty list of hits.

Each call leaves <scenario>/calls/<number>.json: its arguments, its working folder, the system prompt, the
request, the rule that applied, and `beside`, the number of stand-ins that were running when it started,
itself included. The tests read the limit on light sessions off that number.
"""
import json
import os
from pathlib import Path
import sys
import time


def emit(event):
    print(json.dumps(event), flush=True)


def result(text, error=False, **more):
    return {'type': 'result', 'subtype': 'success', 'is_error': error, 'result': text, 'duration_ms': 1200,
            'total_cost_usd': 0.0125,
            'modelUsage': {'claude-stand-in': {'inputTokens': 3, 'outputTokens': 40, 'cacheReadInputTokens': 1000,
                                               'cacheCreationInputTokens': 200, 'costUSD': 0.0125}}, **more}


def main(scenario, argv):
    sys.stdin.reconfigure(encoding='utf-8')
    request = sys.stdin.read()
    system = Path(argv[argv.index('--system-prompt-file') + 1]).read_text(encoding='utf-8')
    for name in ('calls', 'running'):
        (scenario / name).mkdir(exist_ok=True)
    mark = scenario / 'running' / str(os.getpid())
    mark.touch()
    beside = len(list((scenario / 'running').iterdir()))
    try:
        records = [json.loads(path.read_text(encoding='utf-8')) for path in sorted((scenario / 'calls').glob('*.json'))]
        applied = None
        for number, rule in enumerate(json.loads((scenario / 'script.json').read_text(encoding='utf-8'))):
            if rule.get('system', '') in system and rule.get('request', '') in request:
                if 'times' not in rule or sum(record['rule'] == number for record in records) < rule['times']:
                    applied = number, rule
                    break
        number, rule = applied or (None, {'answer': '{"hits": [], "unpublished": []}'})
        # The record is named by the time and the process, so two calls that run side by side write two files.
        (scenario / 'calls' / f'{time.time_ns():020d}-{os.getpid()}.json').write_text(json.dumps({
            'argv': argv, 'cwd': os.getcwd(), 'system': system, 'request': request, 'rule': number, 'beside': beside,
            'output_tokens': os.environ.get('CLAUDE_CODE_MAX_OUTPUT_TOKENS')}), encoding='utf-8')
        if 'hold' in rule:
            deadline = time.time() + 60
            while not (scenario / rule['hold']).exists() and time.time() < deadline:
                time.sleep(0.02)
        time.sleep(rule.get('seconds', 0))
        emit({'type': 'system', 'subtype': 'init', 'tools': [], 'mcp_servers': [], 'model': 'claude-stand-in'})
        if 'exit' in rule:
            return rule['exit']
        if 'error' in rule:
            emit(result(rule['error'], error=True))
            return 1
        if rule.get('refuse') == 'usage_limit':
            emit({'type': 'assistant', 'is_api_error_message': True, 'api_error': 'usage_limit_reached',
                  'api_error_params': {'rate_limit_info': {'status': 'rejected', 'rateLimitType': 'five_hour',
                                                           'resetsAt': time.time() + 3600}},
                  'message': {'model': '<synthetic>', 'role': 'assistant', 'content': []}})
            emit(result("You've hit your limit", error=True))
            return 1
        if rule.get('refuse') == 'model_requires_usage_credits':
            emit({'type': 'assistant', 'is_api_error_message': True, 'api_error': 'model_requires_usage_credits',
                  'message': {'model': '<synthetic>', 'role': 'assistant', 'content': []}})
            emit(result('This model requires usage credits', error=True))
            return 1
        if rule.get('refuse') == 'model_refusal':
            emit(result("API Error: the model's safeguards flagged this message.", error=True, stop_reason='refusal'))
            return 1
        emit({'type': 'assistant', 'message': {'model': 'claude-stand-in', 'role': 'assistant',
                                               'content': [{'type': 'text', 'text': rule['answer']}]}})
        emit(result(rule['answer']))
        return 0
    finally:
        mark.unlink()


if __name__ == '__main__':
    raise SystemExit(main(Path(sys.argv[1]), sys.argv[2:]))
