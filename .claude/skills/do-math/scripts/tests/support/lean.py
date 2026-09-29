"""The Lean double at ``formal._worker``'s spawn seam (설계 4.1, 4.5): answers a do-math check file as Lean does.

``formal.verify_lean`` writes a check file (``lean_evidence.check_file``): the
source, then per declaration a signature ``#check`` between two ``#eval``
markers and ``#print axioms``, and with evidence extraction a
``#do_math_dependencies`` command. The double reads that file and writes what
Lean writes for it: the markers around the signature, the axiom line, and the
dependency rows (``__DO_MATH_DEPENDENCY__`` per constant,
``__DO_MATH_DEPENDENCIES__`` per declaration). The recorded output in the corpus
fixes the line formats (``contracts/test_doubles_follow_corpus.py``).

``declare(name, signature=..., axioms=..., dependencies=...)`` states what Lean
reports for a declaration. An undeclared declaration defined in the source by
``theorem``, ``lemma``, ``def`` or ``abbrev`` gets the signature written there, no
axioms and no dependencies. A declaration neither declared nor defined fails as
Lean fails on an unknown identifier (exit code 1).
"""
from __future__ import annotations

import json
from pathlib import Path
import re

MARKER = re.compile(r'^#eval "__DO_MATH_SIGNATURE_BEGIN_(.+)__"$')


class LeanDouble:
    def __init__(self):
        self.declared, self.checks = {}, []

    def declare(self, name, *, signature=None, axioms=(), dependencies=None):
        """``dependencies`` maps each constant of the closure to its evidence ``{"type", "value"}``."""
        self.declared[name] = {'signature': signature, 'axioms': list(axioms), 'dependencies': dict(dependencies or {})}
        return self

    def spawn(self, command, *, cwd=None, stdout=None, stderr=None, shell=False, creationflags=0):
        return FakeLean(self, list(command), stdout, stderr)

    def facts(self, name, source):
        if name in self.declared:
            facts = dict(self.declared[name])
            if facts['signature'] is None:
                facts['signature'] = _source_signature(name, source)
            return facts
        signature = _source_signature(name, source)
        return None if signature is None else {'signature': signature, 'axioms': [], 'dependencies': {}}


def _source_signature(name, source):
    """``name`` and its binders and type as the source writes them before ``:=``, or None."""
    match = re.search(r'(?:theorem|lemma|def|abbrev)\s+' + re.escape(name) + r'(\s[^:=]*)?\s*:\s*(.+?)\s*:=', source, re.S)
    if match is None:
        return None
    binders = (match.group(1) or '').strip()
    return ' '.join(part for part in (name, binders, ':', ' '.join(match.group(2).split())) if part)


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
        text = Path(self.command[-1]).read_text(encoding='utf-8')
        lines = text.splitlines()
        declarations = [match.group(1) for match in map(MARKER.match, lines) if match]
        source = text.split('\n#eval "__DO_MATH_SIGNATURE_BEGIN_', 1)[0]
        extract = any(line.startswith('#do_math_dependencies ') for line in lines)
        self.lean.checks.append({'declarations': declarations, 'extract': extract})
        facts = {name: self.lean.facts(name, source) for name in declarations}
        unknown = [name for name, row in facts.items() if row is None]
        if unknown:
            self.stderr.write(''.join(f"proposal.lean: error: unknown identifier '{name}'\n" for name in unknown).encode())
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
