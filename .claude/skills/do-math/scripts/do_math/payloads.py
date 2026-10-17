"""Content-addressed large text and repeated structural snapshots, with exact values.

The codec is a storage boundary, not an authority cache. Blob bytes are checked
the first time this process reads them from a repository (VERIFIED_ARTIFACTS);
only these decoded immutable values can reuse their encoding in memory.
"""
from copy import deepcopy
import hashlib
import json
from pathlib import Path
from typing import Any

from .values import bytes_evidence
from .state_contract import ARTIFACT_ROOT
from .canonical import FrozenText, canonical_json
from .values import is_sha256

LIMIT = 65536


_SNAPSHOT_PREFIX = ARTIFACT_ROOT + 'snapshot-'
_SNAPSHOT_FAMILIES = frozenset({'review_cycles', 'delegation_applications', 'intent_imports', 'review_inputs'})


def _snapshot_selected(family, tokens, value):
    """One storage selection rule; keep record IDs/scalar summaries inline."""
    return isinstance(value, (dict, list)) and len(tokens) == 1 and family in _SNAPSHOT_FAMILIES


def _encode_snapshot(value, blobs):
    """Return the root reference and add each distinct immutable node once."""
    def node(document):
        raw = canonical_json(document)
        digest = hashlib.sha256(raw).hexdigest()
        path = _SNAPSHOT_PREFIX + digest + '/value.json'
        blobs[path] = raw
        return digest

    def cell(value):
        if isinstance(value, (dict, list)):
            return ['node', visit(value)]
        if isinstance(value, FrozenText):
            path = ARTIFACT_ROOT + 'payload-' + value.payload_hash + '/value.json'
            blobs[path] = value.payload_bytes
            return ['text', value.payload_hash, len(value.payload_bytes)]
        return ['value', value]

    def visit(value):
        if isinstance(value, dict):
            # A canonical compressed binary key trie. Inserting/changing one
            # coordinate rewrites only its key path, not the complete map of
            # child references. The terminal 0 makes UTF-8 key paths prefix-free;
            # a byte is encoded as 1 followed by its eight bits. No key hash or
            # probabilistic collision rule is needed.
            from bisect import bisect_left
            rows = []
            for key, child in value.items():
                if not isinstance(key, str):
                    raise ValueError('snapshot object keys must be strings')
                bits = ''.join('1' + format(byte, '08b') for byte in key.encode('utf-8')) + '0'
                rows.append((bits, key, child))
            rows.sort(key=lambda row: row[0])
            paths = [row[0] for row in rows]
            work, built = [(0, len(rows), None)], {}
            while work:
                lo, hi, branch = work.pop()
                if lo == hi:
                    built[lo, hi] = node({'kind': 'object'})
                elif hi - lo == 1:
                    _, key, child = rows[lo]
                    built[lo, hi] = node({'kind': 'object', 'key': key, 'value': cell(child)})
                elif branch is not None:
                    bit, mid = branch
                    built[lo, hi] = node({'kind': 'object', 'bit': bit,
                        'zero': built[lo, mid], 'one': built[mid, hi]})
                else:
                    first, last = paths[lo], paths[hi - 1]
                    bit = next(i for i, (a, b) in enumerate(zip(first, last)) if a != b)
                    mid = bisect_left(paths, first[:bit] + '1', lo, hi)
                    work.extend([(lo, hi, (bit, mid)), (mid, hi, None), (lo, mid, None)])
            return built[0, len(rows)]
        prefix = node({'kind': 'list'})
        for child in value:
            prefix = node({'kind': 'list', 'previous': prefix, 'item': cell(child)})
        return prefix

    digest = visit(value)
    path = _SNAPSHOT_PREFIX + digest + '/value.json'
    return {'path': path, 'sha256': digest, 'bytes': len(blobs[path])}


