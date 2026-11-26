"""The stand-ins that tests/test_finalize.py launches in place of the CLI of a session, of Lake and of the command that reports the version of Lean.

Run as `finalize_cli.py session <scenario folder>` it reads session.json in its working folder and writes
what `script.json` of the scenario gives for that kind of session: for the key `<kind>:<section>`,
or else `<kind>`, one entry for each session in turn and the last entry for every later one. An
entry maps a path under the session's folder to its text; the key `@copy` lists pairs of paths, each
a file or folder of the session copied to another place in it. Every call is recorded with the files
the session was given. Run as `finalize_cli.py lake ...` it is Lake: `build` succeeds unless
`lake.json` of the scenario names a text that Challenge.lean then holds; `env lean DoMathExtract.lean`
runs the stand-in compiler's extraction, after one more hypothesis was put behind the text of Challenge.lean
that `lake.json` names under `elaborates_otherwise`, as where Lean elaborates what that file prints to another
statement than the library's; `env lean Check.lean` prints an axioms line for every name
that Check.lean asks about, with the axioms that `lake.json` gives the name under `axioms` and no such
line for a name it gives null, and fails at a name that no module Check.lean imports declares; and every
call fails when `lake.json` names under `needs_variable` a variable that its environment does not have.
Run as `finalize_cli.py version` it is Lean's version command.
"""
import json
import os
from pathlib import Path
import re
import shutil
import sys
import time

THIS = Path(__file__).resolve()


def stand_in_session(scenario):
    folder = Path.cwd()
    task = json.loads((folder / 'session.json').read_text(encoding='utf-8'))
    sys.stdin.reconfigure(encoding='utf-8')  # the program hands over the bytes of a UTF-8 file, whatever the locale
    prompt = sys.stdin.read()
    script = json.loads((scenario / 'script.json').read_text(encoding='utf-8'))
    own = f"{task['kind']}:{task['section']}"
    key = next((k for k in (own, task['kind']) if k in script), None)
    given = sorted(p.relative_to(folder).as_posix() for p in folder.rglob('*')
                   if p.is_file() and not p.name.startswith(('cli.', 'worker-')))
    lock = scenario / 'calls.lock'
    while True:
        try:
            os.close(os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY))
            break
        except (FileExistsError, PermissionError):
            time.sleep(0.01)
    stopped = refused = failed = False
    try:
        record = scenario / 'calls.json'
        calls = json.loads(record.read_text(encoding='utf-8')) if record.exists() else []
        if key is not None:
            entries = script[key]
            entry = entries[min(sum(c['key'] == key for c in calls), len(entries) - 1)]
            # An entry `{'@stopped': ...}` stands for a session that a safeguard of the AI system stopped, an entry
            # `{'@refused': ...}` for one whose provider has no capacity for the model, and an entry `{'@failed': ...}`
            # for one whose CLI ended with an error that is neither, before the session wrote anything.
            stopped, refused, failed = '@stopped' in entry, '@refused' in entry, '@failed' in entry
            for source, target in entry.get('@copy', []):
                if (folder / source).is_dir():
                    shutil.copytree(folder / source, folder / target, dirs_exist_ok=True)
                else:
                    (folder / target).parent.mkdir(parents=True, exist_ok=True)
                    shutil.copyfile(folder / source, folder / target)
            for name, content in entry.items():
                if name not in ('@copy', '@stopped', '@refused', '@failed'):
                    (folder / name).parent.mkdir(parents=True, exist_ok=True)
                    (folder / name).write_text(content, encoding='utf-8', newline='\n')
        calls.append({'key': key, 'kind': task['kind'], 'section': task['section'], 'folder': folder.name,
                      'given': given, 'prompt': prompt, 'model': task.get('model')})
        record.write_text(json.dumps(calls), encoding='utf-8')
    finally:
        lock.unlink()
    if failed:
        # An error of the CLI that is no refusal of the provider, as when the connection to it is lost.
        print(json.dumps({'type': 'error', 'message': 'stream disconnected before completion'}))
        return 1
    if refused:
        # What the Codex CLI writes when the provider has no capacity for the model.
        print(json.dumps({'type': 'error', 'message': 'Selected model is at capacity'}))
        return 1
    if stopped:
        # What the Claude CLI writes when the model refuses a request and the CLI has no other model to give it to.
        message = "API Error: the model's safeguards flagged this message. Try rephrasing the request or change your model."
        print(json.dumps({'type': 'assistant', 'is_api_error_message': True, 'error': 'invalid_request',
                          'message': {'model': '<synthetic>', 'role': 'assistant', 'stop_reason': 'refusal',
                                      'content': [{'type': 'text', 'text': message}]}}))
        print(json.dumps({'type': 'result', 'subtype': 'success', 'is_error': True, 'stop_reason': 'refusal',
                          'terminal_reason': 'api_error', 'result': message}))
        return 1
    print(json.dumps({'type': 'item.completed', 'item': {'type': 'agent_message', 'text': 'Scripted session.'}}))
    return 0


