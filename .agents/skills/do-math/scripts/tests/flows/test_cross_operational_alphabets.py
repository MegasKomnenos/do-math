"""Every declared research alphabet reaches real producers under the unchanged LONG budget."""
import unittest
from support.cross_machine import LONG, assert_machine
from support.cross_research_machine import (AlphabetMachine, ReviewAlphabetMachine, OperationAlphabetMachine,
    InvestigationAlphabetMachine, CheckpointAlphabetMachine, AssessmentAlphabetMachine,
    KindAlphabetMachine, ImpactAlphabetMachine, InitialDiagnosisAlphabetMachine)
from support.sim import warm_template

setUpModule = warm_template

class OperationalAlphabetTests(unittest.TestCase):
    def test_operations_alphabet(self):
        assert_machine(OperationAlphabetMachine, LONG)


    def test_operational_task_alphabet(self):
        from support.cross_research_machine import TaskOperationAlphabetMachine
        assert_machine(TaskOperationAlphabetMachine, LONG)


    def test_live_operational_alphabet(self):
        from support.cross_live_operations import LiveOperationMachine
        assert_machine(LiveOperationMachine, LONG)


    def test_initial_diagnosis_alphabet(self):
        assert_machine(InitialDiagnosisAlphabetMachine, LONG)
