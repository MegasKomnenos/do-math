"""Take back the room that an instance holds for files no program reads again. See "Retention and archives" in
../reference/operations.md.

The runner and the broker remove nothing from an instance, so it grows for as long as its research runs. What
stands in it is of three kinds. A record is the one copy of something that happened: what a session said, wrote
and was given, the archives of its work, and the research itself in canon/, knowledge/ and the repository. A
state is what the runner or the broker continues from. The third kind was made by a program from files that are
still in the instance, and is read again only for a reader that can be named. This module removes files of the
third kind once that reader is gone, and nothing of the other two:

- The folder of a compile, runner/lean/jobs/<job>/, and of a build, runner/lean/builds/<build>/. After a compile
  or a build has ended, its folder is opened by its ID alone and for the one that submitted it: by the broker's
  client commands `wait` and `result` (lean_broker.job_record, relay, report_build); for the build that a
  session's `prepare` or `verify` saved in its work folder and for the build of the publication under way
  (canon.build_outcome); and by the check of a review's output, for the review's own build (check.audit_formal).
  The broker opens the folder of an ended one only to see whether a request left in the queue under the same ID
  has been answered (lean_broker.Broker.ingest). So the folder goes when the one that submitted it reads nothing
  more: a session whose work has finished processing (finished_sessions), the runner while no publication is
  under way, and the operator. The folders of the calibration compiles, which the broker submits itself, stay.
  When Lean rejects a calibration compile, the calibration table keeps that verdict until Lean changes, and no
  calibration of those imports runs again meanwhile. The reason in the table sends its reader to the stdout.log
  of the rejected compile (lean_broker.Broker.finish), so that log is the one copy of what Lean said. All
  calibration folders stay, whatever their outcome, so that no rule has to tell which logs the table still
  refers to: such a folder holds some ten kilobytes, and the broker makes one only for a set of imports whose
  cost it cannot estimate from the sets it has measured (lean_broker.Broker.estimate_baseline).
- An entry of the module cache, runner/lean/cache/<key>.*. The broker reads an entry when a build needs a module
  with that key (lean_broker.Broker.advance_build, restore_module), and the Lean output kept with an entry is
  read for an ended build that took the module from the cache (canon.build_outcome, lean_broker.report_build).
  The finalize command copies the folder into its own work folder when a run starts, for the builds it makes
  there. An entry stays when a module of the canon as it stands has its key (canon_keys), so that the next build
  of the library compiles nothing that is unchanged, and when a build whose folder stays names its key. Every
  other entry goes. A build that later needs such a module compiles it and stores the entry again, and that
  compile is all the removal costs, because entries are removed only while no build is being carried forward
  (clean).
- The loose objects of the instance's repository are packed by Git (`git gc`), which removes no commit.

Nothing under sessions/, canon/, knowledge/ or control/ is touched, and no state file.
"""
import os
from pathlib import Path
import re
import shutil
import time

from canon import Canon, library_modules
from coordination import ACTIVE_STATUSES
from lean_broker import (ACTIVE, BUILD_ID, FINISHED, JOB_ID, Paths, broker_alive, cached_entry, discover_modules,
                         ensure_broker, environment_of, module_key, saved_state)
from runtime_support import InstanceLock, alive, git, read_json, terminate_process

# The names under which compiles run that no session submitted and whose folders go once the compiles have ended:
# the runner's builds of a publication, and the build of `init` and what an operator builds under that name. The
# broker's calibration compiles run under a third name, lean_broker.BROKER_SESSION, and their folders stay.
OWNERS = ('runner', 'operator')
REMOVING = 'removing-'  # the name of a job's or build's folder begins so from the moment it is taken out of sight
MANIFEST = '.artifacts.json'  # the file that makes a cache entry complete (lean_broker.cached_entry)
ENTRY_FILE = re.compile(r'([0-9a-f]{32})(\..+)')  # a file of a cache entry: the key, then the suffix
# A file that a broker was writing into the cache when it ended. lean_broker.Broker.cache_module writes each file
# of an entry under such a name and then moves it onto the entry's own.
UNFINISHED_FILE = re.compile(r'\.[0-9a-f]{32}\..+\.[0-9a-f]{32}')
SHOWN = 20  # how many of the files and folders that could not be removed the result names


# ----------------------------------------------------------------------------- when an instance is cleaned

