"""승인된 P vs NP 실험 도구의 실제 호출 결과를 수집한다."""

from __future__ import annotations

import argparse
import importlib.metadata
import json
import os
import platform
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


LOCAL_APPDATA = os.environ.get("LOCALAPPDATA", "")
TOOL_ROOT = Path(LOCAL_APPDATA) / "pvsnp-toolchain"
Z3_FALLBACK = TOOL_ROOT / "z3-5.1.0" / "z3-5.1.0-x64-win" / "bin" / "z3.exe"
WINGET_FALLBACK = Path(LOCAL_APPDATA) / "Microsoft" / "WindowsApps" / "winget.exe"
WINGET_NO_PACKAGE_EXIT_CODE = 0x8A150014
SUPPORTED_EXECUTABLE_SEARCHES = ("PATH", "PATH_then_fallback_path", "PATH_then_winget_package")
SAT_CANDIDATE_SPECS = {
    "minisat": {
        "candidate_id": "minisat",
        "candidate_name": "MiniSat",
        "discovery_sources": ["minimum_candidate_set"],
        "package_query_names": {"winget": "minisat", "choco": "minisat", "scoop": "minisat"},
        "executable": {
            "name": "minisat",
            "search": "PATH_then_winget_package",
            "fallback_path": None,
            "winget_package_glob": "PolarGoose.minisat_*\\minisat.exe",
        },
        "version_command": ["--help"],
        "dimacs_invocation": {"kind": "file_argument"},
        "fallback": "PySAT Minisat22",
        "refresh_trigger": "package manager, MiniSat version, or PATH changes",
    },
    "cadical": {
        "candidate_id": "cadical",
        "candidate_name": "CaDiCaL",
        "discovery_sources": ["minimum_candidate_set"],
        "package_query_names": {"winget": "cadical", "choco": "cadical", "scoop": "cadical"},
        "executable": {"name": "cadical", "search": "PATH", "fallback_path": None},
        "version_command": ["--version"],
        "dimacs_invocation": {"kind": "file_argument"},
        "fallback": "PySAT CaDiCaL binding after an independent smoke test",
        "refresh_trigger": "package manager or official Windows asset changes",
    },
    "kissat": {
        "candidate_id": "kissat",
        "candidate_name": "Kissat",
        "discovery_sources": ["minimum_candidate_set"],
        "package_query_names": {"winget": "kissat", "choco": "kissat", "scoop": "kissat"},
        "executable": {"name": "kissat", "search": "PATH", "fallback_path": None},
        "version_command": ["--version"],
        "dimacs_invocation": {"kind": "file_argument"},
        "fallback": "CryptoMiniSat executable",
        "refresh_trigger": "package manager or official Windows asset changes",
    },
    "cryptominisat": {
        "candidate_id": "cryptominisat",
        "candidate_name": "CryptoMiniSat",
        "discovery_sources": ["minimum_candidate_set", "official_windows_asset"],
        "package_query_names": {"winget": "cryptominisat", "choco": "cryptominisat", "scoop": "cryptominisat"},
        "executable": {
            "name": "cryptominisat5",
            "search": "PATH_then_fallback_path",
            "fallback_path": "%LOCALAPPDATA%\\pvsnp-toolchain\\cryptominisat-5.14.7\\cryptominisat5.exe",
        },
        "version_command": ["--version"],
        "dimacs_invocation": {"kind": "file_argument"},
        "fallback": "PySAT Minisat22",
        "refresh_trigger": "CryptoMiniSat release, operating system, or package manager changes",
    },
}


