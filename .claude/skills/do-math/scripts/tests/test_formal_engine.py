"""Legacy continuation check retained: its inactive trust status is outside the storage schema."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from engine_fixtures import formal_check_engine
from research_fixtures import await_stop
from state_fixtures import owner_calls


class FormalContinuationTests(unittest.TestCase):
    def make(self):
        return formal_check_engine(self)

    def stopped_check(self, arguments):
        """The check reads its stop flag until the owner's judgment sets it."""
        if not await_stop(arguments['should_stop'], timeout=5):
            raise AssertionError('the owner control did not reach the check')
        return {'status': 'stopped'}

    def run_with_control(self, engine, action, operation):
        """Start the check, apply the control on the owner, then judge stops as a publication does."""
        engine.formal_behavior = self.stopped_check
        with owner_calls(engine) as calls:
            engine._formal(action)
            engine.control(operation, {})
            calls.judge()

    def test_resume_rechecks_source_trust_and_authority_before_another_call(self):
        for changed in ('source', 'trust', 'authority'):
            with self.subTest(changed=changed):
                engine, action = self.make()
                self.run_with_control(engine, action, 'pause')
                engine.control('resume', {})
                continuation = next(a for a in engine.runtime['queue'] if a.get('id') == action['id'])
                if changed == 'source':
                    fid = engine.instance['knowledge']['K1']['formal_result_id']
                    engine.instance['formal_results'][fid]['lean_code'] += '\n-- changed candidate'
                elif changed == 'trust':
                    engine.instance['trust_environments'][engine.instance['active_trust_environment']]['status'] = 'inactive'
                else:
                    engine.instance['grants']['GR-research']['status'] = 'revoked'
                engine.formal_behavior = None
                with owner_calls(engine):
                    engine._formal(continuation)
                self.assertEqual(len(engine.formal_calls), 1)


if __name__ == "__main__":
    unittest.main()
