"""The Lean double at ``formal._worker``'s spawn seam (설계 4.1, 4.5): answers a do-math check file as Lean does.

``formal.verify_lean`` writes a check file (``lean_evidence.check_file``): the
source, then per declaration a signature ``#check`` between two ``#eval``
markers and ``#print axioms``, and with evidence extraction a
``#do_math_dependencies`` command. The double reads that file and writes what
Lean writes for it: the markers around the signature, the axiom line, and the
dependency rows (``__DO_MATH_DEPENDENCY__`` per constant,
``__DO_MATH_DEPENDENCIES__`` per declaration). The recorded output in the corpus
fixes the line formats (``contracts/test_doubles_follow_corpus.py``).

``allow(source, declarations, signatures=..., declaration_evidence=...,
axioms=..., dependencies=...)``
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
        defaults = json.loads(Path(__file__).with_name('lean_default_facts.json').read_bytes())
        for name, source in [('t', FORMAL_SOURCE), ('add_zero_fixture', SOURCE)]:
            facts = defaults[name]
            if source != facts['source']:
                raise ValueError('default source differs from its recorded Lean facts')
            self.allow(source, [name], signatures=facts['signatures'],
                       declaration_evidence=facts['declaration_evidence'],
                       axioms=facts['axioms'], dependencies=facts['dependencies'])

    def allow(self, source, declarations, *, signatures, declaration_evidence, axioms, dependencies):
        """Explicit synthetic facts for exactly this source and ordered declaration list.

        The product check-file producer supplies the framing; this is input-table
        lookup, not a second Lean parser or proof/trust validator. Passing both
        evidence tables as None explicitly registers preview only (the old corpus
        records no kernel evidence); an extraction request then fails closed.
        """
        from copy import deepcopy
        from do_math.lean_evidence import check_file
        # Signatures are display output, not a grammar for kernel evidence. In
        # particular a binder contains colons; the caller supplies the full type
        # and value independently. Explicit empty synthetic closures are allowed,
        # but omission never manufactures evidence for existing callers.
        preview_only = declaration_evidence is None and dependencies is None
        tables = [('signatures', signatures), ('axioms', axioms)]
        if not preview_only:
            tables += [('declaration evidence', declaration_evidence), ('dependencies', dependencies)]
        for label, table in tables:
            if not isinstance(table, dict):
                raise ValueError('explicit ' + label + ' must be a table')
            if set(table) != set(declarations):
                raise ValueError('explicit ' + label + ' must cover exactly the registered declarations')
        constants = {}
        for name in (() if preview_only else declarations):
            for evidence in [declaration_evidence[name], *dependencies[name].values()]:
                if (set(evidence) != {'type', 'value'} or not isinstance(evidence['type'], str)
                        or evidence['value'] is not None and not isinstance(evidence['value'], str)):
                    raise ValueError('explicit evidence requires type and value')
            for constant, evidence in dependencies[name].items():
                if constant in constants and constants[constant] != evidence:
                    raise ValueError('conflicting dependency evidence: ' + constant)
                constants[constant] = evidence
        facts = {name: {'signature': signatures[name], 'axioms': list(axioms[name]),
                        **({} if preview_only else {'evidence': deepcopy(declaration_evidence[name]),
                        'dependencies': deepcopy(dependencies[name])})} for name in declarations}
        for extract in (False, True):
            key = check_file(source.encode('utf-8'), list(declarations), extract_evidence=extract)
            if extract and preview_only:
                self.inputs.pop(key, None)
            else:
                self.inputs[key] = facts
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
                 'evidence': facts[name]['evidence'],
                 'axioms': facts[name]['axioms']}) for name in declarations]
        self.stdout.write(''.join(line + '\n' for line in out).encode('utf-8'))
        self.returncode = 0
        return 0

    def kill(self):
        self.returncode = 1