def _local_package_managers() -> dict:
    """PATH 탐색과 실행 가능한 승인 별칭 경로를 분리해 반환한다."""
    managers = {}
    for name in ("winget", "choco", "scoop"):
        path_lookup = _run(["where.exe", name])
        executable = None
        discovery = "none"
        probe = None
        if path_lookup["exit_code"] == 0 and path_lookup["stdout"]:
            executable = path_lookup["stdout"].splitlines()[0]
            discovery = "PATH"
        elif name == "winget" and WINGET_FALLBACK.is_file():
            fallback_probe = _run([str(WINGET_FALLBACK), "--version"])
            if fallback_probe["exit_code"] == 0:
                executable = str(WINGET_FALLBACK)
                discovery = "windowsapps_alias"
                probe = fallback_probe
        if executable and probe is None:
            probe_args = [executable, "--version"] if name != "choco" else [executable, "--version"]
            probe = _run(probe_args)
        available = bool(executable and probe and probe["exit_code"] == 0)
        if executable and probe and not available:
            discovery = f"{discovery}_probe_failed"
        managers[name] = {
            "name": name,
            "path_lookup": path_lookup,
            "discovery": discovery if executable else "none",
            "executable": _redact(executable) if executable else "없음",
            "probe": probe,
            "available": available,
            "failure_reason": probe["stderr"] if probe and not available else "",
        }
    return managers


def _package_id(manager: str, stdout: str, candidate: str) -> str | None:
    """패키지 관리자의 기계 판독 가능한 출력에서 패키지 ID를 읽는다."""
    if manager == "winget":
        normalized_candidate = re.sub(r"[^a-z0-9]", "", candidate.lower())
        for value in re.findall(r"\b[A-Za-z0-9][A-Za-z0-9_-]*\.[A-Za-z0-9._-]+\b", stdout):
            if not all(re.search(r"[A-Za-z]", part) for part in value.split(".", 1)):
                continue
            if normalized_candidate in re.sub(r"[^a-z0-9]", "", value.lower()):
                return value
        return None
    if manager == "choco":
        for line in stdout.splitlines():
            package_id = line.split("|", 1)[0].strip()
            if package_id.lower() == candidate.lower():
                return package_id
        return None
    for line in stdout.splitlines():
        package_name = line.strip().split(maxsplit=1)[0] if line.strip() else ""
        if package_name.lower() == candidate.lower():
            return package_name
    return None


def _query_command(manager: str, executable: str, candidate: str) -> list[str]:
    if manager == "winget":
        return [
            executable,
            "search",
            "--query",
            candidate,
            "--source",
            "winget",
            "--accept-source-agreements",
            "--disable-interactivity",
        ]
    if manager == "choco":
        return [executable, "search", candidate, "--exact", "--limit-output"]
    return [executable, "search", candidate]


def _invocation_executable(display_executable: str) -> str:
    if LOCAL_APPDATA:
        return display_executable.replace("%LOCALAPPDATA%", LOCAL_APPDATA)
    return display_executable


def _broad_discovery_command(manager: str, executable: str) -> list[str]:
    if manager == "winget":
        return [executable, "search", "--query", "sat", "--source", "winget", "--accept-source-agreements", "--disable-interactivity"]
    if manager == "choco":
        return [executable, "search", "sat", "--limit-output"]
    return [executable, "search", "sat"]


def _discovered_package_ids(manager: str, stdout: str) -> list[str]:
    if manager == "winget":
        matches = re.findall(r"\b[A-Za-z0-9][A-Za-z0-9_-]*\.[A-Za-z0-9._-]+\b", stdout)
        return sorted(
            {
                value
                for value in matches
                if all(re.search(r"[A-Za-z]", part) for part in value.split(".", 1))
            }
        )
    package_ids = []
    for line in stdout.splitlines():
        value = line.split("|", 1)[0].strip().split(maxsplit=1)[0] if line.strip() else ""
        if value and not value.startswith(("Chocolatey", "Results")):
            package_ids.append(value)
    return sorted(set(package_ids))


