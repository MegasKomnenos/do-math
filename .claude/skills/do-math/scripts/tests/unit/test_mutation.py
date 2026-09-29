"""Extreme mutation rules and bookkeeping (설계 6.3), judged on small synthetic modules."""
import ast
import inspect
import unittest

from support.mutation import (changed_functions, functions, line_map, mutant_timeout, mutate, rule_of, tests_for,
                               unreasoned, update_list)

SOURCE = '''class Store:
    def put(self, key, value):
        """Keep a value."""
        self.items[key] = value

    def get(self, key):
        return self.items.get(key, '기본값')


def pairs(items):
    for item in items:
        yield item, item


def total(values): return sum(values)


def explicit_none(flag):
    if flag:
        return None
    return


def outer(x):
    def inner():
        return x
    inner()


def stub():
    ...
'''


def _node(source, key):
    return dict(functions(ast.parse(source)))[key]


def _run(source):
    namespace = {}
    exec(compile(source, '<mutant>', 'exec'), namespace)
    return namespace


class RuleTests(unittest.TestCase):
    def test_the_rule_follows_the_body_shape_of_the_function_itself(self):
        rules = {key: rule_of(node) for key, node in functions(ast.parse(SOURCE))}
        self.assertEqual(rules, {'Store.put': 'pass', 'Store.get': 'return_none', 'pairs': 'return_first',
                                 'total': 'return_none', 'explicit_none': 'pass', 'outer': 'pass',
                                 'outer.<locals>.inner': 'return_none', 'stub': 'pass'})


class MutantTests(unittest.TestCase):
    def test_a_value_returning_function_returns_none_and_keeps_its_docstring_and_neighbours(self):
        rule, mutant = mutate(SOURCE, _node(SOURCE, 'Store.get'))
        namespace = _run(mutant)
        store = namespace['Store']()
        store.items = {'k': 1}
        self.assertEqual(rule, 'return_none')
        self.assertIsNone(store.get('k'))
        self.assertEqual(namespace['total']([1, 2]), 3)
        self.assertEqual(ast.get_docstring(_node(mutant, 'Store.put')), 'Keep a value.')

    def test_a_state_changing_function_does_nothing(self):
        rule, mutant = mutate(SOURCE, _node(SOURCE, 'Store.put'))
        store = _run(mutant)['Store']()
        store.items = {}
        store.put('k', 1)
        self.assertEqual((rule, store.items), ('pass', {}))
        self.assertEqual(ast.get_docstring(_node(mutant, 'Store.put')), 'Keep a value.')

    def test_a_generator_stays_a_generator_and_yields_nothing(self):
        rule, mutant = mutate(SOURCE, _node(SOURCE, 'pairs'))
        pairs = _run(mutant)['pairs']
        self.assertEqual(rule, 'return_first')
        self.assertTrue(inspect.isgeneratorfunction(pairs))
        self.assertEqual(list(pairs([1, 2])), [])

    def test_a_one_line_body_is_replaced_in_place(self):
        rule, mutant = mutate(SOURCE, _node(SOURCE, 'total'))
        self.assertIsNone(_run(mutant)['total']([1, 2]))
        one_line_generator = 'def g(): yield 1\n'
        rule, mutant = mutate(one_line_generator, _node(one_line_generator, 'g'))
        self.assertEqual((rule, list(_run(mutant)['g']())), ('return_first', []))

    def test_a_body_of_only_pass_or_ellipsis_has_no_mutant(self):
        self.assertEqual(mutate(SOURCE, _node(SOURCE, 'stub')), ('pass', None))


class ChangeTests(unittest.TestCase):
    def test_a_changed_or_new_body_is_a_target_and_a_docstring_or_neighbour_edit_is_not(self):
        base = SOURCE
        edited = SOURCE.replace('"""Keep a value."""', '"""Keep the value."""') \
            .replace("'기본값'", "'다른 값'") + '\n\ndef added():\n    return 1\n'
        self.assertEqual([key for key, _ in changed_functions(base, edited)], ['Store.get', 'added'])
        self.assertEqual(len(changed_functions('', SOURCE)), 8)

    def test_repeated_names_are_keyed_in_order(self):
        source = 'def f():\n    return 1\n\n\ndef f():\n    return 2\n'
        self.assertEqual([key for key, _ in functions(ast.parse(source))], ['f', 'f#2'])


class SelectionTests(unittest.TestCase):
    ENTRY = {'blob': 'b1', 'lines': {'2': [0], '3': [1, 2]}}
    OLD = 'def f(x):\n    y = x\n    return y\n'

    def test_the_tests_that_ran_the_body_are_chosen_through_moved_lines(self):
        self.assertEqual(tests_for(self.ENTRY, 'b1', {}.get, self.OLD, range(2, 4), '2'), ({0, 1, 2}, ()))
        moved = '# header\n\n' + self.OLD
        self.assertEqual(line_map(self.OLD, moved)[5], 3)
        self.assertEqual(tests_for(self.ENTRY, 'b2', {'b1': self.OLD}.get, moved, range(4, 6), '2'), ({0, 1, 2}, ()))

    def test_an_unknown_line_or_a_missing_index_adds_the_layer_folders(self):
        changed = 'def f(x):\n    y = x + 1\n    return y\n'
        self.assertEqual(tests_for(self.ENTRY, 'b2', {'b1': self.OLD}.get, changed, range(2, 4), '3'), ({1, 2}, ('sim',)))
        self.assertEqual(tests_for(None, 'b1', {}.get, self.OLD, range(2, 4), '1'), (set(), ('unit', 'contracts')))


class ListTests(unittest.TestCase):
    def test_survivors_enter_without_a_reason_and_killed_functions_leave(self):
        listing = {'note': 'n', 'entries': [
            {'module': 'do_math/a.py', 'function': 'kept', 'rule': 'pass', 'base': 'b0', 'reason': 'None is its behaviour'},
            {'module': 'do_math/a.py', 'function': 'fixed', 'rule': 'pass', 'base': 'b0', 'reason': ''}]}
        outcomes = [{'module': 'do_math/a.py', 'function': 'fixed', 'rule': 'pass', 'status': 'killed'},
                    {'module': 'do_math/a.py', 'function': 'kept', 'rule': 'pass', 'status': 'survived'},
                    {'module': 'do_math/b.py', 'function': 'new', 'rule': 'return_none', 'status': 'survived'},
                    {'module': 'do_math/b.py', 'function': 'unrun', 'rule': 'pass', 'status': 'not_executed'}]
        self.assertTrue(update_list(listing, outcomes, 'b1'))
        self.assertEqual([(e['function'], e['reason'], e['base']) for e in listing['entries']],
                         [('kept', 'None is its behaviour', 'b0'), ('new', '', 'b1')])
        self.assertEqual(unreasoned(listing), 1)
        self.assertFalse(update_list(listing, outcomes, 'b1'))



class MutantTimeoutTests(unittest.TestCase):
    def test_a_mutant_gets_three_times_the_unmutated_run_within_a_floor_and_the_ceiling(self):
        self.assertEqual(mutant_timeout(40.0, 300.0), 120.0)
        self.assertEqual(mutant_timeout(2.0, 300.0), 30.0)
        self.assertEqual(mutant_timeout(200.0, 300.0), 300.0)
        self.assertEqual(mutant_timeout(2.0, 10.0), 10.0)

if __name__ == '__main__':
    unittest.main()
