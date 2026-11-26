"""Worker CLI configuration, separate from the operator's instructions and hooks, and the messages sent
into a worker while one of its turns runs."""
import json
import os
import re
import sys
import time
from pathlib import Path
from cli_adapter import Command, build_command
from message_hook import DELIVERED, WAITING
from runtime_support import write_json


CONTEXT_WINDOW = 1_000_000
# The size at which the CLI compacts the conversation of a worker that still has a compaction: a Codex
# worker, and a Claude session that is sent no message (worker_environment).
AUTO_COMPACT_TOKENS = 950_000
# The size of a session's context, in tokens, at which its host sends it the message that asks it to decide
# its ending and, where its work is to go on, to hand its task over to a new session (ending.run_turn).
CONTEXT_MESSAGE_TOKENS = 800_000
# Twice the Claude CLI's default cap: a long reasoning response must not end the turn.
MAX_OUTPUT_TOKENS = 128_000
# Milliseconds the Claude CLI waits for an MCP server to start before beginning the turn without it.
# Its default is about 30 seconds; sixteen literature servers starting at once took up to 41 (measured).
MCP_STARTUP_MS = 180_000
# The limit, in milliseconds, after which the Claude CLI in print mode stops background tasks that are
# still running once the main agent's turn has ended; the CLI's message names this variable, and its
# default is ten minutes. In the sessions of two instances the CLI did so when sub-agents were the only
# background work the main agent had left (32 of 35 stops). A main agent that had left a shell command
# of its own running was not stopped, twelve times for up to 45 minutes. 16 of 22 failed reviews ended
# this way: the reviewer ended its turn to wait, and ten minutes later its three sub-reviewers were
# stopped. A sub-agent that finishes while the CLI still runs starts the main agent's next turn (120
# cases), so two hours is meant to give sub-agents that time. Whether the CLI honours a value other
# than 0 has not been observed.
BACKGROUND_WAIT_MS = 7_200_000


def toml(value):
    if isinstance(value, dict):
        return '{' + ', '.join(json.dumps(k) + ' = ' + toml(v) for k, v in value.items()) + '}'
    if isinstance(value, list):
        return '[' + ', '.join(toml(v) for v in value) + ']'
    return json.dumps(value, ensure_ascii=False)


HOOK = Path(__file__).with_name('message_hook.py')
# What the interpreter is given to run in place of HOOK itself. The CLI ends a turn, and reports the turn
# as a success, when a hook of this event exits with code 2, and that is the code the interpreter gives
# when it cannot open the script it is told to run. Given this text, it opens the script itself, and a
# script that is missing or that fails ends it with code 1, which the CLI passes over.
HOOK_STARTER = "import sys;exec(open(sys.argv[1],encoding='utf-8').read())"
_last_sent = 0


def open_messages(session):
    """Make the folders of a session that is to receive messages while one of its turns runs. The runner
    does this at dispatch for a session it launches on Claude. No other session has them, and no other
    session is sent a message."""
    (Path(session) / WAITING / DELIVERED).mkdir(parents=True)


def receives_messages(session):
    return (Path(session) / WAITING).is_dir()


def send_message(session, sender, text):
    """Leave a message for a session that receives messages, from 'runner' or from 'operator'; returns its file.

    The session's hook (message_hook.py) hands it over after the session's next batch of tool calls. The
    file appears whole, so the hook never reads half a message, and its name sorts by the time of sending,
    so messages are handed over in the order in which they were sent."""
    global _last_sent
    # Later than every message this process has sent, also where the clock has not moved between two.
    _last_sent = max(time.time_ns(), _last_sent + 1)
    path = Path(session) / WAITING / f'{_last_sent:020d}-{os.urandom(4).hex()}.json'
    write_json(path, {'from': sender, 'at': time.time(), 'text': text})
    return path


