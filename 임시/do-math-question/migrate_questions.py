"""One-time migration of a running do-math instance to the question-aware runtime.

This script is not part of the do-math runtime. It runs once, with the runner stopped, on an
instance that was created and operated by the runtime before questions existed, and leaves the
instance in the form the new runtime expects. The runtime itself knows only that form.

What it changes:
  1. settings.json           explore_every becomes 1 (the new default cadence).
  2. runner/state.json       an exploration pipeline still in progress (stage other than done) is
                             recorded as occupying question q0: the producer session receives a
                             declaration.json with that question, or, if the producer has not been
                             launched yet, the pending job's task names the question.
  3. control/inputs/         the operator input named by --retire-input (by default the
                             2026-11-07 note on section registration timing) moves to
                             control/retired-inputs/ so that later launches no longer receive it.
  4. knowledge/              the questions in the --questions file are published as an operator
                             questions event (knowledge/events/<id>.json plus
                             knowledge/questions/<id>/questions.json), which the runtime replays
                             onto the frontier as open questions with origin "operator".
  5. knowledge views         frontier.md, board.md and state.json are rendered again so that the
                             copy can be inspected; the runner renders them again at start anyway.

It then checks the invariants the new runtime relies on and prints a report of what changed.

Usage:
  python migrate_questions.py <instance> [--questions FILE] [--runtime DIR] [--retire-input NAME]
                              [--dry-run] [--commit] [--report FILE]

  --questions FILE   JSON file with the initial question list; see QUESTIONS_FORMAT below. Optional:
                     without it only q0 exists after migration.
  --runtime DIR      the do-math runtime directory to import (default: the canonical installation).
                     Use the directory the runner will actually run from.
  --retire-input     file name under control/inputs/ to move out (default: the known note).
  --dry-run          report what would change without writing anything.
  --commit           commit the new knowledge files in the instance's own Git repository. Without
                     it they stay uncommitted; the runner adds all of knowledge/ at its next
                     publication, so this is optional.
  --report FILE      also write the JSON report to FILE.

Order of operations for the live instance:
  stop the runner (runner.py stop; wait for the runner process to exit, or kill it after STOP so
  that no session is launched during the migration; session hosts and CLIs may keep running),
  then run this script on the instance, then regenerate the installed copy the instance uses
  (.agents/skills/do-math) from the canonical skill, then start the runner again (runner.py start)
  and resume (runner.py resume) if STOP was left in place.

The script refuses to run while the runner's instance lock is held, so it cannot change state
underneath a live runner. Session hosts do not hold that lock and are not disturbed.
"""
import argparse
import json
from pathlib import Path
import re
import shutil
import sys
import time
import uuid

DEFAULT_RUNTIME = Path('C:/math/.claude/skills/do-math/runtime')
DEFAULT_RETIRED_INPUT = '1794056547459557300-f256a90481e544ac926d43a63825f043.txt'
IDENTIFIER = re.compile(r'[A-Za-z0-9][A-Za-z0-9_-]*')

QUESTIONS_FORMAT = """
The --questions file is UTF-8 JSON of this form:

{
  "reason": "Why the operator places these questions on the frontier; recorded in the publication.",
  "questions": [
    {
      "id": "op-critical-scale",
      "statement": "What is to be understood, stated so an explorer can take it up and a reviewer can tell whether an account answers it.",
      "grounds": "What in the published research raises the question and why an answer matters; conjectural grounds are allowed and should be marked as such."
    }
  ]
}

Each id matches [A-Za-z0-9][A-Za-z0-9_-]*, is unique in the file, is not q0, and does not name an
existing question, question alias, node or node alias. A prefix such as op- keeps operator questions
recognizable beside peer proposals, which carry a session-ID prefix. statement and grounds are
nonempty text. The list may be empty, in which case no publication is written.
"""


def fail(message):
    print(json.dumps({'error': message}, ensure_ascii=False), file=sys.stderr)
    raise SystemExit(1)


