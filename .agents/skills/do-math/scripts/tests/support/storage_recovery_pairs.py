"""Recovery publications and their first decode under a fresh installed contract.

The existing execution scenes can use ``StoredRecoveries.read`` without losing
their independent content assertions. Pair and _named_fields own field walks.
Git, clock, Jobs and model responses are port doubles; engine/storage are real.
"""
from copy import deepcopy
import json

from contracts.pairs import Pair
from do_math.state_contract import validate_record
from support.state_builders import installed_contract
from support.storage_authority_pairs import _named_fields
from support.storage_records import record_store


FAMILIES = ('recoveries', 'operational_dispositions', 'maintenance_fence', 'model_policy_violation')


def reader(engine):
    return record_store(engine.store.repository, instance_id=engine.instance['id'],
        contract=installed_contract(), backend=engine.ports.git_backend, clock=engine.ports.clock)


class StoredRecoveries:
    def __init__(self, case):
        self.case, self.samples = case, []

    def keep(self, engine, branch, *, previous=None, head=None):
        cold = reader(engine)
        loaded = cold.load(head or engine.head)
        if head is None:
            self.case.assertEqual(loaded, (engine.head, engine.instance, engine.runtime))
        if previous is not None:
            self.case.assertEqual(reader(engine).load(previous[0]), previous)
        manifest = json.loads(cold.read('runtime/_state/manifest.json', loaded[0]))
        for name in FAMILIES:
            definition = cold.contract.family('runtime', name)
            if name in loaded[2]:
                self.case.assertEqual(manifest['containers'][name]['shape'], definition.shape)
            else:
                self.case.assertNotIn(name, manifest['containers'])
        self.samples.append((branch, deepcopy(loaded[1:])))
        return loaded

    def read(self, engine, branch, *, identifiers=None, head=None):
        rows = self.keep(engine, branch, head=head)[2]['executions']
        return rows if identifiers is None else {key: rows[key] for key in identifiers}


def family_pair(contract, name, samples):
    definition = contract.family('runtime', name)

    def values(state):
        runtime = state[1]
        if name not in runtime:
            return []
        return (list(runtime[name].values()) if definition.shape == 'map' else [runtime[name]])

    def receive(state):
        for value in values(state):
            validate_record(definition.checker, value, 'runtime/' + name)
            if definition.validator:
                definition.validator(value)

    return Pair('runtime.' + name, lambda root: samples, receive,
        frozenset(_named_fields(definition.schema)),
        lambda state: _named_fields(definition.schema, values(state)))


def proposal_pair(samples):
    """The open storage envelope delegates proposal checking to its domain schema."""
    from do_math.contracts import disposition_schema
    from do_math.operational_dispositions import validate_disposition
    schema = disposition_schema()

    def values(state):
        return [row['disposition'] for row in state[1].get('operational_dispositions', {}).values()]

    def receive(state):
        for value in values(state):
            validate_disposition(value)

    return Pair('operational proposal', lambda root: samples, receive,
        frozenset(_named_fields(schema)), lambda state: _named_fields(schema, values(state)))
