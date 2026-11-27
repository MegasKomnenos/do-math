"""Preserve available native transcripts and identify typed CLI refusals."""
import json
import os
from pathlib import Path
import re
import shutil
import time
from cli_adapter import claude_answer, codex_error_message, detect_usage_limit
from runtime_support import copy_to_disk, turn_streams, write_json


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


PACK_READ = 'Left out here: what this call read of pack.md, which stands in this folder.'
PACK_WHOLE = 'Left out here: the whole text of pack.md, which stands in this folder.'


def shown(block, pack, pack_reads):
    """One block of a Claude message as the readable conversation shows it.

    A session has its pack from its first prompt (context.assemble), and it reads pack.md with its Read tool
    where its conversation no longer holds that prompt, as after a compaction. What the tool returns of the
    pack stands in the session folder already, so the result of a call that read `pack` shows PACK_READ in
    place of that text. The call, with the range it read, and every other block are shown as they are.
    `pack_reads` collects the IDs of the calls that read `pack`."""
    if not isinstance(block, dict):
        return block
    if block.get('type') == 'tool_use' and block.get('name') == 'Read' and isinstance(block.get('input'), dict):
        path = block['input'].get('file_path')
        if isinstance(path, str) and isinstance(block.get('id'), str) and Path(os.path.abspath(path)) == pack:
            pack_reads.add(block['id'])
    elif (block.get('type') == 'tool_result' and isinstance(block.get('tool_use_id'), str)
          and block['tool_use_id'] in pack_reads):
        return {**block, 'content': PACK_READ}
    return block


def conversation(source, destination, native, *, append=False, label=None, note=None):
    """Retain all canonical messages and tool contents without truncating their middles, except the text of the
    pack.md that stands beside the destination. The first prompt of a session carries that text whole
    (context.assemble): hundreds of thousands of bytes, which a peer or a review that reads this conversation
    from beginning to end finds in pack.md. A message or a tool result that carries the whole pack therefore
    shows PACK_WHOLE in its place. What a Claude session read of the file is left out as `shown` describes.

    A note, when given, follows the heading: where content the source holds only by reference is kept."""
    written = 0
    pack, pack_reads = Path(os.path.abspath(destination)).with_name('pack.md'), set()
    # The pack as a message carries it. Whether a CLI records a prompt with the white space at its end is the
    # CLI's affair, so the pack is looked for without its own.
    whole = pack.read_bytes().decode('utf-8', errors='replace').strip() if pack.is_file() else ''
    # A line of the source can hold half of a surrogate pair as an escape, which UTF-8 does not encode. It is
    # written as that escape (backslashreplace), so that one such character does not keep the rest from being retained.
    with Path(source).open(encoding='utf-8', errors='replace') as inp, Path(destination).open('a' if append else 'w', encoding='utf-8', errors='backslashreplace', newline='\n') as out:
        if not append:
            out.write('# Retained conversation\n\nFull readable message and tool content follows, except the text of '
                      'pack.md, which stands in this folder: it is left out where a message carried the whole of '
                      'it and where the Read tool returned it. Raw transport is in the '
                      'named source files. They stand in this folder until the work of the session has finished '
                      'processing, and from then on inside raw.tar.xz in this folder, under the same paths.\n\n')
            if note:
                out.write(note + '\n\n')
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
                    payload = {key: item[key] for key in ('summary', 'content')
                               if item.get(key)} or None
                else:
                    payload = item
            elif native and kind == 'compacted':
                payload = event.get('payload')
            elif native and kind in ('assistant', 'user'):
                payload = event.get('message', event)
            elif native and kind == 'attachment':
                # What reaches a Claude session while it is at work in a turn is recorded by the CLI as an
                # attachment, and as no message. A notification is one of the type queued_command: the report
                # of a delegated agent that finished meanwhile, and the notice that a command left in the
                # background has ended. A message of the runner or of the operator, which the session's hook
                # hands it (message_hook.py), is one of the type hook_additional_context, with the text in a list.
                item = event.get('attachment')
                if isinstance(item, dict) and item.get('type') == 'queued_command':
                    payload = item.get('prompt')
                elif isinstance(item, dict) and item.get('type') == 'hook_additional_context':
                    payload = item.get('content') or None
            elif not native and kind in ('item.completed', 'assistant', 'user', 'error', 'turn.failed'):
                payload = event.get('item', event.get('message', event))
            if payload is None:
                continue
            if kind in ('assistant', 'user') and isinstance(payload, dict) and 'content' in payload:
                # A Claude message arrives inside the API's account of the call (model, stop reason, token
                # counts). The role and the content are what was said; the rest stays in the raw source.
                payload = {key: payload[key] for key in ('role', 'content') if key in payload}
                if isinstance(payload['content'], list):
                    payload['content'] = [shown(block, pack, pack_reads) for block in payload['content']]
            body = readable(payload)
            if whole:
                body = body.replace(whole, PACK_WHOLE)
            fence = '`' * max(3, 1 + max((len(x) for x in re.findall(r'`+', body)), default=0))
            out.write(f'## {label or Path(source).name}:{number} — {kind}\n\n{fence}text\n{body}\n{fence}\n\n')
            written += 1
        # On the disk when this returns, as the copies that capture makes are: the runner saves, through to the
        # disk, that the session is retained once capture has returned, and nothing captures it again.
        out.flush()
        os.fsync(out.fileno())
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


