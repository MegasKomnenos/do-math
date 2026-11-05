"""Worker CLI configuration, separate from the operator's instructions and hooks."""
import json
import os
from pathlib import Path
from cli_adapter import Command, build_command
from runtime_support import write_json


def toml(value):
    if isinstance(value, dict):
        return '{' + ', '.join(json.dumps(k) + ' = ' + toml(v) for k, v in value.items()) + '}'
    if isinstance(value, list):
        return '[' + ', '.join(toml(v) for v in value) + ']'
    return json.dumps(value, ensure_ascii=False)


def worker_command(executable, model, effort, session, servers=None):
    base = build_command(executable, model, effort, session)
    argv = [x for x in base.argv if x not in ('--ephemeral', '--no-session-persistence')]
    servers = servers or {}
    if base.provider == 'codex':
        options = ['--ignore-user-config', '--ignore-rules', '-c', 'project_doc_max_bytes=0', '-c', 'developer_instructions=""',
                   '--enable', 'skip_host_skill_discovery', '-c', 'web_search="live"']
        for name in ('hooks', 'memories', 'plugins', 'apps', 'multi_agent'):
            options += ['--disable', name]
        # The CLI splits dotted override paths literally; quoted path components
        # become part of a server's name. Supply the whole TOML table instead.
        options += ['-c', 'mcp_servers=' + toml(servers)]
        # Codex accepts options before the stdin positional argument.
        argv[-1:-1] = options
    else:
        config = Path(session) / 'worker-settings.json'
        write_json(config, {'disableAllHooks': True, 'autoMemoryEnabled': False,
                            'claudeMdExcludes': ['**'], 'enabledPlugins': {}})
        mcp = Path(session) / 'worker-mcp.json'
        write_json(mcp, {'mcpServers': servers})
        argv += ['--setting-sources', '', '--settings', str(config), '--disable-slash-commands',
                 '--strict-mcp-config', '--mcp-config', str(mcp), '--no-chrome']
    return Command(base.provider, argv, base.cwd)


def worker_environment():
    environment = dict(os.environ)
    for key in ('CODEX_THREAD_ID', 'CODEX_SESSION_ID', 'CLAUDE_CODE_SESSION_ID', 'CLAUDECODE'):
        environment.pop(key, None)
    return environment
