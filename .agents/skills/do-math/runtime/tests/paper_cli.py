"""The stand-ins that tests/test_paper.py launches in place of the CLI of a session and of TeX.

Run as `paper_cli.py session <scenario folder>` this file reads session.json in its working folder, writes
the files the scenario scripts for that kind of session, and records what the session was given. Run
as `paper_cli.py tex paper.tex` it is the TeX command: it fails on `\\undefinedmacro` and otherwise
leaves paper.pdf and paper.log. In the log, a line of the manuscript with `% wide` is reported as set
69pt wider than the text block and one with `% nearly` as 2.5pt wider, in the words of TeX. A line with
`% tight` is reported as 12.5pt too wide only when the manuscript carries the lines with which the paper
command measures the room of the displays.

The script of a scenario gives, for a key, what the sessions with that key write, one entry for each
session in turn and the last entry for every later one. A session looks for `<kind>:<section>`, then,
when its section is `<word>-<rest>`, as that of a repair of one section is, for `<kind>:<word>`, then
for `<kind>`. Sessions may run side by side, so the record of the calls is kept under a lock file.
The last repair of findings is a narrow one, and its sessions have the section `narrow-<kind>` or
`narrow-<kind>-<section>`, so `repair:narrow` scripts all of them; the session that then reads the
changed passages has the kind `changes`. The session that resolves what the readings left open has
the kind `resolve`, and a session that compares the running text of a section with the elements
has the kind `cover` and the section as its section. In a draft, the session that sketches a
section has the kind `sketch`, and the session that repairs the plan of a draft for the paper is a
`plan` session with the section `from-draft`.

`together.json` in the scenario folder lists groups of keys: a session whose own key is in a group
waits, before it writes anything, until a session of every key of the group has started, and its
call records under "met" whether they all did. Sessions that the command runs one after another
never meet.
"""
import json
import os
from pathlib import Path
import sys
import time


def stand_in_session(scenario):
    folder = Path.cwd()
    task = json.loads((folder / 'session.json').read_text(encoding='utf-8'))
    sys.stdin.reconfigure(encoding='utf-8')  # the command hands over the bytes of a UTF-8 file, whatever the locale
    prompt = sys.stdin.read()
    script = json.loads((scenario / 'script.json').read_text(encoding='utf-8'))
    record = scenario / 'calls.json'
    own = f"{task['kind']}:{task['section']}"
    names = [own] + ([own.split('-')[0]] if '-' in (task['section'] or '') else []) + [task['kind']]
    key = next((k for k in names if k in script), None)
    given = sorted(p.relative_to(folder).as_posix() for p in folder.rglob('*')
                   if p.is_file() and not p.name.startswith(('cli.', 'worker-')))
    # Sessions of one group wait for each other, which they can only do when the command runs them side by side.
    groups = scenario / 'together.json'
    group = next((g for g in (json.loads(groups.read_text(encoding='utf-8')) if groups.exists() else []) if own in g), None)
    met = None
    if group:
        present = lambda k: scenario / ('present-' + k.replace(':', '-'))
        present(own).touch()
        deadline = time.time() + 20
        while not (met := all(present(k).exists() for k in group)) and time.time() < deadline:
            time.sleep(0.05)
    lock = scenario / 'calls.lock'
    while True:
        try:
            os.close(os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY))
            break
        except (FileExistsError, PermissionError):
            time.sleep(0.01)
    stopped = False
    try:
        calls = json.loads(record.read_text(encoding='utf-8')) if record.exists() else []
        if key is not None:
            entries = script[key]
            entry = entries[min(sum(c['key'] == key for c in calls), len(entries) - 1)]
            # An entry `{'@stopped': ...}` stands for a session that a safeguard of the AI system stopped.
            stopped = '@stopped' in entry
            for name, content in entry.items():
                if name != '@stopped':
                    (folder / name).parent.mkdir(parents=True, exist_ok=True)
                    (folder / name).write_text(content, encoding='utf-8', newline='\n')
        calls.append({'key': key, 'kind': task['kind'], 'section': task['section'], 'folder': folder.name,
                      'given': given, 'prompt': prompt, 'met': met})
        record.write_text(json.dumps(calls), encoding='utf-8')
    finally:
        lock.unlink()
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


def stand_in_tex(arguments):
    text = Path(arguments[-1]).read_text(encoding='utf-8')
    for number, line in enumerate(text.splitlines(), 1):
        if '\\undefinedmacro' in line:
            print(f'./paper.tex:{number}: Undefined control sequence.\nl.{number} \\undefinedmacro')
            return 1
    log = ['This is a stand-in for TeX.']
    for number, line in enumerate(text.splitlines(), 1):
        if '% wide' in line:
            log += [f'Overfull \\hbox (69.23543pt too wide) detected at line {number}', '[]']
        if '% nearly' in line:
            log += [f'Overfull \\hbox (2.5pt too wide) in paragraph at lines {number}--{number + 1}', '[]']
        # A display that fits its line only with its spaces closed up shows in the typesetting that measures the
        # displays and not in the manuscript's own; the lines the script adds for the measuring name \paper@equation.
        if '% tight' in line and '\\paper@equation' in text:
            log += [f'Overfull \\hbox (12.5pt too wide) detected at line {number}', '[]']
    Path('paper.log').write_text('\n'.join(log) + '\n', encoding='utf-8')
    Path('paper.pdf').write_bytes(b'%PDF-1.4 stand-in\n')
    return 0


if __name__ == '__main__' and sys.argv[1:2] == ['session']:
    raise SystemExit(stand_in_session(Path(sys.argv[2])))
if __name__ == '__main__' and sys.argv[1:2] == ['tex']:
    raise SystemExit(stand_in_tex(sys.argv[2:]))
