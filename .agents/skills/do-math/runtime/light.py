"""One light session: a call of the Claude CLI in print mode that reads a text and answers one request.

The search over the index of the canon and the blind descent test (search.py) read on a session's behalf
through such calls. A light session is no session of the research. The runner does not know it, it has no
folder under sessions/, it does not count against `max_sessions`, and nothing resumes it. It has no tools
and no MCP servers, so it can read nothing but what it is given and can change nothing. What it is given is
a system prompt, which holds the instructions and the text to read, and a request on its standard input.

The text to read stands in the system prompt because the provider keeps a system prompt it has read in a
cache. Measured on this CLI (2.1.332): a second call with the same system prompt read it from that cache,
with the same request and with another one, and the CLI asked for a cache that lasts an hour. A part of
the index that has not changed since an earlier search is therefore read at the price of a cached read.
"""
from contextlib import contextmanager
from pathlib import Path
import re
import subprocess
import time

from cli_adapter import Command, provider_for_model
from launch import worker_command, worker_environment
from retention import USAGE_REPORTS, events, refusal
from runtime_support import InstanceLock, popen_options, write_text

# The most tokens a light session may write, its reasoning included. A worker of the research may write
# 128,000 (launch.MAX_OUTPUT_TOKENS). A light session is launched without the `[1m]` suffix, and a provider
# that holds such a model to a window of 200,000 tokens refuses a request whose text and whose permitted
# answer together exceed the window. The text of a part is cut so that it and this number fit (search.PART_CHARS).
# An answer is a short JSON object, and the reasoning before it has stayed below 2,000 tokens at low effort.
OUTPUT_TOKENS = 32_000
# Seconds after which a light session that has not ended is ended. The CLI answered a system prompt of
# 12,000 tokens in 5 to 16 seconds; a part of the index is twelve times that. A session that hangs would
# otherwise hold its slot, and with it the searches of the whole instance, for as long as it hangs.
LIMIT_SECONDS = 1200
SLOT_POLL_SECONDS = 0.5


def command(executable, model, effort, folder, system):
    """The command of one light session, whose working folder is `folder` and whose system prompt is the file `system`.

    It is the command of a worker (launch.worker_command), which keeps out the operator's project and user
    settings, hooks, memories, plugins, slash commands and MCP servers, and writes worker-settings.json and
    worker-mcp.json into `folder` to do so. To that it adds: no built-in tool at all; the system prompt taken
    from a file, in place of the CLI's own, since a part of the index is far longer than a command line may
    be; and no conversation kept on the disk, since a light session is never resumed and its transcript, in
    the operator's profile, would hold a copy of every part it read. The `[1m]` that a worker's model
    carries is taken off: a part is far below 200,000 tokens."""
    if provider_for_model(model) != 'claude':
        raise ValueError(f'a light session runs on the Claude CLI and takes a model claude/<model>; got {model!r}')
    base = worker_command(executable, model, effort, folder)
    argv = list(base.argv)
    place = argv.index('--model') + 1
    argv[place] = re.sub(r'\[(?:1m|200k)\]$', '', argv[place], flags=re.IGNORECASE)
    argv += ['--tools', '', '--system-prompt-file', str(system), '--no-session-persistence']
    return Command('claude', argv, base.cwd)


def environment():
    """The environment of a light session's CLI: a worker's, with the smaller cap on what it writes (OUTPUT_TOKENS)."""
    values = worker_environment()
    values['CLAUDE_CODE_MAX_OUTPUT_TOKENS'] = str(OUTPUT_TOKENS)
    return values


@contextmanager
def slot(folder, parallel, name='slot'):
    """Hold one of `parallel` slots, waiting until one is free. `folder` holds the lock files <name>-<n>.lock.

    Every search and every blind test whose files are kept in the instance takes its slots from the same
    folder, <instance>/runner/search, so the light sessions of all of them together are bounded, whichever
    processes run them. A command that the operator gives with `--out` keeps its files in the folder it
    names, and its slots and its turn with them (search.home_of): it is bounded by `parallel` within that
    folder and stands outside the bound of the instance. A slot is a lock of the operating system on its
    file (runtime_support.InstanceLock), which the system frees when the process that holds it ends or
    dies. The system states no time by which it has done so, and a process that waits for a slot finds it
    free at one of its next looks. So no slot stays taken by a process that is gone, and none has to be
    judged stale. Two threads of one process hold two slots as two processes do, since each opens the file
    for itself.

    Under the name `slot` these are the slots of the light sessions (run). Under the name `turn` the
    processes that do the work of the searches and tests take their turns from the same folder by the
    same means (search.work), so that no more than `parallel` of them hold the research of the instance
    in memory at one time.

    What the number bounds is the light sessions whose slots are held, and the slot is held by the process
    that started the CLI, not by the CLI. When that process is ended from outside while a CLI runs, the
    system frees its slot, and the CLI runs on to the end of its call unless something else ends it. One
    thing does: a research session has a job on Windows, in which every process it starts runs
    (runtime_support.contain_session_processes), and when the session ends the system ends every process
    of the job together, the CLI among them. That holds when the session ends. It does not hold when the
    process that started the CLI is ended alone while its session lives, and it does not hold for a
    process in no such job, as one started by a command of the operator. In both cases the CLI is left
    running, and for that time one light session more than `parallel` allows can run for each CLI so left.
    Nothing here ends such a CLI, and nothing ends it at LIMIT_SECONDS, which the process that is gone
    would have enforced."""
    folder = Path(folder)
    folder.mkdir(parents=True, exist_ok=True)
    while True:
        for number in range(max(1, int(parallel))):
            lock = InstanceLock(folder / f'{name}-{number}.lock', holder='light session')
            try:
                lock.__enter__()
            except RuntimeError:
                continue
            try:
                yield number
            finally:
                lock.__exit__(None, None, None)
            return
        time.sleep(SLOT_POLL_SECONDS)


