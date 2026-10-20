"""Storage lifecycle: isolation, exact history, safe cleanup, and legacy migration."""
import json
from pathlib import Path
import shutil
import sys
import tempfile
import unittest
from unittest.mock import patch

ENGINE = Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ENGINE))
import workspaces as w
import check


class StorageTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name);self.repo=self.root/'repo';self.records=self.root/'records'
        (self.repo/'src').mkdir(parents=True);self.records.mkdir()
        (self.repo/'src/a.txt').write_text('old',encoding='utf-8')
        (self.repo/'src/data.bin').write_bytes(b'fixed input\0'*500)
        for name in ('context','plan','seams'):(self.records/(name+'.md')).write_text(name)
        self.task={'id':'a','kind':'work','depends_on':[],'writes':['src/a.txt','src/new.txt'], 'inputs':[]}
        self.home=self.records/'tasks/a'
        w.write_json(self.records/'queue.json',{'status':'active','tasks':[self.task],'accepted':[]})
        w.write_json(self.records/'state.json',{'tasks':{'a':{'status':'exited'}}})
        self.workspace=w.prepare(self.repo,self.records,self.task,{'snapshot_paths':['src']})
        (self.home/'objective.md').write_text('Change a')

    def accept(self):
        _,delta=w.changes(self.records,'a')
        w.write_json(self.home/'report.json',dict(status='complete',summary='Changed',changes=list(delta),verification='Verified',findings=[]))
        w.integrate(self.repo,self.records,'a')
        q=w.read_json(self.records/'queue.json');q['accepted']=['a'];w.write_json(self.records/'queue.json',q)

    def test_shared_baselines_are_independent_of_workers_and_live_source(self):
        other={**self.task,'id':'b'}
        second=w.prepare(self.repo,self.records,other,{'snapshot_paths':['src']})
        self.assertFalse((self.home/'base').exists())
        self.assertEqual(len(list((self.records/'objects').glob('*/*'))),2)
        (self.workspace/'src/a.txt').write_text('worker')
        (self.repo/'src/a.txt').write_text('user')
        self.assertEqual((second/'src/a.txt').read_text(),'old')
        dest=self.root/'baseline'
        w.restore(self.records,'a','baseline',dest)
        self.assertEqual((dest/'src/a.txt').read_text(),'old')
        with self.assertRaisesRegex(ValueError,'conflict'):w.integrate(self.repo,self.records,'a')

    def test_cleanup_preserves_history_evidence_and_changed_added_deleted_files(self):
        (self.workspace/'src/a.txt').unlink()
        (self.workspace/'src/new.txt').write_text('result')
        (self.home/'evidence').mkdir();(self.home/'evidence/review.md').write_text('independent finding')
        self.accept();(self.repo/'src/new.txt').write_text('later user revision')
        w.cleanup(self.records,'a')
        self.assertFalse(self.workspace.exists())
        self.assertEqual((self.home/'evidence/review.md').read_text(),'independent finding')
        check.report(self.records,'a');check.queue(self.records)
        out=self.root/'result';w.restore(self.records,'a','result',out)
        self.assertFalse((out/'src/a.txt').exists())
        self.assertEqual((out/'src/new.txt').read_text(),'result')
        # A duplicate completion event cannot reapply archived output over later work.
        w.integrate(self.repo,self.records,'a')
        self.assertEqual((self.repo/'src/new.txt').read_text(),'later user revision')
        w.cleanup(self.records,'a')
        self.assertEqual(w.cleanup_accepted(self.records),[])
        selected=self.root/'one-file';w.restore(self.records,'a','result',selected,['src/new.txt'])
        self.assertEqual(list(p.relative_to(selected).as_posix() for p in selected.rglob('*') if p.is_file()),['src/new.txt'])
        w.restore(self.records,'a','baseline',self.home/'evidence/old',['src/a.txt'])
        self.assertEqual((self.home/'evidence/old/src/a.txt').read_text(),'old')
        with self.assertRaisesRegex(ValueError,'managed task snapshots'):
            w.restore(self.records,'a','result',self.workspace)

    def test_unaccepted_running_and_unintegrated_work_is_retained(self):
        with self.assertRaisesRegex(ValueError,'not accepted'):w.cleanup(self.records,'a')
        self.accept()
        w.write_json(self.records/'state.json',{'tasks':{'a':{'status':'running'}}})
        with self.assertRaisesRegex(ValueError,'not terminated'):w.cleanup(self.records,'a')
        w.write_json(self.records/'state.json',{'tasks':{'a':{'status':'exited'}}})
        (self.workspace/'src/a.txt').write_text('unintegrated')
        with self.assertRaisesRegex(ValueError,'Unintegrated'):w.cleanup(self.records,'a')
        self.assertTrue(self.workspace.exists())

    def test_changed_output_after_integration_cannot_be_cleaned(self):
        (self.workspace/'src/a.txt').write_text('first');self.accept()
        (self.workspace/'src/a.txt').write_text('second')
        with self.assertRaisesRegex(ValueError,'Integrated content changed'):w.cleanup(self.records,'a')
        self.assertEqual((self.repo/'src/a.txt').read_text(),'first')
        self.assertTrue(self.workspace.exists())

    def test_legacy_base_migration_and_cleanup_interruption(self):
        # Simulate the old two-copy layout with its path-only integration receipt.
        shutil.copytree(self.workspace,self.home/'base')
        shutil.rmtree(self.records/'objects')
        (self.workspace/'src/a.txt').write_text('new');self.accept()
        receipt=w.read_json(self.home/'integration.json');receipt.pop('changes')
        w.write_json(self.home/'integration.json',receipt)
        real_remove=w._remove_snapshot
        def interrupt(home,name,inventory):
            if name=='workspace':
                (home/'workspace/src/data.bin').unlink()
                raise OSError('simulated interruption')
            return real_remove(home,name,inventory)
        with patch.object(w,'_remove_snapshot',side_effect=interrupt):
            with self.assertRaisesRegex(OSError,'simulated'):w.cleanup(self.records,'a')
        self.assertTrue((self.home/'archive.json').exists())
        w.cleanup(self.records,'a')
        for version,expected in [('baseline','old'),('result','new')]:
            dest=self.root/version;w.restore(self.records,'a',version,dest)
            self.assertEqual((dest/'src/a.txt').read_text(),expected)
            self.assertEqual((dest/'src/data.bin').read_bytes(),b'fixed input\0'*500)

    def test_corrupt_object_prevents_deletion_and_restore(self):
        self.accept()
        digest=w.read_json(self.home/'baseline.json')['src/a.txt']
        obj=w.object_path(self.records,digest);obj.write_text('corrupt')
        with self.assertRaisesRegex(ValueError,'baseline content'):w.cleanup(self.records,'a')
        self.assertTrue(self.workspace.exists())
        with self.assertRaisesRegex(ValueError,'corrupt'):w.restore(self.records,'a','baseline',self.root/'restore')
        self.assertFalse((self.root/'restore').exists())

    def test_cleanup_does_not_follow_directory_links(self):
        self.accept();outside=self.root/'external';outside.mkdir();(outside/'important').write_text('keep')
        link=self.workspace/'linked'
        if sys.platform=='win32':
            import subprocess
            result=subprocess.run(['cmd','/c','mklink','/J',str(link),str(outside)],capture_output=True)
            if result.returncode:self.skipTest('Cannot create junction')
        else:link.symlink_to(outside,target_is_directory=True)
        try:
            with self.assertRaisesRegex(ValueError,'Linked'):w.cleanup(self.records,'a')
            self.assertTrue((outside/'important').exists())
        finally:
            if sys.platform=='win32':link.rmdir()
            else:link.unlink()


if __name__=='__main__':unittest.main()
