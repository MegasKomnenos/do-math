"""The Sim template (설계 4.4): each restore is the same active instance, and nothing one test does reaches the next."""
import unittest

from support.sim import Sim, warm_template

setUpModule = warm_template


class TemplateTests(unittest.TestCase):
    def test_a_restore_is_active_with_the_clock_continuing_and_forgets_the_previous_restore(self):
        """About 3 s, over the 2 s Sim budget: its two restores (about 1.1 s each) are what it checks."""
        first = Sim.activated()
        self.assertEqual(first.instance['lifecycle']['state'], 'active')
        self.assertEqual(first.real_time_leaks(), [])
        next_id = first.clock.new_id('XX')
        first.control('pause', text='pause the restored copy')
        first.engine.process_controls()
        self.assertEqual(first.runtime['status'], 'paused')

        second = Sim.activated()
        self.assertEqual(second.instance['lifecycle']['state'], 'active')
        self.assertNotEqual(second.runtime['status'], 'paused')
        self.assertEqual(second.clock.new_id('XX'), next_id, 'the clock continues from the template, not from the last test')

    def test_a_template_takes_no_options(self):
        with self.assertRaisesRegex(ValueError, 'template Sim has the default options'):
            Sim.activated(goal='another goal')


if __name__ == '__main__':
    unittest.main()
