"""Every declared research alphabet reaches real producers under the unchanged LONG budget."""
import unittest
from support.cross_machine import LONG, assert_machine
from support.cross_research_machine import (AlphabetMachine, ReviewAlphabetMachine, OperationAlphabetMachine,
    InvestigationAlphabetMachine, CheckpointAlphabetMachine, AssessmentAlphabetMachine,
    KindAlphabetMachine, ImpactAlphabetMachine, InitialDiagnosisAlphabetMachine)
from support.sim import warm_template

setUpModule = warm_template

class ReviewAlphabetTests(unittest.TestCase):
    def test_review_alphabet(self):
        assert_machine(ReviewAlphabetMachine, LONG)


    def test_investigation_alphabet(self):
        assert_machine(InvestigationAlphabetMachine, LONG)


    def test_impact_alphabet(self):
        assert_machine(ImpactAlphabetMachine, LONG)


    def test_supplemental_alphabet(self):
        from support.cross_research_machine import SupplementalAlphabetMachine
        assert_machine(SupplementalAlphabetMachine, LONG)
