"""The installed Lean's exact result through knowledge revision, trust transition and storage (``formal``, ``knowledge``).

The compiler is the portable Lean (``provider_fixtures.actual_command``; a
worktree reaches it through a junction to the main tree's toolchains), run by
the product's real Job transport. The state that adopts it as ``TE-old`` is
``support.knowledge_roundtrip.installed_trust_state``: the adoption and the
noncompiler clean-build evidence are synthetic, as in the central boundary
tests. Storage is the real ``ResearchRepository`` on the Git port's fake
(``KnowledgeRoundtripHarness``). Names and expressions that normalization
would change are written as escapes.
"""
import copy
import hashlib
import unittest

from do_math import formal, knowledge, knowledge_records as kr
from provider_fixtures import actual_command
from research_fixtures import current_state
from support.knowledge_roundtrip import KnowledgeRoundtripHarness, installed_trust_state
from test_categories import test_group as category


class InstalledLeanStorageTests(KnowledgeRoundtripHarness):
    @category('lean')
    def test_actual_lean_git_revision_and_transition_preserve_exact_inputs_and_evidence(self):
        self.assert_exact_lean_result_survives(self.roundtrip)

    @category('lean')
    def test_actual_lean_domain_revision_and_transition_preserve_exact_inputs_and_evidence(self):
        self.assert_exact_lean_result_survives(lambda: None)

    def assert_exact_lean_result_survives(self, persist):
        """The installed Lean's result for exact Unicode source survives revision and transition; ``persist`` stores between steps."""
        source = 'theorem \u212a (\u2126 : True) : True := \u2126\r\ntheorem K : True := True.intro\n-- e\u0301\n'
        names = ['\u212a', 'K']
        observed = formal.verify_lean(source=source, declarations=names, workspace=self.root, lean_command=actual_command())
        self.assertEqual(observed['status'], 'verified', observed.get('reason'))
        instance, runtime, self.kid = installed_trust_state(self.root, observed['toolchain'])
        # The legacy fixture's engine state also named its workspace and a configured command
        # deliberately different from the approved one.
        instance.update(workspace=str(self.root), config={'lean_command': ['unapproved-config-command']})
        profiles, constraints = self.state['execution_profiles'], self.state['capacity_constraints']
        # Every stored state passes the current lifecycle gate.
        self.state, self.runtime = current_state(
            {**instance, 'execution_profiles': profiles, 'capacity_constraints': constraints},
            {'queue': [], 'history': [], 'trust_bindings': copy.deepcopy(runtime['trust_bindings'])})
        fid = self.state['knowledge'][self.kid]['formal_result_id']
        self.state['formal_results'][fid].update(lean_code=source, declaration_names=names)
        persist()  # The Git case checks candidate transport before compilation.
        proposal = kr.proposal_view(self.state, self.kid)
        self.assertEqual(proposal['lean_code'].encode(), source.encode())
        observed = formal.verify_lean(source=proposal['lean_code'], declarations=proposal['declaration_names'],
            workspace=self.root, lean_command=actual_command(), expected_toolchain=observed['toolchain'])
        self.assertEqual(observed['status'], 'verified', observed.get('reason'))
        self.state = kr.record_formal_result(self.state, self.kid, observed, 'TE-old', runtime=self.runtime)
        expected = copy.deepcopy(self.state['formal_results'][fid])
        persist()
        self.assertEqual(self.state['formal_results'][fid], expected)
        self.assertEqual(self.state['formal_results'][fid]['verification']['source_sha256'], hashlib.sha256(source.encode()).hexdigest())
        changes = {'summary': 'Exact compiler expression \u2126 preserved in a clearer explanation'}
        roots = knowledge.revision_roots(self.state, self.kid)
        scope = knowledge.plan_impact(self.state, self.runtime, roots, [])['computed_impact']
        old = self.kid
        self.state, self.runtime = knowledge.revise_knowledge(self.state, self.runtime, old, changes,
            reason='Explanation only', actor_ref='synthetic:author', declared_impact=scope)
        self.kid = next(k for k, row in self.state['knowledge'].items() if row.get('supersedes') == old)
        persist()
        self.assertEqual(self.state['knowledge'][self.kid]['formal_result_id'], fid)
        self.assertEqual(self.state['formal_results'][fid], expected)
        self.assertEqual(kr.proposal_view(self.state, self.kid)['summary'], changes['summary'])
        self.state['trust_environments']['TE-next'] = {**copy.deepcopy(self.state['trust_environments']['TE-old']),
            'id': 'TE-next', 'status': 'registered', 'source_ref': 'synthetic:next-adoption'}
        self.runtime['trust_bindings']['TE-next'] = copy.deepcopy(self.runtime['trust_bindings']['TE-old'])
        transition = knowledge.begin_transition(self.state, 'TE-next')
        transition = knowledge.record_transition_result(self.state, transition, {'id': self.kid, **observed})
        self.runtime['trust_transitions'] = {transition['id']: transition}
        persist()
        stored_transition = self.runtime['trust_transitions'][transition['id']]
        self.assertEqual(stored_transition['results'][self.kid]['declaration_evidence'], observed['declaration_evidence'])
        self.state = knowledge.activate_transition(self.state, stored_transition)
        stored_transition['status'] = 'active'
        persist()
        new_formal = self.state['formal_results'][self.state['knowledge'][self.kid]['formal_result_id']]
        self.assertEqual(new_formal['lean_code'].encode(), source.encode())
        self.assertEqual(new_formal['declaration_names'], names)
        self.assertEqual(new_formal['verification']['declaration_evidence'], observed['declaration_evidence'])
        self.assertEqual(self.state['formal_results'][fid], expected)
        self.assertTrue(kr.formal_usable(self.state, new_formal))


if __name__ == '__main__':
    unittest.main()
