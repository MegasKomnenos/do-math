"""The operator's `cleanup` on an instance whose compiles a fake lean made: what goes, what stays, and when
nothing goes; no Lean is run."""

import json
import os
from pathlib import Path
import shutil
import sys
import time
import unittest
from unittest.mock import patch

sys.path[:0] = [str(Path(__file__).resolve().parents[1]), str(Path(__file__).resolve().parent)]
import cleanup
import lean_broker
import runtime_support
from runner import main
from broker_fixture import BrokerFixture, source
from support import kept_copy

# The instance that `CleanupTests.research` builds and the IDs it returns, made once for the test process; every
# test that asks for it works on a copy of its own.
RESEARCH = {}
NOTHING = {'cache': {'entries': 0, 'files': 0, 'bytes': 0}, 'builds': {'folders': 0, 'files': 0, 'bytes': 0},
           'jobs': {'folders': 0, 'files': 0, 'bytes': 0}}


def write_library(root, change=None):
    """The library `Lib` under a module root: Lib.A imports the imported library and Lib.B imports Lib.A. With
    `change`, Lib.B holds a further line, so its source, its key and its output are others. Returns the target."""
    source(root / 'Lib/A.lean', module=True)
    source(root / 'Lib/B.lean', imports=('Lib.A',), module=True, **({'marker': change} if change else {}))
    return [root / 'Lib/B.lean']


class FinishedSessionTests(unittest.TestCase):
    def test_a_session_is_finished_when_it_holds_no_slot_and_its_pipeline_or_its_own_job_is_over(self):
        state = {
            'sessions': {'published': {'job': 'a', 'status': 'integrated'},
                         'awaiting review': {'job': 'b', 'status': 'ended'},
                         'publishing': {'job': 'c', 'status': 'publishing'},
                         'replaced': {'job': 'd', 'status': 'failed'},
                         'organized': {'job': 'e', 'status': 'integrated'},
                         'handed over': {'job': 'f', 'status': 'ended'},
                         'dropped': {'job': 'g', 'status': 'failed'}},
            'jobs': {'a': {'pipeline': 'p1', 'status': 'done'}, 'b': {'pipeline': 'p2', 'status': 'done'},
                     'c': {'pipeline': 'p1', 'status': 'running'}, 'd': {'pipeline': 'p2', 'status': 'cancelled'},
                     'e': {'pipeline': None, 'status': 'done'}, 'f': {'pipeline': None, 'status': 'pending'},
                     'g': {'pipeline': None, 'status': 'cancelled'}},
            'pipelines': {'p1': {'stage': 'done'}, 'p2': {'stage': 'review'}}}
        # A session of a pipeline that has not reached `done` stays out whatever its own status and its own
        # job say, and so does the session of a job without a pipeline that waits for its next session.
        self.assertEqual(cleanup.finished_sessions(state), {'published', 'organized', 'dropped'})