def _decode_snapshot(reference, read_json, read_text):
    """Verify the whole reachable graph and materialize fresh containers.

    read_json/read_text are payloads' existing checked artifact boundary. Only
    encoded node documents are memoized for this decode, never domain dicts.
    List prefixes are followed iteratively, independently of revision count.
    """
    nodes, active = {}, set()

    def document(digest, size=None):
        if not is_sha256(digest):
            raise ValueError('invalid snapshot node reference')
        if digest not in nodes:
            value, raw = read_json(_SNAPSHOT_PREFIX + digest + '/value.json', digest, size)
            if (not isinstance(value, dict) or value.get('kind') not in {'object', 'list'}
                    or value['kind'] == 'object' and not (
                        set(value) == {'kind'}
                        or set(value) == {'kind', 'key', 'value'} and isinstance(value['key'], str)
                        or set(value) == {'kind', 'bit', 'zero', 'one'} and type(value['bit']) is int and value['bit'] >= 0)
                    or value['kind'] == 'list' and set(value) not in ({'kind'}, {'kind', 'previous', 'item'})):
                raise ValueError('invalid snapshot node')
            nodes[digest] = value
        # Only the root supplies size, and read_json checked its bytes above.
        return nodes[digest]

    def cell(value):
        if not isinstance(value, list) or not value:
            raise ValueError('invalid snapshot cell')
        if len(value) == 2 and value[0] == 'node':
            return visit(value[1])
        if len(value) == 2 and value[0] == 'value' and type(value[1]) in {str, int, bool, type(None)}:
            return value[1]
        if (len(value) == 3 and value[0] == 'text' and is_sha256(value[1])
                and type(value[2]) is int):
            return read_text(value[1], value[2])
        raise ValueError('invalid snapshot cell')

    def visit(digest, size=None):
        if not is_sha256(digest):
            raise ValueError('invalid snapshot node reference')
        if digest in active:  # pragma: no cover - decode verifies each node's SHA256; a back edge needs a hash fixed point, which finite hostile-byte fixtures cannot construct
            raise ValueError('cyclic snapshot reference')
        root_digest = digest
        active.add(digest)
        try:
            value = document(digest, size)
            if value['kind'] == 'object':
                result, work, seen = {}, [digest], set()
                while work:
                    current = work.pop()
                    if current in seen:
                        raise ValueError('overlapping snapshot object coordinates')
                    seen.add(current)
                    row = document(current)
                    if row['kind'] != 'object':
                        raise ValueError('snapshot object branch is not an object')
                    if 'key' in row:
                        if row['key'] in result:
                            raise ValueError('duplicate snapshot object key')
                        result[row['key']] = cell(row['value'])
                    elif 'bit' in row:
                        if not is_sha256(row['zero']) or not is_sha256(row['one']):
                            raise ValueError('invalid snapshot node reference')
                        work.extend([row['one'], row['zero']])
                return result
            items, seen = [], set()
            while 'previous' in value:
                if digest in seen:  # pragma: no cover - verified SHA256 list links cannot repeat without constructing a hash cycle; retain the guard against such a graph
                    raise ValueError('cyclic snapshot list prefix')
                seen.add(digest)
                items.append(value['item'])
                digest = value['previous']
                value = document(digest)
                if value['kind'] != 'list':
                    raise ValueError('snapshot prefix is not a list')
            return [cell(item) for item in reversed(items)]
        finally:
            # digest changes while following a list prefix.
            active.remove(root_digest)

    return visit(reference['sha256'], reference['bytes'])



def seal(value, raw=None, digest=None):
    """Seal the string ``value`` with its canonical bytes; ``digest`` is their SHA-256 when already known."""
    from .canonical import canonical_json
    raw = canonical_json(value) if raw is None else raw
    result = FrozenText(value)
    result.payload_bytes = raw
    result.payload_hash = digest or hashlib.sha256(raw).hexdigest()
    return result


def _eligible(value):
    # Only large strings (source and document text) are sealed; mutable task
    # and history containers never are. One payload can appear in several records.
    return isinstance(value, str) and len(value) >= LIMIT // 6


# Children that can never be sealed and hold nothing to seal.
_LEAVES = {bool, int, type(None)}


