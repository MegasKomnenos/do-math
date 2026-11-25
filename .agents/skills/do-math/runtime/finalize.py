"""Turn a finished do-math research into a package under solved/.

    python finalize.py <instance> --name <name> [--config <file>]

<instance> is a finished do-math instance whose root is proved formally. The package ends as
<repository>/solved/<name>/, where <repository> is the repository that holds this skill. The run keeps
everything that is not the package in <repository>/.skill-workspace/finalize-<name>/, and started again
with the same arguments it continues the run that this folder holds. It asks nothing while it runs.

Exit codes: 0 the package is in place; 1 the command refused before any work; 2 a stage could not
meet its exit condition, and report.md in the work folder says which and why.

This program conducts: it holds the order of the stages and their exit checks, and no session decides
either. A step writes into folders of its own, records the hashes of its products in state.json when
its exit check has passed, and compares the hash of every product it reads before it reads it. What
needs no session is in package.py; the sessions are launched as the paper command launches them
(paper.Sessions), from the instruction files under <skill>/finalize/.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import shutil
import subprocess
import sys
import threading
import time
import traceback

import canon
from canon import CanonError, module_file, name_path, parse_record
import knowledge
import package
import paper
from paper import Sessions, Stop, Unusable, produce
from package import write_json, write_text  # safe from several threads, unlike the runtime's own writer
from runtime_support import alive, contain_session_processes, popen_options, read_json, remove_tree
from settings import validate

RUNTIME = Path(__file__).resolve().parent
SKILL = RUNTIME.parent
REPOSITORY = Path(__file__).resolve().parents[4]
NAME = re.compile(r'[a-z0-9][a-z0-9-]*')
PART_ID = re.compile(r'[a-z0-9][a-z0-9-]*')
PLACEHOLDER = re.compile(r'\{\{([a-z_]+)\}\}')
FINDING_KINDS = ('hypothesis', 'conclusion', 'comment', 'other')
KEPT_AT_END = ('report.md', 'decisions.md', 'log.json')
BUILD_SECONDS = 10      # one wait for a build before the broker is looked at again
BROKER_SECONDS = 5      # how often the run looks whether its broker is alive


class Refusal(Exception):
    """The command does not begin; the message says why."""


class Halt(Exception):
    """A step could not meet its exit condition; the run stops here and continues here when started again."""

    def __init__(self, step, message):
        super().__init__(message)
        self.step, self.message = step, message


class Changed(ValueError):
    """Something a step accepted is no longer what was accepted. It stops the run and discards nothing."""


def default_config():
    return {'authors': [], 'licence': 'CC-BY-4.0',
            'human_review': {'status': 'none', 'reviewers': [], 'notes': ''}, 'parallel': 8, 'tex': None}


def load_config(path):
    """The configuration of a run: the defaults with what the file gives; a key the command does not know is refused."""
    config = default_config()
    if path is None:
        return config
    try:
        raw = json.loads(Path(path).read_text(encoding='utf-8-sig'))
    except (OSError, ValueError) as error:
        raise Refusal(f'the configuration {path} cannot be read: {error}')
    if not isinstance(raw, dict):
        raise Refusal('the configuration is a JSON object')
    unknown = sorted(set(raw) - set(config))
    if unknown:
        raise Refusal('unknown configuration key: ' + ', '.join(unknown))
    config.update(raw)
    text = lambda value: isinstance(value, str) and bool(value.strip())
    authors = config['authors']
    if not isinstance(authors, list) or not all(
            isinstance(a, dict) and text(a.get('name')) and not set(a) - {'name', 'address', 'email', 'orcid', 'github'}
            and all(isinstance(value, str) for value in a.values()) for a in authors):
        raise Refusal('"authors" is a list of objects with "name" and optionally "address", "email", "orcid", "github"')
    if not text(config['licence']):
        raise Refusal('"licence" is an SPDX identifier')
    review = config['human_review']
    if (not isinstance(review, dict) or set(review) - {'status', 'reviewers', 'notes'} or not text(review.get('status'))
            or not isinstance(review.get('reviewers', []), list) or not isinstance(review.get('notes', ''), str)):
        raise Refusal('"human_review" is an object with "status", "reviewers" and "notes"')
    config['human_review'] = {'status': review['status'], 'reviewers': list(review.get('reviewers', [])),
                              'notes': review.get('notes', '')}
    if type(config['parallel']) is not int or config['parallel'] < 1:
        raise Refusal('"parallel" is the number of sessions that run at once, at least 1')
    if config['tex'] is not None and not (isinstance(config['tex'], list) and config['tex']
                                          and all(text(word) for word in config['tex'])):
        raise Refusal('"tex" is the TeX command as an array, or null')
    return config


def tree(prefix, folder, only=None):
    """The files of a folder for a session, by their path under `prefix`; `only` names the entries of the folder to take."""
    found = {}
    for relative, path in package.files_under(folder).items():
        if only is None or relative.split('/')[0] in only:
            found[prefix + relative] = path.read_bytes()
    return found


def as_json(value):
    return json.dumps(value, ensure_ascii=False, indent=2) + '\n'


def given_digest(prompt, files):
    """One identity for what a session is given: its prompt and its files."""
    digest = hashlib.sha256(prompt.encode('utf-8'))
    for name in sorted(files):
        content = files[name]
        digest.update(name.encode('utf-8') + b'\0'
                      + hashlib.sha256(content if isinstance(content, bytes) else content.encode('utf-8')).digest())
    return digest.hexdigest()


def is_text(value):
    return isinstance(value, str) and bool(value.strip())


def collapsed(text):
    return ' '.join(text.split())


class Run:
    """One run of the command: its work folder, its state, its sessions and its compile service."""

    def __init__(self, instance, name, config, config_path=None):
        self.instance, self.name, self.config = Path(instance).resolve(), name, config
        self.config_path = config_path
        self.work = REPOSITORY / '.skill-workspace' / ('finalize-' + name)
        self.solved = REPOSITORY / 'solved' / name
        self.package = self.work / 'package'
        self.lock = threading.RLock()
        self.gate = threading.BoundedSemaphore(config['parallel'])
        self.ending = threading.Event()
        self.broker_lock, self.broker_attempt = threading.Lock(), float('-inf')
        self.state = self.sessions = self.settings = None

    # -- state, products and steps ----------------------------------------------------------------------

    def path(self, relative):
        return self.work / relative

    def save(self):
        with self.lock:
            write_json(self.work / 'state.json', self.state)

    def recorded(self, relative):
        """The hash that the step which wrote a product recorded for it, or None when no step has finished it."""
        with self.lock:
            for step in self.state['steps'].values():
                if relative in step['products']:
                    return step['products'][relative]
        return None

    def step(self, sid, reads, writes, work, keep=()):
        """One step: its inputs compared with what their steps left, its own folders cleared, its work, its record.

        A step that has an entry in state.json has passed its exit check and is not made again. `work`
        returns when the exit check has passed and raises otherwise. `keep` names the products that
        are not cleared when the step is entered again, for a step that continues what it has on disk."""
        with self.lock:
            if sid in self.state['steps']:
                return
        try:
            for relative in reads:
                known = self.recorded(relative)
                if known is None:
                    raise Stop(f'the product {relative} has no entry in state.json: the step that writes it has not '
                               'passed its exit check')
                if not self.path(relative).exists() or package.product_hash(self.path(relative)) != known:
                    raise Stop(f'the product {relative} is not what the step that wrote it left: its hash differs from '
                               'the one in state.json. A product is written once; restore it, or delete the entries of '
                               'that step and of the steps after it from state.json so that they are made again')
            for relative in writes:
                target = self.path(relative)
                if relative in keep or not target.exists():
                    continue
                remove_tree(target) if target.is_dir() else target.unlink()
            self.sessions.event('step', step=sid)
            work()
            record = {'products': {relative: package.product_hash(self.path(relative)) for relative in writes
                                   if self.path(relative).exists()},
                      'read': {relative: self.recorded(relative) for relative in reads}}
        except Halt:
            raise
        except (Stop, CanonError, OSError, ValueError, RuntimeError) as error:
            self.sessions.event('check', check='exit check of ' + sid, problems=[str(error)])
            raise Halt(sid, str(error))
        except Exception:
            raise Halt(sid, 'the program failed in this step:\n' + traceback.format_exc())
        with self.lock:
            self.state['steps'][sid] = record
            self.save()
        self.sessions.event('check', check='exit check of ' + sid, problems=[])

    def decide(self, stage, text):
        """One choice, with its reason, appended to decisions.md."""
        with self.lock:
            path = self.work / 'decisions.md'
            before = path.read_text(encoding='utf-8') if path.is_file() else '# Decisions of the run\n'
            write_text(path, before + f'\n## {stage}\n\n{text.strip()}\n')

    # -- sessions ---------------------------------------------------------------------------------------

    def prompt(self, instruction, names=None):
        """`finalize/common.md` followed by the instruction file, with every `{{name}}` replaced."""
        folder = SKILL / 'finalize'
        text = package.read_text(folder / 'common.md') + '\n' + package.read_text(folder / (instruction + '.md'))
        source = self.settings['lean']['cwd']
        values = {'work': self.work.as_posix(), 'skill': SKILL.as_posix(), 'python': Path(sys.executable).as_posix(),
                  'library': self.library, 'root': self.root, 'main': self.state.get('main') or '',
                  'imported_source': source if source else
                  'There is none: the library imports nothing beyond what Lean itself brings.',
                  'expect_mb': str(self.expect_mb), **(names or {})}

        def value(match):
            if match[1] not in values:
                raise Stop(f'{instruction}.md uses {{{{{match[1]}}}}}, a name the command does not give')
            return values[match[1]]

        return PLACEHOLDER.sub(value, text)

    def task(self, kind, instruction, files, read, model, label=None, names=None, servers=None):
        """One task of a session: launched until `read` accepts its output, and not launched again once it was accepted.

        The accepted output is hashed and entered in state.json with the identity of what the session
        was given. When the run is started again and gives the task the same prompt and files, the
        output is read from its folder; an accepted output that has changed since stops the run."""
        prompt = self.prompt(instruction, names)
        given = given_digest(prompt, files)
        key = kind + (':' + label if label else '')
        with self.lock:
            kept = self.state['accepted'].get(key)
        if kept and kept['given'] == given:
            output = self.work / kept['folder'] / 'output'
            if not output.is_dir() or canon.tree_hash(output) != kept['hash']:
                raise Changed(f"the accepted output of the session {kept['folder']} is not what was accepted: its hash "
                              'differs from the one in state.json')
            try:
                return read(output)
            except Unusable as error:
                raise Changed(f"the accepted output of the session {kept['folder']} is no longer usable: {error}")
        found = {}

        def reading(output):
            result = read(output)
            found['output'] = output
            return result

        result = self.sessions.session(kind, prompt, files, reading, model, section=label, servers=servers)
        with self.lock:
            self.state['accepted'][key] = {'given': given, 'hash': canon.tree_hash(found['output']),
                                           'folder': found['output'].parent.relative_to(self.work).as_posix()}
            self.save()
        return result

    def discardable(self, what, work):
        """A simplification: when its sessions leave nothing usable it is discarded and the fact recorded.

        Returns what `work` returns, or None when the part was discarded. An interruption of the
        command is not a failed simplification and goes on as it is."""
        try:
            return work()
        except Stop as error:
            if self.sessions.stopping.is_set():
                raise
            self.decide(what, f'Discarded; that part of the library keeps the form it had. {error}')
            return None

    def paper_main(self):
        """The main result of the paper when it is not the root: the theorem the selection built the package around.

        The paper command takes the declaration that settles the root as its main result unless it is given
        another. Where the selection chose a stronger theorem, the paper states that theorem first and the
        root as its corollary."""
        return self.state['main'] if self.state['main'] != self.root else None

    def paper_run(self, view, out, **options):
        """The paper command in this process, on a view, with the run's bound on sessions; returns its exit code.

        A folder that holds a run of the paper command is continued as that command continues it. A run
        that was stopped, or whose last end is a failure, is resumed. A run that came to its end with
        findings left open is taken up by `paper.act_on_open`, since the paper command does not resume
        a run that has ended. A run that came to its end without them is done, and nothing is launched
        for it."""
        out = Path(out)
        log = read_json(out / 'log.json') if (out / 'log.json').is_file() else []
        ended = log[-1] if log and log[-1].get('event') == 'end' and log[-1].get('status') != 'failed' else None
        if ended is not None and ended['status'] == 'open_findings':
            return paper.act_on_open(view, out, self.config['tex'], None, self.config['parallel'], gate=self.gate)
        if ended is not None:
            return 0 if ended['status'] in ('complete', 'draft') else 3
        resume = (out / 'materials.json').is_file()
        if out.exists() and not resume:
            remove_tree(out)
        return produce(view, out, tex=self.config['tex'], parallel=self.config['parallel'], resume=resume,
                       gate=self.gate, **options)

    # -- compiling --------------------------------------------------------------------------------------

    def ensure_broker(self):
        """Start the run's Lean broker when none is alive."""
        from lean_broker import Paths, broker_alive, launch_broker
        paths = Paths(self.work)
        with self.broker_lock:
            if broker_alive(paths) or time.monotonic() - self.broker_attempt < BROKER_SECONDS:
                return
            self.broker_attempt = time.monotonic()
            launch_broker(paths)

    def watch_broker(self):
        """Sessions compile through the broker while the program waits for them, so it is looked after all the time."""
        while not self.ending.wait(BROKER_SECONDS):
            try:
                self.ensure_broker()
            except OSError:
                pass

    def stop_broker(self):
        from lean_broker import Paths, broker_alive, terminate_tree
        self.ending.set()
        info = broker_alive(Paths(self.work))
        if info:
            terminate_tree(info['process']['pid'])
            deadline = time.monotonic() + 30
            while alive(info['process']) and time.monotonic() < deadline:
                time.sleep(0.1)

    def library_ok(self, label, base=None, files=None, replace=None, delete=(), extract=False, records=None,
                   due=False, keep=None, modules=None, onto=None, whole=True):
        """The exit check of every step that writes Lean, on a library put together in stage/<label>/lean.

        The library is the folder `base`, or exactly `files` (path to text), with `replace` written
        over it and `delete` removed. Checked: every file is a module of at most 10,000 lines; each
        definition module has its first bytes; the build of all modules through the run's broker
        succeeds. With `extract` the build includes the extraction, and the index is checked: the root's
        statement, complete proofs from the allowed axioms, names that differ only in case, and
        `canon.check_applied`, with the records when they are `due`. `records` are the records whose
        claims of another proof the extraction asks Lean about. `modules` with `onto` extracts only
        those modules into the index `onto`, and without `whole` the checks of the index are left to
        the caller, who has a library in which not every theorem is proved. With `keep` the library is
        left in that folder. Returns (problems, index)."""
        stage = self.work / 'stage' / label / 'lean'
        if stage.parent.exists():
            remove_tree(stage.parent)
        if base is not None:
            shutil.copytree(base, stage)
        stage.mkdir(parents=True, exist_ok=True)
        for relative, text in {**(files or {}), **(replace or {})}.items():
            write_text(stage / relative, text)
        for relative in delete:
            (stage / relative).unlink(missing_ok=True)
        try:
            problems = package.lean_form_problems(stage) + package.definition_problems(
                stage, self.work / 'first' / 'lean', self.definitions)
            index = None
            if not problems:
                problems, index = self.build(stage, extract, records, modules, onto)
            if not problems and extract and whole:
                problems = package.index_problems(index, self.root, self.statement_hash, self.allowed,
                                                  records if due else None)
            if not problems and keep is not None:
                (stage / (canon.EXTRACT_MODULE + '.lean')).unlink(missing_ok=True)
                package.copy_tree(stage, keep)
        finally:
            remove_tree(stage.parent)
        self.sessions.event('check', check='library ' + label, problems=[p[:2000] for p in problems])
        return problems, index

    def build(self, stage, extract, records, modules, onto):
        """One build of a staged library through the run's broker; returns (errors, index or None)."""
        names = [module for module, _ in canon.library_modules(stage, self.library)]
        given = {path: record for path, record in (records or {}).items() if not isinstance(record, CanonError)}
        pairs = canon.required_pairs(given) if extract else []
        targets = (modules if modules is not None else names) if extract else []
        failures = 0
        build = None
        while True:
            try:
                self.ensure_broker()
                if build is None:
                    # The runtime's writer shares one buffer among its callers; the paper command holds this lock
                    # around its own use of it, and the steps of this run build from several threads.
                    with paper.WRITING:
                        build = canon.start_build(self.work, stage, self.library, 'finalize', self.expect_mb, targets,
                                                  pairs)
                outcome = canon.wait_build(self.work, build, timeout=BUILD_SECONDS)
                if outcome is not None:
                    break
                failures = 0
            except RuntimeError as error:  # no broker became ready; it is started again and asked again
                failures += 1
                if failures > 5:
                    return [f'the Lean broker of the run does not stay alive: {error}'], None
                time.sleep(BROKER_SECONDS)
            except ValueError as error:  # the library cannot be built as it stands: no module, a file outside the root
                return [str(error)], None
        if not outcome['ok']:
            return [f"{e['module']}: {e['status']}" + (f" ({e['reason']})" if e.get('reason') else '')
                    + (f", exit code {e['exit_code']}" if e.get('exit_code') else '') + ('\n' + e['output'] if e['output'] else '')
                    for e in outcome['errors']], None
        if not extract:
            return [], None
        return [], canon.update_index(onto if onto is not None else canon.empty_index(), outcome['rows'],
                                      outcome['pairs'], stage, 0, modules=targets)

    # -- stage 0: start ---------------------------------------------------------------------------------

    def start(self):
        """Stage 0: the refusals, and for a new run the pinned research, the settings and the seeded cache."""
        if not NAME.fullmatch(self.name):
            raise Refusal(f'the name {self.name!r} does not name a package: lower-case letters, digits and hyphens, '
                          'beginning with a letter or a digit')
        instance = self.instance
        if not ((instance / 'instance.json').is_file() and (instance / 'canon').is_dir() and (instance / '.git').exists()):
            raise Refusal(f'{instance} is not an instance of this runtime with a Git repository of its own')
        licence = SKILL / 'finalize' / 'licences' / (self.config['licence'] + '.txt')
        if not licence.is_file():
            raise Refusal(f"the skill has no licence text for {self.config['licence']}: {licence} is missing")
        try:
            import yaml  # noqa: F401
        except ImportError:
            # The check of the registry's files at the freeze reads formalization.yaml back with it.
            raise Refusal('this Python has no PyYAML (the module `yaml`), with which the freeze reads '
                          'formalization.yaml back; install it and start again')
        identity = hashlib.sha256(json.dumps(self.config, sort_keys=True).encode('utf-8')).hexdigest()
        if (self.work / 'state.json').is_file():
            self.state = read_json(self.work / 'state.json')
            run = self.state['run']
            differing = [name for name, value in (('instance', str(instance)), ('name', self.name), ('configuration', identity))
                         if run[{'configuration': 'config'}.get(name, name)] != value]
            try:
                package.git_run(instance, 'cat-file', '-e', run['commit'] + '^{commit}')
            except CanonError:
                differing.append('pinned commit')
            if differing:
                raise Refusal(f'{self.work} holds a run that differs from this one in: ' + ', '.join(differing)
                              + '; continue it with its own arguments, or remove the folder to begin anew')
            if self.solved.exists() and not ('6-check' in self.state['steps'] and not self.package.exists()):
                raise Refusal(f'{self.solved} exists')
            self.settings = validate(read_json(self.work / 'settings.json'))
            self.sessions = Sessions(self.work, self.work, self.config['parallel'], gate=self.gate)
            self.sessions.event('resume', steps=list(self.state['steps']))
            return
        if self.solved.exists():
            raise Refusal(f'{self.solved} exists')
        try:
            settings = validate(read_json(instance / 'settings.json'))
        except (OSError, ValueError) as error:
            raise Refusal(f"the settings of the instance are not valid: {error}")
        reduced = package.reduced_settings(settings)
        self.settings = validate(reduced)
        try:
            if paper.tex_recipe(self.config['tex']) is None:
                raise Refusal('no TeX command is available: none of ' + ', '.join(paper.ENGINES)
                              + ' is on PATH, and the configuration names none')
            paper.load_collection()
        except Stop as error:
            raise Refusal(str(error))
        try:
            commit = package.head_commit(instance)
            first = package.first_commit(instance, commit)
        except CanonError as error:
            raise Refusal(f'the repository of the instance cannot be read: {error}')
        if self.work.exists():
            remove_tree(self.work)  # what a refused start left; a run that began has state.json
        source = self.work / 'source'
        package.export_commit(instance, commit, ['canon', 'knowledge', 'root.md', 'instance.json'], source)
        write_json(self.work / 'settings.json', reduced)
        write_json(source / 'settings.json', reduced)  # replay reads the allowed axioms beside the canon
        try:
            model = knowledge.replay(source)
        except (OSError, ValueError, KeyError) as error:
            raise Refusal(f'the research at the commit {commit[:12]} cannot be read: {error}')
        if model['root_state'] == 'formal_refuted':
            raise Refusal('the root is formally refuted; the packaging of a refutation is not built')
        if model['root_state'] != 'formal_proved':
            raise Refusal(f"the root is {model['root_state']} at the commit {commit[:12]}; a research is packaged once "
                          'its root is proved formally')
        lean = self.settings['lean']
        try:
            done = subprocess.run(lean['version_command'], cwd=lean['cwd'] or None, env={**os.environ, **lean['env']},
                                  stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                  timeout=300, **popen_options())
            version = done.stdout.decode('utf-8', errors='replace').strip()
            if done.returncode:
                raise OSError(f'exit code {done.returncode}: {version}')
        except (OSError, subprocess.SubprocessError) as error:
            raise Refusal(f'the Lean environment does not answer its version command: {error}')
        meta = read_json(source / 'instance.json')
        package.export_commit(instance, first, ['canon/index.json', 'canon/lean'], self.work / 'first', strip='canon/')
        root_module = canon.read_index(source / 'canon' / 'index.json')['entries'][meta['root']]['module']
        definitions = package.definition_modules(self.work / 'first' / 'lean', meta['library'], root_module)
        cache = instance / 'runner' / 'lean' / 'cache'
        if cache.is_dir():
            shutil.copytree(cache, self.work / 'runner' / 'lean' / 'cache', dirs_exist_ok=True)
        measured = package.challenge_measure(package.challenge_text(self.work / 'first' / 'lean', definitions, root_module))
        self.state = {'run': {'instance': str(instance), 'name': self.name, 'commit': commit, 'first': first,
                              'config': identity},
                      'definitions': definitions, 'root_module': root_module, 'version': version, 'measured': measured,
                      'main': None, 'accepted': {},
                      'steps': {'0-start': {'products': {name: package.product_hash(self.work / name)
                                                         for name in ('source', 'first', 'settings.json')}, 'read': {}}}}
        self.save()
        self.sessions = Sessions(self.work, self.work, self.config['parallel'], gate=self.gate)
        self.sessions.event('start', instance=str(instance), commit=commit, first=first, definitions=definitions,
                            version=version, measured=measured)
        self.decide('Stage 0: start', f'The research is read at the commit `{commit}`, the head of the instance\'s '
                    f'repository when the run began. The definition modules are: ' + ', '.join(definitions) + '.')

    def load(self):
        """The values every stage uses, from the pinned research and the state."""
        meta = read_json(self.work / 'source' / 'instance.json')
        self.library, self.root, self.statement_hash = meta['library'], meta['root'], meta['root_statement_hash']
        self.allowed = self.settings['lean']['allowed_axioms']
        self.expect_mb = self.settings['lean']['calibration_expect_mb']
        self.definitions = self.state['definitions']
        self.account = package.account_name()

    def posed(self):
        """The first line of a file that a session reads the library by: which modules stay as they were posed."""
        return ('The definition modules are ' + ', '.join(f'`{module}`' for module in self.definitions)
                + f"; the root's module is `{self.state['root_module']}`.\n\n")

    # -- stage 1: selection -----------------------------------------------------------------------------

    def selection(self):
        source = self.work / 'source'
        index = canon.read_index(source / 'canon' / 'index.json')
        model = knowledge.replay(source)
        bibliography = package.read_text(source / 'canon' / 'bibliography.bib') \
            if (source / 'canon' / 'bibliography.bib').is_file() else ''
        files = {'digest.md': self.posed() + package.selection_digest(model, index),
                 'root.md': (source / 'root.md').read_bytes(),
                 'index.json': as_json(index),
                 **tree('canon/', source / 'canon', ('lean', 'records', 'questions', 'approaches', 'bibliography.bib'))}
        check = lambda output: self.read_decision(output, index, model, bibliography)
        chosen = self.task('selection', 'selection', files, check, self.sessions.writer)

        def read_reading(output):
            data = Sessions.load(output / 'reading.json')
            claims = data.get('claims')
            ids = {option['id'] for option in chosen['decision']['options']}
            problems = []
            if not isinstance(claims, list):
                raise Unusable(['"claims" in reading.json is an array'])
            for number, claim in enumerate(claims, 1):
                if not isinstance(claim, dict) or claim.get('option') not in ids or not is_text(claim.get('claim')):
                    problems.append(f'claim {number} names an option of the decision and gives the claim')
                elif type(claim.get('holds')) is not bool:
                    problems.append(f'claim {number} has no verdict: "holds" is true or false')
                elif not claim['holds'] and (not is_text(claim.get('correction'))
                                             or type(claim.get('changes_comparison')) is not bool
                                             or type(claim.get('printed')) is not bool):
                    problems.append(f'claim {number} does not hold and gives no correction, or does not say whether the '
                                    'correction changes a ground of the comparison ("changes_comparison"), or whether '
                                    'the claim stands in a text that the package prints ("printed")')
            if problems:
                raise Unusable(problems)
            return data

        given = {**files, 'decision.json': as_json(chosen['decision']),
                 **{f'derivations/{oid}.lean': text for oid, text in chosen['derivations'].items()}}
        reading = self.task('selection-read', 'selection-read', given, read_reading, self.sessions.assessor)
        wrong = [claim for claim in reading['claims'] if not claim['holds']]
        # The sentence and the registry's texts go into the package as the decision has them, and no later step
        # rewrites them: a corrected claim there is acted on by a decision made once more, as a changed ground is.
        if any(claim['changes_comparison'] or claim.get('printed') for claim in wrong):
            again = {**files, 'reading.json': as_json(reading), 'previous/decision.json': as_json(chosen['decision']),
                     **{f'previous/derivations/{oid}.lean': text for oid, text in chosen['derivations'].items()}}
            chosen = self.task('selection', 'selection', again, check, self.sessions.writer, label='again')
        decision = chosen['decision']
        option = next(o for o in decision['options'] if o['id'] == decision['choice'])
        target = self.work / 'lib' / '0-selected'
        shutil.copytree(source / 'canon' / 'lean', target / 'lean')
        derivation = chosen['derivations'].get(option['id'])
        if derivation is not None:
            write_text(target / 'lean' / module_file(self.state['root_module']), derivation)
        if (source / 'canon' / 'records').is_dir():
            shutil.copytree(source / 'canon' / 'records', target / 'records')
        else:
            (target / 'records').mkdir()
        write_text(target / 'bibliography.bib', bibliography)
        write_json(target / 'index.json', chosen['index'])
        write_json(target / 'decision.json', decision)
        write_json(target / 'reading.json', reading)
        with self.lock:
            self.state['main'] = option['main']
        lines = [f"The main theorem is `{option['main']}` (option {option['id']}"
                 + (', with the root derived from it by a module the program compiled' if derivation is not None else '')
                 + f"). {decision['reasons'].strip()}", '', 'The options compared:']
        lines += [f"- {o['id']}: `{o['main']}`. For: {o['for'].strip()} Against: {o['against'].strip()}"
                  for o in decision['options']]
        lines += ['', 'The runner-up: ' + (decision.get('runner_up') or 'none, there was one option') + '.']
        lines += [f"- The independent reading corrected a claim about option {c['option']}: {c['correction'].strip()}"
                  + (' This changed a ground of the comparison, and the selection decided once more.'
                     if c['changes_comparison'] else
                     ' The claim stood in a text that the package prints, and the selection decided once more.'
                     if c.get('printed') else '') for c in wrong]
        registry = decision['registry']
        lines += ['', f"For the registry the result is recorded as {registry['origin']}. "
                  + registry.get('novelty', '').strip()]
        self.decide('Stage 1: selection', '\n'.join(lines))

    def read_decision(self, output, index, model, bibliography):
        """The exit check of the selection on one output; returns the decision, its derivations and the index of the choice."""
        data = Sessions.load(output / 'decision.json')
        options = data.get('options')
        problems = []
        if not isinstance(options, list) or not options or not all(isinstance(o, dict) for o in options):
            raise Unusable(['"options" in decision.json is a nonempty array of objects'])
        ids = [o.get('id') for o in options]
        if len(set(ids)) != len(ids) or not all(isinstance(i, str) and PART_ID.fullmatch(i) for i in ids):
            raise Unusable(['every option has an "id" of lower-case letters, digits and hyphens, and no two share one'])
        for option in options:
            problems += [f"option {option['id']}: \"{key}\" is empty" for key in
                         ('main', 'route', 'proves', 'rests_on', 'size', 'for', 'against') if not is_text(option.get(key))]
        problems += [f'"{key}" is empty' for key in ('reasons', 'sentence', 'account') if not is_text(data.get(key))]
        if data.get('choice') not in ids:
            problems.append('"choice" names none of the options')
        runner = data.get('runner_up')
        if len(ids) > 1 and (runner not in ids or runner == data.get('choice')):
            problems.append('"runner_up" names another option than the choice; it is absent only when there is one option')
        if len(ids) == 1 and runner is not None:
            problems.append('"runner_up" is null when there is one option')
        registry = data.get('registry')
        if not isinstance(registry, dict):
            problems.append('"registry" is an object with "arxiv", "msc2020", "origin", "sources", '
                            '"related_formalizations", "divergences", "settles", "novelty" and "stated_in"')
        else:
            arxiv, msc = registry.get('arxiv'), registry.get('msc2020')
            if not (isinstance(arxiv, list) and 1 <= len(arxiv) <= 2
                    and all(isinstance(c, str) and package.ARXIV.fullmatch(c) for c in arxiv)):
                problems.append('"registry.arxiv" holds one or two arXiv categories, such as math.CO')
            if not (isinstance(msc, list) and 1 <= len(msc) <= 8
                    and all(isinstance(c, str) and package.MSC.fullmatch(c) for c in msc)):
                problems.append('"registry.msc2020" holds one to eight MSC2020 codes of five characters, such as 05A15')
            if registry.get('origin') not in ('original', 'source-based'):
                problems.append('"registry.origin" is "original" or "source-based"')
            if not is_text(registry.get('divergences')):
                problems.append('"registry.divergences" says where the Lean statement of the root departs from the '
                                'proposition in words, or in a plain sentence that it does not')
            problems += [f'"registry.{key}" says {what}' for key, what in (
                ('settles', 'what the result is, whose conjecture or question it settles and where that was posed, as '
                            'far as root.md and the records say'),
                ('novelty', 'what the research recorded about whether the result was known before, and what it did '
                            'not look into'),
                ('stated_in', 'where each statement of "settles", of "novelty", of the notes and of the earlier '
                              'formalisations stands')) if not is_text(registry.get(key))]
            keys = package.bibliography_keys(bibliography)
            sources = registry.get('sources')
            if not isinstance(sources, list) or not all(
                    isinstance(s, dict) and s.get('key') in keys and s.get('relationship') in package.RELATIONSHIPS
                    and is_text(s.get('note')) for s in sources):
                problems.append('"registry.sources" gives, for sources of the bibliography by their keys, a relationship '
                                'of ' + ', '.join(package.RELATIONSHIPS) + ', and a note that says what the source '
                                'has of the result and where')
            related = registry.get('related_formalizations')
            if not isinstance(related, list) or not all(
                    isinstance(r, dict) and is_text(r.get('id')) and r.get('relationship') in package.RELATED
                    and is_text(r.get('note')) for r in related):
                problems.append('"registry.related_formalizations" is an array, empty when root.md and the records '
                                'name no earlier formalisation; each entry has an "id", a "relationship" of '
                                + ', '.join(package.RELATED) + ', and a "note"')
        if problems:
            raise Unusable(problems)
        elements, entries = model['elements'], index['entries']
        derivations, indexes, eligible = {}, {}, []
        for option in options:
            main = option['main']
            if main not in elements or elements[main]['kind'] != 'theorem' or not (
                    elements[main]['settled'] and elements[main]['formal']):
                problems.append(f"option {option['id']}: {main} is not a settled formal theorem of the canon")
                continue
            path = output / 'derivations' / (option['id'] + '.lean')
            if path.is_file():
                text = package.read_text(path)
                relative = module_file(self.state['root_module'])
                found, derived = self.library_ok(f"{output.parent.name}-{option['id']}", base=self.work / 'source' / 'canon' / 'lean',
                                                 replace={relative: text}, extract=True,
                                                 modules=[self.state['root_module']], onto=index, whole=False)
                if not found:
                    root = derived['entries'].get(self.root)
                    if root is None or root['kind'] != 'theorem' or root['statement_hash'] != self.statement_hash:
                        found = ['the root does not have the statement the instance fixed']
                    elif canon.beyond_allowed(root, self.allowed):
                        found = ['the root is not proved from the allowed axioms: '
                                 + ', '.join(canon.beyond_allowed(root, self.allowed))]
                    elif main not in package.rests_from(derived, self.root):
                        found = [f'the root does not rest on {main} in this derivation']
                if found:
                    problems.append(f"option {option['id']}: its derivation is not accepted: " + '; '.join(found))
                    continue
                derivations[option['id']], indexes[option['id']] = text, derived
            elif option['route'] != 'present':
                problems.append(f"option {option['id']}: its route is not the root's present proof, and "
                                f"derivations/{option['id']}.lean was not written")
                continue
            elif canon.beyond_allowed(entries[self.root], self.allowed) or main not in package.rests_from(index, self.root):
                problems.append(f"option {option['id']}: without a derivation an option is eligible when the root's own "
                                f'declaration is proved from the allowed axioms and rests on {main}')
                continue
            else:
                indexes[option['id']] = index
            eligible.append(option['id'])
        if data['choice'] not in eligible:
            raise Unusable(problems + ['the choice is not eligible; the eligible options are: '
                                       + (', '.join(eligible) or 'none')])
        return {'decision': data, 'derivations': derivations, 'index': indexes[data['choice']]}

    # -- stage 2, step 1: the take ----------------------------------------------------------------------

    def take(self):
        selected, target = self.work / 'lib' / '0-selected', self.work / 'lib' / '1-taken'
        index = read_json(selected / 'index.json')
        plan = package.take(index, selected / 'lean', self.library, self.root, self.definitions,
                            self.settings['lean']['allowed_axioms'])
        files, back = plan['files'], []
        problems, _ = self.library_ok('take', files=files)
        if problems:
            before = {relative: package.read_text(selected / 'lean' / relative) for relative in files}
            given = {**{'lean/' + relative: text for relative, text in files.items()},
                     **{'before/' + relative: text for relative, text in before.items()},
                     'removed.json': as_json([{'declaration': item['declaration'], 'file': item['file']}
                                              for item in plan['spans']]),
                     'errors.txt': '\n\n'.join(problems) + '\n'}

            def read(output):
                returned = {relative: package.read_text(path)
                            for relative, path in package.files_under(output / 'lean').items()}
                if not returned:
                    raise Unusable(['no file was written under output/lean'])
                again, texts, bad = package.restored_files(plan['spans'], before, returned)
                if bad:
                    raise Unusable(bad)
                merged = {**files, **texts}
                found, _ = self.library_ok('take-' + output.parent.name, files=merged)
                if found:
                    raise Unusable(['the library does not build with these elements put back:'] + found)
                return again, merged

            back, files = self.task('restore', 'restore', given, read, self.sessions.writer)
            self.decide('Step 1: the take', 'The library did not build after the take, and these removed elements were '
                        'put back: ' + ', '.join(f'`{name}`' for name in back) + '.')
        for relative, text in files.items():
            write_text(target / 'lean' / relative, text)
        kept = sorted(set(plan['kept']) | set(back))
        (target / 'records').mkdir(parents=True, exist_ok=True)
        for name in kept:
            record = selected / 'records' / (name_path(name) + '.md')
            if record.is_file():
                (target / 'records' / (name_path(name) + '.md')).parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(record, target / 'records' / (name_path(name) + '.md'))
        shutil.copyfile(selected / 'bibliography.bib', target / 'bibliography.bib')
        write_json(target / 'taken.json', {'kept': kept, 'removed': sorted(set(plan['removed']) - set(back)),
                                           'restored': back, 'modules': plan['modules'], 'deleted': plan['deleted'],
                                           'definitions': self.definitions})
        self.decide('Step 1: the take', f"Kept {len(kept)} elements in {len(plan['modules'])} modules; removed "
                    f"{len(plan['removed']) - len(back)} elements that the chosen theorem and the root do not rest on, and "
                    f"{len(plan['deleted'])} modules that no kept module imports.")

    # -- stage 2, steps 2 to 4: review, simplify, merge, arrange ----------------------------------------

    def review(self):
        taken = self.work / 'lib' / '1-taken'
        index = read_json(self.work / 'lib' / '0-selected' / 'index.json')
        kept = set(read_json(taken / 'taken.json')['kept'])
        modules = {module for module, _ in canon.library_modules(taken / 'lean', self.library)} - set(self.definitions)
        files = {**tree('lean/', taken / 'lean'), **tree('records/', taken / 'records'),
                 'rests-on.md': self.posed() + package.rests_on_text(index, kept)}

        def read(output):
            data = Sessions.load(output / 'review.json')
            parts, cross = data.get('parts'), data.get('cross', [])
            if not isinstance(parts, list) or not parts or not all(
                    isinstance(p, dict) and isinstance(p.get('id'), str) and PART_ID.fullmatch(p['id'])
                    and isinstance(p.get('modules'), list) for p in parts):
                raise Unusable(['"parts" is a nonempty array; each part has an "id" of lower-case letters, digits and '
                                'hyphens and its "modules"'])
            ids = [p['id'] for p in parts]
            listed = [module for p in parts for module in p['modules']]
            problems = []
            if len(set(ids)) != len(ids):
                problems.append('two parts have the same id')
            twice = sorted({module for module in listed if listed.count(module) > 1})
            if twice:
                problems.append('modules in more than one part: ' + ', '.join(twice))
            if set(listed) - modules:
                problems.append('not modules of the library outside the definition modules: '
                                + ', '.join(sorted(set(listed) - modules)))
            if modules - set(listed):
                problems.append('modules in no part: ' + ', '.join(sorted(modules - set(listed))))
            if not isinstance(cross, list) or not all(isinstance(c, dict) and is_text(c.get('id')) and is_text(c.get('what'))
                                                      for c in cross):
                problems.append('"cross" is an array of items with "id", "owner" and "what"')
            else:
                if len({c['id'] for c in cross}) != len(cross):
                    problems.append('two cross-part items have the same id')
                problems += [f"the cross-part item {c['id']} has no owner that is a part" for c in cross
                             if c.get('owner') not in ids]
            if problems:
                raise Unusable(problems)
            return {'parts': parts, 'cross': cross}

        data = self.task('review', 'review', files, read, self.sessions.writer)
        write_json(self.work / 'lib' / '2-review' / 'review.json', data)

    def simplify(self):
        taken = self.work / 'lib' / '1-taken' / 'lean'
        review = read_json(self.work / 'lib' / '2-review' / 'review.json')
        kept = set(read_json(self.work / 'lib' / '1-taken' / 'taken.json')['kept'])
        index = {'entries': {name: entry for name, entry in
                             read_json(self.work / 'lib' / '0-selected' / 'index.json')['entries'].items() if name in kept}}
        library = tree('lean/', taken)
        target = self.work / 'lib' / '3-parts'

        def simplify(part):
            owned = [c for c in review['cross'] if c['owner'] == part['id']]
            given = {**library, 'part.json': as_json({
                'id': part['id'], 'title': part.get('title', ''), 'modules': part['modules'], 'inside': part.get('inside', ''),
                'interface': package.interface(index, part['modules']),
                'cross': [{'id': c['id'], 'what': c['what']} for c in owned]})}

            def read(output):
                files, deleted, problems = package.part_output(output, taken, lambda m: m in part['modules'], self.definitions)
                report = Sessions.load(output / 'report.json')
                answered = {c.get('id'): c for c in report.get('cross', []) if isinstance(c, dict)}
                problems += [f"report.json does not say whether the cross-part item {c['id']} is done" for c in owned
                             if type(answered.get(c['id'], {}).get('done')) is not bool]
                if not problems and (files or deleted):
                    problems, _ = self.library_ok('part-' + output.parent.name, base=taken, replace=files, delete=deleted)
                if problems:
                    raise Unusable(problems)
                return {'files': files, 'deleted': deleted, 'report': report}

            return self.discardable(f"Step 3: the simplification of the part {part['id']}", lambda: self.task(
                'simplify', 'simplify', given, read, self.sessions.writer, label=part['id'], names={'part': part['id']}))

        results = self.sessions.side_by_side([lambda part=part: simplify(part) for part in review['parts']])
        summary = {'accepted': [], 'discarded': []}
        target.mkdir(parents=True, exist_ok=True)
        for part, result in zip(review['parts'], results):
            if result is None:
                summary['discarded'].append(part['id'])
                continue
            summary['accepted'].append(part['id'])
            for relative, text in result['files'].items():
                write_text(target / part['id'] / 'lean' / relative, text)
            write_json(target / part['id'] / 'report.json', {**result['report'], 'deleted': result['deleted']})
        write_json(target / 'parts.json', summary)

    def merge_parts(self, what, label, base, parts, records, keep):
        """Put accepted parts together and build with the extraction; when that fails, add them one at a time.

        `parts` are (id, files, deleted) in the order they are added. A part that touches a file an
        earlier part touched, or whose addition does not build, is discarded and the fact recorded.
        Returns (index, the ids merged, the ids discarded)."""
        merged, discarded, replace, delete = [], [], {}, []
        for pid, files, deleted in parts:
            if (set(files) | set(deleted)) & (set(replace) | set(delete)):
                discarded.append(pid)
                self.decide(what, f'The part {pid} was discarded: it changes a file that an earlier part changed.')
                continue
            merged.append(pid)
            replace.update(files)
            delete += deleted
        problems, index = self.library_ok(label, base=base, replace=replace, delete=delete, extract=True,
                                          records=records, keep=keep)
        if problems and merged:
            candidates, merged, replace, delete = merged, [], {}, []
            by_id = {pid: (files, deleted) for pid, files, deleted in parts}
            for pid in candidates:
                files, deleted = by_id[pid]
                found, _ = self.library_ok(f'{label}-{pid}', base=base, replace={**replace, **files},
                                           delete=delete + deleted)
                if found:
                    discarded.append(pid)
                    self.decide(what, f'The part {pid} was discarded: the library does not build with it added. '
                                + found[0][:600])
                else:
                    merged.append(pid)
                    replace.update(files)
                    delete += deleted
            problems, index = self.library_ok(label, base=base, replace=replace, delete=delete, extract=True,
                                              records=records, keep=keep)
        if problems:
            raise Stop('the merged library does not pass its check: ' + '; '.join(problems))
        return index, merged, discarded

    def part_files(self, folder):
        """What an accepted part left in its folder: its files by path under lean/, and the files it deleted."""
        files = {relative: package.read_text(path) for relative, path in package.files_under(folder / 'lean').items()}
        return files, read_json(folder / 'report.json').get('deleted', [])

    def merge(self):
        taken, parts = self.work / 'lib' / '1-taken', self.work / 'lib' / '3-parts'
        target = self.work / 'lib' / '4-merged'
        accepted = read_json(parts / 'parts.json')['accepted']
        index, merged, discarded = self.merge_parts(
            'Step 4: the merge', 'merge', taken / 'lean', [(pid, *self.part_files(parts / pid)) for pid in accepted],
            package.read_records(taken / 'records'), target / 'lean')
        write_json(target / 'index.json', index)
        write_json(target / 'merge.json', {'merged': merged, 'discarded': discarded})

    def arrange(self):
        merged, taken = self.work / 'lib' / '4-merged', self.work / 'lib' / '1-taken'
        target = self.work / 'lib' / '4-arranged'
        index = read_json(merged / 'index.json')
        records = package.read_records(taken / 'records')
        parts = self.work / 'lib' / '3-parts'
        files = {**tree('lean/', merged / 'lean'),
                 'review.json': (self.work / 'lib' / '2-review' / 'review.json').read_bytes(),
                 **{f'reports/{pid}.json': (parts / pid / 'report.json').read_bytes()
                    for pid in read_json(merged / 'merge.json')['merged']},
                 'declarations.md': self.posed() + package.declarations_text(index)}

        def read(output):
            texts = {relative: package.read_text(path) for relative, path in package.files_under(output / 'lean').items()}
            renames = Sessions.load(output / 'renames.json')
            removed = [item['declaration'] for item in Sessions.load(output / 'removed.json', list)]
            if not texts:
                raise Unusable(['output/lean holds no file; it holds every file of the library'])
            if not all(isinstance(old, str) and isinstance(new, str) for old, new in renames.items()):
                raise Unusable(['renames.json maps old names to new names'])
            problems, arranged = self.library_ok('arrange-' + output.parent.name, files=texts, extract=True, records=records)
            if not problems:
                now = arranged['entries']
                lost = [name for name in index['entries'] if renames.get(name, name) not in now and name not in removed]
                if lost:
                    problems.append('elements of the merged library that are neither in the arranged library, under '
                                    'their name or their new name, nor among those removed: ' + ', '.join(sorted(lost)))
                if renames.get(self.state['main'], self.state['main']) not in now:
                    problems.append(f"the main theorem {self.state['main']} is not in the arranged library")
            if problems:
                raise Unusable(problems)
            return {'files': texts, 'index': arranged, 'renames': renames, 'removed': removed}

        result = self.discardable('Step 4: the arrangement', lambda: self.task(
            'arrange', 'arrange', files, read, self.sessions.writer))
        if result is None:
            shutil.copytree(merged / 'lean', target / 'lean')
            result = {'index': index, 'renames': {}, 'removed': []}
        else:
            for relative, text in result['files'].items():
                write_text(target / 'lean' / relative, text)
            with self.lock:
                self.state['main'] = result['renames'].get(self.state['main'], self.state['main'])
            if result['renames'] or result['removed']:
                self.decide('Step 4: the arrangement', 'Renamed: ' + (', '.join(
                    f'`{old}` to `{new}`' for old, new in sorted(result['renames'].items())) or 'nothing')
                    + '. Removed: ' + (', '.join(f'`{name}`' for name in result['removed']) or 'nothing') + '.')
        shutil.copytree(taken / 'records', target / 'records')
        package.follow_renames(target / 'records', result['renames'], result['removed'])
        package.drop_orphans(target / 'records', result['index'])
        shutil.copyfile(taken / 'bibliography.bib', target / 'bibliography.bib')
        write_json(target / 'index.json', result['index'])
        write_json(target / 'renames.json', result['renames'])

    # -- stage 2, step 5 and the records of step 6 ------------------------------------------------------

    def bring_records(self, tag, lean, index, base, records_in, bibliography_in, requests, target, earlier=()):
        """Write the records that are due, have each compared by a session that did not write it, and check the sources.

        `base` is the index the lists are made against, `requests` the results the draft asks to cite,
        `earlier` the sources an earlier step verified. The records go to <target>/records, with
        bibliography.bib, findings.json, sources.json, verdicts.json and requests.json beside them."""
        records, bibliography = target / 'records', target / 'bibliography.bib'
        package.copy_tree(records_in, records)
        shutil.copyfile(bibliography_in, bibliography)
        dropped = package.drop_orphans(records, index)
        todo = package.record_todo(index, base, records)
        groups = package.batches(todo, package.WRITER_BATCH, key=lambda item: PurePosixPath(item['file']).parent.as_posix())
        library = tree('lean/', lean)
        reference = SKILL / 'reference'
        confirmed = index.get('pairs', {})

        def parsed(output, item, problems):
            path = output / 'records' / (name_path(item['declaration']) + '.md')
            if not path.is_file():
                problems.append(f"records/{name_path(item['declaration'])}.md was not written")
                return None
            text = package.read_text(path)
            try:
                meta = parse_record(text, path.name)['meta']
            except CanonError as error:
                problems.append(str(error))
                return None
            for key, kind in (('proves', 'same'), ('refutes', 'negation')):
                if meta.get(key) and not confirmed.get(f"{kind}|{item['declaration']}|{meta[key]}"):
                    problems.append(f"{item['declaration']}: \"{key}: {meta[key]}\" is a claim that Lean did not confirm "
                                    'in this library; leave it out')
            return text

        def write(number, group):
            given = {**library, 'todo.json': as_json(group), **tree('records/', records),
                     'bibliography.bib': bibliography.read_bytes(),
                     'records-format.md': (reference / 'records.md').read_bytes(),
                     'user-writing-preferences.md': (reference / 'user-writing-preferences.md').read_bytes()}

            def read(output):
                problems, texts = [], {}
                for item in group:
                    texts[item['declaration']] = parsed(output, item, problems)
                findings = Sessions.load(output / 'findings.json', list)
                names = set(index['entries'])
                problems += [f'finding {n} names a declaration of the library, a kind of ' + ', '.join(FINDING_KINDS)
                             + ' and a detail' for n, f in enumerate(findings, 1)
                             if not (isinstance(f, dict) and f.get('declaration') in names
                                     and f.get('kind') in FINDING_KINDS and is_text(f.get('detail')))]
                if problems:
                    raise Unusable(problems)
                return texts, findings

            return self.task('records-write', 'records-write', given, read, self.sessions.writer, label=f'{tag}-{number}')

        written = self.sessions.side_by_side([lambda n=n, g=g: write(n, g) for n, g in groups])
        findings = []
        for texts, found in written:
            findings += found
            for name, text in texts.items():
                write_text(records / (name_path(name) + '.md'), text)

        def compare(number, group):
            given = {**library, 'todo.json': as_json([{**item, 'record': 'records/' + name_path(item['declaration']) + '.md'}
                                                      for item in group]),
                     **tree('records/', records), 'records-format.md': (reference / 'records.md').read_bytes()}

            def read(output):
                verdicts = {v.get('declaration'): v for v in Sessions.load(output / 'verdicts.json', list)
                            if isinstance(v, dict)}
                problems, texts = [], {}
                for item in group:
                    verdict = verdicts.get(item['declaration'], {}).get('verdict')
                    if verdict not in ('agrees', 'corrected'):
                        problems.append(f"{item['declaration']} has no verdict of \"agrees\" or \"corrected\"")
                    elif verdict == 'corrected':
                        texts[item['declaration']] = parsed(output, item, problems)
                if problems:
                    raise Unusable(problems)
                return [verdicts[item['declaration']] for item in group], texts

            return self.task('records-compare', 'records-compare', given, read, self.sessions.assessor,
                             label=f'{tag}-{number}')

        compared = self.sessions.side_by_side([lambda n=n, g=g: compare(n, g) for n, g in groups])
        verdicts = []
        for found, texts in compared:
            verdicts += found
            for name, text in texts.items():
                write_text(records / (name_path(name) + '.md'), text)

        # A source that an earlier step verified is not verified again, unless a record that cites it is listed now.
        listed = {item['declaration'] for item in todo}
        every = package.cited(records, index)
        cited = [item for item in every if not any(row['key'] == item['key'] and row.get('status') == 'verified'
                                                   for row in earlier)
                 or any(row['declaration'] in listed for row in item['records'])]
        still = [row for row in earlier if row.get('status') == 'verified'
                 and row['key'] in {item['key'] for item in every} - {item['key'] for item in cited}]
        settled = {row['key'] for row in still}
        sources, answers = list(still), []
        if cited or requests:
            given = {'bibliography.bib': bibliography.read_bytes(), 'cited.json': as_json(cited),
                     'requests.json': as_json(requests), **tree('records/', records), **library}

            def read(output):
                rows = {row.get('key'): row for row in Sessions.load(output / 'sources.json', list) if isinstance(row, dict)}
                problems = [f"sources.json has no status of \"verified\" or \"removed\" for {item['key']}" for item in cited
                            if rows.get(item['key'], {}).get('status') not in ('verified', 'removed')]
                problems += [f'{key} is verified without an identifier' for key, row in rows.items()
                             if row.get('status') == 'verified' and not is_text(row.get('identifier'))]
                if not (output / 'bibliography.bib').is_file():
                    raise Unusable(problems + ['output/bibliography.bib was not written'])
                keys = package.bibliography_keys(package.read_text(output / 'bibliography.bib'))
                changed = {}
                for relative, path in package.files_under(output / 'records').items():
                    try:
                        parse_record(package.read_text(path), relative)
                        changed[relative] = package.read_text(path)
                    except CanonError as error:
                        problems.append(str(error))
                paths = {name_path(name) + '.md': name for name in index['entries']}
                problems += [f'records/{relative} belongs to no declaration of the library' for relative in changed
                             if relative not in paths]
                for name in index['entries']:
                    relative = name_path(name) + '.md'
                    text = changed.get(relative) or (package.read_text(records / relative)
                                                     if (records / relative).is_file() else None)
                    if text is None:
                        continue
                    try:
                        key = parse_record(text, relative)['meta'].get('source')
                    except CanonError:
                        continue
                    if key and (key not in keys or (key not in settled and rows.get(key, {}).get('status') != 'verified')):
                        problems.append(f'the record of {name} cites {key}, which is not a verified entry of the '
                                        'returned bibliography')
                answered = Sessions.load(output / 'requests.json', list) if requests else []
                by_name = {a.get('declaration'): a for a in answered if isinstance(a, dict)}
                problems += [f"requests.json does not say whether a source was found for {r['declaration']}"
                             for r in requests if type(by_name.get(r['declaration'], {}).get('found')) is not bool]
                if problems:
                    raise Unusable(problems)
                return list(rows.values()), package.read_text(output / 'bibliography.bib'), changed, answered

            found, text, changed, answers = self.task('sources', 'sources', given, read, self.sessions.assessor,
                                                      label=tag, servers=self.settings['mcp_servers'])
            sources += found
            write_text(bibliography, text)
            for relative, content in changed.items():
                write_text(records / relative, content)
            gone = [row['key'] for row in sources if row.get('status') == 'removed']
            if gone:
                self.decide(f'Step {tag}: the sources', 'Removed from the bibliography, because the source could not be '
                            'found or does not state what the records said of it: ' + ', '.join(gone) + '.')
        write_json(target / 'findings.json', findings)
        write_json(target / 'sources.json', sources)
        write_json(target / 'verdicts.json', verdicts)
        write_json(target / 'requests.json', answers)
        # The exit check.
        current = package.read_records(records)
        problems = package.index_problems(index, self.root, self.statement_hash, self.allowed, current)
        judged = {verdict['declaration'] for verdict in verdicts}
        problems += [f"the record of {item['declaration']} was listed and has no verdict" for item in todo
                     if item['declaration'] not in judged]
        keys = package.bibliography_keys(package.read_text(bibliography))
        verified = {row['key'] for row in sources if row.get('status') == 'verified'}
        problems += [f"the record of {row['declaration']} cites {item['key']}, which is not verified in the bibliography"
                     for item in package.cited(records, index) for row in item['records']
                     if item['key'] not in keys or item['key'] not in verified]
        if problems:
            raise Stop('the records do not pass their check: ' + '; '.join(problems))
        if dropped:
            self.decide(f'Step {tag}: the records', 'The records of declarations the library no longer has were deleted: '
                        + ', '.join(f'`{name}`' for name in dropped) + '.')
        return findings

    def records(self):
        arranged = self.work / 'lib' / '4-arranged'
        self.bring_records('5', arranged / 'lean', read_json(arranged / 'index.json'),
                           read_json(self.work / 'lib' / '0-selected' / 'index.json'), arranged / 'records',
                           arranged / 'bibliography.bib', [], self.work / 'lib' / '5-records')

    # -- stage 2, step 6: draft and fold-back -----------------------------------------------------------

    def draft(self):
        arranged, records = self.work / 'lib' / '4-arranged', self.work / 'lib' / '5-records'
        decision = read_json(self.work / 'lib' / '0-selected' / 'decision.json')
        view = package.make_view(self.work / 'view' / '4', arranged / 'lean', records / 'records',
                                 records / 'bibliography.bib', read_json(arranged / 'index.json'),
                                 self.work / 'source', self.settings, decision['account'])
        code = self.paper_run(view, self.work / 'draft', draft=True, main=self.paper_main())
        lacking = [name for name in ('plan.json', 'study.md', 'draft.json') if not (self.work / 'draft' / name).is_file()]
        if code != 0 or lacking:
            raise Stop(f'the paper command did not make the draft: exit code {code}'
                       + ('; missing: ' + ', '.join(lacking) if lacking else ''))
        draft = read_json(self.work / 'draft' / 'draft.json')
        if not all(isinstance(draft.get(key), list) for key in ('statements', 'formulas', 'gaps', 'citations')):
            raise Stop('draft.json does not hold "statements", "formulas", "gaps" and "citations"')

    def foldback(self):
        arranged, folded = self.work / 'lib' / '4-arranged', self.work / 'lib' / '6-folded'
        index = read_json(arranged / 'index.json')
        entries = index['entries']
        draft = read_json(self.work / 'draft' / 'draft.json')
        items = [{'id': gap['id'], 'from': 'draft', 'declaration': gap['element'], 'kind': gap['kind'],
                  'detail': f"{gap['reason']} What the library has: {gap['has']}", 'wanted': gap['wanted']}
                 for gap in draft['gaps']]
        items += [{'id': f'r{number}', 'from': 'records', 'declaration': finding['declaration'], 'kind': finding['kind'],
                   'detail': finding['detail']}
                  for number, finding in enumerate(read_json(self.work / 'lib' / '5-records' / 'findings.json'), 1)]
        by_part, outcome = {}, []
        for item in items:
            entry = entries.get(item['declaration'])
            if entry is None or entry['module'] in self.definitions:
                outcome.append({**item, 'part': None, 'closed': False, 'declarations': [],
                                'note': 'the declaration it concerns is in no part: it is not in the library, or it '
                                        'stands in a definition module, which stays as it was posed'})
            else:
                by_part.setdefault(package.folder_of(entry['module']), []).append(item)
        modules = [module for module, _ in canon.library_modules(arranged / 'lean', self.library)]
        library, records = tree('lean/', arranged / 'lean'), tree('records/', self.work / 'lib' / '5-records' / 'records')
        target = self.work / 'lib' / '6-parts'

        def fold(part, given_items):
            inside = lambda module: package.folder_of(module) == part
            given = {**library, **records, 'items.json': as_json(given_items), 'part.json': as_json({
                'id': part, 'title': part, 'modules': [m for m in modules if inside(m) and m not in self.definitions],
                'inside': '', 'interface': package.interface(index, [m for m in modules if inside(m)]), 'cross': []})}

            def read(output):
                files, deleted, problems = package.part_output(output, arranged / 'lean', inside, self.definitions, inside)
                report = Sessions.load(output / 'report.json')
                answers = {a.get('id'): a for a in report.get('items', []) if isinstance(a, dict)}
                for item in given_items:
                    answer = answers.get(item['id'], {})
                    if type(answer.get('closed')) is not bool:
                        problems.append(f"report.json does not say whether the item {item['id']} is closed")
                    elif answer['closed'] and not (isinstance(answer.get('declarations'), list) and answer['declarations']):
                        problems.append(f"the item {item['id']} is closed and report.json names no declaration that closes it")
                    elif not answer['closed'] and not is_text(answer.get('note')):
                        problems.append(f"the item {item['id']} is not closed and report.json gives no reason")
                if not problems and (files or deleted):
                    problems, _ = self.library_ok('fold-' + output.parent.name, base=arranged / 'lean', replace=files,
                                                  delete=deleted)
                if problems:
                    raise Unusable(problems)
                return {'files': files, 'deleted': deleted, 'report': report}

            return self.discardable(f'Step 6: the fold-back of the part {part}', lambda: self.task(
                'foldback', 'foldback', given, read, self.sessions.writer, label=part.replace('.', '-'), names={'part': part}))

        parts = sorted(by_part)
        results = self.sessions.side_by_side([lambda part=part: fold(part, by_part[part]) for part in parts])
        accepted = []
        target.mkdir(parents=True, exist_ok=True)
        for part, result in zip(parts, results):
            if result is None:
                continue
            label = part.replace('.', '-')
            for relative, text in result['files'].items():
                write_text(target / label / 'lean' / relative, text)
            write_json(target / label / 'report.json', {**result['report'], 'deleted': result['deleted']})
            accepted.append((part, result))
        if accepted:
            new, merged, discarded = self.merge_parts(
                'Step 6: the fold-back', 'fold', arranged / 'lean',
                [(part, result['files'], result['deleted']) for part, result in accepted],
                package.read_records(self.work / 'lib' / '5-records' / 'records'), folded / 'lean')
        else:
            # Nothing changed, so the library and its index are those of step 4, and nothing is built for them.
            shutil.copytree(arranged / 'lean', folded / 'lean')
            new, merged, discarded = index, [], []
        reports = {part: result['report'] for part, result in accepted}
        for part in parts:
            for item in by_part[part]:
                answer = next((a for a in reports.get(part, {}).get('items', []) if a.get('id') == item['id']), None)
                closes = [name for name in (answer or {}).get('declarations', []) if name in new['entries']]
                closed = bool(part in merged and answer and answer['closed'] and closes)
                outcome.append({**item, 'part': part, 'closed': closed, 'declarations': closes if closed else [],
                                'note': (answer or {}).get('note', '') if part in merged else
                                'the part was discarded, so the library keeps the form it had'})
        write_json(folded / 'index.json', new)
        write_json(folded / 'foldback.json', {'items': outcome, 'merged': merged, 'discarded': discarded})
        lines = [f"- {item['id']} ({item['from']}, `{item['declaration']}`): "
                 + ('closed by ' + ', '.join(f'`{name}`' for name in item['declarations']) if item['closed']
                    else 'not closed') + (f". {item['note'].strip()}" if item['note'].strip() else '') for item in outcome]
        self.decide('Step 6: the fold-back', '\n'.join(lines) or 'Nothing was to be folded back.')

    def records_again(self):
        folded, arranged = self.work / 'lib' / '6-folded', self.work / 'lib' / '4-arranged'
        index = read_json(folded / 'index.json')
        draft = read_json(self.work / 'draft' / 'draft.json')
        requests = [{'declaration': c['element'], 'result': c['result'], 'reason': c['reason']}
                    for c in draft['citations'] if c['element'] in index['entries']]
        late = self.bring_records('6', folded / 'lean', index, read_json(arranged / 'index.json'),
                                  self.work / 'lib' / '5-records' / 'records',
                                  self.work / 'lib' / '5-records' / 'bibliography.bib', requests, folded,
                                  read_json(self.work / 'lib' / '5-records' / 'sources.json'))
        answers = read_json(folded / 'requests.json')
        if requests:
            self.decide('Step 6: the sources the draft asked for', '\n'.join(
                f"- `{a['declaration']}`: " + (f"cited from {a.get('key')}" if a.get('found') else 'no source found that '
                                               'states it in the form the library has; the paper proves it')
                + (f". {a['note'].strip()}" if is_text(a.get('note')) else '') for a in answers))
        if late:
            self.decide('Step 6: the records', 'The writers of the records of what the fold-back changed reported '
                        f'{len(late)} further findings. The fold-back is one pass, so they stand in '
                        'lib/6-folded/findings.json and the library was not changed for them.')

    def compare_draft(self):
        folded, target = self.work / 'lib' / '6-folded', self.work / 'lib' / '6-draft'
        index, before = read_json(folded / 'index.json'), read_json(self.work / 'lib' / '4-arranged' / 'index.json')
        entries = index['entries']
        draft = read_json(self.work / 'draft' / 'draft.json')
        closed = {item['id']: item['declarations'][0] for item in read_json(folded / 'foldback.json')['items']
                  if item['closed']}
        gaps = {gap['id']: gap for gap in draft['gaps']}

        def changed(name):
            return name is not None and (name not in entries or name not in before['entries']
                                         or entries[name]['source_sha'] != before['entries'][name]['source_sha'])

        def row(rid, kind, item, text, declaration):
            declaration = declaration if declaration in entries else None
            record = folded / 'records' / (name_path(declaration) + '.md') if declaration else None
            lean = canon.declaration_text(package.read_text(folded / 'lean' / entries[declaration]['file']),
                                          entries[declaration]['span']) if declaration else ''
            return {'id': rid, 'kind': kind, 'label': item.get('label'), 'section': item.get('section'), 'draft': text,
                    'declaration': declaration, 'lean': lean,
                    'record': package.read_text(record) if record and record.is_file() else ''}

        rows, placed = [], set()
        for kind, prefix, listed in (('statement', 's:', draft['statements']), ('formula', 'f:', draft['formulas'])):
            for item in listed:
                gap = item.get('gap')
                if gap:
                    placed.add(gap)
                    rows.append(row(gap, kind, item, item['text'], closed.get(gap) or item.get('element')))
                elif changed(item.get('element')):
                    rows.append(row(prefix + item['label'], kind, item, item['text'], item['element']))
        rows += [row(gid, gap['kind'], gap, gap['wanted'], closed.get(gid)) for gid, gap in gaps.items() if gid not in placed]
        verdicts = []
        if rows:
            given = {'rows.json': as_json(rows), **tree('lean/', folded / 'lean'), **tree('records/', folded / 'records')}

            def read(output):
                found = {v.get('id'): v for v in Sessions.load(output / 'verdicts.json', list) if isinstance(v, dict)}
                problems = []
                for item in rows:
                    verdict = found.get(item['id'], {})
                    if verdict.get('verdict') not in ('same', 'rewritten', 'cut'):
                        problems.append(f"{item['id']} has no verdict of \"same\", \"rewritten\" or \"cut\"")
                    elif verdict['verdict'] == 'rewritten' and not is_text(verdict.get('text')):
                        problems.append(f"{item['id']} is rewritten and verdicts.json does not give the text")
                    elif verdict['verdict'] != 'cut' and item['declaration'] is None:
                        problems.append(f"{item['id']}: no declaration states it, so it is cut")
                if problems:
                    raise Unusable(problems)
                return [found[item['id']] for item in rows]

            verdicts = self.task('draft-compare', 'draft-compare', given, read, self.sessions.assessor)
        judged = {verdict['id']: verdict for verdict in verdicts}
        by_id = {item['id']: item for item in rows}
        for kind, prefix, listed in (('statement', 's:', draft['statements']), ('formula', 'f:', draft['formulas'])):
            for item in listed:
                verdict = judged.get(item.get('gap') or prefix + item['label'])
                if verdict is None:
                    continue
                if verdict['verdict'] == 'cut':
                    item['cut'] = True
                    continue
                if verdict['verdict'] == 'rewritten':
                    item['text'] = verdict['text']
                item['element'] = by_id[verdict['id']]['declaration']
        for gid, gap in gaps.items():
            gap['closed_by'] = closed[gid] if gid in closed and judged[gid]['verdict'] != 'cut' else None
        problems = [f"the drafted {kind} {item.get('label')} has no declaration that states it"
                    for kind, listed in (('statement', draft['statements']), ('formula', draft['formulas']))
                    for item in listed if not item.get('cut') and item.get('element') not in entries]
        if problems:
            raise Stop('the draft asks for more than the library has: ' + '; '.join(problems))
        target.mkdir(parents=True, exist_ok=True)
        for name in ('plan.json', 'study.md'):
            shutil.copyfile(self.work / 'draft' / name, target / name)
        write_json(target / 'draft.json', draft)
        write_json(target / 'verdicts.json', verdicts)
        cut = [verdict['id'] for verdict in verdicts if verdict['verdict'] == 'cut']
        rewritten = [verdict['id'] for verdict in verdicts if verdict['verdict'] == 'rewritten']
        if cut or rewritten:
            self.decide('Step 6: the draft brought to the library', 'Cut from the draft, because no declaration states '
                        'it: ' + (', '.join(cut) or 'nothing') + '. Restated as the declaration says it: '
                        + (', '.join(rewritten) or 'nothing') + '.')

    # -- stage 2, step 7: the freeze --------------------------------------------------------------------

    def freeze(self):
        folded, lean = self.work / 'lib' / '6-folded', self.package / 'lean'
        missing = [sid for sid in ('2.5-records', '2.6-records', '2.6-compare') if sid not in self.state['steps']]
        if missing:
            raise Stop('the checks of these steps do not stand in state.json: ' + ', '.join(missing))
        index = read_json(folded / 'index.json')
        entries, main = index['entries'], self.state['main']
        shutil.copytree(folded / 'lean', lean)
        shutil.copytree(folded / 'records', self.package / 'records')
        shutil.copyfile(folded / 'bibliography.bib', self.package / 'records' / 'bibliography.bib')
        modules = dict(canon.library_modules(lean, self.library))
        stale = [module for module in set(modules) | set(index['modules'])
                 if module not in modules or module not in index['modules']
                 or package.sha256_file(modules[module]) != index['modules'][module]['sha256']]
        if stale:
            raise Stop('the index of step 6 is not of the bytes that are frozen: ' + ', '.join(sorted(stale)))
        project = package.lake_project(self.settings)
        build = package.build_files(self.library, self.name, project, self.state['version'],
                                    (lean / (self.library + '.lean')).is_file())
        for name, text in build.items():
            write_text(lean / name, text)
        toolchain = build['lean-toolchain'].strip()
        first, root_module = self.work / 'first' / 'lean', self.state['root_module']
        decision = read_json(self.work / 'lib' / '0-selected' / 'decision.json')
        title = read_json(self.work / 'lib' / '6-draft' / 'plan.json')['title']
        records = package.read_records(self.package / 'records')
        record = records.get(name_path(self.root))
        models = list(dict.fromkeys([self.sessions.writer['model'], self.sessions.assessor['model']]))
        stage = self.work / 'stage' / 'lake'
        lake = package.lake_command(self.settings)

        def registry(compared):
            both = main in compared
            texts = {'Challenge.lean': package.challenge_text(first, self.definitions, root_module,
                                                              entries[main]['statement'] if both else None),
                     'Solution.lean': package.solution_text([entries[self.root]['module']]
                                                            + ([entries[main]['module']] if both else [])),
                     'comparator.json': as_json(package.comparator(compared)),
                     'Check.lean': package.check_text(entries[self.root]['module'], [self.root, main]),
                     'formalization.yaml': package.yaml_text(package.formalization(
                         title, decision, package.read_text(folded / 'bibliography.bib'), self.config,
                         self.config['licence'], models, self.library, compared, record,
                         {name: entries[name]['module'] for name in compared}, toolchain,
                         {name: ((records.get(name_path(name)) or {}).get('sections') or {}).get('Statement')
                          for name in compared})) + '\n'}
            for name, text in texts.items():
                write_text(lean / name, text)
                write_text(stage / name, text)
            return texts['Challenge.lean']

        def built(compared):
            """Lake on the staged project: the build, then the statements of Challenge.lean; returns what failed."""
            code, out, err = package.lake_run(lake, stage, 'build')
            self.sessions.event('check', check='lake build', problems=[] if code == 0 else [(out + err)[-2000:]])
            if code != 0:
                return f'lake build ended with exit code {code}: ' + (out + err)[-1500:]
            write_text(stage / (canon.EXTRACT_MODULE + '.lean'), canon.extraction_source('Challenge', ['Challenge'], []))
            code, out, err = package.lake_run(lake, stage, 'env', 'lean', canon.EXTRACT_MODULE + '.lean')
            (stage / (canon.EXTRACT_MODULE + '.lean')).unlink()
            if code != 0:
                return f'the statements of Challenge.lean could not be extracted: exit code {code}: ' + (out + err)[-1500:]
            rows, pairs = canon.parse_rows(out)
            posed = canon.update_index(canon.empty_index(), rows, pairs, stage, 0)['entries']
            differing = [name for name in compared
                         if name not in posed or posed[name]['statement_hash'] != entries[name]['statement_hash']]
            return ('Challenge.lean does not state as the library does: ' + ', '.join(differing)) if differing else None

        if stage.exists():
            remove_tree(stage)
        shutil.copytree(lean, stage)
        if project is not None:
            manifest = read_json(lean / 'lake-manifest.json')
            packages = project / read_json(project / 'lake-manifest.json').get('packagesDir', '.lake/packages')
            problems = package.packages_problems(manifest, packages)
            if problems:
                raise Stop('; '.join(problems))
            write_text(stage / 'lake-manifest.json', json.dumps({**manifest, 'packagesDir': packages.as_posix()}, indent=1) + '\n')
        compared, failed = [self.root], None
        named = entries[main]['statement_uses']
        if main != self.root and all(used in entries and entries[used]['module'] in self.definitions for used in named):
            measure = package.challenge_measure(registry([self.root, main]))
            limits = [fail for fail in measure['fails'] if 'imports' not in fail]
            failed = '; '.join(limits) if limits else built([self.root, main])
            if failed is None:
                compared = [self.root, main]
            else:
                self.decide('Step 7: what is compared', f'The root alone is compared. With the main theorem `{main}` '
                            f'added to Challenge.lean: {failed}')
        elif main != self.root:
            self.decide('Step 7: what is compared', f'The root alone is compared: the statement of the main theorem '
                        f'`{main}` names declarations outside the definition modules ('
                        + ', '.join(f'`{used}`' for used in named
                                    if used not in entries or entries[used]['module'] not in self.definitions)
                        + '), so it cannot be stated in Challenge.lean. It is named in formalization.yaml only.')
        if compared == [self.root]:
            measure = package.challenge_measure(registry(compared))
            failed = built(compared)
            if failed is not None:
                raise Stop(failed)
        code, out, err = package.lake_run(lake, stage, 'env', 'lean', 'Check.lean')
        if code != 0:
            raise Stop(f'lake env lean Check.lean ended with exit code {code}: ' + (out + err)[-1500:])
        axioms = package.axioms_printed(out)
        problems = [f'Check.lean prints no axioms line for {name}' for name in (self.root, main) if name not in axioms]
        problems += [f'{name} depends on axioms beyond the three: ' + ', '.join(sorted(set(found) - set(self.allowed)))
                     for name, found in axioms.items() if set(found) - set(self.allowed)]
        problems += package.definition_problems(lean, first, self.definitions)
        if entries[self.root]['statement_hash'] != self.statement_hash:
            problems.append('the statement of the root is not the statement the instance fixed')
        problems += package.registry_problems(lean, self.config['licence'])
        if problems:
            raise Stop('the frozen library does not pass its check: ' + '; '.join(problems))
        remove_tree(stage)
        package.make_view(self.work / 'view' / 'frozen', folded / 'lean', self.package / 'records',
                          folded / 'bibliography.bib', index, self.work / 'source', self.settings, decision['account'])
        requires = ', '.join(f"{p['name']} {p.get('inputRev') or p['rev'][:12]}" for p in
                             read_json(lean / 'lake-manifest.json')['packages'] if not p.get('inherited'))
        write_json(self.work / 'freeze.json', {**package.freeze_hashes(self.package), 'compared': compared,
                                               'axioms': {name: axioms[name] for name in (self.root, main)},
                                               'check_output': out, 'toolchain': toolchain, 'requires': requires,
                                               'title': title, 'fails': measure['fails']})

    # -- stage 3: history and knowledge archive ---------------------------------------------------------

    def archive(self):
        info = package.knowledge_archive(self.instance, self.state['run']['commit'], self.package / 'knowledge',
                                         self.name, self.account)
        wanted = lambda name: name.startswith(('knowledge/', 'canon/approaches/', 'canon/questions/', 'canon/history/'))
        members = package.archive_members(self.package / 'knowledge' / info['archive'], wanted)
        write_json(self.work / 'history' / 'ledger.json', package.ledger(members))
        write_json(self.work / 'history' / 'archive.json', info)

    def history(self):
        archive = read_json(self.work / 'history' / 'archive.json')
        rows = read_json(self.work / 'history' / 'ledger.json')
        path = self.package / 'knowledge' / archive['archive']
        names = package.archive_names(path)
        pointed = {row['event']: package.event_members(row, names) for row in rows}
        wanted = {name for found in pointed.values() for name in found}
        members = package.archive_members(path, lambda name: name in wanted)
        by_event = {row['event']: row for row in rows}

        def given_members(group):
            return {'archive/' + name: members[name] for row in group for name in pointed[row['event']]}

        def write(number, group):
            def read(output):
                found = {e.get('event'): e for e in Sessions.load(output / 'entries.json', list) if isinstance(e, dict)}
                problems = [f"entries.json has no entry with a text for the event {row['event']}" for row in group
                            if not is_text(found.get(row['event'], {}).get('text'))]
                problems += [f"the entry of the event {row['event']} names another record than its ledger line"
                             for row in group if row['event'] in found
                             and found[row['event']].get('record', row['record']) != row['record']]
                for row in group:
                    entry = found.get(row['event'])
                    if entry and is_text(entry.get('text')):
                        problems += package.entry_problems(row['event'], entry['text'], entry.get('list', []))
                if problems:
                    raise Unusable(problems)
                return [{'event': row['event'], 'date': row['date'], 'kind': row['kind'], 'title': row['title'],
                         'elements': row['elements'], 'text': found[row['event']]['text'],
                         'list': found[row['event']].get('list') or [], 'record': row['record']} for row in group]

            return self.task('history-write', 'history-write', {'ledger.json': as_json(group), **given_members(group)},
                             read, self.sessions.writer, label=number)

        groups = package.batches(rows, package.HISTORY_BATCH)
        written = self.sessions.side_by_side([lambda n=n, g=g: write(n, g) for n, g in groups])

        def check(number, group, entries):
            given = {'entries.json': as_json([{key: entry[key] for key in ('event', 'date', 'text', 'list', 'record')}
                                              for entry in entries]), **given_members(group)}

            def read(output):
                found = {v.get('event'): v for v in Sessions.load(output / 'verdicts.json', list) if isinstance(v, dict)}
                problems = []
                for entry in entries:
                    verdict = found.get(entry['event'], {})
                    if verdict.get('verdict') not in ('stands', 'corrected'):
                        problems.append(f"the entry of the event {entry['event']} has no verdict of \"stands\" or \"corrected\"")
                    elif verdict['verdict'] == 'corrected' and not is_text(verdict.get('text')):
                        problems.append(f"the entry of the event {entry['event']} is corrected and no text is given")
                    elif verdict['verdict'] == 'corrected':
                        problems += package.entry_problems(entry['event'], verdict['text'], verdict.get('list', []))
                if problems:
                    raise Unusable(problems)
                corrected = lambda entry: found[entry['event']]['verdict'] == 'corrected'
                return [{**entry, 'verdict': found[entry['event']]['verdict'],
                         'text': found[entry['event']]['text'] if corrected(entry) else entry['text'],
                         'list': (found[entry['event']].get('list') or []) if corrected(entry) else entry['list']}
                        for entry in entries]

            return self.task('history-read', 'history-read', given, read, self.sessions.assessor, label=number)

        read_through = self.sessions.side_by_side([lambda n=n, g=g, e=e: check(n, g, e)
                                                   for (n, g), e in zip(groups, written)])
        entries = []
        for (number, _), found in zip(groups, read_through):
            write_json(self.work / 'history' / 'entries' / (number + '.json'), found)
            entries += found
        problems = [f"the entry of the event {entry['event']} points to {entry['record']}, which is no member of the archive"
                    for entry in entries if entry['record'] not in names]
        problems += [f"the event {event} has no entry with a reader's verdict" for event in by_event
                     if event not in {entry['event'] for entry in entries if entry.get('verdict')}]
        if package.sha256_file(path) != package.manifest_sha(self.package / 'knowledge' / 'MANIFEST.md'):
            problems.append('the SHA-256 of the archive is not the one MANIFEST.md states')
        if problems:
            raise Stop('the history does not pass its check: ' + '; '.join(problems))
        write_text(self.package / 'history' / 'timeline.md', package.timeline(entries, self.root))

    # -- stage 4: map and paper -------------------------------------------------------------------------

    def depmap(self):
        done = subprocess.run([sys.executable, '-B', str(RUNTIME / 'depmap.py'), str(self.work / 'view' / 'frozen'),
                               '--out', str(self.package / 'dependency-map')], stdin=subprocess.DEVNULL,
                              stdout=subprocess.PIPE, stderr=subprocess.STDOUT, **popen_options())
        if done.returncode != 0:
            raise Stop(f'the map command ended with exit code {done.returncode}: '
                       + done.stdout.decode('utf-8', errors='replace')[-1500:])

    def write_paper(self):
        out = self.work / 'paper'
        page = self.work / 'title-page.json'
        write_json(page, {'authors': [{key: author[key] for key in ('name', 'address', 'email') if key in author}
                                      for author in self.config['authors']]})
        code = self.paper_run(self.work / 'view' / 'frozen', out, from_draft=self.work / 'lib' / '6-draft', title_page=page,
                              main=self.paper_main())
        log = read_json(out / 'log.json') if (out / 'log.json').is_file() else []
        end = next((event for event in reversed(log) if event['event'] == 'end'), {})
        if code != 0:
            raise Stop(f'the paper command ended with exit code {code}: '
                       + as_json(end.get('open') or end.get('error') or 'no end event in its log')[:3000])
        target = self.package / 'paper'
        target.mkdir(parents=True, exist_ok=True)
        for name in ('paper.tex', 'paper.pdf', 'references.bib', 'correspondence.json'):
            if not (out / name).is_file():
                raise Stop(f'the paper command left no {name}')
            shutil.copyfile(out / name, target / name)
        kept = end.get('kept') or []
        if kept:
            self.decide('Stage 4: findings of the readings that the paper keeps', '\n'.join(
                f"- {collapsed(str(item.get('finding')))[:500]} Kept because: {collapsed(str(item.get('reason')))}"
                for item in kept))

    # -- stage 5: documents -----------------------------------------------------------------------------

    def documents(self):
        freeze = read_json(self.work / 'freeze.json')
        decision = read_json(self.work / 'lib' / '0-selected' / 'decision.json')
        index = read_json(self.work / 'lib' / '6-folded' / 'index.json')
        entries, main = index['entries'], self.state['main']
        archive = read_json(self.work / 'history' / 'archive.json')
        timeline = [entry for path in sorted((self.work / 'history' / 'entries').glob('*.json')) for entry in read_json(path)]
        correspondence = read_json(self.package / 'paper' / 'correspondence.json')
        plan = read_json(self.work / 'paper' / 'plan.json')
        # The sessions of the run are in its own log and in the logs of its two runs of the paper command.
        launched = [event for log in (self.sessions.log, *(read_json(self.work / name / 'log.json')
                                                           for name in ('draft', 'paper')))
                    for event in log if event['event'] == 'session']
        models = list(dict.fromkeys(event['model'] for event in launched))
        # The numbered statements that the paper cites and does not prove; the library proves each of them.
        cited = [row['element'] for row in correspondence.get('statements', []) if row.get('cited')]
        facts = package.package_facts(
            self.package, self.name, self.library, self.root, main, index, freeze, archive, timeline, correspondence,
            cited, plan['title'], freeze['toolchain'], freeze['requires'], models, len(launched),
            self.state['run']['commit'])
        write_json(self.work / 'facts.json', facts)
        # The text of the licence as the skill has it, with LF line endings: a checkout on Windows can give the
        # skill's file Windows line endings, and no text file of the package has them.
        write_text(self.package / 'LICENSE',
                   package.read_text(SKILL / 'finalize' / 'licences' / (self.config['licence'] + '.txt')))
        fails = list(self.state['measured']['fails'] if freeze['compared'] == [self.root] else freeze['fails'])
        introduction = self.work / 'paper' / 'parts' / (plan['sections'][0]['id'] + '.tex')
        given = {'facts.json': as_json(facts), 'account.md': decision['account'],
                 'introduction.tex': introduction.read_bytes() if introduction.is_file() else '',
                 'timeline.md': (self.package / 'history' / 'timeline.md').read_bytes()}

        def prose(output):
            texts, problems = {}, []
            for name in ('outline.md', 'obtained.md'):
                if not (output / name).is_file() or not package.read_text(output / name).strip():
                    problems.append(f'output/{name} was not written')
                    continue
                texts[name], missing = package.fill(package.read_text(output / name), facts)
                problems += [f'{name} uses {{{{facts.{key}}}}}, and facts.json has no such key' for key in missing]
            if problems:
                raise Unusable(problems)
            return texts

        def compose(texts):
            write_text(self.package / 'README.md', package.readme_text(
                facts, package.read_text(self.work / 'source' / 'root.md'), entries[self.root]['statement'],
                entries[main]['statement'], texts['outline.md'], texts['obtained.md'], freeze['check_output'],
                self.config, self.config['licence'], fails, cited,
                package.provenance(decision['registry'], self.package / 'lean' / 'formalization.yaml')))

        texts = self.task('readme-write', 'readme-write', given, prose, self.sessions.writer)
        compose(texts)
        copy = {'package/' + relative: path.read_bytes() for relative, path in package.files_under(self.package).items()
                if relative != 'knowledge/' + archive['archive']}

        def read_findings(output):
            findings = Sessions.load(output / 'findings.json', list)
            if not all(isinstance(f, dict) and is_text(f.get('file')) and is_text(f.get('quote')) and is_text(f.get('problem'))
                       for f in findings):
                raise Unusable(['every finding has "file", "quote" and "problem"'])
            return findings

        findings = self.task('package-read', 'package-read', copy, read_findings, self.sessions.assessor)
        write_json(self.work / 'findings.json', findings)
        if findings:
            whole = collapsed(' '.join(texts.values()))
            ours = [f for f in findings if not (f['file'].endswith('README.md') and collapsed(f['quote']) in whole)]
            if ours:
                raise Stop('the reader of the package found faults outside the two prose sections of the README, which '
                           'are faults of the script or of an earlier stage: ' + as_json(ours)[:3000])
            again = {**given, 'findings.json': as_json(findings),
                     **{'previous/' + name: (self.work / self.state['accepted']['readme-write']['folder'] / 'output' / name).read_bytes()
                        for name in ('outline.md', 'obtained.md')}}
            texts = self.task('readme-write', 'readme-write', again, prose, self.sessions.writer, label='correction')
            compose(texts)
            self.decide('Stage 5: the documents', f'The reader of the package found {len(findings)} faults in the two '
                        'prose sections of the README; a session corrected them.')
        if '{{facts.' in package.read_text(self.package / 'README.md'):
            raise Stop('README.md holds a placeholder that was not filled')
        write_text(self.package / 'MANIFEST.sha256', package.manifest_text(self.package))

    # -- stage 6: the final check, and the end ----------------------------------------------------------

    def final_check(self):
        problems = package.standalone_problems(self.package, self.work, self.account, read_json(self.work / 'freeze.json'))
        if problems:
            raise Stop('the package does not pass its final check: ' + '; '.join(problems))

    def finish(self):
        """Move the package into solved/, list it in the repository's README, write the report, delete the rest."""
        freeze, facts = read_json(self.work / 'freeze.json'), read_json(self.work / 'facts.json')
        decision = read_json(self.work / 'lib' / '0-selected' / 'decision.json')
        if self.package.exists():
            self.solved.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(self.package), str(self.solved))
        package.add_solved_entry(REPOSITORY / 'README.md', self.name,
                                 f"- [{facts['title']}](solved/{self.name}/README.md): {collapsed(decision['sentence'])} "
                                 f"Lean {freeze['toolchain']}" + (f", {freeze['requires']}" if freeze['requires'] else '')
                                 + f"; root `{self.root}`.")
        fails = self.state['measured']['fails'] if freeze['compared'] == [self.root] else freeze['fails']
        fill = []
        if not self.config['authors']:
            fill.append('`project.authors` and `project.responsible_maintainers` in `lean/formalization.yaml`: the '
                        'configuration names no author, and the registry requires people in both.')
        if not facts.get('registry_sources'):
            fill.append('`sources` in `lean/formalization.yaml`: the selection recorded the result as known, and '
                        'neither the selection nor the record of the root names a source for it. The registry '
                        'requires at least one source with the relationship `formalizes`, `adapts` or '
                        '`independently-proves`.')
        fill += [f'{rule}. The registry will not accept the package as it is.' for rule in fails]
        registry = decision['registry']
        fill.append('What the result is in the literature. Under "Where the result comes from" the README says what the '
                    "research's records hold: whose question the result settles, where that was posed, and on what "
                    "grounds the result is recorded as original or as known. The registry's review rejects a result "
                    'for which it cannot identify a research area and a reader, and it marks down a claim of novelty '
                    'that has no search of the literature behind it. The run adds no such claim of its own. Read that '
                    'part, and add what you know and the records do not, each with its source.')
        if registry.get('origin') == 'original':
            fill.append('`sources` in `lean/formalization.yaml`: an earlier public account of the result that the '
                        "research's records do not name belongs there, your own included, such as a preprint, a note "
                        'or a deposited record of earlier work. With such an account the result may be source-based '
                        'and no longer original.')
        if not registry.get('related_formalizations'):
            fill.append("`related_formalizations` in `lean/formalization.yaml` is empty: the research's records name no "
                        'earlier formal proof of the result, and the run did not search for one. Add each one you '
                        'know, with how this library relates to it.')
        if facts.get('registry_sources', 0) > (registry.get('origin') == 'original'):
            fill.append('`author_endorsement` of each source in `lean/formalization.yaml`: whether the authors of a '
                        'source took part, were contacted or answered is known to you alone, so the field is not '
                        'written. Its values are `participated`, `endorsed`, `no-response`, `not-contacted`, '
                        '`declined`, `n/a` and `other`; the registry does not require it.')
        fill.append(f"The Lean release. The library is on {freeze['toolchain']}. The registry takes the tools with which "
                    'it renders and exports a submission from the Lean release of the submitted library, so a '
                    'submission can fail there because of the release alone, with a library that passes every check. '
                    "Before submitting, read the registry's open issues for this release, and the minimum release it "
                    'accepts, which it changes.')
        fill.append('A submission is the package published as a repository of its own, with `lean` as the project '
                    'directory; the pipeline prepares and does not submit.')
        self.stop_broker()
        write_text(self.work / 'report.md', '\n'.join([
            f'# Report of the run: {self.name}', '',
            f"The package is in place: `solved/{self.name}/`. The repository's README lists it under \"Solved problems\". "
            'Nothing was committed and nothing was pushed.', '',
            '## What was made', '',
            f"- `lean/`: the library `{self.library}`, {facts['modules']} modules, {facts['lines']} lines, "
            f"{facts['declarations']} public declarations; the build files; `Check.lean`; the registry's files.",
            f"- `records/`: {facts['records']} records and the bibliography ({facts['sources']} entries).",
            '- `dependency-map/`, `paper/`, `history/timeline.md`, `knowledge/` with the archive and its manifest, '
            '`README.md`, `LICENSE`, `MANIFEST.sha256`.', '',
            '## The checks, and what each established', '',
            f"- The research was read at the commit `{self.state['run']['commit']}`; its root was formally proved there.",
            '- Every step that wrote Lean: each file a module of at most 10,000 lines; the definition modules byte for '
            'byte those of the first commit; the build of all modules through the run\'s compile service.',
            f"- The freeze: `lake build` ended with exit code 0; Lean reports for `{self.root}`: {facts['axioms_root']}; "
            f"for `{self.state['main']}`: {facts['axioms_main']}; the root has the statement the instance fixed, by the "
            f"term Lean elaborates; Challenge.lean states the compared theorems ({facts['compared']}) as the library does.",
            '- The records: each parses; each record that was written was compared by a session that did not write it; '
            'every cited source is in the bibliography and was verified by the sources session.',
            '- The draft: every drafted statement and formula has a declaration that states it.',
            '- The paper command ended with exit code 0: typeset, every numbered statement compared with its element, '
            'the running text covered by declarations.',
            '- The history: every entry points to a member of the archive and was read by a session that had only the '
            'entries and those records; the archive has the SHA-256 its manifest states.',
            '- The final check: every relative link resolves inside the package; no file and no member of the archive '
            'holds the account name; no document the pipeline wrote holds a drive path; every text file ends its '
            'lines with LF; `lean/` and `records/` have the hashes of the freeze; every line of `MANIFEST.sha256` '
            'holds.', '',
            '## What was not verified', '',
            "- The classification codes were checked for their form, not against the registry's lists.",
            "- The registry's verifier and Lean's comparator were not run on the package.",
            '- No second complete check of the frozen library was made beyond the Lake build and the axioms Lean reports.',
            '- No person read the Lean statement against the proposition, unless the configuration says so.', '',
            '## What you fill in before a submission to the registry', '', *['- ' + item for item in fill], '',
            '## The choices', '', 'Every choice the run made, with its reason, is in `decisions.md` beside this file.', '']))
        for path in self.work.iterdir():
            if path.name not in KEPT_AT_END:
                remove_tree(path) if path.is_dir() else path.unlink()

    def stopped(self, halt):
        """report.md of a run that stops: the step, the check, and what it found."""
        write_text(self.work / 'report.md', '\n'.join([
            f'# Report of the run: {self.name}', '',
            f'The run stopped at the step `{halt.step}`, which could not meet its exit condition.', '',
            '## What the check found', '', halt.message.strip(), '',
            '## Continuing', '',
            'The work folder is whole. Once the cause is repaired, the same command with the same arguments continues '
            f'at the step `{halt.step}`; the steps that passed are not made again.', '',
            'The steps that passed: ' + ', '.join(f'`{sid}`' for sid in self.state['steps']) + '.', '']))

    # -- the order --------------------------------------------------------------------------------------

    def run(self):
        """The whole command; returns the exit code."""
        self.start()
        self.load()
        if '6-check' in self.state['steps'] and not self.package.exists():
            self.finish()  # the run was stopped after the package had been moved
            return 0
        watcher = threading.Thread(target=self.watch_broker, daemon=True)
        watcher.start()
        lib = 'lib/'
        failed = []

        def beside():
            try:
                self.step('3-archive', [], ['package/knowledge', 'history/ledger.json', 'history/archive.json'], self.archive)
                self.step('3-history', ['package/knowledge', 'history/ledger.json', 'history/archive.json'],
                          ['history/entries', 'package/history'], self.history)
            except BaseException as error:
                failed.append(error)

        history = threading.Thread(target=beside)
        try:
            history.start()
            try:
                self.step('1-selection', ['source', 'first'], [lib + '0-selected'], self.selection)
                self.step('2.1-take', [lib + '0-selected', 'first'], [lib + '1-taken'], self.take)
                self.step('2.2-review', [lib + '0-selected', lib + '1-taken'], [lib + '2-review'], self.review)
                self.step('2.3-simplify', [lib + '0-selected', lib + '1-taken', lib + '2-review'], [lib + '3-parts'],
                          self.simplify)
                self.step('2.4-merge', [lib + '1-taken', lib + '3-parts'], [lib + '4-merged'], self.merge)
                self.step('2.4-arrange', [lib + '1-taken', lib + '2-review', lib + '3-parts', lib + '4-merged'],
                          [lib + '4-arranged'], self.arrange)
                self.step('2.5-records', [lib + '0-selected', lib + '4-arranged'], [lib + '5-records'], self.records)
                self.step('2.6-draft', ['source', lib + '0-selected', lib + '4-arranged', lib + '5-records'],
                          ['view/4', 'draft'], self.draft, keep=('draft',))
                folded = lib + '6-folded/'
                self.step('2.6-foldback', [lib + '4-arranged', lib + '5-records', 'draft'],
                          [lib + '6-parts', folded + 'lean', folded + 'index.json', folded + 'foldback.json'], self.foldback)
                self.step('2.6-records', [lib + '4-arranged', lib + '5-records', 'draft', folded + 'lean', folded + 'index.json'],
                          [folded + name for name in ('records', 'bibliography.bib', 'findings.json', 'sources.json',
                                                      'verdicts.json', 'requests.json')], self.records_again)
                self.step('2.6-compare', [lib + '4-arranged', 'draft', folded + 'lean', folded + 'index.json',
                                          folded + 'foldback.json', folded + 'records'], [lib + '6-draft'], self.compare_draft)
                self.step('2.7-freeze', ['source', 'first', lib + '0-selected', lib + '6-draft', folded + 'lean',
                                         folded + 'index.json', folded + 'records', folded + 'bibliography.bib'],
                          ['package/lean', 'package/records', 'view/frozen', 'freeze.json'], self.freeze)
                self.step('4-map', ['view/frozen'], ['package/dependency-map'], self.depmap)
                self.step('4-paper', ['view/frozen', lib + '6-draft'], ['paper', 'package/paper', 'title-page.json'],
                          self.write_paper, keep=('paper',))
            finally:
                history.join()
            if failed:
                raise failed[0]
            self.step('5-documents', ['source', lib + '0-selected', folded + 'index.json', 'freeze.json', 'paper',
                                      'history/entries', 'history/archive.json', 'package/lean', 'package/records',
                                      'package/knowledge', 'package/history', 'package/dependency-map', 'package/paper'],
                      ['facts.json', 'findings.json', 'package/LICENSE', 'package/README.md', 'package/MANIFEST.sha256'],
                      self.documents)
            self.step('6-check', ['freeze.json', 'package/lean', 'package/records', 'package/knowledge', 'package/history',
                                  'package/dependency-map', 'package/paper', 'package/LICENSE', 'package/README.md',
                                  'package/MANIFEST.sha256'], [], self.final_check)
            try:
                self.finish()
            except OSError as error:
                raise Halt('the end of the run', f'the package could not be put in place: {error}')
            return 0
        except Halt as halt:
            self.stopped(halt)
            return 2
        finally:
            self.stop_broker()


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('instance', type=Path, help='a finished do-math instance')
    parser.add_argument('--name', required=True, help='the name of the package: solved/<name>/')
    parser.add_argument('--config', type=Path, help='a JSON file with authors, licence, human_review, parallel, tex')
    args = parser.parse_args(argv)
    try:
        code = Run(args.instance, args.name, load_config(args.config), args.config).run()
    except Refusal as refusal:
        print('finalize.py: ' + str(refusal), file=sys.stderr)
        return 1
    work = REPOSITORY / '.skill-workspace' / ('finalize-' + args.name)
    print(f'finalize.py: the package is in {REPOSITORY / "solved" / args.name}; the report is {work / "report.md"}'
          if code == 0 else f'finalize.py: the run stopped; {work / "report.md"} says where and why', file=sys.stderr)
    return code


if __name__ == '__main__':
    contain_session_processes()  # whatever a session or the compile service starts ends with this command
    raise SystemExit(main())