class CleanupTests(BrokerFixture):
    """`cleanup` on an instance whose canon is the library of `write_library`.

    `research` gives the state most tests start from. The runner's state names three sessions: `sdone`, whose
    work has finished processing; `sopen`, which has ended while its pipeline waits for review; and `sheld`,
    which is held behind the stop for its next turn. `sdone` built the canon, the runner then built it with
    Lib.B changed, as a publication does, and `sopen` built a candidate that changes Lib.B once more. `sdone`
    and `sheld` each compiled one file of their own. So the cache holds four entries: Lib.A and the Lib.B of
    the canon as it stands, the Lib.B that the canon no longer has, and the Lib.B of the candidate. `sdone` also
    compiled a file whose import Lean rejects, so the broker's calibration of that import failed and the
    calibration table holds the verdict."""

    # session -> its status, the status of its job and the stage of its pipeline, once its compiles have ended
    ENDS = {'sdone': ('integrated', 'done', 'done'), 'sopen': ('ended', 'done', 'review'),
            'sheld': ('running', 'running', 'producing')}

    def setUp(self):
        super().setUp()
        runtime_support.write_json(self.instance / 'instance.json', {'schema': 2, 'library': 'Lib'})
        (self.instance / 'control').mkdir()

    def write_runner_state(self, ends):
        runtime_support.write_json(self.instance / 'runner/state.json', {
            'sessions': {sid: {'id': sid, 'job': 'job-' + sid, 'status': status, 'cli': None}
                         for sid, (status, _, _) in ends.items()},
            'jobs': {'job-' + sid: {'pipeline': 'pipe-' + sid, 'status': status}
                     for sid, (_, status, _) in ends.items()},
            'pipelines': {'pipe-' + sid: {'stage': stage} for sid, (_, _, stage) in ends.items()},
            'publication': None, 'publish_queue': [], 'finished': False})

    def carried(self, build_id):
        """The record of a build carried to its end, which is `finished`."""
        self.until(lambda: self.build_record(build_id)['status'] in lean_broker.FINISHED)
        record = self.build_record(build_id)
        self.assertEqual(record['status'], 'finished', record)
        return record

    def settle(self):
        """Let the hosts of the compiles end, which hold their logs until then, and have the broker under test
        write its state, as a served broker does when a command asks for it."""
        for host in list(self.broker.hosts.values()):
            host.wait(timeout=30)
        self.broker.dirty = True
        self.broker.save(now=True)

    def research(self):
        """Put the state that the class describes into the instance; returns the cache keys, by what they are the
        entry of, and the IDs of the builds and jobs, by who submitted them."""
        if not RESEARCH:
            # While the compiles run every session is live, so that the broker cancels none of them as orphaned.
            self.write_runner_state({sid: ('running', 'running', 'producing') for sid in self.ENDS})
            self.start_broker()
            canon = self.instance / 'canon/lean'
            first = self.carried(self.build(canon, write_library(canon), session='sdone'))
            published = self.carried(self.build(canon, write_library(canon, 'published'), session='runner'))
            candidate = self.instance / 'sessions/sopen/work/lean'
            proposed = self.carried(self.build(candidate, write_library(candidate, 'proposed'), session='sopen'))
            single = [self.submit(self.session_file(sid), expect_mb=40, session=sid) for sid in ('sdone', 'sheld')]
            single.append(self.submit(self.session_file('sdone', name='M.lean', imports=('Missing.Module',)),
                                      expect_mb=40, session='sdone'))
            self.until(lambda: all(self.finished(job) for job in single))
            self.assertEqual((published['modules']['Lib.A']['status'], proposed['modules']['Lib.A']['status']),
                             ('cached', 'cached'))
            jobs = self.broker.state['jobs']
            owners = {job_id: job['session'] for job_id, job in jobs.items()}
            rejected = [job_id for job_id, job in jobs.items() if job['kind'] == 'calibration' and job['exit_code']]
            self.assertEqual(len(rejected), 1, rejected)
            ids = {'A': first['modules']['Lib.A']['key'], 'B first': first['modules']['Lib.B']['key'],
                   'B published': published['modules']['Lib.B']['key'],
                   'B proposed': proposed['modules']['Lib.B']['key'],
                   'build sdone': first['id'], 'build runner': published['id'], 'build sopen': proposed['id'],
                   'file of sdone': single[0],
                   'jobs unread': sorted(job for job, owner in owners.items() if owner in ('sdone', 'runner')),
                   'jobs kept': sorted(job for job, owner in owners.items() if owner in ('sopen', 'sheld')),
                   'calibrations': sorted(job for job, owner in owners.items() if owner == 'broker'),
                   'calibration rejected': rejected[0], 'closure rejected': jobs[rejected[0]]['closure']}
            self.assertEqual(len({ids[name] for name in ('A', 'B first', 'B published', 'B proposed')}), 4)
            self.assertEqual(len(ids['jobs unread']) + len(ids['jobs kept']) + len(ids['calibrations']), len(owners))
            self.assertGreater(len(ids['calibrations']), 1)  # the calibrations that Lean accepted are among them
            self.write_runner_state(self.ENDS)
            runtime_support.write_json(self.instance / 'sessions/sheld/end-check.json', {'status': 'waiting_dispatch'})
            self.settle()
            RESEARCH.update(instance=kept_copy(self.instance, 'do-math-cleanup-'), ids=ids)
        else:
            shutil.rmtree(self.instance)
            shutil.copytree(RESEARCH['instance'], self.instance)
        return RESEARCH['ids']

    def command(self, *options):
        """The operator's command through the runner's own entry: its exit code and what it printed."""
        with patch('builtins.print') as shown:
            code = main(['cleanup', str(self.instance), *options])
        return code, json.loads(shown.call_args.args[0])

    def held(self):
        """Every file and folder under the three folders that `cleanup` removes from, by its path from
        runner/lean."""
        return sorted(path.relative_to(self.paths.root).as_posix()
                      for folder in (self.paths.cache, self.paths.builds, self.paths.jobs)
                      for path in folder.rglob('*'))

    def names(self, folder):
        return {path.name for path in folder.iterdir()}

    def entry(self, key):
        return lean_broker.cached_entry(self.paths.cache, key)

    # -- what goes and what stays ------------------------------------------------------------------------

    def test_what_nothing_reads_again_goes_and_everything_else_stays(self):
        ids = self.research()
        (self.instance / 'control/STOP').touch()
        # Folders that stand beside the compiles of the research, made by hand. Two builds that the broker
        # answered as duplicates: one of a build that goes, one of a build that stays.
        answered, repeated = 'b' + '1' * 32, 'b' + '2' * 32
        for build, of in ((answered, ids['build sdone']), (repeated, ids['build sopen'])):
            (self.paths.builds / build).mkdir()
            runtime_support.write_json(self.paths.builds / build / 'result.json',
                                       {'id': build, 'status': 'duplicate', 'duplicate_of': of})
        # A build that has not ended has no result, and a request the broker refused has a result that names no session.
        unended, refused = 'b' + '3' * 32, 'j' + '4' * 32
        (self.paths.builds / unended).mkdir()
        (self.paths.jobs / refused).mkdir()
        runtime_support.write_json(self.paths.jobs / refused / 'result.json',
                                   {'id': refused, 'status': 'failed', 'reason': 'request rejected: no source'})
        # A folder and a file of no known form, and a file that a broker left while it wrote an entry.
        (self.paths.jobs / 'notes').mkdir()
        (self.paths.cache / 'README').write_text('not an entry', encoding='utf-8')
        unfinished = self.paths.cache / ('.' + 'a' * 32 + '.olean.' + 'b' * 32)
        unfinished.write_bytes(b'half')
        # A request that is still in the queue under the ID of a job that would otherwise go: the compile of the
        # one file that the finished session submitted by itself.
        waiting = ids['file of sdone']
        runtime_support.write_json(self.paths.queue / (waiting + '.json'), {'id': waiting})

        before = self.held()
        code, shown = self.command('--dry-run')
        self.assertEqual((code, shown['conditions'], shown['dry_run']), (0, [], True), shown)
        self.assertEqual(self.held(), before)  # a dry run changes nothing
        self.assertFalse(self.paths.lock.exists())  # and has not come to the broker's lock

        code, done = self.command()
        self.assertEqual(code, 0, done)
        self.assertEqual(done['removed'], shown['removable'])  # what the dry run said would go is what went
        self.assertEqual((done['left']['count'], done['cache_skipped'], done['broker']), (0, None, None), done)
        # The cache: the entry of the Lib.B that the canon no longer has is gone with every file of it. The
        # entries of the canon stay, and so does the entry of the candidate, which the build of `sopen` names.
        self.assertEqual(done['removed']['cache']['entries'], 1)
        self.assertEqual(list(self.paths.cache.glob(ids['B first'] + '*')), [])
        for name in ('A', 'B published', 'B proposed'):
            self.assertIsNotNone(self.entry(ids[name]), name)
            self.assertTrue((self.paths.cache / (ids[name] + '.stdout.log')).is_file(), name)
        self.assertEqual(done['kept']['cache'], {'canon': 2, 'named_by_builds': 1, 'unknown_files': 1})
        self.assertTrue((self.paths.cache / 'README').is_file())
        self.assertFalse(unfinished.exists())
        # The builds: those of the finished session and of the runner are gone, with the duplicate of the first.
        self.assertEqual(self.names(self.paths.builds), {ids['build sopen'], repeated, unended})
        self.assertEqual(lean_broker.job_record(self.paths, ids['build sopen'])['status'], 'finished')
        # The jobs: those of the finished session and of the runner are gone. Those of the session whose pipeline
        # is open and of the session held behind the stop stay, with Lean's output, and so do the broker's
        # calibration compiles.
        self.assertEqual(self.names(self.paths.jobs),
                         {*ids['jobs kept'], *ids['calibrations'], refused, 'notes', waiting})
        for job in ids['jobs kept']:
            self.assertIn('compiled', (self.paths.jobs / job / 'stdout.log').read_text(encoding='utf-8'))
        self.assertEqual(done['kept']['jobs'], len(ids['jobs kept']) + len(ids['calibrations']) + 3)
        # The calibration that Lean rejected: the calibration table keeps the verdict and sends its reader to
        # that compile's output. The compile of the finished session that waited for it is gone, and what Lean
        # said of the import is still to be read where the table says.
        verdict = runtime_support.read_json(self.paths.calibration)['entries'][ids['closure rejected']]['failed']
        self.assertIn('see its stdout.log in runner/lean/jobs/' + ids['calibration rejected'], verdict['reason'])
        self.assertIn('unknown module', (self.paths.jobs / ids['calibration rejected'] / 'stdout.log')
                      .read_text(encoding='utf-8'))

        # The job whose request stood in the queue goes once the request is gone, and then nothing is left to remove.
        (self.paths.queue / (waiting + '.json')).unlink()
        code, done = self.command()
        self.assertEqual((code, done['removed']['jobs']['folders']), (0, 1), done)
        self.assertFalse((self.paths.jobs / waiting).exists())
        after = self.held()
        code, done = self.command()
        self.assertEqual((code, done['removed']), (0, NOTHING), done)
        self.assertEqual(self.held(), after)

    def test_nothing_goes_while_a_condition_does_not_hold(self):
        self.research()
        before = self.held()
        state_file = self.instance / 'runner/state.json'
        state, compiles = runtime_support.read_json(state_file), runtime_support.read_json(self.paths.state)

        def refused(reason):
            code, shown = self.command()
            self.assertEqual(code, 1, shown)
            self.assertIn('nothing was removed', shown['error'])
            self.assertIn(reason, shown['error'])
            self.assertEqual(self.held(), before)

        refused('new dispatch is not stopped')
        (self.instance / 'control/STOP').touch()
        # A session in a turn: it has no end check that says it waits behind the stop.
        turn = {'id': 'sturn', 'job': 'job-sheld', 'status': 'running', 'cli': None}
        runtime_support.write_json(state_file, {**state, 'sessions': {**state['sessions'], 'sturn': turn}})
        refused('CLI turns are still running: sturn')
        # A session whose work waits for publication, a publication under way, and one that waits in the queue.
        runtime_support.write_json(state_file, {**state, 'sessions': {**state['sessions'],
                                                                      'sturn': {**turn, 'status': 'publishing'}}})
        refused('a publication is under way or waits in state.publish_queue, for the sessions sturn')
        runtime_support.write_json(state_file, {**state, 'publication': {'stage': 'build'}})
        refused('a publication is under way')
        runtime_support.write_json(state_file, {**state, 'publish_queue': [{'kind': 'questions'}]})
        refused('a publication is under way')
        runtime_support.write_json(state_file, state)
        # A compile that has not ended, and a build that has not.
        for kind in ('jobs', 'builds'):
            identifier = sorted(compiles[kind])[0]
            unended = {**compiles[kind], identifier: {**compiles[kind][identifier], 'status': 'queued'}}
            runtime_support.write_json(self.paths.state, {**compiles, kind: unended})
            refused('Lean compiles are queued or running: ' + identifier)
        runtime_support.write_json(self.paths.state, compiles)
        # A dry run names the condition and still says what would go.
        (self.instance / 'control/STOP').unlink()
        code, shown = self.command('--dry-run')
        self.assertEqual((code, shown['conditions']), (0, ['new dispatch is not stopped; run stop first']), shown)
        self.assertEqual(shown['removable']['cache']['entries'], 1)
        self.assertEqual(self.held(), before)

    def test_the_cache_is_left_as_it_is_when_what_the_canon_uses_cannot_be_told(self):
        ids = self.research()
        (self.instance / 'control/STOP').touch()
        cache = self.names(self.paths.cache)
        # A build whose record cannot be read may name any entry.
        broken = self.paths.builds / ('b' + '5' * 32)
        broken.mkdir()
        (broken / 'result.json').write_text('{', encoding='utf-8')
        code, done = self.command()
        self.assertEqual(code, 0, done)
        self.assertIn(broken.name, done['cache_skipped'])
        self.assertEqual((self.names(self.paths.cache), done['removed']['cache']), (cache, NOTHING['cache']))
        self.assertTrue(broken.is_dir())
        self.assertFalse((self.paths.builds / ids['build sdone']).exists())  # the folders went all the same
        shutil.rmtree(broken)
        # After a change of Lean the cache holds nothing of the canon under the new environment.
        self.write_settings(cache_epoch='second')
        self.start_broker()
        code, done = self.command()
        self.assertEqual(code, 0, done)
        self.assertIn('2 of the 2 modules', done['cache_skipped'])
        self.assertEqual(self.names(self.paths.cache), cache)
        # Once the canon is built there, the entries of the earlier environment go, apart from those that the
        # build of `sopen`, which stays, names: the Lib.A it took from the cache and the Lib.B it compiled.
        canon = self.instance / 'canon/lean'
        rebuilt = self.carried(self.build(canon, [canon / 'Lib/B.lean'], session='operator'))
        self.settle()
        code, done = self.command()
        self.assertEqual((code, done['cache_skipped']), (0, None), done)
        for name in ('B first', 'B published'):
            self.assertEqual(list(self.paths.cache.glob(ids[name] + '*')), [], name)
        for key in (ids['A'], ids['B proposed'], *(row['key'] for row in rebuilt['modules'].values())):
            self.assertIsNotNone(self.entry(key))

    def test_the_cache_is_left_for_its_own_reason_when_the_broker_had_not_yet_read_the_lean_version(self):
        ids = self.research()
        (self.instance / 'control/STOP').touch()
        cache = self.names(self.paths.cache)
        # A broker that starts writes its state without the Lean version and reads the version after that. This
        # one comes to an end in between, as a broker does that a cleaning ends while it starts.
        starting = lean_broker.Broker(self.instance, log_path=self.paths.log)
        with patch.object(starting, 'reload_settings', side_effect=KeyboardInterrupt), \
                self.assertRaises(KeyboardInterrupt):
            starting.start()
        saved = self.on_disk()
        self.assertEqual((saved['version'], saved['version_error'], 'environment_key' in saved), (None, None, True))
        code, done = self.command()
        self.assertEqual(code, 0, done)
        # The reason names the missing version. It does not say that the canon's modules are absent from the
        # cache, which an operator would read as a canon that has to be built again.
        self.assertIn('holds no Lean version', done['cache_skipped'])
        self.assertNotIn('no complete entry', done['cache_skipped'])
        self.assertEqual((self.names(self.paths.cache), done['removed']['cache']), (cache, NOTHING['cache']))
        self.assertFalse((self.paths.builds / ids['build sdone']).exists())  # the folders went all the same
        # Once a broker has read the version, the next call sweeps the cache.
        self.start_broker()
        code, done = self.command()
        self.assertEqual((code, done['cache_skipped']), (0, None), done)
        self.assertEqual(list(self.paths.cache.glob(ids['B first'] + '*')), [])
        for name in ('A', 'B published', 'B proposed'):
            self.assertIsNotNone(self.entry(ids[name]), name)

    # -- a cleaning that does not run to its end ----------------------------------------------------------

    def test_a_cleaning_that_is_cut_short_leaves_an_instance_that_builds_and_the_next_call_finishes_it(self):
        ids = self.research()
        (self.instance / 'control/STOP').touch()
        canon = self.instance / 'canon/lean'
        real_unlink, gone = os.unlink, []

        def cut_after_the_first_file(path, *args, **kwargs):
            if Path(path).parent == self.paths.cache:
                if gone:
                    raise KeyboardInterrupt
                gone.append(Path(path).name)
            return real_unlink(path, *args, **kwargs)

        with patch.object(os, 'unlink', cut_after_the_first_file), self.assertRaises(KeyboardInterrupt):
            cleanup.clean(self.instance)
        # The manifest went first, so the entry is absent to the broker while its other files still stand.
        self.assertEqual(gone, [ids['B first'] + cleanup.MANIFEST])
        self.assertIsNone(self.entry(ids['B first']))
        self.assertTrue((self.paths.cache / (ids['B first'] + '.olean')).is_file())
        with runtime_support.InstanceLock(self.paths.lock, 'Lean broker'):
            pass  # the lock was given back, so a broker can serve
        # The instance builds as before: the canon comes from the cache whole, and the module whose entry was
        # cut is compiled and stored again.
        self.start_broker()
        again = self.carried(self.build(canon, [canon / 'Lib/B.lean'], session='operator'))
        self.assertEqual({name: row['status'] for name, row in again['modules'].items()},
                         {'Lib.A': 'cached', 'Lib.B': 'cached'})
        earlier = self.instance / 'sessions/searlier/work/lean'
        rebuilt = self.carried(self.build(earlier, write_library(earlier), session='searlier'))
        self.assertEqual({name: (row['status'], row['exit_code']) for name, row in rebuilt['modules'].items()},
                         {'Lib.A': ('cached', 0), 'Lib.B': ('finished', 0)})
        self.assertEqual(rebuilt['modules']['Lib.B']['key'], ids['B first'])
        self.assertIsNotNone(self.entry(ids['B first']))
        self.settle()

        # Cut again, now after a folder was taken out of sight and before its files were removed.
        def cut(*args, **kwargs):
            raise KeyboardInterrupt

        with patch.object(shutil, 'rmtree', cut), self.assertRaises(KeyboardInterrupt):
            cleanup.clean(self.instance)
        moved = [name for name in self.names(self.paths.builds) if name.startswith(cleanup.REMOVING)]
        self.assertEqual(len(moved), 1)
        self.assertFalse((self.paths.builds / moved[0][len(cleanup.REMOVING):]).exists())  # found whole or not at all
        code, done = self.command()
        self.assertEqual((code, done['left']['count']), (0, 0), done)
        # The folder that was moved is gone with the others that nothing reads, the build of this test's own
        # session stays, and the entry it stored again stays with it.
        self.assertEqual(self.names(self.paths.builds), {ids['build sopen'], rebuilt['id']})
        self.assertEqual(done['removed']['builds']['folders'], 3)
        self.assertFalse(any(name.startswith(cleanup.REMOVING) for name in self.names(self.paths.jobs)))
        for name in ('A', 'B first', 'B published', 'B proposed'):
            self.assertIsNotNone(self.entry(ids[name]), name)

    def test_what_another_process_holds_stays_whole_and_is_named(self):
        ids = self.research()
        (self.instance / 'control/STOP').touch()
        manifest = self.paths.cache / (ids['B first'] + cleanup.MANIFEST)
        folder = self.paths.builds / ids['build sdone']
        real_unlink, real_rename = os.unlink, os.rename

        def unlink(path, *args, **kwargs):
            if Path(path) == manifest:
                raise PermissionError(13, 'The process cannot access the file', str(path))
            return real_unlink(path, *args, **kwargs)

        def rename(old, new, *args, **kwargs):
            if Path(old) == folder:
                raise PermissionError(13, 'The process cannot access the file', str(old))
            return real_rename(old, new, *args, **kwargs)

        with patch.object(os, 'unlink', unlink), patch.object(os, 'rename', rename):
            code, done = self.command()
        self.assertEqual((code, done['left']['count']), (0, 2), done)
        self.assertEqual({Path(item['path']).name for item in done['left']['first']}, {manifest.name, folder.name})
        # An entry whose manifest could not be removed keeps every file, and the folder keeps its result.
        self.assertIsNotNone(self.entry(ids['B first']))
        self.assertTrue((self.paths.cache / (ids['B first'] + '.stdout.log')).is_file())
        self.assertTrue((folder / 'result.json').is_file())
        self.assertFalse((self.paths.builds / ids['build runner']).exists())  # what nothing held went
        code, done = self.command()
        self.assertEqual((code, done['left']['count']), (0, 0), done)
        self.assertEqual(list(self.paths.cache.glob(ids['B first'] + '*')), [])
        self.assertFalse(folder.exists())

    def test_a_name_that_a_build_shares_with_the_cache_is_counted_without_its_bytes(self):
        # For a cached module that one of its compiles read, a build's lib names the cache's own file
        # (lean_broker.restore_module). Removing that name gives back no room: the room goes with the entry of
        # the cache and is counted there. So a cleaning counts such a file and none of its bytes.
        ids = self.research()
        _, before = self.command('--dry-run')
        lib = self.paths.builds / ids['build sdone'] / 'lib'
        lib.mkdir(exist_ok=True)
        try:
            os.link(self.paths.cache / (ids['A'] + '.olean'), lib / 'Shared.olean')
        except OSError:
            self.skipTest('the file system of the temporary folder makes no hard links')
        _, after = self.command('--dry-run')
        builds = before['removable']['builds']
        self.assertEqual(after['removable']['builds'], {**builds, 'files': builds['files'] + 1})

    # -- work that begins while the command runs -----------------------------------------------------------

    def test_work_that_begins_after_the_first_reading_is_met_by_a_second_reading_and_by_the_brokers_lock(self):
        self.research()
        (self.instance / 'control/STOP').touch()
        before = self.held()
        compiles = runtime_support.read_json(self.paths.state)
        registered = sorted(compiles['builds'])[0]
        end_broker = cleanup.end_broker

        def end_a_broker_that_has_registered_a_build(paths):
            # What a broker wrote last before it was ended: a build that it registered after the conditions were
            # read. The state holds it once the lock is taken, where the conditions are read again.
            lock_and_whether_one_was_alive = end_broker(paths)
            unended = {**compiles['builds'], registered: {**compiles['builds'][registered], 'status': 'queued'}}
            runtime_support.write_json(self.paths.state, {**compiles, 'builds': unended})
            return lock_and_whether_one_was_alive

        with patch.object(cleanup, 'end_broker', end_a_broker_that_has_registered_a_build):
            code, shown = self.command()
        self.assertEqual(code, 1, shown)
        self.assertIn('took up work while the command began', shown['error'])
        self.assertIn('Lean compiles are queued or running: ' + registered, shown['error'])
        self.assertEqual(self.held(), before)
        with runtime_support.InstanceLock(self.paths.lock, 'Lean broker'):
            pass  # the refusal gave the lock back
        runtime_support.write_json(self.paths.state, compiles)

        # A broker that starts while the instance is surveyed and swept asks for the lock and ends there
        # (lean_broker.Broker.serve), so it registers no build and carries none forward. Each of the two steps
        # asks for the lock here as that broker would.
        refusals = []

        def under_the_lock(step):
            def asked_first(*arguments):
                lock = runtime_support.InstanceLock(self.paths.lock, 'Lean broker')
                try:
                    lock.__enter__()
                except RuntimeError as exc:
                    refusals.append(str(exc))
                else:
                    lock.__exit__(None, None, None)
                    refusals.append(None)
                return step(*arguments)
            return asked_first

        with patch.object(cleanup, 'survey', under_the_lock(cleanup.survey)), \
                patch.object(cleanup, 'sweep', under_the_lock(cleanup.sweep)):
            code, done = self.command()
        self.assertEqual(code, 0, done)
        self.assertEqual(refusals, ['This instance already has a running Lean broker'] * 2)
        self.assertEqual(done['removed']['cache']['entries'], 1)  # and the cleaning went on under it

    # -- the broker, the repository and an instance without compiles ----------------------------------------

    def live_broker(self):
        """The receipt of the instance's detached broker, once one is alive."""
        deadline = time.monotonic() + lean_broker.READY_SECONDS
        while not lean_broker.broker_alive(self.paths) and time.monotonic() < deadline:
            time.sleep(0.05)
        return lean_broker.broker_alive(self.paths)

    def test_a_live_broker_is_ended_for_the_cleaning_with_one_that_took_the_lock_first_and_another_follows(self):
        ids = self.research()
        (self.instance / 'control/STOP').touch()
        lean_broker.launch_broker(self.paths)
        first = self.live_broker()['process']
        terminate, ended = cleanup.terminate_process, []

        def end_and_have_another_take_the_lock(identity):
            # A runner that is alive starts a broker when it finds none (Runner.ensure_broker). Here one is
            # started as soon as the first broker has ended, and it holds the lock before the cleaning asks for it.
            terminate(identity)
            ended.append(identity)
            if identity == first:
                self.wait_gone(first)
                lean_broker.launch_broker(self.paths)
                self.live_broker()
                # It answers a request for its state once it has started, and it has read the Lean version by then.
                self.assertIsNotNone(lean_broker.saved_state(self.paths, current=True)['version'])

        with patch.object(cleanup, 'terminate_process', end_and_have_another_take_the_lock):
            code, done = self.command()
        self.assertEqual(code, 0, done)
        # Both were ended: the broker that was alive, and the one that held the lock when the cleaning asked for it.
        self.assertEqual((len(ended), ended[0]), (2, first), ended)
        self.assertNotEqual(ended[1], first)
        self.assertFalse(any(runtime_support.alive(identity) for identity in ended))
        self.assertNotIn(done['broker']['process'], ended)
        self.assertEqual(lean_broker.broker_alive(self.paths)['process'], done['broker']['process'])
        self.assertEqual(list(self.paths.cache.glob(ids['B first'] + '*')), [])
        self.assertEqual(self.names(self.paths.builds), {ids['build sopen']})

    def test_the_repository_is_packed_and_keeps_its_commits(self):
        runtime_support.git(self.instance, 'init')
        for text in ('one', 'two'):
            (self.instance / 'root.md').write_text(text, encoding='utf-8')
            runtime_support.git(self.instance, 'add', '-f', '--', 'root.md')
            runtime_support.git(self.instance, 'commit', '-m', text)
        (self.instance / 'control/STOP').touch()
        code, done = self.command()
        self.assertEqual(code, 0, done)
        self.assertGreater(done['repository']['before']['loose_objects'], 0)
        self.assertEqual(done['repository']['after']['loose_objects'], 0)
        self.assertEqual(runtime_support.git(self.instance, 'log', '--format=%s').split(), ['two', 'one'])

    def test_an_instance_that_has_compiled_nothing_gives_up_nothing(self):
        code, shown = self.command()
        self.assertEqual(code, 1, shown)
        (self.instance / 'control/STOP').touch()
        code, done = self.command()
        self.assertEqual((code, done['removed'], done['left']['count']), (0, NOTHING, 0), done)
        self.assertIn('the canon holds no module', done['cache_skipped'])
        self.assertNotIn('repository', done)  # this fixture has no repository


if __name__ == "__main__":
    unittest.main()