def _resolve_candidate_id(manager: str, package_id: str, candidate_specs: dict) -> str | None:
    normalized = re.sub(r"[^a-z0-9]", "", package_id.lower())
    matches = []
    for candidate_id, spec in candidate_specs.items():
        names = {candidate_id, spec["candidate_name"], spec["package_query_names"].get(manager, "")}
        hits = [
            re.sub(r"[^a-z0-9]", "", name.lower())
            for name in names
            if name and re.sub(r"[^a-z0-9]", "", name.lower()) in normalized
        ]
        if hits:
            matches.append((len(max(hits, key=len)), candidate_id))
    if not matches:
        return None
    longest = max(length for length, _ in matches)
    finalists = [candidate_id for length, candidate_id in matches if length == longest]
    return finalists[0] if len(finalists) == 1 else None


def discover_sat_candidates(local_package_managers: dict, candidate_specs: dict) -> dict:
    """사용 가능한 로컬 패키지 관리자 전건의 광범위 SAT 검색을 기록한다."""
    searches = []
    packages = []
    for manager, manager_row in local_package_managers.items():
        if not manager_row["available"]:
            continue
        executable = _invocation_executable(manager_row["executable"])
        result = _run(_broad_discovery_command(manager, executable))
        search = {
            "manager": manager,
            "discovery_source": "local_package_manager_broad_search",
            **result,
        }
        searches.append(search)
        for package_id in _discovered_package_ids(manager, result["stdout"]):
            candidate_id = _resolve_candidate_id(manager, package_id, candidate_specs)
            packages.append(
                {
                    "manager": manager,
                    "package_id": package_id,
                    "candidate_id": candidate_id,
                    "resolution_status": "resolved" if candidate_id else "unresolved",
                    "discovery_source": "local_package_manager_broad_search",
                }
            )
    unresolved = [package for package in packages if package["resolution_status"] == "unresolved"]
    return {
        "searches": searches,
        "packages": packages,
        "unresolved_candidates": unresolved,
        "discovery_complete": bool(searches)
        and all(
            search["exit_code"] == 0
            or (search["manager"] == "winget" and search["exit_code"] == WINGET_NO_PACKAGE_EXIT_CODE)
            for search in searches
        ),
    }


def _query_sat_candidates(local_package_managers: dict, candidate_specs: dict, discovery: dict) -> dict:
    """기존 로컬 패키지 관리자에서 SAT 후보별 회답을 반환한다."""
    rows = {}
    for candidate, spec in candidate_specs.items():
        queries = []
        selected = None
        discovery_matches = [
            package
            for package in discovery["packages"]
            if package.get("candidate_id") == candidate
        ]
        for manager, manager_row in local_package_managers.items():
            if not manager_row["available"]:
                continue
            executable = _invocation_executable(manager_row["executable"])
            query_name = spec["package_query_names"].get(manager, candidate)
            args = _query_command(manager, executable, query_name)
            result = _run(args)
            package_id = _package_id(manager, result["stdout"], query_name)
            if package_id and _resolve_candidate_id(manager, package_id, candidate_specs) != candidate:
                package_id = None
            query = {
                "manager": manager,
                "command": result["command"],
                "exit_code": result["exit_code"],
                "stdout": result["stdout"],
                "stderr": result["stderr"],
                "package_id": package_id,
                "available": result["exit_code"] == 0 and package_id is not None,
            }
            queries.append(query)
            if selected is None and query["available"]:
                selected = query
        if selected is None and discovery_matches:
            selected = {
                "manager": discovery_matches[0]["manager"],
                "package_id": discovery_matches[0]["package_id"],
                "available": True,
            }
        rows[candidate] = {
            "candidate_id": candidate,
            "candidate_name": spec["candidate_name"],
            "discovery_sources": sorted(
                set(spec["discovery_sources"])
                | {match["discovery_source"] for match in discovery_matches}
            ),
            "broad_discoveries": discovery_matches,
            "resolution_status": "resolved",
            "package_queries": queries,
            "available": selected is not None,
            "package_manager": selected["manager"] if selected else None,
            "package_id": selected["package_id"] if selected else None,
        }
    return rows