def seal_large(value):
    """Seal large eligible leaves of ``value``; plain dicts and lists change in place.

    The walk visits every node of a state on each save, so leaves that cannot
    be sealed (scalars, short plain strings) are skipped without a call, and a
    string already encoded below the limit is not encoded again. It rejects a
    float, which the storage value domain excludes: a record equal to its
    parent's under ``==`` (``1.0 == 1``) is neither schema-checked nor
    serialized again (StateContract.validate, repository._encode_families).
    """
    from .canonical import canonical_json

    def walk(value):
        if isinstance(value, FrozenText): return value
        if isinstance(value, float):
            raise ValueError("JSON floating-point numbers are not permitted")
        if _eligible(value):
            raw = canonical_json(value)
            return seal(value, raw) if len(raw) >= LIMIT else value
        if isinstance(value, dict):
            for key, child in value.items():
                kind = type(child)
                if kind in _LEAVES or kind is str and len(child) < LIMIT // 6 or isinstance(child, FrozenText):
                    continue
                sealed = walk(child)
                if sealed is not child:
                    value[key] = sealed
        elif isinstance(value, list):
            for index, child in enumerate(value):
                kind = type(child)
                if kind in _LEAVES or kind is str and len(child) < LIMIT // 6:
                    continue
                sealed = walk(child)
                if sealed is not child:
                    value[index] = sealed
        return value

    return walk(value)


_PLAIN = {str, int, bool, type(None)}


def encode(envelope):
    """Replace each sealed payload of the record by a reference to its blob.

    Only sealed values carry payload bytes: plain scalars and strings are
    copied without a call, plain dicts and lists skip the attribute probe, and
    a payload's coordinate is copied from the walk's path only when found.
    """
    blobs, references, tokens = {}, [], []
    def visit(value):
        if _snapshot_selected(envelope['family'], tokens, value):
            references.append({'tokens': list(tokens), **_encode_snapshot(value, blobs)})
            return None
        kind = type(value)
        if kind is not dict and kind is not list and hasattr(value, 'payload_bytes'):
            raw, digest = value.payload_bytes, value.payload_hash
            path = ARTIFACT_ROOT + 'payload-' + digest + '/value.json'
            blobs[path] = raw
            references.append({'tokens':list(tokens), 'path':path, 'sha256':digest, 'bytes':len(raw)})
            return None
        if isinstance(value, dict):
            result = {}
            for key in sorted(value):
                child = value[key]
                if type(child) in _PLAIN:
                    result[key] = child
                else:
                    tokens.append(key)
                    result[key] = visit(child)
                    tokens.pop()
            return result
        if isinstance(value, list):
            result = []
            for index, child in enumerate(value):
                if type(child) in _PLAIN:
                    result.append(child)
                else:
                    tokens.append(index)
                    result.append(visit(child))
                    tokens.pop()
            return result
        return value
    result = {**envelope, 'record':visit(envelope['record'])}
    if references: result['payloads'] = references
    return result, blobs


def _read_json_blob(path, digest, size, read_payload, git_dir, label):
    """The canonical-JSON variant of the shared immutable artifact boundary.

    Both text leaves and structural nodes register a match only after checking
    the bytes' canonical JSON. Missing nodes are restoration failures.
    """
    from .values import reject_constant, unique_pairs
    from .repository import artifact_verified, mark_artifact_verified
    try:
        raw = read_payload(path)
    except (KeyError, FileNotFoundError) as error:
        raise ValueError('immutable ' + label + ' missing: ' + path) from error
    known = git_dir is not None and artifact_verified(git_dir, path, digest, size)
    if (size is not None and len(raw) != size) or not known and hashlib.sha256(raw).hexdigest() != digest:
        raise ValueError('immutable ' + label + ' bytes differ')
    decoded = json.loads(raw, object_pairs_hook=unique_pairs, parse_constant=reject_constant)
    if not known:
        if canonical_json(decoded) != raw:
            raise ValueError('noncanonical immutable ' + label)
        if git_dir is not None:
            mark_artifact_verified(git_dir, path, digest, len(raw))
    return decoded, raw