def unmet_conditions(instance):
    """What does not hold, at this moment, of the conditions under which an instance is cleaned: one sentence
    for each, and an empty list when all hold.

    The conditions are those of restart-broker (runner.main): new dispatch is stopped, and the running CLI
    turns, the publications and the compiles have finished. A session held behind the stop for its next turn
    has no CLI and does not count. While they hold, no session runs a command, the runner starts no build, and
    the broker compiles nothing. They are read here and not enforced: what keeps the removal safe when work
    begins all the same is the broker's lock (clean)."""
    instance = Path(instance)
    state = read_json(instance / 'runner/state.json')
    unmet = []
    if not (instance / 'control/STOP').exists():
        unmet.append('new dispatch is not stopped; run stop first')
    turns, publishing = [], []
    for sid, session in state['sessions'].items():
        if session['status'] == 'publishing':
            publishing.append(sid)
        elif session['status'] in ACTIVE_STATUSES:
            check = instance / 'sessions' / sid / 'end-check.json'
            held = check.is_file() and read_json(check)['status'] == 'waiting_dispatch'
            if not held or alive(session.get('cli')):
                turns.append(sid)
    if turns:
        unmet.append('CLI turns are still running: ' + ', '.join(sorted(turns)))
    if publishing or state.get('publication') or state.get('publish_queue'):
        unmet.append('a publication is under way or waits in state.publish_queue'
                     + (', for the sessions ' + ', '.join(sorted(publishing)) if publishing else ''))
    # As `status` reads it: a live broker writes its state first, so that a compile registered a moment ago shows.
    compiles = saved_state(Paths(instance), current=True)
    unfinished = sorted(identifier for kind in ('jobs', 'builds')
                        for identifier, record in compiles.get(kind, {}).items() if record['status'] in ACTIVE)
    if unfinished:
        unmet.append('Lean compiles are queued or running: ' + ', '.join(unfinished))
    return unmet


def finished_sessions(state):
    """The sessions of the runner's state whose work has finished processing.

    This is the rule by which the archiver packs a session (runner.archive_finished): the session holds no slot,
    and its pipeline has reached the stage `done`, or, for a review or an organizer without a pipeline, its job
    is done or cancelled. A pipeline does not leave that stage and such a job does not run again, so a session
    that is in this set stays in it. Until then a session that has itself ended is not in it: a peer whose
    candidate waits for review, a session whose task a later session continues, a session that a replacement
    was launched for. Their folders under runner/lean/ stay, whoever may still ask for them."""
    finished = set()
    for sid, session in state['sessions'].items():
        job = state['jobs'][session['job']]
        pipeline = state['pipelines'].get(job['pipeline'])
        done = pipeline['stage'] == 'done' if pipeline else job['status'] in ('done', 'cancelled')
        if done and session['status'] not in ACTIVE_STATUSES:
            finished.add(sid)
    return finished


# ----------------------------------------------------------------------------- what stands there

def tree_size(folder):
    """(number of files, the bytes that removing them gives back) under a folder; a file that cannot be read off
    counts as nothing.

    A file that has another name gives back nothing when this one goes. A build's lib holds such files: for a
    cached module that one of its compiles read, it names the cache's own file (lean_broker.restore_module),
    whose room goes with the entry of the cache and is counted there."""
    files = size = 0
    for top, _, names in os.walk(folder):
        for name in names:
            try:
                found = os.lstat(os.path.join(top, name))
            except OSError:
                continue
            files += 1
            if found.st_nlink <= 1:
                size += found.st_size
    return files, size


