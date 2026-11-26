"""The session runner that the paper command and the finalize pipeline share: it launches one session in a folder, waits for a provider that refuses it, reads what the session wrote, and runs sessions side by side."""
from concurrent.futures import ThreadPoolExecutor, wait
from contextlib import contextmanager
import json
from pathlib import Path
import re
import subprocess
import threading
import time

from cli_adapter import provider_for_model
from launch import worker_command, worker_environment
from retention import events, model_refused, refusal
from runtime_support import InstanceLock, popen_options, read_json, write_json, write_text
from settings import load_settings

SESSION_ATTEMPTS = 2   # sessions for one task before the command gives up on output it can read, unless the caller says otherwise
PARALLEL = 4           # sessions side by side, unless the caller says otherwise; a session mostly waits on the network
LIMIT_WAITS = 12       # times one session is started again after its provider refused it (Sessions.launch)
NO_OUTPUT = ('Nothing is to be repaired by hand: the reasons are what the sessions left, and a new session may do '
             'better. Start the same command again. If it stops in the same way, the reasons say what the task asks '
             'and the sessions could not do.')
# What a person does when the CLI of every session of a task ended with an error before the session wrote anything.
DIED = ('Nothing that a session wrote is in question: the CLI of each session ended with an error before the session '
        'wrote anything, as when the network or the provider fails. The `session` events of log.json name the folders '
        'of these sessions, and cli.stderr.log and cli.stdout.jsonl there hold what the CLI said. Where that names '
        'something of this machine, such as the network, the login of the CLI or its memory, put it right first. '
        'Then start the same command again.')
# What a person does when a safeguard of the AI system stopped every session of a task that the run needs.
STOPPED = ('Nothing is to be repaired by hand. Start the same command again: it starts the session again, with the '
           'same prompt and the same files. The folders of the stopped sessions, which are named above, hold what '
           'each session was given and what the CLI answered.')
# What a person does when a provider refused a session through every wait (Sessions.launch).
REFUSED = ('Nothing is to be repaired by hand, and no output of a session is in question: the provider did not take '
           'the session. The reason named above is usage_limit for the usage limit of the account, model_capacity for '
           'a model for which the provider has no capacity, and model_requires_usage_credits for a model that asks for '
           'usage credits. Start the same command again when the provider takes sessions of that model again.')
# The tools by which a session of the Claude CLI can arrange to be called again later. Sessions.launch
# withholds them from every session. The command reads a session's output when its process has ended, and
# the CLI does not exit while such a call is pending: a reading session that had set itself a reminder
# while its sub-agents worked wrote its output, ended its turn, and held the run idle for eleven minutes
# until the reminder fired. A session needs none of them, because its own sub-agents and background
# commands call it back when they end.
SELF_SCHEDULING = ('ScheduleWakeup', 'CronCreate', 'CronDelete', 'CronList', 'Monitor')
AGAIN = '''

A session before this one had the same task, and the script could not use what it left, for these reasons:

{problems}

What it left is in `previous-output/`. Do the task again so that these reasons no longer hold.
'''


class Stop(Exception):
    """The command cannot go on; the message says why.

    `todo` says what the person who reads the message does next, where that is something else than
    putting right what the message names and starting the command again."""

    def __init__(self, message='', todo=None):
        super().__init__(message)
        self.todo = todo


class Unusable(Exception):
    """A session left output the script cannot use; the problems go to the session that is started in its place."""

    def __init__(self, problems):
        super().__init__('; '.join(problems))
        self.problems = list(problems)


class Held(Stop):
    """Another command is at work in the folder of the run, so this one does not begin."""


class Refused(Stop):
    """A provider refused a session each time it was started, through every wait; no output of the task was read."""


class Unmade(Stop):
    """No session of a task left output that the script can use, and the script read what at least one of them left.

    `died` is true when nothing that a session wrote was read: the CLI of every such session had ended with
    an error before the session wrote anything. A caller that discards a piece of work for what its
    sessions wrote does not discard it then."""

    def __init__(self, message='', todo=None, died=False):
        super().__init__(message, todo)
        self.died = died


@contextmanager
def alone(folder):
    """Hold the folder of a run for the command that calls this; Held when another command is at work in it.

    A command keeps the state and the log of its run in memory and writes them whole, numbers the folders
    of its sessions from what it found at its start, and clears what it is about to make again. Two commands
    at work in one folder do each of these against the other. A run can stand still for hours while it waits for
    a provider that refused a session, and its folder then looks like that of a command that has ended. So the command
    holds a lock beside the folder, as the runner holds one in its instance (runtime_support.InstanceLock):
    the operating system frees it when the command ends or dies, and the command takes the file away with it."""
    folder = Path(folder).resolve()
    lock = InstanceLock(folder.with_name(folder.name + '.lock'))
    lock.path.parent.mkdir(parents=True, exist_ok=True)
    try:
        lock.__enter__()
    except RuntimeError:
        raise Held(f'another command is at work in {folder} and holds {lock.path}. It goes on by itself, also '
                   'while it waits for a provider that refused a session; give the command again when it has '
                   'ended') from None
    try:
        yield
    finally:
        lock.__exit__(None, None, None)
        try:
            lock.path.unlink()
        except OSError:
            pass  # a command that is starting has the file open at this moment; a later command removes it


