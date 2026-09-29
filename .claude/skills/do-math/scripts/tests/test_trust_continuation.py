from pathlib import Path
import sys

SCRIPTS = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(SCRIPTS), str(SCRIPTS / 'tests')]
from unittest.mock import create_autospec, patch
from research_fixtures import bare_engine, trust_fixture


import unittest
import tempfile


class PublicationTrustIdentityTests(unittest.TestCase):
    def test_changed_identity_blocks_match_publication_but_olean_metadata_is_not_rechecked(self):
        from research_fixtures import trust_environment
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            request = trust_fixture(root, ['synthetic-lean'])
            environment, binding = trust_environment(request, environment_id='TE-test', source_ref='approved-test')
            engine = bare_engine()
            engine.instance = {'active_trust_environment':'TE-test', 'trust_environments':{'TE-test':environment}}
            from datetime import datetime, timezone
            engine.runtime = {'trust_transitions':{}, 'last_observed_utc':datetime.now(timezone.utc).isoformat(),
                              'trust_bindings':{'TE-test':binding}}
            engine._review_publication_premises = create_autospec(engine._review_publication_premises,
                return_value={'fixed':'same stored environment'})
            updated = {'id':'RC-test','proposal':{},'decision':'match','identity_basis':{},'policy_ref':'policy',
                       'publication_premises':{'fixed':'same stored environment'}}
            with patch('do_math.review_engine.identity_assessment', return_value={'decision':'match'}), \
                 patch('do_math.review_engine.kr.record_identity_assessment', side_effect=RuntimeError('publication reached')):
                with self.assertRaisesRegex(RuntimeError, 'publication reached'):
                    engine._publish_identity_review_result({'target':'KN-test'}, updated, 'EX-review')
                # The fingerprint was checked before compiling; publication checks only the identity.
                olean = Path(environment['toolchain']['executable']).parents[1] / 'lib/lean/Init/Prelude.olean'
                olean.write_bytes(b'changed module after the formal check')
                with self.assertRaisesRegex(RuntimeError, 'publication reached'):
                    engine._publish_identity_review_result({'target':'KN-test'}, updated, 'EX-review')
                Path(environment['toolchain']['executable']).write_bytes(b'changed compiler')
                with self.assertRaisesRegex(ValueError, 'current trust identity required: approved toolchain file changed'):
                    engine._publish_identity_review_result({'target':'KN-test'}, updated, 'EX-review')


if __name__ == '__main__':
    unittest.main()