def survey_compiles(folder, pattern, finished, waiting):
    """Sort the folders of the jobs, or of the builds, under `folder` into those nothing reads again and the rest.

    `pattern` is the form of their IDs, `finished` the sessions whose work has finished processing, and `waiting`
    the IDs that have a request in the broker's queue. Returns a dictionary:

    - `unread`: the folders that nothing reads again, each as {'path', 'files', 'bytes'}. Such a folder holds a
      result.json that says the job or build has ended (lean_broker.FINISHED) and names, as the session that
      submitted it, a finished session or one of OWNERS. A request the broker answered as a duplicate has a
      result that names the job or build doing the work and no session; the same session submitted both
      (lean_broker.Broker.ingest, ingest_build), so its folder goes when that of the other one does, and stands
      before it in the list. A folder whose name begins with REMOVING was taken out of sight by a call that did
      not come to remove its files, and is listed as well.
    - `kept`: how many folders stay. A folder stays without a result.json, which is that of a job or build that
      has not ended; with a result that cannot be read; with a result that names another session, or the broker,
      as that of a calibration compile does, or no session, as that of a refused request does; and with a
      request still in the queue under its ID, which the next broker would otherwise register and compile again.
    - `keys`: the cache keys that the records of the folders that stay name.
    - `unreadable`: the ID of one folder whose result.json is there and could not be read, or None. Which
      entries of the cache such a record names is then not known."""
    ended, duplicates, keys, unread, kept, unreadable = {}, {}, set(), [], 0, None
    names = []
    if folder.is_dir():
        with os.scandir(folder) as listing:
            names = sorted(item.name for item in listing if item.is_dir(follow_symlinks=False))
    for name in names:
        if name.startswith(REMOVING):
            unread.append(name)
            continue
        if not pattern.fullmatch(name):
            kept += 1
            continue
        try:
            record = read_json(folder / name / 'result.json')
            if not isinstance(record, dict):
                raise ValueError('not an object')
        except FileNotFoundError:
            kept += 1
            continue
        except (OSError, ValueError):
            kept += 1
            unreadable = unreadable or name
            continue
        if record.get('status') == 'duplicate':
            duplicates[name] = record.get('duplicate_of')
            continue
        owner = record.get('session')
        ended[name] = (record.get('status') in FINISHED and isinstance(owner, str)
                       and (owner in finished or owner in OWNERS) and name not in waiting)
        if not ended[name]:
            kept += 1
            if record.get('key'):
                keys.add(record['key'])
            rows = record.get('modules')
            for row in rows.values() if isinstance(rows, dict) else ():
                if isinstance(row, dict) and row.get('key'):
                    keys.add(row['key'])
    answered = [name for name, target in duplicates.items()
                if isinstance(target, str) and ended.get(target) and name not in waiting]
    kept += len(duplicates) - len(answered)
    unread += answered + [name for name, over in ended.items() if over]
    listed = []
    for name in unread:
        files, size = tree_size(folder / name)
        listed.append({'path': folder / name, 'files': files, 'bytes': size})
    return {'unread': listed, 'kept': kept, 'keys': keys, 'unreadable': unreadable}


def canon_keys(instance, paths, broker):
    """The cache key of every module of the canon as it stands, by name, and None; or {} and the reason why the
    keys cannot be told.

    The keys are made as the broker makes them for a build of the canon in which every module comes from the
    cache (lean_broker.Broker.advance_build), with the broker's own functions: a module's key from the
    environment of the broker's saved state, the module's name, its source bytes, and the identity of the output
    of every local module its compile reads, taken from the manifest of that module's entry. A module's key can
    therefore be told only when the entries of the modules it reads are complete.

    They are given only when every module of the canon is found so. That is the case after any build of the
    canon in the environment the broker last ran in, and each publication that changes a Lean file is such a
    build. It is not the case after a change of Lean until the canon has been built again, nor when this
    function and the broker have come to differ in how they make a key. Entries that the canon uses could then
    not be told from the others, and the caller leaves the cache as it is.

    A saved state that holds no Lean version is given a reason of its own. A broker that starts writes its state
    without the version and reads the version after that (lean_broker.Broker.start); in between it asks lake
    for Lean's environment, which can take minutes. A state read in that time, as after a broker was ended while
    it started, gives keys under which the cache holds nothing. Reported as a cache without the canon's modules,
    that case would read to an operator as a canon that has to be built again."""
    try:
        library = read_json(instance / 'instance.json')['library']
        lean_root = Canon(instance).lean
        modules = discover_modules(lean_root, [path for _, path in library_modules(lean_root, library)])
    except (OSError, ValueError, KeyError, TypeError) as exc:
        return {}, f'the modules of the canon could not be read: {exc}'
    if not modules:
        return {}, 'the canon holds no module'
    if 'version' in broker and broker['version'] is None and not broker.get('version_error'):
        return {}, ("the broker's saved state holds no Lean version, because the broker that wrote it had not yet "
                    'read the version, as a broker that is still starting has not; the keys of the cache are made '
                    'from the version, so run cleanup again once `status` shows it under `lean`')
    try:
        environment = environment_of(broker)
    except (KeyError, TypeError):
        return {}, "the broker's saved state names no Lean environment"
    keys, identities, absent = {}, {}, []
    for name, module in modules:
        if all(needed in identities for needed in module['needs']):
            key = module_key(environment, name, module['source_sha256'],
                             [(needed, identities[needed][module['reads']]) for needed in module['needs']])
            found = cached_entry(paths.cache, key)
            if found is not None:
                keys[name], identities[name] = key, found[1]
                continue
        absent.append(name)
    if absent:
        return {}, (f'the cache holds no complete entry for {len(absent)} of the {len(modules)} modules of the '
                    f'canon in the Lean environment the broker last ran in, {absent[0]} among them, so the '
                    'entries that the canon uses cannot be told from the others')
    return keys, None