def result_event(folder):
    """The report with which the CLI ended the call whose streams are in `folder`, or None when it wrote none.

    The CLI in print mode ends a call with one event of the type `result`. It carries the final answer as
    text (`result`), whether the call ended in an error (`is_error`), and the use of the call
    (`total_cost_usd`, `modelUsage`, `duration_ms`). A CLI that was ended or that died wrote none."""
    found = None
    for event in events(Path(folder) / 'cli.stdout.jsonl'):
        if event.get('type') == 'result':
            found = event
    return found


def usage_of(event, seconds):
    """What a `result` event says the call used: tokens by kind, `cost_usd` and `seconds`.

    The kinds of tokens and the cost are those that the totals of a research session count
    (retention.usage), under the same names, so that the two can be added up side by side. The cost is the
    CLI's own estimate. `seconds` is the CLI's `duration_ms`, and the time measured around the process
    where the event has none or there is no event."""
    _, _, counted = USAGE_REPORTS['claude']
    event = event or {}
    tokens = {}
    by_model = event.get('modelUsage')
    for table in by_model.values() if isinstance(by_model, dict) else ():
        for key in counted:
            if isinstance(table, dict) and type(table.get(key)) is int:
                tokens[key] = tokens.get(key, 0) + table[key]
    cost, duration = event.get('total_cost_usd'), event.get('duration_ms')
    return {'tokens': tokens, 'cost_usd': cost if type(cost) in (int, float) else None,
            'seconds': round(duration / 1000, 1) if type(duration) in (int, float) else round(seconds, 1)}


def run(folder, system, request, *, executable, model, effort, slots, parallel, retry_seconds=1800):
    """Run one light session to its end and say what came of it.

    `folder` becomes the session's working folder and keeps request.txt and the CLI's streams,
    cli.stdout.jsonl and cli.stderr.log. `system` is the file with the system prompt, `request` the text
    for the standard input. `slots` is the folder of the slot files and `parallel` their number; a slot
    is held while the CLI runs and at no other time.

    Returns a mapping with exactly one of `text`, `refused` and `error` not None:
        text      the final answer, when the CLI ended the call with one;
        refused   {'reason', 'until'} when the provider or the model refused the session, as
                  retention.refusal tells it and as the runner knows a refusal: `usage_limit`,
                  `model_requires_usage_credits` or `model_refusal`. `until` is the time, in Unix
                  seconds, from which another session may be tried. Nothing is waited for here;
        error     a sentence, when the CLI could not be started, ended without an answer or ended in
                  an error of another kind, or was ended at LIMIT_SECONDS;
    and with `exit_code` (None for a CLI that was not started or was ended here) and `usage` (usage_of)."""
    folder = Path(folder)
    folder.mkdir(parents=True, exist_ok=True)
    write_text(folder / 'request.txt', request)
    line = command(executable, model, effort, folder, system)
    outcome = {'text': None, 'refused': None, 'error': None, 'exit_code': None, 'usage': usage_of(None, 0.0)}
    with slot(slots, parallel):
        started = time.time()
        try:
            with (folder / 'request.txt').open('rb') as inp, (folder / 'cli.stdout.jsonl').open('wb') as out, \
                    (folder / 'cli.stderr.log').open('wb') as err:
                process = subprocess.Popen(line.argv, cwd=line.cwd, env=environment(), stdin=inp, stdout=out,
                                           stderr=err, shell=False, **popen_options())
                try:
                    outcome['exit_code'] = process.wait(timeout=LIMIT_SECONDS)
                except subprocess.TimeoutExpired:
                    process.kill()
                    process.wait()
                except BaseException:  # the process that waits here is being ended: the CLI ends with it
                    process.kill()
                    process.wait()
                    raise
        except OSError as exc:
            outcome['error'] = f'the Claude CLI could not be started: {exc}'
            return outcome
        seconds = time.time() - started
    event = result_event(folder)
    outcome['usage'] = usage_of(event, seconds)
    refused = refusal(folder, 'claude', model, started, retry_seconds)
    text = event.get('result') if event and event.get('is_error') is not True else None
    if refused is not None:
        outcome['refused'] = {'reason': refused['reason'], 'until': refused['until']}
    elif isinstance(text, str) and text.strip():
        outcome['text'] = text
    elif outcome['exit_code'] is None:
        outcome['error'] = f'the light session had not ended after {LIMIT_SECONDS // 60} minutes and was ended'
    elif event is None:
        outcome['error'] = (f"the Claude CLI ended with exit code {outcome['exit_code']} and reported no result; "
                            f'what it wrote is in {folder}')
    elif event.get('is_error') is True:
        said = ' '.join(str(event.get('result') or event.get('subtype') or '').split())[:300]
        outcome['error'] = f'the Claude CLI ended the session with an error: {said or "(no message)"}'
    else:
        outcome['error'] = 'the light session ended without an answer'
    return outcome
