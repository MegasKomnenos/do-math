"""Judge formal proofs from outside do-math's own index.

    python judge.py <instance> --out <new folder> [--no-paranoid] [--no-review] [--timeout <seconds>]

do-math decides that a statement is formal from its structural index: the Lean proof is complete and
every axiom it depends on is allowed. The index is computed inside a Lean process that has loaded the
modules it describes, so it is only as good as that process. The judge checks the same thing from
outside. Lean's exporter writes a theorem out together with everything it rests on, and
`lake comparator` reads that export alone: it compares it with a second export, works out the axioms
again, and replays every declaration through the kernel.

There are two uses.

A publication that brings a formal proof, or changes one, has those theorems judged before it is
installed. The export is compared with itself, which leaves the axioms and the kernel. The runner does
this, and so does `init` for the canon it starts from (runner.py).

This command judges the root of an instance whose root is formally proved or refuted, against the root
as the instance's first commit fixed it. It shows that the statement proved is the statement that was
posed, with every definition the statement depends on unchanged, and that the proof uses only the
allowed axioms and is accepted by the kernel, and by the other kernels Lean ships unless
--no-paranoid is given. A rejection is written to the instance as a request for a comprehensive
review of the proof, unless --no-review is given.

Every tool runs inside one job of the instance's Lean broker, so that the memory it takes is counted
with the compiles. The job is a small Lean file that starts the tools and prints their exit codes.

Exit codes: 0 accepted; 1 the command refused or the judge could not run; 2 rejected.
"""
import argparse
import base64
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import time
import uuid

from canon import STATEMENT_KINDS, Canon, CanonError, axiom_closure, copy_tree, module_file, wait_build
from runtime_support import read_json, write_json, write_text

LAUNCHER = 'DoMathJudge'
ROOT_MODULE = 'DoMathJudgeRoot'
ROOT_NAME = ROOT_MODULE + '.statement'
MARK = '@@judge '
PLAN_MARK = '-- plan: '
# The comparator asks every export for the constants the kernel treats specially, and for the quotient
# constants when Quot.sound is permitted (Lake/CLI/Check.lean of Lean 4.36.0, primitiveTargets and
# builtinTargets). The exporter writes only what it is asked for, so they are named with every export.
PRIMITIVES = ('Nat.add', 'Nat.sub', 'Nat.mul', 'Nat.pow', 'Nat.gcd', 'Nat.div', 'Nat.mod', 'Nat.beq', 'Nat.ble',
              'Nat.land', 'Nat.lor', 'Nat.xor', 'Nat.shiftLeft', 'Nat.shiftRight', 'String.ofList', 'Char.ofNat',
              'List', 'eagerReduce', 'Nat', 'String', 'String.mk', 'Char', 'optParam', 'autoParam', 'semiOutParam',
              'outParam')
QUOTIENT = ('Quot', 'Quot.mk', 'Quot.lift', 'Quot.ind')
# Windows limits a command line to 32,767 characters; the names of one export stay well below it.
ARGUMENT_BUDGET = 20000
MISSING = re.compile(r"Const not found in (?:challenge|solution):? ?'([^']+)'")


class Stop(Exception):
    """The command cannot go on; the message says why."""


# ----------------------------------------------------------------------------- which commands judge

