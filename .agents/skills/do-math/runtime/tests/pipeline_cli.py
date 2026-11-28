"""Scripted session outputs for testing the real orchestration and publication path.

The scripted research is small and real: the sum of the first n odd numbers is n * n. The Lean it
writes is written as valid Lean 4, so the script can also be run against Lean itself in place of the
stand-in compiler; test_pipeline, the only test that uses it, runs it against the stand-in."""
import contextlib
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import time

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from canon_tool import prepare, verify
from coordination import lease, section
from runtime_support import read_json, write_json

session = Path.cwd()
inp = read_json(session / 'input.json')
role, task = inp['role'], inp['task']
instance = Path(inp['instance'])
output = session / 'output'
print(json.dumps({'type': 'item.completed', 'item': {'type': 'agent_message', 'text': 'Scripted test activity.'}}), flush=True)

STEP = '''module

public import Small.Defs

@[expose] public section

namespace Small

/-- Adding the next odd number. -/
theorem oddSum_succ (n : Nat) : oddSum (n + 1) = oddSum n + (2 * n + 1) := by
  rfl

end Small
'''
INFORMAL = '''/-- The sum of the first `n` odd numbers is the square of `n`. -/
theorem root (n : Nat) : oddSum n = n * n := by
  have step := oddSum_succ
  sorry'''
FORMAL = '''/-- The sum of the first `n` odd numbers is the square of `n`. -/
theorem root (n : Nat) : oddSum n = n * n := by
  induction n with
  | zero => rfl
  | succ k ih =>
    rw [oddSum_succ, ih]
    simp only [Nat.add_mul, Nat.mul_add, Nat.mul_one, Nat.one_mul]
    omega'''
ROOT_RECORD = '''---
short: sum of odd numbers
weight: unit
---
## Description

The sum of the first n odd numbers equals n times n.

## Statement

For every natural number $n$, $1 + 3 + \\dots + (2n - 1) = n^2$.

## Proof

By induction on $n$. The case $n = 0$ is the empty sum. If the sum of the first $k$ odd numbers is $k^2$,
adding the next one, $2k + 1$, gives $k^2 + 2k + 1 = (k + 1)^2$; the step uses `Small.oddSum_succ`.
'''
STEP_RECORD = '''---
short: next odd number
weight: step
---
## Description

Passing from n to n + 1 adds the odd number 2n + 1 to the sum.

## Statement

For every natural number $n$, the sum of the first $n + 1$ odd numbers is the sum of the first $n$ plus $2n + 1$.
'''
APPROACH = '''---
title: Induction on the number of terms
sessions: {sessions}
---
## Idea

Compare the sum for n + 1 with the sum for n.

## Established

Small.oddSum_succ

## Where it stops

The inductive step is stated; the arithmetic identity has not been checked in Lean.
'''


def write(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding='utf-8', newline='\n')


STEP_LINE = 'The passage from n terms of the sum of odd numbers to n + 1 terms, the step of an induction on it.\n'
STEP_PURPOSE = 'how the sum of the first odd numbers changes when one more odd number is added'


def descent_tested():
    """Take the blind descent test on the descriptions of the output folder, by the command a session has.

    The command is `commands.canon` of input.json with `descent-test` as its command. It starts the test in
    a process of its own and says with exit code 124 that the test continues, and the same command, given
    again, finds it; with 0 every purpose passed or its reader could not be had, and the receipt
    descriptions/tests.json is written. The reader is a light session on the CLI that the instance's
    settings name as the Claude CLI, which in test_pipeline is the stand-in tests/light_cli.py."""
    command = ['descent-test' if part == '<command>' else part for part in inp['commands']['canon']]
    # No compiled file is left beside the programs, which stand in the skill folder that the test reads.
    environment = {**os.environ, 'PYTHONDONTWRITEBYTECODE': '1'}
    deadline = time.monotonic() + 240
    while True:
        done = subprocess.run(command, capture_output=True, text=True, encoding='utf-8', env=environment)
        if done.returncode != 124 or time.monotonic() > deadline:
            break
    if done.returncode:
        raise RuntimeError(f'scripted blind descent test ended with exit code {done.returncode}: '
                           + done.stdout + done.stderr)


def built(command):
    """Build as a session does, by the function behind its command, which writes the receipt itself.

    The command prints a summary for the session; it is kept out of the stream that the host reads."""
    with contextlib.redirect_stdout(io.StringIO()) as summary:
        code = command(session, 64, None)
    if code:
        raise RuntimeError('scripted candidate did not build: ' + summary.getvalue())


