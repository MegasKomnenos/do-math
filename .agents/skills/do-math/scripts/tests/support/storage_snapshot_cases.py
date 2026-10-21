"""Exact logical snapshot bytes and a fresh schema-backed repository reader."""
import hashlib

from do_math.repository import ResearchRepository
from support.state_builders import installed_contract


def payload_state(count=8):
    """Current-schema state with distinct text blobs and shared nested snapshots."""
    from support.state_builders import current_state
    from do_math.canonical import exact_content_hash
    instance, runtime = current_state({'object_format': 'sha1'})
    for index in range(count):
        text = f'exact 원문 {index}\r\n' * 6000
        raw = text.encode('utf-8')
        runtime['inputs'].append({'id': f'UI-payload-{index}', 'text': text,
            'sha256': hashlib.sha256(raw).hexdigest(), 'config': {'goal': 'fixture'},
            'created_at': '2026-01-01T00:00:00+00:00'})
    proposal = {'rows': [{'id': index, 'flags': [True, None, index]} for index in range(8)]}
    runtime['review_inputs'] = {'seat': {'proposal_digest': exact_content_hash(proposal),
        'proposal': proposal, 'request': {'same': proposal, 'text': runtime['inputs'][-1]['text']},
        'slot': 'seat', 'visible_execution_ids': [], 'workspace': 'fixture',
        'supplied_sources': [], 'source_snapshot': 'a' * 40}}
    return instance, runtime


def snapshot_files(store, head):
    return store.read_many(store.list_files('research/', head) +
                           store.list_files('runtime/', head), head)


def fresh_reader(store):
    # A new installed contract identity forces decoding, rather than the
    # publisher's validated-state memo, on the same Git port and clock.
    return ResearchRepository(store.repository, store._store.instance_id,
        contract=installed_contract(), backend=store._store._backend, clock=store._store._clock)