def _installed_winget_executable(package_id: str, executable_name: str) -> Path | None:
    package_root = Path(LOCAL_APPDATA) / "Microsoft" / "WinGet" / "Packages"
    if not package_root.is_dir():
        return None
    matches = sorted(package_root.glob(f"{package_id}_*\\{executable_name}.exe"))
    return matches[0] if matches else None


def _find_installed_winget_executable(executable_spec: dict, package_id: str | None = None) -> Path | None:
    """winget 조회 성공 여부와 무관하게 실제 설치 경로를 찾는다."""
    executable_name = executable_spec["name"]
    if package_id:
        installed = _installed_winget_executable(package_id, executable_name)
        if installed:
            return installed
    package_root = Path(LOCAL_APPDATA) / "Microsoft" / "WinGet" / "Packages"
    package_glob = executable_spec.get("winget_package_glob")
    if not package_glob or not package_root.is_dir():
        return None
    matches = sorted(path for path in package_root.glob(package_glob) if path.is_file())
    return matches[0] if matches else None


def _measure_sat_candidate(spec: dict, discovery_row: dict) -> dict:
    candidate_id = spec["candidate_id"]
    metadata = {
        "candidate_id": candidate_id,
        "candidate_name": spec["candidate_name"],
        "candidate_spec": spec,
        "discovery": discovery_row,
        "fallback": spec["fallback"],
        "refresh_trigger": spec["refresh_trigger"],
    }
    invocation_kind = spec["dimacs_invocation"]["kind"]
    executable_spec = spec["executable"]
    search_kind = executable_spec["search"]
    if invocation_kind != "file_argument":
        measurement_error = (
            f"unsupported DIMACS invocation kind {invocation_kind!r} for {candidate_id}"
        )
    elif search_kind not in SUPPORTED_EXECUTABLE_SEARCHES:
        measurement_error = (
            f"unsupported executable search kind {search_kind!r} for {candidate_id}"
        )
    else:
        measurement_error = ""
    if measurement_error:
        not_run = {
            "execution_status": "NOT_RUN",
            "command": "없음",
            "exit_code": None,
            "stdout": "",
            "stderr": measurement_error,
        }
        return {
            "name": candidate_id,
            "executable": "없음",
            "version": dict(not_run),
            "sat_input": "",
            "sat": dict(not_run),
            "unsat_input": "",
            "unsat": dict(not_run),
            "status": "FAIL",
            **metadata,
            "measurement_status": "UNSUPPORTED",
            "measurement_error": measurement_error,
        }
    fallback_value = executable_spec.get("fallback_path")
    fallback = Path(_invocation_executable(fallback_value)) if fallback_value else None
    if search_kind == "PATH_then_winget_package":
        fallback = _find_installed_winget_executable(executable_spec, discovery_row.get("package_id"))
    executable = _find_executable(executable_spec["name"], fallback)
    row = _solver_row(candidate_id, executable, spec["version_command"], "dimacs")
    row.update(
        {
            **metadata,
            "measurement_status": "MEASURED",
            "measurement_error": "",
        }
    )
    return row


def _install_command(manager: str, executable: str, package_id: str) -> list[str]:
    if manager == "winget":
        return [
            executable,
            "install",
            "--id",
            package_id,
            "--exact",
            "--source",
            "winget",
            "--accept-package-agreements",
            "--accept-source-agreements",
            "--disable-interactivity",
        ]
    if manager == "choco":
        return [executable, "install", package_id, "--yes", "--no-progress"]
    return [executable, "install", package_id]


