"""Validate and start one unused phase with the existing service; never resume it implicitly."""
import argparse
import datetime
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--phase', default='001')
    parser.add_argument('--check-only', action='store_true')
    args = parser.parse_args()
    if not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', args.phase):
        parser.error('phase must be a new service phase ID')
    records = Path(__file__).resolve().parent
    repo = records.parents[2]
    engine = repo / 'services/continuous-development'
    phase = records / 'phases' / args.phase
    codex = shutil.which('codex.exe') if os.name == 'nt' else shutil.which('codex')
    if not codex:
        parser.error('native Codex CLI is not on PATH')
    marker = records / 'runtime' / ('launch-' + args.phase + '.json')
    used = marker.exists() or any(phase.glob('tasks/*/report.json'))
    used = used or (phase / 'manager.json').exists() or (phase / 'manager.pending.json').exists()
    used = used or any(path.name != '.gitkeep' for path in (phase / 'logs').glob('*'))
    if used:
        parser.error('phase has execution records; do not rerun it. Follow README.md recovery procedure.')
    check = [sys.executable, str(engine / 'check.py'), 'phase', str(repo), str(records), args.phase]
    checked = subprocess.run(check, cwd=repo)
    if checked.returncode:
        return checked.returncode
    command = [sys.executable, str(engine / 'run.py'), str(repo), str(records), args.phase,
               '--sandbox', 'danger-full-access', '-c', 'approval_policy="never"']
    if args.check_only:
        print(json.dumps({'state': 'ready_not_started', 'repo': str(repo), 'records': str(records),
                          'codex': codex, 'command': command}, ensure_ascii=False))
        return 0
    marker.parent.mkdir(exist_ok=True)
    receipt = {'phase': args.phase, 'state': 'starting', 'controller_pid': os.getpid(),
               'started_at': datetime.datetime.now(datetime.timezone.utc).isoformat(),
               'command': command, 'codex': codex}
    # Exclusive creation also prevents two concurrent launchers from starting the same phase.
    with marker.open('x', encoding='utf-8') as stream:
        json.dump(receipt, stream, ensure_ascii=False, indent=2)
    log_path = marker.parent / ('runner-' + args.phase + '.log')
    env = os.environ.copy()
    env['PATH'] = str(Path(codex).parent) + os.pathsep + env.get('PATH', '')
    try:
        with log_path.open('xb') as log:
            process = subprocess.Popen(command, cwd=repo, env=env, stdout=log, stderr=subprocess.STDOUT)
            receipt.update(state='running', runner_pid=process.pid, log=str(log_path))
            marker.write_text(json.dumps(receipt, ensure_ascii=False, indent=2), encoding='utf-8')
            print(f'Runner PID {process.pid}; phase logs: {phase / "logs"}', flush=True)
            code = process.wait()
        receipt.update(state='exited', exit_code=code,
                       finished_at=datetime.datetime.now(datetime.timezone.utc).isoformat())
    except KeyboardInterrupt:
        receipt.update(state='observation_interrupted', note='Inspect actual runner and child processes; no completion inferred.')
        marker.write_text(json.dumps(receipt, ensure_ascii=False, indent=2), encoding='utf-8')
        return 130
    except OSError as error:
        receipt.update(state='launch_or_observation_error', error=str(error))
        marker.write_text(json.dumps(receipt, ensure_ascii=False, indent=2), encoding='utf-8')
        raise
    marker.write_text(json.dumps(receipt, ensure_ascii=False, indent=2), encoding='utf-8')
    return code


if __name__ == '__main__':
    raise SystemExit(main())
