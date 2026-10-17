"""Real kind proposals and independent checker preparation shared by storage tests."""
from copy import deepcopy
from pathlib import Path


def kind_scene():
    from support.sim import Sim
    from support.engine_lifecycle import clear_work
    sim = Sim.activated()
    clear_work(sim)
    return sim


def propose_kinds(engine):
    """Publish two definitions through a returned research worker's extensions."""
    from support.engine_lifecycle import _ended_execution
    _ended_execution(engine, 'EX-kind-author', 'research_work')
    definitions = [dict(family=family, token=token, meaning='독립 원문 e\u0301\r\n' + token,
                        constraints={}) for family, token in
                   (('knowledge', 'pending_fact'), ('relation', 'pending_link'))]
    engine.runtime['executions']['EX-kind-author']['extensions'] = {'kind_definitions': deepcopy(definitions)}
    engine._apply_extensions({'role': 'research_work'}, 'EX-kind-author')
    engine._save()
    return definitions


def kind_checker(engine, action, identifier):
    """A real registered independent checker whose input basis came from _context."""
    from do_math.canonical import exact_content_hash
    context = engine._context(action, Path(engine.instance['workspace']) / identifier)
    definition = context['kind_definition_to_check']
    execution = engine._register_execution(action, {'id': identifier, 'role': 'maintenance', 'status': 'running'})
    execution.update(input_snapshot=engine.head, input_basis={'kind_definition': {
        'id': definition['id'], 'sha256': exact_content_hash(definition)}})
    # End using the real lifecycle, without a model/native process.
    from do_math.execution_lifecycle import transition_execution
    for status in ('stopping', 'ended'):
        transition_execution(execution, status, at=engine.ports.clock.now(),
                             **({'outcome': 'execution_incomplete'} if status == 'ended' else {}))
    return execution, deepcopy(definition)
