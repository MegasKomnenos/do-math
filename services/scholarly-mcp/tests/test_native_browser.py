"""The native browser owns its listener, temporary files, and state snapshot."""
import json
import os
from pathlib import Path
import socket
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch
from uuid import uuid4

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from native_browser import NativeChromeGateway, owns_loopback_port
from scholarly import Sanitizer


class NativeBrowserContract(unittest.TestCase):
    @unittest.skipUnless(os.name == 'nt','Windows Chrome launch contract')
    def test_owned_profile_downloads_pdf_instead_of_opening_the_internal_viewer(self):
        from scholarly import ServiceError
        seen=[]
        def launched(arguments,**kwargs):
            profile=Path(next(value.split('=',1)[1] for value in arguments if value.startswith('--user-data-dir=')))
            preferences=profile/'Default/Preferences'
            seen.append(json.loads(preferences.read_text()) if preferences.exists() else None)
            raise RuntimeError('synthetic launch stop')
        with tempfile.TemporaryDirectory() as temp,patch('native_browser.Path.is_file',lambda path:path.is_absolute()), \
                patch('native_browser.subprocess.Popen',side_effect=launched):
            with self.assertRaises(ServiceError):
                NativeChromeGateway(temp,Sanitizer()).start()
        self.assertEqual(seen,[{'plugins':{'always_open_pdf_externally':True}}])

    def test_empty_install_roots_never_select_a_relative_chrome_executable(self):
        from scholarly import ServiceError
        with tempfile.TemporaryDirectory() as temp, patch.dict(os.environ,{'PROGRAMFILES':'','LOCALAPPDATA':''}), \
                patch('native_browser.Path.is_file',lambda path:not path.is_absolute()), \
                patch('native_browser.subprocess.Popen',side_effect=AssertionError('relative executable selected')) as launch:
            gateway=NativeChromeGateway(temp,Sanitizer())
            with self.assertRaises(ServiceError) as raised:
                gateway.start()
            self.assertEqual(raised.exception.result['code'],'browser_unavailable')
            launch.assert_not_called()

    @unittest.skipUnless(os.name == 'nt', 'Windows listener ownership API')
    def test_listener_must_belong_to_the_spawned_process(self):
        with socket.socket() as listener:
            listener.bind(('127.0.0.1', 0)); listener.listen()
            port = listener.getsockname()[1]
            self.assertTrue(owns_loopback_port(port, os.getpid()))
            self.assertFalse(owns_loopback_port(port, 0))

    def test_close_preserves_other_profiles_and_engine_states(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            gateway = NativeChromeGateway(root, Sanitizer())
            parent = root / 'scholarly-mcp/native-chrome-runs'
            owned = parent / 'owned-example'; owned.mkdir(parents=True)
            neighbor = parent / 'owned-other'; neighbor.mkdir(); (neighbor / 'keep').write_text('keep')
            other_state = root / 'scholarly-mcp/kudos-chromium.json'; other_state.write_text('existing')
            gateway._run = owned; gateway._ready = True
            gateway.context = SimpleNamespace(storage_state=lambda: {'cookies': [], 'origins': []})
            gateway._process = SimpleNamespace(wait=Mock(), poll=lambda: 0)
            gateway.close()
            self.assertFalse(owned.exists())
            self.assertTrue((neighbor / 'keep').exists())
            self.assertEqual(other_state.read_text(), 'existing')
            self.assertEqual(json.loads(gateway.state_path().read_text()), {'cookies': [], 'origins': []})
            gateway.close()

    def test_failed_initialization_does_not_replace_the_saved_state(self):
        with tempfile.TemporaryDirectory() as temp:
            gateway = NativeChromeGateway(temp, Sanitizer())
            gateway.state_path().parent.mkdir(parents=True)
            gateway.state_path().write_text('previous')
            gateway.context = SimpleNamespace(storage_state=lambda: {'cookies': [], 'origins': []})
            gateway.close()
            self.assertEqual(gateway.state_path().read_text(), 'previous')

    def test_driver_disconnect_failure_still_reaps_the_owned_process(self):
        with tempfile.TemporaryDirectory() as temp:
            gateway = NativeChromeGateway(temp, Sanitizer())
            wait = Mock()
            gateway._process = SimpleNamespace(wait=wait, poll=lambda: 0)
            gateway.playwright = SimpleNamespace(stop=Mock(side_effect=RuntimeError('SYNTHETIC_PRIVATE')))
            with self.assertLogs('scholarly', level='WARNING') as captured:
                gateway.close()
            wait.assert_called_once_with(timeout=15)
            self.assertNotIn('SYNTHETIC_PRIVATE', '\n'.join(captured.output))

    def test_temporary_windows_file_lock_is_retried_after_process_exit(self):
        import shutil
        with tempfile.TemporaryDirectory() as temp:
            gateway = NativeChromeGateway(temp, Sanitizer())
            owned = Path(temp) / 'scholarly-mcp/native-chrome-runs/owned-example'
            owned.mkdir(parents=True); (owned / 'temporary').write_text('temporary')
            gateway._run = owned
            gateway._process = SimpleNamespace(wait=Mock(), poll=lambda: 0)
            remove = shutil.rmtree
            attempts = []
            def transient(path):
                attempts.append(path)
                if len(attempts) == 1:
                    raise PermissionError('SYNTHETIC_LOCK')
                return remove(path)
            with patch('native_browser.shutil.rmtree', side_effect=transient), patch('native_browser.time.sleep'):
                gateway.close()
            self.assertFalse(owned.exists())
            self.assertEqual(len(attempts), 2)

    def test_native_download_ignores_unrelated_and_preexisting_files(self):
        with tempfile.TemporaryDirectory() as temp:
            gateway = NativeChromeGateway(temp, Sanitizer()); gateway._download_dir = Path(temp)
            old, unrelated, selected = str(uuid4()), str(uuid4()), str(uuid4())
            endpoint = 'https://epubs.siam.org/action/downloadCitation'
            gateway._download_started({'guid': old, 'url': endpoint})
            def action():
                gateway._download_started({'guid': unrelated, 'url': 'https://example.org/action/downloadCitation'})
                gateway._download_started({'guid': '../private', 'url': endpoint})
                gateway._download_started({'guid': selected, 'url': endpoint, 'suggestedFilename': 'null.bib'})
                (Path(temp) / selected).write_bytes(b'citation')
                gateway._download_progress({'guid': selected, 'state': 'completed', 'receivedBytes': 8})
            data, name, url = gateway.native_download(SimpleNamespace(wait_for_timeout=Mock()), action,
                                                     {'epubs.siam.org'}, '/action/downloadCitation')
            self.assertEqual((data, name, url), (b'citation', 'null.bib', endpoint))
            self.assertNotIn('../private', gateway._downloads)

    def test_download_navigation_exception_is_accepted_only_with_matching_native_file(self):
        from playwright.sync_api import Error
        with tempfile.TemporaryDirectory() as temp:
            gateway=NativeChromeGateway(temp,Sanitizer());gateway._download_dir=Path(temp)
            selected=str(uuid4());url='https://epubs.siam.org/doi/pdf/10.1137/example?download=1'
            def action():
                gateway._download_started({'guid':selected,'url':url,'suggestedFilename':'file.pdf'})
                (Path(temp)/selected).write_bytes(b'%PDF-test')
                gateway._download_progress({'guid':selected,'state':'completed','receivedBytes':9})
                raise Error('Download is starting')
            result=gateway.native_download(SimpleNamespace(wait_for_timeout=Mock()),action,
                {'epubs.siam.org'},'/doi/pdf/10.1137/example',query='download=1')
            self.assertEqual(result[0],b'%PDF-test')
            with self.assertRaises(Error):
                gateway.native_download(SimpleNamespace(wait_for_timeout=Mock()),
                    lambda: (_ for _ in ()).throw(Error('unrelated navigation failure')),
                    {'epubs.siam.org'},'/doi/pdf/10.1137/example',query='download=1')

    def test_delayed_native_event_after_download_navigation_is_observed(self):
        from playwright.sync_api import Error
        with tempfile.TemporaryDirectory() as temp:
            gateway=NativeChromeGateway(temp,Sanitizer());gateway._download_dir=Path(temp)
            guid=str(uuid4());url='https://epubs.siam.org/doi/pdf/10.1137/delayed'
            def delivered(delay):
                gateway._download_started({'guid':guid,'url':url,'suggestedFilename':'file.pdf'})
                (Path(temp)/guid).write_bytes(b'%PDF-test')
                gateway._download_progress({'guid':guid,'state':'completed','receivedBytes':9})
            page=SimpleNamespace(wait_for_timeout=Mock(side_effect=delivered))
            def navigate():raise Error('Download is starting')
            data,_,_=gateway.native_download(page,navigate,{'epubs.siam.org'},'/doi/pdf/10.1137/delayed',query='')
            self.assertEqual(data,b'%PDF-test')

    def test_source_file_path_predicate_rejects_another_document_and_host(self):
        with tempfile.TemporaryDirectory() as temp:
            gateway=NativeChromeGateway(temp,Sanitizer());gateway._download_dir=Path(temp)
            expected='S1234567890'
            candidates=[('https://pdf.example.org/asset/S0000000000/main.pdf',b'other'),
                        ('https://unrelated.example/asset/'+expected+'/main.pdf',b'external'),
                        ('https://pdf.example.org/asset/'+expected+'/main.pdf',b'selected')]
            def action():
                for url,data in candidates:
                    guid=str(uuid4());gateway._download_started({'guid':guid,'url':url})
                    (Path(temp)/guid).write_bytes(data)
                    gateway._download_progress({'guid':guid,'state':'completed','receivedBytes':len(data)})
            result=gateway.native_download(SimpleNamespace(wait_for_timeout=Mock()),action,{'pdf.example.org'},
                                           lambda path:path.endswith('/'+expected+'/main.pdf'),timeout=1)
            self.assertEqual(result[0],b'selected')


if __name__ == '__main__':
    unittest.main()
