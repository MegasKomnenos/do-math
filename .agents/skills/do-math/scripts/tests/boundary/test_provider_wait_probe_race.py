"""Two real processes race for one provider probe over real Git storage (``session_slots``, ``repository`` on
``git_process``), moved from ``test_provider_wait``.

When a closed provider gate reaches its retry time, exactly one probe may be
admitted. The admission is a stored transaction under the instance's writer
lock, so two processes that try at the same time are serialized by the real
lock and the real Git ref update: one is admitted, the other sees the probe and
is refused, and the stored gate names the winner. Each process uses the real
ports (``wiring.real_ports``); provider results and times are synthetic.
"""
import multiprocessing
from pathlib import Path
import tempfile
import threading
import time
import unittest

from do_math.git_store import GitStateStoreLockError
from do_math.session_slots import SessionSlots
from do_math.wiring import real_ports
from provider_fixtures import PROVIDER_LIMIT_FAILURE, admit, finish, report
from research_fixtures import git_init
from support.provider_state import gate_store, transact
from support.storage_records import record_store


def compete(root, ready, release, output, name):
    """A child process: wait for the start, admit ``name`` as the probe at time 500, and settle it after release."""
    ports = real_ports()
    repository = record_store(Path(root) / 'repository', backend=ports.git_backend, clock=ports.clock)
    acquired = False
    try:
        if not ready.wait(120):
            raise AssertionError("probe race was not released")
        deadline = time.monotonic() + 120
        while True:
            try:
                acquired = transact(repository, lambda slots, instance, runtime:
                                    admit(slots, instance, runtime, name, current=500),
                                    clock=ports.clock, jobs=ports.jobs)
                break
            except GitStateStoreLockError:
                if time.monotonic() >= deadline:
                    raise
                threading.Event().wait(.02)  # poll the other writer's lock until the deadline
        output.put((name, acquired, None))
        if acquired and not release.wait(120):
            raise AssertionError("probe race cleanup was not released")
    except Exception as error:  # reported to the parent, then raised again
        output.put((name, False, type(error).__name__ + ": " + str(error)))
        raise
    finally:
        if acquired:
            transact(repository, lambda slots, instance, runtime: finish(slots, runtime, name, 501),
                     clock=ports.clock, jobs=ports.jobs)


class ProbeRaceTests(unittest.TestCase):
    def test_two_real_processes_admit_one_probe(self):
        root = Path(self.enterContext(tempfile.TemporaryDirectory()))
        git_init(root / 'repository')
        ports = real_ports()
        repository = gate_store(root, clock=ports.clock, backend=ports.git_backend)

        def reject(slots, instance, runtime):
            self.assertTrue(admit(slots, instance, runtime, "EX-original", current=100))
            report(slots, instance, "EX-original", 100, PROVIDER_LIMIT_FAILURE)
            finish(slots, runtime, "EX-original", 100)
        transact(repository, reject, clock=ports.clock, jobs=ports.jobs)
        context = multiprocessing.get_context("spawn")
        ready, release, output = context.Event(), context.Event(), context.Queue()
        children = [context.Process(target=compete, args=(str(root), ready, release, output, name))
                    for name in ("EX-one", "EX-two")]
        try:
            for child in children:
                child.start()
            ready.set()
            outcomes = [output.get(timeout=180), output.get(timeout=180)]
            self.assertTrue(all(error is None for _, _, error in outcomes), outcomes)
            self.assertEqual(sum(success for _, success, _ in outcomes), 1, outcomes)
            _, instance, runtime = repository.load()
            gate = SessionSlots(runtime, instance, observer=True, clock=ports.clock,
                                jobs=ports.jobs).provider_snapshot(current_time=500)["providers"]["claude"]
            winner = next(name for name, success, _ in outcomes if success)
            self.assertEqual((gate["state"], gate["probe_owner"]), ("checking", winner))
        finally:
            release.set()
            for child in children:
                child.join(180)
                if child.is_alive():
                    child.terminate()
                    child.join(5)
                self.assertEqual(child.exitcode, 0)
            output.close()


if __name__ == "__main__":
    unittest.main()
