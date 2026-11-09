"""Configuration for fresh research instances."""
from copy import deepcopy
import math
from pathlib import Path
import shutil
from cli_adapter import build_command, provider_for_model
from runtime_support import LEAN_DEFAULTS, read_json

ROLES = ('attempt', 'explore', 'formalizer', 'peer', 'review', 'organizer')
PRODUCERS = ('attempt', 'explore', 'formalizer')
MODELS = [{'model': 'codex/gpt-6.1-sol', 'effort': 'xhigh'},
          {'model': 'claude/opus', 'effort': 'xhigh'}]
# A record and its review come from a different model than the work they assess.
ASSESSORS = [{'model': 'claude/opus', 'effort': 'xhigh'},
             {'model': 'codex/gpt-6.1-sol', 'effort': 'xhigh'}]
AXIOMS = ['propext', 'Classical.choice', 'Quot.sound']


def defaults():
    return {'schema': 1, 'max_sessions': 8, 'explore_every': 1,
            'organizer_every_records': 4, 'launch_interval': 180, 'models': deepcopy(MODELS),
            'roles': {'peer': deepcopy(ASSESSORS), 'review': deepcopy(ASSESSORS)},
            'cli': {p: shutil.which(p) or p for p in ('codex', 'claude')},
            'retry_seconds': 60, 'retry_max_seconds': 1800, 'mcp_servers': {},
            'max_end_resumptions': 3,
            'lean': {**LEAN_DEFAULTS, 'command': ['lean'],
                     'version_command': ['lean', '--version'], 'cwd': None,
                     'env': {}, 'cache_epoch': 'initial', 'allowed_axioms': list(AXIOMS)}}


def validate(raw):
    if not isinstance(raw, dict) or raw.get('schema', 1) != 1:
        raise ValueError('settings must be a fresh-runtime schema 1 object')
    for section in ('cli', 'lean'):
        if not isinstance(raw.get(section, {}), dict):
            raise ValueError(section + ' must be an object')
    value = defaults()
    value.update(raw)
    value['cli'] = {**defaults()['cli'], **raw.get('cli', {})}
    value['lean'] = {**defaults()['lean'], **raw.get('lean', {})}
    known = defaults()
    unknown = [key for key in raw if key not in known]
    for section in ('cli', 'lean'):
        nested = raw.get(section, {})
        if isinstance(nested, dict):
            unknown += [section + '.' + key for key in nested if key not in known[section]]
    if unknown:
        # A misspelled or earlier-runtime key would otherwise leave its default silently in force.
        raise ValueError('unknown setting: ' + ', '.join(unknown))
    for key in ('max_sessions', 'explore_every', 'organizer_every_records',
                'retry_seconds', 'retry_max_seconds'):
        if type(value[key]) is not int or value[key] < 1:
            raise ValueError(f'{key} must be a positive integer')
    if type(value['launch_interval']) is not int or value['launch_interval'] < 0:
        raise ValueError('launch_interval must be a nonnegative integer number of seconds')
    if type(value['max_end_resumptions']) is not int or value['max_end_resumptions'] < 0:
        raise ValueError('max_end_resumptions must be a nonnegative integer')
    if value['retry_max_seconds'] < value['retry_seconds']:
        raise ValueError('retry_max_seconds must be at least retry_seconds')
    if not isinstance(value['roles'], dict) or set(value['roles']) - set(ROLES):
        raise ValueError('roles contains an unknown role')
    if not isinstance(value['mcp_servers'], dict) or not all(isinstance(k, str) and isinstance(v, dict) for k, v in value['mcp_servers'].items()):
        raise ValueError('mcp_servers must map explicit server names to configurations')
    for role in ROLES:
        pool = value['roles'].get(role, value['models'])
        if not isinstance(pool, list) or not pool:
            raise ValueError(f'{role} needs an ordered nonempty model list')
        for choice in pool:
            if not isinstance(choice, dict) or set(choice) != {'model', 'effort'}:
                raise ValueError(f'{role} model entries need exactly "model" and "effort"; got: {choice!r}')
            provider = provider_for_model(choice['model'])
            if not isinstance(value['cli'][provider], str):
                raise ValueError(f'cli.{provider} must be an executable path or name')
            build_command(value['cli'][provider], choice['model'], choice['effort'], Path.cwd())
    lean = value['lean']
    if not isinstance(lean['cache_epoch'], str) or not lean['cache_epoch'].strip():
        raise ValueError('lean.cache_epoch must be nonempty text')
    for key in ('command', 'version_command'):
        if not isinstance(lean[key], list) or not lean[key] or not all(isinstance(x, str) and x.strip() for x in lean[key]):
            raise ValueError(f'lean.{key} must be a nonempty command array')
    if lean['cwd'] is not None and not (isinstance(lean['cwd'], str) and Path(lean['cwd']).is_absolute()):
        raise ValueError('lean.cwd must be absolute or null')
    if not isinstance(lean['env'], dict) or not all(isinstance(k, str) and isinstance(v, str) for k, v in lean['env'].items()):
        raise ValueError('lean.env must map strings to strings')
    for key in ('memory_budget_mb', 'cpu_threads_budget', 'threads', 'calibration_expect_mb'):
        if lean[key] is None and key in ('memory_budget_mb', 'cpu_threads_budget'):
            continue
        if type(lean[key]) is not int or lean[key] < 1:
            raise ValueError(f'lean.{key} must be positive')
    for key in ('min_free_memory_mb', 'max_passes'):
        if type(lean[key]) is not int or lean[key] < 0:
            raise ValueError(f'lean.{key} must be a nonnegative integer')
    for key in ('confidence', 'default_spread'):
        if type(lean[key]) not in (int, float) or not math.isfinite(lean[key]) or lean[key] < 0:
            raise ValueError(f'lean.{key} must be nonnegative and finite')
    if lean['priority'] not in ('normal', 'below_normal', 'idle'):
        raise ValueError('unknown Lean priority')
    if not isinstance(lean['allowed_axioms'], list) or not all(isinstance(x, str) and x for x in lean['allowed_axioms']):
        raise ValueError('allowed_axioms must be a string list')
    if 'sorryAx' in lean['allowed_axioms']:
        raise ValueError('sorryAx cannot be allowed')
    return value


def load_settings(instance):
    return validate(read_json(Path(instance) / 'settings.json'))
