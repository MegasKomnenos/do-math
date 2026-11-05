"""Preserve available native transcripts and identify typed CLI refusals."""
import json
import os
from pathlib import Path
import re
import shutil
import time
from cli_adapter import detect_usage_limit
from runtime_support import write_json


def readable(value):
    """Expose complete readable content; opaque encrypted transport stays in the raw log."""
    if isinstance(value, str):
        return value
    if isinstance(value, list):
        return '\n\n'.join(readable(x) for x in value)
    if isinstance(value, dict):
        if value.get('type') in ('text', 'input_text', 'output_text') and isinstance(value.get('text'), str):
            return value['text']
        return '\n'.join(str(k) + ':\n' + readable(v) for k, v in value.items()
                         if k not in ('encrypted_content', 'signature', 'internal_chat_message_metadata_passthrough'))
    return json.dumps(value, ensure_ascii=False)


def conversation(source, destination, native):
    """Retain all canonical messages and tool contents without truncating their middles."""
    written = 0
    with Path(source).open(encoding='utf-8', errors='replace') as inp, Path(destination).open('w', encoding='utf-8', newline='\n') as out:
        out.write('# Retained conversation\n\nFull readable message and tool content follows. Raw transport remains in ' + Path(source).name + '.\n\n')
        for number, line in enumerate(inp, 1):
            try:
                event = json.loads(line)
            except ValueError:
                continue
            if not isinstance(event, dict):
                continue
            kind = event.get('type')
            payload = None
            if native and kind == 'response_item':
                item = event.get('payload', {})
                if not isinstance(item, dict):
                    continue
                if item.get('type') == 'reasoning':
                    if item.get('summary'):
                        payload = item['summary']
                else:
                    payload = item
            elif native and kind == 'compacted':
                payload = event.get('payload')
            elif native and kind in ('assistant', 'user'):
                payload = event.get('message', event)
            elif not native and kind in ('item.completed', 'assistant', 'user', 'error', 'turn.failed'):
                payload = event.get('item', event.get('message', event))
            if payload is None:
                continue
            body = readable(payload)
            fence = '`' * max(3, 1 + max((len(x) for x in re.findall(r'`+', body)), default=0))
            out.write(f'## {Path(source).name}:{number} — {kind}\n\n{fence}text\n{body}\n{fence}\n\n')
            written += 1
    return written


def events(path):
    if not Path(path).exists():
        return
    with Path(path).open(encoding='utf-8', errors='replace') as stream:
        for line in stream:
            try:
                item = json.loads(line)
            except ValueError:
                continue
            if isinstance(item, dict):
                yield item


def capture(session, provider):
    session = Path(session)
    ids = set()
    activity = False
    for event in events(session / 'cli.stdout.jsonl'):
        if provider == 'codex' and event.get('type') == 'thread.started':
            if isinstance(event.get('thread_id'), str):
                ids.add(event['thread_id'])
        if provider == 'claude' and isinstance(event.get('session_id'), str):
            ids.add(event['session_id'])
        if event.get('type') in ('item.completed', 'item.started') and isinstance(event.get('item'), dict):
            activity |= event['item'].get('type') not in ('error', None)
        if event.get('type') == 'assistant' and not event.get('is_api_error_message'):
            activity = True
    copied = []
    profile = Path.home()
    for identity in ids:
        if not identity or any(c not in '0123456789abcdefABCDEF-' for c in identity):
            continue
        if provider == 'codex':
            root = Path(os.environ.get('CODEX_HOME', str(profile / '.codex'))) / 'sessions'
            paths = root.glob('**/*' + identity + '*.jsonl')
        else:
            root = Path(os.environ.get('CLAUDE_CONFIG_DIR', str(profile / '.claude'))) / 'projects'
            paths = root.glob('*/' + identity + '.jsonl')
        for path in paths:
            destination = session / ('transcript-' + identity + '.jsonl')
            shutil.copyfile(path, destination)
            copied.append(destination.name)
            break
    native_activity = False
    for name in copied:
        for event in events(session / name):
            if provider == 'codex' and event.get('type') == 'response_item':
                item = event.get('payload')
                if not isinstance(item, dict):
                    continue
                if item.get('type') == 'message':
                    native_activity |= item.get('role') == 'assistant' and bool(item.get('content'))
                elif item.get('type') == 'reasoning':
                    native_activity |= bool(item.get('summary') or item.get('content'))
                else:
                    native_activity |= item.get('type') not in ('error', None)
            elif provider == 'claude' and event.get('type') == 'assistant' and not event.get('is_api_error_message'):
                native_activity = True
    receipt = {'native_transcripts': copied, 'cli_activity': activity,
               'native_activity': native_activity,
               'streams': ['cli.stdout.jsonl', 'cli.stderr.log'],
               'limitation': None if copied else 'No native transcript was located; retained CLI streams and artifacts are the available source.'}
    source = session / copied[0] if copied else session / 'cli.stdout.jsonl'
    if source.exists():
        receipt['conversation_items'] = conversation(source, session / 'conversation.md', bool(copied))
        receipt['conversation'] = 'conversation.md'
    write_json(session / 'retention.json', receipt)
    return receipt


def refusal(session, provider, model, started, retry_seconds):
    session = Path(session)
    try:
        limit = detect_usage_limit(provider, session / 'cli.stdout.jsonl', session / 'cli.stderr.log',
                                   now=time.time(), fallback_seconds=retry_seconds, session_started_at=started)
    except OSError:
        limit = None
    if limit:
        return {'key': 'provider:' + provider, 'until': limit.retry_at,
                'reason': 'usage_limit', 'source': limit.source}
    for event in events(session / 'cli.stdout.jsonl'):
        if provider == 'claude' and event.get('type') == 'assistant' and event.get('is_api_error_message') is True:
            if event.get('api_error') == 'model_requires_usage_credits':
                return {'key': 'model:' + model, 'until': time.time() + retry_seconds,
                        'reason': 'model_requires_usage_credits', 'source': 'backoff'}
        if provider == 'codex':
            error = event.get('error')
            message = event.get('message') if event.get('type') == 'error' else error.get('message') if event.get('type') == 'turn.failed' and isinstance(error, dict) else None
            if isinstance(message, str) and message.startswith('Selected model is at capacity'):
                return {'key': 'model:' + model, 'until': time.time() + retry_seconds,
                        'reason': 'model_capacity', 'source': 'backoff'}
    return None
