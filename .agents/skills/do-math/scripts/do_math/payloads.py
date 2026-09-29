"""Content-addressed immutable large JSON leaves, with exact logical values.

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

LIMIT = 65536


class FrozenText(str):
    def __deepcopy__(self, memo): return self


def seal(value, raw=None, digest=None):
    """Seal the string ``value`` with its canonical bytes; ``digest`` is their SHA-256 when already known."""
    from .repository import canonical_json
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
    from .repository import canonical_json

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


def decode(envelope, read_payload, git_dir=None):
    """Restore externalized payloads; ``git_dir`` names the repository they are read from.

    A payload blob this process already matched in that repository
    (repository.VERIFIED_ARTIFACTS) is parsed but not hashed or re-checked
    for canonical encoding again: its path is its digest and bundles are
    immutable.
    """
    from .values import is_sha256, reject_constant, unique_pairs
    from .repository import canonical_json, artifact_verified, mark_artifact_verified
    if set(envelope) not in ({'contract_id','family','record'}, {'contract_id','family','record','payloads'}):
        raise ValueError('invalid record envelope fields')
    value = deepcopy(envelope['record'])
    references = envelope.get('payloads', [])
    if not isinstance(references, list): raise ValueError('payload references must be a list')
    for ref in references:
        if (not isinstance(ref, dict) or set(ref) != {'tokens','path','sha256','bytes'} or not isinstance(ref['tokens'], list)
                or any(type(t) not in {str,int} or type(t) is int and t < 0 for t in ref['tokens'])
                or not is_sha256(ref['sha256'])
                or type(ref['bytes']) is not int or ref['bytes'] < LIMIT
                or ref['path'] != ARTIFACT_ROOT + 'payload-' + ref['sha256'] + '/value.json'):
            raise ValueError('invalid immutable payload reference')
        cache = getattr(read_payload, 'decoded', {})
        key = (ref['path'], ref['sha256'], ref['bytes'])
        if key not in cache:
            raw = read_payload(ref['path'])
            known = git_dir is not None and artifact_verified(git_dir, ref['path'], ref['sha256'], ref['bytes'])
            if len(raw) != ref['bytes'] or not known and hashlib.sha256(raw).hexdigest() != ref['sha256']:
                raise ValueError('immutable payload bytes differ')
            decoded = json.loads(raw, object_pairs_hook=unique_pairs, parse_constant=reject_constant)
            if not known:
                if canonical_json(decoded) != raw:
                    raise ValueError('noncanonical immutable payload')
                if git_dir is not None:
                    mark_artifact_verified(git_dir, ref['path'], ref['sha256'], len(raw))
            if not _eligible(decoded):
                raise ValueError('payload is not an externalized immutable field')
            cache[key] = seal(decoded, raw, ref['sha256'])  # matched above or earlier
        parent = value
        try:
            if not ref['tokens']:
                if value is not None or len(references) != 1: raise ValueError('payload root overlaps')
                value = cache[key]
                continue
            for token in ref['tokens'][:-1]: parent = parent[token]
            last = ref['tokens'][-1]
            if parent[last] is not None: raise ValueError('payload coordinate overlaps')
            parent[last] = cache[key]
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