def _read_text(ref, read_payload, git_dir):
    cache = getattr(read_payload, 'decoded', {})
    key = (ref['path'], ref['sha256'], ref['bytes'])
    if key not in cache:
        decoded, raw = _read_json_blob(ref['path'], ref['sha256'], ref['bytes'], read_payload, git_dir, 'payload')
        if not _eligible(decoded):
            raise ValueError('payload is not an externalized immutable field')
        cache[key] = seal(decoded, raw, ref['sha256'])
    return cache[key]


def decode(envelope, read_payload, git_dir=None):
    """Restore externalized payloads; ``git_dir`` names the repository they are read from.

    A payload blob this process already matched in that repository
    (repository.VERIFIED_ARTIFACTS) is parsed but not hashed or re-checked
    for canonical encoding again: its path is its digest and bundles are
    immutable.
    """
    from .values import is_sha256
    from .canonical import canonical_json
    if set(envelope) not in ({'contract_id','family','record'}, {'contract_id','family','record','payloads'}):
        raise ValueError('invalid record envelope fields')
    value = deepcopy(envelope['record'])
    references = envelope.get('payloads', [])
    if not isinstance(references, list): raise ValueError('payload references must be a list')
    for ref in references:
        snapshot = isinstance(ref, dict) and isinstance(ref.get('path'), str) and ref['path'].startswith(_SNAPSHOT_PREFIX)
        prefix = _SNAPSHOT_PREFIX if snapshot else ARTIFACT_ROOT + 'payload-'
        if (not isinstance(ref, dict) or set(ref) != {'tokens','path','sha256','bytes'} or not isinstance(ref['tokens'], list)
                or any(type(t) not in {str,int} or type(t) is int and t < 0 for t in ref['tokens'])
                or not is_sha256(ref['sha256'])
                or type(ref['bytes']) is not int or ref['bytes'] < (1 if snapshot else LIMIT)
                or ref['path'] != prefix + ref['sha256'] + '/value.json'):
            raise ValueError('invalid immutable payload reference')
        if snapshot:
            def read_json(path, digest, size):
                return _read_json_blob(path, digest, size, read_payload, git_dir, 'snapshot')
            def read_text(digest, size):
                if size < LIMIT:
                    raise ValueError('invalid snapshot text reference')
                return _read_text({'path': ARTIFACT_ROOT + 'payload-' + digest + '/value.json',
                                  'sha256': digest, 'bytes': size}, read_payload, git_dir)
            restored = _decode_snapshot(ref, read_json, read_text)
        else:
            restored = _read_text(ref, read_payload, git_dir)
        parent = value
        try:
            if not ref['tokens']:
                if value is not None or len(references) != 1: raise ValueError('payload root overlaps')
                value = restored
                continue
            for token in ref['tokens'][:-1]: parent = parent[token]
            last = ref['tokens'][-1]
            if parent[last] is not None: raise ValueError('payload coordinate overlaps')
            parent[last] = restored
        except (KeyError, IndexError, TypeError) as error:
            raise ValueError('invalid payload coordinate') from error
    # Enforce the one current encoding, including mandatory externalization of
    # large immutable fields. No implicit migration of old inline records.
    rebuilt, _ = encode({**{k:envelope[k] for k in ('contract_id','family')}, 'record':seal_large(value)})
    if rebuilt != envelope:
        raise ValueError('record differs from canonical payload encoding')
    return value


def json_safe(value: Any) -> Any:
    """A JSON-safe projection of a reported value: bytes, paths, unsafe integers and floats made explicit."""
    if isinstance(value, bytes):
        return bytes_evidence(value)
    if isinstance(value, dict):
        return {str(k): json_safe(v) for k, v in value.items()}
    if isinstance(value, (tuple, list)):
        return [json_safe(v) for v in value]
    if isinstance(value, Path):
        return str(value)
    if isinstance(value, int) and not isinstance(value, bool) and abs(value) > (1 << 53) - 1:
        return str(value)
    if isinstance(value, float):
        # Opaque provider reports retain their original artifact bytes. State
        # projections represent decimals explicitly without integer rounding.
        return {"reported_decimal": repr(value)}
    return value
