"""Explicit expensive-test labels; unlabeled tests conservatively use integration."""
GROUPS = ('unit', 'integration', 'lean', 'resource', 'archive')

# These modules exercise in-process rules or disposable files, not real Git,
# compilers, providers, servers or process lifetimes. New modules are opt-in.
UNIT_MODULES = frozenset('''
test_academic test_budget test_claude_adapter test_claude_stream
test_contract_checks test_decision_basis test_execution_window
test_knowledge test_knowledge_io test_machine_scheduling test_model_metadata_boundary
test_model_runner test_observation_audit1 test_observations
test_planning test_provider_final_contract test_questions test_reference_catalog
test_review_cycle test_review_scope_wire test_revision_obligations test_scholarly
test_state_checks test_state_contract_registration test_task_scope
test_preparation_cache test_test_runner
'''.split())


def test_group(group):
    if group not in GROUPS:
        raise ValueError('unknown test group: ' + str(group))
    def decorate(target):
        target.do_math_test_group = group
        return target
    return decorate


def group_for(test):
    method = getattr(test, getattr(test, '_testMethodName', ''), None)
    group = getattr(method, 'do_math_test_group', None) or getattr(type(test), 'do_math_test_group', None)
    if group is not None:
        if group not in GROUPS:
            raise ValueError('unknown test group: ' + str(group))
        return group
    return 'unit' if type(test).__module__.split('.')[-1] in UNIT_MODULES else 'integration'
