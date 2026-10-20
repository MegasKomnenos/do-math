"""A real child process used to verify the dispatcher's ordering, not model quality."""

import json
import os
import sys
import time
from pathlib import Path

prompt = sys.stdin.buffer.read().decode("utf-8")
values = dict(line.split(": ", 1) for line in prompt.splitlines() if ": " in line)
records = Path(values["실행 기록 루트"])
repo = Path(values["프로젝트 루트"])
phase = values["phase"]
task = values["task"]
role = values["역할"]
directory = records / "phases" / phase
events = records / "events"
events.mkdir(exist_ok=True)
name = f"{phase}-{task if role == 'task' else 'manager'}"

assert sys.argv[1:] == ["-C", str(repo), "--add-dir", str(records), "-"]
assert Path.cwd() == repo
assert "protocol.md" in prompt
assert Path(values["Python"]).is_file()
(events / f"{name}.prompt").write_text(prompt, encoding="utf-8")
(events / f"{name}.started").touch()

if phase == "002":
    assert (events / "001-manager.finished").exists()

tasks = json.loads((directory / "phase.json").read_text("utf-8"))["tasks"]
if role == "task":
    # If the runner becomes sequential, the first child times out before its peer starts.
    deadline = time.monotonic() + 10
    while not all((events / f"{phase}-{row['id']}.started").exists() for row in tasks):
        assert time.monotonic() < deadline, "tasks were not dispatched in parallel"
        time.sleep(0.01)
    assert not (events / f"{phase}-manager.started").exists()
    sys.stdout.buffer.write(("task output 한글\n" * 10000).encode("utf-8"))
    time.sleep(0.03)
else:
    assert all((events / f"{phase}-{row['id']}.finished").exists() for row in tasks)
    if os.environ.get("PHASE_TEST_NO_MANAGER_RESULT") != "1":
        # Intentionally incomplete manager schema: the runner must only read next.
        (directory / "manager.json").write_text(json.dumps({"next": "002" if phase == "001" else None}), encoding="utf-8")
    sys.stderr.buffer.write(b"manager stderr\n")

(events / f"{name}.finished").touch()
# Both task and manager nonzero returns are deliberately ignored by the runner.
raise SystemExit(7 if role == "task" else 9)