def install_available_sat_candidates(report: dict) -> list[dict]:
    """확보 가능 후보 전건을 설치하고 후보별 재측정을 반환한다."""
    events = []
    managers = report["runtime"]["local_package_managers"]
    candidate_specs = report["sat_candidate_specs"]
    discovery_rows = report["sat_candidate_discovery"]["candidates"]
    for candidate, row in discovery_rows.items():
        if not row["available"]:
            continue
        manager = row["package_manager"]
        package_id = row["package_id"]
        executable = _invocation_executable(managers[manager]["executable"])
        result = _run(_install_command(manager, executable, package_id))
        remeasurement = _measure_sat_candidate(candidate_specs[candidate], row)
        event = {
                "event_id": f"I-SAT-{candidate.upper()}",
                "evidence_type": "recorded_event",
                "candidate_id": candidate,
                "candidate": candidate,
                "target": candidate,
                "package_manager": manager,
                "package_id": package_id,
                "command": result["command"],
                "exit_code": result["exit_code"],
                "stdout": result["stdout"],
                "stderr": result["stderr"],
                "remeasurement": {"evidence_type": "live_measurement", **remeasurement},
                "source_coordinates": [
                    "experiments/pvsnp/smoke/evidence/environment-changes.json"
                ],
            }
        installed = result["exit_code"] == 0
        if not installed:
            event.update(
                {
                    "status": "FAIL",
                    "error": result["stderr"] or result["stdout"] or f"installation exited {result['exit_code']}",
                    "fallback": candidate_specs[candidate]["fallback"],
                    "refresh_trigger": candidate_specs[candidate]["refresh_trigger"],
                }
            )
        else:
            event["status"] = "PASS"
        events.append(event)
    return events


def _redact(value: str) -> str:
    """사용자 로컬 경로를 재현 가능한 환경 변수 표기로 바꾼다."""
    if LOCAL_APPDATA:
        value = value.replace(LOCAL_APPDATA, "%LOCALAPPDATA%")
        value = value.replace(LOCAL_APPDATA.lower(), "%LOCALAPPDATA%")
    return value


def _run(args: list[str], *, stdin: str | None = None) -> dict:
    display = subprocess.list2cmdline([_redact(str(arg)) for arg in args])
    try:
        completed = subprocess.run(
            args, input=stdin, capture_output=True, text=True, check=False, timeout=30
        )
        return {
            "command": display,
            "exit_code": completed.returncode,
            "stdout": _redact(completed.stdout.strip()),
            "stderr": _redact(completed.stderr.strip()),
        }
    except (FileNotFoundError, PermissionError) as error:
        return {
            "command": display,
            "exit_code": 127,
            "stdout": "",
            "stderr": f"실행 파일 없음: {type(error).__name__}",
        }
    except subprocess.TimeoutExpired as error:
        return {
            "command": display,
            "exit_code": 124,
            "stdout": _redact(error.stdout or ""),
            "stderr": "30초 제한 시간 초과",
        }


PYTHON_SMOKES = {
    "python-sat": (
        "pysat",
        "from pysat.solvers import Minisat22; "
        "s=Minisat22(bootstrap_with=[[1]]); a=s.solve(); s.delete(); "
        "u=Minisat22(bootstrap_with=[[1],[-1]]); b=u.solve(); u.delete(); "
        "print(f'SAT={a} UNSAT={not b}')",
    ),
    "sympy": (
        "sympy",
        "from sympy import symbols; from sympy.logic.inference import satisfiable; "
        "x=symbols('x'); print(f'SAT={bool(satisfiable(x))} "
        "UNSAT={satisfiable(x & ~x) is False}')",
    ),
    "z3-solver": (
        "z3",
        "import z3; x=z3.Bool('x'); s=z3.Solver(); s.add(x); a=s.check(); "
        "u=z3.Solver(); u.add(x, z3.Not(x)); b=u.check(); "
        "print(f'SAT={a == z3.sat} UNSAT={b == z3.unsat}')",
    ),
    "ortools": (
        "ortools",
        "from ortools.sat.python import cp_model; "
        "m=cp_model.CpModel(); x=m.new_bool_var('x'); m.add(x == 1); "
        "a=cp_model.CpSolver().solve(m); u=cp_model.CpModel(); "
        "y=u.new_bool_var('y'); u.add(y == 1); u.add(y == 0); "
        "b=cp_model.CpSolver().solve(u); "
        "print(f'SAT={a in (cp_model.OPTIMAL, cp_model.FEASIBLE)} "
        "UNSAT={b == cp_model.INFEASIBLE}')",
    ),
}


