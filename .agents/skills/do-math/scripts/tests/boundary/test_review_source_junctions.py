"""Windows 정션으로 원천 경로가 작업 공간 밖을 가리키는 실제 경계."""
import _winapi

from do_math import review_cycle as rc
from support.review_owner_inputs import ReviewOwnerCase
from support.review_scene import warm


def setUpModule():
    warm()


class SourceJunctionTests(ReviewOwnerCase):
    def junction(self, link):
        target = self.root / 'outside'
        target.mkdir(exist_ok=True)
        link.parent.mkdir(parents=True, exist_ok=True)
        _winapi.CreateJunction(str(target), str(link))
        # rmdir은 정션 자체만 지운다. 대상은 이 시험의 Temp 안에 있다.
        self.addCleanup(link.rmdir)
        return target

    def test_review_source_directory_cannot_escape_workspace(self):
        _, action = self.opened()
        workspace = self.root / 'workspace'
        target = self.junction(workspace / 'input' / 'review-sources')
        with self.assertRaisesRegex(ValueError, 'review source directory escapes workspace'):
            self.engine._prepare_review_context(action, workspace)
        self.assertEqual(list(target.iterdir()), [])

    def test_review_source_file_cannot_follow_an_existing_junction(self):
        cid, action = self.opened()
        cycle = rc.record_turn(self.engine.runtime['review_cycles'][cid], action['slot'], [
            {'role': 'tool', 'message_id': 'source', 'content': '정확 원문'}])
        self.engine.runtime['review_cycles'][cid] = cycle
        digest = cycle['transcript_manifest'][action['slot']][0]['sha256']
        workspace = self.root / 'workspace'
        target = self.junction(workspace / 'input' / 'review-sources' / (digest + '.json'))
        with self.assertRaisesRegex(ValueError, 'review source file escapes its materialization directory'):
            self.engine._prepare_review_context(action, workspace)
        self.assertEqual(list(target.iterdir()), [])

    def test_research_source_directory_cannot_escape_workspace(self):
        workspace = self.root / 'workspace'
        target = self.junction(workspace / 'input' / 'review-research')
        source = rc.inline_source_row('proposal', {'text': '원문'})
        with self.assertRaisesRegex(ValueError, 'research source directory escapes workspace'):
            self.engine._materialize_research_sources([source], workspace)
        self.assertEqual(list(target.iterdir()), [])

    def test_research_source_file_cannot_follow_an_existing_junction(self):
        workspace = self.root / 'workspace'
        source = rc.inline_source_row('proposal', {'text': '원문'})
        target = self.junction(workspace / 'input' / 'review-research' / ('0000-' + source['sha256'] + '.json'))
        with self.assertRaisesRegex(ValueError, 'research source file escapes workspace'):
            self.engine._materialize_research_sources([source], workspace)
        self.assertEqual(list(target.iterdir()), [])