def judge_commands(lean):
    """({'export': argv, 'compare': argv}, None) for the judge of these Lean settings, or (None, why there is none).

    `lean.judge` is "auto", null, or the two commands. With "auto" the exporter and Lake are looked for
    beside the Lean command, where a Lean installation of version 4.35 or later has them. The sandbox of
    `lake comparator` needs Linux namespaces through bubblewrap; where it cannot run, the commands
    carry the option that switches it off, and the builds of the canon are then trusted as they are."""
    choice = lean.get('judge', 'auto')
    if choice is None:
        return None, 'lean.judge is null in the settings'
    if isinstance(choice, dict):
        return {'export': list(choice['export']), 'compare': list(choice['compare'])}, None
    first = lean['command'][0]
    folder = Path(first).parent if ('/' in first or os.sep in first) else None

    def tool(name):
        if folder is None:
            return shutil.which(name)
        for candidate in (folder / name, folder / (name + '.exe')):
            if candidate.is_file():
                return candidate.as_posix()
        return None

    exporter, lake = tool('leanexport'), tool('lake')
    if not exporter or not lake:
        return None, ('no leanexport and lake were found beside the Lean command; they come with Lean 4.35 and '
                      'later, and lean.judge can name them')
    compare = [lake, 'comparator']
    if os.name == 'nt' or not shutil.which(os.environ.get('COMPARATOR_BWRAP') or 'bwrap'):
        compare.append('--inadvisably-no-sandbox')
    return {'export': [exporter], 'compare': compare}, None


# ----------------------------------------------------------------------------- what is judged

def formal_names(index, allowed):
    """The theorems of the index that are proved in Lean from the allowed axioms."""
    closure, allowed = axiom_closure(index), set(allowed)
    return sorted(name for name, entry in index['entries'].items()
                  if entry['kind'] in STATEMENT_KINDS and set(closure[name]) <= allowed)


def publication_targets(old, new, touched, allowed):
    """The theorems a publication has judged: formal after it, and either given a proof by it or formal only now.

    A theorem whose own proof the change adds or replaces is judged for that proof. A theorem that the
    change did not touch becomes formal when the last statement it rests on does; it is judged then,
    because the export follows everything it rests on, whichever publication brought each part."""
    before, after, touched = set(formal_names(old, allowed)), formal_names(new, allowed), set(touched)
    return [name for name in after if name in touched or name not in before]


def carried(index, touched):
    """The record of earlier judgments that still holds after a change: of theorems it left as they were."""
    return {name: revision for name, revision in index.get('judged', {}).items()
            if name in index['entries'] and name not in touched}


def export_targets(names, allowed):
    quotient = QUOTIENT if 'Quot.sound' in allowed else ()
    return list(dict.fromkeys([*quotient, *names, *allowed, *PRIMITIVES]))


def batches(names, module_of, allowed):
    """(modules, names) groups whose export command stays within the length a command line may have."""
    fixed = sum(len(name) + 1 for name in export_targets([], allowed))
    group, size = [], fixed
    for name in names:
        cost = len(name) + 1 + len(module_of[name]) + 1
        if group and size + cost > ARGUMENT_BUDGET:
            yield sorted({module_of[n] for n in group}), group
            group, size = [], fixed
        group.append(name)
        size += cost
    if group:
        yield sorted({module_of[n] for n in group}), group


# ----------------------------------------------------------------------------- the job

def lean_string(text):
    pieces = []
    for character in text:
        if character in '\\"':
            pieces.append('\\' + character)
        elif character == '\n':
            pieces.append('\\n')
        elif character == '\r':
            pieces.append('\\r')
        elif character == '\t':
            pieces.append('\\t')
        elif ord(character) < 32:
            pieces.append('\\x%02x' % ord(character))
        else:
            pieces.append(character)
    return '"' + ''.join(pieces) + '"'


def lean_array(items):
    return '#[' + ', '.join(lean_string(item) for item in items) + ']'