def _python_rows() -> dict:
    rows = {}
    for distribution, (import_name, snippet) in PYTHON_SMOKES.items():
        smoke = _run([sys.executable, "-c", snippet])
        try:
            version = importlib.metadata.version(distribution)
        except importlib.metadata.PackageNotFoundError:
            version = "미설치"
        passed = smoke["exit_code"] == 0 and "SAT=True UNSAT=True" in smoke["stdout"]
        rows[distribution] = {
            "distribution": distribution,
            "import_name": import_name,
            "version": version,
            "smoke": smoke,
            "status": "PASS" if passed else "FAIL",
        }
    return rows


def _find_executable(name: str, fallback: Path | None = None) -> str:
    located = shutil.which(name)
    if located:
        return located
    if fallback and fallback.is_file():
        return str(fallback)
    return name


def _solver_row(name: str, executable: str, version_args: list[str], kind: str) -> dict:
    version = _run([executable, *version_args])
    with tempfile.TemporaryDirectory(prefix="pvsnp-smoke-") as directory:
        suffix = ".smt2" if kind == "smt2" else ".cnf"
        sat_path = Path(directory) / f"sat{suffix}"
        unsat_path = Path(directory) / f"unsat{suffix}"
        if kind == "smt2":
            sat_input = "(declare-const x Bool)\n(assert x)\n(check-sat)\n"
            unsat_input = "(declare-const x Bool)\n(assert x)\n(assert (not x))\n(check-sat)\n"
        else:
            sat_input = "p cnf 1 1\n1 0\n"
            unsat_input = "p cnf 1 2\n1 0\n-1 0\n"
        sat_path.write_text(sat_input, encoding="utf-8")
        unsat_path.write_text(unsat_input, encoding="utf-8")
        sat = _run([executable, str(sat_path)])
        unsat = _run([executable, str(unsat_path)])
        for result in (sat, unsat):
            redacted_directory = _redact(str(Path(directory)))
            for field in ("command", "stdout", "stderr"):
                result[field] = result[field].replace(redacted_directory, "%TEMP%")
    sat_text = f"{sat['stdout']}\n{sat['stderr']}".lower()
    unsat_text = f"{unsat['stdout']}\n{unsat['stderr']}".lower()
    if kind == "smt2":
        passed = sat["exit_code"] == 0 and unsat["exit_code"] == 0
        passed = passed and sat_text.strip() == "sat" and unsat_text.strip() == "unsat"
    else:
        passed = sat["exit_code"] in (0, 10) and unsat["exit_code"] in (0, 20)
        passed = passed and "unsatisfiable" not in sat_text and "satisfiable" in sat_text
        passed = passed and "unsatisfiable" in unsat_text
    return {
        "name": name,
        "executable": _redact(executable),
        "version": version,
        "sat_input": sat_input,
        "sat": sat,
        "unsat_input": unsat_input,
        "unsat": unsat,
        "status": "PASS" if passed else "FAIL",
    }