def survey_cache(instance, paths, broker, named, unreadable):
    """Sort the files of the module cache into the entries that nothing reads again and the rest.

    `broker` is the broker's saved state, `named` the keys that the records of the builds and jobs that stay
    name, and `unreadable` the ID of a build whose record could not be read, or None. Returns a dictionary:

    - `skipped`: None, or the reason why the cache is left as it is: a record that could not be read, or keys
      of the canon that cannot be told (canon_keys). The other lists are then empty.
    - `unread`: the entries that go, each key with {suffix: bytes} for its files. An entry goes when no module
      of the canon has its key, no record that stays names it, and the broker's saved state names it in no build
      that has not ended. A build that has not ended has no result yet, and the broker that takes it up again
      reads the modules it had counted as cached under the keys in that state (lean_broker.Broker.advance_build).
      The caller cleans only when there is no such build; they are read all the same.
    - `unfinished`: the files (path, bytes) that a broker left while it was writing an entry (UNFINISHED_FILE).
    - `kept`: how many entries stay for the canon and how many more for the builds and jobs that stay, and how
      many names in the folder are of neither form and stay because nothing here knows what they are."""
    entries, unfinished, unknown = {}, [], 0
    if paths.cache.is_dir():
        with os.scandir(paths.cache) as listing:
            for item in listing:
                try:
                    regular = item.is_file(follow_symlinks=False)
                    size = item.stat(follow_symlinks=False).st_size if regular else 0
                except OSError:
                    continue  # gone since it was listed
                entry = ENTRY_FILE.fullmatch(item.name) if regular else None
                if entry:
                    entries.setdefault(entry[1], {})[entry[2]] = size
                elif regular and UNFINISHED_FILE.fullmatch(item.name):
                    unfinished.append((Path(item.path), size))
                else:
                    unknown += 1
    reason = canon = None
    if unreadable:
        reason = (f'the record of the build {unreadable} could not be read, so the entries of the cache that it '
                  'names are not known')
    else:
        canon, reason = canon_keys(instance, paths, broker)
    if reason:
        return {'skipped': reason, 'unread': {}, 'unfinished': [], 'kept': {'entries': len(entries)}}
    stated = {row['key'] for build in broker.get('builds', {}).values() if build['status'] in ACTIVE
              for row in build.get('modules', {}).values() if row.get('key')}
    used = set(canon.values())
    others = (named | stated) - used
    return {'skipped': None,
            'unread': {key: files for key, files in entries.items() if key not in used and key not in others},
            'unfinished': unfinished,
            'kept': {'canon': len(used), 'named_by_builds': len(others & set(entries)), 'unknown_files': unknown}}


def survey(instance, paths):
    """What a cleaning would remove as the instance stands at this moment, and what it would keep.

    Nothing is changed. Everything is read from the instance: the runner's state for the sessions whose work
    has finished processing, the result of each job and build for the one that submitted it, the broker's
    saved state and the canon's own files for the entries of the cache that are still used."""
    state = read_json(instance / 'runner/state.json')
    finished = finished_sessions(state)
    broker = read_json(paths.state) if paths.state.exists() else {}
    waiting = {path.stem for path in paths.queue.glob('*.json')} if paths.queue.is_dir() else set()
    builds = survey_compiles(paths.builds, BUILD_ID, finished, waiting)
    jobs = survey_compiles(paths.jobs, JOB_ID, finished, waiting)
    cache = survey_cache(instance, paths, broker, builds['keys'] | jobs['keys'], builds['unreadable'])
    return {'builds': builds, 'jobs': jobs, 'cache': cache}