def load_runtime(directory):
    directory = Path(directory).resolve()
    for name in ('runner.py', 'knowledge.py', 'coordination.py', 'settings.py', 'runtime_support.py'):
        if not (directory / name).is_file():
            fail(f'runtime directory lacks {name}: {directory}')
    sys.path.insert(0, str(directory))
    import knowledge, coordination, settings, runtime_support, runner  # noqa: E402
    if not hasattr(knowledge, 'ROOT_QUESTION') or not hasattr(coordination, 'question_availability'):
        fail('the runtime at ' + str(directory) + ' does not know questions; point --runtime at the new runtime')
    return {'knowledge': knowledge, 'coordination': coordination, 'settings': settings,
            'support': runtime_support, 'runner': runner}


def read_questions_file(path, model, knowledge):
    data = json.loads(Path(path).read_text(encoding='utf-8-sig'))
    if not isinstance(data, dict) or not isinstance(data.get('questions'), list):
        fail('questions file must be an object with a "questions" array' + QUESTIONS_FORMAT)
    reason = data.get('reason', '')
    if not isinstance(reason, str) or not reason.strip():
        fail('questions file needs a nonempty "reason"' + QUESTIONS_FORMAT)
    taken = set(model['questions']) | set(model['question_aliases']) | set(model['nodes']) | set(model['aliases'])
    seen = set()
    for item in data['questions']:
        if not isinstance(item, dict):
            fail('each question must be an object' + QUESTIONS_FORMAT)
        qid = item.get('id')
        if not isinstance(qid, str) or not IDENTIFIER.fullmatch(qid):
            fail(f'invalid question id: {qid!r}' + QUESTIONS_FORMAT)
        if qid == knowledge.ROOT_QUESTION:
            fail('q0 is created by the runtime and cannot be listed')
        if qid in seen:
            fail('duplicate question id: ' + qid)
        if qid in taken:
            fail('question id already names a question or node in this instance: ' + qid)
        for key in ('statement', 'grounds'):
            if not isinstance(item.get(key), str) or not item[key].strip():
                fail(f'question {qid} needs nonempty {key}' + QUESTIONS_FORMAT)
        seen.add(qid)
    return reason, [{'id': q['id'], 'statement': q['statement'], 'grounds': q['grounds']} for q in data['questions']]


