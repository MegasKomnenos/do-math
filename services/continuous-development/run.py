"""Dispatch every task, wait, dispatch the manager, and follow its next phase."""

import json
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path


def selected_command(command, selection):
    args = list(command)
    if "model" in selection:
        args, i = [], 0
        while i < len(command):
            token = command[i]
            if token in ("-m", "--model"):
                i += 2
                continue
            if token.startswith("--model=") or (token.startswith("-m") and not token.startswith("--")):
                i += 1
                continue
            args.append(token)
            i += 1
        args.extend(["--model", selection["model"]])
    if "effort" in selection:
        args.extend(["-c", "model_reasoning_effort=" + json.dumps(selection["effort"])])
    return args


def run(repo, records, phase, command=("codex", "exec")):
    repo, records = Path(repo).resolve(), Path(records).resolve()
    engine = Path(__file__).resolve().parent
    settings_path = records / "settings.json"
    settings = json.loads(settings_path.read_text("utf-8-sig")) if settings_path.exists() else {}
    manager_selection = settings.get("manager", {})

    def dispatch(phase_dir, task=None):
        role = "manager" if task is None else "task"
        task_id = "-" if task is None else task["id"]
        name = "manager" if task is None else f"task-{task_id}"
        selection = manager_selection if task is None else task
        prompt = (
            f"역할: {role}\n프로젝트 루트: {repo}\n실행 기록 루트: {records}\n"
            f"phase: {phase_dir.name}\ntask: {task_id}\n"
            f"Python: {sys.executable}\n"
            f"{engine / 'protocol.md'}를 읽고 지정된 역할의 절차를 수행한다.\n"
        )
        with (phase_dir / "logs" / f"{name}.log").open("wb") as log:
            subprocess.run(
                [*selected_command(command, selection), "-C", str(repo), "--add-dir", str(records), "-"],
                input=prompt.encode("utf-8"),
                stdout=log,
                stderr=subprocess.STDOUT,
                cwd=repo,
            )

    while phase is not None:
        phase_dir = records / "phases" / phase
        tasks = json.loads((phase_dir / "phase.json").read_text("utf-8-sig"))["tasks"]
        with ThreadPoolExecutor(max_workers=len(tasks)) as pool:
            list(pool.map(lambda task: dispatch(phase_dir, task), tasks))
        dispatch(phase_dir)
        phase = json.loads((phase_dir / "manager.json").read_text("utf-8-sig"))["next"]


if __name__ == "__main__":
    run(*sys.argv[1:4], command=("codex", "exec", *sys.argv[4:]))