def removable(found):
    """The count of what a survey lists for removal, in the form in which `sweep` counts what it removed."""
    cache = found['cache']
    sizes = [size for files in cache['unread'].values() for size in files.values()]
    sizes += [size for _, size in cache['unfinished']]
    count = {'cache': {'entries': len(cache['unread']), 'files': len(sizes), 'bytes': sum(sizes)}}
    for kind in ('builds', 'jobs'):
        count[kind] = {'folders': len(found[kind]['unread']),
                       'files': sum(folder['files'] for folder in found[kind]['unread']),
                       'bytes': sum(folder['bytes'] for folder in found[kind]['unread'])}
    return count


# ----------------------------------------------------------------------------- removing

def sweep(paths, found):
    """Remove what a survey listed. Returns (the count of what was removed, what could not be removed).

    Every step leaves the instance in a state from which it runs as before, and a call that is cut short at any
    point is completed by the next call.

    An entry of the cache loses its manifest first. From that moment the broker takes the entry for absent
    (lean_broker.cached_entry) and a build compiles the module, so no entry is read with part of its files. The
    emitted files go next and the two logs last. When the manifest cannot be removed, the entry is left whole.
    Files that a removed manifest leaves behind, here or after a cut, belong to no entry; the next survey lists
    them under their key again, and a compile that stores the entry anew writes over them.

    The folder of a job or build is first renamed, in one step, to a name that is no ID (REMOVING), and its files
    are removed after that. Whoever opens the folder by its ID finds it whole or does not find it. A folder that
    was renamed and not emptied is found by the next survey.

    A file or folder that the system refuses to remove, as Windows does while another process holds it, stays
    and is listed; nothing waits for it. An entry whose manifest is refused stays whole, and so does a folder
    that cannot be renamed."""
    count = {'cache': {'entries': 0, 'files': 0, 'bytes': 0},
             'builds': {'folders': 0, 'files': 0, 'bytes': 0}, 'jobs': {'folders': 0, 'files': 0, 'bytes': 0}}
    left = []

    def remove_file(path, size):
        try:
            os.unlink(path)
        except FileNotFoundError:
            return True
        except OSError as exc:
            left.append({'path': str(path), 'error': str(exc)})
            return False
        count['cache']['files'] += 1
        count['cache']['bytes'] += size
        return True

    for key, files in found['cache']['unread'].items():
        if MANIFEST in files and not remove_file(paths.cache / (key + MANIFEST), files[MANIFEST]):
            continue
        for suffix in sorted(set(files) - {MANIFEST}, key=lambda suffix: (suffix.endswith('.log'), suffix)):
            remove_file(paths.cache / (key + suffix), files[suffix])
        count['cache']['entries'] += 1
    for path, size in found['cache']['unfinished']:
        remove_file(path, size)

    def refused(function, path, error):
        left.append({'path': str(path), 'error': str(error)})

    for kind in ('builds', 'jobs'):
        for folder in found[kind]['unread']:
            path = folder['path']
            if not path.name.startswith(REMOVING):
                moved = path.with_name(REMOVING + path.name)
                try:
                    os.rename(path, moved)
                except FileNotFoundError:
                    continue
                except OSError as exc:
                    left.append({'path': str(path), 'error': str(exc)})
                    continue
                path = moved
            shutil.rmtree(path, onexc=refused)
            if not path.exists():
                for unit, amount in (('folders', 1), ('files', folder['files']), ('bytes', folder['bytes'])):
                    count[kind][unit] += amount
    return count, left


def end_broker(paths):
    """End the instance's broker, when one is alive, and take the lock that a broker holds for its life.

    Returns the lock, entered, and whether a broker was alive. A broker reads the cache for a build, stores
    entries in it and writes the results of jobs and builds, and it does all of that under runner/lean/lock
    (lean_broker.Broker.serve). So for as long as the caller holds the lock, no build is registered or carried
    forward and no compile is started or collected, whatever a session, the runner or an operator asks for
    meanwhile: the request waits in the queue for the broker that follows. A runner that is alive starts a
    broker when it finds none (Runner.ensure_broker). Such a broker ends at the lock, or, where it took the
    lock first, is ended here like the one before it. The lock is the system's and is released when the
    process that holds it ends."""
    was_alive = False
    deadline = time.monotonic() + 60
    while True:
        info = broker_alive(paths)
        if info:
            was_alive = True
            try:
                terminate_process(info['process'])
            except (OSError, RuntimeError):
                pass  # it has ended since it was found alive
            ended = time.monotonic() + 10
            while alive(info['process']) and time.monotonic() < ended:
                time.sleep(0.05)
            if alive(info['process']):
                raise RuntimeError('the Lean broker did not end; nothing was removed')
        lock = InstanceLock(paths.lock, 'Lean broker', wait=2.0)
        try:
            lock.__enter__()
            return lock, was_alive
        except RuntimeError:
            if time.monotonic() >= deadline:
                raise RuntimeError('the lock of the Lean broker could not be taken; nothing was removed') from None