def is_text(value):
    return isinstance(value, str) and bool(value.strip())


def collapsed(text):
    """The text with every run of whitespace replaced by one space."""
    return re.sub(r'\s+', ' ', text).strip()


def read_file(path):
    return Path(path).read_text(encoding='utf-8-sig').replace('\r\n', '\n')


def stopped_by_safeguard(folder, provider):
    """Whether a safeguard of the AI system ended the session in `folder` before it had finished.

    The sign is in what the CLI wrote to its standard output, cli.stdout.jsonl: the result of a turn
    that a refusal of the model ended (retention.model_refused, by which the research's runner knows
    such a refusal as well). The sign is known for the Claude CLI only; a session of another provider
    is never taken to be stopped in this way. The exit code does not tell such a session from another
    that failed, and its folder `output` can hold files that the session wrote before it was stopped,
    so nothing of it is read."""
    return provider == 'claude' and any(model_refused(event) for event in events(Path(folder) / 'cli.stdout.jsonl'))


class Sessions:
    """The sessions that a command launches, each in a folder of its own under <out>/sessions, and the log <out>/log.json.

    `instance` is a folder with settings.json, from which the CLIs and the models are taken: `writer` is
    the first entry of `models`, `assessor` the first entry of the role `review`, or of `models` when the
    settings name none. `parallel` bounds the sessions that side_by_side runs at a time. `gate`, when it
    is given, is a semaphore that bounds the CLI processes of every object that shares it: launch holds it
    while the process of a session runs, and not while it waits for a provider that refused the session. With `dry`
    the log is kept in memory and not written."""

    def __init__(self, instance, out, parallel=PARALLEL, dry=False, gate=None):
        self.instance, self.out = Path(instance).resolve(), Path(out).resolve()
        self.settings = load_settings(self.instance)
        first = self.settings['models'][0]
        self.writer = {'model': first['model'], 'effort': first['effort']}
        self.assessor = self.settings['roles'].get('review', self.settings['models'])[0]
        self.parallel, self.dry, self.gate = max(1, int(parallel)), dry, gate
        # Sessions that run side by side share the log and the numbering of their folders.
        self.lock = threading.RLock()
        self.stopping, self.running = threading.Event(), set()
        self.log = read_json(self.out / 'log.json') if (self.out / 'log.json').is_file() else []
        # The checks that were not made, because a safeguard of the AI system stopped every session that had the
        # task (session): each with the kind of the session, its section, what the check speaks for ("about"),
        # the words that name it in a report ("what"), and the number of attempts. Kept in <out>/not-done.json.
        self.undone = read_json(self.out / 'not-done.json') if (self.out / 'not-done.json').is_file() else []
        numbers = [int(match[0]) for path in (self.out / 'sessions').iterdir() if (match := re.match(r'\d+', path.name))] \
            if (self.out / 'sessions').is_dir() else []
        self.count = max(numbers, default=0)

    def event(self, name, **fields):
        with self.lock:
            self.log.append({'event': name, 'at': time.strftime('%Y-%m-%d %H:%M:%S'), **fields})
            if not self.dry:
                write_json(self.out / 'log.json', self.log)

    def launch(self, kind, prompt, files, choice, section=None, servers=None):
        """One session in its own folder: its prompt and its files are written, the CLI runs to its end.

        `files` maps a path under the folder to its content, a text or bytes. `servers` are the MCP
        servers of the session; without them it has none. Returns the folder.

        A session that its provider refuses is waited for and started again, in the same folder and
        with the same model, LIMIT_WAITS times at the most. A refusal can reach a session that has
        already written files, and such files are no finished output, so `output` is emptied before
        each new start. The refusals are those that retention.refusal tells, by which the research's
        runner knows them as well: the usage limit of the account, a model for which the provider has
        no capacity, and a model that asks for usage credits. The wait lasts until the reset that the
        provider named for a usage limit, and for retry_max_seconds of the settings where none is
        named. A refusal of the model itself is none of these: a safeguard stopped that session, and
        `session` starts it again (stopped_by_safeguard). When the provider still refuses the last
        start, Refused is raised."""
        with self.lock:
            if self.stopping.is_set():
                raise Stop('the command was interrupted')
            self.count += 1
            folder = self.out / 'sessions' / f"{self.count:02d}-{kind}{'-' + section if section else ''}"
            (folder / 'output').mkdir(parents=True)
        for name, content in files.items():
            (folder / name).parent.mkdir(parents=True, exist_ok=True)
            if isinstance(content, bytes):
                (folder / name).write_bytes(content)
            else:
                write_text(folder / name, content)
        write_text(folder / 'prompt.txt', prompt)
        write_json(folder / 'session.json', {'kind': kind, 'section': section, **choice})
        provider = provider_for_model(choice['model'])
        for waits in range(LIMIT_WAITS + 1):
            # The gate is held from here to the end of the process, so that the sessions of everything that shares
            # it are bounded together. It is given back before a wait for the provider, which can last hours.
            while self.gate is not None and not self.gate.acquire(timeout=0.5):
                if self.stopping.is_set():
                    raise Stop('the command was interrupted')
            try:
                command = worker_command(self.settings['cli'][provider], choice['model'], choice['effort'], folder,
                                         servers or {}, withheld=SELF_SCHEDULING)
                started = time.time()
                try:
                    # A start that the provider refused may have written into `output` before it was cut off. The
                    # session that starts now knows nothing of those files, so it begins with an empty `output`.
                    for path in sorted((folder / 'output').rglob('*'), reverse=True) if waits else ():
                        if path.is_dir():
                            path.rmdir()
                        else:
                            path.unlink()
                    with (folder / 'prompt.txt').open('rb') as inp, (folder / 'cli.stdout.jsonl').open('wb') as out, \
                            (folder / 'cli.stderr.log').open('wb') as err:
                        process = subprocess.Popen(command.argv, cwd=command.cwd, env=worker_environment(), stdin=inp,
                                                   stdout=out, stderr=err, shell=False, **popen_options())
                        with self.lock:
                            self.running.add(process)
                            if self.stopping.is_set():  # the interrupt came before this process existed
                                process.kill()
                        try:
                            code = process.wait()
                        except BaseException:  # the command is interrupted while this thread waits: the session ends with it
                            process.kill()
                            process.wait()
                            raise
                        finally:
                            with self.lock:
                                self.running.discard(process)
                except OSError as exc:
                    raise Stop(f'the {kind} session could not be started: {exc}')
            finally:
                if self.gate is not None:
                    self.gate.release()
            if self.stopping.is_set():
                raise Stop('the command was interrupted')
            # The refusals of the provider that are waited for. A refusal of the model itself is none of them: a
            # safeguard stopped that session, and `session` starts it again and counts it.
            refused = refusal(folder, provider, choice['model'], started, self.settings['retry_max_seconds'])
            if refused is not None and refused['reason'] == 'model_refusal':
                refused = None
            until = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(refused['until'])) if refused else None
            self.event('session', folder=folder.relative_to(self.out).as_posix(), kind=kind, section=section, **choice,
                       exit_code=code, seconds=round(time.time() - started, 1),
                       usage_limit_until=until if refused and refused['reason'] == 'usage_limit' else None,
                       refused=refused['reason'] if refused else None, refused_until=until)
            if refused is None:
                return folder
            # The same session is started again when the wait ends. After the last start nothing is waited for.
            if waits < LIMIT_WAITS and self.stopping.wait(max(0.0, refused['until'] - time.time())):
                raise Stop('the command was interrupted')
        raise Refused(f'the provider refused the {kind} session' + (f' of {section}' if section else '')
                      + f" with the model {choice['model']} each of the {LIMIT_WAITS + 1} times it was started, the last "
                      f"time for this reason: {refused['reason']} ({folder.relative_to(self.out).as_posix()} holds what "
                      'the CLI answered)', todo=REFUSED)

    def session(self, kind, prompt, files, read, choice, section=None, attempts=SESSION_ATTEMPTS, servers=None,
                check=None):
        """Launch sessions for one task until one leaves output that `read` accepts; returns what `read` returns.

        `read` is given the folder `output` of the session and returns what the caller wants, or raises
        Unusable with the reasons, which the next session is told.

        A session that a safeguard of the AI system stopped (stopped_by_safeguard) is another case. Its
        output is not read, and the session is started again as it was: with the same prompt and the
        same files, and without a word about the stop. It counts among the `attempts`. When every
        attempt was stopped, what follows depends on the task. A task that makes something the run
        needs stops the run. A task that is a check of what the run has made is given `check`: a
        mapping from each thing the check speaks for (None when that is the whole of what the session
        is given, otherwise for example the label of a statement) to the words that name the check
        in a report. Each of them is then recorded as not done (`undone`, <out>/not-done.json), and
        None is returned in the place of what `read` returns. A check that is made later for the same
        thing takes the record away, since it speaks for the text as it then stands."""
        problems, previous, stopped, died = None, {}, [], 0
        provider = provider_for_model(choice['model'])
        for _ in range(attempts):
            text = prompt if problems is None else prompt + AGAIN.format(problems='\n'.join('- ' + p for p in problems))
            folder = self.launch(kind, text, {**files, **previous}, choice, section, servers)
            if stopped_by_safeguard(folder, provider):
                stopped.append(folder.relative_to(self.out).as_posix())
                self.event('safeguard', folder=stopped[-1], kind=kind, section=section)
                continue
            # A CLI that ended with an error before its session wrote anything left no work of the session to judge.
            # Its exit code is in the `session` event that `launch` wrote for this folder.
            name = folder.relative_to(self.out).as_posix()
            with self.lock:
                code = next(event['exit_code'] for event in reversed(self.log)
                            if event['event'] == 'session' and event['folder'] == name)
            died += bool(code) and not any((folder / 'output').iterdir())
            try:
                result = read(folder / 'output')
            except Unusable as exc:
                problems = exc.problems
            except (TypeError, KeyError, AttributeError, UnicodeDecodeError) as exc:
                problems = [f'the output does not have the form the prompt describes ({type(exc).__name__}: {exc})']
            else:
                if check is not None:
                    self.record_undone(kind, section, check, None)
                return result
            self.event('check', check='output of the ' + kind + ' session', problems=problems)
            previous = {'previous-output/' + path.relative_to(folder / 'output').as_posix():
                        path.read_text(encoding='utf-8', errors='replace')
                        for path in sorted((folder / 'output').rglob('*')) if path.is_file()}
        if len(stopped) < attempts:
            died = died == attempts - len(stopped)
            raise Unmade(f'no {kind} session left output the script can use, in {attempts} attempts'
                         + (f', of which a safeguard of the AI system stopped {len(stopped)}' if stopped else '') + ': '
                         + '; '.join(problems)
                         + ('. The CLI of every session that was read had ended with an error before the session '
                            'wrote anything' if died else ''), todo=DIED if died else NO_OUTPUT, died=died)
        if check is None:
            raise Stop(f'a safeguard of the AI system stopped every {kind} session' + (f' of {section}' if section else '')
                       + f', in {attempts} attempts, before it had finished (' + ', '.join(stopped) + '). The run needs '
                       'what this session makes, so it cannot go on without it', todo=STOPPED)
        self.record_undone(kind, section, check, attempts)
        self.event('not done', kind=kind, section=section, checks=list(check.values()), attempts=attempts, sessions=stopped)
        return None

    def record_undone(self, kind, section, check, attempts):
        """Record the checks of `check` as not done after `attempts` stopped sessions, or with None as made after all."""
        with self.lock:
            left = [entry for entry in self.undone
                    if (entry['kind'], entry['section']) != (kind, section) or entry['about'] not in check]
            if attempts is not None:
                left += [{'kind': kind, 'section': section, 'about': about, 'what': what, 'attempts': attempts}
                         for about, what in check.items()]
            if left != self.undone:
                self.undone = left
                if not self.dry:
                    write_json(self.out / 'not-done.json', self.undone)

    def interrupt(self):
        """The command is being stopped from outside: the sessions that run end with it, and no other is started."""
        self.stopping.set()
        with self.lock:
            for process in list(self.running):
                process.kill()

    def side_by_side(self, tasks):
        """Run tasks that do not depend on each other, up to `parallel` at a time; their results, in the order of the tasks.

        Each task keeps on disk what it makes, as soon as it has made it. When one fails for good, the
        tasks that have not begun are not begun, those that are running come to their end and keep
        what they make, and only then is the failure raised, so that a later --resume finds all of it."""
        if len(tasks) < 2 or self.parallel < 2:
            return [task() for task in tasks]
        failed = threading.Event()

        def run(task):
            if failed.is_set() or self.stopping.is_set():
                return None
            try:
                return task()
            except BaseException:
                failed.set()
                raise

        pool = ThreadPoolExecutor(max_workers=min(self.parallel, len(tasks)))
        futures = [pool.submit(run, task) for task in tasks]
        try:
            while wait(futures, timeout=0.5).not_done:  # a wait with an end, so that an interrupt reaches this thread
                pass
        except BaseException:
            self.interrupt()
            pool.shutdown(wait=True)
            raise
        pool.shutdown()
        for future in futures:
            if future.exception() is not None:
                raise future.exception()
        return [future.result() for future in futures]

    @staticmethod
    def load(path, kind=dict):
        """The JSON that a session left at `path`, an object or with `kind=list` an array; Unusable when it is not there."""
        if not path.is_file():
            raise Unusable([f'output/{path.name} was not written'])
        try:
            data = json.loads(read_file(path))
        except ValueError as exc:
            raise Unusable([f'output/{path.name} is not JSON: {exc}'])
        if not isinstance(data, kind):
            raise Unusable([f"output/{path.name} holds a JSON {'object' if kind is dict else 'array'}"])
        return data
