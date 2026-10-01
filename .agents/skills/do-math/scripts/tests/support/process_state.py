"""Process facts a new simulated owner must recompute (seam 21).

These are observed or parsed facts, not declaration tables or schemas. The
fake external resources and Sim templates represent the world outside the
owner and survive. Engine instance caches disappear with its old object.
"""
import importlib
import os
from pathlib import Path

from support.branch_gate import process_caches

PRODUCT = Path(__file__).resolve().parents[2] / 'do_math'
MAPPINGS = {
    'core_engine': ('_HASHED_INSTALLATION',),
    'file_io': ('_hashed',),
    'formal': ('_GIT_ROOTS', '_SEARCH_PATHS'),
    'planning': ('_VALID_ARTIFACTS',),
    'repository': ('VERIFIED_ARTIFACTS', '_VALIDATED_READS', '_RETAINED_READS',
                   '_ARTIFACT_FACTS', '_PUBLISHED_PARENTS'),
    'submission': ('_ISSUED_INPUTS',),
}
SLOTS = {'repository': {'_held_bytes': 0}}


def reset_owner_process():
    for name, attributes in MAPPINGS.items():
        module = importlib.import_module('do_math.' + name)
        for attribute in attributes:
            getattr(module, attribute).clear()
    for name, attributes in SLOTS.items():
        module = importlib.import_module('do_math.' + name)
        for attribute, initial in attributes.items():
            # Check registration names; misspellings must not create new globals.
            getattr(module, attribute)
            setattr(module, attribute, initial)
    for cache in process_caches(str(PRODUCT) + os.sep):
        cache.cache_clear()
