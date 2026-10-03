"""Every declared research alphabet reaches real producers under the unchanged LONG budget."""
import unittest
from support.cross_machine import LONG, assert_machine
from support.cross_research_machine import (AlphabetMachine, ReviewAlphabetMachine, OperationAlphabetMachine,
    InvestigationAlphabetMachine, CheckpointAlphabetMachine, AssessmentAlphabetMachine,
    KindAlphabetMachine, ImpactAlphabetMachine, InitialDiagnosisAlphabetMachine)
from support.sim import warm_template

setUpModule = warm_template

class PlanningAlphabetTests(unittest.TestCase):
    def test_planning_alphabet(self):
        assert_machine(AlphabetMachine, LONG)


    def test_assessment_alphabet(self):
        assert_machine(AssessmentAlphabetMachine, LONG)


    def test_kind_alphabet(self):
        assert_machine(KindAlphabetMachine, LONG)


    def test_checkpoint_alphabet(self):
        assert_machine(CheckpointAlphabetMachine, LONG)
