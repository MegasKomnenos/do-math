"""Reproduce elevated Windows sandbox read-root isolation without a model call."""
from __future__ import annotations

import argparse
from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
import json
import os
import platform
from pathlib import Path
import shutil
import subprocess
import sys
import time
import uuid

from do_math.codex_worker import sanitized_environment
from do_math.windows_job import WindowsJob


STEP_TIMEOUT = 50.0
POWERSHELL = Path(r"C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe")
CANARY_A = "NATIVE_ISOLATION_A_7f983a"
CANARY_B = "NATIVE_ISOLATION_B_2c41de"


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def dump(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x", encoding="utf-8", newline="\n") as stream:
        json.dump(value, stream, ensure_ascii=False, indent=2)
        stream.write("\n")


def run_host(argv: list[str], timeout: float = 20) -> dict[str, object]:
    result = subprocess.run(argv, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE, check=False, timeout=timeout)
    return {"argv": argv, "returncode": result.returncode,
            "stdout": result.stdout.decode("utf-8", errors="replace"),
            "stderr": result.stderr.decode("utf-8", errors="replace")}


def reset_private_acl(paths: tuple[Path, ...]) -> list[dict[str, object]]:
    owner = subprocess.check_output(["whoami"], text=True).strip()
    machine = os.environ["COMPUTERNAME"]
    sandbox_principals = [f"{machine}\\{name}" for name in
                          ("CodexSandboxUsers", "CodexSandboxOffline", "CodexSandboxOnline")]
    records: list[dict[str, object]] = []
    for path in paths:
        commands = [
            ["icacls", str(path), "/inheritance:r"],
            ["icacls", str(path), "/remove:g", "*S-1-5-32-545", "*S-1-5-11",
             *sandbox_principals, "/T", "/C"],
            ["icacls", str(path), "/remove:d", "*S-1-5-32-545", "*S-1-5-11",
             *sandbox_principals, "/T", "/C"],
            ["icacls", str(path), "/grant:r", "*S-1-5-18:(OI)(CI)F",
             "*S-1-5-32-544:(OI)(CI)F", f"{owner}:(OI)(CI)F"],
            ["icacls", str(path / "*"), "/reset", "/T", "/C"],
        ]
        for argv in commands:
            record = run_host(argv)
            records.append(record)
            if record["returncode"] != 0:
                raise RuntimeError(f"ACL setup failed for {path}: {argv}")
    return records


def acl_snapshot(paths: tuple[Path, ...]) -> dict[str, object]:
    return {path.name + "@" + path.parent.name: run_host(["icacls", str(path)]) for path in paths}


def one_shot_source(own: Path, other: Path, own_value: str, label: str) -> str:
    return f"""$ErrorActionPreference='Stop'
$results=[ordered]@{{}}
$attempts=[ordered]@{{own={{(Get-Content -Raw -LiteralPath '{own.as_posix()}/canary.txt').Trim()}};other={{(Get-Content -Raw -LiteralPath '{other.as_posix()}/canary.txt').Trim()}}}}
foreach($entry in $attempts.GetEnumerator()){{try{{$results[$entry.Key]=[ordered]@{{state='read';content=(& $entry.Value);error_type=$null;message=$null}}}}catch{{$type=$_.Exception.GetType().FullName;if($_.Exception -is [System.UnauthorizedAccessException]){{$state='access_denied'}}elseif($_.Exception -is [System.IO.FileNotFoundException] -or $_.Exception -is [System.IO.DirectoryNotFoundException]){{$state='file_missing'}}else{{$state='program_failed'}};$results[$entry.Key]=[ordered]@{{state=$state;content=$null;error_type=$type;message=$_.Exception.Message}}}}}}
[ordered]@{{label='{label}';observed_at=[DateTimeOffset]::UtcNow.ToString('o');results=$results}}|ConvertTo-Json -Depth 6 -Compress
if($results.own.state-ne'read'-or$results.own.content-ne'{own_value}'-or$results.other.state-ne'access_denied'){{exit 7}}
"""


def concurrent_source(own: Path, other: Path, workspace: Path, duration: int) -> str:
    return f"""$ErrorActionPreference='Stop'
$own='{own.as_posix()}/canary.txt';$other='{other.as_posix()}/canary.txt';$ready='{workspace.as_posix()}/ready.txt';$samples='{workspace.as_posix()}/samples.jsonl'
$deadline=[DateTimeOffset]::UtcNow.AddSeconds({duration});$index=0;$ownFailed=0;$ownDenied=0;$otherReads=0
while([DateTimeOffset]::UtcNow-lt$deadline){{try{{$ownContent=(Get-Content -Raw -LiteralPath $own).Trim();$ownState='read'}}catch{{$ownContent=$null;$ownState=if($_.Exception-is[System.UnauthorizedAccessException]){{'access_denied'}}elseif($_.Exception-is[System.IO.FileNotFoundException]-or$_.Exception-is[System.IO.DirectoryNotFoundException]){{'file_missing'}}else{{'program_failed'}}}};try{{$otherContent=(Get-Content -Raw -LiteralPath $other).Trim();$otherState='read'}}catch{{$otherContent=$null;$otherState=if($_.Exception-is[System.UnauthorizedAccessException]){{'access_denied'}}elseif($_.Exception-is[System.IO.FileNotFoundException]-or$_.Exception-is[System.IO.DirectoryNotFoundException]){{'file_missing'}}else{{'program_failed'}}}};if($ownState-ne'read'-or$ownContent-ne'{CANARY_A}'){{$ownFailed++}};if($ownState-eq'access_denied'){{$ownDenied++}};if($otherState-eq'read'){{$otherReads++}};[ordered]@{{index=$index;observed_at=[DateTimeOffset]::UtcNow.ToString('o');own_state=$ownState;own_content=$ownContent;other_state=$otherState;other_content=$otherContent}}|ConvertTo-Json -Compress|Add-Content -LiteralPath $samples -Encoding UTF8;if($index-eq0){{Set-Content -LiteralPath $ready -Value ready -Encoding ASCII}};$index++;Start-Sleep -Milliseconds 100}}
[ordered]@{{label='concurrent-a';sample_count=$index;own_failed=$ownFailed;own_denied=$ownDenied;other_reads=$otherReads}}|ConvertTo-Json -Compress
if($ownFailed-ne0-or$otherReads-ne0){{exit 8}}
"""


RUNNER_SOURCE = r'''import json, pathlib, subprocess, sys
request=json.loads(pathlib.Path(sys.argv[1]).read_text(encoding="utf-8"))
try:
    with open(request["stdout"],"xb") as out, open(request["stderr"],"xb") as err:
        process=subprocess.Popen(request["argv"],stdin=subprocess.DEVNULL,stdout=out,stderr=err,shell=False)
        code=process.wait()
    status={"state":"exited","exit_code":code}
except BaseException as exc:
    status={"state":"program_failed","error_type":type(exc).__name__,"message":str(exc)}
pathlib.Path(request["status"]).write_text(json.dumps(status),encoding="utf-8")
raise SystemExit(0 if status.get("state")=="exited" else 125)
'''


@dataclass
class OwnedRun:
    label: str
    directory: Path
    job: WindowsJob
    started_at: str
    deadline: float
    request: dict[str, object]


def profile_argv(codex: Path, profile: str, workspace: Path, read_root: Path,
                 deny_root: Path | None, script: Path) -> list[str]:
    entries = {'":minimal"': '"read"', '":workspace_roots"': '"write"',
               f'"{read_root.resolve().as_posix()}"': '"read"'}
    if deny_root is not None:
        entries[f'"{deny_root.resolve().as_posix()}"'] = '"deny"'
    filesystem = "{" + ",".join(key + "=" + value for key, value in entries.items()) + "}"
    return [str(codex), "sandbox", "-C", str(workspace), "-P", profile,
            "-c", 'windows.sandbox="elevated"', "-c", f"permissions.{profile}.filesystem={filesystem}",
            "-c", f"permissions.{profile}.network.enabled=false", "--", str(POWERSHELL),
            "-NoProfile", "-NonInteractive", "-File", str(script)]


def start_owned(root: Path, runner: Path, label: str, argv: list[str]) -> OwnedRun:
    directory = root / "runs" / label
    directory.mkdir(parents=True)
    request = {"label": label, "argv": argv, "started_at": utc_now(), "timeout_seconds": STEP_TIMEOUT,
               "stdout": str(directory / "stdout.txt"), "stderr": str(directory / "stderr.txt"),
               "status": str(directory / "runner-status.json")}
    request_path = directory / "request.json"
    dump(request_path, request)
    job = WindowsJob([sys.executable, str(runner), str(request_path)], cwd=root,
                     env=sanitized_environment(os.environ))
    receipt = {"pid": job.pid, "creation_filetime": job.creation_filetime}
    dump(directory / "process.json", receipt)
    job.resume()
    return OwnedRun(label, directory, job, request["started_at"], time.monotonic() + STEP_TIMEOUT, request)


def finish_owned(execution: OwnedRun) -> dict[str, object]:
    timed_out = False
    terminated = False
    try:
        while True:
            state = execution.job.inspect()
            if state.root_signaled and state.active_processes == 0 and state.process_ids == ():
                break
            if time.monotonic() >= execution.deadline:
                timed_out = True
                execution.job.terminate()
                terminated = True
                barrier_deadline = time.monotonic() + 10
                while time.monotonic() < barrier_deadline:
                    state = execution.job.inspect()
                    if state.root_signaled and state.active_processes == 0 and state.process_ids == ():
                        break
                    time.sleep(.02)
                break
            time.sleep(.02)
        final_state = execution.job.inspect()
    finally:
        execution.job.close()
    status_path = Path(str(execution.request["status"]))
    status = json.loads(status_path.read_text(encoding="utf-8")) if status_path.exists() else None
    result = {"label": execution.label, "started_at": execution.started_at, "finished_at": utc_now(),
              "timed_out": timed_out, "terminate_job_called": terminated, "runner_status": status,
              "barrier": {"root_signaled": final_state.root_signaled,
                          "active_processes": final_state.active_processes,
                          "process_ids": list(final_state.process_ids),
                          "confirmed": final_state.root_signaled and final_state.active_processes == 0 and final_state.process_ids == ()},
              "request": str(execution.directory / "request.json"),
              "stdout": str(execution.directory / "stdout.txt"), "stderr": str(execution.directory / "stderr.txt")}
    dump(execution.directory / "result.json", result)
    return result


def parse_probe(run: dict[str, object]) -> dict[str, object] | None:
    path = Path(str(run["stdout"]))
    if not path.exists():
        return None
    for line in reversed(path.read_text(encoding="utf-8-sig", errors="replace").splitlines()):
        if line.strip().startswith("{"):
            try:
                return json.loads(line)
            except json.JSONDecodeError:
                return None
    return None


def successful_run(run: dict[str, object]) -> bool:
    status = run.get("runner_status")
    return bool(not run["timed_out"] and run["barrier"]["confirmed"] and isinstance(status, dict)
                and status.get("state") == "exited" and status.get("exit_code") == 0)


def prepare_fixture(root: Path, name: str, duration: int) -> dict[str, object]:
    base = root / "fixtures" / name
    input_a, input_b, workspace_a, workspace_b = (base / part for part in ("inputA", "inputB", "workspaceA", "workspaceB"))
    for path in (input_a, input_b, workspace_a, workspace_b):
        path.mkdir(parents=True)
    (input_a / "canary.txt").write_text(CANARY_A + "\n", encoding="utf-8")
    (input_b / "canary.txt").write_text(CANARY_B + "\n", encoding="utf-8")
    (workspace_a / "probe.ps1").write_text(one_shot_source(input_a, input_b, CANARY_A, "a"), encoding="utf-8")
    (workspace_b / "probe.ps1").write_text(one_shot_source(input_b, input_a, CANARY_B, "b"), encoding="utf-8")
    (workspace_a / "concurrent.ps1").write_text(concurrent_source(input_a, input_b, workspace_a, duration), encoding="utf-8")
    paths = (input_a, input_b, workspace_a, workspace_b)
    acl_setup = reset_private_acl(paths)
    return {"base": base, "input_a": input_a, "input_b": input_b,
            "workspace_a": workspace_a, "workspace_b": workspace_b,
            "paths": paths, "acl_setup": acl_setup}


def evaluate_pair(a: dict[str, object] | None, b: dict[str, object] | None) -> bool:
    return bool(a and b and a["results"]["own"]["state"] == "read"
                and a["results"]["own"]["content"] == CANARY_A
                and a["results"]["other"]["state"] == "access_denied"
                and b["results"]["own"]["state"] == "read"
                and b["results"]["own"]["content"] == CANARY_B
                and b["results"]["other"]["state"] == "access_denied")


def samples_are_isolated(samples: list[dict], timeline: dict[str, int]) -> bool:
    """Missing files and failed reads are not proof of access denial."""
    return bool(samples and all(timeline.get(phase, 0) > 0 for phase in
                                ("before_b", "during_b", "after_b")) and all(
        sample["own_state"] == "read" and sample["own_content"] == CANARY_A
        and sample["other_state"] == "access_denied" for sample in samples))


def scenario(root: Path, runner: Path, codex: Path, name: str, deny: bool, duration: int) -> dict[str, object]:
    print(f"probe {name} sequential", file=sys.stderr, flush=True)
    seq = prepare_fixture(root, name + "-sequential", duration)
    seq_initial = acl_snapshot(seq["paths"])
    a = finish_owned(start_owned(root, runner, name + "-seq-a",
        profile_argv(codex, name + "a", seq["workspace_a"], seq["input_a"], seq["input_b"] if deny else None, seq["workspace_a"] / "probe.ps1")))
    seq_after_a = acl_snapshot(seq["paths"])
    b = finish_owned(start_owned(root, runner, name + "-seq-b",
        profile_argv(codex, name + "b", seq["workspace_b"], seq["input_b"], seq["input_a"] if deny else None, seq["workspace_b"] / "probe.ps1")))
    seq_after_b = acl_snapshot(seq["paths"])
    oa, ob = parse_probe(a), parse_probe(b)
    sequential_passed = successful_run(a) and successful_run(b) and evaluate_pair(oa, ob)

    print(f"probe {name} concurrent", file=sys.stderr, flush=True)
    con = prepare_fixture(root, name + "-concurrent", duration)
    con_initial = acl_snapshot(con["paths"])
    arun = start_owned(root, runner, name + "-concurrent-a",
        profile_argv(codex, name + "a", con["workspace_a"], con["input_a"], con["input_b"] if deny else None, con["workspace_a"] / "concurrent.ps1"))
    arun_result = None
    try:
        ready = con["workspace_a"] / "ready.txt"
        while not ready.exists() and time.monotonic() < arun.deadline and not arun.job.inspect().root_signaled:
            time.sleep(.02)
        ready_at = utc_now()
        con_after_a = acl_snapshot(con["paths"])
        brun = finish_owned(start_owned(root, runner, name + "-concurrent-b",
            profile_argv(codex, name + "b", con["workspace_b"], con["input_b"], con["input_a"] if deny else None, con["workspace_b"] / "probe.ps1")))
        con_after_b = acl_snapshot(con["paths"])
    finally:
        arun_result = finish_owned(arun)
    ca, cb = parse_probe(arun_result), parse_probe(brun)
    samples_path = con["workspace_a"] / "samples.jsonl"
    samples = [json.loads(line.lstrip("\ufeff")) for line in samples_path.read_text(encoding="utf-8-sig").splitlines() if line.strip()] if samples_path.exists() else []
    b_start, b_finish = datetime.fromisoformat(brun["started_at"]), datetime.fromisoformat(brun["finished_at"])
    timeline = {"before_b": 0, "during_b": 0, "after_b": 0}
    for item in samples:
        stamp = datetime.fromisoformat(item["observed_at"])
        timeline["before_b" if stamp < b_start else "during_b" if stamp <= b_finish else "after_b"] += 1
    sample_summary = {"path": str(samples_path), "count": len(samples),
                      "own_failures": sum(x["own_state"] != "read" or x["own_content"] != CANARY_A for x in samples),
                      "own_denied": sum(x["own_state"] == "access_denied" for x in samples),
                      "other_reads": sum(x["other_state"] == "read" for x in samples), "relative_to_b": timeline}
    concurrent_passed = bool(successful_run(arun_result) and successful_run(brun) and ready.exists()
        and ca and cb and ca["own_failed"] == 0 and ca["other_reads"] == 0
        and cb["results"]["own"]["state"] == "read" and cb["results"]["own"]["content"] == CANARY_B
        and cb["results"]["other"]["state"] == "access_denied"
        and samples_are_isolated(samples, timeline))
    return {"deny_other_root": deny, "sequential": {"passed": sequential_passed, "runs": {"a": a, "b": b},
            "observations": {"a": oa, "b": ob}, "acl": {"initial": seq_initial, "after_a": seq_after_a, "after_b": seq_after_b}},
            "concurrent": {"passed": concurrent_passed, "ready_observed": ready.exists(), "ready_observed_at": ready_at,
            "runs": {"a": arun_result, "b": brun}, "observations": {"a": ca, "b": cb}, "samples": sample_summary,
            "acl": {"initial": con_initial, "a_running_before_b": con_after_a, "after_b_while_a_running": con_after_b}},
            "passed": sequential_passed and concurrent_passed}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repository", type=Path, default=Path(__file__).resolve().parents[4])
    parser.add_argument("--codex", type=Path, default=shutil.which("codex"))
    parser.add_argument("--output-dir", type=Path, help="New evidence directory; must not exist")
    parser.add_argument("--duration-seconds", type=int, default=15, help="Concurrent A observation duration (5-30)")
    args = parser.parse_args()
    if os.name != "nt": parser.error("this probe requires Windows")
    if args.codex is None or not Path(args.codex).is_file(): parser.error("an installed codex executable is required")
    if not 5 <= args.duration_seconds <= 30: parser.error("--duration-seconds must be between 5 and 30")
    root = (args.output_dir or args.repository / ".skill-workspace" /
            ("do-math-native-isolation-" + datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ") + "-" + uuid.uuid4().hex[:8])).resolve()
    root.mkdir(parents=True, exist_ok=False)
    runner = root / "runner.py"
    runner.write_text(RUNNER_SOURCE, encoding="utf-8")
    started = utc_now()
    try:
        allow = scenario(root, runner, Path(args.codex).resolve(), "allow", False, args.duration_seconds)
        deny = scenario(root, runner, Path(args.codex).resolve(), "deny", True, args.duration_seconds)
        passed = allow["passed"] and deny["passed"]
        report = {"schema_version": "do-math-native-isolation-probe/1", "scope": "elevated Windows sandbox sequential/concurrent read-root independence",
                  "started_at": started, "finished_at": utc_now(), "codex": str(Path(args.codex).resolve()),
                  "powershell": str(POWERSHELL), "step_timeout_seconds": STEP_TIMEOUT,
                  "canaries": {"a": CANARY_A, "b": CANARY_B}, "scenarios": {"allow_only": allow, "explicit_deny": deny},
                  "passed": passed, "model_calls": 0,
                  "not_tested": ["network isolation", "global ACL changes", "other sandbox backends"]}
    except BaseException as exc:
        report = {"schema_version": "do-math-native-isolation-probe/1", "scope": "elevated Windows sandbox sequential/concurrent read-root independence",
                  "started_at": started, "finished_at": utc_now(), "passed": False, "model_calls": 0,
                  "probe_failure": {"error_type": type(exc).__name__, "message": str(exc)}}
    report_path = root / "report.json"
    report["host"] = {"platform": platform.platform(), "python": platform.python_version()}
    report["source_sha256"] = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    with Path(args.codex).open("rb") as binary:
        report["codex_binary_sha256"] = hashlib.file_digest(binary, "sha256").hexdigest()
    report["codex_version"] = run_host([str(args.codex), "--version"])
    report["artifacts"] = [{"path": path.relative_to(root).as_posix(),
                            "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}
                           for path in sorted(root.rglob("*")) if path.is_file()]
    dump(report_path, report)
    print(json.dumps({"passed": report["passed"], "report": str(report_path), "model_calls": 0}, ensure_ascii=False))
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