def launcher_source(plan):
    """A Lean file without imports that runs the commands of the plan and prints each exit code.

    It is compiled by the broker like any single file, so the processes it starts are measured and
    ended with the job. The plan is repeated in a comment for a reader of the job's folder."""
    encoded = base64.b64encode(json.dumps(plan).encode('utf-8')).decode('ascii')
    lines = ['-- Written by do-math: this file starts the judge and prints exit codes. It states no mathematics.',
             PLAN_MARK + encoded, '', 'namespace ' + LAUNCHER, '',
             'partial def pump (source target : IO.FS.Handle) : IO Unit := do',
             '  let chunk ← source.read 65536',
             '  if chunk.isEmpty then',
             '    pure ()',
             '  else',
             '    target.write chunk',
             '    pump source target', '',
             'def exportTo (cmd : String) (args : Array String) (lib file : String) : IO UInt32 := do',
             '  let inherited := (← IO.getEnv "LEAN_PATH").getD ""',
             '  let separator := if System.Platform.isWindows then ";" else ":"',
             '  let path := if inherited.isEmpty then lib else lib ++ separator ++ inherited',
             '  let child ← IO.Process.spawn {',
             '    cmd := cmd, args := args, env := #[("LEAN_PATH", some path)],',
             '    stdin := .null, stdout := .piped, stderr := .inherit }',
             '  let target ← IO.FS.Handle.mk file .write',
             '  pump child.stdout target',
             '  target.flush',
             '  child.wait', '',
             'def compare (cmd : String) (args : Array String) (log : String) : IO UInt32 := do',
             '  let result ← IO.Process.output { cmd := cmd, args := args, stdin := .null }',
             '  IO.FS.writeFile log (result.stdout ++ result.stderr)',
             '  pure result.exitCode', '',
             'end ' + LAUNCHER, '', '#eval show IO Unit from do']
    for number, case in enumerate(plan['cases']):
        codes = []
        for position, item in enumerate(case['exports']):
            code = f'e{number}x{position}'
            codes.append(code)
            lines += [f'  let {code} ← {LAUNCHER}.exportTo {lean_string(item["command"][0])} '
                      f'{lean_array(item["command"][1:] + item["args"])} {lean_string(item["lib"])} {lean_string(item["file"])}',
                      f'  IO.println s!"{MARK}{number} export {position} {{{code}}}"']
        compare = case['compare']
        lines += ['  if ' + ' && '.join(code + ' == 0' for code in codes) + ' then',
                  f'    let c{number} ← {LAUNCHER}.compare {lean_string(compare["command"][0])} '
                  f'{lean_array(compare["command"][1:] + compare["args"])} {lean_string(compare["log"])}',
                  f'    IO.println s!"{MARK}{number} compare {{c{number}}}"']
    lines += [f'  IO.println "{MARK}done"', '']
    return '\n'.join(lines)


def start(instance, folder, cases, commands, allowed, expect_mb, session):
    """Queue the judge for the cases and return the job. A case names theorems and where their compiled modules are.

    Each case is {'names', 'solution': {'lib', 'modules'}} and, when the theorems are compared with another
    build of them, 'challenge' of the same form. Without it the export is compared with itself."""
    from lean_broker import Paths, submit
    folder = Path(folder)
    folder.mkdir(parents=True, exist_ok=True)
    plan = {'cases': []}
    for number, case in enumerate(cases):
        exports = []
        for side in ('challenge', 'solution'):
            if case.get(side):
                exports.append({'command': commands['export'], 'lib': Path(case[side]['lib']).as_posix(),
                                'args': [*case[side]['modules'], '--', *export_targets(case['names'], allowed)],
                                'file': (folder / f'case-{number}.{side}.ndjson').as_posix()})
        config = folder / f'case-{number}.json'
        write_json(config, {'challenge_module': (case.get('challenge') or case['solution'])['modules'][0],
                            'solution_module': case['solution']['modules'][0],
                            'theorem_names': case['names'], 'permitted_axioms': list(allowed)})
        plan['cases'].append({'names': case['names'], 'exports': exports, 'compare': {
            'command': commands['compare'], 'log': (folder / f'case-{number}.log').as_posix(),
            'args': ['--config', config.as_posix(), '--challenge-from-export', exports[0]['file'],
                     '--solution-from-export', exports[-1]['file']]}})
    write_json(folder / 'plan.json', plan)
    source = folder / (LAUNCHER + '.lean')
    write_text(source, launcher_source(plan))
    return submit(Paths(instance), source, int(expect_mb), session)['job']


