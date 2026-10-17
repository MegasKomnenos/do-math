"""Exact logical snapshot bytes and a fresh schema-backed repository reader."""
from do_math.repository import ResearchRepository
from support.state_builders import installed_contract


def snapshot_files(store, head):
    return store.read_many(store.list_files('research/', head) +
                           store.list_files('runtime/', head), head)


def fresh_reader(store):
    # A new installed contract identity forces decoding, rather than the
    # publisher's validated-state memo, on the same Git port and clock.
    return ResearchRepository(store.repository, store._store.instance_id,
        contract=installed_contract(), backend=store._store._backend, clock=store._store._clock)
