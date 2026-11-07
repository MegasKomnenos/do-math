"""Worker CLI configuration, separate from the operator's instructions and hooks."""
import json
import os
import re
from pathlib import Path
from cli_adapter import Command, build_command
from runtime_support import write_json


CONTEXT_WINDOW = 1_000_000
AUTO_COMPACT_TOKENS = 900_000


def toml(value):
    if isinstance(value, dict):
        return '{' + ', '.join(json.dumps(k) + ' = ' + toml(v) for k, v in value.items()) + '}'
    if isinstance(value, list):
        return '[' + ', '.join(toml(v) for v in value) + ']'
    return json.dumps(value, ensure_ascii=False)


def worker_command(executable, model, effort, session, servers=None, *, resume_id=None):
    base = build_command(executable, model, effort, session)
    # Native session persistence retains tool messages beyond the CLI stream.
    argv = [x for x in base.argv if x not in ('--ephemeral', '--no-session-persistence')]
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
        write_json(config, {'disableAllHooks': True, 'autoMemoryEnabled': False,
                            'claudeMdExcludes': ['**'], 'enabledPlugins': {}})
        mcp = Path(session) / 'worker-mcp.json'
        write_json(mcp, {'mcpServers': servers})
        argv += ['--setting-sources', '', '--settings', str(config), '--disable-slash-commands',
                 '--strict-mcp-config', '--mcp-config', str(mcp), '--no-chrome']
    if resume_id is not None:
        from uuid import UUID
        resume_id = str(UUID(resume_id))
        if base.provider == 'codex':
            argv[-1:] = ['resume', resume_id, '-']
        else:
            argv += ['--resume', resume_id]
    return Command(base.provider, argv, base.cwd)


def worker_environment():
    environment = dict(os.environ)
    for key in ('CODEX_THREAD_ID', 'CODEX_SESSION_ID', 'CLAUDE_CODE_SESSION_ID', 'CLAUDECODE'):
        environment.pop(key, None)
    # Worker context policy is explicit, independent of the operator's shell.
    environment.pop('CLAUDE_CODE_DISABLE_1M_CONTEXT', None)
    environment.pop('CLAUDE_AUTOCOMPACT_PCT_OVERRIDE', None)
    environment['CLAUDE_CODE_AUTO_COMPACT_WINDOW'] = str(AUTO_COMPACT_TOKENS)
    return environment
