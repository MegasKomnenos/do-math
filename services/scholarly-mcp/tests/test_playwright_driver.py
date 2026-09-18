"""한 프로세스의 sync Playwright 드라이버는 하나다.

서버의 WORKER는 max_workers=1이므로 chromium·firefox·소유 Chrome 게이트웨이가 모두 같은 스레드에서 산다.
sync_playwright().start()를 그 스레드에서 두 번째로 부르면 Playwright가 거절한다:
"It looks like you are using Playwright Sync API inside the asyncio loop."
그러면 먼저 뜬 게이트웨이만 살고 나머지 자료원은 일반 Error로 영구히 실패한다.
"""
import sys
import tempfile
from pathlib import Path
from types import SimpleNamespace
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import browser_adapters
from browser_adapters import KudosGateway
from native_browser import NativeChromeGateway
from scholarly import Sanitizer, ServiceError


def recording_factory(starts, stops):
    """sync_playwright() 대역. 드라이버를 몇 번 시작하고 멈추는지 센다."""
    context = SimpleNamespace(set_default_timeout=lambda value: None, storage_state=lambda: {}, on=lambda event, callback: None)
    browser = SimpleNamespace(new_context=lambda **kwargs: context, close=lambda: None)
    engine = SimpleNamespace(launch=lambda **kwargs: browser)
    driver = SimpleNamespace(chromium=engine, firefox=engine, webkit=engine,
                             stop=lambda: stops.append(1))

    def start():
        starts.append(1)
        return driver

    return lambda: SimpleNamespace(start=start)


class SharedPlaywrightDriver(unittest.TestCase):
    def setUp(self):
        browser_adapters.DRIVER = None
        self.addCleanup(setattr, browser_adapters, 'DRIVER', None)

    def test_two_engines_in_one_thread_share_one_driver(self):
        starts, stops = [], []
        with tempfile.TemporaryDirectory() as temp, \
                patch('playwright.sync_api.sync_playwright', recording_factory(starts, stops)):
            first = KudosGateway(temp, Sanitizer(), engine='chromium')
            second = KudosGateway(temp, Sanitizer(), engine='firefox')
            first.start()
            second.start()
            self.assertEqual(len(starts), 1, 'a thread may hold only one sync Playwright driver')
            self.assertIs(first.playwright, second.playwright)

    def test_closing_one_gateway_leaves_the_shared_driver_running(self):
        starts, stops = [], []
        with tempfile.TemporaryDirectory() as temp, \
                patch('playwright.sync_api.sync_playwright', recording_factory(starts, stops)):
            first = KudosGateway(temp, Sanitizer(), engine='chromium')
            second = KudosGateway(temp, Sanitizer(), engine='firefox')
            first.start()
            second.start()
            first.close()
            self.assertEqual(stops, [], 'one gateway must not stop the driver the others still use')

    def test_the_owned_chrome_route_reuses_the_shared_driver(self):
        starts, stops = [], []
        exited = SimpleNamespace(poll=lambda: 1, pid=-1, wait=lambda timeout=None: 1,
                                 terminate=lambda: None, kill=lambda: None)
        with tempfile.TemporaryDirectory() as temp, \
                patch('playwright.sync_api.sync_playwright', recording_factory(starts, stops)), \
                patch('native_browser.Path.is_file', lambda path: path.is_absolute()), \
                patch('native_browser.subprocess.Popen', lambda *args, **kwargs: exited):
            KudosGateway(temp, Sanitizer(), engine='firefox').start()
            with self.assertRaises(ServiceError):
                NativeChromeGateway(temp, Sanitizer()).start()
            self.assertEqual(len(starts), 1, 'the owned Chrome route must reuse the shared driver')
            self.assertEqual(stops, [], 'a failed owned Chrome start must not stop the shared driver')


if __name__ == '__main__':
    unittest.main()
