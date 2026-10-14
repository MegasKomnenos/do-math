"""Observe real storage/CLI returns with monitoring; run the unchanged official runner."""
from contextlib import ExitStack
from copy import deepcopy
import inspect
import json
from pathlib import Path
import runpy
import sys

HERE = Path(__file__).resolve().parent
runner = Path(sys.argv[1]).resolve()
label = sys.argv[2]
arguments = sys.argv[3:]
sys.path[:0] = [str(runner.parent), str(runner.parent / 'tests')]
from do_math.repository import ResearchRepository
from do_math import cli, scheduled_operator
from support.storage_probes import Returns

targets = {'test_default_review_policy_is_generated_from_current_config_and_saved',
           'test_explicit_review_policy_takes_precedence_over_default_adoption',
           'test_resume_requires_a_live_generation_newer_than_the_lost_generation',
           'test_hold_stops_wake_engine_and_supervisor_at_the_public_boundary',
           'test_normal_probe_observes_without_calling_a_model_or_starting_research',
           'test_probe_status_failure_returns_its_error_without_a_required_model_marker'}

def current_test():
    frame = inspect.currentframe()
    try:
        while frame:
            test = frame.f_locals.get('self')
            name = getattr(test, '_testMethodName', None)
            if name in targets:
                return test.id()
            frame = frame.f_back
    finally:
        del frame

stream = (HERE / (label + '-returns.jsonl')).open('w', encoding='utf-8')
counts = {}

def snapshot(kind, value):
    test = current_test()
    if not test:
        return None
    if kind == 'load':
        head, instance, runtime = value
        data = {'snapshot': head, 'config': {k: instance['config'][k] for k in ('reviewers', 'review_rounds')},
                'review_policy': instance.get('review_policy'),
                'adoption': instance['lifecycle']['adoption'],
                'conversation_loss_policy': instance.get('conversation_loss_policy'),
                'conversations': runtime['conversations']}
    else:
        data = value
    # Selected storage and CLI results contain no bytes. Do not silently convert
    # byte-valued objects into strings; preserve observer faults as failures.
    stream.write(json.dumps({'test': test, 'kind': kind, 'value': data}, ensure_ascii=False) + '\n')
    stream.flush()
    counts[test + ':' + kind] = counts.get(test + ':' + kind, 0) + 1
    return None

try:
    with ExitStack() as stack:
        for kind, function in [('load', ResearchRepository.load), ('cli', cli.execute),
                               ('probe', scheduled_operator.check)]:
            stack.enter_context(Returns(function, snapshot=lambda value, kind=kind: snapshot(kind, value)))
        sys.argv = [str(runner), *arguments]
        runpy.run_path(str(runner), run_name='__main__')
finally:
    stream.close()
    (HERE / (label + '-return-counts.json')).write_text(json.dumps(counts, indent=2), encoding='utf-8')
