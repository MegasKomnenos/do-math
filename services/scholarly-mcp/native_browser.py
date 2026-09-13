"""Owned Chrome windows for publisher routes verified through native Chrome/CDP."""
from __future__ import annotations

import json
import logging
import os
from pathlib import Path
import shutil
import socket
import subprocess
import tempfile
import time
from urllib.parse import urlsplit
from uuid import UUID

from browser_adapters import KudosGateway, require_source_url
from scholarly import ServiceError


def owns_loopback_port(port, pid):
    """Check the Windows TCP listener before attaching to a debugging endpoint."""
    import ctypes
    from ctypes import wintypes
    class Row(ctypes.Structure):
        _fields_ = [(name, wintypes.DWORD) for name in ('state', 'local_address', 'local_port',
                                                     'remote_address', 'remote_port', 'pid')]
    get_table = ctypes.windll.iphlpapi.GetExtendedTcpTable
    size = wintypes.DWORD()
    get_table(None, ctypes.byref(size), False, socket.AF_INET, 3, 0)
    if size.value < 4:
        return False
    table = ctypes.create_string_buffer(size.value)
    if get_table(table, ctypes.byref(size), False, socket.AF_INET, 3, 0):
        return False
    count = wintypes.DWORD.from_buffer(table).value
    for index in range(count):
        row = Row.from_buffer(table, 4 + index * ctypes.sizeof(Row))
        address = socket.inet_ntoa(int(row.local_address).to_bytes(4, 'little'))
        if address == '127.0.0.1' and socket.ntohs(row.local_port & 0xffff) == port and row.pid == pid:
            return True
    return False