def open_explorations(state):
    return [(pid, p) for pid, p in state['pipelines'].items() if p['role'] == 'explore' and p['stage'] != 'done']


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('instance', type=Path)
    parser.add_argument('--questions', type=Path)
    parser.add_argument('--runtime', type=Path, default=DEFAULT_RUNTIME)
    parser.add_argument('--retire-input', default=DEFAULT_RETIRED_INPUT)
    parser.add_argument('--dry-run', action='store_true')
    parser.add_argument('--commit', action='store_true')
    parser.add_argument('--report', type=Path)
    args = parser.parse_args(argv)
    instance = args.instance.resolve()
    modules = load_runtime(args.runtime)
    knowledge, coordination, settings_module, support, runner_module = (
        modules['knowledge'], modules['coordination'], modules['settings'], modules['support'], modules['runner'])
    read_json, write_json = support.read_json, support.write_json

    if not (instance / 'instance.json').is_file() or read_json(instance / 'instance.json').get('schema') != 1:
        fail('not a do-math instance: ' + str(instance))
    if not (instance / '.git').is_dir():
        fail('the instance has no Git repository; the runner requires one')
    report = {'instance': str(instance), 'dry_run': args.dry_run, 'runtime': str(Path(args.runtime).resolve()),
              'before': {}, 'changes': [], 'after': {}, 'checks': {}, 'warnings': []}

    try:
        lock = support.InstanceLock(instance / 'runner/lock')
        lock.__enter__()
    except RuntimeError:
        fail('the runner holds this instance; stop it and wait for it to exit before migrating')
    try:
        receipt_path = instance / 'runner/process.json'
        if receipt_path.is_file():
            receipt = read_json(receipt_path)
            if support.alive(receipt.get('process')):
                # The lock is free, so this process is a runner of another directory (a copy's
                # origin) or an unrelated process that reused the PID.
                report['warnings'].append('runner/process.json names a live process but the instance lock is free; '
                                          'this is expected on a copy of a running instance')

        # Before.
        settings = read_json(instance / 'settings.json')
        state = read_json(instance / 'runner/state.json')
        model = knowledge.replay(instance)
        explorations = open_explorations(state)
        report['before'] = {
            'explore_every': settings.get('explore_every'),
            'explore_requested': state.get('explore_requested'),
            'open_explorations': [{'pipeline': pid, 'stage': p['stage'], 'producer': p['producer']} for pid, p in explorations],
            'questions': sorted(model['questions']),
            'knowledge_sequence': model['sequence'],
            'retired_input_present': (instance / 'control/inputs' / args.retire_input).is_file(),
            'unknown_state_keys': sorted(set(state) - {
                'schema', 'sessions', 'pipelines', 'jobs', 'blocks', 'attempt_research_starts',
                'attempt_availability_epoch', 'attempt_dispatch_gate', 'explore_requested', 'complete',
                'processed_concerns', 'processed_conflicts', 'publication', 'seen_requests', 'last_error',
                'finished', 'last_attempt_launch', 'settings_error'}),
        }
        if len(explorations) > 1:
            fail('more than one exploration pipeline is in progress; the earlier runtime allowed one, '
                 'and only one can occupy q0. Resolve this by hand before migrating: ' + ', '.join(pid for pid, _ in explorations))

        questions = []
        reason = None
        if args.questions:
            reason, questions = read_questions_file(args.questions, model, knowledge)

        # 1. settings
        if settings.get('explore_every') != 1:
            new_settings = dict(settings)
            new_settings['explore_every'] = 1
            settings_module.validate(new_settings)
            report['changes'].append({'file': 'settings.json', 'explore_every': [settings.get('explore_every'), 1]})
            if not args.dry_run:
                write_json(instance / 'settings.json', new_settings)

        # 2. in-progress exploration occupies q0
        for pid, pipeline in explorations:
            sid = pipeline['producer']
            if sid:
                declaration = instance / 'sessions' / sid / 'declaration.json'
                data = read_json(declaration) if declaration.is_file() else {'at': time.time()}
                if data.get('question'):
                    report['changes'].append({'pipeline': pid, 'session': sid, 'question': data['question']['id'],
                                              'note': 'already declared; left unchanged'})
                    continue
                data['question'] = {'id': knowledge.ROOT_QUESTION, 'at': time.time(), 'by': 'runner',
                                    'note': 'assigned by the question migration to an exploration in progress'}
                report['changes'].append({'pipeline': pid, 'session': sid, 'file': str(declaration),
                                          'question': knowledge.ROOT_QUESTION})
                if not args.dry_run:
                    write_json(declaration, data)
            else:
                job = state['jobs'].get(pid + ':producer')
                if job is None:
                    fail('exploration pipeline without a producer job: ' + pid)
                job['task']['question'] = knowledge.ROOT_QUESTION
                report['changes'].append({'pipeline': pid, 'job': job['id'], 'task.question': knowledge.ROOT_QUESTION})
                if not args.dry_run:
                    write_json(instance / 'runner/state.json', state)

        # 3. retire the operator input
        source = instance / 'control/inputs' / args.retire_input
        if source.is_file():
            target_dir = instance / 'control/retired-inputs'
            target = target_dir / args.retire_input
            report['changes'].append({'moved': str(source), 'to': str(target)})
            if not args.dry_run:
                target_dir.mkdir(exist_ok=True)
                if target.exists():
                    fail('retired input already exists: ' + str(target))
                shutil.move(str(source), str(target))
        else:
            report['warnings'].append('retired input not present under control/inputs: ' + args.retire_input)

        # 4. operator questions publication
        if questions:
            eid = 'q' + uuid.uuid4().hex
            sequence = model['sequence'] + 1
            folder = instance / 'knowledge/questions' / eid
            event = {'id': eid, 'kind': 'questions', 'sequence': sequence, 'folder': 'questions/' + eid,
                     'at': time.time(), 'source': 'operator-migration'}
            publication = {'source': 'operator', 'reason': reason, 'questions': questions, 'at': time.time(),
                           'migration': 'do-math question introduction; placed by the operator, not through peer and review'}
            report['changes'].append({'event': eid, 'sequence': sequence, 'questions': [q['id'] for q in questions]})
            if not args.dry_run:
                folder.mkdir(parents=True)
                write_json(folder / 'questions.json', publication)
                write_json(instance / 'knowledge/events' / (eid + '.json'), event)

        # 5. views
        if not args.dry_run:
            state = read_json(instance / 'runner/state.json')
            model = knowledge.replay(instance)
            rows = coordination.board(instance, state, model)
            knowledge.render(instance, model, rows, coordination.lease_table(instance, state, model))
            report['changes'].append({'rendered': ['knowledge/frontier.md', 'knowledge/board.md', 'knowledge/state.json',
                                                   'knowledge/index.md', 'knowledge/glossary.md']})
            if args.commit:
                support.git(instance, 'add', '-A', '--', 'knowledge')
                if support.git(instance, 'status', '--porcelain', '--', 'knowledge'):
                    support.git(instance, 'commit', '-m', 'Introduce questions', '--', 'knowledge')
                    report['changes'].append({'git': 'committed knowledge/'})
            else:
                report['warnings'].append('knowledge/ changes are uncommitted; the runner commits all of knowledge/ '
                                          'at its next publication, or run with --commit')

        if args.dry_run:
            # Nothing was written; the invariant checks apply to the written state only.
            report['checks'] = {'dry_run': True, 'all_passed': None}
            report['after'] = {'note': 'dry run; run without --dry-run to migrate and check'}
            text = json.dumps(report, ensure_ascii=False, indent=2)
            print(text)
            if args.report:
                args.report.write_text(text + '\n', encoding='utf-8')
            return 0
        # Checks on the written state.
        settings = read_json(instance / 'settings.json')
        state = read_json(instance / 'runner/state.json')
        model = knowledge.replay(instance)
        rows = coordination.board(instance, state, model)
        availability = coordination.question_availability(instance, state, model, rows)
        held = {}
        for pid, pipeline in open_explorations(state):
            row = next(r for r in rows if r['pipeline'] == pid)
            held[pid] = row['question']
        checks = report['checks']
        checks['settings_valid'] = bool(settings_module.validate(settings))
        checks['explore_every_is_1'] = settings.get('explore_every') == 1
        checks['q0_present_and_open'] = model['questions'].get(knowledge.ROOT_QUESTION, {}).get('state') == 'open'
        checks['open_explorations_hold_a_question'] = all(held.values())
        checks['no_question_held_twice'] = len([q for q in held.values() if q]) == len({q for q in held.values() if q})
        checks['held_questions_open'] = all(model['questions'][q]['state'] == 'open' for q in held.values() if q)
        checks['operator_questions_open'] = all(model['questions'].get(q['id'], {}).get('state') == 'open' for q in questions)
        checks['retired_input_absent'] = not (instance / 'control/inputs' / args.retire_input).is_file()
        checks['state_keys_present'] = all(key in state for key in ('explore_requested', 'pipelines', 'jobs', 'sessions'))
        checks['frontier_lists_questions'] = ('# Questions' in (instance / 'knowledge/frontier.md').read_text(encoding='utf-8')
                                              if not args.dry_run else None)
        # The new runner must be able to read this state and reach a dispatch judgment.
        engine = runner_module.Runner(instance, Path(args.runtime).resolve().parent)
        checks['runner_loads_state'] = True
        report['after'] = {
            'explore_every': settings.get('explore_every'),
            'explore_requested': state.get('explore_requested'),
            'questions': {qid: q['state'] for qid, q in model['questions'].items()},
            'question_availability': availability,
            'open_explorations': held,
            'available_nodes': engine.available_nodes(),
            'question_slot': engine.question_slot(),
            'attempt_dispatch_ready': engine.attempt_dispatch_ready(),
            'knowledge_sequence': model['sequence'],
        }
        checks['all_passed'] = all(v is not False for v in checks.values())
    finally:
        lock.__exit__(None, None, None)

    text = json.dumps(report, ensure_ascii=False, indent=2)
    print(text)
    if args.report:
        args.report.write_text(text + '\n', encoding='utf-8')
    return 0 if report['checks'].get('all_passed') else 1


if __name__ == '__main__':
    raise SystemExit(main())
