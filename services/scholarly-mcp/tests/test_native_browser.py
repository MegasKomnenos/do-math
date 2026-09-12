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


if __name__ == '__main__':
    unittest.main()
