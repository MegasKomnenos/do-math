"""Preservation assertions for the two recorded default sources, not a verifier.

Lean 4.32.0, current lean_evidence.check_file emitter; raw capture and acquisition
report: finish/resume-lean-preservation-capture (2026-10-02). The Nat proof is a
lambda/application DAG and its transitive closure has 32 constants. Historical
pretty strings and fixture-label hashes are not current compiler evidence.
"""
from copy import deepcopy
import hashlib
import json
from pathlib import Path

from do_math.canonical import exact_content_hash


def recorded_defaults():
    raw = Path(__file__).with_name('lean_default_facts.json').read_bytes()
    if hashlib.sha256(raw).hexdigest() != '0263acb7dbfdc2aacde306ba6712f9f589e0825f76730e636cd25df822713162':
        raise AssertionError('default Lean capture changed: independently recapture before updating the pin')
    return json.loads(raw)


def assert_default_result(test, result, name):
    facts = recorded_defaults()[name]
    dependencies = facts['dependencies'][name]
    expected = deepcopy(result)
    expected.update(status='verified', reason=None, exit_code=0, stderr='',
        source_sha256=hashlib.sha256(facts['source'].encode('utf-8')).hexdigest(),
        declarations=[name], declaration_signatures=facts['signatures'],
        signature_hash=exact_content_hash(facts['signatures']), axioms=facts['axioms'],
        declaration_evidence=facts['declaration_evidence'],
        dependency_closure={name: sorted(dependencies)},
        dependency_evidence={key: exact_content_hash(value) for key, value in dependencies.items()})
    test.assertEqual(result, expected)
    test.assertTrue(result['dependency_closure'][name])
    test.assertTrue(result['declaration_evidence'][name]['value'])
    test.assertEqual(result['signature_hash'], exact_content_hash(result['declaration_signatures']))
    test.assertEqual(set(result['dependency_evidence']), set(result['dependency_closure'][name]))
    return expected
