"""삼킨 예외는 유형과 함께 난 자리를 보고한다.

실측: ScienceDirect의 두 번째 원문 확보가 {'code':'fulltext_retrieval_failed','error_type':'TimeoutError'}로만 보고되어
어느 대기가 소진됐는지 알 수 없었다. 예외 메시지는 인증 URL을 담을 수 있어 버리지만, 우리 코드의 파일·줄·함수는 비밀을 담을 수 없다.
"""
import re, sys, unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
BARE = re.compile(r"""(?<![\w])error_type['"]?\s*[:=]\s*type\(""")


class FailureDetails(unittest.TestCase):
    def test_details_name_the_innermost_project_frame_and_drop_the_message(self):
        from scholarly import failure_details
        def adapter_step():
            raise TimeoutError('https://example.org/?token=SYNTHETIC-PRIVATE')
        try:
            adapter_step()
        except Exception as error:
            details = failure_details(error)
        self.assertEqual(details['error_type'], 'TimeoutError')
        self.assertEqual((details['where']['file'], details['where']['function']), ('test_failure_details.py', 'adapter_step'))
        self.assertNotIn('SYNTHETIC-PRIVATE', repr(details))

    def test_no_module_reports_an_exception_type_without_its_location(self):
        offenders = [f"{path.name}:{number}" for path in sorted(ROOT.glob('*.py')) if path.name != 'scholarly.py'
                     for number, line in enumerate(path.read_text(encoding='utf-8').splitlines(), 1) if BARE.search(line)]
        self.assertEqual(offenders, [], 'report swallowed exceptions with **failure_details(error)')


if __name__ == '__main__':
    unittest.main()