def outcome(instance, job, folder):
    """None while the job runs; afterwards the verdict, 'accepted', 'rejected' or 'unavailable', and its reason.

    'rejected' is the judge's answer about the theorems: a statement that differs, an axiom that is not
    permitted, or a declaration a kernel does not accept. 'unavailable' means that no answer was
    obtained: a tool did not start, an export failed, or the job ended early. It says nothing about the
    theorems, and the caller must not treat it as a rejection."""
    from lean_broker import FINISHED, Paths, job_record
    paths, folder = Paths(instance), Path(folder)
    record = job_record(paths, job)
    if record is None:
        raise CanonError('unknown judge job: ' + job)
    if record['status'] == 'duplicate':
        return outcome(instance, record['duplicate_of'], folder)
    if record['status'] not in FINISHED:
        return None

    def read(path):
        return path.read_text(encoding='utf-8', errors='replace') if path.is_file() else ''

    plan = read_json(folder / 'plan.json')
    printed, errors = read(paths.job(record['id']) / 'stdout.log'), read(paths.job(record['id']) / 'stderr.log')
    exports, compares, done = {}, {}, False
    for line in printed.splitlines():
        parts = line[len(MARK):].split() if line.startswith(MARK) else []
        if parts == ['done']:
            done = True
        elif len(parts) == 4 and parts[1] == 'export':
            exports[(int(parts[0]), int(parts[2]))] = int(parts[3])
        elif len(parts) == 3 and parts[1] == 'compare':
            compares[int(parts[0])] = int(parts[2])
    cases = []
    for number, case in enumerate(plan['cases']):
        log = '\n'.join(line for line in read(Path(case['compare']['log'])).splitlines()
                        if not line.startswith('WARNING: Sandbox disabled')).strip()
        failed = [f'the exporter ended with code {exports.get((number, position))}'
                  for position in range(len(case['exports'])) if exports.get((number, position)) != 0]
        missing = MISSING.search(log)
        if failed:
            verdict, reason = 'unavailable', '; '.join(failed)
        elif compares.get(number) == 0:
            verdict, reason = 'accepted', ''
        elif compares.get(number) == 1 and not (missing and missing[1] not in case['names']):
            verdict, reason = 'rejected', log
        else:
            verdict, reason = 'unavailable', log or f'the comparator ended with code {compares.get(number)}'
        cases.append({'names': case['names'], 'verdict': verdict, 'reason': reason})
    if record['status'] != 'finished' or record.get('exit_code') != 0 or not done:
        tail = (printed + errors).strip()[-3000:]
        return {'verdict': 'unavailable', 'cases': cases, 'job': record['id'],
                'reason': f"the judge's job ended as {record['status']} with code {record.get('exit_code')}"
                          + (f" ({record['reason']})" if record.get('reason') else '') + (': ' + tail if tail else '')}
    for verdict in ('rejected', 'unavailable', 'accepted'):
        chosen = [case for case in cases if case['verdict'] == verdict]
        if chosen:
            reason = '; '.join(f"{', '.join(case['names'][:3])}{' and others' if len(case['names']) > 3 else ''}: "
                               f"{case['reason']}" for case in chosen if case['reason'])
            return {'verdict': verdict, 'cases': cases, 'job': record['id'],
                    'reason': reason + ('\n' + errors.strip()[-2000:] if verdict == 'unavailable' and errors.strip() else '')}
    return {'verdict': 'accepted', 'cases': cases, 'job': record['id'], 'reason': ''}


def wait(instance, job, folder, timeout=None):
    """The outcome of a judge job, or None when the timeout passes first; the job continues either way.

    The waiting is the broker client's (`lean_broker.await_record`), as for a build."""
    from lean_broker import Paths, await_record
    result = outcome(instance, job, folder)
    if result is not None:
        return result
    _, _, ended = await_record(Paths(instance), job, timeout)
    return outcome(instance, job, folder) if ended else None