def stand_in_lake(scenario, arguments):
    settings = json.loads((scenario / 'lake.json').read_text(encoding='utf-8')) if (scenario / 'lake.json').exists() else {}
    with (scenario / 'lake-calls.txt').open('a', encoding='utf-8') as stream:
        stream.write(' '.join(arguments) + '\n')
    needed = settings.get('needs_variable')
    if needed and not os.environ.get(needed):
        print(f'error: the stand-in for Lake was started without {needed} in its environment')
        return 1
    if arguments == ['build']:
        failing = settings.get('build_fails_when')
        if failing and failing in Path('Challenge.lean').read_text(encoding='utf-8'):
            print('error: Challenge.lean: the stand-in refuses this text')
            return 1
        manifest = json.loads(Path('lake-manifest.json').read_text(encoding='utf-8'))
        Path('built.json').write_text(json.dumps({'packagesDir': manifest['packagesDir']}), encoding='utf-8')
        return 0
    if arguments[:2] == ['env', 'lean'] and arguments[2] == 'DoMathExtract.lean':
        sys.path.insert(0, str(THIS.parent))
        import canon_lean
        other = settings.get('elaborates_otherwise')
        if other:
            # The stand-in compiler makes a statement's hash from its text, so a statement that is printed and read
            # again always has the hash it had. Lean can elaborate it to another term; this stands for that.
            challenge = Path('Challenge.lean')
            challenge.write_text(challenge.read_text(encoding='utf-8').replace(other, other + ' (h : True)'),
                                 encoding='utf-8', newline='\n')
        return canon_lean.extract('.', 'DoMathExtract.lean')
    if arguments[:2] == ['env', 'lean'] and arguments[2] == 'Check.lean':
        sys.path.insert(0, str(THIS.parent))
        import canon_lean
        text = Path('Check.lean').read_text(encoding='utf-8')
        # As in Lean, a name is known when a module that the file imports, directly or through others, declares it.
        visible = canon_lean.imported('.', re.findall(r'^import (\S+)$', text, re.M))
        declared = {declaration['user'] for declaration in canon_lean.library('.')
                    if declaration['module'] in visible and not declaration['private']}
        for name in re.findall(r'^#print axioms (\S+)$', text, re.M):
            if name not in declared:
                print(f'Check.lean: the stand-in finds no declaration {name} in the modules the file imports')
                return 1
            axioms = settings.get('axioms', {}).get(name, ['propext', 'Quot.sound'])
            if axioms is None:  # what is printed for this name holds no axioms line that the program can read
                print(f'{name} : a statement')
                continue
            print(f"{name} : a statement\n'{name}' depends on axioms: [{', '.join(axioms)}]" if axioms
                  else f"'{name}' does not depend on any axioms")
        return 0
    return 2


if __name__ == '__main__' and sys.argv[1:2] == ['session']:
    raise SystemExit(stand_in_session(Path(sys.argv[2])))
if __name__ == '__main__' and sys.argv[1:2] == ['lake']:
    raise SystemExit(stand_in_lake(Path(sys.argv[2]), sys.argv[3:]))
if __name__ == '__main__' and sys.argv[1:2] == ['version']:
    print('Lean (version 4.99.0, stand-in)')
    raise SystemExit(0)