def conversation_identity(event, provider):
    """The native conversation identity one CLI stream event announces, or None.

    Codex announces its thread once in thread.started; Claude stamps session_id on its events.
    Retention and the session host both read this rule here, so a provider change is one edit."""
    if provider == 'codex':
        return event.get('thread_id') if event.get('type') == 'thread.started' else None
    return event.get('session_id')


def model_refused(event):
    """Whether a Claude CLI stream event says that a refusal of the model ended the turn.

    The model refused a request and the CLI had no other model to give it to, so the turn ended there:
    the result of the turn, the last event of the call, is an error with the stop reason "refusal".
    refusal below and the sessions of the paper and finalize commands (command_sessions.stopped_by_safeguard) both
    read this rule here, so a change of the CLI is one edit."""
    return event.get('type') == 'result' and event.get('is_error') is True and event.get('stop_reason') == 'refusal'


# What a CLI reports of its use when a call ends: the stream event that carries the report, the keys kept
# from that event, and the kinds of tokens that a session's totals count.
USAGE_REPORTS = {
    'claude': ('result', ('total_cost_usd', 'modelUsage'),
               ('inputTokens', 'outputTokens', 'cacheReadInputTokens', 'cacheCreationInputTokens')),
    'codex': ('turn.completed', ('usage',),
              ('input_tokens', 'cached_input_tokens', 'output_tokens', 'reasoning_output_tokens')),
}


def usage(session, provider):
    """Write usage.json, what the session's CLI reported of its use, and return the session's totals.

    A call of the CLI ends with a report, and the file keeps the last report of each turn as the stream
    gave it. Claude reports the cost and, for each model, the token counts of the whole conversation up
    to that point: the turns before it are in them, and so are the agents the session delegated to,
    which the `usage` of the same event leaves out. The totals are therefore those of the last turn
    that has a report, and no sum over the turns. The cost is the CLI's own estimate: do-math holds no
    prices, and a report without a cost, as every report of Codex is, leaves the cost None. The reports
    of Codex are taken as Claude's are; whether the report of a resumed call includes the calls before
    it has not been observed. A turn that its CLI did not end itself, as when its host was ended, has
    no report."""
    session = Path(session)
    kind, kept, counted = USAGE_REPORTS[provider]
    turns = []
    for stream in turn_streams(session):
        report = None
        for event in events(stream):
            if event.get('type') == kind:
                report = {key: event[key] for key in kept if key in event}
        turns.append({'stream': stream.relative_to(session).as_posix(), 'report': report})
    last = next((turn['report'] for turn in reversed(turns) if turn['report'] is not None), {})
    by_model = last.get('modelUsage')
    tables = list(by_model.values()) if isinstance(by_model, dict) else [last.get('usage')]
    tokens = {}
    for table in tables:
        for key in counted:
            if isinstance(table, dict) and type(table.get(key)) is int:
                tokens[key] = tokens.get(key, 0) + table[key]
    cost = last.get('total_cost_usd')
    totals = {'tokens': tokens, 'cost_usd': cost if type(cost) in (int, float) else None, 'turns': len(turns),
              'turns_without_report': sum(turn['report'] is None for turn in turns)}
    write_json(session / 'usage.json', {'provider': provider, 'turns': turns, 'totals': totals})
    return totals


def capture(session, provider):
    session = Path(session)
    ids = set()
    activity = False
    streams = turn_streams(session)
    for event in (event for stream in streams for event in events(stream)):
        identity = conversation_identity(event, provider)
        if isinstance(identity, str):
            ids.add(identity)
        if event.get('type') in ('item.completed', 'item.started') and isinstance(event.get('item'), dict):
            activity |= event['item'].get('type') not in ('error', None)
        if event.get('type') == 'assistant' and not event.get('is_api_error_message'):
            activity = True
    copied, companions = [], []
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
            # Through to the disk (copy_to_disk), this copy and the folder below: the runner saves, through to the
            # disk, that the session is retained once this function has returned (Runner.finish), and nothing
            # captures it again. After a loss of power the copies must not stand there without their content.
            copy_to_disk(path, destination)
            copied.append(destination.name)
            # Claude keeps large tool outputs and subagent conversations in a folder named
            # after the transcript; the transcript's tool result then holds only a preview.
            companion = path.with_suffix('')
            if provider == 'claude' and companion.is_dir():
                shutil.copytree(companion, session / ('transcript-' + identity), dirs_exist_ok=True,
                                copy_function=copy_to_disk)
                companions.append('transcript-' + identity)
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
            # Claude's native transcript stores the internal isApiErrorMessage flag;
            # the CLI stream read above names the same flag is_api_error_message.
            elif provider == 'claude' and event.get('type') == 'assistant' and not event.get('isApiErrorMessage'):
                native_activity = True
    receipt = {'native_transcripts': copied, 'native_companions': companions,
               'cli_activity': activity, 'native_activity': native_activity,
               'streams': [str(path.relative_to(session)).replace('\\', '/')
                           for stream in streams for path in (stream, stream.with_name('cli.stderr.log'))],
               'limitation': None if copied else 'No native transcript was located; retained CLI streams and artifacts are the available source.'}
    sources = [session / name for name in sorted(copied)] if copied else [p for p in streams if p.exists()]
    # A Claude transcript keeps only a preview of a large tool result and names the file in the operator's
    # profile that holds the rest; the readable conversation says where this session keeps its copy.
    note = ("Where a tool result below shows only a preview, the full output is in the file it names, in the "
            "Claude CLI's folder for this conversation. This session keeps a copy of that folder, with those "
            "output files and any subagent conversations, as " + ', '.join(name + '/' for name in companions)
            + '.') if companions else None
    if sources:
        receipt['conversation_items'] = sum(conversation(source, session / 'conversation.md', bool(copied),
                                                        append=i > 0, label=source.relative_to(session).as_posix(),
                                                        note=note)
                                            for i, source in enumerate(sources))
        receipt['conversation'] = 'conversation.md'
    write_json(session / 'retention.json', receipt)
    return receipt