def build_lib(instance, build):
    """The folder in which a finished build of the broker keeps its compiled modules."""
    from lean_broker import Paths
    return Paths(instance).build(build) / 'lib'


def judge_index(instance, folder, index, names, lib, commands, allowed, expect_mb, session):
    """Queue the judging of theorems of an index against their own export; returns the job."""
    module_of = {name: index['entries'][name]['module'] for name in names}
    cases = [{'names': group, 'solution': {'lib': lib, 'modules': modules}}
             for modules, group in batches(names, module_of, allowed)]
    return start(instance, folder, cases, commands, allowed, expect_mb, session)


# ----------------------------------------------------------------------------- the root of a finished instance

def settling(model):
    """(kind, declaration) of the formal proof that settles the root: 'proved' or 'refuted'."""
    from knowledge import refuting_proofs
    elements, root = model['elements'], model['root']
    if model['root_state'] == 'formal_proved':
        proofs = [p for p in elements[root]['proofs'] if elements[p]['settled'] and elements[p]['formal']]
        return 'proved', sorted(proofs, key=lambda name: (name != root, name))[0]
    if model['root_state'] == 'formal_refuted':
        return 'refuted', sorted(refuting_proofs(model, elements[root]['statement_of'], formal=True))[0]
    raise Stop(f"the root is {model['root_state']}; the judge is for a root that is formally proved or refuted")


def wrapper(root, root_module, kind, proof=None, proof_module=None):
    """A module with one theorem whose statement is the root's, or its negation, and whose proof is the one named.

    The challenge and the solution each get one, under the same name, because the comparator looks a
    theorem up by its name. `type_of%` takes the statement from the root's declaration as that build
    elaborated it, so no statement is copied by hand. Without a proof it stands on the open root."""
    statement = f'type_of% @{root}'
    if kind == 'refuted':
        statement = f'¬ ({statement})'
    value = f'@{proof}' if proof else (f'@{root}' if kind == 'proved' else 'sorry')
    imports = [root_module] + ([proof_module] if proof_module and proof_module != root_module else [])
    return ''.join(f'import {module}\n' for module in imports) + f'\ntheorem {ROOT_NAME} : {statement} := {value}\n'


def first_commit(instance):
    result = subprocess.run(['git', '-C', str(instance), 'rev-list', '--max-parents=0', 'HEAD'],
                            capture_output=True, text=True, check=True)
    return result.stdout.split()[0]


def checkout(instance, commit, target):
    """The Lean sources of the canon as a commit of the instance has them."""
    listed = subprocess.run(['git', '-C', str(instance), 'ls-tree', '-r', '--name-only', commit, '--', 'canon/lean'],
                            capture_output=True, text=True, check=True, encoding='utf-8').stdout.split('\n')
    for path in filter(None, listed):
        data = subprocess.run(['git', '-C', str(instance), 'show', f'{commit}:{path}'], capture_output=True, check=True).stdout
        file = Path(target) / Path(path).relative_to('canon/lean')
        file.parent.mkdir(parents=True, exist_ok=True)
        file.write_bytes(data)


