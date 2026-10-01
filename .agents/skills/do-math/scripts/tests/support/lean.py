"""The Lean double at ``formal._worker``'s spawn seam (설계 4.1, 4.5): answers a do-math check file as Lean does.

``formal.verify_lean`` writes a check file (``lean_evidence.check_file``): the
source, then per declaration a signature ``#check`` between two ``#eval``
markers and ``#print axioms``, and with evidence extraction a
``#do_math_dependencies`` command. The double reads that file and writes what
Lean writes for it: the markers around the signature, the axiom line, and the
dependency rows (``__DO_MATH_DEPENDENCY__`` per constant,
``__DO_MATH_DEPENDENCIES__`` per declaration). The recorded output in the corpus
fixes the line formats (``contracts/test_doubles_follow_corpus.py``).

``allow(source, declarations, signatures=..., axioms=..., dependencies=...)``
registers exact compiler inputs and synthetic output facts. Only the two fixed
response producers are registered by default. No source is parsed as a proof.
The product still checks signatures, forbidden axioms, evidence and trust.
"""
from __future__ import annotations

import json
from pathlib import Path
import re

from do_math.lean_evidence import LEAN_VERSION

MARKER = re.compile(r'^#eval "__DO_MATH_SIGNATURE_BEGIN_(.+)__"$')


class LeanDouble:
    def __init__(self):
        from support.default_responder import FORMAL_SOURCE
        from support.purpose_answers import SOURCE
        self.inputs, self.checks = {}, []
        self.version = f"Lean (version {LEAN_VERSION}, test double)"
        self.commands = []
        self.allow(FORMAL_SOURCE, ['t'], signatures={'t': 't : True'})
        self.allow(SOURCE, ['add_zero_fixture'],
                   signatures={'add_zero_fixture': 'add_zero_fixture (n : Nat) : n + 0 = n'})

    def allow(self, source, declarations, *, signatures, axioms=None, dependencies=None):
        """Explicit synthetic facts for exactly this source and ordered declaration list.

        The product check-file producer supplies the framing; this is input-table
        lookup, not a second Lean parser or proof/trust validator. Both preview
        and evidence extraction are allowed for the same registered input.
        """
        from copy import deepcopy
        from do_math.lean_evidence import check_file
        if set(signatures) != set(declarations):
            raise ValueError('explicit signatures must cover exactly the registered declarations')
        facts = {name: {'signature': signatures[name], 'axioms': list((axioms or {}).get(name, [])),
                        'dependencies': deepcopy((dependencies or {}).get(name, {}))} for name in declarations}
        for extract in (False, True):
            self.inputs[check_file(source.encode('utf-8'), list(declarations), extract_evidence=extract)] = facts
        return self

    def spawn(self, command, *, cwd=None, stdout=None, stderr=None, shell=False, creationflags=0):
        self.commands.append(list(command))
        return FakeLean(self, list(command), stdout, stderr)


class FakeLean:
    """One Lean process on a check file; ``wait`` runs it to completion."""

    def __init__(self, lean, command, stdout, stderr):
        self.lean, self.command, self.stdout, self.stderr = lean, command, stdout, stderr
        self.returncode = None

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False

    def wait(self, timeout=None):
        if self.command[-1] == '--version':
            self.stdout.write((self.lean.version + '\n').encode('utf-8'))
            self.returncode = 0
            return 0
        raw = Path(self.command[-1]).read_bytes()
        text = raw.decode('utf-8')
        lines = text.splitlines()
        declarations = [match.group(1) for match in map(MARKER.match, lines) if match]
        extract = any(line.startswith('#do_math_dependencies ') for line in lines)
        facts = self.lean.inputs.get(raw)
        self.lean.checks.append({'declarations': declarations, 'extract': extract,
                                 'registered': facts is not None, 'synthetic': True})
        if facts is None:
            self.stderr.write(b'proposal.lean: error: unregistered synthetic Lean source/declarations\n')
            self.returncode = 1
            return 1
        out = []
        for name in declarations:
            row = facts[name]
            axioms = ("'" + name + "' does not depend on any axioms" if not row['axioms'] else
                      "'" + name + "' depends on axioms: [" + ', '.join(row['axioms']) + ']')
            out += [f'"__DO_MATH_SIGNATURE_BEGIN_{name}__"', row['signature'], f'"__DO_MATH_SIGNATURE_END_{name}__"', axioms]
        if extract:
            constants = {}
            for name in declarations:
                constants.update(facts[name]['dependencies'])
            out += ['__DO_MATH_DEPENDENCY__' + json.dumps({'name': constant, 'evidence': evidence})
                    for constant, evidence in constants.items()]
            out += ['__DO_MATH_DEPENDENCIES__' + json.dumps(
                {'declaration': name, 'dependencies': sorted(facts[name]['dependencies']),
                 'evidence': {'type': facts[name]['signature'].split(' : ', 1)[-1], 'value': None},
                 'axioms': facts[name]['axioms']}) for name in declarations]
        self.stdout.write(''.join(line + '\n' for line in out).encode('utf-8'))
        self.returncode = 0
        return 0

    def kill(self):
        self.returncode = 1