def output_limit(folder, provider):
    """The CLI message when Claude's output-token cap ended the turn whose folder is `folder`, or None.

    The CLI discards the response that reached the cap; the conversation and files remain,
    so the session host can resume the same conversation instead of ending it."""
    if provider != 'claude':
        return None
    message = None
    for event in events(Path(folder) / 'cli.stdout.jsonl'):
        if event.get('api_error') != 'max_output_tokens':
            continue
        if event.get('type') == 'result':
            text = event.get('result')
        else:
            content = (event.get('message') or {}).get('content') or []
            text = ''.join(block.get('text', '') for block in content if isinstance(block, dict))
        if isinstance(text, str) and text.strip():
            message = text.strip()
        elif message is None:
            message = 'max_output_tokens'
    return message


def context_limit(folder, provider):
    """Whether the Claude turn whose folder is `folder` ended because its conversation had reached the limit
    of the context window.

    With automatic compaction off (launch.worker_environment) the CLI shortens nothing: it refuses the
    request that no longer fits, and the result of the turn names that ground. The conversation and the
    files are as they were. No provider and no model refused anything, and `refusal` below gives no signal
    for such a turn."""
    if provider != 'claude':
        return False
    return any(event.get('type') == 'result' and event.get('terminal_reason') == 'blocking_limit'
               for event in events(Path(folder) / 'cli.stdout.jsonl'))


def refusal(folder, provider, model, started, retry_seconds):
    """The refusal of a provider or of a model that the streams of one turn show, or None.

    `folder` is the folder of that turn, which holds its cli.stdout.jsonl and cli.stderr.log: the session
    folder for a first turn and the turn's own folder for a resumed one (ending.turn_directory).

    Claude's notice that a model requires usage credits counts on the condition on which a refusal of the
    provider counts (cli_adapter.detect_usage_limit): no response of a model to the session itself follows it
    in the stream. The CLI writes the notice into the stream where it occurs, also when an agent the session
    delegated to met it under another model, and a response that follows shows that the turn went on under the
    session's model."""
    folder = Path(folder)
    try:
        limit = detect_usage_limit(provider, folder / 'cli.stdout.jsonl', folder / 'cli.stderr.log',
                                   now=time.time(), fallback_seconds=retry_seconds, session_started_at=started)
    except OSError:
        limit = None
    if limit:
        return {'key': 'provider:' + provider, 'until': limit.retry_at,
                'reason': 'usage_limit', 'source': limit.source}
    notice = None
    for event in events(folder / 'cli.stdout.jsonl'):
        if provider == 'claude' and claude_answer(event):
            notice = None
        if provider == 'claude' and event.get('type') == 'assistant' and event.get('is_api_error_message') is True:
            if event.get('api_error') == 'model_requires_usage_credits':
                notice = {'key': 'model:' + model, 'until': time.time() + retry_seconds,
                          'reason': 'model_requires_usage_credits', 'source': 'backoff'}
        if provider == 'claude' and model_refused(event):
            return {'key': 'model:' + model, 'until': time.time() + retry_seconds,
                    'reason': 'model_refusal', 'source': 'backoff'}
        if provider == 'codex':
            message = codex_error_message(event)
            if isinstance(message, str) and message.startswith('Selected model is at capacity'):
                return {'key': 'model:' + model, 'until': time.time() + retry_seconds,
                        'reason': 'model_capacity', 'source': 'backoff'}
    return notice


def model_blocked(blocks, provider, model, now):
    """Whether a block keeps sessions from a model at the time `now`.

    `blocks` is the table of the runner's state. A block stands there under the key of the provider or
    of the model, as the signal of refusal above names it, and lasts until its `until`. The runner
    dispatches no session to a model while either block lasts (Runner.selection), and a session host
    waits as long before it resumes one (ending.wait_to_resume). Both read this rule here, so the two
    processes cannot come to differ."""
    return any(blocks.get(key, {}).get('until', 0) > now for key in ('provider:' + provider, 'model:' + model))