if role in ('attempt', 'explore', 'formalizer'):
    if role == 'attempt':
        lease(session, 'Small.root')
        write(session / 'work/section.json', json.dumps({'whole': True}))
        if not section(session, 'Small.root', session / 'work/section.json')['registered']:
            raise RuntimeError('scripted attempt could not register the whole root')
    write(output / 'report.md', 'The sum of the first n odd numbers is n * n, by induction through Small.oddSum_succ.')
    if role == 'formalizer':
        write(output / 'root.lean', FORMAL)
elif role == 'peer':
    source_role = task['source_role']
    change = {'title': 'The sum of the first odd numbers', 'description': 'An induction that proves the root.',
              'replace': [], 'questions': [], 'resolutions': []}
    if source_role == 'attempt':
        write(output / 'lean/Small/Step.lean', STEP)
        write(output / 'replace/root.lean', INFORMAL)
        change['replace'] = [{'declaration': 'Small.root', 'file': 'replace/root.lean', 'imports': ['Small.Step']}]
        write(output / 'records/Small/root.md', ROOT_RECORD)
        write(output / 'records/Small/oddSum_succ.md', STEP_RECORD)
        write(output / 'approaches/Small/root/induction.md', APPROACH.format(sessions=Path(task['source']).name))
        # The candidate adds the module Small.Step, so it carries the line of that module, a purpose drawn
        # from what the module holds, and, before it is prepared, the receipt of the blind descent test.
        write(output / 'descriptions/modules/Small/Step.md', STEP_LINE)
        write_json(output / 'descriptions/purposes.json', [{'target': 'Small.Step', 'purpose': STEP_PURPOSE}])
    elif source_role == 'formalizer':
        write(output / 'replace/root.lean', FORMAL)
        change.update(title='The root proved in Lean', description='The induction written as a Lean proof.',
                      replace=[{'declaration': 'Small.root', 'file': 'replace/root.lean'}])
    else:
        question = task.get('question')
        change.update(title='What the sum of odd numbers shows', description='An account of the root problem as a whole.')
        if question:
            write(output / 'questions' / (question + '.md'),
                  'The sum grows by one odd number at a time, and each step completes a square. '
                  'The elements `Small.oddSum` and `Small.root` carry the exact statements.\n')
        if question == 'q0':
            # An exploration of the whole problem leaves a question that later explorers can take up.
            change['questions'] = [{'id': session.name + '-squares',
                                    'statement': 'Why does adding consecutive odd numbers complete a square at every step?',
                                    'grounds': 'The scripted proof uses the identity without saying what it shows.'}]
    write_json(output / 'change.json', change)
    if (output / 'descriptions').is_dir():
        descent_tested()
    built(prepare)
elif role == 'review':
    # The scripted reviews raise no concern and the scripted research contests nothing, so the runner assigns
    # no comprehensive review: every review here is the review of a candidate.
    write(output / 'feedback.md', 'The precise argument was assessed.')
    candidate = Path(task['candidate'])
    change = read_json(candidate / 'change.json')
    receipt = read_json(candidate / 'prepared.json')
    assessment = {'publish': True, 'reason': 'Useful retained mathematics.',
                  'contribution': 'Closed the step it took on within its exact scope.', 'feedback': 'feedback.md',
                  'elements': [], 'concerns': [], 'findings': [],
                  'questions': [{'proposal': q['id'], 'verdict': 'admitted', 'reason': 'A question later explorers can take up.'}
                                for q in change['questions']],
                  'resolutions': []}
    formal = False
    for name in receipt['added'] + receipt['replaced']:
        entry = receipt['entries'][name]
        proved = entry['kind'] == 'theorem' and (entry['lean_proof'] == 'complete' or entry['written_proof'])
        formal = formal or (proved and entry['lean_proof'] == 'complete')
        verdict = {'element': name, 'correct': 'confirmed' if proved else 'not_applicable',
                   'accepted': proved, 'reason': 'The argument was followed step by step.'}
        if name in receipt['replaced']:
            verdict['replaces'] = True
        assessment['elements'].append(verdict)
    if formal:
        built(verify)
        assessment['formal_check'] = {'build': read_json(session / 'work/verify/outcome.json')['build']}
    write_json(output / 'assessment.json', assessment)
elif role == 'organizer':
    write_json(output / 'organization.json', {'batch': task['batch'], 'merge_questions': []})
