import json
import io
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock


HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import toolchain_smoke


class ToolchainSmokeTest(unittest.TestCase):
    @staticmethod
    def synthetic_specs():
        specs = dict(toolchain_smoke.SAT_CANDIDATE_SPECS)
        specs["synthetic_sat"] = {
            "candidate_id": "synthetic_sat",
            "candidate_name": "Synthetic SAT",
            "discovery_sources": ["synthetic_test"],
            "package_query_names": {"winget": "synthetic-sat", "choco": "synthetic-sat", "scoop": "synthetic-sat"},
            "executable": {"name": "synthetic-sat", "search": "PATH", "fallback_path": None},
            "version_command": ["--version"],
            "dimacs_invocation": {"kind": "file_argument"},
            "fallback": "PySAT Minisat22",
            "refresh_trigger": "synthetic package changes",
        }
        return specs

    def test_synthetic_fifth_candidate_remeasurement_uses_candidate_specification(self):
        synthetic = self.synthetic_specs()["synthetic_sat"]
        discovery = {
            "candidate_id": "synthetic_sat",
            "resolution_status": "resolved",
            "package_queries": [],
            "available": False,
            "package_manager": None,
            "package_id": None,
        }
        measured = {
            "name": "synthetic_sat",
            "status": "PASS",
            "version": {"command": "synthetic-sat --version", "exit_code": 0},
            "sat": {"command": "synthetic-sat sat.cnf", "exit_code": 10},
            "unsat": {"command": "synthetic-sat unsat.cnf", "exit_code": 20},
        }
        with mock.patch.object(toolchain_smoke, "_find_executable", return_value="synthetic-sat"), mock.patch.object(
            toolchain_smoke, "_solver_row", return_value=measured
        ):
            result = toolchain_smoke._measure_sat_candidate(synthetic, discovery)
        self.assertEqual("synthetic_sat", result["candidate_id"])
        self.assertEqual("Synthetic SAT", result["candidate_name"])
        self.assertEqual("PASS", result["status"])
        self.assertEqual("MEASURED", result["measurement_status"])
        self.assertEqual("", result["measurement_error"])
        self.assertEqual(synthetic, result["candidate_spec"])
        self.assertEqual(discovery, result["discovery"])
        self.assertEqual("PySAT Minisat22", result["fallback"])
        self.assertEqual("synthetic package changes", result["refresh_trigger"])

    def test_unsupported_executable_search_kind_fails_closed(self):
        synthetic = {
            **self.synthetic_specs()["synthetic_sat"],
            "executable": {"name": "synthetic-sat", "search": "registry_lookup", "fallback_path": None},
        }
        discovery = {
            "candidate_id": "synthetic_sat",
            "resolution_status": "resolved",
            "package_queries": [],
            "available": False,
            "package_manager": None,
            "package_id": None,
        }

        measured = toolchain_smoke._measure_sat_candidate(synthetic, discovery)
        self.assertEqual("UNSUPPORTED", measured["measurement_status"])
        self.assertIn("registry_lookup", measured["measurement_error"])
        self.assertEqual("FAIL", measured["status"])
        self.assertEqual(synthetic, measured["candidate_spec"])
        for key in ("version", "sat", "unsat"):
            self.assertEqual("NOT_RUN", measured[key]["execution_status"])
            self.assertEqual("없음", measured[key]["command"])
            self.assertIsNone(measured[key]["exit_code"])

    def test_unsupported_additional_candidate_fails_closed_but_does_not_gate_required_status(self):
        specs = self.synthetic_specs()
        unsupported = {**specs["synthetic_sat"], "dimacs_invocation": {"kind": "stdin_only"}}
        specs["synthetic_sat"] = unsupported
        discovery_row = {
            "candidate_id": "synthetic_sat",
            "candidate_name": "Synthetic SAT",
            "discovery_sources": ["synthetic_test"],
            "broad_discoveries": [],
            "resolution_status": "resolved",
            "package_queries": [],
            "available": True,
            "package_manager": "winget",
            "package_id": "Example.synthetic-sat",
        }

        measured = toolchain_smoke._measure_sat_candidate(unsupported, discovery_row)
        self.assertEqual("synthetic_sat", measured["candidate_id"])
        self.assertEqual("Synthetic SAT", measured["candidate_name"])
        self.assertEqual(unsupported, measured["candidate_spec"])
        self.assertEqual(discovery_row, measured["discovery"])
        self.assertEqual("PySAT Minisat22", measured["fallback"])
        self.assertEqual("synthetic package changes", measured["refresh_trigger"])
        self.assertEqual("UNSUPPORTED", measured["measurement_status"])
        self.assertIn("stdin_only", measured["measurement_error"])
        self.assertEqual("FAIL", measured["status"])
        for key in ("version", "sat", "unsat"):
            self.assertEqual("NOT_RUN", measured[key]["execution_status"])
            self.assertEqual("없음", measured[key]["command"])
            self.assertIsNone(measured[key]["exit_code"])
            self.assertEqual("", measured[key]["stdout"])
            self.assertEqual(measured["measurement_error"], measured[key]["stderr"])

        rows = {
            candidate_id: ({**discovery_row, "candidate_id": candidate_id, "candidate_name": spec["candidate_name"]}
                           if candidate_id == "synthetic_sat" else {
                               "candidate_id": candidate_id,
                               "candidate_name": spec["candidate_name"],
                               "discovery_sources": spec["discovery_sources"],
                               "broad_discoveries": [],
                               "resolution_status": "resolved",
                               "package_queries": [],
                               "available": False,
                               "package_manager": None,
                               "package_id": None,
                           })
            for candidate_id, spec in specs.items()
        }
        discovery = {
            "searches": [{"manager": "winget", "exit_code": 0}],
            "packages": [],
            "unresolved_candidates": [],
            "discovery_complete": True,
        }
        supported_measurement = {
            "name": "solver",
            "executable": "solver",
            "version": {"command": "solver --version", "exit_code": 0, "stdout": "1", "stderr": ""},
            "sat_input": "p cnf 1 1\n1 0\n",
            "sat": {"command": "solver sat.cnf", "exit_code": 10, "stdout": "SATISFIABLE", "stderr": ""},
            "unsat_input": "p cnf 1 2\n1 0\n-1 0\n",
            "unsat": {"command": "solver unsat.cnf", "exit_code": 20, "stdout": "UNSATISFIABLE", "stderr": ""},
            "status": "PASS",
        }
        original_measure = toolchain_smoke._measure_sat_candidate

        def measure(spec, row):
            if spec["candidate_id"] == "synthetic_sat":
                return original_measure(spec, row)
            return {
                **supported_measurement,
                "candidate_id": spec["candidate_id"],
                "candidate_name": spec["candidate_name"],
                "candidate_spec": spec,
                "discovery": row,
                "fallback": spec["fallback"],
                "refresh_trigger": spec["refresh_trigger"],
                "measurement_status": "MEASURED",
                "measurement_error": "",
            }

        managers = {"winget": {"available": True, "executable": "winget.exe"}}
        with mock.patch.object(toolchain_smoke, "_local_package_managers", return_value=managers), mock.patch.object(
            toolchain_smoke, "discover_sat_candidates", return_value=discovery
        ), mock.patch.object(toolchain_smoke, "_query_sat_candidates", return_value=rows), mock.patch.object(
            toolchain_smoke, "_measure_sat_candidate", side_effect=measure
        ), mock.patch.object(toolchain_smoke, "_python_rows", return_value={}), mock.patch.object(
            toolchain_smoke, "_solver_row", return_value=supported_measurement
        ), mock.patch.object(toolchain_smoke, "_run", return_value={"command": "pip", "exit_code": 0, "stdout": "", "stderr": ""}):
            report = toolchain_smoke.collect_report(specs)
        self.assertEqual(set(specs), set(report["sat_solvers"]))
        self.assertEqual("UNSUPPORTED", report["sat_solvers"]["synthetic_sat"]["measurement_status"])
        self.assertEqual("FAIL", report["sat_solvers"]["synthetic_sat"]["status"])
        self.assertEqual(
            "PASS",
            report["sat_candidate_status"],
            "synthetic_sat의 discovery_sources는 minimum_candidate_set을 담지 않으므로 그 UNSUPPORTED가 필수 후보 판정을 흔들지 않는다",
        )

        with mock.patch.object(
            toolchain_smoke, "_run", return_value={"command": "winget install Example.synthetic-sat", "exit_code": 0, "stdout": "ok", "stderr": ""}
        ):
            events = toolchain_smoke.install_available_sat_candidates(report)
        event = next(row for row in events if row["candidate_id"] == "synthetic_sat")
        self.assertEqual("synthetic_sat", event["remeasurement"]["candidate_id"])
        self.assertEqual("UNSUPPORTED", event["remeasurement"]["measurement_status"])

        with tempfile.TemporaryDirectory() as directory, mock.patch.object(
            toolchain_smoke, "collect_report", return_value=report
        ), mock.patch("sys.stdout", new_callable=io.StringIO) as stdout:
            toolchain_smoke.main(["--json", "--evidence-dir", directory], specs)
            json_report = json.loads(stdout.getvalue())
            evidence = json.loads((Path(directory) / "sat-solvers.txt").read_text(encoding="utf-8"))
        for surface in (json_report["sat_solvers"], evidence["solvers"]):
            row = surface["synthetic_sat"]
            self.assertEqual("UNSUPPORTED", row["measurement_status"])
            self.assertIn("stdin_only", row["measurement_error"])
            self.assertEqual("NOT_RUN", row["version"]["execution_status"])
        self.assertEqual("PASS", json_report["sat_candidate_status"])
        self.assertEqual("PASS", evidence["candidate_status"])

    def test_candidate_specifications_have_distinct_required_fields(self):
        required = {
            "candidate_id",
            "candidate_name",
            "discovery_sources",
            "package_query_names",
            "executable",
            "version_command",
            "dimacs_invocation",
            "fallback",
            "refresh_trigger",
        }
        self.assertTrue(
            {"minisat", "cadical", "kissat", "cryptominisat"}
            <= set(toolchain_smoke.SAT_CANDIDATE_SPECS)
        )
        for candidate_id, spec in toolchain_smoke.SAT_CANDIDATE_SPECS.items():
            self.assertEqual(required, set(spec))
            self.assertEqual(candidate_id, spec["candidate_id"])

    def test_broad_discovery_searches_every_available_manager_and_fails_closed(self):
        managers = {
            "winget": {"available": True, "executable": "winget.exe"},
            "choco": {"available": False, "executable": "없음"},
            "scoop": {"available": True, "executable": "scoop.cmd"},
        }

        def fake_run(args, **_kwargs):
            manager = "winget" if "winget" in str(args[0]) else "scoop"
            stdout = "Synthetic SAT Example.synthetic-sat 1.0\nUnknown Mystery.unknown 2.0" if manager == "winget" else "synthetic-sat"
            return {"command": " ".join(args), "exit_code": 0, "stdout": stdout, "stderr": ""}

        with mock.patch.object(toolchain_smoke, "_run", side_effect=fake_run):
            discovery = toolchain_smoke.discover_sat_candidates(managers, self.synthetic_specs())
        self.assertEqual({"winget", "scoop"}, {row["manager"] for row in discovery["searches"]})
        for row in discovery["searches"]:
            self.assertEqual("local_package_manager_broad_search", row["discovery_source"])
            for field in ("command", "exit_code", "stdout", "stderr"):
                self.assertIn(field, row)
        resolved = next(row for row in discovery["packages"] if row["package_id"] == "Example.synthetic-sat")
        self.assertEqual("synthetic_sat", resolved["candidate_id"])
        self.assertTrue(discovery["unresolved_candidates"])
        self.assertTrue(discovery["discovery_complete"])

    def test_discovery_completeness_fails_closed_on_search_failure(self):
        specs = self.synthetic_specs()
        managers = {
            "winget": {"available": True, "executable": "winget.exe"},
            "scoop": {"available": True, "executable": "scoop.cmd"},
        }

        def runner(exit_codes):
            def fake_run(args, **_kwargs):
                manager = "winget" if "winget" in str(args[0]) else "scoop"
                return {
                    "command": " ".join(str(value) for value in args),
                    "exit_code": exit_codes[manager],
                    "stdout": "",
                    "stderr": "",
                }

            return fake_run

        no_package = toolchain_smoke.WINGET_NO_PACKAGE_EXIT_CODE
        cases = [
            (managers, {"winget": 0, "scoop": 0}, True),
            (managers, {"winget": no_package, "scoop": 0}, True),
            (managers, {"winget": 0, "scoop": 1}, False),
            (managers, {"winget": 1, "scoop": 0}, False),
            ({"scoop": managers["scoop"]}, {"winget": 0, "scoop": no_package}, False),
            ({}, {"winget": 0, "scoop": 0}, False),
        ]
        for available_managers, exit_codes, expected in cases:
            with self.subTest(managers=sorted(available_managers), exit_codes=exit_codes):
                with mock.patch.object(toolchain_smoke, "_run", side_effect=runner(exit_codes)):
                    discovery = toolchain_smoke.discover_sat_candidates(available_managers, specs)
                self.assertEqual(expected, discovery["discovery_complete"])

    def test_synthetic_candidate_flows_through_query_collect_install_and_main(self):
        specs = self.synthetic_specs()
        managers = {"winget": {"available": True, "executable": "winget.exe"}}
        discovery = {
            "searches": [],
            "packages": [
                {
                    "manager": "winget",
                    "package_id": "Example.synthetic-sat",
                    "candidate_id": "synthetic_sat",
                    "resolution_status": "resolved",
                    "discovery_source": "local_package_manager_broad_search",
                }
            ],
            "unresolved_candidates": [],
        }

        def query_run(args, **_kwargs):
            query_name = str(args[3])
            if query_name == "synthetic-sat":
                return {"command": " ".join(args), "exit_code": 1, "stdout": "", "stderr": "not found"}
            package_id = f"Example.{query_name}"
            return {"command": " ".join(args), "exit_code": 0, "stdout": f"Name Id {package_id}", "stderr": ""}

        with mock.patch.object(toolchain_smoke, "_run", side_effect=query_run):
            rows = toolchain_smoke._query_sat_candidates(managers, specs, discovery)
        synthetic_row = rows["synthetic_sat"]
        self.assertEqual("Synthetic SAT", synthetic_row["candidate_name"])
        self.assertEqual("Example.synthetic-sat", synthetic_row["package_id"])
        self.assertEqual("local_package_manager_broad_search", synthetic_row["broad_discoveries"][0]["discovery_source"])
        discovery["candidates"] = rows

        base_solver = {
            "name": "synthetic_sat",
            "executable": "synthetic-sat",
            "version": {"command": "synthetic-sat --version", "exit_code": 0, "stdout": "1", "stderr": ""},
            "sat_input": "p cnf 1 1\n1 0\n",
            "sat": {"command": "synthetic-sat sat.cnf", "exit_code": 10, "stdout": "SATISFIABLE", "stderr": ""},
            "unsat_input": "p cnf 1 2\n1 0\n-1 0\n",
            "unsat": {"command": "synthetic-sat unsat.cnf", "exit_code": 20, "stdout": "UNSATISFIABLE", "stderr": ""},
            "status": "PASS",
            "measurement_status": "MEASURED",
            "measurement_error": "",
        }
        with mock.patch.object(toolchain_smoke, "_local_package_managers", return_value=managers), mock.patch.object(
            toolchain_smoke,
            "discover_sat_candidates",
            return_value={"searches": [], "packages": [], "unresolved_candidates": [], "discovery_complete": True},
        ), mock.patch.object(toolchain_smoke, "_query_sat_candidates", return_value=rows), mock.patch.object(
            toolchain_smoke, "_measure_sat_candidate", side_effect=lambda spec, _row: {**base_solver, "candidate_id": spec["candidate_id"], "candidate_name": spec["candidate_name"], "candidate_spec": spec}
        ), mock.patch.object(toolchain_smoke, "_python_rows", return_value={}), mock.patch.object(
            toolchain_smoke, "_solver_row", return_value=base_solver
        ), mock.patch.object(toolchain_smoke, "_run", return_value={"command": "pip", "exit_code": 0, "stdout": "", "stderr": ""}):
            report = toolchain_smoke.collect_report(specs)
        self.assertIn("synthetic_sat", report["sat_candidate_specs"])
        self.assertIn("synthetic_sat", report["sat_candidate_discovery"]["candidates"])
        self.assertIn("synthetic_sat", report["sat_solvers"])
        self.assertEqual("PASS", report["sat_candidate_status"])

        report["runtime"]["local_package_managers"] = managers
        with mock.patch.object(
            toolchain_smoke, "_run", return_value={"command": "winget install Example.synthetic-sat", "exit_code": 1, "stdout": "", "stderr": "denied"}
        ), mock.patch.object(toolchain_smoke, "_measure_sat_candidate", return_value=base_solver):
            events = toolchain_smoke.install_available_sat_candidates(report)
        synthetic_event = next(event for event in events if event["candidate_id"] == "synthetic_sat")
        self.assertEqual("FAIL", synthetic_event["status"])
        for field in ("package_manager", "package_id", "command", "exit_code", "stdout", "stderr", "error", "fallback", "refresh_trigger"):
            self.assertIn(field, synthetic_event)

        with tempfile.TemporaryDirectory() as directory, mock.patch.object(toolchain_smoke, "collect_report", return_value=report), mock.patch(
            "sys.stdout", new_callable=io.StringIO
        ) as stdout:
            toolchain_smoke.main(["--json", "--evidence-dir", directory], specs)
            json_report = json.loads(stdout.getvalue())
            evidence = json.loads((Path(directory) / "sat-solvers.txt").read_text(encoding="utf-8"))
        self.assertIn("synthetic_sat", json_report["sat_candidate_specs"])
        self.assertIn("synthetic_sat", evidence["candidate_specs"])
        self.assertIn("synthetic_sat", evidence["candidate_discovery"]["candidates"])
        self.assertIn("synthetic_sat", evidence["installation_targets"])
        self.assertIn("synthetic_sat", evidence["solvers"])

        previous = {**synthetic_event, "event_id": "old-id", "command": "old command"}
        past = {"event_id": "I-PY", "evidence_type": "recorded_event", "command": "past pip install", "exit_code": 0}
        with tempfile.TemporaryDirectory() as directory:
            changes_path = Path(directory) / "environment-changes.json"
            changes_path.write_text(json.dumps({"events": [past, previous]}), encoding="utf-8")
            with mock.patch.object(toolchain_smoke, "collect_report", side_effect=[report, report]), mock.patch.object(
                toolchain_smoke, "install_available_sat_candidates", return_value=[synthetic_event]
            ), mock.patch("sys.stdout", new_callable=io.StringIO):
                toolchain_smoke.main(
                    ["--json", "--install-available-sat", "--environment-changes", str(changes_path)], specs
                )
            merged = json.loads(changes_path.read_text(encoding="utf-8"))["events"]
        self.assertEqual(2, len(merged))
        self.assertEqual("I-PY", merged[0]["event_id"])
        self.assertEqual("past pip install", merged[0]["command"])
        self.assertEqual("synthetic_sat", merged[1]["candidate_id"])
        self.assertEqual(synthetic_event["command"], merged[1]["command"])

    def test_collect_report_ignores_unresolved_discovered_packages_for_required_status(self):
        unresolved = {
            "searches": [{"manager": "winget", "exit_code": 0}],
            "packages": [{"candidate_id": None, "package_id": "Unknown.sat", "resolution_status": "unresolved"}],
            "unresolved_candidates": [{"candidate_id": None, "package_id": "Unknown.sat", "resolution_status": "unresolved"}],
            "discovery_complete": True,
        }
        rows = {
            candidate_id: {
                "candidate_id": candidate_id,
                "candidate_name": spec["candidate_name"],
                "available": False,
                "package_manager": None,
                "package_id": None,
                "package_queries": [],
            }
            for candidate_id, spec in toolchain_smoke.SAT_CANDIDATE_SPECS.items()
        }
        solver = {
            "name": "solver",
            "version": {"command": "version", "exit_code": 127},
            "sat_input": "sat",
            "sat": {"command": "sat", "exit_code": 127},
            "unsat_input": "unsat",
            "unsat": {"command": "unsat", "exit_code": 127},
            "status": "FAIL",
            "candidate_spec": {"discovery_sources": ["minimum_candidate_set"]},
            "measurement_status": "MEASURED",
            "measurement_error": "",
        }
        with mock.patch.object(toolchain_smoke, "_local_package_managers", return_value={}), mock.patch.object(
            toolchain_smoke, "discover_sat_candidates", return_value=unresolved
        ), mock.patch.object(toolchain_smoke, "_query_sat_candidates", return_value=rows), mock.patch.object(
            toolchain_smoke, "_measure_sat_candidate", return_value=solver
        ), mock.patch.object(toolchain_smoke, "_python_rows", return_value={}), mock.patch.object(
            toolchain_smoke, "_solver_row", return_value=solver
        ), mock.patch.object(toolchain_smoke, "_run", return_value={"command": "pip", "exit_code": 0, "stdout": "", "stderr": ""}):
            report = toolchain_smoke.collect_report()
        self.assertEqual(
            "PASS",
            report["sat_candidate_status"],
            "필수 후보 4건이 모두 MEASURED이면, winget 광범위 검색이 무관 패키지를 미해소로 남겨도 candidate_status는 PASS다",
        )
        self.assertEqual("Unknown.sat", report["sat_candidate_discovery"]["unresolved_candidates"][0]["package_id"])

    def test_collect_report_fails_closed_on_empty_required_candidate_set(self):
        additional_only = {
            "extra_sat": {
                **toolchain_smoke.SAT_CANDIDATE_SPECS["minisat"],
                "candidate_id": "extra_sat",
                "candidate_name": "Extra SAT",
                "discovery_sources": ["broad_discovery"],
            }
        }
        discovery = {
            "searches": [{"manager": "winget", "exit_code": 0}],
            "packages": [],
            "unresolved_candidates": [],
            "discovery_complete": True,
        }
        rows = {
            "extra_sat": {
                "candidate_id": "extra_sat",
                "candidate_name": "Extra SAT",
                "available": False,
                "package_manager": None,
                "package_id": None,
                "package_queries": [],
            }
        }
        solver = {
            "name": "extra_sat",
            "version": {"command": "version", "exit_code": 0},
            "sat_input": "sat",
            "sat": {"command": "sat", "exit_code": 10},
            "unsat_input": "unsat",
            "unsat": {"command": "unsat", "exit_code": 20},
            "status": "PASS",
            "candidate_spec": additional_only["extra_sat"],
            "measurement_status": "MEASURED",
            "measurement_error": "",
        }
        with mock.patch.object(toolchain_smoke, "_local_package_managers", return_value={}), mock.patch.object(
            toolchain_smoke, "discover_sat_candidates", return_value=discovery
        ), mock.patch.object(toolchain_smoke, "_query_sat_candidates", return_value=rows), mock.patch.object(
            toolchain_smoke, "_measure_sat_candidate", return_value=solver
        ), mock.patch.object(toolchain_smoke, "_python_rows", return_value={}), mock.patch.object(
            toolchain_smoke, "_solver_row", return_value=solver
        ), mock.patch.object(toolchain_smoke, "_run", return_value={"command": "pip", "exit_code": 0, "stdout": "", "stderr": ""}):
            report = toolchain_smoke.collect_report(additional_only)
        self.assertEqual(
            "FAIL",
            report["sat_candidate_status"],
            "필수 후보(minimum_candidate_set)가 0건이면 공허한 PASS를 막기 위해 FAIL이어야 한다",
        )

    def test_path_invisible_winget_uses_only_executable_windowsapps_alias(self):
        def fake_run(args, **_kwargs):
            command = [str(value) for value in args]
            if command[:2] == ["where.exe", "winget"]:
                return {"command": "where.exe winget", "exit_code": 1, "stdout": "", "stderr": "not found"}
            if command[-1] == "--version":
                return {"command": "winget.exe --version", "exit_code": 0, "stdout": "v1", "stderr": ""}
            return {"command": " ".join(command), "exit_code": 1, "stdout": "", "stderr": "not found"}

        fallback = mock.Mock()
        fallback.is_file.return_value = True
        fallback.__str__ = mock.Mock(return_value="C:\\WindowsApps\\winget.exe")
        with mock.patch.object(toolchain_smoke, "_run", side_effect=fake_run), mock.patch.object(
            toolchain_smoke, "WINGET_FALLBACK", fallback
        ):
            managers = toolchain_smoke._local_package_managers()
        winget = managers["winget"]
        self.assertEqual("windowsapps_alias", winget["discovery"])
        self.assertTrue(winget["available"])
        self.assertEqual(1, winget["path_lookup"]["exit_code"])
        self.assertEqual(0, winget["probe"]["exit_code"])

    def test_windowsapps_alias_probe_failure_is_preserved(self):
        alias = "C:\\WindowsApps\\winget.exe"

        def fake_run(args, **_kwargs):
            command = [str(value) for value in args]
            if command[:2] == ["where.exe", "winget"]:
                return {"command": "where.exe winget", "exit_code": 0, "stdout": alias, "stderr": ""}
            if command == [alias, "--version"]:
                return {
                    "command": f"{alias} --version",
                    "exit_code": 127,
                    "stdout": "",
                    "stderr": "실행 파일 없음: FileNotFoundError",
                }
            return {"command": " ".join(command), "exit_code": 1, "stdout": "", "stderr": "not found"}

        with mock.patch.object(toolchain_smoke, "_run", side_effect=fake_run):
            winget = toolchain_smoke._local_package_managers()["winget"]
        self.assertFalse(winget["available"])
        self.assertEqual("PATH_probe_failed", winget["discovery"])
        self.assertEqual(alias, winget["executable"])
        self.assertEqual(127, winget["probe"]["exit_code"])
        self.assertEqual(winget["probe"]["stderr"], winget["failure_reason"])

    def test_minisat_fallback_does_not_depend_on_winget_query_success(self):
        spec = toolchain_smoke.SAT_CANDIDATE_SPECS["minisat"]
        discovery = {
            "candidate_id": "minisat",
            "resolution_status": "resolved",
            "package_queries": [],
            "available": False,
            "package_manager": None,
            "package_id": None,
        }
        installed = Path("C:/LocalAppData/Microsoft/WinGet/Packages/PolarGoose.minisat_source/minisat.exe")
        measured = {
            "name": "minisat",
            "executable": "%LOCALAPPDATA%\\Microsoft\\WinGet\\Packages\\PolarGoose.minisat_source\\minisat.exe",
            "version": {"command": "minisat.exe --help", "exit_code": 0, "stdout": "MiniSat 2.2", "stderr": ""},
            "sat": {"command": "minisat.exe sat.cnf", "exit_code": 10},
            "unsat": {"command": "minisat.exe unsat.cnf", "exit_code": 20},
            "status": "PASS",
        }
        with mock.patch.object(toolchain_smoke, "_find_installed_winget_executable", return_value=installed) as finder, mock.patch.object(
            toolchain_smoke, "_find_executable", side_effect=lambda _name, fallback: str(fallback)
        ), mock.patch.object(toolchain_smoke, "_solver_row", return_value=measured):
            row = toolchain_smoke._measure_sat_candidate(spec, discovery)
        finder.assert_called_once_with(spec["executable"], None)
        self.assertEqual("PASS", row["status"])
        self.assertEqual(10, row["sat"]["exit_code"])
        self.assertEqual(20, row["unsat"]["exit_code"])

    def test_candidate_queries_have_complete_structure_and_derive_availability(self):
        managers = {
            "winget": {
                "name": "winget",
                "available": True,
                "executable": "winget.exe",
            }
        }
        responses = {
            "minisat": "Name MiniSat Id PolarGoose.minisat Version 2.2",
        }
        not_found = "No package found matching input criteria."

        def fake_run(args, **_kwargs):
            candidate = str(args[3])
            return {
                "command": " ".join(str(value) for value in args),
                "exit_code": 0 if candidate in responses else 1,
                "stdout": responses.get(candidate, not_found),
                "stderr": "",
            }

        with mock.patch.object(toolchain_smoke, "_run", side_effect=fake_run):
            rows = toolchain_smoke._query_sat_candidates(
                managers, toolchain_smoke.SAT_CANDIDATE_SPECS, {"searches": [], "packages": [], "unresolved_candidates": []}
            )
        self.assertEqual(set(toolchain_smoke.SAT_CANDIDATE_SPECS), set(rows))
        required = {"manager", "command", "exit_code", "stdout", "stderr", "package_id", "available"}
        for row in rows.values():
            self.assertEqual(required, set(row["package_queries"][0]))
        self.assertTrue(rows["minisat"]["available"])
        self.assertEqual("PolarGoose.minisat", rows["minisat"]["package_id"])
        self.assertFalse(rows["cadical"]["available"])

    def test_all_available_candidates_are_installed_and_remeasured(self):
        report = {
            "sat_solvers": {
                name: {
                    "name": name,
                    "available": name in {"minisat", "kissat"},
                    "package_manager": "winget" if name in {"minisat", "kissat"} else None,
                    "package_id": f"Example.{name}" if name in {"minisat", "kissat"} else None,
                }
                for name in toolchain_smoke.SAT_CANDIDATE_SPECS
            },
            "sat_candidate_specs": toolchain_smoke.SAT_CANDIDATE_SPECS,
            "sat_candidate_discovery": {
                "candidates": {
                    name: {
                        "candidate_id": name,
                        "available": name in {"minisat", "kissat"},
                        "package_manager": "winget" if name in {"minisat", "kissat"} else None,
                        "package_id": f"Example.{name}" if name in {"minisat", "kissat"} else None,
                    }
                    for name in toolchain_smoke.SAT_CANDIDATE_SPECS
                }
            },
            "runtime": {
                "local_package_managers": {
                    "winget": {"available": True, "executable": "winget.exe"}
                }
            },
        }
        install_results = iter(
            [
                {"command": "install minisat", "exit_code": 0, "stdout": "ok", "stderr": ""},
                {"command": "install kissat", "exit_code": 1, "stdout": "", "stderr": "failed"},
            ]
        )
        measured = {name: {"name": name, "status": "PASS"} for name in ("minisat", "kissat")}
        with mock.patch.object(toolchain_smoke, "_run", side_effect=lambda *_a, **_k: next(install_results)), mock.patch.object(
            toolchain_smoke, "_measure_sat_candidate", side_effect=lambda spec, _discovery: measured[spec["candidate_id"]]
        ) as remeasure:
            events = toolchain_smoke.install_available_sat_candidates(report)
        self.assertEqual(["minisat", "kissat"], [event["candidate"] for event in events])
        self.assertEqual(2, remeasure.call_count)
        for event in events:
            self.assertEqual("recorded_event", event["evidence_type"])
            self.assertEqual("winget", event["package_manager"])
            self.assertTrue(event["package_id"])
            self.assertIn("remeasurement", event)
            for field in ("package_manager", "package_id", "command", "exit_code", "stdout", "stderr"):
                self.assertIn(field, event)
        failed = next(event for event in events if event["candidate_id"] == "kissat")
        self.assertEqual("FAIL", failed["status"])
        kissat_spec = toolchain_smoke.SAT_CANDIDATE_SPECS["kissat"]
        self.assertEqual("failed", failed["error"])
        self.assertEqual(kissat_spec["fallback"], failed["fallback"])
        self.assertEqual(kissat_spec["refresh_trigger"], failed["refresh_trigger"])

    def test_report_has_all_approved_python_packages_and_real_commands(self):
        report = toolchain_smoke.collect_report()
        self.assertEqual(
            {"python-sat", "sympy", "z3-solver", "ortools"},
            set(report["python_packages"]),
        )
        for row in report["python_packages"].values():
            self.assertIn(row["status"], {"PASS", "FAIL"})
            self.assertIsInstance(row["smoke"]["exit_code"], int)
            self.assertTrue(row["smoke"]["command"])
            self.assertIn("stdout", row["smoke"])
            self.assertIn("stderr", row["smoke"])

    def test_report_separates_z3_executable_and_all_sat_candidates(self):
        report = toolchain_smoke.collect_report()
        self.assertEqual(
            {"winget", "choco", "scoop"},
            set(report["runtime"]["local_package_managers"]),
        )
        for manager in report["runtime"]["local_package_managers"].values():
            self.assertIn("path_lookup", manager)
            self.assertIsInstance(manager["path_lookup"]["exit_code"], int)
        self.assertEqual("z3", report["smt_solver"]["name"])
        self.assertIn(report["smt_solver"]["status"], {"PASS", "FAIL"})
        self.assertTrue(
            {"minisat", "cadical", "kissat", "cryptominisat"}
            <= set(report["sat_solvers"])
        )
        minimum_candidate_ids = ("minisat", "cadical", "kissat", "cryptominisat")
        minimum_rows = [report["sat_solvers"][candidate_id] for candidate_id in minimum_candidate_ids]
        for row in report["sat_solvers"].values():
            self.assertIn(row["status"], {"PASS", "FAIL"})
            self.assertIn(row["measurement_status"], {"MEASURED", "UNSUPPORTED"})
        for row in [report["smt_solver"], *minimum_rows]:
            self.assertIn(row["status"], {"PASS", "FAIL"})
            self.assertTrue(row["sat_input"])
            self.assertTrue(row["unsat_input"])
            for key in ("version", "sat", "unsat"):
                self.assertIn("command", row[key])
                self.assertIsInstance(row[key]["exit_code"], int)
        for row in minimum_rows:
            self.assertEqual("MEASURED", row["measurement_status"])
            self.assertEqual("", row["measurement_error"])
            for query in row["package_queries"]:
                self.assertEqual(
                    {"manager", "command", "exit_code", "stdout", "stderr", "package_id", "available"},
                    set(query),
                )

    def test_cli_is_the_same_live_report_surface(self):
        completed = subprocess.run(
            [sys.executable, str(HERE / "toolchain_smoke.py"), "--json"],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(0, completed.returncode, completed.stderr)
        report = json.loads(completed.stdout)
        self.assertIn("runtime", report)
        self.assertTrue(report["runtime"]["python_executable"].endswith("python.exe"))
        escaped_home = json.dumps(str(Path.home()), ensure_ascii=False)[1:-1]
        self.assertNotIn(escaped_home, completed.stdout)

    def test_evidence_files_are_generated_from_live_results(self):
        with tempfile.TemporaryDirectory() as directory:
            completed = subprocess.run(
                [
                    sys.executable,
                    str(HERE / "toolchain_smoke.py"),
                    "--evidence-dir",
                    directory,
                ],
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(0, completed.returncode, completed.stderr)
            escaped_home = json.dumps(str(Path.home()), ensure_ascii=False)[1:-1]
            for filename in ("python-packages.txt", "smt-z3.txt", "sat-solvers.txt"):
                raw = (Path(directory) / filename).read_text(encoding="utf-8")
                parsed = json.loads(raw)
                self.assertTrue(parsed)
                serialized = json.dumps(parsed)
                self.assertNotIn(escaped_home, raw)
                self.assertNotIn("environment_change", serialized)
                self.assertNotIn("recorded_event", serialized)

    def test_recorded_events_have_type_and_source_coordinates(self):
        path = HERE / "evidence" / "environment-changes.json"
        parsed = json.loads(path.read_text(encoding="utf-8"))
        self.assertTrue(parsed["events"])
        self.assertEqual({"I-PY", "I-Z3", "I-CMS", "I-SAT-MINISAT"}, {event["event_id"] for event in parsed["events"]})
        for event in parsed["events"]:
            self.assertEqual("recorded_event", event["evidence_type"])
            self.assertTrue(event["source_coordinates"])
        install = next(event for event in parsed["events"] if event["event_id"] == "I-SAT-MINISAT")
        for field in ("candidate", "target", "package_manager", "package_id", "command", "exit_code", "stdout", "stderr", "remeasurement"):
            self.assertIn(field, install)

    def test_baseline_sections_five_and_six_consume_candidate_and_installation_structures(self):
        baseline = (HERE.parents[2] / "research" / "pvsnp" / "environment" / "toolchain-baseline.md").read_text(encoding="utf-8")
        section_five = baseline.split("## 5.", 1)[1].split("## 6.", 1)[0]
        section_six = baseline.split("## 6.", 1)[1].split("## 7.", 1)[0]
        for value in (
            "candidate_specs",
            "candidate_discovery",
            "candidate_status",
            "unresolved_candidates",
            "measurement_status",
            "MEASURED",
            "UNSUPPORTED",
            "measurement_error",
        ):
            self.assertIn(value, section_five)
        for value in (
            "environment-changes.json",
            "package_manager",
            "package_id",
            "command",
            "exit_code",
            "stdout",
            "stderr",
            "error",
            "fallback",
            "refresh_trigger",
            "status: FAIL",
            "execution_status: NOT_RUN",
            "command: 없음",
            "exit_code: null",
        ):
            self.assertIn(value, section_six)


if __name__ == "__main__":
    unittest.main()