def worker_command(executable, model, effort, session, servers=None, *, resume_id=None, withheld=()):
    """The command of one worker session. `withheld` names tools of the Claude CLI that the session is
    launched without; the research roles are launched with none withheld."""
    base = build_command(executable, model, effort, session)
    argv = list(base.argv)
    servers = servers or {}
    if base.provider == 'codex':
        options = ['--ignore-user-config', '--ignore-rules', '-c', 'project_doc_max_bytes=0', '-c', 'developer_instructions=""',
                   '-c', f'model_context_window={CONTEXT_WINDOW}',
                   '-c', f'model_auto_compact_token_limit={AUTO_COMPACT_TOKENS}',
                   '--enable', 'skip_host_skill_discovery', '-c', 'web_search="live"']
        for name in ('hooks', 'memories', 'plugins', 'apps', 'multi_agent'):
            options += ['--disable', name]
        # The CLI splits dotted override paths literally; quoted path components
        # become part of a server's name. Supply the whole TOML table instead.
        options += ['-c', 'mcp_servers=' + toml(servers)]
        # Codex accepts options before the stdin positional argument.
        argv[-1:-1] = options
    else:
        model_index = argv.index('--model') + 1
        argv[model_index] = re.sub(r'\[(?:1m|200k)\]$', '', argv[model_index], flags=re.IGNORECASE) + '[1m]'
        config = Path(session) / 'worker-settings.json'
        settings = {'autoMemoryEnabled': False, 'claudeMdExcludes': ['**'], 'enabledPlugins': {}}
        if receives_messages(session):
            # The worker's one hook. With hooks on, --setting-sources '' below is what keeps the hooks of the
            # operator's project and account out. -I keeps the folder in which the hook is started off the
            # interpreter's module path, so that no file of the session is loaded in place of a library module.
            settings['hooks'] = {'PostToolBatch': [{'hooks': [{
                'type': 'command', 'command': sys.executable,
                'args': ['-I', '-c', HOOK_STARTER, str(HOOK), str(base.cwd)]}]}]}
        else:
            settings['disableAllHooks'] = True
        write_json(config, settings)
        mcp = Path(session) / 'worker-mcp.json'
        write_json(mcp, {'mcpServers': servers})
        argv += ['--setting-sources', '', '--settings', str(config), '--disable-slash-commands',
                 '--strict-mcp-config', '--mcp-config', str(mcp), '--no-chrome']
        if withheld:
            argv += ['--disallowedTools', ','.join(withheld)]
    if resume_id is not None:
        from uuid import UUID
        resume_id = str(UUID(resume_id))
        if base.provider == 'codex':
            argv[-1:] = ['resume', resume_id, '-']
        else:
            argv += ['--resume', resume_id]
    return Command(base.provider, argv, base.cwd)


def worker_environment(session=None):
    """The environment of a worker's CLI. `session` is the session folder of a worker of the runner; a
    session of the paper command or of the finalize pipeline has none to give."""
    environment = dict(os.environ)
    for key in ('CODEX_THREAD_ID', 'CODEX_SESSION_ID', 'CLAUDE_CODE_SESSION_ID', 'CLAUDECODE'):
        environment.pop(key, None)
    # Worker context policy is explicit, independent of the operator's shell.
    for key in ('CLAUDE_CODE_DISABLE_1M_CONTEXT', 'CLAUDE_AUTOCOMPACT_PCT_OVERRIDE',
                'CLAUDE_CODE_AUTO_COMPACT_WINDOW', 'DISABLE_AUTO_COMPACT', 'DISABLE_COMPACT'):
        environment.pop(key, None)
    if session is not None and receives_messages(session):
        # Its host tells this session when its context is nearly full, and its task then goes on in a new
        # session (ending.CONTEXT_MESSAGE). The CLI therefore does not replace its conversation with a summary.
        environment['DISABLE_AUTO_COMPACT'] = '1'
    else:
        # A session that cannot be sent that message: a compaction is its only way past the limit.
        environment['CLAUDE_CODE_AUTO_COMPACT_WINDOW'] = str(AUTO_COMPACT_TOKENS)
    environment['CLAUDE_CODE_MAX_OUTPUT_TOKENS'] = str(MAX_OUTPUT_TOKENS)
    environment['MCP_TIMEOUT'] = str(MCP_STARTUP_MS)
    environment['CLAUDE_CODE_PRINT_BG_WAIT_CEILING_MS'] = str(BACKGROUND_WAIT_MS)
    return environment
