import sys
from copy import deepcopy
from pathlib import Path

ROOT = next(p for p in Path(__file__).resolve().parents if (p / '.claude/skills/do-math').is_dir())
SCRIPTS = ROOT / '.claude/skills/do-math/scripts'
sys.path[:0] = [str(SCRIPTS), str(SCRIPTS / 'tests')]
from test_input_recovery import InputRecoveryPublicTests
from research_fixtures import trust_fixture
from do_math.engine import ResearchEngine, control

for field in ('foundation_profile', 'validation'):
    fixture = InputRecoveryPublicTests()
    fixture.setUp()
    try:
        request = trust_fixture(fixture.root, ['lean'])
        request['manifest'][field] = []
        accepted = control(fixture.repo, fixture.identifier, 'trust', config=request,
                           request_id='UC-bad-trust')
        assert accepted['accepted'] is True
        for attempt in range(2):
            owner = ResearchEngine(fixture.repo, fixture.identifier)
            try:
                owner.process_controls()
            except AttributeError as error:
                assert "has no attribute 'get'" in str(error), error
                assert 'UC-bad-trust' not in owner.runtime['processed_controls']
                print('CONFIRMED', field, 'restart', attempt, 'unhandled', repr(error))
            else:
                raise AssertionError('Expected current bug was not reproduced')
    finally:
        fixture.doCleanups()
