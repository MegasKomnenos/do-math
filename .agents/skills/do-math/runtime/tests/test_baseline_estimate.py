"""The baseline of a set of imports, estimated from the size of what they load (lean_broker.Library,
lean_broker.Broker.estimate_baseline).

Measuring a set of external imports costs a compile of its own. In one instance such compiles were
a third of all compile time, and most sets were used once or twice. The baseline follows the size on
disk of the modules the imports load, each counted once, closely enough that a line through the
measured sets predicts the next within about 2%. So the broker measures a set only until it has
ESTIMATE_BASIS measured sets and whenever a set is smaller or larger than every measured one, and
estimates the others.

The first class fixes how the size is read from a compiled library; a small library is written into a
temporary folder for it. The second fixes when the broker estimates and when it measures; there the
stand-in compiler has no library, so the size of a set is given to the broker directly. The third
fixes that the broker finds a library itself, in the folders the configured Lean searches.
"""
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path[:0] = [str(Path(__file__).resolve().parents[1]), str(Path(__file__).resolve().parent)]
import lean_broker
import runtime_support
from test_lean_broker import BrokerFixture

MIB = 1024 * 1024


def compiled(root, name, imports, public_mib, private_mib=0, form="list", key=True):
    """Write a module's compiled files as Lean leaves them: sizes on disk, and its direct imports in `.ilean`."""
    base = Path(root) / name.replace(".", "/")
    base.parent.mkdir(parents=True, exist_ok=True)
    listed = [[i, False, False, False] if form == "list" else {"module": i} if form == "dict" else i for i in imports]
    record = {"decls": {"some.decl": [1, 0, 2, 0, 1, 4, 1, 8]}, "module": name, "references": {}, "version": 4}
    if key:
        record["directImports"] = listed
    Path(str(base) + ".ilean").write_text(json.dumps(dict(sorted(record.items()))), encoding="utf-8")
    if public_mib:
        Path(str(base) + ".olean").write_bytes(b"\0" * int(public_mib * MIB))
    if private_mib:
        Path(str(base) + ".olean.private").write_bytes(b"\0" * int(private_mib * MIB))


