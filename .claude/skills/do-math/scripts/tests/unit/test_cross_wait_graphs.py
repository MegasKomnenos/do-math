"""7-A checks actual dependency/wait relations using an independent cycle detector."""
import unittest

from support.cross_contracts import assert_acyclic, assert_wait_graphs


class WaitGraphTests(unittest.TestCase):
    def test_shared_prerequisites_are_acyclic_but_self_and_multi_node_cycles_are_not(self):
        self.assertIsNone(assert_acyclic({'A': {'C'}, 'B': {'C'}, 'C': set()}, 'specimen'))
        for graph in ({'A': {'A'}}, {'A': {'B'}, 'B': {'C'}, 'C': {'A'}}):
            with self.subTest(graph=graph), self.assertRaisesRegex(AssertionError, '^specimen has a cycle:') as caught:
                assert_acyclic(graph, 'specimen')
            self.assertIn('A', str(caught.exception))

    def test_task_cycle_is_detected_without_a_product_cycle_predicate(self):
        runtime = {'tasks': {'TK-A': {'dependencies': ['TK-B']}, 'TK-B': {'dependencies': ['TK-A']}}}
        with self.assertRaisesRegex(AssertionError, '^task dependency graph has a cycle:') as caught:
            assert_wait_graphs({}, runtime)
        self.assertIn('TK-A', str(caught.exception))
        self.assertIn('TK-B', str(caught.exception))
