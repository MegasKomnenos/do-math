"""Real failure producers on the owner/worker, with faults only in the model port."""
import sys

from support.engine_lifecycle import clear_work
from support.role_answers import disposition
from support.scheduling_model import explicit, native_final, scenario_model
from support.scheduling_recovery import empty_plan, failed_plan_sim
from support.sim import Sim, built


def _failed(root, shared, *, kind):
    if kind not in {'output_validation', 'submission_failure'}:
        raise AssertionError('failure producer is missing: ' + kind)
    config = {'max_output_repairs': 0}
    sim = Sim.activated(root, shared=shared, config=config)
    clear_work(sim)
    sim.engine._enqueue('research_plan', id='AC-failed', reason='Compare the current task population')
    if kind == 'output_validation':
        model = scenario_model(sim)
        output = empty_plan(dispositions=[disposition('TK-absent')])
    else:
        from do_math import submission
        from support.submission_calls import submission_model
        from support.submission_scenes import withhold_publication, release_publication, unmatched
        model = submission_model(sim)
        output = empty_plan()
        model.after('research_plan', lambda context, workspace: withhold_publication(sim, context['execution_id']))
    model.on('research_plan').reply(native_final(output)
                                   if kind == 'output_validation' else explicit(output))
    sim.engine._save()
    sim.step()
    if kind == 'submission_failure':
        if sim.runtime['waiting_actions']['AC-failed']['kind'] != 'submission_publication':
            raise AssertionError('the exact model submission did not reach publication waiting')
        release_publication(sim)
        # An independent receiver uses its own actual repository, without the first receiver's byte memo.
        sim.engine = unmatched(sim, 'failure-receiving-repository')
        sim.repository = sim.engine.store.repository
        backend = sim.ports.git_backend
        original = backend.read_objects
        faults = []
        receiving = submission.read_sealed_submission.__code__
        def unavailable(repository, specs):
            frame = sys._getframe(1)
            while frame is not None:
                if frame.f_code is receiving and not faults:
                    faults.append(list(specs))
                    raise OSError('Git objects temporarily unavailable during sealed submission receipt')
                frame = frame.f_back
            return original(repository, specs)
        backend.read_objects = unavailable
        try:
            sim.engine._retry_submission_publications()
        finally:
            del backend.read_objects
        if len(faults) != 1:
            raise AssertionError('the external Git read fault was not reached exactly once')
    entry = sim.runtime['waiting_actions']['AC-failed']
    if entry['kind'] != kind:
        raise AssertionError('real failure did not produce its declared kind: ' + repr(entry))
    return sim


def failure_sim(kind):
    if kind == 'execution_failure':
        return failed_plan_sim()
    if kind != 'output_validation':
        raise AssertionError('an independent receiver scene needs its own root: ' + kind)
    return built('failed-action-contract', _failed, kind=kind)


def failed_action_scene(root, kind):
    """Return the actual owner's failure before asking whether it can be frozen."""
    return _failed(root, None, kind=kind)