class LibrarySizes(unittest.TestCase):
    def setUp(self):
        folder = tempfile.TemporaryDirectory()
        self.addCleanup(folder.cleanup)
        self.folder = Path(folder.name)
        self.root = self.folder / "lib"
        compiled(self.root, "Init", ["Init.Prelude"], 1)
        compiled(self.root, "Init.Prelude", [], 1)
        compiled(self.root, "Mathlib.A", ["Init"], 2, 1)
        compiled(self.root, "Mathlib.B", ["Mathlib.A"], 4)
        compiled(self.root, "Mathlib.C", ["Mathlib.A", "Mathlib.B"], 8, 2)
        self.index = self.folder / "library.json"

    def library(self, roots=None):
        return lean_broker.Library(self.index, [self.root] if roots is None else roots)

    def test_each_module_a_set_loads_is_counted_once_and_init_always(self):
        library = self.library()
        self.assertEqual(library.closure_mb([]), 2.0)  # Init and what it imports
        self.assertEqual(library.closure_mb(["Mathlib.A"]), 5.0)
        self.assertEqual(library.closure_mb(["Mathlib.B"]), 9.0)
        self.assertEqual(library.closure_mb(["Mathlib.C"]), 19.0)  # A is reached twice and counted once
        self.assertEqual(library.closure_mb(["Mathlib.C", "Mathlib.B", "Mathlib.A", "Mathlib.C"]), 19.0)

    def test_a_set_with_a_module_that_is_not_in_the_library_has_no_size(self):
        library = self.library()
        self.assertIsNone(library.closure_mb(["Mathlib.Missing"]))
        compiled(self.root, "Mathlib.D", ["Mathlib.Missing"], 1)
        self.assertIsNone(library.closure_mb(["Mathlib.D"]))
        # Nothing is remembered about a module that was not found: once it is there, it is seen.
        compiled(self.root, "Mathlib.Missing", [], 3)
        self.assertEqual(library.closure_mb(["Mathlib.D"]), 6.0)

    def test_a_file_this_reader_does_not_know_gives_no_size(self):
        compiled(self.root, "Mathlib.NoKey", ["Mathlib.A"], 1, key=False)
        compiled(self.root, "Mathlib.NoFiles", [], 0)
        (self.root / "Mathlib" / "Broken.ilean").write_text('{"decls":{},"directImports":[["Mathlib.A",fal', encoding="utf-8")
        (self.root / "Mathlib" / "Broken.olean").write_bytes(b"\0" * MIB)
        (self.root / "Mathlib" / "Odd.ilean").write_text('{"decls":{},"directImports":[7]}', encoding="utf-8")
        (self.root / "Mathlib" / "Odd.olean").write_bytes(b"\0" * MIB)
        library = self.library()
        for name in ("Mathlib.NoKey", "Mathlib.NoFiles", "Mathlib.Broken", "Mathlib.Odd"):
            self.assertIsNone(library.closure_mb([name]), name)

    def test_the_forms_in_which_imports_have_been_written_are_read(self):
        compiled(self.root, "Mathlib.Old", ["Mathlib.A"], 1, form="string")
        compiled(self.root, "Mathlib.Dict", ["Mathlib.B"], 1, form="dict")
        library = self.library()
        self.assertEqual(library.closure_mb(["Mathlib.Old"]), 6.0)
        self.assertEqual(library.closure_mb(["Mathlib.Dict"]), 10.0)

    def test_a_module_is_found_in_whichever_folder_of_the_search_path_has_it(self):
        other = self.folder / "other"
        compiled(other, "Pkg.E", ["Mathlib.B"], 16)
        self.assertEqual(self.library([other, self.root]).closure_mb(["Pkg.E"]), 25.0)
        self.assertIsNone(self.library([other]).closure_mb(["Pkg.E"]))

    def test_what_was_read_is_kept_for_the_next_broker(self):
        library = self.library()
        self.assertEqual(library.closure_mb(["Mathlib.C"]), 19.0)
        self.assertFalse(self.index.exists())
        library.save()
        self.assertEqual(sorted(runtime_support.read_json(self.index)), ["Init", "Init.Prelude", "Mathlib.A", "Mathlib.B", "Mathlib.C"])
        # A later broker answers from the file without reading the library again.
        self.assertEqual(self.library(roots=[]).closure_mb(["Mathlib.C"]), 19.0)
        library.save()  # nothing new: the file is not rewritten
        self.index.write_text("{not json", encoding="utf-8")
        self.assertEqual(self.library().closure_mb(["Mathlib.B"]), 9.0)  # an unreadable file is read over


SIZES = {}


