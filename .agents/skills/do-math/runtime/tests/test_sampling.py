"""How the Lean broker reads the memory of a running compile (lean_broker.Broker.sample).

Listing every process of the machine to find a compile's process tree costs far more than reading the
memory of a few known processes. So the broker lists the tree at most once every TREE_SECONDS and
reads the memory of the processes last listed at each poll in between. These tests fix that the
memory is read at every poll, that the listing is renewed when it is due, that a listed process is
read only while its PID is still its own, and that nothing is kept for a job that has ended.
"""
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

sys.path[:0] = [str(Path(__file__).resolve().parents[1]), str(Path(__file__).resolve().parent)]
import lean_broker
from broker_fixture import BrokerFixture


class SamplingOfARunningCompile(BrokerFixture):
    def running_job(self, sleep=4):
        self.start_broker()
        job_id = self.submit(self.session_file("s1", sleep=sleep), expect_mb=40)
        self.until(lambda: self.broker.state["jobs"][job_id].get("pid")
                   and lean_broker.alive(self.broker.state["jobs"][job_id].get("lean")))
        return job_id, self.broker.state["jobs"][job_id]

    def counted(self):
        listed, read = [], []
        real_tree, real_memory = lean_broker.process_tree, lean_broker.private_memory_mb
        return listed, read, (
            patch.object(lean_broker, "process_tree", side_effect=lambda pid: listed.append(pid) or real_tree(pid)),
            patch.object(lean_broker, "private_memory_mb", side_effect=lambda pids: read.append(list(pids)) or real_memory(pids)))

    def test_the_memory_is_read_at_every_poll_and_the_tree_is_listed_only_when_a_listing_is_due(self):
        # One running compile serves the four cases: each sets the listing that the broker holds for the job and
        # counts from nothing. The compile outlasts them on any machine, and the fixture ends it after the test.
        job_id, job = self.running_job(sleep=30)
        with self.subTest("the tree is listed once and the memory read at every poll"):
            listed, read, (tree, memory) = self.counted()
            self.broker.trees.clear()
            with patch.object(lean_broker, "TREE_SECONDS", 3600), tree, memory:
                for _ in range(6):
                    self.broker.sample(job)
            self.assertEqual(listed, [job["pid"]])
            self.assertEqual(len(read), 6)
            self.assertIn(job["pid"], read[-1])
            self.assertGreater(job["measured"]["peak_mb"], 0)
        with self.subTest("the listing is renewed when it is due"):
            listed, read, (tree, memory) = self.counted()
            self.broker.trees.clear()
            with patch.object(lean_broker, "TREE_SECONDS", 0), tree, memory:
                for _ in range(3):
                    self.broker.sample(job)
            self.assertEqual(len(listed), 3)
            self.assertEqual(len(read), 3)
        with self.subTest("a listing made for another process is not used"):
            listed, read, (tree, memory) = self.counted()
            self.broker.trees[job_id] = (job["pid"] + 1, lean_broker.time.monotonic(), [job["pid"] + 1])
            with patch.object(lean_broker, "TREE_SECONDS", 3600), tree, memory:
                self.broker.sample(job)
            self.assertEqual(listed, [job["pid"]])
            self.assertIn(job["pid"], read[-1])
        with self.subTest("a listed process whose PID has passed to another process is not read"):
            # A process of the tree can end between two listings, and the system can give its PID to a process that
            # is none of the compile's. Read as the compile's, that process's memory would become the compile's peak
            # and, when the compile ends, the baseline or an excess of its imports in the calibration table.
            listed, read, (tree, memory) = self.counted()
            ended = {"pid": lean_broker.os.getpid(), "birth": "a process of the compile that has ended"}
            self.broker.trees[job_id] = (job["pid"], lean_broker.time.monotonic(), [job["lean"], ended])
            with patch.object(lean_broker, "TREE_SECONDS", 3600), tree, memory:
                self.broker.sample(job)
            self.assertEqual((listed, read), ([], [[job["pid"]]]))

    def test_nothing_is_kept_for_a_job_that_has_ended(self):
        job_id, job = self.running_job()
        self.broker.sample(job)
        self.assertIn(job_id, self.broker.trees)
        self.until(lambda: self.finished(job_id))
        self.assertNotIn(job_id, self.broker.trees)
        self.assertGreater(self.broker.state["jobs"][job_id]["measured"]["peak_mb"], 0)


if __name__ == "__main__":
    unittest.main()