def repository(instance, pack):
    """Git's count of the objects of the instance's repository: how many are loose, their bytes, and the bytes of
    the packs. With `pack`, the count before and after Git has packed them.

    Every publication commits knowledge/ and canon/, and each object of a commit is first a file of its own.
    `git gc` writes those objects into one pack, where versions of a file are kept as their differences, and
    removes a loose object only once a pack in its place holds it, so a packing that is cut short loses
    nothing. No commit is removed, and Git does the same by itself after a commit once the loose objects are
    several thousand. What Git refuses is returned as `error` and stops nothing."""
    def count():
        counted = dict(line.split(': ', 1) for line in git(instance, 'count-objects', '-v').splitlines())
        return {'loose_objects': int(counted['count']), 'loose_bytes': int(counted['size']) * 1024,
                'packed_bytes': int(counted['size-pack']) * 1024}
    try:
        before = count()
        if not pack:
            return before
        git(instance, 'gc', '--quiet')
        return {'before': before, 'after': count()}
    except (OSError, RuntimeError, ValueError, KeyError) as exc:
        return {'error': str(exc)}


def clean(instance, dry_run=False):
    """The operator's `cleanup`: remove what no program reads again, or with `dry_run` say what would be removed.

    A dry run changes nothing and can be made at any time. Its result gives `conditions`, what does not hold
    of the conditions at this moment (unmet_conditions), and `removable`, the count of what a cleaning would
    remove as the instance stands.

    A cleaning removes nothing while a condition does not hold, and its refusal names each one. It then ends
    the broker and takes the broker's lock (end_broker), reads the conditions once more, in case work began
    between the first reading and the lock, surveys the instance and removes what the survey lists (sweep),
    all under the lock. The lock is what makes the removal safe against work that begins meanwhile. A build is
    carried forward by the broker alone, and only a build that is being carried forward can have counted an
    entry of the cache as present without having read it yet. Under the lock no build is carried forward, and a
    build that a broker registers after the lock is released looks every entry up afresh. The folders of jobs
    and builds that go belong to readers that are gone for good, and nothing that begins brings such a reader
    back. After the lock is released, a broker is started again when one was alive, and Git packs the
    repository (repository).

    The result gives `removed`, the count of what was removed; `left`, how many files and folders could not
    be removed, with the first of them by path; `kept`, how many folders and entries stay; `cache_skipped`,
    the reason when the cache was left as it is; `broker`, the receipt of the broker that was started, or
    None; and `repository`."""
    instance = Path(instance).resolve()
    paths = Paths(instance)
    unmet = unmet_conditions(instance)
    if dry_run:
        found = survey(instance, paths)
        result = {'dry_run': True, 'conditions': unmet, 'removable': removable(found)}
    else:
        if unmet:
            raise ValueError('nothing was removed: ' + '; '.join(unmet))
        lock, was_alive = end_broker(paths)
        broker = None
        try:
            unmet = unmet_conditions(instance)
            if unmet:
                raise ValueError('nothing was removed, because the instance took up work while the command began: '
                                 + '; '.join(unmet))
            found = survey(instance, paths)
            count, left = sweep(paths, found)
        finally:
            lock.__exit__(None, None, None)
            if was_alive:
                try:
                    broker = ensure_broker(paths)
                except (OSError, RuntimeError) as exc:
                    broker = {'error': str(exc)}
        result = {'dry_run': False, 'conditions': [], 'removed': count,
                  'left': {'count': len(left), 'first': left[:SHOWN]}, 'broker': broker}
    result['kept'] = {'builds': found['builds']['kept'], 'jobs': found['jobs']['kept'], 'cache': found['cache']['kept']}
    result['cache_skipped'] = found['cache']['skipped']
    if (instance / '.git').is_dir():
        result['repository'] = repository(instance, pack=not dry_run)
    return result
