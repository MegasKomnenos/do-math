"""Content-addressed immutable large JSON leaves, with exact logical values.

The codec is a storage boundary, not an authority cache. Blob bytes are checked
the first time this process reads them from a repository (VERIFIED_ARTIFACTS);
only these decoded immutable values can reuse their encoding in memory.
"""
from copy import deepcopy
import hashlib
import json

LIMIT = 65536


class FrozenDict(dict):
    def __deepcopy__(self, memo): return self
    def _deny(self, *args, **kwargs): raise TypeError('sealed payload is immutable; author a new value')
    __setitem__ = __delitem__ = clear = pop = popitem = setdefault = update = __ior__ = _deny


class FrozenList(list):
    def __deepcopy__(self, memo): return self
    def _deny(self, *args, **kwargs): raise TypeError('sealed payload is immutable; author a new value')
    __setitem__ = __delitem__ = append = clear = extend = insert = pop = remove = reverse = sort = __iadd__ = __imul__ = _deny


class FrozenText(str):
    def __deepcopy__(self, memo): return self


def frozen(value):
    if isinstance(value, dict): return FrozenDict({k:frozen(v) for k,v in value.items()})
    if isinstance(value, list): return FrozenList(frozen(v) for v in value)
    return value


def seal(value, raw=None, digest=None):
    """Freeze ``value`` with its canonical bytes; ``digest`` is their SHA-256 when already known."""
    from .repository import canonical_json
    raw = canonical_json(value) if raw is None else raw
    result = FrozenText(value) if isinstance(value, str) else frozen(value)
    result._payload_bytes = raw
    result._payload_hash = digest or hashlib.sha256(raw).hexdigest()
    return result


def _eligible(key, value):
    # Immutable source text and trust manifests; mutable task/history arrays are
    # never frozen as a whole. The same payload can appear in several records.
    return (isinstance(value, str) and len(value) >= LIMIT // 6
            or key == 'manifest' and isinstance(value, dict) and 'foundation_profile' in value)


def seal_large(value):
    from .repository import canonical_json
    if isinstance(value, (FrozenDict, FrozenList, FrozenText)): return value
    if isinstance(value, str) and len(value) >= LIMIT // 6:
        raw = canonical_json(value)
        return seal(value, raw) if len(raw) >= LIMIT else value
    if isinstance(value, dict):
        for key, child in list(value.items()):
            if isinstance(child, (FrozenDict, FrozenList, FrozenText)):
                continue
            if _eligible(key, child):
                raw = canonical_json(child)
                if len(raw) >= LIMIT:
                    value[key] = seal(child, raw)
                    continue
            value[key] = seal_large(child)
    elif isinstance(value, list):
        for index, child in enumerate(value): value[index] = seal_large(child)
    return value


def encode(envelope):
    blobs, references = {}, []
    def visit(value, tokens):
        if hasattr(value, '_payload_bytes'):
            raw, digest = value._payload_bytes, value._payload_hash
            path = 'runtime/artifacts/payload-' + digest + '/value.json'
            blobs[path] = raw
            references.append({'tokens':tokens, 'path':path, 'sha256':digest, 'bytes':len(raw)})
            return None
        if isinstance(value, dict): return {k:visit(value[k], [*tokens,k]) for k in sorted(value)}
        if isinstance(value, list): return [visit(v, [*tokens,i]) for i,v in enumerate(value)]
        return value
    result = {**envelope, 'record':visit(envelope['record'], [])}
    if references: result['payloads'] = references
    return result, blobs


def decode(envelope, read_payload, git_dir=None):
    """Restore externalized payloads; ``git_dir`` names the repository they are read from.

    A payload blob this process already matched in that repository
    (repository.VERIFIED_ARTIFACTS) is parsed but not hashed or re-checked
    for canonical encoding again: its path is its digest and bundles are
    immutable.
    """
    from .file_io import is_sha256, reject_constant, unique_pairs
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
                or ref['path'] != 'runtime/artifacts/payload-' + ref['sha256'] + '/value.json'):
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
            cache[key] = seal(decoded, raw, ref['sha256'])  # matched above or earlier
        if not _eligible(ref['tokens'][-1] if ref['tokens'] else 'manifest', cache[key]):
            raise ValueError('payload is not an externalized immutable field')
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