class NativeChromeGateway(KudosGateway):
    """One server-owned profile and process; never attach to a user's browser."""

    def __init__(self, credential_root, sanitizer):
        super().__init__(credential_root, sanitizer, engine='chromium')
        self._process = self._process_log = self._run = self._cdp = None
        self._downloads = {}
        self._ready = False

    def state_path(self):
        return self.root / 'scholarly-mcp' / 'kudos-native-chromium.json'

    def start(self):
        if self.context is not None:
            return
        candidates = [Path(os.environ.get('PROGRAMFILES', 'C:/Program Files')) / 'Google/Chrome/Application/chrome.exe',
                      Path(os.environ.get('LOCALAPPDATA', '')) / 'Google/Chrome/Application/chrome.exe']
        executable = next((candidate for candidate in candidates if candidate.is_absolute() and candidate.is_file()), None)
        if executable is None:
            raise ServiceError('browser_unavailable', 'This verified browser route requires installed Google Chrome', status='restricted')
        parent = self.root / 'scholarly-mcp' / 'native-chrome-runs'
        parent.mkdir(parents=True, exist_ok=True)
        self._run = Path(tempfile.mkdtemp(prefix='owned-', dir=parent)).resolve()
        preferences = self._run / 'profile' / 'Default' / 'Preferences'
        preferences.parent.mkdir(parents=True)
        preferences.write_text(json.dumps({'plugins': {'always_open_pdf_externally': True}}), encoding='utf-8')
        self._download_dir = self._run / 'downloads'
        self._download_dir.mkdir()
        with socket.socket() as reservation:
            reservation.bind(('127.0.0.1', 0))
            port = reservation.getsockname()[1]
        self._process_log = (self._run / 'chrome.log').open('wb')
        try:
            self._process = subprocess.Popen([
                str(executable), '--remote-debugging-address=127.0.0.1', f'--remote-debugging-port={port}',
                '--user-data-dir=' + str(self._run / 'profile'), '--no-first-run', '--no-default-browser-check',
                '--disable-backgrounding-occluded-windows', '--window-size=1280,900', 'about:blank',
            ], stdin=subprocess.DEVNULL, stdout=self._process_log, stderr=self._process_log, cwd=self.root.parent)
            from playwright.sync_api import sync_playwright
            self.playwright = sync_playwright().start()
            deadline = time.monotonic() + 20
            while time.monotonic() < deadline:
                if self._process.poll() is not None:
                    break
                if not owns_loopback_port(port, self._process.pid):
                    time.sleep(0.25)
                    continue
                try:
                    self.browser = self.playwright.chromium.connect_over_cdp(
                        f'http://127.0.0.1:{port}', timeout=1000, no_defaults=True)
                    break
                except Exception:
                    time.sleep(0.25)
            if self.browser is None:
                raise ServiceError('browser_start_failed', 'The owned Chrome window did not become ready')
            self.context = self.browser.contexts[0]
            self.context.set_default_timeout(25000)
            self._cdp = self.browser.new_browser_cdp_session()
            self._cdp.send('Browser.setDownloadBehavior', {
                'behavior': 'allowAndName', 'downloadPath': str(self._download_dir), 'eventsEnabled': True,
            })
            self._cdp.on('Browser.downloadWillBegin', self._download_started)
            self._cdp.on('Browser.downloadProgress', self._download_progress)
            state = self.state_path()
            if state.exists():
                saved = json.loads(state.read_text(encoding='utf-8'))
                self.context.add_cookies(saved.get('cookies', []))
                origins = {entry['origin']: entry.get('localStorage', []) for entry in saved.get('origins', [])}
                if origins:
                    self.context.add_init_script('(() => { const origins = ' + json.dumps(origins) +
                        '; for (const entry of origins[location.origin] || []) localStorage.setItem(entry.name, entry.value); })();')
            self._ready = True
        except Exception as error:
            self.close()
            if isinstance(error, ServiceError):
                raise
            raise ServiceError('browser_start_failed', 'The owned Chrome window could not be initialized',
                               error_type=type(error).__name__) from None

    def _download_started(self, event):
        try:
            guid = str(UUID(event['guid']))
        except (KeyError, ValueError, TypeError, AttributeError):
            return
        if guid == event['guid']:
            self._downloads[guid] = {**event, 'state': 'inProgress'}

    def _download_progress(self, event):
        if event['guid'] in self._downloads:
            self._downloads[event['guid']].update(event)

    def native_download(self, page, action, hosts, path, *, timeout=45000, query=None):
        """Read a completed, source-bound download started by the supplied UI action."""
        before = set(self._downloads)
        def matching():
            return [(guid,item) for guid,item in self._downloads.items() if guid not in before
                    and urlsplit(item['url']).hostname in hosts
                    and (path(urlsplit(item['url']).path) if callable(path) else urlsplit(item['url']).path==path)
                    and (query is None or urlsplit(item['url']).query==query)]
        from playwright.sync_api import Error as BrowserError
        try:
            action()
        except BrowserError:
            for _ in range(10):
                if matching():
                    break
                try:
                    page.wait_for_timeout(100)
                except BrowserError:
                    break
            if not matching():
                raise
        deadline = time.monotonic() + timeout / 1000
        while time.monotonic() < deadline:
            matches = matching()
            if len(matches) > 1:
                raise ServiceError('ambiguous_download', 'The native action produced multiple matching files')
            if matches:
                guid, item = matches[0]
                require_source_url(item['url'], hosts)
                if item['state'] == 'canceled':
                    raise ServiceError('download_cancelled', 'The publisher download was cancelled')
                file = self._download_dir / guid
                if item['state'] == 'completed' and file.is_file():
                    data = file.read_bytes()
                    if len(data) != item.get('receivedBytes', len(data)):
                        raise ServiceError('download_incomplete', 'Native download size does not match its completion event')
                    return data, item.get('suggestedFilename', ''), item['url']
            page.wait_for_timeout(100)
        raise ServiceError('download_missing', 'The native action did not produce a completed requested file', retryable=True)

    def close(self):
        process = self._process
        if self.context is not None and self._ready:
            try:
                self.save_state()
            except Exception as error:
                logging.getLogger('scholarly').warning('native browser state was not saved: %s', type(error).__name__)
        if self.browser is not None:
            try:
                self.browser.new_browser_cdp_session().send('Browser.close')
            except Exception:
                pass
        if self.playwright is not None:
            try:
                self.playwright.stop()
            except Exception as error:
                logging.getLogger('scholarly').warning('native browser driver did not disconnect cleanly: %s', type(error).__name__)
        if process is not None:
            try:
                process.wait(timeout=15)
            except subprocess.TimeoutExpired:
                process.terminate()
                try:
                    process.wait(timeout=10)
                except subprocess.TimeoutExpired:
                    process.kill()
                    process.wait(timeout=10)
        if self._process_log is not None:
            self._process_log.close()
        if self._run is not None and (process is None or process.poll() is not None):
            parent = (self.root / 'scholarly-mcp' / 'native-chrome-runs').resolve()
            target = self._run.resolve()
            if target.parent == parent and target.name.startswith('owned-'):
                for attempt in range(5):
                    if not target.exists():
                        break
                    if target.resolve().parent != parent:
                        break
                    try:
                        shutil.rmtree(target)
                        break
                    except OSError as error:
                        if attempt == 4:
                            logging.getLogger('scholarly').warning('native browser temporary profile remains: %s', type(error).__name__)
                        else:
                            time.sleep(0.25 * (attempt + 1))
        self.context = self.browser = self.playwright = None
        self._process = self._process_log = self._run = self._cdp = None
        self._ready = False
        self.pages.clear()
        self._downloads.clear()
