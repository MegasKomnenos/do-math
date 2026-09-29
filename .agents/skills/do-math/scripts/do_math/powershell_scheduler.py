"""The real scheduler port: the PowerShell task adapter ``operator_schedule.ps1`` (boundary adapter)."""
from __future__ import annotations

import json
from pathlib import Path
import shutil
import subprocess
from typing import Callable

Runner = Callable[..., subprocess.CompletedProcess[str]]
# The adapter finds operator_bootstrap.py beside itself. Its ValidateSet is the one
# action list: an unsupported action fails there and ``scheduled_operator.schedule`` raises its error.
SCHEDULE_SCRIPT = Path(__file__).resolve().parents[1] / "operator_schedule.ps1"


class PowerShellScheduler:
    """Real scheduler port: the PowerShell adapter ``operator_schedule.ps1``."""

    def __init__(self, runner: Runner = subprocess.run):
        self.runner = runner

    def run(self, action: str, arguments: dict) -> dict:
        powershell = shutil.which("powershell.exe") or shutil.which("powershell") or "powershell.exe"
        command = [powershell, "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", str(SCHEDULE_SCRIPT),
                   "-Action", action]
        for name, value in arguments.items():
            command.extend(["-" + name, value])
        completed = self.runner(command, capture_output=True, text=True, encoding="utf-8", check=False,
                                creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
        if completed.returncode:
            raise RuntimeError(completed.stderr.strip() or completed.stdout.strip() or "scheduled-task operation failed")
        try:
            value = json.loads(completed.stdout)
        except json.JSONDecodeError as error:
            raise RuntimeError("scheduled-task adapter returned invalid JSON") from error
        if not isinstance(value, dict):
            raise RuntimeError("scheduled-task adapter result must be an object")
        return value
