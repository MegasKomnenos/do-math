"""How the Lean broker reads the memory of a running compile (lean_broker.Broker.sample).

Listing every process of the machine to find a compile's process tree costs far more than reading the
memory of a few known processes. So the broker lists the tree at most once every TREE_SECONDS and
reads the memory of the processes last listed at each poll in between. These tests fix that the
memory is read at every poll, that the listing is renewed when it is due, and that nothing is kept
for a job that has ended.
"""
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

sys.path[:0] = [str(Path(__file__).resolve().parents[1]), str(Path(__file__).resolve().parent)]
import lean_broker
from test_lean_broker import BrokerFixture


class SamplingOfARunningCompile(BrokerFixture):
    def running_job(self):
        self.start_broker()
        job_id = self.submit(self.session_file("s1", sleep=4), expect_mb=40)
        self.until(lambda: self.broker.state["jobs"][job_id].get("pid")
                   and lean_broker.alive(self.broker.state["jobs"][job_id].get("lean")))
        return job_id, self.broker.state["jobs"][job_id]

    def counted(self):
        listed, read = [], []
        real_tree, real_memory = lean_broker.process_tree, lean_broker.private_memory_mb
        return listed, read, (
            patch.object(lean_broker, "process_tree", side_effect=lambda pid: listed.append(pid) or real_tree(pid)),
            patch.object(lean_broker, "private_memory_mb", side_effect=lambda pids: read.append(list(pids)) or real_memory(pids)))

    def test_the_tree_is_listed_once_and_the_memory_read_at_every_poll(self):
        job_id, job = self.running_job()
        listed, read, (tree, memory) = self.counted()
        self.broker.trees.clear()
        with patch.object(lean_broker, "TREE_SECONDS", 3600), tree, memory:
            for _ in range(6):
                self.broker.sample(job)
        self.assertEqual(listed, [job["pid"]])
        self.assertEqual(len(read), 6)
        self.assertIn(job["pid"], read[-1])
        self.assertGreater(job["measured"]["peak_mb"], 0)

    def test_the_listing_is_renewed_when_it_is_due(self):
        job_id, job = self.running_job()
        listed, read, (tree, memory) = self.counted()
        self.broker.trees.clear()
        with patch.object(lean_broker, "TREE_SECONDS", 0), tree, memory:
            for _ in range(3):
                self.broker.sample(job)
        self.assertEqual(len(listed), 3)
        self.assertEqual(len(read), 3)

    def test_a_listing_made_for_another_process_is_not_used(self):
        job_id, job = self.running_job()
        listed, read, (tree, memory) = self.counted()
        self.broker.trees[job_id] = (job["pid"] + 1, lean_broker.time.monotonic(), [job["pid"] + 1])
        with patch.object(lean_broker, "TREE_SECONDS", 3600), tree, memory:
            self.broker.sample(job)
        self.assertEqual(listed, [job["pid"]])
        self.assertIn(job["pid"], read[-1])

    def test_nothing_is_kept_for_a_job_that_has_ended(self):
        job_id, job = self.running_job()
        self.broker.sample(job)
        self.assertIn(job_id, self.broker.trees)
        self.until(lambda: self.finished(job_id))
        self.assertNotIn(job_id, self.broker.trees)
        self.assertGreater(self.broker.state["jobs"][job_id]["measured"]["peak_mb"], 0)


if __name__ == "__main__":
    unittest.main()
