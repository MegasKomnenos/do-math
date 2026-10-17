"""The template key binds all declared JSON inputs before building any state."""
import unittest
from unittest.mock import patch

from support import sim as simulation
from support.sim import template_inputs


def configured(root, shared, *, config=None, criteria=('one', 'two')):
    return root, shared, config, criteria


class TemplateInputTests(unittest.TestCase):
    def test_warming_preserves_a_failed_build_for_the_actual_consumers_without_retry(self):
        error = ValueError('explicit template build failure')
        with patch.object(simulation, '_TEMPLATE', []), \
             patch.object(simulation, '_Template', side_effect=error) as build:
            simulation.warm_template()
            for _ in range(2):
                with self.assertRaisesRegex(ValueError, '^explicit template build failure$') as caught:
                    simulation._template()
                self.assertIs(caught.exception, error)
            self.assertEqual(build.call_count, 1)

    def test_omitted_defaults_and_equivalent_json_forms_have_one_key(self):
        key, values = template_inputs(configured, {})
        self.assertEqual(template_inputs(configured, {'config': None, 'criteria': ['one', 'two']}), (key, values))
        a = template_inputs(configured, {'config': {'alpha': 1, 'nested': {'x': True, 'y': None}}})
        b = template_inputs(configured, {'config': {'nested': {'y': None, 'x': True}, 'alpha': 1}})
        self.assertEqual(a, b)
        self.assertEqual(values, {'config': None, 'criteria': ['one', 'two']})

    def test_different_configuration_or_criteria_cannot_share_a_key(self):
        first = template_inputs(configured, {'config': {'call_timeout_seconds': 10}})
        second = template_inputs(configured, {'config': {'call_timeout_seconds': 11}})
        self.assertNotEqual(first[0], second[0])
        self.assertEqual(second[1]['config']['call_timeout_seconds'], 11)
        self.assertNotEqual(template_inputs(configured, {'criteria': ['a|b']})[0],
                            template_inputs(configured, {'criteria': ['a', 'b']})[0])

    def test_unknown_non_json_and_captured_inputs_are_refused(self):
        with self.assertRaisesRegex(TypeError, 'unexpected keyword argument'):
            template_inputs(configured, {'ignored': 1})
        with self.assertRaisesRegex(TypeError, 'not JSON serializable'):
            template_inputs(configured, {'config': object()})
        with self.assertRaisesRegex(ValueError, 'Out of range float'):
            template_inputs(configured, {'config': float('nan')})
        secret = {'not': 'in the key'}
        def captured(root, shared):
            return secret
        with self.assertRaisesRegex(ValueError, 'must not capture inputs'):
            template_inputs(captured, {})

    def test_variadic_builders_and_nested_non_string_object_keys_are_refused(self):
        def keywords(root, shared, **options):
            return options
        def positional(root, shared, *options):
            return options
        for build in (keywords, positional):
            with self.subTest(build=build.__name__):
                with self.assertRaisesRegex(ValueError, '^template builders require named JSON inputs$'):
                    template_inputs(build, {})
        value = {'rows': [{'valid': {1: 'not a string key'}}]}
        with self.assertRaisesRegex(TypeError, '^template JSON object keys must be strings$'):
            template_inputs(configured, {'config': value})
        self.assertEqual(value, {'rows': [{'valid': {1: 'not a string key'}}]})