def judge_root(instance, out, paranoid=True, timeout=None, review=True):
    """Judge the settled root against the root of the first commit; returns the exit code."""
    from knowledge import replay
    from lean_broker import Paths, build
    from settings import load_settings
    instance, out = Path(instance).resolve(), Path(out).resolve()
    if out.exists() and any(out.iterdir()):
        raise Stop(f'{out} is not empty; give a new folder to --out')
    model = replay(instance)
    kind, proof = settling(model)
    lean = load_settings(instance)['lean']
    commands, why = judge_commands(lean)
    if commands is None:
        raise Stop('no judge is available: ' + why)
    if paranoid:
        commands = {**commands, 'compare': commands['compare'] + ['--paranoid']}
    canon, root = Canon(instance), model['root']
    index = canon.load_index()['entries']
    commit = first_commit(instance)
    out.mkdir(parents=True, exist_ok=True)
    checkout(instance, commit, out / 'challenge')
    copy_tree(canon.lean, out / 'solution')
    root_module = index[root]['module']
    if not (out / 'challenge' / module_file(root_module)).is_file():
        raise Stop(f'the first commit of the instance has no module {root_module}; the root has to stand where it was fixed')
    write_text(out / 'challenge' / (ROOT_MODULE + '.lean'), wrapper(root, root_module, kind))
    write_text(out / 'solution' / (ROOT_MODULE + '.lean'),
               wrapper(root, root_module, kind, proof, index[proof]['module']))
    paths, libs = Paths(instance), {}
    for side in ('challenge', 'solution'):
        started = build(paths, out / side, [out / side / (ROOT_MODULE + '.lean')], lean['calibration_expect_mb'], 'operator')
        result = wait_build(instance, started['build'], timeout)
        if result is None:
            raise Stop(f'the build of the {side} did not finish within the timeout; it continues as {started["build"]}')
        if not result['ok']:
            raise Stop(f'the {side} does not build: ' + '; '.join(
                f"{e['module'] or 'build'}: {e['status']} {e.get('reason') or ''} {e['output']}" for e in result['errors']))
        libs[side] = build_lib(instance, result['build'])
    case = {'names': [ROOT_NAME], 'challenge': {'lib': libs['challenge'], 'modules': [ROOT_MODULE]},
            'solution': {'lib': libs['solution'], 'modules': [ROOT_MODULE]}}
    job = start(instance, out / 'judge', [case], commands, lean['allowed_axioms'], lean['calibration_expect_mb'], 'operator')
    result = wait(instance, job, out / 'judge', timeout)
    if result is None:
        raise Stop(f'the judge did not finish within the timeout; it continues as {job}')
    verdict = {'verdict': result['verdict'], 'reason': result['reason'], 'root': root, 'root_state': model['root_state'],
               'proof': proof, 'compared_with_commit': commit, 'permitted_axioms': lean['allowed_axioms'],
               'commands': commands, 'job': result['job']}
    if result['verdict'] == 'rejected' and review:
        request = instance / 'control/requests' / ('request' + uuid.uuid4().hex + '.json')
        write_json(request, {'kind': 'review', 'elements': [proof], 'concerns': [],
                             'reason': 'The judge rejected the formal settlement of the root: ' + result['reason']})
        verdict['review_request'] = str(request)
    write_json(out / 'verdict.json', verdict)
    print(json.dumps({key: verdict[key] for key in ('verdict', 'root', 'root_state', 'proof', 'reason')}, indent=2))
    if result['verdict'] == 'accepted':
        print(f'The root is {kind} by {proof}: the statement and what it depends on are those of the first commit, '
              'the axioms are within the allowed list, and every kernel that ran accepts the proof.')
    elif result['verdict'] == 'rejected':
        print('The judge rejected the settlement.' + (' A comprehensive review of the proof is requested; start the '
              'runner to have it made.' if review else ''))
    else:
        print('The judge could not run to a verdict. This says nothing about the proof.')
    print(f'The record is {out / "verdict.json"}.')
    return {'accepted': 0, 'rejected': 2, 'unavailable': 1}[result['verdict']]


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('instance', type=Path)
    parser.add_argument('--out', type=Path, required=True, help='the folder that receives the builds and the verdict; new or empty')
    parser.add_argument('--no-paranoid', action='store_true', help="use Lean's own kernel only")
    parser.add_argument('--no-review', action='store_true', help='do not request a review when the judge rejects')
    parser.add_argument('--timeout', type=float, help='seconds to wait for each build and for the judge')
    args = parser.parse_args(argv)
    try:
        return judge_root(args.instance, args.out, not args.no_paranoid, args.timeout, not args.no_review)
    except (Stop, CanonError, OSError, ValueError, subprocess.CalledProcessError) as exc:
        print('judge.py: ' + str(exc), file=sys.stderr)
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