def collect_report(candidate_specs: dict | None = None) -> dict:
    """도구별 버전과 SAT·UNSAT 스모크 결과를 실제 호출로 반환한다."""
    candidate_specs = candidate_specs or SAT_CANDIDATE_SPECS
    z3_executable = _find_executable("z3", Z3_FALLBACK)
    local_package_managers = _local_package_managers()
    broad_discovery = discover_sat_candidates(local_package_managers, candidate_specs)
    candidate_queries = _query_sat_candidates(local_package_managers, candidate_specs, broad_discovery)
    broad_discovery["candidates"] = candidate_queries
    runtime = {
        "python_version": platform.python_version(),
        "python_executable": _redact(sys.executable),
        "architecture": platform.architecture()[0],
        "platform": platform.platform(),
        "pip": _run([sys.executable, "-m", "pip", "--version"]),
        "local_package_managers": local_package_managers,
    }
    sat_solvers = {}
    for candidate_id, spec in candidate_specs.items():
        sat_solvers[candidate_id] = _measure_sat_candidate(spec, candidate_queries[candidate_id])
        sat_solvers[candidate_id].update(candidate_queries[candidate_id])
    required_sat_solvers = [
        row
        for row in sat_solvers.values()
        if "minimum_candidate_set" in row["candidate_spec"]["discovery_sources"]
    ]
    return {
        "runtime": runtime,
        "python_packages": _python_rows(),
        "smt_solver": _solver_row("z3", z3_executable, ["-version"], "smt2"),
        "sat_candidate_specs": candidate_specs,
        "sat_candidate_discovery": broad_discovery,
        "sat_candidate_status": (
            "PASS"
            if required_sat_solvers
            and all(row.get("measurement_status") == "MEASURED" for row in required_sat_solvers)
            else "FAIL"
        ),
        "sat_solvers": sat_solvers,
    }


def main(argv: list[str] | None = None, candidate_specs: dict | None = None) -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true", help="JSON 판정표를 stdout에 쓴다.")
    parser.add_argument("--evidence-dir", type=Path, help="도구군별 원시 JSON 로그를 쓴다.")
    parser.add_argument("--install-available-sat", action="store_true", help="확보 가능 SAT 후보 전건을 설치한다.")
    parser.add_argument("--environment-changes", type=Path, help="SAT 설치 사건 JSON을 쓴다.")
    args = parser.parse_args(argv)
    candidate_specs = candidate_specs or SAT_CANDIDATE_SPECS
    report = collect_report(candidate_specs)
    if args.install_available_sat:
        if args.environment_changes is None:
            parser.error("--install-available-sat에는 --environment-changes가 필요합니다.")
        existing_events = []
        if args.environment_changes.is_file():
            existing = json.loads(args.environment_changes.read_text(encoding="utf-8"))
            existing_events = existing.get("events", [])
        new_events = install_available_sat_candidates(report)
        replaced_candidate_ids = {event["candidate_id"] for event in new_events}
        events = [
            event for event in existing_events
            if event.get("candidate_id", event.get("candidate")) not in replaced_candidate_ids
        ]
        events.extend(new_events)
        args.environment_changes.write_text(
            json.dumps({"events": events}, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        report = collect_report(candidate_specs)
    if args.evidence_dir:
        args.evidence_dir.mkdir(parents=True, exist_ok=True)
        evidence = {
            "python-packages.txt": {
                "runtime": report["runtime"],
                "python_packages": report["python_packages"],
            },
            "smt-z3.txt": {
                "solver": report["smt_solver"],
            },
            "sat-solvers.txt": {
                "runtime": {"local_package_managers": report["runtime"]["local_package_managers"]},
                "candidate_specs": report["sat_candidate_specs"],
                "candidate_discovery": report["sat_candidate_discovery"],
                "candidate_status": report["sat_candidate_status"],
                "installation_targets": [
                    candidate_id
                    for candidate_id, row in report["sat_candidate_discovery"]["candidates"].items()
                    if row["available"]
                ],
                "solvers": report["sat_solvers"],
            },
        }
        for filename, value in evidence.items():
            (args.evidence_dir / filename).write_text(
                json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
            )
    if args.json:
        json.dump(report, sys.stdout, ensure_ascii=False, indent=2)
        sys.stdout.write("\n")
    else:
        for name, row in report["python_packages"].items():
            print(f"{name}: {row['status']} {row['version']}")
        print(f"z3: {report['smt_solver']['status']}")
        for name, row in report["sat_solvers"].items():
            print(f"{name}: {row['status']}")


if __name__ == "__main__":
    main()