class EstimatedBaselines(BrokerFixture):
    """The broker with a compiler that has no library: the size of a set is what SIZES says, or unknown."""

    def setUp(self):
        super().setUp()
        SIZES.clear()
        # The baselines entered below are a real library's, hundreds of MiB, and the machine gate would hold each
        # stand-in compile until the test machine had its baseline free. The gate is given ample memory instead.
        for target, name, value in ((lean_broker.Broker, "closure_mb", lambda broker, imports: SIZES.get(tuple(imports))),
                                    (lean_broker, "available_memory", lambda: 1024 * 1024 * lean_broker.MIB)):
            patcher = patch.object(target, name, value)
            patcher.start()
            self.addCleanup(patcher.stop)
        self.start_broker()

    def measured(self, name, size, baseline, **changed):
        """Enter a set as if it had been measured: its baseline and, unless `size` is None, its size."""
        identity = {"imports": [name], "version": self.broker.state["version"],
                    "environment_key": self.broker.state["environment_key"], "direct": False, **changed}
        key = lean_broker.closure_key(self.broker.environment_identity(), [name], False) + ("x" if changed else "")
        self.broker.calibration.record_baseline(key, identity, baseline, 10.0, size)
        return key

    def line(self, count=5):
        """`count` measured sets on the line baseline = 100 + 2 * size, sizes 100, 200, ..."""
        for n in range(1, count + 1):
            self.measured(f"Mathlib.M{n}", 100.0 * n, 100.0 + 200.0 * n)

    def run_job(self, name, size, **fake):
        if size is not None:
            SIZES[(name,)] = size
        job_id = self.submit(self.session_file("s1", name.replace(".", "_") + ".lean", imports=(name,), **fake), expect_mb=400)
        self.until(lambda: self.finished(job_id))
        job = self.broker.state["jobs"][job_id]
        return job, self.broker.calibration.entry(job["closure"])

    def calibrations(self):
        return [j for j in self.broker.state["jobs"].values() if j["kind"] == "calibration"]

    def test_a_set_between_measured_sizes_is_estimated_and_not_measured(self):
        self.line()
        job, entry = self.run_job("Mathlib.New", 250.0, alloc_mb=40)
        self.assertEqual(self.calibrations(), [])
        self.assertEqual((job["status"], job["exit_code"], job["waiting_for"]), ("finished", 0, None))
        self.assertTrue(entry["estimated"])
        self.assertAlmostEqual(entry["baseline_mb"], 600.0, places=1)  # 100 + 2 * 250
        self.assertEqual((entry["closure_mb"], entry["measured_sets"], entry["import_seconds"]), (250.0, 5, None))
        self.assertEqual((entry["imports"], entry["direct"], entry["failed"]), (["Mathlib.New"], False, None))
        self.assertIn('"event": "baseline_estimated"', self.paths.log.read_text(encoding="utf-8"))
        # The table on disk says which baselines were estimated, for a session that reads it.
        saved = runtime_support.read_json(self.paths.calibration)["entries"][job["closure"]]
        self.assertTrue(saved["estimated"])
        # The estimate is used as a measured baseline is: the excess is what the compile took above it.
        self.assertEqual(job["measured"]["excess_mb"], max(0.0, round(job["measured"]["peak_mb"] - 600.0, 1)))
        # A second compile of the same set neither measures nor estimates again.
        again, _ = self.run_job("Mathlib.New", 250.0)
        self.assertEqual(self.calibrations(), [])
        self.assertEqual(self.paths.log.read_text(encoding="utf-8").count('"event": "baseline_estimated"'), 1)

    def test_a_set_at_a_measured_size_is_estimated_and_one_outside_is_measured(self):
        self.line()
        _, lowest = self.run_job("Mathlib.Low", 100.0)
        _, highest = self.run_job("Mathlib.High", 500.0)
        self.assertTrue(lowest["estimated"] and highest["estimated"])
        self.assertEqual(self.calibrations(), [])
        _, smaller = self.run_job("Mathlib.Smaller", 99.0)
        _, larger = self.run_job("Mathlib.Larger", 501.0)
        self.assertEqual(len(self.calibrations()), 2)
        self.assertFalse(smaller["estimated"] or larger["estimated"])
        # A measured set keeps its size, so that the range it widens serves the next set.
        self.assertEqual((smaller["closure_mb"], larger["closure_mb"]), (99.0, 501.0))
        _, beyond = self.run_job("Mathlib.Beyond", 500.5)
        self.assertTrue(beyond["estimated"])

    def test_fewer_measured_sets_than_the_basis_or_an_unknown_size_means_measuring(self):
        self.line(count=lean_broker.ESTIMATE_BASIS - 1)
        _, entry = self.run_job("Mathlib.Early", 250.0)
        self.assertFalse(entry["estimated"])
        self.assertEqual(len(self.calibrations()), 1)
        # With that one the basis is complete; a set whose modules are not all found is still measured.
        _, unknown = self.run_job("Mathlib.Unknown", None)
        self.assertFalse(unknown["estimated"])
        self.assertIsNone(unknown["closure_mb"])
        self.assertEqual(len(self.calibrations()), 2)
        _, entry = self.run_job("Mathlib.Then", 150.0)
        self.assertTrue(entry["estimated"])

    def test_only_sets_measured_in_this_environment_and_launch_mode_are_fitted_to(self):
        self.line(count=3)
        self.measured("Mathlib.OtherEnvironment", 400.0, 900.0, environment_key="another")
        self.measured("Mathlib.OtherMode", 450.0, 1000.0, direct=True)
        self.measured("Mathlib.OtherVersion", 480.0, 1060.0, version="Lean (version 0)")
        _, first = self.run_job("Mathlib.One", 250.0)   # three measured sets here: measured, the fourth
        self.assertFalse(first["estimated"])
        _, second = self.run_job("Mathlib.Two", 150.0)  # four: measured, the fifth
        self.assertFalse(second["estimated"])
        _, third = self.run_job("Mathlib.Three", 200.0)
        self.assertTrue(third["estimated"])
        self.assertEqual(third["measured_sets"], 5)

    def test_estimated_baselines_are_never_fitted_to(self):
        self.line()
        for n in range(2):
            _, entry = self.run_job(f"Mathlib.E{n}", 120.0 + 60 * n)
            self.assertTrue(entry["estimated"])
            self.assertEqual(entry["measured_sets"], 5)
        self.assertEqual(self.calibrations(), [])

    def test_a_set_measured_before_sizes_were_kept_is_given_its_size_and_used(self):
        for n in range(1, 6):
            key = self.measured(f"Mathlib.M{n}", None, 100.0 + 200.0 * n)
            del self.broker.calibration.entry(key)["closure_mb"]
            del self.broker.calibration.entry(key)["estimated"]
            SIZES[(f"Mathlib.M{n}",)] = 100.0 * n
        _, entry = self.run_job("Mathlib.New", 350.0)
        self.assertTrue(entry["estimated"])
        self.assertAlmostEqual(entry["baseline_mb"], 800.0, places=1)
        sizes = sorted(e["closure_mb"] for e in runtime_support.read_json(self.paths.calibration)["entries"].values()
                       if not e.get("estimated"))
        self.assertEqual(sizes, [100.0, 200.0, 300.0, 400.0, 500.0])

    def test_an_estimate_stays_within_the_measured_baselines(self):
        # Five sets of one size whose measured baselines differ: the line has no slope to go by.
        for n, baseline in enumerate((300.0, 310.0, 305.0, 295.0, 290.0)):
            self.measured(f"Mathlib.S{n}", 200.0, baseline)
        _, same = self.run_job("Mathlib.Same", 200.0)
        self.assertAlmostEqual(same["baseline_mb"], 300.0, places=1)
        # A set far out on a steep line is held to what was measured.
        self.measured("Mathlib.Steep", 201.0, 900.0)
        _, held = self.run_job("Mathlib.Held", 200.5)
        self.assertLessEqual(held["baseline_mb"], 900.0)
        self.assertGreaterEqual(held["baseline_mb"], 290.0)


class TheLibraryTheBrokerFinds(BrokerFixture):
    """The broker with a library on the search path of the configured Lean: it reads the size of a set there itself."""

    def test_the_size_of_a_set_is_read_from_the_search_path_and_kept_for_the_environment(self):
        library = self.root / "library"
        compiled(library, "Init", [], 1)
        compiled(library, "Mathlib.A", ["Init"], 2, 1)
        self.write_settings(env={"LEAN_PATH": str(library)})
        self.start_broker()
        self.assertEqual(self.broker.closure_mb(["Mathlib.A"]), 4.0)
        self.assertIsNone(self.broker.closure_mb(["Mathlib.Missing"]))
        self.broker.save()
        kept = self.paths.root / f"library-{self.broker.state['environment_key']}.json"
        self.assertEqual(sorted(runtime_support.read_json(kept)), ["Init", "Mathlib.A"])


if __name__ == "__main__":
    unittest.main()
